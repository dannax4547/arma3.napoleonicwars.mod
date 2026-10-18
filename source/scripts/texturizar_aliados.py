# COPY of texturizar_shako_fr.py for the French allies (2026-10-18). One addition: atlas=<png> replaces the French mod
# atlas (FranceINF_diffuse.png) as the source of the kind "arte" (traced plates, art discs), e.g. the Polish infantry
# atlas polandINF_diffuse.png for the czapka's plate, eagle and star boss; arte_faixa=<lo>,<hi> sets the luminance range of
# that art in LINEAR values (default 0.05,0.45 as the French brass; the dark polandINF filigree needs 0.005,0.045).
# Everything else is unchanged.
# Original description:
# Textures (Phase 6 style) for the French line infantry shakos of the blockout (blockout_shako_fr.py): every variant's
# parts are joined into one mesh in character space (on the head at x = 0), get an atlas UV and baked textures:
#   felt body (fine fibres, uneven nap), black leather bands and chevrons (grain), wool lace bands and chevrons of the
#   elite companies (weave), gold rank lace of the officers, patent-leather visor (gloss), brass plate / tulip /
#   rosettes / chinscales (polish, tarnish in the recesses), tricolour cockade (pleats), wool pompom (fuzz), braided
#   wool cords, raquette and tassels; feathered plumes on their own feather tiles (barbs, shaft, darker edges, three
#   shades per colour picked by each feather's "tint").
# Maps (2048 PNG, sources for ImageToPAA, same conventions as the Prussian shako): _co (albedo x baked AO), _nohq
# (tangent normals, OpenGL +Y, from the bump of the procedural materials), _smdi (R = 1, G = specular, B = gloss).
# Bakes with Cycles: DIFFUSE colour only, NORMAL (tangent), AO, EMIT (smdi values). The feather tiles are painted with
# numpy over the baked atlas (the feathers share their tile, so they cannot be baked one by one).
#   blender -b --factory-startup --python texturizar_shako_fr.py -- <blockout .blend> <out .blend> <tex dir> <img dir>
#           [so=<tag>[,<tag>...]] [ao_samples=64] [res=2048] [raiz=FR_] [nome=HCL_Shako_Fr_] [textura=hcl_shako_fr_]
# raiz/nome/textura: prefixes of the root empties, output objects and texture files, so the same baker serves other
# headgear with the same blend layout (2026-10-12: the Prussian cloth cap, blockout_bone_landwehr.py: raiz=PR_bone_
# nome=HCL_Bone_Pruss_ textura=hcl_bone_pruss_).
# v5 (2026-10-13, Old Guard bearskin): arte=<png> replaces the mod atlas for the kind "arte" by a redrawn relief
# (Non-Color height, placa_guarda_relevo.py); arte_escala=<k> / pele_escala=<k> scale the UV islands of the plate /
# fur shell before packing (texel density where the detail is: the shell is mostly hidden by the locks).
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, TEX, IMG = [os.path.abspath(x) for x in a[:4]]
OPT = dict(x.split("=", 1) for x in a[4:] if "=" in x)
RES = int(OPT.get("res", 2048))
AO_S = int(OPT.get("ao_samples", 64))
RAIZ, NOME, TEXP = OPT.get("raiz", "FR_"), OPT.get("nome", "HCL_Shako_Fr_"), OPT.get("textura", "hcl_shako_fr_")
os.makedirs(TEX, exist_ok=True); os.makedirs(IMG, exist_ok=True); os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene

# ---------------------------------------------------------------- kinds of surface
# colour names of the blockout materials (BO_<colour>, BO_plumet_<colour>)
COL = dict(feltro=(0.018, 0.018, 0.020), couro=(0.024, 0.021, 0.019), latao=(0.62, 0.44, 0.15),
           vermelho=(0.55, 0.035, 0.035), amarelo=(0.80, 0.60, 0.08), verde=(0.04, 0.20, 0.07),
           branco=(0.83, 0.82, 0.78), azul=(0.04, 0.09, 0.36), verde_esc=(0.02, 0.15, 0.05), carmesim=(0.40, 0.02, 0.07),
           ouro=(0.80, 0.60, 0.22), preto=(0.02, 0.02, 0.02), ganse=(0.55, 0.54, 0.50),
           prata=(0.60, 0.60, 0.58),   # white metal (tin-plated) of the lozenge-plate variant
           # Prussian cloth cap (blockout_bone_landwehr.py; linear values of the sRGB uniform palette)
           azul_pano=(0.010, 0.016, 0.040), verde_pano=(0.010, 0.022, 0.010),
           couro_marrom=(0.050, 0.028, 0.014), forro=(0.33, 0.29, 0.22),
           pelo=(0.011, 0.009, 0.008))               # bearskin fur (black, brownish in the light)
