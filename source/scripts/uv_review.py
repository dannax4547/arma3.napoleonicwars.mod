# Phase 6 UV review (read-only on the mesh): bounds, texel density per mesh island, UV overlaps between and
# within islands, and a UV layout image.
# Usage: blender -b <file.blend> --python uv_review.py -- <object_name> <layout_png> <tex_size>
import bpy, bmesh, sys
import numpy as np
from mathutils.bvhtree import BVHTree

args = sys.argv[sys.argv.index("--") + 1:]
name, out_png, TEX = args[0], args[1], int(args[2])
me = bpy.data.objects[name].data
bm = bmesh.new()
bm.from_mesh(me)
uvl = bm.loops.layers.uv.active
bm.faces.ensure_lookup_table()

island_of, islands = {}, []
for f in bm.faces:
    if f.index in island_of:
        continue
    stack, comp = [f], []
    island_of[f.index] = len(islands)
    while stack:
        g = stack.pop(); comp.append(g)
        for v in g.verts:
            for h in v.link_faces:
                if h.index not in island_of:
                    island_of[h.index] = len(islands); stack.append(h)
    islands.append(comp)

def uv_area(f):
    p = [l[uvl].uv for l in f.loops]
    return 0.5 * sum(p[i].x * p[(i + 1) % len(p)].y - p[(i + 1) % len(p)].x * p[i].y for i in range(len(p)))

oob = [(f, l) for f in bm.faces for l in f.loops if not (0 <= l[uvl].uv.x <= 1 and 0 <= l[uvl].uv.y <= 1)]
print(f"UV out-of-bounds corners: {len(oob)}")
for f, l in oob[:10]:
    c = f.calc_center_median()
    print(f"   oob uv=({l[uvl].uv.x:.4f},{l[uvl].uv.y:.4f}) face at ({c.x:.3f},{c.y:.3f},{c.z:.3f}) material={me.materials[f.material_index].name}")
mats = [m.name if m else "-" for m in me.materials]
trees = []
for i, comp in enumerate(islands):
    a3 = sum(f.calc_area() for f in comp)
    auv = sum(abs(uv_area(f)) for f in comp) * TEX * TEX
    neg = sum(1 for f in comp if uv_area(f) < 0)
    dom = max({mats[f.material_index] for f in comp}, key=lambda m: sum(1 for f in comp if mats[f.material_index] == m))
    print(f"UVISLAND {i} {dom:24s} texel={((auv / a3) ** 0.5 if a3 > 0 else 0):7.0f} px/m  faces={len(comp)}  mirrored_faces={neg}")
    verts, polys, owners = [], [], []
    for f in comp:
        base = len(verts)
        for l in f.loops:
            verts.append((l[uvl].uv.x, l[uvl].uv.y, 0.0))
        polys.append(list(range(base, base + len(f.loops))))
        owners.append(f)
    trees.append((BVHTree.FromPolygons(verts, polys, epsilon=0.0), owners))

def real_overlap(fa, fb):
    """BVH overlap is conservative for coplanar 2D polygons; confirm with a polygon-area test on a coarse raster."""
    def poly(f):
        return [(l[uvl].uv.x, l[uvl].uv.y) for l in f.loops]
    pa, pb = poly(fa), poly(fb)
    xs = [p[0] for p in pa + pb]; ys = [p[1] for p in pa + pb]
    x0, x1, y0, y1 = max(min(p[0] for p in pa), min(p[0] for p in pb)), min(max(p[0] for p in pa), max(p[0] for p in pb)), \
                     max(min(p[1] for p in pa), min(p[1] for p in pb)), min(max(p[1] for p in pa), max(p[1] for p in pb))
    if x1 <= x0 or y1 <= y0:
        return False
    def inside(pt, pol):
        c, n = False, len(pol)
        for i in range(n):
            (xa, ya), (xb, yb) = pol[i], pol[(i + 1) % n]
            if (ya > pt[1]) != (yb > pt[1]) and pt[0] < (xb - xa) * (pt[1] - ya) / (yb - ya + 1e-30) + xa:
                c = not c
        return c
    for gx in np.linspace(x0, x1, 7)[1:-1]:
        for gy in np.linspace(y0, y1, 7)[1:-1]:
            if inside((gx, gy), pa) and inside((gx, gy), pb):
                return True
    return False

cross = []
for i in range(len(islands)):
    for j in range(i + 1, len(islands)):
        hits = [(a, b) for a, b in trees[i][0].overlap(trees[j][0]) if real_overlap(trees[i][1][a], trees[j][1][b])]
        if hits:
            cross.append((i, j, len(hits)))
print(f"UV overlaps between islands: {len(cross)}")
for i, j, n in cross:
    print(f"   islands {i} x {j}: {n} face pairs")
self_ov = 0
for i, (tree, owners) in enumerate(trees):
    for a, b in tree.overlap(tree):
        if a < b and not (set(v.index for v in owners[a].verts) & set(v.index for v in owners[b].verts)) and real_overlap(owners[a], owners[b]):
            self_ov += 1
print(f"UV self-overlaps inside islands: {self_ov}")

img = np.full((TEX, TEX, 3), 0.12, np.float32)
for f in bm.faces:
    pts = [(l[uvl].uv.x * (TEX - 1), (1 - l[uvl].uv.y) * (TEX - 1)) for l in f.loops]
    for k in range(len(pts)):
        (xa, ya), (xb, yb) = pts[k], pts[(k + 1) % len(pts)]
        n = int(max(abs(xb - xa), abs(yb - ya))) + 1
        xs = np.clip(np.linspace(xa, xb, n).astype(int), 0, TEX - 1)
        ys = np.clip(np.linspace(ya, yb, n).astype(int), 0, TEX - 1)
        img[ys, xs] = (0.95, 0.85, 0.3)
rgba = np.concatenate([img[::-1], np.ones((TEX, TEX, 1), np.float32)], axis=2)
im = bpy.data.images.new("uv_layout", TEX, TEX, alpha=False)
im.pixels.foreach_set(rgba.ravel())
im.file_format = 'PNG'
im.save(filepath=out_png)
print("OK layout", out_png)
