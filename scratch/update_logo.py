import shutil
import base64
import re
from pathlib import Path

src = Path(r"C:\Users\GaneshSriKumarMarimu\.gemini\antigravity\brain\a82e2717-9243-4800-b82c-5c404381dc54\.user_uploaded\media_1794548578042_b8740ce6.png")
assets_dir = Path("ui/assets")
assets_dir.mkdir(parents=True, exist_ok=True)

raw_bytes = src.read_bytes()
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
    shutil.copy2(src, dst)
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
    theme_css.write_text(css_text, encoding="utf-8")
    print("Updated theme.css background-image with new logo base64!")
else:
    print("WARNING: regex match failed in theme.css")

