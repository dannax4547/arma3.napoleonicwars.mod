# Phase 7 of the Russian army greatcoat 1812 (build_capote_rus.py, textures generate_uniform_textures_rus.py): weights,
# visual LODs, shadow, editable P3D (MLOD) and .rvmat. Same method as the coat (build_p3d_uniforme_rus.py, left
# untouched); report: docs/reports/capote_rus_p3d.md.
#   blender -b --factory-startup --python build_p3d_capote_rus.py -- <project root> <template .p3d> <render dir>
# 1. WEIGHTS. The greatcoat is the French greatcoat mesh (build_capote_fr.py) with buttons and cuff flaps deleted, the
#    collar lowered and the legs made flush with the gaiters (build_capote_rus.py): the vertex count differs, so the
#    approved French weights (source/models/pesos/hcl_fr_capote_pesos.blend, the ones of hcl_u_fr1812_capote.p3d) go
#    over BY POSITION, not by index. A vertex at the place of a French vertex (< 0.01 mm) takes its weights; a vertex
#    that build_capote_rus.py moved (collar, trousers) takes the weights of the nearest point of the same French part,
#    blended over that triangle; every new button takes the weights of the nearest vertex of the cloth under it. At most
#    4 bones per vertex, normalized. Saved in source/models/pesos/hcl_rus_capote_pesos.blend.
# 2. P3D, 3. SHADOW, 4. .RVMAT: as the coat. Res 1 = the greatcoat; Res 2, 3, 4 = ~50 %, 25 %, 10 %, part by part;
#    "Camo" = every garment face (hiddenSelectionsTextures of the 4 variants C01-C04, decision RU11); the template's
#    body shadow volumes, Geometry, Memory and the rest from 10000 up; one .rvmat per physical material.
import bpy, bmesh, sys, os, math
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse
from p3d_build_common import lod_from_mesh, merge_template_extras, finish, props_of, proxy_faces, save

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, TPL, REN = [os.path.abspath(x) for x in a[:3]]
J = lambda *p: os.path.join(ROOT, *p)
COAT = J("source", "models", "coats", "hcl_capote_rus", "hcl_capote_rus_LOD0.blend")
PES_FR = J("source", "models", "pesos", "hcl_fr_capote_pesos.blend")
PES_OUT = J("source", "models", "pesos", "hcl_rus_capote_pesos.blend")
OUT = J("source", "addon", "hcl", "hcl_rus")
TEX = J("source", "textures", "hcl_capote_rus")
os.makedirs(os.path.join(OUT, "data"), exist_ok=True); os.makedirs(REN, exist_ok=True)
PREFIX = r"hcl\hcl_rus"
DATA = PREFIX + r"\data"
BASE = "hcl_u_rus1812_capote"
NAME = "HCL_U_RUS1812_Capote_LOD0"
MIN_PART = 80                                          # triangles kept at least per part in the reduced LODs
LODS = [(2.0, 0.50, False), (3.0, 0.25, True), (4.0, 0.10, True)]       # resolution, share, drop buttons
MAX_BONES = 4
OVERLAP_K = 2.0                                        # share of the overlapping cloth at Res 3-4 (see lod_object)
MIN_OVERLAP = 300                                      # and its floor: with 80 the skirt halves fold through at Res 4
LOG = []


def log(s):
    print(s); LOG.append(s)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def append(path, names):
    with bpy.data.libraries.load(path, link=False) as (s, d):
        d.objects = [n for n in s.objects if n in names]
    for o in d.objects:
        sc.collection.objects.link(o)
    return {o.name: o for o in d.objects}


ru = append(COAT, [NAME])[NAME]
fr = append(PES_FR, ["HCL_U_Fr1812_Capote_LOD0"])["HCL_U_Fr1812_Capote_LOD0"]
parts = ru["hcl_partes"].split(",")
assert parts == fr["hcl_partes"].split(","), "partes diferentes"
PID = {n: i for i, n in enumerate(parts)}
OVERLAP = {PID["saia_E"], PID["saia_D"], PID["casaco_corpo"]}


