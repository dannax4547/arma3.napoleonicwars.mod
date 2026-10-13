# Ficha Técnica: Barretina de Infantaria de Linha Francesa, 1810–1815 (por companhia)

Fase 2 do pipeline. Versão 1.0, 2026-10-12.

Pedido do usuário (2026-10-12): *"as barretinas que têm pompons aumentados, ex. granadeiros e voltigeurs, devem ser adicionadas iguais às daquela época"*. Por isso as companhias de elite entram já no protótipo, e não depois (decisão F6 da ficha do uniforme francês).

**Estado:** ficha + esboço (Fase 3, `docs/reports/barretina_fr_blockout.md`), aguardando aprovação.

Legenda: ✅ fonte lida · 🔶 provável (fontes secundárias, ou só fórum) · ❓ incerto · 🎮 visto no atlas do mod

---

## 1. Forma

| Item | Valor | Confiança |
|---|---|---|
| Modelo | Barretina de feltro preto com faixas de couro no alto e no pé, divisas laterais em V, pala, placa de latão, cocar tricolor e pompom na cor da companhia. Cordões e borlas só em gala, retirados em campanha | ✅ [W1] |
| Modelo de 1811 | "Um pouco mais alto e mais alargado no topo"; sem divisas laterais; com jugulares de escamas e um pano de nuca interno | ✅ [W1] |
| Placa | Losango **ou** águia sobre semicírculo (as duas existiram) | ✅ [W1]; 🎮 as duas no atlas (c3 r4, c4 r5) |
| Divisas laterais | O modelo de 1811 não as tinha, mas o mod mostra divisas brancas, amarelas e vermelhas (c5–c7 r5) | ✅ [W1] + 🎮. Mantidas como no mod (decisão B2) |

## 2. Distinções por companhia

| Companhia | Pompom / plumet | Faixas e divisas | Cordões | Confiança |
|---|---|---|---|---|
| **Fuzileiros** (4 companhias) | Pompom (lentilha) na cor da companhia: **1ª verde-escuro, 2ª azul-celeste, 3ª aurora (laranja-rosado), 4ª violeta** (ordem de fevereiro de 1811) | Couro preto | Não | 🔶 [S1][S2] (ordem citada, texto não lido); cores 🎮 (verde, azul, amarelo-laranja) |
| **Granadeiros** | **Vermelho**: plumet alto (gala) ou pompom (campanha) | Galões vermelhos no alto e no pé e divisas vermelhas | **Vermelhos**, com raquetes e borlas (gala) | ✅ [W1] "vermelho" + 🔶 [S1][S2] detalhes; 🎮 divisas e galão vermelhos |
| **Voltigeurs** | Padrão de 1807: **plumet verde de ponta amarela** (ou todo verde). Mais tarde: pompom ou plumet **amarelo** | Galões e divisas **amarelos** | **Verdes** (padrão de 1807) | ✅ [W2] (1807) + 🔶 [S1] (amarelo depois); 🎮 divisas e galão amarelos |
| Oficiais subalternos e sargentos | Pompom branco | — | — | 🔶 [S1] |

**Ressalvas históricas (das próprias fontes):**
- O regulamento de 1812 ("Bardin") restringia plumets e cordões aos oficiais superiores. Na prática, eles continuaram em uso 🔶 [S1][S2].
- Os uniformes de 1812 foram distribuídos sobretudo aos conscritos de 1813; o estoque antigo seguiu em uso até 1814 🔶 [S1].
- As distinções variavam de regimento para regimento: plumet **ou** pompom, com ou sem cordões 🔶 [S1].

Por isso o addon traz, para cada companhia de elite, uma versão de **gala** (plumet e cordões) e uma de **campanha** (pompom grande, sem cordões). As duas são de época.

## 2.1 Oficiais (pedido de 2026-10-12: "cria um destes para oficiais franceses")

