# Austrian line infantry coat 1809 (Phase 3), German and Hungarian, derived from the validated Prussian 1813 production
# mesh like the Russian coat (build_uniforme_rus.py, whose tail method is copied here; that script is left untouched).
# The Russian mesh itself is not the base: its front edge was moved out for the double-breasted front, while the
# Austrian coat is single-breasted like the Prussian one. Spec: docs/specs/aus_1809.md 2, 3, 5, 8 (AT7, AT8, AT10).
# Dossier: docs/research/aus/HIST-AUS-INF-COAT-1809-001.md (A1-A5). Changes:
#   1. tails: hem 0.70 -> 0.74 m, the Russian 400 mm until a source is found (spec 8, F1), re-draped the same way
#   2. front: the 14 Prussian buttons -> ONE row of 8, closed to the waist (WS, A1); first 22 mm under the collar foot,
#      last at the waist (h 1.158, as on the Russian coat); the row sits on the overlapping front 12 mm inside its edge
#   3. cuffs: the Prussian flap and its buttons removed. German: plain round cuff (A2, unsourced). Hungarian: the cuff
#      top rises to a point on the outside of the forearm (A3, unsourced); the "bear's paw" lace is painted (Phase 6)
#   4. legs. German: white trousers with the short black gaiters already modelled (A4). Hungarian: no gaiters (A5): the
#      gaiter shells become the lower trouser legs (tight, into short boots), their buttons go, and the leg above the
#      old gaiter top comes out flush with it (the Russian knee-high gaiter code, copied)
#   Collar: the Prussian collar v2 is kept (77 mm at the front; F4, no source). No new topology except the 8 buttons.
#   blender -b --factory-startup --python build_uniforme_aus.py -- <prussian LOD0 .blend> <out dir> <render dir>
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT_DIR, RENDER_DIR = [os.path.abspath(x) for x in a[:3]]
TAIL_HEM = 0.74
N_BTN, FIRST, LAST_H = 8, 0.022, 1.158
INSIDE = 0.012                                          # button centres inside the overlapping edge
POINT = 0.070                                           # Hungarian cuff: height of the point above the round top
POINT_HALF = math.radians(60)                           # ... and its half-width around the forearm
GROUND = -1.0069
Z = lambda h: GROUND + h
VARIANTS = {"alema": "HCL_U_AUS1809_Alema_LOD0", "hungara": "HCL_U_AUS1809_Hungara_LOD0"}


