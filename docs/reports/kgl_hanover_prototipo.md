# KGL e Hanôver 1812–1815 no addon `hcl_uk`

2026-10-19. É a última etapa do pedido do Reino Unido e seus aliados. O usuário escolheu todas as unidades. A ficha técnica é `docs/specs/kgl_brunswick_1815.md`, §2–3.

**Nada foi visto no jogo.** Tudo foi verificado fora do Arma 3.

## 1. O que entrou

| Peça | Classes | Malha | Textura |
|---|---|---|---|
| KGL, linha, companhia de batalhão | `HCL_U_KGL1812_KL1` | casaca britânica de linha | vistas **azul-escuras** [K1][K2], galão branco em pares (🔶), calça cinza |
| KGL, linha, companhia de flanco (wings) | `HCL_U_KGL1812_KF1` | casaca britânica de flanco | idem, wings azul-escuras |
| KGL, 1º e 2º batalhões ligeiros | `HCL_U_KGL1812_KR1`, `KR2` | jaqueta dos Rifles | a mesma do 95th: verde com vistas pretas [K3] |
| Hanôver, 4 batalhões de campo e 4 de Landwehr | `HCL_U_HAN1815_H01` … `H08` (Lauenburg, Calenberg, York, Hoya; Osnabrück, Quakenbrück, Lüneburg, Peine) | jaqueta lisa portuguesa | vermelha, vistas azul-escuras; **Peine amarelo-claro** [H1][H3] |
| Belgic da KGL com o **número do batalhão** na placa | `HCL_H_KGL1812_Belgic_{Batalhao,Granadeiro,Ligeira}_1` … `_8` | `hcl_h_uk_kgl_belgic_*.p3d` | placa britânica traçada e faixa numerada (`numero`, exemplar de Celle [K6], 🔶) |
| Barretina dos ligeiros da KGL | `HCL_H_KGL1812_Stovepipe_Ligeira` | a dos Rifles (corneta, cordões verdes) | 🔶 |
| Barretina de Hanôver | `HCL_H_HAN1815_Stovepipe` | `hcl_h_uk_han_stovepipe.p3d` | placa **oval** de latão com borda recortada, **coroa** e **"GR"** [K5][K6]; cocar preto e tufo branco (🔶) |

Todas as barretinas têm a jugular de couro.

## 2. Verificações (fora do jogo)

| Verificação | Resultado |
|---|---|
| Barretinas | Belgic da KGL com 21,6–22,8 mil triângulos e a faixa do número com 56 faces na seleção `numero` (Res 2: 30); Hanôver com 17,5 mil |
| PAA | 183 conversões, 0 falhas |
| Config | 194 itens, 67 soldados, 2 mochilas, 30 `CfgModels` (o `model.cfg` deixou de repetir as malhas reaproveitadas) |
| Build | Binarize e CfgConvert com código 0; nenhum modelo sem esqueleto |
| `pbo_verify.py` | `hcl_uk.pbo` 223,0 MB; 245 arquivos; sem fontes; **244 referências, nenhuma faltando** |
| Renders | `soldado_kgl_*` (flanco com o 2º, batalhão com o "5", ligeiro) e `soldado_han_*` |

**Observação:** outra sessão corrigiu a emenda da calça (`unir_calca.py`, 14:08–14:52) nas malhas britânicas de linha e flanco e repintou as texturas britânicas. A casaca de linha passou de 11.875 para 11.755 faces. O build das 15:21 já usa essas malhas, e a KGL foi pintada sobre elas.

## 3. Pendências 🔶

- **Galão da KGL:** o regimental não foi achado; ficou o britânico em pares.
- **Ligeiros da KGL:** usam a barretina dos Rifles. A fonte (fórum) diz pluma em pé no 1º e cordões com pompom no 2º.
- **Hanôver:**
  - cocar, tufo e calças sem fonte lida;
  - Lüneburg e Verden têm a cor discutida (verde ou vermelho);
  - a Landwehr real tinha equipamento misturado.
- **Brunswick:** ainda faltam o chapéu corso da Avantgarde e a Landwehr.
