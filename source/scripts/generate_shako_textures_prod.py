# Phase 6: paints the shako texture set from the mesh itself (no hand-placed coordinates).
# The UV triangles of HCL_Shako_Pruss_LOD0 are rasterised to get, for every texel, its material and its position on the
# shako (local frame of shako_fit). Procedural rules then place felt, patent leather, leather, stitches, back seam,
# cockade pleats, lace, brass, etc. Outputs (2048x2048 PNG, sources for ImageToPAA):
#   <prefix>_co.png    colour (sRGB)
#   <prefix>_nohq.png  tangent-space normal map, OpenGL convention (+Y up) - verified as Arma's convention
#   <prefix>_smdi.png  R = 1, G = specular intensity, B = glossiness (as read by TexConvert.cfg class *_smdi)
# Usage:
#   blender -b <LOD0.blend> --python generate_shako_textures_prod.py -- <Samples Test_Character_01 dir> <out_dir> <prefix> [amarela|branca|preta] [latao|estanho] [badge_tone=original|latao|prata] [linha=branca|verde|latao]
# Badge variants (object property hcl_distintivo = JSON from build_shako_production.py): the front of the badge is
# painted from the Eras Mod art it was traced from (authorised by the user), 1:1, with its relief in the normal map.
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit
import shako_uv_layout as LY

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_DIR, PREFIX = args[:3]
_pos = [a for a in args[3:] if "=" not in a]
OPT = dict(a.split("=", 1) for a in args[3:] if "=" in a)
LOOP = _pos[0] if len(_pos) > 0 else "amarela"
METAL = _pos[1] if len(_pos) > 1 else "latao"
BADGE_TONE = OPT.get("badge_tone", "original")
F = shako_fit.compute(SAMPLES)
S, H = F["S"], F["H"]
ROOT_INV = F["root"].inverted()
T = LY.TEX
rng = np.random.default_rng(1813)

def rx(z): return F["base_hw"] + (F["top_hw"] - F["base_hw"]) * z / H
def ry(z): return F["base_hd"] + (F["top_hd"] - F["base_hd"]) * z / H

# ---------------------------------------------------------------- rasterise UVs -> material id + local position
ob = bpy.data.objects["HCL_Shako_Pruss_LOD0"]
me = ob.data
mat_names = [m.name for m in me.materials]
MID = {n: i for i, n in enumerate(mat_names)}
bm = bmesh.new(); bm.from_mesh(me)
uvl = bm.loops.layers.uv.active
mat_id = np.full((T, T), -1, np.int16)
pos = np.zeros((T, T, 3), np.float32)

for f in bm.faces:
    loops = list(f.loops)
    P2 = [(l[uvl].uv.x * T - 0.5, (1 - l[uvl].uv.y) * T - 0.5) for l in loops]
    P3 = [ROOT_INV @ l.vert.co for l in loops]
    for k in range(1, len(loops) - 1):
        (x0, y0), (x1, y1), (x2, y2) = P2[0], P2[k], P2[k + 1]
        a, b, c = P3[0], P3[k], P3[k + 1]
        xmin, xmax = int(max(0, math.floor(min(x0, x1, x2)))), int(min(T - 1, math.ceil(max(x0, x1, x2))))
        ymin, ymax = int(max(0, math.floor(min(y0, y1, y2)))), int(min(T - 1, math.ceil(max(y0, y1, y2))))
        if xmax < xmin or ymax < ymin:
            continue
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(det) < 1e-12:
            continue
        gy, gx = np.mgrid[ymin:ymax + 1, xmin:xmax + 1].astype(np.float32)
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / det
        w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / det
        w2 = 1 - w0 - w1
        inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        if not inside.any():
            continue
        yy, xx = gy[inside].astype(int), gx[inside].astype(int)
        mat_id[yy, xx] = f.material_index
        for d in range(3):
            pos[yy, xx, d] = w0[inside] * a[d] + w1[inside] * b[d] + w2[inside] * c[d]

covered = mat_id >= 0
print(f"RASTER texels covered: {covered.mean() * 100:.1f}%")

