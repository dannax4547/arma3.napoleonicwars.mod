# Builds the editable P3D models (MLOD) of the in-game TEST addon hcl_pruss, on top of the official templates of the
# Arma 3 Samples (Test_Character_01, modding licence: non-commercial Arma 3 content). Written with p3d_mlod_io.py,
# whose writer reproduces all 34 MLOD files of the Samples byte for byte. Blender only supplies the meshes and weights.
#   uniform  hcl_u_pruss1813.p3d : character template; Resolution 1 and View Pilot replaced by the uniform (with the
#                                   template hands and all template proxies); template Res 2-4 dropped (they show the
#                                   template's bare body); shadow, Geometry, Memory, LandContact, HitPoints and Fire
#                                   Geometry kept from the template
#   shakos   hcl_h_pruss_{fwr,aguia,estrela}.p3d : headgear template; Res 1 = shako, shadow = convex hull, rigid on Head
#   vest     hcl_v_pruss1813_correame.p3d, knapsack hcl_b_pruss1813_tornister.p3d : vest template; Res 1 = production
#                                   mesh (build_equipamento_producao.py) with its UV atlas, texture and material, weights
#                                   from teste_movimentos.py (pesos_out); a blockout in the weights file falls back to
#                                   flat procedural colours
#   blender -b --factory-startup --python build_p3d_pruss.py -- <project root> <samples dir> <addon dir>
#   (normally called by build_mod_pruss.ps1 with <addon dir> = source/addon/hcl/hcl_pruss)
import bpy, bmesh, sys, os, struct
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse, write, tag, weight_byte, get_tag

ROOT, SAMPLES, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
TC = os.path.join(SAMPLES, r"Addons\Test_Character_01")
PREFIX = r"hcl\hcl_pruss"
DATA = PREFIX + r"\data"
LOG = []


def log(s):
    print(s); LOG.append(s)


def append(path, names):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in names]
    return list(dst.objects)


def to_p3d(v):
    return (v[0], v[2], v[1])                       # inverse of p3d_mlod.to_blender (y and z swapped)


# ---------------------------------------------------------------- conventions checked on the official files
tpl = parse(os.path.join(TC, "A3_character_template.p3d"))
hg = parse(os.path.join(TC, "A3_headgear_example.p3d"))
b = get_tag(hg["lods"][0], "Head")
log(f"CHECK headgear example 'Head' point bytes: {sorted(set(b[:len(hg['lods'][0]['points'])]))} (1 = full weight)")
L0 = tpl["lods"][0]
npts = len(L0["points"])
sel = get_tag(L0, "LeftHand")
inpts = {i for i in range(npts) if sel[i]}
full = sum(1 for f in L0["faces"] if all(v[0] in inpts for v in f["verts"][:f["n"]]))
marked = sum(1 for k in range(len(L0["faces"])) if sel[npts + k])
log(f"CHECK template 'LeftHand': faces marked {marked}, faces with all points in it {full} (rule used: all points in)")


