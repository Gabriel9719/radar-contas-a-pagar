import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from referencia_e_mockup import carregar, medidas  # noqa: E402


def test_medidas_de_referencia_coerentes():
    b = carregar()
    m = medidas(b["t"], b["r"])
    assert 0 <= m["Valor Vencido"] <= m["Valor em Aberto"]
    assert 0 < m["% Exceção D+3 (recebidos em 2026)"] < 1
    assert m["Qtd Pagos sem Lançamento"] > 0          # problema plantado nos dados
    t = b["t"]
    assert t["titulo_id"].is_unique
    # toda conta usada está vigente no vencimento (dimensão com chave substituta correta)
    ok = (t["data_vencimento"] >= t["vigencia_inicio"]) & (t["data_vencimento"] <= t["vigencia_fim"])
    assert ok.all()
