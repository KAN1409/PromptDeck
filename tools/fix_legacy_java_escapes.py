#!/usr/bin/env python3
from pathlib import Path

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Repair escape sequences that were flattened by the historical patch chain.
s=s.replace('replaceAll("\\s+"," ")','replaceAll("\\\\s+"," ")')

lines=s.splitlines()
out=[]
i=0
while i < len(lines):
    line=lines[i]
    if 'java.util.regex.Pattern header=java.util.regex.Pattern.compile(' in line:
        out.append('    java.util.regex.Pattern header=java.util.regex.Pattern.compile("^\\\\s*(?:\\\\d+[.)]\\\\s*)?/([A-Za-z0-9_-]+)(?:\\\\s*(?:→|->|—|–|:|\\\\\\\\||=)\\\\s*(.*))?\\\\s*$");')
        i+=1
        continue
    if '}else if(currentName!=null){if(body.length()>0)body.append("' in line:
        # Historical source contains a literal newline inside a Java string,
        # split over this line and the next line.
        out.append("      }else if(currentName!=null){if(body.length()>0)body.append('\\n');body.append(line);}")
        if i+1 < len(lines) and '");body.append(line);}' in lines[i+1]:
            i+=2
        else:
            i+=1
        continue
    out.append(line)
    i+=1

s='\n'.join(out)+'\n'
p.write_text(s,encoding='utf-8')
print('Legacy Java escape repair applied')
