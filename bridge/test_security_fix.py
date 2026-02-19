import os
import requests
import time
import subprocess

BASE_URL = "http://localhost:8000"
API_KEY = "security_test_key"
HEADERS = {"X-API-KEY": API_KEY}

def run_test():
    # Start the server with small limits
    env = os.environ.copy()
    env["JULES_BRIDGE_API_KEY"] = API_KEY
    env["MAX_HISTORY_SIZE"] = "5"
    env["MAX_SIGNALS_SIZE"] = "3"

    server_process = subprocess.Popen(
        ["python3", "bridge/server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(2)  # Wait for server to start

    try:
        # 1. Test History Limit
        print("Testing history limit...")
        for i in range(10):
            data = {
                "symbol": f"SYM{i}",
                "price": 1.0 + i,
                "time": f"2024-05-20 10:00:0{i}"
            }
            res = requests.post(BASE_URL + "/ea/update", json=data, headers=HEADERS)
            assert res.status_code == 200

        # Get history
        res = requests.get(BASE_URL + "/agent/history?limit=10", headers=HEADERS)
        history = res.json()
        print(f"History size: {len(history)}")
        assert len(history) == 5
        # Should contain SYM5 to SYM9
        symbols = [item["symbol"] for item in history]
        print(f"Symbols in history: {symbols}")
        assert "SYM9" in symbols
        assert "SYM4" not in symbols
        assert symbols == ["SYM5", "SYM6", "SYM7", "SYM8", "SYM9"]

        # 2. Test Signals Queue Limit
        print("\nTesting signals queue limit...")
        for i in range(5):
            signal = {
                "action": "BUY",
                "symbol": f"SIG{i}",
                "volume": 0.1
            }
            res = requests.post(BASE_URL + "/agent/push-signal", json=signal, headers=HEADERS)
            assert res.status_code == 200
            print(f"Queued SIG{i}, size: {res.json()['queue_size']}")

        # Verify current size in response (it should have been capped)
        # Wait, the push_signal response returns len(signals_queue)
        # deque(maxlen=3) will have len 3 after 3 pushes.

        # Check remaining signals
        # We can't easily list all signals, but we can poll for them.
        # Since it's a queue, SIG0, SIG1 should have been evicted by SIG3, SIG4.
        # SIG2, SIG3, SIG4 should remain.

        for i in range(2):
            res = requests.get(f"{BASE_URL}/ea/signal?symbol=SIG{i}", headers=HEADERS)
            assert res.json() is None
            print(f"SIG{i} correctly evicted")

        for i in range(2, 5):
            res = requests.get(f"{BASE_URL}/ea/signal?symbol=SIG{i}", headers=HEADERS)
            assert res.json()["symbol"] == f"SIG{i}"
            print(f"SIG{i} correctly retrieved")

        print("\nSecurity fix verification PASSED!")

    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_test()
