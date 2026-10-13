# Bearskin ("bonnet a poil") of the French Imperial Guard foot grenadiers and chasseurs (Old Guard), Phases 3-4
# (blockout + production geometry). Spec: docs/specs/velha_guarda.md. User decisions 2026-10-12: start the Old Guard,
# "profissional e com bastante detalhe nos modelos"; top patch with a WHITE CROSS (historical, 🔶) instead of the
# mod's white grenade.
# What the mod art shows (FranceINF c1-c2 r4, FranceINF_3 c1-c2 r4-r5; Reto pack, authorised; 🎮): black fur in
# clumps, a red top patch, a brass front plate (eagle between grenades, pointed bottom), white and red cords with
# raquettes and fringed tassels, a red plume, a tricolour cockade. Proportions are NOT in the art (no side view): 🔶.
# Geometry (no alpha textures: every hair lock is real geometry, like the feathers of plumet.py):
#   pele_corpo   shell: band fitted on the official head band (shako_fit.py), swelling to 1.24x at 60 % of the side,
#                rounded dome; low-frequency tufts so the silhouette is not a turned solid
#   pelo         hundreds of hair locks: narrow double-sided ribbons rooted on the shell, lying down it (gravity along
#                the surface, random turn), tip lifted and curled; shorter above the plate so they never cover it
#   placa        brass plate traced from the mod art (UV layer "arte" -> relief baked from the art), on the fur front
#   calota       red top patch on the back of the dome; cruz_galao: white lace cross on it
#   cocar_*      tricolour cockade on the left side, under the plume; tulipa + plumet: red plume (chasseurs: red over
#                green), plumet.py v3
#   cordao, raquete, borla: white cords: festoon across the front, two raquettes and two tassels on the right side
# Variants: granadeiro_gala (plate, cords, plume), granadeiro_campanha (plate only), cacador_gala (no plate, cords,
# red-over-green plume). Layout read by texturizar_shako_fr.py raiz=GD_ nome=HCL_Bonnet_Fr_ textura=hcl_bonnet_fr_.
#   blender -b --factory-startup --python blockout_bonnet_guarda.py -- <Test_Character_01 dir> <out.blend> <render dir>
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit
from plumet import plumet, feather_material

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- proportions (PROPOSED, 🔶)
HS = 0.262              # straight-ish side up to the dome
DOME = 0.068            # dome height (total ~0.33 m above the band)
SWELL = 1.24            # widest / band
PLATE_W, PLATE_STRETCH = 0.128, 1.90      # plate width; vertical stretch of the mod art (its tile is squashed 🔶)
PLATE_Z0 = 0.016
COCK_R = 0.030
PLUME_H = 0.36          # user 2026-10-12: bigger plumes (was 0.30)
PLUME_R = 0.050
WALL, CLEAR, TILT, DEPTH_RATIO = shako_fit.WALL, shako_fit.CLEAR, shako_fit.TILT, shako_fit.DEPTH_RATIO

F = shako_fit.compute(SAMPLES)
base_hw = F["head_hw"] + WALL + CLEAR + 0.004          # fur thickness at the band
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR + 0.004)
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.006))) @ Matrix.Rotation(-TILT, 4, 'X')
ATLAS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "ntw", "france", "FranceINF_diffuse.png"))
ATLAS_PX = 4096
PLATE_JSON = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "bonnet", "hcl_bonnet_fr", "placa_bonnet_guarda.json"))

COL = dict(pelo=(0.010, 0.009, 0.008), latao=(0.70, 0.50, 0.16), vermelho=(0.55, 0.03, 0.03), branco=(0.82, 0.82, 0.80),
           azul=(0.04, 0.08, 0.35), verde=(0.03, 0.20, 0.06))
MATS, PMATS, PARTS = {}, {}, []


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name == "latao" else 0.8
        b.inputs["Metallic"].default_value = 1.0 if name == "latao" else 0.0
        MATS[name] = m
    return MATS[name]


def pmat(name):
    if name not in PMATS:
        m = bpy.data.materials.new("BO_plumet_" + name); m.use_nodes = True
        feather_material(m, COL[name]); PMATS[name] = m
    return PMATS[name]


