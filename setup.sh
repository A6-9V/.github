#!/bin/bash

# A6-9V Organization Setup Script
# This script installs common dependencies for algorithm trading and infrastructure.

echo "🚀 Starting A6-9V environment setup..."

# Update pip
echo "📦 Updating pip..."
python3 -m pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies from requirements.txt..."
    python3 -m pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Installing base dependencies..."
    python3 -m pip install ccxt pandas numpy python-dotenv scikit-learn
fi

echo "✅ Setup complete! You are ready to trade."
echo "📓 Reminder: Always read the NotebookLM at https://notebooklm.google.com/notebook/e8f4c29d-9aec-4d5f-8f51-2ca168687616 before starting work."
