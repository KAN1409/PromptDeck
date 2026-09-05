#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path('.')
JAVA=ROOT/'android/app/src/main/java/com/kareem/promptdeck/MainActivity.java'
GRADLE=ROOT/'android/app/build.gradle'


def method_span(s, marker):
    start=s.find(marker)
    if start < 0:
        raise SystemExit(f'method marker missing: {marker}')
    brace=s.find('{',start)
    if brace < 0:
        raise SystemExit(f'opening brace missing: {marker}')
    depth=0;i=brace;in_str=False;esc=False;quote=''
    while i < len(s):
        ch=s[i]
        if in_str:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: in_str=False
        else:
            if ch in ('"',"'"): in_str=True;quote=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:return start,i+1
        i+=1
    raise SystemExit(f'unclosed method: {marker}')


def replace_method(s, marker, block):
    a,b=method_span(s,marker)
    return s[:a]+block+s[b:]


def insert_before(s, marker, block):
    p=s.find(marker)
    if p<0:raise SystemExit(f'insert marker missing: {marker}')
    return s[:p]+block+s[p:]

s=JAVA.read_text(encoding='utf-8')

# ------------------------------------------------------------------
# Pixel-lock pass 2: the approved proposal is the visual source of truth.
# Key correction: the PromptDeck brand row belongs on Home only.
# ------------------------------------------------------------------

if 'ImageView drawableIcon(int res,int tint)' not in s:
    helper='''  ImageView drawableIcon(int res,int tint){ImageView v=new ImageView(this);v.setImageResource(res);v.setColorFilter(tint);v.setScaleType(ImageView.ScaleType.CENTER_INSIDE);return v;}\n\n'''
    s=insert_before(s,'  LinearLayout bottomNav(){',helper)

s=replace_method(s,'  void base(',r'''  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);
    ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);sv.setClipToPadding(false);
    root=vbox();root.setPadding(dp(14),dp(8),dp(14),dp(16));root.setClipChildren(false);root.setClipToPadding(false);sv.addView(root);
    LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,0,1);shell.addView(sv,sp);
    shell.addView(bottomNav(),new LinearLayout.LayoutParams(-1,dp(62)));setContentView(shell);
    sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();if(top>0)root.setPadding(dp(14),Math.max(dp(8),top+dp(4)),dp(14),dp(16));return insets;});

    if("home".equals(page)){
      LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);
      ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.promptdeck_mark);mark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(28),dp(28));mp.setMargins(0,0,dp(7),0);top.addView(mark,mp);
      TextView brand=text("PromptDeck",17,true,TEXT);brand.setGravity(Gravity.CENTER_VERTICAL);top.addView(brand,new LinearLayout.LayoutParams(0,dp(30),1));
      ImageView gear=drawableIcon(R.drawable.pd_nav_settings,TEXT);gear.setPadding(dp(6),dp(6),dp(6),dp(6));gear.setContentDescription("Settings");gear.setOnClickListener(v->settings());top.addView(gear,new LinearLayout.LayoutParams(dp(32),dp(32)));
      root.addView(top,new LinearLayout.LayoutParams(-1,dp(34)));
    }else if("group".equals(page)||"detail".equals(page)||"customDetail".equals(page)){
      LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);
      TextView back=text("‹",30,false,TEXT);back.setGravity(Gravity.CENTER_VERTICAL);back.setPadding(0,0,dp(8),0);back.setOnClickListener(v->{if("group".equals(page))browseCategories();else if("detail".equals(page)&&currentGroup!=null)group(currentGroup);else if("customDetail".equals(page))library();else home();});top.addView(back,new LinearLayout.LayoutParams(dp(34),dp(32)));
      Space fill=new Space(this);top.addView(fill,new LinearLayout.LayoutParams(0,dp(1),1));root.addView(top,new LinearLayout.LayoutParams(-1,dp(34)));
    }

    if(title!=null&&!title.isEmpty()){TextView ttl=text(title,22,true,TEXT);ttl.setPadding(0,"home".equals(page)?dp(9):dp(3),0,dp(2));ttl.setGravity(Gravity.START);root.addView(ttl);}
    if(sub!=null&&!sub.isEmpty()){TextView st=text(sub,12,false,MUTED);st.setLineSpacing(0,1.06f);st.setPadding(0,0,0,dp(9));st.setGravity(Gravity.START);root.addView(st);}
  }''')

