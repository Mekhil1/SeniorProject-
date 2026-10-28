# Workflow Optimization Baseline

## Executive Summary

**Coverage status:** All planned cases attempted; capacity failures/censoring still limit completed-answer coverage.

Checkpoint: `beeb3a87ad2f8892dce9e30f376bd2768b65c239`. Measurements use the unchanged canonical local workflow with SDK `1.165.1`, ADK `2.12.0`, Vertex project `cosc-490`, and the existing global model configuration. No Agent Engine endpoint, production inference, deployment, backend or frontend path was used or changed.
Reached 9 specialist targets. Completed current-case responses (not automatic quality passes): 6/8 domain cases. Trust conflict/reliability completed: 2/2.


Recorded 35 live attempts: 28 completed public responses, 2 diagnostic deadline cutoff(s), and 5 capacity-affected attempt(s). Failed/censored samples are not successful performance observations. Planned primary cases: 32 (28 requested cases plus two clarified Research probes and one current Roadmap and employer-specific Interview probe). Additional Certification, Internship-stable and Roadmap-stable attempts are explicitly labelled; they do not replace failures or cutoffs. Certification received only one additional attempt, then no further retry. The stable follow-ups sought completed repeats after the first failures; Internship completed and Roadmap failed at the root.

Coverage and verdict must distinguish an attempted route from a completed current-fact answer. The scorecard records missing/censored evidence instead of manufacturing a full reliability result. Prior v4 remote/Flask measurements are context only and are not pooled with these local timings.

### Method and limits

- Fresh in-memory session for every sample; normal unchanged root routing. Two stable attempts per domain, two human-escalation samples, one initial current sample per domain, and conflict/reliability Trust cases. Research-readiness, explicit Roadmap and Google Interview probes are supplemental because the original degree-choice prompt had overlapping routes.
- Sequential execution, initially 3 seconds between cases, then 10 and 20 seconds; pauses of about two minutes and later at least five minutes after 429s. Batches stop on 429; failed cases are not automatically retried. Certification received one explicitly labelled additional attempt and no further retry.
- Process/source imports are excluded; time zero starts before the local runner/session setup. Observer overhead is included and not separately isolated. Agent Engine/container and Flask transport overhead are excluded. Root request start is the SDK call start; transfer is the emitted first transfer decision. Handoff is transfer-to-first-specialist-event elapsed time. Model spans are SDK response-arrival waits (including SDK/network/provider waiting, not pure compute); early spans use a labelled ADK response-event upper bound so nested tool waits are not double-counted.
- First text means first public, non-thought text on the outer ADK runner. It is not hidden reasoning or a provider first-token metric. Flask currently buffers its upstream result, so browser display latency is the completed POST time rather than this local event time.
- Retrieval time is the union of helper intervals. Search helper invocations (H), Search-enabled SDK model calls (E), model responses exposing grounding metadata (G), and reported Search queries (Q) are different counts. URL counts are helper invocations, not undisclosed internal page fetches. SDK internal HTTP retries, complete Google search workload, and URL retrieval-status metadata are not fully exposed.
- GREEN <=15 s; YELLOW >15–30 s; ORANGE >30–60 s; RED >60 s. These are triage bands, not SLAs. A 240 s diagnostic cutoff is right-censoring, not an application timeout or completed latency.
- Public final/helper text is retained only for quality review. Artifact fields are allowlisted; credentials, tokens, session IDs, thought signatures and hidden thought parts are excluded. A network-blocked synthetic nested-runner test verified observer coverage and thought/signature exclusion.
- Small, ordered samples are not percentile estimates. Clarification, routing overlap, source scope and provider capacity can change the work performed; do not optimize by simply deleting retrieval while preserving unsupported current claims.

## Specialist Scorecard

Latency lists individual attempts under the requested intent; actual first targets are retained, so root-only failures are not specialist execution times. `!` means a failure or cutoff, not a fast completed answer. Search and URL counts are observed calls including partial failed work; S is the primary stable/human set and C the current/conflict/reliability set. Research original prompts and clarified probes are distinguished in detailed results.

| Specialist | Stable latency (s) | Current latency (s) | Search calls | URL Context calls | Main bottleneck | Reliability concern | Optimization priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Career Exploration | 38.06/20.26 | 63.45 | S 0/0; C 1 | S 0/0; C 2 | Bounded reference; model/helper request waits | Freshness signal does not establish specific current benefits/funding. | P3 |
| Internship & Job Preparation | 67.39/17.88!/90.29 | 56.72 | S 2/2!/3; C 2 | S 0/0!/0; C 0 | Unrequested current examples on stable path; broad opportunity discovery | Openings and exact eligibility asserted before intake; no final citations or URL inspection. | P1 |
| Resume & Portfolio | 61.03/54.51 | 54.07 | S 2/1; C 2 | S 0/0; C 0 | Stable-to-current scope expansion and weak source traceability | Current employer expectations lack final citations and a defined posting sample. | P1 |
| Interview Preparation | 23.88/18.47 | 18.09!/240.02! | S 0/0; C 2!/4! | S 0/0; C 0!/0! | Named-company cutoff; model wait plus four helpers | No completed current answer; employer-process reliability remains unassessed. | P0 (provisional) |
| Networking & Professional Communication | 18.02/16.95 | 160.70 | S 0/0; C 6 | S 0/0; C 0 | Six helpers / 59 queries; institutional and partnership broadening | Active clubs and partnership/access benefits lack claim-level current verification. | P0 |
| Skill Gap & Career Roadmap | 78.19/240.01!/80.33! | 62.18 [other route]/53.23 | S 3/0!/0!; C 2/2 | S 0/0!/0!; C 0/0 | Both over-retrieval and a separate model-response stall | Original current answer off scope; clarified market claims lack a defined sample/citations. | P1 |
| Research & Graduate Pathways | 46.62 [other route]/49.07; readiness 29.40/18.73 | 226.91 | S 0/2; C 8 | S 0/0; C 0 | Eight helpers / 86 queries; active/funding assertions and routing overlap | Active programs, funding and eligibility asserted without final links or URL verification. | P0 |
| Certification & Technical Development | 16.22/20.26 | 0.80!/91.94! | S 0/0; C 0!/3! | S 0/0; C 0!/0! | Current path retrieval/capacity tail plus stable grounding leaks | Stable vendor discount/policy claims ungrounded; no completed current version/price answer. | P0 |
| Trust & Human Escalation | 19.37/9.06 | 100.16/9.82 | S 1/0; C 3/0 | S 0/0; C 0/0 | Speculative conflict resolution; three helpers / 39 queries | Invented conflict context and blanket active-status claims without source pair/citations. | P0 |

### Completed timing comparisons and retrieval totals

- Stable/human (including labelled readiness probes): fastest `trust_human_2` 9.06 s; slowest `internship_stable_2 [additional]` 90.29 s. Completion is not a factual-quality pass; the known off-scope Roadmap original is excluded from current winners.
- Current external-fact requests/probes: fastest `roadmap_current_probe_1` 53.23 s; slowest `research_current_1` 226.91 s. Completion is not a factual-quality pass; the known off-scope Roadmap original is excluded from current winners.

The following totals follow actual helper ownership across all attempts, including partial failures and supplemental probes; they are not counts of verified claims.

| Actual owner | Search helpers | Search-enabled requests | Grounded responses | Reported queries | URL helpers |
| --- | --- | --- | --- | --- | --- |
| Career Exploration | 3 | 3 | 3 | 11 | 2 |
| Internship & Job Preparation | 9 | 9 | 8 | 32 | 0 |
| Resume & Portfolio | 5 | 5 | 5 | 12 | 0 |
| Interview Preparation | 6 | 6 | 5 | 36 | 0 |
| Networking & Professional Communication | 6 | 6 | 6 | 59 | 0 |
| Skill Gap & Career Roadmap | 5 | 5 | 5 | 15 | 0 |
| Research & Graduate Pathways | 11 | 11 | 11 | 96 | 0 |
| Certification & Technical Development | 3 | 3 | 2 | 4 | 0 |
| Trust & Human Escalation | 4 | 4 | 4 | 41 | 0 |

Transfer calls are routing steps, labelled NECESSARY for dispatch and excluded from retrieval totals.

Manual per-call review categories: NECESSARY=18, OPTIONAL=18, REDUNDANT=2, UNNECESSARY=16. These are request-relative judgments, not proof that an API call was billed or a returned claim was correct.

**Priority summary:** P0: Research, Networking, Certification and Trust; Interview is provisional P0 because the named-company path exceeded the cutoff with both model wait and retrieval. P1: Internship, Resume and Skill Roadmap (with separate routing/capacity escalation). No specialist is assigned P2 in this limited sample set. P3: Career Exploration within its validated Morgan-resource scope. Provider capacity and routing/evidence-scope mismatches are cross-workflow P0 investigation items, not a reason to rewrite every specialist prompt.


## Detailed Results

### Career Exploration

The current control registered three candidates, verified C1/C2, rendered C1 VERIFIED CURRENT and C2 HISTORICAL, and omitted C3. The verifier used a September 2026 news update as a freshness signal for C1; this does not establish specific current benefits or funding. Deterministic transport/status preservation is not a truth oracle. A public date-lookup argument was intercepted by the discovery wrapper and replaced with the original student request, so this was a necessary domain search, not an actual calendar-only lookup.

Test prompt: I'm interested in cloud security and risk management. What career paths should I explore?

Test prompt: What current cybersecurity career resources are available to Morgan State Computer Science students?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| career_stable_1 | `career_exploration_agent` | completed | 10.67 | 10.68 | 0.01 | — | 38.06 | 38.06 / ORANGE |
| career_stable_2 | `career_exploration_agent` | completed | 1.94 | 1.94 | 0.00 | — | 20.25 | 20.26 / YELLOW |
| career_current_1 | `career_exploration_agent` | completed | 8.21 | 8.21 | 0.01 | 14.74 | 63.45 | 63.45 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| career_stable_1 | 1.20 | 9.47 | 27.37 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| career_stable_2 | 0.01 | 1.93 | 18.31 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| career_current_1 | 1.08 | 7.12 | 9.56 | 1 / 1 / 1 / 6 | 2 | 45.61 | 2 |

Retrieval call review: **career_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Career_Exploration_Agent_google_search_agent` | search | 23.27 | NECESSARY | current calendar year today | Original-question discovery or selected-ID verification; wrapper ignores calendar-only public request. |
| URL Context helper #1; tool #3 `verify_evidence_candidate` | verification | 10.46 | NECESSARY | C1 | Original-question discovery or selected-ID verification; wrapper ignores calendar-only public request. |
| URL Context helper #2; tool #4 `verify_evidence_candidate` | verification | 11.92 | NECESSARY | C2 | Original-question discovery or selected-ID verification; wrapper ignores calendar-only public request. |

Observed nested source titles/domains (not independent factual verification): morgan.edu.

### Internship & Job Preparation

Stable preparation expanded into current recruiting cycles and employer programs. The current request retrieved many employer listings before gathering the missing background, then asserted current openings and exact eligibility windows without URL Context or clickable citations. Search metadata included official employer domains as well as aggregators; that is discovery evidence, not per-posting active-status verification.

Test prompt: How should I prepare for cybersecurity internships as a computer science senior?

Test prompt: What cybersecurity internships are currently open to students with my background?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| internship_stable_1 | `internship__job_preparation_agent` | completed | 7.80 | 15.63 | 7.83 | 15.64 | 67.39 | 67.39 / RED |
| internship_stable_2 | `internship__job_preparation_agent` | failed | 2.56 | 4.15 | 1.60 | 4.17 | — | 17.88 / YELLOW |
| internship_current_1 | `internship__job_preparation_agent` | completed | 3.10 | 12.34 | 9.24 | 12.35 | 56.71 | 56.72 / ORANGE |
| internship_stable_2 [additional] | `internship__job_preparation_agent` | completed | 8.00 | 15.27 | 7.28 | 15.28 | 90.29 | 90.29 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| internship_stable_1 | 1.00 | 6.81 | 27.43 | 2 / 2 / 2 / 5 | 0 | 32.11 | 0 |
| internship_stable_2 | 0.01 | 2.55 | 7.13 | 2 / 2 / 1 / 2 | 0 | 8.16 | 0 |
| internship_current_1 | 0.02 | 3.08 | 24.54 | 2 / 2 / 2 / 10 | 0 | 29.04 | 0 |
| internship_stable_2 [additional] | 1.10 | 6.89 | 28.91 | 3 / 3 / 3 / 15 | 0 | 53.31 | 0 |

Retrieval call review: **internship_stable_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Internship___Job_Preparation_Agent_google_search_agent` | search | 7.29 | UNNECESSARY | current year calendar date | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Internship___Job_Preparation_Agent_google_search_agent` | search | 24.84 | UNNECESSARY | "cybersecurity" "new grad" OR "associate" jobs 2027 | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): almanac.com, calendar-365.com, indeed.com, newgrad-jobs.com, builtin.com, myworkdayjobs.com, ziprecruiter.com, grinnell.edu, ibm.com, jobright.ai, prosple.com, vodafone.com.

Retrieval call review: **internship_stable_2**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Internship___Job_Preparation_Agent_google_search_agent` | search | 3.22 | UNNECESSARY | current year calendar date | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Internship___Job_Preparation_Agent_google_search_agent` | search | 4.96 censored | UNNECESSARY | "Morgan State University" "computer science" "cybersecurity" courses | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): whattheday.com.

Errors: RuntimeError / 429, _ResourceExhaustedError / 429. Callback records may describe the same provider failure more than once.

Retrieval call review: **internship_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Internship___Job_Preparation_Agent_google_search_agent` | search | 7.90 | OPTIONAL | what is today's date? | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Internship___Job_Preparation_Agent_google_search_agent` | search | 21.16 | NECESSARY | cybersecurity internships summer 2027 open | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): datetoday.net, extern.com, metacareers.com, github.com, intuit.com, t-mobile.com, bankofamerica.com, ibm.com, jpmorganchase.com, walmart.com, homedepot.com, siemens.com, indeed.com, trylitos.com, pages.dev, checkpoint.com.

Retrieval call review: **internship_stable_2 [additional]**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Internship___Job_Preparation_Agent_google_search_agent` | search | 10.59 | UNNECESSARY | current year date | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Internship___Job_Preparation_Agent_google_search_agent` | search | 18.32 | UNNECESSARY | cybersecurity internship requirements 2027 entry level | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #3; tool #4 `Internship___Job_Preparation_Agent_google_search_agent` | search | 24.45 | UNNECESSARY | Morgan State University cybersecurity club program | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): saturdaygift.com, chiaroai.com, extern.com, sandiego.edu, ibm.com, research.com, coursera.org, cybrary.it, ziprecruiter.com, grm.institute, morgan.edu, hbcubuzz.com, facebook.com.

### Resume & Portfolio

Both stable samples searched. Retrieved current-market claims were injected into otherwise conceptual resume advice; completed searched answers lacked clickable source citations. Current-market frequency assertions need a defined sample and authoritative sources, or should remain clearly labelled general guidance.

Test prompt: What should I emphasize on my resume for an entry-level cloud security role?

Test prompt: What resume expectations are employers currently emphasizing for entry-level cloud security roles?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resume_stable_1 | `resume__portfolio_agent` | completed | 2.58 | 10.87 | 8.29 | 10.88 | 61.03 | 61.03 / RED |
| resume_stable_2 | `resume__portfolio_agent` | completed | 7.27 | 13.45 | 6.17 | 13.46 | 54.51 | 54.51 / ORANGE |
| resume_current_1 | `resume__portfolio_agent` | completed | 4.30 | 10.03 | 5.73 | 10.04 | 54.07 | 54.07 / ORANGE |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| resume_stable_1 | 0.01 | 2.57 | 21.21 | 2 / 2 / 2 / 5 | 0 | 37.20 | 0 |
| resume_stable_2 | 0.99 | 6.28 | 19.57 | 1 / 1 / 1 / 2 | 0 | 27.64 | 0 |
| resume_current_1 | 0.02 | 4.28 | 20.73 | 2 / 2 / 2 / 5 | 0 | 28.99 | 0 |

Retrieval call review: **resume_stable_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Resume___Portfolio_Agent_google_search_agent` | search | 7.33 | UNNECESSARY | current year date | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Resume___Portfolio_Agent_google_search_agent` | search | 29.89 | UNNECESSARY | entry-level cloud security resume skills projects 2026 | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): timeanddate.com, almanac.com, youtube.com, edirae.com, tekskillsacademy.com, artempolynko.com, enhancv.com, cloudresumechallenge.dev, medium.com, defectdojo.com, wininlifeacademy.com, skillifysolutions.com, pwnedlabs.io, unihackers.com.

Retrieval call review: **resume_stable_2**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Resume___Portfolio_Agent_google_search_agent` | search | 27.65 | UNNECESSARY | entry-level cloud security resume requirements skills | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): acsmi.org, csoh.org, enhancv.com, eccu.edu, tryhackme.com, amazon.com, wahresume.com, applybuddy.ai.

Retrieval call review: **resume_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Resume___Portfolio_Agent_google_search_agent` | search | 6.95 | OPTIONAL | current year date | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Resume___Portfolio_Agent_google_search_agent` | search | 22.07 | NECESSARY | entry-level cloud security resume skills requirements 2026 2025 | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): utctime.net, time.now, pwnedlabs.io, youtube.com, reddit.com, airesume.guru, enhancv.com, refontelearning.com, tryhackme.com, tealhq.com, networkershome.com.

### Interview Preparation

The Google-specific probe reached Interview but had no final answer by the 240 s diagnostic cutoff. Its first specialist model request waited 95.03 s before any helper, followed by four Search helpers and 35 reported queries. This does not establish pure retrieval as the only cause or permit a final company-process reliability verdict. Both stable samples used no tools and labelled advice as general industry patterns. The generic current-process test supplied no employer, yet began a date search and a cross-year generic process search before capacity failure. No completed current/company-specific answer was available to assess final reliability; clarification before retrieval is a candidate, not evidence that exact employer processes can be answered without sources.

Test prompt: Give me a technical interview preparation strategy for an entry-level cybersecurity role.

Test prompt: What is the current interview process for an entry-level cybersecurity role at a major employer?

Test prompt: What is the current interview process for an entry-level cybersecurity role at Google? Distinguish confirmed employer information from general interview patterns.

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| interview_stable_1 | `interview_preparation_agent` | completed | 3.52 | 23.88 | 20.36 | — | 23.88 | 23.88 / YELLOW |
| interview_stable_2 | `interview_preparation_agent` | completed | 2.37 | 18.47 | 16.10 | — | 18.47 | 18.47 / YELLOW |
| interview_current_1 | `interview_preparation_agent` | failed | 2.36 | 8.88 | 6.52 | 8.89 | — | 18.09 / YELLOW |
| interview_company_probe_1 | `interview_preparation_agent` | timeout_censored | 4.84 | 99.88 | 95.03 | 99.89 | — | 240.02 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| interview_stable_1 | 0.01 | 3.51 | 20.35 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| interview_stable_2 | 0.01 | 2.35 | 16.10 | 0 / 0 / 0 / 0 | 0 | 0.00 | 1 |
| interview_current_1 | 0.02 | 2.34 | 8.62 | 2 / 2 / 1 / 1 | 0 | 7.08 | 0 |
| interview_company_probe_1 | 0.01 | 4.83 | 121.77 | 4 / 4 / 4 / 35 | 0 | 113.32 | 0 |

Retrieval call review: **interview_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Interview_Preparation_Agent_google_search_agent` | search | 6.68 | OPTIONAL | what calendar year is it today | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Interview_Preparation_Agent_google_search_agent` | search | 0.42 censored | OPTIONAL | entry level cybersecurity interview process 2025 2026 | Generic employer/process unspecified; ask for company/role before claiming an exact current process. |

Observed nested source titles/domains (not independent factual verification): wikipedia.org.

Errors: RuntimeError / 429, _ResourceExhaustedError / 429. Callback records may describe the same provider failure more than once.

Retrieval call review: **interview_company_probe_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Interview_Preparation_Agent_google_search_agent` | search | 17.63 | OPTIONAL | current year date today | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Interview_Preparation_Agent_google_search_agent` | search | 24.59 | NECESSARY | Google Associate Security Engineer interview process | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #3; tool #4 `Interview_Preparation_Agent_google_search_agent` | search | 28.32 | NECESSARY | site:careers.google.com "security engineer" interview process | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #4; tool #5 `Interview_Preparation_Agent_google_search_agent` | search | 42.82 | NECESSARY | site:careers.google.com "technical interview" security OR cybersecurity | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): datetoday.net, chillinterview.com, crackingwalnuts.com, interviewhelp.io, skillpanel.com, prepnplaced.com, dataford.io, interviewkickstart.com, reddit.com, quora.com, medium.com, haiderm.com, interviews.chat, finalroundai.com, startup.jobs, cleverprep.com, substack.com, migratemate.co, localjobs.com, google.com, resumize.ai, theinterviewguys.com, myinternships.in, greatfrontend.com, lgbtqhire.com, microsoft.com, newopportunitiespress.com.

Errors: TimeoutError / None. Callback records may describe the same provider failure more than once.

### Networking & Professional Communication

The current request took 160.70 s, used six sequential Search helpers and 59 reported queries, and never used URL Context. It labelled an extensive club/event ecosystem active as of 2026 and added Google partnership/cloud-access benefits without per-claim current-status verification. Only the Handshake portal was linked in the final answer. Targeted club lookups expanded into history, national societies and research infrastructure rather than bounding actionable networking resources.

Test prompt: How should I introduce myself to a cybersecurity recruiter?

Test prompt: What current networking resources can Morgan State Computer Science students use?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| networking_stable_1 | `networking__professional_communication_agent` | completed | 2.16 | 18.02 | 15.86 | — | 18.02 | 18.02 / YELLOW |
| networking_stable_2 | `networking__professional_communication_agent` | completed | 2.67 | 16.94 | 14.28 | — | 16.94 | 16.95 / YELLOW |
| networking_current_1 | `networking__professional_communication_agent` | completed | 8.22 | 14.31 | 6.09 | 14.35 | 160.69 | 160.70 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| networking_stable_1 | 0.01 | 2.15 | 15.86 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| networking_stable_2 | 0.01 | 2.65 | 14.27 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| networking_current_1 | 1.13 | 7.08 | 23.66 | 6 / 6 / 6 / 59 | 0 | 128.66 | 1 |

Retrieval call review: **networking_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Networking___Professional_Communication_Agent_google_search_agent` | search | 6.67 | OPTIONAL | current calendar year | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Networking___Professional_Communication_Agent_google_search_agent` | search | 23.27 | NECESSARY | Morgan State University Computer Science student organizations networking resources | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #3; tool #4 `Networking___Professional_Communication_Agent_google_search_agent` | search | 10.96 | REDUNDANT | Morgan State "SACS" Computer Science | The broad discovery already described SACS; this follow-up largely added history without establishing current schedules. |
| Search helper #4; tool #5 `Networking___Professional_Communication_Agent_google_search_agent` | search | 38.34 | OPTIONAL | "WiCyS" "Morgan State" | Expanded the resource inventory into more clubs and partnership detail instead of verifying a bounded core set. |
| Search helper #5; tool #6 `Networking___Professional_Communication_Agent_google_search_agent` | search | 40.76 | OPTIONAL | "Google Developer Student Club" "Morgan State" | Expanded the resource inventory into more clubs and partnership detail instead of verifying a bounded core set. |
| Search helper #6; tool #7 `Networking___Professional_Communication_Agent_google_search_agent` | search | 8.76 | NECESSARY | Morgan State "Handshake" Center for Career Development | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): saturdaygift.com, morgan.edu, honorsociety.org, excelsior.edu, wikipedia.org, wicys.org, thehbcuadvocate.com, hbcuconnect.com, devpost.com, watchtheyard.com, nsf.gov, instagram.com, campusesp.com, dlslibrary.state.md.us, uic.edu, hbculifestyle.com, archives.gov, researchgate.net, purdue.edu, lsu.edu, googleblog.com, engineering.com, google.com.

### Skill Gap & Career Roadmap

The clarified current roadmap probe reached Skill Gap & Career Roadmap and completed in 53.23 s with two Search helpers and five reported queries. The clarified answer separated observed requirements, general patterns and a preparation sequence, but supplied no final links or defined posting sample for its 2026 market claims. The original current market-skills prompt routed to Career Exploration, retried discovery twice, then returned an off-scope Morgan-resource no-evidence answer after 62.18 s. The first target is not intrinsically forbidden, but its pipeline answered the wrong question. This is an ownership/scope boundary, not a completed Skill Roadmap current benchmark. The first stable sample used a date lookup plus two substantially overlapping current-market lookups, including a repeated reported query and predominantly training/job-aggregator sources. The second routed in 2.89 s but awaited a specialist model response without helper calls until the 240 s cutoff. Tool budgets cannot explain or fix that separate stalled sample; capacity/model wait needs isolation. Treat the routing/renderer mismatch and availability tail as cross-workflow escalations rather than proof that all delay is caused by Roadmap retrieval.

Test prompt: I want to become a cloud security engineer. What skills should I build over the next year?

Test prompt: Which current technologies and skills are appearing most often in entry-level cloud security roles?

Test prompt: For my cloud security skill-gap roadmap, what current tools and technologies should I prioritize based on recent entry-level job postings?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| roadmap_stable_1 | `skill_gap__career_roadmap_agent` | completed | 4.13 | 10.69 | 6.55 | 10.70 | 78.19 | 78.19 / RED |
| roadmap_stable_2 | `skill_gap__career_roadmap_agent` | timeout_censored | 2.88 | — | — | — | — | 240.01 / RED |
| roadmap_current_1 | `career_exploration_agent` | completed | 3.80 | 3.80 | 0.00 | 14.09 | 62.18 | 62.18 / RED |
| roadmap_current_probe_1 | `skill_gap__career_roadmap_agent` | completed | 8.17 | 14.10 | 5.93 | 14.12 | 53.23 | 53.23 / ORANGE |
| roadmap_stable_2 [additional] | `None` | failed | — | — | — | — | — | 80.33 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| roadmap_stable_1 | 0.01 | 4.12 | 27.59 | 3 / 3 / 3 / 10 | 0 | 46.42 | 0 |
| roadmap_stable_2 | 0.01 | 2.87 | 237.12 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| roadmap_current_1 | 0.01 | 3.78 | 16.15 | 2 / 2 / 2 / 5 | 0 | 42.18 | 0 |
| roadmap_current_probe_1 | 1.08 | 7.08 | 22.09 | 2 / 2 / 2 / 5 | 0 | 22.91 | 0 |
| roadmap_stable_2 [additional] | 0.01 | 80.31 | 0.00 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |

Retrieval call review: **roadmap_stable_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Skill_Gap___Career_Roadmap_Agent_google_search_agent` | search | 6.68 | UNNECESSARY | current date and year | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Skill_Gap___Career_Roadmap_Agent_google_search_agent` | search | 17.13 | UNNECESSARY | entry level cloud security engineer job requirements 2026 | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #3; tool #4 `Skill_Gap___Career_Roadmap_Agent_google_search_agent` | search | 22.64 | REDUNDANT | "cloud security engineer" "entry level" OR "junior" job posting requirements 2026 | Substantially overlaps the preceding skill-market summary and repeats a reported query; both are outside the stable request. |

Observed nested source titles/domains (not independent factual verification): datetoday.net, futurense.com, sritechsolutions.com, augusta.edu, coursera.org, ziprecruiter.com, refontelearning.com, examos.io, offsec.com, migratemate.co, cybersn.com, ekascloud.com, cover6solutions.com, practical-devsecops.com, youtube.com, jobleads.com, fusioncyber.co, quickstart.com, unihackers.com, encryptedgelabs.com, kore1.com, indeed.com.

Retrieval call review: **roadmap_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Career_Exploration_Agent_google_search_agent` | search | 23.51 | NECESSARY | entry-level cloud security roles skills technologies requirements | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #2; tool #3 `Career_Exploration_Agent_google_search_agent` | search | 18.70 | OPTIONAL | verify_evidence_candidate(candidate_id="C2") | A bounded retry sought usable sources under the wrong resource scope. It did not repair the task mismatch; insufficient first evidence prevents calling every retry redundant. |

