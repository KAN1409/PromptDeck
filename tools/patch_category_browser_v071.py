#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

new_group=r'''  void group(Group g){group(g,null,"");}

  void group(Group g,String activeSub,String initialQuery){
    page="group"; currentGroup=g;
    base(g.title,g.sub,true);

    EditText search=input("Search inside "+g.title+"…",1);search.setSingleLine(true);search.setImeOptions(EditorInfo.IME_ACTION_SEARCH);search.setText(initialQuery==null?"":initialQuery);root.addView(search);

    ArrayList<Cmd> items=groupCommands(g);
    LinkedHashMap<String,Integer> counts=new LinkedHashMap<>();
    for(Cmd c:items){String sc=groupSubcategory(c,g);counts.put(sc,counts.containsKey(sc)?counts.get(sc)+1:1);}

    HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);
    LinearLayout chips=hbox();chips.setPadding(0,dp(2),dp(4),dp(8));hsv.addView(chips);root.addView(hsv);
    Button allChip=filterChip("All",activeSub==null);allChip.setOnClickListener(v->group(g,null,search.getText().toString()));chips.addView(allChip);
    for(String sc:counts.keySet()){
      Button chip=filterChip(sc,sc.equals(activeSub));chip.setOnClickListener(v->group(g,sc,search.getText().toString()));chips.addView(chip);
    }

    TextView meta=text(items.size()+" prompts  •  "+counts.size()+" subcategories",11,false,MUTED);meta.setPadding(0,0,0,dp(8));root.addView(meta);
    LinearLayout results=vbox();root.addView(results);
    renderGroupResults(g,results,search.getText().toString(),activeSub);

    search.addTextChangedListener(new android.text.TextWatcher(){
      public void beforeTextChanged(CharSequence x,int st,int c,int a){}
      public void onTextChanged(CharSequence x,int st,int b,int c){renderGroupResults(g,results,x.toString(),activeSub);}
      public void afterTextChanged(android.text.Editable e){}
    });

    Button back=ghost("←  Categories");back.setOnClickListener(v->home());root.addView(back);
  }

  ArrayList<Cmd> groupCommands(Group g){
    ArrayList<Cmd> out=new ArrayList<>();LinkedHashSet<Cmd> seen=new LinkedHashSet<>();
    for(String n:g.names){Cmd c=find(n);if(c!=null&&!seen.contains(c)){out.add(c);seen.add(c);}}
    for(Cmd c:all){if(!seen.contains(c)&&c.category.equalsIgnoreCase(g.title)){out.add(c);seen.add(c);}}
    return out;
  }

  String groupSubcategory(Cmd c,Group g){
    if(c.subcategory!=null&&!c.subcategory.trim().isEmpty())return c.subcategory.trim();
    if(c.custom)return"Custom";
    return subcat(c.command,g.title);
  }

  int groupCount(Group g){return groupCommands(g).size();}

  Button filterChip(String label,boolean active){
    Button b=new Button(this);b.setAllCaps(false);b.setText(label);b.setTextSize(11);b.setTextColor(active?Color.WHITE:TEXT);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));b.setSingleLine(true);b.setMinWidth(0);b.setMinHeight(dp(36));b.setPadding(dp(12),0,dp(12),0);b.setBackground(shape(active?ACCENT:SURFACE2,active?ACCENT:BORDER,18));
    LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(36));lp.setMargins(0,0,dp(8),0);b.setLayoutParams(lp);return b;
  }

  void renderGroupResults(Group g,LinearLayout target,String query,String activeSub){
    target.removeAllViews();String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);
    LinkedHashMap<String,ArrayList<Cmd>> subs=new LinkedHashMap<>();
    for(Cmd c:groupCommands(g)){
      String sc=groupSubcategory(c,g);if(activeSub!=null&&!activeSub.equals(sc))continue;
      if(!q.isEmpty()){
        String hay=(c.command+" "+c.description+" "+sc).toLowerCase(Locale.ROOT);
        if(!hay.contains(q))continue;
      }
      if(!subs.containsKey(sc))subs.put(sc,new ArrayList<>());subs.get(sc).add(c);
    }
    int shown=0;for(ArrayList<Cmd> v:subs.values())shown+=v.size();
    if(shown==0){LinearLayout empty=surface(true);TextView e=text("No prompts match this search.",13,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(20),0,dp(20));empty.addView(e);target.addView(empty);return;}
    TextView found=text(shown+" result"+(shown==1?"":"s"),11,false,MUTED);found.setPadding(0,0,0,dp(8));target.addView(found);
    for(Map.Entry<String,ArrayList<Cmd>> en:subs.entrySet()){
      target.addView(section(en.getKey(),en.getValue().size()));
      LinearLayout block=vbox();block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2));block.setPadding(0,dp(2),0,dp(2));
      int i=0;for(Cmd c:en.getValue()){View row=commandRow(c,i++<en.getValue().size()-1);row.setOnClickListener(v->detail(c,g));block.addView(row);}target.addView(block);TextView gap=text("",4,false,MUTED);target.addView(gap);
    }
  }

'''

pat=r'  void group\(Group g\)\{.*?\n  View commandRow\(Cmd c,boolean divider\)\{'
m=re.search(pat,s,re.S)
if not m:
    raise SystemExit('group() block not found')
s=s[:m.start()]+new_group+'  View commandRow(Cmd c,boolean divider){'+s[m.end():]

# Show actual integrated prompt counts on category cards.
s=s.replace('''LinearLayout copy=vbox();TextView title=text(g.title,17,true,TEXT);TextView sub=text(g.sub,13,false,MUTED);copy.addView(title);copy.addView(sub);''',
'''LinearLayout copy=vbox();TextView title=text(g.title,17,true,TEXT);TextView sub=text(g.sub+"  •  "+groupCount(g)+" prompts",13,false,MUTED);copy.addView(title);copy.addView(sub);''',1)

# Add-more page should use the same integrated categories rather than only the named built-ins.
old=r'''    root.addView(label("ALL COMMANDS"));
    for(Group g:groups){
      TextView gh=section(g.title,availableCount(g));root.addView(gh);
      LinearLayout block=vbox();block.setBackground(satinShape(SATIN_TOP,SATIN_BOTTOM,SATIN_EDGE,12));block.setElevation(dp(2));block.setPadding(0,dp(2),0,dp(2));
      int shown=0,total=availableCount(g);
      for(String n:g.names){
        Cmd c=find(n);if(c==null)continue;
        boolean divider=shown<total-1;View row=pickCommandRow(c,divider);block.addView(row);shown++;
      }
      root.addView(block);spacer(10);
    }
'''
new=r'''    root.addView(label("BROWSE BY CATEGORY"));
    for(Group g:groups){
      int total=groupCount(g);if(total==0)continue;
      View card=menuCard(g.icon,g.title,total+" prompts");card.setOnClickListener(v->group(g));root.addView(card);
    }
'''
if old in s:s=s.replace(old,new,1)

# The separate PromptLibrary activity is no longer part of the user navigation.
s=s.replace('''    if("group".equals(page)||"library".equals(page)){home();return;}''','''    if("group".equals(page)||"library".equals(page)){home();return;}''',1)

if re.search(r'[\u0600-\u06FF]',s):
    hits=[]
    for i,line in enumerate(s.splitlines(),1):
        if re.search(r'[\u0600-\u06FF]',line):hits.append(f'{i}: {line[:180]}')
    raise SystemExit('Arabic UI text remains:\n'+'\n'.join(hits[:30]))

p.write_text(s,encoding='utf-8')
print('PromptDeck v0.7.1 category browser patch applied')
