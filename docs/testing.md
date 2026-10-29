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
| 2026-10-13 | **Suíços a serviço da França, addon `hcl_suica.pbo`** (`docs/reports/suica_1812.md`): 4 regimentos × fuzileiro, granadeiro e voltigeur; chapéu de pele do granadeiro com placa de granada; barretinas francesas de fuzileiro (4 companhias) e voltigeur | 12 texturas de casaca pintadas; PAA 34/34 com cabeçalho certo; binarize 0, 7/7 modelos com `OFP2_ManSkeleton` (avisos só dos 3 materiais do jogo); `CfgConvert` 0 (config e 7 rvmat); PBO de 59,2 MB em `release/@Historical_Clothing/Addons/` às 18:56; `pbo_verify`: prefixo `hcl\hcl_suica`, 48 referências, nenhuma faltando. Sem dependência do `hcl_fr`. **G1–G12 não executados** | `docs/reports/img/suica/`, `work/build_suica.log`, `work/build/binarize_suica_log.txt` |
| 2026-10-18 | **Ducado de Varsóvia, addon `hcl_varsovia.pbo`** (`docs/reports/varsovia_1810.md`): regulamento de 1810, 7º e 9º; mais regimentos (1º, 13º, 15º, czapkas com placa numerada, chapéus de pele do 5º, 6º e lisos) | PAA 54/54; binarize 0, 10/10 modelos com `OFP2_ManSkeleton`; `CfgConvert` 0 (config e 10 rvmat); PBO de 93,1 MB às 20:59; `pbo_verify`: prefixo `hcl\hcl_varsovia`, 74 referências, nenhuma faltando; close-up das placas 2, 12, 17 e 1 no modelo: números na direção certa. **Não testado no jogo** | `docs/reports/img/varsovia/`, `work/build_varsovia.log`, `work/cadeia_varsovia6.log` |
| 2026-10-18 | **Reino da Itália e Reino de Nápoles, addon `hcl_italia.pbo`** (`docs/reports/italia_1812.md`): 7 regimentos italianos e 4 napolitanos de linha, granadeiros e voltigeurs do 3º e 5º italianos e do 7º napolitano; barretinas com placa losango e escudo, chapéus de pele | Casacas 17; PAA 63/63; binarize 0, 16/16 modelos com `OFP2_ManSkeleton`; `CfgConvert` 0 (config e 16 rvmat); PBO de 119,5 MB às 22:51; `pbo_verify`: prefixo `hcl\hcl_italia`, 95 referências, nenhuma faltando. **Não testado no jogo** | `docs/reports/img/italia/`, `work/build_italia.log`, `work/cadeia_italia1.log` |

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

## 6. Suíços a serviço da França, `hcl_suica.pbo` (2026-10-13, não testado no jogo)

**Antes de testar:** Arma 3 **sem BattlEye** e sem o Blender trabalhando (ver §5). O `hcl_suica` não precisa do `hcl_fr`.

Texto para o console de depuração (granadeiro do 1º Suíço):

