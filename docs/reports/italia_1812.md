# Reino da Itália e Reino de Nápoles, c. 1812: addon de teste `hcl_italia`

Data: 2026-10-18. Pedido do usuário: *"lets finish the duchy of warsaw and after start the kingdom of italy and kingdom of naples"*; regra de fontes: *"utilize fontes históricas de museus e documentos"*. Ficha: `docs/specs/aliados_fr_1812.md` §3 (decisão A2: Itália e Nápoles num só PBO, `hcl_italia`).

**Estado:** `hcl_italia.pbo` montado e verificado **fora do jogo** (§5). Nada foi visto no Arma 3.

## 1. Fontes usadas

| Tipo | Fonte | O que deu |
|---|---|---|
| 📜 Historiador da época | A. Zanoli, *Sulla milizia cisalpino-italiana … dal 1796 al 1814* (Milão, 1845; o autor serviu no exército italiano), texto OCR do Internet Archive | Cocar nacional **branco, verde e vermelho**; as pranchas de Artaria (Viena) dedicadas ao ministro Fontanelli |
| 🖼🏛 Imagens de época | Gravuras coloridas de **1812**, filas de soldados por regimento, **coleção Vinkhuijzen, New York Public Library** (via Wikimedia Commons) | Confirmam a tabela de cores para o 3º (tudo vermelho), 4º (lapelas brancas, gola vermelha), 5º (lapelas verdes, gola vermelha), 7º (lapelas brancas, gola verde) e 1º (lapelas vermelhas). Legendas do colecionador → 🔶 |
| 🖼 Imagem de época | *Freiberger Bilderhandschrift* (aquarelas de 1813), via M. Gärtner, *Depesche* 1 (com Boisselier, Brauer, Forthoffer e os acervos de San Martino e de Rastatt) | **7º napolitano**: casaca branca, gola, lapelas, viras e canhões amarelos, botões de latão, barretina com placa em coração, sem cordões, cocar branco com amaranto |
| 🖼 Fim do séc. XIX | R. Knötel, *Uniformenkunde* III/25 (Itália 1812), V/46 e VI/23 (Nápoles 1812), exemplares da coleção Vinkhuijzen | Itália: casacas brancas com distintivos vermelhos, verdes e brancos. Nápoles: 1 escarlate, 2 verde, 3 amarelo, 4 laranja, 5 azul, 6 carmesim (o autor diz "parecem ter sido") |
| 🔶 Secundária | it.wikipedia (Pivka & Chappell, Osprey MAA 43); Schultheis 1996 via miniatures.de | Companhias (pompons verde, azul-celeste, laranja, violeta), granadeiros e voltigeurs; tabela de cores dos 7 regimentos italianos |
| 🎮 Arte do mod | `ItalyINF` e `NaplesINF` c3 r4 (Reto, autorizado) | Placa **losango** com águia (Itália; região idêntica pixel a pixel à do `FranceINF`); **escudo com monograma N** (Nápoles); os cocares do atlas batem com as fontes |

Não lidos: os decretos de uniforme (o *Bollettino delle leggi* italiano e o Decreto 821 napolitano, só citado); a água-tinta de Albrecht Adam na Bibliothèque Marmottan (a ficha não descreve as cores).

## 2. O que entra no primeiro lote

| Peça | Classes | Base |
|---|---|---|
| Casaca branca, Itália, 1º a 7º | `HCL_U_Italia1812_IT01` … `_IT07` | Malha e pesos da casaca francesa (só leitura); cores da tabela, conferidas nas gravuras de 1812 |
| Casaca branca, Nápoles, 1º, 2º, 5º, 7º | `HCL_U_Italia1812_NA01`, `_NA02`, `_NA05`, `_NA07` | *Habit-veste* de lapelas fechadas; tudo na cor distintiva, vivos brancos nos canhões e viras (7º, Freiberg) |
| Elite | `_Granadeiro_IT03`, `_Voltigeur_IT03`, `_Granadeiro_IT05`, `_Voltigeur_IT05`, `_Granadeiro_NA07`, `_Voltigeur_NA07` | Dragonas vermelhas; voltigeur italiano verde com crescente amarelo, napolitano amarelo |
| Barretina italiana | `HCL_H_Italia1812_Shako_Italia_Fuzileiro_1aComp` … `_4aComp`, `..._Voltigeur_Gala` | Cópia da barretina francesa v4 (`blockout_shako_italia.py nacao=italia`): placa losango do mod, cocar vermelho-branco-verde, pompons das 4 companhias; voltigeur com plumet verde de ponta amarela e cordões verdes; sem galões (sem fonte) |
| Barretina napolitana | `..._Shako_Napoles_Fuzileiro_R01`, `_R02`, `_R05`, `_R07`, `..._Voltigeur_Gala` | `nacao=napoles`: escudo com N do mod, cocar branco e amaranto, **sem cordões**; pompom na cor do regimento; voltigeur com plumet amarelo |
| Chapéu de pele | `..._Bonnet_Italia_Granadeiro_Gala`, `_Campanha`; `..._Bonnet_Napoles_Granadeiro_Gala`, `_Campanha` | Cópia do chapéu dos Suíços: Itália com placa de granada, cordões brancos e plumet vermelho; Nápoles com cordões e plumet vermelhos, **sem placa** (a fonte não cita uma) |

