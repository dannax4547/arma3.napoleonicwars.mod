# Phase 4 (production mesh) + Phase 6 UV of the Prussian 1813 equipment, worn over the uniform production mesh.
#   HCL_V_Pruss1813_Correame_LOD0 (Arma "vest") and HCL_B_Pruss1813_Tornister_LOD0 (Arma "backpack")
# Same layout, guides and fit rules as the Phase 3 blockout (blockout_equipamento_pruss.py), with production detail:
#   straps with rounded top edges; waist belt with brass frame buckle (centre bar, tongue), belt tip and keeper;
#   crossbelt legs ending under the cartridge-box flap; cartridge box with rounded body, bent flap with rounded corners,
#   plain brass plate (decision E2 recommendation), closing tab and stud; bayonet frog (belt loop, pocket, back panel);
#   scabbard with brass locket, chape and ball finial; socket bayonet: socket with reinforcing ring, neck, blade root;
#   knapsack with rounded, slightly bulging body, bent calfskin flap, two closing straps with buckles and tabs; greatcoat
#   roll with longitudinal folds, the outer layer's edge, recessed ends and pinches under its two straps (buckles on top);
#   shoulder straps with a chest buckle, tip and keeper.
# Every face carries hcl_part (names in ob["hcl_partes"]) and hcl_lado (0 outer face, 1 edge, 2 underside); UV "UVMap" is
# the texture atlas (active, exported), UV "local" holds metres along/across each strap, tube and flap for the texture
# painter; ob["hcl_frames"] (JSON) holds the frames of boxes, flaps and the roll. Checks: triangles per item and per part,
# vertices under the uniform surface, UV bounds and texel density.
#   blender -b --factory-startup --python build_equipamento_producao.py -- <uniform LOD0 .blend> <out .blend> <out img dir> [norender]
#           [nacao=fr]
# nacao=fr (2026-10-12): French line infantry 1812 over the French coat (build_uniforme_fr.py): no waist belt; the
#   cartridge-box belt as the Prussian crossbelt (left shoulder -> box on the right hip); a second crossbelt
#   ("boldrie", baudrier) from the right shoulder to the bayonet frog on the left hip, crossing UNDER the cartridge
#   belt on the chest and the back (order assumed); the frog hangs from the baudrier's two ends; knapsack (havresac)
#   of hair-on calfskin with the rolled greatcoat on top (same construction, slightly larger). Objects
#   HCL_V_Fr1812_Correame_LOD0 / HCL_B_Fr1812_Havresac_LOD0.
import bpy, bmesh, sys, os, math, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

