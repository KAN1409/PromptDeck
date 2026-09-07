#!/usr/bin/env python3
import subprocess,xml.etree.ElementTree as ET,time,re,json,os,sys,shlex
from pathlib import Path

OUT=Path('/tmp/promptdeck-v14-comprehensive')
SC=OUT/'screens';SC.mkdir(parents=True,exist_ok=True)
PKG='com.kareem.promptdeck'
APK='android/app/build/outputs/apk/debug/app-debug.apk'
results=[]

def adb(*args,check=True,timeout=40):
    p=subprocess.run(['adb',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    if check and p.returncode!=0:raise RuntimeError('adb '+ ' '.join(args)+'\n'+p.stdout)
    return p.stdout.strip()

def wait(sec=.7):time.sleep(sec)
def screenshot(name):
    path=SC/(re.sub(r'[^A-Za-z0-9_.-]+','_',name)+'.png')
    subprocess.run(['adb','exec-out','screencap','-p'],stdout=open(path,'wb'),stderr=subprocess.DEVNULL)
    return str(path)

def dump():
    adb('shell','uiautomator','dump','/sdcard/window.xml',check=False)
    adb('pull','/sdcard/window.xml','/tmp/window.xml',check=False)
    try:return ET.parse('/tmp/window.xml').getroot()
    except Exception as e:raise RuntimeError('unable to parse UI dump: '+str(e))

def nodes():return list(dump().iter('node'))
def texts():return [n.attrib.get('text','') for n in nodes() if n.attrib.get('text','')]
def bounds(node):
    m=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.attrib.get('bounds',''))
    if not m:return None
    x1,y1,x2,y2=map(int,m.groups());return ((x1+x2)//2,(y1+y2)//2)
def find_text(needle,contains=True):
    needle=needle.lower()
    for n in nodes():
        t=n.attrib.get('text','')
        if (needle in t.lower() if contains else needle==t.lower()):return n
    return None
def has_text(needle):return find_text(needle) is not None
def tap_node(n):
    pt=bounds(n)
    if not pt:raise RuntimeError('node has no bounds: '+str(n.attrib))
    adb('shell','input','tap',str(pt[0]),str(pt[1]));wait()
def tap_text(*candidates):
    for c in candidates:
        n=find_text(c)
        if n is not None:tap_node(n);return c
    raise AssertionError('none of text candidates visible: '+repr(candidates)+'\nVisible: '+repr(texts()[:80]))
def first_edittext():
    for n in nodes():
        if n.attrib.get('class','').endswith('EditText'):return n
    return None
def input_text(value):
    n=first_edittext()
    if n is None:raise AssertionError('no EditText visible; '+repr(texts()[:60]))
    tap_node(n);adb('shell','input','keyevent','KEYCODE_MOVE_END',check=False)
    # clear existing text with KEYCODE_CLEAR then Ctrl+A/backspace fallback
    adb('shell','input','keyevent','KEYCODE_CLEAR',check=False)
    adb('shell','input','keyevent','113',check=False) # ctrl down-ish on some images, harmless
    adb('shell','input','keyevent','29',check=False)
    adb('shell','input','keyevent','KEYCODE_DEL',check=False)
    safe=value.replace(' ','%s').replace('&','\\&')
    adb('shell','input','text',safe);wait(.3)
def assert_resumed():
    out=adb('shell','dumpsys','activity','activities',check=False)
    if PKG not in out or ('mResumedActivity' in out and PKG not in out[out.find('mResumedActivity'):out.find('mResumedActivity')+300]):
        raise AssertionError('PromptDeck not resumed')
def launch(clear=False):
    if clear:adb('shell','pm','clear',PKG,check=False)
    adb('shell','monkey','-p',PKG,'-c','android.intent.category.LAUNCHER','1',check=False);wait(1.2)
    assert_resumed()
def home():
    launch(False)
    # up to four backs to normalize to landing without exiting; relaunch if needed
    for _ in range(4):
        if has_text('Ask PromptDeck') and has_text('Browse prompts'):return
        adb('shell','input','keyevent','KEYCODE_BACK',check=False);wait(.35)
        if not (has_text('Ask PromptDeck') or has_text('Browse prompts')):
            launch(False)
    if not (has_text('Ask PromptDeck') and has_text('Browse prompts')):raise AssertionError('could not reach landing; '+repr(texts()[:80]))

def record(name,status,detail=''):
    results.append({'name':name,'status':status,'detail':detail,'screenshot':screenshot(name+'_'+status)})
    print(status,name,detail)
def test(name,fn):
    try:
        fn();record(name,'PASS')
    except Exception as e:
        record(name,'FAIL',str(e)[:1200])
        try:launch(False)
        except:pass

def t_install_launch():
    out=adb('install','-r',APK,check=False,timeout=120)
    if 'Success' not in out:raise AssertionError(out)
    launch(True)
    if not has_text('Ask PromptDeck') or not has_text('Browse prompts'):raise AssertionError('landing choices missing: '+repr(texts()[:80]))

def t_back_from_ask():
    home();tap_text('Ask PromptDeck');
    if not has_text('Find the best approach'):raise AssertionError('Ask screen missing action')
    adb('shell','input','keyevent','KEYCODE_BACK');wait(.5)
    if not has_text('Ask PromptDeck') or not has_text('Browse prompts'):raise AssertionError('Back exited or skipped landing: '+repr(texts()[:80]))
    assert_resumed()

def t_ask_broad_photo():
    home();tap_text('Ask PromptDeck');input_text('photo edit');tap_text('Find the best approach');wait(.8)
    expected=['Enhance & restore','Retouch portrait','Background','Remove something','Light & color','Crop / expand','Change the look']
    visible=texts();missing=[x for x in expected if not any(x.lower() in t.lower() for t in visible)]
    if len(missing)>2:raise AssertionError('broad image capability chooser incomplete; missing '+repr(missing)+' visible='+repr(visible[:100]))
    if any('midjourney' in t.lower() for t in visible):raise AssertionError('Midjourney visible in broad image flow')

def t_ask_specific_decision():
    home();tap_text('Ask PromptDeck');input_text('compare two cars');tap_text('Find the best approach');wait(.9);assert_resumed()
    vis=' | '.join(texts()).lower()
    if not any(k in vis for k in ['compare options','best approach','recommend','using:']):raise AssertionError('specific decision did not reach recommendation: '+vis[:1200])

def t_browse_vertical_hierarchy():
    home();tap_text('Browse prompts');wait(.5)
    if not has_text('Browse by category'):raise AssertionError('category-first browse missing: '+repr(texts()[:100]))
    # choose a stable category
    tap_text('Images & Design','Writing & Communication','Technology & Data');wait(.5)
    if not has_text('Choose what you want to do'):raise AssertionError('subcategory screen missing: '+repr(texts()[:100]))
    # all rows must be vertically stacked: y centers should increase for visible named subcategories
    ns=[n for n in nodes() if n.attrib.get('text') and ('prompts' in n.attrib.get('text','').lower() or n.attrib.get('text') in ['Photo Editing & Restore','Image Generation','Portraits & People'])]
    ys=[bounds(n)[1] for n in ns if bounds(n)]
    if len(ys)>=3 and len(set(ys))<3:raise AssertionError('subcategory items overlap / not vertical')
    # enter first sensible subcategory
    for cand in ['Photo Editing & Restore','Image Generation','Portraits & People','Coding & Implementation','Drafting & Rewriting']:
        if has_text(cand):tap_text(cand);break
    else:
        # tap first non-header row that contains a count is too risky; fail explicitly
        raise AssertionError('no known subcategory visible: '+repr(texts()[:100]))
    wait(.5)
    vis=texts()
    if not any(re.search(r'\b\d+\b',t) and 'prompt' in t.lower() for t in vis):raise AssertionError('prompt list count/meta missing: '+repr(vis[:100]))

def t_browse_back_stack():
    # Start from a known hierarchy path then walk back level-by-level.
    home();tap_text('Browse prompts');tap_text('Images & Design','Writing & Communication','Technology & Data');wait(.3)
    if has_text('Photo Editing & Restore'):tap_text('Photo Editing & Restore')
    elif has_text('Image Generation'):tap_text('Image Generation')
    else:raise AssertionError('subcat not found')
    adb('shell','input','keyevent','KEYCODE_BACK');wait(.35)
    if not has_text('Choose what you want to do'):raise AssertionError('Back from prompt list did not return subcategories')
    adb('shell','input','keyevent','KEYCODE_BACK');wait(.35)
    if not has_text('Browse by category'):raise AssertionError('Back from subcategories did not return categories')
    adb('shell','input','keyevent','KEYCODE_BACK');wait(.35)
    if not has_text('Ask PromptDeck'):raise AssertionError('Back from categories did not return landing')

def t_midjourney_not_discoverable():
    # Product policy is ChatGPT-only; global ask/search should not expose a Midjourney command.
    home();tap_text('Ask PromptDeck');input_text('midjourney');tap_text('Find the best approach');wait(.8)
    vis=' | '.join(texts()).lower()
    if 'midjourney' in vis:raise AssertionError('Midjourney remains discoverable in app UI: '+vis[:1200])

def navigate_to_prompt_detail():
    home();tap_text('Browse prompts');tap_text('Images & Design','Writing & Communication','Technology & Data');wait(.3)
    if has_text('Photo Editing & Restore'):tap_text('Photo Editing & Restore')
    elif has_text('Image Generation'):tap_text('Image Generation')
    else:raise AssertionError('no subcategory')
    wait(.4)
    # Click first likely prompt row: choose first node with clickable=true and non-empty text not navigation/meta.
    for n in nodes():
        t=n.attrib.get('text','').strip()
        if not t:continue
        low=t.lower()
        if any(x in low for x in ['prompts','show more','all categories']):continue
        if n.attrib.get('clickable')=='true' and len(t)>3:
            tap_node(n);wait(.5)
            if has_text('Add to Stack') or has_text('Run now') or has_text('Favorite') or has_text('PROMPT'):return
    # fallback: tap first text near a card area not header
    raise AssertionError('could not open prompt detail; '+repr(texts()[:120]))

def t_prompt_add_stack_copy():
    navigate_to_prompt_detail()
    if has_text('Add to Stack'):tap_text('Add to Stack')
    elif has_text('Add to stack'):tap_text('Add to stack')
    else:raise AssertionError('Add to Stack action missing: '+repr(texts()[:100]))
    wait(.5)
    # selection may open stack/review directly or sticky bar appears
    if has_text('Review & Run'):tap_text('Review & Run')
    elif has_text('Ready to run'):tap_text('Ready to run')
    elif not (has_text('Copy final prompt') or has_text('Copy prompt')):
        # try a visible selected review bar
        for cand in ['Review','Run']:
            if has_text(cand):tap_text(cand);break
    wait(.4)
    if has_text('Copy final prompt'):tap_text('Copy final prompt')
    elif has_text('Copy prompt'):tap_text('Copy prompt')
    else:raise AssertionError('copy action missing after selection: '+repr(texts()[:120]))
    wait(.3)
    # Debug app permits run-as; make sure selected stack was non-empty in memory is not directly introspectable.
    assert_resumed()

def t_favorites_persist():
    navigate_to_prompt_detail()
    star=find_text('☆',contains=False) or find_text('★',contains=False)
    if star is None:raise AssertionError('favorite star missing')
    tap_node(star);wait(.2)
    xml=adb('shell','run-as',PKG,'cat','shared_prefs/promptdeck.xml',check=False)
    if 'favorite_prompt_ids' not in xml:raise AssertionError('favorite not persisted in SharedPreferences: '+xml[:600])
    adb('shell','am','force-stop',PKG);launch(False)
    xml2=adb('shell','run-as',PKG,'cat','shared_prefs/promptdeck.xml',check=False)
    if 'favorite_prompt_ids' not in xml2:raise AssertionError('favorite lost after restart')

def t_incoming_share_text():
    adb('shell','am','force-stop',PKG)
    adb('shell','am','start','-n',PKG+'/.MainActivity','-a','android.intent.action.SEND','-t','text/plain','--es','android.intent.extra.TEXT','shared_from_test',check=False)
    wait(.8);assert_resumed();vis=' | '.join(texts()).lower()
    # A functioning share target should surface or prefill the shared text somewhere.
    if 'shared_from_test' not in vis:raise AssertionError('app declares ACTION_SEND but shared text is not surfaced/prefilled: '+vis[:1000])

def t_state_survives_recreation():
    # Ask mode should survive a configuration-driven Activity recreation if workspace state is robust.
    home();tap_text('Ask PromptDeck');input_text('study');
    before=' | '.join(texts()).lower()
    adb('shell','settings','put','system','accelerometer_rotation','0',check=False)
    adb('shell','settings','put','system','user_rotation','1',check=False);wait(1.0)
    after=' | '.join(texts()).lower()
    adb('shell','settings','put','system','user_rotation','0',check=False);wait(.4)
    if 'study' not in after or 'find the best approach' not in after:raise AssertionError('Ask query/mode lost on Activity recreation/rotation. before='+before[:500]+' after='+after[:500])

def t_memory_startup_smoke():
    adb('shell','am','force-stop',PKG);adb('shell','am','start','-W','-n',PKG+'/.MainActivity',check=False);wait(.5)
    mem=adb('shell','dumpsys','meminfo',PKG,check=False)
    m=re.search(r'TOTAL PSS:\s*(\d+)',mem)
    if not m:m=re.search(r'TOTAL\s+(\d+)\s+',mem)
    if m:
        pss=int(m.group(1))
        # Very generous smoke threshold; report only catastrophic footprint.
        if pss>250000:raise AssertionError(f'PSS too high after startup: {pss} KB')

# Run all independent tests.
test('01_install_and_launch',t_install_launch)
test('02_back_from_ask_returns_landing',t_back_from_ask)
test('03_ask_broad_photo_routes_to_capabilities',t_ask_broad_photo)
test('04_ask_specific_decision_no_crash',t_ask_specific_decision)
test('05_browse_is_vertical_category_subcategory_prompt',t_browse_vertical_hierarchy)
test('06_browse_back_navigation_level_by_level',t_browse_back_stack)
test('07_midjourney_not_discoverable',t_midjourney_not_discoverable)
test('08_prompt_add_stack_and_copy',t_prompt_add_stack_copy)
test('09_favorite_persists_restart',t_favorites_persist)
test('10_incoming_share_text_is_consumed',t_incoming_share_text)
test('11_workspace_state_survives_recreation',t_state_survives_recreation)
test('12_startup_memory_smoke',t_memory_startup_smoke)

passes=sum(r['status']=='PASS' for r in results);fails=len(results)-passes
summary={'tests':len(results),'passed':passes,'failed':fails,'results':results}
(OUT/'emulator-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
lines=['# PromptDeck v14 — Emulator User-Flow Tests','',f'**{passes}/{len(results)} passed · {fails} failed**','']
for r in results:
    lines.append(f"- **{r['status']}** — {r['name']}"+(f": {r['detail']}" if r['detail'] else ''))
(OUT/'emulator-results.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'passed':passes,'failed':fails},indent=2))
# Do not fail the emulator action; report is the product. Release gate happens in workflow after artifact upload.
