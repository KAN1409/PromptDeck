#!/usr/bin/env python3
import json,re,collections,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
AS=ROOT/'android/app/src/main/assets'
SOURCES=['commands.json','curated_photo_prompts.json','daily_gap_prompts_100.json','imported_pdf_prompts.json','prompts_library.json']
STOP=set('a an the and or to of for in on with from by as is are be act expert specialist assistant professional comprehensive ultimate advanced ai chatgpt gpt prompt'.split())
INTENTS={
'rewrite':['rewrite','rephrase','polish','improve writing','humanize','proofread','edit text'],
'summarize':['summarize','summary','distill','recap','condense'],
'research':['research','deep research','investigate','find sources','literature','evidence'],
'compare':['compare','comparison','versus','pros and cons','tradeoff'],
'decide':['decision','choose','recommend','prioritize','best option','verdict'],
'explain':['explain','teach','understand','eli5','tutor'],
'extract':['extract','parse','identify from','pull out'],
'brainstorm':['brainstorm','ideas','ideate','generate ideas'],
'plan':['plan','planner','roadmap','strategy','schedule','itinerary'],
'email':['email','cold email','outreach','reply'],
'career':['resume','cv','cover letter','interview','recruiter'],
'code_review':['code review','review code','pull request review'],
'debug':['debug','bug','root cause','troubleshoot','error'],
'refactor':['refactor','clean code','technical debt'],
'test':['test cases','testing','qa','quality assurance','regression'],
'security':['security audit','vulnerability','threat model','secure code'],
'architecture':['architecture','system design','database design','api design'],
'optimize':['optimize','performance','tuning','speed up'],
'photo_restore':['restore','restoration','recover detail','old photo'],
'photo_enhance':['enhance photo','enhance image','retouch','skin texture','face recovery'],
'photo_style':['cinematic','editorial','surreal','vintage','film look','portrait style'],
'background':['background replacement','replace background','remove background','background blur'],
'image_analyze':['analyze image','analyze photo','photo critic','why looks ai'],
'buy':['buy','purchase','worth it','upgrade','value for money'],
}
def walk(x,src,out):
 if isinstance(x,dict):
  # candidate prompt-like dictionaries
  keys={str(k).lower():k for k in x}
  title=next((x[keys[k]] for k in ['title','name','command','label'] if k in keys and isinstance(x[keys[k]],str)),'')
  body=next((x[keys[k]] for k in ['prompt','text','content','description','template'] if k in keys and isinstance(x[keys[k]],str)),'')
  if title and (body or len(title)>2): out.append({'source':src,'title':title,'text':body})
  for v in x.values(): walk(v,src,out)
 elif isinstance(x,list):
  for v in x: walk(v,src,out)
def norm(s):
 s=s.lower(); s=re.sub(r'https?://\S+',' ',s); s=re.sub(r'[^a-z0-9]+',' ',s)
 return ' '.join(w for w in s.split() if w not in STOP)
def main():
 rows=[]
 for f in SOURCES:
  p=AS/f
  if not p.exists(): continue
  try: data=json.loads(p.read_text(encoding='utf-8'))
  except Exception: continue
  walk(data,f,rows)
 # de-dupe extraction artifacts by source/title/text
 seen=set(); clean=[]
 for i,r in enumerate(rows):
  k=(r['source'],r['title'].strip(),r['text'].strip())
  if k in seen: continue
  seen.add(k); r['rid']=len(clean)+1; clean.append(r)
 families=collections.defaultdict(list); unmatched=[]
 for r in clean:
  hay=norm(r['title']+' '+r['text'][:1800]); scores=[]
  for intent,terms in INTENTS.items():
   score=sum(3 if ' ' in t and t in hay else 1 for t in terms if t in hay)
   if score: scores.append((score,intent))
  scores.sort(reverse=True)
  if scores:
   best=scores[0][0]
   for sc,intent in scores[:3]:
    if sc>=max(1,best-1): families[intent].append({'rid':r['rid'],'title':r['title'],'source':r['source'],'score':sc})
  else: unmatched.append({'rid':r['rid'],'title':r['title'],'source':r['source']})
 out={'extracted_count':len(clean),'families':dict(sorted(families.items(),key=lambda kv:-len(kv[1]))),'unmatched':unmatched}
 (ROOT/'audit/GLOBAL_INTENT_INDEX_V8.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# Global Intent Index V8','',f'Extracted candidate records: **{len(clean)}**','', 'This index is retrieval assistance only. Human editorial review decides canonical/merge/variant/distinct/remove.','', '## Family queue']
 for k,v in sorted(families.items(),key=lambda kv:-len(kv[1])):
  lines += ['',f'### {k} — {len(v)} candidates']+[f"- RID {q['rid']}: {q['title']} [{q['source']}]" for q in v[:80]]
  if len(v)>80: lines.append(f'- … {len(v)-80} more in JSON')
 lines += ['',f'## Unmatched — {len(unmatched)} candidates','', 'These require later capability discovery rather than forced assignment.']
 (ROOT/'audit/GLOBAL_INTENT_INDEX_V8.md').write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'records':len(clean),'families':{k:len(v) for k,v in families.items()},'unmatched':len(unmatched)},indent=2))
if __name__=='__main__': main()
