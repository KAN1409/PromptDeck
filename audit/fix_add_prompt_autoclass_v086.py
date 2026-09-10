#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text()

# Landing semantics: Add a prompt, not Ask PromptDeck.
s=s.replace('View paste=modeChoiceCard(R.drawable.pd_ic_content,"Paste a prompt","Paste from your clipboard and let PromptDeck understand it automatically.",PURPLE,()->pastePromptFromClipboardV16());root.addView(paste);','View paste=modeChoiceCard(R.drawable.pd_ic_content,"Add a prompt","Paste a complete prompt and save it to your library automatically.",PURPLE,()->showBulkPaste());root.addView(paste);',1)
s=s.replace('Button pasteClipboard=secondary("Paste from clipboard");pasteClipboard.setOnClickListener(v->pastePromptFromClipboardV16());root.addView(pasteClipboard);','',1)
start=s.find('  void pastePromptFromClipboardV16(){')
end=s.find('\n\n  void home(){',start)
if start>=0 and end>start:
    s=s[:start]+s[end:]

# Replace old smart-paste dialog with an Add Prompt dialog that reads clipboard and auto-classifies.
new_method=r'''  void showBulkPaste(){
    LinearLayout box=vbox();box.setPadding(dp(18),dp(4),dp(18),0);
    EditText bulk=input("Paste your complete prompt here...",10);bulk.setMinLines(8);bulk.setGravity(Gravity.TOP|Gravity.START);
    try{android.content.ClipboardManager cb=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(cb!=null&&cb.hasPrimaryClip()&&cb.getPrimaryClip()!=null&&cb.getPrimaryClip().getItemCount()>0){CharSequence x=cb.getPrimaryClip().getItemAt(0).coerceToText(this);if(x!=null&&!x.toString().trim().isEmpty())bulk.setText(x.toString().trim());}}catch(Exception ignored){}
    box.addView(bulk);
    TextView note=text("PromptDeck will create the title, choose the category and subcategory, and save the prompt to your library.",12,false,MUTED);note.setPadding(0,dp(8),0,dp(8));box.addView(note);
    AlertDialog d=new AlertDialog.Builder(this).setTitle("Add a prompt").setView(box).setNegativeButton("Cancel",null).setPositiveButton("Add prompt",null).create();
    d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String raw=bulk.getText().toString().trim();if(raw.isEmpty()){toast("Paste a prompt first");return;}int[] result=parseBulkCommands(raw,"");if(result[0]==0){toast("Couldn't add this prompt");return;}saveCustom();d.dismiss();library();toast("Prompt added to your library");}));d.show();
  }

  String inferPromptCategoryV86(String prompt){
    String z=(prompt==null?"":prompt).toLowerCase(Locale.ROOT);
    if(hasAny(z,"image","photo","portrait","background","retouch","upscale","visual","poster","thumbnail","logo","graphic design","render"))return "Images & Design";
    if(hasAny(z,"health","medical","wellness","fitness","nutrition","diet","sleep","habit","relationship","lifestyle"))return "Health & Life";
    if(hasAny(z,"learn","study","teach","explain","quiz","tutor","lesson","exam","flashcard","education"))return "Learning & Education";
    if(hasAny(z,"code","coding","developer","software","debug","api","database","sql","android","python","javascript","data","dataset","spreadsheet","excel","csv","statistics","dashboard"))return "Technology & Data";
    if(hasAny(z,"business","career","resume","cv","interview","marketing","sales","customer","meeting","workplace","strategy","proposal"))return "Work & Business";
    if(hasAny(z,"plan","roadmap","schedule","checklist","prioritize","decision","compare options","recommend the best","trade-off","tradeoff"))return "Planning & Decisions";
    if(hasAny(z,"research","verify","evidence","sources","investigate","fact-check","fact check","analyze","analysis","compare sources"))return "Research & Analysis";
    if(hasAny(z,"brainstorm","creative","story","script","social media","content ideas","caption","campaign","concept"))return "Creativity & Content";
    return "Writing & Communication";
  }

  String inferPromptSubcategoryV86(String prompt,String category){
    String z=(prompt==null?"":prompt).toLowerCase(Locale.ROOT);
    if("Images & Design".equals(category)){if(hasAny(z,"edit","retouch","remove","background","restore","upscale"))return "Image Editing";if(hasAny(z,"logo","poster","graphic","layout","brand"))return "Graphic Design";return "Image Generation";}
    if("Technology & Data".equals(category)){if(hasAny(z,"data","dataset","spreadsheet","excel","csv","statistics","dashboard"))return "Data Analysis";if(hasAny(z,"debug","bug","error","fix"))return "Debugging";if(hasAny(z,"prompt engineering","ai workflow","agent"))return "AI & Prompting";return "Software Development";}
    if("Research & Analysis".equals(category)){if(hasAny(z,"verify","fact-check","fact check","sources","evidence"))return "Verification";if(hasAny(z,"compare"))return "Comparative Analysis";return "Research";}
    if("Planning & Decisions".equals(category)){if(hasAny(z,"decision","compare options","recommend","tradeoff","trade-off"))return "Decision Making";if(hasAny(z,"schedule","timeline"))return "Scheduling";return "Planning";}
    if("Work & Business".equals(category)){if(hasAny(z,"resume","cv","interview","career","job"))return "Career";if(hasAny(z,"marketing","sales","campaign"))return "Marketing & Sales";return "Business";}
    if("Learning & Education".equals(category)){if(hasAny(z,"quiz","exam","flashcard"))return "Study & Practice";return "Teaching & Explanation";}
    if("Creativity & Content".equals(category)){if(hasAny(z,"story","script"))return "Storytelling";if(hasAny(z,"social media","caption"))return "Social Content";return "Ideation";}
    if("Health & Life".equals(category)){if(hasAny(z,"fitness","workout"))return "Fitness";if(hasAny(z,"nutrition","diet"))return "Nutrition";return "Wellness & Life";}
    if(hasAny(z,"email","message","reply"))return "Email & Messaging";if(hasAny(z,"rewrite","edit","polish","proofread"))return "Rewriting & Editing";return "General Writing";
  }

  int[] parseBulkCommands'''
