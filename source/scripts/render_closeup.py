# Close-up render of a saved .blend (inspection only; does not save the file).
#   blender -b <file.blend> --python render_closeup.py -- <out.png> <cam x,y,z> <target x,y,z> [lens] [wire]
# "wire" adds a thin wireframe overlay of every mesh in the HCL_* collections.
import bpy, sys, math
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]
loc = Vector(tuple(float(v) for v in a[1].split(",")))
tgt = Vector(tuple(float(v) for v in a[2].split(",")))
lens = float(a[3]) if len(a) > 3 and a[3] != "wire" else 70.0
wire = "wire" in a
scene = bpy.context.scene
cd = bpy.data.cameras.new("CAM_closeup")
cd.lens = lens
cam = bpy.data.objects.new("CAM_closeup", cd)
cam.location = loc
cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam
if wire:
    m = bpy.data.materials.new("REF_fio_closeup")
    m.diffuse_color = (0.95, 0.8, 0.2, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.8, 0.2, 1)
    for coll in bpy.data.collections:
        if not coll.name.startswith("HCL_"):
            continue
        for ob in list(coll.objects):
            if ob.type != "MESH":
                continue
            w = ob.copy()
            w.data = ob.data.copy()
            w.data.materials.clear()
            w.data.materials.append(m)
            md = w.modifiers.new("fio", "WIREFRAME")
            md.thickness = 0.0006
            md.use_replace = True
            scene.collection.objects.link(w)
scene.render.resolution_x, scene.render.resolution_y = 1000, 800
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("render", out)
