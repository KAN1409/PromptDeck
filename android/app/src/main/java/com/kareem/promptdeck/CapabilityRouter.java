package com.kareem.promptdeck;

import java.util.*;

/**
 * Capability-first routing for PromptDeck Ask mode.
 * The router understands the user's outcome first, then selects a capability family.
 * Prompt ranking happens only after routing, never across the full catalog blindly.
 */
final class CapabilityRouter {
  static final String IMAGE="IMAGE", CAREER="CAREER", DECISION="DECISION", CODE="CODE", DATA="DATA",
      RESEARCH="RESEARCH", PLANNING="PLANNING", LEARNING="LEARNING", WRITING="WRITING", GENERAL="GENERAL";
  static final String EDIT="EDIT", CREATE="CREATE", UNKNOWN="UNKNOWN";

  static final class Route {
    final String domain, mode;
    final boolean broad;
    final ArrayList<String> capabilities;
    Route(String domain,String mode,boolean broad,ArrayList<String> capabilities){
      this.domain=domain;this.mode=mode;this.broad=broad;this.capabilities=capabilities;
    }
  }

  private CapabilityRouter(){}

  static String norm(String x){
    return (x==null?"":x.toLowerCase(Locale.ROOT)).replaceAll("[^a-z0-9]+"," ").replaceAll("\\s+"," ").trim();
  }
  static boolean has(String q,String...terms){
    String z=" "+norm(q)+" ";
    for(String t:terms){String n=norm(t);if(!n.isEmpty()&&z.contains(" "+n+" "))return true;}
    return false;
  }

  static String domain(String q){
    String z=norm(q);
    if(has(z,"photo","image","picture","portrait","background","retouch","upscale","sharpen","blur","crop","visual","poster","thumbnail"))return IMAGE;
    if(has(z,"resume","cv","interview","career","job","ats","cover letter"))return CAREER;
    if(has(z,"compare","choose","decision","decide","recommend","versus","tradeoff","trade off"))return DECISION;
    if(has(z,"data","dataset","spreadsheet","excel","csv","statistics","statistical","analyze data","analyse data","data analysis","dashboard","chart","visualization","visualisation","insights","trend"))return DATA;
    if(has(z,"debug","code","coding","error","bug","refactor","programming","api","sql"))return CODE;
    if(has(z,"research","sources","evidence","fact check","verify","investigate"))return RESEARCH;
    if(has(z,"plan","roadmap","schedule","checklist","project","organize","strategy"))return PLANNING;
    if(has(z,"learn","study","teach","explain","quiz","tutor"))return LEARNING;
    if(has(z,"write","rewrite","email","article","post","caption","summarize","summary","tone"))return WRITING;
    return GENERAL;
  }

  static String imageMode(String q){
    String z=norm(q);
    if(has(z,"generate","create","draw","render","make an image","make a photo","from scratch","new image","new picture"))return CREATE;
    if(has(z,"edit","editing","retouch","remove","replace","background","upscale","restore","sharpen","blur","crop","reframe","expand","fix lighting","color grade","cleanup","clean up"))return EDIT;
    return UNKNOWN;
  }

