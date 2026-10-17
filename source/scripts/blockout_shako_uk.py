# British infantry caps 1800-1815 (Phase 3 blockout + production detail, like blockout_shako_fr.py v4): the 1812
# "Belgic" cap and the "stovepipe" cap (1800/1806), one per company distinction. Fitted on the official Arma 3 Samples
# head band (shako_fit.py, read-only Samples), parts with flat identification colours; texturizar_shako_uk.py joins
# and bakes them. Spec: docs/specs/uk_1812.md sections 2.2, 3.1, 3.2, 8 (sources H1, H2, W1, W2, AR, F1).
#   blender -b --factory-startup --python blockout_shako_uk.py -- <Samples Test_Character_01 dir> <out.blend> <render dir>
# The helper functions (bands, sweeps, lathes, traced plate, tassels, twisted cords, pleated cockade) are copied from
# blockout_shako_fr.py, which is left untouched. Measures (spec section 8, x the fit scale k ~1.03):
#   Belgic: felt body 165 mm (6 1/2"), cylindrical; tombstone FALSE FRONT 210 mm (8 1/4") bound with black worsted
#           tape; plate = crowned baroque shield with GR TRACED from the mod art (britainINF c2 r5); black leather
#           cockade on the LEFT side at the foot of the worsted tuft; white (or green) cords from the tuft's foot across
#           the front under the plate, ending on the right side in tassels (H1)
#   stovepipe: 178 mm (8" or 6 3/4" in the sources: the mean), tapering 4 mm in radius to the top (1806 pattern, W2);
#           brass plate 6 x 4" (F1) TRACED from the art (britainINF c3 r4: GR, Garter, lion, trophy; left half mirrored);
#           cockade above the plate, tuft of ~6" (152 mm) in a leather socket at the top front (H2)
#   tufts (H1/H2): battalion white with the bottom third red, grenadiers white, light companies and Rifles dark green
#   Rifles / light: bugle badge instead of the plate (H2; bugle traced from britainINF c3 r4), Rifles dark green cords
#   28th (North Gloucestershire): stovepipe with the regimental number "28" at the bottom of the back (W2, S5)
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
# absolute paths: Blender resolves a relative render path against the drive root when no .blend is open
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def main_root():
    """Project root with the heavy files (work/, source/models). Scripts may run from a git worktree under
    <root>/.claude/worktrees/<name>, which has no work/ folder: walk up to the folder that holds .claude."""
    d = os.path.dirname(os.path.abspath(__file__))
    parts = d.replace("\\", "/").split("/")
    if ".claude" in parts:
        return "/".join(parts[:parts.index(".claude")])
    return os.path.abspath(os.path.join(d, "..", ".."))


ROOT_DIR = main_root()
# ---------------------------------------------------------------- proportions (spec section 8)
SPEC_BASE_W = 0.180                                     # same head band fit as the Prussian / French shakos
BELGIC_H, BELGIC_FRONT_H = 0.165, 0.210
BELGIC_TH = math.radians(74)                            # half-width of the false front around the body
STOVE_H, STOVE_TAPER = 0.178, 0.004
VISOR_LEN, VISOR_DROP = 0.055, math.radians(38)
TAPE = 0.010                                            # black worsted tape binding (spec: "bound in black tape")
FF_OFF, FF_T = 0.0016, 0.0022                           # false front: gap to the body wall, thickness
DEPTH_RATIO, TILT = shako_fit.DEPTH_RATIO, shako_fit.TILT
WALL, CLEAR = shako_fit.WALL, shako_fit.CLEAR
N = 96

F = shako_fit.compute(SAMPLES)                           # head band of the official cap (read-only Samples)
base_hw = max(SPEC_BASE_W / 2, F["head_hw"] + WALL + CLEAR)
k = base_hw / (SPEC_BASE_W / 2)
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
H = BELGIC_H * k                                        # set per cap by shako(); rx/ry/P read these globals
top_hw, top_hd = base_hw, base_hd
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')
print(f"FIT k={k:.4f} base={2*base_hw:.3f}x{2*base_hd:.3f} Belgic H={BELGIC_H * k:.3f} frente={BELGIC_FRONT_H * k:.3f} "
      f"stovepipe H={STOVE_H * k:.3f}")