# dilate 12 px so texture filtering/mipmaps never pick up empty texels at island borders
for _ in range(12):
    empty = mat_id < 0
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        src_m = np.roll(mat_id, (dy, dx), axis=(0, 1))
        src_p = np.roll(pos, (dy, dx), axis=(0, 1))
        take = empty & (src_m >= 0)
        mat_id[take] = src_m[take]
        pos[take] = src_p[take]
        empty = mat_id < 0

X, Y, Z = pos[..., 0], pos[..., 1], pos[..., 2]
yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)

# ---------------------------------------------------------------- noise helpers (texture space)
def vnoise(cy, cx):
    g = rng.random((cy + 1, cx + 1)).astype(np.float32)
    xs, ys = np.arange(T) * cx / T, np.arange(T) * cy / T
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), (fy * fy * (3 - 2 * fy))[:, None]
    a, b, c, d = g[y0][:, x0], g[y0][:, x0 + 1], g[y0 + 1][:, x0], g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def fbm(c0, octaves=4):
    tot, amp, norm = np.zeros((T, T), np.float32), 1.0, 0.0
    for o in range(octaves):
        tot += amp * vnoise(min(c0 * 2 ** o, T), min(c0 * 2 ** o, T)); norm += amp; amp *= 0.5
    return tot / norm * 2 - 1

N_LOW, N_MID, N_FINE = fbm(6), fbm(48), fbm(256, 2)
PIX = rng.random((T, T)).astype(np.float32) - 0.5

col = np.zeros((T, T, 3), np.float32)
hgt = np.zeros((T, T), np.float32)
spec = np.zeros((T, T), np.float32)
gloss = np.zeros((T, T), np.float32)

def paint(mask, rgb, h=None, sp=0.0, gl=0.0):
    col[mask] = rgb[mask] if np.ndim(rgb) == 3 else rgb
    if h is not None:
        hgt[mask] = h[mask] if np.ndim(h) == 2 else h
    spec[mask] = sp[mask] if np.ndim(sp) == 2 else sp
    gloss[mask] = gl[mask] if np.ndim(gl) == 2 else gl

theta = np.arctan2(X / rx(np.clip(Z, 0, H)), Y / ry(np.clip(Z, 0, H)))     # 0 = back, +-pi = front
ratio = np.sqrt((X / rx(np.clip(Z, 0, H))) ** 2 + (Y / ry(np.clip(Z, 0, H))) ** 2)
rmean = (rx(np.clip(Z, 0, H)) + ry(np.clip(Z, 0, H))) / 2
arcpos = theta * rmean                                                        # metres around the body

def dashes(coord_m, period, duty=0.55):
    return (np.mod(coord_m / period, 1.0) < duty)

# ---------------------------------------------------------------- felt (wall + crown)
m = mat_id == MID["HCL_feltro"]
crown = m & (Z > H - 0.0105)          # the felt wall ends under the binding (H - 0.0115); anything above is the concave crown
wall = m & ~crown
felt_rgb = np.dstack([0.030 + 0.006 * N_LOW + 0.004 * N_MID + 0.006 * PIX] * 3) * np.array([1.0, 1.04, 1.25], np.float32)
felt_h = 0.04 * N_MID + 0.03 * N_FINE + 0.02 * PIX
dust = np.clip((Z - (H - 0.035)) / 0.035, 0, 1) * 0.010
felt_rgb = felt_rgb + dust[..., None] * np.array([0.9, 0.85, 0.7], np.float32)
seam_d = np.abs(np.arctan2(np.sin(theta), np.cos(theta))) * rmean               # distance to the back seam (m)
seam = wall & (seam_d < 0.0007)
stitch = wall & (np.abs(seam_d - 0.003) < 0.0004) & dashes(Z, 0.0045)
paint(wall, felt_rgb, felt_h, 0.04, 0.10)
paint(seam, felt_rgb * 0.45, np.full((T, T), -0.25, np.float32), 0.02, 0.05)
paint(stitch, np.full((T, T, 3), 0.055, np.float32), np.full((T, T), 0.18, np.float32), 0.05, 0.12)
crho = np.sqrt((X / (rx(H) - 0.0105)) ** 2 + (Y / (ry(H) - 0.0105)) ** 2)
crown_rgb = felt_rgb + 0.008
cstitch = crown & (np.abs(crho - 0.945) < 0.006) & dashes(np.arctan2(X, Y) * 0.12, 0.004)
paint(crown, crown_rgb, felt_h, 0.04, 0.10)
paint(cstitch, np.full((T, T, 3), 0.06, np.float32), np.full((T, T), 0.15, np.float32), 0.05, 0.12)

