# Fusilier companies 2-4 of the French shakos WITHOUT a new model: the pompom texels of an already textured shako
# (texturizar_shako_fr.py) are recoloured in its _co map, keeping the baked shading (AO, wool fuzz). The game swaps the
# texture through hiddenSelectionsTextures (selection "camo" = the whole shako), so one P3D serves the 4 companies.
# Company colours (order of February 1811, spec docs/specs/barretina_francesa_1812.md section 2, decision B4; the
# shades are ours, 🔶): 2nd sky blue (bleu celeste), 3rd aurore (orange-pink), 4th violet.
# Pompom texels = UV triangles of the faces whose surface kind is "la" (wool; attribute hcl_kind_i + ob["hcl_kinds"]),
# rasterised and grown by the bake margin; inside that mask only texels close to the original pompom hue change.
#   blender -b --factory-startup <texturas .blend> --python variantes_pompom_fr.py -- <tex dir> <tag>[,<tag>...]
import bpy, sys, os, math
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
TEX = os.path.abspath(a[0])
TAGS = a[1].split(",")
COMP = {"2a_comp": (0.13, 0.36, 0.78), "3a_comp": (0.86, 0.34, 0.12), "4a_comp": (0.22, 0.045, 0.30)}   # linear RGB
ALBEDO = {"verde_esc": (0.02, 0.15, 0.05)}           # texturizar_shako_fr.COL (linear)
GROW = 6                                             # px, = bake margin of texturizar_shako_fr.py


def to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


for tag in TAGS:
    ob = bpy.data.objects[f"HCL_Shako_Fr_{tag}_LOD0"]
    me = ob.data
    kinds = [k.split(":") for k in ob["hcl_kinds"].split(",")]
    la = {i for i, (k, _) in enumerate(kinds) if k == "la"}
    base_name = kinds[min(la)][1]
    src = os.path.join(TEX, f"hcl_shako_fr_{tag}_co.png")
    im = bpy.data.images.load(src)
    W, H = im.size
    px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)          # row 0 = bottom (v = 0)
    kattr = me.attributes["hcl_kind_i"].data
    uv = me.uv_layers["UVMap"].data
    mask = np.zeros((H, W), bool)
    for p in me.polygons:
        if kattr[p.index].value not in la:
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
    for _ in range(GROW):                            # grow by the bake margin (4-neighbourhood)
        m2 = mask.copy()
        m2[1:] |= mask[:-1]; m2[:-1] |= mask[1:]; m2[:, 1:] |= mask[:, :-1]; m2[:, :-1] |= mask[:, 1:]
        mask = m2
    lin = to_lin(px[..., :3])
    ref = np.median(lin[mask], axis=0)               # the pompom's own (shaded) colour
    hue = ref / max(1e-6, np.linalg.norm(ref))
    nrm = np.linalg.norm(lin, axis=2) + 1e-6
    close = (lin @ hue) / nrm > 0.93                 # direction of the colour close to the pompom's (not black leather)
    sel = mask & close
    f = (lin @ ref) / float(ref @ ref)               # shading of each texel relative to the median
    print(f"POMPOM {tag}: cor original {base_name}, texels {int(sel.sum())} de {int(mask.sum())} na mascara; mediana linear {np.round(ref, 3)}")
    alb = np.array(ALBEDO[base_name], np.float32)   # albedo the bake started from (texturizar_shako_fr.COL)
    shade_med = float(ref @ alb) / float(alb @ alb)  # baked shading (AO x wool noise) of the median texel
    print(f"  sombreamento mediano {shade_med:.3f}")
    for comp, rgb in COMP.items():
        out = px.copy()
        out[..., :3][sel] = to_srgb(np.array(rgb, np.float32)[None, :] * shade_med * f[sel][:, None])
        dst_tag = tag.replace("1a_comp", comp) if tag.endswith("1a_comp") else f"{tag}_{comp}"
        dst = os.path.join(TEX, f"hcl_shako_fr_{dst_tag}_co.png")
        o = bpy.data.images.new(os.path.basename(dst), W, H, alpha=False)
        o.colorspace_settings.name = "sRGB"
        out[..., 3] = 1.0
        o.pixels.foreach_set(out.ravel())
        o.filepath_raw = dst; o.file_format = "PNG"; o.save()
        print(f"  -> {os.path.basename(dst)}")
