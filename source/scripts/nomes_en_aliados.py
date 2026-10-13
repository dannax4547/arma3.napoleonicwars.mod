# English display names of the French-allied test addons (hcl_suica, later hcl_varsovia, hcl_italia, hcl_reno). Own
# module (the shared nomes_en.py of hcl_fr / hcl_pruss is not edited); same contract: gen_config_<group>.py calls
# apply() on the finished config text, every displayName is replaced and a class without an English name fails the
# build. Regiment names only where a cited source supports them (docs/specs/aliados_fr_1812.md):
#   Swiss (French service), 1812: 1st yellow facings (Wikipedia, 1812 regulations ✅), 3rd black facings (Wikipedia
#   citing Fieffé 1854 ✅); 2nd royal blue and 4th sky blue are NOT sourced (🔶, user decision A6) -> the name says so.
import re

T = " (HCL test)"
SUICA_REG = {"1": "1st Swiss Regiment", "2": "2nd Swiss Regiment (facing colour unconfirmed)",
             "3": "3rd Swiss Regiment", "4": "4th Swiss Regiment (facing colour unconfirmed)"}
SUICA_COMP = {"": "Fusiliers", "Granadeiro": "Grenadier Company", "Voltigeur": "Voltigeur Company"}
SUICA_HEAD = {
    "Bonnet_Granadeiro_Gala": "Grenadier Bearskin - full dress (grenade plate, cords, plume)",
    "Bonnet_Granadeiro_Campanha": "Grenadier Bearskin - campaign (grenade plate)",
    "Fuzileiro_1aComp": "Shako 1812 (French model) - Fusilier, 1st Company, dark green pompom",
    "Fuzileiro_2aComp": "Shako 1812 (French model) - Fusilier, 2nd Company, sky blue pompom",
    "Fuzileiro_3aComp": "Shako 1812 (French model) - Fusilier, 3rd Company, aurore pompom",
    "Fuzileiro_4aComp": "Shako 1812 (French model) - Fusilier, 4th Company, violet pompom",
    "Voltigeur_Gala": "Shako 1812 (French model) - Voltigeur, full dress (plume and cords)",
    "Voltigeur_Campanha": "Shako 1812 (French model) - Voltigeur, campaign (pompom)",
}


def name(cls):
    m = re.fullmatch(r"HCL_Suica1812_Soldado_(?:(Granadeiro|Voltigeur)_)?S(\d)", cls)
    if m:
        return f"Swiss Infantryman (French service) - {SUICA_REG[m[2]]}, {SUICA_COMP[m[1] or '']}{T}"
    if cls == "HCL_Suica1812_Soldado_Base":
        return "Swiss Infantryman (French service) 1812" + T
    if cls == "HCL_Suica1812_Soldado_Elite_Base":
        return "Swiss Infantryman (French service) 1812, elite company" + T
    m = re.fullmatch(r"HCL_U_Suica1812_(?:(Granadeiro|Voltigeur)_)?S(\d)", cls)
    if m:
        return f"[HCL] Swiss Coat 1812 (French service) - {SUICA_REG[m[2]]}, {SUICA_COMP[m[1] or '']}"
    m = re.fullmatch(r"HCL_H_Suica1812_(\w+)", cls)
    if m and m[1] in SUICA_HEAD:
        return f"[HCL] Swiss Regiments (French service) {SUICA_HEAD[m[1]]}"
    return None


def apply(txt):
    """Replace the displayName inside every class block of a generated config.cpp; every class that has a
    displayName must have an English name."""
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
