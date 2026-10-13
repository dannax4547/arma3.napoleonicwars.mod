# Plano do Projeto

Atualizado em 2026-10-09. Briefing em vigor: **"Historical Clothing — Pipeline Profissional de Modelagem 3D para ARMA 3"** (substitui os briefings anteriores).

## 1. Escopo

**Dentro:** casacos e uniformes, calças, barretinas e outros itens de cabeça, correames, cintos, bolsas, botões, distintivos e acessórios, além de variantes históricas documentadas.

**Fora:** facções, missões, sistemas de combate, personagens de facção.

## 2. Regras em vigor

1. Um único protótipo por vez, com aprovação antes de avançar.
2. Nenhuma etapa é declarada concluída sem verificar arquivos e critérios.
3. Não inventar modelos, arquivos, classes, caminhos ou detalhes regimentais.
4. Referências de terceiros sem autorização (NTW/Eras): **só visuais**.
5. O Blender não gera `.p3d`; a conversão é documentada e validada (`export_pipeline.md`).
6. Não instalar ferramentas, apagar arquivos nem modificar nada fora do projeto sem autorização.
7. Separar testes executados, verificações manuais pendentes e itens não testados no jogo.

## 3. Fases

| Fase | Entrega | Critério de conclusão | Estado |
|---|---|---|---|
| 1. Inspeção e planejamento | `references.md`, `modeling_standards.md`, `asset_inventory.md`, `export_pipeline.md`, `testing.md` | Documentos com dados verificados; dúvidas e pendências registradas; **plano aprovado pelo usuário** | ✅ Aprovado em 2026-10-09 |
| 2. Ficha técnica histórica | `docs/specs/<peça>.md` | Período, identificação, referências autorizadas, vistas, silhueta, proporções, costuras, componentes, cores, materiais, elementos confirmados × incertos, requisitos do ARMA 3; aprovada (V1) | 🔶 `docs/specs/shako_prussiano_infantaria.md` v1 pronta; **aguarda decisões F1–F5 e aprovação** |
| 3. Blockout | `.blend` com formas principais sobre o corpo de referência oficial | Silhueta conferida nas vistas ortográficas; escala registrada; sem UV ou textura finais; aprovado (V2) | ✅ Aprovado em 2026-10-09 (pala 55°, jugular sob o queixo) |
| 4. Modelagem de produção | Malha organizada | Topologia e densidade conforme `modeling_standards.md`; aprovada (V3) | 🔶 Pronta (`docs/reports/shako_pruss_producao.md`, 5.194 triângulos); **aguarda aprovação** |
| 5. Revisão técnica | `docs/reports/<peça>_mesh_review.md` | Checklist M1–M7 executado; defeitos, correções e pendências listados | ✅ Executada (`docs/reports/shako_pruss_mesh_review.md`): todas as verificações automáticas passaram após 3 iterações |
| 6. UV e texturas | UVs, texturas-fonte e `.paa` | T1–T4 | 🔶 Pronta (`docs/reports/shako_pruss_uv_texturas.md`); T1, T2, T4 ✅; T3 automático ✅, TexView 2 manual pendente; **aguarda aprovação** |
| 7. Preparação ARMA 3 | `.p3d` com LODs, seleções, pesos e propriedades | B1–B2; para roupas, esqueleto, pesos e articulações | ⏳ |
| 8. Configuração | `config.cpp` com `HCL_` e bases verificadas | C1–C2 | ⏳ |
| 9. Testes | PBO + testes no jogo | P1–P2, G1–G12 com evidência | ⏳ |

## 4. Protótipo único proposto

**Barretina, tendo como referência principal a foto R2** (`docs/references/img/ref_shako_02_foto_fwr.png`), que o usuário indicou como "mais assim".

Por que começar pela barretina: é um item rígido, preso a um único osso (`head`). O pipeline completo (LODs, seleções, `.rvmat`, config, PBO) fica validado com menos risco do que num casaco, que exige pesos em várias articulações.

### Requisitos para produzir este protótipo