```sqf
player forceAddUniform "HCL_U_Suica1812_Granadeiro_S1"; removeHeadgear player; player addHeadgear "HCL_H_Suica1812_Bonnet_Granadeiro_Gala";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| S1 | Casacas de linha | `HCL_U_Suica1812_S1` … `_S4` | Vistas amarela, azul-real, preta e azul-celeste; vivos |
| S2 | Casacas de elite | `HCL_U_Suica1812_Granadeiro_S1` … `_S4`, `HCL_U_Suica1812_Voltigeur_S1` … `_S4` | Dragonas com o braço erguido; granadas e cornetas nas viradas |
| S3 | Chapéu de pele suíço | `HCL_H_Suica1812_Bonnet_Granadeiro_Gala`, `..._Campanha` | Placa com granada legível a 1–2 m; troca para a Res 2; desempenho (46 mil triângulos na gala) |
| S4 | Barretinas | `HCL_H_Suica1812_Fuzileiro_1aComp` … `_4aComp`, `HCL_H_Suica1812_Voltigeur_Gala`, `..._Campanha` | Mesmo modelo da França; pompom da companhia |
| S5 | Nomes no Arsenal | todos | Inglês; 2º e 4º com "facing colour unconfirmed" |

## 7. Ducado de Varsóvia, `hcl_varsovia.pbo` (2026-10-18, não testado no jogo)

**Antes de testar:** Arma 3 **sem BattlEye** e sem o Blender trabalhando (ver §5). O `hcl_varsovia` não precisa do `hcl_fr`. Relatório: `docs/reports/varsovia_1810.md`.

Texto para o console de depuração (fuzileiro do regulamento de 1810):

```sqf
player forceAddUniform "HCL_U_Varsovia1810_L1810"; removeHeadgear player; player addHeadgear "HCL_H_Varsovia1810_Czapka_Fuzileiro";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| V1 | Kurtkas | `HCL_U_Varsovia1810_L1810`, `_R07`, `_R09`, `_Granadeiro_L1810`, `_Voltigeur_L1810` | Lapelas brancas, gola e punhos carmesim; botões brancos no 7º e 9º; gola amarela do voltigeur |
| V2 | Czapka | `HCL_H_Varsovia1810_Czapka_Fuzileiro`, `..._Czapka_Voltigeur` | Topo quadrado sem atravessar nada ao olhar para cima/baixo; águia e "4" legíveis a 1–2 m; troca para a Res 2 |
| V3 | Chapéu de pele | `HCL_H_Varsovia1810_Bonnet_Granadeiro_Gala`, `..._Campanha` | Águia branca sobre a placa de latão; cocar branco; desempenho (47 mil triângulos na gala) |
| V4 | Nomes no Arsenal | todos | Inglês; "7th/9th Infantry Regiment", "1810 regulation" |
| V5 | Mais regimentos: casacas | `HCL_U_Varsovia1810_R13`, `_R15`, `_Fuzileiro_R01`, `_Granadeiro_R13`, `_Voltigeur_R13`, `_Granadeiro_R15`, `_Voltigeur_R15` | Casaca branca com azul do 13º; lapelas carmesim e platinas amarelas do 15º; dragonas brancas com franja do 1º |
| V6 | Czapkas numeradas | `HCL_H_Varsovia1810_Czapka_Fuzileiro_R01` … `_R17` | O número da placa **lê na direção certa** (na textura está espelhado de propósito); sem mancha onde estava o "4"; kita preta no 1º |
| V7 | Chapéus de pele do 5º, 6º e liso | `..._Bonnet_Granadeiro_R05`, `_R06`, `_Lisa` | Sem placa; granada de latão só no 5º; cordões carmesim (5º, 6º) e brancos (liso) |

## 8. Reino da Itália e Reino de Nápoles, `hcl_italia.pbo` (2026-10-18, não testado no jogo)

**Antes de testar:** Arma 3 **sem BattlEye** e sem o Blender trabalhando (ver §5). O `hcl_italia` não precisa do `hcl_fr`. Relatório: `docs/reports/italia_1812.md`.

Texto para o console de depuração (fuzileiro do 5º italiano e do 7º napolitano):

