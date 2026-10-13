# Colour variants of a baked headgear texture WITHOUT a new model or a new bake (generic form of
# variantes_pompom_fr.py): the texels of the chosen surfaces (kind:colour of texturizar_shako_fr.py, stored in the
# object's hcl_kind_i attribute + ob["hcl_kinds"]) are found by rasterising their UV triangles (grown by the bake
# margin) and repainted with a new albedo, keeping the baked shading (AO, cloth nap) texel by texel. Only the _co map
# changes; _nohq and _smdi stay shared, the game swaps _co through hiddenSelectionsTextures.
#   blender -b --factory-startup <texturas .blend> --python recolorir_textura.py -- <tex dir> <object> <src prefix>
#           <dst prefix>=<kind:colour>=<r,g,b>[;<kind:colour>=<r,g,b>...] [<dst prefix>=...]
# colours are LINEAR (as the albedos of texturizar_shako_fr.COL); the source albedo of each surface is read from ALB.
# 2026-10-12: the Prussian cloth caps (blockout_bone_landwehr.py), 5 cloth/band colours of the mod art.
import bpy, sys, os, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
TEX, OBJ, SRC = os.path.abspath(a[0]), a[1], a[2]
JOBS = []
for spec in a[3:]:
    dst, rest = spec.split("=", 1)
    rules = {}
    for r in rest.split(";"):
        k, rgb = r.rsplit("=", 1)
        rules[k] = tuple(float(x) for x in rgb.split(","))
    JOBS.append((dst, rules))
# source albedos (linear) = texturizar_shako_fr.COL
ALB = {"azul_pano": (0.010, 0.016, 0.040), "verde_pano": (0.010, 0.022, 0.010), "vermelho": (0.55, 0.035, 0.035),
       "verde_esc": (0.02, 0.15, 0.05)}
GROW = 6


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


ob = bpy.data.objects[OBJ]
me = ob.data
kinds = ob["hcl_kinds"].split(",")
im = bpy.data.images.load(os.path.join(TEX, f"{SRC}_co.png"))
W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)
lin = to_lin(px[..., :3])
kattr = me.attributes["hcl_kind_i"].data
uv = me.uv_layers["UVMap"].data


def mask_of(key):
    ki = kinds.index(key)
    m = np.zeros((H, W), bool)
    for p in me.polygons:
        if kattr[p.index].value != ki:
            continue
        P2 = [(uv[li].uv.x * W - 0.5, uv[li].uv.y * H - 0.5) for li in p.loop_indices]
        for k in range(1, len(P2) - 1):
            (x0, y0), (x1, y1), (x2, y2) = P2[0], P2[k], P2[k + 1]
            xa, xb = max(0, int(math.floor(min(x0, x1, x2))) - 1), min(W - 1, int(math.ceil(max(x0, x1, x2))) + 1)
            ya, yb = max(0, int(math.floor(min(y0, y1, y2))) - 1), min(H - 1, int(math.ceil(max(y0, y1, y2))) + 1)
            det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(det) < 1e-12:
                continue
            gy, gx = np.mgrid[ya:yb + 1, xa:xb + 1].astype(np.float32)
            l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / det
            l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / det
            m[ya:yb + 1, xa:xb + 1] |= (l0 >= -0.02) & (l1 >= -0.02) & (1 - l0 - l1 >= -0.02)
    core = m.copy()
    for _ in range(GROW):
        m2 = m.copy()
        m2[1:] |= m[:-1]; m2[:-1] |= m[1:]; m2[:, 1:] |= m[:, :-1]; m2[:, :-1] |= m[:, 1:]
        m = m2
    return core, m


MASKS = {}
for _, rules in JOBS:
    for key in rules:
        if key not in MASKS:
            core, grown = mask_of(key)
            ref = np.median(lin[core], axis=0)
            alb = np.array(ALB[key.split(":")[1]], np.float32)
            shade = (lin @ alb) / float(alb @ alb)            # baked shading of every texel against the source albedo
            MASKS[key] = (core, grown, shade)
            print(f"SUPERFICIE {key}: {int(core.sum())} texels (+{int((grown & ~core).sum())} de margem); mediana linear "
                  f"{np.round(ref, 3)}, sombreamento mediano {float(np.median(shade[core])):.3f}")
# grown masks of different surfaces may overlap at shared borders: each texel goes to the surface whose CORE is
# nearest, approximated by giving priority to core texels
for dst, rules in JOBS:
    out = lin.copy()
    taken = np.zeros((H, W), bool)
    for key, rgb in rules.items():
        core, _, shade = MASKS[key]
        out[core] = np.array(rgb, np.float32)[None, :] * shade[core][:, None]
        taken |= core
    for key, rgb in rules.items():
        _, grown, shade = MASKS[key]
        m = grown & ~taken
        out[m] = np.array(rgb, np.float32)[None, :] * shade[m][:, None]
        taken |= m
    img = np.dstack([to_srgb(out), np.ones((H, W), np.float32)])
    o = bpy.data.images.new(dst, W, H, alpha=False)
    o.colorspace_settings.name = "sRGB"
    o.pixels.foreach_set(img.astype(np.float32).ravel())
    o.filepath_raw = os.path.join(TEX, f"{dst}_co.png"); o.file_format = "PNG"; o.save()
    print(f"  -> {dst}_co.png: " + ", ".join(f"{k} -> {v}" for k, v in rules.items()))
