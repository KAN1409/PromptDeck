#!/usr/bin/env python3
from pathlib import Path
p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='englishizeDescriptions();}'
new='englishizeDescriptions();canonicalizeLibrary();}'
if old not in s and 'canonicalizeLibrary();}' not in s:
    raise SystemExit('load() anchor not found')
s=s.replace(old,new,1)
# Replace prior canonicalizeLibrary implementation if present.
start=s.find('  void canonicalizeLibrary(){')
end=s.find('  void loadCommunityPrompts(){', start if start>=0 else 0)
method=r'''  void canonicalizeLibrary(){
    HashMap<String,String> legacy=new HashMap<>();
    legacy.put("Writing","Writing & Rewriting");legacy.put("Explain","Learning & Study");legacy.put("Ideation","Thinking & Ideas");legacy.put("Planning","Planning & Execution");legacy.put("Analysis","Research & Analysis");legacy.put("Decision","Thinking & Ideas");legacy.put("Study","Learning & Study");legacy.put("Research","Research & Analysis");legacy.put("Work","Work & Career");legacy.put("Format","Data & Formatting");legacy.put("Reasoning","Thinking & Ideas");legacy.put("Career","Work & Career");legacy.put("Technical","Problem Solving & Technical");legacy.put("Coding","Problem Solving & Technical");legacy.put("Data","Data & Formatting");legacy.put("Quality","Writing & Rewriting");legacy.put("Evaluation","Research & Analysis");legacy.put("Meta","AI & Prompting");legacy.put("Content","Content Creation");

    HashMap<String,String> preferred=new HashMap<>();
    preferred.put("NoteTakingAssistant2","NoteTakingassistant");
    preferred.put("Sales","Digitalproductideas");
    preferred.put("Selarideasforautomation","Digitalproductideas");
    preferred.put("Ainew","UltraRealisticNoirPortraitCreation");
    preferred.put("VirtualizationExpert","CompareTopVirtualizationSolutions");
    preferred.put("emailsProfessionals","ProfessionalEmailWriterforAnyOccasion");
    preferred.put("PowerShellScripttoMoveDisabledADUserst","PowerShellScriptforManagingDisabledADU");
    preferred.put("NightShiftDessertShop","EveningataTurkishDessertShopAPhotograp");
    preferred.put("DevelopaUILibraryforESP32","ESP32UILibraryDevelopment");
    preferred.put("MinimalistEditorialBeautyAnalysiswithT","MinimalistEditorialBeautyAnalysiswithE");
    preferred.put("MinimalistEditorialBeautyAnalysiswithE2","MinimalistEditorialBeautyAnalysiswithE");
    preferred.put("FrontendDeveloper","FrontendDeveloperSkill");
    preferred.put("InvestigativeResearchAssistantforUncov","InvestigativeResearchAssistant");
    preferred.put("MakeAIwritenaturally","PlainTalkStyleGuide");
    preferred.put("PromptGeneratorforclaudecode","PromptGeneratorforLanguageModels");
    preferred.put("WebApplicationTestingSkillImported","WebApplicationTestingSkill");
    preferred.put("Videoextractorprompt","Videoreviewandteacher");
    preferred.put("BikiniGirl","Seasidewalker");
    preferred.put("Video","Cocktailvideos");
    preferred.put("MirrorSelfieSceneDescription","Detailedmirrorselfieroomscene");
    preferred.put("Image","ProfessionalBadgePhotoReadytoUse");

    HashMap<String,String> rename=new HashMap<>();
    rename.put("Digitalproductideas","SelarDigitalProductIdeas");
    rename.put("NoteTakingassistant","LectureNoteTakingAssistant");
    rename.put("Detailedmirrorselfieroomscene","MirrorSelfieScene");
    rename.put("InvestigativeResearchAssistant","InvestigativeResearchAssistant");
    rename.put("CompareTopVirtualizationSolutions","VirtualizationSolutionsComparison");
    rename.put("EveningataTurkishDessertShopAPhotograp","TurkishDessertShopNightScene");
    rename.put("ESP32UILibraryDevelopment","ESP32UILibraryDevelopment");
    rename.put("FrontendDeveloperSkill","FrontendDeveloper");
    rename.put("MinimalistEditorialBeautyAnalysiswithE","MinimalistEditorialBeautyAnalysis");
    rename.put("PromptGeneratorforLanguageModels","ChatGPTPromptGenerator");
    rename.put("ProfessionalEmailWriterforAnyOccasion","ProfessionalEmailWriter");
    rename.put("PowerShellScriptforManagingDisabledADU","MoveDisabledADUsers");
    rename.put("Videoreviewandteacher","VideoReviewAndTeachingExtractor");
    rename.put("PlainTalkStyleGuide","PlainTalkNaturalWriting");

    HashSet<String> commands=new HashSet<>();for(Cmd c:all)commands.add(c.command);
    Iterator<Cmd> it=all.iterator();
    while(it.hasNext()){
      Cmd c=it.next();
      String keep=preferred.get(c.command);
      if(keep!=null&&commands.contains(keep)){it.remove();continue;}
      String mapped=legacy.get(c.category);if(mapped!=null)c.category=mapped;
      if(c.category.equals("Transform")){
        String q=(c.command+" "+c.description).toLowerCase(Locale.ROOT);
        c.category=(q.contains("json")||q.contains("csv")||q.contains("table")||q.contains("format")||q.contains("extract")||q.contains("convert")||q.contains("structure"))?"Data & Formatting":"Writing & Rewriting";
      }
      if(c.subcategory==null||c.subcategory.trim().isEmpty())c.subcategory="General";
      String rn=rename.get(c.command);if(rn!=null)c.command=rn;
      if(c.command.equals("ChatGPTPromptGenerator")&&!c.instruction.toLowerCase(Locale.ROOT).contains("chatgpt"))c.instruction="Optimize the following task specifically for ChatGPT. "+c.instruction;
    }
    // Final exact-body duplicate guard. This is the only automatic text-based removal.
    HashSet<String> seen=new HashSet<>();it=all.iterator();while(it.hasNext()){Cmd c=it.next();String k=normalizePrompt(c.instruction);if(!seen.add(k))it.remove();}
  }

'''
if start>=0 and end>start:
    s=s[:start]+method+s[end:]
else:
    anchor='  void loadCommunityPrompts(){'
    if anchor not in s: raise SystemExit('method anchor not found')
    s=s.replace(anchor,method+anchor,1)
p.write_text(s,encoding='utf-8')
print('V14 semantic canonical consolidation patch applied')
