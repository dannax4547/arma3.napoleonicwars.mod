# Collar fix of HCL_U_Pruss1813_01_LOD0, in place (vertices moved, topology and UVs unchanged, so all texture variants
# stay valid). Problem seen in game (2026-10-11): the head's throat covered the front of the collar; only the sides
# showed red. Cause: build_uniforme_production.py shaped the collar on the convex hull of the body section at 1.555 m
# (neck + upper shoulders, |x| <= 0.10): an opening 190 mm wide x 91 mm deep, its front only 11 mm in front of the
# pelvis axis. New collar: neck-shaped ring around a neck of 104 x 104 mm centred at y = +0.050, the front leaning
# forward with height (the throat goes up and forward), back kept vertical; inner wall 7.5-8.5 mm off the neck as before
# (each vertex keeps its offset from the old profile, so the collar's thickness, roll and heights are unchanged).
# The coat yoke within 7 cm of the collar base follows the collar base displacement, fading to zero, sliding along
# the old coat surface (shoulder shape kept); shoulder boards and their buttons are not moved; coat buttons move rigidly.
#   blender -b <LOD0.blend> --python ajustar_gola.py -- <Samples Test_Character_01 dir> [dry]
import bpy, bmesh, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uniform_fit import Body, UP, profile, radius, fpoint, theta_of, frame_centre

a = sys.argv[sys.argv.index("--") + 1:]
TC = a[0]
DRY = "dry" in a
B = Body(os.path.join(TC, "A3_character_example.p3d"))
Z = B.Z
# the old collar frame, exactly as build_uniforme_production.py computed it
neck_idx = B.group_idx({"neck", "spine3", "head"})
neck_pts = B.section(neck_idx, Vector((0, 0, Z(1.555))), UP, xlim=0.10)
old = profile(neck_pts, Vector((0, 0, Z(1.535))), UP)
oc = frame_centre(old)
u, v = old["u"], old["v"]                        # u = front (-Y), v = +X (left)

# new neck surface (where the old profile had radius(old, th)): asymmetric ellipse around (0, Y_C)
Y_C, A_W, A_B = 0.050, 0.052, 0.052
A_F0, A_F_TILT = 0.052, 0.12                       # front half-depth grows 0.12 m per m of height (forward lean)
FRONT_DIP = 0.008                                  # the top of the collar is this much lower at the front (chin room)
H0 = 1.535


def new_neck_point(th, z):
    h = z - Z(0)
    aF = A_F0 + A_F_TILT * max(0.0, h - H0)
    c, s = math.cos(th), math.sin(th)
    aD = aF if c >= 0 else A_B
    R = 1.0 / math.sqrt((c / aD) ** 2 + (s / A_W) ** 2)
    d = u * c + v * s
    return Vector((0, Y_C, z)) + Vector((d.x, d.y, 0)) * R, Vector((d.x, d.y, 0)), R


def map_collar(p):
    q = p - oc
    q.z = 0
    th = theta_of(old, q)
    r_v = (p - fpoint(old, th, 0.0)).length if False else None
    base = fpoint(old, th, 0.0)                    # old neck profile point at this angle (height of the frame origin)
    base.z = p.z
    rad_dir = Vector((math.cos(th) * u.x + math.sin(th) * v.x, math.cos(th) * u.y + math.sin(th) * v.y, 0))
    e = (p - base).dot(rad_dir)                    # offset of the vertex from the old profile (wall thickness)
    np_, d, R = new_neck_point(th, p.z)
    out = np_ + d * e
    up = max(0.0, min(1.0, (p.z - Z(1.535)) / 0.055))     # 0 at the collar base, 1 at its top
    out.z -= FRONT_DIP * max(0.0, math.cos(th)) ** 2 * up
    return out, th, e


ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
vpart = {}
for f in bm.faces:
    for vv in f.verts:
        vpart.setdefault(vv.index, set()).add(f[PL])
bm.verts.ensure_lookup_table()
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
OLD_COAT = BVHTree.FromPolygons([x.co.copy() for x in bm.verts],
                                [[x.index for x in f.verts] for f in bm.faces if f[PL] == PID["casaco_corpo"]])
_pl = [x for x in bm.verts if vpart.get(x.index, set()) & {PID["platina_E"], PID["platina_D"]}]
PLAT_KD = KDTree(len(_pl))
for k_, x in enumerate(_pl):
    PLAT_KD.insert(x.co, k_)
PLAT_KD.balance()

# 1. collar
moved = {}
shift_f = []
for vv in bm.verts:
    if PID["gola"] in vpart.get(vv.index, ()):
        np_, th, e = map_collar(vv.co.copy())
        if abs(math.cos(th)) > 0.95 and math.cos(th) > 0:
            shift_f.append((np_ - vv.co).dot(Vector((0, -1, 0))))
        moved[vv.index] = np_
