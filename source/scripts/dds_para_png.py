# Read-only conversion of mod reference textures (.dds) to PNG, for contact sheets and tile crops.
# The source .dds is only read; the PNG goes to the given output path.
#   blender -b --factory-startup --python dds_para_png.py -- <in.dds> <out.png> [<in2.dds> <out2.png> ...]
import os
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
assert args and len(args) % 2 == 0, "pares <in.dds> <out.png>"
for src, dst in zip(args[0::2], args[1::2]):
    src, dst = os.path.abspath(src), os.path.abspath(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img = bpy.data.images.load(src)
    _ = img.pixels[0]  # forces the DDS to load; save() alone reports "no image data"
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    img.save_render(dst)
    print("OK", img.size[0], img.size[1], dst)
    bpy.data.images.remove(img)
