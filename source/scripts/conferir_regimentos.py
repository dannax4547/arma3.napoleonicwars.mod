# Completeness check of the regimental lots in the BUILT addon: for every uniform variant of variantes_regimentos.json,
# every shako of gen_config_pruss.py and both leather sets, the class must exist in the packed config (config.bin,
# de-rapified with CfgConvert -txt) and every texture / model it references must be inside the PBO.
# Also writes the in-game parade snippet (debug console) from the same data, so the two never disagree.
#   python -I conferir_regimentos.py <project root> <config.cpp from CfgConvert -txt of the PBO's config.bin> <file.pbo>
import sys, os, re, json, struct

ROOT, CFG_TXT, PBO = sys.argv[1:4]
VAR = json.load(open(os.path.join(ROOT, r"source\textures\hcl_uniforme_pruss\variantes_regimentos.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(ROOT, "source", "scripts"))
src = open(os.path.join(ROOT, r"source\scripts\gen_config_pruss.py"), encoding="utf-8").read()
SHAKOS = re.findall(r'\("(HCL_H_Pruss1813_\w+)",', src)
cfg = open(CFG_TXT, encoding="latin-1").read()

d = open(PBO, "rb").read()
p, ents = 0, []
while True:
    e = d.index(b"\0", p); name = d[p:e].decode("latin-1"); p = e + 1
    packing, orig, _, _, size = struct.unpack_from("<5I", d, p); p += 20
    if not name:
        if packing == 0x56657273:
            while True:
                e = d.index(b"\0", p); k = d[p:e]; p = e + 1
                if not k:
                    break
                e = d.index(b"\0", p); p = e + 1
            continue
        break
    ents.append(name.lower())
inside = set(ents)


def class_block(name):
    m = re.search(r"class\s+" + re.escape(name) + r"\s*:\s*(\w+)\s*\{", cfg)
    if not m:
        return None, None
    i, depth = m.end(), 1
    while depth:
        depth += {"{": 1, "}": -1}.get(cfg[i], 0); i += 1
    return m.group(1), cfg[m.end():i]


def refs(block):
    return [r.lower().lstrip("\\") for r in re.findall(r'"(\\?hcl\\hcl_pruss\\[^"]+)"', block)]


rows, bad = [], 0
for v in sorted(VAR):
    for cls in (f"HCL_U_Pruss1813_{v}", f"HCL_Pruss1813_Soldado_{v}"):
        base, blk = class_block(cls)
        missing = [r for r in (refs(blk) if blk else []) if r[len("hcl\\hcl_pruss\\"):] not in inside]
        ok = blk is not None and not missing
        bad += not ok
        rows.append((cls, base, "OK" if ok else f"FALTA {missing or 'classe'}"))
for cls in SHAKOS + ["HCL_V_Pruss1813_Correame", "HCL_V_Pruss1813_Correame_Preto", "HCL_B_Pruss1813_Tornister",
                     "HCL_B_Pruss1813_Tornister_Preto"]:
    base, blk = class_block(cls)
    missing = [r for r in (refs(blk) if blk else []) if r[len("hcl\\hcl_pruss\\"):] not in inside]
    ok = blk is not None and not missing
    bad += not ok
    rows.append((cls, base, "OK" if ok else f"FALTA {missing or 'classe'}"))
for r in rows:
    print(f"  {r[0]:48s} : {str(r[1]):18s} {r[2]}")
print(f"UNIFORMES {len(VAR)} (+ {len(VAR)} soldados) | BARRETINAS {len(SHAKOS)} | CORREAMES 2 | MOCHILAS 2 | problemas: {bad}")

# ---------------------------------------------------------------- in-game parade (debug console, local exec)
vids = sorted(VAR)
leather = ["_Preto" if VAR[v].get("correame_no_mod") == "preto" else "" for v in vids]
sqf = ("// Historical Clothing - desfile de teste: todos os uniformes em fila na frente do jogador, cada um com uma\n"
       "// barretina (em rodizio) e o couro indicado no bloco do mod. Colar no console de depuracao (Esc) e LOCAL EXEC.\n"
       "private _u = [" + ", ".join(f'"{v}"' for v in vids) + "];\n"
       "private _c = [" + ", ".join(f'"{x}"' for x in leather) + "];\n"
       "private _h = [" + ", ".join(f'"{s}"' for s in SHAKOS) + "];\n"
       "private _g = createGroup west;\n"
       "{\n"
       "    private _s = _g createUnit [\"B_Soldier_F\", player modelToWorld [(_forEachIndex - 8) * 1.4, 7, 0], [], 0, \"CAN_COLLIDE\"];\n"
       "    removeAllWeapons _s; removeVest _s; removeBackpack _s; removeHeadgear _s;\n"
       "    _s forceAddUniform format [\"HCL_U_Pruss1813_%1\", _x];\n"
       "    _s addHeadgear (_h select (_forEachIndex mod count _h));\n"
       "    _s addVest format [\"HCL_V_Pruss1813_Correame%1\", _c select _forEachIndex];\n"
       "    _s addBackpack format [\"HCL_B_Pruss1813_Tornister%1\", _c select _forEachIndex];\n"
       "    _s disableAI \"MOVE\"; _s disableAI \"ANIM\";\n"
       "    _s setDir (_s getDir player);\n"
       "} forEach _u;\n"
       "hint format [\"HCL: %1 soldados no desfile\", count _u];\n")
out = os.path.join(ROOT, r"release\@Historical_Clothing\teste_desfile_console.sqf")
open(out, "w", encoding="ascii", newline="\r\n").write(sqf)
print("SQF", out)