# ---------------------------------------------------------------- generic LOD builder from a Blender mesh
def lod_from_mesh(ob, res, props, face_tex, sel_extra, weights=True, uv=True):
    """ob: Blender mesh object (rest pose, character space). face_tex(poly_index) -> (texture, material).
    sel_extra: {name: set(poly_index)} extra named selections (points = points of those faces)."""
    me = ob.data
    me.calc_loop_triangles()
    cn = me.corner_normals
    uvl = me.uv_layers.active.uv if (uv and me.uv_layers.active) else None
    pts = [to_p3d(v.co) + (0,) for v in me.vertices]
    nidx, normals, faces, fpoly = {}, [], [], []
    for t in me.loop_triangles:
        verts = []
        for li, vi in zip(t.loops, t.vertices):
            n = cn[li].vector
            key = (round(-n.x, 5), round(-n.z, 5), round(-n.y, 5))        # P3D stores the normal of the stored order
            if key not in nidx:
                nidx[key] = len(normals); normals.append(key)
            u, v = (uvl[li].vector.x, 1.0 - uvl[li].vector.y) if uvl else (0.0, 0.0)
            verts.append((vi, nidx[key], u, v))
        verts.append((0, 0, 0.0, 0.0))
        tex, mat = face_tex(t.polygon_index)
        faces.append({"n": 3, "verts": verts, "flags": 0, "tex": tex.encode("latin-1"), "mat": mat.encode("latin-1")})
        fpoly.append(t.polygon_index)
    np_, nf = len(pts), len(faces)
    sels = {}
    if weights:
        names = {g.index: g.name for g in ob.vertex_groups}
        pb = {}
        for v in me.vertices:
            for g in v.groups:
                if g.weight > 0:
                    pb.setdefault(names[g.group], {})[v.index] = weight_byte(g.weight)
        for name, d in pb.items():
            fb = [k for k, f in enumerate(faces) if all(x[0] in d for x in f["verts"][:3])]
            sels[name] = (d, fb)
    for name, polys in sel_extra.items():
        fb = [k for k in range(nf) if fpoly[k] in polys]
        d = {x[0]: 1 for k in fb for x in faces[k]["verts"][:3]}
        sels[name] = (d, fb)
    return {"major": 0x1C, "minor": 0x100, "flags": 0, "points": pts, "normals": normals, "faces": faces,
            "sels": sels, "props": props, "res": res}


def merge_template_extras(L, T, keep_face):
    """Append to L the faces of template LOD T for which keep_face(face_index) is true (proxies), with their points,
    normals, point flags and the bytes of every template selection that contains them."""
    tnp = len(T["points"])
    fidx = [k for k in range(len(T["faces"])) if keep_face(k)]
    pmap, nmap = {}, {}
    for k in fidx:
        for v in T["faces"][k]["verts"][:T["faces"][k]["n"]]:
            if v[0] not in pmap:
                pmap[v[0]] = len(L["points"]); L["points"].append(T["points"][v[0]])
            if v[1] not in nmap:
                nmap[v[1]] = len(L["normals"]); L["normals"].append(T["normals"][v[1]])
    fmap = {}
    for k in fidx:
        f = T["faces"][k]
        verts = [(pmap[v[0]], nmap[v[1]], v[2], v[3]) if j < f["n"] else v for j, v in enumerate(f["verts"])]
        fmap[k] = len(L["faces"])
        L["faces"].append(dict(f, verts=verts))
    lower = {n.lower(): n for n in L["sels"]}
    for a, name, blob in T["tags"]:
        if name.startswith(b"#"):
            continue
        nm = name.decode("latin-1")
        d = {pmap[i]: blob[i] for i in pmap if blob[i]}
        fb = [fmap[k] for k in fidx if blob[tnp + k]]
        if not d and not fb:
            continue
        key = lower.get(nm.lower(), nm)
        if key not in L["sels"]:
            L["sels"][key] = ({}, []); lower[nm.lower()] = key
        L["sels"][key][0].update(d); L["sels"][key][1].extend(fb)
    return len(fidx)


def finish(L):
    """Turn a built LOD into the raw MLOD layout (tags: selections, properties, UV set 0, end of file)."""
    np_, nf = len(L["points"]), len(L["faces"])
    tags = []
    for name, (d, fb) in L["sels"].items():
        pb = bytearray(np_); fbb = bytearray(nf)
        for i, bb in d.items():
            pb[i] = bb
        for k in fb:
            fbb[k] = 1
        tags.append(tag(name, bytes(pb) + bytes(fbb)))
    for blob in L["props"]:
        tags.append(tag("#Property#", blob))
    uvs = bytearray(struct.pack("<I", 0))
    for f in L["faces"]:
        for v in f["verts"][:f["n"]]:
            uvs += struct.pack("<ff", v[2], v[3])
    tags.append(tag("#UVSet#", bytes(uvs)))
    tags.append(tag("#EndOfFile#", b""))
    return {"major": L["major"], "minor": L["minor"], "flags": L["flags"], "points": L["points"],
            "normals": L["normals"], "faces": L["faces"], "tags": tags, "res": L["res"]}


