# Variantes Regimentais Prussianas de 1813: barretina e uniforme

Versão 1.1, 2026-10-11. **Estado: aguarda aprovação.**

**Novidades da 1.1** (pedido do usuário: "finalizar todos os regimentos possíveis da Prússia"):
- **lote 2:** 9 casacas **verdes** (V09–V17);
- **V03 corrigida:** o bloco de origem tem punhos **pretos debruados de vermelho**;
- **barretinas:** 8 novas, com presilha preta e linhas da faixa (V-C e V-D feitos);
- **correame e mochila** em **couro preto**;
- **limite do possível:** §9.

O pedido do usuário foi: *"este modelo serve como uma versão para todos os outros regimentos da Prússia; aplica mais padrões e visuais únicos de barretinas de acordo com aquela época, para criar mais roupas de vários outros regimentos"*.

A base são os protótipos já feitos:
- a barretina (`HCL_Shako_Pruss_LOD0`, Fase 6);
- o uniforme (`HCL_U_Pruss1813_01_LOD0`, Fases 4–5). Ele recebeu agora a UV e as texturas da Fase 6.

Legenda:
- ✅ confirmado;
- 🔶 provável, ou estendido por analogia;
- ❓ incerto;
- 🎮 visto nas texturas do Eras Mod (autorização declarada pelo usuário em 2026-10-09; os detalhes estão pendentes em U7).

---

## 1. Regras aplicadas

| Regra | Como foi aplicada |
|---|---|
| Uma base para todos os regimentos | O **uniforme** usa a mesma malha em todas as variantes; muda só a textura de cor `_co`. O relevo (`_nohq`) e o brilho (`_smdi`) são comuns a todas. A **barretina** muda de cor só por textura; águia e estrela têm formas diferentes do monograma, por isso cada uma tem malha própria |
| Mecanismo do ARMA 3 para variantes de textura | ✅ Uma classe filha troca só `hiddenSelectionsTextures[]` (o `H_MilCap_mcamo` faz isso sobre o `H_MilCap_ocamo`, ver `shako_variantes_plano.md` §3). Isso será aplicado no config, na Fase 8 |
| "Não invente detalhes regimentais" | **Nenhuma variante leva nome de regimento.** Os nomes são técnicos e descrevem a aparência (V01–V08, `aguia_amarela`…) até o usuário informar o nome que o Eras Mod dá a cada unidade (§7, V-B) |
| Leitura "cor da província + cor da antiguidade" [S1] | 🔶 Só como pista (ficha do uniforme, §2). Não entra em nome de classe nem em texto do addon |
| Material do Eras Mod | Usado com a autorização declarada: as cores foram **amostradas** dos atlas e os contornos da águia e da estrela foram **traçados** da arte do mod. Se a autorização não cobrir distribuição (U7), esses contornos e cores precisam ser refeitos a partir de fonte própria ou de domínio público (pranchas de Knötel) **antes** de qualquer distribuição |

## 2. O que foi lido no mod

### 2.1 Casacas (atlas `prussia1813_01..03`)

Método: `source/scripts/catalog_mod_coats.ps1` lê cada bloco de 512 px nas mesmas posições:
- casaca;
- vira (viradas das abas);
- punho;
- platina;
- botão.

Saída: `work/ntw/prussia1813/catalogo_casacas.{png,csv}` (só consulta local).

Combinações de **casaca azul** encontradas (os blocos estão na forma `atlas cColuna rLinha`):

| Gola, punhos e viras | Platina | Botões | Blocos do mod | Variante |
|---|---|---|---|---|
| Vermelho | Branca | Latão | 01 c0r1, c1r1 · 02 c2r1, c5r3 | **V01** (protótipo) |
| Vermelho | Branca | Metal branco | 01 c2r2 · 02 c2r2, c3r2, c5r2, c2r3 | **V02** |
| Vermelho; **punhos pretos debruados de vermelho** (corrigido na 1.1) | Vermelha | Latão | 01 c3r2 | **V03** |
| Vermelho | Amarela | Metal branco | 03 c0r1, c0r2 | **V04** |
| Amarelo | Branca | Metal branco | 01 c2r1 | **V05** |
| Amarelo | Vermelha | Latão | 01 c0r3, c1r3 | **V06** |
| Branco | Vermelha | Latão | 01 c0r2, c1r2 | **V07** |
| Azul-claro | Azul-clara | Metal branco | 03 c1r3 | **V08** |

### 2.1b Lote 2: casacas verdes (versão 1.1)

Os 12 blocos foram lidos ampliados, com recortes em `work/ntw/prussia1813/casacas_verdes_512.png` e `verdes_detalhe.png`, e não só pela amostra automática do CSV. A amostra automática caía no debrum e lia vermelho onde o punho é preto (foi o erro da V03).

A cor da **gola** é lida pela linha do pescoço no topo do bloco. O **cinturão** pintado no bloco aparece branco ou preto.

| Gola | Punhos | Viras | Platina | Botões | Extra | Cinturão no bloco | Blocos | Variante |
|---|---|---|---|---|---|---|---|---|
| Vermelha | Vermelhos | Vermelhas | Vermelha | Latão | — | Preto (02) / branco (03) | 02 c0r1 · 03 c2r1 | **V09** |
| Vermelha | Vermelhos | Vermelhas | Branca, borda vermelha | Latão | — | Branco | 02 c1r1 · 03 c3r1 | **V10** |
| Vermelha | Vermelhos | Vermelhas | Branca | Latão | **Galões amarelos** nos botões das palas | Branco | 02 c3r1 | **V11** |
| Vermelha | Vermelhos | Vermelhas | Branca | **Metal branco** | Galões amarelos | Preto | 02 c3r3 | **V12** |
| **Branca** | Brancos | Brancas | **Azul** | Latão | — | Preto | 02 c0r2 | **V13** |
| Branca | Brancos | Brancas | Branca, borda azul | Latão | — | Branco | 02 c1r2 | **V14** |
| **Preta debruada de vermelho** 🔶 | **Pretos debruados de vermelho** | Pretas debruadas de vermelho | Vermelha | Latão | — | Preto | 02 c0r3 | **V15** |
| Preta debruada de vermelho 🔶 | Pretos debruados de vermelho | Pretas debruadas de vermelho | Branca, borda vermelha | Latão | — | Branco | 02 c1r3 | **V16** |
| Vermelha | **Brancos debruados de vermelho** | **Verdes debruadas de vermelho** | Branca, borda vermelha | Latão | — | Preto / branco | 03 c2r2, c3r2 | **V17** |

🔶 Nas V15 e V16, a linha do pescoço é vermelha. Lida como **debrum de uma gola preta**, igual aos punhos e às viras. Também pode ser uma gola vermelha; a decidir com uma referência.

Também vistos nos atlas, mas **não produzidos** (ver §9):

| O quê | Onde | Observação |
|---|---|---|
| Oficiais e generais | Atlas 04 | Outra peça (outro corte e bordados) |
| Hussardos | Atlas 05 | Outra peça |
| Casacas de **outro corte**: coluna c4 dos três atlas (azul ou verde, gola com outro arranjo, botões espaçados), `01 c2r3` (com boné redondo), `01 c3r1` (preta) | 01–03 | Outro molde de peça no mod (provavelmente Landwehr e unidades livres); não serve na malha do Kollet |
| Casacas **azul-claras** com vivos rosa ou vermelhos, **brancas** com vivos vermelhos ou amarelos, calças cinza com faixa | 03 c0r0–c3r0, c1r1, c1r2, c4r3, c5r3, c2r3, c3r3 | Cavalaria (dragões e couraceiros, pelas cores); outra peça |
| `prussiabz` | — | Peças cinza: a cor de cada unidade vem de uma máscara do jogo, e nenhum arquivo do mod diz qual cor cada unidade usa |
| `prussiar` | — | Casacas com lapelas e alamares (outro período e outro corte) |

### 2.2 Barretinas (faixa das barretinas dos atlas 01–03)

