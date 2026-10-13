# English display names of every class of the test addons (user 2026-10-13: "muda os nomes de tudo para os seus
# respectivos regimentos e em ingles"). Only displayName changes; the class names (HCL_...) stay, so saved loadouts and
# missions keep working. gen_config_pruss.py / gen_config_fr.py call apply() on the finished config text; it replaces
# the displayName of every listed class and fails if any displayName is left without an English name.
# REGIMENT NAMES: the mod files carry no unit table, so a regiment is named ONLY where a cited source supports the
# colours read on the mod art (🔶 = secondary/hobby source, to be checked against Knötel or Osprey); everything else
# keeps an English descriptive name, "unidentified" where the colours match no source found.
#   Prussia 1808-1813 line: collar = province (Silesia yellow, Pomerania white; Brandenburg and East Prussia both
#   red shades, so red collars stay unidentified), shoulder strap = seniority within the province (white 1st, red 2nd,
#   yellow 3rd, light blue 4th) - Gripping Beast/Calpe Miniatures and miniatures.de (🔶).
#   Silesian Schützen Battalion: green, black facings piped red - Gripping Beast/Calpe (🔶).
#   Landwehr cap band = provincial colour: Silesia yellow, Pomerania white (same sources, 🔶).
#   1st Swiss Regiment (French service), 1812 regulations: red coat, yellow collar, closed yellow lapels, yellow cuffs
#   - Wikipedia "1st Swiss Regiment (France)" (🔶; the mod's piping is white, the article says red).
#   Old Guard: requested by the user (docs/specs/velha_guarda.md).
import re

T = " (HCL test)"

PRUSS_UNI = {
    "V01": "Line Infantry, red facings, white straps, brass buttons (regiment unidentified)",
    "V02": "Line Infantry, red facings, white straps, white buttons (regiment unidentified)",
    "V03": "Line Infantry, red collar, black cuffs, red straps (regiment unidentified)",
    "V04": "Line Infantry, red facings, yellow straps, white buttons (regiment unidentified)",
    "V05": "1st Silesian Infantry Regiment",
    "V06": "2nd Silesian Infantry Regiment",
    "V07": "2nd Pomeranian Infantry Regiment",
    "V08": "Line Infantry, light blue facings (regiment unidentified)",
    "V09": "Jaeger, green coat, red facings, red straps (unit unidentified)",
    "V10": "Jaeger, green coat, red facings, white straps (unit unidentified)",
    "V11": "Jaeger, green coat, red facings, yellow lace (unit unidentified)",
    "V12": "Jaeger, green coat, red facings, yellow lace, white buttons (unit unidentified)",
    "V13": "Jaeger, green coat, white facings, blue straps (unit unidentified)",
    "V14": "Jaeger, green coat, white facings, white straps (unit unidentified)",
    "V15": "Silesian Schuetzen Battalion (red straps)",
    "V16": "Silesian Schuetzen Battalion (white straps)",
    "V17": "Jaeger, green coat, red collar, white cuffs (unit unidentified)",
}
FR_UNI = {
    "F01": "Line Infantry, Fusiliers (1812 regulation)",
    "F02": "Line Infantry, black facings (regiment unidentified)",
    "F03": "Foreign Regiment, yellow coat, red facings (unidentified)",
    "F04": "1st Swiss Regiment",
    "W01": "Line Infantry, beige, white trousers",
    "W02": "Line Infantry, grey, white trousers",
    "W03": "Line Infantry, beige, blue trousers",
    "W04": "Line Infantry, grey, grey trousers",
    "W05": "Imperial Guard, Foot Grenadiers (Old Guard), blue campaign greatcoat",
    "Granadeiro_F01": "Line Infantry, Grenadier Company",
    "Voltigeur_F01": "Line Infantry, Voltigeur Company",
    # light infantry (mod FranceINF c0 r2, 2026-10-13); regiment numbers unknown
    "Ligeira_Cacador": "Light Infantry, Chasseur Company",
    "Ligeira_Carabineiro": "Light Infantry, Carabinier Company",
    "Ligeira_Voltigeur": "Light Infantry, Voltigeur Company",
    "Guarda_Granadeiro": "Imperial Guard, Foot Grenadiers (Old Guard)",
    "Guarda_Cacador": "Imperial Guard, Foot Chasseurs (Old Guard)",
}
COMP = {"1a": "1st Company, dark green pompom", "2a": "2nd Company, sky blue pompom", "3a": "3rd Company, aurore pompom",
        "4a": "4th Company, violet pompom"}
TOK = [("Estrela_Prata", "silver star"), ("Estrela_Latao", "brass star"), ("FWR", "FWR cipher"), ("Aguia", "eagle"),
       ("_Amarela", ", yellow cockade loop"), ("_Branca", ", white cockade loop"), ("_PresilhaPreta", ", black cockade loop"),
       ("_LinhaVerde", ", green band line"), ("_LinhaLatao", ", brass band line"), ("_LinhaBranca", ", white band line"),
       ("_PlumetVerde", ", green plume"), ("_StutzGarde", ", Foot Guards white-over-black Stutz")]
BONE = {"C01": "blue, red band (Brandenburg or East Prussia, unidentified)", "C02": "blue, yellow band (Silesian Landwehr)",
        "C03": "green, black band (unidentified)", "C04": "blue, green band (unidentified)",
        "C05": "blue, white band (Pomeranian Landwehr)"}
