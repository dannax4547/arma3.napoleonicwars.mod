# King's German Legion and Hanover 1813-1815 variants (docs/specs/kgl_brunswick_1815.md sections 2-3; user decision of
# 2026-10-19: every unit). Writes, next to the British JSONs (source/textures/hcl_uniforme_uk):
#   variantes_kgl_linha.json   KL1      KGL line, battalion companies: the British jacket (lace in pairs, 🔶) with DARK
#                                       BLUE facings [K1][K2], white lace, grey trousers           -> painted (UK linha mesh)
#   variantes_kgl_flanco.json  KF1      the same with the flank-company wings                       -> painted (UK flank mesh)
#   variantes_kgl_ligeira.json KR1,KR2  1st / 2nd light battalions: green jacket, black facings [K3] = the 95th jacket
#                                       texture (hcl_u_uk1812_rifles_v01), nothing new painted
#   variantes_han_pintura.json HP1,HP2  Hanover, red jacket WITHOUT lace (Portuguese plain-front mesh), dark blue
#                                       facings / light yellow (Peine Landwehr), grey trousers [H1][H3] -> painted
#   variantes_han.json         H01..   Hanover field and Landwehr battalions named in the sources, each pointing at
#                                       one of the two painted textures (config only)
# The KGL jackets are the British variant L03 / FL03 (blue facings) with the blue made dark; nothing else changes.
#   python gen_variantes_kgl.py
import json, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))
TX = os.path.join(HERE, "..", "textures", "hcl_uniforme_uk")
AZUL_ESC = [0.07, 0.10, 0.22]            # dark blue (the Portuguese "azul ferrete" value; British "blue" was royal blue)
AMARELO_CLARO = [0.85, 0.78, 0.45]       # Peine Landwehr: light yellow facings [H1]
CINZA = [0.42, 0.43, 0.45]               # grey trousers (the British value)


def load(fn):
    return json.load(open(os.path.join(TX, fn), encoding="utf-8"))


def dump(fn, d):
    with open(os.path.join(TX, fn), "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"OK {fn}: {len(d)} variantes")


def darken_blue(v, prefix, name):
    v = copy.deepcopy(v)
    old_blue = v["cores"]["gola"]
    for k, c in v["cores"].items():
        if c == old_blue:
            v["cores"][k] = AZUL_ESC
    v["cores"]["calca"] = CINZA
    v["prefixo"], v["nome"], v["curto"] = prefix, name, "KGL"
    v["fonte"] = "docs/specs/kgl_brunswick_1815.md 2 [K1][K2]; galao em pares do britanico (🔶)"
    return v


uk_l, uk_f = load("variantes_uk_linha.json"), load("variantes_uk_flanco.json")
dump("variantes_kgl_linha.json", {"KL1": darken_blue(uk_l["L03"], "hcl_u_kgl1812_linha_v01",
                                                     "KGL, batalhao de linha: casaca vermelha, vistas azul-escuras")})
dump("variantes_kgl_flanco.json", {"KF1": darken_blue(uk_f["FL03"], "hcl_u_kgl1812_flanco_v01",
                                                      "KGL, companhia de flanco: vistas azul-escuras, wings")})
r = load("variantes_uk_rifles.json")["R01"]
dump("variantes_kgl_ligeira.json", {
    "KR1": dict(copy.deepcopy(r), nome="KGL, 1o batalhao ligeiro (jaqueta dos Rifles)", unidade="1st Light Battalion"),
    "KR2": dict(copy.deepcopy(r), nome="KGL, 2o batalhao ligeiro (jaqueta dos Rifles)", unidade="2nd Light Battalion")})
# Hanover: the Portuguese line jacket (no lace) recoloured
p = load("variantes_por_linha.json")["L01"]


def han(prefix, facing, name):
    v = copy.deepcopy(p)
    c = v["cores"]
    c.update(casaca=[0.55, 0.11, 0.07], gola=facing, punho=facing, pala=facing, viras=[0.86, 0.85, 0.80],
             gola_debrum=facing, punho_debrum=facing, debrum=[0.55, 0.11, 0.07], platina=facing, platina_borda=facing,
             calca=CINZA, botoes=[0.60, 0.58, 0.50])
    for k in ("regimento", "nome_regimento", "divisao"):
        v.pop(k, None)
    v.update(prefixo=prefix, nome=name, curto="Hanover", fonte="docs/specs/kgl_brunswick_1815.md 3 [H1][H3]")
    return v


dump("variantes_han_pintura.json", {"HP1": han("hcl_u_han1813_v01", AZUL_ESC, "Hanover: casaca vermelha lisa, vistas azul-escuras"),
                                     "HP2": han("hcl_u_han1813_v02", AMARELO_CLARO, "Hanover: vistas amarelo-claro (Landwehr Peine)")})
# battalions named by the sources (config only): (id, English name, kind, painted texture)
HAN = [("H01", "Field Battalion Lauenburg", "field", "hcl_u_han1813_v01"),
       ("H02", "Field Battalion Calenberg", "field", "hcl_u_han1813_v01"),
       ("H03", "Field Battalion York", "field", "hcl_u_han1813_v01"),
       ("H04", "Field Battalion Hoya", "field", "hcl_u_han1813_v01"),
       ("H05", "Landwehr Battalion Osnabrueck", "landwehr", "hcl_u_han1813_v01"),
       ("H06", "Landwehr Battalion Quakenbrueck", "landwehr", "hcl_u_han1813_v01"),
       ("H07", "Landwehr Battalion Lueneburg", "landwehr", "hcl_u_han1813_v01"),
       ("H08", "Landwehr Battalion Peine", "landwehr", "hcl_u_han1813_v02")]
dump("variantes_han.json", {i: {"prefixo": t, "unidade": n, "tipo": k, "nome": f"Hanover 1815, {n}",
                                "fonte": "docs/specs/kgl_brunswick_1815.md 3 [H1][H3]"} for i, n, k, t in HAN})
