# Colour variants of the Confederation of the Rhine infantry, lot 1: Wuerttemberg and Bavaria c. 1811, the two states
# with the crested helmet (blockout_raupenhelm.py); lot 2 (2026-10-27): Saxony 1810 (blockout_shako_reno.py). Spec docs/specs/aliados_fr_1812.md section 2.0; user 2026-10-19:
# "remember to add ALL of these regiments". Writes the variant file read by generate_uniform_textures_v2.py (unchanged,
# shared painter) on the 1812 coat (HCL_U_Fr1812_01_LOD0):
#   source/textures/hcl_uniforme_reno/variantes_reno.json
# SOURCE of every line: the Vinkhuijzen collection watercolours [VK-REN] (NYPL b14896507, albums "Wuerttemberg 1811" and
# "Baiern 1811"), plate index of the session contact sheets and the collector's caption, shades read on the scan 🔶.
# Buttons are not readable on the watercolours: Wuerttemberg after the 1813 list of [MD-W] (Knoetel-Sieg; 1st-5th white,
# 6th-9th yellow), Bavaria all brass except where noted ❓.
# The French coat mesh has lapels: the Wuerttemberg coat (closed, piped front on the watercolours) gets lapels in the
# coat colour piped with the facing colour, so it reads as a piped front; Bavaria has coloured lapels as painted.
#   python variantes_reno.py <out dir>
import json, os, sys

# sRGB palette (same family as variantes_italia.py)
WHI, RED, YEL = [0.86, 0.85, 0.8], [0.62, 0.07, 0.07], [0.8, 0.6, 0.12]
BLACK, ORANGE, PINK = [0.06, 0.06, 0.07], [0.85, 0.42, 0.12], [0.86, 0.55, 0.62]
LBLUE, CRIMSON_P, PALE = [0.42, 0.6, 0.84], [0.72, 0.25, 0.42], [0.85, 0.80, 0.55]
GREEN_F = [0.12, 0.40, 0.18]
DKB = [0.08, 0.10, 0.24]                 # Wuerttemberg dark blue
CORN = [0.40, 0.56, 0.80]                # Bavarian light ("cornflower") blue
DKG = [0.06, 0.18, 0.11]                 # Jaeger / light infantry dark green
BRASS, TIN = [0.8, 0.62, 0.28], [0.74, 0.75, 0.76]
LOWER = {"calca": [0.84, 0.82, 0.72], "polaina": [0.06, 0.06, 0.07], "sapato": [0.03, 0.028, 0.025],
         "sola": [0.2, 0.13, 0.08]}
GREY = [0.55, 0.56, 0.56]


def coat(casaca, gola, lapela, punho, vivo, viras, botoes, calca=None, gola_debrum=None, punho_debrum=None):
    c = {"casaca": casaca, "gola": gola, "gola_debrum": gola_debrum or vivo, "lapela": lapela, "lapela_debrum": vivo,
         "punho": punho, "punho_debrum": punho_debrum or vivo, "pala": casaca, "debrum": vivo, "viras": viras,
         "viras_debrum": vivo, "platina": casaca, "platina_borda": vivo, "botoes": botoes}
    c.update(LOWER)
    if calca:
        c["calca"] = calca
    return c


V = {}


def add(key, curto, nome, fonte, cores):
    V[key] = {"prefixo": f"hcl_u_reno1811_{key.lower()}", "curto": curto, "nome": nome, "fonte": fonte, "cores": cores}


