#!/usr/bin/env python3
from pathlib import Path
import json,re,statistics,collections,hashlib,sys,os

ROOT=Path('.')
JAVA=ROOT/'android/app/src/main/java/com/kareem/promptdeck/MainActivity.java'
ROUTER=ROOT/'android/app/src/main/java/com/kareem/promptdeck/CapabilityRouter.java'
GRADLE=ROOT/'android/app/build.gradle'
MANIFEST=ROOT/'android/app/src/main/AndroidManifest.xml'
ASSETS=ROOT/'android/app/src/main/assets'
OUT=Path('/tmp/promptdeck-v14-comprehensive')
OUT.mkdir(parents=True,exist_ok=True)

findings=[]
def add(sev,area,title,evidence='',recommendation=''):
    findings.append(dict(severity=sev,area=area,title=title,evidence=evidence,recommendation=recommendation))

def clean(x): return re.sub(r'\s+',' ',str(x or '')).strip()
def norm(x): return clean(x).lower()
def slug(title):
    x=re.sub(r'(?i)^act as (an? )?','',title or '')
    x=re.sub(r'[^A-Za-z0-9]+','',x).strip() or 'ExpertPrompt'
    return x[:38]

def method(src,marker):
    st=src.find(marker)
    if st<0:return ''
    br=src.find('{',st); d=0; ins=False; esc=False; q=''; i=br
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
                if d==0:return src[st:i+1]
        i+=1
    return src[st:]

java=JAVA.read_text(encoding='utf-8')
router=ROUTER.read_text(encoding='utf-8') if ROUTER.exists() else ''
gradle=GRADLE.read_text(encoding='utf-8')
manifest=MANIFEST.read_text(encoding='utf-8')
pack=json.loads((ASSETS/'chatgpt_native_final.json').read_text(encoding='utf-8'))

# ---------- reconstruct source records by stable IDs ----------
records=[]
def rec(i,command,category,subcategory,description,instruction,source,source_url=''):
    try:i=int(i)
    except:return
    if i<=0:return
    records.append(dict(id=i,command=str(command or ''),category=str(category or ''),subcategory=str(subcategory or ''),description=str(description or ''),instruction=str(instruction or ''),source=source,source_url=str(source_url or '')))
for o in json.loads((ASSETS/'commands.json').read_text(encoding='utf-8')):
    rec(o.get('id'),o.get('command'),o.get('category'),o.get('subcategory'),o.get('description',o.get('description_ar','')),o.get('instruction'),'core',o.get('source_url',''))
for i,x in enumerate(json.loads((ASSETS/'prompts_library.json').read_text(encoding='utf-8'))):
    rec(30000+i,slug(str(x.get('title',''))),x.get('category'),x.get('subcategory'),x.get('description',x.get('title','')),x.get('prompt'),'community',x.get('source_url',''))
for i,x in enumerate(json.loads((ASSETS/'curated_photo_prompts.json').read_text(encoding='utf-8'))):
    rec(x.get('id',50000+i),x.get('command'),x.get('category','Photo Editing & Image Generation'),x.get('subcategory'),x.get('description'),x.get('instruction'),'photo',x.get('source_url',''))
for i,x in enumerate(json.loads((ASSETS/'imported_pdf_prompts.json').read_text(encoding='utf-8'))):
    rec(60000+i,slug(str(x.get('title',''))),x.get('category'),x.get('subcategory'),x.get('description',x.get('title','')),x.get('prompt'),'pdf',x.get('source_url',''))
for i,x in enumerate(json.loads((ASSETS/'daily_gap_prompts_100.json').read_text(encoding='utf-8'))):
    rec(x.get('id',70000+i),x.get('command'),x.get('category'),x.get('subcategory'),x.get('description'),x.get('instruction'),'daily',x.get('source_url',''))

ids=[r['id'] for r in records]
if len(ids)!=len(set(ids)): add('CRITICAL','Catalog','Duplicate source IDs',f'{len(ids)-len(set(ids))} duplicate IDs','Make IDs globally stable and unique before runtime loading.')
remove=set(int(x) for x in pack.get('remove_ids',[]))
ov={int(o['match_id']):o for o in pack.get('overrides',[]) if 'match_id' in o}
retained=[]
for r in records:
    if r['id'] in remove:continue
    x=dict(r)
    o=ov.get(r['id'])
    if o:
        for k in ('command','description','instruction'):
            if clean(o.get(k)):x[k]=o[k]
    retained.append(x)