def finish(bm, name, colour, parent, by_colour=None, keep_normals=False, plume=False, smooth=True):
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
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); ob.parent = parent
    scene.collection.objects.link(ob); PARTS.append(ob)
    return ob


def grid(bm, rows, closed_u=True):
    nc = len(rows[0])
    for j in range(len(rows) - 1):
        for i in range(nc - (0 if closed_u else 1)):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nc], rows[j + 1][(i + 1) % nc], rows[j + 1][i]))


# ---------------------------------------------------------------- the shell surface S(theta, s)
# profile: (radius factor, z) from the band (s = 0) over the side and the dome to the top (s = 1), by arc length
prof = []
for k in range(25):
    t = k / 24
    prof.append((1.0 + (SWELL - 1.0) * math.sin(math.pi / 2 * min(1.0, t / 0.62)) ** 1.25 - 0.015 * max(0.0, t - 0.62) / 0.38, HS * t))
rf_top = prof[-1][0]
for k in range(1, 13):
    a = math.pi / 2 * k / 12
    prof.append((rf_top * math.cos(a) if k < 12 else 0.0, HS + DOME * math.sin(a)))
L_ = [0.0]
for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
    L_.append(L_[-1] + math.hypot((r1 - r0) * base_hd, z1 - z0))
L_ = np.array(L_) / L_[-1]
PR = np.array(prof)
S_SIDE = float(np.interp(HS, PR[:, 1], L_))     # s at the top of the side


def tuft(th, s):
    """Low-frequency lumps of the fur mass (m), deterministic."""
    return 0.0050 * (math.sin(5 * th + 1.3) * math.sin(9 * s + 0.4) + 0.6 * math.sin(11 * th - 7 * s + 2.0)) * min(1.0, s * 8)


def S(th, s, off=0.0, lumps=True):
    """Shell point; th = 0 is the FRONT (-Y), +90 deg the wearer's left (+X). off along the outward normal."""
    rf = float(np.interp(s, L_, PR[:, 0])); z = float(np.interp(s, L_, PR[:, 1]))
    p = Vector((base_hw * rf * math.sin(th), -base_hd * rf * math.cos(th), z))
    if off or lumps:
        n = Sn(th, s)
        p = p + n * (off + (tuft(th, s) if lumps else 0.0))
    return p


def Sn(th, s, e=1e-3):
    def raw(t_, s_):
        rf = float(np.interp(s_, L_, PR[:, 0])); z = float(np.interp(s_, L_, PR[:, 1]))
        return Vector((base_hw * rf * math.sin(t_), -base_hd * rf * math.cos(t_), z))
    s0, s1 = max(0.0, s - e), min(1.0, s + e)
    dth = raw(th + e, s) - raw(th - e, s)
    ds = raw(th, s1) - raw(th, s0)
    n = dth.cross(ds)
    if n.length < 1e-9:
        return Vector((0, 0, 1))
    n.normalize()
    c = raw(th, s)
    return n if n.dot(Vector((c.x, c.y, 0.0)) + Vector((0, 0, 0.3 * (c.z - HS * 0.5)))) > 0 else -n


def s_of_z(z):
    return float(np.interp(z, PR[:25, 1], L_[:25]))


# ---------------------------------------------------------------- pieces
def shell(tag, root):
    bm = bmesh.new()
    NT, NSS = 48, 26
    rows = [[bm.verts.new(S(2 * math.pi * i / NT, j / NSS)) for i in range(NT)] for j in range(NSS)]
    grid(bm, rows)
    top = bm.verts.new(S(0.0, 1.0))
    for i in range(NT):
        bm.faces.new((rows[-1][i], rows[-1][(i + 1) % NT], top))
    # inner face of the band (seen from below): a short lining ring
    inner = [bm.verts.new(Vector((base_hw * math.sin(2 * math.pi * i / NT) * 0.97, -base_hd * math.cos(2 * math.pi * i / NT) * 0.97, 0.0))) for i in range(NT)]
    inner2 = [bm.verts.new(Vector((base_hw * math.sin(2 * math.pi * i / NT) * 0.95, -base_hd * math.cos(2 * math.pi * i / NT) * 0.95, 0.05))) for i in range(NT)]
    grid(bm, [inner2, inner, rows[0]])
    finish(bm, f"{tag}_pele_corpo", "pelo", root)


