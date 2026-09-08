#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
s=JAVA.read_text(encoding='utf-8')

def method_span(src,marker):
    st=src.find(marker)
    if st<0:raise SystemExit('missing '+marker)
    b=src.find('{',st);d=0;ins=False;esc=False;q='';i=b
    while i<len(src):
        ch=src[i]
        if ins:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:ins=False
        else:
            if ch in ('"',"'"):ins=True;q=ch
            elif ch=='{':d+=1
            elif ch=='}':
                d-=1
                if d==0:return st,i+1
        i+=1
    raise SystemExit('unclosed '+marker)
def repl(src,marker,block):
    a,b=method_span(src,marker);return src[:a]+block+src[b:]

anchor='final ArrayList<Cmd> all=new ArrayList<>(), selected=new ArrayList<>();'
if 'BUILTIN_CACHE_V15' not in s:
    if anchor not in s:raise SystemExit('catalog field anchor missing')
    s=s.replace(anchor,anchor+'\n  static final ArrayList<Cmd> BUILTIN_CACHE_V15=new ArrayList<>(); static volatile boolean BUILTIN_CACHE_READY_V15=false;',1)

s=repl(s,'  void load()',r'''  void load(){
    all.clear();
    try{
      synchronized(BUILTIN_CACHE_V15){
        if(!BUILTIN_CACHE_READY_V15){
          JSONArray a=new JSONArray(readAsset("final_catalog_v15.json"));
          BUILTIN_CACHE_V15.clear();
          for(int i=0;i<a.length();i++)BUILTIN_CACHE_V15.add(new Cmd(a.getJSONObject(i),false));
          BUILTIN_CACHE_READY_V15=true;
        }
        all.addAll(BUILTIN_CACHE_V15);
      }
      JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));
      for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}
    }catch(Exception e){throw new RuntimeException(e);}
  }''')

s=repl(s,'  @Override public void onCreate(Bundle b)',r'''  @Override public void onCreate(Bundle b){
    super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(0);
    final Bundle saved=b;
    if(BUILTIN_CACHE_READY_V15){
      try{load();restoreWorkspaceV15(saved);consumeIncomingShareV15();home();return;}catch(Throwable ignored){}
    }
    showStartupV15();
    new Thread(()->{try{load();runOnUiThread(()->{restoreWorkspaceV15(saved);consumeIncomingShareV15();home();});}catch(Throwable e){runOnUiThread(()->{LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setBackgroundColor(BG);box.setPadding(dp(24),dp(24),dp(24),dp(24));box.addView(text("PromptDeck could not load the prompt library.",16,true,TEXT));box.addView(text(e.getMessage()==null?e.getClass().getSimpleName():e.getMessage(),12,false,MUTED));setContentView(box);});}},"PromptDeckCatalog").start();
  }''')

# Format count for humans while keeping it dynamic.
s=s.replace('"Search and explore the complete "+all.size()+"-prompt library yourself."','"Search and explore the complete "+String.format(Locale.US,"%,d",all.size())+"-prompt library yourself."',1)

g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.2-rc4'",g,count=1)
JAVA.write_text(s,encoding='utf-8');GRADLE.write_text(g,encoding='utf-8')
for token in ['BUILTIN_CACHE_READY_V15','all.addAll(BUILTIN_CACHE_V15)','if(BUILTIN_CACHE_READY_V15)','String.format(Locale.US,"%,d",all.size())',"versionName '0.8.2-rc4'"]:
    hay=s if not token.startswith('versionName') else g
    if token not in hay:raise SystemExit('v15d gate missing '+token)
print('v15d: cached prebuilt catalog + instant recreation + formatted count')
