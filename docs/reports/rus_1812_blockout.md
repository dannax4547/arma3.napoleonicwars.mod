# Rússia 1812: blockout da casaca e dos kivers (Fase 3)

2026-10-17. Pedido do usuário: *"Aceito as recomendações RU3–RU10. Segue para o blockout (Fase 3): casaca, kiver de 1812 e kiver de 1808."*

Ficha: `docs/specs/rus_1812.md` v1.0 (RU3–RU10 aprovadas). **Nada foi visto no jogo.** Tudo foi verificado fora do Arma 3, e **sem o Arma 3 Samples**, que ainda não está instalado nesta máquina (§4).

## 1. O que foi feito

| Peça | Arquivo | Script |
|---|---|---|
| Casaca de linha 1812 (corpo inteiro: casaca, calças, polainas, sapatos, mãos do template) | `source/models/coats/hcl_uniforme_rus/hcl_uniforme_rus_linha_LOD0.blend`, objeto `HCL_U_RUS1812_Linha_LOD0` | `build_uniforme_rus.py` |
| Kivers de 1812 e de 1808, mosqueteiro e granadeiro (4 peças) | `source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_blockout.blend` | `blockout_kiver_rus.py` |
| Renders do blockout | `docs/renders/rus/` | os dois scripts acima + `render_blockout_rus.py` |

Comandos (Blender 5.2, sem interface):

```
blender -b --factory-startup --python source/scripts/build_uniforme_rus.py -- source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend source/models/coats/hcl_uniforme_rus/hcl_uniforme_rus_linha_LOD0.blend
blender -b --factory-startup --python source/scripts/blockout_kiver_rus.py -- - source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_blockout.blend docs/renders/rus
blender -b --factory-startup --python source/scripts/render_blockout_rus.py -- . docs/renders/rus samples=32
```

O `-` do segundo comando quer dizer "sem Samples". Com o Samples instalado, passa-se a pasta `Test_Character_01`.

## 2. Casaca

Derivada da malha prussiana de produção (gola v2), pelo mesmo método da francesa e da britânica. **Nenhuma topologia nova:** a UV e os mapas do pintor continuam valendo.

| Mudança | Antes (prussiana) | Depois (russa) | Base |
|---|---|---|---|
| Barra das abas | 0,700 m | **0,738 m** (400 mm abaixo da cintura de 1,14 m), redrapejadas sobre a calça com o código britânico | ✅ [V10B] 15¾" (1802) |
| Botões da frente (v2, 2026-10-17) | 2 colunas de 7, passo de 51 mm (h 1,170–1,478) | **6 + 6 botões chatos** (altura × 0,6), **passo de 64 mm**, 1º par 22 mm sob a gola, último na cintura (h 1,158–1,478) | Dossiê C2, C3: tabela de 1802 (⅞", 2⅝", "chatos") e a casaca original do Hermitage |
| Distância entre as fileiras | 34 mm | **36 mm**, paralelas | Dossiê C1: Hermitage ~37 mm, tabela de 1802 32 mm. **A prancha 1359 (~100 mm) foi rejeitada**: gravura estilizada, abaixo do objeto original na hierarquia de fontes |
| Botões das abas | — | **1 por aba, onde as viradas se juntam** (h 0,768) | Dossiê C6: tabela de 1802 |
| Gola | 77 mm na frente, 59 mm atrás | **70 mm na frente, 54 mm atrás** (fator 0,914). A v1 desta casaca tinha 55 mm, baixa demais | Dossiê C4: "baixa" em 1812 (sem medida); Hermitage de 1812–1817 ~75 mm |
| Polainas até o joelho | topo a 0,42 m | **só na pintura**: `hcl_polaina_topo = 0,52` m guardado no objeto para o pintor | ✅ [V10B] (1 jan 1812) |
| Portinhola do punho | 3 botões | 3 botões | ✅ tabela de 1802 (2 no punho + 1 na portinhola), casaca do Hermitage e prancha 1359 |