def art_uv(px, py):
    return (px / ATLAS_PX, 1.0 - py / ATLAS_PX)


def plate(tag, root):
    """Brass plate from the traced outline, wrapped on the front of the fur, 7 mm proud of the shell (it rests on the
    fur), with thickness; UV "arte" = the same point in the mod art."""
    bj = json.load(open(PLATE_JSON))
    X0, Y0 = bj["box"][:2]
    loop = bj["loops"][0]
    xs = [x for x, _ in loop]; ys = [y for _, y in loop]
    kf = PLATE_W / (max(xs) - min(xs))
    cx = (max(xs) + min(xs)) / 2
    h_ = (max(ys) - min(ys)) * kf * PLATE_STRETCH
    z_top = PLATE_Z0 + h_
    # subdivided fill: a grid inside the outline (the plate is curved over the fur)
    cu = bpy.data.curves.new("pc", "CURVE"); cu.dimensions, cu.fill_mode = "2D", "BOTH"
    sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1)
    for p_, (x, y) in zip(sp.points, loop):
        p_.co = (x, -y, 0.0, 1.0)
    sp.use_cyclic_u = True
    cu.extrude = 0.0011 / kf
    tob = bpy.data.objects.new("pc", cu); scene.collection.objects.link(tob)
    bpy.context.view_layer.update()
    me0 = bpy.data.meshes.new_from_object(tob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tob); bpy.data.curves.remove(cu)
    ub = bmesh.new(); ub.from_mesh(me0); bpy.data.meshes.remove(me0)
    bmesh.ops.triangulate(ub, faces=ub.faces[:])
    for _ in range(8):
        long_e = [e for e in ub.edges if e.calc_length() * kf > 0.020]
        if not long_e:
            break
        bmesh.ops.subdivide_edges(ub, edges=long_e, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(ub, faces=[f for f in ub.faces if len(f.verts) > 3])
    zmin = min(v.co.z for v in ub.verts)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("arte")
    vm = {}
    ymax = max(ys)
    for v in ub.verts:
        lx = (v.co.x - cx) * kf
        lz = (ymax + v.co.y) * kf * PLATE_STRETCH            # v.co.y = -y_image: bottom of the outline -> lz = 0
        thick = (v.co.z - zmin) * kf
        z = PLATE_Z0 + lz
        s = s_of_z(z)
        rf = float(np.interp(s, L_, PR[:, 0]))
        th = lx / (base_hd * rf)
        vm[v.index] = (bm.verts.new(S(th, s, 0.007 + thick, lumps=False)), art_uv(X0 + v.co.x, Y0 - v.co.y))
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
    ob = finish(bm, f"{tag}_placa", "latao", root, keep_normals=True)
    print(f"PLACA {tag}: {PLATE_W * 1000:.0f} x {h_ * 1000:.0f} mm, z {PLATE_Z0:.3f}..{z_top:.3f}, {len(ob.data.polygons)} faces")
    half_th = PLATE_W / 2 / (base_hd * 1.05)
    return (PLATE_Z0, z_top, half_th)


def top_patch(tag, root):
    """Red top patch on the back of the dome, a white lace cross on it. Returns (centre th, s, radius) to keep the
    hair locks off it."""
    th0, s0 = math.pi, S_SIDE + (1 - S_SIDE) * 0.30
    c = S(th0, s0, 0.0, lumps=False)
    n = Sn(th0, s0)
    u = Vector((1, 0, 0)); v_ = n.cross(u).normalized(); u = v_.cross(n).normalized()
    R_ = 0.046
    bm = bmesh.new()
    NR, NA = 5, 32
    rings = []
    for j in range(1, NR + 1):
        r = R_ * j / NR
        ring = []
        for i in range(NA):
            a = 2 * math.pi * i / NA
            p = c + (u * math.cos(a) + v_ * math.sin(a)) * r
            ring.append(bm.verts.new(p + n * (0.0075 - 0.0025 * (r / R_) ** 2)))   # padded cloth, edges into the fur
        rings.append(ring)
    cv = bm.verts.new(c + n * 0.0075)
    for i in range(NA):
        bm.faces.new((cv, rings[0][i], rings[0][(i + 1) % NA]))
    grid(bm, rings)
    finish(bm, f"{tag}_calota", "vermelho", root)
    # cross: two lace strips 9 mm wide, 1.2 mm thick, from rim to rim (🔶 user choice)
    for k, (a_, b_) in enumerate(((u, v_), (v_, u))):
        bm = bmesh.new()
        pts = [c + a_ * (R_ * 0.92 * t) for t in np.linspace(-1, 1, 13)]
        rows = []
        for p in pts:
            r = (p - c).length
            h = 0.0075 - 0.0025 * (r / R_) ** 2 + 0.0004
            rows.append([bm.verts.new(p + n * h + b_ * sx * 0.0045 + n * sz * 0.0012) for sx, sz in ((-1, 0), (1, 0), (1, 1), (-1, 1))])
        grid(bm, rows)
        for r_, sg in ((rows[0], -1), (rows[-1], 1)):
            bm.faces.new(r_ if sg > 0 else r_[::-1])
        finish(bm, f"{tag}_cruz_galao_{k}", "branco", root, smooth=False)
    return th0, s0, R_


def disc(name, centre, normal, r, t, colour, parent, segs=24):
    bm = bmesh.new()
    u = normal.orthogonal().normalized(); v = normal.cross(u).normalized()
    rows = [[bm.verts.new(centre + normal * a + rr * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)]
            for a, rr in ((0, 0.0005), (0, r), (t, r), (t, 0.0005))]
    grid(bm, rows)
    return finish(bm, name, colour, parent)


def lathe_obj(name, profile, centre, colour, parent, axis=Vector((0, 0, 1)), segs=20):
    bm = bmesh.new()
    u = axis.orthogonal().normalized(); v = axis.cross(u).normalized()
    rows = [[bm.verts.new(centre + axis * a + r * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)] for a, r in profile]
    grid(bm, rows)
    for ring, a in ((rows[0], profile[0][0]), (rows[-1], profile[-1][0])):
        cc = bm.verts.new(centre + axis * a)
        for i in range(segs):
            bm.faces.new((cc, ring[i], ring[(i + 1) % segs]))
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


def tube(name, path, r, colour, parent, segs=8):
    bm = bmesh.new()
    rows = []
    for k, p in enumerate(path):
        tng = (path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]).normalized()
        nrm = tng.orthogonal().normalized(); side = tng.cross(nrm)
        rows.append([bm.verts.new(p + r * (math.cos(2 * math.pi * s / segs) * nrm + math.sin(2 * math.pi * s / segs) * side)) for s in range(segs)])
    grid(bm, rows)
    for ring, p in ((rows[0], path[0]), (rows[-1], path[-1])):
        cc = bm.verts.new(p)
        for i in range(segs):
            bm.faces.new((cc, ring[i], ring[(i + 1) % segs]))
    return finish(bm, name, colour, parent)


