#!/usr/bin/env python3
import json,re,math,os
from pathlib import Path
from collections import Counter,defaultdict

ASSETS=Path('android/app/src/main/assets')
SOURCES=[
 ('core','commands.json'),
 ('community','prompts_library.json'),
 ('pdf','imported_pdf_prompts.json'),
 ('photo','curated_photo_prompts.json'),
 ('deep_hunt','daily_gap_prompts_100.json'),
]

def norm(s):
    s=(s or '').lower()
    s=re.sub(r'https?://\S+',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def words(s): return set(norm(s).split())

def load_items():
    out=[]
    for source,fn in SOURCES:
        p=ASSETS/fn
        if not p.exists(): continue
        data=json.load(open(p,encoding='utf-8'))
        for i,x in enumerate(data):
            title=x.get('command') or x.get('title') or f'{source}_{i}'
            prompt=x.get('instruction') or x.get('prompt') or ''
            desc=x.get('description') or ''
            cat=x.get('category') or 'Uncategorized'
            sub=x.get('subcategory') or ''
            if not prompt.strip(): continue
            out.append({'source':source,'title':title,'prompt':prompt,'description':desc,'category':cat,'subcategory':sub})
    return out

def quality(x):
    p=x['prompt']; n=len(p.split()); s=0.0
    # Prefer prompts that are specific, bounded, and reusable rather than merely verbose.
    s += min(n,180)/180*3.0
    s += 0.45*sum(k in p.lower() for k in ['preserve','avoid','include','compare','identify','prioritize','explain','return','do not','if ','before ','after ','rank ','distinguish'])
    s += 0.7 if any(ch in p for ch in ':;—') else 0
    s += 0.8 if 18 <= n <= 160 else 0
    s -= 0.7 if n > 300 else 0
    s -= 0.7 if 'act as' in p.lower() and n < 60 else 0
    s += {'deep_hunt':1.4,'core':1.0,'photo':0.9,'pdf':0.4,'community':0.2}.get(x['source'],0)
    return round(s,3)

def compatible(a,b):
    if a['category']==b['category']: return True
    # allow cross-category duplicates among generic text/reasoning utility prompts
    generic={'Writing & Rewriting','Thinking & Ideas','Research & Analysis','Planning & Execution','Learning & Study','AI & Prompting','Data & Formatting','Specialist Roles'}
    return a['category'] in generic and b['category'] in generic

def main():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    items=load_items(); n=len(items)
    texts=[]
    for x in items:
        texts.append(' '.join([x['title']]*3+[x['description']]*2+[x['prompt']]))
    vec=TfidfVectorizer(lowercase=True,stop_words='english',ngram_range=(1,2),min_df=1,max_df=.97,sublinear_tf=True,max_features=60000)
    X=vec.fit_transform(texts)
    nn=NearestNeighbors(metric='cosine',algorithm='brute',n_neighbors=min(16,n)).fit(X)
    dists,inds=nn.kneighbors(X)
    parent=list(range(n))
    def find(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]]; a=parent[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[b]=a
    exact=defaultdict(list)
    for i,x in enumerate(items): exact[norm(x['prompt'])].append(i)
    exact_groups=[v for v in exact.values() if len(v)>1]
    for g in exact_groups:
        for j in g[1:]: union(g[0],j)
    strong_pairs=[]; possible_pairs=[]
    for i in range(n):
        for d,j in zip(dists[i][1:],inds[i][1:]):
            if j<=i: continue
            sim=1-float(d)
            if not compatible(items[i],items[j]): continue
            # lexical overlap guards against false semantic joins from boilerplate
            A,B=words(items[i]['title']+' '+items[i]['description']),words(items[j]['title']+' '+items[j]['description'])
            jac=len(A&B)/max(1,len(A|B))
            if sim>=0.91 or (sim>=0.86 and jac>=0.18):
                union(i,j); strong_pairs.append((i,j,sim,jac))
            elif sim>=0.80 and jac>=0.12:
                possible_pairs.append((i,j,sim,jac))
    comps=defaultdict(list)
    for i in range(n): comps[find(i)].append(i)
    clusters=[g for g in comps.values() if len(g)>1]
    clusters.sort(key=lambda g:(-len(g),-max(quality(items[i]) for i in g)))
    canonical=[]
    for g in clusters:
        winner=max(g,key=lambda i:quality(items[i]))
        canonical.append((g,winner))
    estimated=n-sum(len(g)-1 for g,_ in canonical)
    cats=Counter(x['category'] for x in items); srcs=Counter(x['source'] for x in items)
    report=[]
    report += ['# PromptDeck Semantic Catalog Audit','',f'- Raw prompt entries: **{n}**',f'- Exact duplicate groups: **{len(exact_groups)}**',f'- High-confidence semantic duplicate families: **{len(clusters)}**',f'- Entries removable by canonical-family merge: **{n-estimated}**',f'- Estimated canonical prompt count after conservative merge: **{estimated}**','']
    report += ['## Source counts','']+[f'- {k}: {v}' for k,v in srcs.most_common()]+['','## Category counts','']+[f'- {k}: {v}' for k,v in cats.most_common()]+['']
    report += ['## Largest high-confidence families','']
    for rank,(g,w) in enumerate(canonical[:120],1):
        win=items[w]
        report += [f'### {rank}. Canonical: /{win["title"]}  ({len(g)} → 1)',f'Winner: **{win["source"]} / {win["category"]} / {win["subcategory"]}** · quality {quality(win)}','Members:']
        for i in sorted(g,key=lambda i:-quality(items[i]))[:15]:
            x=items[i]; report.append(f'- /{x["title"]} — {x["source"]} — {x["category"]} — q={quality(x)}')
        if len(g)>15: report.append(f'- … +{len(g)-15} more')
        report.append('')
    report += ['## Possible overlaps for human review','']
    for i,j,sim,jac in sorted(possible_pairs,key=lambda t:-t[2])[:250]:
        a,b=items[i],items[j]
        report.append(f'- **/{a["title"]}** ({a["source"]}) ↔ **/{b["title"]}** ({b["source"]}) — cosine {sim:.3f}, label overlap {jac:.3f}')
    out={'raw_count':n,'estimated_canonical_count':estimated,'removable_count':n-estimated,'exact_duplicate_groups':len(exact_groups),'semantic_families':len(clusters),'source_counts':srcs,'category_counts':cats,'families':[]}
    for g,w in canonical:
        out['families'].append({'canonical':items[w],'members':[items[i] for i in g],'size':len(g)})
    Path('audit').mkdir(exist_ok=True)
    Path('audit/PROMPT_CATALOG_AUDIT.md').write_text('\n'.join(report),encoding='utf-8')
    Path('audit/PROMPT_CATALOG_AUDIT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['raw_count','estimated_canonical_count','removable_count','exact_duplicate_groups','semantic_families']},indent=2))

if __name__=='__main__': main()
