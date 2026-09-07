#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
s=JAVA.read_text(encoding='utf-8')

def method_span(src, marker):
    st=src.find(marker)
    if st<0: raise SystemExit('missing '+marker)
    brace=src.find('{',st);depth=0;ins=False;esc=False;q='';i=brace
    while i<len(src):
        ch=src[i]
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==q: ins=False
        else:
            if ch in ('"',"'"): ins=True;q=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:return st,i+1
        i+=1
    raise SystemExit('unclosed '+marker)

def replace_method(src, marker, block):
    a,b=method_span(src,marker);return src[:a]+block+src[b:]

def insert_before(src, marker, block):
    p=src.find(marker)
    if p<0: raise SystemExit('missing anchor '+marker)
    return src[:p]+block+src[p:]

# Preserve the proven v14 loading pipeline, but run it off the UI thread and do one
# deterministic, linear-time cleanup pass afterwards.
a,b=method_span(s,'  void load()')
old=s[a:b]
legacy=old.replace('  void load()','  void loadLegacyV15()',1)
s=s[:a]+legacy+s[b:]

helpers=r'''  void load(){
    loadLegacyV15();
    finalCatalogCleanupV15();
  }
  boolean containsAnyV15(String x,String... terms){
    if(x==null)return false;String z=x.toLowerCase(Locale.ROOT);
    for(String t:terms)if(z.contains(t))return true;
    return false;
  }
  boolean externalModelCommandV15(Cmd c){
    String x=(c.command==null?"":c.command)+" "+(c.description==null?"":c.description);
    return containsAnyV15(x,"midjourney","claude","anthropic","gemini","grok","deepseek","mistral","copilot","perplexity");
  }
  boolean externalRuntimePromptV15(Cmd c){
    String x=c.instruction==null?"":c.instruction.toLowerCase(Locale.ROOT);
    String[] models={"midjourney","claude","anthropic","gemini","grok","deepseek","mistral","copilot","perplexity"};
    String[] verbs={"use ","invoke ","run ","open ","send to ","format for ","optimized for ","prompt for "};
    for(String model:models)for(String verb:verbs)if(x.contains(verb+model)||x.contains(verb+"the "+model))return true;
    return x.contains("claude.md")||x.contains("skill.md")||x.contains("gemini cli")||x.contains("anthropic console");
  }
  String cleanPromptBodyV15(String x){
    if(x==null)return "";String y=x.trim();
    String prefix="For this step in a larger workflow:";
    if(y.regionMatches(true,0,prefix,0,prefix.length()))y=y.substring(prefix.length()).trim();
    String suffix="Apply these instructions only to this step. Do not override or block later steps in the PromptDeck stack.";
    int si=y.toLowerCase(Locale.ROOT).lastIndexOf(suffix.toLowerCase(Locale.ROOT));
    if(si>=0&&y.substring(si).trim().equalsIgnoreCase(suffix))y=y.substring(0,si).trim();
    StringBuilder out=new StringBuilder(y.length());int p=0;
    while(p<=y.length()){
      int n=y.indexOf('\n',p);if(n<0)n=y.length();String line=y.substring(p,n);String low=line.trim().toLowerCase(Locale.ROOT);
      if(!(low.startsWith("name:")||low.startsWith("version:")||low.startsWith("author:")||low.startsWith("changelog:"))){
        if(out.length()>0)out.append('\n');out.append(line);
      }
      if(n==y.length())break;p=n+1;
    }
    return out.toString().trim();
  }
  String dedupKeyV15(String x){
    if(x==null)return "";StringBuilder b=new StringBuilder(Math.min(x.length(),4096));boolean gap=false;
    for(int i=0;i<x.length();i++){
      char ch=Character.toLowerCase(x.charAt(i));
      if(Character.isLetterOrDigit(ch)){if(gap&&b.length()>0)b.append(' ');b.append(ch);gap=false;}
      else gap=true;
    }
    return b.toString();
  }
  void finalCatalogCleanupV15(){
    HashSet<String> seen=new HashSet<>();Iterator<Cmd> it=all.iterator();
    while(it.hasNext()){
      Cmd c=it.next();if(c.custom)continue;
      if(externalModelCommandV15(c)||externalRuntimePromptV15(c)){it.remove();continue;}
      c.instruction=cleanPromptBodyV15(c.instruction);
      if(c.instruction.length()<8){it.remove();continue;}
      String k=dedupKeyV15(c.instruction);if(!seen.add(k))it.remove();
    }
  }
  void showStartupV15(){
    LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setBackgroundColor(BG);box.setPadding(dp(28),dp(28),dp(28),dp(28));
    TextView brand=text("PromptDeck",28,true,TEXT);brand.setGravity(Gravity.CENTER);box.addView(brand);
    TextView sub=text("Loading your prompt library…",13,false,MUTED);sub.setGravity(Gravity.CENTER);sub.setPadding(0,dp(12),0,0);box.addView(sub);setContentView(box);
  }
  void restoreWorkspaceV15(Bundle b){
    if(b==null)return;
    discoverMode=b.getString("v15_mode",discoverMode);askGoal=b.getString("v15_goal",askGoal);askCapability=b.getString("v15_cap",askCapability);contextDraft=b.getString("v15_context",contextDraft);
    discoverCategory=b.getString("v15_cat",discoverCategory);discoverSubcategory=b.getString("v15_sub",discoverSubcategory);discoverFavorites=b.getBoolean("v15_fav",discoverFavorites);browseLimit=b.getInt("v15_limit",browseLimit);
    ArrayList<Integer> ids=b.getIntegerArrayList("v15_selected");if(ids!=null){selected.clear();for(Integer id:ids){for(Cmd c:all)if(c.id==id){selected.add(c);break;}}}
  }
  void consumeIncomingShareV15(){
    Intent in=getIntent();if(in==null||!Intent.ACTION_SEND.equals(in.getAction())||!"text/plain".equals(in.getType()))return;
    String t=in.getStringExtra(Intent.EXTRA_TEXT);if(t==null||t.trim().isEmpty())return;
    contextDraft=t.trim();askGoal=contextDraft;discoverMode="ask";
  }
'''
s=insert_before(s,'  void loadCommunityPrompts(){',helpers)