def fringe_tassel(name, top, colour, parent, r=0.010, length=0.040, strands=20, seed=3):
    rnd = random.Random(seed)
    lathe_obj(name + "_cabeca", [(0.0, 0.002), (-0.006, 0.007), (-0.013, r), (-0.015, r * 0.85)], top, colour, parent, segs=12)
    bm = bmesh.new()
    for i in range(strands):
        a = 2 * math.pi * i / strands + rnd.uniform(-0.12, 0.12)
        o = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-math.sin(a), math.cos(a), 0))
        L = length * rnd.uniform(0.9, 1.08)
        rows = []
        for t_ in (0.0, 0.5, 1.0):
            c = top + Vector((0, 0, -0.013 - L * t_)) + o * (r * 0.9 + 0.004 * t_)
            hw = 0.0016 * (1 - 0.4 * t_)
            rows.append((bm.verts.new(c - sd * hw), bm.verts.new(c + sd * hw)))
        for (a0, b0), (a1, b1) in zip(rows, rows[1:]):
            bm.faces.new((a0, b0, b1, a1))
        rows2 = [(bm.verts.new(a0.co - o * 0.0003), bm.verts.new(b0.co - o * 0.0003)) for a0, b0 in rows]
        for (a0, b0), (a1, b1) in zip(rows2, rows2[1:]):
            bm.faces.new((a1, b1, b0, a0))
    return finish(bm, name + "_franja", colour, parent, keep_normals=True)


