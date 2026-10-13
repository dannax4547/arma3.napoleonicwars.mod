# Ficha Técnica: Uniforme de Infantaria de Linha Prussiana, 1813

Fase 2 do pipeline. Versão 1.1, 2026-10-10. **Estado: aprovada pelo usuário ("aprovo") em 2026-10-10**, com as recomendações de U2–U6; U1 e U7 continuam pendentes (§10). Blockout: `docs/reports/uniforme_pruss_blockout.md`.

Protótipo iniciado a pedido do usuário ("inicia a modelagem das roupas"). A barretina fica **pausada na Fase 6** (aguarda aprovação; Fases 7–9 pendentes).

Legenda: ✅ confirmado · 🔶 provável, ou medido com ressalvas · ❓ incerto/não documentado · 🎮 visto na textura do mod (autorização declarada pelo usuário)

---

## 1. O que é um "uniforme" no ARMA 3 (verificado nos Samples)

No ARMA 3 o uniforme **não é uma peça solta**: é o **corpo inteiro** do personagem, menos a cabeça. Verificado em `Arma 3 Samples\Addons\Test_Character_01`:

| Fato | Evidência |
|---|---|
| O item de uniforme (`U_Test_uniform: ItemCore`, `ItemInfo: UniformItem`) aponta para uma classe de soldado (`uniformClass = Test_Soldier_base_F`); é essa classe que tem o `model` | `cfgUniforms.hpp`, `config.cpp` linha 67–70 |
| O modelo do soldado (`A3_character_example.p3d`) contém tronco, braços, mãos, pernas e pés | Renders `docs/reports/img/uniforme/ref_corpo_exemplo_*.png` |
| A cabeça vem da identidade do personagem por um proxy (`proxy:\A3\characters_f\Heads\bysta.001`) | Seleções do LOD 0 |
| O `A3_character_template.p3d` traz só as partes que um uniforme novo reaproveita: **antebraços, mãos e pernas** (pele, seleção `hl`) e todos os LODs técnicos | Render `ref_corpo_template_frente.png`; tabela §8 |
| A licença dos Samples permite abrir e modificar os exemplos para conteúdo **não comercial do ARMA 3** | `readme.txt` dos Samples |

Consequência para o projeto: o protótipo "roupas" é **um único modelo** com **casaco + calças + polainas + sapatos**, mais as **mãos do template oficial** (as únicas partes de pele visíveis). Correame, mochila e barretina são itens separados.

## 2. Identificação

| Item | Valor | Confiança |
|---|---|---|
| Peça | Uniforme de infantaria de linha (mosqueteiro), casaco curto com abas (*Kollet*; na infantaria prussiana o nome oficial continuava *Rock*) | ✅ forma (🎮); terminologia em [S4] |
| Estado e período | Prússia, campanhas de 1813–1815 (Guerras de Libertação) | Escopo do projeto; atlas do mod `prussia1813_*` |
| Variante de partida | A do atlas `prussia1813_01` do mod: gola e punhos **vermelhos**, platina **branca** com debrum vermelho, botões **de latão** | 🎮 |
| Regimento | **Não identificado.** Pela regra do projeto, o nome da variante segue o Eras Mod; **falta o nome que o mod dá a esta unidade** (U1) | ❓ |
| O que as cores indicam (fonte secundária) | Gola e punhos na **cor da província** (Brandemburgo = vermelho, Pomerânia = branco, Silésia = amarelo, Prússia Oriental = vermelho-tijolo, Prússia Ocidental = carmim); platina na cor da **antiguidade do regimento** dentro da província (branca, vermelha, amarela, azul-claro) | 🔶 [S1] (resumo de página de fabricante de miniaturas; nenhum texto do regulamento foi lido) |

Pela combinação de [S1], "vermelho + platina branca" corresponderia ao regimento mais antigo de Brandemburgo. **Isso é inferência, não confirmação**, e não entra em nome de classe nem em texto do addon.

## 3. Referências

