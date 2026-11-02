# Phase 7 of the Russian kivers: editable P3D (MLOD) of each game kiver of build_kiver_rus_jogo.py, textured by
# texturizar_kiver_rus.py. Report: docs/reports/kiver_rus_p3d.md. Standards: docs/modeling_standards.md section 6 (LODs
# and properties of a head item, verified on the official A3_headgear_template.p3d).
#   blender -b --factory-startup --python build_p3d_kiver_rus.py -- <jogo .blend> <template .p3d> <addon dir> <render dir>
# The Arma 3 Samples are not installed on this machine, so <template .p3d> is a headgear the project already built FROM
# the official template (source/addon/hcl/hcl_fr/hcl_h_fr_fuzileiro_losango.p3d, build_p3d_fr.py): its View Pilot (1100)
# and Geometry (1e13) LODs are the template's, copied verbatim, and so are the LOD properties read from it.
# Per kiver (rigid on the bone Head, selection camo = every visual face, for hiddenSelectionsTextures):
#   Res 1        the game mesh (LOD0, <= 6000 triangles)
#   Res 2, 3, 4  the same mesh decimated to ~50 %, 25 %, 10 % (modeling_standards.md section 3), same UVs and atlas
#   10000        shadow volume: closed convex hulls of the kiver (body, crown, visor, cords on the body, grenade),
#                the pompom and the plume; the chin strap and the hanging cords stay out (thin, under the head)
#   1100, 1e13   View Pilot (empty) and Geometry (empty, autocenter=0, prefershadowvolume=1), from the template
# Faces carry the 1st-battalion _co (the config swaps it per battalion) and one .rvmat per physical material
# (modeling_standards.md section 5), all reading the kiver's _nohq and _smdi.
import bpy, bmesh, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse, property_blob
from p3d_build_common import lod_from_mesh, finish, save

a = sys.argv[sys.argv.index("--") + 1:]
SRC, TPL, OUT, REN = [os.path.abspath(x) for x in a[:4]]
DATA_DIR = os.path.join(OUT, "data")
os.makedirs(DATA_DIR, exist_ok=True); os.makedirs(REN, exist_ok=True)
PREFIX = r"hcl\hcl_rus"
DATA = PREFIX + r"\data"
# resolution, share of the LOD0 triangles, materials removed (inside of the kiver: sweatband and lining, not seen from
# afar), smallest part kept (bounding box diagonal: at 10 % the rosettes, tassels and raquette pieces go)
INTERIOR = ("couro_marrom", "forro")
LODS = [(2.0, 0.50, (), 0.0), (3.0, 0.25, INTERIOR, 0.0), (4.0, 0.10, INTERIOR, 0.030)]
SHADOW_GRID = 0.008                                  # m: hull points snapped to this grid (fewer shadow faces)
LOG = []


def log(s):
    print(s); LOG.append(s)


# physical material of each game-mesh material (dossier HIST-RUS-INF-KIVER-1812-001 section 7, M1-M10)
RV_OF = {"pano": "pano", "feltro": "feltro", "forro": "pano", "verniz": "verniz", "couro": "couro",
         "couro_marrom": "couro", "latao": "latao", "ferro": "latao", "branco": "la", "vermelho": "la", "verde": "la",
         "celeste": "la", "crina": "crina"}
# Super shader (structure of the project's .rvmat, from the Samples' nodiffuse.rvmat). The _smdi carries intensity (G)
# and gloss (B) per texel; here only the maximum power and the colour of the highlight change per material.
# Values are ours (estimated, to tune in Buldozer): matte wool/felt, leather, lacquer, brass with a warm highlight.
RV = {"pano":   dict(spec=(0.6, 0.6, 0.6), power=20),
      "feltro": dict(spec=(0.6, 0.6, 0.6), power=25),
      "la":     dict(spec=(0.6, 0.6, 0.6), power=18),
      "couro":  dict(spec=(1.0, 1.0, 1.0), power=60),
      "verniz": dict(spec=(1.0, 1.0, 1.0), power=140),
      "latao":  dict(spec=(1.0, 0.82, 0.55), power=90),
      "crina":  dict(spec=(0.9, 0.9, 0.9), power=60)}
