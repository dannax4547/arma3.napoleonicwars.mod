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


def name(cls):
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