s,n=re.subn(r'  void showBulkPaste\(\)\{.*?\n  \}\n\n  int\[\] parseBulkCommands',new_method,s,count=1,flags=re.S)
if n!=1: raise SystemExit('showBulkPaste replacement failed')

# Make parsed prompts auto-classify when no category was supplied.
s=s.replace('if(blocks.isEmpty()){\n      String fullRaw=raw==null?"":raw.trim();\n      if(!fullRaw.isEmpty())blocks.add(new String[]{autoCommandName(fullRaw,category),"",fullRaw});\n    }','if(blocks.isEmpty()){\n      String fullRaw=raw==null?"":raw.trim();\n      if(!fullRaw.isEmpty())blocks.add(new String[]{autoCommandName(fullRaw,inferPromptCategoryV86(fullRaw)),"",fullRaw});\n    }',1)
s=s.replace('String base=name;int suffix=2;while(find(name)!=null)name=base+(suffix++);\n      String desc=!inline.isEmpty()&&!full.isEmpty()?inline:autoDescription(instruction,category);','String actualCategory=(category==null||category.trim().isEmpty())?inferPromptCategoryV86(instruction):category.trim();String actualSubcategory=inferPromptSubcategoryV86(instruction,actualCategory);\n      String base=name;int suffix=2;while(find(name)!=null)name=base+(suffix++);\n      String desc=!inline.isEmpty()&&!full.isEmpty()?inline:autoDescription(instruction,actualCategory);',1)
s=s.replace('o.put("id",nextId());o.put("command",name);o.put("category",category);\n        o.put("description",category.toLowerCase(Locale.ROOT).contains("photo")?photoDescription(desc):desc);','o.put("id",nextId());o.put("command",name);o.put("category",actualCategory);o.put("subcategory",actualSubcategory);\n        o.put("description","Images & Design".equals(actualCategory)?photoDescription(desc):desc);',1)

p.write_text(s)

g=Path('android/app/build.gradle')
x=g.read_text()
x=re.sub(r'versionCode\s+\d+','versionCode 43',x,count=1)
x=re.sub(r"versionName\s+'[^']+'","versionName '0.8.6'",x,count=1)
g.write_text(x)

assert '"Add a prompt"' in s
assert 'inferPromptCategoryV86' in s and 'inferPromptSubcategoryV86' in s
assert 'o.put("subcategory",actualSubcategory)' in s
assert 'pastePromptFromClipboardV16' not in s
print('Add Prompt auto-classification restored; version 0.8.6 (43)')
