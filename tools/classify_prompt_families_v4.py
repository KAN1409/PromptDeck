#!/usr/bin/env python3
import json,re
from pathlib import Path
from collections import defaultdict,Counter

ASSETS=Path('android/app/src/main/assets')
SOURCES=[('core','commands.json'),('community','prompts_library.json'),('pdf','imported_pdf_prompts.json'),('photo','curated_photo_prompts.json'),('deep_hunt','daily_gap_prompts_100.json')]
CATMAP={'Writing & Language':'Writing & Rewriting','Writing':'Writing & Rewriting','Transform':'Writing & Rewriting','Format':'Data & Formatting','Research':'Research & Analysis','Analysis':'Research & Analysis','Reasoning':'Thinking & Ideas','Decision':'Thinking & Ideas','Ideation':'Thinking & Ideas','Planning':'Planning & Execution','Study':'Learning & Study','Learning & Education':'Learning & Study','Explain':'Learning & Study','Work':'Work & Career','Career':'Work & Career','Creative & Content':'Content Creation','Content':'Content Creation','Technology & Development':'Problem Solving & Technical','Technical':'Problem Solving & Technical','Coding':'Problem Solving & Technical','Quality':'Problem Solving & Technical','Evaluation':'Problem Solving & Technical','Tools & Simulations':'Data & Formatting','Data':'Data & Formatting','Other Expert Roles':'Specialist Roles'}

def cat(c): return CATMAP.get(c,c or 'Specialist Roles')

def load():
 out=[]
 for src,fn in SOURCES:
  p=ASSETS/fn
  if not p.exists(): continue
  data=json.load(open(p,encoding='utf-8'))
  for ix,x in enumerate(data):
   title=x.get('command') or x.get('title') or 'Untitled'
   prompt=x.get('instruction') or x.get('prompt') or ''
   desc=x.get('description') or ''
   if prompt.strip():
    out.append({'id':f'{src}:{ix}','source':src,'title':title,'prompt':prompt,'description':desc,'category':cat(x.get('category')),'subcategory':x.get('subcategory') or ''})
 return out

def qscore(x):
 n=len(x['prompt'].split()); p=x['prompt'].lower(); s=min(n,180)/55
 s+=.28*sum(k in p for k in ['preserve','avoid','include','compare','identify','prioritize','explain','verify','distinguish','return','do not','ask','criteria','steps'])
 s += {'deep_hunt':1.8,'core':1.5,'photo':1.05,'pdf':.55,'community':.2}.get(x['source'],0)
 return round(s,3)

def norm_title(s):
 s=s.lower().replace('/',' ')
 s=re.sub(r'\b(imported|expert|specialist|professional|assistant|role|agent|comprehensive|ultimate|best|advanced|v\d+|\d+)\b',' ',s)
 s=re.sub(r'[^a-z0-9]+',' ',s)
 return ' '.join(s.split())

def tokens(s): return set(re.findall(r'[a-z0-9]+',norm_title(s)))

def title_jaccard(a,b):
 A,B=tokens(a),tokens(b)
 return len(A&B)/max(1,len(A|B))

PHOTO_DISTINCT={'underwater','water','floral','nature','vintage','horror','black','white','monochrome','spotlight','foggy','desolate','autumn','infrared','green','gradient','surreal','abstract','double','exposure','editorial','cinematic','noir','product','portrait','landscape','interior'}
METHOD_DISTINCT={'translate','summarize','rewrite','audit','review','compare','plan','analyze','generate','extract','verify','research','debug','test','optimize','teach','quiz','email','seo','api','security'}

