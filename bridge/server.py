from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict
from collections import deque, defaultdict
import itertools
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

# In-memory storage optimized for performance
# history: deque for O(1) append and O(limit) slice access
history: deque = deque(maxlen=10000)
# signals_by_symbol: defaultdict(deque) for O(1) symbol lookup and O(1) popleft
signals_by_symbol: Dict[str, deque] = defaultdict(deque)
signals_count: int = 0

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
    if signals_by_symbol[symbol]:
        signals_count -= 1
        return signals_by_symbol[symbol].popleft()
    return None

@app.post("/agent/push-signal", dependencies=[Depends(verify_api_key)])
async def push_signal(signal: Signal):
    global signals_count
    signals_by_symbol[signal.symbol].append(signal)
    signals_count += 1
    return {"status": "signal_queued", "queue_size": signals_count}

@app.get("/agent/history", dependencies=[Depends(verify_api_key)])
async def get_history(limit: int = 10):
    # Optimized for O(limit) access
    return list(itertools.islice(reversed(history), limit))[::-1]

if __name__ == "__main__":
    print(f"Starting server with API_KEY: {API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
