# Blender headless: composes the 1024x1024 shako colour texture from regions of the NTW prussia1813_01 atlas.
# Usage: blender -b --factory-startup --python compose_shako_texture.py -- <prussia1813_01_diffuse.dds> <out_co.png>
# Personal-use project: the output contains third-party pixels (see docs/source_inventory.md).
import bpy, sys, os
import numpy as np

args = sys.argv[sys.argv.index("--") + 1:]
ATLAS, OUT = args[0], args[1]
SIZE = 1024

# Source regions in atlas pixels (x, y, w, h), top-left origin. Measured on a full-resolution crop.
FELT = (80, 2742, 304, 98)        # black felt with vertical folds
BAND = (330, 2872, 430, 60)       # dark leather band (no cipher)
BAND_INNER = (330, 2884, 430, 36)  # band without its light edges, tiled for the visor
TOP = (5, 2556, 120, 120)         # round leather crown
LOOP_SILVER = (388, 2672, 104, 172)  # cockade rosette + white-metal loop
LOOP_BRASS = (774, 2672, 104, 172)   # same, brass (variant)
EAGLE = (492, 2702, 130, 142)        # brass eagle plate (variant)
STAR = (628, 2702, 134, 142)         # guard star (variant)


def load_rgb(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()   # flip to top-left origin


def region(src, r):
    x, y, w, h = r
    return src[y:y + h, x:x + w]


def resize(img, nw, nh):
    h, w, _ = img.shape
    xs = (np.arange(nw) + 0.5) * w / nw - 0.5
    ys = (np.arange(nh) + 0.5) * h / nh - 0.5
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 1); x1 = np.clip(x0 + 1, 0, w - 1)
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 1); y1 = np.clip(y0 + 1, 0, h - 1)
    fx = np.clip(xs - np.floor(xs), 0, 1)[None, :, None]
    fy = np.clip(ys - np.floor(ys), 0, 1)[:, None, None]
    top = img[y0][:, x0] * (1 - fx) + img[y0][:, x1] * fx
    bot = img[y1][:, x0] * (1 - fx) + img[y1][:, x1] * fx
    return top * (1 - fy) + bot * fy


def mirror_tile(img, W, H, vertical=True):
    h, w, _ = img.shape
    strip = np.concatenate([img if k % 2 == 0 else img[:, ::-1] for k in range(W // w + 2)], axis=1)
    rows = [strip if (k % 2 == 0 or not vertical) else strip[::-1] for k in range(H // h + 2)]
    return np.concatenate(rows, axis=0)[:H, :W]


def paste(dst, img, x, y):
    h, w, _ = img.shape
    dst[y:y + h, x:x + w] = img


atlas = load_rgb(ATLAS)
out = np.zeros((SIZE, SIZE, 3), dtype=np.float32)

felt = resize(region(atlas, FELT), 456, 147)
band = region(atlas, BAND)

paste(out, mirror_tile(felt, 1024, 288), 0, 0)                                   # body felt
paste(out, mirror_tile(resize(band, 344, 48), 1024, 48, vertical=False), 0, 288)  # bottom band
paste(out, resize(region(atlas, TOP), 256, 256), 0, 352)                          # crown
paste(out, mirror_tile(felt, 256, 256) * 0.45, 256, 352)                          # inside (darkened felt)
paste(out, mirror_tile(region(atlas, BAND_INNER), 256, 256), 512, 352)            # visor leather
paste(out, resize(region(atlas, LOOP_SILVER), 156, 258), 784, 352)                # cockade + loop (used)
paste(out, resize(region(atlas, EAGLE), 195, 213), 0, 640)                        # variant: eagle
paste(out, resize(region(atlas, STAR), 201, 213), 256, 640)                       # variant: star
paste(out, resize(region(atlas, LOOP_BRASS), 156, 258), 512, 640)                 # variant: brass loop

rgba = np.concatenate([out[::-1], np.ones((SIZE, SIZE, 1), dtype=np.float32)], axis=2)
img = bpy.data.images.new("shako_co", SIZE, SIZE, alpha=False)
img.pixels.foreach_set(rgba.ravel())
scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save_render(OUT, scene=scene)
print("OK texture", OUT)
