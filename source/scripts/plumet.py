# Feathered plume ("plumet", "Stutz") generator, shared by the French and Prussian shakos. A plume of the period is a
# dense column of cut cock feathers on a wire core: carrot-shaped, the feathers laid in overlapping tiers pointing up,
# their tips curling outwards and drooping a little, so the column looks full and soft. Built as: a tapered core
# (hidden under the feathers) + tiers of long, narrow, cupped feathers in a golden-angle spiral, each double-sided
# (Arma draws faces one-sided), twisted and splayed at random, a few loose feathers standing out of the silhouette,
# and a soft tuft closing the tip.
# v2 (2026-10-12, user: "de mais volume aos plumets"): fuller column (default radius 0.042 m carrot / 0.050 m Stutz,
# was 0.032 / 0.040; the carrot widens sooner, by 28 % of the height), more, longer and narrower feathers (26 tiers
# of up to 17, 0.075 m long, was 18 x 11 of 0.050 m) with pointed hackle tips splaying out to ~1.2x the envelope,
# 10 % loose feathers, a 10-feather tip tuft; 4 stations per feather (3 segments).
# v3 (2026-10-12, user: "traz mais realismo a pumlet ... como se fossem na quela epoca"): a period plumet is covered
# by MANY SHORT cut feathers whose soft tips curl away from the column, so it reads as a fluffy, slightly ragged
# column, not as tiers of long blades (v2 looked like a pine cone). Defaults now: 40 tiers of up to 21 feathers,
# 0.048 m long (max width ~0.21 x length), 3 stations (2 segments: half the triangles per feather of v2), lying
# along the column with only the tips curling out (splay 0.13..0.31 x envelope; v3 first try at 0.3..0.8 looked like
# grass), 7 % loose feathers, a ragged tip tuft.
# Every feather gets its own UV square (u across the vane, 0.5 = shaft; v from root to tip), so ONE feather texture
# (barbs, shaft, darker edges) serves all feathers; face float layer "tint" (0..1) varies each feather's shade.
#   from plumet import plumet
#   faces_by_colour = plumet(bm, base, H=0.30, colours=[(0.0, "verde"), (0.78, "amarelo")], seed=1)
# colours: list of (t_from, name) by height fraction t (0 = base, 1 = tip); the edge is jittered per feather.
import math, random
from mathutils import Vector, Matrix

R_DEFAULT = {"cenoura": 0.042, "stutz": 0.050}


def profile(t, R, shape="cenoura"):
    """Radius of the plume envelope at height fraction t."""
    if shape == "stutz":                    # short, full brush: wide early, blunt rounded top
        return R * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t / 0.35) / 2)) * (1 - t ** 4) ** 0.5
    return 0.20 * R + 0.92 * R * math.sin(math.pi * min(1.0, t / 0.28) / 2) * (1 - t) ** 0.75   # carrot (plumet)


