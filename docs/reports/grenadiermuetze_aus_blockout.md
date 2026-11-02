# Áustria 1809: blockout da barretina de pele dos granadeiros (Fase 3)

2026-11-01. Pedido do usuário: *"Approve, next cap"* (depois de aprovar o tschako). Dossiê: `docs/research/aus/HIST-AUS-INF-TSCHAKO-1809-001.md` §2 (G1–G4); ficha `docs/specs/aus_1809.md` §4 e §8 (AT6).

```
blender -b --factory-startup --python <raiz>/source/scripts/blockout_grenadiermuetze_aus.py -- - <raiz>/source/models/shakos/hcl_grenadiermuetze_aus/hcl_grenadiermuetze_aus_blockout.blend <raiz>/docs/renders/aus
```

O script importa o `blockout_kiver_rus.py` (encaixe e funções de perfil) e o `blockout_tschako_aus.py` (a pala), sem alterar nenhum dos dois. O encaixe vem do blockout britânico, como no tschako.

## Resultado

| Medida | Valor | Fonte |
|---|---|---|
| Altura | 310 mm na frente, 129 mm atrás (300 / 125 × fator de encaixe 1,03) | 🔶 [NAP] |
| Copa | Curva convexa: plana logo atrás da frente, caindo até a nuca; levemente abaulada | ❓ (forma estimada pelas descrições) |
| Pele | Preta, com relevo leve na malha; o pelo de verdade fica para a textura e o normal map (Fase 6) | 🔶 [EMB, NAP] |
| Placa | Latão, ~120 mm de altura, 104 mm de largura, topo em arco, emblema como um boss oval | 🔶 placa [EMB, NAP] / ❓ desenho (G2) |
| Saco de trás (Lehnstuhlmützl) | Na vista do regimento, galão branco de 10 mm nas 4 bordas; 4 variantes | 🔶 [EMB] |
| Pompom | Amarelo com centro preto, no lado direito | 🔶 [EMB] |
| Pala | Couro envernizado, 45 mm, só na frente | 🔶 / ❓ (EMB fala em duas palas; fonte única) |
| Jugular | Couro preto em botões de latão, como no tschako | ❓ |
| Folga | 1,051 (fora da cabeça aproximada) | — |

Variantes (pela ordem da fila nas prévias de frente): IR 1 Kaiser (pompadour), IR 3 Erzherzog Karl (azul-celeste), IR 2 Hiller (amarelo-imperial), IR 39 Duka (vermelho-papoula). Cada uma: 19 peças, 13.320 triângulos (modelo de desenho, não é orçamento de jogo).

Prévias: `docs/renders/aus/blockout_grenadiermuetze_aus_{fila_frente,fila_costas,IR1_lado_direito,IR1_tres_quartos,IR1_costas_3-4}.png`.

## Limitações

- O desenho da placa (águia, monograma, troféu) não tem fonte lida; o boss oval só marca o lugar (G2, AT11).
- A forma exata da copa e o tamanho do saco de trás são estimados; as fontes só dão as duas alturas.
- O pompom e o cocar são uma peça só, como no tschako.
- O encaixe precisa ser refeito com o Samples (B2).
