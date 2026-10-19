# English display names of the classes of the test addon hcl_uk (same rule as nomes_en.py, which serves hcl_pruss and
# hcl_fr and is left untouched): class names (HCL_*) never change; a regiment is named ONLY where a cited source
# supports it (docs/specs/uk_1812.md section 6):
#   28th (North Gloucestershire) Regiment of Foot: yellow facings, 1806 stovepipe with the number at the back at
#     Waterloo (wtj.com British line infantry guide; Plastic Soldier Review; Wikipedia "28th Foot") - 🔶, and the lace
#     pattern of the coat is the mod art's, not the regiment's (no source read for it)
#   95th Regiment of Foot (Rifles): green jacket, black facings, black belts, bugle (miniatures.de, Historical Twist) - 🔶
# Everything else: "(regiment unidentified)".
import re

T = " (HCL test)"
FACING = {"L01": "yellow", "L02": "green", "L03": "blue", "L04": "white"}
REG = {"L01": "28th (North Gloucestershire) Regiment of Foot"}
CAPS = {"Belgic_Batalhao": "British Belgic Cap 1812 - Battalion Company (white-over-red tuft, white cords)",
        "Belgic_Granadeiro": "British Belgic Cap 1812 - Grenadier Company (white tuft, white cords)",
        "Belgic_Ligeira": "British Belgic Cap 1812 - Light Company (green tuft, green cords)",
        "Stovepipe_Batalhao": "British Stovepipe Cap - Battalion Company (white-over-red tuft)",
        "Stovepipe_Granadeiro": "British Stovepipe Cap - Grenadier Company (white tuft)",
        "Stovepipe_Ligeira": "British Stovepipe Cap - Light Company (green tuft)",
        "Stovepipe_28th": "British Stovepipe Cap - 28th (North Gloucestershire) Regiment of Foot, back badge",
        "Stovepipe_Rifles": "British Stovepipe Cap - 95th Regiment of Foot (Rifles), bugle",
        "Bonnet_Highland": "British Highland Feather Bonnet (diced band, black ostrich feathers)"}
# Highland dress (build_kilt_uk.py): 92nd = yellow facings (wtj.com) + Gordon tartan (forum; mod art) - 🔶
KILT = {"K01": "92nd Regiment of Foot (Gordon Highlanders)",
        "K02": "Highland Infantry, Government tartan, blue facings (regiment unidentified)"}


def coat(v):
    if v.startswith("R"):
        return "95th Regiment of Foot (Rifles)"
    if v.startswith("K"):
        return KILT[v]
    k = "L" + v[-2:]
    company = "Flank Company (wings)" if v.startswith("FL") else "Battalion Company"
    if k in REG:
        return f"{REG[k]}, {company}"
    return f"Line Infantry, {FACING[k]} facings, {company} (regiment unidentified)"


# Portugal (docs/specs/portugal_1812.md): every line regiment and Cacadores battalion is named by the sources (P1, P3,
# P8), with the spelling of the English-language sources; read from the variant JSONs next to this script
import json, os
_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "textures", "hcl_uniforme_uk")
POR_L = {k: v for k, v in json.load(open(os.path.join(_JS, "variantes_por_linha.json"), encoding="utf-8")).items()}
POR_C = {k: v for k, v in json.load(open(os.path.join(_JS, "variantes_por_cacadores.json"), encoding="utf-8")).items()}


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def por_unit(v):
    if v.startswith("L"):
        d = POR_L[v]
        return f"{ordinal(d['regimento'])} Line Infantry Regiment ({d['nome_regimento']})"
    d = POR_C[v]
    return f"{ordinal(d['batalhao'])} Cacadores Battalion ({d['provincia']})"


POR_CAP = {"Batalhao": "Battalion Company (white plume)", "Granadeiro": "Grenadier Company (white plume, grenade)",
           "Ligeira": "Light Company (green plume, bugle)", "Cacadores": "green plume and cords, bugle"}


def name_por(cls):
    m = re.fullmatch(r"HCL_POR1812_Soldado_(\w+)", cls)
    if m:
        if m[1] == "Base":
            return "Portuguese Line Infantryman 1812" + T
        if m[1] == "Cacadores_Base":
            return "Portuguese Cacador 1812" + T
        kind = "Cacador" if m[1].startswith("C") else "Line Infantryman"
        return f"Portuguese {kind} 1812 - {por_unit(m[1])}{T}"
    m = re.fullmatch(r"HCL_U_POR1812_(\w+)", cls)
    if m:
        kind = "Portuguese Cacadores Jacket (brown)" if m[1].startswith("C") else "Portuguese Infantry Jacket 1812"
        return f"[HCL] {kind} - {por_unit(m[1])}"
    m = re.fullmatch(r"HCL_H_POR1812_Stovepipe_(\w+)_(\d\d)", cls)
    if m:
        unit = por_unit(("C" if m[1] == "Cacadores" else "L") + m[2])
        return f"[HCL] Portuguese Stovepipe Cap - {unit}, {POR_CAP[m[1]]}"
    return None


# Brunswick 1815 (docs/specs/kgl_brunswick_1815.md section 4; Feldcorps glossary and others): every battalion named
BRU_D = json.load(open(os.path.join(_JS, "variantes_bru_dolman.json"), encoding="utf-8"))
BRU_CAP = {"Leib": "Leib-Bataillon (black horsehair, skull and crossbones)",
           "Ligeiro": "Light Battalions (white-metal bugle, blue and yellow pompom)",
           "Avantgarde": "Avantgarde, light companies (bugle, green plume; the round hat is not made yet)"}