```sqf
player forceAddUniform "HCL_U_Italia1812_IT05"; removeHeadgear player; player addHeadgear "HCL_H_Italia1812_Shako_Italia_Fuzileiro_1aComp";
player forceAddUniform "HCL_U_Italia1812_NA07"; removeHeadgear player; player addHeadgear "HCL_H_Italia1812_Shako_Napoles_Fuzileiro_R07";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| I1 | Casacas italianas | `HCL_U_Italia1812_IT01` … `_IT07`, `_Granadeiro_IT03/IT05`, `_Voltigeur_IT03/IT05` | Branco não estourado ao sol; gola, lapelas e canhões de cada regimento; dragonas verdes com crescente amarelo do voltigeur |
| I2 | Casacas napolitanas | `HCL_U_Italia1812_NA01/02/05/07`, `_Granadeiro_NA07`, `_Voltigeur_NA07` | Vivos brancos nos canhões e viras; dragonas amarelas do voltigeur |
| I3 | Barretinas | `HCL_H_Italia1812_Shako_Italia_*`, `..._Shako_Napoles_*` | Águia no losango e "N" no escudo legíveis a 1–2 m; cocar italiano (vermelho, branco, verde) e napolitano (branco, amaranto); troca para a Res 2 |
| I4 | Chapéus de pele | `..._Bonnet_Italia_Granadeiro_Gala/Campanha`, `..._Bonnet_Napoles_Granadeiro_Gala/Campanha` | Placa de granada só na Itália; cordões brancos (Itália) e vermelhos (Nápoles); desempenho (46 mil triângulos na gala) |
| I5 | Nomes no Arsenal | todos | Inglês; "Kingdom of Italy / Naples, Nth Line Infantry Regiment" |

**Lote 2 (2026-10-18 23:51, `hcl_italia.pbo` 151,2 MB, 17/17 com esqueleto, 121 referências, nenhuma faltando; não testado no jogo):**

| ID | Item | Classes | Observar |
|---|---|---|---|
| I6 | Infantaria ligeira | `HCL_U_Italia1812_LE01/LE03/LE04`, `_Carabiniere_LE01/LE03/LEX`, `_Voltigeur_LE01/LE04/LEX`, `HCL_H_Italia1812_Bonnet_Italia_Carabineiro_Gala` | Verde-escuro sem virar preto à sombra; golas vermelha, branca, violeta e amarela; calça verde |
| I7 | Outros corpos | `_DAL`, `_Granadeiro_DAL`, `_RES`, `_MIL`, `_VOL`, `_BRE`, `_DRA`, `_ART` | Azul-claro da Guarda de Milão; lapelas rosa dos dragões; calça cinza de Brescia |
| I8 | Linha (correções e oficiais) | `_Voltigeur_IT03/IT05` (agora verdes), `_Granadeiro_IT06`, `_Oficial_IT01/IT04`, `_Oficial_Granadeiro_IT05` | Dragonas de prata dos oficiais |

## 10. Confederação do Reno, lote 1 (Württemberg e Baviera), `hcl_reno.pbo` (2026-10-20, não testado no jogo)

Montagem: 55,3 MB, 3/3 modelos com esqueleto, `pbo_verify` com 45 referências, nenhuma faltando. Relatório: `docs/reports/reno_1811.md`. O `hcl_reno` não precisa do `hcl_fr`.

```sqf
player forceAddUniform "HCL_U_Reno1811_WUE01"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Raupenhelm_Wurttemberg";
player forceAddUniform "HCL_U_Reno1811_BAV07"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Raupenhelm_Baviera";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| R1 | Capacete de lagarta (Raupenhelm) | `HCL_H_Reno1811_Raupenhelm_Wurttemberg`, `_Baviera` | Encaixe na cabeça (calota 3 cm acima); crista sem atravessar a mochila nem o pescoço ao olhar para cima; placa (brasão / oval coroado) legível; desempenho (33 mil triângulos; a Res 2 não tem as mechas) |
| R2 | Casacas de Württemberg | `HCL_U_Reno1811_WUE01` … `_WUE09`, `_WUE10P`, `_WUE10A`, `_WUEJK` | Azul-escuro que não fique preto; golas amarela, laranja, branca, rosa, azul-clara e vermelha |
| R3 | Casacas da Baviera | `HCL_U_Reno1811_BAV01` … `_BAV13`, `_BAV11L/V/P`, `_BAVL1` … `_BAVL7` | Azul-claro; lapelas de cada regimento; ligeiros verdes com calça cinza |
| R4 | Nomes no Arsenal | todos | Inglês: "Wuerttemberg / Bavaria, Nth Line Infantry Regiment 'nome'" |

## 9. França, variantes pedidas pelo usuário (2026-10-19, `hcl_fr.pbo` remontado, não testado no jogo)

O `hcl_fr` foi remontado com os scripts deste worktree (`build_mod_fr.ps1 <raiz> <pasta de scripts>`, parâmetro novo e opcional). 147,5 MB; Binarize 0, 19 modelos com esqueleto; `pbo_verify`: 122 referências, nenhuma faltando. As duas peças só mudam a textura `_co` (mesmo modelo); não têm fonte histórica (variante do usuário).

| ID | Item | Classe | Observar |
|---|---|---|---|
| F-A1 | Barretina de carabineiro de ligeira, azul-escura | `HCL_H_Fr1812_Ligeira_Carabineiro_Gala_Azul` | Plumet, galões, divisas e cordões azul-escuros; o cocar continua tricolor (`variantes_cor_shako_fr.py`) |
| F-A2 | Granadeiro de casaca verde | `HCL_U_Fr1812_Granadeiro_F01_Verde` | Casaca verde, canhões vermelhos, dragonas azuis |

