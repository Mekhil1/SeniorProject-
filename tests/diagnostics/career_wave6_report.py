"""Offline aggregation and reviewed Wave 6 scorecard; never makes API calls."""
import json
from pathlib import Path
import statistics
from career_wave6 import ROOT,OUT,MANIFEST,verify


LABELS=['Career Exploration','Internship & Job Preparation','Resume & Portfolio','Interview Preparation',
        'Networking & Professional Communication','Skill Gap & Career Roadmap','Research & Graduate Pathways',
        'Certification & Technical Development','Trust & Human Escalation']
KEYS=['career','internship','resume','interview','networking','roadmap','research','certification','trust']
BASE_CONCERNS=[
    'Bounded reference; freshness did not establish specific current benefits/funding.',
    'Stable over-retrieval; current openings/eligibility asserted before intake without final citations.',
    'Stable over-retrieval; current market claims without a defined posting sample or final citations.',
    'No completed employer-process current answer; named-company attempt censored at 240.017s.',
    'Six current Search helpers; unsupported active partnerships/access and incomplete current verification.',
    'Stable over-retrieval; current original off-scope; clarified market claims lacked a defined sample/citations.',
    'Stable routing overlap; eight current helpers; unsupported openings/funding/eligibility.',
    'Stable vendor/policy leakage; no completed local current version/price answer.',
    'Human escalation sometimes searched; invented conflict context and unverified program activity.']
CONTRACTS=[
    'Existing Career registry/status/budget/Runner tests pass; current live confirmation deferred.',
    'Stable fast path and current tool plumbing pass offline; real current openings/eligibility not assessed.',
    'Stable fast path and current tool plumbing pass offline; real current-market evidence not assessed.',
    'Official/anecdotal separation, bounded verification and stable Runner contracts pass offline; current live deferred.',
    'Current deterministic statuses and bounded verification pass offline; stable unsupported platform limit recurs live.',
    'Stable fast path and current tool plumbing pass offline; real frequency claims not assessed.',
    'Current status/funding boundaries pass offline; no Wave 6 healthy stable/current sample.',
    'Per-fact exam/version/price and stable vendor boundary tests pass offline; Wave 6 live deferred.',
    'Immediate escalation, conflict clarification and supplied-pair bounded adjudication pass offline; Wave 6 live deferred.']


def stats(rows):
    xs=[r['total_seconds'] for r in rows if r['status']=='completed' and not r.get('errors') and r['route_match']]
    return dict(n=len(xs),minimum=min(xs) if xs else None,median=statistics.median(xs) if xs else None,
                maximum=max(xs) if xs else None,samples=xs)


def compact(r,artifact):
    return {k:r[k] for k in ('id','status','mode','total_seconds','actual_specialist','route_match',
                            'search_helper_invocations','search_queries_reported','url_context_invocations')}|{'artifact':artifact}


