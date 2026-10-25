"""Per-specialist stable/current ADK plumbing matrix with mocked model outputs.

These tests prove structural/tool/evidence plumbing, not actual LLM obedience.
Semantic mapping and selective live canaries complement these offline checks.
"""
import asyncio
import contextlib
import io
import json
import logging
import unittest
from unittest.mock import patch
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types
import career_baseline as b
from test_career_shared_evidence import candidate,verification

DOMAINS=('interview','research','networking','certification','internship','resume','roadmap')


class MatrixTests(unittest.TestCase):
    def check_path(self,domain,mode):
        lookup={x[0]:x for x in b.DOMAINS};spec=lookup[domain]
        expected=spec[2];prompt=spec[3 if mode=='stable' else 4]
        if domain=='interview' and mode=='current':prompt='What is the current interview process for an entry-level cybersecurity role at Microsoft?'
        if domain=='research' and mode=='stable':prompt='What are the general steps to prepare for graduate cybersecurity research? Focus on research readiness, not current programs.'
        calls=[];checks=[]
        url1='https://www.morgan.edu/a?q=%2F&v=1';url2='https://www.morgan.edu/b?q=%26'
        if domain=='certification':url1='https://www.comptia.org/exam';url2='https://store.comptia.org/exam'
        if domain=='interview':url1='https://careers.microsoft.com/guide';url2='https://www.reddit.com/report'
        structured=domain in {'interview','research','networking','certification'}
        async def generate(model,llm_request,stream=False):
            name=b.MODEL_AGENT.get();calls.append(name)
            if 'Orchestration' in name:
                part=types.Part(function_call=types.FunctionCall(name='transfer_to_agent',args={'agent_name':expected}))
            elif 'google_search' in name.lower():
                if structured:
                    rows=[candidate('Exact requested scope only',url1),candidate('Second selected scope only',url2)]
                    if domain=='interview':rows[1]['source_type']='anecdotal'
                    labels={'claim':'CLAIM','source_url':'SOURCE URL','source_type':'SOURCE TYPE','source_title':'SOURCE TITLE','apparent_date_or_cycle':'APPARENT DATE OR CYCLE','discovery_support':'DISCOVERY SUPPORT','discovery_limits':'DISCOVERY LIMITS','discovery_status':'DISCOVERY STATUS'}
                    output='\n'.join('EVIDENCE CANDIDATE '+str(i)+'\n'+'\n'.join(labels[k]+': '+v for k,v in row.items()) for i,row in enumerate(rows,1))
                else:output='Selected authoritative source: '+url1+'; requested current fact not established.'
                part=types.Part(text=output)
            elif 'url_context' in name.lower():
                checks.append(name);index=len(checks)
                if structured:
                    status=('CURRENT STATUS UNVERIFIED' if index==1 else 'HISTORICAL')
                    if domain=='interview':status='VERIFIED OFFICIAL' if index==1 else 'ANECDOTAL / REPORTED'
                    host='careers.microsoft.com' if domain=='interview' and index==1 else 'www.reddit.com' if domain=='interview' else 'www.comptia.org' if domain=='certification' and index==1 else 'store.comptia.org' if domain=='certification' else 'www.morgan.edu'
                    part=types.Part(text=verification(status,authority_host=host))
                else:part=types.Part(text='CURRENT STATUS UNVERIFIED; exact selected URL '+url1)
            elif mode=='stable':part=types.Part(text='Prioritize a manageable plan using real student experience, general practice and next steps; no current external claims.')
            else:
                number=calls.count(expected)
                if number==1:
                    tool=next(n for n in llm_request.tools_dict if n.endswith('google_search_agent'));args={'request':prompt}
                elif structured:
                    tool=next(n for n in llm_request.tools_dict if n.startswith('verify_'));args={'candidate_id':'C'+str(number-1)}
                elif number==2:
                    tool=next(n for n in llm_request.tools_dict if n.endswith('url_context_agent'));args={'request':'Inspect exactly '+url1}
                else:
                    yield LlmResponse(content=types.Content(role='model',parts=[types.Part(text='CURRENT STATUS UNVERIFIED — no current requirement or availability asserted. Source: '+url1)]));return
                part=types.Part(function_call=types.FunctionCall(name=tool,args=args))
            yield LlmResponse(content=types.Content(role='model',parts=[part]))
        case=dict(id='offline_wave5_'+domain+'_'+mode,domain=domain,label=domain,mode=mode,expected=expected,prompt=prompt)
        async def run():
            with patch.object(Gemini,'generate_content_async',generate):
                with b.instrumentation():return await b.execute(case,15)
        with contextlib.redirect_stdout(io.StringIO()):r=asyncio.run(run())
        self.assertEqual(r['status'],'completed',r['errors']);self.assertTrue(r['route_match'])
        if mode=='stable':
            self.assertEqual((r['search_helper_invocations'],r['url_context_invocations']),(0,0))
            self.assertNotIn('VERIFIED CURRENT',r['final_answer'])
        else:
            self.assertEqual(r['search_helper_invocations'],1)
            self.assertEqual(r['url_context_invocations'],2 if structured else 1)
            if domain=='interview':
                self.assertIn('VERIFIED OFFICIAL',r['final_answer']);self.assertIn('ANECDOTAL / REPORTED',r['final_answer'])
                self.assertIn('varies by team',r['final_answer'])
            elif domain in {'research','networking'}:
                self.assertIn('CURRENT STATUS UNVERIFIED',r['final_answer']);self.assertIn('HISTORICAL',r['final_answer'])
                self.assertIn(url1,r['final_answer']);self.assertIn(url2,r['final_answer'])
                self.assertNotIn('VERIFIED CURRENT',r['final_answer'])
            else:self.assertIn('CURRENT STATUS UNVERIFIED',r['final_answer'])


def test_for(domain,mode):
    def test(self):self.check_path(domain,mode)
    return test

for domain in DOMAINS:
    for mode in ('stable','current'):setattr(MatrixTests,'test_'+domain+'_'+mode,test_for(domain,mode))

if __name__=='__main__':unittest.main()
