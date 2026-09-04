#!/usr/bin/env python3
"""V11 full-text duplicate/capability candidate pair generator.
No external packages/network. Candidate retrieval only; never auto-deletes.
"""
import json,re,pathlib,collections,math
ROOT=pathlib.Path(__file__).resolve().parents[1]
AS=ROOT/'android/app/src/main/assets'
SOURCES=['commands.json','curated_photo_prompts.json','daily_gap_prompts_100.json','imported_pdf_prompts.json','prompts_library.json']
OUTJ=ROOT/'audit/CANDIDATE_PAIRS_V11.json'; OUTM=ROOT/'audit/CANDIDATE_PAIRS_V11.md'
STOP=set('a an the and or to of for in on with from by as is are be been being this that these those it its you your yours we our please act role expert specialist assistant professional comprehensive ultimate advanced ai chatgpt gpt prompt prompts use using'.split())

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
def grams(s,n=3):
 t=norm(s).split(); return set(tuple(t[i:i+n]) for i in range(max(0,len(t)-n+1)))
def jac(a,b): return len(a&b)/(len(a|b) or 1)
def cosine(a,b):
 # sparse token-frequency cosine
 ca=collections.Counter(norm(a).split()); cb=collections.Counter(norm(b).split())
 dot=sum(v*cb.get(k,0) for k,v in ca.items()); da=math.sqrt(sum(v*v for v in ca.values())); db=math.sqrt(sum(v*v for v in cb.values()))
 return dot/(da*db) if da and db else 0.0

def main():
 rows=[]
 for f in SOURCES:
  p=AS/f
  if not p.exists(): continue
  try: walk(json.loads(p.read_text(encoding='utf-8')),f,rows)
  except Exception: continue
 seen=set(); clean=[]
 for r in rows:
  k=(r['source'],r['title'],r['text'])
  if k in seen: continue
  seen.add(k); r['rid']=len(clean)+1; r['nt']=norm(r['title']); r['nb']=norm(r['text']); r['tg']=grams(r['title'],2); r['bg']=grams(r['text'][:5000],3); clean.append(r)
 # blocking index by meaningful title/body tokens; avoids all-pairs cost
 inv=collections.defaultdict(list)
 for r in clean:
  toks=set(r['nt'].split()) | set(r['nb'].split()[:80])
  for t in toks:
   if len(t)>=5: inv[t].append(r['rid'])
 pair_hits=collections.Counter()
 for ids in inv.values():
  if len(ids)>180: continue
  for i in range(len(ids)):
   for j in range(i+1,len(ids)):
    a,b=ids[i],ids[j]
    if a>b:a,b=b,a
    pair_hits[(a,b)]+=1
 pairs=[]
 for (a,b),shared in pair_hits.items():
  if shared<2: continue
  A=clean[a-1]; B=clean[b-1]
  title=jac(A['tg'],B['tg']); body3=jac(A['bg'],B['bg']); bodycos=cosine(A['text'][:6000],B['text'][:6000])
  exact = A['nb'] and A['nb']==B['nb']
  score=.24*title+.40*body3+.36*bodycos
  if exact: label='EXACT_DUPLICATE'; conf=1.0
  elif body3>=.72 or (score>=.78 and bodycos>=.82): label='NEAR_DUPLICATE'; conf=max(body3,score)
  elif score>=.58 or (title>=.60 and bodycos>=.52): label='SAME_CAPABILITY_VARIANT'; conf=score
  elif score>=.43 or (title>=.45 and bodycos>=.40): label='REVIEW'; conf=score
  else: continue
  pairs.append({'a':a,'b':b,'label':label,'confidence':round(conf,4),'title_similarity':round(title,4),'body_3gram':round(body3,4),'body_cosine':round(bodycos,4),'a_title':A['title'],'b_title':B['title'],'a_source':A['source'],'b_source':B['source']})
 pairs.sort(key=lambda x:({'EXACT_DUPLICATE':0,'NEAR_DUPLICATE':1,'SAME_CAPABILITY_VARIANT':2,'REVIEW':3}[x['label']],-x['confidence']))
 counts=collections.Counter(p['label'] for p in pairs)
 out={'source_records':len(clean),'candidate_pairs':len(pairs),'counts':dict(counts),'pairs':pairs,'note':'Retrieval assistance only. Human review decides merge/variant/distinct/remove; no automatic deletion.'}
 OUTJ.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Candidate Pairs V11','',f'Source records: **{len(clean)}**',f'Candidate pairs: **{len(pairs)}**','', 'No automatic deletion. Human editorial review remains authoritative.','']
 for label in ('EXACT_DUPLICATE','NEAR_DUPLICATE','SAME_CAPABILITY_VARIANT','REVIEW'):
  subset=[p for p in pairs if p['label']==label]; lines += [f'## {label} — {len(subset)}','']
  for p in subset[:250]: lines.append(f"- {p['confidence']:.3f} | RID {p['a']} `{p['a_title']}` ↔ RID {p['b']} `{p['b_title']}`")
  if len(subset)>250: lines.append(f'- … {len(subset)-250} more in JSON')
  lines.append('')
 OUTM.write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'source_records':len(clean),'candidate_pairs':len(pairs),'counts':dict(counts),'top_pairs':pairs[:20]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
