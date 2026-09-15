#!/usr/bin/env python3
from pathlib import Path
import json, re

catalog_path = Path('android/app/src/main/assets/final_catalog_v15.json')
gradle_path = Path('android/app/build.gradle')

catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
if not isinstance(catalog, list):
    raise SystemExit('final_catalog_v15.json must be a JSON array')

source = 'Akashgraphxic — 8 AI Color Grading Prompts to Transform Ordinary Photos Into Cinematic Visuals'
prompts = [
    {
        'command': 'WarmGoldenHourColorGrade',
        'description': 'Warm cinematic golden-hour color grade with amber highlights, soft contrast, natural skin tones and controlled saturation.',
        'instruction': 'Color grade the uploaded photo into a warm cinematic golden-hour look. Preserve the original subject, composition, skin tone, details and lighting direction. Add rich golden highlights, warm amber sunlight, subtle orange tones, soft contrast, gentle shadows and a natural cinematic film look. Keep the image realistic and sophisticated, with beautiful sunset warmth and controlled saturation. Do not alter the subject or background elements.'
    },
    {
        'command': 'MoodyCinematicColorGrade',
        'description': 'Moody modern-film grade with deeper blacks, controlled highlights, cool tones and realistic skin texture.',
        'instruction': 'Transform the uploaded photo into a moody cinematic color grade. Preserve the exact composition, subject, facial features and environment. Create deeper blacks, controlled highlights, slightly desaturated colors, rich shadows and subtle cool tones. Add cinematic contrast while maintaining realistic skin tones and natural textures. The final image should feel like a frame from a sophisticated modern film, dramatic but realistic.'
    },
    {
        'command': 'TealOrangeColorGrade',
        'description': 'Balanced teal-and-orange cinematic grade with cool shadows, warm highlights and natural skin tones.',
        'instruction': 'Apply a professional teal and orange cinematic color grade to the uploaded photo. Preserve the original subject, composition, skin texture and environment. Introduce subtle teal tones into the shadows and richer warm orange tones into skin, sunlight and highlights. Create balanced cinematic contrast, controlled saturation and natural skin tones. Keep the result realistic, premium and similar to a professionally color-graded movie still.'
    },
    {
        'command': 'FilmFadeColorGrade',
        'description': 'Premium analog-film grade with lifted blacks, muted highlights, warm tones and refined 35mm character.',
        'instruction': 'Give the uploaded photo a premium analog film color grade. Preserve the original composition, subject and details. Create slightly lifted blacks, soft contrast, muted highlights, subtle warm tones and gentle color fading inspired by high-end 35mm film photography. Add a refined filmic character without adding artificial grain or changing the subject. Keep skin tones natural and the overall image elegant, nostalgic and realistic.'
    },
    {
        'command': 'DarkLuxuryColorGrade',
        'description': 'Dark luxury editorial grade with rich blacks, restrained highlights and premium tonal separation.',
        'instruction': 'Color grade the uploaded photo into a dark luxury editorial style. Preserve the exact subject, composition and details. Deepen the shadows, create rich blacks, control bright highlights and introduce sophisticated neutral and slightly warm tones. Increase depth and tonal separation without making the image look artificial. The final result should resemble a high-end luxury fashion campaign with cinematic contrast and premium color grading.'
    },
    {
        'command': 'CoolCleanColorGrade',
        'description': 'Clean cool-toned editorial grade with subtle blue-gray tones, neutral whites and controlled contrast.',
        'instruction': 'Transform the uploaded photo into a clean cool-toned editorial color grade. Preserve the original image, subject and composition. Introduce subtle blue and cool gray tones, clean highlights, neutral whites and controlled contrast. Keep skin tones realistic where applicable. Create a sophisticated modern photography aesthetic with a fresh, minimal and professional appearance. Avoid excessive blue saturation or unnatural colors.'
    },
    {
        'command': 'VintageSummerColorGrade',
        'description': 'Nostalgic summer-film grade with warm sunlight, creamy highlights, faded color and gentle pastel tones.',
        'instruction': 'Transform the uploaded photo into a nostalgic vintage summer film look. Preserve the original subject, composition and details. Add warm sunlight, slightly faded colors, creamy highlights, soft contrast, subtle yellow and orange tones and gentle pastel colors. Keep the skin tones natural and the scene realistic. Create the feeling of a beautifully scanned analog summer photograph from a premium lifestyle campaign.'
    },
    {
        'command': 'MatteEditorialColorGrade',
        'description': 'Sophisticated matte editorial grade with soft blacks, muted saturation and understated tonal separation.',
        'instruction': 'Apply a sophisticated matte editorial color grade to the uploaded photo. Preserve the original subject, facial features, composition and environment. Create soft blacks, restrained highlights, muted saturation, subtle neutral tones and elegant tonal separation. Maintain realistic skin tones and natural textures. The final image should resemble a premium fashion magazine photograph with refined, understated and modern color grading.'
    },
]

def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())

seen_body = {norm(x.get('instruction','')) for x in catalog if isinstance(x, dict)}
seen_cmd = {x.get('command','') for x in catalog if isinstance(x, dict)}
max_id = max([int(x.get('id',0) or 0) for x in catalog if isinstance(x, dict)] or [0])
added = []
for item in prompts:
    if norm(item['instruction']) in seen_body:
        continue
    command = item['command']
    if command in seen_cmd:
        base = command + 'Akash'
        command = base
        n = 2
        while command in seen_cmd:
            command = f'{base}{n}'
            n += 1
    max_id += 1
    out = {
        'id': max_id,
        'command': command,
        'category': 'Images & Design',
        'subcategory': 'Color & Mood',
        'description': item['description'],
        'instruction': item['instruction'],
        'source': source,
    }
    catalog.append(out)
    seen_body.add(norm(item['instruction']))
    seen_cmd.add(command)
    added.append(command)

if len(added) != 8:
    raise SystemExit(f'Expected 8 new prompts, added {len(added)}: {added}')

catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

g = gradle_path.read_text(encoding='utf-8')
g = re.sub(r'versionCode\s+\d+', 'versionCode 45', g, count=1)
g = re.sub(r"versionName\s+'[^']+'", "versionName '0.8.8'", g, count=1)
gradle_path.write_text(g, encoding='utf-8')

# Static gates
check = json.loads(catalog_path.read_text(encoding='utf-8'))
for name in [p['command'] for p in prompts]:
    if not any(x.get('command') == name for x in check):
        raise SystemExit(f'Missing prompt {name}')
if not all(any(x.get('instruction') == p['instruction'] and x.get('category') == 'Images & Design' and x.get('subcategory') == 'Color & Mood' for x in check) for p in prompts):
    raise SystemExit('One or more color grading prompt payloads are incorrect')
if 'versionCode 45' not in gradle_path.read_text() or "versionName '0.8.8'" not in gradle_path.read_text():
    raise SystemExit('Version gate failed')
print('Added 8 Akashgraphxic color grading prompts; PromptDeck 0.8.8 (45)')
