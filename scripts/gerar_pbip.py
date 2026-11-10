"""Gera pbip/RadarCP.pbip a partir de powerquery/*.pq e dax/medidas.dax.

    python scripts/gerar_pbip.py --pasta-dados "C:\\Projetos\\radar-contas-a-pagar\\data\\"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pbip_lib import (coluna, escrever_pbip, ler_medidas_dax, pagina, relacao, tabela_calculada, tabela_m,  # noqa: E402
                      tabela_medidas, visual)

RAIZ = Path(__file__).resolve().parents[1]


def pq(nome: str) -> str:
    """Conteúdo da consulta M, sem as linhas de comentário iniciais."""
    linhas = (RAIZ / "powerquery" / f"{nome}.pq").read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in linhas if not l.lstrip().startswith("//"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta-dados", default=r"C:\Projetos\radar-contas-a-pagar\data" + "\\")
    a = ap.parse_args()
    caminho = a.pasta_dados.replace("\\", "\\\\")

    expressoes = [
        {"name": "PastaDados", "kind": "m",
         "expression": f'"{caminho}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'},
        {"name": "fxLerCsv", "kind": "m", "expression": pq("01_fxLerCsv").split("\n")},
    ]
    I, S, D, N, B, F = "int64", "string", "dateTime", "decimal", "boolean", "double"
    tabelas = [
        tabela_m("fTitulo", pq("fTitulo"), [
            coluna("titulo_id", I), coluna("fornecedor_id", I, isHidden=True), coluna("pa_id", I, isHidden=True),
            coluna("conta_sk", I, isHidden=True), coluna("usuario_inclusao", S), coluna("data_emissao", D),
            coluna("data_recebimento", D), coluna("data_vencimento", D), coluna("data_pagamento", D), coluna("valor", N),
            coluna("dias_antecedencia", I), coluna("excecao_d3", B), coluna("dias_atraso", I), coluna("situacao", S)]),
        tabela_m("fRazao", pq("fRazao"), [
            coluna("lancamento_id", I), coluna("data_lancamento", D), coluna("conta_sk", I, isHidden=True),
            coluna("historico", S), coluna("valor", N), coluna("titulo_id", I)]),
        tabela_m("dFornecedor", pq("dFornecedor"), [
            coluna("fornecedor_id", I, isHidden=True), coluna("razao_social", S), coluna("cnpj", S),
            coluna("grupo_despesa", S), coluna("peso_analise", F)]),
        tabela_m("dPA", pq("dPA"), [coluna("pa_id", I, isHidden=True), coluna("nome_pa", S), coluna("regional", S)]),
        tabela_m("dConta", pq("dConta"), [
            coluna("conta_sk", I, isHidden=True), coluna("cod_reduzido", I), coluna("conta_completa", S),
            coluna("descricao", S), coluna("tipo_despesa", S), coluna("vigencia_inicio", D), coluna("vigencia_fim", D),
            coluna("conta_rotulo", S)]),
        tabela_m("dCalendario", pq("dCalendario"), [
            coluna("Data", D, isKey=True), coluna("Ano", I), coluna("MesNum", I, isHidden=True),
            coluna("Mes", S, sortByColumn="MesNum"), coluna("AnoMes", S), coluna("Trimestre", S), coluna("DiaUtil", B)],
            dataCategory="Time"),
        tabela_calculada("dFaixaAging",
                         'DATATABLE("Faixa", STRING, "Ordem", INTEGER, "Min", INTEGER, "Max", INTEGER, '
                         '{{"A vencer", 1, -99999, 0}, {"1-30", 2, 1, 30}, {"31-60", 3, 31, 60}, '
                         '{"61-90", 4, 61, 90}, {"> 90", 5, 91, 99999}})',
                         [("Faixa", S), ("Ordem", I), ("Min", I), ("Max", I)]),
        tabela_medidas(ler_medidas_dax(RAIZ / "dax/medidas.dax")),
    ]
    for c in tabelas[6]["columns"]:
        if c["name"] == "Faixa":
            c["sortByColumn"] = "Ordem"
    relacoes = [
        relacao("fTitulo", "fornecedor_id", "dFornecedor", "fornecedor_id"),
        relacao("fTitulo", "pa_id", "dPA", "pa_id"),
        relacao("fTitulo", "conta_sk", "dConta", "conta_sk"),
        relacao("fRazao", "conta_sk", "dConta", "conta_sk"),
        relacao("fTitulo", "data_vencimento", "dCalendario", "Data"),
        relacao("fTitulo", "data_pagamento", "dCalendario", "Data", ativo=False),
        relacao("fTitulo", "data_recebimento", "dCalendario", "Data", ativo=False),
    ]
    M = "_Medidas"
    card = lambda x, y, med, tit: visual("card", x, y, 240, 110, {"Values": [(M, med, True)]}, tit)
    resumo = pagina("Resumo", [
        visual("slicer", 1040, 10, 220, 60, {"Values": [("dCalendario", "Ano", False)]}, "Ano"),
        card(20, 80, "Valor em Aberto", "Em aberto"), card(270, 80, "Valor Vencido", "Vencido"),
        card(520, 80, "% Exceção D+3", "Exceções D+3"), card(770, 80, "% Pago em Dia", "Pago em dia"),
        card(1020, 80, "Var % YoY (acumulado)", "YoY acumulado"),
        visual("clusteredColumnChart", 20, 210, 780, 240, {"Category": [("dCalendario", "AnoMes", False)],
                                                          "Y": [(M, "Valor Total", True)]}, "Valor por mês de vencimento"),
        visual("lineChart", 820, 210, 440, 240, {"Category": [("dCalendario", "AnoMes", False)],
                                               "Y": [(M, "% Exceção D+3", True)]}, "% exceções D+3"),
        visual("clusteredBarChart", 20, 470, 780, 230, {"Category": [("dFornecedor", "razao_social", False)],
                                                       "Y": [(M, "Valor Total", True)]}, "Valor por fornecedor"),
        visual("clusteredColumnChart", 820, 470, 440, 230, {"Category": [("dPA", "regional", False)],
                                                          "Y": [(M, "Valor em Aberto", True)]}, "Em aberto por regional"),
    ], 0)
    excecoes = pagina("Exceções D+3", [
        visual("tableEx", 20, 20, 1240, 680, {"Values": [("dFornecedor", "razao_social", False), (M, "Qtd Recebidos", True),
                                                        (M, "Qtd Exceções D+3", True), (M, "% Exceção D+3", True),
                                                        (M, "Status Meta D+3", True)]}, "Exceções D+3 por fornecedor"),
    ], 1)
    abc = pagina("Despesas e ABC", [
        visual("tableEx", 20, 20, 620, 680, {"Values": [("dFornecedor", "razao_social", False), (M, "Valor Total", True),
                                                       (M, "% Acumulado ABC", True), (M, "Classe ABC", True)]}, "Curva ABC"),
        visual("tableEx", 660, 20, 600, 680, {"Values": [("dConta", "tipo_despesa", False), (M, "Valor Acumulado no Ano", True),
                                                        (M, "Valor Acumulado Ano Anterior", True), (M, "Var % YoY (acumulado)", True)]},
               "Comparativo anual por tipo de despesa"),
    ], 2)
    aging = pagina("Aging e conciliação", [
        visual("tableEx", 20, 20, 600, 300, {"Values": [("dFaixaAging", "Faixa", False), (M, "Valor Aging", True)]}, "Aging do em aberto"),
        card(660, 20, "Qtd Pagos sem Lançamento", "Pagos sem lançamento"),
        card(920, 20, "Diferença Título x Razão", "Diferença título x razão"),
        visual("tableEx", 20, 340, 1240, 360, {"Values": [("dCalendario", "AnoMes", False), (M, "Valor Pago", True),
                                                        (M, "Valor Razão", True)]}, "Pago x contabilizado por mês"),
    ], 3)
    arq = escrever_pbip(RAIZ / "pbip", "RadarCP", tabelas, relacoes, expressoes, [resumo, excecoes, abc, aging])
    print(f"Projeto gerado: {arq}")


if __name__ == "__main__":
    main()
