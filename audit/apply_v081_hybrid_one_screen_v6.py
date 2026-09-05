#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
RES=Path('android/app/src/main/res/drawable')


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

# v6 final IA: one main workspace with two explicit paths.
# Ask PromptDeck = intelligent routing. Browse = manual library access.
# Stack and detail are contextual sheets, never navigation destinations.
if 'String discoverMode="landing";' not in s:
    anchor='String discoverCategory=""; boolean discoverFavorites=false; String discoverPreset="";'
    if anchor not in s: raise SystemExit('v5 discovery state missing')
    s=s.replace(anchor,anchor+' String discoverMode="landing"; String askGoal=""; int browseLimit=30;',1)

# Generate dedicated vector assets for the two entry modes.
RES.mkdir(parents=True,exist_ok=True)
(RES/'pd_mode_ask.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#58A6FF" android:pathData="M12,2l1.5,4.5L18,8l-4.5,1.5L12,14l-1.5,-4.5L6,8l4.5,-1.5zM18.5,13l0.9,2.6L22,16.5l-2.6,0.9L18.5,20l-0.9,-2.6L15,16.5l2.6,-0.9zM5.5,14l0.8,2.2L8.5,17l-2.2,0.8L5.5,20l-0.8,-2.2L2.5,17l2.2,-0.8z"/></vector>''',encoding='utf-8')
(RES/'pd_mode_browse.xml').write_text('''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="#A6B5C8" android:pathData="M4,4h6v6H4zM14,4h6v6h-6zM4,14h6v6H4zM14,14h6v6h-6z"/></vector>''',encoding='utf-8')