| Elemento | Variações vistas 🎮 | Produzido? |
|---|---|---|
| Presilha do cocar | Branca, latão (amarela), **preta** | Todas (preta na 1.1) |
| Distintivo frontal | Monograma FWR, **águia de latão**, **estrela prateada ou de latão** | Sim, todos |
| Linha no alto da faixa (entre o feltro e a faixa envernizada) 🔶 | Branca, latão, verde | Sim, na 1.1 (§4) |
| Pluma verde | Uma variante | **Não** (precisa de geometria) |
| Caveira | Uma variante | Fora do escopo (não é infantaria prussiana) |

## 3. Variantes do uniforme

Comum a todas:
- casaca azul-escura (sRGB 0,10 / 0,13 / 0,22);
- calças cinza;
- polainas pretas;
- sapatos de couro preto, sola de couro.

As cores por variante estão em `source/textures/hcl_uniforme_pruss/variantes_regimentos.json`.

| ID | Gola, punhos e viras | Debrum (frente e palas) | Platina (borda) | Botões | Textura de cor |
|---|---|---|---|---|---|
| V01 | Vermelho | Vermelho | Branca (vermelha) | Latão | `hcl_u_pruss1813_v01_co` |
| V02 | Vermelho | Vermelho | Branca (vermelha) | Metal branco | `…_v02_co` |
| V03 | Vermelho; **punhos pretos debruados de vermelho** (1.1) | Vermelho | Vermelha (azul da casaca) | Latão | `…_v03_co` |
| V04 | Vermelho | Vermelho | Amarela (vermelha) | Metal branco | `…_v04_co` |
| V05 | Amarelo | Amarelo | Branca (amarela) | Metal branco | `…_v05_co` |
| V06 | Amarelo | Amarelo | Vermelha (amarela) | Latão | `…_v06_co` |
| V07 | Branco | Branco | Vermelha (branca) | Latão | `…_v07_co` |
| V08 | Azul-claro | Azul-claro | Azul-clara (azul da casaca) | Metal branco | `…_v08_co` |

**Lote 2, casaca verde** (sRGB 0,10 / 0,15 / 0,10; mesmas calças, polainas e sapatos). Detalhe por variante no §2.1b. Texturas `…_v09_co` a `…_v17_co`.

Para isso, `generate_uniform_textures_v2.py` ganhou chaves opcionais por variante, só de cor:
- `punho`;
- `gola_debrum`, `punho_debrum` e `viras_debrum` (faixa de 2,5 mm nas bordas da peça);
- `pala`;
- `galoes` (uma barra tecida sob cada botão das palas, achada pelos botões perto da pala: 3 de cada lado).

Por serem só de cor, o relevo e o brilho continuam comuns às 17 variantes.

Confiança:
- 🎮 Gola, punhos, viras, platina e botões vêm do catálogo (§2.1).
- 🔶 O **debrum** e a **borda da platina** só foram vistos com clareza em V01 (bloco M1). Nas outras variantes foram estendidos por analogia: o debrum na cor da gola; a platina na cor da gola, ou sem borda visível quando a platina já é da cor da gola.

Mapas comuns: `hcl_u_pruss1813_nohq` (relevo) e `hcl_u_pruss1813_smdi` (brilho).

### 3.1 UV do uniforme (Fase 6)

| Item | Valor |
|---|---|
| Script | `source/scripts/uv_uniforme_pruss.py` (salva no próprio `LOD0.blend`; cópia de segurança no scratchpad da sessão) |
| Método | Projeção por ângulo (60°) só nas peças de roupa; empacotamento com margem de 0,004; área limitada a 0,94² |
| Botões | Os 44 botões compartilham um quadrado no canto (0,95–0,995), porque são peças idênticas |
| Mãos | Mantêm a UV oficial do template (usam a textura de pele da identidade) |
| Densidade | ≈ 765–810 px/m em 2048², igual entre as peças |
| Ocupação | 48,9% da textura; 0 cantos fora de [0, 1] |
| Layout | `docs/reports/img/uniforme/uv_uniforme_layout.png` |

