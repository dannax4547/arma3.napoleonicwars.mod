# Plano: Império Russo e Império Austríaco (Fase 1)

Data: 2026-10-17. Pedido do usuário: *"vai fazer a parte do império austríaco e império russo [...] planejar tudo antes de começar"*.

Este documento é o plano. **Nada foi modelado nem pesquisado a fundo ainda.** Os dados históricos da §4 são hipóteses de partida (❓). A Fase 2 confirma ou corrige cada uma com fonte, como manda a regra 3 do `plan.md`.

Legenda: ✅ verificado · 🔶 provável · ❓ hipótese, a verificar · 🎮 visto só na arte do mod · ⛔ bloqueio

---

## 1. Escopo

Igual ao resto do projeto (`plan.md` §1): **só vestimentas**. "Império Russo" e "Império Austríaco" são duas **nações de uniformes**, como a Prússia, a França, o Reino Unido e a Suíça. Ficam de fora facções, grupos de IA, missões e armas funcionais.

Serão dois addons novos, no padrão dos existentes:

| Nação | Addon | Prefixo de classe (proposto) | Período |
|---|---|---|---|
| Rússia | `hcl_rus` (`hcl\hcl_rus`) | `HCL_*_RUS1812_*` | 1812–1814 (decisão RU1) |
| Áustria | `hcl_aus` (`hcl\hcl_aus`) | `HCL_*_AUS1809_*` | 1806–1815, recorte de 1809 (decisão AT1) |

## 2. Situação desta máquina (verificada em 2026-10-17)

O trabalho anterior foi feito em outra máquina (`C:\Users\lucas`). Nesta (`C:\Users\SpartanGamerBR`):

| Item | Estado | Efeito |
|---|---|---|
| Repositório | ✅ Clonado de novo em `Workspace Github\arma3.napoleonicwars.mod` (o clone anterior parou no meio). Branch `main` = `58ba464` | — |
| Push em `dannax4547/arma3.napoleonicwars.mod` | ❌ A conta `Lucas-Belucci-Bellini` só tem leitura | Os commits ficam locais até o dono dar acesso ou aceitar um fork/PR |
| ARMA 3 | ✅ Steam, caminho padrão | Teste no jogo possível (Fase 9) |
| Blender 5.2 | ✅ `C:\Program Files\Blender Foundation\Blender 5.2`, o mesmo caminho dos scripts | As Fases 3–6 rodam aqui |
| Arma 3 Tools | ⛔ Não instalado | Sem binarização nem PBO (Fases 7–9) |
| Arma 3 Samples | ⛔ Não instalado | Sem `A3_character_template.p3d`: `build_p3d_*.py` e `build_mod_*.ps1` não rodam |
| Pasta de referências (pacotes Reto/LME4 do Eras Mod) | ⛔ Não existe nesta máquina | Sem os atlas `rus1812INF*` e `austriaINF*`: sem catálogo 🎮 nem cores medidas |
| `work/` (conversões dos atlas e builds) | ❌ Fica fora do git, então não veio no clone | Os scripts a regeneram quando as referências e as ferramentas existirem |

Os scripts usam os caminhos padrão da Steam (`build_mod_uk.ps1`, linhas 12–14). Com o Tools e o Samples instalados pela Steam (gratuitos, em Steam → Ferramentas), eles funcionam sem mudança. Pela regra 6, **quem instala é o usuário**.

## 3. O que já existe e será reaproveitado

| Peça validada | Onde | Uso na Rússia / Áustria |
|---|---|---|
| Malha de produção prussiana + gola v2 + pesos v2 | `source/models/coats/hcl_uniforme_pruss`, `pesos/` | Base das duas casacas, pelo mesmo método do francês e do britânico |
| Abas curtas e corte de 1812 | `build_uniforme_fr.py`, `build_uniforme_uk.py` | Kurtka russa de 1812; casaca austríaca |
| Capote | `build_capote_fr.py` | Capote cinza russo (muito usado em 1812) e capote austríaco |
| Chapéu de pele / tufos de pelo | `blockout_bonnet_guarda.py` | Barretina de pele dos granadeiros austríacos |
| Barretina cilíndrica, placa traçada, pompom, cordões | `blockout_shako_fr.py`, `texturizar_shako_*.py`, `trace_badge.py`, `variantes_pompom_fr.py` | Kiver russo; barretina austríaca |
| Correame cruzado e mochila | `build_equipamento_producao.py` | As duas nações (retexturizados no 1º lote) |
| Gravador de P3D, `model.cfg`, config, build do PBO | `p3d_mlod_io.py`, `build_p3d_uk.py`, `gen_config_uk.py`, `build_mod_uk.ps1` | Copiados para `_rus` e `_aus` |
| Teste de movimentos fora do jogo | `teste_movimentos.py` | As duas nações |

Regra mantida: scripts de outra nação **não são alterados**. Uso cópias `_rus` / `_aus` ou só faço import.

## 4. Conteúdo proposto (hipóteses de partida, a confirmar na Fase 2)

### 4.1 Rússia, infantaria de 1812

