# Ficha Técnica: Aliados da França, c. 1812–1815 (Fase 1 + Fase 2)

Versão 0.1, 2026-10-13. Pedido do usuário: *"agora adiciona os aliados franceses"*, com 4 grupos:
1. Ducado de Varsóvia (infantaria polonesa);
2. Confederação do Reno (Baviera, Saxônia, Vestfália, Württemberg, Baden, Hesse-Darmstadt…);
3. Reino da Itália e Reino de Nápoles;
4. Suíços a serviço da França (os 4 regimentos de casaca vermelha).

**Estado (2026-10-18):** decisões A1–A6 fechadas (§8). **Suíços feitos** (`hcl_suica.pbo`, verificado fora do jogo, `docs/reports/suica_1812.md`). **Varsóvia feita** (`hcl_varsovia.pbo`, verificado fora do jogo, `docs/reports/varsovia_1810.md`; mais regimentos em 2026-10-18). **Itália e Nápoles feitos** (`hcl_italia.pbo`, primeiro lote de §3.3, verificado fora do jogo, `docs/reports/italia_1812.md`). Próximo: Reno.

Legenda: ✅ fonte lida (página aberta nesta fase) · 🔶 provável (fonte secundária, de hobby ou de loja; ou só citada, sem leitura) · ❓ incerto ou com fontes em conflito · 🎮 só visto na arte do mod (atlas Reto)

Regra de nomes (igual a `nomes_en.py`): nome de regimento **só** quando uma fonte citada bate com as cores lidas no atlas. O resto fica com nome técnico em inglês ("regiment unidentified").

---

## 0. Arte do mod disponível (Fase 1)

Pacote `(N)_Reto_BattleMOV11-15\variantmodels\units\atlas` (autorizado). Só os `_diffuse.dds` foram lidos. Conversão para PNG feita com `source/scripts/dds_para_png_aliados.py` (cópia do conversor do Reino Unido). Folhas de contato rotuladas com `folha_contato_atlas.ps1`.

| Grupo | Atlas de infantaria | PNG e folhas (pasta principal) |
|---|---|---|
| Varsóvia | `polandINF` | `work/ntw/varsovia/` |
| Reno | `saxonINF1812`, `saxonINF1812b`, `BavariaINF`, `WestphaliaINF`, `WurtembergINF_2` | `work/ntw/reno/` |
| Itália e Nápoles | `ItalyINF`, `NaplesINF` | `work/ntw/italia/` |
| Suíços | Nenhum atlas próprio. Estão dentro de `FranceINF_3` (c5 r0, c5 r1, c6 r1 = casaca vermelha, lapelas amarelas: já é a **F04 "1st Swiss Regiment"** do `hcl_fr`) | `work/ntw/france/` |

- **Baden e Hesse-Darmstadt: não há atlas** nos pacotes Reto. Só haveria arte no LME4, que **não tem autorização confirmada** (F7). Por isso ficam fora do primeiro lote, a menos que o usuário decida fazer só com fontes, sem arte do mod.
- Cavalaria, artilharia e generais (`PolandCAV`, `PolandART`, `ItalyCAV`, `NaplesCAV`, `NaplesGEN`, `BavariaCAV`, `BavariaGEN`, `saxonCAV1812`, `WestphaliaCAV`, `WestphaliaLighCAV`, `WurtembergCAV_2`, `WurtembergLighCAV`) existem, mas ficam fora do escopo (o mod só tem infantaria a pé).
- **Os atlas não trazem nome de unidade.** A leitura abaixo é pela folha de contato (256 px por bloco). O recorte ampliado de cada bloco escolhido (botões, vivos, números) é feito antes de pintar, como foi na França.
- Muitos blocos repetem peças genéricas da França: barretina com placa losango ou águia, divisas, pompons, cocar tricolor (Itália, Nápoles, Vestfália, Saxônia c3–c7 r4–r5). O cocar desses blocos é o **tricolor francês** 🎮, o que não está certo para todos os aliados (ver cada grupo).

---

## 1. Ducado de Varsóvia — infantaria de linha

### 1.1 Fontes

| Item | Valor | Confiança |
|---|---|---|
| Regulamento | Regulamento de uniformes de **3 de setembro de 1810**. Ele **não padronizou** de fato: vários regimentos diferiam bastante | ✅ [WP-PL1], [WP-PL9] (citam Gembarzewski e Askenazy) |
| Casaca | Azul-escura (granatowy) com lapelas brancas | ✅ [WP-PL9] (1807: lapelas e botões brancos, gola vermelha) |
| 9º Regimento (depois de 1810) | Gola carmesim com vivo azul-escuro, lapelas brancas, canhões carmesim com vivo branco, portinholas azul-escuras, botões brancos | ✅ [WP-PL9] (Askenazy e Gembarzewski 2003) |
| 7º Regimento | Mesmo corte do 4º; gola azul-escura com vivo carmesim, platinas carmesim e azul, botões brancos | ✅ [WP-PL] (resumo da busca, página do 7º) 🔶 |
| 1º Regimento | Fuzileiros com dragonas de lã branca com franja | ✅ [WP-PL1] |
| Cobertura (antes de 1810) | Em disputa: czapka × barretina. O regulamento de março de 1807 previa barretina; há relatos de czapka em 1807–1809 | ❓ [F-PEN] (fórum) |
| Granadeiros do 6º | Barretina de pelo sem pala, sem placa nem granada; cordões vermelho-claros | ✅ [WP-PL] (página do 6º) 🔶 |

**Fontes documentais (pedido do usuário de 2026-10-18: "utilize fontes históricas de museus e documentos").** O regulamento *Przepis ubiorów* de **3 de setembro de 1810** (texto publicado por Gembarzewski 1905, pp. 48–49 e 106–109, a partir dos documentos da época) e o resumo de Żygulski (jun.) e Wielecki, *Polski mundur wojskowy* (Kraków 1988), pp. 57–62:

