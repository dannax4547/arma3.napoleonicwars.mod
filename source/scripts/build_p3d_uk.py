# Builds the editable P3D models (MLOD) of the in-game TEST addon hcl_uk (British infantry 1812-1815 and, later, the
# allied contingents), on top of the official templates of the Arma 3 Samples (Test_Character_01), exactly like
# build_p3d_fr.py (copied here, left untouched):
#   uniforms hcl_u_uk1812_linha.p3d (battalion companies), hcl_u_uk1812_flanco.p3d (flank companies, wings) and
#            hcl_u_uk1812_rifles.p3d (95th): character template; Res 1 and View Pilot replaced by the uniform
#   caps     hcl_h_uk_<tag>.p3d : headgear template; Res 1 = textured cap (texturizar_shako_uk.py), Res 2 decimated,
#            shadow = convex hull, rigid on Head
#   vest     hcl_v_uk1812_correame.p3d, knapsack hcl_b_uk1812_mochila.p3d: the French crossbelts / havresac meshes
#            (spec uk_1812.md K4) with British textures, weights from teste_movimentos.py (nacao=fr uni=<UK coat>)
#   blender -b --factory-startup --python build_p3d_uk.py -- <project root> <samples dir> <addon dir>
#   (normally called by build_mod_uk.ps1 with <addon dir> = source/addon/hcl/hcl_uk)
import bpy, bmesh, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse
from p3d_build_common import append, lod_from_mesh, merge_template_extras, finish, props_of, proxy_faces, save

ROOT, SAMPLES, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
TC = os.path.join(SAMPLES, r"Addons\Test_Character_01")
PREFIX = r"hcl\hcl_uk"
DATA = PREFIX + r"\data"
LOG = []
SHAKO_TAGS = ["belgic_batalhao", "belgic_granadeiro", "belgic_ligeira", "stovepipe_batalhao", "stovepipe_granadeiro",
              "stovepipe_ligeira", "stovepipe_28th", "stovepipe_rifles"]
# the newest blend that has the tag wins: the stovepipes were re-baked on a levels copy of the art (realce_arte_uk.py)
SHAKO_BLENDS = [r"source\models\shakos\hcl_shako_uk\hcl_shako_uk_texturas_stovepipe.blend",
                r"source\models\shakos\hcl_shako_uk\hcl_shako_uk_texturas.blend"]


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


UNIS = [("linha", "HCL_U_UK1812_Linha_LOD0", "hcl_u_uk1812_linha"),
        ("flanco", "HCL_U_UK1812_Flanco_LOD0", "hcl_u_uk1812_flanco"),
        ("rifles", "HCL_U_UK1812_Rifles_LOD0", "hcl_u_uk1812_rifles"),
        ("kilt", "HCL_U_UK1812_Kilt_LOD0", "hcl_u_uk1812_kilt"),            # Highland dress (build_kilt_uk.py)
        # Portugal (docs/specs/portugal_1812.md): line (frente=simples) and Cacadores (frente=alamares)
        ("por_linha", "HCL_U_POR1812_Linha_LOD0", "hcl_u_por1812_linha"),
        ("por_cacadores", "HCL_U_POR1812_Cacadores_LOD0", "hcl_u_por1812_cacadores")]
objs = {}
for k_, oname, base in UNIS:
    PES = os.path.join(ROOT, rf"source\models\pesos\hcl_uk_{k_}_pesos.blend")
    got = {o.name: o for o in append(PES, [oname] + (["HCL_V_Fr1812_Correame_LOD0", "HCL_B_Fr1812_Havresac_LOD0"] if k_ == "linha" else []))}
    log(f"PESOS {os.path.basename(PES)}: {sorted(got)}")
    objs.update(got)
    build_uniform(got[oname], f"{base}_v01_co.paa", f"{base}.rvmat", f"{base}.p3d")

# ---------------------------------------------------------------- shakos and bearskins (rigid on Head)
TS = next(x for x in hgt["lods"] if abs(x["res"] - 10000) < 0.5)
T2 = next(x for x in hgt["lods"] if abs(x["res"] - 2.0) < 0.01)


def number_faces(me, kinds_str):
    """Faces of kind latao_num (Portuguese number band, texturizar_shako_uk.py); their UVMap is rewritten so the
    band shows the 1024 x 128 number texture (gen_numeros_por.py) at its real aspect: v = 0..1 over the band height,
    u = 0.5 +- (along X) / (8 x height), centred."""
    kinds = kinds_str.split(",")
    if "hcl_kind_i" not in me.attributes or not any(k.startswith("latao_num") for k in kinds):
        return set()
    num_k = {i for i, k in enumerate(kinds) if k.startswith("latao_num")}
    ka = me.attributes["hcl_kind_i"].data
    polys = {p.index for p in me.polygons if ka[p.index].value in num_k}
    if not polys:
        return polys
    import numpy as np
    vids = sorted({v for pi in polys for v in me.polygons[pi].vertices})
    V = np.array([me.vertices[i].co[:] for i in vids])
    c = V.mean(axis=0); D = V - c; D[:, 0] = 0
    w_, ev = np.linalg.eigh(D.T @ D); up = ev[:, -1]                  # the band's height direction (not X)
    if up[2] < 0:
        up = -up
    hv = D @ up; h0, h1 = hv.min(), hv.max(); hb = max(h1 - h0, 1e-4)
    uvd = me.uv_layers["UVMap"].data
    for pi in polys:
        for li in me.polygons[pi].loop_indices:
            co = np.array(me.vertices[me.loops[li].vertex_index].co[:]) - c
            uvd[li].uv = (0.5 + co[0] / (8 * hb), (co @ up - h0) / hb)
    return polys


