# Shared fitting tools for clothing worn on the official Arma 3 body (Arma 3 Samples, A3_character_example.p3d):
# body loading in character space, bone-weight regions, joint estimates, exact cross-sections, convex-hull section
# profiles, polyline frames and lofting helpers.
# Used by build_uniforme_production.py and the equipment scripts. Runs inside Blender (bmesh / mathutils).
#
# Conventions (verified on the Samples): Blender axes +Z up, front -Y, character's left +X; the P3D origin is
# 1.007 m above the ground. Heights h are metres above the ground; Body.Z(h) converts to z.
import math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import convex_hull_2d
import bmesh
from p3d_mlod import read_mlod, to_blender

NS = 72                                           # angular samples of a section profile
UP, FRONT = Vector((0, 0, 1)), Vector((0, -1, 0))
BONES = """pelvis spine spine1 spine2 spine3 neck head leftshoulder leftarm leftarmroll leftforearm leftforearmroll
lefthand rightshoulder rightarm rightarmroll rightforearm rightforearmroll righthand leftupleg leftuplegroll leftleg
leftlegroll leftfoot lefttoebase rightupleg rightuplegroll rightleg rightlegroll rightfoot righttoebase""".split()


def weight_of_byte(b):
    """MLOD selection byte -> weight (verified on the Samples: 1 = full weight, pairs sum to 1)."""
    return (256 - b) / 255.0


class Body:
    def __init__(self, path, lod_index=0):
        lod = read_mlod(path)[lod_index]
        self.lod = lod
        self.pts = [Vector(to_blender(p)) for p in lod["points"]]
        self.W = [dict() for _ in self.pts]
        self.proxy = set()
        for name, blob in lod["selections"].items():
            n = name.lower()
            if n.startswith("proxy:") or n.startswith("-"):
                self.proxy.update(i for i, b in enumerate(blob) if b)
                continue
            if n in BONES or n.startswith("lefthand") or n.startswith("righthand"):
                for i, b in enumerate(blob):
                    if b:
                        self.W[i][n] = weight_of_byte(b)
        self.face_ids = [k for k, f in enumerate(lod["faces"])
                         if not any(i in self.proxy for i in f) and len(set(f)) >= 3]
        self.faces = [lod["faces"][k] for k in self.face_ids]
        self.idx = sorted({i for f in self.faces for i in f})
        self.ground = min(self.pts[i].z for i in self.idx)
        self.edges = sorted({(min(a, b), max(a, b)) for f in self.faces for a, b in zip(f, f[1:] + f[:1]) if a != b})
        # body surface with the native winding (normals outward, see p3d_mlod.py)
        bm = bmesh.new()
        bv = [bm.verts.new(p) for p in self.pts]
        for f in self.faces:
            try:
                bm.faces.new([bv[i] for i in f])
            except ValueError:
                pass
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.normal_update()
        self.bm = bm
        self.bvh = BVHTree.FromBMesh(bm)
        c, n, _, _ = self.bvh.find_nearest(Vector((0, -0.6, self.Z(1.30))))
        self.sign = 1.0 if (Vector((0, -0.6, self.Z(1.30))) - c).dot(n) > 0 else -1.0
        self.hand = {1: {b for w in self.W for b in w if b.startswith("lefthand")},
                     -1: {b for w in self.W for b in w if b.startswith("righthand")}}

    def Z(self, h):
        return self.ground + h

    def H(self, z):
        return z - self.ground

    def group_idx(self, group, thr=0.5, side=0):
        return {i for i in self.idx
                if sum(w for b, w in self.W[i].items() if b in group) >= thr and (side == 0 or self.pts[i].x * side > 0)}

    def joint(self, A, B, thr=0.15):
        P = [self.pts[i] for i in self.idx
             if sum(self.W[i].get(b, 0) for b in A) >= thr and sum(self.W[i].get(b, 0) for b in B) >= thr]
        if len(P) < 3:
            raise RuntimeError(f"joint {A}/{B}: not enough shared vertices")
        return sum(P, Vector()) / len(P)

    def joints(self):
        J = {}
        for s, p in ((1, "left"), (-1, "right")):
            J[("shoulder", s)] = self.joint({f"{p}shoulder"}, {f"{p}arm"})
            J[("elbow", s)] = self.joint({f"{p}armroll"}, {f"{p}forearm"})
            J[("wrist", s)] = self.joint({f"{p}forearmroll"}, {f"{p}hand"})
            J[("hip", s)] = self.joint({"pelvis"}, {f"{p}upleg"})
            J[("knee", s)] = self.joint({f"{p}uplegroll"}, {f"{p}leg"})
            J[("ankle", s)] = self.joint({f"{p}legroll"}, {f"{p}foot"})
        return J

    def section(self, idx, origin, axis, rmax=None, xside=0, xlim=None, xmargin=0.002):
        """Exact cross-section: intersections of the body edges touching the vertex set idx with the plane."""
        out = []
        for a, b in self.edges:
            if a not in idx and b not in idx:
                continue
            pa, pb = self.pts[a], self.pts[b]
            ta, tb = (pa - origin).dot(axis), (pb - origin).dot(axis)
            if ta * tb > 0 or ta == tb:
                continue
            p = pa + (pb - pa) * (ta / (ta - tb))
            w = p - origin
            if rmax is not None and (w - axis * w.dot(axis)).length > rmax:
                continue
            if xside and p.x * xside <= xmargin:
                continue
            if xlim is not None and abs(p.x) > xlim:
                continue
            out.append(p)
        return out

    def top(self, x, y):
        hit = self.bvh.ray_cast(Vector((x, y, self.Z(2.2))), Vector((0, 0, -1)))
        return hit[0].z if hit[0] is not None else None

    def signed_distance(self, p):
        c, n, _, d = self.bvh.find_nearest(p)
        if c is None:
            return 1.0
        return d if (p - c).dot(n) * self.sign >= 0 else -d