_a = sys.argv[sys.argv.index("--") + 1:]
UNIFORM_BLEND, OUT_BLEND, OUT_IMG = _a[:3]
RENDER = "norender" not in _a[3:]
FR = "nacao=fr" in _a[3:]
UNI_NAME = "HCL_U_Fr1812_01_LOD0" if FR else "HCL_U_Pruss1813_01_LOD0"
os.makedirs(OUT_IMG, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
GROUND = -1.0069                                     # official body: P3D origin 1.007 m above the ground
UP = Vector((0, 0, 1))


def Z(h):
    return GROUND + h


# ---------------------------------------------------------------- uniform (reference + projection surfaces)
with bpy.data.libraries.load(UNIFORM_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in (UNI_NAME,)]
REFC = bpy.data.collections.new("REF_Uniforme")
bpy.context.scene.collection.children.link(REFC)
for o in dst.objects:
    REFC.objects.link(o)
uni = bpy.data.objects[UNI_NAME]
uparts = uni["hcl_partes"].split(",")
ubm = bmesh.new()
ubm.from_mesh(uni.data)
ubm.transform(uni.matrix_world)
UPL = ubm.faces.layers.int.get("hcl_part")
ucoords = [v.co.copy() for v in ubm.verts]


def bvh_of(names):
    ids = {uparts.index(n) for n in names}
    return BVHTree.FromPolygons(ucoords, [[v.index for v in f.verts] for f in ubm.faces if f[UPL] in ids])


TORSO_OUT = bvh_of(["casaco_corpo", "gola", "aba_E", "aba_D", "platina_E", "platina_D", "calca_assento"]
                   + [n for n in ("lapela_E", "lapela_D") if n in uparts])              # French lapels
ALL_U = BVHTree.FromBMesh(ubm)
LEGS_OUT = bvh_of(["aba_E", "aba_D", "calca_assento", "calca_perna_E", "calca_perna_D"])

S = dict(cross_w=0.060, waist_w=0.050, belt_t=0.0035, belt_gap=0.0045, strap_w=0.045, strap_t=0.003, strap_gap=0.014,
         box_w=0.20, box_h=0.13, box_d=0.065, box_r=0.008, flap_t=0.003, flap_drop=0.075,
         scab_len=0.45, socket_len=0.075, socket_r=0.0113, socket_off=0.030,
         pack_w=0.34, pack_h=0.30, pack_d=0.12, pack_r=0.018, pack_bulge=0.008, pflap_t=0.006, pflap_drop=0.20,
         roll_r=0.055, roll_len=0.42, roll_strap_w=0.024, step=0.025)
if FR:                                               # havresac 1812 (~37 x 32 x 13 cm, assumed from period figures)
    S.update(pack_w=0.36, pack_h=0.32, pack_d=0.125, roll_len=0.46)

MATS = [("HCL_couro_branco", (0.80, 0.79, 0.74), 0.6, 0), ("HCL_latao", (0.62, 0.43, 0.13), 0.35, 1),
        ("HCL_couro_preto", (0.015, 0.014, 0.013), 0.45, 0), ("HCL_pele_bezerro", (0.17, 0.09, 0.045), 0.95, 0),
        ("HCL_capote_cinza", (0.16, 0.16, 0.155), 0.95, 0), ("HCL_ferro", (0.18, 0.18, 0.19), 0.4, 1)]
BRANCO, LATAO, PRETO, BEZERRO, CAPOTE, FERRO = range(len(MATS))
TOP, EDGE, UNDER = 0, 1, 2


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


# ---------------------------------------------------------------- mesh builder with part / side / UV bookkeeping
class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.lc = self.bm.loops.layers.uv.new("local")
        self.PL = self.bm.faces.layers.int.new("hcl_part")
        self.KL = self.bm.faces.layers.int.new("hcl_lado")
        self.XL = self.bm.faces.layers.int.new("hcl_uvx")        # 1 = atlas UV set here; 0 = smart projection later
        self.parts = []
        self.frames = {}
        self.isl = 0

    def pid(self, name):
        if name not in self.parts:
            self.parts.append(name)
        return self.parts.index(name)

    def v(self, p):
        return self.bm.verts.new(p)

    def face(self, vs, part, mat, kind=TOP, uv=None, local=None, expect=None):
        """uv / local: per-vertex lists in the order of vs. expect: outward direction; the face is flipped to face it.
        UVs are assigned by vertex after any flip."""
        f = self.bm.faces.new(vs)
        f[self.PL] = self.pid(part)
        f[self.KL] = kind
        f.material_index = mat
        f.normal_update()
        if expect is not None and f.normal.dot(expect) < 0:
            f.normal_flip()
        if uv is not None:
            d = dict(zip(vs, uv))
            for l in f.loops:
                l[self.uv].uv = d[l.vert]
            f[self.XL] = 1
        if local is not None:
            d = dict(zip(vs, local))
            for l in f.loops:
                l[self.lc].uv = d[l.vert]
        return f

    def island(self):
        """Distinct far-away offset per UV island (the packer rearranges them; offsets only keep islands apart)."""
        self.isl += 1
        return Vector((0.0, 10.0 * self.isl))


# ---------------------------------------------------------------- surface projection and curves (as in the blockout)
def project_out(q, bvh, axis_y=0.02, up_bias=0.0):
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


def project_line(guide, bvh, up_bias_fn=lambda q: 0.0, smooth=2):
    C, N = [], []
    for q in guide:
        p, n = project_out(q, bvh, up_bias=up_bias_fn(q))
        if p is None:
            continue
        C.append(p); N.append(n.normalized())
    for _ in range(smooth):
        C = [C[0]] + [(C[i - 1] + C[i] * 2 + C[i + 1]) / 4 for i in range(1, len(C) - 1)] + [C[-1]]
        N = [N[0]] + [(N[i - 1] + N[i] * 2 + N[i + 1]).normalized() for i in range(1, len(N) - 1)] + [N[-1]]
    return C, N


def arclen(C, closed=False):
    s = [0.0]
    for i in range(1, len(C)):
        s.append(s[-1] + (C[i] - C[i - 1]).length)
    return s, (s[-1] + (C[0] - C[-1]).length if closed else s[-1])


def point_at(C, N, x):
    """Point, normal and tangent at arc length x along the open polyline C."""
    s, L = arclen(C)
    x = max(0.0, min(L, x))
    j = 0
    while j < len(s) - 2 and s[j + 1] < x:
        j += 1
    f = (x - s[j]) / max(s[j + 1] - s[j], 1e-9)
    return C[j].lerp(C[j + 1], f), N[j].lerp(N[j + 1], f).normalized(), (C[j + 1] - C[j]).normalized()


def resample(C, N, step, closed=False):
    pts = C + ([C[0]] if closed else [])
    nrm = N + ([N[0]] if closed else [])
    s, L = arclen(pts)
    m = max(2, round(L / step))
    oc, on = [], []
    j = 0
    for k in range(m if closed else m + 1):
        x = L * k / m
        while j < len(s) - 2 and s[j + 1] < x:
            j += 1
        f = (x - s[j]) / max(s[j + 1] - s[j], 1e-9)
        oc.append(pts[j].lerp(pts[j + 1], f))
        on.append(nrm[j].lerp(nrm[j + 1], f).normalized())
    return oc, on


def sub_line(C, N, x0, x1, step):
    """Resampled piece of the open polyline between arc lengths x0 and x1 (x1 < x0 walks backwards)."""
    m = max(1, round(abs(x1 - x0) / step))
    pts = [point_at(C, N, x0 + (x1 - x0) * k / m) for k in range(m + 1)]
    return [p for p, _, _ in pts], [n for _, n, _ in pts]


def frames_along(C, N, closed=False):
    out = []
    n = len(C)
    for i in range(n):
        t = (C[(i + 1) % n] - C[i - 1]) if closed else (C[min(i + 1, n - 1)] - C[max(i - 1, 0)])
        t.normalize()
        nn = (N[i] - t * N[i].dot(t)).normalized()
        out.append((t, nn, nn.cross(t).normalized()))
    return out


def tip_line(C, N, x0, x1, step, R):
    """Piece of C from x0 to x1 for a strap tip: `step` spacing, then fine samples over the last R (rounded end)."""
    L = abs(x1 - x0)
    sg = 1 if x1 >= x0 else -1
    xs = [k * step for k in range(int((L - R) / step) + 1)]
    xs += [L - R + R * math.sin(math.radians(a)) for a in (0, 20, 40, 60, 75, 90)]
    xs = sorted(set(round(v, 6) for v in xs if v <= L + 1e-9))
    pts = [point_at(C, N, x0 + sg * v) for v in xs]
    return [p for p, _, _ in pts], [n for _, n, _ in pts]


def belt_point(bvh, th, h, half_w, axis=Vector((0, 0.02, 0))):
    """Point of a horizontal belt around the body at angle th: the radius clears the surface at the belt's middle,
    upper and lower edges (the coat flares below the waist)."""
    d = Vector((math.sin(th), -math.cos(th), 0))
    best = None
    for dz in (0.0, -half_w, half_w):
        hit = bvh.ray_cast(Vector((axis.x, axis.y, Z(h + dz))) + d * 0.4, -d, 0.6)
        if hit[0] is None:
            continue
        r = (Vector((hit[0].x, hit[0].y, 0)) - Vector((axis.x, axis.y, 0))).length
        if best is None or r > best[0]:
            best = (r, Vector((hit[1].x, hit[1].y, 0)).normalized())
    r, n = best
    return Vector((axis.x, axis.y, Z(h))) + d * r, n


def rounded_end(s, L, w):
    """Width along a strap tip that ends in a half circle."""
    R = w / 2
    return [w if x < L - R else max(0.004, 2 * math.sqrt(max(0.0, R * R - (x - (L - R)) ** 2))) for x in s]


# ---------------------------------------------------------------- strap sweep (rounded top edges)
def strap_section(w, t):
    c = min(0.0012, 0.4 * t)
    return [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.55 * t), (w / 2 - c, t), (-w / 2 + c, t), (-w / 2, 0.55 * t)]


STRAP_KIND = [UNDER, EDGE, EDGE, TOP, EDGE, EDGE]


def sweep_strap(B, C, N, width, thick, gap, part, mat, closed=False, island=0.30, widths=None, caps=True):
    """Strap along the centre line C (on the surface) with normals N. Section: flat bottom, sides, chamfered top edges.
    Atlas UV: developed perimeter (bottom face its own island), islands cut every `island` metres. Local UV: (s, x)."""
    fr = frames_along(C, N, closed)
    n = len(C)
    s, total = arclen(C, closed)
    rings, secs, perim = [], [], []
    for i in range(n):
        t, nn, b = fr[i]
        w = widths[i] if widths else width
        sec = strap_section(w, thick)
        base = C[i] + nn * gap
        rings.append([B.v(base + b * x + nn * y) for x, y in sec])
        secs.append(sec)
        pc, acc = {1: 0.0}, 0.0                                  # perimeter from P1 around to P0 (bottom excluded)
        for p0, p1 in ((1, 2), (2, 3), (3, 4), (4, 5), (5, 0)):
            acc += math.hypot(sec[p1][0] - sec[p0][0], sec[p1][1] - sec[p0][1])
            pc[p1] = acc
        perim.append(pc)
    offs = {}
    for k in range(n if closed else n - 1):
        k2 = (k + 1) % n
        sa, sb = s[k], (s[k2] if k2 > k else total)
        key = math.floor(sa / island)
        if key not in offs:
            offs[key] = (B.island(), B.island())
        o_side, o_bot = offs[key]
        u0 = key * island
        for a in range(6):
            a2 = (a + 1) % 6
            vs = [rings[k][a], rings[k][a2], rings[k2][a2], rings[k2][a]]
            ss = [sa, sa, sb, sb]
            ids = [a, a2, a2, a]
            rr = [k, k, k2, k2]
            if a == 0:
                uv = [Vector((x - u0, secs[r][j][0] + secs[r][1][0])) + o_bot for x, j, r in zip(ss, ids, rr)]
            else:
                uv = [Vector((x - u0, perim[r][j] if not (j == 1 and a == 5) else perim[r][1])) + o_side
                      for x, j, r in zip(ss, ids, rr)]
            local = [Vector((x, secs[r][j][0])) for x, j, r in zip(ss, ids, rr)]
            B.face(vs, part, mat, STRAP_KIND[a], uv=uv, local=local)
    if not closed and caps:
        for ring, sec, sv, rev in ((rings[0], secs[0], 0.0, True), (rings[-1], secs[-1], s[-1], False)):
            o = B.island()
            vs = ring[::-1] if rev else ring
            d = {v: (x, y) for v, (x, y) in zip(ring, sec)}
            B.face(vs, part, mat, EDGE, uv=[Vector(d[v]) + o for v in vs], local=[Vector((sv, d[v][0])) for v in vs])
    return rings, s


