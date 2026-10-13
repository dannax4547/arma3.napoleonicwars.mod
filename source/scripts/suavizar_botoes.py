# Buttons of HCL_U_Pruss1813_01_LOD0 shaded round, in place: the mesh is smooth-shaded with sharp edges above 40
# degrees (build_uniforme_production.py), and the button domes have 5-8 segments (45-72 degrees between neighbours), so
# every segment edge was sharp and the buttons looked faceted. Clears the sharp flag on all edges of the "botoes" part
# (geometry, UVs and textures unchanged; the exported normals become smooth on the buttons).
#   blender -b <LOD0.blend> --python suavizar_botoes.py -- [dry]
import bpy, sys

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
me = ob.data
parts = ob["hcl_partes"].split(",")
BTN = parts.index("botoes")
pa = me.attributes["hcl_part"].data
bverts = set()
for p in me.polygons:
    if pa[p.index].value == BTN:
        bverts.update(p.vertices)
sharp = me.attributes.get("sharp_edge")
n = 0
if sharp:
    for e in me.edges:
        if e.vertices[0] in bverts and e.vertices[1] in bverts and sharp.data[e.index].value:
            sharp.data[e.index].value = False
            n += 1
print(f"BOTOES: {len(bverts)} vertices; arestas duras removidas: {n}")
if "dry" in a:
    print("DRY: nada salvo")
else:
    me.update()
    bpy.ops.wm.save_mainfile()
    print("SALVO", bpy.data.filepath)
