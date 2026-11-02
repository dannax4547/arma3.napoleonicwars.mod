# Phase 3 (blockout / design model) of the Austrian infantry tschako of 1806, as worn in 1809: shapes and flat
# identification colours, NO UVs or final textures. Dossier: docs/research/aus/HIST-AUS-INF-TSCHAKO-1809-001.md
# (sources WS, EMB, NAP; decisions T1-T6). Spec: docs/specs/aus_1809.md 2.3, 8 (AT1, AT5 approved 2026-11-01).
#   blender -b --factory-startup --python blockout_tschako_aus.py -- <Test_Character_01 dir | -> <out.blend> <render dir>
# Head fit, profile maths and helpers are IMPORTED from blockout_kiver_rus.py (left untouched): the same fit read back
# from the approved British blockout while the Samples are missing.
#   - body: black cloth over leather, 208 mm (8 Zoll / 20.5 cm, T2), straight cone, top 26 mm wider (1", T3)
#   - crown: lacquered leather, sunk ~1/2" below the rim (EMB)
#   - black leather bands: top 2" (WS), bottom 20 mm (estimated)
#   - peaks: front 79 mm (3", WS), rear ~40 mm (EMB: peak front and back; size estimated, T4)
#   - front: yellow wool pompom with a black centre on the top edge, brass loop down to a brass button (WS, EMB; T5).
#     No plate (no source cites one before 1810)
#   - chin: plain black leather strap on small brass buttons (WS)
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import blockout_kiver_rus as K

TSCHAKO = dict(H=0.208, grow=0.013, dish=0.012, band_top=0.050, band_bot=0.020,
               visor_front=(0.079, 20.0, 84.0), visor_back=(0.040, 38.0, 70.0))
K.COL.update(amarelo=(0.85, 0.66, 0.08))


def peak(tag, root, a_c, half_span, length, drop):
    """Lacquered peak on the lower edge, centred on wall angle a_c (0 = front, pi = back), bound edge."""
    bm = bmesh.new()
    na = 48
    arc = [a_c + math.radians(-half_span + 2 * half_span * i / na) for i in range(na + 1)]
    dr = math.radians(drop)

    def vrow(off_len, dz):
        out = []
        for a in arc:
            n = K.wall_n(a, 0.0); n.z = 0; n.normalize()
            w = 1 - (abs(a - a_c) / math.radians(half_span)) ** 3
            out.append(K.P(a, 0.004, 0.002) + n * off_len * w * math.cos(dr) + Vector((0, 0, -off_len * w * math.sin(dr) + dz)))
        return out
    rows = [[bm.verts.new(p) for p in vrow(0.0, 0.0)], [bm.verts.new(p) for p in vrow(length * 0.5, 0.0012)],
            [bm.verts.new(p) for p in vrow(length, 0.0)], [bm.verts.new(p) for p in vrow(length, -0.0028)],
            [bm.verts.new(p) for p in vrow(length * 0.5, -0.0016)], [bm.verts.new(p) for p in vrow(0.0, -0.0028)]]
    K.grid(bm, rows, closed_u=False, closed_v=True)
    edge = [p.lerp(q, 0.5) for p, q in zip(vrow(length, 0.0), vrow(length, -0.0028))]
    K.finish(bm, f"{tag}_pala", "verniz", root, smooth=True)
    K.sweep(f"{tag}_pala_debrum", edge[2:-2], 0.0021, 0, "verniz", root, round_=True, segs=8, smooth=True)


