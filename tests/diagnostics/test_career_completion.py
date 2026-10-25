"""Offline domain completion contracts; fake evidence only."""
import asyncio
import json
from types import SimpleNamespace
import unittest
from google.genai import types
from agents.career.workflow import evidence as old
from agents.career.workflow.shared_evidence import certification_evidence as cert, interview_evidence as interview, trust_evidence as trust, networking_evidence as network, research_evidence as research, SharedVerification
from test_career_shared_evidence import candidate, context, verification, response


class CompletionTests(unittest.TestCase):
    def test_all_namespaces_and_reset(self):
        ctx=context(prompt='Current Microsoft CompTIA evidence')
        for policy in (cert,interview,trust,network,research):
            policy.begin(ctx);policy.register(ctx,[candidate(policy.namespace)])
        self.assertEqual(len([k for k in ctx.state if k.endswith(':candidates')]),5)
        ctx.invocation_id='next';interview.begin(ctx)
        self.assertEqual(interview.state(ctx)[old.CANDIDATES],{})
        self.assertTrue(cert.state(ctx)[old.CANDIDATES])

    def test_budgets_all_targets_and_invalid_ids(self):
        for policy in (cert,interview,trust):
            ctx=context();policy.begin(ctx)
            with self.assertRaises(ValueError):policy.register(ctx,[candidate()]*(policy.candidate_limit+1))
            policy.register(ctx,[candidate()]*policy.candidate_limit)
            for _ in range(2):
                with self.assertRaises(ValueError):policy.reserve(ctx,'UNKNOWN')
            with self.assertRaises(ValueError):policy.reserve(ctx,'C1')

    def test_certification_partial_fact_and_missing_price(self):
        ctx=context(prompt='What is the current CompTIA Security+ exam version and price?');cert.begin(ctx)
        cert.register(ctx,[candidate('Exam code only',url='https://www.comptia.org/exam')]);c,_=cert.reserve(ctx,'C1')
        out=json.loads(verification('CURRENT STATUS UNVERIFIED',authority_host='www.comptia.org',source_date_or_cycle='UNKNOWN',current_claim_explicit=False,
            page_evidence='The current exam code is TEST-123.',facts={'exam_code':'TEST-123'}))
        out['fact_statuses']={'exam_code':'VERIFIED CURRENT'};out['fact_evidence']={'exam_code':'The current exam code is TEST-123.'}
        r=cert.store(ctx,c,json.dumps(out));self.assertEqual(r['fact_statuses']['exam_code'],'VERIFIED CURRENT')
        text=cert.render(ctx);self.assertIn('TEST-123',text);self.assertIn('### Price\n\n**CURRENT STATUS UNVERIFIED**',text)
        self.assertEqual(r['claim'],'Exam code only')

    def test_certification_value_requires_literal_evidence(self):
        ctx=context(prompt='Current CompTIA exam price');cert.begin(ctx);cert.register(ctx,[candidate(url='https://www.comptia.org/price')]);c,_=cert.reserve(ctx,'C1')
        out=verification(authority_host='www.comptia.org',facts={'price':'999.99','discount':'50%'})
        cert.store(ctx,c,out);text=cert.render(ctx)
        self.assertNotIn('999.99',text);self.assertNotIn('50%',text)

    def test_interview_statuses_never_upgraded(self):
        for status in ('VERIFIED OFFICIAL','ANECDOTAL / REPORTED','CURRENT STATUS UNVERIFIED','HISTORICAL','UNSUPPORTED'):
            ctx=context(prompt='What is the current Microsoft interview process?');interview.begin(ctx)
            interview.register(ctx,[candidate('Documented role scope',url='https://careers.microsoft.com/guide')]);c,_=interview.reserve(ctx,'C1')
            r=interview.store(ctx,c,verification(status,authority_host='careers.microsoft.com'))
            self.assertEqual(r['status'],status)
            final=interview.after(ctx,response('All stages are verified and universal.')).content.parts[0].text
            self.assertIn(status,final);self.assertNotIn('All stages are verified',final)

    def test_interview_one_anecdotal_candidate_hard_limit(self):
        ctx=context(prompt='Current Microsoft process');interview.begin(ctx)
        rows=[dict(candidate('Anecdote '+str(i),url='https://www.reddit.com/'+str(i)),source_type='anecdotal') for i in range(3)]
        summaries=interview.register(ctx,rows)
        self.assertEqual(len(summaries),1)
        self.assertEqual(interview.state(ctx)[old.CANDIDATES]['C1']['claim'],'Anecdote 0')

    def test_anecdote_cannot_be_official(self):
        ctx=context(prompt='Current Microsoft interview process');interview.begin(ctx)
        interview.register(ctx,[dict(candidate(url='https://www.reddit.com/example'),source_type='anecdotal')]);c,_=interview.reserve(ctx,'C1')
        r=interview.store(ctx,c,verification('VERIFIED OFFICIAL',authority_host='www.reddit.com'))
        self.assertEqual(r['status'],'CURRENT STATUS UNVERIFIED')
        self.assertNotIn('Current claim only',interview.render(ctx))

    def test_historical_cannot_become_official_current(self):
        ctx=context(prompt='Current Microsoft interview process');interview.begin(ctx)
        interview.register(ctx,[dict(candidate(url='https://careers.microsoft.com/archive'),discovery_status='POSSIBLY HISTORICAL')]);c,_=interview.reserve(ctx,'C1')
        self.assertEqual(interview.store(ctx,c,verification('VERIFIED OFFICIAL',authority_host='careers.microsoft.com'))['status'],'HISTORICAL')

    def test_trust_supplied_pair_skips_search_and_preserves_exact_urls(self):
        urls=['https://www.morgan.edu/a?q=%2F&x=1','https://www.morgan.edu/b?q=%26']
        ctx=context(prompt='Conflicting eligibility: <'+urls[0]+'> and <'+urls[1]+'>');trust.begin(ctx)
        self.assertEqual([c['source_url'] for c in trust.state(ctx)[old.CANDIDATES].values()],urls)
        request=SimpleNamespace(tools_dict={})
        call=trust.step(ctx,request).content.parts[0].function_call
        self.assertEqual(call.name,'verify_trust_candidate');self.assertEqual(call.args,{'candidate_id':'C1'})
        self.assertEqual(trust.state(ctx)[old.CONTROL]['search_attempts'],0)
        c,payload=trust.reserve(ctx,'C1');self.assertIn(urls[0],payload);self.assertEqual(c.claim,ctx.user_content.parts[0].text)

    def test_trust_human_immediate_and_underspecified_asks_sources(self):
        for prompt in ('I need a human to review this because the available evidence is contradictory.',
                       'I found conflicting information about whether this Morgan cybersecurity program is still active. Which source should I trust?'):
            ctx=context(prompt=prompt);text=trust.step(ctx,SimpleNamespace(tools_dict={})).content.parts[0].text
            self.assertIn('UNRESOLVED',text);self.assertEqual(trust.state(ctx)[old.CONTROL]['search_attempts'],0)
        self.assertIn('Please supply',text)

    def test_trust_authority_alone_not_resolution(self):
        ctx=context(prompt='Eligibility conflict https://www.morgan.edu/a https://example.edu/b');trust.begin(ctx)
        for cid,statement in [('C1','Eligible'),('C2','Not eligible')]:
            c,_=trust.reserve(ctx,cid);out=json.loads(verification(authority_host='www.morgan.edu' if cid=='C1' else 'example.edu'))
            out.update(assertion=statement,population='Undergraduates',version_cycle='2026')
            trust.store(ctx,c,json.dumps(out))
        text=trust.render(ctx);self.assertIn('### ASSESSMENT\n\nUNRESOLVED',text)
        self.assertIn('Source A: Eligible; Source B: Not eligible',text)

    def test_trust_historical_agreement_does_not_resolve_current_status(self):
        ctx=context(prompt='Is the named program currently active? https://www.morgan.edu/a https://example.edu/b');trust.begin(ctx)
        for cid in ('C1','C2'):
            c,_=trust.reserve(ctx,cid)
            out=json.loads(verification('HISTORICAL',authority_host='www.morgan.edu' if cid=='C1' else 'example.edu',source_date_or_cycle='2019'))
            out.update(assertion='Program is active',population='Undergraduates',version_cycle='2019')
            trust.store(ctx,c,json.dumps(out))
        self.assertIn('### ASSESSMENT\n\nUNRESOLVED',trust.render(ctx))

    def test_exact_registered_claim_and_url_reach_each_verifier(self):
        from agents.career.workflow.shared_evidence import SharedVerification
        for policy,prompt in ((cert,'Current CompTIA price'),(interview,'Current Microsoft interview process'),(trust,'Compare named sources')):
            ctx=context(prompt=prompt);policy.begin(ctx)
            row=candidate('Exact claim with punctuation: café?',url='https://www.morgan.edu/a?q=%2F&n=1')
            policy.register(ctx,[row])
            class FakeVerifier:
                async def run_async(self,*,args,tool_context):
                    self.sent=args['request'];return verification('CURRENT STATUS UNVERIFIED')
            fake=FakeVerifier();tool=SharedVerification(policy,fake)
            asyncio.run(tool.run_async(args={'candidate_id':'C1'},tool_context=ctx))
            self.assertTrue(fake.sent.startswith('CLAIM:\n'+row['claim']+'\n\nSOURCE URL:\n'+row['source_url']+'\n'))
            stored=policy.state(ctx)[old.VERIFICATIONS]['C1']
            self.assertEqual(stored['claim'],row['claim']);self.assertEqual(stored['source_url'],row['source_url'])

    def test_trust_source_agreement_does_not_decide_personal_eligibility(self):
        ctx=context(prompt='Do I qualify? https://www.morgan.edu/a https://example.edu/b');trust.begin(ctx)
        for cid in ('C1','C2'):
            c,_=trust.reserve(ctx,cid)
            out=json.loads(verification(authority_host='www.morgan.edu' if cid=='C1' else 'example.edu'))
            out.update(assertion='Applicants meeting criteria qualify',population='Undergraduates',version_cycle='2026')
            trust.store(ctx,c,json.dumps(out))
        self.assertIn('### ASSESSMENT\n\nPARTIALLY RESOLVED',trust.render(ctx))

    def test_interview_status_category_cannot_leak_into_other_namespaces(self):
        for policy in (cert,trust):
            ctx=context(prompt='Current CompTIA or Morgan evidence');policy.begin(ctx);policy.register(ctx,[candidate()]);c,_=policy.reserve(ctx,'C1')
            self.assertEqual(policy.store(ctx,c,verification('VERIFIED OFFICIAL'))['status'],'UNSUPPORTED')

    def test_final_sections_separate_anecdotes(self):
        ctx=context(prompt='Current Microsoft process');interview.begin(ctx)
        interview.register(ctx,[dict(candidate(url='https://www.reddit.com/a'),source_type='anecdotal')]);c,_=interview.reserve(ctx,'C1')
        interview.store(ctx,c,verification('ANECDOTAL / REPORTED',authority_host='www.reddit.com'))
        text=interview.render(ctx)
        self.assertIn('Candidates have reported (not an official employer process)',text)
        self.assertIn('no official process claim was verified',text)


if __name__=='__main__':unittest.main()
