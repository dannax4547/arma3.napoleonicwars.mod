# Production plumes for the Prussian shakos (Phases 4 + 6), from the blockout blockout_plumet_pruss.py (spec
# docs/specs/variantes_regimentos_pruss.md section 9.2; user decision 2026-10-12: "Plumet verde" and "Stutz da Guarda"):
#   verde : dark green plumet of the mod art (prussia1813_01 c5-c6 r5, 🎮), 0.30 m, on the FWR, eagle and star shakos
#           (unit probably the volunteer Jäger, 🔶);
#   stutz : Garde zu Fuss, short tall brush, white above black (order assumed, 🔶), 0.22 m, on the star shako.
# Each plume is a separate object (brass socket "tulipa" + feathered column of plumet.py v3) in character space, placed
# at the top front of its shako behind the cockade, exactly as in the blockout. It carries its own small texture set
# (hcl_plumet_pruss_{co,nohq,smdi}.png, 1024 px): feather tiles (barbs, shaft, darker edges; 3 shades per colour picked
# by each feather's "tint"), a brass tile for the socket and a dark tile for the hidden core. The game model is the
# shako (selection "camo", its texture swappable) + the plume (fixed texture), built by build_p3d_pruss.py.
#   blender -b --factory-startup --python build_plumet_pruss.py -- <project root> <img dir>
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plumet import plumet