Observed nested source titles/domains (not independent factual verification): amazon.com, tryhackme.com, pwnedlabs.io.

Retrieval call review: **roadmap_current_probe_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Skill_Gap___Career_Roadmap_Agent_google_search_agent` | search | 7.41 | OPTIONAL | current calendar date year today | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Skill_Gap___Career_Roadmap_Agent_google_search_agent` | search | 15.53 | NECESSARY | "entry level" "cloud security" engineer job requirements skills 2026 OR 2025 | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): truecalendar.com, augusta.edu, serveracademy.com, futurense.com, refontelearning.com, tryhackme.com, unihackers.com, kore1.com, wahresume.com, icims.com, networkershome.com, airesume.guru, offsec.com, amazon.com, enhancv.com.

### Research & Graduate Pathways

The current-opportunity sample completed in 226.91 s with eight Search helpers, 86 reported queries, zero URL Context, and zero final source links. Helper elapsed time was 188.77 s versus a 2.13 s transfer. It labelled many labs/programs active for 2026–2027 and asserted exact scholarship benefits, departmental eligibility and current staff roles; CURRENT CYCLE UNVERIFIED caveats do not verify those additional assertions. The original degree-choice prompt first routed to Career Exploration (no retrieval), then to Research (two searches). Do not pool those as two measurements of the same specialist. The Research response introduced active-program, credit-count and online-modality assertions without URL inspection or final source links. Two explicit research-readiness probes retain the original cases while disambiguating intent.

Test prompt: How should I decide between graduate school and going directly into cybersecurity industry work?

Test prompt: What current cybersecurity research or graduate opportunities should I investigate at Morgan State?

Test prompt: What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs.

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| research_stable_1 | `career_exploration_agent` | completed | 5.99 | 5.99 | 0.00 | — | 46.62 | 46.62 / ORANGE |
| research_stable_2 | `research__graduate_pathways_agent` | completed | 4.25 | 10.79 | 6.54 | 10.80 | 49.07 | 49.07 / ORANGE |
| research_current_1 | `research__graduate_pathways_agent` | completed | 2.13 | 7.66 | 5.53 | 7.67 | 226.91 | 226.91 / RED |
| research_readiness_stable_1 | `research__graduate_pathways_agent` | completed | 2.40 | 5.92 | 3.52 | 5.93 | 29.40 | 29.40 / YELLOW |
| research_readiness_stable_2 | `research__graduate_pathways_agent` | completed | 3.20 | 18.73 | 15.53 | — | 18.73 | 18.73 / YELLOW |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| research_stable_1 | 0.01 | 5.97 | 40.62 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| research_stable_2 | 0.01 | 4.23 | 22.68 | 2 / 2 / 2 / 7 | 0 | 22.11 | 0 |
| research_current_1 | 0.02 | 2.11 | 35.84 | 8 / 8 / 8 / 86 | 0 | 188.77 | 0 |
| research_readiness_stable_1 | 0.02 | 2.38 | 14.89 | 1 / 1 / 1 / 3 | 0 | 12.07 | 0 |
| research_readiness_stable_2 | 0.02 | 3.18 | 15.52 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |

Retrieval call review: **research_stable_2**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 6.49 | UNNECESSARY | current year calendar date | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |
| Search helper #2; tool #3 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 15.64 | UNNECESSARY | Morgan State University Computer Science graduate programs cybersecurity | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): datetoday.net, morgan.edu, maryland.gov.

Retrieval call review: **research_current_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 7.20 | OPTIONAL | current year date | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 23.59 | NECESSARY | Morgan State University cybersecurity research labs programs | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #3; tool #4 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 30.87 | NECESSARY | Morgan State University Computer Science Department cybersecurity research | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #4; tool #5 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 38.59 | NECESSARY | "Scholarship for Service" "Morgan State University" application deadline | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #5; tool #6 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 38.27 | NECESSARY | "Morgan State University" "Computer Science" "Scholarship for Service" | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #6; tool #7 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 22.95 | OPTIONAL | "Guobin Xu" "Morgan State" "Quantum-Enabled IoT Security" | Expanded from core programs/scholarship questions into additional faculty/project inventories instead of verifying a bounded selected set. |
| Search helper #7; tool #8 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 14.37 | OPTIONAL | "TRAILS" "Morgan State" "GUARD" | Expanded from core programs/scholarship questions into additional faculty/project inventories instead of verifying a bounded selected set. |
| Search helper #8; tool #9 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 13.04 | OPTIONAL | "C4 Lab" "Morgan State" Onyema Osuagwu | Expanded from core programs/scholarship questions into additional faculty/project inventories instead of verifying a bounded selected set. |

Observed nested source titles/domains (not independent factual verification): time.gov, timeanddate.com, morgan.edu, nist.gov, github.io, computer.org, researchgate.net, ieee.org, thec4lab.com, blogspot.com, opm.gov, grantedai.com, louisville.edu, marymount.edu, securitymagazine.com, nsf.gov, cybersecurityguide.org, fsu.edu, google.com, mdpi.com, jhu.edu.

Retrieval call review: **research_readiness_stable_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Research___Graduate_Pathways_Agent_google_search_agent` | search | 12.09 | UNNECESSARY | "Morgan State University" cybersecurity research lab center | Judge against the original conceptual request; omit unsolicited current facts rather than retaining them ungrounded. |

Observed nested source titles/domains (not independent factual verification): morgan.edu, youtube.com, maryland.gov, researchgate.net, einnews.com.

### Certification & Technical Development

Stable certification decision guidance was tool-free, but one sample asserted provider-specific student discounts (often 50% or more) and another discussed government credential requirements without retrieved evidence. No current version/price answer completed in this profiling run: one root request failed immediately; an additional attempt reached three Search helpers and failed at 91.94 s. The broad helper returned approximate prices and a future-version transition; the subsequent official-provider refinement was justified, not automatically redundant.

Test prompt: How should I decide whether a cybersecurity certification is worth pursuing?

Test prompt: What is the current CompTIA Security+ exam version and price?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| certification_stable_1 | `certification__technical_development_agent` | completed | 2.83 | 16.21 | 13.38 | — | 16.22 | 16.22 / YELLOW |
| certification_stable_2 | `certification__technical_development_agent` | completed | 3.21 | 20.26 | 17.05 | — | 20.26 | 20.26 / YELLOW |
| certification_current_1 | `None` | failed | — | — | — | — | — | 0.80 / GREEN |
| certification_current_1 [additional] | `certification__technical_development_agent` | failed | 9.52 | 18.52 | 9.01 | 18.54 | — | 91.94 / RED |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| certification_stable_1 | 0.01 | 2.82 | 13.38 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| certification_stable_2 | 0.01 | 3.20 | 17.04 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| certification_current_1 | 0.02 | 0.78 | 0.00 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| certification_current_1 [additional] | 1.08 | 8.43 | 12.69 | 3 / 3 / 2 / 4 | 0 | 69.67 | 0 |

Retrieval call review: **certification_current_1 [additional]**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Certification___Technical_Development_Agent_google_search_agent` | search | 7.33 | OPTIONAL | current year | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Certification___Technical_Development_Agent_google_search_agent` | search | 10.13 | NECESSARY | current CompTIA Security+ exam version 2026 | Current external claim needs evidence; number of calls alone does not establish redundancy. |
| Search helper #3; tool #4 `Certification___Technical_Development_Agent_google_search_agent` | search | 52.25 censored | NECESSARY | site:comptia.org "Security+" exam code "SY0-701" price OR voucher | Current external claim needs evidence; number of calls alone does not establish redundancy. |

Observed nested source titles/domains (not independent factual verification): thecurrentdate.com, certgps.com, acilearning.com, cyberkrafttraining.com, secuspark.com, comptia.org, getcertified4less.com, youtube.com, epicdetect.io, trainingcamp.com, figigexams.com.

Errors: RuntimeError / 429, _ResourceExhaustedError / 429. Callback records may describe the same provider failure more than once.

### Trust & Human Escalation

The conflict sample completed in 100.16 s with three Search helpers, 39 reported queries, no URL Context and no final source links. Despite no identified program or source pair, it declared Morgan programs fully active for 2026–2027 and guessed causes for the conflict, including program transitions and funding events. This does not resolve the student’s actual contradictory evidence. Human escalation took 19.37 s with a calendar-only search and 9.06 s without tools. The searched result only asked for the missing decision/evidence details, so the date lookup was unused. Conflict and generic reliability requests must not invent the program, sources, or disagreement being reconciled.

Test prompt: I need a human to review this because the evidence is contradictory and this decision matters.

Test prompt: I found conflicting information about whether a Morgan cybersecurity program is still active. Which source should I trust?

Test prompt: How reliable is this current information if the sources disagree?

| Sample | First target | Status | Transfer | First specialist event | Handoff | First helper | First public text | Total / band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trust_human_1 | `trust__human_escalation_agent` | completed | 1.59 | 8.47 | 6.88 | 8.48 | 19.37 | 19.37 / YELLOW |
| trust_human_2 | `trust__human_escalation_agent` | completed | 1.87 | 9.05 | 7.18 | — | 9.06 | 9.06 / GREEN |
| trust_conflict_1 | `trust__human_escalation_agent` | completed | 2.69 | 10.70 | 8.01 | 10.71 | 100.16 | 100.16 / RED |
| trust_reliability_1 | `trust__human_escalation_agent` | completed | 2.17 | 9.82 | 7.64 | — | 9.82 | 9.82 / GREEN |

All times above are seconds from invocation start except handoff, which is a duration.

| Sample | Root request start | Root model wait | First-target model wait | Search H / E / G / Q | URL helpers | Retrieval union | Final URL count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trust_human_1 | 0.01 | 1.57 | 11.49 | 1 / 1 / 1 / 2 | 0 | 6.27 | 0 |
| trust_human_2 | 0.01 | 1.86 | 7.18 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |
| trust_conflict_1 | 0.02 | 2.67 | 22.63 | 3 / 3 / 3 / 39 | 0 | 74.77 | 0 |
| trust_reliability_1 | 0.01 | 2.16 | 7.63 | 0 / 0 / 0 / 0 | 0 | 0.00 | 0 |

Retrieval call review: **trust_human_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Trust___Human_Escalation_Agent_google_search_agent` | search | 6.28 | UNNECESSARY | current date and year | No concrete source/claim supplied; clarify/review framework first. Calendar lookup does not resolve the disagreement. |

Observed nested source titles/domains (not independent factual verification): datetoday.net, saturdaygift.com.

Retrieval call review: **trust_conflict_1**

| Call | Kind | Duration (s) | Necessity | Request / purpose | Rationale |
| --- | --- | --- | --- | --- | --- |
| Search helper #1; tool #2 `Trust___Human_Escalation_Agent_google_search_agent` | search | 7.38 | OPTIONAL | current year date | Cycle context is useful, but a future trusted runtime timestamp could replace a calendar search; none was injected here. |
| Search helper #2; tool #3 `Trust___Human_Escalation_Agent_google_search_agent` | search | 20.55 | OPTIONAL | Morgan State University cybersecurity program | Program and contradictory sources unspecified; any broad search is exploratory, not resolution of the specific conflict. |
| Search helper #3; tool #4 `Trust___Human_Escalation_Agent_google_search_agent` | search | 46.87 | OPTIONAL | "Morgan State" cybersecurity program inactive discontinued | Program and contradictory sources unspecified; any broad search is exploratory, not resolution of the specific conflict. |

Observed nested source titles/domains (not independent factual verification): truecalendar.com, calendar-365.com, morgan.edu, cybersecurityeducationguides.org, usmd.edu, marketscale.com, insidehighered.com, login-master.com, calpoly.edu, arizona.edu.

## Cross-Workflow Patterns

1. **Stable-to-current scope expansion is measurable.** Internship, Resume, Roadmap and Research introduced current-market or Morgan-specific details into conceptual requests. Those claims then triggered date/domain searches. A fast path must stay general or ask for context; it must not retain ungrounded versions of those facts.
2. **Model/provider waiting and retrieval are different bottlenecks.** Research spent 188.77 s in helpers during a 226.91 s response, Networking made 59 reported queries, Roadmap waited about 237 s without tools after a fast handoff, and Certification spent about 69.67 s in helpers before a 429. The additional Roadmap-labelled sample failed at the root after 80.33 s, before dispatch, so provider/model tails can occur at either stage. Tool budgets alone cannot remove capacity stalls.
3. **A helper call is not one search query.** Career control used one Search helper but exposed six queries; Internship current used two helpers and exposed ten queries. Report all levels rather than claiming helper limits bound Google internal queries.
4. **Source traceability is weaker outside the reference registry.** Several searched answers had source metadata in nested helpers but no final links or URL inspection. Generic AgentTool wrappers are not configured to propagate grounding metadata; summaries alone do not preserve per-claim evidence. Official-domain discovery is helpful but does not by itself establish open dates, exact eligibility, active benefits or pricing.
5. **Currentness and precision need explicit bounds.** Research labelled institutional programs active and supplied specific requirements on a stable question; Internship listed open roles before learning the student background; Certification stable advice included provider-discount figures without evidence. Treat these as grounding gaps, not independently proven false claims.
6. **Trust still broadens an unspecified conflict.** The conflict test used three helpers and 39 queries, then asserted fully active programs and speculative explanations without an identified source pair. That is a completed reliability concern, not merely latency. **Trust human escalation separately has a viable no-tool path.** The two samples differed by an unused calendar lookup. Do not search an unspecified disagreement instead of first asking for the claim, sources and intended decision.
7. **Routing and evidence scope affect attribution.** The generic current skills-market prompt reached Career Exploration and returned a Morgan-resource no-evidence response rather than the requested skills. Its two discovery attempts did not verify the secondary market candidates. Career is the reference for its validated Morgan-resource scope, not a universal renderer/source policy. A clarified Roadmap probe preserves this original failure. **Routing overlap also affects stable attribution.** The degree-choice prompt reached different specialists. The report preserves actual first targets; clarified readiness probes do not replace those observations or change routing.
8. **Capacity failures limit conclusions.** 429-affected and deadline-censored requests cannot support final-answer quality or completed-latency claims. Repeated retrieval is not automatically redundant: Certification’s official refinement followed an approximate broad result.

### Previous v4 context (not new local samples)

The validated remote v4 smoke/evidence totals were approximately 22.71/53.69 s. The prior Flask Certification test completed in 165.12 s with four Search helpers; its fourth helper alone took 112.59 s, while the initial transfer occurred at 2.44 s. The new additional local Certification attempt failed at 91.94 s after three helpers, with 69.67 s retrieval. This supports retrieval/provider waiting as a major suspect, not routing as the dominant cause. It does not prove all 165 s was redundant work or reproduce a completed Certification current answer in this run.

## Recommended Optimization Waves

**Wave 0 - Restore measurement confidence.** Re-run only capacity-affected or censored cases when the provider is healthy, preserve failed samples, and compare local and v4 runs separately. Investigate model-request stalls without assuming prompt size or tool loops caused them. Do not choose models or change retry policy from censored data alone.

**Wave A - Stable/clarification intent gates.** First prevent Trust from inventing a program or source pair for an unspecified conflict. Prioritize Internship, Resume, Roadmap and Research for conceptual-only responses without unsolicited current facts. Preserve Interview/Networking/Certification no-tool strengths, remove unsupported vendor-specific details from conceptual Certification advice, and keep explicit human-escalation clarification tool-free. Confirm ambiguous Research routing before optimizing it.

**Wave B - Bound current discovery.** Include Interview’s role-specific/company clarification and source limits; do not infer a universal Google process from generic preparation sites. Start with Research’s eight-helper program/project expansion, Networking’s six-helper resource expansion, and Certification’s official version/price lookup and high-breadth opportunity/market searches. Set explicit candidate/claim scope, ask for missing employer/student context before broad searches, and combine compatible official-source lookups. Track internal reported query breadth as well as parent helper counts; do not delete justified refinements.

**Wave C - Evidence enforcement where observed facts require it.** Apply selective deterministic transport/status/citation handling to exact certification prices/versions, internship eligibility/opening dates, institutional program/activity claims and any current market claims retained. Career Exploration is a reference design, not a mandate to copy its registry into every agent. Stable writing/coaching paths should not acquire retrieval machinery merely for consistency.

**Wave D - Complete Trust evidence enforcement (after the Wave A clarification gate).** Preserve human escalation and uncertainty. For concrete conflicts, require the specific claim and sources, selectively inspect authoritative evidence, and avoid broad institutional searching or historical-to-current upgrades. The new three-helper/39-query conflict case independently justifies high priority; do not rely only on the older misrouted v3 request.

For market-frequency requests, a handful of example resources does not prove what appears most often across employers. Use a defined posting sample and appropriately limited wording; do not blindly copy the resource-oriented registry into market-analysis tasks.

**Wave E - Rebenchmark and review quality.** Repeat the same matrix, retain at least two completed stable samples where possible, include clarified probes separately, and verify source/date/status/citation boundaries alongside time. Do not promote or deploy from this report. All optimization waves are recommendations only.

## Reproduce and inspect

Use the pinned workflow environment and authenticated development credentials. The harness does not call production or any Agent Engine endpoint.

```powershell
python -B tests/diagnostics/career_baseline.py
python -B tests/diagnostics/career_baseline.py --live --resume --research-probes --roadmap-probe --interview-probe --pace 20
python -B -m pytest tests/diagnostics/test_career_baseline.py -q -p no:cacheprovider
```

Live commands are billable model requests. Stop after a capacity error; cooldown/resume is deliberate, not an automatic retry. Read `tests/diagnostics/README.md` before running. Raw allowlisted measurements and quality outputs are in `tests/diagnostics/career_baseline.json` and `tests/diagnostics/career_baseline_followup.json`. No credentials, session identifiers, hidden reasoning or signatures belong in these artifacts.

Product workflow prompts, models, tools, routing, backend/frontend, production/default configuration and deployed engines remain unchanged. This profiling work is diagnostic/report infrastructure only; no deployment, commit or push is part of it.

## Validation and safety

- Seven offline harness tests passed; new Python sources parse successfully. A separate network-blocked synthetic nested-runner check covered helper instrumentation and thought/signature exclusion.
- Both JSON artifacts parse; all captured canonical workflow source hashes still match. Manual retrieval review labels are retained alongside initial classifications. Credential-pattern and forbidden-field scans passed.
- `git diff --check` and separate whitespace checks covering all six untracked diagnostic/report files passed. Tracked files and index are unchanged at the checkpoint commit.
- Only the harness, its offline tests/README, two measurement artifacts and this report were created. No product behavior, deployment, existing engine, production inference, commit or push was performed.
## Wave 1 — Stable Fast-Path Results

### Scope and instruction discipline

The preserved sections above describe the pre-Wave 1 profiling checkpoint; their unchanged-product/source-hash statements apply to that historical baseline. Wave 1 intentionally changes only the four appended specialist instruction sections described below.

Appended a stable-guidance gate only to Internship, Resume, Skill Gap & Career Roadmap, and Research & Graduate Pathways. Existing instructions remain verbatim as the left operand of string concatenation. The gate runs before Search, URL Context and date/cycle resolution: answer stable concepts from general professional knowledge and student context; do not retrieve for enrichment or introduce optional current facts. Requested external/current facts still activate the original evidence procedures. No new current-path search budget, helper change, retry or runtime enforcement was added.

- Internship: preparation, application/search organization and readiness assessment use direct guidance; current openings, eligibility, employer requirements and cycles retain retrieval. An additional compact output boundary uses generic local labs rather than named services or unverified free/access claims and forbids declaring eligibility from graduation timing alone.
- Resume: structure, truthful bullets, project framing, broad-role tailoring and general readable formatting use direct guidance; current postings and employer/market requirements retain retrieval.
- Roadmap: foundational skills, sequencing and context-based development plans use direct guidance; current posting-frequency, vendor availability and version claims retain retrieval.
- Research: graduate/industry tradeoffs, degree comparison, research fit and general preparation use direct guidance; current Morgan opportunities, programs, faculty, funding, deadlines and labs retain retrieval.

Career Exploration, Trust, the root orchestrator, Interview, Networking, Certification, every helper, evidence.py, backend and frontend remain untouched. Secondary specialists had no observed unnecessary stable retrieval and were intentionally excluded. Models, names, tools, sub-agent relationships and callbacks are unchanged.

