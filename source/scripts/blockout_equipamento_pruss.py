# Phase 3 blockout of the Prussian 1813 infantry equipment, worn over the uniform production mesh:
#   HCL_V_Pruss1813_Correame (Arma "vest"): white crossbelt over the left shoulder, white waist belt with brass buckle,
#       black cartridge box at the right rear hip, bayonet in its scabbard on a frog at the left hip (decorative, no
#       weapon function: combat systems are out of the project's scope).
#   HCL_B_Pruss1813_Tornister (Arma "backpack"): knapsack with a hair-on calfskin flap, two white shoulder straps and
#       the rolled grey greatcoat strapped on top.
# Both are modelled in character space (backpack proxy of the official character = identity, verified).
# Every strap is laid on the OUTER surface of the uniform: rays are cast from outside toward the body axis against the
# relevant uniform parts only (coat, tails, collar, shoulder boards), so they never snap to an inner layer.
#
#   blender -b --factory-startup --python blockout_equipamento_pruss.py -- <uniform LOD0 .blend> <shako LOD0 .blend> <out .blend> <out img dir> [norender]
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

_a = sys.argv[sys.argv.index("--") + 1:]
UNIFORM_BLEND, SHAKO_BLEND, OUT_BLEND, OUT_IMG = _a[:4]
RENDER = "norender" not in _a[4:]
os.makedirs(OUT_IMG, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

GROUND = -1.0069                                     # official body (uniform report): P3D origin 1.007 m above ground


def Z(h):
    return GROUND + h


# ---------------------------------------------------------------- uniform (reference + projection surfaces)
with bpy.data.libraries.load(UNIFORM_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ("HCL_U_Pruss1813_01_LOD0", "REF_corpo_A3_character_example")]
with bpy.data.libraries.load(SHAKO_BLEND, link=False) as (src, dst2):
    dst2.objects = [n for n in src.objects if n in ("HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial")]
REFC = bpy.data.collections.new("REF_Uniforme_e_corpo")
bpy.context.scene.collection.children.link(REFC)
for o in list(dst.objects) + list(dst2.objects):
    REFC.objects.link(o)
uni = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = uni["hcl_partes"].split(",")
ubm = bmesh.new()
ubm.from_mesh(uni.data)
ubm.transform(uni.matrix_world)
PL = ubm.faces.layers.int.get("hcl_part")
coords = [v.co.copy() for v in ubm.verts]


def bvh_of(names):
    ids = {parts.index(n) for n in names}
    return BVHTree.FromPolygons(coords, [[v.index for v in f.verts] for f in ubm.faces if f[PL] in ids])


# buttons are left out: the straps keep a gap larger than a button's height (4.5 mm) instead of riding over them
TORSO_OUT = bvh_of(["casaco_corpo", "gola", "aba_E", "aba_D", "platina_E", "platina_D", "calca_assento"])
ALL_U = BVHTree.FromBMesh(ubm)
LEGS_OUT = bvh_of(["aba_E", "aba_D", "calca_assento", "calca_perna_E", "calca_perna_D"])   # where the scabbard rests

S = dict(cross_w=0.060, waist_w=0.050, belt_t=0.0035, belt_gap=0.0045, strap_w=0.045, strap_gap=0.014,
         box_w=0.20, box_h=0.13, box_d=0.065, scab_len=0.45, socket_len=0.075, socket_r=0.012,
         pack_w=0.34, pack_h=0.30, pack_d=0.12, roll_r=0.055, roll_len=0.42)

MATS = [("HCL_couro_branco", (0.80, 0.79, 0.74), 0.6, 0), ("HCL_latao", (0.62, 0.43, 0.13), 0.35, 1),
        ("HCL_couro_preto", (0.015, 0.014, 0.013), 0.45, 0), ("HCL_pele_bezerro", (0.17, 0.09, 0.045), 0.95, 0),
        ("HCL_capote_cinza", (0.16, 0.16, 0.155), 0.95, 0), ("HCL_ferro", (0.18, 0.18, 0.19), 0.4, 1)]
BRANCO, LATAO, PRETO, BEZERRO, CAPOTE, FERRO = range(len(MATS))


def make_mats(me):
    for name, rgb, rough, metal in MATS:
        m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*rgb, 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        m.diffuse_color = (*rgb, 1)
        me.materials.append(m)


def project_out(q, bvh, axis_y=0.02, up_bias=0.0):
    """Outer surface point under q: ray from outside toward the body axis (optionally tilted downward)."""
    o = Vector((q.x, q.y - axis_y, 0.0))
    o = (o.normalized() if o.length > 1e-6 else Vector((0, -1, 0))) + Vector((0, 0, up_bias))
    o.normalize()
    hit = bvh.ray_cast(q + o * 0.35, -o, 0.7)
    return (hit[0], hit[1]) if hit[0] is not None else (None, None)


def catmull(P, n):
    out = []
    pts = [P[0]] + P + [P[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-1])
    return out


def strap(bm, guide, width, gap, thick, bvh, mat, up_bias_fn=lambda q: 0.0, smooth=2):
    """Flat strap laid on the outer surface along a guide polyline: centre line projected, offset gap + thick/2,
    cross direction = normal x tangent. Closed box section (top, bottom, two edges)."""
    C, N = [], []
    for q in guide:
        p, n = project_out(q, bvh, up_bias=up_bias_fn(q))
        if p is None:
            continue
        C.append(p); N.append(n.normalized())
    for _ in range(smooth):                                   # relax the projected line and normals
        C = [C[0]] + [(C[i - 1] + C[i] * 2 + C[i + 1]) / 4 for i in range(1, len(C) - 1)] + [C[-1]]
        N = [N[0]] + [(N[i - 1] + N[i] * 2 + N[i + 1]).normalized() for i in range(1, len(N) - 1)] + [N[-1]]
    rows = []
    for i, (c, n) in enumerate(zip(C, N)):
        t = (C[min(i + 1, len(C) - 1)] - C[max(i - 1, 0)]).normalized()
        b = n.cross(t).normalized()
        base = c + n * gap
        rows.append([base + b * (-width / 2), base + b * (width / 2),
                     base + n * thick + b * (width / 2), base + n * thick + b * (-width / 2)])
    V = [[bm.verts.new(p) for p in r] for r in rows]
    fs = []
    for k in range(len(V) - 1):
        for a in range(4):
            b_ = (a + 1) % 4
            fs.append(bm.faces.new((V[k][a], V[k][b_], V[k + 1][b_], V[k + 1][a])))
    for end_, flip in ((V[0], True), (V[-1], False)):
        fs.append(bm.faces.new(end_[::-1] if flip else end_))
    for f in fs:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    return C, N, fs


def box(bm, centre, xaxis, yaxis, zaxis, sx, sy, sz, mat, bevel=0.0):
    """Oriented box (half sizes sx, sy, sz along the given axes)."""
    corners = []
    for dz in (-1, 1):
        for dy in (-1, 1):
            for dx in (-1, 1):
                corners.append(centre + xaxis * dx * sx + yaxis * dy * sy + zaxis * dz * sz)
    vs = [bm.verts.new(p) for p in corners]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    fs = [bm.faces.new([vs[i] for i in q]) for q in quads]
    for f in fs:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    if bevel > 0:
        edges = list({e for f in fs for e in f.edges})
        res = bmesh.ops.bevel(bm, geom=edges + vs, offset=bevel, segments=2, affect="EDGES", profile=0.5)
        for f in res["faces"]:                      # bevel faces do not inherit the material
            f.material_index = mat
        fs = fs + list(res["faces"])
    return fs


def cylinder(bm, p0, p1, r, seg, mat, r1=None, flatten=1.0, side_axis=None):
    d = (p1 - p0).normalized()
    a = side_axis if side_axis is not None else d.orthogonal()
    a = (a - d * a.dot(d)).normalized()
    b = d.cross(a)
    rings = []
    for p, rr in ((p0, r), (p1, r if r1 is None else r1)):
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * i / seg) + b * math.sin(2 * math.pi * i / seg) * flatten) * rr)
                      for i in range(seg)])
    fs = [bm.faces.new((rings[0][i], rings[0][(i + 1) % seg], rings[1][(i + 1) % seg], rings[1][i])) for i in range(seg)]
    fs.append(bm.faces.new(rings[0][::-1]))
    fs.append(bm.faces.new(rings[1]))
    for f in fs:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    return fs