| # | Requisito | Situação |
|---|---|---|
| R-1 | Aprovação deste plano (Fase 1) | ⏳ Usuário |
| R-2 | Identificação histórica da peça de R2 (período, Estado, tipo de unidade) por uma fonte confiável; o que não for confirmado fica marcado como incerto | ⏳ Usuário fornece ou aprova a fonte |
| R-3 | Origem das imagens R1/R2 | ⏳ Usuário |
| R-4 | Corpo de referência oficial: **Arma 3 Samples** (gratuito, Steam → Ferramentas) | ❌ Precisa de autorização e instalação pelo usuário |
| R-5 | Requisitos de LOD e propriedades confirmados na wiki da Bohemia | ❌ Leitura bloqueada; o usuário pode liberar a página no navegador do app ou colar o texto |
| R-6 | Teste B1: importação de FBX no Object Builder | ⏳ Usuário, depois do blockout |
| R-7 | Reorganização de pastas (`asset_inventory.md` §4) | ✅ Feita em 2026-10-09 (só movimentos; `.blend` religados às texturas) |

## 5. Decisões registradas

| Data | Decisão |
|---|---|
| 2026-10-09 | Addon de uso pessoal; sem facções |
| 2026-10-09 | Prefixo `HCL_` |
| 2026-10-09 | Material NTW: só referência visual (sem autorização) |
| 2026-10-09 | Barretinas v1/v2 = protótipos exploratórios, não aprovados; v1 obsoleta |
| 2026-10-09 | Usuário indicou R2 como referência principal para a barretina |
| 2026-10-09 | Briefing "Pipeline Profissional" adotado; `build_shako_v3.py` fica como rascunho não executado |
| 2026-10-09 | Itens de cabeça: ponderados ao osso `head` de `OFP2_ManSkeleton` e modelados na posição da cabeça do personagem (observado nos modelos oficiais) |
| 2026-10-09 | Fase 4 (malha de produção) aprovada |
| 2026-10-09 | Usuário declarou autorização dos autores do Eras Mod (detalhes pendentes, ver `references.md` §3.2); texturas do mod podem entrar no addon |
| 2026-10-09 | Variantes de regimento: nomes segundo o Eras Mod; produção depois que o protótipo passar nos testes (plano em `docs/specs/shako_variantes_plano.md`) |
| 2026-10-10 | Usuário pediu "mais realismo" no uniforme (blockout aceito → Fase 4 feita) e o "passo final": mochila e colete com o armamento. Protótipo 3 = correame (colete) + mochila; armamento só visual (baioneta na bainha, cartucheira), sem sistemas de combate |
| 2026-10-10 | Usuário pediu para iniciar as roupas: **protótipo 2 = uniforme de infantaria de linha prussiana de 1813** (casaco, calças, polainas e sapatos num só modelo de corpo inteiro, como exige o ARMA 3). Barretina pausada na Fase 6. Ficha: `docs/specs/uniforme_prussiano_infantaria_1813.md` |
| 2026-10-10 | Usuário pediu o mod para testar no jogo. Gerado `release/@Historical_Clothing/Addons/hcl_pruss.pbo`: 8 uniformes, 6 barretinas, correame e mochila (blockout). Rota sem Object Builder e sem drive P:: MLOD escrito por `p3d_mlod_io.py` (validado byte a byte nos Samples) sobre os templates oficiais, binarizado e empacotado com as ferramentas oficiais. É um **build de teste** das Fases 7–9 antes das aprovações; não substitui a revisão dessas fases. Relatório: `docs/reports/mod_teste_pruss.md` |
| 2026-10-10 | Usuário pediu um "teste final" com os movimentos do ARMA 3 e depois o correame e a mochila em todas as roupas e barretinas. Como o teste no jogo exige as Fases 7–9, foi feito **fora do jogo**: animações oficiais dos Samples (`RTM_0101`), pesos v0 transferidos do corpo oficial, medidas de camadas, separações, cruzamentos e esticamento, e galeria com as 8 roupas e as 6 barretinas. Relatório: `docs/reports/teste_movimentos_pruss.md` |
| 2026-10-10 | Usuário declarou o uniforme como **base para os outros regimentos prussianos** e pediu mais padrões de barretina. Feito: UV + texturas do uniforme (Fase 6) com **8 variantes de cor** (V01–V08, catalogadas nos atlas do mod) e **5 variantes novas de barretina** (FWR branca; águia amarela/branca; estrela prata/latão; águia e estrela com malha própria). Nomes técnicos, sem regimento. Ficha: `docs/specs/variantes_regimentos_pruss.md` |

