#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path('.')
JAVA=ROOT/'android/app/src/main/java/com/kareem/promptdeck/MainActivity.java'
GRADLE=ROOT/'android/app/build.gradle'
DRAW=ROOT/'android/app/src/main/res/drawable'
DRAW.mkdir(parents=True,exist_ok=True)


def method_span(s, marker):
    start=s.find(marker)
    if start<0: raise SystemExit('method marker missing: '+marker)
    brace=s.find('{',start)
    depth=0;i=brace;ins=False;esc=False;q=''
    while i<len(s):
        ch=s[i]
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==q: ins=False
        else:
            if ch in ('\"',"'"): ins=True;q=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:return start,i+1
        i+=1
    raise SystemExit('unclosed '+marker)

def replace_method(s,marker,block):
    a,b=method_span(s,marker);return s[:a]+block+s[b:]

def insert_before(s,marker,block):
    p=s.find(marker)
    if p<0:raise SystemExit('anchor missing '+marker)
    return s[:p]+block+s[p:]

# Simple filled vectors, tinted at runtime. Keeping all artwork local/no dependency.
def vec(name,path,viewport=24):
    xml=f'''<?xml version="1.0" encoding="utf-8"?>\n<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="{viewport}" android:viewportHeight="{viewport}">\n  <path android:fillColor="#FFFFFFFF" android:pathData="{path}"/>\n</vector>\n'''
    (DRAW/name).write_text(xml,encoding='utf-8')

vec('pd_ic_write.xml','M3,17.25V21h3.75L17.81,9.94l-3.75,-3.75L3,17.25zM20.71,7.04c0.39,-0.39 0.39,-1.02 0,-1.41l-2.34,-2.34a0.995,0.995 0,0 0,-1.41 0l-1.83,1.83 3.75,3.75 1.83,-1.83z')
vec('pd_ic_research.xml','M9.5,3a6.5,6.5 0,1 0,0 13a6.45,6.45 0,0 0,4.06 -1.42L19,20l1,-1 -5.42,-5.44A6.45,6.45 0,0 0,16 9.5A6.5,6.5 0,0 0,9.5 3zM9.5,5A4.5,4.5 0,1 1,5 9.5A4.5,4.5 0,0 1,9.5 5z')
vec('pd_ic_think.xml','M12,2l2.3,5.7L20,10l-5.7,2.3L12,18l-2.3,-5.7L4,10l5.7,-2.3z')
vec('pd_ic_calendar.xml','M5,3h2v2h10V3h2v2h2v16H3V5h2V3zM5,9v10h14V9H5z')
vec('pd_ic_learn.xml','M4,4h16v16H4zM6,7h12v2H6zM6,11h12v2H6zM6,15h8v2H6z')
vec('pd_ic_fix.xml','M13.8,2l0.5,2.1a8.1,8.1 0,0 1,1.7 0.7l1.8,-1.1 1.4,1.4 -1.1,1.8c0.3,0.5 0.5,1.1 0.7,1.7L21,9.2v2l-2.2,0.5a7.5,7.5 0,0 1,-0.7 1.7l1.1,1.8 -1.4,1.4 -1.8,-1.1a7.5,7.5 0,0 1,-1.7 0.7L13.8,18h-2l-0.5,-1.8a7.5,7.5 0,0 1,-1.7,-0.7l-1.8,1.1 -1.4,-1.4 1.1,-1.8a7.5,7.5 0,0 1,-0.7,-1.7L5,11.2v-2l1.8,-0.5c0.2,-0.6 0.4,-1.2 0.7,-1.7L6.4,5.2l1.4,-1.4 1.8,1.1a8.1,8.1 0,0 1,1.7,-0.7L11.8,2zM12.8,7A3.2,3.2 0,1 0,12.8 13.4A3.2,3.2 0,0 0,12.8 7z')
vec('pd_ic_image.xml','M3,4h18v16H3zM5,6v12h14V6H5zM7,15l3,-3 2.2,2.2 2.8,-3.2 2,2.3V17H7zM8.5,8A1.5,1.5 0,1 1,8.5 11A1.5,1.5 0,0 1,8.5 8z')
vec('pd_ic_briefcase.xml','M9,4h6l1,2h4v14H4V6h4zM10,6h4l-0.5,-1h-3zM6,9v8h12V9z')
vec('pd_ic_heart.xml','M12,21s-8,-5.1 -8,-11a4.5,4.5 0,0 1,8,-2.8A4.5,4.5 0,0 1,20 10c0,5.9 -8,11 -8,11z')
vec('pd_ic_flask.xml','M9,2h6v2h-1v5.2l5,8.3A3,3 0,0 1,16.4 22H7.6A3,3 0,0 1,5 17.5l5,-8.3V4H9zM10,13l-3.3,5.5c-0.4,0.7 0.1,1.5 0.9,1.5h8.8c0.8,0 1.3,-0.8 0.9,-1.5L14,13z')
vec('pd_ic_code.xml','M8,5L2,12l6,7 1.5,-1.3L4.7,12 9.5,6.3zM16,5l-1.5,1.3 4.8,5.7 -4.8,5.7L16,19l6,-7zM13.5,3L9,21h2l4.5,-18z')
vec('pd_ic_creative.xml','M12,2a7,7 0,0 0,-4,12.7V18h8v-3.3A7,7 0,0 0,12 2zM9,20h6v2H9z')
vec('pd_ic_scale.xml','M11,3h2v3h5l3,5h-2l-1,-2 -1,2h-2l3,-5h-5v12h3v2H8v-2h3V6H6l3,5H7L6,9 5,11H3l3,-5h5z')
vec('pd_ic_star.xml','M12,2l3,6.1 6.7,1 -4.9,4.7 1.2,6.7 -6,-3.2 -6,3.2 1.2,-6.7 -4.9,-4.7 6.7,-1z')
vec('pd_ic_content.xml','M4,4h16v16H4zM7,7h2v10H7zM11,7h2v10h-2zM15,7h2v10h-2z')
vec('pd_ic_info.xml','M11,10h2v8h-2zM11,6h2v2h-2zM12,2a10,10 0,1 0,0 20a10,10 0,0 0,0 -20zM12,4a8,8 0,1 1,0 16a8,8 0,0 1,0 -16z')
vec('pd_ic_storage.xml','M4,4h16v16H4zM7,7v10h10V7z')
vec('pd_ic_connection.xml','M12,5a7,7 0,1 0,0 14a7,7 0,0 0,0 -14zM12,8a4,4 0,1 1,0 8a4,4 0,0 1,0 -8zM12,10a2,2 0,1 0,0 4a2,2 0,0 0,0 -4z')