def rx(z): return base_hw + (top_hw - base_hw) * min(z, H) / H
def ry(z): return base_hd + (top_hd - base_hd) * min(z, H) / H
def P(theta, z, off=0.0):
    """Cap-local point; theta = 0 is the FRONT (-Y), +90 deg the wearer's left (+X)."""
    return Vector(((rx(z) + off) * math.sin(theta), -(ry(z) + off) * math.cos(theta), z))
def wall_n(theta, z):
    n = Vector((math.sin(theta) / rx(z), -math.cos(theta) / ry(z), 0)).normalized()
    return (n - Vector((0, 0, (top_hw - base_hw) / H))).normalized()


ATLAS = os.path.join(ROOT_DIR, "work", "ntw", "britain", "britainINF_diffuse.png")
SHK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "shakos", "hcl_shako_uk")
PLATES = {"belgic": os.path.abspath(os.path.join(SHK_DIR, "placa_belgic.json")),
          "stovepipe": os.path.abspath(os.path.join(SHK_DIR, "placa_stovepipe.json")),
          "corneta": os.path.abspath(os.path.join(SHK_DIR, "corneta.json"))}
ATLAS_PX = 4096
COL = dict(feltro=(0.015, 0.015, 0.016), couro=(0.03, 0.025, 0.02), latao=(0.70, 0.50, 0.16),
           vermelho=(0.55, 0.03, 0.03), verde=(0.03, 0.20, 0.06), branco=(0.82, 0.82, 0.80),
           verde_esc=(0.02, 0.12, 0.04), preto=(0.02, 0.02, 0.02), estanho=(0.62, 0.62, 0.60),
           couro_marrom=(0.05, 0.028, 0.014), forro=(0.33, 0.29, 0.22))
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




# ---------------------------------------------------------------- UK caps
def body(tag, root, crown_colour):
    """Felt wall with thickness and soft inward dents, crown, sweatband and lining (as in the French v4 shako)."""
    bm = bmesh.new()
    zs = [H * i / 12 for i in range(13)]
    rnd_f = random.Random(sum(map(ord, tag)) + 11)
    ph1, ph2 = rnd_f.uniform(0, 6.3), rnd_f.uniform(0, 6.3)

    def dent(th, z):
        if z < TAPE + 0.004 or z > H - TAPE - 0.004:
            return 0.0
        w = math.sin(math.pi * (z - TAPE - 0.004) / (H - 2 * TAPE - 0.008))
        return -0.0010 * w * (0.5 + 0.5 * math.sin(3 * th + ph1)) * (0.6 + 0.4 * math.sin(7 * th - 5 * z / H + ph2))
    outer = [[bm.verts.new(P(2 * math.pi * i / N, z, dent(2 * math.pi * i / N, z))) for i in range(N)] for z in zs]
    inner = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL)) for i in range(N)] for z in (0.0, H * 0.33, H * 0.66, H - 0.008)]
    grid(bm, outer); grid(bm, [inner[0], outer[0]]); grid(bm, inner[::-1])
    grid(bm, [inner[-1], [bm.verts.new(P(2 * math.pi * i / N, H - 0.004, -WALL)) for i in range(N)]])
    finish(bm, f"{tag}_corpo", "feltro", root)
    bm = bmesh.new()
    rim = [bm.verts.new(P(2 * math.pi * i / N, H, 0.0004)) for i in range(N)]
    seam = [bm.verts.new(P(2 * math.pi * i / N, H + 0.0012, -0.0025)) for i in range(N)]
    rings_t = [rim, seam]
    for f_ in (0.75, 0.45, 0.18):
        rings_t.append([bm.verts.new(Vector((rx(H) * f_ * math.sin(2 * math.pi * i / N), -ry(H) * f_ * math.cos(2 * math.pi * i / N),
                                             H - 0.003 * (1 - f_ ** 2)))) for i in range(N)])
    grid(bm, rings_t)
    cap_ring(bm, rings_t[-1], Vector((0, 0, H - 0.003)))
    finish(bm, f"{tag}_topo", crown_colour, root)
    bm = bmesh.new()
    rows_s = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.020, 0.040, 0.057)]
    grid(bm, rows_s[::-1])
    finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    bm = bmesh.new()
    rows_l = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0012)) for i in range(N)] for z in (0.055, H * 0.5, H - 0.006)]
    grid(bm, rows_l[::-1])
    cap_ring(bm, rows_l[-1][::-1], Vector((0, 0, H - 0.006)))
    finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    # black worsted tape binding round the bottom and the crown edge
    lathe_band(f"{tag}_faixa_baixo", 0.0, TAPE, 0.0014, "preto", root)
    lathe_band(f"{tag}_faixa_cima", H - TAPE * 0.6, H, 0.0014, "preto", root)