# mod art (Reto pack, authorised) for the traced plate and the star rosettes, sampled through their UV layer "arte"
ATLAS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "ntw", "france",
                                     "FranceINF_diffuse.png"))
if "atlas" in OPT:                                  # allies: another mod atlas for the kind "arte"
    ATLAS = os.path.abspath(OPT["atlas"])
ART_GAIN = 1.55                                     # the art is darker than our brass (shading baked in the mod)
# feathers are dyed brighter than the cloth of the same name (scarlet plume, light green, yellow, white)
PENA = dict(vermelho=(0.74, 0.07, 0.05), verde=(0.07, 0.34, 0.11), amarelo=(0.93, 0.74, 0.12),
            branco=(0.93, 0.93, 0.89), preto=(0.03, 0.03, 0.03), verde_esc=(0.04, 0.22, 0.07))
# kind -> (spec, gloss) for _smdi
SMDI = dict(feltro=(0.05, 0.12), couro=(0.35, 0.55), verniz=(0.60, 0.85), latao=(0.85, 0.72), ouro=(0.80, 0.65), arte=(0.85, 0.72),
            galao=(0.07, 0.18), cocar=(0.10, 0.25), la=(0.03, 0.08), cordao=(0.06, 0.15), pena=(0.08, 0.25),
            pano=(0.04, 0.10), pele=(0.10, 0.30))


def kind_of(part, colour):
    """Surface kind from the part name (tag removed) and the blockout colour."""
    if part.startswith("pele_corpo"):                   # bearskin shell (blockout_bonnet_guarda.py)
        return "pele"
    if part.startswith("pelo"):                         # bearskin hair locks: tiles like the plume feathers
        return "pena"
    if part.startswith("cruz_galao"):                   # lace cross on the bearskin top patch
        return "galao"
    if part.startswith(("copa", "faixa_pano", "forro", "calota")):   # cloth cap: wool broadcloth, linen lining
        return "pano"
    if part.startswith(("pala_couro", "suadouro", "topo")):      # topo: leather crown of the shako (2026-10-13)
        return "couro"
    if part.startswith("cruz"):
        return "latao"
    if part.startswith("plumet"):
        return "pena"
    if part.endswith("_couro"):                         # leather backing of the chinscales
        return "couro"
    if part.startswith(("placa", "roseta")):            # traced plate / star rosette: relief baked from the mod art
        return "arte"
    if part == "ganse":
        return "galao"
    if part == "ganse_botao":
        return "latao"
    if part == "corpo":
        return "feltro"
    if part == "pala":
        return "verniz"
    if part.startswith(("placa", "tulipa", "roseta", "jugular")):
        return "latao"
    if part.startswith("galao_posto"):
        return "ouro"
    if part.startswith("cocar"):
        return "cocar"
    if part.startswith("pompom"):
        return "la"
    if part.startswith(("cordao", "raquete", "borla")):
        return "cordao"
    if part.startswith(("faixa", "divisa")):
        return "couro" if colour == "couro" else "galao"
    if colour in ("latao", "prata", "ouro"):            # allies: metal parts with other names (czapka peak binding,
        return "latao"                                  # plain bosses, the white eagle laid on a bearskin plate)
    return "feltro"


