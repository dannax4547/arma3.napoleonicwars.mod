# Phase 6, texture set v2 of the uniform HCL_U_Pruss1813_01_LOD0 (v1: generate_uniform_textures.py, kept; its outputs are
# copied in source/textures/hcl_uniforme_pruss/_v1). Same UV layout, same palettes (variantes_regimentos.json); added:
#   - ambient occlusion baked with Cycles from the uniform itself (hands and buttons left out of the bake)
#   - hems and seams on every border of every garment piece (rolled edge, seam groove, hem allowance ridge), from the
#     3D distance of each texel to the borders of its own piece; welt stitching where the shoe upper meets the sole
#   - tailoring seams by 3D rules: centre back and curved side-back seams of the coat, two-piece sleeve seams, outer and
#     inner leg seams of the trousers, the buttoned flap edge of the gaiters (line through the gaiter buttons)
#   - cloth folds in the normal map and in the colour: inner elbow, above the cuffs, armpits, back of the knees, front of
#     the hips, ankles (gaiters), drape of the tails, toe creases of the shoes
#   - fulled wool broadcloth (no visible weave), sun fading on the upper surfaces, wear shine (elbows, cuff and front
#     edges, seat, knees), road dust and dried mud rising from the ground, grime at collar and cuffs
#   - heights painted in millimetres -> OpenGL normal map with the real texel size; gradients never cross UV islands
#   - optional colour keys per variant: "punho" (cuffs, default = collar colour), "gola_debrum" / "punho_debrum" /
#     "viras_debrum" (piping along the borders of collar, cuffs, turnbacks), "pala" (cuff flaps, default = coat),
#     "galoes" (lace bar under each cuff-flap button); colour only, so _nohq / _smdi stay shared by all variants
#   blender -b <LOD0.blend> --python generate_uniform_textures_v2.py -- <out_dir> <variants.json> [only=<id,id>] [maps]
#                                                                      [ao_samples=N]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

a = sys.argv[sys.argv.index("--") + 1:]
OUT_DIR, VARIANTS = a[0], json.load(open(a[1]))
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
ONLY = set(OPT["only"].split(",")) if "only" in OPT else None
MAPS = "maps" in a[2:]
T = 2048
GROUND = -1.0069
rng = np.random.default_rng(1813)
scene = bpy.context.scene

# obj=<uniform object> and mapas=<prefix of the shared maps> (defaults: the Prussian uniform); the French coat 1812
# (build_uniforme_fr.py) is the same mesh with lapels: colour keys "lapela" (default: collar colour) and "lapela_debrum"
ob = bpy.data.objects[OPT.get("obj", "HCL_U_Pruss1813_01_LOD0")]
MAPAS = OPT.get("mapas", "hcl_u_pruss1813")
parts = ob["hcl_partes"].split(",")
me = ob.data
mats = [m.name for m in me.materials]
MID = {n: i for i, n in enumerate(mats)}
PID = {n: i for i, n in enumerate(parts)}
HANDS, BTN = PID["maos_template"], PID["botoes"]
os.makedirs(OUT_DIR, exist_ok=True)


# ---------------------------------------------------------------- 1. ambient occlusion (the uniform alone)
def bake_ao(samples):
    img = bpy.data.images.new("AO_uniforme", T, T, alpha=False)
    dummy = bpy.data.images.new("AO_descartar", 256, 256, alpha=False)
    bm_ = {}
    for nm, im in (("BAKE", img), ("BAKE_X", dummy)):
        m = bpy.data.materials.new(nm); m.use_nodes = True
        n = m.node_tree.nodes.new("ShaderNodeTexImage"); n.image = im; m.node_tree.nodes.active = n
        bm_[nm] = m
    # bake on a temporary copy WITHOUT the template hands: their UVs belong to the template's own skin texture and
    # overlap the atlas; even with a discard material Cycles wrote two fingertip triangles into this AO (a dark
    # triangle on the trouser seat, found 2026-10-11)
    ob_full = ob
    tmp_me = ob_full.data.copy()
    bmt = bmesh.new(); bmt.from_mesh(tmp_me)
    plt = bmt.faces.layers.int.get("hcl_part")
    bmesh.ops.delete(bmt, geom=[f for f in bmt.faces if f[plt] == HANDS], context="FACES")
    bmt.to_mesh(tmp_me); bmt.free()
    tgt = bpy.data.objects.new("AO_sem_maos", tmp_me)
    scene.collection.objects.link(tgt)
    tgt.matrix_world = ob_full.matrix_world
    saved = None
    for i, s in enumerate(tgt.material_slots):
        s.link = "OBJECT"
        s.material = bm_["BAKE_X"] if mats[i] in ("HCL_pele_hl", "HCL_latao") else bm_["BAKE"]
    hidden = []
    for o in scene.objects:
        if o is not tgt and o.type == "MESH" and not o.hide_render:
            o.hide_render = True; hidden.append(o)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("AO_mundo")
    scene.world.light_settings.distance = 0.08
    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = samples
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    tgt.hide_set(False); tgt.hide_render = False
    tgt.select_set(True); bpy.context.view_layer.objects.active = tgt
    bpy.ops.object.bake(type="AO", margin=8, use_clear=True)
    px = np.array(img.pixels[:], np.float32).reshape(T, T, 4)[::-1, :, 0].copy()
    bpy.data.objects.remove(tgt)
    bpy.data.meshes.remove(tmp_me)
    for o in hidden:
        o.hide_render = False
    return px


AO = bake_ao(int(OPT.get("ao_samples", 64)))
print(f"AO mean (garment texels later) raw {AO.mean():.3f}")

