# Inventário de Ativos

Fase 1. Atualizado em 2026-10-09. Substitui `source_inventory.md` (mantido como histórico).

Estados: **Exploratório** = feito antes deste briefing, não aprovado · **Obsoleto** = não usar · **Rascunho** = escrito e não executado · **Aprovado** = passou na revisão da fase correspondente.

---

## 1. Ativos do projeto

> **Reorganização feita em 2026-10-09** (§4). Novos locais: scripts em `source/scripts/`; `.blend` e `.fbx` em `source/models/shakos/_exploratorio/` (v2) e `_obsoleto/` (v1); texturas em `source/textures/_exploratorio/` e `_obsoleto/`. Nos caminhos da tabela abaixo, `source/blender/` corresponde a esses novos locais.

### 1.1 Barretinas: protótipos exploratórios (antes do pipeline profissional)

Nenhum destes é um protótipo aprovado. Pelo briefing atual, a barretina recomeça pela **Fase 2 (ficha técnica)** e pela **Fase 3 (blockout)**.

| Arquivo | O que é | Origem | Estado |
|---|---|---|---|
| `source/blender/build_shako.py`, `compose_shako_texture.py` | v1: cilindro simples; textura com recortes do atlas NTW | Script próprio + pixels de terceiros | ⛔ **Obsoleto** (pixels de terceiros sem autorização) |
| `source/blender/hcl_shako_prussline1813.blend`, `export/hcl_shako_prussline1813.fbx` | Saídas da v1 | idem | ⛔ Obsoleto |
| `source/textures/prussline1813_shako/hcl_shako_prussline1813_co.png` | Textura da v1 | Recortes de `prussia1813_01_diffuse.dds` (NTW) | ⛔ Obsoleto, não usar |
| `docs/renders/shako_prussline1813_*.png` | Renders da v1 | — | Histórico |
| `source/blender/build_shako_v2.py`, `generate_shako_textures.py` | v2: corpo oval, pala com debrum, cocar, presilha, rosetas, jugular; texturas procedurais próprias. 5.484 triângulos | Próprio | 🔶 Exploratório |
| `source/blender/hcl_shako_prussline1813_v2.blend` (+ `.blend1`, backup automático do Blender), `export/hcl_shako_prussline1813_v2.fbx` | Saídas da v2 | Próprio | 🔶 Exploratório |
| `source/textures/shako_prussline1813_v2/*_co.png`, `*_nohq.png`, `*_rough_preview.png` | Texturas da v2 | Próprio | 🔶 Exploratório |
| `docs/renders/v2/*.png` | Renders da v2 | — | Histórico |
| `source/blender/build_shako_v3.py` | v3 baseada na referência R2. **Não executado**: o novo briefing chegou antes da execução | Próprio | 📝 Rascunho (base para o blockout da Fase 3, depois da ficha técnica) |
| `generate_shako_textures.py`, estilo `v3` | Couro envernizado, faixa branca de sarja, pompom. **Não executado** | Próprio | 📝 Rascunho |

Problemas conhecidos dos protótipos exploratórios, para não repetir:
- encaixe feito sobre um manequim oval, não sobre o corpo oficial do ARMA 3;
- modelados na origem, e não na posição da cabeça do personagem;
- sem LODs, sem seleção `camo`, sem pesos no osso `head`;
- material do Blender, não `.rvmat`.

### 1.1b Barretina prussiana: protótipo do pipeline profissional

| Arquivo | O que é | Origem | Estado |
|---|---|---|---|
| `docs/specs/shako_prussiano_infantaria.md` | Ficha técnica v1.1 | Próprio | ✅ Aprovada (decisões F1–F5) |
| `source/models/shakos/hcl_shako_pruss/hcl_shako_pruss_blockout.blend` | Blockout | Próprio | ✅ Aprovado |
| `source/models/shakos/hcl_shako_pruss/hcl_shako_pruss_LOD0.blend` | Malha LOD 0 com UVs (5.194 triângulos) | Próprio | ✅ Fase 4 aprovada; UV na Fase 6 |
| `source/textures/hcl_shako_pruss/hcl_shako_pruss_{co,nohq,smdi}.png` | Texturas-fonte 2048² | Próprio (procedural) | 🔶 Fase 6, aguarda aprovação |
| `source/textures/hcl_shako_pruss/paa/*.paa` | Texturas convertidas (ImageToPAA) | Derivado das fontes acima | 🔶 Fase 6 |
| `source/scripts/*.py` | Scripts reproduzíveis (encaixe, produção, UV, texturas, revisões, leitor `.p3d`) | Próprio | — |
| Fonte `C:\Windows\Fonts\Gabriola.ttf` | Usada só como forma geradora do monograma | Microsoft (instalada com o Windows) | Uso pessoal; verificar a licença se houver distribuição |

