# Phase 6 (uniform): paints the texture set of HCL_U_Pruss1813_01_LOD0 from the mesh itself, one colour palette per
# regimental variant (palettes sampled from the Eras Mod infantry atlases, see docs/specs/variantes_regimentos_pruss.md).
# For every texel the UV triangles give the piece, the material, the 3D position and the face normal; the rules below
# place cloth, facings, turnbacks, piping, shoulder boards, buttons, leather, wear. Patterns that must not show the UV
# seams are computed in 3D. Outputs (2048x2048 PNG, sources for ImageToPAA):
#   <prefix>_co.png (one per variant), <prefix>_nohq.png and <prefix>_smdi.png (shared by all variants)
#   blender -b <LOD0.blend> --python generate_uniform_textures.py -- <out_dir> <variants.json> [only=<id,id>] [maps]
#   "maps" also writes the shared _nohq and _smdi.
import bpy, bmesh, sys, os, math, json
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
OUT_DIR, VARIANTS = a[0], json.load(open(a[1]))
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
ONLY = set(OPT["only"].split(",")) if "only" in OPT else None
MAPS = "maps" in a[2:]
T = 2048
rng = np.random.default_rng(1813)

ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = ob["hcl_partes"].split(",")
me = ob.data
mats = [m.name for m in me.materials]
MID = {n: i for i, n in enumerate(mats)}
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(me)
uvl = bm.loops.layers.uv.active
PL = bm.faces.layers.int.get("hcl_part")
bm.normal_update()

# ---------------------------------------------------------------- rasterise
mat_id = np.full((T, T), -1, np.int16)
part_id = np.full((T, T), -1, np.int16)
pos = np.zeros((T, T, 3), np.float32)
nrm = np.zeros((T, T, 3), np.float32)
for f in bm.faces:
    if f[PL] == PID["maos_template"]:
        continue                                                 # hands use the identity's skin texture
    loops = list(f.loops)
    P2 = [(l[uvl].uv.x * T - 0.5, (1 - l[uvl].uv.y) * T - 0.5) for l in loops]
    P3 = [l.vert.co for l in loops]
    n = f.normal
    for k in range(1, len(loops) - 1):
        (x0, y0), (x1, y1), (x2, y2) = P2[0], P2[k], P2[k + 1]
        A, B, C = P3[0], P3[k], P3[k + 1]
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
        ins = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        if not ins.any():
            continue
        yy_, xx_ = gy[ins].astype(int), gx[ins].astype(int)
        mat_id[yy_, xx_] = f.material_index
        part_id[yy_, xx_] = f[PL]
        for d in range(3):
            pos[yy_, xx_, d] = w0[ins] * A[d] + w1[ins] * B[d] + w2[ins] * C[d]
            nrm[yy_, xx_, d] = n[d]
print(f"RASTER covered {np.mean(mat_id >= 0) * 100:.1f}%")
for _ in range(12):                                              # dilate: no empty texels at chart borders
    empty = mat_id < 0
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        sm, sp_, spos, snr = (np.roll(x, (dy, dx), axis=(0, 1)) for x in (mat_id, part_id, pos, nrm))
        take = empty & (sm >= 0)
        mat_id[take], part_id[take], pos[take], nrm[take] = sm[take], sp_[take], spos[take], snr[take]
        empty = mat_id < 0
X, Y, Z = pos[..., 0], pos[..., 1], pos[..., 2]
yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
GROUND = -1.0069
Hh = Z - GROUND                                                  # height above the ground


