# English display names of the French-allied test addons (hcl_suica, later hcl_varsovia, hcl_italia, hcl_reno). Own
# module (the shared nomes_en.py of hcl_fr / hcl_pruss is not edited); same contract: gen_config_<group>.py calls
# apply() on the finished config text, every displayName is replaced and a class without an English name fails the
# build. Regiment names only where a cited source supports them (docs/specs/aliados_fr_1812.md):
#   Swiss (French service), 1812: 1st yellow (Wikipedia, 1812 regulations), 2nd royal blue, 3rd black, 4th sky blue
#   (Fieffé, Geschichte der Fremdtruppen II, 1860, p. 183, via de.wikipedia, read 2026-10-18; until then the 2nd and
#   4th were named "facing colour unconfirmed").
import re

T = " (HCL test)"
SUICA_REG = {"1": "1st Swiss Regiment", "2": "2nd Swiss Regiment", "3": "3rd Swiss Regiment", "4": "4th Swiss Regiment"}
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


# Duchy of Warsaw, regulation of 3 September 1810 (📜 Gembarzewski 1905 / Zygulski & Wielecki 1988); 7th and 9th
# Regiments from Askenazy & Gembarzewski (Wikipedia regiment pages); the czapka plate shows "4" (mod art polandINF).
# More regiments (2026-10-18), pl.wikipedia regiment articles after Gembarzewski: 1st fusiliers white fringed
# epaulettes and black tufts, 13th white Austrian-stock coats with blue, 15th crimson/amaranth facings; bearskins of
# the 5th and 6th (no plate, crimson cords) and plain ones with white cords (8th, 11th, 12th); numbered plates.
VARS_UNI = {"L1810": "Line Infantry, 1810 regulation", "R07": "7th Infantry Regiment", "R09": "9th Infantry Regiment",
            "R01": "1st Infantry Regiment", "R13": "13th Infantry Regiment (white coat)",
            "R15": "15th Infantry Regiment"}
VARS_COMP = {"": "Fusiliers", "Granadeiro": "Grenadier Company", "Voltigeur": "Voltigeur Company",
             "Fuzileiro": "Fusiliers (white fringed epaulettes)"}
VARS_HEAD = {"Czapka_Fuzileiro": "Czapka 1810 - Fusilier, black pompom, plate of the 4th Regiment",
             "Czapka_Voltigeur": "Czapka 1810 - Voltigeur, yellow-green plume, plate of the 4th Regiment",
             "Bonnet_Granadeiro_Gala": "Grenadier Bearskin 1810 - full dress (eagle and grenades plate, cords, plume)",
             "Bonnet_Granadeiro_Campanha": "Grenadier Bearskin 1810 - campaign (eagle and grenades plate)",
             "Czapka_Fuzileiro_R01": "Czapka 1810 - Fusilier, black tuft, plate of the 1st Regiment",
             "Bonnet_Granadeiro_R05": "Grenadier Bearskin - 5th Regiment (no plate, brass grenade, crimson cords)",
             "Bonnet_Granadeiro_R06": "Grenadier Bearskin - 6th Regiment (no plate or grenade, crimson cords)",
             "Bonnet_Granadeiro_Lisa": "Grenadier Bearskin - plain, white cords (8th, 11th, 12th Regiments)"}


