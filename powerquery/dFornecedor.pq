let
    Origem = fxLerCsv("dim_fornecedor.csv"),
    Tipos  = Table.TransformColumnTypes(Origem, {
        {"fornecedor_id", Int64.Type}, {"razao_social", type text}, {"cnpj", type text},
        {"grupo_despesa", type text}, {"peso_analise", type number}}, "en-US")
in
    Tipos