def components(me, pid):
    pa_ = me.attributes["hcl_part"].data
    adj = {}
    for p in me.polygons:
        if pa_[p.index].value == pid:
            vs = list(p.vertices)
            for v in vs:
                adj.setdefault(v, set()).update(vs)
    seen, comps = set(), []
    for v in adj:
        if v in seen:
            continue
        st, comp = [v], []
        seen.add(v)
        while st:
            x = st.pop(); comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); st.append(y)
        comps.append(comp)
    return comps


def vpart(me):
    pa_ = me.attributes["hcl_part"].data
    vp_ = {}
    for p in me.polygons:
        for v in p.vertices:
            vp_.setdefault(v, pa_[p.index].value)
    return vp_


def blend(ws, ks):
    out = {}
    for w, k in zip(ws, ks):
        for g, x in w.items():
            out[g] = out.get(g, 0.0) + x * k
    return out


def bary(p, a_, b_, c_):
    v0, v1, v2 = b_ - a_, c_ - a_, p - a_
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-18:
        return (1.0, 0.0, 0.0)
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    k = [max(0.0, 1 - v - w), max(0.0, v), max(0.0, w)]
    s = sum(k) or 1.0
    return tuple(x / s for x in k)


# ---------------------------------------------------------------- 1. weights (by position)
pa = ru.data.attributes["hcl_part"].data
gnames = [g.name for g in fr.vertex_groups]
for g in list(ru.vertex_groups):
    ru.vertex_groups.remove(g)
G = [ru.vertex_groups.new(name=n) for n in gnames]
WF = [{g.group: g.weight for g in v.groups if g.weight > 0} for v in fr.data.vertices]
kd_fr = KDTree(len(fr.data.vertices))
for v in fr.data.vertices:
    kd_fr.insert(v.co, v.index)
kd_fr.balance()
fpa = fr.data.attributes["hcl_part"].data
fr.data.calc_loop_triangles()
tri_of = {}
for t in fr.data.loop_triangles:
    tri_of.setdefault(fpa[t.polygon_index].value, []).append(tuple(t.vertices))
fco = [v.co.copy() for v in fr.data.vertices]
bvh_of = {pid: BVHTree.FromPolygons(fco, ts) for pid, ts in tri_of.items()}

vp = vpart(ru.data)
btn_v = {i for c in components(ru.data, PID["botoes"]) for i in c}
W = [None] * len(ru.data.vertices)
same, moved = 0, {}
for v in ru.data.vertices:
    if v.index in btn_v:
        continue
    _, j, d = kd_fr.find(v.co)
    if d < 1e-5:
        W[v.index] = dict(WF[j]); same += 1
        continue
    pid = vp[v.index]
    loc, _, fi, dist = bvh_of[pid].find_nearest(v.co)
    t = tri_of[pid][fi]
    W[v.index] = blend([WF[i] for i in t], bary(loc, *(fco[i] for i in t)))
    m = moved.setdefault(parts[pid], [0, 0.0]); m[0] += 1; m[1] = max(m[1], dist)
host = [i for p in ru.data.polygons if pa[p.index].value in
        (PID["casaco_corpo"], PID["saia_E"], PID["saia_D"], PID["aba_E"], PID["aba_D"]) for i in p.vertices]
kd = KDTree(len(host))
for i in set(host):
    kd.insert(ru.data.vertices[i].co, i)
kd.balance()
kept_btn = new_btn = 0
for comp in components(ru.data, PID["botoes"]):
    hits = [kd_fr.find(ru.data.vertices[i].co) for i in comp]
    if max(h[2] for h in hits) < 1e-5:                 # a French button left in place (shoulder straps, gaiters...)
        for i, h in zip(comp, hits):
            W[i] = dict(WF[h[1]])
        kept_btn += 1
        continue
    c = sum((ru.data.vertices[i].co for i in comp), Vector()) / len(comp)
    _, j, _ = kd.find(c)
    for i in comp:
        W[i] = dict(W[j])
    new_btn += 1
