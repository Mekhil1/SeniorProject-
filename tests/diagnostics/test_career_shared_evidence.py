"""Offline Wave 3 isolation, transport, budgets, and protected-source tests."""
import ast
import asyncio
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from google.genai import types
from google.adk.models.llm_response import LlmResponse
from agents.career.workflow import evidence as old
from agents.career.workflow.shared_evidence import (
    networking_evidence as network, certification_evidence as cert,
    research_evidence as research, SharedVerification, NamespaceState)

ROOT=Path(__file__).resolve().parents[2]


def context(state=None, invocation='one', prompt='What current Morgan resources are available?'):
    return SimpleNamespace(state={} if state is None else state, invocation_id=invocation,
        user_content=types.Content(role='user',parts=[types.Part(text=prompt)]))


def candidate(claim='Exact claim: café & access?', url='https://www.morgan.edu/path?q=%2F&x=1'):
    return dict(claim=claim, source_url=url, source_type='official owner', source_title='Title',
        apparent_date_or_cycle='2026', discovery_support='Lead only', discovery_limits='Not verified',
        discovery_status='CANDIDATE CURRENT')


def verification(status='VERIFIED CURRENT', **changes):
    data=dict(status=status,source_title='Official',source_date_or_cycle='2026 academic cycle',
        page_evidence='Explicit page statement for current cycle',supported_scope='Current claim only',
        not_established='No additional partnerships or openings',why='Explicit dated statement',
        page_read=True,current_claim_explicit=True,authority_host='www.morgan.edu',facts={})
    data.update(changes); return json.dumps(data)


