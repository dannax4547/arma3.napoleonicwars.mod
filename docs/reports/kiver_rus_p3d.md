# Kivers russos: P3D, LODs, sombra, camo e .rvmat (Fase 7)

2026-10-18. Pedido do usuário: *"Sim. Segue para a Fase 7 do kiver russo (LODs, sombra, Geometry, seleção camo dos pompons e .rvmat), mantendo o padrão de fontes."*

**Base:**
- **Formato:** `docs/modeling_standards.md` §6 (LODs e propriedades de item de cabeça, verificados no `A3_headgear_template.p3d` oficial).
- **Pompons:** ficha `docs/specs/rus_1812.md` §2.4 (ordem de 22 fev 1811) e dossiê `HIST-RUS-INF-KIVER-1812-001`, decisão D18 e incerteza I6.

**Situação:**
- **Gerado e verificado fora do jogo:** P3D lido de volta, byte a byte idêntico; sombra fechada; contagens.
- **Nada foi aberto no Object Builder nem visto no ARMA 3.** As `.paa` ainda não existem (precisam do Arma 3 Tools), e `config.cpp` e `model.cfg` são da Fase 8.

## 1. Modelo-base sem o Samples

O Arma 3 Samples continua ausente nesta máquina. Por isso o modelo-base é uma barretina que o projeto já construiu **a partir** do template oficial: `source/addon/hcl/hcl_fr/hcl_h_fr_fuzileiro_losango.p3d` (`build_p3d_fr.py`).
- **View Pilot (1100) e Geometry (1e13):** copiados sem mudança. São os do template.
- **Propriedades lidas e conferidas pelo script:** `LODNoShadow=1` nos visuais; `autocenter=0` e `prefershadowvolume=1` na Geometry.
- **Coordenadas:** o mesmo espaço da barretina francesa (frente em −Y, P3D com y e z trocados). A base do corpo fica em z 0,700 e as francesas em 0,57–0,99 (com o barbicacho).
- **Com o Samples instalado:** basta trocar o 2º argumento pelo template oficial.

## 2. Método

| Item | O que foi feito | Por quê |
|---|---|---|
| Res 1 | A malha de jogo da Fase 4, sem mudança | Já conferida (`mesh_review`, orçamento de 6.000) |
| Res 2, 3, 4 | ~50 %, 25 % e 10 % dos triângulos (`modeling_standards.md` §3), **por peça**: cada peça de jogo é reduzida com a mesma razão, achada por bisseção. No Res 3 e 4 sai o interior (carneira e forro); no Res 4, também as peças menores que 3 cm (rosetas, pontas da raquete) | A 1ª versão, uma redução única sobre a malha toda, gastava o orçamento nas peças pequenas e quebrava a pala e o corpo no Res 3 e 4 (render conferido). Mesmo UV e mesmo atlas em todos os LODs |
| Sombra (10000) | Cascos convexos fechados: kiver (corpo, tampo, pala, cordões e granada, acima da base do corpo), pompom e pluma. Pontos em grade de 8 mm | Sombra precisa de volume fechado. O casco único (método das barretinas britânicas) encheria o vão sob o queixo, por causa do barbicacho e dos cordões pendentes |
| Seleções | `camo` = todas as faces visuais; `Head` = todos os pontos com peso total, em todos os LODs e na sombra | `modeling_standards.md` §5–6; item rígido na cabeça, como as outras barretinas |
| Batalhões (RU7) | 2º e 3º batalhão **só por textura**: o pompom é assado de novo com as cores de cada batalhão sobre uma cópia do albedo, e o resto do atlas fica igual. A troca no jogo é por `hiddenSelectionsTextures` na seleção `camo` | O mesmo método dos pompons franceses (`variantes_pompom_fr.py`): um P3D serve aos 3 batalhões |
| `.rvmat` | **Um por material físico** e por kiver: pano, feltro, couro, verniz, latão, lã, crina. Mesma estrutura dos `.rvmat` do projeto (shader *Super*, do `nodiffuse.rvmat` do Samples), lendo o `_nohq` e o `_smdi` do kiver. Mudam só `specularPower` e a cor do brilho | `modeling_standards.md` §5 (um `.rvmat` por material). O brilho por texel já está no `_smdi` |

