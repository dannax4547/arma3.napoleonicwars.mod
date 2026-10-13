# The French crossbelts are shared by the coat 1812 and the greatcoat (one vest item for both uniforms). Over the
# greatcoat the bayonet scabbard must hang OUTSIDE the skirt, but it was built lying against the coat tail and the
# thigh (its tip 6 mm inside the skirt, build_capote_fr.py check). It is swung out about the frog: the scabbard, its
# throat and tip and the bayonet turn by ANGLE about a horizontal axis through the top of the throat, the tip moving
# away from the leg (~12 mm). Over the coat the scabbard then hangs that much off the tail, as a hanging scabbard does.
#   blender -b <hcl_equipamento_fr_LOD0.blend> --python ajustar_bainha_fr.py -- [angle_deg=1.5]
# The .blend is saved in place; a copy of the previous one goes to _antes_bainha/ next to it (kept, never deleted).
import bpy, sys, os, math, shutil
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OPT = dict(x.split("=", 1) for x in a if "=" in x)
ANGLE = math.radians(float(OPT.get("angle_deg", 1.5)))
path = bpy.data.filepath
bk = os.path.join(os.path.dirname(path), "_antes_bainha")
os.makedirs(bk, exist_ok=True)
dst = os.path.join(bk, os.path.basename(path))
if not os.path.exists(dst):
    shutil.copy2(path, dst)
o = bpy.data.objects["HCL_V_Fr1812_Correame_LOD0"]
if "hcl_bainha_girada_graus" in o.keys():                               # never turn it twice
    raise SystemExit(f"bainha ja girada ({o['hcl_bainha_girada_graus']:.2f} graus): nada feito")
names = o["hcl_partes"].split(",")
pa = o.data.attributes["hcl_part"].data
group = {names.index(n) for n in ("bainha", "bainha_bocal", "bainha_ponteira", "baioneta_alvado", "baioneta_pescoco",
                                  "baioneta_lamina") if n in names}
vs = sorted({i for p in o.data.polygons if pa[p.index].value in group for i in p.vertices})
co = [o.data.vertices[i].co.copy() for i in vs]
top = max(co, key=lambda c: c.z)
bocal = [o.data.vertices[i].co for p in o.data.polygons if pa[p.index].value == names.index("bainha_bocal") for i in p.vertices]
pivot = sum(bocal, Vector()) / len(bocal)
pivot.z = max(c.z for c in bocal)
radial = Vector((pivot.x, pivot.y - 0.02, 0)).normalized()            # outward from the body axis (0, 0.02)
axis = Vector((0, 0, 1)).cross(radial).normalized()
R = Matrix.Rotation(ANGLE, 3, axis)
# the tip must move OUTWARD: pick the sign that increases the radial distance of the lowest point
low = min(co, key=lambda c: c.z)
if (R @ (low - pivot) + pivot - low).dot(radial) < 0:
    R = Matrix.Rotation(-ANGLE, 3, axis)
for i, c in zip(vs, co):
    o.data.vertices[i].co = R @ (c - pivot) + pivot
o.data.update()
moved = (R @ (low - pivot) + pivot - low)
print(f"BAINHA: {len(vs)} vertices girados {math.degrees(ANGLE):.2f} graus em torno do topo do bocal "
      f"({pivot.x:.3f}, {pivot.y:.3f}, h {pivot.z + 1.0069:.3f}); ponta deslocada {moved.dot(radial) * 1000:.1f} mm para fora")
o["hcl_bainha_girada_graus"] = math.degrees(ANGLE)
bpy.ops.wm.save_mainfile()
print("SALVO", path, "copia anterior em", dst)
