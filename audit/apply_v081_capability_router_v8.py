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


def replace_visible_calls(s,marker):
    a,b=method_span(s,marker);block=s[a:b]
    block=block.replace('displayTitle(c)','presentationTitleV8(c)').replace('shortDescription(c)','presentationOutcomeV8(c)')
    return s[:a]+block+s[b:]

s=JAVA.read_text(encoding='utf-8')
if 'fastSmartScore(Cmd c,String[] toks)' not in s: raise SystemExit('v7 stability layer missing')
if 'String discoverMode="landing";' not in s: raise SystemExit('hybrid state missing')

state='String discoverMode="landing"; String askGoal=""; int browseLimit=30;'
if state in s:s=s.replace(state,'String discoverMode="landing"; String askGoal=""; String askCapability=""; int browseLimit=30;',1)
elif 'String askCapability="";' not in s:raise SystemExit('ask capability state anchor missing')

helpers=r'''  boolean longTokenV8(String x){if(x==null)return false;for(String w:x.split("\\s+"))if(w.length()>20)return true;return false;}
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
  View capabilityTileV8(String id,Runnable action){LinearLayout card=surface(true);card.setPadding(dp(11),dp(10),dp(11),dp(10));card.setMinHeight(dp(68));card.addView(text(CapabilityRouter.label(id),12,true,TEXT));TextView sub=text(CapabilityRouter.outcome(id),9,false,MUTED);sub.setMaxLines(2);sub.setEllipsize(android.text.TextUtils.TruncateAt.END);card.addView(sub);card.setOnClickListener(v->action.run());return card;}
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
  View bestCapabilityCardV8(Cmd c,String goal){LinearLayout card=surface(true);card.setPadding(dp(12),dp(11),dp(12),dp(11));LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);row.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(presentationTitleV8(c),14,true,TEXT));TextView d=text(presentationOutcomeV8(c),10,false,MUTED);d.setMaxLines(2);copy.addView(d);row.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(row);Button use=primary(selected.contains(c)?"Added":"Use this prompt");use.setEnabled(!selected.contains(c));use.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});card.addView(use);return card;}
  void renderCapabilityRecommendationV8(LinearLayout target,String goal,String cap){
    target.removeAllViews();TextView eyebrow=text(CapabilityRouter.label(cap).toUpperCase(Locale.ROOT),10,true,TERTIARY);eyebrow.setLetterSpacing(.10f);eyebrow.setPadding(0,dp(10),0,dp(3));target.addView(eyebrow);TextView why=text(CapabilityRouter.outcome(cap),10,false,MUTED);why.setPadding(0,0,0,dp(7));target.addView(why);ArrayList<Cmd> ranked=rankCapabilityV8(cap,goal,8);if(ranked.isEmpty()){LinearLayout e=surface(true);TextView t=text("No curated prompt is strong enough for this capability yet. Try Browse prompts.",11,false,MUTED);t.setPadding(0,dp(10),0,dp(10));e.addView(t);target.addView(e);return;}Cmd first=ranked.get(0);TextView best=text("BEST MATCH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(4),0,dp(5));target.addView(best);target.addView(bestCapabilityCardV8(first,goal));if(ranked.size()>1){TextView more=text("ALTERNATIVES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(9),0,dp(5));target.addView(more);for(int i=1;i<Math.min(4,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}}Button back=secondary("←  Choose another capability");back.setOnClickListener(v->{askCapability="";CapabilityRouter.Route route=CapabilityRouter.route(goal);if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode))renderImageModeChooserV8(target,goal);else renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(back);
  }
  void renderCompoundWorkflowV8(LinearLayout target,String goal,CapabilityRouter.Route route){
    target.removeAllViews();ArrayList<Cmd> flow=new ArrayList<>();for(String cap:route.capabilities){ArrayList<Cmd> r=rankCapabilityV8(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0)))flow.add(r.get(0));if(flow.size()>=4)break;}if(flow.size()<2){renderCapabilityRecommendationV8(target,goal,route.capabilities.get(0));return;}TextView h=text("SUGGESTED WORKFLOW",10,true,TERTIARY);h.setLetterSpacing(.10f);h.setPadding(0,dp(10),0,dp(5));target.addView(h);target.addView(workflowCard(flow,goal));TextView meta=text("Built from "+flow.size()+" different capabilities — not duplicate search matches.",9,false,MUTED);meta.setPadding(0,dp(4),0,dp(8));target.addView(meta);for(String cap:route.capabilities){TextView ch=text(CapabilityRouter.label(cap),11,true,TEXT);ch.setPadding(0,dp(5),0,dp(3));target.addView(ch);for(Cmd c:rankCapabilityV8(cap,goal,2)){View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}}
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

'''
if 'void renderAskResultsV8(' not in s:s=insert_before(s,'  void renderAskResults(',helpers)

s=replace_method(s,'  void renderAskResults(',r'''  void renderAskResults(LinearLayout target,String goal){renderAskResultsV8(target,goal);}''')
s=replace_method(s,'  void runAskRecommendation(',r'''  void runAskRecommendation(LinearLayout target,EditText goal){String next=goal.getText().toString().trim();if(next.length()<2){toast("Describe what you want first");return;}if(!next.equals(askGoal))askCapability="";askGoal=next;contextDraft=askGoal;hideKeyboard(goal);try{renderAskResultsV8(target,askGoal);}catch(Exception e){target.removeAllViews();LinearLayout box=surface(true);TextView title=text("Couldn't build a recommendation",12,true,TEXT);TextView sub=text("Try a more specific description, or switch to Browse prompts.",10,false,MUTED);title.setPadding(0,dp(8),0,dp(2));sub.setPadding(0,0,0,dp(8));box.addView(title);box.addView(sub);target.addView(box);}}''')

for marker in ['  View commandRow(','  View bestMatchCard(','  View workflowCard(','  void showPromptDialog(','  void showStackSheet()']:
    try:s=replace_visible_calls(s,marker)
    except SystemExit:pass

s=s.replace('discoverMode="browse";discoverPreset="";browseLimit=30;home();','discoverMode="browse";askCapability="";discoverPreset="";browseLimit=30;home();')
s=s.replace('discoverMode="ask";discoverPreset="";browseLimit=30;home();','discoverMode="ask";askCapability="";discoverPreset="";browseLimit=30;home();')

g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 31',g,count=1);GRADLE.write_text(g,encoding='utf-8')

required=['CapabilityRouter.route(q)','void renderCapabilityChooserV8','void renderImageModeChooserV8','ArrayList<Cmd> rankCapabilityV8','void renderCapabilityRecommendationV8','void renderCompoundWorkflowV8','presentationTitleV8(Cmd c)','presentationOutcomeV8(Cmd c)','versionCode 31']
for token in required:
    hay=s if token!='versionCode 31' else g
    if token not in hay:raise SystemExit('v8 capability-router gate missing: '+token)
if 'c.id>=50000&&c.id<50200' not in s:raise SystemExit('curated image family gate missing')
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck capability router v8 applied: domain -> capability -> family -> prompt')
