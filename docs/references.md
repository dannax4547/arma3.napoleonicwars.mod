# Referências

Fase 1 do briefing "Pipeline Profissional de Modelagem 3D". Atualizado em 2026-10-09.

Legenda: ✅ confirmado na fonte · 🔶 confirmado só em resumo/citação indireta, ainda falta ler a fonte · ❔ não verificado

---

## 1. Documentação técnica oficial (Bohemia Interactive)

| Página | URL | Acesso em 2026-10-09 |
|---|---|---|
| Characters And Gear Encoding Guide | https://community.bistudio.com/wiki/Arma_3:_Characters_And_Gear_Encoding_Guide | ❌ Leitura automática bloqueada (HTTP 403; no navegador embutido, a verificação de segurança do site não terminou). **Não foi contornada** |
| Modding Characters | https://community.bistudio.com/wiki/Arma_3:_Modding_Characters | ❔ Não lida (mesmo site) |
| Named Properties | https://community.bistudio.com/wiki/Arma_3:_Named_Properties | ❔ Não lida |
| LOD | https://community.bistudio.com/wiki/LOD | ❔ Não lida |
| Object Builder | https://community.bistudio.com/wiki/Object_Builder | ❔ Não lida |
| Fórum: tópico do guia | https://forums.bohemia.net/forums/topic/180812-characters-and-gear-encoding-guide/ | ✅ Lido (é uma discussão, não o guia) |
| Fórum: arquivos de exemplo (`a3_headgear_example.p3d`) | https://forums.bohemia.net/forums/topic/179379-arma-tools-sample-files-cannot-open-object-a3_headgear_examplep3d/ | 🔶 Só o resumo da busca |

### 1.1 Informações obtidas de forma indireta (🔶, a confirmar lendo a wiki)

Fonte: resumo de busca sobre as páginas acima.

