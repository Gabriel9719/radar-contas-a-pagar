// Dimensão de contas com chave substituta (conta_sk) e vigência.
// O cod_reduzido foi reutilizado na reestruturação de 2025: NUNCA relacionar por ele.
let
    Origem = fxLerCsv("dim_conta_contabil.csv"),
    Tipos  = Table.TransformColumnTypes(Origem, {
        {"conta_sk", Int64.Type}, {"cod_reduzido", Int64.Type}, {"conta_completa", type text}, {"descricao", type text},
        {"tipo_despesa", type text}, {"vigencia_inicio", type date}, {"vigencia_fim", type date}}, "en-US"),
    Rotulo = Table.AddColumn(Tipos, "conta_rotulo", each [conta_completa] & " - " & [descricao], type text)
in
    Rotulo