def new_object(name, bm, coll):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    make_mats(me)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


V_COLL = bpy.data.collections.new("HCL_Colete_Blockout")
B_COLL = bpy.data.collections.new("HCL_Mochila_Blockout")
for c in (V_COLL, B_COLL):
    bpy.context.scene.collection.children.link(c)

# =============================================================== VEST: crossbelt, waist belt, cartridge box, bayonet
vb = bmesh.new()
# 1. waist belt over the coat hem / top of the tails, brass buckle at the front
H_BELT = 1.112
ring = []
for i in range(64):
    th = 2 * math.pi * i / 64
    d = Vector((math.sin(th), -math.cos(th), 0))
    hit = TORSO_OUT.ray_cast(Vector((0, 0.02, Z(H_BELT))) + d * 0.4, -d, 0.6)
    ring.append((hit[0], hit[1]))
C = [p for p, _ in ring]
Nn = [Vector((n.x, n.y, 0)).normalized() for _, n in ring]
rows = []
for c, n in zip(C, Nn):
    base = c + n * S["belt_gap"]
    up = Vector((0, 0, 1))
    rows.append([base + up * (-S["waist_w"] / 2), base + up * (S["waist_w"] / 2),
                 base + n * S["belt_t"] + up * (S["waist_w"] / 2), base + n * S["belt_t"] + up * (-S["waist_w"] / 2)])