| Item (regulamento de 1810) | Valor | Fonte |
|---|---|---|
| Kurtka | **Azul-marinho** (granatowa), **lapelas brancas** abotoadas dos dois lados, **gola, canhões e vivos carmesim** (*karmazynowe*); viras (*poły*); portinhola do punho | 📜 [REG1810] via [WP-MUN] e [NOP-1810] |
| Voltigeurs | **Gola amarela** | 📜 idem |
| Botões | Metal amarelo, **com o número do regimento** | 📜 [NOP-1810] |
| Platinas / dragonas | Fuzileiros: patkas azul-marinho; granadeiros: dragonas **carmesim**; voltigeurs: **verdes** (cordão de fio verde) | 📜 [WP-MUN] (Żygulski p. 58) |
| Calça e polainas | Verão: calça de linho branca; outono–inverno: calça azul-marinho e polainas de pano escuro | 📜 [WP-MUN], [NOP-1810] |
| **Cobertura: czapka rogata** (fuzileiros e voltigeurs) | Feltro preto, papelão e linho, **~22,5 cm de altura, lados do topo ~25 cm**; pala de couro debruada de metal amarelo; **águia de metal branco sobre placa amarela com o número do regimento**; botão de metal amarelo com estrela (fuzileiro) ou corneta (voltigeur); **cocar branco**; **cordões brancos**; **pompom preto** (fuzileiros) ou **penacho amarelo-verde** (voltigeurs) | 📜 [WP-MUN] (Żygulski pp. 60–61), [NOP-1810] |
| Granadeiros: barretina de pelo (*bermyca*) | Placa amarela com o **número do regimento, águia branca e duas granadas** dos lados; **plumet carmesim**; cordões brancos; **topo redondo de pano carmesim** | 📜 idem |
| Peça de museu | Barretina (czako) do **2º Regimento** no **Museu Nacional de Cracóvia** (MNK); catálogo da exposição *Militaria Księstwa Warszawskiego* (MNK 1959) | 🏛 [NOP-1810] (citada; ficha do objeto **não encontrada** online) |
| Iconografia da época | Aquarela de **Józef Kosiński, 1810**, base das pranchas do napoleon.org.pl | 🖼 [NOP-1810] (não vista) |

Legenda nova: 📜 documento da época (regulamento) lido por meio de historiador que o publicou · 🏛 objeto de museu · 🖼 imagem da época.

### 1.2 Arte do mod (`polandINF`) 🎮

| Bloco | O que mostra |
|---|---|
| c0, c1, c2, c4, c5 r0 | Casaca azul-escura, mesmo molde. Peças da cor distintiva: vermelho (c0), amarelo (c1), azul-claro (c2), branco (c4), amarelo (c5). Dragonas e pompons coloridos ao lado |
| c0 r2, c0 r3, c1 r3 | Casaca azul com lapelas **vermelhas** (r2, r3) e **amarelas** (c1 r3), molde de casaca com lapelas |
| c0 r1, c1 r2, c2 r2 | Casacas azuis com lapelas vermelhas e galões; c2 r2 tem lapela branca/vermelha (provável guarda ou oficial ❓) |
| c4 r1, c5 r1, c4 r2 | Calças azuis com listra vermelha; polainas |
| c3 r0 | Calça vermelha com listra branca (cavalaria? ❓; fora) |
| c0–c5 r5 | **Peças de barretina polonesa**: placa de **sol raiado com águia**, placa de cruz, cordões; cintas azul, verde e preta; galões amarelos |
| c6 r5 | Topo vermelho com placa amarela e "N" (sapador ou guarda ❓) |
| c3–c5 r4 | Plumet e penacho branco; c6 r4 pompom de pelo branco |

### 1.3 Proposta de peças

Revisão de 2026-10-18, pelas fontes documentais (substitui a proposta da v0.1):
- **Casaca:** a de abas curtas francesa como base do corte 🔶. As cores seguem o **regulamento de 1810** 📜: azul-marinho, lapelas brancas, gola, canhões e vivos carmesim, e gola amarela nos voltigeurs. O bloco `polandINF` c4 r0 (lapelas brancas) é o único do atlas que bate com o regulamento 🎮. Os blocos com lapelas vermelhas, amarelas e azul-claras não têm documento e **ficam fora**.
- **Variantes com documento:** além do padrão de 1810, o **9º Regimento** (gola carmesim com vivo azul, lapelas brancas, botões brancos) e o **7º** (gola azul-marinho com vivo carmesim, botões brancos), segundo Askenazy e Gembarzewski [WP-PL9], [WP-PL].
- **Cobertura (A5, revista):** a **czapka rogata** do regulamento 📜, peça nova (`blockout_czapka_varsovia.py`). Granadeiros: chapéu de pele com placa de águia e granadas (cópia do da Guarda, como no suíço).
- **Infantaria ligeira:** o Ducado não tinha regimentos ligeiros; os voltigeurs são as companhias ligeiras de cada regimento.
- **Nomes:** "Duchy of Warsaw, Line Infantry (1810 regulation)"; 7th e 9th com o nome do regimento.

---

## 2. Confederação do Reno

### 2.0 Inventário pelas pranchas de época (2026-10-19, pedido do usuário: "adicionar TODOS estes regimentos")

Fonte comum: aquarelas e gravuras da **coleção Vinkhuijzen (NYPL)**, vistas pelo Commons [VK-REN]. Os números entre parênteses são o índice da prancha nas folhas de contato da sessão (`scratchpad/fontes_reno/<estado>_thumbs/indice.txt`, com o ID NYPL de cada prancha). Regras de leitura:
- a **legenda é do colecionador** (escrita à mão em alemão), não da imagem → o nome do regimento vem da legenda, 🔶;
- a **cor** é lida da aquarela (tons de aguada) → 🔶;
- quando a prancha contradiz a tabela de 1813 [MD-W], vale a prancha da data certa (1810–1812), e o conflito fica anotado.

Ficam fora deste lote: cavalaria, artilharia, trem, generais e oficiais de estado-maior (a mesma regra da Itália: não há malha de cavalo, bicorne nem sobrecasaca).

#### Württemberg — álbum "1811" (aquarelas; todas com Raupenhelm de latão e crista preta)

| Prancha | Legenda (transcrição) | Casaca / peças | Cabeça |
|---|---|---|---|
| 022 (b14896507-1525642) | "1. Regiment Linie Prinz Paul" | azul-escura, gola, canhões e vivos **amarelos** | Raupenhelm |
| 020 (-1525640) | "2. Linie Regiment Herzog Wilhelm" | azul-escura, **laranja** | Raupenhelm |
| 021 (-1525641) | "3. Linie Regiment Infanterie" | azul-escura, **branco** (gola clara) | Raupenhelm |
| 019 (-1525639) | "Linie Infanterie Regiment No 4" | azul-escura, **rosa** | Raupenhelm |
| 018 (-1525638) | "Lin. Regiment No 5 Prinz Friedrich, Grenadier" | azul-escura, **azul-claro** | **barretina de pele** (granadeiro) |
| 017 (-1525637) | "Linie Infanterie Regiment No 6 Kronprinz" | azul-escura, gola vermelha, canhões **brancos com vivo vermelho** | Raupenhelm |
| 016, 015 (-1525636/35) | "Linie Regiment Infanterie No 8 Neubronn, Officier" / "No 8 Grenadier Leutnant" | azul-escura, **vermelho** | Raupenhelm (016), pele (015) |
| 014 (-1525634) | "Linie Infanterie Regiment No 9" | azul-escura, **vermelho** | Raupenhelm |
| 012 (-1525632) | "Leichte Infanterie Reg. No 10" | **verde-escura, peças pretas**, vivo vermelho | barretina, pluma vermelha |
| 013 (-1525633) | "Regiment Leichte Infanterie No 10" | verde-escura, peças **azul-claras** | barretina, pluma vermelha |
| 011 (-1525631) | "Erstes Bataillon Jäger König" | verde-escura, peças pretas | barretina, pluma verde |

