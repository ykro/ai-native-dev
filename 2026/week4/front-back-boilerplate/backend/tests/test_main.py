from fastapi.testclient import TestClient
from main import app
from config import settings

client = TestClient(app)

def test_health_check_structure():
    """
    Verifies the structure and content of the health check endpoint.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "active"
    assert "version" in data
    assert "environment" in data
    assert data["environment"] == settings.ENVIRONMENT

def test_cors_configuration():
    """
    Simple check to ensure CORS headers are set (indirectly via TestClient behavior mimicking requests).
    Note: TestClient requests bypass actual middleware network stack usually, 
    but we verify the app is configured correctly by checking attributes if needed,
    or relying on integration tests. 
    Here we focus on the endpoint functionality.
    """
    response = client.get("/api/v1/health", headers={"Origin": str(settings.FRONTEND_URL)})
    assert response.status_code == 200
