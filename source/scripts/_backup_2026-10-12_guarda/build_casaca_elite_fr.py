# Elite company coat 1812 (grenadiers, voltigeurs): the French coat HCL_U_Fr1812_01_LOD0 (build_uniforme_fr.py) with
# EPAULETTES in place of the plain shoulder straps. Reference: mod atlas FranceINF c0 r3 (grenadier: red epaulettes)
# and c2 r3 (voltigeur: green epaulettes with a yellow crescent), spec uniforme_frances_infantaria_1812.md §11.1 (F12).
# The coat's shoulder strap (platina) is kept as the epaulette's tongue (same shape, weights and UV; colour from the
# variant). Added on each shoulder, beyond the tongue's outer end (the shoulder seam):
#   dragona_corpo_<s>    the body ("palette"): a stiff rounded slab 4 mm over the shoulder, its neck lying on the
#                        tongue's end, widening to a half-ellipse over the top of the sleeve
#   dragona_meialua_<s>  the crescent: a padded roll along the half-ellipse, thickest at the outer end
#   dragona_franja_<s>   the fringe: wool cords hanging from under the crescent, draped over the sleeve head by
#                        gravity along the cloth surface (A-pose), plus a dark under-curtain that fills the gaps
# UV: every new face has its own area in the free strip at the top of the atlas (v > 0.93; nothing of the coat is
# there), so the AO bake of the texture painter works; the areas are stored in ob["hcl_dragona_uv"] (JSON) for the
# painter's cord twist / crescent rules. New material slot "HCL_la_dragona" (painter only; the P3D uses one texture).
# Measures (🔶, no source read): crescent 9.2 cm across, roll up to 7.5 mm thick, fringe 8 cm, 32 cords of 5.4 mm.
#   blender -b --factory-startup --python build_casaca_elite_fr.py -- <French coat LOD0 .blend> <out .blend>
#                                                                     [cordoes=32] [franja=0.080]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
NCORD = int(OPT.get("cordoes", 32))
FRINGE = float(OPT.get("franja", 0.080))
GROUND = -1.0069
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Fr1812_01_LOD0"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
ob.name = "HCL_U_Fr1812_Elite_LOD0"
ob.data = ob.data.copy(); ob.data.name = "HCL_U_Fr1812_Elite_LOD0"
parts = ob["hcl_partes"].split(",")
NEW = [f"dragona_{k}_{s}" for k in ("corpo", "meialua", "franja") for s in "ED"]
parts += NEW
PID = {n: i for i, n in enumerate(parts)}
mat = bpy.data.materials.new("HCL_la_dragona")
ob.data.materials.append(mat)
MI = len(ob.data.materials) - 1
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
uvl = bm.loops.layers.uv.active
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
rng = np.random.default_rng(1812)
DENS = 0.50                                                   # UV units per metre for the epaulettes (coat: 0.402)


def bvh(names, sx):
    vs = list(bm.verts)
    idx = {v: i for i, v in enumerate(vs)}
    ids = {PID[n] for n in names}
    tris = []
    for f in bm.faces:
        if f[PL] in ids and f.calc_center_median().x * sx > 0:
            q = [idx[v] for v in f.verts]
            for t in range(1, len(q) - 1):
                tris.append([q[0], q[t], q[t + 1]])
    return BVHTree.FromPolygons([v.co.copy() for v in vs], tris)


def new_face(vs, part, uvs):
    f = bm.faces.new(vs)
    f[PL] = PID[part]; f.material_index = MI
    for l, uv in zip(f.loops, uvs):
        l[uvl].uv = uv
    return f


def orient(f, outward):
    f.normal_update()
    if f.normal.dot(outward) < 0:
        f.normal_flip()


# ---------------------------------------------------------------- UV areas in the free top strip
UVR = {}
DENS_C = 0.42                                               # along the cords (they are the longest pieces)
CORD_W, CORD_H = 0.0058, FRINGE * 1.12 * DENS_C             # one cord: 3 faces around, its length (longest cord)
UVR["franja_cordoes"] = [0.004, 0.957, CORD_W, 0.0062]    # u0, v0, cord width, step between cords
UVR["franja_cortina_E"] = [0.004, 0.932, 0.090, 0.022]    # u0, v0, width, height
UVR["franja_cortina_D"] = [0.100, 0.932, 0.090, 0.022]
UVR["meialua_E"] = [0.200, 0.932, 0.090, 0.021]
UVR["meialua_D"] = [0.300, 0.932, 0.090, 0.021]
UVR["corpo_E"] = [0.430, 0.948]                            # origin of the planar map (s, t) * DENS
UVR["corpo_D"] = [0.490, 0.948]
UVR["corpo_parede_E"] = [0.550, 0.932, 0.003]               # u0, v0, wall height in UV
UVR["corpo_parede_D"] = [0.550, 0.940, 0.003]
assert 0.004 + 2 * NCORD * 0.0062 < 0.425 and 0.957 + CORD_H < 0.997, "cords do not fit the free strip"