# ---------------------------------------------------------------- patent leather (band + visor)
m = mat_id == MID["HCL_couro_envernizado"]
band = m & (ratio < 1.045) & (Z > -0.0008)
visor = m & ~band
pat_rgb = np.dstack([0.012 + 0.003 * N_LOW + 0.002 * PIX] * 3) * np.array([1.0, 1.0, 1.15], np.float32)
pat_h = 0.006 * N_LOW
B = S["band"]
band_edge = band & ((Z < 0.0025) | (Z > B - 0.0012))
paint(band, pat_rgb, pat_h, 0.85, 0.92)
paint(band_edge, pat_rgb * 1.6, pat_h, 0.65, 0.75)                     # rolled edges: slightly worn
# optional coloured line along the top of the band (Eras Mod atlases 01-03: white, green or brass line between the
# felt and the band). Colour only: the relief and gloss maps stay shared by all variants of the same badge model.
LINE = OPT.get("linha")
if LINE:
    line_rgb = {"branca": [0.80, 0.80, 0.76], "verde": [0.10, 0.30, 0.13], "latao": [0.78, 0.60, 0.26]}[LINE]
    line = band & (Z > B - 0.0042) & (Z < B - 0.0013)
    col[line] = (np.array(line_rgb, np.float32)[None, None, :] * (0.92 + 0.08 * N_MID[..., None]))[line]
half_span = math.asin(min(0.99, S["visor_chord"] / 2 / F["base_hw"]))
phi = np.arctan2(np.sin(theta - np.pi), np.cos(theta - np.pi))
L = np.maximum(0.004, shako_fit.VISOR_LEN * np.clip(np.cos(np.clip(phi / half_span, -1, 1) * np.pi / 2), 0, 1) ** 0.5)
horiz = np.hypot(X, Y) - np.hypot(rx(0.006) * np.sin(theta), ry(0.006) * np.cos(theta))
dist = np.clip(horiz, 0, None) / math.cos(shako_fit.VISOR_DROP)
v_stitch = visor & (L > 0.012) & (np.abs(dist - (L - 0.0045)) < 0.00045) & dashes(phi * 0.1, 0.0035)
v_edge = visor & (dist > L - 0.0016)
scratches = visor & (N_FINE > 0.78)                                  # rare, subtle wear marks
paint(visor, pat_rgb, pat_h, 0.85, 0.92)
paint(scratches, pat_rgb * 1.35, pat_h - 0.015, 0.65, 0.70)
paint(v_edge, pat_rgb * 1.5, pat_h + 0.05, 0.6, 0.7)
paint(v_stitch, np.full((T, T, 3), 0.05, np.float32), np.full((T, T), -0.12, np.float32), 0.2, 0.3)

# ---------------------------------------------------------------- leather (binding + chinstrap)
m = mat_id == MID["HCL_couro"]
binding = m & (Z > H - 0.0125) & (ratio < 1.06)
strap = m & ~binding
lea_rgb = np.dstack([0.020 + 0.005 * N_MID + 0.004 * PIX] * 3) * np.array([1.05, 1.0, 0.97], np.float32)
lea_h = 0.05 * N_FINE + 0.02 * PIX
b_stitch = binding & (np.abs(Z - (H - 0.0078)) < 0.0004) & dashes(arcpos, 0.004)
paint(binding, lea_rgb, lea_h, 0.30, 0.45)
paint(b_stitch, np.full((T, T, 3), 0.045, np.float32), np.full((T, T), 0.15, np.float32), 0.10, 0.20)
paint(strap, lea_rgb, lea_h, 0.30, 0.45)
ox, oy = LY.STRAP_OUTER["x0"], LY.STRAP_OUTER["y0"]
across = (yy - oy) / LY.D_BIG
s_stitch = strap & (yy >= oy) & (yy <= oy + 0.012 * LY.D_BIG + 1) & \
           ((np.abs(across - 0.0019) < 0.00035) | (np.abs(across - (0.012 - 0.0019)) < 0.00035)) & dashes((xx - ox) / LY.D_BIG, 0.0035)