# normalized duplicate pass like runtime final pack
seen=set(); unique=[]; duplicate_rows=[]
for r in retained:
    k=norm(r['instruction'])
    if k in seen: duplicate_rows.append(r); continue
    seen.add(k); unique.append(r)

expected=int(pack.get('expected_builtin_count',-1))
if expected!=3345:add('HIGH','Catalog','Expected catalog count differs from v14 contract',f'pack expected_builtin_count={expected}','Reconcile catalog count and release notes from one generated manifest.')
if duplicate_rows:add('MEDIUM','Catalog','Exact normalized duplicates remain before runtime dedup',f'{len(duplicate_rows)} duplicate rows are still loaded then discarded at runtime','Deduplicate at build time so the APK does not ship redundant data.')

# ---------- prompt purity / quality ----------
external_names=['midjourney','claude','anthropic','gemini','dall-e','dalle','stable diffusion','sdxl','comfyui','runway','perplexity','copilot','grok','llama','mistral','deepseek','cursor']
ext_hits=collections.defaultdict(list)
for r in retained:
    hay=(r['command']+' '+r['description']+' '+r['instruction']).lower()
    for name in external_names:
        if name in hay: ext_hits[name].append(r)

# direct target/dependency patterns are a stronger blocker than incidental mentions
external_action=re.compile(r'(?i)\b(use|invoke|call|run|open|configure|for use with|create(?: a)? .*prompt for|prompt generator for|designed for)\b.{0,100}\b(midjourney|claude(?: code)?|gemini(?: cli| gem)?|runway(?:ml)?|stable diffusion|sdxl|comfyui|copilot|grok|perplexity|deepseek|mistral|llama)\b')
external_action_rows=[r for r in retained if external_action.search(r['instruction'])]
if ext_hits['midjourney']:
    add('CRITICAL','Prompt purity','Midjourney references still exist in retained built-ins',', '.join(f"{r['id']}:{r['command']}" for r in ext_hits['midjourney'][:12]),'Remove or rewrite every retained Midjourney-branded/targeted prompt; enforce a post-build corpus scan.')
if external_action_rows:
    add('CRITICAL','Prompt purity','External-model dependent/target prompts still remain',', '.join(f"{r['id']}:{r['command']}" for r in external_action_rows[:20]),'Use semantic conversion or removal, then fail CI on external-runtime directives unless explicitly whitelisted by product policy.')

# model-branded command names are confusing even when body is generic
brand_cmd=[]
for r in retained:
    c=r['command'].lower()
    if any(n.replace(' ','').replace('-','') in c.replace('-','').replace('_','') for n in ['midjourney','claude','gemini','grok','mistral','deepseek','copilot','perplexity']):brand_cmd.append(r)
if brand_cmd:add('HIGH','Prompt purity','Model-branded prompt names remain in ChatGPT-only catalog',', '.join(f"{r['id']}:{r['command']}" for r in brand_cmd[:20]),'Rename converted capabilities to neutral ChatGPT-facing names or remove them.')

lens=[len(r['instruction']) for r in retained]
very_long=[r for r in retained if len(r['instruction'])>10000]
if very_long:add('MEDIUM','Prompt quality','Very long prompts remain',f'{len(very_long)} prompts >10k characters; max={max(lens)}','Review individually; shorten imported wrappers while preserving task-specific constraints.')
raw_json=[r for r in retained if re.match(r'^\s*[\[{]',r['instruction'])]
if raw_json:add('MEDIUM','Prompt quality','Prompts begin as raw JSON/array payloads',f'{len(raw_json)} prompts','Convert presentation/config dumps into clean natural-language prompts unless JSON is the actual required input.')
legacy=[r for r in retained if re.search(r'(?im)^\s*(---|name:|description:|version:|author:|license:|metadata:|changelog:)',r['instruction'])]
if legacy:add('HIGH','Prompt quality','Legacy skill/agent metadata still appears inside prompt bodies',', '.join(f"{r['id']}:{r['command']}" for r in legacy[:15]),'Strip imported SKILL/agent headers and keep only capability instructions.')
boiler=[r for r in retained if re.search(r'(?i)\b(here.?s a strong (copy[- ]paste )?prompt|copy[- ]paste prompt|this is a request for a system instruction|prompt name:)\b',r['instruction'])]
if boiler:add('MEDIUM','Prompt quality','Meta-prompt boilerplate remains',', '.join(f"{r['id']}:{r['command']}" for r in boiler[:15]),'Rewrite as the direct prompt itself, not commentary about a prompt.')

