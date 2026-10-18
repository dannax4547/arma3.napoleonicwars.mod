# Portuguese variants (docs/specs/portugal_1812.md, user decisions D1-D3 of 2026-10-18): writes
#   source/textures/hcl_uniforme_uk/variantes_por_linha.json     24 line regiments (L01..L24)
#   source/textures/hcl_uniforme_uk/variantes_por_cacadores.json 12 Cacadores battalions, 1811-15 facings (C01..C12)
# Colours are the calibrated values already used by the French and Prussian painters (the painter darkens nothing;
# the mod-art calibration of the British set does not apply: there is no Portuguese art in the Reto atlases).
#   python gen_variantes_por.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "textures", "hcl_uniforme_uk")

AZUL = [0.07, 0.10, 0.22]          # "azul ferrete" (dark blue; Prussian dark blue 0.10/0.13/0.22 a touch darker)
COR = {
    "azul": AZUL,
    "branco": [0.86, 0.85, 0.80],
    "escarlate": [0.62, 0.07, 0.07],
    "amarelo": [0.80, 0.62, 0.14],
    "celeste": [0.40, 0.60, 0.80],
    "preto": [0.035, 0.035, 0.04],
}
CASTANHO = [0.21, 0.11, 0.08]      # Cacadores brown ("saragoca", surviving examples dark maroon-leaning)
CINZA_CLARO = [0.60, 0.61, 0.62]   # D3: light grey summer/campaign trousers
COMUM = {"polaina": [0.045, 0.045, 0.045], "sapato": [0.03, 0.028, 0.025], "sola": [0.2, 0.13, 0.08]}

# spec 1.2: number, name (as the sources spell it, for the English display names), collar, cuffs, division colour
LINHA = [
    (1, "Lippe", "azul", "branco", "branco"), (2, "Lagos", "azul", "branco", "escarlate"),
    (3, "1st Olivenza", "azul", "branco", "amarelo"), (4, "Freire", "azul", "escarlate", "branco"),
    (5, "1st Elvas", "azul", "escarlate", "escarlate"), (6, "1st Porto", "azul", "escarlate", "amarelo"),
    (7, "Setubal", "azul", "amarelo", "branco"), (8, "Evora", "azul", "amarelo", "escarlate"),
    (9, "Viana", "azul", "amarelo", "amarelo"), (10, "Lisbon", "azul", "celeste", "branco"),
    (11, "1st Almeida", "azul", "celeste", "escarlate"), (12, "Chaves", "azul", "celeste", "amarelo"),
    (13, "Peniche", "branco", "branco", "branco"), (14, "Tavira", "branco", "branco", "escarlate"),
    (15, "2nd Olivenza", "branco", "branco", "amarelo"), (16, "Vieira Telles", "escarlate", "escarlate", "branco"),
    (17, "2nd Elvas", "escarlate", "escarlate", "escarlate"), (18, "2nd Porto", "escarlate", "escarlate", "amarelo"),
    (19, "Cascaes", "amarelo", "amarelo", "branco"), (20, "Campo Maior", "amarelo", "amarelo", "escarlate"),
    (21, "Valenca", "amarelo", "amarelo", "amarelo"), (22, "Serpa", "celeste", "celeste", "branco"),
    (23, "2nd Almeida", "celeste", "celeste", "escarlate"), (24, "Braganca", "celeste", "celeste", "amarelo"),
]
DIVISAO = {"branco": "Centre", "escarlate": "South", "amarelo": "North"}
# spec section 2: battalion, province, collar, cuffs (1811-15)
CACADORES = [
    (1, "Estremadura", "preto", "celeste"), (2, "Algarve", "preto", "escarlate"), (3, "Beira", "preto", "preto"),
    (4, "Estremadura", "celeste", "celeste"), (5, "Alentejo", "escarlate", "escarlate"), (6, "Minho", "amarelo", "amarelo"),
    (7, "Estremadura", "preto", "amarelo"), (8, "Beira", "celeste", "preto"), (9, "Minho", "escarlate", "preto"),
    (10, "Porto", "amarelo", "preto"), (11, "Beira", "celeste", "escarlate"), (12, "Tras-os-Montes", "escarlate", "celeste"),
]


def linha():
    out = {}
    for n, nome, gola, punho, div in LINHA:
        d = COR[div]
        out[f"L{n:02d}"] = {
            "prefixo": f"hcl_u_por1812_linha_v{n:02d}",
            "regimento": n, "nome_regimento": nome, "divisao": DIVISAO[div],
            "nome": f"Linha portuguesa, {n} {nome}: jaqueta azul-escura, gola {gola}, punhos {punho}, viras e debrum {div}",
            "fonte": "docs/specs/portugal_1812.md 1.2 [P1][P3]",
            "curto": f"{n} {nome}",
            "cores": dict(COMUM, **{
                "calca": CINZA_CLARO, "botoes": [0.60, 0.58, 0.50],
                "casaca": AZUL, "gola": COR[gola], "punho": COR[punho], "pala": COR[punho],
                "gola_debrum": d, "punho_debrum": d, "viras": d,
                "debrum": AZUL, "platina": AZUL, "platina_borda": d}),
        }
    return out


def cacadores():
    out = {}
    pr = COR["preto"]
    for n, prov, gola, punho in CACADORES:
        out[f"C{n:02d}"] = {
            "prefixo": f"hcl_u_por1812_cacadores_v{n:02d}",
            "batalhao": n, "provincia": prov,
            "nome": f"Cacadores {n} ({prov}): jaqueta castanha, gola {gola}, punhos {punho}, debrum e alamares pretos",
            "fonte": "docs/specs/portugal_1812.md 2 [P8][P9]",
            "curto": f"Cacadores {n}",
            "cores": dict(COMUM, **{
                "calca": CASTANHO, "botoes": [0.05, 0.05, 0.05],
                "casaca": CASTANHO, "gola": COR[gola], "punho": COR[punho], "pala": COR[punho],
                "gola_debrum": pr, "punho_debrum": pr, "viras": CASTANHO, "viras_debrum": pr,
                "debrum": pr, "platina": CASTANHO, "platina_borda": pr, "alamar": pr}),
        }
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for nome, dados in (("variantes_por_linha.json", linha()), ("variantes_por_cacadores.json", cacadores())):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=1, ensure_ascii=False)
        print(f"OK {nome}: {len(dados)} variantes")
