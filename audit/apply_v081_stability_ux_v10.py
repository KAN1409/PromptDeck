#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
ROUTER=Path('android/app/src/main/java/com/kareem/promptdeck/CapabilityRouter.java')
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
r=ROUTER.read_text(encoding='utf-8')

# Scope selections created by Ask PromptDeck to the goal that created them.
state='String discoverMode="landing"; String askGoal=""; String askCapability=""; int browseLimit=30;'
if state in s:
    s=s.replace(state,'String discoverMode="landing"; String askGoal=""; String askCapability=""; String askSelectionGoal=""; int browseLimit=30;',1)
elif 'String askSelectionGoal="";' not in s:
    raise SystemExit('ask state anchor missing')

helpers=r'''  void beginAskSelectionV10(String goal){
    String g=goal==null?"":goal.trim();
    if(!askSelectionGoal.isEmpty()&&!askSelectionGoal.equalsIgnoreCase(g))selected.clear();
    else if(askSelectionGoal.isEmpty()&&!selected.isEmpty()&&!contextDraft.trim().equalsIgnoreCase(g))selected.clear();
    askSelectionGoal=g;contextDraft=g;
  }
  String safePresentationTitleV10(Cmd c){
    String t=presentationTitleV8(c);if(t==null)t="";t=t.replaceAll("(?i)\\b(?:from|for)?prompt(?:ing)?(?:agent|role|skill)?\\b$","").replaceAll("\\s+"," ").trim();
    if(uglyPresentationV8(t)||longTokenV8(t)||t.matches(".*[{}\\[\\]\"<>].*")){String d=c.description==null?"":c.description.replaceAll("[{}\\[\\]\"<>#]"," ").replaceAll("\\s+"," ").trim();if(!uglyPresentationV8(d)&&!longTokenV8(d)&&d.length()>=4)t=d;}
    if(t.length()>58)t=t.substring(0,55).trim()+"…";return t.isEmpty()?"ChatGPT workflow":t;
  }
  String safePresentationOutcomeV10(Cmd c){
    String d=presentationOutcomeV8(c);if(d==null)d="";d=d.replaceAll("(?is)^(?:act as|you are|role:|title:|for this step in a larger workflow:)\\s*","").replaceAll("[{}\\[\\]\"<>#]"," ").replaceAll("\\s+"," ").trim();
    if(d.length()<8||uglyPresentationV8(d)||longTokenV8(d))d="Focused ChatGPT workflow for this outcome.";if(d.length()>92)d=d.substring(0,89).trim()+"…";return d;
  }
'''
if 'void beginAskSelectionV10(' not in s:
    s=insert_before(s,'  boolean longTokenV8(',helpers)

# Make visible presentation helpers use the safer generic layer.
for marker in ['  View bestCapabilityCardV8(','  void renderCapabilityRecommendationV8(','  void renderCompoundWorkflowV8(','  View workflowCard(','  View commandRow(','  void showStackSheet()']:
    if marker in s:
        a,b=method_span(s,marker);block=s[a:b]
        block=block.replace('presentationTitleV8(c)','safePresentationTitleV10(c)').replace('presentationOutcomeV8(c)','safePresentationOutcomeV10(c)')
        s=s[:a]+block+s[b:]

# Ask selections replace stale goal-scoped selections rather than silently inheriting them.
a,b=method_span(s,'  View bestCapabilityCardV8(');block=s[a:b]
old='use.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});'
new='use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(c))selected.add(c);home();});'
if old not in block: raise SystemExit('best capability use anchor missing')
block=block.replace(old,new,1);s=s[:a]+block+s[b:]

# Workflow selection follows the same goal scoping rule.
a,b=method_span(s,'  View workflowCard(');block=s[a:b]
old='use.setOnClickListener(v->{for(Cmd c:flow)if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});'
new='use.setOnClickListener(v->{beginAskSelectionV10(goal);for(Cmd c:flow)if(!selected.contains(c))selected.add(c);home();});'
if old in block:block=block.replace(old,new,1)
else:
    # tolerate presentation-wrapped variant but require an actual workflow listener
    if 'use.setOnClickListener' not in block: raise SystemExit('workflow use listener missing')
