# Movement test outside the game: the official sample animations of the Arma 3 Samples (unbinarized RTM_0101) are
# applied by linear blend skinning to the uniform (HCL_U_Pruss1813_01_LOD0) and to the shako, with bone weights
# transferred from the official body (A3_character_example.p3d). The game head (TemplateRTM/bust.p3d, Resolution 1)
# is posed with its own weights and used for the collar and shako checks.
# Verified conventions (see docs/reports/teste_movimentos_pruss.md):
#   RTM matrix = 9 floats (images of the x, y, z axes, i.e. columns of R) + translation; v_pose = R v_bind + t,
#   v_bind in P3D model space (pelvis pivot at the origin), posed space with the ground at y = 0.
# All sources are read-only. Writes: a weighted copy of the uniform (first version of the Phase 7 weights), renders,
# and a text report.
#   blender -b --factory-startup --python teste_movimentos.py -- <project root> <samples dir> <out_dir>
#           [abas=transfer|pelve] [norender] [samples=N] [tag=<name>] [equip=blockout|<blend>] [pesos_out=<blend>]
#           [poses=a,b] [so_galeria] [sem_galeria] [nacao=fr] [uni=<uniform .blend>] [uni_obj=<object name>]
# uni= / uni_obj=: another uniform of the same nation, e.g. the French greatcoat (build_capote_fr.py: no tails, no
# lapels, a skirt "saia_E"/"saia_D" that takes the weights of the body like the trousers; the coat under the skirt top
# rides with the skirt)
# nacao=fr: the French coat 1812 (build_uniforme_fr.py) and its crossbelts / havresac (build_equipamento_producao.py
# nacao=fr); the lapels carry the equipment like the coat; no renders (they use the Prussian textures)
import bpy, bmesh, sys, os, re, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender
from rtm_read import read_rtm
from uniform_fit import Body, weight_of_byte

ARGS = sys.argv[sys.argv.index("--") + 1:]
ROOT, SAMPLES, OUT = ARGS[:3]
OPT = dict(a.split("=", 1) for a in ARGS[3:] if "=" in a)
ABAS = OPT.get("abas", "pelve")
TAG = OPT.get("tag", ABAS)
FR = OPT.get("nacao") == "fr"
UNI_NAME = "HCL_U_Fr1812_01_LOD0" if FR else "HCL_U_Pruss1813_01_LOD0"
UNI_NAME = OPT.get("uni_obj", UNI_NAME)
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
REST_GROUND = -1.0069
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


# ---------------------------------------------------------------- skeleton (canonical names and parents)
cfg = open(os.path.join(SAMPLES, r"Addons\TemplateRTM\model.cfg"), encoding="latin-1").read()
blk = re.search(r"skeletonBones\[\]\s*=\s*\{(.*?)\};", cfg, re.S).group(1)
blk = re.sub(r"//[^\n]*", "", blk)
toks = re.findall(r'"([^"]*)"', blk)
PARENT = {toks[i].lower(): toks[i + 1].lower() for i in range(0, len(toks), 2)}
CANON = {toks[i].lower(): toks[i] for i in range(0, len(toks), 2)}

# ---------------------------------------------------------------- animations (official samples)
A = os.path.join(SAMPLES, "Addons")
POSES = [  # (id, label, file, frame step)
    ("em_pe", "Em pé, fuzil erguido", r"Test_Anims\AmovPercMstpSrasWrflDnon.rtm", 1),
    ("agachado", "Agachado (um joelho no chão), fuzil erguido", r"Test_Anims\AmovPknlMstpSrasWrflDnon.rtm", 1),
    ("deitado", "Deitado, fuzil erguido", r"Test_Anims\AmovPpneMstpSrasWrflDnon.rtm", 1),
    ("inventario", "Ajoelhado, mãos no chão (inventário)", r"Test_Anims\AinvPknlMstpSlayWrflDnon.rtm", 1),
    ("sentado", "Sentado (passageiro, FFV)", r"Test_FFV_Poses_F\Anim\ffv_01_idle1.rtm", 5),
    ("sentado_mira", "Sentado mirando (FFV)", r"Test_FFV_Poses_F\Anim\ffv_01_aim1.rtm", 2),
    ("morte", "Morte sentado (FFV)", r"Test_FFV_Poses_F\Anim\ffv_01_die.rtm", 1),
    ("binoculo", "Sentado com binóculo (FFV)", r"Test_FFV_Poses_F\Anim\ffv_01_aim_binoc.rtm", 2),
]
S_SWAP = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], np.float64)     # Blender <-> P3D (y and z swapped)


def frame_mats(mats):
    """RTM frame -> {bone(lower): (R, t)} in Blender axes."""
    out = {}
    for k, m in mats.items():
        if k.lower().startswith(("face_", "eye")):
            # facial bones are identity in the body animations (the face is animated separately, verified on
            # AmovPercMstpSrasWrflDnon.rtm): leave them out so they follow the head through the parent chain
            continue
        m = np.array(m, np.float64)
        R = m[:9].reshape(3, 3).T                     # the 9 floats are the images of x, y, z (columns)
        out[k.lower()] = (S_SWAP @ R @ S_SWAP, S_SWAP @ m[9:])
    return out


def bone_mat(fm, b):
    while b and b not in fm:
        b = PARENT.get(b, "")
    return fm.get(b, (np.eye(3), np.zeros(3)))


def skin(V, W, bones, fm):
    P = np.zeros_like(V)
    for j, b in enumerate(bones):
        w = W[:, j]
        nz = w > 0
        if not nz.any():
            continue
        R, t = bone_mat(fm, b)
        P[nz] += w[nz, None] * (V[nz] @ R.T + t)
    return P


# ---------------------------------------------------------------- load the uniform and the shako
def append(path, names):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in names]
    got = list(dst.objects)
    for o in got:
        bpy.context.scene.collection.objects.link(o)
    return got


UNI = os.path.join(ROOT, r"source\models\coats\hcl_uniforme_fr\hcl_uniforme_fr_LOD0.blend") if FR else \
    os.path.join(ROOT, r"source\models\coats\hcl_uniforme_pruss\hcl_uniforme_pruss_LOD0.blend")
UNI = OPT.get("uni", UNI)
SHK = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss\hcl_shako_pruss_LOD0.blend")
uni = append(UNI, [UNI_NAME])[0]
shk = next(o for o in append(SHK, ["HCL_Shako_Pruss_LOD0"]) if o.name.startswith("HCL_Shako"))
parts = uni["hcl_partes"].split(",")
me = uni.data
NV = len(me.vertices)
V0 = np.array([v.co[:] for v in me.vertices], np.float64)
bm = bmesh.new(); bm.from_mesh(me)
PL = bm.faces.layers.int.get("hcl_part")
FACES = [[v.index for v in f.verts] for f in bm.faces]
FPART = np.array([f[PL] for f in bm.faces])
vpart = np.full(NV, -1)
for fi, f in enumerate(FACES):
    vpart[f] = FPART[fi]
HANDS = parts.index("maos_template")
bm.free()

# ---------------------------------------------------------------- weights: transfer from the official body
body = Body(os.path.join(A, r"Test_Character_01\A3_character_example.p3d"))
JB = body.joints()
# a left piece (suffix _E, +X) takes weights only from the left half of the body and vice versa: near the crotch and the
# back vent some vertices of a left piece cross the midline, and the nearest body surface there is the other leg
fcx = [sum(body.pts[i].x for i in f) / len(f) for f in body.faces]
side_faces = {0: list(range(len(body.faces))), 1: [k for k, x in enumerate(fcx) if x > -0.005],
              -1: [k for k, x in enumerate(fcx) if x < 0.005]}
btree = {s: BVHTree.FromPolygons([tuple(p) for p in body.pts], [body.faces[k] for k in ks]) for s, ks in side_faces.items()}
PSIDE = [1 if p.endswith("_E") else -1 if p.endswith("_D") else 0 for p in parts]
OPP = {1: "right", -1: "left"}
hand_groups = {g.index: g.name.lower() for g in uni.vertex_groups}
Wd = [dict() for _ in range(NV)]
for v in me.vertices:
    if vpart[v.index] == HANDS:                                      # official template weights, kept as they are
        for g in v.groups:
            Wd[v.index][hand_groups[g.group]] = Wd[v.index].get(hand_groups[g.group], 0) + g.weight
        continue
    s = PSIDE[vpart[v.index]] if vpart[v.index] >= 0 else 0
    loc, _, fi, _ = btree[s].find_nearest(v.co)
    f = body.faces[side_faces[s][fi]]
    ws = poly_3d_calc([body.pts[i] for i in f], loc)
    for i, wi in zip(f, ws):
        for b, wb in body.W[i].items():
            if s and b.startswith(OPP[s]):
                continue
            Wd[v.index][b] = Wd[v.index].get(b, 0) + wi * wb
    if not Wd[v.index]:
        Wd[v.index]["pelvis"] = 1.0
