# ============================================================================
# QUICKGLANCE - STREAMLIT SETUP & RUN GUIDE
# ============================================================================
# Complete step-by-step instructions for Windows, macOS, and Linux
# ============================================================================

## WINDOWS - Command Prompt (cmd.exe)

### Initial Setup (One Time)

```bash
# 1. Navigate to project directory
cd d:\Git\Visual Web Agent\Visual-web-Agent

# 2. Check Python version (must be 3.9+)
python --version

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
.venv\Scripts\activate.bat

# 5. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# 6. Install dependencies
pip install -r requirements_clean.txt

# 7. Create .env file
copy .env.clean .env

# 8. Edit .env and add your API keys
# Edit with any text editor:
# - GOOGLE_API_KEY=your_actual_google_key
# - SERPER_API_KEY=your_actual_serper_key
notepad .env
```

### Run Streamlit App

```bash
# 1. Activate venv (if not already active)
.venv\Scripts\activate.bat

# 2. Run Streamlit
streamlit run streamlit_gemini_pipeline_fixed.py

# 3. App opens at: http://localhost:8501
```

---

## WINDOWS - PowerShell

### Initial Setup (One Time)

```powershell
# 1. Navigate to project directory
cd d:\Git\Visual Web Agent\Visual-web-Agent

# 2. Check Python version
python --version

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
& ".venv/Scripts/Activate.ps1"

# 5. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# 6. Install dependencies
pip install -r requirements_clean.txt

# 7. Create .env file
Copy-Item .env.clean .env

# 8. Edit .env
notepad .env
```

### Run Streamlit App

```powershell
# 1. Activate venv
& ".venv/Scripts/Activate.ps1"

# 2. Run Streamlit
streamlit run streamlit_gemini_pipeline_fixed.py
```

---

## WINDOWS - Automated Setup

### Using Batch Script

```bash
# Simply double-click or run:
setup_windows.bat
```

### Using PowerShell Script

```powershell
# Run in PowerShell:
.\setup_windows.ps1
```

---

## macOS / Linux

### Initial Setup (One Time)

```bash
# 1. Navigate to project directory
cd /path/to/Visual-web-Agent

# 2. Check Python version (must be 3.9+)
python3 --version

# 3. Create virtual environment
python3 -m venv .venv

# 4. Activate virtual environment
source .venv/bin/activate

# 5. Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# 6. Install dependencies
pip install -r requirements_clean.txt

# 7. Create .env file
cp .env.clean .env

# 8. Edit .env and add API keys
nano .env
# OR
vi .env
```

### Run Streamlit App

```bash
# 1. Activate venv
source .venv/bin/activate

# 2. Run Streamlit
streamlit run streamlit_gemini_pipeline_fixed.py

# 3. App opens at: http://localhost:8501
```

---

## Configuration Validation

Before running the app, verify configuration:

```bash
# With venv activated, run:
python -c "from config import Config; valid, errors = Config.validate(); print('✓ Valid' if valid else f'✗ Errors: {errors}')"
```

Expected output: `✓ Valid`

If you see errors, check your .env file:
```bash
# View .env contents (on Windows)
type .env

# View .env contents (on macOS/Linux)
cat .env
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
# 1. Make sure venv is activated
# Windows: .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements_clean.txt

# 3. Verify installation
pip list | grep streamlit
```

### "ModuleNotFoundError: No module named 'config'"

**Solution:**
```bash
# Make sure you're in the Visual-web-Agent directory
cd d:\Git\Visual Web Agent\Visual-web-Agent

# Run streamlit from the correct location
streamlit run streamlit_gemini_pipeline_fixed.py
```

### "Configuration Error: GOOGLE_API_KEY is missing"

**Solution:**
```bash
# 1. Check .env exists
type .env  # Windows
cat .env   # macOS/Linux

# 2. Ensure .env has your actual API key (not placeholder)
# GOOGLE_API_KEY=your_actual_key_here  <- Replace this!

# 3. If .env is malformed, recreate it
del .env  # Windows: del .env
rm .env   # macOS/Linux: rm .env

copy .env.clean .env  # Windows
cp .env.clean .env    # macOS/Linux
```

### "requests.exceptions.Timeout: HTTPConnectionPool"

**Solution:**
```bash
# This is a network timeout, try:
# 1. Check internet connection
# 2. Try a different/simpler query
# 3. Increase timeout in .env
REQUEST_TIMEOUT=60  # Increase from 30
```

### "No results found for this query"

**Solution:**
- Try a different query
- Enable Debug Mode to see what URLs were searched
- Check Serper API key is valid

---

## Debug Mode

To enable detailed logging:

1. Open the app (streamlit running)
2. Click sidebar "⚙️ Settings & Status"
3. Check "🐛 Debug Mode"
4. Re-run your query
5. Terminal and UI will show:
   - URLs fetched
   - Content length
   - Token counts
   - API responses

---

## Important Files

| File | Purpose |
|------|---------|
| `.env` | API keys and configuration (PRIVATE - don't commit) |
| `.env.clean` | Template for .env (safe to commit) |
| `requirements_clean.txt` | Minimal production dependencies |
| `config.py` | Configuration management |
| `streamlit_gemini_pipeline_fixed.py` | Main Streamlit app |

---

## Environment Variables (.env)

Minimum required:
```
GOOGLE_API_KEY=your_actual_key
SERPER_API_KEY=your_actual_key
```

Optional (defaults provided):
```
REQUEST_TIMEOUT=30
SERPER_TIMEOUT=15
SCRAPE_TIMEOUT=10
MAX_CONTENT_PER_URL=10000
MAX_TOTAL_CONTENT=50000
DEBUG=false
```

---

## API Keys Setup

### Google Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy the key
4. Paste in `.env`: `GOOGLE_API_KEY=your_key_here`

### Serper Search API Key

1. Go to: https://serper.dev/api
2. Sign up (free tier available)
3. Copy your API key
4. Paste in `.env`: `SERPER_API_KEY=your_key_here`

---

## Testing the Setup

```bash
# With venv activated:

# 1. Test imports
python -c "import streamlit; import google.generativeai; print('✓ All imports OK')"

# 2. Test config
python -c "from config import Config; print(f'✓ Config loaded: Timeouts={Config.REQUEST_TIMEOUT}s')"

# 3. Test API keys
python -c "from config import Config; valid, errors = Config.validate(); print('✓ Valid' if valid else f'✗ {errors}')"

# 4. Run app
streamlit run streamlit_gemini_pipeline_fixed.py
```

---

## Common Issues Reference

| Issue | Command | Fix |
|-------|---------|-----|
| Venv not activating | Nothing shows in terminal | Check path: `cd Visual-web-Agent` first |
| Pip not found | "pip is not recognized" | Use `python -m pip` instead |
| Wrong Python version | `python --version` shows 2.7 | Use `python3` explicitly |
| Module import errors | `ModuleNotFoundError` | Reinstall: `pip install -r requirements_clean.txt` |
| API key errors | "Missing or not configured" | Edit .env with actual keys (not placeholders) |

---

## Support

For detailed error messages, enable Debug Mode in the app sidebar "⚙️ Settings & Status"

Check terminal output for full error traces and API responses.

