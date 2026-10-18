# Phase 3 (blockout) of the Polish infantry "czapka rogata" of the Duchy of Warsaw, regulation of 3 September 1810
# (spec docs/specs/aliados_fr_1812.md section 1.1; user 2026-10-18: "utilize fontes historicas de museus e
# documentos"). Built as a COPY of blockout_shako_fr.py (helpers, fit on the official Samples head band, visor,
# chinscales, cords, pompom, plume, traced plates with UV "arte"); the body and the crown are new:
#   regulation (Gembarzewski 1905; Zygulski & Wielecki 1988, pp. 60-61; 📜): black felt, card and linen, ~22.5 cm high,
#   sides of the top 25 cm; leather peak edged with yellow metal; white-metal eagle above a yellow plate with the
#   regiment number; yellow chin strap with a fusilier star (voltigeur bugle) on the boss; white cockade; white cords;
#   black pompom (fusiliers) or yellow-green tuft (voltigeurs).
#   shape: the felt body rises from the head band and flares in its upper part into the square top, set with a corner
#   to the front (Knoetel, Uniformenkunde IV 9, 1890, "Polen 1812"; lancer czapka practice; 🔶), body flare 🔶.
#   plate and eagle: outlines drawn on 6x zooms of the mod art polandINF c0 r5 (Reto pack, authorised; 🎮), the art
#   shows the number 4 (4th Regiment). Sizes from the art's own scale (0.79 mm per atlas pixel 🔶).
#   blender -b --factory-startup --python blockout_czapka_varsovia.py -- <Test_Character_01 dir> <out.blend> <render dir>
#           [dir=<folder of placa_aguia_varsovia.json / placa_numero_varsovia.json>]
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender
import shako_fit
from plumet import plumet, feather_material

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
# absolute paths: Blender resolves a relative render path against the drive root when no .blend is open (renders of
# 2026-10-10 and 2026-10-12 landed in C:\docs\... that way)
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- proportions (regulation 1810 📜 + 🔶)
SPEC_BASE_W, SPEC_H = 0.180, 0.225          # band width as the French shako (head fit); height 22.5 cm (📜)
SQ = 0.250                                  # side of the square top (📜 "szerokosci bokow 25 cm")
BODY_FLARE = 1.06                           # felt body widens 6 % below the square part (🔶)
Z_SQ = 0.55                                 # the square part starts at 55 % of the height (🔶, Knoetel)
BAND_BOT = 0.020                            # leather band at the bottom (🔶)
VISOR_LEN, VISOR_DROP = 0.055, math.radians(38)
COCK_R = 0.026
PLUME_V = dict(H=0.20, R=0.032, feather_len=0.040, rings=26, per_ring=14, estilo="v4")   # voltigeur tuft (🔶 size)
DEPTH_RATIO, TILT = shako_fit.DEPTH_RATIO, shako_fit.TILT
WALL, CLEAR = shako_fit.WALL, shako_fit.CLEAR
N = 96                                      # multiple of 4: vertices on the four corners of the top

F = shako_fit.compute(SAMPLES)
base_hw = max(SPEC_BASE_W / 2, F["head_hw"] + WALL + CLEAR)
k = base_hw / (SPEC_BASE_W / 2)
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
H = SPEC_H * k
H_BASE = H
A_SQ = SQ * k / math.sqrt(2)                # centre -> corner of the top square
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')
print(f"FIT k={k:.4f} H={H:.3f} base={2*base_hw:.3f}x{2*base_hd:.3f} top square side {SQ*k:.3f} (diagonal {2*A_SQ:.3f})")


def r_ell(theta, z):
    f = 1 + (BODY_FLARE - 1) * min(1.0, z / (H * Z_SQ))
    a, b = base_hw * f, base_hd * f
    return 1.0 / math.sqrt((math.sin(theta) / a) ** 2 + (math.cos(theta) / b) ** 2)


def r_sq(theta):
    return A_SQ / (abs(math.sin(theta)) + abs(math.cos(theta)))     # square with a corner at theta = 0 (front)


def blend(z):
    t = min(1.0, max(0.0, (z / H - Z_SQ) / (1 - Z_SQ)))
    return t * t * (3 - 2 * t)


def R(theta, z):
    b = blend(z)
    return (1 - b) * r_ell(theta, z) + b * r_sq(theta)


def ry(z): return R(0.0, z)                 # front radius: arc length -> angle near the front (traced plates)
def rx(z): return R(math.pi / 2, z)
def P(theta, z, off=0.0):
    """Czapka-local point; theta = 0 is the FRONT (-Y), +90 deg the wearer's left (+X)."""
    r = R(theta, z) + off
    return Vector((r * math.sin(theta), -r * math.cos(theta), z))
