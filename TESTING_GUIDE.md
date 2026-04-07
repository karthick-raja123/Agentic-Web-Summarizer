# 🧪 Testing & Verification Guide

## Pre-Deployment Testing

Before deploying, ensure everything works locally.

---

## Local Testing (Before Deployment)

### 1. Environment Setup
```bash
# Check Python version (requires 3.9+)
python --version

# Create virtual environment
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
cp .env.example .env
# Edit .env and add:
# GOOGLE_API_KEY=your_key
# SERPER_API_KEY=your_key
```

### 2. Test API Locally
```bash
# Terminal 1: Start API
python -m uvicorn api:app --reload

# Terminal 2: Test endpoints
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0",...}
```

### 3. Test Query Endpoint
```bash
# Simple query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'

# Should return JSON with results
```

### 4. Test Streamlit UI
```bash
# Terminal 3: Start Streamlit
streamlit run streamlit_enhanced_app.py

# Open browser
# http://localhost:8501

# Try searching
# Should work and return results
```

### 5. API Documentation
```bash
# Open browser
# http://localhost:8000/docs

# Should show Swagger UI with all endpoints
# Can test endpoints directly here
```

---

## Post-Deployment Testing

After deploying to platform, verify each service works.

### Test Spreadsheet

| Test | Render | Railway | HF | Status |
|------|--------|---------|----|----|
| API Health | ✓ | ✓ | N/A | |
| API Query | ✓ | ✓ | N/A | |
| API Docs | ✓ | ✓ | N/A | |
| UI Loads | ✓ | ✓ | ✓ | |
| UI Searches | ✓ | ✓ | ✓ | |

### Step 1: Test API Health

**Command:**
```bash
curl https://your-api-url.com/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600
}
```

**Troubleshooting:**
- ❌ "Connection refused" → Service still deploying (wait 2-3 min)
- ❌ "404 Not Found" → Wrong URL path
- ❌ "500 Error" → Check environment variables

### Step 2: Test Query Endpoint

**Command:**
```bash
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?"}'
```

**Expected Response (200 OK):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "query": "What is artificial intelligence?",
  "results": {
    "summary": "Artificial intelligence (AI) is...",
    "sources": [...]
  },
  "metadata": {
    "processing_time_seconds": 4.2
  }
}
```

**Troubleshooting:**
- ❌ "API key invalid" → Check GOOGLE_API_KEY
- ❌ "Search failed" → Check SERPER_API_KEY
- ❌ "Timeout" → Query took too long, try simpler query

### Step 3: Test API Documentation

**URL:**
```
https://your-api-url.com/docs
```

**Expected:**
- Swagger UI loads
- Shows all endpoints
- Can test endpoints in browser
- Shows request/response examples

**Troubleshooting:**
- ❌ "404 Not Found" → Wrong URL or old browser cache
- ❌ Blank page → Wait for service to fully start

### Step 4: Test UI Access

**URL:**
```
https://your-ui-url.com
```

**Expected:**
- Streamlit app loads
- Search input visible
- Search button clickable
- Results display after search

**Troubleshooting:**
- ❌ "Connection refused" → Service still deploying
- ❌ "Cannot find API" → Check API_URL in environment variables
- ❌ Blank page → Check browser console for errors

### Step 5: End-to-End Test

**Scenario:** Search for something in UI

**Steps:**
```
1. Open https://your-ui-url.com
2. Enter search query: "machine learning basics"
3. Click Search
4. Wait for results
5. See summary and sources
```

**Expected:**
- Results appear within 15 seconds
- Summary is readable
- Sources are linked
- No error messages

---

## Automated Testing

### Unit Tests

**File:** `tests/test_api.py`

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_api.py::test_health -v
```

### Example Test

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query_endpoint():
    response = client.post(
        "/api/query",
        json={"query": "What is AI?"}
    )
    assert response.status_code == 200
    assert "results" in response.json()

def test_invalid_query():
    response = client.post(
        "/api/query",
        json={"query": ""}
    )
    assert response.status_code == 400
