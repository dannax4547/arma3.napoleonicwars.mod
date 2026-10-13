# Blender headless: generates ORIGINAL procedural textures for the Prussian 1813 shako (v2).
# No third-party pixels are used. Outputs, in <out_dir>:
#   hcl_shako_prussline1813_co.png            colour (sRGB)
#   hcl_shako_prussline1813_nohq.png          tangent-space normal map (OpenGL/Blender convention, +Y up)
#   hcl_shako_prussline1813_rough_preview.png roughness, used only for Blender previews
# Usage: blender -b --factory-startup --python generate_shako_textures.py -- <out_dir> [v2|v3]
#   v2 (default): stitched leather band, felt crown, white loop.
#   v3: patent-leather band/visor/crown, black chinstrap, yellow loop, plus a white twill top band
#       (0,612 768x56, wraps) and a pompom disc (0,680 192x192).
#
# Layout (pixels, top-left origin) shared with build_shako_v2.py:
#   felt body 0..1024 x 0..288 (wraps) | leather band 0..1024 x 288..336 (wraps)
#   crown box 0,352 256x256 | inside 256,352 256x256 | visor 512,352 256x256 | cockade 768,352 256x256
#   loop 768,608 64x256 | button 832,608 64x64 | side boss 896,608 64x64 | chinstrap 0,880 768x32
import bpy, sys, os, math
import numpy as np

_args = sys.argv[sys.argv.index("--") + 1:]
OUT_DIR = _args[0]
STYLE = _args[1] if len(_args) > 1 else "v2"
LOOP_COLOUR = "yellow" if STYLE == "v3" else "white"
S = 1024
rng = np.random.default_rng(1813)

co = np.zeros((S, S, 3), np.float32)
hgt = np.full((S, S), 0.5, np.float32)
rough = np.full((S, S), 0.9, np.float32)


# ---------------------------------------------------------------- noise helpers
def vnoise(h, w, cy, cx, wrap_x=False):
    g = rng.random((cy + 1, cx + 1)).astype(np.float32)
    if wrap_x:
        g[:, -1] = g[:, 0]
    xs = np.arange(w) * cx / w
    ys = np.arange(h) * cy / h
    x0 = np.floor(xs).astype(int); fx = xs - x0; fx = fx * fx * (3 - 2 * fx)
    y0 = np.floor(ys).astype(int); fy = ys - y0; fy = (fy * fy * (3 - 2 * fy))[:, None]
    a, b = g[y0][:, x0], g[y0][:, x0 + 1]
    c, d = g[y0 + 1][:, x0], g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(h, w, cy, cx, octaves=3, wrap_x=False):
    total, amp, norm = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(octaves):
        total += amp * vnoise(h, w, min(cy * 2 ** o, h), min(cx * 2 ** o, w), wrap_x)
        norm += amp
        amp *= 0.5
    return total / norm * 2 - 1          # roughly -1..1


def pix(h, w):
    return rng.random((h, w)).astype(np.float32) - 0.5


def polar(size, cx, cy):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    return np.hypot(xx - cx, yy - cy), np.arctan2(yy - cy, xx - cx)


def put(x, y, col, h, r):
    hh, ww = h.shape
    co[y:y + hh, x:x + ww] = col
    hgt[y:y + hh, x:x + ww] = h
    rough[y:y + hh, x:x + ww] = r


def felt(h, w, wrap, base=0.052):
    n_low, n_fine = fbm(h, w, 2, 8, 3, wrap), fbm(h, w, 32, 128, 3, wrap)
    folds, fuzz = fbm(h, w, 1, 24, 2, wrap), pix(h, w)
    lum = base + 0.008 * n_low + 0.005 * n_fine + 0.006 * folds + 0.010 * fuzz
    col = lum[..., None] * np.array([1.0, 0.95, 0.97], np.float32)
    height = 0.5 + 0.05 * n_fine + 0.05 * fuzz + 0.03 * folds      # felt is soft: keep relief subtle
    return col, height, 0.88 + 0.05 * n_fine


