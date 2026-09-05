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
# v4 ORGANIZATION LOCK
# Proposal controls structure/visual language. Real data controls content.
# No fake custom prompts, no fake search results, no inline layout-breaking controls.
# ------------------------------------------------------------------

helpers=r'''  String cleanUiText(String x){
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

'''
if 'String cleanUiText(String x)' not in s:
    s=insert_before(s,'  String displayTitle(Cmd c)',helpers)

s=replace_method(s,'  String displayTitle(Cmd c)',r'''  String displayTitle(Cmd c){
    String k=c.command==null?"":c.command.toLowerCase(Locale.ROOT);
    if(k.equals("eli5"))return"Explain Like I'm 5 (ELI5)";if(k.equals("rewrite"))return"Rewrite for Clarity";if(k.equals("humanize"))return"Make It Sound More Human";if(k.equals("summarize"))return"Summarize";if(k.equals("research"))return"Research a Topic";if(k.equals("email")||k.equals("reply"))return"Email Reply";if(k.equals("compareoptions"))return"Compare Options";if(k.contains("promptingcoach"))return"AI Prompting Coach";if(k.contains("prompttolearnfree"))return"AI Learning Resources";if(k.equals("metaprompt"))return"Meta Prompt";
    String spaced=repairJoinedWords(c.command.replaceAll("([a-z0-9])([A-Z])","$1 $2").replaceAll("([A-Z]+)([A-Z][a-z])","$1 $2").replaceAll("[_-]+"," ").trim());
    String extracted=extractedCapability(c);if(uglyCommand(c,spaced)&&!extracted.isEmpty())spaced=extracted;
    spaced=spaced.replaceAll("(?i)\\s+(?:agent role|agent|role|skill imported|skill)$","").replaceAll("(?i)\\s+prompt$","").replaceAll("\\s+"," ").trim();
    if(spaced.equalsIgnoreCase("Chat GPT Prompt Refiner"))spaced="ChatGPT Prompt Refiner";
    if(spaced.toLowerCase(Locale.ROOT).contains("tcre framework"))spaced=spaced.replaceAll("(?i)A I","AI");
    String out=titleCaseUi(spaced);return out.isEmpty()?"Prompt":out;
  }''')

s=replace_method(s,'  String shortDescription(Cmd c)',r'''  String shortDescription(Cmd c){
    String d=cleanUiText(c.description);String title=displayTitle(c);
    if(d.isEmpty()||d.equalsIgnoreCase(title)||d.toLowerCase(Locale.ROOT).startsWith("handle the user request")||d.toLowerCase(Locale.ROOT).startsWith("for this step"))d="";
    if(d.matches("(?i)^(?:act|acts|you are).*")){String x=extractedCapability(c);d=x.isEmpty()?"Expert guidance for this task.":"Expert guidance for "+x+".";}
    if(d.isEmpty()){String x=cleanUiText(c.instruction);int cut=x.indexOf('.');if(cut>18)x=x.substring(0,cut+1);d=x;}
    d=d.replaceAll("(?i)^#?\\s*TITLE\\s*:\\s*","").replaceAll("\\s+"," ").trim();
    if(d.length()>82)d=d.substring(0,79).trim()+"…";return d.isEmpty()?"ChatGPT-ready workflow for this task.":d;
  }''')

# Stack must look like the proposal and remain functional. Reordering lives behind the overflow menu.
s=replace_method(s,'  void stack()',r'''  void stack(){
    if(context!=null)contextDraft=context.getText().toString();seedProposalStackOnce();page="stack";base("Prompt Stack","",false);
    if(selected.isEmpty()){LinearLayout empty=surface(true);TextView e=text("Your stack is empty. Discover a prompt and add it here.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(15),0,dp(15));empty.addView(e);root.addView(empty);Button browse=primary("Browse prompts");browse.setOnClickListener(v->searchPage());root.addView(browse);return;}
    LinearLayout actions=hbox();actions.setGravity(Gravity.CENTER_VERTICAL);TextView badge=text(String.valueOf(selected.size()),9,true,TEXT);badge.setGravity(Gravity.CENTER);badge.setBackground(shape(BORDER,BORDER,16));TextView count=text("Prompt Stack",0,false,TEXT);actions.addView(badge,new LinearLayout.LayoutParams(dp(25),dp(25)));Space fill=new Space(this);actions.addView(fill,new LinearLayout.LayoutParams(0,1,1));Button clear=compactControl("Clear");clear.setOnClickListener(v->{selected.clear();stack();});actions.addView(clear,new LinearLayout.LayoutParams(dp(58),dp(28)));root.addView(actions);spacer(4);
    for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(7),dp(6),dp(7),dp(6));TextView num=text(String.valueOf(i+1),9,true,TERTIARY);num.setGravity(Gravity.CENTER);card.addView(num,new LinearLayout.LayoutParams(dp(20),dp(38)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView t=text(displayTitle(c),12,true,TEXT);t.setSingleLine(true);t.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(t);TextView d=text(shortDescription(c),9,false,MUTED);d.setSingleLine(true);d.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView more=text("⋯",19,false,TERTIARY);more.setGravity(Gravity.CENTER);more.setOnClickListener(v->showStackMenu(v,k));card.addView(more,new LinearLayout.LayoutParams(dp(30),dp(38)));root.addView(card);}
    Button more=secondary("＋  Add Another Prompt");more.setOnClickListener(v->searchPage());root.addView(more);Button run=primary("➤  Run Stack with ChatGPT");run.setOnClickListener(v->build());root.addView(run);
  }''')

