# Phase 2 support: loads the official Arma 3 Samples character (example = dressed body, template = parts that a
# new uniform keeps) as Blender meshes, prints body landmarks measured from bone selections, and renders
# orthographic views coloured by selection (camo = uniform cloth, hl = skin).
# Read-only on the Samples; writes only the renders and a reference .blend inside the project.
#   blender -b --factory-startup --python inspect_character_ref.py -- <Samples Test_Character_01 dir> <out_img_dir> [<out.blend>]
import bpy, bmesh, sys, os, math
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT = args[0], args[1]
OUT_BLEND = args[2] if len(args) > 2 else None
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    return m


M_CAMO = mat("REF_camo_uniforme", (0.20, 0.32, 0.55))
M_SKIN = mat("REF_hl_pele", (0.80, 0.60, 0.48))
M_OTHER = mat("REF_outros", (0.45, 0.45, 0.45))


def build(path, name, lod_index=0):
    lod = read_mlod(path)[lod_index]
    pts = [Vector(to_blender(p)) for p in lod["points"]]
    sels = lod["selections"]
    camo = sels.get("camo") or sels.get("Camo")
    hl = sels.get("hl")
    # Proxy triangles (weapon, headgear, head...) are helper faces, not body geometry: skip them.
    proxy = set()
    for sname, blob in sels.items():
        if sname.startswith("proxy:") or sname.startswith("-"):
            proxy.update(i for i, b in enumerate(blob) if b)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bm.verts.ensure_lookup_table()
    for f in lod["faces"]:
        idx = list(reversed(f))                   # handedness flip (see p3d_mlod.to_blender)
        if len(set(idx)) < 3 or any(i in proxy for i in f):
            continue
        try:
            face = bm.faces.new([vs[i] for i in idx])
        except ValueError:
            continue
        if camo is not None and all(camo[i] for i in f):
            face.material_index = 0
        elif hl is not None and all(hl[i] for i in f):
            face.material_index = 1
        else:
            face.material_index = 2
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in (M_CAMO, M_SKIN, M_OTHER):
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    # Vertex groups = bone selections (presence only, for landmark measurement and later weighting reference)
    for sname, blob in sels.items():
        if sname.startswith("proxy:") or sname.startswith("-"):
            continue
        vg = ob.vertex_groups.new(name=sname)
        members = [i for i, b in enumerate(blob) if b]
        if members:
            vg.add(members, 1.0, "REPLACE")
    return ob, lod, pts


ex, ex_lod, ex_pts = build(os.path.join(SAMPLES, "A3_character_example.p3d"), "REF_A3_character_example_LOD0")
tp, tp_lod, tp_pts = build(os.path.join(SAMPLES, "A3_character_template.p3d"), "REF_A3_character_template_LOD0")


def sel_box(lod, pts, name):
    blob = lod["selections"].get(name)
    if blob is None:
        return None
    P = [pts[i] for i, b in enumerate(blob) if b]
    if not P:
        return None
    lo = Vector((min(p.x for p in P), min(p.y for p in P), min(p.z for p in P)))
    hi = Vector((max(p.x for p in P), max(p.y for p in P), max(p.z for p in P)))
    return lo, hi, len(P)


def fmt(b):
    lo, hi, n = b
    return (f"x[{lo.x:+.3f},{hi.x:+.3f}] y[{lo.y:+.3f},{hi.y:+.3f}] z[{lo.z:+.3f},{hi.z:+.3f}] "
            f"size {hi.x-lo.x:.3f} x {hi.y-lo.y:.3f} x {hi.z-lo.z:.3f} ({n} pts)")


# Real body bbox: the LOD bboxes include far proxy/helper points (x up to 2.6), so measure the faces only.
def face_bbox(ob):
    used = set()
    for p in ob.data.polygons:
        used.update(p.vertices)
    P = [ob.data.vertices[i].co for i in used]
    lo = Vector((min(p.x for p in P), min(p.y for p in P), min(p.z for p in P)))
    hi = Vector((max(p.x for p in P), max(p.y for p in P), max(p.z for p in P)))
    return lo, hi, len(P)