  static boolean broad(String domain,String q){
    String z=norm(q);if(z.isEmpty())return true;
    if(IMAGE.equals(domain)){
      if(z.equals("photo")||z.equals("image")||z.equals("picture")||z.equals("photo edit")||z.equals("edit photo")||z.equals("image edit")||z.equals("edit image")||z.equals("photo editing")||z.equals("image editing")||z.equals("edit my photo")||z.equals("edit a photo")||z.equals("create image")||z.equals("generate image"))return true;
      return false;
    }
    if(LEARNING.equals(domain))return z.equals("study")||z.equals("learn")||z.equals("learning")||z.equals("explain")||z.equals("help me study")||z.equals("teach me");
    if(CAREER.equals(domain))return z.equals("resume")||z.equals("cv")||z.equals("career")||z.equals("job")||z.equals("help with my cv")||z.equals("help with my resume");
    if(DECISION.equals(domain))return z.equals("compare")||z.equals("choose")||z.equals("decision")||z.equals("decide")||z.equals("help me decide");
    if(DATA.equals(domain))return z.equals("data")||z.equals("analyze data")||z.equals("analyse data")||z.equals("data analysis")||z.equals("analyze my data")||z.equals("spreadsheet analysis");
    if(CODE.equals(domain))return z.equals("code")||z.equals("coding")||z.equals("debug")||z.equals("bug")||z.equals("help with code");
    if(RESEARCH.equals(domain))return z.equals("research")||z.equals("verify")||z.equals("do research");
    if(PLANNING.equals(domain))return z.equals("plan")||z.equals("planning")||z.equals("project plan")||z.equals("help me plan");
    if(WRITING.equals(domain))return z.equals("write")||z.equals("rewrite")||z.equals("writing")||z.equals("email")||z.equals("summary");
    return false;
  }

  static String[] capabilities(String domain,String mode){
    if(IMAGE.equals(domain)){
      if(CREATE.equals(mode))return new String[]{"image.create","image.portrait","image.product","image.text","image.style"};
      return new String[]{"image.enhance","image.portrait","image.background","image.remove","image.light","image.frame","image.style","image.product","image.text"};
    }
    if(CAREER.equals(domain))return new String[]{"career.createcv","career.improvecv","career.ats","career.tailor","career.interview"};
    if(DECISION.equals(domain))return new String[]{"decision.compare","decision.risk","decision.matrix","decision.recommend"};
    if(DATA.equals(domain))return new String[]{"data.analyze","data.clean","data.stats","data.visualize","data.spreadsheet","data.extract"};
    if(CODE.equals(domain))return new String[]{"code.debug","code.explain","code.review","code.build","code.optimize"};
    if(RESEARCH.equals(domain))return new String[]{"research.deep","research.verify","research.summarize","research.compare"};
    if(PLANNING.equals(domain))return new String[]{"planning.plan","planning.roadmap","planning.checklist","planning.schedule"};
    if(LEARNING.equals(domain))return new String[]{"learning.explain","learning.tutor","learning.study","learning.quiz"};
    if(WRITING.equals(domain))return new String[]{"writing.draft","writing.rewrite","writing.summarize","writing.tone","writing.email","writing.social"};
    return new String[0];
  }

  static String label(String id){
    switch(id){
      case "image.enhance":return "Enhance & restore"; case "image.portrait":return "Retouch portrait";
      case "image.background":return "Background"; case "image.remove":return "Remove something";
      case "image.light":return "Light & color"; case "image.frame":return "Crop / expand";
      case "image.style":return "Change the look"; case "image.product":return "Product photo";
      case "image.text":return "Text & graphics"; case "image.create":return "Create a new image";
      case "career.createcv":return "Create a CV"; case "career.improvecv":return "Improve my CV";
      case "career.ats":return "ATS check"; case "career.tailor":return "Tailor to a job"; case "career.interview":return "Interview prep";
      case "decision.compare":return "Compare options"; case "decision.risk":return "Risk & trade-offs";
      case "decision.matrix":return "Decision matrix"; case "decision.recommend":return "Recommend the best";
      case "data.analyze":return "Analyze data"; case "data.clean":return "Clean & structure data";
      case "data.stats":return "Statistics & patterns"; case "data.visualize":return "Charts & visualization";
      case "data.spreadsheet":return "Spreadsheet analysis"; case "data.extract":return "Extract insights";
      case "code.debug":return "Debug a problem"; case "code.explain":return "Explain code";
      case "code.review":return "Review code"; case "code.build":return "Build something"; case "code.optimize":return "Improve performance";
      case "research.deep":return "Deep research"; case "research.verify":return "Verify facts";
      case "research.summarize":return "Summarize evidence"; case "research.compare":return "Compare sources";
      case "planning.plan":return "Build a plan"; case "planning.roadmap":return "Create a roadmap";
      case "planning.checklist":return "Make a checklist"; case "planning.schedule":return "Build a schedule";
      case "learning.explain":return "Explain a topic"; case "learning.tutor":return "Tutor me";
      case "learning.study":return "Study plan"; case "learning.quiz":return "Quiz me";
      case "writing.draft":return "Draft from scratch"; case "writing.rewrite":return "Rewrite & improve";
      case "writing.summarize":return "Summarize"; case "writing.tone":return "Change tone";
      case "writing.email":return "Write an email"; case "writing.social":return "Social content";
      default:return "Best match";
    }
  }

