# Relatório de Ambiente — Etapa 1

Projeto: `@Historical_Clothing` (addon de vestimentas históricas para ARMA 3)
Data da inspeção: 2026-10-09
Método: somente leitura. Nenhum arquivo do ARMA 3, do Arma 3 Tools ou da pasta de referência foi alterado, copiado ou movido.

Legenda: ✅ verificado · ⚠️ verificado com ressalva · ❌ ausente · ❔ não verificado

---

## 1. Pasta do projeto

| Item | Estado |
|---|---|
| `C:\Users\lucas\Documents\HistoricalClothing` | ✅ Existia e estava **vazia** antes desta etapa |
| Repositório git | ❌ Não é um repositório git |

---

## 2. ARMA 3

| Item | Valor verificado |
|---|---|
| Instalação | ✅ `C:\Program Files (x86)\Steam\steamapps\common\Arma 3` |
| Versão (`arma3_x64.exe`) | ✅ `2.22.0.154089` (Steam buildid `25623484`) |
| PBOs em `Addons\` | ✅ 196 |
| PBOs de personagens/uniformes | ✅ `characters_f.pbo`, `characters_f_beta.pbo`, `characters_f_bootcamp.pbo`, `characters_f_decade.pbo`, `characters_f_epa.pbo`, `characters_f_epb.pbo`, `characters_f_epc.pbo`, `characters_f_gamma.pbo` |
| DLCs/CDLCs presentes (pastas) | ✅ `Argo, AoW, Contact, CSLA, Curator, Enoch, Expansion, GM, Heli, Jets, Kart, Mark, Orange, SPE, Tacops, Tank, vn` |
| Perfil do jogador | ✅ `C:\Users\lucas\OneDrive\Documentos\Arma 3\usuario.Arma3Profile` |
| Mods instalados (`!Workshop`, `@*`) | Nenhum na pasta do jogo |
| Logs `.rpt` | ❌ `%LOCALAPPDATA%\Arma 3` não existe. Nenhum log encontrado |

> O conteúdo interno dos PBOs (classes de uniforme, `hiddenSelections`, caminhos `.paa`) **ainda não foi inspecionado**. Isso fica para a Etapa 3. Nenhuma classe de jogo é citada neste relatório.

---

## 3. Arma 3 Tools

Instalação: ✅ `C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools` (Steam buildid `24661848`)

| Ferramenta | Executável verificado | Uso no projeto |
|---|---|---|
| TexView 2 | ✅ `TexView2\TexView.exe` (o arquivo **não** se chama `TexView2.exe`) | Visualizar/converter `.paa` ↔ `.tga`/`.png` |
| ImageToPAA | ✅ `ImageToPAA\ImageToPAA.exe`, `imageToPaaGUI.exe` | Conversão em lote para `.paa` |
| Addon Builder | ✅ `AddonBuilder\AddonBuilder.exe` | Empacotar o PBO |
| CfgConvert | ✅ `CfgConvert\CfgConvert.exe` (+ `BINToCPP.bat`, `CPPToBIN.bat`) | Ler `config.bin` de PBOs oficiais e validar `config.cpp` |
| BankRev | ✅ `BankRev\BankRev.exe`, `BankRevGUI.exe` | Desempacotar PBOs oficiais para **cópia de trabalho** (fora da instalação) |
| Object Builder | ✅ `ObjectBuilder\ObjectBuilder.exe` | Inspecionar modelos `.p3d` (se necessário) |
| DSSignFile / DSCreateKey | ✅ `DSSignFile\DSSignFile.exe`, `DSCreateKey.exe` | Assinatura do PBO (opcional, servidores) |
| WorkDrive (unidade P:) | ⚠️ `WorkDrive\WorkDrive.exe` existe, mas **P: não está montada** | Ambiente de trabalho padrão da BI |
| `settings.ini` | ⚠️ Caminhos ainda são placeholders (`A3_Path="/full/path/to/Arma3"`, `P_DrivePath="/full/path/to/ArmaWork"`) | Configurar só se a unidade P: for usada |

> Verifiquei apenas que os arquivos existem. **Nenhuma ferramenta foi executada.**

---

## 4. Ferramentas auxiliares

| Ferramenta | Estado |
|---|---|
| Blender | ✅ 5.2.2 em `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (fora do PATH) |
| Python | ❌ Só o atalho da Microsoft Store (`python` retorna código 9009). Não é necessário por enquanto |
| Editor de imagem 2D com camadas (GIMP, Krita, Paint.NET, Photoshop, Affinity) | ❌ **Nenhum encontrado** (Program Files, AppData\Programs e registro de desinstalação) |
| Mikero Tools (DePbo, pboProject…) | ❌ Não encontrado. Não é obrigatório: BankRev e Addon Builder cobrem o fluxo básico |
| Arma 3 Samples (Steam → Ferramentas) | ❌ Não instalado |

