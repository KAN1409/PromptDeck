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
if 'void beginAskSelectionV10(String goal)' not in s: raise SystemExit('v10 layer missing')
if 'String composeStackPromptV9(String user)' not in s: raise SystemExit('v9 composer missing')

helpers=r'''  String commandWordsV11(Cmd c){
    String x=c==null||c.command==null?"":c.command; x=x.replace('_',' ').replace('-',' ');
    x=x.replaceAll("([a-z0-9])([A-Z])","$1 $2").replaceAll("(?i)\\b(?:prompt|agent|role|skill)\\b"," ").replaceAll("\\s+"," ").trim();
    if(x.isEmpty())return "ChatGPT workflow";StringBuilder out=new StringBuilder();for(String w:x.split(" ")){if(w.isEmpty())continue;if(out.length()>0)out.append(' ');if(w.length()<=3&&w.equals(w.toUpperCase(Locale.ROOT)))out.append(w);else out.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));}return out.toString();
  }
  boolean genericPresentationV11(String x){if(x==null)return true;String z=x.trim().toLowerCase(Locale.ROOT);return z.isEmpty()||z.equals("chatgpt workflow")||z.equals("focused chatgpt workflow for this outcome.")||z.startsWith("ready-to-use chatgpt workflow")||z.startsWith("use the strongest prompt family");}
  String polishedTitleV11(Cmd c){
    String t=safePresentationTitleV10(c);if(genericPresentationV11(t)||uglyPresentationV8(t)||longTokenV8(t)){String d=c.description==null?"":c.description.replaceAll("[{}\\[\\]\\\"<>#]"," ").replaceAll("\\s+"," ").trim();if(d.length()>=4&&d.length()<=62&&!uglyPresentationV8(d)&&!longTokenV8(d))t=d;else t=commandWordsV11(c);}if(t.length()>58)t=t.substring(0,55).trim()+"…";return t;
  }
  String polishedOutcomeV11(Cmd c,String cap){
    String d=safePresentationOutcomeV10(c);if(genericPresentationV11(d)||uglyPresentationV8(d)||longTokenV8(d)){d=(cap==null||cap.isEmpty())?"Focused workflow for this task.":CapabilityRouter.outcome(cap);}if(d.length()>98)d=d.substring(0,95).trim()+"…";return d;
  }
  int qualityPenaltyV11(Cmd c){
    int p=0;String t=polishedTitleV11(c),d=polishedOutcomeV11(c,"");if(t.length()>54)p+=5;if(genericPresentationV11(t))p+=20;if(genericPresentationV11(d))p+=8;if(c.id>=30000&&c.id<50000)p+=3;if(c.id>=60000&&c.id<70000)p+=2;return p;
  }
  int qualityScoreV11(Cmd c,String cap,String query){
    int score=capabilityScoreV8(c,cap,query)-qualityPenaltyV11(c);if(c.id>0&&c.id<10000)score+=10;if(c.id>=70000&&c.id<70100)score+=7;if(imagePromptV8(c)&&c.id>=50000&&c.id<50200)score+=8;String q=CapabilityRouter.norm(query);String hay=(polishedTitleV11(c)+" "+polishedOutcomeV11(c,cap)+" "+c.subcategory+" "+c.command).toLowerCase(Locale.ROOT);for(String w:q.split(" "))if(w.length()>3&&hay.contains(w))score+=5;return score;
  }
  String familyKeyV11(Cmd c,String cap){
    String t=polishedTitleV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9 ]"," ").replaceAll("\\s+"," ").trim();String[] w=t.split(" ");StringBuilder k=new StringBuilder(cap==null?"":cap);int n=0;for(String x:w){if(x.length()<4||x.equals("prompt")||x.equals("chatgpt")||x.equals("workflow"))continue;k.append('|').append(x);if(++n==2)break;}if(n==0)k.append('|').append(c.subcategory==null?"":c.subcategory.toLowerCase(Locale.ROOT));return k.toString();
  }
  ArrayList<Cmd> rankCapabilityV11(String cap,String query,int limit){
    ArrayList<Cmd> pool=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();for(Cmd c:all){int sc=qualityScoreV11(c,cap,query);int floor=cap.startsWith("image.")?38:24;if(sc>=floor){pool.add(c);scores.put(c,sc);}}
    Collections.sort(pool,(a,b)->{int x=scores.get(a),y=scores.get(b);if(x!=y)return Integer.compare(y,x);return polishedTitleV11(a).compareToIgnoreCase(polishedTitleV11(b));});
    ArrayList<Cmd> out=new ArrayList<>();HashSet<String> families=new HashSet<>(),titles=new HashSet<>();for(Cmd c:pool){String title=polishedTitleV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim(),fam=familyKeyV11(c,cap);if(titles.contains(title)||families.contains(fam))continue;titles.add(title);families.add(fam);out.add(c);if(out.size()>=limit)break;}return out;
  }
  String fitReasonV11(String cap,String query){
    String base=CapabilityRouter.outcome(cap);String q=query==null?"":query.trim();if(q.isEmpty())return base;return base+" PromptDeck routed your request to this capability before ranking individual prompts.";
  }
'''
if 'ArrayList<Cmd> rankCapabilityV11(' not in s:
    s=insert_before(s,'  int capabilityCategoryBoostV8(',helpers)

