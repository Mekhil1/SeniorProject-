"""Dedicated localhost RC server using unmodified Flask/backend/frontend files."""
import json
import logging
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'tests/diagnostics'
sys.path.insert(0,str(ROOT))


def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent/'.env')
    deployment=json.loads((BASE/'career_networking_rc2_deployment.json').read_text())
    assert deployment['status']=='created' and deployment['engine_id']!='3463694723959488512'
    os.environ.update(CAREER_REASONING_ENGINE_ID=deployment['engine_id'],GOOGLE_CLOUD_PROJECT='cosc-490',GOOGLE_CLOUD_LOCATION='us-west1')
    from advisor import create_app
    from flask import request,g
    from agents.career import service
    assert service.REASONING_ENGINE_ID==deployment['engine_id']
    app=create_app();rows=[];users={};last_by_user={};timings=[]
    class Handler(logging.Handler):
        def emit(self,record):
            text=record.getMessage()
            if text.startswith('CAREER_LATENCY'):timings.append(text)
    service.logger.addHandler(Handler())
    @app.before_request
    def start():g.rc_started=time.perf_counter()
    @app.after_request
    def observe(response):
        if request.path=='/api/career':
            payload=request.get_json(silent=True) or {};data=response.get_json(silent=True) or {}
            who=payload.get('user_id');who=who if isinstance(who,str) else None
            ordinal=users.setdefault(who,len(users)+1) if who else None
            supplied=payload.get('session_id');returned=data.get('session_id');previous=last_by_user.get(who)
            rows.append(dict(index=len(rows)+1,http_status=response.status_code,user_ordinal=ordinal,
                new_session_requested=not bool(supplied),returned_session_present=bool(returned),
                supplied_matches_returned=bool(supplied and returned==supplied),
                differs_from_prior_session=bool(previous and returned and previous!=returned),
                user_returned_matches_request=bool(who and data.get('user_id')==who),
                total_seconds=round(time.perf_counter()-g.rc_started,3)))
            if returned:last_by_user[who]=returned
            (BASE/'career_networking_rc2_flask_audit.json').write_text(json.dumps(dict(engine_id=deployment['engine_id'],port=5003,requests=rows,timings=timings),indent=2)+'\n',encoding='utf8')
        return response
    print('Dedicated RC Flask: port 5003; selected dev engine '+service.REASONING_ENGINE_ID,flush=True)
    app.run(host='127.0.0.1',port=5003,debug=False,use_reloader=False)


if __name__=='__main__':main()