---

## 5. Pasta de referência fornecida

Caminho: `C:\Users\lucas\OneDrive\Área de Trabalho\roupas e texturas para mod da era napoleonica no arma 3`

- 2.204 arquivos, 11.521,7 MB.
- Só há dois tipos de arquivo: `.dds` (1.182 arquivos, 11.268,4 MB) e `.tga` (1.022 arquivos, 253,3 MB).
- Atributo OneDrive `0x420` (Archive + ReparsePoint, sem "Offline"): os arquivos estão **no disco local**.
- **Não há** modelos 3D, configs, readme, licença ou créditos.
- **Nenhum** nome de arquivo ou pasta contém "Eras".

### 5.1 Subpastas

| Subpasta | Arquivos | MB | Conteúdo |
|---|---:|---:|---|
| `(N)_LME4_Camp1815_Chapter_XIV` | 192 | 142,3 | Bandeiras de UI (`ui\flags\<nação>\*.tga`) e 2 texturas de bandeira 3D |
| `(N)_LME4_graphics` | 454 | 1.052,1 | Bandeiras de UI, atlas de bandeiras e **72 atlas de unidades** (`variantmodels\units\atlas`) |
| `(N)_Reto_BattleMOV11-15` | 242 | 4.498,8 | **242 atlas de unidades** (`variantmodels\units\atlas`) |
| `(N)_Reto_BattleMOv2` | 90 | 22,3 | Peças de uniforme britânico (`variantmodels\unitparts\britain\{hats,legs,shoulders,torsos}`) |
| `(N)_Reto_rigidmodels` | 32 | 22,2 | Bandeiras, peças de campanha, naval, marcadores |
| `(N)_Reto_texture9` | 2 | 0,8 | `carriage_1_textureflag_diffuse.dds`, `flag_15thalabama_diffuse.dds` (bandeira da Guerra Civil Americana, não napoleônica) |
| `(N)_Reto-BattleMOVearly` | 1.192 | 5.783,1 | ⚠️ **Duplicata completa** (ver 5.2) |

### 5.2 Duplicação

`(N)_Reto-BattleMOVearly` contém cópias das 6 pastas acima e mais duas cópias de `(N)_Reto_BattleMOv2\variantmodels`. A comparação por caminho relativo e tamanho deu **0 diferenças** em todos os conjuntos, e o SHA-256 de uma amostra (`texture_diffuse.dds`) é igual nas três cópias.

**Conteúdo único real: 1.012 arquivos, cerca de 5.738 MB.** Os outros 5,7 GB são redundantes. Nada foi apagado.

### 5.3 Formato das texturas (cabeçalhos lidos)

| Tipo | Arquivos por conjunto | Resolução | Compressão |
|---|---|---|---|
| Peças `unitparts\britain\*` | `texture_diffuse.dds`, `texture_normal.dds`, `texture_gloss_map.dds` | 512×512 (chapéus: 384×384) | DXT5, sem mipmaps |
| Atlas de unidade `*_diffuse/_normal/_gloss/_colour_mask.dds` | 4 mapas por atlas | 4096×4096 ou 4096×2048 | DXT1/DXT3/DXT5 ou RGB 16bpp, com ou sem mipmaps |
| Bandeiras UI | `.tga` RLE (tipo 10) | 19×24 a 512×256 | 24/32 bpp |

Atlas encontrados:
- **BattleMOV11-15:** austriaCAV, austriaCAV_2, austriaINF, austriaINF_2, BavariaCAV, BavariaGEN, BavariaINF, britainCAVb, britainCAVc, britainINF, britainINFb, britainINFc, denmarkINF, FranceART, FranceART2, FranceCAV, FranceGeneral18051815, FranceINF, FranceINF_2, FranceINF_3, FranceLighCAV, FranceLighCAV_2, ItalyCAV, ItalyINF, NaplesCAV, NaplesGEN, NaplesINF, NederlandCAV18061811 (a/b/c), NederlandINF18061811 (a/b), oldenburgCAV1812, oldenburgINF1812, PolandART, polandCAV, polandINF, prussia1813_01…05, rus1812CAV (1–3), rus1812GEN, rus1812INF (1–2), saxonCAV1812, saxonINF1812 (a/b), Spanish2INF, SpanishART_CAV, spanishCAV, SpanishINF, WestphaliaCAV, WestphaliaINF, WestphaliaLighCAV, WurtembergCAV_2, WurtembergINF_2, WurtembergLighCAV
- **LME4_graphics:** austrialme, bavaria, britain1, britain2, britainr, france_roy, franceb, francec, franced, francee, francee2, francee98, francef, franceg, francerc, imperial_guardsb, prussiabz, prussiar