def wall_n(theta, z):
    e = 1e-4
    dt = P(theta + e, z) - P(theta - e, z)
    dz = P(theta, min(H, z + e)) - P(theta, max(0.0, z - e))
    n = dt.cross(dz).normalized()
    out = Vector((math.sin(theta), -math.cos(theta), 0))
    return n if n.dot(out) > 0 else -n


ATLAS = None                                # UV "arte" is in atlas pixels of polandINF (texturizar_aliados.py atlas=)
OPT = dict(x.split("=", 1) for x in args[3:] if "=" in x)
PL_DIR = os.path.abspath(OPT.get("dir", "."))
PLATES = {"aguia": os.path.join(PL_DIR, "placa_aguia_varsovia.json"), "numero": os.path.join(PL_DIR, "placa_numero_varsovia.json")}
ATLAS_PX = 4096
ROSETTE_BOX = (94, 2611, 160, 2677)                # fusilier star on the chin-strap boss (polandINF c0 r5)
COL = dict(feltro=(0.015, 0.015, 0.016), couro=(0.03, 0.025, 0.02), latao=(0.70, 0.50, 0.16), ganse=(0.55, 0.54, 0.50),
           vermelho=(0.55, 0.03, 0.03), amarelo=(0.80, 0.62, 0.06), verde=(0.03, 0.20, 0.06),
           branco=(0.82, 0.82, 0.80), azul=(0.04, 0.08, 0.35), verde_esc=(0.02, 0.15, 0.05),
           ouro=(0.85, 0.62, 0.20), preto=(0.02, 0.02, 0.02), prata=(0.72, 0.72, 0.70),
           couro_marrom=(0.05, 0.028, 0.014), forro=(0.33, 0.29, 0.22))
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


# ---------------------------------------------------------------- one czapka
MM_PX = 0.00079                                 # metres per atlas pixel of the plate art (🔶)


