# Numbered plates of the Duchy of Warsaw czapka (user 2026-10-18: "so adiciona mais regimentos para a polonia").
# The 1810 regulation puts the REGIMENT NUMBER on the yellow plate under the white eagle (📜 Gembarzewski 1905 /
# Zygulski & Wielecki 1988: "pod nim zolta blacha z numerem pulku"); the mod art (polandINF c0 r5) shows the plate of the
# 4th Regiment. Copy of the method of numerar_placa_fr.py, only the _co map changes:
#   - the plate texels are found by rasterising the faces of kind "arte" in the game UV, each with its point in the mod
#     art (UV layer "arte");
#   - the engraved "4" of the art (atlas pixels x 183..197, y 2899..2930, read on a 6x zoom) is covered by diffusing the
#     brass of the plate around it into the box (keeps the shading of the raised plate, no flat patch);
#   - the new number is engraved as a thin line like the art's "4" (dark groove with a lit lower edge), centred on the
#     raised middle of the plate (atlas ~(190, 2914)), 24 px high (two digits narrower, they must fit the 20 px wide
#     raised part). Digits are placed in ATLAS space, so they read the same way round as the art's "4" in the game.
#   blender -b <texturas .blend> --python numerar_placa_varsovia.py -- <tex dir> <tag> <dst prefix> <n> [<n>...]
#   e.g. ... -- source/textures/hcl_czapka_varsovia fuzileiro hcl_czapka_varsovia_fuzileiro_rgt 1 2 3 5 6 ...
import bpy, sys, os, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
TEX, TAG, DST = os.path.abspath(a[0]), a[1], a[2]
NUMS = [int(x) for x in a[3:]]
ATLAS_PX = 4096
ERASE = (180.0, 2896.0, 201.0, 2933.0)        # box of the art's "4" (atlas px, x0 y0 x1 y1)
PLAIN = (205.0, 2918.0, 245.0, 2934.0)        # plain bar of the same plate
CENTRE = (190.5, 2914.0)
HALF_W = 1.1                                  # half width of the engraved stroke (atlas px; the art's "4" ~2 px)