BONES = sorted({b for d in Wd for b in d})
BI = {b: j for j, b in enumerate(BONES)}
W = np.zeros((NV, len(BONES)))
for i, d in enumerate(Wd):
    for b, w in d.items():
        W[i, BI[b]] = w
garment = vpart != HANDS
# smoothing along the garment surface (parts are separate meshes, so left and right legs never mix)
nb = [[] for _ in range(NV)]
for f in FACES:
    for a, b in zip(f, f[1:] + f[:1]):
        nb[a].append(b); nb[b].append(a)
for _ in range(2):
    Wn = W.copy()
    for i in np.nonzero(garment)[0]:
        if nb[i]:
            Wn[i] = 0.5 * W[i] + 0.5 * W[list(set(nb[i]))].mean(axis=0)
    W = Wn
# tails: blend towards the pelvis with depth below the waist (hanging cloth should not follow one thigh fully)
H0 = V0[:, 2] - REST_GROUND
if ABAS == "pelve" and "aba_E" in parts:
    tails = np.isin(vpart, [parts.index("aba_E"), parts.index("aba_D")])
    k = np.clip((1.04 - H0) / (1.04 - 0.70), 0, 1)
    k = 0.5 * k * k * (3 - 2 * k)
    W[tails] *= (1 - k[tails])[:, None]
    W[tails, BI["pelvis"]] += k[tails]
def limit4(W):
    """At most 4 bones per point, normalized (Arma limit, see references.md)."""
    order = np.argsort(-W, axis=1)
    Wc = np.zeros_like(W)
    rows = np.arange(len(W))[:, None]
    Wc[rows, order[:, :4]] = W[rows, order[:, :4]]
    Wc[Wc < 0.01] = 0
    return Wc / Wc.sum(axis=1, keepdims=True)


W = limit4(W)
# greatcoat skirt (build_capote_fr.py): it follows the pelvis and the thigh only. Its hem hangs below the knee, where the
# transfer gave it shin weights: kneeling, the shin folded the hem back under the thigh (edges stretched 5x, 2026-10-12)
SAIA_P = [parts.index(p) for p in ("saia_E", "saia_D") if p in parts]
if SAIA_P:
    sv = np.isin(vpart, SAIA_P)
    moved = 0.0
    for side in ("left", "right"):
        up = BI.get(side + "upleg")
        if up is None:
            continue
        for b, j in list(BI.items()):
            if b.startswith(side) and any(k in b for k in ("leg", "foot", "toe")) and "upleg" not in b:
                # all of it above 0.60 m; at the hem half of it stays (thigh-only made the gaiter tops cut the hem
                # when standing with the knees bent)
                fr_ = 0.5 + 0.5 * np.clip((H0[sv] - 0.46) / (0.60 - 0.46), 0, 1)
                mv = W[sv, j] * fr_
                moved += float(mv.sum())
                W[sv, up] += mv; W[sv, j] -= mv
    W = limit4(W)
    log(f"SAIA {int(sv.sum())} vertices: peso de canela/pe passado para a coxa ({moved:.1f} somado; na barra fica metade)")
# the standing collar must follow the neck partly (the game's head and neck turn and bend inside it): extra Neck weight
# rising from the collar base to its top (the transfer gave it ~80% Spine3 and only ~10% Neck)
GOLA_P = parts.index("gola")
gola_v = np.nonzero(vpart == GOLA_P)[0]
if len(gola_v) and "neck" in BI:
    # height fraction inside each collar column (collar v2, 2026-10-12: the front runs 1.50-1.575 m, the back
    # 1.54-1.60 m, so fixed heights would give the front almost no Neck weight); columns = same angle about the
    # game neck's leaning axis y = yc(h), which ajustar_gola_v2.py keeps for every vertex
    yc_g = 0.0177 - (np.clip(H0[gola_v], 1.50, 1.585) - 1.56) * 0.535
    th_g = np.round(np.degrees(np.arctan2(V0[gola_v, 0], -(V0[gola_v, 1] - yc_g))), 1)
    tg = np.zeros(len(gola_v))
    for t_ in np.unique(th_g):
        m_ = np.abs(th_g - t_) < 0.6
        lo_, hi_ = H0[gola_v][m_].min(), H0[gola_v][m_].max()
        tg[m_] = np.clip((H0[gola_v][m_] - lo_) / max(hi_ - lo_, 1e-6), 0, 1)
    sg = 0.35 * tg * tg * (3 - 2 * tg) + 0.05
    W[gola_v] *= (1 - sg)[:, None]
    W[gola_v, BI["neck"]] += sg
    W = limit4(W)
    log(f"GOLA {len(gola_v)} vertices em {len(np.unique(th_g))} colunas: peso extra no Neck de 5% (base) a 40% (topo); Neck medio no topo "
        f"{W[gola_v[tg > 0.9], BI['neck']].mean():.2f}")
# buttons ride on the cloth they are sewn to: copy the weights of the garment surface under each button
# (taking them from the body made the tail buttons follow the thigh while the tails follow the pelvis)
BTN = parts.index("botoes")
host_faces = [f for f, p in zip(FACES, FPART) if p not in (BTN, HANDS)]
htree = BVHTree.FromPolygons([tuple(p) for p in V0], host_faces)
bt = np.nonzero(vpart == BTN)[0]
Wb = np.zeros((len(bt), W.shape[1]))
for k, i in enumerate(bt):
    loc, _, fi, _ = htree.find_nearest(Vector(V0[i]))
    f = host_faces[fi]
    for j, wj in zip(f, poly_3d_calc([Vector(V0[j]) for j in f], loc)):
        Wb[k] += wj * W[j]
W[bt] = limit4(Wb)

# ---------------------------------------------------------------- weights v2 (2026-10-11): layers move together
# Problems P1, P2 and P7 of the first movement test: where one piece of the uniform lies on another, the two must follow
# the same bones, otherwise the inner one shows through (armpit, sleeve end inside the cuff) or the outer one lifts off
# (top of the gaiter). Only pieces of the uniform itself: the uniform's weights must not depend on the vest or the
# knapsack, which are optional. camadas=v1 switches this off (for comparison).
import heapq
LAYERS = OPT.get("camadas", "v2")
PU = {p: i for i, p in enumerate(parts)}
VN0 = np.zeros_like(V0)
for f in FACES:
    VN0[f] += np.cross(V0[f[1]] - V0[f[0]], V0[f[2]] - V0[f[0]])
VN0 /= np.linalg.norm(VN0, axis=1, keepdims=True) + 1e-12
V0L = [tuple(p) for p in V0]


def faces_of(*names, side=0):
    ids = [PU[n] for n in names]
    out = [f for f, p in zip(FACES, FPART) if p in ids]
    if side:
        out = [f for f in out if np.sign(V0[f, 0].mean()) == side]
    return out


def surf_w(src_faces, pts):
    """Weights interpolated on the source surface at its point nearest to each of pts."""
    tree = BVHTree.FromPolygons(V0L, src_faces)
    out = np.zeros((len(pts), W.shape[1]))
    for k, p in enumerate(pts):
        loc, _, fi, _ = tree.find_nearest(Vector(p))
        f = src_faces[fi]
        for j, wj in zip(f, poly_3d_calc([Vector(V0[j]) for j in f], loc)):
            out[k] += wj * W[j]
    return out


def geodesic(part_vs, seeds, radius):
    """Distance along the piece's own edges from the seed vertices, up to radius."""
    pset, dist = set(part_vs), {int(i): 0.0 for i in seeds}
    hq = [(0.0, int(i)) for i in seeds]
    while hq:
        d, i = heapq.heappop(hq)
        if d > dist.get(i, 9.0):
            continue
        for j in set(nb[i]):
            nd = d + float(np.linalg.norm(V0[i] - V0[j]))
            if j in pset and nd < radius and nd < dist.get(j, 9.0):
                dist[j] = nd
                heapq.heappush(hq, (nd, j))
    return dist


def ride(inner, outer, radius=0.03):
    """Inner vertices covered by the outer piece take its weights; the change fades out over `radius` along the
    inner piece (no tearing at the edge of the covered area)."""
    iv = np.nonzero(vpart == PU[inner])[0]
    of = faces_of(outer)
    tree = BVHTree.FromPolygons(V0L, of)
    seeds = [i for i in iv if tree.ray_cast(Vector(V0[i]) + Vector(VN0[i]) * 1e-4, Vector(VN0[i]), 0.05)[0] is not None]
    if not seeds:
        return 0, 0
    dist = geodesic(iv, seeds, radius)
    idx = np.array(sorted(dist))
    t = np.clip(np.array([dist[i] for i in idx]) / radius, 0, 1)
    f = 1 - t * t * (3 - 2 * t)
    W[idx] = limit4((1 - f)[:, None] * W[idx] + f[:, None] * surf_w(of, V0[idx]))
    return len(seeds), len(idx)


