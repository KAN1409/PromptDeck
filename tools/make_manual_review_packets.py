#!/usr/bin/env python3
import json, math, re
from pathlib import Path
from collections import defaultdict

ASSETS=Path('android/app/src/main/assets')
OUT=Path('audit/manual_review_packets')
SOURCES=[('core','commands.json'),('community','prompts_library.json'),('pdf','imported_pdf_prompts.json'),('photo','curated_photo_prompts.json'),('deep_hunt','daily_gap_prompts_100.json')]
CATMAP={'Writing & Language':'Writing & Rewriting','Writing':'Writing & Rewriting','Transform':'Writing & Rewriting','Format':'Data & Formatting','Research':'Research & Analysis','Analysis':'Research & Analysis','Reasoning':'Thinking & Ideas','Decision':'Thinking & Ideas','Ideation':'Thinking & Ideas','Planning':'Planning & Execution','Study':'Learning & Study','Learning & Education':'Learning & Study','Explain':'Learning & Study','Work':'Work & Career','Career':'Work & Career','Creative & Content':'Content Creation','Content':'Content Creation','Technology & Development':'Problem Solving & Technical','Technical':'Problem Solving & Technical','Coding':'Problem Solving & Technical','Quality':'Problem Solving & Technical','Evaluation':'Problem Solving & Technical','Tools & Simulations':'Data & Formatting','Data':'Data & Formatting','Other Expert Roles':'Specialist Roles'}
def cat(c): return CATMAP.get(c,c or 'Specialist Roles')

def load():
    out=[]; gid=1
    for src,fn in SOURCES:
        p=ASSETS/fn
        if not p.exists(): continue
        for x in json.load(open(p,encoding='utf-8')):
            title=x.get('command') or x.get('title') or 'Untitled'
            prompt=x.get('instruction') or x.get('prompt') or ''
            if not prompt.strip(): continue
            desc=x.get('description') or ''
            out.append({'gid':gid,'source':src,'title':title,'category':cat(x.get('category')),'subcategory':x.get('subcategory') or '', 'description':desc.strip(), 'prompt':prompt.strip()})
            gid+=1
    return out

def clean(s): return re.sub(r'\s+',' ',s).strip()

def main():
    items=load(); OUT.mkdir(parents=True,exist_ok=True)
    bycat=defaultdict(list)
    for x in items: bycat[x['category']].append(x)
    manifest=[]
    for category in sorted(bycat):
        xs=bycat[category]
        # stable source/title ordering makes cross-comparison easier
        xs.sort(key=lambda x:(x['subcategory'].lower(),x['title'].lower(),x['source'],x['gid']))
        packet_size=75
        safe=re.sub(r'[^a-z0-9]+','_',category.lower()).strip('_')
        for idx in range(0,len(xs),packet_size):
            chunk=xs[idx:idx+packet_size]
            fn=f'{safe}_{idx//packet_size+1:02d}.md'
            lines=[f'# Manual Review Packet — {category} — {idx//packet_size+1}', '', f'Entries: {len(chunk)}', '']
            for x in chunk:
                # Keep enough body to judge prompt engineering and usefulness; full source remains addressable by gid/title.
                preview=clean(x['prompt'])[:1800]
                desc=clean(x['description'])[:500]
                lines += [f"## GID {x['gid']} — /{x['title']}", f"Source: {x['source']} | Subcategory: {x['subcategory'] or '-'}", f"Description: {desc or '-'}", f"Prompt preview: {preview}", '']
            (OUT/fn).write_text('\n'.join(lines),encoding='utf-8')
            manifest.append({'file':fn,'category':category,'count':len(chunk),'first_gid':chunk[0]['gid'],'last_gid':chunk[-1]['gid']})
    (OUT/'manifest.json').write_text(json.dumps({'raw_count':len(items),'packets':manifest},indent=2),encoding='utf-8')
    print('raw_count',len(items),'packets',len(manifest))
if __name__=='__main__': main()
