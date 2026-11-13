import numpy as np
from PIL import Image
from scipy import ndimage

src_path = r"C:\Users\GaneshSriKumarMarimu\.gemini\antigravity\brain\a82e2717-9243-4800-b82c-5c404381dc54\.user_uploaded\media_1794548578042_b8740ce6.png"
img = Image.open(src_path).convert("RGBA")
arr = np.array(img, dtype=np.float32)

# Colors in 0-255:
# Green: R < 150, G > 130, B < 100
is_green = (arr[:, :, 0] < 150) & (arr[:, :, 1] > 130) & (arr[:, :, 2] < 100)
# Blue: R < 80, G < 150, B > 150
is_blue = (arr[:, :, 0] < 80) & (arr[:, :, 1] < 150) & (arr[:, :, 2] > 150)
# Yellow: R > 190, G > 130, B < 100
is_yellow = (arr[:, :, 0] > 190) & (arr[:, :, 1] > 130) & (arr[:, :, 2] < 100)
# Dark pupils: R < 80, G < 80, B < 100
is_dark = (arr[:, :, 0] < 80) & (arr[:, :, 1] < 80) & (arr[:, :, 2] < 100)

colored = is_green | is_blue | is_yellow | is_dark

# Mascot mask:
# Dilate by 16 px to connect eyes and white stripe, fill holes, erode back
dilated = ndimage.binary_dilation(colored, iterations=16)
filled = ndimage.binary_fill_holes(dilated)
mascot_mask = ndimage.binary_erosion(filled, iterations=16)

# Smooth the mask boundary with Gaussian blur for perfect anti-aliasing
mask_float = ndimage.gaussian_filter(mascot_mask.astype(np.float32), sigma=1.0)
mask_float = np.clip(mask_float * 1.2, 0.0, 1.0)

# Build result image
res = arr.copy()
res[:, :, 3] = res[:, :, 3] * mask_float

res_img = Image.fromarray(np.uint8(res))
# Crop to mascot bounding box with slight padding
ys, xs = np.where(mascot_mask)
pad = 12
ymin = max(0, ys.min() - pad)
ymax = min(512, ys.max() + pad)
xmin = max(0, xs.min() - pad)
xmax = min(512, xs.max() + pad)

cropped = res_img.crop((xmin, ymin, xmax, ymax))
# Resize to square 512x512
size = max(cropped.width, cropped.height)
square_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
offset_x = (size - cropped.width) // 2
offset_y = (size - cropped.height) // 2
square_img.paste(cropped, (offset_x, offset_y))
square_img = square_img.resize((512, 512), Image.Resampling.LANCZOS)

out_path = r"ui\assets\kairix_mascot_transparent.png"
square_img.save(out_path)
print(f"Saved transparent mascot to {out_path}, size={square_img.size}")

