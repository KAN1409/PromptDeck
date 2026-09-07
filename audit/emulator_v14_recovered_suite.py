#!/usr/bin/env python3
import subprocess,xml.etree.ElementTree as ET,time,re,json,os
from pathlib import Path
OUT=Path('/tmp/promptdeck-v14-recovered');SC=OUT/'screens';SC.mkdir(parents=True,exist_ok=True)
PKG='com.kareem.promptdeck';APK='android/app/build/outputs/apk/debug/app-debug.apk';results=[]

def adb(*a,check=True,timeout=60):
 p=subprocess.run(['adb',*a],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 if check and p.returncode:raise RuntimeError(p.stdout)
 return p.stdout.strip()
def shot(n):
 p=SC/(re.sub(r'[^A-Za-z0-9_.-]','_',n)+'.png');subprocess.run(['adb','exec-out','screencap','-p'],stdout=open(p,'wb'),stderr=subprocess.DEVNULL);return str(p)
def dump_safe():
 for _ in range(3):
  adb('shell','uiautomator','dump','--compressed','/sdcard/u.xml',check=False,timeout=12)
  adb('pull','/sdcard/u.xml','/tmp/u.xml',check=False,timeout=12)
  try:return ET.parse('/tmp/u.xml').getroot()
  except:time.sleep(.35)
 return None
def nodes():
 r=dump_safe();return list(r.iter('node')) if r is not None else []
def texts():return [n.attrib.get('text','') for n in nodes() if n.attrib.get('text')]
def center(n):
 m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',n.attrib.get('bounds',''))
 if not m:return None
 x1,y1,x2,y2=map(int,m.groups());return((x1+x2)//2,(y1+y2)//2)
def find(s,exact=False):
 for n in nodes():
  t=n.attrib.get('text','')
  if (t.lower()==s.lower()) if exact else (s.lower() in t.lower()):return n
 return None
def has(s):return find(s) is not None
def tap_node(n):
 c=center(n)
 if not c:raise AssertionError('no bounds '+repr(n.attrib))
 adb('shell','input','tap',str(c[0]),str(c[1]),check=False);time.sleep(.45)
def tap(*names):
 for s in names:
  n=find(s)
  if n is not None:tap_node(n);return s
 raise AssertionError('missing '+repr(names)+' visible='+repr(texts()[:120]))
def edit(value):
 n=next((n for n in nodes() if n.attrib.get('class','').endswith('EditText')),None)
 if n is None:raise AssertionError('no EditText '+repr(texts()[:100]))
 tap_node(n);adb('shell','input','keyevent','KEYCODE_CLEAR',check=False);time.sleep(.1)
 adb('shell','input','text',value.replace(' ','%s'),check=False);time.sleep(.3)
def resumed_package():
 s=adb('shell','dumpsys','activity','activities',check=False)
 m=re.search(r'mResumedActivity:.*? ([A-Za-z0-9_.]+)/',s)
 return m.group(1) if m else ''
def recover_anr_and_wait_ready(timeout=35):
 start=time.time();pressed=0
 while time.time()-start<timeout:
  ts=texts()
  joined=' | '.join(ts)
  if "isn't responding" in joined.lower() or 'is not responding' in joined.lower():
   n=find('Wait')
   if n is not None:tap_node(n);pressed+=1;time.sleep(.8);continue
  if has('Ask PromptDeck') and has('Browse prompts'):return time.time()-start,pressed
  time.sleep(.45)
 raise AssertionError('landing not ready in time; visible='+repr(texts()[:80]))
def launch(clear=False):
 if clear:adb('shell','pm','clear',PKG,check=False)
 adb('shell','monkey','-p',PKG,'-c','android.intent.category.LAUNCHER','1',check=False);return recover_anr_and_wait_ready()
def landing():
 # Try back within current instance; if gone, launch and recover.
 for _ in range(5):
  if has('Ask PromptDeck') and has('Browse prompts'):return
  if "isn't responding" in ' | '.join(texts()).lower():
   if has('Wait'):tap('Wait');time.sleep(.5);continue
  adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.3)
 try:recover_anr_and_wait_ready(8)
 except:launch(False)
def result(name,status,detail=''):
 d={'name':name,'status':status,'detail':detail,'screenshot':shot(name+'_'+status)};results.append(d);print(status,name,detail)
def test(name,fn):
 try:fn();result(name,'PASS')
 except Exception as e:result(name,'FAIL',str(e)[:1500])

def t_startup_timing():
 out=adb('install','-r',APK,check=False,timeout=120)
 if 'Success' not in out:raise AssertionError(out)
 elapsed,anrs=launch(True)
 (OUT/'startup.json').write_text(json.dumps({'ready_seconds':elapsed,'anr_wait_pressed':anrs},indent=2))
 if anrs>0:raise AssertionError(f'ANR occurred during startup; UI became ready after {elapsed:.2f}s and Wait was pressed {anrs} time(s)')

def t_landing_and_back():
 landing();tap('Ask PromptDeck');
 if not has('Find the best approach'):raise AssertionError('Ask content missing')
 adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.4)
 if not has('Ask PromptDeck'):raise AssertionError('back from Ask did not return landing')

