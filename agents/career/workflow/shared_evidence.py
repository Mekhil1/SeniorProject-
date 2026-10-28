"""Shared bounded evidence policy; legacy Career registry remains unchanged.

The adapter maps only the legacy registry's four keys into specialist-local
ADK temporary state. Models never supply verification URLs or final statuses.
"""
from copy import deepcopy
from dataclasses import dataclass
import json
import re
from types import SimpleNamespace
from urllib.parse import urlsplit

from google.adk.models.llm_response import LlmResponse
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.base_tool import BaseTool
from google.genai import types

from . import evidence as legacy


def _networking_delivery_support(claim, data):
    """Fail closed for benefit delivery; retain literal, narrower page support.

    Only Networking calls this rule. Verifier summaries/flags are not proof:
    each claimed benefit needs a direct operational clause in page_evidence.
    """
    benefits = (r"\bmentor(?:ing|ship|s)?\b", r"\bworkshops?\b",
                r"\b(?:networking (?:opportunities|events)|recruiter access|employer access|industry access|partnerships?)\b",
                r"\b(?:programming|student benefits)\b")
    aspiration = r"\b(?:aims? to|seeks? to|strives? to|goals?|vision|mission|intends? to|designed to|planned|expected|hopes? to)\b"
    needed = [p for p in benefits if re.search(p, claim, re.I)]
    goal = re.search(aspiration, claim, re.I)
    first_benefit = min((m.start() for p in needed if (m := re.search(p, claim, re.I))), default=len(claim))
    # A statement *about* a goal does not assert delivered benefits.
    if goal and goal.start() < first_benefit and not re.search(
            r"\b(?:currently|receives?|provides|delivers|offers|ongoing)\b", claim[goal.end():], re.I):
        return True, ""
    clauses = re.split(r"[.!?;\n]+", data["page_evidence"])
    operational_clauses = []
    goal_section = False
    for line in data["page_evidence"].splitlines():
        heading = line.strip(" #*-:\t").lower()
        if heading in {"goals", "our goals", "mission", "our mission", "vision", "our vision"}:
            goal_section = True
        elif heading in {"current operations", "current availability", "current programming", "registration"}:
            goal_section = False
        elif not goal_section:
            operational_clauses.extend(re.split(r"[.!?;]+", line))
    direct = []
    years = set(re.findall(r"\b20\d{2}\b", data["source_date_or_cycle"]))
    for clause in operational_clauses:
        dated = set(re.findall(r"\b20\d{2}\b", clause))
        if re.search(aspiration, clause, re.I) or re.search(r"\b(?:not|no longer|will|would)\b", clause, re.I):
            continue
        if dated and years and not dated & years:
            continue
        operation = r"\b(?:can (?:register|attend|enroll|participate)|registration is open|currently (?:offers?|provides?|runs?|hosts?|delivers?)|(?:offers|provides|runs|hosts|delivers) (?:weekly|monthly|ongoing)|(?:is|are) (?:currently )?(?:available|running|open))\b"
        if re.search(operation, clause, re.I):
            direct.append(clause.strip())
    supported = []
    for clause in clauses:
        for part in re.split(r"\band\b", clause, flags=re.I):
            if any(re.search(p, part, re.I) for p in benefits) or re.search(aspiration, part, re.I):
                continue
            membership = r"\b(?:invited to join|invites? (?:new )?members|membership (?:is )?open|exists)\b|\bis (?:the |a |an )?[^.;!?]{0,70}\b(?:club|organization)\b"
            if re.search(membership, part, re.I):
                supported.append(part.strip())
    supported.extend(c for c in direct if any(re.search(p, c, re.I) for p in needed))
    complete = all(any(re.search(p, c, re.I) for c in direct) for p in needed)
    return complete, "; ".join(dict.fromkeys(supported))