if LAYERS == "v2":
    msg = []
    Jb = body.joints()
    for s, sx in ((1, "E"), (-1, "D")):
        # P7: the gaiter top lies on the trouser leg: it follows the leg under it, fully at the top edge, fading out
        # 5 cm lower (the lower gaiter keeps its own weights, which follow the shin and the ankle)
        gv = np.nonzero(vpart == PU[f"polaina_{sx}"])[0]
        fg = np.clip((H0[gv] - 0.36) / (0.41 - 0.36), 0, 1)
        fg = fg * fg * (3 - 2 * fg)
        sel = gv[fg > 0]
        W[sel] = limit4((1 - fg[fg > 0])[:, None] * W[sel] + fg[fg > 0][:, None] * surf_w(faces_of(f"calca_perna_{sx}"), V0[sel]))
        msg.append(f"polaina_{sx} topo {len(sel)} v. seguem a calca")
        # P1: the template hand runs 6 cm up into the cuff; with the wrist bent 90 degrees (seated poses) the back of the
        # hand came out through the cuff wall 2-13 mm before the wrist (21 mm). Making the cuff follow the hand made it
        # worse (28 mm, cuff edges stretched 3.8x; tried 2026-10-11). Instead the part of the hand HIDDEN in the cuff
        # rides with the cuff (fading out over 2 cm into the visible hand, which keeps the official weights)
        a_, b_ = ride(f"maos_template", f"punho_{sx}", radius=0.02)
        msg.append(f"mao sob o punho_{sx}: {a_} cobertos, {b_} com transicao")
        # the sleeve end under the cuff, and the coat under the sleeve at the armpit (P2), ride with the outer piece
        a_, b_ = ride(f"manga_{sx}", f"punho_{sx}")
        msg.append(f"manga_{sx} sob o punho: {a_} cobertos, {b_} com transicao")
        a_, b_ = ride("casaco_corpo", f"manga_{sx}")
        msg.append(f"casaco sob a manga_{sx} (axila): {a_} cobertos, {b_} com transicao")
        # the cuff flap sits on the cuff: same weights as the cuff surface under it
        pv = np.nonzero(vpart == PU[f"pala_{sx}"])[0]
        W[pv] = limit4(surf_w(faces_of(f"punho_{sx}"), V0[pv]))
        # elite epaulettes (build_casaca_elite_fr.py). The body and the crescent are stiff: ONE set of weights, the
        # mean of the shoulder surface under them (tongue, coat, sleeve head); taking each point's own surface made the
        # body crumple when the arm rose (edges down to 3% of their length, 2026-10-12). The fringe cords lie on the
        # sleeve: rigid with the crescent at their roots, following the sleeve under them fully 4 cm down
        if f"dragona_corpo_{sx}" in PU:
            host_d = faces_of("casaco_corpo", f"manga_{sx}", f"platina_{sx}", side=s)
            rv = np.nonzero(np.isin(vpart, [PU[f"dragona_corpo_{sx}"], PU[f"dragona_meialua_{sx}"]]))[0]
            Rd = limit4(surf_w(host_d, V0[rv]).mean(axis=0)[None, :])[0]
            W[rv] = Rd
            fv = np.nonzero(vpart == PU[f"dragona_franja_{sx}"])[0]
            cres = np.nonzero(vpart == PU[f"dragona_meialua_{sx}"])[0]
            kdc = KDTree(len(cres))
            for k_, i in enumerate(cres):
                kdc.insert(V0[i], k_)
            kdc.balance()
            tf = np.array([min(1.0, kdc.find(V0[i])[2] / 0.04) for i in fv])
            ff = (tf * tf * (3 - 2 * tf))[:, None]
            W[fv] = limit4((1 - ff) * Rd[None, :] + ff * surf_w(host_d, V0[fv]))
            msg.append(f"dragona_{sx}: corpo e meia-lua rigidos ({len(rv)} v.: " +
                       ", ".join(f"{BONES[j]} {Rd[j]:.2f}" for j in np.nonzero(Rd)[0]) +
                       f"), franja {len(fv)} v. da meia-lua para a manga em 4 cm")
    a_, b_ = ride("casaco_corpo", "gola", radius=0.02)
    msg.append(f"casaco sob a gola: {a_} cobertos, {b_} com transicao")
    for sx in ("E", "D"):                                         # greatcoat: the coat edge under the skirt top
        if f"saia_{sx}" in PU:
            a_, b_ = ride("casaco_corpo", f"saia_{sx}", radius=0.03)
            msg.append(f"casaco sob a saia_{sx}: {a_} cobertos, {b_} com transicao")
    # buttons again (their cloth changed above)
    for k, i in enumerate(bt):
        loc, _, fi, _ = htree.find_nearest(Vector(V0[i]))
        f = host_faces[fi]
        Wb[k] = 0
        for j, wj in zip(f, poly_3d_calc([Vector(V0[j]) for j in f], loc)):
            Wb[k] += wj * W[j]
    W[bt] = limit4(Wb)
    log("CAMADAS v2: " + "; ".join(msg))
log(f"PESOS {NV} vertices, {len(BONES)} ossos usados, abas={ABAS}; maximo de ossos por vertice = "
    f"{int((W > 0).sum(axis=1).max())}; soma 1 em todos = {bool(np.allclose(W.sum(axis=1), 1))}")
# store as vertex groups on the uniform copy (canonical names) and save it
for g in list(uni.vertex_groups):
    uni.vertex_groups.remove(g)
for j, b in enumerate(BONES):
    g = uni.vertex_groups.new(name=CANON.get(b, b))
    for i in np.nonzero(W[:, j] > 0)[0]:
        g.add([int(i)], float(W[i, j]), "REPLACE")

# ---------------------------------------------------------------- equipment: vest and knapsack
# production meshes (build_equipamento_producao.py) by default; equip=blockout uses the Phase 3 blockout
EQD = os.path.join(ROOT, r"source\models\accessories\hcl_equipamento_pruss")
EQ = os.path.join(EQD, "hcl_equipamento_pruss_blockout.blend") if OPT.get("equip") == "blockout" else \
    OPT.get("equip", os.path.join(EQD, "hcl_equipamento_pruss_LOD0.blend"))
if FR and "equip" not in OPT:
    EQ = os.path.join(ROOT, r"source\models\accessories\hcl_equipamento_fr\hcl_equipamento_fr_LOD0.blend")
with bpy.data.libraries.load(EQ, link=False) as (src_, dst_):
    eq_names = [n for n in src_.objects if n.startswith(("HCL_V_", "HCL_B_"))]
eqo = {o.name: o for o in append(EQ, eq_names)}
vest = next(o for n, o in eqo.items() if n.startswith("HCL_V_"))
pack = next(o for n, o in eqo.items() if n.startswith("HCL_B_"))
EQ_KIND = "producao" if "hcl_partes" in pack.keys() else "blockout"
# the belts, the cartridge box and the scabbard hang from the coat and the waist belt: they copy the weights of the
# coat surface under them (coat body, collar, shoulder straps), never of the tails, sleeves or legs
host_parts = [parts.index(p) for p in ("casaco_corpo", "gola", "platina_E", "platina_D", "lapela_E", "lapela_D")
              if p in parts]
hf = [f for f, p in zip(FACES, FPART) if p in host_parts]
htree2 = BVHTree.FromPolygons([tuple(p) for p in V0], hf)


def host_weights(Vx):
    out = np.zeros((len(Vx), W.shape[1]))
    for k, v in enumerate(Vx):
        loc, _, fi, _ = htree2.find_nearest(Vector(v))
        f = hf[fi]
        for j, wj in zip(f, poly_3d_calc([Vector(V0[j]) for j in f], loc)):
            out[k] += wj * W[j]
    return limit4(out)


EV0 = np.array([v.co[:] for v in vest.data.vertices], np.float64)
KV0 = np.array([v.co[:] for v in pack.data.vertices], np.float64)
EW = host_weights(EV0)


def sub_vertices(ob_):
    """{piece name: set of vertex indices} of a production equipment mesh (face attribute hcl_part)."""
    out = {}
    if "hcl_partes" in ob_.keys():
        names = ob_["hcl_partes"].split(",")
        pa = ob_.data.attributes["hcl_part"].data
        for p in ob_.data.polygons:
            out.setdefault(names[pa[p.index].value], set()).update(p.vertices)
    return out


