# Relief of the yellow-metal front plate of the Duchy of Warsaw grenadiers' bearskin (regulation of 3 September 1810:
# "na zoltej blasze z numerem pulku widnial bialy orzel, a po bokach dwa granaty" - yellow plate with the regiment
# number, a WHITE eagle and two grenades at the sides; Gembarzewski 1905 / Zygulski & Wielecki 1988 via pl.wikipedia, 📜).
# Copy of placa_suica_relevo.py: outline, rim and beads of the Old Guard plate (🔶 shape); two flaming grenades at the
# sides (the Guard plate's, 🔶 drawing); the regiment number at the bottom (here 4, the number of the mod art,
# polandINF c0 r5 🎮); the field in the middle is left flat for the white-metal eagle, a separate part laid on the
# plate (blockout_bonnet_varsovia.py, outline of the czapka eagle).
# Writes <out>/placa_varsovia_relevo.png, placa_varsovia_previa.png, placa_varsovia_contorno.json.
#   blender -b --factory-startup --python placa_varsovia_relevo.py -- <out dir>
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


def dome(sd, h, r):
    t = np.clip(sd / r, 0, 1)
    return h * np.sqrt(1 - (1 - t) ** 2)


# ---------------------------------------------------------------- outline: the Old Guard plate's (🔶)
half = [(0.0, 153.0), (54.0, 153.0), (108.5, 153.0), (108.5, 130.0), (108.5, 107.0), (101.0, 98.0), (88.0, 82.0),
        (72.0, 62.0), (55.0, 42.0), (38.0, 22.0), (22.0, 8.0), (9.0, 1.5), (0.0, 0.0)]
side = catmull(half[4:], 6)
outline = [(0.0, 153.0), (108.5, 153.0)] + [tuple(p) for p in side]
outline = mirror(outline)
SD = sdf(outline, pad=8.0)
plate = SD > 0
H = np.where(plate, 0.30, 0.0).astype(np.float32)

# rim and bead row (as the Old Guard plate)
rim = np.clip(1 - np.abs(SD - 3.5) / 2.2, 0, 1)
H += 0.22 * np.sqrt(rim) * plate
H -= 0.06 * np.clip(1 - np.abs(SD - 6.4) / 0.7, 0, 1)
ol = np.array(outline + [outline[0]])
seglen = np.hypot(*np.diff(ol, axis=0).T); cum = np.concatenate([[0], np.cumsum(seglen)])
B = np.zeros(X.shape, np.float32)
for s in np.arange(0, cum[-1], 3.4):
    i = max(0, min(np.searchsorted(cum, s) - 1, len(ol) - 2))
    f = (s - cum[i]) / max(seglen[i], 1e-9)
    p = ol[i] + (ol[i + 1] - ol[i]) * f
    tng = (ol[i + 1] - ol[i]) / max(seglen[i], 1e-9)
    q = p + np.array([tng[1], -tng[0]]) * 9.0
    d = np.hypot(X - q[0], Y - q[1])
    B = np.maximum(B, np.sqrt(np.clip(1 - (d / 1.15) ** 2, 0, 1)))
H += 0.10 * B * (SD > 7.0)


def put(poly, h, r, floor=0.30):
    global H
    sd = sdf(poly)
    H = np.maximum(H, np.where(sd > 0, floor + dome(sd, h, r), H))
    return sd


# ---------------------------------------------------------------- two flaming grenades (as the Guard plate)
def grenade(gx, gy, K=1.0):
    global H
    R = 10.5 * K
    d = np.hypot(X - gx, Y - gy)
    ball = np.sqrt(np.clip(1 - (d / R) ** 2, 0, 1))
    H = np.maximum(H, np.where(d < R, 0.30 + 0.85 * ball, H))
    H -= 0.06 * np.clip(1 - np.abs(Y - (gy + 6.5 * K)) / 0.5, 0, 1) * (d < R - 1.0)
    put([(gx - 3.4 * K, gy + 9.4 * K), (gx + 3.4 * K, gy + 9.4 * K), (gx + 3.0 * K, gy + 12.6 * K), (gx - 3.0 * K, gy + 12.6 * K)], 0.75, 1.0)
    for k, (dx, ht, lean) in enumerate(((-6.5, 13, -0.55), (-3.4, 18, -0.25), (0.0, 21, 0.0), (3.4, 18, 0.25), (6.5, 13, 0.55))):
        bx, by = gx + dx * 0.55 * K, gy + 12.0 * K
        tx, ty = gx + (dx + lean * 6) * K, by + ht * K
        wv = 1.6 * K * (1 if k % 2 else -1)
        fl = catmull([(bx - 2.2 * K, by), (bx + (tx - bx) * 0.35 - 2.3 * K + wv, by + ht * K * 0.35),
                      (bx + (tx - bx) * 0.7 - 1.2 * K - wv, by + ht * K * 0.7), (tx, ty),
                      (bx + (tx - bx) * 0.7 + 0.6 * K - wv, by + ht * K * 0.62), (bx + (tx - bx) * 0.35 + 1.8 * K + wv, by + ht * K * 0.30),
                      (bx + 2.2 * K, by)], 5, closed=True)
        put(fl, 0.50 + 0.05 * (2 - abs(k - 2)), 1.4)


