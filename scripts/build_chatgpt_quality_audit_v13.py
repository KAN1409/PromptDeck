#!/usr/bin/env python3
import json,re,sys,pathlib,collections
P=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'PromptDeck-ALL-prompts.json')
D=json.load(open(P,encoding='utf-8')); rows=D['commands']
ACTION=re.compile(r'\b(explain|summari[sz]e|rewrite|translate|generate|create|write|analy[sz]e|compare|review|plan|design|debug|fix|research|extract|evaluate|identify|recommend|teach|draft|classify|convert|optimi[sz]e|brainstorm|suggest|make|act as|use|give|help|turn|simplify|clarify|polish|proofread|rephrase|paraphrase|shorten|expand|rank|prioritize|test|check|diagnose|restore|enhance|edit|format)\b',re.I)
CONS=re.compile(r"\b(avoid|include|exclude|preserve|without|must|should|do not|don't|keep|focus|prioriti[sz]e|ensure|only|exactly|at least|briefly|concise|simple|specific)\b",re.I)
FMT=re.compile(r'\b(table|json|markdown|bullet|bullets|list|sections?|format|schema|steps?|outline|template|columns?|headings?|paragraphs?|return|output)\b',re.I)
PH=re.compile(r'(\[[^\]]+\]|\$\{[^}]+\}|\{[^}]+\}|<[^>]+>)')
OTHER=['claude code','cursor','midjourney','stable diffusion','gemini api','copilot workspace']
DUMP=['file:','package.json','import {','export interface','def main(','#!/usr/bin/env','npm install','pip install']
LEGACY={'Writing','Planning','Analysis','Content','Decision','Study','Research','Work','Transform','Format','Reasoning','Explain','Coding','Ideation','Career','Technical','Data','Quality','Evaluation','Meta'}
def norm(s):return re.sub(r'\s+',' ',(s or '').strip().lower())
def score(c):
 t=(c.get('instruction') or '').strip();lo=t.lower();n=len(t);a=bool(ACTION.search(t));
 task=2 if a else (1.3 if '?' in t or 'you are' in lo else (.8 if n>=80 else .3));ctx=1.5 if PH.search(t) or re.search(r'\b(user|text|topic|material|goal|input|provided|given|current|uploaded|image|photo|document|code|query|problem|task)\b',lo) or n<220 else 1.0
 k=len(CONS.findall(t));spec=1.5 if k>=2 else (1.25 if k==1 else (1.0 if a and n>=60 else .5));out=1.0 if FMT.search(t) else (.9 if n<250 and a else .6);fit=2.5;flags=[]
 if any(x in lo for x in OTHER):fit=1.0;flags.append('other_model_or_tool_specific')
 if 'current tab' in lo or 'open tabs' in lo:fit=min(fit,1.5);flags.append('environment_specific')
 sig=1.5;dp=sum(x in lo for x in DUMP)
 if n<20:sig=.5
 elif n>30000:sig=.1
 elif n>15000:sig=.3
 elif n>10000:sig=.5
 elif n>6000:sig=.9
 if dp>=3:sig=min(sig,.2);flags.append('source_or_repository_dump')
 elif dp and n>4000:sig=min(sig,.5);flags.append('source_dump_risk')
 if n>10000:flags.append('very_long')
 if not a and n<350:sig=min(sig,.7);flags.append('fragment_or_non_actionable')
 return round(task+ctx+spec+out+fit+sig,2),flags
G=collections.defaultdict(list)
for i,c in enumerate(rows):G[norm(c.get('instruction',''))].append(i)
EG=[g for g in G.values() if len(g)>1 and norm(rows[g[0]].get('instruction',''))]; losers=set()
for g in EG:
 w=max(g,key=lambda i:(score(rows[i])[0],len(rows[i].get('command',''))));losers.update(i for i in g if i!=w)
rec=[]
for i,c in enumerate(rows):
 s,f=score(c)
 if c.get('category') in LEGACY:f.append('legacy_category')
 r='PRUNE_EXACT_DUPLICATE' if i in losers else ('REVIEW' if f else 'KEEP')
 rec.append({'index':i+1,'id':c.get('id'),'command':c.get('command'),'category':c.get('category'),'score':s,'flags':f,'recommendation':r,'length':len(c.get('instruction',''))})
counts=collections.Counter(x['recommendation'] for x in rec);flags=collections.Counter(y for x in rec for y in x['flags'])
out={'source_records':len(rows),'recommendations':dict(counts),'flags':dict(flags),'exact_duplicate_groups':len(EG),'records':rec,'note':'Uses the in-app Export All file as source of truth; brevity is not a quality penalty.'}
pathlib.Path('audit/CHATGPT_QUALITY_AUDIT_V13.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:out[k] for k in ('source_records','recommendations','flags','exact_duplicate_groups')},ensure_ascii=False,indent=2))
