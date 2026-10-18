# Report renders of complete British test soldiers (copy of render_soldado_fr.py, left untouched): textured jacket
# (line, flank company, Rifles, Highland), crossbelts (white, or black for the Rifles), Trotter knapsack and caps, with
# the GAME head (Arma 3 Samples TemplateRTM\bust.p3d, Resolution 1; plain skin colour) so the collar and the cap are
# seen where the game puts them. Soldiers side by side.
#   blender -b --factory-startup --python render_soldado_uk.py -- <project root> <samples dir> <out dir>
#           [soldados=<uniform>:<variant>:<cap tag>,...] [nome=soldado_uk] [samples=48] [detalhe]
#   uniform = linha (v01..v04), flanco (v01..v04), rifles (v01), kilt (v01..v02); cap tag = a tag of
#   blockout_shako_uk.py (belgic_batalhao, stovepipe_28th, ...) or bonnet_highland
import bpy, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
SOLD = [s.split(":") for s in OPT.get("soldados", "flanco:v01:belgic_ligeira,linha:v01:belgic_batalhao,"
                                                   "flanco:v01:belgic_granadeiro").split(",")]
NOME = OPT.get("nome", "soldado_uk")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
G = -1.0069
J = lambda *p: os.path.join(ROOT, *p)
TU = J("source", "textures", "hcl_uniforme_uk")
UNI = {k: (J("source", "models", "coats", "hcl_uniforme_uk", f"hcl_uniforme_uk_{k}_LOD0.blend"), f"HCL_U_UK1812_{k.capitalize()}_LOD0",
           TU, f"hcl_u_uk1812_{k}_{{}}_co.png", f"hcl_u_uk1812_{k}_nohq.png") for k in ("linha", "flanco", "rifles", "kilt")}
# Portugal (docs/specs/portugal_1812.md): por_linha v01..v24, por_cacadores v01..v12; the cap's number band shows the
# variant's number (gen_numeros_por.py), mapped like build_p3d_uk.py does
for k in ("linha", "cacadores"):
    UNI[f"por_{k}"] = (J("source", "models", "coats", "hcl_uniforme_uk", f"hcl_uniforme_uk_por_{k}_LOD0.blend"),
                       f"HCL_U_POR1812_{k.capitalize()}_LOD0", TU, f"hcl_u_por1812_{k}_{{}}_co.png", f"hcl_u_por1812_{k}_nohq.png")
BLACK_BELTS = ("rifles", "por_cacadores")


def load(blend, names):
    with bpy.data.libraries.load(blend, link=False) as (s, d):
        d.objects = [n for n in names if n in s.objects]
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
# equipment: the French crossbelts / havresac meshes with the British textures (spec K4)
TE = J("source", "textures", "hcl_equipamento_uk")
eq = load(J("source", "models", "accessories", "hcl_equipamento_fr", "hcl_equipamento_fr_LOD0.blend"),
          ["HCL_V_Fr1812_Correame_LOD0", "HCL_B_Fr1812_Havresac_LOD0"])
EQMAT = {}
for o in eq:
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    o.data.materials.clear()
    o.data.materials.append(flat("tmp_eq", (0.5, 0.5, 0.5)))
    for p in o.data.polygons:
        p.material_index = 0
for base in ("hcl_v_uk1812_correame", "hcl_v_uk1812_correame_preto", "hcl_b_uk1812_mochila"):
    nh = os.path.join(TE, base.replace("_preto", "") + "_nohq.png")
    EQMAT[base] = texmat(base, os.path.join(TE, base + "_co.png"), nh, 0.7)
bust = read_mlod(os.path.join(SAMPLES, "Addons", "TemplateRTM", "bust.p3d"))[0]
BF = [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3]
hm = bpy.data.meshes.new("cabeca_jogo_bust")
hm.from_pydata([tuple(to_blender(p)) for p in bust["points"]], [], BF)
hm.validate()
for poly in hm.polygons:
    poly.use_smooth = True
hm.materials.append(skin)
head = bpy.data.objects.new("REF_cabeca_jogo_bust_p3d", hm)
# caps: the newest blend that has the tag wins; the Highland bonnet has its own blend and prefix
TS = J("source", "textures", "hcl_shako_uk")
SRCS = [(J("source", "models", "shakos", "hcl_shako_uk", "hcl_shako_uk_texturas_por.blend"), "HCL_Shako_UK_", "hcl_shako_uk_"),
        (J("source", "models", "shakos", "hcl_shako_uk", "hcl_shako_uk_texturas_stovepipe.blend"), "HCL_Shako_UK_", "hcl_shako_uk_"),
        (J("source", "models", "shakos", "hcl_shako_uk", "hcl_shako_uk_texturas.blend"), "HCL_Shako_UK_", "hcl_shako_uk_"),
        (J("source", "models", "bonnet", "hcl_bonnet_uk", "hcl_bonnet_uk_texturas.blend"), "HCL_UK_", "hcl_uk_")]
