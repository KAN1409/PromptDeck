#!/usr/bin/env python3
from pathlib import Path
import base64, importlib.util, json, re, tempfile

ROOT=Path('.')
JAVA=ROOT/'android/app/src/main/java/com/kareem/promptdeck/MainActivity.java'
ASSETS=ROOT/'android/app/src/main/assets'
GRADLE=ROOT/'android/app/build.gradle'
DATA=ROOT/'audit/chatgpt_native_final_data'
FINAL_ASSET=ASSETS/'chatgpt_native_final.json'

# ---------- helpers ----------
def method_span(s, marker):
    start=s.find(marker)
    if start < 0:
        raise SystemExit(f'method marker missing: {marker}')
    brace=s.find('{', start)
    if brace < 0:
        raise SystemExit(f'opening brace missing: {marker}')
    depth=0
    i=brace
    in_str=False
    esc=False
    quote=''
    while i < len(s):
        ch=s[i]
        if in_str:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: in_str=False
        else:
            if ch in ('"', "'"):
                in_str=True; quote=ch
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:
                    return start,i+1
        i+=1
    raise SystemExit(f'unclosed method: {marker}')

def replace_method(s, marker, new_block):
    a,b=method_span(s,marker)
    return s[:a]+new_block+s[b:]

def insert_before(s, marker, block):
    p=s.find(marker)
    if p<0: raise SystemExit(f'insert marker missing: {marker}')
    return s[:p]+block+s[p:]

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def clean(x): return re.sub(r'\s+',' ',str(x or '')).strip()
def library_slug(title):
    x=re.sub(r'(?i)^act as (an? )?','',title or '')
    x=re.sub(r'[^A-Za-z0-9]+','',x).strip() or 'ExpertPrompt'
    return x[:38]

# ---------- reconstruct staged semantic curation module ----------
chunks=[]
for p in sorted(DATA.glob('curation_*.b64')):
    chunks.append(p.read_text(encoding='utf-8').strip())
if not chunks:
    raise SystemExit('curation chunks missing')
raw=base64.b64decode(''.join(chunks))
module_path=Path(tempfile.gettempdir())/'promptdeck_curation_v081.py'
module_path.write_bytes(raw)
spec=importlib.util.spec_from_file_location('promptdeck_curation_v081',module_path)
cur=importlib.util.module_from_spec(spec);spec.loader.exec_module(cur)

def cset(*names):
    for n in names:
        if hasattr(cur,n): return set(getattr(cur,n))
    return set()
def cmap(*names):
    for n in names:
        if hasattr(cur,n): return dict(getattr(cur,n))
    return {}

REMOVE_IDS=cset('REMOVE_IDS')
CONVERT_IDS=cset('CONVERT_IDS')
REWRITE_IDS=cset('REWRITE_IDS')
STACK_IDS=cset('STACK_IDS','STACK_LIMITED_IDS')
RAW_AGENT_IDS=cset('RAW_AGENT_IDS','RAW_SKILL_IDS','RAW_AGENT_SKILL_IDS')
OVERENGINEERED_IDS=cset('OVERENGINEERED_IDS','VERY_LONG_IDS')
LEGACY_METADATA_IDS=cset('LEGACY_METADATA_IDS')
COT_REF_IDS=cset('COT_REF_IDS')
REASONING_MICRO_IDS=cset('REASONING_MICRO_IDS','REASONING_MICROMANAGEMENT_IDS')
EXTERNAL_TARGET_IDS=cset('EXTERNAL_TARGET_IDS','KEEP_EXTERNAL_TARGET_IDS')
CUSTOM_BY_ID=cmap('CUSTOM_BY_ID')
RENAME_BY_ID=cmap('RENAME_BY_ID')
DESC_BY_ID=cmap('DESC_BY_ID')

# Fallback semantic transformations if the staged module does not expose helpers.
def fallback_sanitize_reasoning(t):
    t=re.sub(r'(?is)\b(?:show|reveal|write out|provide|display)\s+(?:your\s+)?(?:full\s+)?(?:chain[- ]of[- ]thought|internal reasoning|reasoning process)\b[^.\n]*[.\n]?','',t)
    t=re.sub(r'(?is)\bthink step[- ]by[- ]step\b','reason carefully',t)
    return t.strip()

def fallback_sanitize(t, external_runtime=False, preserve=False):
    x=t
    if not preserve:
        x=re.sub(r'(?im)^\s*(?:---|name:|description:|version:|author:|license:|metadata:|changelog:).*$','',x)
        x=re.sub(r'(?i)\b(?:Claude Code|Claude Desktop|Anthropic Console|Gemini CLI|Cursor rules?|\.claude|CLAUDE\.md|SKILL\.md)\b','ChatGPT',x)
        x=re.sub(r'(?i)\b(?:use|invoke|call)\s+(?:the\s+)?(?:Claude|Gemini|Cursor)\s+(?:tool|runtime|agent|CLI)\b','use an available ChatGPT capability',x)
    x=fallback_sanitize_reasoning(x)
    x=re.sub(r'\n{4,}','\n\n',x).strip()
    return x

def fallback_concise(r,preserve=False,external_runtime=False):
    title=clean(r.get('description')) or clean(r.get('command')) or 'this specialist task'
    body=fallback_sanitize(r.get('instruction',''),external_runtime,preserve)
    # Preserve unique requirements, but remove giant imported wrappers.
    paras=[clean(p) for p in re.split(r'\n\s*\n',body) if clean(p)]
    useful=[]
    for p in paras:
        low=p.lower()
        if any(k in low for k in ('author:','version:','changelog:','installation','directory structure','skill.md','claude.md')): continue
        useful.append(p)
        if sum(len(z) for z in useful)>2600: break
    core='\n\n'.join(useful)[:3600].strip()
    if not core:
        core=f'Handle the user request as an expert in {title}. Identify the goal, important constraints and required evidence, then produce a practical, accurate result.'
    return core

sanitize=getattr(cur,'sanitize',fallback_sanitize)
sanitize_reasoning=getattr(cur,'sanitize_reasoning',fallback_sanitize_reasoning)
concise=getattr(cur,'concise',fallback_concise)
card_desc=getattr(cur,'card_desc',lambda text,cmd: (clean(text).split('.')[0][:120] or clean(cmd)))

# ---------- build exact ID-indexed source map ----------
def records_from_assets():
    out={}
    def add(i,command,description,instruction):
        try:i=int(i)
        except:return
        if i<=0:return
        out[i]={'id':i,'command':str(command or ''),'description':str(description or ''),'instruction':str(instruction or '')}
    for o in read_json(ASSETS/'commands.json'):
        add(o.get('id'),o.get('command'),o.get('description',o.get('description_ar','')),o.get('instruction'))
    for i,x in enumerate(read_json(ASSETS/'prompts_library.json')):
        add(30000+i,library_slug(str(x.get('title',''))),x.get('description',x.get('title','')),x.get('prompt',''))
    for i,x in enumerate(read_json(ASSETS/'curated_photo_prompts.json')):
        add(x.get('id',50000+i),x.get('command'),x.get('description',''),x.get('instruction',''))
    for i,x in enumerate(read_json(ASSETS/'imported_pdf_prompts.json')):
        add(60000+i,library_slug(str(x.get('title',''))),x.get('description',x.get('title','')),x.get('prompt',''))
    for i,x in enumerate(read_json(ASSETS/'daily_gap_prompts_100.json')):
        add(x.get('id',70000+i),x.get('command'),x.get('description',''),x.get('instruction',''))
    return out

