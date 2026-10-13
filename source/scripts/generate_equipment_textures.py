# Phase 6 (equipment): paints the texture sets of the vest (correame) and the knapsack (tornister) from their production
# meshes (build_equipamento_producao.py). For every texel the UV triangles give the material, part, side (outer face /
# edge / underside), the local coordinates along and across each strap, tube and flap, the 3D position and the normal;
# an ambient-occlusion bake (Cycles, with the uniform as occluder, the other item hidden) gives contact shadows.
# Materials: pipeclayed buff leather (clay streaks, worn edges, creases, tongue holes), blackened leather (grain, worn
# edges, stitched flap border and seams, holes), brass (polish, tarnish in recesses, scratches), iron (socket with its
# slot), hair-on calfskin (directional hair, leather edging with stitches), grey wool greatcoat roll (folds, the outer
# layer's edge, spiral ends). Heights are painted in millimetres and turned into an OpenGL normal map with the real
# texel size; gradients never cross UV islands.
#   blender -b <equipment LOD0 .blend> --python generate_equipment_textures.py -- <out dir> [ao_samples=N] [only=vest|pack]
# Outputs (2048 PNG, sources for ImageToPAA): hcl_v_pruss1813_correame_{co,nohq,smdi}.png, hcl_b_pruss1813_tornister_...
import bpy, bmesh, sys, os, math, json
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
OUT_DIR = a[0]
OPT = dict(x.split("=", 1) for x in a[1:] if "=" in x)
T = 2048
BLACK_SET = OPT.get("couro") == "preto"                 # couro=preto: black-leather set, files named <prefix>_preto_*
SUFFIX = "_preto" if BLACK_SET else ""
os.makedirs(OUT_DIR, exist_ok=True)
GROUND = -1.0069
FR_SET = OPT.get("nacao") == "fr"                      # nacao=fr: French crossbelts + havresac (build_equipamento_producao)
ITEMS = [("vest", "HCL_V_Pruss1813_Correame_LOD0", "hcl_v_pruss1813_correame"),
         ("pack", "HCL_B_Pruss1813_Tornister_LOD0", "hcl_b_pruss1813_tornister")]
if FR_SET:
    ITEMS = [("vest", "HCL_V_Fr1812_Correame_LOD0", "hcl_v_fr1812_correame"),
             ("pack", "HCL_B_Fr1812_Havresac_LOD0", "hcl_b_fr1812_havresac")]
BRANCO, LATAO, PRETO, BEZERRO, CAPOTE, FERRO = range(6)
TOP, EDGE, UNDER = 0, 1, 2
scene = bpy.context.scene


# ---------------------------------------------------------------- ambient occlusion bake (uniform as occluder)
def bake_ao(ob, others, samples):
    img = bpy.data.images.new(f"AO_{ob.name}", T, T, alpha=False)
    mat = bpy.data.materials.new(f"BAKE_{ob.name}")
    mat.use_nodes = True
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = img
    mat.node_tree.nodes.active = node
    saved = [(s.link, s.material) for s in ob.material_slots]
    for s in ob.material_slots:
        s.link = "OBJECT"
        s.material = mat
    for o in others:
        o.hide_render = True
    if scene.world is None:
        scene.world = bpy.data.worlds.new("AO_mundo")
    scene.world.light_settings.distance = 0.05
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.bake(type="AO", margin=8, use_clear=True)
    px = np.array(img.pixels[:], np.float32).reshape(T, T, 4)[::-1, :, 0].copy()
    for s, (lk, m) in zip(ob.material_slots, saved):
        s.link = lk
        s.material = m
    for o in others:
        o.hide_render = False
    return px