| Item | Valor | Confiança |
|---|---|---|
| Plumet | Só oficiais superiores: **coronel branco**, **major branco com ponta vermelha**, **chefe de batalhão vermelho** | 🔶 [S3] (resumo; uma fonte diz que o modelo de 1812 já não tinha plumet) |
| Galões do posto | Ouro (prata na ligeira) no alto: **coronel 34 mm + 14 mm, 20 mm abaixo** (o único com dois); subtenente e ajudante: um galão de 18 mm | 🔶 [S3] (medidas sem data) |
| Cordões | Proibidos a partir de novembro de 1810, quando vieram as jugulares de escamas | 🔶 [S3] |
| Placa e escamas | Douradas; águia e número do regimento | 🔶 (peça de leilão do 52º de linha, modelo de 1812) |

No esboço: oficial **coronel**, com 2 galões dourados, sem divisas e com plumet branco. O major e o chefe de batalhão mudam só a cor do plumet (fileira de plumets).

## 2.2 Plumet realista (pedido de 2026-10-12: "dê mais realismo neste e neste")

- O plumet da época era uma coluna densa de penas de galo cortadas, em forma de cenoura: mais larga no primeiro terço e com a ponta macia.
- `source/scripts/plumet.py` monta isso por script:
  - um núcleo coberto por camadas de penas estreitas e côncavas, em espiral, com as pontas arredondadas curvando para fora;
  - um tufo que fecha a ponta;
  - uma leve inclinação;
  - variação de tom de pena para pena.
- Cada pena tem o seu quadrado de UV: uma única textura de pena (barbas, nervura, bordas) serve para todas, e as cores entram por variante.
- Triângulos: ~2.700 por plumet na Resolução 1. Nas Resoluções 2 e 3 ele vira o fuso liso.

## 3. Fontes

