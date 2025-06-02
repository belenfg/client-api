from fastapi.testclient import TestClient
from fastapi import status

from main import app

def test_health_endpoint_returns_ok():
    """
    The /health endpoint should return HTTP 200 and expected payload keys.
    """
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Expect keys: status, service, timestamp
    assert "status" in data and data["status"] == "healthy"
    assert "service" in data
    assert "timestamp" in data
    # timestamp should be a string in ISO format
    assert isinstance(data["timestamp"], str)
