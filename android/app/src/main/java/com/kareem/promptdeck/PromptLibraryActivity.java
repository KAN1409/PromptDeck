package com.kareem.promptdeck;

import android.app.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.*;
import android.view.inputmethod.EditorInfo;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class PromptLibraryActivity extends Activity {
  static final int BG=Color.rgb(8,10,14), SURFACE=Color.rgb(18,21,27), SURFACE2=Color.rgb(25,29,37), BORDER=Color.rgb(47,54,66);
  static final int TEXT=Color.rgb(248,249,251), MUTED=Color.rgb(143,152,168), ACCENT=Color.rgb(47,107,255);
  static class Item {
    int id; String title,prompt,category,subcategory,description;
    Item(JSONObject o){id=o.optInt("id");title=o.optString("title");prompt=o.optString("prompt");category=o.optString("category","Other Expert Roles");subcategory=o.optString("subcategory","");description=o.optString("description","");}
  }

  final ArrayList<Item> all=new ArrayList<>(), filtered=new ArrayList<>();
  final LinkedHashSet<String> categories=new LinkedHashSet<>();
  LinearLayout root, chips;
  ListView list;
  PromptAdapter adapter;
  EditText search;
  TextView count;
  String activeCategory="All";
  Item current;

  @Override public void onCreate(Bundle b){super.onCreate(b);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);load();showBrowser();}
  @Override public void onBackPressed(){if(current!=null){current=null;showBrowser();}else super.onBackPressed();}

  void load(){
    all.clear(); categories.clear();
    try{
      String raw=readAsset("prompts_library.json");
      JSONArray a=new JSONArray(raw);
      for(int i=0;i<a.length();i++){Item x=new Item(a.getJSONObject(i));if(x.title.isEmpty()||x.prompt.isEmpty())continue;all.add(x);categories.add(x.category);}
    }catch(Exception e){Toast.makeText(this,"Prompt Library could not be loaded",Toast.LENGTH_LONG).show();}
  }

  void showBrowser(){
    current=null;
    ScrollView outer=new ScrollView(this);outer.setFillViewport(true);outer.setBackgroundColor(BG);
    root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(20),dp(18),dp(20),dp(20));outer.addView(root,new ScrollView.LayoutParams(-1,-1));
    LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);
    TextView back=text("‹",34,false,TEXT);back.setGravity(Gravity.CENTER);back.setOnClickListener(v->finish());top.addView(back,new LinearLayout.LayoutParams(dp(42),dp(46)));
    LinearLayout titles=new LinearLayout(this);titles.setOrientation(LinearLayout.VERTICAL);
    titles.addView(text("Prompt Library",24,true,TEXT));titles.addView(text("2,160 full prompts • categorized and searchable",12,false,MUTED));
    top.addView(titles,new LinearLayout.LayoutParams(0,-2,1));root.addView(top);

    search=new EditText(this);search.setHint("Search prompts, roles or topics…");search.setHintTextColor(MUTED);search.setTextColor(TEXT);search.setSingleLine(true);search.setTextSize(15);search.setPadding(dp(16),0,dp(16),0);search.setBackground(round(SURFACE,BORDER,13));search.setImeOptions(EditorInfo.IME_ACTION_SEARCH);
    LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(52));sp.setMargins(0,dp(18),0,dp(12));root.addView(search,sp);

    HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);chips=new LinearLayout(this);chips.setOrientation(LinearLayout.HORIZONTAL);hsv.addView(chips);root.addView(hsv,new LinearLayout.LayoutParams(-1,dp(48)));
    rebuildChips();

    count=text("",12,false,MUTED);count.setPadding(dp(2),dp(8),0,dp(8));root.addView(count);

    list=new ListView(this);list.setDividerHeight(0);list.setBackgroundColor(Color.TRANSPARENT);list.setVerticalScrollBarEnabled(false);adapter=new PromptAdapter(this,filtered);list.setAdapter(adapter);list.setOnItemClickListener((p,v,pos,id)->showDetail(filtered.get(pos)));
    root.addView(list,new LinearLayout.LayoutParams(-1,dp(620)));
    setContentView(outer);

    search.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int a){}public void onTextChanged(CharSequence s,int st,int b,int c){applyFilter();}public void afterTextChanged(Editable e){}});
    applyFilter();
  }

  void rebuildChips(){
    chips.removeAllViews();addChip("All");for(String c:categories)addChip(c);
  }
  void addChip(String name){
    TextView x=text(name,12,true,name.equals(activeCategory)?Color.WHITE:TEXT);x.setGravity(Gravity.CENTER);x.setPadding(dp(14),0,dp(14),0);x.setBackground(round(name.equals(activeCategory)?ACCENT:SURFACE,BORDER,18));x.setOnClickListener(v->{activeCategory=name;rebuildChips();applyFilter();});
    LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-2,dp(36));p.setMargins(0,dp(4),dp(8),dp(4));chips.addView(x,p);
  }

  void applyFilter(){
    String q=search==null?"":search.getText().toString().trim().toLowerCase(Locale.ROOT);filtered.clear();
    for(Item x:all){if(!activeCategory.equals("All")&&!x.category.equals(activeCategory))continue;if(!q.isEmpty()){String hay=(x.title+" "+x.category+" "+x.subcategory+" "+x.description+" "+x.prompt).toLowerCase(Locale.ROOT);if(!hay.contains(q))continue;}filtered.add(x);}
    if(count!=null)count.setText(filtered.size()+" prompt"+(filtered.size()==1?"":"s")+(activeCategory.equals("All")?"":" in "+activeCategory));if(adapter!=null)adapter.notifyDataSetChanged();
  }

  void showDetail(Item x){
    current=x;ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(20),dp(18),dp(20),dp(28));sv.addView(box);
    TextView back=text("‹  Prompt Library",14,true,ACCENT);back.setPadding(0,dp(4),0,dp(18));back.setOnClickListener(v->{current=null;showBrowser();});box.addView(back);
    box.addView(text(x.title,27,true,TEXT));TextView meta=text(x.category+(x.subcategory.isEmpty()?"":"  •  "+x.subcategory),12,true,ACCENT);meta.setPadding(0,dp(8),0,dp(18));box.addView(meta);
    if(!x.description.isEmpty()){TextView d=text(x.description,15,false,MUTED);d.setLineSpacing(0,1.18f);d.setPadding(0,0,0,dp(18));box.addView(d);}
    TextView label=text("FULL PROMPT",11,true,ACCENT);label.setLetterSpacing(.12f);label.setPadding(0,dp(4),0,dp(8));box.addView(label);
    TextView prompt=text(x.prompt,15,false,TEXT);prompt.setTextIsSelectable(true);prompt.setLineSpacing(0,1.18f);prompt.setPadding(dp(16),dp(16),dp(16),dp(16));prompt.setBackground(round(SURFACE,BORDER,14));box.addView(prompt,new LinearLayout.LayoutParams(-1,-2));
    Button add=button("Add to Prompt Stack",ACCENT,Color.WHITE);add.setOnClickListener(v->{Intent data=new Intent();data.putExtra("library_title",x.title);data.putExtra("library_prompt",x.prompt);data.putExtra("library_category",x.category);data.putExtra("library_subcategory",x.subcategory);setResult(RESULT_OK,data);finish();});LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(-1,dp(54));ap.setMargins(0,dp(18),0,dp(10));box.addView(add,ap);
    Button copy=button("Copy prompt",SURFACE2,TEXT);copy.setOnClickListener(v->{((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText(x.title,x.prompt));Toast.makeText(this,"Prompt copied",Toast.LENGTH_SHORT).show();});box.addView(copy,new LinearLayout.LayoutParams(-1,dp(50)));
    setContentView(sv);
  }

  class PromptAdapter extends BaseAdapter {
    final Context ctx; final ArrayList<Item> data; PromptAdapter(Context c,ArrayList<Item>d){ctx=c;data=d;}
    public int getCount(){return data.size();}public Object getItem(int p){return data.get(p);}public long getItemId(int p){return data.get(p).id;}
    public View getView(int p,View convert,android.view.ViewGroup parent){
      LinearLayout row;if(convert instanceof LinearLayout)row=(LinearLayout)convert;else{row=new LinearLayout(ctx);row.setOrientation(LinearLayout.VERTICAL);row.setPadding(dp(16),dp(14),dp(16),dp(14));}
      row.removeAllViews();Item x=data.get(p);TextView t=text(x.title,16,true,TEXT);row.addView(t);TextView m=text(x.category+(x.subcategory.isEmpty()?"":"  •  "+x.subcategory),11,true,ACCENT);m.setPadding(0,dp(4),0,dp(5));row.addView(m);TextView d=text(x.description,13,false,MUTED);d.setMaxLines(2);row.addView(d);row.setBackground(round(SURFACE,BORDER,13));AbsListView.LayoutParams lp=new AbsListView.LayoutParams(-1,dp(102));row.setLayoutParams(lp);return row;
    }
  }

  TextView text(String s,int size,boolean bold,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);t.setTypeface(Typeface.create("sans",bold?Typeface.BOLD:Typeface.NORMAL));t.setGravity(Gravity.START);t.setTextDirection(View.TEXT_DIRECTION_LTR);return t;}
  Button button(String s,int fill,int color){Button b=new Button(this);b.setText(s);b.setTextColor(color);b.setTextSize(14);b.setAllCaps(false);b.setTypeface(Typeface.DEFAULT_BOLD);b.setBackground(round(fill,BORDER,14));return b;}
  GradientDrawable round(int fill,int stroke,int radius){GradientDrawable g=new GradientDrawable();g.setColor(fill);g.setCornerRadius(dp(radius));g.setStroke(dp(1),stroke);return g;}
  int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
  String readAsset(String n)throws Exception{InputStream in=getAssets().open(n);ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buf=new byte[8192];int r;while((r=in.read(buf))>0)b.write(buf,0,r);in.close();return b.toString("UTF-8");}
}
