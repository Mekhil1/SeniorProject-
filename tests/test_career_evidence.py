"""Network-free invariants for the Career Exploration evidence transport."""

import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from google.adk.sessions.state import State
from agents.career.workflow.evidence import (
    CANDIDATES, CONTROL, HANDOFFS, VERIFICATIONS, CandidateRegistry,
    DiscoveryRegistryTool, VerifyEvidenceCandidateTool, begin_evidence_invocation,
    bounded_evidence_step, parse_discovery, render_evidence,
)


LONG_URL = ("https://vertexaisearch.cloud.google.com/grounding-api-redirect/"
            + "AUZIYQEBHTAa_Zz-09" * 25 + "==?Case=UPPER_lower&encoded=%2F%2b%3D&x=a-b_c")


def candidate(url=LONG_URL, claim="Morgan's CAP Center: exact claim — café & CS students."):
    return dict(claim=claim, source_url=url, source_type="Official Morgan",
                source_title="Title", apparent_date_or_cycle="UNKNOWN",
                discovery_support="Description", discovery_limits="No current cycle",
                discovery_status="CANDIDATE CURRENT")


def context(invocation="one"):
    ctx = SimpleNamespace(state=State({}, {}), invocation_id=invocation)
    begin_evidence_invocation(ctx)
    return ctx


class FakeVerifier:
    def __init__(self):
        self.requests = []

    async def run_async(self, *, args, tool_context):
        self.requests.append(args["request"])
        return ("VERIFICATION ITEM 1\nCLAIM: rewritten by model\n"
                "SOURCE URL: https://wrong.example/\nSOURCE TITLE: title\n"
                "SOURCE DATE OR CYCLE: UNKNOWN\nPAGE EVIDENCE: Description\n"
                "SUPPORTED SCOPE: Stated research scope\nNOT ESTABLISHED: Current access\n"
                "STATUS: CURRENT STATUS UNVERIFIED\nWHY: No dated cycle")


