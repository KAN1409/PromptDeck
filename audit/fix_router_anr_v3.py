#!/usr/bin/env python3
from pathlib import Path
import re

src=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
gradle=Path('android/app/build.gradle')
s=src.read_text(encoding='utf-8')

# Add an async generation token once.
needle='String page="home"; Group currentGroup=null; String contextDraft=""; String discoverCategory=""; String discoverSubcategory=""; boolean discoverFavorites=false; String discoverPreset=""; String discoverMode="landing"; String askGoal=""; String askCapability=""; String askSelectionGoal=""; int browseLimit=30; HashMap<Integer,HashMap<String,String>> promptVars=new HashMap<>();'
if 'int routeGenerationV20=0;' not in s:
    if needle not in s: raise SystemExit('state field anchor missing')
    s=s.replace(needle,needle+' int routeGenerationV20=0;',1)

# Capability chooser taps must use async recommendation rendering.
s=s.replace('renderCapabilityRecommendationV8(target,goal,left);','renderCapabilityRecommendationAsyncV20(target,goal,left);')
s=s.replace('renderCapabilityRecommendationV8(target,goal,right);','renderCapabilityRecommendationAsyncV20(target,goal,right);')

start=s.find('  void renderAskResultsV8(LinearLayout target,String goal){')
end=s.find('\n\n  void renderAskResults(LinearLayout target,String goal)',start)
if start<0 or end<0: raise SystemExit('renderAskResultsV8 block missing')

