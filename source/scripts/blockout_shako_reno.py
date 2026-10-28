# Blockout of the shakos of the Confederation of the Rhine (hcl_reno; spec docs/specs/aliados_fr_1812.md section 2.0).
# COPY of blockout_shako_italia.py (itself a copy of the French shako v4: same fit, proportions, chinscales, plume and
# cords), so hcl_reno does not depend on hcl_italia. Rhine nations:
#   - nacao=saxonia (2026-10-27): Saxony after the 1810 reform. The mod art (saxonINF1812 c3 r4, Reto, authorised) has a
#     brass SHIELD under a crown with the "FA" cipher (Friedrich August), traced by trace_badge.py into
#     source/models/shakos/hcl_shako_reno/placa_saxonia.json, and a WHITE cockade. The Vinkhuijzen album "1810" [VK-REN]
#     shows the line with WHITE cords and a small pompom (plate 036 "Regiment Koenig": white with a red top; plate 005
#     "Prinz Clemens": white 🔶), the grenadier (plate 006) with a tall RED plume and RED cords and tassels, the light
#     infantry (020) with GREEN cords and a small red-and-green tuft (here a green pompom 🔶), the Jaeger (019) with a
#     tall BLACK plume and green cords. Same crowned plate for all (the light plates are too small to read it 🔶).
# The Italian / Neapolitan notes of the source script, kept for the record:
#   - nacao=italia: the brass LOZENGE plate of the mod art (ItalyINF c3 r4; the atlas region is identical to FranceINF's,
#     so the measured outline is the French one, copied as placa_losango_italia.json); cockade red ring, white ring,
#     GREEN centre (📜 Zanoli 1845, "la coccarda nazionale riuniva i colori bianco-verde e rosso"; the mod art shows the
#     same rings). Fusiliers: lentil pompom of the company (1st green, 2nd sky blue, 3rd orange, 4th violet, it.wikipedia
#     after Osprey MAA 43 🔶). Voltigeurs: green plume with a yellow tip, green cords (idem). No lace bands (no source).
#   - nacao=napoles: the SHIELD plate with the "N" monogram of the mod art (NaplesINF c3 r4, outline drawn on a 4x zoom,
#     placa_escudo_napoles.json); cockade white outer ring, amaranth inside; NO cords; fusiliers a lentil pompom in the
#     regiment's distinctive colour, voltigeurs a yellow plume (M. Gaertner, 7th Neapolitan Line 1812-13, after the
#     Freiberger Bilderhandschrift 1813 and others).
#   blender -b --factory-startup --python blockout_shako_reno.py -- <Test_Character_01 dir> <out.blend> <render dir>
#           dir=<folder of the plate JSONs> nacao=saxonia
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender
import shako_fit
from plumet import plumet, feather_material

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OPT = dict(a.split("=", 1) for a in args[3:] if "=" in a)
NACAO = OPT.get("nacao", "saxonia")
RAIZ = {"saxonia": "SX_"}[NACAO]
# absolute paths: Blender resolves a relative render path against the drive root when no .blend is open (renders of
# 2026-10-10 and 2026-10-12 landed in C:\docs\... that way)
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- proportions (PROPOSED, see spec section 4)
# v4 (2026-10-13, "mais profissionalmente ... altura com fontes historicas"): measures of the 1812 regulation (Bardin)
# and of surviving shakos, see docs/specs/barretina_francesa_1812.md section 7: felt 202 mm (fusiliers; grenadiers and
# light carabiniers +15 mm), top 244 mm, top band 41 mm, bottom band 27 mm, visor 58 mm, rosettes 41 mm, chinscales
# 34 -> 21 mm wide, sweatband 57 mm. The fit scale k (~1.03) multiplies the SPEC values.
SPEC_BASE_W, SPEC_H, SPEC_TOP_W = 0.180, 0.196, 0.2365
BAND_TOP, BAND_BOT = 0.041, 0.027
ELITE_EXTRA_H = 0.015
CHEV_W, CHEV_SPREAD = 0.016, math.radians(34)           # V on each side, arms to the top band
VISOR_LEN, VISOR_DROP = 0.058, math.radians(40)
COCK_R = 0.030
PLUME_H = 0.30
# elite gala plumes, user 2026-10-12 "aumenta mais os pumlets dos granadeiros e voltigeurs": taller and fuller
# (0.38 m, radius 54 mm, longer feathers in more tiers); the officers' plumes keep 0.30 m
PLUME_ELITE = dict(H=0.38, R=0.054, feather_len=0.060, rings=36, per_ring=18, estilo="v4")
# 2026-10-13 ("de mais realismo as pumlets"): plumet.py estilo v4 (3-segment feathers, raised shaft, curled tips)
PLUME_OFICIAL = dict(H=PLUME_H, feather_len=0.050, rings=30, per_ring=16, estilo="v4")
DEPTH_RATIO, TILT = shako_fit.DEPTH_RATIO, shako_fit.TILT
WALL, CLEAR = shako_fit.WALL, shako_fit.CLEAR
N = 96                                                  # v4: 96 segments around (was 48)

