#!/usr/bin/env python3
import json,re,sys,urllib.request
from pathlib import Path

OUT=Path(sys.argv[1] if len(sys.argv)>1 else 'android/app/src/main/assets/curated_photo_prompts.json')

TECH_URL='https://academy.techpresso.co/prompts/chatgpt-prompts-photos'
RANDOM_URL='https://randomprompts.org/chatgpt-photo-editing-prompts'
META_URL='https://ai.meta.com/learn/ai-creativity/ai-photo-editing-prompts/'
STYLE_URL='https://github.com/roblaughter/style-reference'
STYLE_RAW='https://raw.githubusercontent.com/roblaughter/style-reference/master/README.md'

tech=[
('AI Selfies & Portraits','Professional Headshot from Description'),('AI Selfies & Portraits','Consistent Character Across Multiple Scenes'),('AI Selfies & Portraits','Couples or Group Portrait'),('AI Selfies & Portraits','Seasonal or Holiday Self-Portrait'),('AI Selfies & Portraits','Before and After Transformation Photo'),('AI Selfies & Portraits','Professional Bio Photo Set'),
('Photo Editing & Enhancement','Background Replacement'),('Photo Editing & Enhancement','Color Grading and Mood Shift'),('Photo Editing & Enhancement','Image Upscale and Detail Enhancement'),('Photo Editing & Enhancement','Object Removal and Scene Cleanup'),('Photo Editing & Enhancement','Lighting Correction'),('Photo Editing & Enhancement','Style Transfer Between Photos'),
('Product Photography','Clean Product Shot on White Background'),('Product Photography','Lifestyle Product Photo'),('Product Photography','Product Flat Lay Composition'),('Product Photography','Product Scale and Size Reference'),('Product Photography','Product Packaging Mockup'),('Product Photography','Multi-Angle Product Gallery'),
('Social Media Visuals','Instagram Post Visual'),('Social Media Visuals','LinkedIn Banner Image'),('Social Media Visuals','YouTube Thumbnail'),('Social Media Visuals','Story or Reel Cover Image'),('Social Media Visuals','Quote Card Visual'),('Social Media Visuals','Carousel Slide Series'),
('Creative & Artistic','Specific Art Style Rendering'),('Creative & Artistic','Surreal Photo Manipulation Concept'),('Creative & Artistic','Digital Illustration in Specific Medium'),('Creative & Artistic','Comic or Graphic Novel Panel'),('Creative & Artistic','Abstract Art for Wall Decor'),
('Holiday & Event Photos','Christmas Card Photo'),('Holiday & Event Photos','Birthday Party Invitation Visual'),('Holiday & Event Photos','Wedding or Engagement Announcement'),('Holiday & Event Photos','Halloween Costume Concept'),('Holiday & Event Photos','Graduation Photo'),('Holiday & Event Photos','Event Promotional Graphic'),('Holiday & Event Photos','Seasonal Business Promotion Visual'),
('Trending & Viral Image Styles','Boxed Action Figure of Yourself'),('Trending & Viral Image Styles','3D Collectible Figurine on a Desk'),('Trending & Viral Image Styles','Retro Polaroid Snapshot'),('Trending & Viral Image Styles','Crochet Plushie Version of You'),('Trending & Viral Image Styles','Classic Hand-Painted Anime Portrait'),('Trending & Viral Image Styles','90s Yearbook Photo'),('Trending & Viral Image Styles','Your Pet as a Renaissance Portrait'),('Trending & Viral Image Styles','Tiny Miniature Diorama World'),('Trending & Viral Image Styles','Custom Sticker Pack of You'),('Trending & Viral Image Styles','Fantasy RPG Hero Avatar'),('Trending & Viral Image Styles','Authentic 35mm Film Look'),('Trending & Viral Image Styles','Stylized Caricature Cartoon')]

random_titles=[
('Professional Editing','Professional Portrait Enhancement'),('Film & Vintage','Vintage Film Aesthetic'),('Color & Lighting','Dramatic Cinematic Color Grading'),('Landscape & Travel','Natural Landscape Enhancement'),('Portraits & People','High-Fashion Editorial Look'),('Cinematic & Moody','Moody Dark & Atmospheric')]

