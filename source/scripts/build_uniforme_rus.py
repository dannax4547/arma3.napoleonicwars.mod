# Russian army infantry coat 1812 (double-breasted, closed low collar), derived from the validated Prussian 1813 uniform
# production mesh like the French and British coats (build_uniforme_uk.py, copied here and left untouched): same body,
# sleeves, cuffs with flaps (3 buttons, RU5 pending the atlas), shoulder straps, trousers, gaiters, shoes, template hands
# and the collar v2 fitted to the GAME head. Spec: docs/specs/rus_1812.md sections 2.1, 2.2, 5, 8 (RU4, RU8). Changes:
#   1. tails: hem from 0.70 m to TAIL_HEM. The 1802 table gives 15 3/4" (400 mm) from the waist to the tail ends for a
#      6 ft man (V10B); the tails start at 1.14 m, so the hem goes to 0.74 m. Re-draped over the trousers with the
#      British code (same function, unchanged)
#   2. front (v2, 2026-10-17, research dossier docs/research/rus/HIST-RUS-INF-COAT-1812-001.md, decisions C1-C3): the 14
#      Prussian front buttons are removed and 6 + 6 FLATTER buttons placed (1802 table: "flat"): two parallel rows
#      ROW_GAP (36 mm) apart centre to centre (Hermitage coat 1812-1817 ~37 mm, 1802 table 3" turnover - 2 x 7/8" =
#      32 mm; Viskovatov plate 1359 shows them far apart but is a stylised engraving, rejected), first pair 22 mm (7/8")
#      under the collar foot, pitch PITCH (64 mm: 2 5/8" x 0.96 to end at the waist like the Hermitage coat). Their
#      centres go in ob["hcl_botoes_frente"] for the painter
#   2a. edge of the double-breasted front (Phase 4, 2026-10-18, dossier C11): the Prussian closure step, which lay
#      between the two rows, slides to 22 mm (7/8") outside the wearer's right row (section 1b below)
#   2b. tails: one button per tail where the turnbacks join (1802 table, C6), near the tail end on the back face
#   3. collar: low and closed from 1 Jan 1812 (V10B), no measure in the source; Hermitage coat 1812-1817 ~75 mm: the
#      collar v2 (77 mm at the front, 59 mm at the back) goes to GOLA_FRENTE (70 mm, C4), the same fraction all round. Every collar vertex
#      slides DOWN ITS OWN WALL: at its angle about the v1 axis, its height fraction f between the collar base and top
#      becomes f * s, and it moves by the change of height and of radius of the wall between those fractions (the
#      v2 wall was fitted around the game neck, so the lower top stays on it). Base, thickness and roll are kept.
#      The neck clearance must be re-measured with the game head (diag_gola_bust.py, needs the Arma 3 Samples)
#   4. knee-high gaiters (1 Jan 1812, V10B): only painted; ob["hcl_polaina_topo"] tells the painter where they end
#   No new topology: every UV is kept, so the painter's maps stay valid.
#   blender -b --factory-startup --python build_uniforme_rus.py -- <prussian LOD0 .blend> <out .blend> [hem=0.74]
#                                                         [gola=0.070] [polaina=0.52] [nome=HCL_U_RUS1812_Linha_LOD0]
#                                                         [corpo=<ref_corpo_arma3_samples.blend>]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
TAIL_HEM = float(OPT.get("hem", 0.74))
GOLA_FRENTE = float(OPT.get("gola", 0.070))
ROW_GAP = float(OPT.get("fileiras", 0.036))             # C1: centre to centre
PITCH = float(OPT.get("passo", 0.064))                 # C2
FIRST = 0.022                                          # C2: 7/8" under the collar foot
FLAT = 0.6                                             # C3: button height x 0.6 ("flat", 1802)
POLAINA_TOPO = float(OPT.get("polaina", 0.52))
NOME = OPT.get("nome", "HCL_U_RUS1812_Linha_LOD0")
CORPO = os.path.abspath(OPT.get("corpo", os.path.join(os.path.dirname(SRC), "ref_corpo_arma3_samples.blend")))
GROUND = -1.0069
Z = lambda h: GROUND + h
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
ob.name = NOME
ob.data = ob.data.copy(); ob.data.name = NOME
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()