def tschako(tag, x_off):
    K.N = 96
    H = TSCHAKO["H"] * K.k
    g_ = TSCHAKO["grow"] * K.k
    K.PRO.update(H=H, expo=1.0, side=g_, front=g_, back=g_, tan_s=0.0)
    root = bpy.data.objects.new(f"AUS_{tag}", None)
    root.matrix_world = Matrix.Translation(Vector((x_off, 0, 0))) @ K.ROOT
    K.scene.collection.objects.link(root)
    N = K.N
    # body: closed shell with wall thickness
    bm = bmesh.new()
    zs = [H * i / 12 for i in range(13)]
    outer = [[bm.verts.new(K.P(2 * math.pi * i / N, z)) for i in range(N)] for z in zs]
    inner = [[bm.verts.new(K.P(2 * math.pi * i / N, z, -K.WALL)) for i in range(N)] for z in zs[::3]]
    K.grid(bm, outer); K.grid(bm, [inner[0], outer[0]]); K.grid(bm, inner[::-1]); K.grid(bm, [outer[-1], inner[-1]])
    K.finish(bm, f"{tag}_corpo", "pano", root, smooth=True)
    # crown: lacquered leather, sunk below the rim
    bm = bmesh.new()
    rings = [[bm.verts.new(K.P(2 * math.pi * i / N, H, 0.0008)) for i in range(N)],
             [bm.verts.new(K.P(2 * math.pi * i / N, H, 0.0004) + Vector((0, 0, 0.0016))) for i in range(N)],
             [bm.verts.new(K.P(2 * math.pi * i / N, H, -0.0022) + Vector((0, 0, 0.0012))) for i in range(N)],
             [bm.verts.new(K.P(2 * math.pi * i / N, H - TSCHAKO["dish"], -0.0024)) for i in range(N)]]
    for f_ in (0.8, 0.5, 0.2):
        rings.append([bm.verts.new(K.P(2 * math.pi * i / N, H, 0.0, f_) - Vector((0, 0, TSCHAKO["dish"]))) for i in range(N)])
    K.grid(bm, rings)
    K.cap_ring(bm, rings[-1], K.P(0.0, H, 0.0, 0.0) - Vector((0, 0, TSCHAKO["dish"])))
    K.finish(bm, f"{tag}_topo", "verniz", root, smooth=True)
    # inside: sweatband and lining
    bm = bmesh.new()
    rows = [[bm.verts.new(K.P(2 * math.pi * i / N, z, -K.WALL - 0.0008)) for i in range(N)] for z in (0.001, 0.028, 0.055)]
    K.grid(bm, rows[::-1]); K.finish(bm, f"{tag}_suadouro", "couro_marrom", root, keep_normals=True)
    bm = bmesh.new()
    rows = [[bm.verts.new(K.P(2 * math.pi * i / N, z, -K.WALL - 0.0012)) for i in range(N)] for z in (0.053, H * 0.5, H - 0.006)]
    K.grid(bm, rows[::-1]); K.finish(bm, f"{tag}_forro", "forro", root, keep_normals=True)
    # bands
    K.lathe_band(f"{tag}_faixa_baixo", 0.0, TSCHAKO["band_bot"], 0.0018, "verniz", root)
    K.lathe_band(f"{tag}_faixa_cima", H - TSCHAKO["band_top"], H, 0.0018, "verniz", root, bead=True)
    # peaks
    L, d, s = TSCHAKO["visor_front"]; peak(tag, root, 0.0, s, L, d)
    L, d, s = TSCHAKO["visor_back"]; peak(f"{tag}_tras", root, math.pi, s, L, d)
    # pompom on the top edge, brass loop down to a brass button
    front_top = K.P(0, H, -0.008)
    n_top = K.wall_n(0.0, H * 0.95); n_top.z = 0; n_top.normalize()
    up_w = (Matrix.Rotation(K.TILT, 3, 'X') @ Vector((0, 0, 1))).normalized()
    K.pompom(tag, root, front_top + up_w * 0.030 + n_top * 0.010, n_top, up_w, "amarelo", "preto", seed=sum(map(ord, tag)))
    z_btn = H - 0.072
    lp = [K.P(0, H - 0.004 - (H - 0.004 - z_btn) * i / 10, 0.0024) for i in range(11)]
    K.sweep(f"{tag}_presilha", lp, 0.0055, 0.0008, "latao", root, normals=[K.wall_n(0, p.z) for p in lp])
    nb = K.wall_n(0.0, z_btn)
    K.lathe_obj(f"{tag}_botao", [(0, 0.0005), (0, 0.0080), (0.0015, 0.0078), (0.0030, 0.0060), (0.0038, 0.0005)],
                K.P(0.0, z_btn, 0.0030), "latao", root, axis=nb, segs=24)
    # chin strap: plain black leather on small brass buttons
    inv = root.matrix_world.inverted()
    chin_w = Matrix.Translation(Vector((x_off, 0, 0))) @ Vector((0.0, K.F["head_cy"] - K.F["head_hd"] * 0.62, 0.585))
    chin = inv @ chin_w
    for sgn in (1, -1):
        th = sgn * math.radians(95)
        ro = K.P(th, 0.030, 0.0028); nr = K.wall_n(th, 0.030)
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
    return root, H


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    samples, out_blend, render_dir = args[:3]
    out_blend, render_dir = os.path.abspath(out_blend), os.path.abspath(render_dir)
    os.makedirs(os.path.dirname(out_blend), exist_ok=True)
    K.setup(samples)
    root, H = tschako("tschako_1806", 0.0)
    bpy.context.view_layer.update()
    a_b, _, d_b = K.ring(0.0); a_t, _, d_t = K.ring(H)
    tris = sum(len(p.vertices) - 2 for o in K.PARTS for p in o.data.polygons)
    print(f"TSCHAKO k={K.k:.4f} altura {H * 1000:.0f} mm; base {2 * a_b * 1000:.0f} x {2 * d_b * 1000:.0f} mm; "
          f"topo {2 * a_t * 1000:.0f} x {2 * d_t * 1000:.0f} mm; pecas {len(K.PARTS)} triangulos {tris}")
    # approximate head (render and clearance only)
    hb = bmesh.new(); bmesh.ops.create_uvsphere(hb, u_segments=40, v_segments=20, radius=1.0)
    hme = bpy.data.meshes.new("REF_cabeca"); hb.to_mesh(hme); hb.free()
    for p in hme.polygons:
        p.use_smooth = True
    skin = bpy.data.materials.new("REF_pele"); skin.use_nodes = True
    skin.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.66, 0.55, 0.47, 1)
    hme.materials.append(skin)
    F = K.F
    h = bpy.data.objects.new("REF_cabeca_APROX_0", hme)
    h.scale = (F["head_hw"] - 0.006, F["head_hd"] - 0.004, (F["z_head_top"] - 0.57) / 2 - 0.004)
    h.location = (0.0, F["head_cy"], (F["z_head_top"] + 0.57) / 2)
    K.scene.collection.objects.link(h)
    bpy.context.view_layer.update()
    inv_h = h.matrix_world.inverted()
    obs = [o for o in K.PARTS if o.name.endswith(("_suadouro", "_corpo", "_forro"))]
    worst = min((inv_h @ (o.matrix_world @ v.co)).length for o in obs for v in o.data.vertices)
    print(f"FOLGA menor distancia normalizada parede/cabeca {worst:.3f} (> 1 = fora da cabeca aproximada)")
    # renders
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
    zc = (K.ROOT @ Vector((0, 0, 0.10))).z + 0.06

    def shot(name, loc, target, ortho=None, lens=60, res=(1000, 1100)):
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        cam.data.lens = lens
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = os.path.join(render_dir, f"blockout_tschako_aus_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("render", sc.render.filepath)

    cy = F["head_cy"]
    shot("frente", (0.0, -2.0, zc), (0.0, cy, zc), ortho=0.62)
    shot("lado", (-2.0, cy, zc), (0.0, cy, zc), ortho=0.62)
    shot("tres_quartos", (0.75, -1.1, zc + 0.35), (0.0, cy, zc - 0.02), lens=70, res=(1200, 1200))
    shot("costas", (0.5, 1.5, zc + 0.25), (0.0, cy, zc), lens=70, res=(1100, 1100))
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print("saved", out_blend)


if __name__ == "__main__":
    main()
