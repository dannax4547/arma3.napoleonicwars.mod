# Blender headless: builds the Prussian shako v3, following the user's reference photo
# (tall flared body, white twill top band, leather top binding, white/black pompom on a stem,
# brass "FWR" cipher, patent-leather bottom band and visor, side buttons and a chinstrap under the chin).
# Usage: blender -b --factory-startup --python build_shako_v3.py -- <tex_dir> <out.blend> <out.fbx> <render_dir> [font.ttf]
#
# Conventions: metres, +Z up, front = -Y (Blender default). Origin = centre of the bottom opening.
# Proportions were estimated from the reference photo, scaled so the bottom opening fits a ~0.18 m wide head.
# The chinstrap is fitted to the preview mannequin, NOT to the real Arma 3 head: it must be checked in Object Builder.
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
TEX_DIR, OUT_BLEND, OUT_FBX, RENDER_DIR = args[:4]
FONT = args[4] if len(args) > 4 else r"C:\Windows\Fonts\Gabriola.ttf"
NAME = "HCL_Shako_Pruss_v3"
TEX_CO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_co.png")
TEX_NO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_nohq.png")
TEX_RO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_rough_preview.png")

# ---------------------------------------------------------------- dimensions (metres)
H = 0.190
RXB, RYB = 0.091, 0.103          # bottom half-width / half-depth
RXT, RYT = 0.124, 0.134          # top: strongly flared, as in the photo
PB, PB_OFF = 0.020, 0.0012       # patent-leather bottom band
WB0, WB1, WB_OFF = 0.128, 0.176, 0.0009   # white twill band
BEV, SAG, WALL = 0.007, 0.004, 0.004
N = 80

VISOR_SPAN, VISOR_LEN, VISOR_DROP = math.radians(85), 0.065, math.radians(30)
VISOR_Z, VISOR_T = 0.006, 0.0025

POM_R = (0.040, 0.026, 0.040)    # pompom half-sizes (x, y, z)
POM_Z = H + 0.047

CIPHER_Z, CIPHER_W, CIPHER_H = 0.076, 0.082, 0.052

BOSS_DTH, BOSS_Z, BOSS_R, BOSS_H = 1.40, 0.011, 0.007, 0.0025

HEAD_C, HEAD_S = Vector((0, 0.004, -0.046)), Vector((0.078, 0.088, 0.118))   # preview mannequin

TS = 1024.0
def uv(px, py):
    return (px / TS, 1.0 - py / TS)

MAT_FELT, MAT_LEATHER, MAT_CLOTH, MAT_METAL = range(4)


def rx(z): return RXB + (RXT - RXB) * z / H
def ry(z): return RYB + (RYT - RYB) * z / H


def wob(theta, z):
    return (0.0006 * math.sin(3 * theta + 1.3) + 0.0004 * math.sin(5 * theta + 0.4 + 12 * z)
            + 0.0003 * math.sin(2 * theta + 2.1) * (z / H))


def P(theta, z, off=0.0):
    d = off + wob(theta, z)
    return Vector(((rx(z) + d) * math.sin(theta), (ry(z) + d) * math.cos(theta), z))


def outward(theta, z=0.1):
    return Vector((math.sin(theta) / rx(z), math.cos(theta) / ry(z), 0)).normalized()


bm = bmesh.new()
uvl = bm.loops.layers.uv.new("UVMap")


def face(verts, uvs, mat, expect, smooth=True):
    if len(verts) == 3:
        n = (verts[1].co - verts[0].co).cross(verts[2].co - verts[0].co)
    else:
        n = (verts[2].co - verts[0].co).cross(verts[3].co - verts[1].co)
    if n.dot(expect) < 0:
        verts, uvs = verts[::-1], uvs[::-1]
    f = bm.faces.new(verts)
    f.material_index = mat
    f.smooth = smooth
    for lp, t in zip(f.loops, uvs):
        lp[uvl].uv = t
    return f


def centroid(vs):
    return sum((v.co for v in vs), Vector()) / len(vs)


