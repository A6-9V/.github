import os
import pytest
from fastapi.testclient import TestClient

# Set environment variable before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"

from bridge.server import app, history

client = TestClient(app)
API_KEY = "test_secret_key"
HEADERS = {"X-API-KEY": API_KEY}

@pytest.fixture(autouse=True)
def clear_history():
    history.clear()
    yield

def test_get_history_limit_exceeding_size():
    # 1. Add some data to history
    data1 = {"symbol": "EURUSD", "price": 1.0850, "time": "2024-05-20 10:00:00"}
    data2 = {"symbol": "GBPUSD", "price": 1.2750, "time": "2024-05-20 10:05:00"}

    client.post("/ea/update", json=data1, headers=HEADERS)
    client.post("/ea/update", json=data2, headers=HEADERS)

    assert len(history) == 2

    # 2. Request history with limit greater than size
    response = client.get("/agent/history?limit=10", headers=HEADERS)

    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 2
    assert res_data[0]["symbol"] == "EURUSD"
    assert res_data[1]["symbol"] == "GBPUSD"

def test_get_history_normal_limit():
    # Add 5 items
    for i in range(5):
        data = {"symbol": f"SYM{i}", "price": 1.0 + i, "time": f"2024-05-20 10:0{i}:00"}
        client.post("/ea/update", json=data, headers=HEADERS)

    assert len(history) == 5

    # Request with limit 2
    response = client.get("/agent/history?limit=2", headers=HEADERS)

    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 2
    assert res_data[0]["symbol"] == "SYM3"
    assert res_data[1]["symbol"] == "SYM4"

def test_get_history_empty():
    assert len(history) == 0

    response = client.get("/agent/history?limit=10", headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == []

def test_get_history_default_limit():
    # Add 15 items
    for i in range(15):
        data = {"symbol": f"SYM{i}", "price": 1.0 + i, "time": "2024-05-20 10:00:00"}
        client.post("/ea/update", json=data, headers=HEADERS)

    response = client.get("/agent/history", headers=HEADERS)

    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 10  # Default limit is 10
    assert res_data[0]["symbol"] == "SYM5"
    assert res_data[9]["symbol"] == "SYM14"

def test_get_history_limit_zero():
    # Add some data
    data = {"symbol": "EURUSD", "price": 1.0850, "time": "2024-05-20 10:00:00"}
    client.post("/ea/update", json=data, headers=HEADERS)

    response = client.get("/agent/history?limit=0", headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == []

def test_get_history_limit_negative():
    # Add some data
    data = {"symbol": "EURUSD", "price": 1.0850, "time": "2024-05-20 10:00:00"}
    client.post("/ea/update", json=data, headers=HEADERS)

    response = client.get("/agent/history?limit=-5", headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == []
