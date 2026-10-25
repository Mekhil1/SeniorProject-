"""Instruction contract/parity checks, not factual validation of any platform."""
import ast
from copy import deepcopy
import json
import pytest
from career_wave5 import nodes,instruction_value
from career_wave65 import ROOT,MANIFEST,RULE,TARGET,restore_before_patch,sha


def current():return ast.parse((ROOT/'agents/career/workflow/agent.py').read_bytes())


def test_only_networking_append_changed_and_other_29_instructions_exact():
    m=json.loads(MANIFEST.read_text(encoding='utf8'));tree=current()
    assert ast.dump(restore_before_patch(deepcopy(tree)))==ast.dump(ast.parse(m['entry_agent_source']))
    old=nodes(ast.parse(m['entry_agent_source']));new=nodes(tree)
    assert len(old)==len(new)==30
    for name,node in new.items():
        before=instruction_value(next(k.value for k in old[name].value.keywords if k.arg=='instruction'))
        after=instruction_value(next(k.value for k in node.value.keywords if k.arg=='instruction'))
        assert after==before+RULE if name==TARGET else after==before
    assert sha((ROOT/'agents/career/workflow/agent.py').read_bytes())==m['final_source_sha256']
    from career_wave7_resume import historical_bytes
    for path,digest in m['protected_files'].items():assert sha(historical_bytes(path))==digest,path
    for path,digest in m['previous_json_artifacts'].items():assert sha((ROOT/path).read_bytes())==digest,path


@pytest.mark.parametrize('unsupported_example,scope',[
    ('under 300 characters','limits'),('300-character limit','limits'),
    ('exact LinkedIn connection-note limits','LinkedIn connection-note/message limits'),
    ('current InMail limits','InMail allowances'),('current recruiter product behavior','recruiter/Premium features'),
    ('platform pricing','pricing'),('current account restrictions','account restrictions')])
def test_unsupported_platform_examples_are_in_prohibited_scope(unsupported_example,scope):
    # Examples are untrusted candidate claims, never assertions about LinkedIn.
    assert unsupported_example and scope in RULE
    assert 'On stable/no-retrieval guidance, do not state exact platform-specific' in RULE
    assert 'unless explicitly supplied by the user' in RULE
    assert 'retrieve and support it' in RULE and 'explicitly say it was not verified' in RULE


@pytest.mark.parametrize('allowed',['keep it brief','keep it concise','personalize the note',"mention why you\'re reaching out"])
def test_durable_guidance_is_not_forced_into_retrieval(allowed):
    assert not any(c.isdigit() for c in allowed)
    assert 'brief and personalized' in RULE and 'remain useful and tool-free' in RULE
    assert 'Generic recruiter templates, outreach/follow-up strategy, tone, personalization and relationship-building' in RULE
    assert 'do not search merely to enrich them' in RULE


def test_current_exact_platform_question_and_user_attribution_preserved():
    assert "What is LinkedIn's current connection-request note character limit?" in RULE
    assert 'qualifies for current-fact retrieval' in RULE
    assert 'attribute those facts to the user, not independent verification' in RULE


def test_historical_normalization_rejects_unmeasured_networking_text():
    tree=current();k=next(k for k in nodes(tree)[TARGET].value.keywords if k.arg=='instruction')
    k.value=ast.Constant(value='Unreviewed Networking replacement')
    with pytest.raises(AssertionError):restore_before_patch(tree)
