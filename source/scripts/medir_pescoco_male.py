# Neck of the official animation template body (Arma 3 Samples TemplateRTM\Male.p3d, full body with head): cross-
# section per height measured with rays from the neck axis outward (first hit = neck skin), axis re-centred at every
# height. Writes the sections as JSON (centre x/y, radius per direction) for the collar rebuild, and prints the
# clearance of the current collar's inner wall in 8 directions.
#   blender -b --factory-startup --python medir_pescoco_male.py -- <Samples dir> <uniform LOD0 .blend> <out .json>
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod, to_blender

a = sys.argv[sys.argv.index("--") + 1:]
SAMPLES, UNI, OUTJ = a[:3]
GROUND = -1.0069
male = read_mlod(os.path.join(SAMPLES, r"Addons\TemplateRTM\Male.p3d"))[0]
P = [Vector(to_blender(p)) for p in male["points"]]
F = [list(dict.fromkeys(f)) for f in male["faces"] if len(set(f)) >= 3]
mb = BVHTree.FromPolygons(P, F)
with bpy.data.libraries.load(UNI, link=False) as (src, dst):
    dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
uni = dst.objects[0]
parts = uni["hcl_partes"].split(",")
bm = bmesh.new(); bm.from_mesh(uni.data)
PL = bm.faces.layers.int.get("hcl_part")
gf = [[v.index for v in f.verts] for f in bm.faces if f[PL] == parts.index("gola")]
gb = BVHTree.FromPolygons([v.co.copy() for v in bm.verts], gf)
NDIR = 64


def ring(bvh, h, c, rmax=0.20):
    out = []
    for k in range(NDIR):
        th = 2 * math.pi * k / NDIR
        d = Vector((math.sin(th), -math.cos(th), 0))
        hit = bvh.ray_cast(Vector((c.x, c.y, GROUND + h)), d, rmax)
        out.append(None if hit[0] is None else (hit[0] - Vector((c.x, c.y, GROUND + h))).length)
    return out


DIRS = [("frente", 0), ("fr-esq", 8), ("esq", 16), ("tr-esq", 24), ("tras", 32), ("tr-dir", 40), ("dir", 48), ("fr-dir", 56)]
c = Vector((0.0, 0.04, 0))
sections = []
print("PESCOCO Male.p3d (raios do eixo para fora) e folga da parede interna da gola atual (mm)")
print("  altura  cx      cy     larg  prof | " + " ".join(f"{n:>7s}" for n, _ in DIRS))
for h in np.round(np.arange(1.48, 1.665, 0.01), 3):
    for _ in range(4):                                       # re-centre on the section
        r = ring(mb, h, c)
        if sum(x is None for x in r) > 4:
            break
        pts = [Vector((c.x + r[k] * math.sin(2 * math.pi * k / NDIR), c.y - r[k] * math.cos(2 * math.pi * k / NDIR), 0))
               for k in range(NDIR) if r[k] is not None]
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        c = Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0))
    r = ring(mb, h, c)
    if sum(x is None for x in r) > 4:
        print(f"  {h:.3f}: sem secao fechada")
        continue
    wl = ring(gb, h, c, rmax=0.25)
    hw = (max(r[k] for k in (16,)) + max(r[k] for k in (48,)))
    sections.append({"h": float(h), "cx": c.x, "cy": c.y, "r": [float(x) if x is not None else None for x in r]})
    cols = []
    for n, k in DIRS:
        cols.append("    ---" if (wl[k] is None or r[k] is None) else f"{(wl[k] - r[k]) * 1000:7.1f}")
    print(f"  {h:.3f} {c.x:+.3f} {c.y:+.4f} {(r[16] + r[48]) * 1000:5.0f} {(r[0] + r[32]) * 1000:5.0f} | " + " ".join(cols))
json.dump({"fonte": "Arma 3 Samples TemplateRTM\\Male.p3d", "ndir": NDIR, "theta0": "frente (-Y), sentido +X", "secoes": sections},
          open(OUTJ, "w"), indent=1)
print("JSON", OUTJ, len(sections), "secoes")
