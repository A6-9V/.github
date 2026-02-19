import os
import pytest
from fastapi.testclient import TestClient

# Set environment variable before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app, history, signals_queue

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Jules Cloud Bridge is active" in response.json()["message"]

def test_ea_update_success():
    # Clear history for clean test
    history.clear()
    payload = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00",
        "indicator_value": 45.5
    }
    headers = {"X-API-KEY": "test_secret_key"}
    response = client.post("/ea/update", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "received"}
    assert len(history) == 1
    assert history[0].symbol == "EURUSD"

def test_ea_update_invalid_key():
    payload = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    headers = {"X-API-KEY": "wrong_key"}
    response = client.post("/ea/update", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_ea_update_missing_key():
    payload = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post("/ea/update", json=payload)
    # APIKeyHeader returns 401 if header is missing
    assert response.status_code == 401

def test_push_signal_success():
    signals_queue.clear()
    payload = {
        "action": "BUY",
        "symbol": "GBPUSD",
        "volume": 0.1,
        "stop_loss": 1.2500,
        "take_profit": 1.2700
    }
    headers = {"X-API-KEY": "test_secret_key"}
    response = client.post("/agent/push-signal", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "signal_queued"
    assert response.json()["queue_size"] == 1

def test_get_signal_success():
    signals_queue.clear()
    # Add a signal manually or via endpoint
    payload = {
        "action": "SELL",
        "symbol": "USDJPY",
        "volume": 0.2
    }
    headers = {"X-API-KEY": "test_secret_key"}
    client.post("/agent/push-signal", json=payload, headers=headers)

    response = client.get("/ea/signal?symbol=USDJPY", headers=headers)
    assert response.status_code == 200
    assert response.json()["symbol"] == "USDJPY"
    assert response.json()["action"] == "SELL"

    # Should be empty now
    response = client.get("/ea/signal?symbol=USDJPY", headers=headers)
    assert response.status_code == 200
    assert response.json() is None

def test_get_history():
    history.clear()
    headers = {"X-API-KEY": "test_secret_key"}
    # Add some data
    for i in range(15):
        client.post("/ea/update", json={
            "symbol": "EURUSD",
            "price": 1.0 + i/100,
            "time": f"2024-05-20 10:00:{i:02d}"
        }, headers=headers)

    response = client.get("/agent/history?limit=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    # The last one should be approx 1.14
    assert data[-1]["price"] == pytest.approx(1.14)

def test_invalid_trading_data():
    headers = {"X-API-KEY": "test_secret_key"}
    # Missing required field 'price'
    payload = {
        "symbol": "EURUSD",
        "time": "2024-05-20 10:00:00"
    }
    response = client.post("/ea/update", json=payload, headers=headers)
    assert response.status_code == 422 # Validation error