def headgear(o, tx, fname, tg, lod2_polys=None, lod2_decimate=None, numero=None):
    """Res 1 = the whole textured mesh (selection camo); optional Res 2 = only the polygons lod2_polys, or the mesh
    decimated to lod2_decimate of its triangles (2026-10-13: the v4 shakos are 14-28k triangles); shadow = convex
    hull; everything rigid on Head. numero = (paa, rvmat) of the Portuguese number band: its faces get that texture
    and the selection "numero" (hiddenSelections in the config), the rest stays "camo"."""
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    allp = {p.index for p in o.data.polygons}
    nump = number_faces(o.data, o.get("hcl_kinds", "")) if numero else set()
    if numero:
        log(f"BARRETINA {tg}: faixa do numero {len(nump)} faces (selecao numero)")
    Lr = lod_from_mesh(o, 1.0, props_of(hgt["lods"][0]), lambda pi, tx=tx: numero if pi in nump else tx,
                       {"camo": allp - nump, **({"numero": nump} if nump else {})}, weights=False)
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
        num2 = number_faces(m2, o.get("hcl_kinds", "")) if numero else set()
        L2 = lod_from_mesh(o2, 2.0, props_of(T2), lambda pi, tx=tx: numero if pi in num2 else tx,
                           {"camo": {p.index for p in m2.polygons} - num2, **({"numero": num2} if num2 else {})},
                           weights=False)
        L2["sels"]["Head"] = ({i: 1 for i in range(len(L2["points"]))}, list(range(len(L2["faces"]))))
        extra = [finish(L2)]
        if numero:
            log(f"BARRETINA {tg}: Res 2 faixa do numero {len(num2)} faces")
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
    name = f"HCL_Shako_UK_{tg}_LOD0"
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
    headgear(o, (DATA + rf"\hcl_shako_uk_{tg}_co.paa", DATA + rf"\hcl_shako_uk_{tg}.rvmat"), f"hcl_h_uk_{tg}.p3d", tg,
             lod2_decimate=0.4)
# Portuguese stovepipes (blockout_shako_uk.py conjunto=por): number band in the hidden selection "numero"; the P3D
# carries the 1st regiment's number, the config sets each regiment's own (gen_numeros_por.py)
POR_BLEND = r"source\models\shakos\hcl_shako_uk\hcl_shako_uk_texturas_por.blend"
for tg, num0 in (("por_batalhao", "l01"), ("por_granadeiro", "l01"), ("por_ligeira", "l01"), ("por_cacadores", "c01")):
    name = f"HCL_Shako_UK_{tg}_LOD0"
    o = next(x for x in append(os.path.join(ROOT, POR_BLEND), [name]) if x.name.startswith(name))
    headgear(o, (DATA + rf"\hcl_shako_uk_{tg}_co.paa", DATA + rf"\hcl_shako_uk_{tg}.rvmat"), f"hcl_h_uk_{tg}.p3d", tg,
             lod2_decimate=0.4, numero=(DATA + rf"\hcl_por_numero_{num0}_co.paa", DATA + r"\hcl_por_numero.rvmat"))
# Highland feather bonnet (bonnet_highland_uk.py + texturizar_shako_uk.py nome=HCL_UK_ textura=hcl_uk_): Res 1 full,
# Res 2 without the feather fronds (the shell carries the feather texture), like the French bearskins
BONNET_BLEND = r"source\models\bonnet\hcl_bonnet_uk\hcl_bonnet_uk_texturas.blend"
o = next(x for x in append(os.path.join(ROOT, BONNET_BLEND), ["HCL_UK_bonnet_highland_LOD0"]) if x.name.startswith("HCL_UK_bonnet_highland"))
kinds = o["hcl_kinds"].split(",")
fur = {i for i, k in enumerate(kinds) if k == "pena:pelo"}
ka = o.data.attributes["hcl_kind_i"].data
headgear(o, (DATA + r"\hcl_uk_bonnet_highland_co.paa", DATA + r"\hcl_uk_bonnet_highland.rvmat"), "hcl_h_uk_bonnet_highland.p3d",
         "bonnet_highland", lod2_polys=[p.index for p in o.data.polygons if ka[p.index].value not in fur])

# ---------------------------------------------------------------- vest and knapsack (production meshes)
for ob_name, base in (("HCL_V_Fr1812_Correame_LOD0", "hcl_v_uk1812_correame"),
                      ("HCL_B_Fr1812_Havresac_LOD0", "hcl_b_uk1812_mochila")):
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