```sqf
player forceAddUniform "HCL_U_Fr1812_Granadeiro_F01_Verde"; removeHeadgear player; player addHeadgear "HCL_H_Fr1812_Ligeira_Carabineiro_Gala_Azul";
```

## 11. Barretinas de pelo renovadas e crista nova do capacete de lagarta (2026-10-27, não testado no jogo)

Pedidos do usuário: "renova as bearskins" (todas, inclusive o Reino Unido), "a parte de trás está errada", "na frente é mais alto e atrás mais baixo", "centraliza mais a parte circular vermelha"; e, no capacete de lagarta, "está de trás para frente".

- Pelo v6 (`source/scripts/pelo_v6.py`): mechas estreitas que se abrem em três pontas finas e uma textura de fios finos, no lugar das mechas largas (que pareciam telhas).
- Barretinas da Guarda, Suíça, Varsóvia, Itália e Nápoles: a frente ficou mais alta e as costas 8 % mais baixas. Antes as costas eram mais altas (35/39 cm, segundo a Wikipédia francesa); o pedido do usuário prevalece. Também sumiu a faixa lisa que descia pelas costas embaixo da calota (erro antigo do teste da calota). A calota vermelha fica perto do centro do topo, inteira à vista, e o pelo em volta dela aponta para fora.
- Capacete de lagarta (Württemberg, Baviera): o P3D não estava invertido (a frente está em −Z, igual às barretinas e aos pés do personagem de exemplo). O problema era a crista. Agora a massa fica na frente, enrolando sobre a placa, e a cauda é fina e termina alta.

| PBO | Tamanho | Verificação fora do jogo |
|---|---|---|
| `hcl_fr.pbo` | 147,7 MB | 122 referências, nenhuma faltando |
| `hcl_italia.pbo` | 151,9 MB | 121 referências, nenhuma faltando |
| `hcl_suica.pbo` | 59,3 MB | 48 referências, nenhuma faltando |
| `hcl_varsovia.pbo` | 93,6 MB | 74 referências, nenhuma faltando |
| `hcl_uk.pbo` | 223,2 MB | 30 modelos com esqueleto, 244 referências, nenhuma faltando |
| `hcl_reno.pbo` | 55,3 MB | 45 referências, nenhuma faltando |

```sqf
removeHeadgear player; player addHeadgear "HCL_H_Fr1812_Guarda_Bonnet_Granadeiro_Gala";
removeHeadgear player; player addHeadgear "HCL_H_Suica1812_Bonnet_Granadeiro_Gala";
removeHeadgear player; player addHeadgear "HCL_H_Varsovia1810_Bonnet_Granadeiro_Gala";
removeHeadgear player; player addHeadgear "HCL_H_Italia1812_Bonnet_Italia_Granadeiro_Gala";
removeHeadgear player; player addHeadgear "HCL_H_UK1812_Bonnet_Highland";
removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Raupenhelm_Wurttemberg";
```

| ID | Item | Observar |
|---|---|---|
| B1 | Pelo das barretinas | Mechas finas, sem cara de telha; desempenho (cerca de 48 mil triângulos na Res 1) |
| B2 | Costas | Pelo contínuo até a borda, sem faixa lisa; o topo desce para trás |
| B3 | Calota vermelha | Perto do centro do topo, inteira, sem pelo nem pele passando por cima |
| B4 | Capacete de lagarta | Crista com a massa na frente e enrolada sobre a placa; a cauda não encosta na nuca |

## 12. Confederação do Reno, lote 2 (Saxônia 1810), `hcl_reno.pbo` (2026-10-28, não testado no jogo)

Montagem: 96,8 MB, 8/8 modelos com esqueleto (casaca, 2 capacetes de lagarta, 5 barretinas saxônicas), `pbo_verify` com 80 referências, nenhuma faltando. Os avisos "Cannot load material" de `hl_white_bald_muscular`, `meat` e `meatbones` são materiais do jogo usados pelo modelo dos Samples e aparecem em todas as montagens. Relatório: `docs/reports/reno_1811.md` §5.

