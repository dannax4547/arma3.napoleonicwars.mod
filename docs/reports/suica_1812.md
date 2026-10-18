# Suíços a serviço da França, 1812: addon de teste `hcl_suica`

Data: 2026-10-13. Pedido do usuário: *"agora adiciona os aliados franceses"*. Os suíços são o 1º grupo (decisão A1). Ficha: `docs/specs/aliados_fr_1812.md` §4 e §8.

**Estado:** PBO montado e verificado **fora do jogo**. Nada foi visto no Arma 3.

## 1. O que entrou

| Peça | Classes | Base | Fonte das cores |
|---|---|---|---|
| Casaca de linha, 4 regimentos | `HCL_U_Suica1812_S1` … `_S4` | Malha e pesos da casaca francesa 1812 (`hcl_fr_pesos.blend`, só leitura) | 1º ✅ (Wikipedia, regulamento de 1812); 3º ✅ (Fieffé 1854 via Wikipedia); 2º e 4º 🔶 (decisão A6) |
| Casaca de granadeiro, 4 regimentos | `HCL_U_Suica1812_Granadeiro_S1` … `_S4` | Casaca de elite francesa (dragonas) | Dragonas vermelhas ✅ (1º); granadas nas viradas 🔶 (padrão francês) |
| Casaca de voltigeur, 4 regimentos | `HCL_U_Suica1812_Voltigeur_S1` … `_S4` | Idem | Dragonas verdes de meia-lua amarela e cornetas 🔶 (padrão francês). Gola do regimento mantida (sem fonte para gola camurça) |
| Chapéu de pele do granadeiro | `HCL_H_Suica1812_Bonnet_Granadeiro_Gala`, `..._Campanha` | Cópia do chapéu da Velha Guarda v5 (`blockout_bonnet_suica.py`) | Placa "de cobre com granada" ✅ (Wikipedia, 1º Suíço, 1812). Contorno da placa, cordões, plumet e cruz no topo 🔶 |
| Barretinas | `HCL_H_Suica1812_Fuzileiro_1aComp` … `_4aComp`, `HCL_H_Suica1812_Voltigeur_Gala`, `..._Campanha` | Barretinas francesas v4, cópias com prefixo próprio | Modelo francês 🔶 para os suíços |
| Soldados (escopo 1) | `HCL_Suica1812_Soldado_S1` … , `_Granadeiro_S1` … , `_Voltigeur_S1` … | — | — |

Cores por regimento (sRGB, mesmas da França e da Prússia):

| Regimento | Vistas (gola, lapelas, punhos, viradas) | Vivos | Confiança |
|---|---|---|---|
| 1º | amarelo | vermelho na gola e lapelas; branco nas portinholas | ✅ + viradas e botões 🎮 (`FranceINF_3` c5 r0) |
| 2º | azul-real | branco | 🔶 (sem fonte de cor) |
| 3º | preto | branco | ✅ (Fieffé); viradas e platinas 🔶 |
| 4º | azul-celeste | branco | 🔶 ("azul" só em páginas de loja) |

Nomes em inglês (`nomes_en_aliados.py`): o 2º e o 4º levam *"(facing colour unconfirmed)"*.

## 2. Placa com granada

`placa_suica_relevo.py`, cópia de `placa_guarda_relevo.py`: mesmo contorno, borda e fileira de pérolas da placa da Guarda (🔶), com **uma granada flamejante grande** no lugar da águia (bola de raio 27 mm, chamas até 136 mm, 17 mm dentro da borda). Relevo de 8 px/mm em `source/models/bonnet/hcl_bonnet_suica/placa/`.

Chapéu (`blockout_bonnet_suica.py` + `texturizar_shako_fr.py raiz=SU_`, sem editar o script compartilhado):

| Variante | Triângulos Res 1 | Res 2 (sem mechas) |
|---|---|---|
| gala (placa, cordões brancos, plumet vermelho) | 46.154 | 22.266 |
| campanha (só a placa) | 32.800 | 8.936 |

## 3. Montagem e verificação (fora do jogo)

- Texturas das casacas: `generate_uniform_textures_v2.py` (sem editar), com os JSONs de `variantes_suica.py`. 4 + 8 `_co` de 2048 px; `_nohq`/`_smdi` são os franceses (mesma UV).
- PAA: 34 de 34 com cabeçalho certo (`convert_suica_paa.ps1`).
- `build_mod_suica.ps1`: P3D sobre os templates oficiais; Binarize código 0; **7 de 7 modelos com `OFP2_ManSkeleton`**. Avisos só dos 3 materiais do jogo (mãos e penetração), iguais aos da França.
- `CfgConvert` 0 (config e 7 rvmat). Config: 20 itens e 12 soldados, `requiredAddons` só `A3_Characters_F`.
- PBO: `release/@Historical_Clothing/Addons/hcl_suica.pbo`, 59,2 MB, 13/10 às 18:56.
- `pbo_verify.py`: prefixo `hcl\hcl_suica`, 48 referências, **nenhuma faltando**.

Imagens: `docs/reports/img/suica/` (pasta principal):
- `suica_linha_fila_frente.png`, `_fila_costas`, `_busto_*`;
- `suica_elite_fila_frente.png` (granadeiro 1º gala, voltigeur 1º gala, granadeiro 3º campanha, voltigeur 4º campanha), `_fila_costas`, `_ombro`, `_abas_costas`.

## 4. Pendências

- Testes no jogo: `docs/testing.md` §6 (S1–S5).
- 2º e 4º Suíço: confirmar as cores numa fonte (Osprey *Napoleon's Swiss Troops*).
- Granadeiro suíço: forma da placa e topo (cruz × granada, ligado à decisão G7 da Guarda) 🔶.
- O correame e a mochila não foram copiados para o `hcl_suica`; use os do `hcl_fr` no Arsenal, se ele estiver carregado.

Próximo grupo (A1): **Ducado de Varsóvia**. Falta a decisão A5 (barretina com placa de sol × czapka).
