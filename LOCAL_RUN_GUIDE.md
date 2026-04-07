# 🚀 LOCAL RUN GUIDE - QuickGlance

Complete step-by-step instructions to run QuickGlance locally with full testing.

---

## 📋 STEP 1: PREREQUISITES

### System Requirements
- **Python**: 3.9+ (check with `python --version`)
- **OS**: Windows, macOS, Linux
- **Disk Space**: 500MB
- **Internet**: Required (API calls to Gemini + Serper)

### Required API Keys (Get Free)
1. **Google Gemini API**
   - Go to: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy and save the key

2. **Serper Search API**
   - Go to: https://serper.dev
   - Sign up (free tier available)
   - Get your API key from dashboard
   - Copy and save the key

---

## 🔧 STEP 2: SETUP ENVIRONMENT

### Windows PowerShell / Command Prompt

```powershell
# 1. Navigate to project directory
cd "d:\Git\Visual Web Agent\Visual-web-Agent"

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If you get "cannot be loaded because running scripts is disabled..."
# Run this ONCE:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then retry activation
```

### macOS / Linux

```bash
# 1. Navigate to project directory
cd ~/path/to/Visual-web-Agent

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate
```

### Verify Activation
You should see `(.venv)` at the start of your terminal prompt.

---

## 📦 STEP 3: INSTALL DEPENDENCIES

```powershell
# With virtual environment activated
pip install --upgrade pip

# Install clean requirements
pip install -r requirements_clean.txt

# Verify installation
pip list | findstr "google\|langchain\|streamlit\|requests"
```

---

## 🔐 STEP 4: SETUP .ENV FILE

### Option A: Automatic (Recommended)

```powershell
# Copy template
Copy-Item ".env.clean" ".env"

# Edit .env with your API keys
notepad .env
```

### Option B: Manual

1. Copy `.env.clean` to `.env`
2. Open `.env` in any text editor
3. Replace these lines:
   ```
   GOOGLE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
4. Save and close

### Verify Configuration

```powershell
# Test configuration loading
python config.py

# Should output:
# ✅ All configurations valid!
```

---

## 🧪 STEP 5: VALIDATE ENVIRONMENT BEFORE RUNNING

```powershell
# Run configuration validator
python -c "from config import Config; is_valid, errors = Config.validate(); print('✅ Valid' if is_valid else f'❌ Errors: {errors}')"

# Check all dependencies work
python -c "import google.generativeai; import requests; print('✅ All imports successful')"
```

---

## ▶️ STEP 6: RUN CLI VERSION

### Basic Usage

```powershell
# Run with query as argument
python agentic_browser_pipeline_fixed.py "machine learning basics"

# Or interactive (will prompt for query)
python agentic_browser_pipeline_fixed.py
```

### Sample Output

```
======================================================================
CONFIGURATION VALIDATION
======================================================================
✅ Google API Key: Configured
✅ Serper API Key: Configured
✅ Timeouts: Configured
✅ All required settings valid

======================================================================
QUICKGLANCE - MULTI-AGENT RESEARCH PIPELINE
======================================================================

✍️  INITIALIZE NODE: Initializing Gemini...
✅ Gemini initialized

Query: machine learning basics

🔍 SEARCH NODE: Searching for 'machine learning basics'
  → Sending request to Serper API (timeout: 15s)
  ✓ Found 5 URLs
    1. https://www.example.com/ml-intro
    2. https://www.example.com/ml-guide
    ...

📄 BROWSE NODE: Scraping 5 URLs
  → Scraping: https://www.example.com/ml-intro...
    ✓ Scraped 8945 chars
  ...
  ✓ Scraped 4 URLs, Failed: 1
  ✓ Total content: 29384 chars

✍️  SUMMARIZE NODE: Generating summary with Gemini
  → Content length: 29384 chars
  ✓ Summary generated (487 chars)

======================================================================
RESULTS
======================================================================

⏱️  Execution Time: 12.45s

📌 URLs Found: 5
   1. https://www.example.com/ml-intro
   2. https://www.example.com/ml-guide
   ...

📄 Content Scraped: 29384 characters

📋 SUMMARY
----------------------------------------------------------------------
• Machine Learning is a subset of AI that enables systems to learn
  from data without explicit programming