meta=[
('Enhance & Restore','Clarity and Contrast Boost'),('Enhance & Restore','Photo Damage Restoration'),('Enhance & Restore','Crisp Professional Finish'),
('Background & Cleanup','Pure White Background Replacement'),('Background & Cleanup','Green Gradient Background Replacement'),('Background & Cleanup','Gray Subject Cutout Background'),
('Background & Cleanup','Remove Power Lines'),('Background & Cleanup','Remove Backpack'),('Background & Cleanup','Remove Wall Shadow'),
('Color & Lighting','Reduce Color Saturation'),('Portraits & People','Correct Skin Tone While Preserving Texture'),('Portraits & People','Darken Subject Hair Naturally'),
('Color & Lighting','Soft Pastel Aesthetic'),('Cinematic & Moody','Dramatic High-Contrast Editorial Style'),('Film & Vintage','Vintage Faded Photo Look'),
('Creative Transformations','Animated Princess Transformation'),('Creative Transformations','Video Game Hero Transformation'),('Creative Transformations','Dreamlike Fantasy Transformation'),
('Framing & Composition','Center the Subject'),('Framing & Composition','Zoom Out and Expand the Frame'),('Framing & Composition','Tight Crop Around the Subject'),
('Product Photography','High-Contrast Product Pop'),('Product Photography','Clean Studio-Quality Product Look'),('Product Photography','Add Ingredients Around the Product'),
('Social & Marketing','Social Media Color and Zoom Boost'),('Portraits & People','Natural Smile Toward Camera'),('Social & Marketing','Bold How-To Text Overlay'),
('Illustration & Art','Anime Photo Transformation'),('Illustration & Art','Watercolor Portrait Transformation'),('Illustration & Art','3D Cartoon Animation Look')]

def slug(s):
    x=re.sub(r'[^A-Za-z0-9]+','',s)
    return (x or 'PhotoPrompt')[:42]

def subcategory(title,source_cat=''):
    s=(title+' '+source_cat).lower()
    if any(k in s for k in ['headshot','portrait','selfie','character','couple','group','bio photo','fashion','skin tone','hair','smile']):return 'Portraits & People'
    if any(k in s for k in ['background','remove ','removal','cleanup','cutout','shadow']):return 'Background & Cleanup'
    if any(k in s for k in ['upscale','restore','damage','clarity','crisp','enhance','detail']):return 'Enhance & Restore'
    if any(k in s for k in ['color','lighting','pastel','contrast','mood shift']):return 'Color & Lighting'
    if any(k in s for k in ['product','packaging','flat lay','e-commerce','ingredients']):return 'Product Photography'
    if any(k in s for k in ['instagram','linkedin','youtube','reel','story','quote card','carousel','social','promotional','business promotion','text overlay']):return 'Social & Marketing'
    if any(k in s for k in ['christmas','birthday','wedding','engagement','halloween','graduation','holiday','seasonal']):return 'Events & Seasonal'
    if any(k in s for k in ['polaroid','35mm','film','vintage','yearbook','retro']):return 'Film & Vintage'
    if any(k in s for k in ['cinematic','noir','moody','dramatic']):return 'Cinematic & Moody'
    if any(k in s for k in ['landscape','travel','nature','ocean','waterfall','outdoor']):return 'Landscape & Travel'
    if any(k in s for k in ['surreal','abstract','double exposure','ethereal','dreamlike','fantasy']):return 'Abstract & Surreal'
    if any(k in s for k in ['illustration','comic','watercolor','anime','art style','artistic','painting','ukiyo','caricature']):return 'Illustration & Art'
    if any(k in s for k in ['figurine','action figure','plushie','miniature','diorama','sticker']):return 'Miniature & Collectibles'
    if any(k in s for k in ['crop','reframe','zoom','composition','framing']):return 'Framing & Composition'
    return 'Creative Transformations'

