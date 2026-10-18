# Highland dress (92nd Gordon Highlanders and a second, unidentified tartan; spec docs/specs/uk_1812.md section 3.3):
# the British line jacket 1812 (build_uniforme_uk.py) with a pleated KILT from the waist to the knee, worn UNDER the
# jacket's tails and under the crossbelts' cartridge box and bayonet. Built with the skirt technique of the French
# greatcoat (build_capote_fr.py, copied, left untouched):
#   - per height ring: convex hull of the trousers + a clearance growing to the hem; never narrower than the ring above
#   - the back and sides are PLEATED (box pleats: a ripple of the radius, 26 mm pleats), the front apron is flat; the
#     kilt wraps left over right at the front (apron over apron), like the greatcoat skirt halves
#   - tucked in: wherever the jacket (body above its lower edge, tails) or the equipment comes within 2.5 mm, the kilt
#     is pulled in under it (never closer than 3 mm to the trousers)
#   - outer cloth + lining 2 mm inside + edge strips; parts "saia_E" / "saia_D" (teste_movimentos.py gives them the
#     weights of the body under them, like the greatcoat skirt)
#   - the trousers stay under the kilt (the legs are the trousers mesh): the painter colours the knee as skin and the
#     calves as diced hose (generate_uniform_textures_uk.py, keys "kilt_*", "meia_*", "pele")
#   - UV: every island except the template hands and the buttons' corner square is packed again into u, v < 0.94
#   blender -b --factory-startup --python build_kilt_uk.py -- <UK line jacket LOD0 .blend> <fr equipment .blend> <out .blend>
#           [hem=0.50] [top=1.135] [nome=HCL_U_UK1812_Kilt_LOD0]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, EQ, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
HEM, TOP = float(OPT.get("hem", 0.50)), float(OPT.get("top", 1.135))
NOME = OPT.get("nome", "HCL_U_UK1812_Kilt_LOD0")
GROUND = -1.0069
Z = lambda h: GROUND + h
AX = Vector((0.0, 0.02, 0.0))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_UK1812_Linha_LOD0"]
ob = dst.objects[0]
sc.collection.objects.link(ob)
ob.name = NOME
ob.data = ob.data.copy(); ob.data.name = NOME
with bpy.data.libraries.load(EQ, link=False) as (src, dst):
    dst.objects = ["HCL_V_Fr1812_Correame_LOD0", "HCL_B_Fr1812_Havresac_LOD0"]
equip = list(dst.objects)
parts = ob["hcl_partes"].split(",")
parts += ["saia_E", "saia_D"]
PID = {n: i for i, n in enumerate(parts)}
MAT = {m.name: i for i, m in enumerate(ob.data.materials)}
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


def hull2d(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) < 3:
        return pts
    cross = lambda o, a_, b_: (a_[0] - o[0]) * (b_[1] - o[1]) - (a_[1] - o[1]) * (b_[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


d2 = lambda th: np.array([math.sin(th), -math.cos(th)])               # 0 = front (-Y), +90 deg = wearer's left (+X)


def hull_radius(hull, th):
    d = d2(th)
    best = 0.0
    for p, q in zip(hull, hull[1:] + hull[:1]):
        p = np.array(p) - AX.to_2d()[:]; q = np.array(q) - AX.to_2d()[:]
        e = q - p
        den = d[0] * (-e[1]) - d[1] * (-e[0])
        if abs(den) < 1e-12:
            continue
        t = (p[0] * (-e[1]) - p[1] * (-e[0])) / den
        s = (d[0] * p[1] - d[1] * p[0]) / den
        if t > 0 and -1e-9 <= s <= 1 + 1e-9:
            best = max(best, t)
    return best


# ---------------------------------------------------------------- 1. ring radii: trousers hull + clearance, pleats
vp = vparts()
TP = np.array([v.co[:] for v in bm.verts if vp.get(v, set()) & {PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]}])
TRB = tri_bvh({PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]})
JACKET = tri_bvh({PID["casaco_corpo"], PID["aba_E"], PID["aba_D"]})
ebm = bmesh.new()
for e in equip:
    tmp = bmesh.new(); tmp.from_mesh(e.data); tmp.transform(e.matrix_world)
    m_ = bpy.data.meshes.new("tmp"); tmp.to_mesh(m_); tmp.free()
    ebm.from_mesh(m_); bpy.data.meshes.remove(m_)