for sgn in (1, -1):
    grenade(sgn * 78.0, 100.0)


# ---------------------------------------------------------------- the regiment number (4) at the bottom
def stroke(path, w, h):
    global H
    path = np.asarray(path, float)
    d = np.full(X.shape, 1e9, np.float32)
    for (ax, ay), (bx, by) in zip(path[:-1], path[1:]):
        ex, ey = bx - ax, by - ay
        l2 = ex * ex + ey * ey + 1e-12
        t = np.clip(((X - ax) * ex + (Y - ay) * ey) / l2, 0, 1)
        d = np.minimum(d, np.hypot(X - ax - t * ex, Y - ay - t * ey))
    H = np.maximum(H, np.where(d < w, 0.30 + h * np.sqrt(np.clip(1 - d / w, 0, 1)), H))


NX0, NY0, NH = 0.0, 20.0, 24.0                    # digit 24 mm high above the point of the plate
stroke([(NX0 + 4.0, NY0), (NX0 + 4.0, NY0 + NH)], 1.8, 0.55)                       # upright
stroke([(NX0 + 4.0, NY0 + NH), (NX0 - 8.0, NY0 + 7.0), (NX0 + 8.0, NY0 + 7.0)], 1.6, 0.55)   # diagonal and bar
stroke([(NX0 + 0.5, NY0), (NX0 + 7.5, NY0)], 1.2, 0.45)                             # foot serif
print("NUMERO 4 na base da placa; granadas em x +-78 mm, y 100 mm")

H = np.clip(np.where(plate, H, 0.0), 0, 1).astype(np.float32)


def save(arr, name, rgb=None):
    im = bpy.data.images.new(name, NX, NY, alpha=False, float_buffer=True)
    im.colorspace_settings.name = "Non-Color"
    px = np.ones((NY, NX, 4), np.float32)
    px[..., :3] = arr[..., None] if rgb is None else rgb
    im.pixels.foreach_set(px.ravel()); im.update()
    sc = bpy.context.scene
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16" if rgb is None else "8"
    im.save_render(os.path.join(OUT, name), scene=sc)
    print("saved", os.path.join(OUT, name))


save(H, "placa_varsovia_relevo.png")
gy_, gx_ = np.gradient(H * 8.0)
nrm = np.dstack([-gx_, -gy_, np.ones_like(H) * 0.35]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ldir = np.array([-0.5, 0.6, 0.62]); ldir /= np.linalg.norm(ldir)
lit = np.clip((nrm * ldir).sum(2), 0, 1)
brass = np.array([0.78, 0.56, 0.20])
prev = brass[None, None, :] * (0.25 + 0.95 * lit[..., None]) * (0.55 + 0.45 * np.clip((H - 0.2) / 0.6, 0, 1))[..., None]
prev = np.where(plate[..., None], prev, np.array([0.05, 0.05, 0.05]))
save(np.zeros_like(H), "placa_varsovia_previa.png", rgb=np.clip(prev, 0, 1) ** (1 / 2.2))
json.dump({"mm": [list(map(float, p)) for p in outline], "largura_mm": W_MM, "altura_mm": H_MM, "px_por_mm": PX,
           "nota": "contorno da placa da Velha Guarda (forma polonesa 🔶); UV da placa = (x/217 + 0.5, y/153)"},
          open(os.path.join(OUT, "placa_varsovia_contorno.json"), "w"), indent=1)
print("PLACA RELEVO", NX, NY, "px; altura min/max", float(H[plate].min()), float(H.max()))