def th(i):
    return 2 * math.pi * i / N


def ring_strip(rows, uv_fn, mat, expect_fn):
    """rows: list of vertex rings (each N verts). uv_fn(i, j) -> uv for column i (0..N) of row j."""
    for j in range(len(rows) - 1):
        for i in range(N):
            i2 = (i + 1) % N
            face([rows[j][i], rows[j][i2], rows[j + 1][i2], rows[j + 1][i]],
                 [uv_fn(i, j), uv_fn(i + 1, j), uv_fn(i + 1, j + 1), uv_fn(i, j + 1)], mat, expect_fn(i, j))


# ---------------------------------------------------------------- felt wall, leather binding over the rounded top edge
prof = [(PB - 0.003, 0.0), (0.050, 0.0), (0.080, 0.0), (0.105, 0.0), (WB0, 0.0), (WB1, 0.0), (H - BEV, 0.0)]
for a in (22.5, 45.0, 67.5, 90.0):
    al = math.radians(a)
    prof.append((H - BEV + BEV * math.sin(al), -BEV * (1 - math.cos(al))))
arc = [0.0]
for (z0, o0), (z1, o1) in zip(prof, prof[1:]):
    arc.append(arc[-1] + math.hypot(z1 - z0, o1 - o0))
J_WB0, J_WB1 = 4, 5
wall = [[bm.verts.new(P(th(i), z, o)) for i in range(N)] for z, o in prof]

def wall_py(j):
    if j <= J_WB0:                                    # felt: y 172 (bottom) -> 0 (white band start)
        return (arc[J_WB0] - arc[j]) / arc[J_WB0] * 172
    if j == J_WB1 and False:
        return 0
    return 334 - (arc[j] - arc[J_WB1]) / (arc[-1] - arc[J_WB1]) * 44   # leather binding uses the band strip

for j in range(len(prof) - 1):
    mat = MAT_FELT if j < J_WB1 else MAT_LEATHER
    for i in range(N):
        i2 = (i + 1) % N
        q = [wall[j][i], wall[j][i2], wall[j + 1][i2], wall[j + 1][i]]
        if j == J_WB0:                                # hidden under the white band
            ys = (0.0, 0.0)
        else:
            ys = (wall_py(j), wall_py(j + 1))
        face(q, [uv(TS * i / N, ys[0]), uv(TS * (i + 1) / N, ys[0]), uv(TS * (i + 1) / N, ys[1]), uv(TS * i / N, ys[1])],
             mat, outward(th(i + 0.5), prof[j][0]) + Vector((0, 0, 2.0 if j >= 6 else 0.0)))

# crown (patent leather)
rhos = [1.0, 0.75, 0.5, 0.25]
rings = [wall[-1]]
for rho in rhos[1:]:
    z = H - SAG * (1 - rho * rho)
    rings.append([bm.verts.new(((rx(H) - BEV) * rho * math.sin(th(i)), (ry(H) - BEV) * rho * math.cos(th(i)), z)) for i in range(N)])
centre = bm.verts.new((0, 0, H - SAG))
def crown_uv(rho, i):
    return uv(128 + 117 * rho * math.sin(th(i)), 480 - 117 * rho * math.cos(th(i)))
ring_strip(rings, lambda i, j: crown_uv(rhos[j], i), MAT_LEATHER, lambda i, j: Vector((0, 0, 1)))
for i in range(N):
    face([centre, rings[-1][i], rings[-1][(i + 1) % N]], [uv(128, 480), crown_uv(rhos[-1], i), crown_uv(rhos[-1], i + 1)],
         MAT_LEATHER, Vector((0, 0, 1)))

# ---------------------------------------------------------------- white twill band (raised) + lips
wz = [WB0, (WB0 + WB1) / 2, WB1]
wb = [[bm.verts.new(P(th(i), z, WB_OFF)) for i in range(N)] for z in wz]
def wb_py(z):
    return 666 - (z - WB0) / (WB1 - WB0) * 52
