#!/usr/bin/env python3
import json,re,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path

PKG='com.kareem.promptdeck';APK='android/app/build/outputs/apk/debug/app-debug.apk'
OUT=Path('/tmp/promptdeck-v15c-runtime');OUT.mkdir(parents=True,exist_ok=True);SC=OUT/'screens';SC.mkdir(exist_ok=True);R=[]

def adb(*a,check=True,timeout=90):
    p=subprocess.run(['adb',*a],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    if check and p.returncode:raise RuntimeError(p.stdout)
    return p.stdout.strip()
def dump():
    adb('shell','uiautomator','dump','/sdcard/w.xml',check=False);adb('pull','/sdcard/w.xml','/tmp/w.xml',check=False)
    return ET.parse('/tmp/w.xml').getroot()
def nodes():return list(dump().iter('node'))
def txts():return[n.attrib.get('text','') for n in nodes() if n.attrib.get('text')]
def find(s,exact=False):
    q=s.lower()
    for n in nodes():
        t=n.attrib.get('text','')
        if (t.lower()==q if exact else q in t.lower()):return n
    return None
def has(s):return find(s) is not None
def center(n):
    m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
    if not m:raise AssertionError('no bounds')
    a,b,c,d=map(int,m.groups());return((a+c)//2,(b+d)//2)
def tap(s):
    n=find(s)
    if n is None:raise AssertionError('missing '+s+' visible='+repr(txts()[:100]))
    x,y=center(n);adb('shell','input','tap',str(x),str(y));time.sleep(.5)
def edit(value):
    n=next((n for n in nodes() if n.attrib.get('class','').endswith('EditText')),None)
    if n is None:raise AssertionError('no edit field visible='+repr(txts()[:100]))
    x,y=center(n);adb('shell','input','tap',str(x),str(y));adb('shell','input','keyevent','KEYCODE_CTRL_A',check=False);adb('shell','input','keyevent','KEYCODE_DEL',check=False);adb('shell','input','text',value.replace(' ','%s'));time.sleep(.3)
def shot(name):
    p=SC/(name+'.png');subprocess.run(['adb','exec-out','screencap','-p'],stdout=open(p,'wb'));return str(p)
def workspace_ready():return has('Ask PromptDeck') and (has('Browse all prompts') or has('Browse prompts'))
def landing_ready():return has('How do you want to start?') and has('Browse all prompts')
def wait_ui(timeout=12):
    end=time.time()+timeout
    while time.time()<end:
        try:
            if workspace_ready():return
        except:pass
        time.sleep(.3)
    raise AssertionError('workspace did not become ready; visible='+repr(txts()[:100]))
def launch(clear=False):
    if clear:adb('shell','pm','clear',PKG,check=False)
    adb('shell','monkey','-p',PKG,'-c','android.intent.category.LAUNCHER','1',check=False);wait_ui()
def home():
    launch(False)
    for _ in range(5):
        if landing_ready():return
        adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.4)
    if not landing_ready():raise AssertionError('could not normalize to landing; visible='+repr(txts()[:100]))
def run(name,fn):
    try:fn();R.append({'name':name,'status':'PASS','screenshot':shot(name+'_PASS')});print('PASS',name)
    except Exception as e:R.append({'name':name,'status':'FAIL','detail':str(e)[:1200],'screenshot':shot(name+'_FAIL')});print('FAIL',name,e)

def t01():
    out=adb('install','-r',APK,check=False,timeout=180)
    if 'Success' not in out:raise AssertionError(out)
    launch(True)
    if not landing_ready():raise AssertionError('fresh launch did not reach landing; visible='+repr(txts()[:100]))
    anr=adb('shell','dumpsys','activity','lastanr',check=False).lower()
    if PKG in anr and ('not responding' in anr or 'anr' in anr):raise AssertionError('startup ANR recorded: '+anr[:900])
    visible=' | '.join(txts())
    if '3,304-prompt library' not in visible:raise AssertionError('dynamic final catalog count missing: '+visible[:1200])
def t02():
    home();tap('Ask PromptDeck');
    if not has('Find the best approach'):raise AssertionError('Ask UI missing')
    adb('shell','input','keyevent','KEYCODE_BACK');time.sleep(.5)
    if not landing_ready():raise AssertionError('Back did not return landing')
def t03():
    home();tap('Ask PromptDeck');edit('photo edit');tap('Find the best approach');time.sleep(.8)
    req=['Enhance & restore','Retouch portrait','Background','Light & color'];missing=[x for x in req if not has(x)]
    if missing:raise AssertionError('missing capabilities '+repr(missing)+' visible='+repr(txts()[:120]))
def t04():
    home();tap('Browse all prompts');time.sleep(.5)
    if not has('Browse by category'):raise AssertionError('category-first browse missing: '+repr(txts()[:100]))
    tap('Images & Design');time.sleep(.4)
    if not has('Choose what you want to do'):raise AssertionError('subcategory level missing')
    if not(has('Photo Editing & Restore') or has('Image Generation')):raise AssertionError('image subcategories missing')
def t05():
    home();tap('Browse all prompts');
    edit('midjourney');time.sleep(.7)
    bad=[t for t in txts() if 'midjourney' in t.lower() and t.lower().strip()!='midjourney']
    if bad:raise AssertionError('Midjourney result visible: '+repr(bad[:8]))
def t06():
    adb('shell','am','force-stop',PKG);adb('shell','am','start','-n',PKG+'/.MainActivity','-a','android.intent.action.SEND','-t','text/plain','--es','android.intent.extra.TEXT','shared_runtime_probe',check=False);wait_ui();time.sleep(.3)
    if 'shared_runtime_probe' not in ' | '.join(txts()).lower():raise AssertionError('shared text not consumed: '+repr(txts()[:100]))
def t07():
    home();tap('Ask PromptDeck');edit('study');time.sleep(.2)
    adb('shell','settings','put','system','accelerometer_rotation','0',check=False);adb('shell','settings','put','system','user_rotation','1',check=False);time.sleep(1.0)
    vis=' | '.join(txts()).lower();adb('shell','settings','put','system','user_rotation','0',check=False);time.sleep(.4)
    if 'study' not in vis:raise AssertionError('workspace query lost after recreation')
def t08():
    adb('shell','am','force-stop',PKG);out=adb('shell','am','start','-W','-n',PKG+'/.MainActivity',check=False);wait_ui();
    m=re.search(r'TotalTime:\s*(\d+)',out)
    if m and int(m.group(1))>5000:raise AssertionError('startup TotalTime too high '+m.group(1)+'ms')
    mem=adb('shell','dumpsys','meminfo',PKG,check=False);m2=re.search(r'TOTAL PSS:\s*(\d+)',mem) or re.search(r'TOTAL\s+(\d+)\s+',mem)
    if m2 and int(m2.group(1))>280000:raise AssertionError('startup PSS too high '+m2.group(1)+' KB')

for name,fn in [('01_install_launch_no_anr_dynamic_count',t01),('02_back_navigation',t02),('03_ask_photo_capabilities',t03),('04_vertical_browse_hierarchy',t04),('05_no_midjourney_search_result',t05),('06_share_in_consumed',t06),('07_workspace_state_recreation',t07),('08_startup_time_and_memory',t08)]:run(name,fn)
summary={'tests':len(R),'passed':sum(x['status']=='PASS' for x in R),'failed':sum(x['status']=='FAIL' for x in R),'results':R}
(OUT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
