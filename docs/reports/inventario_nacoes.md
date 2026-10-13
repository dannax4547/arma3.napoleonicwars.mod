# Inventário das Nações nas Referências do Mod (Fase 1)

Data: 2026-10-12. Pedido do usuário: *"dar continuidade às próximas nações"*.

**Fonte (só leitura):** `C:\Users\lucas\OneDrive\Área de Trabalho\roupas e texturas para mod da era napoleonica no arma 3`. Ali há 7 pacotes de mods:
- `(N)_Reto_BattleMOV11-15`, `(N)_Reto_BattleMOv2`, `(N)_Reto-BattleMOVearly`, `(N)_Reto_rigidmodels`, `(N)_Reto_texture9`;
- `(N)_LME4_graphics`, `(N)_LME4_Camp1815_Chapter_XIV`.

Os atlas da Prússia já usados vêm de `(N)_Reto_BattleMOV11-15`.

Só existem texturas (`.dds`). **Não há nenhum arquivo que dê o nome do regimento de cada bloco**, então os nomes continuam técnicos, como na Prússia.

## 1. Atlas de unidades por nação

Cada atlas tem 4096 × 4096 px (8 × 8 blocos de 512 px), com `_diffuse`, `_normal`, `_gloss` e `_colour_mask`.

| Nação | Infantaria | Cavalaria / outros | Pacote |
|---|---|---|---|
| **França** | `FranceINF`, `FranceINF_2`, `FranceINF_3`; e no LME4 `franceb`…`franceg`, `francee2`, `francee98`, `francerc`, `france_roy`, `imperial_guardsb` | `FranceCAV`, `FranceLighCAV` (2), `FranceART` (2), `FranceGeneral18051815` | Reto + LME4 |
| Grã-Bretanha | `britainINF`, `britainINFb`, `britainINFc`; LME4 `britain1`, `britain2`, `britainr`; peças soltas (chapéus, pernas, troncos) em `Reto_BattleMOv2` e `Reto-BattleMOVearly` | `britainCAVb`, `britainCAVc` | Reto + LME4 |
| Rússia | `rus1812INF`, `rus1812INF2` | `rus1812CAV` (3), `rus1812GEN` | Reto |
| Áustria | `austriaINF`, `austriaINF_2`; LME4 `austrialme` | `austriaCAV` (2) | Reto + LME4 |
| Prússia | `prussia1813_01`…`05` (**já feita**); LME4 `prussiar`, `prussiabz` | — | Reto + LME4 |
| Saxônia | `saxonINF1812`, `saxonINF1812b` | `saxonCAV1812` | Reto |
| Baviera | `BavariaINF`; LME4 `bavaria` | `BavariaCAV`, `BavariaGEN` | Reto + LME4 |
| Vestfália | `WestphaliaINF` | `WestphaliaCAV`, `WestphaliaLighCAV` | Reto |
| Württemberg | `WurtembergINF_2` | `WurtembergCAV_2`, `WurtembergLighCAV` | Reto |
| Espanha | `SpanishINF`, `Spanish2INF` | `spanishCAV`, `SpanishART_CAV` | Reto |
| Polônia (Ducado de Varsóvia) | `polandINF` | `PolandCAV`, `PolandART` | Reto |
| Reino da Itália | `ItalyINF` | `ItalyCAV` | Reto |
| Nápoles | `NaplesINF` | `NaplesCAV`, `NaplesGEN` | Reto |
| Holanda (1806–1811) | `NederlandINF18061811` (2) | `NederlandCAV18061811` (3) | Reto |
| Dinamarca | `denmarkINF` | — | Reto |
| Oldemburgo | `oldenburgINF1812` | `oldenburgCAV1812` | Reto |

Também há bandeiras de interface de muitas outras nações e repúblicas (`ui\flags\...`, LME4). Elas não são uniformes e ficam fora do escopo.

## 2. Ordem proposta (um protótipo por vez, como no briefing)

| # | Nação | Por quê |
|---|---|---|
| 1 | **França** | Mais material (3 atlas Reto + 9 LME4 + Guarda) e principal adversária da Prússia em 1813–1815 |
| 2 | Grã-Bretanha | 6 atlas de infantaria e peças soltas; casaca vermelha muito diferente (teste de variedade) |
| 3 | Rússia | Aliada de 1813; 2 atlas |
| 4 | Áustria | Aliada de 1813; 3 atlas |
| 5 | Confederação do Reno: Saxônia, Baviera, Vestfália, Württemberg | Cortes parecidos entre si; boa reutilização |
| 6 | Espanha, Polônia, Itália, Nápoles, Holanda, Dinamarca, Oldemburgo | Um atlas de infantaria cada |

Cada nação passa pelas 9 fases, mas reaproveita o que a Prússia já validou:
- o corpo e os LODs técnicos do template;
- o gravador de P3D, os pesos v2 e o teste de movimentos;
- o pintor de texturas e o build do mod.

O que muda é a malha da casaca e da barretina (ou do chapéu) de cada nação.

## 3. Ressalvas

- **Autorização:** em 2026-10-09 o usuário declarou autorização dos autores do mod (detalhes pendentes, U7). **Não está confirmado se ela cobre também os pacotes LME4** (decisão F7 na ficha da França).
- Nada foi alterado na pasta de referências. As conversões PNG estão em `work/ntw/<nação>/`.
