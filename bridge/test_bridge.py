import os
import requests
import json
import time

port = os.getenv("PORT", "8000")
BASE_URL = f"http://localhost:{port}"
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

if __name__ == "__main__":
    try:
        test_bridge()
    except Exception as e:
        print(f"Error: {e}. Is the server running?")
