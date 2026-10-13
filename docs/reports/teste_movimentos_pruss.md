# Teste de Movimentos (fora do jogo): Uniforme, Barretinas, Correame e Mochila Prussianos

Data: 2026-10-10.

Pedidos do usuário:
- *"faz um teste final nos modelos da Prússia, coloca eles para testar os movimentos do ARMA 3"*;
- *"adiciona o colete e mochila com todas as roupas e barretinas em animações diferentes"*.

**Estado: executado no Blender. NÃO é um teste dentro do ARMA 3** (§8).

Legenda: ✅ verificado · 🔶 provável ou com ressalva · ❓ não verificado

---

## 1. O que foi testado

| Item | Versão usada | Estado do item no pipeline |
|---|---|---|
| Uniforme | `HCL_U_Pruss1813_01_LOD0`; as 8 variantes de cor usam a mesma malha | Fases 4–6, aguarda aprovação |
| Barretina | As 3 malhas (FWR, águia e estrela) e as 6 texturas | Fase 6, aguarda aprovação |
| Correame (colete) | `HCL_V_Pruss1813_Correame_blockout` | **Blockout** (Fase 3; aguarda E1–E6) |
| Mochila | `HCL_B_Pruss1813_Tornister_blockout` | **Blockout** (Fase 3) |

## 2. Animações: oficiais, dos Arma 3 Samples (só leitura)

| ID | Animação | Arquivo | Quadros avaliados |
|---|---|---|---|
| `em_pe` | Em pé, fuzil erguido | `Test_Anims\AmovPercMstpSrasWrflDnon.rtm` | 3 |
| `agachado` | Ajoelhado num joelho, fuzil erguido | `Test_Anims\AmovPknlMstpSrasWrflDnon.rtm` | 2 |
| `deitado` | Deitado, fuzil erguido | `Test_Anims\AmovPpneMstpSrasWrflDnon.rtm` | 11 |
| `inventario` | Ajoelhado, mãos no chão | `Test_Anims\AinvPknlMstpSlayWrflDnon.rtm` | 2 |
| `sentado` | Passageiro sentado (FFV) | `Test_FFV_Poses_F\Anim\ffv_01_idle1.rtm` | 26 (1 a cada 5) |
| `sentado_mira` | Sentado mirando (FFV) | `…\ffv_01_aim1.rtm` | 17 (1 a cada 2) |
| `morte` | Morte sentado (FFV) | `…\ffv_01_die.rtm` | 26 |
| `binoculo` | Sentado com binóculo (FFV) | `…\ffv_01_aim_binoc.rtm` | 17 (1 a cada 2) |

**Não testados:** correr, andar e as outras animações do jogo. As do jogo (`anims_f*.pbo`) estão no formato binarizado `BMTR`, que não foi lido. Só os Samples trazem animações no formato aberto (`RTM_0101`).

## 3. Como foi feito

### 3.1 Leitura das animações

`source/scripts/rtm_read.py` lê o formato aberto. Verificações:

| Verificação | Resultado |
|---|---|
| Formato | ✅ O tamanho de cada arquivo bate exatamente: 28 + 32 × ossos + quadros × (4 + 80 × ossos) |
| Convenção da matriz | ✅ Os 9 primeiros números são os eixos x, y e z do osso (colunas da rotação); os 3 últimos, a translação. Assim, `ponto_na_pose = R · ponto_no_repouso + t` |
| Prova da convenção | ✅ Em cada junta, pai e filho levam o pivô (de `ManSkeleton_Pivots.p3d`) ao mesmo lugar: diferença mediana de 0,7 mm, máxima de 5,4 mm. Na outra ordem a diferença passa de 1 m |
| Prova no corpo | ✅ O corpo oficial (`A3_character_example.p3d`) posado com os próprios pesos fica com os pés no chão (altura mínima 0,000 m em pé). Ajoelhado, o joelho direito toca o chão |
| Ossos do rosto | ✅ Nas animações do corpo, todos os ossos `Face_*` e `Eye*` vêm com a matriz identidade (o rosto é animado à parte). Por isso seguem o osso `Head` |

### 3.2 Pesos

É a **primeira versão** dos pesos da roupa, que pertencem à Fase 7.

| Peça | Regra |
|---|---|
| Roupa | Passados do corpo oficial pela superfície mais próxima (interpolados na face). Peças do lado esquerdo só recebem pesos do lado esquerdo do corpo, e vice-versa. Depois, 2 passadas de suavização e no máximo **4 ossos por ponto**, com soma 1 |
| Abas | Misturadas com a pelve conforme descem: 0% na cintura, 50% na barra. Assim não seguem uma coxa sozinha. Comparação com e sem a mistura no §6 |
| Botões | Copiam os pesos do pano onde estão pregados |
| Mãos | Pesos oficiais do template, sem mudança |
| Correame | Copia os pesos da casaca logo abaixo (corpo, gola e platinas; nunca das abas ou das pernas) |
| Mochila | Corpo rígido na coluna (`Spine` 0,08, `Spine1` 0,38, `Spine2` 0,30, `Spine3` 0,23). As **correias de ombro** passam para os pesos da casaca conforme se afastam da mochila: 0 junto a ela, total a partir de 6 cm (512 pontos). 🔶 Não foi verificado como as mochilas oficiais são ponderadas |
| Barretina | Rígida no osso `Head` |

