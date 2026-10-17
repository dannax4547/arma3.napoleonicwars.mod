# Brass mask for badges drawn WITHOUT alpha on the dark felt of the British shako art (atlas britainINF, Reto pack,
# authorised): writes a copy of the atlas whose alpha, inside the given boxes, is 1 on brass and 0 elsewhere, so
# trace_badge.py (alpha mode) can trace them with the atlas pixel coordinates unchanged. Only reads the atlas.
#   blender -b --factory-startup --python mascara_latao_uk.py -- <atlas.png> <out.png> x0,y0,x1,y1 [...]
import bpy, sys
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
im = bpy.data.images.load(a[0]); W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)[::-1].copy()      # top row first
for box in a[2:]:
    x0, y0, x1, y1 = map(int, box.split(","))
    c = px[y0:y1, x0:x1]
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    brass = np.clip((r - 0.16) / 0.06, 0, 1) * np.clip(((r - b) - 0.08) / 0.05, 0, 1)
    c[..., 3] = brass
    print(f"caixa {box}: latao {float((brass > 0.5).mean()) * 100:.1f}%")
out = bpy.data.images.new("mascara", W, H, alpha=True)
out.pixels.foreach_set(px[::-1].ravel())
out.filepath_raw = a[1]; out.file_format = "PNG"; out.save()
print("OK", a[1])
