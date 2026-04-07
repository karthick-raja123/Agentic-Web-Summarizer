# 🔧 TROUBLESHOOTING GUIDE

Comprehensive troubleshooting for all common issues.

---

## 🚨 CONFIGURATION ISSUES

### Issue: "GOOGLE_API_KEY not found in environment variables"

**Symptoms:**
```
ValueError: GOOGLE_API_KEY not found in environment variables
```

**Causes & Solutions:**

1. **.env file not found**
   ```powershell
   # Check if .env exists
   Test-Path "./.env"
   
   # Solution: Create from template
   Copy-Item ".env.clean" ".env"
   ```

2. **API key not filled in**
   ```powershell
   # Check .env content
   Get-Content ".env" | Select-String "GOOGLE_API_KEY"
   
   # Should show: GOOGLE_API_KEY=sk-xxxxxxx...
   # If shows: GOOGLE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   # Solution: Get real key from https://makersuite.google.com/app/apikey
   ```

3. **Virtual environment not active**
   ```powershell
   # Check (.venv) in prompt
   # If not showing, activate:
   .\.venv\Scripts\Activate.ps1
   ```

4. **Using wrong .env file**
   ```powershell
   # Verify correct .env location
   Get-Location
   # Should show project root
   
   # .env must be in project root, not subdirectory
   ```

---

### Issue: "SERPER_API_KEY is missing or not configured"

**Symptoms:**
```
Config error: SERPER_API_KEY is missing
```

**Solutions:**
```powershell
# 1. Get API key from https://serper.dev
# 2. Edit .env
echo "SERPER_API_KEY=your_actual_key_here" >> .env

# 3. Verify
Get-Content ".env" | Select-String "SERPER_API_KEY"

# 4. Test connection
python -c "from config import Config; print(f'✓ Key configured: {Config.SERPER_API_KEY[:10]}...')"
```

---

## 🌐 API & NETWORK ISSUES

### Issue: "Serper API timeout"

**Symptoms:**
```
requests.exceptions.Timeout: Connection timeout after 15s
```

**Causes & Solutions:**

1. **Poor internet connection**
   ```powershell
   # Test connection
   Test-NetConnection google.com -Port 443
   
   # Solution: Check WiFi/ethernet, restart router
   ```

2. **Serper API down**
   ```powershell
   # Check status
   Invoke-WebRequest "https://google.serper.dev/search" -Method POST `
     -Headers @{"X-API-KEY"="test"} -Body '{"q":"test"}'
   
   # Solution: Wait for service to recover
   # Check: https://status.serper.dev
   ```

3. **Timeout value too low**
   ```powershell
   # Increase timeout in .env
   SERPER_TIMEOUT=30  # Increased from 15
   REQUEST_TIMEOUT=45
   ```

4. **Rate limiting (too many requests)**
   ```powershell
   # Wait before retrying
   Start-Sleep -Seconds 60
   
   # Check usage: https://dashboard.serper.dev
   # Free tier: limited requests per day
   ```

---

### Issue: "Failed to connect to Gemini API"

**Symptoms:**
```
google.api_core.exceptions.PermissionDenied: 403 Permission denied
```

**Causes & Solutions:**

1. **Invalid API key**
   ```powershell
   # Verify key format (should start with "sk-")
   Get-Content ".env" | Select-String "GOOGLE_API_KEY"
   
   # Get fresh key:
   # 1. https://makersuite.google.com/app/apikey
   # 2. Delete existing key
   # 3. Create new one
   # 4. Update .env
   ```

2. **API key quota exceeded**
   ```powershell
   # Check quota
   # Visit: https://console.cloud.google.com/apis/dashboard
   
   # Solution:
   # - Upgrade to paid plan
   # - Wait for quota reset (daily/monthly)
   ```

3. **API not enabled in Google Cloud**
   ```powershell
   # Enable Generative Language API
   # Visit: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
   # Click "Enable"
   ```

---

## 📄 SCRAPING ISSUES

### Issue: "No content extracted from pages"

**Symptoms:**
```
No content could be scraped from any URLs
Content is empty after scraping
```

**Causes & Solutions:**

1. **Dynamic JavaScript content**
   ```powershell
   # URLs with JS-rendered content can't be scraped with requests
   
   # Check if content needs JS rendering
   # Solution: Use Playwright (not in base package)
   pip install playwright
   
   # Update code to use browser automation
   ```

2. **Website blocks scraping**
   ```powershell
   # Some sites block user-agents
   
   # Solution: Try different User-Agent
   # Edit: headers = {"User-Agent": "Mozilla/5.0..."}
   ```

3. **Rate limiting from target site**
   ```powershell
   # Some sites block rapid requests
   
   # Solution: Add delay between requests
   # Increase SCRAPE_TIMEOUT in .env
   SCRAPE_TIMEOUT=10
   ```

4. **Content behind login**
   ```powershell
   # Private content can't be accessed
   
   # Solution: Use different search query with public content
   # Or use API endpoints for content (if available)
   ```

---

### Issue: "HTML parsing errors"

**Symptoms:**
```
BeautifulSoup unable to parse HTML
AttributeError: 'NoneType' has no attribute...
```

**Solutions:**
```powershell
# 1. Verify BeautifulSoup installed
pip list | findstr beautifulsoup

