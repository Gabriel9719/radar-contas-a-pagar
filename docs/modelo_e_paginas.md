# Modelo de dados e páginas do Radar CP

## Modelo estrela

| Tabela | Tipo | Chave | Observação |
|---|---|---|---|
| `fTitulo` | fato | `titulo_id` | 1 linha por título; colunas `dias_antecedencia`, `excecao_d3`, `dias_atraso` e `situacao` criadas no Power Query |
| `fRazao` | fato | `lancamento_id` | lançamentos contábeis; `titulo_id` vazio = ajuste manual |
| `dCalendario` | dimensão | `Data` | contínua (requisito da inteligência de tempo); marcada como **tabela de datas** |
| `dFornecedor` | dimensão | `fornecedor_id` | grupo de despesa e peso de análise |
| `dPA` | dimensão | `pa_id` | PA → regional |
| `dConta` | dimensão | `conta_sk` | **chave substituta** com vigência (o código reduzido foi reutilizado em 2025) |
| `dFaixaAging` | desconectada | — | faixas do aging (`DATATABLE` em `dax/medidas.dax`) |
| `_Medidas` | medidas | — | todas as medidas em uma tabela própria |

### Relacionamentos

- Todos **1:N** com filtro em **direção única** (dimensão → fato).
- `dCalendario[Data]` → `fTitulo[data_vencimento]` é o **ativo**. Os de pagamento e recebimento ficam **inativos** e são ligados nas medidas com `USERELATIONSHIP`. Assim, uma única tabela de datas atende três perspectivas sem criar ambiguidade.

### Problemas reais resolvidos neste modelo

| Sintoma | Causa | Solução |
|---|---|---|
| Segmentador de ano "não filtrava" alguns visuais | relacionamento inativo + filtro **bidirecional** criando caminho ambíguo entre fato e dimensão | só direção única; `USERELATIONSHIP` nas medidas que precisam de outra data |
| Variação mensal errada **em janeiro** | `DATEADD` respeitava o filtro do segmentador de ano e o dezembro anterior ficava de fora | `REMOVEFILTERS(dCalendario)` + janela calculada com `EOMONTH` |
| Comparativo anual somando contas diferentes | código reduzido reutilizado na reestruturação do plano de contas | dimensão de contas com chave substituta `conta_sk` e vigência |
| Comparação com o ano anterior "injusta" no meio do mês | ano anterior inteiro × ano atual parcial | acumulado anterior limitado ao mesmo dia (`EDATE(_ultimo, -12)`) |

## Páginas

| Página | Pergunta | Visuais principais |
|---|---|---|
| **Resumo** | Como está o contas a pagar hoje? | cartões (em aberto, vencido, % D+3, % pago em dia, YoY), valor por mês, top fornecedores, em aberto por regional |
| **Operação e metas** | A equipe está dentro das metas? | % exceção D+3 × meta por mês, % pago em dia, produtividade ponderada por colaborador |
| **Exceções D+3** | Quem envia documento em cima do vencimento? | matriz fornecedor × mês com `% Exceção D+3`, detalhe dos títulos |
| **Despesas ADM (macro/micro)** | Onde gastamos e como evolui? | tipo de despesa → conta (hierarquia), YoY acumulado, curva ABC |
| **Aging** | O que está vencido e há quanto tempo? | matriz regional × faixa (`dFaixaAging`) |
| **Conciliação** | Todo pagamento foi contabilizado? | pagos sem lançamento, diferença título × razão, lançamentos manuais |

Paleta: azul-petróleo `#003641` (principal), verde `#00AE9D` (positivo), vermelho `#C0392B` (alerta) e fundo `#F4F7F8`.