| 2026-10-11 | Usuário pediu "mais detalhe e texturas" nas roupas, no colete e na mochila, com qualidade de artista profissional. Feito: **malha de produção do correame e da mochila** (Fase 4) com UV e texturas próprias (Fase 6), **texturas v2 do uniforme** (oclusão, costuras, dobras, desgaste, lama) e pesos v1. O v1 das texturas foi guardado. Relatório: `docs/reports/detalhe_texturas_pruss.md` |

| 2026-10-11 | Usuário pediu "finalizar todos os regimentos possíveis da Prússia". Feito tudo o que os atlas de infantaria do Eras Mod mostram no corte do Kollet: **17 uniformes** (9 verdes novos; V03 corrigida), **14 barretinas** (presilha preta e linhas da faixa) e **couro preto** para correame e mochila. Landwehr, cavalaria e oficiais precisam de peças novas (fora desta base). Ficha 1.1: `docs/specs/variantes_regimentos_pruss.md` §9 |

## 6. Decisões pendentes

| # | Decisão | Quando |
|---|---|---|
| D1 | ~~Aprovar o protótipo único~~: aprovado (barretinas) em 2026-10-09 | ✅ |
| D2 | ~~Instalar o Arma 3 Samples~~: instalado pelo usuário em 2026-10-09 | ✅ |
| D8 | Jugular: sob o queixo (exige teste no jogo) ou recolhida sobre a pala | Aprovação do blockout |
| D3 | ~~Reorganização de pastas~~: aprovada e feita | ✅ |
| D7 | Silhueta e distintivos da barretina (ficha técnica, F1–F5) | Agora |
| D4 | Base de config do item de cabeça: `HelmetBase` ou `H_HelmetB` | Fase 8 |
| D5 | Unidade P: e prefixo do PBO | Fase 7/8 |
| D6 | ~~Primeiro uniforme~~: infantaria de linha prussiana de 1813, iniciado em 2026-10-10 a pedido do usuário | ✅ |
| D10 | Equipamento: decisões E1–E6 da ficha `equipamento_pruss_1813.md` (E6 = mosquete funcional, fora do escopo) | Agora |
| D9 | Decisões da ficha do uniforme: U2–U6 aprovadas em 2026-10-10 (recomendações); **U1** (nome da unidade no mod) e **U7** (detalhes da autorização) pendentes | U1 antes da Fase 8 |
| D11 | Variantes regimentais: V-A (aprovar), V-B (nomes do mod), V-C (casacas verdes), V-D (presilha preta, linhas da faixa), V-E (= U7, antes de qualquer distribuição) | Agora |
| D12 | Aprovar a malha de produção e as texturas do correame e da mochila, o orçamento revisto (≤ 4.000 triângulos por item) e as texturas v2 do uniforme | Agora |
| D13 | **Próximas nações** (pedido de 2026-10-12): inventário em `docs/reports/inventario_nacoes.md`; protótipo da França em `docs/specs/uniforme_frances_infantaria_1812.md` (Fase 2), que aguarda F1–F5, F7 e F8. **Barretina francesa por companhia** (fuzileiros, granadeiros e voltigeurs, gala e campanha), pedida pelo usuário em 2026-10-12: ficha `docs/specs/barretina_francesa_1812.md` e esboço `docs/reports/barretina_fr_blockout.md` (B1–B4). A Prússia continua com V-A/V-F/V-G e o teste no jogo pendentes | Agora |

## 7. Limitações conhecidas

- Os uniformes oficiais são binarizados (`ODOL`) e não editáveis; casacos novos exigem modelagem própria com pesos no esqueleto `OFP2_ManSkeleton`. O `A3_character_template.p3d` dos Samples (MLOD, editável) fornece as mãos e todos os LODs técnicos.
- A importação FBX do Object Builder ainda não foi testada.
- Não há editor de imagem 2D instalado; as texturas têm sido geradas por código.