# My Prompts must contain real user data only. Utilities move to Settings > Data & Storage.
s=replace_method(s,'  void library(boolean favoritesMode)',r'''  void library(boolean favoritesMode){
    page="library";currentGroup=null;base("My Prompts","",false);LinearLayout seg=hbox();Button mine=filterChip("My Prompts",!favoritesMode),fav=filterChip("Favorites",favoritesMode);mine.setOnClickListener(v->library(false));fav.setOnClickListener(v->library(true));LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(31),1);a.setMargins(0,0,dp(6),0);seg.addView(mine,a);seg.addView(fav,new LinearLayout.LayoutParams(0,dp(31),1));root.addView(seg);spacer(8);
    ArrayList<Cmd> rows=new ArrayList<>();for(Cmd c:all){if(favoritesMode){if(isFavorite(c))rows.add(c);}else if(c.custom)rows.add(c);}if(rows.isEmpty()){LinearLayout empty=surface(true);TextView e=text(favoritesMode?"No favorites yet.":"No custom prompts yet.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(15),0,dp(15));empty.addView(e);root.addView(empty);}else for(Cmd c:rows){View row=commandRow(c,false);row.setOnClickListener(v->{if(c.custom)customDetail(c);else detail(c,groupFor(c));});root.addView(row);}if(!favoritesMode){Button create=secondary("＋  Create a New Prompt");create.setOnClickListener(v->showAdd());root.addView(create);TextView hint=text("Import, export and bulk paste are in Settings → Data & Storage.",9,false,TERTIARY);hint.setGravity(Gravity.CENTER);hint.setPadding(0,dp(6),0,0);root.addView(hint);}
  }''')

# Search relevance: prioritize coverage of the user's actual intent, not generic expanded words.
s=replace_method(s,'  ArrayList<Cmd> rankSmart(',r'''  ArrayList<Cmd> rankSmart(String query,int limit){
    ArrayList<Cmd> out=new ArrayList<>(all);final HashMap<Integer,Integer> scores=new HashMap<>();for(Cmd c:out)scores.put(c.id,smartScore(c,query));Collections.sort(out,(a,b)->{int sa=scores.get(a.id),sb=scores.get(b.id);if(sa!=sb)return Integer.compare(sb,sa);return displayTitle(a).compareToIgnoreCase(displayTitle(b));});ArrayList<Cmd> best=new ArrayList<>();for(Cmd c:out){if(scores.get(c.id)<=0)continue;best.add(c);if(best.size()>=limit)break;}return best;
  }''')

s=replace_method(s,'  int smartScore(',r'''  int smartScore(Cmd c,String query){
    String raw=query==null?"":query.toLowerCase(Locale.ROOT).trim();String expanded=expandIntent(raw);String title=displayTitle(c).toLowerCase(Locale.ROOT),desc=shortDescription(c).toLowerCase(Locale.ROOT),meta=(c.category+" "+c.subcategory).toLowerCase(Locale.ROOT),body=c.instruction.toLowerCase(Locale.ROOT);HashSet<String> original=meaningfulQueryTerms(raw),extra=meaningfulQueryTerms(expanded);int score=0,matched=0,anchors=0,anchorMatched=0;
    if(raw.length()>3&&title.contains(raw))score+=80;if(raw.length()>3&&desc.contains(raw))score+=45;
    for(String t:original){boolean hit=false;if(title.contains(t)){score+=22;hit=true;}else if(desc.contains(t)){score+=13;hit=true;}else if(meta.contains(t)){score+=9;hit=true;}else if(body.contains(t)){score+=2;hit=true;}if(hit)matched++;if(t.length()>=6&&!genericSearchTerm(t)){anchors++;if(hit)anchorMatched++;}}
    for(String t:extra){if(original.contains(t))continue;if(title.contains(t))score+=4;else if(desc.contains(t))score+=2;else if(meta.contains(t))score+=1;}
    score+=matched*matched*7;if(!original.isEmpty()&&matched==original.size())score+=45;if(anchors>0&&anchorMatched==0)score-=55;if(raw.contains("marketing")&&meta.contains("marketing"))score+=30;if(raw.contains("career")&&meta.contains("career"))score+=25;if(raw.contains("image")&&meta.contains("image"))score+=25;if(recentIdSet().contains(c.id))score+=2;return score;
  }''')