# Ask recommendation becomes capability-first and refuses weak random matches.
s=replace_method(s,'  void renderCapabilityRecommendationV8(',r'''  void renderCapabilityRecommendationV8(LinearLayout target,String goal,String cap){
    target.removeAllViews();TextView eyebrow=text(CapabilityRouter.label(cap).toUpperCase(Locale.ROOT),10,true,TERTIARY);eyebrow.setLetterSpacing(.10f);eyebrow.setPadding(0,dp(10),0,dp(3));target.addView(eyebrow);
    TextView why=text(fitReasonV11(cap,goal),10,false,MUTED);why.setPadding(0,0,0,dp(8));target.addView(why);
    ArrayList<Cmd> ranked=rankCapabilityV11(cap,goal,6);if(ranked.isEmpty()){LinearLayout e=surface(true);e.addView(text("I understand the capability, but I don't have a strong enough prompt match to recommend confidently.",12,true,TEXT));TextView t=text("Choose another capability or browse the library instead of getting a weak recommendation.",10,false,MUTED);t.setPadding(0,dp(4),0,dp(8));e.addView(t);target.addView(e);Button choose=secondary("Choose another capability");choose.setOnClickListener(v->{CapabilityRouter.Route route=CapabilityRouter.route(goal);renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(choose);return;}
    Cmd first=ranked.get(0);TextView best=text("BEST APPROACH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(4),0,dp(5));target.addView(best);
    LinearLayout hero=surface(true);hero.setPadding(dp(13),dp(12),dp(13),dp(12));TextView capability=text(CapabilityRouter.label(cap),16,true,TEXT);hero.addView(capability);TextView outcome=text(CapabilityRouter.outcome(cap),10,false,MUTED);outcome.setPadding(0,dp(3),0,dp(8));hero.addView(outcome);TextView using=text("Using: "+polishedTitleV11(first),10,false,TERTIARY);using.setSingleLine(true);using.setEllipsize(android.text.TextUtils.TruncateAt.END);hero.addView(using);Button use=primary(selected.contains(first)?"Added":"Use this approach");use.setEnabled(!selected.contains(first));use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(first))selected.add(first);home();});hero.addView(use);target.addView(hero);
    if(ranked.size()>1){TextView more=text("OTHER STRONG MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(10),0,dp(5));target.addView(more);for(int i=1;i<Math.min(4,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}}
    Button back=secondary("Choose another capability");back.setOnClickListener(v->{askCapability="";CapabilityRouter.Route route=CapabilityRouter.route(goal);if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode))renderImageModeChooserV8(target,goal);else renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(back);
  }''')

