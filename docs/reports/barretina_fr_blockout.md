# Esboço (Fase 3): Barretina Francesa por Companhia

Data: 2026-10-12. Ficha: `docs/specs/barretina_francesa_1812.md`.

**Estado:** aguarda aprovação (B1–B4). Tem formas e cores de identificação; **não tem UV nem textura**, como pede a Fase 3.

- Script: `source/scripts/blockout_shako_fr.py`
- Cena: `source/models/shakos/hcl_shako_fr/hcl_shako_fr_blockout.blend`
- Imagens: `docs/reports/img/barretina_fr/`

## 1. Encaixe

Mesmo método da barretina prussiana aprovada:
- aro de cabeça medido no boné oficial dos Samples (`shako_fit.py`, só leitura);
- inclinação de 8° (nuca mais baixa);
- parede de 4 mm, com folga de 2 mm.

Resultado do encaixe: escala 1,0317, altura 0,196 m, base 0,186 × 0,210 m, topo 0,258 × 0,291 m.

## 2. As cinco configurações

| # | Configuração | Peças | Triângulos (esboço) | Topo acima do chão |
|---|---|---:|---:|---:|
| 1 | Fuzileiro, 1ª companhia: pompom lentilha verde-escuro, faixas e divisas de couro preto | 16 | 4.576 | 0,983 m |
| 2 | **Granadeiro de gala**: galões e divisas vermelhos, plumet vermelho de 0,30 m, cordões vermelhos com raquete e 2 borlas do lado direito | 22 | 6.272 | 1,239 m |
| 3 | **Granadeiro de campanha**: galões e divisas vermelhos, pompom vermelho grande | 16 | 4.736 | 0,997 m |
| 4 | **Voltigeur de gala**: galões e divisas amarelos, plumet verde de ponta amarela, cordões verdes | 23 | 6.352 | 1,239 m |
| 5 | **Voltigeur de campanha**: galões e divisas amarelos, pompom amarelo grande | 16 | 4.736 | 0,997 m |

Todas têm placa de águia sobre semicírculo, cocar tricolor, pala, e jugulares de escamas com rosetas.

Os triângulos são do esboço: as voltas dos pompons e do plumet ainda estão em alta resolução. Na produção (Fase 4), o alvo é o da barretina prussiana (~5.200).

### 2.1 Atualização de 2026-10-12: plumet realista e oficial

- **Plumet** (`plumet.py`): penas em camadas no lugar do fuso liso. Fica mais cheio (raio 0,032 m), com a ponta macia; ~2.700 triângulos.
- **Oficial coronel:** 2 galões dourados (34 + 14 mm), sem divisas, plumet branco. 17 peças, 7.610 triângulos no esboço.
- **Fileira de plumets** (`blockout_fr_plumets.png`, da esquerda para a direita):
  1. granadeiro (vermelho);
  2. voltigeur (verde de ponta amarela);
  3. coronel (branco);
  4. major (branco de ponta vermelha);
  5. chefe de batalhão (vermelho);
  6. Garde zu Fuß prussiana (Stutz branco e preto);
  7. Prússia (verde-escuro).

  Vista de perto: `blockout_fr_plumets_detalhe.png`.

### 2.2 Atualização de 2026-10-12, à tarde: plumet com mais volume (v2)

Pedido: *"de mais volume aos pumlets"*. Mudanças em `plumet.py`, que valem para os plumets franceses e para o prussiano:
- raio da forma de cenoura de 0,032 para **0,042 m**, e o Stutz (Garde) para 0,050 m;
- perfil mais cheio: a largura máxima chega mais cedo (a 28% da altura) e afina devagar até a ponta;
- penas mais largas no meio, torcidas (até ±0,45 rad) e mais abertas;
- 10% das penas soltas: 35% mais compridas e com o dobro de abertura, para o contorno não ficar liso;
- tufo de 14 penas na ponta.

Triângulos: ~4.600 por plumet (Stutz ~5.200). Os scripts que chamam `plumet()` não passam mais o raio: usam o padrão novo. As imagens `blockout_fr_plumets*.png` já são da v2.

### 2.3 Texturas das 6 barretinas (2026-10-12)

Pedido: *"de mais texturas as barretinas francesas"*. Script `source/scripts/texturizar_shako_fr.py`.

Cada configuração vira **uma malha** (`HCL_Shako_Fr_<tag>_LOD0`) com **um jogo de texturas de 2048 px** (`_co`, `_nohq`, `_smdi`), gerado a partir de materiais procedurais assados no Cycles (cor, normal, oclusão):