**Fonte:** dossiê `docs/research/rus/HIST-RUS-INF-COAT-1812-001.md`. O usuário pediu para afastar as fileiras pela prancha 1359. A pesquisa achou uma casaca original de 1812–1817 no Hermitage com as fileiras juntas (~37 mm), o que bate com a tabela de 1802. Pela hierarquia de fontes da especificação mestre (§4), **o objeto original e o regulamento prevalecem sobre a gravura**, então as fileiras ficaram em 36 mm. O que o objeto e a tabela pediam de fato era o **passo maior** (64 mm), a **gola mais alta** (70 mm), os **botões chatos** e os **botões das viradas**.

**Como a gola desceu.** Cada vértice da gola desliza para baixo ao longo da parede da sua própria coluna, no ângulo em torno do eixo da v1 (o mesmo que `ajustar_gola_v2.py` preserva). A fração de altura f entre a base e o topo vira f × 0,914. A base, a espessura e a dobra do topo não mudam. **A folga do pescoço precisa ser medida de novo com a cabeça do jogo** (`diag_gola_bust.py`, que precisa do Samples).

Saída do script (v2):

```
ABAS: barra 0.738 m (era 0.700); fator 0.909; afastamento da calca preservado em 642 vertices (min -0.8 mm, mediana 14.3 mm; minimo imposto 4 mm); 86 sem calca na direcao (so a altura muda); 2 botoes das abas movidos
FRENTE: 14 botoes prussianos trocados por 12 (achatados x0.6); fileiras a 36 mm; passo 64 mm; h 1.158..1.478 (pe da gola 1.500; barra da frente 1.103)
ABAS: botao das viradas em cada aba (x, h): [(0.109, 0.768), (-0.108, 0.768)]
GOLA: 23 faixas de 15 graus; frente 77 -> 70 mm, tras 59 -> 54 mm (fator 0.914); 152 vertices movidos; topo agora h 1.593 (era 1.598)
UNIFORME RUS: 6470 vertices, 11960 triangulos (Res 1; o prussiano tem 11960 + gola)
```

`mesh_review.py` (v2): M1–M4 = 0; as mesmas 3 autointerseções da malha prussiana; corpo × abas 68 / 69 pares (sem mudança); **11.960 triângulos**.

Renders da casaca v2: `blockout_soldado_rus_peito_frente.png` (para comparar com a casaca do Hermitage) e `blockout_soldado_rus_abas_costas.png` (botões da cintura e das viradas).

## 3. Kivers (v3, sobre fontes históricas)

**Histórico:**
- **v1:** sino simétrico;
- **v2:** a partir das fotos de réplicas do usuário (confiança baixa);
- **v3:** refeita sobre o dossiê de pesquisa `docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md`, a pedido do usuário ("utiliza fontes históricas … mais profissional e detalhista").

**Fontes principais:**
- o **kiver original do Hermitage** (ЭРТ‑10900/10804, Guarda, 1812–1817);
- as **pranchas 1308, 1320, 1323 e 1359 do Viskovatov** (ГПИБ);
- o **texto das ordens** (Viskovatov, vol. 10).

Cada linha da tabela abaixo cita a decisão do dossiê (D1–D17).

| | Kiver de 1812 | Kiver de 1808 |
|---|---|---|
| Altura (× encaixe 1,032) | **184 mm na frente, 153 mm atrás**: o tampo desce 6° para trás (D1, D3; perfil da prancha 1323) 🔶 | 196 mm (proporção da barretina francesa) ❓ |
| Base / topo | 186 × 210 → **252 × 288 mm**: frente +6, lados +32, trás +70 mm; laterais côncavas (D2) 🔶 | 206 × 233 mm, quase cilíndrico ❓ |
| Corpo | **Pano preto fosco** sobre couro (D4) | Feltro |
| Tampo, faixas, tiras, pala | Couro **envernizado**: faixa de cima de 18 mm com costura, faixa de baixo de 20 mm, um V de 22 mm em cada lado, **tira de ajuste atrás** de topo arredondado (D5–D8) | Couro |
| Pala | 62 mm, 22°, borda debruada (D16) | igual |
| Granada | Bola de ⌀ 22 mm, chama central em lágrima de 46 mm com bordas onduladas; granadeiro com 2 chamas laterais **curtas** (26 mm, 55°) (D9) | igual |
| Pompom | **Oval em pé de lã felpuda**, 76 × 48 × 22 mm, anel + centro oval, **2 hastes de arame** (D10). 1º batalhão: mosqueteiro branco/verde, granadeiro vermelho | igual |
| Presilha | Couro preto envernizado, do alto até a chama (D11) | igual |
| Pluma (granadeiro) | Crina preta em clava, 420 mm, domo arredondado, **320 mechas soltas**, suporte envernizado (D12) | igual |
| Cordões | **Duas tranças chatas em espinha de peixe** de 22 mm (frente baixa e trás). Lado esquerdo: 2 borlas curtas. Lado direito: pendente com **raquete trançada** e 2 borlas, até a mandíbula (D13, D14) | igual |
| Barbicacho | **18 escamas** por lado, de 33 a 20 mm, sobre **rosetas de ⌀ 44 mm** com anéis e domo (D15) | Correia de couro |