---

## 6. Avaliação: dá para "extrair roupas e texturas" desta pasta para o ARMA 3?

### 6.1 Roupas (modelos 3D): não

A pasta contém **apenas texturas**. Não há nenhum modelo de roupa para extrair.

### 6.2 Texturas: tecnicamente incompatíveis para uso direto

1. **UV diferente.** As texturas foram pintadas para o layout UV dos modelos do Napoleon: Total War. Os atlas 4096² agrupam várias peças de unidade numa só folha. Um uniforme do ARMA 3 usa outro layout. Aplicar essas imagens num modelo do ARMA 3 produziria uma textura embaralhada. **Não há conversão automática possível.** Seria preciso repintar no layout UV do modelo-base do ARMA 3.
2. **Conjunto de mapas diferente.** O NTW usa `diffuse / normal / gloss / colour_mask`. O ARMA 3 usa `.paa` com convenções próprias (por exemplo `_co` para cor) e materiais `.rvmat`. Para um retexto simples basta substituir a textura de cor e manter o material do modelo-base. Isso será confirmado na Etapa 3.

### 6.3 Permissões: bloqueado

- Não há licença, readme nem créditos em nenhuma das 2.204 entradas.
- Os nomes das pastas indicam pacotes de **mods de terceiros** para Napoleon: Total War (`Reto`, `LME4`). A autoria e as permissões **não foram verificadas**. Mods de NTW também podem conter material derivado do jogo original da Creative Assembly.
- O enunciado do projeto proíbe presumir permissão de redistribuição.

**Decisão inicial (substituída):** só referência visual; nenhum arquivo copiado para o addon.

**Decisão atual (2026-10-09):** o usuário informou que o addon é **de uso pessoal e não será publicado**.
- Os arquivos desta pasta **podem ser usados como material de recorte** nas texturas do addon (galões, botões, tecido, placas), sempre remontados no UV do modelo-base do ARMA 3, como descrito em 6.2.
- O PBO resultante conterá material de terceiros e **não deve ser compartilhado** (Workshop, Discord, servidores, arquivos enviados a outras pessoas).
- Os termos de uso do NTW e dos mods de origem não foram verificados. A decisão de uso pessoal é do usuário.
- Cada arquivo de terceiros usado no addon deve constar em `docs/source_inventory.md`.

---

## 7. Componentes ausentes ou pendentes

| # | Componente | Necessidade | Ação sugerida |
|---|---|---|---|
| 1 | Editor de imagem 2D com camadas | **Obrigatório** para pintar a textura | Instalar GIMP, Krita ou Paint.NET (gratuitos) |
| 2 | Textura-base e `hiddenSelections` do uniforme escolhido | **Obrigatório** (Etapa 3) | Extrair com BankRev para uma cópia de trabalho **fora** da instalação do jogo e ler o `config.bin` com CfgConvert |
| 3 | Unidade P: | Recomendado. A necessidade real será definida na Etapa 5 | Montar com `WorkDrive.exe` / `mapdisk.bat` ou configurar o Addon Builder sem P: |
| 4 | Arma 3 Samples | Opcional. Material oficial de exemplo da BI; o conteúdo exato será confirmado após instalação | Steam → Biblioteca → Ferramentas → "Arma 3 Samples" |
| 5 | Autorização dos autores da pasta de referência | Só se quiser usar esses arquivos além de referência visual | Contatar os autores |
| 6 | Confirmação da origem "Eras Mod" | A pasta não menciona "Eras" | Informar de onde vieram esses arquivos |
| 7 | Logs `.rpt` | Necessário para a Etapa 6 | Rodar o jogo uma vez sem `-noLogs` e confirmar onde o `.rpt` é gravado |

---

## 8. Como verificar este relatório

