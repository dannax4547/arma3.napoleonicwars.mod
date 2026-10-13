# Blender headless: builds the Prussian 1813 line-infantry shako v2 (more realistic geometry, original textures),
# renders previews, saves the .blend and exports an FBX.
# Usage: blender -b --factory-startup --python build_shako_v2.py -- <tex_dir> <out.blend> <out.fbx> <render_dir>
#
# Conventions: metres, +Z up, front = -Y (Blender default). Origin = centre of the bottom opening.
# The Arma 3 placement relative to the head is NOT handled here; it is set when the model is converted to P3D.
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
TEX_DIR, OUT_BLEND, OUT_FBX, RENDER_DIR = args[:4]
NAME = "HCL_Shako_PrussLine1813"
TEX_CO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_co.png")
TEX_NO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_nohq.png")
TEX_RO = os.path.join(TEX_DIR, "hcl_shako_prussline1813_rough_preview.png")

# ---------------------------------------------------------------- dimensions (metres)
H = 0.190                         # body height
RXB, RYB = 0.091, 0.103           # bottom half-width / half-depth (oval, like a head)
RXT, RYT = 0.097, 0.108           # top (slightly bell-shaped)
BAND = 0.028                      # leather band height
BAND_OFF = 0.0012                 # band stands proud of the felt
WALL = 0.004
BEV = 0.007                       # rounded top edge
SAG = 0.004                       # crown dips slightly in the middle
N = 72

VISOR_SPAN, VISOR_LEN = math.radians(80), 0.058
VISOR_Z, VISOR_T = 0.007, 0.0025
ROS_Z, ROS_R = H - 0.050, 0.028   # cockade at the top front
LOOP_W = 0.017
BTN_R, BTN_H = 0.0065, 0.0035
BOSS_Z, BOSS_R, BOSS_H, BOSS_OFF = 0.016, 0.010, 0.003, 0.0036

TS = 1024.0
def uv(px, py):
    return (px / TS, 1.0 - py / TS)

MAT_FELT, MAT_LEATHER, MAT_CLOTH, MAT_METAL = range(4)


def rx(z): return RXB + (RXT - RXB) * z / H
def ry(z): return RYB + (RYT - RYB) * z / H


def wob(theta, z):
    # small hand-made irregularity (about 1 mm), periodic around the shako
    return (0.0007 * math.sin(3 * theta + 1.3) + 0.0005 * math.sin(5 * theta + 0.4 + 12 * z)
            + 0.0004 * math.sin(2 * theta + 2.1) * (z / H))


def P(theta, z, off=0.0):
    d = off + wob(theta, z)
    return Vector(((rx(z) + d) * math.sin(theta), (ry(z) + d) * math.cos(theta), z))


def outward(theta):
    return Vector((math.sin(theta) / RXB, math.cos(theta) / RYB, 0)).normalized()


bm = bmesh.new()
uvl = bm.loops.layers.uv.new("UVMap")


def face(verts, uvs, mat, expect):
    if len(verts) == 3:
        n = (verts[1].co - verts[0].co).cross(verts[2].co - verts[0].co)
    else:
        n = (verts[2].co - verts[0].co).cross(verts[3].co - verts[1].co)
    if n.dot(expect) < 0:
        verts, uvs = verts[::-1], uvs[::-1]
    f = bm.faces.new(verts)
    f.material_index = mat
    f.smooth = True
    for lp, t in zip(f.loops, uvs):
        lp[uvl].uv = t
    return f


def centroid(vs):
    return sum((v.co for v in vs), Vector()) / len(vs)


def th(i):
    return 2 * math.pi * i / N


# ---------------------------------------------------------------- felt wall + rounded top edge + crown
prof = [(BAND - 0.003, 0.0), (0.045, 0.0), (0.075, 0.0), (0.105, 0.0), (0.135, 0.0), (0.160, 0.0), (H - BEV, 0.0)]
for a in (22.5, 45.0, 67.5, 90.0):
    al = math.radians(a)
    prof.append((H - BEV + BEV * math.sin(al), -BEV * (1 - math.cos(al))))
arc = [0.0]
for (z0, o0), (z1, o1) in zip(prof, prof[1:]):
    arc.append(arc[-1] + math.hypot(z1 - z0, o1 - o0))
