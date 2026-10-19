# Colour variants of the Kingdom of Italy and Kingdom of Naples line infantry, c. 1812 (spec docs/specs/aliados_fr_1812.md
# section 3; user 2026-10-18: "utilize fontes historicas de museus e documentos"). Writes the variant files read by
# generate_uniform_textures_v2.py (unchanged, shared painter):
#   source/textures/hcl_uniforme_italia/variantes_italia.json        coat 1812 cut (HCL_U_Fr1812_01_LOD0)
#   source/textures/hcl_uniforme_italia/variantes_italia_elite.json  coat with epaulettes (HCL_U_Fr1812_Elite_LOD0)
# SOURCES:
#   Italy  white coat of French cut since 1806 (it.wikipedia after Pivka & Chappell, Osprey MAA 43 p. 23; Knoetel,
#          Uniformenkunde III/25: "weisse Uniformen ... roth, gruen und weiss"). Regimental table (Schultheis 1996 via
#          miniatures.de, 🔶) checked against the coloured prints of 1812 in the Vinkhuijzen collection (NYPL
#          b14896507-1528382..87, captions by the collector): 3rd all red, 4th white lapels and red collar, 5th green
#          lapels and red collar, 7th white lapels and green collar, 1st red lapels. Buttons per the table 🔶. Turnbacks
#          white piped with the facing colour, cuff flaps white piped 🔶 (not readable on the prints).
#   Naples white habit-veste with closed lapels (Decree 821, 1810/11, cited by M. Gaertner). 7th: collar, lapels,
#          turnbacks and cuffs YELLOW, brass buttons, white piping on cuffs and turnbacks (Freiberger Bilderhandschrift
#          1813 and others via Gaertner, Depesche 1). 1st scarlet, 2nd green, 5th blue (Knoetel, Uniformenkunde V/46:
#          "scheinen ... gewesen zu sein" 🔶; 5th light blue on VI/23).
#   elite  Italy: grenadiers red epaulettes, voltigeurs green epaulettes with yellow crescents (it.wikipedia / Osprey).
#          Naples: grenadiers red, voltigeurs yellow (Gaertner).
# Colours are sRGB palette values, the same family as variantes_varsovia.py.
#   python variantes_italia.py <out dir>
import json, os, sys

WHI, RED, GREEN = [0.86, 0.85, 0.8], [0.62, 0.07, 0.07], [0.07, 0.26, 0.11]
SCARLET, YEL, LBLUE = [0.7, 0.08, 0.06], [0.8, 0.6, 0.12], [0.42, 0.6, 0.84]
NGREEN = [0.1, 0.32, 0.14]
BRASS, TIN = [0.8, 0.62, 0.28], [0.74, 0.75, 0.76]
LOWER = {"calca": [0.84, 0.83, 0.78], "polaina": [0.06, 0.06, 0.07], "sapato": [0.03, 0.028, 0.025],
         "sola": [0.2, 0.13, 0.08]}


def italy(gola, lapela, punho, botoes, gola_debrum=None, lapela_debrum=None, punho_debrum=None, vivo=None):
    """White coat; piping in the regiment's distinctive colour (vivo) where the part itself is white."""
    vivo = vivo or next(c for c in (lapela, gola, punho) if c is not WHI)
    c = {"casaca": WHI, "gola": gola, "gola_debrum": gola_debrum or (vivo if gola is WHI else gola),
         "lapela": lapela, "lapela_debrum": lapela_debrum or (vivo if lapela is WHI else lapela),
         "punho": punho, "punho_debrum": punho_debrum or (vivo if punho is WHI else punho),
         "pala": WHI, "debrum": vivo, "viras": WHI, "viras_debrum": vivo,
         "platina": WHI, "platina_borda": vivo, "botoes": botoes}
    c.update(LOWER)
    return c


def naples(fac, botoes=BRASS):
    """White habit-veste, everything in the facing colour, white piping on cuffs and turnbacks (7th, Freiberg)."""
    c = {"casaca": WHI, "gola": fac, "gola_debrum": fac, "lapela": fac, "lapela_debrum": fac,
         "punho": fac, "punho_debrum": WHI, "pala": fac, "debrum": fac, "viras": fac, "viras_debrum": WHI,
         "platina": WHI, "platina_borda": fac, "botoes": botoes}
    c.update(LOWER)
    return c


