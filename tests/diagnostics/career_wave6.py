"""Measurement-only Wave 6. Local source model calls; never an Agent Engine.

Default is offline plan inspection. --live --batch selects one ordered batch.
Any abnormal run stops further requests; no retry or automatic resume.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import subprocess
import sys

import career_baseline as b
from career_wait_analysis import analyze

ROOT=b.ROOT
OUT=ROOT/'tests/diagnostics/career_wave6_final.json'
MANIFEST=ROOT/'tests/diagnostics/career_wave6_parity.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    """Capture tracked product/config plus untracked workflow product files."""
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    paths={p for p in tracked if p and (ROOT/p).is_file()}
    paths.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'agents/career/workflow').iterdir()
                 if p.is_file() and p.name!='OPTIMIZATION_REPORT.md')
    prior={str(p.relative_to(ROOT)).replace('\\','/'):digest(p)
           for p in (ROOT/'tests/diagnostics').iterdir()
           if p.is_file() and not p.name.startswith('career_wave6')}
    report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
    return dict(checkpoint=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                captured_utc=datetime.now(timezone.utc).isoformat(),
                protected_files={p:digest(ROOT/p) for p in sorted(paths)},previous_artifacts=prior,
                report_prefix_bytes=len(report.read_bytes()),report_prefix_sha256=digest(report))


def verify():
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    for group in ('protected_files','previous_artifacts'):
        for path,sha in m[group].items():
            assert digest(ROOT/path)==sha,path
    raw=(ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md').read_bytes()
    assert hashlib.sha256(raw[:m['report_prefix_bytes']]).hexdigest()==m['report_prefix_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==m['checkpoint']
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()


def plan():
    domains=[*b.DOMAINS,('trust','Trust & Human Escalation','trust__human_escalation_agent',
        'I need a human to review this because the available evidence is contradictory.','')]
    batches=[]
    for sample in (1,2,3):
        cases=[dict(id=f'wave6_{key}_stable_{sample}',domain=key,label=label,expected=agent,
                    mode='human' if key=='trust' else 'stable',prompt=stable)
               for key,label,agent,stable,_ in domains]
        batches.append((f'stable_{sample}',cases))
    current_overrides={
        'resume':'What skills are employers currently emphasizing in entry-level cloud security job postings?',
        'interview':'What is the current interview process for an entry-level cybersecurity role at Microsoft?',
        'roadmap':'Which technologies are currently appearing most often in entry-level cloud security roles?',
        'research':'What current cybersecurity research opportunities are available at Morgan State?'}
    current=[dict(id=f'wave6_{key}_current_1',domain=key,label=label,expected=agent,mode='current',
                  prompt=current_overrides.get(key,prompt)) for key,label,agent,_,prompt in domains[:-1]]
    for suffix,prompt in [('a','I found conflicting information about whether this Morgan cybersecurity program is still active. Which source should I trust?'),
                          ('b','The sources disagree about whether I qualify for this opportunity and I could make an important decision based on it. How reliable is this information?')]:
        current.append(dict(id='wave6_trust_current_'+suffix,domain='trust',label=domains[-1][1],
                            expected=domains[-1][2],mode='conflict',prompt=prompt))
    for i in range(0,len(current),3):batches.append((f'current_{i//3+1}',current[i:i+3]))
    # Cover all paths before spending capacity on second/third stable samples.
    batches=[batches[0],*batches[3:],*batches[1:3]]
    return [dict(batch=name,cases=[dict(id='wave6_health_'+name,domain='networking',label='Provider health gate',
        expected=b.DOMAINS[4][2],mode='stable_probe',prompt=b.DOMAINS[4][3]),*cases]) for name,cases in batches]


async def run_batch(batch):
    verify()
    data=json.loads(OUT.read_text(encoding='utf8'))
    assert not data.get('batch_stopped'),'Prior abnormal run: stop; do not retry in this measurement wave.'
    done={r['id'] for r in data['runs']}
    expected=next(x for x in plan() if not all(c['id'] in done for c in x['cases']))
    assert expected['batch']==batch,'Follow ordered batches; no retries.'
    versions={k:importlib.metadata.version(k) for k in ('google-cloud-aiplatform','google-adk')}
    assert versions=={'google-cloud-aiplatform':'1.165.1','google-adk':'2.12.0'}
    data['versions']=versions
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent/'.env')
    os.environ.update(GOOGLE_CLOUD_PROJECT='cosc-490',GOOGLE_CLOUD_LOCATION='us-west1',GOOGLE_GENAI_USE_VERTEXAI='true')
    logging.disable(logging.CRITICAL)
    sys.path.insert(0,str(ROOT))
    with b.instrumentation():
        for case in expected['cases']:
            assert case['id'] not in done,'Do not retry attempted cases.'
            started=datetime.now(timezone.utc).isoformat()
            print('START '+case['id'],flush=True)
            r=await b.execute(case,90 if case['mode']=='stable_probe' else 240)
            r['request_started_utc']=started
            r['batch']=batch
            r['wait_diagnosis']=analyze(r)
            r['deterministic_verification_count']=sum(t['kind']=='verification' for t in r['tools'])
            r['reliability_verdict']='PENDING_MANUAL_REVIEW' if r['status']=='completed' else 'UNASSESSED_NO_HEALTHY_COMPLETION'
            abnormal=r['status']!='completed' or bool(r['errors'])
            invalid_probe=case['mode']=='stable_probe' and (not r['route_match'] or r['search_helper_invocations'] or r['url_context_invocations'])
            data['runs'].append(r)
            if abnormal or invalid_probe:
                data['batch_stopped']=dict(batch=batch,after_case=case['id'],
                    classification='PROVIDER_UNHEALTHY' if abnormal else 'HEALTH_PROBE_CONTRACT_FAILURE',
                    failure=r['wait_diagnosis']['failure'],no_more_live_calls=True)
            OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
            print(json.dumps({k:r[k] for k in ('id','status','total_seconds','actual_specialist','search_helper_invocations','url_context_invocations','errors')}),flush=True)
            verify()
            if data.get('batch_stopped'):break
            await asyncio.sleep(5)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true');parser.add_argument('--verify',action='store_true')
    parser.add_argument('--live',action='store_true');parser.add_argument('--batch',choices=[x['batch'] for x in plan()])
    args=parser.parse_args()
    if args.capture:
        assert not MANIFEST.exists() and not OUT.exists(),'Never overwrite entry capture/results.'
        MANIFEST.write_text(json.dumps(capture(),indent=2)+'\n',encoding='utf8')
        OUT.write_text(json.dumps(dict(schema_version=1,execution='local source workflow; Vertex model requests only; no Agent Engine',
            plan=plan(),runs=[]),indent=2)+'\n',encoding='utf8')
        print('Captured source/artifact hashes before live measurement.');return
    if args.verify:verify();print('Source/artifact/report-prefix/HEAD/index parity PASS');return
    if args.live:
        if not args.batch:parser.error('Select one ordered batch.')
        asyncio.run(run_batch(args.batch));return
    print(json.dumps(plan(),indent=2))


if __name__=='__main__':main()
