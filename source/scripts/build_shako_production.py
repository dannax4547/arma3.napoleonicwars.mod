# Phase 4 (production mesh) + Phase 6 UVs of the Prussian shako (layout in shako_uv_layout.py); preview materials only.
# Builds ONE object "HCL_Shako_Pruss_LOD0" in character space (same space as Arma 3 Samples A3_headgear_example),
# with closed shells per part, faces of 3-4 vertices only (P3D limit), sharp edges marked at hard corners.
# Usage: blender -b --factory-startup --python build_shako_production.py -- <Test_Character_01 dir> <out.blend> <render_dir> [font] [badge=<json>] [badge_depth=<m>]
#   Default: the approved brass "FWR" monogram. badge=<json> (from trace_badge.py, Eras Mod art authorised by the user)
#   replaces it by an extruded badge (eagle, star) in the same place; its UVs map the badge 1:1 onto the source art.
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod
import shako_fit
import shako_uv_layout as LY

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OPT = dict(a.split("=", 1) for a in args[3:] if "=" in a)
_pos = [a for a in args[3:] if "=" not in a]
FONT = _pos[0] if _pos else r"C:\Windows\Fonts\Gabriola.ttf"
BADGE_JSON = OPT.get("badge")
BADGE_DEPTH = float(OPT.get("badge_depth", "0.0012"))
D_BADGE = 1900.0                         # px per metre for traced badges (fits between the cockade skirt and the buttons)
F = shako_fit.compute(SAMPLES)
S, H = F["S"], F["H"]
ROOT = F["root"]
N = 40                                   # segments around the body
WALL = shako_fit.WALL
SAG = 0.003
print(f"FIT k={F['k']:.4f} H={H:.3f} base={2*F['base_hw']:.3f}x{2*F['base_hd']:.3f} top={2*F['top_hw']:.3f}x{2*F['top_hd']:.3f}")

MAT_NAMES = ["HCL_feltro", "HCL_couro_envernizado", "HCL_couro", "HCL_tecido_branco", "HCL_tecido_preto",
             "HCL_la_amarela", "HCL_latao", "HCL_forro"]
FELT, PATENT, LEATHER, CL_WHITE, CL_BLACK, WOOL_Y, BRASS, LINING = range(8)


def rx(z): return F["base_hw"] + (F["top_hw"] - F["base_hw"]) * z / H
def ry(z): return F["base_hd"] + (F["top_hd"] - F["base_hd"]) * z / H
def P(theta, z, off=0.0):
    return Vector(((rx(z) + off) * math.sin(theta), (ry(z) + off) * math.cos(theta), z))
def out_h(theta, z=0.0):
    return Vector((math.sin(theta) / rx(z), math.cos(theta) / ry(z), 0)).normalized()
def on_wall(theta0, s, z, off):
    local_r = rx(z) if abs(math.sin(theta0)) < 0.5 else ry(z)
    return P(theta0 + s / local_r, z, off)
def th(i):
    return 2 * math.pi * i / N


bm = bmesh.new()
uvl = bm.loops.layers.uv.new("UVMap")
sharp_pairs = []                         # vertex pairs whose edge must be sharp


def U(px, py):
    """layout pixels (top-left origin) -> UV."""
    return (px / LY.TEX, 1.0 - py / LY.TEX)


def face(vs, mat, uvs=None):
    f = bm.faces.new(vs)
    f.material_index = mat
    f.smooth = True
    if uvs is not None:
        for lp, t in zip(f.loops, uvs):
            lp[uvl].uv = U(*t)
    return f


def loft(rings, mats, closed_u=True, closed_v=False, uv=None):
    """rings: list of vertex lists (same length). mats: material per ring-to-ring band (len = bands).
    uv(band, row, i, vert) -> layout pixels; i runs to nc (not wrapped) so seams get their own UVs."""
    nr, nc = len(rings), len(rings[0])
    bands = nr if closed_v else nr - 1
    for j in range(bands):
        a, b = rings[j], rings[(j + 1) % nr]
        for i in range(nc if closed_u else nc - 1):
            i2 = (i + 1) % nc
            uvs = None
            if uv is not None:
                uvs = [uv(j, j, i, a[i]), uv(j, j, i + 1, a[i2]), uv(j, j + 1, i + 1, b[i2]), uv(j, j + 1, i, b[i])]
            face((a[i], a[i2], b[i2], b[i]), mats[j], uvs)


def fan(centre_co, ring, mat, uv=None):
    """uv(i, vert) -> layout pixels; i is None for the centre vertex."""
    c = bm.verts.new(centre_co)
    for i in range(len(ring)):
        i2 = (i + 1) % len(ring)
        uvs = [uv(None, c), uv(i, ring[i]), uv(i + 1, ring[i2])] if uv is not None else None
        face((c, ring[i], ring[i2]), mat, uvs)