EQB = BVHTree.FromBMesh(ebm)
NTH = 360
THS = np.linspace(-math.pi, math.pi, NTH, endpoint=False)
NR = 12
HS = np.linspace(TOP, HEM, NR)
PLEAT = 0.026                                                         # pleat width along the cloth (box pleats)
APRON = math.radians(52)                                              # flat front apron half-width
R = np.zeros((NR, NTH)); RB = np.zeros((NR, NTH))
for j, h in enumerate(HS):
    sl = TP[np.abs(TP[:, 2] - Z(h)) < 0.02][:, :2]
    hull = hull2d(sl)
    t = (TOP - h) / (TOP - HEM)
    clear = 0.006 + 0.022 * t ** 1.3                                  # a kilt hangs close at the hips, flares to the knee
    for i, th in enumerate(THS):
        RB[j, i] = hull_radius(hull, th)
        R[j, i] = RB[j, i] + clear
    if j:
        R[j] = np.maximum(R[j], R[j - 1] - 0.002)
    ring = np.array([AX.to_2d()[:] + d2(th) * r for th, r in zip(THS, R[j])])
    hr = hull2d(ring)
    R[j] = [hull_radius(hr, th) for th in THS]
# pleats: radius ripple on the back and sides (|th| > APRON), growing from the waist band (sewn flat) to the hem
pleat_amp = np.zeros_like(R)
for j, h in enumerate(HS):
    t = (TOP - h) / (TOP - HEM)
    grow = min(1.0, max(0.0, (t - 0.12) / 0.25))
    arc = THS * R[j].mean()
    side = np.clip((np.abs(THS) - APRON) / math.radians(10), 0, 1)
    pleat_amp[j] = 0.0035 * grow * side * (0.5 - 0.5 * np.cos(2 * math.pi * arc / PLEAT))
R = R + pleat_amp
# tuck under the jacket (body / tails) and the equipment: ray outward from the trousers surface
cut = np.zeros_like(R)
for j, h in enumerate(HS):
    for i, th in enumerate(THS):
        d = d2(th)
        o = Vector((AX.x, AX.y, Z(h)))
        start = max(RB[j, i] + 0.0015, 0.02)
        for bvh, gap in ((JACKET, 0.0040), (EQB, 0.0035)):
            hit = bvh.ray_cast(o + Vector((d[0], d[1], 0)) * start, Vector((d[0], d[1], 0)), 0.5)
            if hit[0] is not None:
                lim = max(RB[j, i] + 0.003, start + hit[3] - gap)
                if R[j, i] > lim:
                    cut[j, i] = max(cut[j, i], R[j, i] - lim)
spread = cut.copy()
for j in range(NR):
    for di in range(-8, 9):
        for dj in (-1, 0, 1):
            jj = j + dj
            if 0 <= jj < NR:
                spread[j] = np.maximum(spread[j], np.roll(cut[jj], di) * (1 - abs(di) / 9.0) * (1 - 0.5 * abs(dj)))
R = np.maximum(R - spread, RB + 0.003)
print(f"KILT: {NR} aneis de {HEM:.2f} a {TOP:.2f} m; raio medio topo {R[0].mean():.3f}, barra {R[-1].mean():.3f} m; "
      f"pregas de {PLEAT * 1000:.0f} mm fora do avental (+-{math.degrees(APRON):.0f} graus); recolhido sob casaca/correame "
      f"em {int((cut > 0).sum())} pontos (ate {cut.max() * 1000:.1f} mm)")


def r_at(j, th):
    th = (th + math.pi) % (2 * math.pi) - math.pi
    x = (th + math.pi) / (2 * math.pi) * NTH
    i0 = int(math.floor(x)) % NTH; f = x - math.floor(x)
    return R[j, i0] * (1 - f) + R[j, (i0 + 1) % NTH] * f


# ---------------------------------------------------------------- 2. the kilt halves (outer, lining, edges)
DENS = 0.402
NC = 78
LSTEP = 3                                                             # lining columns: every 3rd (NC % LSTEP == 0)
LINING = 0.002
HALVES = {"E": (math.radians(-12), math.radians(182)), "D": (math.radians(-182), math.radians(8))}
OVER_F = (math.radians(-12), math.radians(8)); OVER_B = (math.radians(178), math.radians(182))


