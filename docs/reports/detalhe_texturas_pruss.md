# Mais detalhe e texturas: uniforme, correame e mochila prussianos 1813

2026-10-11. Pedido do usuário: "mais um detalhe nas roupas, colete e mochila. Traz mais texturas e detalhes para se parecer mais realistas e vivas".

**Estado: aguarda aprovação.** Isto é a Fase 4 (malha de produção) e a Fase 6 (UV e texturas) do correame e da mochila, mais a versão 2 das texturas do uniforme. Nada foi testado dentro do jogo ainda.

Legenda: ✅ verificado · 🔶 prática geral da época, sem fonte primária · ❓ a decidir

## 1. O que mudou

### 1.1 Correame e mochila: do blockout para a malha de produção

| | Blockout (Fase 3) | Produção (agora) |
|---|---|---|
| Correias | Caixa de seção retangular, cor lisa | Seção com bordas superiores arredondadas; cinturão fecha numa **fivela de latão de moldura**, com barra central e fuzilete; **ponta do cinturão** com final arredondado e furos; **passador** |
| Cartucheira | Duas caixas | Corpo com arestas arredondadas; **tampa dobrada** sobre o topo e a frente, cantos inferiores arredondados; **placa lisa de latão** (recomendação E2); **presilha de fecho com botão** |
| Bandoleira | Termina atrás da caixa | As duas pernas entram sob a dobra da tampa, nos cantos de cima da cartucheira |
| Baioneta | Cilindros | Bainha achatada com bocal e ponteira de latão e **remate em bola**; passador com alça no cinturão, bolso e painel; baioneta de alvado com anel de reforço, pescoço e raiz da lâmina |
| Mochila | Caixa e tampa retas | Corpo de cantos arredondados e **levemente estufado**; **tampa de pele dobrada** sobre o topo; **2 correias de fecho com fivelas** e presilhas |
| Capote enrolado | Cilindro liso | Dobras ao longo do rolo, borda da camada de fora, **pontas rebaixadas em espiral**, **estrangulado sob as 2 cintas**, cintas com fivela e ponta |
| Correias de ombro | Correia contínua | **Fivela no peito**, ponta da correia de baixo com furos e passador |

Script: `source/scripts/build_equipamento_producao.py`. Saída: `source/models/accessories/hcl_equipamento_pruss/hcl_equipamento_pruss_LOD0.blend`, com os objetos `HCL_V_Pruss1813_Correame_LOD0` e `HCL_B_Pruss1813_Tornister_LOD0`.

Verificações (saída do script, `docs/reports/img/equipamento/equip_producao_output.txt`):

| | Correame | Mochila |
|---|---|---|
| Triângulos (Resolução 1) | 3.212 | 3.776 |
| Vértices sob a superfície do uniforme | **0** (eram 15 no blockout, até 3,8 mm) | **0** |
| UV | Tudo em 0..1; 78% da textura usada | Tudo em 0..1; 72% da textura usada |
| Densidade de textura | ~2.500 px/m | ~1.790 px/m |

O uniforme tem ~800 px/m.

❓ **Orçamento:** a ficha propunha ≤ 3.000 triângulos por item; a produção passa disso (3.212 e 3.776). Proposta nova: **≤ 4.000**, com aprovação.

Para encaixar sem atravessar, o cinturão mede a folga no meio e nas duas bordas, de cima e de baixo, porque o casaco abre abaixo da cintura.

### 1.2 Texturas do correame e da mochila (novas)

`source/scripts/generate_equipment_textures.py`: 2048 px por item (`_co`, `_nohq`, `_smdi`). Cada texel é pintado pela peça, pelo lado (face de cima, borda ou avesso), pelas coordenadas ao longo e através da correia, pela posição 3D e por uma **oclusão de ambiente calculada no Cycles** com o uniforme por baixo.

| Material | Detalhes |
|---|---|
| Couro branqueado (alvaiade) | Branco giz com manchas suaves de pincel e borrões; borda mais crua, onde o alvaiade gastou; avesso de couro cru; vincos transversais; sujeira nos cantos sombreados; **furos do fuzilete** nas pontas. Sem costura ao longo das correias: o couro de búfalo era de uma camada só 🔶 |
| Couro preto (cartucheira, bainha, corpo da mochila, correias de fecho) | Grão; desgaste castanho nas arestas; arranhões finos; poeira por cima; **costura na borda da tampa** da cartucheira; **costura e vira** nas arestas da mochila; costura nas bordas das correias de fecho; furos |
| Latão | Polido, com escurecimento nos cantos fechados e arranhões; chanfro brilhante na placa |
| Ferro | Pátina e pontos de ferrugem; **fenda em zigue-zague do alvado**; boca escura |
| Pele de bezerro | Pelo direcional (para baixo) com redemoinhos e manchas de tom; **debrum de couro preto costurado** 🔶; avesso de carnaça |
| Lã do capote | Feltro cinza; dobras ao longo do rolo; borda da camada de fora; **espiral das camadas** nas pontas; dobras apertadas sob as cintas |

### 1.3 Uniforme: texturas v2

`source/scripts/generate_uniform_textures_v2.py`. A malha, a UV e as cores das 8 variantes (`variantes_regimentos.json`) são as mesmas. O v1 continua em `generate_uniform_textures.py`, com cópia das saídas em `source/textures/hcl_uniforme_pruss/_v1/`.