def cords(tag, root):
    """White parade cords: a festoon across the front over the plate, hanging on the right side (-X) in two raquettes
    with fringed tassels."""
    off = 0.016
    fest = catmull([S(math.radians(-118), s_of_z(0.235), off, False), S(math.radians(-60), s_of_z(0.19), off, False),
                    S(0.0, s_of_z(0.168), off + 0.002, False), S(math.radians(60), s_of_z(0.19), off, False),
                    S(math.radians(118), s_of_z(0.235), off, False)], 8)
    tube(f"{tag}_cordao", fest, 0.0038, "branco", root)
    side = S(math.radians(-102), s_of_z(0.205), off, False)
    hang = catmull([S(math.radians(-118), s_of_z(0.235), off, False), side, side + Vector((0, 0, -0.04))], 6)
    tube(f"{tag}_cordao_lado", hang, 0.0038, "branco", root)
    n = Sn(math.radians(-102), s_of_z(0.10)); n.z = 0; n.normalize()
    for k, dz in enumerate((-0.060, -0.112)):
        rq = side + Vector((0, 0, dz)) + n * (0.005 + 0.003 * k)
        ob = lathe_obj(f"{tag}_raquete_{k}", [(-0.030, 0.002), (-0.021, 0.013), (0.0, 0.0175), (0.021, 0.013), (0.030, 0.002)],
                       rq, "branco", root, segs=16)
        for v in ob.data.vertices:                         # a raquette is a flat woven oval, not a ball
            d = v.co - rq
            v.co = rq + d - n * d.dot(n) * 0.62
    tb = side + Vector((0, 0, -0.140)) + n * 0.010
    for dx, sd in ((-0.012, 7), (0.012, 8)):
        t0 = tb + Vector((dx * n.y, -dx * n.x, 0.0))
        fringe_tassel(f"{tag}_borla_{sd}", t0, "branco", root, seed=sd)


def plume_and_cockade(tag, root, colours):
    th = math.radians(88)                                   # wearer's left
    zc = 0.172
    s = s_of_z(zc)
    n = Sn(th, s)
    c0 = S(th, s, 0.009, False)
    disc(f"{tag}_cocar_vermelho", c0, n, COCK_R, 0.003, "vermelho", root)
    disc(f"{tag}_cocar_branco", c0 + n * 0.003, n, COCK_R * 0.66, 0.0015, "branco", root)
    disc(f"{tag}_cocar_azul", c0 + n * 0.0045, n, COCK_R * 0.33, 0.0015, "azul", root)
    if not colours:
        return
    sb = s_of_z(0.205)
    base = S(th, sb, 0.020, False)
    lathe_obj(f"{tag}_tulipa", [(-0.018, 0.0045), (0.0, 0.0065), (0.012, 0.010)], base, "latao", root)
    bm = bmesh.new()
    by = plumet(bm, base + Vector((0, 0, 0.012)), H=PLUME_H, R=PLUME_R, colours=colours, seed=sum(map(ord, tag)), lean=0.02,
                rings=38, per_ring=19, feather_len=0.054)
    finish(bm, f"{tag}_plumet", None, root, by_colour=by, keep_normals=True, plume=True)


