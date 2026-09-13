#!/usr/bin/env python3
from pathlib import Path
import re
main=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
gradle=Path('android/app/build.gradle')
s=main.read_text()
s=s.replace('View paste=modeChoiceCard(R.drawable.pd_ic_content,"Paste a prompt","Paste from your clipboard and let PromptDeck understand it automatically.",PURPLE,()->pastePromptFromClipboardV16());root.addView(paste);','View paste=modeChoiceCard(R.drawable.pd_ic_content,"Add a prompt","Paste a complete prompt and save it to your library automatically.",PURPLE,()->showBulkPaste());root.addView(paste);')
s=s.replace('Button pasteClipboard=secondary("Paste from clipboard");pasteClipboard.setOnClickListener(v->pastePromptFromClipboardV16());root.addView(pasteClipboard);','')
start=s.find('  void pastePromptFromClipboardV16(){')
if start>=0:
    end=s.find('\n\n  void home(){',start)
    if end>start:s=s[:start]+s[end:]
for x in ['void showBulkPaste()','inferPromptCategoryV86','inferPromptSubcategoryV86','parseBulkCommands(raw,"")','"Add a prompt"','()->showBulkPaste()']:
    assert x in s,x
assert 'pastePromptFromClipboardV16' not in s
main.write_text(s)
g=gradle.read_text();g=re.sub(r'versionCode\s+\d+','versionCode 42',g,count=1);g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.5'",g,count=1);gradle.write_text(g)
print('PromptDeck v0.8.5 Add Prompt flow finalized')
