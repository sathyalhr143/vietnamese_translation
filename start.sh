#!/bin/bash

# Vietnamese Translation Service - Streamlit Edition
# Quick start script for local development

set -e

echo "🚀 Vietnamese Translation Service (Streamlit)"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your OPENAI_API_KEY"
    echo ""
    echo "cp .env.example .env"
    exit 1
fi

# Activate virtual environment
if [ ! -d .venv ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

echo "📝 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting services..."
echo "- Backend API (FastAPI): http://localhost:8000"
echo "- Frontend UI (Streamlit): http://localhost:8501"
echo ""
echo "📌 Note: You need two terminal windows to run both services."
echo ""

# Check if user wants to start services
read -p "Start Streamlit frontend now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎬 Starting Streamlit..."
    streamlit run streamlit_app.py
else
    echo "Run 'streamlit run streamlit_app.py' to start the frontend"
    echo "Run 'python -m uvicorn src.app:app --reload' in another terminal for the backend"
fi
