import pytest
import os
from fastapi.testclient import TestClient

# Mock the API key before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app, history

client = TestClient(app)
API_KEY = "test_secret_key"
HEADERS = {"X-API-KEY": API_KEY}

def setup_function():
    """Clear the history before each test."""
    history.clear()

def test_ea_update_success():
    """Test successful EA update with valid data and API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00",
        "indicator_value": 45.5
    }
    response = client.post("/ea/update", json=data, headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == {"status": "received"}
    assert len(history) == 1
    assert history[0].symbol == "EURUSD"
    assert history[0].price == 1.0850

def test_ea_update_invalid_api_key():
    """Test EA update with an invalid API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post("/ea/update", json=data, headers={"X-API-KEY": "wrong_key"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"
    assert len(history) == 0

def test_ea_update_missing_api_key():
    """Test EA update with a missing API key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post("/ea/update", json=data)

    assert response.status_code == 401

def test_ea_update_invalid_data():
    """Test EA update with missing required fields in data."""
    # Missing 'price' and 'time'
    data = {
        "symbol": "EURUSD"
    }
    response = client.post("/ea/update", json=data, headers=HEADERS)

    assert response.status_code == 422
    assert len(history) == 0

def test_ea_update_persistence():
    """Test that multiple updates are correctly persisted in history."""
    updates = [
        {"symbol": "EURUSD", "price": 1.0850, "time": "2024-05-20 10:00:00"},
        {"symbol": "GBPUSD", "price": 1.2500, "time": "2024-05-20 10:05:00"},
        {"symbol": "USDJPY", "price": 155.50, "time": "2024-05-20 10:10:00"}
    ]

    for data in updates:
        response = client.post("/ea/update", json=data, headers=HEADERS)
        assert response.status_code == 200

    assert len(history) == 3
    assert history[0].symbol == "EURUSD"
    assert history[1].symbol == "GBPUSD"
    assert history[2].symbol == "USDJPY"