Fica para depois: infantaria ligeira italiana (verde), casaca de 1813, regimentos napolitanos 3º, 4º e 6º.

## 3. Problemas achados e corrigidos

1. **Arte da placa apagada** no primeiro bake das barretinas (mesmo caso de Varsóvia): a faixa padrão `arte_faixa=0.05,0.45` está acima dos valores **lineares** da arte. Medida na placa (percentis 2–98 %): Itália 0,006–0,13, Nápoles 0,018–0,13. A cadeia foi interrompida (árvore inteira, nada sobrou) e refeita com `arte_faixa=0.008,0.13` (Itália), `0.018,0.13` (Nápoles) e `arte_escala=2`. Agora a águia e a moldura do losango e o monograma "N" do escudo aparecem em relevo.
2. O Python do Blender no Windows grava os scripts com CRLF; foram normalizados para LF antes do commit.

## 4. Pendências e incertezas

- 🔶 Tabela de cores italiana (Schultheis) confirmada pelas gravuras só nas peças grandes (gola, lapelas); canhões, portinholas e vivos 🔶.
- 🔶 Nápoles 1º, 2º e 5º pela lista de Knötel ("parecem ter sido"); o 4º é amarelo numa prancha e laranja na outra (❓, ficou fora).
- 🔶 Casaca: a malha é a do *habit-veste* de 1812; a Itália só o recebeu em 1813 (na Rússia, o modelo de abas longas).
- 🔶 Chapéu de pele: tampo vermelho com cruz branca herdado do chapéu da Guarda; Nápoles sem placa (fonte não cita).
- A coroa acima do escudo napolitano está recortada no atlas e não foi modelada.

## 5. Montagem e verificação (fora do jogo)

- Casacas: `generate_uniform_textures_v2.py` (sem editar) com os JSONs de `variantes_italia.py`: 11 de linha e 6 de elite. `_nohq`/`_smdi` franceses (mesma UV).
- Barretinas: `blockout_shako_italia.py` (`nacao=italia`, 13,5 mil triângulos no fuzileiro e 25,5 mil no voltigeur; `nacao=napoles`, 13,0 mil e 21,2 mil) e `texturizar_aliados.py`. Chapéus de pele: `blockout_bonnet_italia.py` (46,2 mil / 32,9 mil Itália; 45,9 mil / 32,6 mil Nápoles).
- PAA: 63 de 63 com cabeçalho certo.
- `build_mod_italia.ps1`: Binarize código 0, **16 de 16 modelos com `OFP2_ManSkeleton`**; avisos só dos materiais do jogo (iguais aos da França). `CfgConvert` 0 (config e 16 rvmat). 17 soldados e 31 itens (17 casacas, 14 coberturas de cabeça); `requiredAddons` só `A3_Characters_F`.
- PBO: `release/@Historical_Clothing/Addons/hcl_italia.pbo`, **119,5 MB**, 18/10 às 22:51.
- `pbo_verify.py`: prefixo `hcl\hcl_italia`, **95 referências, nenhuma faltando**.

Imagens (pasta principal, `docs/reports/img/italia/`): `italia_linha_*` (1º, 3º, 4º, 5º e 7º com os pompons das 4 companhias), `italia_elite_*` (granadeiro do 3º, fuzileiro e voltigeur do 5º), `napoles_linha_*` (1º, 2º, 5º, 7º), `napoles_elite_*` (granadeiro, fuzileiro e voltigeur do 7º); `blockout_shako_italia_*`, `blockout_shako_napoles_*`, `blockout_bonnet_italia_*`.

## 6. Lote 2: os regimentos das pranchas 175–204 (pedido: "FAZ ESTES REGIMENTOS")

