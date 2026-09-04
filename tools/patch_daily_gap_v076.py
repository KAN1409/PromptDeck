from pathlib import Path

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

old='loadCommunityPrompts();loadImportedPdfPrompts();loadCuratedPhotoPrompts();'
new='loadCommunityPrompts();loadImportedPdfPrompts();loadDailyGapPrompts();loadCuratedPhotoPrompts();'
if old in s and 'loadDailyGapPrompts();' not in s:
    s=s.replace(old,new,1)

anchor='  String normalizePrompt(String s){return s==null?"":s.replaceAll("\\\\s+"," ").trim().toLowerCase(Locale.ROOT);}\n'
method='''  void loadDailyGapPrompts(){\n    try{\n      JSONArray a=new JSONArray(readAsset("daily_gap_prompts_100.json"));\n      HashSet<String> seen=new HashSet<>();\n      for(Cmd c:all)seen.add(normalizePrompt(c.instruction));\n      for(int i=0;i<a.length();i++){\n        JSONObject x=a.getJSONObject(i);\n        String raw=x.optString("command","").trim(),prompt=x.optString("instruction","").trim();\n        if(raw.isEmpty()||prompt.isEmpty())continue;\n        String norm=normalizePrompt(prompt);if(seen.contains(norm))continue;\n        String command=Cmd.clean(raw),base=command;int n=2;while(find(command)!=null)command=base+(n++);\n        JSONObject o=new JSONObject(x.toString());o.put("command",command);\n        try{all.add(new Cmd(o,false));seen.add(norm);}catch(Exception ignored){}\n      }\n    }catch(Exception ignored){}\n  }\n\n'''
if 'void loadDailyGapPrompts()' not in s:
    if anchor not in s:
        raise SystemExit('normalizePrompt anchor not found')
    s=s.replace(anchor,method+anchor,1)

p.write_text(s,encoding='utf-8')
print('Daily gap prompt loader patched')