def classify_family(items,idxs,E):
 import numpy as np
 sims=[]
 for ai in range(len(idxs)):
  for bi in range(ai+1,len(idxs)):
   sims.append(float(np.dot(E[idxs[ai]],E[idxs[bi]])))
 minsim=min(sims); meansim=sum(sims)/len(sims); maxsim=max(sims)
 tj=[]
 for ai in range(len(idxs)):
  for bi in range(ai+1,len(idxs)):
   tj.append(title_jaccard(items[idxs[ai]]['title'],items[idxs[bi]]['title']))
 meantj=sum(tj)/len(tj)
 cats={items[i]['category'] for i in idxs}; srcs={items[i]['source'] for i in idxs}
 title_sets=[tokens(items[i]['title']) for i in idxs]
 union=set().union(*title_sets); common=set.intersection(*title_sets) if title_sets else set()
 differentiators=union-common
 photo_diff=len(differentiators & PHOTO_DISTINCT)
 method_diff=len(differentiators & METHOD_DISTINCT)
 exact_norm=len({norm_title(items[i]['title']) for i in idxs})==1
 # Strong duplicate evidence: bodies and labels are both nearly the same, or normalized titles are identical.
 if exact_norm or (minsim>=0.91 and meantj>=0.55) or (meansim>=0.94 and meantj>=0.38):
  label='MERGE'; confidence='high'
  reason='near-identical intent/body and strongly overlapping labels'
 # Photo/style and multi-style families should normally surface as one family with variants rather than delete styles.
 elif ('Photo Editing & Image Generation' in cats and photo_diff>=1 and meansim>=0.70) or (len(idxs)>=3 and meansim>=0.74 and (photo_diff>=1 or method_diff==0)):
  label='VARIANT'; confidence='high' if meansim>=0.80 else 'medium'
  reason='shared base capability with meaningful style/context differentiators'
 # Same workflow but parameter/audience/method differences: keep under a family as variants.
 elif len(cats)==1 and meansim>=0.79 and (meantj>=0.22 or maxsim>=0.86):
  label='VARIANT'; confidence='medium'
  reason='same functional neighborhood but differences may change the output'
 else:
  label='KEEP_DISTINCT'; confidence='medium' if minsim<0.74 else 'low'
  reason='similarity is not strong enough to safely collapse capability'
 return {'decision':label,'confidence':confidence,'reason':reason,'mean_similarity':round(meansim,3),'min_similarity':round(minsim,3),'max_similarity':round(maxsim,3),'mean_title_overlap':round(meantj,3),'differentiators':sorted(differentiators)[:20]}

