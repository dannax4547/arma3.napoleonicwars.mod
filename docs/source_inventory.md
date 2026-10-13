# Inventário de Fontes

> **Histórico.** A partir de 2026-10-09 este arquivo foi substituído por [`asset_inventory.md`](asset_inventory.md) (ativos) e [`references.md`](references.md) (referências e autorizações). Ele continua aqui só como registro.

Atualizado em 2026-10-09 (briefing revisado).

Este arquivo registra **de onde vem cada recurso** do addon, com origem e permissões conhecidas. Toda textura ou modelo que entrar em `addons/` precisa de uma linha na seção 3.

## 1. Política de uso (regra 5 do briefing revisado)

- Recursos de terceiros **sem autorização** são usados **apenas como referência visual**. O addon usa recursos próprios ou licenciados.
- **Não há autorização** dos autores dos mods do NTW (Reto, LME4, Eras). O fato de o addon ser de uso pessoal não substitui a autorização.
- Se o usuário obtiver autorização escrita, ela será registrada aqui (autor, data, escopo) antes de qualquer uso.
- Histórico: entre a Etapa 2 e o novo briefing, o material do NTW chegou a ser liberado como recorte por ser uso pessoal. Essa decisão foi **substituída**. O único arquivo gerado nesse período (barretina v1) está marcado como obsoleto na seção 3.

## 2. Fontes disponíveis

### A. ARMA 3 (Bohemia Interactive): modelos-base

| Fonte | Caminho | Uso previsto | Verificado |
|---|---|---|---|
| `characters_f.pbo` | `...\Arma 3\Addons\characters_f.pbo` (prefixo `a3\characters_f`) | Modelo-base, referenciado por herança no config, **sem copiar** o `.p3d` | 153 `.p3d`, todos binarizados (`ODOL`); 713 `.paa`; 176 `.rvmat` |
| Outros `characters_f_*.pbo` (jogo base e DLCs) | Ver environment.md, seções 2 e 9.4 | Alternativas de modelo-base | Só os nomes dos arquivos |
| Textura de cor do modelo escolhido | A definir na Fase 2 | Guia de UV; cópia em `work/a3/` | ⏳ |

**Coberturas de cabeça instaladas** (lidas nos cabeçalhos dos PBOs em 2026-10-09; todos `.p3d` binarizados):

| PBO | Modelos |
|---|---|
| `characters_f.pbo` | Capacetes (`headgear_b_helmet_*`, `headgear_o_helmet_*`, `headgear_helmet_heli*`, `headgear_helmet_pilot`, `helmet_heli`), `C_Helmet_Skate_F`, `hat`, `hat_straw`, `headgear_beaniehat01`, `headgear_booniehat01`, `booniehat`, `headgear_c_bandana1`, `headgear_c_capbandana01`, `headgear_shemagmask`, `headgear_shemagopen`, `headgear_turban`, `capb`, `capb_headphones`, **`cappatrol`**, `headgear_beanie`, `headgear_beret01`, `woolhat`, `H_Beret_CSAT_01_F`, `headgear_placeholder` |
| `characters_f_beta`, `_bootcamp`, `_epa`, `_epb`, `_gamma` | Capacetes, bandanas, boinas, bonés, shemagh e `H_Tank_unzip_F` |
| `Expansion\characters_f_exp` | `H_HelmetB_TI_tna_F`, `headgear_beret02`, `headgear_o_vipersp` |
| `Enoch\characters_f_enoch` | Boina, capacetes, `H_TinFoil_Hat_01` |
| `Orange\characters_f_orange` | Capacetes de obra, protetores auriculares, `H_Hat_Safari_F`, bandagem, headsets, PASGT |
| `AoW\characters_f_aow` | **`ParadeDressCap_01_F`** (quepe de desfile) |
| `Kart\characters_f_kart` | Capacete de corrida |

Conclusão: **nenhum modelo tem formato de barretina**, o que justifica geometria nova (regra 7). Para a Fase 4, `Common\cappatrol.p3d` (boné com pala) e `ParadeDressCap_01_F` são candidatos a retextura para bonés de forrageio ou da Landwehr, sem verificação visual ainda.