assert all(W), "vertice sem peso"
nb_max = 0
for i, w in enumerate(W):
    nb_max = max(nb_max, len(w))
    top = dict(sorted(w.items(), key=lambda x: -x[1])[:MAX_BONES])
    s = sum(top.values())
    W[i] = {g: x / s for g, x in top.items()}
for i, w in enumerate(W):
    for gi, wt in w.items():
        G[gi].add([i], wt, "REPLACE")
sums = [sum(w.values()) for w in W]
log(f"PESOS: {len(gnames)} grupos de hcl_fr_capote_pesos.blend; {same} vertices no lugar de um vertice frances; "
    + "; ".join(f"{n}: {c} movidos (ate {d * 1000:.1f} mm da peca francesa)" for n, (c, d) in sorted(moved.items()))
    + f"; botoes: {kept_btn} no lugar, {new_btn} novos pelo pano sob eles; ossos por vertice {nb_max} -> ate {MAX_BONES}; "
    f"soma {min(sums):.3f}..{max(sums):.3f}")
ru["hcl_pesos"] = "hcl_fr_capote_pesos.blend por posicao (build_p3d_capote_rus.py, 2026-10-31)"
bpy.data.objects.remove(fr, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=PES_OUT, copy=True)
log(f"SALVO {PES_OUT}")


# ---------------------------------------------------------------- 2. LOD meshes (part by part, weights kept)
def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def part_object(src, keep_faces, name):
    o = src.copy(); o.data = src.data.copy(); o.name = name
    sc.collection.objects.link(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep_faces], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(o.data); bm.free()
    return o


