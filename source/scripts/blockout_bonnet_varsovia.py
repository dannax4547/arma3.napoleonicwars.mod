# Bearskin ("bermyca") of the GRENADIERS OF THE DUCHY OF WARSAW line infantry, regulation of 3 September 1810 (spec
# docs/specs/aliados_fr_1812.md section 1.1, 📜 Gembarzewski 1905 / Zygulski & Wielecki 1988): "a small peak edged
# with yellow metal" (not modelled yet 🔶); yellow plate with the regiment number, a WHITE eagle and two grenades at the
# sides; CRIMSON plume ("kita pasowa"); WHITE cords; round top of crimson cloth (the white lace cross of the Guard
# bearskin kept: it is seen on a Polish grenadier's top in the drawing "Wojsko polskie z okresu Ksiestwa Warszawskiego"
# 1850-60, Polona, 🔶).
# Copy of blockout_bonnet_suica.py (itself a copy of the Old Guard bearskin v5): plate from placa_varsovia_relevo.py
# (placa=), plus the white-metal eagle as its own part on the plate ("aguia_prata", outline aguia=<json>, the czapka
# eagle traced from polandINF c0 r5 🎮). Root empties PB_<tag>: texturizar_aliados.py raiz=PB_ nome=HCL_Bonnet_Varsovia_
# textura=hcl_bonnet_varsovia_ arte=<relief png>.
#   blender -b --factory-startup --python blockout_bonnet_varsovia.py -- <Test_Character_01 dir> <out.blend> <render dir>
#           placa=<placa_varsovia_contorno.json> aguia=<placa_aguia_varsovia.json>
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit
from plumet import plumet, feather_material

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- proportions (PROPOSED, 🔶)
# v4 (2026-10-13): sourced measures (docs/specs/barretina_francesa_1812.md 7.1; Bertrand-Malvaux bonnet 1808-1815,
# Wikipedia fr): 35 cm at the front, 39 cm at the back, 27 cm wide at the top, plate 217 x 160 mm, top patch oval
# 135 x 115 mm, plume socket 24 cm above the band
HS = 0.304              # side up to the top at the FRONT
DOME = 0.046            # rounded edge into a flat-ish top (front total 0.35 m)
BACK_RISE = 0.114       # the back is 39 cm: 11.4 % higher than the front
SWELL = 1.39            # top / band (27 cm at the top)
PLATE_W, PLATE_STRETCH = 0.217, 1.89      # plate width; vertical stretch of the mod art (its tile is squashed 🔶)
PLATE_Z0 = 0.016
COCK_R = 0.030
PLUME_H = 0.35          # sources: 28 (reproduction) to 37 cm; was 0.38
PLUME_R = 0.075
WALL, CLEAR, TILT, DEPTH_RATIO = shako_fit.WALL, shako_fit.CLEAR, shako_fit.TILT, shako_fit.DEPTH_RATIO

F = shako_fit.compute(SAMPLES)
base_hw = F["head_hw"] + WALL + CLEAR + 0.004          # fur thickness at the band
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR + 0.004)
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], F["z_forehead"] - 0.006))) @ Matrix.Rotation(-TILT, 4, 'X')
ATLAS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "ntw", "france", "FranceINF_diffuse.png"))
ATLAS_PX = 4096
PLATE_JSON = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "bonnet", "hcl_bonnet_fr", "placa_bonnet_guarda.json"))
OPTB = dict(x.split("=", 1) for x in args[3:] if "=" in x)
PLATE_V5 = os.path.abspath(OPTB["placa"])                  # placa_varsovia_relevo.py
AGUIA_JSON = os.path.abspath(OPTB["aguia"])               # outline of the white eagle (atlas pixels)

COL = dict(pelo=(0.010, 0.009, 0.008), latao=(0.70, 0.50, 0.16), vermelho=(0.55, 0.03, 0.03), branco=(0.82, 0.82, 0.80),
           azul=(0.04, 0.08, 0.35), verde=(0.03, 0.20, 0.06))
COL["prata"] = (0.72, 0.72, 0.70)                       # white metal of the eagle
MATS, PMATS, PARTS = {}, {}, []


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name == "latao" else 0.8
        b.inputs["Metallic"].default_value = 1.0 if name == "latao" else 0.0
        MATS[name] = m
    return MATS[name]


def pmat(name):
    if name not in PMATS:
        m = bpy.data.materials.new("BO_plumet_" + name); m.use_nodes = True
        feather_material(m, COL[name]); PMATS[name] = m
    return PMATS[name]


def finish(bm, name, colour, parent, by_colour=None, keep_normals=False, plume=False, smooth=True):
    if not keep_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if by_colour:
        names = list(by_colour)
        for mi, nm in enumerate(names):
            for f in by_colour[nm]:
                f.material_index = mi
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for nm in (names if by_colour else [colour]):
        me.materials.append(pmat(nm) if plume else mat(nm))
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


# ---------------------------------------------------------------- the shell surface S(theta, s)
# profile: (radius factor, z) from the band (s = 0) over the side and the dome to the top (s = 1), by arc length
prof = []
for k in range(25):
    t = k / 24
    prof.append((1.0 + (SWELL - 1.0) * (0.75 * t ** 0.9 + 0.25 * math.sin(math.pi / 2 * t)), HS * t))
