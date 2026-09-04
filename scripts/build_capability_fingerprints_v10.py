#!/usr/bin/env python3
"""V10 capability fingerprints for PromptDeck.

Purpose: build a global, category-independent candidate index using actual prompt text.
This is retrieval assistance only; human editorial review remains authoritative.
No external packages or network access required.
"""
import json,re,math,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
AS=ROOT/'android/app/src/main/assets'
SOURCES=['commands.json','curated_photo_prompts.json','daily_gap_prompts_100.json','imported_pdf_prompts.json','prompts_library.json']
OUTJ=ROOT/'audit/CAPABILITY_FINGERPRINTS_V10.json'
OUTM=ROOT/'audit/CAPABILITY_FINGERPRINTS_V10.md'
STOP=set('a an the and or to of for in on with from by as is are be been being this that these those it its you your yours we our act acting role expert specialist assistant professional comprehensive ultimate advanced ai chatgpt gpt prompt prompts please help use using make create'.split())
VERBS=['analyze','audit','brainstorm','build','check','choose','compare','convert','critique','debug','decide','design','diagnose','edit','enhance','explain','extract','find','fix','format','generate','humanize','identify','improve','investigate','optimize','plan','prioritize','proofread','recommend','refactor','research','restore','review','rewrite','summarize','teach','test','translate','troubleshoot','verify','write']
OBJECTS=['api','architecture','background','business','career','code','content','cv','database','decision','document','email','image','interview','job','lighting','market','photo','portrait','prompt','repository','research','resume','security','seo','software','strategy','system','text','travel','writing']
QUAL=['concise','deep','detailed','natural','professional','technical','cinematic','editorial','realistic','photorealistic','structured','critical','independent','step by step','evidence based']

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

def phrase_hits(s,terms): return [t for t in terms if re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',s)]
def tokens(s): return set(norm(s).split())
def signature(r):
 raw=(r['title']+' '+r['text'][:5000]).lower()
 vs=phrase_hits(raw,VERBS); os=phrase_hits(raw,OBJECTS); qs=phrase_hits(raw,QUAL)
 # title is weighted because it often encodes intended user outcome
 tt=tokens(r['title']); bt=tokens(r['text'][:2200]); all_t=tt|bt
 key=[]
 if vs: key.append(vs[0])
 if os: key.append(os[0])
 if not key:
  key=sorted(tt)[:3] or sorted(all_t)[:3]
 return {'verbs':vs[:5],'objects':os[:5],'qualifiers':qs[:5],'key':' + '.join(key),'tokens':all_t,'title_tokens':tt}

def sim(a,b):
 # Weighted lexical similarity + intent agreement. Conservative by design.
 inter=len(a['tokens']&b['tokens']); union=len(a['tokens']|b['tokens']) or 1
 jac=inter/union
 ti=len(a['title_tokens']&b['title_tokens']); tu=len(a['title_tokens']|b['title_tokens']) or 1
 tj=ti/tu
 verb=1.0 if set(a['verbs'])&set(b['verbs']) else 0.0
 obj=1.0 if set(a['objects'])&set(b['objects']) else 0.0
 return .42*jac+.28*tj+.16*verb+.14*obj

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
  seen.add(k); r['rid']=len(clean)+1; r['fp']=signature(r); clean.append(r)
 # Buckets dramatically reduce O(n^2), while allowing cross-category grouping.
 buckets=collections.defaultdict(list)
 for r in clean:
  fp=r['fp']; keys=set()
  for v in fp['verbs'][:2]: keys.add('v:'+v)
  for o in fp['objects'][:2]: keys.add('o:'+o)
  if not keys:
   for t in sorted(fp['title_tokens'])[:2]: keys.add('t:'+t)
  for k in keys: buckets[k].append(r['rid'])
 parent=list(range(len(clean)+1))
 def find(x):
  while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b: parent[b]=a
 compared=set()
 for ids in buckets.values():
  # cap pathological generic buckets by requiring title/object/verb overlap in sim
  for i in range(len(ids)):
   for j in range(i+1,len(ids)):
    a,b=ids[i],ids[j]; pair=(a,b) if a<b else (b,a)
    if pair in compared: continue
    compared.add(pair)
    A=clean[a-1]['fp']; B=clean[b-1]['fp']; s=sim(A,B)
    # Conservative threshold: candidate family, not automatic deletion.
    if s>=0.43: union(a,b)
 groups=collections.defaultdict(list)
 for r in clean: groups[find(r['rid'])].append(r)
 clusters=[]; singles=[]
 for members in groups.values():
  slim=[{'rid':r['rid'],'title':r['title'],'source':r['source'],'fingerprint':r['fp']['key']} for r in members]
  if len(members)>=2:
   # representative label from most common fingerprint key
   label=collections.Counter(r['fp']['key'] for r in members).most_common(1)[0][0]
   clusters.append({'label':label,'size':len(members),'members':slim})
  else: singles.extend(slim)
 clusters.sort(key=lambda c:(-c['size'],c['label']))
 out={'source_records':len(clean),'cluster_count':len(clusters),'clustered_records':sum(c['size'] for c in clusters),'singletons':len(singles),'clusters':clusters,'singleton_records':singles,'note':'Candidate families only. Human editorial review decides canonical/merge/variant/distinct/remove.'}
 OUTJ.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Capability Fingerprints V10','',f'Source records: **{len(clean)}**',f'Candidate clusters: **{len(clusters)}**',f'Records in clusters: **{out["clustered_records"]}**',f'Singletons: **{len(singles)}**','', '> Candidate retrieval only — similarity never authorizes deletion.','', '## Largest candidate families']
 for n,c in enumerate(clusters[:250],1):
  lines += ['',f'### {n}. {c["label"] or "unlabeled"} — {c["size"]}']
  for q in c['members'][:40]: lines.append(f"- RID {q['rid']}: {q['title']} [{q['source']}]")
  if c['size']>40: lines.append(f'- … {c["size"]-40} more in JSON')
 OUTM.write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'source_records':len(clean),'candidate_clusters':len(clusters),'clustered_records':out['clustered_records'],'singletons':len(singles),'largest_clusters':[{'label':c['label'],'size':c['size']} for c in clusters[:20]]},indent=2))
if __name__=='__main__': main()
