from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import datetime
import os

app = FastAPI(title="Jules Cloud Bridge")

# Simple API Key Security
API_KEY = os.getenv("JULES_BRIDGE_API_KEY", "default_secret_key")
api_key_header = APIKeyHeader(name="X-API-KEY")

# IP Allow-listing
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")
ALLOWED_IPS = [ip.strip() for ip in ALLOWED_IPS if ip.strip()]

async def verify_ip(request: Request):
    if not ALLOWED_IPS:
        return

    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        print(f"Blocked request from unauthorized IP: {client_ip}")
        raise HTTPException(status_code=403, detail=f"IP {client_ip} not allowed")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Global dependencies for all protected routes
protected_dependencies = [Depends(verify_ip), Depends(verify_api_key)]

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
        "security": "Enabled (X-API-KEY and optional IP allow-listing)"
    }

@app.post("/ea/update", dependencies=protected_dependencies)
async def ea_update(data: TradingData):
    history.append(data)
    print(f"[{data.time}] Received data for {data.symbol}: {data.price}")
    return {"status": "received"}

@app.get("/ea/signal", response_model=Optional[Signal], dependencies=protected_dependencies)
async def get_signal(symbol: str):
    for i, signal in enumerate(signals_queue):
        if signal.symbol == symbol:
            return signals_queue.pop(i)
    return None

@app.post("/agent/push-signal", dependencies=protected_dependencies)
async def push_signal(signal: Signal):
    signals_queue.append(signal)
    return {"status": "signal_queued", "queue_size": len(signals_queue)}

@app.get("/agent/history", dependencies=protected_dependencies)
async def get_history(limit: int = 10):
    return history[-limit:]

if __name__ == "__main__":
    print(f"Starting server with API_KEY: {API_KEY}")
    if ALLOWED_IPS:
        print(f"IP Allow-listing enabled for: {ALLOWED_IPS}")
    else:
        print("IP Allow-listing disabled (allowing all IPs)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
