# Diagnosis of the collar against the OFFICIAL head (Arma 3 Samples TemplateRTM\Male.p3d, the head the game places on
# the character): per height, the neck section (centre, half-width, half-depth) versus the collar's inner wall, the gap
# in front / back / at the sides, and close-up renders (front, side, 3/4, back, top) with the uniform textures.
#   blender -b --factory-startup --python diag_gola.py -- <project root> <samples dir> <out dir> [uniform=<LOD0 .blend>] [tag=antes]
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender
from uniform_fit import weight_of_byte

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = a[:3]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
TAG = OPT.get("tag", "antes")
UNI = OPT.get("uniform", os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
GROUND = -1.0069
LOG = []


def log(s):
    print(s); LOG.append(s)


# ---------------------------------------------------------------- official head (skin of head and neck)
male = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\Male.p3d"))[0]
mp = np.array([to_blender(p) for p in male["points"]], np.float64)
mW = {}
for name, blob in male["selections"].items():
    n = name.lower()
    for i, b in enumerate(blob[:len(mp)]):
        if b and (n in ("head", "neck", "neck1", "spine3") or n.startswith(("face_", "eye"))):
            mW.setdefault(i, {})[n] = weight_of_byte(b)
# neck and head skin: faces with every point above the upper chest (z > 1.43 m) and within the neck/head width
ZMIN = float(OPT.get("zmin", 1.43))
hface = [f for f in male["faces"] if len(set(f)) >= 3 and all(mp[i, 2] > GROUND + ZMIN and abs(mp[i, 0]) < 0.115 for i in f)]
log(f"CABECA: faces acima de {ZMIN} m: {len(hface)}; vertices do pescoco (1.50-1.62 m, |x|<0.09): "
    f"{int(((mp[:, 2] > GROUND + 1.50) & (mp[:, 2] < GROUND + 1.62) & (np.abs(mp[:, 0]) < 0.09)).sum())}")
par = {}


def _f(x):
    par.setdefault(x, x)
    while par[x] != x:
        par[x] = par[par[x]]; x = par[x]
    return x


for f in hface:
    for b_ in f[1:]:
        ra, rb = _f(f[0]), _f(b_)
        if ra != rb:
            par[ra] = rb
comp = {}
for k, f in enumerate(hface):
    comp.setdefault(_f(f[0]), []).append(k)
# (no component-size filter: the P3D splits points along UV/normal seams, so the neck comes in many small pieces)
hm = bpy.data.meshes.new("cabeca_oficial")
hm.from_pydata([tuple(p) for p in mp], [], [list(dict.fromkeys(f)) for f in hface])
hm.validate()
hb_ = bmesh.new(); hb_.from_mesh(hm)
bmesh.ops.remove_doubles(hb_, verts=hb_.verts, dist=1e-5)
bmesh.ops.delete(hb_, geom=[v for v in hb_.verts if not v.link_faces], context="VERTS")
hb_.to_mesh(hm); hb_.free()
head = bpy.data.objects.new("REF_cabeca_oficial_Male_p3d", hm)
bpy.context.scene.collection.objects.link(head)
hbvh = BVHTree.FromObject(head, bpy.context.evaluated_depsgraph_get())
log(f"CABECA oficial: {len(hm.polygons)} faces; altura {mp[:, 2].min() - GROUND:.3f}..{mp[:, 2].max() - GROUND:.3f} m")

# ---------------------------------------------------------------- uniform collar
with bpy.data.libraries.load(UNI, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "HCL_U_Pruss1813_01_LOD0"]
uni = dst.objects[0]
bpy.context.scene.collection.objects.link(uni)
parts = uni["hcl_partes"].split(",")
pa = uni.data.attributes["hcl_part"].data
GOLA = parts.index("gola")
gpolys = [p for p in uni.data.polygons if pa[p.index].value == GOLA]
gverts = sorted({i for p in gpolys for i in p.vertices})
G = np.array([uni.data.vertices[i].co[:] for i in gverts])
log(f"GOLA: {len(gpolys)} faces, altura {G[:, 2].min() - GROUND:.3f}..{G[:, 2].max() - GROUND:.3f} m")


def section(points_bvh, h, centre_guess, n=48, r_max=0.15):
    """Ring of the surface at height h: for each direction from the vertical axis through centre_guess, the NEAREST
    hit from the axis outward (inner wall of a tube / skin of the neck)."""
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        d = Vector((math.sin(th), -math.cos(th), 0))          # th = 0: front (-Y)
        o = Vector((centre_guess.x, centre_guess.y, GROUND + h))
        hit = points_bvh.ray_cast(o, d, r_max)
        out.append(hit[0])
    return out


gb = bmesh.new(); gb.from_mesh(uni.data)
gb.faces.ensure_lookup_table()
glayer = gb.faces.layers.int.get("hcl_part")
gfaces = [[v.index for v in f.verts] for f in gb.faces if f[glayer] == GOLA]
gco = [v.co.copy() for v in gb.verts]
gbvh = BVHTree.FromPolygons(gco, gfaces)
c0 = Vector((G[:, 0].mean(), G[:, 1].mean(), 0))
log("ALTURA  pescoco: centro y, meia-largura, meia-prof | folga ate a parede interna da gola: frente, tras, lados (mm)")
for h in np.arange(1.535, 1.606, 0.005):
    nk = section(hbvh, h, c0)
    # neck surface seen from the axis: we need the skin (first hit from INSIDE the neck); cast from far outside inward
    skin = []
    for k in range(48):
        th = 2 * math.pi * k / 48
        d = Vector((math.sin(th), -math.cos(th), 0))
        o = Vector((c0.x, c0.y, GROUND + h)) + d * 0.2
        hit = hbvh.ray_cast(o, -d, 0.2)
        skin.append(hit[0])
    wall = section(gbvh, h, c0)
    if any(p is None for p in skin):
        log(f"  h {h:.3f}: pescoco nao fechado nesta altura")
        continue
    S_ = np.array([p[:] for p in skin])
    cy = S_[:, 1].mean()
    hw = (S_[:, 0].max() - S_[:, 0].min()) / 2
    hd = (S_[:, 1].max() - S_[:, 1].min()) / 2
    gaps = []
    for k in (0, 24, 12, 36):                                 # front, back, left, right
        if wall[k] is None:
            gaps.append(float("nan")); continue
        d = Vector((math.sin(2 * math.pi * k / 48), -math.cos(2 * math.pi * k / 48), 0))
        gaps.append(((wall[k] - Vector((c0.x, c0.y, wall[k].z))).dot(d) - (skin[k] - Vector((c0.x, c0.y, skin[k].z))).dot(d)) * 1000)
    log(f"  h {h:.3f}: y {cy:+.3f} larg {hw * 1000:5.1f} prof {hd * 1000:5.1f} | frente {gaps[0]:6.1f} tras {gaps[1]:6.1f} "
        f"esq {gaps[2]:6.1f} dir {gaps[3]:6.1f}")
# intersections head x collar at rest
pairs = hbvh.overlap(gbvh)
log(f"CRUZA cabeca oficial x gola no repouso: {len(pairs)} pares de faces")

# ---------------------------------------------------------------- renders
TXU = os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss")


def tex_material(name, co, nohq, smdi):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    ic = nt.nodes.new("ShaderNodeTexImage"); ic.image = bpy.data.images.load(co)
    inn = nt.nodes.new("ShaderNodeTexImage"); inn.image = bpy.data.images.load(nohq); inn.image.colorspace_settings.name = "Non-Color"
    isd = nt.nodes.new("ShaderNodeTexImage"); isd.image = bpy.data.images.load(smdi); isd.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); sep = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(ic.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(inn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(isd.outputs["Color"], sep.inputs["Color"]); nt.links.new(sep.outputs["Blue"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], bsdf.inputs["Roughness"]); nt.links.new(sep.outputs["Green"], bsdf.inputs["Specular IOR Level"])
    return m


skin_m = bpy.data.materials.new("pele"); skin_m.use_nodes = True
skin_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.45, 0.36, 1)
mu = tex_material("U", os.path.join(TXU, "hcl_u_pruss1813_v01_co.png"), os.path.join(TXU, "hcl_u_pruss1813_nohq.png"),
                  os.path.join(TXU, "hcl_u_pruss1813_smdi.png"))
for i, slot in enumerate(uni.material_slots):
    slot.link = "OBJECT"
    slot.material = skin_m if uni.data.materials[i].name.startswith("HCL_pele") else mu
for p in uni.data.polygons:
    p.use_smooth = True
uni.data.set_sharp_from_angle(angle=math.radians(35))
head.data.materials.append(skin_m)
head.hide_render = "semcabeca" in a                 # the template head carries helper parts: hide to see the collar
for p in head.data.polygons:
    p.use_smooth = True
scene = bpy.context.scene
for nm_, en, rot in (("sol", 3.2, (50, 0, 25)), ("preench", 1.3, (65, 0, 200)), ("contra", 1.0, (60, 0, 130))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(x) for x in rot); scene.collection.objects.link(lo)
world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.9, 0.9, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
scene.world = world
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = int(OPT.get("samples", 32))
scene.view_settings.view_transform = "Standard"
T = Vector((0, 0.0, GROUND + 1.57))


def cam(name, loc, target, lens=70):
    c = bpy.data.cameras.new(name); c.lens = lens
    o = bpy.data.objects.new(name, c); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(o); return o


shots = [("frente", cam("f", (0, -0.9, GROUND + 1.62), T), (900, 900)),
         ("lado", cam("l", (0.9, 0.0, GROUND + 1.60), T), (900, 900)),
         ("tres_quartos", cam("q", (0.6, -0.7, GROUND + 1.68), T), (900, 900)),
         ("costas", cam("c", (0, 0.9, GROUND + 1.64), T), (900, 900)),
         ("cima", cam("t", (0.25, -0.35, GROUND + 1.95), T, lens=60), (900, 900))]
if "norender" not in a:
    for name, c, (rx, ry) in shots:
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT, f"gola_{TAG}_{name}.png")
        bpy.ops.render.render(write_still=True)
open(os.path.join(OUT, f"gola_{TAG}_output.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
