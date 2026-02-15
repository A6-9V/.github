from fastapi.testclient import TestClient
from bridge.server import app, history, API_KEY
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_history():
    """Clear history before each test."""
    history.clear()
    yield

def test_get_history_empty():
    """Test getting history when it's empty."""
    response = client.get("/agent/history", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200
    assert response.json() == []

def test_get_history_with_data():
    """Test getting history with some data."""
    # Add some data to history
    history.append({"symbol": "EURUSD", "price": 1.0850, "time": "2024-05-20 10:00:00"})
    history.append({"symbol": "GBPUSD", "price": 1.2500, "time": "2024-05-20 10:05:00"})

    response = client.get("/agent/history", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["symbol"] == "EURUSD"
    assert data[1]["symbol"] == "GBPUSD"

def test_get_history_limit():
    """Test the limit parameter."""
    for i in range(15):
        history.append({"symbol": "EURUSD", "price": 1.0 + i, "time": f"2024-05-20 10:{i:02d}:00"})

    # Default limit is 10
    response = client.get("/agent/history", headers={"X-API-KEY": API_KEY})
    assert len(response.json()) == 10

    # Custom limit
    response = client.get("/agent/history?limit=5", headers={"X-API-KEY": API_KEY})
    assert len(response.json()) == 5
    # Last 5 prices: 11.0, 12.0, 13.0, 14.0, 15.0
    assert response.json()[0]["price"] == 11.0

def test_get_history_large_limit():
    """Test limit larger than history size."""
    history.append({"symbol": "EURUSD", "price": 1.0, "time": "2024-05-20 10:00:00"})

    response = client.get("/agent/history?limit=100", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_history_authentication():
    """Test authentication for the history endpoint."""
    # No API Key
    response = client.get("/agent/history")
    assert response.status_code == 403

    # Invalid API Key
    response = client.get("/agent/history", headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403

    # Valid API Key
    response = client.get("/agent/history", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200