### 3.2 Texturas do uniforme

Script: `source/scripts/generate_uniform_textures.py`.

- Cada texel recebe a peça, o material, a posição 3D e a normal da face.
- O ruído é **3D**, por isso não aparece costura entre as ilhas da UV.
- Detalhes por regra:
  - sarja fina;
  - debrum da frente e das palas;
  - borda da platina;
  - poeira subindo nas calças e nas polainas;
  - desgaste na barra das abas;
  - relevo dos botões.
- O mapa normal segue a convenção **OpenGL (+Y)**, a mesma medida no template oficial.

## 4. Variantes da barretina

| ID | Distintivo | Presilha do cocar | Metais (rosetas, guarnições) | Malha | Triângulos |
|---|---|---|---|---|---|
| `fwr_amarela` (protótipo) | Monograma FWR | Amarela | Latão | `hcl_shako_pruss_LOD0.blend` | 5.194 |
| `fwr_branca` | Monograma FWR | Branca | Metal branco | idem | 5.194 |
| `aguia_amarela` | Águia de latão (cor da arte do mod) | Amarela | Latão | `variantes/hcl_shako_pruss_aguia_LOD0.blend` | 5.262 |
| `aguia_branca` | Águia de latão | Branca | Metal branco | idem | 5.262 |
| `estrela_prata` | Estrela prateada | Branca | Metal branco | `variantes/hcl_shako_pruss_estrela_LOD0.blend` | 5.778 |
| `estrela_latao` | Estrela de latão | Amarela | Latão | idem | 5.778 |
| `estrela_prata_presilha_preta` (1.1) | Estrela prateada | **Preta** | Metal branco | estrela | 5.778 |
| `aguia_presilha_preta` (1.1) | Águia | **Preta** | Latão | águia | 5.262 |
| `estrela_latao_linha_verde` (1.1) | Estrela de latão | Amarela | Latão; **linha verde** na faixa | estrela | 5.778 |
| `aguia_amarela_linha_verde` (1.1) | Águia | Amarela | Latão; **linha verde** | águia | 5.262 |
| `estrela_latao_linha_latao` (1.1) | Estrela de latão | Amarela | Latão; **linha de latão** | estrela | 5.778 |
| `aguia_amarela_linha_latao` (1.1) | Águia | Amarela | Latão; **linha de latão** | águia | 5.262 |
| `estrela_prata_linha_branca` (1.1) | Estrela prateada | Branca | Metal branco; **linha branca** | estrela | 5.778 |
| `aguia_branca_linha_branca` (1.1) | Águia | Branca | Metal branco; **linha branca** | águia | 5.262 |

As combinações da 1.1 são as das faixas dos atlas:
- presilha preta com estrela prateada e com águia (atlas 02);
- linha verde e linha de latão com presilha de latão (atlas 02);
- linha branca com presilha branca (atlas 01–03).

`generate_shako_textures_prod.py` ganhou a presilha `preta` e a opção `linha=branca|verde|latao`, só de cor (relevo e brilho continuam comuns a cada malha).

**Regressão:** a `estrela_prata` refeita com o gerador modificado ficou **idêntica** à de 2026-10-10 (diferença máxima 0,0).

### 4.1 Como os distintivos foram feitos

1. **Recorte:** a região dos distintivos do atlas 01 (posição 480, 2690; 300 × 160 px) vira `work/ntw/prussia1813/distintivos_atlas01.png`.
2. **Traçado do contorno:** `source/scripts/trace_badge.py` traça o contorno pelo **canal alfa** da arte. Usa *marching squares* em 3× a resolução e simplificação de Douglas-Peucker.
   - Saídas: `source/models/shakos/hcl_shako_pruss/distintivos/aguia.json` e `estrela.json` (91 pontos; simplificação de 1 px).
