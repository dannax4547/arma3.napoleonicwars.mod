# Read-only reader for unbinarized Arma animation files (RTM_0101), as shipped in the Arma 3 Samples.
# Layout (verified on Samples\Addons\Test_Anims\*.rtm by file size: 28 + 32*bones + frames*(4 + 80*bones)):
#   "RTM_0101", float[3] displacement, int32 frames, int32 bones, bones x char[32] names,
#   per frame: float phase, then per bone: char[32] name + float[12] (3x4 matrix, model space of the P3D).
# Usage as a module: read_rtm(path) -> {"disp", "bones", "frames": [(phase, {bone: 3x4 list})]}
import struct


def _name(b):
    return b.split(b"\0")[0].decode("latin-1")


def read_rtm(path):
    d = open(path, "rb").read()
    if d[:8] != b"RTM_0101":
        raise ValueError(f"{path}: not an unbinarized RTM_0101 file")
    disp = struct.unpack_from("<3f", d, 8)
    nf, nb = struct.unpack_from("<2i", d, 20)
    pos = 28
    bones = [_name(d[pos + 32 * i: pos + 32 * (i + 1)]) for i in range(nb)]
    pos += 32 * nb
    frames = []
    for _ in range(nf):
        phase = struct.unpack_from("<f", d, pos)[0]; pos += 4
        mats = {}
        for _ in range(nb):
            name = _name(d[pos:pos + 32]); pos += 32
            mats[name] = struct.unpack_from("<12f", d, pos); pos += 48
        frames.append((phase, mats))
    if pos != len(d):
        raise ValueError(f"{path}: {len(d) - pos} trailing bytes (layout assumption wrong)")
    return {"disp": disp, "bones": bones, "frames": frames}


if __name__ == "__main__":
    import sys
    r = read_rtm(sys.argv[1])
    print("disp", r["disp"], "frames", len(r["frames"]), "bones", len(r["bones"]))
    for b in sys.argv[2:]:
        for ph, m in r["frames"][:2]:
            print(f"{b:14s} phase {ph:.3f}", " ".join(f"{x:7.3f}" for x in m[b]))