Saída do script (v3):

```
ENCAIXE (lido do blockout britanico aprovado (hcl_shako_uk_blockout.blend); Samples ausente): head_cy -0.0136 z_testa 0.7181 cabeca 0.174 x 0.197, topo 0.826, inclinacao lida 8.00 graus
ENCAIXE k=1.0317 base 186 x 210 mm
KIVER 1812_mosqueteiro   altura frente 184 mm, tras 153 mm; topo 252 x 288 mm  pecas 49  triangulos 48632 cordoes=28448 corpo_e_resto=16920 jugular=3264
KIVER 1812_granadeiro    altura frente 184 mm, tras 153 mm; topo 252 x 288 mm  pecas 53  (com a pluma e as mechas)
KIVER 1808_mosqueteiro   altura frente 196 mm, tras 196 mm; topo 206 x 233 mm  pecas 47  triangulos 46304
FOLGA (todas)            menor distancia normalizada parede/cabeca 1.051 (> 1 = fora da cabeca aproximada)
```

**Os triângulos (46–53 mil por kiver) são do modelo de fonte (high‑poly).** As tranças (28 mil) e as borlas são modeladas ponto a ponto **para servirem de fonte de bake**. Na Fase 4, viram uma faixa simples com normal map, como manda o pipeline (especificação mestre §21, passos 6–11). A barretina prussiana de produção tem 5.194 triângulos. **Nenhum destes números é orçamento de jogo.**

## 4. Sem o Arma 3 Samples: o que foi feito no lugar

| Precisa do Samples | Feito no lugar | A refazer quando o Samples chegar |
|---|---|---|
| Faixa da cabeça (`shako_fit.compute` sobre `A3_headgear_example.p3d`) | **Lida de volta** do blockout britânico aprovado: a matriz do kiver (head_cy −0,0136, testa 0,7181, inclinação 8,00°) e a cabeça aproximada (0,174 × 0,197, topo 0,826). É o mesmo encaixe de todas as barretinas | Rodar `blockout_kiver_rus.py` com a pasta `Test_Character_01`: o script usa o Samples e imprime o encaixe; deve dar os mesmos números |
| Cabeça do jogo (`TemplateRTM\bust.p3d`) para gola e barbicacho | Cabeça aproximada (elipsoide do blockout francês) | `diag_gola_bust.py` na gola russa; render com a cabeça do jogo |
| Corpo do Samples para `uniform_review.py` (cruzamentos visíveis × escondidos) | `mesh_review.py` (§5) | `uniform_review.py` na Fase 5 |

## 5. Verificações (fora do jogo)

`mesh_review.py` na casaca russa, comparada com a prussiana de origem e com a britânica, que usa o mesmo redrapejamento das abas:

| Verificação | Prussiana | Russa | Britânica |
|---|---|---|---|
| M1 ilhas de volume invertido ou abertas | 0 | 0 | 0 |
| M2 vértices duplicados | 0 | 0 | 0 |
| M3 arestas não-manifold | 0 | 0 | 0 |
| M4 faces de área zero, geometria solta | 0 | 0 | 0 |
| M5 autointerseções dentro das ilhas | 3 | 3 (as mesmas) | 3 |
| M5 corpo da casaca × abas (pares, E / D) | 45 / 47 | **68 / 69** | 167 / 163 |
| M7 triângulos | 11.960 | 11.912 | 11.864 |

