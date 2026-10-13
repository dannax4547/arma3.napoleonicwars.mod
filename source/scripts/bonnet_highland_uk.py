# Highland FEATHER BONNET (92nd Gordon Highlanders and the second, unidentified Highland variant), spec
# docs/specs/uk_1812.md section 3.3: worn by the 73rd, 79th and 92nd at Waterloo (S8, 🔶); diced band of three rows
# red / white / green (S8 forum 🔶, and the mod art britainINFb c7 r4 🎮); black ostrich feathers over a knitted blue
# bonnet; black cockade on the left side with a hackle (no source read for its colour: the line tuft convention,
# white with the bottom third red, H1/H2 🔶). No peak (none in the sources read).
# Geometry, like the Old Guard bearskin (blockout_bonnet_guarda.py, left untouched): every feather frond is real
# geometry (narrow double-sided ribbons with UV + 'tint', baked on fur tiles by texturizar_shako_uk.py kind "pena"),
# rooted on an ellipsoid feather mass over the bonnet, falling by gravity along it; the mass leans to the wearer's RIGHT
# and the fronds on the right side hang down to the ear (mod art: tails on one side 🎮). The diced band carries the
# mod art (UV layer "arte" on britainINFb, texturizar_shako_uk.py atlas=britainINFb_diffuse.png).
#   blender -b --factory-startup --python bonnet_highland_uk.py -- <Samples Test_Character_01 dir> <out.blend> <render dir>
# Helper functions copied from blockout_shako_uk.py (themselves from blockout_shako_fr.py).
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
DEPTH_RATIO, TILT = shako_fit.DEPTH_RATIO, shako_fit.TILT
WALL, CLEAR = shako_fit.WALL, shako_fit.CLEAR
N = 96
SPEC_BASE_W = 0.180
F = shako_fit.compute(SAMPLES)
base_hw = max(SPEC_BASE_W / 2, F["head_hw"] + WALL + CLEAR)
k = base_hw / (SPEC_BASE_W / 2)
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
H = 0.040                                                  # diced band height (rx/ry/P of the helpers read H)
top_hw, top_hd = base_hw, base_hd
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')


def rx(z): return base_hw
def ry(z): return base_hd
def P(theta, z, off=0.0):
    return Vector(((rx(z) + off) * math.sin(theta), -(ry(z) + off) * math.cos(theta), z))
def wall_n(theta, z):
    return Vector((math.sin(theta) / rx(z), -math.cos(theta) / ry(z), 0)).normalized()


ATLAS_PX = 4096
DICE_BOX = (3584, 2358, 3710, 2420)                        # britainINFb c7 r4: 6 columns of the 3-row dicing
COL = dict(feltro=(0.015, 0.015, 0.016), couro=(0.03, 0.025, 0.02), latao=(0.70, 0.50, 0.16),
           vermelho=(0.55, 0.03, 0.03), branco=(0.82, 0.82, 0.80), preto=(0.02, 0.02, 0.02), estanho=(0.62, 0.62, 0.60),
           azul_pano=(0.010, 0.016, 0.040), pelo=(0.011, 0.009, 0.008), couro_marrom=(0.05, 0.028, 0.014),
           forro=(0.33, 0.29, 0.22), verde=(0.03, 0.20, 0.06), verde_esc=(0.02, 0.12, 0.04))
MATS = {}


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name in ("latao", "ouro", "prata", "estanho") else 0.7
        b.inputs["Metallic"].default_value = 1.0 if name in ("latao", "ouro", "prata", "estanho") else 0.0
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


def traced_plate(name, json_path, z_bot, z_top, max_w, depth, colour, parent, off=0.0008):
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
        vm[v.index] = (bm.verts.new(P(lx / ry(z), z, off + lz)), art_uv(X0 + v.co.x, Y0 - v.co.y))
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