ring_strip(wb, lambda i, j: uv(768 * i / N, wb_py(wz[j])), MAT_CLOTH, lambda i, j: outward(th(i + 0.5), wz[j]))
for z, ex, py in ((WB0, -1, 667), (WB1, 1, 613)):
    o = [bm.verts.new(P(th(i), z, WB_OFF)) for i in range(N)]
    n_ = [bm.verts.new(P(th(i), z, -0.0004)) for i in range(N)]
    ring_strip([o, n_], lambda i, j, py=py: uv(768 * i / N, py), MAT_CLOTH, lambda i, j, ex=ex: Vector((0, 0, ex)))

# ---------------------------------------------------------------- patent-leather bottom band + lip + bottom rim
bz = [0.0, PB / 2, PB]
band = [[bm.verts.new(P(th(i), z, PB_OFF)) for i in range(N)] for z in bz]
ring_strip(band, lambda i, j: uv(TS * i / N, 290 + (PB - bz[j]) / PB * 44), MAT_LEATHER, lambda i, j: outward(th(i + 0.5), 0.01))
lo = [bm.verts.new(P(th(i), PB, PB_OFF)) for i in range(N)]
li = [bm.verts.new(P(th(i), PB, -0.0005)) for i in range(N)]
ring_strip([lo, li], lambda i, j: uv(TS * i / N, 289 + j), MAT_LEATHER, lambda i, j: Vector((0, 0, 1)))
ro = [bm.verts.new(P(th(i), 0.0, PB_OFF)) for i in range(N)]
ri = [bm.verts.new(P(th(i), 0.0, -WALL)) for i in range(N)]
ring_strip([ro, ri], lambda i, j: uv(260 + 248 * i / N, 600 + 3 * j), MAT_FELT, lambda i, j: Vector((0, 0, -1)))

# inside
DX, DY = 256, 352
zin = [0.0, 0.06, 0.12, H - WALL - SAG]
inner = [[bm.verts.new(P(th(i), z, -WALL)) for i in range(N)] for z in zin]
ring_strip(inner, lambda i, j: uv(DX + 256 * i / N, DY + 256 * (1 - zin[j] / H)), MAT_FELT, lambda i, j: -outward(th(i + 0.5), zin[j]))
cc = bm.verts.new((0, 0, H - WALL - SAG))
for i in range(N):
    face([cc, inner[-1][i], inner[-1][(i + 1) % N]], [uv(DX + 128, DY + 128), uv(DX + 20, DY + 20), uv(DX + 40, DY + 20)],
         MAT_FELT, Vector((0, 0, -1)))

# ---------------------------------------------------------------- visor (patent leather, steep, squarish front)
M, K = 36, 7
def visor_point(m, t):
    phi = -VISOR_SPAN + 2 * VISOR_SPAN * m / M
    L = max(0.003, VISOR_LEN * math.cos(phi / VISOR_SPAN * math.pi / 2) ** 0.35)
    theta = math.pi + phi
    e = t * L
    base = P(theta, VISOR_Z, -0.002)
    z = -e * math.tan(VISOR_DROP) - 0.012 * t * t * (L / VISOR_LEN)
    return base + outward(theta, VISOR_Z) * e + Vector((0, 0, z)), theta
vt = [[bm.verts.new(visor_point(m, k / K)[0]) for m in range(M + 1)] for k in range(K + 1)]
vb = [[bm.verts.new(visor_point(m, k / K)[0] - Vector((0, 0, VISOR_T))) for m in range(M + 1)] for k in range(K + 1)]
vmid = [bm.verts.new(visor_point(m, 1.0)[0] + outward(visor_point(m, 1.0)[1], VISOR_Z) * 0.0012 - Vector((0, 0, VISOR_T / 2)))
        for m in range(M + 1)]
VX, VY = 512, 352
def vuv(m, py):
    return uv(VX + 256 * m / M, py)
