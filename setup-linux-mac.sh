#!/bin/bash

# Quick deployment setup for Linux/Mac

echo "======================================"
echo "  QuickGlance Deployment Setup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "Found Python $PYTHON_VERSION"

# Step 1: Create virtual environment
echo "[1/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Step 2: Activate virtual environment
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

# Step 3: Install dependencies
echo "[3/4] Installing dependencies..."
pip install -r requirements-deploy.txt -q
echo "Dependencies installed."

# Step 4: Check .env file
echo "[4/4] Checking configuration..."
if [ -f ".env" ]; then
    echo ".env file found."
else
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "Created .env from template. Please edit with your API keys!"
    else
        echo "ERROR: .env and .env.template not found."
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys:"
echo "   - GEMINI_API_KEY (from https://makersuite.google.com/app/apikey)"
echo "   - SERPER_API_KEY (from https://serper.dev/dashboard)"
echo ""
echo "2. Start the backend (Terminal 1):"
echo "   python -m uvicorn app_fastapi:app --reload"
echo ""
echo "3. Start the frontend (Terminal 2):"
echo "   streamlit run streamlit_app_pdf.py"
echo ""
echo "4. Test:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Run 'source venv/bin/activate' to activate venv in new terminal"
echo ""
