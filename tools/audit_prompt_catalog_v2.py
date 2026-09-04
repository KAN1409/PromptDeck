#!/usr/bin/env python3
import json,re,unicodedata,math
from pathlib import Path
from collections import Counter,defaultdict

ASSETS=Path('android/app/src/main/assets')
SOURCES=[('core','commands.json'),('community','prompts_library.json'),('pdf','imported_pdf_prompts.json'),('photo','curated_photo_prompts.json'),('deep_hunt','daily_gap_prompts_100.json')]
CATMAP={
'Writing & Language':'Writing & Rewriting','Writing':'Writing & Rewriting','Transform':'Writing & Rewriting','Format':'Data & Formatting',
'Research':'Research & Analysis','Analysis':'Research & Analysis','Reasoning':'Thinking & Ideas','Decision':'Thinking & Ideas','Ideation':'Thinking & Ideas',
'Planning':'Planning & Execution','Study':'Learning & Study','Learning & Education':'Learning & Study','Explain':'Learning & Study',
'Work':'Work & Career','Career':'Work & Career','Creative & Content':'Content Creation','Content':'Content Creation',
'Technology & Development':'Problem Solving & Technical','Technical':'Problem Solving & Technical','Coding':'Problem Solving & Technical','Quality':'Problem Solving & Technical','Evaluation':'Problem Solving & Technical',
'Tools & Simulations':'Data & Formatting','Data':'Data & Formatting','Other Expert Roles':'Specialist Roles'
}

def normcat(c): return CATMAP.get(c,c or 'Specialist Roles')
def norm(s):
 s=unicodedata.normalize('NFKC',s or '').lower(); s=re.sub(r'https?://\S+',' ',s); s=re.sub(r'[^\w]+',' ',s,flags=re.UNICODE); return re.sub(r'\s+',' ',s).strip()
def englishish(s):
 letters=[c for c in (s or '') if c.isalpha()]
 if not letters:return False
 latin=sum('LATIN' in unicodedata.name(c,'') for c in letters)
 return latin/len(letters)>=.82

def title_core(s):
 s=norm(s)
 drop={'act','as','a','an','the','professional','expert','assistant','specialist','generator','creator','writer','tool','prompt','for','best','ultimate','advanced','skill','imported','new'}
 toks=[t for t in s.split() if t not in drop and len(t)>1]
 return ' '.join(toks[:12])

def load_items():
 out=[]
 for source,fn in SOURCES:
  p=ASSETS/fn
  if not p.exists(): continue
  data=json.load(open(p,encoding='utf-8'))
  for i,x in enumerate(data):
   title=x.get('command') or x.get('title') or f'{source}_{i}'; prompt=x.get('instruction') or x.get('prompt') or ''; desc=x.get('description') or ''
   if not prompt.strip(): continue
   out.append({'id':len(out),'source':source,'title':title,'prompt':prompt,'description':desc,'category':normcat(x.get('category')),'subcategory':x.get('subcategory') or ''})
 return out

def qscore(x):
 p=x['prompt']; t=x['title']; n=len(p.split()); s=0
 s+=min(n,180)/55
 s+=.35*sum(k in p.lower() for k in ['preserve','avoid','include','compare','identify','prioritize','explain','return','do not','distinguish','verify','rank','if ','before ','after '])
 s+=.8 if 20<=n<=190 else 0
 s-=1.0 if n<12 else 0; s-=1.0 if n>420 else 0
 s-=1.4 if not englishish(t) else 0
 s-=1.8 if re.search(r'\?{4,}|^[^a-zA-Z]{4,}$',t or '') else 0
 s+= {'deep_hunt':1.8,'core':1.4,'photo':1.1,'pdf':.6,'community':.2}.get(x['source'],0)
 return round(s,3)