def plumet(bm, base, H=0.30, R=None, colours=((0.0, "vermelho"),), seed=1, lean=0.035, shape="cenoura",
           rings=40, per_ring=21, feather_len=0.048, core_colour=None, fluff=1.0, estilo="v3"):
    """estilo="v4" (2026-10-13, user: "de mais realismo as pumlets"): every feather has 3 segments, a raised shaft
    with the two half-vanes in a shallow V (3 points across), a fine curled tip, and its underside only on the last
    segment (where the curled tip shows it); v3 = the flat double-sided 2-segment vanes of 2026-10-12."""
    R = R or R_DEFAULT[shape]
    rnd = random.Random(seed)
    up = Vector((0, 0, 1))
    uvl = bm.loops.layers.uv.verify()
    tint = bm.faces.layers.float.get("tint") or bm.faces.layers.float.new("tint")

    def spine(t):                           # gentle lean (feathers are not a turned post)
        return base + up * (H * t) + Vector((0.0, -lean * H * (t ** 2) * (1 - 0.5 * t), 0.0))

    def colour_at(t, jitter=0.0):
        name = colours[0][1]
        for t0, nm in colours:
            if t + jitter >= t0:
                name = nm
        return name

    out = {}

    def add(face, nm, uvs=None, shade=0.5):
        out.setdefault(nm, []).append(face)
        face.smooth = True
        face[tint] = shade
        if uvs:
            for l, uv in zip(face.loops, uvs):
                l[uvl].uv = uv

    # core: closed tapered post, 60 % of the envelope (only visible deep between the feathers)
    seg, nz = 10, 12
    rows = []
    for j in range(nz + 1):
        t = j / nz
        c = spine(t)
        r = 0.6 * profile(t, R, shape) if j < nz else 0.0008
        rows.append([bm.verts.new(c + Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0))) for i in range(seg)])
    for j in range(nz):
        for i in range(seg):
            f = bm.faces.new((rows[j][i], rows[j][(i + 1) % seg], rows[j + 1][(i + 1) % seg], rows[j + 1][i]))
            add(f, core_colour or colour_at(j / nz), shade=0.25)
    cb = bm.verts.new(spine(0.0))
    for i in range(seg):
        add(bm.faces.new((cb, rows[0][(i + 1) % seg], rows[0][i])), core_colour or colour_at(0.0), shade=0.25)

    V4 = estilo == "v4"
    S = [0.0, 0.35, 0.70, 1.0] if V4 else [0.0, 0.50, 1.0]   # stations along the feather (root .. tip)
    W = [0.45, 1.0, 0.72, 0.08] if V4 else [0.50, 1.0, 0.12]  # vane width profile (fine pointed tip)

    def feather(pts, wid, side, out_d, nm, shade):
        """Double-sided cupped vane through the given stations (root .. tip); UV u across, v along."""
        if V4:
            return feather_v4(pts, wid, side, out_d, nm, shade)
        front, back = [], []
        for p, hw, s_ in zip(pts, wid, S):
            cup = out_d * (0.35 * hw)                            # vane edges curl back towards the core
            front.append((bm.verts.new(p - side * hw - cup), bm.verts.new(p + side * hw - cup), s_))
            back.append((bm.verts.new(p - side * hw - cup - out_d * 0.0004), bm.verts.new(p + side * hw - cup - out_d * 0.0004), s_))
        for k in range(len(pts) - 1):
            (a0, b0, s0), (a1, b1, s1) = front[k], front[k + 1]
            add(bm.faces.new((a0, b0, b1, a1)), nm, [(0.0, s0), (1.0, s0), (1.0, s1), (0.0, s1)], shade)
            (c0, d0, _), (c1, d1, _) = back[k], back[k + 1]
            add(bm.faces.new((c1, d1, d0, c0)), nm, [(0.0, s1), (1.0, s1), (1.0, s0), (0.0, s0)], shade)

    def feather_v4(pts, wid, side, out_d, nm, shade):
        """Raised shaft + two half-vanes curling back at the edges; underside on the last segment only."""
        rows, under = [], []
        for k, (p, hw, s_) in enumerate(zip(pts, wid, S)):
            cup = out_d * (0.40 * hw)
            shaft = p + out_d * (0.16 * hw)
            rows.append((bm.verts.new(p - side * hw - cup), bm.verts.new(shaft), bm.verts.new(p + side * hw - cup), s_))
            if k >= len(pts) - 2:
                o = -out_d * 0.0004
                under.append((bm.verts.new(p - side * hw - cup + o), bm.verts.new(shaft + o), bm.verts.new(p + side * hw - cup + o), s_))
        for k in range(len(rows) - 1):
            (a0, m0, b0, s0), (a1, m1, b1, s1) = rows[k], rows[k + 1]
            add(bm.faces.new((a0, m0, m1, a1)), nm, [(0.0, s0), (0.5, s0), (0.5, s1), (0.0, s1)], shade)
            add(bm.faces.new((m0, b0, b1, m1)), nm, [(0.5, s0), (1.0, s0), (1.0, s1), (0.5, s1)], shade)
        (a0, m0, b0, s0), (a1, m1, b1, s1) = under
        add(bm.faces.new((m1, a1, a0, m0)), nm, [(0.5, s1), (0.0, s1), (0.0, s0), (0.5, s0)], shade)
        add(bm.faces.new((b1, m1, m0, b0)), nm, [(1.0, s1), (0.5, s1), (0.5, s0), (1.0, s0)], shade)

    # feathers: root on the core, laid along the column a tier or two up, the tip splaying out and drooping
    golden = math.pi * (3 - math.sqrt(5))
    for j in range(rings):
        t = 0.02 + 0.92 * (j / (rings - 1)) ** 0.9
        n_here = max(6, int(round(per_ring * (0.40 + 0.60 * profile(t, R, shape) / R))))
        for q in range(n_here):
            phi = 2 * math.pi * q / n_here + j * golden + rnd.uniform(-0.2, 0.2)
            tj = min(0.96, t + rnd.uniform(-0.012, 0.012))
            out_d = Vector((math.cos(phi), math.sin(phi), 0.0))
            side = Vector((-math.sin(phi), math.cos(phi), 0.0))
            side = Matrix.Rotation(rnd.uniform(-0.45, 0.45), 3, out_d) @ side       # twist about the radius
            loose = rnd.random() < 0.07 * fluff
            L = feather_len * rnd.uniform(0.85, 1.15) * (0.7 if tj > 0.85 else 1.0) * (0.8 if shape == "stutz" else 1.0)
            L *= 1.35 if loose else 1.0
            w = (0.13 + 0.08 * profile(tj, R, shape) / R) * L * rnd.uniform(0.80, 1.15)
            splay = (0.08 + 0.14 * fluff) * rnd.uniform(0.6, 1.4) * (2.2 if loose else 1.0)
            droop = 0.22 * L * rnd.uniform(0.4, 1.3) * (1.6 if loose else 1.0)
            pts, wid = [], []
            twist = rnd.uniform(-0.25, 0.25) * L if V4 else 0.0            # v4: the tip curls a little sideways
            for s_, wf in zip(S, W):
                ts = min(1.0, tj + s_ * L / H)
                env = profile(ts, R, shape)
                r = (0.66 + 0.36 * min(1.0, s_ / 0.45)) * env + splay * env * s_ ** 2
                p = spine(ts) + out_d * r - up * (droop * s_ ** 3) + side * (twist * s_ ** 3)
                pts.append(p)
                wid.append(w * wf / 2)
            nm = colour_at(tj + (L / H) * 0.6, rnd.uniform(-0.03, 0.03))
            feather(pts, wid, side, out_d, nm, rnd.uniform(0.0, 1.0))
    # soft pointed tip: a tuft of feathers rising from the last tiers and meeting above the column
    n_tip = 18
    apex = spine(1.0) + up * (0.035 * H)
    for q in range(n_tip):
        t0 = rnd.uniform(0.82, 0.90)
        phi = 2 * math.pi * q / n_tip + rnd.uniform(-0.2, 0.2)
        out_d = Vector((math.cos(phi), math.sin(phi), 0.0))
        side = Vector((-math.sin(phi), math.cos(phi), 0.0))
        root = spine(t0) + out_d * 0.75 * profile(t0, R, shape)
        tip = apex + out_d * rnd.uniform(0.0, 0.012) + Vector((rnd.uniform(-0.006, 0.006), rnd.uniform(-0.006, 0.006), rnd.uniform(-0.018, 0.0)))
        pts = [root.lerp(tip, s_) + out_d * (0.008 * math.sin(math.pi * s_)) for s_ in S]
        w = 0.17 * feather_len
        feather(pts, [w * wf / 2 for wf in W], side, out_d, colour_at(1.0), rnd.uniform(0.0, 1.0))
    return out


