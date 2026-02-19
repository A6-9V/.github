import os
import pytest

# Set API Key for testing BEFORE importing app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"
API_KEY = "test_secret_key"
HEADERS = {"X-API-KEY": API_KEY}

from fastapi.testclient import TestClient
from bridge.server import app, signals_queue

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_queue():
    """Clear the signals queue before each test."""
    signals_queue.clear()
    yield

def test_push_signal_success():
    signal_data = {
        "action": "BUY",
        "symbol": "EURUSD",
        "volume": 0.1,
        "stop_loss": 1.0800,
        "take_profit": 1.1000
    }
    response = client.post("/agent/push-signal", json=signal_data, headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"status": "signal_queued", "queue_size": 1}
    assert len(signals_queue) == 1
    assert signals_queue[0].symbol == "EURUSD"

def test_push_signal_invalid_api_key():
    signal_data = {
        "action": "BUY",
        "symbol": "EURUSD",
        "volume": 0.1
    }
    response = client.post("/agent/push-signal", json=signal_data, headers={"X-API-KEY": "wrong_key"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_push_signal_missing_fields():
    # Missing 'symbol'
    signal_data = {
        "action": "BUY",
        "volume": 0.1
    }
    response = client.post("/agent/push-signal", json=signal_data, headers=HEADERS)
    assert response.status_code == 422

def test_push_signal_and_retrieve():
    # Push signal
    signal_data = {
        "action": "SELL",
        "symbol": "GBPUSD",
        "volume": 0.2
    }
    client.post("/agent/push-signal", json=signal_data, headers=HEADERS)

    # Retrieve signal
    response = client.get("/ea/signal?symbol=GBPUSD", headers=HEADERS)
    assert response.status_code == 200
    retrieved_signal = response.json()
    assert retrieved_signal["symbol"] == "GBPUSD"
    assert retrieved_signal["action"] == "SELL"
    assert retrieved_signal["volume"] == 0.2

    # Verify queue is empty after retrieval
    assert len(signals_queue) == 0
    response = client.get("/ea/signal?symbol=GBPUSD", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None