# 2. Reinstall if needed
pip install --force-reinstall beautifulsoup4==4.12.2

# 3. Check HTML validity
# Add debug output to see raw HTML

# 4. Use different parser
# Change: BeautifulSoup(response.text, "html.parser")
# To:     BeautifulSoup(response.text, "lxml")
# Or:     BeautifulSoup(response.text, "html5lib")
```

---

## 🤖 SUMMARIZATION ISSUES

### Issue: "Empty response from Gemini"

**Symptoms:**
```
summary = ""
Gemini returns blank response
```

**Causes & Solutions:**

1. **Content too short**
   ```powershell
   # Gemini needs meaningful content
   
   # Check scraped content length
   # Should be > 100 characters
   
   # Try different search query with more content
   ```

2. **Prompt too complex**
   ```powershell
   # Simplify prompt
   # Instead of: "Summarize in 7 bullets with academic tone..."
   # Use: "Summarize in 5 bullet points"
   ```

3. **Content all boilerplate**
   ```powershell
   # Remove navigation, footer, sidebar HTML
   
   # Update scraper:
   for tag in soup(['script', 'style', 'nav', 'footer']):
       tag.decompose()
   ```

---

### Issue: "Summarization takes too long"

**Symptoms:**
```
Request hangs for > 30 seconds
Eventually times out
```

**Solutions:**
```powershell
# 1. Reduce content size in .env
MAX_TOTAL_CONTENT=30000  # Reduced from 50000

# 2. Increase timeout
REQUEST_TIMEOUT=60

# 3. Use faster model
# Instead of: "gemini-1.5-pro"
# Use: "gemini-1.5-flash" (faster, cheaper)

# 4. Reduce scraping URLs
MAX_URLS_TO_SCRAPE=3  # Reduced from 5
```

---

## 🧪 TEST FAILURES

### Issue: "Tests timeout"

**Symptoms:**
```
pytest: test timed out after 300 seconds
```

**Solutions:**
```powershell
# 1. Run specific test without timeout
pytest test_name.py --override-ini="timeout=0"

# 2. Skip slow tests
pytest -m "not timeout"

# 3. Increase timeout for all tests
# Edit pytest.ini:
timeout = 600  # Increased to 10 minutes

# 4. Check network is stable
# Retry test later
```

---

### Issue: "Tests fail due to API errors"

**Symptoms:**
```
test_search.py::test_serper_search FAILED
Serper API returned 401/403
```

**Solutions:**
```powershell
# 1. Verify API credentials in .env
python config.py

# 2. Check API quota
# Visit: https://dashboard.serper.dev
# Visit: https://makersuite.google.com/app/usage

# 3. Skip tests if APIs unavailable
pytest -k "not test_serper" -v

# 4. Run tests later when API available
```

---

### Issue: "Network-related test failures"

**Symptoms:**
```
ConnectionError: HTTPConnectionPool
requests.exceptions.ConnectionError
```

**Solutions:**
```powershell
# 1. Check internet connectivity
Test-NetConnection google.com -Port 443

# 2. Check firewall/proxy
# Corporate networks may block API calls

# 3. Try VPN if behind proxy
# Or configure proxy in code

# 4. Skip network tests while offline
pytest -m "not network" -v
```

---

## 📦 INSTALLATION ISSUES

### Issue: "pip install fails"

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
ERROR: No matching distribution found
```