def ang_dist(t, a0, a1):
    w = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    c, hw = (a0 + a1) / 2, (a1 - a0) / 2
    return max(0.0, abs(w(t - c)) - hw)


def under(th):
    dd = min(ang_dist(th, *OVER_F), ang_dist(th, *OVER_B))
    return max(0.0, 1 - dd / math.radians(4))


cloth = MAT.get("HCL_la_azul")
for s, (a0, a1) in HALVES.items():
    pid = PID[f"saia_{s}"]
    ths = np.linspace(a0, a1, NC + 1)
    outer, inner = [], []
    for j, h in enumerate(HS):
        ro, ri = [], []
        for th in ths:
            r = r_at(j, th) - (0.0025 * under(th) if s == "D" else 0.0)
            d = d2(th)
            ro.append(bm.verts.new((AX.x + d[0] * r, AX.y + d[1] * r, Z(h))))
            ri.append(bm.verts.new((AX.x + d[0] * (r - LINING), AX.y + d[1] * (r - LINING), Z(h))))
        outer.append(ro); inner.append(ri)

    def uvp(j, i, lin=False):
        arc = sum((outer[j][k + 1].co - outer[j][k].co).length for k in range(i))
        sc_ = 0.5 if lin else 1.0
        return (arc * DENS * sc_, (HS[j] - HEM) * DENS * sc_)
    newf = []
    for j in range(NR - 1):
        for i in range(NC):
            f = bm.faces.new((outer[j][i], outer[j + 1][i], outer[j + 1][i + 1], outer[j][i + 1]))
            quads = [(f, False, ((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1)))]
            if i % LSTEP == 0:                            # lining: one quad every LSTEP columns (it is not seen pleated)
                i2 = i + LSTEP
                g = bm.faces.new((inner[j][i2], inner[j + 1][i2], inner[j + 1][i], inner[j][i]))
                quads.append((g, True, ((j, i2), (j + 1, i2), (j + 1, i), (j, i))))
            for ff, lin, ij in quads:
                ff[PL] = pid; ff.material_index = cloth
                for l, (jj, ii) in zip(ff.loops, ij):
                    l[uvl].uv = uvp(jj, ii, lin)
                newf.append(ff)
    sides = [[(NR - 1, i) for i in range(NC + 1)], [(j, NC) for j in range(NR - 1, -1, -1)],
             [(0, i) for i in range(NC, -1, -1)], [(j, 0) for j in range(0, NR)]]
    for k_, side in enumerate(sides):
        run = 0.0
        for p_, q_ in zip(side, side[1:]):
            A, B = outer[p_[0]][p_[1]], outer[q_[0]][q_[1]]
            Ai, Bi = inner[p_[0]][p_[1]], inner[q_[0]][q_[1]]
            L = (B.co - A.co).length
            f = bm.faces.new((A, B, Bi, Ai))
            f[PL] = pid; f.material_index = cloth
            v0 = 0.02 * k_
            for l, uv in zip(f.loops, ((run * DENS, v0), ((run + L) * DENS, v0), ((run + L) * DENS, v0 + 0.004), (run * DENS, v0 + 0.004))):
                l[uvl].uv = uv
            run += L
            newf.append(f)
    IN, OU = set(sum(inner, [])), set(sum(outer, []))
    mid = outer[NR // 2][NC // 2].co
    for f in newf:
        f.normal_update()
        c = f.calc_center_median()
        radial = Vector((c.x - AX.x, c.y - AX.y, 0)).normalized()
        vs_ = set(f.verts)
        if vs_ <= OU or vs_ <= IN:
            want = -1 if vs_ <= IN else 1
            if f.normal.dot(radial) * want < 0:
                f.normal_flip()
        else:
            away = c - mid
            if c.z < Z(HEM) + 0.002 or c.z > Z(TOP) - 0.002:
                away = Vector((0, 0, c.z - mid.z))
            if f.normal.dot(away) < 0:
                f.normal_flip()
    print(f"KILT_{s}: {len(newf)} faces; de {math.degrees(a0):.0f} a {math.degrees(a1):.0f} graus")

loose = [v for v in bm.verts if not v.link_faces]                    # lining verts between its coarse columns
bmesh.ops.delete(bm, geom=loose, context="VERTS")
bm.normal_update()
bm.to_mesh(ob.data); ob.data.update()
bm.free()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_kilt"] = json.dumps({"hem": HEM, "top": TOP, "pleat": PLEAT, "apron_deg": math.degrees(APRON), "ax": [AX.x, AX.y]})
ob["hcl_origem"] = f"derivado de HCL_U_UK1812_Linha_LOD0 por build_kilt_uk.py (hem {HEM}), 2026-10-13"

# ---------------------------------------------------------------- 3. UV: pack every island but the hands and buttons
me = ob.data
pa = me.attributes["hcl_part"].data
skip = {PID["maos_template"], PID["botoes"]}
for o in sc.objects:
    o.select_set(o is ob)
bpy.context.view_layer.objects.active = ob
sc.tool_settings.use_uv_select_sync = True
bpy.ops.object.mode_set(mode="EDIT")
eb = bmesh.from_edit_mesh(me)
epl = eb.faces.layers.int.get("hcl_part")
for f in eb.faces:
    f.select = f[epl] not in skip
bmesh.update_edit_mesh(me)
try:
    bpy.ops.uv.pack_islands(rotate=False, margin=0.003, scale=True)
except TypeError:
    bpy.ops.uv.pack_islands(rotate=False, margin=0.003)
eb = bmesh.from_edit_mesh(me)
euv = eb.loops.layers.uv.active
epl = eb.faces.layers.int.get("hcl_part")
for f in eb.faces:
    if f[epl] not in skip:
        for l in f.loops:
            u, v = l[euv].uv
            l[euv].uv = (u * 0.94, v * 0.94)
bmesh.update_edit_mesh(me)
bpy.ops.object.mode_set(mode="OBJECT")
uvd = me.uv_layers.active.data
packed = [uvd[li].uv[:] for p in me.polygons if pa[p.index].value not in skip for li in p.loop_indices]
pu, pv = [u for u, v in packed], [v for u, v in packed]
print(f"UV: ilhas reempacotadas em u {min(pu):.3f}..{max(pu):.3f}, v {min(pv):.3f}..{max(pv):.3f}")

# ---------------------------------------------------------------- 4. checks
bm = bmesh.new(); bm.from_mesh(me)
PL = bm.faces.layers.int.get("hcl_part")
kilt = tri_bvh({PID["saia_E"], PID["saia_D"]})
vp = vparts()
tv = [v for v in bm.verts if vp.get(v, set()) & {PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]}
      and Z(HEM) < v.co.z < Z(TOP)]
