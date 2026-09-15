#!/usr/bin/env python3
from pathlib import Path
import re

src=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
gradle=Path('android/app/build.gradle')
s=src.read_text(encoding='utf-8')

old='''  ArrayList<Cmd> rankCapabilityV11(String cap,String query,int limit){
    ArrayList<Cmd> pool=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();for(Cmd c:all){int sc=qualityScoreV11(c,cap,query);int floor=cap.startsWith("image.")?38:24;if(sc>=floor){pool.add(c);scores.put(c,sc);}}
    Collections.sort(pool,(a,b)->{int x=scores.get(a),y=scores.get(b);if(x!=y)return Integer.compare(y,x);return polishedTitleV11(a).compareToIgnoreCase(polishedTitleV11(b));});
    ArrayList<Cmd> out=new ArrayList<>();HashSet<String> families=new HashSet<>(),titles=new HashSet<>();for(Cmd c:pool){String title=polishedTitleV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim(),fam=familyKeyV11(c,cap);if(titles.contains(title)||families.contains(fam))continue;titles.add(title);families.add(fam);out.add(c);if(out.size()>=limit)break;}return out;
  }
'''
new='''  boolean capabilityCandidateV21(Cmd c,String cap){
    if(c==null)return false;String cat=c.category==null?"":c.category;
    if(cap.startsWith("image."))return imagePromptV8(c);
    if(cap.startsWith("career."))return cat.equals("Work & Business")||cat.equals("Career & Business");
    if(cap.startsWith("decision."))return cat.equals("Planning & Decisions")||cat.equals("Research & Analysis");
    if(cap.startsWith("data."))return cat.equals("Technology & Data")||cat.equals("Research & Analysis");
    if(cap.startsWith("code."))return cat.equals("Technology & Data")||cat.equals("Technology & Development");
    if(cap.startsWith("research."))return cat.equals("Research & Analysis")||cat.equals("Research & Learning");
    if(cap.startsWith("planning."))return cat.equals("Planning & Decisions")||cat.equals("Productivity & Planning");
    if(cap.startsWith("learning."))return cat.equals("Learning & Education")||cat.equals("Research & Analysis")||cat.equals("Science & Education");
    if(cap.startsWith("writing."))return cat.equals("Writing & Communication")||cat.equals("Creativity & Content")||cat.equals("Writing & Content");
    return true;
  }
  String cheapSearchV21(Cmd c){
    return ((c.command==null?"":c.command)+" "+(c.description==null?"":c.description)+" "+(c.category==null?"":c.category)+" "+(c.subcategory==null?"":c.subcategory)).toLowerCase(Locale.ROOT);
  }
  ArrayList<Cmd> rankCapabilityV11(String cap,String query,int limit){
    final String q=CapabilityRouter.norm(query);final String[] qWords=q.split(" ");final String[] capWords=CapabilityRouter.terms(cap).split(" ");
    ArrayList<Cmd> candidates=new ArrayList<>();
    for(Cmd c:all){
      if(!capabilityCandidateV21(c,cap))continue;
      String hay=cheapSearchV21(c);boolean useful=false;
      for(String w:capWords)if(w.length()>2&&hay.contains(w)){useful=true;break;}
      if(!useful)for(String w:qWords)if(w.length()>3&&hay.contains(w)){useful=true;break;}
      if(useful||capabilityCategoryBoostV8(c,cap)>=30)candidates.add(c);
    }
    // Bound expensive presentation/regex scoring. Category routing already narrowed semantics.
    if(candidates.size()>700)candidates=new ArrayList<>(candidates.subList(0,700));
    ArrayList<Cmd> pool=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();
    for(Cmd c:candidates){int sc=qualityScoreV11(c,cap,query);int floor=cap.startsWith("image.")?38:24;if(sc>=floor){pool.add(c);scores.put(c,sc);}}
    Collections.sort(pool,(a,b)->{int x=scores.get(a),y=scores.get(b);if(x!=y)return Integer.compare(y,x);return commandWordsV11(a).compareToIgnoreCase(commandWordsV11(b));});
    ArrayList<Cmd> out=new ArrayList<>();HashSet<String> families=new HashSet<>(),titles=new HashSet<>();for(Cmd c:pool){String title=commandWordsV11(c).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ").trim(),fam=familyKeyV11(c,cap);if(titles.contains(title)||families.contains(fam))continue;titles.add(title);families.add(fam);out.add(c);if(out.size()>=limit)break;}return out;
  }
'''
if 'boolean capabilityCandidateV21' not in s:
    if old not in s: raise SystemExit('rankCapabilityV11 anchor missing')
    s=s.replace(old,new,1)

# Make workflow cap count bounded to three distinct capabilities for responsiveness.
s=s.replace('for(String cap:route.capabilities){ArrayList<Cmd> r=rankCapabilityV11(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0))){flow.add(r.get(0));usedCaps.add(cap);}if(flow.size()>=4)break;}',
'''int capCount=0;for(String cap:route.capabilities){if(capCount++>=3)break;ArrayList<Cmd> r=rankCapabilityV11(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0))){flow.add(r.get(0));usedCaps.add(cap);}if(flow.size()>=3)break;}''')

src.write_text(s,encoding='utf-8')
g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 49',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.9.3-router-performance'",g,count=1)
gradle.write_text(g,encoding='utf-8')

out=src.read_text(encoding='utf-8')
for token in ['capabilityCandidateV21','cheapSearchV21','candidates.size()>700','capCount++>=3']:
    if token not in out: raise SystemExit('performance gate missing: '+token)
if 'versionCode 49' not in gradle.read_text() or "versionName '0.9.3-router-performance'" not in gradle.read_text(): raise SystemExit('version gate failed')
print('PromptDeck router performance v0.9.3 applied')
