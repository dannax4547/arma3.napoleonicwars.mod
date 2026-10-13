# Blockout + production mesh (Phases 3-4) of the Prussian cloth cap of the mod art ("boné"; the Landwehr cap,
# Landwehrmütze), user decision 2026-10-12 ("Boné da Landwehr", accepted although the Landwehr wore the Litewka, not
# the Kollet of our uniforms: anachronism noted in the report). Read on the mod art (prussia1813_01..03, Reto pack,
# authorised; tiles of 384 px at x 1536-1920, y 2560-3328): cloth crown with a polygonal top seam, a coloured band at
# the bottom, a brown leather peak, two round marks on the front (badge places). Colours of the mod caps (🎮):
#   azul/vermelha (01), azul/amarela (01, 02), verde/preta (02, 03), azul/verde (03), azul/branca (01, partial strip).
# Not in the mod art (🔶): the white-metal Landwehr cross on the front of the band (the national badge of the Landwehr,
# 1813), the proportions (no side view), the lining and the leather sweatband.
# The blend follows the layout read by texturizar_shako_fr.py: one EMPTY "PR_bone_<tag>" per variant, child meshes
# "<tag>_<part>" with materials "BO_<colour>"; texturizar_shako_fr.py raiz=PR_bone_ bakes the texture set.
#   blender -b --factory-startup --python blockout_bone_landwehr.py -- <Test_Character_01 dir> <out.blend> <render dir>
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- proportions (PROPOSED, 🔶)
BAND_H = 0.042            # coloured band (mod art: band ~1/9 of the 384 px tile height of the crown pattern)
CROWN_H = 0.060           # cloth from the band top to the rim of the top
FLARE = 1.17              # the crown widens over the band (soft "Mütze"), rim / band
TOP_DOME = 0.006          # the top disc bulges a little
PLEATS, PLEAT_A = 9, 0.0022   # soft gathers where the cloth is sewn into the band
PEAK_LEN, PEAK_DROP, PEAK_T = 0.050, math.radians(32), 0.0028
N = 72
WALL, CLEAR, TILT, DEPTH_RATIO = shako_fit.WALL, shako_fit.CLEAR, shako_fit.TILT, shako_fit.DEPTH_RATIO

F = shako_fit.compute(SAMPLES)
base_hw = F["head_hw"] + WALL + CLEAR
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')
# crown high enough to clear the top of the head by 10 mm under the centre of the top (the head's highest point is
# near the middle of the band ellipse; the back of the band is lower because of the tilt, which does not matter)
need = F["z_head_top"] + 0.010 - (ROOT @ Vector((0.0, 0.0, 0.0))).z
H_TOTAL = max(BAND_H + CROWN_H, need - 0.006)        # the top disc centre sits ~6 mm above the rim (dome)
CROWN_H = H_TOTAL - BAND_H
print(f"FIT bone: base {2 * base_hw:.3f} x {2 * base_hd:.3f} m, altura {H_TOTAL:.3f} m (faixa {BAND_H:.3f}), "
      f"aba do topo {2 * base_hw * FLARE:.3f} x {2 * base_hd * FLARE:.3f}")

COL = dict(azul_pano=(0.010, 0.016, 0.040), verde_pano=(0.010, 0.022, 0.010), vermelho=(0.274, 0.008, 0.010),
           amarelo=(0.540, 0.320, 0.022), preto=(0.004, 0.004, 0.004), branco=(0.68, 0.68, 0.62),
           verde=(0.007, 0.055, 0.016), couro_marrom=(0.050, 0.028, 0.014), couro=(0.024, 0.021, 0.019),
           prata=(0.60, 0.60, 0.58), forro=(0.33, 0.29, 0.22))
MATS = {}


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name == "prata" else 0.8
        b.inputs["Metallic"].default_value = 1.0 if name == "prata" else 0.0
        MATS[name] = m
    return MATS[name]


PARTS = []


def finish(bm, name, colour, parent, keep_normals=False, smooth=True):
    if not keep_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat(colour))
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); ob.parent = parent
    scene.collection.objects.link(ob); PARTS.append(ob)
    return ob


def grid(bm, rows, closed_u=True):
    nc = len(rows[0])
    for j in range(len(rows) - 1):
        for i in range(nc - (0 if closed_u else 1)):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nc], rows[j + 1][(i + 1) % nc], rows[j + 1][i]))


def ell(th, hw, hd, z):
    """Cap-local point; th = 0 is the FRONT (-Y), +90 deg the wearer's left (+X)."""
    return Vector((hw * math.sin(th), -hd * math.cos(th), z))


def crown_r(t):
    """Crown radius factor from the band top (t = 0) to the rim (t = 1): leaves the band, then swells out to the rim
    with a soft roll (cloth over a stiffened top)."""
    return 1.0 + (FLARE - 1.0) * math.sin(math.pi / 2 * min(1.0, t / 0.85)) ** 1.6 + 0.012 * math.sin(math.pi * t)