VV = [[vb.verts.new(p) for p in r] for r in rows]
belt_fs = []
for k in range(len(VV)):
    k2 = (k + 1) % len(VV)
    for a in range(4):
        b_ = (a + 1) % 4
        belt_fs.append(vb.faces.new((VV[k][a], VV[k][b_], VV[k2][b_], VV[k2][a])))
for f in belt_fs:
    f.material_index = BRANCO
bmesh.ops.recalc_face_normals(vb, faces=belt_fs)
front = C[0] + Nn[0] * (S["belt_gap"] + S["belt_t"])
buckle = box(vb, front + Nn[0] * 0.003, Vector((1, 0, 0)), Vector((0, 0, 1)), Nn[0], 0.032, 0.029, 0.003, LATAO, bevel=0.0015)

# 2. crossbelt: over the left shoulder, across the chest to the cartridge box behind the right hip, and down the back
G_FRONT = [Vector((0.15, 0.035, Z(1.585))), Vector((0.118, -0.06, Z(1.52))), Vector((0.07, -0.12, Z(1.42))),
           Vector((-0.01, -0.145, Z(1.30))), Vector((-0.09, -0.135, Z(1.19))), Vector((-0.16, -0.08, Z(1.08))),
           Vector((-0.19, 0.03, Z(1.02))), Vector((-0.15, 0.13, Z(0.99)))]
G_BACK = [Vector((0.15, 0.035, Z(1.585))), Vector((0.12, 0.11, Z(1.50))), Vector((0.06, 0.155, Z(1.38))),
          Vector((-0.02, 0.165, Z(1.25))), Vector((-0.08, 0.17, Z(1.12))), Vector((-0.11, 0.17, Z(1.03)))]
shoulder_bias = lambda q: 1.6 * max(0.0, min(1.0, (q.z - Z(1.47)) / 0.08))   # rays from above over the shoulder
cf_C, cf_N, _ = strap(vb, catmull(G_FRONT, 8), S["cross_w"], S["belt_gap"] + S["belt_t"] + 0.001, S["belt_t"],
                      TORSO_OUT, BRANCO, up_bias_fn=shoulder_bias)
cb_C, cb_N, _ = strap(vb, catmull(G_BACK, 8), S["cross_w"], S["belt_gap"] + S["belt_t"] + 0.001, S["belt_t"],
                      TORSO_OUT, BRANCO, up_bias_fn=shoulder_bias)

