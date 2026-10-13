# Relatório: Modelagem de Produção da Barretina (Fase 4)

Data: 2026-10-09 · **Estado: aguarda aprovação do usuário (V3)** · Blockout aprovado (V2) em 2026-10-09.

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/build_shako_production.py` | Script reproduzível (gera a malha, os renders e o `.blend`) |
| `source/scripts/shako_fit.py` | Medidas e encaixe aprovados no blockout (fonte única) |
| `source/models/shakos/hcl_shako_pruss/hcl_shako_pruss_LOD0.blend` | Objeto `HCL_Shako_Pruss_LOD0` (coleção `HCL_Shako_Producao`) + referências em `REF_Arma3Samples` (**não exportar**) |
| `docs/reports/img/producao/*.png` | Vistas, detalhe, sem cabeça e topologia (aramado) |

## 2. Decisões aplicadas

| Decisão | Origem |
|---|---|
| Silhueta, medidas e encaixe do blockout (H 0,206 m; base 0,186 × 0,210; topo 0,251 × 0,283; inclinação 8°) | Blockout aprovado |
| Pala a 55°, 0,068 m | Usuário |
| Jugular sob o queixo | Usuário. **Ajustada a uma cabeça estimada; validação obrigatória no jogo (G6/G7)** |
| Objeto único em coordenadas do personagem, transformações aplicadas | Padrão do item de cabeça oficial |
| Faces de 3 ou 4 vértices (n-gons triangulados) | Limite do formato `.p3d` (MLOD) |
| Materiais de pré-visualização (cores lisas), **sem UV e sem textura** | Fases 6–7 |

## 3. Componentes, topologia e justificativa de geometria separada

| # | Peça (ilha) | Construção | Triângulos | Por que é uma peça separada |
|---:|---|---|---:|---|
| 0 | Corpo | Uma casca fechada, perfil girado em 40 segmentos: faixa envernizada com bordas roladas e degrau, feltro, debrum de couro com degrau dobrado sobre a borda arredondada (raio 4,5 mm), copa côncava (3 mm), forro interno de 4 mm | 1.920 | — (peça principal) |
| 1 | Pala | Casca fechada: grade 24 × 6, espessura 2,5 mm, debrum arredondado na borda; raiz encostada na faixa, sem penetração | 850 | Placa fina presa por fora da faixa; unir à casca exigiria geometria interna |
| 2 | Cocar | Casca abaulada (28 segmentos), centro preto, face traseira acompanhando a folga sobre o feltro e o debrum | 560 | Peça aplicada sobre o feltro, com relevo próprio |
| 3 | Presilha | Fita em relevo (1,4–1,8 mm) com ponta arredondada; começa logo abaixo da borda do cocar | 140 | Aplicada sobre o feltro |
| 4–5 | Botões laterais | Domos de latão (16 segmentos) acima da jugular | 96 + 96 | Peças metálicas aplicadas |
| 6 | Monograma "FWR" | Letras em relevo de 1,5 mm (fonte Gabriola), entrelaçadas e **fundidas numa casca única** (união booleana + limpeza), 0,084 × 0,047 m | 964 | Relevo de latão aplicado |
| 7 | Jugular | Fita de 12 × 1,8 mm ao longo de uma curva que sai dos botões e passa sob o queixo | 568 | Correia que sai do volume da barretina |

**Total: 5.194 triângulos** (orçamento proposto: ≤ 6.000). Para comparação, o LOD 1 do boné oficial tem 400 faces; a barretina tem muito mais volume e detalhe.

Densidade: maior onde a silhueta e o brilho pedem (bordas roladas, debrum, pala), menor nas superfícies retas (o feltro tem só 2 linhas verticais de apoio). Costuras, tramas e o plissado do cocar ficam para o normal map (Fase 6), não para a geometria.

## 4. Espessuras

| Elemento | Espessura |
|---|---|
| Parede de feltro e forro | 4 mm |
| Faixa envernizada sobre o feltro | 1,8–2,1 mm |
| Debrum sobre o feltro | 1,2–1,4 mm |
| Pala | 2,5 mm (+ debrum de ~1,2 mm) |
| Cocar | 3,2–3,6 mm sobre a superfície |
| Presilha | 1,1–1,5 mm |
| Monograma | 1,5 mm |
| Jugular | 1,8 mm |

## 5. Pendências que passam para as próximas fases

- Monograma: a fonte Gabriola (Windows) gera uma interpretação caligráfica, não uma cópia do monograma da foto. A fonte é usada só como forma geradora; se o projeto um dia for distribuído, a licença dela precisa ser verificada.
- Jugular: ajustada a uma cabeça **estimada**; validar no jogo (G6/G7). A mandíbula do ARMA 3 se mexe com as animações faciais; a folga foi incluída de propósito.
- LODs 2–3, LOD de sombra, Geometry e ViewPilot: Fase 7.
- Limite de polígonos por LOD no Buldozer: Fase 7 (teste B2).
