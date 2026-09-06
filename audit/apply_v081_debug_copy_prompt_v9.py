#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')


def method_span(s, marker):
    start=s.find(marker)
    if start<0: raise SystemExit('method marker missing: '+marker)
    brace=s.find('{',start)
    if brace<0: raise SystemExit('opening brace missing: '+marker)
    depth=0;i=brace;ins=False;esc=False;q=''
    while i<len(s):
        ch=s[i]
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==q: ins=False
        else:
            if ch in ('"',"'"): ins=True;q=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:return start,i+1
        i+=1
    raise SystemExit('unclosed '+marker)


def replace_method(s,marker,block):
    a,b=method_span(s,marker);return s[:a]+block+s[b:]


def insert_before(s,marker,block):
    p=s.find(marker)
    if p<0: raise SystemExit('anchor missing: '+marker)
    return s[:p]+block+s[p:]

s=JAVA.read_text(encoding='utf-8')
if 'void showStackSheet()' not in s: raise SystemExit('Review & Run sheet missing')
if 'resolveTemplate(Cmd c,String user)' not in s: raise SystemExit('ChatGPT-native template resolver missing')

helpers=r'''  String composeStackPromptV9(String user){
    String u=user==null?"":user.trim();StringBuilder p=new StringBuilder();p.append("Use the user's request/context as the source of truth.\n\n");if(!u.isEmpty())p.append("USER REQUEST / CONTEXT:\n").append(u).append("\n\n");p.append("SELECTED PROMPT MODULES:\n");for(int i=0;i<selected.size();i++){Cmd c=selected.get(i);p.append("\nSTEP ").append(i+1).append(" — ").append(presentationTitleV8(c)).append("\n");p.append(resolveTemplate(c,u)).append("\n");}p.append("\nEXECUTION RULES:\n- Apply the selected modules in order, carrying forward only useful findings from earlier steps.\n- Each module is scoped to its step and must not override or block later modules.\n- Use tools or external capabilities only when they are actually available in the current ChatGPT conversation.\n- If one essential input is missing and cannot reasonably be inferred, ask one concise clarifying question; otherwise make a reasonable assumption and state it when important.\n- Produce one clear, coherent final answer rather than separate disconnected answers for each module.\n- Show useful conclusions, evidence and verification where relevant, but do not expose private chain-of-thought.\n");return p.toString();
  }
  void copyPromptTextV9(String value){android.content.ClipboardManager cb=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(cb==null){toast("Clipboard unavailable");return;}cb.setPrimaryClip(ClipData.newPlainText("PromptDeck prompt",value==null?"":value));toast("Prompt copied");}

'''
if 'String composeStackPromptV9(' not in s:
    s=insert_before(s,'  void showStackSheetMenu(',helpers)

# Make Final Prompt use the exact same composer as Review & Run copy.
s=replace_method(s,'  void build()',r'''  void build(){
    page="build";String user=context==null?contextDraft:context.getText().toString().trim();contextDraft=user;base("Final Prompt","Review the composed ChatGPT-ready request.",false);String composed=composeStackPromptV9(user);finalPrompt=input("",12);finalPrompt.setText(composed);finalPrompt.setTextSize(13);finalPrompt.setMinHeight(dp(260));root.addView(finalPrompt);Button send=primary("➤  Open in ChatGPT");send.setOnClickListener(v->send());root.addView(send);Button copy=secondary("Copy prompt");copy.setOnClickListener(v->copyPromptTextV9(finalPrompt.getText().toString()));root.addView(copy);Button edit=ghost("Edit stack");edit.setOnClickListener(v->stack());root.addView(edit);
  }''')

# Patch only the action area of the final post-v8 Review & Run method.
a,b=method_span(s,'  void showStackSheet()')
block=s[a:b]
needle='outer.addView(req);LinearLayout actions=hbox();Button add=secondary("Add prompt");'
if needle not in block:
    raise SystemExit('Review & Run action anchor missing')
replacement='outer.addView(req);Button copyPrompt=secondary("Copy prompt");copyPrompt.setOnClickListener(v->{contextDraft=req.getText().toString();copyPromptTextV9(composeStackPromptV9(contextDraft));});outer.addView(copyPrompt);LinearLayout actions=hbox();Button add=secondary("Add prompt");'
block=block.replace(needle,replacement,1)
s=s[:a]+block+s[b:]

# Keep the legacy copy helper consistent too.
s=replace_method(s,'  void copy()',r'''  void copy(){if(finalPrompt==null)return;copyPromptTextV9(finalPrompt.getText().toString());}''')

g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 32',g,count=1)
GRADLE.write_text(g,encoding='utf-8')

for token in ['String composeStackPromptV9(String user)','void copyPromptTextV9(String value)','Button copyPrompt=secondary("Copy prompt")','copyPromptTextV9(composeStackPromptV9(contextDraft))','versionCode 32']:
    hay=s if token!='versionCode 32' else g
    if token not in hay:raise SystemExit('v9 copy-prompt gate missing: '+token)

JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v9 debug copy applied: Review & Run copies the exact composed prompt')
