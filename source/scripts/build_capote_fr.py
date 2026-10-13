# French infantry greatcoat ("capote"), the WINTER version of the 1812 uniform (user 2026-10-12: "adiciona ... as versoes
# de inverno dos uniformes"). Reference: mod tiles FranceINF_diffuse c0 r1 (beige) and c3 r1 (grey): a long
# double-breasted coat of plain cloth, two rows of 7 brass buttons, same cloth collar and cuffs, a long skirt.
# Derived from the French coat 1812 (build_uniforme_fr.py, collar v2 on the game head), so the body, sleeves, cuffs,
# shoulder straps, collar, trousers, gaiters, shoes and template hands are the validated ones:
#   1. removed: tails, lapels, the lapel and tail buttons
#   2. the skirt: two halves (saia_E over saia_D) from the waist (TOP, over the coat's lower edge at 1.124 m) to HEM,
#      hanging around both legs: per row, the convex hull of the trousers + a clearance growing to the hem, never
#      narrower than the row above (cloth falls from the seat), rings smoothed outward and made convex; the left half
#      laps over the right at the front and at the back; outer cloth + lining 2.5 mm inside + hem/edge strips
#   3. the crossbelts, cartridge box, bayonet and havresac are SHARED with the coat 1812 (one vest item for both
#      uniforms): wherever the skirt would come within 2.5 mm of them it is pulled in under them (never closer than
#      4 mm to the trousers)
#   4. two rows of 7 buttons on the chest (copies of a lapel button), rows 10 cm apart at the waist, 15 cm at the top
#   5. UV: every island except the template hands and the buttons' corner square is packed again (same relative scale)
#      into u, v < 0.94, so the corner square (u, v >= 0.948) stays the buttons' own; new texture set (hcl_u_fr1812_capote)
#   blender -b --factory-startup --python build_capote_fr.py -- <fr coat LOD0 .blend> <fr equipment .blend> <out .blend>
#           [hem=0.46] [top=1.15]
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, EQ, OUT = [os.path.abspath(x) for x in a[:3]]
OPT = dict(x.split("=", 1) for x in a[3:] if "=" in x)
HEM, TOP = float(OPT.get("hem", 0.46)), float(OPT.get("top", 1.15))
GROUND = -1.0069
Z = lambda h: GROUND + h
AX = Vector((0.0, 0.02, 0.0))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Fr1812_01_LOD0"]
ob = dst.objects[0]
sc.collection.objects.link(ob)
ob.name = "HCL_U_Fr1812_Capote_LOD0"
ob.data = ob.data.copy(); ob.data.name = "HCL_U_Fr1812_Capote_LOD0"
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


def tri_bvh(pids, bmesh_=None):
    b_ = bmesh_ or bm
    vs = list(b_.verts)
    idx = {v: i for i, v in enumerate(vs)}
    tris = []
    for f in b_.faces:
        if pids is None or f[PL] in pids:
            q = [idx[v] for v in f.verts]
            for t in range(1, len(q) - 1):
                tris.append([q[0], q[t], q[t + 1]])
    return BVHTree.FromPolygons([v.co.copy() for v in vs], tris)


# ---------------------------------------------------------------- 1. remove tails, lapels and their buttons
COAT = tri_bvh({PID["casaco_corpo"]})
gone = {PID["aba_E"], PID["aba_D"], PID["lapela_E"], PID["lapela_D"]}
btn_dead, tmpl = [], None
for comp in components(PID["botoes"]):
    c = sum((v.co for v in comp), Vector()) / len(comp)
    h = c.z - GROUND
    chest = abs(c.x) < 0.12 and c.y < -0.04 and 1.10 < h < 1.52             # lapel buttons
    back = c.y > 0.03 and 0.80 < h < 1.16 and abs(c.x) < 0.20                # tail / pocket buttons
    if chest or back:
        btn_dead.append(comp)
        if chest and tmpl is None and c.x > 0.02 and 1.30 < h < 1.40:
            faces_ = {f for v in comp for f in v.link_faces}
            loc, n0, _, _ = COAT.find_nearest(c)
            n0 = n0 if n0.y < 0 else -n0
            tmpl = dict(co=[v.co.copy() for v in comp], base=loc + n0 * 0.003, n=n0.copy(),
                        faces=[([comp.index(x) for x in f.verts], [l[uvl].uv.copy() for l in f.loops], f.material_index) for f in faces_])