replacement=r'''  void showRouteLoadingV20(LinearLayout target,String label){
    target.removeAllViews();LinearLayout box=surface(true);box.setPadding(dp(12),dp(12),dp(12),dp(12));
    ProgressBar p=new ProgressBar(this);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);row.addView(p,new LinearLayout.LayoutParams(dp(28),dp(28)));TextView t=text(label,11,false,MUTED);LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,-2,1);tp.setMargins(dp(10),0,0,0);row.addView(t,tp);box.addView(row);target.addView(box);
  }

  boolean routeStillValidV20(int generation){return generation==routeGenerationV20&&"home".equals(page)&&"ask".equals(discoverMode);}

  void renderCapabilityRecommendationPreparedV20(LinearLayout target,String goal,String cap,ArrayList<Cmd> ranked){
    target.removeAllViews();TextView eyebrow=text(CapabilityRouter.label(cap).toUpperCase(Locale.ROOT),10,true,TERTIARY);eyebrow.setLetterSpacing(.10f);eyebrow.setPadding(0,dp(10),0,dp(3));target.addView(eyebrow);
    TextView why=text(fitReasonV11(cap,goal),10,false,MUTED);why.setPadding(0,0,0,dp(8));target.addView(why);
    if(ranked.isEmpty()){LinearLayout e=surface(true);e.addView(text("I understand the capability, but I don't have a strong enough prompt match to recommend confidently.",12,true,TEXT));TextView t=text("Choose another capability or browse the library instead of getting a weak recommendation.",10,false,MUTED);t.setPadding(0,dp(4),0,dp(8));e.addView(t);target.addView(e);Button choose=secondary("Choose another capability");choose.setOnClickListener(v->{CapabilityRouter.Route route=CapabilityRouter.route(goal);renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(choose);return;}
    Cmd first=ranked.get(0);TextView best=text("BEST APPROACH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(4),0,dp(5));target.addView(best);
    LinearLayout hero=surface(true);hero.setPadding(dp(13),dp(12),dp(13),dp(12));hero.addView(text(CapabilityRouter.label(cap),16,true,TEXT));TextView outcome=text(CapabilityRouter.outcome(cap),10,false,MUTED);outcome.setPadding(0,dp(3),0,dp(8));hero.addView(outcome);TextView using=text("Using: "+polishedTitleV11(first),10,false,TERTIARY);using.setSingleLine(true);using.setEllipsize(android.text.TextUtils.TruncateAt.END);hero.addView(using);Button use=primary(selected.contains(first)?"Added":"Use this approach");use.setEnabled(!selected.contains(first));use.setOnClickListener(v->{beginAskSelectionV10(goal);rememberRecent(first);if(!selected.contains(first))selected.add(first);home();});hero.addView(use);target.addView(hero);
    if(ranked.size()>1){TextView more=text("OTHER STRONG MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(10),0,dp(5));target.addView(more);for(int i=1;i<Math.min(7,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}}
    Button allMatches=secondary("View all matches");allMatches.setOnClickListener(v->{discoverMode="browse";discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset=goal;browseLimit=60;home();});target.addView(allMatches);
    Button back=secondary("Choose another capability");back.setOnClickListener(v->{askCapability="";CapabilityRouter.Route route=CapabilityRouter.route(goal);if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode))renderImageModeChooserV8(target,goal);else renderCapabilityChooserV8(target,route.domain,goal,route.mode);});target.addView(back);
  }

  void renderCapabilityRecommendationAsyncV20(LinearLayout target,String goal,String cap){
    final int generation=++routeGenerationV20;showRouteLoadingV20(target,"Finding the strongest match…");
    new Thread(()->{ArrayList<Cmd> ranked=rankCapabilityV11(cap,goal,20);runOnUiThread(()->{if(routeStillValidV20(generation))renderCapabilityRecommendationPreparedV20(target,goal,cap,ranked);});},"PromptDeckRankOne").start();
  }

  void renderCompoundWorkflowPreparedV20(LinearLayout target,String goal,ArrayList<Cmd> flow,ArrayList<String> usedCaps){
    target.removeAllViews();if(flow.size()<2){if(usedCaps.isEmpty()){renderFallbackAsyncV20(target,goal);return;}renderCapabilityRecommendationAsyncV20(target,goal,usedCaps.get(0));return;}
    TextView h=text("SUGGESTED WORKFLOW",10,true,TERTIARY);h.setLetterSpacing(.10f);h.setPadding(0,dp(10),0,dp(5));target.addView(h);LinearLayout card=surface(true);card.setPadding(dp(12),dp(10),dp(12),dp(10));for(int i=0;i<flow.size();i++){Cmd c=flow.get(i);String cap=usedCaps.get(i);LinearLayout row=hbox();row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(String.valueOf(i+1),9,true,TERTIARY);n.setGravity(Gravity.CENTER);row.addView(n,new LinearLayout.LayoutParams(dp(24),dp(36)));LinearLayout copy=vbox();copy.addView(text(CapabilityRouter.label(cap),12,true,TEXT));TextView sub=text(polishedTitleV11(c),9,false,MUTED);sub.setSingleLine(true);sub.setEllipsize(android.text.TextUtils.TruncateAt.END);copy.addView(sub);row.addView(copy,new LinearLayout.LayoutParams(0,dp(36),1));card.addView(row);}Button use=primary("Use this workflow");use.setOnClickListener(v->{beginAskSelectionV10(goal);for(Cmd c:flow){rememberRecent(c);if(!selected.contains(c))selected.add(c);}home();});card.addView(use);target.addView(card);TextView meta=text("Each step comes from a different capability family, so the workflow adds coverage instead of duplicate prompts.",9,false,MUTED);meta.setPadding(0,dp(5),0,dp(8));target.addView(meta);
  }

  void renderCompoundWorkflowAsyncV20(LinearLayout target,String goal,CapabilityRouter.Route route){
    final int generation=++routeGenerationV20;showRouteLoadingV20(target,"Building the best workflow…");
    new Thread(()->{ArrayList<Cmd> flow=new ArrayList<>();ArrayList<String> usedCaps=new ArrayList<>();for(String cap:route.capabilities){ArrayList<Cmd> r=rankCapabilityV11(cap,goal,1);if(!r.isEmpty()&&!flow.contains(r.get(0))){flow.add(r.get(0));usedCaps.add(cap);}if(flow.size()>=4)break;}runOnUiThread(()->{if(routeStillValidV20(generation))renderCompoundWorkflowPreparedV20(target,goal,flow,usedCaps);});},"PromptDeckRankFlow").start();
  }

  void renderFallbackPreparedV20(LinearLayout target,String q,ArrayList<Cmd> ranked){
    target.removeAllViews();if(ranked.isEmpty()){LinearLayout e=surface(true);TextView t=text("Describe the outcome in a little more detail, or switch to Browse prompts.",11,false,MUTED);t.setPadding(0,dp(10),0,dp(10));e.addView(t);target.addView(e);return;}TextView best=text("BEST MATCH",10,true,TERTIARY);best.setLetterSpacing(.10f);best.setPadding(0,dp(10),0,dp(5));target.addView(best);target.addView(bestMatchCard(ranked.get(0),q));TextView more=text("MORE MATCHES",10,true,TERTIARY);more.setLetterSpacing(.10f);more.setPadding(0,dp(9),0,dp(5));target.addView(more);for(int i=1;i<Math.min(7,ranked.size());i++){Cmd c=ranked.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}Button allMatches=secondary("View all matches");allMatches.setOnClickListener(v->{discoverMode="browse";discoverCategory="";discoverSubcategory="";discoverFavorites=false;discoverPreset=q;browseLimit=60;home();});target.addView(allMatches);
  }

  void renderFallbackAsyncV20(LinearLayout target,String q){
    final int generation=++routeGenerationV20;showRouteLoadingV20(target,"Searching your prompt library…");new Thread(()->{ArrayList<Cmd> ranked=rankSmart(q,60);runOnUiThread(()->{if(routeStillValidV20(generation))renderFallbackPreparedV20(target,q,ranked);});},"PromptDeckRankFallback").start();
  }

  void renderAskResultsV8(LinearLayout target,String goal){
    target.removeAllViews();String q=goal==null?"":goal.trim();if(q.isEmpty())return;CapabilityRouter.Route route=CapabilityRouter.route(q);
    if(CapabilityRouter.IMAGE.equals(route.domain)&&route.broad&&CapabilityRouter.UNKNOWN.equals(route.mode)){renderImageModeChooserV8(target,q);return;}
    if(route.broad){renderCapabilityChooserV8(target,route.domain,q,route.mode);return;}
    if(CapabilityRouter.IMAGE.equals(route.domain)&&CapabilityRouter.UNKNOWN.equals(route.mode)&&route.capabilities.isEmpty()){renderImageModeChooserV8(target,q);return;}
    if(route.capabilities.size()>=2){renderCompoundWorkflowAsyncV20(target,q,route);return;}
    if(route.capabilities.size()==1){askCapability=route.capabilities.get(0);renderCapabilityRecommendationAsyncV20(target,q,askCapability);return;}
    renderFallbackAsyncV20(target,q);
  }'''

