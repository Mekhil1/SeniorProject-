"""Wave 5 diagnostics and strict normalization for historical parity tests.

Restoration is test-only and accepts only the measured new instruction hashes.
It never alters runtime agents, prompts, models, configuration or tool behavior.
"""
import argparse
import ast
import asyncio
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'tests/diagnostics/career_wave5_parity.json'


def nodes(tree):
    return {n.targets[0].id:n for n in tree.body if isinstance(n,ast.Assign)
        and isinstance(n.value,ast.Call) and getattr(n.value.func,'id','')=='LlmAgent'}


def instruction_value(n):
    if isinstance(n,ast.BinOp):return instruction_value(n.left)+instruction_value(n.right)
    if isinstance(n,ast.Name):
        shared=ast.parse((ROOT/'agents/career/workflow/shared_evidence.py').read_text(encoding='utf8'))
        return next(x.value.value for x in shared.body if isinstance(x,ast.Assign)
            and isinstance(x.targets[0],ast.Name) and x.targets[0].id==n.id and isinstance(x.value,ast.Constant))
    return ast.literal_eval(n)


def restore_before_compression(tree):
    from career_wave65 import restore_before_patch
    tree=restore_before_patch(tree)
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    old=nodes(ast.parse(m['entry_agent_source']))
    for name,node in nodes(tree).items():
        row=m['components'][name]
        if not row['reduction_chars']:continue
        keyword=next(k for k in node.value.keywords if k.arg=='instruction')
        assert hashlib.sha256(instruction_value(keyword.value).encode()).hexdigest()==row['new_sha256'],name
        keyword.value=deepcopy(next(k.value for k in old[name].value.keywords if k.arg=='instruction'))
    return tree


def plan():
    import career_baseline as b
    lookup={c['id']:c for c in b.plan()}
    cases=[]
    for domain,mode in [('networking','stable'),('certification','stable'),('interview','stable'),('networking','stable'),('research','stable'),('certification','current'),('networking','current')]:
        case=dict(lookup[domain+'_'+mode+'_1'])
        case['id']='wave5_health_probe' if not cases else 'wave5_'+domain+'_'+mode
        if domain=='research':case['prompt']='What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs.'
        cases.append(case)
    return cases


def cli():
    import career_baseline as b
    from career_wait_analysis import analyze
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true');parser.add_argument('--case',choices=[c['id'] for c in plan()])
    parser.add_argument('--output',type=Path,default=ROOT/'tests/diagnostics/career_wave5.json')
    args=parser.parse_args()
    if not args.live:print(json.dumps(plan(),indent=2));return
    if not args.case:parser.error('Select exactly one case, review it before the next.')
    prior=json.loads(args.output.read_text(encoding='utf8')) if args.output.exists() else {'runs':[]}
    if any(r['status']!='completed' or r['errors'] for r in prior['runs']):parser.error('Prior runtime/capacity failure: no more live requests in this session.')
    expected=next((c for c in plan() if c['id'] not in {r['id'] for r in prior['runs']}),None)
    if expected is None or args.case!=expected['id']:parser.error('Follow the exact plan order; no retries.')
    if prior['runs']:
        probe=prior['runs'][0]
        if not probe['route_match'] or probe['search_helper_invocations'] or probe['url_context_invocations']:parser.error('Health gate did not pass.')
    timeout=90 if args.case=='wave5_health_probe' else 180
    config=argparse.Namespace(resume=args.output.exists(),output=args.output,case=[args.case],timeout=timeout,pace=0)
    asyncio.run(b.main_async(config,cases_override=plan()))
    data=json.loads(args.output.read_text(encoding='utf8'))
    for run in data['runs']:run['wait_diagnosis']=analyze(run)
    args.output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')


if __name__=='__main__':cli()