felt_py = [(arc[-1] - s) / arc[-1] * 286 for s in arc]          # top edge -> y 0, bottom -> y 286

wall = [[bm.verts.new(P(th(i), z, o)) for i in range(N)] for z, o in prof]
for j in range(len(prof) - 1):
    for i in range(N):
        i2 = (i + 1) % N
        q = [wall[j][i], wall[j][i2], wall[j + 1][i2], wall[j + 1][i]]
        face(q, [uv(TS * i / N, felt_py[j]), uv(TS * (i + 1) / N, felt_py[j]),
                 uv(TS * (i + 1) / N, felt_py[j + 1]), uv(TS * i / N, felt_py[j + 1])],
             MAT_FELT, (centroid(q) - Vector((0, 0, centroid(q).z))) + Vector((0, 0, 2.0 if j >= 6 else 0.0)))

rings = [wall[-1]]
rhos = [1.0, 0.75, 0.5, 0.25]
for rho in rhos[1:]:
    z = H - SAG * (1 - rho * rho)
    rings.append([bm.verts.new(((rx(H) - BEV) * rho * math.sin(th(i)), (ry(H) - BEV) * rho * math.cos(th(i)), z))
                  for i in range(N)])
centre = bm.verts.new((0, 0, H - SAG))
def crown_uv(rho, i):
    return uv(128 + 117 * rho * math.sin(th(i)), 480 - 117 * rho * math.cos(th(i)))
for k in range(len(rings) - 1):
    for i in range(N):
        i2 = (i + 1) % N
        face([rings[k][i], rings[k][i2], rings[k + 1][i2], rings[k + 1][i]],
             [crown_uv(rhos[k], i), crown_uv(rhos[k], i + 1), crown_uv(rhos[k + 1], i + 1), crown_uv(rhos[k + 1], i)],
             MAT_FELT, Vector((0, 0, 1)))
for i in range(N):
    face([centre, rings[-1][i], rings[-1][(i + 1) % N]],
         [uv(128, 480), crown_uv(rhos[-1], i), crown_uv(rhos[-1], i + 1)], MAT_FELT, Vector((0, 0, 1)))

# ---------------------------------------------------------------- leather band (proud of the felt) + top lip
bz = [0.0, 0.014, BAND]
band = [[bm.verts.new(P(th(i), z, BAND_OFF)) for i in range(N)] for z in bz]
def band_py(z):
    return 290 + (BAND - z) / BAND * 44
for j in range(2):
    for i in range(N):
        i2 = (i + 1) % N
        face([band[j][i], band[j][i2], band[j + 1][i2], band[j + 1][i]],
             [uv(TS * i / N, band_py(bz[j])), uv(TS * (i + 1) / N, band_py(bz[j])),
              uv(TS * (i + 1) / N, band_py(bz[j + 1])), uv(TS * i / N, band_py(bz[j + 1]))],
             MAT_LEATHER, outward(th(i + 0.5)))
lip_o = [bm.verts.new(P(th(i), BAND, BAND_OFF)) for i in range(N)]
lip_i = [bm.verts.new(P(th(i), BAND, -0.0005)) for i in range(N)]
for i in range(N):
    i2 = (i + 1) % N
    face([lip_o[i], lip_o[i2], lip_i[i2], lip_i[i]],
         [uv(TS * i / N, 288.5), uv(TS * (i + 1) / N, 288.5), uv(TS * (i + 1) / N, 289.5), uv(TS * i / N, 289.5)],
         MAT_LEATHER, Vector((0, 0, 1)))

# ---------------------------------------------------------------- inside: inner wall, ceiling, bottom rim
DX, DY = 256, 352
zin = [0.0, 0.05, 0.10, 0.15, H - WALL - SAG]
inner = [[bm.verts.new(P(th(i), z, -WALL)) for i in range(N)] for z in zin]
for j in range(len(zin) - 1):
    for i in range(N):
        i2 = (i + 1) % N
        v0, v1 = DY + 256 * (1 - zin[j] / H), DY + 256 * (1 - zin[j + 1] / H)
        face([inner[j][i], inner[j][i2], inner[j + 1][i2], inner[j + 1][i]],
             [uv(DX + 256 * i / N, v0), uv(DX + 256 * (i + 1) / N, v0), uv(DX + 256 * (i + 1) / N, v1), uv(DX + 256 * i / N, v1)],
             MAT_FELT, -outward(th(i + 0.5)))
