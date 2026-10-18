# Colour variants of the Duchy of Warsaw line infantry (spec docs/specs/aliados_fr_1812.md section 1.1; user
# 2026-10-18: "utilize fontes historicas de museus e documentos"). Writes the variant files read by
# generate_uniform_textures_v2.py (unchanged, shared painter):
#   source/textures/hcl_uniforme_varsovia/variantes_varsovia.json        coat 1812 cut (HCL_U_Fr1812_01_LOD0)
#   source/textures/hcl_uniforme_varsovia/variantes_varsovia_elite.json  coat with epaulettes (HCL_U_Fr1812_Elite_LOD0)
# SOURCES (📜 = the regulation of 3 September 1810 as published by Gembarzewski 1905 and summarised by Zygulski &
# Wielecki 1988, read through pl.wikipedia "Mundur Armii Ksiestwa Warszawskiego" and napoleon.org.pl):
#   L1810  navy kurtka, WHITE lapels, CRIMSON collar, cuffs and piping (📜); yellow-metal buttons with the regiment
#          number (📜); fusiliers navy shoulder straps (📜). Turnbacks white piped crimson and navy cuff flaps 🔶.
#   R09    9th Regiment: crimson collar piped navy, white lapels, crimson cuffs piped white, navy cuff flaps, white
#          buttons (Askenazy & Gembarzewski, via Wikipedia "9th Infantry Regiment (Duchy of Warsaw)").
#   R07    7th Regiment: navy collar piped crimson, white buttons, cut of the 4th (Wikipedia "7th Infantry Regiment
#          (Duchy of Warsaw)", summary); lapels and cuffs as the regulation 🔶.
#   elite  grenadiers crimson epaulettes, voltigeurs green epaulettes and YELLOW collar (📜). No turnback ornaments
#          (none in the sources).
# Colours are sRGB palette values; red family as the French/Swiss variants, crimson darker and bluer (karmazyn).
#   python variantes_varsovia.py <out dir>
import json, os, sys

NAVY, CRIM, WHI = [0.07, 0.09, 0.22], [0.52, 0.04, 0.12], [0.86, 0.85, 0.8]
YEL, GREEN = [0.8, 0.6, 0.12], [0.07, 0.26, 0.11]
BRASS, TIN = [0.8, 0.62, 0.28], [0.74, 0.75, 0.76]
LOWER = {"calca": [0.84, 0.83, 0.78], "polaina": [0.06, 0.06, 0.07], "sapato": [0.03, 0.028, 0.025],
         "sola": [0.2, 0.13, 0.08]}


def coat(gola=CRIM, gola_debrum=CRIM, punho=CRIM, punho_debrum=CRIM, botoes=BRASS):
    c = {"casaca": NAVY, "gola": gola, "gola_debrum": gola_debrum, "lapela": WHI, "lapela_debrum": CRIM,
         "punho": punho, "punho_debrum": punho_debrum, "pala": NAVY, "debrum": CRIM, "viras": WHI, "viras_debrum": CRIM,
         "platina": NAVY, "platina_borda": CRIM, "botoes": botoes}
    c.update(LOWER)
    return c


line = {
    "L1810": {"prefixo": "hcl_u_varsovia1810_l1810", "curto": "regulamento de 1810",
              "nome": "Linha, regulamento de 3/9/1810: azul-marinho, lapelas brancas, gola e punhos carmesim",
              "fonte": "📜 regulamento de 1810 (Gembarzewski 1905; Zygulski & Wielecki 1988); viras e portinholas 🔶",
              "cores": coat()},
    "R09": {"prefixo": "hcl_u_varsovia1810_r09", "curto": "9o regimento",
            "nome": "9o Regimento: gola carmesim debruada de azul, punhos carmesim debruados de branco, botoes brancos",
            "fonte": "Askenazy & Gembarzewski via Wikipedia (9th Infantry Regiment)",
            "cores": coat(gola_debrum=NAVY, punho_debrum=WHI, botoes=TIN)},
    "R07": {"prefixo": "hcl_u_varsovia1810_r07", "curto": "7o regimento",
            "nome": "7o Regimento: gola azul-marinho debruada de carmesim, botoes brancos",
            "fonte": "Wikipedia (7th Infantry Regiment), resumo; lapelas e punhos do regulamento 🔶",
            "cores": coat(gola=NAVY, gola_debrum=CRIM, botoes=TIN)},
}

# ---- more regiments (user 2026-10-18: "so adiciona mais regimentos para a polonia"); deviations from the 1810
# regulation as quoted by the pl.wikipedia regiment articles (after Gembarzewski), shades 🔶:
#   1st: fusiliers with white woollen epaulettes with fringes ("szlify biale wloczkowe z fredzlami") -> elite coat mesh
#   13th: dressed at Zamosc in WHITE coats with BLUE piping from Austrian army stores, collars, cuffs and gold buttons
#         kept, BLUE lapels added; white trousers. Grenadiers red epaulettes, voltigeurs green ("Epolety czerwone",
#         "zielone ... epolety").
#   15th: fusiliers crimson lapels and collars, YELLOW shoulder straps; grenadiers crimson lapels, collars and shoulder
#         straps; voltigeurs green shoulder straps, YELLOW collars, AMARANTH lapels.
BLUE, AMAR, RED = [0.2, 0.38, 0.7], [0.55, 0.08, 0.3], [0.62, 0.07, 0.07]