s=replace_method(s,'  LinearLayout bottomNav()',r'''  LinearLayout bottomNav(){
    LinearLayout nav=hbox();nav.setGravity(Gravity.CENTER);nav.setPadding(dp(3),dp(3),dp(3),dp(3));nav.setBackground(satinShape(Color.rgb(7,17,29),Color.rgb(5,14,24),BORDER,0));
    nav.addView(navItem(R.drawable.pd_nav_home,"Home",navActive("home"),()->home()),new LinearLayout.LayoutParams(0,-1,1));
    nav.addView(navItem(R.drawable.pd_nav_search,"Browse",navActive("browse"),()->searchPage()),new LinearLayout.LayoutParams(0,-1,1));
    nav.addView(navItem(R.drawable.pd_nav_stack,"Stack",navActive("stack"),()->stack()),new LinearLayout.LayoutParams(0,-1,1));
    nav.addView(navItem(R.drawable.pd_nav_document,"My Prompts",navActive("my"),()->library()),new LinearLayout.LayoutParams(0,-1,1));
    nav.addView(navItem(R.drawable.pd_nav_settings,"Settings",navActive("settings"),()->settings()),new LinearLayout.LayoutParams(0,-1,1));return nav;
  }''')

s=replace_method(s,'  View navItem(',r'''  View navItem(int iconRes,String label,boolean active,Runnable action){
    LinearLayout x=vbox();x.setGravity(Gravity.CENTER);ImageView i=drawableIcon(iconRes,active?ACCENT:TERTIARY);i.setPadding(dp(5),dp(4),dp(5),dp(3));TextView l=text(label,9,active,active?ACCENT:TERTIARY);l.setGravity(Gravity.CENTER);x.addView(i,new LinearLayout.LayoutParams(-1,dp(29)));x.addView(l,new LinearLayout.LayoutParams(-1,dp(17)));x.setOnClickListener(v->action.run());return x;
  }''')

s=replace_method(s,'  void spacerH(',r'''  void spacerH(LinearLayout row){Space s=new Space(this);row.addView(s,new LinearLayout.LayoutParams(dp(6),1));}''')

s=replace_method(s,'  LinearLayout surface(',r'''  LinearLayout surface(boolean compact){LinearLayout l=vbox();l.setPadding(dp(compact?10:12),dp(compact?8:10),dp(compact?10:12),dp(compact?8:10));l.setBackground(satinShape(SURFACE2,SURFACE,BORDER,14));l.setElevation(0);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(1),0,dp(6));l.setLayoutParams(lp);return l;}''')

s=replace_method(s,'  TextView sectionTitle(',r'''  TextView sectionTitle(String title,String action){TextView v=text(action==null?title:title+"                                      "+action,13,true,TEXT);v.setPadding(dp(1),dp(12),0,dp(6));return v;}''')

s=replace_method(s,'  View goalTile(',r'''  View goalTile(String icon,String title,String query,int accent){LinearLayout card=vbox();card.setPadding(dp(9),dp(7),dp(7),dp(7));card.setGravity(Gravity.START);card.setBackground(tintedCard(accent,14));TextView ic=text(icon,18,true,accent);card.addView(ic,new LinearLayout.LayoutParams(-1,dp(24)));TextView t=text(title,10,true,TEXT);t.setMaxLines(2);card.addView(t);card.setOnClickListener(v->smartCollection(title,"Best matching prompts",query,null,"Best matches"));return card;}''')

