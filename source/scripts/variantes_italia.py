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

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for name, d in (("variantes_italia.json", line), ("variantes_italia_elite.json", elite)):
    json.dump(d, open(os.path.join(out, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", name, len(d), "variantes")