paint(s_stitch, np.full((T, T, 3), 0.05, np.float32), np.full((T, T), 0.15, np.float32), 0.10, 0.20)

# ---------------------------------------------------------------- lining
m = mat_id == MID["HCL_forro"]
weave = 0.5 + 0.5 * np.sin(xx * 1.7) * np.sin(yy * 1.7)
lin_rgb = np.dstack([0.20 + 0.03 * weave, 0.15 + 0.02 * weave, 0.10 + 0.015 * weave]) * (1 + 0.15 * N_MID[..., None])
paint(m, lin_rgb, 0.08 * weave, 0.03, 0.10)

# ---------------------------------------------------------------- cockade (black centre, pleated white ring, black rim)
CR = S["cockade_r"]
CZ = min(S["cockade_z"], H - 0.0045 - CR - 0.0005)
m = (mat_id == MID["HCL_tecido_branco"]) | (mat_id == MID["HCL_tecido_preto"])
rho = np.hypot(X, Z - CZ) / CR
ang = np.arctan2(Z - CZ, X)
pleat = 0.5 + 0.5 * np.cos(ang * 44)
white = np.dstack([0.83 * (0.86 + 0.14 * pleat)] * 3) * np.array([1.0, 0.99, 0.94], np.float32) + 0.02 * N_MID[..., None]
black = np.dstack([0.028 + 0.01 * N_MID] * 3)
is_black = m & ((rho < 0.45) | (rho > 0.93))
paint(m, white, 0.25 * pleat, 0.08, 0.20)
paint(is_black, black, 0.05 * N_MID + 0.15 * pleat * (rho > 0.93), 0.06, 0.15)

# ---------------------------------------------------------------- loop (lace)
m = mat_id == MID["HCL_la_amarela"]
LW = S["loop_w"]
weave = (np.mod(Z * 400 + np.abs(X) * 300, 1.0) < 0.5)          # herringbone, ~2.5 mm period (~10 px)
edge = np.abs(X) > LW / 2 - 0.0013
if LOOP == "branca":
    main, edge_c = np.array([0.80, 0.80, 0.78], np.float32), np.array([0.55, 0.55, 0.55], np.float32)
elif LOOP == "preta":                                                    # black loop (Eras Mod atlas 02, 2nd slot)
    main, edge_c = np.array([0.050, 0.050, 0.050], np.float32), np.array([0.14, 0.14, 0.14], np.float32)
else:
    main, edge_c = np.array([0.86, 0.64, 0.16], np.float32), np.array([0.84, 0.83, 0.79], np.float32)
lace = np.where(weave[..., None], main, main * 0.88) * (1 + 0.05 * N_MID[..., None])
lace = np.where(edge[..., None], edge_c, lace)
paint(m, lace, np.where(weave, 0.15, -0.05) + np.where(edge, -0.1, 0), 0.06, 0.15)

# ---------------------------------------------------------------- brass / tin (cipher + buttons)
m = mat_id == MID["HCL_latao"]
metal = np.array([0.78, 0.60, 0.28] if METAL == "latao" else [0.72, 0.73, 0.74], np.float32)
tarnish = np.clip(0.5 + 0.5 * N_MID, 0, 1)
met_rgb = metal * (0.80 + 0.20 * tarnish)[..., None]
paint(m, met_rgb, 0.01 * N_FINE, 0.75 + 0.15 * tarnish, 0.65 + 0.15 * tarnish)

