#!/usr/bin/env python3
from pathlib import Path
import re
p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text()
s=s.replace('View paste=modeChoiceCard(R.drawable.pd_ic_content,"Paste a prompt","Paste from your clipboard and let PromptDeck understand it automatically.",PURPLE,()->pastePromptFromClipboardV16());root.addView(paste);','View paste=modeChoiceCard(R.drawable.pd_ic_content,"Add a prompt","Paste a complete prompt and save it to your library.",PURPLE,()->showBulkPaste());root.addView(paste);',1)
s=s.replace('Button pasteClipboard=secondary("Paste from clipboard");pasteClipboard.setOnClickListener(v->pastePromptFromClipboardV16());root.addView(pasteClipboard);','',1)
start=s.find('  void pastePromptFromClipboardV16(){')
end=s.find('\n\n  void home(){',start)
if start>=0 and end>start:s=s[:start]+s[end:]
p.write_text(s)
g=Path('android/app/build.gradle');x=g.read_text();x=re.sub(r'versionCode\s+\d+','versionCode 42',x,count=1);x=re.sub(r"versionName\s+'[^']+'","versionName '0.8.5'",x,count=1);g.write_text(x)
assert '"Add a prompt"' in s and '()->showBulkPaste()' in s and 'pastePromptFromClipboardV16' not in s
print('Add Prompt restored')