DISCOVERY_PROTOCOL = """
WAVE 3 DISCOVERY TRANSPORT (takes precedence over earlier output formats):
One grounded discovery response only. Return at most the requested candidate
limit. No surrounding prose. For each source use these exact field labels:
EVIDENCE CANDIDATE 1
CLAIM: one precise proposed claim relevant to the original question
SOURCE URL: exact discovered HTTP(S) URL, never reconstructed
SOURCE TYPE: official owner / other
SOURCE TITLE: title
APPARENT DATE OR CYCLE: explicit date/cycle or UNKNOWN
DISCOVERY SUPPORT: what discovery actually supports
DISCOVERY LIMITS: what remains unproven
DISCOVERY STATUS: CANDIDATE CURRENT or POSSIBLY HISTORICAL or INSUFFICIENT EVIDENCE
If no usable source exists return NO CANDIDATES. Discovery cannot verify facts.
"""
VERIFICATION_PROTOCOL = """
WAVE 3 VERIFICATION TRANSPORT (takes precedence over earlier output formats):
Inspect only the exact SOURCE URL supplied in the request. Do not substitute,
regenerate or browse additional URLs. Assess only the exact CLAIM in the request.
Return a single JSON object, no fences, with these fields:
status: VERIFIED CURRENT / CURRENT STATUS UNVERIFIED / HISTORICAL / UNSUPPORTED
source_title, source_date_or_cycle, page_evidence, supported_scope,
not_established, why: strings
page_read, current_claim_explicit: booleans
authority_host: actual publisher hostname of inspected content
facts: object of requested certification facts only, otherwise empty object
Use UNKNOWN for missing dates. Copyright dates are not currentness evidence.
VERIFIED CURRENT requires explicit current evidence for the entire proposed
claim. Historical events, sponsors and organizational goals do not establish
active partnerships, recruiting relationships or student access. Research
activity does not establish openings, funding, application status or eligibility.
Certification facts must be explicit official-vendor facts; include only requested
keys exam_version, exam_code, price, currency, region, retirement_date, eligibility.
No discounts, training partners, salaries or alternatives unless requested.
"""
PARENT_PROTOCOL = """
WAVE 3 PYTHON EVIDENCE BOUNDARY:
For current factual requests use the discovery helper once, then select only
registered candidate IDs for verification. Never supply or rewrite URLs/claims.
Python enforces candidate/verification budgets and renders final evidence.
Discovery is not verification. Preserve VERIFIED CURRENT, CURRENT STATUS
UNVERIFIED, HISTORICAL and UNSUPPORTED without upgrades. Do not add assertions
about current partnerships, access, openings, funding or vendor offers.
Stable conceptual coaching remains tool-free. Certification decision guidance
must stay generic: cost, role relevance, practical experience and target postings;
no invented student discounts, eligibility, pricing or employer rankings.
"""


class NamespaceState:
    def __init__(self, state, namespace):
        if not re.fullmatch(r"[a-z_]+", namespace):
            raise ValueError("Invalid namespace")
        self.state = state
        self.keys = {key: f"temp:evidence:{namespace}:{suffix}" for key, suffix in (
            (legacy.CONTROL, "control"), (legacy.CANDIDATES, "candidates"),
            (legacy.VERIFICATIONS, "verifications"), (legacy.HANDOFFS, "handoffs"))}

    def __getitem__(self, key):
        return self.state[self.keys[key]]

    def __setitem__(self, key, value):
        self.state[self.keys[key]] = value

    def get(self, key, default=None):
        return self.state.get(self.keys[key], default)


def question(context):
    return "\n".join(p.text for p in context.user_content.parts if p.text and not p.thought)


def response(text):
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


def literal(text):
    # Render helper strings as plain Markdown text, never helper-provided markup.
    return re.sub(r"([\\`*_{}\[\]<>#|])", r"\\\1", str(text)).replace("\n", " ")