def _ell(cx, cy, rx, ry, a0=0.0, a1=360.0, n=24):
    """Points of an elliptic arc; angle 0 = top, clockwise (x right, y down)."""
    return [(cx + rx * math.sin(math.radians(a0 + (a1 - a0) * k / n)),
             cy - ry * math.cos(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


# stroke font: polylines in a unit box (x right, y DOWN)
FONT = {
    "0": [_ell(0.5, 0.5, 0.5, 0.5)],
    "1": [[(0.2, 0.22), (0.55, 0.0), (0.55, 1.0)], [(0.2, 1.0), (0.9, 1.0)]],
    "2": [_ell(0.5, 0.27, 0.48, 0.27, -90, 110, 12) + [(0.0, 1.0), (1.0, 1.0)]],
    "3": [_ell(0.48, 0.25, 0.45, 0.25, -70, 180, 14), _ell(0.48, 0.73, 0.52, 0.27, 0, 250, 14)],
    "4": [[(0.72, 1.0), (0.72, 0.0), (0.0, 0.7), (1.0, 0.7)]],
    "5": [[(0.95, 0.0), (0.12, 0.0), (0.05, 0.45)] + _ell(0.45, 0.68, 0.5, 0.3, -60, 230, 14)],
    "6": [[(0.85, 0.03), (0.5, 0.0), (0.2, 0.15), (0.03, 0.45)] + _ell(0.5, 0.7, 0.5, 0.3, -90, 270, 18)],
    "7": [[(0.0, 0.0), (1.0, 0.0), (0.35, 1.0)]],
    "8": [_ell(0.5, 0.25, 0.4, 0.25), _ell(0.5, 0.73, 0.48, 0.27)],
}
FONT["9"] = [[(1 - x, 1 - y) for x, y in pl] for pl in FONT["6"]]


def _seg_dist(ax, ay, p, q):
    (px_, py_), (qx, qy) = p, q
    dx, dy = qx - px_, qy - py_
    t = np.clip(((ax - px_) * dx + (ay - py_) * dy) / max(dx * dx + dy * dy, 1e-9), 0, 1)
    return np.hypot(ax - (px_ + t * dx), ay - (py_ + t * dy))


def mask_digits(ax, ay, text, dy=0.0):
    """Antialiased coverage (0..1) of the engraved number at atlas coords (ax, ay)."""
    n = len(text)
    dig_h = 24.0
    dig_w, gap = (12.0, 0.0) if n == 1 else (7.5, 3.0)
    total = n * dig_w + (n - 1) * gap
    x0 = CENTRE[0] - total / 2
    y0 = CENTRE[1] - dig_h / 2 + dy
    d = np.full(ax.shape, 1e9, np.float32)
    for k, ch in enumerate(text):
        ox = x0 + k * (dig_w + gap)
        for pl in FONT[ch]:
            pts = [(ox + u * dig_w, y0 + v * dig_h) for u, v in pl]
            for p, q in zip(pts, pts[1:]):
                d = np.minimum(d, _seg_dist(ax, ay, p, q))
    return np.clip((HALF_W - d) / 0.7 + 0.5, 0, 1)


ob = bpy.data.objects[f"HCL_Czapka_Varsovia_{TAG}_LOD0"]
me = ob.data
kinds = ob["hcl_kinds"].split(",")
arte_k = {i for i, k in enumerate(kinds) if k == "arte:latao"}       # the brass plate (the eagle is arte:prata)
src = os.path.join(TEX, f"hcl_czapka_varsovia_{TAG}_co.png")
im = bpy.data.images.load(src)
W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)
ka = me.attributes["hcl_kind_i"].data
uv = me.uv_layers["UVMap"].data
art = me.uv_layers["arte"].data
AX = np.full((H, W), -1.0, np.float32); AY = np.full((H, W), -1.0, np.float32)
for p in me.polygons:
    if ka[p.index].value not in arte_k:
        continue
    li = list(p.loop_indices)
    P2 = [(uv[i].uv.x * W - 0.5, uv[i].uv.y * H - 0.5) for i in li]
    A2 = [(art[i].uv.x * ATLAS_PX, (1 - art[i].uv.y) * ATLAS_PX) for i in li]
    for t in range(1, len(li) - 1):
        (x0, y0), (x1, y1), (x2, y2) = P2[0], P2[t], P2[t + 1]
        xa, xb = max(0, int(math.floor(min(x0, x1, x2)))), min(W - 1, int(math.ceil(max(x0, x1, x2))))
        ya, yb = max(0, int(math.floor(min(y0, y1, y2)))), min(H - 1, int(math.ceil(max(y0, y1, y2))))
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(det) < 1e-12 or xb < xa or yb < ya:
            continue
        gy, gx = np.mgrid[ya:yb + 1, xa:xb + 1].astype(np.float32)
        l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / det
        l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / det
        l2 = 1 - l0 - l1
        ins = (l0 >= -0.01) & (l1 >= -0.01) & (l2 >= -0.01)
        ax = l0 * A2[0][0] + l1 * A2[t][0] + l2 * A2[t + 1][0]
        ay = l0 * A2[0][1] + l1 * A2[t][1] + l2 * A2[t + 1][1]
        sub_x = AX[ya:yb + 1, xa:xb + 1]; sub_y = AY[ya:yb + 1, xa:xb + 1]
        sub_x[ins] = ax[ins]; sub_y[ins] = ay[ins]
plate = AX >= 0
# only the FRONT face of the plate carries the engraving: its art coords fall inside the plate outline; the side walls
# map to the outline itself, so the erase box (well inside) touches only the front
er = plate & (AX >= ERASE[0]) & (AX <= ERASE[2]) & (AY >= ERASE[1]) & (AY <= ERASE[3])
pl = plate & (AX >= PLAIN[0]) & (AX <= PLAIN[2]) & (AY >= PLAIN[1]) & (AY <= PLAIN[3])
clean = np.median(px[pl][:, :3], axis=0) if pl.any() else np.array((0.6, 0.45, 0.2), np.float32)
print(f"PLACA {TAG}: {int(plate.sum())} texels da placa, {int(er.sum())} no numero do mod, latao liso {np.round(clean, 3)}")
base = px.copy()
# cover the art's number: Laplace diffusion of the plate texels around the box into it (plate texels only, so the black
# of the UV gaps never bleeds in)
ys, xs = np.nonzero(er)
if len(ys):
    y0_, y1_ = max(ys.min() - 4, 0), min(ys.max() + 5, H)
    x0_, x1_ = max(xs.min() - 4, 0), min(xs.max() + 5, W)
    win = base[y0_:y1_, x0_:x1_, :3].copy()
    e = er[y0_:y1_, x0_:x1_]
    ok = plate[y0_:y1_, x0_:x1_].astype(np.float32)
    ring = plate[y0_:y1_, x0_:x1_] & ~e
    win[e] = np.median(win[ring], axis=0) if ring.any() else clean
    for _ in range(1500):
        acc = np.zeros_like(win); cnt = np.zeros(win.shape[:2], np.float32)
        for sy, sx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            acc += np.roll(win * ok[..., None], (sy, sx), (0, 1))
            cnt += np.roll(ok, (sy, sx), (0, 1))
        win[e] = acc[e] / np.maximum(cnt[e], 1)[:, None]
    base[y0_:y1_, x0_:x1_, :3] = win
near = plate & (np.abs(AX - CENTRE[0]) < 16) & (np.abs(AY - CENTRE[1]) < 18)   # only these texels can be engraved
for n in NUMS:
    txt = str(n)
    m = np.zeros((H, W), np.float32); lo = np.zeros((H, W), np.float32)
    m[near] = mask_digits(AX[near], AY[near], txt)
    lo[near] = mask_digits(AX[near], AY[near], txt, dy=-1.3)                   # stroke shifted up: lit lower edge
    out = base.copy()
    out[..., :3] = out[..., :3] * (1 - 0.45 * m[..., None])                    # engraved groove: darker brass
    out[..., :3] = np.clip(out[..., :3] + 0.12 * np.clip(lo - m, 0, 1)[..., None], 0, 1)
    dst = os.path.join(TEX, f"{DST}{n:02d}_co.png")
    o = bpy.data.images.new(os.path.basename(dst), W, H, alpha=False)
    o.colorspace_settings.name = "sRGB"
    out[..., 3] = 1.0
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = dst; o.file_format = "PNG"; o.save()
    print(f"  -> {os.path.basename(dst)}: {int((m > 0.5).sum())} texels gravados ({txt})")