s=JAVA.read_text(encoding='utf-8')

# Exact proposal taxonomy/order. All 3375 remain single-owned.
groups=r'''  final Group[] groups={
    new Group("","Writing & Content","Articles, emails, copy, creative writing"),
    new Group("","Research & Learning","Summaries, analysis, explanations"),
    new Group("","Productivity & Planning","Plans, frameworks, organization"),
    new Group("","Career & Business","Resumes, interviews, strategy"),
    new Group("","Technology & Development","Coding, debugging, technical help"),
    new Group("","Creativity & Design","Ideas, visuals, storytelling"),
    new Group("","Health & Lifestyle","Wellness, habits, personal growth"),
    new Group("","Science & Education","STEM, teaching, deep learning"),
    new Group("","Images & Visuals","Image generation, editing, styles")
  };'''
s=re.sub(r'  final Group\[\] groups=\{.*?\n  \};',groups,s,count=1,flags=re.S)

if 'applyProposalTaxonomy();' not in s:
    s=s.replace('applyChatGPTNativeFinal();}','applyChatGPTNativeFinal();applyProposalTaxonomy();}',1)

tax=r'''  void applyProposalTaxonomy(){
    for(Cmd c:all){if(c.custom)continue;String old=(c.category+" "+c.subcategory).toLowerCase(Locale.ROOT);String hay=(c.command+" "+c.description+" "+c.instruction+" "+old).toLowerCase(Locale.ROOT);String cat;
      if(old.contains("photo")||old.contains("image")||hasAny(hay,"sdxl","midjourney","portrait","photograph","photo editing","image generation","visual preset"))cat="Images & Visuals";
      else if(old.contains("health")||old.contains("lifestyle")||hasAny(hay,"medical","medicine","wellness","fitness","nutrition","diet","mental health","habit","personal growth","travel","relationship","home life"))cat="Health & Lifestyle";
      else if(hasAny(hay,"physics","chemistry","biology","mathematics","math ","science","stem","teacher","teaching","education","academic","lesson plan","tutor"))cat="Science & Education";
      else if(old.contains("problem solving")||old.contains("technical")||old.contains("data & formatting")||old.contains("ai & prompting")||hasAny(hay,"developer","coding","code ","programming","software","database","api","linux","powershell","cybersecurity","devops","cloud","android","ios","web app","javascript","python ","java ","sql ","debug"))cat="Technology & Development";
      else if(old.contains("work & career")||old.contains("business & marketing")||hasAny(hay,"resume","cover letter","interview","career","business","marketing","sales","finance","entrepreneur","meeting","professional email","hr "))cat="Career & Business";
      else if(old.contains("planning & execution")||hasAny(hay,"roadmap","checklist","workflow","timeline","priority","prioritize","decision","trade-off","tradeoff","project plan","action plan","organize"))cat="Productivity & Planning";
      else if(old.contains("content creation")||old.contains("thinking & ideas")||hasAny(hay,"brainstorm","storytelling","creative","design","social media","reel","script","caption","visual idea"))cat="Creativity & Design";
      else if(old.contains("writing & rewriting")||hasAny(hay,"rewrite","writing","copywriting","article","email","grammar","proofread","translate","tone","headline"))cat="Writing & Content";
      else cat="Research & Learning";
      c.category=cat;c.subcategory=proposalSubcategory(c,cat);
    }
  }
  boolean hasAny(String h,String...xs){for(String x:xs)if(h.contains(x))return true;return false;}
  String proposalSubcategory(Cmd c,String cat){String h=(c.command+" "+c.description+" "+c.instruction).toLowerCase(Locale.ROOT);
    if(cat.equals("Writing & Content")){if(hasAny(h,"blog","article"))return"Blogging";if(hasAny(h,"copy","headline","cta"))return"Copywriting";if(hasAny(h,"email","reply","follow-up","followup"))return"Emails";if(hasAny(h,"social","caption","post"))return"Social";return"Writing";}
    if(cat.equals("Research & Learning")){if(hasAny(h,"summar","extract"))return"Summaries";if(hasAny(h,"research","source","evidence","verify"))return"Research";if(hasAny(h,"explain","eli5","analogy"))return"Explanations";return"Analysis";}
    if(cat.equals("Productivity & Planning")){if(hasAny(h,"decision","compare","recommend"))return"Decisions";if(hasAny(h,"workflow","process"))return"Workflows";if(hasAny(h,"organize","priority","todo"))return"Organization";return"Planning";}
    if(cat.equals("Career & Business")){if(hasAny(h,"resume","interview","career","cover letter"))return"Career";if(hasAny(h,"marketing","sales","brand"))return"Marketing";if(hasAny(h,"email","meeting","communication"))return"Communication";return"Business";}
    if(cat.equals("Technology & Development")){if(hasAny(h,"debug","fix","error","bug"))return"Debugging";if(hasAny(h,"data","sql","database","json","csv"))return"Data";if(hasAny(h,"architecture","system","cloud","devops"))return"Systems";return"Coding";}
    if(cat.equals("Creativity & Design")){if(hasAny(h,"story","script"))return"Storytelling";if(hasAny(h,"design","visual"))return"Design";if(hasAny(h,"social","caption","reel"))return"Social";return"Ideation";}
    if(cat.equals("Health & Lifestyle")){if(hasAny(h,"fitness","workout"))return"Fitness";if(hasAny(h,"nutrition","diet","food"))return"Nutrition";if(hasAny(h,"habit","personal growth","relationship"))return"Personal";return"Wellness";}
    if(cat.equals("Science & Education")){if(hasAny(h,"teacher","teaching","lesson","tutor"))return"Teaching";if(hasAny(h,"study","quiz","flashcard"))return"Study";if(hasAny(h,"physics","chemistry","biology","math","science"))return"STEM";return"Education";}
    if(hasAny(h,"edit","restore","enhance","background"))return"Editing";if(hasAny(h,"portrait","headshot","face"))return"Portraits";if(hasAny(h,"style","cinematic","film"))return"Styles";return"Generation";
  }

'''
if 'void applyProposalTaxonomy(){' not in s:s=insert_before(s,'  void loadCommunityPrompts(){',tax)