def feather_material(mat, base_rgb):
    """Preview shader for a plume colour: barbs angled from the shaft, darker shaft line and vane edges, per-feather
    shade from the 'tint' face attribute. The same pattern is painted into the game texture later (Phase 6)."""
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.type not in ("OUTPUT_MATERIAL", "BSDF_PRINCIPLED"):
            nt.nodes.remove(n)
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.75
    uv = nt.nodes.new("ShaderNodeUVMap")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs["Vector"])
    M = lambda op, a=None, b=None, c=None: _math(nt, op, a, b, c)
    du = M("SUBTRACT", sep.outputs["X"], 0.5)
    adu = M("ABSOLUTE", du)
    barbs = M("SINE", M("SUBTRACT", M("MULTIPLY", adu, 70.0), M("MULTIPLY", sep.outputs["Y"], 55.0)))
    barbs01 = M("MULTIPLY_ADD", barbs, 0.5, 0.5)
    shaft = M("LESS_THAN", adu, 0.045)
    edge = M("GREATER_THAN", adu, 0.42)
    att = nt.nodes.new("ShaderNodeAttribute"); att.attribute_name = "tint"; att.attribute_type = "GEOMETRY"
    shade = M("MULTIPLY_ADD", att.outputs["Fac"], 0.35, 0.80)            # 0.80 .. 1.15
    f = M("MULTIPLY", M("MULTIPLY_ADD", barbs01, 0.30, 0.70), shade)
    f = M("MULTIPLY", f, M("MULTIPLY_ADD", shaft, -0.25, 1.0))
    f = M("MULTIPLY", f, M("MULTIPLY_ADD", edge, -0.30, 1.0))
    rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = (*base_rgb, 1)
    mix = nt.nodes.new("ShaderNodeVectorMath"); mix.operation = "SCALE"
    nt.links.new(rgb.outputs[0], mix.inputs[0]); nt.links.new(f, mix.inputs["Scale"])
    nt.links.new(mix.outputs["Vector"], bsdf.inputs["Base Color"])
    bsdf.inputs["Sheen Weight"].default_value = 0.4 if "Sheen Weight" in bsdf.inputs else 0.0


def _math(nt, op, a, b, c=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]