Conflitos: o 9º aparece **vermelho** em 1811, mas preto/amarelo na lista de 1813 [MD-W]. Vale a prancha de 1811 🔶. As duas pranchas da ligeira dizem "No 10", com cores diferentes (preto e azul-claro). Uma das legendas deve estar errada, e por isso as duas entram com o nome da legenda e a cor no nome. O 7º não tem prancha em 1811: entra pela lista [MD-W] (vermelho, botão amarelo) 🔶. O álbum "1813–1814" já mostra a barretina de 1813, que fica para outro lote.

#### Baviera — álbum "1811" (aquarelas; casaca azul-clara, Raupenhelm com crista de pele)

| Prancha | Legenda | Gola / lapelas |
|---|---|---|
| 003 | "Infanterie Regiment König No 1" | **vermelho** / vermelho |
| 005 | "Infanterie Regiment Kronprinz No 2" | vermelho / vermelho, **com alamares amarelos** |
| 006 | "Infanterie Regiment Sachsen-Hildburghausen No 4" (oficial) | **amarelo** / amarelo |
| 015 | "Infanterie Regiment Herzog Wilhelm No 6" (oficial) | vermelho / vermelho |
| 014 | "Infanterie Regiment Löwenstein No 7" | **rosa-carmim** / rosa-carmim |
| 013 | "Infanterie Regiment Herzog Pius No 8" | amarelo / amarelo |
| 012 | "Infanterie Regiment Ysenburg No 9" | vermelho / **amarelo** |
| 011 | "Infanterie Regiment Junker No 10" | vermelho / **amarelo** (como o 9º; a diferença deve ser o botão ❓) |
| 010 | "Infanterie Regiment Kinkel No 11" | três figuras: lapelas **laranja**, **verdes** e **pretas**, gola vermelha. Pela legenda, só uma é do 11º ❓ |
| 009 | "Infanterie Regiment No 13" | vermelho / **preto** com vivo vermelho |
| 008 | "Infanterie Regiment No 14, Tambour" | tambor; só o corte |
| 007 | "Leichte Infanterie Bataillon No 1 Gedoni (Carabinier)" | **verde**, lapelas pretas, gola **vermelha**, calça cinza |
| 019 | "Leichte Infanterie Bataillon No 2 Wreden" | verde, lapelas pretas, gola **vermelha** |
| 018 | "Leichte Infanterie Bataillon No 3 Bernclau" | verde, lapelas pretas, gola **clara** (amarelo-pálido? ❓) |
| 017 | "Leichte Infanterie Bataillon No 4 Theobald" | verde, lapelas pretas, gola **preta** com vivo vermelho |
| 016 | "Leichte Infanterie Bataillon No 5 Butler" | verde, lapelas pretas, gola **amarela** |
| 021 | "Leichte Infanterie Bataillon No 6 La Roche" | verde, lapelas pretas, gola **amarela** |
| 020 | "Leichte Infanterie Bataillon No 7 Günther" | verde, lapelas pretas, gola **azul-clara** |

O 3º, o 5º e o 12º de linha não têm prancha no álbum. Ficam fora até haver fonte.

#### Saxônia — álbum "1810" (aquarelas; reforma de 1810: casaca branca, barretina)

| Prancha | Legenda | Peças (gola, lapelas, canhões) |
|---|---|---|
| 036 | "Linie Infanterie Regiment König" | **vermelho** |
| 010 | "Linie Infanterie Regiment Niesemeuschel" | **vermelho** |
| 007 | "Linie Infanterie Regiment Prinz Anton" | **azul-claro** |
| 043 | "Infanterie Regiment von Löw" | **azul** (médio) |
| 035 | "Infanterie Regiment Prinz Max" | **amarelo** |
| 008 | "Linie Infanterie Regiment Rechten" | **amarelo** |
| 044 | "Infanterie Regiment Prinz Friedrich August" | **verde-escuro** |
| 005 | "Linie Infanterie Regiment Prinz Clemens" | **verde-claro** |
| 006 | "Grenadier ... Prinz Clemens" | granadeiro com as peças verdes, dragonas vermelhas, pluma vermelha |
| 037, 038 | "Garde Grenadier" | casaca **vermelha**, peças **amarelas**, barretina de pele |
| 020 | "Leichte Infanterie" | **verde**, peças pretas, vivo vermelho |
| 019 | "Jaeger" | verde, peças pretas, calça cinza |

Os oito regimentos de linha da reforma de 1810 estão todos. Pares com a mesma cor (König/Niesemeuschel, Max/Rechten) se distinguem pelo botão, que a aquarela não mostra ❓.

Barretina (lote 2, 2026-10-27), lida nas pranchas em alta resolução (005, 006) e nas miniaturas (036, 019, 020):

| Peça | Valor | Fonte |
|---|---|---|
| Corpo | Feltro preto, pala, jugulares de escamas; sem divisas laterais nas aquarelas | 🖼 [VK-REN] 005, 006, 036 |
| Placa | Escudo de latão sob coroa com a cifra "FA" (Friedrich August) | 🎮 arte do mod `saxonINF1812` c3 r4, traçada em `placa_saxonia.json` |
| Cocar | Branco | 🎮 idem (disco branco plissado) |
| Linha | Cordões **brancos**; pompom pequeno: branco (005) ou branco com topo vermelho (036, König) | 🖼 🔶 |
| Granadeiro | Pluma **vermelha** alta, cordões e borlas **vermelhos** | 🖼 006 |
| Ligeira | Cordões **verdes**, tufo pequeno vermelho e verde (no modelo, pompom verde 🔶); calça cinza | 🖼 020 (miniatura) |
| Jäger | Pluma **preta** alta, cordões verdes; calça cinza | 🖼 019 (miniatura) |

A Guarda (037/038, barretina de pele) e o granadeiro com casaca de dragonas (006) precisam da casaca de elite e ficam para depois.

#### Vestfália — álbuns "1809" e "1810–1815" (gravuras em fila + aquarelas)