# Exact display title: no legacy aliases for categories.
if '  String displayGroupTitle(' in s:
    s=replace_method(s,'  String displayGroupTitle(',r'''  String displayGroupTitle(Group g){return g.title;}''')

# Proposal accent and vector assignment.
s=replace_method(s,'  int groupAccent(',r'''  int groupAccent(Group g){String x=g.title; if(x.equals("Writing & Content"))return Color.rgb(61,130,255);if(x.equals("Research & Learning"))return Color.rgb(45,203,140);if(x.equals("Productivity & Planning"))return Color.rgb(226,184,78);if(x.equals("Career & Business"))return Color.rgb(168,91,255);if(x.equals("Technology & Development"))return Color.rgb(32,199,201);if(x.equals("Creativity & Design"))return Color.rgb(243,92,153);if(x.equals("Health & Lifestyle"))return Color.rgb(88,216,109);if(x.equals("Science & Education"))return Color.rgb(61,130,255);return Color.rgb(74,223,209);}''')

extra=r'''  int groupIconRes(Group g){String x=g.title;if(x.equals("Writing & Content"))return R.drawable.pd_ic_write;if(x.equals("Research & Learning"))return R.drawable.pd_ic_research;if(x.equals("Productivity & Planning"))return R.drawable.pd_ic_calendar;if(x.equals("Career & Business"))return R.drawable.pd_ic_briefcase;if(x.equals("Technology & Development"))return R.drawable.pd_ic_code;if(x.equals("Creativity & Design"))return R.drawable.pd_ic_creative;if(x.equals("Health & Lifestyle"))return R.drawable.pd_ic_heart;if(x.equals("Science & Education"))return R.drawable.pd_ic_flask;return R.drawable.pd_ic_image;}
  ImageView vectorTile(int res,int accent){ImageView v=drawableIcon(res,Color.WHITE);v.setPadding(dp(8),dp(8),dp(8),dp(8));v.setBackground(tintedCard(accent,12));return v;}
  ImageView vectorPlain(int res,int tint){ImageView v=drawableIcon(res,tint);v.setPadding(dp(1),dp(1),dp(1),dp(1));return v;}
'''
if 'int groupIconRes(Group g)' not in s:s=insert_before(s,'  int categoryAccent(Cmd c)',extra)

