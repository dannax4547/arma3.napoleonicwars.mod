# Ficha Técnica: Uniforme de Infantaria de Linha Francesa, 1812–1815 (Fuzileiro)

Fase 2 do pipeline. Versão 1.0, 2026-10-12. **Estado: aguarda aprovação do usuário** (decisões F1–F8, §10).

Protótipo da segunda nação, a pedido do usuário (*"dar continuidade às próximas nações"*). A ordem das nações está em `docs/reports/inventario_nacoes.md`.

Legenda: ✅ confirmado · 🔶 provável (conhecimento geral, sem fonte lida nesta fase) · ❓ incerto · 🎮 visto na textura do mod

---

## 1. O que muda em relação à Prússia (reaproveitamento)

No ARMA 3 o uniforme é o corpo inteiro do personagem (verificado nos Samples, ficha da Prússia §1). Por isso tudo o que foi validado na Prússia vale aqui:

| Reaproveitado sem mudança | Novo para a França |
|---|---|
| Template oficial (mãos, LODs técnicos, proxies), gravador de P3D, `model.cfg`, build e verificação do PBO | Malha da **casaca** (lapelas, abas curtas, viradas, gola, punho com pala) |
| Pesos v2 (camadas que se movem juntas) e teste de movimentos com as 8 animações | **Barretina francesa** (outra forma e outra placa) |
| Pintor de texturas v2 (AO, costuras, desgaste, lama, variantes só de cor) | **Correame francês**: dois boldriés cruzados no peito, em vez de cinturão + uma bandoleira |
| Calça, polainas e sapatos: mesma construção, com outras cores e alturas | Mochila: provavelmente o mesmo tipo (pele de bezerro com capote enrolado) 🔶; só muda o detalhe |

## 2. Identificação

| Item | Valor | Confiança |
|---|---|---|
| Peça | Casaca de infantaria de linha de **abas curtas e lapelas fechadas até a cintura** (*habit-veste*, regulamento de 1812, dito "Bardin") | 🎮 forma no bloco M1; nome e data 🔶 |
| Estado e período | Império Francês, campanhas de 1812–1815 | Escopo; atlas `FranceINF*` |
| Companhia de partida | **Fuzileiro** (companhia do centro): platinas azuis com debrum vermelho, sem dragonas | 🎮 M1 (platinas com contorno vermelho) |
| Regimento | **Não identificado**; nomes técnicos (`HCL_U_Fr1812_01`…) até haver os nomes do mod | ❓ |

## 3. Referências (só leitura; cópias em `docs/references/img/`)

| ID | Arquivo | O que mostra |
|---|---|---|
| M1 | `ref_fr_01_casaca_fuzileiro_mod.png` (`FranceINF_diffuse`, bloco c4 r2) | **Principal**. Casaca azul planificada:<br>• lapelas brancas com debrum vermelho e **7 botões** cada;<br>• abas curtas com **viradas brancas** e enfeite azul (N coroado);<br>• bolsos verticais com debrum vermelho e 3 botões;<br>• gola vermelha com debrum branco;<br>• punho vermelho com debrum branco e uma pala de 3 botões;<br>• platinas azuis com debrum vermelho;<br>• cartucheira preta com N coroado |
| M2 | `ref_fr_02_casaca_lapelas_brancas_mod.png` (c5 r0) | Mesmo padrão de M1 (variação de pintura) |
| M3 | `ref_fr_03_casaca_lapelas_vermelhas_mod.png` (c3 r3) | Outro corte:<br>• lapelas brancas recortadas em curva;<br>• **abas longas com viradas vermelhas**;<br>• **dragonas** vermelhas, vermelho-douradas e douradas (companhias de elite).<br>Pelo corte, provavelmente a casaca de antes de 1812 🔶 |
| M4 | `ref_fr_04_casaca_ligeira_mod.png` (c0 r2) | Casaca azul com lapelas pontudas e debrum branco: **infantaria ligeira** 🔶 |
| M5 | `ref_fr_05_barretinas_folha_mod.png` (linhas 4–5) | Barretinas:<br>• placa **losango com águia** (c3 r4) e placa **águia sobre semicírculo** (c4 r5);<br>• cocar tricolor;<br>• pompons verde, amarelo, azul, vermelho e branco;<br>• jugulares de escamas de latão;<br>• divisas laterais em V brancas, amarelas e vermelhas;<br>• cordões |
| M6 | `ref_fr_06_casacas_folha_mod.png` (linhas 0–3) | Os outros blocos:<br>• casacas verdes com lapelas brancas e galões amarelos (❓ unidade);<br>• capotes bege e cinza;<br>• calças brancas com polainas pretas abotoadas (c4 r1);<br>• mochila de pele, cantil, divisas de sargento |

