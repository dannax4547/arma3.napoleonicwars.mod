# French line infantry coat 1812 ("habit-veste", fusilier), derived from the validated Prussian 1813 uniform
# production mesh (same body, sleeves, cuffs with flaps, shoulder straps, trousers, gaiters, shoes, template hands, and
# the collar v2 fitted to the GAME head). Spec: docs/specs/uniforme_frances_infantaria_1812.md (F1-F3 as recommended:
# fusilier, short tails, white trousers). Changes:
#   1. tails shortened: hem from 0.70 m to TAIL_HEM (short tails of the 1812 coat, mod tile M1), compressed toward the
#      waist, then pushed out of the trousers where they would cut into the seat
#   2. the Prussian single-breasted front (14 buttons in two close rows) is removed
#   3. lapels: two closed lapels on the chest from under the collar to the waist, meeting at the centre line, each a
#      panel 3 mm proud of the coat with walls down to it, 7 buttons along its outer edge (copies of a coat button)
#   4. UV: the lapels go in the free strip at the right of the atlas (u 0.94-1.0), at the coat's texel density;
#      every other UV is kept, so the texture painter works unchanged (new colour keys "lapela", "lapela_debrum")
#   blender -b --factory-startup --python build_uniforme_fr.py -- <prussian LOD0 .blend> <out .blend> [hem=0.92]
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = [os.path.abspath(x) for x in a[:2]]
OPT = dict(x.split("=", 1) for x in a[2:] if "=" in x)
TAIL_HEM = float(OPT.get("hem", 0.92))
GROUND = -1.0069
Z = lambda h: GROUND + h
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(SRC, link=False) as (src, dst):
    dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
ob.name = "HCL_U_Fr1812_01_LOD0"
ob.data = ob.data.copy(); ob.data.name = "HCL_U_Fr1812_01_LOD0"
parts = ob["hcl_partes"].split(",")
parts += ["lapela_E", "lapela_D"]
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

# ---------------------------------------------------------------- 3. lapels
COAT = tri_bvh({PID["casaco_corpo"]})
_vp = vparts()
GOLA_V = [v.co.copy() for v in bm.verts if PID["gola"] in _vp.get(v, ())]
DENS = 0.402                                                   # coat texel density, UV units per metre (measured)
OFF = 0.003                                                    # lapel face this far off the coat
H_BOT = 1.135
NU, NV = 5, 16


def coat_front(x, z):
    hit = COAT.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 1.0)
    if hit[0] is None:
        return None, None
    n = hit[1] if hit[1].y < 0 else -hit[1]
    return hit[0], n.normalized()


def h_top(x):
    """Just under the collar's front foot at this x (the lapels start at the collar seam)."""
    near = [p for p in GOLA_V if p.y < 0.02 and abs(abs(p.x) - abs(x)) < 0.008]
    return (min(p.z for p in near) - GROUND - 0.004) if near else 1.47


def width(h):
    t = (h - H_BOT) / (1.47 - H_BOT)
    return 0.072 + 0.010 * max(0.0, min(1.0, t))                # 7.2 cm at the waist, 8.2 cm at the top


