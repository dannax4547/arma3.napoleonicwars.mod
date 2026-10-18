# Reino Unido 1812–1815: protótipo da infantaria britânica e addon de teste `hcl_uk`

2026-10-13. Pedido do usuário: *"inicia tudo da forma mais profissional o reino unido e seus fantoches"*.

Ficha técnica: `docs/specs/uk_1812.md`. Respostas do usuário na abertura:
- contingentes: Reino Unido, Portugal, KGL + Hanôver, Brunswick;
- ordem: Brit → Portugal → KGL/Hanôver → Brunswick;
- barretinas: Belgic + stovepipe;
- 1º lote: Rifles, Highlanders e companhias de elite.

> As decisões K1–K6 da ficha (§9) **ainda não foram aprovadas**. Usei as respostas recomendadas na própria ficha. Se alguma resposta for outra, muda um parâmetro de script, não o trabalho todo.

**Nada foi visto no jogo.** Tudo foi verificado fora do Arma 3.

## 1. O que entrou

| Peça | Classes | Malha | Origem |
|---|---|---|---|
| Casaca de linha, companhia de batalhão | `HCL_U_UK1812_L01` … `L04` (vistas amarela, verde, azul, branca) | `hcl_u_uk1812_linha.p3d` | `build_uniforme_uk.py frente=linha` |
| Casaca de linha, companhia de flanco (wings) | `HCL_U_UK1812_FL01` … `FL04` | `hcl_u_uk1812_flanco.p3d` | `build_casaca_elite_fr.py` rodado **sem alteração** sobre a casaca britânica (`franja=0.045 cordoes=30`) |
| 95th Rifles | `HCL_U_UK1812_R01` | `hcl_u_uk1812_rifles.p3d` | `build_uniforme_uk.py frente=rifles` |
| Highlanders (casaca + kilt) | `HCL_U_UK1812_K01` (92nd Gordon), `K02` (tartan Government, regimento não identificado) | `hcl_u_uk1812_kilt.p3d` | `build_kilt_uk.py` |
| Barretina Belgic 1812 | `HCL_H_UK1812_Belgic_Batalhao` / `_Granadeiro` / `_Ligeira` | `hcl_h_uk_belgic_*.p3d` | `blockout_shako_uk.py` + `texturizar_shako_uk.py` |
| Barretina stovepipe | `HCL_H_UK1812_Stovepipe_Batalhao` / `_Granadeiro` / `_Ligeira` / `_28th` / `_Rifles` | `hcl_h_uk_stovepipe_*.p3d` | idem (stovepipe reassada com `realce_arte_uk.py`) |
| Bonnet de penas highland | `HCL_H_UK1812_Bonnet_Highland` | `hcl_h_uk_bonnet_highland.p3d` | `bonnet_highland_uk.py` |
| Correame | `HCL_V_UK1812_Correame` (branqueado), `HCL_V_UK1812_Correame_Preto` (Rifles) | `hcl_v_uk1812_correame.p3d` | malha francesa (K4) + `generate_equipment_textures_uk.py` |
| Mochila Trotter | `HCL_B_UK1812_Mochila` | `hcl_b_uk1812_mochila.p3d` | malha francesa (K4), lona laqueada preta |

Nomes de regimento só onde há fonte (`nomes_en_uk.py`):
- **28th (North Gloucestershire)**: vista amarela; a stovepipe tem o "28" atrás;
- **92nd (Gordon Highlanders)**;
- **95th (Rifles)**.

Todos com 🔶 (fonte secundária). O resto fica *"(regiment unidentified)"*.

## 2. Casacas

- **Corte.** Malha prussiana de produção com a gola v2 e as abas curtas da francesa, a mesma técnica de `build_uniforme_fr.py`:
  - barra a 0,907 m;
  - os 14 botões prussianos foram tirados.
- **Linha.** 10 botões no centro, em 5 pares (atlas `britainINF` c0–c3 r0).
- **Presilhas de galão.** São pintadas a partir da lista de botões, gravada no objeto (`hcl_botoes_frente`):
  - ½" (12,7 mm), 78 mm, de ponta quadrada;
  - nos dois lados de cada botão;
  - relevo de 0,5 mm com nervuras e a fresta da dobra.
- **Rifles.** 3 fileiras de 10 botões, com as laterais abrindo de 55 mm na cintura para 95 mm no alto (`britainINF` c3 r2).
- **Wings.** São feitas com a meia-lua e a franja do script das dragonas francesas: um corpo na cor da vista, barras de galão a cada 12 mm e franja branca de 4,5 cm.
  - **🔶 Aproximação:** a wing real é uma peça de pano chata, e não uma meia-lua acolchoada.
- **Kilt.**
  - pregas de 26 mm atrás e nos lados, avental liso na frente;
  - fica sob as abas da casaca e sob o correame;
  - **tartan amostrado do atlas** autorizado: Gordon em `britainINFb` c7 r2, Government em `britainINF` c3 r3, na escala de 0,70 m por faixa de arte;
  - joelho nu, meia virada com a liga vermelha, meias xadrez vermelho e branco e polaina preta curta embaixo.
- **Cores** (`source/textures/hcl_uniforme_uk/variantes_uk_*.json`): medidas no atlas e calibradas, porque o mod escurece a arte. Casaca vermelha "brick red" da tropa, viradas brancas, botões de estanho, calça cinza (K3).

## 3. Barretinas

