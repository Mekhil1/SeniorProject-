"""Offline Wave 7 blocked-deployment report. No runtime or cloud mutation."""
import json
from career_wave7_preflight import ROOT,verify


def main():
    verify();base=ROOT/'tests/diagnostics'
    def read(name):return json.loads((base/name).read_text(encoding='utf8'))
    pack=read('career_wave7_packaging.json');val=read('career_wave7_validation.json')
    py=read('career_wave7_predeploy_pytest.json');adk=read('career_wave7_predeploy_adk.json')
    assert py['passed']==74 and py['failed']==1 and adk['passed']==68 and not adk['failed'] and not adk['errors']
    blocked='NOT RUN: deployment package omits shared_evidence.py and fails isolated import; no engine created.'
    domains=['Career Exploration','Internship','Resume','Interview','Networking','Skill Roadmap','Research','Certification','Trust']
    out=dict(decision='RELEASE CANDIDATE — NO-GO',stage='PREDEPLOYMENT_PACKAGING',engine_id=None,resource_name=None,
        display_name=None,creation_timestamp=None,runtime_metadata=None,
        desired_display_name='Career & Professional Orchestration Agent - Final Dev RC',project='cosc-490',region='us-west1',
        staging_bucket='gs://cosc-490-agent-staging-20261021-a41c7e9b',staging_prefix=None,staging_uploads=0,engine_created=False,
        dependencies=pack['versions'],staged_source_parity='NOT APPLICABLE: no staged source; offline actual SDK archive fails import.',
        packaging=pack,source_validation=val,remote_smoke=blocked,routing_matrix={d:blocked for d in domains},
        current_spot_checks={d:blocked for d in ['Career','Networking','Certification','Interview','Trust','Research','LinkedIn exact limit']},
        flask_tests={d:blocked for d in ['fresh_session','same_session_continuity','different_user_isolation','malformed_request_release_check','natural_upstream_failure']},
        browser_tests={d:blocked for d in ['initial_message','input_thinking','Markdown_DOMPurify','timestamps_copy','retry_visibility',
            'Enter_ShiftEnter','textarea_autogrow_scroll_counter','refresh_session_persistence','user_persistence','New_Chat_fresh_backend_session']},
        networking_regression='Wave 6.5 blocker remains cleared offline; no remote Wave 7 validation.',
        evidence_integrity='Offline contracts pass; no deployed response to assess.',
        latency=dict(remote=None,flask=None,classification='WORKFLOW DEFECT: packaging, not provider capacity'),
        provider_capacity_incidents=0,live_inference_attempts=0,
        predeploy_offline=dict(passed=142,known_stale_failed=1,pytest_passed=74,adk_unittest_passed=68),
        stale_test='tests/test_agents.py::test_agent_starter_endpoint[career]: obsolete HTTP 501 expectation; integrated service returns 503 under offline auth block. Not a deployment blocker.',
        exact_defect='deploy_dev.py config.extra_packages omits agents/career/workflow/shared_evidence.py, imported by agent.py. Actual SDK archive has only six listed files; clean import raises ModuleNotFoundError: agents.career.workflow.shared_evidence.',
        minimal_required_repair=pack['minimal_repair'],repair_applied=False,awaiting_separate_repair_authorization=True,
        product_files_modified=[],production_engine='3463694723959488512',production_untouched=True,production_fallback_unchanged=True,
        old_dev_engines_untouched=True,nothing_staged_committed_pushed=True)
    (base/'career_wave7_final.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
    assert b'## Wave 7 ' not in report.read_bytes(),'Do not overwrite/duplicate report history'
    lines=['','','## Wave 7 — Final Dev Release Candidate','',
        '**RELEASE CANDIDATE — NO-GO.** A reproducible packaging/import defect blocks deployment. Stopped before any create/upload call; '
        'the repair remains unapplied under the explicit separate-authorization rule. This is not a new optimization wave. '
        'Wave 6.5’s Networking output blocker remains cleared; the new blocker is deployment packaging.','',
        '### Freeze, dependencies and deployment metadata','',
        'Captured Git status/branch/HEAD and protected file hashes before testing in `career_wave7_freeze.json`. '
        'Project/region intended: cosc-490/us-west1; supplied bucket: gs://cosc-490-agent-staging-20261021-a41c7e9b. '
        'Desired display name: Career & Professional Orchestration Agent - Final Dev RC. **No engine ID, resource name, creation timestamp, '
        'runtime metadata, staging prefix or uploaded artifact exists.** No cloud read/write was needed for the offline reproduction. '
        'Production, existing dev engines, and the staging bucket remain untouched.','',
        'Pinned environment: google-cloud-aiplatform[agent_engines,adk]==1.165.1 and google-adk==2.12.0; no dependency changes. '
        'Existing helper is still create-only, with its Source Dev v4 display/prefix defaults. Those names do not select an update '
        'target and are not the blocker. Production fallback remains 3463694723959488512.','',
        '### Exact defect, reproduction and minimal repair','',
        '`agent.py` imports `.shared_evidence`. `agents/career/workflow/deploy_dev.py:config.extra_packages` omits '
        '`agents/career/workflow/shared_evidence.py`. The six listed files are package initializers, agent.py, evidence.py and main.py. '
        'The pinned SDK archives those explicit file paths without discovering the missing sibling module.','',
        'Executed the actual SDK `_agent_engines_utils._upload_extra_packages` with an in-memory fake storage bucket, so no real '
        'upload occurred. Inspected its six-file archive and extracted only contained paths into an isolated temporary directory. '
        'A clean pinned `python -I -B` process importing `agents.career.workflow.main.app` from that archive failed with '
        '**ModuleNotFoundError: agents.career.workflow.shared_evidence**. Temporary files were removed on context exit. '
        'The packaging artifact retains only public findings, not source pickles, credentials or managed-session identifiers.','',
        '**Minimal repair:** add `agents/career/workflow/shared_evidence.py` to the existing `config.extra_packages` list in '
        '`deploy_dev.py`; preserve create-only behavior and all workflow/model/tool/graph settings. Re-run archive/import parity '
        'before creating a NEW engine. **No repair applied; wait for separate authorization.** No broad optimization or production '
        'promotion is proposed. Local source import alone cannot detect an omitted deployment file.','',
        '### Source/import parity','',
        '| Required source | SHA-256 |','| --- | --- |']
    lines += [f'| {name} | `{digest}` |' for name,digest in val['source_hashes'].items()]
    lines += ['',
        'All protected files unchanged. Local AdkApp import passes with explicit offline project/region and AnonymousCredentials; '
        'all 30 instruction hashes/models match Wave 6.5, with nine root specialists. Tools, callbacks, graph and evidence mechanics '
        'are unchanged. An initial auth-blocked import without project configuration required diagnostic setup; configured import passed. '
        '**Staged/deployed-byte parity is not applicable, not passed:** nothing was uploaded and isolated archive import fails.','',
        '### Remote routing/current evidence','',
        '| Specialist | Stable/routing | Current evidence |','| --- | --- | --- |']
    lines += [f'| {d} | Not run: deployment blocked | Not run: deployment blocked |' for d in domains]
    lines += ['',
        'Remote smoke, managed-session create/query/transfer/helper/first-text timings and current spot checks are all **not run**. '
        'Provider-capacity incidents: **0**; live inference attempts: **0**. No prior-wave result is relabelled as new deployed validation. '
        'Offline evidence status/URL transport and Networking exact-platform retrieval contracts pass, but no deployed current answer exists '
        'to inspect for status upgrades, anecdotes labelled official, partnerships, openings/funding or vendor offers.','',
        '### Flask, sessions and browser','',
        'No dedicated Flask override was started: there is no new validated engine. Fresh-session HTTP 200, same-user “those paths” '
        'continuity, different-user isolation, malformed-request release validation, natural upstream failure and New Chat managed-session '
        'reset are **not tested end to end**. Existing offline API/configuration tests are not substitutes for new-engine validation.','',
        'No browser interaction/redesign occurred. Initial message/input/thinking, Markdown/DOMPurify, timestamps/copy/retry, '
        'Enter/Shift+Enter, autogrow/scroll/counter, refresh/session/user persistence and New Chat fresh backend session are all '
        '**not run in Wave 7**. The existing ambient localhost page was neither repointed nor mistaken for the new release candidate. '
        'Remote/Flask latency: unavailable; classification **WORKFLOW DEFECT (packaging)**, not provider variance. No SLA added.','',
        '### Offline and final decision','',
        'Predeploy complete offline suite: **142 passed + one known stale failure**: 74 pytest passes/one stale failure; 68 ADK unittest '
        'passes. External auth/sockets blocked, allowing Windows asyncio loopback. Known stale '
        '`tests/test_agents.py::test_agent_starter_endpoint[career]` expects the obsolete HTTP 501 stub; the integrated route returns '
        '503 under offline auth block. This obsolete expectation is not the deployment blocker and was not changed. '
        'Final suite/hash/privacy/syntax/whitespace reruns are recorded below.','',
        '**RELEASE CANDIDATE — NO-GO.** Only demonstrated release blocker: omitted required module in '
        '`deploy_dev.py:config.extra_packages`. Wait for the minimal repair authorization, then resume package/deployment/end-to-end '
        'validation. Do not claim final release validation complete or start a broad optimization wave.','',
        'Added Wave 7 preflight/report drivers, freeze/packaging/validation/final-result JSON, and predeploy/final pytest/ADK result '
        'JSON under `tests/diagnostics/`. This append is the only existing-file edit during Wave 7. Previous report history and prior '
        'JSON artifacts are preserved. No product changes, dependencies, cloud engine/session/staging-object creation, staging, '
        'commit, push, merge or promotion occurred. Production and all old dev engines remain untouched.','']
    with report.open('ab') as f:f.write('\r\n'.join(lines).encode('utf8'))
    verify();print('Wave 7 report appended. RELEASE CANDIDATE — NO-GO. Minimal repair not applied.')


if __name__=='__main__':main()
