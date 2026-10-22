# Career workflow

**STATUS: SOURCE-CONTROLLED DEVELOPMENT RELEASE CANDIDATE**

This package is the canonical Career & Professional workflow for current development. It was migrated from Google Agent Studio and is deployed as the separate **Source Dev v4** Agent Engine. Workflow and Flask/browser integration have been validated; promotion to the production engine or the Flask default has not occurred.

The original `agent-studio-export/agent.py` is intentionally retained as an immutable migration baseline and provenance/reference. It is not the current development implementation. The initial parity copy has since received intentional Career Exploration evidence instructions/tool wiring and root domain-first routing changes. Do not claim complete behavioral or instruction parity with the original export.

## Deployment status and production boundary

| Setting | Current value |
| --- | --- |
| Development engine | `7801100969768386560` (Source Dev v4) |
| Resource | `projects/717132085388/locations/us-west1/reasoningEngines/7801100969768386560` |
| Display name | `Career & Professional Orchestration Agent - Source Dev v4` |
| Project | `cosc-490` (project number `717132085388`) |
| Deployment region | `us-west1` |
| Production engine / Flask default | `3463694723959488512` |

Production remains separate and untouched by the development migration. **Do not overwrite, update, delete, or redeploy production during development testing.** Flask continues to select production unless `CAREER_REASONING_ENGINE_ID` is explicitly set before startup. Selecting a development engine changes the application's request destination; it does not update an Agent Engine.

## Package inventory

| File | Purpose |
| --- | --- |
| `__init__.py` | Defines the workflow package and imports its agent module. |
| `agent.py` | Defines the 30-agent graph, root orchestrator, specialists, Search/URL Context helpers, domain-first routing, and Career Exploration evidence instructions/tool wiring. |
| `evidence.py` | Implements deterministic candidate IDs, invocation-local state, retrieval budgets, exact claim/URL transport, verification-result storage, and final evidence rendering. |
| `main.py` | Constructs `vertexai.agent_engines.AdkApp(agent=root_agent)` as `agents.career.workflow.main.app`. |
| `deploy_dev.py` | Explicit, create-only development deployment helper requiring a staging bucket; importing it has no deployment side effect. |
| `requirements.txt` | Pins the deployment SDK and ADK versions. |
| `README.md` | Documents the current architecture, configuration, provenance, and validated development state. |

The Studio export itself did not include an ADK application/runtime wrapper. The current `main.py` supplies that wrapper around the existing `root_agent`; Flask calls the selected managed runtime through `agents/career/service.py`.

## Dependencies and serialization compatibility

The deployment requirements are exactly:

```text
google-cloud-aiplatform[agent_engines,adk]==1.165.1
google-adk==2.12.0
```

Install them in a dedicated development environment from the repository root:

```powershell
python -m pip install -r agents/career/workflow/requirements.txt
```

The validated environment also resolved compatible transitive dependencies including `google-genai`, `google-auth`, `cloudpickle`, and `pydantic`. They are intentionally not separately pinned in this requirements file unless needed. The SDK added resolved `cloudpickle` and `pydantic` pins to the staged deployment requirements for serialization compatibility; the source requirements file retains the two direct pins above.

The first source development deployment was serialized under `google-adk==1.14.1`, whose `LlmAgent` schema did not contain `.mode`. The remote runtime failed with `'LlmAgent' object has no attribute 'mode'`. Rebuilding the application and freshly serializing it under ADK `2.12.0` and SDK `1.165.1` resolved that incompatibility. Reconstruct the app under the aligned stack before deployment; do not reuse an older serialized app/pickle.

## Agent architecture

The graph contains **30 agents: one root, nine specialists, and twenty helper agents**.

Root: `root_agent`, named `Career___Professional_Orchestration_Agent`.

| Specialist | Agent name |
| --- | --- |
| Career Exploration | `career_exploration_agent` |
| Internship & Job Preparation | `internship__job_preparation_agent` |
| Resume & Portfolio | `resume__portfolio_agent` |
| Interview Preparation | `interview_preparation_agent` |
| Networking & Professional Communication | `networking__professional_communication_agent` |
| Skill Gap & Career Roadmap | `skill_gap__career_roadmap_agent` |
| Research & Graduate Pathways | `research__graduate_pathways_agent` |
| Certification & Technical Development | `certification__technical_development_agent` |
| Trust & Human Escalation | `trust__human_escalation_agent` |

Each specialist and the root retain a Search helper and a URL Context helper as defined by the exported graph. The built-in tools remain on separate helpers. Most parent agents expose these through `AgentTool`; Career Exploration uses the evidence wrappers described below. Its `before_agent_callback` is `begin_evidence_invocation`, and its `before_model_callback` is `bounded_evidence_step`.

