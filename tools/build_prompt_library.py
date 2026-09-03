#!/usr/bin/env python3
import csv, json, re, sys
from pathlib import Path

CATEGORY_RULES = [
    ("AI & Prompting", ["prompt", "chatgpt", "midjourney", "artificial intelligence", " ai ", "llm", "model", "agent", "claude", "gemini"]),
    ("Technology & Development", ["developer", "programmer", "programming", "software", "python", "javascript", "typescript", "java ", "golang", "rust ", "sql", "linux", "terminal", "console", "frontend", "backend", "fullstack", "web design", "ux/ui", "cyber", "security", "devops", "database", "api", "regex", "blockchain", "ethereum", "machine learning", "data engineer", "it architect", "system engineer", "code reviewer", "svg"]),
    ("Writing & Language", ["writer", "writing", "translator", "translation", "grammar", "proofread", "editor", "novelist", "poet", "poetry", "screenwriter", "journalist", "essay", "title generator", "synonym", "pronunciation", "language", "elocution", "copywriter", "paraphrase"]),
    ("Research & Analysis", ["research", "analyst", "analysis", "statistician", "scientist", "critic", "reviewer", "fact", "fallacy", "debater", "debate", "historian", "philosopher", "journal reviewer", "auditor", "investigator"]),
    ("Work & Career", ["interviewer", "interview", "recruiter", "career", "resume", "curriculum", "cover letter", "meeting", "manager", "chief executive", "ceo", "leadership", "hr ", "human resources", "project manager", "product manager", "talent coach", "public speaking coach"]),
    ("Learning & Education", ["teacher", "tutor", "instructor", "school", "student", "study", "exam", "academician", "professor", "education", "educational", "lesson", "learning", "math teacher", "philosophy teacher", "coach for interviews"]),
    ("Creative & Content", ["storyteller", "artist", "composer", "music", "designer", "design", "photograph", "film", "movie", "social media", "influencer", "content creator", "creative", "advertiser", "stand-up", "comedian", "rapper", "magician", "gallery", "makeup artist"]),
    ("Business & Marketing", ["advertiser", "marketing", "sales", "salesperson", "business", "startup", "entrepreneur", "financial", "finance", "accountant", "investment", "real estate", "e-commerce", "brand", "campaign", "logistician"]),
    ("Health & Wellness", ["doctor", "dentist", "dietitian", "psychologist", "therap", "mental health", "medical", "health", "nutrition", "yogi", "personal trainer", "hypnotherapist", "first aid", "emergency response"]),
    ("Lifestyle & Personal", ["travel", "chef", "food", "stylist", "interior", "florist", "personal shopper", "pet", "relationship", "life coach", "self-help", "babysitter", "automobile mechanic", "tea-taster", "dream interpreter"]),
    ("Tools & Simulations", ["terminal", "console", "interpreter", "text based", "game", "web browser", "excel", "calculator", "generator", "navigation system", "simulator", "shell", "tic-tac-toe", "password generator"]),
]

