# Fur locks v6 for every bearskin of the mod (user 2026-10-26: "renova as bearskins", all of them, UK included).
# The v2-v5 locks were one wide leaf each (11-17 mm, smooth outline) on a tile with darkened edges: up close the fur read
# as shingles or broad feathers. v6:
#   - geometry: a narrower lock (0.75 x the old width) whose body splits at 45 % of its length into THREE fine tips of
#     slightly different lengths that part a little ("pontas que desfiam"); single-sided as before (the underside lies on
#     the shell); 15 triangles per long lock (was 12), 3 per short under-fur lock (was 4, now two tips);
#   - tile: ~300 fine strands that converge on the three tips, dark roots, a warm brown sheen on the strand crests (black
#     bearskin is brownish in the light), no darkened lock edge (the parting tips give the depth now).
# UV of a lock: u across (0..1), v root -> tip (0..1); tip k ends at u = (k + 0.5) / 3 (TIP_U).
# Used by blockout_bonnet_guarda.py, blockout_bonnet_suica.py, blockout_bonnet_varsovia.py, blockout_bonnet_italia.py,
# blockout_raupenhelm.py, bonnet_highland_uk.py (geometry) and texturizar_shako_fr.py, texturizar_aliados.py,
# texturizar_shako_uk.py (tile).
import math
import numpy as np

WIDTH = 0.75                         # width factor applied to the callers' old lock widths
SPLIT = 0.45                         # body / tips
TIP_U = (1 / 6, 0.5, 5 / 6)


def lock(bm, uvl, tint, rnd, centre, n, sd, W, short=False, shade=None):
    """One lock. centre(t) -> point of the lock's mid line at t (0 root .. 1 tip, the caller's arch, gravity, tuck and
    drop already in it); n = outward normal of the shell at the root; sd = unit vector across the lock; W = the OLD
    full width (scaled here by WIDTH). Faces get UV (u across, v along) and the shade float `tint`."""
    W = W * WIDTH
    sh = rnd.uniform(0.0, 1.0) if shade is None else shade
    faces = []

    def P(t, u, w_t, lift=0.0, spread=0.0):
        c = centre(t)
        x = (u - 0.5) * w_t
        cup = n * (0.35 * abs(x))                      # edges curl into the mass
        return c + sd * (x + spread) - cup + n * lift

    def face(vs, uvs):
        f = bm.faces.new(vs)
        for l, uv in zip(f.loops, uvs):
            l[uvl].uv = uv
        f[tint] = sh
        f.smooth = True
        f.normal_update()
        if f.normal.dot(n) < 0:
            f.normal_flip()
        faces.append(f)

    if short:                                          # under-fur: root edge, two tips
        r = [bm.verts.new(P(0.0, u, W * 0.95)) for u in (0.0, 0.5, 1.0)]
        l1, l2 = rnd.uniform(0.85, 1.0), rnd.uniform(0.85, 1.0)
        ta = bm.verts.new(P(l1, 0.25, W * 0.2, spread=-0.12 * W))
        tb = bm.verts.new(P(l2, 0.75, W * 0.2, spread=0.12 * W))
        face((r[0], r[1], ta), ((0.0, 0.0), (0.5, 0.0), (0.25, l1)))
        face((r[1], r[2], tb), ((0.5, 0.0), (1.0, 0.0), (0.75, l2)))
        face((r[1], tb, ta), ((0.5, 0.0), (0.75, l2), (0.25, l1)))
        return faces
    # body: root row and split row, 4 columns (3 strips), the middle columns raised (rounded lock)
    us = (0.0, 1 / 3, 2 / 3, 1.0)
    rise = (0.0, 0.0011, 0.0011, 0.0)
    root = [bm.verts.new(P(0.0, u, W * 0.80, lift=r)) for u, r in zip(us, rise)]
    mid = [bm.verts.new(P(SPLIT, u, W * 1.0, lift=r * 1.2)) for u, r in zip(us, rise)]
    for k in range(3):
        face((root[k], root[k + 1], mid[k + 1], mid[k]), ((us[k], 0.0), (us[k + 1], 0.0), (us[k + 1], SPLIT), (us[k], SPLIT)))
    # three tips: each from its strip of the split row, through a narrower station, to a point; they part a little
    for k in range(3):
        tl = rnd.uniform(0.82, 1.0) if k != 1 else rnd.uniform(0.92, 1.0)      # the middle one is the longest
        part = (k - 1) * W * rnd.uniform(0.10, 0.22)
        tm = SPLIT + (tl - SPLIT) * 0.55
        a = bm.verts.new(P(tm, TIP_U[k] - 0.10, W * 0.9, spread=part * 0.5))
        b = bm.verts.new(P(tm, TIP_U[k] + 0.10, W * 0.9, spread=part * 0.5))
        tip = bm.verts.new(P(tl, TIP_U[k], W * 0.1, spread=part))
        ua, ub = TIP_U[k] - 0.10, TIP_U[k] + 0.10
        face((mid[k], mid[k + 1], b, a), ((us[k], SPLIT), (us[k + 1], SPLIT), (ub, tm), (ua, tm)))
        face((a, b, tip), ((ua, tm), (ub, tm), (TIP_U[k], tl)))
    return faces


def paint_tile(n, rgb, shade, seed):
    """Lock tile v6 (n x n px; rows = v root -> tip, cols = u). Returns (colour rgb, normal rgb, height). ~300 fine strands,
    each running from the root to one of the three tips (TIP_U), waving a little; dark roots, a warm sheen on the crests."""
    v, u = np.mgrid[0:n, 0:n] / (n - 1.0)
    rng = np.random.default_rng(seed)
    h = np.zeros((n, n), np.float32)
    lit = np.zeros((n, n), np.float32)
    for s in range(300):
        k = s % 3
        c0 = rng.uniform(k / 3, (k + 1) / 3) * 0.9 + 0.05
        end = rng.uniform(0.70, 1.0)
        amp = rng.uniform(0.002, 0.012); fr = rng.uniform(4, 11); ph = rng.uniform(0, 6.3)
        conv = np.clip((v - 0.2) / 0.8, 0, 1) ** 1.3                 # gathers toward its tip after the split
        cx = c0 + (TIP_U[k] - c0) * conv + amp * np.sin(fr * v + ph)
        w = rng.uniform(0.0025, 0.0065) * (1.0 - 0.55 * v)
        prof = np.exp(-((u - cx) / w) ** 2) * (v < end) * (1 - np.clip((v - end + 0.12) / 0.12, 0, 1))
        hv = rng.uniform(0.55, 1.0)
        h = np.maximum(h, prof * hv)
        lit += prof * rng.uniform(0.0, 0.6) * (0.4 + 0.6 * v)          # the sheen is on the hanging part
    root = np.clip(1 - v / 0.25, 0, 1)
    f = (0.30 + 0.95 * h + 0.30 * np.clip(lit, 0, 1)) * shade * (1 - 0.35 * root)
    warm = np.array((0.016, 0.009, 0.004))                          # brown sheen of black bearskin
    col = np.clip(np.array(rgb)[None, None, :] * f[..., None] + warm[None, None, :] * np.clip(lit, 0, 1)[..., None], 0, 1)
    gy, gx = np.gradient(h)
    nv = np.dstack([-gx * 12, -gy * 12, np.ones_like(h)])
    nv /= np.linalg.norm(nv, axis=2, keepdims=True)
    return col, nv * 0.5 + 0.5, h
