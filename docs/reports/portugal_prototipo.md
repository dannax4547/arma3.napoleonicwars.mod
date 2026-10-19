# Portugal 1810–1815: linha e Caçadores no addon `hcl_uk`

2026-10-18/19. Esta é a etapa 2 do pedido *"inicia tudo da forma mais profissional o reino unido e seus fantoches"*, depois de o usuário relatar que testou o `hcl_uk` britânico no jogo e que *"ficou bom"*.

A ficha técnica é `docs/specs/portugal_1812.md`. Decisões do usuário:
- barretina **stovepipe** de 1810–15;
- **todos** os 24 regimentos de linha e os 12 batalhões de Caçadores;
- calça **cinza-claro** e correame **branco** na linha.

**Nada foi visto no jogo.** Tudo foi verificado fora do Arma 3.

## 1. O que entrou

| Peça | Classes | Malha | Origem |
|---|---|---|---|
| Jaqueta de linha (azul-escura, sem galões, 10 botões) | `HCL_U_POR1812_L01` … `L24` | `hcl_u_por1812_linha.p3d` | `build_uniforme_uk.py frente=simples` |
| Jaqueta de Caçadores (castanha, 8 fileiras de alamares pretos) | `HCL_U_POR1812_C01` … `C12` | `hcl_u_por1812_cacadores.p3d` | `build_uniforme_uk.py frente=alamares` |
| Stovepipe de linha | `HCL_H_POR1812_Stovepipe_Batalhao_NN` / `_Granadeiro_NN` / `_Ligeira_NN` (NN = 01–24) | `hcl_h_uk_por_{batalhao,granadeiro,ligeira}.p3d` | `blockout_shako_uk.py conjunto=por` |
| Stovepipe de Caçadores | `HCL_H_POR1812_Stovepipe_Cacadores_NN` (01–12) | `hcl_h_uk_por_cacadores.p3d` | idem |
| Soldados | `HCL_POR1812_Soldado_L01` … `L24`, `_C01` … `C12` | | `gen_config_uk.py` |
| Equipamento | Linha: `HCL_V_UK1812_Correame` (branco). Caçadores: `HCL_V_UK1812_Correame_Preto`. Mochila britânica | | já existiam |

**Cores e nomes.** As cores saem das tabelas das fontes [P1][P3][P8] (`gen_variantes_por.py`):
- linha: gola e punhos na cor do regimento; viras e debrum na cor da divisão (Norte amarelo, Centro branco, Sul escarlate);
- Caçadores: gola e punhos na cor do batalhão (1811–15).

Todos os regimentos e batalhões têm nome, porque as fontes nomeiam todos. Exemplo: *"17th Line Infantry Regiment (2nd Elvas)"*.

**Barretinas.**
- Placa oval de latão com o escudo coroado e as cinco quinas em relevo. É um desenho simples, sem heráldica fina 🔶, porque o mod não tem arte dela e as fontes não dão medida.
- Faixa de latão embaixo com o **número do regimento**.
- Cocar azul e vermelho e pluma na frente: branca no batalhão e nos granadeiros, verde na ligeira e nos Caçadores. A pluma tem a forma de tufo 🔶.
- Granada (granadeiros) e cornetinha (ligeira) entre a faixa e a placa 🔶.
- Caçadores: corneta traçada, faixa numerada embaixo e cordões verdes.

**Número por regimento.** A faixa tem a seleção escondida própria `numero`, com uma textura de 1024 × 128 por unidade (`gen_numeros_por.py`, 36 texturas). Assim bastam **4 malhas**, e não 84. O `build_p3d_uk.py` refaz o UV dessa faixa para o número não ficar esticado.

## 2. Verificações (fora do jogo)

| Verificação | Resultado |
|---|---|
| Jaquetas | Linha: 11.864 triângulos, 10 botões. Caçadores: 12.200 triângulos, 24 botões (8 × 3), 8 fileiras de alamares |
| Pesos | 6.402 e 6.640 vértices, 62 ossos, no máximo 4 por vértice, soma 1 em todos |
| Barretinas | 10,3–13,0 mil triângulos; faixa do número com 56 faces na seleção `numero` (Res 2: 26–49) |
| PAA | 141 conversões, 0 falhas (tudo do `hcl_uk`) |
| Binarize | Código 0; **21/21 modelos com `OFP2_ManSkeleton`**; avisos só dos 3 materiais do jogo, como antes |
| CfgConvert | `config.bin` e 22 rvmat com código 0; 142 itens, 47 soldados, 21 `CfgModels` |
| `pbo_verify.py` | `hcl_uk.pbo` 162,5 MB; prefixo `hcl\hcl_uk`; 185 arquivos; sem fontes; **184 referências, nenhuma faltando** |
| Renders | `docs/reports/img/soldado_uk/soldado_por_linha_*` (1º Lippe, 17º com granadeiro, 21º com ligeira) e `soldado_por_cacadores_*` (1º, 6º, 11º): o número aparece certo na faixa ("17") |

## 3. Pendências 🔶

- O número e a medida dos botões da linha não estão nas fontes lidas (fiquei com 10). A largura dos alamares (8 mm) também não.
- **Punhos dos Caçadores:** em ponta só no 6º [P9]; aqui todos ficaram redondos.
- **Correias da mochila nos Caçadores:** saem brancas, porque há uma mochila só. A mochila castanha com manta cinza [P9] não foi feita.
- **Forro claro da barretina:** aparece entre a pala e o corpo em alguns ângulos de câmera, como já acontece nas barretinas britânicas.
- **Livros de referência:** Chartrand (Osprey MAA 343/346/358) não foi consultado direto; tudo veio por resumos.
- **Próxima etapa:** KGL / Hanôver.
