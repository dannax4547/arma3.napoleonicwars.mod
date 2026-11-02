# Phase 6 of the Russian kivers: material textures over the Phase 4 bake (build_kiver_rus_jogo.py).
# Materials and their sources: docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md section 7 (M1-M9): the MATERIAL of every
# part is sourced (black cloth, lacquered leather, brass, white wool cords, wool pompom, black horsehair); the numeric
# TONES are estimates (no colorimetric source), to be checked on the mod atlas. Report: docs/reports/kiver_rus_texturas.md.
#   blender -b --factory-startup --python texturizar_kiver_rus.py -- <jogo .blend> <texture dir> <render dir> [res=2048]
#           [so=<tag>,...]
# Like the French / Prussian shakos (texturizar_shako_fr.py): procedural 3D materials (no UV seams) on the high-poly model,
# baked onto the game mesh. Exploded by part ("grupo" face attribute written by build_kiver_rus_jogo.py), so a part only
# receives its own materials. Maps (2048 PNG, sources for ImageToPAA; conventions of docs/modeling_standards.md section 5):
#   <base>_co.png    albedo x ambient occlusion (the _ao of Phase 4, 70 %)
#   <base>_smdi.png  R = 1, G = specular, B = gloss (the convention of the other shakos of the project)
#   (<base>_nohq.png and <base>_ao.png come from Phase 4, <base>_cor.png stays as the identification palette)
# Wear is limited to what use explains (dossier section 7): brass darkened in the recesses and polished on the edges,
# light soiling in the recesses of the white wool, tonal variation of the cloth.
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
SRC, TEX, REN = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
RES = int(OPT.get("res", 2048))
SO = set(OPT["so"].split(",")) if "so" in OPT else None
SPREAD, EXTR, RAY, MARGIN = 0.8, 0.006, 0.020, 16
AO_MIX = 0.70
os.makedirs(TEX, exist_ok=True); os.makedirs(REN, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"

# kind: base colour (linear), (spec, gloss) for _smdi, pattern kind (dossier section 7, M1-M9)
MAT = {
    "pano":         dict(col=(0.013, 0.012, 0.012), smdi=(0.04, 0.10), kind="la"),
    "feltro":       dict(col=(0.015, 0.015, 0.016), smdi=(0.05, 0.12), kind="la"),
    "verniz":       dict(col=(0.006, 0.006, 0.007), smdi=(0.60, 0.85), kind="verniz"),
    "couro":        dict(col=(0.020, 0.018, 0.016), smdi=(0.30, 0.45), kind="couro"),
    "couro_marrom": dict(col=(0.070, 0.035, 0.016), smdi=(0.25, 0.40), kind="couro"),
    "forro":        dict(col=(0.350, 0.310, 0.240), smdi=(0.03, 0.10), kind="linho"),
    "latao":        dict(col=(0.660, 0.470, 0.170), smdi=(0.85, 0.72), kind="latao"),
    "branco":       dict(col=(0.740, 0.730, 0.680), smdi=(0.06, 0.15), kind="la_branca"),
    "vermelho":     dict(col=(0.500, 0.030, 0.030), smdi=(0.05, 0.12), kind="la"),
    "verde":        dict(col=(0.030, 0.170, 0.060), smdi=(0.05, 0.12), kind="la"),
    "crina":        dict(col=(0.015, 0.015, 0.016), smdi=(0.35, 0.55), kind="crina"),
    "ferro":        dict(col=(0.090, 0.088, 0.085), smdi=(0.55, 0.45), kind="ferro"),   # M10, pompom stem (wire)
    "celeste":      dict(col=(0.130, 0.360, 0.780), smdi=(0.05, 0.12), kind="la"),      # M6, 3rd battalion (sky blue)
}
# battalion pompoms (RU7; spec rus_1812.md section 2.4 and dossier D18, order of 22 Feb 1811). The 1st battalion is the
# model as built (<base>_co); the 2nd and 3rd re-bake ONLY the pompom (its high parts: ring, centre, wire prongs) with
# their colours into a copy of the albedo, so one P3D serves the 3 battalions through hiddenSelectionsTextures.
#   original kind -> new kind, or (top, bottom): "red, green (sky blue) below" = lower third of the oval, D18
BAT = {"mosqueteiro": {"b2": {"branco": "verde", "verde": "branco"}, "b3": {"branco": "celeste", "verde": "branco"}},
       "granadeiro": {"b2": {"vermelho": ("vermelho", "verde")}, "b3": {"vermelho": ("vermelho", "celeste")}}}
BAT_MARGIN = 8                                   # px: half of the 16 px between islands, so no neighbour is painted


def kind_of(mat_name):
    n = mat_name.split(".")[0]
    for pre in ("BO_", "TX_cor_", "TX_smdi_"):          # blockout material, or one already swapped by a previous bake
        if n.startswith(pre):
            n = n[len(pre):]
    return n if n in MAT else None


def node(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def build(kname, mode):
    """Procedural material for kind kname; mode 'cor' -> Principled with the albedo; 'smdi' -> Emission (1, spec, gloss)."""
    spec = MAT[kname]
    m = bpy.data.materials.new(f"TX_{mode}_{kname}"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial")
    tc = node(nt, "ShaderNodeTexCoord")
    base = Vector(spec["col"])
    k = spec["kind"]
    if k in ("la", "la_branca", "linho"):        # wool / linen: fine fibres x coarse mottling
        fine = node(nt, "ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 1400.0; fine.inputs["Detail"].default_value = 6.0
        coarse = node(nt, "ShaderNodeTexNoise"); coarse.inputs["Scale"].default_value = 45.0
        nt.links.new(tc.outputs["Object"], fine.inputs["Vector"]); nt.links.new(tc.outputs["Object"], coarse.inputs["Vector"])
        mix = node(nt, "ShaderNodeMath", operation="MULTIPLY")
        nt.links.new(fine.outputs["Fac"], mix.inputs[0]); nt.links.new(coarse.outputs["Fac"], mix.inputs[1])
        drv = mix.outputs[0]; amp = 0.22 if k == "la" else 0.10
    elif k == "couro":                            # leather grain
        vor = node(nt, "ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 900.0
        nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
        drv = vor.outputs["Distance"]; amp = 0.18
    elif k == "verniz":                           # lacquer: almost uniform
        n_ = node(nt, "ShaderNodeTexNoise"); n_.inputs["Scale"].default_value = 30.0
        nt.links.new(tc.outputs["Object"], n_.inputs["Vector"])
        drv = n_.outputs["Fac"]; amp = 0.10
    elif k == "crina":                            # horsehair: streaks along the plume (object Z)
        mp = node(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 0.04)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        n_ = node(nt, "ShaderNodeTexNoise"); n_.inputs["Scale"].default_value = 600.0
        nt.links.new(mp.outputs["Vector"], n_.inputs["Vector"])
        drv = n_.outputs["Fac"]; amp = 0.35
    else:                                         # brass / iron
        n_ = node(nt, "ShaderNodeTexNoise"); n_.inputs["Scale"].default_value = 300.0
        nt.links.new(tc.outputs["Object"], n_.inputs["Vector"])
        drv = n_.outputs["Fac"]; amp = 0.06
    # tone variation: base * (1 + 2 amp (drv - 0.5))
    sub = node(nt, "ShaderNodeMath", operation="SUBTRACT"); sub.inputs[1].default_value = 0.5
    nt.links.new(drv, sub.inputs[0])
    sc = node(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); sc.inputs[1].default_value = 2 * amp; sc.inputs[2].default_value = 1.0
    nt.links.new(sub.outputs[0], sc.inputs[0])
    col = node(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    col.inputs["Factor"].default_value = 1.0
    col.inputs[6].default_value = (*base, 1.0)
    cv = node(nt, "ShaderNodeCombineColor")
    for i in range(3):
        nt.links.new(sc.outputs[0], cv.inputs[i])
    nt.links.new(cv.outputs[0], col.inputs[7])
    colour_out = col.outputs[2]
    wear = None
    # recesses (local AO, 6 mm): brass tarnish / soiling of the white wool; brass edges polished (pointiness)
    if k in ("latao", "la_branca"):
        ao = node(nt, "ShaderNodeAmbientOcclusion", only_local=True); ao.inputs["Distance"].default_value = 0.006
        ramp = node(nt, "ShaderNodeMapRange"); ramp.inputs["From Min"].default_value = 0.35; ramp.inputs["From Max"].default_value = 0.95
        nt.links.new(ao.outputs["AO"], ramp.inputs["Value"])
        dirty = node(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MIX")
        tar = (0.30, 0.20, 0.07) if k == "latao" else (0.52, 0.50, 0.44)
        dirty.inputs[7].default_value = (*tar, 1.0)
        inv = node(nt, "ShaderNodeMath", operation="SUBTRACT"); inv.inputs[0].default_value = 1.0
        nt.links.new(ramp.outputs[0], inv.inputs[1])
        nt.links.new(inv.outputs[0], dirty.inputs["Factor"])
        nt.links.new(colour_out, dirty.inputs[6])
        colour_out = dirty.outputs[2]
        wear = ramp                                   # 1 = clean, 0 = recess (tarnish is dull)
        if k == "latao":
            geo = node(nt, "ShaderNodeNewGeometry")
            pr = node(nt, "ShaderNodeMapRange"); pr.inputs["From Min"].default_value = 0.52; pr.inputs["From Max"].default_value = 0.60
            nt.links.new(geo.outputs["Pointiness"], pr.inputs["Value"])
            pol = node(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MIX")
            pol.inputs[7].default_value = (0.86, 0.68, 0.32, 1.0)
            fm = node(nt, "ShaderNodeMath", operation="MULTIPLY"); fm.inputs[1].default_value = 0.6
            nt.links.new(pr.outputs[0], fm.inputs[0])
            nt.links.new(fm.outputs[0], pol.inputs["Factor"]); nt.links.new(colour_out, pol.inputs[6])
            colour_out = pol.outputs[2]
    if mode == "cor":
        b = node(nt, "ShaderNodeBsdfPrincipled")
        b.inputs["Metallic"].default_value = 0.0      # the colour bake needs a dielectric
        nt.links.new(colour_out, b.inputs["Base Color"])
        nt.links.new(b.outputs[0], out.inputs["Surface"])
    else:
        s_, g_ = spec["smdi"]
        cmb = node(nt, "ShaderNodeCombineColor")
        cmb.inputs[0].default_value = 1.0
        if wear is not None:
            gm = node(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); gm.inputs[1].default_value = g_ * 0.6; gm.inputs[2].default_value = g_ * 0.4
            sm = node(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); sm.inputs[1].default_value = s_ * 0.6; sm.inputs[2].default_value = s_ * 0.4
            nt.links.new(wear.outputs[0], gm.inputs[0]); nt.links.new(wear.outputs[0], sm.inputs[0])
            nt.links.new(sm.outputs[0], cmb.inputs[1]); nt.links.new(gm.outputs[0], cmb.inputs[2])
        else:
            cmb.inputs[1].default_value = s_
            gm = node(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); gm.inputs[1].default_value = 0.15 * g_; gm.inputs[2].default_value = g_ * 0.925
            nt.links.new(sc.outputs[0], gm.inputs[0])
            nt.links.new(gm.outputs[0], cmb.inputs[2])
        em = node(nt, "ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
        nt.links.new(cmb.outputs[0], em.inputs["Color"])
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def exploded_copy(ob, name):
    c = ob.copy(); c.data = ob.data.copy(); c.name = name
    scene.collection.objects.link(c)
    c.hide_render = False; c.hide_viewport = False
    bm = bmesh.new(); bm.from_mesh(c.data)
    gl = bm.faces.layers.int.get("grupo")
    off = {}
    for f in bm.faces:
        for v in f.verts:
            off[v] = f[gl]
    for v, g in off.items():
        v.co.x += g * SPREAD
    bm.to_mesh(c.data); bm.free()
    return c


def select_only(objs, active):
    for o in scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def bake(low, high, mode, img):
    for i, m in enumerate(list(high.data.materials)):
        kn = kind_of(m.name) if m else None
        if kn is None:
            raise SystemExit(f"material sem tipo: {m.name if m else None}")
        high.data.materials[i] = MATS[mode][kn]
    tgt = bpy.data.materials.new("BAKE_TARGET"); tgt.use_nodes = True
    nd = tgt.node_tree.nodes.new("ShaderNodeTexImage"); nd.image = img; tgt.node_tree.nodes.active = nd
    for i in range(len(low.data.materials)):
        low.data.materials[i] = tgt
    select_only([high, low], low)
    sb = scene.render.bake
    sb.use_selected_to_active = True; sb.cage_extrusion = EXTR; sb.max_ray_distance = RAY; sb.margin = MARGIN
    scene.cycles.samples = 4
    if mode == "cor":
        sb.use_pass_direct = False; sb.use_pass_indirect = False; sb.use_pass_color = True
        bpy.ops.object.bake(type="DIFFUSE")
    else:
        bpy.ops.object.bake(type="EMIT")
    bpy.data.materials.remove(tgt)


def part_copy(ob, name, g):
    """Copy of an exploded object keeping only the faces of bake group g."""
    c = ob.copy(); c.data = ob.data.copy(); c.name = name
    scene.collection.objects.link(c)
    bm = bmesh.new(); bm.from_mesh(c.data)
    gl = bm.faces.layers.int.get("grupo")
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[gl] != g], context="FACES")
    bm.to_mesh(c.data); bm.free()
    return c


def pompom_variant(lx, hx, vmap, alb, name):
    """Albedo of another battalion: alb (RES x RES x 4) with the pompom re-baked under the colours of vmap."""
    kinds = [kind_of(m.name) for m in hx.data.materials]
    gl = hx.data.attributes["grupo"].data
    g = {gl[p.index].value for p in hx.data.polygons if kinds[p.material_index] in ("vermelho", "verde")}
    if len(g) != 1:
        raise SystemExit(f"grupo do pompom ambiguo: {g}")
    g = g.pop()
    lp = part_copy(lx, "TX_POMPOM_JOGO", g); hp = part_copy(hx, "TX_POMPOM_ALTA", g)
    me = hp.data
    split = [p for p in me.polygons if isinstance(vmap.get(kinds[p.material_index]), tuple)]
    if split:
        zs = [p.center.z for p in split]
        z_cut = min(zs) + (max(zs) - min(zs)) / 3
    new = []
    for p in me.polygons:
        k = kinds[p.material_index]
        v = vmap.get(k, k)
        if isinstance(v, tuple):
            v = v[0] if p.center.z >= z_cut else v[1]
        new.append(v)
    me.materials.clear()
    order = sorted(set(new))
    for kn in order:
        me.materials.append(MATS["cor"][kn])
    for p, kn in zip(me.polygons, new):
        p.material_index = order.index(kn)
    img = bpy.data.images.new(name, RES, RES, alpha=False)
    img.pixels[:] = alb.ravel()
    tgt = bpy.data.materials.new("BAKE_TARGET"); tgt.use_nodes = True
    nd = tgt.node_tree.nodes.new("ShaderNodeTexImage"); nd.image = img; tgt.node_tree.nodes.active = nd
    for i in range(len(lp.data.materials)):
        lp.data.materials[i] = tgt
    select_only([hp, lp], lp)
    sb = scene.render.bake
    sb.use_selected_to_active = True; sb.cage_extrusion = EXTR; sb.max_ray_distance = RAY; sb.margin = BAT_MARGIN
    sb.use_clear = False
    sb.use_pass_direct = False; sb.use_pass_indirect = False; sb.use_pass_color = True
    scene.cycles.samples = 4
    bpy.ops.object.bake(type="DIFFUSE")
    sb.use_clear = True
    bpy.data.materials.remove(tgt)
    bpy.data.objects.remove(lp, do_unlink=True); bpy.data.objects.remove(hp, do_unlink=True)
    out = np.array(img.pixels[:]).reshape(RES, RES, 4)
    changed = np.abs(out[..., :3] - alb[..., :3]).max(axis=2) > 2e-3
    ys, xs = np.nonzero(changed)
    print(f"POMPOM {name}: grupo {g}, {changed.sum()} texels mudaram, caixa x {xs.min()}..{xs.max()} y {ys.min()}..{ys.max()}"
          + (f", divisao z {z_cut:.4f}" if split else ""))
    return out


def compose_co(alb, ao, path):
    co = alb.copy()
    co[..., :3] = alb[..., :3] * (1.0 - AO_MIX + AO_MIX * ao)
    out = bpy.data.images.new(os.path.basename(path), RES, RES, alpha=False)
    out.pixels[:] = co.ravel()
    out.filepath_raw = path; out.file_format = "PNG"; out.save()


MATS = {mode: {kn: build(kn, mode) for kn in MAT} for mode in ("cor", "smdi")}
lods = [o for o in bpy.data.objects if o.name.startswith("HCL_H_RUS") and o.name.endswith("_LOD0")]
done = []
for low in sorted(lods, key=lambda o: o.name):
    model = low.name[len("HCL_H_RUS"):len("HCL_H_RUS") + 4]
    var = low.name[len("HCL_H_RUS") + 5:-len("_LOD0")].lower()
    tag = f"{model}_{var}"
    if SO and tag not in SO:
        continue
    high = bpy.data.objects[f"ALTA_{tag}"]
    base = f"hcl_kiver_rus{model}_{var}"
    lx = exploded_copy(low, "TX_JOGO_" + tag)
    hx = exploded_copy(high, "TX_ALTA_" + tag)
    imgs = {}
    for mode, nc in (("cor", False), ("smdi", True)):
        img = bpy.data.images.new(f"{base}_{mode}_tx", RES, RES, alpha=False)
        if nc:
            img.colorspace_settings.name = "Non-Color"
        bake(lx, hx, mode, img)
        imgs[mode] = img
    # _co = albedo x AO (Phase 4 map), multiplied on the stored values (report kiver_rus_texturas.md section 5)
    alb = np.array(imgs["cor"].pixels[:]).reshape(RES, RES, 4)
    ao_img = bpy.data.images.load(os.path.join(TEX, f"{base}_ao.png"), check_existing=True)
    ao_img.colorspace_settings.name = "Non-Color"
    ao = np.array(ao_img.pixels[:]).reshape(ao_img.size[1], ao_img.size[0], 4)[..., :1]
    compose_co(alb, ao, os.path.join(TEX, f"{base}_co.png"))
    sm = imgs["smdi"]
    sm.filepath_raw = os.path.join(TEX, f"{base}_smdi.png"); sm.file_format = "PNG"; sm.save()
    done.append((tag, low, base, f"{base}_co.png", True))
    print(f"TEXTURAS {tag:18s} {base}_co.png e {base}_smdi.png ({RES})")
    for b_, vmap in BAT[var].items():
        compose_co(pompom_variant(lx, hx, vmap, alb, f"{base}_{b_}_alb"), ao, os.path.join(TEX, f"{base}_{b_}_co.png"))
        done.append((f"{tag}_{b_}", low, base, f"{base}_{b_}_co.png", False))
        print(f"TEXTURAS {tag}_{b_:4s} {base}_{b_}_co.png")
    bpy.data.objects.remove(lx, do_unlink=True); bpy.data.objects.remove(hx, do_unlink=True)

# ---------------------------------------------------------------- previews: game mesh with _co, _nohq and _smdi
for o in scene.objects:
    if o.type == "MESH":
        o.hide_render = True
cam = bpy.data.objects.get("cam") or bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
if cam.name not in scene.collection.objects:
    scene.collection.objects.link(cam)
scene.camera = cam
scene.cycles.samples = 64
for tag, low, base, co_file, full in done:
    c = low.copy(); c.data = low.data.copy(); scene.collection.objects.link(c); c.hide_render = False
    m = bpy.data.materials.new("PREVIEW_TX_" + tag); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t_co = nt.nodes.new("ShaderNodeTexImage"); t_co.image = bpy.data.images.load(os.path.join(TEX, co_file), check_existing=True)
    nt.links.new(t_co.outputs["Color"], b.inputs["Base Color"])
    t_n = nt.nodes.new("ShaderNodeTexImage"); t_n.image = bpy.data.images.load(os.path.join(TEX, f"{base}_nohq.png"), check_existing=True)
    t_n.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(t_n.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    t_s = nt.nodes.new("ShaderNodeTexImage"); t_s.image = bpy.data.images.load(os.path.join(TEX, f"{base}_smdi.png"), check_existing=True)
    t_s.image.colorspace_settings.name = "Non-Color"
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(t_s.outputs["Color"], sep.inputs["Color"])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs[2], inv.inputs[1]); nt.links.new(inv.outputs[0], b.inputs["Roughness"])     # gloss -> roughness
    nt.links.new(sep.outputs[1], b.inputs["Specular IOR Level"])
    # preview only: high specular (brass, G >= 0.8) shown as metal; in the game this is the job of the .rvmat (Phase 7)
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.65; mr.inputs["From Max"].default_value = 0.80
    nt.links.new(sep.outputs[1], mr.inputs["Value"]); nt.links.new(mr.outputs[0], b.inputs["Metallic"])
    c.data.materials.clear(); c.data.materials.append(m)
    bb = [c.matrix_world @ Vector(v) for v in c.bound_box]
    ctr = sum(bb, Vector()) / 8
    # 85 mm lens, the 1300 px height on the 36 mm sensor: vertical field 23.9 deg; the kiver fills ~80 % of the height
    dims = Vector([max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3)])
    dist = max(dims.z, dims.x * 1300 / 1100) * 2.95
    views = (("frente", Vector((0, -1, 0))), ("perfil", Vector((-1, 0, 0))), ("tres_quartos", Vector((0.46, -0.78, 0.28))))
    for nm_, d_ in (views if full else views[:1]):                 # battalion variants: front view only
        off = d_.normalized() * dist
        cam.data.type = "PERSP"; cam.data.lens = 85
        cam.location = ctr + off
        cam.rotation_euler = (-off).to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x, scene.render.resolution_y = 1100, 1300
        scene.render.filepath = os.path.join(REN, f"textura_kiver_rus_{tag}_{nm_}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    bpy.data.objects.remove(c, do_unlink=True)
print("FIM")