| Prancha | Legenda | Casaca / peças |
|---|---|---|
| 060, 062 | "Linien Infanterie" / "Grenadier ... tenue de campagne" | branca, lapelas e gola **azul-escuras** |
| 005 | "Linie Grenadier" | branca, lapelas **azul-claras**, pluma vermelha |
| 006 | "Linie Voltigeur" | branca, lapelas **azul-claras**, pluma verde-amarela |
| 003 | "5. Linie Regiment, Grenadier" | branca, lapelas **laranja** |
| 004 | "5. Linie Regiment, Voltigeur" | branca, lapelas **laranja** |
| 058 | "Voltigeur 7me R. d'Inf. d. L." | branca, gola **amarela**, dragonas verdes |
| 092 | "Sergeant ... Linie Infanterie 1812" | branca, peças azul-escuras |
| 008 | "Garde Grenadier" | Guarda; casaca branca de peças vermelhas, barretina de pele |
| 007 | "Garde Jäger" | verde-escura |
| 009 | "Leichte Infanterie" | verde-escura, calça com faixa amarela |

### 2.1 Württemberg — o grupo com melhor fonte de cores

| Item | Valor | Confiança |
|---|---|---|
| Capacete | Capacete de couro com crista (**Raupenhelm**), desde o fim de 1806, até a barretina de **1813** | 🔶 [PSR-W] (resenha de figuras) |
| Raupenhelm | "Preto, com placa de latão" | 🔶 [MD-W] |
| Casaca | Azul-escura; 5º Regimento: gola, canhões, viras e platinas azul-claro | 🔶 [MD-W] |
| Cores por regimento (lista de **1813**) | 1º amarelo / botão branco · 2º laranja / branco · 3º branco / branco · 4º rosa / branco · 5º azul-claro / branco · 6º branco com vivo vermelho / amarelo · 7º vermelho / amarelo · 8º palha / amarelo · 9º preto / amarelo · Fuzileiros von Neubronn vermelho | 🔶 [MD-W] citando **Knötel-Sieg, *Handbuch der Uniformkunde* pp. 78–79** e **Haythornthwaite, *Uniforms of 1812*, prancha 33** (livros não lidos) |
| Equipamento | Correame francês de dois boldriés, desde 1811–1812 | 🔶 [PSR-W] |

Arte do mod (`WurtembergINF_2`) 🎮:

| Bloco | O que mostra |
|---|---|
| c0–c3 r1 e r2 | Casaca azul-escura, viras e canhões em **vermelho (c0), amarelo (c1), rosa (c2), branco com vermelho (c3)**. r2 = as mesmas cores com pompom/emblema prateado (outra companhia ❓) |
| c4 r1 | Azul-escura com peças amarelo-alaranjadas e botões amarelos |
| c4 r2 | Azul-escura com peças vermelhas e botões amarelos |
| c5 r1, c5 r2 | Azul-escura com galões brancos no peito (guarda? ❓) |
| c6 r2, c7 r2 | Casaca **azul-clara** com galões (unidade ❓) |
| c4 r0, c5 r0 | Casaca **verde** com peças pretas (c4) e azul-claras (c5): Jäger ou infantaria ligeira ❓ |
| c3–c6 r4 | **Peças do Raupenhelm**: crista preta, placa de latão com coroa e monograma, escamas, cocar com centro vermelho |

**Cruzamento fonte × atlas (a conferir no recorte):** rosa + botão branco = 4º; vermelho + botão amarelo (c4 r2) = 7º; branco com vermelho = 6º se o botão for amarelo. É o único grupo do Reno em que dá para dar nomes 🔶. Ressalva: a lista é de 1813, depois da renumeração ❓.

### 2.2 Baviera

| Item | Valor | Confiança |
|---|---|---|
| Casaca | Azul-claro tradicional ("azul-centáurea" nas fontes inglesas; tom exato incerto) | ✅ [WP-BAV] (sem citação inline) 🔶 |
| Capacete | **Raupenhelm** para todas as armas desde **1801**, com crista de crina de proa a popa | ✅ [WP-BAV] 🔶 |
| Linha | Casaca azul média, viras vermelhas, calça branca, polainas pretas, lapela na cor do regimento, placa de latão | 🔶 [WTJ] (tabela de jogo) |
| Infantaria ligeira | Verde; calça cinza depois de 1811 | 🔶 [WTJ] |
| Cores por regimento | **Não encontradas** em fonte aberta. Referência a consultar: Osprey *Napoleon's German Allies (4): Bavaria* | ❓ |

Arte do mod (`BavariaINF`) 🎮:

| Bloco | O que mostra |
|---|---|
| c2 r0, c7 r0, c1–c7 r1, c0–c4 r2 | Casaca azul-clara, **lapelas vermelhas**; gola e canhões em **preto** (c2 r0, c2 r1, c3 r1), **amarelo** (c1 r1, c7 r1, c0 r2), **verde** (c1 r2, c2 r2), **rosa** (c3 r2, c4 r2), vermelho (c5 r1) |
| c5 r0, c6 r1 | Azul-clara com galões brancos nos canhões (guarda/Leib-Regiment? ❓) |
| c4 r0, c4 r1, c5 r2, c6 r2 | Casaca **verde** com lapelas vermelhas (infantaria ligeira ❓: a fonte diz verde) |
| c0 r3, c1 r3 | Casaca verde de outro corte, com cinto branco (❓) |
| c0 r0, c7 r5 | **Peças do Raupenhelm**: couro preto, crista, placa de latão com coroa, cocar branco e azul (losangos bávaros) |

### 2.3 Saxônia

| Item | Valor | Confiança |
|---|---|---|
| Reforma de 1810 | Casaca **branca**, lapelas retas na cor distintiva, forro com vivo; corte diferente do prussiano de 1806 | 🔶 [F-NO] (fórum Napoleon-Online) |
| Cores por regimento | Não encontradas em fonte aberta. Referência: Bunde, *The Saxon Army 1810–1813* (tabelas por regimento, não lido) | ❓ |

Arte do mod (`saxonINF1812`, `saxonINF1812b`) 🎮: casacas **brancas** com lapelas e canhões em vermelho, azul-escuro, verde, amarelo, azul e vermelho-escuro; casacas **verdes com peças pretas e vivo vermelho** (c0 r1, c0 r2: infantaria ligeira ❓); casaca vermelha com lapelas amarelas (`b` c4–c5 r3, ❓); barretina com **placa de monograma coroado** (c3 r4, c0 r5) e pompons. Cocar dos blocos de barretina genéricos = tricolor francês, errado para a Saxônia 🔶.

### 2.4 Vestfália

| Item | Valor | Confiança |
|---|---|---|
| Casaca | Branca de corte francês | 🔶 [F-TAP] (fórum) |
| Cor distintiva | **Conflito**: azul-escuro [F-TAP] × azul-claro com vivo azul-claro, lapelas brancas (4º de linha) [WM-4W] | ❓ |
| Placa | Não encontrada | ❓ |

