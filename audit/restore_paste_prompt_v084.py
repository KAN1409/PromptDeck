#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')

s=JAVA.read_text(encoding='utf-8')

helper='''  void pastePromptFromClipboardV16(){\n    try{\n      android.content.ClipboardManager cb=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);\n      if(cb==null||!cb.hasPrimaryClip()||cb.getPrimaryClip()==null||cb.getPrimaryClip().getItemCount()==0){toast("Clipboard is empty");return;}\n      CharSequence raw=cb.getPrimaryClip().getItemAt(0).coerceToText(this);\n      String pasted=raw==null?"":raw.toString().trim();\n      if(pasted.isEmpty()){toast("Clipboard is empty");return;}\n      askGoal=pasted;contextDraft=pasted;askCapability="";discoverMode="ask";\n      home();\n      toast("Prompt pasted and understood");\n    }catch(Exception e){toast("Couldn't read clipboard");}\n  }\n\n'''

if 'void pastePromptFromClipboardV16()' not in s:
    anchor='  void home(){\n'
    if anchor not in s: raise SystemExit('home anchor missing')
    s=s.replace(anchor,helper+anchor,1)

old='root.addView(ask);View browse=modeChoiceCard(R.drawable.pd_mode_browse,"Browse all prompts"'
new='root.addView(ask);View paste=modeChoiceCard(R.drawable.pd_ic_content,"Paste a prompt","Paste from your clipboard and let PromptDeck understand it automatically.",PURPLE,()->pastePromptFromClipboardV16());root.addView(paste);View browse=modeChoiceCard(R.drawable.pd_mode_browse,"Browse all prompts"'
if '"Paste a prompt"' not in s:
    if old not in s: raise SystemExit('landing insertion anchor missing')
    s=s.replace(old,new,1)

old2='goal.setText(askGoal);root.addView(goal);Button find=primary("Find the best approach");root.addView(find);'
new2='goal.setText(askGoal);root.addView(goal);Button pasteClipboard=secondary("Paste from clipboard");pasteClipboard.setOnClickListener(v->pastePromptFromClipboardV16());root.addView(pasteClipboard);Button find=primary("Find the best approach");root.addView(find);'
if 'Paste from clipboard' not in s:
    if old2 not in s: raise SystemExit('ask insertion anchor missing')
    s=s.replace(old2,new2,1)

JAVA.write_text(s,encoding='utf-8')

g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 41',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.4'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')

for token in ['void pastePromptFromClipboardV16()','"Paste a prompt"','Paste from clipboard','Prompt pasted and understood']:
    if token not in s: raise SystemExit('missing '+token)
if 'versionCode 41' not in g or "versionName '0.8.4'" not in g: raise SystemExit('version bump failed')
print('Paste Prompt restored; version 0.8.4 (41)')
