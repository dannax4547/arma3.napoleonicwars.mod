# Velha Guarda, barretinas novas e mais regimentos (2026-10-12/13)

Pedidos do usuário:
- *"agora cria mais regimes para a franca e prussia com barretinas novas e na franca inicia a velha guarda tudo de uma forma profissional e com bastante detalhe nos modelos"*;
- no meio do trabalho, *"traz mais realismo a bear skin e aumenta mais os pumlets dos granadeiros e voltigeurs"* e uma foto de referência: *"faz igual a este"*;
- *"atualiza o mod"*.

Respostas do usuário às perguntas:
- fazer tudo em paralelo;
- topo do chapéu de pele com **cruz branca**;
- na Prússia: plumet verde, Stutz da Guarda e boné da Landwehr;
- abas longas **só para a Guarda**.

Inventário: `inventario_guarda_regimentos.md`. Ficha da Guarda: `docs/specs/velha_guarda.md`.

**Nada foi visto no jogo.** Tudo foi feito e verificado fora dele.

## 1. Velha Guarda (França)

**Chapéu de pele**, em 3 variantes: granadeiro de gala, granadeiro de campanha e caçador de gala.

| Detalhe | Como foi feito |
|---|---|
| Pelo | Geometria de verdade, sem textura com transparência. São 2 camadas de mechas: cerca de 880 curtas (sub-pelo) e 970 longas, de 5,8 a 9,2 cm. As mechas descem pela superfície e saem em redemoinho do alto. Atrás e dos lados caem sobre a faixa; na testa, não. Cada mecha recebe um ladrilho com ~180 fios em 3 tons |
| Forma | Como na foto: alarga para cima e tem o topo quase plano. 0,32 m acima da faixa |
| Placa | Latão, com o contorno medido na arte do mod (águia entre granadas) e o relevo assado da própria arte. O pelo cai sobre a borda de cima, como na foto |
| Trança | Branca, larga, na diagonal da frente (foto). Cada trança da espinha é uma peça abaulada; borla no alto |
| Cordões | Pelo lado direito, até 2 raquetes chatas e 2 borlas com franja |
| Topo | Vermelho, com cruz branca de galão |
| Pluma | 0,38 m, larga e solta, do lado esquerdo. Caçador: verde embaixo e vermelha em cima. Cocar tricolor |
| LODs | Res 1 completa (≈ 22,6 mil triângulos na gala). Res 2 sem as mechas (≈ 11,3 mil), para a distância |

**Casaca de abas longas**, com 2 variantes: granadeiro e caçador.
- Mesma cadeia já validada da casaca francesa, com a barra das abas em **0,64 m** (a de 1812 fica em 0,907 m).
- Dragonas da casaca de elite.
- Ornamentos nas viradas: águia + granada no granadeiro; corneta + granada no caçador. A águia foi traçada da arte do mod.
- Malha com 16.414 triângulos. Pesos refeitos com as 8 animações.
- Ponto a observar no jogo: sentado e ajoelhado, as abas longas esticam mais e cruzam as pernas mais vezes que as abas curtas (8 ocorrências contra 4).

## 2. Barretinas francesas

| Item | O que mudou |
|---|---|
| Plumet do granadeiro e do voltigeur de gala | **Maior**: 0,38 m (era 0,30), raio 54 mm (era 42), penas mais longas e em mais camadas. O topo passou de 1,25 m para 1,33 m |
| Placa em losango | Nova, de latão e de metal branco (arte `FranceINF` c3 r4); no metal branco, jugular e rosetas também são brancas |
| 2ª, 3ª e 4ª companhias de fuzileiros | Pompom azul-celeste, aurora e violeta. Só textura: o modelo é o da 1ª companhia. Existem para a placa de águia e para as duas de losango |

## 3. Prússia

| Item | O que foi feito |
|---|---|
| Plumet verde (arte do mod) | Nas 14 barretinas existentes: 14 classes novas. A pluma tem textura própria; a textura da barretina continua trocável |
| Stutz da Guarda a Pé | Branco em cima e preto embaixo 🔶, na estrela prateada. 2 classes |
| Boné da Landwehr | Copa de pano com pregas, faixa colorida, pala de couro, forro, suadouro e cruz da Landwehr em metal branco 🔶. 5 cores do mod: azul/vermelha, azul/amarela, verde/preta, azul/verde, azul/branca. **Anacrônico com o Kollet** (a Landwehr usava a Litewka), como você aceitou |

Imagens:
- `docs/reports/img/cabeca_pruss/`
- `docs/reports/img/bonnet_guarda/`
- `docs/reports/img/barretina_fr_lote2/`
- `docs/reports/img/bone_landwehr/`

## 4. Telas azuis do PC (2026-10-12, 20:58 e 21:29)

