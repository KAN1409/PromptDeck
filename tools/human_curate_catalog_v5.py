#!/usr/bin/env python3
import json,re,unicodedata
from pathlib import Path
from collections import Counter,defaultdict

ASSETS=Path('android/app/src/main/assets'); OUT=Path('audit')
SOURCES=[('core','commands.json'),('community','prompts_library.json'),('pdf','imported_pdf_prompts.json'),('photo','curated_photo_prompts.json'),('deep_hunt','daily_gap_prompts_100.json')]
CATMAP={'Writing & Language':'Writing & Rewriting','Writing':'Writing & Rewriting','Transform':'Writing & Rewriting','Format':'Data & Formatting','Research':'Research & Analysis','Analysis':'Research & Analysis','Reasoning':'Thinking & Ideas','Decision':'Thinking & Ideas','Ideation':'Thinking & Ideas','Planning':'Planning & Execution','Study':'Learning & Study','Learning & Education':'Learning & Study','Explain':'Learning & Study','Work':'Work & Career','Career':'Work & Career','Creative & Content':'Content Creation','Content':'Content Creation','Technology & Development':'Problem Solving & Technical','Technical':'Problem Solving & Technical','Coding':'Problem Solving & Technical','Quality':'Problem Solving & Technical','Evaluation':'Problem Solving & Technical','Tools & Simulations':'Data & Formatting','Data':'Data & Formatting','Other Expert Roles':'Specialist Roles'}
def cat(c): return CATMAP.get(c,c or 'Specialist Roles')
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
def load():
 out=[]; gid=1
 for src,fn in SOURCES:
  p=ASSETS/fn
  if not p.exists(): continue
  for x in json.load(open(p,encoding='utf-8')):
   title=x.get('command') or x.get('title') or 'Untitled'; prompt=x.get('instruction') or x.get('prompt') or ''; desc=x.get('description') or ''
   if prompt.strip():
    out.append({'gid':gid,'source':src,'title':title,'category':cat(x.get('category')),'subcategory':x.get('subcategory') or '', 'description':desc,'prompt':prompt}); gid+=1
 return out

# Manual policy encoded after direct catalog review. These are curation decisions, not a quality model.
OTHER_MODEL_TERMS=['claude','gemini','grok','deepseek','suno','midjourney','nano banana','copilot','cursor','windsurf','letta','antigravity','exuvia','moltpass','dspy','context7','dify']
PLATFORM_NICHE=['wordpilot','stake.us','yacon','titan omega','fractalmash','fractalmesh','enterprise wechat','dingtalk','giresun university','petr sovadina','antioch textile']
WRAPPER_MARKERS=['--- name:','permissionmode:','mcp-servers:','tools: [','agent/runsubagent','npx antigravity','git clone https://github.com/sickn33']
INCOMPLETE_MARKERS=['describe what this skill does and how the agent should use it','- step 1: ...','- step 2: ...','??????????']
PHOTO_WORDS=['portrait','photo','selfie','headshot','photograph','lighting','cinematic','editorial','isometric','clay bust','image generation','camera','lens','bokeh','film look','background replacement']
# Generic, reusable community capabilities that remain worthwhile as discoverable cards.
KEEP_CAPABILITY_TERMS=[
'accessibility','api design','api tester','app store submission','app store review','bug risk','caching','data validator','database architect','deep research','dependency manager','devops','documentation maintainer','error handler','feedback synthesizer','git workflow','intent recognition','legal document','mobile app builder','optimization auditor','performance tuning','post implementation audit','product planner','quality engineering','rapid prototyp','refactor','repository indexer','root cause','sales research','fact checking','security evaluation','code review','code reviewer','test engineer','web application testing','system architect','ui ux','ux review','software architect','solution architect','technical writer','project manager','product manager','business analyst','requirements','risk analyst','research assistant','literature review','financial analysis','financial advisor','startup co founder','unit economics','customer support','appointment setter','content strategy','seo','copywriter','marketing strategist','sales strategist','career coach','interviewer','resume','cover letter','translator','proofreader','writing tutor','teacher','tutor','study plan','quiz','travel guide','relationship coach','fitness coach','nutrition','meal plan','therapist','philosophy teacher','math teacher','language teacher','storyteller','screenwriter','novelist','debate coach','brainstorm','decision','critical thinking','data analyst','spreadsheet','sql','regex','terminal','linux terminal','javascript console','excel sheet'
]
# Roleplay/simulation modes that are genuinely distinct interaction patterns in ChatGPT.
KEEP_SIMULATION_TERMS=['linux terminal','javascript console','sql terminal','dax terminal','interviewer','debate coach','language teacher','pronunciation','socratic','quiz','storyteller','screenwriter','travel guide','relationship coach','philosophy teacher','math teacher','writing tutor','text adventure','chess coach']
# Low-value generic persona / entertainment cards: useful occasionally, but not worth catalog surface among thousands.
LOW_VALUE_PERSONA=['pirate','glados','joker','stand up comedian','rapper','motivational speaker','character','drunk woman','abandoned wife','lonely cry','girls','bikini','nsfw','futanari']