# ---------------------------------------------------------------- rasterise per-texel attributes
def rasterise(ob):
    me = ob.data
    me.calc_loop_triangles()
    uv = me.uv_layers["UVMap"].data
    lc = me.uv_layers["local"].data
    pa = me.attributes["hcl_part"].data
    ka = me.attributes["hcl_lado"].data
    # UV islands: faces joined through edges whose two loops carry the same UVs
    bm = bmesh.new()
    bm.from_mesh(me)
    uvl = bm.loops.layers.uv["UVMap"]
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
        def uv_at(l, v):
            return l[uvl].uv if l.vert == v else l.link_loop_next[uvl].uv
        ok = all((uv_at(la, v) - uv_at(lb, v)).length < 1e-6 for v in e.verts)
        if ok:
            ra, rb = find(la.face.index), find(lb.face.index)
            parent[ra] = rb
    island = [find(i) for i in range(len(bm.faces))]
    bm.free()
    D = {k: np.full((T, T), -1, np.int32) for k in ("mat", "part", "kind", "isl")}
    pos = np.zeros((T, T, 3), np.float32)
    nrm = np.zeros((T, T, 3), np.float32)
    loc = np.zeros((T, T, 2), np.float32)
    for t in me.loop_triangles:
        P2 = [(uv[li].uv.x * T - 0.5, (1 - uv[li].uv.y) * T - 0.5) for li in t.loops]
        P3 = [me.vertices[vi].co for vi in t.vertices]
        L2 = [lc[li].uv for li in t.loops]
        N3 = [t.split_normals[k] for k in range(3)]
        (x0, y0), (x1, y1), (x2, y2) = P2
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
        ins = (w0 >= -0.03) & (w1 >= -0.03) & (w2 >= -0.03)
        if not ins.any():
            continue
        yy, xx = gy[ins].astype(int), gx[ins].astype(int)
        W = (w0[ins], w1[ins], w2[ins])
        p = t.polygon_index
        D["mat"][yy, xx] = me.polygons[p].material_index
        D["part"][yy, xx] = pa[p].value
        D["kind"][yy, xx] = ka[p].value
        D["isl"][yy, xx] = island[p]
        for d in range(3):
            pos[yy, xx, d] = W[0] * P3[0][d] + W[1] * P3[1][d] + W[2] * P3[2][d]
            nrm[yy, xx, d] = W[0] * N3[0][d] + W[1] * N3[1][d] + W[2] * N3[2][d]
        for d in range(2):
            loc[yy, xx, d] = W[0] * L2[0][d] + W[1] * L2[1][d] + W[2] * L2[2][d]
    covered = D["mat"] >= 0
    for _ in range(10):                                             # dilate into the gutters between islands
        empty = D["mat"] < 0
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            src = np.roll(D["mat"], (dy, dx), axis=(0, 1)) >= 0
            take = empty & src
            for k in D:
                D[k][take] = np.roll(D[k], (dy, dx), axis=(0, 1))[take]
            pos[take] = np.roll(pos, (dy, dx), axis=(0, 1))[take]
            nrm[take] = np.roll(nrm, (dy, dx), axis=(0, 1))[take]
            loc[take] = np.roll(loc, (dy, dx), axis=(0, 1))[take]
            empty = D["mat"] < 0
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True) + 1e-9
    return D, pos, nrm, loc, covered


# ---------------------------------------------------------------- noise
rng = np.random.default_rng(1813)
LAT3 = rng.random((64, 64, 64)).astype(np.float32)
LAT2 = rng.random((256, 256)).astype(np.float32)


def noise3(P, scale, off=0.0):
    p = P * scale + off
    i = np.floor(p).astype(np.int64); f = p - i
    f = f * f * (3 - 2 * f)
    i0, i1 = i % 64, (i + 1) % 64
    g = lambda ix, iy, iz: LAT3[ix[..., 0], iy[..., 1], iz[..., 2]]
    fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
    x00 = g(i0, i0, i0) * (1 - fx) + g(i1, i0, i0) * fx
    x10 = g(i0, i1, i0) * (1 - fx) + g(i1, i1, i0) * fx
    x01 = g(i0, i0, i1) * (1 - fx) + g(i1, i0, i1) * fx
    x11 = g(i0, i1, i1) * (1 - fx) + g(i1, i1, i1) * fx
    return ((x00 * (1 - fy) + x10 * fy) * (1 - fz) + (x01 * (1 - fy) + x11 * fy) * fz) * 2 - 1


def noise2(u, v, su, sv, off=0.0):
    x, y = u * su + off, v * sv + off * 0.37
    i, j = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - i, y - j
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    i0, i1, j0, j1 = i % 256, (i + 1) % 256, j % 256, (j + 1) % 256
    a_ = LAT2[i0, j0] * (1 - fx) + LAT2[i1, j0] * fx
    b_ = LAT2[i0, j1] * (1 - fx) + LAT2[i1, j1] * fx
    return (a_ * (1 - fy) + b_ * fy) * 2 - 1


