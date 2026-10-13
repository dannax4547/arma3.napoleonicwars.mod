# Relatório: UV e Texturas da Barretina (Fase 6)

Data: 2026-10-10 · **Estado: aguarda aprovação do usuário** · Fase 4 aprovada em 2026-10-09.

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/shako_uv_layout.py` | Disposição das ilhas na textura 2048² (fonte única) |
| `source/scripts/build_shako_production.py` | Agora também atribui os UVs (geometria **idêntica** à aprovada: 2.605 vértices, 3.004 faces, 5.194 triângulos) |
| `source/scripts/uv_review.py` | Verificação de UV + imagem do mapa (`docs/reports/img/uv/shako_uv_layout.png`) |
| `source/scripts/generate_shako_textures_prod.py` | Gera as texturas a partir da própria malha |
| `source/scripts/render_shako_textured.py` | Pré-visualização texturizada no Blender |
| `source/scripts/check_normal_convention.py` | Mede a convenção do mapa normal num arquivo oficial |
| `source/textures/hcl_shako_pruss/hcl_shako_pruss_{co,nohq,smdi}.png` | **Fontes editáveis** (2048²) |
| `source/textures/hcl_shako_pruss/paa/hcl_shako_pruss_{co,nohq,smdi}.paa` | Texturas convertidas para o ARMA 3 |
| `docs/reports/img/texturas/*.png` | Renders texturizados |
| `docs/reports/shako_pruss_uv_review_output.txt` | Saída da verificação de UV |

## 2. UV

| Ilha | Projeção | Densidade |
|---|---|---|
| Feltro, faixa envernizada, debrum | Cada anel desenrolado pelo **perímetro real**, sem esticar no alargamento; costura de UV **nas costas**, onde a barretina real tem a costura | 1.800 px/m |
| Copa | Plana | 1.800 px/m |
| Pala (frente, verso, borda, raiz) | Fileiras desenroladas pelo comprimento real | ~2.000 px/m |
| Cocar (frente / lateral / trás) | Plana / tira / plana | ~4.000 px/m (detalhe do plissado) |
| Presilha | Plana + tiras laterais | ~4.000 px/m |
| Monograma | Plana frontal | ~2.100 px/m |
| Botões | Plana; **os dois compartilham a mesma ilha** (peças idênticas) | ~3.700 px/m |
| Jugular | 4 tiras ao longo do comprimento | ~1.800 px/m |
| Forro e teto interno | Desenrolado / plana | 700 px/m (raramente visível) |

Ocupação: 24,4% da textura. **A metade inferior está reservada** para os distintivos das variantes (águia, estrela da Guarda); ver `docs/specs/shako_variantes_plano.md`.

### Verificação (execução final)

| Critério | Resultado |
|---|---|
| Cantos de UV fora do quadro 0–1 | ✅ 0 |
| Sobreposição entre peças | ✅ 0 (a ilha compartilhada dos botões é intencional) |
| Sobreposição dentro das peças | ✅ 0 |
| Faces visíveis espelhadas | ✅ 0 no corpo, pala, cocar, presilha e jugular |
| Espelhamento restante | Só em faces **escondidas** (traseira dos botões, encostada na faixa) e nas costas/laterais do monograma, que usa relevo plano |
| Geometria inalterada pela UV | ✅ Revisão M1–M7 repetida: tudo continua passando |

### Defeitos encontrados e corrigidos

| Defeito | Correção |
|---|---|
| 7 cantos de UV fora do quadro (fileiras externas da pala com ~0,30 m) | Ilhas da pala movidas para uma área maior |
| Ilhas espelhadas (feltro desenrolado no sentido oposto à superfície, verso da pala, etc.) | Detecção automática de ilhas com orientação invertida e espelhamento dentro da própria caixa |
| Botão visível espelhado (área projetada igual à da traseira) | Sentido do U invertido no código dos botões |

## 3. Texturas

**Método:** o gerador rasteriza os UVs da malha. Assim cada pixel sabe seu material e sua posição na barretina, e os detalhes são postos por posição real:
- costura vertical nas costas;
- pesponto do debrum a 7,8 mm do topo;
- anel costurado na copa;
- pesponto da pala a 4,5 mm da borda;
- plissado do cocar;
- trama em espinha de peixe da presilha;
- pespontos da jugular.

As bordas das ilhas são estendidas em 12 px para os mipmaps não puxarem pixels vazios.

| Mapa | Conteúdo | Formato `.paa` verificado |
|---|---|---|
| `_co` | Cor: feltro preto, couro envernizado, couro, tecido branco e preto, lã amarela, latão, forro | DXT1 (cabeçalho `0xFF01`), 276.672 bytes |
| `_nohq` | Relevo, **convenção OpenGL (+Y para cima)** | DXT5 (`0xFF05`), 1.206.147 bytes |
| `_smdi` | R = 1, **G = intensidade do brilho**, **B = nitidez do brilho**, por material | DXT1 (`0xFF01`), 70.707 bytes |

**Convenção do mapa normal, medida:** no `displaceTest_middle_nopx.tga` oficial (Arma 3 Samples), a correlação entre o canal verde e a inclinação da altura dá **+0,785**, e o vermelho dá −0,785 (controle). Isso confirma OpenGL/+Y.

**Conversão:** `ImageToPAA.exe <entrada.png> <saída.paa>` funciona nos dois sentidos (código de saída 0). A volta `.paa` → `.png` devolveu 2048 × 2048 com o conteúdo preservado.

**Origem dos pixels:** a textura base é **100% própria (procedural)**. O material do Eras Mod (autorizado, ver `references.md` §3.2) entra nas **variantes de regimento**.

**Parâmetros para variantes**, já no gerador: presilha `amarela`/`branca` e metal `latao`/`estanho`.

## 4. Pendências

| Item | Fase |
|---|---|
| Abrir os `.paa` no TexView 2 (teste T3, manual) | Usuário |
| `.rvmat` por material (feltro, couro envernizado, couro, tecido, lã, latão), usando os `_nohq` e `_smdi` | 7 |
| Mapa `_as` (sombra ambiente): opcional; os modelos oficiais de cabeça variam (o capacete usa, o boné não) | 7 (decidir) |
| Aparência no jogo sob iluminações diferentes (G8/G9) | 9 |