rf_top = prof[-1][0]
for k in range(1, 13):
    a = math.pi / 2 * k / 12
    prof.append((rf_top * math.cos(a) ** 0.55 if k < 12 else 0.0, HS + DOME * math.sin(a) ** 0.55))   # squarish edge
L_ = [0.0]
for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
    L_.append(L_[-1] + math.hypot((r1 - r0) * base_hd, z1 - z0))
L_ = np.array(L_) / L_[-1]
PR = np.array(prof)
S_SIDE = float(np.interp(HS, PR[:, 1], L_))     # s at the top of the side


def tuft(th, s):
    """Low-frequency lumps of the fur mass (m), deterministic."""
    return 0.0050 * (math.sin(5 * th + 1.3) * math.sin(9 * s + 0.4) + 0.6 * math.sin(11 * th - 7 * s + 2.0)) * min(1.0, s * 8)


def S(th, s, off=0.0, lumps=True):
    """Shell point; th = 0 is the FRONT (-Y), +90 deg the wearer's left (+X). off along the outward normal."""
    rf = float(np.interp(s, L_, PR[:, 0])); z = float(np.interp(s, L_, PR[:, 1]))
    p = Vector((base_hw * rf * math.sin(th), -base_hd * rf * math.cos(th), z * (1 + BACK_RISE * (1 - math.cos(th)) / 2)))
    if off or lumps:
        n = Sn(th, s)
        p = p + n * (off + (tuft(th, s) if lumps else 0.0))
    return p


def Sn(th, s, e=1e-3):
    def raw(t_, s_):
        rf = float(np.interp(s_, L_, PR[:, 0])); z = float(np.interp(s_, L_, PR[:, 1]))
        return Vector((base_hw * rf * math.sin(t_), -base_hd * rf * math.cos(t_), z * (1 + BACK_RISE * (1 - math.cos(t_)) / 2)))
    s0, s1 = max(0.0, s - e), min(1.0, s + e)
    dth = raw(th + e, s) - raw(th - e, s)
    ds = raw(th, s1) - raw(th, s0)
    n = dth.cross(ds)
    if n.length < 1e-9:
        return Vector((0, 0, 1))
    n.normalize()
    c = raw(th, s)
    return n if n.dot(Vector((c.x, c.y, 0.0)) + Vector((0, 0, 0.3 * (c.z - HS * 0.5)))) > 0 else -n


def s_of_z(z):
    return float(np.interp(z, PR[:25, 1], L_[:25]))


# ---------------------------------------------------------------- pieces
def shell(tag, root):
    bm = bmesh.new()
    NT, NSS = 72, 36                                      # v4 (was 48 x 26)
    rows = [[bm.verts.new(S(2 * math.pi * i / NT, j / NSS)) for i in range(NT)] for j in range(NSS)]
    grid(bm, rows)
    top = bm.verts.new(S(0.0, 1.0))
    for i in range(NT):
        bm.faces.new((rows[-1][i], rows[-1][(i + 1) % NT], top))
    # inner face of the band (seen from below): a short lining ring
    inner = [bm.verts.new(Vector((base_hw * math.sin(2 * math.pi * i / NT) * 0.97, -base_hd * math.cos(2 * math.pi * i / NT) * 0.97, 0.0))) for i in range(NT)]
    inner2 = [bm.verts.new(Vector((base_hw * math.sin(2 * math.pi * i / NT) * 0.95, -base_hd * math.cos(2 * math.pi * i / NT) * 0.95, 0.05))) for i in range(NT)]
    grid(bm, [inner2, inner, rows[0]])
    finish(bm, f"{tag}_pele_corpo", "pelo", root)


def art_uv(px, py):
    return (px / ATLAS_PX, 1.0 - py / ATLAS_PX)


