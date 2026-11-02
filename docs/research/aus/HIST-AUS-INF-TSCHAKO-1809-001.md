# HIST-AUS-INF-TSCHAKO-1809-001: tschako de 1806 e barretina de pele dos granadeiros austríacos, 1809

Dossiê de fontes da peça. Mesmo padrão e mesmas fontes de `HIST-AUS-INF-COAT-1809-001.md` (ACE, EMB, WS, NAP). Criado em 2026-11-01.

Fonte extra: **HG**, [Tschako (heeresgeschichten.at)](https://www.heeresgeschichten.at/adjustierung/infanterie/kopfbedeckungen/tschako/tschako1.htm). Dá só a história geral: introduzido em 1806, alto e mais largo em cima. Os detalhes são dos modelos de 1871 e 1891, fora do período.

## 1. Tschako de 1806

### 1.1 O que as fontes dizem

- **Ordem de 18 ago 1806**, primeiro nos regimentos húngaros. O capacete (Kasket de 1798) continuou em uso, e alguns regimentos ainda o usaram em 1809 (WS, EMB). NAP: os alemães usaram o tschako na campanha de 1809.
- **Material:** pano preto, ou pano sobre couro (WS, NAP). **24 dez 1810:** passa a feltro (WS).
- **Altura:** **8 polegadas** (WS, EMB). NAP: **20,5 cm**.
  - Na polegada de Viena (Zoll, 26,34 mm), 8" = **211 mm**. Na inglesa, 203 mm. Os 20,5 cm de NAP ficam no meio: as fontes concordam em torno de 205–211 mm.
- **Forma:** o topo é **1 polegada mais largo** que a base (WS); o tampo fica ~½" abaixo da borda (EMB).
- **Pala:** de couro envernizado, com **3 polegadas** de largura (WS, ~79 mm). EMB: **pala na frente e atrás**.
- **Bordas:** tira de couro preto em cima e embaixo, de ~2" (WS).
- **Cocar e pompom:**
  - cocar amarelo e preto na frente, preso por **botão e presilha de latão** (WS);
  - em cima, **pompom de lã amarelo com centro preto** (WS, EMB);
  - oficiais: pompom maior, de ouro e preto (EMB).
- **Barbicacho** de couro preto (WS). Capa de lona preta para chuva (WS).
- **Sem placa** na frente: nenhuma fonte cita placa ou águia antes dos modelos posteriores.

### 1.2 Decisões propostas

| # | Item | Proposta | Rótulo |
|---|---|---|---|
| T1 | Malha | **Nova** (`blockout_tschako_aus.py`), partindo do perfil da barretina francesa: corpo tronco-cônico invertido, tampo rebaixado, pala na frente e atrás | Solução de produção |
| T2 | Altura | **208 mm** (média de 8" e 20,5 cm) × fator de encaixe | 🔶 |
| T3 | Topo | Diâmetro da base + 26 mm | 🔶 (WS) |
| T4 | Pala da frente | 79 mm; pala de trás menor (~40 mm, estimada) | 🔶 / ❓ |
| T5 | Frente | Cocar amarelo-preto, presilha e botão de latão, pompom amarelo de centro preto. Sem placa | 🔶 |
| T6 | Kasket de 1798 | **Fora do 1º lote** | Decisão de escopo |

## 2. Barretina de pele dos granadeiros

### 2.1 O que as fontes dizem

- Só a companhia **velha** de granadeiros usa a barretina de pele; a nova usa a cobertura dos fuzileiros (WS, NAP, ACE).
- **Placa de latão** na frente (EMB, NAP).
- **Altura:** **30 cm na frente, 12,5 cm atrás** (NAP).
- **Pala:** EMB fala em "duas palas parecidas com as do tschako" ❓.
- **Atrás:** o pano do topo, o **"Lehnstuhlmützl"**, **na cor da vista**, com **galão branco** (EMB).
- **Pompom amarelo e preto do lado direito** (EMB).
- Em campanha, a pele ia coberta por uma capa (NAP).
- Os granadeiros de 1809 ficavam destacados em **batalhões de granadeiros** (21 em 1809, segundo a Wikipedia; ACE tem um capítulo sobre eles). Cada batalhão juntava companhias de vários regimentos, e cada companhia mantinha a vista do seu regimento.

### 2.2 Decisões propostas

| # | Item | Proposta | Rótulo |
|---|---|---|---|
| G1 | Malha | **Nova** (`blockout_grenadiermuetze_aus.py`): frente alta de 300 mm caindo a 125 mm atrás, pala curta, placa de latão em relevo | 🔶 |
| G2 | Placa | Desenho estimado (águia dupla sobre troféu), ~120 mm de altura | ❓ (nenhuma fonte descreve o desenho) |
| G3 | Saco de trás | Na vista do regimento, com galão branco: **4 texturas** (IR 1, 3, 2, 39) | 🔶 (EMB) |
| G4 | Pompom | Amarelo e preto, do lado direito | 🔶 (EMB) |

## 3. Incertezas

- **F1:** o perfil do tschako (quanto alarga; tamanho da pala de trás).
- **F2:** desenho e tamanho da placa dos granadeiros.
- **F3:** se a barretina de pele tem mesmo duas palas (EMB, fonte única).
- **F4:** quais dos 4 regimentos ainda usavam o Kasket em 1809.