# ---------------------------------------------------------------- tubes (scabbard, socket, roll)
def tube(B, P, R, side, seg, part, mat, flatten_a=1.0, flatten_b=1.0, caps=(True, True), kind=TOP, rfun=None):
    """Tube along the polyline P with radii R. Section axes: a = side made perpendicular (the UV seam, put it on the hidden
    side), b = direction x a; flatten_a / flatten_b scale them. rfun(i, theta) -> radius factor.
    Local UV: (s, theta * mean radius)."""
    n = len(P)
    s = [0.0]
    for i in range(1, n):
        s.append(s[-1] + (P[i] - P[i - 1]).length)
    rings = []
    rmean = sum(R) / n
    for i in range(n):
        d = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        a = (side - d * side.dot(d)).normalized()
        b = d.cross(a)
        ring = []
        for j in range(seg):
            th = 2 * math.pi * j / seg
            f = rfun(i, th) if rfun else 1.0
            ring.append(B.v(P[i] + (a * math.cos(th) * flatten_a + b * math.sin(th) * flatten_b) * R[i] * f))
        rings.append(ring)
    o = B.island()
    for i in range(n - 1):
        for j in range(seg):
            j2 = (j + 1) % seg
            vs = [rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j]]
            th = [j, j + 1, j + 1, j]
            ss = [s[i], s[i], s[i + 1], s[i + 1]]
            lc = [Vector((x, 2 * math.pi * t / seg * rmean)) for x, t in zip(ss, th)]
            B.face(vs, part, mat, kind, uv=[q + o for q in lc], local=lc)
    for ring, rev, sv, k in ((rings[0], True, 0.0, caps[0]), (rings[-1], False, s[-1], caps[1])):
        if k:
            vs = ring[::-1] if rev else ring
            B.face(vs, part, mat, EDGE, local=[Vector((sv, 0.0))] * len(vs))
    return rings, s


# ---------------------------------------------------------------- rounded box (lattice on a cube, edges rounded)
def axis_coords(h, r, n):
    if r <= 0:
        return [-h + 2 * h * k / n for k in range(n + 1)]
    hi = h - r
    inner = [-hi + 2 * hi * k / n for k in range(1, n)]
    return [-h, -hi - 0.414 * r, -hi] + inner + [hi, hi + 0.414 * r, h]


def rounded_box(B, centre, ax, ay, az, hx, hy, hz, r, part, mat, nseg=(1, 1, 1), bulge=None, kind=TOP, name=None):
    """Box of half sizes hx, hy, hz on the axes ax, ay, az, edges rounded with radius r (4 segments per 90 deg).
    bulge = (axis index, sign, amount): that side pushed out, most at its centre."""
    cs = [axis_coords(h, r, n) for h, n in zip((hx, hy, hz), nseg)]
    H = (hx, hy, hz)
    verts = {}
    right = ax.cross(ay).dot(az) > 0

    def vert(i, j, k):
        key = (i, j, k)
        if key not in verts:
            c = Vector((cs[0][i], cs[1][j], cs[2][k]))
            pin = Vector([max(-(H[q] - r), min(H[q] - r, c[q])) for q in range(3)])
            off = c - pin
            p = pin + (off.normalized() * r if r > 0 and off.length > 1e-12 else off)
            if bulge:
                q, sg, amt = bulge
                nrm = off.normalized() if off.length > 1e-12 else Vector((0, 0, 0))
                o1, o2 = [x for x in range(3) if x != q]
                w = max(0.0, nrm[q] * sg) * max(0.0, 1 - (c[o1] / H[o1]) ** 2) * max(0.0, 1 - (c[o2] / H[o2]) ** 2)
                p = p + nrm * amt * w
            verts[key] = B.v(centre + ax * p.x + ay * p.y + az * p.z)
        return verts[key]

    N = [len(c) - 1 for c in cs]
    for q, sg, ua, va in ((0, 1, 1, 2), (0, -1, 2, 1), (1, 1, 2, 0), (1, -1, 0, 2), (2, 1, 0, 1), (2, -1, 1, 0)):
        fixed = N[q] if sg > 0 else 0
        for i in range(N[ua]):
            for j in range(N[va]):
                idx = []
                for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    ijk = [0, 0, 0]
                    ijk[q], ijk[ua], ijk[va] = fixed, i + du, j + dv
                    idx.append(vert(*ijk))
                B.face(idx if right else idx[::-1], part, mat, kind)
    if name:
        B.frames[name] = {"c": list(centre), "x": list(ax), "y": list(ay), "z": list(az), "h": [hx, hy, hz], "r": r}


