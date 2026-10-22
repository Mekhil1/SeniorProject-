"""Invocation-local evidence registry and bounded Career Exploration tools.

Built-in Search and URL Context stay on separate helper agents. AgentTool wraps
each helper; Python, rather than the parent model, transports evidence strings.
No output_key is needed: it would expose raw helper output to the parent.
"""

from copy import deepcopy
import re
from typing import Any
from urllib.parse import urlsplit

from google.adk.models.llm_response import LlmResponse
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.base_tool import BaseTool
from google.genai import types
from pydantic import BaseModel, ConfigDict, field_validator


PREFIX = "temp:career_evidence_"
CANDIDATES = PREFIX + "candidates"
VERIFICATIONS = PREFIX + "verifications"
CONTROL = PREFIX + "control"
HANDOFFS = PREFIX + "handoffs"
VERIFY_TOOL = "verify_evidence_candidate"
DISCOVERY_STATUSES = {"CANDIDATE CURRENT", "POSSIBLY HISTORICAL", "INSUFFICIENT EVIDENCE"}
VERIFICATION_STATUSES = {
    "VERIFIED CURRENT", "CURRENT STATUS UNVERIFIED", "HISTORICAL", "UNSUPPORTED"
}


class EvidenceCandidate(BaseModel):
    """Frozen strings: no URL normalization, decoding, or case conversion."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    candidate_id: str
    claim: str
    source_url: str
    source_type: str
    source_title: str
    apparent_date_or_cycle: str
    discovery_support: str
    discovery_limits: str
    discovery_status: str

    @field_validator("claim")
    @classmethod
    def nonempty_claim(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A candidate needs a claim")
        return value

    @field_validator("source_url")
    @classmethod
    def exact_http_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("A candidate needs an HTTP(S) URL")
        if re.search(r"[\s<>]", value):
            raise ValueError("URL contains whitespace or markup")
        return value

    @field_validator("discovery_status")
    @classmethod
    def discovery_only(cls, value: str) -> str:
        if value not in DISCOVERY_STATUSES:
            raise ValueError("Discovery cannot verify a candidate")
        return value


def _fields(text: str) -> dict[str, str]:
    """Parse the existing helper protocol without regenerating field values."""
    labels = (
        "CLAIM|SOURCE URL|SOURCE TYPE|SOURCE TITLE|APPARENT DATE OR CYCLE|"
        "DISCOVERY SUPPORT|DISCOVERY LIMITS|DISCOVERY STATUS|REQUIRES URL CONTEXT|"
        "SOURCE DATE OR CYCLE|PAGE EVIDENCE|SUPPORTED SCOPE|NOT ESTABLISHED|STATUS|WHY"
    )
    matches = list(re.finditer(r"^(" + labels + r"):[ \t]*", text, re.M))
    result = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        value = text[match.end():end].strip()
        # Strip record separators, never punctuation belonging to a URL/claim.
        value = re.sub(r"\n\s*(?:\*\*\*|---)\s*$", "", value)
        if match[1] in result:
            raise ValueError("Duplicate evidence field")
        result[match[1]] = value
    return result


def parse_discovery(text: str) -> list[dict[str, str]]:
    blocks = re.split(r"^EVIDENCE CANDIDATE \d+\s*$", text, flags=re.M)[1:]
    if len(blocks) > 3:
        raise ValueError("Discovery returned more than three candidates")
    names = {
        "claim": "CLAIM", "source_url": "SOURCE URL", "source_type": "SOURCE TYPE",
        "source_title": "SOURCE TITLE", "apparent_date_or_cycle": "APPARENT DATE OR CYCLE",
        "discovery_support": "DISCOVERY SUPPORT", "discovery_limits": "DISCOVERY LIMITS",
        "discovery_status": "DISCOVERY STATUS",
    }
    records = []
    for block in blocks:
        fields = _fields(block)
        records.append({key: fields[label] for key, label in names.items()})
    return records


class CandidateRegistry:
    """Copy-on-write state updates are tracked by ADK State.__setitem__."""

    def __init__(self, state: Any):
        self.state = state

    def register(self, candidates: list[dict[str, str]]) -> list[dict[str, str]]:
        if len(candidates) > 3:
            raise ValueError("At most three candidates are allowed")
        if self.state.get(CANDIDATES):
            raise ValueError("Discovery candidates are already registered")
        validated = [
            EvidenceCandidate(candidate_id=f"C{i}", **record)
            for i, record in enumerate(candidates, 1)
        ]
        self.state[CANDIDATES] = {c.candidate_id: c.model_dump() for c in validated}
        return [
            {"candidate_id": c.candidate_id, "claim": c.claim,
             "source_type": c.source_type, "discovery_status": c.discovery_status}
            for c in validated
        ]

    def get(self, candidate_id: str) -> EvidenceCandidate:
        record = self.state.get(CANDIDATES, {}).get(candidate_id)
        if record is None:
            raise ValueError("Unknown candidate ID")
        return EvidenceCandidate.model_validate(deepcopy(record))

    def reserve_verification(self, candidate_id: str) -> tuple[EvidenceCandidate, str]:
        control = deepcopy(self.state.get(CONTROL, {}))
        if control.get("verification_attempts", 0) >= 2:
            raise ValueError("Verification budget exhausted")
        control["verification_attempts"] = control.get("verification_attempts", 0) + 1
        self.state[CONTROL] = control  # Count invalid/failed attempts as well.
        candidate = self.get(candidate_id)
        if candidate_id in control.get("selected", []):
            raise ValueError("Candidate already selected")
        control["selected"] = [*control.get("selected", []), candidate_id]
        self.state[CONTROL] = control
        payload = f"CLAIM:\n{candidate.claim}\n\nSOURCE URL:\n{candidate.source_url}"
        sent_claim, sent_url = payload.removeprefix("CLAIM:\n").rsplit("\n\nSOURCE URL:\n", 1)
        assert sent_claim == candidate.claim and sent_url == candidate.source_url
        # These audit values are private state, never parent-model tool output.
        self.state[HANDOFFS] = [*self.state.get(HANDOFFS, []), {
            "candidate_id": candidate_id, "claim": candidate.claim,
            "stored_url": candidate.source_url, "verifier_url": sent_url,
            "request": payload,
        }]
        return candidate, payload

    def store_verification(self, candidate: EvidenceCandidate, output: str) -> dict:
        try:
            fields = _fields(output)
            status = fields.get("STATUS", "UNSUPPORTED")
            if status not in VERIFICATION_STATUSES:
                raise ValueError("Invalid verification status")
            date = fields.get("SOURCE DATE OR CYCLE", "UNKNOWN")
            if "copyright" in date.lower():
                date = "UNKNOWN"
            if status == "VERIFIED CURRENT" and date.upper() == "UNKNOWN":
                status = "CURRENT STATUS UNVERIFIED"
            record = {
                "candidate_id": candidate.candidate_id,
                "claim": candidate.claim, "source_url": candidate.source_url,
                "source_title": fields.get("SOURCE TITLE", "UNKNOWN"),
                "source_date_or_cycle": date, "status": status,
                "page_evidence": fields.get("PAGE EVIDENCE", "UNKNOWN"),
                "supported_scope": fields.get("SUPPORTED SCOPE", "UNKNOWN"),
                "not_established": fields.get("NOT ESTABLISHED", "UNKNOWN"),
                "why": fields.get("WHY", "Verification did not establish this claim."),
            }
        except ValueError:
            record = {"candidate_id": candidate.candidate_id, "claim": candidate.claim,
                      "source_url": candidate.source_url, "status": "UNSUPPORTED",
                      "source_date_or_cycle": "UNKNOWN", "supported_scope": "UNKNOWN",
                      "not_established": "Malformed verification output", "why": "Verification failed."}
        records = deepcopy(self.state.get(VERIFICATIONS, {}))
        records[candidate.candidate_id] = record
        self.state[VERIFICATIONS] = records
        return deepcopy(record)


def begin_evidence_invocation(callback_context):
    """A fresh registry per invocation, including reused chat sessions."""
    state = callback_context.state
    if state.get(CONTROL, {}).get("invocation") != callback_context.invocation_id:
        state[CONTROL] = {"invocation": callback_context.invocation_id,
                          "search_attempts": 0, "verification_attempts": 0, "selected": []}
        state[CANDIDATES] = {}
        state[VERIFICATIONS] = {}
        state[HANDOFFS] = []


def render_evidence(state) -> str:
    """Only registered verification records can enter the factual section."""
    records = state.get(VERIFICATIONS, {})
    lines = ["### Morgan cybersecurity resources: evidence and status"]
    if not records:
        lines.append("No current Morgan-specific resource could be verified in this request.")
    for record in records.values():
        lines.extend(["", f"**{record['candidate_id']} — {record['status']}**",
                      f"Proposed claim: {record['claim']}"])
        if record['status'] in {"VERIFIED CURRENT", "HISTORICAL"}:
            lines.append(f"Supported scope: {record['supported_scope']}")
        lines.extend([f"Evidence limits: {record['not_established']}",
                      f"Assessment: {record['why']}",
                      f"Source: [Exact inspected source](<{record['source_url']}>)"])
    lines.extend(["", "### General exploration guidance",
                  "Try a small defensive security lab or threat-modeling exercise to explore your interests. "
                  "Ask the relevant university office to confirm current eligibility, openings, and dates "
                  "before relying on a resource."])
    return "\n\n".join(line for line in lines if line)


class DiscoveryRegistryTool(AgentTool):
    """Run the unchanged Search tool stack; intercept output before the parent."""

    async def run_async(self, *, args, tool_context):
        begin_evidence_invocation(tool_context)
        control = deepcopy(tool_context.state[CONTROL])
        candidates = tool_context.state.get(CANDIDATES, {})
        usable = any(c["source_type"] in {"Official Morgan", "Official Government", "Government"}
                     for c in candidates.values())
        if (control["search_attempts"] >= 2 or usable
                or control["verification_attempts"]):
            return {"error": "Discovery is closed; verify registered IDs or finish."}
        control["search_attempts"] += 1
        tool_context.state[CONTROL] = control
        if candidates:  # Retry may replace non-official leads, never usable official records.
            tool_context.state[CANDIDATES] = {}
        # Ignore model-written research text: use the actual student's request.
        request = "\n".join(p.text for p in tool_context.user_content.parts
                            if p.text and not p.thought)
        try:
            output = await super().run_async(args={"request": request}, tool_context=tool_context)
            summary = CandidateRegistry(tool_context.state).register(parse_discovery(output))
        except (ValueError, KeyError, TypeError):
            return {"candidates": [], "error": "Discovery did not return valid candidate records."}
        return {"candidates": summary, "next_action": "Select candidate IDs only; never supply URLs."}


class VerifyEvidenceCandidateTool(BaseTool):
    """The public function schema has only candidate_id, never URL or claim."""

    def __init__(self, verifier):
        super().__init__(name=VERIFY_TOOL, description="Verify a registered candidate by ID (C1, C2, C3).")
        self._verifier = verifier

    def _get_declaration(self):
        return types.FunctionDeclaration(name=self.name, description=self.description,
            parameters_json_schema={"type": "object", "properties": {
                "candidate_id": {"type": "string", "enum": ["C1", "C2", "C3"]}},
                "required": ["candidate_id"], "additionalProperties": False})

    async def run_async(self, *, args, tool_context):
        begin_evidence_invocation(tool_context)
        registry = CandidateRegistry(tool_context.state)
        if set(args) != {"candidate_id"} or not isinstance(args["candidate_id"], str):
            try:
                registry.reserve_verification("")  # Invalid calls consume the same finite budget.
            except ValueError:
                pass
            return {"error": "Only candidate_id is accepted; URL/claim overrides are forbidden."}
        try:
            candidate, payload = registry.reserve_verification(args["candidate_id"])
        except ValueError as error:
            return {"error": str(error)}
        output = await self._verifier.run_async(args={"request": payload}, tool_context=tool_context)
        record = registry.store_verification(candidate, output)
        # Do not make the parent LLM transcribe citation/status fields.
        return {"candidate_id": candidate.candidate_id, "status": record["status"],
                "summary": record["why"], "next_action": "Select another ID or finish; Python renders evidence."}


def evidence_tools(search_agent, verifier_agent):
    return [DiscoveryRegistryTool(agent=search_agent),
            VerifyEvidenceCandidateTool(AgentTool(agent=verifier_agent))]


def bounded_evidence_step(callback_context, llm_request):
    """Stop retrieval in Python, not by hoping the model follows a budget."""
    begin_evidence_invocation(callback_context)
    state = callback_context.state
    control = state[CONTROL]
    if control["verification_attempts"] >= 2:
        return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=render_evidence(state))]))
    if not control["search_attempts"]:
        return None  # Normal non-retrieval Career Exploration stays unchanged.
    candidates = state.get(CANDIDATES, {})
    usable = any(c["source_type"] in {"Official Morgan", "Official Government", "Government"}
                 for c in candidates.values())
    done = (control["verification_attempts"] >= min(2, len(candidates)) if usable
            else control["search_attempts"] >= 2)
    if done:
        return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=render_evidence(state))]))
    name = VERIFY_TOOL if usable else "Career_Exploration_Agent_google_search_agent"
    selected = llm_request.tools_dict[name]
    llm_request.tools_dict = {name: selected}
    llm_request.config.tools = [types.Tool(function_declarations=[selected._get_declaration()])]
    llm_request.config.tool_config = types.ToolConfig(function_calling_config=
        types.FunctionCallingConfig(mode="ANY", allowed_function_names=[name]))
    return None
