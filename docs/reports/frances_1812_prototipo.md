# Protótipo francês 1812: uniforme, correame, mochila e addon de teste

2026-10-12. Pedidos do usuário: *"cria as roupas francesas baseadas na quela epoca"* e *"cria os coletes e mochilas dos franceses"*.

Ficha: `docs/specs/uniforme_frances_infantaria_1812.md`.

> As decisões F1–F8 da ficha **ainda não foram aprovadas**. Usei as respostas recomendadas na própria ficha:
> - F1: fuzileiro de linha, casaca de 1812 de abas curtas;
> - F2: calças brancas;
> - F3: abas curtas;
> - F4: placa de águia sobre semicírculo;
> - F8: nomes técnicos.
>
> Se alguma resposta for outra, o que muda é o parâmetro do script, não o trabalho todo.

## 1. Uniforme (`HCL_U_Fr1812_01_LOD0`)

Script: `source/scripts/build_uniforme_fr.py`. A casaca francesa sai da malha prussiana de produção, **já com a gola v2** (`gola_pruss_v2.md`). Assim, os pesos e o encaixe da gola valem igual.

| Peça | O que foi feito |
|---|---|
| Abas | Encurtadas de 0,70 m para **0,907 m** de altura da barra. Mantêm a mesma folga sobre a calça (mín. 4 mm, máx. 25 mm), com o deslocamento suavizado. Não há espinhos na abertura de trás |
| Peito | 14 botões prussianos tirados. **Lapelas** E e D novas (material `HCL_la_vermelha`, área própria na UV), de 1,135 a 1,497 m, com 7,2 a 8,2 cm de largura. 7 botões em cada uma |
| Gola, punhos, platinas, calça, polainas | Iguais aos da prussiana |

- Tamanho: 6.758 vértices e 12.448 triângulos. Nenhum canto da UV de outra peça cai na área das lapelas.
- **Cores F01** (`source/textures/hcl_uniforme_fr/variantes_fr.json`):
  - casaca azul imperial;
  - gola e punhos vermelhos, com debrum branco;
  - lapelas brancas com debrum vermelho;
  - viradas das abas brancas;
  - platinas azuis com borda vermelha;
  - botões de latão;
  - calça branca e polainas pretas.
- **🔶 Pala do punho:** branca com debrum vermelho, mas a do mod não dá para ler (ficha F, 4).
- Texturas (2048 px): `hcl_u_fr1812_v01_co`, `hcl_u_fr1812_nohq`, `hcl_u_fr1812_smdi`. Geradas por `generate_uniform_textures_v2.py` com `obj=` e `mapas=` franceses e com a regra nova das lapelas.

## 2. Correame e mochila

Script: `build_equipamento_producao.py nacao=fr`. Arquivo: `source/models/accessories/hcl_equipamento_fr/hcl_equipamento_fr_LOD0.blend`.

### Correame (`HCL_V_Fr1812_Correame_LOD0`, 3.176 triângulos)

- Cartucheira atrás, com a placa de latão, pendurada na bandoleira do ombro esquerdo.
- **Boldrié** do ombro direito ao quadril esquerdo. Leva a bainha da baioneta, com o passador.
- **Sem cinturão:** segue a ficha (§6), com dois boldriés cruzados no peito no lugar do cinturão + bandoleira prussianos 🔶.
- O sabre-briquet que a ficha cita no boldrié **não foi modelado**: só a baioneta.

### Mochila (`HCL_B_Fr1812_Havresac_LOD0`, 3.776 triângulos)

- Havresac de 0,36 × 0,32 × 0,125 m, com a tampa de pele de bezerro.
- Capote enrolado de 0,46 m em cima, preso por 3 correias.
- Duas correias de ombro.

### Pontos 🔶

São premissas minhas, a confirmar:
- o boldrié passa **por baixo** da bandoleira da cartucheira;
- as medidas do havresac;
- a cor do capote, bege-acinzentado.

### Verificações