| Superfície | Textura |
|---|---|
| Feltro do corpo | felpa fina e manchas leves |
| Couro (faixas, divisas do fuzileiro) | grão de couro (Voronoi) |
| Pala | verniz liso e brilhante |
| Latão (placa, jugulares, rosetas, tulipa) | oxidação, riscos e brilho de metal |
| Galão dourado do oficial | metal com nervuras do tecido |
| Galões e divisas de lã (vermelhos, amarelos) | nervuras do galão e felpa |
| Cocar | pregas em anel |
| Pompons | lã felpuda, relevo forte |
| Cordões, raquete e borlas | trança |
| Penas do plumet | pintadas à parte: barbas e haste, em 3 tons por cor, com as cores de penas tingidas (mais vivas que a lã) |

- O `_smdi` dá brilho e reflexo por superfície: o metal e o verniz brilham, a lã e o feltro não.
- A UV é automática (Smart UV). As penas usam 9 quadros reservados no atlas.

| Configuração | Triângulos |
|---|---:|
| Fuzileiro, 1ª companhia | 4.520 |
| Granadeiro de gala | 9.982 |
| Granadeiro de campanha | 4.680 |
| Voltigeur de gala | 9.982 |
| Voltigeur de campanha | 4.680 |
| Oficial coronel | 9.462 |

As de gala passam de 5.200 por causa do plumet v2. Dá para reduzir na produção se o jogo pesar.

Arquivos:
- texturas: `source/textures/hcl_shako_fr/`;
- malhas texturizadas: `source/models/shakos/hcl_shako_fr/hcl_shako_fr_texturas.blend`.

### 2.4 Atualização de 2026-10-12, noite: barretinas "da época"

Pedido: *"traz mais realismo a pumlet e as barretinas como se fossem na quela epoca"*.

Mudanças:
- placa traçada da arte do mod (águia coroada sobre semicírculo; versão com granadas para os granadeiros);
- jugulares de escamas sobrepostas;
- presilha e botão no cocar;
- rosetas com estrela;
- borlas com franja;
- pompons de lã irregular;
- plumet v3, de penas curtas deitadas.

Detalhes e triângulos: `frances_1812_prototipo.md` §8.3. Os traçados estão em `source/models/shakos/hcl_shako_fr/placa_aguia_{semicirculo,granadas}.json`.

**Erro achado e corrigido:** os bakes deixavam só a última barretina visível no render. Por isso as primeiras imagens saíram vazias. O script agora reativa todas antes dos renders, e o `.blend` foi salvo de novo com as 6 visíveis.

## 3. Imagens

| Arquivo | Vista |
|---|---|
| `blockout_fr_fila_frente.png` | As 5, de frente, na ordem da tabela |
| `blockout_fr_fila_tres_quartos.png` | As 5, em 3/4 |
| `blockout_fr_granadeiro_lado.png` | Granadeiro de gala, lado direito: divisa em V, cordões, raquete e borlas |
| `blockout_fr_voltigeur_lado.png` | Voltigeur de gala, lado direito |
| `blockout_fr_fuzileiro_lado.png` | Fuzileiro, lado direito |
| `blockout_fr_oficial_lado.png` | Oficial coronel, lado direito |
| `blockout_fr_plumets.png`, `blockout_fr_plumets_detalhe.png` | Os 7 plumets sozinhos |
| `textura_fr_fila_tres_quartos.png` | As 6 texturizadas, em 3/4 (fuzileiro, granadeiro gala e campanha, voltigeur gala e campanha, coronel) |
| `textura_fr_{fuzileiro,granadeiro,voltigeur,oficial}_perto.png` | De perto: feltro, couro, galões, cordões, latão, galão dourado |

A cabeça das imagens é uma **aproximação** (elipsoide do aro oficial), não a cabeça do jogo. A posição das jugulares sob o queixo é estimada e só fica confirmada no jogo, como na Prússia.

## 4. Achado durante o trabalho (corrigido)

O Blender salvou os renders com caminho relativo na raiz do disco, `C:\docs\reports\img\...`, fora do projeto. Já tinha acontecido em 2026-10-10 com as imagens das barretinas águia e estrela, que **não estavam no projeto**.

- O script novo usa caminhos absolutos.
- As imagens foram **copiadas** para `docs/reports/img/barretina_fr/` e `docs/reports/img/variantes/barretina_{aguia,estrela}/`.
- A pasta `C:\docs` **não foi apagada**: fica fora do projeto e depende de autorização do usuário.

## 5. Vale também para a Prússia

O atlas `prussia1813_01` tem um plumet verde-escuro (c5–c6 r5), que antes estava fora de alcance por falta de geometria. A mesma forma de plumet, aprovada em B1, entra na barretina prussiana (`docs/specs/variantes_regimentos_pruss.md` §9.2).

## 6. Próximo passo depois da aprovação

Fase 4, a malha de produção:
- forma final, com o plumet em penas (lâminas em leque) e os cordões trançados;
- placa traçada da arte do mod com `trace_badge.py`, como foi feito na águia prussiana;
- depois UV, as texturas das 8 classes e a montagem no mod.
