# Brunswick 1815 variants of the black dolman (docs/specs/kgl_brunswick_1815.md section 4; user decisions of
# 2026-10-19: every unit, Brunswick first). Writes source/textures/hcl_uniforme_uk/variantes_bru_dolman.json:
#   B01 Leib-Bataillon (steel blue) | B02-B04 1st-3rd light battalions | B05-B07 1st-3rd line battalions |
#   B08 Avantgarde, the two light companies (black with green, green cuffs too)
# Rule of 1815 (B5, B6): black single-breasted dolman with black braid and black glass buttons, black cuffs, collar and
# shoulder straps in the battalion colour, black trousers with a piping ("Biese") in that colour. No mod art for the
# facings (only the Leib-Bataillon's blue collar in britainINFb c0 r0): colours are the calibrated values of the
# French / Prussian / Portuguese sets.
#   python gen_variantes_bru.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "textures", "hcl_uniforme_uk", "variantes_bru_dolman.json")
PRETO = [0.045, 0.045, 0.05]           # black broadcloth (lighter than the leather black, so the folds read)
TRANCA = [0.025, 0.025, 0.028]         # black worsted braid
BOTAO = [0.03, 0.03, 0.035]            # black glass buttons
COR = {
    "azul_aco": [0.28, 0.40, 0.55], "camurca": [0.78, 0.64, 0.44], "amarelo": [0.80, 0.62, 0.14],
    "laranja": [0.85, 0.40, 0.08], "vermelho": [0.62, 0.07, 0.07], "verde": [0.08, 0.30, 0.12],
    "branco": [0.86, 0.85, 0.80],
}
UNITS = [  # id, short name (English, for nomes_en_uk.py), colour, sources / notes
    ("B01", "Leib-Bataillon", "azul_aco", "B1 B5 B7; mod art britainINFb c0 r0"),
    ("B02", "1st Light Battalion", "camurca", "B2 B5 B6 (chamois at Waterloo; rose red from late June 1815)"),
    ("B03", "2nd Light Battalion", "amarelo", "B2 B6 (B5 gives green: sources differ)"),
    ("B04", "3rd Light Battalion", "laranja", "B2 B5 B6"),
    ("B05", "1st Line Battalion", "vermelho", "B5 B6"),
    ("B06", "2nd Line Battalion", "verde", "B5 B6"),
    ("B07", "3rd Line Battalion", "branco", "B5 B6"),
    ("B08", "Avantgarde, light company", "verde", "B5 (green also on the cuffs)"),
]


def variants():
    out = {}
    for i, (vid, nome, cor, fonte) in enumerate(UNITS, 1):
        c = COR[cor]
        punho = c if vid == "B08" else PRETO
        out[vid] = {
            "prefixo": f"hcl_u_bru1815_dolman_v{i:02d}",
            "unidade": nome, "nome": f"Brunswick 1815, {nome}: dolma preto, gola e platinas {cor}, vivo da calca {cor}",
            "fonte": f"docs/specs/kgl_brunswick_1815.md 4 [{fonte}]", "curto": nome,
            "cores": {"polaina": [0.045, 0.045, 0.045], "sapato": [0.03, 0.028, 0.025], "sola": [0.2, 0.13, 0.08],
                      "calca": PRETO, "calca_vivo": c, "botoes": BOTAO,
                      "casaca": PRETO, "gola": c, "punho": punho, "pala": punho, "viras": PRETO,
                      "debrum": PRETO, "platina": c, "platina_borda": c, "alamar": TRANCA},
        }
    return out


if __name__ == "__main__":
    d = variants()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"OK {os.path.basename(OUT)}: {len(d)} variantes")