report = []
for s, sx in (("E", 1.0), ("D", -1.0)):
    # ------------------------------------------------------------ frame at the tongue's outer end
    pv = sorted({v for f in bm.faces if f[PL] == PID[f"platina_{s}"] for v in f.verts}, key=lambda v: v.index)
    P = np.array([v.co[:] for v in pv])
    xo = np.abs(P[:, 0]).max()
    end = P[np.abs(np.abs(P[:, 0]) - xo) < 0.002]
    tops = []
    for y in np.unique(np.round(end[:, 1], 4)):                # top vertex of each column of the end wall
        col = end[np.abs(end[:, 1] - y) < 1e-4]
        tops.append(col[col[:, 2].argmax()])
    O = Vector(np.mean(tops, axis=0))
    inner = P[np.abs(P[:, 0]) < np.abs(P[:, 0]).min() + 0.004]
    I0 = Vector(inner.mean(axis=0))
    tongue_w = float(np.ptp(np.array(tops)[:, 1]))
    SURF = bvh(["casaco_corpo", f"manga_{s}"], sx)
    SURF_T = bvh(["casaco_corpo", f"manga_{s}", f"platina_{s}"], sx)
    hit = SURF.ray_cast(O + Vector((0, 0, 0.10)), Vector((0, 0, -1)), 0.3)
    n0 = hit[1] if hit[1].z > 0 else -hit[1]
    ax = (O - I0); ax = (ax - n0 * ax.dot(n0)).normalized()
    wv = n0.cross(ax).normalized()
    if wv.y < 0:
        wv = -wv                                               # t > 0 toward the back on both sides
    lift = (O - hit[0]).dot(n0)
    report.append(f"DRAGONA {s}: lingua {(O - I0).length * 100:.1f} cm, largura {tongue_w * 100:.1f} cm, ponta "
                  f"({O.x:+.3f}, {O.y:+.3f}, {O.z - GROUND:.3f}) a {lift * 1000:.1f} mm do pano; normal "
                  f"({n0.x:+.2f}, {n0.y:+.2f}, {n0.z:+.2f}), eixo ({ax.x:+.2f}, {ax.y:+.2f}, {ax.z:+.2f})")

    def to3(sv, tv):
        return O + ax * sv + wv * tv

    def drop(sv, tv, tree=SURF_T, extra=0.004):
        """Point of the shape (s, t) dropped onto the shoulder along -n0, `extra` above what it lands on."""
        p = to3(sv, tv)
        h = tree.ray_cast(p + n0 * 0.12, -n0, 0.4)
        if h[0] is None:
            raise RuntimeError(f"dragona {s}: nada sob ({sv:.3f}, {tv:.3f})")
        nn = h[1] if h[1].dot(n0) > 0 else -h[1]
        return h[0] + nn * extra, h[0], nn

    # ------------------------------------------------------------ body (palette): outline, rings, walls
    S0, SC, A_, B_ = -0.012, 0.028, 0.040, 0.046               # neck start, crescent centre, half-ellipse semi-axes
    hw0 = max(tongue_w / 2 + 0.001, 0.024)
    outline = []                                               # closed, counter-clockwise in (s, t)
    for k in range(4):                                         # neck edge, front to back (on the tongue)
        outline.append((S0, -hw0 + 2 * hw0 * k / 3))
    for k in range(1, 4):                                      # back side, neck to crescent start
        u = k / 3
        outline.append((S0 + (SC - S0) * u, hw0 + (B_ - hw0) * (u * u * (3 - 2 * u))))
    NA = 18
    arc = [(SC + A_ * math.cos(th), B_ * math.sin(th)) for th in np.linspace(math.pi / 2, -math.pi / 2, NA + 1)]
    outline += arc[1:]
    for k in range(1, 3):                                      # front side, crescent start back to the neck
        u = 1 - k / 3
        outline.append((S0 + (SC - S0) * u, -(hw0 + (B_ - hw0) * (u * u * (3 - 2 * u)))))
    PC = (SC - 0.004, 0.0)
    # the body is stiffened cloth: one smooth surface, not a copy of every dip of the cloth and of the tongue's end
    # wall under it (first try: dents at the tongue's end). A global cubic fit cleared everything but floated up to
    # 17 mm at the back edge (a box on the shoulder). So: height field over the shoulder on a grid along n0, relaxed
    # (Laplacian) while never coming closer than CLR to what is under it; bilinear between grid nodes
    CLR = 0.0035
    GS = np.linspace(S0 - 0.006, SC + A_ + 0.006, 34)
    GT = np.linspace(-B_ - 0.006, B_ + 0.006, 34)
    floor_ = np.array([[(drop(sv, tv, extra=0.0)[1] - O).dot(n0) + CLR for tv in GT] for sv in GS])
    hgrid = floor_.copy()
    for _ in range(120):
        sm = hgrid.copy()
        sm[1:-1, 1:-1] = (hgrid[:-2, 1:-1] + hgrid[2:, 1:-1] + hgrid[1:-1, :-2] + hgrid[1:-1, 2:]) / 4
        hgrid = np.maximum(sm, floor_)

    def hval(sv, tv, H):
        i = min(max(np.searchsorted(GS, sv) - 1, 0), len(GS) - 2)
        j = min(max(np.searchsorted(GT, tv) - 1, 0), len(GT) - 2)
        fs, ft = (sv - GS[i]) / (GS[i + 1] - GS[i]), (tv - GT[j]) / (GT[j + 1] - GT[j])
        return float(H[i, j] * (1 - fs) * (1 - ft) + H[i + 1, j] * fs * (1 - ft) + H[i, j + 1] * (1 - fs) * ft + H[i + 1, j + 1] * fs * ft)

    def top(sv, tv, extra=0.0):
        """Point on the body's smooth top surface (plus `extra` along n0)."""
        return O + ax * sv + wv * tv + n0 * (hval(sv, tv, hgrid) + extra)

    gap = (hgrid - floor_ + CLR)[2:-2, 2:-2]
    report.append(f"   corpo rigido: superficie alisada a >= {CLR * 1000:.1f} mm do que esta sob ela; folga media "
                  f"{gap.mean() * 1000:.1f} mm, maxima {gap.max() * 1000:.1f} mm")

    RINGS = (1.0, 0.72, 0.45, 0.20)
    grid = []
    for r in RINGS:
        row = []
        for (sv, tv) in outline:
            ss, tt = PC[0] + (sv - PC[0]) * r, PC[1] + (tv - PC[1]) * r
            row.append((bm.verts.new(top(ss, tt)), ss, tt))
        grid.append(row)
    vc = bm.verts.new(top(*PC))
    part = f"dragona_corpo_{s}"
    u0c, v0c = UVR[f"corpo_{s}"]
    uvp = lambda ss, tt: (u0c + (tt + B_) * DENS, v0c + (ss - S0) * DENS)
    M = len(outline)
    faces_c = []
    for r in range(len(RINGS) - 1):
        for k in range(M):
            k2 = (k + 1) % M
            a1, a2, b1, b2 = grid[r][k], grid[r][k2], grid[r + 1][k2], grid[r + 1][k]
            faces_c.append(new_face([a1[0], a2[0], b1[0], b2[0]], part, [uvp(x[1], x[2]) for x in (a1, a2, b1, b2)]))
    last = grid[-1]
    for k in range(M):
        k2 = (k + 1) % M
        faces_c.append(new_face([last[k][0], last[k2][0], vc], part,
                                [uvp(last[k][1], last[k][2]), uvp(last[k2][1], last[k2][2]), uvp(*PC)]))
    for f in faces_c:
        orient(f, n0)
    # the tongue's end lies under the body's neck; its corners stuck through the body's faces (the body's flat faces
    # lie under the smooth surface between its vertices). Every tongue vertex under the body is kept 2.5 mm under
    # the body's actual faces (hidden there, so nothing visible is lost)
    lst = list(bm.verts)
    li = {v: i for i, v in enumerate(lst)}
    ptree = BVHTree.FromPolygons([v.co.copy() for v in lst], [[li[v] for v in f.verts] for f in faces_c])
    n_cl = 0
    for v in pv:
        h_ = ptree.ray_cast(v.co - n0 * 0.05, n0, 0.10)
        if h_[0] is not None and (h_[0] - v.co).dot(n0) < 0.0025:
            v.co -= n0 * (0.0025 - (h_[0] - v.co).dot(n0)); n_cl += 1
    report.append(f"   lingua: {n_cl} vertices da ponta baixados para ficar 2,5 mm sob o corpo")
    # rim wall down to whatever is under it (shoulder cloth or the tongue), 1 mm into it
    wu0, wv0, wh = UVR[f"corpo_parede_{s}"]
    run = 0.0
    foot = []
    for (v_, ss, tt) in grid[0]:
        _, base, nn = drop(ss, tt, extra=0.0)
        foot.append(bm.verts.new(base - nn * 0.001))
    for k in range(M):
        k2 = (k + 1) % M
        ta, tb = grid[0][k][0], grid[0][k2][0]
        L = (tb.co - ta.co).length
        f = new_face([ta, foot[k], foot[k2], tb], part,
                     [(wu0 + run * DENS * 0.5, wv0 + wh), (wu0 + run * DENS * 0.5, wv0),
                      (wu0 + (run + L) * DENS * 0.5, wv0), (wu0 + (run + L) * DENS * 0.5, wv0 + wh)])
        orient(f, f.calc_center_median() - vc.co)
        run += L
    ntri_c = sum(len(f.verts) - 2 for f in faces_c) + 2 * M

    # ------------------------------------------------------------ crescent: tapered padded roll on the rim
    part = f"dragona_meialua_{s}"
    NSEG, NSIDE = 22, 8
    ths = np.linspace(math.pi / 2 + 0.16, -math.pi / 2 - 0.16, NSEG + 1)
    RC = 0.0075
    cen, rad = [], []
    for th in ths:
        c_ = abs(math.cos(min(abs(th), math.pi / 2)))
        r_ = RC * (0.62 + 0.38 * c_ ** 0.6)
        ss, tt = SC + (A_ - r_ * 0.5) * math.cos(th), (B_ - r_ * 0.5) * math.sin(th)
        p, nn = top(ss, tt, extra=r_ * 0.60), n0
        q, m, _, _ = SURF.find_nearest(p)
        if (p - q).dot(m) < r_ + 0.0012:                       # ends of the roll where the shoulder falls away
            p = q + m * (r_ + 0.0012)
        cen.append((p, nn)); rad.append(r_)
    u0m, v0m, wm, hm = UVR[f"meialua_{s}"]
    ring_v = []
    for j, ((p, nn), r_) in enumerate(zip(cen, rad)):
        tng = (cen[min(j + 1, NSEG)][0] - cen[max(j - 1, 0)][0]).normalized()
        nrm_ = (nn - tng * nn.dot(tng)).normalized()
        bin_ = tng.cross(nrm_)
        ring_v.append([bm.verts.new(p + (nrm_ * math.cos(2 * math.pi * i / NSIDE) + bin_ * math.sin(2 * math.pi * i / NSIDE)) * r_)
                       for i in range(NSIDE)])
    faces_m = []
    for j in range(NSEG):
        for i in range(NSIDE):
            i2 = (i + 1) % NSIDE
            uvs = [(u0m + j / NSEG * wm, v0m + i / NSIDE * hm), (u0m + (j + 1) / NSEG * wm, v0m + i / NSIDE * hm),
                   (u0m + (j + 1) / NSEG * wm, v0m + (i + 1) / NSIDE * hm), (u0m + j / NSEG * wm, v0m + (i + 1) / NSIDE * hm)]
            f = new_face([ring_v[j][i], ring_v[j + 1][i], ring_v[j + 1][i2], ring_v[j][i2]], part, uvs)
            orient(f, f.calc_center_median() - (cen[j][0] + cen[j + 1][0]) / 2)
            faces_m.append(f)
    for j, sgn in ((0, -1), (NSEG, 1)):                        # rounded caps
        tng = (cen[j][0] - cen[j - sgn][0]).normalized() if j else (cen[0][0] - cen[1][0]).normalized()
        tip = bm.verts.new(cen[j][0] + tng * rad[j] * 0.8)
        for i in range(NSIDE):
            i2 = (i + 1) % NSIDE
            uu = u0m + (0 if j == 0 else wm)
            f = new_face([ring_v[j][i], ring_v[j][i2], tip], part,
                         [(uu, v0m + i / NSIDE * hm), (uu, v0m + (i + 1) / NSIDE * hm), (uu, v0m + hm * 0.5)])
            orient(f, f.calc_center_median() - cen[j][0])
            faces_m.append(f)

    # ------------------------------------------------------------ fringe: cords draped over the sleeve head
    part = f"dragona_franja_{s}"
    NS_ = 6
    RCORD = 0.0027
    gvec = Vector((0, 0, -1))
    cords = []
    cu0, cv0, cw, cstep = UVR["franja_cordoes"]
    for k, th in enumerate(np.linspace(math.pi / 2 + 0.06, -math.pi / 2 - 0.06, NCORD)):
        ss, tt = SC + (A_ + 0.0005) * math.cos(th), (B_ + 0.0005) * math.sin(th)
        root, nn = top(ss, tt, extra=-0.0015), n0
        q, m, _, _ = SURF.find_nearest(root)
        if (root - q).dot(m) < RCORD + 0.0012:                  # where the shoulder falls away under the rim
            root = q + m * (RCORD + 0.0012)
        d = (ax * math.cos(th) + wv * math.sin(th))
        d = (d - nn * d.dot(nn)).normalized()
        L = FRINGE * (1 + 0.05 * (rng.random() * 2 - 1)) * (0.94 + 0.06 * abs(math.cos(th)))
        sway = wv * float(rng.normal(0, 1)) + ax * float(rng.normal(0, 0.5))           # cords never hang alike
        seg = L / NS_
        pts, nrms = [root], [nn]
        p, prev = root, root
        for j in range(1, NS_ + 1):
            q, m, _, _ = SURF.find_nearest(p)
            # (coat and sleeve faces point outward: no flipping by the previous point, which sent cords inside)
            gt = gvec - m * gvec.dot(m)
            if gt.length > 1e-6:
                d = (d * (0.55 if j == 1 else 0.35) + gt.normalized() + sway * (0.12 if j > 1 else 0.0)).normalized()
            p = p + d * seg
            q, m, _, _ = SURF.find_nearest(p)
            m = m.normalized()
            off = 0.0035 + 0.0030 * j / NS_ + 0.0012 * (rng.random() - 0.5)
            p = q + m * off
            d = (p - prev).normalized()
            pts.append(p); nrms.append(m); prev = p
        cords.append((pts, nrms, L))
    faces_f = []
    for k, (pts, nrms, L) in enumerate(cords):
        cu = cu0 + (k + (NCORD if s == "D" else 0)) * cstep
        rings = []
        for j, (p, m) in enumerate(zip(pts, nrms)):
            tng = (pts[min(j + 1, NS_)] - pts[max(j - 1, 0)]).normalized()
            m_ = (m - tng * m.dot(tng)).normalized()
            b_ = tng.cross(m_)
            rr = RCORD * (1.0 if j < NS_ else 0.85)
            rings.append([bm.verts.new(p + (m_ * math.cos(2 * math.pi * i / 3) + b_ * math.sin(2 * math.pi * i / 3)) * rr)
                          for i in range(3)])
        vlen = [0.0]
        for j in range(1, len(pts)):
            vlen.append(vlen[-1] + (pts[j] - pts[j - 1]).length)
        for j in range(NS_):
            for i in range(3):
                i2 = (i + 1) % 3
                uvs = [(cu + i / 3 * CORD_W, cv0 + vlen[j] * DENS_C), (cu + i / 3 * CORD_W, cv0 + vlen[j + 1] * DENS_C),
                       (cu + (i + 1) / 3 * CORD_W, cv0 + vlen[j + 1] * DENS_C), (cu + (i + 1) / 3 * CORD_W, cv0 + vlen[j] * DENS_C)]
                f = new_face([rings[j][i], rings[j + 1][i], rings[j + 1][i2], rings[j][i2]], part, uvs)
                orient(f, f.calc_center_median() - (pts[j] + pts[j + 1]) / 2)
                faces_f.append(f)
        tng = (pts[-1] - pts[-2]).normalized()
        tip = bm.verts.new(pts[-1] + tng * RCORD * 1.3)
        for i in range(3):
            i2 = (i + 1) % 3
            f = new_face([rings[-1][i], rings[-1][i2], tip], part,
                         [(cu + i / 3 * CORD_W, cv0 + vlen[-1] * DENS_C), (cu + (i + 1) / 3 * CORD_W, cv0 + vlen[-1] * DENS_C),
                          (cu + (i + 0.5) / 3 * CORD_W, cv0 + (vlen[-1] + RCORD) * DENS_C)])
            orient(f, f.calc_center_median() - pts[-1])
            faces_f.append(f)
    # under-curtain: joins the cord centre lines 2 mm closer to the cloth over the top third only (it fills the roots;
    # longer, it showed as a dark sheet where the cords fan out over the back of the shoulder)
    u0k, v0k, wk, hk = UVR[f"franja_cortina_{s}"]
    NJ = 2
    cv = [[bm.verts.new(pts[j] - nrms[j] * 0.0021) for j in range(NJ + 1)] for pts, nrms, L in cords]
    for k in range(NCORD - 1):
        for j in range(NJ):
            uvs = [(u0k + k / (NCORD - 1) * wk, v0k + hk - j / NJ * hk), (u0k + (k + 1) / (NCORD - 1) * wk, v0k + hk - j / NJ * hk),
                   (u0k + (k + 1) / (NCORD - 1) * wk, v0k + hk - (j + 1) / NJ * hk), (u0k + k / (NCORD - 1) * wk, v0k + hk - (j + 1) / NJ * hk)]
            f = new_face([cv[k][j], cv[k + 1][j], cv[k + 1][j + 1], cv[k][j + 1]], part, uvs)
            orient(f, cords[k][1][j] + cords[k + 1][1][j])
            faces_f.append(f)
    tips = [c[0][-1] for c in cords]
    drop_z = [(c[0][0].z - c[0][-1].z) for c in cords]
    report.append(f"   corpo {M} pontos de contorno, {ntri_c} triangulos; meia-lua {NSEG}x{NSIDE}, raio {rad[0] * 1000:.1f}.."
                  f"{max(rad) * 1000:.1f} mm; franja {NCORD} cordoes de {2 * RCORD * 1000:.1f} mm, {FRINGE * 100:.1f} cm "
                  f"(+-6%), queda {min(drop_z) * 100:.1f}..{max(drop_z) * 100:.1f} cm; ponta mais baixa a "
                  f"{min(t.z for t in tips) - GROUND:.3f} m")

