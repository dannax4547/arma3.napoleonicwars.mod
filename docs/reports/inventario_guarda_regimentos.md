# Inventário: Velha Guarda, novos regimentos e barretinas novas (Fase 1)

Data: 2026-10-12. Pedido do usuário: *"agora cria mais regimes para a franca e prussia com barretinas novas e na franca inicia a velha guarda tudo de uma forma profissional e com bastante detalhe nos modelos"*.

Foram lidos só os atlas **Reto** (autorizados) convertidos em `work/ntw/<nação>/`, em recortes de 512 px. O pacote LME4 tem um atlas `imperial_guardsb`, mas ele **não foi aberto**, porque a autorização do LME4 não está confirmada (F7).

Legenda: 🎮 visto no mod · ✅ fonte citada · 🔶 suposição ou fonte fraca · ❓ desconhecido.

## 1. Velha Guarda: o que os atlas Reto já trazem

**Achado principal:** o chapéu de pele (*bonnet à poil*) **está nos atlas Reto**. Não é preciso usar o LME4. Referência: `docs/references/img/ref_fr_07_bonnet_a_poil_mod.png`.

| Peça | Onde | O que mostra | Confiança |
|---|---|---|---|
| Pele preta | `FranceINF` c1–c2 r4, `FranceINF_3` c1 r4–r5 | Tufos de pelo preto com recorte (alfa), para cartões de pelo | 🎮 |
| Topo (*calot*) | `FranceINF` c2 r4, `FranceINF_3` c1–c2 r5 | Disco vermelho com **granada branca**, cercado de pelo | 🎮 |
| Placa frontal | `FranceINF` c2 r4 | Placa de latão com **águia entre granadas**, ponta embaixo, borda superior trançada prateada | 🎮 |
| Cordões e raquetes | `FranceINF` c1 r4 (vermelhos), c2 r4 (brancos) | Raquete trançada, borlas e franja | 🎮 |
| Pluma | `FranceINF` c2 r4, c4 r5 | Pluma vermelha vista de cima, e pluma branca | 🎮 |
| Cocar | `FranceINF` c2 r4 | Cocar tricolor | 🎮 |

**Casaca de abas longas** (corte anterior a 1812, "M3"; decisão F14). Referência: `docs/references/img/ref_fr_08_casacas_abas_longas_mod.png`. São 6 blocos no mesmo desenho de UV:

| ID proposto | Atlas | Casaca | Lapelas | Viradas (abas) | Confiança |
|---|---|---|---|---|---|
| M3-A | `FranceINF` c3 r3, c4 r3, c7 r3 | azul | brancas, recortadas, 7 botões | vermelhas, debrum branco | 🎮; unidade ❓ |
| M3-B | `FranceINF_2` c0 r1 | azul | brancas, debrum vermelho | **brancas**, debrum vermelho | 🎮; unidade ❓ |
| M3-C | `FranceINF_3` c0 r1 | **vermelha** | amarelas, debrum branco | amarelas | 🎮; unidade ❓ (estrangeiro 🔶) |
| M3-D | `FranceINF_3` c1 r1 | azul | amarelas, debrum branco | amarelas | 🎮; unidade ❓ |

Os mesmos blocos trazem:
- dragonas vermelhas, vermelhas com franja dourada, douradas, verdes com meia-lua amarela e brancas;
- ornamentos de virada: águia, granada e corneta;
- colete branco abotoado, que aparece porque a casaca de abas longas fica aberta embaixo.

**O que o mod não mostra para a Guarda** e terá de vir de fonte histórica (🔶 até você confirmar):

