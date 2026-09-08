#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
MANIFEST=Path('android/app/src/main/AndroidManifest.xml')
GRADLE=Path('android/app/build.gradle')

s=JAVA.read_text(encoding='utf-8')

# Built-in library count must not increase when the user adds custom prompts.
s=s.replace('String.format(Locale.US,"%,d",all.size())','String.format(Locale.US,"%,d",BUILTIN_CACHE_V15.size())')

# Handle share-to-PromptDeck while the Activity is already alive. This complements
# the cold-start consumeIncomingShareV15() path and avoids creating a stale second Activity.
if 'onNewIntent(Intent intent)' not in s:
    anchor='  @Override protected void onSaveInstanceState(Bundle out)'
    if anchor not in s:
        raise SystemExit('missing state anchor')
    block='''  @Override protected void onNewIntent(Intent intent){\n    super.onNewIntent(intent);setIntent(intent);\n    if(BUILTIN_CACHE_READY_V15){consumeIncomingShareV15();home();}\n  }\n\n'''
    s=s.replace(anchor,block+anchor,1)

JAVA.write_text(s,encoding='utf-8')

m=MANIFEST.read_text(encoding='utf-8')
activity='''        <activity\n            android:name=".MainActivity"\n            android:exported="true">'''
replacement='''        <activity\n            android:name=".MainActivity"\n            android:exported="true"\n            android:launchMode="singleTop">'''
if activity in m:
    m=m.replace(activity,replacement,1)
elif 'android:name=".MainActivity"' in m and 'android:launchMode="singleTop"' not in m:
    raise SystemExit('MainActivity manifest shape changed')
MANIFEST.write_text(m,encoding='utf-8')

g=GRADLE.read_text(encoding='utf-8')
# Keep the current RC identity; the frozen source, not another version suffix, is the milestone.
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.2-rc4'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')

for token,hay in [
    ('BUILTIN_CACHE_V15.size()',s),
    ('onNewIntent(Intent intent)',s),
    ('android:launchMode="singleTop"',m),
    ("versionName '0.8.2-rc4'",g),
]:
    if token not in hay: raise SystemExit('release-freeze gate missing '+token)
print('release freeze refinements applied: stable built-in count + warm share-in')
