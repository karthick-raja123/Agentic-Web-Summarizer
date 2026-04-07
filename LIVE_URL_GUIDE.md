# 🔗 Live URL Access Guide

## Quick Reference - After Deployment

### Render Deployment URLs

```
API Service:          https://quickglance-api.onrender.com
API Docs (Swagger):   https://quickglance-api.onrender.com/docs
API Docs (ReDoc):     https://quickglance-api.onrender.com/redoc
Health Check:         https://quickglance-api.onrender.com/health

UI Service:           https://quickglance-ui.onrender.com
UI (Direct Access):   https://quickglance-ui.onrender.com (opens in browser)
```

### Railway Deployment URLs

```
API Service:          https://quickglance-api-[random].up.railway.app
API Docs (Swagger):   https://quickglance-api-[random].up.railway.app/docs
Health Check:         https://quickglance-api-[random].up.railway.app/health

UI Service:           https://quickglance-ui-[random].up.railway.app
UI (Direct Access):   https://quickglance-ui-[random].up.railway.app
```

### HuggingFace Spaces URL

```
UI Service:           https://huggingface.co/spaces/yourusername/quickglance
```

---

## 📊 Finding Your Deployment URLs

### On Render

**Step 1:** Go to https://render.com/dashboard

**Step 2:** Click on your service (quickglance-api or quickglance-ui)

**Step 3:** Look for "Service URL" - Copy it

Example:
```
https://quickglance-api.onrender.com
https://quickglance-ui.onrender.com
```

### On Railway

**Step 1:** Go to https://railway.app/dashboard

**Step 2:** Click your project

**Step 3:** Select service → Settings

**Step 4:** Find "Domains" section

**Step 5:** Look for public URL

Example:
```
https://quickglance-api-production.up.railway.app
https://quickglance-ui-production.up.railway.app
```

### On HuggingFace

**Step 1:** Go to https://huggingface.co/spaces

**Step 2:** Find your space: `your-username/quickglance`

**Step 3:** URL is directly: https://huggingface.co/spaces/yourusername/quickglance

---

## 🧪 Testing Your Live URLs

### Test API is Running

```bash
# Replace with your actual URL
curl https://your-api-url.com/health

# Should return:
# {"status":"healthy","version":"1.0.0",...}
```

### Test Query Endpoint

```bash
# Replace with your actual URL
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is cloud computing?"}'
```

### Check API Documentation

1. Open browser: `https://your-api-url.com/docs`
2. Should show Swagger UI
3. Can test endpoints directly in browser

### Access UI

1. Open browser: `https://your-ui-url.com`
2. Should load Streamlit app
3. Try searching for something

---

## 🔄 Connecting Frontend to Backend

### For Streamlit UI to Access API

Edit `streamlit_enhanced_app.py`:

```python
import streamlit as st
import requests
from urllib.parse import urljoin

# Get API URL from environment or use default
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# Use secrets for API key if needed
API_KEY = st.secrets.get("API_KEY", "")

def query_api(query_text):
    """Query the FastAPI backend"""
    try:
        response = requests.post(
            urljoin(API_URL, "/api/query"),
            json={"query": query_text},
            timeout=30,
            headers={"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# In your main UI code:
if st.button("Search"):
    result = query_api(user_query)
    if result and result.get("status") == "success":
        st.write(result["results"]["summary"])
```

### On Render

Set environment variable:
```
API_URL = https://quickglance-api.onrender.com
```

In Render dashboard:
1. UI Service → Environment
2. Add: `API_URL=https://quickglance-api.onrender.com`
3. Redeploy

### On Railway

Set environment variable:
```
API_URL = https://quickglance-api-production.up.railway.app
```

In Railway dashboard:
1. UI Service → Variables
2. Add: `API_URL=https://quickglance-api-production.up.railway.app`
3. Redeploy

### On HuggingFace Spaces

Create `.env` file or set in secrets:
```
API_URL=https://your-api-url.com
```

---

## 🎯 Important URL Endpoints

### API Endpoints (Available at all versions)

| Path | Method | Purpose |
|------|--------|---------|
| `/health` | GET | Health check |
| `/api/query` | POST | Main query endpoint |
| `/api/batch` | POST | Batch queries |
| `/api/status/{id}` | GET | Check query status |
| `/api/capabilities` | GET | List capabilities |
| `/docs` | GET | Swagger documentation |
| `/redoc` | GET | ReDoc documentation |
| `/openapi.json` | GET | OpenAPI schema |

### Usage Examples

**Get API Documentation:**
```
https://your-api-url.com/docs
```

**Health Check:**
```
https://your-api-url.com/health
```

**API Capabilities:**
```
https://your-api-url.com/api/capabilities
```

**Query via browser:** (not recommended, use POST with body)
```
POST to: https://your-api-url.com/api/query
Body: {"query": "Your question"}
```

---

## 🚀 Setting Custom Domains (Optional)

### Render Custom Domain

**Steps:**
1. Dashboard → Service → Settings → Custom Domain
2. Enter your domain: `api.yourdomain.com`
3. Follow DNS setup instructions
4. Wait 10-30 minutes for propagation