@dataclass(frozen=True)
class EvidencePolicy:
    namespace: str
    label: str
    candidate_limit: int
    verification_limit: int

    @property
    def verify_name(self):
        return f"verify_{self.namespace}_candidate"

    def state(self, context):
        return NamespaceState(context.state, self.namespace)

    def begin(self, callback_context):
        legacy.begin_evidence_invocation(SimpleNamespace(
            state=self.state(callback_context), invocation_id=callback_context.invocation_id))

    def current(self, text):
        text = text.lower().replace("not current programs", "")
        if self.namespace == "certification":
            return bool(re.search(r"\b(version|exam code|price|pricing|retirement|eligibility|discount|voucher)\b", text))
        return bool(re.search(r"\b(current|active|available|openings|funding|eligib\w*|partnerships|recruiting relationships)\b", text))

    def register(self, context, candidates):
        if len(candidates) > self.candidate_limit:
            raise ValueError("Candidate budget exceeded")
        return legacy.CandidateRegistry(self.state(context)).register(candidates)

    def reserve(self, context, candidate_id):
        state = self.state(context)
        if state[legacy.CONTROL]["verification_attempts"] >= self.verification_limit:
            raise ValueError("Verification budget exhausted")
        return legacy.CandidateRegistry(state).reserve_verification(candidate_id)

    def official(self, host, text):
        host = host.lower().rstrip(".")
        if self.namespace == "networking":
            return host == "morgan.edu" or host.endswith(".morgan.edu")
        if self.namespace == "research":
            return host.endswith((".edu", ".gov"))
        vendors = {"comptia": "comptia.org", "microsoft": "microsoft.com",
                   "cisco": "cisco.com", "isc2": "isc2.org", "aws": "aws.amazon.com"}
        return any(name in text.lower() and (host == domain or host.endswith("." + domain))
                   for name, domain in vendors.items())

    def store(self, context, candidate, output):
        state = self.state(context)
        try:
            data = json.loads(output)
            required = {"status", "source_title", "source_date_or_cycle", "page_evidence",
                        "supported_scope", "not_established", "why", "page_read",
                        "current_claim_explicit", "authority_host", "facts"}
            if set(data) != required or data["status"] not in legacy.VERIFICATION_STATUSES:
                raise ValueError("Invalid verification schema")
            if any(not isinstance(data[k], str) for k in required - {"facts", "page_read", "current_claim_explicit"}):
                raise ValueError("Invalid verification field types")
            if any(type(data[k]) is not bool for k in ("page_read", "current_claim_explicit")):
                raise ValueError("Invalid evidence flags")
            if not isinstance(data["facts"], dict):
                raise ValueError("Invalid facts")
            reported = data["status"]
            date = data["source_date_or_cycle"]
            exact_host = urlsplit(candidate.source_url).hostname or ""
            # Grounding redirect URLs are kept byte-for-byte; their publisher is
            # supplied by the inspecting helper, never by the parent specialist.
            redirect = exact_host == "vertexaisearch.cloud.google.com"
            authority = data["authority_host"].lower().rstrip(".")
            owner_matches = redirect or exact_host.lower() == authority
            complete = (data["page_read"] and data["current_claim_explicit"]
                        and data["page_evidence"].strip() not in {"", "UNKNOWN"}
                        and data["supported_scope"].strip() not in {"", "UNKNOWN"}
                        and date.strip().upper() not in {"", "UNKNOWN"}
                        and "copyright" not in date.lower()
                        and owner_matches and self.official(authority, question(context)))
            networking_scope = ""
            if self.namespace == "networking" and reported == "VERIFIED CURRENT":
                delivery, networking_scope = _networking_delivery_support(candidate.claim, data)
                if not delivery:
                    complete = False
                    data["not_established"] = "Current delivery of every claimed benefit is not directly established; goals/vision are not delivery evidence."
            if reported == "VERIFIED CURRENT" and not complete:
                data["status"] = "CURRENT STATUS UNVERIFIED"
                data["why"] = "Current claim not established by explicit dated official evidence."
            labels = {"status": "STATUS", "source_title": "SOURCE TITLE",
                      "source_date_or_cycle": "SOURCE DATE OR CYCLE", "page_evidence": "PAGE EVIDENCE",
                      "supported_scope": "SUPPORTED SCOPE", "not_established": "NOT ESTABLISHED", "why": "WHY"}
            # Reject protocol injection rather than parsing helper field labels.
            if any(re.search(r"(?m)^[A-Z][A-Z ]+:", data[k]) for k in labels):
                raise ValueError("Embedded protocol label")
            record = legacy.CandidateRegistry(state).store_verification(candidate,
                "\n".join(f"{label}: {data[key]}" for key, label in labels.items()))
            record["reported_status"] = reported
            if self.namespace == "networking" and networking_scope and data["page_read"] and owner_matches and self.official(authority, question(context)):
                record["networking_supported_scope"] = networking_scope
            record["facts"] = {k: v for k, v in data["facts"].items()
                               if k in self.requested_facts(question(context)) and isinstance(v, str)
                               and self.safe_fact(k, v)}
        except (ValueError, TypeError, KeyError):
            record = legacy.CandidateRegistry(state).store_verification(candidate, "STATUS: UNSUPPORTED")
        records = deepcopy(state.get(legacy.VERIFICATIONS, {}))
        records[candidate.candidate_id] = record
        state[legacy.VERIFICATIONS] = records
        return record

    @staticmethod
    def safe_fact(key, value):
        # Narrow fact fields cannot carry unrelated offers or prose.
        patterns = {"price": r"[0-9]+(?:[.,][0-9]{1,2})?", "currency": r"[A-Z]{3}",
                    "exam_code": r"[A-Za-z0-9+ -]{1,40}", "exam_version": r"[A-Za-z0-9+ .-]{1,60}",
                    "region": r"[A-Za-z .-]{1,60}", "retirement_date": r"[A-Za-z0-9 ,/-]{1,60}"}
        return bool(re.fullmatch(patterns[key], value)) if key in patterns else len(value) <= 300

    def requested_facts(self, text):
        text = text.lower()
        keys = set()
        for pattern, fields in [(r"version|exam code", {"exam_version", "exam_code"}),
                                (r"price|cost|pricing", {"price", "currency", "region"}),
                                (r"retire", {"retirement_date"}), (r"eligib", {"eligibility"})]:
            if re.search(pattern, text):
                keys.update(fields)
        return keys

    def render(self, context):
        records = self.state(context).get(legacy.VERIFICATIONS, {})
        lines = [f"### {self.label}: evidence and status"]
        if not records:
            lines.append("CURRENT STATUS UNVERIFIED — no requested current fact was verified in this request.")
        for record in records.values():
            lines.extend([f"**{record['candidate_id']} — {record['status']}**"])
            if self.namespace != "certification":
                lines.append("Proposed claim (not an assertion): " + literal(record["claim"]))
            if record["status"] in {"VERIFIED CURRENT", "HISTORICAL"}:
                if self.namespace == "certification":
                    for key, value in record.get("facts", {}).items():
                        lines.append(f"{key.replace('_', ' ')}: {literal(value)}")
                    if not record.get("facts"):
                        lines.append("Requested fact values were not supplied in a usable form.")
                else:
                    lines.append("Supported scope: " + literal(record["supported_scope"]))
            elif self.namespace == "networking" and record.get("networking_supported_scope"):
                lines.append("Supported narrower source scope (not verification of the whole claim): " + literal(record["networking_supported_scope"]))
            if self.namespace != "certification":
                lines.append("Evidence limits: " + literal(record["not_established"]))
            lines.extend(["Assessment: " + literal(record["why"]) if self.namespace != "certification"
                          else "Assessment: only verified requested fact values appear above.",
                          f"Source: [Exact inspected source](<{record['source_url']}>)"])
        lines.append("Confirm unresolved current details with the official owner before relying on them.")
        return "\n\n".join(lines)

    def tools(self, search_agent, verifier_agent):
        return [SharedDiscovery(agent=search_agent, policy=self),
                SharedVerification(self, AgentTool(agent=verifier_agent))]

    def step(self, callback_context, llm_request):
        self.begin(callback_context)
        state = self.state(callback_context)
        control = state[legacy.CONTROL]
        active = self.current(question(callback_context)) or bool(control["search_attempts"])
        if not active:
            # Stable guidance cannot silently turn into retrieval.
            removed = {n for n in llm_request.tools_dict if n.endswith("google_search_agent") or n == self.verify_name}
            llm_request.tools_dict = {n: t for n, t in llm_request.tools_dict.items() if n not in removed}
            declarations = [t._get_declaration() for t in llm_request.tools_dict.values()]
            llm_request.config.tools = [types.Tool(function_declarations=declarations)] if declarations else []
            return None
        candidates = state.get(legacy.CANDIDATES, {})
        if control["search_attempts"] and (not candidates or control["verification_attempts"] >= min(self.verification_limit, len(candidates))):
            return response(self.render(callback_context))
        name = self.verify_name if control["search_attempts"] else next(
            n for n in llm_request.tools_dict if n.endswith("google_search_agent"))
        selected = llm_request.tools_dict[name]
        llm_request.tools_dict = {name: selected}
        llm_request.config.tools = [types.Tool(function_declarations=[selected._get_declaration()])]
        llm_request.config.tool_config = types.ToolConfig(function_calling_config=
            types.FunctionCallingConfig(mode="ANY", allowed_function_names=[name]))

    def after(self, callback_context, llm_response):
        content = llm_response.content
        if not content:
            return None
        calls = [p for p in content.parts if p.function_call or p.thought]
        if self.current(question(callback_context)) or self.state(callback_context)[legacy.CONTROL]["search_attempts"]:
            return llm_response.model_copy(update={"content": types.Content(role="model", parts=calls)}) if any(p.function_call for p in calls) else response(self.render(callback_context))
        if self.namespace == "certification" and re.search(r"decide|worth|choose|consider", question(callback_context), re.I) and not any(p.function_call for p in calls):
            return response("### Deciding whether to pursue a certification\n\n"
                "- Compare the credential's subject matter with the role you want.\n"
                "- Consider total cost and preparation time alongside hands-on experience.\n"
                "- Review job postings you care about to see whether they request the credential.\n"
                "- Identify practical projects that demonstrate the same skills.\n"
                "- Choose a manageable study plan and reassess your progress before spending money.\n\n"
                "Check official requirements and costs when you are ready to make a specific choice.")
        return None