def props_of(T):
    return [blob for a, n, blob in T["tags"] if n == b"#Property#"]


def proxy_faces(T):
    np_ = len(T["points"])
    out = set()
    for a, n, blob in T["tags"]:
        if n.lower().startswith(b"proxy:"):
            out.update(k for k in range(len(T["faces"])) if blob[np_ + k])
    return out


def save(model, name):
    p = os.path.join(OUT, name)
    write(model, p)
    back = parse(p)                                                     # read back: structure must survive
    log(f"P3D {name}: {len(back['lods'])} LODs " + ", ".join(
        f"{L['res']:.6g}:{len(L['points'])}p/{len(L['faces'])}f" for L in back["lods"]))


# ---------------------------------------------------------------- uniform
# newest weights first: v2 = layers ride together (2026-10-11), v1 = production equipment, v0 = first transfer
PES = next(p for p in (os.path.join(ROOT, rf"source\models\pesos\hcl_pruss_pesos_v{k}.blend") for k in (2, 1, 0))
           if os.path.exists(p))
with bpy.data.libraries.load(PES, link=False) as (src_, dst_):
    names_ = [n for n in src_.objects if n.startswith(("HCL_U_Pruss1813_01_LOD0", "HCL_V_", "HCL_B_"))]
objs = {o.name: o for o in append(PES, names_)}
log(f"PESOS {os.path.basename(PES)}: {sorted(objs)}")
uni = next(o for n, o in objs.items() if n.startswith("HCL_U_"))
parts = uni["hcl_partes"].split(",")
HANDS = parts.index("maos_template")
pa = uni.data.attributes["hcl_part"].data
hand_polys = {p.index for p in uni.data.polygons if pa[p.index].value == HANDS}
garment_polys = {p.index for p in uni.data.polygons} - hand_polys
T1 = tpl["lods"][0]
hl_tex = next((f["tex"].decode(), f["mat"].decode()) for f in T1["faces"] if f["tex"])
log(f"UNIFORME template hand texture/material kept: {hl_tex}")
U_TEX = (DATA + r"\hcl_u_pruss1813_v01_co.paa", DATA + r"\hcl_u_pruss1813.rvmat")
face_tex_u = lambda pi: hl_tex if pi in hand_polys else U_TEX

# check the face order and UV convention on the template hands (same faces in both files)
L = lod_from_mesh(uni, 1.0, props_of(T1), face_tex_u, {"Camo": garment_polys, "hl": hand_polys, "injury_hands": hand_polys})
tp = np.array([p[:3] for p in T1["points"]])
from mathutils.kdtree import KDTree
kd = KDTree(len(tp))
for i, p in enumerate(tp):
    kd.insert(p, i)
kd.balance()
tface = {}
for f in T1["faces"]:
    key = tuple(sorted(v[0] for v in f["verts"][:3]))
    tface[key] = f
same_order = same_uv = checked = 0
for f in L["faces"]:
    if f["tex"].decode() != hl_tex[0]:
        continue
    ids = []
    for v in f["verts"][:3]:
        co, i, d = kd.find(L["points"][v[0]][:3])
        ids.append(i if d < 1e-5 else None)
    if None in ids or tuple(sorted(ids)) not in tface:
        continue
    tf = tface[tuple(sorted(ids))]
    torder = [v[0] for v in tf["verts"][:3]]
    k0 = torder.index(ids[0])
    same_order += torder[k0:] + torder[:k0] == ids
    tuv = {v[0]: (v[2], v[3]) for v in tf["verts"][:3]}
    same_uv += all(abs(tuv[i][0] - v[2]) < 2e-3 and abs(tuv[i][1] - v[3]) < 2e-3 for i, v in zip(ids, f["verts"][:3]))
    checked += 1
