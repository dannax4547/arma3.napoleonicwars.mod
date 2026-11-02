# Rússia 1812: capote, Fases 7 e 8 (pesos, LODs, P3D, `.rvmat` e config)

2026-10-31. Pedido do usuário: *"Yes, Phase 7"*, em resposta a *"Start greatcoat Phase 7 (weights, LODs, P3D, config)?"*.

**Situação:**
- **Gerado e verificado fora do jogo:** pesos, LODs, P3D, `.rvmat`, `config.cpp` e `model.cfg`.
- **Nada testado no ARMA 3** (faltam Tools e Samples). **Nada commitado** (congelamento do GitHub, `CLAUDE.md`).

Script: `source/scripts/build_p3d_capote_rus.py`. Segue o mesmo método da casaca (`build_p3d_uniforme_rus.py`, intacto). Log: `source/addon/hcl/hcl_rus/build_p3d_capote_rus_log.txt`.

```
blender -b --factory-startup --python source/scripts/build_p3d_capote_rus.py -- . source/addon/hcl/hcl_fr/hcl_u_fr1812.p3d docs/renders/rus
python source/scripts/gen_config_rus.py .
```

## 1. Pesos

Vêm dos pesos aprovados do capote francês (`source/models/pesos/hcl_fr_capote_pesos.blend`, os do `hcl_u_fr1812_capote.p3d`).

O `build_capote_rus.py` apaga botões e portinholas, por isso o número de vértices muda (7.568 → 7.341). A cópia é **por posição**, não por índice:

| Caso | Vértices | Regra |
|---|---|---|
| No lugar de um vértice francês (< 0,01 mm) | 6.646 | Pesos dele |
| Gola baixada | 148 (até 2,1 mm da gola francesa) | Ponto mais próximo da mesma peça francesa, misturado no triângulo |
| Pernas da calça rentes à polaina | 2 × 74 (até 7,4 mm) | Idem |
| Botões franceses que ficaram (platinas, polainas) | 22 botões | Pesos deles |
| Botões novos (7 da frente, 2 das costas) | 9 botões | Pesos do pano sob eles (corpo ou saia) |

- 62 grupos (ossos do template).
- No máximo 4 ossos por vértice, soma 1,000 em todos.
- Salvo em `source/models/pesos/hcl_rus_capote_pesos.blend`.

## 2. LODs

| LOD | Triângulos | Parcela |
|---|---|---|
| Res 1 | 13.900 | 100 % |
| Res 2 | 6.951 | 50 % |
| Res 3 | 3.476 | 25 % |
| Res 4 | 2.087 | **15 %** |
| View Pilot (1100) | 13.900 | o capote |

- **Redução peça por peça**, com razão comum (bisseção).
- **Botões:** saem no Res 3 e 4; a textura os mantém.
- **Mãos do template:** metade da razão no Res 3 e 4.
- **Res 4 (correção):** com 10 % e o piso de 80 triângulos por peça, as duas metades da saia (`saia_E` sobre `saia_D`) e o corpo se dobravam uma através da outra, com triângulos escuros no peito e na saia.
  - Correção: essas 3 peças têm o dobro da razão e piso de 300 triângulos.
  - Custo: o Res 4 fica em 15 % em vez de 10 % (a casaca tem 13 %).
- Prévia: `docs/renders/rus/lods_capote_rus.png`, Res 1 a 4 da esquerda para a direita.

## 3. P3D

`source/addon/hcl/hcl_rus/hcl_u_rus1812_capote.p3d` tem 12 LODs: Res 1–4, View Pilot, as duas sombras do corpo (10000, 10010), Geometry, Memory, LandContact, Hit-points e Fire Geometry.

**Do modelo-base** (`hcl_u_fr1812.p3d`, montado a partir do template oficial), sem mudança:
- os 11 proxies;
- a textura e o material das mãos;
- todos os LODs de 10000 para cima.

**Seleções:**
- `Camo` em toda a roupa;
- `hl` e `injury_hands` nas mãos do template;
- 67 seleções de ossos.

**Verificações:**
- As seleções do Res 1 e do View Pilot são **as mesmas** do capote francês.
- Ler e regravar o P3D dá o arquivo **byte a byte idêntico**.

**`.rvmat`:** um por material físico em `data/`:
- `hcl_u_rus1812_capote_la.rvmat` (todo o pano, polainas também);
- `hcl_u_rus1812_capote_couro.rvmat` (sapatos e solas);
- `hcl_u_rus1812_capote_latao.rvmat` (botões).

Todos leem o `_nohq` e o `_smdi` do capote.

## 4. Config (Fase 8)

O `gen_config_rus.py` agora gera também:
- **`HCL_RUS1812_Capote_Soldado_C01…C04`**: soldados (scope 1), modelo `hcl_u_rus1812_capote.p3d`, textura `hcl_u_rus1812_capote_v0N_co.paa`;
- **`HCL_U_RUS1812_Capote_C01…C04`**: itens de uniforme (Arsenal, scope 2);
- **`class hcl_u_rus1812_capote: ArmaMan {};`** no `model.cfg`.

Os nomes seguem a casaca, por exemplo "Russian Musketeer Greatcoat 1812 - 1st regiment of a division (red shoulder straps, also grenadier regiments)". São 4 cores de platina (decisão RU11).

O addon agora tem:
- 20 itens: 4 casacas, 4 capotes e 12 kivers;
- 8 soldados.

Todos os P3D e PAA referenciados têm arquivo de origem.

## 5. Limitações

- **Orçamento:** 13.900 triângulos no Res 1, contra a meta de 12.000 (o capote francês tem 14.224).
- **Res 4:** 15 % (ver §2).
- **Pesos da saia:** são os do capote francês, sem teste de movimento com as animações oficiais (precisa do Samples, `docs/pendencias.md` §3.5).
- **Sombra:** é o volume do corpo do template, o mesmo dos outros capotes do projeto; a saia passa alguns centímetros dele.
