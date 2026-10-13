# Relief of the brass front plate of the Old Guard bearskin (v5, 2026-10-13, user: "agora de mais realismo na barretina
# da velha guarda"). The mod art of the plate (FranceINF c2 r4, Reto pack, authorised) is only 180 x 72 px, so the
# relief baked from it was a blur. This script redraws the same layout at 8 px/mm as a height map:
#   - outline: the traced outline of placa_bonnet_guarda.json, smoothed (straight top, upright upper corners, the
#     sides narrowing to a rounded point), 217 x 153 mm (docs/specs/velha_guarda.md section 4);
#   - a raised rim and a row of beads inside it (stamped plates; 🔶 bead row);
#   - the imperial eagle in the middle, head to its right (viewer's left), wings spread, standing on a thunderbolt
#     (🎮 eagle with spread wings between grenades in the mod art; drawing of the details 🔶);
#   - a flaming grenade on each side (🎮), a small oval boss at the point (🎮 a small cartouche; its content 🔶).
# No crown above the eagle: the mod art does not show one clearly (not invented).
# Writes <out>/placa_guarda_relevo.png (16-bit, Non-Color: R=G=B height 0..1, plate field 0.30, recesses lower) and
# placa_guarda_previa.png (lit preview) and placa_guarda_contorno.json (smoothed outline in mm, for the model).
#   blender -b --factory-startup --python placa_guarda_relevo.py -- <out dir>
import bpy, sys, os, json, math
import numpy as np

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
os.makedirs(OUT, exist_ok=True)
W_MM, H_MM, PX = 217.0, 153.0, 8.0
NX, NY = int(W_MM * PX), int(H_MM * PX)
xs = (np.arange(NX) + 0.5) / PX - W_MM / 2
ys = (np.arange(NY) + 0.5) / PX
X, Y = np.meshgrid(xs, ys)                       # row 0 = bottom of the plate (Blender image convention)


def catmull(pts, n=8, closed=False):
    P = [np.array(p, float) for p in pts]
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(P[-2])
    return np.array(out)


def mirror(half):
    """half: points from the top centre clockwise down the RIGHT side to the bottom point; returns the closed loop."""
    right = [p for p in half]
    left = [(-x, y) for x, y in reversed(half) if abs(x) > 1e-6]
    return right + left


def sdf(poly, X=X, Y=Y, pad=4.0):
    """Signed distance (mm, + inside) to a closed polygon, computed in its bounding box; -pad elsewhere."""
    poly = np.asarray(poly, float)
    x0, y0 = poly.min(0) - pad; x1, y1 = poly.max(0) + pad
    i0, i1 = max(0, int((x0 + W_MM / 2) * PX)), min(NX, int((x1 + W_MM / 2) * PX) + 1)
    j0, j1 = max(0, int(y0 * PX)), min(NY, int(y1 * PX) + 1)
    out = np.full(X.shape, -pad, np.float32)
    if i1 <= i0 or j1 <= j0:
        return out
    x = X[j0:j1, i0:i1]; y = Y[j0:j1, i0:i1]
    d = np.full(x.shape, 1e9, np.float32); inside = np.zeros(x.shape, bool)
    a = poly; b = np.roll(poly, -1, 0)
    for (ax, ay), (bx, by) in zip(a, b):
        ex, ey = bx - ax, by - ay
        l2 = ex * ex + ey * ey + 1e-12
        t = np.clip(((x - ax) * ex + (y - ay) * ey) / l2, 0, 1)
        d = np.minimum(d, np.hypot(x - ax - t * ex, y - ay - t * ey))
        cond = ((ay > y) != (by > y)) & (x < (bx - ax) * (y - ay) / (ey + 1e-12) + ax)
        inside ^= cond
    out[j0:j1, i0:i1] = np.maximum(np.where(inside, d, -d), -pad)
    return out


def seg_dist(path, X=X, Y=Y):
    path = np.asarray(path, float)
    d = np.full(X.shape, 1e9, np.float32)
    for (ax, ay), (bx, by) in zip(path[:-1], path[1:]):
        ex, ey = bx - ax, by - ay
        l2 = ex * ex + ey * ey + 1e-12
        t = np.clip(((X - ax) * ex + (Y - ay) * ey) / l2, 0, 1)
        d = np.minimum(d, np.hypot(X - ax - t * ex, Y - ay - t * ey))
    return d