for k in range(K):
    for m in range(M):
        y0, y1 = VY + 228 * k / K, VY + 228 * (k + 1) / K
        face([vt[k][m], vt[k][m + 1], vt[k + 1][m + 1], vt[k + 1][m]], [vuv(m, y0), vuv(m + 1, y0), vuv(m + 1, y1), vuv(m, y1)],
             MAT_LEATHER, Vector((0, 0, 1)))
        face([vb[k][m], vb[k][m + 1], vb[k + 1][m + 1], vb[k + 1][m]], [vuv(m, y0), vuv(m + 1, y0), vuv(m + 1, y1), vuv(m, y1)],
             MAT_LEATHER, Vector((0, 0, -1)))
for m in range(M):
    d = outward(math.pi - VISOR_SPAN + 2 * VISOR_SPAN * (m + 0.5) / M, VISOR_Z)
    face([vt[K][m], vt[K][m + 1], vmid[m + 1], vmid[m]], [vuv(m, 584), vuv(m + 1, 584), vuv(m + 1, 594), vuv(m, 594)],
         MAT_LEATHER, d + Vector((0, 0, 0.5)))
    face([vmid[m], vmid[m + 1], vb[K][m + 1], vb[K][m]], [vuv(m, 594), vuv(m + 1, 594), vuv(m + 1, 604), vuv(m, 604)],
         MAT_LEATHER, d - Vector((0, 0, 0.5)))
for m, sgn in ((0, -1), (M, 1)):
    t_ang = math.pi + sgn * VISOR_SPAN
    tang = Vector((math.cos(t_ang) / RXB, -math.sin(t_ang) / RYB, 0)).normalized() * sgn
    for k in range(K):
        face([vt[k][m], vt[k + 1][m], vb[k + 1][m], vb[k][m]], [vuv(0, 586), vuv(1, 586), vuv(1, 600), vuv(0, 600)],
             MAT_LEATHER, tang)

# ---------------------------------------------------------------- helpers for details placed on the wall
def on_wall(theta0, s, z, off):
    local_r = rx(z) if abs(math.sin(theta0)) < 0.5 else ry(z)
    return P(theta0 + s / local_r, z, off)


def dome(theta0, z0, base_off, R, Hd, uc, mat, segs=20, rings_=4):
    pts = [[bm.verts.new(on_wall(theta0, 0, z0, base_off + Hd))]]
    for k in range(1, rings_ + 1):
        b = math.pi / 2 * k / rings_
        rho, off = R * math.sin(b), base_off + Hd * math.cos(b)
        pts.append([bm.verts.new(on_wall(theta0, rho * math.cos(2 * math.pi * a / segs), z0 + rho * math.sin(2 * math.pi * a / segs), off))
                    for a in range(segs)])
    inner_pt = on_wall(theta0, 0, z0, base_off - 0.01)
    def duv(k, a):
        r = 28 * math.sin(math.pi / 2 * k / rings_)
        t = 2 * math.pi * a / segs
        return uv(uc[0] - r * math.cos(t), uc[1] - r * math.sin(t))
    for a in range(segs):
        a2 = (a + 1) % segs
        q = [pts[0][0], pts[1][a], pts[1][a2]]
        face(q, [duv(0, 0), duv(1, a), duv(1, a + 1)], mat, centroid(q) - inner_pt)
        for k in range(1, rings_):
            q = [pts[k][a], pts[k][a2], pts[k + 1][a2], pts[k + 1][a]]
            face(q, [duv(k, a), duv(k, a + 1), duv(k + 1, a + 1), duv(k + 1, a)], mat, centroid(q) - inner_pt)


def box(center, ax, ay, az, hx, hy, hz, uvc, mat):
    """Oriented box (axes ax, ay, az unit vectors; half-sizes hx, hy, hz)."""
    vs = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                vs[(sx, sy, sz)] = bm.verts.new(center + ax * (sx * hx) + ay * (sy * hy) + az * (sz * hz))
    quads = [((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)), ((-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)),
             ((-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)), ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)),
             ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)), ((-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1))]
    for qd in quads:
        q = [vs[k] for k in qd]
        face(q, [uv(uvc[0], uvc[1]), uv(uvc[0] + 6, uvc[1]), uv(uvc[0] + 6, uvc[1] + 6), uv(uvc[0], uvc[1] + 6)],
             mat, centroid(q) - center, smooth=False)


