"""Wave 7 read-only/offline checks. Never creates or contacts an Agent Engine."""
import argparse
import ast
import contextlib
import importlib
import importlib.metadata
import io
import json
import logging
from pathlib import Path
import socket
import subprocess
import sys
import tarfile
import tempfile
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'tests/diagnostics')]
from career_wave65 import sha
from career_wave6_offline import offline_connect,ADK_MODULES
FREEZE=ROOT/'tests/diagnostics/career_wave7_freeze.json'


def capture():
    assert not FREEZE.exists(),'Do not overwrite entry freeze'
    paths=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    paths.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'agents/career/workflow').iterdir()
                 if p.is_file() and p.name!='OPTIMIZATION_REPORT.md')
    report=ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md'
    x=dict(status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        checkpoint=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        protected_files={p:sha((ROOT/p).read_bytes()) for p in sorted(paths) if p and (ROOT/p).is_file()},
        prior_json={str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in (ROOT/'tests/diagnostics').glob('*.json')},
        report_prefix_bytes=len(report.read_bytes()),report_prefix_sha256=sha(report.read_bytes()))
    FREEZE.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
    print('Predeploy freeze captured; no product edit.')


def verify():
    m=json.loads(FREEZE.read_text(encoding='utf8'))
    for section in ('protected_files','prior_json'):
        for name,digest in m[section].items():assert sha((ROOT/name).read_bytes())==digest,name
    raw=(ROOT/'agents/career/workflow/OPTIMIZATION_REPORT.md').read_bytes()
    assert sha(raw[:m['report_prefix_bytes']])==m['report_prefix_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==m['checkpoint']
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()


def offline(suite,label):
    logging.disable(logging.CRITICAL)
    modules=[*ADK_MODULES,'test_career_wave65_runner']
    with patch('google.auth.default',side_effect=RuntimeError('Offline authentication blocked')),patch.object(socket.socket,'connect',new=offline_connect):
        if suite=='pytest':
            import pytest
            rows=[]
            class Observer:
                def pytest_runtest_logreport(self,report):
                    if report.when=='call' or report.failed:rows.append(dict(test=report.nodeid,phase=report.when,outcome=report.outcome))
            skip=[f'--ignore=tests/diagnostics/{m}.py' for m in modules[1:]]
            code=pytest.main(['tests','-q','-p','no:cacheprovider','--ignore=tests/test_career_evidence.py',*skip],plugins=[Observer()])
            out=dict(exit_code=int(code),passed=sum(r['outcome']=='passed' for r in rows),failed=sum(r['outcome']=='failed' for r in rows),tests=rows)
        else:
            tests=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(m)) for m in modules)
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):r=unittest.TextTestRunner(stream=io.StringIO()).run(tests)
            out=dict(tests_run=r.testsRun,passed=r.testsRun-len(r.failures)-len(r.errors),failed=len(r.failures),errors=len(r.errors),failed_tests=[str(t) for t,_ in r.failures],error_tests=[str(t) for t,_ in r.errors])
    out['external_network_and_auth_blocked']=True
    (ROOT/f'tests/diagnostics/career_wave7_{label}_{suite}.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in out.items() if k!='tests'}))


def package_audit():
    verify()
    from vertexai._genai import _agent_engines_utils as sdk
    source=ROOT/'agents/career/workflow/deploy_dev.py'
    tree=ast.parse(source.read_bytes())
    # Read the existing create config without executing deploy_dev.main().
    config=next(n for n in ast.walk(tree) if isinstance(n,ast.Dict) and any(isinstance(k,ast.Constant) and k.value=='extra_packages' for k in n.keys))
    packages=ast.literal_eval(next(v for k,v in zip(config.keys,config.values) if isinstance(k,ast.Constant) and k.value=='extra_packages'))
    blobs={}
    class Blob:
        def __init__(self,name):self.name=name
        def upload_from_string(self,data):blobs[self.name]=data
    class Bucket:
        name='offline-in-memory-no-cloud-upload'
        def blob(self,name):return Blob(name)
    # Actual pinned SDK packaging function; fake storage bucket prevents uploads.
    sdk._upload_extra_packages(extra_packages=packages,gcs_bucket=Bucket(),gcs_dir_name='offline')
    archive=next(iter(blobs.values()))
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
        members=tar.getnames()
        with tempfile.TemporaryDirectory(prefix='career-wave7-package-audit-') as tmp:
            base=Path(tmp).resolve()
            for member in tar.getmembers():
                path=(base/member.name).resolve();assert path.is_relative_to(base)
                if member.isfile():
                    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(tar.extractfile(member).read())
            child='import sys,json; from unittest.mock import patch; sys.path.insert(0,sys.argv[1]); '+\
                  '\ntry:\n with patch("google.auth.default",side_effect=RuntimeError("Offline auth blocked")):\n  from agents.career.workflow.main import app\n print(json.dumps({"loaded":True}))'+\
                  '\nexcept ModuleNotFoundError as e:\n print(json.dumps({"loaded":False,"exception_type":type(e).__name__,"missing_module":e.name}))'
            r=subprocess.run([sys.executable,'-I','-B','-c',child,str(base)],cwd=base,text=True,capture_output=True)
            assert r.returncode==0,(r.returncode,r.stderr[-1500:])
            isolated=json.loads(r.stdout.strip().splitlines()[-1])
    result=dict(versions={k:importlib.metadata.version(k) for k in ('google-cloud-aiplatform','google-adk')},
        actual_sdk_packaging=True,network_upload=False,extra_packages=packages,archive_members=members,
        missing_required_file='agents/career/workflow/shared_evidence.py',isolated_archive_import=isolated,
        deployment_attempted=False,engine_created=False,source_modified=False,
        minimal_repair='Add agents/career/workflow/shared_evidence.py to deploy_dev.py config.extra_packages; preserve create-only behavior and all runtime source. Re-run archive/import parity before deployment.')
    assert result['versions']=={'google-cloud-aiplatform':'1.165.1','google-adk':'2.12.0'}
    assert result['missing_required_file'] not in members
    assert isolated==dict(loaded=False,exception_type='ModuleNotFoundError',missing_module='agents.career.workflow.shared_evidence')
    (ROOT/'tests/diagnostics/career_wave7_packaging.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    verify();print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['capture','verify','pytest','adk','package']);p.add_argument('--label',default='predeploy');a=p.parse_args()
    if a.mode=='capture':capture()
    elif a.mode=='verify':verify();print('Freeze/source/report/HEAD/index verification PASS')
    elif a.mode=='package':package_audit()
    else:offline(a.mode,a.label)
