#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')


def method_span(s, marker):
    start=s.find(marker)
    if start<0: raise SystemExit('method marker missing: '+marker)
    brace=s.find('{',start)
    depth=0;i=brace;ins=False;esc=False;q=''
    while i<len(s):
        ch=s[i]
        if ins:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch==q:ins=False
        else:
            if ch in ('"',"'"):ins=True;q=ch
            elif ch=='{':depth+=1
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

s=JAVA.read_text(encoding='utf-8')

# ------------------------------------------------------------------
# v5 TWO-PAGE LOCK
# Main navigation is intentionally reduced to Discover + Stack only.
# Categories, favorites, custom prompts and settings are overlays/dialogs.
# ------------------------------------------------------------------

# Persistent discovery state.
if 'String discoverCategory="";' not in s:
    anchor='String page="home"; Group currentGroup=null; String contextDraft="";'
    if anchor not in s: raise SystemExit('page state anchor missing')
    s=s.replace(anchor,anchor+' String discoverCategory=""; boolean discoverFavorites=false; String discoverPreset="";',1)

helpers=r'''  void showCategoryPicker(){
    String[] names=new String[groups.length+1];names[0]="All categories";for(int i=0;i<groups.length;i++)names[i+1]=groups[i].title+"  ("+groupCount(groups[i])+")";
    new AlertDialog.Builder(this).setTitle("Browse by category").setItems(names,(d,which)->{discoverCategory=which==0?"":groups[which-1].title;discoverFavorites=false;discoverPreset="";home();}).setNegativeButton("Cancel",null).show();
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
  void showPromptDialog(Cmd c){
    ScrollView sv=new ScrollView(this);LinearLayout box=vbox();box.setPadding(dp(16),dp(8),dp(16),dp(8));sv.addView(box);
    TextView title=text(displayTitle(c),18,true,TEXT);box.addView(title);TextView desc=text(shortDescription(c),11,false,MUTED);desc.setPadding(0,dp(3),0,dp(10));box.addView(desc);
    String body=c.instruction==null?"":c.instruction.trim();if(body.length()>1100)body=body.substring(0,1097).trim()+"…";TextView prompt=text(body,11,false,TEXT);prompt.setLineSpacing(dp(1),1.10f);prompt.setPadding(0,0,0,dp(10));box.addView(prompt);
    ArrayList<String> vars=templateVariables(c.instruction);for(String key:vars){TextView l=text(prettyKey(key),10,true,MUTED);l.setPadding(0,dp(4),0,dp(3));box.addView(l);EditText field=input("Enter "+prettyKey(key).toLowerCase(Locale.ROOT),1);field.setText(promptVar(c.id,key));field.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int co,int a){}public void onTextChanged(CharSequence x,int st,int b,int co){setPromptVar(c.id,key,x.toString());}public void afterTextChanged(android.text.Editable e){}});box.addView(field);}
    Button fav=secondary(isFavorite(c)?"★  Favorited":"☆  Add to Favorites");fav.setOnClickListener(v->{toggleFavorite(c);fav.setText(isFavorite(c)?"★  Favorited":"☆  Add to Favorites");});box.addView(fav);
    String addLabel=selected.contains(c)?"Added to Stack":"Add to Stack";new AlertDialog.Builder(this).setView(sv).setPositiveButton(addLabel,(d,w)->{if(!selected.contains(c))selected.add(c);}).setNeutralButton("Run now",(d,w)->sendText(buildSinglePrompt(c,""))).setNegativeButton("Close",null).show();
  }

'''
if 'void showCategoryPicker(){' not in s:
    s=insert_before(s,'  String cleanUiText(String x)',helpers)

