from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from collections import deque, defaultdict
import uvicorn
import datetime
import os

app = FastAPI(title="Jules Cloud Bridge")

# Simple API Key Security
API_KEY = os.getenv("JULES_BRIDGE_API_KEY")
if not API_KEY:
    raise RuntimeError("JULES_BRIDGE_API_KEY environment variable is not set")
api_key_header = APIKeyHeader(name="X-API-KEY")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Models
class TradingData(BaseModel):
    symbol: str
    price: float
    time: str
    indicator_value: Optional[float] = None

class Signal(BaseModel):
    action: str  # BUY, SELL, CLOSE
    symbol: str
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

# In-memory storage
# Using defaultdict(deque) for O(1) lookup and pop from signal queue by symbol
signals_queue: defaultdict = defaultdict(deque)
# Track total number of signals across all symbols for O(1) size reporting
signals_count: int = 0
# Using deque with maxlen to prevent memory leaks from unbounded history growth
history: deque = deque(maxlen=10000)

@app.get("/")
async def root():
    return {
        "message": "Jules Cloud Bridge is active",
        "timestamp": datetime.datetime.now().isoformat(),
        "security": "Enabled (X-API-KEY required for data/signal endpoints)"
    }

@app.post("/ea/update", dependencies=[Depends(verify_api_key)])
async def ea_update(data: TradingData):
    history.append(data)
    print(f"[{data.time}] Received data for {data.symbol}: {data.price}")
    return {"status": "received"}

@app.get("/ea/signal", response_model=Optional[Signal], dependencies=[Depends(verify_api_key)])
async def get_signal(symbol: str):
    global signals_count
    # O(1) lookup and O(1) pop from the left of the deque
    if signals_queue.get(symbol) and len(signals_queue[symbol]) > 0:
        signal = signals_queue[symbol].popleft()
        signals_count -= 1
        return signal
    return None

@app.post("/agent/push-signal", dependencies=[Depends(verify_api_key)])
async def push_signal(signal: Signal):
    global signals_count
    # O(1) append to the specific symbol's queue
    signals_queue[signal.symbol].append(signal)
    signals_count += 1
    return {"status": "signal_queued", "queue_size": signals_count}

@app.get("/agent/history", dependencies=[Depends(verify_api_key)])
async def get_history(limit: int = 10):
    # Efficiently get the last 'limit' items from the deque without full conversion to list
    # deque indexed access is O(1) near the ends
    h_len = len(history)
    start = max(0, h_len - limit)
    return [history[i] for i in range(start, h_len)]

if __name__ == "__main__":
    print(f"Starting server with API_KEY: {API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
