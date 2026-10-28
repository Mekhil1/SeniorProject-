"""At most two Networking stable samples and one unrelated stable sample."""
import argparse
import asyncio
from datetime import datetime,timezone
import importlib.metadata
import json
import logging
import os
import sys
from career_wave65 import ROOT,MANIFEST,sha
import career_baseline as b
from career_wait_analysis import analyze

OUT=ROOT/'tests/diagnostics/career_wave65_live.json'


def plan():
    lookup={c['id']:c for c in b.plan()}
    cases=[]
    for key in ('networking_stable_1','networking_stable_2','interview_stable_1'):
        case=dict(lookup[key]);case['id']='wave65_'+key;cases.append(case)
    return cases


async def run(case):
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    assert sha((ROOT/'agents/career/workflow/agent.py').read_bytes())==m['final_source_sha256']
    d=json.loads(OUT.read_text(encoding='utf8')) if OUT.exists() else dict(plan=plan(),runs=[],execution='local source; Vertex model requests only; no Agent Engine')
    assert not any(r['status']!='completed' or r['errors'] for r in d['runs']),'Prior failure: stop all live calls.'
    assert not any(r.get('manual_review')=='FAIL' for r in d['runs']),'Reliability failure: do not retry.'
    expected=plan()[len(d['runs'])];assert expected['id']==case
    if d['runs']:
        first=d['runs'][0]
        assert first['route_match'] and not first['search_helper_invocations'] and not first['url_context_invocations'],'Health contract failed'
    d['versions']={k:importlib.metadata.version(k) for k in ('google-cloud-aiplatform','google-adk')}
    assert d['versions']=={'google-cloud-aiplatform':'1.165.1','google-adk':'2.12.0'}
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent/'.env')
    os.environ.update(GOOGLE_CLOUD_PROJECT='cosc-490',GOOGLE_CLOUD_LOCATION='us-west1',GOOGLE_GENAI_USE_VERTEXAI='true')
    logging.disable(logging.CRITICAL);sys.path.insert(0,str(ROOT))
    started=datetime.now(timezone.utc).isoformat()
    with b.instrumentation():r=await b.execute(expected,120)
    r['request_started_utc']=started;r['wait_diagnosis']=analyze(r);r['manual_review']='PENDING'
    d['runs'].append(r);d['source_sha256']=m['final_source_sha256']
    OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({k:r[k] for k in ('id','status','total_seconds','actual_specialist','search_helper_invocations','url_context_invocations','errors')}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--case',choices=[c['id'] for c in plan()]);a=p.parse_args()
    if a.live:
        if not a.case:p.error('Select one case and review it before the next.')
        asyncio.run(run(a.case))
    else:print(json.dumps(plan(),indent=2))
