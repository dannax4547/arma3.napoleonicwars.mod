# Blender headless (read-only): horizontal slices of one LOD of an MLOD P3D, in Blender axes (Z up, front -Y).
# Usage: blender -b --factory-startup --python slice_p3d.py -- <file.p3d> <lod_index> <step_m>
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

args = sys.argv[sys.argv.index("--") + 1:]
lod = read_mlod(args[0])[int(args[1])]
step = float(args[2])
pts = [to_blender(p) for p in lod["points"]]
zmin, zmax = min(p[2] for p in pts), max(p[2] for p in pts)
print(f"SLICES {os.path.basename(args[0])} LOD{args[1]} points={len(pts)} z[{zmin:.3f},{zmax:.3f}]")
z = zmin
while z < zmax + 1e-9:
    s = [p for p in pts if z <= p[2] < z + step]
    if s:
        xs, ys = [p[0] for p in s], [p[1] for p in s]
        print(f"SLICE z[{z:.3f},{z + step:.3f}) n={len(s):3d} x[{min(xs):.3f},{max(xs):.3f}] w={max(xs) - min(xs):.3f}  "
              f"y[{min(ys):.3f},{max(ys):.3f}] d={max(ys) - min(ys):.3f}")
    z += step
