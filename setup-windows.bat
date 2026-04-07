@echo off
REM Quick deployment setup for Windows

echo ======================================
echo  QuickGlance Deployment Setup
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)

REM Step 1: Create virtual environment
echo [1/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists.
) else (
    python -m venv venv
    echo Virtual environment created.
)

REM Step 2: Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Step 3: Install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements-deploy.txt -q
echo Dependencies installed.

REM Step 4: Check .env file
echo [4/4] Checking configuration...
if exist .env (
    echo .env file found.
) else (
    if exist .env.template (
        copy .env.template .env
        echo Created .env from template. Please edit with your API keys!
    ) else (
        echo ERROR: .env and .env.template not found.
        exit /b 1
    )
)

echo.
echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env and add your API keys:
echo    - GEMINI_API_KEY (from https://makersuite.google.com/app/apikey)
echo    - SERPER_API_KEY (from https://serper.dev/dashboard)
echo.
echo 2. Start the backend (Terminal 1):
echo    python -m uvicorn app_fastapi:app --reload
echo.
echo 3. Start the frontend (Terminal 2):
echo    streamlit run streamlit_app_pdf.py
echo.
echo 4. Test:
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:8501
echo    API Docs: http://localhost:8000/docs
echo.
pause
