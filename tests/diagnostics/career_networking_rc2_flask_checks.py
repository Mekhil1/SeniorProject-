"""Minimum RC2 Flask/session acceptance; IDs stay in process memory."""
import json,time,uuid,requests
from pathlib import Path
BASE=Path(__file__).resolve().parent
out=BASE/'career_networking_rc2_flask_checks.json'
assert not out.exists(),'No automatic retry'
rows=[];user='rc2-api-'+uuid.uuid4().hex

def call(label,question,sid=None):
 payload=dict(question=question,user_id=user)
 if sid:payload['session_id']=sid
 t=time.perf_counter();r=requests.post('http://127.0.0.1:5003/api/career',json=payload,timeout=240);d=r.json()
 row=dict(case=label,http_status=r.status_code,total_seconds=round(time.perf_counter()-t,3),reply=d.get('reply'),error=d.get('error'),managed_session_present=bool(d.get('session_id')),user_matches=d.get('user_id')==user)
 rows.append(row);out.write_text(json.dumps(dict(results=rows),indent=2,ensure_ascii=False)+'\n',encoding='utf8');print(label,r.status_code,flush=True)
 return r.status_code,d
code,first=call('fresh',"I'm interested in cloud security and risk management. What career paths should I explore?")
if code==200:
 sid=first['session_id']
 code,follow=call('followup','Which of those paths best matches someone who already has IT risk management experience?',sid)
 rows[-1]['same_session_retained']=follow.get('session_id')==sid
 if code==200:
  code,new=call('new_chat','What career paths did we discuss earlier? I have not provided any background in this new conversation.')
  rows[-1]['new_session']=bool(new.get('session_id') and new.get('session_id')!=sid)
  rows[-1]['persistent_user_preserved']=new.get('user_id')==user
out.write_text(json.dumps(dict(results=rows),indent=2,ensure_ascii=False)+'\n',encoding='utf8')