# ---------------------------------------------------------------- 3D value noise (no seams across UV charts)
LAT = rng.random((64, 64, 64)).astype(np.float32)
def noise3(scale, off=0.0):
    p = pos * scale + off
    i = np.floor(p).astype(np.int64); f = p - i
    f = f * f * (3 - 2 * f)
    i0, i1 = i % 64, (i + 1) % 64
    def g(ix, iy, iz):
        return LAT[ix[..., 0], iy[..., 1], iz[..., 2]]
    c000, c100, c010, c110 = g(i0, i0, i0), g(i1, i0, i0), g(i0, i1, i0), g(i1, i1, i0)
    c001, c101, c011, c111 = g(i0, i0, i1), g(i1, i0, i1), g(i0, i1, i1), g(i1, i1, i1)
    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    x00 = c000 * (1 - fx) + c100 * fx; x10 = c010 * (1 - fx) + c110 * fx
    x01 = c001 * (1 - fx) + c101 * fx; x11 = c011 * (1 - fx) + c111 * fx
    return ((x00 * (1 - fy) + x10 * fy) * (1 - fz) + (x01 * (1 - fy) + x11 * fy) * fz) * 2 - 1
N_BIG, N_MID, N_FINE = noise3(9.0), noise3(45.0, 7.3), noise3(160.0, 3.1)
PIX = rng.random((T, T)).astype(np.float32) - 0.5
TWILL = np.sin((xx + yy) * (2 * math.pi / 3.0)) * 0.5                        # fine diagonal twill (texture space)

is_ = lambda name: part_id == PID[name]
isp = lambda prefix: np.isin(part_id, [i for n, i in PID.items() if n.startswith(prefix)])
ism = lambda name: mat_id == MID[name]


def cloth(rgb, mottle=0.06, grain=0.035):
    base = np.array(rgb, np.float32)
    v = 1 + mottle * N_BIG + 0.5 * mottle * N_MID + grain * PIX + 0.02 * TWILL
    return base[None, None, :] * v[..., None]


def wall_mask(part_mask, top_cos=0.6):
    """Faces of a raised piece that are walls (normal far from the piece's mean top normal)."""
    nm = nrm[part_mask]
    top = nm.mean(axis=0); top /= np.linalg.norm(top) + 1e-9
    out = np.zeros((T, T), bool)
    out[part_mask] = np.abs(nm @ top) < top_cos
    return out


def grow(mask, inside, px):
    m = mask.copy()
    for _ in range(px):
        g = m.copy()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            g |= np.roll(m, (dy, dx), axis=(0, 1))
        m = g & inside
    return m


# ---------------------------------------------------------------- shared maps (height, spec, gloss)
hgt = 0.04 * N_MID + 0.03 * N_FINE + 0.03 * TWILL + 0.015 * PIX
spec = np.full((T, T), 0.05, np.float32)
gloss = np.full((T, T), 0.12, np.float32)
# front closure piping of the coat (edge of the overlapping panel, theta = -0.18 around the torso)
coat = is_("casaco_corpo")
theta = np.arctan2(X, -(Y - 0.015))
piping_front = coat & (np.abs(theta + 0.18) < 0.017) & (Y < -0.03) & (Hh > 1.10) & (Hh < 1.545)
hgt[piping_front] += 0.12
flap_wall = {s: wall_mask(is_(f"pala_{s}")) for s in "ED"}
flap_pipe = {s: grow(flap_wall[s], is_(f"pala_{s}"), 2) for s in "ED"}
strap_wall = {s: wall_mask(is_(f"platina_{s}")) for s in "ED"}
strap_pipe = {s: grow(strap_wall[s], is_(f"platina_{s}"), 2) for s in "ED"}
for s in "ED":
    hgt[flap_pipe[s]] += 0.08
    hgt[strap_pipe[s]] += 0.08
# trouser seat seam and gaiter strip edge stitches (3D rules)
gait = isp("polaina")
leather = ism("HCL_couro_sapato")
sole = ism("HCL_sola")
metal = ism("HCL_latao")
spec[leather], gloss[leather] = 0.45, 0.62
spec[sole], gloss[sole] = 0.12, 0.25
spec[metal], gloss[metal] = 0.85, 0.75
spec[gait], gloss[gait] = 0.10, 0.22
hgt[leather] = 0.02 * N_FINE[leather]
hgt[metal] = 0.0
# buttons share one corner square: concentric relief
bu = (xx / T >= 0.948) & (1 - yy / T >= 0.948)
rr = np.hypot(xx / T - 0.9725, (1 - yy / T) - 0.9725) / 0.0225
hgt[bu & metal] = np.clip(0.3 * (1 - rr[bu & metal]) + 0.08 * (np.abs(rr[bu & metal] - 0.62) < 0.08), 0, 0.4)