helpers=r'''  View modeChoiceCard(int iconRes,String title,String sub,int accent,Runnable action){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(13),dp(12),dp(12),dp(12));card.setBackground(tintedCard(accent,16));ImageView icon=vectorTile(iconRes,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(46),dp(46));ip.setMargins(0,0,dp(12),0);card.addView(icon,ip);LinearLayout copy=vbox();copy.addView(text(title,15,true,TEXT));TextView d=text(sub,10,false,MUTED);d.setMaxLines(2);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView arrow=text("›",24,false,TERTIARY);arrow.setGravity(Gravity.CENTER);card.addView(arrow,new LinearLayout.LayoutParams(dp(28),dp(46)));card.setOnClickListener(v->action.run());return card;
  }
  LinearLayout modeSwitch(){
    LinearLayout seg=hbox();Button ask=filterChip("Ask PromptDeck","ask".equals(discoverMode)),browse=filterChip("Browse prompts","browse".equals(discoverMode));ask.setOnClickListener(v->{discoverMode="ask";discoverPreset="";browseLimit=30;home();});browse.setOnClickListener(v->{discoverMode="browse";discoverPreset="";browseLimit=30;home();});LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(36),1);a.setMargins(0,0,dp(6),0);seg.addView(ask,a);seg.addView(browse,new LinearLayout.LayoutParams(0,dp(36),1));return seg;
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
    LinearLayout card=surface(true);card.setPadding(dp(12),dp(11),dp(12),dp(11));LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);row.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),14,true,TEXT));TextView d=text(shortDescription(c),10,false,MUTED);d.setMaxLines(2);copy.addView(d);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(row);Button use=primary(selected.contains(c)?"Added":"Use this prompt");use.setEnabled(!selected.contains(c));use.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});card.addView(use);return card;
  }
  View workflowCard(ArrayList<Cmd> flow,String goal){
    LinearLayout card=surface(true);card.setPadding(dp(12),dp(10),dp(12),dp(10));TextView meta=text(flow.size()+"-step workflow",10,true,ACCENT);meta.setPadding(0,0,0,dp(5));card.addView(meta);for(int i=0;i<flow.size();i++){Cmd c=flow.get(i);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(String.valueOf(i+1),9,true,TERTIARY);n.setGravity(Gravity.CENTER);row.addView(n,new LinearLayout.LayoutParams(dp(24),dp(30)));TextView t=text(displayTitle(c),11,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);row.addView(t,new LinearLayout.LayoutParams(0,dp(30),1));card.addView(row);}Button use=secondary("Use workflow");use.setOnClickListener(v->{for(Cmd c:flow)if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});card.addView(use);return card;
  }
  void renderAskResults(LinearLayout target,String goal){
    target.removeAllViews();String q=goal==null?"":goal.trim();if(q.isEmpty())return;ArrayList<Cmd> ranked=rankSmart(q,12);if(ranked.isEmpty()){LinearLayout e=surface(true);TextView t=text("I couldn't find a strong match. Try describing the outcome in a little more detail.",11,false,MUTED);t.setPadding(0,dp(10),0,dp(10));e.addView(t);target.addView(e);return;}TextView best=text("BEST APPROACH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(dp(1),dp(12),0,dp(5));target.addView(best);Cmd first=ranked.get(0);target.addView(bestMatchCard(first,q));ArrayList<Cmd> flow=workflowForGoal(q);if(flow.size()>=2){TextView wh=text("SUGGESTED WORKFLOW",10,true,TERTIARY);wh.setLetterSpacing(.10f);wh.setPadding(dp(1),dp(9),0,dp(5));target.addView(wh);target.addView(workflowCard(flow,q));}TextView more=text("MORE MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(dp(1),dp(10),0,dp(5));target.addView(more);int shown=0;for(Cmd c:ranked){if(c==first||flow.contains(c))continue;View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);if(++shown>=3)break;}
  }
  void renderBrowseResultsV6(LinearLayout target,String query){
    target.removeAllViews();String q=query==null?"":query.trim();ArrayList<Cmd> rows=new ArrayList<>();if(q.isEmpty()){if(discoverFavorites){for(Cmd c:all)if(isFavorite(c))rows.add(c);}else if(!discoverCategory.isEmpty()){Group g=groupByTitle(discoverCategory);if(g!=null)rows.addAll(groupCommands(g));}else for(Cmd c:all)if(!c.custom)rows.add(c);}else{for(Cmd c:rankSmart(q,250)){if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;rows.add(c);}}
    TextView meta=text((discoverFavorites?"Favorites":discoverCategory.isEmpty()?"All prompts":discoverCategory)+"  ·  "+rows.size(),10,true,TERTIARY);meta.setPadding(dp(1),dp(9),0,dp(5));target.addView(meta);if(rows.isEmpty()){LinearLayout e=surface(true);TextView t=text("No prompts match this view.",11,false,MUTED);t.setGravity(Gravity.CENTER);t.setPadding(0,dp(15),0,dp(15));e.addView(t);target.addView(e);return;}int limit=Math.min(browseLimit,rows.size());for(int i=0;i<limit;i++){Cmd c=rows.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}if(limit<rows.size()){Button more=secondary("Show more  ("+(rows.size()-limit)+" remaining)");more.setOnClickListener(v->{browseLimit+=30;home();});target.addView(more);}
  }
  void showStackSheetMenu(View anchor,int index,android.app.Dialog sheet){
    PopupMenu p=new PopupMenu(this,anchor);if(index>0)p.getMenu().add("Move up");if(index<selected.size()-1)p.getMenu().add("Move down");p.getMenu().add("Remove");p.setOnMenuItemClickListener(item->{String t=item.getTitle().toString();if(t.equals("Move up")&&index>0)Collections.swap(selected,index,index-1);else if(t.equals("Move down")&&index<selected.size()-1)Collections.swap(selected,index,index+1);else if(t.equals("Remove"))selected.remove(index);sheet.dismiss();home();if(!selected.isEmpty())showStackSheet();return true;});p.show();
  }
  void showStackSheet(){
    if(selected.isEmpty()){toast("Choose a prompt first");return;}android.app.Dialog sheet=new android.app.Dialog(this);LinearLayout outer=vbox();outer.setPadding(dp(16),dp(12),dp(16),dp(16));outer.setBackground(shape(SURFACE,BORDER,24));LinearLayout head=hbox();head.setGravity(Gravity.CENTER_VERTICAL);LinearLayout hc=vbox();hc.addView(text("Review & Run",19,true,TEXT));hc.addView(text(selected.size()+" selected prompt"+(selected.size()==1?"":"s"),10,false,MUTED));head.addView(hc,new LinearLayout.LayoutParams(0,-2,1));TextView close=text("×",24,false,MUTED);close.setGravity(Gravity.CENTER);close.setOnClickListener(v->sheet.dismiss());head.addView(close,new LinearLayout.LayoutParams(dp(38),dp(38)));outer.addView(head);ScrollView scroll=new ScrollView(this);LinearLayout list=vbox();for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout row=surface(true);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(8),dp(6),dp(7),dp(6));TextView num=text(String.valueOf(i+1),9,true,TERTIARY);num.setGravity(Gravity.CENTER);row.addView(num,new LinearLayout.LayoutParams(dp(22),dp(38)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);row.addView(ic,ip);LinearLayout copy=vbox();TextView tt=text(displayTitle(c),12,true,TEXT);tt.setSingleLine(true);tt.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(tt);TextView dd=text(shortDescription(c),9,false,MUTED);dd.setSingleLine(true);dd.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(dd);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView menu=text("⋯",19,false,TERTIARY);menu.setGravity(Gravity.CENTER);menu.setOnClickListener(v->showStackSheetMenu(v,k,sheet));row.addView(menu,new LinearLayout.LayoutParams(dp(30),dp(38)));list.addView(row);}scroll.addView(list);outer.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));TextView lab=text("Your request",11,true,TEXT);lab.setPadding(0,dp(8),0,dp(4));outer.addView(lab);EditText req=input("Paste text or describe what you want ChatGPT to work on...",3);req.setMaxLines(5);req.setText(contextDraft);outer.addView(req);LinearLayout actions=hbox();Button add=secondary("Add prompt");add.setOnClickListener(v->{contextDraft=req.getText().toString();sheet.dismiss();discoverMode="browse";home();});Button run=primary("Run with ChatGPT");run.setOnClickListener(v->{contextDraft=req.getText().toString();sheet.dismiss();build();});actions.addView(add,new LinearLayout.LayoutParams(0,dp(44),1));Space gap=new Space(this);actions.addView(gap,new LinearLayout.LayoutParams(dp(8),1));actions.addView(run,new LinearLayout.LayoutParams(0,dp(44),1));outer.addView(actions);sheet.setContentView(outer);sheet.show();android.view.Window w=sheet.getWindow();if(w!=null){w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));w.setGravity(Gravity.BOTTOM);w.setLayout(-1,(int)(getResources().getDisplayMetrics().heightPixels*.86f));w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);android.view.WindowManager.LayoutParams lp=w.getAttributes();lp.dimAmount=.55f;w.setAttributes(lp);}
  }

'''
if 'View modeChoiceCard(' not in s:
    s=insert_before(s,'  void showCategoryPicker(){',helpers)

