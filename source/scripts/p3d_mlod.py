# Minimal read-only reader for editable Arma P3D files (MLOD). Shared by the project's Blender scripts.
# Returns, per LOD: resolution, points [(x,y,z)], faces [[point indices]], faces_uv [[(u, v)] per face vertex],
# faces_tex [(texture, material)], selections {name: bytes per point}, properties [(name, value)].
# Axis convention of P3D (verified on the Arma 3 Samples character): +Y up, front = -Z, character's left = +X.
# Face winding (verified 2026-10-10 on A3_character_example.p3d): keep the MLOD vertex order after to_blender();
# the normals then point outward. Reversing the order (as the early inspection scripts did) makes them point inward.
import struct


def to_blender(p):
    """P3D (x, y, z) -> Blender (x, y, z): up stays up, front -Z -> -Y, left stays +X (mirror between handedness)."""
    return (p[0], p[2], p[1])


def read_mlod(path):
    d = open(path, "rb").read()
    pos = 0

    def u32():
        nonlocal pos
        v = struct.unpack_from("<I", d, pos)[0]; pos += 4; return v

    def f32():
        nonlocal pos
        v = struct.unpack_from("<f", d, pos)[0]; pos += 4; return v

    def raw(n):
        nonlocal pos
        v = d[pos:pos + n]; pos += n; return v

    def cstr():
        nonlocal pos
        e = d.index(b"\0", pos)
        s = d[pos:e].decode("latin-1"); pos = e + 1; return s

    if raw(4) != b"MLOD":
        raise ValueError(f"{path}: not an MLOD file")
    u32()
    lods = []
    for _ in range(u32()):
        if raw(4) != b"P3DM":
            raise ValueError("bad LOD signature")
        u32(); u32()
        npts, nnorm, nfaces = u32(), u32(), u32()
        u32()
        pts = [struct.unpack_from("<fff", d, pos + i * 16) for i in range(npts)]
        pos += npts * 16 + nnorm * 12
        faces, faces_uv, faces_tex = [], [], []
        for _ in range(nfaces):
            nv = u32()
            idx = [struct.unpack_from("<I", d, pos + k * 16)[0] for k in range(nv)]
            uvs = [struct.unpack_from("<ff", d, pos + k * 16 + 8) for k in range(nv)]
            pos += 4 * 16 + 4
            tex, mat = cstr(), cstr()
            faces.append(idx)
            faces_uv.append(uvs)
            faces_tex.append((tex, mat))
        if raw(4) != b"TAGG":
            raise ValueError("TAGG not found")
        sels, props = {}, []
        while True:
            raw(1)
            name = cstr()
            blob = raw(u32())
            if name == "#EndOfFile#":
                break
            if name == "#Property#":
                props.append((blob[:64].split(b"\0")[0].decode("latin-1"), blob[64:128].split(b"\0")[0].decode("latin-1")))
            elif not name.startswith("#"):
                sels[name] = blob[:npts]
        lods.append({"res": f32(), "points": pts, "faces": faces, "faces_uv": faces_uv, "faces_tex": faces_tex,
                     "selections": sels, "properties": props})
    return lods