s=replace_method(s,'  View collectionTile(',r'''  View collectionTile(String icon,String title,String sub,String query,int accent){LinearLayout card=hbox();card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(7),dp(6),dp(7),dp(6));card.setBackground(tintedCard(accent,12));TextView ic=iconTile(icon,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(29),dp(29));ip.setMargins(0,0,dp(7),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,10,true,TEXT));TextView d=text(sub,8,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.setOnClickListener(v->smartCollection(title,sub,query,null,"Best matches"));return card;}''')

s=replace_method(s,'  View groupCard(',r'''  View groupCard(Group g){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(8),dp(7));
    int accent=groupAccent(g);TextView icon=iconTile(g.icon,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(icon,ip);
    LinearLayout copy=vbox();TextView title=text(displayGroupTitle(g),13,true,TEXT);TextView sub=text(g.sub,9,false,MUTED);sub.setMaxLines(1);copy.addView(title);copy.addView(sub);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));
    TextView count=text(String.valueOf(groupCount(g)),9,false,TERTIARY);count.setPadding(dp(6),0,dp(5),0);card.addView(count);card.addView(text("›",20,false,TERTIARY));return card;
  }''')

s=replace_method(s,'  View menuCard(',r'''  View menuCard(String icon,String title,String sub){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(8),dp(7));TextView ic=iconTile(icon,ACCENT);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,13,true,TEXT));TextView d=text(sub,9,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",20,false,TERTIARY));return card;
  }''')

s=replace_method(s,'  View commandRow(',r'''  View commandRow(Cmd c,boolean divider){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(8),dp(7),dp(7),dp(7));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(35),dp(35));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView title=text(displayTitle(c),13,true,TEXT);title.setMaxLines(1);copy.addView(title);TextView d=text(shortDescription(c),9,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView star=text(isFavorite(c)?"★":"☆",15,false,isFavorite(c)?FAVORITE:TERTIARY);star.setGravity(Gravity.CENTER);star.setOnClickListener(v->{toggleFavorite(c);star.setText(isFavorite(c)?"★":"☆");star.setTextColor(isFavorite(c)?FAVORITE:TERTIARY);});card.addView(star,new LinearLayout.LayoutParams(dp(29),dp(35)));TextView more=text("⋯",17,false,TERTIARY);more.setGravity(Gravity.CENTER);card.addView(more,new LinearLayout.LayoutParams(dp(22),dp(35)));return card;
  }''')

s=replace_method(s,'  Button filterChip(',r'''  Button filterChip(String label,boolean active){
    Button b=new Button(this);b.setAllCaps(false);b.setText(label);b.setTextSize(9);b.setTextColor(active?Color.WHITE:MUTED);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));b.setSingleLine(true);b.setMinWidth(0);b.setMinHeight(0);b.setPadding(dp(9),0,dp(9),0);b.setBackground(shape(active?ACCENT:SURFACE2,active?ACCENT:BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(29));lp.setMargins(0,0,dp(6),0);b.setLayoutParams(lp);return b;
  }''')

s=replace_method(s,'  EditText input(',r'''  EditText input(String hint,int lines){EditText e=new EditText(this);e.setHint(hint);e.setHintTextColor(TERTIARY);e.setTextColor(TEXT);e.setTextSize(12);e.setGravity((lines==1?Gravity.CENTER_VERTICAL:Gravity.TOP)|Gravity.START);e.setSingleLine(lines==1);e.setMinLines(lines);e.setPadding(dp(12),lines==1?0:dp(9),dp(12),lines==1?0:dp(9));e.setBackground(shape(INPUT,BORDER,14));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,lines==1?dp(42):-2);lp.setMargins(0,dp(2),0,dp(7));e.setLayoutParams(lp);return e;}''')

