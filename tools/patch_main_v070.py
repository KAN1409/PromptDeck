#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# v0.7.1 direction: the 2,160 prompts are not a separate Prompt Library tab.
# They are loaded into the same category system as the built-in operators.

# Remove the separate full-library launcher from Home if it exists.
s=s.replace('''    View fullLibrary=menuCard("⌕","Prompt Library","Browse 2,160 full prompts by category or search");fullLibrary.setOnClickListener(v->startActivityForResult(new Intent(this,PromptLibraryActivity.class),LIBRARY_PICK_REQ));root.addView(fullLibrary);spacer(8);View library=menuCard("＋","My Prompt Library","Add, import or export your own prompts");library.setOnClickListener(v->library());root.addView(library);''',
'''    View library=menuCard("＋","My Prompts","Add, import or export your own prompts");library.setOnClickListener(v->library());root.addView(library);''',1)

# Keep Cmd rich enough to retain the source subcategory from prompts_library.json.
s=s.replace('''    int id; String command,category,description,instruction; boolean custom;''',
'''    int id; String command,category,subcategory,description,instruction; boolean custom;''',1)
s=s.replace('''      id=o.optInt("id",0); command=clean(o.optString("command","")); category=o.optString("category","Custom").trim();
      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim(); this.custom=custom;''',
'''      id=o.optInt("id",0); command=clean(o.optString("command","")); category=o.optString("category","Custom").trim(); subcategory=o.optString("subcategory","").trim();
      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim(); this.custom=custom;''',1)
s=s.replace('''    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);o.put("description",description);o.put("instruction",instruction);return o; }''',
'''    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);if(subcategory!=null&&!subcategory.isEmpty())o.put("subcategory",subcategory);o.put("description",description);o.put("instruction",instruction);return o; }''',1)

# Add only genuinely missing top-level categories; preserve all original categories.
needle='''    new Group("▦","Data & Formatting","Structure, transform and present information","table","bullets","outline","format","json","csv","schema","template","prompt"),
    new Group("◉","Photo Editing & Image Generation"'''
replacement='''    new Group("▦","Data & Formatting","Structure, transform and present information","table","bullets","outline","format","json","csv","schema","template","prompt"),
    new Group("✧","AI & Prompting","AI roles, prompt patterns, agents and model workflows"),
    new Group("▤","Business & Marketing","Business, strategy, marketing, sales and finance roles"),
    new Group("♡","Health & Wellness","Medical, mental wellness, fitness and nutrition roles"),
    new Group("⌂","Lifestyle & Personal","Travel, food, home, relationships and personal-life roles"),
    new Group("◆","Specialist Roles","Specialized expert roles that do not fit another category"),
    new Group("◉","Photo Editing & Image Generation"'''
if needle in s:
    s=s.replace(needle,replacement,1)

# Load the community prompt collection directly into the canonical all[] list.
s=s.replace('''  void load(){all.clear();try{JSONArray a=new JSONArray(readAsset("commands.json"));for(int i=0;i<a.length();i++)all.add(new Cmd(a.getJSONObject(i),false));JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}}catch(Exception e){throw new RuntimeException(e);}seedPhotoCommands();seedExtraPhotoCommands();englishizeDescriptions();}''',
'''  void load(){all.clear();try{JSONArray a=new JSONArray(readAsset("commands.json"));for(int i=0;i<a.length();i++)all.add(new Cmd(a.getJSONObject(i),false));loadCommunityPrompts();JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}}catch(Exception e){throw new RuntimeException(e);}seedPhotoCommands();seedExtraPhotoCommands();englishizeDescriptions();}''',1)

