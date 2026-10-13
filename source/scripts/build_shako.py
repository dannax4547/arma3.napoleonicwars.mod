# Blender headless: builds the Prussian 1813 line-infantry shako, renders preview views,
# saves the .blend and exports an FBX.
# Usage: blender -b --factory-startup --python build_shako.py -- <co.png> <out.blend> <out.fbx> <render_dir>
#
# Conventions: metres, +Z up, front = -Y (Blender default). Origin = centre of the shako's bottom opening.
# The Arma 3 placement (offset relative to the head proxy) is NOT handled here; it is set when exporting to P3D.
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
TEX, OUT_BLEND, OUT_FBX, RENDER_DIR = args[0], args[1], args[2], args[3]
NAME = "HCL_Shako_PrussLine1813"

# ---------------------------------------------------------------- dimensions (metres)
H = 0.195           # body height
RB, RT = 0.098, 0.104   # bottom / top outer radius (slightly bell-shaped)
BAND = 0.025        # leather band at the bottom
WALL = 0.004        # felt thickness
N = 48              # segments around

VISOR_SPAN = math.radians(75)   # half-angle covered by the peak
VISOR_LEN = 0.055               # length at the front
VISOR_DROP = math.radians(22)   # downward slope
VISOR_Z = 0.004
VISOR_T = 0.003

ROS_Z, ROS_R = 0.118, 0.032     # cockade rosette centre height / radius
LOOP_W, LOOP_TOP = 0.024, H - 0.006

# ---------------------------------------------------------------- texture layout (pixels, top-left origin)
TS = 1024.0
def uv(px, py):
    return (px / TS, 1.0 - py / TS)

FELT_Y0, FELT_Y1 = 0, 288
BAND_Y0, BAND_Y1 = 288, 336
CROWN_C, CROWN_R = (128, 480), 117
DARK = (256, 352, 256, 256)
VISOR_BOX = (520, 360, 240, 240)
ROS_C, ROS_PR = (861, 530), 72
LOOP_X0, LOOP_X1, LOOP_PY_TOP = 835, 890, 360


def r_at(z):
    return RB + (RT - RB) * z / H


def cyl(theta, rad, z):
    # theta = 0 at the back (+Y), pi at the front (-Y)
    return Vector((rad * math.sin(theta), rad * math.cos(theta), z))


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
    for loop, t in zip(f.loops, uvs):
        loop[uvl].uv = t
    return f


MAT_FELT, MAT_LEATHER, MAT_METAL = 0, 1, 2

# ---------------------------------------------------------------- outer wall (felt + bottom band)
zs = [0.0, 0.0125, BAND, 0.06, 0.10, 0.14, 0.17, H]
wall = [[bm.verts.new(cyl(2 * math.pi * i / N, r_at(z), z)) for i in range(N)] for z in zs]
for j in range(len(zs) - 1):
    in_band = zs[j + 1] <= BAND + 1e-9
    def py(z):
        if in_band:
            return BAND_Y0 + (BAND - z) / BAND * (BAND_Y1 - BAND_Y0)
        return FELT_Y0 + (H - z) / (H - BAND) * (FELT_Y1 - FELT_Y0)
    for i in range(N):
        i2 = (i + 1) % N
        u0, u1 = i / N * TS, (i + 1) / N * TS
        tc = 2 * math.pi * (i + 0.5) / N
        face([wall[j][i], wall[j][i2], wall[j + 1][i2], wall[j + 1][i]],
             [uv(u0, py(zs[j])), uv(u1, py(zs[j])), uv(u1, py(zs[j + 1])), uv(u0, py(zs[j + 1]))],
             MAT_FELT, Vector((math.sin(tc), math.cos(tc), 0)))

# ---------------------------------------------------------------- crown (top)
c = bm.verts.new((0, 0, H))
ring = [bm.verts.new(cyl(2 * math.pi * i / N, RT, H)) for i in range(N)]
def crown_uv(i):
    t = 2 * math.pi * i / N
    return uv(CROWN_C[0] + CROWN_R * math.sin(t), CROWN_C[1] - CROWN_R * math.cos(t))