# template variable coverage
vars_dollar=[r for r in retained if re.search(r'\$\{[^}]{1,120}\}',r['instruction'])]
vars_bracket=[r for r in retained if re.search(r'\[[A-Za-z][A-Za-z0-9 _-]{1,40}\]',r['instruction'])]
if vars_dollar or vars_bracket:
    add('INFO','Templates','Template variables are widespread',f'${{...}} in {len(vars_dollar)} prompts; [field] style in {len(vars_bracket)} prompts','Keep resolver tests broad and distinguish variables from JSON/schema syntax.')

# prompt-only output gates
single=method(java,'String buildSinglePrompt(')
stack=method(java,'void build()')
for bad in ['USER REQUEST / CONTEXT:','TASK — ','SELECTED PROMPT MODULES:','EXECUTION RULES:','Use available ChatGPT tools only']:
    if bad in single or bad in stack:add('CRITICAL','Composer','PromptDeck wrapper text still injected',bad,'Single and stack copy/run must emit only resolved selected prompt body plus explicit user text.')
if 'resolveTemplate(c,user).trim()' not in single:add('HIGH','Composer','Single-prompt output not clearly based on resolved prompt body',single[:400],'Use one canonical compose function for Copy and Run.')
if 'p.append(resolveTemplate(selected.get(i),user).trim())' not in stack:add('HIGH','Composer','Stack composer does not concatenate resolved prompt bodies directly',stack[:500],'Use a single deterministic composer shared by copy and send.')

# ---------- feature/source tests ----------
def require(token,sev,area,title,rec=''):
    if token not in java:add(sev,area,title,f'missing token: {token}',rec)
require('ClipboardManager','HIGH','Copy','Clipboard implementation not found','Copy should use the exact same composed text as Send.')
require('ClipData','HIGH','Copy','Clipboard payload implementation not found','Copy should place plain text into primary clipboard.')
require('com.openai.chatgpt','HIGH','ChatGPT handoff','Explicit ChatGPT package handoff not found','Keep direct ChatGPT launch with chooser fallback.')
require('Intent.createChooser','MEDIUM','ChatGPT handoff','Share fallback chooser not found','Fallback gracefully when ChatGPT is not installed.')
require('favorite_prompt_ids','MEDIUM','Favorites','Favorite persistence not found','Persist favorite IDs and test after process restart.')
require('custom_commands_v1','MEDIUM','Custom prompts','Custom prompt persistence not found','Persist and validate custom prompts.')
require('openImport','MEDIUM','Import/Export','Import path not found','Keep SAF-based import and validate malformed files.')
require('openExport','MEDIUM','Import/Export','Export path not found','Export should round-trip all custom prompts safely.')
require('CapabilityRouter.route','HIGH','Ask','Capability router not used by Ask flow','Route broad/specific intent before prompt ranking.')
require('rankSmart','HIGH','Search','Ranking implementation not found','Keep ranking metadata-only and bounded.')
require('Review & Run','HIGH','Stack','Review & Run UX not present','Selected prompts should surface a contextual review/run sheet.')
require('Copy prompt','HIGH','Stack','Copy prompt action missing','Expose prompt-only copy in debug and release builds.')

# hierarchy / horizontal-list drift
browse=method(java,'void renderBrowseResultsV6(')
for t in ['vertical category list','vertical subcategory list','vertical prompt list']:
    if t not in browse:add('HIGH','Browse',f'Browse hierarchy gate missing: {t}','', 'Browse must be Category → Subcategory → Prompt as vertical lists.')
if 'HorizontalScrollView subscroll' in method(java,'void home()') or 'HorizontalScrollView subscroll' in browse:
    add('HIGH','Browse','Horizontal subcategory strip returned','HorizontalScrollView subscroll','Keep all hierarchy levels vertical as specified.')

