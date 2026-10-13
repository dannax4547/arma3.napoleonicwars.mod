# Report renders of complete French 1812 test soldiers: textured uniform (coat 1812 or greatcoat), crossbelts,
# havresac and shakos, with the GAME head (Arma 3 Samples TemplateRTM\bust.p3d, Resolution 1; plain skin colour, its
# texture is not used) so the collar and the shako are seen where the game puts them. Soldiers side by side.
#   blender -b --factory-startup --python render_soldado_fr.py -- <project root> <samples dir> <out dir>
#           [soldados=<uniform>:<variant>:<shako tag>,...] [nome=soldado_fr] [samples=48] [detalhe]
#   uniform = casaca (coat 1812, variants v01..), capote (greatcoat, w01..) or elite (epaulettes, gr01, vo01); default: three coats v01 with the
#   voltigeur (campaign), fusilier and grenadier (parade) shakos
import bpy, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
SOLD = [s.split(":") for s in OPT.get("soldados", "casaca:v01:voltigeur_campanha,casaca:v01:fuzileiro_1a_comp,"
                                                   "casaca:v01:granadeiro_gala").split(",")]
NOME = OPT.get("nome", "soldado_fr")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
G = -1.0069                                                     # ground height of the character frame
J = lambda *p: os.path.join(ROOT, *p)
UNI = {"casaca": (J(r"source\models\coats\hcl_uniforme_fr\hcl_uniforme_fr_LOD0.blend"), "HCL_U_Fr1812_01_LOD0",
                  J(r"source\textures\hcl_uniforme_fr"), "hcl_u_fr1812_{}_co.png", "hcl_u_fr1812_nohq.png"),
       "capote": (J(r"source\models\coats\hcl_capote_fr\hcl_capote_fr_LOD0.blend"), "HCL_U_Fr1812_Capote_LOD0",
                  J(r"source\textures\hcl_capote_fr"), "hcl_u_fr1812_capote_{}_co.png", "hcl_u_fr1812_capote_nohq.png"),
       "elite": (J(r"source\models\coats\hcl_uniforme_fr\hcl_uniforme_fr_elite_LOD0.blend"), "HCL_U_Fr1812_Elite_LOD0",
                 J(r"source\textures\hcl_uniforme_fr_elite"), "hcl_u_fr1812_elite_{}_co.png", "hcl_u_fr1812_elite_nohq.png"),
       # Old Guard (2026-10-12): long-tailed habit, variants gr01 / ch01; headgear tag "bonnet_<tag>" = bearskin
       "guarda": (J(r"source\models\coats\hcl_uniforme_fr\hcl_uniforme_fr_guarda_LOD0.blend"), "HCL_U_Fr1812_Guarda_LOD0",
                  J(r"source\textures\hcl_uniforme_fr_guarda"), "hcl_u_fr1812_guarda_{}_co.png", "hcl_u_fr1812_guarda_nohq.png")}


def load(blend, names):
    with bpy.data.libraries.load(blend, link=False) as (s, d):
        d.objects = names
    return list(d.objects)


def texmat(name, co, nohq=None, rough=0.85):
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