for i in range(N):
    face([c, ring[i], ring[(i + 1) % N]], [uv(*CROWN_C), crown_uv(i), crown_uv(i + 1)], MAT_FELT, Vector((0, 0, 1)))

# ---------------------------------------------------------------- inside: inner wall, ceiling, bottom rim
dx, dy, dw, dh = DARK
zin = [0.0, 0.05, 0.10, 0.15, H - WALL]
inner = [[bm.verts.new(cyl(2 * math.pi * i / N, r_at(z) - WALL, z)) for i in range(N)] for z in zin]
for j in range(len(zin) - 1):
    for i in range(N):
        i2 = (i + 1) % N
        tc = 2 * math.pi * (i + 0.5) / N
        u0, u1 = dx + dw * i / N, dx + dw * (i + 1) / N
        v0, v1 = dy + dh * (1 - zin[j] / H), dy + dh * (1 - zin[j + 1] / H)
        face([inner[j][i], inner[j][i2], inner[j + 1][i2], inner[j + 1][i]],
             [uv(u0, v0), uv(u1, v0), uv(u1, v1), uv(u0, v1)],
             MAT_FELT, Vector((-math.sin(tc), -math.cos(tc), 0)))
cc = bm.verts.new((0, 0, H - WALL))
for i in range(N):
    i2 = (i + 1) % N
    face([cc, inner[-1][i], inner[-1][i2]], [uv(dx + dw / 2, dy + dh / 2), uv(dx + 10, dy + 10), uv(dx + 20, dy + 10)],
         MAT_FELT, Vector((0, 0, -1)))
rim_o = [bm.verts.new(cyl(2 * math.pi * i / N, RB, 0.0)) for i in range(N)]
rim_i = [bm.verts.new(cyl(2 * math.pi * i / N, RB - WALL, 0.0)) for i in range(N)]
for i in range(N):
    i2 = (i + 1) % N
    face([rim_o[i], rim_o[i2], rim_i[i2], rim_i[i]],
         [uv(dx + 5, dy + 5), uv(dx + 15, dy + 5), uv(dx + 15, dy + 8), uv(dx + 5, dy + 8)],
         MAT_FELT, Vector((0, 0, -1)))

# ---------------------------------------------------------------- visor (peak)
M, K = 24, 4
top, bot = [], []
for k in range(K + 1):
    rt_row, rb_row = [], []
    for m in range(M + 1):
        phi = -VISOR_SPAN + 2 * VISOR_SPAN * m / M
        L = max(0.004, VISOR_LEN * math.cos(phi / VISOR_SPAN * math.pi / 2) ** 0.7)
        t = k / K
        rad = r_at(VISOR_Z) - 0.002 + t * L
        z = VISOR_Z - t * L * math.tan(VISOR_DROP)
        theta = math.pi + phi
        rt_row.append(bm.verts.new(cyl(theta, rad, z)))
        rb_row.append(bm.verts.new(cyl(theta, rad, z - VISOR_T)))
    top.append(rt_row)
    bot.append(rb_row)
xy = [v.co for row in top for v in row]
minx, maxx = min(p.x for p in xy), max(p.x for p in xy)
miny, maxy = min(p.y for p in xy), max(p.y for p in xy)
vx, vy, vw, vh = VISOR_BOX
def visor_uv(v):
    return uv(vx + (v.co.x - minx) / (maxx - minx) * vw, vy + (v.co.y - miny) / (maxy - miny) * vh)
for k in range(K):
    for m in range(M):
        q = [top[k][m], top[k][m + 1], top[k + 1][m + 1], top[k + 1][m]]
        face(q, [visor_uv(v) for v in q], MAT_LEATHER, Vector((0, 0, 1)))
        q = [bot[k][m], bot[k][m + 1], bot[k + 1][m + 1], bot[k + 1][m]]
        face(q, [visor_uv(v) for v in q], MAT_LEATHER, Vector((0, 0, -1)))