print(f"GOLA: {len(moved)} vertices; frente avancou {min(shift_f) * 1000:.1f}..{max(shift_f) * 1000:.1f} mm")


# 2. displacement of the collar base (old ring at de = 0.010 -> new ring at the same offset), as a function of angle
def base_disp(th, z):
    old_p = fpoint(old, th, 0.010)
    old_p.z = z
    np_, d, R = new_neck_point(th, z)
    return (np_ + d * 0.010) - old_p, old_p


FADE = 0.07
OUTER = 0.0135                                     # outermost offset of the collar wall from the neck (roll)


def keep_clear(p, margin=0.006):
    """Push a point radially (about the new collar axis) so it stays `margin` outside the collar's outer wall."""
    q = Vector((p.x, p.y - Y_C, 0))
    if q.length < 1e-9:
        return p
    th = math.atan2(q.dot(v), q.dot(u))
    np_, d, R = new_neck_point(th, p.z)
    rmin = R + OUTER + margin
    if q.length < rmin:
        q = q.normalized() * rmin
        return Vector((q.x, q.y + Y_C, p.z))
    return p


n_yoke = n_strap = 0
for vv in bm.verts:
    ps = vpart.get(vv.index, set())
    if PID["gola"] in ps or PID["casaco_corpo"] not in ps:
        continue
    p = vv.co.copy()
    if p.z < Z(1.40):
        continue
    q = p - oc; q.z = 0
    th = theta_of(old, q)
    disp, old_base = base_disp(th, p.z)
    r_base = (Vector((old_base.x, old_base.y, 0)) - Vector((oc.x, oc.y, 0))).length
    r_v = q.length
    t = max(0.0, min(1.0, (r_v - r_base) / FADE))
    w = 1.0 - t * t * (3 - 2 * t)
    if r_v < r_base:
        w = 1.0
    if w <= 0:
        continue
    newp = p + Vector((disp.x, disp.y, 0)) * w
    # slide along the OLD coat surface (shoulder shape kept, so the shoulder boards stay seated on it); inside the old
    # collar ring there was no coat: keep the height of the old top ring there
    hit = OLD_COAT.ray_cast(Vector((newp.x, newp.y, p.z + 0.15)), Vector((0, 0, -1)), 0.30)
    if hit[0] is not None and abs(hit[0].z - p.z) < 0.05:
        newp.z = hit[0].z
    n_yoke += 1
    moved[vv.index] = newp
# 3. buttons near the collar move rigidly with the field at their centre
seen = set()
n_btn = 0
for vv in bm.verts:
    if vv.index in seen or PID["botoes"] not in vpart.get(vv.index, ()):
        continue
    comp, stack = [], [vv]
    seen.add(vv.index)
    while stack:
        x = stack.pop(); comp.append(x)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen:
                seen.add(y.index); stack.append(y)
    c = sum((x.co for x in comp), Vector()) / len(comp)
    if c.z < Z(1.40):
        continue
    near_strap = PLAT_KD.find(c)[2] < 0.012
    if near_strap:                                     # shoulder-board button: the board does not move
        continue
    q = c - oc; q.z = 0
    th = theta_of(old, q)
    disp, old_base = base_disp(th, c.z)
    r_base = (Vector((old_base.x, old_base.y, 0)) - Vector((oc.x, oc.y, 0))).length
    t = max(0.0, min(1.0, (q.length - r_base) / FADE))
    w = 1.0 - t * t * (3 - 2 * t)
    if w <= 0:
        continue
    c_new = c + Vector((disp.x, disp.y, 0)) * w
    for x in comp:
        moved[x.index] = x.co + (c_new - c)
    n_btn += 1
print(f"CASACO: {n_yoke} vertices do encaixe (deslizam na superficie antiga); PLATINAS: nao movidas; BOTOES do casaco movidos inteiros: {n_btn}")

# 4. the new inner opening, measured
gola_new = [moved[i] for i in moved if PID["gola"] in vpart.get(i, ())]
for h in (1.535, 1.56, 1.585):
    ring = [p for p in gola_new if abs(p.z - Z(h)) < 0.006]
    if ring:
        xs = [p.x for p in ring]; ys = [p.y for p in ring]
        print(f"GOLA h~{h:.3f}: x {min(xs):+.3f}..{max(xs):+.3f}  y {min(ys):+.3f}..{max(ys):+.3f}  (paredes externas incluidas)")
if DRY:
    print("DRY: nada salvo")
else:
    for i, p in moved.items():
        bm.verts[i].co = p
    bm.to_mesh(ob.data)
    ob.data.update()
    ob["hcl_gola_ajustada"] = "2026-10-11: gola em volta do pescoco (ajustar_gola.py)"
    bpy.ops.wm.save_mainfile()
    print("SALVO", bpy.data.filepath)
