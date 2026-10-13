# Phase 4: production mesh of the Prussian line infantry 1813 uniform (HCL_U_Pruss1813_01), Resolution 1 (LOD 0).
# Built from the approved blockout parameters (docs/reports/uniforme_pruss_blockout.md) on the official Arma 3 body,
# in character space. One object, one island per garment piece; hands taken unchanged from the official template
# (A3_character_template.p3d: geometry, UVs and bone weights).
#
# Realism added over the blockout: cloth thickness and turned hems on every visible edge, collar with a rolled top,
# front overlap of the button stand, waist shaping, elbow compression folds and slack, tails with lining, red
# turnbacks, drape and back pleats, trousers bunching over the gaiters, gaiter side strip, shoes with welt, sole and
# heel, domed buttons, shoulder boards with a rounded end.
#
#   blender -b --factory-startup --python build_uniforme_production.py -- <Samples Test_Character_01 dir> <shako LOD0 .blend> <out .blend> <out img dir> [norender]
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uniform_fit import (Body, UP, FRONT, profile, fill_and_smooth, radius, fpoint, theta_of, frame_centre,
                         vertical_frames, polyline_at, polyline_length, axis_frames, smoothstep, gauss, angdiff,
                         loft, dome)
from p3d_mlod import read_mlod, to_blender