Os atlas `FranceINF_2` e `FranceINF_3` (folhas em `work/ntw/france/folha_f2_*`, `folha_f3_*`) trazem mais variantes. Em `FranceINF_3` há casacas **vermelhas e amarelas** (regimentos estrangeiros 🔶). Elas serão catalogadas na fase de variantes, como foi feito na Prússia.

## 4. Componentes, cores e materiais (protótipo = M1)

Cores médias medidas em M1 (sRGB). A textura do mod é escura e tem sombra embutida; além disso, o mod usa máscara de cor (`_colour_mask`). A cor final do albedo é calibrada na Fase 6.

| Componente | Descrição | Cor no mod | Confiança |
|---|---|---|---|
| Casaca: corpo e mangas | Azul imperial, muito escuro na textura | #1A1D25 | 🎮 |
| Lapelas | Brancas, debrum vermelho, 7 botões cada, fechadas até a cintura | #A2A3A1 | 🎮 |
| Gola | Vermelha, com debrum branco | #682326 | 🎮 |
| Punhos | Vermelhos, com debrum branco e pala de 3 botões | #5E1716 | 🎮; a cor da pala ❓ (tecido de M1 pouco legível) |
| Abas | **Curtas**, com viradas brancas e enfeites | Viradas #8E8C8B | 🎮 (comprimento ❓, F3) |
| Bolsos das abas | Verticais, debrum vermelho, 3 botões | — | 🎮 |
| Platinas | Azuis, debrum vermelho | — | 🎮 |
| Botões | Latão (bronze escuro na textura) | #543E20 | 🎮 |
| Colete | Branco, visível sob as lapelas? | — | ❓ (as lapelas fechadas cobrem o peito) |
| Calças | **Brancas** (M6, c4 r1), com fileira de botões | — | 🎮 (cor de campanha ❓, F2) |
| Polainas | Pretas, abotoadas, até abaixo do joelho | — | 🎮 (altura ❓) |
| Sapatos | Pretos, baixos | — | 🔶 |

## 5. Barretina (item separado, protótipo próprio depois da casaca)

| Item | No mod (M5) | Confiança |
|---|---|---|
| Corpo | Feltro preto, com faixa de couro no topo e no pé | 🎮 |
| Placa | Losango de latão com águia (c3 r4) **ou** águia sobre semicírculo (c4 r5) | 🎮 (F4) |
| Cocar | Tricolor, acima da placa | 🎮 |
| Pompom | Cor por companhia/batalhão (verde, amarelo, azul, vermelho e branco no atlas) | 🎮; sistema de cores 🔶 |
| Jugulares | Escamas de latão com rosetas | 🎮 |
| Divisas laterais em V | Brancas, amarelas ou vermelhas (elite) | 🎮 |

A barretina prussiana já aprovada serve de base técnica: mesmos LODs, mesmo osso `Head`, mesmo gerador de texturas com parâmetros. A forma e as proporções são novas; sem vista lateral no mod, a altura e o alargamento ficam 🔶.

## 6. Correame e mochila (protótipo próprio depois)

| Item | Francês | Prussiano (feito) |
|---|---|---|
| Boldriés | **Dois, cruzados no peito**: um da cartucheira (ombro esquerdo → quadril direito) e um do sabre-briquet e da baioneta (ombro direito → quadril esquerdo) 🔶 | Cinturão + uma bandoleira |
| Cartucheira | Preta, com N coroado ou águia (🎮 M1, M3) | Preta |
| Mochila | Pele de bezerro com capote enrolado 🔶 (bloco de pele em M6) | Mesma ideia |

## 7. Medidas

Mesmo corpo oficial e mesmas medidas da ficha prussiana §6. Proporções propostas para o blockout:

| Medida | Proposta | Observação |
|---|---|---|
| Folga da casaca | Igual à prussiana (10–15 mm no tronco) | Já validada no teste de movimentos |
| Lapelas | Do pescoço à cintura (~1,12 m), largura ~0,08 m cada | 🔶 lido em M1 |
| Barra das abas | **~0,95–1,00 m** (abas curtas, no alto da coxa) | F3; mais curtas que as prussianas (0,70 m) |
| Gola | ~0,055 m, com a mesma abertura da gola prussiana corrigida | Usar já a lição da gola (garganta da cabeça do jogo) |
| Topo das polainas | Logo abaixo do joelho (~0,42 m), como na Prússia | 🎮 M6 |

## 8. Requisitos do ARMA 3

São os mesmos da ficha prussiana §8 (verificados nos Samples):
- LODs do template;
- seleções `camo` e `hl` e os ossos de `OFP2_ManSkeleton`;
- no máximo 4 ossos por ponto;
- `class <p3d>: ArmaMan {}` no `model.cfg`;
- soldado com `scope = 1` e sem facção.

Orçamento: ≤ 12.000 triângulos na Resolução 1, como na Prússia.

## 9. Riscos

| Risco | Mitigação |
|---|---|
| Lapelas sobre o peito atravessando o correame cruzado | Lapelas com relevo baixo; correame feito sobre a casaca, com o teste de 0 vértices sob o uniforme |
| Abas curtas com viradas: menos tecido, mas a junção com a cintura aparece mais | Mesma regra de camadas da Prússia (pesos v2) |
| Dois boldriés cruzados no peito × correias da mochila | Mesmas regras de pesos do equipamento prussiano |
| Cores do mod tingidas por máscara | Calibrar o albedo pela máscara na Fase 6 (como foi feito na Prússia) |

## 10. Decisões pedidas ao usuário

| # | Pergunta | Recomendação |
|---|---|---|
| F1 | Protótipo francês = **fuzileiro de linha, casaca de 1812 de abas curtas** (M1)? | **Sim**. A casaca de abas longas (M3) e a ligeira (M4) viram variantes de corte depois |
| F2 | Calças **brancas** (como no mod) ou de campanha (cinza/castanho) | **Brancas**; as de campanha viram variante de cor |
| F3 | Comprimento das abas | **Curtas, ~0,95 m**, como em M1 |
| F4 | Placa da barretina: losango com águia (c3 r4) ou águia sobre semicírculo (c4 r5) | **As duas**, como variantes (o gerador já trabalha por parâmetro). Protótipo com a águia sobre semicírculo |
| F5 | Ordem das próximas nações (inventário §2): França → Grã-Bretanha → Rússia → Áustria → Confederação do Reno → demais | **Como proposto** |
| F6 | Companhias de elite (granadeiros, voltigeurs: dragonas, pompons, divisas) | **Respondida em 2026-10-12**: o usuário pediu as barretinas de granadeiros e voltigeurs "iguais às daquela época" já agora. Ficha `docs/specs/barretina_francesa_1812.md` e esboço `docs/reports/barretina_fr_blockout.md`. As dragonas da casaca entram nas variantes da casaca |
| F7 | A autorização declarada (U7) cobre também os pacotes **LME4** (`france*`, `imperial_guardsb`)? | Você informa. Até lá uso só os atlas Reto (`FranceINF*`) como referência |
| F8 | Nomes de regimento | Técnicos, até haver nomes do mod (como na Prússia) |

**Próximo passo depois da aprovação:** Fase 3, o blockout da casaca francesa sobre o corpo oficial, reaproveitando `blockout_uniforme_pruss.py` e `build_uniforme_production.py` com os parâmetros da França.

---

## 11. Mais regimentos e versão de inverno (adendo de 2026-10-12)

Pedidos do usuário:
- *"adiciona mais regimentos a franca e as versoes de inverno dos uniformes"*;
- *"traz mais realismo a pumlet e as barretinas como se fossem na quela epoca"*.

### 11.1 Casacas de 1812 no mesmo corte (catálogo dos atlas)

Lidas em recortes de 512 px dos atlas. Recortes em `work/ntw/france/tiles/`, grades `grade_a…d.png`; cores medidas com amostrador de 11 × 11 px.