cc = bm.verts.new((0, 0, H - WALL - SAG))
for i in range(N):
    face([cc, inner[-1][i], inner[-1][(i + 1) % N]], [uv(DX + 128, DY + 128), uv(DX + 20, DY + 20), uv(DX + 40, DY + 20)],
         MAT_FELT, Vector((0, 0, -1)))
rim_o = [bm.verts.new(P(th(i), 0.0, BAND_OFF)) for i in range(N)]
rim_i = [bm.verts.new(P(th(i), 0.0, -WALL)) for i in range(N)]
for i in range(N):
    i2 = (i + 1) % N
    face([rim_o[i], rim_o[i2], rim_i[i2], rim_i[i]],
         [uv(DX + 256 * i / N, DY + 250), uv(DX + 256 * (i + 1) / N, DY + 250), uv(DX + 256 * (i + 1) / N, DY + 254), uv(DX + 256 * i / N, DY + 254)],
         MAT_FELT, Vector((0, 0, -1)))

# ---------------------------------------------------------------- visor: curved, with a rounded bound edge
M, K = 32, 6
vt, vb = [], []
def visor_point(m, t):
    phi = -VISOR_SPAN + 2 * VISOR_SPAN * m / M
    L = max(0.003, VISOR_LEN * math.cos(phi / VISOR_SPAN * math.pi / 2) ** 0.65)
    theta = math.pi + phi
    e = t * L
    base = P(theta, VISOR_Z, -0.002)
    z = -e * math.tan(math.radians(14)) - 0.010 * t * t * (L / VISOR_LEN)
    return base + outward(theta) * e + Vector((0, 0, z)), theta
for k in range(K + 1):
    vt.append([bm.verts.new(visor_point(m, k / K)[0]) for m in range(M + 1)])
    vb.append([bm.verts.new(visor_point(m, k / K)[0] - Vector((0, 0, VISOR_T))) for m in range(M + 1)])
mid = [bm.verts.new(visor_point(m, 1.0)[0] + outward(visor_point(m, 1.0)[1]) * 0.0012 - Vector((0, 0, VISOR_T / 2)))
       for m in range(M + 1)]
VX, VY = 512, 352
def vuv(m, py):
    return uv(VX + 256 * m / M, py)
for k in range(K):
    for m in range(M):
        y0, y1 = VY + 228 * k / K, VY + 228 * (k + 1) / K
        face([vt[k][m], vt[k][m + 1], vt[k + 1][m + 1], vt[k + 1][m]],
             [vuv(m, y0), vuv(m + 1, y0), vuv(m + 1, y1), vuv(m, y1)], MAT_LEATHER, Vector((0, 0, 1)))
        face([vb[k][m], vb[k][m + 1], vb[k + 1][m + 1], vb[k + 1][m]],
             [vuv(m, y0), vuv(m + 1, y0), vuv(m + 1, y1), vuv(m, y1)], MAT_LEATHER, Vector((0, 0, -1)))
for m in range(M):
    d = outward(math.pi - VISOR_SPAN + 2 * VISOR_SPAN * (m + 0.5) / M)
    face([vt[K][m], vt[K][m + 1], mid[m + 1], mid[m]], [vuv(m, 584), vuv(m + 1, 584), vuv(m + 1, 594), vuv(m, 594)],
         MAT_LEATHER, d + Vector((0, 0, 0.5)))
    face([mid[m], mid[m + 1], vb[K][m + 1], vb[K][m]], [vuv(m, 594), vuv(m + 1, 594), vuv(m + 1, 604), vuv(m, 604)],
         MAT_LEATHER, d - Vector((0, 0, 0.5)))
for m, sgn in ((0, -1), (M, 1)):
    t_ang = math.pi + sgn * VISOR_SPAN
    tang = Vector((math.cos(t_ang) / RXB, -math.sin(t_ang) / RYB, 0)).normalized() * sgn
    for k in range(K):
        face([vt[k][m], vt[k + 1][m], vb[k + 1][m], vb[k][m]], [vuv(0, 586), vuv(1, 586), vuv(1, 600), vuv(0, 600)],
             MAT_LEATHER, tang)

