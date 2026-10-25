"""Append repair findings; preserve all historical Wave 1–7 report bytes."""
import json
from career_networking_delivery import BASE,ROOT,verify

def main():
 verify()
 def read(n):return json.loads((BASE/n).read_text(encoding='utf8'))
 m=read('career_networking_delivery_parity.json');deployment=read('career_networking_rc2_deployment.json')
 remote=read('career_networking_rc2_remote.json');api=dict(results=[],status='DEFERRED: stopped immediately on provider 429 before Flask inference')
 validation=read('career_networking_delivery_validation.json');staged=read('career_networking_rc2_staged.json')
 before=read('career_networking_delivery_before.json');after=read('career_networking_delivery_after.json')
 py=read('career_wave7_networking_final_pytest.json');adk=read('career_wave7_networking_final_adk.json')
 lookup={r['id']:r for r in remote['runs']};required=['rc_career_stable','rc_networking_stable','rc_networking_current','rc_career_current','rc_trust_current']
 remote_ok=all(k in lookup and lookup[k]['status']=='completed' and lookup[k]['route_match'] and not lookup[k]['capacity_failure'] for k in required)
 rows=api['results'];api_ok=len(rows)==3 and all(r['http_status']==200 and r['managed_session_present'] and r['user_matches'] for r in rows) and rows[1].get('same_session_retained') and rows[2].get('new_session') and rows[2].get('persistent_user_preserved')
 assert before['status']=='VERIFIED CURRENT' and after['status']=='CURRENT STATUS UNVERIFIED'
 assert py['passed']==74 and py['failed']==1 and adk['passed']==85 and adk['failed']==adk['errors']==0
 decision='RELEASE CANDIDATE — PASS' if remote_ok and api_ok else 'RELEASE CANDIDATE — NO-GO'
 result=dict(decision=decision,root_cause='Networking accepted helper VERIFIED CURRENT flags and whole-claim scope without deterministic separation of goal/vision language from actual benefit delivery.',fix='Networking-only page_evidence operational-clause acceptance and narrower membership/existence support; downgrade incomplete compound benefit claims.',only_product_source_changed='agents/career/workflow/shared_evidence.py',fixture_provenance=read('career_networking_delivery_fixture.json')['provenance'],before=before,after=after,offline=dict(passed=159,pytest_passed=74,adk_passed=85,networking_new_tests=17,known_stale_failed=1),hashes=dict(old_shared=m['old_shared_sha256'],new_shared=m['new_shared_sha256'],instructions_unchanged=30,unrelated_sources_unchanged=True,models_tools_relationships_unchanged=True),deployment=deployment,remote_results=[{k:r.get(k) for k in ('id','status','route_match','search_helpers','url_helpers','verifications','query_seconds','capacity_failure')} for r in remote['runs']],flask=api,source_parity=staged,provider_incidents=[r['id'] for r in remote['runs'] if r['capacity_failure']],sdk_warning='Cloud Resource Manager disabled API 403 warning; SDK continued and creation succeeded. No API/IAM changes.',production_untouched=True,old_engines_untouched=True,nothing_staged_committed_pushed=True)
 (BASE/'career_networking_delivery_final.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
 raw=report.read_bytes();assert len(raw)==m['report_prefix_bytes'],'Do not duplicate report append'
 lines=['','### Networking current-delivery reliability repair and RC2 acceptance (2026-10-23)','','**'+decision+'**','','This is the single authorized reliability repair, not another optimization wave.',
 '- Root cause: a helper summary/currentness flag could upgrade SACS stated goals/vision to verified delivery of mentoring/workshops. Whole-claim support obscured narrower membership evidence.',
 '- Product change: `shared_evidence.py` only. Networking requires direct operational page evidence for each recognized benefit category; goals, mission, vision, future/negative and mismatched-year clauses cannot prove delivery. Existing authority/date/readability gates still apply. Narrow literal membership/existence and directly supported benefit scope remain visible without upgrading the compound claim.',
 '- No prompt, model, tool, agent name, callback assignment, graph, other specialist, evidence.py, backend, frontend, dependency or deployment-helper changes in this repair. Shared base store/render branches are Networking-gated; Research outputs compare equal to the original implementation.',
 '- Fixture provenance: '+result['fixture_provenance'],
 '- Captured-case adversarial regression: old implementation VERIFIED CURRENT; repaired CURRENT STATUS UNVERIFIED. Literal invitation to join SACS survives as narrower support.',
 '- All 17 new regression methods pass, including 11 aspirational wording subcases, historical 2024 workshops, goal headings, misleading goal-prefix/current assertion, compound partial evidence, explicit Fall 2026 registration, normal evidence gates, actual ADK mocked Search/URL flow, stable boundary, and non-Networking equivalence.',
 '- Full offline suite: 159 pass (74 pytest +85 ADK unittest); one known stale Career HTTP 501 expectation fails against implemented/auth-blocked HTTP 503. No additional failures.',
 '- Existing Career, Research, Certification, Interview official/anecdotal, and Trust conflict regressions pass.',
 '- Shared SHA-256 before: `'+m['old_shared_sha256']+'`.',
 '- Shared SHA-256 after: `'+m['new_shared_sha256']+'`.',
 '- All 30 instruction/model hashes and protected unrelated source bytes match entry. Networking instruction remains `b512838305e558ecfd6a39b067fff900fbd01f9417aa57ddef5dc318999d0226`. Root retains nine specialists; models remain gemini-3.5-flash.',
 '- Local live Networking: stable correct route/0 Search/0 URL, useful recruiter coaching without platform limits; current completed/1 Search/2 URL and SACS benefits CURRENT STATUS UNVERIFIED.',
 '- One initial local diagnostic invocation completed its model work but failed while saving because of a wrong expected-field name. Corrected invocation saved both local cases; no product issue.',
 '- RC2 engine: `'+deployment['engine_id']+'`; resource `'+deployment['resource_name']+'`; display **'+deployment['display_name']+'**; creation '+str(deployment['create_seconds'])+' seconds.',
 '- Existing create-only helper used unchanged; invocation sets RC2 display and archives original requirements.txt, as for RC1. Staged agent/evidence/shared/main/requirements bytes all match local. No pickle was downloaded or unpickled.',
 '- SDK Cloud Resource Manager API-disabled warning occurred; creation continued successfully. No APIs or IAM changed.',
 '- RC2 Networking current discovery hit provider 429 (TOOL_CAPACITY). Live batch stopped immediately; no retry, Career/Trust current and Flask inference deferred. Provider capacity is not classified as an architecture/evidence failure. Local Networking current and offline evidence regressions remain passing, but complete RC2 acceptance is not established.',
 '', '| RC2 check | Result | Search | Verification calls | Query seconds |','|---|---|---:|---:|---:|']
 for r in remote['runs']:lines.append('| '+r['id']+' | '+r['status']+'; route '+str(r['route_match'])+' | '+str(r['search_helpers'])+' | '+str(r['verifications'])+' | '+str(r.get('query_seconds'))+' |')
 lines += ['', 'Remote counts show outer SSE calls only. Nested URL Context/provider work is not fully exposed; a verification call is not zero retrieval.', '', '- Flask RC2 acceptance at localhost:5003: '+('PASS' if api_ok else 'DEFERRED')+' — server initialized with correct RC2 selection, but no fresh/followup/New Chat model calls made after the 429. Previous RC1 session/browser checks remain passing; RC2-specific session acceptance remains untested.', '- Previous Wave 7 routing/browser controls remain inherited: changed evidence adjudication cannot alter those frontend controls. No redundant full browser/routing sweep.', '- Production `3463694723959488512`, old RC `932407850586603520`, all other existing dev engines, and production fallback remain untouched. No stage, commit, push, promotion or engine deletion.', '- Syntax/import, instruction/source/staged parity and privacy pass. Final whitespace/status checks are recorded in the final validation artifact.', '', 'Career workflow optimization is complete.' if decision.endswith('PASS') else 'Release remains blocked pending missing acceptance checks.', 'Next actions only: commit the completed Wave 1–7 work; optionally push; production promotion later as a separate explicit task.' if decision.endswith('PASS') else 'Resume only the outstanding minimum live acceptance checks in a healthy provider window; no further optimization or production promotion.', '']
 report.write_bytes(raw+'\n'.join(lines).encode('utf8'))
 print(decision)
if __name__=='__main__':main()
