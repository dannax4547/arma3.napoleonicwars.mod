# Correções e Realismo: Uniforme, Correame e Mochila Prussianos (2026-10-11)

Pedido do usuário: *"continuar a parte final (corrigir erros e trazer mais realismo a tudo)"*.

**Estado:** corrigido e medido fora do jogo (Blender + animações oficiais dos Samples). **Não visto dentro do ARMA 3.**

Legenda: ✅ verificado · 🔶 com ressalva · ❓ não verificado

---

## 1. Linha serrilhada na calça (R1) ✅

**Problema.** Nos renders aparecia um corte serrilhado em volta das coxas, na altura da virilha. Causa:
- o assento (`calca_assento`, até h = 0,86 m) e as pernas (`calca_perna_*`, a partir de 0,90 m) se sobrepunham em 4 cm;
- as folgas se cruzavam (assento 10 mm; topo da perna de 6 a 18 mm);
- então as duas superfícies se cortavam numa linha irregular.

**Correção.** Script `source/scripts/ajustar_calca.py`. Ele só move vértices: a malha e o UV não mudam, então todas as texturas continuam valendo.
- O assento passa a ser a camada de fora até a barra.
- A barra do assento fica 1,5 mm acima da perna original.
- O anel logo acima da barra acompanha metade do movimento dela. Sem isso, os quadriláteros entre os dois entortavam.
- O topo das pernas fica pelo menos 2,5 mm por dentro do assento. Isso é conferido nas **duas diagonais** de cada quadrilátero, porque o render e o exportador podem dividir um quad torto pela outra diagonal (§1.1).
- Backup: `source/models/coats/hcl_uniforme_pruss/_antes_calca/`.

| Medida | Antes | Depois |
|---|---|---|
| Triângulos assento × pernas se cortando (as duas diagonais) | 580 | **0** |
| Topo das pernas fora do assento ou a menos de 2,5 mm | 41 vértices (até 11 mm) | **0** |
| Triângulos com a normal virada mais de 60° | — | 0 |
| Calça × abas / casaca | 45 / 46 / 0 pares | iguais (nada piorou) |

Na textura, a barra do assento não ganha mais bainha (`generate_uniform_textures_v2.py`). O pano passa contínuo para a perna, e a oclusão (AO) foi assada de novo.

Imagens (antes, com a textura antiga; depois, com a geometria e a textura novas):
- `docs/reports/img/correcoes/calca_antes_quadril.png`
- `docs/reports/img/correcoes/calca_depois_quadril.png`
- `docs/reports/img/correcoes/calca_depois_virilha.png` (bem de perto)

### 1.1 Triângulo escuro na virilha (achado e corrigido durante a correção)

A primeira versão da correção deixou um triângulo contornado na frente da calça. Busca da causa:

| Hipótese | Teste | Resultado |
|---|---|---|
| UV sobreposto entre peças | rasterização do atlas a 2048 px | só as mãos do template se sobrepõem, o que é esperado: elas usam a textura de pele do jogo |
| Pontas dos dedos assadas por cima do assento | AO assada sem as mãos | o triângulo continuou (a mudança ficou, porque é mais correta) |
| Face dobrada ou duplicada | normais e autointerseção | nada |
| **Superfície na frente** | raios a partir do ponto | **um triângulo da perna a 0,6 mm na frente do assento** |

A checagem anterior dividia o quad por uma diagonal e o render pela outra. Agora a checagem usa as duas, e o anel acima da barra acompanha a barra.

## 2. Pesos v2: peças sobrepostas se movem juntas

Script `teste_movimentos.py`, com `camadas=v2` como padrão; `camadas=v1` refaz a versão anterior para comparar.

### Regra geral
- Onde uma peça cobre outra, os vértices cobertos recebem os pesos da superfície de cima, com transição de 2–3 cm ao longo da peça de baixo.
- Só entre peças do próprio uniforme. Os pesos do uniforme não dependem do correame nem da mochila, porque esses itens são opcionais.

| Problema | Regra | Antes (pior pose) | Depois |
|---|---|---|---|
| P2 casaca aparecendo na axila | casaca sob a manga segue a manga | 34 mm (em pé), em todas as poses | ✅ 0 em 6 das 8 animações; 1 ponto a 16 mm sentado e 1 a 2,7 mm na morte |
| Manga aparecendo pelo punho | manga sob o punho segue o punho | 13 mm (sentado, binóculo) | ✅ 0 |
| Casaca aparecendo pela gola | casaca sob a gola segue a gola | 7 mm (deitado, morte) | ✅ 0 |
| P7 topo da polaina abrindo | topo da polaina copia a calça embaixo (5 cm de transição) | 9–10 mm (ajoelhado, sentado) | ✅ 0 |
| P1 mão saindo pelo punho (pulso dobrado 90°) | a parte da mão **escondida** no punho segue o punho; a mão visível mantém os pesos oficiais | dorso da mão atravessando a parede do punho | ✅ nas imagens de perto, a mão sai pela abertura, sem atravessar (ver 2.1) |