VSUB, KSUB = sub_vertices(vest), sub_vertices(pack)
if LAYERS == "v2" and VSUB:
    # P3 (weights v2): the cartridge box and the bayonet scabbard rest on the coat tails and swing with them. Each is
    # one rigid set (the mean of the weights of the tails and coat under it), so the tails under them can no longer
    # pass through when the thigh comes up; the crossbelt end and the frog blend into it over 5 cm.
    seat_host = faces_of(*[n for n in ("aba_E", "aba_D", "saia_E", "saia_D", "casaco_corpo") if n in PU])
    rigid_msg = []
    # the box is short and stiff: one rigid set. The scabbard is long and lies along the tail over the thigh: a rigid
    # scabbard cut through the bending tail (77 face pairs kneeling, against 41 with the coat's weights), so it follows
    # the surface under it point by point (it bends a little with the tail, like leather on cloth)
    for label, names, mode in (("cartucheira", ["cartucheira_corpo", "cartucheira_tampa", "cartucheira_placa",
                                               "cartucheira_presilha", "cartucheira_botao"], "rigida"),
                               ("bainha", ["bainha", "bainha_bocal", "bainha_ponteira", "baioneta_lamina",
                                           "baioneta_pescoco", "baioneta_alvado"], OPT.get("bainha", "segue"))):
        gi = sorted(set().union(*(VSUB.get(n, set()) for n in names)))
        if not gi:
            continue
        Wg = surf_w(seat_host, EV0[gi])
        R_ = limit4(Wg.mean(axis=0)[None, :])[0]
        EW[gi] = R_ if mode == "rigida" else limit4(Wg)
        if mode != "rigida" and VSUB.get("passador"):
            # the scabbard's throat hangs in the frog on the waist belt: near the frog it follows the frog (coat
            # weights), over 8 cm it hands over to the tail under it (the frog stayed put while the throat swung away)
            fr_ = sorted(VSUB["passador"])
            kdf = KDTree(len(fr_))
            for k_, i in enumerate(fr_):
                kdf.insert(EV0[i], k_)
            kdf.balance()
            for k_, i in enumerate(gi):
                _, j_, d_ = kdf.find(EV0[i])
                t_ = min(1.0, d_ / 0.08)
                f_ = 1 - t_ * t_ * (3 - 2 * t_)
                EW[i] = limit4(((1 - f_) * EW[i] + f_ * EW[fr_[j_]])[None, :])[0]
        kd_ = KDTree(len(gi))
        for k_, i in enumerate(gi):
            kd_.insert(EV0[i], k_)
        kd_.balance()
        gs, nb_ = set(gi), 0
        for i in range(len(EV0)):
            if i in gs or mode != "rigida":                      # a following scabbard needs no transition
                continue
            d_ = kd_.find(EV0[i])[2]
            if d_ < 0.05:
                t_ = d_ / 0.05
                f_ = 1 - t_ * t_ * (3 - 2 * t_)
                EW[i] = limit4(((1 - f_) * EW[i] + f_ * R_)[None, :])[0]
                nb_ += 1
        rigid_msg.append(f"{label} {mode} ({len(gi)} v.; media: " + ", ".join(f"{BONES[j]} {R_[j]:.2f}" for j in np.nonzero(R_)[0])
                         + f"; {nb_} v. em transicao)")
    log("CAMADAS v2 correame: " + "; ".join(rigid_msg))
# the knapsack body is stiff: one set of weights for all its points, the mean of the coat under it, spine bones only
KH = host_weights(KV0)
km = KH.mean(axis=0)
km[[j for j, b in enumerate(BONES) if not b.startswith("spine")]] = 0
KR = limit4(km[None, :])[0]
KW = np.repeat(KR[None, :], len(KV0), axis=0)
# its white shoulder straps lie on the shoulders and the chest: they follow the coat under them, blending into the
# rigid set near the pack (0 at the pack, full at 6 cm and beyond); the roll straps stay on the roll, so stay rigid
from mathutils.kdtree import KDTree
sv_, bv_ = set(), set()
if EQ_KIND == "producao":                        # shoulder straps with their buckles, tips and keepers
    pparts = pack["hcl_partes"].split(",")
    ppa = pack.data.attributes["hcl_part"].data
    is_strap = lambda p: pparts[ppa[p.index].value].startswith("correia_ombro")
else:                                            # blockout: every white strap (the roll straps stay on the roll)
    is_strap = lambda p: pack.data.materials[p.material_index].name.startswith("HCL_couro_branco")
for p in pack.data.polygons:
    (sv_ if is_strap(p) else bv_).update(p.vertices)
kdb = KDTree(len(bv_))
for i in bv_:
    kdb.insert(KV0[i], i)
kdb.balance()
nstrap = 0
# P4 (weights v2): where a shoulder strap lies on the vest's belts it must follow them fully, even close to the pack
# (the belts follow the coat at the shoulders; a half-rigid strap there let them through when lying prone)
vest_tree = BVHTree.FromPolygons([tuple(p) for p in EV0], [list(p.vertices) for p in vest.data.polygons])
n_on_vest = 0
for i in sorted(sv_ - bv_):
    t = min(1.0, kdb.find(KV0[i])[2] / 0.06)
    t = t * t * (3 - 2 * t)
    if LAYERS == "v2":
        dv = vest_tree.find_nearest(Vector(KV0[i]))[3]
        tv = 1 - min(1.0, max(0.0, (dv - 0.008) / 0.017)) ** 2 * (3 - 2 * min(1.0, max(0.0, (dv - 0.008) / 0.017)))
        n_on_vest += tv > 0.5
        t = max(t, tv)
    if t > 0:
        KW[i] = limit4(((1 - t) * KR + t * KH[i])[None, :])[0]
        nstrap += 1
log("EQUIPAMENTO (%s, %s): correame %d vertices (pesos copiados da casaca), mochila %d vertices "
    "(corpo rigido: %s; %d pontos das correias de ombro seguem a casaca)"
    % (EQ_KIND, os.path.basename(EQ), len(EV0), len(KV0), ", ".join(f"{BONES[j]} {KR[j]:.2f}" for j in np.nonzero(KR)[0]),
       nstrap) + (f"; {int(n_on_vest)} pontos das correias sobre o correame seguem-no por inteiro" if LAYERS == "v2" else ""))
for ob_, Wx in ((vest, EW), (pack, KW)):                         # keep the equipment weights as vertex groups too
    for g in list(ob_.vertex_groups):
        ob_.vertex_groups.remove(g)
    for j, b in enumerate(BONES):
        idx = np.nonzero(Wx[:, j] > 0)[0]
        if len(idx):
            g = ob_.vertex_groups.new(name=CANON.get(b, b))
            for i in idx:
                g.add([int(i)], float(Wx[i, j]), "REPLACE")
if "pesos_out" in OPT:                                            # weights v0 for the Phase 7 / in-game test build
    bpy.data.libraries.write(OPT["pesos_out"], {uni, vest, pack}, fake_user=True)
    log(f"PESOS gravados em {OPT['pesos_out']}")
NU, NE = NV, len(EV0)
FACES = FACES + [[i + NU for i in p.vertices] for p in vest.data.polygons] + \
    [[i + NU + NE for i in p.vertices] for p in pack.data.polygons]
parts = parts + ["correame", "mochila"]
PSIDE = PSIDE + [0, 0]
FPART = np.concatenate([FPART, np.full(len(vest.data.polygons), len(parts) - 2), np.full(len(pack.data.polygons), len(parts) - 1)])
V0 = np.vstack([V0, EV0, KV0])
W = np.vstack([W, EW, KW])
NV = len(V0)
SUBNAME = [""] * NV                                               # equipment piece of each vertex (diagnosis)
for off, sub in ((NU, VSUB), (NU + NE, KSUB)):
    for n_, vs_ in sub.items():
        for i in vs_:
            SUBNAME[off + i] = n_
vpart = np.full(NV, -1)
for fi, f in enumerate(FACES):
    vpart[f] = FPART[fi]

# ---------------------------------------------------------------- game head (TemplateRTM/bust.p3d), posed too
# bust.p3d Resolution 1 is the head the game draws (texture a3\characters_f\heads\data\m_white_01_co, whole neck down
# to 1.476 m, its nape and bib fitting A3_character_example). Until 2026-10-12 the test used the head of the animation
# body TemplateRTM\Male.p3d, filtered by bone weight, which lost most of the neck: the collar was fitted to the wrong
# neck (docs/reports/gola_pruss_v2.md).
bust = read_mlod(os.path.join(A, "TemplateRTM", "bust.p3d"))[0]
mp = np.array([to_blender(p) for p in bust["points"]], np.float64)
mW = {}
for name, blob in bust["selections"].items():
    n = name.lower()
    if n in PARENT or n in ("pelvis",):
        for i, b in enumerate(blob):
            if b:
                mW.setdefault(i, {})[n] = weight_of_byte(b)
hface = [list(dict.fromkeys(f)) for f in bust["faces"] if len(set(f)) >= 3]
hidx = sorted({i for f in hface for i in f})
remap = {i: k for k, i in enumerate(hidx)}
HF = [[remap[i] for i in f] for f in hface]
HV0 = mp[hidx]
HB = sorted({b for i in hidx for b in mW.get(i, {})} | {"head"})
HW = np.zeros((len(hidx), len(HB)))
for k, i in enumerate(hidx):
    for b, w in mW.get(i, {}).items():
        HW[k, HB.index(b)] = w
    if HW[k].sum() <= 0:
        HW[k, HB.index("head")] = 1.0
