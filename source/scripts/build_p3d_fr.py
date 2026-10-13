# Builds the editable P3D models (MLOD) of the in-game TEST addon hcl_fr (French line infantry 1812), on top of the
# official templates of the Arma 3 Samples (Test_Character_01, modding licence: non-commercial Arma 3 content), the same
# way as build_p3d_pruss.py:
#   uniform  hcl_u_fr1812.p3d (coat 1812), hcl_u_fr1812_capote.p3d (greatcoat, build_capote_fr.py) and
#            hcl_u_fr1812_elite.p3d (coat with epaulettes, build_casaca_elite_fr.py): character
#                               template; Res 1 and View Pilot replaced by the uniform (template hands and proxies kept);
#                               template Res 2-4 dropped; shadow and technical LODs kept from the template
#   shakos   hcl_h_fr_<tag>.p3d : headgear template; Res 1 = textured shako (texturizar_shako_fr.py), one texture set
#                               each, shadow = convex hull, rigid on Head
#   vest     hcl_v_fr1812_correame.p3d, knapsack hcl_b_fr1812_havresac.p3d : vest template; Res 1 = production mesh with
#                               its UV atlas, weights from teste_movimentos.py (nacao=fr)
#   blender -b --factory-startup --python build_p3d_fr.py -- <project root> <samples dir> <addon dir>
#   (normally called by build_mod_fr.ps1 with <addon dir> = source/addon/hcl/hcl_fr)
import bpy, bmesh, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse
from p3d_build_common import append, lod_from_mesh, merge_template_extras, finish, props_of, proxy_faces, save

ROOT, SAMPLES, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
TC = os.path.join(SAMPLES, r"Addons\Test_Character_01")
PREFIX = r"hcl\hcl_fr"
DATA = PREFIX + r"\data"
LOG = []
SHAKO_TAGS = ["fuzileiro_1a_comp", "granadeiro_gala", "granadeiro_campanha", "voltigeur_gala", "voltigeur_campanha",
              "oficial_coronel", "fuzileiro_losango", "fuzileiro_losango_branco", "ligeira_carabineiro_gala",
              "ligeira_voltigeur_gala"]
# textured shakos live in several blends (texturizar_shako_fr.py so=...): the newest blend that has the tag wins
# (lote3: the elite gala shakos with the bigger plumes of 2026-10-12; lote2: the lozenge plates)
SHAKO_BLENDS = [r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_v3.blend",   # 2026-10-13: all 10, realism v3
                r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_lote3.blend",
                r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas_lote2.blend",
                r"source\models\shakos\hcl_shako_fr\hcl_shako_fr_texturas.blend"]
# Old Guard bearskins (blockout_bonnet_guarda.py + texturizar_shako_fr.py raiz=GD_): Res 1 full, Res 2 without the
# hair locks (the shell carries the fur texture) for distance
BONNET_TAGS = ["granadeiro_gala", "granadeiro_campanha", "cacador_gala"]
BONNET_BLEND = r"source\models\bonnet\hcl_bonnet_fr\hcl_bonnet_fr_texturas.blend"


def log(s):
    print(s); LOG.append(s)


def out(name):
    return os.path.join(OUT, name)


tpl = parse(os.path.join(TC, "A3_character_template.p3d"))
hgt = parse(os.path.join(TC, "A3_headgear_template.p3d"))
vt = parse(os.path.join(TC, "A3_vest_template.p3d"))

# ---------------------------------------------------------------- uniforms (coat 1812 and greatcoat)
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
objs = {o.name: o for o in append(PES, ["HCL_U_Fr1812_01_LOD0", "HCL_V_Fr1812_Correame_LOD0",
                                        "HCL_B_Fr1812_Havresac_LOD0"])}
log(f"PESOS {os.path.basename(PES)}: {sorted(objs)}")
build_uniform(objs["HCL_U_Fr1812_01_LOD0"], "hcl_u_fr1812_v01_co.paa", "hcl_u_fr1812.rvmat", "hcl_u_fr1812.p3d")
PESC = os.path.join(ROOT, r"source\models\pesos\hcl_fr_capote_pesos.blend")
cap = append(PESC, ["HCL_U_Fr1812_Capote_LOD0"])[0]
log(f"PESOS {os.path.basename(PESC)}: {cap.name}")
build_uniform(cap, "hcl_u_fr1812_capote_w01_co.paa", "hcl_u_fr1812_capote.rvmat", "hcl_u_fr1812_capote.p3d")
# elite companies (grenadiers, voltigeurs): the coat with epaulettes (build_casaca_elite_fr.py), its own texture set
PESE = os.path.join(ROOT, r"source\models\pesos\hcl_fr_elite_pesos.blend")
eli = append(PESE, ["HCL_U_Fr1812_Elite_LOD0"])[0]
log(f"PESOS {os.path.basename(PESE)}: {eli.name}")
build_uniform(eli, "hcl_u_fr1812_elite_gr01_co.paa", "hcl_u_fr1812_elite.rvmat", "hcl_u_fr1812_elite.p3d")
# Old Guard (2026-10-12): long-tailed habit with epaulettes (build_uniforme_fr.py hem=0.64 + build_casaca_elite_fr.py
# nome=HCL_U_Fr1812_Guarda_LOD0), weights hcl_fr_guarda_pesos.blend, textures hcl_uniforme_fr_guarda
PESG = os.path.join(ROOT, r"source\models\pesos\hcl_fr_guarda_pesos.blend")
gua = append(PESG, ["HCL_U_Fr1812_Guarda_LOD0"])[0]
log(f"PESOS {os.path.basename(PESG)}: {gua.name}")
build_uniform(gua, "hcl_u_fr1812_guarda_gr01_co.paa", "hcl_u_fr1812_guarda.rvmat", "hcl_u_fr1812_guarda.p3d")