SUB_RULES = {
    "AI & Prompting": [("Prompt Design", ["prompt"]),("Image AI", ["midjourney","image"]),("AI Agents", ["agent"]),("General AI", [])],
    "Technology & Development": [("Coding & Engineering", ["developer","programmer","code","frontend","backend","fullstack","python","javascript","java ","golang","rust"]),("Data & AI", ["machine learning","data","sql","database"]),("Security & IT", ["security","cyber","it ","system","linux","network"]),("Web & Product", ["ux","ui","web design","product"]),("General Tech", [])],
    "Writing & Language": [("Translation & Language", ["translator","translation","language","pronunciation","grammar","synonym"]),("Creative Writing", ["novelist","poet","screenwriter","story"]),("Editing & Improvement", ["proofread","editor","rewrite","improve"]),("Professional Writing", [])],
    "Research & Analysis": [("Evidence & Research", ["research","fact","investigator"]),("Review & Critique", ["critic","reviewer","auditor"]),("Reasoning & Debate", ["debate","fallacy","philosopher"]),("Data & Statistics", ["analyst","statistician","data"]),("General Analysis", [])],
    "Work & Career": [("Hiring & Interviews", ["interview","recruiter","resume","career","talent"]),("Leadership & Management", ["manager","ceo","leadership"]),("Meetings & Communication", ["meeting","public speaking"]),("General Work", [])],
    "Learning & Education": [("Teaching", ["teacher","tutor","instructor","lesson"]),("Study & Exams", ["study","exam","student"]),("Academic", ["academician","professor"]),("General Learning", [])],
    "Creative & Content": [("Social & Marketing Content", ["social media","influencer","advertiser","content"]),("Stories & Scripts", ["story","film","movie","screenwriter"]),("Art & Design", ["artist","designer","makeup","gallery"]),("Music & Performance", ["music","composer","rapper","comedian"]),("General Creative", [])],
    "Business & Marketing": [("Marketing & Sales", ["marketing","sales","advertiser","campaign","brand"]),("Finance & Investment", ["finance","financial","accountant","investment"]),("Startup & Strategy", ["startup","entrepreneur","business"]),("Operations", ["logistic"]),("General Business", [])],
    "Health & Wellness": [("Medical", ["doctor","dentist","medical","first aid","emergency"]),("Mental Wellness", ["psychologist","mental health","therap","hypno"]),("Fitness & Nutrition", ["diet","nutrition","trainer","yogi"]),("General Wellness", [])],
    "Lifestyle & Personal": [("Travel", ["travel"]),("Food & Home", ["chef","food","interior","florist","tea"]),("Style & Shopping", ["stylist","shopper"]),("Relationships & Coaching", ["relationship","life coach","self-help"]),("General Lifestyle", [])],
    "Tools & Simulations": [("Developer Simulators", ["terminal","console","interpreter","shell"]),("Games & Interactive", ["game","tic-tac-toe"]),("Generators", ["generator"]),("Utilities", [])],
}

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

def category_for(title, prompt):
    text = f" {title} {prompt[:800]} ".lower()
    best=(0,"Other Expert Roles")
    for cat, keys in CATEGORY_RULES:
        score=sum(1 for k in keys if k in text)
        if score>best[0]: best=(score,cat)
    return best[1]

def subcategory_for(category, title, prompt):
    text=f" {title} {prompt[:500]} ".lower()
    rules=SUB_RULES.get(category)
    if not rules:return "Specialist Roles"
    for sub,keys in rules:
        if not keys or any(k in text for k in keys):return sub
    return rules[-1][0]

def description_for(title,prompt):
    t=norm(prompt)
    t=re.sub(r"(?i)^i want you to act as (an?|my)\s+", "Acts as ", t)
    t=re.sub(r"(?i)^act as (an?|my)?\s*", "Acts as ", t)
    end=re.search(r"(?<=[.!?])\s",t)
    if end and end.start()<180:t=t[:end.start()+1]
    if len(t)>180:t=t[:177].rstrip()+"…"
    if not t:return f"Full prompt for {title}."
    return t

def main():
    if len(sys.argv)<3:
        raise SystemExit("usage: build_prompt_library.py INPUT.csv OUTPUT.json [LIMIT]")
    src=Path(sys.argv[1]);out=Path(sys.argv[2]);limit=int(sys.argv[3]) if len(sys.argv)>3 else 2160
    with src.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        fields={k.lower().strip():k for k in (reader.fieldnames or [])}
        title_key=fields.get("act") or fields.get("title") or fields.get("name")
        prompt_key=fields.get("prompt") or fields.get("content") or fields.get("text")
        if not title_key or not prompt_key:raise SystemExit(f"Unsupported CSV columns: {reader.fieldnames}")
        rows=[]
        for row in reader:
            title=norm(row.get(title_key));prompt=norm(row.get(prompt_key))
            if not title or not prompt:continue
            cat=category_for(title,prompt);sub=subcategory_for(cat,title,prompt)
            rows.append({"id":len(rows)+1,"title":title,"category":cat,"subcategory":sub,"description":description_for(title,prompt),"prompt":prompt})
            if len(rows)>=limit:break
    if len(rows)!=limit:raise SystemExit(f"Expected {limit} prompts, found {len(rows)}")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    from collections import Counter
    print(f"Built {len(rows)} prompts")
    for k,v in Counter(r["category"] for r in rows).most_common():print(f"{k}: {v}")
if __name__=="__main__":main()
