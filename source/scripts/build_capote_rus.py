# Russian army greatcoat 1812 (шинель), from the French greatcoat (build_capote_fr.py, left untouched): the body,
# sleeves, shoulder straps, collar v2, skirt (saia_E over saia_D), trousers, gaiters, shoes, template hands and UVs
# are the validated ones. Sources: dossier docs/research/rus/HIST-RUS-INF-CAPOTE-1812-001.md (V10B, table of 30 Apr 1802
# and orders of 7 Nov 1807, 1 Jan 1812), spec docs/specs/rus_1812.md section 4. Changes:
#   1. front: the 2 x 7 French buttons out; ONE row of 7 flat brass buttons (1802: "fastened with seven flat brass
#      buttons"), on the centre line, 22 mm (7/8", as the coat, C2) under the collar foot down to the waist; the
#      edge of the overlapping front is the closure step of the base mesh, ~25 mm from the buttons (single-breasted)
#   2. cuffs: "round grey cuffs" (1802): the cuff flaps and their buttons out
#   3. collar: "the same colour and pattern as on the coat" (1802) and red (7 Nov 1807): lowered to GOLA_FRENTE like
#      the coat (build_uniforme_rus.py section 3, same method), painted red
#   4. back: a button at the top of each rear flap ("the top button of the rear flaps", 1802), where the skirt
#      halves meet at the back; the rest of the rear flaps is not described (no more buttons modelled)
#   5. knee-high gaiters (1 Jan 1812): only painted, as on the coat (ob["hcl_polaina_topo"]); the trousers' bunching
#      over the short gaiter is taken back and the leg made flush with it (build_uniforme_rus.py section 4b)
#   blender -b --factory-startup --python build_capote_rus.py -- <fr greatcoat .blend> <out .blend>
#           [gola=0.070] [polaina=0.52] [nome=HCL_U_RUS1812_Capote_LOD0]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
GOLA_FRENTE = float(OPT.get("gola", 0.070))
POLAINA_TOPO = float(OPT.get("polaina", 0.52))
NOME = OPT.get("nome", "HCL_U_RUS1812_Capote_LOD0")
FIRST, FLAT, OFF = 0.022, 0.6, 0.0008
WAIST = 1.12                                           # last button: the waist (1802: "under the swordbelt")
GROUND = -1.0069
Z = lambda h: GROUND + h
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Fr1812_Capote_LOD0"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
ob.name = NOME
ob.data = ob.data.copy(); ob.data.name = NOME
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
uvl = bm.loops.layers.uv.active
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


def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- 1-2. out: French front buttons, cuff flaps + buttons
front, cuff_btn = [], []
pala_v = [v for v in bm.verts if vparts().get(v, set()) & {PID["pala_E"], PID["pala_D"]}]
pala_bvh = tri_bvh({PID["pala_E"], PID["pala_D"]})
for comp in components(PID["botoes"]):
    c = sum((v.co for v in comp), Vector()) / len(comp)
    near = pala_bvh.find_nearest(c)
    if abs(c.x) < 0.12 and c.y < -0.04 and Z(1.10) < c.z < Z(1.56):
        front.append((c, comp))
    elif near[3] is not None and near[3] < 0.012:
        cuff_btn.append(comp)
assert len(front) == 14, f"frente francesa: {len(front)} botoes (esperados 14)"
tc, tcomp = min(front, key=lambda t: abs(t[0].z - Z(1.33)))
tmpl_faces = {f for v in tcomp for f in v.link_faces}
tmpl_data = [([tcomp.index(x) for x in f.verts], [l[uvl].uv.copy() for l in f.loops], f.material_index) for f in tmpl_faces]
tmpl_co = [v.co.copy() for v in tcomp]
gone = {v for _, comp in front for v in comp} | {v for comp in cuff_btn for v in comp} | set(pala_v)
bmesh.ops.delete(bm, geom=list(gone), context="VERTS")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
print(f"FORA: 14 botoes da frente francesa, {len(cuff_btn)} botoes e as 2 palas dos punhos (punho redondo, 1802)")

# ---------------------------------------------------------------- 1. front: 7 flat buttons on the centre line
COAT = tri_bvh({PID["casaco_corpo"]})
loc0, n0, _, _ = COAT.find_nearest(tc)
n0 = n0 if n0.y < 0 else -n0
base_h = min((co - loc0).dot(n0) for co in tmpl_co)
tmpl_co = [co - n0 * ((co - loc0).dot(n0) - base_h) * (1 - FLAT) for co in tmpl_co]