FR_SHAKO = {"Granadeiro_Gala": "Grenadier, full dress (plume and cords)", "Granadeiro_Campanha": "Grenadier, campaign (pompom)",
            "Voltigeur_Gala": "Voltigeur, full dress (plume and cords)", "Voltigeur_Campanha": "Voltigeur, campaign (pompom)",
            "Oficial_Coronel": "Officer, Colonel",
            "Ligeira_Carabineiro_Gala": "Light Infantry, Carabinier, full dress (plume and cords, white metal)",
            "Ligeira_Voltigeur_Gala": "Light Infantry, Voltigeur, full dress (plume and cords, white metal)"}
# numbered line regiments (plate number, numerar_placa_fr.py); sobriquets are well known (🔶 to be checked)
LINHA = {18: "18th Line Infantry Regiment (le Brave)", 46: "46th Line Infantry Regiment",
         57: "57th Line Infantry Regiment (le Terrible)", 84: "84th Line Infantry Regiment (Un contre Dix)"}
BONNET = {"Granadeiro_Gala": "Foot Grenadiers, full dress (plate, braid, plume)", "Granadeiro_Campanha": "Foot Grenadiers, campaign (plate)",
          "Cacador_Gala": "Foot Chasseurs, full dress (braid, plume)"}


def name(cls):
    m = re.fullmatch(r"HCL_Pruss1813_Soldado_(V\d\d)", cls)
    if m:
        return f"Prussian Infantryman 1813 - {PRUSS_UNI[m[1]]}{T}"
    if cls == "HCL_Pruss1813_Soldado_Base":
        return "Prussian Infantryman 1813" + T
    m = re.fullmatch(r"HCL_U_Pruss1813_(V\d\d)", cls)
    if m:
        return f"[HCL] Prussian Kollet 1813 - {PRUSS_UNI[m[1]]}"
    m = re.fullmatch(r"HCL_H_Pruss1813_Bone_(C\d\d)", cls)
    if m:
        return f"[HCL] Prussian Landwehr Cap 1813 - {BONE[m[1]]}"
    m = re.fullmatch(r"HCL_H_Pruss1813_(\w+)", cls)
    if m:
        s = m[1]
        for k, v in TOK:
            s = s.replace(k, v)
        assert not re.search(r"[A-Z][a-z]+_|_", s), (cls, s)
        return f"[HCL] Prussian Shako 1813 - {s}"
    if cls.startswith("HCL_V_Pruss1813_Correame"):
        return "[HCL] Prussian Crossbelts 1813 - " + ("black leather" if cls.endswith("_Preto") else "whitened leather") + T
    if cls.startswith("HCL_B_Pruss1813_Tornister"):
        return "[HCL] Prussian Knapsack 1813 - " + ("black leather" if cls.endswith("_Preto") else "whitened leather") + T
    # France
    m = re.fullmatch(r"HCL_Fr1812_Soldado_(?:Capote_)?(\w+)", cls)
    if m and m[1] in FR_UNI:
        return f"French Infantryman - {FR_UNI[m[1]]}{', greatcoat' if 'Capote' in cls else ''}{T}"
    bases = {"HCL_Fr1812_Soldado_Base": "French Infantryman 1812", "HCL_Fr1812_Soldado_Capote_Base": "French Infantryman 1812, greatcoat",
             "HCL_Fr1812_Soldado_Elite_Base": "French Infantryman 1812, elite company",
             "HCL_Fr1812_Soldado_Guarda_Base": "French Imperial Guard infantryman"}
    if cls in bases:
        return bases[cls] + T
    m = re.fullmatch(r"HCL_U_Fr1812_(?:Capote_)?(\w+)", cls)
    if m and m[1] in FR_UNI:
        kind = "Imperial Guard Habit" if m[1].startswith("Guarda") else ("French Greatcoat" if "Capote" in cls else "French Coat 1812")
        return f"[HCL] {kind} - {FR_UNI[m[1]].replace('Imperial Guard, ', '')}"
    m = re.fullmatch(r"HCL_H_Fr1812_Guarda_Bonnet_(\w+)", cls)
    if m:
        return f"[HCL] Imperial Guard Bearskin - {BONNET[m[1]]}"
    m = re.fullmatch(r"HCL_H_Fr1812_Fuzileiro(_Losango|_LosangoBranco)?_(\d)aComp", cls)
    if m:
        if m[1] == "_LosangoBranco":         # white metal = light infantry (2026-10-13)
            return f"[HCL] French Light Infantry Shako - Chasseur, {COMP[m[2] + 'a']}, lozenge plate, white metal"
        plate = {None: "eagle plate", "_Losango": "1810 lozenge plate, brass"}[m[1]]
        return f"[HCL] French Line Shako 1812 - Fusilier, {COMP[m[2] + 'a']}, {plate}"
    m = re.fullmatch(r"HCL_H_Fr1812_Linha_(\d+)", cls)
    if m:
        return f"[HCL] French Line Shako 1812 - {LINHA[int(m[1])]}, Fusilier, numbered eagle plate"
    m = re.fullmatch(r"HCL_H_Fr1812_(\w+)", cls)
    if m and m[1] in FR_SHAKO:
        if m[1].startswith("Ligeira"):
            return f"[HCL] French Light Infantry Shako - {FR_SHAKO[m[1]].replace('Light Infantry, ', '')}"
        return f"[HCL] French Line Shako 1812 - {FR_SHAKO[m[1]]}"
    if cls == "HCL_V_Fr1812_Correame":
        return "[HCL] French Infantry Crossbelts 1812" + T
    if cls == "HCL_B_Fr1812_Havresac":
        return "[HCL] French Infantry Knapsack (havresac) 1812" + T
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