s=replace_method(s,'  void base(',r'''  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);root=vbox();root.setPadding(dp(14),dp(8),dp(14),dp(18));sv.addView(root);shell.addView(sv,new LinearLayout.LayoutParams(-1,0,1));shell.addView(bottomNav(),new LinearLayout.LayoutParams(-1,dp(58)));setContentView(shell);
    sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();if(top>0)root.setPadding(dp(14),Math.max(dp(8),top+dp(3)),dp(14),dp(18));return insets;});
    if("home".equals(page)){LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.promptdeck_mark);mark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(28),dp(28));mp.setMargins(0,0,dp(7),0);top.addView(mark,mp);top.addView(text("PromptDeck",17,true,TEXT),new LinearLayout.LayoutParams(0,dp(30),1));TextView more=text("⋯",24,true,TEXT);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showMoreMenu());top.addView(more,new LinearLayout.LayoutParams(dp(38),dp(34)));root.addView(top);spacer(7);}else{LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);top.addView(text("Stack",22,true,TEXT),new LinearLayout.LayoutParams(0,dp(34),1));if(!selected.isEmpty()){TextView badge=text(String.valueOf(selected.size()),10,true,TEXT);badge.setGravity(Gravity.CENTER);badge.setBackground(shape(BORDER,BORDER,16));top.addView(badge,new LinearLayout.LayoutParams(dp(28),dp(28)));}root.addView(top);spacer(5);}
  }''')

s=replace_method(s,'  LinearLayout bottomNav()',r'''  LinearLayout bottomNav(){
    LinearLayout nav=hbox();nav.setGravity(Gravity.CENTER);nav.setPadding(dp(8),dp(3),dp(8),dp(3));nav.setBackground(satinShape(Color.rgb(7,17,29),Color.rgb(5,14,24),BORDER,0));
    nav.addView(navItem(R.drawable.pd_nav_search,"Discover",!"stack".equals(page),()->home()),new LinearLayout.LayoutParams(0,-1,1));
    String stackLabel=selected.isEmpty()?"Stack":"Stack ("+selected.size()+")";nav.addView(navItem(R.drawable.pd_nav_stack,stackLabel,"stack".equals(page),()->stack()),new LinearLayout.LayoutParams(0,-1,1));return nav;
  }''')

s=replace_method(s,'  View navItem(',r'''  View navItem(int iconRes,String label,boolean active,Runnable action){LinearLayout x=vbox();x.setGravity(Gravity.CENTER);ImageView i=drawableIcon(iconRes,active?ACCENT:TERTIARY);i.setPadding(dp(5),dp(3),dp(5),dp(2));TextView l=text(label,9,active,active?ACCENT:TERTIARY);l.setGravity(Gravity.CENTER);x.addView(i,new LinearLayout.LayoutParams(-1,dp(27)));x.addView(l,new LinearLayout.LayoutParams(-1,dp(17)));x.setOnClickListener(v->action.run());return x;}''')

s=replace_method(s,'  View commandRow(',r'''  View commandRow(Cmd c,boolean divider){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(9),dp(7),dp(8),dp(7));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView t=text(displayTitle(c),13,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(t);TextView d=text(shortDescription(c),9,false,MUTED);d.setSingleLine(true);d.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView add=text(selected.contains(c)?"✓":"＋",18,true,selected.contains(c)?SUCCESS:ACCENT);add.setGravity(Gravity.CENTER);add.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);add.setText("✓");add.setTextColor(SUCCESS);toast("Added to Stack");}});card.addView(add,new LinearLayout.LayoutParams(dp(34),dp(36)));return card;
  }''')

s=replace_method(s,'  void home()',r'''  void home(){
    page="home";currentGroup=null;base("","",false);TextView h=text("What do you want to do?",22,true,TEXT);h.setPadding(0,0,0,dp(6));root.addView(h);EditText q=input("Search or describe your goal...",1);q.setSingleLine(true);q.setText(discoverPreset);root.addView(q);
    LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverCategory="";discoverPreset=q.getText().toString();home();});filters.addView(fav);if(!discoverCategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverFavorites=false;discoverPreset="";home();});filters.addView(clear);}root.addView(filters);spacer(5);
    HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout quick=hbox();String[][] goals={{"Write","rewrite writing"},{"Research","research verify explain"},{"Plan","plan organize decision"},{"Learn","learn explain study"},{"Code","code debug technical"},{"Images","image photo edit"}};for(String[] g:goals){Button b=filterChip(g[0],false);b.setOnClickListener(v->{q.setText(g[1]);q.setSelection(q.length());});quick.addView(b);}hsv.addView(quick);root.addView(hsv);
    LinearLayout results=vbox();root.addView(results);renderDiscoverResults(results,q.getText().toString());q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();renderDiscoverResults(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }''')

