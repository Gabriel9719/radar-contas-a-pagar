let
    Origem = fxLerCsv("fato_titulo.csv"),
    Tipos  = Table.TransformColumnTypes(Origem, {
        {"titulo_id", Int64.Type}, {"fornecedor_id", Int64.Type}, {"pa_id", Int64.Type}, {"conta_sk", Int64.Type},
        {"usuario_inclusao", type text}, {"data_emissao", type date}, {"data_recebimento", type date},
        {"data_vencimento", type date}, {"data_pagamento", type date}, {"valor", Currency.Type}}, "en-US"),
    // Colunas calculadas na origem (Power Query) em vez de DAX: comprimem melhor e não pesam no modelo
    DiasAntecedencia = Table.AddColumn(Tipos, "dias_antecedencia",
        each Duration.Days([data_vencimento] - [data_recebimento]), Int64.Type),
    ExcecaoD3 = Table.AddColumn(DiasAntecedencia, "excecao_d3", each [dias_antecedencia] < 3, type logical),
    DiasAtraso = Table.AddColumn(ExcecaoD3, "dias_atraso",
        each if [data_pagamento] = null then null else Duration.Days([data_pagamento] - [data_vencimento]), Int64.Type),
    Situacao = Table.AddColumn(DiasAtraso, "situacao", each if [data_pagamento] = null then "Em aberto" else "Pago", type text)
in
    Situacao