def main():
 import numpy as np
 from sentence_transformers import SentenceTransformer
 from sklearn.neighbors import NearestNeighbors
 items=load_items(); n=len(items)
 model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
 body=[f"{x['title']}. {x['description']}. {x['prompt'][:2600]}" for x in items]
 title=[f"{x['title']}. {x['description']}" for x in items]
 E=model.encode(body,batch_size=64,normalize_embeddings=True,show_progress_bar=False)
 T=model.encode(title,batch_size=128,normalize_embeddings=True,show_progress_bar=False)
 nn=NearestNeighbors(metric='cosine',algorithm='brute',n_neighbors=min(26,n)).fit(E)
 dists,inds=nn.kneighbors(E)
 parent=list(range(n))
 def find(a):
  while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
  return a
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b: parent[b]=a
 # Exact normalized duplicates always merge
 exact=defaultdict(list)
 for i,x in enumerate(items): exact[norm(x['prompt'])].append(i)
 exact_groups=[v for v in exact.values() if len(v)>1]
 for g in exact_groups:
  for j in g[1:]: union(g[0],j)
 strong=[]; review=[]
 for i in range(n):
  for d,j in zip(dists[i][1:],inds[i][1:]):
   if j<=i: continue
   bs=1-float(d); ts=float(np.dot(T[i],T[j])); a,b=items[i],items[j]
   samecat=a['category']==b['category']; ac,bc=title_core(a['title']),title_core(b['title'])
   aset,bset=set(ac.split()),set(bc.split()); jac=len(aset&bset)/max(1,len(aset|bset))
   # Strong functional duplicates: body meaning + title/use-case alignment. Cross-category requires higher certainty.
   isstrong=(samecat and ((bs>=.91 and ts>=.72) or (bs>=.865 and ts>=.84) or (bs>=.84 and jac>=.67))) or ((not samecat) and bs>=.94 and ts>=.88)
   if isstrong:
    union(i,j); strong.append((i,j,bs,ts,jac))
   elif samecat and ((bs>=.82 and ts>=.72) or (bs>=.78 and jac>=.6)):
    review.append((i,j,bs,ts,jac))
 comps=defaultdict(list)
 for i in range(n): comps[find(i)].append(i)
 fam=[g for g in comps.values() if len(g)>1]
 fam.sort(key=lambda g:(-len(g),-max(qscore(items[i]) for i in g)))
 # Quality pruning candidates independent of dedup: English-only app, gibberish, fragmentary or ultra-thin prompts.
 low=[]
 for i,x in enumerate(items):
  nwords=len(x['prompt'].split()); reasons=[]
  if not englishish(x['title']): reasons.append('non-English/non-Latin title')
  if re.search(r'\?{4,}',x['title']): reasons.append('gibberish title')
  if nwords<10: reasons.append('very short/incomplete prompt')
  if len(norm(x['title']))<3: reasons.append('non-descriptive title')
  if reasons: low.append((i,reasons))
 winners=[]
 for g in fam: winners.append((g,max(g,key=lambda i:qscore(items[i]))))
 dedup_count=n-sum(len(g)-1 for g,_ in winners)
 low_ids={i for i,_ in low}
 # Do not double-count low-quality members already removed through a family unless winner itself is low.
 low_after=sum(1 for i in low_ids if all(i not in g or i==w for g,w in winners))
 projected=max(0,dedup_count-low_after)
 out={'raw_count':n,'exact_duplicate_groups':len(exact_groups),'high_confidence_families':len(fam),'dedup_removable':n-dedup_count,'count_after_dedup':dedup_count,'quality_prune_candidates':len(low),'quality_prune_after_dedup':low_after,'projected_clean_count':projected,'source_counts':dict(Counter(x['source'] for x in items)),'category_counts':dict(Counter(x['category'] for x in items)),'families':[],'quality_candidates':[],'review_pairs':[]}
 for g,w in winners:
  out['families'].append({'canonical':items[w]|{'quality':qscore(items[w])},'members':[items[i]|{'quality':qscore(items[i])} for i in sorted(g,key=lambda i:-qscore(items[i]))],'size':len(g)})
 for i,r in low: out['quality_candidates'].append({'item':items[i]|{'quality':qscore(items[i])},'reasons':r})
 for i,j,bs,ts,jac in sorted(review,key=lambda z:-(z[2]*.65+z[3]*.35))[:500]: out['review_pairs'].append({'a':items[i],'b':items[j],'body_similarity':round(bs,3),'title_similarity':round(ts,3),'title_token_overlap':round(jac,3)})
 Path('audit').mkdir(exist_ok=True)
 Path('audit/PROMPT_CATALOG_AUDIT_V2.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 md=['# PromptDeck Semantic Catalog Audit V2','',f"- Raw entries: **{n}**",f"- High-confidence duplicate families: **{len(fam)}**",f"- Entries removable by semantic canonicalization: **{n-dedup_count}**",f"- Count after semantic dedup: **{dedup_count}**",f"- Quality/language prune candidates: **{len(low)}**",f"- Additional quality candidates after dedup: **{low_after}**",f"- Projected clean count (conservative): **{projected}**",'', '## Normalized category counts','']
 md += [f'- {k}: {v}' for k,v in Counter(x['category'] for x in items).most_common()]
 md += ['','## Largest semantic families','']
 for r,(g,w) in enumerate(winners[:150],1):
  cw=items[w]; md += [f"### {r}. /{cw['title']} — {len(g)} → 1",f"Winner: {cw['source']} · {cw['category']} · {cw['subcategory']} · q={qscore(cw)}"]
  for i in sorted(g,key=lambda i:-qscore(items[i]))[:18]:
   x=items[i]; md.append(f"- /{x['title']} — {x['source']} — q={qscore(x)}")
  md.append('')
 md += ['## Quality/language prune sample','']
 for i,r in low[:200]:
  x=items[i]; md.append(f"- /{x['title']} — {x['source']} — {', '.join(r)}")
 md += ['','## Possible overlap sample (review before merging)','']
 for p in out['review_pairs'][:200]: md.append(f"- /{p['a']['title']} ↔ /{p['b']['title']} — body {p['body_similarity']} · title {p['title_similarity']}")
 Path('audit/PROMPT_CATALOG_AUDIT_V2.md').write_text('\n'.join(md),encoding='utf-8')
 print(json.dumps({k:out[k] for k in ['raw_count','high_confidence_families','dedup_removable','count_after_dedup','quality_prune_candidates','quality_prune_after_dedup','projected_clean_count']},indent=2))

if __name__=='__main__': main()
