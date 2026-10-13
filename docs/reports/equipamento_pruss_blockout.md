# Relatório da Fase 3: Blockout do Correame e da Mochila

Data: 2026-10-10. **Estado: aguarda aprovação**, junto com a ficha `docs/specs/equipamento_pruss_1813.md`.

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/blockout_equipamento_pruss.py` | Gerador reproduzível |
| `source/models/accessories/hcl_equipamento_pruss/hcl_equipamento_pruss_blockout.blend` | `HCL_Colete_Blockout` (correame), `HCL_Mochila_Blockout` (mochila) e referências (uniforme LOD0, corpo oficial, barretina, cabeça aproximada) |
| `docs/reports/img/equipamento/equip_blockout_*.png` | Frente, lado, costas, 3/4, 3/4 costas, cartucheira, baioneta |
| `docs/reports/equipamento_pruss_blockout_output.txt` | Saída do gerador |

## 2. Método

- Cada correia é um caminho guia sobre o tronco. Cada ponto é **projetado na superfície externa do uniforme**, com raios de fora para dentro, só contra as peças externas (casaco, abas, gola, platinas, assento). Assim a correia nunca cai numa camada interna.
- Sobre o ombro os raios vêm de cima.
- A bainha da baioneta tem três pontos (topo no passador, meio e ponta) projetados para fora das abas e da coxa.
- A mochila apoia-se no ponto mais saliente das costas do casaco e inclina como as costas (6,9°).

## 3. Medidas e contagens

| Item | Valor |
|---|---|
| Cinturão | perímetro 0,937 m, a 1,112 m do chão |
| Bandoleira | frente 0,857 m, costas 0,653 m |
| Bainha | topo a 1,102 m, ponta a 0,665 m, comprimento 0,447 m |
| Triângulos | correame 1.996; mochila 1.492 (blockout) |

## 4. Verificação: peça sob a superfície do uniforme

| Item | Resultado |
|---|---|
| Mochila | **0** de 764 vértices |
| Correame | 15 de 1.024 vértices, **até 3,8 mm**: 13 no meio da bainha, sobre o osso do quadril (a bainha ainda é reta entre 3 pontos), 2 na borda do cinturão |

Correções feitas durante o blockout:
- A ponta da bainha caía dentro da perna da calça (até 136 mm). Agora apoia-se na coxa.
- As correias encostavam na gola. Afastei o caminho sobre o ombro.
- As faces dos chanfros das caixas saíam brancas. Agora herdam o material.

## 5. Para a Fase 4 (se aprovado)

- Bainha curva acompanhando o quadril (elimina os 3,8 mm).
- Fivelas, passadores e rebites. Costuras e bordas boleadas nas correias.
- Cartucheira com tampa sobreposta e alças. Mochila com cantos costurados, pelo da tampa no mapa normal e espirais visíveis nas pontas do capote.
- Pesos nos ossos: tronco e ombros (colete), e mochila (a confirmar no teste B1).
