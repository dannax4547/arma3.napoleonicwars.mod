# Ducado de Varsóvia, regulamento de 1810: addon de teste `hcl_varsovia`

Data: 2026-10-18. Pedidos do usuário: *"continuar os projetos"* e *"utilize fontes históricas de museus e documentos"*. Ficha: `docs/specs/aliados_fr_1812.md` §1.1, §8 (A5).

**Estado:** `hcl_varsovia.pbo` montado e verificado **fora do jogo** (§5). Nada foi visto no Arma 3.

## 1. Fontes usadas

| Tipo | Fonte | O que deu |
|---|---|---|
| 📜 Documento | Regulamento *Przepis ubiorów* de **3/9/1810**, texto em Gembarzewski, *Wojsko polskie. Księstwo Warszawskie 1807–1814* (1905), pp. 48–49, 106–109; resumo de Żygulski e Wielecki, *Polski mundur wojskowy* (1988), pp. 57–62 | Cores da kurtka, botões numerados, dragonas por companhia, a **czapka rogata** (22,5 cm, lados do topo 25 cm, águia branca sobre placa amarela com número, cocar branco, cordões brancos, pompom preto / penacho amarelo-verde), o chapéu de pele dos granadeiros |
| 🏛 Museu | Barretina do 2º Regimento no **Museu Nacional de Cracóvia**; catálogo *Militaria Księstwa Warszawskiego* (MNK, 1959) | Citada; a ficha do objeto não foi achada online |
| 🖼 Imagem | Knötel, *Uniformenkunde* IV 9 (1890), "Polen 1812" | Forma da czapka de infantaria (corpo que se alarga no topo quadrado) |
| 🖼 Imagem | Desenho *Wojsko polskie z okresu Księstwa Warszawskiego* (1850–60, Polona via Wikimedia) | Granadeiros com plumet carmesim e topo carmesim com cruz branca |
| 🎮 Arte do mod | `polandINF` c0 r5 (Reto, autorizado) | Águia coroada, placa com o número **4**, botão com estrela, cocar branco: contornos desenhados à mão sobre zoom 6× |

## 2. O que entrou

| Peça | Classes | Base |
|---|---|---|
| Kurtka de linha, regulamento de 1810 | `HCL_U_Varsovia1810_L1810` | Malha e pesos da casaca francesa (só leitura); azul-marinho, lapelas brancas, gola, punhos e vivos carmesim 📜 |
| 7º e 9º Regimentos | `HCL_U_Varsovia1810_R07`, `_R09` | Gola azul-marinho debruada de carmesim (7º); gola carmesim debruada de azul, punhos debruados de branco (9º); botões brancos (Askenazy e Gembarzewski) |
| Granadeiro e voltigeur | `HCL_U_Varsovia1810_Granadeiro_L1810`, `_Voltigeur_L1810` | Casaca de elite: dragonas carmesim; voltigeur com gola amarela e dragonas verdes 📜. Sem ornamentos nas viradas (nenhuma fonte os cita) |
| **Czapka rogata** (peça nova) | `HCL_H_Varsovia1810_Czapka_Fuzileiro`, `..._Czapka_Voltigeur` | `blockout_czapka_varsovia.py`: 23,2 cm de altura no ajuste à cabeça do jogo, topo quadrado de 25,8 cm de lado com um canto à frente (🔶 Knötel); águia de metal branco 77 × 64 mm sobre placa de latão 104 × 41 mm com o "4"; cocar branco; escamas com botão de estrela; cordões brancos pelas costas (🔶); pompom preto ou penacho verde e amarelo. 20,5 mil e 25,1 mil triângulos |
| Chapéu de pele dos granadeiros | `HCL_H_Varsovia1810_Bonnet_Granadeiro_Gala`, `..._Campanha` | Cópia do chapéu da Guarda: placa de latão com duas granadas e o "4" (`placa_varsovia_relevo.py`), **águia de metal branco** como peça própria por cima (94 × 78 mm), cocar **branco**, plumet carmesim, cordões brancos. 47,0 mil e 33,7 mil triângulos |

