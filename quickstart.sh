#!/usr/bin/env bash
# Quick Start Script for Visual Web Agent
# Run: bash quickstart.sh

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║     QuickGlance - Setup Script                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -n "Checking Python version... "
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create virtual environment
echo -n "Creating virtual environment... "
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
echo -e "${GREEN}✓${NC}"

# Activate virtual environment
echo -n "Activating virtual environment... "
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
echo -e "${GREEN}✓${NC}"

# Install dependencies
echo -n "Installing dependencies... "
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC}"

# Check for .env file
echo -n "Checking configuration... "
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env not found${NC}"
    echo "Copying from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your API keys${NC}"
else
    echo -e "${GREEN}✓${NC}"
fi

# Create logs directory
mkdir -p logs

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run web UI:  streamlit run app.py"
echo "  3. Run CLI:     python main.py"
echo ""
echo "Documentation:"
echo "  - Architecture:  See ARCHITECTURE.md"
echo "  - Full guide:    See README_REFACTORED.md"
echo ""