# navigation/state
back=method(java,'onBackPressed()')
if 'discoverMode=""' not in back and 'discoverMode = ""' not in back:add('HIGH','Navigation','Back handler does not clearly reset Ask/Browse workspace state',back[:600],'Back from Ask/Browse should return landing before exiting.')
if 'onSaveInstanceState' not in java:
    add('HIGH','State','Stack/Ask state is not saved across Activity recreation','No onSaveInstanceState implementation found','Persist selected prompt IDs, current mode, current category/subcategory, query and context across rotation/process recreation.')
if 'onRestoreInstanceState' not in java and 'savedInstanceState' not in java:
    add('MEDIUM','State','No explicit state restoration path','Activity rebuilds from scratch on recreation','Restore transient workspace state, not just favorites/custom prompts.')

# incoming share declaration vs handler
if 'android.intent.action.SEND' in manifest:
    if 'getIntent()' not in java and 'getIntent(' not in java and 'onNewIntent' not in java:
        add('HIGH','Share-in','Manifest declares text/plain share target but no intent ingestion found','MainActivity exported SEND intent-filter is present','Either implement share-in to prefill Ask/context, or remove the SEND intent-filter to avoid a dead entry in Android share sheet.')

# ---------- security/privacy ----------
perms=re.findall(r'<uses-permission[^>]+android:name="([^"]+)"',manifest)
extra=[p for p in perms if p!='android.permission.INTERNET']
if extra:add('MEDIUM','Permissions','Unexpected permissions requested',', '.join(extra),'Use least privilege.')
if 'android:allowBackup="true"' in manifest:
    add('MEDIUM','Privacy','App backup is enabled while custom prompts/favorites are stored locally','android:allowBackup="true"','Decide explicitly whether prompt data should be included in device/cloud backup; consider dataExtractionRules/fullBackupContent exclusions for sensitive custom prompts.')
if 'android:exported="true"' in manifest and 'android.intent.action.SEND' in manifest:
    add('INFO','Security','MainActivity is exported as launcher/share receiver','Expected for launcher/share target','Validate all incoming intents; never trust arbitrary extras.')

# ---------- under-the-hood architecture/performance ----------
oncreate=method(java,'onCreate(')
load=method(java,'void load()')
if 'load();home();' in oncreate or 'load();' in oncreate:
    add('HIGH','Performance','Large prompt catalog is loaded synchronously during Activity startup','onCreate calls load() before rendering; prompts_library.json alone is multi-megabyte','Move parsing/index construction off the main thread and cache a compact prebuilt index/database.')
if 'new JSONArray(readAsset("prompts_library.json"))' in java:
    add('HIGH','Performance','Full multi-megabyte JSON is parsed into memory at runtime','prompts_library.json is loaded with org.json.JSONArray','Ship the final canonical catalog directly instead of rebuilding from five source collections on every launch.')
if 'decodeStream' in java and 'loadRemoteImage' in java:
    add('MEDIUM','Images','Remote example images decode at full source resolution','BitmapFactory.decodeStream without sampling/cache','Use an image loader or sampled decoding, memory/disk caching, cancellation and lifecycle awareness.')
if 'new Thread' in method(java,'void loadRemoteImage('):
    add('MEDIUM','Images','Ad-hoc unmanaged thread used for remote image loading','new Thread(...) in loadRemoteImage','Use an executor/coroutine/image loader with cancellation and bounded concurrency.')
if 'source_url' in ''.join(p.name for p in ASSETS.glob('*')):
    pass
http_urls=[]
for r in records:
    if r['source_url'].lower().startswith('http://'):http_urls.append(r['source_url'])
if http_urls:add('LOW','Networking','Plain HTTP source URLs exist',f'{len(http_urls)} http:// URLs','Prefer HTTPS; Android may block cleartext traffic depending on target/network config.')

# build/release config
m=re.search(r'versionCode\s+(\d+)',gradle);vc=int(m.group(1)) if m else -1
if vc!=37:add('HIGH','Build','Unexpected versionCode',str(vc),'Keep monotonically increasing update-safe version codes.')
if 'debuggable true' in gradle.lower():add('HIGH','Build','Gradle explicitly enables debuggable','', 'Release build must be non-debuggable.')
# Workflow currently builds assembleDebug; source cannot prove final APK signature, but record risk.
add('CRITICAL','Release','Current tested artifact is a debug APK','Workflow builds assembleDebug and prior APK badging reports application-debuggable','Produce a release-signed APK with the permanent key and verify v2 + v3 signatures and in-place update compatibility before release.')

