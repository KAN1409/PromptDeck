#!/usr/bin/env python3
from pathlib import Path
import re

src=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
gradle=Path('android/app/build.gradle')
s=src.read_text(encoding='utf-8')

def must_replace(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing source block: {label}')
    s=s.replace(old,new,1)

must_replace(
'''  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){discoverMode="ask";askGoal=(baseQuery==null?"":baseQuery)+(active==null?"":" "+active);home();}\n''',
'''  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){\n    StringBuilder q=new StringBuilder(baseQuery==null?"":baseQuery.trim());\n    if(active!=null&&!active.trim().isEmpty())q.append(' ').append(active.trim());\n    if(refiners!=null)for(String r:refiners)if(r!=null&&!r.trim().isEmpty())q.append(' ').append(r.trim());\n    discoverMode="ask";askCapability="";askGoal=q.toString().trim();contextDraft=title==null?askGoal:title;home();\n  }\n''','smartCollection')

must_replace(
'''  boolean imagePromptV8(Cmd c){return (c.id>=50000&&c.id<50200)||"Images & Visuals".equals(c.category)||(c.category!=null&&c.category.toLowerCase(Locale.ROOT).contains("photo"));}\n''',
'''  boolean imagePromptV8(Cmd c){if(c==null)return false;String cat=c.category==null?"":c.category;return (c.id>=50000&&c.id<50200)||"Images & Design".equals(cat)||"Images & Visuals".equals(cat)||cat.toLowerCase(Locale.ROOT).contains("photo")||cat.toLowerCase(Locale.ROOT).contains("image");}\n''','imagePromptV8')

old='''  int capabilityCategoryBoostV8(Cmd c,String cap){String cat=c.category==null?"":c.category;if(cap.startsWith("career."))return cat.equals("Career & Business")?24:0;if(cap.startsWith("decision."))return cat.equals("Productivity & Planning")||cat.equals("Research & Learning")?18:0;if(cap.startsWith("data."))return cat.equals("Technology & Data")?30:cat.equals("Research & Analysis")?14:0;if(cap.startsWith("code."))return cat.equals("Technology & Development")?24:0;if(cap.startsWith("research."))return cat.equals("Research & Learning")?24:0;if(cap.startsWith("planning."))return cat.equals("Productivity & Planning")?24:0;if(cap.startsWith("learning."))return cat.equals("Science & Education")||cat.equals("Research & Learning")?20:0;if(cap.startsWith("writing."))return cat.equals("Writing & Content")?24:0;return 0;}\n'''
new='''  int capabilityCategoryBoostV8(Cmd c,String cap){\n    String cat=c==null||c.category==null?"":c.category;\n    if(cap.startsWith("image."))return cat.equals("Images & Design")||cat.equals("Images & Visuals")?30:0;\n    if(cap.startsWith("career."))return cat.equals("Work & Business")||cat.equals("Career & Business")?30:0;\n    if(cap.startsWith("decision."))return cat.equals("Planning & Decisions")?30:cat.equals("Research & Analysis")?18:0;\n    if(cap.startsWith("data."))return cat.equals("Technology & Data")?32:cat.equals("Research & Analysis")?16:0;\n    if(cap.startsWith("code."))return cat.equals("Technology & Data")||cat.equals("Technology & Development")?32:0;\n    if(cap.startsWith("research."))return cat.equals("Research & Analysis")||cat.equals("Research & Learning")?32:0;\n    if(cap.startsWith("planning."))return cat.equals("Planning & Decisions")||cat.equals("Productivity & Planning")?32:0;\n    if(cap.startsWith("learning."))return cat.equals("Learning & Education")||cat.equals("Science & Education")?30:cat.equals("Research & Analysis")?12:0;\n    if(cap.startsWith("writing."))return cat.equals("Writing & Communication")||cat.equals("Writing & Content")?32:cat.equals("Creativity & Content")?12:0;\n    return 0;\n  }\n'''
must_replace(old,new,'capabilityCategoryBoostV8')

must_replace(
'''    if(cap.startsWith("image.")&&!(c.id>=50000&&c.id<50200))return -1000;\n''',
'''    if(cap.startsWith("image.")&&!imagePromptV8(c))return -1000;\n''','image pool guard')

old='''  int groupAccent(Group g){String x=g.title; if(x.equals("Writing & Content"))return Color.rgb(61,130,255);if(x.equals("Research & Learning"))return Color.rgb(45,203,140);if(x.equals("Productivity & Planning"))return Color.rgb(226,184,78);if(x.equals("Career & Business"))return Color.rgb(168,91,255);if(x.equals("Technology & Development"))return Color.rgb(32,199,201);if(x.equals("Creativity & Design"))return Color.rgb(243,92,153);if(x.equals("Health & Lifestyle"))return Color.rgb(88,216,109);if(x.equals("Science & Education"))return Color.rgb(61,130,255);return Color.rgb(74,223,209);}\n'''
new='''  int groupAccent(Group g){String x=g.title;if(x.equals("Writing & Communication"))return Color.rgb(61,130,255);if(x.equals("Research & Analysis"))return Color.rgb(45,203,140);if(x.equals("Planning & Decisions"))return Color.rgb(226,184,78);if(x.equals("Work & Business"))return Color.rgb(168,91,255);if(x.equals("Technology & Data"))return Color.rgb(32,199,201);if(x.equals("Creativity & Content"))return Color.rgb(243,92,153);if(x.equals("Health & Life"))return Color.rgb(88,216,109);if(x.equals("Learning & Education"))return Color.rgb(61,130,255);if(x.equals("Images & Design"))return Color.rgb(74,223,209);return Color.rgb(74,223,209);}\n'''
must_replace(old,new,'groupAccent')

old='''  int groupIconRes(Group g){String x=g.title;if(x.equals("Writing & Content"))return R.drawable.pd_ic_write;if(x.equals("Research & Learning"))return R.drawable.pd_ic_research;if(x.equals("Productivity & Planning"))return R.drawable.pd_ic_calendar;if(x.equals("Career & Business"))return R.drawable.pd_ic_briefcase;if(x.equals("Technology & Development"))return R.drawable.pd_ic_code;if(x.equals("Creativity & Design"))return R.drawable.pd_ic_creative;if(x.equals("Health & Lifestyle"))return R.drawable.pd_ic_heart;if(x.equals("Science & Education"))return R.drawable.pd_ic_flask;return R.drawable.pd_ic_image;}\n'''
new='''  int groupIconRes(Group g){String x=g.title;if(x.equals("Writing & Communication"))return R.drawable.pd_ic_write;if(x.equals("Research & Analysis"))return R.drawable.pd_ic_research;if(x.equals("Planning & Decisions"))return R.drawable.pd_ic_calendar;if(x.equals("Work & Business"))return R.drawable.pd_ic_briefcase;if(x.equals("Technology & Data"))return R.drawable.pd_ic_code;if(x.equals("Creativity & Content"))return R.drawable.pd_ic_creative;if(x.equals("Health & Life"))return R.drawable.pd_ic_heart;if(x.equals("Learning & Education"))return R.drawable.pd_ic_flask;return R.drawable.pd_ic_image;}\n'''
must_replace(old,new,'groupIconRes')

# Make use/stack actions feed recency so Home becomes genuinely adaptive.
s=s.replace('use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(c))selected.add(c);home();});','use.setOnClickListener(v->{beginAskSelectionV10(goal);rememberRecent(c);if(!selected.contains(c))selected.add(c);home();});')
s=s.replace('use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(first))selected.add(first);home();});','use.setOnClickListener(v->{beginAskSelectionV10(goal);rememberRecent(first);if(!selected.contains(first))selected.add(first);home();});')
s=s.replace('run.setOnClickListener(v->{sheet.dismiss();sendText(buildSinglePrompt(c,"ask".equals(discoverMode)?askGoal:""));});','run.setOnClickListener(v->{rememberRecent(c);sheet.dismiss();sendText(buildSinglePrompt(c,"ask".equals(discoverMode)?askGoal:""));});')
s=s.replace('add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);sheet.dismiss();home();});','add.setOnClickListener(v->{rememberRecent(c);if(!selected.contains(c))selected.add(c);sheet.dismiss();home();});')

src.write_text(s,encoding='utf-8')

g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 47',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.9.1-capability-router-fix'",g,count=1)
gradle.write_text(g,encoding='utf-8')

# Regression gates for taxonomy drift.
out=src.read_text(encoding='utf-8')
checks=[
  'cat.equals("Work & Business")',
  'cat.equals("Planning & Decisions")',
  'cat.equals("Technology & Data")',
  'cat.equals("Research & Analysis")',
  'cat.equals("Learning & Education")',
  'cat.equals("Writing & Communication")',
  '"Images & Design".equals(cat)',
  'if(cap.startsWith("image.")&&!imagePromptV8(c))return -1000;',
  'for(String r:refiners)',
]
for token in checks:
    if token not in out: raise SystemExit('routing regression gate failed: '+token)
if 'versionCode 47' not in gradle.read_text() or "versionName '0.9.1-capability-router-fix'" not in gradle.read_text():
    raise SystemExit('version gate failed')
print('Capability Router v2 taxonomy/runtime fix applied')
