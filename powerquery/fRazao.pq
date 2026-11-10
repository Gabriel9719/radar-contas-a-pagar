let
    Origem = fxLerCsv("fato_razao.csv"),
    Tipos  = Table.TransformColumnTypes(Origem, {
        {"lancamento_id", Int64.Type}, {"data_lancamento", type date}, {"conta_sk", Int64.Type},
        {"historico", type text}, {"valor", Currency.Type}, {"titulo_id", Int64.Type}}, "en-US")
in
    Tipos