def build(variant):
    with bpy.data.libraries.load(SRC, link=False) as (src, dst):
        dst.objects = ["HCL_U_Pruss1813_01_LOD0"]
    ob = dst.objects[0]
    bpy.context.scene.collection.objects.link(ob)
    ob.name = VARIANTS[variant]
    ob.data = ob.data.copy(); ob.data.name = ob.name
    parts = ob["hcl_partes"].split(",")
    PID = {n: i for i, n in enumerate(parts)}
    bm = bmesh.new(); bm.from_mesh(ob.data)
    PL = bm.faces.layers.int.get("hcl_part")
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
        return BVHTree.FromPolygons([v.co.copy() for v in vs], tris)

    def centre(comp):
        return sum((v.co for v in comp), Vector()) / len(comp)

    def sstep(e0, e1, x):
        t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
        return t * t * (3 - 2 * t)

    log = []
    # ------------------------------------------------------------ 1. tails (build_uniforme_rus.py section 1, copied)
    TOP = 1.14
    k = (TOP - TAIL_HEM) / (TOP - 0.70)
    AX = Vector((0.0, 0.02, 0.0))
    vp = vparts()
    tail_v = [v for v in bm.verts if vp.get(v, set()) & {PID["aba_E"], PID["aba_D"]}]
    TR = tri_bvh({PID["calca_assento"], PID["calca_perna_E"], PID["calca_perna_D"]})

    def trousers_r(phi, z):
        d = Vector((math.sin(phi), math.cos(phi), 0.0))
        o = Vector((AX.x, AX.y, z)) + d * 0.6
        hit = TR.ray_cast(o, -d, 0.6)
        return None if hit[0] is None else (hit[0] - Vector((AX.x, AX.y, z))).to_2d().length

    new_co = {}
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
            continue
        rr = r1 + min(max(q.length - r0, 0.004), 0.025)
        new_co[v] = Vector((AX.x + math.sin(phi) * rr, AX.y + math.cos(phi) * rr, z1))
    disp = {v: new_co[v] - v.co for v in new_co}
    for _ in range(4):
        nd = {}
        for v, d_ in disp.items():
            nb = [disp[e.other_vert(v)] for e in v.link_edges if e.other_vert(v) in disp]
            nd[v] = d_ * 0.5 + (sum(nb, Vector()) / len(nb)) * 0.5 if nb else d_
        disp = nd
    for v, d_ in disp.items():
        v.co = v.co + d_
    for comp in components(PID["botoes"]):
        c = centre(comp)
        if Z(0.60) < c.z < Z(TOP) and abs(c.x) < 0.30:
            dz = (Z(TOP) - (Z(TOP) - c.z) * k) - c.z
            for v in comp:
                v.co.z += dz
    log.append(f"ABAS: barra {min(v.co.z for v in tail_v) - GROUND:.3f} m (fator {k:.3f})")

    # ------------------------------------------------------------ 2. front: one row of 8 (A1)
    uvl = bm.loops.layers.uv.active
    front = [(centre(c), c) for c in components(PID["botoes"])]
    front = [t for t in front if abs(t[0].x) < 0.03 and t[0].y < -0.05 and Z(1.15) < t[0].z < Z(1.50)]
    assert len(front) == 14, f"frente prussiana: {len(front)} botoes (esperados 14)"
    tc, tcomp = min(front, key=lambda t: abs(t[0].z - Z(1.335)) + (0 if t[0].x > 0 else 1))
    tmpl_faces = {f for v in tcomp for f in v.link_faces}
    tmpl_data = [([tcomp.index(x) for x in f.verts], [l[uvl].uv.copy() for l in f.loops], f.material_index)
                 for f in tmpl_faces]
    tmpl_co = [v.co.copy() for v in tcomp]
    bmesh.ops.delete(bm, geom=list({v for _, comp in front for v in comp}), context="VERTS")
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    COAT = tri_bvh({PID["casaco_corpo"]})
    loc0, n0, _, _ = COAT.find_nearest(tc)
    n0 = n0 if n0.y < 0 else -n0

    def place_button(p, n):
        R = n0.rotation_difference(n).to_matrix()
        nv = [bm.verts.new(p + n * 0.0008 + R @ (co - loc0)) for co in tmpl_co]
        for idxs, uvs, mi in tmpl_data:
            f = bm.faces.new([nv[i] for i in idxs])
            f[PL] = PID["botoes"]; f.material_index = mi
            for l, uv in zip(f.loops, uvs):
                l[uvl].uv = uv

    # the overlapping front: the Prussian closure step (x -0.025 at the chest) stands 1.8 mm over the other front
    def front_y(x, z):
        hit = COAT.ray_cast(Vector((x, -0.6, z)), Vector((0, 1, 0)), 1.0)
        return hit[0].y if hit[0] is not None else 0.0
    zc = Z(1.33)
    side = 1 if front_y(-0.015, zc) < front_y(-0.035, zc) else -1     # +1: the raised panel lies at x > edge
    EDGE = -0.025
    row_x = EDGE + side * INSIDE
    vp = vparts()
    gola_foot = min(v.co.z for v in bm.verts if PID["gola"] in vp.get(v, ()) and v.co.y < 0.0 and abs(v.co.x) < 0.02)
    z0 = gola_foot - FIRST
    pitch = (z0 - Z(LAST_H)) / (N_BTN - 1)
    btn_list = []
    for i in range(N_BTN):
        z = z0 - pitch * i
        hit = COAT.ray_cast(Vector((row_x, -0.6, z)), Vector((0, 1, 0)), 1.0)
        assert hit[0] is not None, f"casaco nao encontrado em h {z - GROUND:.3f}"
        n = hit[1] if hit[1].y < 0 else -hit[1]
        place_button(hit[0], n.normalized())
        btn_list.append([round(hit[0].x, 5), round(hit[0].y, 5), round(hit[0].z, 5)])
    log.append(f"FRENTE: 14 botoes prussianos -> 1 fileira de {N_BTN} em x {row_x:+.3f} (painel por cima do lado "
               f"{'+x' if side > 0 else '-x'}); passo {pitch * 1000:.1f} mm; h {z0 - GROUND:.3f}..{LAST_H:.3f}")

    # ------------------------------------------------------------ 3. cuffs: flap and cuff buttons out; Hungarian point
    cuff_c = {}
    for s_ in "ED":
        vp = vparts()
        cv = [v for v in bm.verts if PID[f"punho_{s_}"] in vp.get(v, ())]
        cuff_c[s_] = sum((v.co for v in cv), Vector()) / len(cv)
    flap = [f for f in bm.faces if f[PL] in (PID["pala_E"], PID["pala_D"])]
    fv = {v for f in flap for v in f.verts}
    vp = vparts()
    only_flap = [v for v in fv if vp[v] <= {PID["pala_E"], PID["pala_D"]}]
    bmesh.ops.delete(bm, geom=flap, context="FACES_ONLY")
    bmesh.ops.delete(bm, geom=[v for v in only_flap if v.is_valid and not v.link_faces], context="VERTS")
    cbtn = [c for c in components(PID["botoes"]) if min((centre(c) - cc).length for cc in cuff_c.values()) < 0.12]
    bmesh.ops.delete(bm, geom=list({v for c in cbtn for v in c}), context="VERTS")
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    log.append(f"PUNHOS: palas removidas ({len(flap)} faces) e {len(cbtn)} botoes dos punhos")
    for s_, sx in (("E", 1), ("D", -1)):
            vp = vparts()
            cv = [v for v in bm.verts if PID[f"punho_{s_}"] in vp.get(v, ())]
            mv = [v for v in bm.verts if PID[f"manga_{s_}"] in vp.get(v, ())]
            c0 = sum((v.co for v in cv), Vector()) / len(cv)
            near = np.array([list(v.co) for v in mv if (v.co - c0).length < 0.16] + [list(v.co) for v in cv])
            w, U = np.linalg.eigh(np.cov((near - near.mean(0)).T))
            ax = Vector(U[:, -1]).normalized()
            ax = ax if ax.z > 0 else -ax                               # towards the shoulder
            out = Vector((sx, 0.0, 0.0)); out = (out - ax * out.dot(ax)).normalized()   # back of the forearm
            ob[f"hcl_punho_{s_}"] = [*c0, *out]                        # for the renders and the painter
            if variant != "hungara":
                continue
            SL = tri_bvh({PID[f"manga_{s_}"]})

            def sleeve_r(t, d):
                o = c0 + ax * t
                hit = SL.ray_cast(o + d * 0.2, -d, 0.2)
                return None if hit[0] is None else (hit[0] - o).length
            ts = [(v.co - c0).dot(ax) for v in cv]
            tmin, tmax = min(ts), max(ts)
            moved = 0
            for v, t in zip(cv, ts):
                q = v.co - c0 - ax * t
                r = q.length
                if r < 1e-6:
                    continue
                d = q / r
                phi = math.acos(max(-1.0, min(1.0, d.dot(out))))
                wv = max(0.0, 1.0 - phi / POINT_HALF)                 # V point on the back of the forearm
                f = (t - tmin) / (tmax - tmin)
                dt = POINT * f * wv
                if dt <= 1e-5:
                    continue
                rs0, rs1 = sleeve_r(t, d), sleeve_r(t + dt, d)
                r1 = r if rs0 is None or rs1 is None else rs1 + max(r - rs0, 0.0015)
                v.co = c0 + ax * (t + dt) + d * r1
                moved += 1
            log.append(f"PUNHO HUNGARO {s_}: ponta de {POINT * 1000:.0f} mm no lado de fora; {moved} vertices")

    # ------------------------------------------------------------ 4. Hungarian: no gaiters (A5)
    if variant == "hungara":
        gb = [c for c in components(PID["botoes"]) if centre(c).z < Z(0.45)]
        bmesh.ops.delete(bm, geom=list({v for c in gb for v in c}), context="VERTS")
        bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        vp = vparts()
        CUT = 0.390                                      # the gaiter shell above the trouser bottom (its turned
        top = [f for f in bm.faces if f[PL] in (PID["polaina_E"], PID["polaina_D"])   # hem) lies under the leg:
               and min(v.co.z for v in f.verts) > Z(CUT) - 0.002]                     # removed, no double surface
        bmesh.ops.delete(bm, geom=top, context="FACES")
        bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        vp = vparts()
        hem = len(top)
        unb = 0
        for s_ in "ED":                                  # build_uniforme_rus.py 4b: the bunching over the gaiter out
            LV = [v for v in bm.verts if PID[f"calca_perna_{s_}"] in vp.get(v, ())]
            for v in LV:
                h = v.co.z - GROUND
                bump = 0.0075 * sstep(0.415, 0.43, h) * (1 - sstep(0.47, 0.50, h))
                if bump <= 0:
                    continue
                ring = [u.co for u in LV if abs(u.co.z - v.co.z) < 0.004]
                c = sum(ring, Vector()) / len(ring)
                d = Vector((v.co.x - c.x, v.co.y - c.y, 0.0))
                if d.length < 1e-6:
                    continue
                v.co = v.co - d.normalized() * bump
                unb += 1
        H_LO, H_FULL, H_END = 0.386, 0.40, 0.48          # the leg's bottom ring wraps the gaiter's new top ring,
        flush = 0                                        # then eases back to the leg by h 0.48
        for s_ in "ED":
            LV = [v for v in bm.verts if PID[f"calca_perna_{s_}"] in vp.get(v, ())]
            GAIT = tri_bvh({PID[f"polaina_{s_}"]})             # this leg's gaiter only
            ref = [u.co for u in LV if abs(u.co.z - Z(0.43)) < 0.006] or [u.co for u in LV]
            c0 = sum(ref, Vector()) / len(ref)
            zr = Z(CUT) - 0.006
            for v in LV:
                h = v.co.z - GROUND
                if not (H_LO <= h < H_END):
                    continue
                d = Vector((v.co.x - c0.x, v.co.y - c0.y, 0.0))
                if d.length < 1e-6:
                    continue
                d.normalize()
                o = Vector((c0.x, c0.y, zr))
                hit = GAIT.ray_cast(o + d * 0.15, -d, 0.15)
                if hit[0] is None:
                    continue
                rg = (hit[0] - o).to_2d().length + 0.0010
                r = Vector((v.co.x - c0.x, v.co.y - c0.y)).length
                wv = 1.0 - sstep(H_FULL, H_END, h)
                if h < H_FULL or rg > r:                     # bottom ring: exactly on the gaiter; above: only outwards
                    v.co = v.co + d * (rg - r) * wv
                    flush += 1
        n_g = 0
        for f in bm.faces:                               # the gaiter shells are now the lower trouser legs
            for s_ in "ED":
                if f[PL] == PID[f"polaina_{s_}"]:
                    f[PL] = PID[f"calca_perna_{s_}"]; n_g += 1
        log.append(f"PERNAS HUNGARAS: {len(gb)} botoes das polainas removidos; {hem} faces da bainha das polainas removidas, "
                   f"franzido desfeito em {unb} e perna "
                   f"rente em {flush} vertices; {n_g} faces das polainas viram calca")

    bm.normal_update()
    bm.to_mesh(ob.data)
    ob.data.update()
    ob["hcl_partes"] = ",".join(parts)
    ob["hcl_botoes_frente"] = json.dumps({"estilo": "simples_8", "botoes": btn_list})
    ob["hcl_variante"] = variant
    ob["hcl_origem"] = f"derivado de HCL_U_Pruss1813_01_LOD0 (gola v2) por build_uniforme_aus.py, 2026-11-01"
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    log.append(f"UNIFORME AUS {variant}: {len(ob.data.vertices)} vertices, {tris} triangulos")
    for line in log:
        print(line)
    return ob


