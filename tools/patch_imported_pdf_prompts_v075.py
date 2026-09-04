from pathlib import Path

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

if 'loadImportedPdfPrompts();' not in s:
    old='loadCommunityPrompts();loadCuratedPhotoPrompts();'
    new='loadCommunityPrompts();loadImportedPdfPrompts();loadCuratedPhotoPrompts();'
    if old not in s:
        raise SystemExit('load() anchor not found')
    s=s.replace(old,new,1)

if 'void loadImportedPdfPrompts()' not in s:
    anchor='  String librarySlug(String title){'
    if anchor not in s:
        raise SystemExit('librarySlug anchor not found')
    method=r'''  void loadImportedPdfPrompts(){
    try{
      JSONArray a=new JSONArray(readAsset("imported_pdf_prompts.json"));
      HashSet<String> seen=new HashSet<>();
      for(Cmd c:all)seen.add(normalizePrompt(c.instruction));
      for(int i=0;i<a.length();i++){
        JSONObject x=a.getJSONObject(i);
        String title=x.optString("title","").trim(),prompt=x.optString("prompt","").trim();
        if(title.isEmpty()||prompt.isEmpty())continue;
        String norm=normalizePrompt(prompt);if(seen.contains(norm))continue;
        String slug=librarySlug(title),baseSlug=slug;int n=2;while(find(slug)!=null)slug=baseSlug+(n++);
        JSONObject o=new JSONObject();
        o.put("id",60000+i);o.put("command",slug);
        o.put("category",x.optString("category","Specialist Roles"));
        o.put("subcategory",x.optString("subcategory","Imported PDF Collection"));
        o.put("description",x.optString("description",title));o.put("instruction",prompt);
        o.put("source",x.optString("source","Imported PDF Collection"));
        try{all.add(new Cmd(o,false));seen.add(norm);}catch(Exception ignored){}
      }
    }catch(Exception ignored){}
  }

  String normalizePrompt(String s){return s==null?"":s.replaceAll("\\s+"," ").trim().toLowerCase(Locale.ROOT);}

'''
    s=s.replace(anchor,method+anchor,1)

p.write_text(s,encoding='utf-8')
print('Imported PDF prompt loader patched')
