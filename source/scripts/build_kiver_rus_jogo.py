# Phase 4 of the Russian kivers (production / game mesh) and the bake of the high-poly detail (plaits, tassels, raquette,
# scales, bands, V straps, slit strip, loop, stitch line, visor binding, plume locks) onto it.
# Research dossier: docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md (decisions D1-D17). Report:
# docs/reports/kiver_rus_producao.md. Standards: docs/modeling_standards.md (LOD 0 of a shako <= 6,000 triangles,
# texel ~1,500-2,000 px/m, margin >= 8 px per 1024, power-of-two maps, _nohq tangent normals).
#   blender -b --factory-startup --python build_kiver_rus_jogo.py -- <out .blend> <texture dir> <render dir>
#           [samples=-] [res=2048] [ao=64] [so=<tag>[,<tag>...]]
# Both meshes come from blockout_kiver_rus.py (imported as a module): LOW = False builds the high-poly design model,
# LOW = True the game mesh, with the SAME profile functions, so the game silhouette is the one checked against the
# sources. Per variant:
#   1. high and game kivers built at x = 0 in character space; the game parts are joined into one object
#      HCL_H_RUS<model>_<variant>_LOD0, keeping a material slot per physical material (felt/cloth, lacquer, leather,
#      brass, wool, horsehair, lining) for the later .rvmat split
#   2. UV: smart project, islands scaled to one texel density, packed with an 8 px margin at RES
#   3. Cycles bakes, high -> game (selected to active, cage extrusion EXTR, max ray RAY):
#        <base>_nohq.png  tangent-space normals (OpenGL, +Y, like the Prussian/French shakos)
#        <base>_cor.png   flat base colour of the high parts (the identification palette; Phase 6 paints the
#                         materials on top of it)
#        <base>_ao.png    ambient occlusion of the high model
#   4. renders: high (left) and game mesh with its baked maps (right), front, right profile (like plate 1323), 3/4
# Texture names: hcl_kiver_rus<model>_<variant>_*.png in <texture dir> (source/textures/hcl_kiver_rus/).
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blockout_kiver_rus as K

a = sys.argv[sys.argv.index("--") + 1:]
OUT, TEX, REN = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
RES = int(OPT.get("res", 2048))
AO_S = int(OPT.get("ao", 64))
SO = set(OPT["so"].split(",")) if "so" in OPT else None
EXTR, RAY = 0.006, 0.020                                # bake cage extrusion and max ray distance (m)
MARGIN_PX = 16                                          # 8 px per 1024 (standards section 4) at 2048
BUDGET = 6000                                           # standards section 3
for d in (TEX, REN, os.path.dirname(OUT)):
    os.makedirs(d, exist_ok=True)

K.setup(OPT.get("samples", "-"))
scene = K.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
results = []


def base_name(o, tag):
    """Part name without the variant prefix ("<tag>_" for the high parts, "<tag>_jogo_" for the game parts)."""
    n = o.name
    for p in (tag + "_jogo_", tag + "_"):
        if n.startswith(p):
            return n[len(p):]
    return n


def bake_groups(lo_parts, hi_parts, tag):
    """Match every high part to the game part it is baked onto (exploded bake, like 'match by mesh name'): the game
    part with the longest name that prefixes the high part's name (pompom_centro -> pompom, sultao_mechas -> sultao,
    borla_E_0_franja -> borla_E_0, pendente_fim_0_1 -> pendente_fim_0); the chin leather goes to its scales; the
    bands, V straps, slit strip, loop and stitch line, which have no game part, are baked onto the body."""
    lo_names = {base_name(o, tag): i for i, o in enumerate(lo_parts)}
    grp_lo = {o: i for i, o in enumerate(lo_parts)}
    grp_hi = {}
    for o in hi_parts:
        b = base_name(o, tag)
        cands = [n for n in lo_names if b == n or b.startswith(n + "_")]
        if not cands and b.startswith("jugular_"):
            cands = [n for n in lo_names if n.startswith(b.rsplit("_", 1)[0])]
        grp_hi[o] = lo_names[max(cands, key=len)] if cands else lo_names["corpo"]
    return grp_lo, grp_hi