# ---------------------------------------------------------------- procedural materials (bake sources)
def node(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def proc_material(kind, colour):
    m = bpy.data.materials.new(f"PROC_{kind}_{colour}"); m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    tc = node(nt, "ShaderNodeTexCoord")
    co = tc.outputs["Object"]
    rgb = Vector(COL.get(colour, COL["feltro"]))
    L = nt.links.new

    def noise(scale, detail=2.0, rough=0.5):
        n = node(nt, "ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
        L(co, n.inputs["Vector"]); return n.outputs["Fac"]

    def mix_mul(fac_out, lo, hi):
        """colour * (lo + (hi - lo) * fac)"""
        mr = node(nt, "ShaderNodeMapRange"); L(fac_out, mr.inputs["Value"])
        mr.inputs["To Min"].default_value = lo; mr.inputs["To Max"].default_value = hi
        return mr.outputs["Result"]

    def colour_out(fac_lohi):
        c = node(nt, "ShaderNodeRGB"); c.outputs[0].default_value = (*rgb, 1)
        vm = node(nt, "ShaderNodeVectorMath", operation="SCALE")
        L(c.outputs[0], vm.inputs[0]); L(fac_lohi, vm.inputs["Scale"])
        L(vm.outputs["Vector"], b.inputs["Base Color"])

    def bump(height, strength, distance=0.001):
        bp = node(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = strength
        bp.inputs["Distance"].default_value = distance
        L(height, bp.inputs["Height"]); L(bp.outputs["Normal"], b.inputs["Normal"])

    def add(x, y):
        mm = node(nt, "ShaderNodeMath", operation="ADD"); L(x, mm.inputs[0]); L(y, mm.inputs[1]); return mm.outputs[0]

    def mul(x, k):
        mm = node(nt, "ShaderNodeMath", operation="MULTIPLY"); L(x, mm.inputs[0]); mm.inputs[1].default_value = k
        return mm.outputs[0]

    def wave(scale, kind_="BANDS", direction="X", profile="SIN", distortion=0.0):
        w = node(nt, "ShaderNodeTexWave", wave_type=kind_)
        if kind_ == "BANDS":
            w.bands_direction = direction
        else:
            w.rings_direction = direction
        w.wave_profile = profile
        w.inputs["Scale"].default_value = scale; w.inputs["Distortion"].default_value = distortion
        L(co, w.inputs["Vector"]); return w.outputs["Fac"]

    if kind == "arte":                                  # relief and colour of the mod art, as polished brass
        uvn = node(nt, "ShaderNodeUVMap"); uvn.uv_map = "arte"
        tx = node(nt, "ShaderNodeTexImage")
        if "arte" in OPT:                               # v5: redrawn relief (height, Non-Color)
            tx.image = bpy.data.images.get("ARTE_RELEVO") or bpy.data.images.load(os.path.abspath(OPT["arte"]))
            tx.image.name = "ARTE_RELEVO"; tx.image.colorspace_settings.name = "Non-Color"
        else:
            tx.image = bpy.data.images.get("ATLAS_FR") or bpy.data.images.load(ATLAS)
            tx.image.name = "ATLAS_FR"
        tx.interpolation = "Cubic"
        L(uvn.outputs["UV"], tx.inputs["Vector"])
        # the art's hue is a dark bronze (its shading is baked in): keep OUR brass colour and take only the art's light
        # and shade (luminance) for the relief, so the plate matches the chinscales, tulip and rosettes
        bw = node(nt, "ShaderNodeRGBToBW"); L(tx.outputs["Color"], bw.inputs["Color"])
        lum = node(nt, "ShaderNodeMapRange"); L(bw.outputs["Val"], lum.inputs["Value"])
        if "arte" in OPT:                               # height 0.24 (grooves) .. 0.30 (field) .. 1.0 (highest relief)
            lum.inputs["From Min"].default_value = 0.22; lum.inputs["From Max"].default_value = 1.0
            lum.inputs["To Min"].default_value = 0.42; lum.inputs["To Max"].default_value = 1.30
            colour_out(add(lum.outputs["Result"], mul(noise(55, 3, 0.6), 0.10)))
            bump(bw.outputs["Val"], 1.0, 0.0012)
        else:
            # allies: arte_faixa=<lo>,<hi> = luminance range of the mod art (linear) mapped onto the metal; the French
            # atlas brass needs 0.05..0.45, the dark Polish filigree (polandINF eagle ~0.006..0.04 linear) needs 0.005..0.045
            lo_, hi_ = (float(x) for x in OPT.get("arte_faixa", "0.05,0.45").split(","))
            lum.inputs["From Min"].default_value = lo_; lum.inputs["From Max"].default_value = hi_
            lum.inputs["To Min"].default_value = 0.40; lum.inputs["To Max"].default_value = ART_GAIN * 0.85
            colour_out(lum.outputs["Result"])
            bump(bw.outputs["Val"], 0.6, 0.0008)
    elif kind == "feltro":
        f = add(mul(noise(900, 3, 0.7), 0.6), mul(noise(35, 2, 0.5), 0.4))
        colour_out(mix_mul(f, 0.75, 1.30)); bump(add(mul(noise(900, 3, 0.7), 1.0), mul(noise(35), 0.4)), 0.25)
    elif kind == "couro":
        vo = node(nt, "ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 700; L(co, vo.inputs["Vector"])
        colour_out(mix_mul(add(mul(noise(60), 0.6), mul(vo.outputs["Distance"], 0.4)), 0.8, 1.4))
        bump(vo.outputs["Distance"], 0.25)
    elif kind == "verniz":
        colour_out(mix_mul(noise(40), 0.85, 1.15)); bump(noise(300), 0.04)
    elif kind in ("latao", "ouro"):
        tarn = noise(55, 3, 0.6)
        scratch = wave(400, "BANDS", "Z", "SIN", 6.0)
        colour_out(add(mix_mul(tarn, 0.55, 1.15), mul(scratch, 0.08))); bump(add(tarn, mul(scratch, 0.3)), 0.12)
        if kind == "ouro":                                  # gold lace: woven ribs over the metal colour
            rib = wave(1600, "BANDS", "Z", "SIN")
            colour_out(add(mix_mul(tarn, 0.6, 1.1), mul(rib, 0.25))); bump(rib, 0.35)
    elif kind == "pele":                                # fur shell: long strands hanging down, clumped
        strands = wave(2600, "BANDS", "X", "SIN", 14.0); clump = noise(60, 3, 0.6)
        colour_out(mix_mul(add(mul(strands, 0.5), mul(clump, 0.5)), 0.55, 1.6)); bump(add(strands, mul(clump, 0.8)), 0.6)
    elif kind == "pano":                                # fulled wool broadcloth: fine twill under a felted nap
        twill = wave(1100, "BANDS", "DIAGONAL", "SIN"); nap = noise(700, 3, 0.7); mottle = noise(25, 2, 0.5)
        colour_out(add(mix_mul(add(mul(nap, 0.6), mul(mottle, 0.4)), 0.78, 1.22), mul(twill, 0.05)))
        bump(add(mul(twill, 0.5), mul(nap, 0.6)), 0.22)
    elif kind == "galao":
        rib = wave(1500, "BANDS", "Z", "SIN"); fuzz = noise(500, 2, 0.6)
        colour_out(add(mix_mul(fuzz, 0.75, 1.05), mul(rib, 0.18))); bump(add(rib, mul(fuzz, 0.4)), 0.35)
    elif kind == "cocar":
        pleat = wave(250, "RINGS", "SPHERICAL", "SAW"); fuzz = noise(400)
        colour_out(add(mix_mul(fuzz, 0.8, 1.05), mul(pleat, 0.15))); bump(pleat, 0.4)
    elif kind == "la":
        f1, f2 = noise(260, 4, 0.75), noise(40, 2, 0.5)
        colour_out(mix_mul(add(mul(f1, 0.7), mul(f2, 0.3)), 0.6, 1.25)); bump(f1, 0.8)
    elif kind == "cordao":
        braid = wave(220, "BANDS", "Z", "SIN", 2.0); fuzz = noise(500)
        colour_out(add(mix_mul(fuzz, 0.7, 1.0), mul(braid, 0.25))); bump(add(braid, mul(fuzz, 0.3)), 0.6)
    else:                                                   # pena (only for the bake fill; painted later)
        colour_out(mix_mul(noise(50), 0.9, 1.0))
    b.inputs["Roughness"].default_value = 1.0 - SMDI[kind][1] * 0.8
    m["hcl_kind"] = kind
    return m


def emit_material(val_rgb, name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*val_rgb, 1)
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m


# ---------------------------------------------------------------- feather tiles
TILE = 0.2                                          # 9 tiles: right strip (5) + bottom strip (4)
TILES = [(0.8, 0.2 * i) for i in range(5)] + [(0.2 * i, 0.0) for i in range(4)]
SHADES = (0.82, 1.0, 1.15)


def paint_fur_tile(img_px, nrm_px, smdi_px, origin, rgb, shade):
    """Hair lock tile (u across the lock, v root -> tip): ~180 strands waving down the lock, thinning and fading toward
    the tip, the lock's edges darker (they curl into the mass), a warm sheen on the strand crests."""
    n = int(TILE * RES)
    x0, y0 = int(origin[0] * RES), int(origin[1] * RES)
    v, u = np.mgrid[0:n, 0:n] / (n - 1.0)
    rng = np.random.default_rng(int(1000 * shade) + 77)
    h = np.zeros((n, n), np.float32); lit = np.zeros((n, n), np.float32)
    for k in range(180):
        c0 = rng.uniform(0.02, 0.98); amp = rng.uniform(0.004, 0.03); fr = rng.uniform(3, 9); ph = rng.uniform(0, 6.3)
        drift = rng.uniform(-0.06, 0.06)
        w = rng.uniform(0.004, 0.011) * (1.0 - 0.6 * v)
        end = rng.uniform(0.65, 1.0)
        cx = c0 + amp * np.sin(fr * v + ph) + drift * v + (0.5 - c0) * 0.35 * v      # strands gather toward the tip
        prof = np.exp(-((u - cx) / w) ** 2) * (v < end) * (1 - np.clip((v - end + 0.15) / 0.15, 0, 1))
        h = np.maximum(h, prof * rng.uniform(0.6, 1.0))
        lit += prof * rng.uniform(0.0, 0.5)
    edge = np.clip((np.abs(u - 0.5) - 0.30) / 0.20, 0, 1)
    f = (0.35 + 0.95 * h + 0.35 * np.clip(lit, 0, 1)) * shade * (1 - 0.55 * edge) * (1 - 0.25 * v)
    col = np.clip(np.array(rgb)[None, None, :] * f[..., None] + np.array((0.010, 0.006, 0.003))[None, None, :] * np.clip(lit, 0, 1)[..., None], 0, 1)
    img_px[y0:y0 + n, x0:x0 + n, :3] = col
    gy, gx = np.gradient(h - 0.5 * edge)
    nv = np.dstack([-gx * 10, -gy * 10, np.ones_like(h)])
    nv /= np.linalg.norm(nv, axis=2, keepdims=True)
    nrm_px[y0:y0 + n, x0:x0 + n, :3] = nv * 0.5 + 0.5
    smdi_px[y0:y0 + n, x0:x0 + n, :3] = (1.0, *SMDI["pele"])


def paint_feather_tile(img_px, nrm_px, smdi_px, origin, rgb, shade):
    """Feather tile v2 (2026-10-13, "mais realismo as pumlets"): u across the vane (0.5 = shaft), v root -> tip.
    Fine barbs running out and up from the shaft (~110 per side), each with its own shade, small gaps between barb
    groups toward the edge (the vane splits), a thin shaft that took less dye (lighter), the down at the root darker
    and denser, the tip a little paler; heights from the barbs and the shaft ridge."""
    n = int(TILE * RES)
    x0, y0 = int(origin[0] * RES), int(origin[1] * RES)
    v, u = np.mgrid[0:n, 0:n] / (n - 1.0)
    du = np.abs(u - 0.5)
    rng = np.random.default_rng(int(1000 * shade) + int(255 * rgb[0]))
    wob = 0.5 * rng.standard_normal((n, n)).cumsum(axis=1) / n * 6
    ph = du * 2.2 - v + 0.012 * wob                          # barbs leave the shaft at ~65 deg toward the tip
    k = 110.0
    idx = np.floor(ph * k)
    frac = ph * k - idx
    barb = np.exp(-((frac - 0.5) / 0.28) ** 2)               # one barb, soft profile
    lot = np.random.default_rng(7).random(4096)
    bshade = 0.80 + 0.35 * lot[(idx.astype(np.int64) % 4096)]
    grp = np.floor(ph * k / 5.0).astype(np.int64)            # groups of ~5 barbs; some groups part from the next
    gap = (lot[(grp * 7 + 3) % 4096] > 0.72) & (np.abs(ph * k / 5.0 - grp - 0.92) < 0.08)
    split = gap * np.clip((du - 0.18) / 0.20, 0, 1)
    shaft = np.exp(-(du / 0.018) ** 2)
    root = np.clip(1 - v / 0.22, 0, 1)
    edge = np.clip((du - 0.40) / 0.10, 0, 1)
    f = (0.55 + 0.50 * barb * bshade) * (1 - 0.55 * split) * (1 - 0.35 * edge)
    f = f * (1 - 0.30 * root) * (0.92 + 0.14 * v) * shade
    col = np.array(rgb)[None, None, :] * f[..., None]
    col = col * (1 - 0.6 * shaft[..., None]) + np.clip(np.array(rgb) * 1.25 + 0.06, 0, 1)[None, None, :] * (0.6 * shaft[..., None])
    img_px[y0:y0 + n, x0:x0 + n, :3] = np.clip(col, 0, 1)
    h = 0.55 * barb - 0.6 * split + 0.9 * shaft - 0.35 * edge
    gy, gx = np.gradient(h)
    nv = np.dstack([-gx * 7, -gy * 7, np.ones_like(h)])
    nv /= np.linalg.norm(nv, axis=2, keepdims=True)
    nrm_px[y0:y0 + n, x0:x0 + n, :3] = nv * 0.5 + 0.5
    smdi_px[y0:y0 + n, x0:x0 + n, :3] = (1.0, SMDI["pena"][0], SMDI["pena"][1])


# ---------------------------------------------------------------- per variant
roots = sorted([o for o in bpy.data.objects if o.name.startswith(RAIZ) and o.type == "EMPTY"], key=lambda o: o.matrix_world.translation.x)
keep = []
log = []


def P_(s):
    print(s); log.append(s)


for root in roots:
    tag = root.name[len(RAIZ):]
    if "so" in OPT and tag not in OPT["so"].split(","):     # so=<tag>[,<tag>...]
        continue
    kids = [o for o in bpy.data.objects if o.parent is root and o.type == "MESH"]
    x_off = root.matrix_world.translation.x
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    art = bm.loops.layers.uv.new("arte")
    KL = bm.faces.layers.int.new("hcl_kind_i")
    PLt = bm.faces.layers.float.new("tint")
    KINDS, KCOL = [], []
    plume_faces = []
    for o in kids:
        part = o.name[len(tag) + 1:]
        me = o.data
        M = Matrix.Translation(Vector((-x_off, 0, 0))) @ o.matrix_world
        vmap = [bm.verts.new(M @ v.co) for v in me.vertices]
        src_uv = me.uv_layers["UVMap"].data if "UVMap" in me.uv_layers else (me.uv_layers[0].data if len(me.uv_layers) and me.uv_layers[0].name != "arte" else None)
        src_art = me.uv_layers["arte"].data if "arte" in me.uv_layers else None
        tint = me.attributes.get("tint")
        for p in me.polygons:
            colour = me.materials[p.material_index].name.replace("BO_plumet_", "").replace("BO_", "")
            kd = kind_of(part, colour)
            key = (kd, colour)
            if key not in KINDS:
                KINDS.append(key)
            try:
                f = bm.faces.new([vmap[i] for i in p.vertices])
            except ValueError:
                continue
            f[KL] = KINDS.index(key)
            f.smooth = kd in ("pena", "la", "cordao", "latao", "ouro") or part.startswith(("pompom", "tulipa"))
            if src_art is not None:
                for l, li in zip(f.loops, p.loop_indices):
                    l[art].uv = src_art[li].uv
            if kd == "pena":
                f[PLt] = tint.data[p.index].value if tint is not None else 0.5
                for l, li in zip(f.loops, p.loop_indices):
                    l[uvl].uv = src_uv[li].uv if src_uv else (0.0, 0.0)
                plume_faces.append(f)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    me_new = bpy.data.meshes.new(f"{NOME}{tag}_LOD0")
    bm.to_mesh(me_new); bm.free()
    ob = bpy.data.objects.new(f"{NOME}{tag}_LOD0", me_new)
    scene.collection.objects.link(ob)
    kinds_attr = me_new.attributes["hcl_kind_i"].data
    for key in KINDS:
        me_new.materials.append(proc_material(*key))
    for p in me_new.polygons:
        p.material_index = kinds_attr[p.index].value
    ob["hcl_kinds"] = ",".join(f"{k}:{c}" for k, c in KINDS)
    me_new.uv_layers.active = me_new.uv_layers["UVMap"]
    me_new.uv_layers["UVMap"].active_render = True
    # UV: smart projection + pack of everything but the feathers, into the atlas region left by the feather tiles
    has_plume = any(k == "pena" for k, _ in KINDS)
    for o_ in scene.objects:
        o_.select_set(False)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    ebm = bmesh.from_edit_mesh(me_new)
    ekl = ebm.faces.layers.int.get("hcl_kind_i")
    pena_i = {i for i, (k, _) in enumerate(KINDS) if k == "pena"}
    for f in ebm.faces:
        f.select = f[ekl] not in pena_i
    bmesh.update_edit_mesh(me_new)
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=0.004, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    escala = {k: float(OPT[f"{k}_escala"]) for k in ("arte", "pele") if f"{k}_escala" in OPT}
    if escala:                                          # v5: more (or fewer) texels for some kinds
        ebm = bmesh.from_edit_mesh(me_new)
        euv = ebm.loops.layers.uv.active
        ekl = ebm.faces.layers.int.get("hcl_kind_i")
        for kname, k_ in escala.items():
            fs = [f for f in ebm.faces if f.select and KINDS[f[ekl]][0] == kname]
            if not fs:
                continue
            cu_ = sum(l[euv].uv.x for f in fs for l in f.loops) / sum(len(f.loops) for f in fs)
            cv_ = sum(l[euv].uv.y for f in fs for l in f.loops) / sum(len(f.loops) for f in fs)
            for f in fs:
                for l in f.loops:
                    l[euv].uv = (cu_ + (l[euv].uv.x - cu_) * k_, cv_ + (l[euv].uv.y - cv_) * k_)
            print(f"ESCALA UV {kname} x{k_} ({len(fs)} faces)")
        bmesh.update_edit_mesh(me_new)
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin=0.004, shape_method="CONCAVE")
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=0.004)
    ebm = bmesh.from_edit_mesh(me_new)
    euv = ebm.loops.layers.uv.active
    ekl = ebm.faces.layers.int.get("hcl_kind_i")
    etint = ebm.faces.layers.float.get("tint")
    for f in ebm.faces:
        if f[ekl] in pena_i:
            colour = KINDS[f[ekl]][1]
            cidx = sorted({KINDS[i][1] for i in pena_i}).index(colour)
            sh = min(2, int(f[etint] * 3))
            ox, oy = TILES[cidx * 3 + sh]
            for l in f.loops:
                u, v = l[euv].uv
                l[euv].uv = (ox + TILE * (0.02 + 0.96 * min(max(u, 0), 1)), oy + TILE * (0.02 + 0.96 * min(max(v, 0), 1)))
        elif has_plume:
            for l in f.loops:
                u, v = l[euv].uv
                l[euv].uv = (u * 0.8, 0.2 + v * 0.8)
    bmesh.update_edit_mesh(me_new)
    bpy.ops.object.mode_set(mode="OBJECT")

    # bakes
    def new_img(name, colour_space="sRGB", fill=(0, 0, 0, 1)):
        im = bpy.data.images.new(name, RES, RES, alpha=False, float_buffer=False)
        im.colorspace_settings.name = colour_space
        im.generated_color = fill
        return im

    def bake(kind_, img, mats=None, **kw):
        saved = [s.material for s in ob.material_slots]
        if mats is not None:
            for s, m in zip(ob.material_slots, mats):
                s.material = m
        for s in ob.material_slots:
            nt = s.material.node_tree
            n = nt.nodes.get("BAKE_TARGET") or nt.nodes.new("ShaderNodeTexImage")
            n.name = "BAKE_TARGET"; n.image = img; nt.nodes.active = n
        for o_ in scene.objects:
            o_.hide_render = o_ is not ob
            o_.select_set(o_ is ob)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.bake(type=kind_, margin=6, use_clear=True, **kw)
        for s, m in zip(ob.material_slots, saved):
            s.material = m

    scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("w")
    scene.cycles.samples = 8
    alb = new_img(f"{tag}_alb")
    bake("DIFFUSE", alb, pass_filter={"COLOR"})
    nrm = new_img(f"{tag}_nrm", "Non-Color", (0.5, 0.5, 1, 1))
    bake("NORMAL", nrm, normal_space="TANGENT")
    scene.cycles.samples = AO_S
    scene.world.light_settings.distance = 0.05
    ao = new_img(f"{tag}_ao", "Non-Color", (1, 1, 1, 1))
    bake("AO", ao)
    scene.cycles.samples = 1
    sm = new_img(f"{tag}_smdi", "Non-Color", (1, 0.05, 0.1, 1))
    bake("EMIT", sm, mats=[emit_material((1.0, *SMDI[k]), f"SMDI_{k}") for k, _ in KINDS])

    def arr(im):
        return np.array(im.pixels[:], np.float32).reshape(RES, RES, 4)

    A, N_, O, S_ = arr(alb), arr(nrm), arr(ao), arr(sm)
    CO = A.copy()
    CO[..., :3] = A[..., :3] * (0.45 + 0.55 * O[..., :1])
    for cidx, colour in enumerate(sorted({KINDS[i][1] for i in pena_i})):
        for sh in range(3):
            painter = paint_fur_tile if colour == "pelo" else paint_feather_tile
            painter(CO, N_, S_, TILES[cidx * 3 + sh], PENA.get(colour, COL[colour]), SHADES[sh])
    base = f"{TEXP}{tag}"
    for data, suffix, cs in ((CO, "co", "sRGB"), (N_, "nohq", "Non-Color"), (S_, "smdi", "Non-Color")):
        im = bpy.data.images.new(f"{base}_{suffix}", RES, RES, alpha=False)
        im.colorspace_settings.name = cs
        data[..., 3] = 1.0
        im.pixels.foreach_set(data.ravel())
        im.filepath_raw = os.path.join(TEX, f"{base}_{suffix}.png"); im.file_format = "PNG"; im.save()
    tris = sum(len(p.vertices) - 2 for p in me_new.polygons)
    P_(f"BARRETINA {tag}: {len(kids)} pecas -> 1 malha, {tris} triangulos; tipos {', '.join(f'{k}:{c}' for k, c in KINDS)}; "
       f"plumet {'sim' if has_plume else 'nao'}; texturas {base}_{{co,nohq,smdi}}.png")
    keep.append((ob, base))

# ---------------------------------------------------------------- textured preview materials, renders, save
for ob, base in keep:
    m = bpy.data.materials.new(f"TEX_{base}"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, f"{base}_co.png"))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(os.path.join(TEX, f"{base}_nohq.png"))
    tn.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    ts = nt.nodes.new("ShaderNodeTexImage"); ts.image = bpy.data.images.load(os.path.join(TEX, f"{base}_smdi.png"))
    ts.image.colorspace_settings.name = "Non-Color"
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(ts.outputs["Color"], sep.inputs["Color"])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs["Blue"], inv.inputs[1]); nt.links.new(inv.outputs[0], b.inputs["Roughness"])
    met = nt.nodes.new("ShaderNodeMath"); met.operation = "GREATER_THAN"; met.inputs[1].default_value = 0.7
    nt.links.new(sep.outputs["Green"], met.inputs[0]); nt.links.new(met.outputs[0], b.inputs["Metallic"])
    ob.data.materials.clear(); ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.material_index = 0
