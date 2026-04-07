@echo off
REM ============================================================================
REM QUICKGLANCE SETUP SCRIPT - Windows (PowerShell)
REM ============================================================================
REM This script sets up the complete development environment
REM Run from: Visual-web-Agent directory
REM ============================================================================

echo ============================================================================
echo QUICKGLANCE SETUP - Windows
echo ============================================================================
echo.

REM Check Python version
echo [STEP 1/5] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo OK - Python installed

REM Create virtual environment
echo.
echo [STEP 2/5] Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Removing...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo OK - Virtual environment created

REM Activate venv
echo.
echo [STEP 3/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK - Virtual environment activated

REM Install dependencies
echo.
echo [STEP 4/5] Installing dependencies from requirements_clean.txt...
pip install --upgrade pip setuptools wheel
pip install -r requirements_clean.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK - Dependencies installed

REM Create .env file if it doesn't exist
echo.
echo [STEP 5/5] Checking .env configuration...
if not exist .env (
    echo Creating .env from .env.clean template...
    copy .env.clean .env
    echo IMPORTANT: Edit .env and add your API keys!
    echo - GOOGLE_API_KEY: https://makersuite.google.com/app/apikey
    echo - SERPER_API_KEY: https://serper.dev/api
    pause
)
if exist .env (
    echo OK - .env file found
)

echo.
echo ============================================================================
echo SETUP COMPLETE!
echo ============================================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Run: streamlit run streamlit_gemini_pipeline_fixed.py
echo.
echo For more details, see DEVELOPMENT_GUIDE.md or RUN_COMMANDS.txt
echo.
pause
