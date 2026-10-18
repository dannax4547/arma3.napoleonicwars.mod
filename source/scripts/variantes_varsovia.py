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
g = coat(); g.update({"platina": CRIM, "platina_borda": CRIM, "dragona": CRIM, "dragona_meialua": CRIM, "dragona_passante": CRIM})
v = coat(gola=YEL, gola_debrum=CRIM)
v.update({"platina": GREEN, "platina_borda": GREEN, "dragona": GREEN, "dragona_meialua": GREEN, "dragona_passante": GREEN})
elite = {
    "Granadeiro_L1810": {"prefixo": "hcl_u_varsovia1810_elite_gr", "viras_externas": True, "curto": "granadeiro",
                         "nome": "Linha 1810, granadeiro: dragonas carmesim", "fonte": "📜 regulamento de 1810", "cores": g},
    "Voltigeur_L1810": {"prefixo": "hcl_u_varsovia1810_elite_vo", "viras_externas": True, "curto": "voltigeur",
                        "nome": "Linha 1810, voltigeur: gola amarela, dragonas verdes", "fonte": "📜 regulamento de 1810", "cores": v},
}
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, d in (("variantes_varsovia.json", line), ("variantes_varsovia_elite.json", elite)):
    json.dump(d, open(os.path.join(out, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", name, len(d), "variantes")
