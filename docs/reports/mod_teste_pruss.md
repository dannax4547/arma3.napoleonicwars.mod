# Addon de Teste no Jogo: `hcl_pruss.pbo`

Data: 2026-10-10.

Pedido do usuário: *"após acabar eu quero que envie o mod para eu testar os modelos dentro do próprio jogo"*.

**Estado:** PBO gerado e verificado fora do jogo. **Nada foi testado dentro do ARMA 3.** Às ~17:25 o jogo deixou de estar instalado neste PC (§6).

Mod: `release/@Historical_Clothing/`. Contém:
- `Addons/hcl_pruss.pbo`, com 19,2 MB e prefixo `hcl\hcl_pruss`;
- `LEIA-ME_TESTE.txt`, com o passo a passo.

## 1. Conteúdo

| Item | Classes | Modelo |
|---|---|---|
| 8 uniformes | `HCL_U_Pruss1813_V01` … `V08` (itens). Cada um aponta para `HCL_Pruss1813_Soldado_V0n` (scope 1, fora do editor) | `hcl_u_pruss1813.p3d` + textura por variante (`hiddenSelectionsTextures`) |
| 6 barretinas | `HCL_H_Pruss1813_FWR_Amarela`, `_FWR_Branca`, `_Aguia_Amarela`, `_Aguia_Branca`, `_Estrela_Prata`, `_Estrela_Latao` | `hcl_h_pruss_{fwr,aguia,estrela}.p3d` |
| Correame (blockout) | `HCL_V_Pruss1813_Correame` | `hcl_v_pruss1813_correame.p3d` |
| Mochila (blockout) | `HCL_B_Pruss1813_Tornister` | `hcl_b_pruss1813_tornister.p3d` |

Classes base (todas conferidas no config do jogo, em `work/a3/configs`, ou no exemplo oficial):

| Classe base | Usada por |
|---|---|
| `B_Soldier_base_F` | Soldados |
| `Uniform_Base` + `UniformItem` (`containerClass="Supply40"`) | Uniformes |
| `H_HelmetB` (`class ItemInfo: ItemInfo`, armadura 0) | Barretinas |
| `Vest_Camo_Base` (`containerClass="Supply100"`) | Correame |
| `Bag_Base` | Mochila |

Patches requeridos: `A3_Characters_F` e `A3_Weapons_F_Ammoboxes`.

**Sem facção:** os soldados existem só porque, no ARMA 3, o uniforme é um modelo de soldado.

## 2. Como foi construído

Script: `source/scripts/build_mod_pruss.ps1`. Tudo fica dentro do projeto e sem drive P:.

| Etapa | Ferramenta | Verificação |
|---|---|---|
| 1. `.p3d` editável (MLOD) | `p3d_mlod_io.py` (próprio) + `build_p3d_pruss.py` | Ver detalhes abaixo |
| 2. `config.cpp` | `gen_config_pruss.py` (classes por extenso, sem macros) | ✅ **C1:** `CfgConvert -bin` com código 0, e volta para texto |
| 3. Binarização | `binarize_x64.exe` oficial, rodando a partir de `source/addon` (pastas espelhando o prefixo) | ✅ 6 modelos `ODOL`, todos com o esqueleto `OFP2_ManSkeleton` e os nomes dos ossos. Os modelos com textura própria embutem o material (`.rvmat` + `nohq` + `smdi`) |
| 4. Materiais e config binários | `CfgConvert` oficial | ✅ `\0raP` em `config.bin` e nos 4 `.rvmat` |
| 5. PBO | `FileBank.exe` oficial, `-property prefix=hcl\hcl_pruss` | ✅ **P1/P2:** código 0; ver `pbo_verify.py` abaixo |

**Detalhes da etapa 1 (MLOD).** O gravador próprio reproduz **byte a byte os 34 MLOD dos Arma 3 Samples**. Conferido contra os templates oficiais:
- peso total = byte 1;
- regra das faces nas seleções (268 = 268);
- as **2.560 faces das mãos** saem com a mesma ordem de vértices e o mesmo UV do template.

