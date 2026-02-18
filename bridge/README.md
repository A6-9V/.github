# Jules Cloud Bridge - Deployment and Setup Guide

This guide explains how to deploy the Jules Cloud Bridge on a VPS and connect it to a MetaTrader 5 Expert Advisor (EA).

## Prerequisites

1.  **VPS**: A Windows VPS (recommended for easiest MT5 setup) or Linux VPS with Wine.
2.  **Python 3.8+**: Installed on the VPS.
3.  **MetaTrader 5**: Installed on the VPS or a local machine.
4.  **Network Access**: Ensure the VPS has a public IP and the bridge port (default 8000) is open in the firewall.

## Step 1: Deploy the Bridge Server

1.  Copy `bridge/server.py` to your VPS.
2.  Install the required dependencies:
    ```bash
    pip install fastapi uvicorn pydantic
    ```
3.  Set the environment variable for your API Key (Required for security):
    ```bash
    export JULES_BRIDGE_API_KEY="your_secure_key"
    ```
4.  Run the server:
    ```bash
    python server.py
    ```
    *Note: For production, use a process manager like `pm2` or `systemd`.*

## Step 2: Configure MetaTrader 5

1.  Open MetaTrader 5.
2.  Go to **Tools -> Options**.
3.  Switch to the **Expert Advisors** tab.
4.  Check **"Allow WebRequest for listed URL"**.
5.  Add your VPS URL (e.g., `http://your-vps-ip:8000`) to the list.
6.  Click **OK**.

## Step 3: Install the EA Connector

1.  Open the MetaTrader 5 Data Folder (**File -> Open Data Folder**).
2.  Navigate to `MQL5/Experts`.
3.  Copy `bridge/ea_connector.mq5` into this folder.
4.  In the MT5 Navigator, right-click **Expert Advisors** and select **Refresh**.
5.  Drag **JulesConnector** onto a chart.
6.  In the "Inputs" tab:
    *   Set `InpServerUrl` to your bridge server address.
    *   Set `InpApiKey` to match the key set on the server.
7.  Ensure "Allow Algorithmic Trading" is enabled in the MT5 toolbar.

## Step 4: Interacting with Jules (AI Agent)

The bridge provides two main interaction points for the AI agent:

1.  **Market Data**: The AI can fetch recent market data received from the EA by calling:
    `GET /agent/history`
2.  **Trade Signals**: The AI can push new trading signals to the EA by calling:
    `POST /agent/push-signal`
    ```json
    {
      "action": "BUY",
      "symbol": "EURUSD",
      "volume": 0.1
    }
    ```

## Architecture Diagram

```
[ Jules (AI Agent) ] <----HTTP----> [ Bridge Server (FastAPI) ] <----HTTP----> [ MetaTrader 5 (EA) ]
```

This setup allows Jules to analyze market data in real-time and send execution commands to the VPS-hosted MT5 instance.
