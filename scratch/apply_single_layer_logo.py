import shutil
import base64
import re
from pathlib import Path

mascot_path = Path("ui/assets/kairix_mascot_transparent.png")
assets_dir = Path("ui/assets")

raw_bytes = mascot_path.read_bytes()
b64_str = base64.b64encode(raw_bytes).decode("utf-8")

# 1. Update asset png files
for fname in [
    "kairix_squircle_badge.png",
    "kairix_emblem_transparent.png",
    "kairix_emblem.png",
    "kairix_logo.png",
    "kairix_nav_icon.png",
]:
    dst = assets_dir / fname
    shutil.copy2(mascot_path, dst)
    print(f"Updated {dst} ({dst.stat().st_size} bytes)")

# 2. Update b64 text files
(assets_dir / "kairix_icon_b64.txt").write_text(b64_str, encoding="utf-8")
(assets_dir / "icon_b64.txt").write_text(b64_str, encoding="utf-8")
print("Updated b64 text files")

# 3. Update ui/styles/theme.css line 1977
theme_css = Path("ui/styles/theme.css")
css_text = theme_css.read_text(encoding="utf-8")

pattern = re.compile(r'background-image:\s*url\("data:image/png;base64,[^"]+"\)\s*!important;')
match = pattern.search(css_text)
if match:
    new_rule = f'background-image: url("data:image/png;base64,{b64_str}") !important;'
    css_text = css_text[:match.start()] + new_rule + css_text[match.end():]
    
    # Also adjust background-size to 30px 30px for perfect single-layer proportion
    css_text = re.sub(
        r'background-size:\s*\d+px\s+\d+px\s*!important;',
        'background-size: 30px 30px !important;',
        css_text,
        count=1
    )
    
    theme_css.write_text(css_text, encoding="utf-8")
    print("Updated theme.css with transparent mascot and background-size: 30px 30px!")
else:
    print("WARNING: regex match failed in theme.css")

