from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict
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
# Using defaultdict(deque) for O(1) signal retrieval by symbol
signals_queue: Dict[str, deque] = defaultdict(deque)
# Using deque with maxlen to prevent unbounded memory growth
history: deque = deque(maxlen=1000)

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
    # Use .get() to avoid creating empty deques in the defaultdict for non-existent symbols
    symbol_queue = signals_queue.get(symbol)
    if symbol_queue:
        return symbol_queue.popleft()
    return None

@app.post("/agent/push-signal", dependencies=[Depends(verify_api_key)])
async def push_signal(signal: Signal):
    # O(1) append to the specific symbol's queue
    signals_queue[signal.symbol].append(signal)

    # Maintain backward compatibility by providing 'queue_size' (total across all symbols)
    # while also providing specific symbol info.
    total_size = sum(len(q) for q in signals_queue.values())

    return {
        "status": "signal_queued",
        "symbol": signal.symbol,
        "queue_size": total_size,
        "symbol_queue_size": len(signals_queue[signal.symbol])
    }

@app.get("/agent/history", dependencies=[Depends(verify_api_key)])
async def get_history(limit: int = 10):
    # deque doesn't support slicing, but converting to list for the last few items is efficient
    # as history is capped at 1000 items.
    history_list = list(history)
    return history_list[-limit:]

if __name__ == "__main__":
    print(f"Starting server with API_KEY: {API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