_args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, SHAKO_BLEND, OUT_BLEND, OUT_IMG = _args[:4]
RENDER = "norender" not in _args[4:]
os.makedirs(OUT_IMG, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

B = Body(os.path.join(SAMPLES, "A3_character_example.p3d"))
J = B.joints()
Z = B.Z

S = dict(
    waist=1.12, coat_bottom=1.105, tails_top=1.14, tails=0.70,
    collar_base=1.535, collar_h=0.055,
    cuff_h=0.075, flap_len=0.11, flap_w=0.04,
    strap_len=0.13, strap_w=0.05,
    gaiter_top=0.42, gaiter_bottom=0.075,
    ease_coat=0.012, ease_sleeve=0.018, ease_sleeve_end=0.010, ease_cuff=0.0145,
    ease_trousers=0.018, ease_gaiter=0.012, ease_shoe=0.006,
    cloth=0.004,                                   # thickness shown at the cloth edges
)
TORSO = {"pelvis", "spine", "spine1", "spine2", "spine3", "neck", "head", "leftshoulder", "rightshoulder"}
ARM = {s: {f"{p}arm", f"{p}armroll", f"{p}forearm", f"{p}forearmroll"} for s, p in ((1, "left"), (-1, "right"))}
LEG = {s: {f"{p}upleg", f"{p}uplegroll", f"{p}leg", f"{p}legroll"} for s, p in ((1, "left"), (-1, "right"))}
FOOT = {s: {f"{p}foot", f"{p}toebase"} for s, p in ((1, "left"), (-1, "right"))}

# ---------------------------------------------------------------- materials (names reused in Phases 6–7)
MATS = [("HCL_la_azul", (0.024, 0.040, 0.105), 0.85, 0), ("HCL_la_vermelha", (0.33, 0.016, 0.020), 0.85, 0),
        ("HCL_la_branca", (0.72, 0.71, 0.67), 0.85, 0), ("HCL_la_cinza", (0.15, 0.148, 0.140), 0.9, 0),
        ("HCL_polaina_preta", (0.018, 0.018, 0.018), 0.8, 0), ("HCL_couro_sapato", (0.012, 0.010, 0.009), 0.4, 0),
        ("HCL_sola", (0.035, 0.022, 0.014), 0.7, 0), ("HCL_latao", (0.62, 0.43, 0.13), 0.35, 1),
        ("HCL_pele_hl", (0.80, 0.60, 0.48), 0.7, 0)]
AZUL, VERM, BRANCO, CINZA, POLAINA, SAPATO, SOLA, LATAO, PELE = range(len(MATS))

bm = bmesh.new()
PART = bm.faces.layers.int.new("hcl_part")
PART_NAMES = []
_part_start = [0]


def begin(name):
    PART_NAMES.append(name)
    bm.faces.ensure_lookup_table()
    _part_start[0] = len(bm.faces)


def end():
    bm.faces.ensure_lookup_table()
    pid = len(PART_NAMES) - 1
    out = []
    for i in range(_part_start[0], len(bm.faces)):
        bm.faces[i][PART] = pid
        out.append(bm.faces[i])
    return out


def orient_island(faces, probe_face, outward_from):
    """Make normals consistent over a shell, then outward (probe face points away from outward_from)."""
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    probe_face.normal_update()
    if probe_face.normal.dot(probe_face.calc_center_median() - outward_from) < 0:
        bmesh.ops.reverse_faces(bm, faces=faces)


def frame_at_h(frames, hs, h):
    """Interpolated vertical frame at height h (frames share orientation)."""
    order = sorted(range(len(hs)), key=lambda k: hs[k])
    H = [hs[k] for k in order]
    F = [frames[k] for k in order]
    if h <= H[0]:
        f0, f1, t = F[0], F[0], 0.0
    elif h >= H[-1]:
        f0, f1, t = F[-1], F[-1], 0.0
    else:
        j = max(k for k in range(len(H)) if H[k] <= h)
        f0, f1 = F[j], F[min(j + 1, len(F) - 1)]
        t = 0.0 if f1 is f0 else (h - H[j]) / (H[j + 1] - H[j])
    return dict(o=Vector((0, 0, Z(h))), a=UP, u=f0["u"], v=f0["v"], c=f0["c"].lerp(f1["c"], t),
                r=[a * (1 - t) + b * t for a, b in zip(f0["r"], f1["r"])])


def solve_theta_x(fr, ease_fn, x_target, th0=0.0, span=0.9):
    """Angle near th0 where the ring point has the given x (bisection)."""
    lo, hi = th0 - span, th0 + span
    f = lambda th: fpoint(fr, th, ease_fn(th)).x - x_target
    flo = f(lo)
    for _ in range(40):
        mid = (lo + hi) / 2
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


# =============================================================== 1. coat body, yoke, collar
torso_idx = B.group_idx(TORSO | ARM[1] | ARM[-1])
xlim = abs(J[("shoulder", 1)].x) + 0.05
hs_c = [1.108] + [1.13 + k * 0.025 for k in range(15) if 1.13 + k * 0.025 <= 1.4801] + [1.50]
coat_fr = vertical_frames(B, torso_idx, hs_c, xlim=xlim)
THC = -0.18                                        # closure line (x = -0.025 at the chest), viewer's left of the buttons
TH_COAT = sorted({round((2 * math.pi * i / 32) % (2 * math.pi), 6) for i in range(32)}
                 | {round((THC - 0.012) % (2 * math.pi), 6), round((THC + 0.012) % (2 * math.pi), 6)})


def coat_ease(th, h):
    e = S["ease_coat"]
    d = angdiff(th, THC)
    if 0 < d < 0.9:                                # button stand overlaps the other front by 1.8 mm
        e += 0.0018 * (1 - smoothstep(0.5, 0.9, d))
    e -= 0.003 * gauss(h, 1.14, 0.03)              # waist shaping
    return e


neck_idx = B.group_idx({"neck", "spine3", "head"})
neck_pts = B.section(neck_idx, Vector((0, 0, Z(1.555))), UP, xlim=0.10)
collar_fr = profile(neck_pts, Vector((0, 0, Z(S["collar_base"]))), UP)
collar_base = []
for th in TH_COAT:
    p = fpoint(collar_fr, th, 0.010)
    zb = B.top(p.x, p.y)
    collar_base.append(Vector((p.x, p.y, max(Z(S["collar_base"]), (zb if zb is not None else -9) + 0.004))))

begin("casaco_corpo")
rings, cen = [], []
for h, de in ((1.124, -0.0045), (1.1035, -0.0015)):        # turned hem at the visible front edge
    fr = frame_at_h(coat_fr, hs_c, h)                       # profile of its own height (else it pokes out)
    rings.append([fpoint(fr, th, coat_ease(th, h) + de) for th in TH_COAT])
    cen.append(frame_centre(fr))
for h, fr in zip(hs_c, coat_fr):
    rings.append([fpoint(fr, th, coat_ease(th, h)) for th in TH_COAT])
    cen.append(frame_centre(fr))
outer = rings[-1]
for k in range(1, 5):                                       # yoke over the shoulders to the collar base
    t = k / 4
    ring = []
    for p_out, p_in in zip(outer, collar_base):
        q = p_out.lerp(p_in, t)
        zb = B.top(q.x, q.y)
        ring.append(Vector((q.x, q.y, q.z if zb is None else max(q.z, zb + (S["ease_coat"] if t < 1 else 0.004)))))
    rings.append(ring)
    cen.append(cen[-1].lerp(frame_centre(collar_fr), t))
loft(bm, rings, orient_centres=cen, orient_band=3)
coat_faces = end()

begin("gola")
crings, ccen = [], []
for i_ring, (kind, de) in enumerate((("base", 0.010), ("top", 0.0135), ("roll", 0.0112), ("top", 0.0085), ("base", 0.0075))):
    ring = []
    for i, th in enumerate(TH_COAT):
        z_top = Z(S["collar_base"] + S["collar_h"]) + 0.005 * -math.cos(th)
        z0 = collar_base[i].z - 0.004
        z = z0 if kind == "base" else max(z_top, z0 + 0.03) + (0.0025 if kind == "roll" else 0.0)
        p = fpoint(collar_fr, th, de)
        ring.append(Vector((p.x, p.y, z)))
    crings.append(ring)
    ccen.append(frame_centre(collar_fr))
CV = loft(bm, crings, mat_of=lambda k, i: VERM)
nC = len(TH_COAT)
for i in range(nC):                                          # close the band under the collar: a closed ring
    j = (i + 1) % nC
    f_ = bm.faces.new((CV[4][i], CV[4][j], CV[0][j], CV[0][i]))
    f_.material_index = VERM
collar_faces = end()
outer_probe = next(f for f in collar_faces if set(f.verts) <= set(CV[0]) | set(CV[1]))
orient_island(collar_faces, outer_probe, frame_centre(collar_fr) + Vector((0, 0, 0.03)))

# =============================================================== 2. sleeves, cuffs, Brandenburg flaps
N_SL = 18
TH_SL = [2 * math.pi * i / N_SL for i in range(N_SL)]
cuff_data = {}
for s in (1, -1):
    sh, el, wr = J[("shoulder", s)], J[("elbow", s)], J[("wrist", s)]
    start = sh - (el - sh).normalized() * 0.05
    end_ = wr + (wr - el).normalized() * 0.012
    P = [start, el, end_]
    L = polyline_length(P)
    s_el = (el - start).length
    s_top = L - S["cuff_h"]
    s_list, x = [], 0.0
    while x < s_top + 0.02:
        s_list.append(x)
        x += 0.02 if abs(x - s_el) < 0.07 else 0.03
    s_list = sorted(set(round(v, 4) for v in s_list + [s_top - 0.01, s_top + 0.02]))
    s_list = [v for v in s_list if v <= s_top + 0.02]
    idx = B.group_idx(ARM[s] | B.hand[s] | {("left" if s > 0 else "right") + "shoulder"}, side=s)
    fr = axis_frames(B, idx, P, s_list, 0.10)
    th_in = {}

    def sleeve_ease(si, th, f):
        e = S["ease_sleeve"] + (S["ease_sleeve_end"] - S["ease_sleeve"]) * smoothstep(L - 0.30, s_top, si)
        e -= 0.016 * (1 - smoothstep(0.0, 0.07, si))                    # sleeve head tucked under the coat
        crease = theta_of(f, FRONT - f["a"] * FRONT.dot(f["a"]))      # inner elbow faces forward in the A pose
        w_in = max(0.0, math.cos(angdiff(th, crease))) ** 2
        w_out = max(0.0, math.cos(angdiff(th, crease + math.pi))) ** 2
        e += 0.0035 * gauss(si, s_el, 0.045) * (0.5 + 0.5 * math.cos(2 * math.pi * (si - s_el) / 0.03)) * w_in
        e += 0.003 * gauss(si, s_el + 0.01, 0.06) * w_out                # slack over the elbow
        return e

    begin(f"manga_{'E' if s > 0 else 'D'}")
    loft(bm, [[fpoint(f, th, sleeve_ease(si, th, f)) for th in TH_SL] for si, f in zip(s_list, fr)],
         mat_of=lambda k, i: AZUL, orient_centres=[frame_centre(f) for f in fr], orient_band=len(fr) // 2)
    end()

    # cuff: tuck under the top edge, outer wall, rolled bottom edge, inner hem
    def cuff_frame(si, P=P, idx=idx, fr=fr):          # defaults bind this side's data (used after the loop)
        o, d = polyline_at(P, si)
        f = profile(B.section(idx, o, d, rmax=0.10), o, d)
        return f if f["c"] is not None else fr[-1]
    ec = S["ease_cuff"]
    spec_c = [(s_top, 0.0085), (s_top + 0.003, ec), (s_top + S["cuff_h"] / 2, ec), (L - 0.003, ec),
              (L, ec - 0.002), (L - 0.015, ec - 0.004)]
    cfr = [cuff_frame(si) for si, _ in spec_c]
    begin(f"punho_{'E' if s > 0 else 'D'}")
    loft(bm, [[fpoint(f, th, e) for th in TH_SL] for f, (_, e) in zip(cfr, spec_c)],
         mat_of=lambda k, i: VERM, orient_centres=[frame_centre(f) for f in cfr], orient_band=2)
    end()

    # Brandenburg flap: flat panel over the cuff, running up onto the sleeve, walls down to the cloth
    out_dir = Vector((s, 0, 0))
    begin(f"pala_{'E' if s > 0 else 'D'}")
    rows_top, rows_bot = [], []
    for q in range(6):
        si = L - 0.012 - S["flap_len"] * q / 5
        f = cuff_frame(si)
        th_o = theta_of(f, out_dir - f["a"] * out_dir.dot(f["a"]))
        e_base = ec if si >= s_top else sleeve_ease(si, th_o, f)
        r = radius(f, th_o) + ec + 0.0025
        dth = (S["flap_w"] / 2) / r
        rows_top.append([fpoint(f, th_o + dth * (c - 1), ec + 0.0025) for c in range(3)])
        rows_bot.append([fpoint(f, th_o + dth * (c - 1), e_base - 0.003) for c in range(3)])   # below the facets
    fs = []
    VT = [[bm.verts.new(p) for p in r] for r in rows_top]
    VB = [[bm.verts.new(p) for p in r] for r in rows_bot]
    for k in range(5):
        for c in range(2):
            fs.append(bm.faces.new((VT[k][c], VT[k][c + 1], VT[k + 1][c + 1], VT[k + 1][c])))
        fs.append(bm.faces.new((VT[k][0], VT[k + 1][0], VB[k + 1][0], VB[k][0])))
        fs.append(bm.faces.new((VT[k][2], VB[k][2], VB[k + 1][2], VT[k + 1][2])))
    for k in (0, 5):
        for c in range(2):
            fs.append(bm.faces.new((VT[k][c], VB[k][c], VB[k][c + 1], VT[k][c + 1])))
    for f_ in fs:
        f_.material_index = AZUL
    orient_island(fs, fs[0], frame_centre(cuff_frame(L - 0.04)))
    end()
    cuff_data[s] = (P, L, s_top, cuff_frame, ec, out_dir)

# =============================================================== 3. tails: outer cloth, red lining, edges, turnbacks, pleats
skirt_idx = B.group_idx({"pelvis", "spine", "spine1"} | LEG[1] | LEG[-1])
hs_t = [S["tails_top"] - k * (S["tails_top"] - S["tails"]) / 13 for k in range(14)]
sk_fr = vertical_frames(B, skirt_idx, hs_t)
# Near the waist the tails follow the coat's own section (so they stay under its hem); lower down, the hull of
# hips and thighs. Blend between the two over 1.10 -> 1.04.
for k, h in enumerate(hs_t):
    w = smoothstep(1.04, 1.10, h)
    if w <= 0:
        continue
    cf = frame_at_h(coat_fr, hs_c, h)
    f = sk_fr[k]
    f["c"] = f["c"].lerp(cf["c"], w)
    f["r"] = [a * (1 - w) + b * w for a, b in zip(f["r"], cf["r"])]
FRONT_CUT = [(0.70, 108), (0.82, 100), (0.95, 80), (1.06, 45), (1.12, 14), (1.14, 14)]
VENT = [(0.70, 3.0), (1.04, 3.0), (1.05, 0.4), (1.14, 0.4)]
MC = 13


def interp(h, table):
    table = sorted(table)
    if h <= table[0][0]:
        return table[0][1]
    for (h0, a0), (h1, a1) in zip(table, table[1:]):
        if h0 <= h <= h1:
            return a0 + (a1 - a0) * (h - h0) / (h1 - h0)
    return table[-1][1]


def tail_ease(h, c):
    # under the coat down to its hem (coat hem edge at ease ~0.0094), then out over the trousers seat
    e = 0.004 + 0.0035 * smoothstep(S["tails_top"], S["coat_bottom"], h)
    e += 0.007 * smoothstep(S["coat_bottom"], 1.08, h)
    t = max(0.0, min(1.0, (S["coat_bottom"] - h) / (S["coat_bottom"] - S["tails"])))
    e += 0.004 * smoothstep(0.0, 0.15, t) + 0.019 * t
    e += 0.0045 * t ** 1.2 * math.sin(2 * math.pi * 1.25 * c / (MC - 1))      # drape
    if c <= 1:
        e += 0.0012 * smoothstep(1.10, 1.07, h)                                # turnback lies on the cloth
    if c == MC - 2:
        e -= 0.004 * smoothstep(1.10, 1.04, h)                                 # back pleat crease
    return e


def tail_angle(h, c, side):
    a0 = math.radians(interp(h, FRONT_CUT))
    a1 = math.pi - math.radians(interp(h, VENT))
    a = a0 + (a1 - a0) * c / (MC - 1)
    return a if side > 0 else -a


tail_frames = (sk_fr, hs_t)
for side in (1, -1):
    begin(f"aba_{'E' if side > 0 else 'D'}")
    O = [[bm.verts.new(fpoint(f, tail_angle(h, c, side), tail_ease(h, c))) for c in range(MC)] for h, f in zip(hs_t, sk_fr)]
    I = [[bm.verts.new(fpoint(f, tail_angle(h, c, side), tail_ease(h, c) - S["cloth"])) for c in range(MC)] for h, f in zip(hs_t, sk_fr)]
    fs, outer_faces = [], []
    nR = len(hs_t)
    # The front cut sweeps quickly near the waist, so the cells are skewed and not planar: outer cloth and lining
    # are split into triangles along the SAME diagonal, otherwise the two 4 mm-apart surfaces cross each other.
    for k in range(nR - 1):
        for c in range(MC - 1):
            mo = VERM if c <= 1 else AZUL                                      # red turnback along the front edge
            d02 = (O[k][c].co - O[k + 1][c + 1].co).length
            d13 = (O[k][c + 1].co - O[k + 1][c].co).length
            if d02 <= d13:
                tri_o = [(O[k][c], O[k][c + 1], O[k + 1][c + 1]), (O[k][c], O[k + 1][c + 1], O[k + 1][c])]
                tri_i = [(I[k][c + 1], I[k][c], I[k + 1][c + 1]), (I[k][c], I[k + 1][c], I[k + 1][c + 1])]
            else:
                tri_o = [(O[k][c], O[k][c + 1], O[k + 1][c]), (O[k][c + 1], O[k + 1][c + 1], O[k + 1][c])]
                tri_i = [(I[k][c + 1], I[k][c], I[k + 1][c]), (I[k][c + 1], I[k + 1][c], I[k + 1][c + 1])]
            for t_ in tri_o:
                fo = bm.faces.new(t_)
                fo.material_index = mo
                fs.append(fo)
                outer_faces.append(fo)
            for t_ in tri_i:
                fi = bm.faces.new(t_)
                fi.material_index = VERM                                       # red lining
                fs.append(fi)
        fa = bm.faces.new((O[k][0], O[k + 1][0], I[k + 1][0], I[k][0]))      # front edge
        fa.material_index = VERM
        fb = bm.faces.new((O[k][MC - 1], I[k][MC - 1], I[k + 1][MC - 1], O[k + 1][MC - 1]))   # vent edge
        fb.material_index = AZUL
        fs += [fa, fb]
    for c in range(MC - 1):                                                    # bottom edge
        fb = bm.faces.new((O[nR - 1][c], O[nR - 1][c + 1], I[nR - 1][c + 1], I[nR - 1][c]))
        fb.material_index = VERM if c <= 1 else AZUL
        fs.append(fb)
    bad = []
    for k, (h, f) in enumerate(zip(hs_t, sk_fr)):
        cc = frame_centre(f)
        for c in range(MC):
            ro, ri = (O[k][c].co - cc).length, (I[k][c].co - cc).length
            if ri >= ro:
                bad.append((k, c, round(ro, 4), round(ri, 4)))
    print(f"TAIL CHECK side {side}: lining outside the outer cloth at {len(bad)} vertices {bad[:6]}")
    orient_island(fs, outer_faces[len(outer_faces) // 2], frame_centre(sk_fr[nR // 2]))
    end()

# =============================================================== 4. shoulder boards (white, rounded end at the collar)
for s in (1, -1):
    begin(f"platina_{'E' if s > 0 else 'D'}")
    xs = [0.095 + S["strap_len"] * q / 5 for q in range(6)]
    rows_t, rows_b = [], []
    for q, xa in enumerate(xs):
        x = s * xa
        ys = [k * 0.004 - 0.06 for k in range(41)]
        tops = [(B.top(x, y), y) for y in ys]
        ridge_y = max((t for t in tops if t[0] is not None), key=lambda t: t[0])[1]
        wf = 0.55 if q == 0 else 1.0
        row_t, row_b = [], []
        for w in (-1, -0.5, 0, 0.5, 1):
            y = ridge_y + w * S["strap_w"] / 2 * wf
            zb = B.top(x, y)
            zb = zb if zb is not None else tops[0][0]
            row_t.append(Vector((x, y, zb + S["ease_coat"] + 0.0035)))
            row_b.append(Vector((x, y, zb + 0.001)))                       # walls end under the coat, on the body
        rows_t.append(row_t)
        rows_b.append(row_b)
    tip_t = Vector((s * 0.088, rows_t[0][2].y, rows_t[0][2].z))               # rounded end beside the collar
    tip_b = Vector((s * 0.088, rows_b[0][2].y, rows_b[0][2].z))
    zt0 = B.top(tip_b.x, tip_b.y)
    if zt0 is not None:
        tip_b.z = min(tip_b.z, zt0 + 0.001)
    VT = [[bm.verts.new(p) for p in r] for r in rows_t]
    VB = [[bm.verts.new(p) for p in r] for r in rows_b]
    t_v, b_v = bm.verts.new(tip_t), bm.verts.new(tip_b)
    fs = []
    for k in range(5):
        for c in range(4):
            fs.append(bm.faces.new((VT[k][c], VT[k][c + 1], VT[k + 1][c + 1], VT[k + 1][c])))
        fs.append(bm.faces.new((VT[k][0], VT[k + 1][0], VB[k + 1][0], VB[k][0])))
        fs.append(bm.faces.new((VT[k][4], VB[k][4], VB[k + 1][4], VT[k + 1][4])))
    for c in range(4):
        fs.append(bm.faces.new((VT[0][c + 1], VT[0][c], t_v)))
        fs.append(bm.faces.new((VT[5][c], VT[5][c + 1], VB[5][c + 1], VB[5][c])))
    fs.append(bm.faces.new((VT[0][0], t_v, b_v, VB[0][0])))
    fs.append(bm.faces.new((t_v, VT[0][4], VB[0][4], b_v)))
    for f_ in fs:
        f_.material_index = BRANCO
    orient_island(fs, fs[6], Vector((s * 0.15, rows_t[2][2].y, rows_t[2][2].z - 0.1)))   # fs[6]: a top face
    end()

# =============================================================== 5. trousers: seat and legs (bunching over the gaiters)
pel_idx = B.group_idx({"pelvis", "spine", "spine1"} | LEG[1] | LEG[-1])
hs_p = [1.13 - k * 0.03 for k in range(9)] + [0.86]
hs_p = sorted(set(round(h, 4) for h in hs_p if h >= 0.86), reverse=True)
pf = vertical_frames(B, pel_idx, hs_p)
TH_P = [2 * math.pi * i / 28 for i in range(28)]
begin("calca_assento")
eps = [0.0025 + 0.0075 * smoothstep(1.12, 0.95, h) for h in hs_p]     # snug under the coat and the tails
loft(bm, [[fpoint(f, th, e) for th in TH_P] for f, e in zip(pf, eps)], mat_of=lambda k, i: CINZA,
     orient_centres=[frame_centre(f) for f in pf], orient_band=len(pf) // 2)
end()
N_LEG = 18
TH_L = [2 * math.pi * i / N_LEG for i in range(N_LEG)]
for s in (1, -1):
    idx = B.group_idx(LEG[s] | {"pelvis"}, side=s)
    hs_l = sorted({round(h, 4) for h in [0.90, 0.87, 0.84, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.47, 0.455, 0.44,
                                         0.425, 0.39]}, reverse=True)
    fr = vertical_frames(B, idx, hs_l, xside=s, xmargin=-0.03)        # crosses the centre line: closes the crotch

    def leg_ease(h, th):
        e = S["ease_trousers"] + (0.008 - S["ease_trousers"]) * smoothstep(0.55, 0.40, h)
        e -= 0.012 * smoothstep(0.86, 0.90, h)                          # top tucked under the seat
        e += 0.0075 * smoothstep(0.415, 0.43, h) * (1 - smoothstep(0.47, 0.50, h))     # bunching over the gaiter
        e += 0.0015 * math.cos(2 * math.pi * (h - 0.44) / 0.03) * gauss(h, 0.45, 0.03)
        w_back = max(0.0, math.cos(angdiff(th, math.pi))) ** 2                           # folds behind the knee
        e += 0.0025 * gauss(h, 0.50, 0.035) * w_back * (0.5 + 0.5 * math.cos(2 * math.pi * h / 0.035))
        return e

    begin(f"calca_perna_{'E' if s > 0 else 'D'}")
    loft(bm, [[fpoint(f, th, leg_ease(h, th)) for th in TH_L] for h, f in zip(hs_l, fr)], mat_of=lambda k, i: CINZA,
         orient_centres=[frame_centre(f) for f in fr], orient_band=2)
    end()

# =============================================================== 6. gaiters: hems at both ends, button strip on the outside
gaiter_info = {}
for s in (1, -1):
    idx = B.group_idx(LEG[s] | FOOT[s], side=s)
    hs_g = sorted({round(S["gaiter_top"] - k * 0.05, 4) for k in range(8)} | {S["gaiter_bottom"]}, reverse=True)
    hs_g = [h for h in hs_g if h >= S["gaiter_bottom"]]
    fr = vertical_frames(B, idx, hs_g, xside=s, passes=1)
    th_out = math.pi / 2 if s > 0 else -math.pi / 2
    DS = 0.22
    TH_G = sorted({round((2 * math.pi * i / 16) % (2 * math.pi), 6) for i in range(16)}
                  | {round((th_out + d) % (2 * math.pi), 6) for d in (-DS - 0.02, -DS, DS, DS + 0.02)})

    def gaiter_ease(h, th, th_out=th_out, DS=DS):
        e = S["ease_gaiter"] + 0.004 * (h - S["gaiter_bottom"]) / (S["gaiter_top"] - S["gaiter_bottom"])
        if abs(angdiff(th, th_out)) <= DS + 1e-6:
            e += 0.0025                                                        # button strip (overlap)
        return e

    def fr_h(h, fr=fr, hs_g=hs_g):
        return frame_at_h(fr, hs_g, h)

    spec_g = [(0.40, -0.004), (0.4235, -0.0015)] + [(h, 0.0) for h in hs_g] + [(0.0715, -0.0015), (0.09, -0.004)]
    begin(f"polaina_{'E' if s > 0 else 'D'}")
    loft(bm, [[fpoint(fr_h(h), th, gaiter_ease(min(max(h, S['gaiter_bottom']), S['gaiter_top']), th) + de)
               for th in TH_G] for h, de in spec_g],
         mat_of=lambda k, i: POLAINA, orient_centres=[frame_centre(fr_h(h)) for h, _ in spec_g], orient_band=3)
    end()
    gaiter_info[s] = (fr_h, gaiter_ease, th_out)

# =============================================================== 7. shoes: sole with welt and heel, leather upper
for s in (1, -1):
    idx = B.group_idx(FOOT[s] | LEG[s], thr=0.3, side=s)
    sole_pts = []
    for h in (0.004, 0.010, 0.020):
        sole_pts += B.section(idx, Vector((0, 0, Z(h))), UP, xside=s)
    sole_fr = fill_and_smooth([profile(sole_pts, Vector((0, 0, Z(0.0))), UP)], passes=0)[0]
    hs_u = [0.035, 0.05, 0.065, 0.08, 0.095]
    ufr = vertical_frames(B, idx, hs_u, xside=s, passes=1)
    TH_S = [2 * math.pi * i / 20 for i in range(20)]
    ground = [fpoint(sole_fr, th, S["ease_shoe"] + 0.006) for th in TH_S]
    ys = [p.y for p in ground]
    y0, y1 = min(ys), max(ys)

    def sole_top(y):
        return 0.010 + 0.014 * smoothstep(y0 + 0.64 * (y1 - y0), y0 + 0.72 * (y1 - y0), y)   # heel at the back

    rings = [[Vector((p.x, p.y, Z(0.0))) for p in ground],
             [Vector((p.x, p.y, Z(sole_top(p.y)))) for p in ground]]
    inner = [fpoint(sole_fr, th, S["ease_shoe"] + 0.002) for th in TH_S]
    rings.append([Vector((p.x, p.y, Z(sole_top(p.y)))) for p in inner])
    rings.append([Vector((p.x, p.y, Z(max(sole_top(p.y) + 0.004, 0.022)))) for p in inner])
    rings += [[fpoint(f, th, S["ease_shoe"]) for th in TH_S] for f in ufr]
    cen = [frame_centre(sole_fr)] * 4 + [frame_centre(f) for f in ufr]
    begin(f"sapato_{'E' if s > 0 else 'D'}")
    V = loft(bm, rings, mat_of=lambda k, i: SOLA if k <= 1 else SAPATO, orient_centres=cen, orient_band=4)
    cv = bm.verts.new(sum(rings[0], Vector()) / len(rings[0]))
    fs = [bm.faces.new((cv, V[0][(i + 1) % 20], V[0][i])) for i in range(20)]
    for f_ in fs:
        f_.material_index = SOLA
        f_.normal_update()
        if f_.normal.z > 0:
            f_.normal_flip()
    end()

# =============================================================== 8. buttons (domed brass)
nb = 0
begin("botoes")
# front: two columns of 7 (U4, as in the mod)
for x in (-0.015, 0.015):
    for k in range(7):
        h = 1.50 - (1.50 - 1.17) * k / 6
        fr = frame_at_h(coat_fr, hs_c, h)
        th = solve_theta_x(fr, lambda t: coat_ease(t, h), x)
        p = fpoint(fr, th, coat_ease(th, h))
        n = (p - frame_centre(fr)); n.z = 0
        dome(bm, p - n.normalized() * 0.0005, n, 0.009, 0.0045, seg=8, mat=LATAO); nb += 1
# back: two at the top of the pleats
for side in (1, -1):
    h = 1.092
    f = frame_at_h(sk_fr, hs_t, h)
    th = tail_angle(h, MC - 2, side)
    p = fpoint(f, th, tail_ease(h, MC - 2))
    n = (p - frame_centre(f)); n.z = 0
    dome(bm, p, n, 0.009, 0.0045, seg=8, mat=LATAO); nb += 1
# shoulder boards: near the rounded end
for s in (1, -1):
    x = s * 0.105
    ys = [k * 0.004 - 0.06 for k in range(41)]
    tops = [(B.top(x, y), y) for y in ys]
    zt, yr = max((t for t in tops if t[0] is not None), key=lambda t: t[0])
    dome(bm, Vector((x, yr, zt + S["ease_coat"] + 0.0035)), UP, 0.0065, 0.003, seg=6, mat=LATAO); nb += 1
# cuff flaps: three each
for s in (1, -1):
    P, L, s_top, cuff_frame, ec, out_dir = cuff_data[s]
    for q in range(3):
        si = L - 0.012 - S["flap_len"] * (0.2 + 0.3 * q)
        f = cuff_frame(si)
        th_o = theta_of(f, out_dir - f["a"] * out_dir.dot(f["a"]))
        p = fpoint(f, th_o, ec + 0.0025)
        n = p - frame_centre(f); n -= f["a"] * n.dot(f["a"])
        dome(bm, p, n, 0.0065, 0.003, seg=6, mat=LATAO); nb += 1
# gaiters: ten each on the strip
for s in (1, -1):
    fr_h, g_ease, th_out = gaiter_info[s]
    for k in range(10):
        h = 0.395 - (0.395 - 0.105) * k / 9
        f = fr_h(h)
        p = fpoint(f, th_out, g_ease(h, th_out))
        n = Vector((s, 0, 0))
        dome(bm, p, n, 0.0048, 0.0025, seg=5, mat=LATAO); nb += 1
end()
print(f"buttons: {nb}")

# =============================================================== 9. hands from the official template (unchanged)
tlod = read_mlod(os.path.join(SAMPLES, "A3_character_template.p3d"))[0]
tpts = [Vector(to_blender(p)) for p in tlod["points"]]
tproxy = set()
for name, blob in tlod["selections"].items():
    if name.lower().startswith("proxy:") or name.startswith("-"):
        tproxy.update(i for i, b in enumerate(blob) if b)
fdir = {s: (J[("wrist", s)] - J[("elbow", s)]).normalized() for s in (1, -1)}


def keep_hand_point(i):
    p = tpts[i]
    s = 1 if p.x > 0 else -1
    w = p - J[("wrist", s)]
    return w.dot(fdir[s]) > -0.06 and w.length < 0.25          # cut 6 cm up the forearm, deep inside the sleeve


uv_layer = bm.loops.layers.uv.verify()
deform = bm.verts.layers.deform.verify()
BONE_GROUPS = [n for n in tlod["selections"] if not n.startswith("proxy:") and not n.startswith("-")
               and (n.lower() in {"leftforearm", "leftforearmroll", "rightforearm", "rightforearmroll"}
                    or n.lower().startswith("lefthand") or n.lower().startswith("righthand"))]
begin("maos_template")
vmap, hand_tex = {}, set()
for f, uvs, tex in zip(tlod["faces"], tlod["faces_uv"], tlod["faces_tex"]):
    if len(set(f)) < 3 or any(i in tproxy for i in f) or not all(keep_hand_point(i) for i in f):
        continue
    for i in f:
        if i not in vmap:
            v = bm.verts.new(tpts[i])
            for gi, gname in enumerate(BONE_GROUPS):
                b = tlod["selections"][gname][i]
                if b:
                    v[deform][gi] = (256 - b) / 255.0
            vmap[i] = v
    try:
        face = bm.faces.new([vmap[i] for i in f])           # native MLOD order: outward normals
    except ValueError:
        continue
    face.material_index = PELE
    for loop, (u, vv) in zip(face.loops, uvs):
        loop[uv_layer].uv = (u, 1.0 - vv)                   # P3D v grows downwards
    hand_tex.add(tex)
end()
loose = [v for v in bm.verts if not v.link_faces]                 # template points whose faces were not kept
bmesh.ops.delete(bm, geom=loose, context="VERTS")
print(f"hand textures/materials in the template: {sorted(hand_tex)}; loose points removed: {len(loose)}")

# =============================================================== object
bm.normal_update()
me = bpy.data.meshes.new("HCL_U_Pruss1813_01_LOD0")
bm.to_mesh(me)
COLL = bpy.data.collections.new("HCL_Uniforme_Producao")
bpy.context.scene.collection.children.link(COLL)
ob = bpy.data.objects.new("HCL_U_Pruss1813_01_LOD0", me)
COLL.objects.link(ob)
for gname in BONE_GROUPS:
    ob.vertex_groups.new(name=gname)
for name, rgb, rough, metal in MATS:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1)
    me.materials.append(m)
me.materials["HCL_pele_hl"]["a3_origem_textura_rvmat"] = "; ".join(f"{t} | {m_}" for t, m_ in sorted(hand_tex))
ob["hcl_partes"] = ",".join(PART_NAMES)

# ---------------------------------------------------------------- references
REFC = bpy.data.collections.new("REF_Arma3Samples")
bpy.context.scene.collection.children.link(REFC)
body_me = bpy.data.meshes.new("REF_corpo_A3_character_example")
B.bm.to_mesh(body_me)
body_ob = bpy.data.objects.new("REF_corpo_A3_character_example", body_me)
REFC.objects.link(body_ob)
skin = bpy.data.materials.new("REF_pele")
skin.diffuse_color = (0.8, 0.6, 0.48, 1)
body_me.materials.append(skin)
with bpy.data.libraries.load(SHAKO_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ("HCL_Shako_Pruss_LOD0", "REF_cabeca_APROXIMADA_nao_oficial")]
SHC = bpy.data.collections.new("REF_Barretina_aprovada")
bpy.context.scene.collection.children.link(SHC)
for o in dst.objects:
    (REFC if o.name.startswith("REF_") else SHC).objects.link(o)

# =============================================================== checks
bm.faces.ensure_lookup_table()
print("\n=== TRIANGLES by part")
tot = 0
for pid, name in enumerate(PART_NAMES):
    t = sum(len(f.verts) - 2 for f in bm.faces if f[PART] == pid)
    tot += t
    print(f"  {name:22s} {t:6d}")
print(f"  TOTAL {tot}   (garment {tot - sum(len(f.verts) - 2 for f in bm.faces if f.material_index == PELE)}, hands "
      f"{sum(len(f.verts) - 2 for f in bm.faces if f.material_index == PELE)})")
by_mat = {}
for f in bm.faces:
    by_mat[MATS[f.material_index][0]] = by_mat.get(MATS[f.material_index][0], 0) + len(f.verts) - 2
print("  by material: " + ", ".join(f"{k}={v}" for k, v in sorted(by_mat.items(), key=lambda kv: -kv[1])))

print("\n=== GARMENT VERTICES INSIDE THE OFFICIAL BODY (by part)")
for pid, name in enumerate(PART_NAMES):
    if name in ("maos_template", "botoes"):
        continue
    vs = {v for f in bm.faces if f[PART] == pid for v in f.verts}
    d = [(B.signed_distance(v.co), v.co) for v in vs]
    ins = [q for q in d if q[0] < 0]
    msg = ""
    if ins:
        hz = [B.H(p.z) for _, p in ins]
        msg = f"  at h {min(hz):.3f}-{max(hz):.3f}"
    print(f"  {name:22s} inside {len(ins):4d}/{len(vs):4d}  min {min(q[0] for q in d)*1000:7.1f} mm{msg}")

# exposed skin (body vertices whose outward normal ray escapes without crossing the uniform); hands/neck skipped
GB = BVHTree.FromBMesh(bm)
wr_dir = fdir
checked, exposed = 0, []
for v in B.bm.verts:
    p, n = v.co, v.normal * B.sign
    if B.H(p.z) > 1.56:
        continue
    s_ = 1 if p.x > 0 else -1
    if (p - J[("wrist", s_)]).dot(wr_dir[s_]) > 0.005:
        continue
    checked += 1
    if GB.ray_cast(p + n * 1e-4, n, 0.25)[0] is None:
        exposed.append(p)
print(f"\n=== EXPOSED SKIN: {len(exposed)} of {checked} body vertices")
for p in exposed[:10]:
    print(f"    x{p.x:+.3f} y{p.y:+.3f} h{B.H(p.z):.3f}")

# open edges: hidden (inside the body, or every ray from the edge meets cloth or body) vs visible.
# Button bases sit on the cloth by design and are not counted.
DIRS = [Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
        for a in [2 * math.pi * k / 8 for k in range(8)] for b in (-0.6, 0.0, 0.6)] + [UP, -UP]


def escapes(p):
    """Directions in which a ray from p leaves the figure without meeting cloth or body (3 m = infinity here)."""
    out = []
    for d in DIRS:
        o = p + d * 0.0015
        if GB.ray_cast(o, d, 3.0)[0] is None and B.bvh.ray_cast(o, d, 3.0)[0] is None:
            out.append(d)
    return out


vis, below, hid = {}, {}, {}
BTN = PART_NAMES.index("botoes")
for e in bm.edges:
    if not e.is_boundary:
        continue
    pid = e.link_faces[0][PART]
    if pid == BTN:
        continue
    m = (e.verts[0].co + e.verts[1].co) / 2
    esc = [] if B.signed_distance(m) < 0.0 else escapes(m)
    if not esc:
        hid[pid] = hid.get(pid, 0) + 1
    elif all(d.z < -0.5 for d in esc):
        below[pid] = below.get(pid, 0) + 1
    else:
        vis.setdefault(pid, []).append(m)
print("\n=== OPEN EDGES: hidden / seen only from below the figure / VISIBLE from the side or above")
for pid, name in enumerate(PART_NAMES):
    if pid in vis or pid in hid or pid in below:
        v = vis.get(pid, [])
        ex = f"  e.g. h {B.H(v[0].z):.3f} x{v[0].x:+.3f} y{v[0].y:+.3f}" if v else ""
        print(f"  {name:22s} hidden {hid.get(pid, 0):4d}  below {below.get(pid, 0):4d}  VISIBLE {len(v):4d}{ex}")

# =============================================================== renders
if RENDER:
    scene = bpy.context.scene
    for nm, en, rot in (("REF_sol", 3.2, (50, 0, 25)), ("REF_preench", 1.3, (65, 0, 200)), ("REF_contra", 1.0, (60, 0, 120))):
        lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN"))
        lo.data.energy = en
        lo.rotation_euler = tuple(math.radians(a) for a in rot)
        REFC.objects.link(lo)
    world = bpy.data.worlds.new("REF_mundo")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.93, 0.93, 0.93, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.65
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 40
    scene.view_settings.view_transform = "Standard"
    body_ob.hide_render = False
    for p_ in me.polygons:
        p_.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(40))

    def cam(name, loc, ortho=None, lens=50, target=None, rot=None):
        c = bpy.data.cameras.new(name)
        if ortho:
            c.type = "ORTHO"; c.ortho_scale = ortho
        else:
            c.lens = lens
        o = bpy.data.objects.new(name, c)
        o.location = loc
        o.rotation_euler = rot if rot else (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        REFC.objects.link(o)
        return o

    ZC = Z(0.98)
    shots = [
        ("frente", cam("CAM_frente", (0, -8, ZC), ortho=2.15, rot=(math.radians(90), 0, 0)), (900, 1100)),
        ("lado", cam("CAM_lado", (8, 0, ZC), ortho=2.15, rot=(math.radians(90), 0, math.radians(90))), (900, 1100)),
        ("costas", cam("CAM_costas", (0, 8, ZC), ortho=2.15, rot=(math.radians(90), 0, math.radians(180))), (900, 1100)),
        ("tres_quartos", cam("CAM_3q", (2.6, -3.6, Z(1.35)), lens=55, target=Vector((0, 0, Z(0.95)))), (900, 1100)),
        ("tres_quartos_costas", cam("CAM_3qc", (-2.6, 3.6, Z(1.35)), lens=55, target=Vector((0, 0, Z(0.95)))), (900, 1100)),
        ("detalhe_tronco", cam("CAM_tronco", (1.3, -1.9, Z(1.55)), lens=60, target=Vector((0.05, 0, Z(1.30)))), (1000, 900)),
        ("detalhe_abas", cam("CAM_abas", (-1.2, 1.9, Z(1.30)), lens=60, target=Vector((0, 0.05, Z(0.95)))), (1000, 900)),
        ("detalhe_punho", cam("CAM_punho", (1.05, -0.75, Z(1.25)), lens=85, target=Vector((0.55, 0.08, Z(1.10)))), (1000, 800)),
        ("detalhe_pernas", cam("CAM_pernas", (1.1, -1.7, Z(0.55)), lens=60, target=Vector((0, 0, Z(0.30)))), (1000, 900)),
    ]
    for name, c, (rx, ry) in shots:
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT_IMG, f"producao_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    # topology overlay
    wire = ob.copy()
    wire.data = ob.data
    wire.name = "REF_wireframe_overlay"
    REFC.objects.link(wire)
    wm = wire.modifiers.new("fio", "WIREFRAME")
    wm.thickness = 0.0009
    wm.use_replace = True
    wmat = bpy.data.materials.new("REF_fio")
    wmat.use_nodes = True
    wmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.75, 0.2, 1)
    wire.data = ob.data.copy()
    wire.data.materials.clear()
    wire.data.materials.append(wmat)
    for name, c, (rx, ry) in (shots[0], shots[3], shots[5]):
        scene.camera = c
        scene.render.resolution_x, scene.render.resolution_y = rx, ry
        scene.render.filepath = os.path.join(OUT_IMG, f"producao_malha_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    wire.hide_render = True
    wire.hide_viewport = True
    scene.camera = shots[0][1]

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
