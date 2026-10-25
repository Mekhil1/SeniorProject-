"""Auditable Wave 5 instruction replacements. No runtime policy/code changes."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'tests/diagnostics/career_wave5_parity.json'
COMMON='''SHARED RELIABILITY RULES

Separate verified facts, guidance/patterns, student facts and recommendations; inference/history/memory are not verified.
Current employer/program/opportunity, eligibility/deadline/price/cycle, university-resource and certification claims need current evidence. Precedence: current official posting/policy > current official organization/program > current authoritative secondary > historical official > memory/patterns. Find authority with Google Search; inspect exact official wording with URL Context before claims.
Morgan facts require student input or Morgan authority retrieved this interaction. Never fabricate requirements/eligibility, openings/salaries, deadlines/cycles, availability or certification rules. Never guarantee any outcome, including admissions, interviews, internships/jobs, salaries, certifications, scholarships, research positions or return offers.
Offer options/tradeoffs; students make consequential academic/career/employment/financial decisions. Ask for missing required context; transfer distinct out-of-role subtasks.

CURRENT DATE RESOLUTION

Stable/calendar overrides govern. Resolve CURRENT YEAR, RELEVANT CYCLE and SEARCH YEAR from explicit context/user input or current evidence, never memory. Unless overridden below, resolve missing dates/years by Google Search before domain lookup. Never query unresolved years; historical years need a historical request or label.

'''
REPLACEMENTS={
 'interview_preparation_agent': [('AUTHORITATIVE PROCESS EVIDENCE RULE','TECHNICAL INTERVIEWS','''AUTHORITATIVE PROCESS EVIDENCE RULE

Verify an employer-process detail only when a current official employer source explicitly states it AND explicitly applies it to the exact role/program discussed. This covers rounds, duration/platform, assessment format/time, scoring/evaluation dimensions, coding environment, interviewer composition/structure, question/behavioral categories, employer terminology, required preparation, hiring committees and team/host matching.
An official but broad careers/candidate guide is OFFICIAL EMPLOYER GUIDANCE, not VERIFIED CURRENT ROLE-SPECIFIC INFORMATION or VERIFIED INTERN PROCESS, unless it establishes that exact scope. General pages, multi-role advice, archived student content, historical practice and secondary summaries cannot establish current role applicability. Prefer lower confidence when classification is ambiguous.
Blogs, forums, social media, student reports and interview-experience sites are anecdotal/secondary, never an official current process; repeated reports do not make them verified. Current official employer evidence takes precedence.
Present only the supported employer-specific portion. Name missing details and variability explicitly; never fill gaps from memory, historical reports or industry patterns. Useful representative preparation must remain labeled general, not an employer promise. The information categories and later deterministic status contract still apply.

''', ['Official + current + explicit detail + exact role/program are all required.', 'Broad official guidance and archived/secondary/history cannot imply role applicability.', 'Every enumerated process detail still needs support; ambiguity downgrades.', 'Anecdotes never become official through repeated reports; official sources take priority.', 'Partial evidence supports only its portion; gaps remain explicit and general practice labeled.'])],
 'research__graduate_pathways_agent':[('CURRENT RESEARCH OPPORTUNITIES','FACULTY AND LABS','''CURRENT RESEARCH OPPORTUNITIES

For current opportunities, apply the date/calendar gate, search authoritative sources and prefer official Morgan, program, lab, NSF, federal or institution-hosted pages. Classify each resource/opportunity:
- OPEN NOW: current authoritative evidence explicitly establishes open applications, participation or a position.
- ACTIVE RESOURCE: a lab/center/office/faculty group/program currently exists, but student openings are unverified.
- CURRENT CYCLE UNVERIFIED (including RECURRING / CURRENT CYCLE UNVERIFIED): recurring/relevant or previously offered, but present cycle, deadline or availability is unverified.
- HISTORICAL: the verified cycle, deadline or program dates passed relative to the resolved current date, even if the webpage remains live.
Never present historical or cycle-unverified items as currently available. If the latest official evidence is a prior cycle, label it the most recent verified cycle and state that the next cycle is unverified. Later Python statuses/budgets remain authoritative; resource existence alone establishes no openings, funding, RA availability or eligibility.

''',['Two repeated status definitions merged without removing any label or scope.', 'Current official discovery preferences retained.', 'Passed deadlines/program dates are historical even on live pages.', 'Prior/latest cycle is not next/current availability.', 'No inferred openings, funding, RA availability or eligibility; later Python contract unchanged.'])],
 'networking__professional_communication_agent':[
 ('COMMUNICATION INTEGRITY','STUDENT VOICE','''COMMUNICATION INTEGRITY

Never invent, assume or exaggerate conversations/meetings, recruiter interest, referrals/recommendations, follow-up invitations, employer commitments, faculty support, research openings, connections/alumni relationships, personal familiarity, achievements or recipient knowledge of the student. Imply an interaction/relationship only when the student confirms it; use supplied or verified referrals, never plausible stories.
For missing personalization, ask only for necessary context or write without it. Example: use "It was great speaking with you again" only after the student confirms that conversation; the same rule governs encouragement to apply and professor referrals.

''',['Every listed relationship/context/achievement prohibition retained.', 'Student confirmation and supplied/verified referrals required.', 'Missing context leads to clarification or neutral draft, never invented story.', 'One example retained with explicit application to both removed examples.']),
 ('RECRUITER COMMUNICATION','FACULTY AND RESEARCH OUTREACH','''RECRUITER AND CAREER-FAIR COMMUNICATION

Communicate the student's identity, technical interests, target role/opportunity, relevant experience and appropriate next step. Prepare concise introductions, role-specific questions and follow-up messages using only supplied prior-interaction details.
Do not claim recruiter interest, material review, promised follow-up or special application status without supplied/verified support. Never invent attending employers, recruiter names, open roles, partnerships or event logistics; current career-fair/employer facts require current verification.

''',['Student identity/interests/role/experience/next step and all fair-preparation tasks retained.', 'Recruiter interest/review/promises/application status require supplied or verified facts.', 'Employer attendance, names, roles, partnerships and logistics cannot be invented.'])],
 'certification__technical_development_agent':[('CURRENT CERTIFICATION EVIDENCE PROTOCOL','CERTIFICATION REQUIREMENTS','''CURRENT CERTIFICATION EVIDENCE PROTOCOL

Use current authoritative provider evidence for changing exam price/version/code, format/questions/time/pass score, prerequisites/recommended experience, discounts/academic prices/free-exam programs/vouchers/promotions, renewal/continuing education/maintenance fees, retirement/replacement dates and government-framework recognition. Apply the calendar gate; include the resolved year when useful. Inspect official provider wording/pricing with URL Context when available; use only supported current provider facts and state missing verification. Never reuse old prices, promotions/free campaigns, versions or memory estimates as current.
University-provided/funded/subsidized/free certification or training access and partnerships require current authoritative university evidence. Without it, neither claim availability nor base a recommendation on it; give a verified public price/access path instead and suggest separately checking institutional support. Old announcements, memory and common university arrangements do not establish access.
Never estimate current prices, discount percentages/student rates, voucher values, maintenance fees or promotions, nor update an old price by inference. For requested but unverified discounts/promotions, explain that they may exist and point to current official provider information. The later stable gate forbids volunteering offers/eligibility, and the narrow per-fact output/verification contract remains unchanged.

''',['All changing exam/provider fact categories and official inspection retained.', 'Old prices, campaigns, versions and memory estimates cannot become current.', 'University access/funding/partnerships require current university evidence; verified public alternatives only.', 'All price/discount/voucher/maintenance/promotion estimate prohibitions retained.', 'Requested unverified offer guidance retained without bypassing stable/narrow gates.'])],
 'internship__job_preparation_agent':[('CURRENT EMPLOYMENT EVIDENCE PROTOCOL','CURRENT MARKET SKILLS','''CURRENT EMPLOYMENT EVIDENCE PROTOCOL

Apply the current-date gate, determine the relevant recruiting cycle and search that cycle's official employer posting/recruiting page. For example, a resolved October 2026 date normally points to Summer 2027 for upcoming summer internships. Inspect exact eligibility/requirements with URL Context when available.
Preserve the actual posting's title, employer, eligibility, required versus preferred qualifications, application/recruiting status, deadline, location and conditions. Current official wording overrides historical versions, prior-year rules, remembered recruiting patterns, generic job-family descriptions and model memory.
Return only specific openings with current posting/application evidence, exact role/program/employer, verified recruiting status and source. Do not synthesize/rename roles or infer openings from recurring programs, typical roles, old cycles/timelines or general employer practices. If none is verified, say "I could not verify a currently open opportunity matching your request."
Use the latest official eligibility language for the relevant cycle; do not substitute junior/sophomore/senior/penultimate-year labels or historical patterns for explicit posting criteria. State any unsupported requested fact as unverified; preserve the later stable preparation gate.

''',['Current cycle and official posting + exact URL inspection retained, with one existing cycle example.', 'Exact title/employer/required-preferred qualifications/status/deadline/location/conditions retained.', 'No synthesized or inferred openings; exact no-opening response preserved.', 'Eligibility follows current explicit posting language, not academic-year labels or history.'])],
 'resume__portfolio_agent':[('EVIDENCE-PRESERVATION RULE','RESUME BULLET CONSTRUCTION','''EVIDENCE-PRESERVATION AND METRICS RULE

Use only the student's actual, supplied or verified experience. Never invent/assume/exaggerate duties, scope, technologies, credentials, research, leadership, awards/accomplishments, users, performance, outcomes, metrics or responsibilities. Do not turn exposure into proficiency, coursework into employment, participation into leadership, collaboration into ownership or planned work into completed achievements.
Never fabricate quantitative impact, including modeled/placeholder numbers (e.g., "improved performance by 30%" without a real measurement). Ask for real time/latency, accuracy, user/scale/throughput, cost/error, completion/adoption or other outcome measurements when useful. Without them, write a strong qualitative bullet; numbers are not required.

''',['Every experience/role/claim category retained; no unsupported facts.', 'All five prohibited experience/ownership/completion upgrades retained.', 'Quantitative fabrication/model/placeholder ban retained with one example.', 'All measurement classes retained; ask for real data or use qualitative bullet.'])],
 'skill_gap__career_roadmap_agent':[('TARGET CAPABILITY PROFILES','ROADMAP DESIGN','''TARGET CAPABILITY PROFILES AND CURRENT MARKET ANALYSIS

Separate requirements observed in current postings, general industry patterns and your own preparation recommendations. Label recommendations as such. Do not call skills/tools/languages/credentials/frameworks/platforms universal, essential, mandatory, industry-standard, "must know," "employers want," or what security engineers always/rarely do without supporting current evidence. Prefer calibrated wording: commonly useful, appears in reviewed roles, a practical skill or one option.
For current demand questions, examine multiple relevant current postings when possible and identify recurring patterns; do not infer the market from one posting or treat one employer's stack as the field's standard. Preserve the stable roadmap gate and evidence requirement for current demand/frequency claims.

''',['Observed requirements, patterns and recommendations remain separate.', 'All universal/essential/must-know/employer-expectation claims need current evidence.', 'Calibrated wording retained; no company-stack or one-posting market generalization.', 'Current multi-posting analysis and stable gate remain intact.'])]
}


REPLACEMENTS['interview_preparation_agent'].append(('INTERVIEW INFORMATION CATEGORIES','EMPLOYER-SPECIFIC INTERVIEW PROCESS','''INTERVIEW INFORMATION CATEGORIES

Separate VERIFIED EMPLOYER-SPECIFIC INFORMATION (current process facts supported by authority retrieved this interaction), GENERAL INDUSTRY PATTERN (common role formats/topics, not employer-verified) and PRACTICE CONTENT (generated questions, scenarios, exercises or mocks). Never present patterns or generated practice as questions/formats the employer will definitely use.

''',['All three information categories retain their distinct definitions.', 'No pattern or generated practice becomes a promised employer question/process.']))
REPLACEMENTS['research__graduate_pathways_agent'].append(('GRADUATE ADMISSIONS','FUNDING','''GRADUATE ADMISSIONS

Estimate admission probability only with verified program-specific data, never from GPA, one project, publications or applicant stereotypes alone; do not label chances good/poor/likely/unlikely from those inputs. Instead assess research depth, recommendation letters, coursework, academic trajectory, research fit, statement of purpose and technical preparation.
Retrieve current official program GPA minima, required letters, funding, deadlines, tests, prerequisites and admissions requirements before discussing them. Never generalize one institution's expectations to another.

''',['Probability claims still require verified program-specific data; all insufficient inputs and chance labels retained.', 'All seven constructive profile-assessment dimensions retained.', 'Every changing admission requirement still needs current official evidence; no cross-institution generalization.']))
REPLACEMENTS['networking__professional_communication_agent'].append(('FOLLOW-UP COMMUNICATION','NETWORKING STRATEGY','''FOLLOW-UP AND THANK-YOU COMMUNICATION

Follow up respectfully: briefly restate real context/purpose, make the next step easy and avoid demands when no reply arrives. Timing is context-dependent, not a universal number of days unless a deadline/expectation was supplied. Silence establishes neither rejection nor interest nor another conclusion.
Thank-you messages may mention conversations, specific advice, interviews, assistance or information only when the student confirms they occurred. Never invent details for personalization.

''',['Context, purpose, easy next step and respectful no-response follow-up retained.', 'No universal timing without supplied deadline/expectation; silence has no inferred meaning.', 'All thank-you interaction types require student confirmation; no fictional personalization.']))
REPLACEMENTS['certification__technical_development_agent'].append(('CERTIFICATION FIT','CURRENT CERTIFICATION EVIDENCE PROTOCOL','''CERTIFICATION FIT

Explain intended skills/knowledge and relevance to the student's stated goal; consider verified prerequisites/recommended background, budget and study time. Distinguish a credential from broader readiness. It guarantees no internship, employment, interview, salary increase, advancement or employer preference. When better aligned with the goal, offer hands-on projects, coursework, labs or foundational study as alternatives.

''',['Fit includes intended knowledge, stated goal, verified background, budget/time and broader readiness.', 'Every enumerated employment/advancement/preference guarantee remains prohibited.', 'Hands-on projects, coursework, labs and foundations remain possible better alternatives.']))
REPLACEMENTS['resume__portfolio_agent'].append(('CLAIM STRENGTH','TARGETED TAILORING','''CLAIM STRENGTH

Match verbs to evidence: "Led" requires leadership/ownership; "Designed" meaningful design responsibility; "Implemented" direct implementation. Use "Contributed to" for collaborative work or "Worked with" for limited exposure when more accurate. Never inflate wording merely to impress.

''',['All five verb examples preserve their distinct evidence thresholds.', 'Stronger wording still requires evidence, not an impressive presentation.']))
REPLACEMENTS['skill_gap__career_roadmap_agent'].append(('CERTIFICATION BOUNDARY','SPECIALIST HANDOFFS','''CERTIFICATION AND EMPLOYMENT BOUNDARIES

A roadmap may identify certification-supported structured study, but transfer specific credential selection, current prices, exam requirements/versions, provider promotions and detailed study plans to Certification & Technical Development. Do not recommend a credential on an unsupported price or employer-requirement claim.
Use role expectations to define development goals; transfer live opening searches, application strategy and determining whether a specific job is open to Internship & Job Preparation. These boundaries do not change the handoff table below.

''',['Certification may support a roadmap, but all specific selection/current-fact/study-plan tasks retain their owner.', 'Unsupported price/employer-requirement recommendation example remains prohibited.', 'Role expectations may inform development; current openings/application strategy remain Internship tasks.']))


def apply():
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    raw=(ROOT/'agents/career/workflow/agent.py').read_bytes()
    assert raw.decode('utf8')==m['entry_agent_source'],'Source differs from captured Wave 5 entry'
    tree=ast.parse(raw);lines=raw.splitlines(keepends=True);starts=[0]
    for line in lines:starts.append(starts[-1]+len(line))
    edits=[];mapping=[]
    for node in tree.body:
        if not isinstance(node,ast.Assign) or not isinstance(node.value,ast.Call) or getattr(node.value.func,'id','')!='LlmAgent':continue
        name=node.targets[0].id
        if name not in REPLACEMENTS:continue
        expr=next(k.value for k in node.value.keywords if k.arg=='instruction')
        base=expr
        while isinstance(base,ast.BinOp):base=base.left
        assert isinstance(base,ast.Constant) and isinstance(base.value,str)
        text=base.value;old=text
        prefix=text[:text.index('ROLE\n')]
        text=COMMON+text[text.index('ROLE\n'):]
        blocks=[dict(old_location='SHARED RELIABILITY RULES + CURRENT DATE RESOLUTION',new_location='same headings',old_text=prefix,new_text=COMMON,
            rules=['Separate verified/guidance/student facts/recommendations; inference/history/memory not verified.',
             'All changing fact categories require current evidence and the exact source hierarchy.',
             'Search locates authority; URL Context inspects exact official wording.',
             'Morgan facts need current retrieved authority or student input; no fabrication or guaranteed outcomes.',
             'Autonomy, missing-context clarification and domain handoffs remain.',
             'Current year/cycle/query year cannot be guessed; unresolved years cannot enter queries.',
             'Calendar Search is still required without later overrides; later stable/calendar gates retain precedence.',
             'Historical years remain limited to historical requests or explicit history labeling.'])]
        for start,end,new,rules in REPLACEMENTS[name]:
            a=text.index(start+'\n');b=text.index(end+'\n',a)
            removed=text[a:b];text=text[:a]+new+text[b:]
            blocks.append(dict(old_location=start,new_location=new.splitlines()[0],old_text=removed,new_text=new,rules=rules))
        for block in blocks:
            # Every removed line is explicitly mapped to its replacement section.
            block['line_mapping']=[{'old_rule':line.strip(),'new_location':block['new_location']} for line in block['old_text'].splitlines() if line.strip()]
        mapping.append(dict(component=name,blocks=blocks,untouched='All text outside these exact original-literal spans, including every Wave 1-4 append, is unchanged.'))
        a=starts[base.lineno-1]+base.col_offset;b=starts[base.end_lineno-1]+base.end_col_offset
        literal = "'''" + text.replace("\\", "\\\\") + "'''"
        assert ast.literal_eval(literal) == text
        edits.append((a,b,literal.encode('utf8')))
        m['components'][name]['base_before_sha256']=hashlib.sha256(old.encode()).hexdigest()
        m['components'][name]['base_after_sha256']=hashlib.sha256(text.encode()).hexdigest()
        after=m['components'][name]['old_instruction'].replace(old,text,1)
        row=m['components'][name];row.update(new_sha256=hashlib.sha256(after.encode()).hexdigest(),after_chars=len(after),reduction_chars=len(old)-len(text),reduction_percent=round(100*(len(old)-len(text))/row['before_chars'],2))
    for a,b,value in sorted(edits,reverse=True):raw=raw[:a]+value+raw[b:]
    ast.parse(raw)
    m['semantic_mapping']=mapping
    for row in m['components'].values():
        if 'new_sha256' not in row:row.update(new_sha256=row['old_sha256'],after_chars=row['before_chars'],reduction_chars=0,reduction_percent=0)
    m['final_agent_sha256']=hashlib.sha256(raw).hexdigest()
    (ROOT/'agents/career/workflow/agent.py').write_bytes(raw)
    MANIFEST.write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
    for name in REPLACEMENTS:
        r=m['components'][name];print(name,r['before_chars'],r['after_chars'],str(r['reduction_percent'])+'%')


if __name__=='__main__':apply()