# ---------------------------------------------------------------- wrapped details (cockade, loop, button, side bosses)
def on_wall(theta0, s, z, off):
    local_r = rx(z) if abs(math.sin(theta0)) < 0.5 else ry(z)
    return P(theta0 + s / local_r, z, off)

def dome_off(rho):
    return 0.0045 - 0.002 * (rho / ROS_R) ** 2

RINGS, SEG = 5, 48
ros = [[bm.verts.new(on_wall(math.pi, 0, ROS_Z, dome_off(0)))]]
for k in range(1, RINGS + 1):
    rho = ROS_R * k / RINGS
    ros.append([bm.verts.new(on_wall(math.pi, rho * math.cos(2 * math.pi * a / SEG), ROS_Z + rho * math.sin(2 * math.pi * a / SEG), dome_off(rho)))
                for a in range(SEG)])
def ros_uv(k, a, scale=1.0):
    r = 120 * k / RINGS * scale
    t = 2 * math.pi * a / SEG
    return uv(896 - r * math.cos(t), 480 - r * math.sin(t))
inside_pt = on_wall(math.pi, 0, ROS_Z, -0.02)
for a in range(SEG):
    a2 = (a + 1) % SEG
    q = [ros[0][0], ros[1][a], ros[1][a2]]
    face(q, [ros_uv(0, 0), ros_uv(1, a), ros_uv(1, a + 1)], MAT_CLOTH, centroid(q) - inside_pt)
    for k in range(1, RINGS):
        q = [ros[k][a], ros[k][a2], ros[k + 1][a2], ros[k + 1][a]]
        face(q, [ros_uv(k, a), ros_uv(k, a + 1), ros_uv(k + 1, a + 1), ros_uv(k + 1, a)], MAT_CLOTH, centroid(q) - inside_pt)
skirt = [bm.verts.new(on_wall(math.pi, ROS_R * math.cos(2 * math.pi * a / SEG), ROS_Z + ROS_R * math.sin(2 * math.pi * a / SEG), 0.0004))
         for a in range(SEG)]
for a in range(SEG):
    a2 = (a + 1) % SEG
    q = [ros[RINGS][a], ros[RINGS][a2], skirt[a2], skirt[a]]
    face(q, [ros_uv(RINGS, a, 0.96), ros_uv(RINGS, a + 1, 0.96), ros_uv(RINGS, a + 1, 0.99), ros_uv(RINGS, a, 0.99)],
         MAT_CLOTH, centroid(q) - on_wall(math.pi, 0, ROS_Z, 0.0))

LC, LR = 4, 10
loop_top = H - BEV - 0.001
def loop_off(s, z, i):
    rho = math.hypot(s, z - ROS_Z)
    base = dome_off(rho) + 0.0012 if rho < ROS_R else 0.0018
    return base + 0.0006 * (1 - (2 * i / LC - 1) ** 2)
lv = []
for j in range(LR + 1):
    z = ROS_Z + (loop_top - ROS_Z) * j / LR
    lv.append([bm.verts.new(on_wall(math.pi, LOOP_W / 2 - LOOP_W * i / LC, z, loop_off(LOOP_W / 2 - LOOP_W * i / LC, z, i)))
               for i in range(LC + 1)])
def loop_uv(i, j):
    return uv(772 + 56 * i / LC, 864 - 256 * j / LR)
for j in range(LR):
    for i in range(LC):
        face([lv[j][i], lv[j][i + 1], lv[j + 1][i + 1], lv[j + 1][i]],
             [loop_uv(i, j), loop_uv(i + 1, j), loop_uv(i + 1, j + 1), loop_uv(i, j + 1)], MAT_CLOTH, Vector((0, -1, 0)))
for i_edge, sx in ((0, -1.0), (LC, 1.0)):
    s = LOOP_W / 2 - LOOP_W * i_edge / LC
    low = [bm.verts.new(on_wall(math.pi, s, ROS_Z + (loop_top - ROS_Z) * j / LR, 0.0003)) for j in range(LR + 1)]
    for j in range(LR):
        face([lv[j][i_edge], lv[j + 1][i_edge], low[j + 1], low[j]],
             [uv(769, 864 - 25.6 * j), uv(769, 864 - 25.6 * (j + 1)), uv(770, 864 - 25.6 * (j + 1)), uv(770, 864 - 25.6 * j)],
             MAT_CLOTH, Vector((sx, 0, 0)))
