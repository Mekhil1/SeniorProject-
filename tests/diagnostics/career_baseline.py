"""Opt-in local Career latency profiling; never calls an Agent Engine.

Run with the workflow's pinned SDK/ADK environment. Default invocation lists
the plan; --live explicitly permits model requests. --resume skips completed
samples (including failures), never retries them. A 429 stops the batch.
"""

import argparse
import asyncio
import contextlib
import contextvars
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
DOMAINS = [
    ("career", "Career Exploration", "career_exploration_agent",
     "I'm interested in cloud security and risk management. What career paths should I explore?",
     "What current cybersecurity career resources are available to Morgan State Computer Science students?"),
    ("internship", "Internship & Job Preparation", "internship__job_preparation_agent",
     "How should I prepare for cybersecurity internships as a computer science senior?",
     "What cybersecurity internships are currently open to students with my background?"),
    ("resume", "Resume & Portfolio", "resume__portfolio_agent",
     "What should I emphasize on my resume for an entry-level cloud security role?",
     "What resume expectations are employers currently emphasizing for entry-level cloud security roles?"),
    ("interview", "Interview Preparation", "interview_preparation_agent",
     "Give me a technical interview preparation strategy for an entry-level cybersecurity role.",
     "What is the current interview process for an entry-level cybersecurity role at a major employer?"),
    ("networking", "Networking & Professional Communication", "networking__professional_communication_agent",
     "How should I introduce myself to a cybersecurity recruiter?",
     "What current networking resources can Morgan State Computer Science students use?"),
    ("roadmap", "Skill Gap & Career Roadmap", "skill_gap__career_roadmap_agent",
     "I want to become a cloud security engineer. What skills should I build over the next year?",
     "Which current technologies and skills are appearing most often in entry-level cloud security roles?"),
    ("research", "Research & Graduate Pathways", "research__graduate_pathways_agent",
     "How should I decide between graduate school and going directly into cybersecurity industry work?",
     "What current cybersecurity research or graduate opportunities should I investigate at Morgan State?"),
    ("certification", "Certification & Technical Development", "certification__technical_development_agent",
     "How should I decide whether a cybersecurity certification is worth pursuing?",
     "What is the current CompTIA Security+ exam version and price?"),
]
ACTIVE = contextvars.ContextVar("career_diagnostic_run", default=None)
MODEL_METRICS = contextvars.ContextVar("career_diagnostic_prompt_metrics", default=None)
MODEL_AGENT = contextvars.ContextVar("career_diagnostic_model_agent", default="unknown")


def plan(include_research_probes=False, include_roadmap_probe=False, include_interview_probe=False):
    cases = []
    for sample in (1, 2):
        for key, label, agent, stable, current in DOMAINS:
            cases.append(dict(id=f"{key}_stable_{sample}", domain=key, label=label,
                              expected=agent, mode="stable", prompt=stable))
    trust = "trust__human_escalation_agent"
    for sample in (1, 2):
        cases.append(dict(id=f"trust_human_{sample}", domain="trust", label="Trust & Human Escalation",
                          expected=trust, mode="human", prompt="I need a human to review this because the evidence is contradictory and this decision matters."))
    # Profile the known expensive Certification case first among current paths.
    for key, label, agent, stable, current in [DOMAINS[-1], *DOMAINS[:-1]]:
        cases.append(dict(id=f"{key}_current_1", domain=key, label=label,
                          expected=agent, mode="current", prompt=current))
    for key, prompt in [
        ("conflict", "I found conflicting information about whether a Morgan cybersecurity program is still active. Which source should I trust?"),
        ("reliability", "How reliable is this current information if the sources disagree?"),
    ]:
        cases.append(dict(id=f"trust_{key}_1", domain="trust", label="Trust & Human Escalation",
                          expected=trust, mode=key, prompt=prompt))
    if include_research_probes:
        for sample in (1, 2):
            cases.append(dict(id=f'research_readiness_stable_{sample}', domain='research',
                              label='Research & Graduate Pathways', expected='research__graduate_pathways_agent',
                              mode='stable_probe', prompt='What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs.'))
    if include_roadmap_probe:
        cases.append(dict(id='roadmap_current_probe_1', domain='roadmap', label='Skill Gap & Career Roadmap',
                          expected='skill_gap__career_roadmap_agent', mode='current_probe',
                          prompt='For my cloud security skill-gap roadmap, what current tools and technologies should I prioritize based on recent entry-level job postings?'))
    if include_interview_probe:
        cases.append(dict(id='interview_company_probe_1', domain='interview', label='Interview Preparation',
                          expected='interview_preparation_agent', mode='current_probe',
                          prompt='What is the current interview process for an entry-level cybersecurity role at Google? Distinguish confirmed employer information from general interview patterns.'))
    return cases