# ---------------------------------------------------------------- shakos and bearskins (rigid on Head)
TS = next(x for x in hgt["lods"] if abs(x["res"] - 10000) < 0.5)
T2 = next(x for x in hgt["lods"] if abs(x["res"] - 2.0) < 0.01)


def headgear(o, tx, fname, tg, lod2_polys=None, lod2_decimate=None):
    """Res 1 = the whole textured mesh (selection camo); optional Res 2 = only the polygons lod2_polys, or the mesh
    decimated to lod2_decimate of its triangles (2026-10-13: the v4 shakos are 14-28k triangles); shadow = convex
    hull; everything rigid on Head."""
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    allp = {p.index for p in o.data.polygons}
    Lr = lod_from_mesh(o, 1.0, props_of(hgt["lods"][0]), lambda pi, tx=tx: tx, {"camo": allp}, weights=False)
    Lr["sels"]["Head"] = ({i: 1 for i in range(len(Lr["points"]))}, list(range(len(Lr["faces"]))))
    extra = []
    if lod2_decimate:
        o2 = o.copy(); o2.data = o.data.copy(); o2.name = f"lod2_{tg}"
        bpy.context.scene.collection.objects.link(o2)
        md = o2.modifiers.new("dec", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.ratio = lod2_decimate
        bpy.context.view_layer.update()
        m2 = bpy.data.meshes.new_from_object(o2.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(o2)
        o2 = bpy.data.objects.new(f"lod2m_{tg}", m2)
        m2.uv_layers.active = m2.uv_layers["UVMap"]
        L2 = lod_from_mesh(o2, 2.0, props_of(T2), lambda pi, tx=tx: tx, {"camo": {p.index for p in m2.polygons}}, weights=False)
        L2["sels"]["Head"] = ({i: 1 for i in range(len(L2["points"]))}, list(range(len(L2["faces"]))))
        extra = [finish(L2)]
    if lod2_polys is not None:
        bm = bmesh.new(); bm.from_mesh(o.data)
        keep = set(lod2_polys)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        m2 = bpy.data.meshes.new(f"lod2_{tg}"); bm.to_mesh(m2); bm.free()
        o2 = bpy.data.objects.new(f"lod2_{tg}", m2)
        m2.uv_layers.active = m2.uv_layers["UVMap"]
        L2 = lod_from_mesh(o2, 2.0, props_of(T2), lambda pi, tx=tx: tx, {"camo": {p.index for p in m2.polygons}}, weights=False)
        L2["sels"]["Head"] = ({i: 1 for i in range(len(L2["points"]))}, list(range(len(L2["faces"]))))
        extra = [finish(L2)]
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
    log(f"BARRETINA {tg}: {len(Lr['faces'])} triangulos" + (f" (Res 2: {len(extra[0]['faces'])})" if extra else "") +
        f", altura {min(zs):.3f}..{max(zs):.3f}, sombra {len(Ls['faces'])} triangulos")
    save({"version": hgt["version"], "lods": lods, "tail": hgt.get("tail", b"")}, out(fname), log)


for tg in SHAKO_TAGS:
    name = f"HCL_Shako_Fr_{tg}_LOD0"
    o = None
    for rel in SHAKO_BLENDS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        found = [x for x in append(path, [name]) if x.name.startswith(name)]
        if found:
            o = found[0]
            log(f"BARRETINA {tg}: de {os.path.basename(path)}")
            break
    headgear(o, (DATA + rf"\hcl_shako_fr_{tg}_co.paa", DATA + rf"\hcl_shako_fr_{tg}.rvmat"), f"hcl_h_fr_{tg}.p3d", tg,
             lod2_decimate=0.4)
for tg in BONNET_TAGS:
    name = f"HCL_Bonnet_Fr_{tg}_LOD0"
    o = next(x for x in append(os.path.join(ROOT, BONNET_BLEND), [name]) if x.name.startswith(name))
    kinds = o["hcl_kinds"].split(",")
    fur = {i for i, k in enumerate(kinds) if k == "pena:pelo"}
    ka = o.data.attributes["hcl_kind_i"].data
    lod2 = [p.index for p in o.data.polygons if ka[p.index].value not in fur]
    headgear(o, (DATA + rf"\hcl_bonnet_fr_{tg}_co.paa", DATA + rf"\hcl_bonnet_fr_{tg}.rvmat"), f"hcl_h_fr_bonnet_{tg}.p3d",
             "bonnet_" + tg, lod2_polys=lod2)

# ---------------------------------------------------------------- vest and knapsack (production meshes)
for ob_name, base in (("HCL_V_Fr1812_Correame_LOD0", "hcl_v_fr1812_correame"),
                      ("HCL_B_Fr1812_Havresac_LOD0", "hcl_b_fr1812_havresac")):
    o = objs[ob_name]
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    allp = {p.index for p in o.data.polygons}
    tx = (DATA + "\\" + base + "_co.paa", DATA + "\\" + base + ".rvmat")
    Lr = lod_from_mesh(o, 1.0, props_of(vt["lods"][0]), lambda pi, tx=tx: tx, {"camo": allp})
    log(f"EQUIPAMENTO {o.name}: producao, UV e textura {base}; {len(Lr['faces'])} triangulos; "
        f"ossos {sorted(n for n in Lr['sels'] if n != 'camo')}")
    lods = [finish(Lr)] + [x for x in vt["lods"] if x["res"] > 1e12]          # Res 1 + empty Geometry (autocenter 0)
    save({"version": vt["version"], "lods": lods, "tail": vt.get("tail", b"")}, out(base + ".p3d"), log)

open(out("build_p3d_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