bm.normal_update()
bm.to_mesh(ob.data)
ob.data.update()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_dragona_uv"] = json.dumps({"dens": DENS, "dens_c": DENS_C, "cord_w": CORD_W, "ncord": NCORD, "rects": UVR})
ob["hcl_origem"] = ("HCL_U_Fr1812_01_LOD0 (build_uniforme_fr.py) com dragonas de elite por build_casaca_elite_fr.py, "
                    "2026-10-12")
for r in report:
    print(r)
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print(f"CASACA ELITE: {len(ob.data.vertices)} vertices, {tris} triangulos (a de fuzileiro tem 12448)")

# ---------------------------------------------------------------- checks
me = ob.data
pa = me.attributes["hcl_part"].data
uv = me.uv_layers.active.data
newp = {PID[n] for n in NEW}
nu = [uv[li].uv[:] for p in me.polygons if pa[p.index].value in newp for li in p.loop_indices]
print(f"UV dragonas: u {min(u for u, v in nu):.3f}..{max(u for u, v in nu):.3f}  v {min(v for u, v in nu):.3f}..{max(v for u, v in nu):.3f}")
old = [uv[li].uv[:] for p in me.polygons if pa[p.index].value not in newp and parts[pa[p.index].value] != "maos_template"
       for li in p.loop_indices]
