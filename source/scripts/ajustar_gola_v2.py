# Collar fix v2 of HCL_U_Pruss1813_01_LOD0, in place (vertices moved; topology and UVs unchanged, so the 17 texture
# variants stay valid). Problem still seen in game on 2026-10-12 after fix v1 (ajustar_gola.py): the head's throat
# covers the front of the collar. Cause: v1 shaped the collar around a neck of 104 x 104 mm centred at y = +0.050,
# taken from the approximate head and TemplateRTM\Male.p3d measurements; the GAME head (Arma 3 Samples
# TemplateRTM\bust.p3d, Resolution 1, texture m_white_01, its nape and bib fitting A3_character_example) has a neck
# ~125 x 140 mm whose centre goes from y = +0.050 (1.50 m) to +0.004 (1.585 m): the throat lies 35-45 mm in front of
# the v1 collar and the nape 15-30 mm in front of its back wall (measured by diag_gola_bust.py).
# v2: every collar vertex keeps its angle theta about the v1 axis (0, 0.050), its offset e from the v1 neck surface
# (wall thickness, roll) and its height fraction between the collar base and top of its column; it is placed at the
# same offset e from the GAME neck surface (max of the skin over a short height window, by ray casts on bust.p3d),
# about the game neck's leaning axis. The front base drops to sit on the chest (the throat goes down to 1.476 m at
# the front), the front top drops TOPDROP for the chin. The coat yoke follows the collar base ring with a smooth
# fade (FADE), sliding on the old coat surface; coat buttons near the collar move rigidly, shoulder boards and their
# buttons take the displacement of the coat under them. Then the coat is pushed out where the head's skin (trapezius
# skirt, bib) would still show through it, and the result is checked: skin visible below the collar top, chin room,
# collar x coat / collar x shoulder-board crossings.
#   blender -b <LOD0.blend> --python ajustar_gola_v2.py -- <Samples dir> [dry] [topdrop=0.005] [fade=0.08]
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
SAMPLES = a[0]
DRY = "dry" in a
OPT = dict(x.split("=", 1) for x in a[1:] if "=" in x)
TOPDROP = float(OPT.get("topdrop", 0.005))
FADE = float(OPT.get("fade", 0.08))
GROUND = -1.0069
Z = lambda h: GROUND + h
O1 = Vector((0.0, 0.050, 0.0))                      # v1 collar axis


def dvec(th):
    return Vector((math.sin(th), -math.cos(th), 0.0))   # th = 0: front (-Y); th = +90 deg: character's left (+X)


def theta_xy(p, c):
    return math.atan2(p.x - c.x, -(p.y - c.y))


# ---------------------------------------------------------------- v1 neck model (ajustar_gola.py, exactly)
Y_C, A_W, A_B, A_F0, A_F_TILT, H0, DIP1 = 0.050, 0.052, 0.052, 0.052, 0.12, 1.535, 0.008


def r_v1(th, z):
    aF = A_F0 + A_F_TILT * max(0.0, (z - GROUND) - H0)
    c, s = math.cos(th), math.sin(th)
    aD = aF if c >= 0 else A_B
    return 1.0 / math.sqrt((c / aD) ** 2 + (s / A_W) ** 2)


# ---------------------------------------------------------------- game head (bust.p3d Res 1)
bust = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\bust.p3d"))[0]
BP = [Vector(to_blender(p)) for p in bust["points"]]
BF = [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3]
HB = BVHTree.FromPolygons(BP, BF)
# merged copy for vertex normals (the P3D splits points along UV seams)
canon, cid = {}, []
for p in BP:
    cid.append(canon.setdefault((round(p.x, 5), round(p.y, 5), round(p.z, 5)), len(canon)))
UP_ = [None] * len(canon)
for i, p in enumerate(BP):
    UP_[cid[i]] = p
hb = bmesh.new()
hv = [hb.verts.new(p) for p in UP_]
for f in BF:
    vs = list(dict.fromkeys(hv[cid[i]] for i in f))
    if len(vs) >= 3:
        try:
            hb.faces.new(vs)
        except ValueError:
            pass
hb.normal_update()
HN = [v.normal.copy() for v in hb.verts]
HP = [v.co.copy() for v in hb.verts]


