"""Mocked model samples prove contract delivery/plumbing, not LLM obedience."""
import asyncio
import contextlib
import io
import unittest
from unittest.mock import patch
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import career_baseline as b
from career_wave65 import RULE,TARGET
from test_career_shared_evidence import candidate,verification

PROMPT='How should I introduce myself to a cybersecurity recruiter?'
CURRENT="What is LinkedIn's current connection-request note character limit?"


class NetworkingPatchTests(unittest.TestCase):
    def run_sample(self,answer,current=False,prompt=PROMPT):
        calls=[];delivered=[]
        async def generate(model,llm_request,stream=False):
            name=b.MODEL_AGENT.get();calls.append(name)
            if 'Orchestration' in name:
                part=types.Part(function_call=types.FunctionCall(name='transfer_to_agent',args={'agent_name':TARGET}))
            elif 'google_search' in name.lower():
                row=candidate('Exact platform limit not established','https://www.linkedin.com/help/linkedin')
                labels={'claim':'CLAIM','source_url':'SOURCE URL','source_type':'SOURCE TYPE','source_title':'SOURCE TITLE',
                    'apparent_date_or_cycle':'APPARENT DATE OR CYCLE','discovery_support':'DISCOVERY SUPPORT','discovery_limits':'DISCOVERY LIMITS','discovery_status':'DISCOVERY STATUS'}
                part=types.Part(text='EVIDENCE CANDIDATE 1\n'+'\n'.join(labels[k]+': '+v for k,v in row.items()))
            elif 'url_context' in name.lower():
                part=types.Part(text=verification('UNSUPPORTED',authority_host='www.linkedin.com'))
            else:
                delivered.append(str(llm_request.config.system_instruction))
                self.assertIn(RULE.strip(),delivered[-1])
                if not current:
                    self.assertFalse(any('google_search' in k or k.startswith('verify_') for k in llm_request.tools_dict))
                    part=types.Part(text=answer)
                elif calls.count(TARGET)==1:
                    name=next(k for k in llm_request.tools_dict if k.endswith('google_search_agent'))
                    part=types.Part(function_call=types.FunctionCall(name=name,args={'request':CURRENT}))
                else:
                    name=next(k for k in llm_request.tools_dict if k.startswith('verify_'))
                    part=types.Part(function_call=types.FunctionCall(name=name,args={'candidate_id':'C1'}))
            yield LlmResponse(content=types.Content(role='model',parts=[part]))
        case=dict(id='offline_wave65',domain='networking',label='Networking',expected=TARGET,
                  mode='current' if current else 'stable',prompt=CURRENT if current else prompt)
        async def execute():
            with patch.object(Gemini,'generate_content_async',generate),b.instrumentation():return await b.execute(case,15)
        with contextlib.redirect_stdout(io.StringIO()):r=asyncio.run(execute())
        self.assertEqual(r['status'],'completed',r['errors']);self.assertTrue(r['route_match'])
        if not current:
            self.assertTrue(delivered);self.assertEqual(r['final_answer'],answer)
            self.assertEqual((r['search_helper_invocations'],r['url_context_invocations']),(0,0))
        else:
            self.assertEqual((r['search_helper_invocations'],r['url_context_invocations']),(1,1))
            self.assertIn('UNSUPPORTED',r['final_answer']);self.assertNotIn('VERIFIED CURRENT',r['final_answer'])
        return r

    def test_brief_personalized_template(self):
        self.run_sample('Keep it brief and personalize the note: Hi [Name], I am exploring cybersecurity and would value learning about your team.')

    def test_concise_context_and_reason(self):
        self.run_sample("Keep it concise; mention why you're reaching out, your real experience, and one low-pressure question.")

    def test_followup_without_inmail_product_claims(self):
        self.run_sample('Personalize the note, refer to your actual conversation, and politely ask whether a follow-up would be welcome.')

    def test_user_supplied_fact_attributed_not_independently_verified(self):
        # Tests the permitted attribution wording, without declaring any limit true.
        self.run_sample('Use the constraint you supplied as your own drafting requirement; I have not independently verified a platform limit. Keep the note concise.',
            prompt='For my recruiter introduction, I supply a personal drafting budget of 123 characters. Please use it without treating it as a verified platform rule.')

    def test_exact_current_platform_question_can_retrieve_and_fail_closed(self):
        from agents.career.workflow.shared_evidence import networking_evidence
        self.assertTrue(networking_evidence.current(CURRENT))
        self.run_sample('',current=True)


if __name__=='__main__':unittest.main()