# Category picker must keep the user in manual Browse mode.
s=replace_method(s,'  void showCategoryPicker()',r'''  void showCategoryPicker(){String[] names=new String[groups.length+1];names[0]="All categories";for(int i=0;i<groups.length;i++)names[i+1]=groups[i].title+"  ("+groupCount(groups[i])+")";new AlertDialog.Builder(this).setTitle("Choose category").setItems(names,(d,which)->{discoverMode="browse";discoverCategory=which==0?"":groups[which-1].title;discoverFavorites=false;discoverPreset="";browseLimit=30;home();}).setNegativeButton("Cancel",null).show();}''')

# One-screen shell. No persistent bottom navigation.
s=replace_method(s,'  void base(',r'''  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);root=vbox();root.setPadding(dp(14),dp(8),dp(14),dp(18));sv.addView(root);shell.addView(sv,new LinearLayout.LayoutParams(-1,0,1));if(!selected.isEmpty())shell.addView(selectionBar(),new LinearLayout.LayoutParams(-1,dp(56)));setContentView(shell);sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();if(top>0)root.setPadding(dp(14),Math.max(dp(8),top+dp(3)),dp(14),dp(18));return insets;});LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);ImageView mark=new ImageView(this);mark.setImageResource(R.drawable.promptdeck_mark);mark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(dp(30),dp(30));mp.setMargins(0,0,dp(7),0);top.addView(mark,mp);top.addView(text("PromptDeck",18,true,TEXT),new LinearLayout.LayoutParams(0,dp(32),1));TextView more=text("⋯",24,true,TEXT);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showMoreMenu());top.addView(more,new LinearLayout.LayoutParams(dp(38),dp(36)));root.addView(top);spacer(9);
  }''')