# 3. cartridge box: black leather, at the right rear hip, back face against the tails, flap on top
pb, nb_ = project_out(Vector((-0.12, 0.16, Z(0.985))), TORSO_OUT)
nb_ = Vector((nb_.x, nb_.y, 0)).normalized()
xa = Vector((0, 0, 1)).cross(nb_).normalized()                   # along the body, horizontal
centre = pb + nb_ * (0.008 + S["box_d"] / 2)
box(vb, centre, xa, Vector((0, 0, 1)), nb_, S["box_w"] / 2, S["box_h"] / 2, S["box_d"] / 2, PRETO, bevel=0.006)
box(vb, centre + Vector((0, 0, S["box_h"] / 2 - 0.035)) + nb_ * 0.004, xa, Vector((0, 0, 1)), nb_,
    S["box_w"] / 2 + 0.004, 0.041, S["box_d"] / 2 + 0.002, PRETO, bevel=0.003)           # flap over the lid
box(vb, centre + nb_ * (S["box_d"] / 2 + 0.0045) + Vector((0, 0, 0.012)), xa, Vector((0, 0, 1)), nb_,
    0.030, 0.022, 0.0012, LATAO, bevel=0.0006)                                          # plain brass plate on the flap

# 4. bayonet: frog on the waist belt at the left hip, black scabbard with brass chape, socket and blade elbow above
th_f = math.radians(100)                                          # left side, slightly behind
d_f = Vector((math.sin(th_f), -math.cos(th_f), 0))
hit = TORSO_OUT.ray_cast(Vector((0, 0.02, Z(H_BELT))) + d_f * 0.4, -d_f, 0.6)
pf_, nf_ = hit[0], Vector((hit[1].x, hit[1].y, 0)).normalized()
frog_c = pf_ + nf_ * (S["belt_gap"] + S["belt_t"] + 0.006)
box(vb, frog_c + Vector((0, 0, -0.035)), Vector((0, 0, 1)).cross(nf_).normalized(), Vector((0, 0, 1)), nf_,
    0.022, 0.06, 0.004, BRANCO, bevel=0.0015)                     # frog (white leather loop)
s0 = frog_c + nf_ * 0.010 + Vector((0, 0, -0.01))
# the tails flare out below the belt: the scabbard hangs from the frog and rests on the OUTSIDE of the tail
tilt = Matrix.Rotation(math.radians(14), 3, Vector((0, 0, 1)).cross(nf_).normalized())   # hangs slightly backwards
q = s0 + (tilt @ Vector((0, 0, -1))) * S["scab_len"]
pt, nt = project_out(q, LEGS_OUT)
s1 = pt + Vector((nt.x, nt.y, 0)).normalized() * 0.016 if pt is not None else q
pm, nm_ = project_out((s0 + s1) / 2, LEGS_OUT)                  # the middle rests on the hip, outside the tail
mid = (s0 + s1) / 2
sm = pm + Vector((nm_.x, nm_.y, 0)).normalized() * 0.016 if pm is not None else mid
if (sm - mid).dot(Vector((nf_.x, nf_.y, 0))) < 0:                 # only ever pushed outward
    sm = mid
down = (sm - s0).normalized()
side = Vector((0, 0, 1)).cross(nf_)
print(f"scabbard: top h {s0.z - GROUND:.3f}, bottom h {s1.z - GROUND:.3f}, length {(sm - s0).length + (s1 - sm).length:.3f} m")
cylinder(vb, s0, s0 + down * 0.035, 0.014, 8, LATAO, flatten=0.55, side_axis=side)                         # locket
cylinder(vb, s0 + down * 0.035, sm, 0.012, 8, PRETO, r1=0.0105, flatten=0.55, side_axis=side)
d2 = (s1 - sm).normalized()
cylinder(vb, sm, s1 - d2 * 0.06, 0.0105, 8, PRETO, r1=0.008, flatten=0.55, side_axis=side)
cylinder(vb, s1 - d2 * 0.06, s1, 0.008, 8, LATAO, r1=0.004, flatten=0.55, side_axis=side)                   # chape
sock0 = s0 + nf_ * 0.004
cylinder(vb, sock0, sock0 + Vector((0, 0, S["socket_len"])) + nf_ * 0.01, S["socket_r"], 10, FERRO)       # socket
cylinder(vb, sock0 + Vector((0, 0, 0.02)), sock0 + Vector((0, 0, 0.02)) + nf_ * 0.035, 0.006, 6, FERRO)    # elbow
vest = new_object("HCL_V_Pruss1813_Correame_blockout", vb, V_COLL)