def yc(z):                                          # game neck axis (fit of the bust sections 1.56-1.585 m)
    h = min(max(z - GROUND, 1.50), 1.585)
    return 0.0177 - (h - 1.56) * 0.535


def c2(z):
    return Vector((0.0, yc(z), 0.0))


def skin_r(th, z, h):
    """Distance from the game neck axis at height z, along theta, to the outer skin at height h (None = miss)."""
    c = Vector((0.0, yc(z), Z(h)))
    d = dvec(th)
    hit = HB.ray_cast(c + d * 0.25, -d, 0.25)
    return None if hit[0] is None else (hit[0] - c).length


NTH = 128
HS = [round(1.495 + 0.0025 * j, 4) for j in range(46)]          # 1.495 .. 1.6075


def r_env(th, z):
    """Neck surface the collar must clear at height z: the largest skin radius in [z - 3 mm, z + 8 mm] (the neck
    flares below and the throat leans forward above), with no chin (front window capped at 1.585 m)."""
    h0 = z - GROUND
    lo, hi = h0 - 0.003, h0 + 0.008
    if math.cos(th) > 0.3:
        hi = min(hi, 1.585)
    if math.cos(th) < -0.2:                         # back: the trapezius rises steeply between two collar rings
        lo = h0 - 0.008
    best = None
    for h in HS:
        if lo - 1e-6 <= h <= hi + 1e-6:
            r = skin_r(th, z, h)
            if r is not None and (best is None or r > best):
                best = r
    if best is None:                                # below the head's skin there: nearest valid height above
        for h in HS:
            if h > hi:
                r = skin_r(th, z, h)
                if r is not None:
                    return r
    return best


# ---------------------------------------------------------------- uniform
ob = bpy.data.objects["HCL_U_Pruss1813_01_LOD0"]
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
vpart = {}
for f in bm.faces:
    for vv in f.verts:
        vpart.setdefault(vv.index, set()).add(f[PL])
ORIG = [v.co.copy() for v in bm.verts]
OLD_COAT = BVHTree.FromPolygons(ORIG, [[x.index for x in f.verts] for f in bm.faces if f[PL] == PID["casaco_corpo"]])
GV = [v.index for v in bm.verts if PID["gola"] in vpart.get(v.index, ())]

# 1. collar columns (v1 kept theta exactly): base / top height per column
col = {}
for i in GV:
    th = theta_xy(ORIG[i], O1)
    col.setdefault(round(math.degrees(th), 1), []).append(i)
keys = sorted(col)
zb_old = {k: min(ORIG[i].z for i in col[k]) for k in keys}
zt_old = {k: max(ORIG[i].z for i in col[k]) for k in keys}
print(f"GOLA: {len(GV)} vertices em {len(keys)} colunas")


def periodic_interp(table, th_deg):
    ks = sorted(table)
    xs = np.array(ks + [ks[0] + 360.0])
    ys = np.array([table[k] for k in ks] + [table[ks[0]]])
    t = (th_deg - ks[0]) % 360.0 + ks[0]
    return float(np.interp(t, xs, ys))


# 2. new base height of each column: the outer foot of the new collar sits 2 mm into the OLD coat surface under it
#    (the front drops onto the chest); never above the old base
def outer_foot(k, zb):
    th = math.radians(k)
    z = zb
    for _ in range(3):
        r = r_env(th, z)
        p = c2(z) + dvec(th) * (r + 0.0135)
        hit = OLD_COAT.ray_cast(Vector((p.x, p.y, z + 0.10)), Vector((0, 0, -1)), 0.25)
        if hit[0] is None:
            return zb
        z = min(zb, hit[0].z - 0.002)
    return z


zb_new = {k: outer_foot(k, zb_old[k]) for k in keys}
# smooth the base line along the collar (3 passes over neighbouring columns), never raising it above the old base
for _ in range(3):
    zs = {k: zb_new[k] for k in keys}
    for j, k in enumerate(keys):
        zb_new[k] = min(zb_old[k], (zs[keys[j - 1]] + 2 * zs[k] + zs[keys[(j + 1) % len(keys)]]) / 4)
