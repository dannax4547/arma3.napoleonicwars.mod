# Preview renders of the shako with the Phase 6 texture set (Blender preview only: the game uses .paa + .rvmat).
# Usage: blender -b <LOD0.blend> --python render_shako_textured.py -- <tex_dir> <prefix> <render_dir> <tag>
import bpy, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
TEX_DIR, PREFIX, OUT, TAG = args[:4]
ob = bpy.data.objects["HCL_Shako_Pruss_LOD0"]
img_co = bpy.data.images.load(os.path.join(TEX_DIR, f"{PREFIX}_co.png"))
img_no = bpy.data.images.load(os.path.join(TEX_DIR, f"{PREFIX}_nohq.png"))
img_sm = bpy.data.images.load(os.path.join(TEX_DIR, f"{PREFIX}_smdi.png"))
for im in (img_no, img_sm):
    im.colorspace_settings.name = 'Non-Color'

for slot in ob.material_slots:
    m = slot.material
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    t_co, t_no, t_sm = (nt.nodes.new("ShaderNodeTexImage") for _ in range(3))
    t_co.image, t_no.image, t_sm.image = img_co, img_no, img_sm
    nm = nt.nodes.new("ShaderNodeNormalMap")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    nt.links.new(t_co.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(t_no.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(t_sm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Blue"], inv.inputs[1])                   # roughness = 1 - glossiness
    nt.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    try:
        nt.links.new(sep.outputs["Green"], bsdf.inputs["Specular IOR Level"])
    except KeyError:
        pass

scene = bpy.context.scene
scene.cycles.samples = 96
cam, target = bpy.data.objects["Cam"], bpy.data.objects["CamTarget"]
head = bpy.data.objects["REF_cabeca_APROXIMADA_nao_oficial"]
body = bpy.data.objects["REF_corpo_A3_character_example"]
wire = bpy.data.objects.get("REF_wireframe_overlay")
if wire:
    wire.hide_render = True
os.makedirs(OUT, exist_ok=True)
M = ob.matrix_world

def render(name, az, el, dist, tgt, res=900):
    target.location = tgt
    a, e = math.radians(az), math.radians(el)
    cam.location = Vector(tgt) + dist * Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
    cam.data.type = 'PERSP'
    cam.data.lens = 85
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT, f"{TAG}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("OK render", scene.render.filepath)

centre = Vector((0.0, -0.014, 0.80))
render("frente_3-4", 35, 10, 1.20, centre)
render("lado", 90, 3, 1.20, centre)
render("costas_3-4", 150, 15, 1.20, centre)
render("detalhe", 18, 6, 0.50, Vector((0.0, -0.12, 0.84)))
head.hide_render = body.hide_render = True
render("topo_sem_cabeca", 40, 30, 0.95, Vector((0.0, -0.014, 0.83)))
