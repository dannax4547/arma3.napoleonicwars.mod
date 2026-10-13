# Colour variants of the four Swiss regiments in French service, 1812 (spec docs/specs/aliados_fr_1812.md section 4;
# user decisions 2026-10-13: A4 grenadiers + voltigeurs in the first lot, A6 2nd and 4th as recolours, marked 🔶).
# Writes the variant files read by generate_uniform_textures_v2.py (unchanged, shared painter):
#   source/textures/hcl_uniforme_suica/variantes_suica.json        line fusiliers, coat 1812 (HCL_U_Fr1812_01_LOD0)
#   source/textures/hcl_uniforme_suica/variantes_suica_elite.json  grenadiers / voltigeurs, coat with epaulettes
#                                                                   (HCL_U_Fr1812_Elite_LOD0)
# Colours are sRGB palette values, the same numbers as the French and Prussian variants (red, yellow, white, black of
# variantes_fr.json F02/F04; sky blue of the Prussian V08), so the nations match side by side.
# SOURCES per regiment:
#   1st: Wikipedia "1st Swiss Regiment (France)", 1812 regulations: red coat, yellow collar, closed yellow lapels,
#        both piped red; cuff flaps piped white; fusiliers red shoulder straps piped yellow; grenadiers red
#        epaulettes (✅ read). Turnbacks yellow and brass buttons as the mod tile FranceINF_3 c5 r0 (🎮).
#   3rd: Wikipedia "3rd Swiss Regiment (France)" citing Fieffé 1854 p. 299: red coat, black facings, white piping
#        (✅ read). Turnbacks, straps and buttons follow the 1st's pattern (🔶).
#   2nd: no colour source found (❓); royal blue facings, white piping 🔶 (general knowledge, user accepted A6).
#   4th: "blue facings" only on miniature shop pages (🔶); sky blue, white piping 🔶.
# Elite companies follow the French line pattern of variantes_fr_elite.json (🔶 for the Swiss): grenadiers red
# epaulettes with yellow keeper and red grenades on the turnbacks; voltigeurs green epaulettes with yellow crescent and
# horns on the turnbacks. The regiment's collar is kept for voltigeurs (no source for a chamois collar on Swiss coats).
#   python variantes_suica.py <out dir>
import json, os, sys

RED, YEL, WHI, BLK = [0.62, 0.07, 0.07], [0.8, 0.6, 0.12], [0.86, 0.85, 0.8], [0.035, 0.035, 0.04]
ROYAL, SKY, GREEN = [0.1, 0.18, 0.46], [0.4, 0.6, 0.8], [0.07, 0.26, 0.11]
BRASS = [0.8, 0.62, 0.28]
LOWER = {"calca": [0.84, 0.83, 0.78], "polaina": [0.045, 0.045, 0.045], "sapato": [0.03, 0.028, 0.025],
         "sola": [0.2, 0.13, 0.08]}

# regiment: (facing, piping of collar/lapels, piping of cuffs/turnbacks, flap piping, english colour word, confidence)
REG = {
    1: (YEL, RED, RED, WHI, "yellow", "1812 regulations, Wikipedia (✅); turnbacks/buttons from the mod (🎮)"),
    2: (ROYAL, WHI, WHI, WHI, "royal blue", "no colour source (❓): royal blue 🔶, accepted by the user (A6)"),
    3: (BLK, WHI, WHI, WHI, "black", "Fieffé 1854 via Wikipedia (✅); turnbacks/straps 🔶"),
    4: (SKY, WHI, WHI, WHI, "sky blue", "'blue facings' on shop pages only (🔶): sky blue 🔶 (A6)"),
}
PT = {1: "amarelas", 2: "azul-real", 3: "pretas", 4: "azul-celeste"}


def coat(n):
    fac, pip_cl, pip_cv, pip_flap, _, _ = REG[n]
    c = {"casaca": RED, "gola": fac, "gola_debrum": pip_cl, "lapela": fac, "lapela_debrum": pip_cl,
         "punho": fac, "punho_debrum": pip_cv, "pala": RED, "debrum": pip_flap, "viras": fac, "viras_debrum": pip_cv,
         "platina": RED, "platina_borda": fac, "botoes": BRASS}
    c.update(LOWER)
    return c


line, elite = {}, {}
for n, (fac, _, _, _, en, conf) in REG.items():
    line[f"S{n}"] = {"prefixo": f"hcl_u_suica1812_s{n}", "curto": f"{n}o suico, vistas {PT[n]}",
                     "nome": f"{n}o Regimento Suico: casaca vermelha, gola, lapelas, punhos e viradas {PT[n]}",
                     "fonte": conf, "cores": coat(n)}
    g = coat(n)
    g.update({"platina": RED, "platina_borda": YEL, "dragona": RED, "dragona_meialua": RED, "dragona_passante": YEL,
              "ornamento_cor": RED})
    elite[f"Granadeiro_S{n}"] = {"prefixo": f"hcl_u_suica1812_elite_gr{n}", "viras_externas": True, "ornamento": "granada",
                                 "curto": f"{n}o suico, granadeiro", "fonte": conf + "; elite pattern of the French line 🔶",
                                 "nome": f"{n}o Regimento Suico, granadeiro: dragonas vermelhas, granadas nas viradas",
                                 "cores": g}
    v = coat(n)
    # horns: yellow, except on the 1st's yellow turnbacks, where they would vanish -> green (🔶)
    v.update({"platina": GREEN, "platina_borda": YEL, "dragona": GREEN, "dragona_meialua": YEL, "dragona_passante": YEL,
              "ornamento_cor": GREEN if n == 1 else YEL})
    elite[f"Voltigeur_S{n}"] = {"prefixo": f"hcl_u_suica1812_elite_vo{n}", "viras_externas": True, "ornamento": "corneta",
                                "curto": f"{n}o suico, voltigeur", "fonte": conf + "; elite pattern of the French line 🔶",
                                "nome": f"{n}o Regimento Suico, voltigeur: dragonas verdes de meia-lua amarela, cornetas nas viradas",
                                "cores": v}

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, d in (("variantes_suica.json", line), ("variantes_suica_elite.json", elite)):
    json.dump(d, open(os.path.join(out, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", name, len(d), "variantes")
