let
    Origem = fxLerCsv("dim_pa.csv"),
    Tipos  = Table.TransformColumnTypes(Origem, {{"pa_id", Int64.Type}, {"nome_pa", type text}, {"regional", type text}})
in
    Tipos