s=replace_method(s,'  Button styledButton(',r'''  Button styledButton(String textValue,int fill,int stroke,int color){Button x=new Button(this);x.setText(textValue);x.setAllCaps(false);x.setTextColor(color);x.setTextSize(12);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));if(fill==ACCENT)x.setBackground(gradientShape(ACCENT,PURPLE,Color.rgb(80,126,255),14));else x.setBackground(satinShape(SURFACE2,SURFACE,stroke,14));x.setElevation(0);x.setPadding(dp(10),dp(6),dp(10),dp(6));x.setMinHeight(dp(44));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(44));lp.setMargins(0,dp(3),0,dp(3));x.setLayoutParams(lp);return x;}''')

# Home: same approved structure, corrected density.
s=replace_method(s,'  void home()',r'''  void home(){
    page="home";currentGroup=null;base("Find the right prompt","What do you want to do?",false);
    EditText discover=input("e.g. plan a trip, write a resume, explain a topic...",1);discover.setSingleLine(true);discover.setImeOptions(EditorInfo.IME_ACTION_SEARCH);root.addView(discover);
    LinearLayout live=vbox();live.setVisibility(View.GONE);root.addView(live);
    discover.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderSmartSearch(live,x.toString());}public void afterTextChanged(android.text.Editable e){}});
    root.addView(sectionTitle("Quick Goals",null));
    LinearLayout r1=hbox();r1.addView(goalTile("✎","Write or rewrite","writing rewrite text",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(0,dp(74),1));spacerH(r1);r1.addView(goalTile("⌕","Research something","research analysis verify sources",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(0,dp(74),1));spacerH(r1);r1.addView(goalTile("◈","Think & decide","brainstorm decision critique ideas",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(0,dp(74),1));root.addView(r1);
    spacer(6);
    LinearLayout r2=hbox();r2.addView(goalTile("▣","Plan something","plan roadmap checklist execution",Color.rgb(96,92,255)),new LinearLayout.LayoutParams(0,dp(74),1));spacerH(r2);r2.addView(goalTile("▤","Learn something","learn explain teach study",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(0,dp(74),1));spacerH(r2);r2.addView(goalTile("⚙","Fix a technical problem","debug technical code fix",Color.rgb(243,92,107)),new LinearLayout.LayoutParams(0,dp(74),1));root.addView(r2);
    spacer(6);View image=goalTile("▧","Create or edit an image","photo image portrait generation editing",Color.rgb(32,199,201));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams((int)(getResources().getDisplayMetrics().widthPixels*.50f),dp(52));image.setLayoutParams(ip);root.addView(image);
    LinearLayout sh=hbox();sh.setGravity(Gravity.CENTER_VERTICAL);TextView st=sectionTitle("Smart Collections",null);sh.addView(st,new LinearLayout.LayoutParams(0,-2,1));TextView see=text("See all",10,true,ACCENT);see.setGravity(Gravity.CENTER_VERTICAL|Gravity.END);see.setPadding(dp(8),dp(12),0,dp(6));see.setOnClickListener(v->searchPage("","Collections"));sh.addView(see);root.addView(sh);
    LinearLayout c1=hbox();c1.addView(collectionTile("⚖","Compare & choose","Make better decisions","compare recommend decision options",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(0,dp(54),1));spacerH(c1);c1.addView(collectionTile("★","Best for ChatGPT","Top prompting workflows","chatgpt prompt optimize ai",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(0,dp(54),1));root.addView(c1);spacer(6);
    LinearLayout c2=hbox();c2.addView(collectionTile("▣","Career toolkit","Jobs, resumes, interviews","career resume interview email",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(0,dp(54),1));spacerH(c2);c2.addView(collectionTile("▥","Content studio","Blog, social, marketing","content hook script caption story",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(0,dp(54),1));root.addView(c2);
  }''')

s=replace_method(s,'  void browseCategories()',r'''  void browseCategories(){
    page="categories";currentGroup=null;base("Browse Categories","",false);
    EditText q=input("Search categories or prompts...",1);q.setSingleLine(true);root.addView(q);LinearLayout results=vbox();root.addView(results);renderCategoryCards(results,"");
    q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderCategoryCards(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }''')