class SharedDiscovery(AgentTool):
    def __init__(self, *, agent, policy):
        super().__init__(agent=agent)
        self.policy = policy

    async def run_async(self, *, args, tool_context):
        policy = self.policy
        policy.begin(tool_context)
        state = policy.state(tool_context)
        control = deepcopy(state[legacy.CONTROL])
        if control["search_attempts"]:
            return {"error": "Discovery budget exhausted"}
        control["search_attempts"] += 1
        state[legacy.CONTROL] = control
        request = policy.discovery_request(tool_context) if hasattr(policy, "discovery_request") else question(tool_context) + f"\nCandidate limit: {policy.candidate_limit}." + DISCOVERY_PROTOCOL
        # Provider failures propagate for diagnosis; never retry or disguise them.
        output = await super().run_async(args={"request": request}, tool_context=tool_context)
        try:
            rows = legacy.parse_discovery(output)
            if policy.namespace == "certification" and not getattr(policy, "preserve_discovered_claim", False):
                rows = [dict(row, claim=question(tool_context)) for row in rows]
            return {"candidates": policy.register(tool_context, rows), "next_action": "Verify candidate IDs only."}
        except (ValueError, KeyError, TypeError):
            return {"candidates": [], "error": "No valid bounded discovery records"}


class SharedVerification(BaseTool):
    def __init__(self, policy, verifier):
        super().__init__(name=policy.verify_name, description="Verify a registered candidate ID; Python preserves its exact claim and URL.")
        self.policy, self.verifier = policy, verifier

    def _get_declaration(self):
        return types.FunctionDeclaration(name=self.name, description=self.description,
            parameters_json_schema={"type": "object", "properties": {"candidate_id": {
                "type": "string", "enum": [f"C{i}" for i in range(1, self.policy.candidate_limit + 1)]}},
                "required": ["candidate_id"], "additionalProperties": False})

    async def run_async(self, *, args, tool_context):
        self.policy.begin(tool_context)
        try:
            candidate, payload = self.policy.reserve(tool_context,
                args.get("candidate_id", "") if set(args) == {"candidate_id"} else "")
        except (ValueError, TypeError):
            return {"error": "Unknown/repeated ID, invalid schema, or exhausted verification budget"}
        request = self.policy.verification_request(tool_context, payload) if hasattr(self.policy, "verification_request") else payload
        output = await self.verifier.run_async(args={"request": request}, tool_context=tool_context)
        record = self.policy.store(tool_context, candidate, output)
        return {"candidate_id": candidate.candidate_id, "status": record["status"], "next_action": "Python renders final evidence."}