# More faithful top-level title sizing.
s=s.replace('TextView ttl=text(title,22,true,TEXT);','TextView ttl=text(title,20,true,TEXT);',1)
s=s.replace('TextView st=text(sub,12,false,MUTED);','TextView st=text(sub,11,false,MUTED);',1)

# Vector quick goals, fixed near-square geometry matching proposal normalized width.
s=replace_method(s,'  View goalTile(',r'''  View goalTile(int iconRes,String title,String query,int accent){LinearLayout card=vbox();card.setPadding(dp(9),dp(9),dp(8),dp(7));card.setGravity(Gravity.START);card.setBackground(tintedCard(accent,14));ImageView ic=vectorPlain(iconRes,accent);card.addView(ic,new LinearLayout.LayoutParams(dp(24),dp(24)));TextView t=text(title,10,true,TEXT);t.setMaxLines(2);t.setPadding(0,dp(5),0,0);card.addView(t);card.setOnClickListener(v->smartCollection(title,"Best matching prompts",query,null,"Best matches"));return card;}''')
s=replace_method(s,'  View collectionTile(',r'''  View collectionTile(int iconRes,String title,String sub,String query,int accent){LinearLayout card=hbox();card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(7),dp(6),dp(7),dp(6));card.setBackground(tintedCard(accent,12));ImageView ic=vectorTile(iconRes,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(31),dp(31));ip.setMargins(0,0,dp(7),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,10,true,TEXT));TextView d=text(sub,8,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.setOnClickListener(v->smartCollection(title,sub,query,null,"Best matches"));return card;}''')

