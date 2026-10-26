# Blockout of the crested leather helmet ("Raupenhelm") of the Wuerttemberg and Bavarian line and light infantry, c. 1811
# (spec docs/specs/aliados_fr_1812.md sections 2.0-2.2). Helpers copied from blockout_czapka_varsovia.py (fit on the
# official Samples head band, peak, chinscales, traced plates with UV "arte", art discs) and the fur locks from
# blockout_bonnet_italia.py; the skull and the crest are new.
# Sources (all 🔶: no surviving helmet measured):
#   - Vinkhuijzen collection (NYPL) watercolours "Wuerttemberg 1811" and "Baiern 1811" [VK-REN]: black leather skull, peak
#     edged with brass, large black fur crest from the forehead over the top to the nape (the Bavarian one rolls forward over
#     the front), brass chinscales; Wuerttemberg: wide brass front plate under a crown; Bavaria: crowned oval plate with the
#     monogram, brass front band;
#   - mod art (Reto pack, authorised; 🎮): WurtembergINF_2 c5 r4 (front plate, traced with mascara_latao.py +
#     trace_badge.py -> placa_wurttemberg.json), c6 r4 (cockade, red in a yellow ring); BavariaINF c0 r0 (crowned oval,
#     outline drawn by hand -> placa_baviera.json; cockade white and blue lozenges);
#   - [WP-BAV]: the Raupenhelm with a crest of horsehair/fur "from front to back" for all arms since 1801.
#   Sizes: skull 3 cm clear of the head top; crest up to 11 cm above the skull, 8 cm wide (read off the watercolours
#   against the face).
#   blender -b --factory-startup --python blockout_raupenhelm.py -- <Test_Character_01 dir> <out.blend> <render dir>
#           dir=<folder of placa_wurttemberg.json / placa_baviera.json> atlas_wue=<png> atlas_bav=<png>
# Root empties RH_<tag>: texturizar_aliados.py raiz=RH_ nome=HCL_Raupenhelm_ textura=hcl_raupenhelm_ so=<tag> atlas=<png>
import bpy, bmesh, sys, os, math, json, random
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import shako_fit

args = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, OUT_BLEND, RENDER_DIR = args[:3]
OUT_BLEND, RENDER_DIR = os.path.abspath(OUT_BLEND), os.path.abspath(RENDER_DIR)
OPT = dict(x.split("=", 1) for x in args[3:] if "=" in x)
PL_DIR = os.path.abspath(OPT.get("dir", "."))
os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- fit and proportions
WALL, CLEAR, TILT, DEPTH_RATIO = shako_fit.WALL, shako_fit.CLEAR, shako_fit.TILT, shako_fit.DEPTH_RATIO
F = shako_fit.compute(SAMPLES)
base_hw = F["head_hw"] + WALL + CLEAR
base_hd = max(base_hw * DEPTH_RATIO, F["head_hd"] + WALL + CLEAR)
Z_ROOT = F["z_forehead"] - 0.004
ROOT = Matrix.Translation(Vector((0.0, F["head_cy"], Z_ROOT))) @ Matrix.Rotation(-TILT, 4, 'X')
H = max(0.145, F["z_head_top"] - Z_ROOT + 0.030)      # skull height over the band (3 cm clear of the head top)
ZD = 0.045                                            # straight side up to here, then the dome
VISOR_LEN, VISOR_DROP = 0.050, math.radians(36)
NECK_LEN, NECK_DROP = 0.034, math.radians(20)
N = 64
print(f"FIT casco H={H:.3f} base={2 * base_hw:.3f}x{2 * base_hd:.3f}")

COL = dict(couro=(0.025, 0.022, 0.020), latao=(0.70, 0.50, 0.16), pelo=(0.010, 0.009, 0.008),
           couro_marrom=(0.05, 0.028, 0.014), forro=(0.33, 0.29, 0.22), branco=(0.82, 0.82, 0.80),
           vermelho=(0.55, 0.03, 0.03), amarelo=(0.80, 0.62, 0.06), azul_claro=(0.36, 0.56, 0.84))
MATS, PARTS = {}, []


def mat(name):
    if name not in MATS:
        m = bpy.data.materials.new("BO_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*COL[name], 1)
        b.inputs["Roughness"].default_value = 0.35 if name == "latao" else 0.7
        b.inputs["Metallic"].default_value = 1.0 if name == "latao" else 0.0
        MATS[name] = m
    return MATS[name]


def finish(bm, name, colour, parent, keep_normals=False, smooth=True):
    if not keep_normals:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(mat(colour))
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); ob.parent = parent
    scene.collection.objects.link(ob); PARTS.append(ob)
    return ob


