# HIST-RUS-INF-KIVER-1812-001: kiver da infantaria do exército russo, 1812–1814

Dossiê de pesquisa (Gate A da especificação mestre, §3–7 e §65–66; registro de referências da documentação do mod, §8.3 e §17.3).
Versão 1.0, 2026-10-17. Pesquisa feita nesta data. Todas as páginas citadas foram abertas em 2026-10-17, salvo quando indicado o contrário.

| Campo | Valor |
|---|---|
| Identificador | `HIST-RUS-INF-KIVER-1812-001` (variantes `-1812` mosqueteiro e granadeiro; `-1808` em §6) |
| Nome histórico | кивер (*kiver*); "кивер образца 1812 года" é nome da literatura, não do regulamento (§4, I1) |
| Nação / arma | Império Russo / infantaria do exército (granadeiros, mosqueteiros) |
| Período | Ordem de 1º jan 1812; uso geral de 1813 a 1814; até 1816–1817 |
| Presença em Waterloo | **Nenhuma** (pacote de expansão `NAP_RUS`) |
| Ativos ligados | `source/scripts/blockout_kiver_rus.py`, `source/models/shakos/hcl_kiver_rus/`, ficha `docs/specs/rus_1812.md`, relatório `docs/reports/rus_1812_blockout.md` |
| Estado | Pesquisa (Gate A) concluída para o blockout; aprovação de design (Gate B) pendente |

Confiança, conforme a documentação do mod (§8.3): **alta** = objeto original ou regulamento; **média** = estudo especializado ou prancha documentada; **baixa** = reconstituição moderna sem proveniência clara.

---

## 1. Fontes

