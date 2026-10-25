# Career workflow diagnostics

`career_baseline.py` runs the canonical local workflow against Vertex model APIs.
It does not import the Flask backend, call an Agent Engine, or deploy resources.
Use an environment with the workflow's SDK/ADK requirements installed and
authenticated development access to project `cosc-490`.

```powershell
# Inspect the 28-sample plan without importing ADK or making model calls.
python -B tests/diagnostics/career_baseline.py

# Explicitly permit live model requests. Samples run sequentially.
python -B tests/diagnostics/career_baseline.py --live

# Continue unattempted samples after a deliberate cooldown or interruption.
python -B tests/diagnostics/career_baseline.py --live --resume

# An additional independent sample requires an explicitly separate output.
python -B tests/diagnostics/career_baseline.py --live --case certification_current_1 --output additional_sample.json
```

There are two stable samples and one current sample for each of eight domain
specialists, plus two human-escalation and two reliability/conflict Trust cases.
Every sample uses a fresh in-memory session and the unchanged root router.
Clarification or routing to another specialist is recorded, never overridden.
`--research-probes` adds two explicitly worded research-readiness prompts when
the original graduate-school/industry comparison has overlapping routing.
The original samples are retained; these probes do not force a route.
`--roadmap-probe` adds an explicit current skill-roadmap question after observing
market-role routing overlap. `--interview-probe` adds one current Google process
question because the original employer-unspecified test cannot verify an exact
company process. All three flags produce 32 planned samples. These are separately
labelled supplemental cases; workflow instructions and routing are unchanged.

The default artifact is `tests/diagnostics/career_baseline.json`. It retains only
allowlisted events, public helper/final text needed for quality evaluation,
grounding queries/source metadata, and timing/count/error summaries. Session
IDs, credentials, thought parts, signatures, complete SDK objects and hidden
reasoning are not serialized. Do not use personal/student data as prompts.

Nested helper runners receive a diagnostic observer; existing agent callbacks,
model/tool assignments and model requests remain unchanged. The observer always
returns `None`. SDK response timing is measured before downstream tool work;
early samples use corresponding ADK response-event arrival as a labelled upper
bound. `normalize_model_timings` removes downstream tool waits from those early
model spans. Retrieval time is the union of helper intervals, not a sum that
double-counts overlapping work.

Search-helper invocations, Search-enabled model requests, requests returning
grounding metadata and reported Search queries are distinct measurements.
Reported query counts do not reveal Google's complete internal search workload.
Tool necessity labels distinguish initial request-based classification from
`reviewed_necessity` and `review_note`, which retain the manual contextual review.
The report includes the same per-call judgments; they are not independent proof
that retrieved claims are true.

The 240-second cutoff is diagnostic censoring, not an application timeout.
Error samples are not silently retried. A 429 stops the batch; wait before an
explicit resume, and stop again if capacity errors recur. Existing SDK behavior
is preserved; this harness adds no model/API retry policy.

Offline harness checks require pytest but no ADK/cloud access:

```powershell
python -B -m pytest tests/diagnostics/test_career_baseline.py -q -p no:cacheprovider
```

See `agents/career/workflow/OPTIMIZATION_REPORT.md` for measurements, quality
limitations, triage bands and proposed optimization waves. These are profiling
results, not SLAs or production-promotion evidence.

## Wave 2 current-fact canaries

`career_wave2.py` reuses the existing observer and runner with an explicit case
plan. The baseline harness accepts an optional diagnostic case plan; its default
plan and CLI behavior are unchanged. Print the plan without cloud calls:

```powershell
python -B tests/diagnostics/career_wave2.py
```

Run exactly one current case at a time, in Certification, Networking, Research,
Microsoft Interview order. Inspect the recorded answer and helper scope before
starting the next case. Use `--resume` to preserve attempts in the same artifact,
and a new `--output` after any workflow source change. No failed case is retried
automatically. Stop a capacity-affected path; do not repeatedly retry it.

```powershell
python -B tests/diagnostics/career_wave2.py --live --case wave2_certification_current
python -B tests/diagnostics/career_wave2.py --live --resume --case wave2_networking_current
```

A 180-second diagnostic ceiling censors an incomplete sample; it is not an
application timeout or SLA. Stable regression cases cover the same four
specialists. Research uses the explicit readiness probe to avoid the known
degree-choice routing overlap. One stable sample per modified specialist checks
for retrieval regression. No production/Agent Engine endpoints are called.

`test_career_wave2_parity.py` checks instruction hashes, exact Wave 1 preservation
and unchanged non-instruction AST configuration against the checkpoint. These
checks are offline and make no model calls.

Wave 2 runtime note: prompt-only Certification testing exceeded its discovery
budget. The four primary specialists therefore also have a temporary
per-invocation/per-specialist backstop denying a third actual Search-helper
execution. This does not bound provider-internal queries or model waiting.
`test_career_search_budget.py` checks the cap and isolation without ADK/network.
The parity tests explicitly exclude only these four new callbacks when comparing
unrelated configuration to the checkpoint.

