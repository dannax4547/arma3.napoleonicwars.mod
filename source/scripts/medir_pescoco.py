# Measures the official body's neck (A3_character_example.p3d, faces up to the head junction at 1.580 m, where the
# game's head proxy takes over) and the collar's inner wall at the same heights: neck centre (y), half-width and
# half-depth per height, and the clearance between the collar's inner wall and the neck in 8 directions.
#   blender -b --factory-startup --python medir_pescoco.py -- <Samples Test_Character_01 dir> <uniform LOD0 .blend>
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
TC, UNI = a[:2]
GROUND = -1.0069
ex = read_mlod(os.path.join(TC, "A3_character_example.p3d"))[0]
P = [Vector(to_blender(p)) for p in ex["points"]]
F = [list(dict.fromkeys(f)) for f in ex["faces"] if len(set(f)) >= 3]
nb = BVHTree.FromPolygons(P, F)                     # whole body: rays leave the neck axis, first hit = neck skin
with bpy.data.libraries.load(UNI, link=False) as (src, dst):
    dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
uni = dst.objects[0]
parts = uni["hcl_partes"].split(",")
bm = bmesh.new(); bm.from_mesh(uni.data)
PL = bm.faces.layers.int.get("hcl_part")
gf = [[v.index for v in f.verts] for f in bm.faces if f[PL] == parts.index("gola")]
gb = BVHTree.FromPolygons([v.co.copy() for v in bm.verts], gf)
DIRS = [("frente", 0), ("frente-esq", 45), ("esq", 90), ("tras-esq", 135), ("tras", 180), ("tras-dir", 225), ("dir", 270),
        ("frente-dir", 315)]


def ring(bvh, h, c, from_out=True):
    out = []
    for k in range(64):
        th = 2 * math.pi * k / 64
        d = Vector((math.sin(th), -math.cos(th), 0))
        o = Vector((c.x, c.y, GROUND + h))
        hit = bvh.ray_cast(o + d * 0.25, -d, 0.25) if from_out else bvh.ray_cast(o, d, 0.25)
        out.append(hit[0])
    return out


print("PESCOCO do corpo oficial (A3_character_example) e folga da parede interna da gola (mm)")
print("  altura  centro_y  meia_larg  meia_prof | " + " ".join(f"{n:>10s}" for n, _ in DIRS))
c = Vector((0, 0.0, 0))
for h in [1.45, 1.48, 1.50, 1.52, 1.535, 1.55, 1.56, 1.57, 1.58]:
    sk = ring(nb, h, c, from_out=False)
    ok = [p for p in sk if p is not None]
    if len(ok) < 48:
        print(f"  {h:.3f}: pescoco com {64 - len(ok)} direcoes sem superficie")
        continue
    A = np.array([p[:] for p in ok])
    cy = (A[:, 1].max() + A[:, 1].min()) / 2
    c = Vector((0, cy, 0))
    sk = ring(nb, h, c, from_out=False)
    wl = ring(gb, h, c, from_out=False)                      # first hit from the axis outward = collar inner wall
    cols = []
    for n, deg in DIRS:
        k = int(round(deg / 360 * 64)) % 64
        d = Vector((math.sin(2 * math.pi * k / 64), -math.cos(2 * math.pi * k / 64), 0))
        if sk[k] is None or wl[k] is None:
            cols.append("       ---"); continue
        gap = ((wl[k] - Vector((c.x, c.y, wl[k].z))).dot(d) - (sk[k] - Vector((c.x, c.y, sk[k].z))).dot(d)) * 1000
        cols.append(f"{gap:10.1f}")
    print(f"  {h:.3f}   {cy:+.4f}    {(A[:, 0].max() - A[:, 0].min()) / 2 * 1000:6.1f}     {(A[:, 1].max() - A[:, 1].min()) / 2 * 1000:6.1f}  | "
          + " ".join(cols))