### Validation method and preliminary correction

Final acceptance selection: eight stable canaries (two per modified specialist) plus four current activation cases. Six superseded saved observations and one interrupted unsaved request are retained/described separately; earlier quality failures are not erased or promoted to passes.

Used the existing harness, pinned SDK 1.165.1 / ADK 2.12.0, fresh local sessions and unchanged root routing. Samples for the unchanged Resume/Research gates are in `career_wave1.json`; final Internship/Roadmap repeats and all current canaries are in `career_wave1_followup.json`. Their source manifests distinguish revisions; they are separate from the original baseline. Counts measure observed helper invocations, not undisclosed provider work.

Two preliminary samples are preserved in `career_wave1_initial.json`: Internship 28.65 s and Resume 21.55 s, both tool-free. The Internship answer nevertheless recommended a named free SIEM, failing the stable availability boundary. The batch was interrupted during the next Roadmap request (no saved final response or latency verdict). Only the appended Internship gate was strengthened; canaries were restarted in a new artifact. The second Internship sample then asserted eligibility from graduation timing alone. Both Internship samples from that revision remain in career_wave1.json; only its appended gate was further tightened to avoid unsolicited eligibility/calendar rules on preparation-only questions and preserve posting-specific uncertainty. Roadmap’s second response also recommended a free-tier cloud account without evidence; only its appended stable-output gate was tightened to use local/simulated labs without unverified free/access claims. Two final repeats for each of Internship and Roadmap are in career_wave1_followup.json. Both earlier Roadmap samples are preserved and excluded from final acceptance comparisons. These earlier Internship observations are not final acceptance samples. Preliminary runs are excluded from final pass counts and latency comparisons.

### Stable before/after

Each cell lists individual completed observations where available, not percentile estimates or speed guarantees. Root-only failures/cutoffs and routes to other specialists are explicitly separate.

| Specialist | Baseline latency (s) | Baseline Search | Final stable latency (s) | Final Search | Final URL Context | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Internship & Job Preparation | 67.39 / 90.29 | 2 / 3 | 28.22 / 17.73 | 0 / 0 | 0 / 0 | PASS |
| Resume & Portfolio | 61.03 / 54.51 | 2 / 1 | 22.66 / 22.50 | 0 / 0 | 0 / 0 | PASS |
| Skill Gap & Career Roadmap | 78.19 / >=240 cutoff | 3 / 0 (cutoff) | 23.93 / 18.20 | 0 / 0 | 0 / 0 | PASS |
| Research & Graduate Pathways | 49.07 actual Research; readiness 29.40 / 18.73 | 2; readiness 1 / 0 | 23.65 / 31.84 | 0 / 0 | 0 / 0 | PASS |

Baseline URL Context was zero for these stable requests. The original Research degree-choice prompt had a Career Exploration route in one baseline sample; Research samples include a final Research handoff when present; the second Wave 1 original prompt first reached Career then Research, so its 31.84 s total is a mixed-route invocation, not a pure Research-only comparison. Clarified readiness probes remain separately labelled and do not override routing.

### Per-sample routing, timing and quality

| Case | Actual first specialist | Status | Transfer (s) | First text (s) | Total (s) | Search / URL | Final answer | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| resume_stable_1 | `resume__portfolio_agent` | completed | 2.38 | 22.66 | 22.66 | 0 / 0 | True | PASS: Useful skill presentation, truthful bullet/project examples and follow-up intake. Named tools illustrate experience, not current access/pricing or verified employer rules. |
| research_stable_1 | `research__graduate_pathways_agent` | completed | 4.62 | 23.65 | 23.65 | 0 / 0 | True | PASS: Useful degree/industry tradeoffs and reflection questions; no named current program, funding offer, deadline or opening. General degree-duration/funding patterns remain broad rather than program-specific verification. |
| resume_stable_2 | `resume__portfolio_agent` | completed | 2.89 | 22.49 | 22.50 | 0 / 0 | True | PASS: Useful skill presentation, truthful bullet/project examples and follow-up intake. Named tools illustrate experience, not current access/pricing or verified employer rules. |
| research_stable_2 | `career_exploration_agent` | completed | 4.70 | 31.84 | 31.84 | 0 / 0 | True | PASS: Useful degree/industry tradeoffs and reflection questions; no named current program, funding offer, deadline or opening. General degree-duration/funding patterns remain broad rather than program-specific verification. First routed Career then handed off to Research; mixed-route total. Generic Morgan faculty-contact suggestion is not a verified faculty inventory or mentoring offer. |
| internship_stable_1 | `internship__job_preparation_agent` | completed | 8.73 | 28.22 | 28.22 | 0 / 0 | True | PASS: Useful local exercises, application organization and follow-up context; no named open role, cycle, deadline or free/access claim. |
| roadmap_stable_1 | `skill_gap__career_roadmap_agent` | completed | 3.22 | 23.93 | 23.93 | 0 / 0 | True | PASS: Useful conceptual skill profile, staged plan/intake and practice suggestions; no free-tier offer, current posting-frequency claim, exact vendor version or access/availability guarantee. Residual generalization: engineers rarely using consoles is overstated general guidance, not verified current-market evidence. |
| internship_stable_2 | `internship__job_preparation_agent` | completed | 2.31 | 17.73 | 17.73 | 0 / 0 | True | PASS: Useful local exercises, application organization and follow-up context; no named open role, cycle, deadline or free/access claim. Residual coaching-quality caveat: declares high competitiveness from remaining enrollment alone; this prediction is unsupported and not validated by the zero-retrieval result. |
| roadmap_stable_2 | `skill_gap__career_roadmap_agent` | completed | 2.61 | 18.20 | 18.20 | 0 / 0 | True | PASS: Useful conceptual skill profile, staged plan/intake and practice suggestions; no free-tier offer, current posting-frequency claim, exact vendor version or access/availability guarantee. |
| internship_current_1 | `internship__job_preparation_agent` | completed | 8.21 | 26.60 | 26.60 | 1 / 0 | True | ACTIVATED: Current canary checks retrieval availability only; 75-second diagnostic ceiling. No current factual-quality pass or latency improvement is claimed. Observed calendar Search invocation only, with zero reported grounding queries; final asks for missing background. Opportunity-domain discovery and current openings are not verified by this sample. |
| resume_current_1 | `resume__portfolio_agent` | timeout_censored | 3.44 | not observed | 75.01 | 3 / 0 | False | INVOKED / DIAGNOSTIC CUTOFF: Current canary checks retrieval availability only; 75-second diagnostic ceiling. No current factual-quality pass or latency improvement is claimed. |
| research_current_1 | `research__graduate_pathways_agent` | failed | 2.59 | not observed | 19.91 | 1 / 0 | False | ATTEMPTED / CAPACITY BLOCKED: Current canary checks retrieval availability only; 75-second diagnostic ceiling. No current factual-quality pass or latency improvement is claimed. Calendar Search invocation was provider-blocked; no successful domain discovery. |
| roadmap_current_probe_1 | `skill_gap__career_roadmap_agent` | timeout_censored | 11.67 | not observed | 75.02 | 1 / 0 | False | INVOKED / DIAGNOSTIC CUTOFF: Current canary checks retrieval availability only; 75-second diagnostic ceiling. No current factual-quality pass or latency improvement is claimed. Only calendar Search was invoked; helper did not return before cutoff. Domain market discovery remains unverified. |

Stable pass requires zero Search, zero URL Context, a completed useful final answer and no unsupported current-specific claim. General role patterns and hypothetical exercises are distinguished from exact current employer rules. Current canaries use a 75-second diagnostic ceiling to limit expensive work; this is not an application timeout or a current-path latency benchmark. They establish retrieval activation only; their factual-quality or latency weaknesses remain outside Wave 1.

### Current-path activation

Internship invoked the calendar Search helper then asked for missing background; it exposed zero grounding queries. This confirms tool-path activation only, not a completed opportunity lookup. Resume completed domain Search calls before cutoff. Research calendar Search failed with 429; Roadmap calendar Search was invoked but never returned before cutoff. These observations demonstrate the gates did not suppress tool invocation, but do not establish complete current-fact execution for all four specialists.

| Specialist | Case | Actual target | Search | URL Context | Status | Activation verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Internship & Job Preparation | internship_current_1 | `internship__job_preparation_agent` | 1 | 0 | completed | ACTIVATED on target |
| Resume & Portfolio | resume_current_1 | `resume__portfolio_agent` | 3 | 0 | timeout_censored | INVOKED / DIAGNOSTIC CUTOFF |
| Skill Gap & Career Roadmap | roadmap_current_probe_1 | `skill_gap__career_roadmap_agent` | 1 | 0 | timeout_censored | INVOKED / DIAGNOSTIC CUTOFF |
| Research & Graduate Pathways | research_current_1 | `research__graduate_pathways_agent` | 1 | 0 | failed | ATTEMPTED / 429 BLOCKED |

### Hash and structural parity

SHA-256 hashes cover the UTF-8 decoded instruction strings. Full hashes for all 30 components are retained in `tests/diagnostics/career_wave1_parity.json`.

| Specialist instruction | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| `internship__job_preparation_agent` | `3d19d074be49aab3ded43e6784b1ad63a976f5c91fee381bb939f4b011d168a8` | `cd4014bbaae6fec25e81b3846a955c07e2e27f430581f218271e54783f7233bb` |
| `resume__portfolio_agent` | `0281946a50ac51e8145645eeec20361806a19a8179f43ed0272a492a7b4a7667` | `c536bc979c045b9ee218431a0be5e6f6bc4ab57ff71b36860b49dee66ce637c2` |
| `skill_gap__career_roadmap_agent` | `1b652dcac199b687d79d7a5f61e698b7545fe9372ceb6767c1f949089aee5df8` | `0f5a5146b54c7db4d32a23ef2b44b40121481d9fbd8122cac96d88cc4e0aeee7` |
| `research__graduate_pathways_agent` | `25693f3ee7cfbecd3c27a624bfb4616468e99b2300acb56f3bda1934437b44b6` | `886466acad54d0cf724d13977794e0d4768dabc375931e0da332fbf42cb63972` |

All 26 untouched component instruction hashes match the checkpoint. Removing the four appended string literals yields an AST identical to checkpoint agent.py, proving unchanged original prompts and all non-instruction fields. Career, Trust and root assignment source segments also match Git after line-ending normalization. Career and Trust instruction contents are identical byte-for-byte as UTF-8.

### Offline checks, limitations and safety

**Verdict:** all eight selected stable samples passed the observed zero-retrieval/current-specific-claim checks, with residual coaching/generalization caveats above. Current tool invocation occurred for all four specialists, but full current-fact execution remains unverified because of intake, a provider 429, and diagnostic cutoffs. This is not an unconditional all-path validation or deployment approval.

- Evidence: 12 network-free unittest cases passed in the pinned ADK environment. Configuration: 11 pytest cases passed. Diagnostic harness: 7 pytest cases passed. The initial combined invocation in the repository environment could not collect evidence tests because that environment lacks ADK; the evidence suite passed after using the pinned environment. No dependency file was changed.
- Syntax/structural checks passed. Root agent (nine specialists) and AdkApp import succeeded with socket connections blocked.
- Original baseline JSON files retain their captured hashes. The original report is preserved byte-for-byte before this appended section. Measurements are small samples with provider variance; a prompt gate is behavioral guidance, not a deterministic tool firewall.
- Final whitespace, privacy, scope and source checks are recorded below after validation. No cloud deployment, Agent Engine operation, production inference, backend/frontend edit, commit or push was performed.

Live execution paused for more than two minutes after the Research 429 before attempting only the previously unattempted Roadmap current canary. Research was not retried.

Capacity failures in acceptance/activation samples: 1. Research Search activation was attempted but provider-blocked; that current check is not a successful execution or reliability pass. No retry of the Research path was made. Failed paths are not counted as passes.

Final validation: git diff --check and untracked-file whitespace checks passed; final source/hash parity, baseline preservation, JSON/privacy scans and repository scope checks passed. Index is unchanged and HEAD remains the checkpoint.
## Wave 2 — Current Retrieval Bounding

### Scope and mechanism

Appended current-fact budgets to Networking, Research, Certification and Interview. Default discovery is one Search helper; exceptional discovery is limited to a second, never a third. Research allows the second only when the first returns zero usable official evidence; Interview requires no usable first evidence and a necessary, explicitly anecdotal secondary context. Search-helper counts differ from underlying grounding-query counts.

Calendar-only Search is explicitly overridden. Use provided runtime/user timing; otherwise use cycle-neutral official-source discovery or request essential cycle context without guessing a year. Existing evidence, uncertainty, autonomy, handoff and stable guidance remain in force. URL Context is reserved for a necessary exact claim on selected official pages, not adjacent browsing.

- Networking: two or three directly relevant official Morgan resources; no separate club/fair/alumni/sponsor inventories or historical-partnership upgrades.
- Research: at most three relevant official candidates; no faculty/lab/grant expansion or inference from existence to openings, funding, RA availability or eligibility.
- Certification: combine exam version/code and standard price into one narrow lookup and two fact bullets with essential qualifications. No bundles, discounts, study resources or exam-format expansion.
- Interview: named employer required, official recruiting sources first; missing exact process details stay unverified rather than reconstructed from community accounts.

Career Exploration, its deterministic evidence registry, evidence.py, Trust, root, Resume, Skill Roadmap and Internship are unchanged from Wave 1. Models, names, tools and relationships are unchanged. Four targeted specialists now have a per-invocation before-tool Search backstop; unrelated callbacks are unchanged. This deliberately adds four callback assignments, rather than claiming that every callback is unchanged. Internship was secondary and not modified because the primary current paths must first pass with adequate capacity.

### Helper change attribution

The first Certification trial completed in 37.34 s with one helper and eight reported queries, but the helper expanded into retake/study bundles, discounts and exam format. All exposed source titles were third-party sites despite the parent official-source query, and the final answer asserted official prices/versions with a direct link absent from the returned evidence. This was a reliability failure, not a successful optimized answer. The sample remains in career_wave2.json and is excluded as a factual-quality success.

Only then was the Certification Search-helper instruction appended with an official-provider-only, narrow requested-fact scope and explicit missing-evidence output. Its parent also received a compact two-fact/source-support output check. No tool relationship or evidence registry was added. Other helpers remained unchanged unless separately documented by measured evidence below.

### Runtime budget backstop

The corrected helper/prompt-only Certification trial still attempted a third Search helper and reached the 180.024 s diagnostic ceiling, exposing 32 queries. The first lookup supported version but not price; the agent failed to stop with a qualified partial answer. This demonstrated that prompt-only bounding was insufficient. A small before-tool callback now blocks a third actual Search-helper execution for each targeted specialist/invocation. The default one-call rule and second-call justification remain prompt-directed. It does not cap provider-internal queries or model waiting, verify factual evidence, or guarantee that the model never requests a denied call.

The guard uses temporary per-invocation/per-specialist state, has no global student counter, and leaves non-Search tools untouched. A network-blocked ADK integration exercised eight attempted calls across two turns: four helpers executed, four were blocked, and the next turn reset correctly. A second offline ADK check used four simultaneous calls per turn and likewise allowed only two actual executions with correct next-turn reset. Four offline behavior tests cover cap, reset, isolation and non-Search preservation.

### Method and comparability

Used the existing sanitized local observer, pinned SDK 1.165.1 / ADK 2.12.0, fresh in-memory sessions and unchanged root routing. The Wave 2 driver requires exactly one live case at a time. Current cases were run in Certification, Networking, Research, Microsoft Interview order, with saved outcomes reviewed before moving on. An instruction revision requires a separate artifact/source manifest; previous attempts are retained.

The 180-second ceiling is diagnostic censoring, not an application timeout or SLA. Any 429 blocks the affected sample and is not a prompt-design failure. No automatic retries were added. Zero query counts on failed/censored requests mean no query metadata was returned; they are not proof of zero provider retrieval work. Two-minute pauses followed the guarded Certification and root Interview 429s; neither current path was retried. All current factual assessments below concern evidence exposed by the run, not independent confirmation of prices, programs or employer process details.

Baseline attribution matters: Research current was eight helpers / 86 queries in the 226.91 s request; 11 / 96 were aggregate actual-Research totals across baseline cases. Interview Google current was four / 35 with a cutoff; six / 36 were aggregate totals. New Research wording omits the old graduate-opportunity category, and Microsoft differs from the Google baseline. These are scoped triage comparisons, not controlled causal latency estimates. Prior Flask Certification timing is historical context, not a completed local pre/post pair.

### Current before/after

| Specialist | Baseline total (s) | Baseline Search / queries / URL | Wave 2 total / status | Wave 2 Search / queries / URL | First public text (s) | Reliability verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Certification & Technical Development | Prior Flask ~165.12; local 91.94 failed | 3 / 4 / 0 | 18.54 / failed | 1 / 0 / 0 | not observed | CAPACITY BLOCKED: Final guarded source hit 429 inside first Search helper; no final answer or grounded queries. Not a completed latency, query-reduction or reliability result; no further current Certification attempt. |
| Networking & Professional Communication | 160.70 | 6 / 59 / 0 | 47.53 / completed | 1 / 10 / 0 | 47.52 | CALL BUDGET PASS / RELIABILITY & SCOPE FAIL: One helper, ten queries, three headline resources, no calendar call; 47.526 s. Helper broadened into historical clubs/sponsors/programs and mixed sources. Final has no source URLs and asserts active Google in Residence weekly access, more than 15 corporate sponsors and current named employer events without current claim-level evidence. Schedule caveats do not verify those active/access/partnership claims. Needs selective deterministic evidence enforcement; facts are unsupported within this run, not independently disproven. Three headline candidates were followed by adjacent event/resource details; candidate scope is still soft. |
| Research & Graduate Pathways | 226.91 | 8 / 86 / 0 | 180.03 / timeout_censored | 1 / 0 / 0 | not observed | WAIT CENSORED / QUALITY UNKNOWN: One targeted non-calendar Search helper; parent-to-helper request scoped to Morgan cybersecurity research. First helper waited about 165.08 s without returning before 180 s ceiling. No repeated discovery, no grounded metadata, no final answer, no 429. Candidate count, authoritative source use and availability/funding/eligibility assertions cannot be assessed. Zero exposed queries is missing response metadata, not a proven query reduction. |
| Interview Preparation | >=240 cutoff (Google) | 4 / 35 / 0 | 9.07 / failed | 0 / 0 / 0 | not observed | ROOT CAPACITY BLOCKED / UNASSESSED: 429 at root before first transfer, specialist or helper. No current Microsoft process answer, no retrieval behavior or quality can be assessed; not a completed latency or query reduction. No retry. |

### Individual attempts and helper durations

Certification baseline counts in the comparison row refer to the failed local attempt (3 helpers / 4 queries / 0 URL); the historical ~165 s Flask observation used 4 helpers, with query count unavailable here. Durations on incomplete helper spans are elapsed waits until abort, not completed retrieval times.

| Dataset / case | First specialist | Search / queries / URL | Helper durations (s) | First text | Total / status | Final answer | Capacity error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| career_wave2.json / wave2_certification_current | `certification__technical_development_agent` | 1 / 8 / 0 | search #1 15.66 | 37.33 | 37.34 / completed | True | False |
| career_wave2_followup.json / wave2_certification_current | `certification__technical_development_agent` | 3 / 32 / 0 | search #1 50.42; search #2 33.93; search #3 17.98 incomplete | not observed | 180.02 / timeout_censored | False | False |
| career_wave2_guarded.json / wave2_certification_current | `certification__technical_development_agent` | 1 / 0 / 0 | search #1 4.45 incomplete | not observed | 18.54 / failed | False | True |
| career_wave2_guarded.json / wave2_networking_current | `networking__professional_communication_agent` | 1 / 10 / 0 | search #1 25.68 | 47.52 | 47.53 / completed | True | False |
| career_wave2_guarded.json / wave2_research_current | `research__graduate_pathways_agent` | 1 / 0 / 0 | search #1 165.08 incomplete | not observed | 180.03 / timeout_censored | False | False |
| career_wave2_guarded.json / wave2_interview_current | `None` | 0 / 0 / 0 | none | not observed | 9.07 / failed | False | True |
| career_wave2_guarded.json / wave2_certification_stable | `certification__technical_development_agent` | 0 / 0 / 0 | none | 103.38 | 103.38 / completed | True | False |
| career_wave2_guarded.json / wave2_networking_stable | `networking__professional_communication_agent` | 0 / 0 / 0 | none | 20.31 | 20.31 / completed | True | False |
| career_wave2_guarded.json / wave2_research_stable | `research__graduate_pathways_agent` | 0 / 0 / 0 | none | not observed | 12.32 / failed | False | True |
| career_wave2_guarded.json / wave2_interview_stable | `interview_preparation_agent` | 1 / 13 / 0 | search #1 86.75 | 115.05 | 115.05 / completed | True | False |
| career_wave2_final.json / wave2_interview_stable | `interview_preparation_agent` | 0 / 0 / 0 | none | 27.75 | 27.75 / completed | True | False |

**career_wave2.json / wave2_certification_current retrieval scope:**
- Tool #2 search: site:comptia.org "Security+" "exam code" OR "exam version" OR price.
Exposed source titles: hackerdna.com, certempire.com, cybertrainingguide.org, coursera.org, unihackers.com, epicdetect.io, totalcyber.com, figigexams.com.
Review: One helper / eight queries completed quickly, but all exposed sources were third-party, the helper expanded into bundles/discounts/format, and final asserted official facts with an unsupported constructed direct URL.

**career_wave2_followup.json / wave2_certification_current retrieval scope:**
- Tool #2 search: CompTIA Security+ current exam code version price site:comptia.org.
- Tool #3 search: CompTIA Security+ SY0-701 exam price site:comptia.org.
- Tool #4 search: CompTIA Security+ SY0-701 exam retail price US.
Exposed source titles: comptia.org.
Review: Corrected helper returned official version support but no official price evidence; parent searched twice more, attempted a third helper, and hit 180 s. Thirty-two reported queries despite narrow helper instructions; no capacity error. This led to the runtime backstop.

**career_wave2_guarded.json / wave2_certification_current retrieval scope:**
- Tool #2 search: CompTIA Security+ official exam code version price site:comptia.org.
Exposed source titles: none.
Review: Final guarded source hit 429 inside first Search helper; no final answer or grounded queries. Not a completed latency, query-reduction or reliability result; no further current Certification attempt.

**career_wave2_guarded.json / wave2_networking_current retrieval scope:**
- Tool #2 search: Morgan State University Computer Science student organizations clubs networking.
Exposed source titles: morgan.edu, researchgate.net, instagram.com, bowiestate.edu, nsf.gov.
Review: One helper, ten queries, three headline resources, no calendar call; 47.526 s. Helper broadened into historical clubs/sponsors/programs and mixed sources. Final has no source URLs and asserts active Google in Residence weekly access, more than 15 corporate sponsors and current named employer events without current claim-level evidence. Schedule caveats do not verify those active/access/partnership claims. Needs selective deterministic evidence enforcement; facts are unsupported within this run, not independently disproven. Three headline candidates were followed by adjacent event/resource details; candidate scope is still soft.

**career_wave2_guarded.json / wave2_research_current retrieval scope:**
- Tool #2 search: "cybersecurity" research center lab faculty "Morgan State University" computer science.
Exposed source titles: none.
Review: One targeted non-calendar Search helper; parent-to-helper request scoped to Morgan cybersecurity research. First helper waited about 165.08 s without returning before 180 s ceiling. No repeated discovery, no grounded metadata, no final answer, no 429. Candidate count, authoritative source use and availability/funding/eligibility assertions cannot be assessed. Zero exposed queries is missing response metadata, not a proven query reduction.

**career_wave2_guarded.json / wave2_interview_current retrieval scope:**
Exposed source titles: none.
Review: 429 at root before first transfer, specialist or helper. No current Microsoft process answer, no retrieval behavior or quality can be assessed; not a completed latency or query reduction. No retry.

### Stable regression checks