def collapsed(o, ratio):
    md = o.modifiers.new("dec", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.ratio = ratio
    md.use_collapse_triangulate = True
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    o.modifiers.remove(md)
    return me


def lod_object(share, drop_buttons, name):
    by_part = {}
    for p in ru.data.polygons:
        pid = pa[p.index].value
        if drop_buttons and pid == PID["botoes"]:
            continue
        by_part.setdefault(pid, set()).add(p.index)
    pos = [part_object(ru, fs, f"tmp_{pid}") for pid, fs in by_part.items()]
    target = share * tris(ru.data)
    lo, hi, best = 0.02, 1.0, None
    for _ in range(14):
        r = (lo + hi) / 2
        # Res 3 and 4: the hands (tiny at that distance) at half the ratio; the skirt halves (saia_E over saia_D)
        # and the body under them at OVERLAP_K x the ratio, so the under half does not fold through the upper one;
        # every part keeps at least MIN_PART triangles (a ring such as the collar breaks below that)
        ms = [collapsed(o, min(1.0, max(r * (OVERLAP_K if drop_buttons and pid in OVERLAP else
                                             0.5 if drop_buttons and pid == PID["maos_template"] else 1.0),
                                        (MIN_OVERLAP if pid in OVERLAP else MIN_PART) / max(1, tris(o.data)))))
              for pid, o in zip(by_part, pos)]
        n = sum(tris(m) for m in ms)
        if best:
            for m in best:
                bpy.data.meshes.remove(m)
        best = ms
        if n > target:
            hi = r
        else:
            lo = r
    objs = []
    for o, m in zip(pos, best):
        no = bpy.data.objects.new(o.name + "_d", m)
        sc.collection.objects.link(no)
        for g in ru.vertex_groups:                         # same order: the deform indices of the mesh stay valid
            no.vertex_groups.new(name=g.name)
        objs.append(no)
    for o in pos:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in sc.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    out = bpy.context.view_layer.objects.active
    out.name = name
    return out


# ---------------------------------------------------------------- 3. P3D
tpl = parse(TPL)
T1 = next(x for x in tpl["lods"] if abs(x["res"] - 1.0) < 1e-6)
TV = next(x for x in tpl["lods"] if abs(x["res"] - 1100) < 0.5)
np1 = len(T1["points"])
hl_sel = next(b for a_, n, b in T1["tags"] if n == b"hl")
hl_tex = next((f["tex"].decode("latin-1"), f["mat"].decode("latin-1")) for k, f in enumerate(T1["faces"]) if hl_sel[np1 + k])
kept = [x for x in tpl["lods"] if x["res"] >= 10000]
log(f"MODELO {os.path.basename(TPL)}: maos {hl_tex}; {len(proxy_faces(T1))} proxies no Res 1; LODs mantidos "
    + ", ".join(f"{x['res']:.6g}" for x in kept))

RV_OF = {"HCL_la_azul": "la", "HCL_la_vermelha": "la", "HCL_la_branca": "la", "HCL_la_cinza": "la",
         "HCL_polaina_preta": "la", "HCL_couro_sapato": "couro", "HCL_sola": "couro", "HCL_latao": "latao"}
RV = {"la": dict(spec=(0.4, 0.4, 0.4), power=50),            # the project's uniform .rvmat (hcl_u_fr1812.rvmat)
      "couro": dict(spec=(1.0, 1.0, 1.0), power=70),
      "latao": dict(spec=(1.0, 0.82, 0.55), power=90)}
RVMAT = """// Historical Clothing - Russian greatcoat 1812 ({mat}). Structure of the official Arma 3 Samples material
// (Addons\\Test_scope3D_01\\Data\\nodiffuse.rvmat, "Super" shader), as the project's other .rvmat; values are ours
// (build_p3d_capote_rus.py: wool = the project's uniforms, leather and brass estimated), _smdi per texel.
ambient[]={{1,1,1,1}};
diffuse[]={{1,1,1,1}};
forcedDiffuse[]={{0,0,0,0}};
emmisive[]={{0,0,0,1}};
specular[]={{{s0},{s1},{s2},1}};
specularPower={power};
PixelShaderID="Super";
VertexShaderID="Super";
{stages}"""
UVT = """
	class uvTransform
	{
		aside[]={1.0,0.0,0.0};
		up[]={0.0,1.0,0.0};
		dir[]={0.0,0.0,0.0};
		pos[]={0.0,0.0,0.0};
	};"""


def write_rvmat(mat):
    st = [(DATA + f"\\{BASE}_nohq.paa", "tex"), ("#(argb,8,8,3)color(0.5,0.5,0.5,0.5,DT)", "tex"),
          ("#(argb,8,8,3)color(1,1,1,0.0,MC)", "tex"), ("#(argb,8,8,3)color(1,1,1,1,AS)", "tex"),
          (DATA + f"\\{BASE}_smdi.paa", "tex"), ("#(ai,64,64,1)fresnel(1.4,0.1)", "none"),
          ("A3\\Data_f\\env_land_co.tga", "tex")]
    stages = ""
    for i, (tex, uv) in enumerate(st, 1):
        extra = "\n\tuseWorldEnvMap=false;" if i == 7 else ""
        stages += f"class Stage{i}\n{{\n\ttexture=\"{tex}\";{extra}\n\tuvSource=\"{uv}\";{UVT if uv == 'tex' else ''}\n}};\n"
    r = RV[mat]
    name = f"{BASE}_{mat}.rvmat"
    open(os.path.join(OUT, "data", name), "w", encoding="utf-8", newline="\r\n").write(
        RVMAT.format(mat=mat, s0=r["spec"][0], s1=r["spec"][1], s2=r["spec"][2], power=r["power"], stages=stages))
    return DATA + "\\" + name


rv_path = {m: write_rvmat(m) for m in RV}
CO = DATA + f"\\{BASE}_v01_co.paa"                        # C01; the config swaps it per variant (Camo)


def build_lod(ob, res, T):
    mats = [m.name for m in ob.data.materials]
    hands = {p.index for p in ob.data.polygons if mats[p.material_index] == "HCL_pele_hl"}
    garment = {p.index for p in ob.data.polygons} - hands
    ftex = lambda pi: hl_tex if pi in hands else (CO, rv_path[RV_OF[mats[ob.data.polygons[pi].material_index]]])
    L = lod_from_mesh(ob, res, props_of(T), ftex, {"Camo": garment, "hl": hands, "injury_hands": hands})
    npx = merge_template_extras(L, T, lambda k, P=proxy_faces(T): k in P)
    return L, npx, len(hands)


ru.data.uv_layers.active = ru.data.uv_layers[0]
lods, counts = [], []
L1, npx, nh = build_lod(ru, 1.0, T1)
lods.append(L1); counts.append(tris(ru.data))
lod_objs = [ru]
for res, share, drop in LODS:
    o = lod_object(share, drop, f"{NAME}_RES{res:.0f}")
    o.data.uv_layers.active = o.data.uv_layers[0]
    L, npx_k, nh_k = build_lod(o, res, T1)
    lods.append(L); counts.append(tris(o.data)); lod_objs.append(o)
    wsum = [sum(g.weight for g in v.groups) for v in o.data.vertices]
    log(f"  Res {res:.0f}: {counts[-1]} triangulos; maos {nh_k} faces; proxies {npx_k}; vertices sem peso "
        f"{sum(1 for s in wsum if s < 1e-6)}; soma dos pesos {min(wsum):.3f}..{max(wsum):.3f}")
LV, npx_v, _ = build_lod(ru, TV["res"], TV)
bones = sorted(n for n in L1["sels"] if n not in ("Camo", "hl", "injury_hands") and not n.lower().startswith("proxy"))
model = {"version": tpl["version"], "lods": [finish(L) for L in lods] + [finish(LV)] + kept, "tail": tpl.get("tail", b"")}
log(f"CAPOTE {BASE}: Res 1-4 {' / '.join(str(c) for c in counts)} triangulos "
    f"({' / '.join(f'{c / counts[0] * 100:.0f} %' for c in counts)}); View Pilot {counts[0]} (+{npx_v} proxies); "
    f"proxies {npx} no Res 1; {len(bones)} selecoes de ossos; maos {nh} faces no Res 1")
save(model, os.path.join(OUT, BASE + ".p3d"), log)

# ---------------------------------------------------------------- 4. preview: Res 1-4 side by side (C01 texture)
m = bpy.data.materials.new("prev"); m.use_nodes = True
nt = m.node_tree; b = nt.nodes["Principled BSDF"]
t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, f"{BASE}_v01_co.png"))
nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.8
skin = bpy.data.materials.new("pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.6, 0.5, 1)
for o in sc.objects:
    o.hide_render = True
for i, o in enumerate(lod_objs):
    c = o.copy(); c.data = o.data.copy(); sc.collection.objects.link(c)
    for k, slot in enumerate(c.material_slots):
        slot.link = "OBJECT"
        slot.material = skin if c.data.materials[k] and c.data.materials[k].name == "HCL_pele_hl" else m
    c.location.x = 1.5 * i; c.hide_render = False
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 6.4
cam.location = (2.25, -6.0, 0.0); cam.rotation_euler = (math.radians(90), 0, 0)
for nm, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200))):
    lo_ = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); lo_.data.energy = en
    lo_.rotation_euler = tuple(math.radians(x) for x in rot); sc.collection.objects.link(lo_)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.8, 1); sc.world = w
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 32
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y = 2400, 1300
sc.render.filepath = os.path.join(REN, "lods_capote_rus.png")
bpy.ops.render.render(write_still=True)
open(os.path.join(OUT, "build_p3d_capote_rus_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
print("FIM")