log(f"CHECK hands vs template Res 1: {checked} faces matched; same vertex order {same_order}; same UV {same_uv}")

res1 = L
n_px = merge_template_extras(res1, T1, lambda k, P=proxy_faces(T1): k in P)
TV = next(x for x in tpl["lods"] if abs(x["res"] - 1100) < 0.5)
vp = lod_from_mesh(uni, TV["res"], props_of(TV), face_tex_u, {"Camo": garment_polys, "hl": hand_polys,
                                                              "injury_hands": hand_polys})
n_px2 = merge_template_extras(vp, TV, lambda k, P=proxy_faces(TV): k in P)
log(f"UNIFORME Res 1: {len(res1['faces'])} faces ({n_px} proxy faces from the template); View Pilot: "
    f"{len(vp['faces'])} faces ({n_px2} proxy)")
kept = [x for x in tpl["lods"] if x["res"] >= 10000]               # shadows and the technical LODs, unchanged
model = {"version": tpl["version"], "lods": [finish(res1), finish(vp)] + kept, "tail": tpl.get("tail", b"")}
save(model, "hcl_u_pruss1813.p3d")


# ---------------------------------------------------------------- shakos (rigid on Head)
hgt = parse(os.path.join(TC, "A3_headgear_template.p3d"))
SHK = {"fwr": (r"source\models\shakos\hcl_shako_pruss\hcl_shako_pruss_LOD0.blend", "hcl_shako_pruss_co.paa", "hcl_shako_pruss.rvmat"),
       "aguia": (r"source\models\shakos\hcl_shako_pruss\variantes\hcl_shako_pruss_aguia_LOD0.blend",
                 "hcl_shako_pruss_aguia_amarela_co.paa", "hcl_shako_pruss_aguia.rvmat"),
       "estrela": (r"source\models\shakos\hcl_shako_pruss\variantes\hcl_shako_pruss_estrela_LOD0.blend",
                   "hcl_shako_pruss_estrela_prata_co.paa", "hcl_shako_pruss_estrela.rvmat")}
for key, (path, co, rv) in SHK.items():
    o = next(x for x in append(os.path.join(ROOT, path), ["HCL_Shako_Pruss_LOD0"]) if x.name.startswith("HCL_Shako"))
    allp = {p.index for p in o.data.polygons}
    Lr = lod_from_mesh(o, 1.0, props_of(hgt["lods"][0]), lambda pi: (DATA + "\\" + co, DATA + "\\" + rv),
                       {"camo": allp}, weights=False)
    Lr["sels"]["Head"] = ({i: 1 for i in range(len(Lr["points"]))}, list(range(len(Lr["faces"]))))
    # shadow volume: closed convex hull of the shako, rigid on Head
    bm = bmesh.new()
    for v in o.data.vertices:
        bm.verts.new(v.co)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.triangulate(bm, faces=bm.faces)
    hm = bpy.data.meshes.new(f"sombra_{key}"); bm.to_mesh(hm); bm.free()
    ho = bpy.data.objects.new(f"sombra_{key}", hm)
    TS = next(x for x in hgt["lods"] if abs(x["res"] - 10000) < 0.5)
    Ls = lod_from_mesh(ho, TS["res"], props_of(TS), lambda pi: ("", ""), {}, weights=False, uv=False)
    Ls["sels"]["Head"] = ({i: 1 for i in range(len(Ls["points"]))}, list(range(len(Ls["faces"]))))
    lods = [finish(Lr)] + [x for x in hgt["lods"] if x["res"] >= 1000 and abs(x["res"] - 10000) > 0.5] + [finish(Ls)]
    lods.sort(key=lambda x: x["res"])
    save({"version": hgt["version"], "lods": lods, "tail": hgt.get("tail", b"")}, f"hcl_h_pruss_{key}.p3d")


