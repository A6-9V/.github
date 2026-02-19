import os
import pytest
from fastapi.testclient import TestClient

# Set environment variable before importing the app
os.environ["JULES_BRIDGE_API_KEY"] = "test_secret_key"
from bridge.server import app

client = TestClient(app)

def test_root_accessible_without_key():
    """The root endpoint should be accessible without an API key."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Jules Cloud Bridge is active" in response.json()["message"]

def test_ea_update_with_valid_key():
    """Endpoints with Depends(verify_api_key) should work with a valid key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post(
        "/ea/update",
        json=data,
        headers={"X-API-KEY": "test_secret_key"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

def test_ea_update_with_invalid_key():
    """Endpoints with Depends(verify_api_key) should fail with an invalid key."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post(
        "/ea/update",
        json=data,
        headers={"X-API-KEY": "wrong_key"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

def test_ea_update_with_missing_key():
    """Endpoints with Depends(verify_api_key) should fail when the key is missing."""
    data = {
        "symbol": "EURUSD",
        "price": 1.0850,
        "time": "2024-05-20 10:00:00"
    }
    response = client.post("/ea/update", json=data)
    # FastAPI (or the version used here) returns 401 for missing APIKeyHeader
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_history_with_valid_key():
    response = client.get(
        "/agent/history",
        headers={"X-API-KEY": "test_secret_key"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_verify_api_key_function_directly():
    """Test the verify_api_key function directly."""
    from bridge.server import verify_api_key

    # Valid key
    result = await verify_api_key("test_secret_key")
    assert result == "test_secret_key"

    # Invalid key
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await verify_api_key("wrong_key")
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Invalid API Key"