UV0 = {"E": (0.942, 0.020), "D": (0.942, 0.190)}
WALL_U = {"E": 0.980, "D": 0.990}
new_faces = {"E": [], "D": []}
btn_pos = {"E": [], "D": []}
for s, sx in (("E", 1.0), ("D", -1.0)):
    grid, surf = [], []
    x_in = 0.0006
    for j in range(NV + 1):
        row, srow = [], []
        for i in range(NU + 1):
            # height first along the inner edge, then each column follows the collar foot at its own x
            u = i / NU
            x = sx * (x_in + u * (width(1.40) - x_in))
            ht = h_top(x)
            h = ht - (ht - H_BOT) * (j / NV)
            x = sx * (x_in + u * (width(h) - x_in))
            p, n = coat_front(x, Z(h))
            if p is None:
                raise RuntimeError(f"lapela {s}: casaco nao encontrado em x {x:.3f} h {h:.3f}")
            row.append(bm.verts.new(p + n * OFF))
            srow.append((p, n, x, h))
        grid.append(row); surf.append(srow)
    PART = PID[f"lapela_{s}"]
    u0, v0 = UV0[s]

    def uv_top(x, h):
        return (u0 + abs(x) * DENS, v0 + (h - H_BOT) * DENS)

    for j in range(NV):
        for i in range(NU):
            vs = [grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]]
            f = bm.faces.new(vs)
            f[PL] = PART; f.material_index = MAT["HCL_la_vermelha"]
            for l, (jj, ii) in zip(f.loops, ((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1))):
                _, _, x, h = surf[jj][ii]
                l[uvl].uv = uv_top(x, h)
            new_faces[s].append(f)
    # walls: around the boundary, from the lapel face down into the coat (1 mm below its surface)
    ring = [(0, i) for i in range(NU + 1)] + [(j, NU) for j in range(1, NV + 1)] + \
           [(NV, i) for i in range(NU - 1, -1, -1)] + [(j, 0) for j in range(NV - 1, 0, -1)]
    feet = {}
    for jj, ii in ring:
        p, n, x, h = surf[jj][ii]
        feet[(jj, ii)] = bm.verts.new(p - n * 0.001)
    run = 0.0
    for a_, b_ in zip(ring, ring[1:] + ring[:1]):
        ta, tb = grid[a_[0]][a_[1]], grid[b_[0]][b_[1]]
        fa, fb = feet[a_], feet[b_]
        L = (tb.co - ta.co).length
        f = bm.faces.new((ta, fa, fb, tb))
        f[PL] = PART; f.material_index = MAT["HCL_la_vermelha"]
        wu = WALL_U[s]
        for l, uv in zip(f.loops, ((wu, 0.02 + run * DENS), (wu + 0.006, 0.02 + run * DENS),
                                   (wu + 0.006, 0.02 + (run + L) * DENS), (wu, 0.02 + (run + L) * DENS))):
            l[uvl].uv = uv
        run += L
        new_faces[s].append(f)
    # outward normals: the lapel face must point away from the coat
    for f in new_faces[s]:
        f.normal_update()
        c = f.calc_center_median()
        loc, nrm, _, _ = COAT.find_nearest(c)
        if f in new_faces[s][:NU * NV]:
            if f.normal.dot(nrm if nrm.y < 0 else -nrm) < 0:
                f.normal_flip()
        else:                                                  # wall: away from the lapel's middle
            if f.normal.dot(c - grid[NV // 2][NU // 2].co) < 0:
                f.normal_flip()
    # 7 buttons along the outer edge
    hs = np.linspace(h_top(sx * 0.07) - 0.030, H_BOT + 0.030, 7)
    for h in hs:
        x = sx * (width(h) - 0.013)
        p, n = coat_front(x, Z(h))
        btn_pos[s].append((p + n * OFF, n))
    print(f"LAPELA {s}: {NU}x{NV} faces + {len(ring)} paredes; altura {H_BOT:.3f}..{h_top(sx * 0.003):.3f} m; "
          f"largura {width(H_BOT) * 100:.1f}..{width(1.47) * 100:.1f} cm; UV {u0:.3f},{v0:.3f} + parede u {WALL_U[s]:.3f}; "
          f"comprimento das paredes {run:.2f} m (v ate {0.02 + run * DENS:.3f})")

# buttons: copies of the removed coat button, turned to the lapel normal
loc0, n0, _, _ = COAT.find_nearest(tmpl_c)
n0 = n0 if n0.y < 0 else -n0
base0 = loc0
nb = 0
for s in "ED":
    for p, n in btn_pos[s]:
        R = n0.rotation_difference(n).to_matrix()
        nv = [bm.verts.new(p + R @ (co - base0)) for co in tmpl_co]
        for idxs, uvs, mi in tmpl_data:
            f = bm.faces.new([nv[i] for i in idxs])
            f[PL] = PID["botoes"]; f.material_index = mi
            for l, uv in zip(f.loops, uvs):
                l[uvl].uv = uv
        nb += 1
print(f"BOTOES das lapelas: {nb}")

bm.normal_update()
bm.to_mesh(ob.data)
ob.data.update()
ob["hcl_partes"] = ",".join(parts)
ob["hcl_origem"] = "derivado de HCL_U_Pruss1813_01_LOD0 (gola v2) por build_uniforme_fr.py, 2026-10-12"
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print(f"UNIFORME FR: {len(ob.data.vertices)} vertices, {tris} triangulos (Res 1; o prussiano tem 11960 + gola)")
# checks: lapel UVs inside the atlas and not on other islands
uv = ob.data.uv_layers.active.data
lap = {PID["lapela_E"], PID["lapela_D"]}
pa = ob.data.attributes["hcl_part"].data
lu = [uv[li].uv[:] for p in ob.data.polygons if pa[p.index].value in lap for li in p.loop_indices]
print(f"UV lapelas: u {min(u for u, v in lu):.3f}..{max(u for u, v in lu):.3f}  v {min(v for u, v in lu):.3f}..{max(v for u, v in lu):.3f}")
other = [uv[li].uv[:] for p in ob.data.polygons if pa[p.index].value not in lap and parts[pa[p.index].value] != "maos_template"
         for li in p.loop_indices]
clash = sum(1 for u, v in other if u > 0.938 and v < 0.40)
print(f"UV de outras pecas na faixa das lapelas: {clash} cantos")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SALVO", OUT)
