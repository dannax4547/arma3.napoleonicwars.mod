# Presentation render: the uniform variants side by side, each with a shako variant (pairing for display only: in the
# game uniform and headgear are independent items). Textured materials: _co (colour), _nohq (normal, OpenGL),
# _smdi (B = gloss -> roughness). Does not modify any source file.
#   blender -b --factory-startup --python render_lineup.py -- <project root> <out_dir> [norender] [only=<shot,...>] [samples=<n>]
import bpy, sys, os, math, json
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = ARGS[:2]
OPT = dict(a.split("=", 1) for a in ARGS[2:] if "=" in a)
ONLY = OPT["only"].split(",") if "only" in OPT else None
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
UNI = os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend")
SHK = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss")
TXU = os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss")
TXS = os.path.join(ROOT, r"source\textures\hcl_shako_pruss")
VAR = json.load(open(os.path.join(TXU, "variantes_regimentos.json")))
LINE = [("V01", "hcl_shako_pruss_LOD0.blend", os.path.join(TXS, "hcl_shako_pruss")),
        ("V02", "hcl_shako_pruss_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_fwr_branca")),
        ("V03", r"variantes\hcl_shako_pruss_aguia_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_aguia_amarela")),
        ("V04", r"variantes\hcl_shako_pruss_aguia_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_aguia_branca")),
        ("V05", r"variantes\hcl_shako_pruss_estrela_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_estrela_prata")),
        ("V06", r"variantes\hcl_shako_pruss_estrela_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_estrela_latao")),
        ("V07", "hcl_shako_pruss_LOD0.blend", os.path.join(TXS, "hcl_shako_pruss")),
        ("V08", "hcl_shako_pruss_LOD0.blend", os.path.join(TXS, r"variantes\hcl_shako_pruss_fwr_branca"))]
GAP = 1.55                                                          # arm span in the A pose is ~1.45 m


def tex_material(name, co, nohq, smdi):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    ic = nt.nodes.new("ShaderNodeTexImage"); ic.image = bpy.data.images.load(co)
    inn = nt.nodes.new("ShaderNodeTexImage"); inn.image = bpy.data.images.load(nohq); inn.image.colorspace_settings.name = "Non-Color"
    isd = nt.nodes.new("ShaderNodeTexImage"); isd.image = bpy.data.images.load(smdi); isd.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.0
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
    return list(dst.objects)


skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.58, 0.46, 1)
coll = bpy.data.collections.new("LINEUP"); bpy.context.scene.collection.children.link(coll)
x0 = -GAP * (len(LINE) - 1) / 2
for k, (vid, shk_file, shk_tex) in enumerate(LINE):
    dx = x0 + k * GAP
    u = append(UNI, ["HCL_U_Pruss1813_01_LOD0"])[0]
    u.name = f"U_{vid}"
    coll.objects.link(u)
    u.location.x = dx
    v = VAR[vid]
    mu = tex_material(f"M_{vid}", os.path.join(TXU, v["prefixo"] + "_co.png"), os.path.join(TXU, "hcl_u_pruss1813_nohq.png"),
                      os.path.join(TXU, "hcl_u_pruss1813_smdi.png"))
    for i, slot in enumerate(u.material_slots):
        slot.link = "OBJECT"
        slot.material = skin if u.data.materials[i].name.startswith("HCL_pele") else mu
    for p in u.data.polygons:
        p.use_smooth = True
    got = append(os.path.join(SHK, shk_file), ["HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial"])
    s = next(o for o in got if o.name.startswith("HCL_Shako"))         # append order is not guaranteed
    h = next(o for o in got if o.name.startswith("REF_cabeca"))
    for o in (s, h):
        coll.objects.link(o)
        o.location.x += dx
    ms = tex_material(f"S_{vid}", shk_tex + "_co.png", shk_tex + "_nohq.png", shk_tex + "_smdi.png")
    for slot in s.material_slots:
        slot.link = "OBJECT"; slot.material = ms
    for slot in h.material_slots:
        slot.link = "OBJECT"; slot.material = skin

scene = bpy.context.scene
for nm_, en, rot in (("sol", 3.4, (50, 0, 25)), ("preench", 1.3, (65, 0, 200)), ("contra", 1.1, (60, 0, 130))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a_) for a_ in rot); coll.objects.link(lo)
world = bpy.data.worlds.new("mundo"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.90, 0.90, 0.90, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
scene.world = world
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = int(OPT.get("samples", 48))
scene.view_settings.view_transform = "Standard"
GROUND = -1.0069


def cam(name, loc, target, lens=50, ortho=None):
    c = bpy.data.cameras.new(name)
    if ortho:
        c.type = "ORTHO"; c.ortho_scale = ortho
    else:
        c.lens = lens
    o = bpy.data.objects.new(name, c); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


if "norender" not in sys.argv:
    shots = [("desfile_frente", cam("CF", (0, -12, GROUND + 1.0), (0, 0, GROUND + 1.0), ortho=12.6), (2800, 900)),
             ("desfile_tres_quartos", cam("C3", (7.5, -9.8, GROUND + 1.8), (1.5, 0, GROUND + 1.0), lens=40), (2400, 1000)),
             ("desfile_costas", cam("CB", (0, 12, GROUND + 1.0), (0, 0, GROUND + 1.0), ortho=12.6), (2800, 900)),
             ("desfile_detalhe", cam("CD", (-3.9, -2.6, GROUND + 1.75), (-3.88, 0, GROUND + 1.48), lens=50), (1600, 1000))]
    for name, c, (rx, ry) in shots:
        if ONLY and name.replace("desfile_", "") not in ONLY:
            continue
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT, f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "desfile_variantes.blend"))
