# Brunswick 1815: o "Corpo Negro" no addon `hcl_uk`

2026-10-19. O usuário pediu *"agora inicia brunswick e a KGL"*. Escolheu **todas as unidades** e **Brunswick primeiro**.

A ficha técnica é `docs/specs/kgl_brunswick_1815.md` §4. A fonte principal é a associação de recriação histórica Herzoglich Braunschweigisches Feldcorps [B5]. A prancha *Brigade-Uniformtafel* Nr. 176 (2º batalhão de linha, 1814–15), enviada pelo usuário [B8], serviu de referência visual.

**Nada foi visto no jogo.** Tudo foi verificado fora do Arma 3.

## 1. O que entrou

| Peça | Classes | Malha | Origem |
|---|---|---|---|
| Dólmã preto, 10 fileiras de alamares, saia curta | `HCL_U_BRU1815_B01` … `B08` | `hcl_u_bru1815_dolman.p3d` | `build_uniforme_uk.py frente=alamares fileiras=10 hem=1.10` |
| Kiwer do Leib-Bataillon (crina preta, caveira e ossos) | `HCL_H_BRU1815_Kiwer_Leib` | `hcl_h_uk_bru_leib.p3d` | `blockout_shako_uk.py conjunto=bru`; caveira **traçada da arte** (`britainINFb` c5 r4) |
| Kiwer dos batalhões ligeiros (corneta de metal branco, pompom azul e amarelo) | `HCL_H_BRU1815_Kiwer_Ligeiro` | `hcl_h_uk_bru_ligeiro.p3d` | idem |
| Kiwer da linha (escudo de metal branco com o Welfenross e o número) | `HCL_H_BRU1815_Kiwer_Linha_1` / `_2` / `_3` | `hcl_h_uk_bru_linha.p3d` | idem; número na seleção escondida `numero` |
| Kiwer da Avantgarde, companhias ligeiras (corneta, pluma verde) | `HCL_H_BRU1815_Kiwer_Avantgarde` | `hcl_h_uk_bru_avantgarde.p3d` | idem; o chapéu corso ainda não foi feito |
| Mochila preta com o **cavalo de metal branco na aba** e correias pretas | `HCL_B_BRU1815_Tornister` | a mochila Trotter | `carimbo_mochila_bru.py` [B8] |
| Correame preto | `HCL_V_UK1812_Correame_Preto` | | já existia |

**Variantes** (`gen_variantes_bru.py`): gola e platinas na cor do batalhão; punhos pretos (verdes na Avantgarde); calça preta com **vivo** na cor do batalhão (`calca_vivo`, chave nova do pintor).

| Variante | Unidade | Cor |
|---|---|---|
| B01 | Leib-Bataillon | azul-aço |
| B02 | 1º ligeiro | camurça (Waterloo); rosa só a partir do fim de junho de 1815 |
| B03 | 2º ligeiro | amarelo [B2][B6]; [B5] diz verde |
| B04 | 3º ligeiro | laranja |
| B05 / B06 / B07 | 1º / 2º / 3º de linha | vermelho / verde / branco |
| B08 | Avantgarde, companhias ligeiras | verde |

## 2. Correções feitas depois dos renders

- **Cavalo do escudo, v1:** saía como um "V" ilegível. O v2 tem mais pontos; no v3 o corpo foi inclinado 30° para ficar empinado.
- **Escudo:** o topo afundava 6 mm na parede curva, porque era um leque plano. Agora é montado como as placas traçadas, acompanhando a parede.
- **Número da linha:** estava enterrado dentro do escudo. A faixa agora fica 2 mm à frente.
- **Kiwer:** passou de 12 para **20 mm** de alargamento no alto, conforme a prancha [B8].
- **Mochila:** correias pretas e cavalo na aba [B8].

## 3. Verificações (fora do jogo)