| Item | Detalhe |
|---|---|
| Erro | Duas telas azuis com `0x1E KMODE_EXCEPTION_NOT_HANDLED`, `c0000005` |
| Culpado | A análise do Windows aponta **`BEDaisy.sys!Unloaded`**, o driver do BattlEye, nas duas |
| Situação | Nas duas vezes, o Arma 3 com BattlEye estava aberto enquanto o Blender assava texturas com a CPU a 100% |
| O que não foi | As texturas novas **não estavam carregadas no jogo**, então não foram a causa |

Medidas tomadas:
- **nenhum bake nem build roda com o Arma 3 ou o BattlEye aberto**: a cadeia confere entre cada etapa e para sozinha se o jogo for aberto;
- o Blender roda com 8 dos 16 threads.

Para testar o mod, dá para abrir o Arma sem BattlEye (opção do Launcher).

## 5. Addons

| Addon | Situação | Verificação |
|---|---|---|
| `hcl_pruss.pbo` | 64,6 MB, remontado e instalado em 13/10 às 12:20, com os nomes em inglês | 54 itens, 17 soldados, 13 modelos com esqueleto, CfgConvert 0, `pbo_verify`: 84 referências, nenhuma faltando |
| `hcl_fr.pbo` | 113 MB, remontado e instalado em 13/10 às 12:20 | Ver §5.1 |

Mudanças nas ferramentas:
- os scripts de build agora acusam modelos declarados no `model.cfg` que não foram gerados (um erro de Python tinha passado despercebido);
- `release\atualizar_mod_teste.bat` troca os **dois** PBOs.

### 5.1 Addon francês

| Item | Resultado |
|---|---|
| Itens | 34 (13 soldados, 1 mochila) |
| Barretinas | 20 |
| Modelos | 17, todos com `OFP2_ManSkeleton` |
| Chapéus de pele | Res 1 + Res 2 (gala: 22.604 / 11.288 triângulos; campanha: 15.698 / 4.430) |
| Barretinas de gala | 14.752 (granadeiro) e 14.326 (voltigeur) triângulos |
| PAA | 69 de 69 com o cabeçalho certo (DXT1, `_nohq` DXT5) |
| CfgConvert | 0 erros |
| Binarize | Avisos só dos 3 materiais do jogo de sempre |
| `pbo_verify` | 103 referências, nenhuma faltando |

**Novo nesta rodada: capote azul de campanha da Velha Guarda (W05).**
- É uma variante de textura do capote.
- Tem dragonas vermelhas pintadas nas platinas e calça azul.
- Cores 🔶, sem fonte lida.
- Classe `HCL_U_Fr1812_Capote_W05`, chamada *"French Greatcoat - Imperial Guard, Foot Grenadiers (Old Guard), blue campaign greatcoat"*.

### 5.2 Nomes em inglês (pedido de 13/10)

`source/scripts/nomes_en.py` dá o nome em inglês de **todas** as classes. Os geradores o aplicam e a montagem falha se faltar algum. Só muda o nome que aparece no jogo; as classes `HCL_*` continuam iguais.

**Regimentos nomeados só com fonte citada** (🔶: fontes de hobby e Wikipedia; conferir em Knötel ou Osprey):

| Variante | Nome |
|---|---|
| V05 | 1st Silesian |
| V06 | 2nd Silesian |
| V07 | 2nd Pomeranian |
| V15 e V16 | Silesian Schuetzen Battalion |
| F04 | 1st Swiss Regiment |
| Bonés C02 e C05 | Silesian / Pomeranian Landwehr |
| Guarda | Foot Grenadiers e Foot Chasseurs (Old Guard) |

O restante leva nome descritivo com *"unidentified"*:
- golas vermelhas prussianas (Brandemburgo ou Prússia Oriental);
- gola azul-clara;
- Jäger verdes;
- F02 e F03;
- bonés C01, C03 e C04.

### 5.3 Imagens

- `docs/reports/img/guarda/velha_guarda_*`: soldados completos (frente, costas, busto, ombro, abas);
- `docs/reports/img/bonnet_guarda/textura_fr_*`: chapéus de pele;
- `docs/reports/img/barretina_fr_lote2/`: losangos e gala;
- `docs/reports/img/cabeca_pruss/`: plumet, Stutz e bonés.

### 5.4 A observar no jogo (`docs/testing.md` §5)

1. **Abrir sem BattlEye.**
2. Abas longas sentado e ajoelhado.
3. O pelo da frente do chapéu de pele desce até as sobrancelhas: ver se atrapalha a visão em primeira pessoa.
4. Desempenho dos chapéus de gala.
5. Troca para a Res 2 ao se afastar.

## 6. Rodada de 13/10: mais regimentos franceses, plumets e barretinas mais realistas

Pedido: *"adiciona mais regimentos para a franca e de mais realismo as pumlets e as barretinas francesas"*.