def plate(tag, root):
    """Brass plate wrapped on the front of the fur, 7 mm proud of the shell (it rests on the fur), 1.1 mm thick.
    v5: the smoothed outline in mm (placa_guarda_relevo.py), filled with an even triangulation (points every 8 mm,
    constrained Delaunay) so it follows the curve of the fur; UV "arte" = position on the 8 px/mm relief."""
    from mathutils.geometry import delaunay_2d_cdt
    from mathutils import Vector as V2
    bj = json.load(open(PLATE_V5))
    WMM, HMM = bj["largura_mm"], bj["altura_mm"]
    out = [tuple(p) for p in bj["mm"]]
    # outline resampled every ~4 mm, interior points on an 8 mm grid
    ring = []
    for a_, b_ in zip(out, out[1:] + out[:1]):
        n = max(1, int(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) / 4.0))
        ring += [(a_[0] + (b_[0] - a_[0]) * k / n, a_[1] + (b_[1] - a_[1]) * k / n) for k in range(n)]

    def inside(x, y, m=3.0):
        c = False
        for (ax_, ay_), (bx_, by_) in zip(out, out[1:] + out[:1]):
            if (ay_ > y) != (by_ > y) and x < (bx_ - ax_) * (y - ay_) / (by_ - ay_) + ax_:
                c = not c
        if not c:
            return False
        return min(math.hypot(x - rx, y - ry) for rx, ry in ring) > m
    pts = list(ring) + [(x, y) for x in np.arange(-WMM / 2 + 4, WMM / 2, 8.0) for y in np.arange(4, HMM, 8.0) if inside(x, y)]
    nr = len(ring)
    vco, _, fcs, _, _, _ = delaunay_2d_cdt([V2(p) for p in pts], [(i, (i + 1) % nr) for i in range(nr)], [], 0, 1e-6)
    fcs = [f for f in fcs if inside(sum(vco[i].x for i in f) / 3, sum(vco[i].y for i in f) / 3, m=0.0)]   # inside the outline
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("arte")

    def P(x, y, off):
        z = PLATE_Z0 + y * 0.001
        s = s_of_z(z)
        rf = float(np.interp(s, L_, PR[:, 0]))
        return S(x * 0.001 / (base_hd * rf), s, off, lumps=False)
    front = [bm.verts.new(P(v.x, v.y, 0.0081)) for v in vco]
    back = [bm.verts.new(P(v.x, v.y, 0.0070)) for v in vco]
    uv = [(v.x / WMM + 0.5, v.y / HMM) for v in vco]
    for f in fcs:
        for layer, rev in ((front, False), (back, True)):
            idx = list(f)[::-1] if rev else list(f)
            try:
                nf = bm.faces.new([layer[i] for i in idx])
            except ValueError:
                continue
            for l, i in zip(nf.loops, idx):
                l[uvl].uv = uv[i]
    # the edge of the sheet
    by_co = {(round(v.x, 4), round(v.y, 4)): i for i, v in enumerate(vco)}
    ridx = [by_co.get((round(x, 4), round(y, 4))) for x, y in ring]
    ridx = [i for i in ridx if i is not None]
    for a_, b_ in zip(ridx, ridx[1:] + ridx[:1]):
        try:
            nf = bm.faces.new((front[a_], back[a_], back[b_], front[b_]))
        except ValueError:
            continue
        for l, i in zip(nf.loops, (a_, a_, b_, b_)):
            l[uvl].uv = uv[i]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    h_ = HMM * 0.001
    z_top = PLATE_Z0 + h_
    ob = finish(bm, f"{tag}_placa", "latao", root, keep_normals=True)
    print(f"PLACA {tag}: {WMM:.0f} x {HMM:.0f} mm, z {PLATE_Z0:.3f}..{z_top:.3f}, {len(ob.data.polygons)} faces, "
          f"{len(ridx)} pontos de borda")
    half_th = PLATE_W / 2 / (base_hd * 1.05)
    return (PLATE_Z0, z_top, half_th, out)


def top_patch(tag, root):
    """Red top patch on the back of the dome, a white lace cross on it. Returns (centre th, s, radius) to keep the
    hair locks off it."""
    th0, s0 = math.pi, S_SIDE + (1 - S_SIDE) * 0.30
    c = S(th0, s0, 0.0, lumps=False)
    n = Sn(th0, s0)
    u = Vector((1, 0, 0)); v_ = n.cross(u).normalized(); u = v_.cross(n).normalized()
    R_ = 0.0675                                           # v4: oval 135 x 115 mm (Ra across, R_ fore-aft)
    Ra = 0.0575
    bm = bmesh.new()
    NR, NA = 5, 32
    rings = []
    for j in range(1, NR + 1):
        r = R_ * j / NR
        ring = []
        for i in range(NA):
            a = 2 * math.pi * i / NA
            p = c + (u * math.cos(a) * Ra / R_ + v_ * math.sin(a)) * r
            ring.append(bm.verts.new(p + n * (0.0045 - 0.0030 * (r / R_) ** 2)))   # v5: lower, the fur rises round it
        rings.append(ring)
    cv = bm.verts.new(c + n * 0.0045)
    for i in range(NA):
        bm.faces.new((cv, rings[0][i], rings[0][(i + 1) % NA]))
    grid(bm, rings)
    finish(bm, f"{tag}_calota", "vermelho", root)
    # cross: two lace strips 9 mm wide, 1.2 mm thick, from rim to rim (🔶 user choice)
    for k, (a_, b_) in enumerate(((u, v_), (v_, u))):
        bm = bmesh.new()
        pts = [c + a_ * ((Ra if k == 0 else R_) * 0.92 * t) for t in np.linspace(-1, 1, 13)]
        rows = []
        for p in pts:
            r = (p - c).length
            h = 0.0045 - 0.0030 * (r / R_) ** 2 + 0.0004
            rows.append([bm.verts.new(p + n * h + b_ * sx * 0.0045 + n * sz * 0.0012) for sx, sz in ((-1, 0), (1, 0), (1, 1), (-1, 1))])
        grid(bm, rows)
        for r_, sg in ((rows[0], -1), (rows[-1], 1)):
            bm.faces.new(r_ if sg > 0 else r_[::-1])
        finish(bm, f"{tag}_cruz_galao_{k}", "branco", root, smooth=False)
    return th0, s0, R_, Ra, c, u, v_