def czapka(tag, x_off, top, boss_art):
    root = bpy.data.objects.new(f"PL_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    # body: felt wall with thickness; soft inward dents on the round part (never on the square part: crisp edges)
    bm = bmesh.new()
    zs = [H * i / 16 for i in range(17)]
    rnd_f = random.Random(sum(map(ord, tag)) + 11)
    ph1, ph2 = rnd_f.uniform(0, 6.3), rnd_f.uniform(0, 6.3)

    def dent(th, z):
        if z < BAND_BOT + 0.004 or z > H * Z_SQ:
            return 0.0
        w = math.sin(math.pi * (z - BAND_BOT - 0.004) / (H * Z_SQ - BAND_BOT - 0.004))
        return -0.0010 * w * (0.5 + 0.5 * math.sin(3 * th + ph1)) * (0.6 + 0.4 * math.sin(7 * th - 5 * z / H + ph2))
    outer = [[bm.verts.new(P(2 * math.pi * i / N, z, dent(2 * math.pi * i / N, z))) for i in range(N)] for z in zs]
    # inner wall and lining follow every row of the outer wall: with few rows the straight segments cut through the
    # flare of the square part and showed outside (first blockout render, 2026-10-18)
    inner = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL)) for i in range(N)] for z in zs[:-1] + [H - 0.006]]
    grid(bm, outer); grid(bm, [inner[0], outer[0]]); grid(bm, inner[::-1])
    grid(bm, [inner[-1], [bm.verts.new(P(2 * math.pi * i / N, H - 0.003, -WALL)) for i in range(N)]])
    finish(bm, f"{tag}_corpo", "feltro", root)
    # square top: black cloth, flat, with a rolled seam on its edge (the 4 corners stand out: "rogata")
    bm = bmesh.new()
    rim = [bm.verts.new(P(2 * math.pi * i / N, H, 0.0004)) for i in range(N)]
    seam = [bm.verts.new(P(2 * math.pi * i / N, H + 0.0015, -0.003)) for i in range(N)]
    rings_t = [rim, seam]
    for f_ in (0.8, 0.5, 0.2):
        rings_t.append([bm.verts.new(Vector((P(2 * math.pi * i / N, H).x * f_, P(2 * math.pi * i / N, H).y * f_,
                                             H - 0.002 * (1 - f_ ** 2)))) for i in range(N)])
    grid(bm, rings_t)
    cap_ring(bm, rings_t[-1], Vector((0, 0, H - 0.002)))
    finish(bm, f"{tag}_copa", "feltro", root)          # "copa": cloth kind in the texturizer
    # inside: sweatband and lining
    bm = bmesh.new()
    rows_s = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.020, 0.040, 0.057)]
    grid(bm, rows_s[::-1])
    finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    bm = bmesh.new()
    rows_l = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0012)) for i in range(N)] for z in [0.055] + [z for z in zs if 0.06 < z < H - 0.008] + [H - 0.008]]
    grid(bm, rows_l[::-1])
    cap_ring(bm, rows_l[-1][::-1], Vector((0, 0, H - 0.006)))
    finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    lathe_band(f"{tag}_faixa_baixo", 0.0, BAND_BOT, 0.0016, "couro", root)
    # leather peak edged with yellow metal (📜 "daszek okuty zolta metalowa obwodka")
    bm = bmesh.new()
    arc = [math.radians(-80 + 160 * i / 48) for i in range(49)]
    def vrow(off_len, dz):
        out = []
        for a in arc:
            n = wall_n(a, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a) / math.radians(80)) ** 4
            out.append(P(a, 0.004, 0.002) + n * off_len * w * math.cos(VISOR_DROP) + Vector((0, 0, -off_len * w * math.sin(VISOR_DROP) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in vrow(0.0, 0.0)], [bm.verts.new(p) for p in vrow(VISOR_LEN, 0.0)],
            [bm.verts.new(p) for p in vrow(VISOR_LEN, -0.003)], [bm.verts.new(p) for p in vrow(0.0, -0.003)]]
    grid(bm, rows, closed_u=False, closed_v=True)
    for r in (0, 48):
        bm.faces.new((rows[0][r], rows[1][r], rows[2][r], rows[3][r]))
    edge = [(rows[1][i].co + rows[2][i].co) / 2 for i in range(len(arc))]
    finish(bm, f"{tag}_pala", "couro", root)
    sweep(f"{tag}_pala_debrum", edge, 0.0021, 0, "latao", root, round_=True, segs=6)
    # yellow plate with the regiment number, the white-metal eagle above it (📜; outlines from the mod art 🎮)
    pw = 131.4 * MM_PX; ph = 52.5 * MM_PX
    z_p0 = BAND_BOT + 0.006
    traced_plate(f"{tag}_placa_numero", PLATES["numero"], z_p0, z_p0 + ph, pw, 0.0018, "latao", root)
    ew = 98.0 * MM_PX; eh = 81.5 * MM_PX
    z_e0 = z_p0 + ph + 0.003
    traced_plate(f"{tag}_placa_aguia", PLATES["aguia"], z_e0, z_e0 + eh, ew, 0.0022, "prata", root)
    # white cockade on the front of the square part, above the eagle (📜 white; place 🔶 Knoetel)
    zc = z_e0 + eh + COCK_R + 0.006
    c0 = P(0, zc, 0.0018); nc = wall_n(0, zc)
    pleated(f"{tag}_cocar_fora", c0, nc, COCK_R * 0.55, COCK_R, 0.003, 36, "branco", root)
    pleated(f"{tag}_cocar_dentro", c0 + nc * 0.0012, nc, COCK_R * 0.22, COCK_R * 0.58, 0.003, 26, "branco", root)
    disc(f"{tag}_cocar_centro", c0 + nc * 0.0034, nc, COCK_R * 0.24, 0.0015, "branco", root, segs=32)
    # top ornament on the front corner
    front_top = P(0, H, -0.012)
    if top[0] == "lentilha":                     # fusiliers: black pompom (📜), lentil shape as the French (🔶)
        c = front_top + Vector((0, -0.002, 0.024))
        woolly(lathe_obj(f"{tag}_pompom", [(-0.010, 0.002), (-0.008, 0.019), (-0.004, 0.027), (0.0, 0.029), (0.004, 0.027), (0.008, 0.019), (0.010, 0.002)],
                         c, top[1], root, axis=Vector((0, -1, 0)), segs=48), amp=0.0008)
    else:                                         # voltigeurs: yellow-green tuft ("kita") in a brass socket
        lathe_obj(f"{tag}_tulipa", [(-0.010, 0.004), (0.0, 0.006), (0.010, 0.009)], front_top + Vector((0, 0, 0.002)), "latao", root)
        bm = bmesh.new()
        by = plumet(bm, front_top + Vector((0, 0, 0.010)), colours=top[1], seed=sum(map(ord, tag)), **PLUME_V)
        finish(bm, f"{tag}_plumet", None, root, by_colour=by, keep_normals=True, plume=True)
    # yellow chin strap (scales) with the star boss (📜; the voltigeur bugle is not in the mod art: plain boss 🔶)
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, F["head_cy"] - F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        ro = P(sgn * math.radians(92), 0.024, 0.0035)
        nro = wall_n(sgn * math.radians(92), 0.024)
        if boss_art:
            art_disc(f"{tag}_roseta_{'E' if sgn > 0 else 'D'}", ro, nro, 0.019, 0.0035, ROSETTE_BOX, "latao", root, segs=48)
        else:
            disc(f"{tag}_botao_{'E' if sgn > 0 else 'D'}", ro, nro, 0.019, 0.0035, "latao", root, segs=48)
        ro_w = root.matrix_world @ ro
        z_mid = (ro_w.z + chin_w.z) / 2
        hz = (F["z_head_top"] - 0.57) / 2 - 0.004; zc_h = (F["z_head_top"] + 0.57) / 2
        half_w = (F["head_hw"] - 0.006) * math.sqrt(max(0.0, 1 - ((z_mid - zc_h) / hz) ** 2))
        mid = inv @ Vector((x_off + sgn * (half_w + 0.010), F["head_cy"] - 0.012, z_mid))
        path = catmull([ro, mid, Vector((sgn * 0.035, chin.y, chin.z + 0.006)), Vector((0.0, chin.y, chin.z))], 6)
        nrm = [Vector((p.x, p.y, 0)).normalized() for p in path]
        chinscales(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, nrm, "latao", root)
    # white cords (📜 "kordony biale"): festoon round the BACK under the square part (the front stays clear for the
    # plate and the eagle; route 🔶), raquette and tassels on the wearer's right
    zf = H * Z_SQ - 0.006
    fest = catmull([P(math.radians(-100), zf, 0.006), P(math.radians(-150), zf - 0.030, 0.007), P(math.pi, zf - 0.045, 0.008),
                    P(math.radians(150), zf - 0.030, 0.007), P(math.radians(100), zf, 0.006)], 8)
    twisted(f"{tag}_cordao", fest, 0.0033, "branco", root)
    side = P(math.radians(-100), zf - 0.040, 0.008)
    hang = [P(math.radians(-100), zf, 0.006), side, side + Vector((0, 0, -0.06))]
    twisted(f"{tag}_cordao_lado", catmull(hang, 6), 0.0033, "branco", root)
    n = wall_n(math.radians(-100), 0.05); n.z = 0; n.normalize()
    rq = side + Vector((0, 0, -0.08)) + n * 0.004
    lathe_obj(f"{tag}_raquete", [(-0.032, 0.002), (-0.023, 0.013), (0.0, 0.016), (0.023, 0.013), (0.032, 0.002)], rq, "branco", root, axis=Vector((0, 0, 1)), segs=12)
    for dx in (-0.011, 0.011):
        t0 = rq + Vector((dx * n.y, -dx * n.x, -0.036))
        fringe_tassel(f"{tag}_borla_{'a' if dx < 0 else 'b'}", t0, "branco", root, seed=7 if dx < 0 else 8)
    return root


VARIANTS = [("fuzileiro", ("lentilha", "preto"), True),
            ("voltigeur", ("plumet", [(0.0, "verde"), (0.55, "amarelo")]), False)]
SPACING = 0.50
roots = [czapka(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

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

bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:12s} pecas {len(obs):2d}  triangulos {tris:5d}  topo {zmax:.3f} m (cabeca {F['z_head_top']:.3f})")
pts = [P(2 * math.pi * i / N, H) for i in range(N)]
print(f"TOPO quadrado: lado {(pts[0] - pts[N // 4]).length:.3f} m, diagonal {(pts[0] - pts[N // 2]).length:.3f} m; altura {H:.3f} m")

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
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_czapka_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_frente", (mid_x, -3.0, zc), (mid_x, 0, zc), ortho=SPACING * len(VARIANTS) + 0.2, res=(1600, 900))
shot("fila_tres_quartos", (mid_x + 1.3, -2.8, zc + 0.6), (mid_x, 0, zc - 0.02), lens=45, res=(1800, 900))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
for j, r in enumerate(roots):
    for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
        o.hide_render = j != 0
shot("fuzileiro_lado", (-2.0, F["head_cy"], zc), (0.0, F["head_cy"], zc), ortho=0.75, res=(900, 1000))
shot("fuzileiro_perto", (0.35, -0.75, zc + 0.15), (0.0, F["head_cy"] - 0.05, zc + 0.05), lens=55, res=(1000, 1000))
shot("fuzileiro_cima", (0.0, F["head_cy"] - 0.01, zc + 2.0), (0.0, F["head_cy"], zc), ortho=0.45, res=(900, 900))
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