# ---------------------------------------------------------------- bent plate (flaps over the top and the front)
def bent_plate(B, origin, ax, out, up, half_depth, top_h, r, gap, W, drop, Rc, thick, part, mat, cols=3, n1=3, n3=3,
               bulge_fn=None, name=None):
    """Plate hinged at the back top edge of a rounded box, over the top, around the front edge (radius r + gap) and down
    the front by `drop`; bottom corners rounded with radius Rc. Local frame: x along ax, q along out, h along up.
    Inner surface at `gap` from the box, outer surface `thick` further out. Local UV = (x, d), d along the plate."""
    L1 = 2 * half_depth - 2 * r
    La = (r + gap) * math.pi / 2
    L3 = drop - r
    D = L1 + La + L3

    def prof(d, layer):
        g = gap + layer
        if d <= L1:
            return -half_depth + r + d, top_h + g, 0.0, 1.0
        if d <= L1 + La:
            ph = math.pi / 2 - (d - L1) / (r + gap)
            return half_depth - r + (r + g) * math.cos(ph), top_h - r + (r + g) * math.sin(ph), math.cos(ph), math.sin(ph)
        return half_depth + g, top_h - r - (d - L1 - La), 1.0, 0.0

    xs = sorted(set([round(x, 7) for x in [-W / 2, -W / 2 + Rc / 2, -W / 2 + Rc, W / 2 - Rc, W / 2 - Rc / 2, W / 2]
                     + [-W / 2 + Rc + (W - 2 * Rc) * k / cols for k in range(1, cols)]]))
    ds = sorted(set([round(x, 7) for x in [L1 * k / n1 for k in range(n1 + 1)] + [L1 + La * k / 3 for k in range(1, 4)]
                     + [L1 + La + (L3 - Rc) * k / n3 for k in range(1, n3 + 1)] + [D - Rc / 2, D]]))

    def round_corner(x, d):
        cd = D - Rc
        if abs(x) > W / 2 - Rc + 1e-9 and d > cd + 1e-9:
            a, b = abs(x) - (W / 2 - Rc), d - cd
            m, ln = max(a, b), math.hypot(a, b)
            return math.copysign(W / 2 - Rc + a * m / ln, x), cd + b * m / ln
        return x, d

    grid, XD = {}, {}
    for layer in (0, 1):
        for i, x0 in enumerate(xs):
            for j, d0 in enumerate(ds):
                x, d = round_corner(x0, d0)
                q, h, nq, nh = prof(d, thick * layer)
                p = origin + ax * x + out * q + up * h
                if bulge_fn and d > L1 + La:
                    p = p + out * bulge_fn(x, h)
                v = B.v(p)
                grid[(layer, i, j)] = v
                XD[v] = (x, d)
    ni, nj = len(xs) - 1, len(ds) - 1
    o_top, o_bot = B.island(), B.island()

    def nrm_at(d):
        _, _, nq, nh = prof(d, 0)
        return out * nq + up * nh

    for layer, kind, o, sg in ((1, TOP, o_top, 1), (0, UNDER, o_bot, -1)):
        for i in range(ni):
            for j in range(nj):
                vs = [grid[(layer, i, j)], grid[(layer, i + 1, j)], grid[(layer, i + 1, j + 1)], grid[(layer, i, j + 1)]]
                dm = sum(XD[v][1] for v in vs) / 4
                B.face(vs, part, mat, kind, uv=[Vector(XD[v]) + o for v in vs], local=[Vector(XD[v]) for v in vs],
                       expect=nrm_at(dm) * sg)
    loop = [(i, 0) for i in range(ni)] + [(ni, j) for j in range(nj)] + [(i, nj) for i in range(ni, 0, -1)] + \
           [(0, j) for j in range(nj, 0, -1)]
    o = B.island()
    acc = 0.0
    for k in range(len(loop)):
        i, j = loop[k]
        i2, j2 = loop[(k + 1) % len(loop)]
        a0, b0 = grid[(0, i, j)], grid[(0, i2, j2)]
        a1, b1 = grid[(1, i, j)], grid[(1, i2, j2)]
        ln = (b0.co - a0.co).length
        if j == j2 == 0:
            exp = -(grid[(0, i, 1)].co - a0.co)
        elif j == j2 == nj:
            exp = a0.co - grid[(0, i, nj - 1)].co
        elif i == i2 == 0:
            exp = -ax
        else:
            exp = ax
        B.face([a0, b0, b1, a1], part, mat, EDGE,
               uv=[Vector((acc, 0)) + o, Vector((acc + ln, 0)) + o, Vector((acc + ln, thick)) + o, Vector((acc, thick)) + o],
               local=[Vector(XD[a0]), Vector(XD[b0]), Vector(XD[b0]), Vector(XD[a0])], expect=exp)
        acc += ln
    if name:
        B.frames[name] = {"W": W, "D": D, "Rc": Rc, "L1": L1, "La": La, "drop": drop, "c": list(origin), "x": list(ax),
                          "q": list(out), "h": list(up), "hz": half_depth, "hy": top_h, "r": r}
    return D


# ---------------------------------------------------------------- frame buckle (chamfered frame, optional centre bar)
def frame_buckle(B, centre, xa, ya, za, iw, ih, bar, th, part, mat, centre_bar=False, tongue=True):
    """Buckle lying on a strap, za outward: inner opening iw (along xa) x ih (along ya), bars `bar` wide, `th` thick.
    centre_bar: a bar along ya at the middle. tongue: hinged on the -ya bar, lying along +ya."""
    ow, oh = iw + 2 * bar, ih + 2 * bar
    cr = bar * 0.6

    def contour(w, h, c):
        return [(-w / 2 + c, -h / 2), (w / 2 - c, -h / 2), (w / 2, -h / 2 + c), (w / 2, h / 2 - c),
                (w / 2 - c, h / 2), (-w / 2 + c, h / 2), (-w / 2, h / 2 - c), (-w / 2, -h / 2 + c)]

    e = min(0.0008, th * 0.3)
    layers = [contour(ow, oh, cr), contour(ow - 2 * e, oh - 2 * e, cr * 0.8), contour(iw + 2 * e, ih + 2 * e, 0.0006),
              contour(iw, ih, 0.0004)]
    zs = [0.0, th, th, 0.0]
    V = [[B.v(centre + xa * x + ya * y + za * z) for x, y in L] for L, z in zip(layers, zs)]
    kinds = [EDGE, TOP, EDGE, UNDER]
    for k in range(4):
        k2 = (k + 1) % 4
        for i in range(8):
            i2 = (i + 1) % 8
            vs = [V[k][i], V[k][i2], V[k2][i2], V[k2][i]]
            mid = sum((v.co for v in vs), Vector()) / 4 - centre
            radial = mid - za * mid.dot(za)
            exp = (radial, za, -radial, -za)[k]
            B.face(vs, part, mat, kinds[k], expect=exp)
    if centre_bar:
        rounded_box(B, centre + za * (th * 0.45), xa, ya, za, bar * 0.4, ih / 2 + bar * 0.5, th * 0.45, 0.0, part, mat)
    if tongue:
        L = ih + bar * 0.8
        rounded_box(B, centre + ya * (-ih / 2 - bar / 2 + L / 2) + za * (th + 0.0008), xa, ya, za, 0.0011, L / 2, 0.0008,
                    0.0, part, mat)


# ---------------------------------------------------------------- objects
def new_object(name, B, coll):
    me = bpy.data.meshes.new(name)
    B.bm.to_mesh(me)
    B.bm.free()
    make_mats(me)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob["hcl_partes"] = ",".join(B.parts)
    ob["hcl_frames"] = json.dumps(B.frames)
    me.uv_layers.active = me.uv_layers["UVMap"]
    me.uv_layers["UVMap"].active_render = True
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(50))
    return ob


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


V_COLL = bpy.data.collections.new("HCL_Colete_LOD0")
B_COLL = bpy.data.collections.new("HCL_Mochila_LOD0")
for c in (V_COLL, B_COLL):
    bpy.context.scene.collection.children.link(c)

