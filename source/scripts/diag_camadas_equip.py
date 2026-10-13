# Diagnosis: which vest (correame) vertices that lie under the knapsack at rest come out through it when posed, by part.
# Uses the weights file written by teste_movimentos.py (pesos_out) and the official sample animations.
#   blender -b --factory-startup --python diag_camadas_equip.py -- <project root> <samples dir> <weights .blend> [poses=a,b]
import bpy, sys, os, re
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtm_read import read_rtm

ROOT, SAMPLES, PES = sys.argv[sys.argv.index("--") + 1:][:3]
OPT = dict(a.split("=", 1) for a in sys.argv[sys.argv.index("--") + 4:] if "=" in a)
bpy.ops.wm.read_factory_settings(use_empty=True)
cfg = open(os.path.join(SAMPLES, r"Addons\TemplateRTM\model.cfg"), encoding="latin-1").read()
blk = re.sub(r"//[^\n]*", "", re.search(r"skeletonBones\[\]\s*=\s*\{(.*?)\};", cfg, re.S).group(1))
toks = re.findall(r'"([^"]*)"', blk)
PARENT = {toks[i].lower(): toks[i + 1].lower() for i in range(0, len(toks), 2)}
S_SWAP = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], np.float64)
POSES = {"em_pe": r"Test_Anims\AmovPercMstpSrasWrflDnon.rtm", "agachado": r"Test_Anims\AmovPknlMstpSrasWrflDnon.rtm",
         "deitado": r"Test_Anims\AmovPpneMstpSrasWrflDnon.rtm", "sentado": r"Test_FFV_Poses_F\Anim\ffv_01_idle1.rtm"}


def frame_mats(m_):
    out = {}
    for k, m in m_.items():
        if k.lower().startswith(("face_", "eye")):
            continue
        m = np.array(m, np.float64)
        out[k.lower()] = (S_SWAP @ m[:9].reshape(3, 3).T @ S_SWAP, S_SWAP @ m[9:])
    return out


def bone_mat(fm, b):
    while b and b not in fm:
        b = PARENT.get(b, "")
    return fm.get(b, (np.eye(3), np.zeros(3)))


with bpy.data.libraries.load(PES, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n.startswith(("HCL_V_", "HCL_B_"))]
vest = next(o for o in dst.objects if o.name.startswith("HCL_V_"))
pack = next(o for o in dst.objects if o.name.startswith("HCL_B_"))


def data(ob):
    V = np.array([v.co[:] for v in ob.data.vertices], np.float64)
    names = [g.name.lower() for g in ob.vertex_groups]
    W = {}
    for v in ob.data.vertices:
        for g in v.groups:
            W.setdefault(names[g.group], np.zeros(len(V)))[v.index] = g.weight
    F = [list(p.vertices) for p in ob.data.polygons]
    parts = ob["hcl_partes"].split(",")
    pa = ob.data.attributes["hcl_part"].data
    vp = np.empty(len(V), object)
    for p in ob.data.polygons:
        for i in p.vertices:
            vp[i] = parts[pa[p.index].value]
    fparts = [parts[pa[p.index].value] for p in ob.data.polygons]
    return V, W, F, vp, fparts


def skin(V, W, fm):
    P = np.zeros_like(V)
    for b, w in W.items():
        R, t = bone_mat(fm, b)
        P += w[:, None] * (V @ R.T + t)
    return P


def vnormals(P, F):
    N = np.zeros_like(P)
    for f in F:
        n = np.cross(P[f[1]] - P[f[0]], P[f[2]] - P[f[0]])
        N[f] += n
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


VV, VW, VF, VP, _ = data(vest)
KV, KW, KF, _, KFP = data(pack)
T0 = BVHTree.FromPolygons([tuple(p) for p in KV], KF)
N0 = vnormals(VV, VF)
cov = [i for i in range(len(VV)) if T0.ray_cast(Vector(VV[i]) + Vector(N0[i]) * 1e-4, Vector(N0[i]), 0.05)[0] is not None]
print("COBERTOS no repouso:", len(cov), {p: int((VP[cov] == p).sum()) for p in set(VP[cov])})
for pid in OPT.get("poses", "em_pe,sentado,deitado").split(","):
    r = read_rtm(os.path.join(SAMPLES, "Addons", POSES[pid]))
    worst = []
    for fr in range(0, len(r["frames"]), max(1, len(r["frames"]) // 8)):
        fm = frame_mats(r["frames"][fr][1])
        P, Q = skin(VV, VW, fm), skin(KV, KW, fm)
        N = vnormals(P, VF)
        T = BVHTree.FromPolygons([tuple(p) for p in Q], KF)
        for i in cov:
            o, n = Vector(P[i]), Vector(N[i])
            if T.ray_cast(o + n * 1e-4, n, 0.05)[0] is not None:
                continue
            hit = T.ray_cast(o - n * 1e-4, -n, 0.05)
            if hit[0] is not None and hit[3] > 0.002:
                worst.append((hit[3], i, fr, KFP[hit[2]]))
    worst.sort(reverse=True)
    seen = {}
    for d, i, fr, kp in worst:
        key = (VP[i], kp)
        seen[key] = max(seen.get(key, 0), d)
    print(f"POSE {pid}: " + "; ".join(f"{a} sai por {b}: ate {d * 1000:.1f} mm" for (a, b), d in sorted(seen.items(), key=lambda kv: -kv[1])))
    for d, i, fr, kp in worst[:5]:
        print(f"    {VP[i]} v{i} quadro {fr}: {d * 1000:.1f} mm por {kp}; repouso {np.round(VV[i], 3)}")