### 6.1 Regimentos novos

| Item | Fonte | Classes |
|---|---|---|
| **Infantaria ligeira** (*Infanterie Légère*), 3 companhias. Casaca azul com lapelas azuis debruadas de branco, gola vermelha (voltigeur: camurça debruada de vermelho), botões de metal branco, dragonas verde com meia-lua vermelha (caçador), vermelha (carabineiro) e verde com meia-lua amarela (voltigeur), cornetas e granadas nas viradas | 🎮 `FranceINF` c0 r2; calça azul e cor dos ornamentos 🔶 | `HCL_U_Fr1812_Ligeira_Cacador`, `..._Carabineiro`, `..._Voltigeur` |
| Barretinas da ligeira: placa em losango de metal branco (caçadores, 4 companhias) e gala de carabineiro (pluma e cordões vermelhos) e de voltigeur (pluma verde de ponta amarela, cordões verdes) | 🎮 losango branco `FranceINF` c5 r4; cores dos cordões 🔶 | `HCL_H_Fr1812_Fuzileiro_LosangoBranco_*` (agora "Light Infantry, Chasseur"), `HCL_H_Fr1812_Ligeira_Carabineiro_Gala`, `..._Voltigeur_Gala` |
| **Regimentos de linha numerados**: número vazado no campo liso da base da placa de águia (`numerar_placa_fr.py`). São o 18e *le Brave*, o 46e, o 57e *le Terrible* e o 84e *Un contre Dix* | 🎮 campo da base na arte; número vazado e apelidos 🔶 (conhecimento geral) | `HCL_H_Fr1812_Linha_018`, `_046`, `_057`, `_084` |

Os regimentos de linha usavam todos a mesma casaca de 1812 (F01). Por isso o número na placa é o que os distingue.

### 6.2 Plumets mais realistas (`plumet.py estilo="v4"`)

- **Penas:** cada uma com 3 segmentos e nervura central elevada, com as duas metades da pena em leve "V". A ponta é fina, curva para fora e um pouco de lado. O avesso só existe no último segmento, onde a ponta curvada o mostra.
- **Textura das penas:**
  - cerca de 110 barbas finas por lado, saindo da nervura em direção à ponta, cada uma com seu tom;
  - pequenas aberturas entre grupos de barbas perto da borda;
  - nervura mais clara, porque tinge menos;
  - base mais escura.
- **Onde:** nas barretinas de gala (granadeiro, voltigeur, ligeira) e na do coronel. As plumas prussianas continuam no estilo v3 (não pedido).

### 6.3 Barretinas mais realistas (`blockout_shako_fr.py`)

- Topo de **couro**, levemente rebaixado no centro (3 mm), com costura enrolada na borda.
- **Suadouro** de couro e **forro** de linho por dentro, visíveis por baixo.
- **Borda da pala** dobrada em couro.
- Feltro com pequenas ondulações para dentro, de até 1,2 mm, entre as faixas. Nunca para fora, para não atravessar placa, rosetas e divisas.

**Triângulos:**

| Barretina | Antes | Agora |
|---|---|---|
| Fuzileiro | 6,4 mil | 7,6 mil |
| Gala | 14,7 mil | 17,3 mil |

### 6.4 Addon francês remontado (13/10, 13:1x)

| Item | Resultado |
|---|---|
| PBO | `hcl_fr.pbo`, 135 MB, instalado direto (jogo fechado) |
| Itens | 43 (16 soldados) |
| Modelos | 19, todos com esqueleto |
| PAA | 82 de 82 com o cabeçalho certo |
| CfgConvert | 0 erros |
| `pbo_verify` | 120 referências, nenhuma faltando |

Erro encontrado e corrigido no caminho: um comentário acrescentado em `convert_fr_paa.ps1` ficou na mesma linha de um laço de uma linha só e anulou o `}`. A conversão parou com erro de sintaxe. O `pbo_verify` acusou as 13 texturas faltando; corrigi o script, converti de novo e remontei.

Imagens: `docs/reports/img/lote3_fr/` (`ligeira_*` e `linha_*`) e `docs/reports/img/barretina_fr_lote3/`.

**Não visto no jogo.**

## 7. Rodada de 13/10 (tarde): mais polígonos, detalhes e medidas com fonte histórica

Pedido: *"faz mais profissionalmente com mais poligonos e adicoes de detalhes e altura com fontes historicas sobre o exercito napoleonico"*.

Fontes e medidas: `docs/specs/barretina_francesa_1812.md` §7. São o regulamento de 1812 (Bardin, citado em fórum de reconstituição), peças de museu e leilão (Bertrand-Malvaux, 1er-empire.com), Wikipedia e Calpe Miniatures.

### 7.1 Barretinas francesas (v4)

