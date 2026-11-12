import json
from pathlib import Path

from fastapi.testclient import TestClient

from traderpulse_api.config import ajustes
from traderpulse_api.main import app


def test_salud(cliente):
    r = cliente.get("/salud")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_panel_trae_numeros_como_numeros(cliente):
    r = cliente.get("/api/v1/panel/nvda")
    assert r.status_code == 200
    panel = r.json()
    cot = panel["cotizacion"]
    assert cot["simbolo"] == "NVDA"
    assert isinstance(cot["precio"], float)
    assert isinstance(cot["cambio_pct"], float)
    assert isinstance(cot["volumen"], int)
    assert len(panel["historico"]) == 22
    assert panel["sentimiento"]["sentimiento"] in {"alcista", "bajista", "neutral"}


def test_simbolo_desconocido_es_404_tipado(cliente):
    r = cliente.get("/api/v1/panel/ZZZZ")
    assert r.status_code == 404
    assert r.json() == {"codigo": "simbolo_desconocido", "mensaje": "No hay datos para 'ZZZZ'."}


def test_buscar_por_nombre(cliente):
    r = cliente.get("/api/v1/instrumentos", params={"q": "micro"})
    assert [i["simbolo"] for i in r.json()] == ["MSFT", "AMD"]


def test_cambio_pct_coincide_con_los_cierres(cliente):
    cot = cliente.get("/api/v1/cotizaciones/AAPL").json()
    hist = cliente.get("/api/v1/historico/AAPL").json()
    esperado = (hist[-1]["cierre"] - hist[-2]["cierre"]) / hist[-2]["cierre"] * 100
    assert cot["cambio_pct"] == round(esperado, 2)
    assert cot["precio"] == hist[-1]["cierre"]


def test_token_requerido_cuando_esta_configurado(monkeypatch):
    monkeypatch.setenv("TRADERPULSE_TOKEN", "secreto-de-prueba")
    ajustes.cache_clear()
    c = TestClient(app)
    assert c.get("/api/v1/panel/AAPL").status_code == 401
    assert c.get("/api/v1/panel/AAPL", headers={"X-TraderPulse-Token": "otro"}).status_code == 401
    ok = c.get("/api/v1/panel/AAPL", headers={"X-TraderPulse-Token": "secreto-de-prueba"})
    assert ok.status_code == 200
    assert c.get("/salud").status_code == 200  # Cloud Run y el juez la usan sin token
    ajustes.cache_clear()


def test_contrato_publicado_es_el_de_la_app():
    """Si alguien cambia un modelo sin regenerar el contrato, esta prueba lo detecta."""
    publicado = json.loads(
        (Path(__file__).parents[2] / "contrato" / "openapi.json").read_text(encoding="utf-8")
    )
    actual = app.openapi()
    actual = json.loads(json.dumps({**actual, "info": {**actual["info"], "version": "contrato"}}))
    assert publicado == actual