def hair(tag, root, plate_box, patch, seed=5):
    """Hair locks in two layers (v2, user 2026-10-12 "traz mais realismo a bear skin"):
      - under-fur: short dense locks lying flat, so no smooth shell shows between the long locks;
      - top locks: long narrow bundles lying down the surface (gravity along it), tips lifted and curled; on the dome
        they swirl out of a crown; at the lower edge the longest hang over the band (not at the forehead); around the
        plate they are lifted over its edges (the plate is mounted ON the fur), never across its face.
    Each lock: 3 stations (root, middle, tip) x 3 points (edges curled into the mass, raised middle) = 8 triangles,
    single-sided (the underside lies against the shell). UV u across / v along, face float 'tint' = shade tile."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    tint = bm.faces.layers.float.new("tint")
    z_p0, z_p1, half_th = plate_box if plate_box else (None, None, None)
    th_c, s_c, R_c = patch
    pc = S(th_c, s_c, 0.0, False)
    count = {"base": 0, "longa": 0}

    def lock(th, s, L, W, lift, extra_ang=0.0, drop_below=0.0, short=False, near_plate=False):
        p0 = S(th, s, 0.0)
        n = Sn(th, s)
        g = Vector((0, 0, -1)) - n * (-n.z)
        if g.length < 0.15:
            g = Vector((p0.x, p0.y, 0.0))
        g.normalize()
        side = n.cross(g).normalized()
        ang = rnd.uniform(-0.55, 0.55) + extra_ang
        if near_plate:
            ang = rnd.uniform(-0.15, 0.15)                  # straight down beside / above the plate
        d = (g * math.cos(ang) + side * math.sin(ang)).normalized()
        sd = n.cross(d).normalized()
        curl = rnd.uniform(-0.007, 0.007)
        pts, wid = [], []
        st = ((0.0, 0.95), (1.0, 0.20)) if short else ((0.0, 0.80), (0.50, 1.0), (1.0, 0.12))
        for t, wf in st:
            p = p0 + n * (0.0015 + lift * t ** 1.6) + d * (L * t) + sd * (curl * t * t)
            if drop_below and t > 0:                       # over the band edge: the tip falls straight down
                p = p + Vector((0, 0, -drop_below * t ** 2))
            pts.append(p); wid.append(W * wf / 2)
        sh = rnd.uniform(0.0, 1.0)
        rows = []
        for p, hw, (t, _) in zip(pts, wid, st):
            cup = n * (0.35 * hw)
            rows.append((bm.verts.new(p - sd * hw - cup), bm.verts.new(p + n * 0.0012), bm.verts.new(p + sd * hw - cup), t))
        for k in range(len(rows) - 1):
            (a0, m0, b0, t0), (a1, m1, b1, t1) = rows[k], rows[k + 1]
            for (x0, x1, y1, y0, u0, u1) in ((a0, m0, m1, a1, 0.0, 0.5), (m0, b0, b1, m1, 0.5, 1.0)):
                f = bm.faces.new((x0, x1, y1, y0))
                for l, uv in zip(f.loops, ((u0, t0), (u1, t0), (u1, t1), (u0, t1))):
                    l[uvl].uv = uv
                f[tint] = sh; f.smooth = True
                f.normal_update()
                if f.normal.dot(n) < 0:
                    f.normal_flip()

    def place(n_th, n_rows, layer):
        for j in range(n_rows):
            for i in range(n_th):
                s = (j + rnd.uniform(0.05, 0.95)) / n_rows * 0.985
                th = 2 * math.pi * (i + rnd.uniform(0.0, 1.0) + 0.5 * (j % 2)) / n_th
                th = (th + math.pi) % (2 * math.pi) - math.pi
                p0 = S(th, s, 0.0)
                z0 = p0.z
                if (p0 - pc).length < R_c + (0.004 if layer == "longa" else 0.0):
                    continue
                dome = max(0.0, (s - S_SIDE) / (1 - S_SIDE))
                swirl = 0.9 * dome                                  # locks wind out of a crown on the top
                if layer == "base":
                    L, W, lift = rnd.uniform(0.020, 0.032), rnd.uniform(0.008, 0.012), rnd.uniform(0.0008, 0.003)
                else:
                    L = rnd.uniform(0.045, 0.072) * (0.75 if dome > 0 else 1.0)
                    W, lift = rnd.uniform(0.009, 0.015), rnd.uniform(0.003, 0.010) * (0.6 if dome > 0 else 1.0)
                drop = 0.0
                if plate_box and abs(th) < half_th + 0.05 and z_p0 - 0.012 < z0 < z_p1 + L:
                    inside = abs(th) < half_th - 0.012 and z0 < z_p1 + 0.004
                    if inside:
                        continue                                    # never across the plate's face
                    if z0 >= z_p1 + 0.004:                          # above it: the tip stops above its top edge
                        L = min(L, (z0 - z_p1 - 0.003) / max(0.3, math.cos(0.55)))
                        if L < 0.014:
                            continue
                    else:
                        lift = max(lift, 0.011)                     # beside it: lifted over its edge
                if s < 0.10:                                        # lower edge
                    front = abs(th) < 0.65
                    if layer == "longa" and not front:
                        drop = rnd.uniform(0.004, 0.010)            # the long hair hangs over the band...
                        L = min(L, z0 + 0.022)                      # ...by at most ~2.5 cm
                    else:
                        L = min(L, z0 + 0.004)
                if L < 0.014:
                    continue
                near = bool(plate_box) and abs(th) < half_th + 0.08 and z0 < z_p1 + 0.08
                lock(th, s, L, W, lift, swirl, drop, short=layer == "base", near_plate=near)
                count[layer] += 1

    place(44, 22, "base")                                   # 4 triangles per lock
    place(42, 25, "longa")                                  # 8 triangles per lock
    finish(bm, f"{tag}_pelo", "pelo", root, keep_normals=True)
    return count


# ---------------------------------------------------------------- variants
def bonnet(tag, x_off, with_plate, plume_cols, with_cords):
    root = bpy.data.objects.new(f"GD_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    shell(tag, root)
    pb = plate(tag, root) if with_plate else None
    patch = top_patch(tag, root)
    plume_and_cockade(tag, root, plume_cols)
    if with_cords:
        cords(tag, root)
    nl = hair(tag, root, pb, patch, seed=sum(map(ord, tag)))
    print(f"PELO {tag}: {nl['base']} mechas curtas (sub-pelo) + {nl['longa']} longas")
    return root


VARIANTS = [("granadeiro_gala", True, [(0.0, "vermelho")], True),
            ("granadeiro_campanha", True, None, False),
            ("cacador_gala", False, [(0.0, "verde"), (0.55, "vermelho")], True)]
SPACING = 0.55
roots = [bonnet(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    per = {o.name[len(t) + 1:]: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}
    big = ", ".join(f"{k} {v}" for k, v in sorted(per.items(), key=lambda kv: -kv[1])[:5])
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    zmin = min((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:20s} pecas {len(obs):2d} triangulos {tris:6d} ({big}); z {zmin:.3f}..{zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

# ---------------------------------------------------------------- renders (approximate head)
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
hme.materials.append(skin)
for p in hme.polygons:
    p.use_smooth = True
for i in range(len(VARIANTS)):
    h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    scene.collection.objects.link(h)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
os.makedirs(RENDER_DIR, exist_ok=True)
zc = (ROOT @ Vector((0, 0, 0.20))).z


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 900)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_bonnet_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_tres_quartos", (mid_x + 1.2, -2.6, zc + 0.5), (mid_x, 0, zc), lens=45, res=(2000, 1000))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
for j, r in enumerate(roots):
    for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
        o.hide_render = j != 0
shot("granadeiro_frente", (0.0, -1.6, zc + 0.05), (0.0, 0.0, zc + 0.05), ortho=0.75, res=(900, 1100))
shot("granadeiro_lado", (-1.6, F["head_cy"], zc + 0.05), (0.0, F["head_cy"], zc + 0.05), ortho=0.75, res=(900, 1100))
shot("granadeiro_costas", (0.5, 1.3, zc + 0.6), (0.0, F["head_cy"], zc + 0.08), lens=55, res=(900, 1000))
shot("granadeiro_perto", (0.30, -0.55, zc + 0.05), (0.0, F["head_cy"] - 0.08, zc - 0.02), lens=55, res=(1000, 1000))
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
