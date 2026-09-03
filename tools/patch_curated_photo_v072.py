#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Rich metadata for curated prompt sources and optional visual examples.
s=s.replace('''    int id; String command,category,subcategory,description,instruction; boolean custom;''',
'''    int id; String command,category,subcategory,description,instruction,sourceName,sourceUrl,exampleMode; ArrayList<String> exampleUrls=new ArrayList<>(); boolean custom;''',1)

s=s.replace('''      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim(); this.custom=custom;
      if(command.isEmpty()||instruction.isEmpty()) throw new JSONException("command and instruction are required");''',
'''      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim();
      sourceName=o.optString("source","").trim();sourceUrl=o.optString("source_url","").trim();exampleMode=o.optString("example_mode","").trim();
      JSONArray ex=o.optJSONArray("example_urls");if(ex!=null)for(int i=0;i<ex.length();i++){String u=ex.optString(i,"").trim();if(!u.isEmpty())exampleUrls.add(u);}this.custom=custom;
      if(command.isEmpty()||instruction.isEmpty()) throw new JSONException("command and instruction are required");''',1)

s=s.replace('''    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);if(subcategory!=null&&!subcategory.isEmpty())o.put("subcategory",subcategory);o.put("description",description);o.put("instruction",instruction);return o; }''',
'''    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);if(subcategory!=null&&!subcategory.isEmpty())o.put("subcategory",subcategory);o.put("description",description);o.put("instruction",instruction);if(sourceName!=null&&!sourceName.isEmpty())o.put("source",sourceName);if(sourceUrl!=null&&!sourceUrl.isEmpty())o.put("source_url",sourceUrl);if(exampleMode!=null&&!exampleMode.isEmpty())o.put("example_mode",exampleMode);if(exampleUrls!=null&&!exampleUrls.isEmpty()){JSONArray a=new JSONArray();for(String u:exampleUrls)a.put(u);o.put("example_urls",a);}return o; }''',1)

# Curated photo sources join the same all[] list and therefore the same category browser.
s=s.replace('''loadCommunityPrompts();JSONArray c=new JSONArray''','''loadCommunityPrompts();loadCuratedPhotoPrompts();JSONArray c=new JSONArray''',1)

loader=r'''  void loadCuratedPhotoPrompts(){
    try{
      JSONArray a=new JSONArray(readAsset("curated_photo_prompts.json"));
      for(int i=0;i<a.length();i++){
        JSONObject x=a.getJSONObject(i);
        String raw=x.optString("command","").trim(), prompt=x.optString("instruction","").trim();
        if(raw.isEmpty()||prompt.isEmpty())continue;
        String command=Cmd.clean(raw),baseSlug=command;int n=2;while(find(command)!=null)command=baseSlug+(n++);
        JSONObject o=new JSONObject(x.toString());o.put("id",50000+i);o.put("command",command);o.put("category","Photo Editing & Image Generation");
        try{all.add(new Cmd(o,false));}catch(Exception ignored){}
      }
    }catch(Exception ignored){}
  }

'''
if 'void loadCuratedPhotoPrompts()' not in s:
    s=s.replace('''  void seedPhotoCommands(){''',loader+'''  void seedPhotoCommands(){''',1)

# Add source provenance and an examples affordance to prompt details.
old='''    info("INSTRUCTION SENT TO CHATGPT",c.instruction);
    relatedActions(c.command);'''
new='''    info("INSTRUCTION SENT TO CHATGPT",c.instruction);
    sourceActions(c);
    relatedActions(c.command);'''
s=s.replace(old,new,1)

source_methods=r'''  void sourceActions(Cmd c){
    if((c.sourceName==null||c.sourceName.isEmpty())&&(c.sourceUrl==null||c.sourceUrl.isEmpty()))return;
    String body=(c.sourceName==null||c.sourceName.isEmpty())?"Curated source":c.sourceName;
    if(c.exampleMode!=null&&!c.exampleMode.isEmpty()){
      if("before_after".equals(c.exampleMode))body+="  •  Before / after examples available";
      else if("results".equals(c.exampleMode))body+="  •  Result examples available";
      else body+="  •  Source examples available";
    }
    info("SOURCE",body);
    if(c.sourceUrl!=null&&!c.sourceUrl.isEmpty()){
      String label="View source";
      if("before_after".equals(c.exampleMode))label="Before / After  ↗";
      else if("results".equals(c.exampleMode))label="Show Results  ↗";
      else if(c.exampleMode!=null&&!c.exampleMode.isEmpty())label="Show Examples  ↗";
      Button examples=secondary(label);examples.setOnClickListener(v->openUrl(c.sourceUrl));root.addView(examples);
    }
  }

  void openUrl(String url){
    try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}catch(Exception e){toast("Unable to open source");}
  }

'''
if 'void sourceActions(Cmd c)' not in s:
    s=s.replace('''  void relatedActions(String command){''',source_methods+'''  void relatedActions(String command){''',1)

# The app is English-only; descriptions should not be forced RTL.
s=s.replace('''d.setTextDirection(View.TEXT_DIRECTION_RTL);d.setGravity(Gravity.END);''','''d.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);d.setGravity(Gravity.START);''')
s=s.replace('''desc.setTextDirection(View.TEXT_DIRECTION_RTL);desc.setGravity(Gravity.END);''','''desc.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);desc.setGravity(Gravity.START);''')
s=s.replace('''hint.setTextDirection(View.TEXT_DIRECTION_RTL);hint.setGravity(Gravity.END);''','''hint.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);hint.setGravity(Gravity.START);''')

if re.search(r'[\u0600-\u06FF]',s):
    hits=[]
    for i,line in enumerate(s.splitlines(),1):
        if re.search(r'[\u0600-\u06FF]',line):hits.append(f'{i}: {line[:180]}')
    raise SystemExit('Arabic visible UI text remains:\n'+'\n'.join(hits[:30]))

p.write_text(s,encoding='utf-8')
print('PromptDeck v0.7.2 curated photo patch applied')