IT = {  # (collar, lapels, cuffs, buttons, extra) - Schultheis table
    "IT01": (GREEN, RED, RED, BRASS, {}),
    "IT02": (WHI, RED, WHI, BRASS, {"vivo": RED}),
    "IT03": (RED, RED, RED, BRASS, {}),
    "IT04": (RED, WHI, WHI, TIN, {"vivo": GREEN}),
    "IT05": (RED, GREEN, GREEN, TIN, {}),
    "IT06": (WHI, GREEN, WHI, BRASS, {"vivo": GREEN}),
    "IT07": (GREEN, WHI, RED, TIN, {"vivo": GREEN}),
}
IT_TXT = {"IT01": "gola verde, lapelas e canhoes vermelhos, latao", "IT02": "gola branca debruada de vermelho, lapelas vermelhas, latao",
          "IT03": "gola, lapelas e canhoes vermelhos, latao", "IT04": "gola vermelha, lapelas e canhoes brancos debruados de verde, estanho",
          "IT05": "gola vermelha, lapelas e canhoes verdes, estanho", "IT06": "gola branca, lapelas verdes, canhoes brancos, latao",
          "IT07": "gola verde, lapelas brancas, canhoes vermelhos, estanho"}
GRAVURA = {"IT01", "IT03", "IT04", "IT05", "IT07"}       # seen on the 1812 prints (collector's captions)
NA = {"NA01": (SCARLET, "escarlate", "Knoetel V/46 🔶"), "NA02": (NGREEN, "verde", "Knoetel V/46 🔶"),
      "NA05": (LBLUE, "azul-claro", "Knoetel V/46 e VI/23 🔶"),
      "NA07": (YEL, "amarelo", "Freiberger Bilderhandschrift 1813 e outras, via Gaertner (Depesche 1)")}

line, elite = {}, {}
for k, (g, l, p, b, kw) in IT.items():
    n = int(k[2:])
    line[k] = {"prefixo": f"hcl_u_italia1812_{k.lower()}", "curto": f"Italia {n}o",
               "nome": f"Reino da Italia, {n}o de Linha: casaca branca, {IT_TXT[k]}",
               "fonte": "tabela de Schultheis 1996 🔶" + (" + gravura de 1812 (Vinkhuijzen, NYPL)" if k in GRAVURA else ""),
               "cores": italy(g, l, p, b, **kw)}
for k, (fac, txt, src) in NA.items():
    n = int(k[2:])
    line[k] = {"prefixo": f"hcl_u_italia1812_{k.lower()}", "curto": f"Napoles {n}o",
               "nome": f"Reino de Napoles, {n}o de Linha: casaca branca, distintivo {txt}",
               "fonte": src + "; Decreto 821 (habit-veste)", "cores": naples(fac)}


def ep(c, col, crescent=None):
    c = dict(c)
    c.update({"platina": col, "platina_borda": col, "dragona": col, "dragona_meialua": crescent or col,
              "dragona_passante": col})
    return c


# elite companies only for the regiments whose colours a period image supports (Italy 3rd and 5th, Naples 7th)
for k in ("IT03", "IT05", "NA07"):
    base = line[k]["cores"]
    gr, vo = (RED, None), ((GREEN, YEL) if k.startswith("IT") else (YEL, None))
    elite[f"Granadeiro_{k}"] = {"prefixo": f"hcl_u_italia1812_elite_{k.lower()}_gr", "viras_externas": True,
                                "curto": f"{line[k]['curto']}, granadeiro", "nome": f"{line[k]['nome']}; granadeiro, dragonas vermelhas",
                                "fonte": line[k]["fonte"], "cores": ep(base, *gr)}
    elite[f"Voltigeur_{k}"] = {"prefixo": f"hcl_u_italia1812_elite_{k.lower()}_vo", "viras_externas": True,
                               "curto": f"{line[k]['curto']}, voltigeur",
                               "nome": f"{line[k]['nome']}; voltigeur, dragonas " + ("verdes com crescente amarelo" if k.startswith("IT") else "amarelas"),
                               "fonte": line[k]["fonte"], "cores": ep(base, *vo)}