s=replace_method(s,'  void group(Group g,String activeSub,String initialQuery)',r'''  void group(Group g,String activeSub,String initialQuery){
    page="group";currentGroup=g;base("","",false);
    LinearLayout hero=hbox();hero.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(g.icon,groupAccent(g));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(46),dp(46));ip.setMargins(0,0,dp(10),0);hero.addView(ic,ip);LinearLayout hcopy=vbox();TextView title=text(displayGroupTitle(g),18,true,TEXT);TextView desc=text(g.sub,10,false,MUTED);desc.setMaxLines(1);hcopy.addView(title);hcopy.addView(desc);hero.addView(hcopy,new LinearLayout.LayoutParams(0,-2,1));TextView count=text(groupCount(g)+" prompts",10,true,TERTIARY);count.setGravity(Gravity.BOTTOM|Gravity.END);hero.addView(count,new LinearLayout.LayoutParams(-2,dp(46)));root.addView(hero);spacer(7);
    ArrayList<Cmd> items=groupCommands(g);LinkedHashMap<String,Integer> counts=new LinkedHashMap<>();for(Cmd c:items){String sc=groupSubcategory(c,g);counts.put(sc,counts.containsKey(sc)?counts.get(sc)+1:1);}
    HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout chips=hbox();chips.setPadding(0,dp(1),dp(3),dp(6));hsv.addView(chips);root.addView(hsv);Button allChip=filterChip("All",activeSub==null);allChip.setOnClickListener(v->group(g,null,""));chips.addView(allChip);for(String sc:counts.keySet()){Button chip=filterChip(sc,sc.equals(activeSub));chip.setOnClickListener(v->group(g,sc,""));chips.addView(chip);}
    LinearLayout results=vbox();root.addView(results);renderGroupResults(g,results,"",activeSub);
  }''')

s=replace_method(s,'  void detail(',r'''  void detail(Cmd c,Group g){
    page="detail";currentGroup=g;rememberRecent(c);base("","",false);
    LinearLayout identity=hbox();identity.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(44),dp(44));ip.setMargins(0,0,dp(10),0);identity.addView(ic,ip);LinearLayout copy=vbox();TextView title=text(displayTitle(c),18,true,TEXT);title.setMaxLines(1);copy.addView(title);TextView sub=text(shortDescription(c),10,false,MUTED);sub.setMaxLines(1);copy.addView(sub);LinearLayout tags=hbox();String[] tt=detailTags(c);for(String t:tt)tags.addView(smallTag(t));copy.addView(tags);identity.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView star=text(isFavorite(c)?"★":"☆",19,false,isFavorite(c)?FAVORITE:TERTIARY);star.setGravity(Gravity.CENTER);star.setOnClickListener(v->{toggleFavorite(c);star.setText(isFavorite(c)?"★":"☆");star.setTextColor(isFavorite(c)?FAVORITE:TERTIARY);});identity.addView(star,new LinearLayout.LayoutParams(dp(34),dp(44)));TextView more=text("⋯",19,false,TERTIARY);more.setGravity(Gravity.CENTER);identity.addView(more,new LinearLayout.LayoutParams(dp(25),dp(44)));root.addView(identity);spacer(8);
    LinearLayout promptCard=surface(false);TextView body=text(c.instruction,11,false,TEXT);body.setLineSpacing(dp(1),1.10f);promptCard.addView(body);root.addView(promptCard);
    ArrayList<String> vars=templateVariables(c.instruction);if(!vars.isEmpty()){LinearLayout variableCard=surface(false);TextView vl=text("Variables (optional)  ⓘ",12,true,TEXT);vl.setPadding(0,0,0,dp(5));variableCard.addView(vl);for(String key:vars){TextView lab=text(prettyKey(key),9,false,MUTED);lab.setPadding(dp(1),dp(2),0,dp(2));variableCard.addView(lab);EditText field=input("e.g. "+prettyKey(key).toLowerCase(Locale.ROOT),1);String old=promptVar(c.id,key);field.setText(old);field.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int co,int a){}public void onTextChanged(CharSequence x,int st,int b,int co){setPromptVar(c.id,key,x.toString());}public void afterTextChanged(android.text.Editable e){}});variableCard.addView(field);}Button add=selected.contains(c)?secondary("✓  Added to Stack"):primary("＋  Add to Stack");add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);stack();});variableCard.addView(add);root.addView(variableCard);}else{Button add=selected.contains(c)?secondary("✓  Added to Stack"):primary("＋  Add to Stack");add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);stack();});root.addView(add);}
    TextView tryTitle=text("Try it now",12,true,TEXT);tryTitle.setPadding(0,dp(8),0,dp(4));root.addView(tryTitle);EditText tryBox=input("Add your context or specific request...",4);tryBox.setMaxLines(6);root.addView(tryBox);Button run=primary("➤  Run with ChatGPT");run.setOnClickListener(v->sendText(buildSinglePrompt(c,tryBox.getText().toString().trim())));root.addView(run);relatedActions(c.command);
  }''')