### B. Pasta de referência (texturas de mods do NTW)

Caminho: `C:\Users\lucas\OneDrive\Área de Trabalho\roupas e texturas para mod da era napoleonica no arma 3`

Conteúdo único: 1.012 arquivos, cerca de 5,7 GB. `(N)_Reto-BattleMOVearly` é uma duplicata.

> **Estado: SÓ REFERÊNCIA VISUAL** (sem autorização). A coluna "Utilidade" indica o valor como referência de cores, cortes e detalhes, não como material a copiar.

| Conjunto | Caminho relativo | Formato | O que contém (visto em pré-visualização) | Utilidade (referência) |
|---|---|---|---|---|
| Torso britânico | `(N)_Reto_BattleMOv2\variantmodels\unitparts\britain\torsos\tex_1\tex_1_{B,G,W,Y}\texture_diffuse.dds` | 512², DXT5 | Casaca vermelha com galões, punhos, gola, abas, alças e placa de cinturão; cor do vivo varia por variante (B = azul e Y = amarelo, confirmados) | **Alta**: material principal para um uniforme britânico |
| Outros torsos britânicos | `...\torsos\tex_3`, `tex_6` a `tex_10`, `tex_1\drum`, `tex_2` | 512², DXT5 | Pré-visualização só de `tex_3` | A avaliar |
| Pernas | `...\britain\legs\tex` a `tex_5` | 512², DXT5 | Pré-visualização gerada, ainda não analisada | A avaliar |
| Chapéus | `...\britain\hats\tex` a `tex_3` | 384², DXT5 | Placa de barretina com cifra "GR" e coroa, plumas (branca/vermelha, branca, verde), corneta de infantaria ligeira | **Alta** na Fase 2 (chapéu) |
| Ombros | `...\britain\shoulders\tex` | 512², DXT5 | Pré-visualização gerada, ainda não analisada | A avaliar |
| Atlas de unidades | `(N)_Reto_BattleMOV11-15\variantmodels\units\atlas\*_diffuse.dds` (61 atlas, 242 arquivos; nem todos têm os 4 mapas) | 4096², até 4 mapas (`diffuse`, `normal`, `gloss`, `colour_mask`) | `FranceINF`: 64 blocos de 512² com casacas azuis de lapela branca, equipamento e rostos | **Média**: exige localizar peças |
| **Atlas prussianos 1813** (uniforme escolhido) | `(N)_Reto_BattleMOV11-15\variantmodels\units\atlas\prussia1813_01` a `_05` (4 mapas cada) | 4096², grade de 8×8 blocos de 512² | Pré-visualizados `_01` e `_02`. `_01`: cerca de 16 blocos de casaca azul-escura com gola e punhos vermelhos, brancos ou amarelos e correame branco; calças cinza/brancas; tampas de barretina com águia e estrela; cartucheira e equipamento de couro; faixa inferior com rostos. `_02`: mesma estrutura, com casacas azuis e verdes | **Alta**: fonte principal da Etapa 3. Cada bloco parece conter frente, costas, mangas e gola de uma casaca (a confirmar em resolução cheia) |
| Atlas prussianos LME4 | `(N)_LME4_graphics\variantmodels\units\atlas\prussiabz_*`, `prussiar_*` | 4096² | Pré-visualizado `prussiar`: rosto de oficial, casacas azul-escuras e verdes com vivos vermelhos/amarelos, galões dourados, dragonas, tampas de chapéu, plumas e rostos | **Média**: detalhes de oficiais e galões |
| Outros atlas LME4 | `(N)_LME4_graphics\variantmodels\units\atlas\*` (18 atlas no total) | 4096×4096 / 4096×2048 | Não visualizados | A avaliar |
| Bandeiras e UI | `ui\flags\*`, `rigidmodels\flags\*` | `.tga`/`.dds` | Bandeiras e ícones | Fora do escopo (não são roupas) |