tags = sorted({t for _, _, t in SOLD})
shk = {}
for blend, pre, tpre in SRCS:
    want = [t for t in tags if t not in shk]
    if not want or not os.path.exists(blend):
        continue
    for o in load(blend, [f"{pre}{t}_LOD0" for t in want]):
        t = o.name[len(pre):].rsplit("_LOD0", 1)[0]
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        o.data.materials.clear()
        o.data.materials.append(texmat(t, os.path.join(TS, f"{tpre}{t}_co.png"), os.path.join(TS, f"{tpre}{t}_nohq.png"), 0.5))
        for p in o.data.polygons:
            p.material_index = 0
        shk[t] = o
DX = 1.55
for i, (kind, var, tag) in enumerate(SOLD):
    x = (i - (len(SOLD) - 1) / 2) * DX
    blend, name, tdir, co_fmt, nohq = UNI[kind]
    c = meshes[kind].copy(); c.location = (x, 0, 0); sc.collection.objects.link(c)
    c.material_slots[0].link = "OBJECT"
    c.material_slots[0].material = texmat(f"{kind}_{var}", os.path.join(tdir, co_fmt.format(var)), os.path.join(tdir, nohq))
    hc = head.copy(); hc.location = (x, 0, 0); sc.collection.objects.link(hc)
    for src in eq:
        cc = src.copy(); cc.location = (x, 0, 0); sc.collection.objects.link(cc)
        cc.material_slots[0].link = "OBJECT"
        vest = src.name.startswith("HCL_V")
        cc.material_slots[0].material = EQMAT[("hcl_v_uk1812_correame_preto" if kind in BLACK_BELTS else "hcl_v_uk1812_correame")
                                              if vest else "hcl_b_uk1812_mochila"]
    s = shk[tag].copy(); s.location = (x, 0, 0); s.hide_render = False; sc.collection.objects.link(s)
    if kind.startswith("por_"):                       # number band: the regiment's / battalion's number texture
        s.data = s.data.copy()
        kinds = s.get("hcl_kinds", "").split(",")
        num_k = {j for j, kk in enumerate(kinds) if kk.startswith("latao_num")}
        ka = s.data.attributes["hcl_kind_i"].data
        polys = [p for p in s.data.polygons if ka[p.index].value in num_k]
        if polys:
            import numpy as np
            vids = sorted({v for p in polys for v in p.vertices})
            V = np.array([s.data.vertices[j].co[:] for j in vids]); c0 = V.mean(axis=0); D = V - c0; D[:, 0] = 0
            up = np.linalg.eigh(D.T @ D)[1][:, -1]; up = -up if up[2] < 0 else up
            hv = D @ up; h0, hb = hv.min(), max(hv.max() - hv.min(), 1e-4)
            uvd = s.data.uv_layers["UVMap"].data
            for p in polys:
                for li in p.loop_indices:
                    co = np.array(s.data.vertices[s.data.loops[li].vertex_index].co[:]) - c0
                    uvd[li].uv = (0.5 + co[0] / (8 * hb), (co @ up - h0) / hb)
                p.material_index = 1
            key = ("c" if kind == "por_cacadores" else "l") + var[-2:]
            s.data.materials.append(texmat(f"num_{key}", os.path.join(TS, "numeros", f"hcl_por_numero_{key}_co.png"), None, 0.35))

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
mid = (len(SOLD) - 1) // 2 * DX - (len(SOLD) - 1) / 2 * DX
shot("busto_tres_quartos", Vector((mid + 0.75, -1.05, G + 1.80)), Vector((mid, 0, G + 1.55)), lens=50, res=(1100, 1100))
shot("busto_lado", Vector((mid + 1.35, -0.05, G + 1.70)), Vector((mid, 0, G + 1.55)), lens=50, res=(1100, 1100))
if "detalhe" in a[3:]:
    shot("ombro", Vector((mid + 0.62, -0.42, G + 1.78)), Vector((mid + 0.22, 0.03, G + 1.50)), lens=60, res=(1100, 1100))
    shot("abas_costas", Vector((mid - 0.35, 1.05, G + 1.25)), Vector((mid, 0.05, G + 1.02)), lens=55, res=(1100, 1100))
