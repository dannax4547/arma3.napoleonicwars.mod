# Rússia 1812: granadeiros e capote (1º lote RU2)

2026-10-18 a 2026-10-25. Pedidos do usuário:
- *"Segue para os granadeiros e o capote russos (resto do 1º lote RU2), mantendo o padrão de fontes."*
- *"faz seguinte termina oque vc começou e cria um arquivo para tudo que tem que ser feito"*

**Situação:**
- **Gerado e verificado fora do jogo:** malha, revisão, texturas e renders.
- **Fases 7–8 do capote** (pesos, LODs, P3D, config): feitas em 2026-10-31, `docs/reports/capote_rus_p3d.md`.
- **Nada testado no ARMA 3. Nada commitado** (congelamento do GitHub, `CLAUDE.md`).

## 1. Fontes primeiro

O [V10B] (Viskovatov, vol. 10, tradução de Mark Conrad) foi **relido** nas seções dos regimentos de granadeiros e de mosqueteiros. Saíram dois dossiês novos:
- `docs/research/rus/HIST-RUS-INF-GRANADEIRO-1812-001.md` (decisões G1–G4);
- `docs/research/rus/HIST-RUS-INF-CAPOTE-1812-001.md` (decisões K1–K8, incertezas J1–J3).

A releitura **corrigiu a ficha** `docs/specs/rus_1812.md`:

| Item | A ficha dizia | A fonte diz | O que mudou |
|---|---|---|---|
| Platinas dos regimentos de granadeiros em 1812 | Regra geral por ordem na divisão | **Vermelhas em todos**, desde 3 fev 1811 | Ficha §3 corrigida. Usam as texturas R01 / C01 (o nome de exibição de R01 diz "also grenadier regiments") |
| Punhos do capote | Coloridos a partir de 1811 ([WG]) | **Redondos, cinza** (1802); nenhuma ordem de 1811 no [V10B] | Ficha §4 atualizada; punho cinza |
| Botões do capote | 7 de latão lisos | **7 de latão chatos**, fecho simples; um botão no alto de cada aba de trás | Ficha §4 atualizada |
| 5ª cor de platina (azul-celeste, R05) | Uma das 5 cores | A ordem de **12 abr 1812** dá só 4 cores; o azul de 1814 é dos 3º regimentos | **RU11 decidida** (2026-10-31): R05 e C05 **saíram** do addon |

## 2. Granadeiros

**Nenhuma malha nova** (dossiê G1–G3):
- **Companhias de granadeiros dos regimentos de mosqueteiros:** usam a casaca e o capote dos mosqueteiros. A diferença está no kiver (granada de 3 chamas, pluma, pompom vermelho), já feito até a Fase 8 (12 classes de kiver no `config.cpp`).
- **Regimentos de granadeiros:** platina vermelha (R01 / C01).
- **Granadas da cartucheira (1808):** ficam para o correame (G4).

## 3. Capote

`source/scripts/build_capote_rus.py` parte do capote francês (`build_capote_fr.py`, intacto), já validado: corpo, mangas, saia em duas metades, calça, polainas, sapatos, mãos do template e UVs. Mudanças, com as fontes do dossiê:

| # | Mudança | Fonte |
|---|---|---|
| K5 | Frente: os 2 × 7 botões franceses saem; entra **uma fileira de 7 botões chatos** no centro, de 22 mm sob a gola até a cintura (passo de 60 mm). O 7º fica sobre o alto da saia | [V10B] 1802 |
| K3 | **Punhos redondos:** saem as portinholas e os 6 botões delas | [V10B] 1802 |
| K2 | **Gola** baixada para 70 mm (mesmo método da casaca) e pintada de vermelho | [V10B] 1802, 1807 |
| K6 | **Costas:** um botão no alto de cada aba de trás | [V10B] 1802 |
| K8 | Polainas até o joelho, com a mesma correção da perna da casaca (C12) | [V10B] 1812 |

**Números:** 7.341 vértices, **13.900 triângulos**. O capote francês tem 14.224; os dois passam da meta proposta de 12.000.

**Revisão** (`uniform_review.py` com o corpo oficial do projeto):

| Verificação | Resultado |
|---|---|
| Duplicados, faces nulas, geometria solta | 0 |
| Arestas não-manifold | 0 |
| Autointerseções | 3 na gola e 2 + 2 na saia, **iguais às do capote francês** (herdadas) |
| "INVERTED" em `pala_*`, `aba_*` e `lapela_*` | São peças **vazias** que ficam só na lista de peças; não é defeito |

**Texturas:**
- **Pintor:** `generate_uniform_textures_rus.py`, agora tolerante a peças sem faces (punho sem portinhola).
- **Paleta:** `source/textures/hcl_capote_rus/variantes_rus_capote.json`. Capote cinza cru (tom **estimado**), gola vermelha, punhos cinza, platina pela divisão (C01–C04, as mesmas cores da casaca), calça branca, polainas pretas.
- **Mapas** em `source/textures/hcl_capote_rus/`:
  - `hcl_u_rus1812_capote_v01…v04_co.png`;
  - `_nohq.png`, `_smdi.png` e `_ao_bake.png`.

**Renders:** `render_texturas_rus.py peca=capote` gera `docs/renders/rus/textura_capote_rus_{fila_frente,fila_costas,tres_quartos,peito_frente,abas_costas,punho,polainas,ombro}.png`.

**Comandos:**

```
blender -b --factory-startup --python source/scripts/build_capote_rus.py -- source/models/coats/hcl_capote_fr/hcl_capote_fr_LOD0.blend source/models/coats/hcl_capote_rus/hcl_capote_rus_LOD0.blend
blender -b source/models/coats/hcl_capote_rus/hcl_capote_rus_LOD0.blend --python source/scripts/generate_uniform_textures_rus.py -- <caminho absoluto>/source/textures/hcl_capote_rus <caminho absoluto>/source/textures/hcl_capote_rus/variantes_rus_capote.json obj=HCL_U_RUS1812_Capote_LOD0 mapas=hcl_u_rus1812_capote maps ao_samples=64
blender -b --factory-startup --python source/scripts/render_texturas_rus.py -- . docs/renders/rus peca=capote
```

## 4. Limitações

- **Comprimento (K7):** barra a 0,46 m, herdada do capote francês e **estimada**. Corte das costas (fenda, meia-cinta) sem fonte (J1).
- **Tom do cinza:** estimado; o regulamento admite cinza escuro ou claro (J2).
- **Saia:** reflexos ondulados (dobras do relevo do pintor herdado). Conferir no jogo.
- **Peito:** os desenhos em estrela no alto do peito e das mangas são dobras pintadas herdadas (axilas), também presentes na casaca.

## 5. O que falta

Está tudo em **`docs/pendencias.md`**, o arquivo único de pendências.
