# HIST-RUS-INF-COAT-1812-001: casaca (мундир) da infantaria do exército russo, 1812–1814

Dossiê de pesquisa (Gate A da especificação mestre, §3–7 e §65–66; registro de referências da documentação do mod, §8.3 e §17.3).
Versão 1.0, 2026-10-17. Todas as páginas foram abertas em 2026-10-17.

| Campo | Valor |
|---|---|
| Identificador | `HIST-RUS-INF-COAT-1812-001` (mosqueteiros e granadeiros; mesma casaca) |
| Nome histórico | мундир (casaca de uniforme), de abotoamento duplo |
| Período | Corte da tabela de 30 abr 1802, com as mudanças de 1807 a 1812; uso de 1812 a 1814 |
| Ativos ligados | `source/scripts/build_uniforme_rus.py`, `source/models/coats/hcl_uniforme_rus/`, ficha `docs/specs/rus_1812.md` §2.1, relatório `docs/reports/rus_1812_blockout.md` |
| Estado | Gate A concluído para a malha; cores e arte do mod pendentes (atlas ausente) |

Confiança, conforme a documentação do mod (§8.3): **alta** = objeto original ou regulamento; **média** = estudo ou prancha documentada; **baixa** = reconstituição moderna.

## 1. Fontes

| ID | Tipo | Fonte | Data | Confiança | Direitos |
|---|---|---|---|---|---|
| **A2** | **Objeto original** | **Museu Estatal Hermitage**: casaca de oficial do Regimento Izmailovsky da Guarda, do grão-duque Nicolau Pavlovich, **Rússia, 1812–1817** ("Мундир офицерский лейб-гвардии Измайловского полка… ГЭ"). Foto de shakko, 2012: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Nicholas_I%27s_uniform_of_the_Lifeguard_Izmaylovsky_(1812-6,_Hermitage)_01_by_shakko.jpg). **Inventário não informado** na legenda | Objeto do período | **Alta** para o corte; **oficial da Guarda** (bordado na gola e nos punhos, botões dourados) | CC BY‑SA 4.0: só pesquisa |
| **R1** | Regulamento (compilação) | Viskovatov, vol. 10 (1851), tradução de M. Conrad: [V10BAll.htm](https://marksrussianmilitaryhistory.info/V10BAll.htm), *Grenadier Regiments*: tabela de 30 abr 1802 e ordens até 1812 | 1851 × 1802–1812 | **Alta** | Citação curta |
| **P2** | Prancha | Viskovatov, **Рис. 1359**, *Мушкетеръ, 1812–1817* (ГПИБ, página `957830`) | [1881] × 1812–1817 | **Média** | ГПИБ: só pesquisa |
| **P5** | Prancha | Viskovatov, **Рис. 1357**, *Мушкетерская шапка 1805–1807* (casaca de 1805–1807; ГПИБ, página `957826`) | idem | Média | idem |
| S4 | Guia de hobby | Warlord Games (Rospond), já citado no dossiê do kiver | Moderno | Baixa | — |

## 2. Observações

### A2, casaca original de 1812–1817 (foto de frente, em manequim)
- **Abotoamento duplo fechado**: **6 pares** de botões, do pé da gola até a borda da cintura.
- **As duas fileiras ficam juntas**: centro a centro, cerca de 22 px, com passo vertical de ~40 px. Calibrando pelo passo de 2⅝" (67 mm) de R1, isso dá **~37 mm entre as fileiras**. Elas são quase paralelas.
- **Gola alta de pé**, fechada, vermelha por baixo do bordado: ~45 px ≈ **75 mm**.
- **Da gola à cintura**: ~215 px ≈ 360 mm. A frente acaba reta na cintura.
- **Abas longas** com **viradas vermelhas largas**: ~220 px ≈ **370 mm** abaixo da cintura.
- **Punho vermelho** com **portinhola verde-escura de 3 botões**.

### R1, tabela de 30 abr 1802 (homem de 6 pés) e mudanças
- Abotoamento duplo, todos os botões fechados no verão e no inverno; botões **chatos**, de latão.
- **Lapela (отворот): 3" (76 mm)**. **1º botão a ⅞" (22 mm) da gola**; **2⅝" (67 mm) entre os botões**; as casas ficam a **⅞" da borda da lapela**.
- Botões: 7 na lapela direita e 6 na esquerda. Em 19 dez 1807 caiu o 7º (correame no ombro direito). Mais 2 por punho e 1 na casa de cima da portinhola, 2 das platinas, **2 na cintura** e **1 onde as viradas de cada aba se juntam**.
- **Gola:** 3½" na frente, 4⅜" atrás (1802). **1º jan 1812: baixa, fechada na frente com colchetes.**
- **Punho:** 3"; portinhola de 1¾" × 6⅛".
- **Abas:** **15¾" (400 mm) da cintura à ponta**. Viradas de 17" × 14⅞", largas embaixo (4⅞").
- **Forro: kersey vermelho.** Em 1813, os fuzileiros navais (padrão mosqueteiro) têm gola, punhos, **viradas e forro** verde-escuros "**em vez de vermelhos**", o que confirma o vermelho na linha.
- **Bolsos: nenhum** na casaca de soldado. Só os oficiais tinham portinholas horizontais de 3 botões nas abas.

