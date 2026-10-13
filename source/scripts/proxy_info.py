# Read-only: prints the proxy triangles of an MLOD LOD (points in P3D and Blender axes, edge lengths).
#   python proxy_info.py <file.p3d> [lod_index]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

path = sys.argv[1]
li = int(sys.argv[2]) if len(sys.argv) > 2 else 0
lod = read_mlod(path)[li]
P = lod["points"]
for name, blob in lod["selections"].items():
    if not name.lower().startswith("proxy:"):
        continue
    idx = [i for i, b in enumerate(blob) if b]
    face = next((f for f in lod["faces"] if set(f) == set(idx)), None)
    order = face if face else idx
    pts = [P[i] for i in order]
    d = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
    print(name)
    for k, i in enumerate(order):
        print(f"   v{k} P3D {tuple(round(c, 4) for c in P[i])}  Blender {tuple(round(c, 4) for c in to_blender(P[i]))}")
    print(f"   edges v0-v1 {d(pts[0], pts[1]):.3f}  v0-v2 {d(pts[0], pts[2]):.3f}  v1-v2 {d(pts[1], pts[2]):.3f}")
