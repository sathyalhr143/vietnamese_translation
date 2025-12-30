#!/bin/bash

# Quick Setup Script for Vietnamese Translation Service
# This script helps you get started quickly

echo "🚀 Vietnamese Translation Service - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  Virtual environment created at ./.venv"
else
    echo "  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate
echo "  Virtual environment activated"
echo ""

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "  pip upgraded"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt
echo "  Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo "  .env file created (please edit with your OpenAI API key)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir logs
    echo "✓ Created logs directory"
fi
echo ""

echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your OPENAI_API_KEY:"
echo "   nano .env"
echo ""
echo "2. Start the server:"
echo "   python -m uvicorn src.app:app --reload"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:8000"
echo ""
echo "4. Run tests to verify everything works:"
echo "   python test_api.py"
echo ""
echo "For more information, see:"
echo "  - README.md (overview)"
echo "  - API_GUIDE.md (API documentation)"
echo "  - RENDER_DEPLOYMENT.md (deployment guide)"
echo ""