• Key types include supervised, unsupervised, and reinforcement learning
• Applications span computer vision, NLP, recommendations, and analytics
• Deep learning uses neural networks with multiple layers
• Common challenges include data quality, overfitting, and resources
----------------------------------------------------------------------

======================================================================
```

---

## 🖥️ STEP 7: RUN STREAMLIT VERSION

### Start Streamlit Server

```powershell
# Run Streamlit app
streamlit run streamlit_gemini_pipeline_fixed.py

# Or specify port
streamlit run streamlit_gemini_pipeline_fixed.py --server.port 8501
```

### Access in Browser

Once running, you should see:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open `http://localhost:8501` in your browser.

### Using Streamlit UI

1. **Enter Query**: Type your research topic
2. **Click Search**: Watch progress
3. **View Results**:
   - 📋 Summary tab: Full summary
   - 📌 Sources tab: URLs used
   - 📊 Debug tab: Detailed info
   - 💾 Export tab: Download as CSV/TXT

---

## 🧬 STEP 8: RUN TESTS

### Test Setup

```powershell
# Verify pytest installed
pip list | findstr pytest

# Should show pytest and pytest-asyncio
```

### Run All Tests

```powershell
# Run complete test suite (may take 5-10 minutes)
pytest -v

# Show summary only
pytest --tb=short

# Stop on first failure
pytest -x

# Run specific test file
pytest test_search.py -v

# Run specific test class
pytest test_pipeline.py::TestFullPipeline -v

# Run specific test
pytest test_search.py::TestSerperAPI::test_serper_search_success -v
```

### Test Files Explained

1. **test_search.py** - Serper API, query handling
   ```powershell
   pytest test_search.py -v
   ```

2. **test_scraper.py** - Web scraping, HTML parsing
   ```powershell
   pytest test_scraper.py -v
   ```

3. **test_summarizer.py** - Gemini API, summarization quality
   ```powershell
   pytest test_summarizer.py -v
   ```

4. **test_pipeline.py** - End-to-end pipeline execution
   ```powershell
   pytest test_pipeline.py -v
   ```

### Test Results Example

```
test_search.py::TestConfiguration::test_config_validate PASSED                 [5%]
test_search.py::TestConfiguration::test_google_api_key_configured PASSED       [10%]
test_search.py::TestSerperAPI::test_serper_search_success PASSED               [15%]
test_scraper.py::TestWebScraping::test_scrape_single_url PASSED                [20%]
test_summarizer.py::TestSummarization::test_basic_summarization PASSED         [25%]
test_pipeline.py::TestFullPipeline::test_full_end_to_end_pipeline PASSED       [100%]

================================= 50 passed in 245.32s =================================
✅ ALL TESTS PASSED!
```

---

## 🐛 STEP 9: DEBUG MODE

### Enable Debug Logging

#### In Code

```python
# agentic_browser_pipeline_fixed.py or streamlit_gemini_pipeline_fixed.py
DEBUG = True  # Change first line in main
```

#### In .env File

```
DEBUG=true
LOG_LEVEL=DEBUG
```

### Debug Output Includes

- ✓ Each API call details
- ✓ URLs fetched
- ✓ Content lengths at each stage
- ✓ Tokens used
- ✓ Timing breakdown
- ✓ Error traces

### Example Debug Run

```powershell
# Enable debug in config
$env:DEBUG = "true"

# Run CLI with debug output
python agentic_browser_pipeline_fixed.py "test query"

# Output will include:
# [10:30:45] [DEBUG] → Sending request to Serper API (timeout: 15s)
# [10:30:50] [DEBUG]   ✓ Found 5 URLs
# [10:30:50] [DEBUG]   → Scraping: https://example.com...
# [10:30:52] [DEBUG]     ✓ Scraped 8945 chars
# [10:31:05] [DEBUG]   → Sending to Gemini (8234 chars in prompt)
```

---

## ❌ STEP 10: TROUBLESHOOTING

### Problem: "GOOGLE_API_KEY not found"

**Solution:**
```powershell
# Check .env file exists
Test-Path ".env"  # Should show True

# Check content
Get-Content ".env" | Select-String "GOOGLE_API_KEY"

# If not found, create it:
Copy-Item ".env.clean" ".env"
# Then edit with your actual keys
```

### Problem: "timeout waiting for Serper API"

