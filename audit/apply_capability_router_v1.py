#!/usr/bin/env python3
from pathlib import Path
import re

src = Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
gradle = Path('android/app/build.gradle')
text = src.read_text(encoding='utf-8')

start = text.find('  void base(String title,String sub,boolean showStack){')
end = text.find('  void addGoalCard(', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate base/home UX segment')

replacement = r'''  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);
    ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);
    root=vbox();root.setPadding(dp(14),dp(8),dp(14),dp(18));sv.addView(root);
    shell.addView(sv,new LinearLayout.LayoutParams(-1,0,1));
    if(!selected.isEmpty())shell.addView(selectionBar(),new LinearLayout.LayoutParams(-1,dp(56)));
    if("home".equals(page))shell.addView(primaryNavV18(),new LinearLayout.LayoutParams(-1,dp(58)));
    setContentView(shell);
    sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();if(top>0)root.setPadding(dp(14),Math.max(dp(8),top+dp(3)),dp(14),dp(18));return insets;});
    LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);
    ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.promptdeck_mark);mark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
    LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(30),dp(30));mp.setMargins(0,0,dp(7),0);top.addView(mark,mp);
    top.addView(text("PromptDeck",18,true,TEXT),new LinearLayout.LayoutParams(0,dp(32),1));
    TextView more=text("⋯",24,true,TEXT);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showMoreMenu());top.addView(more,new LinearLayout.LayoutParams(dp(38),dp(36)));
    root.addView(top);spacer(9);
  }

  View primaryNavV18(){
    LinearLayout bar=hbox();bar.setGravity(Gravity.CENTER);bar.setPadding(dp(10),dp(8),dp(10),dp(8));bar.setBackgroundColor(SURFACE);
    Button home=filterChip("Home","landing".equals(discoverMode));home.setOnClickListener(v->{discoverMode="landing";discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});
    Button find=filterChip("Find","ask".equals(discoverMode));find.setOnClickListener(v->{discoverMode="ask";home();});
    Button library=filterChip("Library","browse".equals(discoverMode));library.setOnClickListener(v->{discoverMode="browse";home();});
    LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(40),1);p.setMargins(dp(3),0,dp(3),0);
    home.setLayoutParams(new LinearLayout.LayoutParams(p));find.setLayoutParams(new LinearLayout.LayoutParams(p));library.setLayoutParams(new LinearLayout.LayoutParams(p));
    bar.addView(home);bar.addView(find);bar.addView(library);return bar;
  }

  void home(){
    page="home";currentGroup=null;base("","",false);

    if("landing".equals(discoverMode)){
      TextView h=text("What do you want to accomplish?",23,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);
      TextView sub=text("Start with the outcome. PromptDeck will route you to the right prompt, capability or workflow.",11,false,MUTED);sub.setPadding(0,0,0,dp(10));root.addView(sub);

      EditText goal=input("Describe anything you want to do…",2);goal.setMaxLines(4);goal.setImeOptions(EditorInfo.IME_ACTION_DONE);root.addView(goal);
      Button route=primary("Find the best approach");root.addView(route);
      View.OnClickListener run=v->{String q=goal.getText().toString().trim();if(q.length()<2){toast("Describe what you want first");return;}askGoal=q;contextDraft=q;discoverMode="ask";home();};
      route.setOnClickListener(run);goal.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){run.onClick(v);return true;}return false;});

      ArrayList<Cmd> recent=recentCommands();
      if(!recent.isEmpty()){
        root.addView(label("CONTINUE"));
        for(Cmd c:recent){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,groupFor(c)));root.addView(row);}
        spacer(6);
      }

      root.addView(label("QUICK START"));
      addGoalCard("✦","Work with an image","Edit, enhance, relight or restyle a photo.","photo image edit enhance","lighting","color","portrait","background");
      addGoalCard("⌕","Research something","Find, verify, compare and synthesize reliable information.","research verify sources evidence","deep research","compare","fact check");
      addGoalCard("✎","Write or rewrite","Create, polish, shorten, translate or improve text.","write rewrite professional text","email","rewrite","summarize");
      addGoalCard("◫","Analyze something","Extract insight from data, files, options or information.","analyze compare insights data","data analysis","compare","extract");
      addGoalCard("◎","Plan or decide","Turn uncertainty into a plan, roadmap or decision.","plan decision compare tradeoffs","roadmap","prioritize","recommend");
      addGoalCard("⌘","Build or fix","Code, debug, troubleshoot and improve technical work.","code debug fix technical","debug","android","software");
      addGoalCard("◇","Learn something","Understand, study, practise or teach a topic.","learn explain teach study","explain","study","quiz");

      View browse=menuCard("☰","Explore the full library",String.format(Locale.US,"%,d",BUILTIN_CACHE_V15.size())+" prompts organized by capability and category");browse.setOnClickListener(v->{discoverMode="browse";home();});root.addView(browse);
      View add=menuCard("＋","Add a prompt","Paste a complete prompt or import a visual prompt pack");add.setOnClickListener(v->showBulkPaste());root.addView(add);
      TextView hint=text("You never need to remember a command name. Start with what you want to achieve.",9,false,TERTIARY);hint.setGravity(Gravity.CENTER);hint.setPadding(dp(6),dp(10),dp(6),0);root.addView(hint);return;
    }

    if("ask".equals(discoverMode)){
      TextView h=text("Find anything",22,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);
      TextView sub=text("Describe the outcome in your own words. PromptDeck will resolve the intent and surface the strongest route.",10,false,MUTED);sub.setPadding(0,0,0,dp(8));root.addView(sub);
      EditText goal=input("e.g. Make this photo look premium but natural…",3);goal.setMaxLines(5);goal.setImeOptions(EditorInfo.IME_ACTION_DONE);goal.setText(askGoal);root.addView(goal);
      Button find=primary("Resolve my intent");root.addView(find);
      HorizontalScrollView examples=new HorizontalScrollView(this);examples.setHorizontalScrollBarEnabled(false);LinearLayout ex=hbox();
      String[] xs={"Improve a photo","Compare two options","Research deeply","Fix a bug","Write professionally","Plan a project"};
      for(String x:xs){Button b=filterChip(x,false);b.setOnClickListener(v->{goal.setText(x);goal.setSelection(goal.length());});ex.addView(b);}examples.addView(ex);root.addView(examples);
      LinearLayout results=vbox();root.addView(results);if(!askGoal.isEmpty())renderAskResults(results,askGoal);
      find.setOnClickListener(v->runAskRecommendation(results,goal));goal.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){askGoal=x.toString();}public void afterTextChanged(android.text.Editable e){}});goal.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){runAskRecommendation(results,goal);return true;}return false;});return;
    }

    TextView h=text("Library",22,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);
    TextView sub=text("Browse the canonical library when you want to explore manually.",10,false,MUTED);sub.setPadding(0,0,0,dp(7));root.addView(sub);
    EditText q=input("Search prompts, outcomes or capabilities…",1);q.setSingleLine(true);q.setText(discoverPreset);root.addView(q);
    LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);
    if(!discoverCategory.isEmpty()){Button subcat=filterChip(discoverSubcategory.isEmpty()?"All subcategories":discoverSubcategory,!discoverSubcategory.isEmpty());subcat.setOnClickListener(v->showSubcategoryPickerV12());filters.addView(subcat);}
    Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverPreset=q.getText().toString();browseLimit=30;home();});filters.addView(fav);
    if(!discoverCategory.isEmpty()||!discoverSubcategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});filters.addView(clear);}root.addView(filters);
    LinearLayout results=vbox();root.addView(results);renderBrowseResultsV6(results,q.getText().toString());q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();browseLimit=30;renderBrowseResultsV6(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }

'''

text = text[:start] + replacement + text[end:]
src.write_text(text, encoding='utf-8')

g = gradle.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 46', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.9.0-capability-router'", g, count=1)
gradle.write_text(g, encoding='utf-8')

# Static gates
out = src.read_text(encoding='utf-8')
required = [
    'What do you want to accomplish?',
    'Find anything',
    'Explore the full library',
    'View primaryNavV18()',
    'Work with an image',
    'Plan or decide',
    'versionName',
]
for token in required[:-1]:
    if token not in out:
        raise SystemExit(f'Missing UX token: {token}')
if 'versionCode 46' not in gradle.read_text() or "versionName '0.9.0-capability-router'" not in gradle.read_text():
    raise SystemExit('Version gate failed')
print('Capability Router UX v1 applied: 0.9.0-capability-router (46)')
