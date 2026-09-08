#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path('.')
ASSETS=ROOT/'android/app/src/main/assets'
JAVA=ROOT/'android/app/src/main/java/com/kareem/promptdeck/MainActivity.java'
GRADLE=ROOT/'android/app/build.gradle'
OUT=ASSETS/'final_catalog_v15.json'
PACK=ASSETS/'chatgpt_native_final.json'


def clean(x): return re.sub(r'\s+',' ',str(x or '')).strip()
def slug(title):
    s=re.sub(r'(?i)^act as (an? )?','',str(title or ''))
    s=re.sub(r'[^A-Za-z0-9]+','',s).strip() or 'ExpertPrompt'
    return s[:38]
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def map_library_category(source):
    m={
      'Writing & Language':'Writing & Rewriting','Research & Analysis':'Research & Analysis',
      'Work & Career':'Work & Career','Learning & Education':'Learning & Study',
      'Creative & Content':'Content Creation','Technology & Development':'Problem Solving & Technical',
      'Tools & Simulations':'Data & Formatting','AI & Prompting':'AI & Prompting',
      'Business & Marketing':'Business & Marketing','Health & Wellness':'Health & Wellness',
      'Lifestyle & Personal':'Lifestyle & Personal'
    }
    return m.get(source,'Specialist Roles')

def add(out,o,id_,command,category,subcategory,description,instruction,source='',source_url='',example_mode='',example_urls=None):
    try:id_=int(id_)
    except:return
    if id_<=0 or not clean(command) or not clean(instruction):return
    out[id_]={
      'id':id_,'command':str(command),'category':str(category or ''),'subcategory':str(subcategory or ''),
      'description':str(description or ''),'instruction':str(instruction or ''),'source':str(source or ''),
      'source_url':str(source_url or ''),'example_mode':str(example_mode or ''),'example_urls':list(example_urls or [])
    }

def records():
    out={}
    for o in load(ASSETS/'commands.json'):
        add(out,o,o.get('id'),o.get('command'),o.get('category',''),o.get('subcategory',''),o.get('description',o.get('description_ar','')),o.get('instruction',''),o.get('source',''),o.get('source_url',''),o.get('example_mode',''),o.get('example_urls',[]))
    for i,x in enumerate(load(ASSETS/'prompts_library.json')):
        add(out,x,30000+i,slug(x.get('title','')),map_library_category(x.get('category','')),x.get('subcategory','Specialist Roles'),x.get('description',x.get('title','')),x.get('prompt',''),x.get('source',''),x.get('source_url',''))
    for i,x in enumerate(load(ASSETS/'curated_photo_prompts.json')):
        add(out,x,x.get('id',50000+i),x.get('command',''),'Photo Editing & Image Generation',x.get('subcategory',''),x.get('description',''),x.get('instruction',''),x.get('source',''),x.get('source_url',''),x.get('example_mode',''),x.get('example_urls',[]))
    for i,x in enumerate(load(ASSETS/'imported_pdf_prompts.json')):
        add(out,x,60000+i,slug(x.get('title','')),x.get('category','Specialist Roles'),x.get('subcategory','Imported PDF Collection'),x.get('description',x.get('title','')),x.get('prompt',''),x.get('source','Imported PDF Collection'),x.get('source_url',''))
    for i,x in enumerate(load(ASSETS/'daily_gap_prompts_100.json')):
        add(out,x,x.get('id',70000+i),x.get('command',''),x.get('category',''),x.get('subcategory',''),x.get('description',''),x.get('instruction',''),x.get('source',''),x.get('source_url',''))
    return out

