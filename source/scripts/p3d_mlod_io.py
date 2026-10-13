# Full-fidelity reader and writer for editable Arma P3D files (MLOD, "P3DM" LODs), plain Python.
# The layout is the one already read by p3d_mlod.py; this module keeps EVERY field (point flags, normals, face flags,
# all TAGG tags as raw bytes, LOD flags) so that a file read and written back is byte-identical. That round trip is the
# validation of the writer (run this file on the Arma 3 Samples: `python p3d_mlod_io.py <file.p3d> ...`).
# Blender does not write P3D; this module does, from data prepared by the project's scripts.
import struct


def parse(path):
    d = open(path, "rb").read()
    pos = 0

    def u32():
        nonlocal pos
        v = struct.unpack_from("<I", d, pos)[0]; pos += 4; return v

    def cstr():
        nonlocal pos
        e = d.index(b"\0", pos)
        s = d[pos:e]; pos = e + 1; return s

    if d[:4] != b"MLOD":
        raise ValueError(f"{path}: not MLOD")
    pos = 4
    model = {"version": u32(), "lods": []}
    for _ in range(u32()):
        if d[pos:pos + 4] != b"P3DM":
            raise ValueError("bad LOD signature")
        pos += 4
        L = {"major": u32(), "minor": u32()}
        npts, nnorm, nfaces = u32(), u32(), u32()
        L["flags"] = u32()
        L["points"] = [struct.unpack_from("<fffI", d, pos + 16 * i) for i in range(npts)]
        pos += 16 * npts
        L["normals"] = [struct.unpack_from("<fff", d, pos + 12 * i) for i in range(nnorm)]
        pos += 12 * nnorm
        faces = []
        for _ in range(nfaces):
            n = u32()
            verts = [struct.unpack_from("<IIff", d, pos + 16 * k) for k in range(4)]
            pos += 64
            fl = u32()
            faces.append({"n": n, "verts": verts, "flags": fl, "tex": cstr(), "mat": cstr()})
        L["faces"] = faces
        if d[pos:pos + 4] != b"TAGG":
            raise ValueError("TAGG not found")
        pos += 4
        tags = []
        while True:
            active = d[pos]; pos += 1
            name = cstr()
            size = u32()
            tags.append((active, name, d[pos:pos + size])); pos += size
            if name == b"#EndOfFile#":
                break
        L["tags"] = tags
        L["res"] = struct.unpack_from("<f", d, pos)[0]; pos += 4
        model["lods"].append(L)
    model["tail"] = d[pos:]
    return model


def dump(model):
    out = bytearray(b"MLOD")
    out += struct.pack("<II", model["version"], len(model["lods"]))
    for L in model["lods"]:
        out += b"P3DM" + struct.pack("<II", L["major"], L["minor"])
        out += struct.pack("<IIII", len(L["points"]), len(L["normals"]), len(L["faces"]), L["flags"])
        for p in L["points"]:
            out += struct.pack("<fffI", *p)
        for n in L["normals"]:
            out += struct.pack("<fff", *n)
        for f in L["faces"]:
            out += struct.pack("<I", f["n"])
            for v in f["verts"]:
                out += struct.pack("<IIff", *v)
            out += struct.pack("<I", f["flags"]) + f["tex"] + b"\0" + f["mat"] + b"\0"
        out += b"TAGG"
        for active, name, blob in L["tags"]:
            out += bytes([active]) + name + b"\0" + struct.pack("<I", len(blob)) + blob
        out += struct.pack("<f", L["res"])
    out += model.get("tail", b"")
    return bytes(out)


def write(model, path):
    open(path, "wb").write(dump(model))


# ---------------------------------------------------------------- helpers to build LODs
def tag(name, blob, active=1):
    return (active, name.encode("latin-1") if isinstance(name, str) else name, blob)


def selection_blob(npts, nfaces, point_bytes, face_bytes):
    """Named selection: one byte per point (0 = not in it; weights coded as in the Samples, 1 = full) and one per face."""
    pb = bytearray(npts); fb = bytearray(nfaces)
    for i, b in point_bytes.items():
        pb[i] = b
    for i in face_bytes:
        fb[i] = 1
    return bytes(pb) + bytes(fb)


def weight_byte(w):
    """Inverse of uniform_fit.weight_of_byte: w = (256 - b) / 255, b = 1 for full weight."""
    return max(1, min(255, int(round(256 - 255 * w))))


def property_blob(name, value):
    return name.encode("latin-1").ljust(64, b"\0")[:64] + value.encode("latin-1").ljust(64, b"\0")[:64]


def get_tag(L, name):
    for a, n, b in L["tags"]:
        if n == (name.encode("latin-1") if isinstance(name, str) else name):
            return b
    return None


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        src = open(p, "rb").read()
        m = parse(p)
        ok = dump(m) == src
        print(f"{'IDENTICO' if ok else 'DIFERENTE'}  {len(src):9d} B  {len(m['lods']):2d} LODs  {p}")