Comandos:

```
blender -b --factory-startup --python source/scripts/texturizar_kiver_rus.py -- source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_jogo.blend source/textures/hcl_kiver_rus docs/renders/rus
blender -b --factory-startup --python source/scripts/build_p3d_kiver_rus.py -- source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_jogo.blend source/addon/hcl/hcl_fr/hcl_h_fr_fuzileiro_losango.p3d source/addon/hcl/hcl_rus docs/renders/rus
```

## 3. Resultado

| P3D (`source/addon/hcl/hcl_rus/`) | Res 1 / 2 / 3 / 4 (triângulos) | Sombra | `.rvmat` |
|---|---|---|---|
| `hcl_h_rus1812_mosqueteiro.p3d` | 4.628 / 2.314 / 1.157 / 463 | 180 (2 cascos) | couro, lã, latão, pano, verniz |
| `hcl_h_rus1812_granadeiro.p3d` | 5.244 / 2.622 / 1.307 / 523 | 340 (3 cascos) | + crina |
| `hcl_h_rus1808_mosqueteiro.p3d` | 4.694 / 2.346 / 1.172 / 468 | 188 (2 cascos) | couro, feltro, lã, latão, pano, verniz |
| `hcl_h_rus1808_granadeiro.p3d` | 5.310 / 2.654 / 1.326 / 530 | 360 (3 cascos) | + crina |

Cada P3D tem 7 LODs: 1, 2, 3, 4, 1100, 10000 e 1e13. Os `.rvmat` estão em `source/addon/hcl/hcl_rus/data/` (24 arquivos) e o log em `build_p3d_kiver_rus_log.txt`.

**Texturas por batalhão** (`source/textures/hcl_kiver_rus/`):

| Arquivo | Batalhão | Mosqueteiro | Granadeiro |
|---|---|---|---|
| `<base>_co.png` | 1º | branco, centro verde | vermelho |
| `<base>_b2_co.png` | 2º | verde, centro branco | vermelho, terço de baixo verde |
| `<base>_b3_co.png` | 3º | azul-celeste, centro branco | vermelho, terço de baixo azul-celeste |

`<base>` = `hcl_kiver_rus<1812|1808>_<mosqueteiro|granadeiro>`. O `_nohq` e o `_smdi` são os mesmos para os 3 batalhões.

**Renders:**
- LODs lado a lado (Res 1, 2, 3, 4 e a sombra em vermelho): `docs/renders/rus/lods_kiver_rus_<variante>.png`;
- batalhões: `docs/renders/rus/textura_kiver_rus_<variante>_b2_frente.png` e `_b3_frente.png`.

## 4. Verificações (fora do jogo)

- **P3D:** cada arquivo foi lido de volta por `p3d_mlod_io.py` e regravado **byte a byte idêntico**.
- **Sombra:** 0 arestas abertas nas 4 (volumes fechados).
- **Batalhões:** só os texels do pompom mudam (11–45 mil texels, conforme a variante). Conferido nos renders das 8 variantes.
- **LODs:** contagens dentro de ±0,5 % do alvo; silhueta conferida nos renders. No Res 4 a pala dobra um pouco (redução forte numa placa fina); a essa distância a pala tem poucos pixels.

## 5. Limitações e pendências

- **Não testado no jogo:** Object Builder, Buldozer e ARMA 3. A troca de LOD por distância e o efeito dos `.rvmat` precisam do motor.
- **Valores dos `.rvmat` (`specularPower` 18–140, brilho do latão em tom quente):** **estimados**, para ajustar no Buldozer.
- **Sombra:** 180–360 triângulos, contra 72 no boné oficial. A pluma e o pompom pedem cascos próprios. Dá para engrossar a grade se o custo pesar.
- **Pompom de granadeiro do 2º e 3º batalhão:** o "terço de baixo" é interpretação (I6); as cores são provisórias até conferir no atlas.
- **Fase 8:**
  - `config.cpp` (classes por batalhão com `hiddenSelectionsTextures`);
  - `model.cfg` com a seção `camo` e o osso `Head`;
  - conversão PNG → PAA (Arma 3 Tools).
- **Com o Samples:** rodar de novo com o template oficial e conferir o encaixe na cabeça (`Test_Character_01`).
