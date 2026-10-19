# Testes e Verificações

Atualizado em 2026-10-09 (briefing "Pipeline Profissional", Fase 1).

Três categorias, como pede o briefing:
1. **Executado**: rodou, com resultado e evidência.
2. **Verificação manual pendente**: depende do usuário numa ferramenta (Object Builder, Blender, aprovação visual).
3. **Não testado no jogo**: tudo o que exige o ARMA 3 aberto.

> Nada do addon foi testado no ARMA 3. Nenhum PBO foi gerado.

`<CLASSE_...>` = nomes definidos na Fase 8; não existem ainda.

---

## 1. Executado

| Data | O que | Resultado | Evidência |
|---|---|---|---|
| 2026-10-09 | Leitura dos cabeçalhos de `characters_f*.pbo` (jogo base e DLCs) | 74 modelos de cabeça listados; nenhum com formato de barretina; 153 `.p3d` de `characters_f` binarizados (`ODOL`) | `asset_inventory.md`, `references.md` |
| 2026-10-09 | Extração de `config.bin` de `characters_f.pbo` e `weapons_f.pbo` + `CfgConvert -txt` | Código de saída 0; 34.470 e 40.033 linhas | `work/a3/configs/` |
| 2026-10-09 | Leitura dos textos internos de `cappatrol.p3d` e `headgear_b_helmet_plain.p3d` | Presença de `head`, `camo`, `OFP2_ManSkeleton`, `autocenter`, `lodnoshadow`, LODs de sombra, `.rvmat` | `references.md` §2 |
| 2026-10-09 | Protótipos exploratórios v1/v2 no Blender (modo headless) | Malhas, renders, `.blend` e `.fbx` gerados sem erro (v2: 5.484 triângulos) | `docs/renders/`, `source/blender/` |
| 2026-10-09 | Revisão visual das renders da v2 | Relevo do feltro e da pala exagerado → corrigido e renderizado de novo | `docs/renders/v2/` |
| — | `build_shako_v3.py` e texturas estilo `v3` | **Não executados** (novo briefing) | — |
| 2026-10-09 | Leitura dos `.p3d` MLOD do Arma 3 Samples (`p3d_mlod_inspect.py`) | LODs, propriedades e seleções do item de cabeça oficial confirmados | `references.md` §2b |
| 2026-10-09 | Importação dos FBX do Samples no Blender | **Falhou**: FBX ASCII e versão 6100 não suportados pelo Blender 5.2; contornado lendo os `.p3d` | Saída do Blender |
| 2026-10-09 | Blockout (`blockout_shako.py`) | 10 peças fechadas, 2.112 triângulos; encaixe sobre a linha da cabeça oficial; comparação com R2 alinhada em base, topo e altura | `docs/reports/shako_pruss_blockout.md`, `docs/reports/img/blockout/` |
| 2026-10-10 | UV (`uv_review.py`): T1/T2 | 0 UV fora do quadro, 0 sobreposições, faces visíveis sem espelhamento; densidades 1.800–4.000 px/m; malha inalterada (M1–M7 repetida) | `docs/reports/shako_pruss_uv_texturas.md`, `shako_pruss_uv_review_output.txt` |
| 2026-10-10 | T4: convenção do mapa normal (`check_normal_convention.py` no template oficial) | OpenGL/+Y (correlação G +0,785; R −0,785) | `shako_pruss_uv_texturas.md` §3 |
| 2026-10-10 | T3 (parte automática): ImageToPAA PNG → PAA e PAA → PNG | 3 arquivos convertidos, código 0, cabeçalhos DXT1/DXT5/DXT1 corretos, volta em 2048² com o conteúdo preservado. **Abrir no TexView 2: manual, pendente** | `source/textures/hcl_shako_pruss/paa/` |
| 2026-10-10 | Variantes da barretina (águia, estrela): M1–M7 (`mesh_review.py`) e UV (`uv_review.py`) | 0 em todos os itens; 5.262 e 5.778 triângulos; 0 faces da frente do distintivo com UV espelhada; regressão do FWR idêntica | `docs/specs/variantes_regimentos_pruss.md` §4.2 |
| 2026-10-10 | UV do uniforme (`uv_uniforme_pruss.py`) | 0 cantos fora do quadro; ≈ 765–810 px/m; 48,9% de ocupação | `variantes_regimentos_pruss.md` §3.1 |
| 2026-10-10 | T3 (parte automática) das variantes: `convert_variants_paa.ps1` | 19 conversões, 0 falhas; cabeçalhos DXT1 (`_co`, `_smdi`) e DXT5 (`_nohq`); volta para PNG em 2048² (diferença média 0,61/255 e 0,20/255). **TexView 2: manual, pendente** | `variantes_regimentos_pruss.md` §5 |
| 2026-10-11 | Jogo reinstalado pelo usuário. Iniciado com `-mod=…\release\@Historical_Clothing` (`release/iniciar_arma3_com_hcl.bat`) e, a pedido do usuário, o mod foi adicionado como **mod local** no Launcher (aba MODS, "Mod local") e marcado em "Mods carregadas" | **G0** ✅ log `.rpt` criado; **G1 (parte do log)** ✅ `@Historical_Clothing` na lista de mods, nenhum erro com `hcl`, sem "Updating base class". Janelas de erro na tela, G2–G12: não verificados | `%LOCALAPPDATA%\Arma 3\arma3_x64_2026-10-11_11-50-14.rpt` |
| 2026-10-11 | **Correções e realismo** (`correcoes_realismo_pruss.md`). Calça: junção assento/pernas sem corte serrilhado (`ajustar_calca.py`). Pesos v2: camadas se movem juntas (axila, manga no punho, gola, topo da polaina, mão escondida no punho, cartucheira rígida, bainha segue a aba, correias da mochila sobre o correame). Botões com sombreamento liso. Dobras do quadril suavizadas. AO assada de novo, sem as mãos | Calça: triângulos assento × pernas se cortando 580 → 0 (as duas diagonais). Teste de movimentos: casaca pela manga 34 → 0 mm em pé (1 ponto a 16 mm sentado); manga pelo punho 13 → 0; gola 7 → 0; polaina 9 → 0 mm. A mão no punho foi conferida em imagens de perto (sentado, em pé, ajoelhado): sai pela abertura. Correame "dentro" da mochila: dentro do corpo fechado, invisível. PAA 0 falhas; binarize com esqueleto nos 8 modelos; `pbo_verify` 67 referências presentes; `conferir_regimentos` 0 problemas; **PBO instalado às 23:13**. Não visto no jogo | `docs/reports/img/correcoes/`, `img/movimentos/teste_movimentos_camadas_v2_output.txt` |
| 2026-10-11 | **Gola corrigida** (`gola_pruss.md`): no jogo, a garganta da cabeça cobria a frente da gola. A abertura era de 190 × 91 mm e virou ~120 × 120 mm; a frente avançou 20–27 mm; o alto da gola ganhou peso no `Neck` | Revisão de malha: 0 autointerseções; gola × platina de 10 para 0 pares visíveis. Equipamento: 0 vértices sob o uniforme. Em pé: 0 contatos queixo × gola; barretinas 0 em todas as poses. PBO verificado e **instalado às 14:52**. Não visto no jogo | `docs/reports/img/gola/` |
| 2026-10-11 | **Defeito achado e corrigido:** os P3D do correame e da mochila de **couro preto** foram binarizados **sem esqueleto**, porque faltava a classe deles no `model.cfg`. Sem esqueleto, não acompanhariam o corpo no jogo. O PBO instalado às 14:19 tem o defeito | `model.cfg` corrigido. `build_mod_pruss.ps1` agora confere `OFP2_ManSkeleton` em todo modelo binarizado: 8/8 com esqueleto. PBO corrigido (14:23) **instalado às 14:23:33**, quando o jogo fechou (cópia idêntica, por hash) | `work/build/hcl/hcl_pruss/*.p3d` |
| 2026-10-11 | **Todos os regimentos possíveis** (`variantes_regimentos_pruss.md` 1.1): 9 casacas verdes (V09–V17), V03 corrigida, 8 barretinas novas, correame e mochila em couro preto | Regressão do gerador da barretina: `estrela_prata` idêntica (diferença 0,0); 49 PAA com cabeçalho certo; config 33 itens + 17 soldados + 2 mochilas (`CfgConvert` 0); binarize 0 (avisos só dos materiais do jogo); PBO verificado: 68 arquivos, 8 modelos ODOL, 51 PAA, 67 referências, nenhuma faltando. **Instalação:** o Arma 3 foi aberto às 14:05 e travou o arquivo; o PBO novo foi trocado sozinho quando o jogo fechou (14:19:33), com cópia idêntica (hash). Não visto no jogo | `docs/reports/img/regimentos/` |
| 2026-10-11 | **Primeira imagem no jogo** (captura do usuário, Editor, sessão 13:10–13:42, com outros mods do século XIX carregados junto). Versão de **2026-10-10** do PBO | **G2 (parcial)** ✅ uniforme com textura, barretina "estrela" e correame/correias aparecem no soldado, no lugar certo, de pé. Log: nenhuma linha de erro com `hcl`; os avisos `GunParticles` são de outro mod. Depois o jogo foi fechado e o PBO novo foi trocado (cópia do antigo em `release/_atualizacao/hcl_pruss_versao_2026-10-10.pbo`) | Captura do usuário; `Arma3_x64_2026-10-11_13-10-49.rpt` |
| 2026-10-11 | **Detalhe e texturas** (`detalhe_texturas_pruss.md`): malha de produção do correame (3.212 triângulos) e da mochila (3.776); texturas próprias; texturas v2 do uniforme; pesos v1; addon refeito | 0 vértices do equipamento sob o uniforme; UV 0..1, ~2.500 e ~1.790 px/m; 25 PAA com cabeçalho certo; teste de movimentos: barretinas 0 colisões; alvado × correia de ombro (20 mm) achado e corrigido; P3D, config e binarize sem erro novo; PBO novo verificado (41 arquivos, 40 referências presentes). **O PBO em `Addons` não foi trocado: o Arma 3 estava aberto e trava o arquivo**; o novo ficou em `release/_atualizacao/` (troca: `release/atualizar_mod_teste.bat`). Não visto no jogo | `docs/reports/detalhe_texturas_pruss.md`, `img/texturas/`, `img/equipamento/` |
| 2026-10-10 | **Addon de teste `hcl_pruss.pbo`** (`build_mod_pruss.ps1`): MLOD próprio (gravador idêntico byte a byte nos 34 MLOD dos Samples) → `binarize` oficial → `CfgConvert` → `FileBank` | **C1** ✅ config sem erro; **P1** ✅ PBO gerado; **P2** ✅ prefixo `hcl\hcl_pruss`, 33 arquivos, sem fontes, 32 referências internas presentes; 6 modelos `ODOL` com `OFP2_ManSkeleton`. Avisos: material das mãos (do jogo) não lido na binarização. **G1–G12 não executados** (jogo desinstalado às ~17:25) | `docs/reports/mod_teste_pruss.md`, `work/build/binarize_log.txt` |
| 2026-10-10 | **Teste de movimentos fora do jogo** (`teste_movimentos.py`). 8 animações oficiais dos Arma 3 Samples (`RTM_0101`) aplicadas ao uniforme, às 3 malhas de barretina e ao correame/mochila (blockout), com pesos v0 transferidos do corpo oficial | Barretinas: 0 contatos em todas as animações. Problemas P1–P9 listados (mãos pelo punho até 21 mm sentado; axila; abas × cartucheira; correias × correame). 4 defeitos achados e corrigidos durante o teste. **Não é teste no jogo**; correr e andar não testados (animações do jogo binarizadas) | `docs/reports/teste_movimentos_pruss.md`, `img/movimentos/` |
| 2026-10-09 | Malha de produção + revisão técnica M1–M7 (`mesh_review.py`), 3 execuções | Final: 8 ilhas fechadas, normais corretas, 0 duplicatas, 0 faces degeneradas, 0 interseções, ≤ 4 vértices por face, transformações aplicadas, 5.194 triângulos. Defeitos das execuções 1–2 corrigidos | `docs/reports/shako_pruss_mesh_review.md`, `shako_pruss_mesh_review_output.txt` |
| 2026-10-12 | **Gola v2** (`gola_pruss_v2.md`): gola das 17 casacas prussianas refeita em volta da cabeça do jogo (`TemplateRTM\bust.p3d`) | Folga pescoço → gola: −44 mm → +2,7 mm; pontos do pescoço fora da gola 54 → 0; teste de movimentos com a cabeça do jogo (repouso 2 pares, sentado 74, morte 116); 17 texturas refeitas; PBO `hcl_pruss` **instalado às 12:35** (jogo fechado), `pbo_verify` 67 referências, nenhuma faltando. Não visto no jogo | `docs/reports/gola_pruss_v2.md`, `img/gola_bust/` |
| 2026-10-12 | **Addon de teste francês `hcl_fr.pbo`** (`convert_fr_paa.ps1`, `build_mod_fr.ps1`): uniforme F01, 6 barretinas, correame, havresac | 27/27 PAA com cabeçalho certo; P3D lidos de volta; binarize 0, 9/9 modelos com `OFP2_ManSkeleton` (avisos só dos 3 materiais do jogo, como na Prússia); `CfgConvert` 0 (config e 9 rvmat); PBO de 44,2 MB em `release/@Historical_Clothing/Addons/`; `pbo_verify`: prefixo `hcl\hcl_fr`, 46 arquivos, sem fontes, 45 referências, nenhuma faltando. **G1–G12 não executados** | `docs/reports/frances_1812_prototipo.md`, `work/build/binarize_fr_log.txt` |
| 2026-10-12 | **França: mais regimentos, capote de inverno, barretinas da época** (`frances_1812_prototipo.md` §8) | Casacas F02–F04 e capote W01–W04; capote: 0 pontos da calça fora da saia em repouso, 27 pontos do correame encostados até 2,1 mm; teste de movimentos do capote, pior caso 38,9 mm ajoelhado (casaco longo); barretinas com placa traçada, escamas e plumet v3; PAA 36/36; binarize 0, 10/10 modelos com esqueleto; `CfgConvert` 0; `hcl_fr.pbo` 61,2 MB, 57 arquivos, 56 referências, nenhuma faltando. **G1–G12 não executados** | `docs/reports/img/soldado_fr/`, `work/teste_movimentos_fr_capote_c.log` |
| 2026-10-12 | **França: casacas de granadeiro e voltigeur com dragonas** (`frances_1812_prototipo.md` §9) | Casaca de elite 16.414 tris, 0 vértices da franja/meia-lua dentro do pano; pesos: corpo rígido, nenhuma aresta fora do limite nas 8 animações (franja toca a manga até 6 mm em poses extremas); PAA 40/40; binarize 0, 11/11 modelos com esqueleto; `CfgConvert` 0; `hcl_fr.pbo` 68,7 MB, 62 referências, nenhuma faltando. **G1–G12 não executados** | `docs/reports/img/soldado_fr/elite_fr_*`, `work/teste_movimentos_fr_elite.log` |

