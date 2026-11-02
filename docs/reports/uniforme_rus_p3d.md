# Casaca russa de 1812: pesos, LODs, sombra, P3D e .rvmat (Fase 7)

2026-10-18. Pedido do usuário: *"Segue para a Fase 7 da casaca russa (pesos, LODs, sombra, P3D com as 5 variantes e .rvmat), mantendo o padrão de fontes."*

**Base:**
- **Formato:** `docs/modeling_standards.md` §3 (LODs ~50/25/10 %), §5 (`.rvmat`, seleção `camo`) e §6.
- **Malha e texturas:** Fases 4–6 da casaca (`docs/reports/uniforme_rus_texturas.md`).
- **Fontes históricas:** a Fase 7 não muda forma nem cor; elas seguem no dossiê `HIST-RUS-INF-COAT-1812-001`.

**Situação:**
- **Gerado e verificado fora do jogo:** P3D lido de volta byte a byte, seleções iguais às do uniforme francês feito do template, pesos completos.
- **Sem o Arma 3 Samples e o Tools nesta máquina:**
  - sem teste de movimento (as animações RTM são do Samples);
  - sem Object Builder, sem `.paa`;
  - nada visto no jogo.

## 1. Pesos

A casaca russa é a malha de produção prussiana com a **mesma topologia**. O `build_uniforme_rus.py` troca os 14 botões da frente prussiana por 12 da frente e 2 das abas, e o BMesh põe os novos nas vagas dos apagados. Todos os outros vértices mantêm o índice.

| Verificação | Resultado |
|---|---|
| Vértices que o construtor não mexe (mangas, punhos, palas, platinas, mãos, assento, polainas, sapatos) | Coincidem com os prussianos no mesmo índice (desvio 0,0000 mm) |
| Vértices movidos (frente C11, gola C4, abas C5, pernas C12) | Mesmo índice: os pesos do mesmo ponto de pano, já deslocado |
| Botões que não estão onde estava o prussiano | 16 (12 da frente, 2 das viradas, 2 da cintura): recebem os pesos do vértice de pano mais próximo, sob cada um |
| Resultado | 6.470 vértices, 62 ossos; soma dos pesos 1,000 em todos; até 4 ossos por vértice |

**Origem:** `source/models/pesos/hcl_pruss_pesos_v2.blend`, os pesos aprovados da casaca prussiana, os mesmos do P3D prussiano. Foram feitos pelo `teste_movimentos.py` a partir do corpo oficial, com o alto da gola no osso `Neck`.

**Arquivo novo:** `source/models/pesos/hcl_rus_pesos.blend`, no padrão dos outros arquivos de pesos.

## 2. P3D

**Modelo-base sem o Samples:** `source/addon/hcl/hcl_fr/hcl_u_fr1812.p3d`, um uniforme que o projeto construiu **a partir** do `A3_character_template.p3d` oficial (`build_p3d_fr.py`). Dele vêm, sem mudança:
- os 11 proxies (arma, pistola, binóculo, lançador, bandeira, equipamento, mochila, óculos, cobertura, HMD, cabeça) e a textura/`.rvmat` das mãos do template;
- as propriedades (`LODNoShadow=1`);
- todos os LODs a partir de 10000: as duas sombras do corpo, Geometry, Memory, LandContact, Hit-points e Fire Geometry.

**LODs visuais**, em `source/addon/hcl/hcl_rus/hcl_u_rus1812_linha.p3d`:

| LOD | Triângulos | Proporção | Conteúdo |
|---|---|---|---|
| Res 1 | 11.960 | 100 % | A casaca da Fase 6 |
| Res 2 | 5.982 | 50 % | Redução por peça, com a mesma razão em todas (bisseção) |
| Res 3 | 2.990 | 25 % | Sem os botões (ficam na textura); mãos com metade da razão |
| Res 4 | 1.524 | **13 %** | Idem. Toda peça guarda **no mínimo 80 triângulos**: com 10 % a gola (anel de 340) e as pernas se rompiam no render. Por isso passou dos 10 % |
| View Pilot (1100) | 11.960 | — | A casaca, como nos outros uniformes do projeto |

- **Proxies:** em todos os LODs visuais.
- **Pesos:** levados pela redução; 0 vértices sem peso em cada LOD.
- **Seleções:** 81 em cada LOD visual, **as mesmas** do uniforme francês: 62 ossos, `Camo`, `hl`, `injury_hands` e os proxies. O View Pilot tem 80, como o francês (sem o proxy de óculos).

**5 variantes:** uma só malha. A seleção `Camo` cobre todas as faces da roupa, e o `config.cpp` (Fase 8) troca a textura por `hiddenSelectionsTextures[] = {"hcl\hcl_rus\data\hcl_u_rus1812_linha_v0N_co.paa"}`, com N de 1 a 4 (platina vermelha, branca, amarela, verde debruada de vermelho; a 5ª, azul-celeste, saiu pela decisão RU11). No P3D as faces levam a `_v01`.

## 3. Sombra

Ficam as **duas sombras do corpo do template** (10000 e 10010), copiadas sem mudança:
- **Por quê:** uma sombra precisa ser fechada **e ter pesos** para acompanhar a animação, e essas a Bohemia já fez e conferiu. É o que os outros uniformes do projeto usam.
- **Limite:** a casaca segue o corpo, mas as abas saem alguns centímetros dele e não projetam sombra própria.

## 4. .rvmat

Um por material físico, em `source/addon/hcl/hcl_rus/data/`. A estrutura é a dos `.rvmat` do projeto (shader *Super*, do `nodiffuse.rvmat` do Samples). Os três leem o `_nohq` e o `_smdi` da casaca:

| Arquivo | Faces | `specular` / `specularPower` |
|---|---|---|
| `hcl_u_rus1812_linha_la.rvmat` | Todo o pano, polainas inclusive | 0,4 / 50 (o mesmo do uniforme francês) |
| `hcl_u_rus1812_linha_couro.rvmat` | Sapatos e solas | 1,0 / 70 (**estimado**) |
| `hcl_u_rus1812_linha_latao.rvmat` | Botões | brilho quente 1,0 / 0,82 / 0,55, 90 (**estimado**) |

As mãos mantêm o `.rvmat` do template (`hl_white_bald_muscular.rvmat`). O `_smdi` dá o brilho de cada texel; os `.rvmat` só limitam o máximo.

**Render dos LODs** (Res 1 a 4, textura R01): `docs/renders/rus/lods_casaca_rus.png`.

Comando:

```
blender -b --factory-startup --python source/scripts/build_p3d_uniforme_rus.py -- . source/addon/hcl/hcl_fr/hcl_u_fr1812.p3d docs/renders/rus
```

## 5. Limitações e pendências

- **Teste de movimento:** o `teste_movimentos.py` precisa das animações RTM do Samples. Os pesos são os prussianos aprovados, mas as peças que mudaram (abas mais curtas, frente, gola mais baixa, polainas até o joelho) **não foram vistas em pose**.
- **Res 4:** passou dos 10 % (13 %) por causa do mínimo por peça. A gola e as abas ainda simplificam bastante, como se espera numa vista distante.
- **Valores dos `.rvmat` de couro e latão:** estimados, para ajustar no Buldozer.
- **Fase 8:**
  - `config.cpp` com as 5 classes de uniforme (`hiddenSelectionsTextures`) e `model.cfg` (esqueleto do personagem);
  - conversão PNG → PAA (Arma 3 Tools).
- **Com o Samples:**
  - rodar o teste de movimento;
  - montar o P3D sobre o template oficial (basta trocar o 2º argumento);
  - medir a folga do pescoço.