**Solution:**
```powershell
# Increase timeouts in .env
REQUEST_TIMEOUT=45
SERPER_TIMEOUT=20

# Or check internet connection
Test-NetConnection google.com -Port 443

# Try simpler query
python agentic_browser_pipeline_fixed.py "AI"
```

### Problem: "No content scraped"

**Solution:**
```powershell
# Check URLs are accessible
$url = "https://www.wikipedia.org/"
Invoke-WebRequest -Uri $url -UseBasicParsing

# Try increasing scrape timeout in .env
SCRAPE_TIMEOUT=15

# Try different search query
python agentic_browser_pipeline_fixed.py "python tutorial"
```

### Problem: "Empty response from Gemini"

**Solution:**
```powershell
# Verify API key in .env
Get-Content ".env" | Select-String "GOOGLE_API_KEY"

# Check Gemini API status
# Visit: https://status.openai.com or https://makersuite.google.com

# Try simpler content
# Edit test by reducing content size in STEP 9

# Verify quota in Google Cloud Console
# https://console.cloud.google.com/apis/dashboard
```

### Problem: Virtual environment not activating

**Solution:**
```powershell
# Check PowerShell execution policy
Get-ExecutionPolicy

# If "Restricted", run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again:
.\.venv\Scripts\Activate.ps1

# Verify activation shows (.venv) in prompt
```

### Problem: Dependencies not installing

**Solution:**
```powershell
# Clear pip cache
pip cache purge

# Reinstall requirements
pip install --upgrade pip setuptools wheel
pip install -r requirements_clean.txt

# If still fails, install individually
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install google-generativeai==0.3.0
```

---

## 📊 PERFORMANCE CHECKLIST

Use this to diagnose performance issues:

```powershell
# Sample Query Performance Test
function Test-Performance {
    $query = "machine learning"
    $start = Get-Date
    & python agentic_browser_pipeline_fixed.py $query
    $elapsed = (Get-Date) - $start
    Write-Host "Total time: $($elapsed.TotalSeconds) seconds"
    
    # Expected times:
    # Search: 3-5 seconds
    # Scrape: 5-15 seconds
    # Summarize: 3-8 seconds
    # TOTAL: 11-28 seconds
}

Test-Performance
```

---

## ✅ FINAL VERIFICATION CHECKLIST

Before considering setup complete:

- [ ] `.venv` folder created and activated
- [ ] `pip list` shows all required packages
- [ ] `.env` file created with valid API keys
- [ ] `python config.py` shows "✅ All configurations valid!"
- [ ] CLI runs: `python agentic_browser_pipeline_fixed.py "test"`
- [ ] Streamlit runs: `streamlit run streamlit_gemini_pipeline_fixed.py`
- [ ] Tests pass: `pytest test_search.py -v`
- [ ] Full pipeline test passes: `pytest test_pipeline.py::TestFullPipeline::test_full_end_to_end_pipeline -v`

---

## 🎯 NEXT STEPS

Once everything is running:

### Deploy to Cloud
```powershell
# Render (recommended for free tier)
# 1. Push to GitHub
# 2. Connect to Render.com
# 3. Set environment variables
# 4. Deploy

# Railway
# Similar process, visit railway.app

# HuggingFace Spaces
# Upload main files + requirements
```

### Monitor Performance
```powershell
# Track execution times
pytest test_pipeline.py -v -s

# Check API usage
# Gemini: https://makersuite.google.com/app/usage
# Serper: https://dashboard.serper.dev
```

### Optimize Further
- Adjust `MAX_CONTENT_PER_URL` in `.env`
- Cache search results
- Use parallel scraping
- Batch process multiple queries

---

## 📞 QUICK REFERENCE COMMANDS

```powershell
# Activation
.\.venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements_clean.txt

# Validate config
python config.py

# Run CLI
python agentic_browser_pipeline_fixed.py "your query"

# Run Streamlit
streamlit run streamlit_gemini_pipeline_fixed.py

# Run tests
pytest -v
pytest test_search.py -v
pytest test_pipeline.py::TestFullPipeline -v

# Enable debug
$env:DEBUG = "true"

# Deactivate venv
deactivate
```

---

**Version**: 1.0  
**Last Updated**: April 2026  
**Status**: ✅ Production Ready
