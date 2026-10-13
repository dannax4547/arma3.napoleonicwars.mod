# Ficha Técnica: Correame e Mochila da Infantaria Prussiana, 1813

Fase 2 do pipeline. Versão 1.0, 2026-10-10. **Estado: aguarda as decisões E1–E6 (§7) e a aprovação.** O blockout já foi feito a pedido do usuário, para ver junto: `docs/reports/equipamento_pruss_blockout.md`.

Legenda: ✅ confirmado · 🔶 provável · ❓ incerto · 🎮 visto na textura do mod

> **Armamento:** o projeto exclui sistemas de combate. Baioneta e cartucheira entram **só como peças visuais** do correame, sem função de arma. Um mosquete funcional exigiria mudar o escopo (decisão E6).

## 1. Itens no ARMA 3 (verificado)

| Item | Tipo no jogo | Base verificada | Fonte |
|---|---|---|---|
| `HCL_V_Pruss1813_Correame` | Colete (`CfgWeapons`) | `Vest_Camo_Base: ItemCore` com `ItemInfo: VestItem` (`hiddenSelections[]={"camo"}`, `uniformModel`, carga pelo macro `LOAD`) | `characters_f` config, linhas 28944 e 28966; `Samples\cfgVests.hpp` |
| `HCL_B_Pruss1813_Tornister` | Mochila (`CfgVehicles`) | `Bag_Base: ReammoBox` (`isbackpack=1`, `hiddenSelections[]={"Camo"}`, `maximumLoad`, `mass`, `model`), patch `A3_Weapons_F_Ammoboxes` | `weapons_f.pbo` → `Ammoboxes\config.bin`, linha 4427 (extraído para `work/a3/configs/`) |

| Fato do modelo | Valor | Fonte |
|---|---|---|
| LODs do colete | Resolução 1–5 (`lodnoshadow=1`), Shadow Volume 0, Geometry **vazia** (`autocenter=0`) | `A3_vest_example.p3d` / `A3_vest_template.p3d` |
| Pesos do colete | Ossos do tronco e dos ombros (`Pelvis`, `Spine`…`Spine3`, `LeftShoulder`, `LeftArm`…) e seleção `camo` | `A3_vest_example.p3d` |
| Proxy da mochila no personagem | **Identidade**: origem (0,0,0), +Y para cima, +Z para a frente, **sem osso** (igual aos proxies da cabeça e do item de cabeça) | `proxy_info.py` em `A3_character_example.p3d` |
| Consequência | Mochila modelada **no espaço do personagem**, como o colete. Que ela precise de pesos próprios nos ossos, como o item de cabeça, é **inferência**, a confirmar no teste B1 e no jogo | — |

Os dois itens ficam por cima do uniforme e foram encaixados sobre a malha `HCL_U_Pruss1813_01_LOD0`.

## 2. Componentes, cores e materiais

### 2.1 Correame (colete)

| Componente | Descrição | Medida (proposta) | Cor / material | Confiança |
|---|---|---|---|---|
| Cinturão | Na cintura, sobre a bainha do casaco, fivela retangular de latão na frente | 5 cm × 3,5 mm | Couro branqueado; latão | 🎮 (pintado no casaco do mod); decisão U5 |
| Bandoleira | Sobre o ombro esquerdo, cruza o peito até a cartucheira atrás da anca direita; outra perna desce pelas costas | 6 cm × 3,5 mm | Couro branqueado | 🔶 (prática geral da infantaria da época; não confirmada para este modelo) |
| Cartucheira | Caixa com tampa, na anca direita atrás | 20 × 13 × 6,5 cm | Couro preto; placa lisa de latão na tampa | 🔶 forma; ❓ distintivo da tampa (E2) |
| Baioneta | De alvado, dentro da bainha; o alvado e o cotovelo da lâmina ficam à mostra acima do passador | Bainha 45 cm; alvado ⌀ 2,4 × 7,5 cm | Bainha de couro preto, bocal e ponteira de latão; ferro | 🔶 |
| Passador da baioneta | Laço branco no cinturão, anca esquerda | 4,4 × 12 cm | Couro branqueado | 🔶 |
| Sabre curto | Não incluído | — | — | ❓ (E3) |