A first Interview stable regression sample unexpectedly made one unnecessary Search call (13 queries, 86.74 s helper wait, 115.05 s total). It is retained in career_wave2_guarded.json. Only the appended Interview section then gained an explicit stable-preparation priority gate: ordinary technical strategies, mock practice and answer feedback must not retrieve to align with SANS/NIST/CompTIA or add examples. The corrected sample is stored separately in career_wave2_final.json; the blocked current Microsoft case was not retried.

Baseline stable timings: Certification 16.22-20.26 s; Networking 16.95-18.02 s; Interview 18.47-23.88 s; explicit Research readiness 18.73-29.40 s (Wave 1 degree-choice 23.65-31.84 s is a different prompt/route mix).

| Specialist | Prompt / target | Total (s) | Search / URL | Final answer | Verdict |
| --- | --- | --- | --- | --- | --- |
| Certification & Technical Development | How should I decide whether a cybersecurity certification is worth pursuing? / `certification__technical_development_agent` | 103.38 | 0 / 0 | True | ZERO-TOOL PASS / QUALITY FAIL / LATENCY OUTLIER |
| Networking & Professional Communication | How should I introduce myself to a cybersecurity recruiter? / `networking__professional_communication_agent` | 20.31 | 0 / 0 | True | ZERO-TOOL PASS / TEMPLATE QUALITY CAVEATS |
| Research & Graduate Pathways | What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs. / `research__graduate_pathways_agent` | 12.32 | 0 / 0 | False | CAPACITY BLOCKED / REGRESSION UNCONFIRMED |
| Interview Preparation | Give me a technical interview preparation strategy for an entry-level cybersecurity role. / `interview_preparation_agent` | 27.75 | 0 / 0 | True | ZERO-TOOL PASS / REGRESSION CORRECTED |

Research stable uses the explicit readiness canary to avoid degree-choice routing overlap. These single regression samples check retrieval/answer preservation, not latency distributions. Exact Wave 1 instruction strings remain intact, including the Internship, Resume and Roadmap stable gates.

### Stable quality notes

wave2_certification_stable: Completed useful decision framework with Search=URL=0, but specialist model wait was 95.024 s and total 103.381 s versus baseline 16.22-20.26 s. Repeated unsupported 40-50 percent academic-discount and .edu eligibility claims plus exact certification eligibility assertions. Similar stable vendor leakage existed in baseline; zero retrieval is not a factual-quality pass. No model/tool loop occurred. One sample cannot isolate provider variance versus prompt effects; stable performance is not validated as unchanged.
wave2_networking_stable: Completed useful recruiter-introduction templates with Search=URL=0 in 20.312 s versus baseline 16.95-18.02 s. Residual quality issues: LinkedIn 300-character limit is an unverified platform-specific rule; a template asserts TryHackMe/home-lab experience not supplied by the student. These are not verified facts or student history. Stable coaching output needs separate tightening without adding retrieval.
wave2_research_stable: Reached Research, then specialist model returned 429 before any helper or final answer. Search=URL=0 is an attempted count, not a completed stable fast-path pass. Wave 1 instruction hash is unchanged, but online regression remains unconfirmed; no retry.
wave2_interview_stable: Corrected Interview stable sample completed a useful general technical strategy, exercises and role/timeline follow-up with Search=URL=0; total 27.751 s versus the failed Wave 2 stable sample 115.051 s with one unnecessary helper, and original baseline 18.47-23.88 s. Advice is framed as general patterns, not a verified current employer process. This one completed sample restores the observed zero-tool behavior; it is not a latency-distribution guarantee.

### Instruction hashes and protected configuration

SHA-256 of decoded UTF-8 instruction strings, compared to Wave 2 entry (the Wave 1 source):

| Component changed | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| `interview_preparation_agent` | `a052c0fda4911f7e0b582211f39ac9d68d425d2e673b2879fa60ed6814bfb23d` | `91cf20eb8e454ccdedb2ec31431bc57917b524ccbeef5ffa3cc5ab368198097d` |
| `networking__professional_communication_agent` | `48549344e1447a191c4d307b75b2a7fa31411fb524797fa2ee761f4b5fe74f4d` | `435792397364594f2e6266061e7a1dbfac28dd330d331241824f4762bb1d8df0` |
| `research__graduate_pathways_agent` | `886466acad54d0cf724d13977794e0d4768dabc375931e0da332fbf42cb63972` | `12586cf414dd589ebb49aea819ba01528dcb69f8d7e4174ef6be6dd120f4caf5` |
| `certification___technical_development_agent_google_search_agent` | `e5187af1a513f3a657ca629cb455bc181039b46c4f546da659c2f8a8502a9071` | `8d503a751c45be82843d8c9124fd8127a9280c577e274474c5efc1841e6a0865` |
| `certification__technical_development_agent` | `20cda283612c674bf750a0ee887b6ecf0b0ccebdc6628aebaa6c8a0c0312086d` | `8338507c63a19415c66ee4ecb34c8759b2d09e4638a68aff912b6e59558bc1b2` |

25 untouched component hashes match Wave 2 entry. Offline parity tests remove the declared Wave 1/Wave 2 instruction appends, new guard function and four targeted callback assignments to recover the original checkpoint AST: names, models, tools, relationships and unrelated callbacks/configuration match after excluding the explicitly authorized four budget callbacks. Career, Trust and root remain unchanged; evidence.py is byte-identical. The complete manifest is tests/diagnostics/career_wave2_parity.json.

### Findings, remaining priorities and validation

Final per-specialist findings and validation are recorded below after all cases are reviewed. No deployment, Agent Engine operation, production inference, commit or push occurred.
### Final Wave 2 assessment

**Not an end-to-end pass and not ready for deployment review as a successful optimization.** The actual Search execution ceiling is implemented and verified offline, but current factual answer reliability and availability remain unresolved. Final current cases include one completed Networking response with reliability/scope failures, one Research wait cutoff, and Certification/Interview capacity failures. No completed reliable current answer is established for all four targets.

- **Networking:** observed 6 to 1 helper (5 fewer), 59 to 10 reported queries (49 fewer), and 160.70 to 47.53 s (113.17 s lower) on the same prompt. This is one sample, not an SLA or causal percentile estimate. It still asserted active partnerships, weekly access and named employer activity without final citations/current claim-level verification. The resource/candidate and factual-output scopes remain soft.
- **Certification:** the fast 37.34 s preliminary answer failed source/scope checks; the corrected helper/prompt-only sample still made a third discovery call and timed out at 180.02 s. The final guarded current sample hit 429 after 18.54 s inside its first helper and must not be presented as a speedup. Official price remains unverified. This explains why helper bounding alone does not resolve the prior ~165 s concern: overlapping retrieval, internal query breadth, model waiting and provider capacity are separate factors.
- **Research:** one current helper waited about 165.08 s before the 180.03 s cutoff. No repeated discovery or calendar lookup occurred, but no answer or grounding metadata returned. Neither three-candidate compliance nor factual reliability can be rated. Zero exposed queries is not a proven reduction. The stable readiness sample also hit 429; do not count its zero tools as a completed fast-path pass.
- **Interview:** the current Microsoft request failed with 429 at the root, before specialist dispatch. Its 9.07 s failure is not Interview execution latency. The first stable sample regressed to one unnecessary Search; the added stable-priority gate corrected the observed behavior in the separate 27.75 s zero-tool repeat. The original regression remains retained. No current case was retried after its capacity error.
- **Internship:** intentionally untouched and not tested in Wave 2. The required primary-path success/capacity condition for the secondary target was not met.

**Stable regression result:** three selected stable cases completed with Search=URL=0 (Certification 103.38 s, Networking 20.31 s, corrected Interview 27.75 s); Research was capacity-blocked before final output. Exact Wave 1 gates are preserved, but online stable regression is not fully confirmed. Certification showed a 95.02 s specialist-model wait and unsupported discount/eligibility claims; Networking had unverified platform-rule and template-history details. Do not hide these quality and latency caveats behind a zero-tool label. Remove unsupported optional specifics in a future scoped output-boundary change rather than adding retrieval to conceptual guidance.

**Remaining P0 paths:** Certification (facts, waiting and capacity), Networking (active/access/partnership evidence), Research (single-helper wait plus prior institutional/funding reliability gaps), and provisional Interview (current completion/quality unassessed). Trust remains an untouched baseline P0. Root/provider capacity is a cross-workflow availability issue, not evidence that prompts or routing should be rewritten.

**Evidence enforcement next:** Networking and Certification now have direct observed reasons for selective deterministic claim/source/status transport and final-output checks. Research also warrants this based on the preserved baseline funding/eligibility/currentness defects, although the new current answer never completed. Require a healthy completed Interview current sample before deciding its enforcement design. Use the smallest domain-appropriate mechanism; do not copy the Morgan-resource whitelist/renderer into unrelated domains.

**Guard limitations:** the runtime callback guarantees at most two actual Search-helper executions per targeted specialist/invocation in the tested ADK contract. The default one-call choice and second-call exception remain model-directed. This guard does not cap underlying grounding queries, total model requests/waiting, or URL Context; it does not validate sources or force a reliable final answer. Serial and parallel offline ADK checks verified execution denial and turn reset; the final Certification live attempt failed before this limit could be exercised.

### Final validation and repository scope

- Tests passed: 12 evidence, 11 configuration, 7 existing diagnostic, 4 Wave 1/Wave 2 parity and 4 Search-budget behavior checks: **38 total**. Two additional network-blocked ADK integrations passed (serial and parallel calls across two turns). Final root/AdkApp import and syntax checks passed.
- Five instruction hashes changed relative to Wave 2 entry: four primary specialists and only the measured-problem Certification Search helper. Four targeted before-tool callbacks and the small guard function were added. All other instruction hashes, models, names, tools, relationships and unrelated callbacks match. Original Wave 1 instruction strings remain exact; Career, root, Trust and evidence.py are untouched.
- The report prefix and all six baseline/Wave 1 JSON artifacts retain their entry SHA-256 hashes. All failed, censored, superseded and corrected Wave 2 samples remain available with separate source manifests and manual review notes.
- Runtime source edit: agents/career/workflow/agent.py. Diagnostic edits: career_baseline.py gains an optional case-plan argument with unchanged default behavior; README documents the Wave 2 driver and guard. New diagnostic files: career_wave2.py, test_career_wave2_parity.py, test_career_search_budget.py, career_wave2_parity.json, and four Wave 2 result JSON artifacts. No dependency changes.
- Final whitespace, privacy, source-manifest, scope and Git checks are recorded below after validation. No backend/frontend edits, deployment, Agent Engine create/update/delete, production inference, commit or push occurred.

Wave 2 sample accounting: 11 saved attempts; 6 completed responses (including retained quality failures), 2 diagnostic cutoffs, 3 capacity-affected attempts. Three superseded observations are not final acceptance cases.

Final checks passed: git diff --check; whitespace checks on all intended untracked files; final instruction/source hashes; original report prefix and all baseline/Wave 1 JSON hashes; artifact JSON/privacy scans; Python syntax; branch/HEAD/index and file scope. Only tracked edit is agent.py; all other task files are the intentional diagnostic/report infrastructure. Nothing staged, committed, pushed or deployed.

Retained superseded Interview stable verdict: STABLE RETRIEVAL REGRESSION (115.051 s, one Search helper, 13 queries). Corrected final stable repeat: 27.751 s, zero Search and URL Context. The superseded completed response is not a zero-tool pass.


## Wave 3 — Evidence Enforcement and Runtime-Wait Diagnosis

### Scope and outcome

Wave 3 is implemented locally. Track A enforces bounded evidence transport and final status rendering for Networking, Certification and Research. Track B measures SDK/provider/runtime waiting in the diagnostic harness only. They establish different results: safer abstention is not a completed current-fact answer, and a faster sample is not proof of reduced model computation or deployment readiness.

Ten fresh-session canaries completed, with no failed/censored attempts and no 429. All first transfers matched the intended specialist. No retries, parallel live requests, Agent Engine calls, cloud deployment, production inference, commit or push occurred. The engine configuration, models, agent names/sub-agent relationships, backend, frontend, root, Trust, Interview and Career Exploration remain unchanged from Wave 3 entry. Previous Wave 1/Wave 2 instruction prefixes and all earlier artifacts remain exact.

### Track A: shared infrastructure and boundaries

`evidence.py` was NOT edited or generalized in place. `shared_evidence.py` reuses its frozen `EvidenceCandidate`, parser, `CandidateRegistry`, exact claim/URL handoff, copy-on-write state updates and invocation reset through a small `NamespaceState` adapter. No three-domain copies of the registry were created. Career retains its original tools, callbacks, renderer and `temp:career_evidence_*` state keys.

New ADK temporary state keys are `temp:evidence:networking:*`, `temp:evidence:certification:*`, and `temp:evidence:research:*`, with `candidates`, `verifications`, `control` and `handoffs` in each. Reset affects only that namespace on a new invocation, including reused sessions. No user/session global registry or cross-specialist state is used.

- Each target has one actual discovery execution per invocation; parallel/repeated calls cannot exceed it. Networking/Research allow three frozen candidates and two verification attempts. Certification allows one candidate and one attempt. Invalid/repeated IDs consume the same finite attempt budget. Discovery protocol/schema failure closes safely without a research retry.
- Public verification schemas accept only candidate IDs. Python sends the exact stored claim and URL to the existing URL Context helper; the parent cannot override either. The narrow Certification pipeline binds its frozen claim to the original requested question at registration so a candidate cannot silently widen the requested fact scope. The resulting stored claim is transported unchanged. Original source URLs, including grounding redirects and escaped paths, are not regenerated.
- Three specialists and their six existing helper agents receive append-only transport instructions. Existing instructions are retained verbatim; models and helper agents are retained. The targets use new tool wrappers plus before-agent, before-model and after-model callbacks; the existing Wave 2 before-tool Search ceiling remains. Root orchestration and all sub-agent relationships are preserved.
- Before-model callbacks force the bounded next step or return a deterministic factual response. After-model callbacks remove premature public factual prose alongside tool calls and prevent final specialist rewrites/status upgrades. Stable coaching has retrieval tools removed; stable Certification decision questions receive a generic Python-rendered decision framework after the observed model call. This suppresses discount/eligibility leakage without hiding the specialist wait or shortening its prompt.
- Verification uses a strict JSON record. Valid statuses are VERIFIED CURRENT / CURRENT STATUS UNVERIFIED / HISTORICAL / UNSUPPORTED. Python rejects malformed records and downgrades unsupported VERIFIED CURRENT results when explicit page-read/current evidence, an official matching publisher, or a non-copyright date/cycle is missing. Other valid statuses are retained; parent text cannot upgrade them. Certification displays only requested, narrowly validated fact fields, excluding unrelated discount/eligibility/vendor-offer fields.
- Final factual sections contain selected verification records only, with exact inspected source links and unchanged enforced statuses. Unselected candidates are omitted. Networking/Research proposed claims are explicitly labeled as proposals, not assertions; unverified records do not display supported-scope assertions. Certification never renders arbitrary helper narrative as its answer.

This is deterministic transport/budget/status enforcement, **not an independent truth oracle**. Page reading, semantic assessment, authority attribution for preserved grounding redirects and discovery quality still depend on helpers/provider tools. Claim-level scope and content need broader adversarial evaluation. Official ownership/date gates are deliberately conservative; they can abstain on valid undated material. No current version, price, opening, funding or eligibility is certified by this report.

### Local canaries: exact counts and quality

Search counts below are actual helper executions; queries are provider-reported grounding queries inside those calls. Verification counts are actual URL Context helper invocations. A bounded helper can still issue multiple internal grounding queries. All rows completed without errors; zero verification for Certification means no candidate was available, not that verification was unnecessary.

| Case | Seconds | Search | Queries | Candidates | Verification | Assessment |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| certification_stable_1 | 25.623 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| certification_stable_2 | 22.897 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| certification_stable_3 | 22.138 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| interview_stable | 25.183 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| certification_current | 33.173 | 1 | 5 | 0 | 0 | SAFE_ABSTENTION; requested version/price NOT answered |
| networking_stable | 18.806 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| networking_current | 82.547 | 1 | 5 | 3 | 2 | BOUNDED_STATUS_PRESERVATION_PASS; no verified current resource established |
| research_stable | 24.031 | 0 | 0 | — | 0 | STABLE ZERO-RETRIEVAL PASS |
| research_current | 78.160 | 1 | 6 | 3 | 2 | BOUNDED_STATUS_PRESERVATION_PASS; no current opening/funding/eligibility established |
| interview_current | 96.547 | 2 | 21 | — | 0 | COMPLETED; CURRENT RELIABILITY FAIL |

**Networking:** the selected C1 partnership claim returned UNSUPPORTED: the cited “over 15 companies” text described an organizational goal, not an established active partnership. C3 returned CURRENT STATUS UNVERIFIED: older conference material did not prove current club activity/access or the proposed club naming. Those statuses were preserved and unselected C2 was omitted. No current partnership/access claim was promoted. This is an observed enforcement pass with unresolved current-resource availability, not proof that no resources exist.

**Certification stable:** all three fresh samples had zero Search/URL and the final generic framework contained no current discount, voucher-price, .edu eligibility, vendor-offer or employer-ranking assertions. This addresses the observed final-output leakage; it does not establish that the raw model itself has stopped producing optional unsupported specifics.

**Certification current:** one Search-enabled model response reported five queries and returned NO CANDIDATES. Final output stated CURRENT STATUS UNVERIFIED with no version/price assertion. Budgets and safe abstention passed, but the requested facts were NOT answered and the live verification path was not exercised here. The transport/current-fact rendering path is covered offline; this is not a current-fact completion pass. Discovery availability remains P0.

**Research:** C1 was reported VERIFIED CURRENT by its helper but lacked dated current evidence, so Python downgraded it to CURRENT STATUS UNVERIFIED. C2 also remained CURRENT STATUS UNVERIFIED because the inspected release described a one-year project without establishing activity beyond its term. Both final statuses were preserved. Current openings, funding, applications and student eligibility were not established; no inferred positive opening/funding assertion was rendered. Stable research-readiness completed with zero retrieval.

**Interview:** stable strategy remained useful and tool-free at 25.183 seconds. The healthy Microsoft current sample exercised two Search helpers (21 queries) and no URL verification. Final output labeled employer-specific process details “verified” without exact claim-level citations; helper output mixed Microsoft sources with third-party interview sites and candidate reports. This is a current reliability failure/remaining P0, not independent proof that each asserted detail is false. Interview was not changed in Wave 3. The prior root 429 was not reproduced and must not be retrospectively reclassified as an Interview regression.

### Before/after reliability and latency

| Path | Earlier observation | Wave 3 observation | Interpretation |
| --- | --- | --- | --- |
| Networking current | Baseline 160.696s, 6 Search/59 queries; Wave 2 47.526s, 1/10 with unsupported active/access assertions | 82.547s, 1 Search/5 queries, 2 verifications; selected claims unsupported/unverified | Stronger output enforcement costs extra verification time; slower than Wave 2, faster than baseline; no verified current-resource list established |
| Certification stable | Wave 2 103.381s, zero retrieval, unsupported discount/.edu eligibility claims | 25.623 / 22.897 / 22.138s, zero retrieval, generic constrained final answer | Leakage addressed by final-output boundary; 103s not reproduced in three fresh sessions; no causal speedup claim |
| Certification current | Previous Flask ~165.117s; prompt-only Wave 2 cutoff; guarded sample 18.544s TOOL_CAPACITY | 33.173s, 1 Search/5 queries, zero candidates/verifications, safe abstention | Capacity failure did not recur; requested facts still unavailable; not a complete-success speedup |
| Research current | Baseline 226.914s, 8 Search/86 queries; Wave 2 180.028s cutoff, single helper waiting ~165.084s | 78.160s, 1 Search/6 queries, 2 verifications; both current statuses unverified | Prior single-helper stall not reproduced; bounded completed output avoids inferred active opportunities; availability/current evidence unresolved |
| Research stable | Wave 1 readiness path tool-free; Wave 2 stable hit specialist 429 | 24.031s, zero retrieval | Fresh stable path completed; does not erase retained capacity failure |
| Interview stable | Corrected Wave 2 27.751s, zero retrieval | 25.183s, zero retrieval | Stable gate preserved; single-sample variance |
| Interview current | Wave 2 Microsoft 9.068s root 429 before dispatch | 96.547s, 2 Search/21 queries, zero verification, reliability failure | Earlier failure was root/provider capacity, not specialist execution latency; healthy current output now reveals separate evidence risk |

### Track B: timing method and phase attribution

All timing instrumentation remains under `tests/diagnostics/`. The observer records request start, first root event, first transfer, first specialist event/start, helper starts/completions, specialist before-model resumptions, first public text and stream completion. Events and allowlisted tool outputs exclude hidden reasoning, signatures, runtime IDs and credentials. Numeric callback metrics do not serialize raw prompts/history. Saved timeline fields provide the detailed milestones for every run.

`career_wait_analysis.py` uses disjoint interval attribution: helper lifetimes take priority over model spans; root SDK waits are separate; specialist waits after any helper completion are POST_TOOL, including intervals between successive helpers. Stream finalization covers the remaining interval after first public text; uncovered time stays UNOBSERVED_RUNTIME_WAIT. Durations sum to request elapsed time apart from rounding. Specialist “resumes” can be a Python final-render callback with no additional model request. SDK response arrival is measured before downstream tools, so open generator lifetimes do not falsely count tool waiting as model waiting.

These observations cannot isolate pure model computation, provider queuing, network transit or internal tool processing. An unfinished helper at cutoff would be censored as TOOL_PROVIDER_STALL/DIAGNOSTIC_CUTOFF, not a proven 429 or a discovery loop. Error classification distinguishes PROVIDER_CAPACITY cause with ROOT_CAPACITY/SPECIALIST_CAPACITY/TOOL_CAPACITY stage, transport errors, and workflow errors; timing tests cover these cases. No automatic retries were added.

| Case | ROOT_WAIT | SPECIALIST_PRE_TOOL_WAIT | TOOL_WAIT | SPECIALIST_POST_TOOL_WAIT | STREAM_FINALIZATION | UNOBSERVED_RUNTIME_WAIT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| certification_stable_1 | 7.111 | 17.355 | 0.000 | 0.000 | 0.002 | 1.155 |
| certification_stable_2 | 7.233 | 14.530 | 0.000 | 0.000 | 0.001 | 1.133 |
| certification_stable_3 | 6.719 | 14.321 | 0.000 | 0.000 | 0.001 | 1.097 |
| interview_stable | 5.660 | 18.353 | 0.000 | 0.000 | 0.001 | 1.169 |
| certification_current | 6.418 | 6.815 | 18.843 | 0.000 | 0.001 | 1.096 |
| networking_stable | 5.722 | 11.974 | 0.000 | 0.000 | 0.001 | 1.109 |
| networking_current | 7.788 | 8.160 | 60.880 | 4.529 | 0.001 | 1.189 |
| research_stable | 6.278 | 16.615 | 0.000 | 0.000 | 0.002 | 1.136 |
| research_current | 6.647 | 5.688 | 61.341 | 3.277 | 0.001 | 1.206 |
| interview_current | 8.357 | 6.477 | 64.767 | 15.760 | 0.002 | 1.184 |

**Certification distribution:** three completed fresh-session totals were 25.623, 22.897 and 22.138s; median 22.897s, mean 23.553s, range 3.485s and population standard deviation 1.496s. Specialist zero-tool SDK waits were 17.355, 14.530 and 14.321s; root waits were 7.111, 7.233 and 6.719s; unobserved overhead was 1.155, 1.133 and 1.097s. The previous 103.381s result (95.024s specialist wait) is an **observed outlier relative to these three fresh runs**, consistent with run/provider/history variation rather than repeatable 100-second fresh-session latency. The sample cannot distinguish provider variance from the earlier session/history conditions, or prove the new output boundary caused a speedup. No claim that latency is solved is warranted. All current Wave 3 samples use the same unchanged model identifiers; prompts were not compressed.

**Research stall diagnosis:** the earlier Wave 2 ~165-second unfinished helper interval was tool/provider waiting, not eight Search-loop executions. In this wave, discovery's SDK wait was 31.301s, verification waits were 16.460s and 13.565s, and total helper lifetimes were 61.341s. The old 180s cutoff did not recur in this one diagnostic. No retries were used to obtain a completed sample. A single healthy run does not establish stall elimination.