RVMAT = """// Historical Clothing - Russian kiver ({mat}). Structure of the official Arma 3 Samples material
// (Addons\\Test_scope3D_01\\Data\\nodiffuse.rvmat, "Super" shader), as the project's other .rvmat; values are ours
// (build_p3d_kiver_rus.py, estimated), the _smdi gives specular and gloss per texel.
ambient[]={{1,1,1,1}};
diffuse[]={{1,1,1,1}};
forcedDiffuse[]={{0,0,0,0}};
emmisive[]={{0,0,0,1}};
specular[]={{{s0},{s1},{s2},1}};
specularPower={power};
PixelShaderID="Super";
VertexShaderID="Super";
{stages}"""
STAGE = """class Stage{i}
{{
	texture="{tex}";
	uvSource="{uv}";{transform}
}};
"""
TRANSFORM = """
	class uvTransform
	{
		aside[]={1.0,0.0,0.0};
		up[]={0.0,1.0,0.0};
		dir[]={0.0,0.0,0.0};
		pos[]={0.0,0.0,0.0};
	};"""


def write_rvmat(base, mat):
    st = [(DATA + f"\\{base}_nohq.paa", "tex"), ("#(argb,8,8,3)color(0.5,0.5,0.5,0.5,DT)", "tex"),
          ("#(argb,8,8,3)color(1,1,1,0.0,MC)", "tex"), ("#(argb,8,8,3)color(1,1,1,1,AS)", "tex"),
          (DATA + f"\\{base}_smdi.paa", "tex"), ("#(ai,64,64,1)fresnel(1.4,0.1)", "none"),
          ("A3\\Data_f\\env_land_co.tga", "tex")]
    stages = ""
    for i, (tex, uv) in enumerate(st, 1):
        s = STAGE.format(i=i, tex=tex, uv=uv, transform=TRANSFORM if uv == "tex" else "")
        if i == 7:
            s = s.replace('uvSource="tex";', 'useWorldEnvMap=false;\n\tuvSource="tex";')
        stages += s
    r = RV[mat]
    txt = RVMAT.format(mat=mat, s0=r["spec"][0], s1=r["spec"][1], s2=r["spec"][2], power=r["power"], stages=stages)
    name = f"{base}_{mat}.rvmat"
    open(os.path.join(DATA_DIR, name), "w", encoding="utf-8", newline="\r\n").write(txt)
    return DATA + "\\" + name


def kind_of(name):
    n = name.split(".")[0]
    return n[3:] if n.startswith("BO_") else n


def rigid_head(L):
    L["sels"]["Head"] = ({i: 1 for i in range(len(L["points"]))}, list(range(len(L["faces"]))))


def visual_lod(ob, res, props, face_tex):
    L = lod_from_mesh(ob, res, props, face_tex, {"camo": {p.index for p in ob.data.polygons}}, weights=False)
    rigid_head(L)
    return L


def collapse(me, ratio, name):
    """Copy of mesh me decimated (collapse) to ratio, triangulated."""
    o = bpy.data.objects.new(name, me.copy())
    bpy.context.scene.collection.objects.link(o)
    md = o.modifiers.new("dec", "DECIMATE"); md.decimate_type = "COLLAPSE"; md.ratio = ratio
    md.use_collapse_triangulate = True
    bpy.context.view_layer.update()
    out = bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(o, do_unlink=True)
    return out


def split_parts(ob, drop_kinds, min_diag):
    """One mesh per bake group (= game part, face attribute "grupo"), without the faces of drop_kinds and without the
    parts smaller than min_diag (bounding box diagonal, m)."""
    kinds = [kind_of(m.name) for m in ob.data.materials]
    bm0 = bmesh.new(); bm0.from_mesh(ob.data)
    gl = bm0.faces.layers.int.get("grupo")
    groups = sorted({f[gl] for f in bm0.faces})
    bm0.free()
    parts, dropped = [], 0
    for g in groups:
        bm = bmesh.new(); bm.from_mesh(ob.data)
        gl = bm.faces.layers.int.get("grupo")
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[gl] != g or kinds[f.material_index] in drop_kinds],
                         context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        if not bm.faces:
            bm.free(); continue
        lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)])
        hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
        if (hi - lo).length < min_diag:
            dropped += 1; bm.free(); continue
        me = bpy.data.meshes.new(f"parte_{g}"); bm.to_mesh(me); bm.free()
        for m in ob.data.materials:
            me.materials.append(m)
        parts.append(me)
    return parts, dropped