def pleated(name, centre, normal, r_in, r_out, t, n, colour, parent):
    """Pleated ring of the cockade: n pleats, each a fold rising t at its crest (as the shakos, v5)."""
    bm = bmesh.new()
    u = normal.orthogonal().normalized(); v = normal.cross(u).normalized()
    M = 2 * n
    rows = []
    for rr, k in ((r_in, 0.4), ((r_in + r_out) / 2, 1.0), (r_out, 0.7)):
        row = []
        for i in range(M):
            a = 2 * math.pi * i / M
            h = t * k * (1.0 if i % 2 == 0 else 0.15)
            row.append(bm.verts.new(centre + normal * h + rr * (math.cos(a) * u + math.sin(a) * v)))
        rows.append(row)
    base_out = [bm.verts.new(centre + r_out * (math.cos(2 * math.pi * i / M) * u + math.sin(2 * math.pi * i / M) * v)) for i in range(M)]
    grid(bm, rows + [base_out])
    return finish(bm, name, colour, parent)


def disc(name, centre, normal, r, t, colour, parent, segs=24):
    bm = bmesh.new()
    u = normal.orthogonal().normalized(); v = normal.cross(u).normalized()
    rows = [[bm.verts.new(centre + normal * a + rr * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)]
            for a, rr in ((0, 0.0005), (0, r), (t, r), (t, 0.0005))]
    grid(bm, rows)
    return finish(bm, name, colour, parent)


def lathe_obj(name, profile, centre, colour, parent, axis=Vector((0, 0, 1)), segs=20):
    bm = bmesh.new()
    u = axis.orthogonal().normalized(); v = axis.cross(u).normalized()
    rows = [[bm.verts.new(centre + axis * a + r * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)] for a, r in profile]
    grid(bm, rows)
    for ring, a in ((rows[0], profile[0][0]), (rows[-1], profile[-1][0])):
        cc = bm.verts.new(centre + axis * a)
        for i in range(segs):
            bm.faces.new((cc, ring[i], ring[(i + 1) % segs]))
    return finish(bm, name, colour, parent)


def catmull(pts, n=10):
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for s in range(n):
            t = s / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def tube(name, path, r, colour, parent, segs=8):
    bm = bmesh.new()
    rows = []
    for k, p in enumerate(path):
        tng = (path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]).normalized()
        nrm = tng.orthogonal().normalized(); side = tng.cross(nrm)
        rows.append([bm.verts.new(p + r * (math.cos(2 * math.pi * s / segs) * nrm + math.sin(2 * math.pi * s / segs) * side)) for s in range(segs)])
    grid(bm, rows)
    for ring, p in ((rows[0], path[0]), (rows[-1], path[-1])):
        cc = bm.verts.new(p)
        for i in range(segs):
            bm.faces.new((cc, ring[i], ring[(i + 1) % segs]))
    return finish(bm, name, colour, parent)


def fringe_tassel(name, top, colour, parent, r=0.010, length=0.040, strands=20, seed=3):
    rnd = random.Random(seed)
    lathe_obj(name + "_cabeca", [(0.0, 0.002), (-0.006, 0.007), (-0.013, r), (-0.015, r * 0.85)], top, colour, parent, segs=12)
    bm = bmesh.new()
    for i in range(strands):
        a = 2 * math.pi * i / strands + rnd.uniform(-0.12, 0.12)
        o = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-math.sin(a), math.cos(a), 0))
        L = length * rnd.uniform(0.9, 1.08)
        rows = []
        for t_ in (0.0, 0.5, 1.0):
            c = top + Vector((0, 0, -0.013 - L * t_)) + o * (r * 0.9 + 0.004 * t_)
            hw = 0.0016 * (1 - 0.4 * t_)
            rows.append((bm.verts.new(c - sd * hw), bm.verts.new(c + sd * hw)))
        for (a0, b0), (a1, b1) in zip(rows, rows[1:]):
            bm.faces.new((a0, b0, b1, a1))
        rows2 = [(bm.verts.new(a0.co - o * 0.0003), bm.verts.new(b0.co - o * 0.0003)) for a0, b0 in rows]
        for (a0, b0), (a1, b1) in zip(rows2, rows2[1:]):
            bm.faces.new((a1, b1, b0, a0))
    return finish(bm, name + "_franja", colour, parent, keep_normals=True)