assert tmpl is not None, "botao de lapela de referencia nao encontrado"
dead_f = [f for f in bm.faces if f[PL] in gone]
dead_v = {v for comp in btn_dead for v in comp}
bmesh.ops.delete(bm, geom=dead_f, context="FACES_ONLY")
bmesh.ops.delete(bm, geom=list(dead_v), context="VERTS")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
print(f"REMOVIDO: abas, lapelas ({len(dead_f)} faces) e {len(btn_dead)} botoes (lapelas e abas)")

# ---------------------------------------------------------------- 2. the skirt: ring radii
vp = vparts()
TROUS = [v.co.copy() for v in bm.verts if vp.get(v, set()) & {PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]}]
TP = np.array([p[:] for p in TROUS])
COAT = tri_bvh({PID["casaco_corpo"]})
TRB = tri_bvh({PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]})
# equipment (shared with the coat 1812): one BVH of the vest and the havresac
ebm = bmesh.new()
for e in equip:
    tmp = bmesh.new(); tmp.from_mesh(e.data)
    tmp.transform(e.matrix_world)
    m_ = bpy.data.meshes.new("tmp"); tmp.to_mesh(m_); tmp.free()
    ebm.from_mesh(m_); bpy.data.meshes.remove(m_)
EQB = BVHTree.FromBMesh(ebm)
NTH = 180
THS = np.linspace(-math.pi, math.pi, NTH, endpoint=False)
d2 = lambda th: np.array([math.sin(th), -math.cos(th)])               # 0 = front (-Y), +90 deg = wearer's left (+X)


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


def hull_radius(hull, th):
    """Distance from AX along direction th to the convex polygon (AX inside)."""
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


def coat_r(th, h):
    d = d2(th)
    o = Vector((AX.x + d[0] * 0.6, AX.y + d[1] * 0.6, Z(h)))
    hit = COAT.ray_cast(o, Vector((-d[0], -d[1], 0)), 0.6)
    return None if hit[0] is None else 0.6 - hit[3]


NR = 15
HS = np.linspace(TOP, HEM, NR)
R = np.zeros((NR, NTH))
RB = np.zeros((NR, NTH))                                              # trousers envelope (floor of every ring)
for j, h in enumerate(HS):
    sl = TP[np.abs(TP[:, 2] - Z(h)) < 0.02][:, :2]
    hull = hull2d(sl)
    t = (TOP - h) / (TOP - HEM)
    clear = 0.012 + 0.028 * t ** 1.2
    for i, th in enumerate(THS):
        rb = hull_radius(hull, th)
        rc = coat_r(th, h) if h > 1.10 else None
        RB[j, i] = rb
        R[j, i] = max(rb + clear, (rc + 0.003) if rc else 0.0)
    if j:                                                             # cloth falls from the seat: never narrower below
        R[j] = np.maximum(R[j], R[j - 1] - 0.002)
    for _ in range(4):                                                # ring smoothing, outward only
        R[j] = np.maximum(R[j], 0.25 * np.roll(R[j], 1) + 0.5 * R[j] + 0.25 * np.roll(R[j], -1))
    ring = np.array([AX.to_2d()[:] + d2(th) * r for th, r in zip(THS, R[j])])
    hr = hull2d(ring)                                                 # convex ring, like a coat skirt hanging
    R[j] = [hull_radius(hr, th) for th in THS]
# equipment: pull the skirt under the vest / havresac wherever they come within 2.5 mm (never < 4 mm off the trousers)
cut = np.zeros_like(R)
for j, h in enumerate(HS):
    for i, th in enumerate(THS):
        d = d2(th)
        o = Vector((AX.x, AX.y, Z(h)))
        start = max(RB[j, i] + 0.002, 0.02)
        hit = EQB.ray_cast(o + Vector((d[0], d[1], 0)) * start, Vector((d[0], d[1], 0)), 0.5)
        if hit[0] is not None:
            r_eq = start + hit[3]
            lim = max(RB[j, i] + 0.004, r_eq - 0.0025)
            if R[j, i] > lim:
                cut[j, i] = R[j, i] - lim
spread = cut.copy()                                                  # plateau: neighbours follow (no dents)
for j in range(NR):
    for i in range(NTH):
        for dj in (-1, 0, 1):
            for di in range(-4, 5):
                jj, ii = j + dj, (i + di) % NTH
                if 0 <= jj < NR:
                    spread[j, i] = max(spread[j, i], cut[jj, ii] * (1 - abs(di) / 5.0) * (1 - 0.5 * abs(dj)))