def place_button(p, n):
    R = n0.rotation_difference(n).to_matrix()
    nv = [bm.verts.new(p + n * OFF + R @ (co - loc0)) for co in tmpl_co]
    for idxs, uvs, mi in tmpl_data:
        f = bm.faces.new([nv[i] for i in idxs])
        f[PL] = PID["botoes"]; f.material_index = mi
        for l, uv in zip(f.loops, uvs):
            l[uvl].uv = uv


vp = vparts()
gola_foot = min(v.co.z for v in bm.verts if PID["gola"] in vp.get(v, ()) and v.co.y < 0.0 and abs(v.co.x) < 0.02)
top = gola_foot - FIRST
pitch = (top - Z(WAIST)) / 6
btn_list = []
OUTER = tri_bvh({PID["casaco_corpo"], PID["saia_E"], PID["saia_D"]})   # the lowest button sits on the skirt top
for i in range(7):
    z = top - pitch * i
    hit = OUTER.ray_cast(Vector((0.0, -0.6, z)), Vector((0, 1, 0)), 1.0)
    assert hit[0] is not None, f"capote nao encontrado em h {z - GROUND:.3f}"
    n = hit[1] if hit[1].y < 0 else -hit[1]
    place_button(hit[0], n.normalized())
    btn_list.append([round(hit[0].x, 5), round(hit[0].y, 5), round(hit[0].z, 5), 0])
print(f"FRENTE: 7 botoes chatos (x{FLAT}) no centro, h {top - GROUND:.3f}..{z - GROUND:.3f}, passo {pitch * 1000:.0f} mm "
      f"(pe da gola {gola_foot - GROUND:.3f})")

# ---------------------------------------------------------------- 4. back: top button of each rear flap
SKIRT = tri_bvh({PID["saia_E"], PID["saia_D"]})
back_btn = []
for sx in (0.045, -0.045):
    z = Z(1.115)
    hit = SKIRT.ray_cast(Vector((sx, 0.6, z)), Vector((0, -1, 0)), 1.0)
    if hit[0] is None:
        continue
    n = hit[1] if hit[1].y > 0 else -hit[1]
    place_button(hit[0], n.normalized())
    back_btn.append((round(hit[0].x, 3), round(z - GROUND, 3)))
print(f"COSTAS: botao do alto de cada aba de tras (x, h): {back_btn}")

# ---------------------------------------------------------------- 3. collar: lower, sliding down its own wall
O1 = Vector((0.0, 0.050, 0.0))
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
tab = {}
for b, vs in bins.items():
    zz = [v.co.z for v in vs]
    zb, zt = min(zz), max(zz)
    if zt - zb < 0.02:
        continue
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
for v in GV:
    th = theta(v.co)
    zb, zt, rb, rt = (interp(th, i) for i in range(4))
    f = max(0.0, min(1.0, (v.co.z - zb) / max(1e-6, zt - zb)))
    d = Vector((v.co.x - O1.x, v.co.y - O1.y, 0.0))
    d = d.normalized() if d.length > 1e-6 else Vector((0, -1, 0))
    v.co = v.co + Vector((0, 0, -f * (1 - s) * (zt - zb))) + d * (-f * (1 - s) * (rt - rb))
print(f"GOLA: frente {h_front * 1000:.0f} -> {h_front * s * 1000:.0f} mm (fator {s:.3f}), como a casaca (C4)")

# ---------------------------------------------------------------- 5. knee-high gaiters (build_uniforme_rus.py 4b)
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
        if d.length > 1e-6:
            v.co = v.co - d.normalized() * bump
            unb += 1
H_REF, H_LO, H_FULL, H_END = 0.415, 0.424, 0.445, 0.53
flush = 0
for s_ in "ED":
    LV = [v for v in bm.verts if PID[f"calca_perna_{s_}"] in vp.get(v, ())]
    GAIT = tri_bvh({PID[f"polaina_{s_}"]})
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
        if r < rg < r + 0.015:
            v.co = v.co + d * (rg - r) * (1.0 - sstep(H_FULL, H_END, h))
            flush += 1
print(f"POLAINAS ATE O JOELHO: franzido desfeito em {unb} vertices, perna rente a polaina em {flush}")

bm.normal_update()
bm.to_mesh(ob.data)
ob.data.update()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_botoes_frente"] = json.dumps({"estilo": "simples_7", "botoes": btn_list})
ob["hcl_polaina_topo"] = POLAINA_TOPO
ob["hcl_origem"] = (f"derivado de HCL_U_Fr1812_Capote_LOD0 por build_capote_rus.py gola={GOLA_FRENTE} "
                    f"polaina={POLAINA_TOPO}, 2026-10-18")
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print(f"CAPOTE RUS: {len(ob.data.vertices)} vertices, {tris} triangulos")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