# Compound workflows use the quality-gated ranker and capability diversity.
s=replace_method(s,'  void renderCompoundWorkflowV8(',r'''  void renderCompoundWorkflowV8(LinearLayout target,String goal,CapabilityRouter.Route route){
    target.removeAllViews();ArrayList<Cmd> flow=new ArrayList<>();ArrayList<String> usedCaps=new ArrayList<>();for(String cap:route.capabilities){ArrayList<Cmd> r=rankCapabilityV11(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0))){flow.add(r.get(0));usedCaps.add(cap);}if(flow.size()>=4)break;}if(flow.size()<2){if(route.capabilities.isEmpty()){renderAskResultsV8(target,goal);return;}renderCapabilityRecommendationV8(target,goal,route.capabilities.get(0));return;}
    TextView h=text("SUGGESTED WORKFLOW",10,true,TERTIARY);h.setLetterSpacing(.10f);h.setPadding(0,dp(10),0,dp(5));target.addView(h);LinearLayout card=surface(true);card.setPadding(dp(12),dp(10),dp(12),dp(10));for(int i=0;i<flow.size();i++){Cmd c=flow.get(i);String cap=usedCaps.get(i);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(String.valueOf(i+1),9,true,TERTIARY);n.setGravity(Gravity.CENTER);row.addView(n,new LinearLayout.LayoutParams(dp(24),dp(36)));LinearLayout copy=vbox();copy.addView(text(CapabilityRouter.label(cap),12,true,TEXT));TextView sub=text(polishedTitleV11(c),9,false,MUTED);sub.setSingleLine(true);sub.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(sub);row.addView(copy,new LinearLayout.LayoutParams(0,dp(36),1));card.addView(row);}Button use=primary("Use this workflow");use.setOnClickListener(v->{beginAskSelectionV10(goal);for(Cmd c:flow)if(!selected.contains(c))selected.add(c);home();});card.addView(use);target.addView(card);TextView meta=text("Each step comes from a different capability family, so the workflow adds coverage instead of duplicate prompts.",9,false,MUTED);meta.setPadding(0,dp(5),0,dp(8));target.addView(meta);
  }''')

# Browse and stack use polished display text too.
for marker in ['  View commandRow(','  void showStackSheet()','  View workflowCard(']:
    if marker in s:
        a,b=method_span(s,marker);block=s[a:b]
        block=block.replace('safePresentationTitleV10(c)','polishedTitleV11(c)').replace('safePresentationOutcomeV10(c)','polishedOutcomeV11(c,"")')
        s=s[:a]+block+s[b:]

# Slightly simplify Review & Run wording without removing controls.
a,b=method_span(s,'  void showStackSheet()');block=s[a:b]
block=block.replace('text("Review & Run",19,true,TEXT)','text("Ready to run",19,true,TEXT)')
block=block.replace('text(selected.size()+" selected prompt"+(selected.size()==1?"":"s"),10,false,MUTED)','text(selected.size()+" step"+(selected.size()==1?"":"s")+" in this workflow",10,false,MUTED)')
block=block.replace('Button copyPrompt=secondary("Copy prompt")','Button copyPrompt=secondary("Copy final prompt")')
s=s[:a]+block+s[b:]

# Version bump.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 34',g,count=1)
GRADLE.write_text(g,encoding='utf-8')

for token in ['ArrayList<Cmd> rankCapabilityV11(String cap,String query,int limit)','qualityScoreV11(Cmd c,String cap,String query)','polishedTitleV11(Cmd c)','BEST APPROACH','Using: ','versionCode 34']:
    hay=s if token!='versionCode 34' else g
    if token not in hay: raise SystemExit('v11 gate missing: '+token)

JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v11 applied: confidence-gated recommendations, family diversity, capability-first hero, polished presentation, simpler Review & Run')