# ---------------------------------------------------------------- section profiles
def _ray_hull(c, th, poly):
    d = Vector((math.cos(th), math.sin(th)))
    best = 0.0
    for a, b in zip(poly, poly[1:] + poly[:1]):
        e = b - a
        den = d.x * e.y - d.y * e.x
        if abs(den) < 1e-12:
            continue
        ac = a - c
        t = (ac.x * e.y - ac.y * e.x) / den
        s = (ac.x * d.y - ac.y * d.x) / den
        if t > 0 and -1e-9 <= s <= 1 + 1e-9:
            best = max(best, t)
    return best


def profile(points, origin, axis, fwd=FRONT):
    """Convex-hull profile of section points in the frame (u = fwd projected, v = axis x u)."""
    axis = axis.normalized()
    u = (fwd - axis * fwd.dot(axis)).normalized()
    v = axis.cross(u)
    fr = dict(o=origin.copy(), a=axis, u=u, v=v, c=None, r=None)
    P2 = [Vector(((p - origin).dot(u), (p - origin).dot(v))) for p in points]
    if len(P2) < 5:
        return fr
    poly = [P2[i] for i in convex_hull_2d(P2)]
    m = sum(poly, Vector((0, 0))) / len(poly)
    poly.sort(key=lambda p: math.atan2(p.y - m.y, p.x - m.x))
    A, cx, cy = 0.0, 0.0, 0.0
    for p, q in zip(poly, poly[1:] + poly[:1]):
        cr = p.x * q.y - q.x * p.y
        A += cr; cx += (p.x + q.x) * cr; cy += (p.y + q.y) * cr
    c = Vector((cx / (3 * A), cy / (3 * A))) if abs(A) > 1e-10 else m
    fr["c"] = c
    fr["r"] = [_ray_hull(c, 2 * math.pi * k / NS, poly) for k in range(NS)]
    return fr


def fill_and_smooth(frames, passes=2):
    valid = [k for k, f in enumerate(frames) if f["c"] is not None]
    if not valid:
        raise RuntimeError("no valid section in this run of frames")
    for k, f in enumerate(frames):
        if f["c"] is None:
            j = min(valid, key=lambda q: abs(q - k))
            f["c"], f["r"] = frames[j]["c"].copy(), list(frames[j]["r"])
    for _ in range(passes):
        cs = [f["c"].copy() for f in frames]
        rs = [list(f["r"]) for f in frames]
        for k in range(1, len(frames) - 1):
            frames[k]["c"] = cs[k - 1] * 0.25 + cs[k] * 0.5 + cs[k + 1] * 0.25
            frames[k]["r"] = [rs[k - 1][a] * 0.25 + rs[k][a] * 0.5 + rs[k + 1][a] * 0.25 for a in range(NS)]
    return frames


def radius(fr, th):
    x = (th % (2 * math.pi)) / (2 * math.pi) * NS
    a = int(x) % NS
    t = x - int(x)
    return fr["r"][a] * (1 - t) + fr["r"][(a + 1) % NS] * t


def fpoint(fr, th, ease):
    r = radius(fr, th) + ease
    c = fr["c"]
    return fr["o"] + fr["u"] * (c.x + r * math.cos(th)) + fr["v"] * (c.y + r * math.sin(th))


def theta_of(fr, direction):
    return math.atan2(direction.dot(fr["v"]), direction.dot(fr["u"]))


def frame_centre(fr):
    return fr["o"] + fr["u"] * fr["c"].x + fr["v"] * fr["c"].y


def lerp_frame(f0, f1, t, origin=None):
    """Blend two frames that share u/v orientation (for extra rings between stations)."""
    return dict(o=origin if origin is not None else f0["o"].lerp(f1["o"], t), a=f0["a"].lerp(f1["a"], t).normalized(),
                u=f0["u"].lerp(f1["u"], t).normalized(), v=f0["v"].lerp(f1["v"], t).normalized(),
                c=f0["c"].lerp(f1["c"], t), r=[a * (1 - t) + b * t for a, b in zip(f0["r"], f1["r"])])


