# Builds the editable P3D models (MLOD) of the in-game TEST addon hcl_varsovia (Duchy of Warsaw line infantry,
# regulation of 3 September 1810; docs/specs/aliados_fr_1812.md section 1), on top of the official templates of the
# Arma 3 Samples (Test_Character_01). Copy of build_p3d_suica.py (own prefix, no dependency on hcl_fr):
#   uniforms hcl_u_varsovia1810.p3d (coat 1812 cut) and hcl_u_varsovia1810_elite.p3d (coat with epaulettes): the French
#            meshes and weights (hcl_fr_pesos.blend, hcl_fr_elite_pesos.blend; read only), Warsaw textures
#   czapka   hcl_h_varsovia_czapka_<tag>.p3d: blockout_czapka_varsovia.py + texturizar_aliados.py (raiz=PL_), Res 2
#            decimated to 40 %
#   bearskin hcl_h_varsovia_bonnet_<tag>.p3d: blockout_bonnet_varsovia.py + texturizar_aliados.py (raiz=PB_), Res 2
#            without the hair locks
#   blender -b --factory-startup --python build_p3d_varsovia.py -- <project root> <samples dir> <addon dir>
import bpy, bmesh, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse
from p3d_build_common import append, lod_from_mesh, merge_template_extras, finish, props_of, proxy_faces, save

ROOT, SAMPLES, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
TC = os.path.join(SAMPLES, r"Addons\Test_Character_01")
PREFIX = r"hcl\hcl_varsovia"
DATA = PREFIX + r"\data"
LOG = []
SHAKO_TAGS = ["fuzileiro", "voltigeur", "fuzileiro_kita"]          # fuzileiro_kita: 1st Regiment, black tuft
SHAKO_BLEND = r"source\models\czapka\hcl_czapka_varsovia\hcl_czapka_varsovia_texturas.blend"
BONNET_TAGS = ["granadeiro_gala", "granadeiro_campanha", "granadeiro_r05", "granadeiro_r06", "granadeiro_lisa"]
BONNET_BLEND = r"source\models\bonnet\hcl_bonnet_varsovia\hcl_bonnet_varsovia_texturas.blend"


def log(s):
    print(s); LOG.append(s)


def out(name):
    return os.path.join(OUT, name)


tpl = parse(os.path.join(TC, "A3_character_template.p3d"))
hgt = parse(os.path.join(TC, "A3_headgear_template.p3d"))

# ---------------------------------------------------------------- uniforms
T1 = tpl["lods"][0]
TV = next(x for x in tpl["lods"] if abs(x["res"] - 1100) < 0.5)
hl_tex = next((f["tex"].decode(), f["mat"].decode()) for f in T1["faces"] if f["tex"])
log(f"UNIFORME template hand texture/material kept: {hl_tex}")


def build_uniform(uni, tex, rvmat, out_name):
    parts = uni["hcl_partes"].split(",")
    HANDS = parts.index("maos_template")
    pa = uni.data.attributes["hcl_part"].data
    hand_polys = {p.index for p in uni.data.polygons if pa[p.index].value == HANDS}
    garment_polys = {p.index for p in uni.data.polygons} - hand_polys
    U_TEX = (DATA + "\\" + tex, DATA + "\\" + rvmat)
    face_tex_u = lambda pi: hl_tex if pi in hand_polys else U_TEX
    sel_u = {"Camo": garment_polys, "hl": hand_polys, "injury_hands": hand_polys}
    res1 = lod_from_mesh(uni, 1.0, props_of(T1), face_tex_u, sel_u)
    n_px = merge_template_extras(res1, T1, lambda k, P=proxy_faces(T1): k in P)
    vp = lod_from_mesh(uni, TV["res"], props_of(TV), face_tex_u, sel_u)
    n_px2 = merge_template_extras(vp, TV, lambda k, P=proxy_faces(TV): k in P)
    bones = sorted(n for n in res1["sels"] if n not in ("Camo", "hl", "injury_hands") and not n.lower().startswith("proxy"))
    log(f"UNIFORME {uni.name}: Res 1 {len(res1['faces'])} faces ({n_px} proxy faces from the template); View Pilot "
        f"{len(vp['faces'])} faces ({n_px2} proxy); {len(bones)} selections of bones; hand faces {len(hand_polys)}")
    kept = [x for x in tpl["lods"] if x["res"] >= 10000]
    save({"version": tpl["version"], "lods": [finish(res1), finish(vp)] + kept, "tail": tpl.get("tail", b"")},
         out(out_name), log)


PES = os.path.join(ROOT, r"source\models\pesos\hcl_fr_pesos.blend")
uni = append(PES, ["HCL_U_Fr1812_01_LOD0"])[0]
log(f"PESOS {os.path.basename(PES)}: {uni.name}")
build_uniform(uni, "hcl_u_varsovia1810_l1810_co.paa", "hcl_u_varsovia1810.rvmat", "hcl_u_varsovia1810.p3d")
PESE = os.path.join(ROOT, r"source\models\pesos\hcl_fr_elite_pesos.blend")
eli = append(PESE, ["HCL_U_Fr1812_Elite_LOD0"])[0]
log(f"PESOS {os.path.basename(PESE)}: {eli.name}")
build_uniform(eli, "hcl_u_varsovia1810_elite_gr_co.paa", "hcl_u_varsovia1810_elite.rvmat", "hcl_u_varsovia1810_elite.p3d")

