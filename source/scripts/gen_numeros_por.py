# Number band textures of the Portuguese stovepipes (docs/specs/portugal_1812.md 3.1; blockout_shako_uk.py conjunto=por,
# part "numfaixa"): a brass strip with the regimental / battalion number struck in, one 1024 x 128 PNG per unit:
#   hcl_por_numero_l01_co.png .. l24 (line)   hcl_por_numero_c01_co.png .. c12 (Cacadores)
# build_p3d_uk.py maps the band's faces to this texture keeping the band's real aspect (u spans the band width over
# 8 x its height, centred), so the digits are not stretched; the config sets it per cap class in the hidden selection
# "numero". Rendered here (no PIL in Blender's Python): emission-only plane + text, orthographic camera.
#   blender -b --factory-startup --python gen_numeros_por.py -- <out dir>
import bpy, sys, os, math

out_dir = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
CONJ = dict(x.split("=", 1) for x in sys.argv[sys.argv.index("--") + 2:] if "=" in x).get("conjunto", "por")
# conjunto=bru: Brunswick line battalions 1-3, number in white metal (kgl_brunswick_1815.md 4): hcl_bru_numero_b1..b3
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 16; sc.cycles.device = "CPU"
sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y = 1024, 128
sc.render.film_transparent = False
w = bpy.data.worlds.new("w"); w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1); sc.world = w
BRASS, DARK, EDGE = (0.62, 0.44, 0.15), (0.13, 0.08, 0.03), (0.45, 0.31, 0.10)
if CONJ == "bru":                                    # white metal (tin-plated), dark grey numbers
    BRASS, DARK, EDGE = (0.62, 0.62, 0.60), (0.10, 0.10, 0.11), (0.42, 0.42, 0.41)


def emit(name, rgb, noise=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = 1.0
    if noise:                                           # tarnish: brass x (1 - noise .. 1 + noise)
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 18.0; nz.inputs["Detail"].default_value = 6.0
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 1 - noise
        mr.inputs["To Max"].default_value = 1 + noise
        rgbn = nt.nodes.new("ShaderNodeRGB"); rgbn.outputs[0].default_value = (*rgb, 1)
        vm = nt.nodes.new("ShaderNodeVectorMath", ); vm.operation = "SCALE"
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        nt.links.new(rgbn.outputs[0], vm.inputs[0]); nt.links.new(mr.outputs["Result"], vm.inputs["Scale"])
        nt.links.new(vm.outputs["Vector"], e.inputs["Color"])
    else:
        e.inputs["Color"].default_value = (*rgb, 1)
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def plane(name, w_, h_, z, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, z))
    p = bpy.context.object; p.name = name; p.scale = (w_, h_, 1); p.data.materials.append(mat)
    return p


plane("latao", 8.0, 1.0, 0.0, emit("brass", BRASS, 0.12))
plane("borda_a", 8.0, 0.06, 0.001, emit("edge", EDGE)).location.y = 0.47
plane("borda_b", 8.0, 0.06, 0.001, emit("edge2", EDGE)).location.y = -0.47
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 8.0; cam.location = (0, 0, 5)
dark = emit("dark", DARK)
cu = bpy.data.curves.new("txt", "FONT"); cu.size = 0.72; cu.align_x = "CENTER"; cu.align_y = "CENTER"
txt = bpy.data.objects.new("txt", cu); sc.collection.objects.link(txt); txt.location.z = 0.002
cu.materials.append(dark)
jobs = [(f"l{n:02d}", str(n)) for n in range(1, 25)] + [(f"c{n:02d}", str(n)) for n in range(1, 13)]
PFX = "hcl_por_numero"
if CONJ == "bru":
    jobs, PFX = [(f"b{n}", str(n)) for n in range(1, 4)], "hcl_bru_numero"
for key, text in jobs:
    cu.body = text
    sc.render.filepath = os.path.join(out_dir, f"{PFX}_{key}_co.png")
    bpy.ops.render.render(write_still=True)
print(f"OK {len(jobs)} texturas de numero em {out_dir}")