def vparts():
    vp = {}
    for f in bm.faces:
        for v in f.verts:
            vp.setdefault(v, set()).add(f[PL])
    return vp


def components(pid):
    vp = vparts()
    seen, comps = set(), []
    for v in bm.verts:
        if v in seen or pid not in vp.get(v, ()):
            continue
        comp, st = [], [v]
        seen.add(v)
        while st:
            x = st.pop(); comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y not in seen and pid in vp.get(y, ()):
                    seen.add(y); st.append(y)
        comps.append(comp)
    return comps


def tri_bvh(pids):
    vs = list(bm.verts)
    idx = {v: i for i, v in enumerate(vs)}
    tris = []
    for f in bm.faces:
        if f[PL] in pids:
            q = [idx[v] for v in f.verts]
            for t in range(1, len(q) - 1):
                tris.append([q[0], q[t], q[t + 1]])
    return BVHTree.FromPolygons([v.co.copy() for v in vs], tris)


# ---------------------------------------------------------------- 1. tails (build_uniforme_uk.py, unchanged method)
TOP = 1.14
k = (TOP - TAIL_HEM) / (TOP - 0.70)
AX = Vector((0.0, 0.02, 0.0))
vp = vparts()
tail_v = [v for v in bm.verts if vp.get(v, set()) & {PID["aba_E"], PID["aba_D"]}]
TR = tri_bvh({PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]})


def trousers_r(phi, z):
    d = Vector((math.sin(phi), math.cos(phi), 0.0))            # phi = 0: back (+Y), +90 deg: +X
    o = Vector((AX.x, AX.y, z)) + d * 0.6
    hit = TR.ray_cast(o, -d, 0.6)
    return None if hit[0] is None else (hit[0] - Vector((AX.x, AX.y, z))).to_2d().length


new_co, kept, offs = {}, 0, []
for v in tail_v:
    if v.co.z >= Z(TOP):
        continue
    q = (v.co - AX).to_2d()
    phi = math.atan2(q.x, q.y)
    r0 = trousers_r(phi, v.co.z)
    z1 = Z(TOP) - (Z(TOP) - v.co.z) * k
    r1 = trousers_r(phi, z1)
    if r0 is None or r1 is None:
        new_co[v] = Vector((v.co.x, v.co.y, z1))
        kept += 1
        continue
    d = q.length - r0
    offs.append(d)
    rr = r1 + min(max(d, 0.004), 0.025)
    new_co[v] = Vector((AX.x + math.sin(phi) * rr, AX.y + math.cos(phi) * rr, z1))
disp = {v: new_co[v] - v.co for v in new_co}
for _ in range(4):
    nd = {}
    for v, d_ in disp.items():
        nb = [disp[e.other_vert(v)] for e in v.link_edges if e.other_vert(v) in disp]
        nd[v] = d_ * 0.5 + (sum(nb, Vector()) / len(nb)) * 0.5 if nb else d_
    disp = nd
for v, d_ in disp.items():
    v.co = v.co + d_
btn_moved = 0
for comp in components(PID["botoes"]):
    c = sum((v.co for v in comp), Vector()) / len(comp)
    if Z(0.60) < c.z < Z(TOP) and abs(c.x) < 0.30:
        dz = (Z(TOP) - (Z(TOP) - c.z) * k) - c.z
        for v in comp:
            v.co.z += dz
        btn_moved += 1
hem = min(v.co.z for v in tail_v) - GROUND
offs.sort()
print(f"ABAS: barra {hem:.3f} m (era 0.700); fator {k:.3f}; afastamento da calca preservado em {len(offs)} vertices "
      f"(min {offs[0] * 1000:.1f} mm, mediana {offs[len(offs) // 2] * 1000:.1f} mm; minimo imposto 4 mm); "
      f"{kept} sem calca na direcao (so a altura muda); {btn_moved} botoes das abas movidos")