for m in range(M):
    q = [top[K][m], top[K][m + 1], bot[K][m + 1], bot[K][m]]
    phi = -VISOR_SPAN + 2 * VISOR_SPAN * (m + 0.5) / M
    face(q, [visor_uv(v) for v in q], MAT_LEATHER, cyl(math.pi + phi, 1.0, 0) - Vector((0, 0, 0)))
for m, sgn in ((0, -1), (M, 1)):
    for k in range(K):
        q = [top[k][m], top[k + 1][m], bot[k + 1][m], bot[k][m]]
        th = math.pi + sgn * VISOR_SPAN
        tang = Vector((math.cos(th), -math.sin(th), 0)) * sgn   # points away from the visor, along the rim
        face(q, [visor_uv(v) for v in q], MAT_LEATHER, tang)

# ---------------------------------------------------------------- cockade rosette + loop (wrapped on the wall)
def on_wall(s, z, off):
    rad = r_at(z)
    return cyl(math.pi + s / rad, rad + off, z)

RINGS, SEG = 4, 32
ros = []
for k in range(RINGS + 1):
    rho = ROS_R * k / RINGS
    off = 0.0035 - 0.0015 * (rho / ROS_R) ** 2
    ros.append([bm.verts.new(on_wall(rho * math.cos(2 * math.pi * a / SEG), ROS_Z + rho * math.sin(2 * math.pi * a / SEG), off))
                for a in range(SEG)] if k else [bm.verts.new(on_wall(0, ROS_Z, off))])
def ros_uv(k, a, scale=1.0):
    rho = ROS_PR * k / RINGS * scale
    t = 2 * math.pi * a / SEG
    return uv(ROS_C[0] - rho * math.cos(t), ROS_C[1] - rho * math.sin(t))
front = Vector((0, -1, 0))
for a in range(SEG):
    a2 = (a + 1) % SEG
    face([ros[0][0], ros[1][a], ros[1][a2]], [ros_uv(0, 0), ros_uv(1, a), ros_uv(1, a + 1)], MAT_METAL, front)
    for k in range(1, RINGS):
        face([ros[k][a], ros[k][a2], ros[k + 1][a2], ros[k + 1][a]],
             [ros_uv(k, a), ros_uv(k, a + 1), ros_uv(k + 1, a + 1), ros_uv(k + 1, a)], MAT_METAL, front)
skirt = [bm.verts.new(on_wall(ROS_R * math.cos(2 * math.pi * a / SEG), ROS_Z + ROS_R * math.sin(2 * math.pi * a / SEG), 0.0003))
         for a in range(SEG)]
centre3d = on_wall(0, ROS_Z, 0)
for a in range(SEG):
    a2 = (a + 1) % SEG
    q = [ros[RINGS][a], ros[RINGS][a2], skirt[a2], skirt[a]]
    mid = (q[0].co + q[1].co) / 2
    face(q, [ros_uv(RINGS, a, 0.97), ros_uv(RINGS, a + 1, 0.97), ros_uv(RINGS, a + 1, 0.99), ros_uv(RINGS, a, 0.99)],
         MAT_METAL, mid - centre3d)

LC, LR = 4, 6
loop_v = [[bm.verts.new(on_wall(LOOP_W / 2 - LOOP_W * i / LC, ROS_Z + (LOOP_TOP - ROS_Z) * j / LR, 0.0012))
           for i in range(LC + 1)] for j in range(LR + 1)]
def loop_uv(i, j):
    return uv(LOOP_X0 + (LOOP_X1 - LOOP_X0) * i / LC, ROS_C[1] - (ROS_C[1] - LOOP_PY_TOP) * j / LR)
for j in range(LR):
    for i in range(LC):
        face([loop_v[j][i], loop_v[j][i + 1], loop_v[j + 1][i + 1], loop_v[j + 1][i]],
             [loop_uv(i, j), loop_uv(i + 1, j), loop_uv(i + 1, j + 1), loop_uv(i, j + 1)], MAT_METAL, front)

