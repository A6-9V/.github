# Google Cloud Deployment Guide for Jules Cloud Bridge

This guide explains how to deploy the Jules Cloud Bridge to Google Cloud Run using the Cloud Shell Terminal.

## Prerequisites

1.  A Google Cloud Project.
2.  Billing enabled for the project.
3.  Google Cloud Shell access.

## Deployment Steps

### 1. Open Cloud Shell
Go to the [Google Cloud Console](https://console.cloud.google.com/) and click the **Activate Cloud Shell** button in the top right.

### 2. Clone the Repository
In the Cloud Shell terminal, clone your repository:
```bash
git clone <your-repo-url>
cd <repo-name>
```

### 3. Set Environment Variables
The bridge requires an API Key for security. Set it as a variable in your shell:
```bash
export JULES_BRIDGE_API_KEY="your_secure_api_key_here"
```

### 4. Deploy to Cloud Run
Run the following command to build and deploy the bridge:
```bash
gcloud run deploy jules-cloud-bridge \
  --source . \
  --region us-central1 \
  --set-env-vars JULES_BRIDGE_API_KEY=$JULES_BRIDGE_API_KEY \
  --allow-unauthenticated
```

*Note: The first time you run this, you may be prompted to enable the Cloud Run, Cloud Build, and Artifact Registry APIs.*

### 5. Verify Deployment
Once completed, the command will output a URL (e.g., `https://jules-cloud-bridge-xxxx-uc.a.run.app`).
You can verify it by visiting the URL in your browser. You should see a JSON response:
```json
{
  "message": "Jules Cloud Bridge is active",
  "timestamp": "...",
  "security": "Enabled (X-API-KEY required for data/signal endpoints)"
}
```

## Using with MetaTrader 5
When configuring the MT5 EA Connector:
- Use the Cloud Run URL as the `InpServerUrl`.
- Ensure you include `https://` in the URL.
- Match the `InpApiKey` with the `JULES_BRIDGE_API_KEY` you set during deployment.

## Troubleshooting
- **Permission Denied**: Ensure your account has the `Cloud Run Admin` and `Storage Admin` roles.
- **Port Error**: Cloud Run handles the port automatically via the `PORT` environment variable, which our server is configured to use.