# router coverage matrix
if router:
    domains=['IMAGE','CAREER','DECISION','CODE','RESEARCH','PLANNING','LEARNING','WRITING']
    missing=[d for d in domains if d not in router]
    if missing:add('HIGH','Ask','Router domain coverage missing',', '.join(missing),'Cover all major user intent domains.')
    # obvious synonym/domain gaps worth testing
    probes={'translate this to arabic':'WRITING','make me a workout plan':'PLANNING','analyze this spreadsheet':'GENERAL','fix my photo face':'IMAGE','help me budget money':'GENERAL','summarize this pdf':'WRITING'}
    # We cannot execute Java here; flag known uncovered high-value domains based on terms table.
    if 'finance' not in router.lower():add('MEDIUM','Ask','No dedicated finance/business intent routing','Router domains omit finance/business','Add business/finance/data domains or a better embedding/capability index before fallback.')
    if 'health' not in router.lower():add('MEDIUM','Ask','No dedicated health/life intent routing','Router domains omit health/life','Add health/life domain routing with safe prompt families.')
    if 'data' not in router.lower() and 'sql' in router.lower():add('MEDIUM','Ask','Data-analysis routing is narrow','SQL is covered under code; generic spreadsheet/data analysis is not a first-class domain','Add data/analysis capability family.')

# ---------- metrics ----------
metrics={
    'source_records':len(records),
    'retained_source_records_before_runtime_seed':len(retained),
    'unique_normalized_instructions_before_runtime_seed':len(unique),
    'pack_expected_builtin_count':expected,
    'remove_ids':len(remove),
    'external_target_ids_removed':len(pack.get('external_target_ids_removed',[])),
    'overrides':len(pack.get('overrides',[])),
    'median_instruction_chars':statistics.median(lens) if lens else 0,
    'p90_instruction_chars':sorted(lens)[int(len(lens)*.9)] if lens else 0,
    'max_instruction_chars':max(lens) if lens else 0,
    'prompts_over_10000_chars':len(very_long),
    'raw_json_prompt_bodies':len(raw_json),
    'legacy_metadata_prompt_bodies':len(legacy),
    'dollar_template_prompts':len(vars_dollar),
    'bracket_template_prompts':len(vars_bracket),
    'retained_midjourney_refs':len(ext_hits['midjourney']),
    'retained_external_action_prompts':len(external_action_rows),
    'model_branded_commands':len(brand_cmd),
}

severity_order={'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3,'INFO':4}
findings.sort(key=lambda x:(severity_order.get(x['severity'],9),x['area'],x['title']))
counts=collections.Counter(f['severity'] for f in findings)
status='FAIL' if counts['CRITICAL'] or counts['HIGH'] else ('WARN' if counts['MEDIUM'] else 'PASS')
report={'status':status,'severity_counts':dict(counts),'metrics':metrics,'findings':findings,
        'external_reference_counts':{k:len(v) for k,v in ext_hits.items() if v},
        'external_action_prompt_ids':[r['id'] for r in external_action_rows],
        'midjourney_prompt_ids':[r['id'] for r in ext_hits['midjourney']],
        'model_branded_prompt_ids':[r['id'] for r in brand_cmd]}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# PromptDeck v0.8.1 v14 — Comprehensive Static / Catalog Audit','',f'**Verdict: {status}**','',
       f"Critical: {counts['CRITICAL']} · High: {counts['HIGH']} · Medium: {counts['MEDIUM']} · Low: {counts['LOW']} · Info: {counts['INFO']}",'','## Key metrics','']
for k,v in metrics.items():lines.append(f'- **{k}**: {v}')
lines+=['','## Findings','']
for f in findings:
    lines.append(f"### [{f['severity']}] {f['area']} — {f['title']}")
    if f['evidence']:lines.append(f"Evidence: {f['evidence']}")
    if f['recommendation']:lines.append(f"Recommendation: {f['recommendation']}")
    lines.append('')
(OUT/'report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'status':status,'severity_counts':dict(counts),'metrics':metrics},indent=2))
# Never abort artifact generation: workflow decides release gate after uploading report.