| Verificação | Resultado |
|---|---|
| Vértices do correame por dentro do uniforme | 6, até 3,5 mm (2 do boldrié perto da gola, lado direito) |
| Vértices da mochila por dentro do uniforme | 0 |

Texturas (2048 px): `hcl_v_fr1812_correame_{co,nohq,smdi}` e `hcl_b_fr1812_havresac_{co,nohq,smdi}`, em `source/textures/hcl_equipamento_fr/`.

## 3. Pesos e teste de movimentos

`teste_movimentos.py nacao=fr` grava `source/models/pesos/hcl_fr_pesos.blend`. Log: `work/teste_movimentos_fr.log`.

| Item | Pesos |
|---|---|
| Uniforme | Os mesmos 62 grupos da Prússia. As lapelas seguem o casaco |
| Correame | Pesos copiados da casaca. A bainha é rígida |
| Mochila | Corpo rígido no tronco. As correias de ombro seguem a casaca |

**Cabeça do jogo × gola/casaco/platinas** (pares de faces): iguais aos da Prússia, porque a gola é a mesma.

| Pose | Pares |
|---|---:|
| Repouso | 2 |
| Em pé, agachado | 4 |
| Sentado mirando | 7 |
| Ajoelhado, deitado | 9–10 |
| Binóculo | 52 |
| Sentado | 74 |
| Morte sentado | 116 |

**Cruzamentos novos que vale olhar no jogo:**

| Peças | Pares | Onde |
|---|---:|---|
| Aba esquerda × boldrié | 20 em pé, **69 agachado** | A bainha pendurada sobre a aba esquerda |
| Gola × bandoleira e boldrié | 16 em pé, **32 deitado** | Nas duas correias, rente ao pé da gola |
| Correame × correias da mochila | 48–176 | Correias cruzando no ombro esquerdo, como na Prússia |

## 4. Addon de teste `hcl_fr`

Montado no mesmo padrão do prussiano, sobre os modelos oficiais dos Samples (`Test_Character_01`).

### Scripts

| Script | Função |
|---|---|
| `p3d_build_common.py` | Funções de montagem de LOD copiadas de `build_p3d_pruss.py`, que não foi mexido |
| `build_p3d_fr.py` | Os P3D |
| `gen_config_fr.py` | `config.cpp`, `model.cfg` e os 9 `.rvmat` |
| `convert_fr_paa.ps1` | As 27 texturas para PAA |
| `build_mod_fr.ps1` | Binarize, CfgConvert e FileBank |

### Conteúdo (prefixo `hcl\hcl_fr`)

| Classe | Tipo | Modelo |
|---|---|---|
| `HCL_U_Fr1812_F01` | Uniforme (Arsenal) | `hcl_u_fr1812.p3d` |
| `HCL_Fr1812_Soldado_F01` | Soldado (escopo 1, só para vestir o uniforme) | idem |
| `HCL_H_Fr1812_Fuzileiro_1aComp` | Barretina | `hcl_h_fr_fuzileiro_1a_comp.p3d` |
| `HCL_H_Fr1812_Granadeiro_Gala`, `_Granadeiro_Campanha` | Barretinas | `hcl_h_fr_granadeiro_{gala,campanha}.p3d` |
| `HCL_H_Fr1812_Voltigeur_Gala`, `_Voltigeur_Campanha` | Barretinas | `hcl_h_fr_voltigeur_{gala,campanha}.p3d` |
| `HCL_H_Fr1812_Oficial_Coronel` | Barretina | `hcl_h_fr_oficial_coronel.p3d` |
| `HCL_V_Fr1812_Correame` | Colete | `hcl_v_fr1812_correame.p3d` |
| `HCL_B_Fr1812_Havresac` | Mochila | `hcl_b_fr1812_havresac.p3d` |

### Montagem (executada em 2026-10-12, 15:14)