```

### Run Tests

```bash
# Create tests directory
mkdir tests
touch tests/__init__.py

# Add test_api.py with above code

# Run tests
pytest tests/ -v

# Expected output:
# test_health PASSED
# test_query_endpoint PASSED
# test_invalid_query PASSED
```

---

## Load Testing

### Using Apache Bench

```bash
# Install ab (Apache Bench)
# On Mac: brew install httpd
# On Windows: Download from Apache website

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 https://your-api-url.com/health

# Check results:
# - Requests per second (higher = better)
# - Average response time (lower = better)
# - Failed requests (should be 0)
```

### Using wrk

```bash
# Install wrk (load testing tool)
# https://github.com/wg/wrk

# Run load test (4 threads, 100 connections, 30 seconds)
wrk -t4 -c100 -d30s https://your-api-url.com/health

# Check results:
# - Average latency (lower = better)
# - Max latency (should be reasonable)
# - Throughput (requests/sec)
```

### Using Python

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def test_endpoint():
    response = requests.get(
        "https://your-api-url.com/health",
        timeout=10
    )
    return response.status_code

# Run 100 concurrent requests
start = time.time()
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: test_endpoint(), range(100)))

elapsed = time.time() - start
success_rate = sum(1 for r in results if r == 200) / len(results)

print(f"Time: {elapsed:.2f}s")
print(f"Success Rate: {success_rate*100:.1f}%")
print(f"Throughput: {100/elapsed:.1f} req/s")
```

---

## Performance Testing

### API Response Time

```bash
# Measure time for single request
time curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'

# Expected: 4-8 seconds for typical query
```

### Memory Usage

```bash
# On local machine:
# Terminal 1
python -m uvicorn api:app --reload

# Terminal 2: Monitor memory
# On Mac/Linux:
ps aux | grep uvicorn

# On Windows:
tasklist | findstr python
```

### CPU Usage

```bash
# During load test, check CPU
# On Mac:
top -P -pid [process_id]

# On Linux:
top -p [process_id]

# On Windows:
Get-Process python | Select-Object Name, CPU, Memory
```

---

## Security Testing

### CORS Testing

```bash
# Test CORS headers
curl -H "Origin: https://different-origin.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://your-api-url.com/api/query

# Should show ACAO (Access-Control-Allow-Origin) header
```

### Input Validation

```bash
# Test with invalid JSON
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{invalid json}'

# Should return 422 Unprocessable Entity

# Test with missing required field
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{}'

# Should return 422 with details
```

### Rate Limiting

```bash
# Send 101 requests (if 100/min limit)
for i in {1..101}; do
  curl https://your-api-url.com/health
done

# 101st should be rate limited (429 status)
```

### API Key Security

```bash
# Verify API key not in logs
# Check deployment platform logs
# Should NOT see GOOGLE_API_KEY or SERPER_API_KEY in plain text

# Verify HTTPS
curl -I https://your-api-url.com/health
# Should show: HTTP/2 200 (not HTTP/1.1 or unencrypted)
```

---

## Monitoring & Logging

### Check Application Logs

**Render:**
```
1. Dashboard → Service → Logs
2. Look for errors
3. Check response times
```

**Railway:**
```
1. Dashboard → Service → Logs
2. Monitor for issues
3. Export logs if needed
```

**Local:**
```bash
# Check API logs
tail -f logs/api.log

# Check Streamlit logs
# Printed to console during startup
```

### Common Log Patterns

**Good (✅):**
```
INFO: Application startup complete
INFO: Uvicorn running on 0.0.0.0:8000
GET /health - "200 OK"
POST /api/query - "200 OK" in 4.23s
```

**Bad (❌):**
```
ERROR: Failed to start application
ERROR: API key invalid
ERROR: Connection timeout to external service
CRITICAL: Service crashed
```

---

## Verification Checklist

**Before Deployment:**
- [ ] Code pushed to GitHub
- [ ] `api.py` present in root
- [ ] `requirements.txt` has all dependencies
- [ ] `.env.example` shows all variables needed
- [ ] API works locally (`/health` returns 200)
- [ ] Query works locally (returns results)
- [ ] Streamlit UI works locally
- [ ] No hardcoded API keys in code