def flat(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    return m


skin = flat("pele", (0.80, 0.60, 0.50))
# uniforms (one mesh per kind, materials per soldier)
meshes = {}
for kind in {k for k, _, _ in SOLD}:
    blend, name, tdir, co_fmt, nohq = UNI[kind]
    u = load(blend, [name])[0]
    parts = u["hcl_partes"].split(","); pa = u.data.attributes["hcl_part"].data
    u.data.materials.clear()
    u.data.materials.append(flat("tmp_" + kind, (0.5, 0.5, 0.5))); u.data.materials.append(skin)
    for p in u.data.polygons:
        p.material_index = 1 if parts[pa[p.index].value] == "maos_template" else 0
        p.use_smooth = True
    meshes[kind] = u
# equipment
TE = J(r"source\textures\hcl_equipamento_fr")
eq = load(J(r"source\models\accessories\hcl_equipamento_fr\hcl_equipamento_fr_LOD0.blend"),
          ["HCL_V_Fr1812_Correame_LOD0", "HCL_B_Fr1812_Havresac_LOD0"])
for o in eq:
    base = "hcl_v_fr1812_correame" if o.name.startswith("HCL_V") else "hcl_b_fr1812_havresac"
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    o.data.materials.clear()
    o.data.materials.append(texmat(base, os.path.join(TE, base + "_co.png"), os.path.join(TE, base + "_nohq.png"), 0.7))
    for p in o.data.polygons:
        p.material_index = 0
# game head
bust = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\bust.p3d"))[0]
BF = [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3]
hm = bpy.data.meshes.new("cabeca_jogo_bust")
hm.from_pydata([tuple(to_blender(p)) for p in bust["points"]], [], BF)
hm.validate()
for poly in hm.polygons:
    poly.use_smooth = True
hm.materials.append(skin)
head = bpy.data.objects.new("REF_cabeca_jogo_bust_p3d", hm)
# shakos
TS = J(r"source\textures\hcl_shako_fr")
tags = sorted({t for _, _, t in SOLD})
shk = {}
# the newest blend that has the shako wins (lote3: bigger elite plumes; lote2: lozenge plates); bearskins "bonnet_*"
SRCS = [(J(r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_v3.blend"), "HCL_Shako_Fr_", TS, "hcl_shako_fr_"),
        (J(r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_lote3.blend"), "HCL_Shako_Fr_", TS, "hcl_shako_fr_"),
        (J(r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_lote2.blend"), "HCL_Shako_Fr_", TS, "hcl_shako_fr_"),
        (J(r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas.blend"), "HCL_Shako_Fr_", TS, "hcl_shako_fr_"),
        (J(r"source\models\bonnet\hcl_bonnet_fr\hcl_bonnet_fr_texturas.blend"), "HCL_Bonnet_Fr_", J(r"source\textures\hcl_bonnet_fr"), "hcl_bonnet_fr_")]
for blend, pre, tdir_, tpre in SRCS:
    want = [t[len("bonnet_"):] if pre == "HCL_Bonnet_Fr_" else t for t in tags
            if t not in shk and (t.startswith("bonnet_") == (pre == "HCL_Bonnet_Fr_"))]
    if not want or not os.path.exists(blend):
        continue
    for o in load(blend, [f"{pre}{t}_LOD0" for t in want]):
        if o is None:
            continue
        t = o.name[len(pre):].rsplit("_LOD0", 1)[0]
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        o.data.materials.clear()
        o.data.materials.append(texmat(t, os.path.join(tdir_, f"{tpre}{t}_co.png"), os.path.join(tdir_, f"{tpre}{t}_nohq.png"), 0.5))
        for p in o.data.polygons:
            p.material_index = 0
        shk[("bonnet_" if pre == "HCL_Bonnet_Fr_" else "") + t] = o
# soldiers, 1.55 m apart (arms out in the template pose), sharing the meshes
DX = 1.55
for i, (kind, var, tag) in enumerate(SOLD):
    x = (i - (len(SOLD) - 1) / 2) * DX
    blend, name, tdir, co_fmt, nohq = UNI[kind]
    c = meshes[kind].copy(); c.location = (x, 0, 0); sc.collection.objects.link(c)
    c.material_slots[0].link = "OBJECT"
    c.material_slots[0].material = texmat(f"{kind}_{var}", os.path.join(tdir, co_fmt.format(var)), os.path.join(tdir, nohq))
    for src in [head] + eq:
        cc = src.copy(); cc.location = (x, 0, 0); sc.collection.objects.link(cc)
    s = shk[tag].copy(); s.location = (x, 0, 0); s.hide_render = False; sc.collection.objects.link(s)

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


def shot(nm, loc, tgt, lens=50, res=(1600, 1100)):
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.lens = lens; cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, f"{NOME}_{nm}.png")
    bpy.ops.render.render(write_still=True)
    print("render", sc.render.filepath)


T = Vector((0, 0, G + 0.95))
wid = DX * (len(SOLD) - 1)
dist = max(4.3, 2.1 * wid + 1.2)
shot("fila_frente", T + Vector((0.3 * dist, -dist, 0.45)), T, lens=45, res=(2000, 1100))
shot("fila_costas", T + Vector((-0.3 * dist, dist, 0.55)), T, lens=45, res=(2000, 1100))
mid = (len(SOLD) - 1) // 2 * DX - (len(SOLD) - 1) / 2 * DX                  # x of the middle soldier
shot("busto_tres_quartos", Vector((mid + 0.75, -1.05, G + 1.80)), Vector((mid, 0, G + 1.55)), lens=50, res=(1100, 1100))
shot("busto_lado", Vector((mid + 1.35, -0.05, G + 1.70)), Vector((mid, 0, G + 1.55)), lens=50, res=(1100, 1100))
if "detalhe" in a[3:]:                                       # close-ups of the middle soldier: shoulder and tails
    shot("ombro", Vector((mid + 0.62, -0.42, G + 1.78)), Vector((mid + 0.22, 0.03, G + 1.50)), lens=60, res=(1100, 1100))
    shot("abas_costas", Vector((mid - 0.35, 1.05, G + 1.25)), Vector((mid, 0.05, G + 1.02)), lens=55, res=(1100, 1100))