# Keep the Activity immediately responsive. Catalog I/O/JSON/curation never runs on main.
s=replace_method(s,'  @Override public void onCreate(Bundle b)',r'''  @Override public void onCreate(Bundle b){
    super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(0);showStartupV15();
    final Bundle saved=b;
    new Thread(()->{try{load();runOnUiThread(()->{restoreWorkspaceV15(saved);consumeIncomingShareV15();home();});}catch(Throwable e){runOnUiThread(()->{LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setBackgroundColor(BG);box.setPadding(dp(24),dp(24),dp(24),dp(24));box.addView(text("PromptDeck could not load the prompt library.",16,true,TEXT));box.addView(text(e.getMessage()==null?e.getClass().getSimpleName():e.getMessage(),12,false,MUTED));setContentView(box);});}},"PromptDeckCatalog").start();
  }''')

state_method=r'''  @Override protected void onSaveInstanceState(Bundle out){
    super.onSaveInstanceState(out);out.putString("v15_mode",discoverMode);out.putString("v15_goal",askGoal);out.putString("v15_cap",askCapability);out.putString("v15_context",contextDraft);out.putString("v15_cat",discoverCategory);out.putString("v15_sub",discoverSubcategory);out.putBoolean("v15_fav",discoverFavorites);out.putInt("v15_limit",browseLimit);ArrayList<Integer> ids=new ArrayList<>();for(Cmd c:selected)ids.add(c.id);out.putIntegerArrayList("v15_selected",ids);
  }

'''
if 'onSaveInstanceState(Bundle out)' not in s:s=insert_before(s,'  @Override public void onBackPressed()',state_method)

g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 38',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.2-rc1'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')
JAVA.write_text(s,encoding='utf-8')

for token in ['PromptDeckCatalog','finalCatalogCleanupV15','dedupKeyV15','consumeIncomingShareV15','onSaveInstanceState(Bundle out)','versionCode 38',"versionName '0.8.2-rc1'"]:
    hay=s if token not in ['versionCode 38',"versionName '0.8.2-rc1'"] else g
    if token not in hay: raise SystemExit('v15 gate missing '+token)
if '.matches(' in s[s.find('boolean externalModelCommandV15'):s.find('void showStartupV15')]:raise SystemExit('regex remains in v15 cleanup hot path')
print('v15 applied: async startup + linear-time ChatGPT-only cleanup + share/state restoration')