- **PAA:** 27 de 27 convertidas, formato certo em todas (`_nohq` DXT5, as outras DXT1).
- **Binarize:** saída 0. Os 9 modelos binarizados têm o esqueleto `OFP2_ManSkeleton`.
  - Os 3 avisos "Cannot load material" são materiais do próprio jogo (`a3\...`), que não estão no disco. São os mesmos 3 da montagem prussiana.
- **CfgConvert:** `config.bin` e os 9 materiais com saída 0.
- **PBO:** `release/@Historical_Clothing/Addons/hcl_fr.pbo`, 44.207.766 bytes, ao lado do `hcl_pruss.pbo`, que não foi tocado.
- **`pbo_verify`:**
  - prefixo `hcl\hcl_fr`, 46 arquivos;
  - nenhum arquivo de fonte dentro;
  - 45 referências internas, **nenhuma faltando**.

  O `pbo_verify.py` agora usa o prefixo do próprio PBO; antes procurava só `hcl\hcl_pruss`. Rodado de novo no prussiano: 67 referências, nenhuma faltando, igual a antes.

**Não visto no jogo.** O addon foi compilado, mas não carregado no Arma 3.

## 5. Imagens

`docs/reports/img/soldado_fr/`, feitas com a cabeça do jogo (`bust.p3d`, cor de pele lisa):

| Arquivo | Vista |
|---|---|
| `soldado_fr_fila_frente.png` | 3 soldados com correame e mochila: voltigeur de campanha, fuzileiro, granadeiro de gala |
| `soldado_fr_fila_costas.png` | Os mesmos de costas: havresac, capote, cartucheira |
| `soldado_fr_busto_tres_quartos.png` | Fuzileiro de perto: gola, lapelas, correias, barretina |
| `soldado_fr_busto_lado.png` | Fuzileiro de lado: gola, jugular, mochila |

Outras:
- `docs/reports/img/uniforme_fr/` (`clay_*`, `textura_*`);
- `docs/reports/img/equipamento_fr/` (`equip_producao_*`, `textura_*`);
- `docs/reports/img/barretina_fr/textura_fr_*`.

Script das imagens: `source/scripts/render_soldado_fr.py`.

## 6. Pontos a observar no jogo

1. Bainha e boldrié atravessando a aba esquerda ao agachar.
2. Bandoleira e boldrié rentes ao pé da gola (deitado).
3. A barretina na cabeça do jogo cobre a testa até a sobrancelha. A pala faz sombra nos olhos (imagens 3/4 e lado). Foi ajustada pela cabeça aproximada, como a prussiana.
4. Plumets: cada pena tem frente e verso, mas o jogo desenha só um lado de cada face. Conferir se não somem de algum ângulo.

## 7. Pendências do usuário

- Aprovar ou mudar F1–F8 (`uniforme_frances_infantaria_1812.md` §10) e B1–B6 (`barretina_francesa_1812.md`).
- As premissas 🔶 do correame e da mochila (§2).
- O teste no jogo.

---

## 8. Atualização de 2026-10-12, noite: mais regimentos, inverno e barretinas da época

Pedidos:
- *"adiciona mais regimentos a franca e as versoes de inverno dos uniformes"*;
- *"traz mais realismo a pumlet e as barretinas como se fossem na quela epoca"*.

Ficha: `uniforme_frances_infantaria_1812.md` §11. As decisões F9–F14 ainda não foram aprovadas.

### 8.1 Casacas F02–F04

Mesma malha da F01; só a textura `_co` muda. As cores foram lidas nos atlas do mod (§11.1 da ficha). Em nenhum caso o mod diz a unidade, por isso os nomes são técnicos.

| Classe | Aparência | Atlas |
|---|---|---|
| `HCL_U_Fr1812_F02` | Azul; lapelas, gola e punhos pretos com debrum vermelho; viradas vermelhas | `FranceINF_2` c5 r0 |
| `HCL_U_Fr1812_F03` | Casaca amarela; lapelas, gola, punhos e viradas vermelhos | `FranceINF_3` c4 r0 |
| `HCL_U_Fr1812_F04` | Casaca vermelha; lapelas, gola, punhos e viradas amarelos | `FranceINF_3` c5 r0 |