def visor(tag, root):
    bm = bmesh.new()
    arc = [math.radians(-82 + 164 * i / 48) for i in range(49)]

    def vrow(off_len, dz):
        out = []
        for a in arc:
            n = wall_n(a, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a) / math.radians(82)) ** 4
            out.append(P(a, 0.004, 0.002) + n * off_len * w * math.cos(VISOR_DROP) + Vector((0, 0, -off_len * w * math.sin(VISOR_DROP) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in vrow(0.0, 0.0)], [bm.verts.new(p) for p in vrow(VISOR_LEN, 0.0)],
            [bm.verts.new(p) for p in vrow(VISOR_LEN, -0.003)], [bm.verts.new(p) for p in vrow(0.0, -0.003)]]
    grid(bm, rows, closed_u=False, closed_v=True)
    for r in (0, 48):
        bm.faces.new((rows[0][r], rows[1][r], rows[2][r], rows[3][r]))
    edge = [(rows[1][i].co + rows[2][i].co) / 2 for i in range(len(arc))]
    finish(bm, f"{tag}_pala", "couro", root)
    sweep(f"{tag}_pala_debrum", edge, 0.0021, 0, "couro", root, round_=True, segs=6)


def egg(L, R, a0, a1, n=14):
    """Profile of the worsted tuft (egg, widest in its lower half) between fractions a0..a1 of its length."""
    out = []
    for i in range(n + 1):
        s = a0 + (a1 - a0) * i / n
        r = R * max(0.0, math.sin(math.pi * s)) ** 0.75 * (1.12 - 0.30 * s)
        out.append((s * L, max(r, 0.0008)))
    return out


def tuft(tag, root, base, axis, L, R, colours):
    """colours = [(from_fraction, colour), ...] bottom to top (battalion: red bottom third, white above)."""
    axis = axis.normalized()
    lathe_obj(f"{tag}_encaixe_couro", [(-0.012, 0.0075), (0.0, 0.0085), (0.006, 0.0070)], base, "couro", root, axis=axis, segs=16)
    bounds = [c[0] for c in colours] + [1.0]
    for i, (f0, cname) in enumerate(colours):
        prof = egg(L, R, f0, bounds[i + 1])
        ob = lathe_obj(f"{tag}_pompom_{i}", prof, base, cname, root, axis=axis, segs=40)
        woolly(ob, amp=0.0010, seed=7 + i)


def cockade(tag, root, centre, normal, r=0.021):
    pleated(f"{tag}_cocar", centre, normal, r * 0.35, r, 0.0026, 30, "preto", root)
    lathe_obj(f"{tag}_botao_cocar", [(0.0, 0.0005), (0.0, 0.0060), (0.0014, 0.0056), (0.0027, 0.0038), (0.0031, 0.0005)],
              centre + normal * 0.0030, "estanho", root, axis=normal, segs=16)


def cords(tag, root, path_pts, colour, hang_at, off):
    """Festoon across the front (twisted two-strand cord) and two tassels hanging on the wearer's right."""
    twisted(f"{tag}_cordao", catmull(path_pts, 8), 0.0030, colour, root)
    side = hang_at
    hang = [path_pts[-1], side, side + Vector((0, 0, -0.045))]
    twisted(f"{tag}_cordao_lado", catmull(hang, 6), 0.0030, colour, root)
    n = Vector((side.x, side.y, 0)).normalized()
    for dx in (-0.010, 0.010):
        t0 = side + Vector((dx * n.y, -dx * n.x, -0.050)) + n * 0.004
        fringe_tassel(f"{tag}_borla_{'a' if dx < 0 else 'b'}", t0, colour, root, r=0.008, length=0.030, seed=7 if dx < 0 else 8)


def number_badge(tag, root, text):
    """Regimental number in brass at the bottom of the back (28th Foot, 'back badge'), letters 22 mm high."""
    cu = bpy.data.curves.new(f"{tag}_numero_txt", "FONT")
    cu.body = text; cu.size = 0.026; cu.extrude = 0.0007; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.bevel_depth = 0.0003
    tob = bpy.data.objects.new(f"{tag}_numero_txt", cu); scene.collection.objects.link(tob)
    bpy.context.view_layer.update()
    me0 = bpy.data.meshes.new_from_object(tob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tob); bpy.data.curves.remove(cu)
    bm = bmesh.new(); bm.from_mesh(me0); bpy.data.meshes.remove(me0)
    zc = TAPE + 0.020
    for v in bm.verts:                                   # text x -> around the back, text y -> height, z -> out
        x, y, z = v.co
        th = math.pi + x / rx(zc)                        # theta = 180 deg is the back; text reads left to right
        v.co = P(th, zc + y, 0.0012 + z + 0.0007)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(bm, f"{tag}_numero_{text}", "latao", root, keep_normals=True)


def false_front(tag, root):
    """Belgic tombstone front: a felt slab on the front of the cylinder, rising to BELGIC_FRONT_H at the centre in a
    rounded arch, its sides at the body height; bound with black tape along its free edge."""
    HF = BELGIC_FRONT_H * k
    HS = H * 0.94
    NU, NV = 48, 26
    def ztop(th):
        return HF - (HF - HS) * (abs(th) / BELGIC_TH) ** 2.6
    bm = bmesh.new()
    ths = [BELGIC_TH * (2 * i / NU - 1) for i in range(NU + 1)]
    out_ = [[bm.verts.new(P(th, ztop(th) * j / NV, FF_OFF + FF_T)) for th in ths] for j in range(NV + 1)]
    in_ = [[bm.verts.new(P(th, ztop(th) * j / NV, FF_OFF)) for th in ths] for j in range(NV + 1)]
    grid(bm, out_, closed_u=False)
    grid(bm, [row[::-1] for row in in_], closed_u=False)
    for j in range(NV):                                   # side walls
        for i in (0, NU):
            bm.faces.new((out_[j][i], out_[j + 1][i], in_[j + 1][i], in_[j][i]))
    for i in range(NU):                                   # top wall
        bm.faces.new((out_[NV][i], out_[NV][i + 1], in_[NV][i + 1], in_[NV][i]))
    finish(bm, f"{tag}_frente", "feltro", root)
    edge = [P(-BELGIC_TH, z, FF_OFF + FF_T / 2) for z in np.linspace(TAPE, ztop(BELGIC_TH), 6)] + \
           [P(th, ztop(th), FF_OFF + FF_T / 2) for th in ths[::-1]][1:] + \
           [P(BELGIC_TH, z, FF_OFF + FF_T / 2) for z in np.linspace(ztop(BELGIC_TH), TAPE, 6)][1:]
    edge = edge[::-1]
    sweep(f"{tag}_faixa_frente", edge, 0.0030, 0, "preto", root, round_=True, segs=8)
    return HF


def shako(tag, x_off, kind, tuft_cols, plate="placa", cord=None, back_number=None):
    """kind: "belgic" | "stovepipe"; plate: "placa" (the model's plate) | "corneta" (bugle badge)."""
    global H, top_hw, top_hd
    if kind == "belgic":
        H = BELGIC_H * k; top_hw, top_hd = base_hw, base_hd
    else:
        H = STOVE_H * k; top_hw, top_hd = base_hw - STOVE_TAPER, base_hd - STOVE_TAPER * base_hd / base_hw
    root = bpy.data.objects.new(f"UK_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    body(tag, root, "feltro" if kind == "belgic" else "couro")
    visor(tag, root)
    if kind == "belgic":
        HF = false_front(tag, root)
        off_f = FF_OFF + FF_T
        th_t = math.radians(60)                          # cockade and tuft on the left side (H1)
        zc = H * 0.80
        cockade(tag, root, P(th_t, zc, off_f + 0.0004), wall_n(th_t, zc))
        nrm = wall_n(th_t, zc)
        tuft(tag, root, P(th_t, zc + 0.018, off_f + 0.013), Vector((0, 0, 1)) + nrm * 0.12, 0.130, 0.026, tuft_cols)
        if plate == "corneta":
            traced_plate(f"{tag}_corneta", PLATES["corneta"], 0.060, 0.120, 0.070, 0.0022, "latao", root, off=off_f + 0.0004)
        else:
            traced_plate(f"{tag}_placa", PLATES["belgic"], 0.034, 0.034 + 0.140, 0.092, 0.0024, "latao", root, off=off_f + 0.0004)
        if cord:
            o = off_f + 0.005
            pts = [P(th_t, zc - 0.008, o), P(math.radians(38), 0.055, o), P(0, 0.022, o + 0.001),
                   P(math.radians(-38), 0.055, o), P(math.radians(-62), 0.115, o)]
            cords(tag, root, pts, cord, P(math.radians(-66), 0.100, o + 0.002), o)
    else:
        zc = H - 0.004
        if plate == "corneta":
            traced_plate(f"{tag}_corneta", PLATES["corneta"], 0.055, 0.120, 0.075, 0.0022, "latao", root)
        else:
            traced_plate(f"{tag}_placa", PLATES["stovepipe"], TAPE + 0.004, TAPE + 0.004 + 0.152, 0.102, 0.0022, "latao", root)
        cockade(tag, root, P(0, zc, 0.0034), wall_n(0, zc))
        tuft(tag, root, P(0, H + 0.010, -0.004) + Vector((0, -0.010, 0)), Vector((0, -0.10, 1)), 0.152, 0.029, tuft_cols)
        if cord:
            o = 0.006
            pts = [P(math.radians(70), H - 0.030, o), P(math.radians(40), 0.050, o), P(0, 0.028, o + 0.003),
                   P(math.radians(-40), 0.050, o), P(math.radians(-70), H - 0.030, o)]
            cords(tag, root, pts, cord, P(math.radians(-74), H - 0.060, o + 0.002), o)
    if back_number:
        number_badge(tag, root, back_number)
    return root


BAT = [(0.0, "vermelho"), (1 / 3, "branco")]           # battalion companies: white, the bottom third red (H1, H2)
VARIANTS = [  # tag, kind, tuft, plate, cords, back number
    ("belgic_batalhao", "belgic", BAT, "placa", "branco", None),
    ("belgic_granadeiro", "belgic", [(0.0, "branco")], "placa", "branco", None),
    ("belgic_ligeira", "belgic", [(0.0, "verde_esc")], "placa", "verde", None),
    ("stovepipe_batalhao", "stovepipe", BAT, "placa", None, None),
    ("stovepipe_granadeiro", "stovepipe", [(0.0, "branco")], "placa", None, None),
    ("stovepipe_ligeira", "stovepipe", [(0.0, "verde_esc")], "placa", None, None),
    ("stovepipe_28th", "stovepipe", BAT, "placa", None, "28"),
    ("stovepipe_rifles", "stovepipe", [(0.0, "verde_esc")], "corneta", "verde_esc", None),
]
SPACING = 0.42
roots = [shako(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

# ---------------------------------------------------------------- references: approximate head under every cap
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
zc = (ROOT @ Vector((0, 0, 0.11))).z + 0.06


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 700)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_uk_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_frente", (mid_x, -3.0, zc), (mid_x, 0, zc), ortho=SPACING * len(VARIANTS) + 0.13, res=(2400, 650))
shot("fila_tres_quartos", (mid_x + 1.3, -2.8, zc + 0.6), (mid_x, 0, zc - 0.02), lens=45, res=(2400, 800))


def solo(i):
    for j, r in enumerate(roots):
        for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
            o.hide_render = j != i


for i, nm_ in ((0, "belgic_batalhao_lado"), (3, "stovepipe_batalhao_lado")):
    solo(i)
    shot(nm_, (i * SPACING - 2.0, F["head_cy"], zc), (i * SPACING, F["head_cy"], zc), ortho=0.75, res=(900, 1000))
solo(6)
shot("stovepipe_28th_costas", (6 * SPACING, 2.5, zc), (6 * SPACING, 0, zc), ortho=0.6, res=(900, 1000))
solo(-1)
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