def dome(sd, h, r):
    """Rounded relief of height h from a signed distance: rises over r mm from the edge (stamped sheet profile)."""
    t = np.clip(sd / r, 0, 1)
    return h * np.sqrt(1 - (1 - t) ** 2)


def ell(cx, cy, rx, ry, ang=0.0, n=48):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + rx * math.cos(a) * c - ry * math.sin(a) * s, cy + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


# ---------------------------------------------------------------- outline (smoothed trace, mm)
half = [(0.0, 153.0), (54.0, 153.0), (108.5, 153.0), (108.5, 130.0), (108.5, 107.0), (101.0, 98.0), (88.0, 82.0),
        (72.0, 62.0), (55.0, 42.0), (38.0, 22.0), (22.0, 8.0), (9.0, 1.5), (0.0, 0.0)]
side = catmull(half[4:], 6)                     # smooth from the upright corner down to the point
outline = [(0.0, 153.0), (108.5, 153.0)] + [tuple(p) for p in side]
outline = mirror(outline)
SD = sdf(outline, pad=8.0)
plate = SD > 0
H = np.where(plate, 0.30, 0.0).astype(np.float32)

# rim: raised band 1.5..5.5 mm in from the edge, a groove, then beads 9 mm in, every 3.4 mm
rim = np.clip(1 - np.abs(SD - 3.5) / 2.2, 0, 1)
H += 0.22 * np.sqrt(rim) * plate
H -= 0.06 * np.clip(1 - np.abs(SD - 6.4) / 0.7, 0, 1)
# bead positions along the inset outline
ol = np.array(outline + [outline[0]])
seglen = np.hypot(*np.diff(ol, axis=0).T); cum = np.concatenate([[0], np.cumsum(seglen)])
beads = []
for s in np.arange(0, cum[-1], 3.4):
    i = np.searchsorted(cum, s) - 1; i = max(0, min(i, len(ol) - 2))
    f = (s - cum[i]) / max(seglen[i], 1e-9)
    p = ol[i] + (ol[i + 1] - ol[i]) * f
    # inward normal: towards the centroid side
    tng = (ol[i + 1] - ol[i]) / max(seglen[i], 1e-9)
    nrm = np.array([tng[1], -tng[0]])
    beads.append(p + nrm * 9.0)
B = np.full(X.shape, 0.0, np.float32)
for q in beads:
    d = np.hypot(X - q[0], Y - q[1])
    B = np.maximum(B, np.sqrt(np.clip(1 - (d / 1.15) ** 2, 0, 1)))
H += 0.10 * B * (SD > 7.0)


def put(poly, h, r, floor=0.30):
    """Raise a shape: its dome sits on the plate field (max-combined, so overlapping shapes stay separate)."""
    global H
    sd = sdf(poly)
    H = np.maximum(H, np.where(sd > 0, floor + dome(sd, h, r), H))
    return sd


def groove(path, w, depth, mask):
    global H
    d = seg_dist(path)
    H -= depth * np.clip(1 - d / w, 0, 1) ** 1.5 * mask


# ---------------------------------------------------------------- the eagle (centre of the body at (0, 72))
# "aigle a l'antique": head turned to its right (viewer's left), wings spread with the wrists raised and the long
# flight feathers pointing down ("vol abaisse"), talons on a thunderbolt (🎮 silhouette in the mod art; details 🔶).
# Feathers are laid like the stamping die: each new feather is painted OVER the ones before, so every feather shows
# its own raised edge where it overlaps the next.
EX, EY = 0.0, 72.0
ONES = np.ones_like(H)
def E(pts):
    return [(EX + x, EY + y) for x, y in pts]


def over(poly, h, r, floor=0.30):
    """Paint a shape OVER what is there (overlapping feathers)."""
    global H
    sd = sdf(poly)
    H = np.where(sd > 0, floor + dome(sd, h, r), H)
    return sd