# ---------------------------------------------------------------- traced badge (eagle / star): the source art, 1:1
meta = ob.get("hcl_distintivo", "")
if meta.startswith("{"):
    bmeta = json.loads(meta)
    src = bpy.data.images.load(bmeta["image"])
    sw, sh = src.size
    art = np.array(src.pixels[:], np.float32).reshape(sh, sw, 4)[::-1]          # top row first, sRGB values
    x0b, y0b = bmeta["box"][0], bmeta["box"][1]
    D, kf = bmeta["density"], bmeta["kf"]
    half_w, half_h = bmeta["size"][0] / 2 * D + 6, bmeta["size"][1] / 2 * D + 6
    rect = (np.abs(xx + 0.5 - bmeta["uv_cx"]) <= half_w) & (np.abs(yy + 0.5 - bmeta["uv_cy"]) <= half_h)
    bmask = (mat_id == MID["HCL_latao"]) & rect
    # flat badge coordinates from the texel's 3D position (immune to any UV mirroring done after the build):
    # the badge was wrapped as x = (r + off) sin(lx / r) on the front, z = cipher_z + ly
    rzz = rx(np.clip(Z, 0, H))
    lx = rzz * np.arcsin(np.clip(X / (rzz + 0.0015), -1, 1))
    ly = Z - S["cipher_z"]
    ax = x0b + lx / kf + bmeta["cx"]                                           # source-image column
    ay = y0b - (ly / kf + bmeta["cy"])                                         # source-image row (curve y is up)
    def sample(img, X_, Y_):
        X_ = np.clip(X_, 0, img.shape[1] - 1.001); Y_ = np.clip(Y_, 0, img.shape[0] - 1.001)
        x0_, y0_ = np.floor(X_).astype(int), np.floor(Y_).astype(int)
        fx_, fy_ = (X_ - x0_)[..., None], (Y_ - y0_)[..., None]
        return ((img[y0_, x0_] * (1 - fx_) + img[y0_, x0_ + 1] * fx_) * (1 - fy_)
                + (img[y0_ + 1, x0_] * (1 - fx_) + img[y0_ + 1, x0_ + 1] * fx_) * fy_)
    s = sample(art, ax[bmask], ay[bmask])
    rgb, alpha = s[:, :3], s[:, 3]
    lum = rgb.mean(axis=1)
    if BADGE_TONE == "latao":                                                  # brass version of a silver badge
        rgb = lum[:, None] * np.array([1.45, 1.10, 0.52], np.float32)
    elif BADGE_TONE == "prata":                                                # the atlas star is gunmetal-dark: polish it
        rgb = np.clip(lum[:, None] * 1.55 + 0.06, 0, 1) * np.array([1.0, 1.0, 1.03], np.float32)
    # relief from the art: local contrast of the luminance (3x3 neighbourhood in the art)
    blur = sum(sample(art, ax[bmask] + dx, ay[bmask] + dy)[:, :3].mean(axis=1)
               for dx in (-2, 0, 2) for dy in (-2, 0, 2)) / 9.0
    relief = np.clip((lum - blur) * 1.2, -0.25, 0.25)
    inside = alpha > 0.5
    base = col[bmask]
    col_b = np.where(inside[:, None], rgb, base)
    hgt_b = np.where(inside, 0.10 + relief, hgt[bmask])
    col[bmask] = col_b
    hgt[bmask] = hgt_b
    spec[bmask] = np.where(inside, 0.55 + 0.35 * np.clip(lum, 0, 1), spec[bmask])
    gloss[bmask] = np.where(inside, 0.55 + 0.25 * np.clip(lum, 0, 1), gloss[bmask])
    print(f"BADGE painted from {os.path.basename(bmeta['image'])}: {int(inside.sum())} texels, tone={BADGE_TONE}")

# ---------------------------------------------------------------- outputs
print("COVERAGE " + ", ".join(f"{n}={(mat_id == i).mean() * 100:.1f}%" for n, i in MID.items()))

def save(arr, name):
    img = bpy.data.images.new(name, T, T, alpha=False)
    rgba = np.concatenate([np.clip(arr, 0, 1)[::-1], np.ones((T, T, 1), np.float32)], axis=2)
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = 'PNG'
    p = os.path.join(OUT_DIR, name)
    img.save(filepath=p)
    print("OK", p)

os.makedirs(OUT_DIR, exist_ok=True)
save(col, f"{PREFIX}_co.png")
gy_, gx_ = np.gradient(hgt)
k = 2.5
n = np.dstack([-gx_ * k, gy_ * k, np.ones_like(hgt)])                 # OpenGL / +Y up (verified for Arma 3)
n /= np.linalg.norm(n, axis=2, keepdims=True)
save(n * 0.5 + 0.5, f"{PREFIX}_nohq.png")
save(np.dstack([np.ones_like(spec), spec, gloss]), f"{PREFIX}_smdi.png")