def fbm3(P, scale, octaves=4, off=0.0):
    out, amp, tot = 0.0, 1.0, 0.0
    for k in range(octaves):
        out = out + amp * noise3(P, scale * 2 ** k, off + 3.7 * k)
        tot += amp
        amp *= 0.5
    return out / tot


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def stitches(along, across, row, pitch=0.0035, length=0.0024, width=0.0007):
    """Height (mm) of a stitch row at `across` == row: raised thread segments every `pitch` metres along `along`."""
    ph = np.mod(along, pitch) / pitch
    on = (ph < length / pitch).astype(np.float32)
    prof = np.clip(1 - ((across - row) / (width / 2)) ** 2, 0, 1)
    channel = np.clip(1 - ((across - row) / (width * 1.6)) ** 2, 0, 1)
    end = np.clip(1 - np.abs(ph - length / pitch / 2) / (length / pitch / 2), 0, 1) ** 0.3
    return 0.22 * prof * on * end - 0.12 * channel, prof * on


def disc(u, v, cu, cv, r):
    return np.clip(1 - np.hypot(u - cu, v - cv) / r, 0, 1)


# ---------------------------------------------------------------- painting
def paint(ob, ao, D, pos, nrm, loc, key):
    parts = ob["hcl_partes"].split(",")
    FR = json.loads(ob["hcl_frames"])
    PID = {n: i for i, n in enumerate(parts)}
    mat, part, kind = D["mat"], D["part"], D["kind"]
    if BLACK_SET:                                       # black-leather set: every buff-leather piece becomes blackened
        mat = np.where(mat == BRANCO, PRETO, mat)
    isp = lambda *names: np.isin(part, [PID[n] for n in names if n in PID])
    s, x = loc[..., 0], loc[..., 1]
    col = np.zeros((T, T, 3), np.float32)
    hgt = np.zeros((T, T), np.float32)                              # millimetres
    spec = np.full((T, T), 0.1, np.float32)
    gloss = np.full((T, T), 0.2, np.float32)
    up = np.clip(nrm[..., 2], 0, 1)
    N_big = fbm3(pos, 9.0, 3)
    N_mid = fbm3(pos, 60.0, 3, 5.1)
    N_fine = noise3(pos, 900.0, 2.3)
    occ = 0.30 + 0.70 * ao

    # ---------- pipeclayed buff leather (white)
    m = mat == BRANCO
    if m.any():
        streak = noise2(s, x, 14.0, 260.0, 11.0)                             # soft brush marks along the strap
        smudge = fbm3(pos, 22.0, 3, 6.0)
        clay = 0.5 + 0.5 * (0.30 * streak + 0.45 * N_mid + 0.25 * smudge)
        base = np.array([0.85, 0.84, 0.79], np.float32)
        fresh = np.array([0.91, 0.90, 0.86], np.float32)
        worn = np.array([0.73, 0.70, 0.62], np.float32)
        c = base + (fresh - base) * np.clip(clay - 0.5, 0, 1)[..., None] * 1.6 \
            - (base - worn) * np.clip(0.45 - clay, 0, 1)[..., None] * 1.8
        # strap width from the section coordinate: edge proximity on the outer face
        half = np.zeros_like(s)
        for nm_, w in (("cinturao", 0.050), ("cinturao_ponta", 0.050), ("bandoleira_frente", 0.060),
                       ("bandoleira_costas", 0.060), ("boldrie_frente", 0.060), ("boldrie_costas", 0.060),
                       ("capote_correia", 0.024), ("correia_ombro_E", 0.045),
                       ("correia_ombro_D", 0.045), ("correia_ombro_E_ponta", 0.045), ("correia_ombro_D_ponta", 0.045),
                       ("passante", 0.053), ("passador", 0.054)):
            if nm_ in PID:
                half[part == PID[nm_]] = w / 2
        edge = np.where(half > 0, np.clip(1 - (half - np.abs(x)) / 0.004, 0, 1), 0)
        c = c * (1 - 0.10 * edge[..., None])
        leather_edge = np.array([0.66, 0.58, 0.45], np.float32)            # bare leather where the clay rubbed off
        e_ = (kind == EDGE) & m
        c[e_] = c[e_] * 0.45 + leather_edge * 0.55
        u_ = (kind == UNDER) & m
        c[u_] = np.array([0.62, 0.57, 0.48], np.float32) * (1 + 0.08 * N_mid[u_, None])
        dirt = np.clip(0.6 - ao, 0, 1) * 0.5 + 0.10 * np.clip(smudge, 0, 1) + 0.05 * np.clip(N_big, 0, 1)
        c = c * (1 - dirt[..., None] * 0.35) + np.array([0.40, 0.36, 0.30], np.float32) * (dirt[..., None] * 0.35)
        col[m] = (c * occ[..., None])[m]
        h = 0.03 * N_fine + 0.02 * streak * (kind == TOP)
        h -= 0.35 * edge ** 2
        cn = noise2(s + 0.12 * x, np.zeros_like(s), 45.0, 1.0, 4.0)                     # transverse creases
        crease = np.clip(0.06 - np.abs(cn), 0, 1) / 0.06 * np.clip(0.5 + noise2(s, x, 8.0, 40.0, 9.0), 0, 1)
        h -= 0.18 * crease
        hgt[m] = h[m]
        spec[m], gloss[m] = 0.06, 0.16
        spec[e_], gloss[e_] = 0.12, 0.30
        # tongue holes in the belt tip and in the shoulder-strap tips
        for nm_, holes in (("cinturao_ponta", (0.030, 0.088, 0.102)), ("correia_ombro_E_ponta", (0.052, 0.064)),
                           ("correia_ombro_D_ponta", (0.052, 0.064))):
            if nm_ not in PID:
                continue
            mm = (part == PID[nm_]) & (kind == TOP)
            for sh in holes:
                dd = disc(s, x, sh, 0.0, 0.0024)
                hole = mm & (dd > 0)
                col[hole] = (col[hole] * (1 - dd[hole, None]) + np.array([0.06, 0.05, 0.04]) * dd[hole, None])
                hgt[hole] -= 1.2 * np.clip(dd[hole] * 3, 0, 1)
                ring = mm & (disc(s, x, sh, 0.0, 0.0034) > 0) & (dd == 0)
                hgt[ring] += 0.15

    # ---------- blackened leather
    m = mat == PRETO
    if m.any():
        grain = 0.5 + 0.5 * noise3(pos, 700.0, 1.7)
        base = np.array([0.032, 0.029, 0.026], np.float32)
        c = base[None, None, :] * (1 + 0.25 * N_mid[..., None] + 0.15 * grain[..., None])
        wear = np.zeros((T, T), np.float32)
        brown = np.array([0.13, 0.085, 0.05], np.float32)
        h = 0.05 * grain + 0.02 * N_fine
        stitch_h = np.zeros((T, T), np.float32)
        stitch_on = np.zeros((T, T), np.float32)
        # box-like bodies: edges (two strong normal components in the box frame) are seams; edge wear on them
        for nm_ in ("cartucheira_corpo", "mochila_corpo"):
            if nm_ not in FR:
                continue
            f = FR[nm_]
            mm = m & (part == PID[nm_])
            ax_ = [np.array(f[k], np.float32) for k in ("x", "y", "z")]
            nl = np.stack([nrm @ v for v in ax_], axis=-1)
            pl = np.stack([(pos - np.array(f["c"], np.float32)) @ v for v in ax_], axis=-1)
            an = np.sort(np.abs(nl), axis=-1)
            edge_w = smooth(0.25, 0.65, an[..., 1])                        # second largest component: on a rounded edge
            wear += np.where(mm, edge_w * (0.5 + 0.5 * np.clip(N_mid + 0.3, 0, 1)), 0)
            # welt along the edge middle (45 degrees) and stitches beside it
            welt = np.clip(1 - np.abs(an[..., 2] - an[..., 1]) / 0.10, 0, 1) * (an[..., 1] > 0.45)
            h += np.where(mm, 0.35 * welt, 0)
            third = np.argmin(np.abs(nl), axis=-1)
            along = np.take_along_axis(pl, third[..., None], axis=-1)[..., 0]
            st, on = stitches(along, an[..., 2] - an[..., 1], 0.28, pitch=0.004, length=0.0028, width=0.08)
            stitch_h += np.where(mm & (an[..., 1] > 0.3), st * 0.8, 0)
            stitch_on += np.where(mm & (an[..., 1] > 0.3), on, 0)
        # flap of the cartridge box: stitched border 4 mm in from the outline
        for nm_ in ("cartucheira_tampa",):
            if nm_ not in FR:
                continue
            f = FR[nm_]
            mm = m & (part == PID[nm_]) & (kind == TOP)
            W, Dd, Rc = f["W"], f["D"], f["Rc"]
            xx, dd = s, x
            ax_ = np.abs(xx)
            cx, cd = W / 2 - Rc, Dd - Rc
            corner = (ax_ > cx) & (dd > cd)
            dist = np.minimum.reduce([dd, W / 2 - ax_, Dd - dd])
            dist = np.where(corner, Rc - np.hypot(ax_ - cx, dd - cd), dist)
            along = np.where(np.minimum(W / 2 - ax_, Dd - dd) < dd, np.where(W / 2 - ax_ < Dd - dd, dd, xx), xx)
            along = np.where(corner, np.arctan2(dd - cd, ax_ - cx) * Rc, along)
            st, on = stitches(along, dist, 0.004)
            stitch_h += np.where(mm, st, 0)
            stitch_on += np.where(mm, on, 0)
            h += np.where(mm, -0.25 * np.clip(1 - dist / 0.0015, 0, 1), 0)      # rounded, burnished edge
            wear += np.where(mm, np.clip(1 - dist / 0.003, 0, 1) * 0.8, 0)
            em = m & (part == PID[nm_]) & (kind == EDGE)
            wear += np.where(em, 0.9, 0)
        # narrow black straps: stitched along both edges, holes for the tongue
        for nm_, w, holes in (("mochila_correia_fecho", 0.024, (0.050, 0.060, 0.070)), ("mochila_presilha", 0.026, ()),
                              ("cartucheira_presilha", 0.022, (0.050,)),
                              # pieces that are black only in the black-leather set: holes, no edge stitching
                              ("cinturao_ponta", 0.0, (0.030, 0.088, 0.102)), ("correia_ombro_E_ponta", 0.0, (0.052, 0.064)),
                              ("correia_ombro_D_ponta", 0.0, (0.052, 0.064))):
            if nm_ not in PID:
                continue
            mm = m & (part == PID[nm_]) & (kind == TOP)
            for side_ in ((-1, 1) if w > 0 else ()):
                st, on = stitches(s, x * side_, w / 2 - 0.0028)
                stitch_h += np.where(mm, st, 0)
                stitch_on += np.where(mm, on, 0)
            wear += np.where(m & (part == PID[nm_]) & (kind == EDGE), 0.9, 0)
            if w > 0:
                wear += np.where(mm, np.clip(1 - (w / 2 - np.abs(x)) / 0.002, 0, 1) * 0.6, 0)
            for sh in holes:
                dd_ = disc(s, x, sh, 0.0, 0.002)
                hole = mm & (dd_ > 0)
                c[hole] = c[hole] * 0.3
                h[hole] -= 1.0 * np.clip(dd_[hole] * 3, 0, 1)
        # scabbard: seam along the hidden back, worn flat edges, creases near the top
        if "bainha" in PID:
            mm = m & (part == PID["bainha"])
            ang = x / max(1e-6, 0.0112)                                     # theta (local v = theta * mean radius)
            flat_edge = np.abs(np.sin(ang)) ** 6                            # the narrow edges of the flattened section
            wear += np.where(mm, flat_edge * 0.7, 0)
            seam = np.clip(1 - np.minimum(np.abs(ang), np.abs(ang - 2 * math.pi)) / 0.08, 0, 1)
            h += np.where(mm, -0.3 * seam, 0)
        scuff = np.clip((noise3(pos, 220.0, 9.1) - 0.55) * 4, 0, 1) * np.clip(noise3(pos, 25.0, 3.3) + 0.2, 0, 1)
        wear = np.clip(wear + 0.25 * scuff, 0, 1)
        c = c * (1 - wear[..., None]) + brown * (0.6 + 0.4 * grain[..., None]) * wear[..., None]
        sc = np.clip((noise2(pos[..., 0] + pos[..., 2], pos[..., 1], 900.0, 40.0, 2.0) - 0.82) * 6, 0, 1) * \
            np.clip(N_big + 0.2, 0, 1)                                      # fine light scratches
        c = c + sc[..., None] * 0.10
        dust = np.clip(up - 0.55, 0, 1) * 0.6 * np.clip(0.5 + N_big, 0, 1)
        c = c * (1 - 0.25 * dust[..., None]) + np.array([0.33, 0.30, 0.26], np.float32) * 0.25 * dust[..., None]
        thread = np.clip(stitch_on, 0, 1)
        c = c * (1 - thread[..., None]) + np.array([0.06, 0.055, 0.05], np.float32) * thread[..., None]
        u_ = m & (kind == UNDER)
        c[u_] = np.array([0.20, 0.15, 0.11], np.float32) * (1 + 0.15 * N_mid[u_, None])   # flesh side
        col[m] = (c * occ[..., None])[m]
        hgt[m] = (h + stitch_h)[m]
        spec[m] = (0.32 - 0.18 * wear - 0.10 * dust + 0.10 * thread)[m]
        gloss[m] = (0.58 - 0.25 * wear - 0.2 * dust)[m]
        spec[u_], gloss[u_] = 0.05, 0.12

    # ---------- brass
    m = mat == LATAO
    if m.any():
        polished = np.array([0.80, 0.62, 0.30], np.float32)
        tarnish = np.array([0.38, 0.30, 0.14], np.float32)
        t_ = np.clip(0.75 - ao, 0, 1) * 1.6 + 0.18 * np.clip(N_big + 0.1, 0, 1)
        t_ = np.clip(t_, 0, 1)
        c = polished * (1 - t_[..., None]) + tarnish * t_[..., None]
        c = c * (0.97 + 0.04 * N_mid[..., None])
        e_ = m & (kind == EDGE)
        c[e_] = c[e_] * 1.08
        sc = np.clip((np.abs(noise2(pos[..., 0] * 0.7 + pos[..., 2], pos[..., 1] - pos[..., 2] * 0.5, 1400.0, 60.0, 5.0))
                      - 0.86) * 8, 0, 1)
        c = c + sc[..., None] * np.array([0.10, 0.09, 0.06], np.float32)
        if "cartucheira_placa" in FR:                                     # plate: bevel highlight toward its edges
            f = FR["cartucheira_placa"]
            mm = m & (part == PID["cartucheira_placa"]) & (kind != UNDER)
            pl = [(pos - np.array(f["c"], np.float32)) @ np.array(f[k], np.float32) for k in ("x", "y")]
            dist = np.minimum(f["h"][0] - np.abs(pl[0]), f["h"][1] - np.abs(pl[1]))
            bev = np.clip(1 - dist / 0.0015, 0, 1)
            hgt[mm] = (-0.45 * bev ** 1.5)[mm]
            c[mm] = (c * (1 + 0.15 * bev[..., None]))[mm]
        col[m] = np.clip(c * (0.55 + 0.45 * ao[..., None]), 0, 1)[m]
        hgt[m] += (0.006 * N_mid)[m]
        spec[m] = (0.95 - 0.50 * t_)[m]
        gloss[m] = (0.86 - 0.40 * t_)[m]

    # ---------- iron (socket bayonet)
    m = mat == FERRO
    if m.any():
        c = np.array([0.30, 0.31, 0.33], np.float32)[None, None, :] * (0.9 + 0.12 * N_mid[..., None])
        pat = np.clip(0.55 - ao + 0.25 * N_big, 0, 1)
        c = c * (1 - 0.45 * pat[..., None])
        rust = np.clip((noise3(pos, 300.0, 7.7) - 0.62) * 5, 0, 1) * np.clip(0.4 + N_big, 0, 1)
        c = c * (1 - rust[..., None]) + np.array([0.33, 0.19, 0.09], np.float32) * rust[..., None]
        if "baioneta_alvado" in PID:
            mm = m & (part == PID["baioneta_alvado"])
            rmean = 0.0119
            vpi = math.pi * rmean
            # zig-zag slot of the socket (outer side): down from the mouth, across, down again
            slot = ((np.abs(x - vpi) < 0.0013) & (s > 0.050)) | ((np.abs(s - 0.050) < 0.0013) & (x > vpi - 0.0013)
                                                                 & (x < vpi + 0.010)) | \
                   ((np.abs(x - (vpi + 0.010)) < 0.0013) & (s > 0.040) & (s < 0.0513))
            sl = mm & slot & (kind == TOP)
            c[sl] = 0.03
            hgt[sl] -= 1.5
            # the mouth (end caps): dark bore inside the rim
            f = FR["baioneta_alvado"]
            ax_ = np.array(f["z"], np.float32)
            rel = pos - np.array(f["c"], np.float32)
            rad = np.linalg.norm(rel - (rel @ ax_)[..., None] * ax_, axis=-1)
            bore = mm & (kind == EDGE) & (rad < 0.0093)
            c[bore] = 0.015
        col[m] = (c * occ[..., None])[m]
        hgt[m] += (0.03 * N_fine)[m]
        spec[m] = (0.65 - 0.4 * rust - 0.2 * pat)[m]
        gloss[m] = (0.60 - 0.35 * rust)[m]

    # ---------- hair-on calfskin flap
    m = mat == BEZERRO
    if m.any() and "mochila_tampa" in FR:
        f = FR["mochila_tampa"]
        W, Dd, Rc = f["W"], f["D"], f["Rc"]
        xx, dd = s, x
        warp = 0.010 * noise2(xx, dd, 25.0, 25.0, 3.0)
        strands = noise2(xx + warp, dd, 2600.0, 140.0, 8.0) * 0.6 + noise2(xx + warp * 1.7, dd, 900.0, 60.0, 1.0) * 0.4
        patches = fbm3(pos, 14.0, 3, 21.0)
        base = np.array([0.20, 0.105, 0.052], np.float32)
        dark = np.array([0.085, 0.045, 0.025], np.float32)
        light = np.array([0.30, 0.17, 0.09], np.float32)
        tone = np.clip(0.5 + 0.55 * patches, 0, 1)
        c = dark * (1 - tone[..., None]) + base * tone[..., None]
        c = c + (light - base) * np.clip(strands, 0, 1)[..., None] * 0.6 - (base - dark) * np.clip(-strands, 0, 1)[..., None] * 0.5
        h = 0.30 * strands + 0.10 * noise2(xx + warp, dd, 300.0, 30.0, 6.0)
        ax_ = np.abs(xx)
        cx, cd = W / 2 - Rc, Dd - Rc
        corner = (ax_ > cx) & (dd > cd)
        dist = np.minimum.reduce([dd, W / 2 - ax_, Dd - dd])
        dist = np.where(corner, Rc - np.hypot(ax_ - cx, dd - cd), dist)
        along = np.where(np.minimum(W / 2 - ax_, Dd - dd) < dd, np.where(W / 2 - ax_ < Dd - dd, dd, xx), xx)
        along = np.where(corner, np.arctan2(dd - cd, ax_ - cx) * Rc, along)
        bind = (dist < 0.007) | (kind == EDGE)                              # black leather edging
        bk = np.array([0.035, 0.03, 0.027], np.float32) * (1 + 0.3 * N_mid[..., None])
        c = np.where(bind[..., None], bk, c)
        h = np.where(bind, 0.25 - 0.3 * np.clip(1 - dist / 0.0012, 0, 1), h)
        st, on = stitches(along, dist, 0.0055)
        h += np.where(bind & (kind == TOP), st, 0)
        c = np.where((on > 0.5)[..., None] & bind[..., None] & (kind == TOP)[..., None], np.array([0.07, 0.06, 0.05]), c)
        u_ = m & (kind == UNDER)
        c[u_] = np.array([0.32, 0.24, 0.16], np.float32) * (1 + 0.12 * N_mid[u_, None])
        col[m] = (c * occ[..., None])[m]
        hgt[m] = h[m]
        spec[m] = np.where(bind, 0.28, 0.10)[m]
        gloss[m] = np.where(bind, 0.48, 0.30)[m]
        spec[u_], gloss[u_] = 0.04, 0.10

    # ---------- grey wool greatcoat roll
    m = mat == CAPOTE
    if m.any() and "capote" in FR:
        f = FR["capote"]
        cx_, ax_, aa, bb = (np.array(f[k], np.float32) for k in ("c", "x", "a", "b"))
        rel = pos - cx_
        axial = rel @ ax_
        ra, rb = rel @ aa, rel @ bb
        th = np.mod(np.arctan2(rb, ra), 2 * math.pi)
        rad = np.hypot(ra, rb)
        # Prussian grey greatcoat; French 1812 greatcoats were beige to grey-brown (assumed beige-grey)
        base = np.array([0.36, 0.32, 0.26] if FR_SET else [0.25, 0.25, 0.24], np.float32)
        felt = 0.06 * N_mid + 0.04 * noise3(pos, 400.0, 2.2)
        c = base[None, None, :] * (1 + felt[..., None] + 0.05 * N_big[..., None])
        folds = noise2(axial, th, 8.0, 7.0, 1.0) * 0.6 + noise2(axial, th, 22.0, 18.0, 4.0) * 0.4
        h = 0.9 * folds + 0.05 * noise3(pos, 400.0, 2.2)
        c = c * (1 + 0.10 * np.clip(folds, -1, 1)[..., None])
        body = m & (part == PID["capote"])
        # the outer layer's edge (selvedge) along the roll
        dth = np.mod(th - f["th_step"], 2 * math.pi)
        lip = np.clip(1 - np.minimum(dth, 2 * math.pi - dth) / 0.05, 0, 1)
        h += np.where(body, 0.4 * lip, 0)
        c = c * (1 - 0.15 * lip[..., None] * body[..., None])
        # compressed under the straps: tight folds
        for sx in f["straps"]:
            near = np.clip(1 - (np.abs(axial - sx) - f["strap_w"] / 2) / 0.03, 0, 1)
            h += np.where(body, 0.4 * near * np.sin(th * 18 + noise2(axial, th, 30, 5, 2) * 3), 0)
        # spiral ends
        cap = m & (part == PID["capote_ponta"])
        layer = 0.0045
        sp = np.mod(rad - th / (2 * math.pi) * layer, layer) / layer
        gap = np.clip(1 - np.minimum(sp, 1 - sp) / 0.12, 0, 1)
        h = np.where(cap, -0.8 * gap + 0.1 * noise3(pos, 400.0, 2.2), h)
        c = np.where(cap[..., None], c * (1 - 0.55 * gap[..., None]), c)
        dust = np.clip(up - 0.5, 0, 1) * 0.5
        c = c * (1 - 0.2 * dust[..., None]) + np.array([0.36, 0.33, 0.28], np.float32) * 0.2 * dust[..., None]
        col[m] = (c * occ[..., None])[m]
        hgt[m] = h[m]
        spec[m], gloss[m] = 0.04, 0.12

    return np.clip(col, 0, 1), hgt, spec, gloss