# ---- lote 2 (user 2026-10-18, "FAZ ESTES REGIMENTOS", Vinkhuijzen plates NYPL b14896507, Italy 1812, nos. 175-204 of
# the Commons category; every plate is a watercolour with the collector's caption, so names follow the caption and
# shades are read on the scan 🔶). Light infantry after Knoetel III/25 too ("wie in Frankreich ... die Carabiniers ... die
# Pelzmuetze und die Grenadierepauletten, die Voltigeure den Czako und die gruenen Voltigeurepaulettes").
#   LE01  "Leggiero Infanterie 1 Reg." (b..-1528327): dark green coat and trousers, RED collar and cuffs, white piping
#   LE03  "Carabiniere 3 Reg. Leggiero" (-1528323): WHITE collar, white piping, red epaulettes
#   LE04  "4 Regiment Leggiero" (-1528324): VIOLET collar, white piping, green epaulettes
#   LEX   "Carabiniere / Volteggiatore della fanteria leggiera" (-1528321/22, no number): YELLOW collar
#   DAL   "Reggimento Dalmato" (-1528325/26): dark green coat, red collar, cuffs and turnbacks, red epaulettes
#   RES   "Compagnie di riserva della Fanteria di linea" (-1528320): dark green coat, red collar and cuffs (Knoetel: "fast
#         dieselbe Uniform" as the green voltigeurs, without their epaulettes)
#   MIL   "Guardia di Milano" (-1528319): light blue coat, red collar and cuffs
#   VOL   "Volontario" (-1528317): dark green coat, yellow collar and lapels
#   BRE   "Bersagliere di Brescia" (-1528318; Knoetel III/25 "Scharfschuetz von Brescia"): dark green coat, light green
#         collar and piping, grey trousers
#   DRA   "Reg. Dragoni Regina" (-1528315): dark green coat, ROSE lapels and turnbacks, white buttons (coat only)
#   ART   "Battaglione d'Artiglieria" (-1528316, caption read with doubt ❓): dark green coat, red piping and epaulettes
#   line  voltigeurs: GREEN coat, red collar, green epaulettes ("Volteggiatore della fanteria di linea", -1528328; Knoetel
#         III/25 "Die Voltigeure (Volteggiatori) waren gruen uniformiert") -> Voltigeur_IT03/IT05 were white, now green.
#         6th grenadier ("6 Reg. Granatiere", -1528330): the 6th's white coat with red epaulettes.
#         officers ("Lieutenant Linie Infanterie 1 / 4 Regiment", "... Grenadier 5 Regiment", -1528337/33/34): the
#         regiment's coat with silver epaulettes (as painted).
DKG, VIOLET, ROSE = [0.05, 0.16, 0.09], [0.42, 0.30, 0.62], [0.72, 0.25, 0.42]
LBLUE_M, LGREEN, GREY = [0.55, 0.62, 0.85], [0.35, 0.62, 0.30], [0.52, 0.52, 0.5]
SILVER = [0.8, 0.8, 0.82]


def coat(casaca, gola, lapela, punho, vivo, viras, botoes=BRASS, calca=None, **kw):
    c = {"casaca": casaca, "gola": gola, "gola_debrum": vivo, "lapela": lapela, "lapela_debrum": vivo,
         "punho": punho, "punho_debrum": vivo, "pala": casaca, "debrum": vivo, "viras": viras, "viras_debrum": vivo,
         "platina": casaca, "platina_borda": vivo, "botoes": botoes}
    c.update(LOWER)
    if calca:
        c["calca"] = calca
    c.update(kw)
    return c


VK = "aquarela da colecao Vinkhuijzen (NYPL), 1812, legenda do colecionador 🔶"
LIGHT = {"LE01": (RED, "1o Ligeiro", "gola e canhoes vermelhos"), "LE03": (WHI, "3o Ligeiro", "gola branca"),
         "LE04": (VIOLET, "4o Ligeiro", "gola violeta"), "LEX": (YEL, "Ligeira, gola amarela", "gola amarela (regimento sem numero)")}
for k, (col, curto, txt) in LIGHT.items():
    c = coat(DKG, col, DKG, col if k == "LE01" else DKG, WHI, DKG, TIN, calca=DKG)
    if k in ("LE01", "LE03", "LE04"):
        line[k] = {"prefixo": f"hcl_u_italia1812_{k.lower()}", "curto": curto,
                   "nome": f"Reino da Italia, {curto}: casaca e calca verde-escuras, {txt}, vivos brancos", "fonte": VK, "cores": c}
    if k in ("LE01", "LE03", "LEX"):
        elite[f"Carabiniere_{k}"] = {"prefixo": f"hcl_u_italia1812_elite_{k.lower()}_ca", "viras_externas": True, "curto": f"{curto}, carabineiro",
                                     "nome": f"Reino da Italia, {curto}, carabineiro: {txt}, dragonas vermelhas", "fonte": VK + "; Knoetel III/25",
                                     "cores": ep(c, RED)}
    if k in ("LE01", "LE04", "LEX"):
        elite[f"Voltigeur_{k}"] = {"prefixo": f"hcl_u_italia1812_elite_{k.lower()}_vo", "viras_externas": True, "curto": f"{curto}, voltigeur",
                                   "nome": f"Reino da Italia, {curto}, voltigeur: {txt}, dragonas verdes", "fonte": VK + "; Knoetel III/25",
                                   "cores": ep(c, GREEN, YEL)}
