"""Offline tests for the diagnostic harness; no model or cloud imports."""

from types import SimpleNamespace

import career_baseline as diagnostic


def test_plan_covers_domains_and_repeated_stable_samples():
    cases = diagnostic.plan()
    assert len(cases) == 28
    assert len({c['id'] for c in cases}) == len(cases)
    for domain, *_ in diagnostic.DOMAINS:
        assert sum(c['domain'] == domain and c['mode'] == 'stable' for c in cases) == 2
        assert sum(c['domain'] == domain and c['mode'] == 'current' for c in cases) == 1
    assert sum(c['domain'] == 'trust' for c in cases) == 4
    probes = diagnostic.plan(include_research_probes=True)
    assert len(probes) == 30
    assert probes[:28] == cases
    assert len(diagnostic.plan(True, True, True)) == 32


def test_triage_boundaries():
    assert [diagnostic.band(x) for x in (15, 15.01, 30, 30.01, 60, 60.01)] == [
        'GREEN', 'YELLOW', 'YELLOW', 'ORANGE', 'ORANGE', 'RED']


def test_thoughts_and_signature_fields_are_not_serialized():
    content = SimpleNamespace(parts=[
        SimpleNamespace(thought=True, text='PRIVATE', function_call=None, function_response=None),
        SimpleNamespace(thought=False, text='Visible', function_call=None,
                        function_response=None, thought_signature=b'PRIVATE'),
    ])
    assert diagnostic.public_parts(content) == [{'text': 'Visible'}]


def test_credential_redaction():
    assert 'secret' not in diagnostic.safe_text('Bearer secret')
    assert 'secret' not in diagnostic.safe_text('session_id=secret')
    assert diagnostic.safe_text('ordinary public claim') == 'ordinary public claim'


def test_retrieval_union_does_not_double_count_overlap():
    assert diagnostic.interval_union([
        {'start': 1, 'end': 5}, {'start': 3, 'end': 6}, {'start': 8, 'end': 9},
        {'start': 10},
    ]) == 6


def test_429_detection_without_recording_exception_text():
    observation = diagnostic.Observation(diagnostic.plan()[0])
    observation.error(RuntimeError('429 RESOURCE_EXHAUSTED private payload'), 'model')
    assert observation.errors[0]['code'] == '429'
    assert 'private payload' not in str(observation.errors)


def test_model_timing_excludes_tools_awaited_after_response():
    result = {'actual_specialist': 'specialist', 'models': [
        {'agent': 'specialist', 'start': 1, 'end': 20, 'duration': 19}],
        'events': [{'author': 'specialist', 't': 3, 'parts': [{'tool': 'search'}]}]}
    diagnostic.normalize_model_timings(result)
    assert result['models'][0]['duration'] == 2
    assert result['models'][0]['generator_lifecycle_seconds'] == 19
    assert result['specialist_model_seconds'] == 2
    diagnostic.normalize_model_timings(result)
    assert result['models'][0]['duration'] == 2