  static String outcome(String id){
    switch(id){
      case "image.enhance":return "Improve quality, sharpness or restore damage without changing the subject.";
      case "image.portrait":return "Refine face, skin, hair and portrait details while preserving identity.";
      case "image.background":return "Remove, replace or blur the background while keeping the subject natural.";
      case "image.remove":return "Remove unwanted people or objects and rebuild the scene convincingly.";
      case "image.light":return "Fix exposure, lighting and color while preserving realistic detail.";
      case "image.frame":return "Crop, straighten, reframe or expand the image consistently.";
      case "image.style":return "Apply a photographic or artistic look while preserving the subject.";
      case "image.product":return "Polish a product image for clean commercial presentation.";
      case "image.text":return "Turn the image into a clear poster, social visual or graphic.";
      case "image.create":return "Generate a new visual from your description.";
      case "learning.explain":return "Understand a topic with clear explanations, examples and analogies.";
      case "learning.tutor":return "Learn interactively with questions, feedback and adaptive teaching.";
      case "learning.study":return "Turn a subject and deadline into a practical study plan.";
      case "learning.quiz":return "Test understanding with questions, answers and targeted review.";
      case "career.createcv":return "Build a strong CV from your experience and target role.";
      case "career.improvecv":return "Improve clarity, impact and positioning of an existing CV.";
      case "career.ats":return "Check ATS fit, keywords and likely screening weaknesses.";
      case "career.tailor":return "Adapt your CV to a specific job description without inventing experience.";
      case "career.interview":return "Prepare likely questions, strong answers and interview strategy.";
      case "decision.compare":return "Compare options consistently across the criteria that matter.";
      case "decision.risk":return "Expose downsides, uncertainty, regret and important trade-offs.";
      case "decision.matrix":return "Score options using explicit weighted criteria.";
      case "decision.recommend":return "Recommend the strongest option and explain the trade-offs.";
      case "data.analyze":return "Analyze a dataset systematically and surface the findings that matter.";
      case "data.clean":return "Clean, normalize and structure messy data before analysis.";
      case "data.stats":return "Find distributions, relationships, anomalies and statistically useful patterns.";
      case "data.visualize":return "Choose clear charts and visual summaries that reveal the important story.";
      case "data.spreadsheet":return "Analyze spreadsheet or CSV data, formulas, tables and business metrics.";
      case "data.extract":return "Turn raw data into concise insights, implications and next actions.";
      case "code.debug":return "Diagnose the likely root cause and produce a testable fix.";
      case "code.explain":return "Explain what the code does and how the important parts fit together.";
      case "code.review":return "Review correctness, maintainability, security and edge cases.";
      case "code.build":return "Turn requirements into an implementation plan and working code.";
      case "code.optimize":return "Improve performance or structure without unnecessary rewrites.";
      case "research.deep":return "Research the question systematically using relevant evidence.";
      case "research.verify":return "Verify important claims and flag uncertainty or weak evidence.";
      case "research.summarize":return "Condense evidence into the findings that actually matter.";
      case "research.compare":return "Compare sources, claims and perspectives consistently.";
      case "planning.plan":return "Turn a goal into clear steps, priorities and next actions.";
      case "planning.roadmap":return "Organize work into milestones, phases and dependencies.";
      case "planning.checklist":return "Convert the work into a concrete, usable checklist.";
      case "planning.schedule":return "Map tasks onto a realistic timeline or schedule.";
      case "writing.draft":return "Create a strong first draft from your goal and context.";
      case "writing.rewrite":return "Improve clarity and flow while preserving the intended meaning.";
      case "writing.summarize":return "Condense material into the most important information.";
      case "writing.tone":return "Change tone or style without changing the core message.";
      case "writing.email":return "Write a clear email suited to the recipient and purpose.";
      case "writing.social":return "Create concise social content shaped for the platform and goal.";
      default:return "Use the strongest prompt family for this outcome.";
    }
  }

