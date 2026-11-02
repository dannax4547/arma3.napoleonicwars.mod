# Phase 3 (blockout / design model) of the Russian army infantry kivers, 1812-1814: shapes and flat identification
# colours, NO UVs or final textures. Research dossier: docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md (sources A1, R1,
# P1-P4, S1-S4; decisions D1-D17 are cited below). Spec: docs/specs/rus_1812.md 2.3, 2.4, 3, 8 (RU3, RU7).
#   blender -b --factory-startup --python blockout_kiver_rus.py -- <Test_Character_01 dir | -> <out.blend> <render dir>
# Head fit: the approved one of every shako (shako_fit.py, read on the Arma 3 Samples head band). When the Samples are
# not installed (machine of 2026-10-17), the same fit is READ BACK from the approved British blockout
# (source/models/shakos/hcl_shako_uk/hcl_shako_uk_blockout.blend): the cap root matrix (head_cy, z_forehead, tilt) and
# the approximate head (head_hw, head_hd, z_head_top). Re-run with the Samples to confirm.
# Helpers (bands, sweeps, lathes, tassels, chinscales) adapted from blockout_shako_fr.py, which is left untouched.
# History: v1 symmetric bell; v2 (2026-10-17) from the user's replica photos (U1-U3, low confidence); v3 (2026-10-17,
#   user: "utiliza fontes historicas ... mais profissional e detalhista") rebuilt on the dossier:
#   - body of matte BLACK CLOTH over leather; crown, bands, V straps and visor of LACQUERED leather (D4, R1 1817, S1-S2)
#   - front nearly upright, flare to the back and sides, crown sloping down to the back (D1-D3, P1 profile, A1 front)
#   - lacquered top band 18 mm with a stitch line, bottom band 20 mm under the cord (D5, D6; P1)
#   - one V strap on each side, apex low by the boss (D7; R1, S2); rear adjustment slit strip, rounded top (D8; S2)
#   - grenade: small ball, tall teardrop flame; grenadiers with two SHORT low side flames (D9; P1, P2, R1)
#   - pompom: upright fluffy wool oval 76 x 48 mm, outer ring + oval centre, two wire prongs (D10; R1, P1-P3)
#   - black leather loop from the top band down to the flame (D11; P1). The white loop and button of U1 have no source
#   - grenadier plume: 420 mm horsehair club in a lacquered socket (D12; R1 1811, P1)
#   - cords (etishket): TWO flat herringbone plaits, front low and back (D13; A1, P1, P2, S2); wearer's left: two short
#     tassels; wearer's right: the hanging cord with a plaited raquette and two tassels, cut at jaw height (D14: design
#     decision, a rigid head item reaching the chest would cut the shoulders)
#   - chin: 18 scales per side (R1 1817), large ringed boss ~44 mm (D15; P1); visor 62 mm, 22 deg, bound edge (D16)
#   kiver 1808 (19 Dec 1807: trimmed with black leather; V straps; RUW): nearly cylindrical; NO measured source (French
#       shako proportions, conferir no atlas); leather chin strap (many units until 1813-1814, RUW).
#   The plaits and tassels are modelled strand by strand: this is the HIGH-POLY design source (to be baked into a
#   simple band + normal map for the game mesh in Phase 4). Triangle counts are printed and are NOT game budgets.
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Phase 4 (2026-10-17): this file is also a MODULE. build_kiver_rus_jogo.py imports it, calls setup() and builds the
# same kivers with LOW = True (game mesh: same profile math, so the silhouette checked against the sources is identical
# by construction; bands, straps, loop, stitch line, visor binding, plait stitches, plume locks and scales become baked
# detail). Run as a script it builds the high-poly design model exactly as before.
HERE = os.path.dirname(os.path.abspath(__file__))
LOW = False                                             # game-mesh mode (set by the importer)
SAMPLES = "-"
UK_BLOCKOUT = os.path.abspath(os.path.join(HERE, "..", "models", "shakos", "hcl_shako_uk", "hcl_shako_uk_blockout.blend"))
WALL, CLEAR, DEPTH_RATIO, TILT = 0.004, 0.002, 1.13, math.radians(8)      # = shako_fit.py


def fit():
    if SAMPLES != "-" and os.path.exists(os.path.join(SAMPLES, "A3_headgear_example.p3d")):
        import shako_fit
        f = shako_fit.compute(SAMPLES)
        f["fonte"] = "Arma 3 Samples (shako_fit.compute)"
        return f
    with bpy.data.libraries.load(UK_BLOCKOUT, link=False) as (s, d):
        d.objects = [n for n in s.objects if n in ("belgic_batalhao_suadouro", "REF_cabeca_APROX_0")]
    sua = next(o for o in d.objects if o.name.startswith("belgic"))
    head = next(o for o in d.objects if o.name.startswith("REF"))
    M = sua.parent.matrix_basis.copy()                    # stored in the file (matrix_world is not evaluated here)
    tilt = math.atan2(-M[2][1], M[1][1])
    f = dict(head_cy=M[1][3], z_forehead=M[2][3] + 0.004, head_hw=head.scale.x + 0.006, head_hd=head.scale.y + 0.004,
             z_head_top=(head.scale.z + 0.004) * 2 + 0.57, tilt_lido=tilt,
             fonte=f"lido do blockout britanico aprovado ({os.path.basename(UK_BLOCKOUT)}); Samples ausente")
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for coll in (bpy.data.meshes, bpy.data.materials):   # nothing of the British file is kept (no BO_*.001 clashes)
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)
    return f


SPEC_BASE_W = 0.180
scene = F = base_hw = k = base_hd = ROOT = None


def setup(samples="-", reset=True):
    """Head fit and proportions (dossier section 3). reset: start from an empty file."""
    global SAMPLES, scene, F, base_hw, k, base_hd, ROOT
    SAMPLES = samples
    if reset:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    F = fit()
    print(f"ENCAIXE ({F['fonte']}): head_cy {F['head_cy']:+.4f} z_testa {F['z_forehead']:.4f} cabeca "
          f"{2 * F['head_hw']:.3f} x {2 * F['head_hd']:.3f}, topo {F['z_head_top']:.3f}" +
          (f", inclinacao lida {math.degrees(F['tilt_lido']):.2f} graus" if "tilt_lido" in F else ""))
    base_hw = max(SPEC_BASE_W / 2, F["head_hw"] + WALL + CLEAR)
    k = base_hw / (SPEC_BASE_W / 2)
    base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
    ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')


