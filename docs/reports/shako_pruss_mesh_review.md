# Relatório: Revisão Técnica da Malha (Fase 5)

Objeto: `HCL_Shako_Pruss_LOD0` em `source/models/shakos/hcl_shako_pruss/hcl_shako_pruss_LOD0.blend`
Ferramenta: `source/scripts/mesh_review.py` (só leitura), executada no Blender 5.2.2 em 2026-10-09.
Saída completa da última execução: `docs/reports/shako_pruss_mesh_review_output.txt`.

## 1. Resultado final (3ª execução)

| Verificação | Critério | Resultado |
|---|---|---|
| M1 Normais e orientação | Volume com sinal positivo em todas as ilhas (normais para fora) | ✅ 8/8 ilhas |
| M2 Vértices duplicados | 0 (< 0,001 mm) | ✅ 0 dentro das ilhas, 0 entre ilhas |
| M3 Buracos / arestas não-manifold | 0 arestas de borda; 0 não-manifold | ✅ 0 / 0 (todas as cascas fechadas) |
| M4 Faces de área zero e geometria solta | 0 | ✅ 0 faces degeneradas, 0 vértices e arestas soltos |
| M4b Vértices por face | ≤ 4 (`.p3d`) | ✅ máximo 4 (2.190 quads, 814 triângulos) |
| M5 Interseções entre peças | 0 pares | ✅ 0 |
| M5 Autointerseções dentro das peças | 0 pares não adjacentes | ✅ 0 |
| M6 Transformações | Posição 0, rotação 0, escala 1 | ✅ |
| M7 Polígonos | ≤ 6.000 triângulos (proposta) | ✅ 5.194 |
| Espessura nas bordas visíveis | Ver `shako_pruss_producao.md` §4 | ✅ medida no script (valores de construção) |

Distribuição: couro envernizado 1.330 · couro 1.208 · latão 1.156 · tecido branco 476 · feltro 440 · forro 360 · lã amarela 140 · tecido preto 84.

## 2. Defeitos encontrados e correções

| Execução | Defeito | Causa | Correção |
|---|---|---|---|
| 1ª | 8.826 triângulos; monograma com 4.844 | Curvas da fonte em resolução alta + fusão das letras | Resolução das curvas 4 → 2; limpeza pós-fusão |
| 1ª | Monograma achatado (0,084 × 0,036 m) | Letras lado a lado | Letras entrelaçadas → 0,084 × 0,047 m |
| 2ª | 12 faces de área zero e 3 autointerseções no monograma | Lascas deixadas pela fusão booleana | Solda de pontos (0,01 mm), dissolução de degeneradas, junção de faces coplanares e nova triangulação |
| 2ª | Corpo × cocar: 10 pares | Faces grandes na traseira do cocar cortavam o degrau do debrum | Rampa de folga de 6 mm e mais anéis na traseira |
| 2ª | Corpo × jugular: 20 pares; botões × jugular: 8 + 8 | Jugular a 0,1 mm da faixa; botões encostados na jugular | Jugular a 0,5 mm da faixa; base dos botões acima da jugular |
| 3ª | Cocar com 1.008 triângulos (densidade alta para a peça) | Anéis traseiros em excesso | 28 segmentos e 4 anéis traseiros → 560, sem novas interseções |

## 3. Pendências (não verificáveis nesta fase)

| Item | Motivo | Quando |
|---|---|---|
| Interseção com a **cabeça real** do ARMA 3 (testa, orelhas, queixo) | A cabeça oficial é um *proxy* do jogo e não está disponível como malha | Teste no jogo G6/G7 |
| Deformações e articulações | Item rígido preso ao osso `head`; a única parte sensível é a jugular (mandíbula animada) | G7 |
| Limite de polígonos por LOD | Medido no Buldozer (Object Builder) | Fase 7 (B2) |
| LODs 2, 3, sombra, Geometry, ViewPilot | Fazem parte da preparação para o ARMA 3 | Fase 7 |
| Normais exportadas e arestas duras no Object Builder | Dependem da importação FBX | Fase 7 (B1) |

**Conclusão:** a malha LOD 0 passou em todas as verificações automáticas desta fase. As pendências acima dependem do jogo ou do Object Builder e estão registradas em `testing.md`.
