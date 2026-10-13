# Side-by-side / grid composition of PNG renders (for before/after report images), inside Blender (no PIL needed).
#   blender -b --factory-startup --python juntar_imagens.py -- <out.png> <cols> <img1> <img2> ... [rotulos=A|B|C]
# All images are scaled to the height of the first one; a light gap separates them. Labels are not drawn (Blender has
# no text raster here): the report text names each panel in order.
import bpy, sys, os
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
OUT, COLS = os.path.abspath(a[0]), int(a[1])
paths = [os.path.abspath(p) for p in a[2:] if "=" not in p]
GAP = 12


def load(p):
    im = bpy.data.images.load(p)
    w, h = im.size
    px = np.array(im.pixels[:], np.float32).reshape(h, w, 4)
    return px


imgs = [load(p) for p in paths]
H = imgs[0].shape[0]
scaled = []
for im in imgs:
    h, w = im.shape[:2]
    if h != H:                                         # nearest-neighbour rescale to the common height
        W = int(round(w * H / h))
        yi = (np.arange(H) * h / H).astype(int)
        xi = (np.arange(W) * w / W).astype(int)
        im = im[yi][:, xi]
    scaled.append(im)
rows = [scaled[i:i + COLS] for i in range(0, len(scaled), COLS)]
row_w = [sum(im.shape[1] for im in r) + GAP * (len(r) - 1) for r in rows]
TW, TH = max(row_w), H * len(rows) + GAP * (len(rows) - 1)
canvas = np.ones((TH, TW, 4), np.float32)
canvas[..., :3] = 0.93
# rows are stacked top to bottom (Blender pixel rows start at the bottom)
for ri, r in enumerate(rows):
    y0 = TH - (ri + 1) * H - ri * GAP
    x = 0
    for im in r:
        canvas[y0:y0 + H, x:x + im.shape[1]] = im
        x += im.shape[1] + GAP
out = bpy.data.images.new("juntar", TW, TH, alpha=True)
out.pixels.foreach_set(canvas.ravel())
out.filepath_raw = OUT
out.file_format = "PNG"
out.save()
print("OK", OUT, TW, "x", TH)
