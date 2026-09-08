#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
s=JAVA.read_text(encoding='utf-8')
old='"Browse all prompts","Search and explore the complete 3,375-prompt library yourself."'
new='"Browse all prompts","Search and explore the complete "+all.size()+"-prompt library yourself."'
if old not in s:
    raise SystemExit('landing catalog-count anchor missing')
s=s.replace(old,new,1)
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.2-rc3'",g,count=1)
JAVA.write_text(s,encoding='utf-8');GRADLE.write_text(g,encoding='utf-8')
assert '"Search and explore the complete "+all.size()+"-prompt library yourself."' in s
assert "versionName '0.8.2-rc3'" in g
print('v15c: landing count is dynamic')