### 8.2 Inverno: capote (`build_capote_fr.py`)

Sai da casaca de 1812. Ficam o corpo, as mangas, os punhos, a gola v2, as platinas, a calça, as polainas e as mãos.

Mudanças:
- **Removidos:** abas, lapelas e 16 botões.
- **Saia:** duas metades, a esquerda por cima da direita, da cintura (1,15 m, por cima da borda da casaca) até 0,46 m.
  - Cada metade tem pano, forro a 2,5 mm e faixas de borda.
  - A saia cai do assento sem estreitar e é convexa como um pano pendurado.
  - Folga sobre a calça: 12 mm na cintura, 40 mm na barra.
- **Botões:** duas fileiras de 7 no peito.
- **UV:** reempacotada, com textura própria (`hcl_u_fr1812_capote_*`).
- **Pintura:** dobras verticais na saia, poeira, respingos e desgaste na barra (regras novas em `generate_uniform_textures_v2.py`).

**O correame é o mesmo da casaca.** Ele foi conferido contra o capote:
- A saia é puxada para dentro onde passaria por cima da cartucheira e da bainha (53 pontos, até 14,6 mm).
- A bainha da baioneta foi girada 1,5° para fora (`ajustar_bainha_fr.py`, ponta +11,8 mm). Antes ela ficava 6 mm dentro da saia. Na casaca, agora pende um pouco afastada da aba.
- Restam 27 pontos do correame encostados até 2,1 mm no pano: o lado de trás da bainha, um canto da cartucheira e a ponta do boldrié na cintura.
- A cópia anterior está em `hcl_equipamento_fr/_antes_bainha/`.

**Malha:** 7.568 vértices e 14.224 triângulos. Passa do alvo de 12.000 por causa da saia com forro. Nenhum ponto da calça fica fora da saia em repouso.

**Pesos** (`teste_movimentos.py uni= uni_obj=`, `hcl_fr_capote_pesos.blend`):
- a saia herda os pesos do corpo do mesmo lado;
- o peso da canela passa para a coxa, todo acima de 0,60 m e metade na barra;
- a borda da casaca sob a saia acompanha a saia.

Testei três versões. Valores máximos: calça ou polaina saindo pela saia / pares de faces cruzando com a saia.

| Pose | Pesos herdados do corpo | Só coxa | **Meio-termo (usado)** |
|---|---|---|---|
| Em pé | 0 mm / 156 | 11,7 mm / 278 | **6,6 mm / 203** |
| Agachado | 34,5 mm / 1.277 | 22,5 mm / 876 | **22,5 mm / 1.022** |
| Sentado | 35,9 mm / 1.506 | 11,8 mm / 1.172 | **11,8 mm / 1.273** |
| Ajoelhado (inventário) | 38,9 mm | 38,9 mm | **38,9 mm** |

Casaco longo em Arma sempre atravessa um pouco quando a perna dobra muito. O joelho no chão empurra a calça pela frente da saia.

**Variantes** (`variantes_capote_fr.json`): W01 capote bege com calça branca, W02 cinza com calça branca, W03 bege com calça azul de campanha, W04 cinza com calça cinza de campanha. Combinações propostas (F11).

### 8.3 Barretinas e plumets "da época"

Detalhes tirados da arte das barretinas do mod (atlas `FranceINF` c3–c4 r4–r5):

