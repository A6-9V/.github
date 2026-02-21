#!/bin/bash
set -e

# Define variables
KEY_URL="https://packages.cloud.google.com/apt/doc/apt-key.gpg"
KEYRING_DIR="/etc/apt/keyrings"
KEYRING_FILE="${KEYRING_DIR}/google-cloud-keyring.gpg"
REPO_FILE="/etc/apt/sources.list.d/google-cloud-sdk.list"

echo "Setting up Google Cloud APT repository..."

# Create keyrings directory if it doesn't exist
if [ ! -d "$KEYRING_DIR" ]; then
    echo "Creating ${KEYRING_DIR}..."
    sudo mkdir -p -m 755 "$KEYRING_DIR"
fi

# Download and de-armor the GPG key
echo "Downloading Google Cloud GPG key..."
curl -fsSL "$KEY_URL" | sudo gpg --dearmor --yes -o "$KEYRING_FILE"

# Add the repository to sources.list.d
echo "Adding Google Cloud SDK repository..."
echo "deb [signed-by=${KEYRING_FILE}] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee "$REPO_FILE" > /dev/null

# Update package lists
echo "Updating package lists..."
sudo apt-get update

echo "Google Cloud APT repository setup complete."