# =============================================================== VEST
VB = Builder()
# 1. waist belt (closed ring from the front centre toward the wearer's left), front buckle, belt tip, keeper
H_BELT = 1.112
b_out = S["belt_gap"] + S["belt_t"]
if not FR:                                        # the French line infantry wore no waist belt
    H_BELT = 1.112
    ring = [belt_point(TORSO_OUT, 2 * math.pi * i / 64, H_BELT, S["waist_w"] / 2) for i in range(64)]
    BC, BN = resample([p for p, _ in ring], [n for _, n in ring], S["step"], closed=True)
    sweep_strap(VB, BC, BN, S["waist_w"], S["belt_t"], S["belt_gap"], "cinturao", BRANCO, closed=True)
    b_out = S["belt_gap"] + S["belt_t"]
    bt_, bn_, bb_ = frames_along(BC, BN, True)[0]                     # along (toward the wearer's left), out, up
    BCo, BNo = BC + [BC[0]], BN + [BN[0]]                              # open copy for arc-length lookups
    tC, tN = tip_line(BCo, BNo, 0.0, 0.115, 0.012, S["waist_w"] / 2)
    ts, tL = arclen(tC)
    sweep_strap(VB, tC, tN, S["waist_w"], S["belt_t"] * 0.9, b_out + 0.0003, "cinturao_ponta", BRANCO,
                widths=rounded_end(ts, tL, S["waist_w"]))
    kp, kn, kt = point_at(BCo, BNo, 0.068)
    sweep_strap(VB, [kp - kt * 0.007, kp + kt * 0.007], [kn, kn], S["waist_w"] + 0.003, 2 * S["belt_t"] + 0.0028,
                S["belt_gap"] - 0.0012, "passante", BRANCO)
    bc = BC[0] + bn_ * (b_out + 0.0006)
    # frame: vertical opening 5.2 cm for the 5 cm belt, centre bar; the tongue lies toward the tip
    frame_buckle(VB, bc, bt_, bb_, bn_, 0.048, 0.052, 0.0065, 0.0038, "fivela_cinturao", LATAO, centre_bar=True, tongue=False)
    rounded_box(VB, bc + bt_ * 0.012 + bn_ * (0.0038 + 0.0008), bt_, bb_, bn_, 0.012, 0.0011, 0.0008, 0.0, "fivela_cinturao", LATAO)

# 2. cartridge box, flap, plate, closing tab, stud
pb, nb_ = project_out(Vector((-0.12, 0.16, Z(0.985))), TORSO_OUT)
nb_ = Vector((nb_.x, nb_.y, 0)).normalized()
xa = UP.cross(nb_).normalized()                                    # toward the wearer's right / front
hx, hy, hz = S["box_w"] / 2, S["box_h"] / 2, S["box_d"] / 2
centre = pb + nb_ * (0.008 + hz)
rounded_box(VB, centre, xa, UP, nb_, hx, hy, hz, S["box_r"], "cartucheira_corpo", PRETO, nseg=(3, 2, 1),
            name="cartucheira_corpo")
bent_plate(VB, centre, xa, nb_, UP, hz, hy, S["box_r"], 0.0012, 2 * hx + 0.008, S["flap_drop"], 0.022, S["flap_t"],
           "cartucheira_tampa", PRETO, cols=4, name="cartucheira_tampa")
front_out = hz + 0.0012 + S["flap_t"]
plate_c = centre + nb_ * (front_out + 0.0007) + UP * (hy - S["box_r"] - (S["flap_drop"] - S["box_r"]) * 0.47)
rounded_box(VB, plate_c, xa, UP, nb_, 0.030, 0.019, 0.0007, 0.0, "cartucheira_placa", LATAO, name="cartucheira_placa")
tab_top, tab_bot = hy - S["flap_drop"] + 0.012, -hy + 0.016
tabC = [centre + nb_ * hz + UP * (tab_top - (tab_top - tab_bot) * k / 4) for k in range(5)]
sweep_strap(VB, tabC, [nb_] * 5, 0.022, 0.0025, 0.0012, "cartucheira_presilha", PRETO)
sp = centre + UP * (tab_bot + 0.004)
tube(VB, [sp + nb_ * (hz + 0.0012), sp + nb_ * (hz + 0.0058), sp + nb_ * (hz + 0.0072)], [0.0048, 0.0048, 0.0025], UP, 8,
     "cartucheira_botao", LATAO, caps=(False, True))

# 3. crossbelt: over the left shoulder, across the chest / down the back, both legs ending under the flap's hinge
attach_out = centre + xa * (hx - 0.035) + UP * (hy - 0.012) - nb_ * (hz - 0.004)
attach_in = centre - xa * (hx - 0.035) + UP * (hy - 0.012) - nb_ * (hz - 0.004)
G_FRONT = [Vector((0.15, 0.035, Z(1.585))), Vector((0.118, -0.06, Z(1.52))), Vector((0.07, -0.12, Z(1.42))),
           Vector((-0.01, -0.145, Z(1.30))), Vector((-0.09, -0.135, Z(1.19))), Vector((-0.16, -0.08, Z(1.08))),
           Vector((-0.19, 0.03, Z(1.04))), attach_out + UP * 0.03 + xa * 0.02, attach_out]
G_BACK = [Vector((0.15, 0.035, Z(1.585))), Vector((0.12, 0.11, Z(1.50))), Vector((0.06, 0.155, Z(1.38))),
          Vector((-0.02, 0.165, Z(1.25))), Vector((-0.07, 0.17, Z(1.14))), attach_in + UP * 0.03, attach_in]
shoulder_bias = lambda q: 1.6 * max(0.0, min(1.0, (q.z - Z(1.47)) / 0.08))
cross_gap = S["belt_gap"] + S["belt_t"] + 0.001
for nm, G in (("bandoleira_frente", G_FRONT), ("bandoleira_costas", G_BACK)):
    C, N = project_line(catmull(G, 8), TORSO_OUT, shoulder_bias)
    C, N = resample(C, N, S["step"])
    sweep_strap(VB, C, N, S["cross_w"], S["belt_t"], cross_gap, nm, BRANCO)
if FR:
    # baudrier: right shoulder -> bayonet frog on the left hip, under the cartridge belt where they cross
    TH_F, H_FROG = math.radians(98), 1.045
    d_f = Vector((math.sin(TH_F), -math.cos(TH_F), 0))
    hit = TORSO_OUT.ray_cast(Vector((0, 0.02, Z(H_FROG))) + d_f * 0.4, -d_f, 0.6)
    frog_top = hit[0] + Vector((hit[1].x, hit[1].y, 0)).normalized() * (S["belt_gap"] + S["belt_t"])
    side_f = UP.cross(Vector((hit[1].x, hit[1].y, 0)).normalized()).normalized()      # toward the back
    B_FRONT = [Vector((-0.15, 0.035, Z(1.585))), Vector((-0.118, -0.06, Z(1.52))), Vector((-0.07, -0.12, Z(1.42))),
               Vector((0.01, -0.145, Z(1.30))), Vector((0.09, -0.135, Z(1.19))), Vector((0.15, -0.085, Z(1.10))),
               frog_top - side_f * 0.018 + UP * 0.02, frog_top - side_f * 0.012]
    B_BACK = [Vector((-0.15, 0.035, Z(1.585))), Vector((-0.12, 0.11, Z(1.50))), Vector((-0.06, 0.155, Z(1.38))),
              Vector((0.02, 0.165, Z(1.25))), Vector((0.10, 0.145, Z(1.14))), Vector((0.165, 0.07, Z(1.08))),
              frog_top + side_f * 0.018 + UP * 0.02, frog_top + side_f * 0.012]
    for nm, G in (("boldrie_frente", B_FRONT), ("boldrie_costas", B_BACK)):
        C, N = project_line(catmull(G, 8), TORSO_OUT, shoulder_bias)
        C, N = resample(C, N, S["step"])
        sweep_strap(VB, C, N, S["cross_w"], S["belt_t"], S["belt_gap"], nm, BRANCO)