def _ord(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


for _n in (2, 3, 5, 6, 7, 8, 9, 11, 12, 14, 15, 16, 17):
    VARS_HEAD[f"Czapka_Fuzileiro_R{_n:02d}"] = f"Czapka 1810 - Fusilier, black pompom, plate of the {_ord(_n)} Regiment"


# Kingdom of Italy and Kingdom of Naples, c. 1812 (docs/specs/aliados_fr_1812.md section 3). Italy: regimental table
# (Schultheis 🔶) checked against the 1812 prints of the Vinkhuijzen collection (NYPL); Naples: 7th after the Freiberger
# Bilderhandschrift (via Gaertner), 1st/2nd/5th after Knoetel ("seem to have been").
ITA_UNI = {f"IT{n:02d}": f"Kingdom of Italy, {o} Line Infantry Regiment" for n, o in
           ((1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th"), (5, "5th"), (6, "6th"), (7, "7th"))}
ITA_UNI.update({f"NA{n:02d}": f"Kingdom of Naples, {o} Line Infantry Regiment" for n, o in
                ((1, "1st"), (2, "2nd"), (5, "5th"), (7, "7th"))})
ITA_HEAD = {"Shako_Italia_Fuzileiro_1aComp": "Kingdom of Italy Shako 1812 - Fusilier, 1st Company, green pompom",
            "Shako_Italia_Fuzileiro_2aComp": "Kingdom of Italy Shako 1812 - Fusilier, 2nd Company, sky blue pompom",
            "Shako_Italia_Fuzileiro_3aComp": "Kingdom of Italy Shako 1812 - Fusilier, 3rd Company, orange pompom",
            "Shako_Italia_Fuzileiro_4aComp": "Kingdom of Italy Shako 1812 - Fusilier, 4th Company, violet pompom",
            "Shako_Italia_Voltigeur_Gala": "Kingdom of Italy Shako 1812 - Voltigeur, full dress (plume and cords)",
            "Shako_Napoles_Fuzileiro_R01": "Kingdom of Naples Shako 1812 - Fusilier, 1st Regiment (scarlet pompom)",
            "Shako_Napoles_Fuzileiro_R02": "Kingdom of Naples Shako 1812 - Fusilier, 2nd Regiment (green pompom)",
            "Shako_Napoles_Fuzileiro_R05": "Kingdom of Naples Shako 1812 - Fusilier, 5th Regiment (light blue pompom)",
            "Shako_Napoles_Fuzileiro_R07": "Kingdom of Naples Shako 1812 - Fusilier, 7th Regiment (yellow pompom)",
            "Shako_Napoles_Voltigeur_Gala": "Kingdom of Naples Shako 1812 - Voltigeur, full dress (yellow plume)",
            "Bonnet_Italia_Granadeiro_Gala": "Kingdom of Italy Grenadier Bearskin - full dress (grenade plate, white cords, plume)",
            "Bonnet_Italia_Granadeiro_Campanha": "Kingdom of Italy Grenadier Bearskin - campaign (grenade plate)",
            "Bonnet_Napoles_Granadeiro_Gala": "Kingdom of Naples Grenadier Bearskin - full dress (red cords and plume)",
            "Bonnet_Napoles_Granadeiro_Campanha": "Kingdom of Naples Grenadier Bearskin - campaign",
            "Bonnet_Italia_Carabineiro_Gala": "Kingdom of Italy Light Infantry Carabinier Bearskin (red cords and plume, no plate)"}
# lote 2 (2026-10-18): Vinkhuijzen watercolours of 1812 with the collector's captions (names follow the captions)
ITA_UNI.update({"LE01": "Kingdom of Italy, 1st Light Infantry Regiment", "LE03": "Kingdom of Italy, 3rd Light Infantry Regiment",
                "LE04": "Kingdom of Italy, 4th Light Infantry Regiment",
                "LEX": "Kingdom of Italy, Light Infantry (yellow collar, regiment unidentified)",
                "DAL": "Kingdom of Italy, Dalmatian Regiment", "RES": "Kingdom of Italy, Line Infantry Reserve Companies",
                "MIL": "Kingdom of Italy, Milan Guard", "VOL": "Kingdom of Italy, Volunteer",
                "BRE": "Kingdom of Italy, Brescia Bersaglieri", "DRA": "Kingdom of Italy, Queen's Dragoons (dismounted)",
                "ART": "Kingdom of Italy, Artillery Battalion (caption uncertain)"})
ITA_COMP = {"Granadeiro": "Grenadier Company", "Voltigeur": "Voltigeur Company", "Carabiniere": "Carabinier Company",
            "Oficial": "Officer", "Oficial_Granadeiro": "Grenadier Company Officer"}
ITA_KEY = r"((?:IT|NA|LE)\d\d|LEX|DAL|RES|MIL|VOL|BRE|DRA|ART)"
ITA_PRE = r"(?:(Oficial_Granadeiro|Granadeiro|Voltigeur|Carabiniere|Oficial)_)?"


def _ita(comp, key):
    if comp:
        return f"{ITA_UNI[key]}, {ITA_COMP[comp]}"
    if key[:2] in ("IT", "NA"):
        return f"{ITA_UNI[key]}, Fusiliers"
    if key[:2] == "LE":
        return f"{ITA_UNI[key]}, Chasseurs"
    return ITA_UNI[key]


# ---- Confederation of the Rhine, lot 1 (2026-10-20): Wuerttemberg and Bavaria c. 1811 (variantes_reno.py; names follow
# the collector's captions of the Vinkhuijzen watercolours)
RENO_UNI = {
    "WUE01": "Wuerttemberg, 1st Line Infantry Regiment 'Prinz Paul'",
    "WUE02": "Wuerttemberg, 2nd Line Infantry Regiment 'Herzog Wilhelm'",
    "WUE03": "Wuerttemberg, 3rd Line Infantry Regiment",
    "WUE04": "Wuerttemberg, 4th Line Infantry Regiment",
    "WUE05": "Wuerttemberg, 5th Line Infantry Regiment 'Prinz Friedrich'",
    "WUE06": "Wuerttemberg, 6th Line Infantry Regiment 'Kronprinz'",
    "WUE07": "Wuerttemberg, 7th Line Infantry Regiment",
    "WUE08": "Wuerttemberg, 8th Line Infantry Regiment 'von Neubronn'",
    "WUE09": "Wuerttemberg, 9th Line Infantry Regiment",
    "WUE10P": "Wuerttemberg, Light Infantry Regiment No. 10 (black facings)",
    "WUE10A": "Wuerttemberg, Light Infantry Regiment No. 10 (light blue facings)",
    "WUEJK": "Wuerttemberg, 1st Jaeger Battalion 'Koenig'",
    "BAV01": "Bavaria, 1st Line Infantry Regiment 'Koenig'",
    "BAV02": "Bavaria, 2nd Line Infantry Regiment 'Kronprinz'",
    "BAV04": "Bavaria, 4th Line Infantry Regiment 'Sachsen-Hildburghausen'",
    "BAV06": "Bavaria, 6th Line Infantry Regiment 'Herzog Wilhelm'",
    "BAV07": "Bavaria, 7th Line Infantry Regiment 'Loewenstein'",
    "BAV08": "Bavaria, 8th Line Infantry Regiment 'Herzog Pius'",
    "BAV09": "Bavaria, 9th Line Infantry Regiment 'Ysenburg'",
    "BAV10": "Bavaria, 10th Line Infantry Regiment 'Junker'",
    "BAV11L": "Bavaria, 11th Line Infantry Regiment 'Kinkel' (plate figure, orange lapels)",
    "BAV11V": "Bavaria, 11th Line Infantry Regiment 'Kinkel' (plate figure, green lapels)",
    "BAV11P": "Bavaria, 11th Line Infantry Regiment 'Kinkel' (plate figure, black lapels)",
    "BAV13": "Bavaria, 13th Line Infantry Regiment",
    "BAVL1": "Bavaria, 1st Light Infantry Battalion 'Gedoni'",
    "BAVL2": "Bavaria, 2nd Light Infantry Battalion 'Wreden'",
    "BAVL3": "Bavaria, 3rd Light Infantry Battalion 'Bernclau'",
    "BAVL4": "Bavaria, 4th Light Infantry Battalion 'Theobald'",
    "BAVL5": "Bavaria, 5th Light Infantry Battalion 'Butler'",
    "BAVL6": "Bavaria, 6th Light Infantry Battalion 'La Roche'",
    "BAVL7": "Bavaria, 7th Light Infantry Battalion 'Guenther'",
    # lot 2 (2026-10-27): Saxony after the 1810 reform (album "Sachsen 1810")
    "SAXKO": "Saxony, Line Infantry Regiment 'Koenig'",
    "SAXNI": "Saxony, Line Infantry Regiment 'von Niesemeuschel'",
    "SAXAN": "Saxony, Line Infantry Regiment 'Prinz Anton'",
    "SAXLO": "Saxony, Line Infantry Regiment 'von Loew'",
    "SAXMA": "Saxony, Line Infantry Regiment 'Prinz Maximilian'",
    "SAXRE": "Saxony, Line Infantry Regiment 'von Rechten'",
    "SAXFA": "Saxony, Line Infantry Regiment 'Prinz Friedrich August'",
    "SAXCL": "Saxony, Line Infantry Regiment 'Prinz Clemens'",
    "SAXLI": "Saxony, Light Infantry",
    "SAXJG": "Saxony, Jaeger",
}
RENO_HEAD = {"Raupenhelm_Wurttemberg": "Wuerttemberg Crested Helmet (Raupenhelm) 1811 - brass front plate, red and yellow cockade",
             "Raupenhelm_Baviera": "Bavarian Crested Helmet (Raupenhelm) 1811 - crowned oval plate, white and blue cockade",
             "Shako_Saxonia_Fuzileiro": "Saxon Shako 1810 - crowned 'FA' plate, white cords, white pompom",
             "Shako_Saxonia_Fuzileiro_Koenig": "Saxon Shako 1810 - crowned 'FA' plate, white cords, red pompom",
             "Shako_Saxonia_Granadeiro_Gala": "Saxon Grenadier Shako 1810 - crowned 'FA' plate, red cords and plume",
             "Shako_Saxonia_Ligeira": "Saxon Light Infantry Shako 1810 - crowned 'FA' plate, green cords, green pompom",
             "Shako_Saxonia_Jaeger": "Saxon Jaeger Shako 1810 - crowned 'FA' plate, green cords, black plume"}


def name(cls):
    m = re.fullmatch(r"HCL_Reno1811_Soldado_(\w+)", cls)
    if m and m[1] in RENO_UNI:
        return f"Soldier, {RENO_UNI[m[1]]}{T}"
    if cls == "HCL_Reno1811_Soldado_Base":
        return "Soldier, Confederation of the Rhine 1811" + T
    m = re.fullmatch(r"HCL_U_Reno1811_(\w+)", cls)
    if m and m[1] in RENO_UNI:
        return f"[HCL] Coat {'1810' if m[1].startswith('SAX') else '1811'} - {RENO_UNI[m[1]]}"
    m = re.fullmatch(r"HCL_H_Reno1811_(\w+)", cls)
    if m and m[1] in RENO_HEAD:
        return f"[HCL] {RENO_HEAD[m[1]]}"
    m = re.fullmatch(r"HCL_Italia1812_Soldado_" + ITA_PRE + ITA_KEY, cls)
    if m:
        return f"Soldier, {_ita(m[1], m[2])}{T}"
    if cls == "HCL_Italia1812_Soldado_Base":
        return "Soldier, Kingdom of Italy / Naples 1812" + T
    if cls == "HCL_Italia1812_Soldado_Elite_Base":
        return "Soldier, Kingdom of Italy / Naples 1812, elite company" + T
    m = re.fullmatch(r"HCL_U_Italia1812_" + ITA_PRE + ITA_KEY, cls)
    if m:
        return f"[HCL] Coat 1812 - {_ita(m[1], m[2])}"
    m = re.fullmatch(r"HCL_H_Italia1812_(\w+)", cls)
    if m and m[1] in ITA_HEAD:
        return f"[HCL] {ITA_HEAD[m[1]]}"
    m = re.fullmatch(r"HCL_Varsovia1810_Soldado_(?:(Granadeiro|Voltigeur|Fuzileiro)_)?(L1810|R\d\d)", cls)
    if m:
        return f"Duchy of Warsaw Infantryman - {VARS_UNI[m[2]]}, {VARS_COMP[m[1] or '']}{T}"
    if cls == "HCL_Varsovia1810_Soldado_Base":
        return "Duchy of Warsaw Infantryman 1810" + T
    if cls == "HCL_Varsovia1810_Soldado_Elite_Base":
        return "Duchy of Warsaw Infantryman 1810, elite company" + T
    m = re.fullmatch(r"HCL_U_Varsovia1810_(?:(Granadeiro|Voltigeur|Fuzileiro)_)?(L1810|R\d\d)", cls)
    if m:
        return f"[HCL] Duchy of Warsaw Kurtka 1810 - {VARS_UNI[m[2]]}, {VARS_COMP[m[1] or '']}"
    m = re.fullmatch(r"HCL_H_Varsovia1810_(\w+)", cls)
    if m and m[1] in VARS_HEAD:
        return f"[HCL] Duchy of Warsaw {VARS_HEAD[m[1]]}"
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