### 1.2 Uniforme prussiano de 1813 (protótipo 2, iniciado em 2026-10-10)

| Arquivo | O que é | Origem | Estado |
|---|---|---|---|
| `docs/specs/uniforme_prussiano_infantaria_1813.md` | Ficha técnica v1.1 | Próprio | ✅ Aprovada (U1 e U7 pendentes) |
| `source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_blockout.blend` | Blockout (16 peças sobre o corpo oficial, com a barretina aprovada como referência) | Próprio | 🔶 Aguarda aprovação |
| `source/scripts/blockout_uniforme_pruss.py` | Gera o blockout, as verificações e os renders | Próprio | — |
| `docs/reports/uniforme_pruss_blockout.md` (+ `_output.txt`), `docs/reports/img/uniforme/blockout_*.png` | Relatório da Fase 3 | Gerado | — |
| `source/models/coats/hcl_uniforme_pruss/ref_corpo_arma3_samples.blend` | Corpo oficial (exemplo e template, Resolução 1) importado dos Samples, com grupos de vértices por osso. **Só referência de encaixe**; não é exportado | Arma 3 Samples (licença de modding) | Referência |
| `docs/reports/img/uniforme/ref_corpo_{exemplo,template}_{frente,lado,costas}.png` | Renders do corpo oficial (azul = `camo`, pele = `hl`) | Gerado | Referência |
| `docs/references/img/ref_uniforme_0{1..4}_*_mod.png` | Recortes do atlas `prussia1813_01_diffuse.dds` | Eras Mod (autorização declarada) | Referência |
| `work/ntw/prussia1813/*` | Atlas `prussia1813_01..03_diffuse` convertidos para PNG, prévias e recortes | Eras Mod | Só consulta local; não entra no addon |
| `source/scripts/inspect_character_ref.py`, `inspect_weights.py` | Leitura do corpo oficial, medidas, renders; estatística de pesos | Próprio | — |

| `source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend` | Malha de produção, Resolução 1 (11.960 triângulos; mãos do template oficial) | Próprio + mãos do Arma 3 Samples (licença de modding) | 🔶 Fase 4, aguarda aprovação; Fase 5 passou |
| `source/scripts/build_uniforme_production.py`, `uniform_fit.py`, `uniform_review.py`, `render_closeup.py` | Gerador, ferramentas de encaixe, revisão, close-ups | Próprio | — |
| `docs/reports/uniforme_pruss_producao.md`, `uniforme_pruss_mesh_review.md` (+ `_output.txt`), `img/uniforme/producao_*.png` | Relatórios das Fases 4 e 5 | Gerado | — |

### 1.2b Variantes regimentais prussianas (2026-10-10)

Ficha: `docs/specs/variantes_regimentos_pruss.md`. Estado de todos: 🔶 aguarda aprovação.

