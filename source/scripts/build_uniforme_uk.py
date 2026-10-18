# British line infantry jacket 1812 (short-tailed, single-breasted), derived from the validated Prussian 1813 uniform
# production mesh like the French coat (build_uniforme_fr.py, copied here and left untouched): same body, sleeves,
# cuffs with flaps, shoulder straps, trousers, gaiters, shoes, template hands and the collar v2 fitted to the GAME head.
# Spec: docs/specs/uk_1812.md section 2.1 (K1-K3 as recommended). Changes:
#   1. tails shortened: hem from 0.70 m to TAIL_HEM (short tails of the 1812 jacket), re-draped over the trousers
#      exactly as in the French coat (same code)
#   2. the Prussian front (14 buttons in two close rows) is removed
#   3. new front buttons (copies of a coat button, turned to the cloth normal):
#        frente=linha   10 buttons on the centre line in 5 pairs (mod art britainINF c0-c3 r0); the white worsted lace
#                       loops of the line are PAINTED by generate_uniform_textures_uk.py from the button list
#        frente=rifles  3 rows of 10: centre + one on each side diverging toward the shoulders (mod art britainINF
#                       c3 r2, the 95th jacket; count and spread read on the art, no source read)
#        frente=simples   Portugal, line: 10 buttons evenly spaced, no lace (docs/specs/portugal_1812.md)
#        frente=alamares  Portugal, Cacadores: 8 rows of 3 (frogging painted between them)
#      the centres go in ob["hcl_botoes_frente"] (JSON: style, list of [x, y, z, side]) for the painter
#   No lapels: every UV is kept, so the painter's maps stay valid.
#   blender -b --factory-startup --python build_uniforme_uk.py -- <prussian LOD0 .blend> <out .blend> [hem=0.92]
#                                                               [frente=linha|rifles|simples|alamares] [nome=...]
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
TAIL_HEM = float(OPT.get("hem", 0.92))
FRENTE = OPT.get("frente", "linha")
NOME = OPT.get("nome", "HCL_U_UK1812_Linha_LOD0")
GROUND = -1.0069
Z = lambda h: GROUND + h
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
ob.name = NOME
ob.data = ob.data.copy(); ob.data.name = NOME
parts = ob["hcl_partes"].split(",")
PID = {n: i for i, n in enumerate(parts)}
MAT = {m.name: i for i, m in enumerate(ob.data.materials)}
bm = bmesh.new(); bm.from_mesh(ob.data)
PL = bm.faces.layers.int.get("hcl_part")
uvl = bm.loops.layers.uv.active
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()


def vparts():
    vp = {}
    for f in bm.faces:
        for v in f.verts:
            vp.setdefault(v, set()).add(f[PL])
    return vp


def components(pid):
    vp = vparts()
    seen, comps = set(), []
    for v in bm.verts:
        if v in seen or pid not in vp.get(v, ()):
            continue
        comp, st = [], [v]
        seen.add(v)
        while st:
            x = st.pop(); comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y not in seen and pid in vp.get(y, ()):
                    seen.add(y); st.append(y)
        comps.append(comp)
    return comps


def tri_bvh(pids):
    vs = list(bm.verts)
    idx = {v: i for i, v in enumerate(vs)}
    tris = []
    for f in bm.faces:
        if f[PL] in pids:
            q = [idx[v] for v in f.verts]
            for t in range(1, len(q) - 1):
                tris.append([q[0], q[t], q[t + 1]])
            if len(q) == 4:
                tris.append([q[0], q[1], q[3]]); tris.append([q[1], q[2], q[3]])
    return BVHTree.FromPolygons([v.co.copy() for v in vs], tris)


# ---------------------------------------------------------------- 1. short tails
# The Prussian tails hang behind the thighs down to 0.70 m. Squeezing them up onto the seat (fuller than the thighs)
# made the trousers cut through the hem and the vent spike (render 2026-10-12). Instead the tails are RE-DRAPED: every
# tail vertex keeps its angle about the body axis and its horizontal offset from the trousers surface at its own
# height, and is placed at the new (compressed) height at the same offset from the trousers there. Cloth and turnback
# lining keep their few-mm separation, so the lining cannot come through.
TOP = 1.14
k = (TOP - TAIL_HEM) / (TOP - 0.70)
AX = Vector((0.0, 0.02, 0.0))
vp = vparts()
tail_v = [v for v in bm.verts if vp.get(v, set()) & {PID["aba_E"], PID["aba_D"]}]
TR = tri_bvh({PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]})


