# Kivers russos: texturas dos materiais (Fase 6)

2026-10-18. Pedido do usuário: *"Sim. Segue para a Fase 6 do kiver russo (texturas dos materiais sobre o bake: pano, verniz, latão, lã, crina), mantendo o padrão de fontes."*

**Base histórica:** dossiê `docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md`, §7 (materiais M1–M10). O **material** de cada peça tem fonte (regulamento, original do Hermitage, estudos). O **tom numérico não tem**: não há colorimetria de época. Os tons são estimativas coerentes com o material e ficam para conferir no atlas do mod.

**Situação:** gerado e conferido no Blender 5.2, nas 4 variantes. **Nada foi visto no ARMA 3**: conversão para PAA, `.rvmat` e teste no motor são das Fases 7–9.

## 1. Método

| Etapa | O que foi feito | Por quê |
|---|---|---|
| Materiais procedurais 3D | Cada material do modelo alto ganha um material de nós em coordenadas do objeto: lã e linho (ruído fino × mosqueado), couro (grão Voronoi), verniz (quase uniforme), crina (veios no comprimento), latão e ferro (ruído leve) | Textura 3D não tem costura de UV. É o método das barretinas francesa e prussiana do projeto |
| Bake explodido, por peça | Mesmo agrupamento da Fase 4 (atributo de face `grupo`, grupos afastados 0,8 m) | Uma peça só recebe os próprios materiais (sem vermelho do pompom na pluma etc.) |
| Desgaste | Latão escurecido nos fundos (AO local de 6 mm) e mais claro nas arestas (*pointiness*); sujeira leve nos fundos da lã branca; variação de tom no pano | Só o desgaste que o uso explica (dossiê §7; especificação mestre §58: decisão artística explícita). Sem arranhões nem lama |
| `_co` | Albedo × (0,3 + 0,7 × AO), com o `_ao` da Fase 4 | Convenção `_co` = cor × oclusão (`modeling_standards.md` §5) |
| `_smdi` | R = 1, G = especular, B = brilho, por material (tabela do dossiê §7); no latão, o fundo escurecido também perde brilho | Mesma convenção das outras barretinas do projeto |
| Pré-visualização | Malha de jogo com `_co`, `_nohq` e `_smdi` (rugosidade = 1 − brilho; latão como metal) | Só para conferência. No jogo, o metal e o brilho vêm do `.rvmat` (Fase 7) |

Comando (depois da Fase 4):

```
blender -b --factory-startup --python source/scripts/texturizar_kiver_rus.py -- source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_jogo.blend source/textures/hcl_kiver_rus docs/renders/rus
```

## 2. Correção na Fase 4 (achada aqui)

Ao montar o `_co`, o `_ao` da Fase 4 estava errado. As superfícies abertas saíam com AO ≈ 0,5 em vez de ≈ 1 (mediana medida 0,47 no 1812 mosqueteiro). Por isso o `_co` escurecia tudo em ~30 %, e as borlas e a base do pompom ficavam manchadas de cinza.

- **Causa:** no bake do AO, a malha de jogo (até 6 mm por fora da alta) e a cópia do modelo alto no lugar também bloqueavam os raios.
- **Correção:** em `build_kiver_rus_jogo.py`, durante o bake do AO, só a fonte do AO fica visível para os raios. A Fase 4 foi rodada de novo nas 4 variantes.
- **Depois:** mediana do AO entre 0,984 e 0,996 nas 4 variantes. O AO baixo fica só onde deve: fundos dos cordões e do latão (percentil 10: 0,02–0,17) e o interior (carneira e forro).

A nova rodada também refez o empacotamento de UV. Os texels mudaram pouco (1812 mosqueteiro 1.944 px/m, 1808 mosqueteiro 2.053 px/m), ainda dentro de 1.500–2.000 ±. Os triângulos são os mesmos. O relatório da Fase 4 foi atualizado.

## 3. Resultado

**Mapas** (2048 PNG, fontes para o ImageToPAA), em `source/textures/hcl_kiver_rus/hcl_kiver_rus<modelo>_<variante>_*.png`, para `1812_mosqueteiro`, `1812_granadeiro`, `1808_mosqueteiro` e `1808_granadeiro`:

| Mapa | Conteúdo | Origem |
|---|---|---|
| `_co` | Cor dos materiais × AO | **Fase 6** |
| `_smdi` | Especular e brilho por material | **Fase 6** |
| `_nohq` | Normal tangente, OpenGL (+Y) | Fase 4 |
| `_ao` | Oclusão ambiente (corrigida) | Fase 4 |
| `_cor` | Paleta de identificação, não vai para o jogo | Fase 4 |

**Renders:** `docs/renders/rus/textura_kiver_rus_<variante>_{frente,perfil,tres_quartos}.png`.

**Material por peça:** veja o dossiê §7. M10 (haste de ferro do pompom) foi acrescentado nesta fase: a haste existe no blockout e nenhuma fonte a mostra. **Estimado**, quase invisível sob o pompom.

## 4. Verificações (fora do jogo)

- **`_smdi`:** valores conferidos por amostragem nos mapas. Pano (10, 27)/255 = 0,04 / 0,11; verniz (153, 232)/255 = 0,60 / 0,91 (alvo 0,85: a fórmula da variação de tom soma ~7 % ao brilho médio dos materiais sem desgaste; corrigir na Fase 7, se o `.rvmat` pedir); latão (211, 178)/255 = 0,83 / 0,70.
- **`_co`:** pano preto ~18/255 (sRGB) sob AO, couro envernizado mais escuro, lã branca sem chegar ao branco puro, latão com fundos escurecidos.
- **Renders:** conferidos nas 4 variantes. Pano fosco ao lado de couro envernizado brilhante (tampo, faixas, tiras em V, pala), latão metálico, cordões e borlas brancos, pompom limpo, pluma de crina com veios.

## 5. Limitações

- **Tons não verificados:** sem atlas do mod nem colorimetria. Pendente ⏳.
- **AO aplicado no espaço sRGB:** a multiplicação é feita nos valores gravados no PNG, como na maioria dos pipelines de `_co`. Escurece um pouco mais que a mesma conta em espaço linear.
- **Franjas das borlas:** têm pontos escuros isolados, onde o raio do bake passa entre os fios sem acertar nenhum. Pouco visíveis a distância de jogo.
- **Pluma:** lê como superfície lisa com veios, não como crina solta; o volume das mechas está só no `_nohq`. Limite da malha de jogo (424 triângulos).
- **No motor:** o brilho do verniz e o metal do latão dependem do `.rvmat` (Fase 7). A pré-visualização do Blender não equivale ao shader do ARMA 3.

## 6. Pendências

- **Fase 7:**
  - LOD1–3, sombra e Geometry;
  - seleção `camo` e `hiddenSelectionsTextures` para os pompons por batalhão (RU7: 6 variantes só de textura, a partir destes `_co`);
  - `.rvmat` por material (pano, verniz, latão, lã, crina);
  - conversão PNG → PAA (precisa do Arma 3 Tools).
- **Com o atlas do mod:** conferir os tons M1–M10.