zt_new = {k: zt_old[k] - TOPDROP * max(0.0, math.cos(math.radians(k))) ** 2 for k in keys}
for k in keys[:: max(1, len(keys) // 16)]:
    print(f"   coluna {k:7.1f}: base {zb_old[k] - GROUND:.3f} -> {zb_new[k] - GROUND:.3f}; topo {zt_old[k] - GROUND:.3f} -> {zt_new[k] - GROUND:.3f}")

# 3. move the collar
moved = {}
env_cache = {}
for i in GV:
    p = ORIG[i]
    th = theta_xy(p, O1)
    k = round(math.degrees(th), 1)
    # v1 lowered the front top by DIP1 * cos^2 * up(z_orig): undo it to recover the height v1 computed r_v1 with
    z0 = p.z
    for _ in range(3):
        up = max(0.0, min(1.0, (z0 - Z(1.535)) / 0.055))
        z0 = p.z + DIP1 * max(0.0, math.cos(th)) ** 2 * up
    e = Vector((p.x - O1.x, p.y - O1.y, 0)).length - r_v1(th, z0)
    span = max(1e-6, zt_old[k] - zb_old[k])
    fr = (p.z - zb_old[k]) / span
    zn = zb_new[k] + fr * (zt_new[k] - zb_new[k])
    key = (k, round(zn, 4))
    if key not in env_cache:
        env_cache[key] = r_env(th, zn)
    r = env_cache[key]
    q = c2(zn) + dvec(th) * (r + e)
    moved[i] = Vector((q.x, q.y, zn))
# 3b. some columns have only a base and a top ring (one straight 45 mm wall): where the skin bulges between the two
#     rings (trapezius at the back sides) the straight inner wall must still clear it by CHORD_CLR; the whole column is
#     moved out by the largest deficit, and the shifts are smoothed with the neighbouring columns
CHORD_CLR = 0.003
shift = {}
for k in keys:
    th = math.radians(k)
    ids = col[k]
    rr = {i: (moved[i] - c2(moved[i].z)).to_2d().length for i in ids}
    ee = {i: rr[i] - (env_cache.get((k, round(moved[i].z, 4))) or rr[i]) for i in ids}
    e_in = min(ee.values())
    inner = sorted((i for i in ids if ee[i] <= e_in + 0.0015), key=lambda i: moved[i].z)
    best = 0.0
    for a_, b_ in zip(inner, inner[1:]):
        za, zb_ = moved[a_].z, moved[b_].z
        if zb_ - za < 0.004:
            continue
        for s_ in np.linspace(0.1, 0.9, 9):
            z = za + s_ * (zb_ - za)
            sk = skin_r(th, z, z - GROUND)
            if sk is None:
                continue
            wall = rr[a_] + s_ * (rr[b_] - rr[a_])
            best = max(best, sk + CHORD_CLR - wall)
    shift[k] = best
# wide plateau: neighbouring columns must move almost alike, or the wall between them twists (base radius falling
# while the top radius rises) and its lining crosses the cloth (dark AO wedge at the back sides, 2026-10-12)
sm = dict(shift)
nk = len(keys)
for j, k in enumerate(keys):
    sm[k] = max(shift[keys[(j + d) % nk]] * (1 - abs(d) / 4.0) for d in range(-3, 4))
n_sh = 0
for k in keys:
    if sm[k] <= 0:
        continue
    n_sh += 1
    d = dvec(math.radians(k))
    for i in col[k]:
        moved[i] = moved[i] + d * sm[k]
print(f"GOLA: {n_sh} colunas afastadas para a parede reta liberar a pele ({CHORD_CLR * 1000:.0f} mm); "
      f"max {max(sm.values()) * 1000:.1f} mm")
# 3c. a collar is a band wrapped round the neck: every ring of it (base inner/outer, top inner/outer, roll) is made
#     convex in plan, so the dips of the skin (between the throat and the trapezius flare, either side of the Adam's
#     apple) are bridged instead of followed; a dip followed by the 2-ring wall made a dark crease on the collar
def hull2d(P):
    P = sorted(set(P))
    if len(P) < 3:
        return P
    cr = lambda o, a_, b_: (a_[0] - o[0]) * (b_[1] - o[1]) - (a_[1] - o[1]) * (b_[0] - o[0])
    lo, up_ = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up_) >= 2 and cr(up_[-2], up_[-1], p) <= 0:
            up_.pop()
        up_.append(p)
    return lo[:-1] + up_[:-1]


def hull_radius(H, d):
    """Distance from the origin along unit 2D direction d to the convex polygon H (origin inside)."""
    best = None
    for a_, b_ in zip(H, H[1:] + H[:1]):
        ex, ey = b_[0] - a_[0], b_[1] - a_[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        t = (a_[0] * ey - a_[1] * ex) / den
        s_ = (a_[0] * d[1] - a_[1] * d[0]) / den
        if t > 0 and -1e-9 <= s_ <= 1 + 1e-9:
            best = t if best is None else min(best, t)
    return best


role = {}
for k in keys:
    ids = col[k]
    zmid = (min(moved[i].z for i in ids) + max(moved[i].z for i in ids)) / 2
    for top in (False, True):
        grp = [i for i in ids if (moved[i].z > zmid) == top]
        rs = sorted(set(round((moved[i] - c2(moved[i].z)).to_2d().length, 4) for i in grp))
        for i in grp:
            role[i] = (top, rs.index(round((moved[i] - c2(moved[i].z)).to_2d().length, 4)))


def rad(i):
    return (moved[i] - c2(moved[i].z)).to_2d().length


def set_rad(i, r):
    q = (moved[i] - c2(moved[i].z)).to_2d()
    if q.length > 1e-9:
        q = q.normalized() * (r - q.length)
        moved[i] = moved[i] + Vector((q.x, q.y, 0))


pre = {i: rad(i) for i in role}
gap = {}                                         # original spacing between the rings of one column and level
for k in keys:
    for top in (False, True):
        grp = sorted((i for i in col[k] if role[i][0] == top), key=lambda i: role[i][1])
        for i, j in zip(grp, grp[1:]):
            if role[j][1] > role[i][1]:
                gap[(k, top, role[j][1])] = pre[j] - pre[i]
# (i) smooth every ring along the collar (2 passes of 1-2-1, outward only: the clearance is kept), so neighbouring
#     columns agree
roles = sorted(set(role.values()))
for rk in roles:
    per = {k: [i for i in col[k] if role[i] == rk] for k in keys}
    ks = [k for k in keys if per[k]]
    for _ in range(2):
        R = {k: sum(rad(i) for i in per[k]) / len(per[k]) for k in ks}
        n_ = len(ks)
        for j, k in enumerate(ks):
            target = max(R[k], 0.25 * R[ks[j - 1]] + 0.5 * R[k] + 0.25 * R[ks[(j + 1) % n_]])   # only outward
            for i in per[k]:
                set_rad(i, rad(i) + (target - R[k]))
# (ii) convex rings
n_hull = 0
for rk in roles:
    ids = [i for i in role if role[i] == rk]
    Q = {i: (moved[i].x, moved[i].y - yc(moved[i].z)) for i in ids}
    H = hull2d(list(Q.values()))
    for i, q in Q.items():
        r = math.hypot(*q)
        if r < 1e-6 or len(H) < 3:
            continue
        rh = hull_radius(H, (q[0] / r, q[1] / r))
        if rh is not None and rh > r + 1e-5:
            set_rad(i, rh)
            n_hull += 1
# (iii) rings of one column never cross: each outer ring stays at least its original spacing beyond the inner one
n_ord = 0
for k in keys:
    for top in (False, True):
        grp = sorted((i for i in col[k] if role[i][0] == top), key=lambda i: role[i][1])
        for i, j in zip(grp, grp[1:]):
            g = gap.get((k, top, role[j][1]))
            if g is not None and rad(j) < rad(i) + g:
                set_rad(j, rad(i) + g)
                n_ord += 1
base_shift = {}
for i in role:
    if not role[i][0] and role[i][1] == 1:
        k = round(math.degrees(theta_xy(ORIG[i], O1)), 1)
        base_shift[k] = rad(i) - pre[i]
print(f"GOLA: aneis suavizados e convexos ({n_hull} vertices ate o casco, {n_ord} reordenados); base "
      f"{min(base_shift.values(), default=0) * 1000:+.1f}..{max(base_shift.values(), default=0) * 1000:+.1f} mm")
sf = [(moved[i] - ORIG[i]).dot(Vector((0, -1, 0))) for i in GV if math.cos(theta_xy(ORIG[i], O1)) > 0.95]
sb = [(moved[i] - ORIG[i]).dot(Vector((0, -1, 0))) for i in GV if math.cos(theta_xy(ORIG[i], O1)) < -0.95]
print(f"GOLA movida: frente avanca {min(sf) * 1000:.0f}..{max(sf) * 1000:.0f} mm; costas avancam {min(sb) * 1000:.0f}..{max(sb) * 1000:.0f} mm")


# 4. coat yoke: displacement of the collar base ring (old ring at offset 0.010 from the v1 neck -> new ring at the same
#    offset from the game neck), faded over FADE from the old ring, sliding on the old coat surface
def base_disp(th):
    k_deg = math.degrees(th)
    zbo, zbn = periodic_interp(zb_old, k_deg), periodic_interp(zb_new, k_deg)
    old_p = O1 + dvec(th) * (r_v1(th, zbo) + 0.010)
    sh = periodic_interp({k: base_shift.get(k, 0.0) for k in keys}, k_deg)      # convex base ring (3c)
    new_p = c2(zbn) + dvec(th) * (r_env(th, zbn) + 0.010 + sh)
    return Vector((new_p.x - old_p.x, new_p.y - old_p.y, zbn - zbo)), r_v1(th, zbo) + 0.010


disp_cache = {}


def disp_at(th):
    k = round(th, 2)
    if k not in disp_cache:
        disp_cache[k] = base_disp(k)
    return disp_cache[k]


def yoke(p):
    th = theta_xy(p, O1)
    d, r_ring = disp_at(th)
    r_p = Vector((p.x - O1.x, p.y - O1.y, 0)).length
    t = max(0.0, min(1.0, (r_p - r_ring) / FADE))
    w = 1.0 if r_p < r_ring else 1.0 - t * t * (3 - 2 * t)
    if w <= 0:
        return None
    newp = p + Vector((d.x, d.y, 0)) * w
    zexp = p.z + d.z * w
    hit = OLD_COAT.ray_cast(Vector((newp.x, newp.y, p.z + 0.15)), Vector((0, 0, -1)), 0.30)
    newp.z = hit[0].z if (hit[0] is not None and abs(hit[0].z - zexp) < 0.03) else zexp
    return newp


n_yoke = 0
COAT_V = [v.index for v in bm.verts if PID["casaco_corpo"] in vpart.get(v.index, ()) and PID["gola"] not in vpart[v.index]]
for i in COAT_V:
    if ORIG[i].z < Z(1.40):
        continue
    np_ = yoke(ORIG[i])
    if np_ is not None and (np_ - ORIG[i]).length > 1e-7:
        moved[i] = np_
        n_yoke += 1
print(f"CASACO: {n_yoke} vertices do encaixe movidos (deslizam na superficie antiga)")

# 5. coat pushed out where the head's skin would still come through it (skirt over the trapezius, bib): every coat
#    vertex near the head lies at least MARGIN outside the skin; the push is spread over the neighbours
MARGIN = 0.003
hkd = KDTree(len(HP))
for j, p in enumerate(HP):
    hkd.insert(p, j)
hkd.balance()
HBM = BVHTree.FromBMesh(hb)
push = {}
for i in COAT_V:
    p = moved.get(i, ORIG[i])
    if p.z < Z(1.44) or p.z > Z(1.62):
        continue
    loc, nrm, fi, dist = HBM.find_nearest(p, 0.05)
    if loc is None:
        continue
    s = (p - loc).dot(nrm)
    if s < MARGIN:
        push[i] = nrm * (MARGIN - s)
if push:
    adj = {}
    for e in bm.edges:
        a_, b_ = e.verts[0].index, e.verts[1].index
        adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
    coat_set = set(COAT_V)
    field = dict(push)
    for _ in range(4):                                # spread: each neighbour takes half of the largest push next to it
        nf = dict(field)
        for i, d in field.items():
            for j in adj.get(i, []):
                if j in coat_set and j not in push and (j not in nf or nf[j].length < 0.5 * d.length):
                    nf[j] = d * 0.5
        field = nf
    for i, d in field.items():
        moved[i] = moved.get(i, ORIG[i]) + d
    print(f"CASACO empurrado para fora da pele: {len(push)} vertices (+{len(field) - len(push)} vizinhos), "
          f"max {max(d.length for d in push.values()) * 1000:.1f} mm")
else:
    print("CASACO empurrado para fora da pele: nenhum vertice precisou")

# 6. coat buttons near the collar move rigidly with the coat under their centre; shoulder boards and their buttons
#    take the displacement of the nearest coat vertex
from mathutils.interpolate import poly_3d_calc
COAT_F = [[x.index for x in f.verts] for f in bm.faces if f[PL] == PID["casaco_corpo"]]


def coat_disp_at(p):
    """Displacement of the coat surface under p: the old coat face straight below (else the nearest one), its vertex
    displacements interpolated at the foot point (the nearest VERTEX alone gave the board's inner end a spike)."""
    hit = OLD_COAT.ray_cast(p + Vector((0, 0, 0.10)), Vector((0, 0, -1)), 0.20)
    if hit[0] is None:
        hit = OLD_COAT.find_nearest(p)
    loc, fi = hit[0], hit[2]
    vs = COAT_F[fi]
    wts = poly_3d_calc([ORIG[i] for i in vs], loc)
    return sum(((moved.get(i, ORIG[i]) - ORIG[i]) * w for i, w in zip(vs, wts)), Vector())


seen = set()
n_btn = n_plat = 0
PLAT = {PID["platina_E"], PID["platina_D"]}
for v in bm.verts:
    if v.index in seen or PID["botoes"] not in vpart.get(v.index, ()):
        continue
    comp, stack = [], [v]
    seen.add(v.index)
    while stack:
        x = stack.pop(); comp.append(x)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in seen:
                seen.add(y.index); stack.append(y)
    c = sum((ORIG[x.index] for x in comp), Vector()) / len(comp)
    if c.z < Z(1.40):
        continue
    d = coat_disp_at(c)
    if d.length > 1e-6:
        for x in comp:
            moved[x.index] = ORIG[x.index] + d
        n_btn += 1
for v in bm.verts:
    if vpart.get(v.index, set()) & PLAT and ORIG[v.index].z > Z(1.40):
        d = coat_disp_at(ORIG[v.index])
        if d.length > 1e-6:
            moved[v.index] = ORIG[v.index] + d
            n_plat += 1
print(f"BOTOES movidos inteiros: {n_btn}; PLATINAS: {n_plat} vertices acompanham o casaco")

# ---------------------------------------------------------------- checks on the new shape
def checks(NEW, label):
    print(f"== VERIFICACAO {label}")


    def bvh_of(pids):
        fs = [[x.index for x in f.verts] for f in bm.faces if f[PL] in pids]
        return BVHTree.FromPolygons(NEW, fs), fs


    def tri_bvh(pids):
        tris = []
        for f in bm.faces:
            if f[PL] in pids:
                vs = [x.index for x in f.verts]
                for t in range(1, len(vs) - 1):
                    tris.append([vs[0], vs[t], vs[t + 1]])
                if len(vs) == 4:
                    tris.append([vs[0], vs[1], vs[3]]); tris.append([vs[1], vs[2], vs[3]])
        return BVHTree.FromPolygons(NEW, tris)


    G_T = tri_bvh({PID["gola"]})
    C_T = tri_bvh({PID["casaco_corpo"]})
    P_T = tri_bvh(PLAT)
    U_T = tri_bvh({PID["gola"], PID["casaco_corpo"]} | PLAT | {PID["manga_E"], PID["manga_D"]})
    print(f"CRUZAMENTOS: gola x casaco {len(G_T.overlap(C_T))} pares; gola x platinas {len(G_T.overlap(P_T))} pares")
    # collar self-intersection: crossing triangle pairs that share no vertex
    # (Blender's own triangulation of each quad: testing both diagonals flags a twisted cloth/lining pair that is
    # split along different diagonals, which the renders and the bake never use together)
    tb = bm.copy()
    for v_, p_ in zip(tb.verts, NEW):
        v_.co = p_
    tpl = tb.faces.layers.int.get("hcl_part")
    gt = [tuple(l.vert.index for l in tri) for tri in tb.calc_loop_triangles() if tri[0].face[tpl] == PID["gola"]]
    tb.free()
    GS = BVHTree.FromPolygons(NEW, gt)
    selfx = [(a_, b_) for a_, b_ in GS.overlap(GS) if a_ < b_ and not set(gt[a_]) & set(gt[b_])]
    print(f"GOLA autointersecao: {len(selfx)} pares de triangulos" +
          ("" if not selfx else " em " + ", ".join(f"{math.degrees(theta_xy(NEW[gt[a_][0]], Vector((0, 0.012, 0)))):+.0f} graus/{NEW[gt[a_][0]].z - GROUND:.3f} m" for a_, b_ in selfx[:4])))

    # skin visible: a head vertex below the collar top of its direction whose outward normal ray leaves without hitting
    # the uniform
    gnew = [NEW[i] for i in GV]
    top_tab = {}
    for p in gnew:
        k = int(round(math.degrees(theta_xy(p, Vector((0, 0.012, 0)))) / 10.0)) % 36
        top_tab[k] = max(top_tab.get(k, -9), p.z)
    vis = []
    for p, n in zip(HP, HN):
        h = p.z - GROUND
        if h > 1.62 or h < 1.44:
            continue
        k = int(round(math.degrees(theta_xy(p, Vector((0, 0.012, 0)))) / 10.0)) % 36
        if p.z > top_tab.get(k, Z(1.59)) - 0.002:
            continue
        hit = U_T.ray_cast(p + n * 0.0005, n, 0.10)
        if hit[0] is None:
            vis.append(p)
    print(f"PELE VISIVEL abaixo do topo da gola: {len(vis)} vertices da cabeca" +
          (f" (alturas {min(q.z for q in vis) - GROUND:.3f}..{max(q.z for q in vis) - GROUND:.3f})" if vis else ""))
    for q in vis:
        print(f"      pele visivel: {math.degrees(theta_xy(q, Vector((0, 0.012, 0)))):+6.1f} graus, {q.z - GROUND:.3f} m")
    # chin room above the collar top (front half): vertical distance to the head
    gap = []
    for i in GV:
        p = NEW[i]
        if math.cos(theta_xy(p, c2(p.z))) < 0.5 or p.z < max(top_tab.values()) - 0.03:
            continue
        hit = HB.ray_cast(p + Vector((0, 0, 0.0005)), Vector((0, 0, 1)), 0.10)
        if hit[0] is not None:
            gap.append((hit[0].z - p.z) * 1000)
    print(f"QUEIXO: folga vertical sobre o topo da frente da gola {min(gap):.1f} mm (mediana {np.median(gap):.1f})" if gap else "QUEIXO: sem cabeca acima")
    # inner wall clearance to the neck (head vertices inside the collar wall)
    inside = 0
    for p in HP:
        if not (Z(1.50) < p.z < Z(1.60)):
            continue
        c = Vector((0, yc(p.z), p.z))
        d = c - p
        if d.length < 1e-6:
            continue
        hit = G_T.ray_cast(p, d.normalized(), d.length)
        if hit[0] is not None:
            inside += 1
    print(f"PESCOCO atravessando a gola (raio do ponto ao eixo cruza a gola): {inside} vertices")
    for h in (1.51, 1.535, 1.56, 1.585):
        ring = [p for p in gnew if abs(p.z - Z(h)) < 0.006]
        if ring:
            print(f"GOLA h~{h:.3f}: x {min(p.x for p in ring):+.3f}..{max(p.x for p in ring):+.3f}  y {min(p.y for p in ring):+.3f}..{max(p.y for p in ring):+.3f}")



checks(ORIG, "antes")
checks([moved.get(i, ORIG[i]) for i in range(len(ORIG))], "depois")

if DRY:
    print("DRY: nada salvo")
else:
    for i, p in moved.items():
        bm.verts[i].co = p
    bm.to_mesh(ob.data)
    ob.data.update()
    ob["hcl_gola_ajustada"] = "2026-10-12: v2, gola em volta do pescoco da cabeca do jogo (bust.p3d) (ajustar_gola_v2.py)"
    bpy.ops.wm.save_mainfile()
    print("SALVO", bpy.data.filepath)