def blade(root, tip, w, h, bend=0.0, rachis=True):
    """A flight feather: tapered blade, rounded tip, slight curve (bend, mm sideways at mid length), shaft groove."""
    (rx, ry), (tx, ty) = root, tip
    ang = math.atan2(ty - ry, tx - rx); L = math.hypot(tx - rx, ty - ry)
    nx, ny = -math.sin(ang), math.cos(ang); cx_, cy_ = math.cos(ang), math.sin(ang)
    def P(t, s):                                        # t along, s across (mm)
        b = bend * math.sin(math.pi * t)
        return (rx + cx_ * L * t + nx * (s + b), ry + cy_ * L * t + ny * (s + b))
    prof = [(0.0, 0.55), (0.25, 0.85), (0.6, 1.0), (0.85, 0.85), (0.95, 0.55), (1.0, 0.0)]
    pts = [P(t, w * f) for t, f in prof] + [P(t, -w * f) for t, f in reversed(prof[:-1])]
    sd = over(E(catmull(pts, 4, closed=True)), h, w * 0.9)
    if rachis:
        groove(E([P(0.08, 0), P(0.5, 0), P(0.9, 0)]), 0.32, 0.06, (sd > 0.4))
    return sd


def scale(cx, cy, rx, ry, h):
    """A covert feather: a scale whose lower rounded edge shows."""
    return over(E(ell(cx, cy, rx, ry, 0.0, 24)), h, min(rx, ry) * 0.9)


for sgn in (1, -1):
    m = lambda x: sgn * x
    # flight feathers first (they lie under the coverts): inner (near the body) first, outer ones over them
    roots = [(13, -2), (16, 3), (19, 8), (22, 14), (25, 20), (28, 26), (31, 32), (34, 37)]
    tips = [(22, -15), (30, -19), (38, -17), (45, -12), (50, -4), (53, 6), (55, 17), (54, 29)]
    for k in range(8):
        (rx, ry), (tx, ty) = roots[k], tips[k]
        blade((m(rx), ry), (m(tx), ty), 3.2 + 0.15 * k, 0.46 + 0.02 * k, bend=sgn * -0.8)
    # leading edge of the wing (the "arm"): a rolled border from the shoulder to the wrist
    lead = catmull([(7, 13), (12, 24), (19, 34), (28, 43), (37, 48), (42, 47), (40, 43), (32, 38), (23, 30), (15, 20), (10, 10)], 5, closed=True)
    over(E([(m(x), y) for x, y in lead]), 0.70, 2.2)
    groove(E([(m(x), y) for x, y in catmull([(10, 16), (16, 27), (25, 37), (35, 45)], 4)]), 0.45, 0.05, ONES)
    # coverts: a lattice of scale feathers filling the upper wing between the leading edge and the roots of the flight
    # feathers; the rows far from the edge are laid first, each row nearer the edge overlaps them (as feathers lie)
    region = [(9, 1), (8, 9), (10, 17), (15, 26), (22, 34), (30, 41), (37, 44), (39, 39), (34, 35), (31, 30), (28, 24),
              (25, 18), (22, 12), (19, 6), (16, 1), (13, -3)]
    def inside(px_, py_, poly=region):
        c = False
        for (ax_, ay_), (bx_, by_) in zip(poly, poly[1:] + poly[:1]):
            if (ay_ > py_) != (by_ > py_) and px_ < (bx_ - ax_) * (py_ - ay_) / (by_ - ay_) + ax_:
                c = not c
        return c
    ux, uy = 30 / math.hypot(30, 32), 32 / math.hypot(30, 32)           # along the leading edge
    vx, vy = uy, -ux                                                     # away from it, toward the trailing edge
    cells = []
    for i in range(-2, 14):
        for j in range(0, 7):
            ox, oy = 8 + ux * (i * 4.2 + (j % 2) * 2.1) + vx * j * 3.6, 12 + uy * (i * 4.2 + (j % 2) * 2.1) + vy * j * 3.6
            if inside(ox, oy):
                cells.append((j, ox, oy))
    for j, ox, oy in sorted(cells, key=lambda c: -c[0]):
        sz = 2.5 + 0.12 * j
        scale(m(ox), oy, sz, sz * 1.15, 0.56 + 0.025 * (6 - j))

# tail: five feathers fanning down between the legs (the middle one on top)
for k in (0, 4, 1, 3, 2):
    a = np.linspace(-0.42, 0.42, 5)[k]
    blade((math.sin(a) * 2, -11), (math.sin(a) * 15, -11 - math.cos(a) * 23), 2.9, 0.60 + 0.04 * (2 - abs(k - 2)))

# thunderbolt: a twisted spindle under the talons, with zig-zag bolts and arrow heads
spindle = catmull([(-24, -29), (-12, -27.4), (0, -27), (12, -27.4), (24, -29), (12, -30.6), (0, -31), (-12, -30.6)], 5, closed=True)
sds = over(E(spindle), 0.66, 1.6)
for xx in np.arange(-20, 21, 2.6):
    groove(E([(xx - 1.0, -30.4), (xx + 1.0, -27.6)]), 0.35, 0.08, (sds > 0.3))