Os mapas `texture_normal.dds`, `texture_gloss_map.dds` e `*_colour_mask.dds` usam convenções do NTW e **não** serão convertidos para o ARMA 3 na primeira variante.

### C. Cópia parcial do Napoleon: Total War (D:)

| Fonte | Caminho | Estado |
|---|---|---|
| 34 `.pack` (LME4, Reto, `(N)_ERA_Logo_UI`) | `D:\SteamLibrary\steamapps\common\Napoleon Total War\data` | Não inspecionado. **Só referência visual** (sem autorização); modelos não serão portados |

### D. Referências históricas (só visuais)

Ainda não coletadas. Sugestões de obras antigas em domínio público, a localizar e confirmar:
- Richard Knötel, *Uniformenkunde* (pranchas, 1890–1921)
- Charles Hamilton Smith, *Costume of the Army of the British Empire* (1812–1815)

Imagens que o usuário fornecer podem ser registradas aqui com a origem.

### E. Criação própria

| Recurso | Como foi feito |
|---|---|
| Geometria da barretina prussiana 1813 v2 | `source/blender/build_shako_v2.py` (modelagem procedural em Python no Blender 5.2) |
| Texturas da barretina v2 (`_co`, `_nohq`, `_rough_preview`) | `source/blender/generate_shako_textures.py` (ruído procedural, costuras, plissado e trama gerados em código; semente fixa 1813). **Nenhum pixel de terceiros** |

## 3. Recursos usados no addon

Preencher a cada arquivo que entrar em `addons/`. Por enquanto nenhum arquivo está em `addons/`; abaixo estão os candidatos.

| Arquivo | Origem | Arquivos de origem | Modificação | Terceiros? | Estado |
|---|---|---|---|---|---|
| `source/textures/shako_prussline1813_v2/hcl_shako_prussline1813_co.png`, `_nohq.png` | E | `generate_shako_textures.py` | Criação própria | Não | ✅ Candidato |
| `source/blender/hcl_shako_prussline1813_v2.blend` / `export/hcl_shako_prussline1813_v2.fbx` | E | `build_shako_v2.py` | Criação própria (5.484 triângulos) | Não | ✅ Candidato; `.p3d` ainda não gerado |
| `source/textures/prussline1813_shako/hcl_shako_prussline1813_co.png` (v1) | B | Recortes de `prussia1813_01_diffuse.dds` (`compose_shako_texture.py`) | Recortes montados em 1024² | **Sim** | ⛔ **Obsoleto, não usar** (regra 5) |
| `source/blender/hcl_shako_prussline1813.blend` / `export/hcl_shako_prussline1813.fbx` (v1) | E + B | `build_shako.py` | Geometria própria com textura v1 | Textura sim | ⛔ Obsoleto (substituído pela v2) |

## 4. Arquivos temporários desta sessão (fora do projeto)

Pré-visualizações PNG geradas pelo Blender em modo headless, na pasta temporária da sessão (`...\scratchpad\previews\`):
- `torsos__tex_1__tex_1_B__texture_diffuse.png`
- `torsos__tex_1__tex_1_Y__texture_diffuse.png`
- `britain__torsos__tex_3__texture_diffuse.png`
- `britain__legs__tex__texture_diffuse.png`
- `britain__hats__tex__texture_diffuse.png`
- `britain__shoulders__tex__texture_diffuse.png`
- `variantmodels__units__atlas__FranceINF_diffuse.png` (reduzido de 4096² para 1024²)
- `variantmodels__units__atlas__britainINF_diffuse.png` (reduzido de 4096² para 1024²)
- `variantmodels__units__atlas__prussia1813_01_diffuse.png` a `_05_diffuse.png` (reduzidos para 1024²)
- `variantmodels__units__atlas__prussiabz_diffuse.png`, `variantmodels__units__atlas__prussiar_diffuse.png` (reduzidos para 1024²)

São temporárias e não fazem parte do addon. Se forem necessárias, serão regeneradas em `work/ntw/` na Etapa 3.