HW /= HW.sum(axis=1, keepdims=True)
log(f"CABECA do jogo (bust.p3d, Samples): {len(HF)} faces, {len(hidx)} vertices, altura "
    f"{HV0[:, 2].min() + 1.0069:.3f}..{HV0[:, 2].max() + 1.0069:.3f} m, ossos {HB[:8]}...")

SV0 = np.array([v.co[:] for v in shk.data.vertices], np.float64)
SF = [list(p.vertices) for p in shk.data.polygons]
# the badge variants (eagle, star) have their own meshes: test all three shako models
SHV = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss\variantes")
SHAKOS = {"fwr": shk}
for k_ in ("aguia", "estrela"):
    SHAKOS[k_] = next(o for o in append(os.path.join(SHV, f"hcl_shako_pruss_{k_}_LOD0.blend"), ["HCL_Shako_Pruss_LOD0"])
                      if o.name.startswith("HCL_Shako"))
SHK_V = {k: (np.array([v.co[:] for v in o.data.vertices], np.float64), [list(p.vertices) for p in o.data.polygons])
         for k, o in SHAKOS.items()}

# ---------------------------------------------------------------- checks
PAIRS = [  # (inner, outer): the inner layer must stay under the outer one
    ("calca_assento", "aba_E"), ("calca_assento", "aba_D"), ("calca_perna_E", "aba_E"), ("calca_perna_D", "aba_D"),
    ("calca_perna_E", "aba_D"), ("calca_perna_D", "aba_E"),
    ("calca_assento", "casaco_corpo"), ("calca_perna_E", "casaco_corpo"), ("calca_perna_D", "casaco_corpo"),
    ("manga_E", "punho_E"), ("manga_D", "punho_D"), ("maos_template", "punho_E"), ("maos_template", "punho_D"),
    ("maos_template", "manga_E"), ("maos_template", "manga_D"),
    ("calca_perna_E", "polaina_E"), ("calca_perna_D", "polaina_D"), ("sapato_E", "polaina_E"), ("sapato_D", "polaina_D"),
    ("casaco_corpo", "gola"), ("casaco_corpo", "platina_E"), ("casaco_corpo", "platina_D"),
    ("casaco_corpo", "manga_E"), ("casaco_corpo", "manga_D"), ("punho_E", "pala_E"), ("punho_D", "pala_D"),
    # equipment over the uniform
    ("casaco_corpo", "correame"), ("platina_E", "correame"), ("platina_D", "correame"), ("aba_E", "correame"),
    ("aba_D", "correame"), ("casaco_corpo", "mochila"), ("platina_E", "mochila"), ("platina_D", "mochila"),
    ("gola", "mochila"), ("correame", "mochila"),
    # greatcoat skirt
    ("calca_assento", "saia_E"), ("calca_assento", "saia_D"), ("calca_perna_E", "saia_E"), ("calca_perna_D", "saia_D"),
    ("calca_perna_E", "saia_D"), ("calca_perna_D", "saia_E"), ("casaco_corpo", "saia_E"), ("casaco_corpo", "saia_D"),
    ("saia_D", "saia_E"), ("saia_E", "correame"), ("saia_D", "correame"),
    # elite epaulettes (build_casaca_elite_fr.py)
    ("manga_E", "dragona_franja_E"), ("manga_D", "dragona_franja_D"), ("casaco_corpo", "dragona_corpo_E"),
    ("casaco_corpo", "dragona_corpo_D"), ("manga_E", "dragona_corpo_E"), ("manga_D", "dragona_corpo_D"),
]
PID = {p: i for i, p in enumerate(parts)}
part_faces = {p: [FACES[i] for i in np.nonzero(FPART == PID[p])[0]] for p in parts}
part_fidx = {p: np.nonzero(FPART == PID[p])[0] for p in parts}
part_verts = {p: np.unique(np.concatenate([np.array(f) for f in part_faces[p]])) for p in parts if part_faces[p]}


def vnormals(P):
    N = np.zeros_like(P)
    for f in FACES:
        a, b, c = P[f[0]], P[f[1]], P[f[2]]
        n = np.cross(b - a, c - a)
        N[f] += n
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def trees(P):
    lst = [tuple(p) for p in P]
    return {p: BVHTree.FromPolygons(lst, part_faces[p]) for p in parts if part_faces[p]}


def covered(P, N, T, outer, i):
    """Ray from the inner vertex along its own outward normal hits the outer part within 5 cm (independent of the
    outer part's face orientation, so cloth + lining pairs count correctly)."""
    o, n = Vector(P[i]), Vector(N[i])
    return T[outer].ray_cast(o + n * 1e-4, n, 0.05)[0] is not None


def poked(P, N, T, outer, i):
    """Inner vertex is outside the outer part: nothing of it above, and the outer part is behind the vertex.
    Returns the depth (distance to the outer part behind) or 0."""
    o, n = Vector(P[i]), Vector(N[i])
    if T[outer].ray_cast(o + n * 1e-4, n, 0.05)[0] is not None:
        return 0.0
    hit = T[outer].ray_cast(o - n * 1e-4, -n, 0.05)
    return hit[3] if hit[0] is not None else 0.0


REST_T = trees(V0)
N0 = vnormals(V0)
COVER = {}
for inner, outer in PAIRS:
    if inner in part_verts and outer in part_verts:
        COVER[(inner, outer)] = [i for i in part_verts[inner] if covered(V0, N0, REST_T, outer, i)]
log("COBERTURA no repouso (vertices da camada de baixo cobertos pela de cima): " +
    ", ".join(f"{a}<{b}={len(c)}" for (a, b), c in COVER.items() if c))

# sanity check of the skinning convention on the official body itself (its own weights)
BB = sorted({b for d in body.W for b in d})
BW = np.zeros((len(body.pts), len(BB)))
for i, d in enumerate(body.W):
    for b, w in d.items():
        BW[i, BB.index(b)] = w
okb = BW.sum(axis=1) > 0
BW[okb] /= BW[okb].sum(axis=1, keepdims=True)
BV0 = np.array([p[:] for p in body.pts], np.float64)
BE = np.array(body.edges)
BE = BE[okb[BE[:, 0]] & okb[BE[:, 1]]]
BL0 = np.linalg.norm(BV0[BE[:, 0]] - BV0[BE[:, 1]], axis=1)
BIDX = np.array(body.idx)


# body regions (dominant bone of each face) to tell garment contacts caused by the animation itself
def region_of_bone(b):
    for side, s in (("left", "E"), ("right", "D")):
        if b.startswith(side):
            return ("perna_" if any(k in b for k in ("upleg", "leg", "foot", "toe")) else "braco_") + s
    return "tronco"


BREG = []
for f in body.faces:
    acc = {}
    for i in f:
        for b, w in body.W[i].items():
            acc[b] = acc.get(b, 0) + w
    BREG.append(region_of_bone(max(acc, key=acc.get)) if acc else "tronco")
REGIONS = ["tronco", "braco_E", "braco_D", "perna_E", "perna_D"]
reg_faces = {g: [body.faces[k] for k in range(len(body.faces)) if BREG[k] == g] for g in REGIONS}
PART_REG = {"casaco_corpo": "tronco", "gola": "tronco", "aba_E": "tronco", "aba_D": "tronco", "platina_E": "tronco",
            "platina_D": "tronco", "calca_assento": "tronco", "botoes": "tronco",
            "manga_E": "braco_E", "punho_E": "braco_E", "pala_E": "braco_E", "manga_D": "braco_D", "punho_D": "braco_D",
            "pala_D": "braco_D", "calca_perna_E": "perna_E", "polaina_E": "perna_E", "sapato_E": "perna_E",
            "calca_perna_D": "perna_D", "polaina_D": "perna_D", "sapato_D": "perna_D",
            "correame": "tronco", "mochila": "tronco", "saia_E": "perna_E", "saia_D": "perna_D",
            "dragona_corpo_E": "tronco", "dragona_corpo_D": "tronco", "dragona_meialua_E": "braco_E",
            "dragona_meialua_D": "braco_D", "dragona_franja_E": "braco_E", "dragona_franja_D": "braco_D"}


def body_region_pairs(BP):
    lst = [tuple(p) for p in BP]
    T = {g: BVHTree.FromPolygons(lst, reg_faces[g]) for g in REGIONS}
    out = {}
    for a in range(len(REGIONS)):
        for b in range(a + 1, len(REGIONS)):
            ga, gb = REGIONS[a], REGIONS[b]
            n = 0
            for i, j in T[ga].overlap(T[gb]):
                if not set(reg_faces[ga][i]) & set(reg_faces[gb][j]):
                    n += 1
            out[(ga, gb)] = n
    return out


BODY_REST = body_region_pairs(BV0)
ht0 = BVHTree.FromPolygons([tuple(p) for p in HV0], HF)
st0 = BVHTree.FromPolygons([tuple(p) for p in SV0], SF)
HEAD_REST = sum(len(ht0.overlap(REST_T[p])) for p in ("gola", "casaco_corpo", "platina_E", "platina_D"))
EQUIP = ("correame", "mochila")


