# Presentation renders of the textured Prussian 1813 set at rest: uniform (one colour variant), FWR shako on the
# approximate reference head, production vest and knapsack. Materials: _co (colour), _nohq (OpenGL normal), _smdi
# (G = specular, B = gloss -> roughness), as in render_lineup.py. Reads the sources only.
#   blender -b --factory-startup --python render_texturas_pruss.py -- <project root> <out dir> [prefix=<file prefix>]
#           [variant=V01] [only=<shot,...>] [samples=N] [sem_equip]
import bpy, sys, os, math, json
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = ARGS[:2]
OPT = dict(a.split("=", 1) for a in ARGS[2:] if "=" in a)
PREFIX = OPT.get("prefix", "texturas")
ONLY = OPT["only"].split(",") if "only" in OPT else None
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
UNI = OPT.get("uniforme", os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend"))
SHK = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss\hcl_shako_pruss_LOD0.blend")
EQ = os.path.join(ROOT, r"source\models\accessories\hcl_equipamento_pruss\hcl_equipamento_pruss_LOD0.blend")
TXU = OPT.get("tex_uniforme", os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss"))
TXS = os.path.join(ROOT, r"source\textures\hcl_shako_pruss")
TXE = os.path.join(ROOT, r"source\textures\hcl_equipamento_pruss")
VAR = json.load(open(os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss\variantes_regimentos.json")))
GROUND = -1.0069


def Z(h):
    return GROUND + h


def tex_material(name, co, nohq, smdi):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    ic = nt.nodes.new("ShaderNodeTexImage"); ic.image = bpy.data.images.load(co)
    inn = nt.nodes.new("ShaderNodeTexImage"); inn.image = bpy.data.images.load(nohq); inn.image.colorspace_settings.name = "Non-Color"
    isd = nt.nodes.new("ShaderNodeTexImage"); isd.image = bpy.data.images.load(smdi); isd.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(ic.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(inn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(isd.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Blue"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Specular IOR Level"])
    return m


def append(path, names):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in names]
    got = list(dst.objects)
    for o in got:
        bpy.context.scene.collection.objects.link(o)
    return got


def assign(ob, mat, keep_prefix=None, other=None):
    for i, slot in enumerate(ob.material_slots):
        slot.link = "OBJECT"
        slot.material = other if (keep_prefix and ob.data.materials[i].name.startswith(keep_prefix)) else mat
    for p in ob.data.polygons:
        p.use_smooth = True


skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.58, 0.46, 1)
vid = OPT.get("variant", "V01")
u = append(UNI, ["HCL_U_Pruss1813_01_LOD0"])[0]
u_tex = os.path.join(TXU, VAR[vid]["prefixo"] + "_co.png")
assign(u, tex_material("M_U", u_tex, os.path.join(TXU, "hcl_u_pruss1813_nohq.png"), os.path.join(TXU, "hcl_u_pruss1813_smdi.png")),
       "HCL_pele", skin)
got = append(SHK, ["HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial"])
s = next(o for o in got if o.name.startswith("HCL_Shako"))
h = next(o for o in got if o.name.startswith("REF_cabeca"))
assign(s, tex_material("M_S", os.path.join(TXS, "hcl_shako_pruss_co.png"), os.path.join(TXS, "hcl_shako_pruss_nohq.png"),
                       os.path.join(TXS, "hcl_shako_pruss_smdi.png")))
assign(h, skin)
if "sem_equip" not in ARGS:
    for name, pre in (("HCL_V_Pruss1813_Correame_LOD0", "hcl_v_pruss1813_correame"),
                      ("HCL_B_Pruss1813_Tornister_LOD0", "hcl_b_pruss1813_tornister")):
        o = append(EQ, [name])[0]
        assign(o, tex_material("M_" + pre, *(os.path.join(TXE, f"{pre}_{k}.png") for k in ("co", "nohq", "smdi"))))

scene = bpy.context.scene
for nm_, en, rot in (("sol", 3.4, (50, 0, 25)), ("preench", 1.3, (65, 0, 200)), ("contra", 1.1, (60, 0, 130))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.data.angle = math.radians(3)
    lo.rotation_euler = tuple(math.radians(a_) for a_ in rot); scene.collection.objects.link(lo)
world = bpy.data.worlds.new("mundo"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.90, 0.90, 0.90, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
scene.world = world
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = int(OPT.get("samples", 64))
scene.view_settings.view_transform = "Standard"
floor = bpy.data.objects.new("chao", bpy.data.meshes.new("chao"))
floor.data.from_pydata([(-4, -4, GROUND), (4, -4, GROUND), (4, 4, GROUND), (-4, 4, GROUND)], [], [[0, 1, 2, 3]])
fm_ = bpy.data.materials.new("chao"); fm_.use_nodes = True
fm_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.60, 0.57, 1)
floor.data.materials.append(fm_)
scene.collection.objects.link(floor)


def cam(name, loc, target, lens=55):
    c = bpy.data.cameras.new(name); c.lens = lens
    o = bpy.data.objects.new(name, c); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(o)
    return o


T = (0, 0, Z(1.05))
shots = [("tres_quartos", cam("C1", (2.3, -3.3, Z(1.45)), T, 50), (1100, 1400)),
         ("tres_quartos_costas", cam("C2", (-2.3, 3.3, Z(1.55)), T, 50), (1100, 1400)),
         ("peito", cam("C3", (0.55, -1.25, Z(1.45)), (0.0, -0.05, Z(1.30)), 55), (1200, 1000)),
         ("cartucheira", cam("C4", (-0.75, 1.05, Z(1.20)), (-0.12, 0.17, Z(1.02)), 55), (1200, 1000)),
         ("mochila", cam("C5", (0.85, 1.25, Z(1.80)), (0.0, 0.24, Z(1.42)), 55), (1200, 1000)),
         ("baioneta", cam("C6", (1.15, -0.55, Z(1.05)), (0.17, 0.02, Z(0.92)), 55), (1000, 1100)),
         ("pernas", cam("C7", (0.9, -1.5, Z(0.55)), (0.0, 0.0, Z(0.45)), 55), (1200, 1000)),
         ("quadril", cam("C8", (0.45, -1.35, Z(0.95)), (0.0, 0.0, Z(0.86)), 55), (1200, 1000)),
         ("quadril_lado", cam("C9", (1.45, -0.2, Z(0.92)), (0.0, 0.02, Z(0.86)), 55), (1200, 1000)),
         ("virilha", cam("C10", (0.05, -0.55, Z(0.90)), (0.0, 0.0, Z(0.87)), 55), (1000, 800))]
for name, c, (rx, ry) in shots:
    if ONLY and name not in ONLY:
        continue
    scene.camera = c
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    scene.render.filepath = os.path.join(OUT, f"{PREFIX}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)
