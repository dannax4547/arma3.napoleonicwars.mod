# Report renders of the textured Russian 1812 musketeer (Phase 6 of the coat): the coat of build_uniforme_rus.py with
# the maps of generate_uniform_textures_rus.py (one soldier per variant of variantes_rus_linha.json = the shoulder
# strap colour by the regiment's place in its division) and the textured game kiver of the kiver Phases 4-7
# (hcl_kiver_rus_jogo.blend + texturizar_kiver_rus.py) on the approximate head of the kiver blockout (the game head,
# TemplateRTM\bust.p3d, needs the Arma 3 Samples). Materials as render_texturas_pruss.py: _co, _nohq (OpenGL),
# _smdi (G = specular, B = gloss -> roughness). Reads the sources only.
#   blender -b --factory-startup --python render_texturas_rus.py -- <project root> <out dir> [samples=48]
#           [variantes=R01,R02,...] [kiver=1812_mosqueteiro]
#           [peca=capote]: the greatcoat (build_capote_rus.py, variantes_rus_capote.json) instead of the coat
#           [equipamento=1]: crossbelts and knapsack (RU10, generate_equipment_textures_rus.py) on every soldier,
#           the grenadier vest (three-flame pouch grenade) on the first, without the French greatcoat roll
import bpy, bmesh, sys, os, math, json
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
J = lambda *p: os.path.join(ROOT, *p)
PECA = OPT.get("peca", "linha")
if PECA == "capote":
    COAT = J("source", "models", "coats", "hcl_capote_rus", "hcl_capote_rus_LOD0.blend")
    COAT_OBJ, TXU, VJSON, MAPAS = "HCL_U_RUS1812_Capote_LOD0", J("source", "textures", "hcl_capote_rus"),         "variantes_rus_capote.json", "hcl_u_rus1812_capote"
else:
    COAT = J("source", "models", "coats", "hcl_uniforme_rus", "hcl_uniforme_rus_linha_LOD0.blend")
    COAT_OBJ, TXU, VJSON, MAPAS = "HCL_U_RUS1812_Linha_LOD0", J("source", "textures", "hcl_uniforme_rus"),         "variantes_rus_linha.json", "hcl_u_rus1812_linha"
NOMEF = "textura_soldado_rus" if PECA == "linha" else f"textura_{PECA}_rus"
EQUIP = OPT.get("equipamento") == "1"
if EQUIP:
    NOMEF = NOMEF.replace("textura_", "equipamento_")
VAR = json.load(open(os.path.join(TXU, VJSON), encoding="utf-8"))
VIDS = OPT.get("variantes", ",".join(VAR)).split(",")
KTAG = OPT.get("kiver", "1812_mosqueteiro")
KMODEL, KVAR = KTAG.split("_")
JOGO = J("source", "models", "shakos", "hcl_kiver_rus", "hcl_kiver_rus_jogo.blend")
KBLOCK = J("source", "models", "shakos", "hcl_kiver_rus", "hcl_kiver_rus_blockout.blend")
TXK = J("source", "textures", "hcl_kiver_rus")
SPACING = 0.60


def load(blend, names):
    with bpy.data.libraries.load(blend, link=False) as (s, d):
        d.objects = [n for n in s.objects if n in names]
    for o in d.objects:
        sc.collection.objects.link(o)
    return {o.name: o for o in d.objects}


def img(path, non_color=False):
    im = bpy.data.images.load(path, check_existing=True)
    if non_color:
        im.colorspace_settings.name = "Non-Color"
    return im


def textured(name, co, nohq, smdi, metal_from_spec=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img(co)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img(nohq, True)
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    ts = nt.nodes.new("ShaderNodeTexImage"); ts.image = img(smdi, True)
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(ts.outputs["Color"], sep.inputs["Color"])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs[2], inv.inputs[1]); nt.links.new(inv.outputs[0], b.inputs["Roughness"])
    nt.links.new(sep.outputs[1], b.inputs["Specular IOR Level"])
    if metal_from_spec:                                   # preview only: the brass (G >= 0.8) as metal
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.65
        mr.inputs["From Max"].default_value = 0.80
        nt.links.new(sep.outputs[1], mr.inputs["Value"]); nt.links.new(mr.outputs[0], b.inputs["Metallic"])
    return m