3. **Malha:** `source/scripts/build_shako_production.py` com a opção `badge=<json>`:
   - preenche o contorno e dá espessura (águia 1,3 mm; estrela 1,5 mm);
   - subdivide até arestas de ≤ 12 mm, para acompanhar a curva da frente;
   - levanta cada vértice até a parede real por raio, com 0,4 mm de folga.
   - Não usa booleana, por isso a malha fica sem arestas não-manifold.
4. **Tamanho:** águia 0,065 × 0,079 m; estrela 0,080 × 0,079 m.
5. **Cor:** `source/scripts/generate_shako_textures_prod.py` amostra a cor da arte do mod pela posição 3D de cada texel, o que evita qualquer espelhamento da UV.
   - O relevo vem do contraste local.
   - Tons usados: `original`, `latao` (estrela de latão) e `prata` (a estrela do atlas é escura; foi polida).

### 4.2 Verificações

| Verificação | Resultado |
|---|---|
| Revisão de malha (não-manifold, faces degeneradas, normais, distintivo dentro da parede) | ✅ zero em águia e estrela |
| Revisão de UV (fora de [0, 1], sobreposições) | ✅ zero |
| Regressão do FWR (sem a opção `badge`) | ✅ Idêntico: 2.605 vértices / 3.004 faces / 5.194 triângulos |
| UV espelhada no distintivo (inverteria o relevo do `_nohq`) | ✅ 0 faces da frente espelhadas (águia 261, estrela 392). As espelhadas são o verso, encostado na parede, e parte das bordas de 1,3–1,5 mm; o FWR aprovado tem o mesmo padrão |
| Relevo e brilho | Dependem só da malha: um par `_nohq`/`_smdi` para a águia e outro para a estrela (as texturas de cor mudam por variante) |

## 5. Arquivos `.paa` (convertidos e verificados)

Script: `source/scripts/convert_variants_paa.ps1` (usa o `ImageToPAA.exe` do Arma 3 Tools e escreve só dentro do projeto).

| Grupo | Arquivos | Formato verificado no cabeçalho |
|---|---|---|
| Barretina, cor | `source/textures/hcl_shako_pruss/paa/variantes/hcl_shako_pruss_{fwr_branca,aguia_amarela,aguia_branca,estrela_prata,estrela_latao}_co.paa` | DXT1 (`0xFF01`), ≈ 278–282 KB cada |
| Barretina, relevo e brilho | `…/paa/variantes/hcl_shako_pruss_{aguia,estrela}_{nohq,smdi}.paa` | `_nohq` DXT5 (`0xFF05`); `_smdi` DXT1 |
| Barretina FWR amarela | `…/paa/hcl_shako_pruss_{co,nohq,smdi}.paa` (já existiam) | idem |
| Uniforme, cor | `source/textures/hcl_uniforme_pruss/paa/hcl_u_pruss1813_v01..v08_co.paa` | DXT1, ≈ 0,89–1,0 MB cada |
| Uniforme, relevo e brilho | `…/paa/hcl_u_pruss1813_{nohq,smdi}.paa` | DXT5 (4,2 MB) e DXT1 |

19 conversões, 0 falhas. Volta `.paa` → `.png` (amostras V05 e `estrela_prata`): 2048² preservado; diferença média de 0,61/255 e 0,20/255, que é a perda normal da compressão DXT.

**Ainda não feito:** abrir no TexView 2 (teste T3, manual).

## 6. Imagens

| Arquivo (`docs/reports/img/variantes/`) | Conteúdo |
|---|---|
| `desfile_frente.png`, `desfile_costas.png`, `desfile_tres_quartos.png` | As 8 variantes do uniforme lado a lado (V01 → V08, da esquerda para a direita na frente) |
| `desfile_detalhe.png` | V02 de perto |
| `<variante>_{frente_3-4,lado,costas_3-4,detalhe,topo_sem_cabeca}.png` | Cada variante da barretina |
| `uv_barretina_{aguia,estrela}.png` | UV das barretinas com distintivo |

No desfile, cada uniforme aparece com uma barretina **só para exibir as duas coisas juntas**. No jogo, uniforme e barretina são itens independentes, e o desfile **não** diz que aquela barretina pertence àquele regimento.