# Prompt rows become simple: row opens detail, + is the only inline action.
s=replace_method(s,'  View commandRow(',r'''  View commandRow(Cmd c,boolean divider){LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(9),dp(7),dp(8),dp(7));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(36),dp(36));ip.setMargins(0,0,dp(9),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView t=text(displayTitle(c),13,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(t);TextView d=text(shortDescription(c),9,false,MUTED);d.setSingleLine(true);d.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView add=text(selected.contains(c)?"✓":"＋",18,true,selected.contains(c)?SUCCESS:ACCENT);add.setGravity(Gravity.CENTER);add.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added");home();}});card.addView(add,new LinearLayout.LayoutParams(dp(34),dp(36)));return card;}''')

# Upgraded prompt detail as a contextual sheet rather than a navigation page.
s=replace_method(s,'  void showPromptDialog(Cmd c)',r'''  void showPromptDialog(Cmd c){android.app.Dialog sheet=new android.app.Dialog(this);LinearLayout outer=vbox();outer.setPadding(dp(16),dp(12),dp(16),dp(16));outer.setBackground(shape(SURFACE,BORDER,24));LinearLayout head=hbox();head.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(42),dp(42));ip.setMargins(0,0,dp(10),0);head.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),16,true,TEXT));copy.addView(text(shortDescription(c),10,false,MUTED));head.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView close=text("×",23,false,MUTED);close.setGravity(Gravity.CENTER);close.setOnClickListener(v->sheet.dismiss());head.addView(close,new LinearLayout.LayoutParams(dp(38),dp(38)));outer.addView(head);ScrollView scroll=new ScrollView(this);LinearLayout content=vbox();String body=c.instruction==null?"":c.instruction.trim();if(body.length()>1400)body=body.substring(0,1397).trim()+"…";TextView prompt=text(body,11,false,TEXT);prompt.setLineSpacing(dp(1),1.10f);prompt.setPadding(0,dp(10),0,dp(8));content.addView(prompt);ArrayList<String> vars=templateVariables(c.instruction);for(String key:vars){TextView l=text(prettyKey(key),10,true,MUTED);l.setPadding(0,dp(5),0,dp(3));content.addView(l);EditText field=input("Enter "+prettyKey(key).toLowerCase(Locale.ROOT),1);field.setText(promptVar(c.id,key));field.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int co,int a){}public void onTextChanged(CharSequence x,int st,int b,int co){setPromptVar(c.id,key,x.toString());}public void afterTextChanged(android.text.Editable e){}});content.addView(field);}Button fav=secondary(isFavorite(c)?"★  Favorited":"☆  Favorite");fav.setOnClickListener(v->{toggleFavorite(c);fav.setText(isFavorite(c)?"★  Favorited":"☆  Favorite");});content.addView(fav);scroll.addView(content);outer.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));LinearLayout actions=hbox();Button run=secondary("Run now");run.setOnClickListener(v->{sheet.dismiss();sendText(buildSinglePrompt(c,"ask".equals(discoverMode)?askGoal:""));});Button add=primary(selected.contains(c)?"Added":"Add to Stack");add.setEnabled(!selected.contains(c));add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);sheet.dismiss();home();});actions.addView(run,new LinearLayout.LayoutParams(0,dp(44),1));Space gap=new Space(this);actions.addView(gap,new LinearLayout.LayoutParams(dp(8),1));actions.addView(add,new LinearLayout.LayoutParams(0,dp(44),1));outer.addView(actions);sheet.setContentView(outer);sheet.show();android.view.Window w=sheet.getWindow();if(w!=null){w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));w.setGravity(Gravity.BOTTOM);w.setLayout(-1,(int)(getResources().getDisplayMetrics().heightPixels*.78f));w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);android.view.WindowManager.LayoutParams lp=w.getAttributes();lp.dimAmount=.5f;w.setAttributes(lp);}}''')

