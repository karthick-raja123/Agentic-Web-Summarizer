# ============================================================================
# TROUBLESHOOTING GUIDE - QuickGlance Streamlit
# ============================================================================
# Complete reference for common errors and exact fixes
# ============================================================================

## Table of Contents

1. [Environment & Installation](#environment--installation)
2. [API Keys & Configuration](#api-keys--configuration)
3. [Runtime Errors](#runtime-errors)
4. [Network & Timeout Issues](#network--timeout-issues)
5. [Debug Mode](#debug-mode)
6. [Clean Reinstall](#clean-reinstall)

---

## Environment & Installation

### Issue: "Python not found" or "python is not recognized"

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Causes:**
- Python not installed
- Python not in PATH
- Using wrong Python version

**Fix:**

**Option 1: Install Python (if not installed)**
- Download from: https://www.python.org/downloads/
- During installation: **CHECK "Add Python to PATH"**
- Verify: `python --version`

**Option 2: Use python3 explicitly**
```bash
python3 --version
python3 -m venv .venv
python3 -m pip install -r requirements_clean.txt
```

**Option 3: Check Python is in PATH**
```bash
# Windows
where python

# macOS/Linux
which python3
```

---

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Causes:**
- Dependencies not installed
- Venv not activated
- Wrong Python version

**Fix:**

```bash
# 1. Verify venv is ACTIVATED (should show in terminal prompt)
# Windows: (.venv) should appear
# If not, run:
.venv\Scripts\activate.bat  # Windows
source .venv/bin/activate   # macOS/Linux

# 2. Verify you're in correct directory
cd d:\Git\Visual Web Agent\Visual-web-Agent

# 3. Reinstall dependencies
pip install --upgrade pip
pip install -r requirements_clean.txt

# 4. Verify installation
pip list | grep streamlit
```

---

### Issue: "venv\Scripts\activate.bat not found"

**Symptoms:**
```
The system cannot find the path specified.
```

**Causes:**
- .venv directory doesn't exist
- Wrong directory
- Typo in command

**Fix:**

```bash
# 1. Check you're in the correct directory
cd d:\Git\Visual Web Agent\Visual-web-Agent
dir  # Should show .venv folder

# 2. If .venv doesn't exist, create it
python -m venv .venv

# 3. Try activating again
.venv\Scripts\activate.bat

# 4. Verify activation (should see (.venv) prefix)
```

---

## API Keys & Configuration

### Issue: "Configuration Error: GOOGLE_API_KEY is missing"

**Symptoms:**
```
❌ Configuration Error
❌ GOOGLE_API_KEY is missing or not configured in .env
```

**Causes:**
- .env file doesn't exist
- .env file is malformed
- API key contains placeholder text
- .env in wrong location

**Fix:**

```bash
# 1. Check .env exists in correct location
type .env  # Windows
cat .env   # macOS/Linux

# If doesn't exist, create it:
copy .env.clean .env  # Windows
cp .env.clean .env    # macOS/Linux

# 2. Edit .env and replace placeholders with REAL API keys
notepad .env          # Windows
nano .env             # macOS/Linux

# WRONG - Contains placeholder:
# GOOGLE_API_KEY=your_google_api_key_here

# CORRECT - Contains actual key:
# GOOGLE_API_KEY=AIzaSyD8-example-key-here

# 3. Save and restart Streamlit

# 4. Verify configuration:
python -c "from config import Config; print(Config.GOOGLE_API_KEY[:20])"
```

---

### Issue: "SERPER_API_KEY is missing"

**Symptoms:**
```
❌ SERPER_API_KEY is missing or not configured in .env
```

**Fix:**

```bash
# 1. Get your Serper API key from: https://serper.dev/api
# 2. Add to .env:
SERPER_API_KEY=your_actual_serper_key_here

# 3. Verify it was added correctly:
grep SERPER .env     # macOS/Linux
findstr SERPER .env  # Windows

# 4. Restart Streamlit

# 5. Verify:
python -c "from config import Config; print('✓' if Config.SERPER_API_KEY else '✗')"
```

---

### Issue: "Config loads but query fails with 401 Unauthorized"

**Symptoms:**
```
Serper API error: 401 Client Error: Unauthorized
```

**Causes:**
- API key is invalid
- API key has expired
- API key is for wrong service
- Account not activated

**Fix:**

```bash
# 1. Verify API key format (should start with specific characters)
# Google: Not starting with 'sk-' or 'your_'
# Serper: Not starting with 'x' or 'your_'

# 2. Test API key directly
curl -H "X-API-KEY: your_serper_key" https://google.serper.dev/search -d '{"q":"test"}'

# 3. If fails:
#    - Login to https://serper.dev
#    - Regenerate key
#    - Copy new key to .env
#    - Restart app

# 4. Verify new key works
python -c "from config import Config; print(Config.SERPER_API_KEY)"
```

---

## Runtime Errors

### Issue: "Failed to initialize Gemini"

**Symptoms:**
```
Error: Failed to initialize Gemini: invalid_request_error
```

**Causes:**
- Invalid API key format
- API key expired
- API not enabled

**Fix:**

```bash
# 1. Verify API key format (20+ characters, no spaces)
python -c "from config import Config; print(len(Config.GOOGLE_API_KEY), Config.GOOGLE_API_KEY[:10])"

# 2. Check API key doesn't have trailing spaces
# Edit .env and remove whitespace after key

# 3. Regenerate key from: https://makersuite.google.com/app/apikey

# 4. Enable Google Generative AI API:
#    - Go to: https://console.cloud.google.com/
#    - Enable Google Generative AI API
#    - Wait 1 minute
#    - Restart app
```

---

### Issue: "No results found for this query"

**Symptoms:**
- Query entered
- Search completes
- Message: "No results found"

**Causes:**
- Query too specific or malformed
- Serper API returned empty results
- API key invalid but didn't error

**Fix:**

```bash
# 1. Try simpler query
# ✗ "What are the long-term neurological effects of COVID-19 on elderly populations?"
# ✓ "COVID-19 neurological effects"

# 2. Enable Debug Mode:
#    - Go to sidebar "⚙️ Settings & Status"
#    - Check "🐛 Debug Mode"
#    - Try query again
#    - Check terminal for API response

# 3. If debug shows 0 URLs, API issue:
python test_search.py  # Run test script

# 4. Check Serper API status and quota:
#    - Go to: https://serper.dev/dashboard
#    - Verify account has remaining API calls
```

---

## Network & Timeout Issues

### Issue: "Serper API timeout (>15s)"

**Symptoms:**
```
Search failed: Serper API timeout (>15s)
```

**Causes:**
- Slow internet connection
- Serper API slow
- Firewall blocking
- Timeout too low

**Fix:**

```bash
# Option 1: Increase timeout in .env
SERPER_TIMEOUT=30  # Increase from 15 to 30

# Option 2: Check internet connection
ping google.com

# Option 3: Check firewall allows HTTPS
# If behind corporate firewall, may need proxy configuration

# Option 4: Try again (might be temporary)
```

---

### Issue: "Failed to parse JSON from API response"

**Symptoms:**
```
Summarization failed: Error parsing response
```

**Causes:**
- API returned error/html instead of JSON
- Network interrupted
- API rate limited

**Fix:**

```bash
# 1. Check API keys are valid (see API Keys section)

# 2. Enable debug mode to see raw response
#    - Check sidebar "Debug Mode"
#    - See actual API response

# 3. Check rate limits:
#    - Google: https://console.cloud.google.com/quotas
#    - Serper: https://serper.dev/dashboard

# 4. Wait and try again (might be temporary)
```

---

### Issue: "Scraping timeout on URLs"

**Symptoms:**
```
Timeout: https://example.com...
```

**Causes:**
- Website is slow
- Timeout too low
- Website blocks scraping

**Fix:**

```bash
# 1. Increase SCRAPE_TIMEOUT in .env
SCRAPE_TIMEOUT=15  # Increase from 10 to 15

# 2. Check which URL is slow
#    - Enable Debug Mode
#    - See which URL times out
#    - Try removing that domain in future

# 3. Some sites block scraping - this is expected
#    - App automatically skips failed URLs
#    - It should continue with other sources
```

---

## Debug Mode

### Enable Debug Mode

1. Run the Streamlit app
2. Look at left sidebar "⚙️ Settings & Status"
3. Check the box "🐛 Debug Mode"
4. Re-run your query
5. See debug output in terminal and browser

### What Debug Mode Shows

```
🐛 Serper returned 5 URLs
🐛 Scraped https://example.com... (8934 chars)
🐛 Scraped https://example2.com... (5123 chars)
🐛 Sending 14057 chars to Gemini
```

### Debug Tab in Results

After query completes with Debug Mode ON:
- Click "📊 Debug Info" tab
- See metrics:
  - URLs Found
  - Execution Time
  - Content Length
  - Configuration values

### Terminal Debug Output

Watch terminal where you ran `streamlit run`:
- API responses
- Error traces
- Configuration summary

---

## Clean Reinstall

If everything fails, do a complete clean reinstall:

```bash
# 1. Navigate to project
cd d:\Git\Visual Web Agent\Visual-web-Agent

# 2. Remove everything
rmdir /s /q .venv   # Windows: del %USERPROFILE%\AppData\Local\pip

# 3. Delete cache
rmdir /s /q __pycache__


# 4. Start fresh
python -m venv .venv
.venv\Scripts\activate.bat  # Windows

# 5. Fresh install
python -m pip install --upgrade pip
pip install -r requirements_clean.txt

# 6. Verify
python -c "import streamlit; print('OK')"

# 7. Verify config
python -c "from config import Config; valid, errors = Config.validate(); print('✓ Valid' if valid else f'✗ {errors}')"

# 8. Run
streamlit run streamlit_gemini_pipeline_fixed.py
```

---

## Verification Checklist

Before running app:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Venv created: `ls .venv` (or `dir .venv` Windows)
- [ ] Venv activated: (should see (.venv) in terminal)
- [ ] Dependencies installed: `pip list | grep streamlit`
- [ ] .env exists: `ls .env` (or `dir .env` Windows)
- [ ] .env has real API keys (not "your_api_key_here")
- [ ] Config validates: `python -c "from config import Config; print(Config.validate())"`
- [ ] Can import modules: `python -c "import streamlit; import google.generativeai"`

---

## Getting More Help

1. **Enable Debug Mode** - See what's actually happening
2. **Check Terminal Output** - Full error traces are logged here
3. **Check .env Configuration** - Most issues are API key related
4. **Review API Documentation**:
   - Google: https://ai.google.dev/
   - Serper: https://serper.dev/docs
5. **Common Issues Repository** - See RUN_COMMANDS.md

---

## Error Code Reference

| Error | Likelihood | Solution |
|-------|-----------|----------|
| ModuleNotFoundError | Very High | Activate venv, install deps |
| API 401 Unauthorized | High | Check API key in .env |
| Timeout | Medium | Increase timeout |
| No results | Medium | Try different query |
| Config validation failed | High | Edit .env with real keys |
| Permission denied | Low | Check file permissions |

---

**Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready

