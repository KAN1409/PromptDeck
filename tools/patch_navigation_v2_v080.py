#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Back navigation for discovery/category hub.
s=s.replace('if("group".equals(page)||"library".equals(page)){home();return;}',
            'if("group".equals(page)||"library".equals(page)||"discover".equals(page)||"categories".equals(page)){home();return;}')

old_home='''  void home(){
    page="home"; currentGroup=null;
    base("Choose a category","All built-in and full prompts live inside these categories. Open a category, choose a prompt, review it, then add it to your Stack.",true);
    for(Group g:groups){View c=groupCard(g);c.setOnClickListener(v->group(g));root.addView(c);} spacer(8);
    View library=menuCard("＋","My Prompts","Add, import or export your own prompts");library.setOnClickListener(v->library());root.addView(library);
    if(!selected.isEmpty()){spacer(10);Button compose=primary("Build prompt from "+selected.size()+" selected command"+(selected.size()==1?"":"s"));compose.setOnClickListener(v->stack());root.addView(compose);}
    TextView foot=text(all.size()+" prompts integrated into categories  •  local  •  no API required",11,false,MUTED);foot.setGravity(Gravity.CENTER);foot.setPadding(0,dp(24),0,0);root.addView(foot);
  }
'''

new_home='''  void home(){
    page="home"; currentGroup=null;
    base("Find the right prompt","Describe what you want to do, or explore by goal. You do not need to know a prompt name.",true);

    EditText discover=input("What do you want to do?",1);discover.setSingleLine(true);discover.setImeOptions(EditorInfo.IME_ACTION_SEARCH);root.addView(discover);
    LinearLayout live=vbox();live.setVisibility(View.GONE);root.addView(live);
    discover.addTextChangedListener(new android.text.TextWatcher(){
      public void beforeTextChanged(CharSequence x,int st,int c,int a){}
      public void onTextChanged(CharSequence x,int st,int b,int c){renderSmartSearch(live,x.toString());}
      public void afterTextChanged(android.text.Editable e){}
    });

    ArrayList<Cmd> recent=recentCommands();
    if(!recent.isEmpty()){
      root.addView(section("RECENT",recent.size()));
      LinearLayout recentBox=vbox();recentBox.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));recentBox.setElevation(dp(2));
      for(int i=0;i<recent.size();i++){Cmd c=recent.get(i);View row=commandRow(c,i<recent.size()-1);row.setOnClickListener(v->detail(c,groupFor(c)));recentBox.addView(row);}root.addView(recentBox);spacer(8);
    }

    root.addView(section("QUICK GOALS",7));
    addGoalCard("✦","Write or rewrite","Rewrite, polish, translate or change tone","writing rewrite text","Rewrite","Professional","Humanize","Shorten","Translate");
    addGoalCard("⌕","Research something","Investigate, verify, compare or summarize","research analysis information","Deep research","Verify","Compare","Summarize","Find sources");
    addGoalCard("◈","Think & decide","Generate ideas, critique options and make decisions","brainstorm decision critique ideas","Brainstorm","Decision","Critique","Challenge","Prioritize");
    addGoalCard("◇","Plan something","Turn a goal into a roadmap, checklist or executable plan","plan roadmap checklist execution","Roadmap","Checklist","Project","Trip","Risk");
    addGoalCard("◎","Learn something","Explain, teach, study, quiz and practice","learn explain teach study","Explain","Teach","Study","Quiz","Examples");
    addGoalCard("⚙","Fix a technical problem","Debug, optimize, review code or design a system","debug technical code fix","Debug","Optimize","Code review","Architecture","Tests");
    addGoalCard("◉","Create or edit an image","Enhance, restore, edit or generate visual work","photo image portrait generation editing","Enhance","Restore","Portrait","Background","Style","Generate");

    root.addView(section("SMART COLLECTIONS",5));
    addCollectionCard("⚖","Compare & choose","Find prompts that compare options and recommend the best one","compare recommend decision options","Compare","Recommend","Pros & cons","Buying research");
    addCollectionCard("✧","Best for ChatGPT","Prompt design, optimization and AI workflows","chatgpt prompt optimize ai","Prompt design","Optimize prompt","AI workflows","Prompt critique");
    addCollectionCard("▣","Career toolkit","Resumes, interviews, applications and professional communication","career resume interview email","Resume","Interview","Cover letter","Email");
    addCollectionCard("△","Content studio","Hooks, scripts, captions, stories and social content","content hook script caption story","Hook","Script","Caption","Story","Social");
    addCollectionCard("◆","Deep specialist roles","Expert workflows for specific domains and professions","specialist expert role","Technical","Business","Research","Health");

    spacer(8);
    View browse=menuCard("▦","Browse all categories","Explore the full canonical library by category and subcategory");browse.setOnClickListener(v->browseCategories());root.addView(browse);
    View library=menuCard("＋","My Prompts","Add, import or export your own prompts");library.setOnClickListener(v->library());root.addView(library);
    if(!selected.isEmpty()){spacer(10);Button compose=primary("Build prompt from "+selected.size()+" selected command"+(selected.size()==1?"":"s"));compose.setOnClickListener(v->stack());root.addView(compose);}
    TextView foot=text(all.size()+" canonical prompts  •  discovery-first navigation  •  local  •  no API required",11,false,MUTED);foot.setGravity(Gravity.CENTER);foot.setPadding(0,dp(24),0,0);root.addView(foot);
  }

  void addGoalCard(String icon,String title,String sub,String baseQuery,String...refiners){
    View c=menuCard(icon,title,sub);c.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));root.addView(c);
  }

  void addCollectionCard(String icon,String title,String sub,String baseQuery,String...refiners){
    View c=menuCard(icon,title,sub);c.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));root.addView(c);
  }

  void browseCategories(){
    page="categories";currentGroup=null;base("Browse categories","Categories are a stable fallback view. Discovery, search and Smart Collections all point to the same canonical prompts.",true);
    for(Group g:groups){View c=groupCard(g);c.setOnClickListener(v->group(g));root.addView(c);}spacer(8);
    Button back=ghost("←  Discover");back.setOnClickListener(v->home());root.addView(back);
  }

  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){
    page="discover";currentGroup=null;base(title,sub,true);
    if(refiners!=null&&refiners.length>0){
      HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout chips=hbox();chips.setPadding(0,dp(2),dp(4),dp(10));hsv.addView(chips);root.addView(hsv);
      Button allChip=filterChip("Best matches",active==null);allChip.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));chips.addView(allChip);
      for(String r:refiners){Button chip=filterChip(r,r.equals(active));chip.setOnClickListener(v->smartCollection(title,sub,baseQuery,r,refiners));chips.addView(chip);}
    }
    String query=baseQuery+(active==null?"":" "+active);
    ArrayList<Cmd> ranked=rankSmart(query,30);
    TextView meta=text(ranked.size()+" ranked prompts  •  local relevance",11,false,MUTED);meta.setPadding(0,0,0,dp(8));root.addView(meta);
    renderRanked(root,ranked);
    Button back=ghost("←  Discover");back.setOnClickListener(v->home());root.addView(back);
  }

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
    final String q=expandIntent(query);ArrayList<Cmd> out=new ArrayList<>(all);final HashMap<Integer,Integer> scores=new HashMap<>();
    for(Cmd c:out)scores.put(c.id,smartScore(c,q));
    Collections.sort(out,(a,b)->{int sa=scores.get(a.id),sb=scores.get(b.id);if(sa!=sb)return Integer.compare(sb,sa);return a.command.compareToIgnoreCase(b.command);});
    ArrayList<Cmd> best=new ArrayList<>();for(Cmd c:out){if(scores.get(c.id)<=0)continue;best.add(c);if(best.size()>=limit)break;}return best;
  }

  int smartScore(Cmd c,String expanded){
    String[] toks=expanded.toLowerCase(Locale.ROOT).split("\\s+");String command=c.command.toLowerCase(Locale.ROOT),desc=(c.description+" "+c.subcategory).toLowerCase(Locale.ROOT),cat=c.category.toLowerCase(Locale.ROOT),body=c.instruction.toLowerCase(Locale.ROOT);int score=0;
    for(String t:toks){if(t.length()<2)continue;if(command.equals(t))score+=14;else if(command.contains(t))score+=9;if(desc.contains(t))score+=6;if(cat.contains(t))score+=4;if(body.contains(t))score+=1;}
    if(recentIdSet().contains(c.id))score+=3;return score;
  }

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
'''

if old_home not in s:
    raise SystemExit('home() block not found; patch target changed')
s=s.replace(old_home,new_home)

# Canonical category ownership: prevent group counters from double-listing command aliases across categories.
old_gc='''  ArrayList<Cmd> groupCommands(Group g){
    ArrayList<Cmd> out=new ArrayList<>();LinkedHashSet<Cmd> seen=new LinkedHashSet<>();
    for(String n:g.names){Cmd c=find(n);if(c!=null&&!seen.contains(c)){out.add(c);seen.add(c);}}
    for(Cmd c:all){if(!seen.contains(c)&&c.category.equalsIgnoreCase(g.title)){out.add(c);seen.add(c);}}
    return out;
  }
'''
new_gc='''  ArrayList<Cmd> groupCommands(Group g){
    ArrayList<Cmd> out=new ArrayList<>();for(Cmd c:all)if(c.category.equalsIgnoreCase(g.title))out.add(c);return out;
  }
'''
if old_gc in s:s=s.replace(old_gc,new_gc)

# Track recents whenever a canonical detail card is opened.
s=s.replace('''  void detail(Cmd c,Group g){
    page="detail"; currentGroup=g;''','''  void detail(Cmd c,Group g){
    rememberRecent(c);page="detail"; currentGroup=g;''')

p.write_text(s,encoding='utf-8')
print('Navigation V2 patch applied')