s=replace_method(s,'  void stack()',r'''  void stack(){
    if(context!=null)contextDraft=context.getText().toString();page="stack";base("Prompt Stack","",false);
    if(selected.isEmpty()){LinearLayout empty=surface(true);TextView e=text("Your stack is empty. Discover a prompt and add it here.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(16),0,dp(16));empty.addView(e);root.addView(empty);Button browse=primary("Browse prompts");browse.setOnClickListener(v->searchPage());root.addView(browse);return;}
    LinearLayout actions=hbox();TextView count=text(selected.size()+" steps",10,true,TERTIARY);actions.addView(count,new LinearLayout.LayoutParams(0,dp(28),1));Button clear=compactControl("Clear");clear.setOnClickListener(v->{selected.clear();stack();});actions.addView(clear,new LinearLayout.LayoutParams(dp(62),dp(28)));root.addView(actions);
    for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView num=text(String.valueOf(i+1),9,true,TERTIARY);num.setGravity(Gravity.CENTER);card.addView(num,new LinearLayout.LayoutParams(dp(20),dp(38)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),12,true,TEXT));TextView d=text(shortDescription(c),9,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));LinearLayout controls=hbox();Button up=mini("↑"),dn=mini("↓"),rm=mini("×");up.setEnabled(k>0);dn.setEnabled(k<selected.size()-1);up.setOnClickListener(v->{if(k>0)Collections.swap(selected,k,k-1);stack();});dn.setOnClickListener(v->{if(k<selected.size()-1)Collections.swap(selected,k,k+1);stack();});rm.setOnClickListener(v->{selected.remove(k);stack();});controls.addView(up);controls.addView(dn);controls.addView(rm);card.addView(controls);root.addView(card);}
    context=input("Enter your request, text or context...",3);context.setMaxLines(6);context.setText(contextDraft);root.addView(context);Button more=secondary("＋  Add Another Prompt");more.setOnClickListener(v->{contextDraft=context==null?contextDraft:context.getText().toString();searchPage();});root.addView(more);Button run=primary("➤  Run Stack with ChatGPT");run.setOnClickListener(v->build());root.addView(run);
  }''')