# =============================================================== BACKPACK: knapsack, calfskin flap, greatcoat roll, straps
kb = bmesh.new()
# back plane of the coat: rays from behind at the pack's corners
samples = []
for x in (-0.12, 0.0, 0.12):
    for h in (1.20, 1.30, 1.42):
        hit = TORSO_OUT.ray_cast(Vector((x, 0.8, Z(h))), Vector((0, -1, 0)), 1.5)
        if hit[0] is not None:
            samples.append(hit[0])
y_back = max(p.y for p in samples)                                 # the pack rests on the most prominent point
lean = math.atan2(max(p.y for p in samples if abs(p.z - Z(1.42)) < 0.01) - max(p.y for p in samples if abs(p.z - Z(1.20)) < 0.01), 0.22)
ax_x = Vector((1, 0, 0))
ax_z = (Matrix.Rotation(-lean, 3, ax_x) @ Vector((0, 0, 1))).normalized()   # pack's up, following the back
ax_y = ax_z.cross(ax_x).normalized() * -1                          # pack's depth, pointing away from the back (+y)
if ax_y.y < 0:
    ax_y = -ax_y
pc = Vector((0, y_back + 0.006 + S["pack_d"] / 2, Z(1.31)))
box(kb, pc, ax_x, ax_z, ax_y, S["pack_w"] / 2, S["pack_h"] / 2, S["pack_d"] / 2, PRETO, bevel=0.012)       # body
flap_c = pc + ax_y * 0.004 + ax_z * (S["pack_h"] / 2 - 0.10)
box(kb, flap_c, ax_x, ax_z, ax_y, S["pack_w"] / 2 + 0.005, 0.105, S["pack_d"] / 2 + 0.003, BEZERRO, bevel=0.01)  # calfskin flap
for sx in (-1, 1):                                                 # flap buckle straps
    box(kb, pc + ax_x * sx * 0.10 + ax_y * (S["pack_d"] / 2 + 0.006) + ax_z * (-0.02), ax_x, ax_z, ax_y,
        0.012, 0.06, 0.002, PRETO, bevel=0.001)
# greatcoat roll on top, wider than the pack, with two white straps
top = pc + ax_z * (S["pack_h"] / 2 + S["roll_r"] - 0.006) + ax_y * 0.004
cylinder(kb, top - ax_x * S["roll_len"] / 2, top + ax_x * S["roll_len"] / 2, S["roll_r"], 14, CAPOTE, side_axis=ax_z)
for sx in (-0.12, 0.12):
    cylinder(kb, top + ax_x * (sx - 0.012), top + ax_x * (sx + 0.012), S["roll_r"] + 0.004, 14, BRANCO, side_axis=ax_z)
# shoulder straps: from the top corners of the pack, over the shoulders, down the chest, under the arms, to the bottom corners
for s in (1, -1):
    g = [pc + ax_x * s * 0.10 + ax_z * (S["pack_h"] / 2 - 0.02) + ax_y * (-S["pack_d"] / 2),
         Vector((s * 0.135, 0.10, Z(1.535))), Vector((s * 0.145, 0.02, Z(1.585))), Vector((s * 0.145, -0.07, Z(1.53))),
         Vector((s * 0.155, -0.115, Z(1.42))), Vector((s * 0.185, -0.08, Z(1.31))), Vector((s * 0.20, 0.02, Z(1.24))),
         Vector((s * 0.17, 0.12, Z(1.19))), pc + ax_x * s * 0.15 + ax_z * (-S["pack_h"] / 2 + 0.03) + ax_y * (-S["pack_d"] / 2)]
    strap(kb, catmull(g, 7), S["strap_w"], S["strap_gap"], 0.003, TORSO_OUT, BRANCO,
          up_bias_fn=lambda q: 1.6 * max(0.0, min(1.0, (q.z - Z(1.47)) / 0.08)))
pack = new_object("HCL_B_Pruss1813_Tornister_blockout", kb, B_COLL)

# ---------------------------------------------------------------- checks
dg = bpy.context.evaluated_depsgraph_get()
print(f"VEST tris {tris(vest)}   BACKPACK tris {tris(pack)}")
body = bpy.data.objects["REF_corpo_A3_character_example"]