| Variante | Atlas | Casaca | Lapelas | Gola | Punhos | Viradas | Confiança |
|---|---|---|---|---|---|---|---|
| F01 (já feita) | `FranceINF` c4 r2, c5 r0, c5 r2 | azul | brancas, debrum vermelho | vermelha, debrum branco | vermelhos | brancas | 🎮 |
| **F02** | `FranceINF_2` c5 r0 | azul | **pretas**, debrum vermelho | preta, debrum vermelho | pretos, debrum vermelho | vermelhas | 🎮; unidade ❓ |
| **F03** | `FranceINF_3` c4 r0 | **amarela** | vermelhas, debrum branco | vermelha | vermelhos | vermelhas | 🎮; unidade ❓ (regimento estrangeiro 🔶) |
| **F04** | `FranceINF_3` c5 r0, c5 r1, c6 r1 | **vermelha** | amarelas, debrum branco | amarela | amarelos | amarelas | 🎮; unidade ❓ (regimento estrangeiro 🔶) |

Platinas de F03 e F04 (cor da casaca com borda da cor da lapela): 🔶, porque não dá para ler no atlas.

**Também nos atlas, mas fora deste corte (não feitos):**

| Atlas | O que mostra | Por que não foi feito |
|---|---|---|
| `FranceINF` c4 r0, c1 r1, c6 r1 | Casaca verde, lapelas brancas, gola e punhos vermelhos, galões dourados | Unidade ❓ e outro desenho de UV |
| `FranceINF` c3 r3, c4 r3, c7 r3; `FranceINF_2` c0 r1, c1 r1; `FranceINF_3` c0 r1, c1 r1 | Corte anterior a 1812 (M3): abas longas, lapelas recortadas | Pede malha de abas longas |
| `FranceINF` c0 r2 | Infantaria ligeira (M4) | Pede outro corte |

**Companhias de elite** (`FranceINF` c0 r3 granadeiro, c2 r3 voltigeur):
- granadeiro: dragonas vermelhas e granadas nas viradas;
- voltigeur: gola amarela (camurça) com debrum vermelho, dragonas verdes com meia-lua amarela, cornetas nas viradas.

As dragonas pedem peças novas na malha (decisão F12).

### 11.2 Inverno: capote

Referência: `FranceINF` c0 r1 (bege) e c3 r1 (cinza), e `FranceINF_3` c3 r1 (cinza).

O capote é:
- longo, de duas fileiras de 7 botões de latão;
- com gola e punhos do mesmo pano;
- com meia-cinta atrás (2 + 2 botões).

O mesmo bloco traz dragonas vermelha, verde e branca e os distintivos de granada e de corneta (elite sobre o capote).

| Variante | Capote | Calça | Confiança |
|---|---|---|---|
| W01 | bege | branca, polainas pretas | capote e calça 🎮; a combinação é proposta 🔶 |
| W02 | cinza | branca | idem |
| W03 | bege | azul de campanha (`FranceINF` c7 r1) | idem |
| W04 | cinza | cinza de campanha (`FranceINF` c7 r1) | idem |

**Medidas propostas** (🔶): barra a 0,46 m, logo acima das polainas; abertura da frente, esquerda sobre direita; fileiras com 10 cm de afastamento na cintura e 15 cm no peito.

Os atlas prussianos `prussia1813` **não têm capote**, só o rolo cinza da mochila (decisão F13).

### 11.3 Decisões pedidas ao usuário

| # | Pergunta | Recomendação (usada até a resposta) |
|---|---|---|
| F9 | Variantes F02–F04 pelas cores do atlas, com nomes técnicos | Sim (feitas) |
| F10 | Capote: barra a 0,46 m, 2 × 7 botões, esquerda sobre direita | Sim (feito) |
| F11 | Combinações capote × calça W01–W04 | As quatro (feitas) |
| F12 | Casacas de granadeiro e de voltigeur com dragonas (malha nova) | Sim, depois da resposta |
| F13 | Capote prussiano: cinza como o rolo da mochila 🎮; corte e gola 🔶 (não há tile) | Fazer com a mesma malha do capote francês, uma fileira de botões, gola na cor do regimento 🔶. Aguarda sua confirmação |
| F14 | Corte de abas longas anterior a 1812 (M3) | Depois, se você quiser |
