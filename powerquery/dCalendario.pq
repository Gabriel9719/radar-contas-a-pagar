// Calendário contínuo (exigência das funções de inteligência de tempo do DAX).
// Vai do primeiro dia do ano da data mais antiga até 31/12 do ano da mais recente,
// cobrindo emissão, recebimento, vencimento e pagamento.
let
    Datas  = List.Combine({fTitulo[data_emissao], fTitulo[data_vencimento], List.RemoveNulls(fTitulo[data_pagamento])}),
    Inicio = #date(Date.Year(List.Min(Datas)), 1, 1),
    Fim    = #date(Date.Year(List.Max(Datas)), 12, 31),
    Lista  = List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)),
    Tabela = Table.FromList(Lista, Splitter.SplitByNothing(), {"Data"}, null, ExtraValues.Error),
    Tipo   = Table.TransformColumnTypes(Tabela, {{"Data", type date}}),
    Ano    = Table.AddColumn(Tipo, "Ano", each Date.Year([Data]), Int64.Type),
    MesNum = Table.AddColumn(Ano, "MesNum", each Date.Month([Data]), Int64.Type),
    Mes    = Table.AddColumn(MesNum, "Mes", each Text.Proper(Date.ToText([Data], "MMM", "pt-BR")), type text),
    AnoMes = Table.AddColumn(Mes, "AnoMes", each Date.ToText([Data], "yyyy-MM"), type text),
    Trim   = Table.AddColumn(AnoMes, "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Data])), type text),
    DiaUtil = Table.AddColumn(Trim, "DiaUtil", each Date.DayOfWeek([Data], Day.Monday) < 5, type logical)
in
    DiaUtil