networking_evidence = EvidencePolicy("networking", "Networking", 3, 2)
certification_evidence = EvidencePolicy("certification", "Certification", 1, 1)
research_evidence = EvidencePolicy("research", "Research", 3, 2)

# Wave 4 adds domain-specific policy; existing Networking/Research methods above
# remain the Wave 3 implementation. Career's registry is still not edited.
CERTIFICATION_DISCOVERY = """
WAVE 4 CERTIFICATION DISCOVERY OVERRIDE:
Locate official source URLs for ONLY the requested facts. Return up to TWO
candidate records for a version/code plus list-price question: the official exam
page and official vendor store/pricing page may be separate. A candidate only
needs to be a relevant official lead, not already prove every fact. Use the
exact discovery field labels below. Do not verify during discovery. Do not reject
an official exam purchase/list-price page merely because its product is called
an exam voucher; exclude discounts, bundles, retakes and training offers from
research and output unless asked. Keep the vendor-domain constraint in queries.
Do not return NO CANDIDATES when a relevant official partial source was located.
"""
INTERVIEW_DISCOVERY = """
WAVE 4 INTERVIEW DISCOVERY:
One targeted discovery of the named employer's official candidate/careers guides
and relevant role documentation. At most THREE candidates, strongest official
sources first. Do not reconstruct a universal process from scattered reports.
Optional: at most ONE anecdotal candidate only if official evidence is insufficient;
label SOURCE TYPE: anecdotal. Do not broadly search interview-report websites.
Use the discovery records below. Historical leads are POSSIBLY HISTORICAL.
"""
TRUST_DISCOVERY = """
WAVE 4 TRUST DISCOVERY:
Adjudicate the exact disputed claim. Locate at most TWO strongest relevant sources
in one targeted discovery, not background research. Preserve each source's date,
population, scope and version/cycle. Authority alone cannot resolve disagreement.
Use the discovery records below. Never guess which unnamed program is disputed.
"""
WAVE4_VERIFICATION = """
WAVE 4 DOMAIN VERIFICATION OVERRIDE:
Inspect the exact supplied URL and claim only. Return the Wave 3 JSON fields.
For Certification, additional optional objects fact_statuses and fact_evidence
map requested keys to their individual status and exact page quotation. One page
may support only one requested fact. Facts must contain only observed requested
values; price is the standard exam-only list price, with explicit currency/region
when present, excluding bundles, offers and discounts. An undated live official
exam/store page can establish the presently displayed version/list price if the
exact inspected content explicitly supports it; don't invent a publication date.
A missing requested fact remains CURRENT STATUS UNVERIFIED, never filled from memory.
For Interview, statuses are VERIFIED OFFICIAL, ANECDOTAL / REPORTED,
CURRENT STATUS UNVERIFIED, HISTORICAL or UNSUPPORTED. VERIFIED OFFICIAL requires
explicit employer-owned evidence for the exact scope; an undated official guide
is not proof of universal/current team-specific stages. Anecdotes never become
official. Date/population/role variability must remain explicit.
For Trust, use the four Wave 3 statuses and optionally include assertion,
population, version_cycle and conflict_type as strings. Quote exactly what the
source supports; do not resolve disagreements or infer supersession yourself.
Missing metadata is UNKNOWN. Read source A/B individually, without broad Search.
"""
WAVE4_PARENT = """
WAVE 4 NARROW EVIDENCE OVERRIDE:
Python bounds discovery, registers exact source/claim records, selects candidate
IDs and renders final evidence. Earlier broad research instructions cannot widen
this pipeline. No status upgrades, reconstructed URLs or unsupported factual
prefaces. Stable coaching remains tool-free. Trust adjudicates source pairs and
escalates explicit human requests immediately; no date/background research loop.
"""