## 2. Verificações previstas por fase

### 2.1 Integridade da malha (Fase 5): o Claude executa por script no Blender

| ID | Verificação | Critério | Estado |
|---|---|---|---|
| M1 | Normais e orientação | 0 faces invertidas em relação às direções esperadas | ⏳ |
| M2 | Vértices duplicados | 0, exceto divisões justificadas (UV/arestas duras), contadas e listadas | ⏳ |
| M3 | Buracos e arestas não-manifold | Cada aresta de borda justificada | ⏳ |
| M4 | Faces de área zero e geometria solta | 0 | ⏳ |
| M5 | Interseções acidentais (BVH) | 0 não justificadas | ⏳ |
| M6 | Transformações aplicadas, escala, orientação | Escala (1,1,1), rotação 0, frente −Y | ⏳ |
| M7 | Distribuição de polígonos | Dentro do orçamento (`modeling_standards.md` §3) | ⏳ |

### 2.2 Texturas e materiais (Fase 6)

| ID | Verificação | Critério | Executor | Estado |
|---|---|---|---|---|
| T1 | Dimensões em potência de 2 | Sim | Claude | ⏳ |
| T2 | Densidade de texel | Dentro do alvo, sem ilhas distorcidas | Claude | ⏳ |
| T3 | Conversão `.paa` | ImageToPAA sem erro; abre no TexView 2 | Claude + usuário | ⏳ |
| T4 | Convenção do normal map igual à dos `_nohq` oficiais | Mesma orientação | Claude | ⏳ |