ROOT, IMG = [os.path.abspath(a) for a in sys.argv[sys.argv.index("--") + 1:][:2]]
os.makedirs(IMG, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
SH = os.path.join(ROOT, r"source\models\shakos\hcl_shako_pruss")
OUT_BLEND = os.path.join(SH, r"variantes\hcl_plumet_pruss.blend")
TEX = os.path.join(ROOT, r"source\textures\hcl_shako_pruss")
SRC = {"fwr": os.path.join(SH, "hcl_shako_pruss_LOD0.blend"),
       "aguia": os.path.join(SH, r"variantes\hcl_shako_pruss_aguia_LOD0.blend"),
       "estrela": os.path.join(SH, r"variantes\hcl_shako_pruss_estrela_LOD0.blend")}
PLUMES = [("fwr", "verde"), ("aguia", "verde"), ("estrela", "verde"), ("estrela", "stutz")]
RES = 1024
TILE = 0.25                                        # 4 x 4 tiles
# tiles: verde 0-2, preto 3-5, branco 6-8 (3 shades each), 9 brass socket, 10.. cores (flat)
TILES = [((i % 4) * TILE, (i // 4) * TILE) for i in range(16)]
FEATHER_TILE = {"verde": 0, "preto": 3, "branco": 6}
BRASS_TILE = 9
SHADES = (0.82, 1.0, 1.15)
PENA = {"verde": (0.035, 0.17, 0.06), "preto": (0.025, 0.025, 0.025), "branco": (0.90, 0.90, 0.86)}   # linear
BRASS = (0.62, 0.44, 0.15)
SMDI_PENA, SMDI_LATAO = (0.08, 0.25), (0.85, 0.72)


def tile_uv(ti, u, v, pad=0.02):
    ox, oy = TILES[ti]
    return (ox + TILE * (pad + (1 - 2 * pad) * min(max(u, 0), 1)), oy + TILE * (pad + (1 - 2 * pad) * min(max(v, 0), 1)))


def load_shako(key):
    with bpy.data.libraries.load(SRC[key], link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n == "HCL_Shako_Pruss_LOD0"]
    o = dst.objects[0]
    o.name = f"shako_{key}"
    scene.collection.objects.link(o)
    return o


def build(key, var, shako):
    # build_p3d_pruss.py writes the shako's mesh coordinates as they are: they must already be character space
    assert all(abs(shako.matrix_world[i][j] - (1.0 if i == j else 0.0)) < 1e-9 for i in range(4) for j in range(4)), shako.matrix_world
    V = np.array([v.co[:] for v in shako.data.vertices])
    ztop = V[:, 2].max()
    near = V[(V[:, 2] > ztop - 0.012) & (np.abs(V[:, 0]) < 0.012)]
    y_front = near[:, 1].min()
    base = Vector((0.0, y_front + 0.012, ztop - 0.012))                # as in blockout_plumet_pruss.py
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.verify()
    # socket ("tulipa"): turned brass cup, UV = cylinder around it in the brass tile
    seg = 16
    prof = [(0.0, 0.004), (0.006, 0.0048), (0.012, 0.006), (0.018, 0.0078), (0.024, 0.010), (0.025, 0.0085)]
    rows = [[bm.verts.new(base + Vector((r * math.cos(2 * math.pi * s / seg), r * math.sin(2 * math.pi * s / seg), a))) for s in range(seg)] for a, r in prof]
    for j in range(len(rows) - 1):
        for i in range(seg):
            f = bm.faces.new((rows[j][i], rows[j][(i + 1) % seg], rows[j + 1][(i + 1) % seg], rows[j + 1][i]))
            f.smooth = True
            for l, (uu, vv) in zip(f.loops, ((i / seg, j / 5), ((i + 1) / seg, j / 5), ((i + 1) / seg, (j + 1) / 5), (i / seg, (j + 1) / 5))):
                l[uvl].uv = tile_uv(BRASS_TILE, uu, vv)
    c = bm.verts.new(base)
    for i in range(seg):
        f = bm.faces.new((c, rows[0][(i + 1) % seg], rows[0][i]))
        for l in f.loops:
            l[uvl].uv = tile_uv(BRASS_TILE, 0.5, 0.0)
    n_socket = len(bm.faces)
    pb = base + Vector((0, 0, 0.024))
    if var == "stutz":
        by = plumet(bm, pb, H=0.22, colours=[(0.0, "preto"), (0.5, "branco")], shape="stutz", seed=7)
    else:
        by = plumet(bm, pb, H=0.30, colours=[(0.0, "verde")], seed=3 + list(SRC).index(key))
    tint = bm.faces.layers.float.get("tint")
    for nm, faces in by.items():
        for f in faces:
            sh = min(2, int(f[tint] * 3))
            core = f[tint] == 0.25 and all(l[uvl].uv.length < 1e-9 for l in f.loops)
            for l in f.loops:
                u, v = (0.5, 0.15) if core else l[uvl].uv
                l[uvl].uv = tile_uv(FEATHER_TILE[nm] + (0 if core else sh), u, v)
    me = bpy.data.meshes.new(f"HCL_Plumet_Pruss_{key}_{var}")
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(me.name, me)
    scene.collection.objects.link(ob)
    ob["hcl_shako"] = key
    ob["hcl_base"] = list(base)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    top = max(v.co.z for v in me.vertices)
    print(f"PLUMET {key}/{var}: base ({base.x:+.3f}, {base.y:+.3f}, {base.z:.3f}); topo {top:.3f} m; "
          f"{tris} triangulos ({n_socket} faces da tulipa)")
    return ob


# ---------------------------------------------------------------- texture atlas (numpy, same painter as the French shakos)
def paint_feather_tile(co, nr, sm, ti, rgb, shade):
    n = int(TILE * RES)
    x0, y0 = int(TILES[ti][0] * RES), int(TILES[ti][1] * RES)
    v, u = np.mgrid[0:n, 0:n] / (n - 1.0)
    du = np.abs(u - 0.5)
    rng = np.random.default_rng(int(1000 * shade) + int(255 * rgb[0]) + ti)
    barbs01 = 0.5 + 0.5 * np.sin(du * 140 - v * 70 + 0.6 * rng.standard_normal((n, n)).cumsum(axis=1) / n * 8)
    shaft = (du < 0.03).astype(np.float32)
    edge = np.clip((du - 0.36) / 0.14, 0, 1)
    f = (0.70 + 0.30 * barbs01 + 0.06 * rng.standard_normal((n, n))) * shade * (1 - 0.25 * shaft) * (1 - 0.30 * edge)
    f *= 0.85 + 0.15 * v
    co[y0:y0 + n, x0:x0 + n, :3] = np.clip(np.array(rgb)[None, None, :] * f[..., None], 0, 1)
    h = 0.6 * barbs01 - 0.8 * shaft - 0.3 * edge
    gy, gx = np.gradient(h)
    nv = np.dstack([-gx * 6, -gy * 6, np.ones_like(h)]); nv /= np.linalg.norm(nv, axis=2, keepdims=True)
    nr[y0:y0 + n, x0:x0 + n, :3] = nv * 0.5 + 0.5
    sm[y0:y0 + n, x0:x0 + n, :3] = (1.0, *SMDI_PENA)


def paint_brass_tile(co, nr, sm, ti):
    n = int(TILE * RES)
    x0, y0 = int(TILES[ti][0] * RES), int(TILES[ti][1] * RES)
    rng = np.random.default_rng(9)
    v, u = np.mgrid[0:n, 0:n] / (n - 1.0)
    tarn = np.clip(0.5 + 0.5 * np.sin(u * 37 + 3 * np.sin(v * 11)) * 0.3 + 0.05 * rng.standard_normal((n, n)), 0, 1)
    lathe_rings = 0.04 * np.sin(v * 900)
    f = 0.75 + 0.35 * tarn + lathe_rings
    co[y0:y0 + n, x0:x0 + n, :3] = np.clip(np.array(BRASS)[None, None, :] * f[..., None], 0, 1)
    gy, gx = np.gradient(lathe_rings * 3)
    nv = np.dstack([-gx, -gy, np.ones_like(f)]); nv /= np.linalg.norm(nv, axis=2, keepdims=True)
    nr[y0:y0 + n, x0:x0 + n, :3] = nv * 0.5 + 0.5
    sm[y0:y0 + n, x0:x0 + n, :3] = (1.0, *SMDI_LATAO)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


CO = np.zeros((RES, RES, 4), np.float32); CO[..., 3] = 1
NR = np.zeros_like(CO); NR[..., :] = (0.5, 0.5, 1.0, 1.0)
SM = np.zeros_like(CO); SM[..., :] = (1.0, 0.05, 0.1, 1.0)
for nm, t0 in FEATHER_TILE.items():
    for s in range(3):
        paint_feather_tile(CO, NR, SM, t0 + s, PENA[nm], SHADES[s])
paint_brass_tile(CO, NR, SM, BRASS_TILE)
CO[..., :3] = to_srgb(CO[..., :3])                    # palette is linear; PNG bytes are sRGB
os.makedirs(TEX, exist_ok=True)
for data, suffix, cs in ((CO, "co", "sRGB"), (NR, "nohq", "Non-Color"), (SM, "smdi", "Non-Color")):
    im = bpy.data.images.new(f"hcl_plumet_pruss_{suffix}", RES, RES, alpha=False)
    im.colorspace_settings.name = cs
    im.pixels.foreach_set(data.ravel())
    im.filepath_raw = os.path.join(TEX, f"hcl_plumet_pruss_{suffix}.png"); im.file_format = "PNG"; im.save()
    print("textura", im.filepath_raw)

# ---------------------------------------------------------------- meshes
shakos = {k: load_shako(k) for k in SRC}
plumes = [build(k, v, shakos[k]) for k, v in PLUMES]
mat = bpy.data.materials.new("TEX_hcl_plumet_pruss"); mat.use_nodes = True
nt = mat.node_tree; b = nt.nodes["Principled BSDF"]
t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, "hcl_plumet_pruss_co.png"))
nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(os.path.join(TEX, "hcl_plumet_pruss_nohq.png"))
tn.image.colorspace_settings.name = "Non-Color"
nm_ = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tn.outputs["Color"], nm_.inputs["Color"])
nt.links.new(nm_.outputs["Normal"], b.inputs["Normal"])
b.inputs["Roughness"].default_value = 0.75
for p in plumes:
    p.data.materials.append(mat)
for k, o in shakos.items():                         # keep the shakos out of the saved file (they live in their blends)
    bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("saved", OUT_BLEND)
