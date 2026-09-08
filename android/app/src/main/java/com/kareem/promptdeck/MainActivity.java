package com.kareem.promptdeck;

import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.view.*;
import android.view.inputmethod.EditorInfo;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class MainActivity extends Activity {
  static final int IMPORT_REQ=1001, EXPORT_REQ=1002, LIBRARY_PICK_REQ=1003, EXPORT_ALL_REQ=1004;
  static final String PREFS="promptdeck", CUSTOM="custom_commands_v1";
  static final int BG=Color.rgb(7,17,29), SURFACE=Color.rgb(13,26,42), SURFACE2=Color.rgb(18,34,53), INPUT=Color.rgb(19,35,56), BORDER=Color.rgb(36,54,76), DIVIDER=Color.rgb(29,44,64);
  static final int TEXT=Color.rgb(243,247,253), MUTED=Color.rgb(166,181,200), TERTIARY=Color.rgb(126,144,167), ACCENT=Color.rgb(44,123,255), PURPLE=Color.rgb(107,93,255), SUCCESS=Color.rgb(79,213,139), FAVORITE=Color.rgb(255,204,77);
  static final int SATIN_TOP=Color.rgb(18,34,53), SATIN_BOTTOM=Color.rgb(13,26,42), SATIN_EDGE=Color.rgb(36,54,76);

  static class Cmd {
    int id; String command,category,subcategory,description,instruction,sourceName,sourceUrl,exampleMode; ArrayList<String> exampleUrls=new ArrayList<>(); boolean custom;
    Cmd(JSONObject o, boolean custom) throws JSONException {
      id=o.optInt("id",0); command=clean(o.optString("command","")); category=o.optString("category","Custom").trim(); subcategory=o.optString("subcategory","").trim();
      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim();
      sourceName=o.optString("source","").trim();sourceUrl=o.optString("source_url","").trim();exampleMode=o.optString("example_mode","").trim();
      JSONArray ex=o.optJSONArray("example_urls");if(ex!=null)for(int i=0;i<ex.length();i++){String u=ex.optString(i,"").trim();if(!u.isEmpty())exampleUrls.add(u);}this.custom=custom;
      if(command.isEmpty()||instruction.isEmpty()) throw new JSONException("command and instruction are required");
    }
    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);if(subcategory!=null&&!subcategory.isEmpty())o.put("subcategory",subcategory);o.put("description",description);o.put("instruction",instruction);if(sourceName!=null&&!sourceName.isEmpty())o.put("source",sourceName);if(sourceUrl!=null&&!sourceUrl.isEmpty())o.put("source_url",sourceUrl);if(exampleMode!=null&&!exampleMode.isEmpty())o.put("example_mode",exampleMode);if(exampleUrls!=null&&!exampleUrls.isEmpty()){JSONArray a=new JSONArray();for(String u:exampleUrls)a.put(u);o.put("example_urls",a);}return o; }
    static String clean(String s){s=s==null?"":s.trim();while(s.startsWith("/"))s=s.substring(1);return s.replaceAll("[^A-Za-z0-9_-]","");}
  }
  static class Group { String title,sub,icon; String[] names; Group(String icon,String title,String sub,String...names){this.icon=icon;this.title=title;this.sub=sub;this.names=names;} }

  final ArrayList<Cmd> all=new ArrayList<>(), selected=new ArrayList<>();
  static final ArrayList<Cmd> BUILTIN_CACHE_V15=new ArrayList<>(); static volatile boolean BUILTIN_CACHE_READY_V15=false;
  LinearLayout root; EditText context,finalPrompt;
  String page="home"; Group currentGroup=null; String contextDraft=""; String discoverCategory=""; String discoverSubcategory=""; boolean discoverFavorites=false; String discoverPreset=""; String discoverMode="landing"; String askGoal=""; String askCapability=""; String askSelectionGoal=""; int browseLimit=30; HashMap<Integer,HashMap<String,String>> promptVars=new HashMap<>();

  final Group[] groups={
    new Group("","Writing & Communication","Write, rewrite, translate and communicate clearly"),
    new Group("","Research & Analysis","Find, verify, summarize and compare information"),
    new Group("","Planning & Decisions","Plan work, organize priorities and make better decisions"),
    new Group("","Work & Business","Career, workplace, strategy, marketing and business"),
    new Group("","Technology & Data","Coding, debugging, data, systems and AI workflows"),
    new Group("","Learning & Education","Understand, study, practice and teach"),
    new Group("","Creativity & Content","Ideas, stories, social content and creative direction"),
    new Group("","Images & Design","Generate, edit and transform images and graphics"),
    new Group("","Health & Life","Wellness, fitness, habits, relationships and lifestyle")
  };

  @Override public void onCreate(Bundle b){
    super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(0);
    final Bundle saved=b;
    if(BUILTIN_CACHE_READY_V15){
      try{load();restoreWorkspaceV15(saved);consumeIncomingShareV15();home();return;}catch(Throwable ignored){}
    }
    showStartupV15();
    new Thread(()->{try{load();runOnUiThread(()->{restoreWorkspaceV15(saved);consumeIncomingShareV15();home();});}catch(Throwable e){runOnUiThread(()->{LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setBackgroundColor(BG);box.setPadding(dp(24),dp(24),dp(24),dp(24));box.addView(text("PromptDeck could not load the prompt library.",16,true,TEXT));box.addView(text(e.getMessage()==null?e.getClass().getSimpleName():e.getMessage(),12,false,MUTED));setContentView(box);});}},"PromptDeckCatalog").start();
  }

  @Override protected void onNewIntent(Intent intent){
    super.onNewIntent(intent);setIntent(intent);
    if(BUILTIN_CACHE_READY_V15){consumeIncomingShareV15();home();}
  }

  @Override protected void onSaveInstanceState(Bundle out){
    super.onSaveInstanceState(out);out.putString("v15_mode",discoverMode);out.putString("v15_goal",askGoal);out.putString("v15_cap",askCapability);out.putString("v15_selection_goal",askSelectionGoal);out.putString("v15_context",contextDraft);out.putString("v15_cat",discoverCategory);out.putString("v15_sub",discoverSubcategory);out.putString("v15_query",discoverPreset);out.putBoolean("v15_fav",discoverFavorites);out.putInt("v15_limit",browseLimit);ArrayList<Integer> ids=new ArrayList<>();for(Cmd c:selected)ids.add(c.id);out.putIntegerArrayList("v15_selected",ids);
  }

  @Override public void onBackPressed(){
    if(!"landing".equals(discoverMode)){discoverMode="landing";discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();return;}
    super.onBackPressed();
  }

  void loadLegacyV15(){all.clear();try{JSONArray a=new JSONArray(readAsset("commands.json"));for(int i=0;i<a.length();i++)all.add(new Cmd(a.getJSONObject(i),false));loadCommunityPrompts();loadImportedPdfPrompts();loadDailyGapPrompts();loadCuratedPhotoPrompts();JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}}catch(Exception e){throw new RuntimeException(e);}seedPhotoCommands();seedExtraPhotoCommands();englishizeDescriptions();canonicalizeLibrary();applyChatGPTNativeFinal();applyProposalTaxonomy();}

  void canonicalizeLibrary(){
    HashMap<String,String> legacy=new HashMap<>();
    legacy.put("Writing","Writing & Rewriting");legacy.put("Explain","Learning & Study");legacy.put("Ideation","Thinking & Ideas");legacy.put("Planning","Planning & Execution");legacy.put("Analysis","Research & Analysis");legacy.put("Decision","Thinking & Ideas");legacy.put("Study","Learning & Study");legacy.put("Research","Research & Analysis");legacy.put("Work","Work & Career");legacy.put("Format","Data & Formatting");legacy.put("Reasoning","Thinking & Ideas");legacy.put("Career","Work & Career");legacy.put("Technical","Problem Solving & Technical");legacy.put("Coding","Problem Solving & Technical");legacy.put("Data","Data & Formatting");legacy.put("Quality","Writing & Rewriting");legacy.put("Evaluation","Research & Analysis");legacy.put("Meta","AI & Prompting");legacy.put("Content","Content Creation");

    HashMap<String,String> preferred=new HashMap<>();
    preferred.put("NoteTakingAssistant2","NoteTakingassistant");
    preferred.put("Sales","Digitalproductideas");
    preferred.put("Selarideasforautomation","Digitalproductideas");
    preferred.put("Ainew","UltraRealisticNoirPortraitCreation");
    preferred.put("VirtualizationExpert","CompareTopVirtualizationSolutions");
    preferred.put("emailsProfessionals","ProfessionalEmailWriterforAnyOccasion");
    preferred.put("PowerShellScripttoMoveDisabledADUserst","PowerShellScriptforManagingDisabledADU");
    preferred.put("NightShiftDessertShop","EveningataTurkishDessertShopAPhotograp");
    preferred.put("DevelopaUILibraryforESP32","ESP32UILibraryDevelopment");
    preferred.put("MinimalistEditorialBeautyAnalysiswithT","MinimalistEditorialBeautyAnalysiswithE");
    preferred.put("MinimalistEditorialBeautyAnalysiswithE2","MinimalistEditorialBeautyAnalysiswithE");
    preferred.put("FrontendDeveloper","FrontendDeveloperSkill");
    preferred.put("InvestigativeResearchAssistantforUncov","InvestigativeResearchAssistant");
    preferred.put("MakeAIwritenaturally","PlainTalkStyleGuide");
    preferred.put("PromptGeneratorforclaudecode","PromptGeneratorforLanguageModels");
    preferred.put("WebApplicationTestingSkillImported","WebApplicationTestingSkill");
    preferred.put("Videoextractorprompt","Videoreviewandteacher");
    preferred.put("BikiniGirl","Seasidewalker");
    preferred.put("Video","Cocktailvideos");
    preferred.put("MirrorSelfieSceneDescription","Detailedmirrorselfieroomscene");
    preferred.put("Image","ProfessionalBadgePhotoReadytoUse");

    HashMap<String,String> rename=new HashMap<>();
    rename.put("Digitalproductideas","SelarDigitalProductIdeas");
    rename.put("NoteTakingassistant","LectureNoteTakingAssistant");
    rename.put("Detailedmirrorselfieroomscene","MirrorSelfieScene");
    rename.put("InvestigativeResearchAssistant","InvestigativeResearchAssistant");
    rename.put("CompareTopVirtualizationSolutions","VirtualizationSolutionsComparison");
    rename.put("EveningataTurkishDessertShopAPhotograp","TurkishDessertShopNightScene");
    rename.put("ESP32UILibraryDevelopment","ESP32UILibraryDevelopment");
    rename.put("FrontendDeveloperSkill","FrontendDeveloper");
    rename.put("MinimalistEditorialBeautyAnalysiswithE","MinimalistEditorialBeautyAnalysis");
    rename.put("PromptGeneratorforLanguageModels","ChatGPTPromptGenerator");
    rename.put("ProfessionalEmailWriterforAnyOccasion","ProfessionalEmailWriter");
    rename.put("PowerShellScriptforManagingDisabledADU","MoveDisabledADUsers");
    rename.put("Videoreviewandteacher","VideoReviewAndTeachingExtractor");
    rename.put("PlainTalkStyleGuide","PlainTalkNaturalWriting");

    HashSet<String> commands=new HashSet<>();for(Cmd c:all)commands.add(c.command);
    Iterator<Cmd> it=all.iterator();
    while(it.hasNext()){
      Cmd c=it.next();
      String keep=preferred.get(c.command);
      if(keep!=null&&commands.contains(keep)){it.remove();continue;}
      String mapped=legacy.get(c.category);if(mapped!=null)c.category=mapped;
      if(c.category.equals("Transform")){
        String q=(c.command+" "+c.description).toLowerCase(Locale.ROOT);
        c.category=(q.contains("json")||q.contains("csv")||q.contains("table")||q.contains("format")||q.contains("extract")||q.contains("convert")||q.contains("structure"))?"Data & Formatting":"Writing & Rewriting";
      }
      if(c.subcategory==null||c.subcategory.trim().isEmpty())c.subcategory="General";
      String rn=rename.get(c.command);if(rn!=null)c.command=rn;
      if(c.command.equals("ChatGPTPromptGenerator")&&!c.instruction.toLowerCase(Locale.ROOT).contains("chatgpt"))c.instruction="Optimize the following task specifically for ChatGPT. "+c.instruction;
    }
    // Final exact-body duplicate guard. This is the only automatic text-based removal.
    HashSet<String> seen=new HashSet<>();it=all.iterator();while(it.hasNext()){Cmd c=it.next();String k=normalizePrompt(c.instruction);if(!seen.add(k))it.remove();}
  }

  void applyChatGPTNativeFinal(){
    try{
      JSONObject pack=new JSONObject(readAsset("chatgpt_native_final.json"));
      HashSet<Integer> remove=new HashSet<>();JSONArray rr=pack.optJSONArray("remove_ids");if(rr!=null)for(int i=0;i<rr.length();i++)remove.add(rr.optInt(i));
      HashMap<Integer,JSONObject> edits=new HashMap<>();JSONArray oo=pack.optJSONArray("overrides");if(oo!=null)for(int i=0;i<oo.length();i++){JSONObject o=oo.optJSONObject(i);if(o!=null)edits.put(o.optInt("match_id",-1),o);}
      Iterator<Cmd> it=all.iterator();while(it.hasNext()){
        Cmd c=it.next();if(c.custom)continue;if(remove.contains(c.id)){it.remove();continue;}JSONObject o=edits.get(c.id);if(o==null)continue;
        if(o.has("command")){String n=Cmd.clean(o.optString("command",c.command));if(!n.isEmpty())c.command=n;}
        if(o.has("description")){String d=o.optString("description",c.description).trim();if(!d.isEmpty())c.description=d;}
        if(o.has("instruction")){String x=o.optString("instruction",c.instruction).trim();if(!x.isEmpty())c.instruction=x;}
      }
      HashSet<String> seen=new HashSet<>();it=all.iterator();while(it.hasNext()){Cmd c=it.next();if(c.custom)continue;String k=normalizePrompt(c.instruction);if(!seen.add(k))it.remove();}
      int built=0;for(Cmd c:all)if(!c.custom)built++;int expected=pack.optInt("expected_builtin_count",-1);if(expected>0&&built!=expected)throw new RuntimeException("Canonical prompt count "+built+" != "+expected);
    }catch(Exception e){throw new RuntimeException("ChatGPT-native final pack failed",e);}
  }

  void applyProposalTaxonomy(){
    for(Cmd c:all){
      if(c.custom)continue;
      String old=(c.category+" "+c.subcategory).toLowerCase(Locale.ROOT);
      String meta=(c.command+" "+c.description+" "+old).toLowerCase(Locale.ROOT);
      String cat;
      if(old.contains("images & visuals")||old.contains("photo")||hasAny(meta,"image generation","image editing","photo editing","portrait","headshot","background removal","sdxl","midjourney","poster image","visual preset"))cat="Images & Design";
      else if(old.contains("health & lifestyle")||hasAny(meta,"health","medical","medicine","wellness","fitness","nutrition","diet","mental health","habit","relationship","travel","lifestyle"))cat="Health & Life";
      else if(old.contains("science & education")||hasAny(meta,"study plan","quiz","flashcard","tutor","teaching","lesson","stem","physics","chemistry","biology","mathematics","academic learning"))cat="Learning & Education";
      else if(old.contains("technology & development")||hasAny(meta,"coding","developer","programming","software","debug","api","database","sql","devops","cloud","cybersecurity","linux","android","ios","prompt engineering","ai prompting","agent workflow"))cat="Technology & Data";
      else if(old.contains("career & business")||hasAny(meta,"resume","cv ","cover letter","interview","career","job search","meeting","workplace","business strategy","marketing","sales","finance","entrepreneur","customer","brand strategy"))cat="Work & Business";
      else if(old.contains("productivity & planning")||hasAny(meta,"roadmap","project plan","action plan","checklist","workflow","timeline","priority","prioritize","decision","trade-off","tradeoff","compare options","recommend the best","organize"))cat="Planning & Decisions";
      else if(old.contains("creativity & design")||hasAny(meta,"brainstorm","creative writing","storytelling","story ","script","social media","caption","reel","content idea","creative direction"))cat="Creativity & Content";
      else if(old.contains("writing & content")||hasAny(meta,"rewrite","proofread","grammar","translate","email","copywriting","article","blog","tone","paraphrase","clarify writing"))cat="Writing & Communication";
      else cat="Research & Analysis";
      c.category=cat;
      c.subcategory=taxonomySubcategoryV12(c,cat);
    }
  }
  boolean hasAny(String h,String...xs){for(String x:xs)if(h.contains(x))return true;return false;}
  String proposalSubcategory(Cmd c,String cat){return taxonomySubcategoryV12(c,cat);}

  void load(){
    all.clear();
    try{
      synchronized(BUILTIN_CACHE_V15){
        if(!BUILTIN_CACHE_READY_V15){
          JSONArray a=new JSONArray(readAsset("final_catalog_v15.json"));
          BUILTIN_CACHE_V15.clear();
          for(int i=0;i<a.length();i++)BUILTIN_CACHE_V15.add(new Cmd(a.getJSONObject(i),false));
          BUILTIN_CACHE_READY_V15=true;
        }
        all.addAll(BUILTIN_CACHE_V15);
      }
      JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));
      for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}
    }catch(Exception e){throw new RuntimeException(e);}
  }
  boolean containsAnyV15(String x,String... terms){
    if(x==null)return false;String z=x.toLowerCase(Locale.ROOT);
    for(String t:terms)if(z.contains(t))return true;
    return false;
  }
  boolean externalModelCommandV15(Cmd c){
    String x=(c.command==null?"":c.command)+" "+(c.description==null?"":c.description);
    return containsAnyV15(x,"midjourney","claude","anthropic","gemini","grok","deepseek","mistral","copilot","perplexity");
  }
  boolean externalRuntimePromptV15(Cmd c){
    String x=c.instruction==null?"":c.instruction.toLowerCase(Locale.ROOT);
    String[] models={"midjourney","claude","anthropic","gemini","grok","deepseek","mistral","copilot","perplexity"};
    String[] verbs={"use ","invoke ","run ","open ","send to ","format for ","optimized for ","prompt for "};
    for(String model:models)for(String verb:verbs)if(x.contains(verb+model)||x.contains(verb+"the "+model))return true;
    return x.contains("claude.md")||x.contains("skill.md")||x.contains("gemini cli")||x.contains("anthropic console");
  }
  String cleanPromptBodyV15(String x){
    if(x==null)return "";String y=x.trim();
    String prefix="For this step in a larger workflow:";
    if(y.regionMatches(true,0,prefix,0,prefix.length()))y=y.substring(prefix.length()).trim();
    String suffix="Apply these instructions only to this step. Do not override or block later steps in the PromptDeck stack.";
    int si=y.toLowerCase(Locale.ROOT).lastIndexOf(suffix.toLowerCase(Locale.ROOT));
    if(si>=0&&y.substring(si).trim().equalsIgnoreCase(suffix))y=y.substring(0,si).trim();
    StringBuilder out=new StringBuilder(y.length());int p=0;
    while(p<=y.length()){
      int n=y.indexOf('\n',p);if(n<0)n=y.length();String line=y.substring(p,n);String low=line.trim().toLowerCase(Locale.ROOT);
      if(!(low.startsWith("name:")||low.startsWith("version:")||low.startsWith("author:")||low.startsWith("changelog:"))){
        if(out.length()>0)out.append('\n');out.append(line);
      }
      if(n==y.length())break;p=n+1;
    }
    return out.toString().trim();
  }
  String dedupKeyV15(String x){
    if(x==null)return "";StringBuilder b=new StringBuilder(Math.min(x.length(),4096));boolean gap=false;
    for(int i=0;i<x.length();i++){
      char ch=Character.toLowerCase(x.charAt(i));
      if(Character.isLetterOrDigit(ch)){if(gap&&b.length()>0)b.append(' ');b.append(ch);gap=false;}
      else gap=true;
    }
    return b.toString();
  }
  void finalCatalogCleanupV15(){
    HashSet<String> seen=new HashSet<>();Iterator<Cmd> it=all.iterator();
    while(it.hasNext()){
      Cmd c=it.next();if(c.custom)continue;
      if(externalModelCommandV15(c)||externalRuntimePromptV15(c)){it.remove();continue;}
      c.instruction=cleanPromptBodyV15(c.instruction);
      if(c.instruction.length()<8){it.remove();continue;}
      String k=dedupKeyV15(c.instruction);if(!seen.add(k))it.remove();
    }
  }
  void showStartupV15(){
    LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setGravity(Gravity.CENTER);box.setBackgroundColor(BG);box.setPadding(dp(28),dp(28),dp(28),dp(28));
    TextView brand=text("PromptDeck",28,true,TEXT);brand.setGravity(Gravity.CENTER);box.addView(brand);
    TextView sub=text("Loading your prompt library…",13,false,MUTED);sub.setGravity(Gravity.CENTER);sub.setPadding(0,dp(12),0,0);box.addView(sub);setContentView(box);
  }
  void restoreWorkspaceV15(Bundle b){
    if(b==null)return;
    discoverMode=b.getString("v15_mode",discoverMode);askGoal=b.getString("v15_goal",askGoal);askCapability=b.getString("v15_cap",askCapability);askSelectionGoal=b.getString("v15_selection_goal",askSelectionGoal);contextDraft=b.getString("v15_context",contextDraft);
    discoverCategory=b.getString("v15_cat",discoverCategory);discoverSubcategory=b.getString("v15_sub",discoverSubcategory);discoverPreset=b.getString("v15_query",discoverPreset);discoverFavorites=b.getBoolean("v15_fav",discoverFavorites);browseLimit=b.getInt("v15_limit",browseLimit);
    ArrayList<Integer> ids=b.getIntegerArrayList("v15_selected");if(ids!=null){selected.clear();for(Integer id:ids){for(Cmd c:all)if(c.id==id){selected.add(c);break;}}}
  }
  void consumeIncomingShareV15(){
    Intent in=getIntent();if(in==null||!Intent.ACTION_SEND.equals(in.getAction())||!"text/plain".equals(in.getType()))return;
    String t=in.getStringExtra(Intent.EXTRA_TEXT);if(t==null||t.trim().isEmpty())return;
    contextDraft=t.trim();askGoal=contextDraft;discoverMode="ask";
  }
  void loadCommunityPrompts(){
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

  void loadImportedPdfPrompts(){
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

  void loadDailyGapPrompts(){
    try{
      JSONArray a=new JSONArray(readAsset("daily_gap_prompts_100.json"));
      HashSet<String> seen=new HashSet<>();
      for(Cmd c:all)seen.add(normalizePrompt(c.instruction));
      for(int i=0;i<a.length();i++){
        JSONObject x=a.getJSONObject(i);
        String raw=x.optString("command","").trim(),prompt=x.optString("instruction","").trim();
        if(raw.isEmpty()||prompt.isEmpty())continue;
        String norm=normalizePrompt(prompt);if(seen.contains(norm))continue;
        String command=Cmd.clean(raw),base=command;int n=2;while(find(command)!=null)command=base+(n++);
        JSONObject o=new JSONObject(x.toString());o.put("command",command);
        try{all.add(new Cmd(o,false));seen.add(norm);}catch(Exception ignored){}
      }
    }catch(Exception ignored){}
  }

  String normalizePrompt(String s){return s==null?"":s.replaceAll("\\s+"," ").trim().toLowerCase(Locale.ROOT);}

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

  void loadCuratedPhotoPrompts(){
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

  void seedPhotoCommands(){
    String[][] defs=new String[][]{
      {"NeonCity","Cyberpunk night portrait"},{"GoldenHour","Cinematic sunset portrait"},{"MiniWorld","Miniature diorama"},{"Fog","Mysterious foggy portrait"},{"LuxuryAd","Luxury product advertisement"},{"LowAngleHero","Powerful hero photograph"},{"VintageFilm","Authentic 1990s photograph"},{"DroneView","Dramatic top-down photograph"},{"Magazine","Fashion editorial photograph"},{"RainyNight","Moody movie scene"},{"ProHeadshot","LinkedIn-ready headshot"},{"SnowWorld","Winter travel photograph"},{"DoubleExposure","Artistic poster portrait"},{"OldMoney","Luxury lifestyle portrait"},{"StudioPro","Professional studio portrait"},{"Autumn","Beautiful autumn portrait"},{"MovieScene","Cinematic movie still"}
    };
    for(String[] d:defs){if(find(d[0])!=null)continue;try{JSONObject o=new JSONObject();o.put("id",20000+all.size());o.put("command",d[0]);o.put("category","Photo Editing & Image Generation");o.put("description",photoDescription(d[1]));o.put("instruction","Use the /"+d[0]+" image direction: "+d[1]+". Apply this style faithfully to the user's image request while preserving any identity, subject, composition, or content constraints they provide.");all.add(new Cmd(o,false));}catch(Exception ignored){}}
  }

  String photoDescription(String shortText){
    return shortText+" — ready-made visual preset for a consistent style while preserving the subject and request.";
  }

  String autoDescription(String prompt,String category){
    if(prompt==null)return "Custom prompt";
    String t=prompt.replaceAll("\\s+"," ").trim();
    t=t.replaceAll("(?i)^(please\\s+|create\\s+|generate\\s+|make\\s+|use\\s+|turn\\s+this\\s+into\\s+)","");
    String lower=t.toLowerCase(Locale.ROOT);
    if(category.toLowerCase(Locale.ROOT).contains("photo")){
      String kind="Photo editing preset";
      if(lower.contains("portrait"))kind="Portrait style";
      else if(lower.contains("product"))kind="Product photography style";
      else if(lower.contains("cinematic")||lower.contains("movie"))kind="Cinematic image style";
      else if(lower.contains("headshot"))kind="Professional headshot style";
      else if(lower.contains("landscape")||lower.contains("travel"))kind="Travel photography style";
      String detail=t;
      int cut=detail.indexOf('.');if(cut>18)detail=detail.substring(0,cut);
      if(detail.length()>72)detail=detail.substring(0,72).trim()+"…";
      return kind+" — "+detail;
    }
    String first=t;int cut=first.indexOf('.');if(cut>15)first=first.substring(0,cut);if(first.length()>86)first=first.substring(0,86).trim()+"…";return first.isEmpty()?"Custom prompt":first;
  }

  void seedExtraPhotoCommands(){
    String[][] defs=new String[][]{
      {"hdreal","HD Real","/hdreal\nCreate a highly realistic, sharply captured version of the supplied image. Recover believable micro-detail, texture, depth and natural contrast while preserving the exact subject identity, face, pose, framing and scene geometry."},
      {"cinematicportrait","Cinematic Portrait","/cinematicportrait\nTransform the supplied portrait into a cinematic movie still with controlled dramatic lighting, dimensional contrast, realistic skin and strong subject separation. Preserve the person's exact identity, expression, pose and composition."},
      {"doubleexposureviral","Double Exposure","/doubleexposureviral\nCreate a polished double-exposure portrait that blends the subject with a complementary city or environmental story layer. Preserve the subject's recognizable face/profile and keep the composite coherent, photographic and intentional."},
      {"Travelstory","Travel Story","/Travelstory\nTurn the supplied travel photograph into a warm visual travel-story frame with cinematic natural light, stronger atmosphere and narrative depth while preserving the actual subject, vehicle and location structure."},
      {"storymytravel","Rainy Travel Story","/storymytravel\nRestyle the supplied travel image as an atmospheric rainy-night travel story with realistic wet surfaces, reflections, depth and moody practical lighting while keeping the original subject and scene recognizable."},
      {"cinematicTravel","Cinematic Travel","/cinematicTravel\nCreate a cinematic travel photograph from the supplied image using dramatic natural light, filmic contrast, atmospheric depth and premium travel-editorial treatment while preserving the original scene and subject."},
      {"documentrytravel","Documentary Travel","/documentrytravel\nRender the supplied travel image as believable documentary travel photography: natural light, observational composition, realistic texture and restrained processing. Preserve scene authenticity and avoid artificial glamour."},
      {"Travelvlog","Travel Vlog","/Travelvlog\nTurn the supplied image into a polished travel-vlog frame with inviting golden-hour light, vivid but realistic detail and social-ready storytelling while preserving the original subject and location."},
      {"FixFaceResolution","Fix Face Resolution","/FixFaceResolution\nRestore and humanise this image in one pass. Reconstruct lost detail from soft or degraded areas, rebuild sharp edges and fine texture, recover hair strand and iris definition. Then remove all artificial AI smoothness, add visible pores, natural skin unevenness, peach fuzz catching light, subtle blemishes and realistic colour variation. Result should read as a sharply captured real photograph. Keep the exact same face, expression, angle, lighting and composition."}
    };
    for(String[] d:defs){
      if(find(d[0])!=null)continue;
      try{
        JSONObject o=new JSONObject();
        o.put("id",24000+all.size());
        o.put("command",d[0]);
        o.put("category","Photo Editing & Image Generation");
        o.put("description",photoDescription(d[1]));
        o.put("instruction",d[2]);
        all.add(new Cmd(o,false));
      }catch(Exception ignored){}
    }
  }

  void englishizeDescriptions(){
    for(Cmd c:all){
      String d=englishDescription(c.command);
      if(d!=null&&!d.isEmpty())c.description=d;
      else if(containsArabic(c.description))c.description=c.custom?"Custom prompt — imported instruction":"Prompt tool for this task";
    }
  }

  boolean containsArabic(String x){return x!=null&&x.matches(".*[\\u0600-\\u06FF].*");}

  String englishDescription(String command){
    if(command==null)return null;String k=command.toLowerCase(Locale.ROOT);
    HashMap<String,String> m=new HashMap<>();
    String[][] d=new String[][]{
      {"eli5","Explains something in very simple, beginner-friendly terms"},{"summarize","Condenses text into the most important points"},{"rewrite","Rewrites text while preserving its meaning"},{"humanize","Makes AI-sounding text feel natural and human"},{"simplify","Makes complex wording easier to understand"},{"brainstorm","Generates a wide range of useful ideas"},{"ideas","Suggests fresh ideas and directions"},{"hook","Creates a strong opening that captures attention"},{"professional","Makes writing polished and professional"},{"translate","Translates text accurately into another language"},{"explain","Explains a topic clearly and thoroughly"},{"steps","Turns an explanation or task into clear steps"},{"critique","Identifies weaknesses, risks and ways to strengthen an idea"},{"improve","Improves the quality of the current result"},{"compare","Compares options using consistent criteria"},{"proscons","Lists meaningful advantages and disadvantages"},{"examples","Provides practical examples"},{"analogy","Explains an idea through a simple analogy"},{"shorten","Makes text shorter without losing the core meaning"},{"expand","Develops an idea with useful additional detail"},{"caption","Writes an engaging caption"},{"script","Turns an idea into a structured script"},{"carousel","Turns content into a social-media carousel"},{"reel","Turns an idea into a short-form reel concept"},{"viral","Suggests a more shareable, high-engagement version"},{"cta","Creates a clear call to action"},{"story","Turns information into a compelling story"},{"headline","Creates a strong headline"},{"angles","Suggests different creative or strategic angles"},{"alternative","Suggests viable alternatives"},{"plan","Turns a goal into a practical plan"},{"strategy","Builds a strategy around the objective"},{"roadmap","Creates a staged roadmap from now to the goal"},{"checklist","Turns work into a clear checklist"},{"todo","Extracts concrete tasks and to-dos"},{"priority","Ranks what matters most"},{"workflow","Organizes a repeatable workflow"},{"timeline","Arranges events or work in chronological order"},{"action","Turns analysis into executable actions"},{"template","Creates a reusable template"},{"study","Turns material into a study-friendly format"},{"quiz","Creates questions to test understanding"},{"flashcards","Creates concise review flashcards"},{"teach","Teaches the topic progressively"},{"hint","Provides a useful hint without giving away the full answer"},{"test","Creates a practice test"},{"review","Reviews information for understanding and gaps"},{"memorize","Creates techniques to help remember information"},{"mistakes","Finds common or likely mistakes"},{"research","Researches a question systematically"},{"verify","Checks important claims and flags uncertainty"},{"sources","Finds or requests reliable sources"},{"deepdive","Explores a topic in depth"},{"evidence","Looks for evidence supporting or challenging a claim"},{"facts","Extracts the most important factual information"},{"insights","Extracts useful insights and implications"},{"trends","Identifies important patterns and trends"},{"data","Extracts or organizes important data"},{"summary","Produces a focused executive summary"},{"grammar","Corrects grammar and language errors"},{"proofread","Proofreads text for clarity, correctness and consistency"},{"paraphrase","Rephrases text using different wording"},{"rephrase","Rewrites a sentence or passage in a new way"},{"polish","Refines wording, flow and overall quality"},{"clarify","Makes vague or confusing text clearer"},{"tone","Changes the tone while preserving the message"},{"formal","Makes writing more formal"},{"casual","Makes writing more natural and conversational"},{"arabic","Converts or adapts text into Arabic"},{"email","Writes a polished email"},{"reply","Drafts an appropriate reply"},{"followup","Writes a professional follow-up message"},{"request","Writes a clear, respectful request"},{"apology","Writes an appropriate apology"},{"resume","Improves resume content and positioning"},{"coverletter","Writes a targeted cover letter"},{"interview","Prepares interview questions and answers"},{"meeting","Helps prepare for a meeting"},{"minutes","Summarizes meeting minutes and actions"},{"rank","Ranks options by defined criteria"},{"recommend","Recommends the strongest option with trade-offs"},{"challenge","Challenges assumptions and weak reasoning"},{"devilsadvocate","Argues the strongest opposing case"},{"blindspots","Finds important blind spots you may have missed"},{"check","Reviews the final result for issues"},{"debug","Diagnoses errors and likely causes"},{"fix","Proposes a direct fix for the problem"},{"optimize","Improves performance, efficiency or quality"},{"better","Suggests a stronger version of the current result"},{"table","Converts information into a clear table"},{"bullets","Converts content into concise bullet points"},{"outline","Builds a logical outline"},{"format","Reformats content for readability or a target structure"},{"json","Structures information as JSON"},{"csv","Structures tabular information as CSV"},{"schema","Defines a clear data or output schema"},{"acceptance","Turns requirements into testable acceptance criteria"},{"requirements","Extracts functional and non-functional requirements"},{"spec","Writes a concise implementation specification"},{"prompt","Designs a stronger prompt for the same task"},{"assumptions","Surfaces assumptions that should be tested"},{"firstprinciples","Breaks the problem down from first principles"},{"counterexample","Looks for counterexamples that challenge the current idea"},{"socratic","Uses Socratic questions to improve reasoning"},{"tradeoffs","Makes the important trade-offs explicit"},{"decision","Structures a decision using evidence and constraints"},{"extract","Extracts the requested information from content"},{"classify","Classifies information into useful categories"},{"constraints","Identifies constraints that shape the solution"},{"risks","Identifies risks, likelihood and impact"},{"estimate","Produces a reasoned estimate with assumptions"},{"rootcause","Investigates the underlying root cause"},{"edgecases","Finds edge cases and failure scenarios"},{"refactor","Improves structure without changing intended behavior"},{"tests","Designs useful tests and validation cases"},{"security","Reviews security risks and weaknesses"},{"rubric","Creates a scoring rubric"},{"score","Scores a result against defined criteria"},
      {"neoncity","Cyberpunk night portrait preset"},{"goldenhour","Cinematic golden-hour portrait preset"},{"miniworld","Miniature diorama image preset"},{"fog","Atmospheric fog and mystery preset"},{"luxuryad","Premium luxury product-advertising preset"},{"lowanglehero","Powerful low-angle hero photography preset"},{"vintagefilm","Authentic vintage film photography preset"},{"droneview","Dramatic top-down aerial photography preset"},{"magazine","Fashion editorial photography preset"},{"rainynight","Moody rainy-night cinematic preset"},{"proheadshot","Professional headshot preset"},{"snowworld","Winter travel photography preset"},{"doubleexposure","Artistic double-exposure portrait preset"},{"oldmoney","Refined old-money lifestyle portrait preset"},{"studiopro","Professional studio portrait preset"},{"autumn","Warm autumn portrait preset"},{"moviescene","Cinematic movie-still preset"},{"hdreal","High-definition realistic image enhancement preset"},{"cinematicportrait","Cinematic portrait transformation preset"},{"doubleexposureviral","High-impact double-exposure visual preset"},{"travelstory","Cinematic travel-story photography preset"},{"storymytravel","Atmospheric rainy travel-story preset"},{"cinematictravel","Premium cinematic travel photography preset"},{"documentrytravel","Natural documentary travel photography preset"},{"travelvlog","Social-ready travel-vlog photography preset"},{"fixfaceresolution","Restores facial detail and natural photographic texture"}
    };
    for(String[] a:d)m.put(a[0],a[1]);return m.get(k);
  }

  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);root=vbox();root.setPadding(dp(14),dp(8),dp(14),dp(18));sv.addView(root);shell.addView(sv,new LinearLayout.LayoutParams(-1,0,1));if(!selected.isEmpty())shell.addView(selectionBar(),new LinearLayout.LayoutParams(-1,dp(56)));setContentView(shell);sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();if(top>0)root.setPadding(dp(14),Math.max(dp(8),top+dp(3)),dp(14),dp(18));return insets;});LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.promptdeck_mark);mark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(30),dp(30));mp.setMargins(0,0,dp(7),0);top.addView(mark,mp);top.addView(text("PromptDeck",18,true,TEXT),new LinearLayout.LayoutParams(0,dp(32),1));TextView more=text("⋯",24,true,TEXT);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showMoreMenu());top.addView(more,new LinearLayout.LayoutParams(dp(38),dp(36)));root.addView(top);spacer(9);
  }

  void home(){
    page="home";currentGroup=null;base("","",false);
    if("landing".equals(discoverMode)){TextView h=text("How do you want to start?",23,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Let PromptDeck choose the best approach, or explore all prompts yourself.",11,false,MUTED);sub.setPadding(0,0,0,dp(10));root.addView(sub);View ask=modeChoiceCard(R.drawable.pd_mode_ask,"Ask PromptDeck","Describe your goal and get the best prompt or workflow automatically.",ACCENT,()->{discoverMode="ask";home();});root.addView(ask);View browse=modeChoiceCard(R.drawable.pd_mode_browse,"Browse all prompts","Search and explore the complete "+String.format(Locale.US,"%,d",BUILTIN_CACHE_V15.size())+"-prompt library yourself.",Color.rgb(45,203,140),()->{discoverMode="browse";home();});root.addView(browse);TextView hint=text("You can switch modes anytime. Your selected prompts stay in your workflow.",9,false,TERTIARY);hint.setGravity(Gravity.CENTER);hint.setPadding(dp(6),dp(10),dp(6),0);root.addView(hint);return;}
    root.addView(modeSwitch());spacer(8);
    if("ask".equals(discoverMode)){TextView h=text("What do you want ChatGPT to help you do?",20,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Describe the outcome. PromptDeck will choose the strongest prompt or build a short workflow.",10,false,MUTED);sub.setPadding(0,0,0,dp(8));root.addView(sub);EditText goal=input("e.g. Compare two cars and recommend the better one for me...",3);goal.setMaxLines(5);goal.setImeOptions(EditorInfo.IME_ACTION_DONE);goal.setText(askGoal);root.addView(goal);Button find=primary("Find the best approach");root.addView(find);HorizontalScrollView examples=new HorizontalScrollView(this);examples.setHorizontalScrollBarEnabled(false);LinearLayout ex=hbox();String[] xs={"Compare options","Write an email","Plan a project","Explain a topic"};for(String x:xs){Button b=filterChip(x,false);b.setOnClickListener(v->{goal.setText(x);goal.setSelection(goal.length());});ex.addView(b);}examples.addView(ex);root.addView(examples);LinearLayout results=vbox();root.addView(results);if(!askGoal.isEmpty())renderAskResults(results,askGoal);find.setOnClickListener(v->runAskRecommendation(results,goal));goal.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){runAskRecommendation(results,goal);return true;}return false;});return;}
    TextView h=text("Browse all prompts",20,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Search directly, or narrow the full library by category.",10,false,MUTED);sub.setPadding(0,0,0,dp(7));root.addView(sub);EditText q=input("Search prompts...",1);q.setSingleLine(true);q.setText(discoverPreset);root.addView(q);LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);if(!discoverCategory.isEmpty()){Button subcat=filterChip(discoverSubcategory.isEmpty()?"All subcategories":discoverSubcategory,!discoverSubcategory.isEmpty());subcat.setOnClickListener(v->showSubcategoryPickerV12());filters.addView(subcat);}Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverPreset=q.getText().toString();browseLimit=30;home();});filters.addView(fav);if(!discoverCategory.isEmpty()||!discoverSubcategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});filters.addView(clear);}root.addView(filters);LinearLayout results=vbox();root.addView(results);renderBrowseResultsV6(results,q.getText().toString());q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();browseLimit=30;renderBrowseResultsV6(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }

  void addGoalCard(String icon,String title,String sub,String baseQuery,String...refiners){
    View c=menuCard(icon,title,sub);c.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));root.addView(c);
  }

  void addCollectionCard(String icon,String title,String sub,String baseQuery,String...refiners){
    View c=menuCard(icon,title,sub);c.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));root.addView(c);
  }

  void browseCategories(){discoverMode="browse";home();}

  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){discoverMode="ask";askGoal=(baseQuery==null?"":baseQuery)+(active==null?"":" "+active);home();}

  void renderSmartSearch(LinearLayout target,String query){
    target.removeAllViews();String q=query==null?"":query.trim();
    if(q.length()<2){target.setVisibility(View.GONE);return;}
    target.setVisibility(View.VISIBLE);ArrayList<Cmd> ranked=rankSmart(q,12);
    if(ranked.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No strong matches yet. Try describing the outcome you want.",13,false,MUTED);e.setPadding(0,dp(12),0,dp(12));empty.addView(e);target.addView(empty);return;}
    TextView best=text("BEST MATCH",10,true,ACCENT);best.setLetterSpacing(.12f);best.setPadding(0,dp(10),0,dp(6));target.addView(best);
    LinearLayout box=vbox();box.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));box.setElevation(dp(2));
    for(int i=0;i<ranked.size();i++){Cmd c=ranked.get(i);View row=commandRow(c,i<ranked.size()-1);row.setOnClickListener(v->detail(c,groupFor(c)));box.addView(row);}target.addView(box);
  }

  void renderRanked(LinearLayout target,ArrayList<Cmd> ranked){
    if(ranked.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No strong matches in this collection.",13,false,MUTED);e.setPadding(0,dp(16),0,dp(16));empty.addView(e);target.addView(empty);return;}
    LinkedHashMap<String,ArrayList<Cmd>> buckets=new LinkedHashMap<>();
    for(Cmd c:ranked){String cat=c.category;if(!buckets.containsKey(cat))buckets.put(cat,new ArrayList<>());buckets.get(cat).add(c);}
    int shown=0;for(Map.Entry<String,ArrayList<Cmd>> en:buckets.entrySet()){
      if(shown>=30)break;target.addView(section(en.getKey(),en.getValue().size()));LinearLayout box=vbox();box.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));box.setElevation(dp(2));
      for(int i=0;i<en.getValue().size();i++){Cmd c=en.getValue().get(i);View row=commandRow(c,i<en.getValue().size()-1);row.setOnClickListener(v->detail(c,groupFor(c)));box.addView(row);shown++;}target.addView(box);spacer(4);
    }
  }

  ArrayList<Cmd> rankSmart(String query,int limit){
    final String expanded=expandIntent(query==null?"":query);final String[] toks=expanded.toLowerCase(Locale.ROOT).split("\\s+");ArrayList<Cmd> candidates=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();
    for(Cmd c:all){int score=fastSmartScore(c,toks);if(score>0){candidates.add(c);scores.put(c,score);}}
    Collections.sort(candidates,(a,b)->{int sa=scores.get(a),sb=scores.get(b);if(sa!=sb)return Integer.compare(sb,sa);return displayTitle(a).compareToIgnoreCase(displayTitle(b));});
    if(candidates.size()<=limit)return candidates;return new ArrayList<>(candidates.subList(0,limit));
  }

  int smartScore(Cmd c,String query){
    String raw=query==null?"":query.toLowerCase(Locale.ROOT).trim();String expanded=expandIntent(raw);String title=displayTitle(c).toLowerCase(Locale.ROOT),desc=shortDescription(c).toLowerCase(Locale.ROOT),meta=(c.category+" "+c.subcategory).toLowerCase(Locale.ROOT),body=c.instruction.toLowerCase(Locale.ROOT);HashSet<String> original=meaningfulQueryTerms(raw),extra=meaningfulQueryTerms(expanded);int score=0,matched=0,anchors=0,anchorMatched=0;
    if(raw.length()>3&&title.contains(raw))score+=80;if(raw.length()>3&&desc.contains(raw))score+=45;
    for(String t:original){boolean hit=false;if(title.contains(t)){score+=22;hit=true;}else if(desc.contains(t)){score+=13;hit=true;}else if(meta.contains(t)){score+=9;hit=true;}else if(body.contains(t)){score+=2;hit=true;}if(hit)matched++;if(t.length()>=6&&!genericSearchTerm(t)){anchors++;if(hit)anchorMatched++;}}
    for(String t:extra){if(original.contains(t))continue;if(title.contains(t))score+=4;else if(desc.contains(t))score+=2;else if(meta.contains(t))score+=1;}
    score+=matched*matched*7;if(!original.isEmpty()&&matched==original.size())score+=45;if(anchors>0&&anchorMatched==0)score-=55;if(raw.contains("marketing")&&meta.contains("marketing"))score+=30;if(raw.contains("career")&&meta.contains("career"))score+=25;if(raw.contains("image")&&meta.contains("image"))score+=25;if(recentIdSet().contains(c.id))score+=2;return score;
  }

  int fastSmartScore(Cmd c,String[] toks){
    String command=c.command==null?"":c.command.toLowerCase(Locale.ROOT);String title=displayTitle(c).toLowerCase(Locale.ROOT);String desc=c.description==null?"":c.description.toLowerCase(Locale.ROOT);String cat=c.category==null?"":c.category.toLowerCase(Locale.ROOT);String sub=c.subcategory==null?"":c.subcategory.toLowerCase(Locale.ROOT);int score=0,matched=0;
    for(String t:toks){if(t==null||t.length()<2)continue;boolean hit=false;if(command.equals(t)){score+=16;hit=true;}else if(command.contains(t)){score+=9;hit=true;}if(title.contains(t)){score+=11;hit=true;}if(desc.contains(t)){score+=6;hit=true;}if(cat.contains(t)){score+=5;hit=true;}if(sub.contains(t)){score+=3;hit=true;}if(hit)matched++;}
    if(matched>=2)score+=matched*4;if(recentIdSet().contains(c.id))score+=2;return score;
  }
  void hideKeyboard(View v){try{android.view.inputmethod.InputMethodManager imm=(android.view.inputmethod.InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);if(imm!=null)imm.hideSoftInputFromWindow(v.getWindowToken(),0);}catch(Exception ignored){}}
  void runAskRecommendation(LinearLayout target,EditText goal){String next=goal.getText().toString().trim();if(next.length()<2){toast("Describe what you want first");return;}if(!next.equals(askGoal))askCapability="";askGoal=next;contextDraft=askGoal;hideKeyboard(goal);try{renderAskResultsV8(target,askGoal);}catch(Exception e){target.removeAllViews();LinearLayout box=surface(true);TextView title=text("Couldn't build a recommendation",12,true,TEXT);TextView sub=text("Try a more specific description, or switch to Browse prompts.",10,false,MUTED);title.setPadding(0,dp(8),0,dp(2));sub.setPadding(0,0,0,dp(8));box.addView(title);box.addView(sub);target.addView(box);}}

  String expandIntent(String query){
    String q=query==null?"":query.toLowerCase(Locale.ROOT);StringBuilder x=new StringBuilder(q);
    String[][] syn={
      {"buy","compare recommend decision research product value"},{"choose","compare recommend decision rank tradeoffs"},{"car","vehicle automotive compare buy"},{"photo","image portrait edit enhance restore style"},{"picture","image photo edit enhance"},{"fix","debug troubleshoot rootcause repair"},{"problem","debug diagnose troubleshoot rootcause"},{"write","rewrite writing professional text"},{"email","email reply professional followup"},{"learn","explain teach study examples quiz"},{"understand","explain simplify examples analogy"},{"research","research verify sources evidence deepdive"},{"decide","decision compare recommend tradeoffs rank"},{"ideas","brainstorm ideas angles alternative"},{"plan","plan roadmap checklist workflow timeline"},{"code","coding debug refactor tests architecture technical"},{"resume","resume career cv interview"},{"social","content caption hook script reel carousel"},{"summarise","summarize summary"},{"summary","summarize extract keypoints"}
    };
    for(String[] s:syn)if(q.contains(s[0]))x.append(' ').append(s[1]);return x.toString();
  }

  Group groupFor(Cmd c){for(Group g:groups)if(g.title.equalsIgnoreCase(c.category))return g;return groups[0];}

  void rememberRecent(Cmd c){
    ArrayList<Integer> ids=new ArrayList<>();ids.add(c.id);for(Integer id:recentIds())if(id!=c.id&&ids.size()<8)ids.add(id);StringBuilder b=new StringBuilder();for(Integer id:ids){if(b.length()>0)b.append(',');b.append(id);}getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString("recent_prompt_ids",b.toString()).apply();
  }

  ArrayList<Integer> recentIds(){ArrayList<Integer> out=new ArrayList<>();String raw=getSharedPreferences(PREFS,MODE_PRIVATE).getString("recent_prompt_ids","");for(String x:raw.split(","))try{if(!x.trim().isEmpty())out.add(Integer.parseInt(x.trim()));}catch(Exception ignored){}return out;}
  HashSet<Integer> recentIdSet(){return new HashSet<>(recentIds());}
  Cmd findById(int id){for(Cmd c:all)if(c.id==id)return c;return null;}
  ArrayList<Cmd> recentCommands(){ArrayList<Cmd> out=new ArrayList<>();for(Integer id:recentIds()){Cmd c=findById(id);if(c!=null)out.add(c);if(out.size()>=4)break;}return out;}

  View groupCard(Group g){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(8),dp(7));int accent=groupAccent(g);ImageView icon=vectorTile(groupIconRes(g),accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(icon,ip);LinearLayout copy=vbox();TextView title=text(g.title,13,true,TEXT);TextView sub=text(g.sub,9,false,MUTED);sub.setMaxLines(1);copy.addView(title);copy.addView(sub);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView count=text(String.valueOf(groupCount(g)),9,false,TERTIARY);count.setPadding(dp(6),0,dp(5),0);card.addView(count);card.addView(text("›",20,false,TERTIARY));return card;}
  View menuCard(String icon,String title,String sub){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(8),dp(7));TextView ic=iconTile(icon,ACCENT);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));TextView d=text(sub,9,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",20,false,TERTIARY));return card;
  }

  void group(Group g){group(g,null,"");}

  void group(Group g,String activeSub,String initialQuery){discoverMode="browse";discoverCategory=g==null?"":g.title;discoverPreset=initialQuery==null?"":initialQuery;browseLimit=30;home();}

  ArrayList<Cmd> groupCommands(Group g){
    ArrayList<Cmd> out=new ArrayList<>();for(Cmd c:all)if(c.category.equalsIgnoreCase(g.title))out.add(c);return out;
  }

  String groupSubcategory(Cmd c,Group g){
    if(c.subcategory!=null&&!c.subcategory.trim().isEmpty())return c.subcategory.trim();
    if(c.custom)return"Custom";
    return subcat(c.command,g.title);
  }

  int groupCount(Group g){return groupCommands(g).size();}

  Button filterChip(String label,boolean active){
    Button b=new Button(this);b.setAllCaps(false);b.setText(label);b.setTextSize(9);b.setTextColor(active?Color.WHITE:MUTED);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));b.setSingleLine(true);b.setMinWidth(0);b.setMinHeight(0);b.setPadding(dp(9),0,dp(9),0);b.setBackground(shape(active?ACCENT:SURFACE2,active?ACCENT:BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(29));lp.setMargins(0,0,dp(6),0);b.setLayoutParams(lp);return b;
  }

  void renderGroupResults(Group g,LinearLayout target,String query,String activeSub){
    target.removeAllViews();String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);ArrayList<Cmd> shown=new ArrayList<>();for(Cmd c:groupCommands(g)){String sc=groupSubcategory(c,g);if(activeSub!=null&&!activeSub.equals(sc))continue;if(!q.isEmpty()){String hay=(displayTitle(c)+" "+c.command+" "+c.description+" "+sc).toLowerCase(Locale.ROOT);if(!hay.contains(q))continue;}shown.add(c);}if(shown.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No prompts match this view.",12,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(18),0,dp(18));empty.addView(e);target.addView(empty);return;}TextView meta=text(shown.size()+" prompt"+(shown.size()==1?"":"s"),11,false,TERTIARY);meta.setPadding(0,0,0,dp(6));target.addView(meta);for(Cmd c:shown){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,g));target.addView(row);}
  }

  View commandRow(Cmd c,boolean divider){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(9),dp(7),dp(8),dp(7));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView t=text(polishedTitleV11(c),13,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(t);TextView d=text(polishedOutcomeV11(c,""),9,false,MUTED);d.setSingleLine(true);d.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView add=text(selected.contains(c)?"✓":"＋",18,true,selected.contains(c)?SUCCESS:ACCENT);add.setGravity(Gravity.CENTER);add.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added");home();}});card.addView(add,new LinearLayout.LayoutParams(dp(34),dp(36)));return card;}

  void detail(Cmd c,Group g){showPromptDialog(c);}

  void info(String label,String body){TextView l=text(label,10,true,ACCENT);l.setLetterSpacing(.14f);l.setPadding(0,dp(14),0,dp(6));root.addView(l);LinearLayout box=surface(true);TextView b=text(body,15,false,TEXT);b.setLineSpacing(0,1.18f);b.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);box.addView(b);root.addView(box);}

  void sourceActions(Cmd c){
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

  void relatedActions(String command){
    String[] names=relatedNames(command);if(names.length==0)return;
    TextView l=text("WORKS WELL WITH",10,true,ACCENT);l.setLetterSpacing(.14f);l.setPadding(0,dp(14),0,dp(6));root.addView(l);
    HorizontalScrollView scroll=new HorizontalScrollView(this);scroll.setHorizontalScrollBarEnabled(false);scroll.setFillViewport(false);
    LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(0,0,dp(4),0);
    for(String name:names){
      Cmd related=find(name);if(related==null||related.command.equals(command))continue;
      Button chip=relatedChip(related);row.addView(chip);
    }
    scroll.addView(row);LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2);sp.setMargins(0,0,0,dp(10));scroll.setLayoutParams(sp);root.addView(scroll);
    TextView hint=text("Tap a command to add it directly to your Prompt Stack.",11,false,MUTED);hint.setPadding(0,0,0,dp(6));root.addView(hint);
  }

  Button relatedChip(Cmd c){
    boolean added=selected.contains(c);Button x=new Button(this);x.setAllCaps(false);x.setText((added?"✓  ":"＋  ")+displayTitle(c));x.setTextColor(added?SUCCESS:TEXT);x.setTextSize(11);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setSingleLine(true);x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(11),0,dp(11),0);x.setBackground(shape(SURFACE2,added?SUCCESS:BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(36));lp.setMargins(0,0,dp(8),0);x.setLayoutParams(lp);x.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added "+displayTitle(c));x.setText("✓  "+displayTitle(c));x.setTextColor(SUCCESS);x.setBackground(shape(SURFACE2,SUCCESS,18));}else toast(displayTitle(c)+" is already in the stack");});return x;
  }

  void seedProposalStackOnce(){if(!selected.isEmpty())return;android.content.SharedPreferences p=getSharedPreferences(PREFS,MODE_PRIVATE);if(p.getBoolean("proposal_starter_stack_seen",false))return;String[] ids={"research","summarize","action"};for(String id:ids){Cmd c=find(id);if(c!=null&&!selected.contains(c))selected.add(c);}p.edit().putBoolean("proposal_starter_stack_seen",true).apply();}
  void stack(){showStackSheet();}

  void addMore(){
    page="addMore";
    base("Add more commands","Start with suggestions that work well with your current Stack, or choose any prompt from the library.",false);

    ArrayList<Cmd> suggestions=suggestedForStack();
    if(!suggestions.isEmpty()){
      TextView sl=label("SUGGESTED / WORKS WELL WITH");root.addView(sl);
      HorizontalScrollView scroll=new HorizontalScrollView(this);scroll.setHorizontalScrollBarEnabled(false);
      LinearLayout chips=hbox();chips.setPadding(0,0,dp(4),0);
      for(Cmd c:suggestions){Button chip=relatedChip(c);chips.addView(chip);}
      scroll.addView(chips);LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,-2);hp.setMargins(0,0,0,dp(8));scroll.setLayoutParams(hp);root.addView(scroll);
      TextView hint=text("Suggestions based on your current Stack. Tap any prompt to add it instantly.",12,false,MUTED);hint.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);hint.setGravity(Gravity.START);hint.setPadding(0,0,0,dp(10));root.addView(hint);
    }

    root.addView(label("BROWSE BY CATEGORY"));
    for(Group g:groups){
      int total=groupCount(g);if(total==0)continue;
      View card=menuCard(g.icon,g.title,total+" prompts");card.setOnClickListener(v->group(g));root.addView(card);
    }

    ArrayList<Cmd> custom=new ArrayList<>();for(Cmd c:all)if(c.custom)custom.add(c);
    if(!custom.isEmpty()){
      root.addView(section("My custom prompts",custom.size()));
      LinearLayout block=vbox();block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2));
      for(int i=0;i<custom.size();i++)block.addView(pickCommandRow(custom.get(i),i<custom.size()-1));
      root.addView(block);spacer(10);
    }

    Button done=primary("Done · Back to Prompt Stack");done.setOnClickListener(v->stack());root.addView(done);
  }

  int availableCount(Group g){int n=0;for(String name:g.names)if(find(name)!=null)n++;return n;}

  View pickCommandRow(Cmd c,boolean divider){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),14,true,TEXT));TextView d=text(shortDescription(c),10,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView state=text(selected.contains(c)?"✓":"＋",16,true,selected.contains(c)?SUCCESS:ACCENT);state.setGravity(Gravity.CENTER);card.addView(state,new LinearLayout.LayoutParams(dp(34),dp(40)));card.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added "+displayTitle(c));}else{selected.remove(c);toast("Removed "+displayTitle(c));}addMore();});return card;
  }

  ArrayList<Cmd> suggestedForStack(){
    LinkedHashSet<String> names=new LinkedHashSet<>();
    for(Cmd current:selected)for(String n:relatedNames(current.command))if(!n.equals(current.command))names.add(n);
    ArrayList<Cmd> out=new ArrayList<>();for(String n:names){Cmd c=find(n);if(c!=null&&!selected.contains(c))out.add(c);}return out;
  }

  void build(){
    page="build";
    String user=context==null?contextDraft:context.getText().toString().trim();contextDraft=user;
    base("Final Prompt","Review the exact prompt text that will be sent to ChatGPT.",false);
    StringBuilder p=new StringBuilder();
    for(int i=0;i<selected.size();i++){
      if(i>0)p.append("\n\n");
      p.append(resolveTemplate(selected.get(i),user).trim());
    }
    if(!user.isEmpty()){
      if(p.length()>0)p.append("\n\n");
      p.append(user);
    }
    finalPrompt=input("",12);finalPrompt.setText(p.toString());finalPrompt.setTextSize(13);finalPrompt.setMinHeight(dp(260));root.addView(finalPrompt);
    Button send=primary("➤  Open in ChatGPT");send.setOnClickListener(v->send());root.addView(send);
    Button copy=secondary("Copy prompt");copy.setOnClickListener(v->copy());root.addView(copy);
    Button edit=ghost("Edit stack");edit.setOnClickListener(v->stack());root.addView(edit);
  }

  void library(){library(false);}
  View starterPreview(String title,String sub,int accent){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);ImageView ic=vectorTile(R.drawable.pd_ic_content,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(35),dp(35));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));copy.addView(text(sub,9,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView more=text("⋯",17,false,TERTIARY);more.setGravity(Gravity.CENTER);card.addView(more,new LinearLayout.LayoutParams(dp(22),dp(35)));card.setOnClickListener(v->showAdd());return card;}
  void library(boolean favoritesMode){showPromptCollectionDialog(favoritesMode);}

  void customDetail(Cmd c){
    page="customDetail";base("/"+c.command,c.description,true);info("INSTRUCTION SENT TO CHATGPT",c.instruction);Button add=selected.contains(c)?secondary("✓  Added to Prompt Stack"):primary("＋  Add to Prompt Stack");add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);stack();});root.addView(add);Button del=ghost("Delete custom prompt");del.setOnClickListener(v->confirmDelete(c));root.addView(del);}

  void showBulkPaste(){
    LinearLayout box=vbox();box.setPadding(dp(18),dp(4),dp(18),0);
    EditText category=input("Category (default: Photo Editing & Image Generation)",1);category.setText("Photo Editing & Image Generation");
    EditText bulk=input("Paste anything here…\n\nSimple:\n/NeonCity → Cyberpunk night portrait\n\nOr full prompt blocks:\n/NeonPortrait\nCreate a dramatic cyberpunk portrait at night with neon reflections, rain, cinematic contrast...\n\n/StudioClean\nCreate a clean professional studio portrait with soft key light...",14);
    box.addView(category);box.addView(bulk);
    TextView note=text("Paste one complete prompt as-is and PromptDeck will create its command name and description automatically. For several prompts at once, start each one with /CommandName.",12,false,MUTED);note.setPadding(0,dp(4),0,dp(8));box.addView(note);
    AlertDialog d=new AlertDialog.Builder(this).setTitle("Smart paste prompts").setView(box).setNegativeButton("Cancel",null).setPositiveButton("Parse & add",null).create();
    d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String cat=category.getText().toString().trim();if(cat.isEmpty())cat="Photo Editing & Image Generation";int[] result=parseBulkCommands(bulk.getText().toString(),cat);if(result[0]==0){toast("Paste a prompt, or use /CommandName when pasting several prompts");return;}saveCustom();d.dismiss();library();toast("Added "+result[0]+" prompts"+(result[1]>0?" • skipped "+result[1]:""));}));d.show();
  }

  int[] parseBulkCommands(String raw,String category){
    int added=0,skipped=0;
    java.util.regex.Pattern header=java.util.regex.Pattern.compile("^\\s*(?:\\d+[.)]\\s*)?/([A-Za-z0-9_-]+)(?:\\s*(?:→|->|—|–|:|=)\\s*(.*))?\\s*$");
    String currentName=null,currentInline=null;StringBuilder body=new StringBuilder();
    ArrayList<String[]> blocks=new ArrayList<>();
    for(String line:raw.split("\\r?\\n")){
      java.util.regex.Matcher m=header.matcher(line.trim());
      if(m.matches()){
        if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});
        currentName=m.group(1);currentInline=m.group(2)==null?"":m.group(2).trim();body.setLength(0);
      }else if(currentName!=null){if(body.length()>0)body.append('\n');body.append(line);}
    }
    if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});

    // No slash headers: treat the complete pasted text as one prompt and infer its command name.
    if(blocks.isEmpty()){
      String fullRaw=raw==null?"":raw.trim();
      if(!fullRaw.isEmpty())blocks.add(new String[]{autoCommandName(fullRaw,category),"",fullRaw});
    }

    for(String[] b:blocks){
      String name=b[0],inline=b[1],full=b[2];String instruction=!full.isEmpty()?full:inline;
      if(instruction==null||instruction.trim().isEmpty()){skipped++;continue;}
      String base=name;int suffix=2;while(find(name)!=null)name=base+(suffix++);
      String desc=!inline.isEmpty()&&!full.isEmpty()?inline:autoDescription(instruction,category);
      if(!inline.isEmpty()&&full.isEmpty())desc=inline;
      try{
        JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",name);o.put("category",category);
        o.put("description",category.toLowerCase(Locale.ROOT).contains("photo")?photoDescription(desc):desc);
        o.put("instruction",instruction);all.add(new Cmd(o,true));added++;
      }catch(Exception e){skipped++;}
    }
    return new int[]{added,skipped};
  }

  String autoCommandName(String prompt,String category){
    String text=prompt==null?"":prompt.trim();
    String lower=text.toLowerCase(Locale.ROOT);
    String candidate="";

    // Prefer an explicit short first line as the title if the user pasted one.
    String[] lines=text.split("\\r?\\n");
    if(lines.length>0){
      String first=lines[0].trim().replaceAll("^[#*\\s-]+","");
      if(first.length()>=3&&first.length()<=56&&first.split("\\s+").length<=8&&!first.endsWith(".")&&!first.endsWith(","))candidate=first;
    }

    if(candidate.isEmpty()&&category!=null&&category.toLowerCase(Locale.ROOT).contains("photo")){
      if(lower.contains("papyrus")||lower.contains("archival")||lower.contains("antique"))candidate="ArchivalArtwork";
      else if(lower.contains("double exposure"))candidate="DoubleExposure";
      else if(lower.contains("cinematic")||lower.contains("movie still"))candidate="CinematicImage";
      else if(lower.contains("portrait")||lower.contains("face"))candidate="PortraitEdit";
      else if(lower.contains("product"))candidate="ProductPhoto";
      else if(lower.contains("background"))candidate="BackgroundEdit";
      else if(lower.contains("restore")||lower.contains("resolution")||lower.contains("upscale"))candidate="PhotoRestore";
      else if(lower.contains("vintage")||lower.contains("film grain")||lower.contains("35mm"))candidate="VintagePhoto";
      else if(lower.contains("watercolor")||lower.contains("illustration")||lower.contains("painting"))candidate="ArtStyle";
    }

    if(candidate.isEmpty()){
      HashSet<String> stop=new HashSet<>(Arrays.asList("the","a","an","and","or","to","of","in","on","for","with","from","this","that","it","is","are","be","as","use","create","make","generate","produce","image","photo","prompt","please","only","into","while","keep","preserve","original","subject"));
      StringBuilder out=new StringBuilder();int count=0;
      for(String w:text.replaceAll("[^A-Za-z0-9 ]"," ").split("\\s+")){
        String lw=w.toLowerCase(Locale.ROOT);if(w.length()<3||stop.contains(lw))continue;
        out.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1).toLowerCase(Locale.ROOT));
        if(++count==3)break;
      }
      candidate=out.length()>0?out.toString():"CustomPrompt";
    }

    String clean=Cmd.clean(candidate);
    if(clean.isEmpty())clean="CustomPrompt";
    if(clean.length()>32)clean=clean.substring(0,32);
    return clean;
  }

  void showAdd(){
    LinearLayout x=vbox();x.setPadding(dp(18),dp(4),dp(18),0);EditText cmd=input("Command name, e.g. architectreview",1),cat=input("Category",1),desc=input("Short explanation",2),inst=input("Full instruction for ChatGPT",5);x.addView(cmd);x.addView(cat);x.addView(desc);x.addView(inst);
    AlertDialog d=new AlertDialog.Builder(this).setTitle("Add prompt").setView(x).setNegativeButton("Cancel",null).setPositiveButton("Add",null).create();d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{try{JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",cmd.getText());o.put("category",cat.getText());o.put("description",desc.getText());o.put("instruction",inst.getText());Cmd c=new Cmd(o,true);all.add(c);saveCustom();d.dismiss();library();toast("Prompt added");}catch(Exception e){toast("Name and instruction are required");}}));d.show();
  }
  void confirmDelete(Cmd c){new AlertDialog.Builder(this).setTitle("Delete /"+c.command+"?").setMessage("This removes the custom prompt from this device.").setNegativeButton("Cancel",null).setPositiveButton("Delete",(d,w)->{all.remove(c);selected.remove(c);saveCustom();library();}).show();}

  ImageView drawableIcon(int res,int tint){ImageView v=new ImageView(this);v.setImageResource(res);v.setColorFilter(tint);v.setScaleType(ImageView.ScaleType.CENTER_INSIDE);return v;}

  LinearLayout bottomNav(){
    LinearLayout nav=hbox();nav.setGravity(Gravity.CENTER);nav.setPadding(dp(8),dp(3),dp(8),dp(3));nav.setBackground(satinShape(Color.rgb(7,17,29),Color.rgb(5,14,24),BORDER,0));
    nav.addView(navItem(R.drawable.pd_nav_search,"Discover",!"stack".equals(page),()->home()),new LinearLayout.LayoutParams(0,-1,1));
    String stackLabel=selected.isEmpty()?"Stack":"Stack ("+selected.size()+")";nav.addView(navItem(R.drawable.pd_nav_stack,stackLabel,"stack".equals(page),()->stack()),new LinearLayout.LayoutParams(0,-1,1));return nav;
  }
  View navItem(int iconRes,String label,boolean active,Runnable action){LinearLayout x=vbox();x.setGravity(Gravity.CENTER);ImageView i=drawableIcon(iconRes,active?ACCENT:TERTIARY);i.setPadding(dp(5),dp(3),dp(5),dp(2));TextView l=text(label,9,active,active?ACCENT:TERTIARY);l.setGravity(Gravity.CENTER);x.addView(i,new LinearLayout.LayoutParams(-1,dp(27)));x.addView(l,new LinearLayout.LayoutParams(-1,dp(17)));x.setOnClickListener(v->action.run());return x;}
  boolean navActive(String key){if("home".equals(key))return"home".equals(page);if("browse".equals(key))return"search".equals(page)||"categories".equals(page)||"group".equals(page)||"detail".equals(page)||"discover".equals(page);if("stack".equals(key))return"stack".equals(page)||"addMore".equals(page)||"build".equals(page);if("my".equals(key))return"library".equals(page)||"customDetail".equals(page);return"settings".equals(page);}
  void spacerH(LinearLayout row){Space s=new Space(this);row.addView(s,new LinearLayout.LayoutParams(dp(6),1));}
  TextView sectionTitle(String title,String action){TextView v=text(action==null?title:title+"                                      "+action,13,true,TEXT);v.setPadding(dp(1),dp(12),0,dp(6));return v;}
  View goalTile(int iconRes,String title,String query,int accent){LinearLayout card=vbox();card.setPadding(dp(9),dp(9),dp(8),dp(7));card.setGravity(Gravity.START);card.setBackground(tintedCard(accent,14));ImageView ic=vectorPlain(iconRes,accent);card.addView(ic,new LinearLayout.LayoutParams(dp(24),dp(24)));TextView t=text(title,10,true,TEXT);t.setMaxLines(2);t.setPadding(0,dp(5),0,0);card.addView(t);card.setOnClickListener(v->smartCollection(title,"Best matching prompts",query,null,"Best matches"));return card;}
  View collectionTile(int iconRes,String title,String sub,String query,int accent){LinearLayout card=hbox();card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(7),dp(6),dp(7),dp(6));card.setBackground(tintedCard(accent,12));ImageView ic=vectorTile(iconRes,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(31),dp(31));ip.setMargins(0,0,dp(7),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,10,true,TEXT));TextView d=text(sub,8,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.setOnClickListener(v->smartCollection(title,sub,query,null,"Best matches"));return card;}
  GradientDrawable tintedCard(int accent,int radius){int r=(Color.red(accent)+Color.red(BG)*5)/6,g=(Color.green(accent)+Color.green(BG)*5)/6,b=(Color.blue(accent)+Color.blue(BG)*5)/6;return satinShape(Color.rgb(Math.min(255,r+10),Math.min(255,g+10),Math.min(255,b+10)),Color.rgb(r,g,b),Color.rgb((Color.red(accent)+36)/2,(Color.green(accent)+54)/2,(Color.blue(accent)+76)/2),radius);}
  TextView iconTile(String icon,int accent){TextView v=text(icon,19,true,Color.WHITE);v.setGravity(Gravity.CENTER);v.setBackground(tintedCard(accent,12));return v;}
  int groupAccent(Group g){String x=g.title; if(x.equals("Writing & Content"))return Color.rgb(61,130,255);if(x.equals("Research & Learning"))return Color.rgb(45,203,140);if(x.equals("Productivity & Planning"))return Color.rgb(226,184,78);if(x.equals("Career & Business"))return Color.rgb(168,91,255);if(x.equals("Technology & Development"))return Color.rgb(32,199,201);if(x.equals("Creativity & Design"))return Color.rgb(243,92,153);if(x.equals("Health & Lifestyle"))return Color.rgb(88,216,109);if(x.equals("Science & Education"))return Color.rgb(61,130,255);return Color.rgb(74,223,209);}
  int groupIconRes(Group g){String x=g.title;if(x.equals("Writing & Content"))return R.drawable.pd_ic_write;if(x.equals("Research & Learning"))return R.drawable.pd_ic_research;if(x.equals("Productivity & Planning"))return R.drawable.pd_ic_calendar;if(x.equals("Career & Business"))return R.drawable.pd_ic_briefcase;if(x.equals("Technology & Development"))return R.drawable.pd_ic_code;if(x.equals("Creativity & Design"))return R.drawable.pd_ic_creative;if(x.equals("Health & Lifestyle"))return R.drawable.pd_ic_heart;if(x.equals("Science & Education"))return R.drawable.pd_ic_flask;return R.drawable.pd_ic_image;}
  ImageView vectorTile(int res,int accent){ImageView v=drawableIcon(res,Color.WHITE);v.setPadding(dp(8),dp(8),dp(8),dp(8));v.setBackground(tintedCard(accent,12));return v;}
  ImageView vectorPlain(int res,int tint){ImageView v=drawableIcon(res,tint);v.setPadding(dp(1),dp(1),dp(1),dp(1));return v;}
  int categoryAccent(Cmd c){Group g=groupFor(c);return groupAccent(g);}
  String promptIcon(Cmd c){String x=(c.category+" "+c.command).toLowerCase(Locale.ROOT);if(x.contains("write")||x.contains("email"))return"✎";if(x.contains("research")||x.contains("learn")||x.contains("explain"))return"⌕";if(x.contains("plan")||x.contains("roadmap"))return"▣";if(x.contains("code")||x.contains("technical")||x.contains("debug"))return"⚙";if(x.contains("photo")||x.contains("image"))return"▧";if(x.contains("health"))return"♡";if(x.contains("marketing")||x.contains("business"))return"▤";return"◆";}
  String displayGroupTitle(Group g){return g.title;}
  View modeChoiceCard(int iconRes,String title,String sub,int accent,Runnable action){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(13),dp(12),dp(12),dp(12));card.setBackground(tintedCard(accent,16));ImageView icon=vectorTile(iconRes,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(46),dp(46));ip.setMargins(0,0,dp(12),0);card.addView(icon,ip);LinearLayout copy=vbox();copy.addView(text(title,15,true,TEXT));TextView d=text(sub,10,false,MUTED);d.setMaxLines(2);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView arrow=text("›",24,false,TERTIARY);arrow.setGravity(Gravity.CENTER);card.addView(arrow,new LinearLayout.LayoutParams(dp(28),dp(46)));card.setOnClickListener(v->action.run());return card;
  }
  LinearLayout modeSwitch(){
    LinearLayout seg=hbox();Button ask=filterChip("Ask PromptDeck","ask".equals(discoverMode)),browse=filterChip("Browse prompts","browse".equals(discoverMode));ask.setOnClickListener(v->{discoverMode="ask";askCapability="";discoverPreset="";browseLimit=30;home();});browse.setOnClickListener(v->{discoverMode="browse";askCapability="";discoverPreset="";browseLimit=30;home();});LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(36),1);a.setMargins(0,0,dp(6),0);seg.addView(ask,a);seg.addView(browse,new LinearLayout.LayoutParams(0,dp(36),1));return seg;
  }
  View selectionBar(){
    LinearLayout bar=hbox();bar.setGravity(Gravity.CENTER_VERTICAL);bar.setPadding(dp(14),dp(7),dp(10),dp(7));bar.setBackground(satinShape(Color.rgb(10,24,40),Color.rgb(7,18,31),BORDER,0));TextView count=text(selected.size()+" selected",11,true,TEXT);bar.addView(count,new LinearLayout.LayoutParams(0,-1,1));Button review=primary("Review & Run  →");review.setTextSize(11);review.setOnClickListener(v->showStackSheet());bar.addView(review,new LinearLayout.LayoutParams(dp(150),dp(40)));return bar;
  }
  boolean containsAny(String x,String...terms){String z=x==null?"":x.toLowerCase(Locale.ROOT);for(String t:terms)if(z.contains(t))return true;return false;}
  void addWorkflowBest(ArrayList<Cmd> out,String query){for(Cmd c:rankSmart(query,20)){if(!out.contains(c)){out.add(c);return;}}}
  ArrayList<Cmd> workflowForGoal(String goal){
    ArrayList<Cmd> out=new ArrayList<>();String q=goal==null?"":goal.toLowerCase(Locale.ROOT);
    if(containsAny(q,"compare","choose","choice","buy","best","versus"," vs ")){addWorkflowBest(out,goal+" research facts evidence");addWorkflowBest(out,goal+" compare options criteria tradeoffs");addWorkflowBest(out,goal+" recommend best option decision");}
    else if(containsAny(q,"plan","project","roadmap","schedule","organize")){addWorkflowBest(out,goal+" clarify goal constraints");addWorkflowBest(out,goal+" plan steps roadmap");addWorkflowBest(out,goal+" action checklist next steps");}
    else if(containsAny(q,"write","email","article","post","caption","resume","cv")){addWorkflowBest(out,goal+" draft write");addWorkflowBest(out,goal+" rewrite clarity improve");}
    else if(containsAny(q,"learn","explain","understand","study","teach")){addWorkflowBest(out,goal+" research explain accurately");addWorkflowBest(out,goal+" simplify teach beginner");}
    else if(containsAny(q,"code","debug","error","bug","technical","fix")){addWorkflowBest(out,goal+" diagnose debug technical");addWorkflowBest(out,goal+" fix solution verify");}
    else if(containsAny(q,"image","photo","picture","visual","design")){addWorkflowBest(out,goal+" image visual prompt");addWorkflowBest(out,goal+" refine image prompt");}
    else{for(Cmd c:rankSmart(goal,5)){if(!out.contains(c))out.add(c);if(out.size()>=2)break;}}
    if(out.size()>4)return new ArrayList<>(out.subList(0,4));return out;
  }
  View bestMatchCard(Cmd c,String goal){
    LinearLayout card=surface(true);card.setPadding(dp(12),dp(11),dp(12),dp(11));LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);row.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(presentationTitleV8(c),14,true,TEXT));TextView d=text(presentationOutcomeV8(c),10,false,MUTED);d.setMaxLines(2);copy.addView(d);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(row);Button use=primary(selected.contains(c)?"Added":"Use this prompt");use.setEnabled(!selected.contains(c));use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(c))selected.add(c);home();});card.addView(use);return card;
  }
  View workflowCard(ArrayList<Cmd> flow,String goal){
    LinearLayout card=surface(true);card.setPadding(dp(12),dp(10),dp(12),dp(10));TextView meta=text(flow.size()+"-step workflow",10,true,ACCENT);meta.setPadding(0,0,0,dp(5));card.addView(meta);for(int i=0;i<flow.size();i++){Cmd c=flow.get(i);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(String.valueOf(i+1),9,true,TERTIARY);n.setGravity(Gravity.CENTER);row.addView(n,new LinearLayout.LayoutParams(dp(24),dp(30)));TextView t=text(polishedTitleV11(c),11,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);row.addView(t,new LinearLayout.LayoutParams(0,dp(30),1));card.addView(row);}Button use=secondary("Use workflow");use.setOnClickListener(v->{beginAskSelectionV10(goal);for(Cmd c:flow)if(!selected.contains(c))selected.add(c);home();});card.addView(use);return card;
  }
  void beginAskSelectionV10(String goal){
    String g=goal==null?"":goal.trim();
    if(!askSelectionGoal.isEmpty()&&!askSelectionGoal.equalsIgnoreCase(g))selected.clear();
    else if(askSelectionGoal.isEmpty()&&!selected.isEmpty()&&!contextDraft.trim().equalsIgnoreCase(g))selected.clear();
    askSelectionGoal=g;contextDraft=g;
  }
  String safePresentationTitleV10(Cmd c){
    String t=presentationTitleV8(c);if(t==null)t="";t=t.replaceAll("(?i)\\b(?:from|for)?prompt(?:ing)?(?:agent|role|skill)?\\b$","").replaceAll("\\s+"," ").trim();
    if(uglyPresentationV8(t)||longTokenV8(t)||t.matches(".*[{}\\[\\]\"<>].*")){String d=c.description==null?"":c.description.replaceAll("[{}\\[\\]\"<>#]"," ").replaceAll("\\s+"," ").trim();if(!uglyPresentationV8(d)&&!longTokenV8(d)&&d.length()>=4)t=d;}
    if(t.length()>58)t=t.substring(0,55).trim()+"…";return t.isEmpty()?"ChatGPT workflow":t;
  }
  String safePresentationOutcomeV10(Cmd c){
    String d=presentationOutcomeV8(c);if(d==null)d="";d=d.replaceAll("(?is)^(?:act as|you are|role:|title:|for this step in a larger workflow:)\\s*","").replaceAll("[{}\\[\\]\"<>#]"," ").replaceAll("\\s+"," ").trim();
    if(d.length()<8||uglyPresentationV8(d)||longTokenV8(d))d="Focused ChatGPT workflow for this outcome.";if(d.length()>92)d=d.substring(0,89).trim()+"…";return d;
  }
  boolean longTokenV8(String x){if(x==null)return false;for(String w:x.split("\\s+"))if(w.length()>20)return true;return false;}
  boolean uglyPresentationV8(String x){
    if(x==null)return true;String z=x.trim();if(z.isEmpty())return true;
    if(z.startsWith("{")||z.startsWith("[")||z.contains("\"project_")||z.contains("\"meta_")||z.contains("${")||z.contains("# TITLE")||z.contains("<prompt>"))return true;
    int punct=0;for(int i=0;i<z.length();i++){char ch=z.charAt(i);if(ch=='{'||ch=='}'||ch=='['||ch==']'||ch=='\"'||ch=='#'||ch=='<')punct++;}return punct>=4;
  }
  boolean imagePromptV8(Cmd c){return (c.id>=50000&&c.id<50200)||"Images & Visuals".equals(c.category)||(c.category!=null&&c.category.toLowerCase(Locale.ROOT).contains("photo"));}
  String presentationTitleV8(Cmd c){
    String t=displayTitle(c);if(t==null)t="";t=t.replaceAll("(?i)^(?:prompt|workflow)\\s*[:\\-]\\s*","").replaceAll("[\\{\\}\\[\\]\\\"]"," ").replaceAll("\\s+"," ").trim();
    if(imagePromptV8(c)&&(uglyPresentationV8(t)||longTokenV8(t))){String cap=CapabilityRouter.inferImageCapability(c);t=CapabilityRouter.label(cap);}
    if(t.length()>60)t=t.substring(0,57).trim()+"…";return t.isEmpty()?"ChatGPT Workflow":t;
  }
  String presentationOutcomeV8(Cmd c){
    String d=shortDescription(c);if(d==null)d="";if(uglyPresentationV8(d)||d.length()>120){String cap=imagePromptV8(c)?CapabilityRouter.inferImageCapability(c):"";d=cap.isEmpty()?"Ready-to-use ChatGPT workflow for this task.":CapabilityRouter.outcome(cap);}d=d.replaceAll("(?is)^\\s*(?:role|title)\\s*:\\s*","").replaceAll("\\s+"," ").trim();if(d.length()>94)d=d.substring(0,91).trim()+"…";return d.isEmpty()?"Ready-to-use ChatGPT workflow for this task.":d;
  }
  String commandWordsV11(Cmd c){
    String x=c==null||c.command==null?"":c.command; x=x.replace('_',' ').replace('-',' ');
    x=x.replaceAll("([a-z0-9])([A-Z])","$1 $2").replaceAll("(?i)\\b(?:prompt|agent|role|skill)\\b"," ").replaceAll("\\s+"," ").trim();
    if(x.isEmpty())return "ChatGPT workflow";StringBuilder out=new StringBuilder();for(String w:x.split(" ")){if(w.isEmpty())continue;if(out.length()>0)out.append(' ');if(w.length()<=3&&w.equals(w.toUpperCase(Locale.ROOT)))out.append(w);else out.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));}return out.toString();
  }
  boolean genericPresentationV11(String x){if(x==null)return true;String z=x.trim().toLowerCase(Locale.ROOT);return z.isEmpty()||z.equals("chatgpt workflow")||z.equals("focused chatgpt workflow for this outcome.")||z.startsWith("ready-to-use chatgpt workflow")||z.startsWith("use the strongest prompt family");}
  String polishedTitleV11(Cmd c){
    String t=safePresentationTitleV10(c);if(genericPresentationV11(t)||uglyPresentationV8(t)||longTokenV8(t)){String d=c.description==null?"":c.description.replaceAll("[{}\\[\\]\\\"<>#]"," ").replaceAll("\\s+"," ").trim();if(d.length()>=4&&d.length()<=62&&!uglyPresentationV8(d)&&!longTokenV8(d))t=d;else t=commandWordsV11(c);}if(t.length()>58)t=t.substring(0,55).trim()+"…";return t;
  }
  String polishedOutcomeV11(Cmd c,String cap){
    String d=safePresentationOutcomeV10(c);if(genericPresentationV11(d)||uglyPresentationV8(d)||longTokenV8(d)){d=(cap==null||cap.isEmpty())?"Focused workflow for this task.":CapabilityRouter.outcome(cap);}if(d.length()>98)d=d.substring(0,95).trim()+"…";return d;
  }
  int qualityPenaltyV11(Cmd c){
    int p=0;String t=polishedTitleV11(c),d=polishedOutcomeV11(c,"");if(t.length()>54)p+=5;if(genericPresentationV11(t))p+=20;if(genericPresentationV11(d))p+=8;if(c.id>=30000&&c.id<50000)p+=3;if(c.id>=60000&&c.id<70000)p+=2;return p;
  }
  int qualityScoreV11(Cmd c,String cap,String query){
    int score=capabilityScoreV8(c,cap,query)-qualityPenaltyV11(c);if(c.id>0&&c.id<10000)score+=10;if(c.id>=70000&&c.id<70100)score+=7;if(imagePromptV8(c)&&c.id>=50000&&c.id<50200)score+=8;String q=CapabilityRouter.norm(query);String hay=(polishedTitleV11(c)+" "+polishedOutcomeV11(c,cap)+" "+c.subcategory+" "+c.command).toLowerCase(Locale.ROOT);for(String w:q.split(" "))if(w.length()>3&&hay.contains(w))score+=5;return score;
  }
  String familyKeyV11(Cmd c,String cap){
    String t=polishedTitleV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9 ]"," ").replaceAll("\\s+"," ").trim();String[] w=t.split(" ");StringBuilder k=new StringBuilder(cap==null?"":cap);int n=0;for(String x:w){if(x.length()<4||x.equals("prompt")||x.equals("chatgpt")||x.equals("workflow"))continue;k.append('|').append(x);if(++n==2)break;}if(n==0)k.append('|').append(c.subcategory==null?"":c.subcategory.toLowerCase(Locale.ROOT));return k.toString();
  }
  ArrayList<Cmd> rankCapabilityV11(String cap,String query,int limit){
    ArrayList<Cmd> pool=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();for(Cmd c:all){int sc=qualityScoreV11(c,cap,query);int floor=cap.startsWith("image.")?38:24;if(sc>=floor){pool.add(c);scores.put(c,sc);}}
    Collections.sort(pool,(a,b)->{int x=scores.get(a),y=scores.get(b);if(x!=y)return Integer.compare(y,x);return polishedTitleV11(a).compareToIgnoreCase(polishedTitleV11(b));});
    ArrayList<Cmd> out=new ArrayList<>();HashSet<String> families=new HashSet<>(),titles=new HashSet<>();for(Cmd c:pool){String title=polishedTitleV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim(),fam=familyKeyV11(c,cap);if(titles.contains(title)||families.contains(fam))continue;titles.add(title);families.add(fam);out.add(c);if(out.size()>=limit)break;}return out;
  }
  String fitReasonV11(String cap,String query){
    String base=CapabilityRouter.outcome(cap);String q=query==null?"":query.trim();if(q.isEmpty())return base;return base+" PromptDeck routed your request to this capability before ranking individual prompts.";
  }
  int capabilityCategoryBoostV8(Cmd c,String cap){String cat=c.category==null?"":c.category;if(cap.startsWith("career."))return cat.equals("Career & Business")?24:0;if(cap.startsWith("decision."))return cat.equals("Productivity & Planning")||cat.equals("Research & Learning")?18:0;if(cap.startsWith("code."))return cat.equals("Technology & Development")?24:0;if(cap.startsWith("research."))return cat.equals("Research & Learning")?24:0;if(cap.startsWith("planning."))return cat.equals("Productivity & Planning")?24:0;if(cap.startsWith("learning."))return cat.equals("Science & Education")||cat.equals("Research & Learning")?20:0;if(cap.startsWith("writing."))return cat.equals("Writing & Content")?24:0;return 0;}
  int capabilityScoreV8(Cmd c,String cap,String query){
    if(cap.startsWith("image.")&&!(c.id>=50000&&c.id<50200))return -1000;
    int score=capabilityCategoryBoostV8(c,cap);if(cap.startsWith("image.")&&CapabilityRouter.inferImageCapability(c).equals(cap))score+=64;
    String hay=(presentationTitleV8(c)+" "+presentationOutcomeV8(c)+" "+c.category+" "+c.subcategory+" "+c.command).toLowerCase(Locale.ROOT);
    for(String t:CapabilityRouter.terms(cap).split(" "))if(t.length()>2&&hay.contains(t))score+=5;
    for(String t:CapabilityRouter.norm(query).split(" "))if(t.length()>2&&hay.contains(t))score+=7;
    if(c.id>=50000&&c.id<50200)score+=12;if(isFavorite(c))score+=2;return score;
  }
  ArrayList<Cmd> rankCapabilityV8(String cap,String query,int limit){
    ArrayList<Cmd> pool=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();for(Cmd c:all){int sc=capabilityScoreV8(c,cap,query);if(sc>0){pool.add(c);scores.put(c,sc);}}
    Collections.sort(pool,(a,b)->{int x=scores.get(a),y=scores.get(b);if(x!=y)return Integer.compare(y,x);return presentationTitleV8(a).compareToIgnoreCase(presentationTitleV8(b));});
    ArrayList<Cmd> out=new ArrayList<>();HashSet<String> seen=new HashSet<>();for(Cmd c:pool){String k=presentationTitleV8(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim();if(k.length()>4&&seen.contains(k))continue;if(k.length()>4)seen.add(k);out.add(c);if(out.size()>=limit)break;}return out;
  }
  View capabilityTileV8(String id,Runnable action){LinearLayout card=surface(true);card.setPadding(dp(11),dp(10),dp(11),dp(10));card.setMinimumHeight(dp(68));card.addView(text(CapabilityRouter.label(id),12,true,TEXT));TextView sub=text(CapabilityRouter.outcome(id),9,false,MUTED);sub.setMaxLines(2);sub.setEllipsize(android.text.TextUtils.TruncateAt.END);card.addView(sub);card.setOnClickListener(v->action.run());return card;}
  void renderImageModeChooserV8(LinearLayout target,String goal){
    target.removeAllViews();TextView h=text("Are you editing or creating?",15,true,TEXT);h.setPadding(0,dp(12),0,dp(2));target.addView(h);TextView sub=text("This keeps photo-editing tools separate from image-generation styles.",10,false,MUTED);sub.setPadding(0,0,0,dp(8));target.addView(sub);
    LinearLayout row=hbox();View edit=capabilityTileV8("image.enhance",()->renderCapabilityChooserV8(target,CapabilityRouter.IMAGE,goal,CapabilityRouter.EDIT));View create=capabilityTileV8("image.create",()->renderCapabilityChooserV8(target,CapabilityRouter.IMAGE,goal,CapabilityRouter.CREATE));LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,-2,1);a.setMargins(0,0,dp(6),0);row.addView(edit,a);row.addView(create,new LinearLayout.LayoutParams(0,-2,1));target.addView(row);
  }
  void renderCapabilityChooserV8(LinearLayout target,String domain,String goal,String forcedMode){
    target.removeAllViews();String mode=forcedMode==null||forcedMode.isEmpty()?(CapabilityRouter.IMAGE.equals(domain)?CapabilityRouter.imageMode(goal):CapabilityRouter.UNKNOWN):forcedMode;
    String heading=CapabilityRouter.IMAGE.equals(domain)&&CapabilityRouter.EDIT.equals(mode)?"What do you want to change?":"Choose the outcome you want";TextView h=text(heading,15,true,TEXT);h.setPadding(0,dp(12),0,dp(2));target.addView(h);TextView sub=text("PromptDeck narrows the library first, then recommends the strongest prompt.",10,false,MUTED);sub.setPadding(0,0,0,dp(8));target.addView(sub);
    String[] ids=CapabilityRouter.capabilities(domain,mode);for(int i=0;i<ids.length;i+=2){LinearLayout row=hbox();final String left=ids[i];View a=capabilityTileV8(left,()->{askCapability=left;renderCapabilityRecommendationV8(target,goal,left);});LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(0,-2,1);ap.setMargins(0,0,i+1<ids.length?dp(6):0,dp(6));row.addView(a,ap);if(i+1<ids.length){final String right=ids[i+1];View b=capabilityTileV8(right,()->{askCapability=right;renderCapabilityRecommendationV8(target,goal,right);});LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(0,-2,1);bp.setMargins(0,0,0,dp(6));row.addView(b,bp);}target.addView(row);}
    if(CapabilityRouter.IMAGE.equals(domain)&&CapabilityRouter.EDIT.equals(mode)){Button create=secondary("Create a new image instead");create.setOnClickListener(v->renderCapabilityChooserV8(target,domain,goal,CapabilityRouter.CREATE));target.addView(create);}
  }
  View bestCapabilityCardV8(Cmd c,String goal){LinearLayout card=surface(true);card.setPadding(dp(12),dp(11),dp(12),dp(11));LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);row.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(safePresentationTitleV10(c),14,true,TEXT));TextView d=text(safePresentationOutcomeV10(c),10,false,MUTED);d.setMaxLines(2);copy.addView(d);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(row);Button use=primary(selected.contains(c)?"Added":"Use this prompt");use.setEnabled(!selected.contains(c));use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(c))selected.add(c);home();});card.addView(use);return card;}
  void renderCapabilityRecommendationV8(LinearLayout target,String goal,String cap){
    target.removeAllViews();TextView eyebrow=text(CapabilityRouter.label(cap).toUpperCase(Locale.ROOT),10,true,TERTIARY);eyebrow.setLetterSpacing(.10f);eyebrow.setPadding(0,dp(10),0,dp(3));target.addView(eyebrow);
    TextView why=text(fitReasonV11(cap,goal),10,false,MUTED);why.setPadding(0,0,0,dp(8));target.addView(why);
    ArrayList<Cmd> ranked=rankCapabilityV11(cap,goal,6);if(ranked.isEmpty()){LinearLayout e=surface(true);e.addView(text("I understand the capability, but I don't have a strong enough prompt match to recommend confidently.",12,true,TEXT));TextView t=text("Choose another capability or browse the library instead of getting a weak recommendation.",10,false,MUTED);t.setPadding(0,dp(4),0,dp(8));e.addView(t);target.addView(e);Button choose=secondary("Choose another capability");choose.setOnClickListener(v->{CapabilityRouter.Route route=CapabilityRouter.route(goal);renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(choose);return;}
    Cmd first=ranked.get(0);TextView best=text("BEST APPROACH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(4),0,dp(5));target.addView(best);
    LinearLayout hero=surface(true);hero.setPadding(dp(13),dp(12),dp(13),dp(12));TextView capability=text(CapabilityRouter.label(cap),16,true,TEXT);hero.addView(capability);TextView outcome=text(CapabilityRouter.outcome(cap),10,false,MUTED);outcome.setPadding(0,dp(3),0,dp(8));hero.addView(outcome);TextView using=text("Using: "+polishedTitleV11(first),10,false,TERTIARY);using.setSingleLine(true);using.setEllipsize(android.text.TextUtils.TruncateAt.END);hero.addView(using);Button use=primary(selected.contains(first)?"Added":"Use this approach");use.setEnabled(!selected.contains(first));use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(first))selected.add(first);home();});hero.addView(use);target.addView(hero);
    if(ranked.size()>1){TextView more=text("OTHER STRONG MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(10),0,dp(5));target.addView(more);for(int i=1;i<Math.min(4,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}}
    Button back=secondary("Choose another capability");back.setOnClickListener(v->{askCapability="";CapabilityRouter.Route route=CapabilityRouter.route(goal);if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode))renderImageModeChooserV8(target,goal);else renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(back);
  }
  void renderCompoundWorkflowV8(LinearLayout target,String goal,CapabilityRouter.Route route){
    target.removeAllViews();ArrayList<Cmd> flow=new ArrayList<>();ArrayList<String> usedCaps=new ArrayList<>();for(String cap:route.capabilities){ArrayList<Cmd> r=rankCapabilityV11(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0))){flow.add(r.get(0));usedCaps.add(cap);}if(flow.size()>=4)break;}if(flow.size()<2){if(route.capabilities.isEmpty()){renderAskResultsV8(target,goal);return;}renderCapabilityRecommendationV8(target,goal,route.capabilities.get(0));return;}
    TextView h=text("SUGGESTED WORKFLOW",10,true,TERTIARY);h.setLetterSpacing(.10f);h.setPadding(0,dp(10),0,dp(5));target.addView(h);LinearLayout card=surface(true);card.setPadding(dp(12),dp(10),dp(12),dp(10));for(int i=0;i<flow.size();i++){Cmd c=flow.get(i);String cap=usedCaps.get(i);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(String.valueOf(i+1),9,true,TERTIARY);n.setGravity(Gravity.CENTER);row.addView(n,new LinearLayout.LayoutParams(dp(24),dp(36)));LinearLayout copy=vbox();copy.addView(text(CapabilityRouter.label(cap),12,true,TEXT));TextView sub=text(polishedTitleV11(c),9,false,MUTED);sub.setSingleLine(true);sub.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(sub);row.addView(copy,new LinearLayout.LayoutParams(0,dp(36),1));card.addView(row);}Button use=primary("Use this workflow");use.setOnClickListener(v->{beginAskSelectionV10(goal);for(Cmd c:flow)if(!selected.contains(c))selected.add(c);home();});card.addView(use);target.addView(card);TextView meta=text("Each step comes from a different capability family, so the workflow adds coverage instead of duplicate prompts.",9,false,MUTED);meta.setPadding(0,dp(5),0,dp(8));target.addView(meta);
  }
  void renderAskResultsV8(LinearLayout target,String goal){
    target.removeAllViews();String q=goal==null?"":goal.trim();if(q.isEmpty())return;CapabilityRouter.Route route=CapabilityRouter.route(q);
    if(CapabilityRouter.IMAGE.equals(route.domain)&&route.broad&&CapabilityRouter.UNKNOWN.equals(route.mode)){renderImageModeChooserV8(target,q);return;}
    if(route.broad){renderCapabilityChooserV8(target,route.domain,q,route.mode);return;}
    if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode)&&route.capabilities.isEmpty()){renderImageModeChooserV8(target,q);return;}
    if(route.capabilities.size()>=2){renderCompoundWorkflowV8(target,q,route);return;}
    if(route.capabilities.size()==1){askCapability=route.capabilities.get(0);renderCapabilityRecommendationV8(target,q,askCapability);return;}
    ArrayList<Cmd> ranked=rankSmart(q,8);if(ranked.isEmpty()){LinearLayout e=surface(true);TextView t=text("Describe the outcome in a little more detail, or switch to Browse prompts.",11,false,MUTED);t.setPadding(0,dp(10),0,dp(10));e.addView(t);target.addView(e);return;}TextView best=text("BEST MATCH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(10),0,dp(5));target.addView(best);target.addView(bestMatchCard(ranked.get(0),q));TextView more=text("MORE MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(9),0,dp(5));target.addView(more);for(int i=1;i<Math.min(4,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}
  }

  void renderAskResults(LinearLayout target,String goal){renderAskResultsV8(target,goal);}
  void renderBrowseResultsV6(LinearLayout target,String query){
    target.removeAllViews();askSelectionGoal="";String q=query==null?"":query.trim();

    // Level 1: vertical category list. Never dump 3,375 prompts on first entry.
    if(q.isEmpty()&&!discoverFavorites&&discoverCategory.isEmpty()){
      TextView intro=text("Browse by category",15,true,TEXT);intro.setPadding(dp(1),dp(10),0,dp(8));target.addView(intro);
      for(Group g:groups){
        int n=groupCount(g);if(n<=0)continue;
        LinearLayout card=surface(false);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(15),dp(13),dp(13),dp(13));
        LinearLayout copy=vbox();TextView title=text(g.title,15,true,TEXT);TextView sub=text(g.sub,11,false,MUTED);sub.setMaxLines(2);TextView count=text(n+" prompts",10,true,TERTIARY);count.setPadding(0,dp(5),0,0);copy.addView(title);copy.addView(sub);copy.addView(count);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",26,false,MUTED));
        card.setOnClickListener(v->{discoverCategory=g.title;discoverSubcategory="";browseLimit=30;home();});target.addView(card);
      }
      TextView hint=text("Or search above to find a prompt across the entire library.",11,false,MUTED);hint.setPadding(dp(1),dp(8),0,dp(4));target.addView(hint);return;
    }

    // Level 2: vertical subcategory list, same visual language as existing lists.
    if(q.isEmpty()&&!discoverFavorites&&!discoverCategory.isEmpty()&&discoverSubcategory.isEmpty()){
      Button back=ghost("‹  All categories");back.setOnClickListener(v->{discoverCategory="";discoverSubcategory="";browseLimit=30;home();});target.addView(back);
      TextView heading=text(discoverCategory,18,true,TEXT);heading.setPadding(dp(1),dp(8),0,dp(2));target.addView(heading);
      TextView help=text("Choose what you want to do",12,false,MUTED);help.setPadding(dp(1),0,0,dp(8));target.addView(help);
      for(String sub:subcategoriesForV12(discoverCategory)){
        int n=subcategoryCountV12(discoverCategory,sub);if(n<=0)continue;
        LinearLayout card=surface(false);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(15),dp(12),dp(13),dp(12));
        LinearLayout copy=vbox();copy.addView(text(sub,15,true,TEXT));copy.addView(text(n+" prompts",11,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",26,false,MUTED));
        card.setOnClickListener(v->{discoverSubcategory=sub;browseLimit=30;home();});target.addView(card);
      }
      return;
    }

    // Level 3: vertical prompt list. Search may enter here directly.
    ArrayList<Cmd> rows=new ArrayList<>();
    if(q.isEmpty()){
      for(Cmd c:all){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }else{
      for(Cmd c:rankSmart(q,350)){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }
    if(q.isEmpty()&&!discoverSubcategory.isEmpty()){
      Button back=ghost("‹  "+discoverCategory);back.setOnClickListener(v->{discoverSubcategory="";browseLimit=30;home();});target.addView(back);
    }
    String scope=discoverFavorites?"Favorites":discoverCategory.isEmpty()?"Search results":discoverSubcategory.isEmpty()?discoverCategory:discoverCategory+"  ›  "+discoverSubcategory;
    TextView meta=text(scope+"  ·  "+rows.size(),10,true,TERTIARY);meta.setPadding(dp(1),dp(9),0,dp(5));target.addView(meta);
    if(rows.isEmpty()){LinearLayout e=surface(true);TextView t=text("No prompts match this search or filter.",11,false,MUTED);t.setGravity(Gravity.CENTER);t.setPadding(0,dp(15),0,dp(15));e.addView(t);target.addView(e);return;}
    int limit=Math.min(browseLimit,rows.size());for(int i=0;i<limit;i++){Cmd c=rows.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}if(limit<rows.size()){Button more=secondary("Show more  ("+(rows.size()-limit)+" remaining)");more.setOnClickListener(v->{browseLimit+=30;home();});target.addView(more);}
  }
  String composeStackPromptV9(String user){
    String u=user==null?"":user.trim();StringBuilder p=new StringBuilder();p.append("Use the user's request/context as the source of truth.\n\n");if(!u.isEmpty())p.append("USER REQUEST / CONTEXT:\n").append(u).append("\n\n");p.append("SELECTED PROMPT MODULES:\n");for(int i=0;i<selected.size();i++){Cmd c=selected.get(i);p.append("\nSTEP ").append(i+1).append(" — ").append(presentationTitleV8(c)).append("\n");p.append(resolveTemplate(c,u)).append("\n");}p.append("\nEXECUTION RULES:\n- Apply the selected modules in order, carrying forward only useful findings from earlier steps.\n- Each module is scoped to its step and must not override or block later modules.\n- Use tools or external capabilities only when they are actually available in the current ChatGPT conversation.\n- If one essential input is missing and cannot reasonably be inferred, ask one concise clarifying question; otherwise make a reasonable assumption and state it when important.\n- Produce one clear, coherent final answer rather than separate disconnected answers for each module.\n- Show useful conclusions, evidence and verification where relevant, but do not expose private chain-of-thought.\n");return p.toString();
  }
  void copyPromptTextV9(String value){android.content.ClipboardManager cb=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(cb==null){toast("Clipboard unavailable");return;}cb.setPrimaryClip(ClipData.newPlainText("PromptDeck prompt",value==null?"":value));toast("Prompt copied");}

  void showStackSheetMenu(View anchor,int index,android.app.Dialog sheet){
    PopupMenu p=new PopupMenu(this,anchor);if(index>0)p.getMenu().add("Move up");if(index<selected.size()-1)p.getMenu().add("Move down");p.getMenu().add("Remove");p.setOnMenuItemClickListener(item->{String t=item.getTitle().toString();if(t.equals("Move up")&&index>0)Collections.swap(selected,index,index-1);else if(t.equals("Move down")&&index<selected.size()-1)Collections.swap(selected,index,index+1);else if(t.equals("Remove"))selected.remove(index);sheet.dismiss();home();if(!selected.isEmpty())showStackSheet();return true;});p.show();
  }
  void showStackSheet(){
    if(selected.isEmpty()){toast("Choose a prompt first");return;}android.app.Dialog sheet=new android.app.Dialog(this);LinearLayout outer=vbox();outer.setPadding(dp(16),dp(12),dp(16),dp(16));outer.setBackground(shape(SURFACE,BORDER,24));LinearLayout head=hbox();head.setGravity(Gravity.CENTER_VERTICAL);LinearLayout hc=vbox();hc.addView(text("Ready to run",19,true,TEXT));hc.addView(text(selected.size()+" step"+(selected.size()==1?"":"s")+" in this workflow",10,false,MUTED));head.addView(hc,new LinearLayout.LayoutParams(0,-2,1));TextView close=text("×",24,false,MUTED);close.setGravity(Gravity.CENTER);close.setOnClickListener(v->sheet.dismiss());head.addView(close,new LinearLayout.LayoutParams(dp(38),dp(38)));outer.addView(head);ScrollView scroll=new ScrollView(this);LinearLayout list=vbox();for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout row=surface(true);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(8),dp(6),dp(7),dp(6));TextView num=text(String.valueOf(i+1),9,true,TERTIARY);num.setGravity(Gravity.CENTER);row.addView(num,new LinearLayout.LayoutParams(dp(22),dp(38)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);row.addView(ic,ip);LinearLayout copy=vbox();TextView tt=text(polishedTitleV11(c),12,true,TEXT);tt.setSingleLine(true);tt.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(tt);TextView dd=text(polishedOutcomeV11(c,""),9,false,MUTED);dd.setSingleLine(true);dd.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(dd);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView menu=text("⋯",19,false,TERTIARY);menu.setGravity(Gravity.CENTER);menu.setOnClickListener(v->showStackSheetMenu(v,k,sheet));row.addView(menu,new LinearLayout.LayoutParams(dp(30),dp(38)));list.addView(row);}scroll.addView(list);outer.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));TextView lab=text("Your request",11,true,TEXT);lab.setPadding(0,dp(8),0,dp(4));outer.addView(lab);EditText req=input("Paste text or describe what you want ChatGPT to work on...",3);req.setMaxLines(5);req.setText(contextDraft);outer.addView(req);Button copyPrompt=secondary("Copy final prompt");copyPrompt.setOnClickListener(v->{contextDraft=req.getText().toString();copyPromptTextV9(composeStackPromptV9(contextDraft));});outer.addView(copyPrompt);LinearLayout actions=hbox();Button add=secondary("Add prompt");add.setOnClickListener(v->{contextDraft=req.getText().toString();sheet.dismiss();discoverMode="browse";home();});Button run=primary("Run with ChatGPT");run.setOnClickListener(v->{contextDraft=req.getText().toString();sheet.dismiss();build();});actions.addView(add,new LinearLayout.LayoutParams(0,dp(44),1));Space gap=new Space(this);actions.addView(gap,new LinearLayout.LayoutParams(dp(8),1));actions.addView(run,new LinearLayout.LayoutParams(0,dp(44),1));outer.addView(actions);sheet.setContentView(outer);sheet.show();android.view.Window w=sheet.getWindow();if(w!=null){w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));w.setGravity(Gravity.BOTTOM);w.setLayout(-1,(int)(getResources().getDisplayMetrics().heightPixels*.86f));w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);android.view.WindowManager.LayoutParams lp=w.getAttributes();lp.dimAmount=.55f;w.setAttributes(lp);}
  }

  String[] subcategoriesForV12(String cat){
    if(cat.equals("Writing & Communication"))return new String[]{"Rewrite & Polish","Emails & Messages","Long-form Writing","Copywriting","Translation & Language"};
    if(cat.equals("Research & Analysis"))return new String[]{"Deep Research","Fact-checking & Sources","Summaries & Extraction","Compare & Evaluate","Analysis & Insights"};
    if(cat.equals("Planning & Decisions"))return new String[]{"Plans & Roadmaps","Projects & Execution","Decisions & Trade-offs","Productivity & Organization","Checklists & SOPs"};
    if(cat.equals("Work & Business"))return new String[]{"Career & Jobs","Meetings & Workplace","Strategy & Operations","Marketing & Sales","Finance & Entrepreneurship"};
    if(cat.equals("Technology & Data"))return new String[]{"Coding & Implementation","Debugging & Troubleshooting","Code Review & Testing","Data & SQL","Systems & DevOps","AI & Prompting"};
    if(cat.equals("Learning & Education"))return new String[]{"Explain & Understand","Tutoring","Study & Revision","Quizzes & Practice","Teaching & Lessons","STEM & Academic"};
    if(cat.equals("Creativity & Content"))return new String[]{"Brainstorming & Ideas","Storytelling & Creative Writing","Social Media","Scripts & Video","Branding & Creative Direction"};
    if(cat.equals("Images & Design"))return new String[]{"Image Generation","Photo Editing & Restore","Portraits & People","Background & Cleanup","Lighting & Color","Product & Commercial","Style & Transformation","Graphics & Posters"};
    if(cat.equals("Health & Life"))return new String[]{"Health & Wellness","Fitness & Nutrition","Habits & Self-Improvement","Relationships & Personal","Travel & Lifestyle"};
    return new String[0];
  }
  String taxonomySubcategoryV12(Cmd c,String cat){
    String h=(c.command+" "+c.description+" "+c.subcategory).toLowerCase(Locale.ROOT);
    if(cat.equals("Writing & Communication")){
      if(hasAny(h,"translate","translation","language","arabic","english","localize"))return"Translation & Language";
      if(hasAny(h,"email","reply","message","follow-up","followup","letter"))return"Emails & Messages";
      if(hasAny(h,"copywriting","headline","cta","landing page","ad copy","sales copy"))return"Copywriting";
      if(hasAny(h,"article","blog","essay","report","proposal","long form","long-form"))return"Long-form Writing";
      return"Rewrite & Polish";
    }
    if(cat.equals("Research & Analysis")){
      if(hasAny(h,"verify","fact check","fact-check","source","citation","evidence"))return"Fact-checking & Sources";
      if(hasAny(h,"summar","extract","key points","notes"))return"Summaries & Extraction";
      if(hasAny(h,"compare","comparison","evaluate","pros cons","proscons","benchmark"))return"Compare & Evaluate";
      if(hasAny(h,"research","deep dive","investigate","web research"))return"Deep Research";
      return"Analysis & Insights";
    }
    if(cat.equals("Planning & Decisions")){
      if(hasAny(h,"decision","tradeoff","trade-off","choose","recommend","matrix","regret"))return"Decisions & Trade-offs";
      if(hasAny(h,"checklist","sop","standard operating","procedure","todo","to-do"))return"Checklists & SOPs";
      if(hasAny(h,"priority","prioritize","organize","productivity","time management"))return"Productivity & Organization";
      if(hasAny(h,"project","execution","requirements","risk","milestone"))return"Projects & Execution";
      return"Plans & Roadmaps";
    }
    if(cat.equals("Work & Business")){
      if(hasAny(h,"resume","cv","cover letter","interview","career","job","ats"))return"Career & Jobs";
      if(hasAny(h,"meeting","minutes","workplace","professional communication","manager","team"))return"Meetings & Workplace";
      if(hasAny(h,"marketing","sales","campaign","customer","brand","seo","market"))return"Marketing & Sales";
      if(hasAny(h,"finance","financial","budget","investment","entrepreneur","startup","business model"))return"Finance & Entrepreneurship";
      return"Strategy & Operations";
    }
    if(cat.equals("Technology & Data")){
      if(hasAny(h,"prompt engineering","prompting","chatgpt","llm","agent","ai workflow","model"))return"AI & Prompting";
      if(hasAny(h,"debug","bug","error","fix","troubleshoot","root cause"))return"Debugging & Troubleshooting";
      if(hasAny(h,"review code","code review","test","testing","security review","lint"))return"Code Review & Testing";
      if(hasAny(h,"sql","database","data analysis","dataset","csv","spreadsheet","query"))return"Data & SQL";
      if(hasAny(h,"devops","cloud","linux","docker","kubernetes","network","system architecture","server"))return"Systems & DevOps";
      return"Coding & Implementation";
    }
    if(cat.equals("Learning & Education")){
      if(hasAny(h,"quiz","flashcard","test me","practice questions","exam questions"))return"Quizzes & Practice";
      if(hasAny(h,"study","revision","memorize","exam prep","learning plan"))return"Study & Revision";
      if(hasAny(h,"tutor","socratic","teach me interactively","coach me"))return"Tutoring";
      if(hasAny(h,"teacher","lesson","curriculum","classroom","teaching"))return"Teaching & Lessons";
      if(hasAny(h,"physics","chemistry","biology","mathematics","math ","science","stem","academic"))return"STEM & Academic";
      return"Explain & Understand";
    }
    if(cat.equals("Creativity & Content")){
      if(hasAny(h,"social media","caption","reel","instagram","tiktok","linkedin post","social post"))return"Social Media";
      if(hasAny(h,"script","video","youtube","podcast","scene","screenplay"))return"Scripts & Video";
      if(hasAny(h,"story","storytelling","character","fiction","creative writing"))return"Storytelling & Creative Writing";
      if(hasAny(h,"brand","creative direction","campaign concept","moodboard","concept"))return"Branding & Creative Direction";
      return"Brainstorming & Ideas";
    }
    if(cat.equals("Images & Design")){
      if(hasAny(h,"restore","enhance","upscale","sharpen","old photo","photo edit","image edit"))return"Photo Editing & Restore";
      if(hasAny(h,"background","remove object","remove person","cleanup","clean up","cutout"))return"Background & Cleanup";
      if(hasAny(h,"portrait","headshot","face","skin","hair","selfie","people"))return"Portraits & People";
      if(hasAny(h,"lighting","exposure","color grade","color grading","contrast","brightness"))return"Lighting & Color";
      if(hasAny(h,"product","commercial","ecommerce","advertising","packaging"))return"Product & Commercial";
      if(hasAny(h,"poster","thumbnail","banner","graphic","text overlay","carousel"))return"Graphics & Posters";
      if(hasAny(h,"style","cinematic","film","vintage","anime","watercolor","editorial","transformation"))return"Style & Transformation";
      return"Image Generation";
    }
    if(cat.equals("Health & Life")){
      if(hasAny(h,"fitness","workout","exercise","nutrition","diet","meal"))return"Fitness & Nutrition";
      if(hasAny(h,"habit","self improvement","self-improvement","personal growth","routine","goal"))return"Habits & Self-Improvement";
      if(hasAny(h,"relationship","dating","family","friend","communication"))return"Relationships & Personal";
      if(hasAny(h,"travel","trip","itinerary","home","food","lifestyle"))return"Travel & Lifestyle";
      return"Health & Wellness";
    }
    return"Other";
  }
  int subcategoryCountV12(String cat,String sub){int n=0;for(Cmd c:all)if(!c.custom&&cat.equals(c.category)&&sub.equals(c.subcategory))n++;return n;}
  void showSubcategoryPickerV12(){
    if(discoverCategory.isEmpty())return;String[] subs=subcategoriesForV12(discoverCategory);ArrayList<String> labels=new ArrayList<>();labels.add("All in "+discoverCategory);ArrayList<String> values=new ArrayList<>();values.add("");for(String sub:subs){int n=subcategoryCountV12(discoverCategory,sub);if(n<=0)continue;labels.add(sub+"  ("+n+")");values.add(sub);}new AlertDialog.Builder(this).setTitle(discoverCategory).setItems(labels.toArray(new String[0]),(d,which)->{discoverSubcategory=values.get(which);browseLimit=30;home();}).setNegativeButton("Cancel",null).show();
  }
  void showCategoryPicker(){
    String[] names=new String[groups.length+1];names[0]="All categories";for(int i=0;i<groups.length;i++)names[i+1]=groups[i].title+"  ("+groupCount(groups[i])+")";
    new AlertDialog.Builder(this).setTitle("Browse by category").setItems(names,(d,which)->{discoverMode="browse";discoverCategory=which==0?"":groups[which-1].title;discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();}).setNegativeButton("Cancel",null).show();
  }
  void showMoreMenu(){
    String[] items={"My Prompts","Favorites","Settings"};new AlertDialog.Builder(this).setTitle("PromptDeck").setItems(items,(d,which)->{if(which==0)showPromptCollectionDialog(false);else if(which==1)showPromptCollectionDialog(true);else showSimpleSettings();}).setNegativeButton("Close",null).show();
  }
  void showPromptCollectionDialog(boolean favorites){
    ArrayList<Cmd> rows=new ArrayList<>();for(Cmd c:all){if(favorites){if(isFavorite(c))rows.add(c);}else if(c.custom)rows.add(c);}String title=favorites?"Favorites":"My Prompts";
    if(rows.isEmpty()){new AlertDialog.Builder(this).setTitle(title).setMessage(favorites?"No favorites yet.":"No custom prompts yet.").setPositiveButton(favorites?"Done":"Create",(d,w)->{if(!favorites)showAdd();}).setNegativeButton(favorites?null:"Cancel",null).show();return;}
    String[] labels=new String[rows.size()];for(int i=0;i<rows.size();i++)labels[i]=displayTitle(rows.get(i));AlertDialog.Builder b=new AlertDialog.Builder(this).setTitle(title).setItems(labels,(d,which)->showPromptDialog(rows.get(which))).setNegativeButton("Close",null);if(!favorites)b.setPositiveButton("Create",(d,w)->showAdd());b.show();
  }
  void showSimpleSettings(){
    String[] items={"App Preferences","ChatGPT Connection","Data & Storage","About PromptDeck"};new AlertDialog.Builder(this).setTitle("Settings").setItems(items,(d,which)->{if(which==0)showAppPreferences();else if(which==1)showChatGPTConnection();else if(which==2)showDataStorage();else new AlertDialog.Builder(this).setTitle("PromptDeck 0.8.1").setMessage("3,375 ChatGPT-first prompts. Two-page interface: Discover and Stack.").setPositiveButton("Done",null).show();}).setNegativeButton("Close",null).show();
  }
  Group groupByTitle(String title){if(title==null||title.isEmpty())return null;for(Group g:groups)if(g.title.equals(title))return g;return null;}
  ArrayList<Cmd> recommendedPrompts(){
    ArrayList<Cmd> out=new ArrayList<>();String[] names={"eli5","summarize","rewrite","research","brainstorm","plan","compare","debug"};for(String n:names){Cmd c=find(n);if(c!=null&&!out.contains(c))out.add(c);}if(out.size()<8){for(Cmd c:rankSmart("useful clear everyday chatgpt",16)){if(!out.contains(c))out.add(c);if(out.size()>=8)break;}}return out;
  }
  void renderDiscoverResults(LinearLayout target,String query){
    target.removeAllViews();String q=query==null?"":query.trim();ArrayList<Cmd> rows=new ArrayList<>();
    if(q.isEmpty()&&discoverCategory.isEmpty()&&!discoverFavorites)rows.addAll(recommendedPrompts());
    else if(q.isEmpty()){
      if(discoverFavorites){for(Cmd c:all)if(isFavorite(c))rows.add(c);}else{Group g=groupByTitle(discoverCategory);if(g!=null)rows.addAll(groupCommands(g));}
    }else{
      for(Cmd c:rankSmart(q,120)){if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;rows.add(c);if(rows.size()>=30)break;}
    }
    String label=q.isEmpty()?(discoverFavorites?"Favorites":discoverCategory.isEmpty()?"Recommended":discoverCategory):"Best matches";TextView h=text(label,13,true,TEXT);h.setPadding(dp(1),dp(9),0,dp(6));target.addView(h);
    if(rows.isEmpty()){LinearLayout empty=surface(true);TextView e=text(discoverFavorites?"No favorites yet.":"No prompts match this view.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(18),0,dp(18));empty.addView(e);target.addView(empty);return;}
    int shown=0;for(Cmd c:rows){View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);if(++shown>=30)break;}
  }
  void showPromptDialog(Cmd c){android.app.Dialog sheet=new android.app.Dialog(this);LinearLayout outer=vbox();outer.setPadding(dp(16),dp(12),dp(16),dp(16));outer.setBackground(shape(SURFACE,BORDER,24));LinearLayout head=hbox();head.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(42),dp(42));ip.setMargins(0,0,dp(10),0);head.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(presentationTitleV8(c),16,true,TEXT));copy.addView(text(presentationOutcomeV8(c),10,false,MUTED));head.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView close=text("×",23,false,MUTED);close.setGravity(Gravity.CENTER);close.setOnClickListener(v->sheet.dismiss());head.addView(close,new LinearLayout.LayoutParams(dp(38),dp(38)));outer.addView(head);ScrollView scroll=new ScrollView(this);LinearLayout content=vbox();String body=c.instruction==null?"":c.instruction.trim();if(body.length()>1400)body=body.substring(0,1397).trim()+"…";TextView prompt=text(body,11,false,TEXT);prompt.setLineSpacing(dp(1),1.10f);prompt.setPadding(0,dp(10),0,dp(8));content.addView(prompt);ArrayList<String> vars=templateVariables(c.instruction);for(String key:vars){TextView l=text(prettyKey(key),10,true,MUTED);l.setPadding(0,dp(5),0,dp(3));content.addView(l);EditText field=input("Enter "+prettyKey(key).toLowerCase(Locale.ROOT),1);field.setText(promptVar(c.id,key));field.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int co,int a){}public void onTextChanged(CharSequence x,int st,int b,int co){setPromptVar(c.id,key,x.toString());}public void afterTextChanged(android.text.Editable e){}});content.addView(field);}Button fav=secondary(isFavorite(c)?"★  Favorited":"☆  Favorite");fav.setOnClickListener(v->{toggleFavorite(c);fav.setText(isFavorite(c)?"★  Favorited":"☆  Favorite");});content.addView(fav);scroll.addView(content);outer.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));LinearLayout actions=hbox();Button run=secondary("Run now");run.setOnClickListener(v->{sheet.dismiss();sendText(buildSinglePrompt(c,"ask".equals(discoverMode)?askGoal:""));});Button add=primary(selected.contains(c)?"Added":"Add to Stack");add.setEnabled(!selected.contains(c));add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);sheet.dismiss();home();});actions.addView(run,new LinearLayout.LayoutParams(0,dp(44),1));Space gap=new Space(this);actions.addView(gap,new LinearLayout.LayoutParams(dp(8),1));actions.addView(add,new LinearLayout.LayoutParams(0,dp(44),1));outer.addView(actions);sheet.setContentView(outer);sheet.show();android.view.Window w=sheet.getWindow();if(w!=null){w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));w.setGravity(Gravity.BOTTOM);w.setLayout(-1,(int)(getResources().getDisplayMetrics().heightPixels*.78f));w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);android.view.WindowManager.LayoutParams lp=w.getAttributes();lp.dimAmount=.5f;w.setAttributes(lp);}}

  String cleanUiText(String x){
    if(x==null)return"";String s=x.replaceAll("(?is)^\\s*for this step in a larger workflow:\\s*","").replaceAll("(?i)^\\s*(?:role|title)\\s*:\\s*","").replaceAll("(?m)^\\s*#+\\s*","").replaceAll("<[^>]+>"," ").replaceAll("\\s+"," ").trim();
    s=s.replaceAll("(?i)^handle the user request as an expert in\\s*","").replaceAll("(?i)^acts? as (?:an? )?","").replaceAll("(?i)^you are (?:an? )?","").trim();
    return s;
  }
  String repairJoinedWords(String x){
    if(x==null)return"";String s=x;
    s=s.replaceAll("(?i)compareoptions","Compare Options").replaceAll("(?i)interviewprep","Interview Prep").replaceAll("(?i)interviewproducer","Interview Producer").replaceAll("(?i)metaprompt","Meta Prompt").replaceAll("(?i)kickstartprompt","Kickstart Prompt");
    s=s.replaceAll("(?i)profilefrom","Profile From ").replaceAll("(?i)versionsof","Versions of ").replaceAll("(?i)promptin","Prompt in ").replaceAll("(?i)youarean","You Are an ").replaceAll("(?i)prompttolearnfree","AI Learning Resources ");
    s=s.replaceAll("(?i)chat gpt","ChatGPT").replaceAll("(?i)\\ba i\\b","AI").replaceAll("\\s+"," ").trim();return s;
  }
  String extractedCapability(Cmd c){
    String src=(c.description==null?"":c.description)+" "+(c.instruction==null?"":c.instruction);java.util.regex.Pattern[] ps={
      java.util.regex.Pattern.compile("(?i)#?\\s*TITLE\\s*:\\s*([^#\\n.;]{3,54})"),
      java.util.regex.Pattern.compile("(?i)(?:act|acts) as (?:an? )?([^,.;\\n]{3,54})"),
      java.util.regex.Pattern.compile("(?i)you are (?:an? )?([^,.;\\n]{3,54})")
    };
    for(java.util.regex.Pattern p:ps){java.util.regex.Matcher m=p.matcher(src);if(m.find()){String z=cleanUiText(m.group(1));if(z.length()>=3&&z.length()<=54)return z;}}
    return"";
  }
  boolean uglyCommand(Cmd c,String spaced){String raw=c.command==null?"":c.command;String low=raw.toLowerCase(Locale.ROOT);return raw.length()>30||(!raw.contains("_")&&!raw.contains("-")&&!raw.contains(" ")&&raw.length()>22)||low.contains("youare")||low.contains("prompttolearn")||low.contains("profilefrom")||low.contains("versionsof")||low.contains("promptin");}
  String titleCaseUi(String s){StringBuilder o=new StringBuilder();for(String w:s.trim().split("\\s+")){if(w.isEmpty())continue;if(o.length()>0)o.append(' ');String u=w.toUpperCase(Locale.ROOT);if(u.equals("AI")||u.equals("ATS")||u.equals("TCRE")||u.equals("CV")||u.equals("API")||u.equals("SQL")||u.equals("JSON")||u.equals("ChatGPT")){o.append(w.equalsIgnoreCase("chatgpt")?"ChatGPT":u);continue;}o.append(Character.toUpperCase(w.charAt(0))).append(w.length()>1?w.substring(1):"");}return o.toString();}
  void showStackMenu(View anchor,int index){
    if(index<0||index>=selected.size())return;PopupMenu p=new PopupMenu(this,anchor);android.view.Menu m=p.getMenu();if(index>0)m.add("Move up");if(index<selected.size()-1)m.add("Move down");m.add("Remove");p.setOnMenuItemClickListener(item->{String t=item.getTitle().toString();if(t.equals("Move up")&&index>0)Collections.swap(selected,index,index-1);else if(t.equals("Move down")&&index<selected.size()-1)Collections.swap(selected,index,index+1);else if(t.equals("Remove"))selected.remove(index);stack();return true;});p.show();
  }
  HashSet<String> meaningfulQueryTerms(String q){HashSet<String> out=new HashSet<>();String stop=" a an the to of for with and or in on my your something want need please create make get ";for(String t:(q==null?"":q.toLowerCase(Locale.ROOT)).replaceAll("[^a-z0-9]+"," ").trim().split("\\s+")){if(t.length()<2||stop.contains(" "+t+" "))continue;out.add(t);}return out;}
  boolean genericSearchTerm(String t){return t.equals("plan")||t.equals("prompt")||t.equals("help")||t.equals("make")||t.equals("create")||t.equals("something")||t.equals("thing");}
  void showAppPreferences(){new AlertDialog.Builder(this).setTitle("App Preferences").setMessage("PromptDeck uses the approved dark v0.8.1 interface. More preference controls can be added here without changing the locked visual system.").setPositiveButton("Done",null).show();}
  void showChatGPTConnection(){new AlertDialog.Builder(this).setTitle("ChatGPT Connection").setMessage("PromptDeck sends the composed prompt to the ChatGPT Android app through Android sharing. No separate API key is required for this flow.").setPositiveButton("Done",null).show();}
  void showDataStorage(){String[] items={"Paste custom prompts","Import prompt pack","Export custom prompts"};new AlertDialog.Builder(this).setTitle("Data & Storage").setItems(items,(d,which)->{if(which==0)showBulkPaste();else if(which==1)openImport();else openExport();}).setNegativeButton("Cancel",null).show();}

  String displayTitle(Cmd c){
    String k=c.command==null?"":c.command.toLowerCase(Locale.ROOT);
    if(k.equals("eli5"))return"Explain Like I'm 5 (ELI5)";if(k.equals("rewrite"))return"Rewrite for Clarity";if(k.equals("humanize"))return"Make It Sound More Human";if(k.equals("summarize"))return"Summarize";if(k.equals("research"))return"Research a Topic";if(k.equals("email")||k.equals("reply"))return"Email Reply";if(k.equals("compareoptions"))return"Compare Options";if(k.contains("promptingcoach"))return"AI Prompting Coach";if(k.contains("prompttolearnfree"))return"AI Learning Resources";if(k.equals("metaprompt"))return"Meta Prompt";
    String spaced=repairJoinedWords(c.command.replaceAll("([a-z0-9])([A-Z])","$1 $2").replaceAll("([A-Z]+)([A-Z][a-z])","$1 $2").replaceAll("[_-]+"," ").trim());
    String extracted=extractedCapability(c);if(uglyCommand(c,spaced)&&!extracted.isEmpty())spaced=extracted;
    spaced=spaced.replaceAll("(?i)\\s+(?:agent role|agent|role|skill imported|skill)$","").replaceAll("(?i)\\s+prompt$","").replaceAll("\\s+"," ").trim();
    if(spaced.equalsIgnoreCase("Chat GPT Prompt Refiner"))spaced="ChatGPT Prompt Refiner";
    if(spaced.toLowerCase(Locale.ROOT).contains("tcre framework"))spaced=spaced.replaceAll("(?i)A I","AI");
    String out=titleCaseUi(spaced);return out.isEmpty()?"Prompt":out;
  }
  String shortDescription(Cmd c){
    String d=cleanUiText(c.description);String title=displayTitle(c);
    if(d.isEmpty()||d.equalsIgnoreCase(title)||d.toLowerCase(Locale.ROOT).startsWith("handle the user request")||d.toLowerCase(Locale.ROOT).startsWith("for this step"))d="";
    if(d.matches("(?i)^(?:act|acts|you are).*")){String x=extractedCapability(c);d=x.isEmpty()?"Expert guidance for this task.":"Expert guidance for "+x+".";}
    if(d.isEmpty()){String x=cleanUiText(c.instruction);int cut=x.indexOf('.');if(cut>18)x=x.substring(0,cut+1);d=x;}
    d=d.replaceAll("(?i)^#?\\s*TITLE\\s*:\\s*","").replaceAll("\\s+"," ").trim();
    if(d.length()>82)d=d.substring(0,79).trim()+"…";return d.isEmpty()?"ChatGPT-ready workflow for this task.":d;
  }
  TextView smallTag(String label){TextView v=text(label,9,true,MUTED);v.setSingleLine(true);v.setPadding(dp(9),dp(5),dp(9),dp(5));v.setBackground(shape(SURFACE2,BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,-2);lp.setMargins(0,0,dp(6),0);v.setLayoutParams(lp);return v;}
  String[] detailTags(Cmd c){String sc=c.subcategory==null?"":c.subcategory.trim();String cat=displayGroupTitle(groupFor(c));if(sc.isEmpty()||"General".equalsIgnoreCase(sc))return new String[]{cat};return new String[]{cat,sc};}
  Set<String> favoriteIds(){return new HashSet<>(getSharedPreferences(PREFS,MODE_PRIVATE).getStringSet("favorite_prompt_ids",new HashSet<>()));}
  boolean isFavorite(Cmd c){return favoriteIds().contains(String.valueOf(c.id));}
  void toggleFavorite(Cmd c){Set<String> s=favoriteIds();String id=String.valueOf(c.id);if(s.contains(id))s.remove(id);else s.add(id);getSharedPreferences(PREFS,MODE_PRIVATE).edit().putStringSet("favorite_prompt_ids",s).apply();}
  void renderCategoryCards(LinearLayout target,String query){target.removeAllViews();String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);for(Group g:groups){String hay=(g.title+" "+displayGroupTitle(g)+" "+g.sub).toLowerCase(Locale.ROOT);if(!q.isEmpty()&&!hay.contains(q)){boolean hit=false;for(Cmd c:groupCommands(g)){if((displayTitle(c)+" "+c.description).toLowerCase(Locale.ROOT).contains(q)){hit=true;break;}}if(!hit)continue;}View card=groupCard(g);card.setOnClickListener(v->group(g));target.addView(card);}}
  void searchPage(){searchPage("","All");}
  void searchPage(String initial,String mode){discoverMode="browse";discoverPreset=initial==null?"":initial;discoverFavorites="Favorites".equals(mode);browseLimit=30;home();}
  void renderSearchResults(LinearLayout target,String query,String mode){
    target.removeAllViews();String q=query==null?"":query.trim();if("Categories".equals(mode)){renderCategoryCards(target,q);return;}if("Collections".equals(mode)){View a=menuCard("⚖","Compare & choose","Compare options and recommend the strongest fit");a.setOnClickListener(v->smartCollection("Compare & choose","Make better decisions","compare recommend decision options",null));target.addView(a);View b=menuCard("★","Best for ChatGPT","Prompt design and AI workflows");b.setOnClickListener(v->smartCollection("Best for ChatGPT","Top prompting workflows","chatgpt prompt optimize ai",null));target.addView(b);View c=menuCard("▣","Career toolkit","Resumes, interviews and professional communication");c.setOnClickListener(v->smartCollection("Career toolkit","Jobs, resumes, interviews","career resume interview email",null));target.addView(c);View d=menuCard("▥","Content studio","Writing, social and marketing workflows");d.setOnClickListener(v->smartCollection("Content studio","Blog, social, marketing","content hook script caption marketing",null));target.addView(d);return;}if(q.length()<2){View browse=menuCard("▦","Browse Categories","Explore the full canonical catalog");browse.setOnClickListener(v->browseCategories());target.addView(browse);TextView hint=text("Describe the outcome you want to rank relevant prompts.",10,false,MUTED);hint.setPadding(dp(2),dp(7),0,0);target.addView(hint);return;}ArrayList<Cmd> ranked=rankSmart(q,12);for(Cmd c:ranked){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,groupFor(c)));target.addView(row);}if(ranked.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No strong matches yet. Try a more specific outcome.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(16),0,dp(16));empty.addView(e);target.addView(empty);}
  }
  View settingsRow(int iconRes,String title,String sub){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);ImageView ic=vectorTile(iconRes,ACCENT);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));copy.addView(text(sub,9,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",20,false,TERTIARY));return card;}
  void settings(){showSimpleSettings();}
  ArrayList<String> templateVariables(String instruction){LinkedHashSet<String> out=new LinkedHashSet<>();String t=instruction==null?"":instruction;java.util.regex.Matcher a=java.util.regex.Pattern.compile("\\$\\{\\s*([A-Za-z][A-Za-z0-9 _-]{0,39})(?::[^}]*)?\\}").matcher(t);while(a.find())out.add(a.group(1).trim());java.util.regex.Matcher b=java.util.regex.Pattern.compile("\\[([A-Za-z][A-Za-z0-9 _-]{1,31})\\]").matcher(t);while(b.find()){String k=b.group(1).trim();if(!k.matches("(?i)(true|false|null|json|array|object|string|number|integer|items?)"))out.add(k);}return new ArrayList<>(out);}
  String prettyKey(String k){String x=k.replace('_',' ').replace('-',' ').trim();if(x.isEmpty())return"Value";return Character.toUpperCase(x.charAt(0))+x.substring(1);}
  String promptVar(int id,String key){HashMap<String,String> m=promptVars.get(id);return m==null?"":m.getOrDefault(key,"");}
  void setPromptVar(int id,String key,String value){HashMap<String,String> m=promptVars.get(id);if(m==null){m=new HashMap<>();promptVars.put(id,m);}m.put(key,value==null?"":value.trim());}
  String resolveTemplate(Cmd c,String user){String text=c.instruction;java.util.regex.Matcher a=java.util.regex.Pattern.compile("\\$\\{\\s*([A-Za-z][A-Za-z0-9 _-]{0,39})(?::([^}]*))?\\}").matcher(text);StringBuffer sb=new StringBuffer();while(a.find()){String key=a.group(1).trim(),def=a.group(2)==null?"":a.group(2).trim(),val=promptVar(c.id,key);if(val.isEmpty())val=!def.isEmpty()?def:(user==null||user.isEmpty()?"the "+prettyKey(key).toLowerCase(Locale.ROOT)+" specified by the user":"the relevant "+prettyKey(key).toLowerCase(Locale.ROOT)+" from the user's request");a.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(val));}a.appendTail(sb);text=sb.toString();java.util.regex.Matcher b=java.util.regex.Pattern.compile("\\[([A-Za-z][A-Za-z0-9 _-]{1,31})\\]").matcher(text);sb=new StringBuffer();while(b.find()){String key=b.group(1).trim();if(key.matches("(?i)(true|false|null|json|array|object|string|number|integer|items?)")){b.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(b.group(0)));continue;}String val=promptVar(c.id,key);if(val.isEmpty())val=(user==null||user.isEmpty()?"the "+prettyKey(key).toLowerCase(Locale.ROOT)+" specified by the user":"the relevant "+prettyKey(key).toLowerCase(Locale.ROOT)+" from the user's request");b.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(val));}b.appendTail(sb);return sb.toString();}
  String buildSinglePrompt(Cmd c,String user){
    String prompt=resolveTemplate(c,user).trim();
    String request=user==null?"":user.trim();
    if(request.isEmpty())return prompt;
    return prompt+"\n\n"+request;
  }
  void sendText(String text){Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,text);i.setPackage("com.openai.chatgpt");try{startActivity(i);}catch(Exception e){i.setPackage(null);startActivity(Intent.createChooser(i,"Send prompt"));}}
  GradientDrawable gradientShape(int left,int right,int stroke,int radius){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{left,right});g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}

  String subcat(String c,String group){if(group.contains("Writing")){if(has(c,"rewrite,rephrase,paraphrase,polish,proofread,grammar"))return"Rewrite & Improve";if(has(c,"humanize,professional,formal,casual,tone"))return"Tone & Style";if(has(c,"shorten,expand,simplify,clarify"))return"Length & Clarity";return"Language & Translation";}if(group.contains("Thinking")){if(has(c,"brainstorm,ideas,angles,alternative"))return"Generate Ideas";if(has(c,"critique,challenge,devilsadvocate,blindspots,counterexample"))return"Challenge & Critique";return"Reason & Decide";}if(group.contains("Research")){if(has(c,"research,sources,evidence,verify,facts"))return"Research & Verification";if(has(c,"compare,proscons"))return"Compare";return"Analyze & Extract";}if(group.contains("Planning")){if(has(c,"plan,strategy,roadmap"))return"Strategy & Roadmap";if(has(c,"requirements,constraints,risks,acceptance,spec"))return"Define the Work";return"Tasks & Execution";}if(group.contains("Learning")){if(has(c,"eli5,explain,steps,examples,analogy,teach"))return"Understand & Learn";return"Practice & Remember";}if(group.contains("Work")){if(has(c,"email,reply,followup,request,apology"))return"Messages & Email";if(has(c,"resume,coverletter,interview"))return"Career";return"Meetings";}if(group.contains("Content")){if(has(c,"hook,headline,caption,cta,viral"))return"Attention & Engagement";return"Content Formats";}if(group.contains("Technical")){if(has(c,"rootcause,debug,fix,check"))return"Diagnose & Fix";return"Improve & Validate";}if(group.contains("Photo Editing")){if(has(c,"ProHeadshot,StudioPro,Magazine,OldMoney,LowAngleHero,hdreal,cinematicportrait,FixFaceResolution"))return"Portrait & Editorial";if(has(c,"NeonCity,GoldenHour,Fog,RainyNight,SnowWorld,Autumn,MovieScene,Travelstory,storymytravel,cinematicTravel,documentrytravel,Travelvlog"))return"Cinematic & Travel";if(has(c,"LuxuryAd,DroneView,VintageFilm"))return"Commercial & Camera Styles";return"Creative Effects";}return"Structure & Convert";}
  String useWhen(Cmd c){String n=c.command;if(has(n,"compare,proscons,rank,recommend,decision"))return"When you have multiple options and want to understand the differences or make a better decision.";if(has(n,"research,verify,sources,evidence,facts"))return"When you need reliable information or want to verify a claim before relying on it.";if(has(n,"rewrite,rephrase,polish,proofread,grammar,humanize"))return"When you already have text and want to improve how it reads without starting from scratch.";if(has(n,"brainstorm,ideas,angles,alternative"))return"When you want more options, fresh ideas, or different directions to explore.";if(has(n,"debug,rootcause,fix,check,tests"))return"When something is wrong and you want to diagnose the cause and reach a testable fix.";if(has(n,"plan,strategy,roadmap,action,priority"))return"When you have a goal and want to turn it into a clear, practical sequence of actions.";return"When you want this capability as a focused step inside a larger request.";}
  String example(Cmd c){return"Apply /"+c.command+" to the request or material I provide and give me a clear, useful result.";}
  String[] relatedNames(String n){if(has(n,"research,verify,sources,evidence,facts"))return new String[]{"research","verify","sources","evidence","facts"};if(has(n,"critique,challenge,blindspots,devilsadvocate,improve"))return new String[]{"critique","challenge","blindspots","devilsadvocate","improve"};if(has(n,"rewrite,rephrase,polish,proofread,clarify,professional"))return new String[]{"rewrite","rephrase","clarify","polish","proofread","professional"};if(has(n,"plan,strategy,roadmap,action,priority"))return new String[]{"strategy","roadmap","priority","action"};if(has(n,"debug,rootcause,fix,check,tests"))return new String[]{"rootcause","debug","fix","tests","check"};if(has(n,"compare,proscons,rank,recommend,decision"))return new String[]{"compare","proscons","tradeoffs","rank","recommend"};if(has(n,"brainstorm,ideas,angles,alternative"))return new String[]{"brainstorm","angles","alternative","critique","rank"};return new String[0];}
  boolean has(String c,String csv){return Arrays.asList(csv.toLowerCase(Locale.ROOT).split(",")).contains(c.toLowerCase(Locale.ROOT));}Cmd find(String n){for(Cmd c:all)if(c.command.equalsIgnoreCase(n))return c;return null;}int nextId(){int m=10000;for(Cmd c:all)m=Math.max(m,c.id+1);return m;}

  void saveCustom(){JSONArray a=new JSONArray();for(Cmd c:all)if(c.custom)try{a.put(c.json());}catch(Exception ignored){}getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString(CUSTOM,a.toString()).apply();}
  void openImport(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");startActivityForResult(i,IMPORT_REQ);}void openExport(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"PromptDeck-custom.promptdeck.json");startActivityForResult(i,EXPORT_REQ);}void openExportAll(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"PromptDeck-ALL-prompts.json");startActivityForResult(i,EXPORT_ALL_REQ);}
  @Override protected void onActivityResult(int r,int result,Intent data){
    super.onActivityResult(r,result,data);
    if(r==LIBRARY_PICK_REQ){
      if(result!=RESULT_OK||data==null)return;
      String title=data.getStringExtra("library_title"), inst=data.getStringExtra("library_prompt"), cat=data.getStringExtra("library_category");
      if(title==null||inst==null||inst.trim().isEmpty())return;
      try{
        String slug=title.replaceAll("[^A-Za-z0-9]+","");if(slug.isEmpty())slug="LibraryPrompt";if(slug.length()>30)slug=slug.substring(0,30);
        String baseSlug=slug;int n=2;while(find(slug)!=null)slug=baseSlug+(n++);
        JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",slug);o.put("category","My Prompts");o.put("description",title);o.put("instruction",inst);Cmd c=new Cmd(o,false);all.add(c);selected.add(c);toast("Added "+title);stack();
      }catch(Exception e){toast("Could not add library prompt");}
      return;
    }
    if(result!=RESULT_OK||data==null||data.getData()==null)return;
    try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());else if(r==EXPORT_ALL_REQ)exportAllPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}
  }
  void importPack(Uri u)throws Exception{Object p=new JSONTokener(readUri(u)).nextValue();JSONArray a;if(p instanceof JSONArray)a=(JSONArray)p;else{JSONObject o=(JSONObject)p;a=o.has("commands")?o.getJSONArray("commands"):new JSONArray().put(o);}int n=0,skip=0;for(int i=0;i<a.length();i++)try{JSONObject o=a.getJSONObject(i);o.put("id",nextId());Cmd c=new Cmd(o,true);boolean dup=false;for(Cmd z:all)if(z.command.equals(c.command)&&z.instruction.equals(c.instruction))dup=true;if(dup){skip++;continue;}all.add(c);n++;}catch(Exception ignored){skip++;}saveCustom();toast("Imported "+n+(skip>0?" • skipped "+skip:""));library();}
  void exportPack(Uri u)throws Exception{JSONObject p=new JSONObject();p.put("format","promptdeck-pack");p.put("version",1);p.put("name","PromptDeck custom prompts");JSONArray a=new JSONArray();for(Cmd c:all)if(c.custom)a.put(c.json());p.put("commands",a);OutputStream out=getContentResolver().openOutputStream(u,"w");if(out==null)throw new IOException("Can't open destination");out.write(p.toString(2).getBytes(StandardCharsets.UTF_8));out.close();toast("Custom prompts exported");}void exportAllPack(Uri u)throws Exception{JSONObject pack=new JSONObject();pack.put("format","promptdeck-all-prompts");pack.put("version",1);pack.put("count",all.size());JSONArray a=new JSONArray();for(Cmd c:all){JSONObject o=c.json();o.put("custom",c.custom);a.put(o);}pack.put("commands",a);OutputStream out=getContentResolver().openOutputStream(u,"w");if(out==null)throw new IOException("Can't open destination");out.write(pack.toString(2).getBytes(StandardCharsets.UTF_8));out.close();toast("Exported all "+all.size()+" prompts");}
  void copy(){if(finalPrompt==null)return;copyPromptTextV9(finalPrompt.getText().toString());}
  void send(){if(finalPrompt==null)return;Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,finalPrompt.getText().toString());i.setPackage("com.openai.chatgpt");try{startActivity(i);}catch(Exception e){i.setPackage(null);startActivity(Intent.createChooser(i,"Send prompt"));}}

  LinearLayout surface(boolean compact){LinearLayout l=vbox();l.setPadding(dp(compact?10:12),dp(compact?8:10),dp(compact?10:12),dp(compact?8:10));l.setBackground(satinShape(SURFACE2,SURFACE,BORDER,14));l.setElevation(0);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(1),0,dp(6));l.setLayoutParams(lp);return l;}
  GradientDrawable satinShape(int top,int bottom,int stroke,int radius){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,new int[]{top,bottom});g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}
  GradientDrawable shape(int fill,int stroke,int radius){GradientDrawable g=new GradientDrawable();g.setColor(fill);g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}
  TextView text(String s,int sp,boolean bold,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(color);v.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);v.setTypeface(Typeface.create(bold?"sans-serif-medium":"sans-serif",Typeface.NORMAL));return v;}
  TextView section(String s,int count){TextView v=text(s+"  ·  "+count,11,true,MUTED);v.setAllCaps(true);v.setLetterSpacing(.06f);v.setPadding(dp(2),dp(5),0,dp(8));return v;}TextView label(String s){TextView v=text(s,10,true,ACCENT);v.setLetterSpacing(.14f);v.setPadding(0,dp(18),0,dp(7));return v;}
  TextView pill(String s){TextView v=text(s,9,true,ACCENT);v.setGravity(Gravity.CENTER);v.setPadding(dp(10),dp(6),dp(10),dp(6));v.setBackground(shape(SURFACE2,BORDER,18));return v;}
  Button styledButton(String textValue,int fill,int stroke,int color){Button x=new Button(this);x.setText(textValue);x.setAllCaps(false);x.setTextColor(color);x.setTextSize(12);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));if(fill==ACCENT)x.setBackground(gradientShape(ACCENT,PURPLE,Color.rgb(80,126,255),14));else x.setBackground(satinShape(SURFACE2,SURFACE,stroke,14));x.setElevation(0);x.setPadding(dp(10),dp(6),dp(10),dp(6));x.setMinHeight(dp(44));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(44));lp.setMargins(0,dp(3),0,dp(3));x.setLayoutParams(lp);return x;}
  Button navBack(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(TEXT);x.setTextSize(12);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(10),0,dp(10),0);x.setBackground(satinShape(Color.rgb(29,35,43),Color.rgb(20,25,32),BORDER,9));x.setElevation(dp(2));return x;}
  Button primary(String s){return styledButton(s,ACCENT,Color.rgb(80,126,255),Color.WHITE);}Button secondary(String s){return styledButton(s,SURFACE2,BORDER,TEXT);}Button ghost(String s){return styledButton(s,SURFACE,BORDER,TEXT);}Button mini(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(MUTED);x.setTextSize(14);x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(8),dp(6),dp(8),dp(6));x.setBackground(shape(SURFACE2,BORDER,8));return x;}
  Button compactControl(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(MUTED);x.setTextSize(11);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(6),0,dp(6),0);x.setBackground(shape(SURFACE2,BORDER,8));return x;}
  EditText input(String hint,int lines){EditText e=new EditText(this);e.setHint(hint);e.setHintTextColor(TERTIARY);e.setTextColor(TEXT);e.setTextSize(12);e.setGravity((lines==1?Gravity.CENTER_VERTICAL:Gravity.TOP)|Gravity.START);e.setSingleLine(lines==1);e.setMinLines(lines);e.setPadding(dp(12),lines==1?0:dp(9),dp(12),lines==1?0:dp(9));e.setBackground(shape(INPUT,BORDER,14));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,lines==1?dp(42):-2);lp.setMargins(0,dp(2),0,dp(7));e.setLayoutParams(lp);return e;}
  LinearLayout vbox(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}LinearLayout hbox(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.HORIZONTAL);return l;}void spacer(int h){Space s=new Space(this);root.addView(s,new LinearLayout.LayoutParams(1,dp(h)));}int dp(int x){return Math.round(x*getResources().getDisplayMetrics().density);}void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
  String readAsset(String n)throws IOException{return slurp(getAssets().open(n));}String readUri(Uri u)throws IOException{return slurp(getContentResolver().openInputStream(u));}String slurp(InputStream in)throws IOException{if(in==null)throw new IOException("Can't open file");ByteArrayOutputStream o=new ByteArrayOutputStream();byte[]b=new byte[4096];int n;while((n=in.read(b))>0)o.write(b,0,n);in.close();return o.toString(StandardCharsets.UTF_8.name());}
}