_small = [0]
def small_box():
    k = _small[0]; _small[0] += 1
    s = LY.SMALL
    return (s["x0"] + (k % s["cols"]) * s["cell"], s["y0"] + (k // s["cols"]) * s["cell"], s["size"])


def planar_uv(points, centre, box):
    """Planar projection of a (nearly flat) loop of points into a square box (x, y, size)."""
    nrm = Vector()
    for i in range(len(points)):
        a, b = points[i] - centre, points[(i + 1) % len(points)] - centre
        nrm += a.cross(b)
    nrm = nrm.normalized() if nrm.length > 1e-12 else Vector((0, 0, 1))
    ax = (points[0] - centre)
    ax = (ax - nrm * ax.dot(nrm)).normalized() if ax.length > 1e-12 else nrm.orthogonal().normalized()
    ay = nrm.cross(ax)
    ext = max(max(abs((p - centre).dot(ax)), abs((p - centre).dot(ay))) for p in points) or 1.0
    x0, y0, size = box
    half = size / 2 - 1
    return lambda p: (x0 + size / 2 + (p - centre).dot(ax) / ext * half, y0 + size / 2 - (p - centre).dot(ay) / ext * half)


def mark_ring_sharp(ring, closed=True):
    for i in range(len(ring) - (0 if closed else 1)):
        sharp_pairs.append((ring[i], ring[(i + 1) % len(ring)]))


def mark_between_sharp(r1, r2):
    for a, b in zip(r1, r2):
        sharp_pairs.append((a, b))


def cap(ring, mat, centre_co=None, uvf=None):
    """Closes a ring with a fan. UVs: uvf(co) if given, otherwise a planar projection into a small box."""
    co = Vector(centre_co) if centre_co is not None else sum((v.co for v in ring), Vector()) / len(ring)
    if uvf is None:
        uvf = planar_uv([v.co.copy() for v in ring], co, small_box())
    fan(co, ring, mat, uv=lambda i, v: uvf(v.co))
    mark_ring_sharp(ring)


def ring_arc(ring):
    """Cumulative edge length around a closed ring: s[0..n], s[n] = perimeter."""
    s = [0.0]
    for i in range(len(ring)):
        s.append(s[-1] + (ring[(i + 1) % len(ring)].co - ring[i].co).length)
    return s

# ================================================================ 1. body shell (band + felt + binding + crown + lining)
B = S["band"]
rb = 0.0045
prof = [(0.0, -WALL, PATENT, True), (0.0, 0.0018, PATENT, True), (0.0025, 0.0021, PATENT, False),
        (B - 0.0025, 0.0021, PATENT, False), (B - 0.0006, 0.0016, PATENT, False), (B, 0.0004, PATENT, True),
        (B, 0.0, FELT, True), (H * 0.45, 0.0, FELT, False), (H - 0.0115, 0.0, LEATHER, True),
        (H - 0.0115, 0.0012, LEATHER, True), (H - 0.0110, 0.0014, LEATHER, False), (H - rb, 0.0014, LEATHER, False)]
for a in (30, 60, 90):
    al = math.radians(a)
    prof.append((H - rb + rb * math.sin(al), 0.0014 - rb * (1 - math.cos(al)), LEATHER, False))
prof += [(H, -0.010, LEATHER, True), (H - 0.0010, -0.0105, FELT, True)]
rings = [[bm.verts.new(P(th(i), z, o)) for i in range(N)] for z, o, _, _ in prof]
# UV: each ring unrolled by its real perimeter (no stretch from the flare); rows by distance along the profile.
# Seam at the back (theta = 0), where a real shako has its back seam. Islands: band (bands 0-5), felt (6-7), binding (8-15).
arcs = [ring_arc(r) for r in rings]
tprof = [0.0]
for (z0, o0, _, _), (z1, o1, _, _) in zip(prof, prof[1:]):
    tprof.append(tprof[-1] + math.hypot(z1 - z0, o1 - o0))
def body_uv(band, row, i, vert):
    isl, base = (LY.BAND, 0) if band <= 5 else ((LY.FELT, 6) if band <= 7 else (LY.BINDING, 8))
    return (isl["cx"] + (arcs[row][i] - arcs[row][-1] / 2) * LY.D_BIG, isl["ybot"] - (tprof[row] - tprof[base]) * LY.D_BIG)
loft(rings, [p[2] for p in prof[:-1]], uv=body_uv)
for r, p in zip(rings, prof):
    if p[3]:
        mark_ring_sharp(r)
# crown (slightly concave), proportional rings towards the centre; planar UV
outer_top = rings[-1]
crown = [outer_top]
for rho in (0.75, 0.5, 0.25):
    z = H - 0.0010 - SAG * (1 - rho * rho)
    crown.append([bm.verts.new((v.co.x * rho, v.co.y * rho, z)) for v in outer_top])
crown_px = lambda co: (LY.CROWN["cx"] + co.x * LY.D_BIG, LY.CROWN["cy"] - co.y * LY.D_BIG)
loft(crown, [FELT] * 3, uv=lambda b, r, i, v: crown_px(v.co))
fan((0, 0, H - 0.0010 - SAG), crown[-1], FELT, uv=lambda i, v: crown_px(v.co))
# lining: inner wall + ceiling, joined to the bottom rim ring
inner = [rings[0]] + [[bm.verts.new(P(th(i), z, -WALL)) for i in range(N)] for z in (0.08, H - 0.008)]
arcs_in = [ring_arc(r) for r in inner]
t_in = [0.0, 0.08, H - 0.008]
loft(inner, [LINING, LINING], uv=lambda b, r, i, v: (LY.LINING["cx"] + (arcs_in[r][i] - arcs_in[r][-1] / 2) * LY.D_LINING,
                                                     LY.LINING["ybot"] - t_in[r] * LY.D_LINING))
mark_ring_sharp(inner[-1])
ceil = [inner[-1]]
for rho in (0.66, 0.33):
    ceil.append([bm.verts.new((v.co.x * rho, v.co.y * rho, H - 0.008)) for v in inner[-1]])
ceil_px = lambda co: (LY.CEILING["cx"] + co.x * LY.D_LINING, LY.CEILING["cy"] - co.y * LY.D_LINING)
loft(ceil, [LINING, LINING], uv=lambda b, r, i, v: ceil_px(v.co))
fan((0, 0, H - 0.008), ceil[-1], LINING, uv=lambda i, v: ceil_px(v.co))

# ================================================================ 2. visor (closed shell, bound rounded edge)
half_span = math.asin(min(0.99, S["visor_chord"] / 2 / F["base_hw"]))
M, K, VT = 24, 6, 0.0025
sections = []
for m in range(M + 1):
    phi = -half_span + 2 * half_span * m / M
    theta = math.pi + phi
    L = max(0.004, shako_fit.VISOR_LEN * math.cos(phi / half_span * math.pi / 2) ** 0.5)
    oh = out_h(theta, 0.006)
    d = oh * math.cos(shako_fit.VISOR_DROP) - Vector((0, 0, 1)) * math.sin(shako_fit.VISOR_DROP)
    n = oh * math.sin(shako_fit.VISOR_DROP) + Vector((0, 0, 1)) * math.cos(shako_fit.VISOR_DROP)
    # root sits ON the band (band surface off = 0.0021): the lower root edge touches it, nothing is embedded
    root = P(theta, 0.006, 0.0021) + oh * (VT * math.sin(shako_fit.VISOR_DROP) + 0.0001)
    top = [root + d * L * k / K for k in range(K + 1)]
    edge = [top[-1] + d * 0.0006 - n * (VT * 0.15), top[-1] + d * 0.0012 - n * (VT * 0.5),
            top[-1] + d * 0.0006 - n * (VT * 0.85)]
    bottom = [p - n * VT for p in reversed(top)]
    sections.append([bm.verts.new(p) for p in top + edge + bottom])
nc = len(sections[0])
# UV: rows k unrolled along the visor (arc length across m), distance from the root outwards.
# Islands: top surface, bottom surface (mirrored), bound edge strip, root strip.
varc = []                                         # varc[k][m]: cumulative length across m on top row k
for k in range(K + 1):
    s = [0.0]
    for m in range(M):
        s.append(s[-1] + (sections[m + 1][k].co - sections[m][k].co).length)
    varc.append(s)
def visor_px(cls, m, ii):
    if cls == "top" or cls == "bot":
        k = ii if cls == "top" else K - (ii - (K + 4))
        isl = LY.VISOR_TOP if cls == "top" else LY.VISOR_BOTTOM
        d = (sections[m][k].co - sections[m][0].co).length
        return (isl["cx"] + (varc[k][m] - varc[k][-1] / 2) * LY.D_BIG, isl["yroot"] - d * LY.D_BIG)
    if cls == "edge":
        return (LY.VISOR_EDGE["cx"] + (varc[K][m] - varc[K][-1] / 2) * LY.D_BIG, LY.VISOR_EDGE["y0"] + (ii - K) * 2.5)
    return (LY.VISOR_ROOT["cx"] + (varc[0][m] - varc[0][-1] / 2) * LY.D_BIG, LY.VISOR_ROOT["y0"] + (0 if ii == 0 else 4))
for m in range(M):
    a, b = sections[m], sections[m + 1]
    for i in range(nc):
        i2 = (i + 1) % nc
        cls = "top" if i < K else ("edge" if i < K + 4 else ("bot" if i < nc - 1 else "root"))
        face((a[i], b[i], b[i2], a[i2]), PATENT,
             [visor_px(cls, m, i), visor_px(cls, m + 1, i), visor_px(cls, m + 1, i2), visor_px(cls, m, i2)])
cap(sections[0], PATENT)
cap(sections[-1], PATENT)
for sec in sections:                      # root edge corners are sharp
    sharp_pairs.append((sec[0], sec[-1]))
for m in range(M):
    sharp_pairs.append((sections[m][0], sections[m + 1][0]))
    sharp_pairs.append((sections[m][-1], sections[m + 1][-1]))

# ================================================================ 3. cockade (domed, black centre), closed shell
CR = S["cockade_r"]
CZ = min(S["cockade_z"], H - rb - CR - 0.0005)      # keep the cockade below the rounded top edge
SEG = 28
def base_off(z):
    """Clearance above the local surface: felt (0) below the binding, binding (+0.0014) above; ramped, no step."""
    z0, ramp = H - 0.0115, 0.006
    if z >= z0:
        return 0.0018
    if z <= z0 - ramp:
        return 0.0004
    return 0.0004 + 0.0014 * (z - (z0 - ramp)) / ramp
def ck(f, a, extra):
    s, z = CR * f * math.cos(2 * math.pi * a / SEG), CZ + CR * f * math.sin(2 * math.pi * a / SEG)
    return on_wall(math.pi, s, z, base_off(z) + extra)
rhos = [0.2, 0.45, 0.62, 0.8, 1.0]
front = [[bm.verts.new(ck(f, a, 0.0036 - 0.0016 * f * f)) for a in range(SEG)] for f in rhos]
# UV: front = planar (x, z) at high density (pleats); skirt = strip; back = planar at low density
ck_front = lambda co: (LY.COCKADE_FRONT["cx"] + co.x / CR * LY.D_COCKADE, LY.COCKADE_FRONT["cy"] - (co.z - CZ) / CR * LY.D_COCKADE)
ck_back = lambda co: (LY.COCKADE_BACK["cx"] + co.x / CR * LY.COCKADE_BACK["scale"], LY.COCKADE_BACK["cy"] - (co.z - CZ) / CR * LY.COCKADE_BACK["scale"])
fan(on_wall(math.pi, 0, CZ, base_off(CZ) + 0.0036), front[0], CL_BLACK, uv=lambda i, v: ck_front(v.co))
loft(front, [CL_BLACK, CL_WHITE, CL_WHITE, CL_WHITE], uv=lambda b, r, i, v: ck_front(v.co))
mark_ring_sharp(front[1])                 # colour boundary
back = [bm.verts.new(ck(1.0, a, 0.0)) for a in range(SEG)]
sk = LY.COCKADE_SKIRT
loft([front[-1], back], [CL_WHITE], uv=lambda b, r, i, v: (sk["x0"] + i / SEG * sk["w"], sk["y0"] + r * sk["h"]))
mark_ring_sharp(front[-1])
back_rings = [back] + [[bm.verts.new(ck(f, a, 0.0)) for a in range(SEG)] for f in (0.85, 0.7, 0.5, 0.3)]
loft(back_rings, [CL_WHITE] * (len(back_rings) - 1), uv=lambda b, r, i, v: ck_back(v.co))   # fine rings follow the clearance ramp
cap(back_rings[-1], CL_WHITE, on_wall(math.pi, 0, CZ, base_off(CZ)), uvf=ck_back)

# ================================================================ 4. loop (yellow lace) from under the cockade rim, rounded tip
LW = S["loop_w"]
z_top = CZ - CR - 0.0005
z_tip = S["loop_bottom"]
zb = z_tip + LW / 2
rows = [(z_top, 1.0)] + [(z_top + (zb - z_top) * t, 1.0) for t in (0.33, 0.66)] + [(zb, 1.0)]
for a in (35, 65, 85):
    al = math.radians(a)
    rows.append((zb - (LW / 2) * math.sin(al), max(0.08, math.cos(al))))
COLS = 4
loop_secs = []
for z, wf in rows:
    hw = LW / 2 * wf
    frt = [on_wall(math.pi, hw - 2 * hw * i / COLS, z, 0.0014 + 0.0004 * (1 - (2 * i / COLS - 1) ** 2)) for i in range(COLS + 1)]
    bck = [on_wall(math.pi, -hw + 2 * hw * i / COLS, z, 0.0003) for i in range(COLS + 1)]
    loop_secs.append([bm.verts.new(p) for p in frt + bck])
lc = len(loop_secs[0])
# UV: front and back planar (x, z); the two thin sides as strips; z measured down from the top of the loop
def loop_px(cls, v):
    dz = (z_top - v.co.z) * LY.D_LOOP
    if cls == "front":
        return (LY.LOOP_FRONT["cx"] + v.co.x * LY.D_LOOP, LY.LOOP_FRONT["y0"] + dz)
    if cls == "back":
        return (LY.LOOP_BACK["cx"] + v.co.x * LY.D_LOOP, LY.LOOP_BACK["y0"] + dz)
    x = LY.LOOP_SIDE["xa"] if cls == "sideA" else LY.LOOP_SIDE["xb"]
    return (x + (LY.LOOP_SIDE["w"] if v in loop_back_set else 0), LY.LOOP_SIDE["y0"] + dz)
loop_back_set = {v for sec in loop_secs for v in sec[COLS + 1:]}
for j in range(len(loop_secs) - 1):
    a, b = loop_secs[j], loop_secs[j + 1]
    for i in range(lc):
        i2 = (i + 1) % lc
        cls = "front" if i < COLS else ("sideA" if i == COLS else ("back" if i < lc - 1 else "sideB"))
        q = (a[i], a[i2], b[i2], b[i])
        face(q, WOOL_Y, [loop_px(cls, v) for v in q])
cap(loop_secs[0], WOOL_Y)
cap(loop_secs[-1], WOOL_Y)

# ================================================================ 5. side buttons (brass domes), closed shells
def dome(theta0, z0, base_off, R, Hd, segs=16, rings_n=3):
    # UV: planar in the button's own plane; both buttons share the same island (identical parts)
    t_axis = -Vector((math.cos(theta0), -math.sin(theta0), 0)).normalized()   # sign: visible dome not mirrored
    c0 = on_wall(theta0, 0, z0, base_off)
    bpx = lambda co: (LY.BUTTON["cx"] + (co - c0).dot(t_axis) / R * LY.D_BUTTON, LY.BUTTON["cy"] - (co.z - z0) / R * LY.D_BUTTON)
    pts = [[bm.verts.new(on_wall(theta0, R * math.sin(math.pi / 2 * k / rings_n) * math.cos(2 * math.pi * a / segs),
                                 z0 + R * math.sin(math.pi / 2 * k / rings_n) * math.sin(2 * math.pi * a / segs),
                                 base_off + Hd * math.cos(math.pi / 2 * k / rings_n))) for a in range(segs)]
           for k in range(1, rings_n + 1)]
    fan(on_wall(theta0, 0, z0, base_off + Hd), pts[0], BRASS, uv=lambda i, v: bpx(v.co))
    loft(pts, [BRASS] * (rings_n - 1), uv=lambda b, r, i, v: bpx(v.co))
    mark_ring_sharp(pts[-1])
    cap(pts[-1], BRASS, on_wall(theta0, 0, z0, base_off), uvf=bpx)

BTN_TH = math.radians(80)
for sgn in (1, -1):
    dome(math.pi - sgn * BTN_TH, S["button_z"], 0.0026 + 0.0018 + 0.0006, S["button_r"], 0.0025)   # above the strap

# ================================================================ 6. "FWR" cipher: 3D brass letters (self-union of interlaced glyphs)
cipher_info = "not built"
badge_meta = None
try:
    if BADGE_JSON:                       # traced badge: closed polygons in source-image pixels (y down)
        bj = json.load(open(BADGE_JSON))
        cu = bpy.data.curves.new("CipherText", 'CURVE')
        cu.dimensions, cu.fill_mode = '2D', 'BOTH'
        for loop in bj["loops"]:
            sp = cu.splines.new('POLY')
            sp.points.add(len(loop) - 1)
            for p_, (x, y) in zip(sp.points, loop):
                p_.co = (x, -y, 0.0, 1.0)  # curve coordinates: x right, y up (= -image row)
            sp.use_cyclic_u = True
        badge_meta = {"json": BADGE_JSON, "image": bj["image"], "box": bj["box"]}
    else:
        font = bpy.data.fonts.load(FONT)
        cu = bpy.data.curves.new("CipherText", 'FONT')
        cu.body, cu.font, cu.size = "FWR", font, 1.0
        cu.space_character = 0.50        # interlaced letters, closer to the monogram in photo R2
        cu.align_x, cu.align_y = 'CENTER', 'CENTER'
        cu.resolution_u = 2              # coarser curves: polygon budget (letters are ~5 cm)
    tobj = bpy.data.objects.new("CipherText", cu)
    bpy.context.scene.collection.objects.link(tobj)

    def evaluated(ob):
        bpy.context.view_layer.update()
        return bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))

    m0 = evaluated(tobj)
    xs0 = [v.co.x for v in m0.vertices]; ys0 = [v.co.y for v in m0.vertices]
    kf = min(S["cipher_w"] / (max(xs0) - min(xs0)), S["cipher_h"] / (max(ys0) - min(ys0)))
    cu.extrude = (BADGE_DEPTH / 2 if badge_meta else 0.00075) / kf
    tmesh = evaluated(tobj)
    tm_obj = bpy.data.objects.new("CipherMesh", tmesh)
    bpy.context.scene.collection.objects.link(tm_obj)
    dummy_me = bpy.data.meshes.new("dummy")
    dbm = bmesh.new(); bmesh.ops.create_cube(dbm, size=0.01); dbm.to_mesh(dummy_me); dbm.free()
    dummy = bpy.data.objects.new("dummy", dummy_me)
    dummy.location = (1000, 1000, 1000)
    bpy.context.scene.collection.objects.link(dummy)
    mod = tm_obj.modifiers.new("union", 'BOOLEAN')
    mod.operation, mod.object = 'UNION', dummy
    try:
        mod.solver = 'EXACT'
        mod.use_self = True
    except Exception as e:
        print("BOOLEAN option:", e)
    if badge_meta:
        # traced badge: one outline extruded is already a closed solid; the boolean/dissolve clean-up meant for the
        # interlaced letters would break it (curve units here are image pixels)
        ubm = bmesh.new(); ubm.from_mesh(tmesh)
        bmesh.ops.remove_doubles(ubm, verts=ubm.verts[:], dist=1e-4)
        bmesh.ops.triangulate(ubm, faces=[f for f in ubm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
        # the fill makes long flat triangles: once wrapped on the curved front they would cut ~7 mm into the wall,
        # so split every edge longer than 12 mm (chord sag on the front: ~0.17 mm) until the badge follows the curvature
        max_len = 0.012 / kf
        for _ in range(8):
            long_e = [e for e in ubm.edges if e.calc_length() > max_len]
            if not long_e:
                break
            bmesh.ops.subdivide_edges(ubm, edges=long_e, cuts=1, use_grid_fill=True)
            bmesh.ops.triangulate(ubm, faces=[f for f in ubm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
        bmesh.ops.recalc_face_normals(ubm, faces=ubm.faces[:])
    else:
        umesh = evaluated(tm_obj)
        # drop the far-away dummy cube from the result
        ubm = bmesh.new(); ubm.from_mesh(umesh)
        bmesh.ops.delete(ubm, geom=[v for v in ubm.verts if v.co.length > 100], context='VERTS')
        # clean the boolean result: weld coincident points, remove degenerate slivers, merge coplanar faces, re-triangulate
        bmesh.ops.remove_doubles(ubm, verts=ubm.verts[:], dist=1e-5)
        bmesh.ops.dissolve_degenerate(ubm, dist=1e-5, edges=ubm.edges[:])
        bmesh.ops.dissolve_limit(ubm, angle_limit=math.radians(1.0), verts=ubm.verts[:], edges=ubm.edges[:])
        bmesh.ops.triangulate(ubm, faces=[f for f in ubm.faces if len(f.verts) > 4], quad_method='BEAUTY', ngon_method='BEAUTY')
    nonman = sum(1 for e in ubm.edges if not e.is_manifold)
    xs = [v.co.x for v in ubm.verts]; ys = [v.co.y for v in ubm.verts]; zs = [v.co.z for v in ubm.verts]
    cx_, cy_, zmin = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, min(zs)
    vmap, lxy = {}, {}
    if badge_meta:
        # tall badges cross the felt band, whose single 6.8 cm quads bow ~1 mm out of the ideal surface once
        # triangulated: rest the badge on the REAL mesh (ray from outside), 0.4 mm clear, same lift front and back
        from mathutils.bvhtree import BVHTree
        wall_tree = BVHTree.FromBMesh(bm)
        lift_cache = {}

        def lift(lx, ly):
            k = (round(lx, 6), round(ly, 6))
            if k not in lift_cache:
                z = S["cipher_z"] + ly
                q = on_wall(math.pi, -lx, z, 0.0006)
                n = (q - Vector((0, 0, z)))
                n.z = 0
                n.normalize()
                hit = wall_tree.ray_cast(q + n * 0.03, -n, 0.06)
                d = (hit[0] - q).dot(n) if hit[0] is not None else -1.0
                lift_cache[k] = max(0.0, d + 0.0004)
            return lift_cache[k]
    for v in ubm.verts:
        lx, ly, lz = (v.co.x - cx_) * kf, (v.co.y - cy_) * kf, (v.co.z - zmin) * kf
        extra = lift(lx, ly) if badge_meta else 0.0
        vmap[v.index] = bm.verts.new(on_wall(math.pi, -lx, S["cipher_z"] + ly, 0.0006 + lz + extra))
        lxy[vmap[v.index]] = (lx, ly)
    ubm.verts.index_update()
    nf = 0
    cz = S["cipher_z"]
    cipher_px = lambda co: (LY.CIPHER["cx"] + co.x * LY.D_CIPHER, LY.CIPHER["cy"] - (co.z - cz) * LY.D_CIPHER)  # planar front
    # traced badge: UV from the flat (pre-wrap) coordinates, so the texture can be sampled 1:1 from the source art
    badge_px = lambda v: (LY.CIPHER["cx"] + lxy[v][0] * D_BADGE, LY.CIPHER["cy"] - lxy[v][1] * D_BADGE)
    for f in ubm.faces:
        try:
            vs = [vmap[v.index] for v in f.verts]
            face(vs, BRASS, [badge_px(v) for v in vs] if badge_meta else [cipher_px(v.co) for v in vs])
            nf += 1
        except ValueError:
            pass
    if badge_meta:
        badge_meta.update(kf=kf, cx=cx_, cy=cy_, uv_cx=LY.CIPHER["cx"], uv_cy=LY.CIPHER["cy"], density=D_BADGE,
                          size=[(max(xs) - min(xs)) * kf, (max(ys) - min(ys)) * kf])
    src = os.path.basename(BADGE_JSON) if badge_meta else f"font={os.path.basename(FONT)}"
    cipher_info = f"{src} faces={nf} non-manifold-edges-after-union={nonman} size=({(max(xs)-min(xs))*kf:.3f} x {(max(ys)-min(ys))*kf:.3f}) m"
    ubm.free()
    for ob in (tobj, tm_obj, dummy):
        bpy.data.objects.remove(ob, do_unlink=True)
except Exception as e:
    cipher_info = f"FAILED: {e}"
print("CIPHER", cipher_info)

# ================================================================ 7. chinstrap under the chin (fitted to an ESTIMATED head; validate in game)
ROOT_INV = ROOT.inverted()
HEAD_C = Vector((0.0, F["head_cy"], (F["z_head_top"] + 0.57) / 2))
HEAD_S = Vector((F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004))
BTN_Z = S["button_z"]

def catmull(pts, samples):
    ext = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    out, segs = [], len(pts) - 1
    for s in range(samples + 1):
        x = s / samples * segs
        i = min(int(x), segs - 1)
        t = x - i
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out

def side_pts(sgn):
    th_b = math.pi - sgn * BTN_TH
    b0 = ROOT @ P(th_b, BTN_Z, 0.0026)          # 0.5 mm clearance over the band
    b1 = ROOT @ P(th_b, 0.0, 0.0026)
    q = [Vector((0.096 * sgn, -0.025, 0.700)), Vector((0.085 * sgn, -0.030, 0.660)),
         Vector((0.068 * sgn, -0.040, 0.625)), Vector((0.035 * sgn, -0.068, 0.600))]
    return [b0, b1] + q

path_w = side_pts(1) + [Vector((0.0, -0.080, 0.592))] + list(reversed(side_pts(-1)))
pw = catmull(path_w, 70)

def strap_normal(p_world, p_local):
    if p_local.z > -0.004:                                   # still on the shako band
        th_ = math.atan2(p_local.x / rx(0), p_local.y / ry(0))
        return (ROOT.to_3x3() @ out_h(th_)).normalized()
    q = p_world - HEAD_C
    nh = Vector((q.x / HEAD_S.x ** 2, q.y / HEAD_S.y ** 2, q.z / HEAD_S.z ** 2)).normalized()
    return nh

SW, ST = 0.012, 0.0018
secs = []
for i, p in enumerate(pw):
    tng = (pw[min(i + 1, len(pw) - 1)] - pw[max(i - 1, 0)]).normalized()
    n = strap_normal(p, ROOT_INV @ p)
    b = tng.cross(n).normalized()
    n = b.cross(tng).normalized()
    ring_w = [p - b * SW / 2, p + b * SW / 2, p + b * SW / 2 + n * ST, p - b * SW / 2 + n * ST]
    secs.append([bm.verts.new(ROOT_INV @ c) for c in ring_w])
# UV: four strips (outer face, inner face, two sides), u = length along the strap
cum = [0.0]
for j in range(len(pw) - 1):
    cum.append(cum[-1] + (pw[j + 1] - pw[j]).length)
STRIP = [(LY.STRAP_INNER, (0, SW)), (LY.STRAP_SIDE_R, (0, ST)), (LY.STRAP_OUTER, (0, SW)), (LY.STRAP_SIDE_L, (0, ST))]
def strap_px(face_i, j, corner):
    isl, (w0, w1) = STRIP[face_i]
    across = w0 if corner == face_i else w1          # first corner of the face edge -> 0, second -> width
    return (isl["x0"] + cum[j] * LY.D_BIG, isl["y0"] + across * LY.D_BIG)
for j in range(len(secs) - 1):
    a, b_ = secs[j], secs[j + 1]
    for i in range(4):
        i2 = (i + 1) % 4
        face((a[i], a[i2], b_[i2], b_[i]), LEATHER,
             [strap_px(i, j, i), strap_px(i, j, i2), strap_px(i, j + 1, i2), strap_px(i, j + 1, i)])
        sharp_pairs.append((a[i], b_[i]))
cap(secs[0], LEATHER)
cap(secs[-1], LEATHER)

# ================================================================ finish: triangulate n-gons (>4), normals, sharp edges, transform to character space
bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
for a, b_ in sharp_pairs:
    e = bm.edges.get((a, b_))
    if e is not None:
        e.smooth = False

# UV orientation: find UV islands (faces joined across edges whose UVs match) and mirror any island whose
# UVs run opposite to the face winding, so normal-map tangents are not flipped. Mirroring stays inside the island box.
bm.faces.ensure_lookup_table()
parent = list(range(len(bm.faces)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
for e in bm.edges:
    lf = e.link_faces
    if len(lf) != 2:
        continue
    same = True
    for v in e.verts:
        l1 = next(l for l in lf[0].loops if l.vert == v)
        l2 = next(l for l in lf[1].loops if l.vert == v)
        if (l1[uvl].uv - l2[uvl].uv).length > 1e-7:
            same = False
            break
    if same:
        parent[find(lf[0].index)] = find(lf[1].index)
groups = {}
for f in bm.faces:
    groups.setdefault(find(f.index), []).append(f)
def signed_uv_area(f):
    p = [l[uvl].uv for l in f.loops]
    return 0.5 * sum(p[i].x * p[(i + 1) % len(p)].y - p[(i + 1) % len(p)].x * p[i].y for i in range(len(p)))
mirrored, mixed = 0, 0
for faces in groups.values():
    areas = [signed_uv_area(f) for f in faces]
    if sum(areas) < 0:
        us = [l[uvl].uv.x for f in faces for l in f.loops]
        u0, u1 = min(us), max(us)
        for f in faces:
            for l in f.loops:
                l[uvl].uv.x = u0 + u1 - l[uvl].uv.x
        mirrored += 1
        areas = [-a for a in areas]
    if any(a < 0 for a in areas) and any(a > 0 for a in areas):
        mixed += 1
print(f"UVFIX uv_islands={len(groups)} mirrored_back={mirrored} islands_with_mixed_orientation={mixed}")
bm.transform(ROOT)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
me = bpy.data.meshes.new("HCL_Shako_Pruss_LOD0")
bm.to_mesh(me)
bm.free()
shako = bpy.data.objects.new("HCL_Shako_Pruss_LOD0", me)
shako["hcl_distintivo"] = json.dumps(badge_meta) if badge_meta else "FWR (fonte Gabriola)"
col_main = bpy.data.collections.new("HCL_Shako_Producao")
col_ref = bpy.data.collections.new("REF_Arma3Samples")
scene.collection.children.link(col_main)
scene.collection.children.link(col_ref)
col_main.objects.link(shako)

PREVIEW = {  # preview materials only (not game materials); colour, roughness, metallic
    "HCL_feltro": ((0.022, 0.024, 0.030), 0.85, 0.0), "HCL_couro_envernizado": ((0.008, 0.008, 0.010), 0.10, 0.0),
    "HCL_couro": ((0.014, 0.013, 0.013), 0.45, 0.0), "HCL_tecido_branco": ((0.80, 0.79, 0.76), 0.80, 0.0),
    "HCL_tecido_preto": ((0.02, 0.02, 0.022), 0.80, 0.0), "HCL_la_amarela": ((0.80, 0.58, 0.12), 0.80, 0.0),
    "HCL_latao": ((0.80, 0.60, 0.25), 0.30, 1.0), "HCL_forro": ((0.10, 0.08, 0.06), 0.90, 0.0)}
def mk(name, colour, rough, metal, alpha=1.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*colour, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Alpha"].default_value = alpha
    return m
for nm in MAT_NAMES:
    me.materials.append(mk(nm, *PREVIEW[nm]))

tri = sum(len(p.vertices) - 2 for p in me.polygons)
quads_n = sum(1 for p in me.polygons if len(p.vertices) == 4)
tris_n = sum(1 for p in me.polygons if len(p.vertices) == 3)
maxv = max(len(p.vertices) for p in me.polygons)
print(f"STATS verts={len(me.vertices)} faces={len(me.polygons)} (quads={quads_n}, tris={tris_n}, max_verts_per_face={maxv}) triangles={tri} sharp_edges={sum(1 for e in me.edges if e.use_edge_sharp)}")
per_mat = {}
for p in me.polygons:
    per_mat[MAT_NAMES[p.material_index]] = per_mat.get(MAT_NAMES[p.material_index], 0) + len(p.vertices) - 2
print("STATS_BY_MATERIAL " + ", ".join(f"{k}={v}" for k, v in per_mat.items()))

# ---------------------------------------------------------------- references for presentation (not exported)
def mesh_from_lod(name, lod):
    from p3d_mlod import to_blender
    pts = [to_blender(p) for p in lod["points"]]
    proxy = set()
    for sname, blob in lod["selections"].items():
        if sname.lower().startswith("proxy:"):
            proxy.update(i for i, b_ in enumerate(blob) if b_)
    faces = [f[::-1] for f in lod["faces"] if not any(i in proxy for i in f)]
    used = sorted({i for f in faces for i in f})
    remap = {old: new for new, old in enumerate(used)}
    m_ = bpy.data.meshes.new(name)
    m_.from_pydata([pts[i] for i in used], [], [[remap[i] for i in f] for f in faces])
    for p in m_.polygons:
        p.use_smooth = True
    return m_
body = bpy.data.objects.new("REF_corpo_A3_character_example", mesh_from_lod("REF_body", read_mlod(os.path.join(SAMPLES, "A3_character_example.p3d"))[0]))
col_ref.objects.link(body)
body.data.materials.append(mk("REF_pele", (0.55, 0.50, 0.46), 0.6, 0.0))
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_head_approx"); hb.to_mesh(hme); hb.free()
for p in hme.polygons:
    p.use_smooth = True
head = bpy.data.objects.new("REF_cabeca_APROXIMADA_nao_oficial", hme)
head.scale, head.location = HEAD_S, HEAD_C
col_ref.objects.link(head)
head.data.materials.append(mk("REF_cabeca", (0.66, 0.58, 0.52), 0.6, 0.0))

# wireframe overlay object (presentation of topology only)
wire = bpy.data.objects.new("REF_wireframe_overlay", me)
col_ref.objects.link(wire)
wmod = wire.modifiers.new("wire", 'WIREFRAME')
wmod.thickness, wmod.use_replace = 0.00045, True
wire.data = me.copy()
wire.data.materials.clear()
wire.data.materials.append(mk("REF_wire", (0.95, 0.95, 0.95), 0.5, 0.0))
wire.hide_render = True

# ---------------------------------------------------------------- render
target = bpy.data.objects.new("CamTarget", None); col_ref.objects.link(target)
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); col_ref.objects.link(cam)
tc = cam.constraints.new('TRACK_TO'); tc.target, tc.track_axis, tc.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
scene.camera = cam
for nm, loc, e in (("Key", (-1.2, -1.5, 2.2), 3.5), ("Fill", (1.5, -0.8, 1.0), 1.3), ("Rim", (0.5, 1.6, 1.8), 2.8)):
    ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(6)
    lo = bpy.data.objects.new(nm, ld); lo.location = loc; col_ref.objects.link(lo)
    c = lo.constraints.new('TRACK_TO'); c.target, c.track_axis, c.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
world = bpy.data.worlds.new("W")
try:
    world.use_nodes = True
except AttributeError:
    pass
next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND').inputs["Color"].default_value = (0.62, 0.64, 0.67, 1)
scene.world = world
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
try:
    scene.cycles.use_denoising = True
except Exception:
    pass
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
os.makedirs(RENDER_DIR, exist_ok=True)

def render(name, az, el, dist, tgt, res=800, ortho=None, lens=85):
    target.location = tgt
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(tgt) + dist * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    cam_d.type = 'ORTHO' if ortho else 'PERSP'
    if ortho:
        cam_d.ortho_scale = ortho
    cam_d.lens = lens
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"producao_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("OK render", scene.render.filepath)
    return scene.render.filepath

centre = ROOT @ Vector((0, 0, H * 0.40))
views = [render("frente_3-4", 35, 10, 1.25, centre - Vector((0, 0, 0.04))), render("frente", 0, 3, 1.25, centre - Vector((0, 0, 0.04))),
         render("lado", 90, 3, 1.25, centre - Vector((0, 0, 0.04))), render("costas_3-4", 150, 15, 1.25, centre - Vector((0, 0, 0.04)))]
render("detalhe_frente", 15, 6, 0.55, ROOT @ Vector((0, -F["base_hd"], 0.10)), res=900)
head.hide_render = body.hide_render = True
render("sem_cabeca_3-4", 40, 25, 1.0, centre, res=900)
wire.hide_render = False
render("topologia_3-4", 40, 25, 1.0, centre, res=1000)
wire.hide_render = True
head.hide_render = body.hide_render = False

def load_rgb(pth):
    im = bpy.data.images.load(pth, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    return a.reshape(h, w, 4)
t = [load_rgb(p_) for p_ in views]
sheet = np.concatenate([np.concatenate([t[2], t[3]], axis=1), np.concatenate([t[0], t[1]], axis=1)], axis=0)
img = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
img.pixels.foreach_set(sheet.ravel())
img.save_render(os.path.join(RENDER_DIR, "producao_vistas.png"), scene=scene)
print("OK sheet")

os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("OK blend", OUT_BLEND)
