# Relatório da Fase 5: Revisão Técnica da Malha do Uniforme

Data: 2026-10-10. Objeto `HCL_U_Pruss1813_01_LOD0`. Saídas completas: `uniforme_pruss_mesh_review_output.txt` (U1–U6) e `uniforme_pruss_producao_output.txt` (pele exposta, bordas abertas, roupa dentro do corpo).

Ferramentas: `source/scripts/uniform_review.py` (nova, para roupa em camadas) e `mesh_review.py` (genérica, usada na barretina).

## 1. Resultado

| Verificação | Resultado | Situação |
|---|---|---|
| U1 Arestas não-manifold | 0 em todas as peças | ✅ |
| U2 Vértices duplicados / faces de área zero / geometria solta | 0 / 0 / 0. Máximo 4 vértices por face | ✅ |
| U3 Autointerseções dentro de cada peça | **0** (eram 2; ver relatório da Fase 4) | ✅ |
| U4 Interseções entre peças | 553 escondidas, 488 "visíveis" (ver §2) | ✅ após inspeção |
| U5 Orientação das peças fechadas | Gola: volume positivo (normais para fora) | ✅ |
| U6 Triângulos | 11.960 ≤ 12.000 | ✅ |
| Transformações do objeto | Posição 0, rotação 0, escala 1 | ✅ |
| Pele exposta | 3 de 1.180 vértices, nenhum visível de frente, de lado ou de cima | ✅ |
| Roupa dentro do corpo | Só onde é de propósito: cabeça da manga e lateral do casaco sob ela (h 1,36–1,52), topo das pernas da calça sob o assento (h 0,80–0,90), base da gola (até 2,2 mm), ponta da platina (1,8 mm) | ✅ esperado |
| Bordas abertas visíveis de lado ou de cima | Junções na superfície: topo do casaco sob a gola; borda superior do punho sobre a manga; fundo do assento na virilha (6 arestas); borda interna da polaina (1) | 🔶 aceitáveis (§3) |

## 2. Por que "interseção visível" não é defeito aqui

Roupa em camadas tem **linhas de junção**: botão sobre o pano, gola costurada no casaco, punho sobre a manga, pala sobre o punho, sapato dentro da polaina. Nesses pontos as superfícies se cruzam de propósito e a linha aparece, como uma costura de verdade. O teste U4 só diz se a linha se vê de fora, não se ela é errada.

Defeito real é **uma camada que devia ficar por baixo aparecer por cima**. Esse caso foi procurado nos renders e em close com malha (`producao_detalhe_*`, `producao_malha_*`). Dois casos foram achados e corrigidos na Fase 4: o assento aparecendo nas abas e o forro aparecendo através do pano. **Nenhum resta nas vistas renderizadas.**

## 3. Pendências para as fases seguintes

| # | Item | Fase |
|---|---|---|
| R1 | Linha entre o assento e as pernas da calça: unir numa malha só | 7 |
| R2 | Gola × cabeça real (a cabeça aproximada não é oficial) | 9 (jogo) |
| R3 | Pesos: roupa sem pesos ainda; mãos com os pesos do template | 7 |
| R4 | Deformação nas animações (abas × coxas ao correr, agachar e deitar) | 7 e 9 |
