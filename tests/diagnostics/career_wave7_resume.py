"""Wave 7 packaging repair audit; explicit create-only deployment entry point."""
import ast
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'tests/diagnostics'
FREEZE=BASE/'career_wave7_resume_freeze.json'
DEPLOY='agents/career/workflow/deploy_dev.py'
ENTRY=b'                "agents/career/workflow/shared_evidence.py",\n'
REQ='agents/career/workflow/requirements.txt'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def historical_bytes(path):
    """Permit only the exact approved packaging append in historical tests."""
    raw=(ROOT/path).read_bytes()
    if str(path).replace('\\','/')=='agents/career/workflow/shared_evidence.py':
        m=json.loads((BASE/'career_networking_delivery_parity.json').read_text(encoding='utf8'))
        assert sha(raw)==m['new_shared_sha256'],'Unmeasured Networking adjudication change'
        old=m['entry_shared_source'].encode('utf8')
        assert sha(old)==m['old_shared_sha256']
        return old
    if str(path).replace('\\','/')!=DEPLOY:return raw
    m=json.loads(FREEZE.read_text(encoding='utf8'))
    assert raw.count(ENTRY)==1
    old=raw.replace(ENTRY,b'',1)
    assert sha(old)==m['old_deploy_sha256']
    return old


def verify():
    m=json.loads(FREEZE.read_text(encoding='utf8'))
    historical_bytes(DEPLOY)
    for path,digest in m['protected_files'].items():assert sha((ROOT/path).read_bytes())==digest,path
    for path,digest in m['prior_json'].items():assert sha((ROOT/path).read_bytes())==digest,path
    raw=(ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md').read_bytes()
    assert sha(raw[:m['report_prefix_bytes']])==m['report_prefix_sha256']


def packages():
    tree=ast.parse((ROOT/DEPLOY).read_bytes())
    d=next(n for n in ast.walk(tree) if isinstance(n,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='extra_packages' for k in n.keys))
    return ast.literal_eval(next(v for k,v in zip(d.keys,d.values) if isinstance(k,ast.Constant) and k.value=='extra_packages'))+[REQ]


def audit():
    from vertexai._genai import _agent_engines_utils as sdk
    import importlib.metadata
    verify();blobs={}
    class Blob:
        def __init__(self,name):self.name=name
        def upload_from_string(self,data):blobs[self.name]=data
    class Bucket:
        name='offline-package-audit'
        def blob(self,name):return Blob(name)
    sdk._upload_extra_packages(extra_packages=packages(),gcs_bucket=Bucket(),gcs_dir_name='offline')
    with tarfile.open(fileobj=io.BytesIO(next(iter(blobs.values()))),mode='r:gz') as tar:
        names=tar.getnames();parity={}
        for name in ('agent.py','evidence.py','shared_evidence.py','main.py','requirements.txt'):
            path='agents/career/workflow/'+name;local=(ROOT/path).read_bytes();packed=tar.extractfile(path).read()
            parity[path]=dict(local_sha256=sha(local),packaged_sha256=sha(packed),match=local==packed)
            assert local==packed
        with tempfile.TemporaryDirectory(prefix='career-rc-repaired-') as tmp:
            base=Path(tmp).resolve()
            for m in tar.getmembers():
                p=(base/m.name).resolve();assert p.is_relative_to(base)
                if m.isfile():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
            code='import sys,json,vertexai; from google.auth.credentials import AnonymousCredentials; vertexai.init(project="cosc-490",location="us-west1",credentials=AnonymousCredentials()); sys.path.insert(0,sys.argv[1]); from agents.career.workflow.main import app; from agents.career.workflow.agent import root_agent; print(json.dumps({"app":type(app).__name__,"root":root_agent.name,"specialists":len(root_agent.sub_agents)}))'
            r=subprocess.run([sys.executable,'-I','-B','-c',code,str(base)],cwd=base,text=True,capture_output=True)
            assert r.returncode==0,r.stderr[-2000:]
            loaded=json.loads(r.stdout.strip().splitlines()[-1])
    out=dict(archive_members=names,byte_parity=parity,isolated_import=loaded,
        versions={k:importlib.metadata.version(k) for k in ('google-cloud-aiplatform','google-adk')},
        runtime_only_config='Append original requirements.txt to this deployment archive; set requested RC display name. No additional product source edit.',
        deploy_source_sha256=sha((ROOT/DEPLOY).read_bytes()),passed=True)
    assert out['versions']=={'google-cloud-aiplatform':'1.165.1','google-adk':'2.12.0'}
    (BASE/'career_wave7_resume_package.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out,indent=2));verify()


if __name__=='__main__':audit()
