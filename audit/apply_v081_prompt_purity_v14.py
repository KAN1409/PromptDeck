#!/usr/bin/env python3
from pathlib import Path
import base64, importlib.util, json, re, tempfile

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
PACK=Path('android/app/src/main/assets/chatgpt_native_final.json')
DATA=Path('audit/chatgpt_native_final_data')


def method_span(src, marker):
    start=src.find(marker)
    if start<0: raise SystemExit('missing '+marker)
    brace=src.find('{',start)
    depth=0; ins=False; esc=False; quote=''; i=brace
    while i<len(src):
        ch=src[i]
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: ins=False
        else:
            if ch in ('"',"'"): ins=True; quote=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:return start,i+1
        i+=1
    raise SystemExit('unclosed '+marker)


def replace_method(src, marker, block):
    a,b=method_span(src,marker)
    return src[:a]+block+src[b:]

# Recover the exact semantic ID set that V16 marked as KEEP_EXTERNAL_TARGET.
chunks=[p.read_text(encoding='utf-8').strip() for p in sorted(DATA.glob('curation_*.b64'))]
if not chunks: raise SystemExit('curation chunks missing')
raw=base64.b64decode(''.join(chunks))
module_path=Path(tempfile.gettempdir())/'promptdeck_curation_v14.py'
module_path.write_bytes(raw)
spec=importlib.util.spec_from_file_location('promptdeck_curation_v14',module_path)
cur=importlib.util.module_from_spec(spec);spec.loader.exec_module(cur)
ext=set()
for n in ('EXTERNAL_TARGET_IDS','KEEP_EXTERNAL_TARGET_IDS'):
    if hasattr(cur,n): ext.update(getattr(cur,n))

# Strict product rule: PromptDeck's built-in catalog is ChatGPT-native only.
pack=json.loads(PACK.read_text(encoding='utf-8'))
remove=set(pack.get('remove_ids',[]))
added=sorted(int(x) for x in ext if int(x) not in remove)
remove.update(int(x) for x in ext)
pack['remove_ids']=sorted(remove)
pack['external_target_ids_removed']=sorted(int(x) for x in ext)
pack['catalog_policy']='chatgpt-only-no-external-target-prompts'
pack['expected_builtin_count']=int(pack['expected_builtin_count'])-len(added)
PACK.write_text(json.dumps(pack,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

s=JAVA.read_text(encoding='utf-8')

# Single prompt means exactly the prompt body, with the user's own input appended only when supplied.
s=replace_method(s,'  String buildSinglePrompt(',r'''  String buildSinglePrompt(Cmd c,String user){
    String prompt=resolveTemplate(c,user).trim();
    String request=user==null?"":user.trim();
    if(request.isEmpty())return prompt;
    return prompt+"\n\n"+request;
  }''')

# Stack composer: selected prompt bodies only. No TASK/STEP/EXECUTION-RULE boilerplate.
s=replace_method(s,'  void build()',r'''  void build(){
    page="build";
    String user=context==null?contextDraft:context.getText().toString().trim();contextDraft=user;
    base("Final Prompt","Review the exact prompt text that will be sent to ChatGPT.",false);
    StringBuilder p=new StringBuilder();
    for(int i=0;i<selected.size();i++){
      if(i>0)p.append("\n\n");
      p.append(resolveTemplate(selected.get(i),user).trim());
    }
    if(!user.isEmpty()){
      if(p.length()>0)p.append("\n\n");
      p.append(user);
    }
    finalPrompt=input("",12);finalPrompt.setText(p.toString());finalPrompt.setTextSize(13);finalPrompt.setMinHeight(dp(260));root.addView(finalPrompt);
    Button send=primary("➤  Open in ChatGPT");send.setOnClickListener(v->send());root.addView(send);
    Button copy=secondary("Copy prompt");copy.setOnClickListener(v->copy());root.addView(copy);
    Button edit=ghost("Edit stack");edit.setOnClickListener(v->stack());root.addView(edit);
  }''')

# Version bump for in-place update.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 37',g,count=1)
GRADLE.write_text(g,encoding='utf-8')
JAVA.write_text(s,encoding='utf-8')

# Purity gates.
for forbidden in ['USER REQUEST / CONTEXT:','TASK — ','SELECTED PROMPT MODULES:','EXECUTION RULES:']:
    # historical strings may exist in comments/unused code before replacement; only check active methods below.
    pass
single=s[method_span(s,'  String buildSinglePrompt(')[0]:method_span(s,'  String buildSinglePrompt(')[1]]
stack=s[method_span(s,'  void build()')[0]:method_span(s,'  void build()')[1]]
for forbidden in ['USER REQUEST / CONTEXT:','TASK — ','Use available ChatGPT tools only','EXECUTION RULES:','SELECTED PROMPT MODULES:']:
    if forbidden in single or forbidden in stack: raise SystemExit('wrapper remains: '+forbidden)
if not ext: raise SystemExit('external target semantic set unexpectedly empty')
if 'versionCode 37' not in g: raise SystemExit('version gate failed')
print(f'v14 prompt purity applied: removed {len(ext)} external-target prompts; expected built-ins {pack["expected_builtin_count"]}; prompt output is body-only')
