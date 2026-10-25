"""Live API/session canaries against the dedicated dev-only localhost server."""
import json
from pathlib import Path
import time
from uuid import uuid4
import requests

BASE=Path(__file__).resolve().parent


def main():
    out=BASE/'career_rc2_completion_flask_checks.json';assert not out.exists(),'No automatic retry'
    results=[];url='http://127.0.0.1:5001/api/career';user='rc-api-'+uuid4().hex
    def call(label,payload):
        t=time.perf_counter();r=requests.post(url,json=payload,timeout=180);d=r.json()
        results.append(dict(case=label,http_status=r.status_code,total_seconds=round(time.perf_counter()-t,3),
            reply=d.get('reply'),error=d.get('error'),managed_session_present=bool(d.get('session_id')),user_matches=d.get('user_id')==payload.get('user_id')))
        out.write_text(json.dumps(dict(results=results),indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        print(label,r.status_code,flush=True);return r.status_code,d
    code,first=call('fresh',dict(user_id=user,question="I'm interested in cloud security and risk management. What career paths should I explore?"))
    if code!=200:return
    sid=first['session_id']
    code,follow=call('followup',dict(user_id=user,session_id=sid,question='Which of those paths best matches someone who already has IT risk management experience?'))
    if code!=200:return
    results[-1]['same_session_retained']=follow.get('session_id')==sid
    code,other=call('different_user',dict(user_id='rc-isolation-'+uuid4().hex,question='What career paths did we discuss earlier? I have not provided any background in this new conversation.'))
    if code!=200:return
    results[-1]['separate_session']=other.get('session_id')!=sid
    out.write_text(json.dumps(dict(results=results),indent=2,ensure_ascii=False)+'\n',encoding='utf8')


if __name__=='__main__':main()