# ---------------------------------------------------------------- Highland feather bonnet
def egg(L, R, a0, a1, n=14):
    out = []
    for i in range(n + 1):
        s = a0 + (a1 - a0) * i / n
        r = R * max(0.0, math.sin(math.pi * s)) ** 0.75 * (1.12 - 0.30 * s)
        out.append((s * L, max(r, 0.0008)))
    return out


def hackle(tag, root, base, axis, L, R, colours):
    axis = axis.normalized()
    bounds = [c[0] for c in colours] + [1.0]
    for i, (f0, cname) in enumerate(colours):
        ob = lathe_obj(f"{tag}_pompom_{i}", egg(L, R, f0, bounds[i + 1]), base, cname, root, axis=axis, segs=36)
        woolly(ob, amp=0.0010, seed=7 + i)


def cockade(tag, root, centre, normal, r=0.022):
    pleated(f"{tag}_cocar", centre, normal, r * 0.35, r, 0.0026, 30, "preto", root)
    lathe_obj(f"{tag}_botao_cocar", [(0.0, 0.0005), (0.0, 0.0060), (0.0014, 0.0056), (0.0027, 0.0038), (0.0031, 0.0005)],
              centre + normal * 0.0030, "estanho", root, axis=normal, segs=16)


MASS_A, MASS_B, MASS_C = 1.30, 1.24, 0.120               # feather mass: x, y factors of the band, height semi-axis (m)
LEAN = 0.018                                              # top of the mass shifted to the wearer's right (-X)
PHI0 = -math.acos(min(0.999, (base_hw + 0.004) / (base_hw * MASS_A)))
ZC = H * 0.80 - MASS_C * math.sin(PHI0)


def S(th, s, off=0.0):
    """Feather mass surface; s 0 (on the band) .. 1 (top); lumpy so it is not an ellipsoid of revolution."""
    phi = PHI0 + (math.pi / 2 - PHI0) * s
    lump = 0.004 * math.sin(3 * th + 1.3) * math.sin(5 * s + 0.4) + 0.003 * math.sin(7 * th - 4 * s)
    ca = math.cos(phi)
    x = (base_hw * MASS_A + lump + off) * ca * math.sin(th) - LEAN * max(0.0, math.sin(phi))
    y = -(base_hd * MASS_B + lump + off) * ca * math.cos(th)
    z = ZC + (MASS_C + off) * math.sin(phi)
    return Vector((x, y, z))


def Sn(th, s, e=1e-3):
    a_ = S(th + e, s) - S(th - e, s)
    b_ = S(th, min(1.0, s + e)) - S(th, max(0.0, s - e))
    n = a_.cross(b_)
    if n.length < 1e-9:
        return Vector((0, 0, 1))
    n.normalize()
    c = S(th, s) - Vector((0, 0, ZC))
    return n if n.dot(c) > 0 else -n


def band(tag, root):
    """Diced band (UV layer "arte" = 8 repeats of the 6-column dicing of the mod art round the head)."""
    bm = bmesh.new()
    arte = bm.loops.layers.uv.new("arte")
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, o)) for i in range(N)] for z, o in ((0.0, 0.0005), (0.0, 0.0022), (H, 0.0022), (H, 0.0005))]
    x0, y0, x1, y1 = DICE_BOX
    REP = 8
    per = N // REP
    for j in range(3):
        for i in range(N):
            f = bm.faces.new((rows[j][i], rows[j][(i + 1) % N], rows[j + 1][(i + 1) % N], rows[j + 1][i]))
            k0 = (i % per) / per; k1 = (i % per + 1) / per
            if j == 1:                                    # outer face: the dicing
                uvs = ((x0 + (x1 - x0) * k0, y1), (x0 + (x1 - x0) * k1, y1), (x0 + (x1 - x0) * k1, y0), (x0 + (x1 - x0) * k0, y0))
            else:                                         # edges: the dark top/bottom border of the strip
                uvs = ((x0, y0 + 1), (x0 + 2, y0 + 1), (x0 + 2, y0 + 2), (x0, y0 + 2))
            for l, (px, py) in zip(f.loops, uvs):
                l[arte].uv = (px / ATLAS_PX, 1.0 - py / ATLAS_PX)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    finish(bm, f"{tag}_xadrez", "vermelho", root, keep_normals=True)
    # knitted bonnet inside the band (seen from below), dark blue
    bm = bmesh.new()
    rows_i = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL)) for i in range(N)] for z in (0.0, H, H + 0.04)]
    grid(bm, rows_i[::-1])
    cap_ring(bm, rows_i[-1][::-1], Vector((0, 0, H + 0.05)))
    grid(bm, [rows_i[0], [bm.verts.new(P(2 * math.pi * i / N, 0.0, 0.0006)) for i in range(N)]])
    finish(bm, f"{tag}_copa", "azul_pano", root, keep_normals=True)