1. Abra `C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\TexView2\` e confirme que o executável é `TexView.exe`.
2. No Explorador, abra a pasta de referência, clique com o botão direito em `(N)_Reto-BattleMOVearly` → Propriedades: devem aparecer cerca de 1.192 arquivos e 5,6 GiB.
3. Compare `(N)_Reto-BattleMOVearly\(N)_Reto_BattleMOv2` com `(N)_Reto_BattleMOv2`: a estrutura é a mesma.
4. No PowerShell, confirme que a unidade P: não existe:
   ```
   Test-Path P:\
   ```

---

## 9. Verificação complementar: Blender e modelos 3D (2026-10-09)

Motivo: o usuário pediu para usar o Blender para "transferir os modelos das roupas".

### 9.1 Modelos oficiais do ARMA 3 não abrem no Blender

Li o cabeçalho de `Addons\characters_f.pbo` sem extrair nada:

| Item | Valor |
|---|---|
| Prefixo | `a3\characters_f` |
| Entradas | 1.179 (713 `.paa`, 176 `.rvmat`, 153 `.p3d`, 120 `.rtm`, 8 `.bin`, 5 `.fsm`, 4 `.sqf`) |
| Assinatura dos 153 `.p3d` | **`ODOL` em todos** (binarizados) |

`ODOL` é o formato binarizado de jogo. Object Builder e Blender editam `MLOD`. Portanto, **não é possível abrir nem modificar os uniformes oficiais no Blender**. Para alterar a geometria seria preciso partir de um modelo editável próprio ou de um modelo de exemplo distribuído oficialmente para edição (ver 9.3).

### 9.2 Pasta `Napoleon Total War` em D:

| Item | Valor |
|---|---|
| Caminho | `D:\SteamLibrary\steamapps\common\Napoleon Total War` |
| Conteúdo | Só `data\` + `installscript.vdf`. Sem executável e sem `appmanifest_34030.acf`: é uma **cópia parcial**, não uma instalação Steam ativa |
| Arquivos | 63 (34 `.pack`, 14 `.lua`, 14 `.esf`), 6.712,2 MB |
| Pacotes relevantes | `(N)_ERA_Logo_UI.pack` (possível ligação com o "Eras"), `(N)_LME4*.pack`, `(N)_Reto*.pack` (origem das texturas da pasta de referência) |

O conteúdo interno dos `.pack` **não foi inspecionado**. Os pacotes podem conter modelos 3D do NTW. Para uso pessoal (6.3), o bloqueio de permissão deixa de valer, mas restam obstáculos técnicos ainda não verificados:
- uma ferramenta para extrair `.pack` do Napoleon e converter os modelos para um formato que o Blender importe;
- o refazimento do rig para o esqueleto do ARMA 3;
- a densidade de polígonos de modelos feitos para RTS.

Isso fica para avaliar na Fase 2 (Blender).

### 9.3 Blender

| Item | Estado |
|---|---|
| Blender 5.2.2 | ✅ Instalado |
| Perfil `%APPDATA%\Blender Foundation\Blender\5.2` | ✅ Existe. Sem `scripts\addons` e sem `extensions` |
| Complemento para importar/exportar `.p3d` | ❌ **Nenhum instalado**. A escolha e a compatibilidade com o Blender 5.2 ainda precisam ser verificadas |
| Modelo-base editável (MLOD) para personagem | ❌ Nenhum disponível. O Arma 3 Samples não está instalado; o conteúdo e a licença serão confirmados após a instalação |
| Leitura de `.dds` pelo Blender em modo headless | ✅ Testado: o script `dds_preview.py` (pasta temporária da sessão) converteu 8 texturas de referência em PNG |

### 9.4 PBOs de personagem por DLC (verificados por nome de arquivo)

| Pasta | PBOs | PBO de personagem |
|---|---:|---|
| `Addons` (jogo base) | 196 | `characters_f*.pbo` (8, ver seção 2) |
| `Expansion` (Apex) | 62 | `characters_f_exp.pbo`, `characters_f_oldman.pbo` |
| `Enoch` (Contact) | 37 | `characters_f_enoch.pbo` |
| `Orange` (Laws of War) | 19 | `characters_f_orange.pbo` |
| `Tacops` | 11 | `characters_f_tacops.pbo` |
| `Tank` | 18 | `characters_f_tank.pbo` |
| `Jets` | 32 | `characters_f_jets.pbo` |
| `Argo` | 23 | `characters_f_patrol.pbo` |
| `AoW` (Art of War) | 16 | `characters_f_aow.pbo` |
| `Mark` (Marksmen) | 27 | `characters_f_mark.pbo` |
| `Kart` | 14 | `characters_f_kart.pbo` |
| `GM`, `SPE`, `vn`, `CSLA` (CDLCs) | **0** | Pastas existem, mas **sem PBOs**: não instaladas |

### 9.5 Object Builder: importação de FBX (verificada nos arquivos, não executada)

| Item | Evidência |
|---|---|
| `ObjectBuilder\FBX.dll` | Arquivo presente (10.975.744 bytes) |
| Funções no `ObjectBuilder.exe` e no `O2Script.exe` | Textos encontrados nos executáveis: `importFBX`, `exportFBX`, `importFBXtoLODobject`, `exportLODobjectToFBX`, "Requires FBX.dll". `ObjectBuilder.exe` também cita `*.3ds` |
| Modelos-base de personagem editáveis | `ObjectBuilder\O2Scripts\CharacterGeo\NewGeometryTemplate.p3d`, `O2Scripts\CharacterFG\NewFireGeometryTemplate.p3d` (LODs de geometria e fire geometry, não o modelo visual) |

Conclusão: o caminho Blender → FBX → Object Builder é suportado pelas ferramentas instaladas. **A importação ainda não foi testada.**