def cords(tag, root):
    """Parade cords as in the user's reference photo (2026-10-12, "faz igual a este"): a wide flat white BRAID across
    the front, from high on the wearer's right down to the left top corner of the plate, its plaits in herringbone
    (each plait its own domed lozenge, alternating sides, over a base band); a tassel hangs from its upper end; from
    there the cord runs round the right side to two flat woven raquettes and two fringed tassels."""
    off = 0.017
    ctrl = [(-1.05, 0.315), (-0.50, 0.270), (0.10, 0.228), (0.62, 0.205), (0.98, 0.192)]   # v4: above the bigger plate
    offs = [0.018, 0.018, 0.019, 0.022, 0.026]           # v5: clear of the long locks where the shell swells (left)
    path = catmull([S(th, s_of_z(z), o_, False) for (th, z), o_ in zip(ctrl, offs)], 10)
    # base band (the braid's underside): flat strip lying on the fur
    bm = bmesh.new()
    rows = []
    nrm = []
    for k, p in enumerate(path):
        tng = (path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]).normalized()
        n = Vector((p.x, p.y, 0.0)).normalized()
        n = (n - tng * n.dot(tng)).normalized()
        sd = tng.cross(n).normalized()
        nrm.append((tng, n, sd))
        rows.append([bm.verts.new(p + sd * w * 0.013 - n * 0.001) for w in (-1, 1)])
    for r0, r1 in zip(rows, rows[1:]):
        bm.faces.new((r0[0], r0[1], r1[1], r1[0]))
    finish(bm, f"{tag}_cordao_base", "branco", root)
    # plaits
    bm = bmesh.new()
    L = [0.0]
    for p0, p1 in zip(path, path[1:]):
        L.append(L[-1] + (p1 - p0).length)
    step, k_, d = 0.0105, 0, 0.004
    while d < L[-1] - 0.004:
        i = max(0, min(len(path) - 2, int(np.searchsorted(L, d)) - 1))
        f_ = (d - L[i]) / max(1e-9, L[i + 1] - L[i])
        c = path[i].lerp(path[i + 1], f_)
        tng, n, sd = nrm[i]
        sg = 1 if k_ % 2 == 0 else -1
        ax = (tng * 0.62 + sd * sg * 0.78).normalized()          # plait axis: diagonal, alternating
        wx = n.cross(ax).normalized()
        cc = c + sd * sg * 0.0055
        grid_ = []
        for u in (-1.0, 0.0, 1.0):
            row = []
            for v in (-1.0, -0.5, 0.0, 0.5, 1.0):
                half_w = 0.0042 * (1 - abs(v) ** 2) + 0.0006
                q = cc + ax * (v * 0.0115) + wx * (u * half_w) + n * (0.0028 * (1 - v * v) * (1 - 0.5 * u * u))
                row.append(bm.verts.new(q))
            grid_.append(row)
        for u in range(2):
            for v in range(4):
                f = bm.faces.new((grid_[u][v], grid_[u + 1][v], grid_[u + 1][v + 1], grid_[u][v + 1]))
                f.normal_update()
                if f.normal.dot(n) < 0:
                    f.normal_flip()
        d += step / 2
        k_ += 1
    finish(bm, f"{tag}_cordao_trancas", "branco", root, keep_normals=True)
    # tassel from the braid's upper end, hanging on the front
    top = path[0] + nrm[0][1] * 0.004
    tube(f"{tag}_cordao_borla", [top, top + Vector((0, 0, -0.018)) + nrm[0][1] * 0.006], 0.0028, "branco", root)
    fringe_tassel(f"{tag}_borla_frente", top + Vector((0, 0, -0.018)) + nrm[0][1] * 0.006, "branco", root, r=0.009,
                  length=0.042, seed=11)
    # round the right side to the raquettes
    side = S(math.radians(-102), s_of_z(0.250), 0.016, False)
    hang = catmull([path[0], S(math.radians(-85), s_of_z(0.29), 0.016, False), side, side + Vector((0, 0, -0.04))], 6)
    tube(f"{tag}_cordao_lado", hang, 0.0036, "branco", root)
    n = Sn(math.radians(-102), s_of_z(0.10)); n.z = 0; n.normalize()
    for k, dz in enumerate((-0.060, -0.112)):
        rq = side + Vector((0, 0, dz)) + n * (0.005 + 0.003 * k)
        ob = lathe_obj(f"{tag}_raquete_{k}", [(-0.030, 0.002), (-0.021, 0.013), (0.0, 0.0175), (0.021, 0.013), (0.030, 0.002)],
                       rq, "branco", root, segs=16)
        for v in ob.data.vertices:                         # a raquette is a flat woven oval, not a ball
            dv = v.co - rq
            v.co = rq + dv - n * dv.dot(n) * 0.62
    tb = side + Vector((0, 0, -0.140)) + n * 0.010
    for dx, sd_ in ((-0.012, 7), (0.012, 8)):
        t0 = tb + Vector((dx * n.y, -dx * n.x, 0.0))
        fringe_tassel(f"{tag}_borla_{sd_}", t0, "branco", root, seed=sd_)