KIVER = {
    # H (front); growth at the top of the half-width / front / back; flare exponent (>1: concave, growth near the
    # top); crown slope to the back; dish of the crown; bands; body material; V strap (apex, front arm, back arm, deg)
    "1812": dict(H=0.178, side=0.032, front=0.006, back=0.070, expo=2.3, slope=6.0, dish=0.006, band_bot=0.020,
                 band_top=0.018, corpo="pano", strap=(95, 55, 135), chin="escamas"),
    "1808": dict(H=0.190, side=0.010, front=0.011, back=0.011, expo=1.0, slope=0.0, dish=0.002, band_bot=0.025,
                 band_top=0.016, corpo="feltro", strap=(90, 60, 120), chin="couro"),
}
STRAP_W = 0.022                                         # V straps 7/8" (R1 1817)
VISOR_LEN, VISOR_DROP = 0.062, math.radians(22)         # D16
N = 96
PRO = {}                                                # current kiver's profile (set by kiver())


def g(t):
    return max(0.0, min(1.0, t)) ** PRO["expo"]


def ring(z):
    """Half-width, centre y and half-depth of the wall at height z (the crown grows backward more than forward)."""
    t = g(z / PRO["H"])
    a = base_hw + PRO["side"] * t
    yf = -(base_hd + PRO["front"] * t)
    yb = base_hd + PRO["back"] * t
    return a, (yb + yf) / 2, (yb - yf) / 2


def P(theta, z, off=0.0, f=1.0):
    """Kiver-local point; theta = 0 is the FRONT (-Y), +90 deg the wearer's left (+X). f < 1: towards the axis.
    D3: the crown slopes down to the back, so every height is lowered in proportion to the distance from the front."""
    a, cy, d = ring(z)
    x = (a * f + off) * math.sin(theta)
    y = cy - (d * f + off) * math.cos(theta)
    dist_front = y - (cy - d)
    return Vector((x, y, z - (z / PRO["H"]) * PRO["tan_s"] * max(0.0, dist_front)))


def wall_n(theta, z):
    e = 1e-4
    up = P(theta, z + e) - P(theta, z - e)
    rnd = P(theta + e, z) - P(theta - e, z)
    n = up.cross(rnd).normalized()
    return n if n.dot(Vector((math.sin(theta), -math.cos(theta), 0.0))) > 0 else -n     # outward


def wall_up(theta, z):
    e = 1e-4
    return (P(theta, z + e) - P(theta, z - e)).normalized()


COL = dict(feltro=(0.015, 0.015, 0.016), pano=(0.013, 0.013, 0.015), couro=(0.03, 0.025, 0.02),
           verniz=(0.006, 0.006, 0.007), latao=(0.70, 0.50, 0.16), branco=(0.80, 0.80, 0.77), verde=(0.03, 0.20, 0.06),
           vermelho=(0.55, 0.03, 0.03), amarelo=(0.80, 0.62, 0.06), azul_celeste=(0.30, 0.52, 0.80),
           preto=(0.02, 0.02, 0.02), crina=(0.012, 0.012, 0.013), couro_marrom=(0.05, 0.028, 0.014),
           ferro=(0.25, 0.25, 0.26), forro=(0.30, 0.27, 0.22))
ROUGH = dict(latao=0.30, verniz=0.10, crina=0.80, pano=0.92, feltro=0.9, branco=0.85, ferro=0.45)
MATS, PARTS = {}, []


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = ROUGH.get(name, 0.7)
        b.inputs["Metallic"].default_value = 1.0 if name in ("latao", "ferro") else 0.0
        MATS[name] = m
    return MATS[name]


def finish(bm, name, colour, parent, keep_normals=False, smooth=False):
    # Phase 4 cleanup (mesh_review M2/M4): weld coincident vertices (collapsed rings at pointed ends) and drop the
    # degenerate faces they leave
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-7)
    if not keep_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat(colour))
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me); ob.parent = parent
    scene.collection.objects.link(ob); PARTS.append(ob)
    return ob


def grid(bm, rows, closed_u=True, closed_v=False):
    nr, nc = len(rows), len(rows[0])
    for j in range(nr - (0 if closed_v else 1)):
        for i in range(nc - (0 if closed_u else 1)):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nc], rows[(j + 1) % nr][(i + 1) % nc], rows[(j + 1) % nr][i]))


def cap_ring(bm, ring_, centre):
    c = bm.verts.new(centre)
    for i in range(len(ring_)):
        bm.faces.new((c, ring_[i], ring_[(i + 1) % len(ring_)]))


def lathe_band(name, z0, z1, t, colour, parent, bead=False):
    """Band on the wall; bead = a raised stitch line along its lower edge (top band, P1)."""
    bm = bmesh.new()
    zs = [z0 + (z1 - z0) * i / 4 for i in range(5)]
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, 0.0005)) for i in range(N)] for z in zs[::-1]] + \
           [[bm.verts.new(P(2 * math.pi * i / N, z, t)) for i in range(N)] for z in zs]
    grid(bm, rows, closed_v=True)
    ob = finish(bm, name, colour, parent, smooth=True)
    if bead:
        bm = bmesh.new()
        zb = z0 + 0.0035
        r = [[bm.verts.new(P(2 * math.pi * i / N, z, o)) for i in range(N)]
             for z, o in ((zb - 0.0009, t), (zb, t + 0.0007), (zb + 0.0009, t))]
        grid(bm, r)
        finish(bm, name + "_costura", colour, parent, smooth=True)
    return ob


