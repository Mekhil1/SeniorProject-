"""Wave 5 structural parity, measured size, and complete replacement mapping."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from career_wave5 import nodes,instruction_value,restore_before_compression
from career_wave5_compression import REPLACEMENTS,COMMON
ROOT=Path(__file__).resolve().parents[2]

def manifest():return json.loads((ROOT/'tests/diagnostics/career_wave5_parity.json').read_text(encoding='utf8'))

def current_tree():
    from career_wave65 import restore_before_patch
    return restore_before_patch(ast.parse((ROOT/'agents/career/workflow/agent.py').read_bytes()))

def test_only_seven_instruction_expressions_changed():
    m=manifest();tree=current_tree()
    assert ast.dump(restore_before_compression(deepcopy(tree)))==ast.dump(ast.parse(m['entry_agent_source']))
    changed=[]
    for name,node in nodes(tree).items():
        value=instruction_value(next(k.value for k in node.value.keywords if k.arg=='instruction'))
        row=m['components'][name]
        assert hashlib.sha256(value.encode()).hexdigest()==row['new_sha256']
        assert len(value)==row['after_chars']
        if value!=row['old_instruction']:changed.append(name)
    assert set(changed)==set(REPLACEMENTS)

@pytest.mark.parametrize('name',list(REPLACEMENTS))
def test_each_replacement_is_auditable_and_all_other_text_preserved(name):
    m=manifest();row=m['components'][name];text=row['old_instruction']
    blocks=next(x['blocks'] for x in m['semantic_mapping'] if x['component']==name)
    for block in blocks:
        assert block['old_text'] in text
        text=text.replace(block['old_text'],block['new_text'],1)
        assert [x['old_rule'] for x in block['line_mapping']]==[x.strip() for x in block['old_text'].splitlines() if x.strip()]
        assert block['rules'] and all(x['new_location']==block['new_location'] for x in block['line_mapping'])
    assert hashlib.sha256(text.encode()).hexdigest()==row['new_sha256']
    assert 15<=row['reduction_percent']<=30
    # All appended gates and domain handoff tables remain exact, not inferred
    # from another agent's instruction or from a shared runtime policy.
    for marker in ('STABLE GUIDANCE GATE','CURRENT-FACT RETRIEVAL BUDGET','WAVE 3 PYTHON EVIDENCE BOUNDARY:','WAVE 4 NARROW EVIDENCE OVERRIDE:'):
        if marker in row['old_instruction']:assert text[text.index(marker):]==row['old_instruction'][row['old_instruction'].index(marker):]
    assert 'SPECIALIST HANDOFFS'+text.split('SPECIALIST HANDOFFS',1)[1]== 'SPECIALIST HANDOFFS'+row['old_instruction'].split('SPECIALIST HANDOFFS',1)[1]


def test_mechanics_models_helpers_career_trust_root_and_previous_artifacts_unchanged():
    m=manifest()
    from career_wave7_resume import historical_bytes
    for path,digest in m['protected_files'].items():assert hashlib.sha256(historical_bytes(path)).hexdigest()==digest,path
    for path,digest in m['previous_artifacts'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    for name,row in m['components'].items():
        if name not in REPLACEMENTS:assert row['old_sha256']==row['new_sha256']


@pytest.mark.parametrize('path,digest',[
    ('agents/success/service.py','229b089a2a4b8e719772d7dbe8a870d4ea1356d47a0e617b4305664f699b7e71'),
    ('requirements.txt','a1e7943d7a45518d09a7e4a9983503549d7e44bd7f2e5d2acbcbdac5d0a6d078'),
    ('tests/test_agents.py','1bf4ba91bc48e8a6558b78f7a630c09ae700d87f0635a4468f8eeb662a0e95c6'),
])
def test_main_merge_adapter_accepts_only_reviewed_bytes(path,digest,tmp_path,monkeypatch):
    import career_wave7_resume as adapter
    merged=(ROOT/path).read_bytes()
    historical=adapter.historical_bytes(path)
    assert adapter.sha(historical)==digest
    monkeypatch.setattr(adapter,'ROOT',tmp_path)
    target=tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True)
    for accepted in (historical,merged):
        target.write_bytes(accepted)
        assert adapter.historical_bytes(path)==historical
    target.write_bytes(merged+b'\n# Unreviewed change\n')
    with pytest.raises(AssertionError,match='Unmeasured .*main merge'):
        adapter.historical_bytes(path)
    # The main-merge exceptions must never normalize arbitrary Career source.
    career=tmp_path/'agents/career/service.py';career.parent.mkdir(parents=True)
    career.write_bytes(b'Unreviewed Career source')
    assert adapter.historical_bytes('agents/career/service.py')==career.read_bytes()


def test_date_and_evidence_scopes_not_removed():
    for token in ('CURRENT YEAR','RELEVANT CYCLE','SEARCH YEAR','Unless overridden below','historical request or label',
                  'current official posting/policy','current official organization/program','current authoritative secondary','historical official',
                  'Morgan authority retrieved this interaction','student facts','consequential academic/career/employment/financial'):
        assert token in COMMON
    assert 'currently exists' in REPLACEMENTS['research__graduate_pathways_agent'][0][2]


def test_historical_test_normalization_rejects_unmeasured_prompt():
    tree=current_tree()
    node=nodes(tree)['interview_preparation_agent'];keyword=next(k for k in node.value.keywords if k.arg=='instruction')
    keyword.value=ast.Constant(value='Unreviewed replacement')
    with pytest.raises(AssertionError):restore_before_compression(tree)


def test_reduction_is_not_only_whitespace():
    m=manifest();current=nodes(current_tree())
    for name in REPLACEMENTS:
        before=''.join(m['components'][name]['old_instruction'].split())
        after=''.join(instruction_value(next(k.value for k in current[name].value.keywords if k.arg=='instruction')).split())
        assert len(after)<.95*len(before),name