records=records_from_assets()
overrides=[]
for i,r in records.items():
    if i in REMOVE_IDS: continue
    orig=r['instruction']
    preserve=i in EXTERNAL_TARGET_IDS
    external_runtime=bool(re.search(r'(?i)\b(?:claude|anthropic|gemini|cursor|copilot|grok|llama|mistral|deepseek)\b',orig)) and not preserve
    compact=(i in RAW_AGENT_IDS or i in OVERENGINEERED_IDS or i in LEGACY_METADATA_IDS or len(orig)>15000)
    new=orig; changed=False
    if i in CUSTOM_BY_ID:
        new=str(CUSTOM_BY_ID[i]).strip();changed=True
    elif compact:
        try:new=concise(r,preserve,external_runtime)
        except TypeError:new=concise(r)
        changed=True
    elif i in CONVERT_IDS or i in REWRITE_IDS:
        try:new=sanitize(orig,external_runtime,preserve)
        except TypeError:new=sanitize(orig)
        if external_runtime and not preserve:
            new += '\n\nUse only ChatGPT capabilities and tools that are actually available in the current conversation. If a referenced external environment is unavailable, state that briefly and continue with a practical ChatGPT-native alternative.'
        if i in COT_REF_IDS or i in REASONING_MICRO_IDS:
            new += '\n\nDo not expose private chain-of-thought. Provide concise rationale, assumptions, evidence or verification instead.'
        changed=True
    elif i in STACK_IDS:
        try:core=sanitize(orig,external_runtime,preserve)
        except TypeError:core=sanitize(orig)
        new='For this step in a larger workflow:\n'+core+'\n\nApply these instructions only to this step. Do not override or block later steps in the PromptDeck stack.'
        changed=True
    elif re.search(r'(?i)\b(chain[- ]of[- ]thought|show your reasoning|make your reasoning explicit|think step[- ]by[- ]step|internal reasoning|reasoning process)\b',orig):
        x=sanitize_reasoning(orig)
        if x!=orig:
            new=x+'\n\nDo not expose private chain-of-thought; provide concise rationale or evidence instead.';changed=True
    newcmd=RENAME_BY_ID.get(i,r['command'])
    ov={'match_id':i}
    if newcmd and newcmd!=r['command']: ov['command']=newcmd
    if changed:
        ov['instruction']=re.sub(r'\n{4,}','\n\n',new).strip()
        ov['description']=DESC_BY_ID.get(i,card_desc(ov['instruction'],newcmd or r['command']))
    elif i in DESC_BY_ID:
        ov['description']=DESC_BY_ID[i]
    if len(ov)>1: overrides.append(ov)