def t_ask_photo():
 landing();tap('Ask PromptDeck');edit('photo edit');tap('Find the best approach');time.sleep(.7)
 vis=' | '.join(texts()).lower()
 need=['enhance & restore','retouch portrait','background','remove something','light & color','crop / expand','change the look']
 miss=[x for x in need if x not in vis]
 if len(miss)>2:raise AssertionError('capabilities missing '+repr(miss)+' '+vis[:1200])

def t_ask_study():
 landing();tap('Ask PromptDeck');edit('study');tap('Find the best approach');time.sleep(.6)
 vis=' | '.join(texts()).lower()
 for x in ['explain a topic','tutor me','study plan','quiz me']:
  if x not in vis:raise AssertionError('study chooser missing '+x+' '+vis[:1200])

def t_ask_compare():
 landing();tap('Ask PromptDeck');edit('compare two cars');tap('Find the best approach');time.sleep(.8)
 vis=' | '.join(texts()).lower()
 if not any(x in vis for x in ['best approach','compare options','recommend the best','using:']):raise AssertionError('specific decision result missing '+vis[:1200])

def enter_browse_subcat():
 landing();tap('Browse prompts')
 if not has('Browse by category'):raise AssertionError('browse not category-first '+repr(texts()[:100]))
 tap('Images & Design','Writing & Communication','Technology & Data');
 if not has('Choose what you want to do'):raise AssertionError('subcategory page missing '+repr(texts()[:100]))
 for c in ['Photo Editing & Restore','Image Generation','Portraits & People','Coding & Implementation','Rewrite & Polish']:
  if has(c):tap(c);return
 raise AssertionError('known subcategory missing '+repr(texts()[:100]))
def t_browse_hierarchy():
 enter_browse_subcat();vis=texts()
 if not any('prompt' in x.lower() and re.search(r'\d',x) for x in vis):raise AssertionError('prompt count/list missing '+repr(vis[:100]))
 # back exactly one level at a time
 adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.35)
 if not has('Choose what you want to do'):raise AssertionError('back prompt->subcategory failed')
 adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.35)
 if not has('Browse by category'):raise AssertionError('back subcategory->categories failed')
 adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.35)
 if not has('Ask PromptDeck'):raise AssertionError('back categories->landing failed')
def t_search_midjourney():
 landing();tap('Browse prompts')
 # Browse screen should expose a search field above category list.
 edit('midjourney');time.sleep(.7)
 vis=' | '.join(texts()).lower()
 if 'midjourney' in vis:raise AssertionError('Midjourney is discoverable in ChatGPT-only catalog: '+vis[:1400])