def plume_and_cockade(tag, root, colours):
    th = math.radians(88)                                   # wearer's left
    zc = 0.210
    s = s_of_z(zc)
    n = Sn(th, s)
    c0 = S(th, s, 0.009, False)
    # Duchy of Warsaw: WHITE cockade (📜 "kokarda biala" of the 1810 regulation), not the French tricolour
    pleated(f"{tag}_cocar_fora", c0, n, COCK_R * 0.62, COCK_R, 0.003, 36, "branco", root)
    pleated(f"{tag}_cocar_dentro", c0 + n * 0.0012, n, COCK_R * 0.30, COCK_R * 0.66, 0.003, 28, "branco", root)
    disc(f"{tag}_cocar_centro", c0 + n * 0.0036, n, COCK_R * 0.33, 0.0015, "branco", root, segs=32)
    if not colours:
        return
    sb = s_of_z(0.240)                                    # socket 24 cm above the band (source)
    base = S(th, sb, 0.020, False)
    lathe_obj(f"{tag}_tulipa", [(-0.018, 0.0045), (0.0, 0.0065), (0.012, 0.010)], base, "latao", root)
    bm = bmesh.new()
    by = plumet(bm, base + Vector((0, 0, 0.012)), H=PLUME_H, R=PLUME_R, colours=colours, seed=sum(map(ord, tag)), lean=0.05,
                rings=40, per_ring=20, feather_len=0.062, fluff=2.2, estilo="v4")   # v5: smaller, denser feathers
    finish(bm, f"{tag}_plumet", None, root, by_colour=by, keep_normals=True, plume=True)