def anyof(h,*terms): return any(t in h for t in terms)
def taxonomy(r):
    old=(r.get('category','')+' '+r.get('subcategory','')).lower()
    meta=(r.get('command','')+' '+r.get('description','')+' '+old).lower()
    if 'images & visuals' in old or 'photo' in old or anyof(meta,'image generation','image editing','photo editing','portrait','headshot','background removal','poster image','visual preset'): cat='Images & Design'
    elif 'health & lifestyle' in old or anyof(meta,'health','medical','medicine','wellness','fitness','nutrition','diet','mental health','habit','relationship','travel','lifestyle'): cat='Health & Life'
    elif 'science & education' in old or anyof(meta,'study plan','quiz','flashcard','tutor','teaching','lesson','stem','physics','chemistry','biology','mathematics','academic learning'): cat='Learning & Education'
    elif 'technology & development' in old or anyof(meta,'coding','developer','programming','software','debug','api','database','sql','devops','cloud','cybersecurity','linux','android','ios','prompt engineering','ai prompting','agent workflow'): cat='Technology & Data'
    elif 'career & business' in old or anyof(meta,'resume','cv ','cover letter','interview','career','job search','meeting','workplace','business strategy','marketing','sales','finance','entrepreneur','customer','brand strategy'): cat='Work & Business'
    elif 'productivity & planning' in old or anyof(meta,'roadmap','project plan','action plan','checklist','workflow','timeline','priority','prioritize','decision','trade-off','tradeoff','compare options','recommend the best','organize'): cat='Planning & Decisions'
    elif 'creativity & design' in old or anyof(meta,'brainstorm','creative writing','storytelling','story ','script','social media','caption','reel','content idea','creative direction'): cat='Creativity & Content'
    elif 'writing & content' in old or anyof(meta,'rewrite','proofread','grammar','translate','email','copywriting','article','blog','tone','paraphrase','clarify writing'): cat='Writing & Communication'
    else: cat='Research & Analysis'
    h=(r.get('command','')+' '+r.get('description','')+' '+r.get('subcategory','')).lower()
    if cat=='Writing & Communication':
        sub='Translation & Language' if anyof(h,'translate','translation','language','arabic','english','localize') else 'Emails & Messages' if anyof(h,'email','reply','message','follow-up','followup','letter') else 'Copywriting' if anyof(h,'copywriting','headline','cta','landing page','ad copy','sales copy') else 'Long-form Writing' if anyof(h,'article','blog','essay','report','proposal','long form','long-form') else 'Rewrite & Polish'
    elif cat=='Research & Analysis':
        sub='Fact-checking & Sources' if anyof(h,'verify','fact check','fact-check','source','citation','evidence') else 'Summaries & Extraction' if anyof(h,'summar','extract','key points','notes') else 'Compare & Evaluate' if anyof(h,'compare','comparison','evaluate','pros cons','proscons','benchmark') else 'Deep Research' if anyof(h,'research','deep dive','investigate','web research') else 'Analysis & Insights'
    elif cat=='Planning & Decisions':
        sub='Decisions & Trade-offs' if anyof(h,'decision','tradeoff','trade-off','choose','recommend','matrix','regret') else 'Checklists & SOPs' if anyof(h,'checklist','sop','standard operating','procedure','todo','to-do') else 'Productivity & Organization' if anyof(h,'priority','prioritize','organize','productivity','time management') else 'Projects & Execution' if anyof(h,'project','execution','requirements','risk','milestone') else 'Plans & Roadmaps'
    elif cat=='Work & Business':
        sub='Career & Jobs' if anyof(h,'resume','cv','cover letter','interview','career','job','ats') else 'Meetings & Workplace' if anyof(h,'meeting','minutes','workplace','professional communication','manager','team') else 'Marketing & Sales' if anyof(h,'marketing','sales','campaign','customer','brand','seo','market') else 'Finance & Entrepreneurship' if anyof(h,'finance','financial','budget','investment','entrepreneur','startup','business model') else 'Strategy & Operations'
    elif cat=='Technology & Data':
        sub='AI & Prompting' if anyof(h,'prompt engineering','prompting','chatgpt','llm','agent','ai workflow','model') else 'Debugging & Troubleshooting' if anyof(h,'debug','bug','error','fix','troubleshoot','root cause') else 'Code Review & Testing' if anyof(h,'review code','code review','test','testing','security review','lint') else 'Data & SQL' if anyof(h,'sql','database','data analysis','dataset','csv','spreadsheet','query') else 'Systems & DevOps' if anyof(h,'devops','cloud','linux','docker','kubernetes','network','system architecture','server') else 'Coding & Implementation'
    elif cat=='Learning & Education':
        sub='Quizzes & Practice' if anyof(h,'quiz','flashcard','test me','practice questions','exam questions') else 'Study & Revision' if anyof(h,'study','revision','memorize','exam prep','learning plan') else 'Tutoring' if anyof(h,'tutor','socratic','teach me interactively','coach me') else 'Teaching & Lessons' if anyof(h,'teacher','lesson','curriculum','classroom','teaching') else 'STEM & Academic' if anyof(h,'physics','chemistry','biology','mathematics','math ','science','stem','academic') else 'Explain & Understand'
    elif cat=='Creativity & Content':
        sub='Social Media' if anyof(h,'social media','caption','reel','instagram','tiktok','linkedin post','social post') else 'Scripts & Video' if anyof(h,'script','video','youtube','podcast','scene','screenplay') else 'Storytelling & Creative Writing' if anyof(h,'story','storytelling','character','fiction','creative writing') else 'Branding & Creative Direction' if anyof(h,'brand','creative direction','campaign concept','moodboard','concept') else 'Brainstorming & Ideas'
    elif cat=='Images & Design':
        sub='Photo Editing & Restore' if anyof(h,'restore','enhance','upscale','sharpen','old photo','photo edit','image edit') else 'Background & Cleanup' if anyof(h,'background','remove object','remove person','cleanup','clean up','cutout') else 'Portraits & People' if anyof(h,'portrait','headshot','face','skin','hair','selfie','people') else 'Lighting & Color' if anyof(h,'lighting','exposure','color grade','color grading','contrast','brightness') else 'Product & Commercial' if anyof(h,'product','commercial','ecommerce','advertising','packaging') else 'Graphics & Posters' if anyof(h,'poster','thumbnail','banner','graphic','text overlay','carousel') else 'Style & Transformation' if anyof(h,'style','cinematic','film','vintage','anime','watercolor','editorial','transformation') else 'Image Generation'
    else:
        sub='Fitness & Nutrition' if anyof(h,'fitness','workout','exercise','nutrition','diet','meal') else 'Habits & Self-Improvement' if anyof(h,'habit','self improvement','self-improvement','personal growth','routine','goal') else 'Relationships & Personal' if anyof(h,'relationship','dating','family','friend','communication') else 'Travel & Lifestyle' if anyof(h,'travel','trip','itinerary','home','food','lifestyle') else 'Health & Wellness'
    r['category']=cat;r['subcategory']=sub