def open_first_prompt_detail():
 enter_browse_subcat();time.sleep(.4)
 ns=nodes()
 # Tap first substantial text row below header/meta. Parent card will receive coordinate tap.
 blacklist=['prompt','show more','all categories','images & design','writing & communication','technology & data']
 for n in ns:
  t=n.attrib.get('text','').strip();c=center(n)
  if not t or not c or c[1]<240 or len(t)<4:continue
  low=t.lower()
  if any(b==low for b in blacklist) or ('prompt' in low and re.search(r'\d',low)):continue
  tap_node(n);time.sleep(.5)
  if any(has(x) for x in ['Add to Stack','Run now','Favorite','Copy prompt']):return
 raise AssertionError('could not open prompt detail '+repr(texts()[:140]))
def t_stack_copy_and_run_entry():
 open_first_prompt_detail()
 if has('Add to Stack'):tap('Add to Stack')
 elif has('Add to stack'):tap('Add to stack')
 else:raise AssertionError('Add to Stack missing '+repr(texts()[:100]))
 time.sleep(.4)
 for x in ['Review & Run','Ready to run']:
  if has(x):tap(x);break
 time.sleep(.4)
 if not (has('Copy final prompt') or has('Copy prompt')):raise AssertionError('copy prompt action missing '+repr(texts()[:120]))
 tap('Copy final prompt','Copy prompt')
 if not (has('Run with ChatGPT') or has('Open in ChatGPT')):raise AssertionError('run action missing '+repr(texts()[:120]))
def t_favorite_persistence():
 landing();open_first_prompt_detail()
 star=find('☆',exact=True) or find('★',exact=True)
 if star is None:raise AssertionError('favorite star not exposed/accessibility missing')
 tap_node(star);time.sleep(.2)
 xml=adb('shell','run-as',PKG,'cat','shared_prefs/promptdeck.xml',check=False)
 if 'favorite_prompt_ids' not in xml:raise AssertionError('favorite not persisted: '+xml[:700])
 adb('shell','am','force-stop',PKG,check=False);elapsed,anrs=launch(False)
 xml2=adb('shell','run-as',PKG,'cat','shared_prefs/promptdeck.xml',check=False)
 if 'favorite_prompt_ids' not in xml2:raise AssertionError('favorite lost after restart')
def t_more_menu_reachability():
 landing();
 if has('•••'):tap('•••')
 elif has('...'):tap('...')
 else:
  # fixed location top-right fallback only for menu icon if no text accessibility
  adb('shell','input','tap','745','42',check=False);time.sleep(.4)
 vis=' | '.join(texts()).lower()
 if 'my prompts' not in vis or 'settings' not in vis:raise AssertionError('More menu missing destinations '+vis[:900])
def t_custom_prompt_paste_persistence():
 landing();
 if has('•••'):tap('•••')
 else:adb('shell','input','tap','745','42',check=False);time.sleep(.3)
 tap('My Prompts');time.sleep(.4)
 # choose paste flow if present
 if has('Paste custom prompts'):tap('Paste custom prompts')
 elif has('Paste'):tap('Paste')
 else:raise AssertionError('custom paste flow missing '+repr(texts()[:120]))
 edit('Test custom prompt created by emulator QA');
 tap('Parse & add','Add');time.sleep(.5)
 xml=adb('shell','run-as',PKG,'cat','shared_prefs/promptdeck.xml',check=False)
 if 'Test custom prompt created by emulator QA' not in xml:raise AssertionError('custom prompt not persisted '+xml[:1000])

def t_import_export_intents():
 # Reach My Prompts; validate Import/Export launch document UI. Exact round-trip handled statically.
 landing();
 if has('•••'):tap('•••')
 else:adb('shell','input','tap','745','42',check=False);time.sleep(.3)
 tap('My Prompts');time.sleep(.3)
 if not has('Import'):raise AssertionError('Import action missing '+repr(texts()[:100]))
 tap('Import');time.sleep(.5)
 rp=resumed_package()
 if 'documentsui' not in rp.lower():raise AssertionError('Import did not launch document picker; resumed='+rp)
 adb('shell','input','keyevent','KEYCODE_BACK',check=False);time.sleep(.4)
 # export may be visible after return
 if not has('Export'):
  # re-enter My Prompts if needed
  landing();
  if has('•••'):tap('•••')
  else:adb('shell','input','tap','745','42',check=False);time.sleep(.3)
  tap('My Prompts');time.sleep(.3)
 tap('Export');time.sleep(.5);rp=resumed_package()
 if 'documentsui' not in rp.lower():raise AssertionError('Export did not launch document create picker; resumed='+rp)
 adb('shell','input','keyevent','KEYCODE_BACK',check=False)