All 30 agents use `GlobalGemini(model='gemini-3.5-flash')`. `GlobalGemini` constructs its Vertex model client with location `global`; this model location is separate from the Agent Engine deployment region `us-west1`.

## Domain-first routing

The root first determines which domain owns the request. Currentness, factual verification, citations, Search, or changed information alone do not transfer ownership to Trust. The owning specialist uses its permitted grounding/retrieval workflow.

| Request | Owning specialist |
| --- | --- |
| Current cybersecurity career resources | Career Exploration |
| Current Security+ version/price | Certification & Technical Development |
| Current internships, eligibility, or deadlines | Internship & Job Preparation |
| Current graduate research opportunities | Research & Graduate Pathways |
| Current networking resources | Networking & Professional Communication |

Trust remains active for requests primarily about conflicting evidence, reliability/trust evaluation, uncertainty the owning specialist cannot responsibly resolve, consequential decision ambiguity or human review, explicit human escalation, and system limitations. Requests asking the AI to make consequential decisions retain the existing Trust escalation rule. Trust is not a generic fact-checking proxy for another specialist.

## Career Exploration evidence path

Stable/general exploration guidance can proceed without retrieval when it is unnecessary. Current factual work uses a bounded evidence flow:

1. Search discovers at most three candidate records. Python assigns deterministic IDs `C1`, `C2`, and `C3`.
2. Usable official candidates close discovery after one Search-helper invocation. Only when no usable official candidate exists may discovery retry; there are at most two Search attempts.
3. The parent model selects candidate IDs through `verify_evidence_candidate`. The tool schema accepts only `candidate_id`, never a replacement claim or URL.
4. Python retrieves the frozen registered claim and URL, constructs the verifier request, and sends those exact strings to the URL Context helper.
5. At most two verification attempts are permitted, including invalid/failed selections. Unknown or duplicate selections are rejected.
6. Verification results retain the registered claim and URL. Python renders evidence, statuses, limits, and exact citations from stored verification records, followed by fixed general exploration guidance. Discovery-only candidates are omitted.

The registry uses ADK `temp:career_evidence_*` state for candidates, control/budgets, verifier handoff audit records, and verification results. This is invocation-local temporary state carried through the active session execution, not durable conversation memory; it resets on the next invocation, including a follow-up in the same chat session.

This design prevents model transcription from mutating URLs or claims, bounds retrieval loops, preserves conservative evidence status, and avoids promoting unverified candidates. Verification statuses are:

- `VERIFIED CURRENT`
- `CURRENT STATUS UNVERIFIED`
- `HISTORICAL`
- `UNSUPPORTED`

A current question is not guaranteed to produce `VERIFIED CURRENT`. Missing current-cycle evidence can leave current status unverified; copyright dates do not establish current availability. The registry also downgrades `VERIFIED CURRENT` when its source date/cycle is `UNKNOWN`.

## Validation checkpoint

These are recorded validation results for the current v4 source, not guarantees for every future query.

### Local

- Twelve focused evidence-registry tests passed (`tests/test_career_evidence.py`).
- Eleven engine-configuration tests passed (`tests/test_career_config.py`).
- Eight routing-only canaries passed: five domain-currentness requests and three Trust/reliability/human-escalation requests. Each stopped at the first transfer without running specialist retrieval.
- Source syntax, imports, app/root identity, graph/configuration integrity, and instruction-hash checks passed. The checkpoint review reconfirmed the graph and source against the validated v4 snapshot without repeating live model calls.
- Eight mocked Career endpoint contract checks and four chatbot page tests passed. The separate legacy Career starter test still expects HTTP 501 although the implemented endpoint returns 200; its deliberate correction remains a follow-up.

### Remote Source Dev v4

- The stable cloud-security/GRC smoke question routed to Career Exploration, returned a final answer, and used no Search or URL Context helpers.
- The Morgan current-cybersecurity-resources question routed to Career Exploration, used one Search helper, registered three candidates, and selected `C1`/`C2` through two candidate-ID verification calls.
- A final answer returned with `C1` marked `UNSUPPORTED` and `C2` marked `HISTORICAL`; the unverified `C3` was omitted. Current partnership/access/funding claims were not promoted beyond the evidence limits.
- No 429, URL-mutation 404, agent-runtime error, or transport interruption was observed in those two remote test calls.
- Remote events did not expose the private temporary registry/handoff records. Exact stored-versus-verifier claim/URL equality was enforced by the deployed Python path and audited in local tests, but was not independently observable in that remote trace. Do not describe this as a complete remote handoff audit.

### Flask and browser application integration