# Final main workspace: landing -> Ask or Browse. Same page, no navigation hierarchy.
s=replace_method(s,'  void home()',r'''  void home(){
    page="home";currentGroup=null;base("","",false);
    if("landing".equals(discoverMode)){TextView h=text("How do you want to start?",23,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Let PromptDeck choose the best approach, or explore all prompts yourself.",11,false,MUTED);sub.setPadding(0,0,0,dp(10));root.addView(sub);View ask=modeChoiceCard(R.drawable.pd_mode_ask,"Ask PromptDeck","Describe your goal and get the best prompt or workflow automatically.",ACCENT,()->{discoverMode="ask";home();});root.addView(ask);View browse=modeChoiceCard(R.drawable.pd_mode_browse,"Browse all prompts","Search and explore the complete 3,375-prompt library yourself.",Color.rgb(45,203,140),()->{discoverMode="browse";home();});root.addView(browse);TextView hint=text("You can switch modes anytime. Your selected prompts stay in your workflow.",9,false,TERTIARY);hint.setGravity(Gravity.CENTER);hint.setPadding(dp(6),dp(10),dp(6),0);root.addView(hint);return;}
    root.addView(modeSwitch());spacer(8);
    if("ask".equals(discoverMode)){TextView h=text("What do you want ChatGPT to help you do?",20,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Describe the outcome. PromptDeck will choose the strongest prompt or build a short workflow.",10,false,MUTED);sub.setPadding(0,0,0,dp(8));root.addView(sub);EditText goal=input("e.g. Compare two cars and recommend the better one for me...",3);goal.setMaxLines(5);goal.setText(askGoal);root.addView(goal);Button find=primary("Find the best approach");root.addView(find);HorizontalScrollView examples=new HorizontalScrollView(this);examples.setHorizontalScrollBarEnabled(false);LinearLayout ex=hbox();String[] xs={"Compare options","Write an email","Plan a project","Explain a topic"};for(String x:xs){Button b=filterChip(x,false);b.setOnClickListener(v->{goal.setText(x);goal.setSelection(goal.length());});ex.addView(b);}examples.addView(ex);root.addView(examples);LinearLayout results=vbox();root.addView(results);if(!askGoal.isEmpty())renderAskResults(results,askGoal);find.setOnClickListener(v->{askGoal=goal.getText().toString().trim();contextDraft=askGoal;renderAskResults(results,askGoal);});return;}
    TextView h=text("Browse all prompts",20,true,TEXT);h.setPadding(0,0,0,dp(3));root.addView(h);TextView sub=text("Search directly, or narrow the full library by category.",10,false,MUTED);sub.setPadding(0,0,0,dp(7));root.addView(sub);EditText q=input("Search prompts...",1);q.setSingleLine(true);q.setText(discoverPreset);root.addView(q);LinearLayout filters=hbox();Button cat=filterChip(discoverCategory.isEmpty()?"All categories":discoverCategory,false);cat.setOnClickListener(v->showCategoryPicker());filters.addView(cat);Button fav=filterChip("Favorites",discoverFavorites);fav.setOnClickListener(v->{discoverFavorites=!discoverFavorites;discoverCategory="";discoverPreset=q.getText().toString();browseLimit=30;home();});filters.addView(fav);if(!discoverCategory.isEmpty()||discoverFavorites){Button clear=filterChip("Clear",false);clear.setOnClickListener(v->{discoverCategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();});filters.addView(clear);}root.addView(filters);LinearLayout results=vbox();root.addView(results);renderBrowseResultsV6(results,q.getText().toString());q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();browseLimit=30;renderBrowseResultsV6(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }''')