def leather(h, w, wrap, base=(0.040, 0.034, 0.030)):
    grain = fbm(h, w, max(1, h // 4), w // 4, 2, wrap)
    scuff = np.clip(fbm(h, w, 2, 16, 3, wrap) - 0.35, 0, 1)
    col = np.array(base, np.float32) * (1 + 0.25 * (grain + 0.6 * pix(h, w))[..., None]) + 0.05 * scuff[..., None]
    return col, 0.5 + 0.04 * grain, 0.40 + 0.06 * grain + 0.25 * scuff


def stitches(col, height, r, row, period, dash, color, start=0):
    xs = np.arange(col.shape[1])
    on = ((xs + start) % period) < dash
    col[row:row + 2, on] = color
    height[row:row + 2, on] = 0.68
    height[row:row + 2, ~on] = 0.38                 # needle holes / groove between stitches
    r[row:row + 2, on] = 0.8


# ---------------------------------------------------------------- felt body (wraps around, seam at the back)
c, h, r = felt(288, 1024, True)
y = np.arange(288, dtype=np.float32)[:, None]
dust = 0.022 * np.exp(-y / 10) + 0.010 * np.exp(-(287 - y) / 6)
c += dust[..., None] * np.array([0.60, 0.55, 0.45], np.float32)
xs = np.arange(1024)
dseam = np.minimum(xs, 1024 - xs)[None, :]           # distance to the back seam (u = 0 / 1)
c[:, :, :] *= np.where(dseam < 3, 0.55, 1.0)[..., None]
h = np.where(dseam < 3, 0.25, h)
for sx in (5, 1024 - 6):                             # stitches either side of the seam
    for sy in range(4, 288, 9):
        c[sy:sy + 4, sx:sx + 2] = 0.11
        h[sy:sy + 4, sx:sx + 2] = 0.62
put(0, 0, c, h, r)

# ---------------------------------------------------------------- leather band (raised, stitched both edges)
def patent(h_, w_, wrap):
    # patent (lacquered) leather: very dark, smooth and glossy
    g = fbm(h_, w_, max(1, h_ // 16), max(1, w_ // 16), 2, wrap)
    col = np.array([0.018, 0.018, 0.020], np.float32) * (1 + 0.15 * g[..., None])
    return col, 0.5 + 0.01 * g, 0.12 + 0.03 * g

edge = np.minimum(np.arange(48), 47 - np.arange(48)).astype(np.float32)[:, None]
if STYLE == "v3":
    c, h, r = patent(48, 1024, True)
    h = h - 0.20 * np.clip(1 - edge / 3, 0, 1)        # rolled edges
    c *= np.clip(0.7 + edge / 10, 0.7, 1.0)[..., None]
else:
    c, h, r = leather(48, 1024, True)
    c *= np.clip(0.55 + edge / 8, 0.55, 1.0)[..., None]
    h = h - 0.25 * np.clip(1 - edge / 4, 0, 1)
    stitches(c, h, r, 6, 10, 5, 0.10)
    stitches(c, h, r, 40, 10, 5, 0.10, start=5)
put(0, 288, c, h, r)

# ---------------------------------------------------------------- crown (felt, stitched ring where it meets the wall)
if STYLE == "v3":
    c, h, r = patent(256, 256, False)                          # leather top in v3
    c = c + 0.008                                             # dust dulls the top a little
    r = r + 0.10
else:
    c, h, r = felt(256, 256, False, base=0.058)
    c += 0.012 * np.array([0.6, 0.55, 0.45], np.float32)      # a little more dust on top
rad, ang = polar(256, 128, 128)
ring = np.abs(rad - 108) < 1.6
on = ((ang + math.pi) * 108 / 9 % 1.0) < 0.5
c[ring & on] = 0.11; h[ring & on] = 0.65; h[ring & ~on] = 0.35
c[rad > 112] *= 0.7
put(0, 352, c, h, r)

# ---------------------------------------------------------------- inside (darkened felt)
c, h, r = felt(256, 256, False, base=0.035)
put(256, 352, c, h, r)

# ---------------------------------------------------------------- visor: lacquered leather, parametric (x = around, y = root -> edge)
c, h, r = leather(256, 256, False, base=(0.020, 0.020, 0.022))
h = 0.5 + 0.012 * fbm(256, 256, 3, 3, 2)            # lacquered: smooth surface
r = (0.12 if STYLE == "v3" else 0.20) + 0.04 * fbm(256, 256, 4, 4, 2)
yy = np.arange(256)[:, None]
binding = (yy >= 230)
c = np.where(binding[..., None], c * 1.5 + 0.01, c)
h = np.where(binding, 0.70 - 0.004 * (yy - 243) ** 2, h)
r = np.where(binding, 0.34, r)
stitches(c, h, r, 222, 8, 4, 0.085)
for _ in range(25):                                  # fine scratches
    x0, y0 = rng.uniform(0, 256), rng.uniform(0, 230)
    a, L = rng.uniform(0, math.pi), rng.uniform(6, 30)
    for t in np.linspace(0, L, int(L * 2)):
        px, py = int(x0 + t * math.cos(a)), int(y0 + t * math.sin(a))
        if 0 <= px < 256 and 0 <= py < 230:
            c[py, px] += 0.018; h[py, px] = 0.48; r[py, px] = 0.45
put(512, 352, c, h, r)

# ---------------------------------------------------------------- cockade: black centre, pleated white ring, black rim
rad, ang = polar(256, 128, 128)
q = rad / 120.0
pleat = 0.5 + 0.5 * np.cos(ang * 56)
cloth = fbm(256, 256, 16, 16, 2) * 0.03 + pix(256, 256) * 0.02
white = np.array([0.82, 0.81, 0.77], np.float32) * (0.86 + 0.14 * pleat)[..., None] + cloth[..., None]
black = (0.030 + cloth)[..., None] * np.ones(3, np.float32)
c = np.where(((q >= 0.40) & (q < 0.92))[..., None], white, black)
h = np.where(q < 0.40, 0.55 + 0.05 * cloth, 0.45 + 0.30 * pleat)
h = np.where(q > 1.0, 0.5, h)
put(768, 352, c, h, np.full((256, 256), 0.75, np.float32))

# ---------------------------------------------------------------- loop (white worsted lace, herringbone weave)
yy, xx = np.mgrid[0:256, 0:64].astype(np.float32)
weave = ((yy + np.abs(xx - 32) * 0.9) % 10) < 5
lum = np.where(weave, 0.86, 0.77) - 0.05 * np.clip(fbm(256, 64, 8, 2, 2), 0, 1)
border = (xx < 6) | (xx > 57)
if LOOP_COLOUR == "yellow":
    # yellow worsted lace with white edges and a thin dark line between them
    c = (lum / 0.86)[..., None] * np.array([0.86, 0.64, 0.16], np.float32)
    c = np.where(border[..., None], np.array([0.84, 0.83, 0.79], np.float32), c)
    line = ((xx >= 6) & (xx < 8)) | ((xx > 55) & (xx <= 57))
    c = np.where(line[..., None], np.array([0.25, 0.20, 0.08], np.float32), c)
else:
    lum = np.where(border, 0.62, lum)
    c = lum[..., None] * np.array([1.0, 0.99, 0.95], np.float32)
h = np.where(border, 0.45, np.where(weave, 0.62, 0.45))
put(768, 608, c, h, np.full((256, 64), 0.85, np.float32))

# ---------------------------------------------------------------- brass button and side bosses
def brass(rosette):
    rad, ang = polar(64, 32, 32)
    tarnish = np.clip(fbm(64, 64, 4, 4, 3), -1, 1)
    c = np.array([0.80, 0.62, 0.28], np.float32) * (0.85 + 0.15 * tarnish)[..., None]
    c = np.where(((rad > 25) & (rad < 28))[..., None], c * 0.6, c)
    h = 0.5 + 0.3 * np.clip(1 - (rad / 28) ** 2, 0, 1)
    if rosette:
        lines = np.cos(ang * 24) > 0.75
        c = np.where(lines[..., None], c * 0.65, c)
        h = np.where(lines, h - 0.1, h)
    return c, h, 0.28 + 0.12 * np.abs(tarnish)

put(832, 608, *brass(False))
put(896, 608, *brass(True))

# ---------------------------------------------------------------- chinstrap (brown-black leather, stitched)
c, h, r = leather(32, 768, False, base=(0.025, 0.024, 0.024) if STYLE == "v3" else (0.050, 0.040, 0.034))
edge = np.minimum(np.arange(32), 31 - np.arange(32)).astype(np.float32)[:, None]
c *= np.clip(0.6 + edge / 6, 0.6, 1.0)[..., None]
stitches(c, h, r, 4, 9, 4, 0.09 if STYLE == "v3" else 0.11)
stitches(c, h, r, 26, 9, 4, 0.09 if STYLE == "v3" else 0.11, start=4)
put(0, 880, c, h, r)

if STYLE == "v3":
    # ------------------------------------------------------------ white twill top band (wraps around)
    yy, xx = np.mgrid[0:56, 0:768].astype(np.float32)
    twill = ((xx + yy) % 6) < 3
    dirt = fbm(56, 768, 2, 24, 3, True)
    lum = np.where(twill, 1.0, 0.93) * (0.97 + 0.03 * dirt) + 0.02 * pix(56, 768)
    c = lum[..., None] * np.array([0.88, 0.86, 0.78], np.float32)
    h = np.where(twill, 0.56, 0.46) + 0.03 * dirt
    edge = np.minimum(yy, 55 - yy)
    c = np.where((edge < 2)[..., None], c * 0.82, c)              # folded edges
    h = np.where(edge < 2, 0.35, h)
    r = np.full((56, 768), 0.85, np.float32)
    for row in (5, 49):                                           # sewing lines
        on = (np.arange(768) % 7) < 4
        c[row:row + 1, on] *= 0.82
        h[row:row + 1, on] = 0.62
        h[row:row + 1, ~on] = 0.40
    put(0, 612, c, h, r)

    # ------------------------------------------------------------ pompom: white wool, black centre (front/back disc)
    rad, ang = polar(192, 96, 96)
    q = rad / 90.0
    wool = fbm(192, 192, 24, 24, 3)
    fuzz = pix(192, 192)
    edge_r = 0.42 + 0.05 * fbm(192, 192, 6, 6, 2)
    white = np.array([0.88, 0.87, 0.84], np.float32) * (0.86 + 0.10 * wool + 0.10 * fuzz)[..., None]
    black = (0.035 + 0.02 * wool + 0.02 * fuzz)[..., None] * np.ones(3, np.float32)
    c = np.where((q < edge_r)[..., None], black, white)
    h = 0.5 + 0.30 * wool + 0.25 * fuzz
    put(0, 680, c, h, np.full((192, 192), 0.95, np.float32))


# ---------------------------------------------------------------- write files
def save(arr_rgb, name):
    img = bpy.data.images.new(name, S, S, alpha=False)
    rgba = np.concatenate([np.clip(arr_rgb, 0, 1)[::-1], np.ones((S, S, 1), np.float32)], axis=2)
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = 'PNG'
    path = os.path.join(OUT_DIR, name)
    try:
        img.save(filepath=path)
    except TypeError:
        img.filepath_raw = path
        img.save()
    print("OK", path)

os.makedirs(OUT_DIR, exist_ok=True)
save(co, "hcl_shako_prussline1813_co.png")

k = 3.0
gy, gx = np.gradient(hgt)                     # gy: down the rows, gx: along the columns
n = np.dstack([-gx * k, gy * k, np.ones_like(hgt)])   # +Y up (rows go down, so the sign flips)
n /= np.linalg.norm(n, axis=2, keepdims=True)
save(n * 0.5 + 0.5, "hcl_shako_prussline1813_nohq.png")
save(np.repeat(np.clip(rough, 0, 1)[..., None], 3, axis=2), "hcl_shako_prussline1813_rough_preview.png")