def name_bru(cls):
    m = re.fullmatch(r"HCL_BRU1815_Soldado_(\w+)", cls)
    if m:
        if m[1] == "Base":
            return "Brunswick Infantryman 1815" + T
        return f"Brunswick Infantryman 1815 - {BRU_D[m[1]]['unidade']}{T}"
    m = re.fullmatch(r"HCL_U_BRU1815_(\w+)", cls)
    if m:
        return f"[HCL] Brunswick Black Dolman 1815 - {BRU_D[m[1]]['unidade']}"
    m = re.fullmatch(r"HCL_H_BRU1815_Kiwer_Linha_(\d)", cls)
    if m:
        return f"[HCL] Brunswick Shako 1815 - {ordinal(int(m[1]))} Line Battalion (white-metal Welfenross shield)"
    m = re.fullmatch(r"HCL_H_BRU1815_Kiwer_(\w+)", cls)
    if m:
        return f"[HCL] Brunswick Shako 1815 - {BRU_CAP[m[1]]}"
    return None


# KGL and Hanover (kgl_brunswick_1815.md 2-3)
KGL_L = json.load(open(os.path.join(_JS, "variantes_kgl_ligeira.json"), encoding="utf-8"))
HAN = json.load(open(os.path.join(_JS, "variantes_han.json"), encoding="utf-8"))
KGL_CAP = {"Batalhao": "Battalion Company (white-over-red tuft)", "Granadeiro": "Grenadier Company (white tuft)",
           "Ligeira": "Light Company (green tuft)"}


def name_kgl(cls):
    m = re.fullmatch(r"HCL_(KGL1812|HAN1815)_Soldado_(\w+)", cls)
    if m:
        nat, v = m[1], m[2]
        if v.endswith("Base"):
            return ("King's German Legion Infantryman 1812" if nat == "KGL1812" else "Hanoverian Infantryman 1815") + T
        return f"{'KGL' if nat == 'KGL1812' else 'Hanoverian'} Infantryman - {unit_kgl(nat, v)}{T}"
    m = re.fullmatch(r"HCL_U_(KGL1812|HAN1815)_(\w+)", cls)
    if m:
        return f"[HCL] {'KGL' if m[1] == 'KGL1812' else 'Hanoverian'} Jacket - {unit_kgl(m[1], m[2])}"
    m = re.fullmatch(r"HCL_H_KGL1812_Belgic_(\w+)_(\d)", cls)
    if m:
        return f"[HCL] KGL Belgic Cap - {ordinal(int(m[2]))} Line Battalion, {KGL_CAP[m[1]]}"
    if cls == "HCL_H_KGL1812_Stovepipe_Ligeira":
        return "[HCL] KGL Light Battalions Cap (bugle, green cords)"
    if cls == "HCL_H_HAN1815_Stovepipe":
        return "[HCL] Hanoverian Infantry Cap 1815 (oval GR plate)"
    return None


def unit_kgl(nat, v):
    if nat == "HAN1815":
        return HAN[v]["unidade"]
    if v == "KL1":
        return "Line Battalions, Battalion Company (dark blue facings)"
    if v == "KF1":
        return "Line Battalions, Flank Company (wings)"
    return KGL_L[v]["unidade"]


def name(cls):
    if "KGL1812" in cls or "HAN1815" in cls:
        return name_kgl(cls)
    if cls == "HCL_B_BRU1815_Tornister":
        return "[HCL] Brunswick Knapsack 1815 (black, white-metal horse on the flap)" + T
    if "BRU1815" in cls:
        return name_bru(cls)
    if "POR1812" in cls:
        return name_por(cls)
    m = re.fullmatch(r"HCL_UK1812_Soldado_(\w+)", cls)
    if m:
        if m[1].endswith("Base"):
            return "British Infantryman 1812" + T
        return f"British Infantryman 1812 - {coat(m[1])}{T}"
    m = re.fullmatch(r"HCL_U_UK1812_(\w+)", cls)
    if m:
        kind = {"R": "British Rifle Jacket", "K": "British Highland Jacket and Kilt"}.get(m[1][0], "British Infantry Jacket 1812")
        return f"[HCL] {kind} - {coat(m[1])}"
    m = re.fullmatch(r"HCL_H_UK1812_(\w+)", cls)
    if m:
        return f"[HCL] {CAPS[m[1]]}"
    if cls == "HCL_V_UK1812_Correame":
        return "[HCL] British Infantry Crossbelts (pipeclayed)" + T
    if cls == "HCL_V_UK1812_Correame_Preto":
        return "[HCL] British Rifles Crossbelts (black leather)" + T
    if cls == "HCL_B_BRU1815_Tornister":
        return "[HCL] Brunswick Knapsack 1815 (black, white-metal horse on the flap)" + T
    if cls == "HCL_B_UK1812_Mochila":
        return "[HCL] British Trotter Knapsack (black)" + T
    return None


def apply(txt):
    """Same contract as nomes_en.apply: every class with a displayName gets its English name, or this fails."""
    out, cls, missing = [], None, []
    for line in txt.split("\n"):
        m = re.match(r"\tclass (\w+)", line)
        if m:
            cls = m[1]
        if "displayName" in line and cls:
            en = name(cls)
            if en is None:
                missing.append(cls)
            else:
                line = re.sub(r'displayName = ".*";', f'displayName = "{en}";', line)
        out.append(line)
    assert not missing, f"classes sem nome em ingles: {missing}"
    res = "\n".join(out)
    assert all(ord(c) < 128 for c in res)
    return res
