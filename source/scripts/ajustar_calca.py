# Trousers seat/leg junction fix (R1) of HCL_U_Pruss1813_01_LOD0, in place (vertices moved; topology and UVs unchanged,
# so the texture variants stay valid; the AO must be baked again). Problem: the seat tube (calca_assento, down to
# h = 0.86) and the leg tubes (calca_perna_*, from h = 0.90) overlap over 4 cm with crossing eases (seat 10 mm, leg top
# 6 -> 18 mm), so the two surfaces cut each other along a ragged line around the thighs, seen in every render.
# New junction: the seat is the outer layer down to its hem; the leg tops stay at least GAP inside the seat; the seat's
# bottom ring lies HEM above the leg surface (a clean hem line instead of a ragged cut). Iterated, because moving the
# seat hem changes the seat surface the leg tops must stay under.
#   blender -b <LOD0.blend> --python ajustar_calca.py -- [dry]
import bpy, bmesh, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
DRY = "dry" in a
GROUND = -1.0069
GAP, HEM = 0.0025, 0.0015
H_LEG = 0.853                          # leg vertices above this height must be under the seat
H_SEAT_HEM = 0.875                     # seat vertices below this height form the hem ring

ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
bm.verts.ensure_lookup_table()
vpart = {}
for f in bm.faces:
    for v in f.verts:
        vpart.setdefault(v.index, set()).add(f[PL])
SEAT = PID["calca_assento"]
LEGS = {PID["calca_perna_E"], PID["calca_perna_D"]}
seat_f = [[v.index for v in f.verts] for f in bm.faces if f[PL] == SEAT]
leg_f = [[v.index for v in f.verts] for f in bm.faces if f[PL] in LEGS]
seat_v = sorted({i for f in seat_f for i in f})
leg_v = sorted({i for f in leg_f for i in f})
H = lambda p: p.z - GROUND
P = {i: bm.verts[i].co.copy() for i in seat_v + leg_v}


def tree(faces):
    """BVH over BOTH triangulations of every quad: the renderer and the exporter may split a non-planar quad along
    either diagonal (one diagonal hid a leg triangle that the other showed, 2026-10-11), so the checks use both."""
    idx = sorted({i for f in faces for i in f})
    tris = []
    for f in faces:
        if len(f) == 4:
            a, b, c, d = f
            tris += [(a, b, c), (a, c, d), (a, b, d), (b, c, d)]
        else:
            tris += [tuple(f[:1] + f[k:k + 2]) for k in range(1, len(f) - 1)]
    return BVHTree.FromPolygons([P.get(i, Vector()) if i in P else Vector() for i in range(max(idx) + 1)], tris)


def leg_out_of_seat(st):
    """Leg vertices above H_LEG and their signed distance to the seat (positive = outside the seat or closer than GAP)."""
    out = []
    for i in leg_v:
        p = P[i]
        if H(p) < H_LEG:
            continue
        loc, n, fi, d = st.find_nearest(p)
        if loc is None or d > 0.03:
            continue                    # crotch: far from any seat face, deep inside the hull
        s = (p - loc).dot(n)
        if s > -GAP + 1e-5:
            out.append((i, s, loc, n))
    return out


def cuts(st, lt):
    return len(st.overlap(lt))


st0, lt0 = tree(seat_f), tree(leg_f)
before = leg_out_of_seat(st0)
cut0 = cuts(st0, lt0)
print(f"ANTES: {len(before)} vertices do topo das pernas fora do assento ou a menos de {GAP*1000:.1f} mm "
      f"(max {max((s for _, s, _, _ in before), default=0)*1000:+.1f} mm); pares de faces assento x pernas se cortando: {cut0}")

moved_leg, moved_seat = set(), set()
# a) the seat hem rides on the ORIGINAL leg surface (the legs are only moved where they are above the hem)
for i in seat_v:
    p = P[i]
    if H(p) > H_SEAT_HEM:
        continue
    loc, n, fi, d = st0.find_nearest(p)
    hit = lt0.ray_cast(p + n * 0.03, -n, 0.06)        # leg surface under this seat point (from outside, inwards)
    if hit[0] is None:
        continue                                     # crotch bridge: no leg under it
    target = hit[0] + n * HEM
    if 1e-5 < (target - p).length <= 0.03:
        P[i] = target; moved_seat.add(i)
# hem vertices with no leg under them (the bridge over the crotch) take the displacement of their moved neighbours on
# the hem ring (inverse-distance mean of the 2 nearest), else the moved neighbours fold the faces between them
# (seen 2026-10-11 as a dark triangle in the baked AO at the front of the crotch)
from mathutils.kdtree import KDTree
hem = [i for i in seat_v if H(bm.verts[i].co) <= H_SEAT_HEM]
mv = [i for i in hem if i in moved_seat]
if mv:
    kdm = KDTree(len(mv))
    for k, i in enumerate(mv):
        kdm.insert(bm.verts[i].co, k)
    kdm.balance()
    n_br = 0
    for i in hem:
        if i in moved_seat:
            continue
        near = kdm.find_n(bm.verts[i].co, 2)
        wsum, dsum = 0.0, Vector()
        for co, k, d in near:
            w = 1.0 / max(d, 1e-4)
            dsum += (P[mv[k]] - bm.verts[mv[k]].co) * w
            wsum += w
        P[i] = bm.verts[i].co + dsum / wsum
        moved_seat.add(i); n_br += 1
    print(f"PONTE da virilha: {n_br} vertices da barra sem perna embaixo acompanham os vizinhos")