R = np.maximum(R - spread, RB + 0.004)
print(f"SAIA: {NR} aneis de {HEM:.2f} a {TOP:.2f} m; raio medio no topo {R[0].mean():.3f}, na barra {R[-1].mean():.3f} m; "
      f"puxada para dentro do correame/mochila em {int((cut > 0).sum())} pontos (ate {cut.max() * 1000:.1f} mm)")


def r_at(j, th):
    th = (th + math.pi) % (2 * math.pi) - math.pi
    x = (th + math.pi) / (2 * math.pi) * NTH
    i0 = int(math.floor(x)) % NTH; f = x - math.floor(x)
    return R[j, i0] * (1 - f) + R[j, (i0 + 1) % NTH] * f


# ---------------------------------------------------------------- 2b. the skirt halves (outer, lining, edges)
DENS = 0.402                                                         # coat texel density (UV units per metre)
NC = 30
LINING = 0.0025
HALVES = {"E": (math.radians(-10), math.radians(182)), "D": (math.radians(-182), math.radians(6))}
OVER_F = (math.radians(-10), math.radians(6)); OVER_B = (math.radians(178), math.radians(182))


def ang_dist(t, a0, a1):
    """Angular distance from t to the interval [a0, a1] (radians, wrap-around); 0 inside."""
    w = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    c, hw = (a0 + a1) / 2, (a1 - a0) / 2
    return max(0.0, abs(w(t - c)) - hw)


def under(th):
    """Right half (under) dips 3 mm inside the left one where they lap, fading 4 deg beyond."""
    dd = min(ang_dist(th, *OVER_F), ang_dist(th, *OVER_B))
    return max(0.0, 1 - dd / math.radians(4))


skirt_faces = []
uv_off = {"E": (0.0, 0.0), "D": (0.0, 0.0)}
for s, (a0, a1) in HALVES.items():
    pid = PID[f"saia_{s}"]
    ths = np.linspace(a0, a1, NC + 1)
    outer, inner = [], []
    for j, h in enumerate(HS):
        ro, ri = [], []
        for th in ths:
            r = r_at(j, th) - (0.003 * under(th) if s == "D" else 0.0)
            d = d2(th)
            ro.append(bm.verts.new((AX.x + d[0] * r, AX.y + d[1] * r, Z(h))))
            ri.append(bm.verts.new((AX.x + d[0] * (r - LINING), AX.y + d[1] * (r - LINING), Z(h))))
        outer.append(ro); inner.append(ri)
    # UV: u = arc length along the row (from the front edge), v = height; laid out flat, packed later
    def uvp(j, i, lin=False):
        arc = sum((outer[j][k + 1].co - outer[j][k].co).length for k in range(i))
        sc_ = 0.5 if lin else 1.0
        return (arc * DENS * sc_, (HS[j] - HEM) * DENS * sc_)
    newf = []
    for j in range(NR - 1):
        for i in range(NC):
            f = bm.faces.new((outer[j][i], outer[j + 1][i], outer[j + 1][i + 1], outer[j][i + 1]))
            g = bm.faces.new((inner[j][i + 1], inner[j + 1][i + 1], inner[j + 1][i], inner[j][i]))
            for ff, lin, ij in ((f, False, ((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1))),
                                (g, True, ((j, i + 1), (j + 1, i + 1), (j + 1, i), (j, i)))):
                ff[PL] = pid; ff.material_index = MAT["HCL_la_azul"]
                for l, (jj, ii) in zip(ff.loops, ij):
                    l[uvl].uv = uvp(jj, ii, lin)
                newf.append(ff)
    # edges: hem, front/back edges and top, joining cloth and lining (2.5 mm strips); one UV island per side (a single
    # 3 m strip would make the packer shrink the whole atlas)
    sides = [[(NR - 1, i) for i in range(NC + 1)], [(j, NC) for j in range(NR - 1, -1, -1)],
             [(0, i) for i in range(NC, -1, -1)], [(j, 0) for j in range(0, NR)]]
    for k_, side in enumerate(sides):
        run = 0.0
        for p_, q_ in zip(side, side[1:]):
            A, B = outer[p_[0]][p_[1]], outer[q_[0]][q_[1]]
            Ai, Bi = inner[p_[0]][p_[1]], inner[q_[0]][q_[1]]
            L = (B.co - A.co).length
            f = bm.faces.new((A, B, Bi, Ai))
            f[PL] = pid; f.material_index = MAT["HCL_la_azul"]
            v0 = 0.02 * k_
            for l, uv in zip(f.loops, ((run * DENS, v0), ((run + L) * DENS, v0), ((run + L) * DENS, v0 + 0.004), (run * DENS, v0 + 0.004))):
                l[uvl].uv = uv
            run += L
            newf.append(f)
    # outward normals for the cloth (away from the body axis), inward for the lining; edge strips face away from the
    # middle of the half (hem down, top up)
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
    skirt_faces += newf
    print(f"SAIA_{s}: {len(newf)} faces; de {math.degrees(a0):.0f} a {math.degrees(a1):.0f} graus")