VKW = "aquarela Vinkhuijzen (NYPL), album 'Wuerttemberg 1811', prancha {} ('{}'), legenda do colecionador 🔶"
# ---- Wuerttemberg: dark blue coat, collar and cuffs in the facing colour, piped front
WUE = [  # key, plate, caption, collar, cuffs, piping, buttons, text
    ("WUE01", "022", "1. Regiment Linie Prinz Paul", YEL, YEL, YEL, TIN, "1o Prinz Paul, amarelo"),
    ("WUE02", "020", "2. Linie Regiment Herzog Wilhelm", ORANGE, ORANGE, ORANGE, TIN, "2o Herzog Wilhelm, laranja"),
    ("WUE03", "021", "3. Linie Regiment Infanterie", WHI, WHI, WHI, TIN, "3o, branco"),
    ("WUE04", "019", "Linie Infanterie Regiment No 4", PINK, PINK, PINK, TIN, "4o, rosa"),
    ("WUE05", "018", "Lin. Regiment No 5 Prinz Friedrich, Grenadier", LBLUE, LBLUE, LBLUE, TIN, "5o Prinz Friedrich, azul-claro"),
    ("WUE06", "017", "Linie Infanterie Regiment No 6 Kronprinz", RED, WHI, RED, BRASS, "6o Kronprinz, gola vermelha, canhoes brancos debruados de vermelho"),
    ("WUE08", "016", "Linie Regiment Infanterie No 8 Neubronn", RED, RED, RED, BRASS, "8o von Neubronn, vermelho"),
    ("WUE09", "014", "Linie Infanterie Regiment No 9", RED, RED, RED, BRASS, "9o, vermelho (a lista de 1813 diz preto ❓)"),
]
for key, pl, cap, gola, punho, vivo, bot, txt in WUE:
    add(key, f"Wuerttemberg {txt.split(',')[0]}", f"Wuerttemberg 1811, {txt}: casaca azul-escura", VKW.format(pl, cap),
        coat(DKB, gola, DKB, punho, vivo, DKB, bot, punho_debrum=RED if key == "WUE06" else None))
add("WUE07", "Wuerttemberg 7o", "Wuerttemberg, 7o de Linha: casaca azul-escura, vermelho, botoes amarelos",
    "sem prancha em 1811: lista de 1813 de [MD-W] (Knoetel-Sieg pp. 78-79) 🔶", coat(DKB, RED, DKB, RED, RED, DKB, BRASS))
add("WUE10P", "Wuerttemberg ligeira 10 (preto)", "Wuerttemberg 1811, Infantaria Ligeira 'No 10': casaca verde-escura, peças pretas, vivo vermelho",
    VKW.format("012", "Leichte Infanterie Reg. No 10"), coat(DKG, BLACK, BLACK, BLACK, RED, DKG, TIN, calca=DKG))
add("WUE10A", "Wuerttemberg ligeira 10 (azul-claro)", "Wuerttemberg 1811, Infantaria Ligeira 'No 10': casaca verde-escura, peças azul-claras",
    VKW.format("013", "Regiment Leichte Infanterie No 10") + " - duas pranchas com o mesmo numero ❓", coat(DKG, LBLUE, LBLUE, LBLUE, LBLUE, DKG, TIN, calca=DKG))
add("WUEJK", "Wuerttemberg Jaeger Koenig", "Wuerttemberg 1811, 1o Batalhao de Jaeger 'Koenig': casaca verde-escura, peças pretas",
    VKW.format("011", "Erstes Bataillon Jaeger Koenig"), coat(DKG, BLACK, BLACK, BLACK, BLACK, DKG, BRASS, calca=DKG))