# ---------------------------------------------------------------- materials, renders
COL = dict(branco=(0.86, 0.85, 0.80), branco_calca=(0.88, 0.87, 0.82), azul_claro=(0.42, 0.58, 0.82),
           preto=(0.03, 0.03, 0.03), couro=(0.05, 0.04, 0.03), latao=(0.85, 0.66, 0.25), estanho=(0.78, 0.79, 0.80),
           pele=(0.66, 0.55, 0.47), pompadour=(0.33, 0.04, 0.13), himmelblau=(0.40, 0.62, 0.86),
           kaisergelb=(0.90, 0.72, 0.10), ponceau=(0.80, 0.06, 0.04))
REGIMENTS = [("IR1_Kaiser", "alema", "pompadour", "latao"), ("IR3_ErzhKarl", "alema", "himmelblau", "estanho"),
             ("IR2_Hiller", "hungara", "kaisergelb", "latao"), ("IR39_Duka", "hungara", "ponceau", "estanho")]
SPACING = 1.0


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (*COL[name], 1)
    metal = name in ("latao", "estanho")
    bs.inputs["Metallic"].default_value = 1.0 if metal else 0.0
    bs.inputs["Roughness"].default_value = 0.35 if metal else 0.85
    return m


def paint(ob, variant, facing, metal):
    parts = ob["hcl_partes"].split(",")
    role = {}
    for n in parts:
        if n.startswith(("casaco", "manga", "aba")):
            role[n] = "branco"
        elif n.startswith(("gola", "punho", "platina", "pala")):
            role[n] = facing
        elif n.startswith("calca"):
            role[n] = "branco_calca" if variant == "alema" else "azul_claro"
        elif n.startswith("polaina"):
            role[n] = "preto"
        elif n.startswith("sapato"):
            role[n] = "couro"
        elif n == "botoes":
            role[n] = metal
        else:
            role[n] = "pele"
    names = sorted(set(role.values()))
    me = ob.data
    me.materials.clear()
    for n in names:
        me.materials.append(mat(n))
    a_ = me.attributes["hcl_part"].data
    for p in me.polygons:
        p.material_index = names.index(role[parts[a_[p.index].value]])


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base = {v: build(v) for v in VARIANTS}
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = bpy.context.scene
    for v, ob in base.items():                           # one clean .blend per variant (Prussian materials kept)
        path = os.path.join(OUT_DIR, f"hcl_uniforme_aus_{v}_LOD0.blend")
        bpy.data.libraries.write(path, {ob}, fake_user=True)
        print("SALVO", path)
    figs = []
    for i, (tag, v, facing, metal) in enumerate(REGIMENTS):
        o = base[v].copy(); o.data = base[v].data.copy(); o.name = f"AUS_{tag}"
        sc.collection.objects.link(o)
        o.location.x = (i - 1.5) * SPACING
        paint(o, v, facing, metal)
        figs.append(o)
    for ob in base.values():
        ob.hide_render = True
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    for nm, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
        lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); lo.data.energy = en
        lo.rotation_euler = tuple(math.radians(x) for x in rot); sc.collection.objects.link(lo)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); sc.world = w
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 48
    sc.view_settings.view_transform = "Standard"
    os.makedirs(RENDER_DIR, exist_ok=True)

    def shot(name, loc, target, ortho, res):
        cam.data.type = "ORTHO"; cam.data.ortho_scale = ortho
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = os.path.join(RENDER_DIR, f"blockout_uniforme_aus_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", sc.render.filepath)

    zm = Z(0.85)
    shot("fila_frente", (0, -6, zm), (0, 0, zm), 4.2, (2000, 1000))
    shot("fila_costas", (0, 6, zm), (0, 0, zm), 4.2, (2000, 1000))
    for i, nm in ((0, "IR1"), (2, "IR2")):              # wearer's left cuff, from the back of the forearm, and legs
        x0 = figs[i].location.x
        q = figs[i]["hcl_punho_E"]
        c, out = Vector(q[:3]) + Vector((x0, 0, 0)), Vector(q[3:])
        for j, o in enumerate(figs):
            o.hide_render = j != i
        shot(f"punho_{nm}", tuple(c + out * 1.5 + Vector((0, -0.6, 0))), tuple(c), 0.36, (900, 900))
        for o in figs:
            o.hide_render = False
        shot(f"pernas_{nm}", (x0 + 1.4, -2.4, Z(0.45)), (x0, 0.0, Z(0.45)), 1.1, (900, 1000))


if __name__ == "__main__":
    main()
