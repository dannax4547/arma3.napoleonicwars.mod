# Read-only: lists the files inside game PBOs whose bytes contain a given text (e.g. a config class name).
# Does not modify or extract anything.   python pbo_find.py <text> <file.pbo> [<file.pbo> ...]
import sys, struct, os


def entries(path):
    with open(path, "rb") as fh:
        d = fh.read()
    p, out = 0, []
    while True:
        e = d.index(b"\0", p)
        name = d[p:e].decode("latin-1")
        p = e + 1
        packing, orig, _, _, size = struct.unpack_from("<5I", d, p)
        p += 20
        if name == "" and packing == 0x56657273:          # 'Vers' header: skip the key/value properties
            while True:
                e = d.index(b"\0", p); k = d[p:e]; p = e + 1
                if not k:
                    break
                e = d.index(b"\0", p); p = e + 1
            continue
        if name == "":
            break
        out.append((name, packing, size))
    data_start = p
    off = data_start
    res = []
    for name, packing, size in out:
        res.append((name, d[off:off + size], packing))
        off += size
    return res


if sys.argv[1] == "--extract":                       # --extract <file.pbo> <inner name> <out file> (copy one entry)
    pbo, inner, out = sys.argv[2:5]
    for name, blob, packing in entries(pbo):
        if name.lower() == inner.lower():
            if packing:
                raise SystemExit("entry is compressed; use BankRev instead")
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            open(out, "wb").write(blob)
            print(f"extracted {name} -> {out} ({len(blob)} bytes)")
            raise SystemExit(0)
    raise SystemExit(f"{inner} not found in {pbo}")

text = sys.argv[1].encode()
for pbo in sys.argv[2:]:
    try:
        for name, blob, packing in entries(pbo):
            if text in blob:
                print(f"{os.path.basename(pbo)} :: {name} ({len(blob)} bytes{', compressed' if packing else ''})")
    except Exception as ex:
        print(f"{os.path.basename(pbo)}: ERROR {ex}")
