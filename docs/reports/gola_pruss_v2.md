# Gola do uniforme prussiano, correção v2 (as 17 variantes)

2026-10-12. Pedido do usuário: *"o erro nas golas ainda continua — arruma o erro da gola no pescoço do personagem"*.

## Causa

A correção v1 (`gola_pruss.md`, 2026-10-11) moldou a gola em volta de um pescoço de 104 × 104 mm centrado em y = +0,050. Esse pescoço veio da cabeça aproximada e de medições no corpo de animação `TemplateRTM\Male.p3d`, cujo pescoço se perdia no filtro por peso dos ossos.

Nos Samples oficiais existe a **cabeça que o jogo desenha**: `TemplateRTM\bust.p3d`, Resolução 1.
- Textura `a3\characters_f\heads\data\m_white_01_co`.
- Vai de 1,476 a 1,821 m, com o pescoço inteiro.
- A nuca e o "peitilho" dela casam com o corpo oficial `A3_character_example`.

Medida contra essa cabeça (`diag_gola_bust.py`), a gola v1:

| Medida | Gola v1 |
|---|---|
| Garganta em relação à parede interna da gola, na frente | **38 a 44 mm para fora** (a garganta passa por fora da gola) |
| Pontos do pescoço fora da gola/casaco | 54 (frente 26, trás 8, lados 20) |
| Pele visível abaixo do topo da gola | 56 pontos |

O pescoço do jogo tem ~125 × 140 mm. O centro dele vai de y = +0,050 (1,50 m) a +0,004 (1,585 m): a garganta sobe inclinada para a frente.

## Correção

Script: `source/scripts/ajustar_gola_v2.py`. Só move vértices: a malha, a UV e as 17 texturas continuam valendo.

1. **Gola:** cada vértice mantém:
   - o ângulo da sua coluna;
   - a distância à superfície do pescoço (espessura da parede e rolo do topo);
   - a fração de altura entre a base e o topo.

   Ele é recolocado em volta do pescoço do jogo, medido por raios no `bust.p3d`, com o eixo inclinado como o pescoço. A parede interna fica a 7,5–8,5 mm da pele, como antes.
2. **Frente:** a base desce até o peito (1,50 m), porque a garganta do jogo desce até 1,476 m. O topo da frente fica 5 mm mais baixo, a 1,575 m, e o queixo tem 15 mm de folga.
3. **Anéis:** onde a gola tem só dois anéis (base e topo), a parede reta precisa passar a pelo menos 3 mm da pele.
   - Cada anel (base, topo, rolo) é suavizado ao longo da volta, só para fora, e deixado **convexo**, como uma faixa enrolada no pescoço.
   - O anel de fora nunca passa para dentro do de dentro.
   - Sem isso, apareceram uma dobra e uma cunha escura na AO, a 119°, entre duas colunas torcidas.
4. **Casaco:**
   - **Encaixe:** acompanha a base nova até 8 cm de distância, deslizando sobre a superfície antiga.
   - **Trapézio e peitilho:** onde a pele do jogo ainda passaria pelo casaco, ele é empurrado 3 mm para fora, com transição nos vizinhos (14 + 64 vértices, até 8,7 mm).
   - **Platinas e botões:** acompanham o casaco embaixo deles, por interpolação na face. Copiar o vértice mais próximo fez um espinho na ponta da platina, já corrigido.
5. **Pesos** (`teste_movimentos.py`): o peso extra no osso `Neck` agora sobe da base ao topo **de cada coluna** (de 5% a 40%), não mais em alturas fixas. Na frente as alturas mudaram (1,50–1,575 m).
6. **Teste de movimentos:** passou a usar a cabeça do jogo (`bust.p3d`) no lugar da `Male.p3d`.

Cópias de antes: `source/models/coats/hcl_uniforme_pruss/_antes_gola_v2/` (LOD0 e pesos) e `source/textures/hcl_uniforme_pruss/_v2_antes_gola_v2/`.

## Verificações (cabeça do jogo, em repouso)

| Verificação | Antes (v1) | Depois (v2) |
|---|---|---|
| Menor folga pescoço → parede interna da gola | −44 mm (atravessa) | **+2,7 mm** |
| Pontos do pescoço fora da gola/casaco | 54 | **0** |
| Pele visível abaixo do topo da gola | 56 | 5, logo abaixo da borda de cima na nuca (o pescoço saindo da gola) |
| Pescoço atravessando a gola (raio até o eixo) | 49 | **0** |
| Queixo: folga sobre o topo da frente | — (a gola estava atrás da garganta) | 15 mm |
| Gola × casaco (pares de triângulos) | 392 | 222 (a base fica 2 mm dentro do casaco, de propósito) |
| Gola × platinas | 0 | 0 |
| Autointerseção da gola (triangulação real) | 0 | 12 pares, na base a −140°, dentro do casaco |

### Em movimento (`teste_movimentos.py`, cabeça do jogo × gola/casaco/platinas, pares de faces)

| Pose | Pares |
|---|---:|
| Repouso | 2 |
| Em pé, agachado | 4 |
| Sentado mirando | 7 |
| Ajoelhado, deitado | 9–10 |
| Binóculo | 52 |
| Sentado | 74 |
| Morte sentado | 116 |

Nas poses de cabeça baixa, o queixo encosta na frente da gola alta fechada (P6 do teste de movimentos, próprio desse tipo de gola). A execução antiga não é comparável, porque media só o queixo.

### Mod

- Texturas refeitas (17 `_co` + `_nohq` + `_smdi` + AO); PAA sem falhas.
- PBO montado e **instalado às 12:35** (o jogo estava fechado).
- `pbo_verify`: 67 referências, nenhuma faltando. `conferir_regimentos`: 17 uniformes, 14 barretinas, 2 + 2 equipamentos, 0 problemas.

**Não visto no jogo.** A cabeça dos Samples é a `m_white_01`; outras faces do jogo podem ter pescoço um pouco diferente.

## Pontos a observar no jogo

- A bandoleira do correame passa rente ao pé da gola, no ombro esquerdo (1 vértice a 8 mm da parede da gola). O equipamento não foi refeito.
- Um ponto escuro pequeno na base da gola, atrás à direita (render `gola_bust_depois_tras.png`).

## Imagens

`docs/reports/img/gola_bust/`:
- `gola_v2_antes_depois.png`: em cima a v1, embaixo a v2 (3/4, lado, costas);
- `gola_bust_{antes,depois}_*.png`: frente, 3/4, lado, costas, de cima, e de cima sem a cabeça.

Saídas: `gola_bust_*_output.txt`, `ajustar_gola_v2_output.txt`, `work/teste_movimentos_gola_v2b.log`.
