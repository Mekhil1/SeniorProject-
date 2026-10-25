"""Actual local ADK Runner tests with mocked model responses; no cloud calls."""
import asyncio
import json
import unittest
from unittest.mock import patch
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import career_baseline as diagnostic
from test_career_shared_evidence import candidate, verification


class RunnerTests(unittest.TestCase):
    def run_case(self,domain,prompt,discovery_rows=None,checks=None,mode="current"):
        expected={'certification':'certification__technical_development_agent','interview':'interview_preparation_agent',
                  'trust':'trust__human_escalation_agent','career':'career_exploration_agent','research':'research__graduate_pathways_agent'}[domain]
        calls=[];verifications=iter(checks or [])
        async def model_generate(model,llm_request,stream=False):
            name=diagnostic.MODEL_AGENT.get();calls.append(name)
            if 'Orchestration' in name:
                part=types.Part(function_call=types.FunctionCall(name='transfer_to_agent',args={'agent_name':expected}))
            elif 'google_search' in name.lower():
                labels={'claim':'CLAIM','source_url':'SOURCE URL','source_type':'SOURCE TYPE','source_title':'SOURCE TITLE',
                    'apparent_date_or_cycle':'APPARENT DATE OR CYCLE','discovery_support':'DISCOVERY SUPPORT',
                    'discovery_limits':'DISCOVERY LIMITS','discovery_status':'DISCOVERY STATUS'}
                text='\n'.join('EVIDENCE CANDIDATE '+str(i)+'\n'+'\n'.join(labels[k]+': '+v for k,v in row.items()) for i,row in enumerate(discovery_rows or [],1))
                part=types.Part(text=text or 'NO CANDIDATES')
            elif 'url_context' in name.lower():part=types.Part(text=next(verifications))
            elif domain=='interview' and mode=='stable':part=types.Part(text='Practice fundamentals, technical scenarios and behavioral examples.')
            elif domain=='research':
                tool=list(llm_request.tools_dict)[0]
                part=types.Part(function_call=types.FunctionCall(name=tool,args={'candidate_id':'C'+str(calls.count(expected)-1)} if tool.startswith('verify_') else {'request':prompt}))
            elif domain=='career':part=types.Part(text='Explore defensive engineering and risk analysis through small projects.')
            else:raise AssertionError('Current parent should be bounded by Python; unexpected model request '+name)
            yield LlmResponse(content=types.Content(role='model',parts=[part]))
        case=dict(id='offline_wave4_'+domain,domain=domain,label=domain,mode=mode,expected=expected,prompt=prompt)
        async def run():
            with patch.object(Gemini,'generate_content_async',model_generate):
                with diagnostic.instrumentation():return await diagnostic.execute(case,15)
        result=asyncio.run(run())
        self.assertEqual(result['status'],'completed',result['errors']);self.assertTrue(result['route_match'])
        return result,calls

    def test_certification_two_authoritative_partial_pages(self):
        a=json.loads(verification(authority_host='www.comptia.org',page_evidence='Exam code TEST-123',facts={'exam_code':'TEST-123'}))
        b=json.loads(verification(authority_host='store.comptia.org',page_evidence='Standard exam list price 123.45 USD US',facts={'price':'123.45','currency':'USD','region':'US'}))
        result,calls=self.run_case('certification','What is the current CompTIA Security+ exam version and price?',
            [candidate('Exam code',url='https://www.comptia.org/exam'),candidate('List price',url='https://store.comptia.org/price')],
            [json.dumps(a),json.dumps(b)])
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(1,2))
        self.assertIn('TEST-123',result['final_answer']);self.assertIn('123.45 USD US',result['final_answer'])
        self.assertNotIn('certification__technical_development_agent',calls)

    def test_interview_official_and_anecdotal_sections(self):
        result,_=self.run_case('interview','What is the current Microsoft interview process?',
            [candidate('Official guide',url='https://careers.microsoft.com/guide'),dict(candidate('Reported experience',url='https://www.reddit.com/a'),source_type='anecdotal')],
            [verification('VERIFIED OFFICIAL',authority_host='careers.microsoft.com',supported_scope='General official candidate guidance only'),
             verification('ANECDOTAL / REPORTED',authority_host='www.reddit.com',supported_scope='A candidate reported a team-specific interview')])
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(1,2))
        text=result['final_answer'];self.assertIn('VERIFIED OFFICIAL',text);self.assertIn('ANECDOTAL / REPORTED',text)
        self.assertLess(text.index('General official'),text.index('### What candidates have reported'))

    def test_interview_stable_remains_tool_free(self):
        result,calls=self.run_case('interview','Give me a technical interview preparation strategy for an entry-level cybersecurity role.',mode='stable')
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(0,0))
        self.assertEqual(len(calls),2)

    def test_research_current_regression_statuses_and_unselected_candidate(self):
        rows=[candidate('Research activity, not an opening'),candidate('Funding not confirmed'),candidate('UNSELECTED SECRET CLAIM')]
        result,_=self.run_case('research','What current cybersecurity research opportunities are available at Morgan State?',rows,
            [verification('CURRENT STATUS UNVERIFIED'),verification('UNSUPPORTED')])
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(1,2))
        self.assertIn('CURRENT STATUS UNVERIFIED',result['final_answer']);self.assertIn('UNSUPPORTED',result['final_answer'])
        self.assertNotIn('UNSELECTED SECRET CLAIM',result['final_answer'])

    def test_trust_a_b_c_have_no_unnecessary_research(self):
        for prompt in ('I found conflicting information about whether this Morgan cybersecurity program is still active. Which source should I trust?',
                       'The sources disagree about whether I qualify for this opportunity and I could make an important decision based on it. How reliable is this information?',
                       'I need a human to review this because the available evidence is contradictory.'):
            result,calls=self.run_case('trust',prompt)
            self.assertEqual(len(calls),1);self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(0,0))
            self.assertIn('UNRESOLVED',result['final_answer'])
            self.assertIn('Human review is appropriate' if 'need a human' in prompt else 'Please supply',result['final_answer'])

    def test_trust_supplied_pair_two_checks_no_search(self):
        checks=[]
        for host,assertion in [('www.morgan.edu','Eligible'),('example.edu','Not eligible')]:
            out=json.loads(verification(authority_host=host));out.update(assertion=assertion,population='Undergraduates',version_cycle='2026');checks.append(json.dumps(out))
        result,_=self.run_case('trust','Eligibility conflict: <https://www.morgan.edu/a?q=%2F> <https://example.edu/b>',checks=checks)
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(0,2))
        self.assertIn('### ASSESSMENT\n\nUNRESOLVED',result['final_answer']);self.assertIn('https://www.morgan.edu/a?q=%2F',result['final_answer'])

    def test_career_stable_path_unchanged(self):
        result,_=self.run_case('career',"I'm interested in cloud security and risk management. What career paths should I explore?")
        self.assertEqual((result['search_helper_invocations'],result['url_context_invocations']),(0,0))
        self.assertIn('Explore defensive engineering',result['final_answer'])


if __name__=='__main__':unittest.main()