def t_incoming_share():
 adb('shell','am','force-stop',PKG,check=False)
 adb('shell','am','start','-n',PKG+'/.MainActivity','-a','android.intent.action.SEND','-t','text/plain','--es','android.intent.extra.TEXT','shared_from_deep_test',check=False);time.sleep(.5)
 # recover possible startup ANR without requiring landing immediately
 try:recover_anr_and_wait_ready(35)
 except:pass
 vis=' | '.join(texts()).lower()
 if 'shared_from_deep_test' not in vis:raise AssertionError('ACTION_SEND text is ignored despite manifest share target '+vis[:1200])
def t_rotation_state():
 landing();tap('Ask PromptDeck');edit('study')
 adb('shell','settings','put','system','accelerometer_rotation','0',check=False);adb('shell','settings','put','system','user_rotation','1',check=False);time.sleep(1)
 # handle recreation ANR if any
 if has('Wait'):tap('Wait');time.sleep(.6)
 vis=' | '.join(texts()).lower();adb('shell','settings','put','system','user_rotation','0',check=False)
 if 'study' not in vis or 'find the best approach' not in vis:raise AssertionError('workspace/query lost across recreation '+vis[:1000])

def t_memory_and_process():
 adb('shell','am','force-stop',PKG,check=False);start=time.time();adb('shell','am','start','-W','-n',PKG+'/.MainActivity',check=False);elapsed,anrs=recover_anr_and_wait_ready(35)
 mem=adb('shell','dumpsys','meminfo',PKG,check=False);m=re.search(r'TOTAL PSS:\s*(\d+)',mem) or re.search(r'TOTAL\s+(\d+)\s+',mem)
 data={'ready_seconds_after_start_command':elapsed,'anr_wait_pressed':anrs,'pss_kb':int(m.group(1)) if m else None};(OUT/'runtime-metrics.json').write_text(json.dumps(data,indent=2))
 if anrs:raise AssertionError('startup ANR repeats after force-stop '+json.dumps(data))

for name,fn in [
 ('01_startup_timing_no_anr',t_startup_timing),('02_landing_back',t_landing_and_back),('03_ask_photo',t_ask_photo),('04_ask_study',t_ask_study),('05_ask_compare',t_ask_compare),('06_browse_hierarchy_and_back',t_browse_hierarchy),('07_midjourney_not_searchable',t_search_midjourney),('08_stack_copy_run_entry',t_stack_copy_and_run_entry),('09_favorite_persistence',t_favorite_persistence),('10_more_menu',t_more_menu_reachability),('11_custom_prompt_persistence',t_custom_prompt_paste_persistence),('12_import_export_document_intents',t_import_export_intents),('13_incoming_share_consumed',t_incoming_share),('14_rotation_state',t_rotation_state),('15_runtime_memory_restart',t_memory_and_process)]:test(name,fn)

p=sum(x['status']=='PASS' for x in results);f=len(results)-p
summary={'passed':p,'failed':f,'tests':len(results),'results':results};(OUT/'results.json').write_text(json.dumps(summary,indent=2))
(OUT/'results.md').write_text('# PromptDeck v14 recovered deep emulator suite\n\n**%d/%d passed · %d failed**\n\n%s\n'%(p,len(results),f,'\n'.join('- **%s** %s%s'%(x['status'],x['name'],(': '+x['detail']) if x['detail'] else '') for x in results)))
print(json.dumps({'passed':p,'failed':f},indent=2))