def grid(bm, rows, closed_u=True):
    nc = len(rows[0])
    for j in range(len(rows) - 1):
        for i in range(nc - (0 if closed_u else 1)):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % nc], rows[j + 1][(i + 1) % nc], rows[j + 1][i]))


def cap_ring(bm, ring, centre):
    c = bm.verts.new(centre)
    for i in range(len(ring)):
        bm.faces.new((c, ring[i], ring[(i + 1) % len(ring)]))


# ---------------------------------------------------------------- skull surface
def prof(z):
    """Radius factor of the skull at height z (1 on the straight side, a quarter ellipse on the dome)."""
    if z <= ZD:
        return 1.0
    return math.sqrt(max(0.0, 1.0 - ((z - ZD) / (H - ZD)) ** 2))


def R(theta, z):
    a, b = base_hw * prof(z), base_hd * prof(z)
    if a < 1e-6:
        return 0.0
    return 1.0 / math.sqrt((math.sin(theta) / a) ** 2 + (math.cos(theta) / b) ** 2)


def ry(z): return max(1e-4, R(0.0, z))


def P(theta, z, off=0.0):
    """Skull-local point; theta = 0 is the FRONT (-Y), +90 deg the wearer's left (+X); off along the outward normal."""
    r = R(theta, z)
    p = Vector((r * math.sin(theta), -r * math.cos(theta), z))
    return p + wall_n(theta, z) * off if off else p


def wall_n(theta, z):
    e = 1e-4
    z = min(z, H - 2e-4)
    dt = Vector((R(theta + e, z) * math.sin(theta + e), -R(theta + e, z) * math.cos(theta + e), z)) - \
        Vector((R(theta - e, z) * math.sin(theta - e), -R(theta - e, z) * math.cos(theta - e), z))
    z0, z1 = max(0.0, z - e), z + e
    dz = Vector((R(theta, z1) * math.sin(theta), -R(theta, z1) * math.cos(theta), z1)) - \
        Vector((R(theta, z0) * math.sin(theta), -R(theta, z0) * math.cos(theta), z0))
    n = dt.cross(dz)
    if n.length < 1e-12:
        return Vector((0, 0, 1))
    n.normalize()
    out = Vector((math.sin(theta), -math.cos(theta), 0.4 * max(0.0, z - ZD) / (H - ZD)))
    return n if n.dot(out) > 0 else -n


def T(u):
    """Rows of the skull mesh: u = 0 band ... 1 top pole; even spacing along the profile."""
    side = ZD / (ZD + (H - ZD) * 1.2)
    if u <= side:
        return ZD * u / side
    a = (u - side) / (1 - side) * math.pi / 2
    return ZD + (H - ZD) * math.sin(a)


def project(p, off=0.0):
    """Radial projection of a point onto the skull (from a centre at mid dome height), plus off along the normal."""
    c = Vector((0.0, 0.0, ZD * 0.5))
    d = (p - c).normalized()
    lo, hi = 0.0, 0.5
    for _ in range(40):
        m = (lo + hi) / 2
        q = c + d * m
        th = math.atan2(q.x, -q.y)
        inside = q.z < H and (q.z < 0 or math.hypot(q.x, q.y) < R(th, max(0.0, q.z)))
        lo, hi = (m, hi) if inside else (lo, m)
    q = c + d * lo
    th = math.atan2(q.x, -q.y)
    return q + wall_n(th, max(0.0, q.z)) * off, wall_n(th, max(0.0, q.z))