# ---------------------------------------------------------------- 3. double-breasted buttons (two rows of 7)
COAT = tri_bvh({PID["casaco_corpo"]})


def coat_front(x, h):
    hit = COAT.ray_cast(Vector((x, -0.6, Z(h))), Vector((0, 1, 0)), 1.0)
    if hit[0] is None:
        return None, None
    n = hit[1] if hit[1].y < 0 else -hit[1]
    return hit[0], n.normalized()


nb = 0
for k, h in enumerate(np.linspace(1.465, 1.175, 7)):
    half = 0.050 + (0.075 - 0.050) * (h - 1.175) / (1.465 - 1.175)
    for sx in (1, -1):
        p, n = coat_front(sx * half, h)
        if p is None:
            continue
        Rm = tmpl["n"].rotation_difference(n).to_matrix()
        nv = [bm.verts.new(p + Rm @ (co - tmpl["base"])) for co in tmpl["co"]]
        for idxs, uvs, mi in tmpl["faces"]:
            f = bm.faces.new([nv[i] for i in idxs])
            f[PL] = PID["botoes"]; f.material_index = mi
            for l, uv in zip(f.loops, uvs):
                l[uvl].uv = uv
        nb += 1
print(f"BOTOES do capote: {nb} (2 fileiras de 7)")

bm.normal_update()
bm.to_mesh(ob.data); ob.data.update()
bm.free()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_origem"] = "derivado de HCL_U_Fr1812_01_LOD0 por build_capote_fr.py, 2026-10-12"

# ---------------------------------------------------------------- 4. UV: pack every island but the hands and buttons
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
corner = sum(1 for u, v in packed if u >= 0.948 and v >= 0.948)
print(f"UV: ilhas reempacotadas em u {min(pu):.3f}..{max(pu):.3f}, v {min(pv):.3f}..{max(pv):.3f}; cantos no quadrado dos botoes: {corner}")

# ---------------------------------------------------------------- 5. checks
bm = bmesh.new(); bm.from_mesh(me)
PL = bm.faces.layers.int.get("hcl_part")
skirt = tri_bvh({PID["saia_E"], PID["saia_D"]})
vp = vparts()
tv = [v for v in bm.verts if vp.get(v, set()) & {PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]}
      and Z(HEM) < v.co.z < Z(TOP)]
inside_bad = 0
for v in tv:                                       # trousers point outside the skirt: ray outward hits no skirt
    q = Vector((v.co.x - AX.x, v.co.y - AX.y, 0)).normalized()
    if skirt.ray_cast(v.co + q * 1e-4, q, 0.3)[0] is None:
        inside_bad += 1
ev_bad, ev_max = 0, 0.0
for e in equip:
    for v in e.data.vertices:
        co = e.matrix_world @ v.co
        if not (Z(HEM) < co.z < Z(TOP)):
            continue
        q = Vector((co.x - AX.x, co.y - AX.y, 0)).normalized()
        hit = skirt.ray_cast(co + q * 1e-4, q, 0.05)
        if hit[0] is not None:                     # skirt cloth outside this equipment point: it is under the skirt
            ev_bad += 1; ev_max = max(ev_max, hit[3])
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print(f"VERIFICA: pontos da calca fora da saia: {inside_bad} de {len(tv)}; pontos do correame/mochila sob a saia: {ev_bad} "
      f"(ate {ev_max * 1000:.1f} mm); triangulos {tris}; vertices {len(me.vertices)}")
bm.free()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
