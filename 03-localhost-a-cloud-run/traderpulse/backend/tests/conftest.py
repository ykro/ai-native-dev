import pytest
from fastapi.testclient import TestClient

from traderpulse_api.config import ajustes
from traderpulse_api.main import app


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("TRADERPULSE_TOKEN", "")
    monkeypatch.setenv("SENTIMIENTO_FUENTE", "ejemplo")
    ajustes.cache_clear()
    yield TestClient(app)
    ajustes.cache_clear()
