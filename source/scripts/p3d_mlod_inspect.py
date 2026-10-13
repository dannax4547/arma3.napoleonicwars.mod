# Read-only inspector for editable Arma P3D files (MLOD / P3DM LODs).
# Prints, per LOD: resolution, vertex/face counts, bounding box, named properties, named selections
# (with how many points each selection uses), textures and materials.
# Run with Blender's bundled Python (headless):
#   blender -b --factory-startup --python p3d_mlod_inspect.py -- <file.p3d> [<file2.p3d> ...] [sel=name1,name2] [lods=0,1]
#   sel=  also prints the bounding box of the points in those named selections (case-insensitive)
#   lods= limits the output to those LOD indices
# Binarized (ODOL) game models are NOT supported; the script says so and skips them.
import sys, struct

# Special LOD resolutions (as documented for Arma P3D LODs). Unlisted values are shown raw.
SPECIAL = {1.0e3: "View Gunner", 1.1e3: "View Pilot", 1.2e3: "View Cargo", 1.0e4: "Shadow Volume 0",
           1.001e4: "Shadow Volume 10", 1.0e13: "Geometry", 1.0e15: "Memory", 2.0e15: "Land Contact",
           3.0e15: "Roadway", 4.0e15: "Paths", 5.0e15: "Hit-points", 6.0e15: "View Geometry",
           7.0e15: "Fire Geometry", 8.0e15: "View Cargo Geometry", 9.0e15: "View Cargo Fire Geometry",
           1.0e16: "View Commander", 1.1e16: "View Commander Geometry", 1.2e16: "View Commander Fire Geometry",
           1.3e16: "View Pilot Geometry", 1.4e16: "View Pilot Fire Geometry", 1.5e16: "View Gunner Geometry",
           1.6e16: "View Gunner Fire Geometry", 1.7e16: "Sub Parts", 1.8e16: "Shadow Volume - View Cargo",
           1.9e16: "Shadow Volume - View Pilot", 2.0e16: "Shadow Volume - View Gunner", 2.1e16: "Wreck"}


def lod_name(res):
    for k, v in SPECIAL.items():
        if abs(res - k) <= abs(k) * 1e-6:
            return v
    if 1.0e4 <= res < 2.0e4:
        return f"Shadow Volume {res - 1.0e4:g}"
    return f"Resolution {res:g}"


class R:
    def __init__(self, data):
        self.d, self.p = data, 0
    def u32(self):
        v = struct.unpack_from("<I", self.d, self.p)[0]; self.p += 4; return v
    def f32(self):
        v = struct.unpack_from("<f", self.d, self.p)[0]; self.p += 4; return v
    def raw(self, n):
        v = self.d[self.p:self.p + n]; self.p += n; return v
    def cstr(self):
        e = self.d.index(b"\0", self.p)
        s = self.d[self.p:e].decode("latin-1"); self.p = e + 1; return s


SEL_BBOX, ONLY_LODS = set(), None


def bbox_of(pts):
    if not pts:
        return "(empty)"
    xs, ys, zs = zip(*pts)
    return f"x[{min(xs):.3f},{max(xs):.3f}] y[{min(ys):.3f},{max(ys):.3f}] z[{min(zs):.3f},{max(zs):.3f}]"


def inspect(path):
    data = open(path, "rb").read()
    r = R(data)
    magic = r.raw(4)
    print(f"\n=== {path}")
    if magic != b"MLOD":
        print(f"  not MLOD (magic={magic!r}) - skipped")
        return
    version, nlods = r.u32(), r.u32()
    print(f"  MLOD version={version} LODs={nlods}")
    for li in range(nlods):
        sig = r.raw(4)
        if sig != b"P3DM":
            print(f"  LOD {li}: unexpected signature {sig!r}; stopping")
            return
        r.u32(); r.u32()                       # major / minor version
        npts, nnorm, nfaces = r.u32(), r.u32(), r.u32()
        r.u32()                                # flags
        pts = [struct.unpack_from("<fff", data, r.p + i * 16) for i in range(npts)]
        r.p += npts * 16 + nnorm * 12
        textures, materials = {}, {}
        for _ in range(nfaces):
            r.u32()                            # vertex count (3 or 4)
            r.p += 4 * 16 + 4                  # 4 vertex tables + face flags
            t, m = r.cstr(), r.cstr()
            textures[t] = textures.get(t, 0) + 1
            materials[m] = materials.get(m, 0) + 1
        if r.raw(4) != b"TAGG":
            print(f"  LOD {li}: TAGG not found; stopping")
            return
        props, sels, others, sel_boxes = [], [], [], []
        while True:
            r.raw(1)                           # active flag
            name = r.cstr()
            size = r.u32()
            blob = r.raw(size)
            if name == "#EndOfFile#":
                break
            if name == "#Property#":
                props.append((blob[:64].split(b"\0")[0].decode("latin-1"), blob[64:128].split(b"\0")[0].decode("latin-1")))
            elif name.startswith("#"):
                others.append(name)
            else:
                used = sum(1 for b in blob[:npts] if b)
                sels.append((name, used))
                if name.lower() in SEL_BBOX:
                    sel_boxes.append((name, bbox_of([pts[i] for i in range(npts) if blob[i]])))
        res = r.f32()
        if ONLY_LODS is not None and li not in ONLY_LODS:
            continue
        print(f"  LOD {li}: {lod_name(res)}  (res={res:g})  points={npts} faces={nfaces}  bbox {bbox_of(pts)}")
        for n, b in sel_boxes:
            print(f"     bbox of selection '{n}': {b}")
        if props:
            print("     properties: " + ", ".join(f"{k}={v}" for k, v in props))
        if sels:
            print("     selections: " + ", ".join(f"{n}({u})" for n, u in sels))
        if others:
            print("     other tags: " + ", ".join(sorted(set(others))))
        tex = [t for t in textures if t]
        mat = [m for m in materials if m]
        if tex:
            print("     textures: " + ", ".join(tex))
        if mat:
            print("     materials: " + ", ".join(mat))


_files = []
for a in sys.argv[sys.argv.index("--") + 1:]:
    if a.startswith("sel="):
        SEL_BBOX = {s.lower() for s in a[4:].split(",") if s}
    elif a.startswith("lods="):
        ONLY_LODS = {int(s) for s in a[5:].split(",") if s}
    else:
        _files.append(a)
for f in _files:
    try:
        inspect(f)
    except Exception as e:
        print(f"  ERROR reading {f}: {e}")
