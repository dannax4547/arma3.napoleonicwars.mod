# Phase 5 technical mesh review (read-only): opens a .blend and inspects one mesh object.
# Usage: blender -b <file.blend> --python mesh_review.py -- <object_name>
# Checks: islands, orientation (signed volume), boundary / non-manifold edges, duplicate vertices,
# zero-area faces, loose geometry, face sizes, intersections between and within islands (BVH), transforms, counts.
import bpy, bmesh, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

name = sys.argv[sys.argv.index("--") + 1]
ob = bpy.data.objects[name]
me = ob.data
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
mats = [m.name if m else "-" for m in me.materials]

# islands (face connectivity through shared vertices)
island_of, islands = {}, []
for f in bm.faces:
    if f.index in island_of:
        continue
    stack, comp = [f], []
    island_of[f.index] = len(islands)
    while stack:
        g = stack.pop()
        comp.append(g)
        for v in g.verts:
            for h in v.link_faces:
                if h.index not in island_of:
                    island_of[h.index] = len(islands)
                    stack.append(h)
    islands.append(comp)

def tris_of(faces):
    t = []
    for f in faces:
        vs = [v.co for v in f.verts]
        for k in range(1, len(vs) - 1):
            t.append((vs[0], vs[k], vs[k + 1]))
    return t

print(f"REVIEW object={name} verts={len(bm.verts)} faces={len(bm.faces)} islands={len(islands)}")
print(f"TRANSFORM loc={tuple(round(x, 6) for x in ob.location)} rot={tuple(round(x, 6) for x in ob.rotation_euler)} scale={tuple(round(x, 6) for x in ob.scale)}")

bad_orient = 0
for i, comp in enumerate(islands):
    vol = sum(a.dot(b.cross(c)) for a, b, c in tris_of(comp)) / 6.0
    edges = {e for f in comp for e in f.edges}
    boundary = sum(1 for e in edges if e.is_boundary)
    nonman = sum(1 for e in edges if not e.is_manifold and not e.is_boundary)
    mat_count = {}
    for f in comp:
        mat_count[mats[f.material_index]] = mat_count.get(mats[f.material_index], 0) + 1
    dom = max(mat_count, key=mat_count.get)
    c = sum((f.calc_center_median() for f in comp), Vector()) / len(comp)
    ntri = len(tris_of(comp))
    if vol <= 0:
        bad_orient += 1
    print(f"ISLAND {i:3d} tris={ntri:5d} material={dom:24s} volume={vol * 1e6:9.3f} cm3 boundary_edges={boundary} nonmanifold_edges={nonman} centre=({c.x:.3f},{c.y:.3f},{c.z:.3f})")
print(f"M1 islands with non-positive volume (inverted or open): {bad_orient}")

# duplicate vertices
kd = KDTree(len(bm.verts))
for v in bm.verts:
    kd.insert(v.co, v.index)
kd.balance()
dup_same, dup_cross = 0, 0
vert_island = {}
for f in bm.faces:
    for v in f.verts:
        vert_island[v.index] = island_of[f.index]
for v in bm.verts:
    for co, j, dist in kd.find_range(v.co, 1e-6):
        if j > v.index:
            if vert_island.get(j) == vert_island.get(v.index):
                dup_same += 1
            else:
                dup_cross += 1
print(f"M2 duplicate vertices (<0.001 mm): same island={dup_same}  between islands={dup_cross}")

all_edges = list(bm.edges)
print(f"M3 boundary edges={sum(1 for e in all_edges if e.is_boundary)} non-manifold edges={sum(1 for e in all_edges if not e.is_manifold and not e.is_boundary)}")
zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
loose_v = sum(1 for v in bm.verts if not v.link_faces)
loose_e = sum(1 for e in bm.edges if not e.link_faces)
print(f"M4 zero-area faces={zero} loose verts={loose_v} loose edges={loose_e} max verts/face={max(len(f.verts) for f in bm.faces)}")

# intersections
bvhs = [BVHTree.FromPolygons([v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in comp]) for comp in islands]
cross = []
for i in range(len(islands)):
    for j in range(i + 1, len(islands)):
        pairs = bvhs[i].overlap(bvhs[j])
        if pairs:
            cross.append((i, j, len(pairs)))
def fc(f):
    c = f.calc_center_median()
    return f"({c.x:.4f},{c.y:.4f},{c.z:.4f})"

print(f"M5 island pairs that intersect: {len(cross)}")
for i, j, n in cross[:40]:
    pairs = bvhs[i].overlap(bvhs[j])
    print(f"   islands {i} x {j}: {n} triangle pairs; e.g. " + "; ".join(f"{fc(islands[i][a])}~{fc(islands[j][b])}" for a, b in pairs[:3]))
self_hits = 0
for i, comp in enumerate(islands):
    faces = [[v.index for v in f.verts] for f in comp]
    tree = BVHTree.FromPolygons([v.co.copy() for v in bm.verts], faces)
    for a, b in tree.overlap(tree):
        if a < b and not (set(faces[a]) & set(faces[b])):
            self_hits += 1
            print(f"   self-hit island {i}: {fc(comp[a])} ~ {fc(comp[b])}")
print(f"M5 self-intersections inside islands (non-adjacent face pairs): {self_hits}")
for f in bm.faces:
    if f.calc_area() < 1e-10:
        print(f"   zero-area face island {island_of[f.index]} verts={len(f.verts)} at {fc(f)}")

per_mat = {}
for f in bm.faces:
    per_mat[mats[f.material_index]] = per_mat.get(mats[f.material_index], 0) + len(f.verts) - 2
print(f"M7 triangles total={sum(per_mat.values())} by material: " + ", ".join(f"{k}={v}" for k, v in sorted(per_mat.items(), key=lambda x: -x[1])))
