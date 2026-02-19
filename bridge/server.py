from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
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
signals_queue: List[Signal] = []
history: List[TradingData] = []

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
    for i, signal in enumerate(signals_queue):
        if signal.symbol == symbol:
            return signals_queue.pop(i)
    return None

@app.post("/agent/push-signal", dependencies=[Depends(verify_api_key)])
async def push_signal(signal: Signal):
    signals_queue.append(signal)
    return {"status": "signal_queued", "queue_size": len(signals_queue)}

@app.get("/agent/history", dependencies=[Depends(verify_api_key)])
async def get_history(limit: int = 10):
    return history[-limit:]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "****"
    print(f"Starting server with API_KEY: {masked_key} on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