**Capacity:** all ten Wave 3 attempts completed with no 429, provider-capacity, transport or workflow errors and no cutoffs. Earlier Wave 2 ROOT/SPECIALIST/TOOL capacity failures remain retained in their original artifacts. There was no pause/retry after 429 in Wave 3 because none occurred. The three Certification samples were not curtailed, and the conditional Microsoft test followed a healthy stable Interview and healthy preceding cases.

### Prompt size and history measurements

Authored sizes below include the append-only Wave 3 transport boundary where applicable. Effective instruction counts are measured at the diagnostic before-model callback and include ADK-added routing/context, so they are larger than the authored prompt. Configured helper descriptions count authored tools; callback counts include transfer availability before evidence callbacks restrict executable tools. This is not a token count or a count of the final forced function declarations. The root also has nine unchanged sub-agent descriptions in its orchestration context.

| Component | Authored instruction chars | Effective callback instruction chars | Configured helper/tool descriptions | Callback available tools | History messages | Visible text history chars |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interview_preparation_agent | 18,990 | 32,590–32,590 | 2 | 3–3 | 3–7 | 1,275–1,275 |
| networking__professional_communication_agent | 16,371 | 29,954–29,954 | 2 | 3–3 | 3–7 | 1,262–1,284 |
| research__graduate_pathways_agent | 16,599 | 30,193–30,193 | 2 | 3–3 | 3–7 | 1,272–1,317 |
| certification__technical_development_agent | 14,574 | 28,159–28,159 | 2 | 3–3 | 3–3 | 1,262–1,277 |
| root_agent | 8,037 | 21,486–21,486 | 2 | 3–3 | 1–1 | 59–125 |

Each canary starts with a new in-memory session and one user message. Subsequent specialist requests include transfer/context and tool results; history counts reflect that growth rather than a prior student conversation. Counts exclude hidden reasoning text. No safe local tokenizer was installed (`tiktoken`, `sentencepiece`, `tokenizers` absent), so approximate token counts are unavailable; no package/model download or token-count API was used. Instruction sizes alone do not demonstrate a latency correlation: only three repeated Certification samples and one current sample per domain were measured. No prompts were shortened.

### Remaining P0 and Wave 4 recommendation

- Certification remains P0 for current-fact discovery/completion and unproven long-tail availability. Stable output leakage is bounded for the conceptual decision path, but the full stable-question space needs evaluation.
- Research remains P0 for explicit current opening/funding/access evidence and long-tail helper availability. This wave improved status integrity; it did not establish a current opportunity is open.
- Networking remains P0 pending a broader completed-current-resource evaluation. The observed active-partnership/access leakage is blocked on this canary, but no VERIFIED CURRENT candidate was established and discovery still generated overbroad proposed claims.
- Interview is now an observed current evidence P0: healthy execution exposed unsupported “verified” labeling and mixed-source synthesis. Trust remains the untouched baseline P0. Root/provider availability remains a separate historical risk.

A controlled prompt-compression experiment is justified as a separate Wave 4 investigation because authored prompts are 8–19k characters and effective instructions are roughly 21–33k. These measurements do **not** prove prompt size caused the prior 103s stall. Freeze this evidence boundary, compare instruction-preserving variants using repeated fresh stable/current canaries, and retain hard budgets/status transport. First improve narrow official Certification discovery and explicit claim coverage; evaluate an Interview evidence boundary based on this healthy current observation. Profile provider variance separately, including controlled history size. Do not globally shorten prompts, add retries, broaden Search, change runtime/model settings, or deploy on the basis of these ten samples.

### Files, preservation and validation

Wave 3 edits: `agents/career/workflow/agent.py` (three specialist wrappers/callbacks, nine append-only protocols), `agents/career/workflow/OPTIMIZATION_REPORT.md` (this appended section), `tests/diagnostics/career_baseline.py` (numeric metrics and generic verification observation), `tests/diagnostics/test_career_wave2_parity.py` (strict normalization of declared Wave 3 additions before existing comparisons), and `tests/diagnostics/README.md` (usage/method). New files: `agents/career/workflow/shared_evidence.py`, `tests/diagnostics/career_wave3.py`, `career_wait_analysis.py`, `test_career_shared_evidence.py`, `test_career_wave3.py`, `career_wave3.json`, and `career_wave3_parity.json`.

No dependency files changed and no packages were installed. `career_wave3_parity.json` stores all 30 entry/effective instruction hashes, declared changed components, source hashes and entry hashes of protected workflow files, previous JSON artifacts and the original report prefix. Nine appended instruction expressions changed; the other 21 are exact. Every previous instruction prefix remains exact. Protected legacy `evidence.py` and the existing Career assignment/behavior are unchanged. The previous parity checks reconstruct the checkpoint AST after stripping only declared Wave 1/Wave 2/Wave 3 additions, proving models, names, relationships and unrelated configuration unchanged.

Offline tests: **59 passed**: 12 existing Career evidence tests, 14 new shared-evidence tests (including actual ADK Runner and concurrent discovery budget tests), 11 engine-configuration, 7 baseline diagnostic, 4 Wave 1/Wave 2 parity, 4 Search-budget and 7 Wave 3 timing/preservation tests. Shared tests cover namespaces, candidate/verification caps, invalid IDs, exact source/claim transport, all four statuses, fail-closed currentness, restricted Certification fields, stable tool removal, final-output rewrite prevention, invocation reset and legacy preservation. The actual offline Runner uses fake model responses, not a cloud request. Python syntax/root loading, protected hashes, artifact privacy, source manifests, report-prefix preservation, whitespace and Git checks are verified at finalization below.

No backend/frontend file, engine configuration or deployment helper changed. No Source Dev v5 or other Agent Engine was created/updated/deleted; production Reasoning Engine 3463694723959488512 remains untouched. Nothing is staged, committed or pushed. The prior baseline/Wave 1/Wave 2 untracked diagnostic/report infrastructure remains in place and is not silently included in a new commit.

Final Wave 3 checks passed: 59 offline tests; all 30 runtime-loaded instruction digests; root/toolset importability; Python syntax; unchanged protected workflow files, earlier JSON artifacts and report prefix; ten completed source-matched canaries with matching routes; disjoint phase sums; JSON privacy scan; git diff --check and whitespace checks on all 25 intended report/diagnostic/shared files including untracked files. The final timing tests were re-run after the distribution-label refinement and passed (7/7). HEAD remains beeb3a87ad2f8892dce9e30f376bd2768b65c239 on feature/career-agent-runtime-integration and the index is empty. Only tracked edit is agent.py; the new shared module and intentional reports/diagnostics remain untracked. No deployment, commit or push occurred.


## Wave 4 — Current-Fact Reliability Completion

### Outcome and validation boundary

Wave 4 reliability mechanisms are implemented locally, but **Wave 4 has NOT passed the full live acceptance matrix and is not ready for deployment**. Four live Certification attempts were retained: one partial grounded current answer, one stable completion, one root-wait diagnostic cutoff and one Search-helper 429. All further live testing stopped after that 429. No failed ID was retried. Interview, Trust A/B/C and Networking/Research/Career live regressions are deferred, not counted as completed live passes.

The completed current answer now verifies requested exam version/code fields from an inspected official page and explicitly leaves price unverified. It does not establish an official current price. Improved partial usefulness is separate from full fact completion, availability and latency. Offline ADK tests validate the new pipelines using synthetic evidence; they do not certify real-world facts or provider behavior.

### Certification discovery diagnosis

The exact retained Wave 3 Search helper output was `NO CANDIDATES`. Its grounded model span exposed five queries and **zero source URLs/grounding chunks**. The discovery tool returned an empty candidate list without its malformed-record error. Therefore the observed boundary was an explicit empty helper response, **not a structured-output parsing failure or rejected registered candidate**. No official CompTIA page was visible in that sample's grounding metadata; it is not possible to prove the provider had returned an official page internally and the parser discarded it.

Contributing contract restrictions were identified in source: Certification allowed only one candidate/one verification for a two-fact request, bound every candidate claim to the entire original question, and the preceding narrow-lookup instructions banned voucher-related discovery even though an official exam purchase page may use that product term. These are contract risks, not a proven sole causal explanation for absent provider sources. Grounding queries also failed to retain the requested official-domain restrictions. Provider-internal query rewriting remains outside the Python helper-execution budget.

The append-only Wave 4 override now requests the official exam/version page and official vendor store/list-price page separately, allowing up to two partial candidates and two checks within one discovery helper. It permits the standard exam-only purchase product as a pricing source, without adding voucher advice, discounts, bundles, retakes, salary, training providers or employer preferences to the answer. Only the requested fact set is researched/rendered. Each registered discovery claim and exact source URL now remain unchanged; no compound-question rewrite is imposed on Certification candidates.

### Shared infrastructure and domain thresholds

The legacy `evidence.py` file remains byte-identical. `CompletionPolicy` extends the existing namespaced adapter and reuses the same `CandidateRegistry`, frozen records, copy-on-write state, invocation reset and exact candidate-ID verification handoff. It does not duplicate registries. Active namespaces are Networking, Research, Certification, Interview and Trust; Career Exploration retains its separate original state keys/behavior. New keys follow `temp:evidence:<namespace>:...`. Every namespace has independent candidates, verification records, budgets and reset behavior.

Current Certification/Interview/Trust progression is deterministic in Python: select discovery, select registered IDs, then render. No specialist SDK synthesis request is needed between helper calls or to rewrite final statuses. Stable Certification and Interview still use their preserved model path with retrieval disabled for conceptual coaching. This is a functional evidence boundary, not prompt compression or a model-configuration change. The runtime model identifiers and all root/sub-agent relationships remain unchanged.

**Certification:** maximum one discovery, two candidates and two verification attempts, including invalid attempts. A page may establish one requested fact while another remains unverified. Per-fact statuses and exact inspected quotations are kept separately from the compound candidate's status: an overall partially unsupported candidate does not erase an explicitly verified narrower fact, and its unverified fields cannot inherit another field's verification. Displayed values must literally occur in the inspecting helper's fact evidence. Only requested facts pass the renderer; unrequested launch/retirement/discount details are filtered. Currency/region are displayed only when supported with the same status. Undated live official exam/store content may establish its presently displayed code/list price through explicit inspection; no publication date or future cycle is invented. This domain threshold intentionally differs from Research/Networking dated-currentness rules.

**Interview:** namespace `interview`, one discovery, three candidates, two deterministic checks, official candidates selected first. Python caps anecdotal candidates at one; optional anecdotes do not require a separate broad research sweep. VERIFIED OFFICIAL requires readable exact employer-owned support for the claimed scope; third-party/anecdotal candidates cannot receive that official label. HISTORICAL remains historical. The renderer separates official documentation, candidate reports and unknown/team-dependent details. Reports use “Candidates have reported,” never an official-process assertion. No fixed universal stages or round count are filled from memory. The official/anecdotal enum is restricted to Interview and is rejected in Certification/Trust.

**Trust:** namespace `trust`, one targeted discovery maximum if a concrete disputed claim lacks sources, two source checks maximum. Supplied source URLs are registered directly and compared without preliminary Search. Missing/unnamed program or opportunity information triggers a request for the disputed wording and sources instead of guessing a program and searching broadly. Explicit human-review requests receive immediate escalation guidance without research; no person is contacted and no referral/ticket is claimed to exist.

Trust renders DISPUTED CLAIM, SOURCE A/B authority/date/scope/population/version/support, exact CONFLICT, ASSESSMENT, WHY and NEXT STEP. Current-source agreement may resolve the documented comparison only at matching known scope/date/population/version; authority hierarchy alone cannot choose a winner. Material disagreement remains UNRESOLVED, and different documented scopes can be PARTIALLY RESOLVED without deciding which applies to the student. Historical agreement cannot resolve a current-status dispute. Agreement on a documented eligibility rule cannot itself decide a particular student's qualification. Unknown metadata is treated as missing evidence, not proof of a mismatch. Unresolved consequential eligibility/funding questions direct the student to the responsible official for confirmation.

These mechanisms enforce transport, limits, source-type/status boundaries and final rendering. Helper assessments and publisher attribution for grounding redirects are still model/tool dependent; this is not an independent truth oracle. Successful offline rendering is not evidence that an external employer process, price or opportunity is current.

### Live canary results

| Case | Seconds | Search / reported queries | URL verification | Result |
| --- | ---: | ---: | ---: | --- |
| certification_current_1 | 116.799 | 1 / 8 | 2 | PARTIAL GROUNDED ANSWER |
| certification_stable_1 | 180.025 | 0 / 0 | 0 | DIAGNOSTIC ROOT WAIT CUTOFF |
| certification_stable_2 | 20.591 | 0 / 0 | 0 | STABLE ZERO-RETRIEVAL PASS |
| certification_current_2 | 21.491 | 1 / 0 | 0 | PROVIDER_CAPACITY / TOOL_CAPACITY |

Current sample 1 registered two candidates. The official exam candidate contained both a supported current version/code and unsupported future-version claims. Verification explicitly supported only the version/code; Python omitted the unsupported launch year/new-code assertion and the unrequested retirement date. Its second pricing candidate was a third-party article, so the final answer did not repeat its price or discounts as official facts. The answer displayed VERIFIED CURRENT for the inspected exam version/code fields and CURRENT STATUS UNVERIFIED for price. This is useful grounded partial output under the conditional missing-fact rule, **not proof that official price discovery is solved**. The live verification result and exact inspected URLs are retained in `career_wave4.json`.

Current sample 2 failed with 429 inside its first Search helper after root dispatch: **PROVIDER_CAPACITY / TOOL_CAPACITY**. It produced no final answer or usable grounding/verification result. Its zero exposed queries must not be called a reduction. Live testing stopped after this attempt, including the eight remaining distinct cases; no new output file was used to bypass the stop.

Stable sample 1 reached the 180.025-second diagnostic cutoff before a root response or transfer. Observed root SDK waiting was 179.073 seconds, with no specialist or retrieval work. This is a censored ROOT_WAIT, not a proven 429, pure model-computation measurement, or Certification specialist regression. The second separately planned fresh stable sample completed in 20.591 seconds with zero retrieval and the constrained generic final framework. Neither timeout nor 429 was silently retried.

### Before/after and remaining live assessments

| Path | Wave 3 | Wave 4 assessment |
| --- | --- | --- |
| Certification current | 33.173s, 1 Search/5 queries, no candidate or verification, total abstention | One 116.799s partial grounded answer: 1 Search/8 queries, 2 candidates, 2 checks; version/code supported, price unresolved. Second sample TOOL_CAPACITY. More useful, slower, not complete/availability-passed |
| Certification stable | Three completed zero-tool samples at 25.623/22.897/22.138s | One 180.025s root cutoff and one 20.591s zero-tool completion; no claim of an end-to-end latency fix |
| Interview current | 96.547s, 2 Search/21 queries, unsupported details labeled verified | Deterministic official/anecdotal pipeline implemented; offline real-Runner test passes, live canary deferred after capacity stop |
| Interview stable | 25.183s, zero retrieval | Offline real-Runner stable path passes with zero tools; live stable repeat deferred |
| Trust A/B | Baseline broad speculative conflict research (~100s/~39 queries) | Offline actual Runner: each asks for unnamed program/opportunity, disputed wording and sources; 0 Search/0 checks, UNRESOLVED. No invented program. Live A/B deferred |
| Trust C | Baseline human-escalation path retained | Offline actual Runner: immediate human-review guidance, 0 Search/0 checks. Live C deferred |
| Networking | 82.547s, 1 Search/5 queries, 3 candidates/2 checks, conservative statuses | No path redesign or instruction/config edit. Prior tests plus mocked Runner status checks pass; current live regression deferred |
| Research | 78.160s, 1 Search/6 queries, 3 candidates/2 checks, current status unverified | No path redesign or instruction/config edit. Offline current Runner: 1 Search/2 checks, selected statuses preserved, unselected candidate omitted. Live regression deferred |
| Career Exploration | Original deterministic evidence behavior | Agent/helper instructions, config and legacy evidence file unchanged. All 12 evidence tests and offline stable Runner regression pass. Live stable regression deferred |

Offline synthetic evidence is deliberately distinguished from live provider evidence. Fake prices/codes in tests are not current facts. No mocked latency is reported as a live performance result. Trust A/B are under-specified as written; asking for the program/source pair is the safe bounded adjudication behavior, rather than searching every Morgan cybersecurity program.

### Diagnostic timing

The existing harness records root SDK waiting, specialist pre-tool/post-tool SDK waiting, helper lifetimes, runtime gaps and total time. Python-directed current steps explain zero specialist SDK waits here; these zeros are not evidence of faster specialist model computation. STREAM_FINALIZATION was 0.001–0.002s for completed responses. Intervals are disjoint and sum to total apart from rounding.

| Case | Root wait | Specialist pre-tool | Tool wait | Specialist post-tool | Unobserved runtime |
| --- | ---: | ---: | ---: | ---: | ---: |
| certification_current_1 | 8.056 | 0.000 | 107.697 | 0.000 | 1.045 |
| certification_stable_1 | 179.073 | 0.000 | 0.000 | 0.000 | 0.952 |
| certification_stable_2 | 7.463 | 12.123 | 0.000 | 0.000 | 1.003 |
| certification_current_2 | 9.881 | 0.000 | 10.580 | 0.000 | 1.030 |

Current sample 1's helper SDK waits were 64.911s discovery, 23.489s first inspection and 19.287s second inspection. Helper lifetimes totaled 107.697s. The result is not a latency optimization pass. The stable root timeout reinforces the earlier finding that Search cannot explain all long-tail delay. Provider queuing, network delay and internal model/tool processing are not separately observable. No retries or production instrumentation were added.

### Offline defect found and corrected

A new Trust test demonstrated that two matching HISTORICAL source statements could yield RESOLVED for a current question. The correction requires current evidence for current adjudication and preserves historical status. Additional tests cover personal eligibility, unknown metadata, rejecting Interview-only statuses in other namespaces, and an exact one-anecdote registration cap. These corrections occurred **after live testing stopped**. The original live source hashes remain untouched; final source/method hashes and the post-live changes are recorded separately in the parity manifest. Valid four-status Certification responses and the measured answer were not altered by these corrections. Final Trust/Interview behavior is offline-validated, not live-validated.

The existing Certification test fixture was strengthened to include its mocked code/price literally in the mocked inspected quotation. Its assertions were retained; the change prevents a fixture from claiming evidence it did not contain. Prior tests still pass. Wave 2/Wave 3 parity normalization removes only the declared Wave 4 append/wrapper/callback additions before checking their immutable manifests.

### Wave 5 compression preparation only

No instructions were shortened. All 30 pre-wave instruction strings remain exact prefixes; nine target specialist/helper expressions received appends. Root, Career, Networking and Research instructions/configuration are exact. No engine/model/backend/frontend setting changed.

Measured on the frozen Wave 3 root plus nine specialist instructions: **148,784 authored characters**, with **30,087 redundant character occurrences (20.22%)** in identical repeated paragraphs of at least 80 characters. Of those, **29,829 characters are cross-agent repetitions** and only **258 are exact repeats within individual prompts**. Full paragraph sizes/owners and the calculation are recorded in `career_wave4_compression.json`.

Repeated policy candidates include current-year/cycle gates and date-availability safeguards, Morgan-specific authority rules, exact-source/no-adjacent-fact synthesis, evidence hierarchy, human decision boundaries and output discipline. These belong in reusable shared instruction constants for maintenance, while domain-specific facts, source thresholds, role scope, budgets/status schemas and escalation/adjudication wording remain specialist-specific.

Moving identical rules into constants can remove up to the measured ~30k source-literal duplication **but saves zero rendered prompt characters if every agent still receives the same text**. A conservative directly measured rendered-prompt opportunity is the 258 exact within-instruction repetitions, subject to parity evaluation; broader savings from consolidating semantically overlapping date/authority rules require a controlled Wave 5 experiment and are not yet quantified as guaranteed runtime reduction. Do not equate the 20.22% source-maintenance figure with token savings or latency improvement.

Recommended Wave 5 sequence: keep this evidence boundary fixed; extract common constants without changing rendered strings first; evaluate exact repetition removal and then overlapping date/authority-policy consolidation one component at a time; compare instruction hashes where exact parity is intended and repeat stable/current reliability canaries where actual compression is tested. Retain source hierarchy, exact handoff and Python status/budget enforcement. Do not deploy or infer a latency benefit solely from large prompts. Reliability and healthy current-fact completion must be established first.

### Files, tests and preservation

Wave 4 edited `agents/career/workflow/agent.py`, `shared_evidence.py`, and this appended report; diagnostic edits are `tests/diagnostics/README.md`, `test_career_wave2_parity.py`, and the quoted-evidence fixture in `test_career_shared_evidence.py`. New diagnostic files are `career_wave4.py`, `career_wave4.json`, `career_wave4_parity.json`, `career_wave4_compression.json`, `test_career_completion.py`, `test_career_completion_runner.py`, and `test_career_wave4_parity.py`. No dependency changes or package installation occurred.

**85 offline tests passed:** 59 prior tests, 3 new Wave 4 parity/compression checks, 16 completion-contract tests and 7 actual ADK Runner tests with fake model responses. Coverage includes namespace isolation/reset, exact claim/URL handoff, invalid IDs, candidate/verification limits, requested-fact output integrity, partial official facts, official/anecdotal separation, historical preservation, source-pair comparisons, human escalation, personal eligibility and no unselected-candidate leakage. Runner checks include Certification, Interview current/stable, Trust A/B/C and supplied sources, Research and Career; the prior Networking Runner test also remains. No cloud calls are made by these offline tests.

The original report bytes and all previous JSON artifacts are preserved. `career_wave4_parity.json` captures entry source, protected hashes, append-only instruction hashes and final source/method hashes. Removing only declared Wave 4 changes reconstructs the exact Wave 3 agent AST; existing tests then reconstruct prior checkpoints. Names, models, root relationships, unrelated callbacks and Career/Networking/Research configurations are unchanged. Legacy `evidence.py` remains byte-identical. All further cloud canaries remain deferred; partial live success and mocked success do not establish deploy readiness.

Remaining P0: official Certification price discovery/completion and provider availability; uncompleted live Interview current/Trust validation; unchanged live Networking/Research regression coverage and conservative availability limits; prior Trust/current-evidence risks pending healthy live evaluation. The root/provider stall is a separate availability risk, not a reason to rewrite routing or compress prompts in this wave.

No deployment, Agent Engine create/update/delete, production inference, commit or push occurred. Production Reasoning Engine 3463694723959488512 and existing dev engines remain untouched. Nothing is staged. Final syntax/import, source/manifest, privacy, whitespace and Git verification is recorded below after checks.

Final Wave 4 verification passed: 85 offline tests (36 pytest + 49 unittest), 30 runtime-loaded instruction/model digests, nine unchanged root sub-agents, protected source and previous artifact hashes, original report-prefix hash, Python syntax/importability, JSON privacy, Git scope/branch/HEAD/index checks, git diff --check and 32 untracked-inclusive whitespace checks. Saved live Certification discovery/verification outputs replayed through the final policy produced the identical final answer without API calls. All eight remaining live cases remain deferred after TOOL_CAPACITY 429. Nothing staged, committed, pushed or deployed.


### Wave 4 Live Acceptance Completion

**Final status: INCOMPLETE DUE TO PROVIDER CAPACITY.** This was acceptance of the existing Wave 4 source, not an optimization or implementation wave. No prompt, tool, evidence architecture, model, routing, backend, frontend, test, diagnostic driver or deployment configuration was edited. All 44 protected source-file hashes captured at entry remain identical. The earlier report and diagnostic results are preserved byte-for-byte before this appended section.

The new user-authorized acceptance session used the local source workflow and Vertex model APIs only, with fresh in-memory sessions. No production/development Agent Engine endpoint was invoked. The earlier Wave 4 capacity-stop artifact was not reused or overwritten. This separate acceptance attempt began with exactly one lightweight provider-health probe and followed the requested suite order until capacity failed.

**Health probe:** “How should I introduce myself to a cybersecurity recruiter?” completed normally in 25.480s, routed to Networking, used zero Search and URL Context calls, and returned useful communication guidance with no errors. The gate passed. Two Certification stable samples were then run before Interview stable, Trust C and Networking current. All completed fast paths were manually reviewed before the expensive current canary.

