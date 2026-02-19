import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure the bridge directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set API Key for testing before importing app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app, signals_queue, history

client = TestClient(app)
HEADERS = {"X-API-KEY": "test_secret_key"}

@pytest.fixture(autouse=True)
def clear_state():
    """Clear signals and history before each test to ensure isolation."""
    signals_queue.clear()
    history.clear()
    yield

def test_multiple_signals_fifo_same_symbol():
    # Push three signals for EURUSD
    signals = [
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.1},
        {"action": "SELL", "symbol": "EURUSD", "volume": 0.2},
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.3},
    ]

    for s in signals:
        response = client.post("/agent/push-signal", json=s, headers=HEADERS)
        assert response.status_code == 200

    # Retrieve signals one by one and check order
    for i in range(3):
        response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["volume"] == signals[i]["volume"]
        assert data["action"] == signals[i]["action"]

    # Queue should be empty now
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None

def test_multiple_signals_different_symbols():
    # Push signals for different symbols
    signals = [
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.1},
        {"action": "SELL", "symbol": "GBPUSD", "volume": 0.2},
        {"action": "BUY", "symbol": "USDJPY", "volume": 0.3},
    ]

    for s in signals:
        client.post("/agent/push-signal", json=s, headers=HEADERS)

    # Retrieve GBPUSD signal
    response = client.get("/ea/signal?symbol=GBPUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["symbol"] == "GBPUSD"
    assert response.json()["volume"] == 0.2

    # Retrieve EURUSD signal (verifies it was still in queue and correct)
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["symbol"] == "EURUSD"
    assert response.json()["volume"] == 0.1

    # Retrieve USDJPY signal
    response = client.get("/ea/signal?symbol=USDJPY", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["symbol"] == "USDJPY"

    # Queue should be empty
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.json() is None

def test_signal_queue_preserves_order_after_middle_pop():
    # Push 1, 2, 3
    signals = [
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.1}, # 0
        {"action": "SELL", "symbol": "GBPUSD", "volume": 0.2}, # 1
        {"action": "BUY", "symbol": "EURUSD", "volume": 0.3}, # 2
    ]

    for s in signals:
        client.post("/agent/push-signal", json=s, headers=HEADERS)

    # Pop GBPUSD (the middle one)
    response = client.get("/ea/signal?symbol=GBPUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["symbol"] == "GBPUSD"

    # Pop EURUSD - should get 0.1 first (verifies FIFO order preserved after middle pop)
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.json()["volume"] == 0.1

    # Pop EURUSD - should get 0.3 next
    response = client.get("/ea/signal?symbol=EURUSD", headers=HEADERS)
    assert response.json()["volume"] == 0.3

def test_unauthorized_access():
    response = client.get("/ea/signal?symbol=EURUSD", headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403