| Arquivo | O que é | Origem |
|---|---|---|
| `source/models/coats/hcl_uniforme_pruss/hcl_uniforme_pruss_LOD0.blend` | Agora com UV (Fase 6) | Próprio |
| `source/textures/hcl_uniforme_pruss/variantes_regimentos.json` | Cores das variantes V01–V08 | Cores amostradas dos atlas do Eras Mod (autorização declarada) |
| `source/textures/hcl_uniforme_pruss/hcl_u_pruss1813_v01..v08_co.png`, `hcl_u_pruss1813_{nohq,smdi}.png` (+ `paa/`) | Texturas do uniforme, 2048² | Próprio (procedural) com as cores acima |
| `source/models/shakos/hcl_shako_pruss/variantes/hcl_shako_pruss_{aguia,estrela}_LOD0.blend` | Barretina com águia (5.262 tris) e com estrela (5.778 tris) | Próprio; **contorno dos distintivos traçado da arte do Eras Mod** |
| `source/models/shakos/hcl_shako_pruss/distintivos/{aguia,estrela}.json` | Contornos traçados | Derivado do atlas `prussia1813_01` do Eras Mod (autorização declarada; U7 pendente) |
| `source/textures/hcl_shako_pruss/variantes/hcl_shako_pruss_*_{co,nohq,smdi}.png` (+ `paa/variantes/`) | 5 variantes de cor da barretina | Próprio (procedural); a cor da águia e da estrela vem da arte do Eras Mod |
| `source/scripts/{catalog_mod_coats.ps1, trace_badge.py, uv_uniforme_pruss.py, generate_uniform_textures.py, render_lineup.py, convert_variants_paa.ps1}` | Catálogo do mod, traçado, UV, texturas, render do desfile, conversão `.paa` | Próprio |
| `docs/reports/img/variantes/*.png`, `desfile_variantes.blend` | Renders das variantes | Gerado |
| `work/ntw/prussia1813/catalogo_casacas.{png,csv}`, `distintivos_atlas01.png`, `faixa_barretinas_0{1..3}.png` | Catálogo e recortes do mod | Só consulta local; não entra no addon |

### 1.2c Addon de teste no jogo (2026-10-10)

Relatório: `docs/reports/mod_teste_pruss.md`. Estado de todos: 🔶 gerado, não testado no jogo.

| Arquivo | O que é | Origem |
|---|---|---|
| `source/addon/hcl/hcl_pruss/` (`*.p3d` MLOD, `config.cpp`, `model.cfg`, `data/`) | Fonte do addon. As pastas espelham o prefixo `hcl\hcl_pruss` | Próprio + LODs técnicos, *proxies* e mãos dos templates dos Arma 3 Samples (licença de modding); `model.cfg` com o esqueleto copiado do exemplo oficial |
| `source/models/pesos/hcl_pruss_pesos_v0.blend` | Pesos v0 do uniforme, do correame e da mochila | Gerado por `teste_movimentos.py` |
| `work/build/hcl/hcl_pruss/`, `work/build/binarize_log.txt` | Saída binarizada e log | Gerado (ferramentas oficiais) |
| `release/@Historical_Clothing/Addons/hcl_pruss.pbo`, `LEIA-ME_TESTE.txt` | Mod de teste | Gerado |
| `source/scripts/{p3d_mlod_io.py, build_p3d_pruss.py, gen_config_pruss.py, build_mod_pruss.ps1, pbo_verify.py, rtm_read.py, teste_movimentos.py}` | Gravador MLOD, montagem, config, build, verificação, animações | Próprio |
| `work/build/hcl_pruss/` | Primeira binarização, antes da reorganização das pastas; não é usada | Gerado (pode ser apagada com a sua autorização) |

### 1.3 Correame e mochila (protótipo 3, iniciado em 2026-10-10)

| Arquivo | O que é | Origem | Estado |
|---|---|---|---|
| `docs/specs/equipamento_pruss_1813.md` | Ficha técnica v1.0 | Próprio | 🔶 Aguarda E1–E6 |
| `source/models/accessories/hcl_equipamento_pruss/hcl_equipamento_pruss_blockout.blend` | Blockout: correame (cinturão, bandoleira, cartucheira, baioneta) e mochila (corpo, tampa, capote, correias) | Próprio | 🔶 Aguarda aprovação |
| `source/scripts/blockout_equipamento_pruss.py`, `proxy_info.py`, `pbo_find.py` | Gerador; leitura de proxies; busca e extração de configs dentro de PBOs (só leitura do jogo) | Próprio | — |
| `work/a3/configs/weapons_f_ammoboxes.config.{bin,cpp}` | Config das mochilas do jogo (`Bag_Base`) | Extraído de `weapons_f.pbo` | Só consulta local |
| `docs/reports/equipamento_pruss_blockout.md` (+ `_output.txt`), `img/equipamento/*.png` | Relatório da Fase 3 | Gerado | — |

