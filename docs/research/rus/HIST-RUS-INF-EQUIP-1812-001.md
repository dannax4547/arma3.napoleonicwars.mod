# HIST-RUS-INF-EQUIP-1812-001: correame, cartucheira, tesak e mochila da infantaria russa, 1812

Dossiê de fontes da peça, padrão da especificação mestre (hierarquia de fontes: original > regulamento > prancha > réplica; rótulos de confiança; registro de direitos). Criado em 2026-11-01 para a pendência RU10.

## 1. Fontes

| ID | Tipo | Referência | Data | Confiança | Direitos |
|---|---|---|---|---|---|
| **R1** | Regulamento (compilação de arquivo) | A. V. Viskovatov, *Историческое описание одежды и вооружения российских войск*, vol. 10, 1851; tradução inglesa de Mark Conrad, 1993 ([V10BAll.htm](https://marksrussianmilitaryhistory.info/V10BAll.htm)), seções *Grenadier Regiments* e *Musketeer Regiments* | Ordens de 1802 a 1812 | **Alta** para as ordens; a tradução é de terceiro | Só trechos curtos citados |

Nenhuma peça original de 1812 foi identificada em museu (⏳ busca no Goskatalog). As pranchas do Viskovatov (ГПИБ) não foram vistas para o equipamento.

## 2. O que as fontes dizem

As ordens de granadeiros de 1802 e 1808 foram estendidas "com a mesma força" aos regimentos de mosqueteiros (R1, seção *Musketeer Regiments*).

- **Correias (30 abr 1802):**
  - bandoleira da cartucheira com 3¾" (95 mm), com vivos;
  - talim (cinturão do sabre) de **camurça branqueada**, 2" (51 mm), fivela de latão e dois passadores (sabre e baioneta).
- **19 dez 1807:**
  - o talim passa a ir **sobre o ombro direito**, sob a bandoleira, cruzando-a com a mesma largura;
  - as duas correias são costuradas nas bordas e cortadas com uma leve curva.
- **8 abr 1809:** o lado vermelho da bandoleira do mosquete é laqueado "para não manchar a bandoleira da cartucheira", que portanto continua branca.
- **Cartucheira:**
  - **30 abr 1802:** placa de latão, com 4 granadas nas companhias de granadeiros e só a placa nas de fuzileiros;
  - **14 jul 1808:** **couro preto polido**, menor que antes, tampa de **10" × 7½"** (254 × 190 mm), com o **distintivo de granada do kiver**: três chamas nas companhias de granadeiros, uma nas de fuzileiros (mosqueteiros).
- **Tesak:**
  - **30 abr 1802:** lâmina de cutelo, punho de latão, bainha de **couro não enegrecido**;
  - **19 dez 1807:** novo punho de guarda larga em concha; a bainha da baioneta encaixa no passador, paralela ao tesak.
- **Mochila (ранец):**
  - **14 jul 1808:** **retangular, de couro preto**, sem forro de lã, em duas correias de camurça branqueada de 2⅝" (67 mm) presas a grandes botões de madeira. O cantil vai em cima, no meio, com correias brancas;
  - **20 abr 1809:** as correias do capote, da mochila e do cantil **não são mais branqueadas**. A esquerda passa por cima do capote enrolado, e uma terceira correia no peito é acrescentada;
  - **24 set 1810:** as correias são costuradas nas bordas, com curva nos ombros.
- **Capote (14 jul 1808, 20 abr 1809):** vai **enrolado no ombro esquerdo** (rolo de 6½", 165 mm), não na mochila.

## 3. Decisões

| # | Item | Decisão | Fonte | Rótulo |
|---|---|---|---|---|
| E1 | Malha | A do correame e da mochila franceses (`build_equipamento_producao.py nacao=fr`), retexturizada, como o Reino Unido (K4) | — | Solução de produção |
| E2 | Bandoleira e talim | Camurça **branqueada**, cruzados no peito | R1 (1802, 1807, 1809) | Confirmado |
| E3 | Cartucheira | **Couro preto polido** | R1 (1808) | Confirmado. Tamanho: a malha francesa tem 208 × 130 mm, menor que os 254 × 190 de R1 (limitação) |
| E4 | Distintivo | **Granada de latão** no lugar da placa francesa: **1 chama** (mosqueteiros) ou **3 chamas** (granadeiros); duas texturas do colete | R1 (1808) | Confirmado; desenho e tamanho **estimados** (cabem na placa de 60 × 38 mm) |
| E5 | Bainha do tesak | Couro **natural** (castanho), ponteira e bocal de latão | R1 (1802) | Provável: a ordem de 1807 não descreve a nova bainha |
| E6 | Mochila | Toda de **couro preto**. A tampa de pele de bezerro francesa vira couro preto com borda costurada | R1 (1808) | Confirmado |
| E7 | Correias da mochila | Couro **não branqueado** (camurça natural) | R1 (1809) | Confirmado; tom **estimado** |
| E8 | Capote | **Fora da mochila.** O rolo francês sai da malha. O rolo no ombro esquerdo fica para depois (RU9) | R1 (1808, 1809) | Confirmado |

## 4. Incertezas e limitações

| # | Dúvida | Impacto | Decisão provisória | Para resolver |
|---|---|---|---|---|
| F1 | Cantil de ferro em cima da mochila (1808) | Baixo | Não modelado | Malha própria no 2º lote |
| F2 | Terceira correia no peito (1809) e botões de madeira | Baixo | Não modelados | Idem |
| F3 | Tamanho da cartucheira (254 × 190 mm em R1) | Baixo | Malha francesa | Escala da peça no 2º lote |
| F4 | Desenho exato da granada do distintivo | Baixo | Granada do kiver simplificada | Pranchas do Viskovatov |
| F5 | Pesos | Médio | Os do correame francês (`hcl_fr_pesos.blend`), sem teste com a casaca russa nas animações | Samples (`docs/pendencias.md` §3.5) |