# ---------------------------------------------------------------- 2. front: 6 + 6 flat buttons (dossier C1-C3)
uvl = bm.loops.layers.uv.active
front = []
for comp in components(PID["botoes"]):
    c = sum((v.co for v in comp), Vector()) / len(comp)
    if abs(c.x) < 0.03 and c.y < -0.05 and Z(1.15) < c.z < Z(1.50):
        front.append((c, comp))
assert len(front) == 14, f"frente prussiana: {len(front)} botoes (esperados 14)"
tc, tcomp = min(front, key=lambda t: abs(t[0].z - Z(1.335)) + (0 if t[0].x > 0 else 1))   # template: a mid button
tmpl_faces = {f for v in tcomp for f in v.link_faces}
tmpl_data = [([tcomp.index(x) for x in f.verts], [l[uvl].uv.copy() for l in f.loops], f.material_index) for f in tmpl_faces]
tmpl_co = [v.co.copy() for v in tcomp]
bmesh.ops.delete(bm, geom=list({v for _, comp in front for v in comp}), context="VERTS")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()

# ---------------------------------------------------------------- 1b. edge of the double-breasted front (dossier C11)
# The Prussian mesh has its single-breasted closure step (the button stand 1.8 mm over the other front) at THC = -0.18
# rad about AXC, x = -0.025 at the chest: BETWEEN the two Russian rows, where it reads as a single-breasted closing.
# On the double-breasted coat the edge of the overlapping front lies outside the row, 7/8" (22 mm) from the button
# centres (1802 table, R1: buttonholes 7/8" from the edge of the 3" turnover). Same side as the Prussian step (wearer's
# right, -x). The coat vertices slide around the axis with one monotonic angle map (no new topology, UVs kept): the
# step moves to the target angle, the ease of each vertex (raised or not) goes with it, and the radius follows the
# official body (reference mesh already in the project) so the cloth stays on the same surface. The ring where the
# coat meets the collar foot does not move (the change fades in the last 14 mm under the collar).
AXC = Vector((0.0, 0.015, 0.0))
THC0 = -0.18
EDGE_X = -(ROW_GAP / 2 + 0.022)
with bpy.data.libraries.load(CORPO, link=False) as (src_b, dst_b):
    dst_b.objects = ["REF_A3_character_example_LOD0"]
bo = dst_b.objects[0]
gn = {g.index: g.name.lower() for g in bo.vertex_groups}
prox = {v.index for v in bo.data.vertices if any(gn[g.group].startswith(("proxy", "-")) for g in v.groups if g.weight > 0)}
BODY = BVHTree.FromPolygons([bo.matrix_world @ v.co for v in bo.data.vertices],
                            [list(p.vertices) for p in bo.data.polygons if not prox & set(p.vertices)])


def th_of(p):
    return math.atan2(p.x - AXC.x, -(p.y - AXC.y))


def body_r(th, z):
    d = Vector((math.sin(th), -math.cos(th), 0.0))
    o = Vector((AXC.x, AXC.y, z))
    hit = BODY.ray_cast(o, d, 0.5)
    return None if hit[0] is None else (hit[0] - o).to_2d().length


def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


vp = vparts()
CV_ = [v for v in bm.verts if PID["casaco_corpo"] in vp.get(v, ())]
chest = [v for v in CV_ if abs(th_of(v.co) - THC0) < 0.03 and Z(1.20) < v.co.z < Z(1.45)]
r_chest = sum(-(v.co.y - AXC.y) for v in chest) / len(chest)
THC1 = math.atan2(EDGE_X, r_chest)
DTH = THC1 - THC0
TH_L, TH_R = -0.393, 0.196                             # the neighbouring Prussian columns (2 pi k / 32) stay put


def wmap(th):
    return sstep(TH_L, THC0, th) if th < THC0 else 1.0 - sstep(THC0, TH_R, th)