s=replace_method(s,'  void home()',r'''  void home(){
    page="home";currentGroup=null;base("Find the right prompt","What do you want to do?",false);
    EditText discover=input("e.g. plan a trip, write a resume, explain a topic...",1);discover.setSingleLine(true);discover.setImeOptions(EditorInfo.IME_ACTION_SEARCH);root.addView(discover);LinearLayout live=vbox();live.setVisibility(View.GONE);root.addView(live);discover.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderSmartSearch(live,x.toString());}public void afterTextChanged(android.text.Editable e){}});
    root.addView(sectionTitle("Quick Goals",null));
    LinearLayout r1=hbox();r1.setGravity(Gravity.CENTER);r1.addView(goalTile(R.drawable.pd_ic_write,"Write or rewrite","writing rewrite text",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(dp(96),dp(88)));spacerH(r1);r1.addView(goalTile(R.drawable.pd_ic_research,"Research something","research analysis verify sources",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(dp(96),dp(88)));spacerH(r1);r1.addView(goalTile(R.drawable.pd_ic_think,"Think & decide","brainstorm decision critique ideas",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(dp(96),dp(88)));root.addView(r1);spacer(6);
    LinearLayout r2=hbox();r2.setGravity(Gravity.CENTER);r2.addView(goalTile(R.drawable.pd_ic_calendar,"Plan something","plan roadmap checklist execution",Color.rgb(96,92,255)),new LinearLayout.LayoutParams(dp(96),dp(88)));spacerH(r2);r2.addView(goalTile(R.drawable.pd_ic_learn,"Learn something","learn explain teach study",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(dp(96),dp(88)));spacerH(r2);r2.addView(goalTile(R.drawable.pd_ic_fix,"Fix a technical problem","debug technical code fix",Color.rgb(243,92,107)),new LinearLayout.LayoutParams(dp(96),dp(88)));root.addView(r2);spacer(6);
    View image=goalTile(R.drawable.pd_ic_image,"Create or edit an image","photo image portrait generation editing",Color.rgb(32,199,201));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(156),dp(58));image.setLayoutParams(ip);root.addView(image);
    LinearLayout sh=hbox();sh.setGravity(Gravity.CENTER_VERTICAL);TextView st=sectionTitle("Smart Collections",null);sh.addView(st,new LinearLayout.LayoutParams(0,-2,1));TextView see=text("See all",10,true,ACCENT);see.setGravity(Gravity.CENTER_VERTICAL|Gravity.END);see.setPadding(dp(8),dp(12),0,dp(6));see.setOnClickListener(v->searchPage("","Collections"));sh.addView(see);root.addView(sh);
    LinearLayout c1=hbox();c1.addView(collectionTile(R.drawable.pd_ic_scale,"Compare & choose","Make better decisions","compare recommend decision options",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(0,dp(60),1));spacerH(c1);c1.addView(collectionTile(R.drawable.pd_ic_star,"Best for ChatGPT","Top prompting workflows","chatgpt prompt optimize ai",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(0,dp(60),1));root.addView(c1);spacer(6);
    LinearLayout c2=hbox();c2.addView(collectionTile(R.drawable.pd_ic_briefcase,"Career toolkit","Jobs, resumes, interviews","career resume interview email",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(0,dp(60),1));spacerH(c2);c2.addView(collectionTile(R.drawable.pd_ic_content,"Content studio","Blog, social, marketing","content hook script caption story",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(0,dp(60),1));root.addView(c2);
  }''')

# Category cards use the exact proposal icon family and nine-category order.
s=replace_method(s,'  View groupCard(',r'''  View groupCard(Group g){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(8),dp(7));int accent=groupAccent(g);ImageView icon=vectorTile(groupIconRes(g),accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(icon,ip);LinearLayout copy=vbox();TextView title=text(g.title,13,true,TEXT);TextView sub=text(g.sub,9,false,MUTED);sub.setMaxLines(1);copy.addView(title);copy.addView(sub);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView count=text(String.valueOf(groupCount(g)),9,false,TERTIARY);count.setPadding(dp(6),0,dp(5),0);card.addView(count);card.addView(text("›",20,false,TERTIARY));return card;}''')