Adicionado:
- **Oclusão de ambiente**, calculada no Cycles a partir do próprio uniforme. As mãos e os botões ficam de fora.
- **Bainhas e costuras em todas as bordas** de cada peça, calculadas pela distância 3D do texel à borda da própria peça: borda virada, sulco da costura, degrau da bainha. Nos sapatos, **costura do vira**, onde a gáspea encontra a sola.
- **Costuras de alfaiataria:**
  - centro das costas e costuras curvas laterais das costas do casaco;
  - manga em duas partes;
  - costuras de fora e de dentro das calças;
  - **pestana abotoada das polainas**, traçada pela linha dos botões.
- **Dobras de tecido** (relevo e cor):
  - cotovelo, por dentro;
  - acima dos punhos;
  - axilas;
  - atrás dos joelhos;
  - frente do quadril;
  - tornozelos (polainas);
  - caimento das abas;
  - vinco do bico dos sapatos.
- **Superfície:**
  - lã batida sem trama visível. O v1 tinha uma sarja que mudava de direção a cada ilha da UV; foi removida;
  - sol desbotando as superfícies de cima;
  - brilho de gasto em cotovelos, beiradas dos punhos e da frente, assento e joelhos;
  - poeira e lama seca subindo do chão;
  - encardido na gola e nos punhos.
- **Relevo em milímetros:** o mapa normal usa o tamanho real do texel (1,25 mm/px) e não cruza as bordas das ilhas da UV.

## 2. Imagens

| Arquivo | O quê |
|---|---|
| `docs/reports/img/equipamento/equip_producao_*.png` | Geometria nova, sem textura (mesmas câmeras do blockout) |
| `docs/reports/img/texturas/v2_tres_quartos.png`, `v2_tres_quartos_costas.png` | Conjunto inteiro com as texturas novas |
| `docs/reports/img/texturas/v2_peito.png`, `v2_cartucheira.png`, `v2_mochila.png`, `v2_baioneta.png`, `v2_pernas.png` | Detalhes |
| `docs/reports/img/texturas/equip_v1_*.png` | Primeira passada das texturas do equipamento (antes dos ajustes do couro branco, do capote e do latão) |

Script dos renders: `source/scripts/render_texturas_pruss.py`.

## 3. Movimentos (fora do jogo)

`teste_movimentos.py` passou a usar o equipamento de produção. Pesos novos: `source/models/pesos/hcl_pruss_pesos_v1.blend` (o v0 foi mantido).

| Verificação | Resultado |
|---|---|
| Barretinas × uniforme, correame e mochila | **0 colisões** nas 8 animações (igual ao v0) |
| Alvado da baioneta × correia de ombro esquerda da mochila | Na 1ª versão, o alvado ficava atrás da bainha, sob a correia, e a atravessava até 20 mm. **Corrigido:** o alvado foi para a frente da bainha |
| Perna de trás da bandoleira × corpo da mochila (deitado, sentado) | Entra até 14 mm no **avesso** do corpo da mochila, encostado às costas. Fica dentro do volume da mochila, então não aparece. No blockout eram 5 mm |
| Diagnóstico por peça | `source/scripts/diag_camadas_equip.py` |

## 4. Addon de teste refeito

`build_mod_pruss.ps1`, com estas mudanças:
- o correame e a mochila saem com UV, textura (`camo` em `hiddenSelections`) e `.rvmat` próprios;
- os pesos vêm do v1;
- os textos "BLOCKOUT" foram retirados dos nomes.

| Etapa | Resultado |
|---|---|
| P3D | Correame 1.651 pontos / 3.212 faces; mochila 1.930 / 3.776; ossos do tronco e dos ombros |
| `config.cpp` → `config.bin`, 6 `.rvmat` | Código 0 |
| Binarize | Código 0. Avisos só dos materiais do jogo (pele das mãos, penetração), como antes |
| PBO | `pbo_verify.py`: prefixo `hcl\hcl_pruss`, 41 arquivos, nenhum arquivo-fonte, 40 referências internas e **nenhuma faltando** |
| Troca no `Addons` | **Não feita**: o Arma 3 estava aberto, e o jogo trava o `.pbo`. O FileBank devolve 0 mesmo sem regravar. O PBO novo está em `release/_atualizacao/hcl_pruss.pbo`. Com o jogo fechado, `release/atualizar_mod_teste.bat` faz a troca. O build agora detecta o arquivo travado e grava lá sozinho |

## 5. Pendências e decisões

| # | Item |
|---|---|
| ❓ | Aprovar a malha de produção do correame e da mochila (Fase 4) e as texturas (Fase 6), além do orçamento ≤ 4.000 triângulos |
| ❓ | E1–E5 da ficha do equipamento continuam abertas (E2 segue a recomendação: placa lisa) |
| 🔶 | Debrum de couro na tampa de pele e as costuras das arestas da mochila seguem a prática geral da época, sem fonte primária |
| Conhecido | Os botões do uniforme são cúpulas de 8 lados; de perto aparecem as facetas. Corrigir exige refazer a malha dos botões e a UV deles (Fase 4 do uniforme) |
| Conhecido | R1, linha entre assento e pernas da calça, continua visível (planejado para a Fase 7) |
