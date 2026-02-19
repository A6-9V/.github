import os
import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("JULES_BRIDGE_API_KEY", "default_secret_key")
HEADERS = {"X-API-KEY": API_KEY}

def test_bridge():
    # 1. Check root
    print("Testing root...")
    res = requests.get(BASE_URL + "/")
    print(res.json())

    # 2. Simulate EA sending data
    print("\nSimulating EA data update...")
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00",
        "indicator_value": 45.5
    }
    res = requests.post(BASE_URL + "/ea/update", json=data, headers=HEADERS)
    print(res.json())

    # 3. Simulate Agent pushing a signal
    print("\nPushing signal from Agent...")
    signal = {
        "action": "BUY",
        "symbol": "EURUSD",
        "volume": 0.1,
        "stop_loss": 1.0800,
        "take_profit": 1.1000
    }
    res = requests.post(BASE_URL + "/agent/push-signal", json=signal, headers=HEADERS)
    print(res.json())

    # 4. Simulate EA polling for signal
    print("\nEA polling for signal...")
    res = requests.get(BASE_URL + "/ea/signal?symbol=EURUSD", headers=HEADERS)
    print(res.json())

    # 5. Verify queue is empty for that symbol
    print("\nEA polling again (should be null)...")
    res = requests.get(BASE_URL + "/ea/signal?symbol=EURUSD", headers=HEADERS)
    print(res.json())

    # 6. Test invalid API Key
    print("\nTesting invalid API Key...")
    res = requests.get(BASE_URL + "/agent/history", headers={"X-API-KEY": "wrong_key"})
    print(f"Status: {res.status_code}, Response: {res.json()}")

def test_history():
    print("\nTesting history retrieval...")
    res = requests.get(BASE_URL + "/agent/history?limit=5", headers=HEADERS)
    history = res.json()
    print(f"History length: {len(history)}")
    if len(history) > 0:
        print(f"Latest entry: {history[-1]}")
    else:
        print("History is empty!")

if __name__ == "__main__":
    try:
        test_bridge()
        test_history()
    except Exception as e:
        print(f"Error: {e}. Is the server running?")