collar_foot = {}
for v in (v for v in bm.verts if PID["gola"] in vp.get(v, ())):
    b = int(math.floor(th_of(v.co) / 0.05))
    collar_foot[b] = min(collar_foot.get(b, 9.0), v.co.z)
moved_e, dr_max = 0, 0.0
for v in CV_:
    th = th_of(v.co)
    if v.co.y > 0.02 or not (TH_L < th < TH_R):
        continue
    zf = min(collar_foot.get(int(math.floor(th / 0.05)) + d, 9.0) for d in (-1, 0, 1))
    wz = max(0.0, min(1.0, (zf - 0.004 - v.co.z) / 0.010))
    th1 = th + DTH * wmap(th) * wz
    if abs(th1 - th) < 1e-7:
        continue
    q = v.co - AXC
    r = q.to_2d().length
    rb0, rb1 = body_r(th, v.co.z), body_r(th1, v.co.z)
    dr = (rb1 - rb0) if (rb0 is not None and rb1 is not None) else 0.0
    dr_max = max(dr_max, abs(dr))
    r += dr
    v.co = Vector((AXC.x + math.sin(th1) * r, AXC.y - math.cos(th1) * r, v.co.z))
    moved_e += 1
print(f"FRENTE DUPLA: borda da frente de x {r_chest * math.tan(THC0):+.3f} para {EDGE_X:+.3f} m (theta {THC0:.3f} -> "
      f"{THC1:.3f} rad; 22 mm fora da fileira); {moved_e} vertices deslizados; correcao de raio pelo corpo ate "
      f"{dr_max * 1000:.1f} mm")
COAT = tri_bvh({PID["casaco_corpo"]})
loc0, n0, _, _ = COAT.find_nearest(tc)
n0 = n0 if n0.y < 0 else -n0
# flatten the template along its own normal (C3) about its base on the cloth
base_h = min((co - loc0).dot(n0) for co in tmpl_co)
tmpl_co = [co - n0 * ((co - loc0).dot(n0) - base_h) * (1 - FLAT) for co in tmpl_co]
OFF = 0.0008


def place_button(p, n):
    R = n0.rotation_difference(n).to_matrix()
    nv = [bm.verts.new(p + n * OFF + R @ (co - loc0)) for co in tmpl_co]
    for idxs, uvs, mi in tmpl_data:
        f = bm.faces.new([nv[i] for i in idxs])
        f[PL] = PID["botoes"]; f.material_index = mi
        for l, uv in zip(f.loops, uvs):
            l[uvl].uv = uv


_vp = vparts()
gola_foot = min(v.co.z for v in bm.verts if PID["gola"] in _vp.get(v, ()) and v.co.y < 0.0 and abs(v.co.x) < 0.02)
btn_list = []
for i in range(6):
    z = gola_foot - FIRST - PITCH * i
    for side in (1, -1):
        x = side * ROW_GAP / 2
        hit = COAT.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 1.0)
        assert hit[0] is not None, f"casaco nao encontrado em x {x:.3f} h {z - GROUND:.3f}"
        n = hit[1] if hit[1].y < 0 else -hit[1]
        place_button(hit[0], n.normalized())
        btn_list.append([round(hit[0].x, 5), round(hit[0].y, 5), round(hit[0].z, 5), side])
zs_ = [b[2] for b in btn_list]
print(f"FRENTE: 14 botoes prussianos trocados por 12 (achatados x{FLAT}); fileiras a {ROW_GAP * 1000:.0f} mm; "
      f"passo {PITCH * 1000:.0f} mm; h {min(zs_) - GROUND:.3f}..{max(zs_) - GROUND:.3f} (pe da gola {gola_foot - GROUND:.3f}; "
      f"barra da frente {min(v.co.z for v in bm.verts if PID['casaco_corpo'] in _vp.get(v, ())) - GROUND:.3f})")