### 2.3 Conversão e configuração (Fases 7–8)

| ID | Verificação | Critério | Executor | Estado |
|---|---|---|---|---|
| B1 | FBX importa no Object Builder | Malha completa, escala em metros, frente correta, UV preservado | **Usuário** | ⏳ manual |
| B2 | `.p3d` válido | Reabre sem erro; LODs, seleções e propriedades exigidos presentes; Buldozer mostra todos os LODs | **Usuário** | ⏳ manual |
| C1 | Sintaxe do `config.cpp` | `CfgConvert -bin` com código de saída 0 | Claude | ⏳ |
| C2 | Caminhos do config batem com os arquivos e o prefixo | 100% | Claude | ⏳ |
| P1 | Addon Builder gera o PBO | PBO existe; log sem erro | Claude/usuário | ⏳ |
| P2 | Conteúdo do PBO | Prefixo correto; sem `source/` nem `work/` | Claude | ⏳ |

### 2.4 Aprovações visuais (manuais)

| ID | Verificação | Executor | Estado |
|---|---|---|---|
| V1 | Ficha técnica aprovada (Fase 2) | Usuário | ⏳ |
| V2 | Blockout aprovado nas vistas ortográficas sobre o corpo de referência (Fase 3) | Usuário | ⏳ |
| V3 | Malha de produção aprovada (Fase 4) | Usuário | ⏳ |
| V4 | Aparência sob iluminações diferentes: dia, nublado, entardecer, interior (renders do Blender e, depois, no jogo) | Usuário | ⏳ |

