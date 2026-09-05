#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Python-authored patch strings can accidentally leave Java 15's \s escape
# (single backslash in Java source). PromptDeck compiles with Java source 8,
# so regex whitespace must be written as \\s in the Java source.
fixed=re.sub(r'(?<!\\)\\s', r'\\\\s', s)

# Keep this guard intentionally narrow: only a single unescaped backslash-s
# is repaired. Existing Java regex strings that already contain \\s are left intact.
if fixed==s:
    print('No Java 8 regex escape repair needed')
else:
    p.write_text(fixed,encoding='utf-8')
    print('Repaired Java 8 regex whitespace escapes')