VKB = "aquarela Vinkhuijzen (NYPL), album 'Baiern 1811', prancha {} ('{}'), legenda do colecionador 🔶"
# ---- Bavaria: light blue coat, collar / lapels / cuffs as painted, white breeches
BAV = [  # key, plate, caption, collar, lapels, cuffs, piping, text
    ("BAV01", "003", "Infanterie Regiment Koenig No 1", RED, RED, RED, RED, "1o Koenig, vermelho"),
    ("BAV02", "005", "Infanterie Regiment Kronprinz No 2", RED, RED, RED, RED, "2o Kronprinz, vermelho (a prancha mostra alamares amarelos nas lapelas, nao pintados ❓)"),
    ("BAV04", "006", "Infanterie Regiment Sachsen-Hildburghausen No 4", YEL, YEL, YEL, YEL, "4o Sachsen-Hildburghausen, amarelo"),
    ("BAV06", "015", "Infanterie Regiment Herzog Wilhelm No 6", RED, RED, RED, RED, "6o Herzog Wilhelm, vermelho"),
    ("BAV07", "014", "Infanterie Regiment Loewenstein No 7", CRIMSON_P, CRIMSON_P, CRIMSON_P, CRIMSON_P, "7o Loewenstein, rosa-carmim"),
    ("BAV08", "013", "Infanterie Regiment Herzog Pius No 8", YEL, YEL, YEL, YEL, "8o Herzog Pius, amarelo"),
    ("BAV09", "012", "Infanterie Regiment Ysenburg No 9", RED, YEL, YEL, RED, "9o Ysenburg, gola vermelha, lapelas amarelas"),
    ("BAV10", "011", "Infanterie Regiment Junker No 10", RED, YEL, YEL, RED, "10o Junker, gola vermelha, lapelas amarelas (igual ao 9o na aquarela ❓)"),
    ("BAV11L", "010", "Infanterie Regiment Kinkel No 11 (figura da esquerda)", RED, ORANGE, ORANGE, RED, "prancha do 11o Kinkel, figura da esquerda: lapelas laranja ❓"),
    ("BAV11V", "010", "Infanterie Regiment Kinkel No 11 (figura do centro)", RED, GREEN_F, GREEN_F, RED, "prancha do 11o Kinkel, figura do centro: lapelas verdes ❓"),
    ("BAV11P", "010", "Infanterie Regiment Kinkel No 11 (figura da direita)", RED, BLACK, BLACK, RED, "prancha do 11o Kinkel, figura da direita: lapelas pretas ❓"),
    ("BAV13", "009", "Infanterie Regiment No 13", RED, BLACK, BLACK, RED, "13o, gola vermelha, lapelas pretas debruadas de vermelho"),
]
for key, pl, cap, gola, lap, punho, vivo, txt in BAV:
    add(key, f"Baviera {txt.split(',')[0]}", f"Baviera 1811, {txt}: casaca azul-clara", VKB.format(pl, cap),
        coat(CORN, gola, lap, punho, vivo, CORN, BRASS, calca=WHI))
LIGHT_BAV = [  # key, plate, caption, collar
    ("BAVL1", "007", "Leichte Infanterie Bataillon No 1 Gedoni", RED, "1o Batalhao Ligeiro Gedoni, gola vermelha"),
    ("BAVL2", "019", "Leichte Infanterie Bataillon No 2 Wreden", RED, "2o Batalhao Ligeiro Wreden, gola vermelha"),
    ("BAVL3", "018", "Leichte Infanterie Bataillon No 3 Bernclau", PALE, "3o Batalhao Ligeiro Bernclau, gola amarelo-palida ❓"),
    ("BAVL4", "017", "Leichte Infanterie Bataillon No 4 Theobald", BLACK, "4o Batalhao Ligeiro Theobald, gola preta"),
    ("BAVL5", "016", "Leichte Infanterie Bataillon No 5 Butler", YEL, "5o Batalhao Ligeiro Butler, gola amarela"),
    ("BAVL6", "021", "Leichte Infanterie Bataillon No 6 La Roche", YEL, "6o Batalhao Ligeiro La Roche, gola amarela"),
    ("BAVL7", "020", "Leichte Infanterie Bataillon No 7 Guenther", LBLUE, "7o Batalhao Ligeiro Guenther, gola azul-clara"),
]
for key, pl, cap, gola, txt in LIGHT_BAV:
    add(key, f"Baviera {txt.split(',')[0]}", f"Baviera 1811, {txt}: casaca verde, lapelas pretas, vivo vermelho, calca cinza",
        VKB.format(pl, cap), coat(DKG, gola, BLACK, BLACK, RED, DKG, BRASS, calca=GREY))

