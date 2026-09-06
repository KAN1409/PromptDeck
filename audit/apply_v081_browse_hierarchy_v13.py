#!/usr/bin/env python3
from pathlib import Path
import re

JAVA=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
GRADLE=Path('android/app/build.gradle')
s=JAVA.read_text(encoding='utf-8')

def method_span(src, marker):
    start=src.find(marker)
    if start<0: raise SystemExit('missing '+marker)
    brace=src.find('{',start); depth=0; ins=False; esc=False; q=''; i=brace
    while i<len(src):
        ch=src[i]
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

def replace_method(src,marker,block):
    a,b=method_span(src,marker);return src[:a]+block+src[b:]

# Browse is navigation first, prompt list second. Every hierarchy level is a vertical list.
s=replace_method(s,'  void renderBrowseResultsV6(',r'''  void renderBrowseResultsV6(LinearLayout target,String query){
    target.removeAllViews();askSelectionGoal="";String q=query==null?"":query.trim();

    // Level 1: vertical category list. Never dump 3,375 prompts on first entry.
    if(q.isEmpty()&&!discoverFavorites&&discoverCategory.isEmpty()){
      TextView intro=text("Browse by category",15,true,TEXT);intro.setPadding(dp(1),dp(10),0,dp(8));target.addView(intro);
      for(Group g:groups){
        int n=groupCount(g);if(n<=0)continue;
        LinearLayout card=surface(false);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(15),dp(13),dp(13),dp(13));
        LinearLayout copy=vbox();TextView title=text(g.title,15,true,TEXT);TextView sub=text(g.sub,11,false,MUTED);sub.setMaxLines(2);TextView count=text(n+" prompts",10,true,TERTIARY);count.setPadding(0,dp(5),0,0);copy.addView(title);copy.addView(sub);copy.addView(count);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",26,false,MUTED));
        card.setOnClickListener(v->{discoverCategory=g.title;discoverSubcategory="";browseLimit=30;home();});target.addView(card);
      }
      TextView hint=text("Or search above to find a prompt across the entire library.",11,false,MUTED);hint.setPadding(dp(1),dp(8),0,dp(4));target.addView(hint);return;
    }

    // Level 2: vertical subcategory list, same visual language as existing lists.
    if(q.isEmpty()&&!discoverFavorites&&!discoverCategory.isEmpty()&&discoverSubcategory.isEmpty()){
      Button back=ghost("‹  All categories");back.setOnClickListener(v->{discoverCategory="";discoverSubcategory="";browseLimit=30;home();});target.addView(back);
      TextView heading=text(discoverCategory,18,true,TEXT);heading.setPadding(dp(1),dp(8),0,dp(2));target.addView(heading);
      TextView help=text("Choose what you want to do",12,false,MUTED);help.setPadding(dp(1),0,0,dp(8));target.addView(help);
      for(String sub:subcategoriesForV12(discoverCategory)){
        int n=subcategoryCountV12(discoverCategory,sub);if(n<=0)continue;
        LinearLayout card=surface(false);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(15),dp(12),dp(13),dp(12));
        LinearLayout copy=vbox();copy.addView(text(sub,15,true,TEXT));copy.addView(text(n+" prompts",11,false,MUTED));card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",26,false,MUTED));
        card.setOnClickListener(v->{discoverSubcategory=sub;browseLimit=30;home();});target.addView(card);
      }
      return;
    }

    // Level 3: vertical prompt list. Search may enter here directly.
    ArrayList<Cmd> rows=new ArrayList<>();
    if(q.isEmpty()){
      for(Cmd c:all){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }else{
      for(Cmd c:rankSmart(q,350)){if(c.custom)continue;if(discoverFavorites&&!isFavorite(c))continue;if(!discoverCategory.isEmpty()&&!discoverCategory.equals(c.category))continue;if(!discoverSubcategory.isEmpty()&&!discoverSubcategory.equals(c.subcategory))continue;rows.add(c);}
    }
    if(q.isEmpty()&&!discoverSubcategory.isEmpty()){
      Button back=ghost("‹  "+discoverCategory);back.setOnClickListener(v->{discoverSubcategory="";browseLimit=30;home();});target.addView(back);
    }
    String scope=discoverFavorites?"Favorites":discoverCategory.isEmpty()?"Search results":discoverSubcategory.isEmpty()?discoverCategory:discoverCategory+"  ›  "+discoverSubcategory;
    TextView meta=text(scope+"  ·  "+rows.size(),10,true,TERTIARY);meta.setPadding(dp(1),dp(9),0,dp(5));target.addView(meta);
    if(rows.isEmpty()){LinearLayout e=surface(true);TextView t=text("No prompts match this search or filter.",11,false,MUTED);t.setGravity(Gravity.CENTER);t.setPadding(0,dp(15),0,dp(15));e.addView(t);target.addView(e);return;}
    int limit=Math.min(browseLimit,rows.size());for(int i=0;i<limit;i++){Cmd c=rows.get(i);View row=commandRow(c,false);row.setOnClickListener(v->showPromptDialog(c));target.addView(row);}if(limit<rows.size()){Button more=secondary("Show more  ("+(rows.size()-limit)+" remaining)");more.setOnClickListener(v->{browseLimit+=30;home();});target.addView(more);}
  }''')

# Remove the horizontal subcategory chip strip completely from Browse.
a,b=method_span(s,'  void home()');home=s[a:b]
needle='if(!discoverCategory.isEmpty()){HorizontalScrollView subscroll=new HorizontalScrollView(this);'
if needle in home:
    start=home.find(needle); depth=0; brace=home.find('{',start); i=brace
    while i<len(home):
        if home[i]=='{': depth+=1
        elif home[i]=='}':
            depth-=1
            if depth==0:
                home=home[:start]+home[i+1:];break
        i+=1
elif 'HorizontalScrollView subscroll' in home:
    raise SystemExit('unexpected subcategory strip form')
s=s[:a]+home+s[b:]

g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 36',g,count=1)
GRADLE.write_text(g,encoding='utf-8')
JAVA.write_text(s,encoding='utf-8')

for token in ['vertical category list','vertical subcategory list','vertical prompt list','Choose what you want to do','‹  All categories','versionCode 36']:
    hay=s if token!='versionCode 36' else g
    if token not in hay: raise SystemExit('v13 gate missing: '+token)
print('PromptDeck v13 applied: fully vertical Category -> Subcategory -> Prompt hierarchy')