def main():
    verify()
    d=json.loads(OUT.read_text(encoding='utf8'))
    originals=[]
    for name in ('career_baseline.json','career_baseline_followup.json'):
        for r in json.loads((ROOT/'tests/diagnostics'/name).read_text(encoding='utf8'))['runs']:
            originals.append(compact(r,name))
    for r in d['runs']:
        if r['status']!='completed':continue
        notes=[]
        if r['id']=='wave6_networking_stable_1':
            verdict='RELIABILITY_FAILURE'
            notes=['Asserts "LinkedIn Connection Request: Needs to be extremely short (under 300 characters)." '
                   'No user-supplied limit, Search, URL Context or supporting source. Treat as unsupported platform policy, '
                   'not as an independently disproven numeric limit. Same symptom documented in Wave 2 stable review. '
                   'General outreach coaching and routing are otherwise appropriate.']
        elif r['id'].startswith('wave6_health_'):
            verdict='HEALTH_GATE_PASS_WITH_QUALITY_NOTE'
            notes=['Correct Networking route; zero retrieval; normal completion. An illustrative template still uses '
                   '"Summer 2025 internships" at a 2026 checkpoint. This is stale example wording, not proof of a current opening.']
        else:
            verdict='PASS_OBSERVED_STABLE_SCOPE'
            notes=['Correct specialist; zero retrieval; general conceptual guidance/intake. No named current opening, '
                   'price, active partnership, funding or verified employer-process assertion observed. '
                   'Not a certification of every generic career recommendation.']
        r['reliability_verdict']=verdict;r['manual_review']=notes
    attempted={r['id'] for r in d['runs']}
    d['deferred_cases']=[dict(id=c['id'],batch=batch['batch'],domain=c['domain'],mode=c['mode'],
         reason='Stopped after ROOT_CAPACITY 429; no retry or later batch was run.')
         for batch in d['plan'] for c in batch['cases'] if c['id'] not in attempted]
    score=[]
    for key,label,before,contracts in zip(KEYS,LABELS,BASE_CONCERNS,CONTRACTS):
        old=[r for r in originals if r['id'].startswith(key+'_')]
        oldstable=[r for r in old if r['mode'] in ('stable','human')]
        oldcurrent=[r for r in old if r['mode'] not in ('stable','human','stable_probe')]
        new=[r for r in d['runs'] if r['domain']==key and not r['id'].startswith('wave6_health_')]
        stable=[r for r in new if r['mode'] in ('stable','human')]
        current=[r for r in new if r['mode'] not in ('stable','human')]
        s=stats(stable);bs=stats(oldstable)
        priority='P0' if key=='networking' else 'P3' if key=='career' else 'P1'
        score.append(dict(domain=key,label=label,priority=priority,
            priority_reason='Unsupported platform-specific current constraint recurs on no-retrieval stable path; fails explicit Wave 7 claim gate.' if key=='networking' else
                'Stable/evidence contracts intact; no observed deployment-blocking defect in established Career scope.' if key=='career' else
                'Deployable only with documented live-coverage/current-evidence limitations; no demonstrated structural defect.',
            original_stable=oldstable,original_current=oldcurrent,original_correct_route_stable_statistics=bs,
            final_stable_statistics=s,final_current=current,
            stable_median_delta_seconds=round(s['median']-bs['median'],3) if s['n'] and bs['n'] else None,
            stable_observed_reduction_percent=round(100*(bs['median']-s['median'])/bs['median'],2) if s['n'] and bs['n'] else None,
            stable_search_before=[r['search_helper_invocations'] for r in oldstable if r['status']=='completed' and r['route_match']],
            stable_search_after=[r['search_helper_invocations'] for r in stable if r['status']=='completed'],
            current_search_before=[r['search_helper_invocations'] for r in oldcurrent],current_search_after=None,
            current_result='NOT ATTEMPTED — PROVIDER CAPACITY STOP',reliability_before=before,
            reliability_after='FAIL: unsupported LinkedIn numeric policy on stable path' if key=='networking' else
                'PASS observed stable scope; current unassessed' if s['n'] else 'LIVE UNASSESSED; offline contracts pass',
            offline_contracts=contracts))
    d['specialist_scorecard']=score
    d['summary']=dict(total_attempts=len(d['runs']),completed_runs=sum(r['status']=='completed' for r in d['runs']),
        completed_benchmark_runs=sum(r['status']=='completed' and not r['id'].startswith('wave6_health_') for r in d['runs']),
        health_attempts=sum(r['id'].startswith('wave6_health_') for r in d['runs']),
        capacity_failed_attempts=sum(any(e.get('code')=='429' for e in r['errors']) for r in d['runs']),
        current_attempts=0,search_helpers=sum(r['search_helper_invocations'] for r in d['runs']),
        url_helpers=sum(r['url_context_invocations'] for r in d['runs']),
        deterministic_verifications=sum(r['deterministic_verification_count'] for r in d['runs']),
        provider_health='HEALTHY INITIAL PROBE; PROVIDER_UNHEALTHY at Research root request',
        live_coverage='INCOMPLETE DUE TO PROVIDER CAPACITY',remaining_p0=['networking'],
        remaining_p1=[r['domain'] for r in score if r['priority']=='P1'],
        structural_architecture_defects_demonstrated=[],
        reliability_defects=['Recurring unsupported platform-specific numeric limit on Networking stable path'],
        wave7_decision='NO-GO — ARCHITECTURE DEFECT REMAINS',
        decision_interpretation='Requested NO-GO label applies to output-reliability enforcement, not a demonstrated graph, routing or registry defect. '
            'Capacity alone is not the blocker. No patch in this measurement wave.',
        latency_causation='Not established: one healthy sample per measured specialist, ordered runs, SDK warming, response-length/provider variance; no current sample.',
        no_deployment=True,nothing_staged_committed_pushed=True)
    d['offline_validation']={x:json.loads((ROOT/f'tests/diagnostics/career_wave6_offline_{x}.json').read_text(encoding='utf8')) for x in ('pytest','adk')}
    d['offline_validation']['combined']=dict(passed=123,known_stale_failed=1,
        stale_test='tests/test_agents.py::test_agent_starter_endpoint[career]: obsolete 501 expectation; auth-blocked integrated service returns 503.',
        diagnostic_correction='Initial ADK guard blocked Windows asyncio loopback: 32 passed/31 diagnostic errors. '
            'Preserved in career_wave6_offline_adk_initial.json; corrected external-only guard rerun: all 63 passed. No product edit.')
    d['source_validation']=json.loads((ROOT/'tests/diagnostics/career_wave6_validation.json').read_text(encoding='utf8'))
    d['source_hashes']=json.loads(MANIFEST.read_text(encoding='utf8'))['protected_files']
    OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
    assert b'## Wave 6 ' not in report.read_bytes(),'Never duplicate/overwrite report section.'
    lines=['','', '## Wave 6 — Final Workflow Benchmark','',
      '**Decision: NO-GO — ARCHITECTURE DEFECT REMAINS.** The blocker is a recurring output-reliability boundary failure in Networking, '
      'not an observed routing/graph/evidence-registry defect. Provider capacity independently prevents full live coverage. '
      'No optimization, product patch, deployment, staging, commit or push occurred.','',
      '### Method, source freeze and provider health','',
      'Captured all existing tracked files and untracked workflow product files before measurement in `career_wave6_parity.json`, '
      'along with prior diagnostic artifact hashes and the exact report-prefix byte count/hash. Reused the existing allowlisted local-source ADK runner '
      '(ADK 2.12.0 / Vertex SDK 1.165.1); fresh local session per request, normal root routing, project cosc-490/global model endpoint. '
      'No Agent Engine/Flask/browser endpoint was called. Timings exclude process imports and include runner setup; observer overhead is not isolated. '
      'First text is outer-runner public text, not model first-token latency. Raw hidden reasoning, credentials and session identifiers are not stored.','',
      'Plan: three stable rounds for all nine specialists, ten current cases including both Trust tests, and a fresh lightweight '
      'Networking no-tool probe before each batch. After the first round, current coverage was prioritized ahead of stable repeats; '
      'no attempted case or prompt changed. Samples were sequential with five seconds between successful requests. '
      'Health deadline 90s; other diagnostic deadlines 240s, not production timeouts. No automatic retry.','',
      'Initial probe passed in 32.289s with correct Networking routing and Search=URL=0. Six benchmark stable cases completed. '
      'The next Research-intent request failed at the root in 2.943s with 429 before transfer. Classification: '
      '**PROVIDER_CAPACITY / ROOT_CAPACITY; batch PROVIDER_UNHEALTHY**. All live calls stopped immediately. '
      'Eight attempts: seven completions including the probe, six benchmark completions, one capacity-failed attempt. '
      'Its four error records describe one failure, not four failed requests. No later health probe/retry/batch was run. '
      'All ten current cases, stable repeats, and first-round Certification/Trust were deferred. Research never dispatched.','',
      '### Nine-specialist scorecard and original baseline comparison','',
      'Baseline values below come from unchanged `career_baseline.json` and `career_baseline_followup.json`, matching the original '
      'report. `!` means failure/censoring; `[other route]` is not a specialist latency. Final min/median/max exclude failures '
      'and health probes. Each completed specialist has n=1: equal extrema are not a measured distribution. Historical readiness '
      'probes and prior-wave successes are not relabelled as Wave 6 samples.','',
      '| Specialist | Original stable seconds; Search | Final stable min / median / max (n); Search | Original current seconds; Search / URL | Final current | Reliability / priority |',
      '| --- | --- | --- | --- | --- | --- |']
    def oldfmt(rows):
        return '; '.join(f"{r['total_seconds']:.3f}{'!' if r['status']!='completed' else ''}{' [other route]' if r['actual_specialist'] and not r['route_match'] else ''}s H{r['search_helper_invocations']}/U{r['url_context_invocations']}" for r in rows)
    for row in score:
        s=row['final_stable_statistics']
        final=f"{s['minimum']:.3f} / {s['median']:.3f} / {s['maximum']:.3f} (1); H0/U0" if s['n'] else 'No healthy sample'
        lines.append(f"| {row['label']} | {oldfmt(row['original_stable'])} | {final} | {oldfmt(row['original_current'])} | Not attempted | {row['reliability_after']}; **{row['priority']}** |")
    lines += ['', 'Certification historical Flask ~165s is context only; the local original attempts failed at 0.803s and 91.939s '
      '(0 and 3 Search helpers), so there is no completed local current latency baseline for that domain. Interview current '
      'Microsoft wording differs from the Google/generic baseline; Research current removes graduate opportunities; Resume/Roadmap wording '
      'also follows the requested canaries rather than forcing identical original prompts. No current pre/post comparison is available.','',
      '### Observed latency and retrieval changes','',
      '| Specialist | Original healthy correctly routed stable median (s) | Wave 6 (s, n=1) | Observed reduction | Search before → after |',
      '| --- | ---: | ---: | ---: | --- |']
    for row in score:
        if not row['final_stable_statistics']['n']:continue
        lines.append(f"| {row['label']} | {row['original_correct_route_stable_statistics']['median']:.3f} | {row['final_stable_statistics']['median']:.3f} | {row['stable_observed_reduction_percent']:.2f}% | {row['stable_search_before']} → {row['stable_search_after']} |")
    lines += ['', 'These six single observations are below their original healthy stable medians. They do **not** establish causal speedups, '
      'typical latency, tail latency or an SLA. Root SDK warming, output length/intake versus full-plan responses, ordering and provider variation '
      'confound the comparison. Roadmap now gives a capability outline plus intake rather than a complete personalized year plan. '
      'No current-path latency, verification success or live retrieval reduction was measured in Wave 6. '
      'All observed requests—including the probe and failed root request—had zero Search, grounding queries, URL helpers and deterministic verifications. '
      'Stable Internship/Resume/Roadmap over-retrieval was absent in their completed samples.','',
      '### Per-attempt timing and reliability review','',
      '| Run | First root event | Transfer | First specialist event | First public text | Total s | Result |',
      '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in d['runs']:
        t=r['wait_diagnosis']['timeline'];transfer=r['first_transfer']
        def f(x):return '—' if x is None else f'{x:.3f}'
        lines.append(f"| {r['id']} | {f(t['first_root_event'])} | {f(transfer['t'] if transfer else None)} | {f(r['first_specialist_event'])} | {f(r['first_text'])} | {r['total_seconds']:.3f} | {r['reliability_verdict']} |")
    lines += ['', 'Each structured run additionally retains request-start UTC, relative time zero, routed specialist, observed queries, '
      'helper/verification counts, public final text, model/helper spans and capacity classification. A first specialist event may be '
      'a state-only event or the final response; it is distinct from the recorded specialist model request start. Failed-root runtime '
      'is excluded from normal latency summaries.','',
      '**Networking reliability failure (P0 under the requested deployment gate):** completed `wave6_networking_stable_1` states '
      '“LinkedIn Connection Request: Needs to be extremely short (under 300 characters).” No platform limit was provided by the user '
      'and the run retrieved nothing. This is an unverified external platform constraint presented as an operational requirement, '
      'not merely a suggested personal word budget. Its truth/falsity across plans was not independently tested; the issue is unsupported '
      'specificity. The same symptom is already documented in Wave 2 stable quality review. Thus this is reproducible across retained '
      'observations, not inferred from the capacity failure or blamed on compression. Current institutional partnerships/access were not '
      'tested here. No prompt patch was made. Useful generic coaching, correct routing and zero Search do not erase the factual boundary failure.','',
      'The health probe also contains “Summer 2025 internships” inside an adaptable example at a 2026 checkpoint. Record this as **P2 stale '
      'example wording**, not as a proven currently open opportunity. Its health gate still passed: route, no tools and completion. '
      'Other healthy benchmark answers provided general conceptual guidance/intake without observed named current opening, price, '
      'partnership, funding or verified employer-process claims. This limited review is not a guarantee for untested current answers.','',
      '### Evidence, routing, Trust and specialist limitations','']
    for row in score:
        lines.append(f"- **{row['label']} ({row['priority']}):** {row['offline_contracts']} Baseline concern: {row['reliability_before']}")
    lines += ['', 'All six completed benchmark routes matched their expected specialist. Research has no route verdict because capacity failed '
      'before transfer; do not classify it as wrong routing. Trust human/conflict/source-pair cases passed offline only. '
      'Deterministic status preservation, discovery/verification caps, exact candidate transport and final rendering remain intact offline; '
      'no healthy Wave 6 current run establishes live evidence quality. Internship/Resume/Roadmap raw-tool current paths remain '
      'model-dependent and require healthy current evidence review before claiming those baseline factual defects are resolved.','',
      '### Offline validation, parity and diagnostic correction','',
      '**123 passed; one known stale failure.** Full existing suite split across its existing environments: repository pytest '
      '**60 passed / 1 failed**, pinned ADK unittest **63 passed / 0 failed**. Known stale '
      '`tests/test_agents.py::test_agent_starter_endpoint[career]` expects the removed HTTP 501 stub; the integrated endpoint '
      'returns 503 under the offline auth block. No backend test was repaired. External sockets/auth were blocked for offline tests.','',
      'Initial ADK diagnostic run had 32 passes and 31 errors because blocking all socket connects also broke Windows asyncio’s '
      'loopback self-pipe. Preserved that result in `career_wave6_offline_adk_initial.json`; changed only the diagnostic guard '
      'to allow loopback, with external access still blocked, and reran all 63 successfully. This was a harness error, not a workflow regression.','',
      'All 30 runtime-loaded instruction SHA-256 hashes/counts match Wave 5; all models and nine root specialist names match. '
      'Python syntax/import validation passed. Product file hashes protect tools, routing, graph, registries, backend/frontend '
      'and deployment configuration unchanged. Prior diagnostics and all pre-Wave 6 report bytes are preserved. '
      'Final privacy/whitespace/Git checks are recorded below after aggregation. No dependencies changed.','',
      '### Final priority and Wave 7 decision','',
      '**P0:** Networking output reliability: recurring unsupported platform-specific policy on a stable no-retrieval path. '
      '**P1:** Internship, Resume, Interview, Roadmap, Research, Certification and Trust: documented live/current-coverage limitations; '
      'no demonstrated new structural defect. **P2:** Networking example date quality (secondary to its P0 gate failure). '
      '**P3:** Career within its established tested scope, with current live revalidation still deferred. '
      'Provider availability is a separate limitation, not automatically P0.','',
      '**NO-GO — ARCHITECTURE DEFECT REMAINS.** This required decision label refers to the unresolved workflow output-reliability '
      'enforcement boundary; no graph/registry/routing architecture failure was demonstrated. GO’s “no reliability defect in healthy '
      'completed runs” condition was not met. Capacity gaps alone would not force NO-GO, but the observed unsupported claim does. '
      'Record a separate authorized fix/revalidation task before reconsidering Wave 7; this measurement wave made no fixes or deployment.','',
      'Artifacts: `tests/diagnostics/career_wave6_final.json`, `career_wave6_parity.json`, `career_wave6_validation.json`, '
      '`career_wave6_offline_pytest.json`, `career_wave6_offline_adk.json`, preserved initial ADK result, and opt-in measurement/offline/report drivers. '
      'Existing diagnostics and runtime source were not edited. Nothing staged, committed, pushed or deployed.','']
    with report.open('ab') as f:f.write(('\r\n'.join(lines)).encode('utf8'))
    verify()
    print(json.dumps(d['summary'],ensure_ascii=True,indent=2))


if __name__=='__main__':main()