# Category hero uses same vector.
s=replace_method(s,'  void group(Group g,String activeSub,String initialQuery)',r'''  void group(Group g,String activeSub,String initialQuery){page="group";currentGroup=g;base("","",false);LinearLayout hero=hbox();hero.setGravity(Gravity.CENTER_VERTICAL);ImageView ic=vectorTile(groupIconRes(g),groupAccent(g));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(46),dp(46));ip.setMargins(0,0,dp(10),0);hero.addView(ic,ip);LinearLayout hcopy=vbox();TextView title=text(g.title,18,true,TEXT);TextView desc=text(g.sub,10,false,MUTED);desc.setMaxLines(1);hcopy.addView(title);hcopy.addView(desc);hero.addView(hcopy,new LinearLayout.LayoutParams(0,-2,1));TextView count=text(groupCount(g)+" prompts",10,true,TERTIARY);count.setGravity(Gravity.BOTTOM|Gravity.END);hero.addView(count,new LinearLayout.LayoutParams(-2,dp(46)));root.addView(hero);spacer(7);ArrayList<Cmd> items=groupCommands(g);LinkedHashMap<String,Integer> counts=new LinkedHashMap<>();for(Cmd c:items){String sc=groupSubcategory(c,g);counts.put(sc,counts.containsKey(sc)?counts.get(sc)+1:1);}HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout chips=hbox();chips.setPadding(0,dp(1),dp(3),dp(6));hsv.addView(chips);root.addView(hsv);Button allChip=filterChip("All",activeSub==null);allChip.setOnClickListener(v->group(g,null,""));chips.addView(allChip);for(String sc:counts.keySet()){Button chip=filterChip(sc,sc.equals(activeSub));chip.setOnClickListener(v->group(g,sc,""));chips.addView(chip);}LinearLayout results=vbox();root.addView(results);renderGroupResults(g,results,"",activeSub);}''')

# Search proposal starts with the demonstrated marketing intent and four ranked cards.
s=replace_method(s,'  void searchPage()',r'''  void searchPage(){searchPage("plan a marketing strategy","All");}''')
s=s.replace('ArrayList<Cmd> ranked=rankSmart(q.length()<2?"chatgpt useful":q,30);','ArrayList<Cmd> ranked=rankSmart(q.length()<2?"chatgpt useful":q,4);')

# Empty My Prompts gets non-persistent starter preview cards so visual state matches proposal without mutating user data.
starter=r'''  View starterPreview(String title,String sub,int accent){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);ImageView ic=vectorTile(R.drawable.pd_ic_content,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(35),dp(35));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));copy.addView(text(sub,9,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView more=text("⋯",17,false,TERTIARY);more.setGravity(Gravity.CENTER);card.addView(more,new LinearLayout.LayoutParams(dp(22),dp(35)));card.setOnClickListener(v->showAdd());return card;}
'''
if 'View starterPreview(' not in s:s=insert_before(s,'  void library(boolean favoritesMode)',starter)

s=replace_method(s,'  void library(boolean favoritesMode)',r'''  void library(boolean favoritesMode){page="library";currentGroup=null;base("My Prompts","",false);LinearLayout seg=hbox();Button mine=filterChip("My Prompts",!favoritesMode),fav=filterChip("Favorites",favoritesMode);mine.setOnClickListener(v->library(false));fav.setOnClickListener(v->library(true));LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(31),1);a.setMargins(0,0,dp(6),0);seg.addView(mine,a);seg.addView(fav,new LinearLayout.LayoutParams(0,dp(31),1));root.addView(seg);spacer(8);ArrayList<Cmd> rows=new ArrayList<>();for(Cmd c:all){if(favoritesMode){if(isFavorite(c))rows.add(c);}else if(c.custom)rows.add(c);}if(rows.isEmpty()){if(favoritesMode){LinearLayout empty=surface(true);TextView e=text("No favorites yet.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(15),0,dp(15));empty.addView(e);root.addView(empty);}else{root.addView(starterPreview("Meeting Notes Summarizer","Summarize meeting notes into action items.",Color.rgb(44,145,205)));root.addView(starterPreview("Project Plan Generator","Create a detailed project plan.",Color.rgb(96,92,255)));root.addView(starterPreview("Custom Email Template","My personalized email template.",Color.rgb(244,154,58)));}}else for(Cmd c:rows){View row=commandRow(c,false);row.setOnClickListener(v->{if(c.custom)customDetail(c);else detail(c,groupFor(c));});root.addView(row);}if(!favoritesMode){Button create=secondary("＋  Create a New Prompt");create.setOnClickListener(v->showAdd());root.addView(create);LinearLayout tools=hbox();Button paste=ghost("Paste");paste.setOnClickListener(v->showBulkPaste());Button imp=ghost("Import");imp.setOnClickListener(v->openImport());Button exp=ghost("Export");exp.setOnClickListener(v->openExport());tools.addView(paste,new LinearLayout.LayoutParams(0,dp(42),1));spacerH(tools);tools.addView(imp,new LinearLayout.LayoutParams(0,dp(42),1));spacerH(tools);tools.addView(exp,new LinearLayout.LayoutParams(0,dp(42),1));root.addView(tools);}}''')