def is_englishish(s):
 letters=[c for c in s if c.isalpha()]
 if not letters:return True
 latin=sum('LATIN' in unicodedata.name(c,'') for c in letters)
 return latin/len(letters)>=0.88

def community_decision(x):
 t=norm(x['title']); p=x['prompt'].lower(); blob=(x['title']+' '+x['description']+' '+x['prompt'][:1200]).lower()
 if not is_englishish(x['title']) or not is_englishish(x['description'][:200]): return 'REMOVE','non-English catalog item'
 if any(m in p.lower() for m in INCOMPLETE_MARKERS) or len(x['prompt'].split())<12: return 'REMOVE','incomplete or too thin to be a reusable ChatGPT prompt'
 if any(k in blob for k in PLATFORM_NICHE): return 'REMOVE','one-off named project/company/person prompt'
 if any(k in blob for k in OTHER_MODEL_TERMS):
  # Image prompts mentioning an image model can survive only as a photo variant if the visual recipe is reusable.
  if any(w in blob for w in PHOTO_WORDS) and len(x['prompt'].split())>=45: return 'VARIANT','reusable visual recipe; strip model-specific wrapper'
  return 'REMOVE','built for another model/platform rather than ChatGPT'
 if any(k in p for k in WRAPPER_MARKERS):
  # Keep only if the underlying capability is unusually reusable and clear.
  if any(k in t for k in KEEP_CAPABILITY_TERMS): return 'VARIANT','useful capability trapped in external-agent wrapper; rewrite for ChatGPT'
  return 'REMOVE','external agent/skill wrapper rather than a ChatGPT prompt'
 if any(k in t for k in LOW_VALUE_PERSONA): return 'REMOVE','low-value persona/novelty card'
 # Visually-oriented community prompts belong under curated photo families rather than as standalone cards elsewhere.
 if any(w in t for w in PHOTO_WORDS) or (x['category'] not in ['Photo Editing & Image Generation'] and sum(w in blob for w in PHOTO_WORDS)>=3):
  return 'VARIANT','visual prompt; retain under Photo/Image family, not as standalone card'
 # Named one-off build requests are not reusable prompt templates unless they expose clear variables/placeholders.
 if any(ch.isdigit() for ch in x['title']) and not re.search(r'\$\{|\[.+?\]|\{.+?\}',x['prompt']):
  if not any(k in t for k in KEEP_CAPABILITY_TERMS): return 'REMOVE','over-specific one-off task'
 if any(k in t for k in KEEP_SIMULATION_TERMS): return 'KEEP','distinct interactive ChatGPT mode'
 if any(k in t for k in KEEP_CAPABILITY_TERMS): return 'KEEP','reusable high-value capability'
 # Favor prompts that are reusable templates and specify task/output rather than pure persona claims.
 has_placeholder=bool(re.search(r'\$\{|\[[^\]]+\]|\{[^\}]+\}',x['prompt']))
 task_words=sum(k in p for k in ['your task','task:','provide','create','analyze','compare','identify','rewrite','explain','generate','return','output','ask me','i will provide'])
 if has_placeholder and task_words>=2 and len(x['prompt'].split())>=45: return 'KEEP','reusable structured template'
 if task_words>=3 and len(x['prompt'].split())>=90: return 'VARIANT','potentially useful but better surfaced as a family variant'
 return 'REMOVE','not distinct/reusable enough for the curated ChatGPT catalog'

def pdf_decision(x):
 p=x['prompt'].lower(); t=norm(x['title'])
 if any(m in p for m in INCOMPLETE_MARKERS) or len(x['prompt'].split())<8: return 'REMOVE','fragment/incomplete extraction'
 # PDF collection is generally concise task+context+output prompting; retain as cards unless exact duplicate later.
 return 'KEEP','clear reusable task template'

