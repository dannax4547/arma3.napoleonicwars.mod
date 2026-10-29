# Edge padding of baked / painted colour textures (2026-10-29, user: "aparece um preto nas partes brancas"): the bakes
# leave the space between UV islands exactly black (0,0,0) with only 2-4 px of margin, so the game's smaller mipmaps
# blend that black into the islands' edges (black seams, worst on white cloth). Every exactly-black pixel is filled
# by push-pull from the surrounding islands (average of the valid pixels at each coarser level, then back up), so the
# islands' own pixels stay identical and the background takes the colour of the nearest cloth.
#   blender -b --factory-startup --python preencher_fundo.py -- <png or folder> [...]
# Folders: every *_co.png in them (not recursive). Run after the bake / painter, before the PAA conversion.
import bpy, sys, os
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
files = []
for a in args:
    if os.path.isdir(a):
        files += sorted(os.path.join(a, f) for f in os.listdir(a) if f.lower().endswith("_co.png"))
    else:
        files.append(a)


def push_pull(col, valid):
    """col (H, W, 3) float, valid (H, W) bool -> col with the invalid pixels filled from the valid ones."""
    levels = []
    c, w = col * valid[..., None], valid.astype(np.float32)
    while c.shape[0] > 1 and c.shape[1] > 1 and c.shape[0] % 2 == 0 and c.shape[1] % 2 == 0:
        levels.append((c, w))
        h, wd = c.shape[0] // 2, c.shape[1] // 2
        c = c.reshape(h, 2, wd, 2, 3).sum(axis=(1, 3))
        w = w.reshape(h, 2, wd, 2).sum(axis=(1, 3))
    out = c / np.maximum(w, 1e-8)[..., None]
    for c, w in reversed(levels):
        up = np.repeat(np.repeat(out, 2, axis=0), 2, axis=1)
        out = np.where(w[..., None] > 0, c / np.maximum(w, 1e-8)[..., None], up)
    return out


for p in files:
    im = bpy.data.images.load(p)
    W, H, ch = im.size[0], im.size[1], im.channels
    a = np.empty(W * H * ch, np.float32)
    im.pixels.foreach_get(a)
    a = a.reshape(H, W, ch)
    rgb = a[..., :3]
    valid = (rgb * 255 + 0.5).astype(np.int16).max(axis=2) > 0
    share = 1.0 - valid.mean()
    if share == 0.0 or valid.sum() == 0:
        print(f"FUNDO {os.path.basename(p)}: sem fundo preto, nada a fazer")
        bpy.data.images.remove(im)
        continue
    a[..., :3] = push_pull(rgb, valid)
    if ch == 4:
        a[..., 3] = 1.0
    im.pixels.foreach_set(a.ravel())
    im.save()
    print(f"FUNDO {os.path.basename(p)}: {share:.1%} do fundo preenchido")
    bpy.data.images.remove(im)
