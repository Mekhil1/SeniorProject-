"""Wave 4 opt-in local reliability canaries; never deploys or retries failures."""
import argparse
import asyncio
import json
from pathlib import Path
import career_baseline as baseline
from career_wait_analysis import analyze


def plan():
    old={c['id']:c for c in baseline.plan()}
    cases=[]
    for mode in ('stable','current'):
        for index in (1,2):
            case=dict(old['certification_'+mode+'_1']);case['id']=f'wave4_certification_{mode}_{index}';cases.append(case)
    for mode in ('stable','current'):
        case=dict(old['interview_'+mode+'_1']);case['id']='wave4_interview_'+mode
        if mode=='current':case['prompt']='What is the current interview process for an entry-level cybersecurity role at Microsoft?'
        cases.append(case)
    for label,prompt in [('a','I found conflicting information about whether this Morgan cybersecurity program is still active. Which source should I trust?'),
                         ('b','The sources disagree about whether I qualify for this opportunity and I could make an important decision based on it. How reliable is this information?'),
                         ('c','I need a human to review this because the available evidence is contradictory.')]:
        cases.append(dict(id='wave4_trust_'+label,domain='trust',label='Trust',expected='trust__human_escalation_agent',mode='conflict' if label!='c' else 'human',prompt=prompt))
    for domain in ('networking','research','career'):
        mode='stable' if domain=='career' else 'current'
        case=dict(old[domain+'_'+mode+'_1']);case['id']='wave4_'+domain+'_regression'
        if domain=='research':case['prompt']='What current cybersecurity research opportunities are available at Morgan State?'
        cases.append(case)
    return cases


def enrich(path):
    data=json.loads(path.read_text(encoding='utf8'))
    for run in data['runs']:run['wait_diagnosis']=analyze(run)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')


def cli():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true');parser.add_argument('--resume',action='store_true')
    parser.add_argument('--case',action='append',choices=[c['id'] for c in plan()])
    parser.add_argument('--output',type=Path,default=baseline.ROOT/'tests/diagnostics/career_wave4.json')
    parser.add_argument('--timeout',type=float,default=180);parser.add_argument('--pace',type=float,default=20)
    args=parser.parse_args()
    if not args.live:print(json.dumps(plan(),indent=2));return
    if not args.case or len(args.case)!=1:parser.error('Choose exactly one case and review its output before the next.')
    if args.output.exists():
        if not args.resume:parser.error('Preserve existing observations with --resume.')
        data=json.loads(args.output.read_text(encoding='utf8'))
        if any(e.get('code')=='429' for r in data['runs'] for e in r['errors']):parser.error('Wave 4 live testing stopped after provider capacity failure; no further live attempts.')
    asyncio.run(baseline.main_async(args,cases_override=plan()))
    enrich(args.output)


if __name__=='__main__':cli()