### 2.2 Mochila (*Tornister*)

| Componente | Descrição | Medida (proposta) | Cor / material | Confiança |
|---|---|---|---|---|
| Corpo | Caixa de couro com cantos arredondados, inclinada como as costas (6,9° medidos) | 34 × 30 × 12 cm | Couro preto | 🔶 |
| Tampa | Pele de bezerro com pelo, cobrindo o topo e a parte de cima da face externa; 2 correias de fecho | — | Castanho | 🔶 (peças castanhas no atlas do mod) |
| Capote enrolado | Rolo cinza sobre a mochila, mais largo do que ela, com 2 correias brancas | ⌀ 11 × 42 cm | Lã cinza | 🎮 (rolo cinza com espirais e correias brancas no atlas) |
| Correias de ombro | 2 brancas: dos cantos de cima, por cima dos ombros, descem pelo peito, passam sob os braços e voltam aos cantos de baixo | 4,5 cm | Couro branqueado | 🔶 |
| Marmita | Não incluída | — | — | ❓ (E4) |

## 3. Referências

| ID | Fonte | Uso |
|---|---|---|
| M1 | `ref_uniforme_01_casaco_frente_mod.png` (atlas `prussia1813_01`) | Cinturão branco com fivela de latão; peças castanhas e pretas (cartucheira e mochila); rolo cinza com correias brancas |
| M2 | `ref_uniforme_02_casaco_costas_mod.png` | Peças de couro castanho e uma bainha preta com guarnição clara |
| Arma 3 Samples | `cfgVests.hpp`, `A3_vest_example.p3d`, `A3_vest_template.p3d`, `A3_character_example.p3d` | Requisitos técnicos (§1) |
| Config do jogo | `characters_f`, `weapons_f\Ammoboxes` | Classes-base (§1) |

**Nenhuma fonte histórica primária foi consultada para o equipamento.** As fontes da ficha do uniforme não descrevem correame nem mochila. Tudo o que está marcado 🔶 segue a prática geral da época e precisa de confirmação (sugestão: pranchas de Knötel, Osprey sobre a infantaria prussiana).

## 4. Requisitos de encaixe

- Por cima do uniforme, sem atravessá-lo: medido por raios para fora a partir de cada vértice.
- Correias sempre acima dos botões (folga maior que os 4,5 mm de altura do botão).
- Ordem das camadas no ombro esquerdo: uniforme → bandoleira → correia da mochila (1,5 mm entre elas).
- Mochila apoiada no ponto mais saliente das costas, com a mesma inclinação.

## 5. Orçamento proposto (Resolução 1)

| Item | Triângulos | Base |
|---|---:|---|
| Correame | ≤ 3.000 | Exemplo oficial de colete: 1.317 faces |
| Mochila | ≤ 3.000 | A confirmar com um modelo oficial (os da mochila são binarizados) |

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Bainha da baioneta × coxa esquerda ao andar | Pesos na pelve e na coxa; teste no jogo |
| Cartucheira × braço direito | Fica atrás da anca; teste no jogo |
| Correias da mochila × braços na pose de tiro | Pesos nos ombros; teste no jogo |
| Colete e mochila usados com outro uniforme | São feitos para este uniforme; com uniformes do jogo podem atravessar |

## 7. Decisões pedidas ao usuário

| # | Pergunta | Recomendação |
|---|---|---|
| E1 | Bandoleira sobre o ombro esquerdo até a cartucheira atrás da anca direita, como no blockout | **Sim** |
| E2 | Distintivo na tampa da cartucheira: liso, placa de latão lisa ou outro (segundo o mod) | **Placa lisa** até haver referência |
| E3 | Incluir sabre curto (*Faschinenmesser*) no correame | **Não**, até confirmar se a infantaria de linha o usava em 1813 |
| E4 | Incluir marmita na mochila | **Não**, até haver referência |
| E5 | Nomes no Eras Mod para o correame e a mochila (como em U1) | Você informa; até lá, nomes técnicos |
| E6 | Mosquete funcional | **Fora do escopo** (sem sistemas de combate). Só com mudança de escopo |
