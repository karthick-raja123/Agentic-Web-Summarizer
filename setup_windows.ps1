#!/usr/bin/env pwsh
# ============================================================================
# QUICKGLANCE SETUP SCRIPT - Windows PowerShell
# ============================================================================
# Run from: Visual-web-Agent directory
# Usage: ./setup_windows.ps1
# ============================================================================

Write-Host "============================================================================"
Write-Host "QUICKGLANCE SETUP - Windows PowerShell"
Write-Host "============================================================================"
Write-Host ""

# Step 1: Check Python
Write-Host "[STEP 1/5] Checking Python version..."
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://python.org"
    exit 1
}
Write-Host "OK - $pythonCheck" -ForegroundColor Green

# Step 2: Create venv
Write-Host ""
Write-Host "[STEP 2/5] Creating virtual environment..."
if (Test-Path ".venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item ".venv" -Recurse -Force
}
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Virtual environment created" -ForegroundColor Green

# Step 3: Activate venv
Write-Host ""
Write-Host "[STEP 3/5] Activating virtual environment..."
& ".venv/Scripts/Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Virtual environment activated" -ForegroundColor Green

# Step 4: Install dependencies
Write-Host ""
Write-Host "[STEP 4/5] Installing dependencies..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements_clean.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "OK - Dependencies installed" -ForegroundColor Green

# Step 5: Check .env
Write-Host ""
Write-Host "[STEP 5/5] Checking .env configuration..."
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from .env.clean..."
    Copy-Item ".env.clean" ".env"
    Write-Host "IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Yellow
    Write-Host "- GOOGLE_API_KEY: https://makersuite.google.com/app/apikey"
    Write-Host "- SERPER_API_KEY: https://serper.dev/api"
} else {
    Write-Host "OK - .env file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================================"
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Edit .env file and add your API keys"
Write-Host "2. Run: streamlit run streamlit_gemini_pipeline_fixed.py"
Write-Host ""
Write-Host "For details, see DEVELOPMENT_GUIDE.md"
Write-Host ""
