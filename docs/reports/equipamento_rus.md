# Rússia 1812: correame e mochila (RU10), texturas, P3D e config

2026-11-01. Pedido do usuário: *"continua contruindo e dá commit, e depois dá push e dá sync changes"*, com *"vamos focar em terminar o russo e depois já ir para o austríaco"*.

**Situação:**
- **Gerado e verificado fora do jogo:** texturas, P3D, `.rvmat`, `config.cpp` e `model.cfg`.
- **Nada testado no ARMA 3** (faltam Tools e Samples).

Dossiê: `docs/research/rus/HIST-RUS-INF-EQUIP-1812-001.md`. Decisão da ficha: RU10 (malha francesa retexturizada, como o K4 britânico).

```
blender -b <raiz>/source/models/accessories/hcl_equipamento_fr/hcl_equipamento_fr_LOD0.blend --python <raiz>/source/scripts/generate_equipment_textures_rus.py -- <raiz>/source/textures/hcl_equipamento_rus nacao=rus granada=1
blender -b <raiz>/source/models/accessories/hcl_equipamento_fr/hcl_equipamento_fr_LOD0.blend --python <raiz>/source/scripts/generate_equipment_textures_rus.py -- <raiz>/source/textures/hcl_equipamento_rus nacao=rus granada=3 only=vest
blender -b --factory-startup --python source/scripts/build_p3d_equip_rus.py -- .
python source/scripts/gen_config_rus.py .
```

## 1. O que muda em relação ao equipamento francês

| Peça | França | Rússia 1812 | Fonte (dossiê) |
|---|---|---|---|
| Bandoleira e talim | Couro branqueado | **Igual** (camurça branqueada) | E2 |
| Cartucheira | Couro preto, placa de latão | Couro preto; a placa vira a **granada do kiver**: 1 chama (mosqueteiros) ou 3 (granadeiros) | E3, E4 |
| Bainha | Couro preto | Couro **natural** (castanho) | E5 |
| Mochila | Couro preto com tampa de pele de bezerro | **Toda de couro preto**; a tampa ganha a borda costurada | E6 |
| Correias da mochila | Brancas | **Não branqueadas** (camurça natural) | E7 |
| Capote | Enrolado em cima da mochila | **Fora da mochila**: as 4 peças do rolo saem da malha (o rolo no ombro fica para o RU9) | E8 |

## 2. Texturas

`source/textures/hcl_equipamento_rus/`, 2048 × 2048, mesmo pintor do Reino Unido (cópia `generate_equipment_textures_rus.py`; o britânico não foi alterado):

- `hcl_v_rus1812_correame_{co,nohq,smdi}.png`: colete de mosqueteiro;
- `hcl_v_rus1812_correame_granadeiro_{co,nohq,smdi}.png`: colete de granadeiro;
- `hcl_b_rus1812_mochila_{co,nohq,smdi}.png`: mochila.

O AO é assado com o uniforme francês como oclusor (o mesmo do Reino Unido).

## 3. P3D

`source/scripts/build_p3d_equip_rus.py`: malhas e pesos aprovados do equipamento francês (`source/models/pesos/hcl_fr_pesos.blend`). Sem o Samples, os P3D franceses servem de modelo (propriedades do Res 1 e Geometry vazio do template oficial).

| P3D | Res 1 | Ossos |
|---|---|---|
| `hcl_v_rus1812_correame.p3d` | 3.176 triângulos (igual ao francês) | 12 |
| `hcl_b_rus1812_mochila.p3d` | 2.456 triângulos (o francês tem 3.776; o rolo saiu) | 10 |

- Seleção `camo` em tudo; os dois coletes usam o mesmo P3D, só muda a textura.
- `.rvmat`: um por peça em `data/` (`hcl_v_rus1812_correame.rvmat`, `hcl_b_rus1812_mochila.rvmat`), a estrutura do `.rvmat` britânico. O colete de granadeiro usa o `_nohq` do de mosqueteiro (só a granada muda).

## 4. Config

O `gen_config_rus.py` agora gera também:
- **`HCL_V_RUS1812_Correame`** e **`HCL_V_RUS1812_Correame_Granadeiro`** (coletes, `Vest_Camo_Base`, Arsenal);
- **`HCL_B_RUS1812_Mochila`** (mochila, `Bag_Base`, Arsenal);
- `class hcl_v_rus1812_correame: ArmaMan {};` e `class hcl_b_rus1812_mochila: ArmaMan {};` no `model.cfg`.

Os soldados continuam sem equipamento de saída, como os britânicos: o equipamento é escolhido no Arsenal.

## 5. Limitações

- **Pesos:** os do correame francês, sem teste com a casaca russa nas animações (precisa do Samples). A casaca russa sai da malha prussiana, de volume próximo ao da francesa; ver a prévia.
- **Cartucheira:** a malha francesa tem 208 × 130 mm; a de 1808 tem 254 × 190 mm.
- **Não modelados:** cantil em cima da mochila, terceira correia no peito (1809), botões de madeira das correias, rolo do capote no ombro (RU9).
- **Distintivo:** o contorno da placa francesa (60 × 38 mm, 0,7 mm de relevo) ainda aparece de leve em volta da granada.
- **Ajuste à casaca:** nas prévias, a bandoleira e o talim encostam na aba da casaca russa no quadril; sem teste nas animações.

## 6. Prévias

`docs/renders/rus/equipamento_soldado_rus_*.png` (`render_texturas_rus.py ... equipamento=1`): os 4 regimentos com correame e mochila. O primeiro soldado (R01) usa o colete de granadeiro (`_cartucheira`, 3 chamas); o segundo, o de mosqueteiro (`_cartucheira_mosqueteiro`, 1 chama).