def white13():
    c = coat(gola=WHI, gola_debrum=BLUE, punho=WHI, punho_debrum=BLUE)
    c.update({"casaca": WHI, "lapela": BLUE, "lapela_debrum": WHI, "pala": WHI, "debrum": BLUE, "viras": WHI,
              "viras_debrum": BLUE, "platina": WHI, "platina_borda": BLUE})
    return c


def r15(gola=CRIM, lapela=CRIM, platina=YEL):
    c = coat(gola=gola, gola_debrum=CRIM)
    c.update({"lapela": lapela, "lapela_debrum": WHI, "punho_debrum": WHI, "platina": platina, "platina_borda": platina})
    return c


line["R13"] = {"prefixo": "hcl_u_varsovia1810_r13", "curto": "13o regimento",
               "nome": "13o Regimento: casaca branca austriaca, vivos e lapelas azuis, botoes dourados",
               "fonte": "pl.wikipedia (13 Pulk Piechoty): mundury biale z niebieskimi wypustkami, niebieskie wyloki; tom de azul 🔶",
               "cores": white13()}
line["R15"] = {"prefixo": "hcl_u_varsovia1810_r15", "curto": "15o regimento",
               "nome": "15o Regimento, fuzileiros: lapelas e gola carmesim, platinas amarelas",
               "fonte": "pl.wikipedia (15 Pulk Piechoty); punhos e vivos 🔶", "cores": r15()}


def ep(c, col):
    c.update({"platina": col, "platina_borda": col, "dragona": col, "dragona_meialua": col, "dragona_passante": col})
    return c


g = ep(coat(), CRIM)
v = ep(coat(gola=YEL, gola_debrum=CRIM), GREEN)
elite = {
    "Granadeiro_L1810": {"prefixo": "hcl_u_varsovia1810_elite_gr", "viras_externas": True, "curto": "granadeiro",
                         "nome": "Linha 1810, granadeiro: dragonas carmesim", "fonte": "📜 regulamento de 1810", "cores": g},
    "Voltigeur_L1810": {"prefixo": "hcl_u_varsovia1810_elite_vo", "viras_externas": True, "curto": "voltigeur",
                        "nome": "Linha 1810, voltigeur: gola amarela, dragonas verdes", "fonte": "📜 regulamento de 1810", "cores": v},
    "Fuzileiro_R01": {"prefixo": "hcl_u_varsovia1810_elite_fu01", "curto": "1o regimento, fuzileiro",
                      "nome": "1o Regimento, fuzileiro: dragonas de la branca com franja",
                      "fonte": "pl.wikipedia (1 Pulk Piechoty): szlify biale wloczkowe z fredzlami", "cores": ep(coat(), WHI)},
    "Granadeiro_R13": {"prefixo": "hcl_u_varsovia1810_elite_gr13", "viras_externas": True, "curto": "13o, granadeiro",
                       "nome": "13o Regimento, granadeiro: casaca branca, dragonas vermelhas",
                       "fonte": "pl.wikipedia (13 Pulk Piechoty): Epolety czerwone", "cores": ep(white13(), RED)},
    "Voltigeur_R13": {"prefixo": "hcl_u_varsovia1810_elite_vo13", "viras_externas": True, "curto": "13o, voltigeur",
                      "nome": "13o Regimento, voltigeur: casaca branca, dragonas verdes",
                      "fonte": "pl.wikipedia (13 Pulk Piechoty): zielone ... epolety", "cores": ep(white13(), GREEN)},
    "Granadeiro_R15": {"prefixo": "hcl_u_varsovia1810_elite_gr15", "viras_externas": True, "curto": "15o, granadeiro",
                       "nome": "15o Regimento, granadeiro: lapelas, gola e dragonas carmesim",
                       "fonte": "pl.wikipedia (15 Pulk Piechoty)", "cores": ep(r15(), CRIM)},
    "Voltigeur_R15": {"prefixo": "hcl_u_varsovia1810_elite_vo15", "viras_externas": True, "curto": "15o, voltigeur",
                      "nome": "15o Regimento, voltigeur: gola amarela, lapelas amaranto, dragonas verdes",
                      "fonte": "pl.wikipedia (15 Pulk Piechoty)", "cores": ep(r15(gola=YEL, lapela=AMAR), GREEN)},
}
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, d in (("variantes_varsovia.json", line), ("variantes_varsovia_elite.json", elite)):
    json.dump(d, open(os.path.join(out, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", name, len(d), "variantes")
