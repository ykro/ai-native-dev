import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "TraderPulse API is running"}

def test_gamification_status():
    response = client.get("/api/v1/gamification/status")
    assert response.status_code == 200
    data = response.json()
    assert "investor_level" in data
    assert "analysis_points" in data
    assert "badges" in data

# Note: We are skipping live API tests to avoid key errors in CI/CD without real keys.
# In a real scenario, we would mock the services.
def test_stocks_endpoint_structure():
    # Calling with a dummy symbol. 
    # If API keys are invalid, it might return 500 or fallback data depending on implementation.
    # Our implementation returns 500 if key is missing/invalid for Alpha Vantage in strict mode,
    # but let's check if it handles it or if we should mock.
    # For now, let's just ensure the endpoint exists.
    assert app.url_path_for("get_stock_data", symbol="AAPL") == "/api/v1/stocks/AAPL"

def test_sentiment_endpoint_structure():
    assert app.url_path_for("get_sentiment", symbol="AAPL") == "/api/v1/sentiment/AAPL"
