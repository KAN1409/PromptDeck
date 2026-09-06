#!/usr/bin/env python3
from pathlib import Path

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=JAVA.read_text(encoding='utf-8')
old='card.setMinHeight(dp(68));'
new='card.setMinimumHeight(dp(68));'
if old not in s:
    if new in s:
        print('Capability card minimum-height fix already applied')
        raise SystemExit(0)
    raise SystemExit('capability card height anchor missing')
s=s.replace(old,new,1)
if 'setMinHeight(dp(68))' in s: raise SystemExit('invalid LinearLayout setMinHeight remains')
JAVA.write_text(s,encoding='utf-8')
print('Capability card compile fix applied')
