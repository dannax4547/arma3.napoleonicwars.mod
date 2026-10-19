# Colour variants of an already textured French shako WITHOUT a new model (user 2026-10-19, image of the light infantry
# carabinier shako: "faz uma variante desta ao inves da cor vermelha coloca uma cor azul escura"). Same method as
# variantes_pompom_fr.py (read only, not edited): the texels of the faces whose surface kind has the source colour are
# rasterised from the game UV (attribute hcl_kind_i + ob["hcl_kinds"]), grown by the bake margin, and only the texels
# close to the original hue are recoloured, keeping the baked shading (AO, wool and feather noise):
#   new_linear = target_albedo * shading,  shading = projection of the texel on the source albedo (texturizar_shako_fr.COL
#   / PENA, linear values).
# The cockade is never touched (its red ring is the national colour, not the company distinction).
#   blender -b --factory-startup <texturas .blend> --python variantes_cor_shako_fr.py -- <tex dir> <tag> <from> <to> <suffix>
#   e.g. ... -- source/textures/hcl_shako_fr ligeira_carabineiro_gala vermelho azul_escuro azul
#   -> hcl_shako_fr_ligeira_carabineiro_gala_azul_co.png
import bpy, sys, os, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
TEX, TAG, SRC, DST, SUF = os.path.abspath(a[0]), a[1], a[2], a[3], a[4]
# linear albedos: sources as in texturizar_shako_fr.py (COL for cloth/lace/cords, PENA for feathers)
ALB = {"vermelho": {"cordao": (0.55, 0.035, 0.035), "galao": (0.55, 0.035, 0.035), "pena": (0.74, 0.07, 0.05)}}
# targets (ours, 🔶): dark blue, a little lighter for the feathers so the plume does not read black
TGT = {"azul_escuro": {"cordao": (0.03, 0.055, 0.24), "galao": (0.03, 0.055, 0.24), "pena": (0.04, 0.07, 0.30)}}
# 2026-10-19 user: "faz ela um pouco mais clara" -> twice the first values (0.015, 0.025, 0.12 / 0.02, 0.035, 0.16)
KINDS = ("cordao", "galao", "pena")                  # never "cocar"
GROW = 6                                             # px, = bake margin of texturizar_shako_fr.py


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


ob = bpy.data.objects[f"HCL_Shako_Fr_{TAG}_LOD0"]
me = ob.data
kinds = [k.split(":") for k in ob["hcl_kinds"].split(",")]
src = os.path.join(TEX, f"hcl_shako_fr_{TAG}_co.png")
im = bpy.data.images.load(src)
W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)          # row 0 = bottom (v = 0)
lin = to_lin(px[..., :3])
out = px.copy()
kattr = me.attributes["hcl_kind_i"].data
uv = me.uv_layers["UVMap"].data
done = np.zeros((H, W), bool)
for kind in KINDS:
    idx = {i for i, (k, c) in enumerate(kinds) if k == kind and c == SRC}
    if not idx:
        continue
    mask = np.zeros((H, W), bool)
    for p in me.polygons:
        if kattr[p.index].value not in idx:
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
            inside = (l0 >= -0.02) & (l1 >= -0.02) & (1 - l0 - l1 >= -0.02)
            mask[ya:yb + 1, xa:xb + 1] |= inside
    for _ in range(GROW):
        m2 = mask.copy()
        m2[1:] |= mask[:-1]; m2[:-1] |= mask[1:]; m2[:, 1:] |= mask[:, :-1]; m2[:, :-1] |= mask[:, 1:]
        mask = m2
    alb = np.array(ALB[SRC][kind], np.float32)
    hue = alb / np.linalg.norm(alb)
    close = (lin @ hue) / (np.linalg.norm(lin, axis=2) + 1e-6) > 0.90   # red-ish texels only (not black leather, white)
    sel = mask & close & ~done
    shade = (lin @ alb) / float(alb @ alb)
    tgt = np.array(TGT[DST][kind], np.float32)
    out[..., :3][sel] = to_srgb(tgt[None, :] * shade[sel][:, None])
    done |= sel
    print(f"COR {TAG} {kind}:{SRC} -> {DST}: {int(sel.sum())} texels de {int(mask.sum())} na mascara; "
          f"sombreamento mediano {float(np.median(shade[sel])):.3f}")
dst = os.path.join(TEX, f"hcl_shako_fr_{TAG}_{SUF}_co.png")
o = bpy.data.images.new(os.path.basename(dst), W, H, alpha=False)
o.colorspace_settings.name = "sRGB"
out[..., 3] = 1.0
o.pixels.foreach_set(out.ravel())
o.filepath_raw = dst; o.file_format = "PNG"; o.save()
print(f"  -> {os.path.basename(dst)}")