Arte do mod (`WestphaliaINF`) 🎮: casaca **branca com peças azul-claras** (c0 r0, c0 r1, c0 r3, c3 r3); casaca branca com vermelho (c7 r2); casacas **verdes** (c0 r2, c1 r2: ligeira ou Jäger ❓); casaca azul com lapelas laranja (c5 r0, c2 r2 ❓); barretina genérica francesa.

### 2.5 Baden, Hesse-Darmstadt e outros

Sem atlas Reto (ver §0). Fora do primeiro lote, salvo decisão A3.

---

## 3. Reino da Itália e Reino de Nápoles

Pesquisa de 2026-10-18 (pedido: "utilize fontes históricas de museus e documentos"). As fontes de época encontradas são **imagens e um historiador quase contemporâneo**. Os decretos italianos de uniforme **não foram lidos**: o *Bollettino delle leggi* não foi achado em texto. Os de Nápoles só aparecem citados.

### 3.1 Itália — infantaria de linha

| Item | Valor | Fonte |
|---|---|---|
| Casaca | **Branca**, corte e distinções de companhia **franceses**, desde **1806** (antes, verde); colete, calça e correame brancos, polainas pretas | ✅ [WP-IT-ES] (cita Pivka & Chappell, Osprey MAA 43, p. 23); 🖼 [KN-III-25] (Knötel, *Uniformenkunde* III/25, 1812: "weisse Uniformen mit regimentweis verschiedenfarbigen Abzeichen … roth, grün und weiss") |
| Cocar | **Branco, verde e vermelho** (cocar nacional) | 📜 [ZANOLI] (Zanoli, *Sulla milizia cisalpino-italiana*, Milão 1845, p. 32 do volume digitalizado no Internet Archive, `bub_gb_SyVEAAAAYAAJ`; o autor serviu no exército italiano) |
| Barretina (fuzileiros) | Francesa, placa losango e escamas de latão, **cocar verde-vermelho(-branco)**, pompom pela companhia: **1ª verde, 2ª azul-celeste, 3ª laranja, 4ª violeta**; cordões brancos de gala | ✅ [WP-IT-ES] 🔶 (Osprey) |
| Granadeiros | **Barretina de pelo**, placa de latão com granada, plumet vermelho, cordões brancos, **dragonas vermelhas** | ✅ [WP-IT-ES] 🔶 |
| Voltigeurs | Plumet **verde com ponta amarela**, cordões verdes, **dragonas verdes com crescente amarelo** | ✅ [WP-IT-ES] 🔶 |
| Cores por regimento | 1º gola verde, lapelas e canhões vermelhos · 2º gola branca com vivo vermelho, lapelas vermelhas, canhões brancos · 3º tudo vermelho · 4º gola vermelha, lapelas e canhões brancos com vivo verde · 5º gola vermelha, lapelas e canhões verdes · 6º gola branca, lapelas verdes, canhões brancos · 7º gola verde, lapelas brancas, canhões vermelhos | 🔶 [MD-I] (Schultheis 1996, sem bibliografia) |
| **Confirmação por imagem de época** | Série de gravuras coloridas de **1812** (filas de soldados, estilo das folhas impressas alemãs da época) na **coleção Vinkhuijzen, New York Public Library**, legendadas à mão por regimento: **3º** lapelas e gola vermelhas (= "tudo vermelho"); **4º** lapelas brancas, gola vermelha; **5º** **lapelas verdes**, gola vermelha; **7º** lapelas brancas, gola escura (verde); **1º** lapelas vermelhas | 🖼🏛 [VK-IT] (NYPL b14896507-1528382…87). A legenda é do colecionador (fim do séc. XIX), não da gravura → 🔶. A resolução da digitalização (≈1000 px) não deixa ler canhões nem vivos |
| Casaca de 1812 | O *habit-veste* francês chegou só em **1813**; na Rússia usaram o modelo anterior (abas longas) | 🔶 [MD-I] |
| Iconografia ainda não vista | Água-tinta aquarelada **"L'Infanteria del Regno d'Italia"**, de **Albrecht Adam** (Artaria, Viena, dedicada ao ministro Fontanelli; Zanoli a cita), na **Bibliothèque Marmottan** | 🏛🖼 [NAP-ADAM] (ficha sem descrição das cores) |

Arte do mod (`ItalyINF`) 🎮: casaca **branca com lapelas vermelhas** (c1 r1), **branca com verde** (c5 r0, c6 r2), **verde com lapelas vermelhas** (c0 r1, c4 r2, c0 r3: ligeira? ❓), verde com amarelo (c0 r2 ❓), azul-clara com vermelho (c5 r2 ❓), azul (c2 r1 ❓). Barretina: losango e águia em latão e prata, pompons, divisas (c3–c7 r4–r5). O cocar dos blocos é o **tricolor francês**, mas a fonte diz verde-vermelho-branco 📜 → pintar o cocar italiano.

**Cruzamento:** branca com vermelho (c1 r1) bate com o **3º** (tudo vermelho) ou o **1º/2º**; branca com verde (c5 r0, c6 r2) bate com o **5º/6º**. O atlas dá o tom e o corte; a regra de nomes usa a tabela + a gravura.

### 3.2 Nápoles — infantaria de linha (Murat)

| Item | Valor | Fonte |
|---|---|---|
| Geral | Regulamentos sucessivos de Murat; as cores são difíceis de fixar ("Die Schwierigkeit Sicheres über die Uniformen dieser Armee zu erfahren, ist sehr gross", Knötel) | 🖼 [KN-V-46]; ✅ [WP-NAP] |
| Casaca | **Branca**, corte do *habit-veste* (lapelas fechadas, abas curtas) pelo **Decreto 821** (1810/1811) | 📜 citado por [GA-7NAP] (não lido) |
| **7º de Linha, 1812–13** | **Gola, lapelas, viras e canhões amarelos**, **botões de latão**; portinholas em ponta de 3 (as fontes divergem: amarela com vivo branco ou branca com vivo amarelo); calça branca (em Danzig, azul-escura) | 🖼 [FREIBERG] (*Freiberger Bilderhandschrift*, aquarelas feitas em 1813 na Saxônia) + Boisselier, Brauer, Forthoffer, Knötel, acervo de **San Martino (Nápoles)** e do **museu de Rastatt**, reunidos por [GA-7NAP] |
| Barretina | Feltro preto, **placa em coração** com "JN" ou o número; **sem cordões**; cocar **branco com centro amaranto**; pompom achatado na cor distintiva com centro branco (fuzileiros), amarelo (voltigeurs) | 🖼📜 [GA-7NAP] |
| Granadeiros | Barretina de pelo com **cordões e plumet vermelhos**, dragonas vermelhas, granadas vermelhas nas viras | 🖼 [GA-7NAP] |
| Voltigeurs | Dragonas, plumet e cordão do sabre **amarelos**; cornetas amarelas nas viras; placa com granada sobre corneta | 🖼 [GA-7NAP] |
| Cores de 1812, 1º a 6º | "scheinen folgende gewesen zu sein": **1 escarlate, 2 verde, 3 amarelo, 4 laranja, 5 azul, 6 carmesim** | 🔶 [KN-V-46] (Knötel, *Uniformenkunde* V/46, 1812; o próprio autor diz "parecem ter sido"). [KN-VI-23] mostra o **4º com amarelo** e o **5º com azul-claro** (músico) → 4º ❓ |
| Imagem de época (provável) | Gravura colorida **"Naples, Infanterie", 1813**: casaca branca, dragonas vermelhas, **calça azul** | 🖼🏛 [VK-NAP] (NYPL b14896507-1608397), autor e data de impressão ❓ |

