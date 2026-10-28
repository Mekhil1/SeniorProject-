"""Wave 3: single fresh local canaries; no automatic retries/deployments."""
import argparse
import asyncio
import json
from pathlib import Path
import career_baseline as baseline
import career_wave2
from career_wait_analysis import analyze, prompt_sizes, distribution


def plan():
    wave2 = {(c['domain'], c['mode']):c for c in career_wave2.plan()}
    keys = [('certification','stable')]*3 + [('interview','stable'), ('certification','current'),
        ('networking','stable'), ('networking','current'), ('research','stable'), ('research','current'), ('interview','current')]
    cases = []
    for index, key in enumerate(keys):
        case = dict(wave2[key]); case['id'] = 'wave3_'+key[0]+'_'+key[1]+(f'_{index+1}' if index<3 else '')
        cases.append(case)
    return cases


def enrich(path):
    data = json.loads(path.read_text(encoding='utf8'))
    for run in data['runs']: run['wait_diagnosis'] = analyze(run)
    data['prompt_sizes'] = prompt_sizes(baseline.ROOT/'agents/career/workflow')
    data['certification_distribution'] = distribution(data['runs'])
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf8')


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true'); parser.add_argument('--resume', action='store_true')
    parser.add_argument('--case', action='append', choices=[c['id'] for c in plan()])
    parser.add_argument('--output', type=Path, default=baseline.ROOT/'tests/diagnostics/career_wave3.json')
    parser.add_argument('--timeout', type=float, default=180); parser.add_argument('--pace', type=float, default=20)
    args = parser.parse_args()
    if not args.live:
        print(json.dumps(plan(), indent=2)); return
    if not args.case or len(args.case)!=1: parser.error('Select exactly one case; review capacity before the next.')
    if args.output.exists() and not args.resume: parser.error('Preserve existing attempts with --resume.')
    if args.output.exists():
        prior=json.loads(args.output.read_text(encoding='utf8'))['runs']
        if args.case[0].startswith('wave3_certification_stable') and any(
                r['id'].startswith('wave3_certification_stable') and any(e.get('code')=='429' for e in r['errors']) for r in prior):
            parser.error('Certification sampling stopped after capacity failure; do not retry.')
        if args.case[0]=='wave3_interview_current' and any(any(e.get('code')=='429' for e in r['errors']) for r in prior):
            parser.error('Current Interview deferred: capacity gate did not pass.')
    asyncio.run(baseline.main_async(args, cases_override=plan()))
    enrich(args.output)


if __name__=='__main__': cli()
