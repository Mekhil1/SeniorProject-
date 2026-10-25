"""Run existing suites in their existing environments, with network/auth blocked."""
import argparse
import contextlib
import importlib
import io
import json
import logging
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
REAL_CONNECT=socket.socket.connect


def offline_connect(sock,address):
    # Windows asyncio builds its self-pipe using a loopback socket pair.
    # Preserve that local mechanism while forbidding external connections.
    if isinstance(address,tuple) and address[0] in ('127.0.0.1','::1'):
        return REAL_CONNECT(sock,address)
    raise RuntimeError('Offline test: external network blocked')


sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'tests/diagnostics')]
ADK_MODULES=['test_career_evidence','test_career_shared_evidence','test_career_completion',
             'test_career_completion_runner','test_career_wave5_matrix']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('suite',choices=['pytest','adk']);args=parser.parse_args()
    logging.disable(logging.CRITICAL)
    with patch('google.auth.default',side_effect=RuntimeError('Offline test: authentication blocked')), \
         patch.object(socket.socket,'connect',new=offline_connect):
        if args.suite=='pytest':
            import pytest
            rows=[]
            class Observer:
                def pytest_runtest_logreport(self,report):
                    if report.when=='call' or report.failed:
                        rows.append(dict(test=report.nodeid,phase=report.when,outcome=report.outcome))
            skip=[f'--ignore=tests/diagnostics/{m}.py' for m in ADK_MODULES[1:]]
            code=pytest.main(['tests','-q','-p','no:cacheprovider','--ignore=tests/test_career_evidence.py',*skip],plugins=[Observer()])
            result=dict(suite='pytest',exit_code=int(code),tests=rows,
                passed=sum(r['outcome']=='passed' for r in rows),failed=sum(r['outcome']=='failed' for r in rows))
        else:
            suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(m)) for m in ADK_MODULES)
            stream=io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                r=unittest.TextTestRunner(stream=stream,verbosity=1).run(suite)
            result=dict(suite='adk_unittest',tests_run=r.testsRun,passed=r.testsRun-len(r.failures)-len(r.errors),
                failed=len(r.failures),errors=len(r.errors),successful=r.wasSuccessful(),
                failure_tests=[str(t) for t,_ in r.failures],error_tests=[str(t) for t,_ in r.errors])
        result['network_and_auth_blocked']=True
        (ROOT/f'tests/diagnostics/career_wave6_offline_{args.suite}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        print(json.dumps({k:v for k,v in result.items() if k!='tests'}))


if __name__=='__main__':main()
