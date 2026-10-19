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
