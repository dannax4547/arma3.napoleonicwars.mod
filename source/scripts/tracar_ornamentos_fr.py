# Turnback ornaments of the French elite coats, traced from the mod art (authorised Reto NTW atlas, FranceINF): the
# grenadier's grenade (tile c0 r3, red on the white turnbacks) and the voltigeur's hunting horn (tile c2 r3, yellow).
# Only the SHAPE is taken: alpha = the ornament's own colour against the white turnback (biggest connected blob in
# the search box), and its luminance inside the shape (embroidery detail, normalised); the colour painted in the game
# texture is ours (variant key "ornamento_cor"). Writes a square RGBA PNG per ornament (R=G=B detail, A shape).
#   blender -b --factory-startup --python tracar_ornamentos_fr.py -- <project root>
import bpy, sys, os
import numpy as np

ROOT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
TILES = os.path.join(ROOT, r"work\ntw\france\tiles")
OUT = os.path.join(ROOT, r"source\textures\hcl_uniforme_fr\ornamentos")
os.makedirs(OUT, exist_ok=True)
JOBS = [  # name, tile, search box x0, x1, y0, y1 (tile pixels, y down), colour test
    ("granada", "FranceINF_diffuse_c0_r3.png", 172, 212, 290, 345, lambda r, g, b: (r > 0.30) & (r > 2.0 * g) & (r > 2.0 * b)),
    ("corneta", "FranceINF_diffuse_c2_r3.png", 214, 262, 295, 340, lambda r, g, b: (r > 0.30) & (g > 0.22) & (b < 0.55 * g)),
    # 2026-10-12 (Old Guard): the small brass eagle on the turnbacks of the long-tailed coat (tile c3 r3, on blue)
    ("aguia", "FranceINF_diffuse_c3_r3.png", 220, 254, 241, 274, lambda r, g, b: (r > 0.17) & (r - b > 0.09)),
]
S = 128
for name, tile, x0, x1, y0, y1, test in JOBS:
    im = bpy.data.images.load(os.path.join(TILES, tile))
    W, H = im.size
    px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)[::-1]          # row 0 = top
    box = px[y0:y1, x0:x1, :3]
    m = test(box[..., 0], box[..., 1], box[..., 2])
    # biggest 4-connected blob
    lab = np.zeros(m.shape, np.int32); n = 0; sizes = {}
    for y in range(m.shape[0]):
        for x in range(m.shape[1]):
            if m[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n; c = 0
                while st:
                    a, b = st.pop(); c += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = a + dy, b + dx
                        if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1] and m[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n; st.append((yy, xx))
                sizes[n] = c
    big = max(sizes, key=sizes.get)
    blob = lab == big
    # close small holes inside the shape (dark embroidery lines inside the ornament belong to it)
    ys, xs = np.nonzero(blob)
    ya, yb, xa, xb = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = blob[ya:yb, xa:xb].copy()
    outside = np.zeros_like(sub)
    st = [(y, x) for y in range(sub.shape[0]) for x in (0, sub.shape[1] - 1) if not sub[y, x]] + \
         [(y, x) for x in range(sub.shape[1]) for y in (0, sub.shape[0] - 1) if not sub[y, x]]
    for p in st:
        outside[p] = True
    while st:
        a, b = st.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = a + dy, b + dx
            if 0 <= yy < sub.shape[0] and 0 <= xx < sub.shape[1] and not sub[yy, xx] and not outside[yy, xx]:
                outside[yy, xx] = True; st.append((yy, xx))
    shape = ~outside
    lum = box[ya:yb, xa:xb].mean(axis=2)
    li = lum[shape]
    det = np.clip((lum - li.min()) / max(li.max() - li.min(), 1e-6), 0, 1) * shape
    # square canvas, upsampled (nearest, then 3x3 box blur for a soft edge)
    side = max(sub.shape) + 2
    can_a = np.zeros((side, side), np.float32); can_d = np.zeros((side, side), np.float32)
    oy, ox = (side - sub.shape[0]) // 2, (side - sub.shape[1]) // 2
    can_a[oy:oy + sub.shape[0], ox:ox + sub.shape[1]] = shape
    can_d[oy:oy + sub.shape[0], ox:ox + sub.shape[1]] = det
    idx = (np.arange(S) * side / S).astype(int)
    A = can_a[idx][:, idx]; D = can_d[idx][:, idx]
    for _ in range(2):
        A = sum(np.roll(np.roll(A, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
        D = sum(np.roll(np.roll(D, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    out = bpy.data.images.new(name, S, S, alpha=True)
    rgba = np.dstack([D, D, D, A])[::-1].astype(np.float32)
    out.pixels.foreach_set(rgba.ravel())
    out.filepath_raw = os.path.join(OUT, name + ".png"); out.file_format = "PNG"; out.save()
    print(f"ORNAMENTO {name}: {tile} caixa x {x0}-{x1} y {y0}-{y1}; forma {sub.shape[1]}x{sub.shape[0]} px do atlas, "
          f"{int(shape.sum())} px; gravado {out.filepath_raw}")