| Item | Antes | Agora (fonte) |
|---|---|---|
| Altura do feltro, fuzileiro | 196 mm | 202 mm (Bardin; peças de 200 mm) |
| Altura, granadeiro e carabineiro da ligeira | 196 mm | 217 mm (+15 mm, Bardin) |
| Topo | 258 mm | 244 mm (modelo de 1810) |
| Faixa de cima / de baixo | 30 / 20 mm | 41 / 27 mm (Bardin) |
| Pala | 55 mm | 58 mm (Bardin: 54–61) |
| Placa de águia | 83 × 105 mm | 96 × 122 mm (peças: ~13 cm de altura) |
| Placa de granadeiro | 111 × 105 mm | 135 × 128 mm |
| Rosetas | ⌀ 24 mm | ⌀ 41 mm (peças: 40–42 mm) |
| Escamas da jugular | 14 → 11 mm | 34 → 21 mm, estampadas em relevo |
| Suadouro | 39 mm | 57 mm |

**Detalhes novos:**
- 96 segmentos em volta (eram 48);
- cocar com pregas de verdade;
- cordões em dois fios torcidos;
- placa mais subdividida, para acompanhar a curva da parede;
- pompom mais liso.

**Triângulos e nível de detalhe:**

| Barretina | Res 1 | Res 2 (nova) |
|---|---|---|
| Fuzileiro | ≈ 14 mil | ~40 %, para a distância |
| Gala | ≈ 26–28 mil | ~40 %, para a distância |

### 7.2 Chapéu de pele (v4)

| Item | Antes | Agora (fonte) |
|---|---|---|
| Altura | 32 cm | 35 cm na frente, 39 cm atrás (Bertrand-Malvaux) |
| Largura no alto | 24 cm | 27 cm (Bertrand-Malvaux) |
| Placa | 128 × 91 mm | 217 × 153 mm (placas autênticas de 21,7 × 15,7–16 cm) |
| Topo | disco de 92 mm | oval de 135 × 115 mm |
| Pluma | 38 cm | 35 cm, encaixe a 24 cm |
| Pelo | 1,8 mil mechas | 2,6 mil mechas |
| Casco | 48 × 26 segmentos | 72 × 36 segmentos |

**Triângulos:**

| Chapéu | Res 1 | Res 2 (sem mechas) |
|---|---|---|
| Gala | ≈ 31,6 mil | ≈ 15 mil |
| Campanha | ≈ 24,6 mil | — |

**Decisão G7:** cruz (1804–1807) ou granada (1808–1815) no topo. Ver `velha_guarda.md` §4.

### 7.3 Incidente da pausa e correção (13/10, 14:05 → 17:06)

**O que aconteceu:**
- A primeira "pausa" não encerrou a cadeia em segundo plano.
- A cadeia continuou e montou às 14:05 um `hcl_fr.pbo` com 6 barretinas com **textura v4 sobre malha v3**: fuzileiro (e as companhias 2–4 e os regimentos 18/46/57/84 derivados dele), granadeiro e voltigeur de gala e de campanha, e coronel.
- A partir daí, "pausar" encerra a árvore inteira de processos (`taskkill /T` no PID de `work/cadeia.pid`), e eu confiro que não sobrou nada.

**Correção:**
- Bake v4 completo das 10 barretinas em `hcl_shako_fr_texturas_v3.blend`, das 16:28 às 17:01.
- Na sequência: pompons, números das placas, PAA (82 tarefas, 0 falhas), montagem e verificação.

| Barretina | Res 1 | Res 2 | Topo (m do chão) |
|---|---|---|---|
| Fuzileiro (1ª comp.) | 14.208 | 5.683 | 0,989 |
| Losango / losango branco | 13.484 | 5.392 | 0,989 |
| Granadeiro de campanha | 15.320 | 6.127 | 1,017 |
| Voltigeur de campanha | 14.152 | 5.659 | 1,003 |
| Coronel | 21.538 | 8.615 | 1,253 |
| Granadeiro de gala | 27.546 | 11.018 | 1,349 |
| Voltigeur de gala | 26.258 | 10.503 | 1,334 |
| Ligeira, carabineiro de gala | 25.654 | 10.261 | 1,351 |
| Ligeira, voltigeur de gala | 25.534 | 10.213 | 1,334 |
| Chapéu de pele de gala | 31.568 | 15.452 | 1,333 |
| Chapéu de pele de campanha | 24.630 | 8.562 | 1,110 |
| Chapéu de pele de caçador | 31.306 | 13.210 | 1,334 |

**`hcl_fr.pbo` às 17:06 (144,4 MB):**
- 43 itens e 16 soldados;
- 19 modelos, todos com esqueleto; 19 rvmat compilados;
- 120 referências, nenhuma faltando no PBO.

Renders em `docs/reports/img/v4_fr_corrigido/`. **Nada foi visto no jogo ainda.**
