# Presentation renders of regimental lots, every soldier fully equipped: uniform variant (v2 textures), shako variant,
# production vest and knapsack (buff or black leather). The uniform-shako-leather pairing is for display only: in the
# game every item is independent. Reads the sources only.
#   blender -b --factory-startup --python render_regimentos.py -- <project root> <out dir> lote=verdes|barretinas
#           [samples=N] [only=frente,tres_quartos,costas,detalhe]
import bpy, sys, os, math, json
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = ARGS[:2]
OPT = dict(a.split("=", 1) for a in ARGS[2:] if "=" in a)
ONLY = OPT["only"].split(",") if "only" in OPT else None
LOTE = OPT.get("lote", "verdes")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
UNI = os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend")
SHK = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss")
EQ = os.path.join(ROOT, r"source\models\accessories\hcl_equipamento_pruss\hcl_equipamento_pruss_LOD0.blend")
TXU = os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss")
TXS = os.path.join(ROOT, r"source\textures\hcl_shako_pruss")
TXE = os.path.join(ROOT, r"source\textures\hcl_equipamento_pruss")
VAR = json.load(open(os.path.join(TXU, "variantes_regimentos.json"), encoding="utf-8"))
GROUND = -1.0069
F, A, E = "hcl_shako_pruss_LOD0.blend", r"variantes\hcl_shako_pruss_aguia_LOD0.blend", r"variantes\hcl_shako_pruss_estrela_LOD0.blend"
sv = lambda n: os.path.join(TXS, "variantes", "hcl_shako_pruss_" + n)
LOTS = {
    # blue coats (Eras Mod atlases 01-03), with the shako pairing of the first line-up (display only)
    "azuis": [("V01", F, os.path.join(TXS, "hcl_shako_pruss")), ("V02", F, sv("fwr_branca")), ("V03", A, sv("aguia_amarela")),
              ("V04", A, sv("aguia_branca")), ("V05", E, sv("estrela_prata")), ("V06", E, sv("estrela_latao")),
              ("V07", F, os.path.join(TXS, "hcl_shako_pruss")), ("V08", F, sv("fwr_branca"))],
    # green coats (Eras Mod atlases 02-03), leather as on the mod tile (correame_no_mod)
    "verdes": [("V09", E, sv("estrela_latao_linha_verde")), ("V10", A, sv("aguia_amarela_linha_verde")),
               ("V11", E, sv("estrela_prata")), ("V12", E, sv("estrela_prata_presilha_preta")),
               ("V13", A, sv("aguia_presilha_preta")), ("V14", E, sv("estrela_prata_linha_branca")),
               ("V15", E, sv("estrela_latao_linha_latao")), ("V16", A, sv("aguia_amarela_linha_latao")),
               ("V17", A, sv("aguia_branca_linha_branca"))],
    # the eight new shakos on blue coats (V03 with its corrected black cuffs first)
    "barretinas": [("V03", E, sv("estrela_prata_presilha_preta")), ("V01", A, sv("aguia_presilha_preta")),
                   ("V02", E, sv("estrela_latao_linha_verde")), ("V04", A, sv("aguia_amarela_linha_verde")),
                   ("V05", E, sv("estrela_latao_linha_latao")), ("V06", A, sv("aguia_amarela_linha_latao")),
                   ("V07", E, sv("estrela_prata_linha_branca")), ("V08", A, sv("aguia_branca_linha_branca"))],
}
LINE = LOTS[LOTE]
GAP = 1.55


def tex_material(name, co, nohq, smdi):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    ic = nt.nodes.new("ShaderNodeTexImage"); ic.image = bpy.data.images.load(co, check_existing=True)
    inn = nt.nodes.new("ShaderNodeTexImage"); inn.image = bpy.data.images.load(nohq, check_existing=True)
    inn.image.colorspace_settings.name = "Non-Color"
    isd = nt.nodes.new("ShaderNodeTexImage"); isd.image = bpy.data.images.load(smdi, check_existing=True)
    isd.image.colorspace_settings.name = "Non-Color"
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
        coll.objects.link(o)
    return got


