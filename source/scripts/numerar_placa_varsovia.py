# Numbered plates of the Duchy of Warsaw czapka (user 2026-10-18: "so adiciona mais regimentos para a polonia").
# The 1810 regulation puts the REGIMENT NUMBER on the yellow plate under the white eagle (📜 Gembarzewski 1905 /
# Zygulski & Wielecki 1988: "pod nim zolta blacha z numerem pulku"); the mod art (polandINF c0 r5) shows the plate of the
# 4th Regiment. Copy of the method of numerar_placa_fr.py, only the _co map changes:
#   - the plate texels are found by rasterising the faces of kind "arte" in the game UV, each with its point in the mod
#     art (UV layer "arte");
#   - the engraved "4" of the art (atlas pixels x 183..197, y 2899..2930, read on a 6x zoom) is covered with the plain
#     brass of the same plate (mean of its plain bar, x 205..245, y 2918..2934);
#   - the new number is engraved in the same style (dark stroke with a bright lower edge), centred on the raised middle
#     of the plate (atlas ~(190, 2914)), 26 px high (two digits narrower, they must fit the 20 px wide raised part).
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
FONT = {  # 5 x 7, top row first (as numerar_placa_fr.py)
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
    n = len(text)
    dig_h = 26.0
    dig_w, gap = (11.0, 0.0) if n == 1 else (8.5, 2.0)
    total = n * dig_w + (n - 1) * gap
    x0 = CENTRE[0] - total / 2
    y0 = CENTRE[1] - dig_h / 2
    m = np.zeros(ax.shape, np.float32)
    for k, ch in enumerate(text):
        gx = (ax - (x0 + k * (dig_w + gap))) / dig_w * 5
        gy = (ay - y0) / dig_h * 7
        ok = (gx >= 0) & (gx < 5) & (gy >= 0) & (gy < 7)
        cx = np.clip(gx.astype(int), 0, 4); cy = np.clip(gy.astype(int), 0, 6)
        bits = np.array([[int(c) for c in row] for row in FONT[ch]], np.float32)
        m = np.maximum(m, np.where(ok, bits[cy, cx], 0.0))
    return m


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
# keep a little of the original light/dark variation so the cover is not a flat patch
lum = base[..., :3].mean(axis=2, keepdims=True)
lum_ref = float(np.median(base[pl][:, :3].mean(axis=1))) if pl.any() else 0.5
var = np.clip(1.0 + 0.35 * (lum - lum_ref) / max(lum_ref, 1e-3), 0.8, 1.2)
base[..., :3] = np.where(er[..., None], clean[None, None, :] * var, base[..., :3])
for n in NUMS:
    txt = str(n)
    m = mask_digits(AX, AY, txt) * plate
    soft = m.copy()
    soft[1:-1, 1:-1] = np.maximum(m[1:-1, 1:-1], 0.5 * (m[:-2, 1:-1] + m[2:, 1:-1] + m[1:-1, :-2] + m[1:-1, 2:]) / 2)
    out = base.copy()
    out[..., :3] = out[..., :3] * (1 - 0.55 * soft[..., None])                 # engraved groove: darker brass
    bev = np.zeros_like(m)
    bev[:-1, :-1] = np.clip(m[1:, 1:] - m[:-1, :-1], 0, 1) * plate[:-1, :-1]
    out[..., :3] = np.clip(out[..., :3] + 0.15 * bev[..., None], 0, 1)         # bright lower edge of the groove
    dst = os.path.join(TEX, f"{DST}{n:02d}_co.png")
    o = bpy.data.images.new(os.path.basename(dst), W, H, alpha=False)
    o.colorspace_settings.name = "sRGB"
    out[..., 3] = 1.0
    o.pixels.foreach_set(out.ravel())
    o.filepath_raw = dst; o.file_format = "PNG"; o.save()
    print(f"  -> {os.path.basename(dst)}: {int(m.sum())} texels gravados ({txt})")