## 3. Não testado no jogo (Fase 9)

Pré-requisito G0: logs `.rpt` ativos (hoje `%LOCALAPPDATA%\Arma 3` não existe).

| ID | Teste | Como | Esperado |
|---|---|---|---|
| G1 | Carregamento do addon | Iniciar o jogo só com `@Historical_Clothing` | Sem caixas de erro |
| G2 | Patch registrado | Console: `isClass (configFile >> "CfgPatches" >> "<PATCH>")` | `true` |
| G3 | Item disponível no Arsenal | Arsenal → categoria correspondente | Item listado |
| G4 | Vestir e remover (cabeça) | `player addHeadgear "<CLASSE_BARRETINA>"; headgear player` → `removeHeadgear player` | Retorna a classe, depois `""` |
| G5 | Vestir e remover (uniforme) | `player forceAddUniform "<CLASSE_UNIFORME>"; uniform player` → `removeUniform player` | Retorna a classe, depois `""` |
| G6 | Posicionamento da barretina | Capturas de frente, lado e costas; em pé, agachado, deitado; olhando para cima e para baixo | Sem flutuar nem atravessar a cabeça |
| G7 | Deformações e interseções (roupas) | Animações de correr, agachar, deitar, mirar | Sem atravessar o corpo |
| G8 | Texturas no jogo | `getObjectTextures player` + capturas a 1 m e a 20 m | Caminhos `HCL` corretos; sem textura branca ou xadrez |
| G9 | Iluminação | Capturas de dia, entardecer, noite e interior | Materiais coerentes |
| G10 | Primeira pessoa | Olhar ao redor com a barretina | Nada bloqueia a visão (ViewPilot) |
| G11 | Logs | `.rpt` sem `No entry`, `Cannot open`, `Warning Message` ou erros com `hcl` | 0 linhas relacionadas |
| G12 | Sem facção nova | Listas do editor Eden | Nenhuma facção/unidade do addon |

