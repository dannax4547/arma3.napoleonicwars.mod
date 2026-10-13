# Phase 3 (blockout) of the Prussian shako: simple shapes, flat identification colours, NO UVs or final textures.
# Fitted on the official Arma 3 Samples character, using the official sample cap as the head-band reference.
# Usage:
#   blender -b --factory-startup --python blockout_shako.py -- <Test_Character_01 dir> <out.blend> <render_dir> <photo_R2.png>
# Spec: docs/specs/shako_prussiano_infantaria.md (v1.1). Every assumption is printed and documented in the report.
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR, PHOTO = args[:4]

# ---------------------------------------------------------------- spec values (photo R2, base width 0.180 m assumed)
SPEC_BASE_W, SPEC_H, SPEC_TOP_W = 0.180, 0.200, 0.243
SPEC = dict(band=0.025, binding=0.010, cockade_r=0.022, cockade_z=0.175, loop_w=0.014, loop_bottom=0.125,
            cipher_w=0.081, cipher_h=0.077, cipher_z=0.081, button_r=0.007, button_z=0.012,
            visor_chord=0.162)
DEPTH_RATIO = 1.13            # ASSUMPTION (no side view): depth = 1.13 x width
VISOR_LEN = 0.068             # ASSUMPTION (no side view): chosen so the front projection matches photo R2 (~0.06 m)
VISOR_DROP = math.radians(55)  # ASSUMPTION (no side view)
TILT = math.radians(8)        # ASSUMPTION: shako sits slightly lower at the back than at the front
WALL, CLEAR = 0.004, 0.002    # felt thickness, clearance over the head band
N = 40

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- official references (read-only from Arma 3 Samples)
def mesh_from_lod(name, lod):
    pts = [to_blender(p) for p in lod["points"]]
    proxy = set()
    for sname, blob in lod["selections"].items():
        if sname.lower().startswith("proxy:"):
            proxy.update(i for i, b in enumerate(blob) if b)
    faces = [f[::-1] for f in lod["faces"] if not any(i in proxy for i in f)]
    used = sorted({i for f in faces for i in f})
    remap = {old: new for new, old in enumerate(used)}
    me = bpy.data.meshes.new(name)
    me.from_pydata([pts[i] for i in used], [], [[remap[i] for i in f] for f in faces])
    me.update()
    for p in me.polygons:
        p.use_smooth = True
    return me

col_ref = bpy.data.collections.new("REF_Arma3Samples")
col_bo = bpy.data.collections.new("HCL_Shako_Blockout")
scene.collection.children.link(col_ref)
scene.collection.children.link(col_bo)
body = bpy.data.objects.new("REF_corpo_A3_character_example", mesh_from_lod("REF_body", read_mlod(os.path.join(SAMPLES, "A3_character_example.p3d"))[0]))
cap_lod = read_mlod(os.path.join(SAMPLES, "A3_headgear_example.p3d"))[0]
cap = bpy.data.objects.new("REF_bone_A3_headgear_example", mesh_from_lod("REF_cap", cap_lod))
col_ref.objects.link(body)
col_ref.objects.link(cap)

# ---------------------------------------------------------------- head band from the official cap
cp = np.array([to_blender(p) for p in cap_lod["points"]])
zmin = cp[:, 2].min()
crown = cp[(cp[:, 2] > zmin + 0.02) & (cp[:, 2] < zmin + 0.10) & (cp[:, 1] > -0.115)]   # crown wall, visor excluded
head_hw = max(abs(crown[:, 0].min()), crown[:, 0].max())
y_front, y_back = crown[:, 1].min(), crown[:, 1].max()
head_cy, head_hd = (y_front + y_back) / 2, (y_back - y_front) / 2
z_forehead = cp[(cp[:, 1] < y_front + 0.02) & (cp[:, 1] > -0.115), 2].min()
z_head_top = cp[:, 2].max()
print(f"FIT head band from official cap: half-width={head_hw:.3f} centre_y={head_cy:.3f} half-depth={head_hd:.3f} "
      f"forehead_z={z_forehead:.3f} head_top_z~{z_head_top:.3f}")