## Wave 3 evidence and wait diagnostics

`career_wave3.py` runs one fresh local case at a time using the pinned ADK
environment. Three Certification stable samples precede current testing. A 429
stops Certification sampling; failed IDs are never retried. Current Interview is
deferred if this wave has encountered capacity failures. No Agent Engine is used.

```powershell
python -B tests/diagnostics/career_wave3.py
python -B tests/diagnostics/career_wave3.py --live --case wave3_certification_stable_1
```

`career_wait_analysis.py` attributes disjoint observed intervals to root,
specialist pre/post-tool, helper and stream phases. Gaps remain
UNOBSERVED_RUNTIME_WAIT. These are SDK/provider/network waiting observations,
not model-compute measurements. Unfinished helper intervals are censored at the
diagnostic cutoff. Capacity failures retain both PROVIDER_CAPACITY cause and
ROOT/SPECIALIST/TOOL_CAPACITY stage. No retry policy is added.

The observer records numeric instruction/history/tool-description counts only,
without raw prompt/history or hidden reasoning. Static authored instruction sizes
and effective SDK instruction sizes differ because ADK adds routing/context.
No tokenizer/API/download is used; token counts remain unavailable.

`test_career_shared_evidence.py` uses the pinned ADK environment for namespace,
transport, strict budget, final-render and actual offline Runner tests. It reuses
the unchanged Career registry through a key adapter. `test_career_wave3.py` is
stdlib/pytest only. Wave 2 parity tests strip exactly the declared Wave 3 wrapper,
callback and protocol additions before comparing prior immutable checkpoints.
The original baseline/Wave 1/Wave 2 result JSON files are not rewritten.

## Wave 4 current-fact completion

`career_wave4.py` prints the 12-case plan without API calls. Live execution requires
`--live --case EXACT_ID`; `--resume` retains every prior attempt and skips attempted
IDs, including failures. The driver refuses further live cases after any recorded
429. This wave stopped after its fourth attempt with TOOL_CAPACITY; eight remaining
cases are explicitly deferred. Do not bypass the capacity stop with another output
file. No automatic retries or Agent Engine requests are added.

The Certification contract allows two authoritative partial sources and two
verifications, with separate requested-fact statuses. Interview and Trust reuse
the registry under separate namespaces. Current pipeline progression for these
three targets is Python-directed: no specialist SDK synthesis request is needed
between bounded helpers or for the final renderer. Stable guidance still follows
its preserved model path. Timing tables distinguish these intentional zero SDK
intervals from reduced model latency.

`test_career_completion.py` covers budgets, exact handoff, per-fact evidence,
official/anecdotal separation, historical-status preservation, source-pair Trust
adjudication and explicit escalation. `test_career_completion_runner.py` executes
the real ADK Runner with fake model responses; those tests make no cloud calls
and their synthetic data/timing are not live canary results.

`career_wave4_compression.json` measures exact duplicated paragraphs for Wave 5
planning only. Shared constants alone reduce source duplication, not rendered
prompt size. No prompt compression was implemented in Wave 4.

Live JSON retains its measured source hashes. Post-live changes covered Trust adjudication safeguards, an Interview-only
anecdotal-candidate cap, and domain-specific enum validation; method hashes are
recorded separately in the parity manifest. Valid four-status Certification live
responses and their measured output are unaffected. Prior result JSON files are immutable.

## Wave 5 controlled prompt compression

`career_wave5_parity.json` captures every pre-edit instruction, old/new hashes and
rendered size, exact changed blocks and displaced-line mappings.
`career_wave5_semantics.md` is the human-readable checklist. Seven original
specialist literals are compressed; every Wave 1–4 append and handoff table is
retained. Helpers, root, Trust, Career, models, tools, callbacks and registry
mechanics are unchanged. The editor `career_wave5_compression.py` only applies
to the exact captured entry source; it refuses to overwrite later edits. Runtime
agents receive their complete policy text locally, not an inherited constant.

Historical parity tests call `restore_before_compression` only after checking the
measured new instruction hash. New Wave 5 tests compare the complete restored AST
to the actual entry source and check replacement replay and full line coverage.
The mocked ADK matrix tests stable/current plumbing, routing expectations and
evidence boundaries for every target; fake model choices are not proof of
arbitrary real-model obedience. Existing Career/Trust tests remain in the suite.

`career_wave5.py` prints its opt-in live plan by default. Live execution requires
one exact `--case`, in order: health probe; Certification/Interview/Networking/
Research stable; at most Certification and Networking current. No model/API
retry is added. Any runtime/capacity error stops subsequent live cases. Wave 5
stopped on its third attempt with SPECIALIST_CAPACITY; do not retry or bypass
that stop using another output file.

Latency comparisons use retained pre-compression observations, not simultaneous
randomized A/B trials. Few completed samples, SDK warming and provider variance
preclude a causal latency claim. Full benchmarking remains Wave 6.