def trousers_r(phi, z):
    d = Vector((math.sin(phi), math.cos(phi), 0.0))            # phi = 0: back (+Y), +90 deg: +X
    o = Vector((AX.x, AX.y, z)) + d * 0.6
    hit = TR.ray_cast(o, -d, 0.6)
    return None if hit[0] is None else (hit[0] - Vector((AX.x, AX.y, z))).to_2d().length


new_co, kept, offs = {}, 0, []
for v in tail_v:
    if v.co.z >= Z(TOP):
        continue
    q = (v.co - AX).to_2d()
    phi = math.atan2(q.x, q.y)
    r0 = trousers_r(phi, v.co.z)
    z1 = Z(TOP) - (Z(TOP) - v.co.z) * k
    r1 = trousers_r(phi, z1)
    if r0 is None or r1 is None:
        new_co[v] = Vector((v.co.x, v.co.y, z1))
        kept += 1
        continue
    d = q.length - r0
    offs.append(d)
    rr = r1 + min(max(d, 0.004), 0.025)        # at the vent the old ray passed between the thighs: cap the offset
    new_co[v] = Vector((AX.x + math.sin(phi) * rr, AX.y + math.cos(phi) * rr, z1))
# smooth the displacement over the tail (both layers move alike; removes spikes where a ray hit a different surface)
disp = {v: new_co[v] - v.co for v in new_co}
for _ in range(4):
    nd = {}
    for v, d_ in disp.items():
        nb = [disp[e.other_vert(v)] for e in v.link_edges if e.other_vert(v) in disp]
        nd[v] = d_ * 0.5 + (sum(nb, Vector()) / len(nb)) * 0.5 if nb else d_
    disp = nd
for v, d_ in disp.items():
    v.co = v.co + d_
btn_moved = 0
for comp in components(PID["botoes"]):                    # buttons on the tails (back waist) follow the same map
    c = sum((v.co for v in comp), Vector()) / len(comp)
    if Z(0.60) < c.z < Z(TOP) and abs(c.x) < 0.30:
        dz = (Z(TOP) - (Z(TOP) - c.z) * k) - c.z
        for v in comp:
            v.co.z += dz
        btn_moved += 1
hem = min(v.co.z for v in tail_v) - GROUND
offs.sort()
print(f"ABAS: barra {hem:.3f} m (era 0.700); fator {k:.3f}; afastamento da calca preservado em {len(offs)} vertices "
      f"(min {offs[0] * 1000:.1f} mm, mediana {offs[len(offs) // 2] * 1000:.1f} mm; minimo imposto 4 mm); "
      f"{kept} sem calca na direcao (so a altura muda); {btn_moved} botoes das abas movidos")

# ---------------------------------------------------------------- 2. remove the Prussian front buttons
front = [comp for comp in components(PID["botoes"])
         if (lambda c: abs(c.x) < 0.03 and c.y < -0.05 and Z(1.15) < c.z < Z(1.50))(sum((v.co for v in comp), Vector()) / len(comp))]
template = None
for comp in front:
    c = sum((v.co for v in comp), Vector()) / len(comp)
    if template is None and abs(c.z - Z(1.335)) < 0.01 and c.x > 0:
        template = True
        tmpl_faces = {f for v in comp for f in v.link_faces}
        tmpl_data = [([comp.index(x) for x in f.verts], [l[uvl].uv.copy() for l in f.loops], f.material_index) for f in tmpl_faces]
        tmpl_co = [v.co.copy() for v in comp]
        tmpl_c = c.copy()
dead = {v for comp in front for v in comp}
bmesh.ops.delete(bm, geom=list(dead), context="VERTS")
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
print(f"FRENTE: {len(front)} botoes prussianos removidos")