def hair(tag, root, plate_box, patch, seed=5):
    """Hair locks in two layers (v2, user 2026-10-12 "traz mais realismo a bear skin"; v5 2026-10-13 "mais realismo"):
      - under-fur: short dense locks lying flat, so no smooth shell shows between the long locks;
      - top locks: long bundles that leave the skin raised and fall in a curve down the surface (gravity), the tip
        lying back on the mass (v4 tips stood out like straw); on the dome they swirl out of a crown; at the sides and
        back the longest hang over the band by up to 2 cm, at the forehead the fur is cut at the band; around the
        plate they are lifted over its edges (the plate is mounted ON the fur), never across its face; around the top
        patch they overlap its rim.
    Long lock: 4 stations (root, 1/3, 2/3, tip) x 3 points (edges curled into the mass, raised middle) = 12 triangles,
    single-sided (the underside lies against the shell). UV u across / v along, face float 'tint' = shade tile."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    tint = bm.faces.layers.float.new("tint")
    z_p0, z_p1, half_th, p_out = plate_box if plate_box else (None, None, None, None)

    def plate_xy(th, z):
        s_ = s_of_z(z)
        rf = float(np.interp(s_, L_, PR[:, 0]))
        return th * base_hd * rf * 1000.0, (z - z_p0) * 1000.0

    def under_plate(th, z, grow=0.0):
        """Root under the plate (its real pointed outline, mm, grown by grow mm)."""
        x, y = plate_xy(th, z)
        c = False
        for (ax_, ay_), (bx_, by_) in zip(p_out, p_out[1:] + p_out[:1]):
            if (ay_ > y) != (by_ > y) and x < (bx_ - ax_) * (y - ay_) / (by_ - ay_) + ax_:
                c = not c
        if c or grow <= 0:
            return c
        for (ax_, ay_), (bx_, by_) in zip(p_out, p_out[1:] + p_out[:1]):
            ex, ey = bx_ - ax_, by_ - ay_
            t = max(0.0, min(1.0, ((x - ax_) * ex + (y - ay_) * ey) / (ex * ex + ey * ey + 1e-9)))
            if math.hypot(x - ax_ - t * ex, y - ay_ - t * ey) < grow:
                return True
        return False
    th_c, s_c, R_c, Ra_c, pc, pu, pv = patch
    count = {"base": 0, "longa": 0}

    def in_patch(p, grow):
        d = p - pc
        return (d.dot(pu) / (Ra_c + grow)) ** 2 + (d.dot(pv) / (R_c + grow)) ** 2 < 1.0

    def lock(th, s, L, W, lift, extra_ang=0.0, drop_below=0.0, short=False, near_plate=False, over=False, tuck=0.0):
        p0 = S(th, s, 0.0)
        n = Sn(th, s)
        g = Vector((0, 0, -1)) - n * (-n.z)
        if g.length < 0.15:
            g = Vector((p0.x, p0.y, 0.0))
        g.normalize()
        side = n.cross(g).normalized()
        ang = rnd.uniform(-0.45, 0.45) + extra_ang
        if near_plate:
            ang = rnd.uniform(-0.15, 0.15)                  # straight down beside / above the plate
        d = (g * math.cos(ang) + side * math.sin(ang)).normalized()
        sd = n.cross(d).normalized()
        curl = rnd.uniform(-0.006, 0.006)
        pts, wid = [], []
        st = ((0.0, 0.95), (1.0, 0.20)) if short else ((0.0, 0.80), (0.34, 1.0), (0.68, 0.78), (1.0, 0.10))
        for t, wf in st:
            if over:
                rise = 0.0125 * min(1.0, t * 3.0)           # over the plate: clear of it
            else:
                rise = lift * (4.0 * t * (1.0 - t) + 0.22 * t) - tuck * t * t   # arched, the tip back on the mass
            dd = (d * (1.0 - 0.35 * t) + g * (0.35 * t)).normalized()          # bends toward the fall line
            p = p0 + n * (0.0015 + rise) + dd * (L * t) + sd * (curl * t * t)
            if drop_below and t > 0:                       # over the band edge: the tip falls straight down
                p = p + Vector((0, 0, -drop_below * t ** 2))
            pts.append(p); wid.append(W * wf / 2)
        sh = rnd.uniform(0.0, 1.0)
        rows = []
        for p, hw, (t, _) in zip(pts, wid, st):
            cup = n * (0.35 * hw)
            rows.append((bm.verts.new(p - sd * hw - cup), bm.verts.new(p + n * 0.0012), bm.verts.new(p + sd * hw - cup), t))
        for k in range(len(rows) - 1):
            (a0, m0, b0, t0), (a1, m1, b1, t1) = rows[k], rows[k + 1]
            for (x0, x1, y1, y0, u0, u1) in ((a0, m0, m1, a1, 0.0, 0.5), (m0, b0, b1, m1, 0.5, 1.0)):
                f = bm.faces.new((x0, x1, y1, y0))
                for l, uv in zip(f.loops, ((u0, t0), (u1, t0), (u1, t1), (u0, t1))):
                    l[uvl].uv = uv
                f[tint] = sh; f.smooth = True
                f.normal_update()
                if f.normal.dot(n) < 0:
                    f.normal_flip()

    def place(n_th, n_rows, layer):
        for j in range(n_rows):
            for i in range(n_th):
                s = (j + rnd.uniform(0.05, 0.95)) / n_rows * 0.985
                th = 2 * math.pi * (i + rnd.uniform(0.0, 1.0) + 0.5 * (j % 2)) / n_th
                th = (th + math.pi) % (2 * math.pi) - math.pi
                p0 = S(th, s, 0.0)
                z0 = p0.z
                # the patch: no roots on the cloth; long locks rooted just outside fall over its rim
                if in_patch(p0, 0.002 if layer == "base" else -0.002):
                    continue
                dome = max(0.0, (s - S_SIDE) / (1 - S_SIDE))
                swirl = 0.9 * dome                                  # locks wind out of a crown on the top
                if layer == "base":
                    L, W, lift = rnd.uniform(0.020, 0.032), rnd.uniform(0.008, 0.012), rnd.uniform(0.0008, 0.003)
                else:
                    # on the dome the locks are shorter and lie close, so the rim stays round (v5b: no flared crown)
                    L = rnd.uniform(0.060, 0.095) * (0.62 if dome > 0 else 1.0)
                    W, lift = rnd.uniform(0.011, 0.017), rnd.uniform(0.004, 0.011) * (0.4 if dome > 0 else 1.0)
                drop = 0.0
                over = False
                tuck = 0.0 if layer == "base" else lift * (0.6 + 1.6 * dome) + 0.006 * dome   # over the rim: bends down
                if plate_box and abs(th) < half_th + 0.05 and z_p0 - 0.012 < z0 < z_p1 + L:
                    if z0 < z_p1 + 0.004 and under_plate(th, z0, -1):
                        continue                                    # never across the plate's face
                    if z0 >= z_p1 - 0.001:                          # at or above its top edge: falls over it, floating
                        if layer == "base":
                            L = min(L, z0 - z_p1 - 0.003)
                            if L < 0.012:
                                continue
                        else:
                            L = min(L, z0 - z_p1 + rnd.uniform(0.004, 0.024))   # an uneven fringe over the top
                            over = True
                    elif under_plate(th, z0, 6.0):
                        lift = max(lift, 0.011)                     # beside its edge: lifted over it
                        tuck = 0.0
                # the band: at the forehead the fur ends at it, at the sides and back the long hair hangs over it
                back = min(1.0, max(0.0, (abs(th) - 0.9) / 0.9))       # 0 at the front ... 1 from the sides back
                allow = 0.003 + 0.017 * back if layer == "longa" else 0.002
                L = min(L, z0 + allow)
                if s < 0.10:
                    lift *= 0.5                                         # flat at the lower edge, no flare
                    if layer == "longa" and back > 0.3:
                        drop = rnd.uniform(0.003, 0.008) * back
                if L < 0.014:
                    continue
                near = bool(plate_box) and abs(th) < half_th + 0.08 and z0 < z_p1 + 0.08
                lock(th, s, L, W, lift, swirl, drop, short=layer == "base", near_plate=near, over=over, tuck=tuck)
                count[layer] += 1

    place(60, 30, "base")                                   # 4 triangles per lock
    place(56, 31, "longa")                                  # 12 triangles per lock
    finish(bm, f"{tag}_pelo", "pelo", root, keep_normals=True)
    return count


# ---------------------------------------------------------------- the white-metal eagle on the plate
AG_Y0, AG_Y1 = 50.0, 128.0                       # mm above the point of the plate (the number below, grenades at the sides)


def aguia(tag, root):
    """White-metal eagle (📜 "bialy orzel") laid 1.4 mm proud of the brass plate: the outline of the czapka eagle
    (atlas pixels, y down) scaled to the plate, filled like plate() and wrapped on the same curved surface."""
    from mathutils.geometry import delaunay_2d_cdt
    from mathutils import Vector as V2
    bj = json.load(open(AGUIA_JSON))
    loop = bj["loops"][0]
    xs = [p[0] for p in loop]; ys = [p[1] for p in loop]
    kmm = (AG_Y1 - AG_Y0) / (max(ys) - min(ys))
    cx = (max(xs) + min(xs)) / 2
    out = [((x - cx) * kmm, AG_Y1 - (y - min(ys)) * kmm) for x, y in loop]
    ring = []
    for a_, b_ in zip(out, out[1:] + out[:1]):
        n = max(1, int(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) / 3.0))
        ring += [(a_[0] + (b_[0] - a_[0]) * k / n, a_[1] + (b_[1] - a_[1]) * k / n) for k in range(n)]

    def inside(x, y):
        c = False
        for (ax_, ay_), (bx_, by_) in zip(out, out[1:] + out[:1]):
            if (ay_ > y) != (by_ > y) and x < (bx_ - ax_) * (y - ay_) / (by_ - ay_) + ax_:
                c = not c
        return c
    W_ = max(p[0] for p in out) - min(p[0] for p in out)
    pts = list(ring) + [(x, y) for x in np.arange(-W_ / 2 + 3, W_ / 2, 6.0) for y in np.arange(AG_Y0 + 3, AG_Y1, 6.0)
                        if inside(x, y) and min(math.hypot(x - rx, y - ry) for rx, ry in ring) > 2.0]
    nr = len(ring)
    vco, _, fcs, _, _, _ = delaunay_2d_cdt([V2(p) for p in pts], [(i, (i + 1) % nr) for i in range(nr)], [], 0, 1e-6)
    fcs = [f for f in fcs if inside(sum(vco[i].x for i in f) / 3, sum(vco[i].y for i in f) / 3)]
    bm = bmesh.new()

    def P(x, y, off):
        z = PLATE_Z0 + y * 0.001
        s = s_of_z(z)
        rf = float(np.interp(s, L_, PR[:, 0]))
        return S(x * 0.001 / (base_hd * rf), s, off, lumps=False)
    front = [bm.verts.new(P(v.x, v.y, 0.0095)) for v in vco]
    back = [bm.verts.new(P(v.x, v.y, 0.0083)) for v in vco]
    for f in fcs:
        for layer, rev in ((front, False), (back, True)):
            idx = list(f)[::-1] if rev else list(f)
            try:
                bm.faces.new([layer[i] for i in idx])
            except ValueError:
                pass
    by_co = {(round(v.x, 4), round(v.y, 4)): i for i, v in enumerate(vco)}
    ridx = [i for i in (by_co.get((round(x, 4), round(y, 4))) for x, y in ring) if i is not None]
    for a_, b_ in zip(ridx, ridx[1:] + ridx[:1]):
        try:
            bm.faces.new((front[a_], back[a_], back[b_], front[b_]))
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = finish(bm, f"{tag}_aguia_prata", "prata", root, keep_normals=True)
    print(f"AGUIA {tag}: {W_:.0f} x {AG_Y1 - AG_Y0:.0f} mm, {len(ob.data.polygons)} faces")
    return ob


# ---------------------------------------------------------------- variants
def bonnet(tag, x_off, with_plate, plume_cols, with_cords):
    root = bpy.data.objects.new(f"PB_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    shell(tag, root)
    pb = plate(tag, root) if with_plate else None
    if with_plate:
        aguia(tag, root)
    patch = top_patch(tag, root)
    plume_and_cockade(tag, root, plume_cols)
    if with_cords:
        cords(tag, root)
    nl = hair(tag, root, pb, patch, seed=sum(map(ord, tag)))
    print(f"PELO {tag}: {nl['base']} mechas curtas (sub-pelo) + {nl['longa']} longas")
    return root


VARIANTS = [("granadeiro_gala", True, [(0.0, "vermelho")], True),
            ("granadeiro_campanha", True, None, False)]
SPACING = 0.55
roots = [bonnet(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    per = {o.name[len(t) + 1:]: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}
    big = ", ".join(f"{k} {v}" for k, v in sorted(per.items(), key=lambda kv: -kv[1])[:5])
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    zmin = min((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:20s} pecas {len(obs):2d} triangulos {tris:6d} ({big}); z {zmin:.3f}..{zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

# ---------------------------------------------------------------- renders (approximate head)
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
zc = (ROOT @ Vector((0, 0, 0.20))).z


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 900)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_bonnet_varsovia_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_tres_quartos", (mid_x + 1.2, -2.6, zc + 0.5), (mid_x, 0, zc), lens=45, res=(2000, 1000))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
for j, r in enumerate(roots):
    for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
        o.hide_render = j != 0
shot("granadeiro_frente", (0.0, -1.6, zc + 0.05), (0.0, 0.0, zc + 0.05), ortho=0.75, res=(900, 1100))
shot("granadeiro_lado", (-1.6, F["head_cy"], zc + 0.05), (0.0, F["head_cy"], zc + 0.05), ortho=0.75, res=(900, 1100))
shot("granadeiro_costas", (0.5, 1.3, zc + 0.6), (0.0, F["head_cy"], zc + 0.08), lens=55, res=(900, 1000))
shot("granadeiro_perto", (0.30, -0.55, zc + 0.05), (0.0, F["head_cy"] - 0.08, zc - 0.02), lens=55, res=(1000, 1000))
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
