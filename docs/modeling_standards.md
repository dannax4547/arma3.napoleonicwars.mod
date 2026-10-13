# Padrões de Modelagem

Fase 1. Atualizado em 2026-10-09.

Cada regra indica a origem: **[V]** verificado (ver `references.md`) · **[W]** wiki, por citação indireta, a confirmar · **[P]** proposta do projeto, a validar nos testes.

---

## 1. Unidades, eixos e nomes

| Regra | Origem |
|---|---|
| 1 unidade do Blender = 1 metro | [P] |
| Blender: +Z para cima, frente do item = −Y. A conversão de eixos para o Object Builder será definida no primeiro teste de importação FBX (teste B1); não é suposta | [P] |
| Transformações aplicadas (escala 1, rotação 0) antes de exportar | [P] |
| Prefixo `HCL_` em classes, objetos e arquivos (`hcl_` em minúsculas nos nomes de arquivo) | Briefing |
| Nomes de seleções e propriedades nomeadas em minúsculas | [W] |

## 2. Corpo de referência e encaixe

| Regra | Origem |
|---|---|
| Itens de cabeça são ponderados ao osso **`head`** do esqueleto **`OFP2_ManSkeleton`** | [V] (os modelos oficiais contêm `head` e `OFP2_ManSkeleton`) |
| Por isso, o item é modelado **na posição da cabeça do personagem do ARMA 3**, e não na origem | [V] por dedução dos modelos oficiais; confirmar com `A3_headgear_example.p3d` |
| Corpo de referência oficial: `A3_character_example.p3d` do **Arma 3 Samples**, lido por `source/scripts/p3d_mlod.py`; linha da cabeça tirada do boné oficial `A3_headgear_example.p3d` | [V] instalado em 2026-10-09 |
| A cabeça oficial é um *proxy* e não vem no Samples; o encaixe usa a linha da cabeça do boné oficial | [V] |
| Alternativa disponível agora: `ObjectBuilder\O2Scripts\CharacterGeo\NewGeometryTemplate.p3d` (LOD de geometria de personagem, editável). Dá volumes, mas não a malha visual | [V] (arquivo existe) |
| O manequim oval usado nos protótipos exploratórios **não** serve como referência de encaixe | Decisão |

## 3. Topologia e densidade

| Regra | Origem |
|---|---|
| Quads onde possível; triângulos aceitos em polos e reduções | [P] |
| Sem faces duplicadas, vértices soltos, faces de área zero ou interseções acidentais | Briefing |
| Normais para fora; bordas duras por arestas marcadas como sharp ou por divisão justificada (costura de UV, quebra de material) | [P] |
| Espessura real nas bordas visíveis: pala ≥ 2,5 mm, parede de feltro ≈ 3–4 mm, faixas de couro/tecido ≈ 1 mm acima da superfície | [P] (medidas de referência, a ajustar à peça) |
| Detalhe proporcional à distância de visualização: costuras, tramas e pespontos ficam na textura e no normal map; geometria só para silhueta e volumes que aparecem de lado | [P] |
| Peças separadas só com justificativa técnica (ex.: pompom e monograma em relevo); cada separação fica registrada | Briefing |
| Orçamento inicial do LOD 0 de uma barretina: **até 6.000 triângulos**; LODs seguintes com cerca de 50%, 25% e 10% | [P]. O limite técnico por LOD existe [W] e será medido no Buldozer |

## 4. UV e texel

| Regra | Origem |
|---|---|
| Uma folha de **1024×1024** por item de cabeça, para começar | [P] |
| Densidade de texel alvo: **≈ 1.500–2.000 px/m**, igual entre ilhas visíveis | [P] |
| Margem entre ilhas: ≥ 8 px (em 1024²) | [P] |
| Simetria/sobreposição de UV só onde não houver detalhe assimétrico (monograma, costura traseira) | Briefing |
| Dimensões das texturas em potência de 2 | [V] (convenção do ImageToPAA e das texturas oficiais) |

## 5. Materiais e texturas

| Regra | Origem |
|---|---|
| Sufixos: `_co` (cor, DXT1), `_ca` (cor + alfa, DXT5), `_nohq` (normal, DXT5), `_smdi` (especular, DXT1), `_as` (sombra ambiente, DXT1) | [V] `TexConvert.cfg` do ImageToPAA |
| Os modelos oficiais de cabeça usam `.rvmat` com `_nohq` e `_smdi`; o capacete também `_as` e o boné `_ti_ca` (térmica) | [V] |
| Um `.rvmat` por material físico: feltro, tecido, couro envernizado, metal | [P] |
| Material do Blender **não** é compatível com o jogo; serve só para pré-visualização. Os `.rvmat` são escritos à parte, tendo como modelo os `.rvmat` oficiais | Briefing + [P] |
| Seleção **`camo`** cobrindo as faces que trocam de textura por `hiddenSelectionsTextures` | [V] |
| Texturas-fonte editáveis (`.blend`/`.png`/scripts) preservadas em `source/textures/` | Briefing |

## 6. LODs e propriedades (item de cabeça)

**Verificado no modelo-base oficial `A3_headgear_template.p3d` (Arma 3 Samples) em 2026-10-09:**

| LOD | Conteúdo | Propriedades | Origem |
|---|---|---|---|
| Resolução 1, 2, 3 | Malha visual com seleções `Head` (pesos) e `camo` | `LODNoShadow=1` | [V] |
| View Pilot (1100) | **Vazio** | — | [V] |
| Shadow Volume 0 (10000) | Sombra simplificada e fechada, seleção `Head` | — | [V] |
| Geometry (1e13) | **Vazio**, com massa | `autocenter=0`, `prefershadowvolume=1` | [V] |

Referência de densidade do exemplo oficial (boné): 400 / 200 / 56 faces nos LODs 1–3; sombra com 72 faces. Uma barretina tem mais volume e detalhe; o orçamento será fixado na Fase 4 tendo esse exemplo como base.

## 7. Coerência histórica

- Toda peça tem uma ficha técnica (Fase 2) com elementos confirmados e incertos.
- **Nenhum detalhe regimental é inventado.** Detalhe sem fonte fica marcado como incerto ou não é modelado.
- Referências de terceiros sem autorização: só visuais.

## 8. Checklist de revisão técnica (Fase 5)

| Verificação | Como | Quem |
|---|---|---|
| Normais e orientação | Script Blender: comparar com as direções esperadas; Face Orientation no viewport | Claude (script) + usuário (visual) |
| Vértices duplicados | `bmesh` / Merge by Distance em modo de teste (contar, não aplicar) | Claude |
| Buracos e arestas não-manifold | Contagem de arestas de borda e não-manifold, justificando cada uma | Claude |
| Faces internas e interseções | Inspeção visual + BVH overlap no Blender | Claude + usuário |
| Espessura | Medição nas vistas ortográficas | Claude |
| Transformações, escala, orientação | Propriedades do objeto | Claude |
| Distribuição de polígonos | Contagem por parte | Claude |
| Encaixe no corpo de referência | Vistas ortográficas sobre o corpo oficial | Usuário aprova |
| Limite por LOD | Buldozer (Object Builder) | Usuário |
