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

# Add source provenance and optional in-app examples tabs to prompt details.
old='''    info("INSTRUCTION SENT TO CHATGPT",c.instruction);
    relatedActions(c.command);'''
new='''    info("INSTRUCTION SENT TO CHATGPT",c.instruction);
    sourceActions(c);
    relatedActions(c.command);'''
s=s.replace(old,new,1)

source_methods=r'''  void sourceActions(Cmd c){
    if((c.sourceName==null||c.sourceName.isEmpty())&&(c.sourceUrl==null||c.sourceUrl.isEmpty()))return;
    String body=(c.sourceName==null||c.sourceName.isEmpty())?"Curated source":c.sourceName;
    info("SOURCE",body);

    boolean hasExamples=(c.exampleMode!=null&&!c.exampleMode.isEmpty());
    if(!hasExamples){
      if(c.sourceUrl!=null&&!c.sourceUrl.isEmpty()){Button source=secondary("View source  ↗");source.setOnClickListener(v->openUrl(c.sourceUrl));root.addView(source);}return;
    }

    LinearLayout tabs=hbox();tabs.setPadding(0,dp(2),0,dp(8));
    Button promptTab=filterChip("Prompt",true);
    String exampleLabel="Examples";
    if("before_after".equals(c.exampleMode))exampleLabel="Before / After";
    else if("results".equals(c.exampleMode))exampleLabel="Results";
    Button examplesTab=filterChip(exampleLabel,false);
    tabs.addView(promptTab);tabs.addView(examplesTab);root.addView(tabs);

    LinearLayout panel=vbox();panel.setVisibility(View.GONE);root.addView(panel);
    final String tabLabel=exampleLabel;
    promptTab.setOnClickListener(v->{panel.setVisibility(View.GONE);promptTab.setBackground(shape(ACCENT,ACCENT,18));examplesTab.setBackground(shape(SURFACE2,BORDER,18));});
    examplesTab.setOnClickListener(v->{
      promptTab.setBackground(shape(SURFACE2,BORDER,18));examplesTab.setBackground(shape(ACCENT,ACCENT,18));
      if(panel.getChildCount()==0)renderExamples(c,panel,tabLabel);
      panel.setVisibility(View.VISIBLE);
    });
  }

  void renderExamples(Cmd c,LinearLayout panel,String label){
    LinearLayout card=surface(true);card.setPadding(dp(14),dp(14),dp(14),dp(14));
    TextView title=text(label.toUpperCase(Locale.ROOT),11,true,MUTED);card.addView(title);
    if(c.exampleUrls!=null&&!c.exampleUrls.isEmpty()){
      TextView note=text("Result previews are loaded from the original source and are not bundled inside PromptDeck.",12,false,MUTED);note.setPadding(0,dp(6),0,dp(10));card.addView(note);
      int i=1;for(String url:c.exampleUrls){
        TextView cap=text("Example "+(i++),12,true,TEXT);cap.setPadding(0,dp(8),0,dp(6));card.addView(cap);
        ImageView img=new ImageView(this);img.setAdjustViewBounds(true);img.setScaleType(ImageView.ScaleType.CENTER_CROP);img.setBackground(shape(SURFACE2,BORDER,10));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(240));lp.setMargins(0,0,0,dp(10));img.setLayoutParams(lp);card.addView(img);loadRemoteImage(url,img);
      }
    }else{
      String msg="Examples are available on the original source page.";
      if("before_after".equals(c.exampleMode))msg="This prompt has a before-and-after example on the original source page.";
      TextView note=text(msg,13,false,MUTED);note.setPadding(0,dp(8),0,dp(10));card.addView(note);
    }
    if(c.sourceUrl!=null&&!c.sourceUrl.isEmpty()){Button source=secondary("Open source examples  ↗");source.setOnClickListener(v->openUrl(c.sourceUrl));card.addView(source);}
    panel.addView(card);
  }

  void loadRemoteImage(String url,ImageView target){
    TextView loading=null;
    new Thread(()->{
      try{
        java.net.URLConnection conn=new java.net.URL(url).openConnection();conn.setConnectTimeout(8000);conn.setReadTimeout(12000);conn.setRequestProperty("User-Agent","PromptDeck/0.7.3");
        java.io.InputStream in=conn.getInputStream();android.graphics.Bitmap bm=android.graphics.BitmapFactory.decodeStream(in);in.close();
        if(bm!=null)runOnUiThread(()->target.setImageBitmap(bm));
      }catch(Exception e){runOnUiThread(()->{target.setImageDrawable(null);target.setMinimumHeight(dp(72));});}
    }).start();
  }

  void openUrl(String url){
    try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)));}catch(Exception e){toast("Unable to open source");}
  }

'''
if 'void sourceActions(Cmd c)' not in s:
    s=s.replace('''  void relatedActions(String command){''',source_methods+'''  void relatedActions(String command){''',1)
else:
    s=re.sub(r'  void sourceActions\(Cmd c\)\{.*?\n  void openUrl\(String url\)\{.*?\n  \}\n\n',source_methods,s,flags=re.S)

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
print('PromptDeck v0.7.3 curated photo examples patch applied')
