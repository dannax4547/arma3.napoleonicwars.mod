# Rússia 1812: config.cpp e model.cfg do addon hcl_rus (Fase 8)

2026-10-18. Pedido do usuário: *"Segue para a Fase 8 da Rússia (config.cpp e model.cfg do addon hcl_rus: casaca com as 5 variantes e os kivers por batalhão), mantendo o padrão de fontes."*

**Base:**
- `gen_config_uk.py` (mesmas classes-base e convenções dos addons `hcl_pruss`, `hcl_fr` e `hcl_uk`, conferidas nos configs do jogo e no exemplo oficial `Test_Character_01`).
- As cores e os nomes vêm da ficha `docs/specs/rus_1812.md` (§2.1 platinas, §2.4 pompons) e dos dossiês.

**Situação:**
- **Gerado e verificado fora do jogo:** sintaxe, heranças, todos os caminhos e as seleções.
- **Não empacotado nem testado no ARMA 3:** faltam o Arma 3 Tools (conversão PNG → PAA e PBO) e o Samples.

## 1. Arquivos

Gerador: `source/scripts/gen_config_rus.py` (`python source/scripts/gen_config_rus.py .`).

**`source/addon/hcl/hcl_rus/config.cpp`** (prefixo do PBO `hcl\hcl_rus`):

| Classe | Base | Quantas | Conteúdo |
|---|---|---|---|
| `HCL_RUS1812_Soldado_Base` | `B_Soldier_base_F` | 1 | `hcl_u_rus1812_linha.p3d`, `hiddenSelections[] = {"Camo"}`, scope 1 (soldado só para vestir o uniforme, sem facção) |
| `HCL_RUS1812_Soldado_R01…R04` | a base | 4 | Uma textura `_v0N_co.paa` cada |
| `HCL_U_RUS1812_R01…R04` | `Uniform_Base` | 4 | Item de uniforme (Arsenal, scope 2) que veste o soldado correspondente |
| `HCL_H_RUS{1812,1808}_{Mosqueteiro,Granadeiro}_B{1,2,3}` | `H_HelmetB` | 12 | 4 kivers × 3 batalhões; `hiddenSelections[] = {"camo"}`, sem proteção (como as outras barretinas do projeto) |

**`source/addon/hcl/hcl_rus/model.cfg`:**
- esqueleto `OFP2_ManSkeleton` e classe `ArmaMan` copiados do `model.cfg` do `hcl_pruss`, que veio do Samples oficial. `Camo` já está nas `sections` do `ArmaMan`;
- uma classe `ArmaMan` por P3D: a casaca e os 4 kivers.

Os `.rvmat` não são escritos aqui: os construtores de P3D já gravaram um por material físico em `data/`, e as faces apontam para eles.

## 2. Variantes e nomes

Nenhum regimento é nomeado: a platina dá a **posição do regimento na divisão**, e o pompom dá o **batalhão**. Os nomes de exibição em inglês dizem isso.

| Uniforme | Platina (ordem de 9 jan 1810) | Textura |
|---|---|---|
| R01 | vermelha (1º regimento da divisão) | `hcl_u_rus1812_linha_v01_co.paa` |
| R02 | branca (2º) | `_v02_co.paa` |
| R03 | amarela (3º) | `_v03_co.paa` |
| R04 | verde-escura debruada de vermelho (4º) | `_v04_co.paa` |

| Kiver | 1º batalhão (`_co`) | 2º (`_b2_co`) | 3º (`_b3_co`) |
|---|---|---|---|
| Mosqueteiro (1812 e 1808) | branco, centro verde | verde, centro branco | azul-celeste, centro branco |
| Granadeiro (1812 e 1808) | vermelho | vermelho, verde embaixo | vermelho, azul-celeste embaixo |

Cores dos pompons: ordem de 22 fev 1811 (ficha §2.4). O "embaixo" do granadeiro é **interpretação** (dossiê do kiver, D18 e I6), e as cores são **provisórias** até conferir no atlas.

## 3. Verificações (fora do jogo)

| Verificação | Resultado |
|---|---|
| `config.cpp` passado num analisador da gramática de config (classes, herança, `nome[] = {…};`) | **Sintaxe OK**, 69 classes. Toda classe-pai é declarada antes ou importada (`B_Soldier_base_F`, `Uniform_Base`, `UniformItem`, `H_HelmetB` e seu `ItemInfo`) |
| Texto | ASCII, CRLF, chaves balanceadas |
| P3D citados no config e no `model.cfg` | 5 de 5 existem |
| `.paa` citados no config | 17 de 17 têm o PNG de origem em `source/textures/` |
| Caminhos **dentro** dos P3D (textura e `.rvmat` de cada face) | Todo `.rvmat` existe em `data/`; todo `.paa` dentro deles tem PNG de origem; fora do prefixo, só os do template (`a3\characters_f\…`, mãos) |
| Seleções | `Camo` (casaca) e `camo` (kivers) presentes em todos os LODs visuais, e o osso `Head` nos kivers |

O analisador é do projeto. Ele não substitui o `CfgConvert` do Tools, que deve rodar no empacotamento.

## 4. Pendências (Fase 9)

- **Com o Arma 3 Tools:**
  - converter as PNG em PAA, com os sufixos `_co`, `_nohq` e `_smdi` do `TexConvert.cfg`;
  - empacotar `hcl_rus.pbo` (`FileBank` com `prefix=hcl\hcl_rus`, como `build_mod_uk.ps1`) e conferir o config no `CfgConvert`.
- **No jogo:**
  - vestir no Arsenal: um soldado `HCL_RUS1812_Soldado_R0N` e um kiver `HCL_H_RUS…`;
  - conferir a troca de textura das 4 variantes e dos 12 kivers, os LODs à distância, a sombra e o movimento.
- **Lote RU2 que falta:** granadeiros (casaca), capote, correame e mochila.