def shako_hits(T, Rh, th):
    """Faces pairs of each shako model (rigid on the head bone) against the uniform, the vest and the knapsack."""
    out = {}
    for k_, (sv, sf) in SHK_V.items():
        t_ = BVHTree.FromPolygons([tuple(p) for p in sv @ Rh.T + th], sf)
        out[k_] = {"uniforme": sum(len(t_.overlap(T[p])) for p in parts if p in T and p not in EQUIP),
                   "correame": len(t_.overlap(T["correame"])), "mochila": len(t_.overlap(T["mochila"]))}
    return out


SHK_REST = shako_hits(REST_T, np.eye(3), np.zeros(3))
log(f"REPOUSO cabeca oficial x gola/casaco/platinas: {HEAD_REST} pares; barretinas x uniforme/correame/mochila: "
    + "; ".join(f"{k}: {v['uniforme']}/{v['correame']}/{v['mochila']}" for k, v in SHK_REST.items())
    + f"; barretina x cabeca do jogo (bust.p3d): {len(st0.overlap(ht0))} pares (a barretina foi ajustada ao template "
    f"de item de cabeca, nao a esta cabeca)")


def pair_set(T, P):
    pairs = set()
    names = [p for p in parts if p in T]
    for a in range(len(names)):
        for b in range(a, len(names)):
            pa, pb = names[a], names[b]
            for i, j in T[pa].overlap(T[pb]):
                fa, fb = part_fidx[pa][i], part_fidx[pb][j]
                if pa == pb and (fa >= fb or set(FACES[fa]) & set(FACES[fb])):
                    continue
                pairs.add((pa, pb, int(fa), int(fb)))
    return pairs


REST_PAIRS = pair_set(REST_T, V0)

# pieces that touch at rest must stay together: for every vertex, its nearest vertex on ANOTHER mesh piece within 5 mm
from mathutils.kdtree import KDTree
root_ = list(range(NV))


def find_(a):
    while root_[a] != a:
        root_[a] = root_[root_[a]]; a = root_[a]
    return a


for f in FACES:
    for a in f[1:]:
        ra, rb = find_(f[0]), find_(a)
        if ra != rb:
            root_[ra] = rb
island = np.array([find_(i) for i in range(NV)])
kd = KDTree(NV)
for i in range(NV):
    kd.insert(V0[i], i)
kd.balance()
TOUCH = []
for i in range(NV):
    for co, j, d in kd.find_range(V0[i], 0.005):
        # left and right pieces (legs, tails at the back vent) are meant to move apart
        if island[j] != island[i] and PSIDE[vpart[i]] * PSIDE[vpart[j]] != -1:
            TOUCH.append((i, j, d)); break
TOUCH = np.array(TOUCH)
TI, TJ, TD0 = TOUCH[:, 0].astype(int), TOUCH[:, 1].astype(int), TOUCH[:, 2]
log(f"CONTATO no repouso: {len(TI)} vertices encostados (<= 5 mm) em outra peca da malha")
EDGES = np.array(sorted({(min(a, b), max(a, b)) for f in FACES for a, b in zip(f, f[1:] + f[:1])}))
EPART = vpart[EDGES[:, 0]]
L0 = np.linalg.norm(V0[EDGES[:, 0]] - V0[EDGES[:, 1]], axis=1)
log(f"REPOUSO: {len(REST_PAIRS)} pares de faces que já se cruzam de propósito (junções), usados como linha de base")

results = {}
worst_frames = {}
for pid, label, rel, step in POSES:
    r = read_rtm(os.path.join(A, rel))
    frames = list(range(0, len(r["frames"]), step))
    agg = {"poke": {}, "new": {}, "stretch": {}, "head": 0, "shako": {}, "frames": len(frames), "worst": (0, -1)}
    for fr in frames:
        fm = frame_mats(r["frames"][fr][1])
        P = skin(V0, W, BONES, fm)
        T = trees(P)
        NP = vnormals(P)
        score = 0.0
        BP = skin(BV0, BW, BB, fm)
        if fr == frames[0]:
            BL = np.linalg.norm(BP[BE[:, 0]] - BP[BE[:, 1]], axis=1) / BL0
            agg["body"] = (float(BP[BIDX, 2].min()), float(BP[BIDX, 2].max()), float(np.percentile(BL, 99)),
                           float(np.mean((BL > 1.3) | (BL < 0.7)) * 100))
        for k, n in body_region_pairs(BP).items():
            agg.setdefault("bodyc", {})[k] = max(agg.get("bodyc", {}).get(k, 0), n - BODY_REST[k])
        # 1. layers: inner vertices that were under the outer layer at rest and are now outside it
        for (inner, outer), cov in COVER.items():
            if not cov:
                continue
            dd_ = [(i, poked(P, NP, T, outer, i)) for i in cov]
            bad = [d for _, d in dd_ if d > 0.002]
            if bad:
                c = agg["poke"].setdefault((inner, outer), [0, 0.0, 0, ""])
                if len(bad) >= c[0] and inner in EQUIP:          # which equipment pieces come through (diagnosis)
                    cnt_ = {}
                    for i, d in dd_:
                        if d > 0.002:
                            cnt_[SUBNAME[i]] = cnt_.get(SUBNAME[i], 0) + 1
                    c[3] = ", ".join(f"{k} {v}" for k, v in sorted(cnt_.items(), key=lambda kv: -kv[1]))
                    if outer == "mochila":                       # inside the closed pack body = not visible
                        kb_ = KSUB.get("mochila_corpo", set()) | KSUB.get("mochila_tampa", set())
                        kbf = [f for f in part_faces["mochila"] if all((j - NU - NE) in kb_ for j in f)]
                        tb_ = BVHTree.FromPolygons([tuple(p) for p in P], kbf)
                        nin = 0
                        for i, d in dd_:
                            if d > 0.002:
                                hits, o_ = 0, Vector(P[i])
                                for _ in range(20):
                                    h_ = tb_.ray_cast(o_, Vector((0.0, 0.0, 1.0)), 1.0)
                                    if h_[0] is None:
                                        break
                                    hits += 1; o_ = h_[0] + Vector((0.0, 0.0, 1e-5))
                                nin += hits % 2
                        c[3] += f"; dentro do corpo fechado da mochila: {nin}"
                if len(bad) >= c[0] and inner == "maos_template":   # where on the hand (mm along the forearm from the wrist)
                    s_ = 1 if outer.endswith("_E") else -1
                    wr_, el_ = np.array(JB[("wrist", s_)]), np.array(JB[("elbow", s_)])
                    fd_ = (wr_ - el_) / np.linalg.norm(wr_ - el_)
                    al_ = sorted(round(float((V0[i] - wr_) @ fd_) * 1000) for i, d in dd_ if d > 0.002)
                    c[3] = f"posicao no antebraco (mm a partir do pulso, + = para a mao): {al_}"
                c[0] = max(c[0], len(bad)); c[1] = max(c[1], max(bad)); c[2] = len(cov)
                if inner == "maos_template" and max(bad) > agg.setdefault("wh", (0.0, -1))[0]:
                    agg["wh"] = (max(bad), fr)
                score += len(bad) * max(bad)
        # 1b. pieces that touched at rest and moved apart (a button leaving the cloth, a turnback leaving its tail)
        gap = np.linalg.norm(P[TI] - P[TJ], axis=1) - TD0
        for p in parts:
            m = vpart[TI] == PID[p]
            if m.any():
                g = agg.setdefault("gap", {}).setdefault(p, [0.0, 0, ""])
                k_ = int(np.argmax(np.where(m, gap, -1)))
                if gap[k_] > g[0]:
                    g[0] = float(gap[k_]); g[2] = parts[vpart[TJ[k_]]]
                g[1] = max(g[1], int((gap[m] > 0.005).sum()))
        score += float(np.sum(gap[gap > 0.005]))
        # 2. new intersections between parts (not present at rest)
        new = pair_set(T, P) - REST_PAIRS
        cnt = {}
        sub_cnt = {}
        for pa, pb, fa, fb in new:
            cnt[(pa, pb)] = cnt.get((pa, pb), 0) + 1
            if pa in EQUIP or pb in EQUIP:                       # equipment pieces involved (diagnosis)
                ka = (pa, pb, SUBNAME[FACES[fa][0]] or pa, SUBNAME[FACES[fb][0]] or pb)
                sub_cnt[ka] = sub_cnt.get(ka, 0) + 1
        for (pa, pb, sa, sb), c_ in sub_cnt.items():
            d_ = agg.setdefault("new_sub", {}).setdefault((pa, pb), {})
            d_[(sa, sb)] = max(d_.get((sa, sb), 0), c_)
        for k, c in cnt.items():
            agg["new"][k] = max(agg["new"].get(k, 0), c)
        score += 0.001 * len(new)
        # 3. stretch per part
        L = np.linalg.norm(P[EDGES[:, 0]] - P[EDGES[:, 1]], axis=1) / np.maximum(L0, 1e-6)
        for p in parts:
            m = EPART == PID[p]
            if not m.any():
                continue
            s = agg["stretch"].setdefault(p, [9.0, 0.0, 0.0])
            s[0] = min(s[0], float(L[m].min())); s[1] = max(s[1], float(L[m].max()))
            s[2] = max(s[2], float(np.mean((L[m] > 1.3) | (L[m] < 0.7)) * 100))
        # 4. official head against the collar and the coat; shako (rigid on the head) against the uniform
        HP = skin(HV0, HW, HB, fm)
        ht = BVHTree.FromPolygons([tuple(p) for p in HP], HF)
        Rh, th = bone_mat(fm, "head")
        agg["head"] = max(agg["head"], sum(len(ht.overlap(T[p])) for p in ("gola", "casaco_corpo", "platina_E", "platina_D")))
        sh = shako_hits(T, Rh, th)
        for k_, d_ in sh.items():
            a_ = agg["shako"].setdefault(k_, {})
            for w_, n_ in d_.items():
                a_[w_] = max(a_.get(w_, 0), n_)
        score += 0.01 * sum(d_["mochila"] + d_["correame"] for d_ in sh.values())
        if score >= agg["worst"][0]:
            agg["worst"] = (score, fr)
    results[pid] = agg
    worst_frames[pid] = (r, agg["wh"][1] if OPT.get("pior") == "maos" and agg.get("wh", (0, -1))[1] >= 0
                         else agg["worst"][1])
    log()
    log(f"== {pid}: {label}  ({os.path.basename(rel)}, {agg['frames']} quadros avaliados)")
    zb0, zb1, bl99, bpc = agg["body"]
    log(f"   REFERENCIA corpo oficial posado com os proprios pesos: altura {zb0:+.3f} .. {zb1:+.3f} m; "
        f"{bpc:4.1f}% das arestas fora de 0,7-1,3x (99% ate {bl99:.2f}x)")
    if agg["poke"]:
        for (inner, outer), (n, dmax, ncov, sub_) in sorted(agg["poke"].items(), key=lambda kv: -kv[1][0] * kv[1][1]):
            log(f"   CAMADA  {inner:14s} sai por fora de {outer:13s}: {n:4d} de {ncov:4d} vertices, ate {dmax * 1000:5.1f} mm"
                + (f"  [{sub_}]" if sub_ else ""))
    else:
        log("   CAMADA  nenhuma camada interna saiu por fora (> 2 mm)")
    seps = [(p, g) for p, g in agg.get("gap", {}).items() if g[1] > 0]
    for p, (gmax, n, other) in sorted(seps, key=lambda kv: -kv[1][0]):
        log(f"   SEPARA  {p:14s}: {n:4d} vertices se afastaram > 5 mm de outra peca; o maior, {gmax * 1000:5.1f} mm, de {other}")
    if not seps:
        log("   SEPARA  nenhuma peca se afastou > 5 mm da vizinha")
    for (pa, pb), c in sorted(agg["new"].items(), key=lambda kv: -kv[1])[:12]:
        ra, rb = PART_REG.get(pa), PART_REG.get(pb)
        note = ""
        if pa == pb == "maos_template":
            note = "  (dedos da malha oficial do template fechando na empunhadura)"
        elif ra and rb and ra != rb:
            key = (ra, rb) if REGIONS.index(ra) < REGIONS.index(rb) else (rb, ra)
            nb_ = agg["bodyc"].get(key, 0)
            note = f"  (corpo oficial {key[0]} x {key[1]}: {nb_} pares novos" + (" -> a pose encosta)" if nb_ > 0 else ")")
        sd_ = agg.get("new_sub", {}).get((pa, pb))
        if sd_:
            note += "  [" + ", ".join(f"{a_}x{b_} {n_}" for (a_, b_), n_ in sorted(sd_.items(), key=lambda kv: -kv[1])[:4]) + "]"
        log(f"   CRUZA   {pa:14s} x {pb:14s}: {c:5d} pares de faces novos{note}")
    for p, (mn, mx, pc) in sorted(agg["stretch"].items(), key=lambda kv: -kv[1][2])[:6]:
        log(f"   ESTICA  {p:14s}: arestas {mn:4.2f}x .. {mx:4.2f}x do repouso; {pc:4.1f}% fora de 0,7-1,3x")
    log(f"   CABECA  cabeca oficial x gola/casaco/platinas: {agg['head']} pares de faces (repouso: {HEAD_REST})")
    log("   BARRETINA x uniforme / correame / mochila (pares de faces; repouso entre parenteses): " + "; ".join(
        f"{k}: {v['uniforme']} ({SHK_REST[k]['uniforme']}) / {v['correame']} ({SHK_REST[k]['correame']}) / "
        f"{v['mochila']} ({SHK_REST[k]['mochila']})" for k, v in agg["shako"].items()))