for sgn in (1, -1):
    for dy in (1, -1):
        zz = [(sgn * 8, -29 + dy * 1.5), (sgn * 15, -29 + dy * 7.5), (sgn * 12.5, -29 + dy * 9), (sgn * 21, -29 + dy * 15)]
        d = seg_dist(E(zz))
        H = np.maximum(H, np.where(d < 1.2, 0.30 + 0.48 * np.sqrt(np.clip(1 - d / 1.2, 0, 1)), H))
        tx, ty = sgn * 21, -29 + dy * 15
        put(E([(tx + sgn * 2.8, ty + dy * 2.8), (tx - sgn * 1.4, ty + dy * 0.9), (tx + sgn * 0.9, ty - dy * 1.4)]), 0.50, 0.8)

# body: a broad breast of scale feathers (lowest first), feathered thighs, talons on the bolt
body = catmull([(0, 18), (7.5, 15), (10.5, 5), (10, -5), (6.5, -12), (0, -15), (-6.5, -12), (-10, -5), (-10.5, 5), (-7.5, 15)], 6, closed=True)
over(E(body), 0.84, 5.0)
for j, yy in enumerate(np.arange(-10, 15, 3.3)):
    for xx in np.arange(-7.5 + (j % 2) * 1.65, 8, 3.3):
        if (xx / 10.5) ** 2 + ((yy - 2) / 16.5) ** 2 < 0.85:
            scale(xx, yy, 2.0, 2.3, 0.86 + 0.01 * j)
for sgn in (1, -1):
    thigh = catmull([(sgn * 3, -7), (sgn * 10, -9), (sgn * 10, -17), (sgn * 7, -22), (sgn * 3.5, -15)], 5, closed=True)
    over(E(thigh), 0.86, 2.4)
    for yy in (-10, -13.5, -17):
        groove(E([(sgn * 4.5, yy), (sgn * 7, yy - 1.6), (sgn * 9.5, yy)]), 0.35, 0.06, ONES)
    d = seg_dist(E([(sgn * 6.5, -20), (sgn * 7, -26)]))
    H = np.maximum(H, np.where(d < 1.6, 0.30 + 0.70 * np.sqrt(np.clip(1 - d / 1.6, 0, 1)), H))
    for tx in (-3.2, 0.0, 3.2):
        d = seg_dist(E([(sgn * 7, -26), (sgn * 7 + tx, -28.5), (sgn * 7 + tx * 1.15, -31.4)]))
        H = np.maximum(H, np.where(d < 0.95, 0.30 + 0.78 * np.sqrt(np.clip(1 - d / 0.95, 0, 1)), H))

# head on a strong neck, turned to the eagle's right: big hooked beak, eye under a brow ridge, neck hackles
neck = catmull([(-4, 13), (6, 16), (5, 24), (-1, 30), (-10, 30), (-11, 22)], 5, closed=True)
over(E(neck), 0.98, 3.6)
for k in range(5):
    groove(E(catmull([(-8 + k * 3, 26 - k * 0.8), (-6.5 + k * 3, 21.5 - k * 0.6), (-6 + k * 3, 16.5)], 4)), 0.45, 0.06, ONES)
over(E(ell(-8.0, 29.0, 8.2, 6.6, 0.12, 40)), 1.06, 3.4)
beak = catmull([(-14.0, 32.4), (-19.0, 32.0), (-24.4, 29.0), (-25.6, 24.6), (-23.6, 22.6), (-22.6, 25.4), (-18.0, 25.8), (-14.0, 25.4)], 5, closed=True)
over(E(beak), 0.98, 1.4)
groove(E([(-14.2, 28.2), (-21.6, 27.4)]), 0.32, 0.12, ONES)          # the mouth line
d = np.hypot(X - (EX - 10.0), Y - (EY + 30.4))
H -= 0.18 * np.clip(1 - d / 1.4, 0, 1)                                 # the eye
H += 0.07 * np.clip(1 - np.abs(d - 2.1) / 0.5, 0, 1)
groove(E(catmull([(-13.0, 32.6), (-10.0, 33.2), (-7.0, 32.6)], 4)), 0.5, 0.07, ONES)   # the brow