VKS = "aquarela Vinkhuijzen (NYPL), album 'Sachsen 1810', prancha {} ('{}'), legenda do colecionador 🔶"
# ---- Saxony after the 1810 reform (lot 2, 2026-10-27): white coat, collar / lapels / cuffs in the facing colour, white
# breeches, black gaiters (plates 036, 005). Turnbacks white piped in the facing colour 🔶. The pairs with the same colour
# (Koenig / Niesemeuschel, Prinz Max / von Rechten) differ by the buttons, not readable on the watercolours ❓: all brass.
MBLUE, DKG2, LGRN = [0.14, 0.24, 0.58], [0.05, 0.22, 0.12], [0.16, 0.46, 0.38]
SAX = [  # key, plate, caption, facing colour, text
    ("SAXKO", "036", "Linie Infanterie Regiment Koenig", RED, "Regimento Koenig, vermelho"),
    ("SAXNI", "010", "Linie Infanterie Regiment Niesemeuschel", RED, "Regimento von Niesemeuschel, vermelho"),
    ("SAXAN", "007", "Linie Infanterie Regiment Prinz Anton", LBLUE, "Regimento Prinz Anton, azul-claro"),
    ("SAXLO", "043", "Infanterie Regiment von Loew", MBLUE, "Regimento von Loew, azul"),
    ("SAXMA", "035", "Infanterie Regiment Prinz Max", YEL, "Regimento Prinz Maximilian, amarelo"),
    ("SAXRE", "008", "Linie Infanterie Regiment Rechten", YEL, "Regimento von Rechten, amarelo"),
    ("SAXFA", "044", "Infanterie Regiment Prinz Friedrich August", DKG2, "Regimento Prinz Friedrich August, verde-escuro"),
    ("SAXCL", "005", "Linie Infanterie Regiment Prinz Clemens", LGRN, "Regimento Prinz Clemens, verde-claro"),
]
for key, pl, cap, fc, txt in SAX:
    add(key, f"Saxonia {txt.split(',')[0]}", f"Saxonia 1810, {txt}: casaca branca", VKS.format(pl, cap),
        coat(WHI, fc, fc, fc, fc, WHI, BRASS, calca=WHI))
add("SAXLI", "Saxonia ligeira", "Saxonia 1810, Infantaria Ligeira: casaca verde, peças pretas, vivo vermelho, calca cinza",
    VKS.format("020", "Leichte Infanterie"), coat(DKG, BLACK, BLACK, BLACK, RED, DKG, BRASS, calca=GREY))
add("SAXJG", "Saxonia Jaeger", "Saxonia 1810, Jaeger: casaca verde, peças pretas, calca cinza",
    VKS.format("019", "Jaeger"), coat(DKG, BLACK, BLACK, BLACK, BLACK, DKG, BRASS, calca=GREY))

VKF = "aquarela Vinkhuijzen (NYPL), album 'Westphalen 1809', prancha {} ('{}'), legenda do colecionador 🔶"
# ---- Westphalia 1809 (lot 3, 2026-10-28): white coat of French cut, collar / lapels / cuffs in the facing colour, white
# breeches; index of scratchpad/fontes_reno/wes_thumbs (NYPL ids in the spec). Buttons yellow (061) for all ❓.
WES = [  # key, plates, caption, collar, lapels, cuffs, text
    ("WESAC", "006, 007", "Linie Grenadier / Linie Voltigeur", LBLUE, LBLUE, LBLUE, "Linha, peças azul-claras"),
    ("WESAE", "000, 046, 047", "Infanterie; Fusilier du 8e; Grenadier du 2e de ligne", DKB, DKB, DKB,
     "Linha, peças azul-escuras (2o e 8o de Linha)"),
    ("WES05", "004, 005", "5. Linie Regiment, Grenadier / Voltigeur-Musketier", ORANGE, ORANGE, ORANGE, "5o de Linha, laranja"),
    ("WES07", "061", "Voltigeur 7me R. d'Inf. de ligne", YEL, DKB, DKB, "7o de Linha, gola amarela, lapelas e canhoes escuros 🔶"),
]
for key, pl, cap, gola, lap, punho, txt in WES:
    add(key, f"Vestfalia {txt.split(',')[0]}", f"Vestfalia 1809, {txt}: casaca branca", VKF.format(pl, cap),
        coat(WHI, gola, lap, punho, gola, WHI, BRASS, calca=WHI))

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
json.dump(V, open(os.path.join(out, "variantes_reno.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK variantes_reno.json", len(V), "variantes")