# ---------------------------------------------------------------- 2b. tails: a button where the turnbacks join (C6)
TAILS = tri_bvh({PID["aba_E"], PID["aba_D"]})
tail_btn = []
for pid, sgn in ((PID["aba_E"], 1), (PID["aba_D"], -1)):
    tv = [v for v in bm.verts if pid in _vp.get(v, ())]
    zmin = min(v.co.z for v in tv)
    low = [v for v in tv if v.co.z < zmin + 0.04]
    x = sum(v.co.x for v in low) / len(low)
    z = zmin + 0.030
    hit = TAILS.ray_cast(Vector((x, 0.6, z)), Vector((0, -1, 0)), 1.0)
    assert hit[0] is not None, f"aba nao encontrada em x {x:.3f} h {z - GROUND:.3f}"
    n = hit[1] if hit[1].y > 0 else -hit[1]
    place_button(hit[0], n.normalized())
    tail_btn.append((round(hit[0].x, 3), round(z - GROUND, 3)))
print(f"ABAS: botao das viradas em cada aba (x, h): {tail_btn}")

# ---------------------------------------------------------------- 3. collar: lower, sliding down its own wall
O1 = Vector((0.0, 0.050, 0.0))                          # v1 collar axis (ajustar_gola_v2.py keeps theta about it)
vp = vparts()
GV = [v for v in bm.verts if PID["gola"] in vp.get(v, ())]


def theta(p):
    return math.degrees(math.atan2(p.x - O1.x, -(p.y - O1.y)))


def rad(p):
    return math.hypot(p.x - O1.x, p.y - O1.y)


BIN = 15.0
bins = {}
for v in GV:
    bins.setdefault(int(math.floor((theta(v.co) + 180.0) / BIN)), []).append(v)
tab = {}                                               # bin centre (deg) -> zb, zt, rb, rt
for b, vs in bins.items():
    zz = [v.co.z for v in vs]
    zb, zt = min(zz), max(zz)
    if zt - zb < 0.02:
        continue                                       # a bin with only the top or the base: interpolated
    lo = [rad(v.co) for v in vs if v.co.z < zb + 0.008]
    hi = [rad(v.co) for v in vs if v.co.z > zt - 0.008]
    tab[b * BIN - 180.0 + BIN / 2] = (zb, zt, sum(lo) / len(lo), sum(hi) / len(hi))
ks = sorted(tab)


def interp(th, i):
    xs = np.array(ks + [ks[0] + 360.0])
    ys = np.array([tab[x][i] for x in ks] + [tab[ks[0]][i]])
    t = (th - ks[0]) % 360.0 + ks[0]
    return float(np.interp(t, xs, ys))


h_front = interp(0.0, 1) - interp(0.0, 0)
s = min(1.0, GOLA_FRENTE / h_front)
moved = 0
for v in GV:
    th = theta(v.co)
    zb, zt, rb, rt = (interp(th, i) for i in range(4))
    f = max(0.0, min(1.0, (v.co.z - zb) / max(1e-6, zt - zb)))
    dz = -f * (1 - s) * (zt - zb)
    dr = -f * (1 - s) * (rt - rb)
    d = Vector((v.co.x - O1.x, v.co.y - O1.y, 0.0))
    d = d.normalized() if d.length > 1e-6 else Vector((0, -1, 0))
    v.co = v.co + Vector((0, 0, dz)) + d * dr
    moved += f > 0
gz = [v.co.z for v in GV]
print(f"GOLA: {len(tab)} faixas de {BIN:.0f} graus; frente {h_front * 1000:.0f} -> {h_front * s * 1000:.0f} mm, "
      f"tras {(interp(180.0, 1) - interp(180.0, 0)) * 1000:.0f} -> {(interp(180.0, 1) - interp(180.0, 0)) * s * 1000:.0f} mm "
      f"(fator {s:.3f}); {moved} vertices movidos; topo agora h {max(gz) - GROUND:.3f} (era {max(interp(t, 1) for t in ks) - GROUND:.3f})")