**Detalhes da etapa 5 (`pbo_verify.py`):**
- 33 arquivos, todos com assinatura válida;
- nenhum arquivo-fonte dentro;
- 32 referências internas, **0 faltando**.

### 2.1 Montagem dos modelos

| Modelo | LODs |
|---|---|
| Uniforme | **Resolução 1** e **View Pilot** (primeira pessoa): o uniforme (11.960 triângulos, já com as mãos do template) mais os 11 *proxies* do template (cabeça, barretina, mochila, colete, armas…). **Sombra, Geometria, Memória, Contato com o chão, Pontos de dano e Geometria de tiro:** os do template oficial, sem mudança. As resoluções 2–4 do template foram retiradas, porque mostram o corpo nu do template |
| Barretinas | Resolução 1 (rígida no osso `Head`, seleção `camo`), View Pilot vazio (não aparece em primeira pessoa), sombra = casca convexa fechada, Geometria vazia (`autocenter=0`) |
| Correame e mochila | Resolução 1 (pesos v0, cores lisas procedurais `#(argb,8,8,3)color(...)`) + Geometria vazia (`autocenter=0`); sem sombra |

Pesos: v0, iguais aos do teste de movimentos (`docs/reports/teste_movimentos_pruss.md`). Arquivo: `source/models/pesos/hcl_pruss_pesos_v0.blend`.

Materiais (`data/*.rvmat`): estrutura do material oficial dos Samples (`Test_scope3D_01\Data\nodiffuse.rvmat`, shader `Super`), com o nosso `nohq` no Stage1 e o `smdi` no Stage5. Valores de especular: uniforme 0,4 / 50; barretina 1,0 / 80. Esses valores são nossos.

## 3. Avisos da binarização

Log completo: `work/build/binarize_log.txt`.

| Aviso | Leitura |
|---|---|
| `Cannot load material file a3\characters_f\heads\data\hl_white_bald_muscular.rvmat` | É o material da pele das mãos, que vem do template. O jogo não está extraído num drive P: (e agora nem instalado), então a ferramenta não o lê. 🔶 O jogo troca materiais por caminho durante a execução (a lista `Wounds` faz isso), por isso provavelmente funciona. **Conferir no jogo (G8).** Se as mãos ficarem erradas, a correção é binarizar com os dados do jogo extraídos (precisa do P:, com a sua autorização) |
| `Cannot load material file a3\data_f\penetration\meat*.rvmat` | Materiais de penetração de bala do LOD de tiro do template. Não afetam a aparência |
| `Subskeleton index out of range` e `Selection … needs a section` | Aparecem **iguais** ao binarizar o exemplo oficial dos Samples |

## 4. Limites deste teste

- Só um nível de detalhe por modelo, sem LODs 2–4.
- Sombra do uniforme = a do corpo do template: as abas não projetam sombra.
- Pesos v0, com os problemas P1–P9 do teste de movimentos.
- Correame e mochila são blockout, sem textura.
- Sem texturas de ferimento.
- 🔶 Não foi verificado como as mochilas oficiais são ponderadas. A nossa segue o esqueleto como o colete; o modelo oficial não pôde ser lido porque o jogo foi desinstalado.

## 5. Como testar

Ver `release/@Historical_Clothing/LEIA-ME_TESTE.txt`. Resumo:
1. Carregar o mod local pelo Launcher.
2. No Editor, abrir o Arsenal e procurar os itens `[HCL]`, ou usar o console com `forceAddUniform` / `addHeadgear` / `addVest` / `addBackpack`.
3. Percorrer G1–G12 de `docs/testing.md`.

## 6. Observação sobre a instalação do jogo

Por volta das 17:25 de 2026-10-10:
- a pasta `C:\Program Files (x86)\Steam\steamapps\common\Arma 3` passou a conter só `!Workshop`;
- o `appmanifest_107410.acf` deixou de existir.

Até cerca das 16:20 os PBOs do jogo estavam lá: foram lidos, só para leitura, no teste de movimentos. Nenhum comando do projeto escreve nessa pasta. **Para testar o mod é preciso reinstalar o ARMA 3 pelo Steam.**
