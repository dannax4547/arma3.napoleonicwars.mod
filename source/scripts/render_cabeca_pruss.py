# Report renders of the Prussian headgear of 2026-10-12 on the GAME head (Arma 3 Samples TemplateRTM\bust.p3d, Res 1):
# the shakos with the dark green plumet (build_plumet_pruss.py), the Guard star shako with the white-black Stutz and the
# cloth caps (blockout_bone_landwehr.py + recolorir_textura.py), with their game textures (PNG sources of the PAA).
#   blender -b --factory-startup --python render_cabeca_pruss.py -- <project root> <samples dir> <out dir> [samples=48]
import bpy, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
J = lambda *p: os.path.join(ROOT, *p)
SH = J("source", "models", "shakos", "hcl_shako_pruss")
TX = J("source", "textures", "hcl_shako_pruss")
TB = J("source", "textures", "hcl_bone_pruss")
SHAKO = {"fwr": (os.path.join(SH, "hcl_shako_pruss_LOD0.blend"), os.path.join(TX, "hcl_shako_pruss_co.png"), os.path.join(TX, "hcl_shako_pruss_nohq.png")),
         "aguia": (os.path.join(SH, "variantes", "hcl_shako_pruss_aguia_LOD0.blend"),
                   os.path.join(TX, "variantes", "hcl_shako_pruss_aguia_amarela_co.png"), os.path.join(TX, "variantes", "hcl_shako_pruss_aguia_amarela_nohq.png")),
         "estrela": (os.path.join(SH, "variantes", "hcl_shako_pruss_estrela_LOD0.blend"),
                     os.path.join(TX, "variantes", "hcl_shako_pruss_estrela_prata_co.png"), os.path.join(TX, "variantes", "hcl_shako_pruss_estrela_prata_nohq.png"))}
ROW = [("fwr", "verde"), ("aguia", "verde"), ("estrela", "verde"), ("estrela", "stutz"),
       ("bone", "c01_azul_vermelha"), ("bone", "c02_azul_amarela"), ("bone", "c03_verde_preta"), ("bone", "c04_azul_verde"),
       ("bone", "c05_azul_branca")]


def load(blend, names):
    with bpy.data.libraries.load(blend, link=False) as (s, d):
        d.objects = names
    return list(d.objects)


def texmat(name, co, nohq=None, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(co, check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if nohq and os.path.exists(nohq):
        tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(nohq, check_existing=True)
        tn.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def retex(o, m):
    o.data = o.data.copy()
    o.data.materials.clear(); o.data.materials.append(m)
    for p in o.data.polygons:
        p.material_index = 0


skin = bpy.data.materials.new("pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.80, 0.60, 0.50, 1)
bust = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\bust.p3d"))[0]
hm = bpy.data.meshes.new("cabeca_jogo_bust")
hm.from_pydata([tuple(to_blender(p)) for p in bust["points"]], [], [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3])
hm.validate()
for p in hm.polygons:
    p.use_smooth = True
hm.materials.append(skin)
plume_mat = texmat("plumet", os.path.join(TX, "hcl_plumet_pruss_co.png"), os.path.join(TX, "hcl_plumet_pruss_nohq.png"), 0.75)
DX = 0.40
for i, (key, var) in enumerate(ROW):
    x = (i - (len(ROW) - 1) / 2) * DX
    h = bpy.data.objects.new(f"cabeca_{i}", hm); h.location.x = x; sc.collection.objects.link(h)
    if key == "bone":
        o = load(J("source", "models", "shakos", "hcl_bone_pruss", "hcl_bone_pruss_texturas.blend"), ["HCL_Bone_Pruss_azul_faixa_vermelha_LOD0"])[0]
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        retex(o, texmat(f"bone_{var}", os.path.join(TB, f"hcl_bone_pruss_{var}_co.png"),
                        os.path.join(TB, "hcl_bone_pruss_azul_faixa_vermelha_nohq.png"), 0.8))
        o.location.x = x; sc.collection.objects.link(o)
        continue
    blend, co, nohq = SHAKO[key]
    s = load(blend, ["HCL_Shako_Pruss_LOD0"])[0]
    retex(s, texmat(f"shako_{key}", co, nohq, 0.5))
    s.location.x = x; sc.collection.objects.link(s)
    pl = load(J("source", "models", "shakos", "hcl_shako_pruss", "variantes", "hcl_plumet_pruss.blend"), [f"HCL_Plumet_Pruss_{key}_{var}"])[0]
    retex(pl, plume_mat)
    pl.location.x = x; sc.collection.objects.link(pl)

for n_, en, rot in (("s", 3.2, (50, 0, 25)), ("p", 1.4, (65, 0, 200)), ("c", 1.2, (60, 0, 120))):
    lo = bpy.data.objects.new(n_, bpy.data.lights.new(n_, "SUN")); lo.data.energy = en
    lo.rotation_euler = [math.radians(v) for v in rot]; sc.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
sc.world = w
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = int(OPT.get("samples", 48))
sc.view_settings.view_transform = "Standard"


def shot(nm, loc, tgt, lens=50, res=(2200, 900)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.lens = lens; cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, f"cabeca_pruss_{nm}.png")
    bpy.ops.render.render(write_still=True)
    print("render", sc.render.filepath)


Z = 0.80
shot("fila_tres_quartos", Vector((1.2, -4.6, Z + 0.55)), Vector((0, 0, Z + 0.05)), lens=55)
x0 = (0 - (len(ROW) - 1) / 2) * DX
shot("plumet_perto", Vector((x0 + 0.45, -0.75, Z + 0.25)), Vector((x0, 0, Z + 0.15)), lens=50, res=(1000, 1100))
x3 = (3 - (len(ROW) - 1) / 2) * DX
shot("stutz_perto", Vector((x3 + 0.45, -0.75, Z + 0.20)), Vector((x3, 0, Z + 0.10)), lens=50, res=(1000, 1100))
x4 = (4 - (len(ROW) - 1) / 2) * DX
shot("bone_perto", Vector((x4 + 0.35, -0.55, Z + 0.10)), Vector((x4, 0, Z)), lens=50, res=(1000, 900))
