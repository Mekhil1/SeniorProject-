"""Network-free timing attribution and Wave 3 source preservation."""
import ast
import hashlib
import json
from pathlib import Path
import career_wait_analysis as waits
import career_wave3
import test_career_wave2_parity as previous

ROOT=Path(__file__).resolve().parents[2]


def test_phases_are_disjoint_and_sum_to_total():
    run=dict(total_seconds=20,status='completed',errors=[],actual_specialist='specialist',
        helpers=[dict(start=6,end=12)], first_text=18,
        models=[dict(agent='Orchestration',start=1,response_received=3),
                dict(agent='specialist',start=4,response_received=6),
                dict(agent='specialist',start=13,response_received=18)],events=[],model_callbacks=[])
    result=waits.analyze(run)
    assert result['phase_seconds']==dict(ROOT_WAIT=2,SPECIALIST_PRE_TOOL_WAIT=2,
        SPECIALIST_POST_TOOL_WAIT=5,TOOL_WAIT=6,STREAM_FINALIZATION=2,UNOBSERVED_RUNTIME_WAIT=3)
    assert sum(result['phase_seconds'].values())==20


def test_capacity_phase_and_censored_helper_stall():
    run=dict(total_seconds=180,status='failed',errors=[dict(code='429')],helpers=[],
        first_text=None,models=[dict(agent='Orchestration',start=0,end=2)],events=[])
    assert waits.analyze(run)['failure']==dict(cause='PROVIDER_CAPACITY',stage='ROOT_CAPACITY')
    run['models'][0]['agent']='Certification_google_search_agent'
    assert waits.analyze(run)['failure']['stage']=='TOOL_CAPACITY'
    run['models'][0]['agent']='certification_specialist'
    assert waits.analyze(run)['failure']['stage']=='SPECIALIST_CAPACITY'
    run.update(errors=[],status='timeout_censored',helpers=[dict(start=2)])
    result=waits.analyze(run)
    assert result['failure']['stage']=='TOOL_PROVIDER_STALL'
    assert result['phase_seconds']['TOOL_WAIT']==178


def test_distribution_does_not_conclude_from_single_run():
    assert waits.distribution([dict(id='wave3_certification_stable_1',total_seconds=12,
        status='completed',route_match=True)])['classification']=='INSUFFICIENT_COMPLETED_SAMPLES'
    assert len([c for c in career_wave3.plan() if c['id'].startswith('wave3_certification_stable')])==3


def test_previous_instruction_prefixes_all_preserved():
    entry=json.loads((ROOT/'tests/diagnostics/career_wave3_parity.json').read_text())
    nodes=previous.agents(previous.source())
    assert set(nodes)==set(entry['entry_instructions'])
    for name,node in nodes.items():
        expression=next(k.value for k in node.value.keywords if k.arg=='instruction')
        assert hashlib.sha256(previous.instruction(expression).encode()).hexdigest()==entry['entry_instructions'][name]


def test_previous_artifacts_unchanged():
    entry=json.loads((ROOT/'tests/diagnostics/career_wave3_parity.json').read_text())
    for path,digest in entry['previous_artifacts'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest


def test_prompt_metrics_are_local_counts_only():
    sizes=waits.prompt_sizes(ROOT/'agents/career/workflow')
    assert len(sizes)==5
    assert all(x['instruction_characters']>0 and x['approximate_tokens'] is None for x in sizes.values())


def test_between_helpers_is_post_tool_wait():
    run=dict(total_seconds=10,status='completed',errors=[],actual_specialist='specialist',
        helpers=[dict(start=2,end=4),dict(start=6,end=9)], first_text=9,
        models=[dict(agent='specialist',start=4,response_received=6)],events=[],model_callbacks=[])
    assert waits.analyze(run)['phase_seconds']['SPECIALIST_POST_TOOL_WAIT']==2