base_hw = max(SPEC_BASE_W / 2, head_hw + WALL + CLEAR)
k = base_hw / (SPEC_BASE_W / 2)                    # uniform scale of the spec to fit the official head
base_hd = max(base_hw * DEPTH_RATIO, head_hd + WALL + CLEAR)
H = SPEC_H * k
top_hw = SPEC_TOP_W / 2 * k
top_hd = top_hw * base_hd / base_hw
S = {key: v * k for key, v in SPEC.items()}
print(f"FIT scale k={k:.4f}  H={H:.3f}  base={2 * base_hw:.3f}x{2 * base_hd:.3f}  top={2 * top_hw:.3f}x{2 * top_hd:.3f}")

def rx(z): return base_hw + (top_hw - base_hw) * z / H
def ry(z): return base_hd + (top_hd - base_hd) * z / H
def P(theta, z, off=0.0):
    return Vector(((rx(z) + off) * math.sin(theta), (ry(z) + off) * math.cos(theta), z))
def wall_normal(theta, z):
    n = Vector((math.sin(theta) / rx(z), math.cos(theta) / ry(z), 0)).normalized()
    slope = (top_hw - base_hw) / H
    return (n - Vector((0, 0, slope))).normalized()
def th(i):
    return 2 * math.pi * i / N