# Legacy stack entry becomes the contextual sheet only.
s=replace_method(s,'  void stack()',r'''  void stack(){showStackSheet();}''')

# Stack composer now sends directly; no hidden third/final page.
s=replace_method(s,'  void build()',r'''  void build(){if(selected.isEmpty()){toast("Choose at least one prompt");return;}String user=contextDraft==null?"":contextDraft.trim();StringBuilder p=new StringBuilder();p.append("Use the user's request/context as the source of truth.\n\n");if(!user.isEmpty())p.append("USER REQUEST / CONTEXT:\n").append(user).append("\n\n");p.append("SELECTED PROMPT MODULES:\n");for(int i=0;i<selected.size();i++){Cmd c=selected.get(i);p.append("\nSTEP ").append(i+1).append(" — ").append(displayTitle(c)).append("\n").append(resolveTemplate(c,user)).append("\n");}p.append("\nEXECUTION RULES:\n- Apply the selected modules in order, carrying forward only useful findings from earlier steps.\n- Each module is scoped to its step and must not override or block later modules.\n- Use ChatGPT tools only when helpful and actually available.\n- If one essential input is missing and cannot be inferred, ask one concise clarifying question; otherwise make reasonable assumptions.\n- Give one coherent final answer. Do not expose private chain-of-thought; provide concise rationale, evidence or verification where useful.");sendText(p.toString());}''')

# Old destinations collapse to the single workspace.
s=replace_method(s,'  void browseCategories()',r'''  void browseCategories(){discoverMode="browse";home();}''')
s=replace_method(s,'  void group(Group g,String activeSub,String initialQuery)',r'''  void group(Group g,String activeSub,String initialQuery){discoverMode="browse";discoverCategory=g==null?"":g.title;discoverPreset=initialQuery==null?"":initialQuery;browseLimit=30;home();}''')
s=replace_method(s,'  void searchPage(String initial,String mode)',r'''  void searchPage(String initial,String mode){discoverMode="browse";discoverPreset=initial==null?"":initial;discoverFavorites="Favorites".equals(mode);browseLimit=30;home();}''')
s=replace_method(s,'  void smartCollection(',r'''  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){discoverMode="ask";askGoal=(baseQuery==null?"":baseQuery)+(active==null?"":" "+active);home();}''')
s=replace_method(s,'  void detail(',r'''  void detail(Cmd c,Group g){showPromptDialog(c);}''')

# Back from an old internal destination always returns to the one main workspace.
s=replace_method(s,'  @Override public void onBackPressed()',r'''  @Override public void onBackPressed(){if(!"home".equals(page)){page="home";home();return;}super.onBackPressed();}''')

# Version bump.
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 29',g,count=1);g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.1'",g,count=1);GRADLE.write_text(g,encoding='utf-8')

# v6 architecture gates.
required=['How do you want to start?','Ask PromptDeck','Browse all prompts','Find the best approach','BEST APPROACH','SUGGESTED WORKFLOW','View selectionBar()','void showStackSheet()','Review & Run','void renderBrowseResultsV6','workflowForGoal(String goal)','R.drawable.pd_mode_ask','R.drawable.pd_mode_browse']
for token in required:
    if token not in s: raise SystemExit('v6 gate missing: '+token)
base=s[method_span(s,'  void base(')[0]:method_span(s,'  void base(')[1]]
if 'bottomNav()' in base: raise SystemExit('persistent bottom nav still attached')
stack=s[method_span(s,'  void stack()')[0]:method_span(s,'  void stack()')[1]]
if 'showStackSheet();' not in stack: raise SystemExit('stack is still a page')
JAVA.write_text(s,encoding='utf-8')
print('Hybrid one-screen v6 applied: Ask PromptDeck + Browse + contextual Review & Run')