expected=3375
pack={
    'format':'promptdeck-chatgpt-native-final',
    'version':1,
    'source_canonical_count':3388,
    'expected_builtin_count':expected,
    'remove_ids':sorted(REMOVE_IDS),
    'overrides':overrides,
}
FINAL_ASSET.write_text(json.dumps(pack,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('Final curation asset:',len(overrides),'overrides,',len(REMOVE_IDS),'removals')

# ---------- patch Java ----------
s=JAVA.read_text(encoding='utf-8')

# Locked visual tokens.
s=re.sub(r'static final int BG=.*?;\n  static final int TEXT=.*?;\n  static final int SATIN_TOP=.*?;',
'''static final int BG=Color.rgb(7,17,29), SURFACE=Color.rgb(13,26,42), SURFACE2=Color.rgb(18,34,53), INPUT=Color.rgb(19,35,56), BORDER=Color.rgb(36,54,76), DIVIDER=Color.rgb(29,44,64);\n  static final int TEXT=Color.rgb(243,247,253), MUTED=Color.rgb(166,181,200), TERTIARY=Color.rgb(126,144,167), ACCENT=Color.rgb(44,123,255), PURPLE=Color.rgb(107,93,255), SUCCESS=Color.rgb(79,213,139), FAVORITE=Color.rgb(255,204,77);\n  static final int SATIN_TOP=Color.rgb(18,34,53), SATIN_BOTTOM=Color.rgb(13,26,42), SATIN_EDGE=Color.rgb(36,54,76);''',s,count=1,flags=re.S)

if 'promptVars=new HashMap' not in s:
    s=s.replace('String page="home"; Group currentGroup=null; String contextDraft="";',
                'String page="home"; Group currentGroup=null; String contextDraft=""; HashMap<Integer,HashMap<String,String>> promptVars=new HashMap<>();')

# Apply semantic asset after prior canonical consolidation.
if 'applyChatGPTNativeFinal();' not in s:
    s=s.replace('englishizeDescriptions();canonicalizeLibrary();}', 'englishizeDescriptions();canonicalizeLibrary();applyChatGPTNativeFinal();}',1)

semantic_java=r'''  void applyChatGPTNativeFinal(){
    try{
      JSONObject pack=new JSONObject(readAsset("chatgpt_native_final.json"));
      HashSet<Integer> remove=new HashSet<>();JSONArray rr=pack.optJSONArray("remove_ids");if(rr!=null)for(int i=0;i<rr.length();i++)remove.add(rr.optInt(i));
      HashMap<Integer,JSONObject> edits=new HashMap<>();JSONArray oo=pack.optJSONArray("overrides");if(oo!=null)for(int i=0;i<oo.length();i++){JSONObject o=oo.optJSONObject(i);if(o!=null)edits.put(o.optInt("match_id",-1),o);}
      Iterator<Cmd> it=all.iterator();while(it.hasNext()){
        Cmd c=it.next();if(c.custom)continue;if(remove.contains(c.id)){it.remove();continue;}JSONObject o=edits.get(c.id);if(o==null)continue;
        if(o.has("command")){String n=Cmd.clean(o.optString("command",c.command));if(!n.isEmpty())c.command=n;}
        if(o.has("description")){String d=o.optString("description",c.description).trim();if(!d.isEmpty())c.description=d;}
        if(o.has("instruction")){String x=o.optString("instruction",c.instruction).trim();if(!x.isEmpty())c.instruction=x;}
      }
      HashSet<String> seen=new HashSet<>();it=all.iterator();while(it.hasNext()){Cmd c=it.next();if(c.custom)continue;String k=normalizePrompt(c.instruction);if(!seen.add(k))it.remove();}
      int built=0;for(Cmd c:all)if(!c.custom)built++;int expected=pack.optInt("expected_builtin_count",-1);if(expected>0&&built!=expected)throw new RuntimeException("Canonical prompt count "+built+" != "+expected);
    }catch(Exception e){throw new RuntimeException("ChatGPT-native final pack failed",e);}
  }

'''
if 'void applyChatGPTNativeFinal(){' not in s:
    s=insert_before(s,'  void loadCommunityPrompts(){',semantic_java)

# Back behavior for new shell.
s=replace_method(s,'  @Override public void onBackPressed()',r'''  @Override public void onBackPressed(){
    if("stack".equals(page)){home();return;}
    if("addMore".equals(page)||"build".equals(page)){stack();return;}
    if("group".equals(page)){browseCategories();return;}
    if("categories".equals(page)||"search".equals(page)||"discover".equals(page)||"settings".equals(page)||"library".equals(page)){home();return;}
    if("detail".equals(page)){if(currentGroup!=null)group(currentGroup);else searchPage();return;}
    if("customDetail".equals(page)){library();return;}
    super.onBackPressed();
  }''')

# Fixed-shell base with persistent five-item bottom navigation.
s=replace_method(s,'  void base(',r'''  void base(String title,String sub,boolean showStack){
    LinearLayout shell=vbox();shell.setBackgroundColor(BG);
    ScrollView sv=new ScrollView(this);sv.setFillViewport(true);sv.setBackgroundColor(BG);sv.setClipToPadding(false);
    root=vbox();root.setPadding(dp(16),dp(10),dp(16),dp(22));root.setClipChildren(false);root.setClipToPadding(false);sv.addView(root);
    LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,0,1);shell.addView(sv,sp);
    shell.addView(bottomNav(),new LinearLayout.LayoutParams(-1,dp(68)));setContentView(shell);
    sv.setOnApplyWindowInsetsListener((v,insets)->{int top=insets.getSystemWindowInsetTop();root.setPadding(dp(16),top+dp(8),dp(16),dp(22));return insets;});sv.requestApplyInsets();

    LinearLayout top=hbox();top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(0,0,0,dp(4));
    if("detail".equals(page)||"group".equals(page)||"categories".equals(page)||"customDetail".equals(page)){
      Button back=navBack("‹");back.setOnClickListener(v->{if("detail".equals(page)&&currentGroup!=null)group(currentGroup);else if("group".equals(page))browseCategories();else if("customDetail".equals(page))library();else home();});
      LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(dp(38),dp(36));bp.setMargins(0,0,dp(8),0);top.addView(back,bp);
    }
    TextView logo=text("◆",19,true,Color.rgb(61,130,255));logo.setGravity(Gravity.CENTER);top.addView(logo,new LinearLayout.LayoutParams(dp(30),dp(34)));
    TextView brand=text("PromptDeck",16,true,TEXT);brand.setGravity(Gravity.CENTER_VERTICAL);top.addView(brand,new LinearLayout.LayoutParams(0,dp(34),1));
    if("home".equals(page)){Button gear=navBack("⚙");gear.setOnClickListener(v->settings());top.addView(gear,new LinearLayout.LayoutParams(dp(40),dp(36)));}
    else if(showStack){TextView stack=pill(selected.isEmpty()?"STACK":"STACK  "+selected.size());stack.setOnClickListener(v->stack());top.addView(stack);}
    root.addView(top);
    if(title!=null&&!title.isEmpty()){TextView ttl=text(title,26,true,TEXT);ttl.setPadding(0,dp(10),0,dp(3));ttl.setGravity(Gravity.START);root.addView(ttl);}
    if(sub!=null&&!sub.isEmpty()){TextView st=text(sub,13,false,MUTED);st.setLineSpacing(0,1.10f);st.setPadding(0,0,0,dp(12));st.setGravity(Gravity.START);root.addView(st);}
  }''')

# Discovery-first Home matching approved composition.
s=replace_method(s,'  void home()',r'''  void home(){
    page="home";currentGroup=null;base("Find the right prompt","What do you want to do?",false);
    EditText discover=input("e.g. plan a trip, write a resume, explain a topic...",1);discover.setSingleLine(true);discover.setImeOptions(EditorInfo.IME_ACTION_SEARCH);root.addView(discover);
    LinearLayout live=vbox();live.setVisibility(View.GONE);root.addView(live);
    discover.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderSmartSearch(live,x.toString());}public void afterTextChanged(android.text.Editable e){}});

    root.addView(sectionTitle("Quick Goals",null));
    LinearLayout r1=hbox();r1.addView(goalTile("✎","Write or rewrite","writing rewrite text",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(0,dp(88),1));spacerH(r1);r1.addView(goalTile("⌕","Research something","research analysis verify sources",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(0,dp(88),1));spacerH(r1);r1.addView(goalTile("◈","Think & decide","brainstorm decision critique ideas",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(0,dp(88),1));root.addView(r1);
    spacer(8);
    LinearLayout r2=hbox();r2.addView(goalTile("▣","Plan something","plan roadmap checklist execution",Color.rgb(96,92,255)),new LinearLayout.LayoutParams(0,dp(88),1));spacerH(r2);r2.addView(goalTile("▤","Learn something","learn explain teach study",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(0,dp(88),1));spacerH(r2);r2.addView(goalTile("⚙","Fix a technical problem","debug technical code fix",Color.rgb(243,92,107)),new LinearLayout.LayoutParams(0,dp(88),1));root.addView(r2);
    spacer(8);View image=goalTile("▧","Create or edit an image","photo image portrait generation editing",Color.rgb(32,199,201));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams((int)(getResources().getDisplayMetrics().widthPixels*.48f),dp(66));image.setLayoutParams(ip);root.addView(image);

    root.addView(sectionTitle("Smart Collections","See all"));
    LinearLayout c1=hbox();c1.addView(collectionTile("⚖","Compare & choose","Make better decisions","compare recommend decision options",Color.rgb(226,184,78)),new LinearLayout.LayoutParams(0,dp(70),1));spacerH(c1);c1.addView(collectionTile("★","Best for ChatGPT","Top prompting workflows","chatgpt prompt optimize ai",Color.rgb(61,130,255)),new LinearLayout.LayoutParams(0,dp(70),1));root.addView(c1);spacer(8);
    LinearLayout c2=hbox();c2.addView(collectionTile("▣","Career toolkit","Jobs, resumes, interviews","career resume interview email",Color.rgb(45,203,140)),new LinearLayout.LayoutParams(0,dp(70),1));spacerH(c2);c2.addView(collectionTile("▥","Content studio","Blog, social, marketing","content hook script caption story",Color.rgb(213,74,205)),new LinearLayout.LayoutParams(0,dp(70),1));root.addView(c2);
  }''')

# Category cards + utility cards.
s=replace_method(s,'  View groupCard(',r'''  View groupCard(Group g){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(12),dp(10),dp(10),dp(10));
    int accent=groupAccent(g);TextView icon=iconTile(g.icon,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(44),dp(44));ip.setMargins(0,0,dp(12),0);card.addView(icon,ip);
    LinearLayout copy=vbox();TextView title=text(displayGroupTitle(g),16,true,TEXT);TextView sub=text(g.sub,11,false,MUTED);sub.setMaxLines(1);copy.addView(title);copy.addView(sub);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));
    TextView count=text(String.valueOf(groupCount(g)),11,false,TERTIARY);count.setPadding(dp(8),0,dp(8),0);card.addView(count);card.addView(text("›",24,false,TERTIARY));return card;
  }''')

s=replace_method(s,'  View menuCard(',r'''  View menuCard(String icon,String title,String sub){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(12),dp(10),dp(10),dp(10));TextView ic=iconTile(icon,ACCENT);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(42),dp(42));ip.setMargins(0,0,dp(12),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,15,true,TEXT));TextView d=text(sub,11,false,MUTED);d.setMaxLines(2);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.addView(text("›",24,false,TERTIARY));return card;
  }''')

# Browse Categories screen.
s=replace_method(s,'  void browseCategories()',r'''  void browseCategories(){
    page="categories";currentGroup=null;base("Browse Categories","Explore the canonical catalog by capability.",false);
    EditText q=input("Search categories or prompts...",1);q.setSingleLine(true);root.addView(q);LinearLayout results=vbox();root.addView(results);renderCategoryCards(results,"");
    q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderCategoryCards(results,x.toString());}public void afterTextChanged(android.text.Editable e){}});
  }''')

# Focused category browsing: hero + chips + compact prompt cards.
s=replace_method(s,'  void group(Group g,String activeSub,String initialQuery)',r'''  void group(Group g,String activeSub,String initialQuery){
    page="group";currentGroup=g;base(displayGroupTitle(g),g.sub,false);
    LinearLayout hero=hbox();hero.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(g.icon,groupAccent(g));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(52),dp(52));ip.setMargins(0,0,dp(12),0);hero.addView(ic,ip);LinearLayout hcopy=vbox();hcopy.addView(text(groupCount(g)+" prompts",12,true,TEXT));hcopy.addView(text("Choose a focused subcategory or browse all.",11,false,MUTED));hero.addView(hcopy,new LinearLayout.LayoutParams(0,-2,1));root.addView(hero);spacer(10);
    ArrayList<Cmd> items=groupCommands(g);LinkedHashMap<String,Integer> counts=new LinkedHashMap<>();for(Cmd c:items){String sc=groupSubcategory(c,g);counts.put(sc,counts.containsKey(sc)?counts.get(sc)+1:1);}
    HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);LinearLayout chips=hbox();chips.setPadding(0,dp(2),dp(4),dp(8));hsv.addView(chips);root.addView(hsv);Button allChip=filterChip("All",activeSub==null);allChip.setOnClickListener(v->group(g,null,""));chips.addView(allChip);for(String sc:counts.keySet()){Button chip=filterChip(sc,sc.equals(activeSub));chip.setOnClickListener(v->group(g,sc,""));chips.addView(chip);}
    LinearLayout results=vbox();root.addView(results);renderGroupResults(g,results,"",activeSub);
  }''')

s=replace_method(s,'  Button filterChip(',r'''  Button filterChip(String label,boolean active){
    Button b=new Button(this);b.setAllCaps(false);b.setText(label);b.setTextSize(10);b.setTextColor(active?Color.WHITE:MUTED);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));b.setSingleLine(true);b.setMinWidth(0);b.setMinHeight(0);b.setPadding(dp(12),0,dp(12),0);b.setBackground(shape(active?ACCENT:SURFACE2,active?ACCENT:BORDER,20));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(32));lp.setMargins(0,0,dp(8),0);b.setLayoutParams(lp);return b;
  }''')

s=replace_method(s,'  void renderGroupResults(',r'''  void renderGroupResults(Group g,LinearLayout target,String query,String activeSub){
    target.removeAllViews();String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);ArrayList<Cmd> shown=new ArrayList<>();for(Cmd c:groupCommands(g)){String sc=groupSubcategory(c,g);if(activeSub!=null&&!activeSub.equals(sc))continue;if(!q.isEmpty()){String hay=(displayTitle(c)+" "+c.command+" "+c.description+" "+sc).toLowerCase(Locale.ROOT);if(!hay.contains(q))continue;}shown.add(c);}if(shown.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No prompts match this view.",12,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(18),0,dp(18));empty.addView(e);target.addView(empty);return;}TextView meta=text(shown.size()+" prompt"+(shown.size()==1?"":"s"),11,false,TERTIARY);meta.setPadding(0,0,0,dp(6));target.addView(meta);for(Cmd c:shown){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,g));target.addView(row);}
  }''')

# Capability-first prompt rows.
s=replace_method(s,'  View commandRow(',r'''  View commandRow(Cmd c,boolean divider){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(11),dp(10),dp(10),dp(10));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(42),dp(42));ip.setMargins(0,0,dp(11),0);card.addView(ic,ip);LinearLayout copy=vbox();TextView title=text(displayTitle(c),15,true,TEXT);title.setMaxLines(1);copy.addView(title);TextView d=text(shortDescription(c),11,false,MUTED);d.setMaxLines(2);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView star=text(isFavorite(c)?"★":"☆",18,false,isFavorite(c)?FAVORITE:TERTIARY);star.setGravity(Gravity.CENTER);star.setPadding(dp(7),0,dp(7),0);star.setOnClickListener(v->{toggleFavorite(c);star.setText(isFavorite(c)?"★":"☆");star.setTextColor(isFavorite(c)?FAVORITE:TERTIARY);});card.addView(star,new LinearLayout.LayoutParams(dp(34),dp(42)));TextView more=text("⋯",20,false,TERTIARY);more.setGravity(Gravity.CENTER);card.addView(more,new LinearLayout.LayoutParams(dp(26),dp(42)));return card;
  }''')

# Prompt detail with variables + try now + related prompts.
s=replace_method(s,'  void detail(',r'''  void detail(Cmd c,Group g){
    page="detail";currentGroup=g;rememberRecent(c);base(displayTitle(c),shortDescription(c),true);
    LinearLayout identity=hbox();identity.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(50),dp(50));ip.setMargins(0,0,dp(12),0);identity.addView(ic,ip);LinearLayout copy=vbox();TextView cmd=text("/"+c.command,10,false,TERTIARY);copy.addView(cmd);LinearLayout tags=hbox();String[] tt=detailTags(c);for(String t:tt){TextView tag=smallTag(t);tags.addView(tag);}copy.addView(tags);identity.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView star=text(isFavorite(c)?"★":"☆",22,false,isFavorite(c)?FAVORITE:TERTIARY);star.setGravity(Gravity.CENTER);star.setOnClickListener(v->{toggleFavorite(c);star.setText(isFavorite(c)?"★":"☆");star.setTextColor(isFavorite(c)?FAVORITE:TERTIARY);});identity.addView(star,new LinearLayout.LayoutParams(dp(42),dp(48)));root.addView(identity);
    info("PROMPT",c.instruction);
    ArrayList<String> vars=templateVariables(c.instruction);if(!vars.isEmpty()){TextView vl=text("Variables (optional)  ⓘ",13,true,TEXT);vl.setPadding(0,dp(14),0,dp(6));root.addView(vl);for(String key:vars){TextView lab=text(prettyKey(key),11,false,MUTED);lab.setPadding(dp(2),dp(3),0,dp(4));root.addView(lab);EditText field=input("e.g. "+prettyKey(key).toLowerCase(Locale.ROOT),1);String old=promptVar(c.id,key);field.setText(old);field.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int co,int a){}public void onTextChanged(CharSequence x,int st,int b,int co){setPromptVar(c.id,key,x.toString());}public void afterTextChanged(android.text.Editable e){}});root.addView(field);}}
    Button add=selected.contains(c)?secondary("✓  Added to Stack"):primary("＋  Add to Stack");add.setOnClickListener(v->{if(!selected.contains(c))selected.add(c);stack();});root.addView(add);
    TextView tryTitle=text("Try it now",14,true,TEXT);tryTitle.setPadding(0,dp(14),0,dp(6));root.addView(tryTitle);EditText tryBox=input("Add your context or specific request...",4);tryBox.setMaxLines(7);root.addView(tryBox);Button run=primary("➤  Run with ChatGPT");run.setOnClickListener(v->sendText(buildSinglePrompt(c,tryBox.getText().toString().trim())));root.addView(run);
    relatedActions(c.command);sourceActions(c);
  }''')

# Related prompt chips display capabilities, not raw command IDs.
s=replace_method(s,'  Button relatedChip(',r'''  Button relatedChip(Cmd c){
    boolean added=selected.contains(c);Button x=new Button(this);x.setAllCaps(false);x.setText((added?"✓  ":"＋  ")+displayTitle(c));x.setTextColor(added?SUCCESS:TEXT);x.setTextSize(11);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));x.setSingleLine(true);x.setMinWidth(0);x.setMinHeight(0);x.setPadding(dp(11),0,dp(11),0);x.setBackground(shape(SURFACE2,added?SUCCESS:BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(36));lp.setMargins(0,0,dp(8),0);x.setLayoutParams(lp);x.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added "+displayTitle(c));x.setText("✓  "+displayTitle(c));x.setTextColor(SUCCESS);x.setBackground(shape(SURFACE2,SUCCESS,18));}else toast(displayTitle(c)+" is already in the stack");});return x;
  }''')

# Stack matching compact multi-step proposal.
s=replace_method(s,'  void stack()',r'''  void stack(){
    if(context!=null)contextDraft=context.getText().toString();page="stack";base("Prompt Stack",selected.isEmpty()?"Build a multi-step workflow.":selected.size()+" selected prompts",false);
    if(selected.isEmpty()){LinearLayout empty=surface(true);TextView e=text("Your stack is empty. Discover a prompt and add it here.",13,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(24),0,dp(24));empty.addView(e);root.addView(empty);Button browse=primary("Browse prompts");browse.setOnClickListener(v->searchPage());root.addView(browse);return;}
    LinearLayout actions=hbox();TextView count=text(selected.size()+" steps",11,true,TERTIARY);actions.addView(count,new LinearLayout.LayoutParams(0,dp(34),1));Button clear=compactControl("Clear");clear.setOnClickListener(v->{selected.clear();stack();});actions.addView(clear,new LinearLayout.LayoutParams(dp(72),dp(34)));root.addView(actions);
    for(int i=0;i<selected.size();i++){final int k=i;Cmd c=selected.get(i);LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView num=text(String.valueOf(i+1),10,true,TERTIARY);num.setGravity(Gravity.CENTER);card.addView(num,new LinearLayout.LayoutParams(dp(24),dp(44)));TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(42),dp(42));ip.setMargins(0,0,dp(10),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),14,true,TEXT));TextView d=text(shortDescription(c),10,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));LinearLayout controls=hbox();Button up=mini("↑"),dn=mini("↓"),rm=mini("×");up.setEnabled(k>0);dn.setEnabled(k<selected.size()-1);up.setOnClickListener(v->{if(k>0)Collections.swap(selected,k,k-1);stack();});dn.setOnClickListener(v->{if(k<selected.size()-1)Collections.swap(selected,k,k+1);stack();});rm.setOnClickListener(v->{selected.remove(k);stack();});controls.addView(up);controls.addView(dn);controls.addView(rm);card.addView(controls);root.addView(card);}
    TextView req=text("REQUEST / CONTEXT",10,true,TERTIARY);req.setLetterSpacing(.10f);req.setPadding(0,dp(8),0,dp(5));root.addView(req);context=input("Enter your request, text or context...",3);context.setMaxLines(7);context.setText(contextDraft);root.addView(context);Button more=secondary("＋  Add Another Prompt");more.setOnClickListener(v->{contextDraft=context==null?contextDraft:context.getText().toString();searchPage();});root.addView(more);Button run=primary("➤  Run Stack with ChatGPT");run.setOnClickListener(v->build());root.addView(run);
  }''')

# Capability-first picker row.
s=replace_method(s,'  View pickCommandRow(',r'''  View pickCommandRow(Cmd c,boolean divider){
    LinearLayout card=surface(true);card.setOrientation(LinearLayout.HORIZONTAL);card.setGravity(Gravity.CENTER_VERTICAL);TextView ic=iconTile(promptIcon(c),categoryAccent(c));LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(40),dp(40));ip.setMargins(0,0,dp(10),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(displayTitle(c),14,true,TEXT));TextView d=text(shortDescription(c),10,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));TextView state=text(selected.contains(c)?"✓":"＋",16,true,selected.contains(c)?SUCCESS:ACCENT);state.setGravity(Gravity.CENTER);card.addView(state,new LinearLayout.LayoutParams(dp(34),dp(40)));card.setOnClickListener(v->{if(!selected.contains(c)){selected.add(c);toast("Added "+displayTitle(c));}else{selected.remove(c);toast("Removed "+displayTitle(c));}addMore();});return card;
  }''')

# ChatGPT-native stack composer with template resolution.
s=replace_method(s,'  void build()',r'''  void build(){
    page="build";String user=context==null?contextDraft:context.getText().toString().trim();contextDraft=user;base("Final Prompt","Review the composed ChatGPT-ready request.",false);StringBuilder p=new StringBuilder();p.append("Use the user's request/context as the source of truth.\n\n");if(!user.isEmpty())p.append("USER REQUEST / CONTEXT:\n").append(user).append("\n\n");p.append("SELECTED PROMPT MODULES:\n");for(int i=0;i<selected.size();i++){Cmd c=selected.get(i);p.append("\nSTEP ").append(i+1).append(" — ").append(displayTitle(c)).append("\n");p.append(resolveTemplate(c,user)).append("\n");}p.append("\nEXECUTION RULES:\n- Apply the selected modules in order, carrying forward only useful findings from earlier steps.\n- Each module is scoped to its step and must not override or block later modules.\n- Use tools or external capabilities only when they are actually available in the current ChatGPT conversation.\n- If one essential input is missing and cannot reasonably be inferred, ask one concise clarifying question; otherwise make a reasonable assumption and state it when important.\n- Produce one clear, coherent final answer rather than separate disconnected answers for each module.\n- Show useful conclusions, evidence and verification where relevant, but do not expose private chain-of-thought.\n");finalPrompt=input("",12);finalPrompt.setText(p);finalPrompt.setTextSize(13);finalPrompt.setMinHeight(dp(260));root.addView(finalPrompt);Button send=primary("➤  Open in ChatGPT");send.setOnClickListener(v->send());root.addView(send);Button copy=secondary("Copy prompt");copy.setOnClickListener(v->copy());root.addView(copy);Button edit=ghost("Edit stack");edit.setOnClickListener(v->stack());root.addView(edit);
  }''')

# My Prompts becomes custom prompts + Favorites only.
s=replace_method(s,'  void library()',r'''  void library(){library(false);}''')

library_overload=r'''  void library(boolean favoritesMode){
    page="library";currentGroup=null;base("My Prompts",favoritesMode?"Your saved built-in and custom favorites.":"Your custom prompts stay on this device.",false);LinearLayout seg=hbox();Button mine=filterChip("My Prompts",!favoritesMode),fav=filterChip("Favorites",favoritesMode);mine.setOnClickListener(v->library(false));fav.setOnClickListener(v->library(true));seg.addView(mine,new LinearLayout.LayoutParams(0,dp(34),1));spacerH(seg);seg.addView(fav,new LinearLayout.LayoutParams(0,dp(34),1));root.addView(seg);spacer(10);
    ArrayList<Cmd> rows=new ArrayList<>();for(Cmd c:all){if(favoritesMode){if(isFavorite(c))rows.add(c);}else if(c.custom)rows.add(c);}if(rows.isEmpty()){LinearLayout empty=surface(true);TextView e=text(favoritesMode?"No favorites yet.":"No custom prompts yet.",12,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(20),0,dp(20));empty.addView(e);root.addView(empty);}else for(Cmd c:rows){View row=commandRow(c,false);row.setOnClickListener(v->{if(c.custom)customDetail(c);else detail(c,groupFor(c));});root.addView(row);}if(!favoritesMode){Button create=secondary("＋  Create a New Prompt");create.setOnClickListener(v->showAdd());root.addView(create);LinearLayout tools=hbox();Button paste=ghost("Paste");paste.setOnClickListener(v->showBulkPaste());Button imp=ghost("Import");imp.setOnClickListener(v->openImport());Button exp=ghost("Export");exp.setOnClickListener(v->openExport());tools.addView(paste,new LinearLayout.LayoutParams(0,-2,1));spacerH(tools);tools.addView(imp,new LinearLayout.LayoutParams(0,-2,1));spacerH(tools);tools.addView(exp,new LinearLayout.LayoutParams(0,-2,1));root.addView(tools);}
  }

'''
if 'void library(boolean favoritesMode)' not in s:
    s=insert_before(s,'  void customDetail(',library_overload)

# ---------- add v0.8.1 visual/navigation/runtime helpers ----------
helpers=r'''  LinearLayout bottomNav(){
    LinearLayout nav=hbox();nav.setGravity(Gravity.CENTER);nav.setPadding(dp(4),dp(5),dp(4),dp(5));nav.setBackground(satinShape(Color.rgb(9,20,33),Color.rgb(7,17,29),BORDER,0));nav.addView(navItem("⌂","Home",navActive("home"),()->home()),new LinearLayout.LayoutParams(0,-1,1));nav.addView(navItem("⌕","Browse",navActive("browse"),()->searchPage()),new LinearLayout.LayoutParams(0,-1,1));nav.addView(navItem("≋","Stack",navActive("stack"),()->stack()),new LinearLayout.LayoutParams(0,-1,1));nav.addView(navItem("▣","My Prompts",navActive("my"),()->library()),new LinearLayout.LayoutParams(0,-1,1));nav.addView(navItem("⚙","Settings",navActive("settings"),()->settings()),new LinearLayout.LayoutParams(0,-1,1));return nav;
  }
  View navItem(String icon,String label,boolean active,Runnable action){LinearLayout x=vbox();x.setGravity(Gravity.CENTER);TextView i=text(icon,19,true,active?ACCENT:TERTIARY);i.setGravity(Gravity.CENTER);TextView l=text(label,9,active,active?ACCENT:TERTIARY);l.setGravity(Gravity.CENTER);x.addView(i,new LinearLayout.LayoutParams(-1,dp(28)));x.addView(l,new LinearLayout.LayoutParams(-1,dp(20)));x.setOnClickListener(v->action.run());return x;}
  boolean navActive(String key){if("home".equals(key))return"home".equals(page);if("browse".equals(key))return"search".equals(page)||"categories".equals(page)||"group".equals(page)||"detail".equals(page)||"discover".equals(page);if("stack".equals(key))return"stack".equals(page)||"addMore".equals(page)||"build".equals(page);if("my".equals(key))return"library".equals(page)||"customDetail".equals(page);return"settings".equals(page);}
  void spacerH(LinearLayout row){Space s=new Space(this);row.addView(s,new LinearLayout.LayoutParams(dp(8),1));}
  TextView sectionTitle(String title,String action){LinearLayout dummy=null;TextView v=text(action==null?title:title+"                                      "+action,14,true,TEXT);v.setPadding(dp(2),dp(16),0,dp(8));return v;}
  View goalTile(String icon,String title,String query,int accent){LinearLayout card=vbox();card.setPadding(dp(10),dp(9),dp(8),dp(8));card.setGravity(Gravity.START);card.setBackground(tintedCard(accent,16));TextView ic=text(icon,21,true,accent);card.addView(ic,new LinearLayout.LayoutParams(-1,dp(30)));TextView t=text(title,11,true,TEXT);t.setMaxLines(2);card.addView(t);card.setOnClickListener(v->smartCollection(title,"Best matching prompts",query,null,"Best matches"));return card;}
  View collectionTile(String icon,String title,String sub,String query,int accent){LinearLayout card=hbox();card.setGravity(Gravity.CENTER_VERTICAL);card.setPadding(dp(9),dp(8),dp(8),dp(8));card.setBackground(tintedCard(accent,14));TextView ic=iconTile(icon,accent);LinearLayout.LayoutParams ip=new LinearLayout.LayoutParams(dp(34),dp(34));ip.setMargins(0,0,dp(8),0);card.addView(ic,ip);LinearLayout copy=vbox();copy.addView(text(title,11,true,TEXT));TextView d=text(sub,9,false,MUTED);d.setMaxLines(1);copy.addView(d);card.addView(copy,new LinearLayout.LayoutParams(0,-2,1));card.setOnClickListener(v->smartCollection(title,sub,query,null,"Best matches"));return card;}
  GradientDrawable tintedCard(int accent,int radius){int r=(Color.red(accent)+Color.red(BG)*5)/6,g=(Color.green(accent)+Color.green(BG)*5)/6,b=(Color.blue(accent)+Color.blue(BG)*5)/6;return satinShape(Color.rgb(Math.min(255,r+10),Math.min(255,g+10),Math.min(255,b+10)),Color.rgb(r,g,b),Color.rgb((Color.red(accent)+36)/2,(Color.green(accent)+54)/2,(Color.blue(accent)+76)/2),radius);}
  TextView iconTile(String icon,int accent){TextView v=text(icon,19,true,Color.WHITE);v.setGravity(Gravity.CENTER);v.setBackground(tintedCard(accent,12));return v;}
  int groupAccent(Group g){String x=g.title.toLowerCase(Locale.ROOT);if(x.contains("writing"))return Color.rgb(61,130,255);if(x.contains("research"))return Color.rgb(45,203,140);if(x.contains("planning"))return Color.rgb(226,184,78);if(x.contains("work")||x.contains("career")||x.contains("business"))return Color.rgb(168,91,255);if(x.contains("technical")||x.contains("data"))return Color.rgb(32,199,201);if(x.contains("content")||x.contains("creative"))return Color.rgb(243,92,153);if(x.contains("health"))return Color.rgb(88,216,109);if(x.contains("photo")||x.contains("image"))return Color.rgb(74,223,209);if(x.contains("learning"))return Color.rgb(61,130,255);return Color.rgb(244,154,58);}
  int categoryAccent(Cmd c){Group g=groupFor(c);return groupAccent(g);}
  String promptIcon(Cmd c){String x=(c.category+" "+c.command).toLowerCase(Locale.ROOT);if(x.contains("write")||x.contains("email"))return"✎";if(x.contains("research")||x.contains("learn")||x.contains("explain"))return"⌕";if(x.contains("plan")||x.contains("roadmap"))return"▣";if(x.contains("code")||x.contains("technical")||x.contains("debug"))return"⚙";if(x.contains("photo")||x.contains("image"))return"▧";if(x.contains("health"))return"♡";if(x.contains("marketing")||x.contains("business"))return"▤";return"◆";}
  String displayGroupTitle(Group g){String x=g.title;if(x.equals("Writing & Rewriting"))return"Writing & Content";if(x.equals("Research & Analysis"))return"Research & Learning";if(x.equals("Planning & Execution"))return"Productivity & Planning";if(x.equals("Work & Career"))return"Career & Business";if(x.equals("Problem Solving & Technical"))return"Technology & Development";if(x.equals("Content Creation"))return"Creativity & Design";if(x.equals("Health & Wellness"))return"Health & Lifestyle";if(x.equals("Photo Editing & Image Generation"))return"Images & Visuals";return x;}
  String displayTitle(Cmd c){String k=c.command.toLowerCase(Locale.ROOT);if(k.equals("eli5"))return"Explain Like I'm 5 (ELI5)";if(k.equals("rewrite"))return"Rewrite for Clarity";if(k.equals("humanize"))return"Make It Sound More Human";if(k.equals("summarize"))return"Summarize";if(k.equals("research"))return"Research a Topic";if(k.equals("email")||k.equals("reply"))return"Email Reply";String s=c.command.replaceAll("([a-z0-9])([A-Z])","$1 $2").replaceAll("([A-Z]+)([A-Z][a-z])","$1 $2").replaceAll("[_-]+"," ").trim();if(s.length()>46&&c.description!=null){String d=c.description.split("[.—]")[0].trim();if(d.length()>=4&&d.length()<=46)s=d;}StringBuilder o=new StringBuilder();for(String w:s.split("\\s+")){if(w.isEmpty())continue;if(o.length()>0)o.append(' ');o.append(Character.toUpperCase(w.charAt(0))).append(w.length()>1?w.substring(1):"");}return o.length()==0?"Prompt":o.toString();}
  String shortDescription(Cmd c){String d=c.description==null?"":c.description.replaceAll("\\s+"," ").trim();if(d.isEmpty()||d.equalsIgnoreCase(displayTitle(c)))d=useWhen(c);if(d.length()>92)d=d.substring(0,89).trim()+"…";return d;}
  TextView smallTag(String label){TextView v=text(label,9,true,MUTED);v.setSingleLine(true);v.setPadding(dp(9),dp(5),dp(9),dp(5));v.setBackground(shape(SURFACE2,BORDER,18));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,-2);lp.setMargins(0,0,dp(6),0);v.setLayoutParams(lp);return v;}
  String[] detailTags(Cmd c){String sc=c.subcategory==null?"":c.subcategory.trim();String cat=displayGroupTitle(groupFor(c));if(sc.isEmpty()||"General".equalsIgnoreCase(sc))return new String[]{cat};return new String[]{cat,sc};}
  Set<String> favoriteIds(){return new HashSet<>(getSharedPreferences(PREFS,MODE_PRIVATE).getStringSet("favorite_prompt_ids",new HashSet<>()));}
  boolean isFavorite(Cmd c){return favoriteIds().contains(String.valueOf(c.id));}
  void toggleFavorite(Cmd c){Set<String> s=favoriteIds();String id=String.valueOf(c.id);if(s.contains(id))s.remove(id);else s.add(id);getSharedPreferences(PREFS,MODE_PRIVATE).edit().putStringSet("favorite_prompt_ids",s).apply();}
  void renderCategoryCards(LinearLayout target,String query){target.removeAllViews();String q=query==null?"":query.trim().toLowerCase(Locale.ROOT);for(Group g:groups){String hay=(g.title+" "+displayGroupTitle(g)+" "+g.sub).toLowerCase(Locale.ROOT);if(!q.isEmpty()&&!hay.contains(q)){boolean hit=false;for(Cmd c:groupCommands(g)){if((displayTitle(c)+" "+c.description).toLowerCase(Locale.ROOT).contains(q)){hit=true;break;}}if(!hit)continue;}View card=groupCard(g);card.setOnClickListener(v->group(g));target.addView(card);}}
  void searchPage(){searchPage("","All");}
  void searchPage(String initial,String mode){page="search";currentGroup=null;base("Search","Find prompts, categories and smart collections.",false);EditText q=input("Search prompts or describe what you want...",1);q.setSingleLine(true);q.setText(initial);root.addView(q);LinearLayout chips=hbox();String[] modes={"All","Prompts","Categories","Collections"};for(String m:modes){Button b=filterChip(m,m.equals(mode));b.setOnClickListener(v->searchPage(q.getText().toString(),m));chips.addView(b);}root.addView(chips);spacer(8);LinearLayout results=vbox();root.addView(results);renderSearchResults(results,q.getText().toString(),mode);q.addTextChangedListener(new android.text.TextWatcher(){public void beforeTextChanged(CharSequence x,int st,int c,int a){}public void onTextChanged(CharSequence x,int st,int b,int c){renderSearchResults(results,x.toString(),mode);}public void afterTextChanged(android.text.Editable e){}});}
  void renderSearchResults(LinearLayout target,String query,String mode){target.removeAllViews();String q=query==null?"":query.trim();if("Categories".equals(mode)){renderCategoryCards(target,q);return;}if("Collections".equals(mode)){View a=menuCard("⚖","Compare & choose","Compare options and recommend the strongest fit");a.setOnClickListener(v->smartCollection("Compare & choose","Make better decisions","compare recommend decision options",null,"Best matches"));target.addView(a);View b=menuCard("★","Best for ChatGPT","Prompt design and AI workflows");b.setOnClickListener(v->smartCollection("Best for ChatGPT","Prompt design and AI workflows","chatgpt prompt optimize ai",null,"Best matches"));target.addView(b);View c=menuCard("▣","Career toolkit","Resumes, interviews and professional communication");c.setOnClickListener(v->smartCollection("Career toolkit","Career workflows","career resume interview email",null,"Best matches"));target.addView(c);return;}if("All".equals(mode)&&q.length()<2){View browse=menuCard("▦","Browse Categories","Explore the full canonical catalog");browse.setOnClickListener(v->browseCategories());target.addView(browse);TextView hint=text("Describe an outcome above to rank the best matching prompts.",11,false,MUTED);hint.setPadding(dp(2),dp(8),0,dp(8));target.addView(hint);return;}ArrayList<Cmd> ranked=rankSmart(q.length()<2?"chatgpt useful":q,30);for(Cmd c:ranked){View row=commandRow(c,false);row.setOnClickListener(v->detail(c,groupFor(c)));target.addView(row);}if(ranked.isEmpty()){LinearLayout empty=surface(true);TextView e=text("No strong matches yet. Try describing the outcome you want.",12,false,MUTED);e.setGravity(Gravity.CENTER);e.setPadding(0,dp(18),0,dp(18));empty.addView(e);target.addView(empty);}}
  void settings(){page="settings";currentGroup=null;base("Settings","Simple app preferences and information.",false);View a=menuCard("⚙","App Preferences","Theme, language and behavior");a.setOnClickListener(v->toast("PromptDeck uses the locked dark v0.8.1 appearance."));root.addView(a);View b=menuCard("◎","ChatGPT Connection","Uses Android share to open ChatGPT");b.setOnClickListener(v->toast("PromptDeck sends prompts to the ChatGPT app when available."));root.addView(b);View c=menuCard("▣","Data & Storage","Manage local custom prompts and favorites");c.setOnClickListener(v->toast(all.size()+" prompts loaded locally"));root.addView(c);View d=menuCard("ⓘ","About PromptDeck","Version 0.8.1");d.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("PromptDeck 0.8.1").setMessage("Discover. Customize. Stack. Create. All with ChatGPT.").setPositiveButton("OK",null).show());root.addView(d);}
  ArrayList<String> templateVariables(String instruction){LinkedHashSet<String> out=new LinkedHashSet<>();String t=instruction==null?"":instruction;java.util.regex.Matcher a=java.util.regex.Pattern.compile("\\$\\{\\s*([A-Za-z][A-Za-z0-9 _-]{0,39})(?::[^}]*)?\\}").matcher(t);while(a.find())out.add(a.group(1).trim());java.util.regex.Matcher b=java.util.regex.Pattern.compile("\\[([A-Za-z][A-Za-z0-9 _-]{1,31})\\]").matcher(t);while(b.find()){String k=b.group(1).trim();if(!k.matches("(?i)(true|false|null|json|array|object|string|number|integer|items?)"))out.add(k);}return new ArrayList<>(out);}
  String prettyKey(String k){String x=k.replace('_',' ').replace('-',' ').trim();if(x.isEmpty())return"Value";return Character.toUpperCase(x.charAt(0))+x.substring(1);}
  String promptVar(int id,String key){HashMap<String,String> m=promptVars.get(id);return m==null?"":m.getOrDefault(key,"");}
  void setPromptVar(int id,String key,String value){HashMap<String,String> m=promptVars.get(id);if(m==null){m=new HashMap<>();promptVars.put(id,m);}m.put(key,value==null?"":value.trim());}
  String resolveTemplate(Cmd c,String user){String text=c.instruction;java.util.regex.Matcher a=java.util.regex.Pattern.compile("\\$\\{\\s*([A-Za-z][A-Za-z0-9 _-]{0,39})(?::([^}]*))?\\}").matcher(text);StringBuffer sb=new StringBuffer();while(a.find()){String key=a.group(1).trim(),def=a.group(2)==null?"":a.group(2).trim(),val=promptVar(c.id,key);if(val.isEmpty())val=!def.isEmpty()?def:(user==null||user.isEmpty()?"the "+prettyKey(key).toLowerCase(Locale.ROOT)+" specified by the user":"the relevant "+prettyKey(key).toLowerCase(Locale.ROOT)+" from the user's request");a.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(val));}a.appendTail(sb);text=sb.toString();java.util.regex.Matcher b=java.util.regex.Pattern.compile("\\[([A-Za-z][A-Za-z0-9 _-]{1,31})\\]").matcher(text);sb=new StringBuffer();while(b.find()){String key=b.group(1).trim();if(key.matches("(?i)(true|false|null|json|array|object|string|number|integer|items?)")){b.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(b.group(0)));continue;}String val=promptVar(c.id,key);if(val.isEmpty())val=(user==null||user.isEmpty()?"the "+prettyKey(key).toLowerCase(Locale.ROOT)+" specified by the user":"the relevant "+prettyKey(key).toLowerCase(Locale.ROOT)+" from the user's request");b.appendReplacement(sb,java.util.regex.Matcher.quoteReplacement(val));}b.appendTail(sb);return sb.toString();}
  String buildSinglePrompt(Cmd c,String user){StringBuilder p=new StringBuilder();if(user!=null&&!user.isEmpty())p.append("USER REQUEST / CONTEXT:\n").append(user).append("\n\n");p.append("TASK — ").append(displayTitle(c)).append(":\n").append(resolveTemplate(c,user)).append("\n\nUse available ChatGPT tools only when helpful and available. If one essential input is missing and cannot be inferred, ask one concise clarifying question. Give one clear final answer with useful conclusions or evidence where relevant, without exposing private chain-of-thought.");return p.toString();}
  void sendText(String text){Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,text);i.setPackage("com.openai.chatgpt");try{startActivity(i);}catch(Exception e){i.setPackage(null);startActivity(Intent.createChooser(i,"Send prompt"));}}
  GradientDrawable gradientShape(int left,int right,int stroke,int radius){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{left,right});g.setCornerRadius(dp(radius));if(stroke!=0)g.setStroke(dp(1),stroke);return g;}

'''
if 'LinearLayout bottomNav(){' not in s:
    s=insert_before(s,'  String subcat(',helpers)

# Core styling helpers.
s=replace_method(s,'  LinearLayout surface(',r'''  LinearLayout surface(boolean compact){LinearLayout l=vbox();l.setPadding(dp(compact?12:14),dp(compact?11:13),dp(compact?12:14),dp(compact?11:13));l.setBackground(satinShape(SURFACE2,SURFACE,BORDER,18));l.setElevation(dp(1));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(2),0,dp(8));l.setLayoutParams(lp);return l;}''')

s=replace_method(s,'  TextView text(',r'''  TextView text(String s,int sp,boolean bold,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(color);v.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);v.setTypeface(Typeface.create(bold?"sans-serif-medium":"sans-serif",Typeface.NORMAL));return v;}''')

s=replace_method(s,'  TextView pill(',r'''  TextView pill(String s){TextView v=text(s,9,true,ACCENT);v.setGravity(Gravity.CENTER);v.setPadding(dp(10),dp(6),dp(10),dp(6));v.setBackground(shape(SURFACE2,BORDER,18));return v;}''')

s=replace_method(s,'  Button styledButton(',r'''  Button styledButton(String s,int fill,int stroke,int color){Button x=new Button(this);x.setText(s);x.setAllCaps(false);x.setTextColor(color);x.setTextSize(13);x.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));if(fill==ACCENT)x.setBackground(gradientShape(ACCENT,PURPLE,Color.rgb(80,126,255),16));else x.setBackground(satinShape(SURFACE2,SURFACE,stroke,16));x.setElevation(dp(1));x.setPadding(dp(12),dp(8),dp(12),dp(8));x.setMinHeight(dp(50));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(50));lp.setMargins(0,dp(4),0,dp(4));x.setLayoutParams(lp);return x;}''')

if 'Button primary(String s){return styledButton(s,ACCENT' not in s:
    s=s.replace('Button primary(String s){return styledButton(s,Color.rgb(47,107,255),Color.rgb(74,128,255),Color.WHITE);}', 'Button primary(String s){return styledButton(s,ACCENT,Color.rgb(80,126,255),Color.WHITE);}',1)

# Input styling if method exists.
if '  EditText input(' in s:
    s=replace_method(s,'  EditText input(',r'''  EditText input(String hint,int lines){EditText e=new EditText(this);e.setHint(hint);e.setHintTextColor(TERTIARY);e.setTextColor(TEXT);e.setTextSize(13);e.setGravity(Gravity.TOP|Gravity.START);e.setSingleLine(lines==1);e.setMinLines(lines);e.setPadding(dp(13),dp(10),dp(13),dp(10));e.setBackground(shape(INPUT,BORDER,16));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(3),0,dp(8));e.setLayoutParams(lp);return e;}''')

# Version bump.
g=GRADLE.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 24',g,count=1)
g=re.sub(r"versionName\s+'[^']+'","versionName '0.8.1'",g,count=1)
GRADLE.write_text(g,encoding='utf-8')

# Visible built-in library wording should not return.
s=s.replace('base("Prompt Library"','base("My Prompts"')
s=s.replace('"Prompt Library"+(cat==null||cat.isEmpty()?"":" • "+cat)','"My Prompts"')

# Source-level gates.
checks=[
    'Find the right prompt','Quick Goals','Smart Collections','LinearLayout bottomNav()','void searchPage()','void settings()','Variables (optional)','Run with ChatGPT','Run Stack with ChatGPT','displayTitle(Cmd c)','resolveTemplate(Cmd c,String user)','applyChatGPTNativeFinal()'
]
for x in checks:
    if x not in s: raise SystemExit('v0.8.1 gate missing: '+x)
if re.search(r'[\u0600-\u06FF]',s): raise SystemExit('Arabic visible/source UI text remains')
JAVA.write_text(s,encoding='utf-8')
print('PromptDeck v0.8.1 design lock + ChatGPT-native runtime patch applied')