**Attempt accounting:** six live attempts including the probe, five completed and one failed. Excluding the probe, five suite samples were attempted and four completed. One failed attempt emitted several observations of the same 429; that is **one capacity failure**, not five independent failures. Six suite cases were deferred. There were no retries, repeated health probes, subsequent live model calls after the failure, or source edits.

| Live case | Seconds | Search helpers | Verification attempts / completions | Verdict |
| --- | ---: | ---: | ---: | --- |
| health_probe | 25.480 | 0 | 0 / 0 | PASS |
| certification_stable_1 | 23.828 | 0 | 0 / 0 | PASS |
| certification_stable_2 | 12.202 | 0 | 0 / 0 | PASS |
| interview_stable | 21.350 | 0 | 0 / 0 | PASS |
| trust_c | 2.060 | 0 | 0 / 0 | PASS |
| networking_current | 118.150 | 1 | 2 / 2 | INCOMPLETE DUE TO PROVIDER CAPACITY |

**Certification stable:** both fresh samples returned the useful generic cost/role-relevance/practical-experience decision framework with zero retrieval. No unsupported discount, price, voucher offer, eligibility, employer-ranking or present vendor-benefit claim appeared. Total runtimes were 23.828s and 12.202s (range 11.626s). These are healthy normal-variance samples, not a repeatable stall. The second sample reused the process/SDK client while using a fresh chat session; warming and provider variance are not isolated. No claim of guaranteed tail-latency improvement or a need to modify prompts follows from these two samples.

**Interview stable:** completed in 21.350s with zero Search/URL Context. The response gave general fundamentals, scenarios, practical-project preparation and practice options. It did not assert current employer-specific process stages. This completed stable path passes its stated acceptance checks.

**Trust C:** completed in 2.060s with zero Search/URL Context. It immediately recommended human review, requested exact disputed wording/source links for the relevant official authority and explicitly avoided claiming anyone had been contacted or a referral created. Its UNRESOLVED assessment did not manufacture a source comparison. This fast path passes.

**Networking current:** routed correctly, completed one Search helper (seven provider-reported queries), registered three candidates and attempted two deterministic verifications. The first verification completed; the second URL Context helper returned 429 RESOURCE_EXHAUSTED. There was no final user-facing answer. Primary failure category: **TOOL_CAPACITY**; underlying cause: PROVIDER_CAPACITY. No HEALTHY_WORKFLOW_FAILURE was established. The 118.150s failed runtime is not a completed-answer latency or speedup. No candidate/status reliability verdict can be assigned to a final response that was never produced.

Immediately after this error, all live testing stopped. Research current, Career Exploration current, Certification current, Interview current, Trust A and Trust B were not attempted in this acceptance session. Their earlier Wave 3/Wave 4 results are not relabeled as new acceptance passes. Current Certification requested-fact statuses/source domains, Interview official/anecdotal results and Trust A/B live adjudication remain unassessed here. Safe partial answers remain acceptable under the requested criteria, but no new current Certification answer was obtained in this session.

**Reliability verdict:** no violation was observed in the five healthy completed responses, and no true product defect was reproduced. This does not establish current-fact architecture acceptance for the unfinished/deferred paths. A provider-capacity failure alone does not fail the evidence architecture; it leaves coverage incomplete. No product correction was attempted or required by the available healthy completed observations.

**Latency detail:** existing diagnostic instrumentation records request start, root first event, transfer, specialist first event/start, helper requests/completions, first public text and total runtime in `career_wave4_acceptance.json`. Disjoint phases below distinguish SDK/helper waiting from gaps; FINALIZATION is the existing stream-finalization interval. They do not measure pure model computation. The failed second Networking helper is censored at the error time; one attempted source check did not complete.

| Case | ROOT_WAIT | SPECIALIST_PRE_TOOL_WAIT | TOOL_WAIT | SPECIALIST_POST_TOOL_WAIT | FINALIZATION | UNOBSERVED_RUNTIME_WAIT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| health_probe | 9.692 | 14.744 | 0.000 | 0.000 | 0.001 | 1.043 |
| certification_stable_1 | 7.587 | 15.281 | 0.000 | 0.000 | 0.001 | 0.959 |
| certification_stable_2 | 3.555 | 8.624 | 0.000 | 0.000 | 0.001 | 0.022 |
| interview_stable | 3.371 | 17.955 | 0.000 | 0.000 | 0.001 | 0.023 |
| trust_c | 2.030 | 0.000 | 0.000 | 0.000 | 0.002 | 0.028 |
| networking_current | 6.512 | 27.078 | 71.122 | 12.146 | 0.000 | 1.292 |

**Full offline validation:** all 85 existing Career evidence/configuration/diagnostic tests passed. The broader repository suite was also run with authentication and outbound sockets blocked so the legacy HTTP test could not call the production-backed Career endpoint. Combined result: **97 passed, 1 failed** across 98 offline tests (48 pytest passes/1 failure plus 49 ADK unittest passes).

The single failure is `tests/test_agents.py::test_agent_starter_endpoint[career]`, which still expects the old unimplemented HTTP 501 stub. The integrated Career route returns 503 when authentication is deliberately disabled. Source inspection confirms that the 501 expectation and the implemented Career endpoint already coexist at stable checkpoint beeb3a87ad2f8892dce9e30f376bd2768b65c239. This is a pre-existing test-contract mismatch, not a newly reproduced Wave 4 logic/evidence defect. It was neither hidden nor patched. All other legacy frontend/advising/health tests passed. No production runtime request was sent by the offline tests.

**Changed files in this acceptance task:** only this appended report and three new diagnostic JSON result files: `tests/diagnostics/career_wave4_acceptance.json` (live observations, reviews, phases, deferred cases), `career_wave4_acceptance_checkpoint.json` (entry product-source/report/history hashes), and `career_wave4_acceptance_offline.json` (all offline outcomes and legacy-test assessment). Product source and existing test/diagnostic source files remain unchanged. The pre-existing dirty/untracked implementation files were left intact.

Syntax/importability, instruction/model parity, privacy, protected-source/history hashes, whitespace and Git checks are recorded at finalization below. No deployment, new dev engine, production modification, staging, commit or push occurred. The next live work remains the six deferred suite cases, following a new user-authorized provider-health check when capacity permits; no recurring/retry automation was created.

Acceptance final checks passed: all 44 captured product/source hashes identical; all previous JSON and report-prefix hashes preserved; syntax/importability and all 30 instruction/model checks passed; privacy and phase/accounting checks passed; git diff --check and changed-file whitespace checks passed. Offline outcome remains 97 passed/1 pre-existing stale stub expectation failed (all 85 Career/configuration/evidence/diagnostic tests passed). HEAD/branch are unchanged and the index is empty. Product source was not edited; the pre-existing dirty implementation files remain intact. No deployment, production request, staging, commit or push occurred. Final acceptance status remains INCOMPLETE DUE TO PROVIDER CAPACITY.


## Wave 5 — Controlled Prompt Compression

### Verdict and scope

**Wave 5 compression verdict: PASS for measured size, reviewed rule preservation, structural parity and offline behavior checks. Selective live confirmation: INCOMPLETE DUE TO PROVIDER CAPACITY.** This is not deployment approval, a claim of full Wave 4 live acceptance, or proof of improved typical latency. Wave 6 remains the full benchmark before any deployment decision.

Seven original specialist instruction literals were consolidated. Root, Trust, Career Exploration and all helper instructions remain exact. No model, tool, name, relationship, callback, routing structure, evidence registry/mechanics, backend, frontend or engine/deployment setting changed. Every Wave 1–4 instruction append and every specialist handoff table remains exact. No new policy inheritance is assumed: each specialist's complete compressed policy is present in its own rendered instruction.

Only repeated concepts and examples within selected original sections were consolidated. This was not a rewrite from scratch or a whitespace-minification exercise. A dedicated test strips all whitespace and still requires a meaningful reduction for every target. Multiline source literals make the changed wording readable; the full AST is identical to entry after restoring only the seven audited instruction expressions.

### Rendered sizes

These are exact runtime `LlmAgent.instruction` string counts, including existing appends, not source-file size or assumed savings from shared constants. The current captured entry sizes differ slightly from the older Wave 3 figures in the task because Wave 4 appended Certification/Interview instructions.

| Component | Before chars | After chars | Reduction chars | Reduction % | Behavior verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| internship__job_preparation_agent | 12,559 | 10,215 | 2,344 | 18.66% | Offline PASS; live coverage below |
| resume__portfolio_agent | 13,785 | 11,703 | 2,082 | 15.10% | Offline PASS; live coverage below |
| interview_preparation_agent | 19,424 | 16,181 | 3,243 | 16.70% | Offline PASS; live coverage below |
| networking__professional_communication_agent | 16,371 | 13,911 | 2,460 | 15.03% | Offline PASS; live coverage below |
| skill_gap__career_roadmap_agent | 12,492 | 10,344 | 2,148 | 17.20% | Offline PASS; live coverage below |
| research__graduate_pathways_agent | 16,599 | 14,073 | 2,526 | 15.22% | Offline PASS; live coverage below |
| certification__technical_development_agent | 15,008 | 12,689 | 2,319 | 15.45% | Offline PASS; live coverage below |
| Seven compressed specialists | 106,238 | 89,116 | 17,122 | 16.12% | Size target met |
| All 30 agents/helpers | 172,168 | 155,046 | 17,122 | 9.94% | 23 components unchanged |

Intentionally unchanged: Career Exploration (23,291 chars), Trust (12,520), root (8,037), and every Google Search/URL Context helper. Root was a secondary target; preserving its validated domain-ownership and explicit Trust routing was preferable to a speculative additional reduction. Career's evidence-specific rules and Trust's conflict-resolution protocol were not compressed.

The captured live SDK request metrics confirm actual augmented instruction reductions too: Networking 29,954 -> 27,494 chars (-2,460; about 8.21%), Certification 28,593 -> 26,274 (-2,319; about 8.11%). Those effective SDK strings include unchanged ADK-added routing/context; they are a different denominator from authored/rendered specialist instruction strings. No tokenizer, download or token-count API was used, and character reduction is not presented as a measured token/latency reduction.

### Exact instruction hashes

The complete pre-edit strings, original base hashes, old/new full instruction hashes, character counts and edited spans are preserved in `tests/diagnostics/career_wave5_parity.json`.

| Component | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| internship__job_preparation_agent | `cd4014bbaae6fec25e81b3846a955c07e2e27f430581f218271e54783f7233bb` | `b30e1f02efed93c03f86a35c7ae9c188d5da0d27717f4e34945a692fddd2245e` |
| resume__portfolio_agent | `c536bc979c045b9ee218431a0be5e6f6bc4ab57ff71b36860b49dee66ce637c2` | `b5c618ce57217ae8e0e32445c3e10f0d86afad9d3f854b959d52ef681f7d3724` |
| interview_preparation_agent | `6d59397f46f97e96dfff3d0f695a49ea3a29228aa33f0de29797c1b7635db8a3` | `a7f7bdd99963a700bb844c81a76e6238a619a558a2a24c21d63ef49fdc539df2` |
| networking__professional_communication_agent | `64a6f3d7ef0f138bda79fe6bc632e3f64a4a5b49430ca4451d1ededeb12aff18` | `d7751ec046a23d95d7e35dacd8f7bd8f737b61f22f90272a61240e23548dd3a4` |
| skill_gap__career_roadmap_agent | `0f5a5146b54c7db4d32a23ef2b44b40121481d9fbd8122cac96d88cc4e0aeee7` | `13a3d974a310089e4d0bf3757c8452f943086124c7717147720ee61f04c911c0` |
| research__graduate_pathways_agent | `d00a56c4c1780b8d87bb67f07bf4d165bdd92b4f6ba564deb090a0ba2d9d143d` | `3c6937682cb6b5adb668c4571b756954d28d80d7b3c5503498a98625c0215e86` |
| certification__technical_development_agent | `113e93e83161d49a399fe7fc8d8bc6f6b5897fbdcc06d235be6869ca3e776866` | `ba514fedf089e2d6cdba34370757c57d4d4246404b3abad2f2a0b189fc4c59ff` |

All 23 other full instruction hashes remain identical. Protected-file hashes include `evidence.py`, `shared_evidence.py`, backend/frontend/configuration and existing tracked tests. No shared mechanic was edited to make compression appear successful.

### Semantic consolidation checklist

The human-readable mapping is `tests/diagnostics/career_wave5_semantics.md`; the JSON contains the exact displaced/replacement text and maps all **631 displaced nonempty source lines** to their new sections. **106 reviewed rule groups** document retained obligations. This is an auditable manual semantic review plus exact replay/unchanged-span tests, not a formal proof of arbitrary LLM obedience.

- Shared reliability/date sections: verified facts versus patterns/recommendations/student input; all changing-fact categories; the full source hierarchy; Search/URL Context roles; Morgan grounding; fabrication/outcome guarantees; autonomy, missing context and handoffs; resolved year/cycle/query year; historical labels and the existing calendar/stable override precedence.
- Interview: overlapping official-process gates were merged while retaining official/current/explicit-detail/exact-role requirements, all enumerated process details, broad-guide versus role-specific classifications, lower-confidence ambiguity handling, anecdotal/official separation, partial support and explicit gaps. Information-category definitions were consolidated without changing their scope. Technical/behavioral/mock practice and handoffs remain unchanged.
- Research: duplicated opportunity-status lists were merged with every label retained. ACTIVE RESOURCE still requires current existence without implying openings. Passed dates remain historical even on live pages. Prior/latest verified cycles do not establish next-cycle availability. Admissions probability, profile dimensions and current program requirements remain bounded. Faculty/funding/RA/eligibility safeguards and all later Python budgets remain exact.
- Networking: repeated integrity/personalization examples, recruiter/fair details and follow-up/thank-you rules were consolidated. All unconfirmed relationship/referral/meeting/achievement prohibitions, actual-context requirements, fair fact verification, non-universal timing and no inference from silence remain. Student review/approval and no impersonation remain exact.
- Certification: current provider fact categories, university funding/access boundaries and price/discount estimate prohibitions were merged. Fit still covers verified background, goals, time/budget, broader readiness, all outcome guarantees and hands-on alternatives. Stable no-search behavior and the exact narrow/per-fact evidence overrides remain unchanged; no offer/eligibility leakage is newly allowed.
- Internship: current-cycle posting, openings and eligibility procedures were consolidated, preserving exact official title/qualifications/status/deadline/location/conditions, non-synthesized openings, the original no-opening response and explicit current-posting eligibility over historical/year-level assumptions. The complete stable preparation gate remains exact.
- Resume: experience and metrics sections were combined, retaining all prohibited experience/ownership/completion upgrades, actual measurements or qualitative alternatives, and evidence-based verb thresholds. Real-experience tailoring, no invented keywords/metrics, ATS honesty, private-work safeguards and student approval remain unchanged.
- Roadmap: capability profiles/current-market analysis and repeated certification/employment boundaries were consolidated. Observed requirements, general patterns and recommendations remain separate; no universal requirements, single-posting market inference or one-employer standard. Goal/time prioritization, demonstrable projects and specialist ownership remain intact.

For Internship/Resume/Roadmap, the earlier calendar resolution remains required when current-date facts need it and no later override applies; it was not silently replaced by the later primary-specialist calendar policy. Existing gates remain local to each agent rather than being moved to root or an assumed shared context.

### Offline acceptance matrix

All seven targets passed stable/current mocked ADK Runner cases and static semantic/structural checks. Every stable case used zero retrieval. Current Interview/Research/Networking/Certification fixtures used one discovery and two selected checks; raw-tool Internship/Resume/Roadmap fixtures used one Search and one exact-source URL check. The original mechanisms and limitations were preserved, not replaced with new enforcement.

| Specialist | Stable path | Current path | Evidence boundary | Routing expectation |
| --- | --- | --- | --- | --- |
| Interview | Zero-tool general practice | Official/anecdotal fixtures separated | Original statuses, scope and team variability preserved | Expected transfer; root/handoffs exact |
| Research | Zero-tool readiness guidance | Bounded selected candidates | UNVERIFIED/HISTORICAL unchanged, exact links, no inferred opening | Expected transfer; root/handoffs exact |
| Networking | Zero-tool communication | Bounded selected candidates | UNVERIFIED/HISTORICAL unchanged, exact links, no active-access promotion | Expected transfer; root/handoffs exact |
| Certification | Zero-tool conceptual guidance | Selected official fact fixtures | Per-fact/missing-fact rendering and exact-source tests retained | Expected transfer; root/handoffs exact |
| Internship | Zero-tool preparation | Original current posting/tool flow | Current-source and eligibility rules mapped; gaps explicit | Expected transfer; root/handoffs exact |
| Resume | Zero-tool material guidance | Original current requirement/tool flow | Actual-experience/source rules mapped; no invented skill/metric allowance | Expected transfer; root/handoffs exact |
| Roadmap | Zero-tool development guidance | Original current-demand/tool flow | Evidence/pattern/recommendation separation mapped | Expected transfer; root/handoffs exact |

Mocked routing checks exercise the real Runner/tool plumbing with expected transfers; they do not prove the stochastic model's choices on every input. Root instructions, graph and specialist handoff tables are exact, and actual live routes below were correct. Current model-directed behavior for the three secondary specialists is not converted into a new deterministic architecture.

Career's 12 existing evidence tests passed, with its instructions/configuration and legacy registry byte-identical. Trust's actual Runner mocks passed immediate human escalation, unnamed-conflict clarification and supplied-source comparison with bounded checks; Trust/root instructions and mechanics are exact. Existing adverse tests for historical/current preservation, official/anecdotal separation, unknown IDs, namespace isolation/reset, exact claims/URLs and final renderer integrity all passed.

Historical Wave 2/Wave 4 parity tests now invoke a test-only restoration helper. It restores an instruction only if its observed new hash matches this manifest, then runs their original historical comparisons. New tests also verify the full restored AST, uncompressed components, exact edited-block replay, complete displaced-line mapping and rejection of an unmeasured replacement. This makes the intended prompt change explicit without masking unrelated configuration changes.

### Selective live observations and capacity stop

The provider health probe (Networking stable) completed normally with the correct route and zero Search/URL Context in 25.197s. Certification stable completed in 27.096s with zero retrieval and the same safe generic framework, without current discounts/offers/eligibility. Interview stable routed correctly, then failed with **SPECIALIST_CAPACITY 429** before a specialist response. Its 12.818s failed runtime is not completed-answer latency and is not evidence of a compression regression.

**Three live attempts, two completed, one capacity-failed attempt. All live calls stopped immediately after the 429.** Networking stable C, Research stable D and current Certification E/Networking F were deferred; no current factual live canary was attempted. The health probe is one equivalent Networking stable observation, not an extra completed C run. No repeated probes, retries, new output file to bypass capacity, or source changes during live execution occurred.

The existing Networking examples remain illustrative templates needing adaptation to actual student context. The advisory “under 300 characters” heading also appears in the pre-compression probe; it is not new evidence of an official platform limit or a compression-introduced claim. Templates should not be treated as verified student history. This wave does not claim to solve inherited example-quality limitations outside the compression scope.

No healthy completed run demonstrated a new unsupported partnership/access/funding claim, status promotion, historical/current confusion, anecdotal-to-official promotion, unnecessary stable retrieval or routing/Trust regression. **No component compression was reverted.** The capacity-failed Interview sample is unassessed for output quality, not a passing response. Four planned live cases remain explicitly deferred in `career_wave5.json`.

### Before/after latency comparison

These are retained pre-compression observations versus selective current-source samples, not randomized or concurrent A/B trials. All chat sessions are fresh; process/SDK warming, provider load, output length and differing context can affect timing. The second old Certification sample reused its process/SDK client. One new sample cannot establish a median or causation.

| Observation | Transfer time | First specialist event | First public text | Total seconds |
| --- | ---: | ---: | ---: | ---: |
| Before: acceptance_health_probe | 10.723 | 10.730 | 25.479 | 25.480 |
| After: wave5_health_probe | 9.328 | 9.337 | 25.195 | 25.197 |
| Before: acceptance_certification_stable_1 | 8.533 | 8.541 | 23.827 | 23.828 |
| After: wave5_certification_stable | 8.995 | 9.006 | 27.094 | 27.096 |

The other completed pre-compression Certification stable sample was 12.202s, so the latest two-sample reference median is 18.015s. The new single 27.096s result does not demonstrate improved typical latency. Networking probe totals are effectively similar (25.480s before, 25.197s after), not a causal speedup. Its unchanged root's SDK wait also varied, reinforcing provider/runtime confounding. New Interview failed, and Research/current after-samples are absent; they cannot support a latency comparison.

Size reduction is proven by actual instruction strings and observed SDK character counts. **Latency improvement is not demonstrated and is not required for the limited Wave 5 compression PASS.** Full behavior/tail-latency evaluation, including the unfinished Wave 4 current acceptance cases, remains Wave 6 work under healthy capacity.

### Tests, files and preservation

Unique offline outcome: **123 passed, one known stale test failed** across 124 tests. This includes **111 passing Career/evidence/configuration/diagnostic tests**, with 12 new compression/parity checks and 14 new per-specialist Runner cases. ADK unittest total: 63 passed. Pytest total: 60 passed and the existing stale HTTP-501 expectation failed. The final non-whitespace compression test was added and run with all 12 Wave 5 parity checks after the broader pytest run; it adds one unique passing test to the recorded counts.

The stale test is unchanged: `tests/test_agents.py::test_agent_starter_endpoint[career]` expects the obsolete unimplemented 501 stub. With authentication/network blocked to prevent production access, the integrated Career route returns 503. This known mismatch is reported separately, not repaired or counted as a compression failure. All other existing tests passed, including root/Career/Trust and evidence status regressions. No real cloud request was made by offline tests.

Product edit: `agents/career/workflow/agent.py`, seven instruction literal expressions only. Documentation: this appended report and `tests/diagnostics/README.md`. Two existing historical parity test files were updated to use strict Wave 5 normalization: `test_career_wave2_parity.py` and `test_career_wave4_parity.py`.

New diagnostic/audit files: `career_wave5_compression.py`, `career_wave5.py`, `career_wave5_parity.json`, `career_wave5_semantics.md`, `test_career_wave5_parity.py`, `test_career_wave5_matrix.py`, `career_wave5_offline.json`, and `career_wave5.json`, all under `tests/diagnostics/`. No dependencies were added or installed. Previous report sections and all prior JSON results are preserved.

Final validation below covers runtime instruction hashes/counts, syntax/importability, protected files, prior artifacts/report prefix, privacy, whitespace and Git scope. No deployment, new dev engine, production modification, staging, commit or push occurred. Models, names, tools, graph, root/Trust/Career, both evidence modules, backend/frontend and deployment configuration remain unchanged. Wave 4 live acceptance remains incomplete; Wave 5 compression does not overwrite that historical status.

### Final validation result

PASS: all 30 loaded ADK agent/helper instruction hashes and counts match the manifest; root graph and models match. Python AST validation passed for 28 workflow/test files. Protected runtime files, prior diagnostic JSON artifacts and the historical report prefix retain their captured SHA-256 hashes. Diagnostic JSON privacy-key audit passed. Both tracked `git diff --check` and untracked-file whitespace checks passed. HEAD remains `beeb3a87ad2f8892dce9e30f376bd2768b65c239` on `feature/career-agent-runtime-integration`, with an empty index. No deployment, staging, commit or push occurred.


## Wave 6 — Final Workflow Benchmark

**Decision: NO-GO — ARCHITECTURE DEFECT REMAINS.** The blocker is a recurring output-reliability boundary failure in Networking, not an observed routing/graph/evidence-registry defect. Provider capacity independently prevents full live coverage. No optimization, product patch, deployment, staging, commit or push occurred.

### Method, source freeze and provider health

Captured all existing tracked files and untracked workflow product files before measurement in `career_wave6_parity.json`, along with prior diagnostic artifact hashes and the exact report-prefix byte count/hash. Reused the existing allowlisted local-source ADK runner (ADK 2.12.0 / Vertex SDK 1.165.1); fresh local session per request, normal root routing, project cosc-490/global model endpoint. No Agent Engine/Flask/browser endpoint was called. Timings exclude process imports and include runner setup; observer overhead is not isolated. First text is outer-runner public text, not model first-token latency. Raw hidden reasoning, credentials and session identifiers are not stored.

