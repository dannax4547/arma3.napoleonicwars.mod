# Kivers russos: malha de jogo e bake (Fase 4)

2026-10-17. Pedido do usuário: *"Aprovo RB1–RB3. Segue para a Fase 4 da Rússia (malha de jogo do kiver e bake das tranças), mantendo o padrão de fontes."*

**Base histórica:** dossiê `docs/research/rus/HIST-RUS-INF-KIVER-1812-001.md` (decisões D1–D17). A Fase 4 **não muda nenhuma forma** aprovada no blockout. Só decide o que vira geometria de jogo e o que vira detalhe assado.

**Situação:** gerado e verificado automaticamente no Blender 5.2. **Nada foi visto no ARMA 3**: P3D, LODs técnicos, seleções e `.rvmat` são da Fase 7. Sem o Arma 3 Samples, o encaixe continua lido do blockout britânico aprovado.

## 1. Método

| Etapa | O que foi feito | Por quê |
|---|---|---|
| Uma fonte paramétrica, dois níveis | `blockout_kiver_rus.py` virou também um módulo: `LOW = False` gera o modelo alto de design e `LOW = True` gera a malha de jogo, **com as mesmas funções de perfil** | A silhueta de jogo é, por construção, a mesma conferida contra as fontes (prancha 1323, Hermitage) |
| Geometria × bake | **Geometria:** corpo, tampo, pala, granada e chamas, pompom, pluma, rosetas, barbicacho (uma tira com a espessura das escamas), tranças (faixa de seção retangular), cordões, borlas, raquete. **Bake:** faixas, tiras em V, tira de trás, presilha, costura, debrum da pala, pontos da trança em espinha de peixe, fios das borlas, mechas da pluma, escamas, centro do pompom | `modeling_standards.md` §3 ("geometria só para silhueta e volumes que aparecem de lado") e especificação mestre §23 |
| UV | *Smart project*, ilhas na mesma densidade (*average islands scale*), empacotadas com margem de 16 px em 2048 (= 8 px por 1024) | `modeling_standards.md` §4 |
| Bake **explodido**, por peça | Cada peça de jogo é assada **só** das peças altas correspondentes: o nome mais longo que é prefixo do nome alto (`pompom_centro` → `pompom`, `sultao_mechas` → `sultao`, `borla_E_0_franja` → `borla_E_0`). O couro do barbicacho vai para as escamas; faixas, tiras, tira de trás, presilha e costura vão para o corpo. Grupos afastados 0,8 m no bake | A 1ª tentativa, sem explodir, contaminou peças vizinhas (vermelho do pompom na pluma, preto da pluma no pompom). É a prática padrão ("match by mesh name") |
| AO montado | O AO é assado com as peças nos lugares (sombra de contato entre cordão e corpo), **sem** as mechas da pluma e as franjas das borlas | Os cartões finos e densos assavam oclusão quase preta; o relevo deles já está no normal map |
| Metais | No bake de cor, o latão é tratado como não metálico | O passe de cor difusa do Cycles devolve preto em material metálico |
| Raios do AO (correção de 2026-10-18) | No bake do AO, só a fonte do AO bloqueia os raios: a malha de jogo e a cópia do modelo alto ficam invisíveis para eles | Na 1ª versão, as superfícies abertas saíam com AO ≈ 0,5 em vez de ≈ 1 (mediana medida 0,47). A malha de jogo, até 6 mm por fora da alta, tapava meio hemisfério. Achado na Fase 6 |

Comando:

```
blender -b --factory-startup --python source/scripts/build_kiver_rus_jogo.py -- source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_jogo.blend source/textures/hcl_kiver_rus docs/renders/rus ao=64
```

## 2. Resultado

| Kiver | Triângulos (LOD0) | Orçamento | Malha alta | Texel (2048) | Materiais (slots) |
|---|---|---|---|---|---|
| 1812 mosqueteiro | **4.628** | 6.000 | 51.104 | 1.944 px/m | pano, verniz, couro (carneira), forro, latão, branco |
| 1812 granadeiro | **5.244** | 6.000 | 55.048 | 1.740 px/m | + vermelho (pompom), crina |
| 1808 mosqueteiro | **4.694** | 6.000 | 48.968 | 2.053 px/m | feltro, verniz, couro, carneira, forro, latão, branco |
| 1808 granadeiro | **5.310** | 6.000 | 52.912 | 1.819 px/m | + vermelho, crina |