FACETS={
 'Photo Editing & Image Generation':{
  'primary_intent':['Fix a photo','Improve a photo','Change the look','Create something new','Explore styles'],
  'problem_or_goal':['Face & identity','Lighting','Color','Background','Quality & detail','Artifacts','Composition','Style transformation'],
  'subject':['Person','Couple','Product','Landscape','Interior','Vehicle','Object'],
  'look':['Natural','Editorial','Cinematic','Bright','Moody','Vintage','Minimal','Surreal'],
  'preservation':['Keep identity','Keep composition','Keep clothing','Keep background','Free transformation']},
 'Research & Analysis':{
  'primary_intent':['Find','Verify','Understand','Compare','Investigate','Extract'],
  'source':['Web','Social','Local','Files','Original source','Multiple sources'],
  'depth':['Quick','Thorough','Deep hunt','Latest only'],
  'evidence':['Facts','Consensus','Contradictions','Timeline','Source quality']},
 'Writing & Rewriting':{
  'primary_intent':['Write','Rewrite','Shorten','Expand','Clarify','Polish','Translate'],
  'format':['Message','Email','Document','Post','Script','Summary'],
  'tone':['Natural','Professional','Warm','Firm','Persuasive','Concise'],
  'preservation':['Keep meaning','Match my voice','Fact-preserving']},
 'Thinking & Ideas':{
  'primary_intent':['Generate ideas','Decide','Challenge','Critique','Explore alternatives','Prioritize'],
  'mode':['Divergent','Balanced','Skeptical','Second opinion','Pre-mortem'],
  'output':['Best next move','Options','Decision tree','Trade-offs','Verdict']},
 'Problem Solving & Technical':{
  'primary_intent':['Build','Fix','Debug','Review','Test','Optimize','Explain'],
  'domain':['Code','App/UI','API','Data','Security','Automation','Hardware'],
  'depth':['Quick fix','Root cause','Architecture','Production-ready'],
  'output':['Code','Plan','Checklist','Diagnosis','Review']},
 'Business & Marketing':{
  'primary_intent':['Sell','Market','Position','Plan','Analyze','Communicate'],
  'area':['Sales','Marketing','SEO','Product','Customer','Strategy'],
  'output':['Ideas','Campaign','Email','Plan','Comparison','Copy']},
 'Learning & Study':{
  'primary_intent':['Learn','Explain','Practice','Test me','Summarize','Plan study'],
  'level':['Beginner','Intermediate','Advanced','Adaptive'],
  'method':['80/20','Teach then test','Examples','Mental model','Quiz']},
 'Planning & Execution':{
  'primary_intent':['Plan','Prioritize','Schedule','Break down','Track'],
  'horizon':['Now','Today','Week','Project','Long term'],
  'output':['Next action','Checklist','Timeline','Roadmap']},
 'Work & Career':{
  'primary_intent':['Apply','Prepare','Write','Analyze','Plan','Communicate'],
  'area':['CV','Interview','Email','Performance','Career decision','Meeting'],
  'output':['Draft','Feedback','Plan','Questions','Summary']},
 'Content Creation':{
  'primary_intent':['Ideate','Create','Improve','Repurpose','Script','Package'],
  'format':['Post','Video','Article','Caption','Story','Campaign'],
  'style':['Educational','Entertaining','Persuasive','Editorial','Viral']},
 'Lifestyle & Personal':{
  'primary_intent':['Plan','Choose','Improve','Organize','Explore'],
  'area':['Travel','Daily life','Relationships','Personal growth','Shopping'],
  'output':['Ideas','Plan','Decision','Checklist']},
 'AI & Prompting':{
  'primary_intent':['Create prompt','Improve prompt','Build agent','Analyze prompt','Use AI better'],
  'mode':['Single prompt','Workflow','Agent','Meta-prompt'],
  'output':['Prompt','Framework','Instructions','Evaluation']},
 'Data & Formatting':{
  'primary_intent':['Extract','Transform','Format','Analyze','Convert'],
  'input':['Text','Table','JSON','Spreadsheet','Document'],
  'output':['Table','JSON','Structured text','Summary']},
 'Health & Wellness':{
  'primary_intent':['Understand','Prepare questions','Track','Plan','Compare'],
  'area':['Symptoms','Fitness','Nutrition','Mental wellness','Appointments'],
  'output':['Questions','Summary','Plan','Comparison']},
 'Specialist Roles':{
  'primary_intent':['Get expert perspective','Create','Analyze','Advise','Simulate'],
  'output':['Advice','Draft','Analysis','Plan','Creative output']},
 'Meta':{'primary_intent':['Discover capabilities','Choose a prompt','Improve workflow']}
}

def cluster(E,idxs,threshold=0.28):
 from sklearn.cluster import AgglomerativeClustering
 if len(idxs)==1:return [[idxs[0]]]
 m=AgglomerativeClustering(n_clusters=None,distance_threshold=threshold,metric='cosine',linkage='average',compute_full_tree=True)
 labels=m.fit_predict(E[idxs]); d=defaultdict(list)
 for lab,i in zip(labels,idxs): d[int(lab)].append(i)
 return list(d.values())