def normal_map(hgt, isl, mm_per_px):
    """Height in mm -> OpenGL normal map; finite differences only between texels of the same UV island."""
    def diff(axis):
        hp, hm = np.roll(hgt, -1, axis), np.roll(hgt, 1, axis)
        ip, im = np.roll(isl, -1, axis), np.roll(isl, 1, axis)
        okp, okm = ip == isl, im == isl
        d = np.where(okp & okm, (hp - hm) / 2, np.where(okp, hp - hgt, np.where(okm, hgt - hm, 0.0)))
        return d / mm_per_px
    gx, gy = diff(1), diff(0)
    n = np.dstack([-gx, gy, np.ones_like(hgt)])
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


def density(ob):
    me = ob.data
    uvl = me.uv_layers["UVMap"].data
    a2 = a3 = 0.0
    for p in me.polygons:
        us = [uvl[li].uv for li in p.loop_indices]
        for k in range(1, len(us) - 1):
            a2 += abs((us[k] - us[0]).cross(us[k + 1] - us[0])) / 2
        a3 += p.area
    return math.sqrt(a2 / a3) * T


objs = {k: bpy.data.objects[n] for k, n, _ in ITEMS}
for key, name, prefix in ITEMS:
    if "only" in OPT and OPT["only"] != key:
        continue
    ob = objs[key]
    others = [o for k, o in objs.items() if k != key]
    ao = np.ones((T, T), np.float32) if "noao" in a else bake_ao(ob, others, int(OPT.get("ao_samples", 64)))
    print(f"AO {key}: mean {ao.mean():.3f}")
    D, pos, nrm, loc, covered = rasterise(ob)
    print(f"RASTER {key}: covered {covered.mean() * 100:.1f}%")
    if "probe" in OPT:                                              # debug: attributes of texels (x,y image pixels)
        parts_ = ob["hcl_partes"].split(",")
        for xy in OPT["probe"].split(";"):
            px_, py_ = (int(v) for v in xy.split(","))
            print(f"PROBE {key} {px_},{py_}: mat {D['mat'][py_, px_]} part {parts_[D['part'][py_, px_]]} kind "
                  f"{D['kind'][py_, px_]} local {loc[py_, px_]} nrm {nrm[py_, px_]} ao {ao[py_, px_]:.2f}")
        continue
    col, hgt, spec, gloss = paint(ob, ao, D, pos, nrm, loc, key)
    dens = density(ob)
    mmpx = 1000.0 / dens
    print(f"DENS {key}: {dens:.0f} px/m -> {mmpx:.3f} mm/px")
    prefix = prefix + SUFFIX
    save(col, f"{prefix}_co.png")
    save(normal_map(hgt, D["isl"], mmpx), f"{prefix}_nohq.png")
    save(np.dstack([np.ones_like(spec), np.clip(spec, 0, 1), np.clip(gloss, 0, 1)]), f"{prefix}_smdi.png")
    if not BLACK_SET:
        save(np.dstack([ao, ao, ao]), f"{prefix}_ao_bake.png")
