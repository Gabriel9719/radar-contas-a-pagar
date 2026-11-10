"""Calcula os valores de referência das principais medidas (para conferir o .pbix) e
desenha um mockup da página Resumo a partir dos dados fictícios.

Saídas: docs/valores_referencia.md e docs/mockup_resumo.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
AZUL, VERDE, VERM, CINZA, FUNDO = "#003641", "#00AE9D", "#C0392B", "#7F8C8D", "#F4F7F8"


def carregar() -> dict[str, pd.DataFrame]:
    d = RAIZ / "data"
    t = pd.read_csv(d / "fato_titulo.csv", parse_dates=["data_emissao", "data_recebimento", "data_vencimento", "data_pagamento"])
    t = (t.merge(pd.read_csv(d / "dim_fornecedor.csv"), on="fornecedor_id")
          .merge(pd.read_csv(d / "dim_pa.csv"), on="pa_id")
          .merge(pd.read_csv(d / "dim_conta_contabil.csv"), on="conta_sk"))
    t["dias_antecedencia"] = (t["data_vencimento"] - t["data_recebimento"]).dt.days
    t["excecao_d3"] = t["dias_antecedencia"] < 3
    t["dias_atraso"] = (t["data_pagamento"] - t["data_vencimento"]).dt.days
    return {"t": t, "r": pd.read_csv(d / "fato_razao.csv")}


def medidas(t: pd.DataFrame, r: pd.DataFrame) -> dict:
    base = t["data_pagamento"].max()
    aberto = t[t["data_pagamento"].isna()]
    rec26 = t[t["data_recebimento"].dt.year == 2026]
    pagos = t[t["data_pagamento"].notna()]
    ytd = lambda ano: t[(t["data_vencimento"] >= f"{ano}-01-01") & (t["data_vencimento"] <= base.replace(year=ano))]["valor"].sum()
    out_mes = t[t["data_vencimento"].dt.to_period("M") == "2026-10"]["valor"].sum()
    set_mes = t[t["data_vencimento"].dt.to_period("M") == "2026-09"]["valor"].sum()
    sem_razao = pagos[~pagos["titulo_id"].isin(r["titulo_id"].dropna())]
    return {
        "Data Base": base.strftime("%d/%m/%Y"),
        "Valor em Aberto": aberto["valor"].sum(),
        "Valor Vencido": aberto[aberto["data_vencimento"] < base]["valor"].sum(),
        "% Exceção D+3 (recebidos em 2026)": rec26["excecao_d3"].mean(),
        "% Pago em Dia (todos os pagos)": (pagos["dias_atraso"] <= 0).mean(),
        "Valor Total out/2026 (vencimento)": out_mes,
        "Var % MoM out/2026": out_mes / set_mes - 1,
        "Acumulado 2026 até a data base": ytd(2026),
        "Acumulado 2025 mesmo período": ytd(2025),
        "Var % YoY acumulado": ytd(2026) / ytd(2025) - 1,
        "Qtd Pagos sem Lançamento": len(sem_razao),
    }


def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def escrever_referencia(m: dict) -> None:
    linhas = ["# Valores de referência (dados fictícios)", "",
              "Calculados em Python (`scripts/referencia_e_mockup.py`) para conferir as medidas DAX depois de montar o `.pbix`.",
              "Se uma medida no Power BI não bater com esta tabela, o problema está no modelo (relacionamento, filtro ou contexto).", "",
              "| Medida | Valor esperado |", "|---|---|"]
    for k, v in m.items():
        if isinstance(v, str):
            s = v
        elif k.startswith(("%", "Var")):
            s = f"{v:.2%}".replace(".", ",")
        elif k.startswith("Qtd"):
            s = str(v)
        else:
            s = brl(v)
        linhas.append(f"| {k} | {s} |")
    (RAIZ / "docs/valores_referencia.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def mockup(t: pd.DataFrame, m: dict) -> None:
    fig = plt.figure(figsize=(16, 9), facecolor=FUNDO)
    fig.text(0.03, 0.94, "Radar CP", fontsize=26, fontweight="bold", color=AZUL)
    fig.text(0.03, 0.905, f"Contas a Pagar · data base {m['Data Base']} · dados fictícios · mockup gerado em Python",
             fontsize=11, color=CINZA)
    kpis = [("Em aberto", brl(m["Valor em Aberto"]), AZUL), ("Vencido", brl(m["Valor Vencido"]), VERM),
            ("Exceções D+3 (meta 15%)", f"{m['% Exceção D+3 (recebidos em 2026)']:.1%}".replace(".", ","),
             VERM if m["% Exceção D+3 (recebidos em 2026)"] > 0.15 else VERDE),
            ("Pago em dia", f"{m['% Pago em Dia (todos os pagos)']:.1%}".replace(".", ","), VERDE),
            ("YoY acumulado", f"{m['Var % YoY acumulado']:+.1%}".replace(".", ","), AZUL)]
    for i, (rot, val, cor) in enumerate(kpis):
        ax = fig.add_axes([0.03 + i * 0.19, 0.74, 0.175, 0.13]); ax.set_facecolor("white")
        ax.set_xticks([]); ax.set_yticks([]); [s.set_color("#DDE3E6") for s in ax.spines.values()]
        ax.text(0.06, 0.62, val, fontsize=19, fontweight="bold", color=cor, transform=ax.transAxes)
        ax.text(0.06, 0.22, rot, fontsize=11, color=CINZA, transform=ax.transAxes)

    t26 = t[t["data_vencimento"].dt.year == 2026]
    mensal = t26.groupby(t26["data_vencimento"].dt.month)["valor"].sum() / 1e3
    ax1 = fig.add_axes([0.04, 0.38, 0.55, 0.30]); ax1.set_facecolor("white")
    ax1.bar(mensal.index, mensal.values, color=AZUL, width=0.6)
    ax1.set_title("Valor por mês de vencimento (R$ mil) · 2026", loc="left", color=AZUL, fontweight="bold")
    ax1.set_xticks(range(1, 13)); ax1.set_xticklabels(["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"])
    ax1.spines[["top", "right"]].set_visible(False)

    rec = t[t["data_recebimento"].dt.year == 2026]
    d3 = rec.groupby(rec["data_recebimento"].dt.month)["excecao_d3"].mean() * 100
    ax2 = fig.add_axes([0.66, 0.38, 0.31, 0.30]); ax2.set_facecolor("white")
    ax2.plot(d3.index, d3.values, marker="o", color=VERDE); ax2.axhline(15, ls="--", color=VERM, lw=1)
    ax2.text(d3.index.min(), 15.6, "meta 15%", color=VERM, fontsize=9)
    ax2.set_title("% exceções D+3 por mês de recebimento", loc="left", color=AZUL, fontweight="bold")
    ax2.spines[["top", "right"]].set_visible(False); ax2.set_ylim(0, max(30, d3.max() + 5))
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    ax2.set_xticks(d3.index); ax2.set_xticklabels([meses[i - 1] for i in d3.index], fontsize=9)

    top = t26.groupby("razao_social")["valor"].sum().nlargest(6).sort_values() / 1e3
    ax3 = fig.add_axes([0.20, 0.05, 0.36, 0.26]); ax3.set_facecolor("white")
    ax3.barh(top.index, top.values, color=VERDE)
    ax3.set_title("Top fornecedores 2026 (R$ mil)", loc="left", color=AZUL, fontweight="bold")
    ax3.spines[["top", "right"]].set_visible(False); ax3.tick_params(labelsize=9)

    reg = t[t["data_pagamento"].isna()].groupby("regional")["valor"].sum() / 1e3
    ax4 = fig.add_axes([0.66, 0.05, 0.31, 0.26]); ax4.set_facecolor("white")
    ax4.bar(reg.index, reg.values, color=AZUL, width=0.5)
    ax4.set_title("Em aberto por regional (R$ mil)", loc="left", color=AZUL, fontweight="bold")
    ax4.spines[["top", "right"]].set_visible(False)
    fig.savefig(RAIZ / "docs/mockup_resumo.png", dpi=110, facecolor=FUNDO)


if __name__ == "__main__":
    b = carregar()
    m = medidas(b["t"], b["r"])
    escrever_referencia(m)
    mockup(b["t"], m)
    for k, v in m.items():
        print(f"{k}: {v}")
