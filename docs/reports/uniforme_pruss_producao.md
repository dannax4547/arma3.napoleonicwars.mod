# Relatório da Fase 4: Malha de Produção do Uniforme Prussiano 1813

Data: 2026-10-10. Objeto `HCL_U_Pruss1813_01_LOD0` (Resolução 1). **Estado: aguarda aprovação.** O blockout foi aprovado implicitamente quando o usuário pediu "mais realismo".

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/build_uniforme_production.py` | Gerador reproduzível (Blender 5.2, headless) |
| `source/scripts/uniform_fit.py` | Ferramentas comuns de encaixe no corpo oficial: cortes exatos, perfis, *loft*, botões |
| `source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend` | Malha (coleção `HCL_Uniforme_Producao`) + referências: corpo oficial, cabeça aproximada, barretina aprovada |
| `docs/reports/img/uniforme/producao_*.png` | Renders: frente, lado, costas, 3/4, detalhes (tronco, abas, punho, pernas) e 3 vistas da malha (`producao_malha_*`) |
| `docs/reports/uniforme_pruss_producao_output.txt` | Saída do gerador (contagens e verificações) |

## 2. Realismo acrescentado ao blockout aprovado

| Peça | O que mudou |
|---|---|
| Casaco | Sobreposição da frente: o lado dos botões fica 1,8 mm acima, com degrau vivo na linha do debrum. Cintura ajustada (−3 mm). **Bainha virada** na borda visível da frente |
| Gola | Anel fechado: parede externa, topo arredondado, parede interna e fundo. 5 mm mais alta atrás |
| Mangas | 3 **dobras de compressão** na dobra do cotovelo e folga sobre o cotovelo. Cabeça da manga enfiada sob o ombro do casaco |
| Punhos | Borda superior encaixada sob a manga, parede, **borda inferior enrolada** e bainha interna |
| Pala brandemburguesa | Painel com espessura, assentado sobre o punho e subindo pela manga; 3 botões |
| Abas | Pano com **forro vermelho** (4 mm de espessura), bordas fechadas, **viras vermelhas** na frente, **caimento** em ondas, **prega** junto à abertura de trás. Por baixo do casaco até a bainha, depois por cima da calça |
| Platinas | Peça com espessura e ponta arredondada junto à gola |
| Calça | Assento justo por baixo do casaco. Pernas que **franzem por cima da polaina**, dobras atrás do joelho |
| Polainas | Bainhas viradas em cima e embaixo, **tira de abotoamento** elevada do lado de fora |
| Sapatos | **Sola com rebordo**, **salto** atrás (2,4 cm), cabedal sobre o pé |
| Botões | Abaulados: frente e costas com 8 lados, punhos e platinas com 6, polainas com 5 |
| Mãos | **As do template oficial, sem alteração**: geometria, UV e pesos dos ossos das mãos e dedos. O corte fica 6 cm dentro da manga |

## 3. Números

| Item | Valor |
|---|---|
| Triângulos | **11.960** (roupa 9.400 + mãos oficiais 2.560). Meta proposta ≤ 12.000: **dentro** |
| Peças (ilhas) | 21 peças nomeadas + botões |
| Materiais | 9: `HCL_la_azul`, `HCL_la_vermelha`, `HCL_la_branca`, `HCL_la_cinza`, `HCL_polaina_preta`, `HCL_couro_sapato`, `HCL_sola`, `HCL_latao`, `HCL_pele_hl` |
| Pele exposta (raio na normal de cada vértice do corpo) | 3 de 1.180: 2 no fundo da virilha (só vistos de baixo) e 1 no pescoço por dentro da gola (coberto pela cabeça) |
| Mãos | Textura/material de origem no template: `hl_white_bald_co.tga` / `hl_white_bald_muscular.rvmat` (gravado no material `HCL_pele_hl`) |

Por peça (triângulos): casaco 1.496 · gola 340 · mangas 2 × 828 · punhos 2 × 180 · palas 2 × 48 · abas 2 × 700 · platinas 2 × 76 · assento 504 · pernas 2 × 504 · polainas 2 × 440 · sapatos 2 × 340 · botões 828 · mãos 2.560.

## 4. Defeitos encontrados e corrigidos nesta fase

| Defeito | Causa | Correção |
|---|---|---|
| Assento da calça aparecendo através das abas | Folgas quase iguais e colunas das abas cortando a curva por dentro | Assento justo (2,5 → 10 mm); abas ≥ 6 mm acima; 13 colunas |
| Manchas vermelhas e azuis no quadril | O recorte da frente deixa as células das abas tortas (não planas); pano e forro triangulados por **diagonais opostas** se cruzavam | Pano e forro triangulados pela **mesma diagonal** |
| Abas cruzando a bainha do casaco | Seções diferentes (casaco × quadril) | Até 1,04 m as abas usam a seção do próprio casaco, com transição suave |
| Autointerseção na bainha do casaco | A bainha interna usava o perfil de outra altura | Perfil interpolado na altura de cada anel |
| Botões pesando 1.560 triângulos | Botões com dois anéis | Um anel + ápice; menos lados nos botões pequenos (1.560 → 828) |
| 38 pontos soltos do template | Faces do antebraço descartadas | Removidos |
| Mangas, gola, punho e topo das pernas com bordas visíveis | Bordas abertas fora de outra peça | Cabeça da manga e topo da perna enfiados; gola fechada; borda do punho por baixo da manga |

## 5. Pendências conhecidas (não bloqueiam a aprovação)

1. Uma linha suave onde o assento encontra as pernas da calça (mesma cor). Na Fase 7 as duas peças podem virar uma só malha.
2. A gola encosta até 1,4 mm na cabeça **aproximada**, que não é a oficial. Só o teste no jogo confirma.
3. Os pesos (esqueleto) das peças da roupa ficam para a Fase 7. Os pesos das mãos vieram do template.
4. As UVs da roupa ficam para a Fase 6. As das mãos são as do template.

## 6. Próximo passo

Aprovação desta malha. Depois: **Fase 6** (UV e texturas, a partir do atlas do mod) e **Fase 7** (pesos, LODs 2–4, sombras, `.p3d` no Object Builder).
