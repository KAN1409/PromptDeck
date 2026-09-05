#!/usr/bin/env python3
"""V12 ChatGPT-first prompt quality/capability audit.
Scores every prompt using explicit editorial criteria, groups capability candidates,
and emits KEEP/REVIEW/PRUNE_CANDIDATE recommendations. Never deletes source data.
No external packages/network.
"""
import json,re,pathlib,collections,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
AS=ROOT/'android/app/src/main/assets'; AUD=ROOT/'audit'
SOURCES=['commands.json','curated_photo_prompts.json','daily_gap_prompts_100.json','imported_pdf_prompts.json','prompts_library.json']
OUTJ=AUD/'CHATGPT_QUALITY_AUDIT_V12.json'; OUTM=AUD/'CHATGPT_QUALITY_AUDIT_V12.md'
STOP=set('a an the and or to of for in on with from by as is are be been being this that these those it its you your yours we our please act role expert specialist assistant professional comprehensive ultimate advanced ai chatgpt gpt prompt prompts use using'.split())
BAD=('ignore previous instructions','jailbreak','dan mode','as an ai language model')
OTHER=('claude code','cursor','midjourney','stable diffusion','gemini api')

def walk(x,src,out):
 if isinstance(x,dict):
  lk={str(k).lower():k for k in x}
  title=next((x[lk[k]] for k in ('title','name','command','label') if k in lk and isinstance(x[lk[k]],str)),'')
  body=next((x[lk[k]] for k in ('prompt','text','content','description','template') if k in lk and isinstance(x[lk[k]],str)),'')
  if title and (body or len(title)>2): out.append({'source':src,'title':title.strip(),'text':body.strip()})
  for v in x.values(): walk(v,src,out)
 elif isinstance(x,list):
  for v in x: walk(v,src,out)

def norm(s):
 s=s.lower(); s=re.sub(r'https?://\S+',' ',s); s=re.sub(r'[^a-z0-9]+',' ',s)
 return ' '.join(w for w in s.split() if w not in STOP and len(w)>1)
def cosine(a,b):
 ca=collections.Counter(norm(a).split()); cb=collections.Counter(norm(b).split())
 dot=sum(v*cb.get(k,0) for k,v in ca.items()); da=math.sqrt(sum(v*v for v in ca.values())); db=math.sqrt(sum(v*v for v in cb.values()))
 return dot/(da*db) if da and db else 0.0

def score(r):
 t=r['text']; lo=t.lower(); n=len(t); words=t.split(); unique=len(set(w.lower() for w in words))/(len(words) or 1)
 # 0-10 rubric: ChatGPT fit, task clarity, useful constraints, output guidance, signal/noise.
 fit=2.0
 if any(x in lo for x in OTHER): fit=.5
 if any(x in lo for x in BAD): fit=.25
 clarity=2.0 if n>=120 and re.search(r'\b(write|create|analy[sz]e|explain|compare|review|design|generate|research|summari[sz]e|plan|debug|rewrite|extract|evaluate|identify)\b',lo) else (1.2 if n>=50 else .5)
 constraints=2.0 if len(re.findall(r'\b(must|should|avoid|include|exclude|preserve|do not|without|require|constraint)\b',lo))>=2 else (1.2 if n>=180 else .5)
 output=2.0 if re.search(r'\b(format|table|json|markdown|bullets?|sections?|return|output|structure|schema|steps?)\b',lo) else (1.0 if n>=150 else .4)
 signal=2.0
 if n<35: signal=.4
 elif n>9000: signal=.8
 elif unique<.30: signal=.7
 total=round(fit+clarity+constraints+output+signal,2)
 reasons=[]
 if fit<2: reasons.append('tool/model-specific or adversarial wording')
 if clarity<1.5: reasons.append('weak task clarity')
 if constraints<1.5: reasons.append('weak useful constraints')
 if output<1.5: reasons.append('weak output guidance')
 if signal<1.5: reasons.append('low signal/noise')
 return total,reasons

