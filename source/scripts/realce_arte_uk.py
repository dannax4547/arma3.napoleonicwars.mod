# Levels for dark badge art (britainINF c3 r4: the stovepipe plate and the bugle are drawn darker and flatter than the
# Belgic plate): writes a COPY of the atlas whose pixels inside the given boxes are stretched so that the brass of the
# badge spans the luminance range texturizar_shako_uk.py maps to relief (0.08 .. 0.55). Only reads the atlas; the copy
# is then passed to the baker with atlas=<copy name>.
#   blender -b --factory-startup --python realce_arte_uk.py -- <atlas.png> <out.png> x0,y0,x1,y1 [...]
import bpy, sys
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
im = bpy.data.images.load(a[0]); W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)[::-1].copy()       # top row first
for box in a[2:]:
    x0, y0, x1, y1 = map(int, box.split(","))
    c = px[y0:y1, x0:x1, :3]
    lum = c @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    brass = (c[..., 0] - c[..., 2]) > 0.08
    lo, hi = np.percentile(lum[brass], 2), np.percentile(lum[brass], 98)
    k = (0.55 - 0.08) / max(hi - lo, 1e-3)
    out = (c - lo) * k + 0.08
    px[y0:y1, x0:x1, :3] = np.clip(np.where(brass[..., None], out, c), 0, 1)
    print(f"caixa {box}: luminancia do latao {lo:.3f}..{hi:.3f} -> 0.08..0.55 (x{k:.2f})")
o = bpy.data.images.new("realce", W, H, alpha=True)
o.pixels.foreach_set(px[::-1].ravel())
o.filepath_raw = a[1]; o.file_format = "PNG"; o.save()
print("OK", a[1])
