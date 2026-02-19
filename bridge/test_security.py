import os
import pytest
from fastapi.testclient import TestClient

# Set environment variable before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app

client = TestClient(app)

def test_root_no_auth_required():
    """Test that the root endpoint does not require an API key."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Jules Cloud Bridge is active" in response.json()["message"]

def test_ea_update_valid_api_key():
    """Test /ea/update with a valid API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00",
        "indicator_value": 45.5
    }
    response = client.post(
        "/ea/update",
        json=data,
        headers={"X-API-KEY": "test_secret_key"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

def test_ea_update_invalid_api_key():
    """Test /ea/update with an invalid API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post(
        "/ea/update",
        json=data,
        headers={"X-API-KEY": "wrong_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_ea_update_missing_api_key():
    """Test /ea/update with a missing API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post(
        "/ea/update",
        json=data
    )
    # FastAPI's APIKeyHeader returns 401 by default if the header is missing
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_agent_history_invalid_api_key():
    """Test /agent/history with an invalid API key."""
    response = client.get(
        "/agent/history",
        headers={"X-API-KEY": "wrong_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_push_signal_invalid_api_key():
    """Test /agent/push-signal with an invalid API key."""
    signal = {
        "action": "BUY",
        "symbol": "EURUSD",
        "volume": 0.1
    }
    response = client.post(
        "/agent/push-signal",
        json=signal,
        headers={"X-API-KEY": "wrong_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_get_signal_invalid_api_key():
    """Test /ea/signal with an invalid API key."""
    response = client.get(
        "/ea/signal?symbol=EURUSD",
        headers={"X-API-KEY": "wrong_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"
