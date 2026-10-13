# Phase 5 technical review of a uniform mesh (read-only). Worn clothing is layered, so intersections between pieces
# are expected where one piece tucks under another; what matters is whether an intersection can be SEEN.
#   blender -b <file.blend> --python uniform_review.py -- <object> <Samples Test_Character_01 dir>
# U1 per-part counts, open and non-manifold edges     U2 duplicate vertices, zero-area faces, loose geometry
# U3 self-intersections inside each part             U4 intersections between parts: hidden vs visible
# U5 face orientation (normals of closed parts outward) U6 triangle budget
import bpy, bmesh, sys, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uniform_fit import Body

name, samples = sys.argv[sys.argv.index("--") + 1:][:2]
ob = bpy.data.objects[name]
me = ob.data
bm = bmesh.new()
bm.from_mesh(me)
bm.transform(ob.matrix_world)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
PART = bm.faces.layers.int.get("hcl_part")
parts = ob["hcl_partes"].split(",")
mats = [m.name for m in me.materials]
body = Body(os.path.join(samples, "A3_character_example.p3d"))
budget = 12000

print(f"REVIEW {name}: verts={len(bm.verts)} faces={len(bm.faces)} parts={len(parts)}")
print(f"TRANSFORM loc={tuple(round(x, 6) for x in ob.location)} rot={tuple(round(x, 6) for x in ob.rotation_euler)} "
      f"scale={tuple(round(x, 6) for x in ob.scale)}")

faces_of = {p: [f for f in bm.faces if f[PART] == p] for p in range(len(parts))}


def tris(fs):
    return sum(len(f.verts) - 2 for f in fs)


# U1
print("\nU1 parts")
for p, fs in faces_of.items():
    edges = {e for f in fs for e in f.edges}
    print(f"  {parts[p]:18s} tris={tris(fs):5d} open_edges={sum(e.is_boundary for e in edges):4d} "
          f"nonmanifold={sum(1 for e in edges if not e.is_manifold and not e.is_boundary)}")

# U2
kd = KDTree(len(bm.verts))
for v in bm.verts:
    kd.insert(v.co, v.index)
kd.balance()
dup = sum(1 for v in bm.verts for co, j, d in kd.find_range(v.co, 1e-6) if j > v.index)
zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
loose_v = sum(1 for v in bm.verts if not v.link_faces)
loose_e = sum(1 for e in bm.edges if not e.link_faces)
print(f"\nU2 duplicate vertices={dup} zero-area faces={zero} loose verts={loose_v} loose edges={loose_e} "
      f"max verts/face={max(len(f.verts) for f in bm.faces)}")

# U3
coords = [v.co.copy() for v in bm.verts]
trees = {p: BVHTree.FromPolygons(coords, [[v.index for v in f.verts] for f in fs]) for p, fs in faces_of.items()}
self_total = 0
for p, fs in faces_of.items():
    idx = [[v.index for v in f.verts] for f in fs]
    n = sum(1 for a, b in trees[p].overlap(trees[p]) if a < b and not (set(idx[a]) & set(idx[b])))
    self_total += n
    if n:
        print(f"  self-intersections in {parts[p]}: {n}")
print(f"\nU3 self-intersections inside parts: {self_total}")

# U4: visibility of each intersection (rays from the crossing point to the outside, ignoring views from below)
ALL = BVHTree.FromBMesh(bm)
DIRS = [Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
        for a in [2 * math.pi * k / 12 for k in range(12)] for b in (-0.4, 0.0, 0.5, 1.0)] + [Vector((0, 0, 1))]


def seen(p):
    for d in DIRS:
        o = p + d * 0.001
        if ALL.ray_cast(o, d, 3.0)[0] is None and body.bvh.ray_cast(o, d, 3.0)[0] is None:
            return True
    return False


print("\nU4 intersections between parts (pairs of triangles): hidden / VISIBLE")
vis_total, hid_total = 0, 0
for p in range(len(parts)):
    for q in range(p + 1, len(parts)):
        pairs = trees[p].overlap(trees[q])
        if not pairs:
            continue
        fp, fq = faces_of[p], faces_of[q]
        vis, ex = 0, None
        for a, b in pairs:
            m = (fp[a].calc_center_median() + fq[b].calc_center_median()) / 2
            if seen(m):
                vis += 1
                ex = ex or m
        hid_total += len(pairs) - vis
        vis_total += vis
        tag = f"  e.g. h {body.H(ex.z):.3f} x{ex.x:+.3f} y{ex.y:+.3f}" if ex else ""
        print(f"  {parts[p]:18s} x {parts[q]:18s} hidden {len(pairs) - vis:4d}  VISIBLE {vis:4d}{tag}")
print(f"U4 total: hidden {hid_total}, VISIBLE {vis_total}")

# U5: closed parts must have positive volume (outward normals); open parts are checked by their lining/outer probe
print("\nU5 orientation of closed parts (signed volume > 0 = outward)")
for p, fs in faces_of.items():
    edges = {e for f in fs for e in f.edges}
    if any(e.is_boundary for e in edges):
        continue
    vol = 0.0
    for f in fs:
        vs = [v.co for v in f.verts]
        for k in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[k].cross(vs[k + 1]))
    print(f"  {parts[p]:18s} volume {vol / 6 * 1e6:9.2f} cm3 {'OK' if vol > 0 else 'INVERTED'}")

# U6
tot = tris(bm.faces)
skin = sum(len(f.verts) - 2 for f in bm.faces if mats[f.material_index] == "HCL_pele_hl")
print(f"\nU6 triangles: total {tot} (garment {tot - skin}, official hands {skin}); proposed budget {budget}: "
      f"{'within' if tot <= budget else 'OVER by ' + str(tot - budget)}")