# ---------------------------------------------------------------- object + materials
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
mesh = bpy.data.meshes.new(NAME)
bm.to_mesh(mesh)
bm.free()
shako = bpy.data.objects.new(NAME, mesh)
col_export = bpy.data.collections.new("Export")
col_preview = bpy.data.collections.new("Preview_Only")
scene.collection.children.link(col_export)
scene.collection.children.link(col_preview)
col_export.objects.link(shako)

img = bpy.data.images.load(TEX, check_existing=True)

def material(name, rough, metal, img=None, color=None):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass   # node-based by default in newer Blender versions
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if img is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if color is not None:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    return m

for m in (material("HCL_Shako_Felt", 0.85, 0.0, img),
          material("HCL_Shako_Leather", 0.35, 0.0, img),
          material("HCL_Shako_Metal", 0.35, 0.7, img)):
    mesh.materials.append(m)

# preview-only mannequin head for scale (not exported)
hb = bmesh.new()
bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hmesh = bpy.data.meshes.new("Preview_Head")
hb.to_mesh(hmesh)
hb.free()
for p in hmesh.polygons:
    p.use_smooth = True
head = bpy.data.objects.new("Preview_Head", hmesh)
head.scale = (0.078, 0.088, 0.118)
head.location = (0, 0.004, -0.046)
hmesh.materials.append(material("Preview_Mannequin", 0.6, 0.0, color=(0.55, 0.47, 0.42)))
col_preview.objects.link(head)

# ---------------------------------------------------------------- camera, lights, world
target = bpy.data.objects.new("Target", None)
target.location = (0, 0, 0.07)
col_preview.objects.link(target)

def track(obj):
    c = obj.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 85
cam = bpy.data.objects.new("Cam", cam_data)
col_preview.objects.link(cam)
track(cam)
scene.camera = cam

for name, loc, strength in (("Key", (-0.9, -1.1, 1.1), 4.0), ("Fill", (1.1, -0.6, 0.3), 1.2), ("Rim", (0.4, 1.2, 0.9), 3.0)):
    ld = bpy.data.lights.new(name, 'SUN')
    ld.energy = strength
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    col_preview.objects.link(lo)
    track(lo)

world = bpy.data.worlds.new("World")
try:
    world.use_nodes = True
except AttributeError:
    pass
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs["Color"].default_value = (0.42, 0.44, 0.47, 1.0)
scene.world = world

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64
try:
    scene.cycles.use_denoising = True
except Exception:
    pass
scene.render.resolution_x = scene.render.resolution_y = 700
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'

# ---------------------------------------------------------------- renders
os.makedirs(RENDER_DIR, exist_ok=True)
views = (("frente_3-4", 35, 12), ("frente", 0, 4), ("lado", 90, 4), ("costas_3-4", 150, 18))
D = 0.95
paths = []
for name, az, el in views:
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(target.location) + D * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    scene.render.filepath = os.path.join(RENDER_DIR, f"shako_prussline1813_{name}.png")
    bpy.ops.render.render(write_still=True)
    paths.append(scene.render.filepath)
    print("OK render", scene.render.filepath)

# 2x2 contact sheet
tiles = []
for p in paths:
    im = bpy.data.images.load(p, check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    tiles.append(px.reshape(h, w, 4))
sheet = np.concatenate([np.concatenate([tiles[2], tiles[3]], axis=1),
                        np.concatenate([tiles[0], tiles[1]], axis=1)], axis=0)   # bottom-left origin
sh = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
sh.pixels.foreach_set(sheet.ravel())
sheet_path = os.path.join(RENDER_DIR, "shako_prussline1813_vistas.png")
sh.save_render(sheet_path, scene=scene)
print("OK sheet", sheet_path)

# ---------------------------------------------------------------- stats, save, export
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
