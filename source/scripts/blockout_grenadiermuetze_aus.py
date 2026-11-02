# Phase 3 (blockout / design model) of the Austrian grenadier fur cap, 1809: shapes and flat identification colours,
# NO UVs or final textures. Dossier: docs/research/aus/HIST-AUS-INF-TSCHAKO-1809-001.md section 2 (sources EMB, NAP,
# WS; decisions G1-G4). Spec: docs/specs/aus_1809.md 4, 8 (AT6 approved 2026-11-01).
#   blender -b --factory-startup --python blockout_grenadiermuetze_aus.py -- <Test_Character_01 dir | -> <out.blend> <render dir>
# Head fit and helpers are IMPORTED from blockout_kiver_rus.py (left untouched), like blockout_tschako_aus.py.
#   - fur body: 300 mm at the front falling to 125 mm at the back (NAP), slight bulge, fur roughness as a small
#     displacement (the real fur is a texture/normal-map matter in Phase 6)
#   - brass front plate, ~120 mm, arched top, raised centre boss standing in for the emblem (design unknown, G2)
#   - rear cloth patch (Lehnstuhlmuetzl) in the regiment's facing with white lace edging (EMB, G3): 4 variants
#   - yellow and black pompom on the wearer's right (EMB, G4)
#   - short lacquered front peak (EMB says two peaks; single source, only the front one is modelled)
#   - black leather chin strap on brass buttons (as the tschako)
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import blockout_kiver_rus as K
import blockout_tschako_aus as T

H_FRONT, H_BACK, P_EXP = 0.300, 0.125, 1.8  # convex crown: flat behind the front, falling to the back
PLATE = dict(z0=0.030, z1=0.150, half_w=0.052, arch=0.050)
PATCH = dict(half_ang=58.0, z0=0.045, lace=0.010)
K.COL.update(pele=(0.018, 0.016, 0.015), pompadour=(0.33, 0.04, 0.13), himmelblau=(0.40, 0.62, 0.86),
             kaisergelb=(0.90, 0.72, 0.10), ponceau=(0.80, 0.06, 0.04), amarelo=(0.85, 0.66, 0.08))
K.ROUGH.update(pele=0.97)
VARIANTS = [  # tag, facing colour (ACE): IR 1, IR 3 (German), IR 2, IR 39 (Hungarian)
    ("IR1_Kaiser", "pompadour"), ("IR3_ErzhKarl", "himmelblau"), ("IR2_Hiller", "kaisergelb"), ("IR39_Duka", "ponceau")]
SPACING = 0.45


def z_top(theta):
    """Top edge height: 300 mm at the front (theta 0), 125 mm at the back (pi)."""
    c = (1 + math.cos(theta)) / 2
    return (H_BACK + (H_FRONT - H_BACK) * (1 - (1 - c) ** P_EXP)) * K.k


def z_crown(theta, f):
    """Crown height at radial fraction f (1 = wall top): same front-to-back slope as z_top, no step inside the rim."""
    c = (1 + f * math.cos(theta)) / 2
    return (H_BACK + (H_FRONT - H_BACK) * (1 - (1 - c) ** P_EXP)) * K.k


def fur(theta, z, amp=0.0028):
    """Deterministic fur roughness (outward offset)."""
    return amp * (0.5 + 0.25 * math.sin(theta * 37 + z * 211) + 0.25 * math.sin(theta * 71 - z * 433 + 1.3))


def bulge(theta, t):
    return 0.010 * math.sin(math.pi * min(1.0, t)) * (0.6 + 0.4 * (1 + math.cos(theta)) / 2)


def wall_pt(theta, t, extra=0.0, with_fur=True):
    z = t * z_top(theta)
    return K.P(theta, z, bulge(theta, t) + (fur(theta, z) if with_fur else 0.0) + extra)