@dataclass(frozen=True)
class CompletionPolicy(EvidencePolicy):
    """Domain thresholds share the registry and exact ID-only handoff."""
    preserve_discovered_claim = True

    def current(self, text):
        if self.namespace == "trust":
            return True
        if self.namespace == "interview":
            return bool(re.search(r"current|process|rounds|assessment|microsoft|google|amazon", text, re.I))
        return super().current(text)

    def register(self, context, candidates):
        if self.namespace == 'interview':
            kept=[]; anecdotal=0
            for row in candidates:
                if row['source_type'].lower() in {'anecdotal','other'}:
                    anecdotal+=1
                    if anecdotal>1:continue
                kept.append(row)
            candidates=kept
        return super().register(context,candidates)

    def discovery_request(self, context):
        protocol = {"certification": CERTIFICATION_DISCOVERY,
                    "interview": INTERVIEW_DISCOVERY, "trust": TRUST_DISCOVERY}[self.namespace]
        return question(context) + f"\nCandidate limit: {self.candidate_limit}." + DISCOVERY_PROTOCOL + protocol

    def verification_request(self, context, payload):
        return payload + "\n\nORIGINAL QUESTION:\n" + question(context) + VERIFICATION_PROTOCOL + WAVE4_VERIFICATION

    def official(self, host, text):
        if self.namespace == "trust":
            return host.lower().endswith((".edu", ".gov")) or super().official(host, text)
        return super().official(host, text)

    def begin(self, callback_context):
        super().begin(callback_context)
        if self.namespace != "trust":
            return
        state = self.state(callback_context)
        control = deepcopy(state[legacy.CONTROL])
        if control.get("trust_initialized"):
            return
        control["trust_initialized"] = True
        urls = list(dict.fromkeys(re.findall(r'https?://[^\s<>]+', question(callback_context))))[:2]
        control["supplied_sources"] = bool(urls)
        state[legacy.CONTROL] = control
        if urls:
            rows = [dict(claim=question(callback_context), source_url=url, source_type="user supplied",
                source_title="Source " + chr(65+i), apparent_date_or_cycle="UNKNOWN",
                discovery_support="Supplied by user, not verified", discovery_limits="Requires source inspection",
                discovery_status="INSUFFICIENT EVIDENCE") for i,url in enumerate(urls)]
            try:
                self.register(callback_context, rows)
            except ValueError:
                state[legacy.CANDIDATES] = {}

    def store(self, context, candidate, output):
        state = self.state(context)
        statuses = (legacy.VERIFICATION_STATUSES | {"VERIFIED OFFICIAL", "ANECDOTAL / REPORTED"}
                    if self.namespace == "interview" else legacy.VERIFICATION_STATUSES)
        try:
            data = json.loads(output)
            required = {"status", "source_title", "source_date_or_cycle", "page_evidence",
                "supported_scope", "not_established", "why", "page_read", "current_claim_explicit",
                "authority_host", "facts"}
            optional = {"fact_statuses", "fact_evidence", "assertion", "population", "version_cycle", "conflict_type"}
            if not isinstance(data, dict) or not required <= set(data) or set(data)-required-optional:
                raise ValueError("Invalid verification schema")
            if data["status"] not in statuses or type(data["page_read"]) is not bool or type(data["current_claim_explicit"]) is not bool:
                raise ValueError("Invalid verification status/flags")
            if any(not isinstance(data[k], str) for k in required-{"facts","page_read","current_claim_explicit"}):
                raise ValueError("Invalid string fields")
            if not isinstance(data['facts'],dict): raise ValueError("Invalid fact map")
            host=(urlsplit(candidate.source_url).hostname or '').lower()
            publisher=data['authority_host'].lower().rstrip('.')
            owned=(host==publisher or host=='vertexaisearch.cloud.google.com') and self.official(publisher,question(context))
            readable=data['page_read'] and data['page_evidence'].strip().upper() not in {'','UNKNOWN'}
            status=data['status']
            if self.namespace=='interview':
                if status=='VERIFIED CURRENT': status='VERIFIED OFFICIAL'
                if candidate.source_type.lower() in {'anecdotal','other'} or not owned:
                    if status=='VERIFIED OFFICIAL': status='CURRENT STATUS UNVERIFIED'
                if status=='VERIFIED OFFICIAL' and not readable: status='UNSUPPORTED'
                if status=='ANECDOTAL / REPORTED' and not readable: status='UNSUPPORTED'
                if candidate.discovery_status=='POSSIBLY HISTORICAL' and status in {'VERIFIED OFFICIAL','VERIFIED CURRENT'}: status='HISTORICAL'
            elif status=='VERIFIED CURRENT' and not (owned and readable and data['current_claim_explicit']):
                status='CURRENT STATUS UNVERIFIED'
            record=dict(candidate_id=candidate.candidate_id,claim=candidate.claim,source_url=candidate.source_url,
                source_title=data['source_title'],source_date_or_cycle=data['source_date_or_cycle'],status=status,
                reported_status=data['status'],page_evidence=data['page_evidence'] if readable else 'UNKNOWN',
                supported_scope=data['supported_scope'],not_established=data['not_established'],why=data['why'],
                authority_host=publisher,source_type=candidate.source_type, facts={})
            if self.namespace=='certification':
                per_status=data.get('fact_statuses',{}); quotations=data.get('fact_evidence',{})
                if not isinstance(per_status,dict) or not isinstance(quotations,dict):raise ValueError('Invalid fact evidence')
                record['fact_statuses']={}
                for key,value in data['facts'].items():
                    if key not in self.requested_facts(question(context)) or not isinstance(value,str) or not self.safe_fact(key,value):continue
                    s=per_status.get(key,status)
                    if s not in legacy.VERIFICATION_STATUSES:s='UNSUPPORTED'
                    quote=quotations.get(key,data['page_evidence'])
                    # Every displayed value must literally occur in inspected evidence.
                    explicit=isinstance(quote,str) and value.casefold() in quote.casefold()
                    if s=='VERIFIED CURRENT' and not (owned and readable and (data['current_claim_explicit'] or key in per_status) and explicit):s='CURRENT STATUS UNVERIFIED'
                    if status in {'UNSUPPORTED','HISTORICAL'} and s=='VERIFIED CURRENT':s=status
                    record['facts'][key]=value;record['fact_statuses'][key]=s
            for key in ('assertion','population','version_cycle','conflict_type'):
                if key in data:
                    if not isinstance(data[key],str):raise ValueError('Invalid comparison metadata')
                    record[key]=data[key]
        except (ValueError,TypeError,KeyError):
            record=dict(candidate_id=candidate.candidate_id,claim=candidate.claim,source_url=candidate.source_url,
                status='UNSUPPORTED',source_date_or_cycle='UNKNOWN',supported_scope='UNKNOWN',
                not_established='Invalid or unavailable verification evidence',why='Verification failed.',facts={})
        records=deepcopy(state.get(legacy.VERIFICATIONS,{}));records[candidate.candidate_id]=record
        state[legacy.VERIFICATIONS]=records
        return record

    def render(self, context):
        records=list(self.state(context).get(legacy.VERIFICATIONS,{}).values())
        if self.namespace=='certification':
            lines=['### Requested certification facts']
            groups=[('Exam version/code',{'exam_version','exam_code'}),('Price',{'price'}),
                    ('Retirement date',{'retirement_date'}),('Eligibility',{'eligibility'})]
            requested=self.requested_facts(question(context))
            for label,keys in groups:
                if not keys & requested:continue
                lines.append('### '+label)
                found=False
                for record in records:
                    for key in sorted(keys & record.get('facts',{}).keys()):
                        status=record.get('fact_statuses',{}).get(key,record['status'])
                        lines.append('**'+status+'**')
                        if status in {'VERIFIED CURRENT','HISTORICAL'}:
                            value=record['facts'][key]
                            if key=='price':
                                value+=' '+ ' '.join(record['facts'][k] for k in ('currency','region') if k in record['facts'] and record.get('fact_statuses',{}).get(k)==status)
                            lines.append(literal(value))
                        else:lines.append('The requested current fact was not established.')
                        lines.append(f"Source: [Inspected official candidate](<{record['source_url']}>)")
                        found=True
                if not found:lines.append('**CURRENT STATUS UNVERIFIED** — no inspected official page established this requested fact.')
            lines.append('Values apply only to the inspected page and stated scope; undated pages do not establish future prices or retirement cycles.')
            return '\n\n'.join(lines)
        if self.namespace=='interview':
            lines=['### What the employer officially documents']
            official=[r for r in records if r['status']=='VERIFIED OFFICIAL']
            if not official:lines.append('CURRENT STATUS UNVERIFIED — no official process claim was verified.')
            for r in official:lines.extend(self.render_record(r))
            lines.append('### What candidates have reported')
            anecdotes=[r for r in records if r['status']=='ANECDOTAL / REPORTED'][:1]
            if not anecdotes:lines.append('No anecdotal report is included.')
            for r in anecdotes:lines.extend(['Candidates have reported (not an official employer process):',*self.render_record(r)])
            lines.append('### What remains unknown or varies by team')
            for r in records:
                if r['status'] not in {'VERIFIED OFFICIAL','ANECDOTAL / REPORTED'}:lines.extend(self.render_record(r,False))
            lines.append('Role, team, location and recruiting cycle may differ. Exact stages, round counts and assessments are unverified unless explicitly supported above; ask the recruiter to confirm the process for the specific role.')
            return '\n\n'.join(lines)
        return self.render_trust(context,records)

    @staticmethod
    def render_record(record, supported=True):
        return [f"**{record['candidate_id']} — {record['status']}**",
            'Scope: '+literal(record.get('supported_scope','UNKNOWN')) if supported else 'The proposed process claim was not verified.',
            'Date/cycle: '+literal(record['source_date_or_cycle']),
            'Limits: '+literal(record['not_established']),
            f"Source: [Exact inspected source](<{record['source_url']}>)"]

    def human(self, text):
        return bool(re.search(r'need a human|human (?:review|to review)|speak to|talk to',text,re.I))

    def underspecified(self, text):
        return bool(re.search(r'this (?:morgan cybersecurity )?(?:program|opportunity)|the sources disagree',text,re.I)) and not re.search(r'https?://',text)

    def render_trust(self, context, records):
        text=question(context)
        lines=['### DISPUTED CLAIM',literal(text)]
        for i in range(2):
            lines.append('### SOURCE '+chr(65+i))
            if i>=len(records):lines.append('Not supplied or verified.');continue
            r=records[i]
            lines.extend(['Authority: '+literal(r.get('authority_host','UNKNOWN'))+'; '+literal(r.get('source_type','UNKNOWN')),
                'Date: '+literal(r['source_date_or_cycle']),
                'Scope/population/version: '+literal(r.get('supported_scope','UNKNOWN'))+' / '+literal(r.get('population','UNKNOWN'))+' / '+literal(r.get('version_cycle','UNKNOWN')),
                'What it supports: '+literal(r.get('assertion',r.get('page_evidence','UNKNOWN'))) if r['status'] not in {'UNSUPPORTED','CURRENT STATUS UNVERIFIED'} else 'What it supports: not established by verified source evidence.',
                'Evidence status: '+r['status'],f"Source: [Exact inspected source](<{r['source_url']}>)"])
        assessment='UNRESOLVED';why='The exact sources, disputed wording and matching date/population/scope have not established a responsible resolution.'
        conflict='Exact disagreement cannot be established without both source statements.'
        if len(records)==2:
            a,b=records
            conflict='Source A: '+literal(a.get('assertion','UNKNOWN'))+'; Source B: '+literal(b.get('assertion','UNKNOWN'))
            complete=all(r.get('assertion') not in {None,'','UNKNOWN'} and r['status']=='VERIFIED CURRENT' for r in records)
            fields=('source_date_or_cycle','supported_scope','population','version_cycle')
            known=all(r.get(k) not in {None,'','UNKNOWN'} for r in records for k in fields)
            if complete and known and all(a.get(k)==b.get(k) for k in fields) and a['assertion']==b['assertion']:
                assessment='RESOLVED';why='Both inspected sources support the same exact statement for the same documented date, scope, population and version; no disagreement is demonstrated at that scope.'
                if re.search(r'(?:I|i) (?:qualify|am eligible)|my eligibility',text):
                    assessment='PARTIALLY RESOLVED';why='Both sources agree on the documented rule, but whether it applies to this student requires confirmation of the individual eligibility criteria.'
            elif complete and known and any(a.get(k)!=b.get(k) for k in fields):
                assessment='PARTIALLY RESOLVED';why='The sources differ in documented date, population, scope or version. That explains a possible mismatch but does not establish which rule governs this student.'
        kinds=[]
        if len(records)==2:
            for field,kind in [('source_date_or_cycle','source-date mismatch'),('population','population/eligibility mismatch'),('supported_scope','scope mismatch'),('version_cycle','version/cycle mismatch')]:
                if all(r.get(field) not in {None,'','UNKNOWN'} for r in records) and records[0][field]!=records[1][field]:kinds.append(kind)
        conflict+='; Conflict type: '+(', '.join(kinds) if kinds else 'unresolved statement disagreement or insufficient source metadata')
        lines.extend(['### CONFLICT',conflict,'### ASSESSMENT',assessment,'### WHY',why,'### NEXT STEP'])
        if self.human(text):lines.append('Human review is appropriate. Share the exact disputed wording and source links with the relevant official university/program authority. I have not contacted anyone or created a referral.')
        elif not records:lines.append('Please supply the program/opportunity name, exact disputed claim, and both source links or quoted statements. For consequential eligibility/funding decisions, obtain confirmation from the responsible official before acting.')
        elif assessment!='RESOLVED':lines.append('Ask the responsible official to confirm the applicable population, cycle and policy in writing before making a consequential decision. Higher source rank alone does not settle the conflict.')
        else:lines.append('No further research is needed for this documented comparison.')
        return '\n\n'.join(lines)

    def step(self, callback_context, llm_request):
        self.begin(callback_context)
        text=question(callback_context);state=self.state(callback_context);control=state[legacy.CONTROL]
        if self.namespace=='trust' and (self.human(text) or self.underspecified(text)):
            return response(self.render(callback_context))
        if not self.current(text) and not control['search_attempts']:
            return super().step(callback_context,llm_request)
        candidates=state.get(legacy.CANDIDATES,{})
        if not control['search_attempts'] and not control.get('supplied_sources'):
            name=next(n for n in llm_request.tools_dict if n.endswith('google_search_agent'))
            return LlmResponse(content=types.Content(role='model',parts=[types.Part(function_call=types.FunctionCall(name=name,args={'request':text}))]))
        remaining=[c for c in candidates.values() if c['candidate_id'] not in control.get('selected',[])]
        remaining.sort(key=lambda c:c['source_type'].lower() in {'other','anecdotal'})
        if not remaining or control['verification_attempts']>=self.verification_limit:
            return response(self.render(callback_context))
        return LlmResponse(content=types.Content(role='model',parts=[types.Part(function_call=types.FunctionCall(name=self.verify_name,args={'candidate_id':remaining[0]['candidate_id']}))]))


certification_evidence = CompletionPolicy('certification','Certification',2,2)
interview_evidence = CompletionPolicy('interview','Interview',3,2)
trust_evidence = CompletionPolicy('trust','Trust',2,2)