| ID | Arquivo / fonte | Uso | Autorização |
|---|---|---|---|
| M1 | `docs/references/img/ref_uniforme_01_casaco_frente_mod.png` (atlas `prussia1813_01_diffuse.dds`, bloco col. 0, lin. 1) | **Principal**: frente do casaco, botões, debrum, abas, punho com pala, platina | Declarada pelo usuário em 2026-10-09 (detalhes pendentes) |
| M2 | `ref_uniforme_02_casaco_costas_mod.png` (bloco col. 7, lin. 0) | Costas de um casaco do mesmo atlas: 2 botões na cintura, pregas das abas, gola vermelha planificada. **Não confirmado** que seja o mesmo casaco de M1 (o azul é mais escuro e não há debrum) | idem |
| M3 | `ref_uniforme_03_calcas_cinza_polainas_mod.png` (bloco col. 0, lin. 0) | Calças cinza com polainas pretas abotoadas | idem |
| M4 | `ref_uniforme_04_calcas_brancas_mod.png` (bloco col. 2, lin. 0) | Calças brancas com polainas pretas (variante) | idem |
| S1 | [Gripping Beast / Calpe: Line Musketeers](https://grippingbeast.co.uk/Line_Musketeers--category--1139.html) | Cores provinciais, platinas, abas vermelhas, calças cinza dentro das polainas pretas | Leitura direta bloqueada (403, não contornada); usado só o resumo do buscador |
| S2 | [Gripping Beast: British Manufactured Uniforms](https://www.grippingbeast.co.uk/British_Manufactured_Uniforms--category--1158.html) | Contraste: unidades com uniformes britânicos (fora do escopo) | Só resumo |
| S3 | [Richard Knötel (Wikipedia)](https://en.wikipedia.org/wiki/Richard_Kn%C3%B6tel) | Pranchas *Uniformenkunde* (domínio público) como fonte primária a consultar | — |
| S4 | [Koller (Uniform), dewiki](https://dewiki.de/Lexikon/Koller_(Uniform)) | Terminologia *Kollet* × *Rock* | — |
| Sugerida | P. Hofschröer, *Prussian Line Infantry 1792–1815* (Osprey) e pranchas de Knötel | Fecharia os itens ❓ (contagem de botões, bolsos, polainas) | **Não consultada**; o usuário pode fornecer |

Os blocos do atlas são **texturas planificadas** (UV), não fotos: dão cores, peças e detalhes, mas **não dão comprimentos** com segurança.

## 4. Vistas disponíveis

| Vista | Disponível | Consequência |
|---|---|---|
| Frente do casaco | ✅ M1 (planificada) | Botões, debrum, gola, cinto pintado |
| Costas | 🔶 M2 (associação não confirmada) | Botões da cintura, pregas |
| Lateral / perfil das abas | ❌ | **Comprimento e caimento das abas não medidos** (U3) |
| Calças e polainas | ✅ M3, M4 (planificadas) | Cores, abotoamento lateral |
| Sapatos | 🔶 peças escuras em M4 | Forma não confirmada |

Uma captura do mod com o soldado de frente, de lado e de costas fecharia U3 e confirmaria M2.

## 5. Componentes, cores e materiais

Cores: média medida no atlas M1/M3 (sRGB). A textura do mod tem sombra embutida, por isso os valores são escuros; a cor final de albedo será calibrada na Fase 6.

| Componente | Descrição | Cor média no mod | Material | Confiança |
|---|---|---|---|---|
| Casaco: corpo e mangas | Azul prussiano muito escuro, quase preto | #151E2D | Lã (pano) | ✅ cor [S1] + 🎮 |
| Gola | Alta e fechada, na cor provincial | Vermelho, #48111A–#52111A | Lã | ✅ existência; cor 🎮 |
| Fecho e botões da frente | Debrum vermelho ao longo da borda; **o mod mostra duas colunas de 7 botões acima do cinto**. As fontes secundárias lidas não dão a contagem. A descrição corrente do casaco prussiano de 1813 é de fila única (8 botões), mas **nenhuma fonte consultada confirma isso** | Latão | Metal | 🎮; contagem histórica ❓ (U4) |
| Punhos | Tipo **brandemburguês**: punho vermelho com **pala azul de 3 botões** | Vermelho, pala azul | Lã | 🎮 (visível no mod) |
| Platinas (ombros) | Brancas com debrum vermelho, um botão junto à gola | Branco acinzentado (amostra parcial #8B8885) | Lã | 🎮; sistema de cores 🔶 [S1] |
| Abas (*Schöße*) com viradas | Viradas vermelhas para todos os regimentos | Vermelho | Lã | ✅ [S1] + 🎮 |
| Costas | 2 botões na cintura, pregas das abas | — | — | 🔶 M2 |
| Bolsos das abas | Linhas no mod sugerem bolsos verticais | — | — | ❓ |
| Calças | Cinza, por dentro das polainas | #575452 | Lã | ✅ [S1] + 🎮 |
| Polainas | Pretas, abotoadas do lado de fora, até abaixo do joelho | #242222, botões de latão | Pano/couro | 🔶 🎮 (altura exata ❓) |
| Sapatos | Baixos, pretos | Preto | Couro | ❓ forma |
| Gravata de pescoço (*Halsbinde*) | Preta, visível acima da gola? | — | — | ❓ (não aparece com clareza no mod) |
| Cinto branco com fivela de latão | **Pintado sobre o casaco no mod** | — | Couro branqueado | 🎮; ver U5 |
| Mãos | Do template oficial (pele pela seleção `hl`) | Pele da identidade | — | ✅ Samples |

## 6. Medidas do corpo oficial (para o encaixe)

Medidas no `A3_character_example.p3d` (LOD 0) com `source/scripts/inspect_character_ref.py`. **Origem do `.p3d` a 1,007 m do chão**; alturas abaixo são a partir do chão. Pose em "A", braços a ~42° da vertical.

| Ponto | Altura (m) | Largura × profundidade (m) | Origem |
|---|---:|---|---|
| Topo do pescoço (início da cabeça-proxy) | 1,580 | — | seleção `Neck` |
| Testa (encaixe da barretina) | 1,725 | — | barretina, Fase 3 |
| Linha dos ombros (com deltoide) | 1,47–1,50 | 0,54–0,57 | seção |
| Axila (braço se separa do tronco) | ~1,37 | — | seção |
| Peito | 1,30 | 0,342 × 0,259 | seção |
| Cintura (mais estreita) | 1,15–1,20 | 0,308 × 0,217 | seção |
| Quadril | 0,95 | 0,350 × 0,241 | seção |
| Gancho (virilha) | ~0,80 | — | fim da seleção `camo` do exemplo (z −0,210) |
| Joelho | ~0,50 | — | limite `LeftUpLegRoll`/`LeftLeg` |
| Início do pé | 0,19 | pé 0,107 × 0,274 | seleções `LeftFoot`/`LeftToeBase` |
| Punho (pulso) | ~1,03 | x ≈ ±0,58 | seção do braço |

Altura total com a cabeça-proxy: ~1,83 m (topo da cabeça usado na barretina: z 0,826).

## 7. Proporções propostas para a roupa

Medidas de partida para o blockout. Todas **propostas** (🔶): as fontes não dão medidas, e o mod é planificado.

| Medida | Valor | Observação |
|---|---|---|
| Folga do casaco sobre o corpo | 10–15 mm no tronco, 15–20 mm nas mangas | Evita atravessar o corpo nas animações |
| Altura da gola | 0,055 m | Gola alta fechada; **risco de atravessar o queixo da cabeça-proxy** (teste no jogo) |
| Costura da cintura do casaco | 1,12 m | Logo abaixo da cintura natural |
| Barra das abas | 0,70 m (meio da coxa) | **U3**; sem vista lateral no mod |
| Botões da frente | ⌀ 18 mm; punhos e platinas ⌀ 13 mm | Escala da textura desconhecida |
| Punho brandemburguês | altura 0,075 m; pala 0,11 × 0,04 m | Proporção lida no mod |
| Platina | 0,13 × 0,05 m | Proporção lida no mod |
| Folga das calças | 15–25 mm | Calça de lã reta |
| Topo das polainas | 0,42 m (logo abaixo do joelho) | 🎮 proporção do bloco M3; confirmar |
| Sapato | Sola plana **no chão**, 8 mm de folga sobre o pé | Corrigido na v1.1: a sola não pode descer abaixo do chão do personagem (pé a 1,007 m abaixo da origem) |

## 8. Requisitos do ARMA 3 para este modelo (verificados)

Fonte: leitura direta dos `.p3d` MLOD dos Samples (`p3d_mlod_inspect.py`, `inspect_weights.py`), `model.cfg` e `config.cpp` dos Samples.

### 8.1 LODs

| LOD | Exemplo oficial | No nosso modelo |
|---|---|---|
| Resolução 1 / 2 / 3 / 4 | 6.235 / 3.127 / 1.998 / 894 faces; `LODNoShadow=1` | **Modelados por nós** (roupa + mãos do template) |
| View Pilot (1100) | Praticamente a Resolução 1 (3.291 pontos × 3.158) | Cópia da nossa Resolução 1 |
| Shadow Volume 0 e 10 | 779 e 264 faces | **Feitos por nós** (fechados, simples) |
| Geometry, Memory, Land Contact, Hit-points, Fire Geometry | Idênticos no exemplo e no template | **Reaproveitados do template sem mudança** |

### 8.2 Seleções (Resolução 1 do exemplo)

- **Ossos**: 65 seleções com os nomes de `OFP2_ManSkeleton` (`Pelvis`, `Spine`…`Spine3`, `Neck`, `Head`, braços, mãos e dedos, pernas, pés). `Camera` e `neck1` não são usados.
- **`camo`**: as faces do uniforme. No config: `hiddenSelections[] = {"Camo", "insignia"}`.
- **`hl`**: a pele (mãos). Recebe a textura de pele da identidade.
- **`injury_body`, `injury_hands`, `injury_legs`**: áreas de dano. `insignia`: emblema no braço esquerdo.
- **Proxies**: `weapon`, `pistol`, `binoculars`, `launcher`, `flag`, `equipment`, `backpack`, `glasses`, `headgear`, `hmd` e a cabeça `bysta`. Ficam onde o template os põe.

### 8.3 Pesos (skinning)

| Fato medido no exemplo (Resolução 1) | Valor |
|---|---|
| Ossos por vértice | 1 osso: 791; 2: 1.585; 3: 651; 4: 76. **Máximo observado: 4** |
| Codificação do peso no `.p3d` MLOD | Um byte por ponto: `1` = peso total; os demais seguem **peso = (256 − byte) / 255** (pares 243/14, 230/26 e 194/63 somam 1,0) |

Na prática, os pesos são pintados no Blender e convertidos na exportação. O procedimento exato de importação no Object Builder é o teste B1, que continua pendente.

### 8.4 Configuração (modelo dos Samples; montada só na Fase 8)

- `CfgVehicles`: classe de soldado `HCL_...` com `model`, `uniformClass`, `hiddenSelections`, `hiddenSelectionsTextures`, `nakedUniform = "U_BasicBody"` e `class Wounds`. Herda de um soldado do jogo verificado, com `scope = 1`, **sem facção nova** (D4/D5 continuam pendentes).
- `CfgWeapons`: `HCL_U_...: Uniform_Base` (ou `ItemCore`, como nos Samples), com `ItemInfo: UniformItem { uniformModel = "-"; uniformClass = ...; containerClass = SupplyXX; mass = ... }`.
- `model.cfg`: `class <nome_do_p3d>: ArmaMan {}` (esqueleto `OFP2_ManSkeleton`, seções que incluem `Camo`, `hl`, `insignia`).

### 8.5 Orçamento proposto

| Resolução | Triângulos (proposta) | Base |
|---|---:|---|
| 1 | ≤ 12.000 | Exemplo: 6.235 faces num corpo liso; o casaco tem abas, gola, punhos e botões |
| 2 / 3 / 4 | ~50% / ~30% / ~15% | Mesma proporção do exemplo (6.235 → 3.127 → 1.998 → 894) |

## 9. Riscos técnicos

| Risco | Mitigação |
|---|---|
| Abas atravessando as coxas ao correr, agachar ou deitar | Pesos das abas misturando `Pelvis` e `LeftUpLeg`/`RightUpLeg`; teste no jogo (G) |
| Gola alta atravessando o queixo ou a jugular da barretina | Gola a 0,055 m; teste no jogo com rostos diferentes |
| Mangas e punhos contra as mãos do template | Costura no pulso, sobre a borda da malha das mãos |
| Botões em geometria custam polígonos | Só os botões da frente, punhos e platinas em geometria na Resolução 1; nas outras, só textura |
| Calças e polainas nos joelhos dobrados | Folga e pesos `LeftLeg`/`LeftUpLegRoll` |

## 10. Decisões pedidas ao usuário

| # | Pergunta | Recomendação |
|---|---|---|
| U1 | Nome da unidade que o Eras Mod dá ao atlas `prussia1813_01` (gola e punhos vermelhos, platina branca) | Você informa; até lá a variante fica `HCL_U_Pruss1813_01` (nome técnico, sem regimento) |
| U2 | Calças **cinza** (M3) ou **brancas** (M4) no protótipo | **Cinza**; brancas viram variante |
| U3 | Comprimento das abas | **Meio da coxa (0,70 m)**, a confirmar com captura do mod |
| U4 | Botões da frente: **duas colunas de 7, como no mod**, ou fila única | **Como no mod** |
| U5 | Cinto branco: pintado no casaco (como no mod) ou **item separado (colete) depois** | **Item separado**: o casaco sai sem cinto, e o correame vira um protótipo próprio |
| U6 | Gravata preta acima da gola | **Não**, até haver referência |
| U7 | Autorização do Eras Mod: quem autorizou e por qual meio (para `references.md` §3.2) | Você informa |

**Respostas (2026-10-10):** o usuário aprovou as recomendações. U2 = cinza; U3 = meio da coxa (0,70 m); U4 = como no mod (duas colunas de 7); U5 = cinto como item separado; U6 = sem gravata. **U1** (nome da unidade no mod) e **U7** (detalhes da autorização) seguem pendentes; até lá vale o nome técnico `HCL_U_Pruss1813_01`.