def sweep(name, path, half_w, half_t, colour, parent, normals=None, round_=False, segs=8, radii=None, smooth=False):
    """Strip (or round tube) along a polyline; radii = per-point scale (tapered)."""
    bm = bmesh.new()
    rows = []
    for k_, p in enumerate(path):
        tng = (path[min(k_ + 1, len(path) - 1)] - path[max(k_ - 1, 0)]).normalized()
        nrm = normals[k_] if normals else (tng.orthogonal()).normalized()
        nrm = (nrm - tng * nrm.dot(tng)).normalized()
        side = tng.cross(nrm).normalized()
        s_ = radii[k_] if radii else 1.0
        if round_:
            rows.append([bm.verts.new(p + s_ * half_w * (math.cos(2 * math.pi * s / segs) * nrm * (half_t / half_w if half_t else 1.0)
                                                          + math.sin(2 * math.pi * s / segs) * side)) for s in range(segs)])
        else:
            rows.append([bm.verts.new(p + side * sx * half_w * s_ + nrm * sz * half_t) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    grid(bm, rows)
    cap_ring(bm, rows[0], path[0]); cap_ring(bm, rows[-1], path[-1])
    return finish(bm, name, colour, parent, smooth=smooth)


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


def lathe_obj(name, profile, centre, colour, parent, axis=Vector((0, 0, 1)), segs=20, smooth=True):
    """Solid of revolution: profile = [(along, radius)], around 'axis' through 'centre'."""
    bm = bmesh.new()
    u = axis.orthogonal().normalized(); v = axis.cross(u).normalized()
    rows = [[bm.verts.new(centre + axis * a + r * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)] for a, r in profile]
    grid(bm, rows)
    cap_ring(bm, rows[0], centre + axis * profile[0][0]); cap_ring(bm, rows[-1], centre + axis * profile[-1][0])
    return finish(bm, name, colour, parent, smooth=smooth)


def ellipsoid_bm(bm, centre, axes, radii, u=32, v=16, fluff=0.0, rnd=None):
    """Add an ellipsoid (optionally fluffy) to bm; returns its faces."""
    A, B, C = axes
    tmp = bmesh.new()
    bmesh.ops.create_uvsphere(tmp, u_segments=u, v_segments=v, radius=1.0)
    vm = {}
    for vv in tmp.verts:
        x, y, z = vv.co
        s = 1.0 + (fluff * (rnd.uniform(-1, 1) * 0.6 + math.sin(x * 23 + y * 17) * math.sin(z * 19) * 0.4) if fluff else 0.0)
        vm[vv] = bm.verts.new(centre + (A * x * radii[0] + B * y * radii[1] + C * z * radii[2]) * s)
    faces = [bm.faces.new([vm[x] for x in f.verts]) for f in tmp.faces]
    tmp.free()
    return faces


def ellipsoid(name, centre, axes, radii, colour, parent, u=32, v=16, fluff=0.0, seed=1):
    bm = bmesh.new()
    ellipsoid_bm(bm, centre, axes, radii, u, v, fluff, random.Random(seed))
    return finish(bm, name, colour, parent, smooth=True)


def length_of(path):
    L = [0.0]
    for a_, b_ in zip(path, path[1:]):
        L.append(L[-1] + (b_ - a_).length)
    return L


def resample(path, step):
    L = length_of(path)
    out, d = [], 0.0
    while d <= L[-1]:
        i = max(0, min(len(path) - 2, next((k_ for k_ in range(len(L) - 1) if L[k_ + 1] >= d), len(L) - 2)))
        f_ = (d - L[i]) / max(1e-9, L[i + 1] - L[i])
        out.append((path[i].lerp(path[i + 1], f_), d))
        d += step
    return out


def herringbone(name, path, width, colour, parent, normals_fn, step=0.0056, lean=math.radians(50), t=0.0030):
    """Flat plait in herringbone ("fishtail", P1): along the path, at every step, two elongated stitches (one on each
    half of the band), each a slim oval whose long axis leans `lean` from the band's axis toward the centre line, so
    the pairs read as a chain of V chevrons. A thin core band under them closes the gaps. High-poly bake source.
    LOW: a flat band of rectangular section (the stitches are baked into the normal map)."""
    if LOW:
        pts = [p for p, _ in resample(path, 0.012)] + [path[-1]]
        return sweep(name, pts, width * 0.5, t * 0.62, colour, parent, normals=[normals_fn(p) for p in pts], smooth=True)
    dense = resample(path, step)
    bm = bmesh.new()
    core = []
    for k_, (p, dd) in enumerate(dense):
        tng = (dense[min(k_ + 1, len(dense) - 1)][0] - dense[max(k_ - 1, 0)][0]).normalized()
        n = normals_fn(p); n = (n - tng * n.dot(tng)).normalized()
        side = tng.cross(n).normalized()
        core.append((p, tng, n, side))
        for sg in (1, -1):
            d_ = (tng * math.cos(lean) - side * sg * math.sin(lean)).normalized()     # stitch axis, leaning inward
            c = p + side * sg * width * 0.17 + n * t * 0.50
            ellipsoid_bm(bm, c, (d_, n.cross(d_).normalized(), n), (width * 0.34, step * 0.62, t * 0.62), u=10, v=5)
    rows = [[bm.verts.new(p + side * sx * width * 0.46 + n * sz * t * 0.35) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            for p, tng, n, side in core]
    grid(bm, rows)
    return finish(bm, name, colour, parent, smooth=True)


def twisted(name, path, r, colour, parent, pitch=0.010, segs=6):
    """Round cord of two strands twisted together (the hanging part). LOW: one round tube (twist baked)."""
    if LOW:
        pts = [p for p, _ in resample(path, 0.010)] + [path[-1]]
        return sweep(name, pts, r * 0.95, 0, colour, parent, round_=True, segs=5, smooth=True)
    dense = resample(path, 0.003)
    for strand in (0, 1):
        pts = []
        for k_, (p, dd) in enumerate(dense):
            tng = (dense[min(k_ + 1, len(dense) - 1)][0] - dense[max(k_ - 1, 0)][0]).normalized()
            nrm = tng.orthogonal().normalized(); bi = tng.cross(nrm)
            a = 2 * math.pi * dd / pitch + math.pi * strand
            pts.append(p + (nrm * math.cos(a) + bi * math.sin(a)) * r * 0.48)
        sweep(f"{name}_{strand}", pts, r * 0.56, 0, colour, parent, round_=True, segs=segs, smooth=True)


def fringe_tassel(name, top, colour, parent, r=0.010, length=0.040, strands=26, seed=3):
    """Tassel (kutas): a turned head with a neck and a ribbed collar, and a skirt of hanging strands.
    LOW: head and skirt as one turned solid (strands baked)."""
    if LOW:
        return lathe_obj(name, [(0.0, 0.0015), (-0.006, 0.0035), (-0.010, r * 0.9), (-0.016, r * 1.08), (-0.020, r * 0.92),
                                (-0.020 - length * 0.5, r * 1.05), (-0.020 - length, r * 1.25), (-0.021 - length, 0.002)],
                         top, colour, parent, axis=Vector((0, 0, 1)), segs=8)
    rnd = random.Random(seed)
    lathe_obj(name + "_cabeca", [(0.0, 0.0015), (-0.004, 0.0035), (-0.007, 0.0035), (-0.010, r * 0.9), (-0.014, r * 1.08),
                                 (-0.017, r * 1.08), (-0.020, r * 0.92)], top, colour, parent, axis=Vector((0, 0, 1)), segs=18)
    # dense core under the strands (a real tassel is solid; also gives the game-mesh bake something to hit)
    lathe_obj(name + "_nucleo", [(-0.019, r * 0.78), (-0.020 - length * 0.5, r * 0.84), (-0.020 - length * 0.92, r * 0.95),
                                 (-0.020 - length * 0.98, 0.002)], top, colour, parent, axis=Vector((0, 0, 1)), segs=12)
    bm = bmesh.new()
    for i in range(strands):
        a = 2 * math.pi * i / strands + rnd.uniform(-0.10, 0.10)
        o = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-math.sin(a), math.cos(a), 0))
        L_ = length * rnd.uniform(0.9, 1.06)
        rows = []
        for t_ in (0.0, 0.35, 0.7, 1.0):
            c = top + Vector((0, 0, -0.018 - L_ * t_)) + o * (r * 0.82 + 0.006 * t_ + rnd.uniform(-0.0005, 0.0005))
            hw = 0.0019 * (1 - 0.45 * t_)
            rows.append((bm.verts.new(c - sd * hw), bm.verts.new(c + sd * hw)))
        for (a0, b0), (a1, b1) in zip(rows, rows[1:]):     # outer layer facing OUT (bake rays come from outside)
            bm.faces.new((a1, b1, b0, a0))
        rows2 = [(bm.verts.new(a0.co - o * 0.0003), bm.verts.new(b0.co - o * 0.0003)) for a0, b0 in rows]
        for (a0, b0), (a1, b1) in zip(rows2, rows2[1:]):  # inner layer facing in
            bm.faces.new((a0, b0, b1, a1))
    return finish(bm, name + "_franja", colour, parent, keep_normals=True)


def raquette(name, centre, out_n, colour, parent, L=0.075, W=0.032, T=0.007):
    """Flat plaited raquette (leaf/lozenge, A1, P1): a flattened pointed oval, with herringbone lobes along its axis on
    both faces."""
    up = Vector((0, 0, 1)); up = (up - out_n * up.dot(out_n)).normalized()
    side = up.cross(out_n).normalized()
    bm = bmesh.new()
    rows = []
    nr, ns = (9, 8) if LOW else (15, 16)
    for j in range(nr):
        t = j / (nr - 1)
        hw = max(0.0012, W / 2 * math.sin(math.pi * t) ** 0.8)   # no collapsed ring at the tips (manifold, normals)
        z = (t - 0.5) * L
        rows.append([bm.verts.new(centre + up * z + side * hw * math.cos(2 * math.pi * s / ns) + out_n * T / 2 * math.sin(2 * math.pi * s / ns))
                     for s in range(ns)])
    grid(bm, rows)
    cap_ring(bm, rows[0], centre - up * L / 2); cap_ring(bm, rows[-1], centre + up * L / 2)
    if LOW:                                             # plait baked
        return finish(bm, name, colour, parent, smooth=True)
    for face in (1, -1):
        for j in range(1, 11):
            t = j / 11
            hw = W / 2 * math.sin(math.pi * t) ** 0.8
            z = (t - 0.5) * L
            for sg in (1, -1):
                d_ = (up * math.cos(math.radians(40)) * -1 + side * sg * math.sin(math.radians(40))).normalized()
                c = centre + up * z + side * sg * hw * 0.45 + out_n * face * T * 0.48
                ellipsoid_bm(bm, c, (d_, out_n.cross(d_).normalized(), out_n), (L / 22, hw * 0.42, T * 0.18), u=8, v=4)
    return finish(bm, name, colour, parent, smooth=True)


def chinscales(name, path, normals, parent, n_scales=18):
    """Black leather strap with 18 overlapping domed brass scales per side (R1 1817), 33 -> 20 mm wide (D15).
    LOW: one brass strip over the scales' envelope, 33 -> 20 mm, thick enough for the relief (scales baked)."""
    if LOW:
        pts = [p for p, _ in resample(path, 0.012)] + [path[-1]]
        nrm = [normals[min(len(normals) - 1, int(i * (len(normals) - 1) / max(1, len(pts) - 1)))] for i in range(len(pts))]
        radii = [1.0 - 0.39 * i / max(1, len(pts) - 1) for i in range(len(pts))]
        return sweep(name + "_escamas", pts, 0.0165, 0.0016, "latao", parent, normals=nrm, radii=radii)
    sweep(name + "_couro", path, 0.0115, 0.0007, "couro", parent, normals=normals)
    L = length_of(path)
    bm = bmesh.new()
    step = (L[-1] - 0.010) / (n_scales - 1)
    for k_ in range(n_scales):
        d0 = 0.004 + k_ * step
        i = next((j for j in range(len(L) - 1) if L[j + 1] >= d0), len(L) - 2)
        t_ = (d0 - L[i]) / max(1e-9, L[i + 1] - L[i])
        p = path[i].lerp(path[i + 1], t_); tg = (path[i + 1] - path[i]).normalized()
        n = normals[i].lerp(normals[i + 1], t_).normalized(); n = (n - tg * n.dot(tg)).normalized()
        side = tg.cross(n).normalized()
        w = 0.0165 - 0.0065 * k_ / (n_scales - 1); ln = step * 1.7; lift = 0.0010 + 0.00028 * (n_scales - 1 - k_)
        outline = [(-w, 0.0), (w, 0.0), (w, ln * 0.45)] + [(w * math.cos(math.pi * j / 8), ln * 0.45 + ln * 0.55 * math.sin(math.pi * j / 8)) for j in range(1, 8)] + [(-w, ln * 0.45)]
        top_, bot_ = [], []
        for sx, sl in outline:
            q = p + side * sx + tg * sl + n * (lift + 0.0014 * (1 - (sx / w) ** 2))
            top_.append(bm.verts.new(q)); bot_.append(bm.verts.new(q - n * 0.0006))
        m_ = len(outline)
        ct = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0012)); cb = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0003))
        for j in range(m_):
            jj = (j + 1) % m_
            bm.faces.new((ct, top_[j], top_[jj])); bm.faces.new((cb, bot_[jj], bot_[j]))
            bm.faces.new((top_[jj], top_[j], bot_[j], bot_[jj]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(bm, name + "_escamas", "latao", parent, keep_normals=True)


def flame(name, base, d_start, side, curl, length, r0, parent, n_wall, colour="latao"):
    """Brass flame: a tapered teardrop tube along a curve starting along d_start and curling toward `side`, flattened
    against the wall (n_wall), swelling then ending in a point."""
    pts, radii = [], []
    ns = 8 if LOW else 16
    for s in range(ns):
        t = s / (ns - 1)
        ang = curl * t ** 1.5
        d = (d_start * math.cos(ang) + side * math.sin(ang)).normalized()
        pts.append(base.copy() if not pts else pts[-1] + d * length / (ns - 1))
        scallop = 1.0 + 0.16 * math.sin(t * math.pi * 5.0) * (1 - t)       # flame tongues along the edge (P1)
        radii.append(max(0.04, math.sin(math.pi * min(1.0, 0.18 + t * 0.95)) * (1 - t) ** 0.35 * scallop))
    return sweep(name, pts, r0, r0 * 0.5, colour, parent, normals=[n_wall] * len(pts), round_=True, segs=6 if LOW else 12, radii=radii, smooth=True)


def grenade(tag, flames, parent, zc):
    """D9 (P1, P2, R1): small brass ball with a collar; a tall teardrop flame; grenadiers add two SHORT side flames,
    low, leaning out ~55 deg from the vertical and curling outward."""
    R_B = 0.011
    n = wall_n(0.0, zc); up = wall_up(0.0, zc)
    side = up.cross(n).normalized()
    c = P(0.0, zc, R_B * 0.42)
    ellipsoid(f"{tag}_granada", c, (side, up, n), (R_B, R_B, R_B * 0.68), "latao", parent, u=10 if LOW else 32, v=6 if LOW else 16)
    collar = c + up * R_B * 0.90
    lathe_obj(f"{tag}_granada_gargalo", [(0.0, 0.0052), (0.0025, 0.0058), (0.0045, 0.0046)], collar - up * 0.0015,
              "latao", parent, axis=up, segs=(8 if LOW else 16))
    tip = collar + up * 0.002                             # flame starts 1 mm inside the collar (no shared vertex)
    flame(f"{tag}_chama_0", tip, up, side, math.radians(-12), 0.046, 0.0075, parent, n)
    if flames == 3:
        for j, sg in enumerate((1, -1)):
            d0 = (up * math.cos(math.radians(55)) + side * sg * math.sin(math.radians(55))).normalized()
            flame(f"{tag}_chama_{j + 1}", tip - up * 0.0025 + side * sg * 0.0035, d0, side * sg, math.radians(22), 0.026,
                  0.0056, parent, n)
    return tip + up * 0.046


def plume(tag, parent, base, up_w, back_w, seed):
    """D12: full black horsehair club (420 mm, 44 -> 146 mm), rounded top bending slightly back, ragged hair surface
    (longitudinal locks + random tufts) in a lacquered socket."""
    rnd = random.Random(seed)
    L, segs = 0.420, (12 if LOW else 56)
    lathe_obj(f"{tag}_sultao_suporte", [(-0.004, 0.0105), (0.0, 0.0115), (0.024, 0.0125), (0.026, 0.0110)], base, "verniz",
              parent, axis=up_w, segs=(8 if LOW else 24))
    base = base + up_w * 0.020
    prof = [(0.0, 0.010), (0.015, 0.021), (0.05, 0.027), (0.12, 0.038), (0.20, 0.050), (0.28, 0.062), (0.34, 0.071)] + \
           [(0.36 + 0.06 * s / 8, max(0.004, 0.073 * math.sqrt(max(0.0, 1 - (s / 8) ** 2)))) for s in range(1, 9)]   # domed top
    u = up_w.orthogonal().normalized(); v = up_w.cross(u).normalized()
    locks = [rnd.uniform(0, 6.3) for _ in range(5)]
    bm = bmesh.new()
    rows = []
    for a, r in prof:
        t = a / L
        c = base + up_w * a + back_w * 0.040 * t ** 2.2
        row = []
        for s in range(segs):
            ang = 2 * math.pi * s / segs
            lock = sum(math.sin((7 + 4 * j) * ang + locks[j] + 3 * t * j) for j in range(5)) / 5
            fluff = 1.0 if LOW else 1.0 + 0.12 * lock + rnd.uniform(-0.07, 0.07)
            row.append(bm.verts.new(c + r * fluff * (math.cos(ang) * u + math.sin(ang) * v)))
        rows.append(row)
    grid(bm, rows)
    cap_ring(bm, rows[0], base); cap_ring(bm, rows[-1], base + up_w * L + back_w * 0.040)
    ob = finish(bm, f"{tag}_sultao", "crina", parent, smooth=True)
    if LOW:                                             # hair locks baked
        return ob
    # loose horsehair locks breaking the silhouette: thin tapered ribbons rising from the surface, upward and outward
    bm = bmesh.new()
    for _ in range(320):
        t = rnd.uniform(0.22, 0.86)       # none on the dome (spikes) nor low down, where they would cross the pompom
        a = t * L
        r = next(r1 + (r2 - r1) * (a - a1) / max(1e-6, a2 - a1) for (a1, r1), (a2, r2) in zip(prof, prof[1:]) if a1 <= a <= a2)
        ang = rnd.uniform(0, 2 * math.pi)
        radial = math.cos(ang) * u + math.sin(ang) * v
        c = base + up_w * a + back_w * 0.040 * t ** 2.2
        p0 = c + radial * r * 0.96
        d = (up_w * 0.96 + radial * 0.18 + (u * rnd.uniform(-.12, .12) + v * rnd.uniform(-.12, .12))).normalized()
        ln = rnd.uniform(0.040, 0.075) * (0.55 if t > 0.88 else 1.0)
        sd = radial.cross(d).normalized()
        pts = [p0 + d * ln * s + radial * 0.006 * s * s for s in (0.0, 0.35, 0.7, 1.0)]   # flowing up, lifting at the tip
        wid = (0.0034, 0.0028, 0.0016, 0.0002)
        vs = [(bm.verts.new(p - sd * w_), bm.verts.new(p + sd * w_)) for p, w_ in zip(pts, wid)]
        for (a0, b0), (a1, b1) in zip(vs, vs[1:]):
            bm.faces.new((a1, b1, b0, a0))   # one-sided card facing OUT (two-sided in the renderer; bake hits its front)
    finish(bm, f"{tag}_sultao_mechas", "crina", parent, keep_normals=True)
    return ob


def pompom(tag, parent, centre, n_top, up_w, outer, centre_col, seed):
    """D10: upright oval of fulled wool 76 x 48 x 22 mm (R1 1817: 3"), outer ring + oval centre (P3), on two wire
    prongs down into the crown edge."""
    side = up_w.cross(n_top).normalized()
    if LOW:                                             # ring, centre and fuzz baked; prongs hidden
        return ellipsoid(f"{tag}_pompom", centre, (side, up_w, n_top), (0.024, 0.038, 0.011), outer, parent, u=12, v=8)
    ellipsoid(f"{tag}_pompom", centre, (side, up_w, n_top), (0.024, 0.038, 0.011), outer, parent, u=40, v=20,
              fluff=0.05, seed=seed)
    if centre_col:
        ellipsoid(f"{tag}_pompom_centro", centre + n_top * 0.0098, (side, up_w, n_top), (0.0125, 0.020, 0.0028),
                  centre_col, parent, u=28, v=12, fluff=0.04, seed=seed + 1)
    for sg in (1, -1):
        top = centre - up_w * 0.034 + side * sg * 0.006
        sweep(f"{tag}_pompom_haste_{'E' if sg > 0 else 'D'}", [top, top - up_w * 0.016], 0.0007, 0, "ferro", parent,
              round_=True, segs=6)


def kiver(tag, model, flames, pompom_col, grenadier, x_off):
    """pompom_col = (outer colour, centre colour or None); grenadier = plume + 3-flame grenade."""
    global N
    N = 32 if LOW else 96                               # LOW: game mesh
    spec = KIVER[model]
    H = spec["H"] * k
    PRO.update(H=H, expo=spec["expo"], side=spec["side"] * k, front=spec["front"] * k, back=spec["back"] * k,
               tan_s=math.tan(math.radians(spec["slope"])))
    root = bpy.data.objects.new(f"RUS_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    # body: cloth over leather (1812) or felt (1808), with wall thickness; 20 rows for the concave flare
    bm = bmesh.new()
    nz = 10 if LOW else 20
    zs = [H * i / nz for i in range(nz + 1)]
    outer = [[bm.verts.new(P(2 * math.pi * i / N, z)) for i in range(N)] for z in zs]
    # inner wall: rows close enough that a straight chord stays inside the concave outer wall (mesh_review, Phase 4)
    inner = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL)) for i in range(N)] for z in zs[::2]]
    grid(bm, outer); grid(bm, [inner[0], outer[0]]); grid(bm, inner[::-1])
    grid(bm, [outer[-1], inner[-1]])                       # top rim: closed shell, so the normals point outward
    body_ob = finish(bm, f"{tag}_corpo", spec["corpo"], root, smooth=True)
    # wall normals for whatever lies on the wall (cords): from the real surface (the crown slope shears the heights,
    # so wall_n at the sheared z would be wrong at the back; Phase 4 mesh review)
    body_bvh = BVHTree.FromPolygons([v.co.copy() for v in body_ob.data.vertices], [list(p.vertices) for p in body_ob.data.polygons])
    # crown: lacquered leather, dished, sewn to the body under a rolled edge
    bm = bmesh.new()
    rings = [[bm.verts.new(P(2 * math.pi * i / N, H, 0.0008)) for i in range(N)],
             [bm.verts.new(P(2 * math.pi * i / N, H, 0.0004) + Vector((0, 0, 0.0018))) for i in range(N)],
             [bm.verts.new(P(2 * math.pi * i / N, H, -0.0022) + Vector((0, 0, 0.0016))) for i in range(N)]]
    for f_ in ((0.7, 0.3) if LOW else (0.85, 0.6, 0.35, 0.12)):
        rings.append([bm.verts.new(P(2 * math.pi * i / N, H, 0.0, f_) - Vector((0, 0, spec["dish"] * (1 - f_ ** 2))))
                      for i in range(N)])
    grid(bm, rings)
    a_, cy_, d_ = ring(H)
    cap_ring(bm, rings[-1], P(0.0, H, 0.0, 0.0) - Vector((0, 0, spec["dish"])))
    finish(bm, f"{tag}_topo", "verniz", root, smooth=True)
    # inside: leather sweatband and linen lining (seen from below)
    bm = bmesh.new()
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.028, 0.055)]
    grid(bm, rows[::-1]); finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    bm = bmesh.new()
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0012)) for i in range(N)] for z in [0.053] + [z_ for z_ in zs[::2] if 0.06 < z_ < H - 0.01] + [H - 0.006]]   # follows the concave wall
    grid(bm, rows[::-1]); finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    # bands: lacquered, the top one with its stitch line (D5, D6)
    band_mat = "verniz" if model == "1812" else "couro"
    if not LOW:                                         # LOW: bands, straps and slit strip are baked
        lathe_band(f"{tag}_faixa_baixo", 0.0, spec["band_bot"], 0.0018, band_mat, root)
        lathe_band(f"{tag}_faixa_cima", H - spec["band_top"], H, 0.0018, band_mat, root, bead=True)
        # V strap on each side: apex low near the boss, arms up to the top band at the front and at the back (D7)
        apex, a_front, a_back = (math.radians(x) for x in spec["strap"])
        for sgn in (1, -1):
            for nm_, a1 in (("f", a_front), ("t", a_back)):
                pts, nrm = [], []
                for s in range(17):
                    t = s / 16
                    a = sgn * (apex + (a1 - apex) * t)
                    z = spec["band_bot"] + 0.004 + (H - spec["band_top"] - spec["band_bot"] - 0.004) * t
                    pts.append(P(a, z, 0.0021)); nrm.append(wall_n(a, z))
                sweep(f"{tag}_tira_{'E' if sgn > 0 else 'D'}{nm_}", pts, STRAP_W / 2, 0.0007, band_mat, root, normals=nrm)
        # rear adjustment slit, bound with a leather strip with a rounded top (D8, S2)
        pts = [P(math.pi, 0.0 + 0.072 * i / 12, 0.0021) for i in range(13)]
        radii = [1.0] * 9 + [0.95, 0.82, 0.58, 0.22]
        sweep(f"{tag}_fenda_tira", pts, 0.015, 0.0007, band_mat, root, normals=[wall_n(math.pi, p.z) for p in pts], radii=radii)
    # visor: lacquered, 62 mm, 22 deg, with a bound (rolled) edge (D16)
    bm = bmesh.new()
    na = 20 if LOW else 56
    arc = [math.radians(-84 + 168 * i / na) for i in range(na + 1)]

    def vrow(off_len, dz):
        out = []
        for a in arc:
            n = wall_n(a, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a) / math.radians(84)) ** 3
            out.append(P(a, 0.004, 0.002) + n * off_len * w * math.cos(VISOR_DROP) + Vector((0, 0, -off_len * w * math.sin(VISOR_DROP) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in vrow(0.0, 0.0)], [bm.verts.new(p) for p in vrow(VISOR_LEN * 0.5, 0.0012)],
            [bm.verts.new(p) for p in vrow(VISOR_LEN, 0.0)], [bm.verts.new(p) for p in vrow(VISOR_LEN, -0.0028)],
            [bm.verts.new(p) for p in vrow(VISOR_LEN * 0.5, -0.0016)], [bm.verts.new(p) for p in vrow(0.0, -0.0028)]]
    grid(bm, rows, closed_u=False, closed_v=True)
    edge = [p.lerp(q, 0.5) for p, q in zip(vrow(VISOR_LEN, 0.0), vrow(VISOR_LEN, -0.0028))]
    finish(bm, f"{tag}_pala", "verniz", root, smooth=True)
    if not LOW:                                         # LOW: binding baked
        sweep(f"{tag}_pala_debrum", edge[2:-2], 0.0021, 0, "verniz", root, round_=True, segs=8, smooth=True)
    # grenade above the front plait (D9)
    zg = H * 0.45
    flame_top = grenade(tag, flames, root, zg)
    # pompom on the top edge at the front, the loop strap down to the flame (D10, D11)
    front_top = P(0, H, -0.008)
    n_top = wall_n(0.0, H * 0.95); n_top.z = 0; n_top.normalize()
    up_w = (Matrix.Rotation(TILT, 3, 'X') @ Vector((0, 0, 1))).normalized()   # world vertical in kiver space
    pompom(tag, root, front_top + up_w * 0.042 + n_top * 0.010, n_top, up_w, pompom_col[0], pompom_col[1],
           seed=sum(map(ord, tag)))
    lp = [P(0, H - spec["band_top"] * 0.6 - (H - spec["band_top"] * 0.6 - (flame_top.z - 0.004)) * i / 10, 0.0026) for i in range(11)]
    if not LOW:                                         # LOW: loop baked
        sweep(f"{tag}_presilha", lp, 0.006, 0.0007, "verniz", root, normals=[wall_n(0, p.z) for p in lp])
    if grenadier:
        plume(tag, root, front_top + up_w * 0.006 - n_top * 0.022, up_w, -n_top, seed=sum(map(ord, tag)))
    # chin: brass scales on ringed bosses (1812) or a plain leather strap (1808)
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, F["head_cy"] - F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        th_r = sgn * math.radians(95)
        ro = P(th_r, 0.026, 0.0030)
        nr = wall_n(th_r, 0.026)
        lathe_obj(f"{tag}_roseta_{'E' if sgn > 0 else 'D'}",
                  [(0, 0.0005), (0, 0.022), (0.0012, 0.0218), (0.0018, 0.019), (0.0030, 0.0185), (0.0036, 0.0145),
                   (0.0052, 0.0130), (0.0060, 0.0085), (0.0078, 0.0060), (0.0085, 0.0005)], ro, "latao", root, axis=nr, segs=(12 if LOW else 32))
        ro_w = root.matrix_world @ ro
        z_mid = (ro_w.z + chin_w.z) / 2
        hz = (F["z_head_top"] - 0.57) / 2 - 0.004; zc_h = (F["z_head_top"] + 0.57) / 2
        half_w = (F["head_hw"] - 0.006) * math.sqrt(max(0.0, 1 - ((z_mid - zc_h) / hz) ** 2))
        mid = inv @ Vector((x_off + sgn * (half_w + 0.010), F["head_cy"] - 0.012, z_mid))
        path = catmull([ro + nr * 0.004, mid, Vector((sgn * 0.035, chin.y, chin.z + 0.006)), Vector((sgn * 0.0015, chin.y, chin.z))], 8)   # the two straps end 3 mm apart
        nrm = [Vector((p.x, p.y, 0)).normalized() for p in path]
        if spec["chin"] == "escamas":
            chinscales(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, nrm, root)
        else:
            sweep(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, 0.008, 0.0008, "couro", root, normals=nrm)

    # cords (etishket, D13): two herringbone plaits, front (low) and back, meeting at the sides
    def n_at(p):
        loc, n, _, _ = body_bvh.find_nearest(p)
        n = n.normalized()
        return n if n.dot(p - loc) >= 0 else -n               # outward: toward the point on the cord
    front_ctrl = [(-100, 0.62), (-62, 0.38), (-30, 0.29), (0, 0.27), (30, 0.29), (62, 0.38), (100, 0.55)]
    back_ctrl = [(101, 0.55), (140, 0.64), (180, 0.68), (220, 0.66), (259, 0.62)]   # ends 1 deg past the front plait's
    for nm_, ctrl in (("frente", front_ctrl), ("tras", back_ctrl)):
        # control points every 10 deg (angle and height interpolated) before projecting on the wall: a spline
        # between points 40 deg apart cut inside the wall (chord sagitta > the 5.8 mm offset; Phase 4 mesh review)
        dense = []
        for (a0, z0), (a1, z1) in zip(ctrl, ctrl[1:]):
            n_ = max(1, int(abs(a1 - a0) / 10))
            dense += [(a0 + (a1 - a0) * s / n_, z0 + (z1 - z0) * s / n_) for s in range(n_)]
        dense.append(ctrl[-1])
        herringbone(f"{tag}_cordao_{nm_}", catmull([P(math.radians(a), H * z, 0.0058) for a, z in dense], 4), 0.022,
                    "branco", root, n_at)
    # wearer's left (+X): two short tassels at the end of the front plait (A1, P2)
    jl = P(math.radians(100), H * 0.55, 0.009)
    nl = wall_n(math.radians(100), H * 0.55)
    for j, dy in enumerate((-0.0105, 0.0105)):            # skirts (r 8 mm x 1.25) side by side, not through each other
        top = jl + nl * 0.004 + Vector((0, dy, -0.012))
        twisted(f"{tag}_borla_E_cordao_{j}", [jl + Vector((0, dy * 0.3, 0)), top + Vector((0, 0, 0.0015))], 0.0022, "branco", root)   # distinct starts (no shared vertices)
        fringe_tassel(f"{tag}_borla_E_{j}", top, "branco", root, r=0.008, length=0.032, seed=11 + j)
    # wearer's right (-X): the hanging cord, raquette and two tassels, cut at jaw height (D14)
    jr = P(math.radians(-100), H * 0.62, 0.009)
    nr_ = wall_n(math.radians(-100), H * 0.40)
    nr_.z = 0; nr_.normalize()
    rq_c = P(math.radians(-122), H * 0.10, 0.020) + Vector((0, 0, -0.035))   # behind the boss, bottom at the jaw (P1)
    twisted(f"{tag}_pendente", catmull([jr, jr + nr_ * 0.012 + Vector((0, 0.002, -0.030)), rq_c + Vector((0, 0, 0.040))], 8),
            0.0030, "branco", root)
    raquette(f"{tag}_raquete", rq_c, nr_, "branco", root)
    for j, dy in enumerate((-0.0128, 0.0128)):            # skirts (r 10 mm x 1.25) side by side
        top = rq_c + Vector((0, dy, -0.040))
        twisted(f"{tag}_pendente_fim_{j}", [rq_c + Vector((0, dy * 0.3, -0.034)), top + Vector((0, 0, 0.0015))], 0.0022, "branco", root)
        fringe_tassel(f"{tag}_kutas_{j}", top, "branco", root, seed=7 + j)
    return root, H


VARIANTS = [  # tag, model, flames, pompom (1st battalion, 22 Feb 1811), grenadier
    ("1812_mosqueteiro", "1812", 1, ("branco", "verde"), False),
    ("1812_granadeiro", "1812", 3, ("vermelho", None), True),
    ("1808_mosqueteiro", "1808", 1, ("branco", "verde"), False),
    ("1808_granadeiro", "1808", 3, ("vermelho", None), True),
]
SPACING = 0.45


def main():
    """Script entry: build the high-poly design model of the four kivers, the approximate heads and the renders."""
    args = sys.argv[sys.argv.index("--") + 1:]
    samples, OUT_BLEND, RENDER_DIR = args[:3]
    OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    setup(samples)
    built = [kiver(t, *rest, i * SPACING) for i, (t, *rest) in enumerate(VARIANTS)]
    roots = [b[0] for b in built]
    bpy.context.view_layer.update()
    print(f"ENCAIXE k={k:.4f} base {2 * base_hw * 1000:.0f} x {2 * base_hd * 1000:.0f} mm")
    for (t, m, *_), (r, H) in zip(VARIANTS, built):
        spec = KIVER[m]
        PRO.update(H=H, expo=spec["expo"], side=spec["side"] * k, front=spec["front"] * k, back=spec["back"] * k,
                   tan_s=math.tan(math.radians(spec["slope"])))
        a_, cy_, d_ = ring(H)
        h_back = P(math.pi, H).z
        obs = [o for o in PARTS if o.parent is r]
        groups = {}
        for o in obs:
            key = ("cordoes" if any(s in o.name for s in ("cordao", "borla", "kutas", "raquete", "pendente")) else
                   "sultao" if "sultao" in o.name else "jugular" if ("jugular" in o.name or "roseta" in o.name) else "corpo_e_resto")
            groups[key] = groups.get(key, 0) + sum(len(p.vertices) - 2 for p in o.data.polygons)
        tris = sum(groups.values())
        print(f"KIVER {t:18s} altura frente {H * 1000:.0f} mm, tras {h_back * 1000:.0f} mm; topo {2 * a_ * 1000:.0f} x {2 * d_ * 1000:.0f} mm  "
              f"pecas {len(obs):3d}  triangulos {tris:6d} " + " ".join(f"{k_}={v}" for k_, v in sorted(groups.items())))

    # ---------------------------------------------------------------- approximate head under every kiver (render only)
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
    hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
    for p in hme.polygons:
        p.use_smooth = True
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
    for (t, *_), r, h in zip(VARIANTS, roots, heads):
        obs = [o for o in PARTS if o.parent is r and o.name.endswith(("_suadouro", "_corpo", "_forro"))]
        inv_h = h.matrix_world.inverted()
        worst = min((inv_h @ (o.matrix_world @ v.co)).length for o in obs for v in o.data.vertices)
        print(f"FOLGA {t:18s} menor distancia normalizada parede/cabeca {worst:.3f} (> 1 = fora da cabeca aproximada)")

    # ---------------------------------------------------------------- renders
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
    for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
        lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
        lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 48
    scene.view_settings.view_transform = "Standard"
    os.makedirs(RENDER_DIR, exist_ok=True)
    zc = (ROOT @ Vector((0, 0, 0.09))).z + 0.08


    def shot(name, loc, target, ortho=None, lens=60, res=(1800, 700)):
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_kiver_rus_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)


    def solo(i):
        for j, r in enumerate(roots):
            for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
                o.hide_render = j != i


    mid_x = SPACING * (len(VARIANTS) - 1) / 2
    shot("fila_frente", (mid_x, -3.0, zc + 0.05), (mid_x, 0, zc + 0.05), ortho=SPACING * len(VARIANTS) + 0.10, res=(2000, 900))
    shot("fila_tres_quartos", (mid_x + 1.3, -2.8, zc + 0.65), (mid_x, 0, zc), lens=45, res=(2000, 900))
    for i, (t, *_) in enumerate(VARIANTS):
        solo(i)
        # the wearer's right side, like the profile of P1 (Рис. 1323)
        shot(f"{t}_lado", (i * SPACING - 2.0, F["head_cy"], zc + 0.05), (i * SPACING, F["head_cy"], zc + 0.05), ortho=0.80, res=(900, 1100))
    # close-ups of the 1812 caps: front and right profile like P1, a 3/4 view and the back
    solo(1)
    shot("1812_granadeiro_frente_P1", (SPACING, -2.0, zc + 0.15), (SPACING, F["head_cy"], zc + 0.15), ortho=0.86, res=(1000, 1100))
    shot("1812_granadeiro_perfil_P1", (SPACING - 2.0, F["head_cy"], zc + 0.15), (SPACING, F["head_cy"], zc + 0.15), ortho=0.86, res=(1000, 1100))
    solo(0)
    shot("1812_mosqueteiro_detalhe", (0.9, -1.2, zc + 0.35), (0.0, F["head_cy"], zc - 0.02), lens=85, res=(1200, 1200))
    shot("1812_mosqueteiro_costas", (0.5, 1.6, zc + 0.25), (0.0, F["head_cy"], zc), lens=70, res=(1100, 1100))
    shot("1812_mosqueteiro_cordao_macro", (0.28, -0.52, zc - 0.03), (0.02, F["head_cy"] - 0.08, zc - 0.05), lens=110, res=(1200, 900))
    solo(-1)
    for o in PARTS + heads:
        o.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("saved", OUT_BLEND)


if __name__ == "__main__":
    main()