def vertical_frames(body, idx, heights, xlim=None, xside=0, passes=2, xmargin=0.002):
    frames = []
    for h in heights:
        o = Vector((0, 0, body.Z(h)))
        frames.append(profile(body.section(idx, o, UP, xside=xside, xlim=xlim, xmargin=xmargin), o, UP))
    return fill_and_smooth(frames, passes)


def polyline_at(P, s, blend=0.04):
    L = [(b - a).length for a, b in zip(P, P[1:])]
    acc = 0.0
    for k, l in enumerate(L):
        if s <= acc + l or k == len(L) - 1:
            t = (s - acc) / l
            d = (P[k + 1] - P[k]).normalized()
            pos = P[k] + (P[k + 1] - P[k]) * t
            if k + 1 < len(L) and (acc + l - s) < blend:
                dn = (P[k + 2] - P[k + 1]).normalized()
                a = 0.5 * (1 - (acc + l - s) / blend)
                d = (d * (1 - a) + dn * a).normalized()
            if k > 0 and (s - acc) < blend:
                dp = (P[k] - P[k - 1]).normalized()
                a = 0.5 * (1 - (s - acc) / blend)
                d = (d * (1 - a) + dp * a).normalized()
            return pos, d
        acc += l
    return P[-1], (P[-1] - P[-2]).normalized()


def polyline_length(P):
    return sum((b - a).length for a, b in zip(P, P[1:]))


def axis_frames(body, idx, P, s_list, rmax, fwd=FRONT, passes=2):
    frames = []
    for s in s_list:
        o, d = polyline_at(P, s)
        frames.append(profile(body.section(idx, o, d, rmax=rmax), o, d, fwd))
    return fill_and_smooth(frames, passes)


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def gauss(x, mu, sigma):
    return math.exp(-((x - mu) / sigma) ** 2)


def angdiff(a, b):
    return (a - b + math.pi) % (2 * math.pi) - math.pi


# ---------------------------------------------------------------- mesh helpers
def loft(bm, rings, closed=True, mat_of=None, orient_centres=None, orient_band=0):
    """Quads between consecutive rings. mat_of(band, column) -> material index. Faces are oriented so that the
    band orient_band faces away from its centre (orient_centres[k] = centre of ring k)."""
    V = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    faces = []
    for k in range(len(rings) - 1):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            f = bm.faces.new((V[k][i], V[k][j], V[k + 1][j], V[k + 1][i]))
            if mat_of:
                f.material_index = mat_of(k, i)
            faces.append((f, k))
    if orient_centres:
        k0 = orient_band
        c = (orient_centres[k0] + orient_centres[k0 + 1]) / 2
        score = 0.0
        for f, k in faces:
            if k == k0:
                f.normal_update()
                score += f.normal.dot(f.calc_center_median() - c)
        if score < 0:
            bmesh.ops.reverse_faces(bm, faces=[f for f, _ in faces])
    return V


def grid(bm, rows, mat=0, flip=False):
    """Open quad grid from rows of points (same length)."""
    V = [[bm.verts.new(p) for p in r] for r in rows]
    out = []
    for k in range(len(rows) - 1):
        for i in range(len(rows[0]) - 1):
            q = (V[k][i], V[k][i + 1], V[k + 1][i + 1], V[k + 1][i])
            f = bm.faces.new(q[::-1] if flip else q)
            f.material_index = mat
            out.append(f)
    return V, out


def dome(bm, centre, normal, r, h, seg=8, mat=0):
    """Domed button: base ring, one shoulder ring and an apex fan (open base, sits on the cloth)."""
    n = normal.normalized()
    t = n.orthogonal().normalized()
    b = n.cross(t)
    rings = []
    for rf, hf in ((1.0, 0.0), (0.66, 0.78)):
        rings.append([centre + (t * math.cos(2 * math.pi * i / seg) + b * math.sin(2 * math.pi * i / seg)) * r * rf
                      + n * h * hf for i in range(seg)])
    V = [[bm.verts.new(p) for p in ring] for ring in rings]
    apex = bm.verts.new(centre + n * h)
    fs = []
    for i in range(seg):
        j = (i + 1) % seg
        fs.append(bm.faces.new((V[0][i], V[0][j], V[1][j], V[1][i])))
    for i in range(seg):
        fs.append(bm.faces.new((V[1][i], V[1][(i + 1) % seg], apex)))
    for f in fs:
        f.material_index = mat
        f.normal_update()
    if fs[0].normal.dot(fs[0].calc_center_median() - centre) < 0:
        bmesh.ops.reverse_faces(bm, faces=fs)
    return fs
