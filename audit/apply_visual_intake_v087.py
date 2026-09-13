#!/usr/bin/env python3
from pathlib import Path
import re

main=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=main.read_text(encoding='utf-8')

def require(anchor,name):
    if anchor not in s: raise SystemExit(f'missing anchor: {name}')

old='''  void consumeIncomingShareV15(){
    Intent in=getIntent();if(in==null||!Intent.ACTION_SEND.equals(in.getAction())||!"text/plain".equals(in.getType()))return;
    String t=in.getStringExtra(Intent.EXTRA_TEXT);if(t==null||t.trim().isEmpty())return;
    contextDraft=t.trim();askGoal=contextDraft;discoverMode="ask";
  }'''
new='''  void consumeIncomingShareV15(){
    Intent in=getIntent();if(in==null||!Intent.ACTION_SEND.equals(in.getAction())||!"text/plain".equals(in.getType()))return;
    String t=in.getStringExtra(Intent.EXTRA_TEXT);if(t==null||t.trim().isEmpty())return;
    String shared=t.trim();
    if(isPromptDeckImportV17(shared)){importPromptDeckPayloadV17(shared,true);in.setAction(null);return;}
    contextDraft=shared;askGoal=contextDraft;discoverMode="ask";
  }'''
require(old,'incoming share')
s=s.replace(old,new,1)

anchor='''  void loadCommunityPrompts(){'''
require(anchor,'loadCommunityPrompts')
methods=r'''  boolean isPromptDeckImportV17(String raw){return raw!=null&&raw.trim().startsWith("PROMPTDECK_IMPORT_V1");}

  String stripImportEnvelopeV17(String raw){
    String x=raw==null?"":raw.trim();
    if(x.startsWith("PROMPTDECK_IMPORT_V1"))x=x.substring("PROMPTDECK_IMPORT_V1".length()).trim();
    if(x.startsWith("```")){int nl=x.indexOf('\n');if(nl>=0)x=x.substring(nl+1);int end=x.lastIndexOf("```");if(end>=0)x=x.substring(0,end);}
    return x.trim();
  }

  String canonicalImportCategoryV17(String requested,String instruction){
    String[] cats={"Writing & Communication","Research & Analysis","Planning & Decisions","Work & Business","Technology & Data","Learning & Education","Creativity & Content","Images & Design","Health & Life"};
    String r=requested==null?"":requested.trim();for(String c:cats)if(c.equals(r))return c;
    return inferPromptCategoryV86(instruction);
  }

  String canonicalImageSubcategoryV17(String requested,String instruction){
    String r=requested==null?"":requested.trim();
    String[] ok={"Photo Editing","Image Enhancement","Lighting & Relighting","Cinematic Style","Travel Photography","Portrait Editing","Composition & Camera","Atmosphere & Weather","Aerial & Perspective","Creative Image Generation","Editorial & Commercial","Color & Mood","Image Editing","Graphic Design","Image Generation"};
    for(String x:ok)if(x.equalsIgnoreCase(r))return x;
    String z=(instruction==null?"":instruction).toLowerCase(Locale.ROOT);
    if(hasAny(z,"fog","mist","haze","rain","snow","weather","atmosphere"))return "Atmosphere & Weather";
    if(hasAny(z,"golden hour","relight","lighting","backlight","soft light","sunset light"))return "Lighting & Relighting";
    if(hasAny(z,"drone","aerial","top-down","top down","bird's-eye","birds-eye"))return "Aerial & Perspective";
    if(hasAny(z,"long exposure","shutter","motion trail","light trail","camera angle","lens"))return "Composition & Camera";
    if(hasAny(z,"cinematic","movie still","filmic","cinema"))return "Cinematic Style";
    if(hasAny(z,"travel","travel diary","travel journal","destination"))return "Travel Photography";
    if(hasAny(z,"portrait","face","headshot","skin"))return "Portrait Editing";
    if(hasAny(z,"enhance","upscale","restore","resolution","detail","sharpness"))return "Image Enhancement";
    if(hasAny(z,"edit","remove","replace","background","retouch"))return "Photo Editing";
    if(hasAny(z,"editorial","commercial","advertising","campaign","product photography"))return "Editorial & Commercial";
    if(hasAny(z,"color grade","colour grade","palette","mood","grading"))return "Color & Mood";
    return "Creative Image Generation";
  }

  boolean duplicateInstructionV17(String instruction){String n=normalizePrompt(instruction);for(Cmd c:all)if(normalizePrompt(c.instruction).equals(n))return true;return false;}

  int importPromptDeckPayloadV17(String raw,boolean fromShare){
    int added=0,skipped=0;
    try{
      String body=stripImportEnvelopeV17(raw);JSONArray arr;
      if(body.startsWith("["))arr=new JSONArray(body);else{JSONObject root=new JSONObject(body);arr=root.optJSONArray("prompts");if(arr==null)throw new JSONException("Missing prompts array");}
      for(int i=0;i<arr.length();i++){
        JSONObject x=arr.optJSONObject(i);if(x==null){skipped++;continue;}
        String instruction=x.optString("instruction",x.optString("prompt","")).trim();if(instruction.isEmpty()||duplicateInstructionV17(instruction)){skipped++;continue;}
        String category=canonicalImportCategoryV17(x.optString("category",""),instruction);
        String subcategory="Images & Design".equals(category)?canonicalImageSubcategoryV17(x.optString("subcategory",""),instruction):x.optString("subcategory","").trim();
        if(subcategory.isEmpty())subcategory=inferPromptSubcategoryV86(instruction,category);
        String rawCommand=x.optString("command","").trim();String command=Cmd.clean(rawCommand);
        if(command.isEmpty())command=autoCommandName(instruction,category);String base=command;int suffix=2;while(find(command)!=null)command=base+(suffix++);
        String description=x.optString("description","").trim();if(description.isEmpty())description=autoDescription(instruction,category);
        JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",command);o.put("category",category);o.put("subcategory",subcategory);o.put("description",description);o.put("instruction",instruction);
        all.add(new Cmd(o,true));added++;
      }
      if(added>0)saveCustom();
      if(fromShare){discoverMode="browse";discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=60;}
      toast(added>0?("Imported "+added+" prompt"+(added==1?"":"s")+(skipped>0?" • "+skipped+" skipped":"")):("No new prompts imported"+(skipped>0?" • "+skipped+" skipped":"")));
    }catch(Exception e){toast("PromptDeck import failed");}
    return added;
  }

  String visualIntakeInstructionV17(){
    return "Analyze every image I attach and extract every reusable visual command, preset, image-editing behavior, photography style, or image-generation concept. Convert each useful item into a standalone ChatGPT-first prompt. Do not copy source metadata, creator names, watermarks, hashtags, social-media clutter, Midjourney parameters, or model-specific syntax. Infer the actual visual intent from both visible text and the example image. Keep meaningful variants; skip covers and non-prompt slides. For image entries use category exactly Images & Design and choose a capability-specific subcategory such as Photo Editing, Image Enhancement, Lighting & Relighting, Cinematic Style, Travel Photography, Portrait Editing, Composition & Camera, Atmosphere & Weather, Aerial & Perspective, Creative Image Generation, Editorial & Commercial, or Color & Mood. Preserve identity, pose, composition, scene geometry, and important objects when the intent is image editing unless the requested effect requires a change. Return ONLY this machine-readable format with no markdown and no explanation: PROMPTDECK_IMPORT_V1 followed by one JSON object: {\\\"prompts\\\":[{\\\"title\\\":\\\"\\\",\\\"command\\\":\\\"\\\",\\\"description\\\":\\\"\\\",\\\"category\\\":\\\"Images & Design\\\",\\\"subcategory\\\":\\\"\\\",\\\"instruction\\\":\\\"\\\",\\\"sourceLabel\\\":\\\"\\\",\\\"confidence\\\":0.0}]}. Normalize awkward slash labels into concise readable commands. If a candidate is too ambiguous to infer safely, omit it rather than inventing details.";
  }

'''
s=s.replace(anchor,methods+anchor,1)