out_bad = sum(1 for v in tv if kilt.ray_cast(v.co + Vector((v.co.x - AX.x, v.co.y - AX.y, 0)).normalized() * 1e-4,
                                               Vector((v.co.x - AX.x, v.co.y - AX.y, 0)).normalized(), 0.3)[0] is None)
jv = [v for v in bm.verts if vp.get(v, set()) & {PID["aba_E"], PID["aba_D"]} and Z(HEM) < v.co.z < Z(TOP)]
jac_bad = 0
for v in jv:                                        # a tail point with kilt cloth OUTSIDE it = the kilt pokes through
    q = Vector((v.co.x - AX.x, v.co.y - AX.y, 0)).normalized()
    if kilt.ray_cast(v.co + q * 1e-4, q, 0.05)[0] is not None:
        jac_bad += 1
ev_bad = 0
for e in equip:
    for v in e.data.vertices:
        co = e.matrix_world @ v.co
        if Z(HEM) < co.z < Z(TOP):
            q = Vector((co.x - AX.x, co.y - AX.y, 0)).normalized()
            if kilt.ray_cast(co + q * 1e-4, q, 0.05)[0] is not None:
                ev_bad += 1
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"VERIFICA: pontos da calca fora do kilt: {out_bad} de {len(tv)}; pontos das abas com kilt por fora: {jac_bad} de "
      f"{len(jv)}; pontos do correame/mochila com kilt por fora: {ev_bad}; triangulos {tris}; vertices {len(me.vertices)}")
bm.free()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