# ---------------------------------------------------------------- new headgear of 2026-10-12 (rigid on Head)
# shakos with a plume (build_plumet_pruss.py): the shako (selection camo, its texture swappable) + the plume with its own
# fixed texture set; the cloth cap (blockout_bone_landwehr.py + texturizar_shako_fr.py): one model, 5 _co textures.
def combine(name, parts):
    """parts = [(object, uv layer name)] -> one mesh object (character space) and the polygon index range of each."""
    co, polys, uvs, smooth, ranges = [], [], [], [], []
    for o, uvname in parts:
        me = o.data
        off = len(co)
        co += [v.co.copy() for v in me.vertices]
        uvd = me.uv_layers[uvname].data
        start = len(polys)
        for p in me.polygons:
            polys.append([off + i for i in p.vertices])
            uvs.append([uvd[li].uv.copy() for li in p.loop_indices])
            smooth.append(p.use_smooth)
        ranges.append(range(start, len(polys)))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(c) for c in co], [], polys)
    uvl = me.uv_layers.new(name="UVMap")
    for p, puv, sm in zip(me.polygons, uvs, smooth):
        p.use_smooth = sm
        for li, uv in zip(p.loop_indices, puv):
            uvl.data[li].uv = uv
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, ranges


def headgear_p3d(o, face_tex, camo, fname, key):
    Lr = lod_from_mesh(o, 1.0, props_of(hgt["lods"][0]), face_tex, {"camo": camo}, weights=False)
    Lr["sels"]["Head"] = ({i: 1 for i in range(len(Lr["points"]))}, list(range(len(Lr["faces"]))))
    bm = bmesh.new()
    for v in o.data.vertices:
        bm.verts.new(v.co)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.triangulate(bm, faces=bm.faces)
    hm = bpy.data.meshes.new(f"sombra_{key}"); bm.to_mesh(hm); bm.free()
    ho = bpy.data.objects.new(f"sombra_{key}", hm)
    TS = next(x for x in hgt["lods"] if abs(x["res"] - 10000) < 0.5)
    Ls = lod_from_mesh(ho, TS["res"], props_of(TS), lambda pi: ("", ""), {}, weights=False, uv=False)
    Ls["sels"]["Head"] = ({i: 1 for i in range(len(Ls["points"]))}, list(range(len(Ls["faces"]))))
    lods = [finish(Lr)] + [x for x in hgt["lods"] if x["res"] >= 1000 and abs(x["res"] - 10000) > 0.5] + [finish(Ls)]
    lods.sort(key=lambda x: x["res"])
    zs = [v.co.z for v in o.data.vertices]
    log(f"BARRETINA {fname}: {len(Lr['faces'])} triangulos, z {min(zs):.3f}..{max(zs):.3f}, sombra {len(Ls['faces'])} triangulos")
    save({"version": hgt["version"], "lods": lods, "tail": hgt.get("tail", b"")}, fname)


PLU = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss\variantes\hcl_plumet_pruss.blend")
TX_PLU = (DATA + r"\hcl_plumet_pruss_co.paa", DATA + r"\hcl_plumet_pruss.rvmat")
for key, var in (("fwr", "verde"), ("aguia", "verde"), ("estrela", "verde"), ("estrela", "stutz")):
    path, co, rv = SHK[key]
    sh = next(x for x in append(os.path.join(ROOT, path), ["HCL_Shako_Pruss_LOD0"]) if x.name.startswith("HCL_Shako"))
    pl = next(x for x in append(PLU, [f"HCL_Plumet_Pruss_{key}_{var}"]) if x.name.startswith("HCL_Plumet"))
    ob, (r_sh, r_pl) = combine(f"comb_{key}_{var}", [(sh, sh.data.uv_layers.active.name), (pl, pl.data.uv_layers.active.name)])
    TX_SH = (DATA + "\\" + co, DATA + "\\" + rv)
    shp = set(r_sh)
    fname = f"hcl_h_pruss_{key}_{'plumet_verde' if var == 'verde' else 'stutz'}.p3d"
    headgear_p3d(ob, lambda pi, a=TX_SH, b_=TX_PLU, s=shp: a if pi in s else b_, shp, fname, f"{key}_{var}")
    log(f"   barretina {len(r_sh)} faces (camo, {co}) + plumet {len(r_pl)} faces (hcl_plumet_pruss_co.paa fixo)")
