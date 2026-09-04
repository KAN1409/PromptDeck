from pathlib import Path

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

old='static final int IMPORT_REQ=1001, EXPORT_REQ=1002, LIBRARY_PICK_REQ=1003;'
new='static final int IMPORT_REQ=1001, EXPORT_REQ=1002, LIBRARY_PICK_REQ=1003, EXPORT_ALL_REQ=1004;'
if old not in s: raise SystemExit('request code anchor not found')
s=s.replace(old,new,1)

old='View exp=menuCard("↑","Export custom","Back up or move your custom prompts");exp.setOnClickListener(v->openExport());root.addView(exp);'
new=old+'View expAll=menuCard("⇧","Export All","Export every prompt currently integrated in PromptDeck (built-in, imported, curated and custom)");expAll.setOnClickListener(v->openExportAll());root.addView(expAll);'
if old not in s: raise SystemExit('library export anchor not found')
s=s.replace(old,new,1)

old='void openImport(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");startActivityForResult(i,IMPORT_REQ);}void openExport(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"PromptDeck-custom.promptdeck.json");startActivityForResult(i,EXPORT_REQ);}'
new=old+'void openExportAll(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"PromptDeck-ALL-prompts.json");startActivityForResult(i,EXPORT_ALL_REQ);}'
if old not in s: raise SystemExit('open export anchor not found')
s=s.replace(old,new,1)

old='try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}'
new='try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());else if(r==EXPORT_ALL_REQ)exportAllPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}'
if old not in s: raise SystemExit('activity result anchor not found')
s=s.replace(old,new,1)

old='void exportPack(Uri u)throws Exception{JSONObject p=new JSONObject();p.put("format","promptdeck-pack");p.put("version",1);p.put("name","PromptDeck custom prompts");JSONArray a=new JSONArray();for(Cmd c:all)if(c.custom)a.put(c.json());p.put("commands",a);OutputStream out=getContentResolver().openOutputStream(u,"w");if(out==null)throw new IOException("Can\'t open destination");out.write(p.toString(2).getBytes(StandardCharsets.UTF_8));out.close();toast("Custom prompts exported");}'
new=old+'void exportAllPack(Uri u)throws Exception{JSONObject pack=new JSONObject();pack.put("format","promptdeck-all-prompts");pack.put("version",1);pack.put("count",all.size());JSONArray a=new JSONArray();for(Cmd c:all){JSONObject o=c.json();o.put("custom",c.custom);a.put(o);}pack.put("commands",a);OutputStream out=getContentResolver().openOutputStream(u,"w");if(out==null)throw new IOException("Can\'t open destination");out.write(pack.toString(2).getBytes(StandardCharsets.UTF_8));out.close();toast("Exported all "+all.size()+" prompts");}'
if old not in s: raise SystemExit('export pack anchor not found')
s=s.replace(old,new,1)

# Guard against duplicate application and verify final functionality.
assert 'Export All' in s
assert 'void exportAllPack(Uri u)' in s
assert 'EXPORT_ALL_REQ=1004' in s
p.write_text(s,encoding='utf-8')
print('Export All patched into MainActivity')