skin = bpy.data.materials.new("pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.80, 0.60, 0.50, 1)
coat0 = load(COAT, [COAT_OBJ])[COAT_OBJ]
mats = [m.name for m in coat0.data.materials]
kname = f"HCL_H_RUS{KMODEL}_{KVAR.capitalize()}_LOD0"
kv0 = load(JOGO, [kname])[kname]
kbase = f"hcl_kiver_rus{KMODEL}_{KVAR}"
kmat = textured("kiver", os.path.join(TXK, f"{kbase}_co.png"), os.path.join(TXK, f"{kbase}_nohq.png"),
                os.path.join(TXK, f"{kbase}_smdi.png"), True)
kv0.data.materials.clear(); kv0.data.materials.append(kmat)
head0 = load(KBLOCK, ["REF_cabeca_APROX_0"]).get("REF_cabeca_APROX_0")
def world(o):
    """World matrix from the parent chain: objects appended without their parent in the scene are not evaluated
    (their matrix_world reads as identity; same pitfall as blockout_kiver_rus.fit)."""
    return (world(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis) if o.parent else o.matrix_basis.copy()


if head0:
    mw = world(head0)
    head0.parent = None
    head0.matrix_world = mw
    head0.data.materials.clear(); head0.data.materials.append(skin)
eq0 = {}
if EQUIP:                                                # same deletion as build_p3d_equip_rus.py (dossier E8)
    TE = J("source", "textures", "hcl_equipamento_rus")
    eq0 = load(J("source", "models", "accessories", "hcl_equipamento_fr", "hcl_equipamento_fr_LOD0.blend"),
               ["HCL_V_Fr1812_Correame_LOD0", "HCL_B_Fr1812_Havresac_LOD0"])
    pk = eq0["HCL_B_Fr1812_Havresac_LOD0"]
    kill = {i for i, n in enumerate(pk["hcl_partes"].split(",")) if n.startswith("capote")}
    bm = bmesh.new(); bm.from_mesh(pk.data)
    lay = bm.faces.layers.int.get("hcl_part")
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] in kill], context="FACES")
    bm.to_mesh(pk.data); bm.free()
    EQM = {}
    for b in ("hcl_v_rus1812_correame", "hcl_v_rus1812_correame_granadeiro", "hcl_b_rus1812_mochila"):
        EQM[b] = textured(b, os.path.join(TE, b + "_co.png"), os.path.join(TE, b + "_nohq.png"),
                          os.path.join(TE, b + "_smdi.png"), True)
    for o in eq0.values():
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        o.data.materials.clear(); o.data.materials.append(EQM["hcl_b_rus1812_mochila"])
        for p in o.data.polygons:
            p.material_index = 0; p.use_smooth = True
soldiers = []
for i, vid in enumerate(VIDS):
    v = VAR[vid]
    um = textured(vid, os.path.join(TXU, f"{v['prefixo']}_co.png"), os.path.join(TXU, f"{MAPAS}_nohq.png"),
                  os.path.join(TXU, f"{MAPAS}_smdi.png"), True)
    c = coat0 if i == 0 else coat0.copy()
    if i:
        sc.collection.objects.link(c)
    for k, slot in enumerate(c.material_slots):
        slot.link = "OBJECT"
        slot.material = skin if mats[k] == "HCL_pele_hl" else um
    x = i * SPACING
    c.location.x = x
    parts = [c]
    for base in (kv0, head0):
        if base is None:
            continue
        o = base if i == 0 else base.copy()
        if i:
            sc.collection.objects.link(o)
            o.location.x = base.location.x + x
        parts.append(o)
    for base in eq0.values():
        o = base if i == 0 else base.copy()
        if i:
            sc.collection.objects.link(o)
            o.location.x = base.location.x + x
        o.material_slots[0].link = "OBJECT"
        o.material_slots[0].material = EQM["hcl_b_rus1812_mochila" if o.name.startswith("HCL_B") else
                                           "hcl_v_rus1812_correame_granadeiro" if i == 0 else "hcl_v_rus1812_correame"]
        parts.append(o)
    for o in parts:
        o.hide_render = False                            # the game blend keeps its objects hidden in renders
    soldiers.append((vid, x, parts))
bpy.context.view_layer.update()

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
for nm, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(x) for x in rot); sc.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); sc.world = w
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = int(OPT.get("samples", 48))
sc.view_settings.view_transform = "Standard"


def shot(name, loc, target, ortho, res):
    cam.data.type = "ORTHO"; cam.data.ortho_scale = ortho
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, f"{NOMEF}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", sc.render.filepath)


def only(keep):
    for vid, x, parts in soldiers:
        for o in parts:
            o.hide_render = vid not in keep


mid = (soldiers[0][1] + soldiers[-1][1]) / 2
wid = soldiers[-1][1] - soldiers[0][1] + 1.6
shot("fila_frente", (mid, -6.0, 0.0), (mid, 0, 0.0), wid, (2400, 1500))
shot("fila_costas", (mid, 6.0, 0.0), (mid, 0, 0.0), wid, (2400, 1500))
only({soldiers[0][0]})
shot("tres_quartos", (2.6, -4.6, 1.2), (0.0, 0.0, 0.05), 2.3, (1400, 1800))
shot("peito_frente", (0.0, -3.0, 0.32), (0.0, 0.0, 0.32), 0.75, (1100, 1200))
shot("abas_costas", (0.0, 3.0, 0.05), (0.0, 0.0, 0.05), 1.05, (1100, 1300))
shot("punho", (1.2, -2.6, 0.30), (0.57, 0.08, 0.13), 0.30, (1100, 1100))
shot("polainas", (-0.6, -3.0, -0.55), (0.0, 0.0, -0.55), 0.80, (1200, 1000))
shot("ombro", (0.25, -2.4, 1.40), (0.15, 0.04, 0.55), 0.40, (1100, 1100))
if EQUIP:                                                # the pouch (behind, on the right hip) with its grenade badge
    shot("cartucheira", (-0.95, 2.8, 0.15), (-0.145, 0.21, 0.0), 0.38, (1100, 1000))
    only({soldiers[1][0]} if len(soldiers) > 1 else {soldiers[0][0]})
    shot("cartucheira_mosqueteiro", (-0.95 + soldiers[min(1, len(soldiers) - 1)][1], 2.8, 0.15),
         (-0.145 + soldiers[min(1, len(soldiers) - 1)][1], 0.21, 0.0), 0.38, (1100, 1000))
print("FIM")
