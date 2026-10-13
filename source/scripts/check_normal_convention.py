# Read-only: determines the tangent-space Y convention of a normal map that also stores its height field in alpha
# (e.g. Arma 3 Samples Art\TemplateNormalMap\displaceTest_middle_nopx.tga).
# Correlates the red/green channels with the height gradient:
#   OpenGL (+Y up):   corr(G, dh/d_row) > 0   (rows grow downwards)
#   DirectX (+Y down): corr(G, dh/d_row) < 0
# Sanity check: corr(R, dh/d_col) should be negative in both conventions.
# Usage: blender -b --factory-startup --python check_normal_convention.py -- <image_with_height_in_alpha>
import bpy, sys
import numpy as np

img = bpy.data.images.load(sys.argv[sys.argv.index("--") + 1])
w, h = img.size
px = np.empty(w * h * 4, np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[::-1]                       # top-left origin
r, g, a = px[..., 0] - 0.5, px[..., 1] - 0.5, px[..., 3]
dh_row, dh_col = np.gradient(a)
mask = (np.abs(dh_row) + np.abs(dh_col)) > 1e-4     # only where the height actually changes

def corr(x, y):
    x, y = x[mask], y[mask]
    return float(np.corrcoef(x, y)[0, 1])

print(f"SIZE {w}x{h} channels=RGBA alpha_range=({a.min():.3f},{a.max():.3f}) informative_px={int(mask.sum())}")
print(f"CORR R vs dh/dcol = {corr(r, dh_col):+.3f}  (expected negative)")
print(f"CORR G vs dh/drow = {corr(g, dh_row):+.3f}  (positive = OpenGL/+Y up, negative = DirectX/+Y down)")
