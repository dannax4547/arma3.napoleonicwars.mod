# Relatório: Blockout da Barretina Prussiana (Fase 3)

Data: 2026-10-09 · **Estado: aguarda aprovação do usuário (V2)**

Ficha técnica: `docs/specs/shako_prussiano_infantaria.md` v1.1 (silhueta da R2; cocar com presilha do mod; cifra FWR; sem faixa branca e sem pompom).

## 1. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `source/scripts/blockout_shako.py` | Script reproduzível do blockout |
| `source/scripts/p3d_mlod.py` | Leitor de `.p3d` editável (MLOD), só leitura |
| `source/models/shakos/hcl_shako_pruss/hcl_shako_pruss_blockout.blend` | Cena: coleção `HCL_Shako_Blockout` (10 peças sob `HCL_Shako_Root`) e coleção `REF_Arma3Samples` (referências, **não exportar**) |
| `docs/reports/img/blockout/*.png` | Vistas ortográficas, perspectiva, checagem de encaixe, comparação com R2 |

## 2. Escala e corpo de referência

| Item | Decisão | Origem |
|---|---|---|
| Unidades | 1 unidade do Blender = 1 m | Padrão |
| Corpo de referência | `A3_character_example.p3d` (Arma 3 Samples), LOD 0, importado pelo leitor MLOD (sem os proxies) | ✅ Oficial |
| Linha da cabeça | Boné oficial `A3_headgear_example.p3d`, feito para a cabeça oficial: meia-largura 0,087 m, meia-profundidade 0,099 m, centro y = −0,014, topo da cabeça z ≈ 0,826 | ✅ Medido (fatias de 1 cm) |
| Cabeça | A cabeça oficial é um *proxy* do jogo e **não vem no Samples**. As imagens usam uma **cabeça aproximada** (elipsoide entre a linha do boné e o pescoço oficial), só para apresentação | ⚠️ Aproximação |
| Conversão de eixos `.p3d` → Blender | (x, y, z) → (x, z, y): cima = +Z; frente −Z → −Y; esquerda do personagem = +X | ✅ Verificado (dedos do pé, mãos) |
| Espaço do modelo | Coordenadas do personagem (origem cerca de 1 m acima do chão), **como o item de cabeça oficial** | ✅ |

## 3. Medidas do blockout

A largura da base da ficha (0,180 m) não cabia na cabeça oficial com parede e folga (0,087 + 0,004 + 0,002 = 0,093 de meia-largura). **Todas as proporções da ficha foram escaladas em k = 1,0317**, mantendo a forma.

| Medida | Ficha (base 0,180) | Blockout |
|---|---:|---:|
| Altura | 0,200 | **0,206** |
| Base (largura × profundidade) | 0,180 × (suposta) | **0,186 × 0,210** |
| Topo (largura × profundidade) | 0,243 × (suposta) | **0,251 × 0,283** |
| Faixa envernizada | 0,025 | 0,026 |
| Debrum do topo | 0,010 | 0,010 |
| Cocar (raio, altura do centro) | 0,022 / 0,175 | 0,023 / 0,181 |
| Presilha (largura, até) | 0,014 / desce a 0,125 | 0,014 / 0,129 |
| Cifra (placeholder) | 0,081 × 0,077, centro 0,081 | 0,084 × 0,079, centro 0,084 |
| Botões laterais | r 0,007, z 0,012 | r 0,007, z 0,012, a ±80° da frente |

Posição: centro da base em (0; −0,014; 0,714) no espaço do personagem, com **inclinação de 8°** (atrás mais baixo). O teto interno fica em z ≈ 0,914, acima do topo da cabeça (0,826).

## 4. Suposições (sem vista lateral, traseira ou superior da peça real)

| Suposição | Valor | Como confirmar |
|---|---|---|
| Profundidade = 1,13 × largura | Base 0,210, topo 0,283 | Foto lateral |
| Pala: comprimento e ângulo | 0,068 m, 55° para baixo (reproduz a altura projetada da R2, ~0,06 m) | Foto lateral |
| Inclinação na cabeça | 8° | Teste no jogo (G6) |
| Copa | Plana | Foto superior |

## 5. Verificação da silhueta

- **Vistas ortográficas** (`blockout_vistas_ortograficas.png`): frente, lado, costas, topo.
- **Comparação com R2** (`blockout_comparacao_foto_R2.png`): foto e blockout na mesma escala (m/px), alinhados pela base. A altura total, a largura da base e a largura do topo coincidem nas linhas de referência. A faixa branca e o pompom da foto **foram excluídos de propósito** (decisão F2–F4).
- **Encaixe** (`blockout_encaixe_lado.png`, `blockout_encaixe_frente.png`): barretina translúcida sobre o boné oficial (vermelho), mostrando que a abertura envolve a linha da cabeça oficial.

Ressalvas: a foto tem perspectiva e cerca de 3° de inclinação; a comparação serve para proporções, não para medidas milimétricas.

## 6. O que o blockout NÃO contém (por regra da Fase 3)

- Sem UV e sem texturas; as cores lisas servem só para identificar as peças.
- A cifra FWR é um **retângulo provisório**; as letras em relevo entram na Fase 4.
- **Jugular ausente**: depende da cabeça real, que não está disponível como malha. Opções para a Fase 4: (a) jugular sob o queixo, ajustada e testada no jogo; (b) jugular recolhida sobre a pala, que não depende da cabeça.
- Sem LODs, seleções ou pesos (Fase 7).

## 7. Contagem

10 peças, **2.112 triângulos**, todas fechadas (manifold), normais recalculadas para fora. Para comparação, o LOD 0 do boné oficial tem 400 faces; o orçamento de produção será revisto na Fase 4.

## 8. Pendências para aprovar

1. Silhueta e proporções.
2. Posição na cabeça (altura e inclinação de 8°).
3. Pala (comprimento e ângulo).
4. Jugular: sob o queixo ou recolhida.
