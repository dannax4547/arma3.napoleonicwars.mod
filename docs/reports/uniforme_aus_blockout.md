# Áustria 1809: casaca alemã e húngara (Fase 3)

2026-11-01. Pedido do usuário: *"Approve, next coat"* (depois de aprovar a barretina de pele). Ficha `docs/specs/aus_1809.md` §2, §3, §5 e §8 (AT7, AT8, AT10); dossiê `docs/research/aus/HIST-AUS-INF-COAT-1809-001.md` (A1–A5).

```
blender -b --factory-startup --python <raiz>/source/scripts/build_uniforme_aus.py -- <raiz>/source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend <raiz>/source/models/coats/hcl_uniforme_aus <raiz>/docs/renders/aus
```

Saídas:
- `source/models/coats/hcl_uniforme_aus/hcl_uniforme_aus_alema_LOD0.blend` (`HCL_U_AUS1809_Alema_LOD0`);
- `…/hcl_uniforme_aus_hungara_LOD0.blend` (`HCL_U_AUS1809_Hungara_LOD0`).

## Base

A AT10 pedia a casaca "derivada da russa". A malha russa tem a borda da frente deslocada para o abotoamento duplo; a austríaca é de abotoamento simples, como a prussiana. Por isso a base é a **malha prussiana de produção** (gola v2), e o que vem da russa é o **método das abas de 400 mm**, copiado (o `build_uniforme_rus.py` não foi alterado). A UV continua a da prussiana; só os 8 botões são peças novas (cópias do botão prussiano).

## Mudanças

| Peça | Antes (prussiana) | Depois (austríaca) | Base |
|---|---|---|---|
| Abas | barra a 0,700 m | **0,738 m** (400 mm abaixo da cintura), redrapejadas sobre a calça | Ficha §8: as da russa até haver fonte ❓ (F1) |
| Frente | 14 botões | **1 fileira de 8**, fechada até a cintura: o 1º 22 mm sob a gola, o último a h 1,158; passo de 45,7 mm; 12 mm para dentro da borda do lado que cobre | 🔶 [WS] (A1) |
| Punho alemão | Punho com portinhola e 3 botões | **Redondo, liso**: portinhola e botões removidos | ❓ (A2, AT8) |
| Punho húngaro | idem | **Pontudo**: a borda de cima sobe em V até **70 mm** no lado de fora do antebraço (meia largura de 60°), por cima da manga. A "pata de urso" fica para a pintura | ❓ (A3, AT8) |
| Pernas alemãs | Calça branca e polainas pretas curtas | **Sem mudança** | 🔶 [NAP, EMB, WS] (A4) |
| Pernas húngaras | idem | **Sem polainas**: os 20 botões das polainas saem; a bainha de cima das polainas (80 faces, debaixo da calça) é removida; a casca das polainas vira a parte de baixo da calça justa; a perna fecha por cima dela, sem degrau no joelho. Cordão e nó austríaco: só na pintura | 🔶 [EMB, NAP, WS] (A5, AT7) |
| Gola | v2, 77 mm na frente | **Sem mudança** | ❓ (F4: nenhuma fonte dá a gola de 1809) |

Saída do script:

```
ABAS: barra 0.738 m (fator 0.909)
FRENTE: 14 botoes prussianos -> 1 fileira de 8 em x -0.013 (painel por cima do lado +x); passo 45.7 mm; h 1.478..1.158
PUNHOS: palas removidas (48 faces) e 6 botoes dos punhos
UNIFORME AUS alema: 6226 vertices, 11612 triangulos
PUNHO HUNGARO E: ponta de 70 mm no lado de fora; 36 vertices
PUNHO HUNGARO D: ponta de 70 mm no lado de fora; 36 vertices
PERNAS HUNGARAS: 20 botoes das polainas removidos; 80 faces da bainha das polainas removidas, franzido desfeito em 180 e perna rente em 122 vertices; 360 faces das polainas viram calca
UNIFORME AUS hungara: 5926 vertices, 11152 triangulos
```

As duas cabem na meta de ~12.000 triângulos da Res 1.

Prévias (cores de identificação, não as finais): `docs/renders/aus/blockout_uniforme_aus_{fila_frente,fila_costas,punho_IR1,punho_IR2,pernas_IR1,pernas_IR2}.png`. A fila mostra, da esquerda para a direita: IR 1 (pompadour, botões amarelos), IR 3 (azul-celeste, brancos), IR 2 (amarelo-imperial, amarelos) e IR 39 (vermelho-papoula, brancos).

## Limitações

- Punhos, gola e comprimento das abas não têm fonte lida (F1, F2, F4). Os primeiros candidatos são Teuber & Ottenfeld e o HGM (AT11).
- Viradas, vivos dos bolsos, "pata de urso", cordão e nó húngaros ficam para a pintura (Fase 6).
- Na perna húngara, o lado de fora mantém a sobreposição abotoada da polaina antiga: uma aresta leve abaixo do joelho (onde vai o cordão) e dois pontinhos onde ela encontra a calça.
- `mesh_review.py`, pesos, LODs e o teste de movimento são das Fases 4–8; a folga da gola precisa da cabeça do jogo (Samples, B2).
