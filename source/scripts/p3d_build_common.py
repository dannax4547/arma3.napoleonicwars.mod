# Shared LOD builders for the editable P3D (MLOD) test models, taken unchanged from build_p3d_pruss.py (which keeps its
# own verified copy). Used by build_p3d_fr.py. Blender only supplies meshes and weights; p3d_mlod_io.py writes the file.
import bpy, os, struct
from p3d_mlod_io import parse, write, tag, weight_byte, get_tag


def append(path, names):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in names]
    return list(dst.objects)


def to_p3d(v):
    return (v[0], v[2], v[1])                       # inverse of p3d_mlod.to_blender (y and z swapped)


def lod_from_mesh(ob, res, props, face_tex, sel_extra, weights=True, uv=True):
    """ob: Blender mesh object (rest pose, character space). face_tex(poly_index) -> (texture, material).
    sel_extra: {name: set(poly_index)} extra named selections (points = points of those faces)."""
    me = ob.data
    me.calc_loop_triangles()
    cn = me.corner_normals
    uvl = me.uv_layers.active.uv if (uv and me.uv_layers.active) else None
    pts = [to_p3d(v.co) + (0,) for v in me.vertices]
    nidx, normals, faces, fpoly = {}, [], [], []
    for t in me.loop_triangles:
        verts = []
        for li, vi in zip(t.loops, t.vertices):
            n = cn[li].vector
            key = (round(-n.x, 5), round(-n.z, 5), round(-n.y, 5))        # P3D stores the normal of the stored order
            if key not in nidx:
                nidx[key] = len(normals); normals.append(key)
            u, v = (uvl[li].vector.x, 1.0 - uvl[li].vector.y) if uvl else (0.0, 0.0)
            verts.append((vi, nidx[key], u, v))
        verts.append((0, 0, 0.0, 0.0))
        tex, mat = face_tex(t.polygon_index)
        faces.append({"n": 3, "verts": verts, "flags": 0, "tex": tex.encode("latin-1"), "mat": mat.encode("latin-1")})
        fpoly.append(t.polygon_index)
    np_, nf = len(pts), len(faces)
    sels = {}
    if weights:
        names = {g.index: g.name for g in ob.vertex_groups}
        pb = {}
        for v in me.vertices:
            for g in v.groups:
                if g.weight > 0:
                    pb.setdefault(names[g.group], {})[v.index] = weight_byte(g.weight)
        for name, d in pb.items():
            fb = [k for k, f in enumerate(faces) if all(x[0] in d for x in f["verts"][:3])]
            sels[name] = (d, fb)
    for name, polys in sel_extra.items():
        fb = [k for k in range(nf) if fpoly[k] in polys]
        d = {x[0]: 1 for k in fb for x in faces[k]["verts"][:3]}
        sels[name] = (d, fb)
    return {"major": 0x1C, "minor": 0x100, "flags": 0, "points": pts, "normals": normals, "faces": faces,
            "sels": sels, "props": props, "res": res}


def merge_template_extras(L, T, keep_face):
    """Append to L the faces of template LOD T for which keep_face(face_index) is true (proxies), with their points,
    normals, point flags and the bytes of every template selection that contains them."""
    tnp = len(T["points"])
    fidx = [k for k in range(len(T["faces"])) if keep_face(k)]
    pmap, nmap = {}, {}
    for k in fidx:
        for v in T["faces"][k]["verts"][:T["faces"][k]["n"]]:
            if v[0] not in pmap:
                pmap[v[0]] = len(L["points"]); L["points"].append(T["points"][v[0]])
            if v[1] not in nmap:
                nmap[v[1]] = len(L["normals"]); L["normals"].append(T["normals"][v[1]])
    fmap = {}
    for k in fidx:
        f = T["faces"][k]
        verts = [(pmap[v[0]], nmap[v[1]], v[2], v[3]) if j < f["n"] else v for j, v in enumerate(f["verts"])]
        fmap[k] = len(L["faces"])
        L["faces"].append(dict(f, verts=verts))
    lower = {n.lower(): n for n in L["sels"]}
    for a, name, blob in T["tags"]:
        if name.startswith(b"#"):
            continue
        nm = name.decode("latin-1")
        d = {pmap[i]: blob[i] for i in pmap if blob[i]}
        fb = [fmap[k] for k in fidx if blob[tnp + k]]
        if not d and not fb:
            continue
        key = lower.get(nm.lower(), nm)
        if key not in L["sels"]:
            L["sels"][key] = ({}, []); lower[nm.lower()] = key
        L["sels"][key][0].update(d); L["sels"][key][1].extend(fb)
    return len(fidx)


def finish(L):
    """Turn a built LOD into the raw MLOD layout (tags: selections, properties, UV set 0, end of file)."""
    np_, nf = len(L["points"]), len(L["faces"])
    tags = []
    for name, (d, fb) in L["sels"].items():
        pb = bytearray(np_); fbb = bytearray(nf)
        for i, bb in d.items():
            pb[i] = bb
        for k in fb:
            fbb[k] = 1
        tags.append(tag(name, bytes(pb) + bytes(fbb)))
    for blob in L["props"]:
        tags.append(tag("#Property#", blob))
    uvs = bytearray(struct.pack("<I", 0))
    for f in L["faces"]:
        for v in f["verts"][:f["n"]]:
            uvs += struct.pack("<ff", v[2], v[3])
    tags.append(tag("#UVSet#", bytes(uvs)))
    tags.append(tag("#EndOfFile#", b""))
    return {"major": L["major"], "minor": L["minor"], "flags": L["flags"], "points": L["points"],
            "normals": L["normals"], "faces": L["faces"], "tags": tags, "res": L["res"]}


def props_of(T):
    return [blob for a, n, blob in T["tags"] if n == b"#Property#"]


def proxy_faces(T):
    np_ = len(T["points"])
    out = set()
    for a, n, blob in T["tags"]:
        if n.lower().startswith(b"proxy:"):
            out.update(k for k in range(len(T["faces"])) if blob[np_ + k])
    return out


def save(model, path, log):
    write(model, path)
    back = parse(path)                                                  # read back: structure must survive
    log(f"P3D {os.path.basename(path)}: {len(back['lods'])} LODs " + ", ".join(
        f"{L['res']:.6g}:{len(L['points'])}p/{len(L['faces'])}f" for L in back["lods"]))