def decimated(ob, share, name, drop_kinds=(), min_diag=0.0):
    """LOD mesh with ~share of the triangles of ob: interior (drop_kinds) and small parts removed first, then every
    remaining part collapsed with one common ratio, found by bisection (parts keep their silhouette better than with
    one collapse over the whole mesh, which spent the budget on the tiny parts and broke the visor)."""
    target = share * tris(ob.data)
    parts, dropped = split_parts(ob, set(drop_kinds), min_diag)
    lo_r, hi_r, best = 0.02, 1.0, None
    for _ in range(14):
        r = (lo_r + hi_r) / 2
        meshes = [collapse(p, r, "tmp") for p in parts]
        n = sum(tris(m) for m in meshes)
        if best:
            for m in best[1]:
                bpy.data.meshes.remove(m)
        best = (n, meshes)
        if n > target:
            hi_r = r
        else:
            lo_r = r
    bm = bmesh.new()
    for m in best[1]:
        bm.from_mesh(m)                                   # appends; material indices and UVs are kept
        bpy.data.meshes.remove(m)
    for p in parts:
        bpy.data.meshes.remove(p)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in ob.data.materials:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    me.uv_layers.active = me.uv_layers[0]
    o["hcl_partes_removidas"] = dropped
    return o


def tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


def hull_mesh(point_sets, name):
    """One mesh made of the closed convex hull of each point set (points snapped to SHADOW_GRID)."""
    bm = bmesh.new()
    for pts in point_sets:
        snapped = {tuple(round(c / SHADOW_GRID) * SHADOW_GRID for c in p) for p in pts}
        if len(snapped) < 4:
            continue
        tmp = bmesh.new()
        for p in snapped:
            tmp.verts.new(p)
        bmesh.ops.convex_hull(tmp, input=tmp.verts)
        bmesh.ops.delete(tmp, geom=[v for v in tmp.verts if not v.link_faces], context="VERTS")
        bmesh.ops.triangulate(tmp, faces=tmp.faces)
        vm = {v: bm.verts.new(v.co) for v in tmp.verts}
        for f in tmp.faces:
            bm.faces.new([vm[v] for v in f.verts])
        tmp.free()
    bm.normal_update()
    open_edges = sum(1 for e in bm.edges if not e.is_manifold)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, open_edges


def shadow_sets(low, high):
    """Point sets of the shadow hulls. Groups (face attribute "grupo", Phase 4) are told apart by the materials of the
    high model: the pompom is the group with the green or red wool, the plume the group with horsehair; the rest is
    the kiver, kept above the bottom of the body (z of the lowest cloth or felt face) so the chin strap and the hanging
    cords and tassels stay out."""
    hk = [kind_of(m.name) for m in high.data.materials]
    hg = high.data.attributes["grupo"].data
    pomp = {hg[p.index].value for p in high.data.polygons if hk[p.material_index] in ("vermelho", "verde")}
    plume = {hg[p.index].value for p in high.data.polygons if hk[p.material_index] == "crina"}
    lk = [kind_of(m.name) for m in low.data.materials]
    lg = low.data.attributes["grupo"].data
    vs = low.data.vertices
    z_base = min(vs[i].co.z for p in low.data.polygons if lk[p.material_index] in ("pano", "feltro") for i in p.vertices)
    sets = {"kiver": set(), "pompom": set(), "pluma": set()}
    for p in low.data.polygons:
        g = lg[p.index].value
        key = "pompom" if g in pomp else "pluma" if g in plume else "kiver"
        for i in p.vertices:
            co = vs[i].co
            if key != "kiver" or co.z >= z_base - 0.002:
                sets[key].add(tuple(co))
    return {k: v for k, v in sets.items() if v}, z_base


# ---------------------------------------------------------------- template LODs and properties
tpl = parse(TPL)
by_res = {round(L["res"], 3): L for L in tpl["lods"]}
T1 = by_res[1.0]
extra = [L for L in tpl["lods"] if L["res"] in (1100.0,) or L["res"] > 1e12]
assert len(extra) == 2 and not any(L["points"] for L in extra), "template: View Pilot and Geometry must be empty"
props_vis = [b for a, n, b in T1["tags"] if n == b"#Property#"]
assert props_vis == [property_blob("LODNoShadow", "1")], props_vis
log(f"MODELO {os.path.basename(TPL)}: LODs " + ", ".join(f"{L['res']:.6g}" for L in tpl["lods"]) +
    "; visuais com LODNoShadow=1; View Pilot e Geometry copiados")

bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene
lows = sorted((o for o in bpy.data.objects if o.name.startswith("HCL_H_RUS") and o.name.endswith("_LOD0")),
              key=lambda o: o.name)