### 1.3 Referências visuais guardadas no projeto

| Arquivo | Descrição |
|---|---|
| `docs/references/img/ref_shako_01_render_baixa_resolucao.png` | R1 (ver `references.md`) |
| `docs/references/img/ref_shako_02_foto_fwr.png` | R2, referência principal indicada pelo usuário |

---

## 2. Ativos do jogo disponíveis como base ou referência técnica

Só consulta; nada é copiado para o addon. Os modelos são referenciados pelo caminho no config.

| Ativo | Caminho | Uso possível | Verificado |
|---|---|---|---|
| Boné de patrulha | `\A3\Characters_F\Common\cappatrol` (classe `H_MilCap_ocamo` e variantes) | Retextura de bonés (fase posterior); exemplo técnico de item de cabeça | ✅ config e textos do `.p3d` |
| Capacete simples | `\A3\Characters_F\BLUFOR\headgear_b_helmet_plain` (`H_HelmetB`, `HelmetBase`) | Exemplo técnico | ✅ |
| Quepe de desfile | `AoW\characters_f_aow.pbo` → `Headgear\ParadeDressCap_01_F.p3d` | Possível base de bonés | Só o nome do arquivo |
| Outros 70+ itens de cabeça | Ver lista em `source_inventory.md` 2.A | Nenhum tem formato de barretina | ✅ nomes |
| Corpos de personagem | `characters_f.pbo` (153 `.p3d`, todos binarizados `ODOL`) | Base de retextura de uniforme, **não editáveis** | ✅ |
| Modelos-base editáveis do Object Builder | `O2Scripts\CharacterGeo\NewGeometryTemplate.p3d`, `O2Scripts\CharacterFG\NewFireGeometryTemplate.p3d` | LODs de geometria e fire geometry de personagem | ✅ existem |
| Arma 3 Samples (`A3_headgear_example.p3d`, `A3_character_example.p3d`, `A3_character_template.p3d`, `Test_Character_01`) | `Steam\steamapps\common\Arma 3 Samples\Addons\Test_Character_01` | Exemplo oficial, corpo de referência e LODs técnicos do uniforme (template) | ✅ Instalado em 2026-10-09 |

Arquivos de trabalho extraídos (`work/a3/configs/*.config.cpp`, `work/a3/models/*.p3d`) servem **só para consulta local** e nunca entram em `addons/` nem em `release/`.

## 3. Ativos de terceiros

| Ativo | Estado |
|---|---|
| Texturas NTW (pasta no OneDrive, 1.012 arquivos únicos) e `.pack` em `D:\SteamLibrary\steamapps\common\Napoleon Total War\data` | Só referência visual, **exceto o Eras Mod**: autorização declarada pelo usuário em 2026-10-09 (detalhes pendentes, `references.md` §3.2). O que deriva do mod está marcado nas tabelas acima |

---

## 4. Reorganização de pastas proposta (aguarda aprovação)

Estrutura pedida pelo briefing:

```
source/models/coats/      source/models/trousers/
source/models/shakos/     source/models/accessories/
source/textures/          source/scripts/
docs/                     release/@Historical_Clothing/Addons/
```

Movimentos propostos (**nada será apagado**; só mudança de lugar):

| De | Para |
|---|---|
| `source/blender/*.py` | `source/scripts/` |
| `source/blender/hcl_shako_prussline1813_v2.blend` (+ `.blend1`) e `export/hcl_shako_prussline1813_v2.fbx` | `source/models/shakos/_exploratorio/` |
| `source/blender/hcl_shako_prussline1813.blend` e `export/hcl_shako_prussline1813.fbx` (v1) | `source/models/shakos/_obsoleto/` |
| `source/textures/prussline1813_shako/` (v1) | `source/textures/_obsoleto/prussline1813_shako/` |
| `source/textures/shako_prussline1813_v2/` | `source/textures/_exploratorio/shako_prussline1813_v2/` |

Depois de mover, os comandos de exemplo no README serão ajustados para os novos caminhos.