## 4. Regras

1. Um teste só vira ✅ com evidência registrada (saída, trecho de log ou captura).
2. Testes manuais ficam ⏳ até o usuário relatar o resultado.
3. Falhas geram uma correção e uma nova execução; não são ignoradas.

## 5. Lote de 2026-10-13: Velha Guarda, barretinas novas e boné (não testado no jogo)

**Antes de testar:** abra o Arma 3 **sem BattlEye** (opção do Launcher) e **nunca** com o Blender trabalhando. Em 12/10 houve duas telas azuis no driver do BattlEye (`BEDaisy.sys`); ver `docs/reports/guarda_barretinas_lote.md` §4.

Texto para o console de depuração (vestir um granadeiro da Velha Guarda):

```sqf
player forceAddUniform "HCL_U_Fr1812_Guarda_Granadeiro"; removeHeadgear player; player addHeadgear "HCL_H_Fr1812_Guarda_Bonnet_Granadeiro_Gala";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| L1 | Casaca da Guarda | `HCL_U_Fr1812_Guarda_Granadeiro`, `HCL_U_Fr1812_Guarda_Cacador` | Abas longas sentado, ajoelhado e deitado; dragonas com o braço erguido |
| L2 | Chapéu de pele | `HCL_H_Fr1812_Guarda_Bonnet_Granadeiro_Gala`, `..._Granadeiro_Campanha`, `..._Cacador_Gala` | Pelo a 1 m; troca para a Res 2 (sem mechas) ao se afastar; desempenho (22,6 mil triângulos) |
| L3 | Barretinas francesas novas | `HCL_H_Fr1812_Fuzileiro_Losango_1aComp`, `..._LosangoBranco_1aComp`, `HCL_H_Fr1812_Fuzileiro_2aComp` … `_4aComp` | Pompom da companhia; placa em losango |
| L4 | Plumets de gala maiores | `HCL_H_Fr1812_Granadeiro_Gala`, `HCL_H_Fr1812_Voltigeur_Gala` | Volume e altura (topo a 1,33 m) |
| L5 | Prússia: plumet verde e Stutz | `HCL_H_Pruss1813_*_PlumetVerde` (14), `HCL_H_Pruss1813_Estrela_Prata_StutzGarde` | Pluma no lugar; textura da barretina trocada pela classe |
| L6 | Boné da Landwehr | `HCL_H_Pruss1813_Bone_C01` … `C05` | Encaixe na cabeça; cores da faixa |
| L7 | Infantaria ligeira e regimentos numerados (13/10) | `HCL_U_Fr1812_Ligeira_Cacador` / `_Carabineiro` / `_Voltigeur`; `HCL_H_Fr1812_Ligeira_Carabineiro_Gala`, `..._Voltigeur_Gala`; `HCL_H_Fr1812_Linha_018` / `_046` / `_057` / `_084` | Número legível na placa a 1–2 m; plumet v4 (penas com nervura); topo de couro, forro e pala debruada |

## 6. Reino Unido `hcl_uk.pbo` (2026-10-18; não testado no jogo)

Detalhes em `docs/reports/reino_unido_prototipo.md` §4.

**Executado fora do jogo:**
- pesos das 4 casacas (soma 1, no máximo 4 ossos);
- PAA: 53 conversões, 0 falhas;
- binarize 0, com 15/15 modelos com `OFP2_ManSkeleton` (avisos só dos 3 materiais do jogo);
- `CfgConvert` 0;
- `pbo_verify`: prefixo `hcl\hcl_uk`, 84 arquivos, 83 referências, nenhuma faltando;
- kilt: 0 pontos da calça e 1 de 676 pontos das abas com o kilt por fora.

**Antes de testar:** abra o Arma 3 **sem BattlEye** e **nunca** com o Blender trabalhando.

Comando para o console (Highlander do 92nd):

```sqf
player forceAddUniform "HCL_U_UK1812_K01"; removeHeadgear player; player addHeadgear "HCL_H_UK1812_Bonnet_Highland"; player addVest "HCL_V_UK1812_Correame"; player addBackpack "HCL_B_UK1812_Mochila";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| U1 | Casaca de linha | `HCL_U_UK1812_L01` … `L04` | Presilhas de galão em pares; gola e punhos nas 4 cores de vista |
| U2 | Companhias de flanco | `HCL_U_UK1812_FL01` … `FL04` | Wings com o braço erguido; franja sem atravessar a manga |
| U3 | Rifles | `HCL_U_UK1812_R01`, `HCL_V_UK1812_Correame_Preto`, `HCL_H_UK1812_Stovepipe_Rifles` | 3 fileiras de botões; correame preto; corneta na barretina |
| U4 | Highlanders | `HCL_U_UK1812_K01`, `K02` | Kilt sentado, ajoelhado e correndo; **abas por cima do kilt**; joelho e meias xadrez |
| U5 | Barretinas | `HCL_H_UK1812_Belgic_*` (3), `HCL_H_UK1812_Stovepipe_*` (5) | Placa legível a 1–2 m; "28" atrás na `_28th`; cordões |
| U6 | Bonnet de penas | `HCL_H_UK1812_Bonnet_Highland` | Penas sem cobrir o rosto; caudas à direita; Res 2 ao se afastar; desempenho (24 mil triângulos) |
| U7 | Equipamento | `HCL_V_UK1812_Correame`, `HCL_B_UK1812_Mochila` | Correias acompanhando a casaca |