# a2) the seat ring just above the hem follows half of the hem's displacement (nearest hem vertex): with the hem moved
# up to 17 mm and this ring left in place, the quads between them folded (non-planar by several mm)
if mv:
    n_up = 0
    for i in seat_v:
        h0 = H(bm.verts[i].co)
        if not (H_SEAT_HEM < h0 < 0.905):
            continue
        co, k, d = kdm.find(bm.verts[i].co)
        P[i] = bm.verts[i].co + (P[mv[k]] - bm.verts[mv[k]].co) * 0.5
        moved_seat.add(i); n_up += 1
    print(f"ANEL acima da barra: {n_up} vertices acompanham metade do movimento da barra")
# b) the leg tops go under the new seat surface, GAP deep. The seat is fixed from here on (the hem does not chase the
# legs), so this step can repeat until every leg top is under it: a vertex whose nearest seat point is on the hem edge
# is not fully inside after one push (13 were left, one of them drawing a dark triangle in the baked AO)
st = tree(seat_f)
for it in range(8):
    rest = leg_out_of_seat(st)
    if not rest:
        break
    for i, s, loc, n in rest:
        P[i] = P[i] - n * (s + GAP + 0.0005)
        moved_leg.add(i)
# c) leg triangles that still cross a seat triangle (any diagonal) although their corners are under it: push their
# corners 1.5 mm deeper, until none crosses
def tri_list(faces):
    out = []
    for f in faces:
        if len(f) == 4:
            a, b, c, d = f
            out += [(a, b, c), (a, c, d), (a, b, d), (b, c, d)]
        else:
            out += [tuple(f[:1] + f[k:k + 2]) for k in range(1, len(f) - 1)]
    return out


LT = tri_list(leg_f)
for it_c in range(10):
    lt_ = tree(leg_f)
    cross = st.overlap(lt_)
    if not cross:
        break
    push = {i for _, j in cross for i in LT[j]}
    for i in push:
        loc, n, fi, d = st.find_nearest(P[i])
        P[i] = P[i] - n * 0.0015
        moved_leg.add(i)
print(f"PERNAS (triangulos): {it_c + 1} passadas; cruzamentos restantes {len(st.overlap(tree(leg_f)))}")
print(f"PERNAS: {it + 1} passadas; restam {len(leg_out_of_seat(st))}: " +
      ", ".join(f"h{H(P[i]):.3f} x{P[i].x:+.3f} y{P[i].y:+.3f} s{s * 1000:+.1f}mm" for i, s, _, _ in leg_out_of_seat(st)[:6]))

st1, lt1 = tree(seat_f), tree(leg_f)
after = leg_out_of_seat(st1)
cut1 = cuts(st1, lt1)
dl = [(P[i] - bm.verts[i].co).length for i in moved_leg]
ds = [(P[i] - bm.verts[i].co).length for i in moved_seat]
print(f"DEPOIS: {len(after)} vertices fora; pares se cortando: {cut1}")
print(f"MOVIDOS: topo das pernas {len(moved_leg)} vertices (ate {max(dl, default=0)*1000:.1f} mm); "
      f"barra do assento {len(moved_seat)} vertices (ate {max(ds, default=0)*1000:.1f} mm)")
# folded triangles: normal turned more than 60 degrees from the original
tris = bm.calc_loop_triangles()
n_fold = 0
for t in tris:
    idx = [l.vert.index for l in t]
    if not (set(idx) & (moved_seat | moved_leg)):
        continue
    a0, b0, c0 = (bm.verts[i].co for i in idx)
    a1, b1, c1 = (P.get(i, bm.verts[i].co) for i in idx)
    n0 = (b0 - a0).cross(c0 - a0); n1 = (b1 - a1).cross(c1 - a1)
    if n0.length > 1e-12 and n1.length > 1e-12 and n0.normalized().dot(n1.normalized()) < 0.5:
        n_fold += 1
print(f"DOBRAS: {n_fold} triangulos com a normal girada mais de 60 graus")
# the seat must still stay under the tails and the coat
OTHER = {n: [[v.index for v in f.verts] for f in bm.faces if f[PL] == PID[n]] for n in ("aba_E", "aba_D", "casaco_corpo")}
allP0 = [v.co.copy() for v in bm.verts]
allP1 = [P.get(i, allP0[i]) for i in range(len(allP0))]
for n, fs in OTHER.items():
    c0 = len(BVHTree.FromPolygons(allP0, seat_f + leg_f).overlap(BVHTree.FromPolygons(allP0, fs)))
    c1 = len(BVHTree.FromPolygons(allP1, seat_f + leg_f).overlap(BVHTree.FromPolygons(allP1, fs)))
    print(f"CALCA x {n}: pares se cortando antes {c0}, depois {c1}")
# hem line: height spread of the seat's bottom ring (a level line reads as a hem)
ring = [P[i] for i in seat_v if H(bm.verts[i].co) < H_SEAT_HEM]
print(f"BARRA do assento: {len(ring)} vertices, altura {min(H(p) for p in ring):.3f}..{max(H(p) for p in ring):.3f} m")

if DRY:
    print("DRY: nada salvo")
else:
    for i, p in P.items():
        bm.verts[i].co = p
    bm.to_mesh(ob.data)
    ob.data.update()
    ob["hcl_calca_ajustada"] = "2026-10-11: juncao assento/pernas (ajustar_calca.py)"
    bpy.ops.wm.save_mainfile()
    print("SALVO", bpy.data.filepath)