def assign(ob, mat, keep_prefix=None, other=None):
    for i, slot in enumerate(ob.material_slots):
        slot.link = "OBJECT"
        slot.material = other if (keep_prefix and ob.data.materials[i].name.startswith(keep_prefix)) else mat
    for p in ob.data.polygons:
        p.use_smooth = True


coll = bpy.data.collections.new("DESFILE"); bpy.context.scene.collection.children.link(coll)
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.58, 0.46, 1)
eq_mats = {}
for pre in ("hcl_v_pruss1813_correame", "hcl_b_pruss1813_tornister"):
    for suf in ("", "_preto"):
        eq_mats[pre + suf] = tex_material("M_" + pre + suf, *(os.path.join(TXE, f"{pre}{suf}_{k}.png") for k in ("co", "nohq", "smdi")))
x0 = -GAP * (len(LINE) - 1) / 2
for k, (vid, shk_file, shk_tex) in enumerate(LINE):
    dx = x0 + k * GAP
    v = VAR[vid]
    u = append(UNI, ["HCL_U_Pruss1813_01_LOD0"])[0]
    u.location.x = dx
    assign(u, tex_material(f"M_{vid}", os.path.join(TXU, v["prefixo"] + "_co.png"), os.path.join(TXU, "hcl_u_pruss1813_nohq.png"),
                           os.path.join(TXU, "hcl_u_pruss1813_smdi.png")), "HCL_pele", skin)
    got = append(os.path.join(SHK, shk_file), ["HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial"])
    s = next(o for o in got if o.name.startswith("HCL_Shako"))
    h = next(o for o in got if o.name.startswith("REF_cabeca"))
    model = "aguia" if "aguia" in shk_file else "estrela" if "estrela" in shk_file else ""
    shared = os.path.join(TXS, "variantes", f"hcl_shako_pruss_{model}") if model else os.path.join(TXS, "hcl_shako_pruss")
    nohq = shared + "_nohq.png" if model else shared + "_nohq.png"
    if model:                                       # relief / gloss are shared per badge model (any of its variants)
        cand = [f for f in os.listdir(os.path.join(TXS, "variantes")) if f.startswith(f"hcl_shako_pruss_{model}") and f.endswith("_nohq.png")]
        nohq = os.path.join(TXS, "variantes", sorted(cand)[0])
    smdi = nohq.replace("_nohq.png", "_smdi.png")
    assign(s, tex_material(f"S_{vid}", shk_tex + "_co.png", nohq, smdi))
    assign(h, skin)
    for o in (s, h):
        o.location.x += dx
    leather = "_preto" if v.get("correame_no_mod") == "preto" else ""
    for name, pre in (("HCL_V_Pruss1813_Correame_LOD0", "hcl_v_pruss1813_correame"),
                      ("HCL_B_Pruss1813_Tornister_LOD0", "hcl_b_pruss1813_tornister")):
        o = append(EQ, [name])[0]
        o.location.x = dx
        assign(o, eq_mats[pre + leather])
    print(f"SOLDADO {k + 1}: {vid} ({v['nome']}), barretina {os.path.basename(shk_tex)}, couro {'preto' if leather else 'branqueado'}")

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


W = GAP * len(LINE) + 0.6
shots = [("frente", cam("CF", (0, -14, GROUND + 1.0), (0, 0, GROUND + 1.0), ortho=W), (int(W * 220), 900)),
         ("costas", cam("CB", (0, 14, GROUND + 1.0), (0, 0, GROUND + 1.0), ortho=W), (int(W * 220), 900)),
         ("tres_quartos", cam("C3", (W * 0.55, -W * 0.72, GROUND + 1.8), (W * 0.12, 0, GROUND + 1.0), lens=40), (2600, 1100)),
         ("detalhe", cam("CD", (x0 + 1.3, -2.6, GROUND + 1.75), (x0 + 0.75, 0, GROUND + 1.40), lens=45), (1800, 1100))]
for name, c, (rx, ry) in shots:
    if ONLY and name not in ONLY:
        continue
    scene.camera = c
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
    scene.render.filepath = os.path.join(OUT, f"{LOTE}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)