# ---------------------------------------------------------------- 3. British front buttons
COAT = tri_bvh({PID["casaco_corpo"]})
_vp = vparts()
GOLA_V = [v.co.copy() for v in bm.verts if PID["gola"] in _vp.get(v, ())]
OFF = 0.0008                                                   # button base just over the cloth (the button is domed)


def coat_front(x, z):
    hit = COAT.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 1.0)
    if hit[0] is None:
        return None, None
    n = hit[1] if hit[1].y < 0 else -hit[1]
    return hit[0], n.normalized()


gola_foot = min(p.z for p in GOLA_V if p.y < 0.0 and abs(p.x) < 0.02) - GROUND     # collar's front foot (height)
H_TOP = gola_foot - 0.028
H_BOT = 1.150                                                   # waist seam of the jacket front
pos = []                                                        # (x, z_height, side) side: 0 centre, +1 left, -1 right
if FRENTE == "linha":
    # 5 pairs (mod art britainINF c0-c3 r0): pair spacing from the top to the waist, 26 mm between the two of a pair
    tops = np.linspace(H_TOP, H_BOT + 0.040, 5)
    for h in tops:
        for dz in (0.0, -0.026):
            pos.append((0.0, h + dz, 0))
elif FRENTE == "rifles":
    # three rows of 10 (britainINF c3 r2): centre row on the closing, side rows 55 mm out at the waist, 95 mm at the top
    for h in np.linspace(H_TOP, H_BOT + 0.012, 10):
        t = (h - H_BOT) / (H_TOP - H_BOT)
        for side in (0, 1, -1):
            pos.append((side * (0.055 + 0.040 * t), h, side))
elif FRENTE == "simples":
    # Portuguese line 1806 regulation (docs/specs/portugal_1812.md 1.1): single-breasted, no lace; 10 buttons evenly
    # spaced on the closing (count not in the sources read, kept from the British jacket)
    for h in np.linspace(H_TOP, H_BOT + 0.012, 10):
        pos.append((0.0, h, 0))
elif FRENTE == "alamares":
    # Portuguese Cacadores (portugal_1812.md section 2; 6th Cacadores 1811, Napoleon Series): 8 rows of black lace
    # frogging with a button at each end and in the centre; the frogging is PAINTED by the painter (key "alamar")
    for h in np.linspace(H_TOP, H_BOT + 0.020, 8):
        t = (h - H_BOT) / (H_TOP - H_BOT)
        for side in (0, 1, -1):
            pos.append((side * (0.055 + 0.040 * t), h, side))
else:
    raise SystemExit(f"frente desconhecida: {FRENTE}")
loc0, n0, _, _ = COAT.find_nearest(tmpl_c)
n0 = n0 if n0.y < 0 else -n0
base0 = loc0
btn_list = []
for x, h, side in pos:
    p, n = coat_front(x, Z(h))
    if p is None:
        raise RuntimeError(f"casaco nao encontrado em x {x:.3f} h {h:.3f}")
    R = n0.rotation_difference(n).to_matrix()
    nv = [bm.verts.new(p + n * OFF + R @ (co - base0)) for co in tmpl_co]
    for idxs, uvs, mi in tmpl_data:
        f = bm.faces.new([nv[i] for i in idxs])
        f[PL] = PID["botoes"]; f.material_index = mi
        for l, uv in zip(f.loops, uvs):
            l[uvl].uv = uv
    btn_list.append([round(p.x, 5), round(p.y, 5), round(p.z, 5), side])
print(f"BOTOES da frente ({FRENTE}): {len(btn_list)}; alturas {H_BOT:.3f}..{H_TOP:.3f} m (pe da gola {gola_foot:.3f})")

bm.normal_update()
bm.to_mesh(ob.data)
ob.data.update()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_botoes_frente"] = json.dumps({"estilo": FRENTE, "botoes": btn_list})
ob["hcl_origem"] = f"derivado de HCL_U_Pruss1813_01_LOD0 (gola v2) por build_uniforme_uk.py frente={FRENTE}"
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print(f"UNIFORME UK: {len(ob.data.vertices)} vertices, {tris} triangulos (Res 1; o prussiano tem 11960 + gola)")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)