Plan: three stable rounds for all nine specialists, ten current cases including both Trust tests, and a fresh lightweight Networking no-tool probe before each batch. After the first round, current coverage was prioritized ahead of stable repeats; no attempted case or prompt changed. Samples were sequential with five seconds between successful requests. Health deadline 90s; other diagnostic deadlines 240s, not production timeouts. No automatic retry.

Initial probe passed in 32.289s with correct Networking routing and Search=URL=0. Six benchmark stable cases completed. The next Research-intent request failed at the root in 2.943s with 429 before transfer. Classification: **PROVIDER_CAPACITY / ROOT_CAPACITY; batch PROVIDER_UNHEALTHY**. All live calls stopped immediately. Eight attempts: seven completions including the probe, six benchmark completions, one capacity-failed attempt. Its four error records describe one failure, not four failed requests. No later health probe/retry/batch was run. All ten current cases, stable repeats, and first-round Certification/Trust were deferred. Research never dispatched.

### Nine-specialist scorecard and original baseline comparison

Baseline values below come from unchanged `career_baseline.json` and `career_baseline_followup.json`, matching the original report. `!` means failure/censoring; `[other route]` is not a specialist latency. Final min/median/max exclude failures and health probes. Each completed specialist has n=1: equal extrema are not a measured distribution. Historical readiness probes and prior-wave successes are not relabelled as Wave 6 samples.

| Specialist | Original stable seconds; Search | Final stable min / median / max (n); Search | Original current seconds; Search / URL | Final current | Reliability / priority |
| --- | --- | --- | --- | --- | --- |
| Career Exploration | 38.060s H0/U0; 20.256s H0/U0 | 23.297 / 23.297 / 23.297 (1); H0/U0 | 63.450s H1/U2 | Not attempted | PASS observed stable scope; current unassessed; **P3** |
| Internship & Job Preparation | 67.391s H2/U0; 17.884!s H2/U0; 90.291s H3/U0 | 22.809 / 22.809 / 22.809 (1); H0/U0 | 56.716s H2/U0 | Not attempted | PASS observed stable scope; current unassessed; **P1** |
| Resume & Portfolio | 61.032s H2/U0; 54.513s H1/U0 | 22.213 / 22.213 / 22.213 (1); H0/U0 | 54.072s H2/U0 | Not attempted | PASS observed stable scope; current unassessed; **P1** |
| Interview Preparation | 23.882s H0/U0; 18.471s H0/U0 | 19.967 / 19.967 / 19.967 (1); H0/U0 | 18.092!s H2/U0; 240.017!s H4/U0 | Not attempted | PASS observed stable scope; current unassessed; **P1** |
| Networking & Professional Communication | 18.020s H0/U0; 16.945s H0/U0 | 12.748 / 12.748 / 12.748 (1); H0/U0 | 160.696s H6/U0 | Not attempted | FAIL: unsupported LinkedIn numeric policy on stable path; **P0** |
| Skill Gap & Career Roadmap | 78.191s H3/U0; 240.013!s H0/U0; 80.330!s H0/U0 | 19.896 / 19.896 / 19.896 (1); H0/U0 | 62.180 [other route]s H2/U0; 53.228s H2/U0 | Not attempted | PASS observed stable scope; current unassessed; **P1** |
| Research & Graduate Pathways | 46.616 [other route]s H0/U0; 49.071s H2/U0 | No healthy sample | 226.914s H8/U0 | Not attempted | LIVE UNASSESSED; offline contracts pass; **P1** |
| Certification & Technical Development | 16.217s H0/U0; 20.260s H0/U0 | No healthy sample | 0.803!s H0/U0; 91.939!s H3/U0 | Not attempted | LIVE UNASSESSED; offline contracts pass; **P1** |
| Trust & Human Escalation | 19.374s H1/U0; 9.056s H0/U0 | No healthy sample | 100.158s H3/U0; 9.818s H0/U0 | Not attempted | LIVE UNASSESSED; offline contracts pass; **P1** |

Certification historical Flask ~165s is context only; the local original attempts failed at 0.803s and 91.939s (0 and 3 Search helpers), so there is no completed local current latency baseline for that domain. Interview current Microsoft wording differs from the Google/generic baseline; Research current removes graduate opportunities; Resume/Roadmap wording also follows the requested canaries rather than forcing identical original prompts. No current pre/post comparison is available.

### Observed latency and retrieval changes

| Specialist | Original healthy correctly routed stable median (s) | Wave 6 (s, n=1) | Observed reduction | Search before → after |
| --- | ---: | ---: | ---: | --- |
| Career Exploration | 29.158 | 23.297 | 20.10% | [0, 0] → [0] |
| Internship & Job Preparation | 78.841 | 22.809 | 71.07% | [2, 3] → [0] |
| Resume & Portfolio | 57.772 | 22.213 | 61.55% | [2, 1] → [0] |
| Interview Preparation | 21.177 | 19.967 | 5.71% | [0, 0] → [0] |
| Networking & Professional Communication | 17.483 | 12.748 | 27.08% | [0, 0] → [0] |
| Skill Gap & Career Roadmap | 78.191 | 19.896 | 74.55% | [3] → [0] |

These six single observations are below their original healthy stable medians. They do **not** establish causal speedups, typical latency, tail latency or an SLA. Root SDK warming, output length/intake versus full-plan responses, ordering and provider variation confound the comparison. Roadmap now gives a capability outline plus intake rather than a complete personalized year plan. No current-path latency, verification success or live retrieval reduction was measured in Wave 6. All observed requests—including the probe and failed root request—had zero Search, grounding queries, URL helpers and deterministic verifications. Stable Internship/Resume/Roadmap over-retrieval was absent in their completed samples.

### Per-attempt timing and reliability review

| Run | First root event | Transfer | First specialist event | First public text | Total s | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| wave6_health_stable_1 | 10.648 | 10.648 | 10.655 | 32.288 | 32.289 | HEALTH_GATE_PASS_WITH_QUALITY_NOTE |
| wave6_career_stable_1 | 2.771 | 2.771 | 2.774 | 23.296 | 23.297 | PASS_OBSERVED_STABLE_SCOPE |
| wave6_internship_stable_1 | 2.979 | 2.979 | 22.807 | 22.808 | 22.809 | PASS_OBSERVED_STABLE_SCOPE |
| wave6_resume_stable_1 | 3.088 | 3.088 | 22.210 | 22.211 | 22.213 | PASS_OBSERVED_STABLE_SCOPE |
| wave6_interview_stable_1 | 3.515 | 3.515 | 3.518 | 19.966 | 19.967 | PASS_OBSERVED_STABLE_SCOPE |
| wave6_networking_stable_1 | 2.121 | 2.121 | 2.123 | 12.747 | 12.748 | RELIABILITY_FAILURE |
| wave6_roadmap_stable_1 | 2.803 | 2.803 | 19.894 | 19.895 | 19.896 | PASS_OBSERVED_STABLE_SCOPE |
| wave6_research_stable_1 | 2.940 | — | — | — | 2.943 | UNASSESSED_NO_HEALTHY_COMPLETION |

Each structured run additionally retains request-start UTC, relative time zero, routed specialist, observed queries, helper/verification counts, public final text, model/helper spans and capacity classification. A first specialist event may be a state-only event or the final response; it is distinct from the recorded specialist model request start. Failed-root runtime is excluded from normal latency summaries.

**Networking reliability failure (P0 under the requested deployment gate):** completed `wave6_networking_stable_1` states “LinkedIn Connection Request: Needs to be extremely short (under 300 characters).” No platform limit was provided by the user and the run retrieved nothing. This is an unverified external platform constraint presented as an operational requirement, not merely a suggested personal word budget. Its truth/falsity across plans was not independently tested; the issue is unsupported specificity. The same symptom is already documented in Wave 2 stable quality review. Thus this is reproducible across retained observations, not inferred from the capacity failure or blamed on compression. Current institutional partnerships/access were not tested here. No prompt patch was made. Useful generic coaching, correct routing and zero Search do not erase the factual boundary failure.

The health probe also contains “Summer 2025 internships” inside an adaptable example at a 2026 checkpoint. Record this as **P2 stale example wording**, not as a proven currently open opportunity. Its health gate still passed: route, no tools and completion. Other healthy benchmark answers provided general conceptual guidance/intake without observed named current opening, price, partnership, funding or verified employer-process claims. This limited review is not a guarantee for untested current answers.

### Evidence, routing, Trust and specialist limitations

- **Career Exploration (P3):** Existing Career registry/status/budget/Runner tests pass; current live confirmation deferred. Baseline concern: Bounded reference; freshness did not establish specific current benefits/funding.
- **Internship & Job Preparation (P1):** Stable fast path and current tool plumbing pass offline; real current openings/eligibility not assessed. Baseline concern: Stable over-retrieval; current openings/eligibility asserted before intake without final citations.
- **Resume & Portfolio (P1):** Stable fast path and current tool plumbing pass offline; real current-market evidence not assessed. Baseline concern: Stable over-retrieval; current market claims without a defined posting sample or final citations.
- **Interview Preparation (P1):** Official/anecdotal separation, bounded verification and stable Runner contracts pass offline; current live deferred. Baseline concern: No completed employer-process current answer; named-company attempt censored at 240.017s.
- **Networking & Professional Communication (P0):** Current deterministic statuses and bounded verification pass offline; stable unsupported platform limit recurs live. Baseline concern: Six current Search helpers; unsupported active partnerships/access and incomplete current verification.
- **Skill Gap & Career Roadmap (P1):** Stable fast path and current tool plumbing pass offline; real frequency claims not assessed. Baseline concern: Stable over-retrieval; current original off-scope; clarified market claims lacked a defined sample/citations.
- **Research & Graduate Pathways (P1):** Current status/funding boundaries pass offline; no Wave 6 healthy stable/current sample. Baseline concern: Stable routing overlap; eight current helpers; unsupported openings/funding/eligibility.
- **Certification & Technical Development (P1):** Per-fact exam/version/price and stable vendor boundary tests pass offline; Wave 6 live deferred. Baseline concern: Stable vendor/policy leakage; no completed local current version/price answer.
- **Trust & Human Escalation (P1):** Immediate escalation, conflict clarification and supplied-pair bounded adjudication pass offline; Wave 6 live deferred. Baseline concern: Human escalation sometimes searched; invented conflict context and unverified program activity.

All six completed benchmark routes matched their expected specialist. Research has no route verdict because capacity failed before transfer; do not classify it as wrong routing. Trust human/conflict/source-pair cases passed offline only. Deterministic status preservation, discovery/verification caps, exact candidate transport and final rendering remain intact offline; no healthy Wave 6 current run establishes live evidence quality. Internship/Resume/Roadmap raw-tool current paths remain model-dependent and require healthy current evidence review before claiming those baseline factual defects are resolved.

### Offline validation, parity and diagnostic correction

**123 passed; one known stale failure.** Full existing suite split across its existing environments: repository pytest **60 passed / 1 failed**, pinned ADK unittest **63 passed / 0 failed**. Known stale `tests/test_agents.py::test_agent_starter_endpoint[career]` expects the removed HTTP 501 stub; the integrated endpoint returns 503 under the offline auth block. No backend test was repaired. External sockets/auth were blocked for offline tests.

Initial ADK diagnostic run had 32 passes and 31 errors because blocking all socket connects also broke Windows asyncio’s loopback self-pipe. Preserved that result in `career_wave6_offline_adk_initial.json`; changed only the diagnostic guard to allow loopback, with external access still blocked, and reran all 63 successfully. This was a harness error, not a workflow regression.

All 30 runtime-loaded instruction SHA-256 hashes/counts match Wave 5; all models and nine root specialist names match. Python syntax/import validation passed. Product file hashes protect tools, routing, graph, registries, backend/frontend and deployment configuration unchanged. Prior diagnostics and all pre-Wave 6 report bytes are preserved. Final privacy/whitespace/Git checks are recorded below after aggregation. No dependencies changed.

### Final priority and Wave 7 decision

**P0:** Networking output reliability: recurring unsupported platform-specific policy on a stable no-retrieval path. **P1:** Internship, Resume, Interview, Roadmap, Research, Certification and Trust: documented live/current-coverage limitations; no demonstrated new structural defect. **P2:** Networking example date quality (secondary to its P0 gate failure). **P3:** Career within its established tested scope, with current live revalidation still deferred. Provider availability is a separate limitation, not automatically P0.

**NO-GO — ARCHITECTURE DEFECT REMAINS.** This required decision label refers to the unresolved workflow output-reliability enforcement boundary; no graph/registry/routing architecture failure was demonstrated. GO’s “no reliability defect in healthy completed runs” condition was not met. Capacity gaps alone would not force NO-GO, but the observed unsupported claim does. Record a separate authorized fix/revalidation task before reconsidering Wave 7; this measurement wave made no fixes or deployment.

Artifacts: `tests/diagnostics/career_wave6_final.json`, `career_wave6_parity.json`, `career_wave6_validation.json`, `career_wave6_offline_pytest.json`, `career_wave6_offline_adk.json`, preserved initial ADK result, and opt-in measurement/offline/report drivers. Existing diagnostics and runtime source were not edited. Nothing staged, committed, pushed or deployed.

### Final validation result

PASS: 44 protected files and 41 prior diagnostic artifacts retain their entry hashes; all pre-Wave 6 report bytes are preserved. All 30 loaded instruction hashes/counts/models and nine root specialists match the Wave 5 checkpoint. Python syntax passed for 31 workflow/test files, including the new diagnostic drivers; runtime import passed. New JSON privacy-key and credential-pattern scans passed. Tracked git diff --check and untracked/new artifact whitespace checks passed. Index remains empty and HEAD remains beeb3a87ad2f8892dce9e30f376bd2768b65c239 on feature/career-agent-runtime-integration. Existing dirty agent.py/shared-evidence/diagnostic files are prior-wave state, unchanged by this measurement wave. No deployment, product edit, stage, commit or push occurred.


### Wave 6.5 — Networking Output Reliability Patch

**WAVE 6 BLOCKER CLEARED. Recommend proceeding directly to Wave 7 as a separately authorized task. No deployment occurred.** This clears the narrow recurring platform-specific no-retrieval claim blocker; it does not rewrite Wave 6 history or manufacture its missing current samples.

The reproduced defect was an unsupported LinkedIn connection-request “under 300 characters” requirement on generic recruiter-introduction guidance. Appended one local instruction rule to Networking only; no architecture, root, Career, Trust, model, tools, relationships, callbacks, registry mechanics, backend/frontend or engine/deployment configuration changed. No deterministic output filter was added.

Exact appended instruction (including its heading; leading/trailing newlines recorded in the manifest):

```text
PLATFORM-SPECIFIC FACT BOUNDARY
On stable/no-retrieval guidance, do not state exact platform-specific limits, requirements, feature rules, pricing, allowances, account restrictions, or current product behavior (including LinkedIn connection-note/message limits, InMail allowances and recruiter/Premium features), unless explicitly supplied by the user; attribute those facts to the user, not independent verification. Say "Keep the connection note brief and personalized," not "Keep it under 300 characters." If an exact platform fact materially matters, retrieve and support it through the existing current-fact path or explicitly say it was not verified. An explicit request such as "What is LinkedIn's current connection-request note character limit?" qualifies for current-fact retrieval. Generic recruiter templates, outreach/follow-up strategy, tone, personalization and relationship-building remain useful and tool-free; do not search merely to enrich them.
```

Networking instruction: **13,911 → 14,878 characters (+967)**. Old SHA-256 `d7751ec046a23d95d7e35dacd8f7bd8f737b61f22f90272a61240e23548dd3a4`; new SHA-256 `b512838305e558ecfd6a39b067fff900fbd01f9417aa57ddef5dc318999d0226`. All other **29 instruction hashes unchanged**. Runtime-loaded strings/models match the audit; removing only this exact appended literal restores the entire entry AST, including tools, graph, callbacks and every other instruction. Evidence modules and protected backend/frontend/config files retain byte hashes.

Before: a LinkedIn connection-request invitation “needs” a specific unverified character threshold. After: both target samples use brief, personalized connection-note guidance and practical templates without exact platform limits, prices, allowances, account restrictions or recruiter/Premium product-policy claims. Generic coaching remains no-retrieval. User-supplied facts must be attributed, not labelled independently verified. Templates contain adaptable company/application/project examples: personalize and verify these before use; this patch did not broadly redesign template behavior.

| Live canary | Total seconds | Route | Search | URL Context | Review |
| --- | ---: | --- | ---: | ---: | --- |
| wave65_networking_stable_1 | 21.615 | networking__professional_communication_agent | 0 | 0 | PASS |
| wave65_networking_stable_2 | 20.911 | networking__professional_communication_agent | 0 | 0 | PASS |
| wave65_interview_stable_1 | 28.570 | interview_preparation_agent | 0 | 0 | PASS |

Both Networking cases used exactly “How should I introduce myself to a cybersecurity recruiter?” First target sample also served as the lightweight health gate. All three requests completed healthily; **zero 429/capacity/transport failures**. No expensive full Wave 6 rerun, current live search, Agent Engine endpoint, deployment or backend/browser request was made. Small separate-process samples do not establish latency causation or guarantee universal model obedience.

**Offline: 142 passed, one known stale failure.** Repository pytest: 74 passed / 1 known stale failed; pinned ADK unittest: 68 passed. Existing suites all ran, including Career evidence, Networking current deterministic evidence statuses, Trust routing/immediate escalation/conflict/source-pair, and unrelated stable paths. New focused checks: 14 contract/parity tests plus 5 actual ADK Runner model-mocked tests. Three generic coaching semantic samples and one user-supplied drafting-constraint sample verify that the exact new instruction reaches the specialist and durable wording remains tool-free. Mocks obey the contract by construction; live samples provide separate model-behavior evidence. Negative examples are scoped as prohibited candidate claims, never validated as factual LinkedIn limits.

The exact question “What is LinkedIn's current connection-request note character limit?” still qualifies for the unchanged current-fact classifier. Its offline actual Runner test reaches **1 Search helper + 1 URL Context verification** and preserves UNSUPPORTED without asserting a numeric fact. Existing Networking authority/status mechanics remain unchanged (including Morgan-specific authority rules); retrieval eligibility does not guarantee a VERIFIED CURRENT LinkedIn answer. Unsupported facts can remain explicitly unverified, as requested.

Known stale failure remains `tests/test_agents.py::test_agent_starter_endpoint[career]`: obsolete HTTP 501 stub expectation versus the integrated endpoint’s 503 under the offline authentication block. No backend/test-expectation fix. Offline tests block external sockets/auth while allowing Windows asyncio loopback. A one-off pytest observer initially used the wrong hook argument name and stopped before collection; correcting only that diagnostic invocation produced the reported complete suite.

Historical-test adaptation: `career_wave5.py` and `test_career_wave5_parity.py` apply strict, diagnostic-only removal of the measured Networking append before historical comparisons. The normalizer verifies exact old/new instruction hashes and rejects unmeasured text; no runtime policy inheritance or historical JSON edits. Previous benchmark report bytes and all existing JSON artifacts remain unchanged.

Modified this task: `agents/career/workflow/agent.py`, this report, `tests/diagnostics/career_wave5.py`, and `tests/diagnostics/test_career_wave5_parity.py`. New diagnostic files: `career_wave65.py`, `career_wave65_live.py`, `test_career_wave65_contract.py`, `test_career_wave65_runner.py`, `career_wave65_parity.json`, `career_wave65_live.json`, `career_wave65_offline_pytest.json`, `career_wave65_offline_adk.json`, `career_wave65_validation.json`, and `career_wave65_final.json`, all under `tests/diagnostics/`. No dependency changes.

Decision: **WAVE 6 BLOCKER CLEARED** by two healthy target samples plus offline contract/current-path and regression checks. Proceed directly to Wave 7 when separately authorized; this is not a deployment action or a full-current-workflow reliability guarantee. Nothing staged, committed, pushed or deployed. Final syntax/import, source/parity, privacy and whitespace checks follow below.

Final validation PASS: runtime import and 30 instruction/model hashes; only Networking changes (+967 characters); full entry AST restored after removing that append, proving unchanged tools/callbacks/relationships. Protected files, prior JSON artifacts and report prefix hashes pass. Python syntax passes for 35 workflow/test files. New artifact privacy/credential-pattern scan and tracked/untracked whitespace checks pass; git diff --check exits 0. Branch/HEAD unchanged, index empty. No dependencies, backend/frontend, evidence mechanics or deployment configuration changed. Nothing staged, committed, pushed or deployed.


## Wave 7 — Final Dev Release Candidate

**RELEASE CANDIDATE — NO-GO.** A reproducible packaging/import defect blocks deployment. Stopped before any create/upload call; the repair remains unapplied under the explicit separate-authorization rule. This is not a new optimization wave. Wave 6.5’s Networking output blocker remains cleared; the new blocker is deployment packaging.

### Freeze, dependencies and deployment metadata

Captured Git status/branch/HEAD and protected file hashes before testing in `career_wave7_freeze.json`. Project/region intended: cosc-490/us-west1; supplied bucket: gs://cosc-490-agent-staging-20261021-a41c7e9b. Desired display name: Career & Professional Orchestration Agent - Final Dev RC. **No engine ID, resource name, creation timestamp, runtime metadata, staging prefix or uploaded artifact exists.** No cloud read/write was needed for the offline reproduction. Production, existing dev engines, and the staging bucket remain untouched.

Pinned environment: google-cloud-aiplatform[agent_engines,adk]==1.165.1 and google-adk==2.12.0; no dependency changes. Existing helper is still create-only, with its Source Dev v4 display/prefix defaults. Those names do not select an update target and are not the blocker. Production fallback remains 3463694723959488512.

### Exact defect, reproduction and minimal repair

`agent.py` imports `.shared_evidence`. `agents/career/workflow/deploy_dev.py:config.extra_packages` omits `agents/career/workflow/shared_evidence.py`. The six listed files are package initializers, agent.py, evidence.py and main.py. The pinned SDK archives those explicit file paths without discovering the missing sibling module.

Executed the actual SDK `_agent_engines_utils._upload_extra_packages` with an in-memory fake storage bucket, so no real upload occurred. Inspected its six-file archive and extracted only contained paths into an isolated temporary directory. A clean pinned `python -I -B` process importing `agents.career.workflow.main.app` from that archive failed with **ModuleNotFoundError: agents.career.workflow.shared_evidence**. Temporary files were removed on context exit. The packaging artifact retains only public findings, not source pickles, credentials or managed-session identifiers.

**Minimal repair:** add `agents/career/workflow/shared_evidence.py` to the existing `config.extra_packages` list in `deploy_dev.py`; preserve create-only behavior and all workflow/model/tool/graph settings. Re-run archive/import parity before creating a NEW engine. **No repair applied; wait for separate authorization.** No broad optimization or production promotion is proposed. Local source import alone cannot detect an omitted deployment file.

### Source/import parity

| Required source | SHA-256 |
| --- | --- |
| agents/career/workflow/agent.py | `abf498103233bf3b52d132cc159602694d09ae6a0cecaed1e29123e21d05fee4` |
| agents/career/workflow/shared_evidence.py | `d1b71f8765056383ed82d2363cdb3c14720796ac931abed220bdfc151fce7123` |
| agents/career/workflow/evidence.py | `140dd5a5e758c7a5cbc051019cf16314f2959e8ffc6a4f451928c97b9192780c` |
| agents/career/workflow/main.py | `bf7ac92680c85ef587d03d246330428cc45863201b00a891285ca075ae3d05f6` |
| agents/career/workflow/requirements.txt | `02a5f474eaadd6d3277c5323c6353f9462f7118c18bdbdcf16642d5c064cb720` |

All protected files unchanged. Local AdkApp import passes with explicit offline project/region and AnonymousCredentials; all 30 instruction hashes/models match Wave 6.5, with nine root specialists. Tools, callbacks, graph and evidence mechanics are unchanged. An initial auth-blocked import without project configuration required diagnostic setup; configured import passed. **Staged/deployed-byte parity is not applicable, not passed:** nothing was uploaded and isolated archive import fails.

