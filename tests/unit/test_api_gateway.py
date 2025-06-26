import pytest
from fastapi.testclient import TestClient
from services.api_gateway.main import app

client = TestClient(app)

def test_health_check():
    """
    Tests the health check endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