uni.name = UNI_NAME + "_pesos"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"teste_movimentos_{TAG}.blend"))
open(os.path.join(OUT, f"teste_movimentos_{TAG}_output.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")

# ---------------------------------------------------------------- renders (worst frame of each animation)
if "norender" in ARGS or FR:
    sys.exit(0)
TXU = os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss")
TXS = os.path.join(ROOT, r"source\textures\hcl_shako_pruss")


def tex_material(name, co, nohq, smdi):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]
    ic = nt.nodes.new("ShaderNodeTexImage"); ic.image = bpy.data.images.load(co)
    inn = nt.nodes.new("ShaderNodeTexImage"); inn.image = bpy.data.images.load(nohq); inn.image.colorspace_settings.name = "Non-Color"
    isd = nt.nodes.new("ShaderNodeTexImage"); isd.image = bpy.data.images.load(smdi); isd.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); sep = nt.nodes.new("ShaderNodeSeparateColor")
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(ic.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(inn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(isd.outputs["Color"], sep.inputs["Color"]); nt.links.new(sep.outputs["Blue"], inv.inputs[1])
    nt.links.new(inv.outputs["Value"], bsdf.inputs["Roughness"]); nt.links.new(sep.outputs["Green"], bsdf.inputs["Specular IOR Level"])
    return m


skin_m = bpy.data.materials.new("REF_pele"); skin_m.use_nodes = True
skin_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.58, 0.46, 1)
mu = tex_material("M_V01", os.path.join(TXU, "hcl_u_pruss1813_v01_co.png"), os.path.join(TXU, "hcl_u_pruss1813_nohq.png"),
                  os.path.join(TXU, "hcl_u_pruss1813_smdi.png"))
ms = tex_material("M_shako", os.path.join(TXS, "hcl_shako_pruss_co.png"), os.path.join(TXS, "hcl_shako_pruss_nohq.png"),
                  os.path.join(TXS, "hcl_shako_pruss_smdi.png"))
for i, slot in enumerate(uni.material_slots):
    slot.link = "OBJECT"
    slot.material = skin_m if uni.data.materials[i].name.startswith("HCL_pele") else mu
for p in uni.data.polygons:
    p.use_smooth = True
for slot in shk.material_slots:
    slot.link = "OBJECT"; slot.material = ms
hm = bpy.data.meshes.new("cabeca_jogo_bust_p3d")
hm.from_pydata([tuple(p) for p in HV0], [], HF)
head_ob = bpy.data.objects.new("REF_cabeca_jogo_bust_p3d", hm)
bpy.context.scene.collection.objects.link(head_ob)
head_ob.data.materials.append(skin_m)
for p in hm.polygons:
    p.use_smooth = True
floor = bpy.data.objects.new("chao", bpy.data.meshes.new("chao"))
floor.data.from_pydata([(-4, -4, 0), (4, -4, 0), (4, 4, 0), (-4, 4, 0)], [], [[0, 1, 2, 3]])
fm_ = bpy.data.materials.new("chao"); fm_.use_nodes = True
fm_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1)
floor.data.materials.append(fm_)
bpy.context.scene.collection.objects.link(floor)
scene = bpy.context.scene
for nm_, en, rot in (("sol", 3.2, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 130))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a_) for a_ in rot); scene.collection.objects.link(lo)
world = bpy.data.worlds.new("mundo"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.90, 0.90, 0.90, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
scene.world = world
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = int(OPT.get("samples", 32))
scene.view_settings.view_transform = "Standard"
scene.render.resolution_x = scene.render.resolution_y = 1100
cam_ob = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam_ob)
scene.camera = cam_ob


def set_coords(ob, P):
    ob.data.vertices.foreach_set("co", np.asarray(P, np.float32).ravel())
    ob.data.update()


def set_pose(P, HP, SP):
    set_coords(uni, P[:NU]); set_coords(vest, P[NU:NU + NE]); set_coords(pack, P[NU + NE:])
    set_coords(head_ob, HP); set_coords(shk, SP)