**Resultado:** 62 ossos usados, no máximo 4 por ponto, soma 1 em todos.

Mistura de ossos: 🔶 linear, com até 4 ossos por ponto, que é o limite do formato. O cálculo exato do motor não foi verificado.

### 3.3 Medidas, sempre comparadas com o repouso

1. **Camada atravessando:** um ponto da camada de baixo, que estava coberto no repouso, aparece do lado de fora da camada de cima. Mede-se com raios para fora e para dentro, o que vale também para peças com forro. Só conta o que passa de 2 mm.
2. **Peças se separando:** pontos que se tocavam no repouso (até 5 mm, em peças diferentes) e se afastam mais de 5 mm. Os pares esquerda × direita ficam de fora, porque pernas e abas abrem naturalmente.
3. **Cruzamentos novos:** pares de faces que se cruzam na pose e não se cruzavam no repouso. Ao lado, o mesmo teste no corpo oficial, entre as mesmas regiões. Se o corpo também encosta, **é a própria animação que encosta uma parte na outra**.
4. **Esticamento:** comprimento das arestas na pose dividido pelo do repouso. A referência é o corpo oficial, que também estica nas juntas (7–10% das arestas fora de 0,7–1,3×).
5. **Cabeça e barretina:**
   - cabeça oficial de referência (crânio e rosto de `TemplateRTM\Male.p3d`) contra a gola;
   - as 3 malhas de barretina contra o uniforme, o correame e a mochila.

## 4. Resultados

Saída completa: `docs/reports/img/movimentos/teste_movimentos_pelve_output.txt`.

### 4.1 O que passou

| Verificação | Resultado |
|---|---|
| **Barretina (FWR, águia, estrela) × uniforme, correame e mochila** | ✅ **0 contatos nas 8 animações**, incluindo deitado com a cabeça erguida |
| Calça saindo por baixo das abas | ✅ No máximo 2 pontos a 3 mm (deitado) |
| Casaca × gola | ✅ No máximo 8 pontos a 4–6 mm (borda da gola) |
| Correame e casaca × mochila | ✅ Até 7 pontos a 5,3 mm (deitado); nas outras poses, 0 |
| Platina × correame | ✅ 1 ponto a 2,6 mm (deitado) |

### 4.2 Problemas encontrados, por gravidade

| # | Problema | Onde | Tamanho | Origem |
|---|---|---|---|---|
| P1 | Mãos saindo pelo punho direito | Sentado, binóculo | 7 de 64 pontos, até 21 mm | O pulso dobra mais que a abertura do punho |
| P2 | Casaca aparecendo pela manga na axila | Todas | 1–2 pontos, até 34 mm; 31–56 pares de faces | **Da roupa:** no corpo oficial a axila não se cruza (0 pares em várias poses) |
| P3 | Abas × cartucheira e bainha | Ajoelhado (90 pares), outras (24–42) | Contato | As abas seguem metade a pelve, e o correame segue a casaca |
| P4 | Correias da mochila × correame no peito | Deitado (118 pares), outras (27–50) | Contato | As duas correias se cruzam no peito |
| P5 | Manga × mochila | Sentado, mirando, morte, binóculo | 30–44 pares | Em parte é a pose: o corpo oficial também encosta o braço no tronco |
| P6 | Queixo na gola alta | Ajoelhado (26 pares), sentado (31), morte (64) | Contato | Gola alta + cabeça baixa: esperado num uniforme de 1813 🔶 |
| P7 | Topo da polaina abrindo na calça atrás do joelho | Agachado, sentado | 3 pontos, 8–10 mm | Nas imagens sentadas, a borda de cima da polaina fica **serrilhada** quando o joelho dobra 90°: a calça cruza a borda. É mais visível do que o número sugere |
| P8 | Correame se afastando dos botões | Várias | Até 12 mm | O cinturão passa sobre os botões |
| P9 | Calça e abas esticando na virilha | Agachado, sentado | Até 3× nas arestas curtas | O corpo oficial estica igual (até 2,2× em 1% das arestas) |
| — | Aba "descolando" da coxa | Sentado | Até 8 cm | **Não é defeito:** o pano fica pendurado quando a coxa sobe |
| — | Dedos da mão se cruzando | Todas | — | **Da malha oficial do template** fechando na empunhadura |

## 5. Defeitos achados e corrigidos durante o teste