def shell(tag, root):
    bm = bmesh.new()
    NS = 30
    rings = [[bm.verts.new(S(2 * math.pi * i / N - math.pi, j / NS)) for i in range(N)] for j in range(NS)]
    grid(bm, rings)
    cap_ring(bm, rings[-1], S(0, 1.0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    finish(bm, f"{tag}_pele_corpo", "pelo", root)


def fronds(tag, root, seed=11):
    """Ostrich feather fronds (v2, 2026-10-13: the first try fell over the face like a mop). The fronds now lie close
    on the mass as a rounded dome: wide, soft, little lift; every frond is shortened until its whole length stays above
    the diced band (H + 5 mm), so the band and the forehead stay clear. Only on the wearer's RIGHT side a few long
    TAILS hang below the band down toward the shoulder (mod art britainINFb c7 r4 shows the feathers swept to one
    side, 🎮)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    tint = bm.faces.layers.float.new("tint")
    count = {"pena": 0, "cauda": 0}
    ZMIN = H + 0.005

    def path(th, s, L, lift, drop, ang):
        p0 = S(th, s)
        n = Sn(th, s)
        g = Vector((0, 0, -1)) - n * (-n.z)
        if g.length < 0.15:
            g = Vector((-1.0, 0.0, 0.0))                  # on the crown: swept toward the wearer's right (-X)
        g.normalize()
        side = n.cross(g).normalized()
        d = (g * math.cos(ang) + side * math.sin(ang)).normalized()
        st = ((0.0, 0.55), (0.25, 1.0), (0.5, 0.95), (0.75, 0.70), (1.0, 0.18))
        pts = []
        for t, wf in st:
            rise = lift * (4.0 * t * (1.0 - t)) - 0.002 * t * t
            dd = (d * (1.0 - 0.45 * t) + g * (0.45 * t)).normalized()
            pts.append((p0 + n * (0.002 + rise) + dd * (L * t) + Vector((0, 0, -drop * t * t)), wf, t))
        return pts, n, d

    def emit(pts, n, d, W):
        sd = n.cross(d).normalized()
        sh = rnd.uniform(0.0, 1.0)
        rows = []
        for p, wf, t in pts:
            hw = W * wf / 2
            cup = n * (0.30 * hw)
            rows.append((bm.verts.new(p - sd * hw - cup), bm.verts.new(p + n * 0.0015), bm.verts.new(p + sd * hw - cup), t))
        for kk in range(len(rows) - 1):
            (a0, m0, b0, t0), (a1, m1, b1, t1) = rows[kk], rows[kk + 1]
            for (x0, x1, y1, y0, u0, u1) in ((a0, m0, m1, a1, 0.0, 0.5), (m0, b0, b1, m1, 0.5, 1.0)):
                f = bm.faces.new((x0, x1, y1, y0))
                for l, uv in zip(f.loops, ((u0, t0), (u1, t0), (u1, t1), (u0, t1))):
                    l[uvl].uv = uv
                f[tint] = sh; f.smooth = True
                f.normal_update()
                if f.normal.dot(n) < 0:
                    f.normal_flip()

    for layer, n_th, n_rows in (("base", 40, 14), ("cima", 36, 15)):
        for j in range(n_rows):
            for i in range(n_th):
                s = (j + rnd.uniform(0.05, 0.95)) / n_rows * 0.98
                th = 2 * math.pi * (i + rnd.uniform(0, 1) + 0.5 * (j % 2)) / n_th - math.pi
                if layer == "base":
                    L, W, lift = rnd.uniform(0.040, 0.060), rnd.uniform(0.026, 0.036), rnd.uniform(0.001, 0.003)
                else:
                    L, W, lift = rnd.uniform(0.070, 0.105), rnd.uniform(0.030, 0.044), rnd.uniform(0.003, 0.008)
                ang = rnd.uniform(-0.35, 0.35)
                while L >= 0.025:                         # shorten until the frond stays above the band
                    pts, n, d = path(th, s, L, lift, 0.0, ang)
                    if min(p.z for p, _, _ in pts) >= ZMIN:
                        break
                    L *= 0.85
                if L < 0.025:
                    continue
                emit(pts, n, d, W)
                count["pena"] += 1
    # tails on the wearer's right side (theta -150 .. -60 deg), rooted on the lower third of the mass
    for i in range(9):
        th = math.radians(-150 + 90 * (i + rnd.uniform(0.2, 0.8)) / 9)
        s = rnd.uniform(0.18, 0.35)
        L = rnd.uniform(0.16, 0.22)
        pts, n, d = path(th, s, L, rnd.uniform(0.006, 0.012), rnd.uniform(0.02, 0.05), rnd.uniform(-0.2, 0.2))
        emit(pts, n, d, rnd.uniform(0.034, 0.046))
        count["cauda"] += 1
    finish(bm, f"{tag}_pelo", "pelo", root, keep_normals=True)
    return f"{count['pena']} penas + {count['cauda']} caudas"


def feather_bonnet(tag, x_off, hackle_cols):
    root = bpy.data.objects.new(f"UK_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    band(tag, root)
    shell(tag, root)
    n = fronds(tag, root)
    # black cockade on the left side ON the diced band; the hackle rises from behind it, outside the feathers, and
    # stands above the mass
    th_c = math.radians(72)
    c0 = P(th_c, H * 0.55, 0.0045)
    nc = wall_n(th_c, H * 0.55)
    cockade(tag, root, c0, nc)
    hackle(tag, root, c0 + nc * 0.030 + Vector((0, 0, 0.020)), Vector((0, 0, 1)) + nc * 0.30, 0.150, 0.022, hackle_cols)
    print(f"BONNET {tag}: {n} plumas; massa {2 * base_hw * MASS_A:.3f} x {2 * base_hd * MASS_B:.3f} m, topo {ZC + MASS_C:.3f} m acima da borda")
    return root


VARIANTS = [("bonnet_highland", [(0.0, "vermelho"), (1 / 3, "branco")])]
SPACING = 0.42
roots = [feather_bonnet(t, i * SPACING, c) for i, (t, c) in enumerate(VARIANTS)]

hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
hme.materials.append(skin)
heads = []
for i in range(len(VARIANTS)):
    h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    scene.collection.objects.link(h); heads.append(h)
bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    zmin = min((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:22s} pecas {len(obs):2d}  triangulos {tris:6d}  {zmin:.3f}..{zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
os.makedirs(RENDER_DIR, exist_ok=True)
zc = (ROOT @ Vector((0, 0, 0.10))).z + 0.03
for name, loc in (("frente", (0, -2.0, zc)), ("lado_direito", (-2.0, F["head_cy"], zc)), ("tres_quartos", (-1.2, -1.6, zc + 0.5))):
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 0.55
    cam.location = loc
    cam.rotation_euler = (Vector((0, F["head_cy"], zc)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 900, 1000
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_uk_bonnet_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