| Peça | Antes | Agora |
|---|---|---|
| Placa | Forma simplificada | **Traçada da arte** (`trace_badge.py`): águia coroada sobre semicírculo; nos granadeiros, a versão com duas granadas. O relevo vem da arte, na cor do nosso latão |
| Jugulares | Fita lisa de latão | **15 escamas sobrepostas** sobre correia de couro preto, mais estreitas no queixo |
| Cocar | 3 discos | Os 3 discos, com **presilha** (cinza-clara, como na arte) e botão de latão |
| Rosetas | Disco liso | Disco com a **estrela** da arte |
| Borlas dos cordões (gala) | Cone | Cabeça torneada e **franja** de 18 fios |
| Pompons | Sólido liso | Lã irregular |
| Plumet | v2: lâminas longas em camadas (parecia pinha) | **v3**: 40 camadas de penas curtas e estreitas, deitadas, com as pontas curvadas. A 1ª tentativa, mais aberta, parecia capim e foi descartada |

| Barretina | Triângulos antes | Triângulos agora |
|---|---:|---:|
| Fuzileiro | 4.520 | 6.436 |
| Granadeiro de gala | 9.982 | 13.656 |
| Granadeiro de campanha | 4.680 | 7.086 |
| Voltigeur de gala | 9.982 | 13.230 |
| Voltigeur de campanha | 4.680 | 6.660 |
| Coronel | 9.462 | 12.390 |

As de gala estão pesadas para um item de cabeça. Um LOD mais leve fica para a produção.

### 8.4 Addon `hcl_fr` remontado (2026-10-12, 16:15)

- **Conteúdo novo:**
  - uniformes `HCL_U_Fr1812_F02`–`F04` e `HCL_U_Fr1812_Capote_W01`–`W04`;
  - soldados (escopo 1) correspondentes;
  - modelo `hcl_u_fr1812_capote.p3d`.
- **PAA:** 36 de 36 com cabeçalho certo.
- **Binarize:** 10 de 10 modelos com esqueleto; avisos só dos 3 materiais do jogo.
- **Config:** `CfgConvert` 0; 15 itens, 8 soldados, 1 mochila.
- **PBO:** `hcl_fr.pbo` de 61,2 MB. `pbo_verify`: 57 arquivos, sem fontes, 56 referências, nenhuma faltando.

**Não visto no jogo.**

### 8.5 Imagens novas

`docs/reports/img/soldado_fr/`:
- `regimentos_fr_*`: F01–F04 com barretinas de granadeiro, fuzileiro e voltigeur;
- `inverno_fr_*`: W01–W04.

`docs/reports/img/barretina_fr/`: `textura_fr_*` e `blockout_fr_*`, refeitas com placa, escamas e plumet v3.

### 8.6 A observar no jogo

1. A saia do capote atravessada pelos joelhos ao agachar e ajoelhar (até 2–4 cm).
2. A bainha, agora mais afastada da aba na casaca de 1812.
3. Peso das barretinas de gala (13 mil triângulos).
4. O plumet v3 nas distâncias de jogo.

---

## 9. Atualização de 2026-10-12, fim da tarde: casacas de granadeiro e voltigeur (F12)

Pedido: *"continua ... a criação de mais roupas da França"*, depois *"deixa mais perfeito"* e *"atualiza e envia o mod"*. A decisão F12 **não foi aprovada**; usei a recomendação da ficha (🔶).

### 9.1 Malha: `build_casaca_elite_fr.py` → `HCL_U_Fr1812_Elite_LOD0`

Arquivo: `source/models/coats/hcl_uniforme_fr/hcl_uniforme_fr_elite_LOD0.blend`. Parte da casaca F01; a platina vira a **língua** da dragona. Em cada ombro:

| Peça | Como é feita |
|---|---|
| Corpo (`dragona_corpo_*`) | Placa rígida: superfície alisada sobre o ombro, sempre ≥ 3,5 mm acima do pano/língua (folga média 4,2 mm). A ponta da língua sob ela foi baixada 2,5 mm (4 vértices, escondidos) |
| Meia-lua (`dragona_meialua_*`) | Rolo acolchoado de 3,8 a 7,5 mm de raio, 22 × 8 faces |
| Franja (`dragona_franja_*`) | 32 cordões de 5,4 mm × 8 cm (±5%), caindo por gravidade sobre a manga, cada um com leve variação; cortina curta sob as raízes |

