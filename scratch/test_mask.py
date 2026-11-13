import numpy as np
from PIL import Image

src_path = r"C:\Users\GaneshSriKumarMarimu\.gemini\antigravity\brain\a82e2717-9243-4800-b82c-5c404381dc54\.user_uploaded\media_1794548578042_b8740ce6.png"
img = Image.open(src_path).convert("RGBA")
arr = np.array(img)

# Mascot color conditions:
# Green: [90-130, 160-210, 30-70]
is_green = (arr[:, :, 0] < 150) & (arr[:, :, 1] > 130) & (arr[:, :, 2] < 100)
# Blue: [20-60, 70-130, 170-240]
is_blue = (arr[:, :, 0] < 80) & (arr[:, :, 1] < 150) & (arr[:, :, 2] > 150)
# Yellow beak: [220-255, 150-200, 20-80]
is_yellow = (arr[:, :, 0] > 190) & (arr[:, :, 1] > 130) & (arr[:, :, 2] < 100)
# Dark pupils: [20-70, 30-80, 40-100]
is_dark = (arr[:, :, 0] < 80) & (arr[:, :, 1] < 80) & (arr[:, :, 2] < 100) & (arr[:, :, 3] > 100)

colored = is_green | is_blue | is_yellow | is_dark

# Find bounding box of colored pixels
ys, xs = np.where(colored)
min_y, max_y = ys.min(), xs.min()
print(f"Colored bounds: Y=[{ys.min()}, {ys.max()}], X=[{xs.min()}, {xs.max()}]")

# Now let's find the convex hull or alpha mask for the mascot
# The mascot is completely contained within Y in [90, 420] and X in [95, 415]
# Any pixel outside [85, 425] x [90, 420] is definitely the white squircle or drop shadow!
# Let's verify what happens if we mask out everything outside [85, 425] x [90, 420]:
print("Pixels outside mascot box with colored content:", np.sum(colored & ~((arr[:, :, 3] > 0))))