s=s[:a]+block+s[b:]

# Direct generic Ask best-match should also scope the selection.
a,b=method_span(s,'  View bestMatchCard(');block=s[a:b]
old='use.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);contextDraft=goal;home();});'
new='use.setOnClickListener(v->{beginAskSelectionV10(goal);if(!selected.contains(c))selected.add(c);home();});'
if old in block:block=block.replace(old,new,1)
s=s[:a]+block+s[b:]

# Clear Ask ownership when user manually starts browsing so Browse can intentionally build a mixed stack.
a,b=method_span(s,'  void renderBrowseResultsV6(');block=s[a:b]
if 'askSelectionGoal="";' not in block:
    block=block.replace('target.removeAllViews();','target.removeAllViews();askSelectionGoal="";',1)
s=s[:a]+block+s[b:]

# Refine broad-intent behavior: broad means genuinely underspecified, not merely short.
r=replace_method(r,'  static boolean broad(',r'''  static boolean broad(String domain,String q){
    String z=norm(q);if(z.isEmpty())return true;
    if(IMAGE.equals(domain)){
      if(z.equals("photo")||z.equals("image")||z.equals("picture")||z.equals("photo edit")||z.equals("edit photo")||z.equals("image edit")||z.equals("edit image")||z.equals("photo editing")||z.equals("image editing")||z.equals("edit my photo")||z.equals("edit a photo")||z.equals("create image")||z.equals("generate image"))return true;
      return false;
    }
    if(LEARNING.equals(domain))return z.equals("study")||z.equals("learn")||z.equals("learning")||z.equals("explain")||z.equals("help me study")||z.equals("teach me");
    if(CAREER.equals(domain))return z.equals("resume")||z.equals("cv")||z.equals("career")||z.equals("job")||z.equals("help with my cv")||z.equals("help with my resume");
    if(DECISION.equals(domain))return z.equals("compare")||z.equals("choose")||z.equals("decision")||z.equals("decide")||z.equals("help me decide");
    if(CODE.equals(domain))return z.equals("code")||z.equals("coding")||z.equals("debug")||z.equals("bug")||z.equals("help with code");
    if(RESEARCH.equals(domain))return z.equals("research")||z.equals("verify")||z.equals("do research");
    if(PLANNING.equals(domain))return z.equals("plan")||z.equals("planning")||z.equals("project plan")||z.equals("help me plan");
    if(WRITING.equals(domain))return z.equals("write")||z.equals("rewrite")||z.equals("writing")||z.equals("email")||z.equals("summary");
    return false;
  }''')

# More useful capability copy outside Images.
r=replace_method(r,'  static String outcome(',r'''  static String outcome(String id){
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
  }''')

# Strengthen deterministic regression tests.
r=replace_method(r,'  static boolean selfTest()',r'''  static boolean selfTest(){
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
  }''')

# Version bump.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 33',g,count=1)

for token in ['String askSelectionGoal="";','void beginAskSelectionV10(String goal)','safePresentationTitleV10(Cmd c)','safePresentationOutcomeV10(Cmd c)','versionCode 33']:
    hay=s if token!='versionCode 33' else g
    if token not in hay: raise SystemExit('v10 gate missing: '+token)
for token in ['route("study")','route("compare two cars")','route("debug app crash")','route("write an email")','route("tailor my cv to this job")']:
    if token not in r: raise SystemExit('router regression missing: '+token)

JAVA.write_text(s,encoding='utf-8')
ROUTER.write_text(r,encoding='utf-8')
GRADLE.write_text(g,encoding='utf-8')
print('PromptDeck v10 applied: Ask selections scoped by goal, broad routing hardened, presentation sanitized, regression suite expanded')