def clean_body(x):
    y=str(x or '').strip()
    p='For this step in a larger workflow:'
    if y.lower().startswith(p.lower()):y=y[len(p):].strip()
    suffix='Apply these instructions only to this step. Do not override or block later steps in the PromptDeck stack.'
    if y.lower().endswith(suffix.lower()):y=y[:-len(suffix)].strip()
    lines=[]
    for line in y.splitlines():
        low=line.strip().lower()
        if low.startswith(('name:','version:','author:','changelog:')):continue
        lines.append(line)
    return '\n'.join(lines).strip()

def external(r):
    branded=('midjourney','claude','anthropic','gemini','grok','deepseek','mistral','copilot','perplexity')
    head=(r.get('command','')+' '+r.get('description','')).lower()
    if any(x in head for x in branded):return True
    body=r.get('instruction','').lower()
    verbs=('use ','invoke ','run ','open ','send to ','format for ','optimized for ','prompt for ')
    for m in branded:
        for v in verbs:
            if v+m in body or v+'the '+m in body:return True
    return any(x in body for x in ('claude.md','skill.md','gemini cli','anthropic console'))

def dedup_key(x):return re.sub(r'[^a-z0-9]+',' ',str(x or '').lower()).strip()

recs=records()
pack=load(PACK)
remove=set(int(x) for x in pack.get('remove_ids',[]))
for i in list(recs):
    if i in remove:recs.pop(i,None)
for ov in pack.get('overrides',[]):
    i=int(ov.get('match_id',0))
    if i not in recs:continue
    for k in ('command','description','instruction'):
        if k in ov:recs[i][k]=ov[k]

seen=set();final=[];removed_external=[];removed_dupe=[]
for i in sorted(recs):
    r=recs[i]
    r['instruction']=clean_body(r.get('instruction',''))
    if len(r['instruction'])<8:continue
    if external(r):removed_external.append(i);continue
    k=dedup_key(r['instruction'])
    if k in seen:removed_dupe.append(i);continue
    seen.add(k);taxonomy(r)
    # Keep only runtime fields. Drop heavy provenance unless actually useful.
    obj={k:r.get(k) for k in ('id','command','category','subcategory','description','instruction')}
    if r.get('source'):obj['source']=r['source']
    if r.get('source_url'):obj['source_url']=r['source_url']
    if r.get('example_mode'):obj['example_mode']=r['example_mode']
    if r.get('example_urls'):obj['example_urls']=r['example_urls']
    final.append(obj)

OUT.write_text(json.dumps(final,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
report={'count':len(final),'removed_external_ids':removed_external,'removed_exact_duplicate_ids':removed_dupe,'bytes':OUT.stat().st_size}
(ASSETS/'final_catalog_v15_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

s=JAVA.read_text(encoding='utf-8')
def method_span(src,marker):
    st=src.find(marker)
    if st<0:raise SystemExit('missing '+marker)
    b=src.find('{',st);d=0;ins=False;esc=False;q='';i=b
    while i<len(src):
        ch=src[i]
        if ins:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:ins=False
        else:
            if ch in ('"',"'"):ins=True;q=ch
            elif ch=='{':d+=1
            elif ch=='}':
                d-=1
                if d==0:return st,i+1
        i+=1
    raise SystemExit('unclosed '+marker)
def repl(src,marker,block):
    a,b=method_span(src,marker);return src[:a]+block+src[b:]

s=repl(s,'  void load()',r'''  void load(){
    all.clear();
    try{
      JSONArray a=new JSONArray(readAsset("final_catalog_v15.json"));
      for(int i=0;i<a.length();i++)all.add(new Cmd(a.getJSONObject(i),false));
      JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));
      for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}
    }catch(Exception e){throw new RuntimeException(e);}
  }''')

JAVA.write_text(s,encoding='utf-8')
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.2-rc2'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')

assert 'readAsset("final_catalog_v15.json")' in s
assert "versionName '0.8.2-rc2'" in g
print('v15b final catalog:',json.dumps(report))