Cena: `desfile_variantes.blend`. Script: `source/scripts/render_lineup.py`.

## 7. Decisões pendentes (do usuário)

| ID | Pergunta | Recomendação |
|---|---|---|
| V-A | Aprovar as 8 variantes do uniforme e as 6 da barretina | — |
| V-B | Nome que o Eras Mod dá a cada combinação (amplia U1) | Até lá ficam os nomes técnicos (V01–V08, `aguia_amarela`…) |
| V-C | ~~Fazer as casacas verdes~~ | **Feito na 1.1** (V09–V17) |
| V-D | ~~Presilha preta e linhas da faixa~~ | **Feito na 1.1** (8 barretinas). A pluma verde continua pendente, porque precisa de geometria |
| V-F | Gola das V15/V16: preta debruada de vermelho (como feito) ou vermelha? | Confirmar com uma referência |
| V-G | Aprovar o correame e a mochila em **couro preto** (cinturão preto pintado em 6 dos 12 blocos verdes; correias pretas na mochila do mod) | — |
| V-E | Detalhes da autorização do Eras Mod (U7) | Necessários antes de qualquer distribuição, porque águia, estrela e cores derivam do mod |

## 8. Limites conhecidos

- **R1** (relatório de revisão do uniforme): a linha entre o assento e as pernas da calça fica **mais visível com a textura** (close na virilha). A correção já está prevista para a Fase 7: unir as duas peças numa malha só.
- Nos renders, a pele e a cabeça são aproximações de exibição; no jogo elas vêm da identidade do personagem.

## 9. O que é possível com esta base (versão 1.1)

**Feito: tudo o que os atlas de infantaria do mod mostram no corte do Kollet de 1813**:

| Item | Quantidade |
|---|---|
| Uniformes | 17 (8 azuis + 9 verdes) |
| Barretinas | 14 (FWR 2, águia 6, estrela 6) |
| Correame e mochila | 2 conjuntos (couro branqueado e couro preto) |

Classes no addon de teste: 33 itens, 17 soldados e 2 mochilas.

**Não é possível sem peças novas** (cada uma é um protótipo próprio, passando pelas 9 fases):

| Grupo | Por quê |
|---|---|
| Landwehr e unidades com casaca de outro corte (coluna c4, 01 c2r3, 01 c3r1) | Outro molde de casaca; barretina diferente (boné) |
| Cavalaria (dragões azul-claros, couraceiros brancos, hussardos do atlas 05) | Casaca, capacete e equipamento de cavalaria |
| Oficiais e generais (atlas 04) | Outro corte, bordados, chapéu bicorne |
| Pluma verde da barretina | Precisa de geometria nova. **Atualizado em 2026-10-12:** a geometria de plumet foi esboçada para a barretina francesa (`docs/reports/barretina_fr_blockout.md`); aprovada a forma (B1), entra aqui também (§9.2) |
| `prussiabz` | O mod não traz a cor de cada unidade (máscara de cor sem tabela) |

**Nomes de regimento:** os arquivos do mod disponíveis são só texturas (`.dds`/`.tga`). Não há arquivo que ligue cada bloco a um regimento, por isso os nomes continuam técnicos (V-B).

### 9.1 Conferência final do lote (2026-10-11, addon instalado às 14:52)

`source/scripts/conferir_regimentos.py` lê o `config.bin` **do PBO instalado**, convertido para texto com `CfgConvert -txt`. Para cada item, confere que a classe existe e que toda textura e modelo citados estão dentro do PBO:

| Grupo | Classes | Problemas |
|---|---|---|
| Uniformes V01–V17 (+ 17 classes de soldado) | 34 | 0 |
| Barretinas | 14 | 0 |
| Correame (branqueado, preto) | 2 | 0 |
| Mochila (branqueada, preta) | 2 | 0 |

Também valem para todos os itens:
- os 8 modelos têm o esqueleto `OFP2_ManSkeleton`;
- a **gola corrigida** (`docs/reports/gola_pruss.md`) é comum aos 17 uniformes, porque eles compartilham a mesma malha.