top_low = [bm.verts.new(on_wall(math.pi, LOOP_W / 2 - LOOP_W * i / LC, loop_top, 0.0003)) for i in range(LC + 1)]
for i in range(LC):
    face([lv[LR][i], lv[LR][i + 1], top_low[i + 1], top_low[i]],
         [uv(772 + 14 * i, 609), uv(772 + 14 * (i + 1), 609), uv(772 + 14 * (i + 1), 611), uv(772 + 14 * i, 611)],
         MAT_CLOTH, Vector((0, 0, 1)))

def dome(theta0, z0, base_off, R, Hd, uc, mat, segs=20, rings=4):
    pts = [[bm.verts.new(on_wall(theta0, 0, z0, base_off + Hd))]]
    for k in range(1, rings + 1):
        b = math.pi / 2 * k / rings
        rho, off = R * math.sin(b), base_off + Hd * math.cos(b)
        pts.append([bm.verts.new(on_wall(theta0, rho * math.cos(2 * math.pi * a / segs), z0 + rho * math.sin(2 * math.pi * a / segs), off))
                    for a in range(segs)])
    inner_pt = on_wall(theta0, 0, z0, base_off - 0.01)
    def duv(k, a):
        r = 28 * math.sin(math.pi / 2 * k / rings)
        t = 2 * math.pi * a / segs
        return uv(uc[0] - r * math.cos(t), uc[1] - r * math.sin(t))
    for a in range(segs):
        a2 = (a + 1) % segs
        q = [pts[0][0], pts[1][a], pts[1][a2]]
        face(q, [duv(0, 0), duv(1, a), duv(1, a + 1)], mat, centroid(q) - inner_pt)
        for k in range(1, rings):
            q = [pts[k][a], pts[k][a2], pts[k + 1][a2], pts[k + 1][a]]
            face(q, [duv(k, a), duv(k, a + 1), duv(k + 1, a + 1), duv(k + 1, a)], mat, centroid(q) - inner_pt)

dome(math.pi, ROS_Z, dome_off(0) + 0.0012 + 0.0006, BTN_R, BTN_H, (864, 640), MAT_METAL)

# ---------------------------------------------------------------- chinstrap, tied up across the front, + side bosses
SW, ST, SC = 0.013, 0.0022, 40
def strap_z(theta):
    return BOSS_Z + 0.020 * math.sin(theta - math.pi / 2) ** 2
def strap_base(z):
    return BAND_OFF if z < BAND + 0.001 else 0.0
st = []
for c in range(SC + 1):
    theta = math.pi / 2 + math.pi * c / SC
    zc = strap_z(theta)
    row = []
    for i in range(3):
        z = zc - SW / 2 + SW * i / 2
        row.append(bm.verts.new(P(theta, z, strap_base(z) + ST)))
    st.append(row)
for c in range(SC):
    for i in range(2):
        q = [st[c][i], st[c + 1][i], st[c + 1][i + 1], st[c][i + 1]]
        face(q, [uv(768 * c / SC, 882 + 14 * i), uv(768 * (c + 1) / SC, 882 + 14 * i),
                 uv(768 * (c + 1) / SC, 882 + 14 * (i + 1)), uv(768 * c / SC, 882 + 14 * (i + 1))],
             MAT_LEATHER, outward(math.pi / 2 + math.pi * (c + 0.5) / SC))
for i_edge, sz in ((0, -1.0), (2, 1.0)):
    low = []
    for c in range(SC + 1):
        theta = math.pi / 2 + math.pi * c / SC
        z = strap_z(theta) - SW / 2 + SW * i_edge / 2
        low.append(bm.verts.new(P(theta, z, strap_base(z) + 0.0002)))
    for c in range(SC):
        face([st[c][i_edge], st[c + 1][i_edge], low[c + 1], low[c]],
             [uv(768 * c / SC, 881), uv(768 * (c + 1) / SC, 881), uv(768 * (c + 1) / SC, 882), uv(768 * c / SC, 882)],
             MAT_LEATHER, Vector((0, 0, sz)))