Arte do mod (`NaplesINF`) 🎮: casaca **branca** com peças **azul-claras** (c5 r0, c1 r3), **verdes** (c1 r1, c3 r2), **vermelhas** (c5 r2, c4 r3), vivo azul (c2 r1); casaca **azul-escura com lapelas vermelhas e galões dourados** (c0 r1, c1 r2, c7 r2, c0 r3: guarda? ❓; âncora em c0 r2 → marinha? ❓); casaca vermelha com preto (c6 r2 ❓); casaca azul-clara com vermelho (c2 r3 ❓). Barretina: placa em escudo e losango (c3–c7 r4), plumets coloridos (c1 r4).

**Cruzamento:** verde (c1 r1, c3 r2) → **2º** 🔶; vermelho (c5 r2, c4 r3) → **1º** 🔶; azul-claro (c5 r0, c1 r3) → **5º** 🔶 (Knötel VI/23). O **7º amarelo** não tem bloco no atlas: casaca pintada só pela fonte.

### 3.3 Proposta do primeiro lote (`hcl_italia.pbo`, Itália + Nápoles juntos, decisão A2)

| Peça | Itália | Nápoles |
|---|---|---|
| Casaca (malha 1812 da França, como em Varsóvia) | Branca, **7 regimentos** pela tabela, com nome só para os confirmados pela gravura (3º, 4º, 5º, 7º) e os demais 🔶 no texto | Branca, **7º** (fonte de época) + **1º, 2º, 5º** (Knötel + atlas 🔶) |
| Elite | Granadeiro (dragonas vermelhas), voltigeur (verdes, crescente amarelo) | Granadeiro (vermelhas), voltigeur (amarelas) |
| Barretina | Cópia da barretina francesa v4, **placa losango**, **cocar verde-branco-vermelho**, pompons das 4 companhias + voltigeur | Cópia da v4 com **placa em coração** traçada do atlas (c3–c7 r4) 🎮, **sem cordões**, cocar **branco e amaranto** |
| Barretina de pelo | Cópia do chapéu de pele francês, placa de latão com granada, cordões brancos, plumet vermelho | Idem, cordões e plumet vermelhos |
| Fica para depois | Ligeira (verde) e casaca de 1813 | 3º, 4º, 6º (cores ❓) |

---

## 4. Suíços a serviço da França

| Item | Valor | Confiança |
|---|---|---|
| Organização em 1812 | Os 4 regimentos reunidos numa divisão para a Rússia, 3 batalhões cada | 🔶 [OSP-SW] (descrição do livro) |
| **1º Suíço**, regulamento de 1812 | Casaca vermelha, **gola amarela, lapelas amarelas fechadas** com vivo vermelho; portinholas com vivo branco; fuzileiros com platinas vermelhas de vivo amarelo; granadeiros com dragonas vermelhas e **barretina de pelo com placa de cobre e granada** | ✅ [WP-SW1] |
| 1º Suíço, 1809–1812 | Barretina preta com cordões brancos | ✅ [WP-SW1] |
| **3º Suíço** | Casaca vermelha, **gola, lapelas e canhões pretos, vivo branco**; barretina para fuzileiros, sargentos e voltigeurs, pelo para granadeiros | ✅ [WP-SW3] citando **Fieffé 1854**, p. 299 |
| **2º Suíço** | Vistas **azul-real** (*königsblau*) | 📜 Fieffé (ed. alemã 1860, II p. 183) via [WP-DE-SW] (lida em 2026-10-18; antes ❓) |
| **4º Suíço** | Vistas **azul-celeste** (*himmelblau*) | 📜 Fieffé via [WP-DE-SW] (antes: só lojas [LOJA-SW4]) |
| Os 4 regimentos | Casaca **vermelho-garança** (*krapprot*) igual para todos, calça branca justa; cor distintiva nas **platinas, portinholas e golas** | 📜 Fieffé via [WP-DE-SW] |
| Peça de museu | Casaca de capitão de voltigeurs do **1º Suíço**, de Abraham Rey (1778–1859), modificada em 1812 (posição dos botões); e a barretina dele, furada por bala em Polotsk (out. 1812) | 🏛 [MUS-MORGES] (Château de Morges; ficha não lida, a página recusou o certificado) |
| Referências | Greentree e Campbell, *Napoleon's Swiss Troops* (Osprey 2012); Jouineau, *Les suisses au service de la France* | 🔶 (não lidos) |

Arte do mod: só a casaca de lapelas **amarelas** (`FranceINF_3` c5 r0, c5 r1, c6 r1), já feita como **F04** no `hcl_fr`. O vivo do mod é branco; a fonte diz vermelho (nota já registrada em `nomes_en.py`). **Não há arte** para o 2º, 3º e 4º.

**Proposta:**
- 1º Suíço: copiar a F04 (casaca) e a barretina de fuzileiro para o addon dos suíços, sem depender do `hcl_fr`.
- 3º Suíço: recolorir a F04 (amarelo → preto, vivo branco) com `recolorir_textura.py` (cópia), porque há fonte.
- 2º e 4º: só se o usuário aceitar 🔶 (A6).
- Granadeiro suíço: a barretina de pelo da Velha Guarda serve de base, mas a placa é **de cobre com granada** (não a águia da Guarda) ✅ [WP-SW1].

---

## 5. Reaproveitamento (o mesmo pipeline da França)