- Flask selected v4 through `CAREER_REASONING_ENGINE_ID`; production remained the unset-variable fallback, verified separately without production inference.
- Stable, same-session follow-up, Morgan evidence, and Certification requests returned HTTP 200. Routing selected Career Exploration or Certification as appropriate.
- Same-session follow-up retained context across a backend restart, and browser refresh retained the conversation session.
- New Chat cleared the visible conversation and caused fresh backend session creation. A post-reset request hit upstream `429 RESOURCE_EXHAUSTED`; its single retry also returned runtime errors/no text. Flask preserved its HTTP 502 behavior and the browser displayed Retry. This is an upstream capacity limitation, not a New Chat reset defect; that post-reset answer check remained blocked.
- Markdown rendering/sanitization, Copy, timestamps, and the thinking indicator worked. A separate controlled connection failure recovered successfully through Retry after restarting the test backend.

## Observed latency and known follow-ups

These representative timings are observations, **not SLAs or latency guarantees**:

| Validated request | Approximate total |
| --- | --- |
| Remote v4 stable smoke | 22 seconds |
| Remote v4 Morgan evidence | 54 seconds |
| Flask stable career question | 37 seconds |
| Flask same-session follow-up | 11 seconds |
| Flask Morgan evidence | 67 seconds |
| Flask Certification version/price | 165 seconds |

Certification latency remains a future optimization target; its specialist was not modified during integration validation. Upstream model capacity/429 behavior and the stale HTTP-501 test remain known follow-ups.

## Development engine history

| Engine | ID | Recorded role/status |
| --- | --- | --- |
| Production | `3463694723959488512` | Separate existing production engine and Flask fallback/default. |
| Failed Source Dev | `7611949785418825728` | ADK 1.x serialization/schema incompatibility. |
| Source Dev v2 | `2265614077776625664` | Runtime compatibility fixed under the aligned stack. |
| Source Dev v3 | `4679543478047211520` | Evidence registry deployed; older root routing sent the Morgan evidence request to Trust. |
| Source Dev v4 | `7801100969768386560` | Domain-first routing and deterministic Career Exploration evidence path; current validated development release candidate. |

These are separate resources. Older development engines have not been deleted or updated as part of this checkpoint.

## Development deployment

Prerequisites: authenticated access to `cosc-490`, the aligned deployment environment, repository-root working directory, and an explicit accessible staging bucket.

Validated bucket: `gs://cosc-490-agent-staging-20261021-a41c7e9b`.

The development deployment command is:

```powershell
$env:CAREER_AGENT_STAGING_BUCKET="gs://cosc-490-agent-staging-20261021-a41c7e9b"
python -m agents.career.workflow.deploy_dev
```

**Running this command creates a new billable Agent Engine resource.** It does not select or update the existing v4 engine or production. Do not run it merely to configure or test Flask.

`deploy_dev.py` uses project `cosc-490`, region `us-west1`, the v4 display name above, and a fresh `career-source-dev-v4-<uuid>` staging prefix. It requires a valid bucket URI and checks that the bucket exists before calling `client.agent_engines.create`. It has no bucket-creation or Agent Engine update/delete operation. Importing the module never invokes `main()` or constructs a deployment client.

Packaging includes `agents/__init__.py`, `agents/career/__init__.py`, and the workflow's `__init__.py`, `agent.py`, `evidence.py`, and `main.py`. The dedicated requirements file supplies deployment dependencies; backend/frontend files, credentials, bytecode caches, and deployment helpers are not included in `extra_packages`.

## Flask engine selection

`agents/career/service.py` reads `CAREER_REASONING_ENGINE_ID` at import/startup:

- Unset: selects production engine `3463694723959488512`.
- Set to a non-empty ASCII numeric engine ID: uses that engine for both session and query URLs.
- Empty, malformed, non-ASCII, or non-numeric values: fail validation before authentication/network calls.

For v4 testing in the current PowerShell process only:

```powershell
$env:CAREER_REASONING_ENGINE_ID="7801100969768386560"
```

Start/restart Flask from that process so it reads the new value. Removing the variable restores the default on the next fresh import/startup; it does not retarget an already-running process. Do not test fallback by sending an unnecessary production inference request. Cloud resource IDs and the bucket URI are operational identifiers, not secrets; credentials, tokens, prompts, replies, and session identifiers must not be logged as configuration diagnostics.

## Provenance and instruction integrity

Keep `agent-studio-export/agent.py` immutable as the original migration baseline. Use this workflow directory for current development.

The current instructions intentionally differ from the export for Career Exploration, its Search and URL Context helpers, and the root orchestrator. Career Exploration also adds evidence tools and callbacks. The remaining exported agents/helpers retain their instructions and structure. All 30 agents' current instructions/configuration matched the validated v4 source snapshot at checkpoint review.

Instruction parity checks compute SHA-256 over the exact decoded instruction string encoded as UTF-8, without trimming or normalization. Record detailed per-component hashes in regenerated validation/audit output rather than maintaining a brittle exhaustive table in this README. Matching hashes verify source integrity; they do not prove identical model-generated answers or complete runtime behavioral parity.