**Repetida em 2026-10-11 às 23:13**, depois das correções de `docs/reports/correcoes_realismo_pruss.md` (calça, pesos v2, botões, texturas refeitas): mesmo resultado, 0 problemas. Os 8 modelos têm esqueleto e as 67 referências estão dentro do PBO. As correções valem para todos os itens: os uniformes compartilham a malha e os pesos, e o equipamento é o mesmo nos dois couros.

**Teste no jogo de todos de uma vez:** `release/@Historical_Clothing/teste_desfile_console.sqf`. É um texto para o console de depuração, gerado pelo mesmo script a partir dos mesmos dados: ele põe os 17 soldados em fila, com as barretinas em rodízio e o couro do bloco do mod. **Não executado** (exige o jogo aberto).

### 9.2 Barretina com plumet verde (pedido de 2026-10-12: "pompons aumentados... iguais aos daquela época")

| Item | Fato | Confiança |
|---|---|---|
| No mod | Plumet **verde-escuro** em leque de pelos ou penas: `prussia1813_01_diffuse`, blocos c5–c6 r5 (folha `work/ntw/prussia1813/folha_p01_cabeca.png`) | 🎮 |
| Outros plumets nos atlas prussianos | Branco (`_04`, c2 r5–r6) junto com dragonas, cruz de ferro e estrela: **oficiais** (atlas 04, fora da base). `_03` e `_05`: capacetes e caveiras de **cavalaria** (fora) | 🎮 |
| Quem usava | Provavelmente os **Jäger voluntários** (*Freiwillige Jäger*) de 1813: mesma casaca do regimento, mas em **base verde** (como V09–V17). Uma barretina de museu de um Jäger voluntário tem "pompom alto", cocar e cruz da Landwehr. **Não era peça de regulamento** | 🔶 [miniatures.de: Freiwillige Jäger](https://www.miniatures.de/freiwillige-jaeger.html), [museum-digital Brandenburg](https://brandenburg.museum-digital.de/pdf/object/41874.pdf?lang=en) |
| Proposta | Barretinas existentes + plumet verde (mesma geometria do plumet francês, com textura de pelos verde-escuros). Nome técnico `..._PlumetVerde`, sem nome de unidade | Depende de B1 |
| Garde zu Fuß (pedido de 2026-10-12) | Barretina de granadeiro do 1º Regimento de Guardas a Pé, "em ordem de 1815", com **Stutz alto branco e preto** (registro de colecionador). No esboço: na barretina de estrela, Stutz de 0,22 m, **branco em cima e preto embaixo** (a ordem das cores é suposição), com o mesmo gerador de penas. Para a Guarda, usar a estrela **prateada** | 🔶 [world4.eu, item 587](https://world4.eu/shakos-napoleonic-wars/) |
| Esboço (2026-10-12) | `source/scripts/blockout_plumet_pruss.py` sobre as 3 barretinas de produção (FWR, águia, estrela): plumet de 0,30 m na frente do alto, atrás do cocar, em tulipa de latão; topo a 1,25 m do chão. Imagens `docs/reports/img/barretina_pruss_plumet/plumet_pruss_{frente,lado}.png`. O mod desenha o plumet como leque de pelos: na produção ele vira lâminas de penas em leque, não um fuso liso | Aguarda B1 |

**O que falta para considerar o lote fechado depende do usuário:**
- aprovar (V-A, V-G);
- decidir a gola das V15/V16 (V-F);
- aprovar a forma do plumet (B1 da barretina francesa); aí faço a barretina prussiana com plumet verde (§9.2);
- olhar no jogo.

Imagens finais (com a gola corrigida): `docs/reports/img/regimentos/{azuis,verdes,barretinas}_{frente,tres_quartos,detalhe}.png`.

Imagens: `docs/reports/img/regimentos/verdes_{frente,costas,tres_quartos,detalhe}.png` e `barretinas_{...}.png`. Script: `source/scripts/render_regimentos.py`.