# Legacy destinations collapse back into Discover rather than creating more pages.
s=replace_method(s,'  void browseCategories()',r'''  void browseCategories(){page="home";home();showCategoryPicker();}''')
s=replace_method(s,'  void group(Group g,String activeSub,String initialQuery)',r'''  void group(Group g,String activeSub,String initialQuery){discoverCategory=g==null?"":g.title;discoverFavorites=false;discoverPreset=initialQuery==null?"":initialQuery;home();}''')
s=replace_method(s,'  void smartCollection(',r'''  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){discoverCategory="";discoverFavorites=false;discoverPreset=(baseQuery==null?"":baseQuery)+(active==null?"":" "+active);home();}''')
s=replace_method(s,'  void searchPage(String initial,String mode)',r'''  void searchPage(String initial,String mode){discoverCategory="";discoverFavorites="Favorites".equals(mode);discoverPreset=initial==null?"":initial;home();}''')

# Prompt details are overlays, not a third page.
s=replace_method(s,'  void detail(',r'''  void detail(Cmd c,Group g){showPromptDialog(c);}''')

# Custom prompts and settings are overlays, not navigation destinations.
s=replace_method(s,'  void library(boolean favoritesMode)',r'''  void library(boolean favoritesMode){showPromptCollectionDialog(favoritesMode);}''')
s=replace_method(s,'  void settings()',r'''  void settings(){showSimpleSettings();}''')

# Clean, functional second page.
s=replace_method(s,'  void stack()',r'''  void stack(){
    if(context!=null)contextDraft=context.getText().toString();page="stack";base("","",false);LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);TextView sub=text(selected.isEmpty()?"Build a simple multi-step prompt.":selected.size()+" selected prompt"+(selected.size()==1?"":"s"),10,false,MUTED);top.addView(sub,new LinearLayout.LayoutParams(0,dp(30),1));if(!selected.isEmpty()){Button clear=compactControl("Clear");clear.setOnClickListener(v->{selected.clear();stack();});top.addView(clear,new LinearLayout.LayoutParams(dp(58),dp(28)));}root.addView(top);
    if(selected.isEmpty()){LinearLayout empty=surface(true);TextView e=text("Nothing here yet. Add prompts from Discover.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(20),0,dp(20));empty.addView(e);root.addView(empty);Button browse=primary("Discover prompts");browse.setOnClickListener(v->home());root.addView(browse);return;}
    for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView num=text(String.valueOf(i+1),9,true,TERTIARY);num.setGravity(Gravity.CENTER);card.addView(num,new LinearLayout.LayoutParams(dp(22),dp(38)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView t=text(displayTitle(c),12,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(t);TextView d=text(shortDescription(c),9,false,MUTED);d.setSingleLine(true);d.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView more=text("⋯",19,false,TERTIARY);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showStackMenu(v,k));card.addView(more,new LinearLayout.LayoutParams(dp(30),dp(38)));root.addView(card);}
    TextView req=text("Your request",11,true,TEXT);req.setPadding(0,dp(6),0,dp(4));root.addView(req);context=input("Paste text or describe what you want the stack to work on...",3);context.setMaxLines(6);context.setText(contextDraft);root.addView(context);Button add=secondary("＋  Add another prompt");add.setOnClickListener(v->{contextDraft=context.getText().toString();home();});root.addView(add);Button run=primary("Run with ChatGPT");run.setOnClickListener(v->{contextDraft=context.getText().toString();build();});root.addView(run);
  }''')

# Back from Stack returns to Discover. Dialogs handle their own back behavior.
s=replace_method(s,'  @Override public void onBackPressed()',r'''  @Override public void onBackPressed(){if("stack".equals(page)){home();return;}super.onBackPressed();}''')

# Version bump for the architecture reset.
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 28',g,count=1);g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.1'",g,count=1);GRADLE.write_text(g,encoding='utf-8')

checks=['What do you want to do?','Discover','Stack (','void showCategoryPicker()','void showMoreMenu()','void showPromptDialog(Cmd c)','void renderDiscoverResults','No custom prompts yet.','Run with ChatGPT']
for x in checks:
    if x not in s:raise SystemExit('two-page gate missing: '+x)
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v0.8.1 two-page UI v5 applied')
