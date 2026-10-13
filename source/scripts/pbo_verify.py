# Read-only check of a built PBO (test P2): header properties (prefix), entries, file signatures, and that every
# path the config and the models reference inside the addon is present.
#   python pbo_verify.py <file.pbo>
import sys, struct, re

d = open(sys.argv[1], "rb").read()
p, ents, props = 0, [], {}
while True:
    e = d.index(b"\0", p); name = d[p:e].decode("latin-1"); p = e + 1
    packing, orig, _, _, size = struct.unpack_from("<5I", d, p); p += 20
    if not name:
        if packing == 0x56657273:
            while True:
                e = d.index(b"\0", p); k = d[p:e].decode("latin-1"); p = e + 1
                if not k:
                    break
                e = d.index(b"\0", p); props[k] = d[p:e].decode("latin-1"); p = e + 1
            continue
        break
    ents.append((name, packing, size))
off = p
data = {}
for name, packing, size in ents:
    data[name.lower()] = d[off:off + size]; off += size
print("properties:", props)
print(f"entries: {len(ents)}; packed (compressed) entries: {sum(1 for e in ents if e[1])}")
bad = [n for n, *_ in ents if re.search(r"\.(cpp|cfg|blend|py|ps1|png|tga)$", n, re.I) and n.lower() != "config.cpp"]
print("source files inside:", bad or "none")
for name, packing, size in ents:
    sig = data[name.lower()][:4]
    print(f"   {name:48s} {size:9d}  {sig!r}")
prefix = props.get("prefix", "").lower().strip("\\")
# references: model / texture / material paths in config.bin and in the models that point inside our prefix
refs = set()
for name, blob in data.items():
    for m in re.findall(re.escape(prefix.encode("latin-1")) + rb"\\[\w\\.]+\.(?:p3d|paa|rvmat)", blob, re.I):
        refs.add(m.decode("latin-1").lower())
missing = sorted(r for r in refs if r[len(prefix) + 1:] not in data)
print(f"references to {prefix}: {len(refs)}; missing in the PBO: {missing or 'none'}")