### Remote routing/current evidence

| Specialist | Stable/routing | Current evidence |
| --- | --- | --- |
| Career Exploration | Not run: deployment blocked | Not run: deployment blocked |
| Internship | Not run: deployment blocked | Not run: deployment blocked |
| Resume | Not run: deployment blocked | Not run: deployment blocked |
| Interview | Not run: deployment blocked | Not run: deployment blocked |
| Networking | Not run: deployment blocked | Not run: deployment blocked |
| Skill Roadmap | Not run: deployment blocked | Not run: deployment blocked |
| Research | Not run: deployment blocked | Not run: deployment blocked |
| Certification | Not run: deployment blocked | Not run: deployment blocked |
| Trust | Not run: deployment blocked | Not run: deployment blocked |

Remote smoke, managed-session create/query/transfer/helper/first-text timings and current spot checks are all **not run**. Provider-capacity incidents: **0**; live inference attempts: **0**. No prior-wave result is relabelled as new deployed validation. Offline evidence status/URL transport and Networking exact-platform retrieval contracts pass, but no deployed current answer exists to inspect for status upgrades, anecdotes labelled official, partnerships, openings/funding or vendor offers.

### Flask, sessions and browser

No dedicated Flask override was started: there is no new validated engine. Fresh-session HTTP 200, same-user “those paths” continuity, different-user isolation, malformed-request release validation, natural upstream failure and New Chat managed-session reset are **not tested end to end**. Existing offline API/configuration tests are not substitutes for new-engine validation.

No browser interaction/redesign occurred. Initial message/input/thinking, Markdown/DOMPurify, timestamps/copy/retry, Enter/Shift+Enter, autogrow/scroll/counter, refresh/session/user persistence and New Chat fresh backend session are all **not run in Wave 7**. The existing ambient localhost page was neither repointed nor mistaken for the new release candidate. Remote/Flask latency: unavailable; classification **WORKFLOW DEFECT (packaging)**, not provider variance. No SLA added.

### Offline and final decision

Predeploy complete offline suite: **142 passed + one known stale failure**: 74 pytest passes/one stale failure; 68 ADK unittest passes. External auth/sockets blocked, allowing Windows asyncio loopback. Known stale `tests/test_agents.py::test_agent_starter_endpoint[career]` expects the obsolete HTTP 501 stub; the integrated route returns 503 under offline auth block. This obsolete expectation is not the deployment blocker and was not changed. Final suite/hash/privacy/syntax/whitespace reruns are recorded below.

**RELEASE CANDIDATE — NO-GO.** Only demonstrated release blocker: omitted required module in `deploy_dev.py:config.extra_packages`. Wait for the minimal repair authorization, then resume package/deployment/end-to-end validation. Do not claim final release validation complete or start a broad optimization wave.

Added Wave 7 preflight/report drivers, freeze/packaging/validation/final-result JSON, and predeploy/final pytest/ADK result JSON under `tests/diagnostics/`. This append is the only existing-file edit during Wave 7. Previous report history and prior JSON artifacts are preserved. No product changes, dependencies, cloud engine/session/staging-object creation, staging, commit, push, merge or promotion occurred. Production and all old dev engines remain untouched.

Final validation: full suite rerun after report creation again gives **142 passed + 1 known stale failure** (74 pytest / 68 unittest). Syntax passed for 37 workflow/test files; local runtime import passes with offline explicit project/credentials, while isolated deployment archive import still fails for the missing module. All protected source and 30 instruction/model hashes match entry; prior JSON/report bytes preserved. Privacy/credential-pattern and tracked/untracked whitespace scans pass; git diff --check exits 0. HEAD/branch unchanged, index empty. No product file edited, cloud deployment/upload/session created, production/old-dev mutation, commit or push. Final decision remains RELEASE CANDIDATE — NO-GO; wait for the minimal packaging repair authorization.


### Wave 7 resumed — Minimal packaging repair and deployed RC validation

**RELEASE CANDIDATE — NO-GO.** The authorized packaging repair succeeded, a NEW dev engine was created, and core routing/session/browser checks passed. A healthy Networking current-evidence response exposed a distinct release-blocking goal/vision-to-current-benefit upgrade. No workflow repair was applied; stop optimization and wait for separate narrow repair authorization.

#### Exact repair and deployment

Only product-source edit this task: one extra_packages entry in deploy_dev.py, `agents/career/workflow/shared_evidence.py`. All other bytes of that file match entry after removing the exact added line. agent.py, shared_evidence.py, evidence.py, main.py, requirements.txt, all 30 instruction hashes/models, tools, callbacks, relationships, backend/frontend, default production ID and existing-engine configuration remain unchanged. Four historical diagnostic tests now normalize only this exact measured deployment-file append before checking prior hashes; their initial expected hash failures and successful reruns are retained.

Called the repaired create-only deployment helper once. Invocation-only configuration used the requested Final Dev RC display name and added an unchanged source requirements.txt copy to the archive to satisfy byte-parity auditing; the helper source itself received no additional edit. The SDK independently stages generated runtime requirements. No deployment helper, diagnostic, .env, credential or unrelated source was included in the archive.

New engine: **932407850586603520**. Resource: `projects/717132085388/locations/us-west1/reasoningEngines/932407850586603520`. Display: **Career & Professional Orchestration Agent - Final Dev RC**. Created `2026-10-23T20:00:46.298162Z`; provisioning took 157.715s. Project cosc-490, region us-west1. Staging: `gs://cosc-490-agent-staging-20261021-a41c7e9b/career-source-dev-v4-1c1060c9113a433ba3462b274eb30c4f/`.

Runtime: Python 3.13 / google-adk; direct dependencies remain google-cloud-aiplatform[agent_engines,adk]==1.165.1 and google-adk==2.12.0. SDK-generated runtime requirements additionally pin cloudpickle==3.1.2 and pydantic==2.14.1 for serialization. These SDK additions are not source requirement edits. The source requirements file inside the archive is byte-identical to local. Cloud Resource Manager service-disabled lookup/telemetry warnings occurred, but creation and queries continued; no service or IAM change was made.

#### Archive/import/source parity

Actual pinned SDK archive: agents/__init__.py, agents/career/__init__.py, and workflow/__init__.py, agent.py, evidence.py, shared_evidence.py, main.py, requirements.txt. Clean isolated process imported both main.app and agent.root_agent successfully and found nine specialists. Only the three newly created staging objects in this invocation prefix were inspected: pickle, dependencies archive, generated runtime requirements. No unrelated bucket objects were read.

| Source file | Local and uploaded SHA-256 (equal) |
| --- | --- |
| agents/career/workflow/agent.py | `abf498103233bf3b52d132cc159602694d09ae6a0cecaed1e29123e21d05fee4` |
| agents/career/workflow/evidence.py | `140dd5a5e758c7a5cbc051019cf16314f2959e8ffc6a4f451928c97b9192780c` |
| agents/career/workflow/shared_evidence.py | `d1b71f8765056383ed82d2363cdb3c14720796ac931abed220bdfc151fce7123` |
| agents/career/workflow/main.py | `bf7ac92680c85ef587d03d246330428cc45863201b00a891285ca075ae3d05f6` |
| agents/career/workflow/requirements.txt | `02a5f474eaadd6d3277c5323c6353f9462f7118c18bdbdcf16642d5c064cb720` |

#### Remote smoke and nine-specialist routing

First diagnostic smoke incorrectly parsed the managed-session operation envelope instead of response.name. It failed before routing and is preserved as DIAGNOSTIC_PROTOCOL_ERROR, not a product/capacity failure. The existing backend already parses response.name correctly; only the diagnostic client changed. Corrected smoke created a fresh session in 1.035s and completed Career query in 28.951s (29.987s including session creation, excluding separate credential-client initialization), with no observed Search/URL calls or runtime errors. No failed provider case was automatically retried.

| Specialist | First route | Query s | Stable Search / observed URL | Result |
| --- | --- | ---: | --- | --- |
| career_exploration_agent | Correct | 28.951 | 0 / 0 | PASS |
| internship__job_preparation_agent | Correct | 23.621 | 0 / 0 | PASS |
| resume__portfolio_agent | Correct | 24.594 | 0 / 0 | PASS |
| interview_preparation_agent | Correct | 21.484 | 0 / 0 | PASS |
| networking__professional_communication_agent | Correct | 13.813 | 0 / 0 | PASS |
| skill_gap__career_roadmap_agent | Correct | 27.558 | 0 / 0 | PASS |
| research__graduate_pathways_agent | Correct | 20.723 | 0 / 0 | PASS |
| certification__technical_development_agent | Correct | 25.701 | 0 / 0 | SPECIALIST_CAPACITY 429 after correct transfer |
| trust__human_escalation_agent | Correct | 2.985 | 0 / 0 | PASS |

All nine first specialist routes matched; eight stable answers completed, Certification stable stopped after specialist 429. Stable batch stopped immediately. Later health-gated batches did not retry that failed Certification case. Networking stable and both later health probes were useful and omitted unsupported exact LinkedIn/platform limits. Generic templates still require factual personalization before use.

#### Current-evidence spot checks and provider incidents

After cooldown, a Networking no-tool probe passed in 11.151s; Trust human escalation then passed in 2.985s, preserving UNRESOLVED and recommending human review without contacting anyone. Career current then received ROOT_CAPACITY 429 in 1.391s before transfer; that batch stopped immediately. After successful Flask/UI tests, one final lightweight health probe passed in 16.128s before the remaining evidence checks.

| Current case | Result |
| --- | --- |
| career | PROVIDER_CAPACITY; no reliability verdict |
| networking | RELIABILITY_FAILURE: goals/vision treated as verified current benefits |
| certification | Stopped on capacity, then a genuine evidence reliability defect; no more inference. |
| interview | Stopped on capacity, then a genuine evidence reliability defect; no more inference. |
| trust | Bounded clarification; UNRESOLVED retained. One Search call despite missing source pair; no broad loop or invented resolution. |
| research | Stopped on capacity, then a genuine evidence reliability defect; no more inference. |
| networking_platform | Stopped on capacity, then a genuine evidence reliability defect; no more inference. |

Trust current completed in 71.325s with one bounded Search, then requested the missing source pair and retained UNRESOLVED. The lookup was low-value given missing context, but did not create a broad loop or invented resolution; no optimization was made for this latency limitation. Networking current completed in 74.977s with one observed Search and two deterministic verification calls. Nested URL helper timing/count and grounding query totals are not fully exposed by outer SSE; an observed zero URL-helper call count must not be read as no internal URL verification. All remote request/session/transfer/first-text timings and public event text are retained without raw user/session identifiers.

**Two provider-capacity incidents:** Certification stable SPECIALIST_CAPACITY and Career current ROOT_CAPACITY. Each stopped its batch. No capacity error is treated as an architecture defect. After the Networking reliability defect below, all further inference stopped; Certification/Interview/Research current and live LinkedIn exact-limit lookup remained deferred. Offline exact-platform current retrieval still activates Search+URL verification and fails closed on unsupported facts.

#### Exact release-blocking reliability defect

Networking C1 labels the combined SACS membership, mentoring, technical-workshop and networking-benefit claim **VERIFIED CURRENT** and describes its scope as fully supported. The exact returned grounding citation was followed successfully (HTTP 200) to https://www.morgan.edu/computer-science/current-students/sacs. That official page invites membership, but places the mentoring/workshop benefits under goals/vision. Membership access is supported; the whole bundle of currently delivered benefits is not established by those goals. The response’s own assessment relies on that goal language without narrowing scope or stating the missing current-delivery evidence. This is unsupported current-status promotion, not proof the club or benefits do not exist. C2 correctly remained UNSUPPORTED; no transport/URL-byte mismatch was observed.

The internal verifier date/cycle field is not exposed in the outer response and temporary registry state is intentionally not persisted. Do not fabricate its value or attribute this failure to a specific date string. The observed issue is the rendered supported_scope/why against the cited source. Exact path to inspect: shared_evidence.py EvidencePolicy.store (current-claim acceptance) and Networking URL Context verifier contract; render() propagates the accepted status. **Minimal repair scope:** retain the supported membership subclaim, mark goal-based operational benefits CURRENT STATUS UNVERIFIED until explicitly supported, and add a captured-case regression. No broad prompt/model/tool/graph redesign. This is outside the one-file packaging repair authorization, so no repair was applied.

#### Flask, managed sessions and browser

Dedicated unchanged Flask application runs at http://localhost:5002/agents/career, with startup explicitly selecting CAREER_REASONING_ENGINE_ID=932407850586603520. The pre-existing port-5001 app/tab was not repointed or stopped. Flask API fresh/same-session/different-user requests all returned HTTP 200. Same-user follow-up retained the managed session and mapped “those paths” to the earlier cloud/risk discussion. A different synthetic user received a different session and explicitly acknowledged no prior discussion. Malformed requests retained 400/413 validation.

Browser: welcome/input/thinking/busy controls, Enter send, Shift+Enter newline, counter, autogrow (76px to 240px cap), timestamps, Copy→Copied and scroll-latest passed. Markdown rendered one actual table, two headings and fourteen strong elements. Both CDN scripts loaded without console errors; unchanged renderMarkdown uses DOMPurify.sanitize(marked.parse()). No malicious payload or artificial provider failure was injected. No natural browser failure occurred: Retry/error textContent branch was inspected unchanged but not exercised live.

Refresh resets the visible transcript to welcome (existing behavior), but retains user/session identity: a follow-up without restating background correctly recalled IT risk management. Server audit confirms same user and same managed session. New Chat cleared visible content and the next message omitted the prior session, returned a different managed session for the same user, and correctly said no experience had been shared in that chat. No raw user/session IDs were written to artifacts; only equality/reset booleans and synthetic-user ordinal groups are stored. Dedicated dev tab/server remain available for inspection; this does not promote production.

#### Latency, offline checks and final decision

Completed stable query timings range from 2.985s (Trust) to 28.951s (Career): healthy observations, not an SLA or percentile estimate. Completed current Trust/Networking at 71.325/74.977s are SLOW BUT FUNCTIONAL in transport terms; Networking still fails reliability. Capacity failures and the diagnostic-envelope mistake are excluded from normal latency summaries. Flask auth/session/stream/total timings and API/browser request totals are recorded in the audit; no new SLA.

Full repaired offline suite: **142 passed + one known stale Career 501 failure** (74 pytest passes/one stale failure; 68 ADK unittest passes). Initial historical hash failures were due only to the authorized deployment entry; strict normalization checks its exact preimage and rejects any additional change. Existing JSON/history remained immutable. The obsolete 501 test sees the integrated route’s 503 under blocked authentication; it is separate from this genuine evidence failure. Syntax/import, all 30 instruction/model hashes, protected source and staged-byte parity pass; final rerun/privacy/whitespace results are recorded below.

**RELEASE CANDIDATE — NO-GO.** Packaging, deployment, routing, session isolation/continuity, New Chat and healthy browser flows are demonstrated. Networking’s current evidence promotion remains release-blocking. Stop optimization here; wait for separate authorization for only that narrow evidence-adjudication repair and regression. Preserve this new dev engine as observed; do not promote, update/delete production or old dev engines, stage, commit, push or merge.

Final resumed-Wave-7 validation PASS for mechanics/parity only: complete post-testing suite again **142 passed + one known stale failure**; syntax for 43 workflow/test files, local runtime import, all 30 instruction/model hashes, protected source hashes, actual staged-byte parity for all five requested files, previous JSON/report-prefix preservation, privacy/credential-pattern and tracked/untracked whitespace checks pass. git diff --check exits 0; branch/HEAD unchanged, index empty. Only this task’s product-source edit is the single deploy_dev.py package entry. New engine 932407850586603520 remains available; production/old dev engines/default fallback untouched. No further inference or workflow repairs after the observed Networking evidence defect. Nothing staged, committed, pushed or promoted. **RELEASE CANDIDATE — NO-GO**; wait for separate authorization for the narrow Networking evidence-adjudication repair.

### Networking current-delivery reliability repair and RC2 acceptance (2026-10-23)

**RELEASE CANDIDATE — NO-GO**

This is the single authorized reliability repair, not another optimization wave.
- Root cause: a helper summary/currentness flag could upgrade SACS stated goals/vision to verified delivery of mentoring/workshops. Whole-claim support obscured narrower membership evidence.
- Product change: `shared_evidence.py` only. Networking requires direct operational page evidence for each recognized benefit category; goals, mission, vision, future/negative and mismatched-year clauses cannot prove delivery. Existing authority/date/readability gates still apply. Narrow literal membership/existence and directly supported benefit scope remain visible without upgrading the compound claim.
- No prompt, model, tool, agent name, callback assignment, graph, other specialist, evidence.py, backend, frontend, dependency or deployment-helper changes in this repair. Shared base store/render branches are Networking-gated; Research outputs compare equal to the original implementation.
- Fixture provenance: Exact public claim and assessment from Wave 7 rc_networking_current C1. Raw helper JSON was not retained. Below verifier transport fields are an explicit adversarial test construction, not claimed to be the original hidden payload. Evidence text paraphrases the captured source review/user-supplied defect description; no live web access.
- Captured-case adversarial regression: old implementation VERIFIED CURRENT; repaired CURRENT STATUS UNVERIFIED. Literal invitation to join SACS survives as narrower support.
- All 17 new regression methods pass, including 11 aspirational wording subcases, historical 2024 workshops, goal headings, misleading goal-prefix/current assertion, compound partial evidence, explicit Fall 2026 registration, normal evidence gates, actual ADK mocked Search/URL flow, stable boundary, and non-Networking equivalence.
- Full offline suite: 159 pass (74 pytest +85 ADK unittest); one known stale Career HTTP 501 expectation fails against implemented/auth-blocked HTTP 503. No additional failures.
- Existing Career, Research, Certification, Interview official/anecdotal, and Trust conflict regressions pass.
- Shared SHA-256 before: `d1b71f8765056383ed82d2363cdb3c14720796ac931abed220bdfc151fce7123`.
- Shared SHA-256 after: `d38f5604d2717ffc6d0a68d20bc0b428554759e5a38e77b5103796b323cc5b03`.
- All 30 instruction/model hashes and protected unrelated source bytes match entry. Networking instruction remains `b512838305e558ecfd6a39b067fff900fbd01f9417aa57ddef5dc318999d0226`. Root retains nine specialists; models remain gemini-3.5-flash.
- Local live Networking: stable correct route/0 Search/0 URL, useful recruiter coaching without platform limits; current completed/1 Search/2 URL and SACS benefits CURRENT STATUS UNVERIFIED.
- One initial local diagnostic invocation completed its model work but failed while saving because of a wrong expected-field name. Corrected invocation saved both local cases; no product issue.
- RC2 engine: `6244403611070103552`; resource `projects/717132085388/locations/us-west1/reasoningEngines/6244403611070103552`; display **Career & Professional Orchestration Agent - Final Dev RC2**; creation 168.531 seconds.
- Existing create-only helper used unchanged; invocation sets RC2 display and archives original requirements.txt, as for RC1. Staged agent/evidence/shared/main/requirements bytes all match local. No pickle was downloaded or unpickled.
- SDK Cloud Resource Manager API-disabled warning occurred; creation continued successfully. No APIs or IAM changed.
- RC2 Networking current discovery hit provider 429 (TOOL_CAPACITY). Live batch stopped immediately; no retry, Career/Trust current and Flask inference deferred. Provider capacity is not classified as an architecture/evidence failure. Local Networking current and offline evidence regressions remain passing, but complete RC2 acceptance is not established.

| RC2 check | Result | Search | Verification calls | Query seconds |
|---|---|---:|---:|---:|
| rc_career_stable | completed; route True | 0 | 0 | 24.544 |
| rc_networking_stable | completed; route True | 0 | 0 | 54.451 |
| rc_networking_current | runtime_error; route True | 1 | 0 | 41.804 |

Remote counts show outer SSE calls only. Nested URL Context/provider work is not fully exposed; a verification call is not zero retrieval.

- Flask RC2 acceptance at localhost:5003: DEFERRED — server initialized with correct RC2 selection, but no fresh/followup/New Chat model calls made after the 429. Previous RC1 session/browser checks remain passing; RC2-specific session acceptance remains untested.
- Previous Wave 7 routing/browser controls remain inherited: changed evidence adjudication cannot alter those frontend controls. No redundant full browser/routing sweep.
- Production `3463694723959488512`, old RC `932407850586603520`, all other existing dev engines, and production fallback remain untouched. No stage, commit, push, promotion or engine deletion.
- Syntax/import, instruction/source/staged parity and privacy pass. Final whitespace/status checks are recorded in the final validation artifact.

Release remains blocked pending missing acceptance checks.
Resume only the outstanding minimum live acceptance checks in a healthy provider window; no further optimization or production promotion.

### RC2 Acceptance Completion

**RELEASE CANDIDATE — PASS** under the explicitly revised provider-capacity exception.

**ACCEPTANCE INCOMPLETE DUE TO PROVIDER CAPACITY.** This decision does not represent deferred RC2 checks as completed. The only previously observed reliability blocker is fixed remotely, every healthy completed release-critical check passes, and the remaining gaps follow the required immediate stop after a provider 429. Prior RC1 routing/browser/session evidence remains valid for unchanged code.

- Existing RC2 only: `6244403611070103552`, `projects/717132085388/locations/us-west1/reasoningEngines/6244403611070103552`, **Career & Professional Orchestration Agent - Final Dev RC2**. No redeploy, update, RC3 or new engine.
- Provider health: PASS. Exact recruiter-introduction prompt routed to Networking, completed normally in 28.932 query seconds, with zero Search/URL Context/verification calls.
- Networking current: PASS, completed in 81.570 query seconds. One Search and two deterministic verification calls. Nested URL Context counts are not fully exposed in outer SSE. SACS remains `CURRENT STATUS UNVERIFIED`; literal membership invitation is preserved as narrower scope, without upgrading networking benefits. The second Career Development/Handshake claim also remains unverified. No asserted active mentoring, workshops, recruiter access or partnerships were invented.
- Career current: provider 429 before routing, classified `ROOT_CAPACITY`, after 1.603 query seconds. No evidence-integrity verdict can be assigned to an incomplete response. Live batch stopped immediately without retry.
- Trust current: deferred after that 429; no new inference attempted. Offline Trust conflict regressions pass.
- Flask: dedicated server started on requested port 5001 with `CAREER_REASONING_ENGINE_ID=6244403611070103552`; startup assertion confirms selection. Replaced the confirmed prior repository stdin-Python local server occupying that port. No persistent environment/backend/frontend configuration changes. RC2 server remains available locally.
- Fresh managed session, same-session continuity and different-user isolation: deferred after 429; do not label these RC2 checks PASS. Prior RC1 session tests remain passing and the affected backend/session code is byte unchanged.
- New Chat/browser: no RC2 message submissions after 429. RC1 send/thinking/Markdown/refresh/reset checks remain inherited; no new RC2 New Chat or browser-flow result is claimed. Error/Retry branch is unchanged. Only the existing RC1 browser tab was inspected; no browser test messages were sent.
- SACS blocker: fixed offline and in a completed healthy RC2 current-resource answer. Evidence integrity passes for that completed answer and the deterministic evidence suite; no new healthy completed run reproduced a release-blocking defect.
- Final offline suite: **159 pass** (74 pytest +85 ADK unittest); **one known stale failure**, Career endpoint expecting HTTP 501 instead of implemented/auth-blocked HTTP 503. All 17 new Networking regressions and unrelated evidence regressions pass.
- Syntax/import, source parity, all 30 instruction/model hashes, callbacks/tools/relationships and privacy checks pass. Product source, RC2 deployment and production fallback are unchanged. `git diff --check` and new-artifact whitespace checks pass.
- Changes this acceptance run are diagnostic scripts/results and this report append only. No prompts, models, adjudication, backend, frontend, requirements or deployment helper changed.
- Production `3463694723959488512` and all existing old RC/dev engines remain untouched. Nothing staged, committed or pushed.

Career workflow optimization is complete.

Recommended next actions only: commit completed Wave 1–7 work; optionally push the branch; production promotion later as a separate explicit task. Stop optimization here.