| Peça | Hipótese | Confiança |
|---|---|---|
| Casaca | Kurtka verde-escura de 1812, abas curtas, gola e punhos vermelhos, platinas na cor da divisão | ❓ |
| Calças | Brancas de verão ou verdes de inverno, com polainas pretas | ❓ |
| Barretina | Kiver de 1812, de topo côncavo, com granada de latão (1 chama na linha, 3 nos granadeiros), pompom e cordões | ❓ |
| Granadeiros | Kiver com sultão (pluma) preto | ❓ |
| Jäger | Verde, com debruns e cores próprias | ❓ |
| Capote | Cinza-castanho, gola na cor da vista | ❓ |
| Correame e mochila | Correias brancas cruzadas, cartucheira preta com placa, mochila de couro | ❓ |

### 4.2 Áustria, infantaria de 1809

| Peça | Hipótese | Confiança |
|---|---|---|
| Casaca | Branca, abas curtas, gola, punhos e viradas na cor da vista do regimento | ❓ |
| Regimentos alemães × húngaros | Alemães: punho redondo, calças brancas e polainas pretas. Húngaros: punho pontudo com galão, calças azul-claras justas com cordões amarelos e pretos | ❓ |
| Barretina | Tschako de 1806, de couro, mais larga em cima, com pala, cocar e pompom amarelo e preto | ❓ |
| Granadeiros | Barretina de pele com placa de latão e saco atrás | ❓ |
| Grenzer e Jäger | Casacas castanhas (Grenzer); cinza-pique com vistas verdes e chapéu "corso" (Jäger) | ❓ (2º lote) |
| Landwehr 1809 | Cinza | ❓ (2º lote) |
| Correame e mochila | Correias brancas, mochila de pele de bezerro | ❓ |

Malhas novas que cada nação exige (o resto é variação de textura):
- **Rússia:** o kiver de 1812 (topo côncavo, diferente de todas as barretinas atuais).
- **Áustria:**
  - o tschako de 1806;
  - a barretina de pele dos granadeiros, com placa;
  - as **calças húngaras**, pintadas sobre a malha da calça, como as meias do kilt britânico.

## 5. Ordem e lotes

Proponho a **Rússia antes da Áustria**, como no inventário de nações (`inventario_nacoes.md` §2). Ela é a 3ª da fila, e o kiver é a única malha nova do seu 1º lote.

| Lote | Rússia | Áustria |
|---|---|---|
| 1º | Linha (mosqueteiros), granadeiros, capote, correame e mochila | Linha alemã e húngara, granadeiros de pele, correame e mochila |
| 2º | Jäger, Guarda, oficiais e músicos | Grenzer, Jäger, Landwehr, oficiais e músicos |

Cada lote passa pelas 9 fases do `plan.md`, com aprovação do usuário entre elas:

| Fase | Entrega por nação | Precisa de |
|---|---|---|
| 1 | Este plano | Aprovação do usuário |
| 2 | Ficha técnica `docs/specs/rus_1812.md` / `aus_1809.md`, com fontes e decisões | Pesquisa (web) e, se possível, os atlas ⛔ |
| 3 | Blockout das peças novas sobre o corpo de referência | Blender ✅ e corpo do Samples ⛔ (paliativo: os `.blend` de pesos que estão no repo) |
| 4–5 | Malha de produção e revisão técnica (`mesh_review.py`) | Blender ✅ |
| 6 | UV, texturas e variantes | Atlas para medir as cores ⛔ (sem eles, as cores vêm só das fontes, marcadas 🔶) |
| 7–8 | P3D, `model.cfg`, `config.cpp` | Tools e Samples ⛔ |
| 9 | PBO e teste no jogo | Tools ⛔ e ARMA 3 ✅ |

**Com os bloqueios ainda abertos, as Fases 2 a 5 das duas nações já podem ser feitas.** O resto fica pronto para rodar.

## 6. Decisões pedidas

| # | Pergunta | Recomendação |
|---|---|---|
| G1 | Fazer as duas nações **em sequência** (Rússia → Áustria, uma por vez, como manda a regra 1) ou **em paralelo** (duas sessões, uma por nação) | **Sequência**. Paralelo só se o usuário aceitar aprovar duas coisas ao mesmo tempo |
| G2 | Copiar para esta máquina a pasta de referências do Eras Mod | **Sim**, antes da Fase 6 (de preferência antes da Fase 2) |
| G3 | Instalar o Arma 3 Tools e o Arma 3 Samples pela Steam | **Sim**, antes da Fase 7 |
| G4 | Push: pedir acesso de escrita ao dono do repositório (`dannax4547`) ou trabalhar num fork | **Acesso de escrita**. Até lá, commits locais numa branch |
| RU1 | Período russo: 1812 (kiver de 1812 e kurtka) | **1812** |
| RU2 | 1º lote russo: linha + granadeiros + capote | **Sim**. Jäger e Guarda no 2º |
| AT1 | Período austríaco: 1809 (tschako de 1806) | **1809**. Serve até 1815 com poucas mudanças |
| AT2 | 1º lote austríaco: alemães + húngaros + granadeiros | **Sim**. Grenzer, Jäger e Landwehr no 2º |
| AT3 | Atlas LME4 `austrialme`: só se a autorização (F7) cobrir o LME4 | **Não abrir** até a F7 ser resolvida |