def adapted_instruction(title,cat):
    sc=subcategory(title,cat)
    t=title.lower()
    base=f"Use the /{slug(title)} image workflow. Goal: {title}. "
    if sc=='Portraits & People':
        return base+"Work from the user's uploaded photo or physical description. Preserve recognizable identity, facial structure, skin texture, expression and body proportions unless the user explicitly asks to change them. Apply the requested portrait treatment with believable lighting, natural detail, clean subject separation and professional composition. Preserve all unspecified personal features."
    if sc=='Background & Cleanup':
        return base+"Edit only the requested background, object or distraction. Preserve the subject, pose, facial identity, camera perspective and every unrelated element. Reconstruct removed areas with matching texture, perspective, lighting, shadows and depth so the result looks natively photographed rather than composited."
    if sc=='Enhance & Restore':
        return base+"Improve clarity, resolution, exposure and fine detail without changing identity or scene geometry. Recover believable texture in skin, hair, fabric and surfaces; control noise and artifacts; protect highlights and shadows; avoid plastic smoothing, halos and invented details that alter the original subject."
    if sc=='Color & Lighting':
        return base+"Change only the requested color, contrast, light direction or mood while keeping composition and content stable. Maintain believable skin tones and material colors, preserve highlight and shadow detail, and make the grade feel photographic rather than filtered."
    if sc=='Product Photography':
        return base+"Create a premium commercial product image while preserving the product's exact geometry, materials, colors, branding and proportions. Use controlled studio-quality lighting, accurate reflections and shadows, clean composition and detail that remains credible for e-commerce or advertising."
    if sc=='Social & Marketing':
        return base+"Design the visual for its intended social or marketing placement. Keep the main subject immediately readable at thumbnail size, use strong hierarchy and clean negative space for text where relevant, preserve brand/product identity, and choose an aspect ratio and composition suited to the requested platform."
    if sc=='Events & Seasonal':
        return base+"Create a polished event or seasonal visual with coherent wardrobe, props, environment, color palette and lighting. Keep people recognizable when an uploaded photo is used, reserve clean space for required text when relevant, and avoid clutter or generic stock-photo styling."
    if sc=='Film & Vintage':
        return base+"Apply an authentic analog or period-photo treatment using coherent grain, contrast, halation, color response, lens character, flash or ambient-light behavior and era-appropriate texture. Preserve subject identity and composition; avoid fake overlays that do not interact naturally with the scene."
    if sc=='Cinematic & Moody':
        return base+"Turn the image into a convincing cinematic frame using motivated directional light, controlled contrast, dimensional shadows, atmospheric depth and filmic color. Preserve subject identity and the core scene; keep effects restrained enough to remain photographic."
    if sc=='Landscape & Travel':
        return base+"Enhance or generate the scene with believable atmospheric depth, natural color, detailed terrain and coherent sky/light conditions. Keep geography and major scene structure stable when editing a supplied photo, and avoid oversaturation or artificial HDR."
    if sc=='Abstract & Surreal':
        return base+"Create the requested surreal or abstract effect while keeping a strong visual anchor and coherent light, texture and perspective. If a person is present, preserve their recognizable identity. Make the impossible elements feel intentionally integrated rather than randomly composited."
    if sc=='Illustration & Art':
        return base+"Translate the subject into the requested illustrative medium using medium-specific linework, texture, shading, palette and surface behavior. Preserve recognizable subject features and composition unless the user requests a redesign; avoid a generic digital-filter look."
    if sc=='Miniature & Collectibles':
        return base+"Transform the subject into the requested collectible, miniature or toy-like form while retaining recognizable signature features, colors and accessories. Use convincing scale cues, material texture, product-style lighting and a coherent physical presentation."
    if sc=='Framing & Composition':
        return base+"Adjust framing exactly as requested while preserving the subject and scene. When expanding the frame, extend the environment consistently with perspective, lighting and texture; when cropping, protect important anatomy and visual balance."
    return base+"Apply this image direction faithfully to the user's request. Preserve identity, subject geometry and all unspecified content. Use coherent lighting, perspective, texture and composition, and make the result look intentional and professionally finished."

def style_instruction(title,prompt):
    natural=re.sub(r'\(([^:()]+):[0-9.]+\)',r'\1',prompt)
    return f"Use the /{slug(title)} photographic style. Apply this style to the user's subject or uploaded image while preserving identity, scene content and composition constraints. Translate any SDXL weighting syntax into natural-language emphasis when needed. Style characteristics: {natural}"

def parse_styles():
    with urllib.request.urlopen(STYLE_RAW,timeout=30) as r: text=r.read().decode('utf-8')
    out=[]
    for line in text.splitlines():
        if not line.startswith('|') or '![Image]' not in line: continue
        parts=[p.strip() for p in line.split('|')[1:-1]]
        if len(parts)<5: continue
        title=re.sub(r'\s*\*+\s*$','',parts[0]).strip()
        if not title or title.startswith(':') or title=='Style': continue
        style=parts[1].strip()
        if not style: continue
        imgs=re.findall(r'\((https://github\.com/roblaughter/style-reference/blob/[^)]+\?raw=true)\)',line)
        out.append((title,style,imgs))
    # The repository currently contains 114 style rows; cap deliberately so source growth does not silently change releases.
    out=out[:114]
    if len(out)!=114: raise SystemExit(f'Expected 114 style references, found {len(out)}')
    return out

def entry(title,source,source_url,source_cat='',example_mode='',example_urls=None,instruction=None):
    return {
      'command':slug(title),'category':'Photo Editing & Image Generation','subcategory':subcategory(title,source_cat),
      'description':f"{title} — {subcategory(title,source_cat).lower()} workflow.",
      'instruction':instruction or adapted_instruction(title,source_cat),
      'source':source,'source_url':source_url,'example_mode':example_mode,'example_urls':example_urls or []
    }

items=[]
for cat,title in tech: items.append(entry(title,'Techpresso AI Academy',TECH_URL,cat,'source_examples'))
for cat,title in random_titles: items.append(entry(title,'RandomPrompts.org',RANDOM_URL,cat,'source_examples'))
for cat,title in meta: items.append(entry(title,'Meta AI',META_URL,cat,'before_after'))
for title,prompt,imgs in parse_styles(): items.append(entry(title,'SDXL Style Reference',STYLE_URL,'Photographic Style Reference','results',imgs,style_instruction(title,prompt)))

# De-duplicate command slugs deterministically.
seen={}
for x in items:
    base=x['command'];n=seen.get(base,0)+1;seen[base]=n
    if n>1:x['command']=f'{base}{n}'

if len(items)!=198: raise SystemExit(f'Expected 198 curated photo prompts, found {len(items)}')
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built',len(items),'curated photo prompts')
from collections import Counter
for k,v in Counter(x['subcategory'] for x in items).most_common():print(f'{k}: {v}')