# ---------------------------------------------------------------- pompom (fluffy ellipsoid) + stem
PC = Vector((0, -(RYT - 0.012), POM_Z))
rng = np.random.default_rng(7)
UU, VV = 48, 24
ph1, ph2, ph3 = rng.uniform(0, 6.28, 3)
def pom_vert(lat, lon):
    lx, ly, lz = POM_R[0] * math.cos(lat) * math.sin(lon), POM_R[1] * math.cos(lat) * math.cos(lon), POM_R[2] * math.sin(lat)
    fl = 1 + 0.05 * math.sin(7 * lon + ph1) * math.sin(5 * lat + ph2) + 0.03 * math.sin(11 * lon + 3 * lat + ph3) \
         + rng.uniform(-0.025, 0.025)
    return PC + Vector((lx, ly, lz)) * fl, (96 + 90 * lx / POM_R[0], 776 - 90 * lz / POM_R[2])
grid, guv = [], []
for v in range(1, VV):
    lat = -math.pi / 2 + math.pi * v / VV
    row, rowuv = [], []
    for u in range(UU):
        p, t = pom_vert(lat, 2 * math.pi * u / UU)
        row.append(bm.verts.new(p)); rowuv.append(t)
    grid.append(row); guv.append(rowuv)
for j in range(len(grid) - 1):
    for u in range(UU):
        u2 = (u + 1) % UU
        q = [grid[j][u], grid[j][u2], grid[j + 1][u2], grid[j + 1][u]]
        face(q, [uv(*guv[j][u]), uv(*guv[j][u2]), uv(*guv[j + 1][u2]), uv(*guv[j + 1][u])], MAT_CLOTH, centroid(q) - PC)
for pole, j, sgn in ((PC + Vector((0, 0, -POM_R[2] * 0.98)), 0, -1), (PC + Vector((0, 0, POM_R[2] * 0.98)), len(grid) - 1, 1)):
    pv = bm.verts.new(pole)
    for u in range(UU):
        u2 = (u + 1) % UU
        q = [pv, grid[j][u], grid[j][u2]]
        face(q, [uv(96, 776 - 90 * sgn), uv(*guv[j][u]), uv(*guv[j][u2])], MAT_CLOTH, Vector((0, 0, sgn)))

z_bot, z_top = WB1 - 0.012, POM_Z - POM_R[2] * 0.85
B = Vector((0, -(ry(z_bot) + WB_OFF + 0.0025), z_bot))
T = Vector((0, PC.y, z_top))
axis = (T - B).normalized()
sx_, sy_ = Vector((1, 0, 0)), axis.cross(Vector((1, 0, 0))).normalized()
SEGS = 10
stem = [[bm.verts.new(c + (sx_ * math.cos(2 * math.pi * a / SEGS) + sy_ * math.sin(2 * math.pi * a / SEGS)) * 0.0022)
         for a in range(SEGS)] for c in (B, T)]
for a in range(SEGS):
    a2 = (a + 1) % SEGS
    q = [stem[0][a], stem[0][a2], stem[1][a2], stem[1][a]]
    face(q, [uv(600, 400), uv(606, 400), uv(606, 420), uv(600, 420)], MAT_LEATHER, centroid(q) - (B + T) / 2)

