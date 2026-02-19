import pytest
from fastapi.testclient import TestClient
import os

# Set environment variable before importing app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app, signals_queue

client = TestClient(app)
API_KEY = "test_secret_key"
HEADERS = {"X-API-KEY": API_KEY}

@pytest.fixture(autouse=True)
def clear_queue():
    signals_queue.clear()
    yield
    signals_queue.clear()

def test_get_signal_happy_path():
    # Push a signal first
    signal_data = {
        "action": "BUY",
        "symbol": "EURUSD",
        "volume": 0.1,
        "stop_loss": 1.0800,
        "take_profit": 1.1000
    }
    client.post("/agent/push-signal", json=signal_data, headers=HEADERS)

    # Get the signal
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EURUSD"
    assert data["action"] == "BUY"

    # Verify it's removed
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None

def test_get_signal_multiple_signals():
    # Push multiple signals
    signals = [
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.1},
        {"action": "SELL", "symbol": "GBPUSD", "volume": 0.2},
        {"action": "SELL", "symbol": "EURUSD", "volume": 0.3},
    ]
    for s in signals:
        client.post("/agent/push-signal", json=s, headers=HEADERS)

    # Get EURUSD signal - should get the first one (BUY)
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["action"] == "BUY"
    assert response.json()["volume"] == 0.1

    # Get next EURUSD signal - should get the second one (SELL)
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["action"] == "SELL"
    assert response.json()["volume"] == 0.3

    # Get GBPUSD signal
    response = client.get("/ea/signal?symbol=GBPUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["action"] == "SELL"
    assert response.json()["symbol"] == "GBPUSD"

def test_get_signal_not_found():
    response = client.get("/ea/signal?symbol=NONEXISTENT", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None

def test_get_signal_unauthorized():
    response = client.get("/ea/signal?symbol=EURUSD", headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_get_signal_missing_key():
    response = client.get("/ea/signal?symbol=EURUSD")
    assert response.status_code == 401