def muetze(tag, facing, x_off):
    K.N = 96
    N = K.N
    K.PRO.update(H=H_FRONT * K.k, expo=1.0, side=0.008 * K.k, front=0.004 * K.k, back=0.004 * K.k, tan_s=0.0)
    root = bpy.data.objects.new(f"AUS_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ K.ROOT
    K.scene.collection.objects.link(root)
    th = [2 * math.pi * i / N for i in range(N)]
    # fur body + top, one closed shell (inner wall plain)
    bm = bmesh.new()
    ts = [i / 20 for i in range(21)]
    outer = [[bm.verts.new(wall_pt(a, t)) for a in th] for t in ts]
    top = []
    for f_ in (0.82, 0.58, 0.32, 0.10):  # crown: the front-to-back slope of the wall top carried inward, slightly domed
        top.append([bm.verts.new(K.P(a, z_crown(a, f_), 0.0, f_) +
                                 Vector((0, 0, 0.018 * (1 - f_ ** 2) + fur(a, f_, 0.002)))) for a in th])
    inner = [[bm.verts.new(K.P(a, t * z_top(a) * 0.96, -K.WALL)) for a in th] for t in (0.0, 0.5, 1.0)]
    K.grid(bm, outer + top)
    K.cap_ring(bm, top[-1], K.P(0.0, z_crown(0.0, 0.0), 0.0, 0.0) + Vector((0, 0, 0.018)))
    K.grid(bm, [inner[0], outer[0]]); K.grid(bm, inner[::-1])
    K.cap_ring(bm, inner[-1][::-1], K.P(0.0, z_top(math.pi / 2) * 0.96, 0.0, 0.0))
    K.finish(bm, f"{tag}_pele", "pele", root, smooth=True)
    # sweatband
    bm = bmesh.new()
    rows = [[bm.verts.new(K.P(a, z, -K.WALL - 0.0008)) for a in th] for z in (0.001, 0.028, 0.050)]
    K.grid(bm, rows[::-1]); K.finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    # short front peak
    T.peak(tag, root, 0.0, 80.0, 0.045, 25.0)
    # brass plate conforming to the wall, arched top, two layers and a rim
    bm = bmesh.new()
    nz, nu = 18, 14
    z0, z1, W, arch = PLATE["z0"] * K.k, PLATE["z1"] * K.k, PLATE["half_w"] * K.k, PLATE["arch"] * K.k
    zs_ = z1 - arch

    def hw(z):
        return W if z <= zs_ else max(0.004, W * math.sqrt(max(0.0, 1 - ((z - zs_) / arch) ** 2)))

    def plate_pt(u, z, off):
        a_, _, _ = K.ring(z)
        t = z / z_top(0.0)
        return K.P(u * hw(z) / (a_ * 0.95), z, bulge(0.0, t) + 0.0045 + off)
    zz = [z0 + (z1 - z0) * j / nz for j in range(nz + 1)]
    uu = [-1 + 2 * i / nu for i in range(nu + 1)]
    Fr = [[bm.verts.new(plate_pt(u, z, 0.0016)) for u in uu] for z in zz]
    Bk = [[bm.verts.new(plate_pt(u, z, 0.0)) for u in uu] for z in zz]
    K.grid(bm, Fr, closed_u=False); K.grid(bm, [r[::-1] for r in Bk], closed_u=False)

    def perim(G):
        return G[0] + [G[j][-1] for j in range(1, nz + 1)] + G[-1][-2::-1] + [G[j][0] for j in range(nz - 1, 0, -1)]
    K.grid(bm, [perim(Fr), perim(Bk)])
    K.finish(bm, f"{tag}_placa", "latao", root, smooth=True)
    zc = (z0 + zs_) / 2 + 0.010
    nb = K.wall_n(0.0, zc)
    K.ellipsoid(f"{tag}_placa_emblema", plate_pt(0.0, zc, 0.0016), (nb.cross(Vector((0, 0, 1))).normalized(),
                Vector((0, 0, 1)), nb), (0.022, 0.030, 0.004), "latao", root, u=24, v=12)
    # rear cloth patch (Lehnstuhlmuetzl) on the back, white lace on its edges
    bm = bmesh.new()
    ha = math.radians(PATCH["half_ang"])
    angs = [math.pi - ha + 2 * ha * i / 24 for i in range(25)]
    t0 = PATCH["z0"] * K.k / z_top(math.pi)
    tt = [t0 + (0.985 - t0) * j / 10 for j in range(11)]
    Fr = [[bm.verts.new(wall_pt(a, t, 0.0050, False)) for a in angs] for t in tt]
    Bk = [[bm.verts.new(wall_pt(a, t, 0.0035, False)) for a in angs] for t in tt]
    K.grid(bm, Fr, closed_u=False); K.grid(bm, [r[::-1] for r in Bk], closed_u=False)
    K.finish(bm, f"{tag}_lehnstuhl", facing, root, smooth=True)
    lace_off = 0.0062
    edges = {"esq": [wall_pt(angs[0], t, lace_off, False) for t in tt],
             "dir": [wall_pt(angs[-1], t, lace_off, False) for t in tt],
             "baixo": [wall_pt(a, tt[0], lace_off, False) for a in angs],
             "cima": [wall_pt(a, tt[-1], lace_off, False) for a in angs]}
    for nm, pts in edges.items():
        nrm = [K.wall_n(a, p.z) for a, p in zip(angs if nm in ("baixo", "cima") else [angs[0] if nm == "esq" else angs[-1]] * len(pts), pts)]
        K.sweep(f"{tag}_galao_{nm}", pts, PATCH["lace"] / 2 * K.k, 0.0008, "branco", root, normals=nrm)
    # pompom on the wearer's right (-X), high on the side
    a_r = -math.radians(90)
    z_p = z_top(a_r) - 0.040
    n_r = K.wall_n(a_r, z_p); n_r.z = 0; n_r.normalize()
    up_w = (Matrix.Rotation(K.TILT, 3, 'X') @ Vector((0, 0, 1))).normalized()
    K.pompom(tag, root, K.P(a_r, z_p, bulge(a_r, z_p / z_top(a_r)) + 0.014), n_r, up_w, "amarelo", "preto",
             seed=sum(map(ord, tag)))
    # chin strap: as the tschako
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, K.F["head_cy"] - K.F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        a_ = sgn * math.radians(95)
        ro = wall_pt(a_, 0.030 / z_top(a_), 0.002, False); nr = K.wall_n(a_, 0.030)
        K.lathe_obj(f"{tag}_botao_jugular_{'E' if sgn > 0 else 'D'}",
                    [(0, 0.0005), (0, 0.0075), (0.0014, 0.0072), (0.0028, 0.0055), (0.0034, 0.0005)], ro, "latao", root,
                    axis=nr, segs=24)
        ro_w = root.matrix_world @ ro
        z_mid = (ro_w.z + chin_w.z) / 2
        hz = (K.F["z_head_top"] - 0.57) / 2 - 0.004; zc_h = (K.F["z_head_top"] + 0.57) / 2
        half_w = (K.F["head_hw"] - 0.006) * math.sqrt(max(0.0, 1 - ((z_mid - zc_h) / hz) ** 2))
        mid = inv @ Vector((x_off + sgn * (half_w + 0.010), K.F["head_cy"] - 0.012, z_mid))
        path = K.catmull([ro + nr * 0.004, mid, Vector((sgn * 0.035, chin.y, chin.z + 0.006)),
                          Vector((sgn * 0.0015, chin.y, chin.z))], 8)
        K.sweep(f"{tag}_jugular_{'E' if sgn > 0 else 'D'}", path, 0.008, 0.0008, "couro", root,
                normals=[Vector((p.x, p.y, 0)).normalized() for p in path])
    return root


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    samples, out_blend, render_dir = args[:3]
    out_blend, render_dir = os.path.abspath(out_blend), os.path.abspath(render_dir)
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    K.setup(samples)
    roots = [muetze(t, c, i * SPACING) for i, (t, c) in enumerate(VARIANTS)]
    bpy.context.view_layer.update()
    for (t, _), r in zip(VARIANTS, roots):
        obs = [o for o in K.PARTS if o.parent is r]
        tris = sum(len(p.vertices) - 2 for o in obs for p in o.data.polygons)
        print(f"MUETZE {t:14s} frente {z_top(0) * 1000:.0f} mm, tras {z_top(math.pi) * 1000:.0f} mm; pecas {len(obs)} triangulos {tris}")
    F = K.F
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
    hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
    for p in hme.polygons:
        p.use_smooth = True
    skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
    skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
    hme.materials.append(skin)
    heads = []
    for i in range(len(VARIANTS)):
        h = bpy.data.objects.new(f"REF_cabeca_APROX_{i}", hme)
        h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
        h.location = (i * SPACING, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
        K.scene.collection.objects.link(h); heads.append(h)
    bpy.context.view_layer.update()
    inv_h = heads[0].matrix_world.inverted()
    obs = [o for o in K.PARTS if o.parent is roots[0] and o.name.endswith(("_pele", "_suadouro"))]
    worst = min((inv_h @ (o.matrix_world @ v.co)).length for o in obs for v in o.data.vertices)
    print(f"FOLGA menor distancia normalizada parede/cabeca {worst:.3f} (> 1 = fora da cabeca aproximada)")
    sc = K.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    for nm, en, rot in (("sol", 3.0, (50, 0, 25)), ("preench", 1.2, (65, 0, 200)), ("contra", 1.0, (60, 0, 120))):
        lo = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN")); lo.data.energy = en
        lo.rotation_euler = tuple(math.radians(a) for a in rot); sc.collection.objects.link(lo)
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.80, 0.80, 1); sc.world = w
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 48
    sc.view_settings.view_transform = "Standard"
    os.makedirs(render_dir, exist_ok=True)
    zc = (K.ROOT @ Vector((0, 0, 0.12))).z + 0.04

    def shot(name, loc, target, ortho=None, lens=60, res=(1000, 1100)):
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = os.path.join(render_dir, f"blockout_grenadiermuetze_aus_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", sc.render.filepath)

    def solo(i):
        for j, r in enumerate(roots):
            for o in [o for o in K.PARTS if o.parent is r] + [heads[j]]:
                o.hide_render = j != i

    cy = F["head_cy"]
    mid_x = SPACING * (len(VARIANTS) - 1) / 2
    shot("fila_frente", (mid_x, -3.0, zc), (mid_x, 0, zc), ortho=SPACING * len(VARIANTS) + 0.10, res=(2000, 800))
    shot("fila_costas", (mid_x, 3.0, zc), (mid_x, 0, zc), ortho=SPACING * len(VARIANTS) + 0.10, res=(2000, 800))
    solo(0)
    shot("IR1_lado_direito", (-2.0, cy, zc), (0.0, cy, zc), ortho=0.70)
    shot("IR1_tres_quartos", (0.8, -1.2, zc + 0.35), (0.0, cy, zc - 0.02), lens=65, res=(1200, 1200))
    shot("IR1_costas_3-4", (-0.7, 1.3, zc + 0.35), (0.0, cy, zc - 0.02), lens=65, res=(1200, 1200))
    solo(-1)
    for o in K.PARTS + heads:
        o.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print("saved", out_blend)


if __name__ == "__main__":
    main()