s=s[:start]+replacement+s[end:]

# Avoid expensive ranking in the Browse text watcher on every keystroke; debounce lightly.
old='''q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();browseLimit=30;renderBrowseResultsV6(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});'''
if old in s:
    s=s.replace(old,'''final android.os.Handler browseHandlerV20=new android.os.Handler(android.os.Looper.getMainLooper());final Runnable[] browseTaskV20=new Runnable[1];q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){discoverPreset=x.toString();browseLimit=30;if(browseTaskV20[0]!=null)browseHandlerV20.removeCallbacks(browseTaskV20[0]);final String next=x.toString();browseTaskV20[0]=()->renderBrowseResultsV6(results,next);browseHandlerV20.postDelayed(browseTaskV20[0],180);}public void afterTextChanged(android.text.Editable e){}});''',1)

src.write_text(s,encoding='utf-8')

g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 48',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.9.2-anr-fix'",g,count=1)
gradle.write_text(g,encoding='utf-8')

out=src.read_text(encoding='utf-8')
for token in ['renderCapabilityRecommendationAsyncV20','renderCompoundWorkflowAsyncV20','renderFallbackAsyncV20','PromptDeckRankFlow','routeStillValidV20','versionName']:
    if token not in out: raise SystemExit('ANR gate missing: '+token)
if 'renderCompoundWorkflowV8(target,q,route)' in out or 'renderCapabilityRecommendationV8(target,q,askCapability)' in out:
    raise SystemExit('synchronous Ask routing remains')
if 'versionCode 48' not in gradle.read_text() or "versionName '0.9.2-anr-fix'" not in gradle.read_text(): raise SystemExit('version gate failed')
print('PromptDeck ANR fix v0.9.2 applied')
