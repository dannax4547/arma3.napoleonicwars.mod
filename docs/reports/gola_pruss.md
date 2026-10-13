# Correção da gola do uniforme prussiano (todas as 17 variantes)

2026-10-11. Pedido do usuário: "corrige a gola das roupas para ficarem corretas no pescoço".

## O problema (visto no jogo)

No print do jogo, a **frente da gola não aparecia**: a garganta da cabeça cobria a gola, e o vermelho só aparecia dos lados e atrás.

| Medida da gola antiga | Valor |
|---|---|
| Abertura interna | 190 mm de largura × 91 mm de profundidade (oval achatado) |
| Parede interna da frente | y = +0,011 m, só 1 cm à frente do eixo do corpo |
| Causa | `build_uniforme_production.py` moldou a gola no casco convexo do corte do corpo a 1,555 m, incluindo a subida dos ombros (até \|x\| = 0,10 m), em vez de só o pescoço |

## A correção

Script: `source/scripts/ajustar_gola.py`. Só **move vértices**: a malha, a UV e as 17 texturas continuam valendo.

- **Gola:** anel em volta de um pescoço de 104 × 104 mm centrado em y = +0,050. A parede interna fica a 7,5–8,5 mm do pescoço, como antes. A espessura, o rolo do topo e as alturas foram mantidos.
- **Abertura nova:** cerca de 120 × 120 mm por dentro (antes 190 × 91).
- **Frente:** de 20 mm (base) a 27 mm (topo) **mais à frente**, inclinada como a garganta (0,12 m/m), com a borda 8 mm mais baixa na frente para dar espaço ao queixo.
- **Encaixe do casaco** (até 7 cm da base da gola): acompanha o deslocamento da base deslizando **sobre a superfície antiga**, então o formato do ombro não muda.
- **Platinas e seus botões:** não se mexem. Os 2 botões do casaco que ficam no encaixe se movem inteiros.
- **Pesos:** o alto da gola agora segue o osso `Neck` em cerca de 45% (base 5%), para acompanhar o pescoço quando a cabeça se mexe. Antes era 80% `Spine3` e 11% `Neck`. Feito em `teste_movimentos.py`; os pesos estão em `hcl_pruss_pesos_v1.blend`.

Cópias de antes: `source/models/coats/hcl_uniforme_pruss/_antes_gola/` (LOD0 e pesos).

## Verificações

| Verificação | Antes | Depois |
|---|---|---|
| Autointerseções (revisão de malha U3) | 0 | 0 |
| Gola × platina, pares visíveis (cada lado) | 10 | **0** |
| Casaco × gola, pares visíveis | 62 | 38 |
| Correame e mochila sob o uniforme | 0 | 0 |
| Queixo × gola (pares), em pé (pose do print) | 0 | 0 |
| Queixo × gola, agachado / sentado / morte / binóculo | 26 / 31 / 64 / 0 | 20 / 37 / 70 / 25 |
| Barretinas × uniforme, todas as poses | 0 (morte: 0) | 0 |
| Mod refeito | — | PBO verificado: 8 modelos com esqueleto, 67 referências, nenhuma faltando; instalado às 14:52 |

O contato do queixo com a cabeça baixa é próprio de uma gola alta fechada (P6 do teste de movimentos).

**Limite:** a cabeça do jogo é binarizada e não vem nos Samples. O molde `TemplateRTM\Male.p3d` tem a mandíbula mais baixa e peças auxiliares, então serve para os contatos em movimento, mas não para medir a folga exata. A confirmação final é no jogo.

## Defeito achado no teste de movimentos

A cabeça de referência do `teste_movimentos.py` ficava **sem pescoço**: as faces do pescoço caíam no filtro por peso dos ossos da cabeça. O contato "CABECA" mede, portanto, queixo e mandíbula.

Ficou corrigida a união dos pontos duplicados nas costuras (os pedaços pequenos não são mais descartados). O filtro por peso continua. Medir o pescoço exige uma cabeça do jogo.

## Imagens

`docs/reports/img/gola/`:
- `gola_antes_depois.png`: sem cabeça, de cima, 3/4 e lado;
- `gola_peito_antes_depois.png`: peito, com a cabeça de exibição.
