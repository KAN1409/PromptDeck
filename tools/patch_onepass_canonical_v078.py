#!/usr/bin/env python3
from pathlib import Path
p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='englishizeDescriptions();}'
new='englishizeDescriptions();canonicalizeLibrary();}'
if old not in s and 'canonicalizeLibrary();}' not in s:
    raise SystemExit('load() anchor not found')
s=s.replace(old,new,1)
if 'void canonicalizeLibrary()' not in s:
    anchor='  void loadCommunityPrompts(){'
    method=r'''  void canonicalizeLibrary(){
    HashMap<String,String> legacy=new HashMap<>();
    legacy.put("Writing","Writing & Rewriting");legacy.put("Transform","Writing & Rewriting");legacy.put("Explain","Learning & Study");legacy.put("Ideation","Thinking & Ideas");legacy.put("Planning","Planning & Execution");legacy.put("Analysis","Research & Analysis");legacy.put("Decision","Thinking & Ideas");legacy.put("Study","Learning & Study");legacy.put("Research","Research & Analysis");legacy.put("Work","Work & Career");legacy.put("Format","Data & Formatting");legacy.put("Reasoning","Thinking & Ideas");legacy.put("Career","Work & Career");legacy.put("Technical","Problem Solving & Technical");legacy.put("Coding","Problem Solving & Technical");legacy.put("Data","Data & Formatting");legacy.put("Quality","Research & Analysis");legacy.put("Evaluation","Research & Analysis");legacy.put("Meta","AI & Prompting");legacy.put("Content","Content Creation");
    HashSet<String> broken=new HashSet<>(Arrays.asList("SocraticLens","MCPBuilder","MinimaxMusicLyricsGeneration","skillmaster","claudemdmaster","GitHubTrends","ComprehensivePythonCodebaseReviewForen","GoIndustrialAutonomousBusinessModuleCo","test3","Test2"));
    HashMap<String,String> preferred=new HashMap<>();
    preferred.put("NoteTakingAssistant2","NoteTakingassistant");preferred.put("Image","ProfessionalBadgePhotoReadytoUse");preferred.put("Selarideasforautomation","Sales");preferred.put("Ainew","UltraRealisticNoirPortraitCreation");preferred.put("WebApplicationTestingSkillImported","WebApplicationTestingSkill");preferred.put("MirrorSelfieSceneDescription","Detailedmirrorselfieroomscene");preferred.put("BikiniGirl","Seasidewalker");preferred.put("Video","Cocktailvideos");preferred.put("ImportedPrompt2032","ExpertPrompt4");
    HashSet<String> commands=new HashSet<>();for(Cmd c:all)commands.add(c.command);
    Iterator<Cmd> it=all.iterator();while(it.hasNext()){Cmd c=it.next();if(broken.contains(c.command)){it.remove();continue;}String keep=preferred.get(c.command);if(keep!=null&&commands.contains(keep)){it.remove();continue;}String mapped=legacy.get(c.category);if(mapped!=null)c.category=mapped;if(c.subcategory==null||c.subcategory.trim().isEmpty())c.subcategory="General";if(c.command.equals("ExpertPrompt"))c.command="MontenegroPanoramicApartment";}
    HashSet<String> seen=new HashSet<>();it=all.iterator();while(it.hasNext()){Cmd c=it.next();String k=normalizePrompt(c.instruction);if(!seen.add(k))it.remove();}
  }

'''
    if anchor not in s: raise SystemExit('method anchor not found')
    s=s.replace(anchor,method+anchor,1)
p.write_text(s,encoding='utf-8')
print('Canonical cleanup patch applied')
