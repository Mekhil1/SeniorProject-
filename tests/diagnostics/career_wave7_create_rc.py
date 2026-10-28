"""Explicitly run repaired create-only helper with RC invocation metadata."""
import json
import os
import time
from datetime import datetime,timezone
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tests/diagnostics')]
from career_wave7_resume import BASE,REQ,packages,verify


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--create',action='store_true');a=p.parse_args()
    if not a.create:p.error('Explicit --create required')
    out=BASE/'career_wave7_rc_deployment.json'
    assert not out.exists(),'No automatic deployment retry or duplicate engine creation.'
    verify()
    assert json.loads((BASE/'career_wave7_resume_package.json').read_text())['passed']
    py=json.loads((BASE/'career_wave7_resume_verified_pytest.json').read_text())
    adk=json.loads((BASE/'career_wave7_resume_verified_adk.json').read_text())
    assert py['passed']==74 and py['failed']==1 and adk['passed']==68 and not adk['failed'] and not adk['errors']
    os.environ.update(CAREER_AGENT_STAGING_BUCKET='gs://cosc-490-agent-staging-20261021-a41c7e9b',
        GOOGLE_CLOUD_PROJECT='cosc-490',GOOGLE_CLOUD_LOCATION='us-west1',GOOGLE_GENAI_USE_VERTEXAI='true')
    from dotenv import load_dotenv
    load_dotenv(ROOT.parent/'.env')
    from vertexai._genai.agent_engines import AgentEngines
    from agents.career.workflow import deploy_dev
    original=AgentEngines.create
    record=dict(started_utc=datetime.now(timezone.utc).isoformat(),operation='CREATE_NEW_ONLY',production_target=False,status='creating')
    def save():out.write_text(json.dumps(record,indent=2,default=str)+'\n',encoding='utf8')
    def create(client,*,agent,config):
        assert config['staging_bucket']==os.environ['CAREER_AGENT_STAGING_BUCKET']
        config=dict(config);config['display_name']='Career & Professional Orchestration Agent - Final Dev RC'
        config['extra_packages']=[*config['extra_packages'],REQ]
        assert config['extra_packages']==packages()
        record.update(display_name=config['display_name'],staging_bucket=config['staging_bucket'],staging_prefix=config['gcs_dir_name'],extra_packages=config['extra_packages'])
        save();print('Creating NEW Final Dev RC engine; staging prefix '+record['staging_prefix'],flush=True)
        t=time.perf_counter()
        remote=original(client,agent=agent,config=config)
        resource=remote.api_resource
        record.update(status='created',resource_name=resource.name,engine_id=resource.name.rsplit('/',1)[-1],create_seconds=round(time.perf_counter()-t,3),
            completed_utc=datetime.now(timezone.utc).isoformat(),create_time=getattr(resource,'create_time',None),update_time=getattr(resource,'update_time',None))
        assert record['engine_id']!='3463694723959488512'
        metadata=resource.model_dump(mode='json',exclude_none=True)
        record['resource_metadata']={k:v for k,v in metadata.items() if k in ('name','display_name','create_time','update_time')}
        record['resource_metadata']['spec']={k:v for k,v in metadata.get('spec',{}).items() if k in ('agent_framework','package_spec','deployment_spec')}
        save();return remote
    save()
    try:
        with patch.object(AgentEngines,'create',create):deploy_dev.main()
    except Exception as e:
        record.update(status='create_failed',exception_type=type(e).__name__);save();raise
    verify()


if __name__=='__main__':main()