def main():
 from sentence_transformers import SentenceTransformer
 items=load(); model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
 texts=[f"{x['title']}. {x['description']}. {x['prompt'][:2800]}" for x in items]
 E=model.encode(texts,batch_size=64,normalize_embeddings=True,show_progress_bar=False)
 bycat=defaultdict(list)
 for i,x in enumerate(items):bycat[x['category']].append(i)
 fams=[]
 for c,idxs in bycat.items():
  fams.extend(g for g in cluster(E,idxs,0.28) if len(g)>1)
 decisions=[]
 for g in fams:
  cl=classify_family(items,g,E)
  winner=max(g,key=lambda i:qscore(items[i])); w=items[winner]
  decisions.append({'canonical':{k:w[k] for k in ['id','title','source','category','subcategory']}|{'quality':qscore(w)},'size':len(g),'classification':cl,'members':[{k:items[i][k] for k in ['id','title','source','category','subcategory']}|{'quality':qscore(items[i])} for i in sorted(g,key=lambda i:-qscore(items[i]))]})
 decisions.sort(key=lambda x:({'MERGE':0,'VARIANT':1,'KEEP_DISTINCT':2}[x['classification']['decision']],-x['size'],-x['canonical']['quality']))
 counts=Counter(x['classification']['decision'] for x in decisions)
 merge_removed=sum(x['size']-1 for x in decisions if x['classification']['decision']=='MERGE')
 variant_hidden=sum(x['size']-1 for x in decisions if x['classification']['decision']=='VARIANT')
 visible=len(items)-merge_removed-variant_hidden
 report={'raw_prompt_cards':len(items),'multi_prompt_candidate_families':len(decisions),'decision_counts':dict(counts),'merge_entries_removed':merge_removed,'variant_cards_collapsed_under_family':variant_hidden,'projected_visible_cards_with_merge_plus_variant_families':visible,'facets':FACETS,'families':decisions}
 Path('audit').mkdir(exist_ok=True)
 Path('audit/PROMPT_FAMILY_CLASSIFICATION_V4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 md=['# PromptDeck Family Classification V4','',f"Raw prompt cards: **{len(items)}**",f"Candidate multi-prompt families: **{len(decisions)}**",f"MERGE families: **{counts.get('MERGE',0)}**",f"VARIANT families: **{counts.get('VARIANT',0)}**",f"KEEP DISTINCT families: **{counts.get('KEEP_DISTINCT',0)}**",f"Entries removed by MERGE: **{merge_removed}**",f"Variant cards collapsed under a family card: **{variant_hidden}**",f"Projected visible cards after family UI: **{visible}**",'',"> Classification is intentionally conservative. MERGE is safe-delete territory; VARIANT means retain content under one discoverable family card; KEEP DISTINCT means do not collapse automatically.",'','## Facet architecture','']
 for c,schema in FACETS.items():
  md.append(f'### {c}')
  for k,vals in schema.items():md.append(f"- **{k.replace('_',' ').title()}**: "+' · '.join(vals))
  md.append('')
 md+=['## Highest-confidence MERGE families','']
 for x in [z for z in decisions if z['classification']['decision']=='MERGE'][:100]:
  md.append(f"### /{x['canonical']['title']} — {x['size']} → 1 ({x['classification']['confidence']})")
  md.append(f"Reason: {x['classification']['reason']} · mean sim {x['classification']['mean_similarity']} · title overlap {x['classification']['mean_title_overlap']}")
  for m in x['members']:md.append(f"- /{m['title']} — {m['source']} — q={m['quality']}")
  md.append('')
 md+=['## Largest VARIANT families','']
 for x in sorted([z for z in decisions if z['classification']['decision']=='VARIANT'],key=lambda z:-z['size'])[:100]:
  md.append(f"### /{x['canonical']['title']} — {x['size']} variants")
  md.append(f"Reason: {x['classification']['reason']} · differentiators: {', '.join(x['classification']['differentiators'][:12])}")
  for m in x['members'][:15]:md.append(f"- /{m['title']} — {m['source']}")
  md.append('')
 Path('audit/PROMPT_FAMILY_CLASSIFICATION_V4.md').write_text('\n'.join(md),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['raw_prompt_cards','multi_prompt_candidate_families','decision_counts','merge_entries_removed','variant_cards_collapsed_under_family','projected_visible_cards_with_merge_plus_variant_families']},indent=2))

if __name__=='__main__':main()