# ---------------------------------------------------------------- mesh helpers (closed, manifold parts)
def finish(name, bm, colour, rough=0.6, metal=0.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    ob = bpy.data.objects.new(name, me)
    col_bo.objects.link(ob)
    m = bpy.data.materials.new("MAT_" + name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Base Color"].default_value = (*colour, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    me.materials.append(m)
    return ob

def quads(bm, rows, closed_u=True, closed_v=False):
    nr, nc = len(rows), len(rows[0])
    for j in range(nr - 1 + (1 if closed_v else 0)):
        for i in range(nc - (0 if closed_u else 1)):
            a, b = rows[j][i], rows[j][(i + 1) % nc]
            c, d = rows[(j + 1) % nr][(i + 1) % nc], rows[(j + 1) % nr][i]
            bm.faces.new((a, b, c, d))

def fan(bm, centre, ring):
    c = bm.verts.new(centre)
    for i in range(len(ring)):
        bm.faces.new((c, ring[i], ring[(i + 1) % len(ring)]))

def lathe_ring(name, profile, colour, **kw):
    bm = bmesh.new()
    rows = [[bm.verts.new(P(th(i), z, off)) for i in range(N)] for z, off in profile]
    quads(bm, rows, closed_u=True, closed_v=True)
    return finish(name, bm, colour, **kw)

def slab(name, top, normals, t, colour, **kw):
    bm = bmesh.new()
    T = [[bm.verts.new(p) for p in row] for row in top]
    B = [[bm.verts.new(p - n * t) for p, n in zip(row, nrow)] for row, nrow in zip(top, normals)]
    quads(bm, T, closed_u=False)
    quads(bm, B, closed_u=False)
    R, C = len(top), len(top[0])
    for j in range(R - 1):
        for col in (0, C - 1):
            bm.faces.new((T[j][col], T[j + 1][col], B[j + 1][col], B[j][col]))
    for i in range(C - 1):
        for row in (0, R - 1):
            bm.faces.new((T[row][i], T[row][i + 1], B[row][i + 1], B[row][i]))
    return finish(name, bm, colour, **kw)

def disk(name, centre, normal, r, t, colour, segs=24, **kw):
    n = normal.normalized()
    u = n.cross(Vector((0, 0, 1)))
    u = u.normalized() if u.length > 1e-6 else Vector((1, 0, 0))
    v = n.cross(u)
    bm = bmesh.new()
    r0 = [bm.verts.new(centre + (u * math.cos(2 * math.pi * a / segs) + v * math.sin(2 * math.pi * a / segs)) * r) for a in range(segs)]
    r1 = [bm.verts.new(p.co + n * t) for p in r0]
    quads(bm, [r0, r1])
    fan(bm, centre, r0)
    fan(bm, centre + n * t, r1)
    return finish(name, bm, colour, **kw)

def strip_on_wall(name, half_w, z0, z1, base_off, t, colour, rows=6, cols=4, **kw):
    top, nrm = [], []
    for j in range(rows + 1):
        z = z0 + (z1 - z0) * j / rows
        row, nrow = [], []
        for i in range(cols + 1):
            s = -half_w + 2 * half_w * i / cols
            theta = math.pi + s / rx(z)
            row.append(P(theta, z, base_off + t))
            nrow.append(wall_normal(theta, z))
        top.append(row)
        nrm.append(nrow)
    return slab(name, top, nrm, t, colour, **kw)

# ---------------------------------------------------------------- blockout parts (local space: base centre at origin, front -Y)
FELT, PATENT, BRASS = (0.020, 0.022, 0.028), (0.008, 0.008, 0.010), (0.70, 0.52, 0.20)
parts = []
bm = bmesh.new()
outer = [[bm.verts.new(P(th(i), z)) for i in range(N)] for z in (0.0, S["band"], H - S["binding"], H)]
inner = [[bm.verts.new(P(th(i), z, -WALL)) for i in range(N)] for z in (H - WALL, 0.0)]
quads(bm, outer)
quads(bm, inner)
quads(bm, [inner[-1], outer[0]])                  # bottom rim
fan(bm, (0, 0, H), outer[-1])
fan(bm, (0, 0, H - WALL), inner[0])
parts.append(finish("HCL_BO_Corpo_feltro", bm, FELT, rough=0.9))
# note: crown and inner ceiling are fans; the felt body is a closed shell

parts.append(lathe_ring("HCL_BO_Faixa_envernizada", [(0.0, 0.0015), (S["band"], 0.0015), (S["band"], -0.001), (0.0, -0.001)], PATENT, rough=0.15))
parts.append(lathe_ring("HCL_BO_Debrum_topo", [(H - S["binding"], 0.0015), (H, 0.0015), (H, -0.003), (H - S["binding"], -0.001)], PATENT, rough=0.35))

# visor (squarish front, steep: ASSUMED angle/length)
half_span = math.asin(min(0.99, S["visor_chord"] / 2 / base_hw))
M, K = 16, 4
top, nrm = [], []
for kk in range(K + 1):
    row, nrow = [], []
    for m in range(M + 1):
        phi = -half_span + 2 * half_span * m / M
        theta = math.pi + phi
        L = max(0.004, VISOR_LEN * math.cos(phi / half_span * math.pi / 2) ** 0.5)
        out_h = Vector((math.sin(theta) / base_hw, math.cos(theta) / base_hd, 0)).normalized()
        d = out_h * math.cos(VISOR_DROP) - Vector((0, 0, 1)) * math.sin(VISOR_DROP)
        row.append(P(theta, 0.004, -0.002) + d * L * kk / K)
        nrow.append(out_h * math.sin(VISOR_DROP) + Vector((0, 0, 1)) * math.cos(VISOR_DROP))
    top.append(row)
    nrm.append(nrow)
parts.append(slab("HCL_BO_Pala", top, nrm, 0.003, PATENT, rough=0.15))

cz = S["cockade_z"]
parts.append(disk("HCL_BO_Cocar", P(math.pi, cz, 0.001), wall_normal(math.pi, cz), S["cockade_r"], 0.004, (0.80, 0.80, 0.78), rough=0.7))
parts.append(disk("HCL_BO_Cocar_centro", P(math.pi, cz, 0.001) + wall_normal(math.pi, cz) * 0.004, wall_normal(math.pi, cz), S["cockade_r"] * 0.45, 0.001, (0.02, 0.02, 0.02), rough=0.7))
parts.append(strip_on_wall("HCL_BO_Presilha", S["loop_w"] / 2, S["loop_bottom"], cz, 0.0005, 0.002, (0.80, 0.58, 0.12), rough=0.7))
parts.append(strip_on_wall("HCL_BO_Cifra_FWR_placeholder", S["cipher_w"] / 2, S["cipher_z"] - S["cipher_h"] / 2,
                           S["cipher_z"] + S["cipher_h"] / 2, 0.0005, 0.002, BRASS, rough=0.35, metal=1.0))
for side, sgn in (("E", 1), ("D", -1)):
    theta = math.pi + sgn * math.radians(80)
    parts.append(disk(f"HCL_BO_Botao_{side}", P(theta, S["button_z"], 0.0015), wall_normal(theta, S["button_z"]),
                      S["button_r"], 0.004, BRASS, rough=0.35, metal=1.0))

# ---------------------------------------------------------------- place on the official head (root empty)
root = bpy.data.objects.new("HCL_Shako_Root", None)
col_bo.objects.link(root)
for p_ in parts:
    p_.parent = root
base_centre = Vector((0.0, head_cy, z_forehead - 0.004))
root.matrix_world = Matrix.Translation(base_centre) @ Matrix.Rotation(-TILT, 4, 'X')
bpy.context.view_layer.update()
print(f"PLACE base centre={tuple(round(v, 3) for v in base_centre)} tilt={math.degrees(TILT):.1f} deg (back lower)")
print(f"CHECK crown inner top z~{(root.matrix_world @ Vector((0, 0, H - WALL))).z:.3f} vs head top {z_head_top:.3f}")

tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in parts)
print(f"STATS blockout parts={len(parts)} tris={tris}")
for o in parts:
    print(f"PART {o.name:32s} tris={sum(len(p.vertices) - 2 for p in o.data.polygons)}")

# ---------------------------------------------------------------- materials for references
def ref_mat(ob, colour, alpha=1.0):
    m = bpy.data.materials.new("MAT_" + ob.name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Base Color"].default_value = (*colour, 1)
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Alpha"].default_value = alpha
    ob.data.materials.append(m)
ref_mat(body, (0.55, 0.50, 0.46))
ref_mat(cap, (0.75, 0.08, 0.08))

# approximate head for presentation only (the official head is a game proxy, not included in the Samples):
# ellipsoid spanning the official cap's head band and head top down to the official neck (z ~0.57)
hb = bmesh.new()
bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_head_approx")
hb.to_mesh(hme)
hb.free()
for p in hme.polygons:
    p.use_smooth = True
head = bpy.data.objects.new("REF_cabeca_APROXIMADA_nao_oficial", hme)
head.scale = (head_hw - 0.006, head_hd - 0.004, (z_head_top - 0.57) / 2 - 0.004)
head.location = (0, head_cy, (z_head_top + 0.57) / 2)
col_ref.objects.link(head)
ref_mat(head, (0.66, 0.58, 0.52))

# ---------------------------------------------------------------- render setup
target = bpy.data.objects.new("CamTarget", None)
col_ref.objects.link(target)
cam_d = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_d)
col_ref.objects.link(cam)
tc = cam.constraints.new('TRACK_TO'); tc.target, tc.track_axis, tc.up_axis = target, 'TRACK_NEGATIVE_Z', 'UP_Y'
scene.camera = cam
for nm, loc, e in (("Key", (-1.2, -1.5, 2.2), 3.5), ("Fill", (1.5, -0.8, 1.0), 1.2), ("Rim", (0.5, 1.6, 1.8), 2.5)):
    ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = e; ld.angle = math.radians(8)
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
scene.cycles.samples = 32
try:
    scene.cycles.use_denoising = True
except Exception:
    pass
scene.view_settings.view_transform = 'Standard'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
os.makedirs(RENDER_DIR, exist_ok=True)

def render(name, az, el, dist, tgt, res=700, ortho=None, lens=85):
    target.location = tgt
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(tgt) + dist * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    cam_d.type = 'ORTHO' if ortho else 'PERSP'
    if ortho:
        cam_d.ortho_scale = ortho
    cam_d.lens = lens
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("OK render", scene.render.filepath)
    return scene.render.filepath

centre = root.matrix_world @ Vector((0, 0, H * 0.45))
cap.hide_render = True                       # official cap only appears in the fit-check views
ortho = [render("orto_frente", 0, 0, 2, centre, ortho=0.46), render("orto_lado", 90, 0, 2, centre, ortho=0.46),
         render("orto_costas", 180, 0, 2, centre, ortho=0.46), render("orto_topo", 0, 89.9, 2, centre, ortho=0.46)]
render("perspectiva_3-4", 35, 12, 1.6, root.matrix_world @ Vector((0, 0, -0.05)), res=800)

# fit check: shako translucent, official cap (red) visible inside
for o in parts:
    b = next(n for n in o.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Alpha"].default_value = 0.22
cap.hide_render, head.hide_render = False, True
render("encaixe_lado", 90, 0, 2, centre, ortho=0.46)
render("encaixe_frente", 0, 0, 2, centre, ortho=0.46)
cap.hide_render, head.hide_render = True, False
for o in parts:
    b = next(n for n in o.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs["Alpha"].default_value = 1.0

# silhouette comparison with photo R2: shako upright at the origin, front orthographic, same metres/pixel
saved = root.matrix_world.copy()
root.matrix_world = Matrix.Identity(4)
body.hide_render = cap.hide_render = head.hide_render = True
bpy.context.view_layer.update()
RES, OS, TZ = 700, 0.40, 0.13
cmp_path = render("comparacao_render", 0, 0, 2, (0, 0, TZ), res=RES, ortho=OS)
root.matrix_world = saved
body.hide_render = head.hide_render = False

def load_rgb(p):
    im = bpy.data.images.load(p, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].copy()

def resize(img, nw, nh):
    h, w, _ = img.shape
    xs = np.clip((np.arange(nw) + 0.5) * w / nw - 0.5, 0, w - 1)
    ys = np.clip((np.arange(nh) + 0.5) * h / nh - 0.5, 0, h - 1)
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (xs - x0)[None, :, None], (ys - y0)[:, None, None]
    top_ = img[y0][:, x0] * (1 - fx) + img[y0][:, x1] * fx
    bot_ = img[y1][:, x0] * (1 - fx) + img[y1][:, x1] * fx
    return top_ * (1 - fy) + bot_ * fy

photo = load_rgb(PHOTO)
rend = load_rgb(cmp_path)
m_per_px_photo = 0.000933 * k            # photo scale from the spec, times the fit scale
f = m_per_px_photo / (OS / RES)
photo_s = resize(photo, int(photo.shape[1] * f), int(photo.shape[0] * f))
photo_base = int(325 * f)                # base row of the shako in the photo (spec §4.1)
rend_base = int(RES / 2 + TZ / (OS / RES))
off_p, off_r = max(0, rend_base - photo_base), max(0, photo_base - rend_base)
Hc = max(photo_s.shape[0] + off_p, RES + off_r)
canvas = np.full((Hc, photo_s.shape[1] + 20 + RES, 3), 1.0, np.float32)
canvas[off_p:off_p + photo_s.shape[0], :photo_s.shape[1]] = photo_s
canvas[off_r:off_r + RES, photo_s.shape[1] + 20:] = rend
base_row = max(photo_base, rend_base)
top_row = base_row - int(H / (OS / RES))
for r_ in (base_row, top_row):
    canvas[r_:r_ + 2, :] = (0.9, 0.1, 0.1)
rgba = np.concatenate([canvas[::-1], np.ones(canvas.shape[:2] + (1,), np.float32)], axis=2)
img = bpy.data.images.new("cmp", canvas.shape[1], canvas.shape[0], alpha=False)
img.pixels.foreach_set(rgba.ravel())
cmp_out = os.path.join(RENDER_DIR, "blockout_comparacao_foto_R2.png")
img.save_render(cmp_out, scene=scene)
print("OK compare", cmp_out)

# 2x2 sheet of the orthographic views
tiles = [load_rgb(p) for p in ortho]
sheet = np.concatenate([np.concatenate([tiles[0], tiles[1]], axis=1), np.concatenate([tiles[2], tiles[3]], axis=1)], axis=0)
rgba = np.concatenate([sheet[::-1], np.ones(sheet.shape[:2] + (1,), np.float32)], axis=2)
img = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
img.pixels.foreach_set(rgba.ravel())
sheet_out = os.path.join(RENDER_DIR, "blockout_vistas_ortograficas.png")
img.save_render(sheet_out, scene=scene)
print("OK sheet", sheet_out)

os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("OK blend", OUT_BLEND)
