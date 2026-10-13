# Phase 6 (uniform): UV layout of HCL_U_Pruss1813_01_LOD0, one 2048 texture for every garment piece (Arma "camo").
# - garment faces: angle-based projection into charts, packed with a margin, then scaled to free one corner
# - buttons: all mapped onto one small brass square in that corner (identical pieces, identical texels)
# - hands: keep the official template UVs (they use the skin texture of the identity, not this one)
# The mesh itself is not changed. Saves the .blend in place and writes a layout PNG.
#   blender -b <LOD0.blend> --python uv_uniforme_pruss.py -- <layout.png>
import bpy, bmesh, sys, math
from mathutils import Vector

OUT_PNG = sys.argv[sys.argv.index("--") + 1:][0]
ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = ob["hcl_partes"].split(",")
mats = [m.name for m in ob.data.materials]
BTN, HANDS = parts.index("botoes"), parts.index("maos_template")
SCALE, CORNER = 0.94, (0.950, 0.950, 0.995, 0.995)          # garment charts in [0, 0.94]^2, buttons in the corner

for o in bpy.context.scene.objects:
    o.select_set(False)
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
ob.hide_set(False)

# 1. select garment faces (not hands, not buttons) and project
bpy.ops.object.mode_set(mode="EDIT")
bm = bmesh.from_edit_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
for f in bm.faces:
    f.select = f[PL] not in (BTN, HANDS)
bmesh.update_edit_mesh(ob.data)
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0,
                         correct_aspect=True, scale_to_bounds=False)
try:
    bpy.ops.uv.pack_islands(rotate=True, margin=0.004, shape_method="CONCAVE")
except TypeError:                                            # older API without shape_method
    bpy.ops.uv.pack_islands(rotate=True, margin=0.004)
bm = bmesh.from_edit_mesh(ob.data)
uv = bm.loops.layers.uv.active
PL = bm.faces.layers.int.get("hcl_part")
for f in bm.faces:
    if f[PL] in (BTN, HANDS):
        continue
    for l in f.loops:
        l[uv].uv = l[uv].uv * SCALE

# 2. buttons: planar projection of each dome onto the same corner square (centre = dome centre)
faces_by_island = {}
for f in bm.faces:
    if f[PL] != BTN:
        continue
    faces_by_island.setdefault(None, []).append(f)
btn_faces = faces_by_island.get(None, [])
# split buttons into connected pieces
seen, pieces = set(), []
for f in btn_faces:
    if f.index in seen:
        continue
    stack, comp = [f], []
    seen.add(f.index)
    while stack:
        g = stack.pop()
        comp.append(g)
        for v in g.verts:
            for h in v.link_faces:
                if h.index not in seen and h[PL] == BTN:
                    seen.add(h.index); stack.append(h)
    pieces.append(comp)
cu0, cv0, cu1, cv1 = CORNER
for comp in pieces:
    vs = {v for f in comp for v in f.verts}
    c = sum((v.co for v in vs), Vector()) / len(vs)
    n = sum((f.normal for f in comp), Vector()).normalized()
    t = n.orthogonal().normalized(); b = n.cross(t)
    r = max((v.co - c).length for v in vs) or 1.0
    for f in comp:
        for l in f.loops:
            d = l.vert.co - c
            l[uv].uv = (cu0 + (cu1 - cu0) * (0.5 + 0.5 * d.dot(t) / r), cv0 + (cv1 - cv0) * (0.5 + 0.5 * d.dot(b) / r))
bmesh.update_edit_mesh(ob.data)
bpy.ops.object.mode_set(mode="OBJECT")

# 3. checks: bounds, area use, texel density per part (px per metre at 2048)
me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
uv = bm.loops.layers.uv.active
PL = bm.faces.layers.int.get("hcl_part")
oob, dens = 0, {}
used = 0.0
for f in bm.faces:
    if f[PL] == HANDS:
        continue
    us = [l[uv].uv.copy() for l in f.loops]
    oob += sum(1 for u in us if not (0 <= u.x <= 1 and 0 <= u.y <= 1))
    a3 = f.calc_area()
    a2 = 0.0
    for k in range(1, len(us) - 1):
        a2 += abs((us[k] - us[0]).cross(us[k + 1] - us[0])) / 2
    if f[PL] != BTN:
        used += a2
        if a3 > 1e-8:
            d = dens.setdefault(parts[f[PL]], [0.0, 0.0])
            d[0] += a2; d[1] += a3
print(f"UVU out-of-bounds corners: {oob}")
print(f"UVU texture area used by garment charts: {used * 100:.1f}% (charts limited to {SCALE * SCALE * 100:.0f}%)")
for name, (a2, a3) in sorted(dens.items()):
    print(f"UVU density {name:18s} {math.sqrt(a2 / a3) * 2048:7.0f} px/m")
print(f"UVU buttons: {len(pieces)} domes share the corner square {CORNER}")

# 4. layout image
W = 2048
img = bpy.data.images.new("layout", W, W, alpha=False)
import numpy as np
px = np.full((W, W, 4), 1.0, np.float32)
px[..., :3] = 0.12
cols = [np.array(c, np.float32) for c in ((0.9, 0.3, 0.3), (0.3, 0.8, 0.3), (0.3, 0.5, 0.95), (0.95, 0.8, 0.2),
                                          (0.8, 0.4, 0.9), (0.3, 0.9, 0.9), (0.95, 0.55, 0.2), (0.6, 0.6, 0.6))]
for f in bm.faces:
    if f[PL] == HANDS:
        continue
    us = [(l[uv].uv.x * W, l[uv].uv.y * W) for l in f.loops]
    for k in range(1, len(us) - 1):
        (x0, y0), (x1, y1), (x2, y2) = us[0], us[k], us[k + 1]
        xmin, xmax = int(max(0, min(x0, x1, x2))), int(min(W - 1, max(x0, x1, x2)) + 1)
        ymin, ymax = int(max(0, min(y0, y1, y2))), int(min(W - 1, max(y0, y1, y2)) + 1)
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(det) < 1e-9 or xmax <= xmin or ymax <= ymin:
            continue
        gy, gx = np.mgrid[ymin:ymax, xmin:xmax].astype(np.float32) + 0.5
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / det
        w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / det
        ins = (w0 >= 0) & (w1 >= 0) & (1 - w0 - w1 >= 0)
        px[ymin:ymax, xmin:xmax, :3][ins] = cols[f[PL] % len(cols)]
img.pixels.foreach_set(px.ravel())
img.filepath_raw = OUT_PNG
img.file_format = "PNG"
img.save()
bpy.ops.wm.save_mainfile()
print("OK", OUT_PNG)