F = shako_fit.compute(SAMPLES)                           # head band of the official cap (read-only Samples)
base_hw = max(SPEC_BASE_W / 2, F["head_hw"] + WALL + CLEAR)
k = base_hw / (SPEC_BASE_W / 2)
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
H = SPEC_H * k
H_BASE = H
top_hw = SPEC_TOP_W / 2 * k
top_hd = top_hw * base_hd / base_hw
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')
print(f"FIT k={k:.4f} H={H:.3f} base={2*base_hw:.3f}x{2*base_hd:.3f} top={2*top_hw:.3f}x{2*top_hd:.3f}")


def rx(z): return base_hw + (top_hw - base_hw) * z / H
def ry(z): return base_hd + (top_hd - base_hd) * z / H
def P(theta, z, off=0.0):
    """Shako-local point; theta = 0 is the FRONT (-Y), +90 deg the wearer's left (+X)."""
    return Vector(((rx(z) + off) * math.sin(theta), -(ry(z) + off) * math.cos(theta), z))
def wall_n(theta, z):
    n = Vector((math.sin(theta) / rx(z), -math.cos(theta) / ry(z), 0)).normalized()
    return (n - Vector((0, 0, (top_hw - base_hw) / H))).normalized()


SHK_DIR = os.path.abspath(OPT["dir"])                # source/models/shakos/hcl_shako_reno
PLATES = {"saxonia": os.path.join(SHK_DIR, "placa_saxonia.json")}
PLATE_W = {"saxonia": 0.076}                        # the crowned shield is 0.62 as wide as high
ATLAS_PX = 4096
ROSETTE_BOX = (1726, 2268, 1776, 2323)             # star rosette, same place in saxonINF1812 (tile c3 r4)
COL = dict(feltro=(0.015, 0.015, 0.016), couro=(0.03, 0.025, 0.02), latao=(0.70, 0.50, 0.16), ganse=(0.55, 0.54, 0.50),
           vermelho=(0.55, 0.03, 0.03), amarelo=(0.80, 0.62, 0.06), verde=(0.03, 0.20, 0.06),
           branco=(0.82, 0.82, 0.80), azul=(0.04, 0.08, 0.35), verde_esc=(0.02, 0.15, 0.05),
           ouro=(0.85, 0.62, 0.20), preto=(0.02, 0.02, 0.02), prata=(0.72, 0.72, 0.70),
           couro_marrom=(0.05, 0.028, 0.014), forro=(0.33, 0.29, 0.22),
           azul_celeste=(0.30, 0.55, 0.85), laranja=(0.85, 0.40, 0.08), violeta=(0.35, 0.10, 0.45),
           amaranto=(0.45, 0.04, 0.18), escarlate=(0.70, 0.06, 0.04), azul_claro=(0.36, 0.56, 0.84))
MATS = {}


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name in ("latao", "ouro", "prata") else 0.7
        b.inputs["Metallic"].default_value = 1.0 if name in ("latao", "ouro", "prata") else 0.0
        MATS[name] = m
    return MATS[name]


PARTS = []
PMATS = {}


def pmat(name):
    """Plume material: feather barbs, shaft and per-feather shade (plumet.feather_material)."""
    if name not in PMATS:
        m = bpy.data.materials.new("BO_plumet_" + name); m.use_nodes = True
        feather_material(m, COL[name])
        PMATS[name] = m
    return PMATS[name]


def finish(bm, name, colour, parent, by_colour=None, keep_normals=False, plume=False):
    """by_colour = {colour: [faces]} for several materials in one object (feathered plumes)."""
    if not keep_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if by_colour:
        names = list(by_colour)
        for mi, nm in enumerate(names):
            for f in by_colour[nm]:
                f.material_index = mi
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for nm in (names if by_colour else [colour]):
        me.materials.append(pmat(nm) if plume else mat(nm))
    ob = bpy.data.objects.new(name, me); ob.parent = parent
    scene.collection.objects.link(ob); PARTS.append(ob)
    return ob


def grid(bm, rows, closed_u=True, closed_v=False):
    nr, nc = len(rows), len(rows[0])
    for j in range(nr - (0 if closed_v else 1)):
        for i in range(nc - (0 if closed_u else 1)):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nc], rows[(j + 1) % nr][(i + 1) % nc], rows[(j + 1) % nr][i]))


def cap_ring(bm, ring, centre):
    c = bm.verts.new(centre)
    for i in range(len(ring)):
        bm.faces.new((c, ring[i], ring[(i + 1) % len(ring)]))


def lathe_band(name, z0, z1, t, colour, parent):
    bm = bmesh.new()
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, o)) for i in range(N)] for z, o in ((z0, 0.0005), (z0, t), (z1, t), (z1, 0.0005))]
    grid(bm, rows, closed_v=True)
    return finish(bm, name, colour, parent)