# 4. bayonet: frog on the belt at the left hip; scabbard; socket bayonet
th_f = math.radians(98 if FR else 100)
d_f = Vector((math.sin(th_f), -math.cos(th_f), 0))
hit = TORSO_OUT.ray_cast(Vector((0, 0.02, Z(1.045 if FR else H_BELT))) + d_f * 0.4, -d_f, 0.6)
pf_, nf_ = hit[0], Vector((hit[1].x, hit[1].y, 0)).normalized()
side = UP.cross(nf_).normalized()                                  # horizontal along the body, toward the back
frog_c = pf_ + nf_ * (b_out + 0.006)
s0 = frog_c + nf_ * 0.010 + Vector((0, 0, -0.01))
tilt = Matrix.Rotation(math.radians(14), 3, side)
q = s0 + (tilt @ Vector((0, 0, -1))) * S["scab_len"]
pt, nt = project_out(q, LEGS_OUT)
s1 = pt + Vector((nt.x, nt.y, 0)).normalized() * 0.016 if pt is not None else q
pm, nm_ = project_out((s0 + s1) / 2, LEGS_OUT)
mid = (s0 + s1) / 2
sm = pm + Vector((nm_.x, nm_.y, 0)).normalized() * 0.016 if pm is not None else mid
if (sm - mid).dot(Vector((nf_.x, nf_.y, 0))) < 0:
    sm = mid
down = (sm - s0).normalized()
d2 = (s1 - sm).normalized()
print(f"scabbard: top h {s0.z - GROUND:.3f}, bottom h {s1.z - GROUND:.3f}")
hidden = -nf_                                       # seams face the body; the body-ward axis is the flattened one
FL = 0.55
scab = [s0 + down * 0.030] + [s0 + down * 0.030 + (sm - s0 - down * 0.030) * (k / 4) for k in range(1, 5)] + \
       [sm + (s1 - d2 * 0.055 - sm) * (k / 4) for k in range(1, 5)]
scab_r = [0.0120 - 0.0015 * (k / (len(scab) - 1)) - 0.0020 * max(0, (k - 4) / 4) for k in range(len(scab))]
tube(VB, scab, scab_r, hidden, 12, "bainha", PRETO, flatten_a=FL)
tube(VB, [s0 - down * 0.002, s0 + down * 0.004, s0 + down * 0.034], [0.0142, 0.0136, 0.0133], hidden, 12, "bainha_bocal",
     LATAO, flatten_a=0.58)
tube(VB, [s1 - d2 * 0.060, s1 - d2 * 0.040, s1 - d2 * 0.015, s1], [0.0090, 0.0082, 0.0068, 0.0058], hidden, 12,
     "bainha_ponteira", LATAO, flatten_a=0.62)
tube(VB, [s1 - d2 * 0.001, s1 + d2 * 0.004, s1 + d2 * 0.009, s1 + d2 * 0.013], [0.0050, 0.0068, 0.0060, 0.0018], hidden, 10,
     "bainha_ponteira", LATAO)
# frog: loop around the belt, pocket around the scabbard under the locket, back panel between them
if not FR:                                          # (French frog: sewn to the baudrier's ends, no belt loop)
    loopC, loopN = [], []
    for th in (th_f - 0.024 / 0.17, th_f, th_f + 0.024 / 0.17):
        p_, n_ = belt_point(TORSO_OUT, th, H_BELT, S["waist_w"] / 2 + 0.002)
        loopC.append(p_); loopN.append(n_)
    sweep_strap(VB, loopC, loopN, S["waist_w"] + 0.004, 2 * S["belt_t"] + 0.003, S["belt_gap"] - 0.001, "passador", BRANCO)
tube(VB, [s0 + down * 0.038, s0 + down * 0.068, s0 + down * 0.098], [0.0152, 0.0150, 0.0146], hidden, 12, "passador", BRANCO,
     flatten_a=0.62)
pa_, pb_ = frog_c - UP * 0.015 - nf_ * 0.004, s0 + down * 0.040 - nf_ * 0.0115
sweep_strap(VB, [pa_.lerp(pb_, k / 3) for k in range(4)], [nf_] * 4, 0.040, 0.003, 0.0, "passador", BRANCO)
# socket bayonet: blade root in the scabbard mouth, neck, socket parallel to the scabbard and offset toward the FRONT
# (behind it, the socket lay under the knapsack's left shoulder strap and came through it in the movement test)
axis_up = -down
root = s0 + axis_up * 0.004
fwd = -side
sock0 = root + fwd * S["socket_off"] + axis_up * 0.010
tube(VB, [root - axis_up * 0.020, root, root + axis_up * 0.006], [0.0075, 0.0075, 0.0060], nf_, 3, "baioneta_lamina", FERRO,
     flatten_b=0.35)
tube(VB, [root + axis_up * 0.004, root + axis_up * 0.009 + fwd * 0.013, sock0 + axis_up * 0.002 - fwd * 0.002],
     [0.0042, 0.0045, 0.0050], hidden, 8, "baioneta_pescoco", FERRO)
tube(VB, [sock0, sock0 + axis_up * 0.006, sock0 + axis_up * 0.008, sock0 + axis_up * 0.040, sock0 + axis_up * S["socket_len"]],
     [0.0128, 0.0128, S["socket_r"], S["socket_r"], S["socket_r"]], hidden, 14, "baioneta_alvado", FERRO)
VB.frames["baioneta_alvado"] = {"c": list(sock0), "z": list(axis_up), "x": list(fwd), "len": S["socket_len"]}
vest = new_object("HCL_V_Fr1812_Correame_LOD0" if FR else "HCL_V_Pruss1813_Correame_LOD0", VB, V_COLL)

# =============================================================== BACKPACK
KB = Builder()
samples = []
for x in (-0.12, 0.0, 0.12):
    for h in (1.20, 1.30, 1.42):
        hit = TORSO_OUT.ray_cast(Vector((x, 0.8, Z(h))), Vector((0, -1, 0)), 1.5)
        if hit[0] is not None:
            samples.append(hit[0])
y_back = max(p.y for p in samples)
lean = math.atan2(max(p.y for p in samples if abs(p.z - Z(1.42)) < 0.01) - max(p.y for p in samples if abs(p.z - Z(1.20)) < 0.01), 0.22)
ax_x = Vector((1, 0, 0))
ax_z = (Matrix.Rotation(-lean, 3, ax_x) @ Vector((0, 0, 1))).normalized()
ax_y = ax_z.cross(ax_x).normalized() * -1
if ax_y.y < 0:
    ax_y = -ax_y