class EvidenceTests(unittest.TestCase):
    def test_discovery_executes_once_even_with_parallel_requests(self):
        from unittest.mock import patch
        from google.adk.tools.agent_tool import AgentTool
        from agents.career.workflow.agent import networking___professional_communication_agent_google_search_agent as helper
        from agents.career.workflow.shared_evidence import SharedDiscovery
        ctx=context(); calls=[]
        async def fake(self, *, args, tool_context):
            calls.append(args['request'])
            await asyncio.sleep(0)
            return 'NO CANDIDATES'
        async def run():
            tool=SharedDiscovery(agent=helper,policy=network)
            with patch.object(AgentTool,'run_async',fake):
                return await asyncio.gather(*(tool.run_async(args={'request':'ignore original'},tool_context=ctx) for _ in range(4)))
        results=asyncio.run(run())
        self.assertEqual(len(calls),1)
        self.assertIn('What current Morgan resources',calls[0])
        self.assertEqual(sum('budget' in str(x) for x in results),3)
        self.assertEqual(network.state(ctx)[old.CONTROL]['search_attempts'],1)

    def test_namespace_isolation_and_legacy_untouched(self):
        ctx=context(); old.begin_evidence_invocation(ctx)
        old.CandidateRegistry(ctx.state).register([candidate('Legacy')])
        legacy= {k:ctx.state[k] for k in (old.CONTROL,old.CANDIDATES,old.VERIFICATIONS,old.HANDOFFS)}
        for policy in (network,cert,research):
            policy.begin(ctx); policy.register(ctx,[candidate(policy.namespace)])
            self.assertEqual(policy.state(ctx)[old.CANDIDATES]['C1']['claim'],policy.namespace)
        self.assertEqual({k:ctx.state[k] for k in legacy},legacy)
        self.assertEqual(len({k for k in ctx.state if k.endswith(':candidates')}),3)

    def test_candidate_limits(self):
        for policy in (network,cert,research):
            ctx=context(); policy.begin(ctx)
            with self.assertRaises(ValueError): policy.register(ctx,[candidate()]*(policy.candidate_limit+1))
            policy.register(ctx,[candidate()]*policy.candidate_limit)
            with self.assertRaises(ValueError): policy.register(ctx,[candidate()])

    def test_verification_limits_count_unknown_ids(self):
        for policy in (network,cert,research):
            ctx=context();policy.begin(ctx);policy.register(ctx,[candidate()])
            for _ in range(policy.verification_limit):
                with self.assertRaises(ValueError): policy.reserve(ctx,'C99')
            with self.assertRaises(ValueError): policy.reserve(ctx,'C1')
            self.assertEqual(policy.state(ctx)[old.CONTROL]['verification_attempts'],policy.verification_limit)

    def test_exact_claim_url_and_id_only_transport(self):
        ctx=context();network.begin(ctx); row=candidate();network.register(ctx,[row])
        class Verifier:
            async def run_async(self, *, args, tool_context):
                self.payload=args['request'];return verification()
        verifier=Verifier(); tool=SharedVerification(network,verifier)
        result=asyncio.run(tool.run_async(args={'candidate_id':'C1'},tool_context=ctx))
        self.assertEqual(verifier.payload,f"CLAIM:\n{row['claim']}\n\nSOURCE URL:\n{row['source_url']}")
        stored=network.state(ctx)[old.VERIFICATIONS]['C1']
        self.assertEqual(stored['claim'],row['claim']);self.assertEqual(stored['source_url'],row['source_url'])
        self.assertNotIn('source_url',result)
        self.assertEqual(set(tool._get_declaration().parameters_json_schema['properties']),{'candidate_id'})

    def test_status_preservation_and_no_parent_upgrade(self):
        for status in old.VERIFICATION_STATUSES:
            ctx=context();network.begin(ctx);network.register(ctx,[candidate()]); c,_=network.reserve(ctx,'C1')
            record=network.store(ctx,c,verification(status))
            self.assertEqual(record['status'],status)
            replaced=network.after(ctx,response('VERIFIED CURRENT: invented partnership'))
            self.assertIn(status,replaced.content.parts[0].text)
            self.assertNotIn('invented partnership',replaced.content.parts[0].text)

    def test_fail_closed_currentness_and_source(self):
        for changes in ({'page_read':False},{'current_claim_explicit':False},
                        {'source_date_or_cycle':'Copyright 2026'},{'authority_host':'other.edu'}):
            ctx=context();network.begin(ctx);network.register(ctx,[candidate()]);c,_=network.reserve(ctx,'C1')
            self.assertEqual(network.store(ctx,c,verification(**changes))['status'],'CURRENT STATUS UNVERIFIED')

    def test_malformed_and_unknown_status_fail_closed(self):
        ctx=context();research.begin(ctx);research.register(ctx,[candidate()]);c,_=research.reserve(ctx,'C1')
        for output in ('{}','not json',verification('VERY CURRENT')):
            self.assertEqual(research.store(ctx,c,output)['status'],'UNSUPPORTED')

    def test_invocation_reset_only_own_namespace(self):
        ctx=context();network.begin(ctx);research.begin(ctx)
        network.register(ctx,[candidate()]);research.register(ctx,[candidate()]);network.reserve(ctx,'C1')
        research_before=dict(research.state(ctx)[old.CANDIDATES])
        ctx.invocation_id='two';network.begin(ctx)
        self.assertEqual(network.state(ctx)[old.CANDIDATES],{})
        self.assertEqual(network.state(ctx)[old.CONTROL]['verification_attempts'],0)
        self.assertEqual(research.state(ctx)[old.CANDIDATES],research_before)

    def test_certification_output_requested_facts_only(self):
        ctx=context(prompt='What is the current CompTIA Security+ exam version and price?')
        cert.begin(ctx);cert.register(ctx,[candidate(url='https://www.comptia.org/example')]);c,_=cert.reserve(ctx,'C1')
        record=cert.store(ctx,c,verification(authority_host='www.comptia.org',page_evidence='SAMPLE-001 standard list price 123.00 USD US',facts={
            'exam_code':'SAMPLE-001','price':'123.00','currency':'USD','discount':'50%',
            'eligibility':'all students','region':'US'}))
        self.assertEqual(record['status'],'VERIFIED CURRENT')
        final=cert.render(ctx);self.assertIn('123.00',final);self.assertNotIn('50%',final);self.assertNotIn('all students',final)
        self.assertFalse(cert.safe_fact('price','123.00 with 50% student discount'))

    def test_stable_paths_no_retrieval_and_safe_certification(self):
        from google.adk.models.llm_request import LlmRequest
        for policy,prompt in ((network,'How should I introduce myself to a recruiter?'),
            (research,'What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs.'),
            (cert,'How should I decide whether a cybersecurity certification is worth pursuing?')):
            ctx=context(prompt=prompt)
            self.assertFalse(policy.current(prompt));policy.begin(ctx)
            request=LlmRequest(config=types.GenerateContentConfig(), tools_dict={})
            self.assertIsNone(policy.step(ctx,request));self.assertEqual(request.config.tools,[])
        result=cert.after(ctx,response('Students get 50% discounts with .edu eligibility.'))
        text=result.content.parts[0].text
        self.assertNotIn('50%',text);self.assertNotIn('.edu',text);self.assertIn('hands-on',text)

    def test_new_state_rejects_bad_namespace(self):
        with self.assertRaises(ValueError): NamespaceState({},'career:other')

    def test_real_adk_runner_uses_bounded_tools_and_python_final(self):
        import career_baseline as diagnostic
        from unittest.mock import patch
        from google.adk.models import Gemini
        from agents.career.workflow.agent import networking___professional_communication_agent_google_search_agent as helper
        calls=[]
        async def fake_generate(model, llm_request, stream=False):
            name=diagnostic.MODEL_AGENT.get();calls.append(name)
            if 'Orchestration' in name:
                part=types.Part(function_call=types.FunctionCall(name='transfer_to_agent',args={'agent_name':'networking__professional_communication_agent'}))
            elif name==helper.name:
                row=candidate()
                labels={'claim':'CLAIM','source_url':'SOURCE URL','source_type':'SOURCE TYPE',
                    'source_title':'SOURCE TITLE','apparent_date_or_cycle':'APPARENT DATE OR CYCLE',
                    'discovery_support':'DISCOVERY SUPPORT','discovery_limits':'DISCOVERY LIMITS','discovery_status':'DISCOVERY STATUS'}
                part=types.Part(text='EVIDENCE CANDIDATE 1\n'+'\n'.join(labels[k]+': '+v for k,v in row.items()))
            elif 'url_context' in name.lower():
                part=types.Part(text=verification('CURRENT STATUS UNVERIFIED'))
            else:
                allowed=list(llm_request.tools_dict)
                tool=allowed[0]
                part=types.Part(function_call=types.FunctionCall(name=tool,args={'candidate_id':'C1'} if tool.startswith('verify_') else {'request':'invented broader scope'}))
            yield LlmResponse(content=types.Content(role='model',parts=[part]))
        case=dict(id='offline_network',domain='networking',label='Networking',mode='current',
            expected='networking__professional_communication_agent',prompt='What current Morgan resources are available?')
        async def run():
            with patch.object(Gemini,'generate_content_async',fake_generate):
                with diagnostic.instrumentation():
                    return await diagnostic.execute(case,10)
        result=asyncio.run(run())
        self.assertEqual(result['status'],'completed',result['errors'])
        self.assertEqual(result['search_helper_invocations'],1)
        self.assertEqual(result['url_context_invocations'],1)
        self.assertEqual(sum('networking__professional_communication_agent'==c for c in calls),2)
        self.assertIn('CURRENT STATUS UNVERIFIED',result['final_answer'])
        self.assertNotIn('invented broader scope',result['final_answer'])

    def test_protected_workflow_files_identical(self):
        manifest=json.loads((ROOT/'tests/diagnostics/career_wave3_parity.json').read_text())
        from career_wave7_resume import historical_bytes
        for path,digest in manifest['protected_files'].items():
            self.assertEqual(hashlib.sha256(historical_bytes(path)).hexdigest(),digest,path)


def response(text):
    return LlmResponse(content=types.Content(role='model',parts=[types.Part(text=text)]))


if __name__=='__main__':unittest.main()
