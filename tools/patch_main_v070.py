#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Add request code for full Prompt Library.
s=s.replace('static final int IMPORT_REQ=1001, EXPORT_REQ=1002;','static final int IMPORT_REQ=1001, EXPORT_REQ=1002, LIBRARY_PICK_REQ=1003;',1)

# Replace the remaining Arabic helper copy exactly.
old='''  String useWhen(Cmd c){String n=c.command;if(has(n,"compare,proscons,rank,recommend,decision"))return"عندك أكتر من اختيار وعاوز تفهم الفرق أو توصل لقرار.";if(has(n,"research,verify,sources,evidence,facts"))return"محتاج معلومة موثوقة أو عاوز تتأكد من ادعاء قبل ما تعتمد عليه.";if(has(n,"rewrite,rephrase,polish,proofread,grammar,humanize"))return"عندك نص موجود وعاوز تطلعه بشكل أحسن بدل ما تبدأ من الصفر.";if(has(n,"brainstorm,ideas,angles,alternative"))return"محتاج توسع مساحة الاختيارات وتطلع أفكار أو اتجاهات جديدة.";if(has(n,"debug,rootcause,fix,check,tests"))return"في مشكلة أو نتيجة غلط وعاوز تشخص السبب وتوصل لإصلاح قابل للاختبار.";if(has(n,"plan,strategy,roadmap,action,priority"))return"عندك هدف وعاوز تحوله لترتيب عملي واضح بدل كلام عام.";return"لما تكون محتاج الوظيفة دي كخطوة واضحة داخل طلب أكبر.";}
  String example(Cmd c){return"طبّق الأمر ده على الموضوع أو النص اللي هبعته، واديني نتيجة واضحة وعملية.";}'''
new='''  String useWhen(Cmd c){String n=c.command;if(has(n,"compare,proscons,rank,recommend,decision"))return"When you have multiple options and want to understand the differences or make a better decision.";if(has(n,"research,verify,sources,evidence,facts"))return"When you need reliable information or want to verify a claim before relying on it.";if(has(n,"rewrite,rephrase,polish,proofread,grammar,humanize"))return"When you already have text and want to improve how it reads without starting from scratch.";if(has(n,"brainstorm,ideas,angles,alternative"))return"When you want more options, fresh ideas, or different directions to explore.";if(has(n,"debug,rootcause,fix,check,tests"))return"When something is wrong and you want to diagnose the cause and reach a testable fix.";if(has(n,"plan,strategy,roadmap,action,priority"))return"When you have a goal and want to turn it into a clear, practical sequence of actions.";return"When you want this capability as a focused step inside a larger request.";}
  String example(Cmd c){return"Apply /"+c.command+" to the request or material I provide and give me a clear, useful result.";}'''
if old not in s: print('warning: old useWhen/example block not found')
else: s=s.replace(old,new,1)

# English-only custom library subtitle.
s=s.replace('View library=menuCard("＋","My Prompt Library","أضف أو استورد أو صدّر prompts خاصة بيك");',
'''View fullLibrary=menuCard("⌕","Prompt Library","Browse 2,160 full prompts by category or search");fullLibrary.setOnClickListener(v->startActivityForResult(new Intent(this,PromptLibraryActivity.class),LIBRARY_PICK_REQ));root.addView(fullLibrary);spacer(8);View library=menuCard("＋","My Prompt Library","Add, import or export your own prompts");''',1)

# Add a safe result handler for Prompt Library before document URI handling.
old_result='''  @Override protected void onActivityResult(int r,int result,Intent data){super.onActivityResult(r,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}}'''
new_result='''  @Override protected void onActivityResult(int r,int result,Intent data){
    super.onActivityResult(r,result,data);
    if(r==LIBRARY_PICK_REQ){
      if(result!=RESULT_OK||data==null)return;
      String title=data.getStringExtra("library_title"), inst=data.getStringExtra("library_prompt"), cat=data.getStringExtra("library_category");
      if(title==null||inst==null||inst.trim().isEmpty())return;
      try{
        String slug=title.replaceAll("[^A-Za-z0-9]+","");if(slug.isEmpty())slug="LibraryPrompt";if(slug.length()>30)slug=slug.substring(0,30);
        String baseSlug=slug;int n=2;while(find(slug)!=null)slug=baseSlug+(n++);
        JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",slug);o.put("category","Prompt Library"+(cat==null||cat.isEmpty()?"":" • "+cat));o.put("description",title);o.put("instruction",inst);Cmd c=new Cmd(o,false);all.add(c);selected.add(c);toast("Added "+title);stack();
      }catch(Exception e){toast("Could not add library prompt");}
      return;
    }
    if(result!=RESULT_OK||data==null||data.getData()==null)return;
    try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}
  }'''
if old_result not in s: print('warning: onActivityResult block not found')
else: s=s.replace(old_result,new_result,1)

# Visible app Java must be English-only. Allow the literal word "arabic" command, but no Arabic script.
if re.search(r'[\u0600-\u06FF]',s):
    hits=[]
    for i,line in enumerate(s.splitlines(),1):
        if re.search(r'[\u0600-\u06FF]',line):hits.append(f'{i}: {line[:180]}')
    raise SystemExit('Arabic UI text remains in MainActivity:\n'+'\n'.join(hits[:30]))

p.write_text(s,encoding='utf-8')
print('PromptDeck v0.7.0 MainActivity patch applied')