| | Belgic 1812 | Stovepipe |
|---|---|---|
| Medidas (fator de encaixe 1,032) | corpo 170 mm, frente falsa 217 mm (fonte: 6½" e 8¼") | 184 mm, afunilando 4 mm no raio (padrão de 1806) |
| Placa | escudo barroco coroado com GR, **traçado da arte** (`britainINF` c2 r5), 91 × 140 mm | GR, jarreteira, leão e troféu, **traçada da arte** (`britainINF` c3 r4, metade espelhada), 89 × 152 mm |
| Cocar e tufo | à esquerda, tufo de 130 mm | na frente, em cima, tufo de 152 mm (6") |
| Cordões | brancos (verdes na ligeira), da base do tufo sob a placa até as borlas à direita | só nos Rifles (verde-escuros) |

- Tufos: batalhão branco com o terço de baixo vermelho; granadeiros branco; ligeira e Rifles verde-escuro.
- 28th: número "28" de latão, com 26 mm de altura, embaixo atrás.
- Rifles: corneta traçada no lugar da placa.
- **Ajuste feito:** a placa da stovepipe saía lisa, porque a arte do mod é escura e de pouco contraste. Fiz uma cópia do atlas com os níveis esticados só nessa caixa (`britainINF_realce.png`, 3,5×) e reassei as 5 stovepipe.
- **Bonnet de penas:**
  - faixa xadrez de 3 fileiras, com as cores da própria arte (`britainINFb` c7 r4);
  - 908 penas de avestruz pretas em domo, todas acima da faixa;
  - 7 caudas do lado direito, até a orelha;
  - cocar preto e hackle à esquerda;
  - **v1 descartada:** as penas caíam sobre o rosto.

## 4. Verificações (fora do jogo)

Cadeia rodada em 13/10 e 18/10, sempre com o Arma 3 e o BattlEye fechados. Log em `work/cadeia_uk_etapa2.log` e `work/cadeia_uk_kilt2.log`.

| Verificação | Resultado |
|---|---|
| Pesos (`teste_movimentos.py`, transferidos do corpo oficial) | Linha 6.402, flanco 8.546, Rifles 6.742 e kilt 9.154 vértices; 62 ossos; no máximo 4 ossos por vértice; soma 1 em todos |
| Kilt (`build_kilt_uk.py`) | 0 de 604 pontos da calça fora do kilt; **1 de 676** pontos das abas com kilt por fora (antes: 90); 4 pontos do correame/mochila; 17.152 triângulos |
| PAA (`convert_uk_paa.ps1`) | 53 conversões, 0 falhas |
| P3D MLOD | 4 casacas com 9 LODs; 9 barretinas/bonnet com 5 LODs; correame e mochila com 2 LODs |
| Binarize | Código 0; **15/15 modelos com `OFP2_ManSkeleton`**. Avisos só dos 3 materiais do jogo que o binarize não acha fora do P: (`hl_white_bald_muscular`, `meat`, `meatbones`), como na Prússia e na França |
| CfgConvert | `config.bin` e 15 rvmat com código 0; 22 itens, 11 soldados, 1 mochila, 15 `CfgModels` |
| `pbo_verify.py` | `hcl_uk.pbo` 93,7 MB; prefixo `hcl\hcl_uk`; 84 arquivos; nenhum fonte dentro; **83 referências, nenhuma faltando** |
| Renders | `docs/reports/img/soldado_uk/`: linha (Belgic), especiais (28th, Rifles, 92nd) e os dois kilts, com a cabeça do jogo |

**Defeitos achados nos renders e corrigidos (18/10):**
- **Tartan das costas do kilt borrado** ("veio de madeira"). A amostragem usava o raio de cada ponto, e a ondulação das pregas (3,5 mm) deslocava o padrão em até ~11 mm nas costas. Agora o arco usa um raio suavizado por altura; também há filtro e amostragem bilinear (o texel mede ~1 px do recorte).
- **Kilt aparecendo através das abas.** As abas ficam a menos de 3 mm do assento, sem espaço para o kilt passar por baixo. No modelo do kilt elas agora são levadas para fora, por cima do kilt, como na peça real (até 47 mm na parte de baixo de trás). Os pontos da costura com o corpo ficam parados.

**Não visto no jogo.** G1–G12 não executados.

## 5. Pendências e pontos 🔶

- **K1–K6 sem aprovação.** O galão em forma de lança (`britainINF` c0–c3 r1) já existe no pintor (`galao_forma=lanca`) e não foi usado.
- As wings são aproximadas pela dragona francesa.
- O correame e a mochila britânicos usam a malha francesa (K4). Falta a chapa de cinto oval no cruzamento; a mochila Trotter real é uma caixa mais estreita (~381 × 432 × 102 mm).
- O kilt fica com a calça por baixo (as pernas são a malha da calça, pintada como pele e meias).
- No kilt, as abas da casaca sobem até 47 mm para passar por cima das pregas. Falta conferir no jogo, sentado e ajoelhado.
- O tartan do K02 (Government, `britainINF` c3 r3) traz manchas de sujeira da própria arte do mod 🎮.
- Rifles: as correias da mochila saem brancas, porque há uma mochila só. Correias pretas pedem uma 2ª textura de mochila. A pala do ombro (verde sobre verde) quase não aparece; só o debrum branco.
- Hackle do bonnet: sem fonte para a cor; usei a convenção do tufo de batalhão.
- Tambores, músicos e oficiais (K6): depois.
- Próximas etapas, na ordem pedida: Portugal → KGL/Hanôver → Brunswick.