for k_, o in SHAKOS.items():                                     # single-pose shots use the FWR shako
    o.hide_render = k_ != "fwr"
TXE = os.path.join(ROOT, r"source\textures\hcl_equipamento_pruss")
for o, pre in ((vest, "hcl_v_pruss1813_correame"), (pack, "hcl_b_pruss1813_tornister")):
    if EQ_KIND == "producao" and os.path.exists(os.path.join(TXE, pre + "_co.png")):
        me_ = tex_material("M_" + pre, *(os.path.join(TXE, f"{pre}_{k}.png") for k in ("co", "nohq", "smdi")))
        for slot in o.material_slots:
            slot.link = "OBJECT"; slot.material = me_
    for p in o.data.polygons:
        p.use_smooth = EQ_KIND == "producao"
ONLY_GAL = "so_galeria" in ARGS
ONLY_POSES = OPT["poses"].split(",") if "poses" in OPT else None
SEATED = {"sentado", "sentado_mira", "morte", "binoculo"}
crate_m = bpy.data.materials.new("caixote"); crate_m.use_nodes = True
crate_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.42, 0.30, 0.18, 1)


def add_crate(name, seat):
    """A plain crate where the vehicle seat would be (FFV poses are authored relative to a seat)."""
    top = float(seat[:, 2].min())
    cx, cy = float(seat[:, 0].mean()), float(seat[:, 1].mean())
    cm = bpy.data.meshes.new(name)
    vs = [(cx + sx * 0.24, cy + sy * 0.24, z) for z in (0.0, top) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    cm.from_pydata(vs, [], [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])
    cm.materials.append(crate_m)
    o = bpy.data.objects.new(name, cm); scene.collection.objects.link(o)
    return o


for pid, label, rel, step in ([] if ONLY_GAL else POSES):
    if ONLY_POSES and pid not in ONLY_POSES:
        continue
    r, fr = worst_frames[pid]
    fm = frame_mats(r["frames"][max(fr, 0)][1])
    P = skin(V0, W, BONES, fm)
    HP = skin(HV0, HW, HB, fm)
    Rh, th = bone_mat(fm, "head")
    SP = SV0 @ Rh.T + th
    lift = np.array([0.0, 0.0, -min(P[:, 2].min(), SP[:, 2].min(), 0.0)])    # nothing below the floor
    P, HP, SP = P + lift, HP + lift, SP + lift
    crate = add_crate(f"caixote_{pid}", P[vpart == PID["calca_assento"]]) if pid in SEATED else None
    set_pose(P, HP, SP)
    allp = np.vstack([P, SP])
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    c = (lo + hi) / 2
    size = float(np.max(hi - lo))
    for view, d in (("3-4", (-0.55, -1.0, 0.30)), ("lado", (-1.0, -0.08, 0.12)), ("costas", (0.45, 1.0, 0.30))):
        d = Vector(d).normalized()
        cam_ob.location = Vector(c) + d * (size * 1.55 + 0.4)
        cam_ob.rotation_euler = (Vector(c) - cam_ob.location).to_track_quat("-Z", "Y").to_euler()
        cam_ob.data.lens = 50
        scene.render.filepath = os.path.join(OUT, f"{pid}_{view}.png")
        bpy.ops.render.render(write_still=True)
        print("render", scene.render.filepath)
    if "zoom" in OPT:                                    # close-ups of one piece (e.g. zoom=punho_D) in this frame
        cz = P[vpart == PID[OPT["zoom"]]].mean(axis=0)
        for view, d in (("a", (-0.3, -1.0, 0.25)), ("b", (1.0, 0.2, 0.3)), ("c", (0.2, 0.3, 1.0)), ("d", (-1.0, 0.3, -0.2))):
            d = Vector(d).normalized()
            cam_ob.location = Vector(cz) + d * 0.42
            cam_ob.rotation_euler = (Vector(cz) - cam_ob.location).to_track_quat("-Z", "Y").to_euler()
            cam_ob.data.lens = 50
            scene.render.filepath = os.path.join(OUT, f"{pid}_zoom_{OPT['zoom']}_{view}.png")
            bpy.ops.render.render(write_still=True)
            print("render", scene.render.filepath)
    if crate:
        bpy.data.objects.remove(crate)
if "sem_galeria" in ARGS:
    sys.exit(0)

# ---------------------------------------------------------------- gallery: the 8 uniforms and the 6 shakos, each soldier
# in a different animation, all with the vest and the knapsack (blockout). Pairings are for display only.
import json
VAR = json.load(open(os.path.join(TXU, "variantes_regimentos.json"), encoding="utf-8"))
SHT = {"fwr_amarela": ("fwr", os.path.join(TXS, "hcl_shako_pruss")),
       "fwr_branca": ("fwr", os.path.join(TXS, r"variantes\hcl_shako_pruss_fwr_branca")),
       "aguia_amarela": ("aguia", os.path.join(TXS, r"variantes\hcl_shako_pruss_aguia_amarela")),
       "aguia_branca": ("aguia", os.path.join(TXS, r"variantes\hcl_shako_pruss_aguia_branca")),
       "estrela_prata": ("estrela", os.path.join(TXS, r"variantes\hcl_shako_pruss_estrela_prata")),
       "estrela_latao": ("estrela", os.path.join(TXS, r"variantes\hcl_shako_pruss_estrela_latao"))}
GAL = [("V01", "em_pe", 0, "fwr_amarela"), ("V02", "agachado", 0, "fwr_branca"), ("V03", "deitado", 0, "aguia_amarela"),
       ("V04", "inventario", 0, "aguia_branca"), ("V05", "sentado", 0, "estrela_prata"),
       ("V06", "sentado_mira", 16, "estrela_latao"), ("V07", "morte", -1, "aguia_amarela"),
       ("V08", "binoculo", 16, "estrela_prata")]
anim_of = {pid: rel for pid, label, rel, step in POSES}
for o in (uni, vest, pack, head_ob) + tuple(SHAKOS.values()):
    o.hide_render = True
mat_cache = {}
log()
log("GALERIA (exibicao; uniforme e barretina sao itens independentes no jogo):")
for k, (vid, pid, frame, sk) in enumerate(GAL):
    r = read_rtm(os.path.join(A, anim_of[pid]))
    fr = frame if frame >= 0 else len(r["frames"]) - 1
    fm = frame_mats(r["frames"][fr][1])
    P = skin(V0, W, BONES, fm)
    HP = skin(HV0, HW, HB, fm)
    Rh, th = bone_mat(fm, "head")
    model, tex = SHT[sk]
    SP = SHK_V[model][0] @ Rh.T + th
    col, row = k % 4, k // 4
    off = np.array([(col - 1.5) * 2.1, row * 2.7, -min(P[:, 2].min(), SP[:, 2].min())])
    objs = []
    for src, Q in ((uni, P[:NU]), (vest, P[NU:NU + NE]), (pack, P[NU + NE:]), (head_ob, HP), (SHAKOS[model], SP)):
        o = bpy.data.objects.new(f"G_{vid}_{src.name}", src.data.copy())
        scene.collection.objects.link(o)
        set_coords(o, Q + off)
        objs.append(o)
    u_o, s_o = objs[0], objs[4]
    key = VAR[vid]["prefixo"]
    if key not in mat_cache:
        mat_cache[key] = tex_material(f"M_{vid}", os.path.join(TXU, key + "_co.png"), os.path.join(TXU, "hcl_u_pruss1813_nohq.png"),
                                      os.path.join(TXU, "hcl_u_pruss1813_smdi.png"))
    for i, slot in enumerate(u_o.material_slots):
        slot.link = "OBJECT"
        slot.material = skin_m if u_o.data.materials[i].name.startswith("HCL_pele") else mat_cache[key]
    if sk not in mat_cache:
        mat_cache[sk] = tex_material(f"S_{sk}", tex + "_co.png", tex + "_nohq.png", tex + "_smdi.png")
    for slot in s_o.material_slots:
        slot.link = "OBJECT"; slot.material = mat_cache[sk]
    if pid in SEATED:
        add_crate(f"caixote_{vid}", P[vpart == PID["calca_assento"]] + off)
    log(f"   {vid} ({VAR[vid]['nome']}) + barretina {sk}: animacao {pid}, quadro {fr}")
floor.scale = (3.0, 3.0, 1.0)
scene.render.resolution_x, scene.render.resolution_y = 2400, 1500
scene.cycles.samples = int(OPT.get("samples", 32))
for view, loc, tgt, lens in (("galeria_frente", (-5.5, -9.5, 4.2), (0.0, 1.35, 0.55), 40),
                             ("galeria_costas", (5.5, 12.2, 4.2), (0.0, 1.35, 0.55), 40)):
    cam_ob.location = loc
    cam_ob.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam_ob.data.lens = lens
    scene.render.filepath = os.path.join(OUT, f"{view}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)
open(os.path.join(OUT, f"teste_movimentos_{TAG}_output.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