  static String terms(String id){
    switch(id){
      case "image.enhance":return "enhance restore upscale sharpen clarity detail resolution damage old photo crisp";
      case "image.portrait":return "portrait face skin hair eyes teeth retouch headshot beauty natural smile identity";
      case "image.background":return "background replace remove background blur background cutout backdrop subject separation";
      case "image.remove":return "remove object person people distraction cleanup erase reconstruct";
      case "image.light":return "lighting exposure color grade grading brightness contrast saturation tone cinematic light";
      case "image.frame":return "crop reframe expand zoom out straighten framing composition extend frame";
      case "image.style":return "style look vintage film cinematic editorial watercolor anime artistic transformation mood";
      case "image.product":return "product commercial ecommerce studio packaging flat lay advertising";
      case "image.text":return "poster social thumbnail text overlay banner carousel marketing graphic";
      case "image.create":return "generate create image illustration visual render description";
      case "career.createcv":return "resume cv create build writer profile"; case "career.improvecv":return "resume cv improve rewrite review quality";
      case "career.ats":return "ats resume scanner keywords screening"; case "career.tailor":return "resume cv tailor job description match role";
      case "career.interview":return "interview questions answers prep practice";
      case "decision.compare":return "compare options criteria pros cons tradeoffs"; case "decision.risk":return "risk regret tradeoffs downside uncertainty";
      case "decision.matrix":return "decision matrix weighted criteria score"; case "decision.recommend":return "recommend best option choose strongest";
      case "data.analyze":return "analyze analysis data dataset metrics findings trends patterns insights";
      case "data.clean":return "clean normalize structure data dataset missing duplicates transform";
      case "data.stats":return "statistics statistical correlation distribution anomaly variance trend patterns";
      case "data.visualize":return "chart charts graph visualization dashboard plot visual data";
      case "data.spreadsheet":return "spreadsheet excel csv table formulas workbook data analysis";
      case "data.extract":return "extract insights findings implications actions data summary";
      case "code.debug":return "debug diagnose error bug root cause fix"; case "code.explain":return "explain code understand walkthrough";
      case "code.review":return "review code quality security tests"; case "code.build":return "build implement code developer";
      case "code.optimize":return "optimize performance refactor improve";
      case "research.deep":return "research deep dive sources evidence"; case "research.verify":return "verify fact check sources evidence accuracy";
      case "research.summarize":return "summarize research evidence findings"; case "research.compare":return "compare sources perspectives evidence";
      case "planning.plan":return "plan steps action goal"; case "planning.roadmap":return "roadmap milestones phases";
      case "planning.checklist":return "checklist todo action items"; case "planning.schedule":return "schedule timeline calendar";
      case "learning.explain":return "explain eli5 simple analogy"; case "learning.tutor":return "tutor teach interactive questions";
      case "learning.study":return "study plan learning revision"; case "learning.quiz":return "quiz test flashcards practice";
      case "writing.draft":return "write draft create article"; case "writing.rewrite":return "rewrite clarity improve polish humanize";
      case "writing.summarize":return "summarize summary concise"; case "writing.tone":return "tone formal casual professional";
      case "writing.email":return "email reply followup"; case "writing.social":return "social post caption hook content";
      default:return "";
    }
  }

