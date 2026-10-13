# Collar diagnosis against the GAME head: Arma 3 Samples TemplateRTM\bust.p3d (Resolution 1 is the head the game draws,
# textured a3\characters_f\heads\data\m_white_01_co, with the whole neck down to 1.476 m), in the character frame of
# A3_character_example (checked: same bones Neck/Neck1/Head/Spine3). The earlier collar fix (ajustar_gola.py) measured
# the neck on TemplateRTM\Male.p3d, an animation body whose neck is not the game head's.
# Prints, per height, the bust neck section and the gap from the neck skin to the collar's inner wall in 16 directions
# (negative = the neck pokes through the collar), counts neck vertices outside the collar's inner wall, and renders
# close-ups with the uniform textures (front, 3/4, side, back, top, first-person look-down).
#   blender -b --factory-startup --python diag_gola_bust.py -- <project root> <samples dir> <out dir> [uniform=<LOD0 .blend>] [tag=antes] [render=0]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
TAG = OPT.get("tag", "antes")
UNI = os.path.abspath(OPT.get("uniform", os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend")))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
GROUND = -1.0069
LOG = []


def log(s):
    print(s); LOG.append(s)


# ---------------------------------------------------------------- game head (bust.p3d, Resolution 1)
bust = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\bust.p3d"))[0]
BP = [Vector(to_blender(p)) for p in bust["points"]]
BF = [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3]
hm = bpy.data.meshes.new("cabeca_jogo_bust")
hm.from_pydata([tuple(p) for p in BP], [], BF)
for poly, f in zip(hm.polygons, [f for f in bust["faces"] if len(set(f)) >= 3]):
    poly.use_smooth = True
uvl = hm.uv_layers.new(name="UVMap")
k = 0
for fi, f in enumerate(bust["faces"]):
    if len(set(f)) < 3:
        continue
    poly = hm.polygons[k]; k += 1
    uvs = dict(zip(f, bust["faces_uv"][fi]))
    for li in poly.loop_indices:
        u, v = uvs[hm.loops[li].vertex_index]
        uvl.data[li].uv = (u, 1 - v)
hm.validate()
head = bpy.data.objects.new("REF_cabeca_jogo_bust_p3d", hm)
scene.collection.objects.link(head)
Hz = np.array([p.z for p in BP])
log(f"CABECA DO JOGO (bust.p3d Res 1): {len(BP)} pontos, {len(BF)} faces; altura {Hz.min() - GROUND:.3f}..{Hz.max() - GROUND:.3f} m")
hbvh = BVHTree.FromPolygons(BP, BF)

# ---------------------------------------------------------------- uniform collar
with bpy.data.libraries.load(UNI, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "HCL_U_Pruss1813_01_LOD0"]
uni = dst.objects[0]
scene.collection.objects.link(uni)
parts = uni["hcl_partes"].split(",")
bm = bmesh.new(); bm.from_mesh(uni.data)
PL = bm.faces.layers.int.get("hcl_part")
co = [v.co.copy() for v in bm.verts]
gf = [[v.index for v in f.verts] for f in bm.faces if f[PL] == parts.index("gola")]
cf = [[v.index for v in f.verts] for f in bm.faces if f[PL] in (parts.index("gola"), parts.index("casaco_corpo"))]
gbvh = BVHTree.FromPolygons(co, gf)
cbvh = BVHTree.FromPolygons(co, cf)
G = np.array([co[i][:] for f in gf for i in f])
log(f"GOLA: {len(gf)} faces, altura {G[:, 2].min() - GROUND:.3f}..{G[:, 2].max() - GROUND:.3f} m; "
    f"x {G[:, 0].min():+.3f}..{G[:, 0].max():+.3f}, y {G[:, 1].min():+.3f}..{G[:, 1].max():+.3f}")

NDIR = 64
DIRS = [("frente", 0), ("fe", 4), ("fr-esq", 8), ("ef", 12), ("esq", 16), ("et", 20), ("tr-esq", 24), ("te", 28),
        ("tras", 32), ("td", 36), ("tr-dir", 40), ("dt", 44), ("dir", 48), ("df", 52), ("fr-dir", 56), ("fd", 60)]


def dvec(k):
    th = 2 * math.pi * k / NDIR
    return Vector((math.sin(th), -math.cos(th), 0))          # k = 0: front (-Y), k = 16: character's left (+X)


def skin_ring(h, c):
    """Neck skin: from the axis outward, the LAST hit before leaving the head (casts from outside inward)."""
    out = []
    for k in range(NDIR):
        d = dvec(k)
        o = Vector((c.x, c.y, GROUND + h)) + d * 0.25
        hit = hbvh.ray_cast(o, -d, 0.25)
        out.append(None if hit[0] is None else (hit[0] - Vector((c.x, c.y, GROUND + h))).length)
    return out


def wall_ring(bvh, h, c, rmax=0.25):
    out = []
    for k in range(NDIR):
        hit = bvh.ray_cast(Vector((c.x, c.y, GROUND + h)), dvec(k), rmax)
        out.append(None if hit[0] is None else (hit[0] - Vector((c.x, c.y, GROUND + h))).length)
    return out


c = Vector((0.0, 0.03, 0))
sections = []
log("ALTURA  centro x/y   larg x prof (mm) | folga pescoco -> parede interna da gola (mm; negativo = pescoco atravessa)")
log("                                      | " + " ".join(f"{n:>6s}" for n, _ in DIRS))
worst = []
for h in np.round(np.arange(1.48, 1.625, 0.005), 3):
    for _ in range(4):
        r = skin_ring(h, c)
        if sum(x is None for x in r) > 4:
            break
        pts = [c + dvec(k) * r[k] for k in range(NDIR) if r[k] is not None]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        c = Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0))
    r = skin_ring(h, c)
    if sum(x is None for x in r) > 4:
        log(f"  {h:.3f}: sem secao fechada do pescoco")
        continue
    wl = wall_ring(gbvh, h, c)
    sections.append({"h": float(h), "cx": c.x, "cy": c.y, "r": r, "gola": wl})
    cols = []
    for n, k in DIRS:
        if wl[k] is None or r[k] is None:
            cols.append("   ---")
        else:
            g = (wl[k] - r[k]) * 1000
            cols.append(f"{g:6.1f}")
            worst.append((g, h, n))
    log(f"  {h:.3f} {c.x:+.3f} {c.y:+.4f} {(r[16] + r[48]) * 1000:4.0f}x{(r[0] + r[32]) * 1000:4.0f} | " + " ".join(cols))