BONE = os.path.join(ROOT, r"source\models\shakos\hcl_bone_pruss\hcl_bone_pruss_texturas.blend")
bo = next(x for x in append(BONE, ["HCL_Bone_Pruss_azul_faixa_vermelha_LOD0"]) if x.name.startswith("HCL_Bone"))
bo.data.uv_layers.active = bo.data.uv_layers["UVMap"]
TX_BO = (DATA + r"\hcl_bone_pruss_c01_azul_vermelha_co.paa", DATA + r"\hcl_bone_pruss.rvmat")
headgear_p3d(bo, lambda pi: TX_BO, {p.index for p in bo.data.polygons}, "hcl_h_pruss_bone.p3d", "bone")


# ---------------------------------------------------------------- vest and knapsack (BLOCKOUT, flat colours)
vt = parse(os.path.join(TC, "A3_vest_template.p3d"))


def flat_tex(ob):
    cols = []
    for m in ob.data.materials:
        c = m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value if m and m.use_nodes else (0.5, 0.5, 0.5, 1)
        cols.append(f"#(argb,8,8,3)color({c[0]:.3f},{c[1]:.3f},{c[2]:.3f},1,CO)")
    mi = [p.material_index for p in ob.data.polygons]
    return lambda pi: (cols[mi[pi]], "")


for ob_name, base in (("HCL_V_Pruss1813_Correame", "hcl_v_pruss1813_correame"),
                      ("HCL_B_Pruss1813_Tornister", "hcl_b_pruss1813_tornister")):
    o = next(x for n, x in objs.items() if n.startswith(ob_name))
    allp = {p.index for p in o.data.polygons}
    prod = "hcl_partes" in o.keys() and o.data.uv_layers.get("UVMap") is not None
    if prod:
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]
        tx = (DATA + "\\" + base + "_co.paa", DATA + "\\" + base + ".rvmat")
        Lr = lod_from_mesh(o, 1.0, props_of(vt["lods"][0]), lambda pi, tx=tx: tx, {"camo": allp})
    else:
        Lr = lod_from_mesh(o, 1.0, props_of(vt["lods"][0]), flat_tex(o), {"camo": allp}, uv=False)
    fname = base + ".p3d"
    log(f"EQUIPAMENTO {o.name}: {'producao, UV e textura ' + base if prod else 'blockout, cores lisas'}; "
        f"{len(Lr['faces'])} triangulos; ossos {sorted(n for n in Lr['sels'] if n != 'camo')}")
    if prod:                                             # black-leather set: same mesh and weights, own texture/material
        txp = (DATA + "\\" + base + "_preto_co.paa", DATA + "\\" + base + "_preto.rvmat")
        Lp = lod_from_mesh(o, 1.0, props_of(vt["lods"][0]), lambda pi, tx=txp: tx, {"camo": allp})
        save({"version": vt["version"], "lods": [finish(Lp)] + [x for x in vt["lods"] if x["res"] > 1e12],
              "tail": vt.get("tail", b"")}, base + "_preto.p3d")
    lods = [finish(Lr)] + [x for x in vt["lods"] if x["res"] > 1e12]          # Res 1 + empty Geometry (autocenter 0)
    save({"version": vt["version"], "lods": lods, "tail": vt.get("tail", b"")}, fname)

open(os.path.join(OUT, "build_p3d_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