  static ArrayList<String> matched(String domain,String q){
    ArrayList<String> out=new ArrayList<>();String z=norm(q);
    String mode=IMAGE.equals(domain)?imageMode(q):UNKNOWN;
    for(String id:capabilities(domain,mode)){
      int hits=0;for(String t:terms(id).split(" "))if(t.length()>2&&z.contains(t))hits++;
      if(hits>0)out.add(id);
    }
    return out;
  }

  static Route route(String q){
    String domain=domain(q);String mode=IMAGE.equals(domain)?imageMode(q):UNKNOWN;
    return new Route(domain,mode,broad(domain,q),matched(domain,q));
  }

  static String inferImageCapability(MainActivity.Cmd c){
    String title=((c.command==null?"":c.command)+" "+(c.subcategory==null?"":c.subcategory)+" "+(c.description==null?"":c.description)).toLowerCase(Locale.ROOT);
    String sub=c.subcategory==null?"":c.subcategory.toLowerCase(Locale.ROOT);
    if(sub.contains("enhance")||sub.contains("restore")||contains(title,"upscale","sharpen","clarity","restore","detail enhancement"))return "image.enhance";
    if(sub.contains("background")&&contains(title,"remove ","object","person","power line","backpack","shadow","cleanup"))return "image.remove";
    if(sub.contains("background")||contains(title,"background replacement","remove background","cutout","backdrop"))return "image.background";
    if(sub.contains("portrait")||contains(title,"portrait","headshot","skin tone","hair","selfie","smile"))return "image.portrait";
    if(sub.contains("color")||sub.contains("lighting")||contains(title,"color grading","lighting correction","exposure","saturation","contrast"))return "image.light";
    if(sub.contains("framing")||sub.contains("composition")||contains(title,"crop","zoom out","expand the frame","center the subject"))return "image.frame";
    if(sub.contains("product"))return "image.product";
    if(sub.contains("social")||contains(title,"poster","thumbnail","banner","text overlay","carousel"))return "image.text";
    if(sub.contains("film")||sub.contains("cinematic")||sub.contains("illustration")||sub.contains("surreal")||sub.contains("creative")||sub.contains("miniature")||contains(title,"style","look","transformation","anime","watercolor","editorial"))return "image.style";
    return "image.create";
  }

  private static boolean contains(String x,String...terms){for(String t:terms)if(x.contains(t))return true;return false;}

  // Cheap deterministic smoke tests used by CI/source gates.
  static boolean selfTest(){
    Route a=route("photo edit");if(!IMAGE.equals(a.domain)||!EDIT.equals(a.mode)||!a.broad)return false;
    Route b=route("remove people from the background");if(!IMAGE.equals(b.domain)||b.broad||!b.capabilities.contains("image.remove"))return false;
    Route c=route("study");if(!LEARNING.equals(c.domain)||!c.broad)return false;
    Route d=route("explain quantum computing");if(!LEARNING.equals(d.domain)||d.broad||!d.capabilities.contains("learning.explain"))return false;
    Route e=route("compare two cars");if(!DECISION.equals(e.domain)||e.broad||!e.capabilities.contains("decision.compare"))return false;
    Route f=route("debug app crash");if(!CODE.equals(f.domain)||f.broad||!f.capabilities.contains("code.debug"))return false;
    Route g=route("write an email");if(!WRITING.equals(g.domain)||g.broad||!g.capabilities.contains("writing.email"))return false;
    Route h=route("tailor my cv to this job");if(!CAREER.equals(h.domain)||h.broad||!h.capabilities.contains("career.tailor"))return false;
    Route i=route("verify this claim with sources");if(!RESEARCH.equals(i.domain)||i.broad||!i.capabilities.contains("research.verify"))return false;
    Route j=route("make a project roadmap");if(!PLANNING.equals(j.domain)||j.broad||!j.capabilities.contains("planning.roadmap"))return false;
    return true;
  }
}
