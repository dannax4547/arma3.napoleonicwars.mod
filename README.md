# @Historical_Clothing

Addon para ARMA 3 com **vestimentas militares históricas da era napoleônica**: casacos, calças, barretinas, correames e acessórios. Modelado no Blender e convertido pelo pipeline oficial de ferramentas do jogo.

Sem facções, missões, sistemas de combate ou personagens de facção. Uso pessoal.

> Referências de terceiros sem autorização servem **só como referência visual**. Exceção: o Eras Mod, cuja autorização o usuário declarou em 2026-10-09 (detalhes pendentes; ver [docs/references.md](docs/references.md) §3.2).

---

## Estado

Briefing em vigor: **Pipeline Profissional de Modelagem 3D** (9 fases; detalhes em [docs/plan.md](docs/plan.md)).

| Fase | Barretina prussiana (1, **pausada**) | Uniforme prussiano 1813 (2) | Correame e mochila (3) |
|---|---|---|---|
| 1. Inspeção e planejamento | ✅ Aprovada | ✅ (plano geral) | ✅ (plano geral) |
| 2. Ficha técnica | ✅ [v1.1](docs/specs/shako_prussiano_infantaria.md) | ✅ [v1.1](docs/specs/uniforme_prussiano_infantaria_1813.md) (U1, U7 pendentes) | 🔶 [v1.0](docs/specs/equipamento_pruss_1813.md); aguarda E1–E6 |
| 3. Blockout | ✅ Aprovado | ✅ (aprovado ao pedir "mais realismo") | 🔶 [Pronto](docs/reports/equipamento_pruss_blockout.md); aguarda aprovação |
| 4. Modelagem de produção | ✅ [Aprovada](docs/reports/shako_pruss_producao.md) | 🔶 [Pronta](docs/reports/uniforme_pruss_producao.md) (11.960 triângulos); aguarda aprovação | ⏳ |
| 5. Revisão técnica | ✅ [Passou](docs/reports/shako_pruss_mesh_review.md) | ✅ [Passou](docs/reports/uniforme_pruss_mesh_review.md) | ⏳ |
| 6. UV e texturas | 🔶 [Pronta](docs/reports/shako_pruss_uv_texturas.md) + [5 variantes](docs/specs/variantes_regimentos_pruss.md); aguarda aprovação | 🔶 [UV + 8 variantes de cor](docs/specs/variantes_regimentos_pruss.md); aguarda aprovação | ⏳ |
| 7–9 | ⏳ | ⏳ | ⏳ |

Em 2026-10-10 o usuário pediu para começar as roupas, depois mais realismo e o equipamento (correame e mochila). A barretina fica pausada na Fase 6. O armamento entra só como peça visual (sem sistemas de combate).

Ainda em 2026-10-10 o uniforme virou a **base dos regimentos prussianos**. Foram feitas:
- 8 variantes de cor do uniforme;
- 6 variantes de barretina: FWR, águia e estrela, com presilha amarela ou branca.

Os nomes ainda são técnicos e descrevem a aparência. Ficam assim até o usuário informar o nome que o Eras Mod dá a cada unidade.

**Mod de teste (2026-10-10):** `release/@Historical_Clothing/Addons/hcl_pruss.pbo`.
- Contém 8 uniformes, 6 barretinas, correame e mochila (os dois em blockout).
- Foi gerado e verificado fora do jogo ([relatório](docs/reports/mod_teste_pruss.md)). **Ainda não foi testado no ARMA 3.**
- Instruções em `release/@Historical_Clothing/LEIA-ME_TESTE.txt`.

Também em 2026-10-10 foi feito um **teste de movimentos fora do jogo**: animações oficiais dos Arma 3 Samples aplicadas ao uniforme, às barretinas, ao correame e à mochila. Relatório: [docs/reports/teste_movimentos_pruss.md](docs/reports/teste_movimentos_pruss.md). Não substitui o teste dentro do ARMA 3 (Fase 9).

Os protótipos de barretina feitos antes deste briefing (v1 e v2) são **exploratórios e não aprovados**; a v1 está obsoleta. Um PBO **de teste** foi compilado em 2026-10-10 (ver acima). **Nada foi testado no ARMA 3 ainda.**

---

## Ferramentas

| Ferramenta | Estado |
|---|---|
| ARMA 3 2.22 | ✅ |
| Arma 3 Tools: Object Builder (com `FBX.dll`), TexView 2 (`TexView2\TexView.exe`), ImageToPAA, CfgConvert, BankRev, Addon Builder | ✅ |
| Blender 5.2.2 | ✅ |
| Arma 3 Samples (exemplo oficial de item de cabeça e corpo de referência) | ✅ Instalado em 2026-10-09 |

Detalhes: [docs/environment.md](docs/environment.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/plan.md](docs/plan.md) | Fases, critérios, decisões e pendências |
| [docs/references.md](docs/references.md) | Documentação técnica, dados verificados no jogo, referências visuais e autorizações |
| [docs/modeling_standards.md](docs/modeling_standards.md) | Escala, encaixe, topologia, UV, materiais, LODs e checklist técnico |
| [docs/asset_inventory.md](docs/asset_inventory.md) | Ativos do projeto e do jogo, estados e reorganização proposta |
| [docs/export_pipeline.md](docs/export_pipeline.md) | Blender → FBX → Object Builder → `.p3d` → `.paa`/`.rvmat` → config → PBO |
| [docs/testing.md](docs/testing.md) | Executado × verificação manual × não testado no jogo |
| [docs/environment.md](docs/environment.md) | Inspeção do ambiente (versões e caminhos) |

## Estrutura

```
source/models/{coats,trousers,shakos,accessories}/
source/textures/
source/scripts/
docs/
work/                                  extrações de consulta; nunca entram no addon
release/@Historical_Clothing/Addons/
```

## Instalação

Pendente (Fase 9). Só será escrita depois que o PBO for gerado e testado.
