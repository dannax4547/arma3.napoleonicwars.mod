# Plano de Variantes da Barretina (rascunho; nada produzido)

Data: 2026-10-09 · Pedido do usuário: "adiciona variáveis para os outros regimentos com as texturas do Eras Mod".

## 1. Restrições do briefing em vigor

| Regra | Efeito no pedido |
|---|---|
| "Usar o Eras Mod como referência visual apenas quando houver acesso aos recursos e autorização apropriados." | **As texturas do Eras/NTW não podem ser aplicadas ao addon** sem autorização dos autores. Podem ser **olhadas** para orientar cores e distintivos; as texturas das variantes são próprias. |
| "Não produza o catálogo inteiro de uma vez. Trabalhe com um único protótipo, obtenha aprovação e só depois avance." | As variantes vêm **depois** que o protótipo passar pelas Fases 6–9 (UV/texturas, preparação, config e teste no jogo). |
| "Não invente detalhes regimentais." | Cada variante só recebe o nome de um regimento com uma fonte histórica. Sem fonte, ela é nomeada pela aparência (ex.: "presilha branca"). |

## 2. Diferenças observadas nas texturas do mod (referência visual)

Fonte: atlas `prussia1813_01_diffuse.dds` (BattleMOV11-15), faixa das barretinas, vista em resolução cheia em 2026-10-09.

| Elemento | Variações vistas | Peça do nosso modelo |
|---|---|---|
| Presilha e roseta do cocar | **Metal branco** e **latão** | Ilha 3 (presilha) + cocar |
| Distintivo frontal | **Águia de latão**, **estrela (prateada)** | Hoje: monograma FWR |
| Faixa de couro | Com a cifra "FWR" pequena | Faixa inferior |
| Pluma | Verde (uma variante) | Não existe no modelo |
| Caveira | Uma variante (provavelmente outra unidade, não infantaria prussiana) | Fora do escopo |

Nos atlas de casacas aparecem golas e punhos **vermelhos, brancos e amarelos** e casacas azuis e verdes. Essas diferenças são da **casaca**, não da barretina.

## 3. Como as variantes funcionam no ARMA 3 (verificado nos arquivos oficiais)

| Mecanismo | Evidência |
|---|---|
| Uma classe filha que muda só `hiddenSelectionsTextures[]` sobre a mesma malha | ✅ `H_MilCap_mcamo: H_MilCap_ocamo` só troca a textura `cappatrol_*_co.paa` (`work/a3/configs/characters_f.config.cpp:31770`) |
| A seção `Camo` (seleção `camo`) definida no `model.cfg` como seção trocável | ✅ `Test_Character_01\model.cfg` |
| Esconder uma peça trocando sua textura por vazio | ❔ **A verificar** antes de usar |

Proposta técnica (para a Fase 6/7 do protótipo, para não refazer depois):
- seleção `camo` no corpo (feltro, faixa, debrum, pala);
- seleções separadas e trocáveis para a presilha/cocar e para o distintivo frontal;
- variantes de cor (presilha branca × amarela) só por textura;
- variantes de **forma** (águia, estrela) exigem geometria própria: novo `.p3d` ou peças alternativas na mesma malha, conforme o resultado da verificação acima.

## 4. Matriz de variantes candidatas (nomes por aparência)

| ID | Variante | Tipo | Fonte histórica para nome de regimento |
|---|---|---|---|
| V1 | Presilha amarela + monograma FWR (protótipo atual) | — | ❓ |
| V2 | Presilha e botões de metal branco | Textura | ❓ Precisa de fonte: cor dos botões por regimento |
| V3 | Águia de latão no lugar do monograma | Geometria + textura | ❓ |
| V4 | Estrela da Guarda | Geometria + textura | ❓ |
| V5 | Capa de oleado preta (uso em campanha) | Geometria | ❓ |

## 5. O que é preciso para avançar

1. Protótipo aprovado nas Fases 6–9.
2. **Autorização dos autores do Eras Mod**, se quiser usar as texturas deles diretamente; caso contrário, texturas próprias.
3. Fontes históricas (Knötel, regulamentos, museus) para associar variantes a regimentos, ou aceitar nomes por aparência.
