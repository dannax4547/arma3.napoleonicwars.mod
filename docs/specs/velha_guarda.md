# Ficha técnica: Velha Guarda, granadeiros e caçadores a pé (Fases 2–4)

Data: 2026-10-12. Pedidos do usuário:
- *"na franca inicia a velha guarda tudo de uma forma profissional e com bastante detalhe nos modelos"*;
- *"traz mais realismo a bear skin e aumenta mais os pumlets"*;
- *"faz igual a este"*, com uma foto de referência de um chapéu de pele: pelo longo, trança branca diagonal na frente, pluma vermelha grande e aberta, placa de latão embaixo.

Legenda: 🎮 visto na arte do mod (pacotes **Reto**, autorizados) · 📷 foto do usuário · 🔶 suposição ou fonte não lida.

O atlas `imperial_guardsb` do pacote LME4 **não foi aberto**, porque a autorização do LME4 não está confirmada (F7). Inventário: `docs/reports/inventario_guarda_regimentos.md`.

## 1. Chapéu de pele (*bonnet à poil*)

| Item | Valor | Confiança |
|---|---|---|
| Forma | Alarga para cima (1,30 × a faixa no alto), topo quase plano com borda arredondada, 0,32 m acima da faixa | 📷 forma; 🔶 medidas |
| Pelo | Duas camadas de mechas de geometria: cerca de 880 curtas (sub-pelo) e 970 longas (5,8 a 9,2 cm). As longas descem pela superfície, com as pontas erguidas, saem em redemoinho do alto e caem sobre a faixa (exceto na testa) | 🎮 pelo preto em tufos; 📷 pelo longo |
| Placa | Latão, águia entre granadas, ponta embaixo, contorno medido na arte (`FranceINF` c2 r4); 128 × 91 mm. O pelo cai sobre a borda de cima | 🎮 desenho; 🔶 altura (a arte é achatada, esticada 1,9×) |
| Trança | Branca, larga e chata, na diagonal da frente: do alto à direita do soldado até o canto esquerdo da placa. Feita com tranças em espinha (cada uma uma peça abaulada) e com borla no alto | 📷 |
| Cordões laterais | Do alto da trança, pelo lado direito, até 2 raquetes chatas e 2 borlas com franja | 🎮 cordões e raquetes brancos; 🔶 posição |
| Topo de trás | Vermelho, com **cruz branca** de galão (decisão do usuário). O mod mostra uma granada | 🎮 vermelho; cruz 🔶 por escolha do usuário |
| Pluma | Vermelha, 0,38 m, larga e solta, do lado esquerdo, em tulipa de latão. Caçadores: verde embaixo, vermelha em cima | 🎮 vermelha; 📷 volume; 🔶 cores dos caçadores |
| Cocar | Tricolor, do lado esquerdo, sob a pluma | 🎮 |

**Variantes:**
- `granadeiro_gala`: placa, trança, cordões e pluma;
- `granadeiro_campanha`: só a placa;
- `cacador_gala`: sem placa, com trança, cordões e pluma verde e vermelha.

**Malha** (`source/scripts/blockout_bonnet_guarda.py`):

| Variante | Res 1 | Res 2 |
|---|---|---|
| Gala | ≈ 22,6 mil triângulos | ≈ 11,3 mil |
| Campanha | ≈ 15,7 mil | — |

A **Res 2 não tem as mechas**: o casco leva a textura de pelo e serve para a distância. O topo da gala fica a 1,32 m do chão.

**Texturas:** `texturizar_shako_fr.py raiz=GD_ nome=HCL_Bonnet_Fr_ textura=hcl_bonnet_fr_`, 2048 px.
- Cada mecha tem um ladrilho de fios (cerca de 180 fios ondulados por ladrilho, 3 tons).
- O casco recebe pelo procedural.
- A placa tem relevo assado da arte do mod.
- A trança e os cordões têm trama.

## 2. Casaca (*habit* de abas longas)

| Item | Valor | Confiança |
|---|---|---|
| Corte | A casaca francesa com **abas até 0,64 m do chão** (`build_uniforme_fr.py hem=0.64`, a de 1812 vai a 0,907 m). Dragonas de `build_casaca_elite_fr.py nome=HCL_U_Fr1812_Guarda_LOD0` | 🎮 abas longas e viradas vermelhas (`FranceINF` c3 r3); 🔶 comprimento |
| Granadeiro | Azul imperial; gola azul; lapelas brancas sem debrum; punhos vermelhos com portinhola branca; viradas vermelhas debruadas de branco, com **águias e granadas** cor de aurora; dragonas vermelhas; calça branca; polainas pretas | 🎮 dragona vermelha e águia nas viradas (c3 r3); restante 🔶 |
| Caçador | Igual, com portinhola vermelha, dragonas verdes com meia-lua vermelha, **cornetas e granadas** nas viradas | 🔶 (não há bloco do mod) |
| Ornamentos | Águia traçada da arte (`FranceINF` c3 r3, `tracar_ornamentos_fr.py`); granada e corneta já existiam | 🎮 forma; cor 🔶 |

- **Malha:** 16.414 triângulos (Res 1).
- **Pesos:** `source/models/pesos/hcl_fr_guarda_pesos.blend`, gerados por `teste_movimentos.py`.
- **Texturas:** `source/textures/hcl_uniforme_fr_guarda/`, variantes em `variantes_fr_guarda.json`.

## 3. Decisões pendentes

| # | Pergunta | Usado até a resposta |
|---|---|---|
| G1 | Altura do chapéu (0,32 m) e placa esticada 1,9× | Como está |
| G2 | Comprimento das abas (0,64 m do chão) | Como está |
| G3 | Cores do granadeiro sem fonte (gola azul, portinhola branca, ornamentos cor de aurora) | Como está |
| G4 | Caçadores: pluma verde e vermelha, dragonas verdes com meia-lua vermelha | Como está |
| G5 | Nomes de unidade: "Velha Guarda, granadeiro / caçador" (pedido seu); o resto continua técnico | Como está |
| G6 | Peso do chapéu de gala (22,6 mil triângulos na Res 1; Res 2 com 11,3 mil) | Manter, olhar o desempenho no jogo |

**Fontes:** não foi lida nenhuma fonte primária sobre a Guarda. Os detalhes 🔶 vêm de conhecimento geral e precisam de conferência; sugestão: pranchas de Martinet, Rousselot.

## 4. Revisão com fontes (2026-10-13)

As medidas do chapéu de pele foram refeitas pelas fontes listadas em `barretina_francesa_1812.md` §7.1:

| Medida | Valor |
|---|---|
| Altura | 35 cm na frente, 39 cm atrás |
| Largura no alto | 27 cm |
| Placa | 217 × 153 mm |
| Topo | oval de 135 × 115 mm |
| Pluma | 35 cm, com encaixe a 24 cm |
| Mechas | ~1.300 curtas + ~1.360 longas |

**Atenção, decisão G7 (nova):** as fontes dizem que a **cruz** do topo é do modelo **1804–1807**. De **1808 a 1815**, época do mod, o topo levava uma **granada branca**, como a arte do mod. A cruz foi mantida por escolha do usuário; trocar pela granada é só mudar a peça do topo.
