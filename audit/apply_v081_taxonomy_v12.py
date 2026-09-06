#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')


def method_span(s, marker):
    start=s.find(marker)
    if start<0: raise SystemExit('method marker missing: '+marker)
    brace=s.find('{',start)
    if brace<0: raise SystemExit('opening brace missing: '+marker)
    depth=0;i=brace;ins=False;esc=False;q=''
    while i<len(s):
        ch=s[i]
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==q: ins=False
        else:
            if ch in ('"',"'"): ins=True;q=ch
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
    if p<0: raise SystemExit('anchor missing: '+marker)
    return s[:p]+block+s[p:]

s=JAVA.read_text(encoding='utf-8')
if 'ArrayList<Cmd> rankCapabilityV11(' not in s: raise SystemExit('v11 layer missing')

# State: category and subcategory are independent filters.
state='String discoverCategory=""; boolean discoverFavorites=false; String discoverPreset="";'
if state in s:
    s=s.replace(state,'String discoverCategory=""; String discoverSubcategory=""; boolean discoverFavorites=false; String discoverPreset="";',1)
elif 'String discoverSubcategory="";' not in s:
    raise SystemExit('browse filter state anchor missing')

# Replace top-level groups with clearer mental-model categories.
groups=r'''  final Group[] groups={
    new Group("","Writing & Communication","Write, rewrite, translate and communicate clearly"),
    new Group("","Research & Analysis","Find, verify, summarize and compare information"),
    new Group("","Planning & Decisions","Plan work, organize priorities and make better decisions"),
    new Group("","Work & Business","Career, workplace, strategy, marketing and business"),
    new Group("","Technology & Data","Coding, debugging, data, systems and AI workflows"),
    new Group("","Learning & Education","Understand, study, practice and teach"),
    new Group("","Creativity & Content","Ideas, stories, social content and creative direction"),
    new Group("","Images & Design","Generate, edit and transform images and graphics"),
    new Group("","Health & Life","Wellness, fitness, habits, relationships and lifestyle")
  };'''
s=re.sub(r'  final Group\[\] groups=\{.*?\n  \};',groups,s,count=1,flags=re.S)

# Replace taxonomy with metadata-first routing. Do not scan giant instruction bodies at startup.
s=replace_method(s,'  void applyProposalTaxonomy()',r'''  void applyProposalTaxonomy(){
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
  }''')

# Replace old proposal subcategory helper if present; keep a compatibility alias.
if '  String proposalSubcategory(' in s:
    s=replace_method(s,'  String proposalSubcategory(',r'''  String proposalSubcategory(Cmd c,String cat){return taxonomySubcategoryV12(c,cat);}''')

helpers=r'''  String[] subcategoriesForV12(String cat){
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
'''
if 'String[] subcategoriesForV12(' not in s:
    s=insert_before(s,'  void showCategoryPicker(){',helpers)

# Category picker resets subcategory and shows category counts.
s=replace_method(s,'  void showCategoryPicker()',r'''  void showCategoryPicker(){
    String[] names=new String[groups.length+1];names[0]="All categories";for(int i=0;i<groups.length;i++)names[i+1]=groups[i].title+"  ("+groupCount(groups[i])+")";
    new AlertDialog.Builder(this).setTitle("Browse by category").setItems(names,(d,which)->{discoverMode="browse";discoverCategory=which==0?"":groups[which-1].title;discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();}).setNegativeButton("Cancel",null).show();
  }''')

# Browse results now support both category and subcategory.
s=replace_method(s,'  void renderBrowseResultsV6(',r'''  void renderBrowseResultsV6(LinearLayout target,String query){
    target.removeAllViews();askSelectionGoal="";String q=query==null?"":query.trim();ArrayList<Cmd> rows=new ArrayList<>();
    if(q.isEmpty()){
      for(Cmd c:all){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }else{
      for(Cmd c:rankSmart(q,350)){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }
    String scope=discoverFavorites?"Favorites":discoverCategory.isEmpty()?"All prompts":discoverSubcategory.isEmpty()?discoverCategory:discoverCategory+"  ›  "+discoverSubcategory;
    TextView meta=text(scope+"  ·  "+rows.size(),10,true,TERTIARY);meta.setPadding(dp(1),dp(9),0,dp(5));target.addView(meta);
    if(rows.isEmpty()){LinearLayout e=surface(true);TextView t=text("No prompts match this category and filter.",11,false,MUTED);t.setGravity(Gravity.CENTER);t.setPadding(0,dp(15),0,dp(15));e.addView(t);target.addView(e);return;}
    int limit=Math.min(browseLimit,rows.size());for(int i=0;i<limit;i++){Cmd c=rows.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}if(limit<rows.size()){Button more=secondary("Show more  ("+(rows.size()-limit)+" remaining)");more.setOnClickListener(v->{browseLimit+=30;home();});target.addView(more);}
  }''')

# Upgrade Browse section of home: category + subcategory picker + visible subcategory chips.
a,b=method_span(s,'  void home()');block=s[a:b]
old='LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverCategory="";discoverPreset=q.getText().toString();browseLimit=30;home();});filters.addView(fav);if(!discoverCategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});filters.addView(clear);}root.addView(filters);LinearLayout results=vbox();root.addView(results);'
new='LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);if(!discoverCategory.isEmpty()){Button subcat=filterChip(discoverSubcategory.isEmpty()?"All subcategories":discoverSubcategory,!discoverSubcategory.isEmpty());subcat.setOnClickListener(v->showSubcategoryPickerV12());filters.addView(subcat);}Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverPreset=q.getText().toString();browseLimit=30;home();});filters.addView(fav);if(!discoverCategory.isEmpty()||!discoverSubcategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});filters.addView(clear);}root.addView(filters);if(!discoverCategory.isEmpty()){HorizontalScrollView subscroll=new HorizontalScrollView(this);subscroll.setHorizontalScrollBarEnabled(false);LinearLayout subs=hbox();Button allSub=filterChip("All",discoverSubcategory.isEmpty());allSub.setOnClickListener(v->{discoverSubcategory="";browseLimit=30;home();});subs.addView(allSub);for(String sn:subcategoriesForV12(discoverCategory)){if(subcategoryCountV12(discoverCategory,sn)<=0)continue;Button sb=filterChip(sn,sn.equals(discoverSubcategory));sb.setOnClickListener(v->{discoverSubcategory=sn;browseLimit=30;home();});subs.addView(sb);}subscroll.addView(subs);root.addView(subscroll);}LinearLayout results=vbox();root.addView(results);'
if old not in block: raise SystemExit('browse filter block anchor missing')
block=block.replace(old,new,1);s=s[:a]+block+s[b:]

# Ensure mode switches/reset paths do not keep stale subcategory.
s=s.replace('discoverCategory="";discoverFavorites=false;','discoverCategory="";discoverSubcategory="";discoverFavorites=false;')

# Version bump.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 35',g,count=1)
GRADLE.write_text(g,encoding='utf-8')

for token in ['Writing & Communication','Research & Analysis','Planning & Decisions','Work & Business','Technology & Data','Learning & Education','Creativity & Content','Images & Design','Health & Life','String discoverSubcategory="";','subcategoriesForV12(String cat)','showSubcategoryPickerV12()','discoverCategory+"  ›  "+discoverSubcategory']:
    if token not in s: raise SystemExit('v12 gate missing: '+token)

JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v12 applied: redesigned 9-category taxonomy, 51 focused subcategories, category/subcategory browse filters')