s=replace_method(s,'  void library(boolean favoritesMode)',r'''  void library(boolean favoritesMode){
    page="library";currentGroup=null;base("My Prompts","",false);LinearLayout seg=hbox();Button mine=filterChip("My Prompts",!favoritesMode),fav=filterChip("Favorites",favoritesMode);mine.setOnClickListener(v->library(false));fav.setOnClickListener(v->library(true));LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(31),1);a.setMargins(0,0,dp(6),0);seg.addView(mine,a);seg.addView(fav,new LinearLayout.LayoutParams(0,dp(31),1));root.addView(seg);spacer(8);
    ArrayList<Cmd> rows=new ArrayList<>();for(Cmd c:all){if(favoritesMode){if(isFavorite(c))rows.add(c);}else if(c.custom)rows.add(c);}if(rows.isEmpty()){LinearLayout empty=surface(true);TextView e=text(favoritesMode?"No favorites yet.":"No custom prompts yet.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(15),0,dp(15));empty.addView(e);root.addView(empty);}else for(Cmd c:rows){View row=commandRow(c,false);row.setOnClickListener(v->{if(c.custom)customDetail(c);else detail(c,groupFor(c));});root.addView(row);}if(!favoritesMode){Button create=secondary("＋  Create a New Prompt");create.setOnClickListener(v->showAdd());root.addView(create);LinearLayout tools=hbox();Button paste=ghost("Paste");paste.setOnClickListener(v->showBulkPaste());Button imp=ghost("Import");imp.setOnClickListener(v->openImport());Button exp=ghost("Export");exp.setOnClickListener(v->openExport());tools.addView(paste,new LinearLayout.LayoutParams(0,dp(42),1));spacerH(tools);tools.addView(imp,new LinearLayout.LayoutParams(0,dp(42),1));spacerH(tools);tools.addView(exp,new LinearLayout.LayoutParams(0,dp(42),1));root.addView(tools);}
  }''')

s=replace_method(s,'  void searchPage(String initial,String mode)',r'''  void searchPage(String initial,String mode){page="search";currentGroup=null;base("Search","",false);EditText q=input("Search prompts or describe what you want...",1);q.setSingleLine(true);q.setText(initial);root.addView(q);LinearLayout chips=hbox();String[] modes={"All","Prompts","Categories","Collections"};for(int i=0;i<modes.length;i++){String m=modes[i];Button b=filterChip(m,m.equals(mode));b.setOnClickListener(v->searchPage(q.getText().toString(),m));LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,dp(29),1);if(i<modes.length-1)cp.setMargins(0,0,dp(5),0);chips.addView(b,cp);}root.addView(chips);spacer(7);LinearLayout results=vbox();root.addView(results);renderSearchResults(results,q.getText().toString(),mode);q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderSearchResults(results,x.toString(),mode);}public void afterTextChanged(android.text.Editable e){}});}''')

s=replace_method(s,'  void settings()',r'''  void settings(){page="settings";currentGroup=null;base("Settings","",false);View a=menuCard("⚙","App Preferences","Theme, language and behavior");a.setOnClickListener(v->toast("PromptDeck uses the locked dark v0.8.1 appearance."));root.addView(a);View b=menuCard("◎","ChatGPT Connection","Configure your ChatGPT access");b.setOnClickListener(v->toast("PromptDeck sends prompts to the ChatGPT app when available."));root.addView(b);View c=menuCard("▣","Data & Storage","Manage your data");c.setOnClickListener(v->toast(all.size()+" prompts loaded locally"));root.addView(c);View d=menuCard("ⓘ","About PromptDeck","Version 0.8.1");d.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("PromptDeck 0.8.1").setMessage("Discover. Customize. Stack. Create. All with ChatGPT.").setPositiveButton("OK",null).show());root.addView(d);}''')

# Keep the visible proposal version while increasing Android versionCode for update testing.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 25',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.1'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')

checks=[
  'R.drawable.promptdeck_mark','R.drawable.pd_nav_home','R.drawable.pd_nav_search','R.drawable.pd_nav_stack','R.drawable.pd_nav_document','R.drawable.pd_nav_settings',
  'base("Settings","",false)','base("Search","",false)','base("Prompt Stack","",false)','base("My Prompts","",false)',
  'new LinearLayout.LayoutParams(0,dp(74),1)','new LinearLayout.LayoutParams(0,dp(54),1)'
]
for token in checks:
    if token not in s:raise SystemExit('pixel-lock gate missing: '+token)
if 'TextView brand=text("PromptDeck"' not in s:raise SystemExit('home brand missing')
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v0.8.1 pixel-lock v2 applied')