Medidas 🔶 (sem fonte lida). Malha: 9.002 vértices, **16.414 triângulos** (fuzileiro: 12.448). Nenhum vértice da franja ou da meia-lua dentro do pano.

Tentativas descartadas (renders no scratch): corpo copiando o ombro (amassados na ponta da língua); ajuste cúbico (flutuava até 17 mm); franja de 26 cordões (rala); cortina longa (aparecia como lençol escuro).

### 9.2 Texturas (`generate_uniform_textures_v2.py`, regras novas) e variantes

- Cordões com torção de dois cabos, cor variando por cordão; meia-lua com pespontos; **passante** atravessado na língua a 2/3 do comprimento (como na arte do mod).
- **Viradas por fora das abas** (chave `viras_externas`): duas cunhas brancas por aba, estreitas na cintura e unidas na barra, debruadas, bordas suavizadas. Só as variantes de elite usam por enquanto (F01–F04 não foram repintadas).
- **Ornamentos** traçados da arte do mod (`tracar_ornamentos_fr.py`, só a forma; cor nossa): granada (c0 r3) e corneta (c2 r3), em `source/textures/hcl_uniforme_fr/ornamentos/`. Quatro por casaca, um em cada cunha, como no atlas 🎮.

`variantes_fr_elite.json`:

| Classe | Aparência | Atlas |
|---|---|---|
| `HCL_U_Fr1812_Granadeiro_F01` | F01 + dragonas vermelhas (língua com borda e passante amarelos), granadas vermelhas | `FranceINF` c0 r3 |
| `HCL_U_Fr1812_Voltigeur_F01` | F01 + gola camurça com debrum vermelho, dragonas verdes com meia-lua e passante amarelos, cornetas amarelas | `FranceINF` c2 r3 |

Texturas 2048 px em `source/textures/hcl_uniforme_fr_elite/`.

### 9.3 Pesos (`teste_movimentos.py`, `hcl_fr_elite_pesos.blend`)

- Corpo e meia-lua: **um só conjunto rígido** (média do ombro sob eles: LeftArm 0,72, LeftShoulder 0,24). Na 1ª versão cada ponto seguia o pano sob ele e o corpo amassava com o braço erguido (arestas até 3% do tamanho).
- Franja: rígida na raiz, passa a seguir a manga em 4 cm.
- Resultado nas 8 animações: nenhuma aresta esticada fora do limite. Restam: franja tocando a manga em poses extremas (2 vértices, até 6 mm), cordões cruzando entre si (até 51 pares), a borda do corpo se afastando até 13 mm da manga com o braço erguido. Log: `work/teste_movimentos_fr_elite.log`.

### 9.4 Addon `hcl_fr` remontado (2026-10-12, 17:18)

- Modelo novo `hcl_u_fr1812_elite.p3d` (+ classe no `model.cfg`, material próprio), soldados `HCL_Fr1812_Soldado_Granadeiro_F01` / `_Voltigeur_F01` (escopo 1).
- PAA: 40 de 40 com cabeçalho certo. Binarize: 11 de 11 modelos com esqueleto; avisos só dos 3 materiais do jogo. CfgConvert 0 (17 itens, 10 soldados).
- PBO `release/@Historical_Clothing/Addons/hcl_fr.pbo`, 68,7 MB; `pbo_verify`: 62 referências, nenhuma faltando.

**Não visto no jogo.**

Imagens: `docs/reports/img/soldado_fr/elite_fr_*` (fila de frente e costas, busto, ombro).

### 9.5 A observar no jogo

1. Franja e braço erguido (mirar, binóculo, deitado).
2. As viradas por trás e os ornamentos.
3. Peso da casaca de elite (16,4 mil triângulos, só Res 1).

### 9.6 Ainda não feito

- Barretinas mais realistas com mais texturas (item 2 do pedido).
- Viradas externas em F01–F04 (precisa repintar; pede sua confirmação).
- Corte de abas longas (F14) e casaca verde.
