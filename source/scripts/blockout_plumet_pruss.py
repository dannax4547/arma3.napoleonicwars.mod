# Blockout of the Prussian shako with the dark green plume of atlas prussia1813_01 (c5-c6 r5), and the Garde zu Fuss
# star shako with the tall white-black 'Stutz' (collector record of a 1815 Guard grenadier shako): the approved production
# shakos (FWR, eagle, star) with the SAME plume shape as the French blockout (blockout_shako_fr.py), standing upright at
# the top front behind the cockade. Flat colour on the plume (no UV/texture yet: Phase 3). Reads the shako blends only.
#   blender -b --factory-startup --python blockout_plumet_pruss.py -- <project root> <render dir>
import bpy, bmesh, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plumet import plumet, feather_material
import numpy as np
from mathutils import Vector

ROOT, OUT = [os.path.abspath(a) for a in sys.argv[sys.argv.index("--") + 1:][:2]]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
SH = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss")
SRC = [("fwr", os.path.join(SH, "hcl_shako_pruss_LOD0.blend")),
       ("aguia", os.path.join(SH, r"variantes\hcl_shako_pruss_aguia_LOD0.blend")),
       ("estrela", os.path.join(SH, r"variantes\hcl_shako_pruss_estrela_LOD0.blend")),
       ("estrela_garde", os.path.join(SH, r"variantes\hcl_shako_pruss_estrela_LOD0.blend"))]
PLUME_H = 0.30                                    # same as the French blockout (decision B1 covers both)
GREEN = (0.03, 0.12, 0.05)
SPACING = 0.42


def r_at(t):                                      # identical profile to blockout_shako_fr.py
    return 0.004 + 0.026 * math.sin(math.pi * min(1.0, t / 0.5) / 2) * (1 - t) ** 0.8


def lathe(name, profile, base, colour, segs=20):
    bm = bmesh.new()
    rows = [[bm.verts.new(base + Vector((r * math.cos(2 * math.pi * s / segs), r * math.sin(2 * math.pi * s / segs), a))) for s in range(segs)] for a, r in profile]
    for j in range(len(rows) - 1):
        for i in range(segs):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % segs], rows[j + 1][(i + 1) % segs], rows[j + 1][i]))
    for ring, a in ((rows[0], profile[0][0]), (rows[-1], profile[-1][0])):
        c = bm.verts.new(base + Vector((0, 0, a)))
        for i in range(segs):
            bm.faces.new((c, ring[i], ring[(i + 1) % segs]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*colour, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me); scene.collection.objects.link(ob)
    return ob


head_done = False
for i, (tag, path) in enumerate(SRC):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith("HCL_Shako") or (n.startswith("REF_cabeca") and True)]
    for o in dst.objects:
        if o is None:
            continue
        o.name = f"{tag}_{o.name}"
        o.location.x += i * SPACING
        scene.collection.objects.link(o)
    sh = next(o for o in dst.objects if o and "HCL_Shako" in o.name)
    bpy.context.view_layer.update()
    V = np.array([(sh.matrix_world @ v.co)[:] for v in sh.data.vertices])
    ztop = V[:, 2].max()
    near = V[(V[:, 2] > ztop - 0.012) & (np.abs(V[:, 0] - i * SPACING) < 0.012)]
    y_front = near[:, 1].min()
    base = Vector((i * SPACING, y_front + 0.012, ztop - 0.012))
    lathe(f"{tag}_tulipa", [(0.0, 0.004), (0.012, 0.006), (0.024, 0.010)], base, (0.70, 0.50, 0.16))
    bm = bmesh.new()
    if tag == "estrela_garde":                     # Garde zu Fuss: tall white-black Stutz (white above black, assumed)
        by = plumet(bm, base + Vector((0, 0, 0.024)), H=0.22, colours=[(0.0, "preto"), (0.5, "branco")], shape="stutz", seed=7)
    else:
        by = plumet(bm, base + Vector((0, 0, 0.024)), H=PLUME_H, colours=[(0.0, "verde")], seed=3 + i)
    names = list(by)
    for mi, nm_ in enumerate(names):
        for f in by[nm_]:
            f.material_index = mi
    me = bpy.data.meshes.new(f"{tag}_plumet"); bm.to_mesh(me); bm.free()
    for nm_ in names:
        m = bpy.data.materials.new(f"BO_plumet_{nm_}"); m.use_nodes = True
        feather_material(m, {"verde": GREEN, "preto": (0.02, 0.02, 0.02), "branco": (0.82, 0.82, 0.80)}[nm_])
        me.materials.append(m)
    ob = bpy.data.objects.new(f"{tag}_plumet", me); scene.collection.objects.link(ob)
    print(f"PLUMET {tag}: base x{base.x:+.3f} y{base.y:+.3f} z{base.z:.3f}; topo do plumet {base.z + 0.026 + PLUME_H:.3f} m")

# lights, camera
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
zc = 0.92


def shot(name, loc, target, ortho, res):
    cam.data.type = "ORTHO"; cam.data.ortho_scale = ortho
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT, f"plumet_pruss_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


shot("frente", (1.5 * SPACING, -3.0, zc), (1.5 * SPACING, 0, zc), 1.75, (1800, 900))
for o in scene.objects:                            # side view: only the first shako (the row is along X)
    if o.type == "MESH" and not o.name.startswith("fwr_"):
        o.hide_render = True
shot("lado", (-2.0, 0.0, zc), (0.0, 0.0, zc), 0.75, (900, 1000))
for o in scene.objects:                            # side view of the Guard shako
    if o.type == "MESH":
        o.hide_render = not o.name.startswith("estrela_garde_")
shot("garde_lado", (3 * SPACING - 2.0, 0.0, zc), (3 * SPACING, 0.0, zc), 0.75, (900, 1000))