O aumento dos cruzamentos corpo × abas fica na cintura (h ~1,10 m), onde as abas entram sob o corpo da casaca. Com o mesmo método, a britânica tem mais que o dobro. Se eles aparecem ou não, só o `uniform_review.py` diz (Fase 5, com o Samples).

Kivers: as paredes internas e as carneiras ficam fora da cabeça aproximada (distância normalizada 1,05 > 1).

## 6. Renders

`docs/renders/rus/`:
- `blockout_kiver_rus_fila_frente.png`, `_fila_tres_quartos.png`: os 4 kivers;
- `blockout_kiver_rus_<kiver>_lado.png`: cada um de lado;
- `blockout_soldado_rus_fila_{frente,costas,tres_quartos}.png`: soldado de 1812 (mosqueteiro, granadeiro, kiver de 1808) e a casaca prussiana ao lado, para comparar;
- `blockout_soldado_rus_lado_1812_mosqueteiro.png`, `_lado_prussiano_comparacao.png`: abas e gola de lado;
- `blockout_soldado_rus_gola_{tres_quartos,lado}.png`: a gola baixa de perto.

Cores chapadas por peça, sem textura. As viradas vermelhas das abas e a polaina pintada até o joelho ficam para a Fase 6.

Kiver v3, renders novos:
- `blockout_kiver_rus_1812_granadeiro_frente_P1.png` e `_perfil_P1.png`: as mesmas vistas da prancha 1323 (frente; perfil direito de quem veste);
- `blockout_kiver_rus_1812_mosqueteiro_detalhe.png` (3/4), `_costas.png`, `_cordao_macro.png` (granada e trança de perto).

**Comparação com as fontes (inspeção visual, não medida):**

| Ponto | Prancha 1323 / Hermitage | v3 |
|---|---|---|
| Perfil: frente quase vertical, traseira alargada, tampo caindo para trás | ✓ | ✓ |
| Cordão baixo na frente, acima da faixa de baixo | ✓ | ✓ |
| Pendente com raquete atrás da roseta, até a mandíbula | ✓ (1323) | ✓ |
| Borlas curtas no lado esquerdo de quem veste | ✓ (Hermitage, 1359) | ✓ |
| Granada de 3 chamas com laterais curtas | ✓ | ✓ |
| Pluma em clava de crina | ✓ | ✓ (mechas no corpo; o domo fica liso) |
| Trança em espinha de peixe | ✓ | 🔶 de frente lê como trança; **em macro e de lado ainda parece corda torcida**. O bake da Fase 6 decide a leitura final |

## 7. Pendências e pontos 🔶 / ❓

- **Casaca:** corrigida pela pesquisa (dossiê da casaca, C1–C6). A prancha 1359 foi rejeitada na distância entre as fileiras, porque a casaca original do Hermitage e a tabela de 1802 mostram ~32–37 mm.
- **RU5 resolvida:** a portinhola do punho tem 3 botões (prancha 1359); a malha já tem 3.
- **I1 do dossiê:** o kiver côncavo como regulamento de 1812 é contestado. Os dois modelos continuam (RU3).
- **Atlas russo** (`rus1812INF`, `rus1812INF2`) ausente: as cores e a arte do mod ficam por conferir.
- **Gola 55 / 43 mm:** sem medida de fonte; a folga do pescoço só se mede com o Samples.
- **Kiver de 1808:** sem medida de fonte.
- Triângulos dos kivers: o modelo de jogo e o bake entram na Fase 4.

## 8. Decisões (RB1–RB3 aprovadas pelo usuário em 2026-10-17)

| # | Pergunta | Recomendação |
|---|---|---|
| RB1 | Casaca v2: aprovar fileiras a 36 mm, passo de 64 mm, botões chatos, botões das viradas, gola de 70 mm e abas a 0,738 m (dossiê C1–C6) | **Sim** |
| RB2 | Aprovar o kiver de 1812 v3 (dossiê D1–D17) | **Sim** |
| RB3 | Aprovar o kiver de 1808 (196 mm, quase cilíndrico, sem fonte de medida) | **Sim**, como peça estimada |