Repartição no 1812 mosqueteiro: tranças, cordões, borlas e raquete ~1.420; corpo, tampo, pala e pompom 2.168; barbicacho e rosetas 800; granada 244.

**Arquivos:**
- malha de jogo e modelo alto (oculto): `source/models/shakos/hcl_kiver_rus/hcl_kiver_rus_jogo.blend`, objetos `HCL_H_RUS<modelo>_<Variante>_LOD0`;
- mapas (2048 PNG, fontes para o ImageToPAA): `source/textures/hcl_kiver_rus/hcl_kiver_rus<modelo>_<variante>_{nohq,cor,ao}.png`;
  - `_nohq`: normal tangente, OpenGL (+Y), a mesma convenção das barretinas prussiana e francesa;
  - `_cor`: cor-base de identificação. **Não é a textura final**: a Fase 6 pinta os materiais (pano, verniz, latão, lã, crina) sobre ela;
  - `_ao`: oclusão ambiente;
- renders: `docs/renders/rus/jogo_kiver_rus_<variante>_{frente,perfil,tres_quartos}.png` (à esquerda o modelo alto; à direita a malha de jogo com os mapas assados).

## 3. Verificações (fora do jogo)

`mesh_review.py` nas 4 malhas de jogo:

| Verificação | Resultado | Observação |
|---|---|---|
| M2 vértices duplicados | **0** | Antes da correção: 25 (anéis colapsados nas pontas, peças que se tocavam no mesmo ponto) |
| M3 arestas não-manifold | **0** | |
| M4 faces de área zero, geometria solta | **0** | Antes: 16 (pontas da raquete e da pala) |
| M5 autointerseções dentro das peças | **0** | Antes: 73–94 (parede interna e forro cortando a parede côncava) |
| M5 pares de peças que se cruzam | 11–20 | **Todos são encaixes**, listados por `diag_low`: granada e gargalo na parede, chama no gargalo, barbicacho na roseta, as duas tiras sob o queixo, cordões nas tranças e na raquete, borlas nos cordões, junção das duas tranças |
| M1 ilhas abertas | 1–2 | **De propósito**: carneira e forro, superfícies internas de face única vistas por baixo |

Correções feitas no gerador (valem também para o modelo alto, regenerado):
- **Parede interna e forro:** passaram a acompanhar as fileiras da parede côncava. A corda entre fileiras distantes atravessava a parede.
- **Borda de cima do corpo:** fechada, para as normais apontarem para fora.
- **Normal da parede sob os cordões:** passou a vir da superfície real. O cisalhamento do tampo (D3) deslocava a altura na traseira em até 31 mm.
- **Pontos de controle das tranças:** densificados a cada 10°. Entre pontos a 40°, a curva cortava a parede.
- **Borlas:** espaçadas pelo diâmetro da saia, e ganharam um núcleo sólido sob os fios.
- **Peças que se tocam:** deslocadas 1–3 mm, sem vértice em comum.
- **Cartões de face única** (mechas da pluma, fios das borlas): viraram para fora. O raio do bake acertava o verso e gravava normais invertidas (manchas oliva no `_nohq`, pretas na pré-visualização).
- **Pontas da raquete:** ganharam largura mínima de 1,2 mm. O anel colapsado deixava a malha não-manifold e as normais da raquete invertidas.

**Não verificado:** cruzamentos com a cabeça do jogo e com a gola (precisam do Samples); LOD1–3, sombra e Geometry (Fase 7); aparência no motor (Fase 9).

## 4. Pendências

- **Fase 6 (texturas):** pintar os materiais sobre `_cor` (pano fosco, couro envernizado, latão polido com escurecimento nos fundos, lã branca, crina), e montar `_co` (cor × AO) e `_smdi`.
- **Fase 7:** LOD1–3 (~50 %, 25 %, 10 %), sombra, Geometry vazia, seleção `camo` para os pompons por batalhão (RU7, 6 variantes só de textura) e os `.rvmat` por material.
- **Com o Samples:** rodar o blockout e esta fase com a pasta `Test_Character_01` e conferir o encaixe.
- **Com o atlas do mod:** conferir as cores.