### P2, Рис. 1359 (gravura)
- 6 + 6 botões; punho com 3 botões; gola fechada.
- **As fileiras aparecem bem afastadas, cerca de 30 % do peito.** As proporções da figura são estilizadas: tronco alongado, cabeça pequena.

## 3. Interpretação e decisões

| # | Elemento | Decisão | Base | Rótulo |
|---|---|---|---|---|
| C1 | **Distância entre as fileiras** | **36 mm** entre centros, paralelas | A2 (~37 mm, objeto original) e R1 (lapela de 3" − 2 × ⅞" = 32 mm). **P2 (~100 mm) foi rejeitada**: é uma gravura estilizada, abaixo do objeto e do regulamento na hierarquia de fontes (especificação §4) | **Provável** |
| C2 | Posição dos botões | 1º par 22 mm abaixo do pé da gola; passo de 64 mm (os 67 mm de R1 × 0,96, para caberem os 6 pares até a cintura de 1,15 m, como em A2) | R1, A2 | Provável |
| C3 | Forma dos botões | Mais **chatos** (altura × 0,6 do botão da base) | R1 ("flat") | Provável |
| C4 | Gola | **70 mm na frente**, a mesma fração atrás. "Baixa" em 1812 é relativa aos 89–111 mm de 1802; A2 mostra ~75 mm | R1, A2, P2 | **Estimado** |
| C5 | Abas | 400 mm abaixo da cintura (barra a 0,74 m) | R1, A2 (~370 mm) | Provável |
| C6 | Botões das viradas | 1 por aba, embaixo, onde as viradas se juntam | R1 | Provável (a posição exata na ponta é **estimada**) |
| C7 | Cintura | 2 botões atrás (já existem na malha base) | R1 | Confirmado (regulamento) |
| C8 | Punho | Vermelho, portinhola verde-escura de 3 botões (já existem) | R1, A2, P2 | Confirmado |
| C9 | Bolsos | Nenhum | R1 | Confirmado (regulamento) |
| C10 | Cores para a pintura (Fase 6) | Verde-escuro; gola, punhos, **viradas e forro vermelhos**; portinhola verde-escura; platina pela ordem na divisão | R1 | Confirmado (regulamento); tons a medir no atlas |
| C11 | Borda da frente (Fase 4, 2026-10-18) | A borda da frente que se sobrepõe fica **22 mm (⅞") fora da fileira** do lado direito de quem veste (x = −40 mm). Na malha prussiana herdada, o degrau do fecho ficava **entre** as duas fileiras, como num fecho simples | R1 (lapela de 3" com as casas a ⅞" da borda) | Provável (o lado da sobreposição segue o da malha base; nenhuma fonte vista mostra o lado) |
| C12 | Polainas até o joelho (Fase 4/6) | Pintadas na perna da calça até h 0,52 m, com bainha virada no alto e a tira de botões continuando para cima, no passo dos botões modelados (6 botões pintados). A calça sobre a polaina curta deixou de franzir e ficou rente à polaina modelada | R1 (1 jan 1812) | Confirmado (regulamento); acabamento estimado |
| C13 | Debrum | **Nenhum** na casaca de soldado (frente, portinhola, gola): nenhuma fonte do dossiê o cita. A borda da frente tem só a bainha enrolada no relevo | R1 (a tabela de 1802 não cita debrum) | Provável; **conferir** na foto de A2 e no atlas |

## 4. Registro de incertezas

| # | Questão | Interpretações | Risco | Implementação | Evidência que falta |
|---|---|---|---|---|---|
| I1 | Distância entre as fileiras | A2 e R1: ~32–37 mm. P2 e P5 (gravuras): bem afastadas | Médio (leitura da frente) | 36 mm (C1) | Uma casaca de **soldado** do exército em museu; o atlas do mod |
| I2 | Altura da gola de 1812 | R1: "baixa" (sem medida). A2: ~75 mm (oficial da Guarda, 1812–1817) | Baixo | 70 mm (C4) | Medida de um objeto |
| I3 | A2 é de oficial da Guarda | O corte é o mesmo; bordados e botões dourados são próprios do oficial | Baixo | Só o corte é usado | — |
| I4 | Escala medida na foto de A2 | Calibrada pelo passo de 67 mm de R1; manequim e perspectiva | Médio | Proporções, não medidas absolutas | Ficha do Hermitage com dimensões |
