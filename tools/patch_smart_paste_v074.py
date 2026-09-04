#!/usr/bin/env python3
from pathlib import Path
import re

p=Path('android/app/src/main/java/com/kareem/promptdeck/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Make Smart Paste accept a complete raw prompt with no /CommandName header.
s=s.replace('toast("No prompts found. Start each prompt with /CommandName")','toast("Paste a prompt, or use /CommandName when pasting several prompts")')

pat=r'''  int\[\] parseBulkCommands\(String raw,String category\)\{.*?\n  \}\n\n  void showAdd\(\)\{'''
replacement=r'''  int[] parseBulkCommands(String raw,String category){
    int added=0,skipped=0;
    java.util.regex.Pattern header=java.util.regex.Pattern.compile("^\\s*(?:\\d+[.)]\\s*)?/([A-Za-z0-9_-]+)(?:\\s*(?:→|->|—|–|:|=)\\s*(.*))?\\s*$");
    String currentName=null,currentInline=null;StringBuilder body=new StringBuilder();
    ArrayList<String[]> blocks=new ArrayList<>();
    for(String line:raw.split("\\r?\\n")){
      java.util.regex.Matcher m=header.matcher(line.trim());
      if(m.matches()){
        if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});
        currentName=m.group(1);currentInline=m.group(2)==null?"":m.group(2).trim();body.setLength(0);
      }else if(currentName!=null){if(body.length()>0)body.append('\n');body.append(line);}
    }
    if(currentName!=null)blocks.add(new String[]{currentName,currentInline==null?"":currentInline,body.toString().trim()});

    // No slash headers: treat the complete pasted text as one prompt and infer its command name.
    if(blocks.isEmpty()){
      String fullRaw=raw==null?"":raw.trim();
      if(!fullRaw.isEmpty())blocks.add(new String[]{autoCommandName(fullRaw,category),"",fullRaw});
    }

    for(String[] b:blocks){
      String name=b[0],inline=b[1],full=b[2];String instruction=!full.isEmpty()?full:inline;
      if(instruction==null||instruction.trim().isEmpty()){skipped++;continue;}
      String base=name;int suffix=2;while(find(name)!=null)name=base+(suffix++);
      String desc=!inline.isEmpty()&&!full.isEmpty()?inline:autoDescription(instruction,category);
      if(!inline.isEmpty()&&full.isEmpty())desc=inline;
      try{
        JSONObject o=new JSONObject();o.put("id",nextId());o.put("command",name);o.put("category",category);
        o.put("description",category.toLowerCase(Locale.ROOT).contains("photo")?photoDescription(desc):desc);
        o.put("instruction",instruction);all.add(new Cmd(o,true));added++;
      }catch(Exception e){skipped++;}
    }
    return new int[]{added,skipped};
  }

  String autoCommandName(String prompt,String category){
    String text=prompt==null?"":prompt.trim();
    String lower=text.toLowerCase(Locale.ROOT);
    String candidate="";

    // Prefer an explicit short first line as the title if the user pasted one.
    String[] lines=text.split("\\r?\\n");
    if(lines.length>0){
      String first=lines[0].trim().replaceAll("^[#*\\s-]+","");
      if(first.length()>=3&&first.length()<=56&&first.split("\\s+").length<=8&&!first.endsWith(".")&&!first.endsWith(","))candidate=first;
    }

    if(candidate.isEmpty()&&category!=null&&category.toLowerCase(Locale.ROOT).contains("photo")){
      if(lower.contains("papyrus")||lower.contains("archival")||lower.contains("antique"))candidate="ArchivalArtwork";
      else if(lower.contains("double exposure"))candidate="DoubleExposure";
      else if(lower.contains("cinematic")||lower.contains("movie still"))candidate="CinematicImage";
      else if(lower.contains("portrait")||lower.contains("face"))candidate="PortraitEdit";
      else if(lower.contains("product"))candidate="ProductPhoto";
      else if(lower.contains("background"))candidate="BackgroundEdit";
      else if(lower.contains("restore")||lower.contains("resolution")||lower.contains("upscale"))candidate="PhotoRestore";
      else if(lower.contains("vintage")||lower.contains("film grain")||lower.contains("35mm"))candidate="VintagePhoto";
      else if(lower.contains("watercolor")||lower.contains("illustration")||lower.contains("painting"))candidate="ArtStyle";
    }

    if(candidate.isEmpty()){
      HashSet<String> stop=new HashSet<>(Arrays.asList("the","a","an","and","or","to","of","in","on","for","with","from","this","that","it","is","are","be","as","use","create","make","generate","produce","image","photo","prompt","please","only","into","while","keep","preserve","original","subject"));
      StringBuilder out=new StringBuilder();int count=0;
      for(String w:text.replaceAll("[^A-Za-z0-9 ]"," ").split("\\s+")){
        String lw=w.toLowerCase(Locale.ROOT);if(w.length()<3||stop.contains(lw))continue;
        out.append(Character.toUpperCase(w.charAt(0))).append(w.substring(1).toLowerCase(Locale.ROOT));
        if(++count==3)break;
      }
      candidate=out.length()>0?out.toString():"CustomPrompt";
    }

    String clean=Cmd.clean(candidate);
    if(clean.isEmpty())clean="CustomPrompt";
    if(clean.length()>32)clean=clean.substring(0,32);
    return clean;
  }

  void showAdd(){'''

# Use a function replacement so Python's regex engine does not reinterpret Java backslashes.
ns2,n=re.subn(pat,lambda m: replacement,s,flags=re.S)
if n!=1:
    raise SystemExit(f'Expected to replace one parseBulkCommands block, replaced {n}')
s=ns2

# Update Smart Paste guidance so the raw-prompt mode is obvious.
s=s.replace('Description is optional. If you paste a full prompt, PromptDeck will derive a short description from the prompt automatically.',
'''Paste one complete prompt as-is and PromptDeck will create its command name and description automatically. For several prompts at once, start each one with /CommandName.''')

p.write_text(s,encoding='utf-8')
print('PromptDeck v0.7.4 Smart Paste raw-prompt fallback applied')