def world_copy(objs, name, groups=None, spread=0.0):
    """Join copies of objs (parented to an empty) into one mesh in world space; materials kept per slot.
    groups: object -> group index, stored per face ("grupo"); spread > 0 moves each group i by i * spread in +X
    (exploded bake)."""
    bm = bmesh.new()
    gl = bm.faces.layers.int.new("grupo")
    mats, slot_of = [], {}
    for o in objs:
        me = o.data
        tmp = bmesh.new(); tmp.from_mesh(me)
        tmp.transform(o.matrix_world)
        g = groups.get(o, 0) if groups else 0
        if spread:
            tmp.transform(Matrix.Translation(Vector((g * spread, 0, 0))))
        remap = {}
        for i, m in enumerate(me.materials):
            if m.name not in slot_of:
                slot_of[m.name] = len(mats); mats.append(m)
            remap[i] = slot_of[m.name]
        smooth = {p.index: p.use_smooth for p in me.polygons}
        vmap = {v: bm.verts.new(v.co) for v in tmp.verts}
        for f in tmp.faces:
            try:
                nf = bm.faces.new([vmap[v] for v in f.verts])
            except ValueError:
                continue
            nf.material_index = remap.get(f.material_index, 0)
            nf.smooth = smooth.get(f.index, True)
            nf[gl] = g
        tmp.free()
    # parts stay separate islands (their contacts are attachments, reported as island pairs); drop degenerates
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-7)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def select_only(objs, active):
    for o in scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def uv_unwrap(ob):
    select_only([ob], ob)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=MARGIN_PX / RES, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(margin=MARGIN_PX / RES, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")


def texel_density(ob):
    """px per metre over the whole mesh (UV area vs 3D area)."""
    me = ob.data
    uvl = me.uv_layers.active.data
    a3 = auv = 0.0
    for p in me.polygons:
        a3 += p.area
        uv = [uvl[li].uv for li in p.loop_indices]
        s = 0.0
        for i in range(len(uv)):
            x0, y0 = uv[i]; x1, y1 = uv[(i + 1) % len(uv)]
            s += x0 * y1 - x1 * y0
        auv += abs(s) / 2
    return math.sqrt(auv / a3) * RES, auv


def new_image(name, non_color):
    img = bpy.data.images.new(name, RES, RES, alpha=False, float_buffer=False)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def bake(low, high, kind, img):
    """Bake `kind` from high onto low into img: every material slot of low temporarily gets one bake material."""
    keep = list(low.data.materials)
    bm_ = bpy.data.materials.new("BAKE_" + kind); bm_.use_nodes = True
    node = bm_.node_tree.nodes.new("ShaderNodeTexImage"); node.image = img
    bm_.node_tree.nodes.active = node
    for i in range(len(low.data.materials)):
        low.data.materials[i] = bm_
    select_only([high, low], low)
    sb = scene.render.bake
    sb.use_selected_to_active = True
    sb.cage_extrusion = EXTR
    sb.max_ray_distance = RAY
    sb.margin = MARGIN_PX
    if kind == "NORMAL":
        sb.normal_space = "TANGENT"
        sb.normal_r, sb.normal_g, sb.normal_b = "POS_X", "POS_Y", "POS_Z"   # OpenGL (+Y), as the other shakos
        scene.cycles.samples = 1
        bpy.ops.object.bake(type="NORMAL")
    elif kind == "DIFFUSE":
        # metals have no diffuse colour in Cycles: bake them as dielectrics so the brass keeps its base colour
        metal = {}
        for m in high.data.materials:
            b_ = m.node_tree.nodes.get("Principled BSDF") if m and m.use_nodes else None
            if b_:
                metal[m] = b_.inputs["Metallic"].default_value
                b_.inputs["Metallic"].default_value = 0.0
        sb.use_pass_direct = False; sb.use_pass_indirect = False; sb.use_pass_color = True
        scene.cycles.samples = 1
        bpy.ops.object.bake(type="DIFFUSE")
        for m, v in metal.items():
            m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = v
    else:
        # local occlusion only (15 mm): the dense tassel fringes and plaits would otherwise bake almost black
        if scene.world is None:
            scene.world = bpy.data.worlds.new("bake_world")
        scene.world.light_settings.distance = 0.015
        scene.cycles.samples = AO_S
        # only the AO source occludes: the low mesh (up to 6 mm outside the high) and any coincident copy of the high
        # parts would otherwise block half of every hemisphere (open surfaces baked ~0.5 instead of ~1)
        RAYS = ("visible_diffuse", "visible_glossy", "visible_shadow", "visible_transmission", "visible_volume_scatter")
        rays = {o: [getattr(o, r) for r in RAYS] for o in scene.objects if o is not high}
        for o in rays:
            for r in RAYS:
                setattr(o, r, False)
        bpy.ops.object.bake(type="AO")
        for o, v in rays.items():
            for r, x in zip(RAYS, v):
                setattr(o, r, x)
    for i, m in enumerate(keep):
        low.data.materials[i] = m
    bpy.data.materials.remove(bm_)


def preview_material(low, co, nohq, ao):
    """Blender preview of the game mesh with its baked maps (not the game material: the .rvmat comes in Phase 7)."""
    m = bpy.data.materials.new("PREVIEW_" + low.name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = co
    ta = nt.nodes.new("ShaderNodeTexImage"); ta.image = ao
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    nt.links.new(tc.outputs["Color"], mix.inputs[6]); nt.links.new(ta.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = nohq
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.55
    low.data.materials.clear(); low.data.materials.append(m)


for tag, model, flames, pomp, gren in K.VARIANTS:
    if SO and tag not in SO:
        continue
    base = f"hcl_kiver_rus{model}_{tag.split('_', 1)[1]}"
    # 1. high and game kivers at x = 0
    K.LOW = False
    n0 = len(K.PARTS)
    hi_root, H = K.kiver(tag, model, flames, pomp, gren, 0.0)
    hi_parts = K.PARTS[n0:]
    K.LOW = True
    n1 = len(K.PARTS)
    lo_root, _ = K.kiver(tag + "_jogo", model, flames, pomp, gren, 0.0)
    lo_parts = K.PARTS[n1:]
    K.LOW = False
    bpy.context.view_layer.update()
    groups = {}
    for o in lo_parts:
        key = ("cordoes" if any(s in o.name for s in ("cordao", "borla", "kutas", "raquete", "pendente")) else
               "sultao" if "sultao" in o.name else "jugular" if ("jugular" in o.name or "roseta" in o.name) else
               "granada" if ("granada" in o.name or "chama" in o.name) else "corpo_topo_pala_pompom")
        groups[key] = groups.get(key, 0) + tri_count(o)
    grp_lo, grp_hi = bake_groups(lo_parts, hi_parts, tag)
    low = world_copy(lo_parts, f"HCL_H_RUS{model}_{tag.split('_', 1)[1].capitalize()}_LOD0", grp_lo)
    high = world_copy(hi_parts, f"ALTA_{tag}", grp_hi)
    SPREAD = 0.8                                         # exploded bake: groups 0.8 m apart (rays reach 20 mm)
    high_x = world_copy(hi_parts, f"ALTA_EXPLODIDA_{tag}", grp_hi, SPREAD)
    # AO source without the hair locks and tassel fringes: thin, dense cards bake near-black occlusion; their detail is
    # in the normal map already
    high_ao = world_copy([o for o in hi_parts if not o.name.endswith(("_sultao_mechas", "_franja"))], f"ALTA_AO_{tag}")
    for o in hi_parts + lo_parts + [hi_root, lo_root]:
        bpy.data.objects.remove(o, do_unlink=True)
    del K.PARTS[n0:]
    tris_lo, tris_hi = tri_count(low), tri_count(high)
    # 2. UV (on the assembled game mesh), then an exploded copy with the same UVs
    uv_unwrap(low)
    td, uv_use = texel_density(low)
    low_x = low.copy(); low_x.data = low.data.copy(); low_x.name = "JOGO_EXPLODIDO_" + tag
    scene.collection.objects.link(low_x)
    _b = bmesh.new(); _b.from_mesh(low_x.data)
    _gl = _b.faces.layers.int.get("grupo")
    _off = {}
    for f in _b.faces:
        for v in f.verts:
            _off[v] = f[_gl]
    for v, g in _off.items():
        v.co.x += g * SPREAD
    _b.to_mesh(low_x.data); _b.free()
    # 3. bakes: normal and colour exploded (each game part only from its own high parts), AO assembled (contact
    #    shadows between the parts are wanted)
    imgs = {}
    for kind, suf, nc in (("NORMAL", "nohq", True), ("DIFFUSE", "cor", False), ("AO", "ao", True)):
        img = new_image(f"{base}_{suf}", nc)
        if kind == "AO":
            bake(low, high_ao, kind, img)
        else:
            bake(low_x, high_x, kind, img)
        img.filepath_raw = os.path.join(TEX, f"{base}_{suf}.png"); img.file_format = "PNG"; img.save()
        imgs[suf] = img
    low["hcl_origem"] = (f"build_kiver_rus_jogo.py (blockout_kiver_rus.py LOW=True), dossier HIST-RUS-INF-KIVER-1812-001; "
                         f"bake from the high-poly design model, 2026-10-17")
    low["hcl_materiais"] = ",".join(m.name for m in low.data.materials)
    for o in (low_x, high_x, high_ao):                   # exploded copies and the AO source only served the bake
        bpy.data.objects.remove(o, do_unlink=True)
    results.append((tag, tris_lo, tris_hi, td, uv_use, groups, low, high, imgs))
    print(f"JOGO {tag:18s} LOD0 {tris_lo:5d} triangulos (orcamento {BUDGET}; alta {tris_hi}); "
          f"texel {td:.0f} px/m em {RES}; UV usado {uv_use * 100:.0f} %; materiais {low['hcl_materiais']}; "
          + " ".join(f"{k_}={v}" for k_, v in sorted(groups.items())))

# ---------------------------------------------------------------- previews: high (left) x game mesh (right)
bpy.context.view_layer.update()
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo_ = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo_.data.energy = en
    lo_.rotation_euler = tuple(math.radians(x) for x in rot); scene.collection.objects.link(lo_)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.view_settings.view_transform = "Standard"
scene.cycles.samples = 48
GAP = 0.40
zc = (K.ROOT @ Vector((0, 0, 0.09))).z + 0.10
for i, (tag, tris_lo, tris_hi, td, uv_use, groups, low, high, imgs) in enumerate(results):
    for o in scene.objects:
        if o.type == "MESH":
            o.hide_render = o not in (low, high)
    lowc = low.copy(); lowc.data = low.data.copy(); scene.collection.objects.link(lowc)
    preview_material(lowc, imgs["cor"], imgs["nohq"], imgs["ao"])
    lowc.location.x = GAP
    low.hide_render = True
    for nm_, loc, tgt, ortho, res, off in (
            ("frente", (GAP / 2, -3.0, zc), (GAP / 2, 0, zc), 0.95, (1600, 1000), (GAP, 0, 0)),
            # right profile (wearer's right, like plate 1323): the game copy stands behind along +Y, seen side by side
            ("perfil", (-3.0, GAP / 2, zc), (0.0, GAP / 2, zc), 1.0, (1600, 1000), (0, GAP, 0)),
            ("tres_quartos", (GAP / 2 + 1.3, -2.6, zc + 0.5), (GAP / 2, 0, zc - 0.02), None, (1600, 1000), (GAP, 0, 0))):
        lowc.location = off
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        cam.data.lens = 50
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.filepath = os.path.join(REN, f"jogo_kiver_rus_{tag}_{nm_}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    bpy.data.objects.remove(lowc, do_unlink=True)
    low.hide_render = False
    high.hide_render = True                              # keep the high model in the .blend, hidden in renders
for tag, tris_lo, tris_hi, td, uv_use, groups, low, high, imgs in results:
    high.hide_viewport = True
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
