#!/usr/bin/env python3
import subprocess,xml.etree.ElementTree as ET,time,re,json
from pathlib import Path
OUT=Path('/tmp/promptdeck-v14-comprehensive');OUT.mkdir(parents=True,exist_ok=True)
PKG='com.kareem.promptdeck'; STUB='com.openai.chatgpt'

def adb(*a,check=True):
 p=subprocess.run(['adb',*a],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 if check and p.returncode:raise RuntimeError(p.stdout)
 return p.stdout.strip()
def wait(x=.5):time.sleep(x)
def dump():
 adb('shell','uiautomator','dump','/sdcard/w.xml',check=False);adb('pull','/sdcard/w.xml','/tmp/w.xml',check=False)
 return ET.parse('/tmp/w.xml').getroot()
def nodes():return list(dump().iter('node'))
def texts():return [n.attrib.get('text','') for n in nodes() if n.attrib.get('text')]
def pt(n):
 m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
 if not m:return None
 a,b,c,d=map(int,m.groups());return((a+c)//2,(b+d)//2)
def find(s):
 for n in nodes():
  if s.lower() in n.attrib.get('text','').lower():return n
def tap(s):
 n=find(s)
 if n is None:raise AssertionError('missing '+s+' visible='+repr(texts()[:100]))
 x,y=pt(n);adb('shell','input','tap',str(x),str(y));wait()
def edit(value):
 n=next((n for n in nodes() if n.attrib.get('class','').endswith('EditText')),None)
 if n is None:raise AssertionError('no edit text')
 x,y=pt(n);adb('shell','input','tap',str(x),str(y));adb('shell','input','text',value.replace(' ','%s'));wait(.2)
def launch():adb('shell','monkey','-p',PKG,'1',check=False);wait(1)

result={'status':'FAIL','detail':''}
try:
    # install stub now that emulator is running
    stub='/tmp/chatgptstub/app/build/outputs/apk/debug/app-debug.apk'
    out=adb('install','-r',stub,check=False)
    if 'Success' not in out:raise AssertionError('stub install failed: '+out)
    launch()
    # normalize to landing
    for _ in range(4):
        if find('Ask PromptDeck'):break
        adb('shell','input','keyevent','KEYCODE_BACK',check=False);wait(.3)
        launch()
    tap('Ask PromptDeck');edit('summarize this text');tap('Find the best approach');wait(.8)
    # pick an available recommendation/capability path
    for cand in ['Summarize','Use this approach','Use this workflow','Add to Stack','Review & Run','Ready to run']:
        if find(cand):tap(cand);wait(.5)
    # If a selection bar is present, open it.
    for cand in ['Review & Run','Ready to run','Review']:
        if find(cand):tap(cand);wait(.4);break
    # Run action may be in sheet or prompt detail.
    run=None
    for cand in ['Run with ChatGPT','Open in ChatGPT']:
        if find(cand):run=cand;break
    if not run:raise AssertionError('Run with ChatGPT action not reachable; visible='+repr(texts()[:120]))
    tap(run);wait(1)
    resumed=adb('shell','dumpsys','activity','activities',check=False)
    if STUB not in resumed:raise AssertionError('explicit ChatGPT package did not receive intent')
    payload='\n'.join(texts())
    if 'RECEIVED_PROMPT' not in payload:raise AssertionError('stub opened without prompt payload: '+payload[:600])
    body=payload.split('RECEIVED_PROMPT',1)[1]
    if not body.strip():raise AssertionError('received prompt body empty')
    forbidden=['TASK —','USER REQUEST / CONTEXT:','SELECTED PROMPT MODULES:','EXECUTION RULES:','Use available ChatGPT tools only']
    bad=[x for x in forbidden if x in body]
    if bad:raise AssertionError('wrapper text leaked into outgoing payload: '+repr(bad))
    result={'status':'PASS','detail':'ChatGPT stub received non-empty prompt-only ACTION_SEND payload'}
except Exception as e:
    result={'status':'FAIL','detail':str(e)[:1400]}
(OUT/'chatgpt-handoff.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(OUT/'chatgpt-handoff.md').write_text('# ChatGPT handoff emulator test\n\n**'+result['status']+'** — '+result['detail']+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