# ---------------------------------------------------------------- shakos and bearskins (rigid on Head)
TS = next(x for x in hgt["lods"] if abs(x["res"] - 10000) < 0.5)
T2 = next(x for x in hgt["lods"] if abs(x["res"] - 2.0) < 0.01)


def lod2_of(o, tg, tx, decimate=None, polys=None):
    if decimate:
        o2 = o.copy(); o2.data = o.data.copy(); o2.name = f"lod2_{tg}"
        bpy.context.scene.collection.objects.link(o2)
        md = o2.modifiers.new("dec", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.ratio = decimate
        bpy.context.view_layer.update()
        m2 = bpy.data.meshes.new_from_object(o2.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(o2)
    else:
        bm = bmesh.new(); bm.from_mesh(o.data)
        keep = set(polys)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        m2 = bpy.data.meshes.new(f"lod2_{tg}"); bm.to_mesh(m2); bm.free()
    o2 = bpy.data.objects.new(f"lod2m_{tg}", m2)
    m2.uv_layers.active = m2.uv_layers["UVMap"]
    L2 = lod_from_mesh(o2, 2.0, props_of(T2), lambda pi, tx=tx: tx, {"camo": {p.index for p in m2.polygons}}, weights=False)
    L2["sels"]["Head"] = ({i: 1 for i in range(len(L2["points"]))}, list(range(len(L2["faces"]))))
    return finish(L2)


def headgear(o, tx, fname, tg, lod2_polys=None, lod2_decimate=None):
    """Res 1 = the whole textured mesh (selection camo), Res 2 = decimated or a subset of polygons; shadow = convex
    hull; everything rigid on Head (as build_p3d_fr.headgear)."""
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    allp = {p.index for p in o.data.polygons}
    Lr = lod_from_mesh(o, 1.0, props_of(hgt["lods"][0]), lambda pi, tx=tx: tx, {"camo": allp}, weights=False)
    Lr["sels"]["Head"] = ({i: 1 for i in range(len(Lr["points"]))}, list(range(len(Lr["faces"]))))
    extra = [lod2_of(o, tg, tx, decimate=lod2_decimate, polys=lod2_polys)]
    bm = bmesh.new()
    for v in o.data.vertices:
        bm.verts.new(v.co)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.triangulate(bm, faces=bm.faces)
    hm = bpy.data.meshes.new(f"sombra_{tg}"); bm.to_mesh(hm); bm.free()
    ho = bpy.data.objects.new(f"sombra_{tg}", hm)
    Ls = lod_from_mesh(ho, TS["res"], props_of(TS), lambda pi: ("", ""), {}, weights=False, uv=False)
    Ls["sels"]["Head"] = ({i: 1 for i in range(len(Ls["points"]))}, list(range(len(Ls["faces"]))))
    lods = [finish(Lr)] + extra + [x for x in hgt["lods"] if x["res"] >= 1000 and abs(x["res"] - 10000) > 0.5] + [finish(Ls)]
    lods.sort(key=lambda x: x["res"])
    zs = [v.co.z for v in o.data.vertices]
    log(f"BARRETINA {tg}: {len(Lr['faces'])} triangulos (Res 2: {len(extra[0]['faces'])}), altura {min(zs):.3f}..{max(zs):.3f}, "
        f"sombra {len(Ls['faces'])} triangulos")
    save({"version": hgt["version"], "lods": lods, "tail": hgt.get("tail", b"")}, out(fname), log)


for tg in SHAKO_TAGS:
    name = f"HCL_Czapka_Varsovia_{tg}_LOD0"
    o = next(x for x in append(os.path.join(ROOT, SHAKO_BLEND), [name]) if x.name.startswith(name))
    log(f"CZAPKA {tg}: de {os.path.basename(SHAKO_BLEND)}")
    headgear(o, (DATA + rf"\hcl_czapka_varsovia_{tg}_co.paa", DATA + rf"\hcl_czapka_varsovia_{tg}.rvmat"), f"hcl_h_varsovia_czapka_{tg}.p3d", tg,
             lod2_decimate=0.4)
for tg in BONNET_TAGS:
    name = f"HCL_Bonnet_Varsovia_{tg}_LOD0"
    o = next(x for x in append(os.path.join(ROOT, BONNET_BLEND), [name]) if x.name.startswith(name))
    kinds = o["hcl_kinds"].split(",")
    fur = {i for i, k in enumerate(kinds) if k == "pena:pelo"}
    ka = o.data.attributes["hcl_kind_i"].data
    lod2 = [p.index for p in o.data.polygons if ka[p.index].value not in fur]
    headgear(o, (DATA + rf"\hcl_bonnet_varsovia_{tg}_co.paa", DATA + rf"\hcl_bonnet_varsovia_{tg}.rvmat"),
             f"hcl_h_varsovia_bonnet_{tg}.p3d", "bonnet_" + tg, lod2_polys=lod2)

open(out("build_p3d_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
