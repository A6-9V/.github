from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Deque, Dict
import uvicorn
import datetime
import os
from collections import deque, defaultdict

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
# Using deque with maxlen to prevent memory leaks and ensure O(1) appends
history: Deque[TradingData] = deque(maxlen=1000)
# Using defaultdict of deques for O(1) signal lookup and removal by symbol
signals_by_symbol: Dict[str, Deque[Signal]] = defaultdict(deque)

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
    # O(1) retrieval and removal
    if symbol in signals_by_symbol and signals_by_symbol[symbol]:
        return signals_by_symbol[symbol].popleft()
    return None

@app.post("/agent/push-signal", dependencies=[Depends(verify_api_key)])
async def push_signal(signal: Signal):
    # O(1) append
    signals_by_symbol[signal.symbol].append(signal)
    queue_size = sum(len(q) for q in signals_by_symbol.values())
    return {"status": "signal_queued", "queue_size": queue_size}

@app.get("/agent/history", dependencies=[Depends(verify_api_key)])
async def get_history(limit: int = 10):
    # Slicing a deque involves converting to list first if we want negative slicing
    # But since maxlen is small (1000), this is efficient enough.
    # Alternatively, we could use itertools.islice.
    h_list = list(history)
    return h_list[-limit:]

if __name__ == "__main__":
    print(f"Starting server with API_KEY: {API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