# ---------------------------------------------------------------- 4b. knee-high gaiters: no bunching (dossier C12)
# The Prussian legs bunch 7.5 mm over the top of the short gaiter (build_uniforme_production.py: +0.0075 between
# h 0.415 and 0.50). Under the knee-high gaiter of 1812 that cloth is the gaiter itself (painted, C12), so the bump is
# taken back, radially from the centre of each leg ring.
vp = vparts()
unb = 0
for s_ in "ED":
    LV = [v for v in bm.verts if PID[f"calca_perna_{s_}"] in vp.get(v, ())]
    for v in LV:
        h = v.co.z - GROUND
        bump = 0.0075 * sstep(0.415, 0.43, h) * (1 - sstep(0.47, 0.50, h))
        if bump <= 0:
            continue
        ring = [u.co for u in LV if abs(u.co.z - v.co.z) < 0.004]
        c = sum(ring, Vector()) / len(ring)
        d = Vector((v.co.x - c.x, v.co.y - c.y, 0.0))
        if d.length < 1e-6:
            continue
        v.co = v.co - d.normalized() * bump
        unb += 1
print(f"POLAINAS ATE O JOELHO: franzido da calca sobre a polaina curta desfeito em {unb} vertices (ate 7.5 mm)")
# ... and the leg just above the modelled gaiter (top hem at h 0.43) comes out flush with the gaiter's outer surface,
# covering that hem, then tapers back to the leg by h 0.53: one continuous gaiter up to the knee instead of a ledge.
H_REF, H_LO, H_FULL, H_END = 0.415, 0.424, 0.445, 0.53       # gaiter top at h 0.423; leg rings 0.425, 0.44, ...
flush, gmax = 0, 0.0
for s_ in "ED":
    LV = [v for v in bm.verts if PID[f"calca_perna_{s_}"] in vp.get(v, ())]
    GAIT = tri_bvh({PID[f"polaina_{s_}"]})             # this leg's gaiter only (a long ray reaches the other leg)
    ref = [u.co for u in LV if abs(u.co.z - Z(0.43)) < 0.006] or [u.co for u in LV]
    c0 = sum(ref, Vector()) / len(ref)
    for v in LV:
        h = v.co.z - GROUND
        if not (H_LO <= h < H_END):
            continue
        d = Vector((v.co.x - c0.x, v.co.y - c0.y, 0.0))
        if d.length < 1e-6:
            continue
        d.normalize()
        o = Vector((c0.x, c0.y, Z(H_REF))) + d * 0.12
        hit = GAIT.ray_cast(o, -d, 0.12)
        if hit[0] is None:
            continue
        rg = (hit[0] - Vector((c0.x, c0.y, Z(H_REF)))).to_2d().length + 0.0008
        r = Vector((v.co.x - c0.x, v.co.y - c0.y)).length
        w = 1.0 - sstep(H_FULL, H_END, h)
        if r < rg < r + 0.015:
            v.co = v.co + d * (rg - r) * w
            gmax = max(gmax, (rg - r) * w)
            flush += 1
print(f"POLAINAS ATE O JOELHO: perna rente a polaina modelada em {flush} vertices (ate {gmax * 1000:.1f} mm), "
      f"de h {H_LO} ate {H_END}")

bm.normal_update()
bm.to_mesh(ob.data)
ob.data.update()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_botoes_frente"] = json.dumps({"estilo": "duplo_6x2", "botoes": btn_list})
ob["hcl_polaina_topo"] = POLAINA_TOPO
ob["hcl_fecho_theta"] = THC1                            # edge of the overlapping front, angle about (0, 0.015)
ob["hcl_origem"] = (f"derivado de HCL_U_Pruss1813_01_LOD0 (gola v2) por build_uniforme_rus.py hem={TAIL_HEM} "
                    f"gola={GOLA_FRENTE}, 2026-10-17")
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print(f"UNIFORME RUS: {len(ob.data.vertices)} vertices, {tris} triangulos (Res 1; o prussiano tem 11960 + gola)")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