def main():
 rows=[]
 for f in SOURCES:
  p=AS/f
  if p.exists():
   try: walk(json.loads(p.read_text(encoding='utf-8')),f,rows)
   except Exception: pass
 seen=set(); clean=[]
 for r in rows:
  k=(r['source'],r['title'],r['text'])
  if k in seen: continue
  seen.add(k); r['rid']=len(clean)+1; r['normalized']=norm(r['text']); r['score'],r['issues']=score(r); clean.append(r)
 # Exact normalized bodies + conservative semantic candidate blocking.
 exact=collections.defaultdict(list); inv=collections.defaultdict(list)
 for r in clean:
  if r['normalized']: exact[r['normalized']].append(r['rid'])
  toks=set(norm(r['title']).split())|set(r['normalized'].split()[:60])
  for tok in toks:
   if len(tok)>=6: inv[tok].append(r['rid'])
 exact_groups=[ids for ids in exact.values() if len(ids)>1]
 pairhits=collections.Counter()
 for ids in inv.values():
  if 1<len(ids)<=120:
   for i in range(len(ids)):
    for j in range(i+1,len(ids)):
     a,b=sorted((ids[i],ids[j])); pairhits[(a,b)]+=1
 variants=[]
 for (a,b),hits in pairhits.items():
  if hits<3: continue
  A=clean[a-1]; B=clean[b-1]; sim=cosine(A['text'][:6000],B['text'][:6000])
  if sim>=.72 and A['normalized']!=B['normalized']:
   winner=a if (A['score'],len(A['text'])) >= (B['score'],len(B['text'])) else b
   variants.append({'a':a,'b':b,'cosine':round(sim,4),'recommended_winner':winner})
 variants.sort(key=lambda x:-x['cosine'])
 exact_losers=set()
 for ids in exact_groups:
  winner=max(ids,key=lambda i:(clean[i-1]['score'],len(clean[i-1]['title'])))
  exact_losers.update(i for i in ids if i!=winner)
 variant_losers=set()
 for p in variants:
  loser=p['b'] if p['recommended_winner']==p['a'] else p['a']
  if p['cosine']>=.90: variant_losers.add(loser)
 for r in clean:
  if r['rid'] in exact_losers: rec='PRUNE_CANDIDATE_EXACT'
  elif r['rid'] in variant_losers: rec='PRUNE_CANDIDATE_VARIANT'
  elif r['score']<5.0: rec='REVIEW_LOW_QUALITY'
  else: rec='KEEP'
  r['recommendation']=rec
 counts=collections.Counter(r['recommendation'] for r in clean)
 out={'rubric':'10-point ChatGPT-first: fit 2, clarity 2, useful constraints 2, output guidance 2, signal/noise 2','source_records':len(clean),'recommendations':dict(counts),'exact_duplicate_groups':len(exact_groups),'high_similarity_variant_pairs':len(variants),'records':clean,'variant_pairs':variants,'note':'Editorial audit only. No source prompt is deleted automatically.'}
 OUTJ.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 dist=collections.Counter(int(r['score']) for r in clean)
 lines=['# ChatGPT-first Quality Audit V12','',f'Prompts audited: **{len(clean)}**','', '## Rubric','',out['rubric'],'','## Recommendations','']
 for k,v in counts.most_common(): lines.append(f'- {k}: **{v}**')
 lines += ['',f'Exact duplicate groups: **{len(exact_groups)}**',f'High-similarity capability/variant pairs: **{len(variants)}**','','## Score distribution','']
 for k in sorted(dist): lines.append(f'- {k}.x: {dist[k]}')
 lines += ['','## Lowest-scoring review queue','']
 for r in sorted(clean,key=lambda x:(x['score'],x['rid']))[:150]: lines.append(f"- {r['score']:.2f} | RID {r['rid']} | `{r['title']}` | {r['source']} | {', '.join(r['issues']) or '—'}")
 lines += ['','No source prompt is deleted automatically; this report is the evidence layer for canonical editorial consolidation.']
 OUTM.write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'source_records':len(clean),'recommendations':dict(counts),'exact_duplicate_groups':len(exact_groups),'variant_pairs':len(variants),'lowest':[{'rid':r['rid'],'title':r['title'],'score':r['score']} for r in sorted(clean,key=lambda x:x['score'])[:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