| Peça | Base copiada | Grupos |
|---|---|---|
| Casaca de abas curtas com lapelas | `build_uniforme_fr.py` / `build_casaca_elite_fr.py` → cópias `_aliados` | Todos (aproximação 🔶 para Varsóvia, Baviera, Württemberg e Saxônia, cujos cortes diferem um pouco) |
| Barretina francesa v4 | `blockout_shako_fr.py` + `texturizar_shako_fr.py` → cópias | Varsóvia, Itália, Nápoles, Vestfália, Saxônia, Suíços |
| Plumet e pompons | `plumet.py` (só leitura, importado) ou cópia | Companhias de elite |
| Barretina de pelo | `blockout_bonnet_guarda.py` → cópia, placa nova | Granadeiros suíços (e italianos, se A4) |
| **Raupenhelm** (peça nova) | Novo script `blockout_raupenhelm.py`, arte traçada de `BavariaINF` c0 r0 / `WurtembergINF_2` c3–c6 r4 | Baviera e Württemberg |
| Czapka polonesa (peça nova, opcional) | Novo script | Varsóvia, só se A5 |
| P3D, config, PAA, build | `build_p3d_fr.py`, `gen_config_fr.py`, `convert_fr_paa.ps1`, `build_mod_fr.ps1` → cópias por grupo | Todos |
| Nomes em inglês | Módulo próprio `nomes_en_aliados.py` (não editar o `nomes_en.py` compartilhado) | Todos |

Saídas na pasta principal só em caminhos dos aliados: `source/models/*/hcl_*_<grupo>*`, `source/textures/hcl_*_<grupo>*`, `source/addon/hcl/hcl_<grupo>`, `release/@Historical_Clothing/Addons/hcl_<grupo>.pbo`.

---

## 6. Proposta de ordem e primeiro lote

| # | Grupo | Por quê | Primeiro lote proposto |
|---|---|---|---|
| 1 | **Suíços** | Mesmo corte e barretina da França; arte e fonte para o 1º; fonte para o 3º | 1º e 3º Suíço (fuzileiro), granadeiro com barretina de pelo e placa de granada |
| 2 | **Varsóvia** | Atlas completo com peças próprias (placa de sol e águia) | Linha, fuzileiros, nas 5 cores do atlas; nomes técnicos |
| 3 | **Itália e Nápoles** | Casaca branca francesa; tabela de cores 🔶 para a Itália | Itália: linha nas cores do atlas, cocar italiano; Nápoles: linha branca nas cores do atlas |
| 4 | **Reno** | Exige peça nova (Raupenhelm) | Württemberg (cores com fonte 🔶) e Baviera, ambos com Raupenhelm |

Alternativa: Reno primeiro, se o usuário preferir a peça nova (Raupenhelm) logo.

## 7. Estrutura do addon (proposta)