def pleat(th, t, seed_ph):
    """Gathers: strongest just above the band, fading toward the rim; a little irregular."""
    w = math.sin(PLEATS * th + seed_ph) + 0.35 * math.sin(2 * PLEATS * th + 2.1 * seed_ph)
    return PLEAT_A * (1 - t) ** 1.4 * (w + 1.35) / 2      # outward only (never into the lining)


# ---------------------------------------------------------------- one cap
def cap(tag, x_off, cloth, band, cross=True):
    root = bpy.data.objects.new(f"PR_bone_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    rnd = random.Random(sum(map(ord, tag)))
    ph = rnd.uniform(0, 6.28)
    # band: coloured cloth over a stiff inner ring, with thickness and a rolled top edge
    bm = bmesh.new()
    zs = [0.0, 0.004, BAND_H * 0.5, BAND_H - 0.004, BAND_H]
    out_rows = [[bm.verts.new(ell(2 * math.pi * i / N, base_hw + 0.0015 + (0.0006 if 0 < k < len(zs) - 1 else 0), base_hd + 0.0015 + (0.0006 if 0 < k < len(zs) - 1 else 0), z)) for i in range(N)] for k, z in enumerate(zs)]
    in_rows = [[bm.verts.new(ell(2 * math.pi * i / N, base_hw - WALL * 0.5, base_hd - WALL * 0.5, z)) for i in range(N)] for z in (0.0, BAND_H)]
    grid(bm, out_rows); grid(bm, [in_rows[0], out_rows[0]]); grid(bm, [out_rows[-1], in_rows[1]])
    finish(bm, f"{tag}_faixa_pano", band, root)
    # leather sweatband inside the band (seen from below), with a stitched top edge
    bm = bmesh.new()
    rows = [[bm.verts.new(ell(2 * math.pi * i / N, base_hw - WALL * 0.5 - 0.0008, base_hd - WALL * 0.5 - 0.0008, z)) for i in range(N)] for z in (0.0015, BAND_H * 0.55, BAND_H * 0.9)]
    grid(bm, rows[::-1])
    finish(bm, f"{tag}_suadouro", "couro", root, keep_normals=True)
    # crown: cloth from the band top to the rim, gathered, then the top disc (stiffened, slightly domed, sagging back)
    bm = bmesh.new()
    NT = 12
    crown = []
    for j in range(NT + 1):
        t = j / NT
        row = []
        for i in range(N):
            th = 2 * math.pi * i / N
            k = crown_r(t) + pleat(th, t, ph) / base_hw
            z = BAND_H + CROWN_H * t - 0.006 * (1 - math.cos(th)) / 2 * t      # back of the crown sinks a little
            row.append(bm.verts.new(ell(th, base_hw * k, base_hd * k, z)))
        crown.append(row)
    grid(bm, crown)
    # rolled rim into the top: two rings stepping in
    rim = crown[-1]
    roll = []
    for s, (dk, dz) in enumerate(((-0.010, 0.004), (-0.030, 0.006))):
        roll.append([bm.verts.new(ell(2 * math.pi * i / N, base_hw * (crown_r(1.0) + dk), base_hd * (crown_r(1.0) + dk),
                                      BAND_H + CROWN_H - 0.006 * (1 - math.cos(2 * math.pi * i / N)) / 2 + dz)) for i in range(N)])
    grid(bm, [rim] + roll)
    # top disc: concentric rings to a centre, domed, with a shallow dent from the wearer's hand at the front
    last = roll[-1]
    rings = [last]
    for r_ in (0.80, 0.58, 0.36, 0.16):
        ring = []
        for i in range(N):
            th = 2 * math.pi * i / N
            kk = (crown_r(1.0) - 0.030) * r_
            z = BAND_H + CROWN_H + 0.006 + TOP_DOME * (1 - r_ ** 2) - 0.006 * (1 - math.cos(th)) / 2 * r_ \
                - 0.0025 * math.exp(-((th) ** 2) / 0.3) * (1 - r_) * 2
            ring.append(bm.verts.new(ell(th, base_hw * kk, base_hd * kk, z)))
        rings.append(ring)
    grid(bm, rings)
    c = bm.verts.new(Vector((0, 0, BAND_H + CROWN_H + 0.006 + TOP_DOME - 0.004)))
    for i in range(N):
        bm.faces.new((c, rings[-1][i], rings[-1][(i + 1) % N]))
    finish(bm, f"{tag}_copa", cloth, root)
    # lining of the crown (light linen, seen from below): a slightly smaller inner shell closing the crown
    bm = bmesh.new()
    lrows = [[bm.verts.new(ell(2 * math.pi * i / N, (base_hw - WALL) * (1 + (crown_r(t) - 1) * 0.75),
                                (base_hd - WALL) * (1 + (crown_r(t) - 1) * 0.75), BAND_H * (1 - t) + (BAND_H + CROWN_H - 0.004) * t
                                - 0.006 * (1 - math.cos(2 * math.pi * i / N)) / 2 * t))
              for i in range(N)] for t in (0.0, 0.5, 1.0)]
    grid(bm, lrows[::-1])
    cl = bm.verts.new(Vector((0, 0, BAND_H + CROWN_H - 0.004)))
    for i in range(N):
        bm.faces.new((cl, lrows[-1][(i + 1) % N], lrows[-1][i]))
    finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    # piping of the top seam (mod art: polygonal seam line): thin cord in the band colour 🔶 -> kept in cloth colour
    # leather peak: front arc, sloping down, with a stitched border (UV/texture) and thickness
    bm = bmesh.new()
    arc = [math.radians(-70 + 140 * i / 28) for i in range(29)]

    def prow(off, dz):
        out = []
        for a in arc:
            p0 = ell(a, base_hw + 0.0015, base_hd + 0.0015, 0.004)
            n = Vector((math.sin(a) / base_hw, -math.cos(a) / base_hd, 0)).normalized()
            w = 1 - (abs(a) / math.radians(70)) ** 3
            out.append(p0 + n * off * w * math.cos(PEAK_DROP) + Vector((0, 0, -off * w * math.sin(PEAK_DROP) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in prow(f * PEAK_LEN, 0.0)] for f in (0.0, 0.5, 1.0)]
    rows += [[bm.verts.new(p) for p in prow(f * PEAK_LEN, -PEAK_T)] for f in (1.0, 0.5, 0.0)]
    grid(bm, rows + [rows[0]], closed_u=False)
    for r in (0, len(arc) - 1):
        bm.faces.new([rows[k][r] for k in range(len(rows))][::-1])
    finish(bm, f"{tag}_pala_couro", "couro_marrom", root)
    # Landwehr cross (cross pattee) in white metal on the front of the band 🔶
    if cross:
        bm = bmesh.new()
        a_, w_, t_ = 0.017, 0.0055, 0.0016            # arm length from the centre, half-width at the centre, thickness
        # outline order: rotate so each arm's points follow round the cross
        pts = []
        for k_ in range(4):
            ang = k_ * math.pi / 2
            c_, s_ = math.cos(ang), math.sin(ang)
            for (u, v) in ((w_, -w_), (a_, -a_ * 0.52), (a_, a_ * 0.52)):
                pts.append((u * c_ - v * s_, u * s_ + v * c_))
        zc = BAND_H * 0.52

        def on_band(x, z, o):
            th = x / base_hd                       # arc length on the front ~ radius base_hd
            return ell(th, base_hw + 0.0021 + o, base_hd + 0.0021 + o, zc + z)
        fr = [bm.verts.new(on_band(x, z, t_)) for x, z in pts]
        bk = [bm.verts.new(on_band(x, z, 0.0)) for x, z in pts]
        cf, cb = bm.verts.new(on_band(0, 0, t_ + 0.0004)), bm.verts.new(on_band(0, 0, 0.0))
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((cf, fr[i], fr[j])); bm.faces.new((cb, bk[j], bk[i])); bm.faces.new((fr[i], bk[i], bk[j], fr[j]))
        finish(bm, f"{tag}_cruz", "prata", root, smooth=False)
    return root


# variants: tag, cloth, band (mod colours)
VARIANTS = [("azul_faixa_vermelha", "azul_pano", "vermelho"), ("azul_faixa_amarela", "azul_pano", "amarelo"),
            ("verde_faixa_preta", "verde_pano", "preto"), ("azul_faixa_verde", "azul_pano", "verde"),
            ("azul_faixa_branca", "azul_pano", "branco")]
SPACING = 0.36
roots = [cap(t, i * SPACING, c, b) for i, (t, c, b) in enumerate(VARIANTS)]

# ---------------------------------------------------------------- checks: clearance over the approximate head
bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:22s} pecas {len(obs)}  triangulos {tris:5d}  topo {zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

# ---------------------------------------------------------------- approximate head + renders
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
hme.materials.append(skin)
for p in hme.polygons:
    p.use_smooth = True
for i in range(len(VARIANTS)):
    h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    scene.collection.objects.link(h)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
os.makedirs(RENDER_DIR, exist_ok=True)
zc = (ROOT @ Vector((0, 0, H_TOTAL / 2))).z


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 700)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_bone_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_tres_quartos", (mid_x + 1.0, -2.2, zc + 0.5), (mid_x, 0, zc - 0.03), lens=45, res=(2000, 700))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
for j, r in enumerate(roots):
    for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
        o.hide_render = j != 0
shot("lado", (-1.5, F["head_cy"], zc), (0, F["head_cy"], zc), ortho=0.45, res=(900, 800))
shot("perto", (0.30, -0.42, zc + 0.10), (0, F["head_cy"], zc - 0.02), lens=60, res=(1000, 900))
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
