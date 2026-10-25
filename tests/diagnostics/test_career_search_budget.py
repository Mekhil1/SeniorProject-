"""Offline behavior checks for the per-invocation Search execution backstop."""
import ast
from pathlib import Path
from types import SimpleNamespace


def guard():
    # Load this pure function without importing ADK or resolving credentials.
    path = Path(__file__).resolve().parents[2] / "agents/career/workflow/agent.py"
    tree = ast.parse(path.read_bytes())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == "_limit_current_search_rounds")
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), namespace)
    return namespace[node.name]


def context(state=None, agent="research__graduate_pathways_agent", invocation="first-turn"):
    return SimpleNamespace(state={} if state is None else state,
                           agent_name=agent, invocation_id=invocation)


SEARCH = SimpleNamespace(name="Research___Graduate_Pathways_Agent_google_search_agent")


def test_third_search_is_denied_without_increasing_execution_count():
    limit = guard()
    ctx = context()
    assert limit(SEARCH, {"request": "official source"}, ctx) is None
    assert limit(SEARCH, {"request": "necessary exception"}, ctx) is None
    denied = limit(SEARCH, {"request": "adjacent expansion"}, ctx)
    assert denied["status"] == "SEARCH_BUDGET_EXHAUSTED"
    assert next(iter(ctx.state.values()))["count"] == 2
    assert limit(SEARCH, {}, ctx) == denied


def test_new_turn_resets_budget_even_when_state_is_reused():
    limit = guard()
    ctx = context()
    for _ in range(2):
        assert limit(SEARCH, {}, ctx) is None
    assert limit(SEARCH, {}, ctx)
    ctx.invocation_id = "next-turn"
    assert limit(SEARCH, {}, ctx) is None
    assert next(iter(ctx.state.values()))["count"] == 1


def test_specialist_and_session_counters_are_isolated():
    limit = guard()
    one = context()
    for _ in range(2):
        limit(SEARCH, {}, one)
    other_agent = context(one.state, agent="interview_preparation_agent")
    other_session = context()
    assert limit(SEARCH, {}, other_agent) is None
    assert limit(SEARCH, {}, other_session) is None
    assert limit(SEARCH, {}, one)


def test_nonsearch_tools_are_untouched_and_do_not_consume_budget():
    limit = guard()
    ctx = context()
    for name in ("transfer_to_agent", "Research_Agent_url_context_agent"):
        assert limit(SimpleNamespace(name=name), {}, ctx) is None
    assert ctx.state == {}