dal = coat(DKG, RED, DKG, RED, RED, RED)
line["DAL"] = {"prefixo": "hcl_u_italia1812_dal", "curto": "Regimento Dalmata", "fonte": VK,
               "nome": "Reino da Italia, Regimento Dalmata: casaca verde-escura, gola, canhoes e viras vermelhos", "cores": dal}
elite["Granadeiro_DAL"] = {"prefixo": "hcl_u_italia1812_elite_dal_gr", "viras_externas": True, "curto": "Dalmata, granadeiro", "fonte": VK,
                           "nome": "Reino da Italia, Regimento Dalmata, granadeiro: dragonas vermelhas", "cores": ep(dal, RED)}
line["RES"] = {"prefixo": "hcl_u_italia1812_res", "curto": "Companhias de reserva", "fonte": VK + "; Knoetel III/25",
               "nome": "Reino da Italia, companhias de reserva da linha: casaca verde-escura, gola e canhoes vermelhos",
               "cores": coat(DKG, RED, DKG, RED, RED, WHI)}
line["MIL"] = {"prefixo": "hcl_u_italia1812_mil", "curto": "Guarda de Milao", "fonte": VK,
               "nome": "Reino da Italia, Guarda de Milao: casaca azul-clara, gola e canhoes vermelhos",
               "cores": coat(LBLUE_M, RED, LBLUE_M, RED, RED, WHI)}
line["VOL"] = {"prefixo": "hcl_u_italia1812_vol", "curto": "Voluntario", "fonte": VK,
               "nome": "Reino da Italia, voluntario: casaca verde-escura, gola e lapelas amarelas",
               "cores": coat(DKG, YEL, YEL, DKG, YEL, DKG, calca=DKG)}
line["BRE"] = {"prefixo": "hcl_u_italia1812_bre", "curto": "Bersaglieri de Brescia", "fonte": VK + "; Knoetel III/25",
               "nome": "Reino da Italia, Bersaglieri de Brescia: casaca verde-escura, gola e vivos verde-claros, calca cinza",
               "cores": coat(DKG, LGREEN, DKG, DKG, LGREEN, DKG, TIN, calca=GREY)}
line["DRA"] = {"prefixo": "hcl_u_italia1812_dra", "curto": "Dragoes da Rainha", "fonte": VK,
               "nome": "Reino da Italia, Dragoes da Rainha: casaca verde-escura, lapelas e viras rosa, botoes brancos",
               "cores": coat(DKG, DKG, ROSE, ROSE, ROSE, ROSE, TIN, calca=WHI)}
elite["ART"] = {"prefixo": "hcl_u_italia1812_elite_art", "viras_externas": True, "curto": "Artilharia", "fonte": VK + " (legenda lida com duvida)",
                "nome": "Reino da Italia, batalhao de artilharia: casaca verde-escura, vivos e dragonas vermelhos",
                "cores": ep(coat(DKG, DKG, DKG, RED, RED, RED, calca=DKG), RED)}
# line voltigeurs in GREEN (replaces the white Voltigeur_IT03 / IT05 of the first lot)
for k in ("IT03", "IT05"):
    elite[f"Voltigeur_{k}"].update({"nome": f"Reino da Italia, {int(k[2:])}o de Linha, voltigeur: casaca VERDE, gola vermelha, dragonas verdes",
                                    "fonte": VK + "; Knoetel III/25",
                                    "cores": ep(coat(DKG, RED, DKG, DKG, RED, DKG), GREEN, YEL)})
elite["Granadeiro_IT06"] = {"prefixo": "hcl_u_italia1812_elite_it06_gr", "viras_externas": True, "curto": "Italia 6o, granadeiro",
                            "nome": line["IT06"]["nome"] + "; granadeiro, dragonas vermelhas", "fonte": VK, "cores": ep(line["IT06"]["cores"], RED)}
for k, kk, src in (("Oficial_IT01", "IT01", "-1528337"), ("Oficial_IT04", "IT04", "-1528333"), ("Oficial_Granadeiro_IT05", "IT05", "-1528334")):
    elite[k] = {"prefixo": f"hcl_u_italia1812_elite_{kk.lower()}_of" + ("gr" if "Granadeiro" in k else ""), "viras_externas": True,
                "curto": f"Italia {int(kk[2:])}o, oficial", "nome": line[kk]["nome"] + "; oficial, dragonas de prata",
                "fonte": VK + f" ({src})", "cores": ep(line[kk]["cores"], SILVER)}

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, d in (("variantes_italia.json", line), ("variantes_italia_elite.json", elite)):
    json.dump(d, open(os.path.join(out, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", name, len(d), "variantes")
