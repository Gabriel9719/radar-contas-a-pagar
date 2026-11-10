"""Gera a base FICTÍCIA de contas a pagar (jul/2024 a out/2026) em CSV.

Planta propositalmente problemas reais para as análises encontrarem:
  - 3 títulos duplicados (mesmo fornecedor, valor e emissão)
  - títulos pagos sem lançamento no razão e lançamentos sem título
  - um código reduzido de conta REUTILIZADO após a reestruturação do plano de contas em 2025
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

DATA_BASE = date(2026, 10, 31)
REGIONAIS = ["Norte", "Centro", "Sul"]
GRUPOS = {  # grupo de despesa -> peso de análise (complexidade do lançamento)
    "Segurança e transporte de valores": 2.0, "Limpeza e conservação": 2.0, "Jurídico": 1.5,
    "Obras e manutenção predial": 1.5, "Tecnologia": 1.0, "Aluguéis e condomínio": 1.0,
    "Material de expediente": 0.8, "Energia e água": 0.5, "Telecomunicações": 0.5,
}
FORNECEDORES = [
    ("PROTEGE VIGILÂNCIA LTDA", "Segurança e transporte de valores"), ("TRANSVALOR LTDA", "Segurança e transporte de valores"),
    ("LIMPA BEM SERVIÇOS LTDA", "Limpeza e conservação"), ("CONSERVA MAIS EIRELI", "Limpeza e conservação"),
    ("SILVA & SOUZA ADVOGADOS", "Jurídico"), ("MANUTENÇÃO ÔMEGA LTDA", "Obras e manutenção predial"),
    ("CONSTRUTORA PILAR LTDA", "Obras e manutenção predial"), ("TECNOLOGIA NUVEM AZUL S.A.", "Tecnologia"),
    ("SOFTWARE GESTÃO LTDA", "Tecnologia"), ("IMOBILIÁRIA CENTRAL LTDA", "Aluguéis e condomínio"),
    ("PAPELARIA TOTAL LTDA", "Material de expediente"), ("ENERGIA CENTRO-OESTE S.A.", "Energia e água"),
    ("SANEAMENTO ESTADUAL S.A.", "Energia e água"), ("FIBRA NET TELECOM LTDA", "Telecomunicações"),
    ("TELEFONIA BRASIL S.A.", "Telecomunicações"),
]
# conta_sk, cod_reduzido, conta_completa, descricao, tipo_despesa, vigencia_inicio, vigencia_fim
CONTAS = [
    (1, 4510, "8.1.7.03.00.01", "Água e energia", "Utilidades", "2020-01-01", "9999-12-31"),
    (2, 4512, "8.1.7.03.00.02", "Telefonia fixa (plano antigo)", "Comunicação", "2020-01-01", "2024-12-31"),
    (3, 4512, "8.1.7.36.00.09", "Limpeza terceirizada (plano novo)", "Serviços terceiros", "2025-01-01", "9999-12-31"),
    (4, 4520, "8.1.7.33.00.01", "Vigilância e segurança", "Serviços terceiros", "2020-01-01", "9999-12-31"),
    (5, 4530, "8.1.7.36.00.01", "Limpeza e conservação", "Serviços terceiros", "2020-01-01", "2024-12-31"),
    (6, 4540, "8.1.7.63.00.04", "Serviços técnicos especializados", "Serviços terceiros", "2020-01-01", "9999-12-31"),
    (7, 4550, "8.1.7.18.00.02", "Manutenção e conservação de bens", "Manutenção", "2020-01-01", "9999-12-31"),
    (8, 4560, "8.1.7.48.00.01", "Material de expediente", "Materiais", "2020-01-01", "9999-12-31"),
    (9, 4570, "8.1.7.12.00.01", "Aluguéis", "Ocupação", "2020-01-01", "9999-12-31"),
    (10, 4580, "8.1.7.03.00.05", "Telecomunicações (plano novo)", "Comunicação", "2025-01-01", "9999-12-31"),
]
CONTA_DO_GRUPO = {  # (vigente até 2024, vigente a partir de 2025)
    "Segurança e transporte de valores": (4, 4), "Limpeza e conservação": (5, 3), "Jurídico": (6, 6),
    "Obras e manutenção predial": (7, 7), "Tecnologia": (6, 6), "Aluguéis e condomínio": (9, 9),
    "Material de expediente": (8, 8), "Energia e água": (1, 1), "Telecomunicações": (2, 10),
}
USUARIOS = [("usr_ana", "Ana Souza", "Contas a Pagar"), ("usr_bruno", "Bruno Lima", "Contas a Pagar"),
            ("usr_carla", "Carla Dias", "Contas a Pagar"), ("usr_diego", "Diego Rocha", "Contas a Pagar"),
            ("usr_elisa", "Elisa Prado", "Controladoria")]


def escrever(pasta: Path, nome: str, cab: list[str], linhas: list) -> None:
    with (pasta / nome).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cab); w.writerows(linhas)


def main(saida: str = "data", seed: int = 2026) -> None:
    rng = random.Random(seed)
    pasta = Path(saida); pasta.mkdir(parents=True, exist_ok=True)

    pas = [(i, f"PA {i:02d}", REGIONAIS[i % 3]) for i in range(1, 16)]
    forn = []
    for i, (nome, grupo) in enumerate(FORNECEDORES, start=1):
        forn.append((i, nome, f"{rng.randint(10, 99)}.{rng.randint(100, 999)}.{rng.randint(100, 999)}/0001-{rng.randint(10, 99)}",
                     grupo, GRUPOS[grupo]))
    titulos, razao = [], []
    tid, lid = 100000, 1
    dia = date(2024, 7, 1)
    while dia <= DATA_BASE:
        for _ in range(rng.randint(3, 9) if dia.weekday() < 5 else 0):
            f = rng.choice(forn)
            grupo = f[3]
            emissao = dia - timedelta(days=rng.randint(0, 10))
            recebimento = dia
            venc = recebimento + timedelta(days=rng.choice([1, 2, 3, 5, 7, 10, 15, 20, 30]))
            conta = CONTA_DO_GRUPO[grupo][0 if venc.year < 2025 else 1]   # plano de contas vigente no vencimento
            base = {"Segurança e transporte de valores": 18000, "Limpeza e conservação": 12000, "Obras e manutenção predial": 9000,
                    "Aluguéis e condomínio": 6500, "Jurídico": 4500, "Tecnologia": 3800}.get(grupo, 900)
            valor = round(rng.lognormvariate(0, 0.45) * base, 2)
            pago = max(recebimento, venc + timedelta(days=rng.choice([0] * 10 + [-1, -2, 1, 2, 5, 9])))
            pagamento = pago if pago <= DATA_BASE else None
            usuario = rng.choice(USUARIOS[:4])[0]
            titulos.append([tid, f[0], rng.choice(pas)[0], conta, usuario, emissao, recebimento, venc, pagamento, valor])
            if pagamento and rng.random() > 0.01:                      # ~1% pago sem razão (planta)
                razao.append([lid, pagamento, conta, f"{f[1]} - ID CP {tid}", valor, tid]); lid += 1
            tid += 1
        dia += timedelta(days=1)
    # duplicidades plantadas
    for t in rng.sample(titulos[:-50], 3):
        titulos.append([tid, *t[1:]]); tid += 1
    # lançamentos no razão sem título (ajustes manuais) e um com valor divergente
    for _ in range(4):
        d = date(2026, rng.randint(1, 10), rng.randint(1, 28))
        razao.append([lid, d, 7, "AJUSTE MANUAL SEM TÍTULO", round(rng.uniform(100, 900), 2), None]); lid += 1
    alvo = next(r for r in razao if r[5] is not None and r[1] >= date(2026, 1, 1))
    alvo[4] = round(alvo[4] + 50, 2)

    escrever(pasta, "dim_pa.csv", ["pa_id", "nome_pa", "regional"], pas)
    escrever(pasta, "dim_fornecedor.csv", ["fornecedor_id", "razao_social", "cnpj", "grupo_despesa", "peso_analise"], forn)
    escrever(pasta, "dim_conta_contabil.csv", ["conta_sk", "cod_reduzido", "conta_completa", "descricao", "tipo_despesa",
                                               "vigencia_inicio", "vigencia_fim"], CONTAS)
    escrever(pasta, "dim_usuario.csv", ["usuario", "nome", "equipe"], USUARIOS)
    escrever(pasta, "fato_titulo.csv", ["titulo_id", "fornecedor_id", "pa_id", "conta_sk", "usuario_inclusao", "data_emissao",
                                        "data_recebimento", "data_vencimento", "data_pagamento", "valor"], titulos)
    escrever(pasta, "fato_razao.csv", ["lancamento_id", "data_lancamento", "conta_sk", "historico", "valor", "titulo_id"], razao)
    escrever(pasta, "parametro.csv", ["chave", "valor"], [("data_base", DATA_BASE.isoformat())])
    print(f"{len(titulos)} títulos, {len(razao)} lançamentos no razão -> {pasta}/")


if __name__ == "__main__":
    main()
