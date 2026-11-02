# Áustria 1809: blockout do tschako de 1806 (Fase 3)

2026-11-01. Pedido do usuário: *"Approve all"* (AT1–AT11 da ficha `docs/specs/aus_1809.md`). Dossiê: `docs/research/aus/HIST-AUS-INF-TSCHAKO-1809-001.md` (T1–T6).

```
blender -b --factory-startup --python <raiz>/source/scripts/blockout_tschako_aus.py -- - <raiz>/source/models/shakos/hcl_tschako_aus/hcl_tschako_aus_blockout.blend <raiz>/docs/renders/aus
```

O script importa o `blockout_kiver_rus.py` (encaixe na cabeça e funções de perfil), que não foi alterado. Sem o Samples, o encaixe vem do blockout britânico aprovado, como no kiver russo.

## Resultado

| Medida | Valor | Fonte |
|---|---|---|
| Altura | 215 mm (208 × fator de encaixe 1,03) | 🔶 8" [WS, EMB] e 20,5 cm [NAP] |
| Base / topo | 186 × 210 mm / 213 × 237 mm (topo 1" mais largo) | 🔶 [WS] |
| Tampo | Couro envernizado, rebaixado 12 mm | 🔶 [EMB] |
| Faixas | Couro preto envernizado: 50 mm em cima (com costura), 20 mm embaixo | 🔶 [WS] / ❓ (a de baixo) |
| Palas | Frente 79 mm a 20°; trás 40 mm a 38° | 🔶 [WS, EMB] / ❓ (a de trás) |
| Frente | Pompom amarelo de centro preto no topo, presilha de latão até um botão de latão; sem placa | 🔶 [WS, EMB] |
| Jugular | Couro preto em botões de latão | 🔶 [WS] |
| Folga | 1,052 (fora da cabeça aproximada) | — |

Modelo de desenho: 21 peças, 15.680 triângulos (não é orçamento de jogo).

Prévias: `docs/renders/aus/blockout_tschako_aus_{frente,lado,tres_quartos,costas}.png`.

## Limitações

- O cocar amarelo-preto e o pompom são a mesma peça (pompom amarelo com centro preto, preso pela presilha); as fontes os citam juntos, sem dizer se são duas peças.
- A pala de trás e a faixa de baixo não têm medida nas fontes.
- O encaixe precisa ser refeito com o Samples (B2).