def band(seconds):
    return "GREEN" if seconds <= 15 else "YELLOW" if seconds <= 30 else "ORANGE" if seconds <= 60 else "RED"


def safe_text(value, limit=60000):
    text = str(value)
    text = re.sub(r"ya29\.[\w.-]+|AIza[\w-]{30,}|Bearer\s+\S+", "[REDACTED]", text, flags=re.I)
    text = re.sub(r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----", "[REDACTED]", text, flags=re.S)
    text = re.sub(r"(?i)((?:access_token|refresh_token|client_secret|api_key|session_id)\s*[=:]\s*)[^\s,}]+", r"\1[REDACTED]", text)
    return text[:limit]


def public_parts(content):
    """Allowlist content fields; never serialize full ADK objects/state."""
    result = []
    for part in getattr(content, "parts", None) or []:
        if getattr(part, "thought", False):
            continue
        if part.text:
            result.append({"text": safe_text(part.text)})
        if part.function_call:
            call = part.function_call
            args = call.args or {}
            result.append({"tool": call.name, "args": {
                key: safe_text(args[key], 10000) for key in ("agent_name", "candidate_id", "request", "query") if key in args
            }})
        if part.function_response:
            result.append({"tool_result": part.function_response.name})
    return result


def interval_union(spans):
    intervals = sorted((s["start"], s["end"]) for s in spans if "end" in s)
    total = 0.0
    end = -1.0
    for start, stop in intervals:
        total += max(0.0, stop - max(start, end))
        end = max(end, stop)
    return round(total, 3)


def normalize_model_timings(result):
    """Generator close can follow nested tools; use response arrival instead.

    Earlier samples can be reconstructed from the corresponding ADK event.
    That fallback includes the small SDK-to-event processing overhead and is
    explicitly labelled as an upper bound, rather than pure network latency.
    """
    for tool in result.get('tools', []):
        if 'necessity' in tool:
            tool['necessity_initial'] = tool.pop('necessity')
    for span in [*result.get('helpers', []), *result.get('tools', [])]:
        if 'end' not in span:
            span['end'] = result['total_seconds']
            span['duration'] = round(span['end'] - span['start'], 3)
            span['censored'] = True
    result['total_retrieval_seconds'] = interval_union(result.get('helpers', []))
    for model in result['models']:
        if 'response_received' not in model:
            candidates = [e['t'] for e in result['events']
                          if e['author'] == model['agent'] and e['parts']
                          and model['start'] <= e['t'] <= model.get('end', float('inf'))]
            if not candidates:
                if result.get('status') != 'completed':
                    model['censored'] = True
                    model['timing_method'] = 'No response before deadline/error; elapsed waiting interval'
                continue
            model['generator_closed_at'] = model.get('end')
            model['generator_lifecycle_seconds'] = model.get('duration')
            model['response_received'] = min(candidates)
            model['timing_method'] = 'ADK response-event arrival upper bound'
        model['end'] = model['response_received']
        model['duration'] = round(model['end'] - model['start'], 3)
    selected = result['actual_specialist']
    result['specialist_model_seconds'] = round(sum(m.get('duration', 0) for m in result['models'] if m['agent'] == selected), 3)
    result['orchestrator_model_seconds'] = round(sum(m.get('duration', 0) for m in result['models'] if 'Orchestration' in m['agent']), 3)
    result['orchestrator_request_start'] = min((m['start'] for m in result['models'] if 'Orchestration' in m['agent']), default=None)
    if 'started_utc' in result:
        result['completed_utc'] = result.pop('started_utc')
    return result


class Observation:
    def __init__(self, case):
        self.case = case
        self.started = time.perf_counter()
        self.events = []
        self.tools = []
        self.helpers = []
        self.models = []
        self.errors = []
        self.seen = set()
        self.agent_starts = {}
        self.model_callbacks = []
        self.first_transfer = None
        self.first_specialist_event = None
        self.first_text = None
        self.final_text = ""

    def now(self):
        return round(time.perf_counter() - self.started, 3)

    def error(self, error, stage):
        message = str(error)
        code = getattr(error, "code", None)
        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            code = 429
        elif "404" in message:
            code = 404
        entry = {"stage": stage, "type": type(error).__name__, "code": str(code) if code is not None else None, "t": self.now()}
        if entry not in self.errors:
            self.errors.append(entry)

    def event(self, event):
        if event.id in self.seen:
            return
        self.seen.add(event.id)  # IDs remain in memory only.
        author = event.author
        parts = public_parts(event.content)
        elapsed = self.now()
        self.events.append(dict(t=elapsed, author=author, parts=parts))
        if author in {d[2] for d in DOMAINS} | {"trust__human_escalation_agent"} and self.first_specialist_event is None:
            self.first_specialist_event = elapsed
        for part in parts:
            if part.get("tool") == "transfer_to_agent" and self.first_transfer is None:
                self.first_transfer = dict(t=elapsed, target=part["args"].get("agent_name"))
        if event.error_code or event.error_message:
            self.error(RuntimeError(str(event.error_code) + " " + str(event.error_message)), "event")

    def result(self, status):
        elapsed = self.now()
        transfer = self.first_transfer
        selected = transfer["target"] if transfer else None
        for tool in self.tools:
            tool["necessity_initial"] = ("UNNECESSARY" if self.case["mode"].startswith("stable") else "OPTIONAL" if self.case["mode"] == "human" else "NECESSARY") if tool["kind"] != "transfer" else "NOT_RETRIEVAL"
            # A fingerprint collision is a review candidate, not proof of redundancy.
            previous = next((t for t in self.tools if t is not tool and t["index"] < tool["index"] and t["fingerprint"] == tool["fingerprint"] and t["name"] == tool["name"]), None)
            tool["duplicate_input_of"] = previous["index"] if previous else None
        return dict(**self.case, status=status, completed_utc=datetime.now(timezone.utc).isoformat(),
                    orchestrator_request_start=min((m["start"] for m in self.models if "Orchestration" in m["agent"]), default=None),
                    total_seconds=elapsed, band=band(elapsed), first_transfer=transfer,
                    actual_specialist=selected, route_match=selected == self.case["expected"],
                    first_specialist_start=self.agent_starts.get(selected),
                    first_specialist_event=self.first_specialist_event,
                    handoff_seconds=round(self.first_specialist_event-transfer["t"], 3) if transfer and self.first_specialist_event is not None else None,
                    first_helper=min((h["start"] for h in self.helpers), default=None),
                    first_text=self.first_text, final_answer=self.final_text,
                    search_helper_invocations=sum(h["kind"] == "search" for h in self.helpers),
                    search_enabled_model_requests=sum(m["search_enabled"] for m in self.models),
                    search_grounded_requests=sum(bool(m.get("search_queries") or m.get("sources")) and m["search_enabled"] for m in self.models),
                    search_queries_reported=sum(len(m.get("search_queries", [])) for m in self.models),
                    url_context_invocations=sum(h["kind"] == "url" for h in self.helpers),
                    total_retrieval_seconds=interval_union(self.helpers),
                    specialist_model_seconds=round(sum(m.get("duration", 0) for m in self.models if m["agent"] == selected), 3),
                    orchestrator_model_seconds=round(sum(m.get("duration", 0) for m in self.models if "Orchestration" in m["agent"]), 3),
                    model_callbacks=self.model_callbacks,
                    tools=self.tools, helpers=self.helpers, models=self.models, errors=self.errors, events=self.events)


@contextlib.contextmanager
def instrumentation():
    """Observe root and nested AgentTool runners; callbacks return None."""
    from google.adk.plugins.base_plugin import BasePlugin
    from google.adk.runners import Runner
    from google.adk.models import Gemini

    class Observer(BasePlugin):
        def __init__(self):
            super().__init__(name="career_latency_observer")

        async def before_agent_callback(self, *, agent, callback_context):
            obs = ACTIVE.get()
            if obs is None:
                return
            obs.agent_starts.setdefault(agent.name, obs.now())
            kind = "search" if "google_search" in agent.name.lower() else "url" if "url_context" in agent.name.lower() else None
            if kind:
                obs.helpers.append(dict(agent=agent.name, kind=kind, start=obs.now(),
                                        index=1+sum(h["kind"] == kind for h in obs.helpers)))
                print(f'HELPER {obs.case["id"]} {kind} #{obs.helpers[-1]["index"]} start={obs.now():.3f}s', flush=True)

        async def after_agent_callback(self, *, agent, callback_context):
            obs = ACTIVE.get()
            if obs:
                span = next((h for h in reversed(obs.helpers) if h["agent"] == agent.name and "end" not in h), None)
                if span:
                    span["end"] = obs.now()
                    span["duration"] = round(span["end"]-span["start"], 3)

        async def before_model_callback(self, *, callback_context, llm_request):
            MODEL_AGENT.set(callback_context.agent_name)
            # Counts only: never persist hidden reasoning or raw request/history.
            contents = llm_request.contents or []
            metrics = dict(history_messages=len(contents),
                visible_history_characters=sum(len(p.text) for c in contents for p in c.parts or []
                                               if p.text and not p.thought),
                instruction_characters=len(str(llm_request.config.system_instruction or "")),
                tool_description_count=len(llm_request.tools_dict))
            MODEL_METRICS.set(metrics)
            if ACTIVE.get():
                ACTIVE.get().model_callbacks.append(dict(agent=callback_context.agent_name,
                                                         t=ACTIVE.get().now(), **metrics))

        async def on_event_callback(self, *, invocation_context, event):
            obs = ACTIVE.get()
            if obs:
                obs.event(event)

        async def before_tool_callback(self, *, tool, tool_args, tool_context):
            obs = ACTIVE.get()
            if obs is None:
                return
            kind = "search" if "google_search" in tool.name.lower() else "url" if "url_context" in tool.name.lower() else "verification" if tool.name.startswith("verify_") and tool.name.endswith("candidate") else "transfer" if tool.name == "transfer_to_agent" else "other"
            fingerprint = hashlib.sha256(json.dumps(tool_args, sort_keys=True, default=str).encode()).hexdigest()
            obs.tools.append(dict(index=len(obs.tools)+1, name=tool.name, kind=kind,
                                  start=obs.now(), fingerprint=fingerprint,
                                  args={k:safe_text(v,10000) for k,v in tool_args.items() if k in {"request","candidate_id","agent_name","query"}}))

        async def after_tool_callback(self, *, tool, tool_args, tool_context, result):
            obs = ACTIVE.get()
            if obs:
                span = next((t for t in reversed(obs.tools) if t["name"] == tool.name and "end" not in t), None)
                if span:
                    span["end"] = obs.now()
                    span["duration"] = round(span["end"]-span["start"],3)
                    if span["kind"] != "transfer":
                        span["quality_output"] = safe_text(result if isinstance(result,str) else json.dumps(result,ensure_ascii=False,default=str))

        async def on_model_error_callback(self, *, callback_context, llm_request, error):
            if ACTIVE.get():
                ACTIVE.get().error(error,"model")

    original_init = Runner.__init__
    original_generate = Gemini.generate_content_async

    def runner_init(self, *args, **kwargs):
        plugins = list(kwargs.get("plugins") or [])
        if ACTIVE.get() and not any(p.name == "career_latency_observer" for p in plugins):
            plugins.append(Observer())
        kwargs["plugins"] = plugins
        original_init(self, *args, **kwargs)

    async def generate(self, llm_request, stream=False):
        obs = ACTIVE.get()
        if obs is None:
            async for response in original_generate(self,llm_request,stream=stream):
                yield response
            return
        if any(e['code'] == '429' for e in obs.errors):
            raise RuntimeError('Diagnostic sample stopped after capacity error; no further model requests')
        config_tools = llm_request.config.tools or []
        model = dict(agent=MODEL_AGENT.get(), start=obs.now(),
                     search_enabled=any(getattr(t,"google_search",None) is not None for t in config_tools),
                     url_enabled=any(getattr(t,"url_context",None) is not None for t in config_tools),
                     search_queries=[], sources=[])
        model.update(MODEL_METRICS.get() or {})
        obs.models.append(model)
        print(f'MODEL {obs.case["id"]} {model["agent"]} start={model["start"]:.3f}s', flush=True)
        try:
            async for response in original_generate(self,llm_request,stream=stream):
                grounding = response.grounding_metadata
                if grounding:
                    model["search_queries"].extend(safe_text(q,2000) for q in grounding.web_search_queries or [])
                    for chunk in grounding.grounding_chunks or []:
                        web = chunk.web
                        if web:
                            source = {"url":safe_text(web.uri,5000),"title":safe_text(web.title,1000)}
                            if source not in model["sources"]:
                                model["sources"].append(source)
                model['response_received'] = obs.now()
                model['timing_method'] = 'SDK response arrival before downstream tools'
                print(f'MODEL_RESULT {obs.case["id"]} {model["agent"]} wait={model["response_received"]-model["start"]:.3f}s', flush=True)
                yield response
        except Exception as error:
            obs.error(error,"model_transport")
            raise
        finally:
            model["end"] = obs.now()
            model["duration"] = round(model["end"]-model["start"],3)

    with patch.object(Runner,"__init__",runner_init), patch.object(Gemini,"generate_content_async",generate):
        yield


async def execute(case, timeout):
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from agents.career.workflow.agent import root_agent
    obs = Observation(case)
    token = ACTIVE.set(obs)
    runner = None
    status = "completed"
    try:
        service = InMemorySessionService()
        runner = Runner(app_name="career_diagnostics",agent=root_agent,session_service=service)
        session = await service.create_session(app_name="career_diagnostics",user_id="synthetic-diagnostic-client")
        async with asyncio.timeout(timeout):
            async with contextlib.aclosing(runner.run_async(user_id=session.user_id,session_id=session.id,
                    new_message=types.Content(role="user",parts=[types.Part(text=case["prompt"])]))) as events:
                async for event in events:
                    # User-visible text is measured only on the outer runner.
                    helper = "google_search" in event.author.lower() or "url_context" in event.author.lower()
                    texts = [p["text"] for p in public_parts(event.content) if "text" in p]
                    if texts and not helper:
                        if obs.first_text is None:
                            obs.first_text = obs.now()
                        obs.final_text = "\n".join(texts)
    except TimeoutError as error:
        status = "timeout_censored"
        obs.error(error,"deadline")
    except Exception as error:
        status = "failed"
        obs.error(error,"runner")
    finally:
        if runner:
            await runner.close()
        ACTIVE.reset(token)
    if obs.errors and status == "completed":
        status = "runtime_error"
    return normalize_model_timings(obs.result(status))


async def main_async(args, cases_override=None):
    expected = {"google-cloud-aiplatform":"1.165.1","google-adk":"2.12.0"}
    versions = {k:importlib.metadata.version(k) for k in expected}
    if versions != expected:
        raise SystemExit("Use the pinned workflow SDK/ADK environment: "+str(expected))
    sys.path.insert(0,str(ROOT))
    # ADC is supplied by the authenticated environment; secrets are never read
    # into artifacts. Optional dotenv loading uses the application's location.
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent/".env")
    os.environ.update(GOOGLE_CLOUD_PROJECT="cosc-490",GOOGLE_CLOUD_LOCATION="us-west1",GOOGLE_GENAI_USE_VERTEXAI="true")
    for name in ("google","vertexai"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    # SDK error tracebacks are not diagnostic artifacts. Keep only the safe
    # structured error summaries above; do not copy raw SDK logs/payloads.
    logging.disable(logging.CRITICAL)
    source_files = list((ROOT/"agents/career/workflow").glob("*.py"))
    source_hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    data = {"schema_version":1,"versions":versions,"checkpoint":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
            "source_hashes":source_hashes,"execution":"local source workflow; Vertex model requests only; no Agent Engine endpoints","runs":[]}
    if args.resume and args.output.exists():
        data = json.loads(args.output.read_text(encoding="utf8"))
        for result in data["runs"]:
            normalize_model_timings(result)
        if data["source_hashes"] != source_hashes:
            raise SystemExit("Source changed; use a new output file instead of mixing baselines.")
    completed = {r["id"] for r in data["runs"]}
    selected_plan = cases_override if cases_override is not None else plan(args.research_probes, args.roadmap_probe, args.interview_probe)
    data['planned_case_ids'] = list(dict.fromkeys([*data.get('planned_case_ids', []), *(args.case or [c['id'] for c in selected_plan])]))
    cases = [c for c in selected_plan if c["id"] not in completed and (not args.case or c["id"] in args.case)]
    with instrumentation():
        for case in cases:
            print("START "+case["id"],flush=True)
            result = await execute(case,args.timeout)
            data["runs"].append(result)
            data["remaining"] = [c for c in data['planned_case_ids'] if c not in {r['id'] for r in data['runs']}]
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
            print(json.dumps({k:result[k] for k in ("id","status","total_seconds","band","actual_specialist","search_helper_invocations","search_queries_reported","url_context_invocations","errors")}),flush=True)
            if any(e["code"] == "429" for e in result["errors"]):
                print("429: live batch stopped. Cool down before explicitly resuming other samples; no automatic retry.",flush=True)
                break
            await asyncio.sleep(args.pace)
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in source_hashes.items())


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live",action="store_true",help="Permit live local-workflow model requests")
    parser.add_argument("--resume",action="store_true")
    parser.add_argument("--case",action="append",help="Exact sample ID; may repeat")
    parser.add_argument('--research-probes',action='store_true',help='Add two explicit research-readiness probes when the degree-choice prompt routes elsewhere')
    parser.add_argument('--roadmap-probe',action='store_true',help='Add a clarified current skill-roadmap probe when the generic market prompt routes elsewhere')
    parser.add_argument('--interview-probe',action='store_true',help='Add a Google-specific current interview probe when the generic employer test is under-specified')
    parser.add_argument("--output",type=Path,default=ROOT/"tests/diagnostics/career_baseline.json")
    parser.add_argument("--timeout",type=float,default=240,help="Diagnostic cutoff, not an application timeout")
    parser.add_argument("--pace",type=float,default=3,help="Seconds between samples; never concurrent")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps(plan(args.research_probes,args.roadmap_probe,args.interview_probe),indent=2))
        return
    if args.output.exists() and not args.resume:
        raise SystemExit("Output already exists; use --resume or a new --output path.")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    cli()
