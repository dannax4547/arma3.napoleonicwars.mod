# Phase 3 blockout of the Prussian line infantry 1813 uniform (HCL_U_Pruss1813_01).
# Main shapes only (no UVs, no final textures), fitted over the official Arma 3 Samples body
# (A3_character_example.p3d, Resolution 1) in character space (P3D origin 1.007 m above the ground).
#
# Every garment surface is lofted from cross-sections of the official body: for each station the body vertices of
# the relevant bones (selected by their skin weights) are projected on the section plane, their convex hull is taken
# (cloth bridges concavities) and offset outward by the ease from the spec (docs/specs/uniforme_prussiano_infantaria_1813.md §7).
#
#   blender -b --factory-startup --python blockout_uniforme_pruss.py -- <Samples Test_Character_01 dir> <shako LOD0 .blend> <out .blend> <out img dir>
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import convex_hull_2d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

_args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, SHAKO_BLEND, OUT_BLEND, OUT_IMG = _args[:4]
RENDER = "norender" not in _args[4:]
os.makedirs(OUT_IMG, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------- spec (heights in metres above the ground)
SPEC = dict(
    waist=1.12,          # waist seam of the coat
    tails=0.70,          # bottom of the tails (U3: mid-thigh)
    collar_base=1.535, collar_h=0.055,
    cuff_h=0.075, flap_len=0.11, flap_w=0.04,
    strap_len=0.13, strap_w=0.05,
    gaiter_top=0.42,
    btn_front_r=0.009, btn_small_r=0.0065,
    ease_coat=0.012, ease_sleeve=0.018, ease_cuff=0.010, ease_trousers=0.018, ease_gaiter=0.012, ease_shoe=0.008,
)
NS = 72                                           # angular samples of each section profile
N_RING = 32                                       # vertices per ring in the blockout meshes
THICK = 0.003                                     # blockout cloth thickness (solidify)

# ---------------------------------------------------------------- official body
BONES = """pelvis spine spine1 spine2 spine3 neck head leftshoulder leftarm leftarmroll leftforearm leftforearmroll
lefthand rightshoulder rightarm rightarmroll rightforearm rightforearmroll righthand leftupleg leftuplegroll leftleg
leftlegroll leftfoot lefttoebase rightupleg rightuplegroll rightleg rightlegroll rightfoot righttoebase""".split()
lod = read_mlod(os.path.join(SAMPLES, "A3_character_example.p3d"))[0]
pts = [Vector(to_blender(p)) for p in lod["points"]]
W = [dict() for _ in pts]
proxy = set()
for name, blob in lod["selections"].items():
    n = name.lower()
    if n.startswith("proxy:") or n.startswith("-"):
        proxy.update(i for i, b in enumerate(blob) if b)
        continue
    if n in BONES or n.startswith("lefthand") or n.startswith("righthand"):
        for i, b in enumerate(blob):
            if b:
                W[i][n] = (256 - b) / 255.0       # MLOD weight byte (verified on the Samples, spec §8.3)
body_faces = [f for f in lod["faces"] if not any(i in proxy for i in f) and len(set(f)) >= 3]
body_idx = sorted({i for f in body_faces for i in f})
GROUND = min(pts[i].z for i in body_idx)


def Z(h):
    return GROUND + h


def group_idx(group, thr=0.5, side=0):
    out = []
    for i in body_idx:
        if sum(w for b, w in W[i].items() if b in group) >= thr and (side == 0 or pts[i].x * side > 0):
            out.append(i)
    return out


def hand_bones(prefix):
    return {b for w in W for b in w if b.startswith(prefix)}


TORSO = {"pelvis", "spine", "spine1", "spine2", "spine3", "neck", "head", "leftshoulder", "rightshoulder"}
ARM = {s: {f"{p}arm", f"{p}armroll", f"{p}forearm", f"{p}forearmroll"} for s, p in ((1, "left"), (-1, "right"))}
HAND = {1: hand_bones("lefthand"), -1: hand_bones("righthand")}
LEG = {s: {f"{p}upleg", f"{p}uplegroll", f"{p}leg", f"{p}legroll"} for s, p in ((1, "left"), (-1, "right"))}
FOOT = {s: {f"{p}foot", f"{p}toebase"} for s, p in ((1, "left"), (-1, "right"))}


def joint(A, B, thr=0.15):
    P = [pts[i] for i in body_idx
         if sum(W[i].get(b, 0) for b in A) >= thr and sum(W[i].get(b, 0) for b in B) >= thr]
    if len(P) < 3:                                  # fallback: midpoints of edges between the two bone regions
        P = []
        for f in body_faces:
            for a, b in zip(f, f[1:] + f[:1]):
                da = max(W[a], key=W[a].get) if W[a] else None
                db = max(W[b], key=W[b].get) if W[b] else None
                if (da in A and db in B) or (da in B and db in A):
                    P.append((pts[a] + pts[b]) / 2)
    return sum(P, Vector()) / len(P)


J = {}
for s, p in ((1, "left"), (-1, "right")):
    J[("shoulder", s)] = joint({f"{p}shoulder"}, {f"{p}arm"})
    J[("elbow", s)] = joint({f"{p}armroll"}, {f"{p}forearm"})
    J[("wrist", s)] = joint({f"{p}forearmroll"}, {f"{p}hand"})
    J[("hip", s)] = joint({"pelvis"}, {f"{p}upleg"})
    J[("knee", s)] = joint({f"{p}uplegroll"}, {f"{p}leg"})
    J[("ankle", s)] = joint({f"{p}legroll"}, {f"{p}foot"})
print(f"GROUND z = {GROUND:+.4f}")
for (n, s), v in sorted(J.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    print(f"JOINT {n:8s} {'L' if s > 0 else 'R'}: x{v.x:+.3f} y{v.y:+.3f} h{v.z - GROUND:.3f}")

# Body mesh (reference, also used for ray casts and clearance checks)
bm_body = bmesh.new()
bv = [bm_body.verts.new(p) for p in pts]
for f in body_faces:
    try:
        # reversed order -> normals point inward (see p3d_mlod.py); BODY_SIGN below compensates for it
        bm_body.faces.new([bv[i] for i in reversed(f)])
    except ValueError:
        pass
bmesh.ops.delete(bm_body, geom=[v for v in bm_body.verts if not v.link_faces], context="VERTS")
# Body edges (point indices) for exact cross-sections: the mesh is too sparse for vertex slabs.
BODY_EDGES = sorted({(min(a, b), max(a, b)) for f in body_faces for a, b in zip(f, f[1:] + f[:1]) if a != b})
bm_body.normal_update()
BODY_BVH = BVHTree.FromBMesh(bm_body)
_c, _n, _i, _d = BODY_BVH.find_nearest(Vector((0, -0.6, Z(1.30))))
BODY_SIGN = 1.0 if (Vector((0, -0.6, Z(1.30))) - _c).dot(_n) > 0 else -1.0


def body_signed_distance(p):
    c, n, i, d = BODY_BVH.find_nearest(p)
    if c is None:
        return 1.0
    s = (p - c).dot(n) * BODY_SIGN
    return d if s >= 0 else -d


# ---------------------------------------------------------------- section profiles
def ray_hull(c, th, poly):
    d = Vector((math.cos(th), math.sin(th)))
    best = 0.0
    for a, b in zip(poly, poly[1:] + poly[:1]):
        e = b - a
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-12:
            continue
        ac = a - c
        t = (ac.x * e.y - ac.y * e.x) / den
        s = (ac.x * d.y - ac.y * d.x) / den
        if t > 0 and -1e-9 <= s <= 1 + 1e-9:
            best = max(best, t)
    return best


def profile(points, origin, axis, fwd):
    axis = axis.normalized()
    u = (fwd - axis * fwd.dot(axis)).normalized()
    v = axis.cross(u)
    P2 = [Vector(((p - origin).dot(u), (p - origin).dot(v))) for p in points]
    fr = dict(o=origin.copy(), a=axis, u=u, v=v, c=None, r=None)
    if len(P2) < 5:
        return fr
    poly = [P2[i] for i in convex_hull_2d(P2)]
    m = sum(poly, Vector((0, 0))) / len(poly)
    poly.sort(key=lambda p: math.atan2(p.y - m.y, p.x - m.x))      # guarantee polygon order
    A, cx, cy = 0.0, 0.0, 0.0
    for p, q in zip(poly, poly[1:] + poly[:1]):
        cr = p.x * q.y - q.x * p.y
        A += cr; cx += (p.x + q.x) * cr; cy += (p.y + q.y) * cr
    c = Vector((cx / (3 * A), cy / (3 * A))) if abs(A) > 1e-10 else sum(poly, Vector((0, 0))) / len(poly)
    fr["c"] = c
    fr["r"] = [ray_hull(c, 2 * math.pi * k / NS, poly) for k in range(NS)]
    return fr


def fill_and_smooth(frames, passes=2):
    valid = [k for k, f in enumerate(frames) if f["c"] is not None]
    for k, f in enumerate(frames):
        if f["c"] is None:
            j = min(valid, key=lambda q: abs(q - k))
            f["c"], f["r"] = frames[j]["c"].copy(), list(frames[j]["r"])
    for _ in range(passes):
        cs = [f["c"].copy() for f in frames]
        rs = [list(f["r"]) for f in frames]
        for k in range(1, len(frames) - 1):
            frames[k]["c"] = cs[k - 1] * 0.25 + cs[k] * 0.5 + cs[k + 1] * 0.25
            frames[k]["r"] = [rs[k - 1][a] * 0.25 + rs[k][a] * 0.5 + rs[k + 1][a] * 0.25 for a in range(NS)]
    return frames


def radius(fr, th):
    x = (th % (2 * math.pi)) / (2 * math.pi) * NS
    a = int(x) % NS
    t = x - int(x)
    return fr["r"][a] * (1 - t) + fr["r"][(a + 1) % NS] * t


def fpoint(fr, th, ease):
    r = radius(fr, th) + ease
    c = fr["c"]
    return fr["o"] + fr["u"] * (c.x + r * math.cos(th)) + fr["v"] * (c.y + r * math.sin(th))


def theta_of(fr, direction):
    return math.atan2(direction.dot(fr["v"]), direction.dot(fr["u"]))


def section(idx, origin, axis, rmax=None, xside=0, xlim=None, xmargin=0.002):
    """Exact cross-section of the body: intersections of the body edges that touch the vertex set idx with the
    plane (origin, axis). Optional filters: distance from the origin inside the plane, side of x (points must be
    more than xmargin on that side; a negative margin lets the section cross the centre line), |x| limit."""
    S_ = idx if isinstance(idx, set) else set(idx)
    out = []
    for a, b in BODY_EDGES:
        if a not in S_ and b not in S_:
            continue
        pa, pb = pts[a], pts[b]
        ta, tb = (pa - origin).dot(axis), (pb - origin).dot(axis)
        if ta * tb > 0 or ta == tb:
            continue
        p = pa + (pb - pa) * (ta / (ta - tb))
        w = p - origin
        if rmax is not None and (w - axis * w.dot(axis)).length > rmax:
            continue
        if xside and p.x * xside <= xmargin:
            continue
        if xlim is not None and abs(p.x) > xlim:
            continue
        out.append(p)
    return out


UP, FRONT = Vector((0, 0, 1)), Vector((0, -1, 0))


def vertical_frames(idx, heights, xlim=None, xside=0, passes=2, xmargin=0.002):
    frames = []
    for h in heights:
        o = Vector((0, 0, Z(h)))
        frames.append(profile(section(idx, o, UP, xside=xside, xlim=xlim, xmargin=xmargin), o, UP, FRONT))
    return fill_and_smooth(frames, passes)


def polyline_at(P, s, blend=0.04):
    L = [(b - a).length for a, b in zip(P, P[1:])]
    acc = 0.0
    for k, l in enumerate(L):
        if s <= acc + l or k == len(L) - 1:
            t = (s - acc) / l
            d = (P[k + 1] - P[k]).normalized()
            pos = P[k] + (P[k + 1] - P[k]) * t
            if k + 1 < len(L) and (acc + l - s) < blend:          # approaching the next joint
                dn = (P[k + 2] - P[k + 1]).normalized()
                a = 0.5 * (1 - (acc + l - s) / blend)
                d = (d * (1 - a) + dn * a).normalized()
            if k > 0 and (s - acc) < blend:                       # leaving the previous joint
                dp = (P[k] - P[k - 1]).normalized()
                a = 0.5 * (1 - (s - acc) / blend)
                d = (d * (1 - a) + dp * a).normalized()
            return pos, d
        acc += l
    return P[-1], (P[-1] - P[-2]).normalized()


def axis_frames(idx, P, s_list, rmax, fwd=FRONT):
    frames = []
    for s in s_list:
        o, d = polyline_at(P, s)
        frames.append(profile(section(idx, o, d, rmax=rmax), o, d, fwd))
    return fill_and_smooth(frames)


# ---------------------------------------------------------------- mesh helpers
COLL = bpy.data.collections.new("HCL_Uniforme_Blockout")
bpy.context.scene.collection.children.link(COLL)
REFC = bpy.data.collections.new("REF_Arma3Samples")
bpy.context.scene.collection.children.link(REFC)


def mat(name, rgb, rough=0.85, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1)
    return m


M = dict(
    azul=mat("BLK_casaco_azul", (0.024, 0.040, 0.105)),
    vermelho=mat("BLK_vermelho_provincial", (0.33, 0.016, 0.020)),
    branco=mat("BLK_platina_branca", (0.72, 0.71, 0.67)),
    cinza=mat("BLK_calca_cinza", (0.15, 0.148, 0.140)),
    preto=mat("BLK_polaina_preta", (0.018, 0.018, 0.018)),
    sapato=mat("BLK_sapato_couro", (0.012, 0.010, 0.009), rough=0.45),
    latao=mat("BLK_latao", (0.62, 0.43, 0.13), rough=0.35, metal=1.0),
    pele=mat("REF_pele", (0.80, 0.60, 0.48), rough=0.7),
)


def new_obj(name, bm, mats, coll=COLL, thick=THICK, mat_offset_inner=None, offset=1.0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if thick:
        sm = ob.modifiers.new("Espessura", "SOLIDIFY")
        sm.thickness = thick
        sm.offset = offset
        sm.use_even_offset = True
        if mat_offset_inner is not None:
            sm.material_offset = mat_offset_inner
    return ob


def loft(bm, rings, closed=True, mat_of=None, axis_pts=None):
    """rings: list of lists of Vectors (same length). Faces oriented outward using axis_pts (one per ring)."""
    V = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    faces = []
    for k in range(len(rings) - 1):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            f = bm.faces.new((V[k][i], V[k][j], V[k + 1][j], V[k + 1][i]))
            if mat_of:
                f.material_index = mat_of(k, i)
            faces.append((f, k))
    bm.normal_update()
    if axis_pts:
        score = 0.0
        for f, k in faces:
            score += f.normal.dot(f.calc_center_median() - (axis_pts[k] + axis_pts[k + 1]) / 2)
        if score < 0:
            bmesh.ops.reverse_faces(bm, faces=[f for f, _ in faces])
    return V


def ring_pts(fr, ease, n=N_RING, th0=0.0, th1=2 * math.pi, closed=True):
    if closed:
        return [fpoint(fr, th0 + (th1 - th0) * i / n, ease) for i in range(n)]
    return [fpoint(fr, th0 + (th1 - th0) * i / (n - 1), ease) for i in range(n)]


def frame_centre(fr):
    return fr["o"] + fr["u"] * fr["c"].x + fr["v"] * fr["c"].y


def button(bm, centre, normal, r, depth=0.004, seg=10, mat_index=0):
    n = normal.normalized()
    rot = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
    m = Matrix.Translation(centre + n * (depth / 2)) @ rot
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r * 0.8,
                                depth=depth, matrix=m)
    for v in res["verts"]:
        for f in v.link_faces:
            f.material_index = mat_index


def obj_bvh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    eo = ob.evaluated_get(dg)
    me = eo.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    eo.to_mesh_clear()
    return t


S = SPEC
parts = []

# ---------------------------------------------------------------- 1. coat body (waist → shoulders) + yoke + collar
# arm vertices inside xlim bridge the armpit (as the underarm of a real coat); the sleeve head overlaps the rest
torso_idx = set(group_idx(TORSO | ARM[1] | ARM[-1]))
xlim = abs(J[("shoulder", 1)].x) + 0.05
hs = [S["waist"] - 0.015 + k * 0.02 for k in range(int((1.50 - (S["waist"] - 0.015)) / 0.02) + 1)]
coat_fr = vertical_frames(torso_idx, hs, xlim=xlim)

neck_idx = set(group_idx({"neck", "spine3", "head"}))
neck_pts = section(neck_idx, Vector((0, 0, Z(1.555))), UP, xlim=0.10)
collar_fr = profile(neck_pts, Vector((0, 0, Z(S["collar_base"]))), UP, FRONT)
print(f"neck section: {len(neck_pts)} pts; collar centre y {collar_fr['c'] and frame_centre(collar_fr).y:+.3f}")

def body_top(x, y):
    hit = BODY_BVH.ray_cast(Vector((x, y, Z(2.0))), Vector((0, 0, -1)))
    return hit[0].z if hit[0] is not None else None


# collar base: around the neck, never below the neck/trapezius surface
collar_base = []
for p in ring_pts(collar_fr, 0.010):
    zb = body_top(p.x, p.y)
    collar_base.append(Vector((p.x, p.y, max(Z(S["collar_base"]), (zb if zb is not None else -9) + 0.004))))

rings, axis_pts = [], []
for fr in coat_fr:
    rings.append(ring_pts(fr, S["ease_coat"]))
    axis_pts.append(frame_centre(fr))
# yoke: from the top coat ring to the collar base, following the shoulder surface
outer = rings[-1]
K = 5
for k in range(1, K + 1):
    t = k / K
    ring = []
    for p_out, p_in in zip(outer, collar_base):
        q = p_out.lerp(p_in, t)
        zb = body_top(q.x, q.y)
        z = q.z if zb is None else max(q.z, zb + (S["ease_coat"] if t < 1.0 else 0.004))
        ring.append(Vector((q.x, q.y, z)))
    rings.append(ring)
    axis_pts.append(frame_centre(collar_fr) * t + axis_pts[-1] * (1 - t))
bm = bmesh.new()
loft(bm, rings, axis_pts=axis_pts)
coat = new_obj("BLK_casaco_corpo", bm, [M["azul"]])
parts.append(coat)

# collar: stand collar, slightly higher at the back
bm = bmesh.new()
crings, caxis = [], []
for k, f in enumerate((0.0, 0.5, 1.0)):
    ring = []
    for i in range(N_RING):
        th = 2 * math.pi * i / N_RING
        base = fpoint(collar_fr, th, 0.010 + 0.004 * f)
        z_top = Z(S["collar_base"] + S["collar_h"]) + 0.005 * -math.cos(th)     # higher at the back
        z0 = collar_base[i].z - 0.004
        ring.append(Vector((base.x, base.y, z0 + (max(z_top, z0 + 0.03) - z0) * f)))
    crings.append(ring)
    caxis.append(frame_centre(collar_fr) + Vector((0, 0, S["collar_h"] * f)))
loft(bm, crings, axis_pts=caxis)
collar = new_obj("BLK_gola", bm, [M["vermelho"]], thick=0.005)
parts.append(collar)

# ---------------------------------------------------------------- 2. sleeves, cuffs, cuff flaps
sleeves, cuffs = {}, {}
for s in (1, -1):
    sh, el, wr = J[("shoulder", s)], J[("elbow", s)], J[("wrist", s)]
    d0 = (el - sh).normalized()
    start = sh - d0 * 0.03
    d_end = (wr - el).normalized()
    end = wr + d_end * 0.012
    P = [start, el, end]
    Ltot = (el - start).length + (end - el).length
    s_list = [k * 0.03 for k in range(int((Ltot - S["cuff_h"]) / 0.03) + 1)] + [Ltot - S["cuff_h"], Ltot - 0.035, Ltot]
    s_list = sorted(set(round(x, 4) for x in s_list))
    idx = set(group_idx(ARM[s] | HAND[s] | {("left" if s > 0 else "right") + "shoulder"}, side=s))
    fr = axis_frames(idx, P, s_list, 0.10)
    ease = [S["ease_sleeve"] + (S["ease_cuff"] - S["ease_sleeve"]) * min(1, max(0, (x - (Ltot - 0.30)) / 0.30))
            for x in s_list]
    rings = [ring_pts(f, e) for f, e in zip(fr, ease)]
    bm = bmesh.new()
    loft(bm, rings, axis_pts=[frame_centre(f) for f in fr])
    sl = new_obj(f"BLK_manga_{'E' if s > 0 else 'D'}", bm, [M["azul"]])
    parts.append(sl)
    sleeves[s] = (fr, s_list, ease, Ltot)
    # cuff: the last cuff_h of the sleeve, 4 mm proud
    k0 = s_list.index(round(Ltot - S["cuff_h"], 4))
    cf = fr[k0:]
    ce = [e + 0.004 for e in ease[k0:]]
    bm = bmesh.new()
    loft(bm, [ring_pts(f, e) for f, e in zip(cf, ce)], axis_pts=[frame_centre(f) for f in cf])
    cu = new_obj(f"BLK_punho_{'E' if s > 0 else 'D'}", bm, [M["vermelho"]], thick=0.004)
    parts.append(cu)
    # Brandenburg flap on the outer side: blue patch over the cuff, 3 buttons
    out_dir = Vector((s, 0, 0))
    bm = bmesh.new()
    rows = []
    for q in range(6):
        sq = Ltot - 0.012 - S["flap_len"] * q / 5
        o, dd = polyline_at(P, sq)
        f = profile(section(idx, o, dd, rmax=0.10), o, dd, FRONT)
        if f["c"] is None:
            f = cf[-1]
        th_o = theta_of(f, out_dir - dd * out_dir.dot(dd))
        e = (ce[-1] if sq > Ltot - S["cuff_h"] else ease[k0]) + 0.006
        r = radius(f, th_o) + e
        dth = (S["flap_w"] / 2) / r
        rows.append([fpoint(f, th_o + dth * (c - 1), e) for c in range(3)])
    loft(bm, rows, closed=False)
    fl = new_obj(f"BLK_pala_punho_{'E' if s > 0 else 'D'}", bm, [M["azul"]], thick=0.003)
    parts.append(fl)
    cuffs[s] = (P, idx, Ltot, out_dir)

# ---------------------------------------------------------------- 3. tails (skirts) with red turnbacks
skirt_idx = set(group_idx({"pelvis", "spine", "spine1"} | LEG[1] | LEG[-1]))
hs_sk = [S["waist"] - k * 0.03 for k in range(int((S["waist"] - S["tails"]) / 0.03) + 1)]
if hs_sk[-1] > S["tails"] + 1e-4:
    hs_sk.append(S["tails"])
sk_fr = vertical_frames(skirt_idx, hs_sk)


def interp(h, table):
    table = sorted(table)
    for (h0, a0), (h1, a1) in zip(table, table[1:]):
        if h0 <= h <= h1:
            return a0 + (a1 - a0) * (h - h0) / (h1 - h0)
    return table[0][1] if h < table[0][0] else table[-1][1]


FRONT_CUT = [(0.70, 108), (0.82, 100), (0.95, 80), (1.06, 45), (1.12, 14)]   # half-angle of the front opening (deg)
VENT = [(0.70, 3.0), (1.04, 3.0), (1.05, 0.0), (1.12, 0.0)]                # half-angle of the back vent (deg)
MC = 14
bm = bmesh.new()
for side in (1, -1):
    rows, axp = [], []
    for h, f in zip(hs_sk, sk_fr):
        t = (S["waist"] - h) / (S["waist"] - S["tails"])
        e = 0.018 + 0.022 * t
        a0 = math.radians(interp(h, FRONT_CUT))
        a1 = math.pi - math.radians(interp(h, VENT))
        row = []
        for c in range(MC):
            a = a0 + (a1 - a0) * c / (MC - 1)
            th = a if side > 0 else -a
            row.append(fpoint(f, th, e))
        rows.append(row)
        axp.append(frame_centre(f))
    loft(bm, rows, closed=False, mat_of=lambda k, i: 1 if i < 2 else 0, axis_pts=axp)
tails = new_obj("BLK_abas", bm, [M["azul"], M["vermelho"]], thick=0.004, mat_offset_inner=1)
parts.append(tails)

# ---------------------------------------------------------------- 4. shoulder straps (white), on the yoke
bpy.context.view_layer.update()
coat_bvh = obj_bvh(coat)
bm = bmesh.new()
strap_buttons = []
for s in (1, -1):
    grid = []
    xs = [s * (0.095 + S["strap_len"] * q / 5) for q in range(6)]      # from beside the collar to the sleeve head
    ridge = []
    for x in xs:
        best = None
        for yy in [k * 0.005 - 0.08 for k in range(41)]:
            hit = coat_bvh.ray_cast(Vector((x, yy, Z(2.0))), Vector((0, 0, -1)))
            if hit[0] is not None and (best is None or hit[0].z > best.z):
                best = hit[0]
        if best is None:
            raise RuntimeError(f"shoulder strap: no coat surface found at x={x:+.3f}")
        ridge.append(best)
    for x, rp in zip(xs, ridge):
        row = []
        for w in (-1, 0, 1):
            yy = rp.y + w * S["strap_w"] / 2
            hit = coat_bvh.ray_cast(Vector((x, yy, Z(2.0))), Vector((0, 0, -1)))
            p = hit[0] if hit[0] is not None else Vector((x, yy, rp.z))
            zb = body_top(x, yy)
            if zb is not None:
                p = Vector((p.x, p.y, max(p.z, zb + S["ease_coat"] + THICK)))
            row.append(p + Vector((0, 0, 0.0035)))
        grid.append(row)
    loft(bm, grid, closed=False)
    strap_buttons.append((grid[1][1] + Vector((0, 0, THICK)), Vector((0, 0, 1))))
straps = new_obj("BLK_platinas", bm, [M["branco"]], thick=0.003)
parts.append(straps)

# ---------------------------------------------------------------- 5. trousers (pelvis + legs), gaiters, shoes
# seat: one tube over pelvis and both thighs, from under the coat down to the crotch
pel_idx = set(group_idx({"pelvis", "spine", "spine1"} | LEG[1] | LEG[-1]))
hs_p = [1.10 - k * 0.025 for k in range(int((1.10 - 0.86) / 0.025) + 1)] + [0.86]
hs_p = sorted(set(round(h, 4) for h in hs_p), reverse=True)
pf = vertical_frames(pel_idx, hs_p)
ep = [0.006 + (S["ease_trousers"] - 0.006) * min(1, (1.10 - h) / 0.10) for h in hs_p]
bm = bmesh.new()
loft(bm, [ring_pts(f, e) for f, e in zip(pf, ep)], axis_pts=[frame_centre(f) for f in pf])
# legs: horizontal sections of each leg, from just above the crotch into the gaiters
for s in (1, -1):
    idx = set(group_idx(LEG[s] | {"pelvis"}, side=s))
    hs_l = [0.90 - k * 0.03 for k in range(int((0.90 - 0.39) / 0.03) + 1)] + [0.39]   # overlaps the seat (0.86)
    hs_l = sorted(set(round(h, 4) for h in hs_l), reverse=True)
    fr = vertical_frames(idx, hs_l, xside=s, xmargin=-0.012)       # crosses the centre line: closes the crotch
    eas =[S["ease_trousers"] + (0.008 - S["ease_trousers"]) * max(0, min(1, (0.55 - h) / (0.55 - 0.40))) for h in hs_l]
    loft(bm, [ring_pts(f, e) for f, e in zip(fr, eas)], axis_pts=[frame_centre(f) for f in fr])
trousers = new_obj("BLK_calca", bm, [M["cinza"]])
parts.append(trousers)

gaiter_frames = {}
for s in (1, -1):
    idx = set(group_idx(LEG[s] | FOOT[s], side=s))
    hs_g = [S["gaiter_top"] - k * 0.03 for k in range(int((S["gaiter_top"] - 0.075) / 0.03) + 1)] + [0.075]
    hs_g = sorted(set(round(h, 4) for h in hs_g), reverse=True)
    fr = vertical_frames(idx, hs_g, xside=s, passes=1)
    eg = [S["ease_gaiter"] + 0.004 * (h - 0.075) / (S["gaiter_top"] - 0.075) for h in hs_g]
    bm = bmesh.new()
    loft(bm, [ring_pts(f, e) for f, e in zip(fr, eg)], axis_pts=[frame_centre(f) for f in fr])
    g = new_obj(f"BLK_polaina_{'E' if s > 0 else 'D'}", bm, [M["preto"]])
    parts.append(g)
    gaiter_frames[s] = (fr, hs_g, eg)

for s in (1, -1):
    idx = set(group_idx(FOOT[s] | LEG[s], thr=0.3, side=s))
    hs_s = [0.02, 0.035, 0.05, 0.065, 0.08, 0.095]
    fr = vertical_frames(idx, hs_s, xside=s, passes=1)
    # flat sole on the ground; its outline is the hull of the 4, 10 and 20 mm sections together (toe tips are low)
    sole_pts = []
    for h in (0.004, 0.010, 0.020):
        sole_pts += section(idx, Vector((0, 0, Z(h))), UP, xside=s)
    sole_fr = fill_and_smooth([profile(sole_pts, Vector((0, 0, Z(0.0))), UP, FRONT)], passes=0)[0]
    sole = [Vector((p.x, p.y, Z(0.0))) for p in ring_pts(sole_fr, S["ease_shoe"] + 0.004)]
    welt = [Vector((p.x, p.y, Z(0.02))) for p in ring_pts(sole_fr, S["ease_shoe"] + 0.002)]
    rings = [sole, welt] + [ring_pts(f, S["ease_shoe"]) for f in fr[1:]]
    bm = bmesh.new()
    V = loft(bm, rings, axis_pts=[frame_centre(sole_fr), frame_centre(sole_fr) + Vector((0, 0, 0.02))]
             + [frame_centre(f) for f in fr[1:]])
    sole_c = sum(rings[0], Vector()) / len(rings[0])
    cv = bm.verts.new(sole_c)
    for i in range(len(V[0])):
        f = bm.faces.new((cv, V[0][(i + 1) % len(V[0])], V[0][i]))
    bm.normal_update()
    for f in bm.faces:
        if len(f.verts) == 3 and cv in f.verts and f.normal.z > 0:
            f.normal_flip()
    sh = new_obj(f"BLK_sapato_{'E' if s > 0 else 'D'}", bm, [M["sapato"]], thick=0.004, offset=-1.0)  # sole stays on the ground
    parts.append(sh)

# ---------------------------------------------------------------- 6. buttons (brass)
bpy.context.view_layer.update()
coat_bvh = obj_bvh(coat)
tails_bvh = obj_bvh(tails)
bm = bmesh.new()
nb = 0
# front: two columns of 7 (U4, as in the mod), viewer-left column 1 cm right of the red piping
for x in (-0.015, 0.015):
    for k in range(7):
        h = 1.50 - (1.50 - 1.17) * k / 6
        hit = coat_bvh.ray_cast(Vector((x, -1.0, Z(h))), Vector((0, 1, 0)))
        if hit[0] is not None:
            button(bm, hit[0], hit[1], S["btn_front_r"]); nb += 1
# back: two at the waist (M2)
for x in (-0.045, 0.045):
    hit = coat_bvh.ray_cast(Vector((x, 1.0, Z(S["waist"] + 0.005))), Vector((0, -1, 0)))
    if hit[0] is not None:
        button(bm, hit[0], hit[1], S["btn_front_r"]); nb += 1
# shoulder straps: one each, near the collar
for c, n in strap_buttons:
    button(bm, c, n, S["btn_small_r"], depth=0.003); nb += 1
# cuff flaps: three each
for s in (1, -1):
    P, idx, Ltot, out_dir = cuffs[s]
    for q in range(3):
        sq = Ltot - 0.012 - S["flap_len"] * (0.2 + 0.3 * q)
        o, dd = polyline_at(P, sq)
        f = profile(section(idx, o, dd, rmax=0.10), o, dd, FRONT)
        if f["c"] is None:
            continue
        th_o = theta_of(f, out_dir - dd * out_dir.dot(dd))
        e = (S["ease_cuff"] + 0.004 if sq > Ltot - S["cuff_h"] else S["ease_cuff"]) + 0.006 + 0.003
        p = fpoint(f, th_o, e)
        nrm = (p - frame_centre(f)); nrm -= dd * nrm.dot(dd)
        button(bm, p, nrm, S["btn_small_r"], depth=0.003); nb += 1
# gaiters: ten each, outer side
for s in (1, -1):
    fr, hs_g, eg = gaiter_frames[s]
    for k in range(10):
        h = 0.40 - (0.40 - 0.11) * k / 9
        j = min(range(len(hs_g)), key=lambda q: abs(hs_g[q] - h))
        f = fr[j]
        th = math.pi / 2 if s > 0 else -math.pi / 2
        p = fpoint(f, th, eg[j] + THICK) + Vector((0, 0, Z(h) - f["o"].z))
        button(bm, p, Vector((s, 0, 0)), 0.005, depth=0.003); nb += 1
buttons = new_obj("BLK_botoes", bm, [M["latao"]], thick=0)
parts.append(buttons)
print(f"buttons: {nb}")

# ---------------------------------------------------------------- references: official body, approximate head, approved shako
me = bpy.data.meshes.new("REF_corpo_A3_character_example")
bm_body.to_mesh(me)
me.materials.append(M["pele"])
body_ob = bpy.data.objects.new("REF_corpo_A3_character_example", me)
REFC.objects.link(body_ob)
with bpy.data.libraries.load(SHAKO_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ("HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial")]
SHC = bpy.data.collections.new("REF_Barretina_aprovada")
bpy.context.scene.collection.children.link(SHC)
head_ob = None
for o in dst.objects:
    (REFC if o.name.startswith("REF_") else SHC).objects.link(o)
    if o.name.startswith("REF_cabeca"):
        head_ob = o

# ---------------------------------------------------------------- checks
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
print("\n=== PARTS (evaluated, with thickness)")
tot = 0
for ob in parts:
    eo = ob.evaluated_get(dg)
    m = eo.to_mesh()
    tris = sum(len(p.vertices) - 2 for p in m.polygons)
    tot += tris
    print(f"  {ob.name:24s} tris {tris:6d}")
    eo.to_mesh_clear()
print(f"  TOTAL tris {tot}")

print("\n=== CLEARANCE to the official body (original surface of each part; negative = inside the body)")
for ob in parts:
    if ob is buttons:
        continue
    P = [ob.matrix_world @ v.co for v in ob.data.vertices]
    vals = [body_signed_distance(p) for p in P]
    inside = [(d, p) for d, p in zip(vals, P) if d < 0]
    where = ""
    if inside:
        hz = [p.z - GROUND for _, p in inside]
        worst = min(inside, key=lambda q: q[0])[1]
        where = (f"  inside at h {min(hz):.3f}-{max(hz):.3f}; worst at x{worst.x:+.3f} y{worst.y:+.3f} "
                 f"h{worst.z - GROUND:.3f}")
    print(f"  {ob.name:24s} min {min(vals)*1000:7.1f} mm  median {sorted(vals)[len(vals)//2]*1000:6.1f} mm  "
          f"inside {len(inside)}/{len(vals)}{where}")

if head_ob is not None:
    hb = obj_bvh(head_ob)
    worst, n_in = 1.0, 0
    for v in collar.data.vertices:
        p = collar.matrix_world @ v.co
        c, n, i, d = hb.find_nearest(p)
        s_ = (p - c).dot(n)
        dd = d if s_ >= 0 else -d
        worst = min(worst, dd)
        n_in += dd < 0
    print(f"\n=== COLLAR vs approximate head (not official): min distance {worst*1000:.1f} mm; collar vertices inside {n_in}")
# Exposed skin: a body vertex is exposed when a ray along its normal leaves without crossing any garment part.
# Hands (beyond the wrist) and the neck above the collar are meant to stay visible and are skipped.
gbm = bmesh.new()
for ob in parts:
    eo = ob.evaluated_get(dg)
    m = eo.to_mesh()
    tmp = bmesh.new()
    tmp.from_mesh(m)
    tmp.transform(ob.matrix_world)
    tm = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(tm)
    tmp.free()
    gbm.from_mesh(tm)
    bpy.data.meshes.remove(tm)
    eo.to_mesh_clear()
G_BVH = BVHTree.FromBMesh(gbm)
gbm.free()
wr_dir = {s: (J[("wrist", s)] - J[("elbow", s)]).normalized() for s in (1, -1)}
checked, exposed = 0, []
print(f"body normal sign: {BODY_SIGN:+.0f}")
for v in body_ob.data.vertices:
    p, n = v.co, v.normal * BODY_SIGN
    if p.z - GROUND > 1.56:
        continue
    s_ = 1 if p.x > 0 else -1
    if (p - J[("wrist", s_)]).dot(wr_dir[s_]) > 0.005:
        continue
    checked += 1
    hit = G_BVH.ray_cast(p + n * 1e-4, n, 0.25)
    if hit[0] is None:
        exposed.append(p)
print(f"\n=== EXPOSED SKIN: {len(exposed)} of {checked} body vertices (hands and neck excluded)")
for p in exposed[:12]:
    print(f"    x{p.x:+.3f} y{p.y:+.3f} h{p.z - GROUND:.3f}")
shoe_min = min((o.matrix_world @ v.co).z for o in parts if o.name.startswith("BLK_sapato") for v in o.data.vertices)
print(f"=== SHOES: lowest point h = {(shoe_min - GROUND)*1000:.1f} mm above the ground")

# ---------------------------------------------------------------- renders
scene = bpy.context.scene
sun = bpy.data.objects.new("REF_sol", bpy.data.lights.new("REF_sol", "SUN"))
sun.data.energy = 3.2
sun.rotation_euler = (math.radians(50), 0, math.radians(25))
REFC.objects.link(sun)
fill = bpy.data.objects.new("REF_preench", bpy.data.lights.new("REF_preench", "SUN"))
fill.data.energy = 1.3
fill.rotation_euler = (math.radians(65), 0, math.radians(200))
REFC.objects.link(fill)
world = bpy.data.worlds.new("REF_mundo")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.93, 0.93, 0.93, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
scene.world = world
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"


def cam(name, loc, rot, ortho=None, lens=50, target=None):
    c = bpy.data.cameras.new(name)
    if ortho:
        c.type = "ORTHO"
        c.ortho_scale = ortho
    else:
        c.lens = lens
    o = bpy.data.objects.new(name, c)
    o.location = loc
    if target is not None:
        o.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    else:
        o.rotation_euler = rot
    REFC.objects.link(o)
    return o


ZC = Z(0.98)
shots = [
    ("frente", cam("CAM_frente", (0, -8, ZC), (math.radians(90), 0, 0), ortho=2.15), (900, 1100)),
    ("lado", cam("CAM_lado", (8, 0, ZC), (math.radians(90), 0, math.radians(90)), ortho=2.15), (900, 1100)),
    ("costas", cam("CAM_costas", (0, 8, ZC), (math.radians(90), 0, math.radians(180)), ortho=2.15), (900, 1100)),
    ("tres_quartos", cam("CAM_3q", (2.6, -3.6, Z(1.35)), None, lens=55, target=Vector((0, 0, Z(0.95)))), (900, 1100)),
    ("tres_quartos_costas", cam("CAM_3q_costas", (-2.6, 3.6, Z(1.35)), None, lens=55, target=Vector((0, 0, Z(0.95)))), (900, 1100)),
    ("detalhe_tronco", cam("CAM_tronco", (1.3, -1.9, Z(1.55)), None, lens=60, target=Vector((0.05, 0, Z(1.30)))), (1000, 900)),
    ("detalhe_pernas", cam("CAM_pernas", (1.1, -1.7, Z(0.55)), None, lens=60, target=Vector((0, 0, Z(0.30)))), (1000, 900)),
]
for name, c, (rx, ry) in (shots if RENDER else []):
    scene.camera = c
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    scene.render.filepath = os.path.join(OUT_IMG, f"blockout_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)

scene.camera = shots[0][1]
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
