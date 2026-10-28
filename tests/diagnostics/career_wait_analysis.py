"""Offline wait attribution. SDK waiting is not a measure of model computation."""
import ast
from collections import defaultdict
from pathlib import Path
import statistics


def analyze(run):
    total = run['total_seconds']
    helpers = run.get('helpers', [])
    first_helper = min((h['start'] for h in helpers), default=total)
    intervals = []
    for h in helpers:
        intervals.append((h['start'], h.get('end', total), 'TOOL_WAIT', 4))
    for m in run.get('models', []):
        if 'google_search' in m['agent'].lower() or 'url_context' in m['agent'].lower():
            label, priority = 'TOOL_WAIT', 4
        elif 'Orchestration' in m['agent']:
            label, priority = 'ROOT_WAIT', 3
        else:
            label = 'SPECIALIST_POST_TOOL_WAIT' if any(h.get('end', total + 1) <= m['start'] for h in helpers) else 'SPECIALIST_PRE_TOOL_WAIT'
            priority = 2
        intervals.append((m['start'], m.get('response_received', m.get('end', total)), label, priority))
    if run.get('first_text') is not None:
        intervals.append((run['first_text'], total, 'STREAM_FINALIZATION', 1))
    points = sorted({0, total, *(max(0, min(total, t)) for a, b, _, _ in intervals for t in (a, b))})
    phases = defaultdict(float)
    for a, b in zip(points, points[1:]):
        active = [(p, label) for start, end, label, p in intervals if start <= (a+b)/2 < end]
        label = max(active)[1] if active else 'UNOBSERVED_RUNTIME_WAIT'
        phases[label] += b-a
    failure = None
    if any(e.get('code') == '429' for e in run.get('errors', [])):
        latest = run.get('models', [{}])[-1].get('agent', '')
        stage = 'ROOT_CAPACITY' if 'Orchestration' in latest else 'TOOL_CAPACITY' if any(x in latest.lower() for x in ('google_search', 'url_context')) else 'SPECIALIST_CAPACITY'
        failure = dict(cause='PROVIDER_CAPACITY', stage=stage)
    elif run['status'] == 'timeout_censored':
        failure = dict(cause='DIAGNOSTIC_CUTOFF', stage='TOOL_PROVIDER_STALL' if any('end' not in h for h in helpers) else 'UNOBSERVED_RUNTIME_WAIT', censored=True)
    elif run.get('errors'):
        types = ' '.join(e['type'] for e in run['errors']).lower()
        failure = dict(cause='CLIENT_TRANSPORT' if any(s in types for s in ('connect', 'ssl', 'transport', 'timeout')) else 'WORKFLOW_LOGIC', stage='UNRESOLVED_ERROR')
    return dict(phase_seconds={k: round(v, 3) for k, v in sorted(phases.items())},
        timing_interpretation='Observed SDK/provider/network waits and helper lifetimes; not pure model computation.',
        timeline=dict(request_start=0,
            first_root_event=next((e['t'] for e in run['events'] if 'Orchestration' in e['author']), None),
            transfer_to_agent=run.get('first_transfer'), first_specialist_event=run.get('first_specialist_event'),
            first_helper_request=min((t['start'] for t in run.get('tools', []) if t['kind'] in {'search','url','verification'}), default=first_helper if helpers else None),
            helper_completions=[h.get('end') for h in helpers],
            specialist_resumes=[m['t'] for m in run.get('model_callbacks', [])
                                if m['agent']==run.get('actual_specialist') and helpers and m['t']>=first_helper],
            first_public_text=run.get('first_text'), stream_completion=total), failure=failure)


def prompt_sizes(path):
    # Static source AST, with explicitly named Wave 3 literal constants; no SDK/API.
    root = Path(path)
    shared = ast.parse((root/'shared_evidence.py').read_text(encoding='utf-8-sig'))
    constants = {n.targets[0].id: n.value.value for n in shared.body if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
    def value(n):
        if isinstance(n, ast.BinOp): return value(n.left)+value(n.right)
        if isinstance(n, ast.Name): return constants[n.id]
        return ast.literal_eval(n)
    wanted = {'root_agent', 'certification__technical_development_agent', 'research__graduate_pathways_agent',
              'networking__professional_communication_agent', 'interview_preparation_agent'}
    result = {}
    for node in ast.parse((root/'agent.py').read_bytes()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in wanted:
            kws = {k.arg:k.value for k in node.value.keywords}
            tools = kws['tools']
            result[node.targets[0].id] = dict(instruction_characters=len(value(kws['instruction'])),
                approximate_tokens=None, tokenizer='No local model-compatible tokenizer used; no API or downloads',
                helper_tool_descriptions=2 if isinstance(tools, ast.Call) else len(tools.elts))
    return result


def distribution(runs):
    samples = [r for r in runs if r['id'].startswith('wave3_certification_stable')]
    completed = [r['total_seconds'] for r in samples if r['status']=='completed' and r['route_match']]
    return dict(attempts=len(samples), completed_seconds=completed,
        minimum=min(completed) if completed else None, maximum=max(completed) if completed else None,
        median=statistics.median(completed) if completed else None,
        mean=statistics.mean(completed) if completed else None,
        population_stdev=statistics.pstdev(completed) if len(completed)>1 else None,
        classification='INSUFFICIENT_COMPLETED_SAMPLES' if len(completed)<3 else '103s NOT REPRODUCED: observed outlier versus three fresh runs; provider versus history cause unresolved')
