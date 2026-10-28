"""Summarize the deployed dev RC without changing its source or cloud resources."""
import json
from career_wave7_resume import BASE,ROOT,verify


def main():
    verify()
    def read(name):return json.loads((BASE/name).read_text(encoding='utf8'))
    deployment=read('career_wave7_rc_deployment.json');remote=read('career_wave7_rc_remote.json')
    staged=read('career_wave7_rc_staged.json');api=read('career_wave7_rc_flask_checks.json')
    ui=read('career_wave7_rc_browser.json');audit=read('career_wave7_rc_flask_audit.json')
    reliability=read('career_wave7_rc_reliability.json');validation=read('career_wave7_rc_final_validation.json')
    runs=remote['runs'];lookup={r['id']:r for r in runs}
    assert reliability['decision']=='RELIABILITY_FAILURE'
    assert reliability['citation_http_status']==200
    assert reliability['resolved_source_url']==reliability['canonical_review_source']
    assert all(row['match'] for row in staged['byte_parity'].values())
    assert len([r for r in api['results'] if r['http_status']==200])==3
    assert next(r for r in api['results'] if r['case']=='followup')['same_session_retained']
    assert next(r for r in api['results'] if r['case']=='different_user')['separate_session']
    for r in runs:
        if r['id']=='diagnostic_career_session_envelope':r['review']='DIAGNOSTIC_PROTOCOL_ERROR; excluded from product verdict'
        elif r['capacity_failure']:r['review']='PROVIDER_CAPACITY; no reliability verdict'
        elif r['id']=='rc_networking_current':r['review']='RELIABILITY_FAILURE: goals/vision treated as verified current benefits'
        elif r['id']=='rc_trust_current':r['review']='Bounded clarification; UNRESOLVED retained. One Search call despite missing source pair; no broad loop or invented resolution.'
        else:r['review']='PASS observed route/stable scope; generic templates require factual personalization'
    (BASE/'career_wave7_rc_remote.json').write_text(json.dumps(remote,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    current={}
    for key in ('career','networking','certification','interview','trust','research','networking_platform'):
        r=lookup.get('rc_'+key+'_current')
        current[key]=dict(status=r['status'],review=r['review'],capacity_failure=r['capacity_failure']) if r else dict(status='DEFERRED',reason='Stopped on capacity, then a genuine evidence reliability defect; no more inference.')
    out=dict(decision='RELEASE CANDIDATE — NO-GO',deployment=deployment,packaging_repair='Exactly one shared_evidence.py entry added to deploy_dev.py extra_packages.',
        package_parity=staged,source_validation=validation,
        remote_summary=dict(attempts=len(runs),diagnostic_protocol_errors=1,completed=sum(r['status']=='completed' for r in runs),capacity_failed_attempts=sum(r['capacity_failure'] for r in runs),
            reliability_failed_completed_samples=1,stable_routes_correct=9,stable_answers_completed=8,
            observability='Outer SSE calls/timing only; nested URL Context/model/grounding work is not fully exposed. Networking current has 1 observed Search and 2 verification calls; do not call its nested URL workload zero.'),
        stable_matrix={c['domain']:dict(status=lookup[c['id']]['status'],routed=lookup[c['id']].get('actual_specialist'),route_match=lookup[c['id']].get('route_match'),query_seconds=lookup[c['id']].get('query_seconds'),search=lookup[c['id']]['search_helpers'],url_observed=lookup[c['id']]['url_helpers'],capacity=lookup[c['id']]['capacity_failure']) for c in remote['plan'] if c['mode'] in ('stable','human')},
        current_checks=current,flask=api,browser=ui,flask_observed_timings=audit['timings'],
        provider_failures=[dict(case=r['id'],classification=r['failure_class']) for r in runs if r['capacity_failure']],
        exact_release_blocker=reliability,minimal_repair_scope='Networking evidence adjudication/currentness acceptance only, with a captured-case regression. No repair applied; wait for separate authorization.',
        offline=dict(passed=142,known_stale_failed=1,pytest_passed=74,adk_unittest_passed=68),
        stale_test='Career HTTP 501 legacy expectation remains; auth-blocked implemented endpoint returns 503. Not the release blocker.',
        production_untouched=True,old_dev_engines_untouched=True,new_rc_preserved=True,production_fallback_unchanged=True,
        nothing_staged_committed_pushed=True,optimization_stopped=True)
    (BASE/'career_wave7_rc_final.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
    assert b'### Wave 7 resumed ' not in report.read_bytes()
    lines=['','','### Wave 7 resumed — Minimal packaging repair and deployed RC validation','',
        '**RELEASE CANDIDATE — NO-GO.** The authorized packaging repair succeeded, a NEW dev engine was created, and core '
        'routing/session/browser checks passed. A healthy Networking current-evidence response exposed a distinct release-blocking '
        'goal/vision-to-current-benefit upgrade. No workflow repair was applied; stop optimization and wait for separate narrow repair authorization.','',
        '#### Exact repair and deployment','',
        'Only product-source edit this task: one extra_packages entry in deploy_dev.py, `agents/career/workflow/shared_evidence.py`. '
        'All other bytes of that file match entry after removing the exact added line. agent.py, shared_evidence.py, evidence.py, main.py, '
        'requirements.txt, all 30 instruction hashes/models, tools, callbacks, relationships, backend/frontend, default production ID '
        'and existing-engine configuration remain unchanged. Four historical diagnostic tests now normalize only this exact measured '
        'deployment-file append before checking prior hashes; their initial expected hash failures and successful reruns are retained.','',
        'Called the repaired create-only deployment helper once. Invocation-only configuration used the requested Final Dev RC display '
        'name and added an unchanged source requirements.txt copy to the archive to satisfy byte-parity auditing; the helper source '
        'itself received no additional edit. The SDK independently stages generated runtime requirements. No deployment helper, '
        'diagnostic, .env, credential or unrelated source was included in the archive.','',
        f"New engine: **{deployment['engine_id']}**. Resource: `{deployment['resource_name']}`. Display: **{deployment['display_name']}**. "
        f"Created `{deployment['create_time']}`; provisioning took {deployment['create_seconds']:.3f}s. Project cosc-490, region us-west1. "
        f"Staging: `{deployment['staging_bucket']}/{deployment['staging_prefix']}/`.", '',
        'Runtime: Python 3.13 / google-adk; direct dependencies remain google-cloud-aiplatform[agent_engines,adk]==1.165.1 and '
        'google-adk==2.12.0. SDK-generated runtime requirements additionally pin cloudpickle==3.1.2 and pydantic==2.14.1 for serialization. '
        'These SDK additions are not source requirement edits. The source requirements file inside the archive is byte-identical to local. '
        'Cloud Resource Manager service-disabled lookup/telemetry warnings occurred, but creation and queries continued; no service or IAM change was made.','',
        '#### Archive/import/source parity','',
        'Actual pinned SDK archive: agents/__init__.py, agents/career/__init__.py, and workflow/__init__.py, agent.py, evidence.py, '
        'shared_evidence.py, main.py, requirements.txt. Clean isolated process imported both main.app and agent.root_agent successfully '
        'and found nine specialists. Only the three newly created staging objects in this invocation prefix were inspected: pickle, '
        'dependencies archive, generated runtime requirements. No unrelated bucket objects were read.','',
        '| Source file | Local and uploaded SHA-256 (equal) |','| --- | --- |']
    lines += [f"| {p} | `{r['local_sha256']}` |" for p,r in staged['byte_parity'].items()]
    lines += ['', '#### Remote smoke and nine-specialist routing','',
        'First diagnostic smoke incorrectly parsed the managed-session operation envelope instead of response.name. It failed before '
        'routing and is preserved as DIAGNOSTIC_PROTOCOL_ERROR, not a product/capacity failure. The existing backend already parses '
        'response.name correctly; only the diagnostic client changed. Corrected smoke created a fresh session in 1.035s and completed '
        'Career query in 28.951s (29.987s including session creation, excluding separate credential-client initialization), with no observed '
        'Search/URL calls or runtime errors. No failed provider case was automatically retried.','',
        '| Specialist | First route | Query s | Stable Search / observed URL | Result |',
        '| --- | --- | ---: | --- | --- |']
    for row in out['stable_matrix'].values():
        lines.append(f"| {row['routed']} | Correct | {row['query_seconds']:.3f} | {row['search']} / {row['url_observed']} | {'SPECIALIST_CAPACITY 429 after correct transfer' if row['capacity'] else 'PASS'} |")
    lines += ['',
        'All nine first specialist routes matched; eight stable answers completed, Certification stable stopped after specialist 429. '
        'Stable batch stopped immediately. Later health-gated batches did not retry that failed Certification case. Networking stable '
        'and both later health probes were useful and omitted unsupported exact LinkedIn/platform limits. Generic templates still '
        'require factual personalization before use.','',
        '#### Current-evidence spot checks and provider incidents','',
        'After cooldown, a Networking no-tool probe passed in 11.151s; Trust human escalation then passed in 2.985s, preserving UNRESOLVED '
        'and recommending human review without contacting anyone. Career current then received ROOT_CAPACITY 429 in 1.391s before '
        'transfer; that batch stopped immediately. After successful Flask/UI tests, one final lightweight health probe passed in '
        '16.128s before the remaining evidence checks.','',
        '| Current case | Result |','| --- | --- |']
    lines += [f"| {key} | {value.get('review') or value.get('reason')} |" for key,value in current.items()]
    lines += ['',
        'Trust current completed in 71.325s with one bounded Search, then requested the missing source pair and retained UNRESOLVED. '
        'The lookup was low-value given missing context, but did not create a broad loop or invented resolution; no optimization was '
        'made for this latency limitation. Networking current completed in 74.977s with one observed Search and two deterministic '
        'verification calls. Nested URL helper timing/count and grounding query totals are not fully exposed by outer SSE; an observed '
        'zero URL-helper call count must not be read as no internal URL verification. All remote request/session/transfer/first-text '
        'timings and public event text are retained without raw user/session identifiers.','',
        '**Two provider-capacity incidents:** Certification stable SPECIALIST_CAPACITY and Career current ROOT_CAPACITY. Each stopped '
        'its batch. No capacity error is treated as an architecture defect. After the Networking reliability defect below, all further '
        'inference stopped; Certification/Interview/Research current and live LinkedIn exact-limit lookup remained deferred. Offline '
        'exact-platform current retrieval still activates Search+URL verification and fails closed on unsupported facts.','',
        '#### Exact release-blocking reliability defect','',
        'Networking C1 labels the combined SACS membership, mentoring, technical-workshop and networking-benefit claim **VERIFIED '
        'CURRENT** and describes its scope as fully supported. The exact returned grounding citation was followed successfully (HTTP '
        '200) to https://www.morgan.edu/computer-science/current-students/sacs. That official page invites membership, but places the '
        'mentoring/workshop benefits under goals/vision. Membership access is supported; the whole bundle of currently delivered '
        'benefits is not established by those goals. The response’s own assessment relies on that goal language without narrowing '
        'scope or stating the missing current-delivery evidence. This is unsupported current-status promotion, not proof the club '
        'or benefits do not exist. C2 correctly remained UNSUPPORTED; no transport/URL-byte mismatch was observed.','',
        'The internal verifier date/cycle field is not exposed in the outer response and temporary registry state is intentionally '
        'not persisted. Do not fabricate its value or attribute this failure to a specific date string. The observed issue is the '
        'rendered supported_scope/why against the cited source. Exact path to inspect: shared_evidence.py EvidencePolicy.store '
        '(current-claim acceptance) and Networking URL Context verifier contract; render() propagates the accepted status. **Minimal '
        'repair scope:** retain the supported membership subclaim, mark goal-based operational benefits CURRENT STATUS UNVERIFIED '
        'until explicitly supported, and add a captured-case regression. No broad prompt/model/tool/graph redesign. This is outside '
        'the one-file packaging repair authorization, so no repair was applied.','',
        '#### Flask, managed sessions and browser','',
        'Dedicated unchanged Flask application runs at http://localhost:5002/agents/career, with startup explicitly selecting '
        'CAREER_REASONING_ENGINE_ID=932407850586603520. The pre-existing port-5001 app/tab was not repointed or stopped. '
        'Flask API fresh/same-session/different-user requests all returned HTTP 200. Same-user follow-up retained the managed '
        'session and mapped “those paths” to the earlier cloud/risk discussion. A different synthetic user received a different '
        'session and explicitly acknowledged no prior discussion. Malformed requests retained 400/413 validation.','',
        'Browser: welcome/input/thinking/busy controls, Enter send, Shift+Enter newline, counter, autogrow (76px to 240px cap), '
        'timestamps, Copy→Copied and scroll-latest passed. Markdown rendered one actual table, two headings and fourteen strong '
        'elements. Both CDN scripts loaded without console errors; unchanged renderMarkdown uses DOMPurify.sanitize(marked.parse()). '
        'No malicious payload or artificial provider failure was injected. No natural browser failure occurred: Retry/error textContent '
        'branch was inspected unchanged but not exercised live.','',
        'Refresh resets the visible transcript to welcome (existing behavior), but retains user/session identity: a follow-up without '
        'restating background correctly recalled IT risk management. Server audit confirms same user and same managed session. '
        'New Chat cleared visible content and the next message omitted the prior session, returned a different managed session for '
        'the same user, and correctly said no experience had been shared in that chat. No raw user/session IDs were written to '
        'artifacts; only equality/reset booleans and synthetic-user ordinal groups are stored. Dedicated dev tab/server remain '
        'available for inspection; this does not promote production.','',
        '#### Latency, offline checks and final decision','',
        'Completed stable query timings range from 2.985s (Trust) to 28.951s (Career): healthy observations, not an SLA or percentile '
        'estimate. Completed current Trust/Networking at 71.325/74.977s are SLOW BUT FUNCTIONAL in transport terms; Networking still '
        'fails reliability. Capacity failures and the diagnostic-envelope mistake are excluded from normal latency summaries. '
        'Flask auth/session/stream/total timings and API/browser request totals are recorded in the audit; no new SLA.','',
        'Full repaired offline suite: **142 passed + one known stale Career 501 failure** (74 pytest passes/one stale failure; 68 '
        'ADK unittest passes). Initial historical hash failures were due only to the authorized deployment entry; strict normalization '
        'checks its exact preimage and rejects any additional change. Existing JSON/history remained immutable. The obsolete 501 '
        'test sees the integrated route’s 503 under blocked authentication; it is separate from this genuine evidence failure. '
        'Syntax/import, all 30 instruction/model hashes, protected source and staged-byte parity pass; final rerun/privacy/whitespace '
        'results are recorded below.','',
        '**RELEASE CANDIDATE — NO-GO.** Packaging, deployment, routing, session isolation/continuity, New Chat and healthy browser '
        'flows are demonstrated. Networking’s current evidence promotion remains release-blocking. Stop optimization here; wait for '
        'separate authorization for only that narrow evidence-adjudication repair and regression. Preserve this new dev engine as '
        'observed; do not promote, update/delete production or old dev engines, stage, commit, push or merge.','']
    with report.open('ab') as f:f.write('\r\n'.join(lines).encode('utf8'))
    verify();print('Resumed Wave 7 report appended; decision NO-GO on observed Networking evidence promotion.')


if __name__=='__main__':main()
