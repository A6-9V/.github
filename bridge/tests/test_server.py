import os
import pytest
from fastapi.testclient import TestClient
import sys

# Add the parent directory to sys.path to import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the environment variable before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from server import app, signals_queue, history, TradingData

client = TestClient(app)
API_KEY = "test_secret_key"
HEADERS = {"X-API-KEY": API_KEY}

@pytest.fixture(autouse=True)
def clear_storage():
    """Clear the in-memory storage before each test."""
    signals_queue.clear()
    history.clear()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Jules Cloud Bridge is active" in response.json()["message"]

def test_ea_update_success():
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

def test_push_signal_success():
    signal = {
        "action": "BUY",
        "symbol": "GBPUSD",
        "volume": 0.2,
        "stop_loss": 1.2500,
        "take_profit": 1.2700
    }
    response = client.post("/agent/push-signal", json=signal, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "signal_queued"
    assert response.json()["queue_size"] == 1
    assert len(signals_queue) == 1

def test_get_signal_exists():
    # First, push a signal
    signal = {
        "action": "SELL",
        "symbol": "USDJPY",
        "volume": 0.5,
        "stop_loss": 157.00,
        "take_profit": 155.00
    }
    client.post("/agent/push-signal", json=signal, headers=HEADERS)

    # Then, poll for it
    response = client.get("/ea/signal?symbol=USDJPY", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "USDJPY"
    assert data["action"] == "SELL"

    # Verify it's removed from queue
    assert len(signals_queue) == 0

def test_get_signal_non_existent():
    """
    Test that polling for a symbol that has no signal in the queue returns null (None).
    This addresses the issue: Missing Test for Non-Existent Signal.
    """
    # Poll for a signal that was never pushed
    response = client.get("/ea/signal?symbol=NONEXISTENT", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None

def test_get_history():
    # Add some history
    for i in range(5):
        history.append(TradingData(
            symbol=f"SYM{i}",
            price=100.0 + i,
            time="2024-05-20 12:00:00"
        ))

    response = client.get("/agent/history?limit=3", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[-1]["symbol"] == "SYM4"

def test_invalid_api_key():
    response = client.get("/agent/history", headers={"X-API-KEY": "wrong"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"