# ---------------------------------------------------------------- colour per variant
def paint_variant(v):
    col = np.zeros((T, T, 3), np.float32)
    C = {k: np.array(c, np.float32) for k, c in v["cores"].items()}
    azul = ism("HCL_la_azul"); verm = ism("HCL_la_vermelha"); bran = ism("HCL_la_branca")
    cinza = ism("HCL_la_cinza")
    col[azul] = cloth(C["casaca"])[azul]
    # red material = facing colour on collar and cuffs, turnback colour on the tails (outer turnbacks and lining)
    gola = verm & is_("gola"); punho = verm & isp("punho"); abas = verm & isp("aba")
    col[gola] = cloth(C["gola"])[gola]
    col[punho] = cloth(C["gola"])[punho]
    col[abas] = cloth(C["viras"])[abas]
    col[piping_front] = cloth(C["debrum"], 0.03)[piping_front]
    for s in "ED":
        col[flap_pipe[s]] = cloth(C["debrum"], 0.03)[flap_pipe[s]]
        top = bran & is_(f"platina_{s}")
        col[top] = cloth(C["platina"], 0.04)[top]
        col[strap_pipe[s]] = cloth(C["platina_borda"], 0.03)[strap_pipe[s]]
    # trousers: grey, dust towards the gaiters, knees slightly worn
    tro = cloth(C["calca"], 0.07, 0.04)
    dust = np.clip((0.62 - Hh) / 0.25, 0, 1) * 0.10
    tro = tro * (1 - 0.4 * dust)[..., None] + dust[..., None] * np.array([0.42, 0.38, 0.30], np.float32)
    col[cinza] = tro[cinza]
    # gaiters: black cloth, road dust rising from the bottom, stitched strip edges
    gai = cloth(C["polaina"], 0.10, 0.05)
    gd = np.clip((0.22 - Hh) / 0.15, 0, 1) * 0.25
    gai = gai + gd[..., None] * np.array([0.30, 0.27, 0.22], np.float32)
    col[gait] = gai[gait]
    # shoes and soles
    shoe = np.array(C["sapato"], np.float32)[None, None, :] * (1 + 0.15 * N_MID[..., None] + 0.05 * PIX[..., None])
    scuff = np.clip((N_FINE - 0.55) * 3, 0, 1)[..., None] * 0.08
    col[leather] = (shoe + scuff)[leather]
    col[sole] = cloth(C["sola"], 0.12)[sole]
    # buttons: polished metal with darker rim
    m_rgb = np.array(C["botoes"], np.float32)
    bt = m_rgb[None, None, :] * (0.85 + 0.25 * np.clip(1 - rr, 0, 1))[..., None]
    col[metal] = bt[metal]
    # coat hem and tails: faint wear lightening on the lowest centimetres
    low_tails = isp("aba") & (Hh < 0.73)
    col[low_tails] *= 1.06
    return np.clip(col, 0, 1)


def save(arr, name):
    img = bpy.data.images.new(name, T, T, alpha=False)
    rgba = np.concatenate([np.clip(arr, 0, 1)[::-1], np.ones((T, T, 1), np.float32)], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = "PNG"
    p = os.path.join(OUT_DIR, name)
    img.filepath_raw = p
    img.save()
    print("OK", p)


os.makedirs(OUT_DIR, exist_ok=True)
for vid, v in VARIANTS.items():
    if ONLY and vid not in ONLY:
        continue
    save(paint_variant(v), f"{v['prefixo']}_co.png")
if MAPS:
    gy_, gx_ = np.gradient(hgt)
    k = 2.5
    n = np.dstack([-gx_ * k, gy_ * k, np.ones_like(hgt)])                 # OpenGL / +Y up (as measured for Arma 3)
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    save(n * 0.5 + 0.5, "hcl_u_pruss1813_nohq.png")
    save(np.dstack([np.ones_like(spec), spec, gloss]), "hcl_u_pruss1813_smdi.png")
