# Phase 3 report renders of the Russian 1812 soldier (blockout): the coat from build_uniforme_rus.py in FLAT
# identification colours per part (no textures yet) and the kivers of blockout_kiver_rus.py on the approximate head of
# that blockout (the game head, TemplateRTM\bust.p3d, needs the Arma 3 Samples). Colours: spec docs/specs/rus_1812.md
# 2.1-2.2 (dark green coat, red collar and cuffs, dark green cuff flaps, red shoulder straps = 1st regiment of a
# division, white trousers, black gaiters to the knee). The red turnbacks of the tails are left for the painter.
#   blender -b --factory-startup --python render_blockout_rus.py -- <project root> <out dir> [samples=48]
import bpy, bmesh, sys, os, math
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
G = -1.0069
J = lambda *p: os.path.join(ROOT, *p)
COAT = J("source", "models", "coats", "hcl_uniforme_rus", "hcl_uniforme_rus_linha_LOD0.blend")
PRUSS = J("source", "models", "coats", "hcl_uniforme_pruss", "hcl_uniforme_pruss_LOD0.blend")
KIVER = J("source", "models", "shakos", "hcl_kiver_rus", "hcl_kiver_rus_blockout.blend")
SOLDIERS = [(0, "1812_mosqueteiro"), (1, "1812_granadeiro"), (2, "1808_mosqueteiro")]   # kiver index in the blockout
SPACING = 0.45                                                                       # = blockout_kiver_rus.py


def flat(name, rgb, rough=0.75, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M = dict(verde=flat("verde_escuro", (0.025, 0.075, 0.040)), vermelho=flat("vermelho", (0.50, 0.035, 0.035)),
         branco=flat("branco", (0.78, 0.78, 0.75)), preto=flat("preto", (0.02, 0.02, 0.02), 0.5),
         latao=flat("latao", (0.70, 0.50, 0.16), 0.35, 1.0), pele=flat("pele", (0.80, 0.60, 0.50)))
PART_COL = dict(casaco_corpo="verde", gola="vermelho", manga_E="verde", manga_D="verde", punho_E="vermelho",
                punho_D="vermelho", pala_E="verde", pala_D="verde", aba_E="verde", aba_D="verde",
                platina_E="vermelho", platina_D="vermelho", calca_assento="branco", calca_perna_E="branco",
                calca_perna_D="branco", polaina_E="preto", polaina_D="preto", sapato_E="preto", sapato_D="preto",
                botoes="latao", maos_template="pele")
ORDER = list(M)


def load(blend, names=None):
    with bpy.data.libraries.load(blend, link=False) as (s, d):
        d.objects = [n for n in s.objects if names is None or n in names]
    for o in d.objects:
        sc.collection.objects.link(o)
    return list(d.objects)


def paint_flat(ob):
    """Flat material per part; the trouser legs below the gaiter top are black (knee-high gaiters, 1812)."""
    parts = ob["hcl_partes"].split(",")
    top = float(ob.get("hcl_polaina_topo", 0.0))
    me = ob.data
    me.materials.clear()
    for k in ORDER:
        me.materials.append(M[k])
    bm = bmesh.new(); bm.from_mesh(me)
    PL = bm.faces.layers.int.get("hcl_part")
    for f in bm.faces:
        pn = parts[f[PL]]
        col = PART_COL[pn]
        if pn.startswith("calca_perna") and f.calc_center_median().z - G < top:
            col = "preto"
        f.material_index = ORDER.index(col)
    bm.to_mesh(me); bm.free()


coat = load(COAT)[0]
paint_flat(coat)
coats = [coat]
for i, _ in SOLDIERS[1:]:
    c = coat.copy(); c.data = coat.data; c.location.x = i * SPACING
    sc.collection.objects.link(c); coats.append(c)
coat.location.x = SOLDIERS[0][0] * SPACING
kv = load(KIVER)
keep = {f"RUS_{t}" for _, t in SOLDIERS} | {f"REF_cabeca_APROX_{i}" for i, _ in SOLDIERS}
for o in kv:
    top_ = o
    while top_.parent:
        top_ = top_.parent
    if top_.name not in keep:
        o.hide_render = True
# Prussian coat for the comparison (tails, collar), flat too, beside the row
pr = load(PRUSS, ["HCL_U_Pruss1813_01_LOD0"])[0]
pr.location.x = -SPACING * 1.4
paint_flat(pr)
bpy.context.view_layer.update()

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
for nm, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(x) for x in rot); sc.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); sc.world = w
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = int(OPT.get("samples", 48))
sc.view_settings.view_transform = "Standard"


def shot(name, loc, target, ortho, res):
    cam.data.type = "ORTHO"; cam.data.ortho_scale = ortho
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, f"blockout_soldado_rus_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", sc.render.filepath)


xs = [i * SPACING for i, _ in SOLDIERS] + [pr.location.x]
mid = (min(xs) + max(xs)) / 2
zc = 0.0
shot("fila_frente", (mid, -6.0, zc), (mid, 0, zc), 2.3, (2000, 1800))
shot("fila_costas", (mid, 6.0, zc), (mid, 0, zc), 2.3, (2000, 1800))
shot("fila_tres_quartos", (mid + 3.5, -5.0, zc + 0.8), (mid, 0, zc), 2.5, (2000, 1800))
# side views, one soldier at a time (the row would hide behind itself)
for o in [o for o in sc.objects if o.type == "MESH"]:
    o["_vis"] = not o.hide_render


def only(x):
    for o in [o for o in sc.objects if o.type == "MESH"]:
        wx = (o.matrix_world @ (sum((v.co for v in o.data.vertices), Vector()) / max(1, len(o.data.vertices)))).x
        o.hide_render = (not o["_vis"]) or abs(wx - x) > SPACING / 2


only(0.0)
shot("lado_1812_mosqueteiro", (-6.0, 0.0, zc), (0.0, 0.0, zc), 2.3, (1100, 1800))
only(pr.location.x)
shot("lado_prussiano_comparacao", (pr.location.x - 6.0, 0.0, zc), (pr.location.x, 0.0, zc), 2.3, (1100, 1800))
only(0.0)
shot("gola_tres_quartos", (0.9, -1.5, 0.75), (0.0, -0.01, 0.58), 0.42, (1200, 1200))
shot("gola_lado", (-2.0, -0.01, 0.60), (0.0, -0.01, 0.60), 0.42, (1200, 1200))
# coat front and back close-ups, to compare with the Hermitage coat 1812-1817 (dossier HIST-RUS-INF-COAT-1812-001, A2)
shot("peito_frente", (0.0, -3.0, 0.32), (0.0, 0.0, 0.32), 0.75, (1100, 1200))
shot("abas_costas", (0.0, 3.0, 0.05), (0.0, 0.0, 0.05), 1.05, (1100, 1300))
print("FIM")
