# Pipeline de Exportação para o ARMA 3

Fase 1. Atualizado em 2026-10-09.

> **O Blender não gera um `.p3d` nativo.** A conversão passa por ferramentas compatíveis (Object Builder) e cada etapa tem uma validação. Nada abaixo foi executado de ponta a ponta ainda.

Legenda: ✅ verificado · 🔶 indício verificado, uso não testado · ❔ a verificar

---

## Visão geral

```
[Blender .blend] ──(A)──► [FBX] ──(B)──► [Object Builder: .p3d MLOD com LODs, seleções, propriedades]
       │                                              │
       └──(C) texturas-fonte .png ──► ImageToPAA ──► .paa       (D) .rvmat (texto)
                                                      │
                     (E) config.cpp ──► (F) Addon Builder ──► hcl_*.pbo ──► release/@Historical_Clothing/Addons/
                                                                                   │
                                                                              (G) testes no jogo
```

---

## (A) Blender → FBX

| Item | Estado |
|---|---|
| Blender 5.2.2 instalado | ✅ |
| Exportação FBX em modo headless (`bpy.ops.export_scene.fbx`) | ✅ Funcionou nos protótipos exploratórios |
| Configuração de eixos e escala que o Object Builder espera | ❔ Definida no teste B1 |
| Antes de exportar | Transformações aplicadas, checklist da Fase 5 aprovado, um objeto por LOD (ou nomes que identifiquem o LOD) |

Quem executa: Claude (script) ou o usuário (menu File → Export → FBX).

## (B) FBX → Object Builder → `.p3d`

| Item | Estado |
|---|---|
| `ObjectBuilder\FBX.dll` presente | ✅ |
| Funções `importFBX` / `importFBXtoLODobject` / `exportFBX` no `ObjectBuilder.exe` e no `O2Script.exe` | 🔶 Encontradas nos executáveis; **não testadas** |
| Montar os LODs: resolução (0..n), sombra, Geometry (`autocenter = 0`), ViewPilot vazio | 🔶 Requisitos em `modeling_standards.md` §6 |
| Seleção `camo`; pesos no osso `head` (`OFP2_ManSkeleton`) | ✅ Requisito observado nos modelos oficiais; procedimento no Object Builder ❔ |
| Caminhos de textura e `.rvmat` nas faces | ❔ Definidos com o prefixo do PBO (etapa F) |
| Saída | `.p3d` MLOD em `addons/hcl_<pbo>/...` (os fontes continuam em `source/models/`) |

Quem executa: **o usuário**, no Object Builder (interface gráfica), com um passo a passo que o Claude escreve depois do teste B1. Depois de validado, a automação com `O2Script.exe` pode ser avaliada.

Validação: reabrir o `.p3d` sem erros; Buldozer mostra todos os LODs; o limite de polígonos não é ultrapassado.

### (B') Rota usada no addon de teste de 2026-10-10 (sem Object Builder e sem drive P:)

1. **Gravação do MLOD:** `source/scripts/p3d_mlod_io.py` grava o MLOD. A gravação foi validada: os 34 MLOD dos Arma 3 Samples saem idênticos byte a byte.
2. **Montagem:** `build_p3d_pruss.py` monta os modelos sobre os templates oficiais. As convenções de ordem das faces, UV, normais e pesos foram conferidas nas mãos do template.
3. **Binarização:** `binarize_x64.exe` oficial, rodando a partir de `source/addon`, com pastas espelhando o prefixo. Assim os materiais do próprio addon são encontrados.
4. **Config e materiais:** `CfgConvert` gera o `config.bin` e os `.rvmat` binários.
5. **Empacotamento:** `FileBank -property prefix=hcl\hcl_pruss`.
6. **Automação e verificação:** `build_mod_pruss.ps1` roda tudo; `pbo_verify.py` verifica o PBO.

**Limite:** materiais do jogo citados pelos templates (pele das mãos, penetração) não são lidos, porque não há dados do jogo extraídos.

A rota com Object Builder (abaixo) continua válida para editar os modelos à mão.