| Item | Informação |
|---|---|
| LOD Geometry em itens de cabeça | Deve existir, mesmo vazio, com a propriedade `autocenter = 0` |
| LOD ViewPilot | Capacetes e óculos precisam de um ViewPilot **vazio**, para não bloquear a visão em primeira pessoa |
| Modelos de exemplo | `A3_headgear_example.p3d` e `A3_vest_example.p3d`, no **Arma 3 Samples** (`samples_f\test_character_01\`) |
| Propriedades nomeadas | Em minúsculas; no Object Builder, janela aberta com Alt+P |
| Limite de polígonos | Cada LOD tem um máximo; se ultrapassar, o LOD não aparece no Buldozer |

Do fórum (✅): o guia diz que itens de cabeça costumam herdar de `H_HelmetB`, e o uniforme se liga ao soldado pela propriedade `uniformClass`.

---

## 2. Verificação nos dados do jogo instalado (fonte primária disponível)

Arquivos extraídos **só para consulta** em `work/a3/` (nunca entram no addon):
- `work/a3/configs/characters_f.config.cpp` e `weapons_f.config.cpp`: `config.bin` dos PBOs, convertidos com CfgConvert (código de saída 0);
- `work/a3/models/Common_cappatrol.p3d` e `BLUFOR_headgear_b_helmet_plain.p3d`: modelos binarizados (ODOL), lidos só como texto.

| Fato verificado | Onde |
|---|---|
| Patch dos personagens: `class A3_Characters_F` | `characters_f.config.cpp:3` |
| Patch das armas: `class A3_Weapons_F` | `weapons_f.config.cpp:3` |
| `class UniformItem: InventoryItem_Base_F { type=801; }` | `characters_f.config.cpp:25852` |
| `class Uniform_Base: ItemCore` com `scope=0`, `allowedSlots[]={901}` e `ItemInfo: UniformItem { uniformModel="-"; uniformClass="B_Soldier_F"; containerClass="Supply0"; mass=0; }` | `characters_f.config.cpp:25856` |
| `class HeadgearItem: InventoryItem_Base_F` com `allowedSlots[]={901,605}`, `type=605`, `hiddenSelections[]={}` | `characters_f.config.cpp:30379` |
| `class HelmetBase: ItemCore` (`scope=0`, `model`, `hiddenSelections[]={"camo"}`, `ItemInfo: HeadgearItem { mass, uniformModel, modelSides[]={3,1}, hiddenSelections, HitpointsProtectionInfo }`) | `characters_f.config.cpp:30387` |
| `class H_HelmetB: ItemCore` (`scope=2`, mesma estrutura) | `characters_f.config.cpp:30423` |
| Boné com pala: `H_MilCap_ocamo: HelmetBase` → `model="\A3\Characters_F\Common\cappatrol"`, `ItemInfo { allowedSlots[]={901,701,605}; uniformModel="...cappatrol.p3d"; modelSides[]={6}; }` | `characters_f.config.cpp:31750` |
| Esqueleto: `CfgSkeletonParameters >> OFP2_ManSkeleton` (`pivotsModel="A3\anims_f\data\skeleton\SkeletonPivots.p3d"`) | `characters_f.config.cpp:25811` |
| Os modelos oficiais de cabeça contêm: seleção **`head`**, seleção **`camo`**, referência a **`OFP2_ManSkeleton`**, nomes dos ossos do esqueleto inteiro, propriedades `autocenter` e `lodnoshadow`, LODs de sombra (ex.: `cap_00shadow`) e materiais `.rvmat` com `_co`, `_nohq`, `_smdi`, `_as` (capacete) e `_ti_ca` (térmica, no boné) | Textos dentro dos `.p3d` em `work/a3/models/` |

Consequência importante: como os modelos oficiais de cabeça carregam o esqueleto de personagem e a seleção `head`, **o item de cabeça é modelado na posição da cabeça do personagem e ponderado ao osso `head`**. O posicionamento exato depende de um corpo de referência oficial (ver `modeling_standards.md`, seção 2).

---

## 2b. Arma 3 Samples (instalado em 2026-10-09; fonte oficial lida diretamente)

Caminho: `C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Samples\Addons\Test_Character_01\` (682 arquivos no pacote; manifesto Steam 390500).

| Fato verificado | Arquivo |
|---|---|
| **Licença**: "Arma 3 - Modding License". Permite abrir e modificar os samples para conteúdo **não comercial para o ARMA 3**; proíbe convertê-los para outros jogos ou engines | `Test_Character_01\readme.txt` |
| **LODs de um item de cabeça** (modelo-base oficial): Resolução 1, 2, 3 (`LODNoShadow=1`) · View Pilot (1100) **vazio** · Shadow Volume 0 (10000) · Geometry (1e13) **vazio**, com `#Mass#`, `autocenter=0`, `prefershadowvolume=1` | `A3_headgear_template.p3d` (lido com `source/scripts/p3d_mlod_inspect.py`) |
| Seleções do exemplo: `Head` (osso) e `camo` em todos os LODs visuais; `Head` também no LOD de sombra. LOD 0/1/2 = 400/200/56 faces; sombra 72 faces. Material `capb.rvmat`, textura `capb_police_co` | `A3_headgear_example.p3d` |
| `model.cfg`: `class A3_headgear_example: ArmaMan{}`; `ArmaMan` usa `skeletonName = "OFP2_ManSkeleton"`, com a seção `Camo` | `model.cfg` |
| Config de exemplo: `H_Test_Headgear: ItemCore` com `model`, `hiddenSelections[]={"camo"}`, `hiddenSelectionsTextures[]`, `ItemInfo: HeadgearItem { mass, uniformModel, allowedSlots, modelSides[]={6} (comentado como "available for all sides"), HitpointsProtectionInfo }` | `cfgHeadgear.hpp` |
| Eixos do `.p3d`: +Y para cima, frente = −Z, esquerda do personagem = +X; a origem do personagem fica cerca de 1 m acima do chão | `A3_character_example.p3d` (seleções de pés e mãos) |
| Os FBX do Samples **não importam no Blender 5.2** (um é FBX ASCII, o outro versão 6100). Os `.p3d` MLOD foram lidos diretamente | Teste de 2026-10-09 |
| A cabeça do personagem é um *proxy*; **a malha da cabeça não vem no Samples** | `A3_character_example.p3d` |

Com isso, os itens 🔶 da seção 1.1 (LOD Geometry com `autocenter=0`, ViewPilot vazio) passam a ✅ **confirmados na fonte oficial**.

**Personagem e uniforme** (lido em 2026-10-10 com `inspect_character_ref.py`, `p3d_mlod_inspect.py` e `inspect_weights.py`):

| Fato verificado | Arquivo |
|---|---|
| O uniforme é o **corpo inteiro** do soldado: o item `U_Test_uniform: ItemCore` (`ItemInfo: UniformItem { uniformModel = "-"; uniformClass = Test_Soldier_base_F; containerClass = Supply90; mass = 80 }`) aponta para a classe de soldado, que tem o `model`, os `hiddenSelections[] = {"Camo", "insignia"}`, `nakedUniform = "U_BasicBody"` e `class Wounds` | `cfgUniforms.hpp`, `config.cpp` |
| `A3_character_example.p3d`: 12 LODs: Resolução 1–4 (6.235 / 3.127 / 1.998 / 894 faces, `LODNoShadow=1`), View Pilot, Shadow Volume 0 e 10, Geometry (`class=man`, `prefershadowvolume=1`), Memory (`autocenter=0`), Land Contact, Hit-points e Fire Geometry | idem |
| `A3_character_template.p3d`: mesmos LODs técnicos, idênticos aos do exemplo; nos LODs visuais só **antebraços, mãos e pernas** (pele, seleção `hl`) | idem |
| Seleções: 65 ossos de `OFP2_ManSkeleton` (`Camera` e `neck1` não usados), `camo`, `hl`, `injury_body/hands/legs`, `insignia`, proxies (`weapon`, `pistol`, `binoculars`, `launcher`, `flag`, `equipment`, `backpack`, `glasses`, `headgear`, `hmd`, cabeça `bysta`) | idem |
| Pesos: até **4 ossos por ponto** (Resolução 1: 791 pontos com 1 osso, 1.585 com 2, 651 com 3, 76 com 4). Byte por ponto: `1` = peso total; demais: **peso = (256 − byte)/255** | `inspect_weights.py` |
| Origem do `.p3d` a **1,007 m do chão**; topo do pescoço a 1,580 m; pose em "A" | `inspect_character_ref.py` |
| Proxies `backpack`, `headgear`, `equipment`, `glasses` e cabeça `bysta`: triângulo **identidade** (origem 0,0,0; +Y; +Z), sem osso | `proxy_info.py` |
| Colete: LODs Resolução 1–5, Shadow Volume 0, Geometry vazia (`autocenter=0`); pesos nos ossos do tronco e ombros; `camo`. Config: `Vest_Camo_Base: ItemCore`, `ItemInfo: VestItem`, macro `LOAD` | `A3_vest_example.p3d`, `A3_vest_template.p3d`, `cfgVests.hpp`; jogo: `characters_f` linhas 28944/28966 |
| Mochila: `Bag_Base: ReammoBox` com `isbackpack=1`, `hiddenSelections[]={"Camo"}`, `maximumLoad`, `mass`; patch `A3_Weapons_F_Ammoboxes` | `weapons_f.pbo` → `Ammoboxes\config.bin` (linha 4427 do texto convertido) |
| UV do MLOD: lidas por vértice de face (`u`, `v`); no Blender, `v` invertido (1 − v). **A confirmar** na volta pelo Object Builder | `p3d_mlod.py` |

## 3. Referências visuais

| ID | Arquivo | Descrição | Origem | Uso permitido |
|---|---|---|---|---|
| R1 | `docs/references/img/ref_shako_01_render_baixa_resolucao.png` (228×235) | Render de jogo, em baixa resolução: barretina baixa com cocar/pompom branco e preto, elemento amarelo vertical, pala e jugular | Enviada pelo usuário em 2026-10-09; **origem desconhecida** | Só referência visual |
| R2 | `docs/references/img/ref_shako_02_foto_fwr.png` (344×425) | Foto de barretina (original ou réplica): corpo preto alargado no topo, faixa larga branca de sarja, debrum de couro preto na borda, pompom branco com centro preto sobre haste, monograma de latão (provável "FWR"), faixa inferior e pala de couro envernizado, botão lateral com jugular | Enviada pelo usuário em 2026-10-09; **origem desconhecida** | Só referência visual. **Em 2026-10-09 o usuário indicou R2 como referência principal ("mais assim")** |
| NTW | Pasta de referência e `.pack` em D: | Texturas de mods do Napoleon: Total War | Terceiros; autorização do Eras Mod declarada em 2026-10-09 (§3.2) | Ver §3.2 |
| M1–M4 | `docs/references/img/ref_uniforme_0{1..4}_*_mod.png` (blocos de 512² do atlas `prussia1813_01_diffuse.dds`, BattleMOV11-15) | Casaco (frente), costas de casaco do mesmo atlas, calças cinza com polainas, calças brancas | Eras Mod | Ficha `docs/specs/uniforme_prussiano_infantaria_1813.md` |

Fontes secundárias do uniforme (2026-10-10), detalhes na ficha §3:
- [Gripping Beast / Calpe: Line Musketeers](https://grippingbeast.co.uk/Line_Musketeers--category--1139.html): cores provinciais, platinas, abas vermelhas, calças cinza. A página devolveu 403 à leitura automática (não contornada); só o resumo do buscador foi usado.
- [Richard Knötel (Wikipedia)](https://en.wikipedia.org/wiki/Richard_Kn%C3%B6tel) e [Koller (Uniform), dewiki](https://dewiki.de/Lexikon/Koller_(Uniform)): fonte primária sugerida e terminologia.

Incertezas sobre R2 (para a ficha técnica da Fase 2):
- Não se sabe se é peça original ou réplica, nem a data.
- A leitura "FWR" é uma interpretação visual do monograma, não confirmada.
- A unidade e o período da combinação faixa branca + pompom + monograma não estão identificados. **Nenhum detalhe regimental será inventado.**

### 3.1 Referências históricas a coletar (domínio público, sugeridas e ainda não obtidas)

- Richard Knötel, *Uniformenkunde* (pranchas, 1890–1921).
- Charles Hamilton Smith, *Costume of the Army of the British Empire* (1812–1815), útil para comparação.
- Fontes de museu com fotos e medidas de barretinas prussianas (a identificar, com licença de uso).

---

### 3.2 Autorização do Eras Mod (registrada em 2026-10-09)

| Item | Registro |
|---|---|
| Declaração | Em 2026-10-09 o usuário declarou na conversa ter **autorização dos autores do Eras Mod** para usar as texturas no addon |
| Autor(es), meio e escopo | **Pendente**: o usuário ainda vai informar de quem, por qual meio (mensagem, licença, página) e para qual uso (pessoal? distribuição?) |
| Efeito | As texturas do Eras/NTW deixam de ser só referência visual e **podem ser usadas** em texturas do addon, sempre registradas em `asset_inventory.md` com o arquivo de origem |
| Nomes de variantes | Decisão do usuário: usar **os nomes de regimento do mod**, marcados como "segundo o Eras Mod", e não como fato histórico verificado |

## 4. Pendências de referência

1. Ler diretamente a wiki da Bohemia, confirmar os itens 🔶 e registrar os requisitos de LOD de itens de cabeça e de roupas. Opções: o usuário conclui a verificação de segurança do site no navegador do app, ou o usuário cola o conteúdo.
2. Instalar o **Arma 3 Samples** (Steam → Ferramentas, gratuito; precisa de autorização do usuário) para ter `A3_headgear_example.p3d` e o corpo de referência.
3. Informar a origem de R1 e R2.
4. Identificar historicamente a barretina de R2 com uma fonte confiável, antes da ficha técnica.