| Defeito | Correção |
|---|---|
| Botões das abas soltos no ar (seguiam a coxa, e as abas a pelve) | Botões copiam os pesos do pano |
| Pontos da perna e da aba esquerdas com pesos da perna direita (cruzavam a linha do meio na virilha e na fenda) | Transferência só do mesmo lado do corpo |
| Correias da mochila atravessadas pela casaca, platinas e correame em até 50 mm (mochila toda rígida) | Correias seguem a casaca, com transição suave |
| Pecinhas cor de pele entre as pernas, e depois em volta da cabeça | Eram da cabeça de referência, não da roupa: rosto com matriz identidade, mais triângulos auxiliares soltos. A cabeça segue o osso `Head` e só as partes grandes são usadas |

## 6. Comparação dos pesos das abas

Saída: `docs/reports/teste_movimentos_abas_sem_pelve_output.txt`.

Mesma versão final do teste, com o equipamento; muda só a regra das abas.

| Medida | Abas só com os pesos da coxa | Abas misturadas com a pelve (escolhido) |
|---|---|---|
| Ajoelhado: esticamento máximo da aba | 4,82× | 2,98× |
| Sentado: esticamento máximo da aba | 4,39× | 2,67× |
| Inventário: esticamento máximo da aba | 4,68× | 2,84× |
| Inventário: aba × assento da calça | 72 pares | 30 pares |
| Inventário: aba × perna | 52 pares | 40 pares |
| Ajoelhado: aba direita × polaina | 59 pares | 44 pares |

## 7. Imagens

Pasta: `docs/reports/img/movimentos/`.

**Por animação:** `<id>_{3-4,lado,costas}.png`, com:
- a variante V01;
- a barretina FWR;
- o correame e a mochila (blockout);
- a cabeça de referência.

Para cada animação, o quadro mostrado é o pior quadro medido.

**Galeria:** `galeria_frente.png` e `galeria_costas.png`, com as 8 roupas e as 6 barretinas, cada soldado numa animação. A combinação é só para exibição.

| Soldado | Roupa | Barretina | Animação |
|---|---|---|---|
| 1 | V01 | FWR, presilha amarela | Em pé |
| 2 | V02 | FWR, presilha branca | Ajoelhado |
| 3 | V03 | Águia, presilha amarela | Deitado |
| 4 | V04 | Águia, presilha branca | Inventário |
| 5 | V05 | Estrela prateada | Sentado |
| 6 | V06 | Estrela de latão | Sentado mirando |
| 7 | V07 | Águia, presilha amarela | Morte (último quadro) |
| 8 | V08 | Estrela prateada | Binóculo |

Os sentados ficam sobre um caixote no lugar do banco do veículo.

## 8. O que este teste NÃO prova

- **Nada foi testado dentro do ARMA 3.** Ainda faltam:
  - converter para `.p3d` no Object Builder, com LODs, seleções, pesos e `model.cfg` (Fase 7);
  - o config (Fase 8);
  - o PBO e o teste no jogo (Fase 9).
- Correr, andar, rolar e mirar em pé com troca de arma não foram testados (§2).
- A cabeça do jogo vem da identidade do personagem. Aqui foi usada a cabeça dos Samples, que não é a mesma.
  - A barretina já cruza essa cabeça no repouso (148 pares). Ela foi ajustada ao template oficial de item de cabeça, e não a esta cabeça.
  - Isso precisa ser conferido no jogo (G6).
- O correame e a mochila são blockout. As medidas deles mostram onde cuidar na Fase 4, não o resultado final.

## 9. Recomendações para as próximas fases

| Problema | Correção proposta | Fase |
|---|---|---|
| P1 | Abrir um pouco o punho; ou passar parte do peso do punho para `ForeArmRoll` e `Hand` | 7 |
| P2 | Prender a cava da manga à casaca (uma malha só) ou suavizar os pesos da axila | 7 |
| P3 | Na produção do correame, afastar a cartucheira e a bainha 1–2 cm das abas; ou fazer as abas seguirem mais a pelve | 4 (correame) e 7 |
| P4 | Na produção, passar as correias da mochila **por baixo** do correame no peito, ou abrir 5 mm entre elas | 4 (equipamento) |
| P6 | Aceitar (é da peça histórica) ou dar ao topo da frente da gola um pouco de peso no `Neck` | 7 |
| P7 | Topo da polaina com os mesmos pesos da calça logo abaixo (copiar, como nos botões), e borda superior um pouco mais aberta | 7 |
| R1 | Unir o assento e as pernas da calça (já previsto) | 7 |

Arquivos do teste:
- `source/scripts/teste_movimentos.py`;
- `source/scripts/rtm_read.py`;
- cena: `docs/reports/img/movimentos/teste_movimentos_pelve.blend`, com os pesos v0 no objeto `HCL_U_Pruss1813_01_LOD0_pesos`.
