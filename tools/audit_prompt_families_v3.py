#!/usr/bin/env python3
import json,re,unicodedata
from pathlib import Path
from collections import Counter,defaultdict
ASSETS=Path('android/app/src/main/assets')
SOURCES=[('core','commands.json'),('community','prompts_library.json'),('pdf','imported_pdf_prompts.json'),('photo','curated_photo_prompts.json'),('deep_hunt','daily_gap_prompts_100.json')]
CATMAP={'Writing & Language':'Writing & Rewriting','Writing':'Writing & Rewriting','Transform':'Writing & Rewriting','Format':'Data & Formatting','Research':'Research & Analysis','Analysis':'Research & Analysis','Reasoning':'Thinking & Ideas','Decision':'Thinking & Ideas','Ideation':'Thinking & Ideas','Planning':'Planning & Execution','Study':'Learning & Study','Learning & Education':'Learning & Study','Explain':'Learning & Study','Work':'Work & Career','Career':'Work & Career','Creative & Content':'Content Creation','Content':'Content Creation','Technology & Development':'Problem Solving & Technical','Technical':'Problem Solving & Technical','Coding':'Problem Solving & Technical','Quality':'Problem Solving & Technical','Evaluation':'Problem Solving & Technical','Tools & Simulations':'Data & Formatting','Data':'Data & Formatting','Other Expert Roles':'Specialist Roles'}
def cat(c): return CATMAP.get(c,c or 'Specialist Roles')
def load():
 out=[]
 for src,fn in SOURCES:
  p=ASSETS/fn
  if not p.exists(): continue
  for x in json.load(open(p,encoding='utf-8')):
   title=x.get('command') or x.get('title') or 'Untitled'; prompt=x.get('instruction') or x.get('prompt') or ''; desc=x.get('description') or ''
   if prompt.strip(): out.append({'source':src,'title':title,'prompt':prompt,'description':desc,'category':cat(x.get('category')),'subcategory':x.get('subcategory') or ''})
 return out

def score(x):
 n=len(x['prompt'].split()); p=x['prompt'].lower(); s=min(n,160)/50
 s+=.3*sum(k in p for k in ['preserve','avoid','include','compare','identify','prioritize','explain','verify','distinguish','return','do not'])
 s+= {'deep_hunt':1.8,'core':1.4,'photo':1.1,'pdf':.6,'community':.2}.get(x['source'],0)
 return round(s,3)

def cluster_category(E,idxs,threshold):
 import numpy as np
 from sklearn.cluster import AgglomerativeClustering
 if len(idxs)==1:return [[idxs[0]]]
 X=E[idxs]
 # cosine distance; average linkage resists chaining more than single linkage
 m=AgglomerativeClustering(n_clusters=None,distance_threshold=threshold,metric='cosine',linkage='average',compute_full_tree=True)
 labels=m.fit_predict(X)
 d=defaultdict(list)
 for lab,i in zip(labels,idxs):d[int(lab)].append(i)
 return list(d.values())

def main():
 from sentence_transformers import SentenceTransformer
 items=load(); n=len(items)
 model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
 texts=[f"{x['title']}. {x['description']}. {x['prompt'][:2600]}" for x in items]
 E=model.encode(texts,batch_size=64,normalize_embeddings=True,show_progress_bar=False)
 bycat=defaultdict(list)
 for i,x in enumerate(items):bycat[x['category']].append(i)
 scenarios=[('strict',0.20),('balanced',0.28),('aggressive',0.36)]
 report={'raw_count':n,'scenarios':{},'category_counts':dict(Counter(x['category'] for x in items))}
 md=['# PromptDeck Canonical Family Analysis V3','',f'Raw prompt cards: **{n}**','']
 for name,thr in scenarios:
  clusters=[]
  for c,idxs in bycat.items():clusters.extend(cluster_category(E,idxs,thr))
  families=[g for g in clusters if len(g)>1]
  visible=len(clusters); collapsed=n-visible
  sizes=Counter(len(g) for g in clusters)
  report['scenarios'][name]={'distance_threshold':thr,'visible_family_count':visible,'cards_collapsed':collapsed,'multi_prompt_families':len(families),'largest_family':max(map(len,clusters))}
  md += [f'## {name.title()} family mode',f'- Cosine distance threshold: **{thr:.2f}**',f'- Visible canonical cards/families: **{visible}**',f'- Raw cards collapsed into families: **{collapsed}** ({collapsed/n*100:.1f}%)',f'- Multi-prompt families: **{len(families)}**',f'- Largest family: **{max(map(len,clusters))} prompts**','']
  # Keep details for balanced mode, the likely UI target.
  if name=='balanced':
   fam_sorted=sorted(families,key=lambda g:(-len(g),-max(score(items[i]) for i in g)))
   report['balanced_families']=[]
   md += ['## Largest balanced families','']
   for rank,g in enumerate(fam_sorted[:180],1):
    w=max(g,key=lambda i:score(items[i])); win=items[w]
    report['balanced_families'].append({'canonical':win|{'quality':score(win)},'size':len(g),'members':[items[i]|{'quality':score(items[i])} for i in sorted(g,key=lambda i:-score(items[i]))]})
    md += [f"### {rank}. /{win['title']} — {len(g)} variants",f"Category: {win['category']} · canonical source: {win['source']} · q={score(win)}"]
    for i in sorted(g,key=lambda i:-score(items[i]))[:20]: md.append(f"- /{items[i]['title']} — {items[i]['source']} — q={score(items[i])}")
    if len(g)>20:md.append(f'- … +{len(g)-20} more')
    md.append('')
 Path('audit').mkdir(exist_ok=True)
 Path('audit/PROMPT_FAMILY_ANALYSIS_V3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 Path('audit/PROMPT_FAMILY_ANALYSIS_V3.md').write_text('\n'.join(md),encoding='utf-8')
 print(json.dumps(report['scenarios'],indent=2))
if __name__=='__main__':main()