**Resultado no jogo (relato do usuário, 2026-10-18):** *"já testei, ficou bom"*. O teste foi feito pelo usuário, sem capturas nem log anexados, e não houve detalhe por item. U1–U7 ficam aprovados de forma geral pelo relato.

## 7. Portugal no `hcl_uk.pbo` (2026-10-19; não testado no jogo)

Detalhes em `docs/reports/portugal_prototipo.md` §2.

**Executado fora do jogo:**
- PAA: 141 conversões, 0 falhas;
- binarize 0, com 21/21 modelos com esqueleto;
- `CfgConvert` 0;
- `pbo_verify`: 185 arquivos, 184 referências, nenhuma faltando;
- o número do regimento aparece na faixa da barretina no render.

**Antes de testar:** abra o Arma 3 **sem BattlEye** e **nunca** com o Blender trabalhando.

Comando para o console (granadeiro do 17º, 2º de Elvas):

```sqf
player forceAddUniform "HCL_U_POR1812_L17"; removeHeadgear player; player addHeadgear "HCL_H_POR1812_Stovepipe_Granadeiro_17"; player addVest "HCL_V_UK1812_Correame"; player addBackpack "HCL_B_UK1812_Mochila";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| P1 | Jaquetas de linha | `HCL_U_POR1812_L01` … `L24` | Gola, punhos e viras nas cores de cada regimento |
| P2 | Jaquetas de Caçadores | `HCL_U_POR1812_C01` … `C12` | Alamares pretos; correame preto (`HCL_V_UK1812_Correame_Preto`) |
| P3 | **Número na barretina** | `HCL_H_POR1812_Stovepipe_*_NN` | O número muda com a classe (seleção escondida `numero`); legível a 1–2 m; troca para a Res 2 sem perder o número |
| P4 | Barretinas | batalhão, granadeiros, ligeira, Caçadores | Placa oval, granada ou corneta, cocar, pluma; encaixe na cabeça |

## 8. Brunswick no `hcl_uk.pbo` (2026-10-19; não testado no jogo)

Detalhes em `docs/reports/brunswick_prototipo.md` §3.

**Executado fora do jogo:**
- PAA: 167 conversões, 0 falhas;
- binarize 0, com 26/26 modelos com esqueleto;
- `pbo_verify`: 221 arquivos, 220 referências, nenhuma faltando.

**Antes de testar:** abra o Arma 3 **sem BattlEye** e **nunca** com o Blender trabalhando.

Comando para o console (2º batalhão de linha):

```sqf
player forceAddUniform "HCL_U_BRU1815_B06"; removeHeadgear player; player addHeadgear "HCL_H_BRU1815_Kiwer_Linha_2"; player addVest "HCL_V_UK1812_Correame_Preto"; player addBackpack "HCL_B_BRU1815_Tornister";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| B1 | Dólmãs | `HCL_U_BRU1815_B01` … `B08` | Gola, platinas e vivo da calça na cor do batalhão; saia curta ao sentar e ajoelhar |
| B2 | Kiwer do Leib-Bataillon | `HCL_H_BRU1815_Kiwer_Leib` | Crina sem atravessar a cabeça; caveira legível; desempenho (14 mil triângulos) |
| B3 | Kiwer da linha | `HCL_H_BRU1815_Kiwer_Linha_1` / `_2` / `_3` | Número certo no escudo, também na Res 2 |
| B4 | Kiwer ligeiro e Avantgarde | `HCL_H_BRU1815_Kiwer_Ligeiro`, `_Avantgarde` | Corneta de metal branco, pompom, pluma |
| B5 | Mochila | `HCL_B_BRU1815_Tornister` | Cavalo na aba; correias pretas |

**2026-10-19 (tarde):** jugular de couro em todas as barretinas do `hcl_uk` (menos o bonnet highland) e crina nova do Leib-Bataillon. PBO de 194,7 MB; `pbo_verify` sem referência faltando. Não testado no jogo. Observar: **J1** a jugular sob o queixo não atravessa o rosto ao virar a cabeça, mirar ou deitar (ela é rígida no osso `Head`); **J2** a crina do Leib não bloqueia a visão em primeira pessoa (190 mm de altura).