# ---------------------------------------------------------------- brass "FWR" cipher (3D letters from a system font)
cipher_ok = False
try:
    font = bpy.data.fonts.load(FONT)
    cu = bpy.data.curves.new("CipherText", 'FONT')
    cu.body, cu.font, cu.size = "FWR", font, 1.0
    cu.space_character = 0.80
    cu.align_x, cu.align_y = 'CENTER', 'CENTER'
    cu.resolution_u = 8
    tobj = bpy.data.objects.new("CipherText", cu)
    bpy.context.scene.collection.objects.link(tobj)

    def eval_mesh():
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        return bpy.data.meshes.new_from_object(tobj.evaluated_get(dg))

    m0 = eval_mesh()
    xs0 = [v.co.x for v in m0.vertices]; ys0 = [v.co.y for v in m0.vertices]
    k = min(CIPHER_W / (max(xs0) - min(xs0)), CIPHER_H / (max(ys0) - min(ys0)))
    cu.extrude = 0.00075 / k
    cu.bevel_depth = 0.00025 / k
    cu.bevel_resolution = 1
    m1 = eval_mesh()
    xs = [v.co.x for v in m1.vertices]; ys = [v.co.y for v in m1.vertices]
    cx_, cy_ = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    w_, h_ = max(xs) - min(xs), max(ys) - min(ys)
    zs = [v.co.z for v in m1.vertices]
    zmin = min(zs)
    vmap = []
    for v in m1.vertices:
        lx, ly, lz = (v.co.x - cx_) * k, (v.co.y - cy_) * k, (v.co.z - zmin) * k
        vmap.append((bm.verts.new(on_wall(math.pi, -lx, CIPHER_Z + ly, 0.0005 + lz)),
                     uv(838 + 52 * (v.co.x - min(xs)) / w_, 614 + 52 * (1 - (v.co.y - min(ys)) / h_))))
    n_faces = 0
    for poly in m1.polygons:
        try:
            f = bm.faces.new([vmap[i][0] for i in poly.vertices])
        except ValueError:
            continue
        f.material_index = MAT_METAL
        f.smooth = False
        for lp, i in zip(f.loops, poly.vertices):
            lp[uvl].uv = vmap[i][1]
        n_faces += 1
    cipher_ok = n_faces > 0
    print(f"CIPHER font={os.path.basename(FONT)} faces={n_faces} size_m=({w_ * k:.3f} x {h_ * k:.3f})")
    bpy.data.objects.remove(tobj, do_unlink=True)
except Exception as e:
    print("CIPHER FAILED:", e)

# ---------------------------------------------------------------- side buttons + chinstrap under the chin + buckle
for sgn in (-1, 1):
    dome(math.pi + sgn * BOSS_DTH, BOSS_Z, PB_OFF + 0.0022, BOSS_R, BOSS_H, (928, 640), MAT_METAL)


def head_point(d, s=1.045):
    d = Vector(d)
    t = s / math.sqrt((d.x / HEAD_S.x) ** 2 + (d.y / HEAD_S.y) ** 2 + (d.z / HEAD_S.z) ** 2)
    return HEAD_C + d * t


def catmull(pts, samples):
    out = []
    ext = [pts[0] + (pts[0] - pts[1])] + pts + [pts[-1] + (pts[-1] - pts[-2])]
    segs = len(pts) - 1
    for s in range(samples + 1):
        x = s / samples * segs
        i = min(int(x), segs - 1)
        t = x - i
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out

bR = on_wall(math.pi - BOSS_DTH, 0, BOSS_Z, PB_OFF + 0.0010)
bL = on_wall(math.pi + BOSS_DTH, 0, BOSS_Z, PB_OFF + 0.0010)
dirs = [(1, -0.15, 0.12), (1, -0.25, -0.45), (0.8, -0.45, -0.95), (0.35, -0.55, -1.0)]
right = [head_point(d) for d in dirs]
left = [head_point((-d[0], d[1], d[2])) for d in reversed(dirs)]
path = [bR, bR + Vector((0.004, 0, -0.021))] + right + [head_point((0, -0.58, -1.0))] + left + [bL + Vector((-0.004, 0, -0.021)), bL]
pts = catmull(path, 120)

def strap_normal(p):
    n_shako = Vector((p.x / RXB ** 2, p.y / RYB ** 2, 0)).normalized()
    q = p - HEAD_C
    n_head = Vector((q.x / HEAD_S.x ** 2, q.y / HEAD_S.y ** 2, q.z / HEAD_S.z ** 2)).normalized()
    w = min(1.0, max(0.0, (-p.z - 0.005) / 0.03))
    return (n_shako * (1 - w) + n_head * w).normalized()