**Fonte:** aquarelas de 1812 da coleção Vinkhuijzen (NYPL `b14896507-1528310` a `-1528339`), cada uma com a legenda escrita pelo colecionador. Os nomes seguem a legenda e os tons foram lidos na digitalização 🔶. A infantaria ligeira e os voltigeurs de linha também estão em Knötel III/25.

| Prancha (legenda) | O que entrou | Classes |
|---|---|---|
| 192 *Leggiero Infanterie 1° Reg.* | Casaca e calça verde-escuras, **gola e canhões vermelhos**, vivos brancos; carabineiro (dragonas vermelhas) e voltigeur (verdes com crescente amarelo) | `HCL_U_Italia1812_LE01`, `_Carabiniere_LE01`, `_Voltigeur_LE01` |
| 188 *Carabiniere 3° Reg. Leggiero* | **Gola branca** | `_LE03`, `_Carabiniere_LE03` |
| 189 *4° Regiment Leggiero* | **Gola violeta** | `_LE04`, `_Voltigeur_LE04` |
| 186, 187 *Carabiniere / Volteggiatore della fanteria leggiera* (sem número) | **Gola amarela** | `_Carabiniere_LEX`, `_Voltigeur_LEX` |
| 190, 191 *Reggimento Dalmato* | Casaca verde-escura, gola, canhões e viras vermelhos; granadeiro com dragonas vermelhas | `_DAL`, `_Granadeiro_DAL` |
| 185 *Compagnie di riserva della Fanteria di linea* | Casaca verde-escura, gola e canhões vermelhos | `_RES` |
| 184 *Guardia di Milano* | Casaca azul-clara, gola e canhões vermelhos | `_MIL` |
| 182 *Volontario* | Casaca verde-escura, gola e lapelas amarelas | `_VOL` |
| 183 *Bersagliere di Brescia* | Casaca verde-escura, gola e vivos verde-claros, calça cinza | `_BRE` |
| 180 *Reg. Dragoni Regina* | Só a casaca: verde-escura, lapelas e viras **rosa**, botões brancos (sem capacete de dragão) | `_DRA` |
| 181 *Battaglione d'Artiglieria* (legenda lida com dúvida ❓) | Casaca verde-escura, vivos e dragonas vermelhos | `_ART` |
| 193 *Volteggiatore della fanteria di linea* | **Correção:** o voltigeur de linha usava casaca **verde** com gola vermelha (também Knötel: *"Die Voltigeure … waren grün uniformiert"*). Os voltigeurs do 3º e do 5º, que no lote 1 eram brancos, agora são verdes | `_Voltigeur_IT03`, `_Voltigeur_IT05` |
| 195, 203 *6 Reg. Granatiere* / *Zappatore* | Granadeiro do 6º (casaca branca, lapelas verdes, dragonas vermelhas) | `_Granadeiro_IT06` |
| 202, 198, 199 *Lieutenant Linie Infanterie 1° / 4° Regiment*, *Grenadier 5° Regiment* | Casaca do regimento com **dragonas de prata** | `_Oficial_IT01`, `_Oficial_IT04`, `_Oficial_Granadeiro_IT05` |
| 186, 188 | Chapéu de pele do carabineiro de ligeira: **sem placa**, cordões e plumet vermelhos, cocar italiano | `HCL_H_Italia1812_Bonnet_Italia_Carabineiro_Gala` |

**Não feitos, e por quê:**
- 175 *3° Reggimento Cacciatori a Cavallo* e 204 *Treno di bagaglio della Guardia*: a casaca tem alamares no peito, e o pintor de casacas não sabe fazer alamares.
- 200 tambor-mor, 201 coronel a cavalo, 194 capitão com sobrecasaca de campanha: precisam de bicórnio e casaca longa ou sobrecasaca, peças que não existem no projeto.
- Coberturas próprias do Bersaglieri de Brescia (chapéu redondo), da Guarda de Milão, do voluntário, da artilharia e o capacete dos dragões: não foram modeladas. Essas casacas usam as barretinas italianas no Arsenal.

**Montagem e verificação do lote 2 (fora do jogo):** 23 casacas novas ou corrigidas (9 de linha, 14 de elite) e os 5 chapéus de pele refeitos com o do carabineiro. PAA 87/87; Binarize 0, **17 de 17 modelos com `OFP2_ManSkeleton`**; `CfgConvert` 0 (config e 17 rvmat); 38 soldados e 53 itens. PBO `hcl_italia.pbo` de **151,2 MB** (18/10 às 23:51); `pbo_verify`: **121 referências, nenhuma faltando**. Imagens: `italia_ligeira_*`, `italia_corpos_*`, `italia_linha_lote2_*`.
