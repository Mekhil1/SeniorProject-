"""Verify Wave 4 only appends target instructions and adds declared wrappers."""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TARGETS={'certification__technical_development_agent','interview_preparation_agent','trust__human_escalation_agent'}
PROTOCOLS={'WAVE4_PARENT','WAVE4_VERIFICATION','CERTIFICATION_DISCOVERY','INTERVIEW_DISCOVERY','TRUST_DISCOVERY'}

def manifest():return json.loads((ROOT/'tests/diagnostics/career_wave4_parity.json').read_text(encoding='utf8'))

def test_exact_wave3_ast_after_declared_additions_removed():
    from career_wave5 import restore_before_compression
    current=restore_before_compression(ast.parse((ROOT/'agents/career/workflow/agent.py').read_bytes()))
    for n in current.body:
        if isinstance(n,ast.ImportFrom) and n.module=='shared_evidence':
            n.names=[x for x in n.names if x.name not in PROTOCOLS|{'interview_evidence','trust_evidence'}]
        if not isinstance(n,ast.Assign) or not isinstance(n.value,ast.Call) or getattr(n.value.func,'id','')!='LlmAgent':continue
        name=n.targets[0].id
        ins=next(k for k in n.value.keywords if k.arg=='instruction')
        if isinstance(ins.value,ast.BinOp) and isinstance(ins.value.right,ast.Name) and ins.value.right.id in PROTOCOLS:ins.value=ins.value.left
        if name in {'interview_preparation_agent','trust__human_escalation_agent'}:
            tools=next(k for k in n.value.keywords if k.arg=='tools')
            tools.value=ast.List(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id='agent_tool',ctx=ast.Load()),attr='AgentTool',ctx=ast.Load()),args=[],keywords=[ast.keyword(arg='agent',value=a)]) for a in tools.value.args],ctx=ast.Load())
            n.value.keywords=[k for k in n.value.keywords if k.arg not in {'before_agent_callback','before_model_callback','after_model_callback'}]
    assert ast.dump(current)==ast.dump(ast.parse(manifest()['entry_agent_source']))

def test_previous_artifacts_and_workflow_files_identical():
    m=manifest()
    for section in ('protected','previous_artifacts'):
        from career_wave7_resume import historical_bytes
        for name,digest in m[section].items():assert hashlib.sha256(historical_bytes(name)).hexdigest()==digest

def test_compression_estimate_is_not_runtime_reduction():
    d=json.loads((ROOT/'tests/diagnostics/career_wave4_compression.json').read_text(encoding='utf8'))
    assert d['repeated_paragraph_characters']==sum(r['characters']*(r['occurrences']-1) for r in d['repeated_paragraphs'])
    assert 'saves no rendered prompt characters' in d['runtime_note']
