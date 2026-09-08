#!/usr/bin/env python3
import json,re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path

PKG='com.kareem.promptdeck'
ACT=PKG+'/.MainActivity'
APK='android/app/build/outputs/apk/debug/app-debug.apk'
OUT=Path('/tmp/promptdeck-frozen-acceptance');OUT.mkdir(parents=True,exist_ok=True)
SC=OUT/'screens';SC.mkdir(exist_ok=True)
R=[]

def adb(*a,check=True,timeout=90):
    p=subprocess.run(['adb',*a],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    if check and p.returncode: raise RuntimeError(p.stdout)
    return p.stdout.strip()

def dump():
    adb('shell','uiautomator','dump','/sdcard/w.xml',check=False,timeout=20)
    adb('pull','/sdcard/w.xml','/tmp/w.xml',check=False,timeout=20)
    return ET.parse('/tmp/w.xml').getroot()

def nodes(): return list(dump().iter('node'))
def txts(): return [n.attrib.get('text','') for n in nodes() if n.attrib.get('text')]
def find(s,exact=False):
    q=s.lower()
    for n in nodes():
        t=n.attrib.get('text','')
        if (t.lower()==q if exact else q in t.lower()): return n
    return None
def has(s): return find(s) is not None

def center(n):
    m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
    if not m: raise AssertionError('node has no bounds')
    a,b,c,d=map(int,m.groups()); return (a+c)//2,(b+d)//2

def tap(s):
    n=find(s)
    if n is None: raise AssertionError('missing '+s+' visible='+repr(txts()[:100]))
    x,y=center(n); adb('shell','input','tap',str(x),str(y)); time.sleep(.45)

def tap_clickable(s,exact=False):
    root=dump();q=s.lower();target=None
    for n in root.iter('node'):
        t=n.attrib.get('text','')
        if (t.lower()==q if exact else q in t.lower()): target=n;break
    if target is None: raise AssertionError('missing '+s+' visible='+repr([n.attrib.get('text','') for n in root.iter('node') if n.attrib.get('text')][:100]))
    parents={c:p for p in root.iter() for c in p}
    n=target
    while n is not None and n.attrib.get('clickable')!='true': n=parents.get(n)
    if n is None: n=target
    x,y=center(n);adb('shell','input','tap',str(x),str(y));time.sleep(.55)

def edit(value):
    n=next((n for n in nodes() if n.attrib.get('class','').endswith('EditText')),None)
    if n is None: raise AssertionError('no edit field visible='+repr(txts()[:100]))
    x,y=center(n);adb('shell','input','tap',str(x),str(y))
    adb('shell','input','keyevent','KEYCODE_CTRL_A',check=False);adb('shell','input','keyevent','KEYCODE_DEL',check=False)
    adb('shell','input','text',value.replace(' ','%s'));time.sleep(.25)

def edit_slow(value):
    n=next((n for n in nodes() if n.attrib.get('class','').endswith('EditText')),None)
    if n is None: raise AssertionError('no edit field visible='+repr(txts()[:100]))
    x,y=center(n);adb('shell','input','tap',str(x),str(y));time.sleep(.2)
    adb('shell','input','keyevent','KEYCODE_CTRL_A',check=False);adb('shell','input','keyevent','KEYCODE_DEL',check=False);time.sleep(.2)
    for ch in value:
        token='%s' if ch==' ' else ch
        adb('shell','input','text',token,check=False);time.sleep(.32)
    time.sleep(.5)

def shot(name):
    p=SC/(name+'.png');
    with open(p,'wb') as f: subprocess.run(['adb','exec-out','screencap','-p'],stdout=f)
    return str(p)

def external_system_anr():
    try:text=' | '.join(txts()).lower()
    except Exception:return None
    if "isn't responding" not in text:return None
    if 'promptdeck' in text:return 'APP'
    return text[:500]

def wait_ui(timeout=12):
    end=time.time()+timeout
    while time.time()<end:
        infra=external_system_anr()
        if infra and infra!='APP':
            n=find('Wait',exact=True)
            if n:
                x,y=center(n);adb('shell','input','tap',str(x),str(y),check=False);time.sleep(1);continue
        if infra=='APP': raise AssertionError('PromptDeck ANR dialog visible')
        try:
            if has('Ask PromptDeck') and (has('Browse all prompts') or has('Browse prompts')):return
        except Exception: pass
        time.sleep(.3)
    raise AssertionError('workspace did not become ready; visible='+repr(txts()[:100]))

def launch(clear=False):
    if clear: adb('shell','pm','clear',PKG,check=False)
    adb('shell','am','force-stop',PKG,check=False)
    adb('shell','am','start','-W','-n',ACT,check=False,timeout=30)
    wait_ui()

def landing_ready(): return has('How do you want to start?') and (has('Browse all prompts') or has('Browse prompts'))
def home():
    launch(False)
    for _ in range(5):
        if landing_ready():return
        adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.35)
    if not landing_ready():raise AssertionError('could not normalize landing; visible='+repr(txts()[:100]))

def run(name,fn):
    try:
        fn();R.append({'name':name,'status':'PASS','screenshot':shot(name+'_PASS')});print('PASS',name)
    except Exception as e:
        R.append({'name':name,'status':'FAIL','detail':str(e)[:1500],'screenshot':shot(name+'_FAIL')});print('FAIL',name,e)

