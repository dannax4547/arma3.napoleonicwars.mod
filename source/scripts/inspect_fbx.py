# Blender headless: imports an FBX into an empty scene (nothing is saved) and prints objects, world bounding boxes
# and selected armature bones. Used to learn the scale/axes of the official Arma 3 Samples character.
# Usage: blender -b --factory-startup --python inspect_fbx.py -- <file.fbx> [bone1,bone2,...]
import bpy, sys
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
path = args[0]
bones = [b.lower() for b in args[1].split(",")] if len(args) > 1 else ["head", "neck", "neck1", "pelvis"]

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=path)
print(f"=== {path}")
print(f"unit scale={bpy.context.scene.unit_settings.scale_length}")
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
        mx = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
        print(f"MESH {o.name:40s} verts={len(o.data.vertices):6d} min=({mn.x:.3f},{mn.y:.3f},{mn.z:.3f}) max=({mx.x:.3f},{mx.y:.3f},{mx.z:.3f}) groups={len(o.vertex_groups)} scale={tuple(round(s, 4) for s in o.scale)}")
    elif o.type == 'ARMATURE':
        print(f"ARMATURE {o.name} bones={len(o.data.bones)} scale={tuple(round(s, 4) for s in o.scale)}")
        for b in o.data.bones:
            if b.name.lower() in bones:
                h, t = o.matrix_world @ b.head_local, o.matrix_world @ b.tail_local
                print(f"  BONE {b.name:12s} head=({h.x:.3f},{h.y:.3f},{h.z:.3f}) tail=({t.x:.3f},{t.y:.3f},{t.z:.3f})")
    else:
        print(f"{o.type} {o.name} loc={tuple(round(v, 3) for v in o.matrix_world.translation)}")
