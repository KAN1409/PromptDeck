#!/usr/bin/env python3
"""V9: subdivide broad V8 intent queues into user-outcome capability candidates.
Retrieval/indexing only. Human curation remains authoritative.
"""
import json,re,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
IDX=ROOT/'audit/GLOBAL_INTENT_INDEX_V8.json'
OUTJ=ROOT/'audit/CAPABILITY_SUBFAMILIES_V9.json'
OUTM=ROOT/'audit/CAPABILITY_SUBFAMILIES_V9.md'

# Ordered, specific outcome signals. A candidate may appear in multiple subfamilies;
# this is intentional for human cross-reference.
SUB={
'plan':{
 'day_week_time':['day','daily','week','weekly','schedule','time management','routine'],
 'project_roadmap':['project','roadmap','milestone','implementation plan','execution plan'],
 'launch_gtm':['launch','go-to-market','go to market','gtm'],
 'content_plan':['content plan','content calendar','topic cluster','editorial'],
 'seo_plan':['seo','organic traffic','topical authority','local seo'],
 'study_learning':['study plan','lesson plan','learning experience','syllabus','exam'],
 'trip_event':['trip','travel','itinerary','field-trip','event plan'],
 'migration':['migration','migrate','move system'],
 'risk_scenario':['pre-mortem','premortem','scenario','worst-case','risk plan'],
 'task_breakdown':['break it into','tasks','task breakdown','action steps'],
},
'explain':{
 'simple_explanation':['eli5','simple','plain english','beginner'],
 'teach_tutor':['teach','tutor','lesson','learning'],
 'analogy_examples':['analogy','analogies','example','examples'],
 'technical_explain':['code','technical','architecture','api','database','system'],
 'concept_analysis':['concept','theory','framework','why'],
},
'decide':{
 'compare_choose':['choose','which','best option','recommend','versus','vs'],
 'prioritize':['prioritize','priority','rank','ranking'],
 'second_opinion':['second opinion','independent','challenge my'],
 'tradeoffs':['tradeoff','trade-off','pros and cons','decision matrix'],
 'risk_reality_check':['risk','reality check','red team','pre-mortem','premortem'],
},
'optimize':{
 'code_performance':['performance','latency','speed','optimize code','profil'],
 'writing_conversion':['conversion','copy','headline','cta','engagement'],
 'seo':['seo','search engine','keyword','organic'],
 'workflow_productivity':['workflow','productivity','process','efficiency'],
 'prompt':['prompt','token','llm'],
},
'research':{
 'deep_research':['deep research','comprehensive research','research report'],
 'fact_verify':['fact-check','fact check','verify','verification','evidence'],
 'literature':['literature','paper','academic','study','studies'],
 'market_competitor':['market','competitor','competitive'],
 'investigative':['investigative','investigate','non-mainstream','open source intelligence','osint'],
 'find_sources':['sources','citations','references','find information'],
},
'photo_style':{
 'cinematic':['cinematic','movie','film still'],
 'editorial':['editorial','fashion','magazine'],
 'surreal':['surreal','dream','fantasy','abstract'],
 'vintage_film':['vintage','film grain','analog','portra','kodak','retro'],
 'candid_lifestyle':['candid','lifestyle','street','selfie'],
 'dramatic':['dramatic','noir','spotlight','low key'],
 'soft_airy':['airy','soft','pastel','ethereal','bright'],
},
'debug':{
 'root_cause':['root cause','diagnose','diagnostic'],
 'bug_fix':['bug','fix','error','exception'],
 'troubleshoot':['troubleshoot','not working','failure'],
 'logs_failures':['log','logs','stack trace','test failure'],
},
'architecture':{
 'system':['system architecture','system design','distributed'],
 'frontend':['frontend','ui architecture','react','next.js'],
 'api':['api','rest','graphql'],
 'database':['database','schema','sql','data model'],
 'cache':['cache','caching'],
 'cloud_devops':['cloud','infrastructure','devops','deployment'],
},
'email':{
 'cold_outreach':['cold email','outreach','prospect'],
 'professional':['professional email','work email','business email'],
 'reply_followup':['reply','follow-up','follow up'],
 'firm_boundary':['firm','boundary','decline','say no'],
},
'rewrite':{
 'professional':['professional','polished','formal'],
 'natural_human':['human','natural','no ai','less ai'],
 'tone':['tone','warm','firm','friendly','confident'],
 'clarity':['clarity','clear','concise','flow'],
 'proofread':['proofread','grammar','spelling'],
},
'summarize':{
 'short_summary':['short','brief','concise','tldr','tl;dr'],
 'structured_notes':['notes','bullet','key points','organized'],
 'meeting_chat':['meeting','chat','conversation','thread'],
 'document':['document','pdf','article','report'],
},
'career':{
 'resume_cv':['resume','cv'],
 'cover_letter':['cover letter'],
 'interview':['interview'],
 'job_search':['job search','role','vacancy','application'],
 'recruiter_hiring':['recruiter','hiring','candidate'],
},
}

def text(q): return (q.get('title') or '').lower()
def main():
 data=json.loads(IDX.read_text(encoding='utf-8'))
 fam=data['families']; result={}; leftovers={}
 for intent,groups in SUB.items():
  rows=fam.get(intent,[]); assigned=set(); result[intent]={}
  for sub,terms in groups.items():
   hits=[]
   for q in rows:
    t=text(q)
    score=sum(1 for term in terms if term in t)
    if score:
     z=dict(q); z['sub_score']=score; hits.append(z); assigned.add(q['rid'])
   hits.sort(key=lambda x:(-x['sub_score'],-x.get('score',0),x['title'].lower()))
   result[intent][sub]=hits
  leftovers[intent]=[q for q in rows if q['rid'] not in assigned]
 out={'source_count':data['extracted_count'],'subfamilies':result,'broad_leftovers':leftovers,'note':'Retrieval assistance only; human editorial review decides survival and canonicalization.'}
 OUTJ.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Capability Subfamilies V9','',f"Source records: **{data['extracted_count']}**",'', 'Retrieval assistance only. Human editorial review remains authoritative.']
 for intent,groups in result.items():
  lines += ['',f'## {intent}']
  for sub,hits in groups.items():
   lines += ['',f'### {sub} — {len(hits)} candidates']
   for q in hits[:60]: lines.append(f"- RID {q['rid']}: {q['title']} [{q['source']}]")
   if len(hits)>60: lines.append(f'- … {len(hits)-60} more in JSON')
  lines += ['',f"### unresolved within {intent} — {len(leftovers[intent])}"]
  for q in leftovers[intent][:30]: lines.append(f"- RID {q['rid']}: {q['title']} [{q['source']}]")
 OUTM.write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'source_records':data['extracted_count'],'subfamilies':{i:{s:len(v) for s,v in g.items()} for i,g in result.items()},'leftovers':{i:len(v) for i,v in leftovers.items()}},indent=2))
if __name__=='__main__': main()
