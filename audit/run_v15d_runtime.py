#!/usr/bin/env python3
from pathlib import Path
src=Path('audit/test_v15c_runtime.py').read_text(encoding='utf-8')
src=src.replace("OUT=Path('/tmp/promptdeck-v15c-runtime')","OUT=Path('/tmp/promptdeck-v15d-runtime')")
src=src.replace("tap('Images & Design');time.sleep(.4)\n    if not has('Choose what you want to do'):raise AssertionError('subcategory level missing')\n    if not(has('Photo Editing & Restore') or has('Image Generation')):raise AssertionError('image subcategories missing')","tap('Writing & Communication');time.sleep(.4)\n    if not has('Choose what you want to do'):raise AssertionError('subcategory level missing')\n    if not has('Rewrite & Polish'):raise AssertionError('writing subcategories missing: '+repr(txts()[:100]))")
src=src.replace("adb('shell','settings','put','system','user_rotation','1',check=False);time.sleep(1.0)\n    vis=' | '.join(txts()).lower();", "adb('shell','settings','put','system','user_rotation','1',check=False);time.sleep(.2);wait_ui(3)\n    vis=' | '.join(txts()).lower();")
if "tap('Images & Design')" in src:raise SystemExit('browse replacement failed')
if "wait_ui(3)" not in src:raise SystemExit('recreation wait replacement failed')
exec(compile(src,'audit/test_v15d_runtime.generated.py','exec'),{'__name__':'__main__'})