**Solutions:**
```powershell
# 1. Clear pip cache
pip cache purge

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install with specific version
pip install google-generativeai==0.3.0 --no-cache-dir

# 4. Try alternative index
pip install -r requirements_clean.txt -i https://pypi.org/simple/

# 5. Check Python version
python --version  # Should be 3.9+

# 6. Use requirement file directly
pip install --upgrade -r requirements_clean.txt
```

---

### Issue: "Virtual environment corrupted"

**Symptoms:**
```
ModuleNotFoundError after activation
Mixed package versions
```

**Solutions:**
```powershell
# 1. Delete and recreate venv
Remove-Item .\.venv -Recurse -Force

# 2. Create fresh
python -m venv .venv

# 3. Activate
.\.venv\Scripts\Activate.ps1

# 4. Reinstall all
pip install -r requirements_clean.txt
```

---

## 🎯 PERFORMANCE ISSUES

### Issue: "Pipeline runs too slow"

**Table of expected times:**

| Stage | Normal | Slow | Issue |
|-------|--------|------|-------|
| Search | 3-5s | 10-15s | Network/API slow |
| Scrape | 5-15s | 30-60s | Slow websites or too many URLs |
| Summarize | 3-8s | 15-30s | Large content or API busy |
| **Total** | **11-28s** | **60+s** | Configuration needed |

**Solutions:**
```powershell
# 1. Reduce search results in .env
MAX_SEARCH_RESULTS=5  # Reduced from 10

# 2. Reduce URLs to scrape
MAX_URLS_TO_SCRAPE=3  # Reduced from 5

# 3. Reduce content limits
MAX_CONTENT_PER_URL=5000  # Reduced from 10000
MAX_TOTAL_CONTENT=30000   # Reduced from 50000

# 4. Use faster model
# Check model name in code, use "-flash" variant

# 5. Parallel processing (advanced)
# Use concurrent.futures for URL scraping
```

---

## 🔍 DEBUG & LOGGING

### Enable Verbose Output

```powershell
# Set debug in .env
DEBUG=true
LOG_LEVEL=DEBUG

# Or export environment variable
$env:DEBUG = "true"

# Run with debug
python agentic_browser_pipeline_fixed.py "query"
```

### Check Log File

```powershell
# If LOG_FILE is configured in .env
Get-Content logs/quickglance.log -Tail 50

# Filter by error
Select-String -Path logs/quickglance.log -Pattern "ERROR"
```

### Add Custom Logging

```python
# In your script
from config import Config

def log_debug(msg):
    if Config.DEBUG:
        print(f"[DEBUG] {msg}")

log_debug("This message only shows when DEBUG=true")
```

---

## ✅ VERIFICATION COMMANDS

Use these to diagnose issues:

```powershell
# 1. Configuration check
python config.py

# 2. Import check
python -c "import requests; import google.generativeai; print('✓ All imports OK')"

# 3. API connectivity
python -c "from config import Config; import requests; r = requests.post('https://google.serper.dev/search', headers={'X-API-KEY': Config.SERPER_API_KEY, 'Content-Type': 'application/json'}, json={'q': 'test'}, timeout=10); print(f'✓ Serper API: {r.status_code}')"

# 4. Python version
python --version

# 5. Virtual environment
Get-Command python

# 6. Installed packages
pip list

# 7. Test connection
Test-NetConnection google.com -Port 443

# 8. Run minimal test
pytest test_search.py::TestConfiguration -v
```

---

## 📞 STILL STUCK?

If none of the above solves your issue:

1. **Collect debug info:**
   ```powershell
   # Copy output of these:
   python config.py
   python --version
   pip list
   Get-Content ".env" | Select-String -Pattern "^[^#]"  # Non-comment lines only
   ```

2. **Check logs:**
   ```powershell
   Get-Content logs/quickglance.log -Tail 100
   ```

3. **Run minimal test:**
   ```powershell
   pytest test_search.py::TestConfiguration::test_config_validate -v -s
   ```

4. **Test individually:**
   - Does Serper API work? `pytest test_search.py -v`
   - Does scraping work? `pytest test_scraper.py -v`
   - Does Gemini work? `pytest test_summarizer.py -v`
   - Does full pipeline work? `pytest test_pipeline.py::TestFullPipeline -v`

---

**Last Updated**: April 2026  
**Version**: 1.0