print("\n=== LANDMARKS (Blender axes: +Z up, front -Y, character's left +X; metres)")
for ob, lod, pts in ((ex, ex_lod, ex_pts), (tp, tp_lod, tp_pts)):
    print(f"\n--- {ob.name}  faces={len(ob.data.polygons)}")
    print("  geometry bbox:", fmt(face_bbox(ob)))
    for s in ("camo", "hl", "Neck", "Spine3", "Spine2", "Spine1", "Spine", "Pelvis", "LeftShoulder", "LeftArm",
              "LeftArmRoll", "LeftForeArm", "LeftForeArmRoll", "LeftHand", "LeftUpLeg", "LeftUpLegRoll", "LeftLeg",
              "LeftLegRoll", "LeftFoot", "LeftToeBase", "injury_body", "injury_legs", "injury_hands", "insignia"):
        b = sel_box(lod, pts, s)
        if b:
            print(f"  {s:16s} {fmt(b)}")

# Horizontal sections of the dressed example: clusters of edge crossings (torso, arms, legs) at heights above
# the ground (ground = lowest vertex of the body faces).
lo_ex, hi_ex, _ = face_bbox(ex)
GROUND = lo_ex.z
print(f"\n=== GROUND z = {GROUND:+.3f} (P3D origin is {-GROUND:.3f} m above the ground); top of body faces z = {hi_ex.z:+.3f}"
      f" ({hi_ex.z - GROUND:.3f} m above ground)")
print("=== SECTIONS of the example body: h = height above ground; each cluster = x range, y range (front is -y)")
me = ex.data
used_edges = set()
for p in me.polygons:
    used_edges.update(p.edge_keys)
edges = [(me.vertices[a].co, me.vertices[b].co) for a, b in used_edges]
for h in (1.58, 1.55, 1.52, 1.50, 1.47, 1.45, 1.42, 1.40, 1.35, 1.30, 1.25, 1.20, 1.15, 1.10, 1.05, 1.00, 0.95,
          0.90, 0.85, 0.80, 0.75, 0.70, 0.60, 0.50, 0.45, 0.40, 0.30, 0.20, 0.10, 0.05):
    z = GROUND + h
    P = []
    for a, b in edges:
        if (a.z - z) * (b.z - z) < 0:
            t = (z - a.z) / (b.z - a.z)
            P.append(a.lerp(b, t))
    if not P:
        continue
    P.sort(key=lambda p: p.x)
    clusters, cur = [], [P[0]]
    for p in P[1:]:
        if p.x - cur[-1].x > 0.02:
            clusters.append(cur); cur = [p]
        else:
            cur.append(p)
    clusters.append(cur)
    desc = "  ".join(f"x[{min(q.x for q in c):+.3f},{max(q.x for q in c):+.3f}] y[{min(q.y for q in c):+.3f},{max(q.y for q in c):+.3f}]"
                     for c in clusters)
    print(f"  h={h:.2f} (z={z:+.3f}): {desc}")

# ---------------- renders
for o in (ex, tp):
    o.hide_render = True


def cam(name, loc, rot, scale):
    c = bpy.data.cameras.new(name)
    c.type = "ORTHO"
    c.ortho_scale = scale
    o = bpy.data.objects.new(name, c)
    o.location = loc
    o.rotation_euler = rot
    scene.collection.objects.link(o)
    return o


sun = bpy.data.objects.new("REF_sun", bpy.data.lights.new("REF_sun", "SUN"))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
scene.collection.objects.link(sun)
fill = bpy.data.objects.new("REF_fill", bpy.data.lights.new("REF_fill", "SUN"))
fill.data.energy = 1.2
fill.rotation_euler = (math.radians(70), 0, math.radians(200))
scene.collection.objects.link(fill)
world = bpy.data.worlds.new("REF_world")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.92, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
scene.world = world
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.render.resolution_x, scene.render.resolution_y = 900, 1100
scene.render.film_transparent = False

ZC = GROUND + 0.86                                 # frame centre: middle of a ~1.75 m figure
VIEWS = {
    "frente": ((0, -6, ZC), (math.radians(90), 0, 0)),
    "lado": ((6, 0, ZC), (math.radians(90), 0, math.radians(90))),
    "costas": ((0, 6, ZC), (math.radians(90), 0, math.radians(180))),
}
for ob, tag in ((ex, "exemplo"), (tp, "template")):
    ob.hide_render = False
    for vname, (loc, rot) in VIEWS.items():
        c = cam(f"REF_cam_{tag}_{vname}", loc, rot, 2.05)
        scene.camera = c
        scene.render.filepath = os.path.join(OUT, f"ref_corpo_{tag}_{vname}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    ob.hide_render = True

if OUT_BLEND:
    for o in (ex, tp):
        o.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    print("saved", OUT_BLEND)