| ID | Fonte | O que dá |
|---|---|---|
| W1 | [Uniforms of La Grande Armée (Wikipedia)](https://en.wikipedia.org/wiki/Uniforms_of_La_Grande_Arm%C3%A9e) | Barretina de 1806/07 e de 1811; placas; vermelho dos granadeiros; amarelo ou verde dos voltigeurs |
| W2 | [Voltigeur (Wikipedia)](https://en.wikipedia.org/wiki/Voltigeur) | Barretina dos voltigeurs em 1807: faixa e divisas amarelas, cordões verdes, plumet verde (às vezes de ponta amarela) |
| S1 | Resumo de busca: [napoleonguide.com](https://www.napoleonguide.com/infantry_frcol.htm), [Warlord Games](https://www.warlordgames.com/community/topic/french/), [The Outpost](https://www.tapatalk.com/groups/theoutpost/viewtopic.php?p=65461) | Cores das companhias de fuzileiros (1811), proibição dos plumets em 1812, pompons brancos dos graduados. **São fóruns e sites de hobby**, não fonte primária |
| S2 | Resumo de busca: [Wikipedia (espelho)](https://wikipedia.classicistranieri.com/en/articles/u/n/i/Uniforms_of_La_Grande_Arm%C3%A9e_62d9.html), [warhistory.org](https://warhistory.org/es/article/french-infantry?amp=1) | Mesmas regras, em resumo |
| S3 | Resumo de busca: [Shako (Wikipedia)](https://en.wikipedia.org/wiki/Shako), [napoleonguide.com](https://www.napoleonguide.com/infantry_frcol.htm), [auction.fr: barretina de oficial do 52º](https://www.auction.fr/en-US/lot/rare-french-officers-shako-of-the-52nd-line-infantry-regiment-first-empire-model-1812-an-82383899), [militaryheritage.com](https://www.militaryheritage.com/napfranc.htm) | Plumets e galões dos oficiais |
| Sugerida | Pranchas de Martinet; L. Rousselot, *L'Armée française*; Osprey *Napoleon's Line Infantry* | Confirmariam alturas e regras exatas. **Não consultadas** |
| M5 | Atlas `FranceINF_diffuse`, linhas 4–5 (`docs/references/img/ref_fr_05_barretinas_folha_mod.png`) | Placas, cocar, pompons de 5 cores, galões, divisas, plumets e escamas, como o mod desenha |

## 4. Medidas propostas (🔶; não há vista lateral no mod)

| Medida | Valor | Base |
|---|---|---|
| Base | 0,180 m, encaixada no aro de cabeça oficial | Mesmo método da barretina prussiana aprovada (`shako_fit.py`) |
| Altura | 0,190 m (0,196 m depois do encaixe) | "Um pouco mais alta" que a de 1806 [W1] |
| Topo | 0,250 m (alargado) | "Mais alargada no topo" [W1] |
| Faixas | Alto 0,030 m, pé 0,020 m | 🎮 proporção do galão no atlas |
| Cocar | ⌀ 0,060 m, no alto da frente | 🎮 |
| Pompom lentilha | ⌀ 0,062 × 0,020 m | 🔶 |
| Pompom grande (elite, campanha) | ⌀ 0,072 m | 🔶 ("pompons aumentados", pedido do usuário) |
| Plumet | 0,30 m acima da barretina, mais largo a 1/4 da altura | 🔶 (proporção de gravuras; confirmar) |
| Pala | 0,055 m, caída 40° | 🔶 |

## 5. Requisitos do ARMA 3

Os mesmos da barretina prussiana (verificados nos Samples):
- template de item de cabeça, rígida no osso `Head`;
- Resoluções 1–3, sombra (casco convexo) e Geometry vazio;
- seleção `camo`.

Cada companhia é uma **classe** do config. Só a cor muda entre:
- as 4 companhias de fuzileiros (cor do pompom);
- os vermelhos e amarelos dos galões e divisas.

Essas usam a mesma malha com outra textura. Gala e campanha precisam de **malhas diferentes** (plumet e cordões são geometria).

| Malha | Usada por |
|---|---|
| Base com pompom lentilha | Fuzileiros 1ª–4ª (4 texturas) |
| Base com pompom grande | Granadeiros e voltigeurs de campanha (2 texturas) |
| Base com plumet + cordões | Granadeiros e voltigeurs de gala (2 texturas; o plumet do voltigeur tem a ponta amarela pintada) |

Mais a escolha da placa (F4 da ficha do uniforme): losango ou águia. Isso dá até 2 × 3 = 6 malhas e 8 classes por placa.

## 6. Decisões pedidas

| # | Pergunta | Recomendação |
|---|---|---|
| B1 | Aprovar o esboço (forma, alturas, plumet de 0,30 m) | Ver as imagens do relatório |
| B2 | Manter as divisas laterais em V, como no mod, mesmo o modelo de 1811 não tendo | **Sim** (o mod as mostra, e a barretina de 1806/1810 as tinha) |
| B3 | Voltigeur de gala: plumet **verde de ponta amarela** com cordões verdes (padrão de 1807, como no esboço) **ou** tudo amarelo | **Verde de ponta amarela** (é o mais documentado) |
| B4 | Fuzileiros: as 4 cores de companhia (verde-escuro, azul-celeste, aurora, violeta) | **Sim**, as 4 |

## 7. Medidas com fonte (2026-10-13; pedido: *"mais profissionalmente com mais poligonos e adicoes de detalhes e altura com fontes historicas"*)

| Medida | Valor adotado | Fonte | Antes |
|---|---|---|---|
| Altura do feltro, fuzileiro | 202 mm | [Bardin 1812, via histoirevivante](https://histoirevivante.1fr1.net/t41-reglement-d-habillement-1812-bardin): 217 mm menos 15 mm; peças: 200 mm ([43e](https://www.bertrand-malvaux.com/p/17926/shako-du-43eme-regiment-de-fusilier-d-infanterie-de-ligne-modele-1812-premier-empire.html), [101e](https://www.bertrand-malvaux.com/en/p/17924/shako-troupe-du-101-regiment-d-infanterie-de-ligne-modele-1812-premier-empire.html)) | 196 mm |
| Altura, granadeiro (e carabineiro) | +15 mm (217 mm) | Bardin 1812; [Calpe Miniatures](https://www.calpeminiatures.co.uk/Guides_and_Research/French/French_Infantry_Uniforms_1813-1815.html) | igual ao fuzileiro |
| Topo | 244 mm | Modelo de 1810: 19 cm de altura, topo de 24,4 cm ([Wikipedia, Uniforms of the Grande Armée](https://en.wikipedia.org/wiki/Uniforms_of_La_Grande_Arm%C3%A9e)) | 250 mm |
| Faixa de cima / de baixo | 41 / 27 mm | Bardin 1812: calota dobrada a 41 mm, bourdalou de 27 mm, galões de granadeiro de 41 e 23 mm | 30 / 20 mm |
| Pala | 58 mm | Bardin 1812: 61 mm embaixo, 54 mm em cima | 55 mm |
| Placa | 130 × 118 mm | Peças: 13,3 × 12,2 cm ([1er de ligne, oficial de granadeiros](https://www.bertrand-malvaux.com/fr/p/44420/SHAKO-D-OFFICIER-DE-GRENADIERS-DU-1er-REGIMENT-D-INFANTERIE-DE-LIGNE-modele-1812-Premier-Empire-27965.html)) | 105 × 83 mm |
| Rosetas da jugular | ⌀ 41 mm | Peças: 41 mm (101e), 42 mm (43e), 40 mm ([8e voltigeur](https://www.bertrand-malvaux.com/fr/p/17922/shako-du-8eme-regiment-de-voltigeur-d-infanterie-de-ligne-type-1812-premier-empire.html)) | 24 mm |
| Escamas | 34 → 21 mm de largura | Peça do 101e | 14 → 11 mm |
| Suadouro (basane) | 57 mm | Peça do 101e | 39 mm |
| Plumet | 0,38 m (mantido) | **Sem medida em fonte**; 1812 aboliu cordões e plumets no regulamento, mantidos na prática pela elite (Calpe; Warlord) | 🔶 |

Medidas de peças de museu variam de exemplar para exemplar: os valores acima são os mais repetidos.

### 7.1 Chapéu de pele da Guarda (ficha `velha_guarda.md`)

| Medida | Valor adotado | Fonte | Antes |
|---|---|---|---|
| Altura | 35 cm na frente, 39 cm atrás | [Bertrand-Malvaux, bonnet de sous-officier 1808-1815](https://www.bertrand-malvaux.com/fr/p/30075/bonnet-a-poils-de-sous-officier-des-grenadiers-a-pied-de-la-garde-imperiale-modele-1808-1815-premier-empire.html); 33 cm segundo [Wikipédia fr](https://fr.wikipedia.org/wiki/Uniforme_des_grenadiers_%C3%A0_pied_de_la_Garde_imp%C3%A9riale) | 32 cm |
| Largura no alto | 27 cm | idem | 24 cm |
| Placa | 217 × 160 mm | Placas autênticas 21,7 × 15,7–16 cm ([1er-empire.com](https://1er-empire.com/fr/archives/113-plaque-de-bonnet-a-poils-de-grenadiers-a-pied-de-la-garde-imperiale-1er-empire.html); leilões) | 128 × 91 mm |
| Topo (*calotte*) | oval 135 × 115 mm | Bertrand-Malvaux | disco de 92 mm |
| Ornamento do topo | **cruz branca até 1807; granada branca de 1808 a 1815** | Bertrand-Malvaux | cruz (escolha do usuário) |
| Pluma | 35 cm, encaixe a 24 cm da borda | Furo a 24 cm (Bertrand-Malvaux); 28 cm (reprodução) a 37 cm (fórum) | 38 cm |