worst.sort()
log("PIORES folgas (mm, altura, direcao): " + "; ".join(f"{g:.1f} @ {h:.3f} {n}" for g, h, n in worst[:8]))

# neck vertices outside the collar/coat: a ray from the vertex towards the neck axis crosses the collar or coat
ax = {round(s["h"], 3): Vector((s["cx"], s["cy"], 0)) for s in sections}
n_out = []
for i, p in enumerate(BP):
    h = p.z - GROUND
    if not (1.50 <= h <= 1.62):
        continue
    hk = min(ax, key=lambda x: abs(x - h))
    cc = Vector((ax[hk].x, ax[hk].y, p.z))
    d = cc - p
    if d.length < 1e-6:
        continue
    hit = cbvh.ray_cast(p, d.normalized(), d.length)
    if hit[0] is not None:
        n_out.append((i, h, (p - cc).normalized()))
log(f"PESCOCO FORA da gola/casaco (vertices entre 1.50 e 1.62 m): {len(n_out)}")
if n_out:
    hs = [x[1] for x in n_out]
    fr = sum(1 for x in n_out if x[2].y < -0.5); tr = sum(1 for x in n_out if x[2].y > 0.5)
    log(f"   alturas {min(hs):.3f}..{max(hs):.3f} m; frente {fr}, tras {tr}, lados {len(n_out) - fr - tr}")
json.dump({"fonte": "Arma 3 Samples TemplateRTM\\bust.p3d Res 1", "ndir": NDIR, "secoes": sections},
          open(os.path.join(OUT, f"pescoco_bust_{TAG}.json"), "w"), indent=1)

if OPT.get("render", "1") == "0":
    open(os.path.join(OUT, f"gola_bust_{TAG}_output.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
    sys.exit(0)

# ---------------------------------------------------------------- renders (uniform V01 textures; head with its own texture if available)
TEX = os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss")


def tex_mat(name, img_path, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    if img_path and os.path.exists(img_path):
        t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(img_path)
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m


co_png = OPT.get("tex")
for cand in (() if co_png else ("hcl_u_pruss1813_v01_co.png",)):
    pth = os.path.join(TEX, cand)
    if os.path.exists(pth):
        co_png = pth; break
if co_png is None:
    for dp, dn, fn in os.walk(TEX):
        for f_ in fn:
            if f_.lower().endswith("_co.png") and "_v1" not in dp and "_antes" not in dp:
                co_png = os.path.join(dp, f_); break
        if co_png:
            break
log(f"TEXTURA do uniforme: {co_png}")
mu = tex_mat("uni", co_png)
uni.data.materials.clear(); uni.data.materials.append(mu)
for p_ in uni.data.polygons:
    p_.material_index = 0
skin = bpy.data.materials.new("pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.80, 0.58, 0.47, 1)
skin.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
head.data.materials.append(skin)

for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(x) for x in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.75, 0.75, 1); scene.world = w
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 24
scene.view_settings.view_transform = "Standard"
zc = GROUND + 1.56
T = Vector((0, 0.03, zc))


def shot(name, loc, target=T, lens=85, res=(900, 900)):
    cam.data.type = "PERSP"; cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT, f"gola_bust_{TAG}_{name}.png")
    bpy.ops.render.render(write_still=True)
    log("render " + scene.render.filepath)


shot("frente", T + Vector((0, -0.9, 0.05)))
shot("tres_quartos", T + Vector((0.62, -0.62, 0.10)))
shot("lado", T + Vector((0.9, 0.0, 0.02)))
shot("tras", T + Vector((0.0, 0.9, 0.08)))
shot("cima", T + Vector((0.25, -0.35, 0.75)))
head.hide_render = True
shot("sem_cabeca_cima", T + Vector((0.25, -0.35, 0.75)))
open(os.path.join(OUT, f"gola_bust_{TAG}_output.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