**DNS Setup:**
```
CNAME: api.yourdomain.com → your-api.onrender.com
```

### Railway Custom Domain

**Steps:**
1. Railway Dashboard → Service → Settings
2. Networking → Custom Domain
3. Add your domain
4. Update DNS records

**DNS Setup:**
```
CNAME: api.yourdomain.com → railway-assigned-domain.up.railway.app
```

### HuggingFace Spaces

HuggingFace doesn't support custom domains for free spaces (requires paid tier).

---

## 📱 Testing in Different Ways

### Using Postman

1. Download Postman
2. Create new request:
   - Method: POST
   - URL: `https://your-api-url.com/api/query`
   - Body (raw JSON):
     ```json
     {
       "query": "What is AI?",
       "timeout": 30
     }
     ```
3. Send → View response

### Using Thunder Client (VS Code)

1. Install Extension
2. New Request
3. Set same parameters as Postman
4. Send

### Using Insomnia

1. Download Insomnia
2. New POST request
3. Similar setup as Postman

### Using Browser Console (for GET endpoints)

```javascript
fetch('https://your-api-url.com/health')
  .then(r => r.json())
  .then(data => console.log(data))

fetch('https://your-api-url.com/api/capabilities')
  .then(r => r.json())
  .then(data => console.log(data))
```

### Using Python REPL

```python
import requests

# Health check
resp = requests.get('https://your-api-url.com/health')
print(resp.json())

# Query
resp = requests.post(
    'https://your-api-url.com/api/query',
    json={'query': 'What is machine learning?'}
)
print(resp.json())
```

---

## ✅ Common URL Issues & Fixes

### "Connection Refused" / "Cannot reach server"

**Cause:** Service is sleeping or not running

**Fix:**
- Render free tier sleeps after 15 min inactivity
- Railway free credit may be exhausted
- Check platform dashboard for errors

### "404 Not Found" on API endpoint

**Cause:** Wrong URL or endpoint path

**Fix:**
```
✅ Correct:   https://your-api-url.com/api/query
❌ Wrong:     https://your-api-url.com/query
❌ Wrong:     https://your-api-url.com/api/v1/query (if no v1)
```

### "CORS Error" in browser console

**Cause:** Frontend and backend on different origins

**Fix:**
- Ensure API_URL is set correctly in Streamlit secrets
- Check CORS configuration in api.py
- Configure allowed origins:
  ```python
  allow_origins=["https://your-ui.com"]
  ```

### "Timeout" - Query takes too long

**Cause:** Complex query or slow API calls

**Fix:**
- Increase timeout: `"timeout": 60` (in seconds)
- Simplify query
- Add caching layer

---

## 🌐 Accessing from Different Locations

### From Your Laptop

```bash
# Direct URL access
curl https://your-api-url.com/health

# Via Python
import requests
r = requests.get('https://your-api-url.com/health')
```

### From Mobile

```
1. Open browser
2. Visit: https://your-api-url.com
3. Or for UI: https://your-ui-url.com
```

### From Another Application

```python
# Same as laptop - use HTTPS
import requests

api_url = "https://quickglance-api.onrender.com"
response = requests.post(
    f"{api_url}/api/query",
    json={"query": "Your question"}
)
```

### From Another Server

```bash
# Use curl or requests, same as above
# No special setup needed - just use HTTPS URLs
```

---

## 📊 URL & Endpoint Quick Reference

| Need | URL |
|------|-----|
| API Docs | `https://your-api-url.com/docs` |
| API Test | `https://your-api-url.com/api/query` (POST) |
| Health | `https://your-api-url.com/health` |
| UI | `https://your-ui-url.com` |
| Capabilities | `https://your-api-url.com/api/capabilities` |

---

## 🔐 Security Note

**Never share:**
- API URLs with API keys in them
- Authorization tokens
- Your deployment secrets
- Database connection strings

**Share:**
- Public API URL
- Documentation link
- UI link

---

## ✨ Example: Complete Flow

**Scenario:** I deployed to Render and want to test everything

1. **Get URLs:**
   ```
   API: https://quickglance-api.onrender.com
   UI: https://quickglance-ui.onrender.com
   ```

2. **Test API:**
   ```bash
   curl https://quickglance-api.onrender.com/health
   # Returns: {"status":"healthy",...}
   ```

3. **Test Query:**
   ```bash
   curl -X POST https://quickglance-api.onrender.com/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is AI?"}'
   # Returns: {"status":"success","results":{...}}
   ```

4. **Access UI:**
   ```
   Open browser: https://quickglance-ui.onrender.com
   Search for: "Example query"
   Results appear
   ```

5. **View Docs:**
   ```
   https://quickglance-api.onrender.com/docs
   Can test endpoints here
   ```

6. **Share URLs:**
   ```
   API Docs: https://quickglance-api.onrender.com/docs
   Live UI: https://quickglance-ui.onrender.com
   ```

---

**All URLs are HTTPS-enabled by default on modern platforms.**

**Deployment complete! 🎉**
