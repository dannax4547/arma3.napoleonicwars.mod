# Numbered line regiments (user 2026-10-13: "adiciona mais regimentos para a franca"): the 1812 shako plate (crowned
# eagle over a semicircular base, art FranceINF c3 r4 traced in placa_aguia_semicirculo.json) carried the regiment's
# number cut out of the plain field of its base (🔶: general knowledge, no source read). Only the _co map changes: the
# plate texels are found by rasterising the plate faces (surface kind "arte") in the game UV, each with its point in the
# mod art (UV layer "arte"); the digits are drawn in ATLAS PIXELS centred on the plain field of the base (atlas
# ~(1984, 2137), read on the art) and shown as cut through to the black felt. The model is the fusilier's.
#   blender -b --factory-startup <texturas .blend> --python numerar_placa_fr.py -- <tex dir> <tag> <dst prefix> <n> [<n>...]
#   e.g. ... -- source/textures/hcl_shako_fr fuzileiro_1a_comp hcl_shako_fr_linha 18 46 57 84
import bpy, sys, os, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
TEX, TAG, DST = os.path.abspath(a[0]), a[1], a[2]
NUMS = [int(x) for x in a[3:]]
ATLAS_PX = 4096
CENTRE = (1984.0, 2137.0)          # plain field of the plate's base, atlas pixels (x right, y down)
DIG_H, DIG_W, GAP = 15.0, 8.0, 2.2  # atlas pixels
FONT = {  # 5 x 7, top row first
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
}


def mask_digits(ax, ay, text):
    """1 inside the cut-out numerals, for atlas pixel coordinates (ax, ay) (arrays)."""
    n = len(text)
    total = n * DIG_W + (n - 1) * GAP
    x0 = CENTRE[0] - total / 2
    y0 = CENTRE[1] - DIG_H / 2
    m = np.zeros(ax.shape, np.float32)
    for k, ch in enumerate(text):
        gx = (ax - (x0 + k * (DIG_W + GAP))) / DIG_W * 5
        gy = (ay - y0) / DIG_H * 7
        ok = (gx >= 0) & (gx < 5) & (gy >= 0) & (gy < 7)
        cx = np.clip(gx.astype(int), 0, 4); cy = np.clip(gy.astype(int), 0, 6)
        bits = np.array([[int(c) for c in row] for row in FONT[ch]], np.float32)
        m = np.maximum(m, np.where(ok, bits[cy, cx], 0.0))
    return m


ob = bpy.data.objects[f"HCL_Shako_Fr_{TAG}_LOD0"]
me = ob.data
kinds = ob["hcl_kinds"].split(",")
arte_k = {i for i, k in enumerate(kinds) if k.startswith("arte:")}
src = os.path.join(TEX, f"hcl_shako_fr_{TAG}_co.png")
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
print(f"PLACA {TAG}: {int(plate.sum())} texels da placa; campo da base em ({CENTRE[0]:.0f}, {CENTRE[1]:.0f}) px do atlas")
for n in NUMS:
    txt = str(n)
    m = mask_digits(AX, AY, txt) * plate
    # soften the cut edge a little (one texel) so the numerals are not jagged at game distance
    soft = m.copy()
    soft[1:-1, 1:-1] = np.maximum(m[1:-1, 1:-1], 0.5 * (m[:-2, 1:-1] + m[2:, 1:-1] + m[1:-1, :-2] + m[1:-1, 2:]) / 2)
    out = px.copy()
    felt = np.array((0.018, 0.018, 0.020), np.float32)          # sRGB-ish dark felt seen through the cut
    out[..., :3] = out[..., :3] * (1 - soft[..., None]) + felt[None, None, :] * soft[..., None]
    # bright bevel along the lower-right edge of each cut (the brass edge catching the light)
    bev = np.zeros_like(m)
    bev[:-1, :-1] = np.clip(m[1:, 1:] - m[:-1, :-1], 0, 1) * plate[:-1, :-1]
    out[..., :3] = np.clip(out[..., :3] + 0.18 * bev[..., None], 0, 1)
    dst = os.path.join(TEX, f"{DST}_{n:03d}_co.png")
    o = bpy.data.images.new(os.path.basename(dst), W, H, alpha=False)
    o.colorspace_settings.name = "sRGB"
    out[..., 3] = 1.0
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = dst; o.file_format = "PNG"; o.save()
    print(f"  -> {os.path.basename(dst)}: {int(m.sum())} texels vazados ({txt})")
