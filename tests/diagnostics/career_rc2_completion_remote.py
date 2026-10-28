"""Opt-in remote canaries; only the newly recorded dev RC engine is allowed."""
import argparse
from datetime import datetime,timezone
import json
import sys
import time
from uuid import uuid4
from pathlib import Path
import google.auth
from google.auth.transport.requests import AuthorizedSession

ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'tests/diagnostics'
sys.path.insert(0,str(BASE))
import career_baseline as b


def plan():
    rows=[]
    for key,label,agent,stable,current in b.DOMAINS:
        rows.append(dict(id='rc_'+key+'_stable',domain=key,expected=agent,mode='stable',prompt=stable))
    rows.append(dict(id='rc_trust_stable',domain='trust',expected='trust__human_escalation_agent',mode='human',prompt='I need a human to review this because the available evidence is contradictory.'))
    lookup={x[0]:x for x in b.DOMAINS}
    for key in ('career','networking','certification','interview'):
        prompt=lookup[key][4]
        if key=='interview':prompt='What is the current interview process for an entry-level cybersecurity role at Microsoft?'
        rows.append(dict(id='rc_'+key+'_current',domain=key,expected=lookup[key][2],mode='current',prompt=prompt))
    rows.append(dict(id='rc_trust_current',domain='trust',expected='trust__human_escalation_agent',mode='current',prompt='I found conflicting information about whether a Morgan cybersecurity program is still active. Which source should I trust?'))
    rows.append(dict(id='rc_research_current',domain='research',expected=lookup['research'][2],mode='current',prompt='What current cybersecurity research opportunities are available at Morgan State?'))
    rows.append(dict(id='rc_networking_platform_current',domain='networking',expected=lookup['networking'][2],mode='current',prompt="What is LinkedIn's current connection-request note character limit?"))
    return rows


def run(case):
    deployment=json.loads((BASE/'career_networking_rc2_deployment.json').read_text())
    assert deployment['status']=='created'
    engine=deployment['engine_id'];assert engine=='6244403611070103552'
    output=BASE/'career_rc2_completion_remote.json'
    d=json.loads(output.read_text(encoding='utf8')) if output.exists() else dict(engine_id=engine,runs=[],plan=plan(),count_scope='Observed outer SSE calls only; nested provider work may not be exposed.')
    assert not any(r.get('capacity_failure') and r.get('batch','stable')==case.get('batch','stable') for r in d['runs']),'Capacity stop: no more requests in this batch.'
    assert not any(r['id']==case['id'] for r in d['runs']),'No automatic retries.'
    root=f'https://us-west1-aiplatform.googleapis.com/v1/projects/cosc-490/locations/us-west1/reasoningEngines/{engine}'
    t=time.perf_counter();creds,_=google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform']);client=AuthorizedSession(creds)
    r=dict(**case,started_utc=datetime.now(timezone.utc).isoformat(),auth_init_seconds=round(time.perf_counter()-t,3),events=[],errors=[],search_helpers=0,url_helpers=0,verifications=0,grounding_query_count=0,first_text=None,transfer=None,final_answer='',status='started',capacity_failure=False)
    started=time.perf_counter();user='rc-diagnostic-'+uuid4().hex;sid=None
    try:
        s=time.perf_counter()
        response=client.post(root.replace('/v1/','/v1beta1/')+'/sessions',json={'userId':user},timeout=45)
        r['session_create_seconds']=round(time.perf_counter()-s,3);r['session_http_status']=response.status_code
        response.raise_for_status();data=response.json();resource=data.get('response') or data.get('session') or data
        sid=resource.get('id') or resource.get('name','').rsplit('/',1)[-1]
        assert sid and isinstance(sid,str),'No managed session returned'
        r['managed_session_created']=True
        s=time.perf_counter()
        with client.post(root+':streamQuery?alt=sse',json={'class_method':'async_stream_query','input':{'user_id':user,'session_id':sid,'message':case['prompt']}},timeout=(30,90 if case['mode']=='stable' else 240),stream=True) as response:
            r['query_http_status']=response.status_code
            if response.status_code==429:r['capacity_failure']=True
            response.raise_for_status()
            for line in response.iter_lines(chunk_size=1):
                if not line:continue
                line=line.decode('utf8',errors='replace').strip()
                if line.startswith('data:'):line=line[5:].strip()
                try:event=json.loads(line)
                except json.JSONDecodeError:continue
                elapsed=round(time.perf_counter()-s,3)
                content=event.get('content') or {};author=event.get('author','');parts=[]
                error=event.get('error') or event.get('error_message') or event.get('errorMessage')
                if error or event.get('error_code') or event.get('errorCode'):
                    r['errors'].append(dict(stage='runtime',t=elapsed))
                    if '429' in str(event) or 'RESOURCE_EXHAUSTED' in str(event):r['capacity_failure']=True
                for p in content.get('parts',[]):
                    if p.get('thought'):continue
                    call=p.get('functionCall') or p.get('function_call')
                    if call:
                        name=call.get('name','');args=call.get('args') or {}
                        parts.append(dict(tool=name))
                        if name=='transfer_to_agent' and r['transfer'] is None:r['transfer']=dict(t=elapsed,target=args.get('agent_name'))
                        if 'google_search' in name.lower():r['search_helpers']+=1
                        if 'url_context' in name.lower():r['url_helpers']+=1
                        if name.startswith('verify_') and name.endswith('candidate'):r['verifications']+=1
                    text=p.get('text')
                    if text:
                        parts.append(dict(text=b.safe_text(text)))
                        if not any(x in author.lower() for x in ('google_search','url_context')):
                            if r['first_text'] is None:r['first_text']=elapsed
                            r['final_answer']=b.safe_text(text)
                grounding=event.get('groundingMetadata') or event.get('grounding_metadata') or {}
                r['grounding_query_count']+=len(grounding.get('webSearchQueries') or grounding.get('web_search_queries') or [])
                r['events'].append(dict(t=elapsed,author=author,parts=parts))
        r['query_seconds']=round(time.perf_counter()-s,3)
        r['actual_specialist']=r['transfer']['target'] if r['transfer'] else None
        r['route_match']=r['actual_specialist']==case['expected']
        r['status']='completed' if r['final_answer'] and not r['errors'] else 'runtime_error'
    except Exception as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):r['capacity_failure']=True
        r['errors'].append(dict(stage='request',exception_type=type(e).__name__))
        r['status']='failed'
    finally:client.close()
    r['total_seconds']=round(time.perf_counter()-started,3)
    if r['capacity_failure']:
        r['failure_class']='TOOL_CAPACITY' if r['search_helpers'] or r['verifications'] else 'SPECIALIST_CAPACITY' if r['transfer'] else 'ROOT_CAPACITY'
    d['runs'].append(r);output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({k:r.get(k) for k in ('id','status','actual_specialist','route_match','session_create_seconds','query_seconds','total_seconds','search_helpers','url_helpers','verifications','capacity_failure','failure_class','errors')}))


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('case',choices=['health','networking','career','trust']);a=p.parse_args()
 target={'health':'rc_networking_stable','networking':'rc_networking_current','career':'rc_career_current','trust':'rc_trust_current'}[a.case]
 case=dict(next(c for c in plan() if c['id']==target));case['id']='rc2_completion_'+a.case;case['batch']='completion'
 run(case)