# remove the blockout parts from the saved file (the blockout blend keeps them)
for o in list(bpy.data.objects):
    if o.type in ("MESH", "EMPTY") and not o.name.startswith((NOME, "REF_cabeca")):
        bpy.data.objects.remove(o)
heads = sorted([o for o in bpy.data.objects if o.name.startswith("REF_cabeca")], key=lambda o: o.name)
for i, h in enumerate(heads):
    if i > 0:
        bpy.data.objects.remove(h)
ROWS = 0.30
for i, (ob, base) in enumerate(keep):
    ob.location.x = i * ROWS
    ob.hide_render = False            # the bakes left only the last baked object render-visible
if heads:
    heads[0].hide_render = True
cam = bpy.data.objects.get("cam") or bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
if cam.name not in scene.collection.objects:
    scene.collection.objects.link(cam)
scene.camera = cam
scene.cycles.samples = 48
scene.view_settings.view_transform = "Standard"
zs = [(ob.matrix_world @ v.co).z for ob, _ in keep for v in ob.data.vertices]
zc = (min(zs) + max(zs)) / 2
mid = ROWS * (len(keep) - 1) / 2


def shot(name, loc, target, ortho=None, lens=60, res=(2000, 900)):
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    cam.data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(IMG, f"textura_fr_{name}.png")
    bpy.ops.render.render(write_still=True)
    P_("render " + scene.render.filepath)


shot("fila_tres_quartos", (mid + 0.9, -2.2, zc + 0.45), (mid, 0, zc), lens=50, res=(2200, 900))
if "so" in OPT:                       # subset: one close-up per baked variant
    for i, (ob, base) in enumerate(keep):
        shot(base.replace(TEXP, "") + "_perto", (i * ROWS + 0.34, -0.48, zc + 0.10), (i * ROWS, 0.01, zc + 0.01),
             lens=60, res=(1000, 900))
elif len(keep) > 1:
    shot("granadeiro_perto", (1 * ROWS + 0.32, -0.42, zc + 0.10), (1 * ROWS, 0.01, zc - 0.03), lens=60, res=(1000, 1100))
    shot("voltigeur_perto", (3 * ROWS - 0.35, -0.40, zc + 0.08), (3 * ROWS, 0.01, zc - 0.03), lens=60, res=(1000, 1100))
    shot("fuzileiro_perto", (0 * ROWS + 0.30, -0.42, zc - 0.02), (0 * ROWS, 0.01, zc - 0.08), lens=60, res=(1000, 900))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
P_(f"saved {OUT}")
open(os.path.join(IMG, "texturizar_shako_fr_output.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