**Um PBO por grupo** (`hcl_suica`, `hcl_varsovia`, `hcl_italia`, `hcl_reno`), com prefixo `hcl\hcl_<grupo>`:
- cada PBO fica menor (o `hcl_fr` já tem 145 MB);
- recompilar um grupo não mexe nos outros;
- se o jogo travar um PBO, só aquele vai para `release\_atualizacao\`.

Alternativa: um único `hcl_aliados_fr` com subpastas por grupo.

## 8. Decisões

Respostas do usuário em 2026-10-13 (AskUserQuestion):

| # | Pergunta | Resposta |
|---|---|---|
| A1 | Ordem dos grupos | ✅ **Suíços → Varsóvia → Itália/Nápoles → Reno** |
| A2 | Um PBO por grupo ou um só | ✅ **Um PBO por grupo** (`hcl_suica`, `hcl_varsovia`, `hcl_italia`, `hcl_reno`) |
| A3 | Estados do Reno no primeiro lote | ✅ **Württemberg, Baviera, Saxônia e Vestfália** (Baden e Hesse continuam sem arte) |
| A4 | Unidades além dos fuzileiros de linha | ✅ **Granadeiros, voltigeurs e ligeira/Jäger** (casacas verdes dos atlas) |
| A5 | Varsóvia: barretina ou czapka | ✅ **Czapka rogata**, pelo regulamento de 3/9/1810 📜 (2026-10-18: "continuar" + "utilize fontes históricas de museus e documentos"). A barretina com placa de sol do atlas fica fora (sem documento) |
| A6 | Suíços 2º e 4º sem fonte firme | ✅ **Entram**, por recolor da F04. Em 2026-10-18 a fonte apareceu (Fieffé): azul-real e azul-celeste, as cores usadas. O nome "(facing colour unconfirmed)" sai na próxima montagem do `hcl_suica` |

Consequência da A2: cada addon é **autônomo** (cópias próprias dos modelos, com prefixo próprio). Nenhum depende do `hcl_fr`, conforme o pedido ("em CÓPIAS próprias").

## 9. Fontes

- [WP-PL1] Wikipedia, "1st Infantry Regiment (Duchy of Warsaw)" — https://en.wikipedia.org/wiki/1st_Infantry_Regiment_(Duchy_of_Warsaw) (cita Askenazy 2003; Gembarzewski).
- [WP-PL9] Wikipedia, "9th Infantry Regiment (Duchy of Warsaw)" — https://en.wikipedia.org/wiki/9th_Infantry_Regiment_(Duchy_of_Warsaw)
- [WP-PL] Wikipedia, páginas do 6º e 7º Regimentos (Duchy of Warsaw), lidas só pelo resumo da busca.
- [F-PEN] Pendraken Forum, discussão czapka × barretina — https://www.pendrakenforum.co.uk/index.php/topic,18209.20.html
- [PSR-W] Plastic Soldier Review, Württemberg — https://plasticsoldierreview.com/Review.aspx?id=1143
- [MD-W] miniatures.de, "Wuerttemberg Napoleonic Line Infantry … 1808–1812" — https://www.miniatures.de/wuerttemberg-infantry-1808-1812.html (cita Knötel-Sieg; Haythornthwaite).
- [WP-BAV] Wikipedia, "Bavarian Army" — https://en.wikipedia.org/wiki/Bavarian_Army
- [WTJ] War Times Journal, Republique Uniform Guide, Bavaria — https://www.wtj.com/games/republique/uniforms/index_bav.htm
- [F-NO] Napoleon-Online, "Saxon army at Danzig 1807" — https://forum.napoleon-online.de/forum/armeen/uniformen/437-saxon-army-at-danzig-1807
- [F-TAP] The Outpost (Tapatalk), "HELP!! Who Are We?" — https://www.tapatalk.com/groups/theoutpost/help-who-are-we-t1469.html
- [WM-4W] Wargaming and Modelmaking wiki, "4th Westphalia Line Regiment" — https://wargaming-and-modelmaking.fandom.com/wiki/4th_Westphalia_Line_Regiment
- [MD-I] miniatures.de, "Italian Line Infantry of the Napoleonic Wars, 1807–1814" — https://www.miniatures.de/italian-infantry-1807-1814.html
- [WP-NAP] Wikipedia, "Army of the Kingdom of Naples (Napoleonic)" — https://en.wikipedia.org/wiki/Army_of_the_Kingdom_of_Naples_(Napoleonic)
- [F-PF] Planetfigure, "reign of Naples" — https://planetfigure.com/threads/reign-of-naples.14535/post-151490
- [WP-SW1] Wikipedia, "1st Swiss Regiment (France)" — https://en.wikipedia.org/wiki/1st_Swiss_Regiment_(France)
- [WP-SW2] Wikipedia, "2nd Swiss Regiment (France)" — https://en.wikipedia.org/wiki/2nd_Swiss_Regiment_(France)
- [WP-SW3] Wikipedia, "3rd Swiss Regiment (France)" — https://en.wikipedia.org/wiki/3rd_Swiss_Regiment_(France) (cita Fieffé 1854).
- [OSP-SW] Osprey, *Napoleon's Swiss Troops* (descrição) — https://www.ospreypublishing.com/uk/napoleons-swiss-troops-9781849086790
- [LOJA-SW4] Treefrog Treasures, "Swiss 4th Line Infantry Officer" — https://www.treefrogtreasures.com/p-31390-swiss-4th-line-infantry-officer.aspx (página de venda).
- [WP-DE-SW] Wikipedia (de), "Schweizerregimenter im Russlandfeldzug 1812", seção Uniform, citando Fieffé, *Geschichte der Fremdtruppen im Dienste Frankreichs*, Bd. II, München 1860, S. 183 — https://de.wikipedia.org/wiki/Schweizerregimenter_im_Russlandfeldzug_1812
- [MUS-MORGES] Château de Morges (museu), "Veste d'uniforme du 1er régiment suisse" — https://chateau-morges.ch/collections-et-bibliotheque/objets-choisis/veste-duniforme-du-1er-regiment-suisse/
- [REG1810] *Przepis ubiorów* do Księstwa Warszawskiego, 3 de setembro de 1810 (regulamento). Texto em Gembarzewski, *Wojsko polskie. Księstwo Warszawskie 1807–1814*, Warszawa 1905, pp. 48–49, 106–109 (digitalizado: Dolnośląska Biblioteca Digital — https://www.dbc.wroc.pl/publication/10484; não lido diretamente).
- [WP-MUN] Wikipedia (pl), "Mundur Armii Księstwa Warszawskiego", citando Żygulski (jun.) e Wielecki, *Polski mundur wojskowy*, KAW, Kraków 1988, pp. 57–62 — https://pl.wikipedia.org/wiki/Mundur_Armii_Ksi%C4%99stwa_Warszawskiego
- [NOP-1810] napoleon.org.pl, "Piechota XW wg przepisu 3 września 1810" (pranchas sobre a aquarela de J. Kosiński, 1810; cita o regulamento, Gembarzewski e a barretina do 2º Regimento no Museu Nacional de Cracóvia) — https://napoleon.org.pl/index.php/biblioteka-barwy-i-broni/piechota-xw-wg-przepisu-3-wrzesnia-1810
- [MNK-1959] Muzeum Narodowe w Krakowie, *Militaria Księstwa Warszawskiego. Katalog wystawy w 150 rocznicę oswobodzenia Krakowa przez wojska polskie 1809–1959* (catálogo; só o registro bibliográfico foi visto).
- [WP-IT-ES] Wikipedia (it), "Esercito del Regno d'Italia (1805-1814)", seção da infantaria, citando Pivka & Chappell, *Napoleon's Italian and Neapolitan Troops* (Osprey MAA 43), pp. 23–24 — https://it.wikipedia.org/wiki/Esercito_del_Regno_d%27Italia_(1805-1814)
- [ZANOLI] A. Zanoli, *Sulla milizia cisalpino-italiana: cenni storico-statistici dal 1796 al 1814*, Milão, Borroni e Scotti, 1845 (texto OCR do Internet Archive, `bub_gb_SyVEAAAAYAAJ`, lido 2026-10-18) — https://archive.org/details/bub_gb_SyVEAAAAYAAJ
- [VK-IT] New York Public Library, *Vinkhuijzen collection of military uniforms*, Italy 1812 / 1811–1812 (série de gravuras coloridas por regimento, NYPL b14896507-1528382 a -1528387; pranchas de Knötel) — via Wikimedia Commons, "Category:Vinkhuijzen: Military uniforms of Italy, Kingdom of Italy (1805-1814)"
- [VK-NAP] Idem, Kingdom of the Two Sicilies 1810–1812 e 1813–1814 — Commons, "Category:Vinkhuijzen: Military uniforms of Italy, napoleonic Kingdom of Naples"
- [KN-III-25] R. Knötel, *Uniformenkunde* III, nº 25, "Das Italienische Heer unter Vice-König Eugen, 1812" (Rathenow, c. 1890–1900; exemplar da coleção Vinkhuijzen, NYPL b14896507-1528391)
- [KN-V-46] R. Knötel, *Uniformenkunde* V, nº 46, "Königl. Neapolitanische Truppen (unter Joachim Murat), 1812" (NYPL b14896507-1608374)
- [KN-VI-23] R. Knötel, *Uniformenkunde* VI, nº 23, "Linien-Infanterie, Königl. Neapolitanische Truppen, 1812" (NYPL b14896507-1608373)
- [GA-7NAP] M. Gärtner, "The 7th Neapolitan Line Infantry Regiment 1812–1813", *Depesche* 1 (trad. J. Howard), The Napoleon Series, 2010 — https://www.napoleon-series.org/military-info/Despeche/Issue1/c_7thNeapolitanInfantry.html (cita a *Freiberger Bilderhandschrift*, Boisselier, Brauer, Forthoffer, Knötel, San Martino e Rastatt)
- [FREIBERG] *Freiberger Bilderhandschrift* (aquarelas de 1813, atribuídas a K. A. Winkler), via [GA-7NAP]; edição: A. Umhey, *Napoleon's Last Grande Armée* (não lida)
- [VK-REN] New York Public Library, *Vinkhuijzen collection of military uniforms*, via Wikimedia Commons, "Category:Vinkhuijzen: Military uniforms of Germany, Württemberg / Bavaria / Saxony / Westphalia" (álbuns de aquarelas "1810", "1811" e "1809", legendados à mão pelo colecionador; IDs NYPL na tabela §2.0 e em `indice.txt`)
- [NAP-ADAM] Fondation Napoléon, "L'Infanteria del Regno d'Italia", A. Adam, água-tinta aquarelada, Bibliothèque Marmottan — https://www.napoleon.org/en/history-of-the-two-empires/images/linfanteria-del-regno-ditalia-the-infantry-of-the-kindgom-of-italy
