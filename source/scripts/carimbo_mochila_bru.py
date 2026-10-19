# Brunswick 1815 knapsack (docs/specs/kgl_brunswick_1815.md 4; Brigade-Uniformtafel Nr. 176, 2. Linien-Bataillon
# 1814-1815, back view: black knapsack with the leaping Welfenross in white metal on the flap). Texture-only variant of
# the British Trotter knapsack (same mesh, HCL_B_Fr1812_Havresac_LOD0 with the hcl_b_uk1812_mochila UVs): the horse
# outline (cavalo_bru.json, hand-drawn simplified, 🔶) is stamped in white metal on the flap. The stamp is placed in
# 3D: every texel of the back-facing triangles gets its surface point by barycentric interpolation, and texels whose
# point falls inside the horse (on the back plane, centred on the flap) are painted, with a darker rim and a soft
# highlight so it reads as a raised plate.
#   blender -b --factory-startup --python carimbo_mochila_bru.py -- <equipment LOD0 .blend> <base _co.png> <horse.json>
#           <out _co.png> [altura=0.075] [centro_z=0.62] [correias=preto|branco]  (centro_z = fraction of the back face height)
import bpy, sys, json, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
EQ, BASE, HORSE, OUT = a[:4]
OPT = dict(x.split("=", 1) for x in a[4:] if "=" in x)
ALT = float(OPT.get("altura", 0.075)); CZ = float(OPT.get("centro_z", 0.62))
bpy.ops.wm.open_mainfile(filepath=EQ)
ob = bpy.data.objects["HCL_B_Fr1812_Havresac_LOD0"]
me = ob.data
uv = me.uv_layers["UVMap"].data
img = bpy.data.images.load(BASE); W, H = img.size
px = np.array(img.pixels[:], np.float32).reshape(H, W, 4)
if OPT.get("correias", "preto") == "preto":
    # Brunswick leather was black (kgl_brunswick_1815.md 4, [B1][B5]): the pipeclayed straps of the British texture
    # (light, unsaturated texels) become black leather, keeping their shading; brass buckles (saturated) are left alone
    rgb = px[..., :3]
    lum = rgb.mean(axis=2); sat = rgb.max(axis=2) - rgb.min(axis=2)
    strap = (lum > 0.30) & (sat < 0.10)
    k_ = np.clip((lum - 0.30) / 0.10, 0, 1)[..., None] * strap[..., None]
    dark = np.array([0.035, 0.032, 0.03], np.float32) * (0.6 + 0.6 * (lum / max(float(lum[strap].mean()), 1e-3)))[..., None] \
        if strap.any() else rgb
    px[..., :3] = rgb * (1 - k_) + dark * k_
    print(f"CORREIAS: {int(strap.sum())} texels claros passados a couro preto")
M = ob.matrix_world
tris = []
for p in me.polygons:
    n = (M.to_3x3() @ p.normal).normalized()
    if n.y < 0.85:                                           # the back panel faces +Y (away from the wearer)
        continue
    vs = [M @ me.vertices[i].co for i in p.vertices]; us = [uv[li].uv[:] for li in p.loop_indices]
    for k in range(1, len(vs) - 1):
        tris.append(((vs[0], vs[k], vs[k + 1]), (us[0], us[k], us[k + 1])))
P3 = np.array([[v[:] for v in t[0]] for t in tris]); U2 = np.array([[u for u in t[1]] for t in tris])
xs, zs = P3[..., 0].ravel(), P3[..., 2].ravel()
x_c = (xs.min() + xs.max()) / 2; z_c = zs.min() + CZ * (zs.max() - zs.min())
print(f"FACE DE TRAS: {len(tris)} triangulos; x {xs.min():.3f}..{xs.max():.3f}, z {zs.min():.3f}..{zs.max():.3f}; centro {x_c:.3f}, {z_c:.3f}")
hj = json.load(open(HORSE, encoding="utf-8"))
loop = np.array(hj["loops"][0], np.float64)
loop[:, 1] = 100 - loop[:, 1]                                # y up
loop -= loop.mean(axis=0)
loop *= ALT / (loop[:, 1].max() - loop[:, 1].min())
loop[:, 0] *= -1                                             # seen from behind: the horse faces the viewer's left


def inside(x, z, poly):
    c = np.zeros(x.shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        cond = ((y1 > z) != (y2 > z)) & (x < (x2 - x1) * (z - y1) / (y2 - y1 + 1e-12) + x1)
        c ^= cond
    return c


painted = 0
for (p3, u2) in zip(P3, U2):
    uvp = u2 * [W, H]
    x0, y0 = np.floor(uvp.min(0)).astype(int); x1, y1 = np.ceil(uvp.max(0)).astype(int)
    if x1 <= x0 or y1 <= y0:
        continue
    gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = uvp
    den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-9:
        continue
    l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
    l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
    l3 = 1 - l1 - l2
    m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
    if not m.any():
        continue
    X = l1 * p3[0][0] + l2 * p3[1][0] + l3 * p3[2][0] - x_c
    Z = l1 * p3[0][2] + l2 * p3[1][2] + l3 * p3[2][2] - z_c
    ins = m & inside(X, Z, loop)
    # rim: inside, but within ~1 mm of the outline (sampled by shrinking the test point toward the centre)
    rim = ins & ~inside(X * 1.04, Z * 1.04, loop)
    iy, ix = gy[ins].astype(int), gx[ins].astype(int)
    keep = (iy >= 0) & (iy < H) & (ix >= 0) & (ix < W)
    shade = 0.55 + 0.35 * np.clip(0.5 + Z[ins] / ALT, 0, 1)        # soft light from above
    col = np.array([0.62, 0.62, 0.60], np.float32)[None, :] * shade[:, None]
    col[rim[ins]] *= 0.55
    px[iy[keep], ix[keep], :3] = col[keep]
    painted += int(keep.sum())
out = bpy.data.images.new("mochila_bru", W, H, alpha=False)
out.pixels.foreach_set(px.ravel())
out.filepath_raw = OUT; out.file_format = "PNG"; out.save()
print(f"OK {OUT}: cavalo de {ALT * 1000:.0f} mm na aba, {painted} texels pintados")