| ID | Tipo | Instituição / autor | Título e localizador | Data da fonte × data da prática | Confiança | Direitos |
|---|---|---|---|---|---|---|
| **A1** | Objeto original | **Museu Estatal Hermitage**, São Petersburgo. Exposto em *Au service des Tsars* (Paris, 2010) | Kiver de infantaria da Guarda Imperial Russa, datado de 1812–1817. Inventários **ЭРТ‑10900 e ЭРТ‑10804** (pela legenda da foto; **a ficha do Hermitage não foi encontrada online**). Foto: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Au_service_des_Tsars_-_Shako_%D0%ADPT-10900_et_%D0%ADPT_10804_001.jpg), autor Thesupermat, 2010‑10‑14 | Objeto do período | **Alta** para forma, materiais e cordão; **é da Guarda** (águia, cordão metálico), não do exército | Foto CC BY‑SA 3.0: só pesquisa; não entra no mod |
| **R1** | Regulamento (compilação de arquivo) | A. V. Viskovatov, *Историческое описание одежды и вооружения российских войск*, vol. 10 (1801–1825), SPb., 1851. Tradução inglesa de Mark Conrad, 1993 | [marksrussianmilitaryhistory.info/V10BAll.htm](https://marksrussianmilitaryhistory.info/V10BAll.htm), seções *Grenadier Regiments* e *Musketeer Regiments* | 1851, compilando ordens de 1802–1825 | **Alta** para datas e textos das ordens; tradução de terceiro | Texto citado só em trecho curto |
| **P1** | Prancha documentada | Viskovatov, *Рисунки…* [Рис. 1274–1400], Biblioteca Histórica Pública Estatal da Rússia (**ГПИБ**) | **Рис. 1323**, *Гренадерскіе кивера, 1812–1816*: frente e perfil. [Nó 8951](http://shpl.dlibrary.org/ru/nodes/8951-risunki-odezhdy-i-vooruzheniya-rossiyskih-voysk-ris-1274-1400-b-g), página `957758` | Edição sem data, catálogo diz [1881]; desenho do arquivo (1840–50) | **Média** | ГПИБ: reprodução só com autorização escrita → **só pesquisa** |
| **P2** | Prancha documentada | idem | **Рис. 1359**, mosqueteiro de corpo inteiro com o kiver de 1812 (legenda: *Мушкетеръ*; o ano da legenda não foi lido com segurança). Página `957830` | idem | **Média** | idem |
| **P3** | Prancha documentada | idem | *Пѣхотные репейки и темляки нижнихъ чиновъ, 1811–1833* (pompons e fiadores; pela ordem das pranchas, o Рис. 1320 citado em R1, a confirmar). Página `957752` | idem | **Média** | idem |
| **P4** | Prancha documentada | idem | **Рис. 1308**, *Гренадеры 1807–1808* (o kiver de 1807–1808). Página `957728` | idem | **Média** | idem |
| **S1** | Texto especializado | Portal "1812" da Rússia (museum.ru), seção de chapéus da infantaria russa | `museum.ru/museum/1812/Army/RussInfantery/gol_ubor_1.htm` (**404 em 2026‑10‑17**; lido só pelo resumo do buscador) | Moderno | Média (não lido direto) | — |
| **S2** | Texto especializado | 1812.nsad.ru, *Форма русской пехоты* | [1812.nsad.ru/46](https://1812.nsad.ru/46) | Moderno, sem citação por item | Média/baixa | Só citação curta |
| **S3** | Enciclopédia | Wikipedia em russo, [Кивер](https://ru.wikipedia.org/wiki/Кивер) e [Знаки на кивера русской армии 1812 года](https://ru.wikipedia.org/wiki/Знаки_на_кивера_русской_армии_1812_года) | Cita Brockhaus‑Efron, Kirsanova (1995), Belovinsky (2007) | Moderno | Baixa/média (texto não revisado, segundo a própria página) | — |
| **S4** | Guia de hobby | V. Rospond, [*Russian Army Uniforms 1807–1815*](https://www.warlordgames.com/russian-army-uniforms-1807-1815/) (Warlord Games), citando Haythornthwaite (Osprey MAA 185), Knötel/Elting, Nafziger | — | Moderno | Baixa | — |
| **F1** | Discussão especializada | [TMP, "kiwer query"](http://theminiaturespage.com/boards/msg.mv?id=356393) e [TMP, "Russia 1808–1811?"](http://theminiaturespage.com/boards/msg.mv?id=323817&page=2) (resumos de busca) | — | Moderno | Baixa (fórum) | — |
| **U1–U3** | Reconstituição moderna | Três fotos de réplicas enviadas pelo usuário no chat em 2026‑10‑17 (fabricante desconhecido; réplicas iguais são vendidas como "копия" em [antikvariat.ru](https://antikvariat.ru/catalog/archive/kiver-obraztsa-1812-goda-s-razvalom-perv/)) | Não salvas no repositório | Moderno | **Baixa** | Do usuário; não entram no mod |

**Consultadas sem resultado (limitações):**
- coleção online do Hermitage: a ficha de ЭРТ‑10900 não foi achada pela busca;
- Goskatalog (goskatalog.ru): nenhuma ficha de kiver de infantaria de 1812 apareceu pela busca;
- GIM e Museu de Artilharia (VIMAIViVS): nenhum objeto identificado online;
- fórum napoleon‑online, "Viskovatov text vs engravings": 404.

**Não consultados:** Haythornthwaite (Osprey MAA 185), Knötel/Elting vol. IV, Nafziger, Kirsanova, e o texto original da ordem de 1º jan 1812 no ПСЗ.

## 2. O que cada fonte mostra (observação)

### A1, objeto do Hermitage (foto de frente, um pouco de cima)
- Corpo preto com brilho; alarga para os lados no alto, cerca de 1,25–1,3 vez a base (medido na foto, com perspectiva).
- Borda de cima reforçada; vê‑se parte do tampo.
- **Cordão (этишкет): trança chata e larga** (proporcionalmente uns 25–30 mm) atravessando a frente **baixo**, logo acima da pala, em arco raso.
- **Borla curta na ponta esquerda do festão** (esquerda de quem veste).
- **Cordão longo pendente no lado direito** de quem veste, com uma **raquete trançada chata** e borlas grandes, bem abaixo do kiver.
- Pala grande, envernizada e arredondada. Escamas de latão no barbicacho. Distintivo: águia da Guarda.

### P1, Рис. 1323 (frente e perfil, granadeiro)
- **Perfil:** frente quase vertical; **a traseira alarga muito para trás**; o tampo desce para trás.
- **Frente:** topo bem mais largo que a base, laterais côncavas.
- **Faixa envernizada no alto**, com uma costura logo abaixo. Faixa escura em baixo, sobre a qual corre o cordão.
- **Pompom oval** em pé, no alto da frente, diante da base da pluma. Uma **presilha escura** desce dele até a granada.
- **Granada de 3 chamas**: bola pequena, chama central alta e estreita, chamas laterais curtas e baixas. Fica logo acima do cordão.
- **Cordão:** trança chata **em espinha de peixe**, larga, cruzando a frente baixo. No perfil, sobe para trás (a segunda trança). Na junção do lado pendem uma **raquete alongada em forma de folha** e uma borla, até a altura da mandíbula.
- **Barbicacho:** **roseta grande** de latão (anéis concêntricos com domo) sobre a orelha; **escamas largas** que se estreitam até o queixo.
- **Pala:** longa, pouco inclinada, com a borda debruada.
- **Pluma:** crina preta em forma de clava, larga em cima, de ponta arredondada, com o contorno irregular dos fios.

### P2, Рис. 1359 (mosqueteiro)
- Kiver de topo largo; pompom oval chato com anel e centro de cores diferentes.
- **Granada de 1 chama**, alta, no meio da frente.
- Cordão branco baixo na frente; **duas borlas curtas** do lado esquerdo de quem veste, perto da pala; **cordão longo** do lado direito, descendo até o peito (mesma disposição de A1).
- Casaca de **abotoamento duplo, 6 + 6**, com **as fileiras bem afastadas** (cerca de 40 % da largura do peito); **portinhola do punho com 3 botões**.

### P3, pompons 1811–1833
- Pompom **oval em pé**, proporção ~1,6 : 1, **de lã felpuda**; anel externo e **centro oval** de outra cor. Preso por **duas hastes de arame**.

### R1, Viskovatov, texto das ordens
- 19 dez 1807: kiver debruado de couro preto em cima e dos lados, pala costurada.
- 14 jul 1808: granada de latão, 3 chamas (granadeiros) e 1 chama (fuzileiros).
- 11 jun 1809: cordões, brancos para os soldados.
- 4 fev 1811: plumas de 16½" × 5¾" em cima × 1¾" na base.
- 22 fev 1811: cores de pompom por batalhão e companhia.
- **1º jan 1812** (Рис. 1323): kiver novo, **mais baixo**, **mais largo em cima, laterais côncavas**, escamas de latão chatas, sem abas de orelha nem de nuca.
- **26 set 1817** (Рис. 1332): o mesmo kiver especificado:
  - couro forrado (ou coberto, conforme a tradução) de pano preto em toda a altura, tampo envernizado;
  - **7"** de altura; **diâmetro de cima 4" maior que o de baixo**;
  - 4 tiras laterais envernizadas de ⅞";
  - pompom **oval de madeira forrado de pano, 3"**;
  - **18 escamas por lado**;
  - plumas de 19" em suporte envernizado.

### S2, 1812.nsad.ru
- Corpo cilíndrico preto com **fenda embaixo atrás, debruada de tira de couro de topo arredondado**, para ajustar ao tamanho da cabeça.
- **Tiras de couro em "V" costuradas dos lados.**
- Cordão: **duas tranças, uma pela frente e outra por trás**.
- Granada de 3 chamas; sultão de 42 cm.

## 3. Interpretação e decisões de implementação

| # | Elemento | Decisão | Base | Rótulo (especificação §2.1) |
|---|---|---|---|---|
| D1 | Altura | 178 mm na frente (× encaixe 1,032) | R1 (1817), o mesmo modelo | **Provável** |
| D2 | Alargamento | Frente +6 mm, lados +32 mm, trás +70 mm no raio; os 4" de R1 lidos como o crescimento frente‑trás | R1 + perfil de P1 + frente de A1 (1,25–1,3) | **Estimado** |
| D3 | Tampo | Desce 6° para trás (além dos 8° de inclinação do encaixe aprovado), côncavo e envernizado | P1 (perfil), R1 | **Estimado** |
| D4 | Material do corpo | **Pano preto fosco** sobre couro; tampo, faixas, tiras em V e pala **em couro envernizado** | R1 1817, S1, S2. A1 parece brilhante: pode ser verniz da Guarda ou a luz da vitrine | **Provável**; divergência registrada (I3) |
| D5 | Faixa de cima | 18 mm envernizada, com costura | P1 | Provável |
| D6 | Faixa de baixo | 20 mm envernizada, sob o cordão | P1 | Provável |
| D7 | Tiras em V | Uma em cada lado, ápice embaixo perto da roseta, braços para cima‑frente e cima‑trás, 22 mm | R1, S2, S3 | Provável (posição exata estimada) |
| D8 | Fenda de ajuste atrás | Tira de couro de 30 × 70 mm, topo arredondado, no meio de trás, embaixo | S2 | Provável |
| D9 | Granada | Bola de ⌀ 22 mm; chama central de 46 mm em lágrima; granadeiro com 2 chamas laterais curtas (26 mm, 55° da vertical). Centro a ~45 % da altura, acima do cordão | P1, P2, R1 | Formas **prováveis**; medidas **estimadas** |
| D10 | Pompom | Oval de 76 × 48 × 22 mm, lã felpuda, anel e centro oval; 2 hastes de arame. Mosqueteiro e granadeiro, cores de 22 fev 1811 | R1 (3"), P1–P3 | Provável |
| D11 | Presilha | Couro preto, 12 mm, do alto da frente até a ponta da chama | P1 | Provável. **A presilha branca com botão de U1 não tem apoio nas fontes e não foi usada** |
| D12 | Pluma (granadeiro) | 420 mm, 44 → 146 mm, forma de clava de ponta redonda, fios irregulares, suporte envernizado | R1 (1811), P1 | Provável |
| D13 | Cordão | Duas tranças chatas em espinha de peixe, ~22 mm de largura: a da frente baixa (~28 % da altura no meio), a de trás em volta da traseira. Lado esquerdo: 2 borlas curtas. Lado direito: cordão pendente com raquete e 2 borlas | A1, P1, P2, S2 | Provável |
| D14 | Comprimento do pendente | **Encurtado até a altura da mandíbula** (P1 de perfil), e não até o peito (P2) | Um item rígido preso ao osso da cabeça atravessaria o ombro e a gola ao virar a cabeça | **Decisão de design** |
| D15 | Barbicacho | Roseta de ⌀ 44 mm com anéis e domo; **18 escamas** de 33 → 20 mm | R1 (18 escamas, 1817), P1 | Provável (medidas estimadas) |
| D16 | Pala | 62 mm, 22° para baixo, borda debruada | P1 | Estimado |
| D17 | Cor do cordão | Branco (soldados) | R1 (1809, 1811) | Confirmado (regulamento) |
| D18 | Pompons do 2º e 3º batalhão (Fase 7, RU7) | Mosqueteiro: 2º verde com centro branco, 3º azul-celeste com centro branco. Granadeiro: 2º vermelho com o **terço de baixo** verde, 3º vermelho com o terço de baixo azul-celeste. Só textura (mesmo modelo) | R1 (22 fev 1811), pela ficha `rus_1812.md` §2.4 | Cores: confirmadas pelo regulamento, mas **provisórias** (o fórum [OP] avisa que boas fontes discordam). "Embaixo" = terço de baixo: **interpretação** nossa (nenhuma prancha do pompom de granadeiro de 2º/3º batalhão foi vista). Tom do azul-celeste: **estimado** (linear 0,13 / 0,36 / 0,78, o mesmo do bleu céleste francês do projeto) |

## 4. Registro de incertezas

| # | Questão | Interpretações | Risco | Implementação atual | Evidência que falta |
|---|---|---|---|---|---|
| I1 | **O kiver côncavo existiu em 1812 como regulamento?** | R1: ordem de 1º jan 1812 com Рис. 1323. S3 e F1: nunca introduzido oficialmente, comum só em 1813–1814, sem modelo sobrevivente de soldado | Alto (identidade do item) | Os dois kivers (RU3). O de 1812 é rotulado "1812–1814"; o de 1808 cobre a campanha de 1812 | Texto da ordem no ПСЗ; fichas do GIM ou do Hermitage |
| I2 | Medidas do modelo de 1812 | Só existe a especificação de 1817 | Médio | D1, D2 | Objeto medido (A1 não tem medidas publicadas online) |
| I3 | Corpo de pano fosco ou couro envernizado | R1, S1 e S2: pano; A1 parece brilhante | Médio (material) | Pano fosco (D4) | Ficha do Hermitage |
| I4 | Lado do pendente e das borlas | A1 e P2 concordam (pendente à direita, borlas curtas à esquerda); P1 só mostra o perfil direito | Baixo | D13 | — |
| I5 | Nenhum kiver de **soldado do exército** de 1812 identificado em museu | — | Alto para Gate F | A1 (Guarda) usado para a forma; P1–P2 para o exército | Busca no Goskatalog pelo nome do museu; contato com o GIM |
| I6 | Divisão do pompom de granadeiro do 2º e 3º batalhão ("vermelho, verde embaixo") | R1 diz só "embaixo"; sem prancha vista | Baixo (cor de um detalhe pequeno) | Terço de baixo do oval (D18) | P3 (pranchas de pompons 1811–1833, ГПИБ), ver de novo com esse foco |

## 5. Manifesto de referências

| Ref | Arquivo no repositório | Uso | Observação |
|---|---|---|---|
| A1 | não copiado (link do Commons) | Forma, cordão, pala | CC BY‑SA 3.0; poderia ser guardado com atribuição, mas não é necessário |
| P1–P4 | **não copiados** (ГПИБ exige autorização) | Perfil, granada, pompom, cordão, barbicacho | Vistos na biblioteca digital; páginas `957728`, `957752`, `957758`, `957826`, `957830` |
| U1–U3 | não salvos | Só contexto | Réplicas modernas |

## 6. Kiver de 1808 (campanha de 1812)

- **Fontes:** R1 (19 dez 1807, 14 jul 1808, 1809–1811); P4 mostra o kiver de 1807–1808 de granadeiro, ainda alto, com pluma alta e cocar. O cocar saiu em 1809–1812 (S3).
- **Uso em 1812:** os granadeiros entraram em 1º jan 1812 com o kiver de 1808 (S1, pelo resumo). Muitas unidades mantiveram a correia de couro até 1813–1814 (S3).
- **Medidas:** nenhuma fonte; proporções da barretina francesa (**estimado**).

## 7. Materiais e cores (Fase 6, 2026-10-17)

O **material** de cada peça tem fonte. O **tom numérico não tem**: não há colorimetria de época nem objeto medido. Os tons abaixo são **estimativas**, coerentes com o material, e ficam para conferir no atlas do mod (⏳).

| # | Peça | Material (fonte) | Tom de partida (linear) | Brilho (_smdi G/B) | Rótulo |
|---|---|---|---|---|---|
| M1 | Corpo (1812) | Pano preto sobre couro: R1 1817, S1, S2 ("чёрное сукно") | 0,013 com trama de lã e mosqueado leve | 0,04 / 0,10 | Material provável; tom estimado |
| M2 | Corpo (1808) | Feltro preto (R1 1807) | 0,015 | 0,05 / 0,12 | idem |
| M3 | Tampo, faixas, tiras, pala, presilha | Couro envernizado: R1 1817 ("lacquered crown", tiras envernizadas), A1 (brilho visível) | 0,006, quase uniforme | 0,60 / 0,85 | Material confirmado (regulamento); tom estimado |
| M4 | Granada, rosetas, escamas | Latão ou "cobre amarelo": S2, R1 | 0,66 / 0,47 / 0,17, com **escurecimento nas cavidades** e polimento nas arestas | 0,85 / 0,72, menos no escurecido | Material confirmado; tom e desgaste estimados (decisão artística, especificação §58) |
| M5 | Cordões, borlas, raquete | Lã branca (R1 1809, 1811) | 0,74 / 0,73 / 0,68 (branco de lã, não branco puro), sujeira leve nos fundos | 0,06 / 0,15 | Material confirmado; tom estimado |
| M6 | Pompom | Lã sobre madeira (R1 1817); cores do 1º batalhão (R1 22 fev 1811): mosqueteiro branco com centro verde, granadeiro vermelho | vermelho 0,50 / 0,03 / 0,03; verde 0,03 / 0,17 / 0,06 | 0,05 / 0,12 | Cores confirmadas; tons estimados |
| M7 | Pluma | Crina preta (R1 1811) | 0,015, veios no sentido do comprimento | 0,35 / 0,55 (a crina tem brilho) | Material confirmado; tom estimado |
| M8 | Carneira | Couro marrom (convenção das barretinas do projeto) | 0,07 / 0,035 / 0,016 | 0,25 / 0,40 | **Estimado** (interior, quase invisível) |
| M9 | Forro | Linho (convenção do projeto) | 0,35 / 0,31 / 0,24 | 0,03 / 0,10 | **Estimado** |
| M10 | Haste do pompom (arame que prende o pompom ao kiver) | Ferro (convenção do blockout; nenhuma fonte mostra a haste, que fica escondida sob o pompom) | 0,09, cinza escuro | 0,55 / 0,45 | **Estimado** (quase invisível) |

**Desgaste:** só o que o uso explica: escurecimento do latão nos fundos, sujeira leve nos fundos da lã branca e variação de tom no pano. Não há arranhões nem lama (especificação §58: o desgaste se baseia em evidência ou em decisão artística explícita, e aqui é decisão).