## (C) Texturas → `.paa`

| Item | Estado |
|---|---|
| `ImageToPAA.exe` e `TexView2\TexView.exe` presentes | ✅ |
| Regras de sufixo e compressão (`_co` DXT1, `_ca` DXT5, `_nohq` DXT5, `_smdi` DXT1, `_as` DXT1) | ✅ `TexConvert.cfg` |
| Fonte | `.png` em `source/textures/<item>/`, dimensões em potência de 2 |
| Conversão | ✅ `ImageToPAA.exe <entrada.png> <saida.paa>` (verificado em 2026-10-10; também converte `.paa` → `.png`) |
| Troca de canais do `_nohq` | ✅ Feita pelo próprio ImageToPAA (`TexConvert.cfg`, classe `normalmap_hq`): entregar um mapa normal RGB comum |
| Validação | ✅ Cabeçalho do `.paa` (DXT1 `0xFF01`, DXT5 `0xFF05`) + conversão de volta; TexView 2 pelo usuário |

✅ **Convenção do mapa normal: OpenGL (+Y para cima)**, medida no template oficial `Arma 3 Samples\Art\TemplateNormalMap\displaceTest_middle_nopx.tga` (correlação verde × inclinação da altura = +0,785).

## (D) Materiais `.rvmat`

| Item | Estado |
|---|---|
| Os modelos oficiais usam `.rvmat` (ex.: `a3\characters_f\common\data\cappatrol.rvmat`) | ✅ (referência dentro do `.p3d`) |
| Modelo de partida | Extrair um `.rvmat` oficial para `work/a3/` e convertê-lo para texto, se estiver binarizado, só para consulta ❔ |
| Um `.rvmat` por material: feltro, tecido, couro envernizado, metal | Proposta |

## (E) `config.cpp`

Estrutura baseada **só** em classes verificadas (`references.md` §2):

| Peça | Base verificada |
|---|---|
| `CfgPatches` | `requiredAddons[]` com `A3_Characters_F` (patch verificado) |
| Item de cabeça | `HCL_H_...: HelmetBase` ou `H_HelmetB`, com `ItemInfo: HeadgearItem` (`uniformModel`, `modelSides`, `hiddenSelections`, `mass`). A escolha entre as duas bases será justificada na Fase 8 |
| Uniforme | `HCL_U_...: Uniform_Base` com `ItemInfo: UniformItem` (`uniformClass`, `containerClass`, `mass`) + classe em `CfgVehicles` herdada de um soldado verificado, `scope = 1` (sem facção nova) |

Validação: `CfgConvert.exe -bin -dst <tmp>.bin config.cpp` (sintaxe confirmada no `CPPToBIN.bat` oficial) com código de saída 0.

## (F) Empacotamento

| Item | Estado |
|---|---|
| `AddonBuilder.exe` presente | ✅ |
| Prefixo do PBO e caminhos internos | ❔ Decisão P3 (com ou sem unidade P:) |
| Binarização dos `.p3d` pelo Addon Builder | ❔ |
| Saída | `release/@Historical_Clothing/Addons/hcl_*.pbo` |
| Validação | Ler o cabeçalho do PBO gerado (prefixo e lista de arquivos); nada de `source/` ou `work/` dentro dele |

**Só se afirma "compilado" se o Addon Builder foi executado e o PBO existe.**

## (G) Testes no jogo

Ver `testing.md`. Executados pelo usuário; os resultados são registrados com evidência.

---

## Dependências desta cadeia

| # | Dependência | Situação |
|---|---|---|
| 1 | Arma 3 Samples (exemplo oficial de item de cabeça e corpo de referência) | ❌ Não instalado; precisa de autorização |
| 2 | Leitura direta da wiki da Bohemia (requisitos de LOD) | ❌ Bloqueada pela verificação do site |
| 3 | Teste B1 (importação FBX no Object Builder) | ⏳ Depende do usuário |
| 4 | Decisão sobre a unidade P: e o prefixo do PBO | ⏳ |