def sweep(name, path, half_w, half_t, colour, parent, normals=None, round_=False, segs=8):
    """Strip (or round tube) along a polyline; normals = outward direction at each point (strip lies across it)."""
    bm = bmesh.new()
    rows = []
    for k_, p in enumerate(path):
        tng = (path[min(k_ + 1, len(path) - 1)] - path[max(k_ - 1, 0)]).normalized()
        nrm = normals[k_] if normals else (tng.orthogonal()).normalized()
        nrm = (nrm - tng * nrm.dot(tng)).normalized()
        side = tng.cross(nrm).normalized()
        if round_:
            rows.append([bm.verts.new(p + half_w * (math.cos(2 * math.pi * s / segs) * nrm + math.sin(2 * math.pi * s / segs) * side)) for s in range(segs)])
        else:
            rows.append([bm.verts.new(p + side * sx * half_w + nrm * sz * half_t) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    grid(bm, rows)
    cap_ring(bm, rows[0], path[0]); cap_ring(bm, rows[-1], path[-1])
    return finish(bm, name, colour, parent)


def catmull(pts, n=10):
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for s in range(n):
            t = s / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def lathe_obj(name, profile, centre, colour, parent, axis=Vector((0, 0, 1)), segs=20):
    """Solid of revolution: profile = [(along, radius)], around 'axis' through 'centre'."""
    bm = bmesh.new()
    u = axis.orthogonal().normalized(); v = axis.cross(u).normalized()
    rows = [[bm.verts.new(centre + axis * a + r * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)] for a, r in profile]
    grid(bm, rows)
    cap_ring(bm, rows[0], centre + axis * profile[0][0]); cap_ring(bm, rows[-1], centre + axis * profile[-1][0])
    return finish(bm, name, colour, parent)


def flat_on_front(name, poly_sz, t, colour, parent, off=0.002):
    """Flat ornament (s = arc length from the front centre, z) laid on the front wall."""
    bm = bmesh.new()
    def at(s, z, o):
        return P(s / ry(z), z, off + o)                     # near the front the local radius of curvature ~ ry
    front = [bm.verts.new(at(s, z, t)) for s, z in poly_sz]
    back = [bm.verts.new(at(s, z, 0.0)) for s, z in poly_sz]
    n = len(poly_sz)
    sc = sum(s for s, _ in poly_sz) / n; zc_ = sum(z for _, z in poly_sz) / n
    cf, cb = bm.verts.new(at(sc, zc_, t)), bm.verts.new(at(sc, zc_, 0.0))   # explicit fans: the outline is not planar
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((cf, front[i], front[j])); bm.faces.new((cb, back[j], back[i]))
        bm.faces.new((front[i], back[i], back[j], front[j]))
    return finish(bm, name, colour, parent)


def disc(name, centre, normal, r, t, colour, parent, segs=24):
    return lathe_obj(name, [(0, 0.0005), (0, r), (t, r), (t, 0.0005)], centre, colour, parent, axis=normal, segs=segs)


def art_uv(px, py):
    """Atlas pixel (x right, y down) -> UV of the mod art."""
    return (px / ATLAS_PX, 1.0 - py / ATLAS_PX)


def traced_plate(name, json_path, z_bot, z_top, max_w, depth, colour, parent):
    """Brass plate from a traced outline (trace_badge.py JSON: loops in crop pixels, holes included), scaled to fit
    between z_bot and z_top (and max_w wide), extruded `depth` and wrapped on the front wall. UV layer "arte" = the
    same point in the mod art, so the plate's relief can be baked from it."""
    bj = json.load(open(json_path))
    X0, Y0 = bj["box"][:2]
    cu = bpy.data.curves.new(name + "_curva", "CURVE")
    cu.dimensions, cu.fill_mode = "2D", "BOTH"
    for loop in bj["loops"]:
        sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1)
        for p_, (x, y) in zip(sp.points, loop):
            p_.co = (x, -y, 0.0, 1.0)
        sp.use_cyclic_u = True
    xs = [x for l in bj["loops"] for x, _ in l]; ys = [y for l in bj["loops"] for _, y in l]
    kf = min(max_w / (max(xs) - min(xs)), (z_top - z_bot) / (max(ys) - min(ys)))
    cu.extrude = depth / 2 / kf
    tob = bpy.data.objects.new(name + "_curva", cu); scene.collection.objects.link(tob)
    bpy.context.view_layer.update()
    me0 = bpy.data.meshes.new_from_object(tob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tob); bpy.data.curves.remove(cu)
    ub = bmesh.new(); ub.from_mesh(me0); bpy.data.meshes.remove(me0)
    bmesh.ops.remove_doubles(ub, verts=ub.verts[:], dist=1e-4)
    bmesh.ops.triangulate(ub, faces=ub.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    for _ in range(8):                                   # long fill triangles would cut the curved wall: a 20 mm
        long_e = [e for e in ub.edges if e.calc_length() * kf > 0.013]   # v4: 13 mm edges (relief is in the normal map)
        if not long_e:
            break
        bmesh.ops.subdivide_edges(ub, edges=long_e, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(ub, faces=[f for f in ub.faces if len(f.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
    cx = (max(xs) + min(xs)) / 2
    ymid = (max(ys) + min(ys)) / 2
    zmin = min(v.co.z for v in ub.verts)
    zc_ = (z_bot + z_top) / 2
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("arte")
    vm = {}
    for v in ub.verts:
        lx, ly, lz = (v.co.x - cx) * kf, (v.co.y + ymid) * kf, (v.co.z - zmin) * kf
        z = zc_ + ly
        vm[v.index] = (bm.verts.new(P(lx / ry(z), z, 0.0008 + lz)), art_uv(X0 + v.co.x, Y0 - v.co.y))
    ub.verts.index_update()
    for f in ub.faces:
        try:
            nf = bm.faces.new([vm[v.index][0] for v in f.verts])
        except ValueError:
            continue
        for l, v in zip(nf.loops, f.verts):
            l[uvl].uv = vm[v.index][1]
    ub.free()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = finish(bm, name, colour, parent, keep_normals=True)
    w_, h_ = (max(xs) - min(xs)) * kf, (max(ys) - min(ys)) * kf
    print(f"PLACA {name}: {os.path.basename(json_path)} {w_ * 1000:.0f} x {h_ * 1000:.0f} mm, {len(ob.data.polygons)} faces")
    return ob


def art_disc(name, centre, normal, r, t, box, colour, parent, segs=24):
    """Disc (rosette) whose front face carries the mod art of `box` (atlas pixels) in UV layer "arte"."""
    ob = disc(name, centre, normal, r, t, colour, parent, segs)
    me = ob.data
    uvl = me.uv_layers.new(name="arte")
    u_ = normal.orthogonal().normalized(); v_ = normal.cross(u_).normalized()
    bx0, by0, bx1, by1 = box
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            d = co - centre
            a, b = d.dot(u_) / r, d.dot(v_) / r            # -1..1 across the disc
            uvl.data[li].uv = art_uv(bx0 + (bx1 - bx0) * (0.5 + 0.5 * a), by0 + (by1 - by0) * (0.5 - 0.5 * b))
    return ob


def chinscales(name, path, normals, colour, parent, n_scales=12):
    """Black leather strap with overlapping brass scales (each rounded edge toward the chin, lying on the next one)."""
    sweep(name + "_couro", path, 0.0115, 0.0007, "couro", parent, normals=normals)   # v4: 23 mm leather strap
    L = [0.0]
    for a_, b_ in zip(path, path[1:]):
        L.append(L[-1] + (b_ - a_).length)
    total = L[-1]

    def at(d):
        for k_ in range(len(L) - 1):
            if L[k_ + 1] >= d:
                t_ = (d - L[k_]) / max(1e-9, L[k_ + 1] - L[k_])
                return path[k_].lerp(path[k_ + 1], t_), normals[k_].lerp(normals[k_ + 1], t_).normalized(), (path[k_ + 1] - path[k_]).normalized()
        return path[-1], normals[-1], (path[-1] - path[-2]).normalized()

    bm = bmesh.new()
    step = (total - 0.012) / (n_scales - 1)
    for k_ in range(n_scales):
        d0 = 0.004 + k_ * step
        p, n, tg = at(d0)
        n = (n - tg * n.dot(tg)).normalized()
        side = tg.cross(n).normalized()
        w = 0.0170 - 0.0065 * k_ / (n_scales - 1)          # v4: 34 -> 21 mm wide toward the chin (surviving shakos)
        ln = step * 1.65                                 # overlap: ~40 % covered by the scale above
        lift = 0.0010 + 0.00035 * (n_scales - 1 - k_)     # upper scale on top of the lower one
        outline = [(-w, 0.0), (0.0, 0.0), (w, 0.0), (w, ln * 0.5)] + [(w * math.cos(math.pi * i / 10), ln * 0.5 + ln * 0.5 * math.sin(math.pi * i / 10)) for i in range(1, 10)] + [(-w, ln * 0.5)]
        top, bot = [], []
        for sx, sl in outline:
            dome = 0.0013 * (1 - (sx / w) ** 2)                # v4: stamped dome
            q = p + side * sx + tg * sl + n * (lift + dome)
            top.append(bm.verts.new(q)); bot.append(bm.verts.new(q - n * 0.0006))
        m_ = len(outline)
        ct = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0009)); cb = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0003))
        for i in range(m_):
            j = (i + 1) % m_
            bm.faces.new((ct, top[i], top[j])); bm.faces.new((cb, bot[j], bot[i]))
            bm.faces.new((top[j], top[i], bot[i], bot[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(bm, name, colour, parent, keep_normals=True)


def fringe_tassel(name, top, colour, parent, r=0.009, length=0.034, strands=18, seed=3):
    """Tassel of the parade cords: a turned head and a skirt of hanging strands (double-sided narrow strips)."""
    rnd = random.Random(seed)
    lathe_obj(name + "_cabeca", [(0.0, 0.002), (-0.006, 0.006), (-0.012, r), (-0.014, r * 0.85)], top, colour, parent,
              axis=Vector((0, 0, 1)), segs=12)
    bm = bmesh.new()
    for i in range(strands):
        a = 2 * math.pi * i / strands + rnd.uniform(-0.12, 0.12)
        o = Vector((math.cos(a), math.sin(a), 0))
        sd = Vector((-math.sin(a), math.cos(a), 0))
        L_ = length * rnd.uniform(0.9, 1.08)
        rows = []
        for t_ in (0.0, 0.5, 1.0):
            c = top + Vector((0, 0, -0.012 - L_ * t_)) + o * (r * 0.9 + 0.004 * t_ + rnd.uniform(-0.0005, 0.0005))
            hw = 0.0016 * (1 - 0.4 * t_)
            rows.append((bm.verts.new(c - sd * hw), bm.verts.new(c + sd * hw)))
        for (a0, b0), (a1, b1) in zip(rows, rows[1:]):
            bm.faces.new((a0, b0, b1, a1))
        rows2 = [(bm.verts.new(a0.co - o * 0.0003), bm.verts.new(b0.co - o * 0.0003)) for a0, b0 in rows]
        for (a0, b0), (a1, b1) in zip(rows2, rows2[1:]):
            bm.faces.new((a1, b1, b0, a0))
    return finish(bm, name + "_franja", colour, parent, keep_normals=True)


def woolly(ob, amp=0.0012, seed=5):
    """Fulled-wool pompom: small irregular bumps, so it is not a perfect solid of revolution."""
    rnd = random.Random(seed)
    me = ob.data
    c = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
    for v in me.vertices:
        d = v.co - c
        if d.length > 1e-6:
            v.co += d.normalized() * amp * (math.sin(d.x * 900 + rnd.random()) * math.sin(d.y * 870) * math.sin(d.z * 930) + rnd.uniform(-0.5, 0.5))
    return ob


def pleated(name, centre, normal, r_in, r_out, t, n, colour, parent):
    """Pleated ring of the cockade: n pleats, each a fold rising t at its crest (v4)."""
    bm = bmesh.new()
    u = normal.orthogonal().normalized(); v = normal.cross(u).normalized()
    M = 2 * n
    rows = []
    for rr, k in ((r_in, 0.4), ((r_in + r_out) / 2, 1.0), (r_out, 0.7)):
        row = []
        for i in range(M):
            a = 2 * math.pi * i / M
            h = t * k * (1.0 if i % 2 == 0 else 0.15)
            row.append(bm.verts.new(centre + normal * h + rr * (math.cos(a) * u + math.sin(a) * v)))
        rows.append(row)
    base_out = [bm.verts.new(centre + r_out * (math.cos(2 * math.pi * i / M) * u + math.sin(2 * math.pi * i / M) * v)) for i in range(M)]
    grid(bm, rows + [base_out])
    return finish(bm, name, colour, parent)


def twisted(name, path, r, colour, parent, pitch=0.012, segs=5):
    """Parade cord of two strands twisted together (v4): two thin tubes winding round the path."""
    L = [0.0]
    for a_, b_ in zip(path, path[1:]):
        L.append(L[-1] + (b_ - a_).length)
    dense = []
    step = 0.004
    d = 0.0
    while d <= L[-1]:
        i = max(0, min(len(path) - 2, next((k for k in range(len(L) - 1) if L[k + 1] >= d), len(L) - 2)))
        f_ = (d - L[i]) / max(1e-9, L[i + 1] - L[i])
        dense.append((path[i].lerp(path[i + 1], f_), d))
        d += step
    for strand in (0, 1):
        pts = []
        for k, (p, dd) in enumerate(dense):
            tng = (dense[min(k + 1, len(dense) - 1)][0] - dense[max(k - 1, 0)][0]).normalized()
            nrm = tng.orthogonal().normalized(); bi = tng.cross(nrm)
            a = 2 * math.pi * dd / pitch + math.pi * strand
            pts.append(p + (nrm * math.cos(a) + bi * math.sin(a)) * r * 0.48)
        sweep(f"{name}_{strand}", pts, r * 0.56, 0, colour, parent, round_=True, segs=segs)


# ---------------------------------------------------------------- one shako
def shako(tag, x_off, lace, chevron, top, cords=None, rank_bands=None, plate=None, metal="latao"):
    """plate: "semicirculo" | "granadas" | "losango" (default by company); metal: "latao" (brass) or "prata" (white
    metal: plate, cockade button, rosettes, chinscales and plume socket)."""
    global H
    H = H_BASE + (ELITE_EXTRA_H if tag.startswith(("granadeiro", "ligeira_carabineiro")) else 0.0)   # Bardin: +15 mm
    root = bpy.data.objects.new(f"{RAIZ}{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    # body: felt wall with thickness; the crown is the separate leather top below (2026-10-13). The felt is not a
    # turned solid: soft inward dents of up to 1.2 mm between the bands (never outward: plate, rosettes and chevrons
    # lie 0.8 mm off the nominal wall)
    bm = bmesh.new()
    zs = [H * i / 12 for i in range(13)]                  # v4: 12 rows outside (was 8); 4 inside (hidden by the lining)
    rnd_f = random.Random(sum(map(ord, tag)) + 11)
    ph1, ph2 = rnd_f.uniform(0, 6.3), rnd_f.uniform(0, 6.3)

    def dent(th, z):
        if z < BAND_BOT + 0.004 or z > H - BAND_TOP - 0.004:
            return 0.0
        w = math.sin(math.pi * (z - BAND_BOT - 0.004) / (H - BAND_TOP - BAND_BOT - 0.008))
        return -0.0012 * w * (0.5 + 0.5 * math.sin(3 * th + ph1)) * (0.6 + 0.4 * math.sin(7 * th - 5 * z / H + ph2))
    outer = [[bm.verts.new(P(2 * math.pi * i / N, z, dent(2 * math.pi * i / N, z))) for i in range(N)] for z in zs]
    inner = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL)) for i in range(N)] for z in (0.0, H * 0.33, H * 0.66, H - 0.008)]
    grid(bm, outer); grid(bm, [inner[0], outer[0]]); grid(bm, inner[::-1])
    grid(bm, [inner[-1], [bm.verts.new(P(2 * math.pi * i / N, H - 0.004, -WALL)) for i in range(N)]])
    finish(bm, f"{tag}_corpo", "feltro", root)
    # leather top: sewn into the felt rim, slightly dished (3 mm at the centre), with a rolled seam at the edge
    bm = bmesh.new()
    rim = [bm.verts.new(P(2 * math.pi * i / N, H, 0.0004)) for i in range(N)]
    seam = [bm.verts.new(P(2 * math.pi * i / N, H + 0.0012, -0.0025)) for i in range(N)]
    rings_t = [rim, seam]
    for f_ in (0.75, 0.45, 0.18):
        rings_t.append([bm.verts.new(Vector((rx(H) * f_ * math.sin(2 * math.pi * i / N), -ry(H) * f_ * math.cos(2 * math.pi * i / N),
                                             H - 0.003 * (1 - f_ ** 2)))) for i in range(N)])
    grid(bm, rings_t)
    cap_ring(bm, rings_t[-1], Vector((0, 0, H - 0.003)))
    finish(bm, f"{tag}_topo", "couro", root)
    # inside: leather sweatband over the bottom band, linen lining above it (seen from below)
    bm = bmesh.new()
    rows_s = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.020, 0.040, 0.057)]
    grid(bm, rows_s[::-1])
    finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    bm = bmesh.new()
    rows_l = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0012)) for i in range(N)] for z in (0.055, H * 0.5, H - 0.006)]
    grid(bm, rows_l[::-1])
    cap_ring(bm, rows_l[-1][::-1], Vector((0, 0, H - 0.006)))
    finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    # leather bands (black) with the lace over them for elite companies
    lathe_band(f"{tag}_faixa_baixo", 0.0, BAND_BOT, 0.0018, lace or "couro", root)
    lathe_band(f"{tag}_faixa_cima", H - BAND_TOP, H, 0.0018, lace or "couro", root)
    # officers: gold lace of the rank on the top band (colonel: 34 mm + 14 mm, 20 mm apart; sub-lieutenant: 18 mm)
    for k_, (w_, gap_) in enumerate(rank_bands or []):
        z1_ = H - 0.002 - gap_
        lathe_band(f"{tag}_galao_posto_{k_}", z1_ - w_, z1_, 0.0026, "ouro", root)
    # side chevrons (officers: none, the 1811 model dropped them)
    for sgn in ((1, -1) if chevron is not False else ()):
        pts, nrm = [], []
        ctrl = [(math.pi / 2 - CHEV_SPREAD, H - BAND_TOP + 0.004), (math.pi / 2, BAND_BOT + 0.006), (math.pi / 2 + CHEV_SPREAD, H - BAND_TOP + 0.004)]
        for (a0, z0), (a1, z1) in zip(ctrl, ctrl[1:]):
            for s in range(8):
                t = s / 8
                a, z = a0 + (a1 - a0) * t, z0 + (z1 - z0) * t
                pts.append(P(sgn * a, z, 0.0026)); nrm.append(wall_n(sgn * a, z))
        a, z = ctrl[-1]; pts.append(P(sgn * a, z, 0.0026)); nrm.append(wall_n(sgn * a, z))
        sweep(f"{tag}_divisa_{'E' if sgn > 0 else 'D'}", pts, CHEV_W / 2, 0.0008, chevron or "couro", root, normals=nrm)
    # visor (front arc, sloping down)
    bm = bmesh.new()
    arc = [math.radians(-82 + 164 * i / 48) for i in range(49)]
    def vrow(off_len, dz):
        out = []
        for a in arc:
            n = wall_n(a, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a) / math.radians(82)) ** 4                      # narrower towards the sides
            out.append(P(a, 0.004, 0.002) + n * off_len * w * math.cos(VISOR_DROP) + Vector((0, 0, -off_len * w * math.sin(VISOR_DROP) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in vrow(0.0, 0.0)], [bm.verts.new(p) for p in vrow(VISOR_LEN, 0.0)],
            [bm.verts.new(p) for p in vrow(VISOR_LEN, -0.003)], [bm.verts.new(p) for p in vrow(0.0, -0.003)]]
    grid(bm, rows, closed_u=False, closed_v=True)
    for r in (0, 48):
        bm.faces.new((rows[0][r], rows[1][r], rows[2][r], rows[3][r]))
    edge = [(rows[1][i].co + rows[2][i].co) / 2 for i in range(len(arc))]   # before finish() frees the bmesh
    finish(bm, f"{tag}_pala", "couro", root)
    sweep(f"{tag}_pala_debrum", edge, 0.0021, 0, "couro", root, round_=True, segs=6)
    # tricolour cockade on the top band, held by a strap ("ganse") with a brass button (mod art)
    zc = H - COCK_R - 0.004
    c0 = P(0, zc, 0.0018); nc = wall_n(0, zc)
    # Saxony: a white cockade (mod art saxonINF1812 c3 r4)
    rings = {"saxonia": ("branco", "branco", "branco")}[NACAO]
    pleated(f"{tag}_cocar_fora", c0, nc, COCK_R * 0.62, COCK_R, 0.003, 36, rings[0], root)
    pleated(f"{tag}_cocar_meio", c0 + nc * 0.0012, nc, COCK_R * 0.30, COCK_R * 0.66, 0.003, 28, rings[1], root)
    disc(f"{tag}_cocar_centro", c0 + nc * 0.0036, nc, COCK_R * 0.33, 0.0015, rings[2], root, segs=32)
    g_pts, g_nrm = [], []
    for i in range(13):
        z = zc + (H - 0.0015 - zc) * i / 12
        over = z < zc + COCK_R * 0.92
        o = 0.0068 if over else 0.0028 + 0.0040 * max(0.0, 1 - (z - zc - COCK_R * 0.92) / 0.004)
        g_pts.append(P(0, z, o)); g_nrm.append(wall_n(0, z))
    sweep(f"{tag}_ganse", g_pts, 0.0045, 0.0005, "ganse", root, normals=g_nrm)
    lathe_obj(f"{tag}_ganse_botao", [(0.0, 0.0005), (0.0, 0.0055), (0.0012, 0.0052), (0.0024, 0.0035), (0.0028, 0.0005)],
              c0 + nc * 0.0072, metal, root, axis=nc, segs=14)
    # plate traced from the mod art (grenadiers: the plate flanked by two grenades), between the bottom band and the
    # cockade
    plate_kind = plate or NACAO
    # Saxony: the crown of the shield stays clear BELOW the cockade (at 0.55 x its radius it was hidden behind it)
    traced_plate(f"{tag}_placa", PLATES[plate_kind], BAND_BOT + 0.003, zc - COCK_R - 0.003,
                 PLATE_W[plate_kind], 0.0024, metal, root)
    # top ornament
    front_top = P(0, H, -0.010)
    kind = top[0]
    if kind == "lentilha":                              # fusilier pompom: lentil standing on the top edge
        c = front_top + Vector((0, -0.002, 0.026))
        woolly(lathe_obj(f"{tag}_pompom", [(-0.010, 0.002), (-0.008, 0.020), (-0.004, 0.029), (0.0, 0.031), (0.004, 0.029), (0.008, 0.020), (0.010, 0.002)],
                         c, top[1], root, axis=Vector((0, -1, 0)), segs=48), amp=0.0008)
    elif kind == "bola":                                # large campaign pompom of the elite companies
        c = front_top + Vector((0, -0.002, 0.034))
        prof = [(-0.036 * math.cos(math.pi * i / 10), 0.0005 + 0.036 * math.sin(math.pi * i / 10)) for i in range(11)]
        woolly(lathe_obj(f"{tag}_pompom", prof, c, top[1], root, axis=Vector((0, 0, 1)), segs=28), amp=0.0015)
    elif kind == "plumet":                              # tall plume in a brass socket ("tulipe")
        elite = tag.startswith(("granadeiro", "voltigeur", "ligeira_"))
        tul = [(-0.012, 0.005), (0.0, 0.0075), (0.012, 0.0125)] if elite else [(-0.012, 0.004), (0.0, 0.006), (0.012, 0.010)]
        lathe_obj(f"{tag}_tulipa", tul, front_top + Vector((0, 0, 0.002)), metal, root)
        base = front_top + Vector((0, 0, 0.012))
        # feathered plume (plumet.py): colour bands by height, e.g. green with a yellow tip, white with a red top
        bm = bmesh.new()
        kw = PLUME_ELITE if elite else PLUME_OFICIAL
        by = plumet(bm, base, colours=top[1], seed=sum(map(ord, tag)), **kw)
        finish(bm, f"{tag}_plumet", None, root, by_colour=by, keep_normals=True, plume=True)
    # chinscales: brass rosettes and scale straps under the chin (chin ESTIMATED: the game head is a proxy)
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, F["head_cy"] - F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        ro = P(sgn * math.radians(92), 0.026, 0.0035)
        art_disc(f"{tag}_roseta_{'E' if sgn > 0 else 'D'}", ro, wall_n(sgn * math.radians(92), 0.026), 0.0205, 0.0035, ROSETTE_BOX, metal, root, segs=48)
        # the strap runs down the outside of the cheek: mid point outside the (approximate) head at that height
        ro_w = root.matrix_world @ ro
        z_mid = (ro_w.z + chin_w.z) / 2
        hz = (F["z_head_top"] - 0.57) / 2 - 0.004; zc_h = (F["z_head_top"] + 0.57) / 2
        half_w = (F["head_hw"] - 0.006) * math.sqrt(max(0.0, 1 - ((z_mid - zc_h) / hz) ** 2))
        mid = inv @ Vector((x_off + sgn * (half_w + 0.010), F["head_cy"] - 0.012, z_mid))
        path = catmull([ro, mid, Vector((sgn * 0.035, chin.y, chin.z + 0.006)), Vector((0.0, chin.y, chin.z))], 6)
        nrm = [Vector((p.x, p.y, 0)).normalized() for p in path]       # strap lies flat on the cheek
        chinscales(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, nrm, metal, root)
    # parade cords: one festoon across the front, "raquette" and two tassels on the wearer's right side
    if cords:
        fest = catmull([P(math.radians(-112), H - 0.040, 0.008), P(math.radians(-60), 0.112, 0.009), P(0, 0.082, 0.010),
                        P(math.radians(60), 0.112, 0.009), P(math.radians(112), H - 0.040, 0.008)], 8)
        twisted(f"{tag}_cordao", fest, 0.0035, cords, root)
        side = P(math.radians(-100), 0.11, 0.010)
        hang = [P(math.radians(-112), H - 0.040, 0.008), side, side + Vector((0, 0, -0.07))]
        twisted(f"{tag}_cordao_lado", catmull(hang, 6), 0.0035, cords, root)
        n = wall_n(math.radians(-100), 0.05); n.z = 0; n.normalize()
        rq = side + Vector((0, 0, -0.09)) + n * 0.004
        lathe_obj(f"{tag}_raquete", [(-0.035, 0.002), (-0.025, 0.014), (0.0, 0.018), (0.025, 0.014), (0.035, 0.002)], rq, cords, root, axis=Vector((0, 0, 1)), segs=12)
        for dx in (-0.012, 0.012):
            t0 = rq + Vector((dx * n.y, -dx * n.x, -0.040))
            fringe_tassel(f"{tag}_borla_{'a' if dx < 0 else 'b'}", t0, cords, root, seed=7 if dx < 0 else 8)
    return root


VARIANTS = {  # tag, lace, chevrons, top ornament, cords
    # Saxony 1810 (Vinkhuijzen album "1810"): no side chevrons in the plates (False); the line with white cords
    "saxonia": [("fuzileiro", None, False, ("lentilha", "branco"), "branco"),                       # 005 Prinz Clemens 🔶
                ("fuzileiro_koenig", None, False, ("lentilha", "vermelho"), "branco"),             # 036 Koenig 🔶
                ("granadeiro_gala", None, False, ("plumet", [(0.0, "vermelho")]), "vermelho"),     # 006 grenadier
                ("ligeira", None, False, ("lentilha", "verde"), "verde"),                          # 020 light infantry 🔶
                ("jaeger", None, False, ("plumet", [(0.0, "preto")]), "verde")],                   # 019 Jaeger
}[NACAO]
SPACING = 0.42
roots = [shako(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

# ---------------------------------------------------------------- references: approximate head under every shako
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
for p in hme.polygons:
    p.use_smooth = True
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
hme.materials.append(skin)
for i in range(len(VARIANTS)):
    h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    scene.collection.objects.link(h)

# ---------------------------------------------------------------- numbers
bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:22s} pecas {len(obs):2d}  triangulos {tris:5d}  topo {zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

# ---------------------------------------------------------------- renders
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
os.makedirs(RENDER_DIR, exist_ok=True)
zc = (ROOT @ Vector((0, 0, H / 2))).z + 0.06


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 700)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_shako_{NACAO}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_frente", (mid_x, -3.0, zc), (mid_x, 0, zc), ortho=SPACING * len(VARIANTS) + 0.13, res=(2200, 700))
shot("fila_tres_quartos", (mid_x + 1.3, -2.8, zc + 0.6), (mid_x, 0, zc - 0.02), lens=45, res=(2200, 800))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]


def solo(i):
    """Only variant i (and its head) renders: side views look along X, through the whole row."""
    for j, r in enumerate(roots):
        for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
            o.hide_render = j != i


for i, nm_ in ((0, "fuzileiro_lado"), (len(VARIANTS) - 1, "voltigeur_lado")):
    solo(i)
    shot(nm_, (i * SPACING - 2.0, F["head_cy"], zc), (i * SPACING, F["head_cy"], zc), ortho=0.75, res=(900, 1000))
solo(-1)
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