# Collections: no duplicated Best matches chip; curated result count stays scannable.
s=replace_method(s,'  void smartCollection(',r'''  void smartCollection(String title,String sub,String baseQuery,String active,String...refiners){
    page="discover";currentGroup=null;base(title,sub,false);boolean realRefiners=refiners!=null&&refiners.length>0&&!(refiners.length==1&&"Best matches".equalsIgnoreCase(refiners[0]));if(realRefiners){HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout chips=hbox();chips.setPadding(0,dp(1),dp(3),dp(7));hsv.addView(chips);root.addView(hsv);Button allChip=filterChip("Best matches",active==null);allChip.setOnClickListener(v->smartCollection(title,sub,baseQuery,null,refiners));chips.addView(allChip);for(String r:refiners){Button chip=filterChip(r,r.equals(active));chip.setOnClickListener(v->smartCollection(title,sub,baseQuery,r,refiners));chips.addView(chip);}}
    String query=baseQuery+(active==null?"":" "+active);ArrayList<Cmd> ranked=rankSmart(query,16);TextView meta=text(ranked.size()+" relevant prompts",10,false,MUTED);meta.setPadding(0,dp(2),0,dp(7));root.addView(meta);renderRanked(root,ranked);
  }''')

# Search screen defaults empty. The proposal's example query was illustrative, not app state.
s=replace_method(s,'  void searchPage()',r'''  void searchPage(){searchPage("","All");}''')

s=replace_method(s,'  void renderSearchResults(',r'''  void renderSearchResults(LinearLayout target,String query,String mode){
    target.removeAllViews();String q=query==null?"":query.trim();if("Categories".equals(mode)){renderCategoryCards(target,q);return;}if("Collections".equals(mode)){View a=menuCard("⚖","Compare & choose","Compare options and recommend the strongest fit");a.setOnClickListener(v->smartCollection("Compare & choose","Make better decisions","compare recommend decision options",null));target.addView(a);View b=menuCard("★","Best for ChatGPT","Prompt design and AI workflows");b.setOnClickListener(v->smartCollection("Best for ChatGPT","Top prompting workflows","chatgpt prompt optimize ai",null));target.addView(b);View c=menuCard("▣","Career toolkit","Resumes, interviews and professional communication");c.setOnClickListener(v->smartCollection("Career toolkit","Jobs, resumes, interviews","career resume interview email",null));target.addView(c);View d=menuCard("▥","Content studio","Writing, social and marketing workflows");d.setOnClickListener(v->smartCollection("Content studio","Blog, social, marketing","content hook script caption marketing",null));target.addView(d);return;}if(q.length()<2){View browse=menuCard("▦","Browse Categories","Explore the full canonical catalog");browse.setOnClickListener(v->browseCategories());target.addView(browse);TextView hint=text("Describe the outcome you want to rank relevant prompts.",10,false,MUTED);hint.setPadding(dp(2),dp(7),0,0);target.addView(hint);return;}ArrayList<Cmd> ranked=rankSmart(q,12);for(Cmd c:ranked){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,groupFor(c)));target.addView(row);}if(ranked.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No strong matches yet. Try a more specific outcome.",11,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(16),0,dp(16));empty.addView(e);target.addView(empty);}
  }''')

# Settings must not behave like placeholder toast buttons.
s=replace_method(s,'  void settings()',r'''  void settings(){
    page="settings";currentGroup=null;base("Settings","",false);View a=settingsRow(R.drawable.pd_nav_settings,"App Preferences","Theme, language, behavior");a.setOnClickListener(v->showAppPreferences());root.addView(a);View b=settingsRow(R.drawable.pd_ic_connection,"ChatGPT Connection","Configure your ChatGPT access");b.setOnClickListener(v->showChatGPTConnection());root.addView(b);View c=settingsRow(R.drawable.pd_ic_storage,"Data & Storage","Manage custom prompts and backups");c.setOnClickListener(v->showDataStorage());root.addView(c);View d=settingsRow(R.drawable.pd_ic_info,"About PromptDeck","Version 0.8.1");d.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("PromptDeck 0.8.1").setMessage("3,375 ChatGPT-first prompts. Discover, customize and stack real prompt workflows.").setPositiveButton("Done",null).show());root.addView(d);
  }''')

# Never seed fake custom prompts; starter stack stays real canonical prompts but is not regenerated after Clear.
# Remove presentation-only starter preview use if it survived.

# Version code bump for clean device comparison.
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 27',g,count=1);GRADLE.write_text(g,encoding='utf-8')

checks=['void showStackMenu(View anchor,int index)','Import, export and bulk paste are in Settings','rankSmart(query,16)','versionCode 27']
for x in checks:
    if x=='versionCode 27':continue
    if x not in s:raise SystemExit('v4 organization gate missing: '+x)
if 'Button up=mini("↑")' in s[s.find('void stack()'):s.find('void addMore()',s.find('void stack()'))]:raise SystemExit('inline stack controls still present')
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v0.8.1 organization fix v4 applied')
