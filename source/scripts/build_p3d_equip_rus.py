# Builds the editable P3D models (MLOD) of the Russian 1812 crossbelts (vest) and knapsack (backpack) for the test
# addon hcl_rus (pendency RU10, dossier docs/research/rus/HIST-RUS-INF-EQUIP-1812-001.md). Same method as the British
# vest and knapsack in build_p3d_uk.py (left untouched): the French production meshes (build_equipamento_producao.py
# nacao=fr) with their approved weights (source/models/pesos/hcl_fr_pesos.blend), Russian textures
# (generate_equipment_textures_rus.py). The knapsack loses the greatcoat roll (capote* parts, dossier E8), exactly the
# faces the painter deletes. No Samples on this machine: the French P3Ds stand in for the official vest template (their
# Res 1 properties and empty Geometry LOD are the template's).
#   blender -b --factory-startup --python build_p3d_equip_rus.py -- <project root>
# Writes source/addon/hcl/hcl_rus/{hcl_v_rus1812_correame,hcl_b_rus1812_mochila}.p3d, their .rvmat in data/ and
# build_p3d_equip_rus_log.txt.
import bpy, bmesh, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod_io import parse
from p3d_build_common import append, lod_from_mesh, finish, props_of, save

ROOT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0])
OUT = os.path.join(ROOT, r"source\addon\hcl\hcl_rus")
DATA = r"hcl\hcl_rus\data"
PES = os.path.join(ROOT, r"source\models\pesos\hcl_fr_pesos.blend")
ROLL_PARTS = ("capote", "capote_correia", "capote_fivela", "capote_ponta")     # same list as the painter
LOG = []
bpy.ops.wm.read_factory_settings(use_empty=True)


def log(s):
    print(s); LOG.append(s)


# the project's equipment .rvmat (hcl_v_uk1812_correame.rvmat): Super shader, nohq + smdi of the item
RVMAT = open(os.path.join(ROOT, r"source\addon\hcl\hcl_uk\data\hcl_v_uk1812_correame.rvmat"), encoding="utf-8").read()

ITEMS = [("HCL_V_Fr1812_Correame_LOD0", "hcl_v_rus1812_correame", r"source\addon\hcl\hcl_fr\hcl_v_fr1812_correame.p3d"),
         ("HCL_B_Fr1812_Havresac_LOD0", "hcl_b_rus1812_mochila", r"source\addon\hcl\hcl_fr\hcl_b_fr1812_havresac.p3d")]
objs = {o.name: o for o in append(PES, [n for n, _, _ in ITEMS])}
for ob_name, base, tpl_path in ITEMS:
    o = objs[ob_name]
    if base.startswith("hcl_b_"):
        parts = o["hcl_partes"].split(",")
        kill = {i for i, n in enumerate(parts) if n in ROLL_PARTS}
        bm = bmesh.new(); bm.from_mesh(o.data)
        lay = bm.faces.layers.int.get("hcl_part")
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] in kill], context="FACES")
        bm.to_mesh(o.data); bm.free()
        log(f"{base}: greatcoat roll removed ({', '.join(ROLL_PARTS)}), {len(o.data.polygons)} faces left")
    o.data.uv_layers.active = o.data.uv_layers["UVMap"]
    tpl = parse(os.path.join(ROOT, tpl_path))
    allp = {p.index for p in o.data.polygons}
    tx = (DATA + "\\" + base + "_co.paa", DATA + "\\" + base + ".rvmat")
    Lr = lod_from_mesh(o, 1.0, props_of(tpl["lods"][0]), lambda pi, tx=tx: tx, {"camo": allp})
    bones = sorted(n for n in Lr["sels"] if n != "camo")
    log(f"{base}: Res 1 {len(Lr['faces'])} triangles, {len(Lr['points'])} points; bones {bones}")
    lods = [finish(Lr)] + [x for x in tpl["lods"] if x["res"] > 1e12]          # Res 1 + empty Geometry
    save({"version": tpl["version"], "lods": lods, "tail": tpl.get("tail", b"")}, os.path.join(OUT, base + ".p3d"), log)
    rv = RVMAT.replace(r"hcl\hcl_uk\data\hcl_v_uk1812_correame", DATA + "\\" + base)
    open(os.path.join(OUT, "data", base + ".rvmat"), "w", encoding="utf-8").write(rv)
    log(f"{base}.rvmat written")

open(os.path.join(OUT, "build_p3d_equip_rus_log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