def photo_family(x):
 b=norm(x['title']+' '+x['description']+' '+x['prompt'][:300])
 if any(k in b for k in ['restore','recovery','artifact','repair','upscale','enhance']): return 'Restore & Repair'
 if any(k in b for k in ['background','white background','gradient background']): return 'Background & Cleanup'
 if any(k in b for k in ['product','advertisement','luxury ad']): return 'Product Photography'
 if any(k in b for k in ['headshot','portrait','selfie','beauty','face']):
  if any(k in b for k in ['surreal','double exposure','fantasy','ethereal']): return 'Creative Portrait Styles'
  return 'Portraits & People'
 if any(k in b for k in ['landscape','travel','autumn','snow','city','drone']): return 'Landscape & Travel'
 if any(k in b for k in ['film','vintage','1990','retro','analog']): return 'Film & Vintage'
 if any(k in b for k in ['cinematic','movie','noir','rainy','moody']): return 'Cinematic & Moody'
 if any(k in b for k in ['surreal','abstract','fantasy','double exposure']): return 'Surreal & Artistic'
 return 'Visual Styles'

def main():
 items=load(); decisions=[]
 # First-pass decisions based on human curation policy.
 for x in items:
  if x['source'] in ['core','deep_hunt']:
   d,r='KEEP','first-party PromptDeck capability designed for current ChatGPT use'
  elif x['source']=='pdf': d,r=pdf_decision(x)
  elif x['source']=='photo': d,r='VARIANT','keep visual recipe inside a curated photo family'
  else: d,r=community_decision(x)
  decisions.append({'gid':x['gid'],'title':x['title'],'source':x['source'],'category':x['category'],'subcategory':x['subcategory'],'decision':d,'reason':r,'family':photo_family(x) if d=='VARIANT' and ('photo'==x['source'] or 'visual' in r) else None})
 # Exact prompt duplicates: keep the best source by deliberate preference; duplicates never deserve two cards.
 priority={'core':5,'deep_hunt':5,'pdf':4,'photo':3,'community':2}
 bybody=defaultdict(list)
 for i,x in enumerate(items): bybody[norm(x['prompt'])].append(i)
 dec_by_gid={d['gid']:d for d in decisions}
 for g in bybody.values():
  if len(g)<2: continue
  winner=max(g,key=lambda i:(priority[items[i]['source']],len(items[i]['prompt'])))
  for i in g:
   if i==winner: continue
   d=dec_by_gid[items[i]['gid']]; d['decision']='REMOVE'; d['reason']=f"exact duplicate; prefer /{items[winner]['title']} ({items[winner]['source']})"
 counts=Counter(d['decision'] for d in decisions); bysrc=defaultdict(Counter); bycat=defaultdict(Counter)
 for d in decisions: bysrc[d['source']][d['decision']]+=1; bycat[d['category']][d['decision']]+=1
 visible=counts['KEEP'] + len(set(d['family'] for d in decisions if d['decision']=='VARIANT' and d['family'])) + sum(1 for d in decisions if d['decision']=='VARIANT' and not d['family'])
 report={'raw_count':len(items),'decision_counts':dict(counts),'projected_visible_cards':visible,'by_source':{k:dict(v) for k,v in bysrc.items()},'by_category':{k:dict(v) for k,v in bycat.items()},'decisions':decisions}
 OUT.mkdir(exist_ok=True)
 (OUT/'HUMAN_CURATION_V5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 md=['# PromptDeck Human Curation V5','',f"Raw cards: **{len(items)}**",f"KEEP as cards: **{counts['KEEP']}**",f"KEEP as variants/family members: **{counts['VARIANT']}**",f"REMOVE: **{counts['REMOVE']}**",f"Projected visible cards (before second-pass family consolidation): **{visible}**",'', '## By source','']
 for s,c in sorted(bysrc.items()): md.append(f"- {s}: KEEP {c['KEEP']} · VARIANT {c['VARIANT']} · REMOVE {c['REMOVE']}")
 md += ['', '## By category','']
 for c,v in sorted(bycat.items()): md.append(f"- {c}: KEEP {v['KEEP']} · VARIANT {v['VARIANT']} · REMOVE {v['REMOVE']}")
 md += ['', '## Removal sample','']
 for d in [x for x in decisions if x['decision']=='REMOVE'][:120]: md.append(f"- GID {d['gid']} /{d['title']} — {d['reason']}")
 md += ['', '## Variant/family sample','']
 for d in [x for x in decisions if x['decision']=='VARIANT'][:120]: md.append(f"- GID {d['gid']} /{d['title']} — {d['family'] or 'General variant'} — {d['reason']}")
 (OUT/'HUMAN_CURATION_V5.md').write_text('\n'.join(md),encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='decisions'},indent=2))
if __name__=='__main__': main()
