# Casaca russa de 1812: malha de jogo, revisão e texturas (Fases 4 a 6)

2026-10-18. Pedido do usuário: *"Segue para as Fases 4 a 6 da casaca russa (malha de jogo, bake e texturas), mantendo o padrão de fontes."*

**Base histórica:**
- Dossiê `docs/research/rus/HIST-RUS-INF-COAT-1812-001.md`: decisões C1–C10 e, novas nesta fase, **C11–C13**.
- Ficha `docs/specs/rus_1812.md` §2.1–2.2.

**Situação:**
- **Gerado e verificado fora do jogo,** com as revisões automáticas e os renders.
- **Sem teste no ARMA 3.**
- **Faltam o atlas do mod e o Arma 3 Samples nesta máquina:**
  - tons não conferidos;
  - folga do pescoço não medida na cabeça do jogo.
- Pesos, LODs e P3D são da Fase 7.

## 1. Fase 4: malha de jogo

A casaca já nasceu da **malha de produção prussiana** (mesma topologia, mesmas UVs; `build_uniforme_rus.py`). A Fase 4 não refez a malha: corrigiu o que o blockout herdou e não batia com as fontes. Continua com **11.960 triângulos** (orçamento de 12.000), 6.470 vértices e 21 peças.

| Correção | Problema | O que foi feito | Fonte |
|---|---|---|---|
| **Borda da frente (C11)** | O degrau do fecho prussiano (a frente que se sobrepõe, 1,8 mm acima) ficava **entre** as duas fileiras de botões e lia como fecho simples | O degrau foi para **22 mm (⅞") fora** da fileira do lado direito de quem veste (x −26 → −40 mm). Os vértices do peito deslizam em volta do eixo com um mapa de ângulo monotônico: sem topologia nova, UVs mantidas. O raio segue o corpo oficial (`ref_corpo_arma3_samples.blend`), para o pano ficar na mesma superfície. Os botões são postos depois, já na superfície nova | R1: lapela de 3" com as casas a ⅞" da borda |
| **Polainas até o joelho (C12)** | A calça prussiana **franzia 7,5 mm** sobre o alto da polaina curta (h 0,415–0,50), o que formava um degrau no meio da canela | O franzido foi desfeito (180 vértices), e a perna logo acima da polaina modelada ficou **rente** a ela, afinando de volta até h 0,53 (72 vértices, até 14,6 mm) | R1: polainas pretas até o joelho, 1 jan 1812 |

## 2. Fase 5: revisão

`uniform_review.py` antes exigia o Samples. Agora aceita o **corpo oficial já importado no projeto** (`ref_corpo_arma3_samples.blend`, sem os pontos de proxy). A casaca prussiana aprovada serve de base de comparação.

| Verificação | Prussiana aprovada | Russa | Leitura |
|---|---|---|---|
| U2 / M2 / M4: duplicados, faces nulas, geometria solta | 0 | **0** | — |
| M3: arestas não-manifold | 0 | **0** | — |
| U3: autointerseções | 3 (gola) | 3 (gola) | **Herdadas**, iguais às da base aprovada (rolo do alto da gola) |
| U4: casaco × abas, cruzamentos "visíveis" | 8 + 8 | 24 + 24 | Abas mais longas (C5), na emenda da cintura atrás. Conferido no render: a emenda está limpa |
| U4: calça × polaina | 30 + 30 | 77 + 75 (4–5 visíveis) | A perna agora encosta na polaina por fora (C12); quase todos escondidos |
| U6: triângulos | 11.960 | **11.960** | Dentro do orçamento |

A visibilidade do U4 é estimada por raios e conta como "visível" a linha onde uma peça encosta na outra (botões no pano, emendas). O critério real é o render.

## 3. Fase 6: UV, bake e texturas

- **UV:** as da malha base prussiana (atlas 2048, botões num quadrado de latão no canto), mantidas pelas correções.
- **Bake:** AO da própria casaca no Cycles (64 amostras, sem as mãos), o mesmo método das outras casacas do projeto.
- **Pintor:** `generate_uniform_textures_rus.py`, cópia russa do pintor britânico (o original fica intacto). Pinta a partir da posição 3D de cada texel: bainhas, costuras de alfaiate, dobras, desgaste, poeira e lama. Acréscimos russos:
  - **polainas até o joelho (C12):** a perna da calça abaixo de h 0,52 vira polaina, com bainha virada costurada no alto. A tira de botões da polaina continua para cima, com **6 botões pintados** (domo no relevo, latão na cor, metal no `_smdi`) no passo dos 20 modelados;
  - **borda da frente:** acompanha a posição nova (`hcl_fecho_theta`), só como bainha enrolada no relevo;
  - **sem debrum (C13);**
  - **calça branca:** mosqueado menor, porque o valor das calças cinza sujava o branco.

**Variantes** (`source/textures/hcl_uniforme_rus/variantes_rus_linha.json`): a platina segue a **ordem do regimento na divisão**, pela ordem de 9 jan 1810 (ficha §2.1):

| Variante | Platina |
|---|---|
| R01 (`_v01`) | vermelha |
| R02 (`_v02`) | branca |
| R03 (`_v03`) | amarela |
| R04 (`_v04`) | verde-escura debruada de vermelho |

Nas 5, o resto é igual: casaca verde-escura, gola, punhos e viradas vermelhos, portinhola verde-escura, botões de latão, calça branca e polainas pretas.

**Mapas** (2048 PNG, fontes para o ImageToPAA) em `source/textures/hcl_uniforme_rus/`:
- `hcl_u_rus1812_linha_v01…v04_co.png`;
- compartilhados: `hcl_u_rus1812_linha_nohq.png`, `_smdi.png` e `_ao_bake.png`.

**Renders** (`render_texturas_rus.py`, com o kiver texturizado das Fases 4–7 na cabeça aproximada): `docs/renders/rus/textura_soldado_rus_{fila_frente,fila_costas,tres_quartos,peito_frente,abas_costas,punho,polainas,ombro}.png`. Os renders de blockout (`blockout_soldado_rus_*`) foram refeitos com a malha nova.

Comandos:

```
blender -b --factory-startup --python source/scripts/build_uniforme_rus.py -- source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend source/models/coats/hcl_uniforme_rus/hcl_uniforme_rus_linha_LOD0.blend
blender -b source/models/coats/hcl_uniforme_rus/hcl_uniforme_rus_linha_LOD0.blend --python source/scripts/generate_uniform_textures_rus.py -- <caminho absoluto>/source/textures/hcl_uniforme_rus <caminho absoluto>/source/textures/hcl_uniforme_rus/variantes_rus_linha.json obj=HCL_U_RUS1812_Linha_LOD0 mapas=hcl_u_rus1812_linha maps ao_samples=64
blender -b --factory-startup --python source/scripts/render_texturas_rus.py -- . docs/renders/rus
```

O pintor precisa de **caminhos absolutos**: com caminho relativo, o Blender não gravou os PNG.

## 4. Limitações

- **Tons estimados:**
  - verde-escuro (0,08 / 0,17 / 0,11), vermelho, branco da calça e cores das platinas;
  - tudo a conferir no atlas `rus1812INF` (⏳).
- **Platina sem o número da divisão bordado:** a ficha marca o número como provável (🔶), e cada regimento tem o seu. Fica para quando houver lista de regimentos.
- **Polaina:**
  - restam um friso de 2–3 mm onde termina a polaina modelada (a bainha dela, h 0,423);
  - e um entalhe pequeno no lado de fora, onde a tira de botões sobressai mais que o limite de 15 mm.
- **Borda da frente:** curva levemente nos últimos 14 mm sob a gola, onde a mudança se desfaz para não mexer no pé da gola.
- **Gola:** 3 autointerseções no rolo do alto, herdadas da base. A folga do pescoço só pode ser medida com a cabeça do jogo (Samples).

## 5. Pendências

- **Fase 7:**
  - pesos (o `teste_movimentos.py` do projeto);
  - LODs, sombra e P3D (`hiddenSelectionsTextures` com as 4 variantes; R05 saiu pela RU11);
  - `.rvmat`;
  - conversão PNG → PAA (Arma 3 Tools).
- **Com o Samples:** medir a folga do pescoço (`diag_gola_bust.py`) e rodar o `uniform_review.py` com a cabeça do jogo.
- **Com o atlas:** conferir os tons e o debrum (C13).