phx, phz, phy = S["pack_w"] / 2, S["pack_h"] / 2, S["pack_d"] / 2
pc = Vector((0, y_back + 0.006 + phy, Z(1.31)))
PB = S["pack_bulge"]


def pbulge(x, h):
    return PB * max(0.0, 1 - (x / phx) ** 2) * max(0.0, 1 - (h / phz) ** 2)


rounded_box(KB, pc, ax_x, ax_y, ax_z, phx, phy, phz, S["pack_r"], "mochila_corpo", PRETO, nseg=(4, 1, 4), bulge=(1, 1, PB),
            name="mochila_corpo")
bent_plate(KB, pc, ax_x, ax_y, ax_z, phy, phz, S["pack_r"], 0.0015, 2 * phx + 0.010, S["pflap_drop"], 0.030, S["pflap_t"],
           "mochila_tampa", BEZERRO, cols=4, n1=3, n3=4, bulge_fn=pbulge, name="mochila_tampa")
# closing straps: sewn under the flap, down the outer face to buckles held by tabs sewn to the body
front = lambda x, h, g: pc + ax_x * x + ax_z * h + ax_y * (phy + pbulge(x, h) + g)
fl_bot = phz - S["pflap_drop"]
hb = fl_bot - 0.050                                                # buckle centre
for sx in (-0.10, 0.10):
    hs = [fl_bot + 0.035 - (0.035 + 0.045) * k / 6 for k in range(7)]
    sweep_strap(KB, [front(sx, h, 0.0) for h in hs], [ax_y] * 7, 0.024, 0.0028, 0.0015, "mochila_correia_fecho", PRETO)
    frame_buckle(KB, front(sx, hb, 0.0015 + 0.0028 + 0.0004), ax_x, -ax_z, ax_y, 0.026, 0.020, 0.004, 0.003,
                 "mochila_fivela", LATAO)
    ht = [hb + 0.004 - 0.034 * k / 3 for k in range(4)]
    sweep_strap(KB, [front(sx, h, 0.0) for h in ht], [ax_y] * 4, 0.026, 0.0028, 0.0010, "mochila_presilha", PRETO)
# greatcoat roll on top of the flap: folds, the outer layer's edge, pinched flat under the two straps
roll_c = pc + ax_z * (phz + S["pflap_t"] + 0.0015 + S["roll_r"] - 0.004) + ax_y * 0.004
RL, RR, SW = S["roll_len"], S["roll_r"], S["roll_strap_w"]
straps_x = (-0.12, 0.12)
xs = sorted(set([round(-RL / 2 + RL * k / 12, 6) for k in range(13)]
                + [round(sx + o, 6) for sx in straps_x for o in (-SW / 2 - 0.001, 0.0, SW / 2 + 0.001)]))
PINCH = 0.075
TH_STEP = 1.05                                       # the outer layer ends on the front, low (from the bottom toward out)


def pinch_of(x):
    return max(1.0 if abs(x - sx) <= SW / 2 + 0.0011 else math.exp(-((abs(x - sx) - SW / 2) / 0.016) ** 2) for sx in straps_x)


def roll_r(i, th):
    x = xs[i]
    pn = pinch_of(x)
    folds = 0.018 * math.cos(3 * th + 0.7) * (1 - 0.6 * abs(x) / (RL / 2)) + 0.012 * math.cos(5 * th + 2.1 + 9 * x)
    step = 0.030 * ((th - TH_STEP) % (2 * math.pi)) / (2 * math.pi) - 0.015
    return (1.0 - PINCH * pn + (folds + step) * (1 - pn)) * (1 - 0.05 * (abs(x) / (RL / 2)) ** 4)


rings, rs = tube(KB, [roll_c + ax_x * x for x in xs], [RR] * len(xs), -ax_z, 16, "capote", CAPOTE, rfun=roll_r,
                 caps=(False, False))
for ring, sgn in ((rings[0], -1), (rings[-1], 1)):
    c0 = sum((v.co for v in ring), Vector()) / len(ring)
    inner = [KB.v(c0.lerp(v.co, 0.55) - ax_x * sgn * 0.007) for v in ring]
    ctr = KB.v(c0 - ax_x * sgn * 0.011)
    n = len(ring)
    for j in range(n):
        j2 = (j + 1) % n
        KB.face([ring[j], ring[j2], inner[j2], inner[j]], "capote_ponta", CAPOTE, TOP, expect=ax_x * sgn)
        KB.face([inner[j], inner[j2], ctr], "capote_ponta", CAPOTE, TOP, expect=ax_x * sgn)
KB.frames["capote"] = {"c": list(roll_c), "x": list(ax_x), "a": list(-ax_z), "b": list(ax_y), "R": RR, "L": RL,
                       "straps": list(straps_x), "strap_w": SW, "th_step": TH_STEP}
for sx in straps_x:
    rr_ = RR * (1 - PINCH) * (1 - 0.05 * (abs(sx) / (RL / 2)) ** 4)
    C, N = [], []
    for j in range(16):
        th = 2 * math.pi * j / 16
        n_ = ax_y * math.cos(th) + ax_z * math.sin(th)
        C.append(roll_c + ax_x * sx + n_ * (rr_ - 0.001)); N.append(n_)
    sweep_strap(KB, C, N, SW, 0.0028, 0.0015, "capote_correia", BRANCO, closed=True)
    th_b = math.radians(55)
    nb2 = ax_y * math.cos(th_b) + ax_z * math.sin(th_b)
    tb = -ax_y * math.sin(th_b) + ax_z * math.cos(th_b)
    frame_buckle(KB, roll_c + ax_x * sx + nb2 * (rr_ + 0.0015 + 0.0028 + 0.0004), ax_x, tb, nb2, 0.026, 0.018, 0.004, 0.003,
                 "capote_fivela", LATAO)
    tipC, tipN = [], []
    for k in range(5):
        th = th_b + 0.020 / rr_ + k * 0.055 / rr_ / 4
        n_ = ax_y * math.cos(th) + ax_z * math.sin(th)
        tipC.append(roll_c + ax_x * sx + n_ * (rr_ - 0.001)); tipN.append(n_)
    ts, tL = arclen(tipC)
    sweep_strap(KB, tipC, tipN, SW, 0.0026, 0.0015 + 0.0028 + 0.0003, "capote_correia", BRANCO,
                widths=rounded_end(ts, tL, SW))