insert_before='''  void seedPhotoCommands(){'''
community_methods=r'''  void loadCommunityPrompts(){
    try{
      JSONArray a=new JSONArray(readAsset("prompts_library.json"));
      for(int i=0;i<a.length();i++){
        JSONObject x=a.getJSONObject(i);
        String title=x.optString("title","").trim(), prompt=x.optString("prompt","").trim();
        if(title.isEmpty()||prompt.isEmpty())continue;
        String slug=librarySlug(title);
        String baseSlug=slug;int n=2;while(find(slug)!=null)slug=baseSlug+(n++);
        JSONObject o=new JSONObject();
        o.put("id",30000+i);
        o.put("command",slug);
        o.put("category",mapLibraryCategory(x.optString("category","Other Expert Roles")));
        o.put("subcategory",x.optString("subcategory","Specialist Roles"));
        o.put("description",x.optString("description",title));
        o.put("instruction",prompt);
        try{all.add(new Cmd(o,false));}catch(Exception ignored){}
      }
    }catch(Exception ignored){}
  }

  String librarySlug(String title){
    String s=title.replaceAll("(?i)^act as (an? )?","").replaceAll("[^A-Za-z0-9]+","").trim();
    if(s.isEmpty())s="ExpertPrompt";
    if(s.length()>38)s=s.substring(0,38);
    return s;
  }

  String mapLibraryCategory(String source){
    if(source==null)return"Specialist Roles";
    if(source.equals("Writing & Language"))return"Writing & Rewriting";
    if(source.equals("Research & Analysis"))return"Research & Analysis";
    if(source.equals("Work & Career"))return"Work & Career";
    if(source.equals("Learning & Education"))return"Learning & Study";
    if(source.equals("Creative & Content"))return"Content Creation";
    if(source.equals("Technology & Development"))return"Problem Solving & Technical";
    if(source.equals("Tools & Simulations"))return"Data & Formatting";
    if(source.equals("AI & Prompting"))return"AI & Prompting";
    if(source.equals("Business & Marketing"))return"Business & Marketing";
    if(source.equals("Health & Wellness"))return"Health & Wellness";
    if(source.equals("Lifestyle & Personal"))return"Lifestyle & Personal";
    return"Specialist Roles";
  }

'''
if 'void loadCommunityPrompts()' not in s and insert_before in s:
    s=s.replace(insert_before,community_methods+insert_before,1)

# A category page now contains built-ins + every mapped prompt from prompts_library.json.
old_group='''    LinkedHashMap<String,ArrayList<Cmd>> subs=new LinkedHashMap<>();for(String n:g.names){Cmd c=find(n);if(c!=null){String sc=subcat(c.command,g.title);if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);}}for(Cmd c:all){if(!c.custom||!c.category.equalsIgnoreCase(g.title))continue;String sc=g.title.contains("Photo Editing")?"Imported Photo Prompts":"Custom";if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);}'''
new_group='''    LinkedHashMap<String,ArrayList<Cmd>> subs=new LinkedHashMap<>();LinkedHashSet<Cmd> seen=new LinkedHashSet<>();for(String n:g.names){Cmd c=find(n);if(c!=null){String sc=subcat(c.command,g.title);if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);seen.add(c);}}for(Cmd c:all){if(seen.contains(c)||!c.category.equalsIgnoreCase(g.title))continue;String sc=(c.subcategory!=null&&!c.subcategory.isEmpty())?c.subcategory:(c.custom?"Custom":"More prompts");if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);}'''
if old_group in s:
    s=s.replace(old_group,new_group,1)

# Update home copy/count so the information architecture is clear.
s=s.replace('''base("Choose a category","Browse prompt tools by category. Open any category, choose a prompt, review what it does, then add it to your Stack.",true);''',
'''base("Choose a category","All built-in and full prompts live inside these categories. Open a category, choose a prompt, review it, then add it to your Stack.",true);''',1)
s=s.replace('''TextView foot=text("120 built-in prompt operators  •  local library  •  no API required",11,false,MUTED);''',
'''TextView foot=text(all.size()+" prompts integrated into categories  •  local  •  no API required",11,false,MUTED);''',1)

# Visible app Java must remain English-only.
if re.search(r'[\u0600-\u06FF]',s):
    hits=[]
    for i,line in enumerate(s.splitlines(),1):
        if re.search(r'[\u0600-\u06FF]',line):hits.append(f'{i}: {line[:180]}')
    raise SystemExit('Arabic UI text remains in MainActivity:\n'+'\n'.join(hits[:30]))

p.write_text(s,encoding='utf-8')
print('PromptDeck category integration patch applied')