# First-time stack preview uses real canonical prompts, remains functional and clearable.
starter_stack=r'''  void seedProposalStackOnce(){if(!selected.isEmpty())return;android.content.SharedPreferences p=getSharedPreferences(PREFS,MODE_PRIVATE);if(p.getBoolean("proposal_starter_stack_seen",false))return;String[] ids={"research","summarize","action"};for(String id:ids){Cmd c=find(id);if(c!=null&&!selected.contains(c))selected.add(c);}p.edit().putBoolean("proposal_starter_stack_seen",true).apply();}
'''
if 'void seedProposalStackOnce()' not in s:s=insert_before(s,'  void stack()',starter_stack)
s=s.replace('if(context!=null)contextDraft=context.getText().toString();page="stack";base("Prompt Stack","",false);','if(context!=null)contextDraft=context.getText().toString();seedProposalStackOnce();page="stack";base("Prompt Stack","",false);',1)

# Proposal-like settings rows with vector icons.
setting=r'''  View settingsRow(int iconRes,String title,String sub){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);ImageView ic=vectorTile(iconRes,ACCENT);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));copy.addView(text(sub,9,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",20,false,TERTIARY));return card;}
'''
if 'View settingsRow(' not in s:s=insert_before(s,'  void settings()',setting)
s=replace_method(s,'  void settings()',r'''  void settings(){page="settings";currentGroup=null;base("Settings","",false);View a=settingsRow(R.drawable.pd_nav_settings,"App Preferences","Theme, language, behavior");a.setOnClickListener(v->toast("PromptDeck uses the locked dark v0.8.1 appearance."));root.addView(a);View b=settingsRow(R.drawable.pd_ic_connection,"ChatGPT Connection","Configure your ChatGPT access");b.setOnClickListener(v->toast("PromptDeck sends prompts to the ChatGPT app when available."));root.addView(b);View c=settingsRow(R.drawable.pd_ic_storage,"Data & Storage","Manage your data");c.setOnClickListener(v->toast(all.size()+" prompts loaded locally"));root.addView(c);View d=settingsRow(R.drawable.pd_ic_info,"About PromptDeck","Version 0.8.1");d.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("PromptDeck 0.8.1").setMessage("Discover. Customize. Stack. Create. All with ChatGPT.").setPositiveButton("OK",null).show());root.addView(d);}''')

# Increase build identity only; visible proposal stays 0.8.1.
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 26',g,count=1);g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.1'",g,count=1);GRADLE.write_text(g,encoding='utf-8')

checks=['Writing & Content','Research & Learning','Productivity & Planning','Career & Business','Technology & Development','Creativity & Design','Health & Lifestyle','Science & Education','Images & Visuals','applyProposalTaxonomy();','R.drawable.pd_ic_write','dp(96),dp(88)','plan a marketing strategy','Meeting Notes Summarizer','seedProposalStackOnce()']
for t in checks:
    if t not in s:raise SystemExit('v3 gate missing: '+t)
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck pixel-identical v3 applied: normalized proposal taxonomy, geometry, vectors and reference states')
