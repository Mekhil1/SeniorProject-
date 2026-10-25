"""Network-free Wave 1 preservation and Wave 2 source-parity checks."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

import career_wave2

ROOT = Path(__file__).resolve().parents[2]
WAVE1 = {"internship__job_preparation_agent", "resume__portfolio_agent",
         "skill_gap__career_roadmap_agent", "research__graduate_pathways_agent"}
WAVE2 = {"certification___technical_development_agent_google_search_agent", "networking__professional_communication_agent", "research__graduate_pathways_agent",
         "certification__technical_development_agent", "interview_preparation_agent"}


def instruction(expression):
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Add):
        return instruction(expression.left) + instruction(expression.right)
    return ast.literal_eval(expression)


def agents(tree):
    return {n.targets[0].id: n for n in tree.body
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
            and getattr(n.value.func, "id", "") == "LlmAgent"}


def source():
    from career_wave5 import restore_before_compression
    tree = restore_before_compression(ast.parse((ROOT / "agents/career/workflow/agent.py").read_bytes()))
    # First strip precisely the Wave 4 instruction appends and two new wrappers.
    for name, node in agents(tree).items():
        keyword = next(k for k in node.value.keywords if k.arg == 'instruction')
        if isinstance(keyword.value, ast.BinOp) and isinstance(keyword.value.right, ast.Name) and keyword.value.right.id in {
                'WAVE4_PARENT', 'WAVE4_VERIFICATION', 'CERTIFICATION_DISCOVERY', 'INTERVIEW_DISCOVERY', 'TRUST_DISCOVERY'}:
            keyword.value = keyword.value.left
        if name in {'interview_preparation_agent', 'trust__human_escalation_agent'}:
            policy = 'interview_evidence' if name.startswith('interview') else 'trust_evidence'
            tools = next(k for k in node.value.keywords if k.arg == 'tools')
            assert tools.value.func.value.id == policy
            tools.value = ast.List(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id='agent_tool', ctx=ast.Load()),
                attr='AgentTool', ctx=ast.Load()), args=[], keywords=[ast.keyword(arg='agent', value=a)]) for a in tools.value.args],ctx=ast.Load())
            for field, method in [('before_agent_callback','begin'), ('before_model_callback','step'), ('after_model_callback','after')]:
                cb = next(k for k in node.value.keywords if k.arg == field)
                assert cb.value.value.id == policy and cb.value.attr == method
                node.value.keywords.remove(cb)
    # Strip only declared Wave 3 additions; the tests below still compare every
    # prior instruction/configuration against the immutable Wave 2 checkpoint.
    tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == 'shared_evidence')]
    policies = {'networking__professional_communication_agent': 'networking_evidence',
                'research__graduate_pathways_agent': 'research_evidence',
                'certification__technical_development_agent': 'certification_evidence'}
    for name, node in agents(tree).items():
        keyword = next(k for k in node.value.keywords if k.arg == 'instruction')
        if isinstance(keyword.value, ast.BinOp) and isinstance(keyword.value.right, ast.Name):
            assert keyword.value.right.id in {'PARENT_PROTOCOL', 'DISCOVERY_PROTOCOL', 'VERIFICATION_PROTOCOL'}
            keyword.value = keyword.value.left
        if name in policies:
            tools = next(k for k in node.value.keywords if k.arg == 'tools')
            assert isinstance(tools.value, ast.Call) and isinstance(tools.value.func, ast.Attribute)
            assert tools.value.func.value.id == policies[name] and tools.value.func.attr == 'tools'
            tools.value = ast.List(elts=[ast.Call(func=ast.Attribute(value=ast.Name(id='agent_tool', ctx=ast.Load()),
                attr='AgentTool', ctx=ast.Load()), args=[], keywords=[ast.keyword(arg='agent', value=a)])
                for a in tools.value.args], ctx=ast.Load())
            for field, method in [('before_agent_callback','begin'), ('before_model_callback','step'), ('after_model_callback','after')]:
                cb = next(k for k in node.value.keywords if k.arg == field)
                assert cb.value.value.id == policies[name] and cb.value.attr == method
                node.value.keywords.remove(cb)
    return tree


def manifest(name):
    return json.loads((ROOT / "tests/diagnostics" / name).read_text(encoding="utf8"))


def test_every_component_matches_reviewed_wave2_hashes():
    data = manifest("career_wave2_parity.json")
    nodes = agents(source())
    assert set(nodes) == set(data["components"])
    assert {name for name, row in data["components"].items() if row["changed"]} == WAVE2
    for name, node in nodes.items():
        value = next(k.value for k in node.value.keywords if k.arg == "instruction")
        assert hashlib.sha256(instruction(value).encode()).hexdigest() == data["components"][name]["new_sha256"]


def test_wave1_gates_and_other_entry_instructions_are_preserved():
    old = manifest("career_wave1_parity.json")["components"]
    for name, node in agents(source()).items():
        value = next(k.value for k in node.value.keywords if k.arg == "instruction")
        if name in WAVE2:
            value = value.left
        assert hashlib.sha256(instruction(value).encode()).hexdigest() == old[name]["new_sha256"]


def test_names_models_tools_relationships_and_callbacks_match_checkpoint():
    current = source()
    current.body = [n for n in current.body if not (isinstance(n, ast.FunctionDef) and n.name == "_limit_current_search_rounds")]
    for name, node in agents(current).items():
        keyword = next(k for k in node.value.keywords if k.arg == "instruction")
        if name in WAVE2:
            keyword.value = keyword.value.left
        if name in WAVE2 and not name.endswith("google_search_agent"):
            callback = next(k for k in node.value.keywords if k.arg == "before_tool_callback")
            assert isinstance(callback.value, ast.Name) and callback.value.id == "_limit_current_search_rounds"
            node.value.keywords.remove(callback)
        if name in WAVE1:
            keyword.value = keyword.value.left
    checkpoint = manifest("career_wave1_parity.json")["checkpoint"]
    original = ast.parse(subprocess.check_output([
        "git", "show", checkpoint + ":agents/career/workflow/agent.py"], cwd=ROOT))
    assert ast.dump(current) == ast.dump(original)


def test_current_canaries_are_scoped_and_in_requested_order():
    cases = career_wave2.plan()
    assert [c["domain"] for c in cases[:4]] == ["certification", "networking", "research", "interview"]
    assert all(c["mode"] == "current" for c in cases[:4])
    assert "Microsoft" in cases[3]["prompt"]
    assert len({c["id"] for c in cases}) == 8
    assert all(c["mode"] == "stable" for c in cases[4:])
