# Relatório da Fase 3: Blockout do Uniforme Prussiano 1813

Data: 2026-10-10. Protótipo 2 (`HCL_U_Pruss1813_01`, nome técnico até a decisão U1). **Estado: aguarda aprovação.**

Blockout = formas principais sobre o corpo oficial, sem UV nem texturas finais. As cores dos renders são só para leitura das peças.

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/blockout_uniforme_pruss.py` | Script reproduzível (Blender 5.2, headless) |
| `source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_blockout.blend` | Coleções `HCL_Uniforme_Blockout` (16 peças), `REF_Arma3Samples` (corpo oficial, cabeça aproximada, câmeras, luzes) e `REF_Barretina_aprovada` |
| `docs/reports/img/uniforme/blockout_*.png` | Frente, lado, costas, 3/4 frente, 3/4 costas, detalhe do tronco, detalhe das pernas |
| `docs/reports/uniforme_pruss_blockout_output.txt` | Saída completa do script (medidas, contagens, verificações) |

## 2. Método

- Corpo: `A3_character_example.p3d`, Resolução 1, lido diretamente do Samples. Espaço do personagem: **origem a 1,007 m do chão**, igual à barretina.
- Cada peça é gerada a partir de **cortes exatos do corpo oficial**: as arestas do corpo são cortadas por um plano, os pontos de corte formam o contorno, e o contorno convexo (o pano não entra nas concavidades) é afastado pela folga da ficha.
- As regiões do corpo são escolhidas pelos **pesos dos ossos**: tronco, braços, pernas e pés.
- As articulações (ombro, cotovelo, pulso, quadril, joelho, tornozelo) foram estimadas onde os pesos de dois ossos se misturam. Os valores estão na saída do script.

## 3. Medidas aplicadas (ficha §7 e decisões U2–U6)

| Medida | Valor |
|---|---|
| Costura da cintura | 1,12 m |
| Barra das abas | 0,70 m (U3: meio da coxa) |
| Gola | base 1,535 m (acompanha o pescoço nos lados), altura 0,055 m, 5 mm mais alta atrás |
| Punho | 0,075 m; pala azul 0,11 × 0,04 m com 3 botões, no lado de fora do braço |
| Platinas | 0,13 × 0,05 m, brancas, botão junto à gola |
| Botões da frente | **duas colunas de 7** (U4, como no mod), colunas a 3 cm uma da outra, ⌀ 18 mm |
| Botões das costas | 2 na cintura (ref. M2) |
| Polainas | topo a 0,42 m, 10 botões no lado de fora |
| Sapatos | sola plana **no chão** (não abaixo dele), 8 mm de folga sobre o pé |
| Folgas | casaco 12 mm, mangas 18 → 10 mm no punho, calça 18 → 8 mm dentro da polaina, polaina 12–16 mm, abas 18 → 40 mm |
| Cinto e gravata | Fora (U5, U6) |

**Correção da ficha:** a linha "sola +12 mm sob o pé" (§7) estava errada. A sola não pode descer abaixo do chão do personagem. O sapato envolve o pé a partir do chão.

## 4. Verificações executadas

| Verificação | Resultado |
|---|---|
| Pele exposta (raio na normal de cada vértice do corpo; mãos e pescoço fora da conta) | **1 de 1.180 vértices**, no fundo da virilha (x +0,007, h 0,825), invisível de fora |
| Gola × cabeça **aproximada** (não oficial) | 3 vértices até 1,4 mm dentro. **A cabeça real só pode ser conferida no jogo** (G) |
| Sapatos | Ponto mais baixo a 0,0 mm do chão |
| Triângulos (blockout, com espessura) | 24.648. **Não é o orçamento final**: no blockout cada peça é uma casca dupla, com anéis uniformes |

Partes **dentro do corpo de propósito** (sobreposições do blockout, resolvidas na Fase 4):

| Peça | Onde | Por quê |
|---|---|---|
| Mangas | h 1,39–1,49 | Cabeça da manga entra no tronco |
| Casaco | h 1,35–1,47, lateral | Fica sob a cabeça da manga |
| Gola | base | Encaixada no pescoço e no ombro |
| Calça | h 0,81–0,90 | Sobreposição entre o assento e as pernas |

## 5. Simplificações do blockout (entram na Fase 4)

- As abas são uma superfície lisa: faltam pregas, caimento e bolsos (❓ na ficha).
- O debrum vermelho da frente e os detalhes de costura ficam para a textura (Fase 6).
- Assento e pernas da calça são peças separadas; na produção viram uma malha só.
- Os botões são cilindros simples.

## 6. Observação técnica registrada (Fase 7)

Na leitura do `.p3d`, **a ordem dos vértices das faces deve ser mantida** depois da troca de eixos. Ao inverter a ordem, como fiz até agora, as normais do corpo ficam para dentro (medido: sinal −1). Os scripts de leitura usavam a inversão; isso não afetou nenhuma medida, mas importa na exportação.

## 7. Itens para aprovação

1. Silhueta geral (frente, lado, costas).
2. Comprimento e largura das abas, e a abertura da frente.
3. Altura da gola (0,055 m).
4. As duas colunas de botões, a 3 cm uma da outra.
5. Altura das polainas (0,42 m) e forma dos sapatos.

Depois da aprovação vem a **Fase 4 (malha de produção)**: uma malha contínua com topologia para animação (anéis nos cotovelos, joelhos e ombros), pregas nas abas, orçamento ≤ 12.000 triângulos na Resolução 1 e as mãos do template oficial.