Não entrou: infantaria ligeira (o Ducado não tinha regimentos ligeiros; os voltigeurs são a companhia ligeira de cada regimento); as casacas do atlas com lapelas vermelhas, amarelas ou azul-claras (sem documento); a barretina com placa de sol do atlas (o regulamento de 1810 prescreve a czapka).

## 3. Problemas achados e corrigidos

1. **Forro atravessando o feltro** na parte alargada da czapka (primeiro render): a parede interna e o forro tinham poucas fileiras. Agora seguem as 17 fileiras do corpo.
2. **Cordão na frente da águia**: o festão passa agora pelas costas.
3. **Cocar tricolor francês** herdado do chapéu da Guarda: trocado pelo cocar branco do Ducado.
4. **Arte apagada na águia e na placa** da czapka (três tentativas):
   - 1ª: ilhas pequenas demais → `arte_escala=4` (4× mais texels). Não bastou.
   - 2ª: faixa de luminância `0,06–0,24`, medida errada em valores **sRGB**. Não mudou nada.
   - Diagnóstico: um bake de teste por emissão mostrou que a UV "arte" e o atlas estavam certos. O albedo cru, gravado por uma cópia de depuração do texturizador, saía **constante** (latão exatamente 0,413). O shader lê o atlas em valores **lineares**, e a filigrana polonesa fica em ~0,006–0,04: tudo caía abaixo do início da faixa.
   - Correção: `texturizar_aliados.py arte_faixa=0.005,0.045`. A águia passa a variar de 0,52 a 0,88 e a placa de 0,41 a 0,71; o "4" e a estrela do botão aparecem no close-up.

## 4. Pendências e incertezas

- 🔶 Forma do topo (canto à frente), início do alargamento a 55 % da altura, rota dos cordões, tamanho da águia e da placa (escala da arte do mod, 0,79 mm/px).
- 🔶 A pala do chapéu de pele dos granadeiros ("mały daszek") não foi modelada.
- 🔶 Viras brancas e portinholas azul-marinho da casaca de linha (o regulamento não detalha).
- O botão do voltigeur deveria ter uma corneta; não há essa arte no atlas, então ficou liso.

## 5. Montagem e verificação (fora do jogo)

- Texturas das casacas: `generate_uniform_textures_v2.py` (sem editar) com os JSONs de `variantes_varsovia.py` (3 de linha e 2 de elite, 2048 px). `_nohq`/`_smdi` são os franceses (mesma UV).
- Czapka e chapéu de pele: `texturizar_aliados.py` (cópia, com `atlas=`, `arte_faixa=` e o metal por cor).
- PAA: 21 de 21 com cabeçalho certo (`convert_varsovia_paa.ps1`).
- `build_mod_varsovia.ps1`: Binarize código 0, **6 de 6 modelos com `OFP2_ManSkeleton`**; avisos só dos 3 materiais do jogo, iguais aos da França. `CfgConvert` 0 (config e 6 rvmat); 9 itens e 5 soldados; `requiredAddons` só `A3_Characters_F`.
- PBO: `release/@Historical_Clothing/Addons/hcl_varsovia.pbo`, 38,3 MB, 18/10 às 17:04.
- `pbo_verify.py`: prefixo `hcl\hcl_varsovia`, 33 referências, **nenhuma faltando**.

Imagens (pasta principal, `docs/reports/img/varsovia/`): `varsovia_linha_*` (regulamento de 1810, 7º e 9º com a czapka de fuzileiro) e `varsovia_elite_*` (granadeiro de gala, fuzileiro, voltigeur, granadeiro de campanha; ombro e abas). `blockout_czapka_*` mostra o blockout.

Na mesma rodada o `hcl_suica.pbo` foi remontado só para os nomes do 2º e do 4º Suíço (fonte Fieffé achada): 7 de 7 com esqueleto, 48 referências, nenhuma faltando.

Próximo grupo (A1): **Reino da Itália e Nápoles**.
