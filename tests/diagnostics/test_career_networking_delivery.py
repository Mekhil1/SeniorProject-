"""Offline captured-case and generalized Networking delivery regressions."""
import ast
import asyncio
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from agents.career.workflow import shared_evidence as shared
from test_career_shared_evidence import candidate,context,verification
import career_baseline as diagnostic

BASE=Path(__file__).resolve().parent
FIXTURE=json.loads((BASE/'career_networking_delivery_fixture.json').read_text(encoding='utf8'))


class DeliveryTests(unittest.TestCase):
    def adjudicate(self,claim,evidence,**changes):
        ctx=context(prompt='What current networking resources are available during Fall 2026?')
        p=shared.networking_evidence;p.begin(ctx);p.register(ctx,[candidate(claim,FIXTURE['source_url'])]);c,_=p.reserve(ctx,'C1')
        data=json.loads(verification(page_evidence=evidence,supported_scope=claim));data.update(changes)
        return p.store(ctx,c,json.dumps(data)),p.render(ctx)

    def test_captured_sacs_compound_is_not_verified_current(self):
        f=FIXTURE;r,text=self.adjudicate(f['claim'],f['verification']['page_evidence'])
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')
        self.assertEqual(r['reported_status'],'VERIFIED CURRENT')
        self.assertIn('Students are invited to join SACS',r['networking_supported_scope'])
        self.assertNotIn('mentoring',r['networking_supported_scope'])
        self.assertIn('Supported narrower source scope',text);self.assertNotIn('— VERIFIED CURRENT',text)
        self.assertEqual(r['source_url'],f['source_url'])

    def test_membership_only_can_remain_supported(self):
        r,_=self.adjudicate('Students are invited to join SACS.',FIXTURE['verification']['page_evidence'])
        self.assertEqual(r['status'],'VERIFIED CURRENT')

    def test_all_aspirational_wordings_reject_current_mentorship(self):
        for text in ('aims to provide mentorship','seeks to provide mentorship','strives to provide mentorship',
                     'The goal is to provide mentorship','Our vision includes mentorship','Our mission includes mentorship',
                     'intends to provide mentorship','designed to provide mentorship','planned mentorship benefits',
                     'expected mentorship benefits','The vision provides opportunities to receive mentorship'):
            with self.subTest(text=text):
                r,_=self.adjudicate('Students currently receive mentorship.',text)
                self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_mission_does_not_prove_employer_partnerships(self):
        r,_=self.adjudicate('Current employer partnerships provide industry access.','Our mission is to connect students with industry.')
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_historical_workshops_not_current_2026(self):
        r,_=self.adjudicate('Workshops are currently available in 2026.','Hosted workshops in 2024.')
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_explicit_current_registration_can_qualify(self):
        r,_=self.adjudicate('Students can register for mentoring.','Students can register for weekly mentoring sessions during Fall 2026.')
        self.assertEqual(r['status'],'VERIFIED CURRENT')

    def test_compound_retains_only_directly_supported_parts(self):
        r,_=self.adjudicate('SACS exists and provides mentoring and workshops.',
            'SACS exists. Students can register for weekly mentoring sessions during Fall 2026; the vision aims to offer workshops.')
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')
        self.assertIn('SACS exists',r['networking_supported_scope']);self.assertIn('can register',r['networking_supported_scope'])
        self.assertNotIn('workshops',r['networking_supported_scope'])

    def test_goal_heading_cannot_launder_operational_looking_bullets(self):
        r,_=self.adjudicate('Students receive mentoring.','Our Goals:\nProvides weekly mentoring.')
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_mission_statement_is_not_a_delivery_claim(self):
        r,_=self.adjudicate('The stated mission is to provide mentorship.','Our mission is to provide mentorship.')
        self.assertEqual(r['status'],'VERIFIED CURRENT')

    def test_goal_prefix_cannot_hide_a_current_delivery_assertion(self):
        r,_=self.adjudicate('The mission includes mentorship and students currently receive mentoring.',
                            'Our mission aims to provide mentorship.')
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_negation_and_wrong_cycle_cannot_qualify(self):
        for text in ('Mentoring is not currently available.','Students can register for mentoring in Fall 2024.'):
            with self.subTest(text=text):
                r,_=self.adjudicate('Mentoring is currently available.',text)
                self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_normal_authority_date_readability_checks_still_required(self):
        for change in ({'page_read':False},{'authority_host':'unrelated.edu'},{'source_date_or_cycle':'UNKNOWN'},{'current_claim_explicit':False}):
            with self.subTest(change=change):
                r,_=self.adjudicate('Mentoring is currently available.','Students can register for weekly mentoring during Fall 2026.',**change)
                self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')

    def test_nothing_upgrades_historical_or_unsupported(self):
        for status in ('HISTORICAL','UNSUPPORTED','CURRENT STATUS UNVERIFIED'):
            r,_=self.adjudicate('Mentoring is available.','Students can register for weekly mentoring during Fall 2026.',status=status)
            self.assertEqual(r['status'],status)

    def test_mock_stable_platform_boundary_and_usefulness(self):
        import test_career_wave65_runner as previous
        previous.NetworkingPatchTests().run_sample('Keep it brief, personalize the note, and mention why you are reaching out.')

    def test_real_runner_captured_current_flow_fails_closed(self):
        expected='networking__professional_communication_agent';calls=[]
        async def generate(model,llm_request,stream=False):
            name=diagnostic.MODEL_AGENT.get();calls.append(name)
            if 'Orchestration' in name:
                part=types.Part(function_call=types.FunctionCall(name='transfer_to_agent',args={'agent_name':expected}))
            elif 'google_search' in name.lower():
                row=candidate(FIXTURE['claim'],FIXTURE['source_url'])
                labels={'claim':'CLAIM','source_url':'SOURCE URL','source_type':'SOURCE TYPE','source_title':'SOURCE TITLE','apparent_date_or_cycle':'APPARENT DATE OR CYCLE','discovery_support':'DISCOVERY SUPPORT','discovery_limits':'DISCOVERY LIMITS','discovery_status':'DISCOVERY STATUS'}
                part=types.Part(text='EVIDENCE CANDIDATE 1\n'+'\n'.join(labels[k]+': '+v for k,v in row.items()))
            elif 'url_context' in name.lower():part=types.Part(text=json.dumps(FIXTURE['verification']))
            else:
                tool=next(k for k in llm_request.tools_dict if k.endswith('google_search_agent') or k.startswith('verify_'))
                args={'request':'Current Morgan networking resources'} if tool.endswith('google_search_agent') else {'candidate_id':'C1'}
                part=types.Part(function_call=types.FunctionCall(name=tool,args=args))
            yield LlmResponse(content=types.Content(role='model',parts=[part]))
        case=dict(id='offline_delivery_capture',domain='networking',label='Networking',expected=expected,mode='current',prompt='What current networking resources can Morgan State Computer Science students use?')
        async def run():
            with patch.object(Gemini,'generate_content_async',generate),diagnostic.instrumentation():return await diagnostic.execute(case,15)
        with contextlib.redirect_stdout(io.StringIO()):r=asyncio.run(run())
        self.assertEqual(r['status'],'completed',r['errors']);self.assertTrue(r['route_match'])
        self.assertEqual((r['search_helper_invocations'],r['url_context_invocations']),(1,1))
        self.assertIn('CURRENT STATUS UNVERIFIED',r['final_answer']);self.assertIn('invited to join SACS',r['final_answer'])
        self.assertNotIn('— VERIFIED CURRENT',r['final_answer'])

    def test_non_networking_policy_methods_and_prompt_constants_unchanged(self):
        m=json.loads((BASE/'career_networking_delivery_parity.json').read_text())
        before=ast.parse(m['entry_shared_source']);after=ast.parse((BASE.parents[1]/'agents/career/workflow/shared_evidence.py').read_bytes())
        def rest(tree):
            tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='_networking_delivery_support']
            for n in tree.body:
                if isinstance(n,ast.ClassDef) and n.name=='EvidencePolicy':n.body=[f for f in n.body if getattr(f,'name','') not in ('store','render')]
            return ast.dump(tree)
        self.assertEqual(rest(before),rest(after))

    def test_research_base_store_and_render_equal_original_implementation(self):
        m=json.loads((BASE/'career_networking_delivery_parity.json').read_text())
        tree=ast.parse(m['entry_shared_source']);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EvidencePolicy')
        methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('store','render')]
        scope=dict(shared.__dict__);exec(compile(ast.Module(body=methods,type_ignores=[]),'original_shared_methods','exec'),scope)
        policy=shared.research_evidence;results=[]
        for old in (True,False):
            ctx=context();policy.begin(ctx);policy.register(ctx,[candidate('Mentorship is currently available.')]);c,_=policy.reserve(ctx,'C1')
            output=verification(page_evidence='The mission aims to provide mentorship.')
            r=scope['store'](policy,ctx,c,output) if old else policy.store(ctx,c,output)
            text=scope['render'](policy,ctx) if old else policy.render(ctx)
            results.append((r,text))
        self.assertEqual(results[0],results[1])


if __name__=='__main__':unittest.main()