print(f"UV de outras pecas na faixa das dragonas (v > 0.93, u < 0.60): {sum(1 for u, v in old if v > 0.93 and u < 0.60)} cantos")
# epaulette points inside the cloth: nearest coat/sleeve face, signed by that face's own (outward) normal
bmc = bmesh.new(); bmc.from_mesh(me)
PLc = bmc.faces.layers.int.get("hcl_part")
for s, sx in (("E", 1), ("D", -1)):
    host = [f for f in bmc.faces if f[PLc] in (PID["casaco_corpo"], PID[f"manga_{s}"]) and f.calc_center_median().x * sx > 0]
    vs = list(bmc.verts)
    tree = BVHTree.FromPolygons([v.co for v in vs], [[v.index for v in f.verts] for f in host])
    msg = []
    for k in ("corpo", "meialua", "franja"):
        ids = {v.index for f in bmc.faces if f[PLc] == PID[f"dragona_{k}_{s}"] for v in f.verts}
        worst, nin = 0.0, 0
        for i in ids:
            p = vs[i].co
            q, n, fi, dist = tree.find_nearest(p)
            if (p - q).dot(n) < -1e-5 and dist < 0.02:
                nin += 1; worst = max(worst, dist)
        msg.append(f"{k} {nin}/{len(ids)} (pior {worst * 1000:.1f} mm)")
    print(f"DENTRO DO PANO {s}: " + ", ".join(msg) + " (os pes da parede do corpo entram 1 mm de proposito)")
bmc.free()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