SW, ST = 0.010, 0.0016
cum = [0.0]
for a, b in zip(pts, pts[1:]):
    cum.append(cum[-1] + (b - a).length)
frames = []
for i, p in enumerate(pts):
    tng = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
    nrm = strap_normal(p)
    bn = tng.cross(nrm).normalized()
    nrm = bn.cross(tng).normalized()
    frames.append((p, tng, bn, nrm))
outer = [[bm.verts.new(p + bn * (sx * SW / 2) + nrm * ST) for sx in (-1, 1)] for p, tng, bn, nrm in frames]
innerv = [[bm.verts.new(p + bn * (sx * SW / 2)) for sx in (-1, 1)] for p, tng, bn, nrm in frames]
for i in range(len(pts) - 1):
    u0, u1 = 768 * cum[i] / cum[-1], 768 * cum[i + 1] / cum[-1]
    nrm = frames[i][3]
    bn = frames[i][2]
    face([outer[i][0], outer[i + 1][0], outer[i + 1][1], outer[i][1]], [uv(u0, 882), uv(u1, 882), uv(u1, 910), uv(u0, 910)], MAT_LEATHER, nrm)
    face([innerv[i][0], innerv[i + 1][0], innerv[i + 1][1], innerv[i][1]], [uv(u0, 882), uv(u1, 882), uv(u1, 910), uv(u0, 910)], MAT_LEATHER, -nrm)
    for sx, sgn in ((0, -1), (1, 1)):
        face([outer[i][sx], outer[i + 1][sx], innerv[i + 1][sx], innerv[i][sx]], [uv(u0, 880), uv(u1, 880), uv(u1, 881), uv(u0, 881)],
             MAT_LEATHER, bn * sgn)

# buckle on the right cheek
bi = 24
p, tng, bn, nrm = frames[bi]
c0 = p + nrm * (ST + 0.0009)
BL, BW, BB, BT = 0.016, 0.014, 0.0022, 0.0018
for dt in (-1, 1):
    box(c0 + tng * (dt * (BL / 2 - BB / 2)), tng, bn, nrm, BB / 2, BW / 2, BT / 2, (846, 620), MAT_METAL)
for db in (-1, 1):
    box(c0 + bn * (db * (BW / 2 - BB / 2)), tng, bn, nrm, BL / 2, BB / 2, BT / 2, (846, 620), MAT_METAL)
box(c0 + nrm * 0.0003, tng, bn, nrm, BL / 2, 0.0006, 0.0006, (846, 620), MAT_METAL)   # prong

# ---------------------------------------------------------------- scene, materials
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
mesh = bpy.data.meshes.new(NAME)
bm.to_mesh(mesh)
bm.free()
shako = bpy.data.objects.new(NAME, mesh)
col_export, col_preview = bpy.data.collections.new("Export"), bpy.data.collections.new("Preview_Only")
scene.collection.children.link(col_export)
scene.collection.children.link(col_preview)
col_export.objects.link(shako)

img_co, img_no, img_ro = (bpy.data.images.load(p) for p in (TEX_CO, TEX_NO, TEX_RO))
for im in (img_no, img_ro):
    im.colorspace_settings.name = 'Non-Color'