**After Deployment:**
- [ ] Platform shows "success" or "deployed"
- [ ] `/health` endpoint returns 200
- [ ] `/api/query` endpoint accepts POST
- [ ] `/docs` shows API documentation
- [ ] UI loads in browser
- [ ] UI can submit query
- [ ] Results display correctly
- [ ] No error messages

**Production:**
- [ ] HTTPS enabled (URLs start with https://)
- [ ] Environment variables configured
- [ ] Auto-deploy from main branch works
- [ ] Logs are being collected
- [ ] Performance is acceptable (< 10s queries)
- [ ] CORS working for cross-origin requests
- [ ] Rate limiting (if configured)
- [ ] Monitoring alerts configured

---

## Troubleshooting Test Failures

### Test: Health Check Fails

**Symptoms:** `curl` returns 502 or cannot connect

**Causes:**
- Service not started
- Port not exposed
- Environment variables missing

**Fix:**
```bash
# Check service logs
# On Render/Railway: View Logs tab
# Restart service
# Verify PYTHONUNBUFFERED=1 is set
```

### Test: Query Timeout

**Symptoms:** Takes > 30 seconds or returns 408

**Causes:**
- Query too complex
- External API slow
- Network issues

**Fix:**
```bash
# Try simpler query
# Increase timeout: "timeout": 60
# Check internet speed
```

### Test: API Documentation Blank

**Symptoms:** `/docs` loads but no endpoints shown

**Causes:**
- Old browser cache
- Service still fully loading
- CORS issue

**Fix:**
```bash
# Hard refresh (Ctrl+F5)
# Wait 30 seconds
# Check browser console for errors
```

### Test: UI Can't Find API

**Symptoms:** UI loads but search doesn't work

**Causes:**
- API_URL environment variable not set
- CORS not enabled
- API down

**Fix:**
```bash
# Check API_URL in Streamlit secrets
# Verify API is running (test /health)
# Check CORS configuration
```

---

## Performance Benchmarking

### Baseline Metrics

Expected performance (from cloud region with good internet):

| Metric | Expected | Warning | Critical |
|--------|----------|---------|----------|
| Health Check | < 200ms | > 500ms | > 2s |
| Simple Query | 2-4s | > 8s | > 15s |
| Complex Query | 8-12s | > 20s | > 30s |
| Batch (3x) | 12-20s | > 30s | > 45s |

### Monitor Performance

```bash
# Create performance dashboard
# Using your platform's monitoring tools

# Render: Set up email alerts
# Railway: Configure usage alerts
# Cloud: Use CloudWatch/Azure Monitor
```

---

## Continuous Monitoring

### Set Up Monitoring

**Option 1: UptimeRobot (Free)**
```
1. uptimerobot.com
2. New monitor
3. Type: HTTPS
4. URL: https://your-api-url.com/health
5. Check interval: 5 minutes
6. Get email alerts if down
```

**Option 2: Better Uptime**
```
1. betterstack.com
2. New monitor
3. Configure endpoints
4. Set up alert webhooks
```

**Option 3: Platform Native**
- Render: Alerts in dashboard
- Railway: monitoring built-in

---

## Support & Debugging

### Get Debug Information

```bash
# API capabilities
curl https://your-api-url.com/api/capabilities

# OpenAPI schema
curl https://your-api-url.com/openapi.json

# Check all headers
curl -v https://your-api-url.com/health
```

### Create Issues/Reports

Include:
- [ ] Exact error message
- [ ] Request parameters
- [ ] Platform (Render/Railway/etc)
- [ ] Timestamp of issue
- [ ] Steps to reproduce

---

## ✅ You're Ready to Test!

Use this guide to verify:
1. ✅ Local development works
2. ✅ Deployment succeeds
3. ✅ All endpoints functional
4. ✅ Performance acceptable
5. ✅ Security verified

**Ready to go live? 🚀**