### 2.1 Mão no punho: o que foi tentado

| Tentativa | Resultado |
|---|---|
| Punho segue a mão até 60% | igual ao v1 (21 mm) |
| Punho segue a mão 100% perto do pulso | **pior**: 28 mm, borda do punho esticada 3,8× e deformada |
| Mão escondida segue o punho (escolhida) | imagens limpas sentado, em pé e ajoelhado. O teste numérico ainda acusa 1–3 pontos, mas isso é da medição: a mão saindo pela abertura do punho conta como "fora" |

Imagens em `docs/reports/img/correcoes/`:
- `punho_sentado_antes_punho_segue_mao.png`: a tentativa rejeitada, com a mão atravessando o dorso do punho;
- `punho_sentado_depois*.png`, `punho_em_pe_depois.png`, `punho_agachado_depois.png`: a versão escolhida.

### 2.2 Correame e mochila (o equipamento se adapta ao uniforme)

| Peça | Regra | Efeito |
|---|---|---|
| Cartucheira | corpo rígido, com a média dos pesos da aba e da casaca embaixo (pelve 0,93) | aba direita × cartucheira saiu da lista de cruzamentos |
| Bainha da baioneta | segue a aba ponto a ponto; perto do passador, segue o passador (8 cm) | bainha × passador: 27 → 8 pares; separação 18 → 6,5 mm |
| Correias de ombro da mochila sobre o correame | seguem o correame por inteiro, mesmo perto da mochila | o correame não sai mais por fora das correias (P4) |
| Correame "dentro" da mochila deitado (até 14 mm) | — | **invisível**: todos os pontos ficam dentro do corpo fechado da mochila (verificado por paridade de raios) |

## 3. Realismo

| Item | Mudança |
|---|---|
| Botões | Sombreamento liso: as arestas dos domos de 5–8 lados estavam marcadas como duras (424 arestas), e os botões pareciam facetados. Ainda se vê a silhueta de 6–8 lados bem de perto (ver §5) |
| Dobras do quadril na calça | Mais suaves e irregulares. As cristas regulares pareciam riscos claros nas coxas |
| Barra do assento | Sem bainha pintada: continua no pano da perna |
| AO | Assada de novo com a gola nova e a calça nova (as texturas eram de antes da correção da gola), numa cópia sem as mãos do template (o UV delas é de outra textura) |
| Variantes | As 17 texturas de cor e os mapas `_nohq`/`_smdi` foram regenerados; backup das anteriores em `source/textures/hcl_uniforme_pruss/_v2_antes_calca/` |

## 4. Verificações do mod montado (2026-10-11, 23:13)

| Verificação | Resultado |
|---|---|
| PAA (`convert_variants_paa.ps1`) | 0 falhas; DXT1/DXT5 conforme o sufixo |
| P3D | pesos **v2** (`hcl_pruss_pesos_v2.blend`, conferido no log `build_p3d_log.txt`) |
| Binarize | exit 0; os 8 modelos com `OFP2_ManSkeleton`. Avisos de material do jogo (pele das mãos, penetração): os de sempre |
| config.bin e rvmat (CfgConvert) | exit 0 |
| PBO (`pbo_verify.py`) | prefixo `hcl\hcl_pruss`; 67 referências, nenhuma faltando; modelos ODOL |
| Regimentos (`conferir_regimentos.py`, sobre o config do próprio PBO) | 17 uniformes + 17 soldados, 14 barretinas, 2 correames, 2 mochilas; **0 problemas** |
| Instalação | `release/@Historical_Clothing/Addons/hcl_pruss.pbo` substituído às 23:13 (o jogo estava fechado) |
| Teste de movimentos final | `docs/reports/img/movimentos/teste_movimentos_camadas_v2_output.txt` |

**Não visto no jogo.**

## 5. Não resolvido / limites

- Silhueta dos botões (6–8 lados): só se resolve com mais segmentos, o que muda a malha e o UV.
- Bordas das platinas e das palas: a transição de cor nas paredes finas (3–4 mm) fica serrilhada bem de perto.
- Pequenos cruzamentos dentro do correame (ponta do cinturão × fivela, chapa × tampa da cartucheira) quando o tronco dobra.
- Nada disso foi visto no jogo.