class EvidenceTests(unittest.TestCase):
    def test_registration_ids_max_three_and_no_mutable_alias(self):
        ctx = context(); registry = CandidateRegistry(ctx.state)
        inputs = [candidate() for _ in range(3)]
        summary = registry.register(inputs)
        self.assertEqual([c['candidate_id'] for c in summary], ['C1', 'C2', 'C3'])
        self.assertNotIn('source_url', summary[0])
        inputs[0]['claim'] = 'mutated'
        self.assertNotEqual(registry.get('C1').claim, 'mutated')
        self.assertIn(CANDIDATES, ctx.state._delta)
        with self.assertRaises(ValueError):
            CandidateRegistry(context().state).register([candidate()] * 4)

    def test_exact_claim_and_url_survive_real_tool_handoff(self):
        ctx = context(); original = candidate()
        CandidateRegistry(ctx.state).register([original])
        fake = FakeVerifier(); tool = VerifyEvidenceCandidateTool(fake)
        result = asyncio.run(tool.run_async(args={'candidate_id': 'C1'}, tool_context=ctx))
        self.assertEqual(fake.requests, [f"CLAIM:\n{original['claim']}\n\nSOURCE URL:\n{LONG_URL}"])
        self.assertEqual(ctx.state[HANDOFFS][0]['stored_url'].encode(),
                         ctx.state[HANDOFFS][0]['verifier_url'].encode())
        stored = ctx.state[VERIFICATIONS]['C1']
        self.assertEqual(stored['source_url'], LONG_URL)
        self.assertEqual(stored['claim'], original['claim'])
        self.assertNotIn('source_url', result)
        self.assertIn(LONG_URL, render_evidence(ctx.state))
        self.assertNotIn('wrong.example', render_evidence(ctx.state))

    def test_schema_structurally_disallows_url_and_claim(self):
        schema = VerifyEvidenceCandidateTool(FakeVerifier())._get_declaration().parameters_json_schema
        self.assertEqual(set(schema['properties']), {'candidate_id'})
        self.assertFalse(schema['additionalProperties'])
        ctx = context(); fake = FakeVerifier()
        response = asyncio.run(VerifyEvidenceCandidateTool(fake).run_async(
            args={'candidate_id': 'C1', 'source_url': 'https://evil.example/'}, tool_context=ctx))
        self.assertIn('error', response)
        self.assertEqual(fake.requests, [])

    def test_unknown_duplicate_and_two_selection_limit(self):
        ctx = context(); registry = CandidateRegistry(ctx.state)
        registry.register([candidate()] * 3)
        registry.reserve_verification('C1'); registry.reserve_verification('C2')
        with self.assertRaisesRegex(ValueError, 'budget'):
            registry.reserve_verification('C3')
        ctx = context(); registry = CandidateRegistry(ctx.state)
        registry.register([candidate()])
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            registry.reserve_verification('C99')
        registry.reserve_verification('C1')
        self.assertEqual(ctx.state[CONTROL]['verification_attempts'], 2)
        ctx = context(); registry = CandidateRegistry(ctx.state); registry.register([candidate()])
        registry.reserve_verification('C1')
        with self.assertRaisesRegex(ValueError, 'already'):
            registry.reserve_verification('C1')

    def test_registry_is_fresh_on_next_turn(self):
        ctx = context(); CandidateRegistry(ctx.state).register([candidate()])
        ctx.invocation_id = 'next-turn'; begin_evidence_invocation(ctx)
        self.assertEqual(ctx.state[CANDIDATES], {})
        self.assertEqual(ctx.state[VERIFICATIONS], {})
        self.assertEqual(ctx.state[HANDOFFS], [])

    def test_discovery_parser_preserves_url_claim_and_rejects_four(self):
        original = candidate()
        fields = {'claim': 'CLAIM', 'source_url': 'SOURCE URL', 'source_type': 'SOURCE TYPE',
                  'source_title': 'SOURCE TITLE', 'apparent_date_or_cycle': 'APPARENT DATE OR CYCLE',
                  'discovery_support': 'DISCOVERY SUPPORT', 'discovery_limits': 'DISCOVERY LIMITS',
                  'discovery_status': 'DISCOVERY STATUS'}
        block = 'EVIDENCE CANDIDATE 1\n\n' + '\n\n'.join(
            f'{label}:\n{original[key]}' for key, label in fields.items())
        self.assertEqual(parse_discovery(block), [original])
        with self.assertRaises(ValueError):
            parse_discovery('\n'.join([block] * 4))

    def test_copyright_cannot_verify_and_unsupported_is_not_upgraded(self):
        ctx = context(); registry = CandidateRegistry(ctx.state); registry.register([candidate()])
        c = registry.get('C1')
        record = registry.store_verification(c, 'STATUS: VERIFIED CURRENT\nSOURCE DATE OR CYCLE: 2026 (Copyright 2026)')
        self.assertEqual(record['status'], 'CURRENT STATUS UNVERIFIED')
        self.assertEqual(record['source_date_or_cycle'], 'UNKNOWN')
        registry.store_verification(c, 'STATUS: UNSUPPORTED\nWHY: Candidate exceeds source')
        rendered = render_evidence(ctx.state)
        self.assertIn('C1 — UNSUPPORTED', rendered)
        self.assertNotIn('CURRENT STATUS UNVERIFIED', rendered)

    def test_final_callback_uses_only_verifications_and_stops_at_budget(self):
        ctx = context(); registry = CandidateRegistry(ctx.state)
        registry.register([candidate(claim='Selected'), candidate(claim='Never verified')])
        ctx.state[CONTROL] = {**ctx.state[CONTROL], 'search_attempts': 1, 'verification_attempts': 2}
        registry.store_verification(registry.get('C1'), 'STATUS: HISTORICAL\nSOURCE DATE OR CYCLE: April 17, 2024\nWHY: Past event')
        response = bounded_evidence_step(ctx, SimpleNamespace())
        text = response.content.parts[0].text
        self.assertIn('HISTORICAL', text)
        self.assertNotIn('Never verified', text)

    def test_discovery_is_closed_after_one_usable_result(self):
        from google.adk.agents import LlmAgent
        from google.genai import types
        ctx = context()
        ctx.user_content = types.Content(role='user', parts=[types.Part(text='Actual student question')])
        tool = DiscoveryRegistryTool(agent=LlmAgent(name='discovery_test'))
        original = candidate()
        labels = ['CLAIM', 'SOURCE URL', 'SOURCE TYPE', 'SOURCE TITLE', 'APPARENT DATE OR CYCLE',
                  'DISCOVERY SUPPORT', 'DISCOVERY LIMITS', 'DISCOVERY STATUS']
        output = 'EVIDENCE CANDIDATE 1\n' + '\n\n'.join(
            label + ':\n' + value for label, value in zip(labels, original.values()))
        mock = AsyncMock(return_value=output)
        with patch('google.adk.tools.agent_tool.AgentTool.run_async', mock):
            asyncio.run(tool.run_async(args={'request': 'calendar lookup'}, tool_context=ctx))
            denied = asyncio.run(tool.run_async(args={'request': 'more research'}, tool_context=ctx))
        self.assertEqual(mock.await_count, 1)
        self.assertEqual(mock.call_args.kwargs['args'], {'request': 'Actual student question'})
        self.assertIn('error', denied)
        self.assertEqual(ctx.state[CONTROL]['search_attempts'], 1)

    def test_discovery_retry_requires_zero_candidates_and_cannot_loop(self):
        from google.adk.agents import LlmAgent
        from google.genai import types
        ctx = context()
        ctx.user_content = types.Content(role='user', parts=[types.Part(text='Actual question')])
        tool = DiscoveryRegistryTool(agent=LlmAgent(name='empty_discovery_test'))
        mock = AsyncMock(return_value='INSUFFICIENT EVIDENCE: no usable official URL')
        with patch('google.adk.tools.agent_tool.AgentTool.run_async', mock):
            for _ in range(4):
                asyncio.run(tool.run_async(args={'request': 'research'}, tool_context=ctx))
        self.assertEqual(mock.await_count, 2)
        self.assertEqual(ctx.state[CONTROL]['search_attempts'], 2)

    def test_invalid_schema_attempts_also_stop_after_two(self):
        ctx = context(); tool = VerifyEvidenceCandidateTool(FakeVerifier())
        for _ in range(4):
            asyncio.run(tool.run_async(args={'source_url': LONG_URL}, tool_context=ctx))
        self.assertEqual(ctx.state[CONTROL]['verification_attempts'], 2)

    def test_retry_can_replace_only_nonofficial_leads(self):
        from google.adk.agents import LlmAgent
        from google.genai import types
        ctx = context(); registry = CandidateRegistry(ctx.state)
        other = candidate(); other['source_type'] = 'Other'
        registry.register([other])
        ctx.state[CONTROL] = {**ctx.state[CONTROL], 'search_attempts': 1}
        ctx.user_content = types.Content(role='user', parts=[types.Part(text='Actual question')])
        labels = ['CLAIM', 'SOURCE URL', 'SOURCE TYPE', 'SOURCE TITLE', 'APPARENT DATE OR CYCLE',
                  'DISCOVERY SUPPORT', 'DISCOVERY LIMITS', 'DISCOVERY STATUS']
        output = 'EVIDENCE CANDIDATE 1\n' + '\n\n'.join(
            label + ':\n' + value for label, value in zip(labels, candidate().values()))
        tool = DiscoveryRegistryTool(agent=LlmAgent(name='retry_discovery_test'))
        with patch('google.adk.tools.agent_tool.AgentTool.run_async', AsyncMock(return_value=output)):
            response = asyncio.run(tool.run_async(args={'request': 'research'}, tool_context=ctx))
        self.assertEqual(response['candidates'][0]['candidate_id'], 'C1')
        self.assertEqual(registry.get('C1').source_type, 'Official Morgan')


if __name__ == '__main__':
    unittest.main()