def t01():
    out=adb('install','-r',APK,check=False,timeout=180)
    if 'Success' not in out:raise AssertionError(out)
    launch(True)
    visible=' | '.join(txts())
    if '3,304-prompt library' not in visible:raise AssertionError('built-in catalog count missing: '+visible[:1200])
    anr=adb('shell','dumpsys','activity','lastanr',check=False).lower()
    if PKG in anr and ('anr' in anr or 'not responding' in anr):raise AssertionError('PromptDeck startup ANR recorded')

def t02():
    home();tap('Ask PromptDeck')
    if not has('Find the best approach'):raise AssertionError('Ask UI missing')
    adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(.4)
    if not landing_ready():raise AssertionError('Back did not return landing')

def t03():
    home();tap('Ask PromptDeck');edit('photo edit');tap('Find the best approach');time.sleep(.7)
    req=['Enhance & restore','Retouch portrait','Background','Light & color']
    miss=[x for x in req if not has(x)]
    if miss:raise AssertionError('missing capabilities '+repr(miss)+' visible='+repr(txts()[:120]))

def t04():
    home();tap('Browse all prompts');time.sleep(.5)
    if not has('Browse by category'):raise AssertionError('category browse missing')
    tap('Writing & Communication');time.sleep(.4)
    if not has('Choose what you want to do'):raise AssertionError('subcategory level missing')
    if not has('Rewrite & Polish'):raise AssertionError('writing subcategory missing')

def t05():
    home();tap('Browse all prompts');edit('midjourney');time.sleep(.6)
    bad=[t for t in txts() if 'midjourney' in t.lower() and t.lower().strip()!='midjourney']
    if bad:raise AssertionError('Midjourney result visible '+repr(bad[:8]))

def t06():
    adb('shell','am','force-stop',PKG,check=False)
    adb('shell','am','start','-W','-n',ACT,'-a','android.intent.action.SEND','-t','text/plain','--es','android.intent.extra.TEXT','cold_share_probe',check=False)
    wait_ui();time.sleep(.3)
    if 'cold_share_probe' not in ' | '.join(txts()).lower():raise AssertionError('cold share not consumed')
    adb('shell','am','start','-W','-n',ACT,'-a','android.intent.action.SEND','-t','text/plain','--es','android.intent.extra.TEXT','warm_share_probe',check=False)
    wait_ui();time.sleep(.3)
    if 'warm_share_probe' not in ' | '.join(txts()).lower():raise AssertionError('warm share not consumed')

def t07():
    home();tap('Ask PromptDeck');edit('study');time.sleep(.2)
    adb('shell','settings','put','system','accelerometer_rotation','0',check=False)
    adb('shell','settings','put','system','user_rotation','1',check=False);time.sleep(.25);wait_ui(4)
    vis=' | '.join(txts()).lower()
    adb('shell','settings','put','system','user_rotation','0',check=False);time.sleep(.25)
    if 'study' not in vis:raise AssertionError('workspace query lost after recreation')

def t08():
    adb('shell','am','force-stop',PKG,check=False)
    out=adb('shell','am','start','-W','-n',ACT,check=False);wait_ui()
    m=re.search(r'TotalTime:\s*(\d+)',out)
    if m and int(m.group(1))>5000:raise AssertionError('startup TotalTime '+m.group(1)+'ms')
    mem=adb('shell','dumpsys','meminfo',PKG,check=False)
    m2=re.search(r'TOTAL PSS:\s*(\d+)',mem) or re.search(r'TOTAL\s+(\d+)\s+',mem)
    if m2 and int(m2.group(1))>280000:raise AssertionError('startup PSS '+m2.group(1)+' KB')

def t09():
    home();tap('Ask PromptDeck');edit('analyze data');tap('Find the best approach');time.sleep(.7)
    req=['Analyze data','Clean & structure data','Statistics & patterns','Charts & visualization','Spreadsheet analysis','Extract insights']
    miss=[x for x in req if not has(x)]
    if miss:raise AssertionError('missing data capabilities '+repr(miss)+' visible='+repr(txts()[:140]))

def t10():
    home();tap('Browse all prompts');edit_slow('eli5');time.sleep(.8)
    visible=' | '.join(txts()).lower()
    if 'eli5' not in visible:raise AssertionError('eli5 result missing visible='+repr(txts()[:140]))
    tap_clickable('eli5',exact=True);time.sleep(.7)
    if not has('Copy prompt'):raise AssertionError('Copy prompt action missing visible='+repr(txts()[:140]))

for name,fn in [
 ('01_install_launch_catalog_no_anr',t01),('02_back_navigation',t02),('03_ask_photo_capabilities',t03),
 ('04_vertical_browse_hierarchy',t04),('05_no_midjourney_search_result',t05),('06_cold_and_warm_share_in',t06),
 ('07_workspace_state_recreation',t07),('08_startup_time_and_memory',t08),('09_data_analysis_routing',t09),('10_copy_prompt_action',t10)]: run(name,fn)

summary={'tests':len(R),'passed':sum(x['status']=='PASS' for x in R),'failed':sum(x['status']=='FAIL' for x in R),'results':R}
(OUT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
