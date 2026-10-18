# COPY of trace_badge.py for the French allies (2026-10-18), with two options for mod art drawn LIGHT ON A DARK
# background (e.g. the white-metal eagle of the Polish czapka, polandINF c0 r5):
#   claro=<lo>,<hi>  ink = luminance mapped from lo..hi to 0..1 (instead of alpha / 1 - darkness)
#   externos         keep only the outer outlines (loops with the orientation of the largest one): a solid silhouette,
#                    the inner detail comes from the art baked through UV "arte"
#   blur=<n>         n passes of a 3x3 box blur on the ink field before tracing (closes thin gaps)
#   blender -b --factory-startup --python trace_arte_aliados.py -- <image.png> <x0> <y0> <x1> <y1> <out.json> [iso] [eps_px]
#           [claro=0.12,0.40] [externos] [blur=2]
# Original description:
# Traces the outline of a badge drawn on a light background (Eras Mod atlas crop, authorised by the user) into
# closed polygons for extrusion (marching squares on an upsampled "ink" field, then Douglas-Peucker simplification).
# Output JSON: {"image": path, "box": [x0, y0, x1, y1] (crop pixels), "loops": [[[x, y], ...], ...]} with x, y in
# IMAGE PIXELS of the given box (y downwards), outer outlines and holes alike (the curve fill resolves nesting).
#   blender -b --factory-startup --python trace_badge.py -- <image.png> <x0> <y0> <x1> <y1> <out.json> [iso] [eps_px]
import bpy, sys, json, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
IMG, X0, Y0, X1, Y1, OUT = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]), a[5]
POS = [x for x in a[6:] if "=" not in x and x != "externos"]
ISO = float(POS[0]) if len(POS) > 0 else 0.16
EPS = float(POS[1]) if len(POS) > 1 else 0.55
UP = 3

im = bpy.data.images.load(IMG)
W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)[::-1]          # top row first
crop = px[Y0:Y1, X0:X1]
OPT = dict(x.split("=", 1) for x in a[6:] if "=" in x)
FLAGS = {x for x in a[6:] if "=" not in x}
if "claro" in OPT:                                                      # light art on a dark background
    lo, hi = (float(v) for v in OPT["claro"].split(","))
    lum = crop[..., :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    ink = np.clip((lum - lo) / (hi - lo), 0.0, 1.0)
elif crop[..., 3].min() < 0.5:                                          # the atlas cuts badges out with alpha
    ink = crop[..., 3].copy()
else:                                                                   # no alpha: white background
    ink = 1.0 - crop[..., :3].min(axis=2)
for _ in range(int(OPT.get("blur", 0))):
    p_ = np.pad(ink, 1, mode="edge")
    ink = sum(p_[1 + dy:1 + dy + ink.shape[0], 1 + dx:1 + dx + ink.shape[1]] for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9.0
ink = np.pad(ink, 2)                                                    # closed contours at the border
h, w = ink.shape
# bilinear upsample
ys = np.linspace(0, h - 1, (h - 1) * UP + 1)
xs = np.linspace(0, w - 1, (w - 1) * UP + 1)
y0 = np.floor(ys).astype(int).clip(0, h - 2); fy = (ys - y0)[:, None]
x0 = np.floor(xs).astype(int).clip(0, w - 2); fx = (xs - x0)[None, :]
F = (ink[y0][:, x0] * (1 - fx) + ink[y0][:, x0 + 1] * fx) * (1 - fy) + (ink[y0 + 1][:, x0] * (1 - fx) + ink[y0 + 1][:, x0 + 1] * fx) * fy
gh, gw = F.shape


def interp(p, q, vp, vq):
    t = (ISO - vp) / (vq - vp) if vq != vp else 0.5
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


segs = []
for i in range(gh - 1):
    for j in range(gw - 1):
        v = (F[i, j], F[i, j + 1], F[i + 1, j + 1], F[i + 1, j])           # tl, tr, br, bl
        c = sum(1 << k for k, val in enumerate(v) if val >= ISO)
        if c in (0, 15):
            continue
        P = [(j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1)]
        e = {0: interp(P[0], P[1], v[0], v[1]), 1: interp(P[1], P[2], v[1], v[2]),
             2: interp(P[2], P[3], v[2], v[3]), 3: interp(P[3], P[0], v[3], v[0])}
        table = {1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)], 5: [(3, 0), (1, 2)], 6: [(0, 2)], 7: [(3, 2)],
                 8: [(2, 3)], 9: [(2, 0)], 10: [(0, 1), (2, 3)], 11: [(2, 1)], 12: [(1, 3)], 13: [(1, 0)], 14: [(0, 3)]}
        for a_, b_ in table[c]:
            segs.append((e[a_], e[b_]))

# link segments into loops
key = lambda p: (round(p[0], 5), round(p[1], 5))
nxt = {}
for p, q in segs:
    nxt.setdefault(key(p), []).append(q)
used, loops = set(), []
for p, q in segs:
    if (key(p), key(q)) in used:
        continue
    loop = [p]
    cur, prev = q, p
    used.add((key(p), key(q)))
    for _ in range(len(segs) + 5):
        loop.append(cur)
        cands = [r for r in nxt.get(key(cur), []) if (key(cur), key(r)) not in used]
        if not cands:
            break
        r = cands[0]
        used.add((key(cur), key(r)))
        prev, cur = cur, r
        if key(cur) == key(loop[0]):
            break
    if len(loop) > 8:
        loops.append(loop)


def area(l):
    return 0.5 * sum(l[i][0] * l[i - 1][1] - l[i - 1][0] * l[i][1] for i in range(len(l)))


def dp(points, eps):
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0.0, 0
    for k in range(1, len(points) - 1):
        d = abs(dy * points[k][0] - dx * points[k][1] + x2 * y1 - y2 * x1) / L
        if d > dmax:
            dmax, idx = d, k
    if dmax > eps:
        return dp(points[:idx + 1], eps)[:-1] + dp(points[idx:], eps)
    return [points[0], points[-1]]


if "externos" in FLAGS and loops:                                       # outer outlines only
    big = max(loops, key=lambda l: abs(area(l)))
    loops = [l for l in loops if area(l) * area(big) > 0]
out = []
for l in loops:
    if abs(area(l)) < (4 * UP) ** 2:                                    # specks under ~4x4 crop pixels
        continue
    # split the closed loop in two halves for DP, then convert to crop pixels (remove pad and upsampling)
    half = len(l) // 2
    s = dp(l[:half + 1], EPS * UP)[:-1] + dp(l[half:] + [l[0]], EPS * UP)[:-1]
    out.append([[round(x / UP - 2, 3), round(y / UP - 2, 3)] for x, y in s])
json.dump({"image": IMG, "box": [X0, Y0, X1, Y1], "iso": ISO, "loops": out}, open(OUT, "w"))
print(f"TRACE {OUT}: {len(out)} loops, points per loop {[len(l) for l in out]}, "
      f"areas {[round(abs(area(l)) / UP / UP) for l in loops if abs(area(l)) >= (4 * UP) ** 2]}")