# ---------------------------------------------------------------- generic pieces (as blockout_czapka_varsovia.py)
def sweep(name, path, half_w, half_t, colour, parent, normals=None, round_=False, segs=8):
    bm = bmesh.new()
    rows = []
    for k_, p in enumerate(path):
        tng = (path[min(k_ + 1, len(path) - 1)] - path[max(k_ - 1, 0)]).normalized()
        nrm = normals[k_] if normals else (tng.orthogonal()).normalized()
        nrm = (nrm - tng * nrm.dot(tng)).normalized()
        side = tng.cross(nrm).normalized()
        if round_:
            rows.append([bm.verts.new(p + half_w * (math.cos(2 * math.pi * s / segs) * nrm + math.sin(2 * math.pi * s / segs) * side)) for s in range(segs)])
        else:
            rows.append([bm.verts.new(p + side * sx * half_w + nrm * sz * half_t) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    grid(bm, rows)
    cap_ring(bm, rows[0], path[0]); cap_ring(bm, rows[-1], path[-1])
    return finish(bm, name, colour, parent)


def catmull(pts, n=10):
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for s in range(n):
            t = s / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return out


def lathe_obj(name, profile, centre, colour, parent, axis=Vector((0, 0, 1)), segs=20):
    bm = bmesh.new()
    u = axis.orthogonal().normalized(); v = axis.cross(u).normalized()
    rows = [[bm.verts.new(centre + axis * a + r * (math.cos(2 * math.pi * s / segs) * u + math.sin(2 * math.pi * s / segs) * v)) for s in range(segs)] for a, r in profile]
    grid(bm, rows)
    cap_ring(bm, rows[0], centre + axis * profile[0][0]); cap_ring(bm, rows[-1], centre + axis * profile[-1][0])
    return finish(bm, name, colour, parent)


def disc(name, centre, normal, r, t, colour, parent, segs=24):
    return lathe_obj(name, [(0, 0.0005), (0, r), (t, r), (t, 0.0005)], centre, colour, parent, axis=normal, segs=segs)


ATLAS_PX = 4096


def art_uv(px, py):
    return (px / ATLAS_PX, 1.0 - py / ATLAS_PX)


def art_disc(name, centre, normal, r, t, box, colour, parent, segs=24):
    """Disc whose faces carry the mod art of `box` (atlas pixels) in UV layer "arte"."""
    ob = disc(name, centre, normal, r, t, colour, parent, segs)
    me = ob.data
    uvl = me.uv_layers.new(name="arte")
    u_ = normal.orthogonal().normalized(); v_ = normal.cross(u_).normalized()
    bx0, by0, bx1, by1 = box
    for poly in me.polygons:
        for li in poly.loop_indices:
            d = me.vertices[me.loops[li].vertex_index].co - centre
            a, b = d.dot(u_) / r, d.dot(v_) / r
            uvl.data[li].uv = art_uv(bx0 + (bx1 - bx0) * (0.5 + 0.5 * a), by0 + (by1 - by0) * (0.5 - 0.5 * b))
    return ob


def traced_plate(name, json_path, z_bot, z_top, max_w, depth, colour, parent):
    """Brass plate from a traced outline (trace_badge.py JSON), scaled into z_bot..z_top and max_w, wrapped on the front
    of the skull; UV layer "arte" = the same point in the mod art (box offset + loop pixel)."""
    bj = json.load(open(json_path))
    X0, Y0 = bj["box"][:2]
    cu = bpy.data.curves.new(name + "_curva", "CURVE")
    cu.dimensions, cu.fill_mode = "2D", "BOTH"
    for loop in bj["loops"]:
        sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1)
        for p_, (x, y) in zip(sp.points, loop):
            p_.co = (x, -y, 0.0, 1.0)
        sp.use_cyclic_u = True
    xs = [x for l in bj["loops"] for x, _ in l]; ys = [y for l in bj["loops"] for _, y in l]
    kf = min(max_w / (max(xs) - min(xs)), (z_top - z_bot) / (max(ys) - min(ys)))
    cu.extrude = depth / 2 / kf
    tob = bpy.data.objects.new(name + "_curva", cu); scene.collection.objects.link(tob)
    bpy.context.view_layer.update()
    me0 = bpy.data.meshes.new_from_object(tob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tob); bpy.data.curves.remove(cu)
    ub = bmesh.new(); ub.from_mesh(me0); bpy.data.meshes.remove(me0)
    bmesh.ops.remove_doubles(ub, verts=ub.verts[:], dist=1e-4)
    bmesh.ops.triangulate(ub, faces=ub.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    for _ in range(8):                                   # long fill triangles would cut the curved skull
        long_e = [e for e in ub.edges if e.calc_length() * kf > 0.013]
        if not long_e:
            break
        bmesh.ops.subdivide_edges(ub, edges=long_e, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(ub, faces=[f for f in ub.faces if len(f.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
    cx = (max(xs) + min(xs)) / 2
    ymid = (max(ys) + min(ys)) / 2
    zmin = min(v.co.z for v in ub.verts)
    zc_ = (z_bot + z_top) / 2
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("arte")
    vm = {}
    for v in ub.verts:
        lx, ly, lz = (v.co.x - cx) * kf, (v.co.y + ymid) * kf, (v.co.z - zmin) * kf
        z = zc_ + ly
        vm[v.index] = (bm.verts.new(P(lx / ry(z), z, 0.0008 + lz)), art_uv(X0 + v.co.x, Y0 - v.co.y))
    ub.verts.index_update()
    for f in ub.faces:
        try:
            nf = bm.faces.new([vm[v.index][0] for v in f.verts])
        except ValueError:
            continue
        for l, v in zip(nf.loops, f.verts):
            l[uvl].uv = vm[v.index][1]
    ub.free()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = finish(bm, name, colour, parent, keep_normals=True)
    print(f"PLACA {name}: {os.path.basename(json_path)} {(max(xs) - min(xs)) * kf * 1000:.0f} x {(max(ys) - min(ys)) * kf * 1000:.0f} mm, {len(ob.data.polygons)} faces")
    return ob


def pleated(name, centre, normal, r_in, r_out, t, n, colour, parent):
    """Pleated ring of the cockade (as blockout_czapka_varsovia.py)."""
    bm = bmesh.new()
    u = normal.orthogonal().normalized(); v = normal.cross(u).normalized()
    M = 2 * n
    rows = []
    for rr, k in ((r_in, 0.4), ((r_in + r_out) / 2, 1.0), (r_out, 0.7)):
        rows.append([bm.verts.new(centre + normal * (t * k * (1.0 if i % 2 == 0 else 0.15)) + rr * (math.cos(2 * math.pi * i / M) * u + math.sin(2 * math.pi * i / M) * v)) for i in range(M)])
    base_out = [bm.verts.new(centre + r_out * (math.cos(2 * math.pi * i / M) * u + math.sin(2 * math.pi * i / M) * v)) for i in range(M)]
    grid(bm, rows + [base_out])
    return finish(bm, name, colour, parent)


def chinscales(name, path, normals, colour, parent, n_scales=11):
    sweep(name + "_couro", path, 0.0110, 0.0007, "couro", parent, normals=normals)
    L = [0.0]
    for a_, b_ in zip(path, path[1:]):
        L.append(L[-1] + (b_ - a_).length)
    total = L[-1]

    def at(d):
        for k_ in range(len(L) - 1):
            if L[k_ + 1] >= d:
                t_ = (d - L[k_]) / max(1e-9, L[k_ + 1] - L[k_])
                return path[k_].lerp(path[k_ + 1], t_), normals[k_].lerp(normals[k_ + 1], t_).normalized(), (path[k_ + 1] - path[k_]).normalized()
        return path[-1], normals[-1], (path[-1] - path[-2]).normalized()

    bm = bmesh.new()
    step = (total - 0.012) / (n_scales - 1)
    for k_ in range(n_scales):
        p, n, tg = at(0.004 + k_ * step)
        n = (n - tg * n.dot(tg)).normalized()
        side = tg.cross(n).normalized()
        w = 0.0160 - 0.0060 * k_ / (n_scales - 1)
        ln = step * 1.65
        lift = 0.0010 + 0.00035 * (n_scales - 1 - k_)
        outline = [(-w, 0.0), (0.0, 0.0), (w, 0.0), (w, ln * 0.5)] + [(w * math.cos(math.pi * i / 10), ln * 0.5 + ln * 0.5 * math.sin(math.pi * i / 10)) for i in range(1, 10)] + [(-w, ln * 0.5)]
        top, bot = [], []
        for sx, sl in outline:
            q = p + side * sx + tg * sl + n * (lift + 0.0013 * (1 - (sx / w) ** 2))
            top.append(bm.verts.new(q)); bot.append(bm.verts.new(q - n * 0.0006))
        m_ = len(outline)
        ct = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0009)); cb = bm.verts.new(p + tg * ln * 0.45 + n * (lift + 0.0003))
        for i in range(m_):
            j = (i + 1) % m_
            bm.faces.new((ct, top[i], top[j])); bm.faces.new((cb, bot[j], bot[i]))
            bm.faces.new((top[j], top[i], bot[i], bot[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return finish(bm, name, colour, parent, keep_normals=True)


# ---------------------------------------------------------------- the crest
def meridian(n=60, front_z=None, back_z=None):
    """Points of the skull's middle line from the front (theta 0, z = front_z) over the top to the back (theta pi)."""
    pts = [P(0.0, front_z + (H - 1e-4 - front_z) * (i / n) ** 0.8) for i in range(n)]
    pts += [P(math.pi, H - 1e-4 - (H - 1e-4 - back_z) * (i / n) ** 1.25) for i in range(n + 1)]
    out = [pts[0]]
    for p in pts[1:]:
        if (p - out[-1]).length > 1e-4:
            out.append(p)
    return out


class Crest:
    """Fur crest: a tube along the meridian, elliptic section (half width w(u) across, half height h(u) along the skull
    normal); the Bavarian one rolls forward over the front (curl)."""

    def __init__(self, front_z, back_z, h_max, w_max, curl, peak_u):
        m = meridian(front_z=front_z, back_z=back_z)
        L = [0.0]
        for a, b in zip(m, m[1:]):
            L.append(L[-1] + (b - a).length)
        self.m, self.L, self.total = m, L, L[-1]
        self.h_max, self.w_max, self.curl, self.peak_u = h_max, w_max, curl, peak_u

    def base(self, u):
        d = u * self.total
        for k in range(len(self.L) - 1):
            if self.L[k + 1] >= d:
                t = (d - self.L[k]) / max(1e-9, self.L[k + 1] - self.L[k])
                p = self.m[k].lerp(self.m[k + 1], t)
                tg = (self.m[k + 1] - self.m[k]).normalized()
                break
        else:
            p, tg = self.m[-1], (self.m[-1] - self.m[-2]).normalized()
        x = Vector((1, 0, 0))
        n = x.cross(tg).normalized()
        if n.dot(p - Vector((0, 0, ZD * 0.5))) < 0:
            n = -n
        return p, tg, n

    def size(self, u):
        # rises fast at the front, fullest at peak_u, tapering to the nape
        a = u / self.peak_u if u < self.peak_u else 1 - (u - self.peak_u) / (1 - self.peak_u)
        f = math.sin(math.pi / 2 * max(0.0, min(1.0, a))) ** (0.55 if u < self.peak_u else 0.9)
        ends = math.sin(math.pi / 2 * min(1.0, u / 0.08)) ** 0.5 * math.sin(math.pi / 2 * min(1.0, (1 - u) / 0.06)) ** 0.5
        return (0.18 + 0.82 * f) * ends                            # rounded nose and tail (v2)

    def point(self, u, v, off=0.0):
        """v = 0 on top of the crest, +-pi/2 its sides, pi its seat (inside the skull)."""
        p, tg, n = self.base(u)
        s = self.size(u)
        h, w = self.h_max * s, self.w_max * (0.35 + 0.65 * s)
        c = p + n * (h * 0.78)
        if u < 0.3 and self.curl:                                  # roll forward over the front
            c += Vector((0, -1, -0.35)).normalized() * self.curl * (1 - u / 0.3) ** 2
        x = Vector((1, 0, 0))
        q = c + n * (h * math.cos(v)) + x * (w * math.sin(v))
        nn = (n * (math.cos(v) / max(h, 1e-4)) + x * (math.sin(v) / max(w, 1e-4))).normalized()
        return q + nn * off, nn, tg


def crest_shell(tag, cr, root):
    bm = bmesh.new()
    NU, NV = 48, 32
    rows = [[bm.verts.new(cr.point(0.004 + 0.992 * j / (NU - 1), 2 * math.pi * i / NV)[0]) for i in range(NV)] for j in range(NU)]
    grid(bm, rows)
    cap_ring(bm, rows[0][::-1], sum((v.co for v in rows[0]), Vector()) / NV)
    cap_ring(bm, rows[-1], sum((v.co for v in rows[-1]), Vector()) / NV)
    finish(bm, f"{tag}_pele_corpo", "pelo", root)


def crest_hair(tag, cr, seed):
    """Locks over the crest (as the bearskin's, blockout_bonnet_italia.hair): the fur is brushed up and BACK, the locks
    leave the shell raised and lie back on it; none on the seat. Two layers: short under-fur, long top locks."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    tint = bm.faces.layers.float.new("tint")
    count = {"base": 0, "longa": 0}

    def lock(u, v, L, W, lift, short):
        p0, n, tg = cr.point(u, v)
        # Bavaria (curl): combed away from the fullest point, forward on the nose (it rolls over the front) and back
        # toward the nape; Wuerttemberg: all back, so the front plate stays clear (watercolour 020)
        fw = cr.curl > 0 and u < cr.peak_u
        back = (-tg if fw else tg) - n * n.dot(-tg if fw else tg)
        if back.length < 1e-6:
            back = n.orthogonal()
        back.normalize()
        up = Vector((0, 0, 1)) - n * n.z
        up = up.normalized() if up.length > 1e-6 else back
        ang = rnd.uniform(-0.35, 0.35)
        d = (back * 0.85 + up * 0.25 * math.cos(v)).normalized()
        d = (d * math.cos(ang) + n.cross(d) * math.sin(ang)).normalized()
        sd = n.cross(d).normalized()
        st = ((0.0, 0.95), (1.0, 0.2)) if short else ((0.0, 0.8), (0.34, 1.0), (0.68, 0.78), (1.0, 0.10))
        sh = rnd.uniform(0.0, 1.0)
        rows = []
        for t, wf in st:
            rise = lift * (4.0 * t * (1.0 - t) + 0.22 * t) - lift * 0.9 * t * t
            p = p0 + n * (0.0015 + rise) + d * (L * t)
            hw = W * wf / 2
            cup = n * (0.35 * hw)
            rows.append((bm.verts.new(p - sd * hw - cup), bm.verts.new(p + n * 0.0012), bm.verts.new(p + sd * hw - cup), t))
        for k in range(len(rows) - 1):
            (a0, m0, b0, t0), (a1, m1, b1, t1) = rows[k], rows[k + 1]
            for (x0, x1, y1, y0, u0, u1) in ((a0, m0, m1, a1, 0.0, 0.5), (m0, b0, b1, m1, 0.5, 1.0)):
                f = bm.faces.new((x0, x1, y1, y0))
                for l, uv in zip(f.loops, ((u0, t0), (u1, t0), (u1, t1), (u0, t1))):
                    l[uvl].uv = uv
                f[tint] = sh; f.smooth = True
                f.normal_update()
                if f.normal.dot(n) < 0:
                    f.normal_flip()

    for layer, nu, nv in (("base", 44, 20), ("longa", 40, 18)):
        for j in range(nu):
            for i in range(nv):
                u = (j + rnd.uniform(0.05, 0.95)) / nu
                v = (i + rnd.uniform(0.0, 1.0) + 0.5 * (j % 2)) / nv * 4.0 - 2.0     # -2..2 rad: not on the seat
                if u > 0.985:
                    continue
                if layer == "base":
                    lock(u, v, rnd.uniform(0.018, 0.028), rnd.uniform(0.008, 0.012), rnd.uniform(0.0008, 0.003), True)
                else:
                    lock(u, v, rnd.uniform(0.040, 0.065), rnd.uniform(0.011, 0.016), rnd.uniform(0.004, 0.010), False)
                count[layer] += 1
    finish(bm, f"{tag}_pelo", "pelo", None, keep_normals=True)
    return count


# ---------------------------------------------------------------- one helmet
def helmet(tag, x_off, plate_json, plate_w, plate_h, plate_z0, cock_art, cock_box, crest_kw, front_band):
    root = bpy.data.objects.new(f"RH_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ ROOT
    scene.collection.objects.link(root)
    # skull: black leather, wall with thickness, closed at the top pole
    bm = bmesh.new()
    NR = 24
    outer = [[bm.verts.new(P(2 * math.pi * i / N, T(j / NR))) for i in range(N)] for j in range(NR)]
    inner = [[bm.verts.new(P(2 * math.pi * i / N, T(j / NR) * 0.985, -WALL)) for i in range(N)] for j in range(NR - 2)]
    grid(bm, outer); grid(bm, [inner[0], outer[0]]); grid(bm, inner[::-1])
    cap_ring(bm, outer[-1], Vector((0, 0, H)))
    cap_ring(bm, inner[-1][::-1], Vector((0, 0, T((NR - 3) / NR) * 0.985 + 0.004)))
    finish(bm, f"{tag}_topo", "couro", root)                 # "topo": leather kind in the texturizer
    # sweatband and lining
    bm = bmesh.new()
    rows_s = [[bm.verts.new(P(2 * math.pi * i / N, z, -WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.018, 0.036)]
    grid(bm, rows_s[::-1])
    finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    # front peak, edged with brass
    bm = bmesh.new()
    arc = [math.radians(-78 + 156 * i / 48) for i in range(49)]

    def prow(centre, half, length, drop, z0, dz):
        out = []
        for a in arc:
            th = centre + a * half / math.radians(78)
            n = wall_n(th, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a) / math.radians(78)) ** 4
            out.append(P(th, z0, 0.002) + n * length * w * math.cos(drop) + Vector((0, 0, -length * w * math.sin(drop) + dz)))
        return out
    for nm, centre, half, length, drop, colour in (("pala", 0.0, math.radians(78), VISOR_LEN, VISOR_DROP, "couro"),
                                                    ("pala_couro_nuca", math.pi, math.radians(70), NECK_LEN, NECK_DROP, "couro")):
        bm = bmesh.new()
        rows = [[bm.verts.new(p) for p in prow(centre, half, l_, drop, 0.004, dz)] for l_, dz in ((0.0, 0.0), (length, 0.0), (length, -0.003), (0.0, -0.003))]
        grid(bm, rows, closed_u=False)
        for r in (0, 48):
            bm.faces.new((rows[0][r], rows[1][r], rows[2][r], rows[3][r]))
        for i in range(48):
            bm.faces.new((rows[3][i], rows[3][i + 1], rows[0][i + 1], rows[0][i]))
        edge = [(rows[1][i].co + rows[2][i].co) / 2 for i in range(len(arc))]
        finish(bm, f"{tag}_{nm}", colour, root)
        # "debrum_<peak>": a name that does not start with "pala_couro" (texturizer kind = brass, not leather)
        sweep(f"{tag}_debrum_{nm}", edge, 0.0019, 0, "latao", root, round_=True, segs=6)
    # brass band round the lower edge of the skull (both watercolour series show a brass rim above the peaks)
    bm = bmesh.new()
    rows = [[bm.verts.new(P(2 * math.pi * i / N, z, o)) for i in range(N)] for z, o in ((0.0, 0.0005), (0.0, 0.0016), (0.010, 0.0016), (0.010, 0.0005))]
    grid(bm, rows)
    finish(bm, f"{tag}_aro", "latao", root)
    if front_band:                                            # Bavaria: wider brass front band over the peak (art c0 r0)
        bm = bmesh.new()
        ths = [math.radians(-62 + 124 * i / 40) for i in range(41)]
        rows = [[bm.verts.new(P(t, z, o)) for t in ths] for z, o in ((0.009, 0.0016), (0.009, 0.0026), (0.026, 0.0026), (0.026, 0.0016))]
        grid(bm, rows, closed_u=False)
        finish(bm, f"{tag}_frente_latao", "latao", root)
    # front plate (traced from the mod art)
    traced_plate(f"{tag}_placa", plate_json, plate_z0, plate_z0 + plate_h, plate_w, 0.0018, "latao", root)
    # crest: fur shell + locks, on a brass comb (two strips along its seat)
    cr = Crest(**crest_kw)
    crest_shell(tag, cr, root)
    for sgn in (1, -1):
        path, nrm = [], []
        for k in range(41):
            u = 0.03 + 0.94 * k / 40
            q, n_, _ = cr.point(u, sgn * math.radians(150), 0.0)
            pp, nn = project(q, 0.0012)
            path.append(pp); nrm.append(nn)
        sweep(f"{tag}_pente_{'E' if sgn > 0 else 'D'}", path, 0.0055, 0.0007, "latao", root, normals=nrm)
    nl = crest_hair(tag, cr, sum(map(ord, tag)))
    PARTS[-1].parent = root
    # cockade on the wearer's left, above the chinscale boss: pleated rings in the colours of the mod art (🎮; the
    # watercolours are too small to show it): Wuerttemberg red in a yellow ring, Bavaria white and light blue
    zc, R_C = 0.062, 0.024
    c0 = P(math.radians(84), zc, 0.0016); nc = wall_n(math.radians(84), zc)
    c_out, c_mid, c_in = cock_box
    pleated(f"{tag}_cocar_fora", c0, nc, R_C * 0.55, R_C, 0.003, 36, c_out, root)
    pleated(f"{tag}_cocar_dentro", c0 + nc * 0.0012, nc, R_C * 0.22, R_C * 0.58, 0.003, 26, c_mid, root)
    disc(f"{tag}_cocar_centro", c0 + nc * 0.0034, nc, R_C * 0.24, 0.0015, c_in, root, segs=32)
    # chinscales on brass bosses
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, F["head_cy"] - F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        ro = P(sgn * math.radians(92), 0.022, 0.0035)
        nro = wall_n(sgn * math.radians(92), 0.022)
        disc(f"{tag}_botao_{'E' if sgn > 0 else 'D'}", ro, nro, 0.017, 0.0035, "latao", root, segs=40)
        ro_w = root.matrix_world @ ro
        z_mid = (ro_w.z + chin_w.z) / 2
        hz = (F["z_head_top"] - 0.57) / 2 - 0.004; zc_h = (F["z_head_top"] + 0.57) / 2
        half_w = (F["head_hw"] - 0.006) * math.sqrt(max(0.0, 1 - ((z_mid - zc_h) / hz) ** 2))
        mid = inv @ Vector((x_off + sgn * (half_w + 0.010), F["head_cy"] - 0.012, z_mid))
        path = catmull([ro, mid, Vector((sgn * 0.035, chin.y, chin.z + 0.006)), Vector((0.0, chin.y, chin.z))], 6)
        nrm = [Vector((p.x, p.y, 0)).normalized() for p in path]
        chinscales(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, nrm, "latao", root)
    print(f"CRISTA {tag}: {nl['base']} mechas curtas + {nl['longa']} longas")
    return root


WUE_BOX = ("amarelo", "vermelho", "vermelho")   # WurtembergINF_2 c6 r4 (3180..3240, 2360..2420): red in a yellow ring
BAV_BOX = ("branco", "azul_claro", "branco")    # BavariaINF c0 r0 (20..97, 195..272): white, light blue ring
VARIANTS = [
    ("wurttemberg", os.path.join(PL_DIR, "placa_wurttemberg.json"), 0.150, 0.075, 0.011, True, WUE_BOX,
     dict(front_z=0.088, back_z=0.040, h_max=0.062, w_max=0.046, curl=0.0, peak_u=0.33), False),
    ("baviera", os.path.join(PL_DIR, "placa_baviera.json"), 0.046, 0.080, 0.028, True, BAV_BOX,
     dict(front_z=0.108, back_z=0.040, h_max=0.070, w_max=0.048, curl=0.040, peak_u=0.26), True),
]
SPACING = 0.55
roots = [helmet(t, i * SPACING, *rest) for i, (t, *rest) in enumerate(VARIANTS)]

bpy.context.view_layer.update()
for (t, *_), r in zip(VARIANTS, roots):
    obs = [o for o in PARTS if o.parent is r]
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs)
    per = {o.name[len(t) + 1:]: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}
    big = ", ".join(f"{k} {v}" for k, v in sorted(per.items(), key=lambda kv: -kv[1])[:5])
    zmax = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
    print(f"VARIANTE {t:12s} pecas {len(obs):2d} triangulos {tris:6d} ({big}); topo {zmax:.3f} m (cabeca {F['z_head_top']:.3f})")

# ---------------------------------------------------------------- renders (approximate head)
hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
hme.materials.append(skin)
for p in hme.polygons:
    p.use_smooth = True
for i in range(len(VARIANTS)):
    h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    scene.collection.objects.link(h)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
for nm_, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
    lo = bpy.data.objects.new(nm_, bpy.data.lights.new(nm_, "SUN")); lo.data.energy = en
    lo.rotation_euler = tuple(math.radians(a) for a in rot); scene.collection.objects.link(lo)
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); scene.world = w
scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"; scene.cycles.samples = 32
scene.view_settings.view_transform = "Standard"
os.makedirs(RENDER_DIR, exist_ok=True)
zc = (ROOT @ Vector((0, 0, 0.08))).z


def shot(name, loc, target, ortho=None, lens=60, res=(1800, 900)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(RENDER_DIR, f"blockout_raupenhelm_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("render", scene.render.filepath)


mid_x = SPACING * (len(VARIANTS) - 1) / 2
shot("fila_tres_quartos", (mid_x + 1.0, -2.2, zc + 0.45), (mid_x, 0, zc), lens=45, res=(1800, 1000))
heads = [o for o in scene.objects if o.name.startswith("REF_cabeca_APROX_")]
for j, r in enumerate(roots):
    for o in [o for o in PARTS if o.parent is r] + [heads[j]]:
        o.hide_render = True
for j, (t, *_) in enumerate(VARIANTS):
    for o in [o for o in PARTS if o.parent is roots[j]] + [heads[j]]:
        o.hide_render = False
    x = j * SPACING
    shot(f"{t}_lado", (x - 1.6, F["head_cy"], zc), (x, F["head_cy"], zc), ortho=0.6, res=(900, 900))
    shot(f"{t}_frente", (x, -1.6, zc), (x, 0.0, zc), ortho=0.6, res=(900, 900))
    shot(f"{t}_perto", (x + 0.32, -0.55, zc + 0.10), (x, F["head_cy"] - 0.04, zc + 0.02), lens=55, res=(1000, 1000))
    for o in [o for o in PARTS if o.parent is roots[j]] + [heads[j]]:
        o.hide_render = True
for o in PARTS + heads:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