old_dialog='''    AlertDialog d=new AlertDialog.Builder(this).setTitle("Add a prompt").setView(box).setNegativeButton("Cancel",null).setPositiveButton("Add prompt",null).create();
    d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String raw=bulk.getText().toString().trim();if(raw.isEmpty()){toast("Paste a prompt first");return;}int[] result=parseBulkCommands(raw,"");if(result[0]==0){toast("Couldn't add this prompt");return;}saveCustom();d.dismiss();library();toast("Prompt added to your library");}));d.show();'''
new_dialog='''    AlertDialog d=new AlertDialog.Builder(this).setTitle("Add a prompt").setView(box).setNegativeButton("Cancel",null).setNeutralButton("Create from images",null).setPositiveButton("Add prompt",null).create();
    d.setOnShowListener(z->{d.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v->sendText(visualIntakeInstructionV17()));d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String raw=bulk.getText().toString().trim();if(raw.isEmpty()){toast("Paste a prompt first");return;}if(isPromptDeckImportV17(raw)){int n=importPromptDeckPayloadV17(raw,false);if(n>0){d.dismiss();discoverMode="browse";home();}return;}int[] result=parseBulkCommands(raw,"");if(result[0]==0){toast("Couldn't add this prompt");return;}saveCustom();d.dismiss();library();toast("Prompt added to your library");});});d.show();'''
require(old_dialog,'Add Prompt dialog')
s=s.replace(old_dialog,new_dialog,1)

main.write_text(s,encoding='utf-8')

gradle=Path('android/app/build.gradle')
g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 44',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.7'",g,count=1)
gradle.write_text(g,encoding='utf-8')

assert 'PROMPTDECK_IMPORT_V1' in s
assert 'importPromptDeckPayloadV17' in s
assert 'Create from images' in s
assert 'versionCode 44' in g and "versionName '0.8.7'" in g
print('PromptDeck visual intake v0.8.7 prepared')