# ---------------------------------------------------------------- the two flaming grenades
for sgn in (1, -1):
    gx, gy = sgn * 80.0, 108.0
    d = np.hypot(X - gx, Y - gy)
    ball = np.sqrt(np.clip(1 - (d / 10.5) ** 2, 0, 1))
    H = np.maximum(H, np.where(d < 10.5, 0.30 + 0.85 * ball, H))
    H -= 0.06 * np.clip(1 - np.abs(Y - (gy + 6.5)) / 0.5, 0, 1) * (d < 9.5)          # the fuse collar
    collar = [(gx - 3.4, gy + 9.4), (gx + 3.4, gy + 9.4), (gx + 3.0, gy + 12.6), (gx - 3.0, gy + 12.6)]
    put(collar, 0.75, 1.0)
    for k, (dx, ht, lean) in enumerate(((-6.5, 13, -0.55), (-3.4, 18, -0.25), (0.0, 21, 0.0), (3.4, 18, 0.25), (6.5, 13, 0.55))):
        bx, by = gx + dx * 0.55, gy + 12.0
        tx, ty = gx + dx + lean * 6, by + ht
        wv = 1.6 * (1 if k % 2 else -1)                 # each tongue licks sideways (S-curve)
        fl = catmull([(bx - 2.2, by), (bx + (tx - bx) * 0.35 - 2.3 + wv, by + ht * 0.35), (bx + (tx - bx) * 0.7 - 1.2 - wv, by + ht * 0.7),
                      (tx, ty), (bx + (tx - bx) * 0.7 + 0.6 - wv, by + ht * 0.62), (bx + (tx - bx) * 0.35 + 1.8 + wv, by + ht * 0.30),
                      (bx + 2.2, by)], 5, closed=True)
        put(fl, 0.50 + 0.05 * (2 - abs(k - 2)), 1.4)

# ---------------------------------------------------------------- the boss at the point
put(ell(0.0, 19.0, 9.5, 7.0, 0.0, 40), 0.40, 2.2)
d = np.hypot((X - 0.0) / 9.5, (Y - 19.0) / 7.0)
H -= 0.05 * np.clip(1 - np.abs(d - 0.78) / 0.07, 0, 1)

H = np.where(plate, H, 0.0)
H = np.clip(H, 0, 1).astype(np.float32)


def save(arr, name, rgb=None):
    im = bpy.data.images.new(name, NX, NY, alpha=False, float_buffer=True)
    im.colorspace_settings.name = "Non-Color"          # BEFORE the pixels: changing it regenerates a new image
    px = np.ones((NY, NX, 4), np.float32)
    px[..., :3] = arr[..., None] if rgb is None else rgb   # the preview is passed already gamma-encoded
    im.pixels.foreach_set(px.ravel()); im.update()
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16" if rgb is None else "8"
    im.save_render(os.path.join(OUT, name), scene=sc)
    print("saved", os.path.join(OUT, name))


save(H, "placa_guarda_relevo.png")
# lit preview: light from the upper left, brass colour, darker in the recesses
gy_, gx_ = np.gradient(H * 8.0)
nrm = np.dstack([-gx_, -gy_, np.ones_like(H) * 0.35]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ldir = np.array([-0.5, 0.6, 0.62]); ldir /= np.linalg.norm(ldir)
lit = np.clip((nrm * ldir).sum(2), 0, 1)
brass = np.array([0.78, 0.56, 0.20])
prev = brass[None, None, :] * (0.25 + 0.95 * lit[..., None]) * (0.55 + 0.45 * np.clip((H - 0.2) / 0.6, 0, 1))[..., None]
prev = np.where(plate[..., None], prev, np.array([0.05, 0.05, 0.05]))
save(np.zeros_like(H), "placa_guarda_previa.png", rgb=np.clip(prev, 0, 1) ** (1 / 2.2))
json.dump({"mm": [list(map(float, p)) for p in outline], "largura_mm": W_MM, "altura_mm": H_MM, "px_por_mm": PX,
           "nota": "contorno suavizado do traco placa_bonnet_guarda.json; UV da placa = (x/217 + 0.5, y/153)"},
          open(os.path.join(OUT, "placa_guarda_contorno.json"), "w"), indent=1)
print("PLACA RELEVO", NX, NY, "px; altura min/max", float(H[plate].min()), float(H.max()))
