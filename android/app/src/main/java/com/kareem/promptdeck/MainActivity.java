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
  static final int IMPORT_REQ=1001, EXPORT_REQ=1002;
  static final String PREFS="promptdeck", CUSTOM="custom_commands_v1";
  static final int BG=Color.rgb(8,10,14), SURFACE=Color.rgb(18,21,27), SURFACE2=Color.rgb(25,29,37), BORDER=Color.rgb(47,54,66);
  static final int TEXT=Color.rgb(248,249,251), MUTED=Color.rgb(143,152,168), ACCENT=Color.rgb(47,107,255), SUCCESS=Color.rgb(65,200,120);
  static final int SATIN_TOP=Color.rgb(27,31,39), SATIN_BOTTOM=Color.rgb(16,19,25), SATIN_EDGE=Color.rgb(52,61,75);

  static class Cmd {
    int id; String command,category,description,instruction; boolean custom;
    Cmd(JSONObject o, boolean custom) throws JSONException {
      id=o.optInt("id",0); command=clean(o.optString("command","")); category=o.optString("category","Custom").trim();
      description=o.optString("description",o.optString("description_ar","")).trim(); instruction=o.optString("instruction","").trim(); this.custom=custom;
      if(command.isEmpty()||instruction.isEmpty()) throw new JSONException("command and instruction are required");
    }
    JSONObject json() throws JSONException { JSONObject o=new JSONObject();o.put("id",id);o.put("command",command);o.put("category",category);o.put("description",description);o.put("instruction",instruction);return o; }
    static String clean(String s){s=s==null?"":s.trim();while(s.startsWith("/"))s=s.substring(1);return s.replaceAll("[^A-Za-z0-9_-]","");}
  }
  static class Group { String title,sub,icon; String[] names; Group(String icon,String title,String sub,String...names){this.icon=icon;this.title=title;this.sub=sub;this.names=names;} }

  final ArrayList<Cmd> all=new ArrayList<>(), selected=new ArrayList<>();
  LinearLayout root; EditText context,finalPrompt;
  String page="home"; Group currentGroup=null; String contextDraft="";

  final Group[] groups={
    new Group("✦","Writing & Rewriting","Write, rewrite, polish and improve text","rewrite","rephrase","paraphrase","polish","proofread","grammar","shorten","expand","simplify","clarify","humanize","professional","formal","casual","tone","translate","arabic"),
    new Group("◈","Thinking & Ideas","Generate ideas, challenge assumptions and make decisions","brainstorm","ideas","angles","alternative","critique","challenge","devilsadvocate","blindspots","assumptions","firstprinciples","counterexample","socratic","tradeoffs","decision","recommend","rank"),
    new Group("⌕","Research & Analysis","Research, verify, compare and understand information","research","verify","sources","evidence","facts","deepdive","insights","trends","data","compare","proscons","summary","summarize","extract","classify"),
    new Group("◇","Planning & Execution","Turn goals into priorities, plans and executable steps","plan","strategy","roadmap","checklist","todo","priority","workflow","timeline","action","requirements","constraints","risks","acceptance","spec","estimate"),
    new Group("◎","Learning & Study","Explain, learn, review and practice effectively","eli5","explain","steps","examples","analogy","study","quiz","flashcards","teach","hint","test","review","memorize","mistakes"),
    new Group("▣","Work & Career","Emails, resumes, interviews and meetings","email","reply","followup","request","apology","resume","coverletter","interview","meeting","minutes"),
    new Group("△","Content Creation","Hooks, scripts, social content and storytelling","hook","caption","script","carousel","reel","viral","cta","story","headline"),
    new Group("⚙","Problem Solving & Technical","Diagnose, fix, test and improve solutions","rootcause","debug","fix","check","optimize","better","edgecases","refactor","tests","security","rubric","score"),
    new Group("▦","Data & Formatting","Structure, transform and present information","table","bullets","outline","format","json","csv","schema","template","prompt"),
    new Group("◉","Photo Editing & Image Generation","Image editing, visual styles and generation presets","NeonCity","GoldenHour","MiniWorld","Fog","LuxuryAd","LowAngleHero","VintageFilm","DroneView","Magazine","RainyNight","ProHeadshot","SnowWorld","DoubleExposure","OldMoney","StudioPro","Autumn","MovieScene","hdreal","cinematicportrait","doubleexposureviral","Travelstory","storymytravel","cinematicTravel","documentrytravel","Travelvlog","FixFaceResolution")
  };

  @Override public void onCreate(Bundle b){super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().getDecorView().setSystemUiVisibility(0);load();home();}

  @Override public void onBackPressed(){
    if("stack".equals(page)){home();return;}
    if("addMore".equals(page)||"build".equals(page)){stack();return;}
    if("group".equals(page)||"library".equals(page)){home();return;}
    if("detail".equals(page)){if(currentGroup!=null)group(currentGroup);else home();return;}
    if("customDetail".equals(page)){library();return;}
    super.onBackPressed();
  }

  void load(){all.clear();try{JSONArray a=new JSONArray(readAsset("commands.json"));for(int i=0;i<a.length();i++)all.add(new Cmd(a.getJSONObject(i),false));JSONArray c=new JSONArray(getSharedPreferences(PREFS,MODE_PRIVATE).getString(CUSTOM,"[]"));for(int i=0;i<c.length();i++)try{all.add(new Cmd(c.getJSONObject(i),true));}catch(Exception ignored){}}catch(Exception e){throw new RuntimeException(e);}seedPhotoCommands();seedExtraPhotoCommands();englishizeDescriptions();}

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
    String t=prompt.replaceAll("\s+"," ").trim();
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
    ScrollView sv=new ScrollView(this); sv.setFillViewport(true); sv.setBackgroundColor(BG);
    root=vbox(); root.setPadding(dp(16),dp(10),dp(16),dp(28));root.setClipChildren(false);root.setClipToPadding(false);sv.setClipToPadding(false); sv.addView(root); setContentView(sv);
    sv.setOnApplyWindowInsetsListener((v,insets)->{
      int top=insets.getSystemWindowInsetTop();
      int bottom=insets.getSystemWindowInsetBottom();
      root.setPadding(dp(16),top+dp(10),dp(16),bottom+dp(28));
      return insets;
    });
    sv.requestApplyInsets();
    LinearLayout top=hbox(); top.setGravity(Gravity.CENTER_VERTICAL);
    if("Prompt Stack".equals(title)||"Add more commands".equals(title)||"Final Prompt".equals(title)){
      Button back=navBack("‹  Back");back.setOnClickListener(v->{if("Prompt Stack".equals(title))home();else stack();});
      LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-2,dp(36));bp.setMargins(0,0,dp(10),0);top.addView(back,bp);
    }
    TextView brand=text("PromptDeck",14,true,TEXT); brand.setLetterSpacing(0f); top.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
    if(showStack){TextView stack=pill(selected.isEmpty()?"STACK":"STACK  "+selected.size());stack.setOnClickListener(v->stack());top.addView(stack);} root.addView(top);
    TextView ttl=text(title,26,true,TEXT); ttl.setPadding(0,dp(14),0,dp(4)); ttl.setTextDirection(View.TEXT_DIRECTION_LTR); root.addView(ttl);
    if(sub!=null&&!sub.isEmpty()){TextView st=text(sub,14,false,MUTED);st.setLineSpacing(0,1.14f);st.setPadding(0,0,0,dp(14));st.setGravity(Gravity.START);root.addView(st);} }

  void home(){
    page="home"; currentGroup=null;
    base("Choose a category","Browse prompt tools by category. Open any category, choose a prompt, review what it does, then add it to your Stack.",true);
    for(Group g:groups){View c=groupCard(g);c.setOnClickListener(v->group(g));root.addView(c);} spacer(8);
    View library=menuCard("＋","My Prompt Library","أضف أو استورد أو صدّر prompts خاصة بيك");library.setOnClickListener(v->library());root.addView(library);
    if(!selected.isEmpty()){spacer(10);Button compose=primary("Build prompt from "+selected.size()+" selected command"+(selected.size()==1?"":"s"));compose.setOnClickListener(v->stack());root.addView(compose);}
    TextView foot=text("120 built-in prompt operators  •  local library  •  no API required",11,false,MUTED);foot.setGravity(Gravity.CENTER);foot.setPadding(0,dp(24),0,0);root.addView(foot);
  }

  View groupCard(Group g){
    LinearLayout card=surface(false); card.setOrientation(LinearLayout.HORIZONTAL); card.setGravity(Gravity.CENTER_VERTICAL);
    TextView icon=text(g.icon,22,true,ACCENT); icon.setGravity(Gravity.CENTER); GradientDrawable circle=shape(SURFACE2,BORDER,20);circle.setStroke(dp(1),BORDER);icon.setBackground(circle);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(14),0);card.addView(icon,ip);
    LinearLayout copy=vbox();TextView title=text(g.title,17,true,TEXT);TextView sub=text(g.sub,13,false,MUTED);copy.addView(title);copy.addView(sub);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView arrow=text("›",28,false,MUTED);card.addView(arrow);return card;
  }
  View menuCard(String icon,String title,String sub){
    LinearLayout card=surface(false);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView ic=text(icon,23,false,ACCENT);ic.setGravity(Gravity.CENTER);card.addView(ic,new LinearLayout.LayoutParams(dp(44),dp(44)));LinearLayout copy=vbox();copy.addView(text(title,16,true,TEXT));copy.addView(text(sub,13,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",28,false,MUTED));return card;
  }

  void group(Group g){
    page="group"; currentGroup=g;
    base(g.title,g.sub,true);
    LinkedHashMap<String,ArrayList<Cmd>> subs=new LinkedHashMap<>();for(String n:g.names){Cmd c=find(n);if(c!=null){String sc=subcat(c.command,g.title);if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);}}for(Cmd c:all){if(!c.custom||!c.category.equalsIgnoreCase(g.title))continue;String sc=g.title.contains("Photo Editing")?"Imported Photo Prompts":"Custom";if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);}
    for(Map.Entry<String,ArrayList<Cmd>> en:subs.entrySet()){
      root.addView(section(en.getKey(),en.getValue().size()));
      LinearLayout block=vbox(); block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2)); block.setPadding(0,dp(2),0,dp(2));
      int index=0;for(Cmd c:en.getValue()){View row=commandRow(c,index++<en.getValue().size()-1);row.setOnClickListener(v->detail(c,g));block.addView(row);}root.addView(block);spacer(12);
    }
    Button back=ghost("←  Categories");back.setOnClickListener(v->home());root.addView(back);
  }

  View commandRow(Cmd c,boolean divider){
    LinearLayout wrap=vbox();wrap.setPadding(dp(14),dp(11),dp(12),dp(9));LinearLayout line=hbox();line.setGravity(Gravity.CENTER_VERTICAL);
    TextView name=text("/"+c.command,15,true,TEXT);name.setTextDirection(View.TEXT_DIRECTION_LTR);name.setGravity(Gravity.START);name.setSingleLine(true);line.addView(name,new LinearLayout.LayoutParams(0,-2,1));if(selected.contains(c)){TextView tick=text("SELECTED",9,true,SUCCESS);tick.setLetterSpacing(.12f);line.addView(tick);}else line.addView(text("›",24,false,MUTED));wrap.addView(line);
    TextView d=text(c.description,12,false,MUTED);d.setTextDirection(View.TEXT_DIRECTION_RTL);d.setGravity(Gravity.END);d.setPadding(0,dp(4),0,0);wrap.addView(d);
    if(divider){View v=new View(this);v.setBackgroundColor(BORDER);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(1));lp.setMargins(0,dp(11),0,0);wrap.addView(v,lp);}return wrap;
  }

  void detail(Cmd c,Group g){
    page="detail"; currentGroup=g;
    base("/"+c.command,c.description,true);
    info("WHAT IT DOES",c.description);
    info("USE IT WHEN",useWhen(c));
    info("EXAMPLE","/"+c.command+"  "+example(c));
    info("INSTRUCTION SENT TO CHATGPT",c.instruction);
    relatedActions(c.command);
    Button add=selected.contains(c)?secondary("✓  Added to Prompt Stack"):primary("＋  Add to Prompt Stack");add.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added /"+c.command);}stack();});root.addView(add);
    Button back=ghost("←  "+g.title);back.setOnClickListener(v->group(g));root.addView(back);
  }

  void info(String label,String body){TextView l=text(label,10,true,ACCENT);l.setLetterSpacing(.14f);l.setPadding(0,dp(14),0,dp(6));root.addView(l);LinearLayout box=surface(true);TextView b=text(body,15,false,TEXT);b.setLineSpacing(0,1.18f);b.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);box.addView(b);root.addView(box);}

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
    boolean added=selected.contains(c);Button x=new Button(this);x.setAllCaps(false);x.setText((added?"✓  ":"＋  ")+"/"+c.command);x.setTextColor(added?SUCCESS:TEXT);x.setTextSize(12);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setTextDirection(View.TEXT_DIRECTION_LTR);x.setSingleLine(true);x.setMinWidth(0);x.setMinHeight(dp(40));x.setPadding(dp(12),0,dp(12),0);x.setBackground(shape(SURFACE2,added?Color.rgb(35,134,54):BORDER,8));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(40));lp.setMargins(0,0,dp(8),0);x.setLayoutParams(lp);x.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added /"+c.command);x.setText("✓  /"+c.command);x.setTextColor(SUCCESS);x.setBackground(shape(SURFACE2,Color.rgb(35,134,54),8));}else toast("/"+c.command+" is already in the stack");});return x;
  }

  void stack(){
    if(context!=null)contextDraft=context.getText().toString();
    page="stack";
    base("Prompt Stack",selected.isEmpty()?"No prompts selected yet.":"Arrange your prompts in order. Each step builds on the useful output of the previous one.",false);
    if(selected.isEmpty()){
      LinearLayout empty=surface(true);TextView e=text("Start by browsing Categories and add one or more prompts.",14,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(24),0,dp(24));empty.addView(e);root.addView(empty);
      Button browse=primary("Browse categories");browse.setOnClickListener(v->home());root.addView(browse);return;
    }
    for(int i=0;i<selected.size();i++){
      final int k=i; Cmd c=selected.get(i);
      LinearLayout card=surface(false); card.setPadding(dp(14),dp(12),dp(14),dp(10));

      LinearLayout top=hbox(); top.setGravity(Gravity.CENTER_VERTICAL);
      TextView num=text(String.format(Locale.ROOT,"%02d",i+1),10,true,ACCENT);num.setLetterSpacing(.12f);num.setGravity(Gravity.CENTER);
      top.addView(num,new LinearLayout.LayoutParams(dp(36),dp(32)));
      TextView command=text("/"+c.command,16,true,TEXT);command.setTextDirection(View.TEXT_DIRECTION_LTR);command.setGravity(Gravity.START);command.setSingleLine(true);
      top.addView(command,new LinearLayout.LayoutParams(0,-2,1));
      card.addView(top);

      TextView desc=text(c.description,12,false,MUTED);desc.setTextDirection(View.TEXT_DIRECTION_RTL);desc.setGravity(Gravity.END);desc.setLineSpacing(0,1.12f);desc.setPadding(dp(36),dp(4),0,dp(10));card.addView(desc);

      LinearLayout controls=hbox();controls.setGravity(Gravity.END|Gravity.CENTER_VERTICAL);
      Button up=compactControl("↑  Up"),dn=compactControl("↓  Down"),rm=compactControl("×  Remove");
      up.setEnabled(k>0); up.setAlpha(k>0?1f:.35f); dn.setEnabled(k<selected.size()-1); dn.setAlpha(k<selected.size()-1?1f:.35f);
      up.setOnClickListener(v->{if(k>0)Collections.swap(selected,k,k-1);stack();});
      dn.setOnClickListener(v->{if(k<selected.size()-1)Collections.swap(selected,k,k+1);stack();});
      rm.setOnClickListener(v->{selected.remove(k);stack();});
      LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,dp(36),1);cp.setMargins(dp(3),0,dp(3),0);
      controls.addView(up,cp);controls.addView(dn,new LinearLayout.LayoutParams(cp));controls.addView(rm,new LinearLayout.LayoutParams(cp));
      card.addView(controls);
      root.addView(card);
    }
    root.addView(label("YOUR REQUEST / CONTEXT"));
    context=input("Enter your request, text or context here…",3);context.setMaxLines(8);context.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);context.setText(contextDraft);root.addView(context);
    Button build=primary("Build final prompt");build.setOnClickListener(v->build());root.addView(build);
    Button more=ghost("＋  Add more commands");more.setOnClickListener(v->{contextDraft=context==null?contextDraft:context.getText().toString();addMore();});root.addView(more);
  }

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
      TextView hint=text("Suggestions based on your current Stack. Tap any prompt to add it instantly.",12,false,MUTED);hint.setTextDirection(View.TEXT_DIRECTION_RTL);hint.setGravity(Gravity.END);hint.setPadding(0,0,0,dp(10));root.addView(hint);
    }

    root.addView(label("ALL COMMANDS"));
    for(Group g:groups){
      TextView gh=section(g.title,availableCount(g));root.addView(gh);
      LinearLayout block=vbox();block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2));block.setPadding(0,dp(2),0,dp(2));
      int shown=0,total=availableCount(g);
      for(String n:g.names){
        Cmd c=find(n);if(c==null)continue;
        boolean divider=shown<total-1;View row=pickCommandRow(c,divider);block.addView(row);shown++;
      }
      root.addView(block);spacer(10);
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
    LinearLayout wrap=vbox();wrap.setPadding(dp(14),dp(10),dp(12),dp(8));
    LinearLayout line=hbox();line.setGravity(Gravity.CENTER_VERTICAL);
    TextView name=text("/"+c.command,15,true,TEXT);name.setTextDirection(View.TEXT_DIRECTION_LTR);name.setGravity(Gravity.START);name.setSingleLine(true);line.addView(name,new LinearLayout.LayoutParams(0,-2,1));
    TextView state=text(selected.contains(c)?"✓ ADDED":"＋ ADD",10,true,selected.contains(c)?SUCCESS:ACCENT);state.setLetterSpacing(.08f);line.addView(state);wrap.addView(line);
    TextView d=text(c.description,12,false,MUTED);d.setTextDirection(View.TEXT_DIRECTION_RTL);d.setGravity(Gravity.END);d.setPadding(0,dp(3),0,0);wrap.addView(d);
    wrap.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added /"+c.command);addMore();}else{selected.remove(c);toast("Removed /"+c.command);addMore();}});
    if(divider){View sep=new View(this);sep.setBackgroundColor(BORDER);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(1));lp.setMargins(0,dp(10),0,0);wrap.addView(sep,lp);}return wrap;
  }

  ArrayList<Cmd> suggestedForStack(){
    LinkedHashSet<String> names=new LinkedHashSet<>();
    for(Cmd current:selected)for(String n:relatedNames(current.command))if(!n.equals(current.command))names.add(n);
    ArrayList<Cmd> out=new ArrayList<>();for(String n:names){Cmd c=find(n);if(c!=null&&!selected.contains(c))out.add(c);}return out;
  }

  void build(){
    page="build";
    String user=context==null?"":context.getText().toString().trim();base("Final Prompt","Your composed prompt is ready to copy or send to ChatGPT.",false);
    StringBuilder p=new StringBuilder("Help me with the request below by following these steps in order. Each step should build on the useful findings of the previous one.\n\n");for(int i=0;i<selected.size();i++){Cmd c=selected.get(i);p.append(i+1).append(". /").append(c.command).append('\n').append("   ").append(c.instruction).append('\n');}if(!user.isEmpty())p.append("\nMy request / context:\n").append(user);p.append("\n\nGive me one clear, coherent final answer. Show useful conclusions and evidence, but do not expose private chain-of-thought.");
    finalPrompt=input("",11);finalPrompt.setText(p);finalPrompt.setTextSize(14);root.addView(finalPrompt);Button send=primary("Open in ChatGPT");send.setOnClickListener(v->send());root.addView(send);Button copy=secondary("Copy prompt");copy.setOnClickListener(v->copy());root.addView(copy);Button edit=ghost("←  Edit stack");edit.setOnClickListener(v->stack());root.addView(edit);
  }

  void library(){
    page="library";
    base("Prompt Library",all.size()+" prompts available  •  custom prompts stay on this device",true);
    View add=menuCard("＋","Add prompt","Create one custom command manually");add.setOnClickListener(v->showAdd());root.addView(add);View paste=menuCard("⌁","Paste prompts","Paste simple command lines or complete multi-line prompts. PromptDeck separates them and creates descriptions automatically");paste.setOnClickListener(v->showBulkPaste());root.addView(paste);View imp=menuCard("↓","Import pack","Import a .promptdeck.json library");imp.setOnClickListener(v->openImport());root.addView(imp);View exp=menuCard("↑","Export custom","Back up or move your custom prompts");exp.setOnClickListener(v->openExport());root.addView(exp);
    ArrayList<Cmd> custom=new ArrayList<>();for(Cmd c:all)if(c.custom)custom.add(c);if(!custom.isEmpty()){spacer(10);root.addView(section("My custom prompts",custom.size()));LinearLayout block=vbox();block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2));for(int i=0;i<custom.size();i++){Cmd c=custom.get(i);View row=commandRow(c,i<custom.size()-1);row.setOnClickListener(v->customDetail(c));block.addView(row);}root.addView(block);}Button back=ghost("←  Categories");back.setOnClickListener(v->home());root.addView(back);
  }
  void customDetail(Cmd c){
    page="customDetail";base("/"+c.command,c.description,true);info("INSTRUCTION SENT TO CHATGPT",c.instruction);Button add=selected.contains(c)?secondary("✓  Added to Prompt Stack"):primary("＋  Add to Prompt Stack");add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);stack();});root.addView(add);Button del=ghost("Delete custom prompt");del.setOnClickListener(v->confirmDelete(c));root.addView(del);}

  void showBulkPaste(){
    LinearLayout box=vbox();box.setPadding(dp(18),dp(4),dp(18),0);
    EditText category=input("Category (default: Photo Editing & Image Generation)",1);category.setText("Photo Editing & Image Generation");
    EditText bulk=input("Paste anything here…\n\nSimple:\n/NeonCity → Cyberpunk night portrait\n\nOr full prompt blocks:\n/NeonPortrait\nCreate a dramatic cyberpunk portrait at night with neon reflections, rain, cinematic contrast...\n\n/StudioClean\nCreate a clean professional studio portrait with soft key light...",14);
    box.addView(category);box.addView(bulk);
    TextView note=text("Description is optional. If you paste a full prompt, PromptDeck will derive a short description from the prompt automatically.",12,false,MUTED);note.setPadding(0,dp(4),0,dp(8));box.addView(note);
    AlertDialog d=new AlertDialog.Builder(this).setTitle("Smart paste prompts").setView(box).setNegativeButton("Cancel",null).setPositiveButton("Parse & add",null).create();
    d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String cat=category.getText().toString().trim();if(cat.isEmpty())cat="Photo Editing & Image Generation";int[] result=parseBulkCommands(bulk.getText().toString(),cat);if(result[0]==0){toast("No prompts found. Start each prompt with /CommandName");return;}saveCustom();d.dismiss();library();toast("Added "+result[0]+" prompts"+(result[1]>0?" • skipped "+result[1]:""));}));d.show();
  }

  int[] parseBulkCommands(String raw,String category){
    int added=0,skipped=0;
    java.util.regex.Pattern header=java.util.regex.Pattern.compile("^\s*(?:\d+[.)]\s*)?/([A-Za-z0-9_-]+)(?:\s*(?:→|->|—|–|:|\\||=)\s*(.*))?\s*$");
    String currentName=null,currentInline=null;StringBuilder body=new StringBuilder();
    ArrayList<String[]> blocks=new ArrayList<>();
    for(String line:raw.split("\\r?\\n")){
      java.util.regex.Matcher m=header.matcher(line.trim());
      if(m.matches()){
        if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});
        currentName=m.group(1);currentInline=m.group(2)==null?"":m.group(2).trim();body.setLength(0);
      }else if(currentName!=null){if(body.length()>0)body.append("
");body.append(line);}
    }
    if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});
    for(String[] b:blocks){String name=b[0],inline=b[1],full=b[2];String instruction=!full.isEmpty()?full:inline;if(instruction==null||instruction.trim().isEmpty()){skipped++;continue;}boolean duplicate=false;for(Cmd c:all)if(c.command.equalsIgnoreCase(name)){duplicate=true;break;}if(duplicate){skipped++;continue;}String desc=!inline.isEmpty()&&!full.isEmpty()?inline:autoDescription(instruction,category);if(!inline.isEmpty()&&full.isEmpty())desc=inline;try{JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",name);o.put("category",category);o.put("description",category.toLowerCase(Locale.ROOT).contains("photo")?photoDescription(desc):desc);o.put("instruction",instruction);all.add(new Cmd(o,true));added++;}catch(Exception e){skipped++;}}
    return new int[]{added,skipped};
  }

  void showAdd(){
    LinearLayout x=vbox();x.setPadding(dp(18),dp(4),dp(18),0);EditText cmd=input("Command name, e.g. architectreview",1),cat=input("Category",1),desc=input("Short explanation",2),inst=input("Full instruction for ChatGPT",5);x.addView(cmd);x.addView(cat);x.addView(desc);x.addView(inst);
    AlertDialog d=new AlertDialog.Builder(this).setTitle("Add prompt").setView(x).setNegativeButton("Cancel",null).setPositiveButton("Add",null).create();d.setOnShowListener(z->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{try{JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",cmd.getText());o.put("category",cat.getText());o.put("description",desc.getText());o.put("instruction",inst.getText());Cmd c=new Cmd(o,true);all.add(c);saveCustom();d.dismiss();library();toast("Prompt added");}catch(Exception e){toast("Name and instruction are required");}}));d.show();
  }
  void confirmDelete(Cmd c){new AlertDialog.Builder(this).setTitle("Delete /"+c.command+"?").setMessage("This removes the custom prompt from this device.").setNegativeButton("Cancel",null).setPositiveButton("Delete",(d,w)->{all.remove(c);selected.remove(c);saveCustom();library();}).show();}

  String subcat(String c,String group){if(group.contains("Writing")){if(has(c,"rewrite,rephrase,paraphrase,polish,proofread,grammar"))return"Rewrite & Improve";if(has(c,"humanize,professional,formal,casual,tone"))return"Tone & Style";if(has(c,"shorten,expand,simplify,clarify"))return"Length & Clarity";return"Language & Translation";}if(group.contains("Thinking")){if(has(c,"brainstorm,ideas,angles,alternative"))return"Generate Ideas";if(has(c,"critique,challenge,devilsadvocate,blindspots,counterexample"))return"Challenge & Critique";return"Reason & Decide";}if(group.contains("Research")){if(has(c,"research,sources,evidence,verify,facts"))return"Research & Verification";if(has(c,"compare,proscons"))return"Compare";return"Analyze & Extract";}if(group.contains("Planning")){if(has(c,"plan,strategy,roadmap"))return"Strategy & Roadmap";if(has(c,"requirements,constraints,risks,acceptance,spec"))return"Define the Work";return"Tasks & Execution";}if(group.contains("Learning")){if(has(c,"eli5,explain,steps,examples,analogy,teach"))return"Understand & Learn";return"Practice & Remember";}if(group.contains("Work")){if(has(c,"email,reply,followup,request,apology"))return"Messages & Email";if(has(c,"resume,coverletter,interview"))return"Career";return"Meetings";}if(group.contains("Content")){if(has(c,"hook,headline,caption,cta,viral"))return"Attention & Engagement";return"Content Formats";}if(group.contains("Technical")){if(has(c,"rootcause,debug,fix,check"))return"Diagnose & Fix";return"Improve & Validate";}if(group.contains("Photo Editing")){if(has(c,"ProHeadshot,StudioPro,Magazine,OldMoney,LowAngleHero,hdreal,cinematicportrait,FixFaceResolution"))return"Portrait & Editorial";if(has(c,"NeonCity,GoldenHour,Fog,RainyNight,SnowWorld,Autumn,MovieScene,Travelstory,storymytravel,cinematicTravel,documentrytravel,Travelvlog"))return"Cinematic & Travel";if(has(c,"LuxuryAd,DroneView,VintageFilm"))return"Commercial & Camera Styles";return"Creative Effects";}return"Structure & Convert";}
  String useWhen(Cmd c){String n=c.command;if(has(n,"compare,proscons,rank,recommend,decision"))return"عندك أكتر من اختيار وعاوز تفهم الفرق أو توصل لقرار.";if(has(n,"research,verify,sources,evidence,facts"))return"محتاج معلومة موثوقة أو عاوز تتأكد من ادعاء قبل ما تعتمد عليه.";if(has(n,"rewrite,rephrase,polish,proofread,grammar,humanize"))return"عندك نص موجود وعاوز تطلعه بشكل أحسن بدل ما تبدأ من الصفر.";if(has(n,"brainstorm,ideas,angles,alternative"))return"محتاج توسع مساحة الاختيارات وتطلع أفكار أو اتجاهات جديدة.";if(has(n,"debug,rootcause,fix,check,tests"))return"في مشكلة أو نتيجة غلط وعاوز تشخص السبب وتوصل لإصلاح قابل للاختبار.";if(has(n,"plan,strategy,roadmap,action,priority"))return"عندك هدف وعاوز تحوله لترتيب عملي واضح بدل كلام عام.";return"لما تكون محتاج الوظيفة دي كخطوة واضحة داخل طلب أكبر.";}
  String example(Cmd c){return"طبّق الأمر ده على الموضوع أو النص اللي هبعته، واديني نتيجة واضحة وعملية.";}
  String[] relatedNames(String n){if(has(n,"research,verify,sources,evidence,facts"))return new String[]{"research","verify","sources","evidence","facts"};if(has(n,"critique,challenge,blindspots,devilsadvocate,improve"))return new String[]{"critique","challenge","blindspots","devilsadvocate","improve"};if(has(n,"rewrite,rephrase,polish,proofread,clarify,professional"))return new String[]{"rewrite","rephrase","clarify","polish","proofread","professional"};if(has(n,"plan,strategy,roadmap,action,priority"))return new String[]{"strategy","roadmap","priority","action"};if(has(n,"debug,rootcause,fix,check,tests"))return new String[]{"rootcause","debug","fix","tests","check"};if(has(n,"compare,proscons,rank,recommend,decision"))return new String[]{"compare","proscons","tradeoffs","rank","recommend"};if(has(n,"brainstorm,ideas,angles,alternative"))return new String[]{"brainstorm","angles","alternative","critique","rank"};return new String[0];}
  boolean has(String c,String csv){return Arrays.asList(csv.toLowerCase(Locale.ROOT).split(",")).contains(c.toLowerCase(Locale.ROOT));}Cmd find(String n){for(Cmd c:all)if(c.command.equalsIgnoreCase(n))return c;return null;}int nextId(){int m=10000;for(Cmd c:all)m=Math.max(m,c.id+1);return m;}

  void saveCustom(){JSONArray a=new JSONArray();for(Cmd c:all)if(c.custom)try{a.put(c.json());}catch(Exception ignored){}getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString(CUSTOM,a.toString()).apply();}
  void openImport(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");startActivityForResult(i,IMPORT_REQ);}void openExport(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"PromptDeck-custom.promptdeck.json");startActivityForResult(i,EXPORT_REQ);}
  @Override protected void onActivityResult(int r,int result,Intent data){super.onActivityResult(r,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;try{if(r==IMPORT_REQ)importPack(data.getData());else if(r==EXPORT_REQ)exportPack(data.getData());}catch(Exception e){toast("File error: "+e.getMessage());}}
  void importPack(Uri u)throws Exception{Object p=new JSONTokener(readUri(u)).nextValue();JSONArray a;if(p instanceof JSONArray)a=(JSONArray)p;else{JSONObject o=(JSONObject)p;a=o.has("commands")?o.getJSONArray("commands"):new JSONArray().put(o);}int n=0,skip=0;for(int i=0;i<a.length();i++)try{JSONObject o=a.getJSONObject(i);o.put("id",nextId());Cmd c=new Cmd(o,true);boolean dup=false;for(Cmd z:all)if(z.command.equals(c.command)&&z.instruction.equals(c.instruction))dup=true;if(dup){skip++;continue;}all.add(c);n++;}catch(Exception ignored){skip++;}saveCustom();toast("Imported "+n+(skip>0?" • skipped "+skip:""));library();}
  void exportPack(Uri u)throws Exception{JSONObject p=new JSONObject();p.put("format","promptdeck-pack");p.put("version",1);p.put("name","PromptDeck custom prompts");JSONArray a=new JSONArray();for(Cmd c:all)if(c.custom)a.put(c.json());p.put("commands",a);OutputStream out=getContentResolver().openOutputStream(u,"w");if(out==null)throw new IOException("Can't open destination");out.write(p.toString(2).getBytes(StandardCharsets.UTF_8));out.close();toast("Custom prompts exported");}
  void copy(){if(finalPrompt==null)return;((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("PromptDeck prompt",finalPrompt.getText()));toast("Prompt copied");}
  void send(){if(finalPrompt==null)return;Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,finalPrompt.getText().toString());i.setPackage("com.openai.chatgpt");try{startActivity(i);}catch(Exception e){i.setPackage(null);startActivity(Intent.createChooser(i,"Send prompt"));}}

  LinearLayout surface(boolean compact){LinearLayout l=vbox();l.setPadding(dp(16),dp(14),dp(16),dp(14));l.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));l.setElevation(dp(3));l.setTranslationZ(dp(1));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(2),0,dp(10));l.setLayoutParams(lp);return l;}
  GradientDrawable satinShape(int top,int bottom,int stroke,int radius){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,new int[]{top,bottom});g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}
  GradientDrawable shape(int fill,int stroke,int radius){GradientDrawable g=new GradientDrawable();g.setColor(fill);g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}
  TextView text(String s,int sp,boolean bold,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(color);v.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);if(bold)v.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));else v.setTypeface(Typeface.create("sans-serif",Typeface.NORMAL));return v;}
  TextView section(String s,int count){TextView v=text(s+"  ·  "+count,11,true,MUTED);v.setAllCaps(true);v.setLetterSpacing(.06f);v.setPadding(dp(2),dp(5),0,dp(8));return v;}TextView label(String s){TextView v=text(s,10,true,ACCENT);v.setLetterSpacing(.14f);v.setPadding(0,dp(18),0,dp(7));return v;}
  TextView pill(String s){TextView v=text(s,10,true,ACCENT);v.setLetterSpacing(.12f);v.setGravity(Gravity.CENTER);v.setPadding(dp(12),dp(7),dp(12),dp(7));v.setBackground(shape(SURFACE2,BORDER,18));return v;}
  Button styledButton(String s,int fill,int stroke,int color){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(color);x.setTextSize(14);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));if(fill==Color.rgb(47,107,255))x.setBackground(satinShape(Color.rgb(67,126,255),Color.rgb(38,91,224),stroke,10));else if(fill==SURFACE||fill==SURFACE2)x.setBackground(satinShape(Color.rgb(31,37,46),Color.rgb(22,27,34),stroke,10));else x.setBackground(shape(fill,stroke,10));x.setElevation(dp(fill==Color.rgb(47,107,255)?3:1));x.setPadding(dp(12),dp(9),dp(12),dp(9));x.setMinHeight(dp(46));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(5),0,dp(5));x.setLayoutParams(lp);return x;}
  Button navBack(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(TEXT);x.setTextSize(12);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(10),0,dp(10),0);x.setBackground(satinShape(Color.rgb(29,35,43),Color.rgb(20,25,32),BORDER,9));x.setElevation(dp(2));return x;}
  Button primary(String s){return styledButton(s,Color.rgb(47,107,255),Color.rgb(74,128,255),Color.WHITE);}Button secondary(String s){return styledButton(s,SURFACE2,BORDER,TEXT);}Button ghost(String s){return styledButton(s,SURFACE,BORDER,TEXT);}Button mini(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(MUTED);x.setTextSize(14);x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(8),dp(6),dp(8),dp(6));x.setBackground(shape(SURFACE2,BORDER,8));return x;}
  Button compactControl(String s){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(MUTED);x.setTextSize(11);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(6),0,dp(6),0);x.setBackground(shape(SURFACE2,BORDER,8));return x;}
  EditText input(String hint,int lines){EditText x=new EditText(this);x.setHint(hint);x.setHintTextColor(Color.rgb(105,108,115));x.setTextColor(TEXT);x.setTextSize(15);x.setMinLines(lines);x.setGravity(Gravity.TOP|Gravity.START);x.setLineSpacing(0,1.12f);x.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);x.setPadding(dp(15),dp(13),dp(15),dp(13));x.setBackground(satinShape(Color.rgb(17,22,29),Color.rgb(12,16,22),BORDER,10));x.setElevation(dp(1));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,0,0,dp(10));x.setLayoutParams(lp);return x;}
  LinearLayout vbox(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}LinearLayout hbox(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.HORIZONTAL);return l;}void spacer(int h){Space s=new Space(this);root.addView(s,new LinearLayout.LayoutParams(1,dp(h)));}int dp(int x){return Math.round(x*getResources().getDisplayMetrics().density);}void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
  String readAsset(String n)throws IOException{return slurp(getAssets().open(n));}String readUri(Uri u)throws IOException{return slurp(getContentResolver().openInputStream(u));}String slurp(InputStream in)throws IOException{if(in==null)throw new IOException("Can't open file");ByteArrayOutputStream o=new ByteArrayOutputStream();byte[]b=new byte[4096];int n;while((n=in.read(b))>0)o.write(b,0,n);in.close();return o.toString(StandardCharsets.UTF_8.name());}
}