| Item (Granadeiros a Pé da Guarda) | Valor histórico mais citado | Confiança |
|---|---|---|
| Gola | Azul, sem debrum | 🔶 |
| Lapelas | Brancas, **retas** (não recortadas como no M3-A) | 🔶 |
| Punhos | Vermelhos, com **portinhola branca** de 3 botões | 🔶 |
| Viradas | Vermelhas, com águias e granadas bordadas em laranja-dourado | 🔶 (o mod mostra só a águia) |
| Dragonas | Vermelhas, com franja vermelha | 🎮 (FranceINF c3 r3) |
| Topo do chapéu | Vermelho com **cruz** branca. No mod: **granada** branca | 🎮 a granada; 🔶 a cruz |
| Cordões | Brancos | 🎮 (c2 r4) |
| Pluma | Vermelha, alta, do lado esquerdo | 🎮 cor; 🔶 posição |
| Caçadores a Pé da Guarda | Chapéu de pele **sem placa**, pluma vermelha sobre verde, dragonas verdes com meia-lua vermelha | 🔶 (não há bloco próprio no mod) |

## 2. França: barretinas e regimentos ainda não feitos

| Item | Onde | Situação | O que precisa |
|---|---|---|---|
| Fuzileiros da 2ª, 3ª e 4ª companhias | Pompons azul, aurora e violeta (decisão B4) | Só a 1ª existe | Só textura |
| Placa em **losango** de latão e de metal branco | `FranceINF` c3 r4, c5 r4; `FranceINF_3` c3 r4, c6–c7 r4 | Não feita | Traçado da placa (como as outras) |
| Placa de **águia coroada** | `FranceINF_3` c4 r5 | Não feita; unidade ❓ | Traçado da placa |
| Pompons de 5 cores e divisas branca, amarela e vermelha | atlas 1–3, linhas 4–5 | 3 cores usadas | Só textura |
| Casacas M3-A a M3-D | §1 | Não feitas | Malha de abas longas (a mesma da Guarda) |
| Casaca verde, infantaria ligeira (M4) | `FranceINF` c4 r0, c0 r2 | Não feitas | Outros cortes, fora deste lote |

## 3. Prússia: o que ainda dá para fazer

As 17 casacas no corte do Kollet já cobrem **todos** os blocos do mod (spec `variantes_regimentos_pruss.md` §9). Para ter "mais regimentos", o caminho são **barretinas novas** combinadas com essas casacas:

| Item | Onde | Situação | Confiança |
|---|---|---|---|
| Barretina com **plumet verde** (provavelmente Jäger voluntários, que usavam casaca de base verde como V09–V17) | `prussia1813_01` c5–c6 r5 | Esboçada em 2026-10-12 (`blockout_plumet_pruss.py`), **fora do addon** | 🎮 o plumet; 🔶 a unidade |
| Barretina da **Guarda a Pé** com Stutz alto branco e preto e estrela prateada | Registro de colecionador | Esboçada, fora do addon | 🔶 |
| **Boné de pano** com faixa vermelha, amarela, verde ou branca (o da Landwehr) | `prussia1813_01..03` c2–c4 r5–r6 | Não feito | 🎮 o boné; mas a Landwehr usava a *Litewka* (outro corte), então com o Kollet seria **anacrônico** |
| Caveira | `prussia1813_01` c0 r5 | Fora (não é infantaria prussiana) | — |
| Capacetes de cavalaria | `prussia1813_03` c5–c6 r5 | Fora (cavalaria) | — |

## 4. Plano proposto (cada etapa com relatório antes de seguir)

1. **Spec da Velha Guarda** (Fase 2): `docs/specs/velha_guarda_granadeiros.md`, com as decisões G1–G6.
2. **Chapéu de pele** (Fases 3–6):
   - corpo modelado em camadas de cartões de pelo, com as texturas do mod;
   - placa traçada da arte do mod; cordões, raquetes e pluma;
   - teto de triângulos a definir na spec (alvo ≤ 12 mil no LOD0), com LOD mais leve.
3. **Corte de abas longas** (F14): malha a partir da casaca de elite, para a Guarda e para M3-A a M3-D.
4. **Barretinas novas:**
   - França: fuzileiros 2ª–4ª e placas em losango (latão e metal branco);
   - Prússia: plumet verde e Stutz da Guarda sobre as 3 malhas.
5. Recompilar os dois addons, verificar (PAA, esqueleto, CfgConvert, `pbo_verify`), fazer as imagens, atualizar os relatórios e enviar os PBOs.

**Nada foi testado no jogo.** Este documento é só leitura dos atlas.