# ---------------------------------------------------------------- 2. rasterise part, material, position, normal, island
bm = bmesh.new(); bm.from_mesh(me)
uvl = bm.loops.layers.uv.active
PL = bm.faces.layers.int.get("hcl_part")
bm.normal_update()
parent = list(range(len(bm.faces)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


for e in bm.edges:
    lf = e.link_loops
    if len(lf) != 2:
        continue
    la, lb = lf
    uv_at = lambda l, v: l[uvl].uv if l.vert == v else l.link_loop_next[uvl].uv
    if all((uv_at(la, v) - uv_at(lb, v)).length < 1e-6 for v in e.verts):
        parent[find(la.face.index)] = find(lb.face.index)
island = [find(i) for i in range(len(bm.faces))]

mat_id = np.full((T, T), -1, np.int16)
part_id = np.full((T, T), -1, np.int16)
isl_id = np.full((T, T), -1, np.int32)
pos = np.zeros((T, T, 3), np.float32)
nrm = np.zeros((T, T, 3), np.float32)
for f in bm.faces:
    if f[PL] == HANDS:
        continue
    loops = list(f.loops)
    P2 = [(l[uvl].uv.x * T - 0.5, (1 - l[uvl].uv.y) * T - 0.5) for l in loops]
    P3 = [l.vert.co for l in loops]
    N3 = [l.vert.normal if f.smooth else f.normal for l in loops]
    for k in range(1, len(loops) - 1):
        (x0, y0), (x1, y1), (x2, y2) = P2[0], P2[k], P2[k + 1]
        A, B, C = P3[0], P3[k], P3[k + 1]
        NA, NB, NC = N3[0], N3[k], N3[k + 1]
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
        isl_id[yy_, xx_] = island[f.index]
        for d in range(3):
            pos[yy_, xx_, d] = w0[ins] * A[d] + w1[ins] * B[d] + w2[ins] * C[d]
            nrm[yy_, xx_, d] = w0[ins] * NA[d] + w1[ins] * NB[d] + w2[ins] * NC[d]
covered = mat_id >= 0
print(f"RASTER covered {covered.mean() * 100:.1f}%")
# the bake only fills a few texels past each chart: extend the AO of the covered texels into the gutters (mipmaps)
AO = np.where(covered, AO, -1.0).astype(np.float32)
for _ in range(16):
    hole = AO < 0
    if not hole.any():
        break
    acc = np.zeros_like(AO); cnt = np.zeros_like(AO)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb_ = np.roll(AO, (dy, dx), axis=(0, 1))
        ok = nb_ >= 0
        acc += np.where(ok, nb_, 0); cnt += ok
    fill = hole & (cnt > 0)
    AO[fill] = acc[fill] / cnt[fill]
AO[AO < 0] = 1.0
for _ in range(12):
    empty = mat_id < 0
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        sm_ = np.roll(mat_id, (dy, dx), axis=(0, 1))
        take = empty & (sm_ >= 0)
        mat_id[take] = sm_[take]
        for arr in (part_id, isl_id, pos, nrm):
            arr[take] = np.roll(arr, (dy, dx), axis=(0, 1))[take]
        empty = mat_id < 0
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True) + 1e-9
X, Y, Zc = pos[..., 0], pos[..., 1], pos[..., 2]
Hh = Zc - GROUND
yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
is_ = lambda name: part_id == PID[name]
isp = lambda prefix: np.isin(part_id, [i for n, i in PID.items() if n.startswith(prefix)])
ism = lambda name: mat_id == MID[name]
garment = (part_id >= 0) & (part_id != BTN) & (part_id != HANDS)

# ---------------------------------------------------------------- 3. distance to the borders of each piece (3D)
samples = {}
for e in bm.edges:
    fs = list(e.link_faces)
    if not fs:
        continue
    keys = {(f[PL], f.material_index) for f in fs}
    if len(fs) > 1 and len(keys) == 1:
        continue
    v0, v1 = e.verts[0].co, e.verts[1].co
    L = (v1 - v0).length
    n = max(1, int(L / 0.0015))
    mat_change = len({f.material_index for f in fs}) > 1
    for f in fs:
        p = f[PL]
        if p in (HANDS, BTN):
            continue
        # the seat's bottom edge lies on the legs (ajustar_calca.py): one cloth with the legs, no hem there
        if p == PID["calca_assento"] and (v0.z + v1.z) / 2 - GROUND < 0.875:
            continue
        lst = samples.setdefault(p, [])
        for k in range(n + 1):
            lst.append((v0.lerp(v1, k / n), e.index * 0.0137 + L * k / n, mat_change))
bdist = np.full((T, T), 0.05, np.float32)
balong = np.zeros((T, T), np.float32)
bmat = np.zeros((T, T), bool)
for p, lst in samples.items():
    kd = KDTree(len(lst))
    for i, (co, _, _) in enumerate(lst):
        kd.insert(co, i)
    kd.balance()
    ys, xs = np.nonzero(part_id == p)
    P = pos[ys, xs]
    dd = np.empty(len(ys), np.float32); al = np.empty(len(ys), np.float32); mc = np.empty(len(ys), bool)
    for k in range(len(ys)):
        co, i, d = kd.find(P[k])
        dd[k] = d; al[k] = lst[i][1]; mc[k] = lst[i][2]
    bdist[ys, xs] = dd; balong[ys, xs] = al; bmat[ys, xs] = mc
print("BORDAS distancias calculadas para", len(samples), "pecas")
bm.free()


# ---------------------------------------------------------------- 4. limb frames (PCA): sleeves and legs
def limb_frame(names, outward):
    vs = np.array([v.co[:] for v in me.vertices], np.float64)
    pa = me.attributes["hcl_part"].data
    ids = set()
    for poly in me.polygons:
        if parts[pa[poly.index].value] in names:
            ids.update(poly.vertices)
    V = vs[sorted(ids)]
    c = V.mean(axis=0)
    w, vec = np.linalg.eigh(np.cov((V - c).T))
    ax = vec[:, -1]
    if ax @ outward < 0:
        ax = -ax
    s_ = (V - c) @ ax
    return c, ax, s_.min(), s_.max()


def frame_coords(fr, front=np.array([0, -1, 0.0]), side_ref=np.array([0, 0, 1.0])):
    c, ax, smin, smax = fr
    u = front - ax * (front @ ax); u /= np.linalg.norm(u)
    v = side_ref - ax * (side_ref @ ax) - u * (side_ref @ u); v /= np.linalg.norm(v)
    d = pos - c.astype(np.float32)
    s_ = d @ ax.astype(np.float32)
    du, dv = d @ u.astype(np.float32), d @ v.astype(np.float32)
    phi = np.arctan2(dv, du)
    r = np.hypot(du, dv)
    return (s_ - smin) / (smax - smin), s_, phi, r


SLV = {s: limb_frame({f"manga_{s}", f"punho_{s}"}, np.array([1.0 if s == "E" else -1.0, 0, -0.6])) for s in "ED"}
LEG = {s: limb_frame({f"calca_perna_{s}", f"polaina_{s}"}, np.array([0, 0, -1.0])) for s in "ED"}

# ---------------------------------------------------------------- 5. noise
LAT = rng.random((64, 64, 64)).astype(np.float32)


def noise3(scale, off=0.0, P=None):
    p = (pos if P is None else P) * scale + off
    i = np.floor(p).astype(np.int64); f = p - i
    f = f * f * (3 - 2 * f)
    i0, i1 = i % 64, (i + 1) % 64
    g = lambda ix, iy, iz: LAT[ix[..., 0], iy[..., 1], iz[..., 2]]
    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    x00 = g(i0, i0, i0) * (1 - fx) + g(i1, i0, i0) * fx; x10 = g(i0, i1, i0) * (1 - fx) + g(i1, i1, i0) * fx
    x01 = g(i0, i0, i1) * (1 - fx) + g(i1, i0, i1) * fx; x11 = g(i0, i1, i1) * (1 - fx) + g(i1, i1, i1) * fx
    return ((x00 * (1 - fy) + x10 * fy) * (1 - fz) + (x01 * (1 - fy) + x11 * fy) * fz) * 2 - 1


N_BIG, N_MID, N_FINE = noise3(6.0), noise3(35.0, 7.3), noise3(260.0, 3.1)
N_FIB = noise3(700.0, 1.9)
PIX = rng.random((T, T)).astype(np.float32) - 0.5
WARP = noise3(12.0, 4.4)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def gauss(x):
    return np.exp(-x * x)


def ridges(coord, spacing, sharp=3.0):
    """Fold crests every `spacing` (metres along coord), zero mean."""
    r = (1 - np.abs(np.sin(np.pi * coord / spacing))) ** sharp
    return r - 1.0 / (sharp + 1)


# ---------------------------------------------------------------- 6. shared height (mm), wear, dirt masks
hgt = np.zeros((T, T), np.float32)
fold = np.zeros((T, T), np.float32)
wear = np.zeros((T, T), np.float32)
cloth_m = ism("HCL_la_azul") | ism("HCL_la_vermelha") | ism("HCL_la_branca") | ism("HCL_la_cinza") | ism("HCL_polaina_preta")
if "HCL_la_dragona" in MID:                             # elite epaulettes (build_casaca_elite_fr.py)
    cloth_m |= ism("HCL_la_dragona")
leather = ism("HCL_couro_sapato"); sole = ism("HCL_sola"); metal = ism("HCL_latao")
gait = isp("polaina")
# fulled broadcloth: felted surface, faint nap, no weave
hgt += np.where(cloth_m, 0.035 * N_FIB + 0.02 * N_FINE, 0)
# borders: rolled edge, seam groove, hem allowance ridge (on cloth); edge of the leather on shoes
edge_roll = np.clip(1 - bdist / 0.0018, 0, 1) ** 2
hem_ridge = smooth(0.010, 0.013, bdist) * (1 - smooth(0.015, 0.019, bdist))
hgt += np.where(garment & cloth_m, -0.45 * edge_roll + 0.18 * hem_ridge, 0)
hgt += np.where(leather | sole, -0.30 * edge_roll, 0)
# coat piping: front closure (as v1), cuff flaps and shoulder straps (walls of the raised pieces, as v1)
coat = is_("casaco_corpo")
theta = np.arctan2(X, -(Y - 0.015))
q_pipe = np.abs(theta + 0.18) / 0.017
piping_front = coat & (q_pipe < 1) & (Y < -0.03) & (Hh > 1.10) & (Hh < 1.545)
hgt[piping_front] += (0.9 * np.sqrt(np.clip(1 - q_pipe ** 2, 0, 1)))[piping_front]


def wall_mask(part_mask, top_cos=0.6):
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


flap_pipe = {s: grow(wall_mask(is_(f"pala_{s}")), is_(f"pala_{s}"), 2) for s in "ED"}
strap_pipe = {s: grow(wall_mask(is_(f"platina_{s}")), is_(f"platina_{s}"), 2) for s in "ED"}
for s in "ED":
    hgt[flap_pipe[s]] += 0.5
    hgt[strap_pipe[s]] += 0.5


def seam(dist, depth=0.40, width=0.0009, allowance=1.0):
    """Seam line at dist == 0 (metres, signed): groove plus the pressed allowance on the positive side."""
    return -depth * gauss(dist / width) + 0.15 * allowance * smooth(0.0005, 0.0015, dist) * (1 - smooth(0.005, 0.008, dist))


# coat back: centre back seam and curved side-back seams
back = coat & (Y > 0.02)
hgt += np.where(back & (Hh > 1.09) & (Hh < 1.53), seam(X), 0)
xs_back = 0.058 + 0.060 * smooth(1.10, 1.44, Hh) ** 1.6
hgt += np.where(back & (Hh > 1.09) & (Hh < 1.44), seam(np.abs(X) - xs_back), 0)
# sleeves: two-piece sleeve, back seam (elbow line) and inner seam
for s in "ED":
    t, sa, phi, r = frame_coords(SLV[s])
    m_ = is_(f"manga_{s}")
    for ph0 in (2.55, -0.95):
        d_ = (np.angle(np.exp(1j * (phi - ph0)))) * r
        hgt += np.where(m_, seam(d_.astype(np.float32)), 0)
    # inner elbow folds (front side) and bunching above the cuff
    w_el = gauss((t - 0.50) / 0.11) * np.clip(np.cos(phi), 0, 1) ** 1.5
    fold += np.where(m_, 1.5 * w_el * (0.6 + 0.4 * N_MID) * ridges(sa + 0.012 * WARP + 0.006 * np.sin(phi * 2), 0.024), 0)
    w_wr = gauss((t - 0.86) / 0.07)
    fold += np.where(m_, 1.0 * w_wr * (0.6 + 0.4 * N_BIG) * ridges(sa + 0.008 * phi + 0.01 * WARP, 0.019), 0)
    # wear: back of the elbow, shine
    wear += np.where(m_, 0.7 * gauss((t - 0.50) / 0.08) * np.clip(-np.cos(phi), 0, 1) ** 2, 0)
    # armpit folds on the coat, front and back, radiating from below the shoulder end of the sleeve
    c, ax, smin, smax = SLV[s]
    pivot = (c + ax * smin).astype(np.float32) + np.array([0, 0, -0.07], np.float32)
    dv_ = pos - pivot
    dist_p = np.linalg.norm(dv_, axis=-1)
    psi = np.arctan2(dv_[..., 2], np.abs(dv_[..., 0]) + 1e-6)
    w_ap = smooth(0.02, 0.05, dist_p) * (1 - smooth(0.09, 0.15, dist_p)) * (np.abs(X) > 0.07)
    fold += np.where(coat, 1.0 * w_ap * (0.5 + 0.5 * N_MID) * ridges(psi + 0.15 * WARP, 0.28), 0)
# legs: outer and inner seams, back-of-knee folds, hip folds, knee wear, gaiter ankle folds
LEGF = {}
for s in "ED":
    out_ = np.array([1.0 if s == "E" else -1.0, 0, 0])
    t, sa, phi, r = frame_coords(LEG[s], side_ref=out_)
    LEGF[s] = (t, sa, phi, r)
    m_ = is_(f"calca_perna_{s}")
    for ph0 in (math.pi / 2, -math.pi / 2):
        d_ = (np.angle(np.exp(1j * (phi - ph0)))) * r
        hgt += np.where(m_, seam(d_.astype(np.float32)), 0)
    w_k = gauss((Hh - 0.555) / 0.045) * np.clip(-np.cos(phi), 0, 1) ** 1.2
    fold += np.where(m_, 1.4 * w_k * (0.6 + 0.4 * N_MID) * ridges(Hh + 0.01 * WARP + 0.004 * phi, 0.016), 0)
    w_h = smooth(0.74, 0.80, Hh) * (1 - smooth(0.90, 0.95, Hh)) * np.clip(np.cos(phi + 0.5), 0, 1)
    # hip folds: soft and irregular (2026-10-11; the regular sharp crests read as light scratches on the thighs)
    fold += np.where(m_, 0.55 * w_h * (0.35 + 0.65 * N_MID) * ridges(Hh - 0.5 * r * phi + 0.025 * WARP, 0.038, 1.6), 0)
    wear += np.where(m_, 0.55 * gauss((Hh - 0.52) / 0.05) * np.clip(np.cos(phi), 0, 1) ** 2, 0)
    g_ = is_(f"polaina_{s}")
    w_a = gauss((Hh - 0.15) / 0.05)
    fold += np.where(g_, 1.0 * w_a * (0.6 + 0.4 * N_MID) * ridges(Hh + 0.006 * phi + 0.008 * WARP, 0.014), 0)
    fold += np.where(g_, 0.35 * ridges(r * phi + 0.02 * WARP, 0.035) * (1 - smooth(0.2, 0.35, Hh)), 0)
# seat wear
wear += np.where(is_("calca_assento") & (Y > 0.03), 0.4, 0)
# tails: drape folds, stronger toward the hem
tails = isp("aba")
fold += np.where(tails, 0.6 * smooth(1.02, 0.80, Hh) * ridges(X + 0.4 * Y + 0.015 * WARP, 0.04, 2.0), 0)
# greatcoat skirt (build_capote_fr.py, parts "saia_*"): vertical drape folds deepening toward the hem (arc length
# around the body axis), a soft crease where the cloth breaks over the seat
saia = isp("saia")
if saia.any():
    arc_s = np.arctan2(X, -(Y - 0.02)) * np.hypot(X, Y - 0.02)
    fold += np.where(saia, (0.35 + 0.95 * smooth(1.05, 0.55, Hh)) * (0.7 + 0.3 * N_MID) * ridges(arc_s + 0.02 * WARP, 0.07, 2.0), 0)
    fold += np.where(saia, 0.35 * gauss((Hh - 0.86) / 0.05) * ridges(Hh + 0.01 * WARP + 0.2 * arc_s, 0.03, 2.0), 0)
# waist: small ripples where the coat is gathered
fold += np.where(coat, 0.4 * gauss((Hh - 1.10) / 0.035) * ridges(X * 0.6 + Y + 0.01 * WARP, 0.022, 2.0), 0)
# gaiters: buttoned flap edge along the line through the gaiter buttons, toward the front
bm2 = bmesh.new(); bm2.from_mesh(me)
PL2 = bm2.faces.layers.int.get("hcl_part")
seen, centres = set(), []
for f in bm2.faces:
    if f[PL2] != BTN or f.index in seen:
        continue
    stack, comp = [f], []
    seen.add(f.index)
    while stack:
        g = stack.pop(); comp.append(g)
        for v in g.verts:
            for h_ in v.link_faces:
                if h_.index not in seen and h_[PL2] == BTN:
                    seen.add(h_.index); stack.append(h_)
    vs = {v for g in comp for v in g.verts}
    centres.append(sum((v.co for v in vs), Vector()) / len(vs))
bm2.free()
# cuff-flap lace (Litzen; painted only for variants with "galoes"): one bar under each flap button, across the flap.
# Flap frame by PCA of its vertices: longest axis along the flap, second across it, smallest = thickness.
lace = np.zeros((T, T), np.float32)
lace_across = np.zeros((T, T), np.float32)
pa_ = me.attributes["hcl_part"].data
vco = np.array([v.co[:] for v in me.vertices], np.float64)
for s in "ED":
    pid_ = PID.get(f"pala_{s}")
    if pid_ is None:
        continue
    ids = sorted({i for poly in me.polygons if pa_[poly.index].value == pid_ for i in poly.vertices})
    Vf = vco[ids]
    cf = Vf.mean(axis=0)
    w_, vec_ = np.linalg.eigh(np.cov((Vf - cf).T))
    ax_l, ax_a, ax_t = vec_[:, 2], vec_[:, 1], vec_[:, 0]
    btn = [np.array(b[:]) for b in centres if np.min(np.linalg.norm(Vf - np.array(b[:]), axis=1)) < 0.012]
    region = is_(f"pala_{s}")
    for b in btn:
        d = pos - b.astype(np.float32)
        al, ac, th_ = d @ ax_l.astype(np.float32), d @ ax_a.astype(np.float32), d @ ax_t.astype(np.float32)
        bar = np.clip((0.0030 - np.abs(al)) / 0.0005, 0, 1) * np.clip((0.0115 - np.abs(ac)) / 0.0008, 0, 1) * (np.abs(th_) < 0.012)
        bar = np.where(region, bar, 0)
        take = bar > lace
        lace[take], lace_across[take] = bar[take], al[take]
    print(f"GALOES pala_{s}: {len(btn)} botoes na pala")
for s in "ED":
    sgn = 1 if s == "E" else -1
    bl = sorted([c for c in centres if c.z - GROUND < 0.62 and c.x * sgn > 0], key=lambda c: c.z)
    if len(bl) < 2:
        continue
    B = np.array([c[:] for c in bl], np.float32)
    g_ = is_(f"polaina_{s}")
    ys, xs = np.nonzero(g_)
    P = pos[ys, xs]
    best = np.full(len(ys), 1e9, np.float32); Q = np.zeros_like(P); D = np.zeros_like(P)
    for k in range(len(B) - 1):
        seg = B[k + 1] - B[k]
        tt = np.clip(((P - B[k]) @ seg) / (seg @ seg), 0, 1)
        q = B[k] + tt[:, None] * seg
        dd = np.linalg.norm(P - q, axis=1)
        take = dd < best
        best[take], Q[take], D[take] = dd[take], q[take], seg / np.linalg.norm(seg)
    nn = nrm[ys, xs]
    e = np.cross(nn, D); e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-9
    c, ax, smin, smax = LEG[s]
    fr_u = np.array([0, -1, 0], np.float32)
    e *= np.sign(e @ fr_u)[:, None]
    off = ((P - Q) * e).sum(axis=1)
    lip = 0.35 * np.exp(-((off - 0.010) / 0.0010) ** 2) - 0.25 * np.exp(-((off - 0.0118) / 0.0007) ** 2)
    lip *= (best < 0.03)
    hgt[ys, xs] += lip
    wear[ys, xs] += 0.4 * np.exp(-((off - 0.010) / 0.0012) ** 2) * (best < 0.03)
# shoes: welt stitches where the upper meets the sole, toe creases, scuffs
shoe_up = isp("sapato") & leather
ph = np.mod(balong, 0.0035) / 0.0035
stitch = shoe_up & bmat & (np.abs(bdist - 0.0032) < 0.0006) & (ph < 0.65)
hgt[shoe_up & bmat] += (-0.2 * gauss((bdist - 0.0032) / 0.0010))[shoe_up & bmat]
hgt[stitch] += 0.25
for s in "ED":
    sh = is_(f"sapato_{s}")
    if not sh.any():
        continue
    ytip = Y[sh].min()
    band = sh & leather & (nrm[..., 2] > 0.25)
    w_t = gauss((Y - ytip - 0.065) / 0.018)
    fold += np.where(band, 0.6 * w_t * ridges(Y + 0.25 * np.abs(X) + 0.004 * WARP, 0.0085, 2.5), 0)
    wear += np.where(sh & leather, 0.8 * gauss((Y - ytip) / 0.03), 0)
# buttons: shared corner square, domed with a rim
bu = (xx / T >= 0.948) & (1 - yy / T >= 0.948)
rr = np.hypot(xx / T - 0.9725, (1 - yy / T) - 0.9725) / 0.0225
dome = np.clip(1 - rr ** 2, 0, 1)
hgt[bu & metal] = (1.4 * dome + 0.15 * (np.abs(rr - 0.80) < 0.06))[bu & metal]
# elite epaulettes (build_casaca_elite_fr.py; areas in ob["hcl_dragona_uv"]): two-ply twist of the fringe cords, the
# under-curtain ribbed like the cords on it, quilting across the padded crescent, and the keeper (passant) across the
# tongue (= the shoulder strap) at 2/3 of its length toward the shoulder, as on the mod art (FranceINF c0 r3, c2 r3)
UU, VV = (xx + 0.5) / T, 1 - (yy + 0.5) / T
NOB = np.zeros((T, T), bool)
cord_m, curtain_m, cres_m, pal_m, keeper = NOB, NOB, NOB, NOB, NOB
cord_k = np.zeros((T, T), np.float32); twist = np.zeros((T, T), np.float32)
DRG = json.loads(ob["hcl_dragona_uv"]) if "hcl_dragona_uv" in ob.keys() else None
if DRG:
    RC_ = DRG["rects"]
    fr_m = isp("dragona_franja"); cres_m = isp("dragona_meialua"); pal_m = isp("dragona_corpo")
    cu0, cv0, cw_, cst = RC_["franja_cordoes"]
    cord_m = fr_m & (VV >= cv0 - 0.002)
    curtain_m = fr_m & ~cord_m
    cord_k = np.floor((UU - cu0) / cst)
    around = np.clip(((UU - cu0) - cord_k * cst) / cw_, 0, 1)
    along = (VV - cv0) / DRG["dens_c"]
    twist = np.cos(2 * np.pi * (along / 0.0070 + 2 * around + 0.37 * cord_k))
    hgt += np.where(cord_m, 0.40 * twist, 0)
    for s in "ED":
        u0k, v0k, wk, hk = RC_[f"franja_cortina_{s}"]
        cuk = (UU - u0k) / wk * (DRG["ncord"] - 1)
        hgt += np.where(curtain_m & (np.abs(UU - u0k - wk / 2) < wk / 2 + 0.002), 0.5 * np.cos(2 * np.pi * cuk), 0)
        u0m, v0m, wm, hm = RC_[f"meialua_{s}"]
        in_m = cres_m & (np.abs(UU - u0m - wm / 2) < wm / 2 + 0.002)
        hgt += np.where(in_m, 0.30 * ridges((UU - u0m) / DRG["dens"], 0.006, 2.0), 0)
    for s in "ED":
        pid_ = PID[f"platina_{s}"]
        ids = sorted({i for poly in me.polygons if me.attributes["hcl_part"].data[poly.index].value == pid_ for i in poly.vertices})
        Vp = np.array([me.vertices[i].co[:] for i in ids])
        lo_, hi_ = Vp[np.abs(Vp[:, 0]).argmin()], Vp[np.abs(Vp[:, 0]).argmax()]
        axp = (hi_ - lo_) / np.linalg.norm(hi_ - lo_)
        sf = ((pos - lo_.astype(np.float32)) @ axp.astype(np.float32)) / np.linalg.norm(hi_ - lo_)
        band = is_(f"platina_{s}") & (np.abs(sf - 0.66) < 0.05)
        keeper = keeper | band
        hgt[band] += (0.7 * smooth(0.05, 0.035, np.abs(sf - 0.66)))[band]
    print(f"DRAGONAS: cordoes {int(cord_m.sum())} texels, cortina {int(curtain_m.sum())}, meia-lua {int(cres_m.sum())}, "
          f"corpo {int(pal_m.sum())}, passante {int(keeper.sum())}")

# turnbacks seen from behind ("viras_externas" in a variant; French 1812 coat, mod tile M1 and FranceINF c0 r3 / c2 r3):
# on the OUTER face of each tail, two white wedges turned back from its vent edge and its front edge, narrow at the
# waist and meeting at the hem (the blue left between them is a triangle pointing down), piped along the fold; the
# elite ornament ("ornamento": granada | corneta, traced by tracar_ornamentos_fr.py) near the hem on each wedge
VIRAS_EXT = any(v.get("viras_externas") for v in VARIANTS.values())
tail_out = ism("HCL_la_azul") & isp("aba")
wedge = NOB.copy(); wedge_edge = np.full((T, T), -1.0, np.float32); orn_uv = {}
wedge_a = pipe_a = np.zeros((T, T), np.float32)
if VIRAS_EXT and tail_out.any():
    PHI = np.arctan2(np.abs(X), Y - 0.02)
    ARC = PHI * np.hypot(X, Y - 0.02)
    hb = np.round(Hh / 0.005).astype(np.int32)
    q_ = np.zeros((T, T), np.float32)
    hem_of = {}
    for s, sg in (("E", 1), ("D", -1)):
        m_ = tail_out & (np.sign(X) == sg)
        ys, xs = np.nonzero(m_)
        bins = hb[ys, xs]; ph = PHI[ys, xs]
        ub = np.unique(bins)
        lo_b = np.array([np.percentile(ph[bins == b], 1) for b in ub])
        hi_b = np.array([np.percentile(ph[bins == b], 99) for b in ub])
        # smooth over 7 bins and interpolate at each texel's own height (per-bin steps made the fold line saw-toothed)
        ker = np.ones(7) / 7
        pad = lambda arr: np.concatenate([np.full(3, arr[0]), arr, np.full(3, arr[-1])])
        lo_s, hi_s = np.convolve(pad(lo_b), ker, "valid"), np.convolve(pad(hi_b), ker, "valid")
        hq = Hh[ys, xs] / 0.005
        lo_a, hi_a = np.interp(hq, ub, lo_s), np.interp(hq, ub, hi_s)
        q_[ys, xs] = np.clip((ph - lo_a) / np.maximum(hi_a - lo_a, 1e-3), 0, 1)
        hem_of[s] = float(Hh[ys, xs].min())
    h_top, h_hem = 1.125, min(hem_of.values())
    w_ = 0.5 * np.clip((h_top - Hh) / (h_top - h_hem), 0, 1)
    d_in, d_out = w_ - q_, q_ - (1 - w_)                 # > 0 inside the vent / the front wedge
    wedge = tail_out & ((d_in > 0) | (d_out > 0))
    # signed distance to the fold line in metres (q is a fraction of the tail's girth at that height, ~0.21 m); the
    # edges are blended over ~1 mm (hard masks were saw-toothed at 0.8 texel/mm)
    wedge_edge = np.where(tail_out, np.maximum(d_in, d_out) * 0.21, -1.0).astype(np.float32)
    wedge_a = smooth(-0.0006, 0.0006, wedge_edge) * tail_out
    pipe_a = gauss((wedge_edge - 0.0013) / 0.0009) * (wedge_edge > -0.0006) * tail_out
    hgt += 0.35 * wedge_a + 0.30 * pipe_a                                                     # a layer of cloth, rolled fold
    hgt += np.where(tail_out, -0.25 * gauss((wedge_edge + 0.0010) / 0.0008), 0)              # its shadow line
    for s, sg in (("E", 1), ("D", -1)):
        m_ = tail_out & (np.sign(X) == sg)
        for qc in (0.25, 0.75):
            near = m_ & (np.abs(q_ - qc) < 0.04)
            if not near.any():
                continue
            hc = float(Hh[near].min()) + 0.040
            ac = float(np.median(ARC[near & (np.abs(Hh - hc) < 0.01)])) if (near & (np.abs(Hh - hc) < 0.01)).any() else float(np.median(ARC[near]))
            orn_uv[(s, qc)] = (ac, hc, sg)
    print(f"VIRAS EXTERNAS: {int(wedge.sum())} texels de viradas nas abas; ornamentos em " +
          ", ".join(f"{s} q {qc:.2f} (h {v[1]:.3f} m)" for (s, qc), v in orn_uv.items()))
ORN = {}
for nm in {n for v in VARIANTS.values() if v.get("ornamento") for n in v["ornamento"].split("+")}:
    img_ = bpy.data.images.load(os.path.join(os.path.dirname(os.path.abspath(a[1])), "ornamentos", nm + ".png"))
    S_ = img_.size[0]
    ORN[nm] = np.array(img_.pixels[:], np.float32).reshape(S_, S_, 4)          # row 0 = bottom (v up)


def stamp(nm, size=0.046):
    """Alpha and detail of ornament `nm` on every wedge (mirrored on the right tail). `nm` = "a+b" alternates: a on
    the vent-side wedge, b on the front wedge of each tail (Old Guard: eagle and grenade, 2026-10-12)."""
    al = np.zeros((T, T), np.float32); de = np.zeros((T, T), np.float32)
    names = nm.split("+")
    if any(n not in ORN for n in names) or not orn_uv:
        return al, de
    for (s, qc), (ac, hc, sg) in orn_uv.items():
        O_ = ORN[names[0] if qc < 0.5 else names[-1]]; S_ = O_.shape[0]
        u_ = (ARC - ac) / size + 0.5
        v_ = (Hh - hc) / size + 0.5
        if sg < 0:
            u_ = 1 - u_
        ok = tail_out & (np.sign(X) == sg) & (u_ >= 0) & (u_ < 1) & (v_ >= 0) & (v_ < 1)
        iu = np.clip((u_ * S_).astype(int), 0, S_ - 1); iv = np.clip((v_ * S_).astype(int), 0, S_ - 1)
        al[ok] = np.maximum(al[ok], O_[iv[ok], iu[ok], 3]); de[ok] = O_[iv[ok], iu[ok], 0]
    return al, de


# combine folds; edges of pieces get wear shine; mud and dust
fold *= 1.4
hgt += fold
wear += np.where(garment & cloth_m, 0.6 * np.clip(1 - bdist / 0.003, 0, 1) * (isp("punho") | coat | isp("aba") | is_("gola")), 0)
wear = np.clip(wear * (0.7 + 0.3 * N_MID), 0, 1)
mud_d = np.clip((0.50 - Hh) / 0.45, 0, 1) ** 1.6
specks = np.clip((noise3(520.0, 8.8) - (0.88 - 0.22 * mud_d)) * 5, 0, 1) * (mud_d > 0)
blots = np.clip((noise3(45.0, 2.2) - 0.45 + 0.25 * mud_d) * 2.0, 0, 1) * smooth(0.22, 0.06, Hh)
mud = 0.7 * np.clip(np.maximum(specks, blots * 0.7), 0, 1) * (isp("calca_perna") | gait | isp("sapato"))
dust = np.where(gait, 0.18 * np.clip(nrm[..., 2], 0, 1) * smooth(0.0, 0.6, mud_d + 0.2), 0)
dust += np.where(isp("sapato"), 0.10 * np.clip(nrm[..., 2], 0, 1), 0)
dust += np.where(isp("calca_perna"), 0.25 * gauss((Hh - 0.52) / 0.05) * np.clip(-nrm[..., 1], 0, 1), 0)   # knees
dust += np.where(tails, 0.15 * smooth(0.85, 0.70, Hh), 0)
if saia.any():                                          # greatcoat hem: road dust, splashes and a worn edge
    dust += np.where(saia, 0.25 * smooth(0.80, 0.47, Hh), 0)
    mud = np.maximum(mud, 0.6 * np.clip(np.maximum(specks, blots * 0.5), 0, 1) * saia * smooth(0.62, 0.47, Hh))
    wear = np.clip(wear + np.where(saia & (bdist < 0.006) & (Hh < 0.55), 0.5, 0), 0, 1)
grime = np.where(isp("punho") & (bdist < 0.010), 0.25, 0) + np.where(is_("gola") & (Hh > 1.53), 0.20, 0)
sun = np.where(cloth_m & (Hh > 1.15), np.clip(nrm[..., 2], 0, 1) ** 2, 0)
cav = np.clip(fold / 1.6, -1, 1)
AOg = np.where(garment, AO, 1.0)
AOg[bu] = 1.0
shade = (0.38 + 0.62 * AOg) * (1 + 0.18 * cav) * (1 - 0.12 * edge_roll * garment)
print(f"AO mean on garment texels {AO[garment & covered].mean():.3f}")


# ---------------------------------------------------------------- 7. colour per variant
def wool(rgb, mottle=1.0):
    base = np.array(rgb, np.float32)
    v = 1 + mottle * (0.06 * N_BIG + 0.035 * N_MID) + 0.03 * N_FIB + 0.015 * PIX
    return base[None, None, :] * v[..., None]


def paint_variant(v):
    col = np.zeros((T, T, 3), np.float32)
    C = {k: np.array(c, np.float32) for k, c in v["cores"].items()}
    azul = ism("HCL_la_azul"); verm = ism("HCL_la_vermelha"); bran = ism("HCL_la_branca"); cinza = ism("HCL_la_cinza")
    col[azul] = wool(C["casaca"])[azul]
    gola = verm & is_("gola"); punho = verm & isp("punho"); abas = verm & isp("aba")
    col[gola] = wool(C["gola"])[gola]
    col[punho] = wool(C.get("punho", C["gola"]))[punho]
    col[abas] = wool(C["viras"])[abas]
    # optional piping along the borders of collar, cuffs and turnbacks (2.5 mm band at the piece's edges)
    for key, m_ in (("gola_debrum", gola), ("punho_debrum", punho), ("viras_debrum", abas)):
        if key in C:
            band = m_ & (bdist < 0.0025)
            col[band] = wool(C[key], 0.5)[band]
    lap = verm & isp("lapela")                          # French lapels (piping band wider: the border is the foot
    if lap.any():                                       # of the 3 mm walls)
        col[lap] = wool(C.get("lapela", C["gola"]))[lap]
        if "lapela_debrum" in C:
            band = lap & (bdist < 0.0055)
            col[band] = wool(C["lapela_debrum"], 0.5)[band]
    if "pala" in C:
        pm = isp("pala") & azul
        col[pm] = wool(C["pala"])[pm]
    col[piping_front] = wool(C["debrum"], 0.5)[piping_front]
    for s in "ED":
        col[flap_pipe[s]] = wool(C["debrum"], 0.5)[flap_pipe[s]]
        top = bran & is_(f"platina_{s}")
        col[top] = wool(C["platina"], 0.6)[top]
        col[strap_pipe[s]] = wool(C["platina_borda"], 0.5)[strap_pipe[s]]
    if DRG and "dragona" in C:                          # elite epaulettes
        dc = C["dragona"]
        col[pal_m] = wool(dc)[pal_m]
        if "dragona_borda" in C:
            bb = pal_m & (bdist < 0.0035)
            col[bb] = wool(C["dragona_borda"], 0.5)[bb]
        var = (0.86 + 0.28 * np.mod(cord_k * 0.618, 1.0))[..., None]          # each cord its own shade of wool
        cc = wool(dc, 1.4) * var * (0.80 + 0.20 * (twist[..., None] + 1) / 2)
        col[cord_m] = cc[cord_m]
        col[curtain_m] = (wool(dc) * 0.62)[curtain_m]
        col[cres_m] = wool(C.get("dragona_meialua", dc))[cres_m]
        if "dragona_passante" in C:
            col[keeper] = wool(C["dragona_passante"], 0.5)[keeper]
    if v.get("viras_externas") and wedge.any():         # turnbacks seen from behind, piped along the fold
        col = col * (1 - wedge_a[..., None]) + wool(C["viras"]) * wedge_a[..., None]
        if "viras_debrum" in C:
            pa_ = np.clip(pipe_a + wedge_a * smooth(0.0030, 0.0020, bdist), 0, 1)[..., None]
            col = col * (1 - pa_) + wool(C["viras_debrum"], 0.5) * pa_
        if v.get("ornamento"):
            al, de = stamp(v["ornamento"])
            oc = np.array(C.get("ornamento_cor", C["debrum"]), np.float32)[None, None, :] * (0.62 + 0.45 * de[..., None])
            al = np.where(wedge, al, 0)[..., None]
            col = col * (1 - al) + oc * al
    col[cinza] = wool(C["calca"], 1.3)[cinza]
    col[gait] = wool(C["polaina"], 1.6)[gait]
    shoe = np.array(C["sapato"], np.float32)[None, None, :] * (1 + 0.20 * N_MID[..., None] + 0.08 * PIX[..., None])
    col[leather] = shoe[leather]
    col[sole] = wool(C["sola"], 2.0)[sole]
    m_rgb = np.array(C["botoes"], np.float32)
    bt = m_rgb[None, None, :] * (0.78 + 0.30 * np.clip(dome, 0, 1))[..., None]
    bt *= (1 - 0.25 * (np.abs(rr - 0.80) < 0.07))[..., None]
    col[metal] = bt[metal]
    if "galoes" in C:                                   # woven lace bars: rib across the bar, darker edges
        rib = 0.88 + 0.12 * (np.mod(lace_across / 0.0008, 1.0) < 0.5)
        lc = np.array(C["galoes"], np.float32)[None, None, :] * rib[..., None]
        lc *= (0.75 + 0.25 * np.clip(lace * 1.2, 0, 1))[..., None]
        col = col * (1 - lace[..., None]) + lc * lace[..., None]
    # sun fading (lighter, slightly greyer), wear (shine and lighter nap), grime, dust, mud
    grey = col.mean(axis=2, keepdims=True)
    col = col * (1 + 0.10 * sun[..., None]) + (grey - col) * (0.12 * sun[..., None])
    col = col * (1 + 0.14 * wear[..., None] * cloth_m[..., None])
    col = np.where((leather & (wear > 0))[..., None], col + 0.03 * wear[..., None], col)        # scuffed toes
    col = col * (1 - 0.25 * grime[..., None])
    dust_c = np.array([0.46, 0.42, 0.35], np.float32)
    col = col * (1 - dust[..., None]) + dust_c * dust[..., None]
    mud_c = np.array([0.34, 0.29, 0.21], np.float32) * (1 + 0.15 * N_MID[..., None])
    col = col * (1 - 0.85 * mud[..., None]) + mud_c * (0.85 * mud[..., None])
    col = np.where(stitch[..., None], np.array([0.12, 0.10, 0.08], np.float32), col)
    col = col * shade[..., None]
    return np.clip(col, 0, 1)


# ---------------------------------------------------------------- 8. shared maps
def normal_map(h, isl, mm_per_px):
    def diff(axis):
        hp, hm = np.roll(h, -1, axis), np.roll(h, 1, axis)
        ip, im = np.roll(isl, -1, axis), np.roll(isl, 1, axis)
        okp, okm = ip == isl, im == isl
        d = np.where(okp & okm, (hp - hm) / 2, np.where(okp, hp - h, np.where(okm, h - hm, 0.0)))
        return d / mm_per_px
    gx, gy = diff(1), diff(0)
    n = np.dstack([-gx, gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n * 0.5 + 0.5


def save(arr, name):
    img = bpy.data.images.new(name, T, T, alpha=False)
    rgba = np.concatenate([np.clip(arr, 0, 1)[::-1], np.ones((T, T, 1), np.float32)], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = "PNG"
    p = os.path.join(OUT_DIR, name)
    img.filepath_raw = p
    img.save()
    print("OK", p)


for vid, v in VARIANTS.items():
    if ONLY and vid not in ONLY:
        continue
    save(paint_variant(v), f"{v['prefixo']}_co.png")
if MAPS:
    spec = np.full((T, T), 0.05, np.float32)
    gloss = np.full((T, T), 0.14, np.float32)
    spec = np.where(cloth_m, 0.05 + 0.07 * wear, spec)
    gloss = np.where(cloth_m, 0.14 + 0.16 * wear, gloss)
    spec = np.where(gait, 0.07 + 0.05 * wear, spec)
    spec = np.where(leather, 0.42 - 0.20 * np.clip(dust * 2, 0, 1) + 0.10 * wear, spec)
    gloss = np.where(leather, 0.62 - 0.25 * np.clip(dust * 2, 0, 1) - 0.15 * np.clip(-cav, 0, 1), gloss)
    spec = np.where(sole, 0.10, spec); gloss = np.where(sole, 0.22, gloss)
    spec = np.where(metal, 0.88, spec); gloss = np.where(metal, 0.78, gloss)
    spec = spec * (1 - 0.8 * mud); gloss = gloss * (1 - 0.6 * mud)
    save(normal_map(hgt, isl_id, 1000.0 / 800.0), f"{MAPAS}_nohq.png")
    save(np.dstack([np.ones_like(spec), np.clip(spec, 0, 1), np.clip(gloss, 0, 1)]), f"{MAPAS}_smdi.png")
    save(np.dstack([AOg, AOg, AOg]), f"{MAPAS}_ao_bake.png")