| Verificação | Resultado |
|---|---|
| Dólmã | 12.344 triângulos, 30 botões (10 × 3), 10 fileiras de alamares; saia até 1,077 m |
| Pesos | 6.742 vértices, 62 ossos, no máximo 4 por vértice, soma 1 em todos |
| Barretinas | Leib 14,0 mil, ligeiro 10,7 mil, linha 11,4 mil, Avantgarde 9,5 mil triângulos; caveira traçada com 5 contornos; faixa do número da linha com 56 faces na seleção `numero` (Res 2: 27) |
| PAA | 167 conversões, 0 falhas (tudo do `hcl_uk`) |
| Binarize | Código 0; **26/26 modelos com `OFP2_ManSkeleton`**; avisos só dos 3 materiais do jogo |
| CfgConvert | `config.bin` e 27 rvmat com código 0; 156 itens, 55 soldados, 2 mochilas, 26 `CfgModels` |
| `pbo_verify.py` | `hcl_uk.pbo` 192,0 MB; prefixo `hcl\hcl_uk`; 221 arquivos; sem fontes; **220 referências, nenhuma faltando** |
| Renders | `docs/reports/img/soldado_uk/soldado_bru_*` (Leib, 3º ligeiro, 1º de linha) e `soldado_bru_2_*` (1º ligeiro, 2º e 3º de linha, Avantgarde): o número aparece no escudo ("2"); a mochila tem o cavalo e as correias pretas |

**Não visto no jogo.**

## 4. Pendências 🔶

- **Cavalo dos Guelfos:** é um desenho simplificado meu. Falta o lema *"Nunquam retrorsum"*.
- **Chapéu corso da Avantgarde e casaca cinza dos Jäger:** ainda não foram feitos.
- **Landwehr:** o "Polrock" ainda não foi feito.
- **Leib-Bataillon:** punhos em ponta [B1]; aqui ficaram redondos.
- **Alamares:** pretos sobre preto, quase só se veem pelo relevo, como no original.
- **Renders:** o tampo da Kiwer parece claro nos renders de costas. É brilho de raspão do couro no render de conferência, e a barretina portuguesa mostra o mesmo; não é a textura.
- **Próxima etapa:** KGL e Hanôver.

## 5. Ajustes de 2026-10-19 (tarde), a pedido do usuário

- **Crina do Leib-Bataillon** (*"aumente mais a pumlet ... como na imagem dos batalhões de brunswick"*, depois *"mais alto"*, *"menos volume nas laterais"*, duas vezes): a franja curta virou uma **coluna de 190 mm** com a crina caindo em cone, como os soldados de 1814 da prancha [B8]. A crina cobre o terço de cima da barretina, acima da caveira, e as laterais ficam rentes à parede (v5). A barretina tem 24 mil triângulos, e a Res 2 é reduzida a 40%.
- **Jugular em todas as barretinas** (*"todas as barretinas estão sem as alças"*): correia de couro preto com roseta de metal dos lados (latão nas britânicas e portuguesas, metal branco em Brunswick). Ela desce na frente da orelha, segue o maxilar e passa por baixo do queixo. Foi medida na cabeça do jogo (`TemplateRTM\bust.p3d`: queixo a 0,587 m, roseta a 0,726 m) e fica a ~6 mm da pele. Brunswick tem fonte [B1][B2]; britânicas e portuguesas não têm fonte lida (🔶). O bonnet highland ficou sem.
  - **Erro corrigido:** a primeira versão descia até o peito, porque a cabeça do jogo tem ombros e o "queixo" era o ponto mais baixo da frente. Agora o queixo é procurado só no rosto, logo atrás da ponta do nariz.
- **Build com as jugulares** (19/10, 12:44): 16 barretinas reassadas; 167 PAA, 0 falhas; nenhum modelo sem esqueleto; `hcl_uk.pbo` 194,7 MB; `pbo_verify`: 221 arquivos, 220 referências, nenhuma faltando.
- **Pausado pelo usuário** antes dos renders dos soldados com jugular. A conferência foi feita só na cabeça do jogo (frente, lado e de baixo, sem textura). **Não visto no jogo.**
