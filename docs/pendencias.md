# Pendências: tudo o que falta fazer

Atualizado em 2026-11-01 (RU10 feita: correame e mochila). Arquivo único, pedido pelo usuário (*"cria um arquivo para tudo que tem que ser feito"*).
- **O que tem aqui:** as pendências da Rússia (em andamento) e da Áustria (planejada).
- **O que não tem:** as decisões antigas da Prússia, França e Reino Unido, que continuam em `docs/plan.md` §6 (D7–D12, U1, U7, V-A…V-E).

Legenda: **[Você]** = só o usuário pode fazer · **[Decidir]** = espera uma resposta · **[IA]** = trabalho que a IA pode fazer · **[Jogo]** = só dá para conferir no ARMA 3.

---

## 1. Bloqueios: o que depende de você

| # | O que | Por quê | Libera |
|---|---|---|---|
| B1 | **[Você]** Instalar o **Arma 3 Tools** (Steam) | Conversão PNG → PAA, empacotamento PBO, `CfgConvert`, Object Builder e Buldozer | Fase 9 inteira (§3.6) |
| B2 | **[Você]** Instalar o **Arma 3 Samples** (Steam) | Template oficial de personagem e de cabeça, cabeça do jogo (`bust.p3d`) e animações RTM para o teste de movimento | §3.5 |
| B3 | **[Você]** Copiar a **pasta de referências do Eras Mod** (atlas Reto, `rus1812INF` e `rus1812INF2`) | Conferir os tons e os detalhes contra a arte do mod | §3.4 |
| B4 | **[Você]** **GitHub congelado:** nada de commit, push, PR ou issue até o seu aviso (`CLAUDE.md`, ticket #4871031) | Conta sinalizada pelos sistemas antiabuso | Commits de todo o trabalho (§6) |
| B5 | **[Você]** Acesso de escrita ao repositório `dannax4547/arma3.napoleonicwars.mod`, ou um fork (decisão G4) | A conta só tem leitura | Push, depois do B4 |
| B6 | **[Você]** Autorização do atlas LME4 `austrialme` (F7, decisão AT3) | Só abrir se a autorização cobrir o LME4 | Arte de referência da Áustria |

## 2. Decisões que esperam você

| # | Pergunta | Recomendação | Onde |
|---|---|---|---|
| RU5 | Portinhola do punho com 1 botão (1802) ou 3 (prancha 1359, [WG]) | **3** (feito); confirmar no atlas | Ficha §9 |
| A-K | Aprovar o **kiver**: P3D, LODs, sombra, camo e `.rvmat` | Aprovar ou pedir ajuste | `docs/reports/kiver_rus_p3d.md` |
| A-C | Aprovar a **casaca**: malha, texturas, pesos, P3D e config | Aprovar ou pedir ajuste | `docs/reports/uniforme_rus_texturas.md`, `uniforme_rus_p3d.md`, `rus_config.md` |
| A-G | Aprovar o **capote** (malha, texturas, pesos, P3D e config) e as correções dos **granadeiros** | Aprovar ou pedir ajuste | `docs/reports/capote_granadeiros_rus.md`, `capote_rus_p3d.md` |

## 3. Rússia, 1º lote (RU2): o que falta

### 3.1 Capote: Fases 7 e 8 **[feito]**

- [x] Pesos (por posição, do capote francês), LODs Res 2–4, P3D, `.rvmat` e config (4 soldados e 4 uniformes de capote). Relatório: `docs/reports/capote_rus_p3d.md`.
- [ ] **[Decidir]** Orçamento: 13.900 triângulos contra a meta de 12.000. Reduzir a saia (2 × 1.856)?

### 3.2 Correame e mochila (RU10) **[feito]**

- [x] Dossiê `docs/research/rus/HIST-RUS-INF-EQUIP-1812-001.md` (V10B): correias branqueadas; cartucheira preta com a granada do kiver (1 chama mosqueteiros, 3 granadeiros, 14 jul 1808); bainha natural; mochila toda preta em correias não branqueadas (1809); capote fora da mochila.
- [x] Malha francesa retexturizada: 2 coletes, 1 mochila (sem o rolo do capote), P3D, `.rvmat` e config. Relatório: `docs/reports/equipamento_rus.md`.
- [ ] (2º lote) Cantil, terceira correia no peito e cartucheira no tamanho de 1808 (254 × 190 mm).

### 3.3 Granadeiros **[IA]**

- [x] Kivers de granadeiro (12 classes no config) e platina vermelha dos regimentos de granadeiros (R01/C01).
- [ ] (Opcional) Classes de soldado "granadeiro" já com o kiver de granadeiro em `linkedItems`.
- [x] Granadas da cartucheira (colete `HCL_V_RUS1812_Correame_Granadeiro`, §3.2).

### 3.4 Com o atlas do mod (depois do B3)

- [ ] **[IA]** Converter os atlas (`dds_para_png.py`) e preencher o catálogo §1.1 da ficha.
- [ ] **[IA]** Conferir e ajustar os tons:
  - verde-escuro da casaca, vermelho, branco da calça, cinza do capote;
  - cores das platinas e dos pompons;
  - materiais do kiver M1–M10.
- [ ] **[IA]** Conferir:
  - RU5 (botões da portinhola);
  - C13 (debrum da casaca);
  - D18 / I6 (o "embaixo" do pompom de granadeiro);
  - os pompons por batalhão (o fórum [OP] avisa que as fontes divergem).

### 3.5 Com o Samples (depois do B2)

- [ ] **[IA]** Refazer o encaixe do kiver com o `Test_Character_01` (hoje vem do blockout britânico) e regerar as Fases 4–7 do kiver se mudar.
- [ ] **[IA]** Medir a folga do pescoço da casaca e do capote na cabeça do jogo (`diag_gola_bust.py`).
- [ ] **[IA]** Teste de movimento com as animações oficiais (`teste_movimentos.py`): abas mais curtas, frente nova, gola mais baixa, polainas até o joelho, saia do capote.
- [ ] **[IA]** Montar os P3D sobre os templates oficiais, trocando o modelo-base francês, e conferir que nada muda.
- [ ] **[IA]** `uniform_review.py` com a cabeça do jogo.

### 3.6 Fase 9: empacotar e testar (depois do B1)

- [ ] **[IA]** `build_mod_rus.ps1`, cópia do `build_mod_uk.ps1`: PNG → PAA (sufixos `_co`, `_nohq`, `_smdi`), `FileBank` com `prefix=hcl\hcl_rus`, `CfgConvert` no `config.cpp`.
- [ ] **[Jogo]** Arsenal:
  - os 4 uniformes, os 12 kivers e os capotes;
  - troca de textura por variante e por batalhão;
  - LODs à distância, sombra, movimento, brilho dos `.rvmat` (ajustar no Buldozer).
- [ ] **[Jogo]** Barbicacho e cordões do kiver na cabeça do jogo (decisão D8 do projeto).

## 4. Limitações conhecidas (melhorar se der tempo) **[IA]**

| Peça | Limitação | Relatório |
|---|---|---|
| Kiver | No Res 4 a pala dobra um pouco; sombra com 180–360 triângulos (o boné oficial tem 72) | `kiver_rus_p3d.md` |
| Kiver | Franjas das borlas com pontos escuros; pluma lisa com veios (as mechas só no relevo) | `kiver_rus_texturas.md` |
| Casaca e capote | Friso de 2–3 mm onde termina a polaina modelada; entalhe pequeno na tira de botões | `uniforme_rus_texturas.md` |
| Casaca e capote | 3 autointerseções no rolo do alto da gola (herdadas) | idem |
| Casaca | Res 4 com 13 % em vez de 10 % (mínimo de 80 triângulos por peça) | `uniforme_rus_p3d.md` |
| Capote | Comprimento e corte das costas estimados (J1); 2 + 2 autointerseções na saia (herdadas) | `capote_granadeiros_rus.md` |
| Capote | Res 4 com 15 % (piso maior nas metades da saia, que se dobravam uma através da outra) | `capote_rus_p3d.md` |
| Pintor | Desenhos em estrela no peito e nas mangas (dobras das axilas, herdadas de todas as nações) | idem |

## 5. Rússia, 2º lote, e Áustria (planejados)

- [ ] **[IA]** Rússia, 2º lote (RU2): **jäger** (casaca sem platinas, verde) e **Guarda**; capote **enrolado** no ombro (RU9; rolo de 6½", [V10B] 1809).
- [ ] **[IA]** Áustria 1809, 1º lote (AT1, AT2), seguindo as 9 fases do `plan.md`:
  - [x] ficha técnica (Fase 2, versão 1.0): `docs/specs/aus_1809.md`; dossiês `docs/research/aus/` (casaca, tschako e barretina de pele, equipamento);
  - [x] AT1–AT11 aprovadas em 2026-11-01 (ficha §9): 1809, regimentos IR 1, 3, 2 e 39, malhas novas;
  - [ ] **[IA]** fontes primárias (Teuber & Ottenfeld, HGM) para punhos, gola, placa dos granadeiros e equipamento;
  - [x] Fase 3: blockout do tschako de 1806 (`docs/reports/tschako_aus_blockout.md`);
  - [x] Fase 3: blockout da barretina de pele dos granadeiros, 4 variantes (`docs/reports/grenadiermuetze_aus_blockout.md`);
  - [x] Fase 3: casaca alemã e húngara, com a calça húngara sem polainas (`docs/reports/uniforme_aus_blockout.md`);
  - [ ] Fase 3: correame e mochila (malha francesa, AT9);
  - infantaria alemã, húngara e granadeiros (Fases 4–8).
  
  O 2º lote austríaco são Grenzer, Jäger e Landwehr. Plano: `docs/reports/plano_austria_russia.md`.

## 6. Estado do repositório

- **Nada foi commitado** (B4). Todo o trabalho da Rússia está no *working tree*:
  - scripts `source/scripts/*_rus.py`;
  - modelos em `source/models/{coats,shakos,pesos}`;
  - texturas `source/textures/hcl_{kiver,uniforme,capote}_rus`;
  - addon `source/addon/hcl/hcl_rus`;
  - documentos em `docs/{specs,research,reports,renders/rus}`;
  - mudanças em `docs/plan.md`, `source/scripts/uniform_review.py` e `source/scripts/build_uniforme_rus.py`.
- **Quando o B4 acabar:** commits em lotes pequenos, um por fase, sem rajadas.