```sqf
player forceAddUniform "HCL_U_Reno1811_SAXKO"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Saxonia_Fuzileiro_Koenig";
player forceAddUniform "HCL_U_Reno1811_SAXCL"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Saxonia_Granadeiro_Gala";
player forceAddUniform "HCL_U_Reno1811_SAXJG"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Saxonia_Jaeger";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| S1 | Barretinas saxônicas | `HCL_H_Reno1811_Shako_Saxonia_Fuzileiro`, `_Fuzileiro_Koenig`, `_Granadeiro_Gala`, `_Ligeira`, `_Jaeger` | Encaixe; placa coroada com "FA" legível e inteira abaixo do cocar branco; cordões e borlas do lado direito |
| S2 | Casacas de linha | `HCL_U_Reno1811_SAXKO`, `_SAXNI`, `_SAXAN`, `_SAXLO`, `_SAXMA`, `_SAXRE`, `_SAXFA`, `_SAXCL` | Branco que não estoure com luz forte; cores distintivas |
| S3 | Ligeira e Jäger | `HCL_U_Reno1811_SAXLI`, `_SAXJG` | Verde com peças pretas, calça cinza |
| S4 | Nomes no Arsenal | todos | "Coat 1810 - Saxony, Line Infantry Regiment '...'" |

## 13. Confederação do Reno, lote 3 (Vestfália 1809), `hcl_reno.pbo` (2026-10-29, não testado no jogo)

Montagem: 126,5 MB, 12/12 modelos com esqueleto (casaca, 2 capacetes de lagarta, 5 barretinas saxônicas, 4 vestfalianas), `pbo_verify` com 104 referências, nenhuma faltando. O PBO foi empacotado em `release\_atualizacao\hcl_reno.pbo`, porque o da pasta Addons estava em uso (o jogo não estava aberto). Copie-o por cima de `release\@Historical_Clothing\Addons\hcl_reno.pbo` antes de testar. Relatório: `docs/reports/reno_1811.md` §6.

```sqf
player forceAddUniform "HCL_U_Reno1811_WESAC"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Vestfalia_Voltigeur_Gala";
player forceAddUniform "HCL_U_Reno1811_WES05"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Vestfalia_Granadeiro_Campanha";
player forceAddUniform "HCL_U_Reno1811_WESAE"; removeHeadgear player; player addHeadgear "HCL_H_Reno1811_Shako_Vestfalia_Fuzileiro";
```

| ID | Item | Classes | Observar |
|---|---|---|---|
| V1 | Barretinas vestfalianas | `HCL_H_Reno1811_Shako_Vestfalia_Fuzileiro`, `_Granadeiro_Campanha`, `_Granadeiro_Gala`, `_Voltigeur_Gala` | Placa em losango, divisas amarelas dos lados, cocar branco de centro azul |
| V2 | Casacas | `HCL_U_Reno1811_WESAC`, `_WESAE`, `_WES05`, `_WES07` | Azul-claro, azul-escuro, laranja, gola amarela |

## 14. Preto nas partes brancas: fundo das texturas preenchido (2026-10-29, não testado no jogo)

O usuário viu no jogo "um preto nas partes brancas". Causa provável: nas texturas de cor (`_co`) o espaço entre as peças do molde era preto puro (0,0,0), com só 2–4 px de margem. Os mipmaps menores, usados com a distância, misturam esse preto nas bordas, e no branco isso aparece como riscos e manchas pretas. As texturas não têm canal alfa (24 bits), então a causa não é transparência.

Correção: `source/scripts/preencher_fundo.py` preenche só os pixels de preto exato com a cor das peças vizinhas (push-pull), sem mudar nenhum pixel das peças. Foi aplicado às 157 texturas de cor de `hcl_suica`, `hcl_varsovia`, `hcl_italia` e `hcl_reno`; depois os PAA foram convertidos de novo (sem falhas) e os quatro PBOs remontados (nenhuma referência faltando). Deve rodar depois de cada bake ou pintura, antes da conversão para PAA. `hcl_fr`, `hcl_uk` e `hcl_pruss` têm o mesmo fundo preto e aguardam a decisão do usuário.

| ID | Observar |
|---|---|
| P1 | Casacas brancas (Saxônia, Vestfália, Itália, 13º de Varsóvia) e calças brancas: sem riscos nem manchas pretas nas costuras, de perto e de longe |
| P2 | Cordões e plumas brancos, cocares: sem contorno preto |