# shoulder straps: pack top corner, over the shoulder, down the chest (buckle), under the arm, pack bottom corner
for s, lado in ((1, "E"), (-1, "D")):
    g = [pc + ax_x * s * 0.10 + ax_z * (phz - 0.02) + ax_y * (-phy),
         Vector((s * 0.135, 0.10, Z(1.535))), Vector((s * 0.145, 0.02, Z(1.585))), Vector((s * 0.145, -0.07, Z(1.53))),
         Vector((s * 0.155, -0.115, Z(1.42))), Vector((s * 0.185, -0.08, Z(1.31))), Vector((s * 0.20, 0.02, Z(1.24))),
         Vector((s * 0.17, 0.12, Z(1.19))), pc + ax_x * s * 0.15 + ax_z * (-phz + 0.03) + ax_y * (-phy)]
    C, N = project_line(catmull(g, 7), TORSO_OUT, lambda q: 1.6 * max(0.0, min(1.0, (q.z - Z(1.47)) / 0.08)))
    C, N = resample(C, N, 0.032)
    sweep_strap(KB, C, N, S["strap_w"], S["strap_t"], S["strap_gap"], f"correia_ombro_{lado}", BRANCO)
    target = Vector((s * 0.155, -0.12, Z(1.40)))
    ib = min(range(len(C)), key=lambda i: (C[i] - target).length)
    sC, _ = arclen(C)
    sb_ = sC[ib]
    t, nn, b = frames_along(C, N)[ib]
    lift = S["strap_gap"] + S["strap_t"]
    frame_buckle(KB, C[ib] + nn * (lift + 0.0004), b, t, nn, 0.047, 0.020, 0.0045, 0.0032, f"correia_ombro_{lado}_fivela",
                 LATAO)
    # the lower strap's tip goes through the buckle and up over the upper strap; a keeper holds it
    tipC, tipN = tip_line(C, N, sb_, sb_ - 0.075, 0.012, S["strap_w"] / 2)
    ts, tL = arclen(tipC)
    sweep_strap(KB, tipC, tipN, S["strap_w"], S["strap_t"] * 0.9, lift + 0.0003, f"correia_ombro_{lado}_ponta", BRANCO,
                widths=rounded_end(ts, tL, S["strap_w"]))
    kp, kn, kt = point_at(C, N, sb_ - 0.035)
    sweep_strap(KB, [kp - kt * 0.006, kp + kt * 0.006], [kn, kn], S["strap_w"] + 0.003, 2 * S["strap_t"] + 0.0028,
                S["strap_gap"] - 0.0012, f"correia_ombro_{lado}_ponta", BRANCO)
pack = new_object("HCL_B_Fr1812_Havresac_LOD0" if FR else "HCL_B_Pruss1813_Tornister_LOD0", KB, B_COLL)


# ---------------------------------------------------------------- atlas UV: smart projection of the rest, then pack
def atlas(ob):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(ob.data)
    XL = bm.faces.layers.int.get("hcl_uvx")
    for f in bm.faces:
        f.select = f[XL] == 0
    bmesh.update_edit_mesh(ob.data)
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin=0.003, shape_method="CONCAVE")
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=0.003)
    bpy.ops.object.mode_set(mode="OBJECT")


for ob in (vest, pack):
    atlas(ob)

# ---------------------------------------------------------------- checks
log = []


def P(s):
    print(s); log.append(s)


def inside_uniform(ob):
    parts = ob["hcl_partes"].split(",")
    pa = ob.data.attributes["hcl_part"].data
    vpart = {}
    for p in ob.data.polygons:
        for i in p.vertices:
            vpart[i] = parts[pa[p.index].value]
    found = []
    for v in ob.data.vertices:
        p = ob.matrix_world @ v.co
        d = Vector((p.x, p.y - 0.02, 0))
        if d.length < 1e-6:
            continue
        d.normalize()
        hit = ALL_U.ray_cast(p + d * 0.0005, d, 0.25)
        if hit[0] is not None and hit[1].dot(d) > 0:
            found.append((p, vpart.get(v.index, "?"), hit[3]))
    return found


for ob in (vest, pack):
    parts = ob["hcl_partes"].split(",")
    pa = ob.data.attributes["hcl_part"].data
    per = {}
    for p in ob.data.polygons:
        per[parts[pa[p.index].value]] = per.get(parts[pa[p.index].value], 0) + len(p.vertices) - 2
    P(f"{ob.name}: {tris(ob)} triangulos, {len(ob.data.vertices)} vertices")
    for k, v in sorted(per.items(), key=lambda kv: -kv[1]):
        P(f"    {k:28s} {v:5d}")
    f_ = inside_uniform(ob)
    P(f"    vertices sob a superficie do uniforme: {len(f_)}" + (f" (mais fundo {max(x[2] for x in f_) * 1000:.1f} mm)" if f_ else ""))
    groups = {}
    for p, part, dist in f_:
        key = (part, round(p.x, 1), round(p.y, 1), round(p.z - GROUND, 2))
        groups.setdefault(key, []).append(dist)
    for k, ds in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:8]:
        P(f"      {k[0]} perto de x{k[1]:+.1f} y{k[2]:+.1f} h{k[3]:.2f}: {len(ds)} vertices, ate {max(ds) * 1000:.1f} mm")
    me = ob.data
    uvl = me.uv_layers["UVMap"].data
    oob = 0
    dens = {}
    for p in me.polygons:
        us = [uvl[li].uv for li in p.loop_indices]
        oob += sum(1 for u in us if not (-1e-6 <= u.x <= 1 + 1e-6 and -1e-6 <= u.y <= 1 + 1e-6))
        a2 = 0.0
        for k in range(1, len(us) - 1):
            a2 += abs((us[k] - us[0]).cross(us[k + 1] - us[0])) / 2
        d = dens.setdefault(parts[pa[p.index].value], [0.0, 0.0])
        d[0] += a2; d[1] += p.area
    used = sum(a for a, _ in dens.values())
    dd = [math.sqrt(a / b) * 2048 for a, b in dens.values() if b > 1e-7]
    P(f"    UV: cantos fora de 0..1: {oob}; area da textura usada {used * 100:.1f}%; densidade {min(dd):.0f}..{max(dd):.0f} px/m (2048 px)")

# ---------------------------------------------------------------- clay renders for the geometry review
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
    for p in uni.data.polygons:
        p.use_smooth = True
    uni.data.set_sharp_from_angle(angle=math.radians(35))

    def cam(name, loc, target, lens=55):
        c = bpy.data.cameras.new(name)
        c.lens = lens
        o = bpy.data.objects.new(name, c)
        o.location = loc
        o.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        REFC.objects.link(o)
        return o

    T = Vector((0, 0, Z(1.0)))
    shots = [("tres_quartos", cam("CAM_3q", (2.6, -3.6, Z(1.35)), T), (900, 1100)),
             ("tres_quartos_costas", cam("CAM_3qc", (-2.6, 3.6, Z(1.45)), T), (900, 1100)),
             ("detalhe_cartucheira", cam("CAM_cart", (-1.0, 1.4, Z(1.25)), Vector((-0.12, 0.12, Z(1.05))), lens=60), (1000, 900)),
             ("detalhe_baioneta", cam("CAM_bai", (1.6, -0.9, Z(1.10)), Vector((0.15, 0.0, Z(0.95))), lens=60), (1000, 900)),
             ("detalhe_fivela", cam("CAM_fiv", (0.35, -0.9, Z(1.25)), Vector((0.02, -0.12, Z(1.12))), lens=70), (1000, 900)),
             ("detalhe_mochila", cam("CAM_moc", (0.9, 1.3, Z(1.75)), Vector((0.0, 0.25, Z(1.42))), lens=60), (1000, 900))]
    for name, c, (rx, ry) in shots:
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT_IMG, f"equip_producao_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    scene.camera = shots[0][1]

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
P(f"saved {OUT_BLEND}")
open(os.path.join(OUT_IMG, "equip_producao_output.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