built = []
for low in lows:
    model = low.name[len("HCL_H_RUS"):len("HCL_H_RUS") + 4]
    var = low.name[len("HCL_H_RUS") + 5:-len("_LOD0")].lower()
    tag = f"{model}_{var}"
    base = f"hcl_kiver_rus{model}_{var}"
    high = bpy.data.objects[f"ALTA_{tag}"]
    co = DATA + f"\\{base}_co.paa"
    kinds = [kind_of(m.name) for m in low.data.materials]
    mats = sorted({RV_OF[k] for k in kinds})
    rv_path = {m: write_rvmat(base, m) for m in mats}

    def face_tex_for(ob):
        ks = [RV_OF[kind_of(m.name)] for m in ob.data.materials]
        return lambda pi: (co, rv_path[ks[ob.data.polygons[pi].material_index]])

    lods = [visual_lod(low, 1.0, props_vis, face_tex_for(low))]
    counts = [tris(low.data)]
    dec_objs = []
    for res, share, drop, min_diag in LODS:
        d = decimated(low, share, f"{low.name}_RES{res:.0f}", drop, min_diag)
        dec_objs.append(d)
        lods.append(visual_lod(d, res, props_vis, face_tex_for(d)))
        counts.append(tris(d.data))
    sets, z_base = shadow_sets(low, high)
    sh, open_edges = hull_mesh(list(sets.values()), f"SOMBRA_{tag}")
    Ls = lod_from_mesh(sh, 10000.0, [], lambda pi: ("", ""), {}, weights=False, uv=False)
    rigid_head(Ls)
    model_ = {"version": tpl["version"],
              "lods": sorted([finish(L) for L in lods] + [finish(Ls)] + extra, key=lambda L: L["res"]),
              "tail": tpl.get("tail", b"")}
    zs = [v.co.z for v in low.data.vertices]
    log(f"KIVER {tag}: Res 1-4 {' / '.join(str(c) for c in counts)} triangulos "
        f"({' / '.join(f'{c / counts[0] * 100:.0f} %' for c in counts)}); sombra {len(Ls['faces'])} triangulos em "
        f"{len(sets)} cascos ({', '.join(sets)}), arestas abertas {open_edges}; base do corpo z {z_base:.3f}; "
        f"altura {min(zs):.3f}..{max(zs):.3f}; partes removidas Res 2-4 "
        f"{'/'.join(str(d['hcl_partes_removidas']) for d in dec_objs)}; rvmat {', '.join(mats)}")
    save(model_, os.path.join(OUT, f"hcl_h_rus{model}_{var}.p3d"), log)
    built.append((tag, base, low, dec_objs, sh, counts))

# ---------------------------------------------------------------- previews: Res 1-4 and the shadow, side by side
for o in scene.objects:
    if o.type == "MESH":
        o.hide_render = True
cam = bpy.data.objects.get("cam") or bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
if cam.name not in scene.collection.objects:
    scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 48
TEX = os.path.join(os.path.dirname(SRC), "..", "..", "..", "textures", "hcl_kiver_rus")    # source/textures/...
for tag, base, low, dec_objs, sh, counts in built:
    m = bpy.data.materials.new("PREVIEW_LOD_" + tag); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(TEX, f"{base}_co.png"), check_existing=True)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6
    ms = bpy.data.materials.new("PREVIEW_SOMBRA"); ms.use_nodes = True
    ms.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.15, 0.1, 1)
    shown = []
    for i, o in enumerate([low] + dec_objs + [sh]):
        c = o.copy(); c.data = o.data.copy(); scene.collection.objects.link(c)
        c.data.materials.clear(); c.data.materials.append(ms if o is sh else m)
        c.location.x += 0.34 * i; c.hide_render = False
        shown.append(c)
    bpy.context.view_layer.update()                   # matrix_world of the moved copies
    bb =[c.matrix_world @ Vector(v) for c in shown for v in c.bound_box]
    ctr = sum(bb, Vector()) / len(bb)
    w = max(v.x for v in bb) - min(v.x for v in bb)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = w * 1.08
    d_ = Vector((0.35, -1.0, 0.25)).normalized()
    cam.location = ctr + d_ * 3.0
    cam.rotation_euler = (-d_).to_track_quat("-Z", "Y").to_euler()
    hgt = max(v.z for v in bb) - min(v.z for v in bb)
    scene.render.resolution_x, scene.render.resolution_y = 2000, int(2000 * min(1.0, hgt * 1.25 / w) + 100)
    scene.render.filepath = os.path.join(REN, f"lods_kiver_rus_{tag}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)
    for c in shown:
        bpy.data.objects.remove(c, do_unlink=True)
open(os.path.join(OUT, "build_p3d_kiver_rus_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
print("FIM")