for theta0 in (math.pi / 2, 3 * math.pi / 2):
    dome(theta0, BOSS_Z, BOSS_OFF, BOSS_R, BOSS_H, (928, 640), MAT_METAL)

# ---------------------------------------------------------------- scene: object, materials
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

img_co = bpy.data.images.load(TEX_CO)
img_no = bpy.data.images.load(TEX_NO)
img_ro = bpy.data.images.load(TEX_RO)
for im in (img_no, img_ro):
    im.colorspace_settings.name = 'Non-Color'

def node_material(name, metallic, rough_scale=1.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Metallic"].default_value = metallic
    t_co, t_no, t_ro = (nt.nodes.new("ShaderNodeTexImage") for _ in range(3))
    t_co.image, t_no.image, t_ro.image = img_co, img_no, img_ro
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t_co.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(t_no.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if rough_scale == 1.0:
        nt.links.new(t_ro.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = rough_scale
        nt.links.new(t_ro.outputs["Color"], mul.inputs[0])
        nt.links.new(mul.outputs[0], bsdf.inputs["Roughness"])
    return m

for m in (node_material("HCL_Shako_Felt", 0.0), node_material("HCL_Shako_Leather", 0.0),
          node_material("HCL_Shako_Cloth", 0.0), node_material("HCL_Shako_Metal", 1.0)):
    mesh.materials.append(m)

# preview-only mannequin head (not exported)
def simple_material(name, color, rough):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return m

hb = bmesh.new()
bmesh.ops.create_uvsphere(hb, u_segments=48, v_segments=24, radius=1.0)
hmesh = bpy.data.meshes.new("Preview_Head")
hb.to_mesh(hmesh)
hb.free()
for p in hmesh.polygons:
    p.use_smooth = True
head = bpy.data.objects.new("Preview_Head", hmesh)
head.scale = (0.078, 0.088, 0.118)
head.location = (0, 0.004, -0.046)
hmesh.materials.append(simple_material("Preview_Mannequin", (0.55, 0.47, 0.42), 0.6))
col_preview.objects.link(head)

# ---------------------------------------------------------------- camera, lights, world, render settings
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
for name, loc, strength in (("Key", (-0.9, -1.1, 1.1), 4.0), ("Fill", (1.1, -0.6, 0.3), 1.3), ("Rim", (0.4, 1.2, 0.9), 3.0)):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = strength
    ld.angle = math.radians(6)
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col_preview.objects.link(lo)
    track(lo)

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

# ---------------------------------------------------------------- renders
os.makedirs(RENDER_DIR, exist_ok=True)
def render(name, az, el, dist, tgt, res, show_head=True):
    head.hide_render = not show_head
    target.location = tgt
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(tgt) + dist * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"shako_v2_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("OK render", scene.render.filepath)
    return scene.render.filepath

T = (0, 0, 0.07)
sheet_paths = [render("frente_3-4", 35, 12, 0.95, T, 800), render("frente", 0, 4, 0.95, T, 800),
               render("lado", 90, 4, 0.95, T, 800), render("costas_3-4", 150, 18, 0.95, T, 800)]
render("detalhe_cocar", 28, 10, 0.42, (0, -0.10, 0.11), 900)
render("topo_sem_cabeca", 40, 38, 0.95, (0, 0, 0.09), 900, show_head=False)

tiles = []
for p in sheet_paths:
    im = bpy.data.images.load(p, check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    tiles.append(px.reshape(h, w, 4))
sheet = np.concatenate([np.concatenate([tiles[2], tiles[3]], axis=1), np.concatenate([tiles[0], tiles[1]], axis=1)], axis=0)
sh = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
sh.pixels.foreach_set(sheet.ravel())
sheet_path = os.path.join(RENDER_DIR, "shako_v2_vistas.png")
sh.save_render(sheet_path, scene=scene)
print("OK sheet", sheet_path)

# ---------------------------------------------------------------- stats, save, export
head.hide_render = False
tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
print(f"STATS verts={len(mesh.vertices)} faces={len(mesh.polygons)} tris={tris}")
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