def inside_uniform(ob):
    """Equipment vertices that sit under the uniform's outer surface (ray to outside crosses the uniform)."""
    found = []
    for v in ob.data.vertices:
        p = ob.matrix_world @ v.co
        d = Vector((p.x, p.y - 0.02, 0))
        if d.length < 1e-6:
            continue
        d.normalize()
        hit = ALL_U.ray_cast(p + d * 0.0005, d, 0.25)
        if hit[0] is not None and hit[1].dot(d) > 0:      # leaving through an outward-facing uniform face
            found.append((p, hit[2], hit[3]))
    return found


for ob in (vest, pack):
    f_ = inside_uniform(ob)
    print(f"{ob.name}: vertices under the uniform surface {len(f_)} of {len(ob.data.vertices)}")
    groups = {}
    for p, fi, dist in f_:
        key = (round(p.x, 1), round(p.y, 1), round(p.z - GROUND, 1))
        groups.setdefault(key, []).append(dist)
    for k, ds in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:8]:
        print(f"    near x{k[0]:+.1f} y{k[1]:+.1f} h{k[2]:.1f}: {len(ds)} vertices, depth up to {max(ds)*1000:.1f} mm")
print(f"waist belt circumference {sum((C[i] - C[i - 1]).length for i in range(len(C))):.3f} m; "
      f"crossbelt front {sum((cf_C[i] - cf_C[i - 1]).length for i in range(1, len(cf_C))):.3f} m, "
      f"back {sum((cb_C[i] - cb_C[i - 1]).length for i in range(1, len(cb_C))):.3f} m; pack lean {math.degrees(lean):.1f} deg")

# ---------------------------------------------------------------- renders
if RENDER:
    scene = bpy.context.scene
    for nm, en, rot in (("REF_sol", 3.2, (50, 0, 25)), ("REF_preench", 1.3, (65, 0, 200)), ("REF_contra", 1.0, (60, 0, 120))):
        lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN"))
        lo.data.energy = en
        lo.rotation_euler = tuple(math.radians(a) for a in rot)
        REFC.objects.link(lo)
    world = bpy.data.worlds.new("REF_mundo")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.93, 0.93, 0.93, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 40
    scene.view_settings.view_transform = "Standard"
    for ob in (uni, vest, pack):
        for p in ob.data.polygons:
            p.use_smooth = True
        ob.data.set_sharp_from_angle(angle=math.radians(35))

    def cam(name, loc, target, lens=55, ortho=None):
        c = bpy.data.cameras.new(name)
        if ortho:
            c.type = "ORTHO"; c.ortho_scale = ortho
        else:
            c.lens = lens
        o = bpy.data.objects.new(name, c)
        o.location = loc
        o.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        REFC.objects.link(o)
        return o

    T = Vector((0, 0, Z(1.0)))
    shots = [("frente", cam("CAM_f", (0, -8, Z(0.98)), Vector((0, 0, Z(0.98))), ortho=2.15), (900, 1100)),
             ("lado", cam("CAM_l", (8, 0, Z(0.98)), Vector((0, 0, Z(0.98))), ortho=2.15), (900, 1100)),
             ("costas", cam("CAM_c", (0, 8, Z(0.98)), Vector((0, 0, Z(0.98))), ortho=2.15), (900, 1100)),
             ("tres_quartos", cam("CAM_3q", (2.6, -3.6, Z(1.35)), T), (900, 1100)),
             ("tres_quartos_costas", cam("CAM_3qc", (-2.6, 3.6, Z(1.45)), T), (900, 1100)),
             ("detalhe_cartucheira", cam("CAM_cart", (-1.0, 1.4, Z(1.25)), Vector((-0.12, 0.12, Z(1.05))), lens=60), (1000, 900)),
             ("detalhe_baioneta", cam("CAM_bai", (1.6, -0.9, Z(1.10)), Vector((0.15, 0.0, Z(0.95))), lens=60), (1000, 900))]
    for name, c, (rx, ry) in shots:
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT_IMG, f"equip_blockout_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    scene.camera = shots[0][1]

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