def new_material(name):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def node_material(name, metallic):
    m, bsdf = new_material(name)
    nt = m.node_tree
    bsdf.inputs["Metallic"].default_value = metallic
    t_co, t_no, t_ro = (nt.nodes.new("ShaderNodeTexImage") for _ in range(3))
    t_co.image, t_no.image, t_ro.image = img_co, img_no, img_ro
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t_co.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(t_no.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(t_ro.outputs["Color"], bsdf.inputs["Roughness"])
    return m

for m in (node_material("HCL_Shako_Felt", 0.0), node_material("HCL_Shako_Leather", 0.0),
          node_material("HCL_Shako_Cloth", 0.0), node_material("HCL_Shako_Metal", 1.0)):
    mesh.materials.append(m)

hb = bmesh.new()
bmesh.ops.create_uvsphere(hb, u_segments=48, v_segments=24, radius=1.0)
hmesh = bpy.data.meshes.new("Preview_Head")
hb.to_mesh(hmesh)
hb.free()
for p_ in hmesh.polygons:
    p_.use_smooth = True
head = bpy.data.objects.new("Preview_Head", hmesh)
head.scale, head.location = HEAD_S, HEAD_C
hm, hbsdf = new_material("Preview_Mannequin")
hbsdf.inputs["Base Color"].default_value = (0.55, 0.47, 0.42, 1.0)
hbsdf.inputs["Roughness"].default_value = 0.6
hmesh.materials.append(hm)
col_preview.objects.link(head)

# ---------------------------------------------------------------- camera, lights, world, render
target = bpy.data.objects.new("Target", None)
col_preview.objects.link(target)
def track(obj):
    c = obj.constraints.new('TRACK_TO')
    c.target, c.track_axis, c.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 85
cam = bpy.data.objects.new("Cam", cam_data)
col_preview.objects.link(cam)
track(cam)
scene.camera = cam
for name, loc, strength in (("Key", (-0.9, -1.1, 1.1), 4.0), ("Fill", (1.1, -0.6, 0.3), 1.4), ("Rim", (0.4, 1.2, 0.9), 3.0)):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy, ld.angle = strength, math.radians(6)
    lo_ = bpy.data.objects.new(name, ld)
    lo_.location = loc
    col_preview.objects.link(lo_)
    track(lo_)
world = bpy.data.worlds.new("World")
try:
    world.use_nodes = True
except AttributeError:
    pass
next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND').inputs["Color"].default_value = (0.42, 0.44, 0.47, 1.0)
scene.world = world
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 80
try:
    scene.cycles.use_denoising = True
except Exception:
    pass
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'

os.makedirs(RENDER_DIR, exist_ok=True)
def render(name, az, el, dist, tgt, res, show_head=True):
    head.hide_render = not show_head
    target.location = tgt
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(tgt) + dist * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"shako_v3_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("OK render", scene.render.filepath)
    return scene.render.filepath

T0 = (0, 0, 0.05)
sheet_paths = [render("frente_3-4", 35, 12, 1.30, T0, 800), render("frente", 0, 4, 1.30, T0, 800),
               render("lado", 90, 4, 1.30, T0, 800), render("costas_3-4", 150, 18, 1.30, T0, 800)]
render("como_foto", 0, 3, 0.95, (0, 0, 0.12), 900, show_head=False)
render("detalhe", 25, 8, 0.55, (0, -0.11, 0.13), 900)

tiles = []
for pth in sheet_paths:
    im = bpy.data.images.load(pth, check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    tiles.append(px.reshape(h, w, 4))
sheet = np.concatenate([np.concatenate([tiles[2], tiles[3]], axis=1), np.concatenate([tiles[0], tiles[1]], axis=1)], axis=0)
sh = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
sh.pixels.foreach_set(sheet.ravel())
sheet_path = os.path.join(RENDER_DIR, "shako_v3_vistas.png")
sh.save_render(sheet_path, scene=scene)
print("OK sheet", sheet_path)

head.hide_render = False
tris = sum(len(p_.vertices) - 2 for p_ in mesh.polygons)
print(f"STATS verts={len(mesh.vertices)} faces={len(mesh.polygons)} tris={tris} cipher={cipher_ok}")
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, relative_remap=True)
print("OK blend", OUT_BLEND)
for o in scene.objects:
    o.select_set(False)
shako.select_set(True)
bpy.context.view_layer.objects.active = shako
os.makedirs(os.path.dirname(OUT_FBX), exist_ok=True)
bpy.ops.export_scene.fbx(filepath=OUT_FBX, use_selection=True, object_types={'MESH'},
                         apply_unit_scale=True, mesh_smooth_type='FACE', path_mode='AUTO')
print("OK fbx", OUT_FBX)
