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

def replace_method(s, marker, block):
    a,b=method_span(s,marker)
    return s[:a]+block+s[b:]

def insert_before(s, marker, block):
    p=s.find(marker)
    if p<0: raise SystemExit('anchor missing: '+marker)
    return s[:p]+block+s[p:]

s=JAVA.read_text(encoding='utf-8')
if 'String discoverMode="landing";' not in s:
    raise SystemExit('v6 hybrid state missing')

# Interactive ranking must never scan multi-kilobyte prompt bodies on the UI thread.
s=replace_method(s,'  ArrayList<Cmd> rankSmart(',r'''  ArrayList<Cmd> rankSmart(String query,int limit){
    final String expanded=expandIntent(query==null?"":query);final String[] toks=expanded.toLowerCase(Locale.ROOT).split("\\s+");ArrayList<Cmd> candidates=new ArrayList<>();final HashMap<Cmd,Integer> scores=new HashMap<>();
    for(Cmd c:all){int score=fastSmartScore(c,toks);if(score>0){candidates.add(c);scores.put(c,score);}}
    Collections.sort(candidates,(a,b)->{int sa=scores.get(a),sb=scores.get(b);if(sa!=sb)return Integer.compare(sb,sa);return displayTitle(a).compareToIgnoreCase(displayTitle(b));});
    if(candidates.size()<=limit)return candidates;return new ArrayList<>(candidates.subList(0,limit));
  }''')

# Remove the legacy scorer completely so no future path can accidentally re-enable full-body scanning.
legacy='  int smartScore(Cmd c,String expanded)'
if legacy in s:
    a,b=method_span(s,legacy)
    s=s[:a]+s[b:]

fast_helpers=r'''  int fastSmartScore(Cmd c,String[] toks){
    String command=c.command==null?"":c.command.toLowerCase(Locale.ROOT);String title=displayTitle(c).toLowerCase(Locale.ROOT);String desc=c.description==null?"":c.description.toLowerCase(Locale.ROOT);String cat=c.category==null?"":c.category.toLowerCase(Locale.ROOT);String sub=c.subcategory==null?"":c.subcategory.toLowerCase(Locale.ROOT);int score=0,matched=0;
    for(String t:toks){if(t==null||t.length()<2)continue;boolean hit=false;if(command.equals(t)){score+=16;hit=true;}else if(command.contains(t)){score+=9;hit=true;}if(title.contains(t)){score+=11;hit=true;}if(desc.contains(t)){score+=6;hit=true;}if(cat.contains(t)){score+=5;hit=true;}if(sub.contains(t)){score+=3;hit=true;}if(hit)matched++;}
    if(matched>=2)score+=matched*4;if(recentIdSet().contains(c.id))score+=2;return score;
  }
  void hideKeyboard(View v){try{android.view.inputmethod.InputMethodManager imm=(android.view.inputmethod.InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);if(imm!=null)imm.hideSoftInputFromWindow(v.getWindowToken(),0);}catch(Exception ignored){}}
  void runAskRecommendation(LinearLayout target,EditText goal){
    askGoal=goal.getText().toString().trim();if(askGoal.length()<2){toast("Describe what you want first");return;}contextDraft=askGoal;hideKeyboard(goal);
    try{renderAskResults(target,askGoal);}catch(Exception e){target.removeAllViews();LinearLayout box=surface(true);TextView title=text("Couldn't build a recommendation",12,true,TEXT);TextView sub=text("Try a shorter description, or switch to Browse prompts.",10,false,MUTED);title.setPadding(0,dp(8),0,dp(2));sub.setPadding(0,0,0,dp(8));box.addView(title);box.addView(sub);target.addView(box);}
  }

'''
if 'int fastSmartScore(Cmd c,String[] toks)' not in s:
    s=insert_before(s,'  String expandIntent(',fast_helpers)

# The hybrid workspace has its own explicit back-state. Ask/Browse -> landing -> exit.
s=replace_method(s,'  @Override public void onBackPressed()',r'''  @Override public void onBackPressed(){
    if(!"landing".equals(discoverMode)){discoverMode="landing";discoverCategory="";discoverFavorites=false;discoverPreset="";browseLimit=30;home();return;}
    super.onBackPressed();
  }''')

# Route the Ask CTA through the guarded, lightweight recommendation path.
old='find.setOnClickListener(v->{askGoal=goal.getText().toString().trim();contextDraft=askGoal;renderAskResults(results,askGoal);});'
new='find.setOnClickListener(v->runAskRecommendation(results,goal));'
if old not in s: raise SystemExit('Ask click listener anchor missing')
s=s.replace(old,new,1)

# Pressing enter from the Ask field runs the same action instead of doing nothing.
anchor='goal.setMaxLines(5);goal.setText(askGoal);root.addView(goal);Button find=primary("Find the best approach");'
if anchor not in s: raise SystemExit('Ask field anchor missing')
s=s.replace(anchor,'goal.setMaxLines(5);goal.setImeOptions(EditorInfo.IME_ACTION_DONE);goal.setText(askGoal);root.addView(goal);Button find=primary("Find the best approach");',1)
anchor2='find.setOnClickListener(v->runAskRecommendation(results,goal));return;}'
if anchor2 not in s: raise SystemExit('Ask listener tail missing')
s=s.replace(anchor2,'find.setOnClickListener(v->runAskRecommendation(results,goal));goal.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){runAskRecommendation(results,goal);return true;}return false;});return;}',1)

# Version bump for runtime-fix build.
g=GRADLE.read_text(encoding='utf-8');g=re.sub(r'versionCode\s+\d+','versionCode 30',g,count=1);GRADLE.write_text(g,encoding='utf-8')

required=['fastSmartScore(Cmd c,String[] toks)','runAskRecommendation(LinearLayout target,EditText goal)','if(!"landing".equals(discoverMode))','versionCode 30']
for token in required:
    hay=s if token!='versionCode 30' else g
    if token not in hay: raise SystemExit('v7 stability gate missing: '+token)
ra,rb=method_span(s,'  ArrayList<Cmd> rankSmart(')
fa,fb=method_span(s,'  int fastSmartScore(')
active_rank=s[ra:rb]+s[fa:fb]
if 'instruction' in active_rank or 'body.contains' in active_rank or 'smartScore(' in active_rank.replace('fastSmartScore(',''):
    raise SystemExit('full prompt body scorer still used by active interactive ranking methods')
JAVA.write_text(s,encoding='utf-8');GRADLE.write_text(g,encoding='utf-8')
print('v0.8.1 runtime stability v7 applied: lightweight ranker + explicit hybrid back navigation')
