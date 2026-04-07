# 🚀 DEPLOYMENT GUIDE - QuickGlance Multi-Agent Pipeline

## 📋 Table of Contents

1. [Quick Deployment Comparison](#deployment-comparison)
2. [Render.com Setup](#render-deployment)
3. [Railway.app Setup](#railway-deployment)
4. [HuggingFace Spaces Setup](#huggingface-deployment)
5. [Local Production Setup](#local-production)
6. [Post-Deployment](#post-deployment)

---

## 📊 Deployment Comparison

| Feature | Render | Railway | HuggingFace | Heroku |
|---------|--------|---------|-------------|--------|
| **Cost** | Free tier available | $5/mo credit | Free | $7+/mo |
| **Setup Time** | 5 minutes | 5 minutes | 10 minutes | 10 minutes |
| **Always-On** | Paid plan | ✅ | ✅ | ✅ |
| **Auto-Deploy** | ✅ | ✅ | ✅ | ✅ |
| **Easy Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Free Tier** | ✅ | ✅ (limited) | ⭐ | ❌ |
| **Recommended** | **Best for most** | **Most affordable** | **Streamlit UI** | Legacy |

---

## 🎯 Render Deployment

### Prerequisites
- GitHub account (code repository)
- Render account (free at render.com)
- API keys: `GOOGLE_API_KEY`, `SERPER_API_KEY`

### Step 1: Push Code to GitHub

```bash
# Initialize repo (if not already)
git init
git add .
git commit -m "Initial commit: QuickGlance project"
git branch -M main
git remote add origin https://github.com/yourusername/quickglance.git
git push -u origin main
```

### Step 2: Create Render Account

1. Visit: https://render.com
2. Click "Sign up with GitHub"
3. Authorize Render access to GitHub
4. Create new account

### Step 3: Create Service on Render

**For API Service:**

```
1. Dashboard → New → Web Service
2. Select your GitHub repository
3. Configure:
   - Name: quickglance-api
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn api:app --host 0.0.0.0 --port $PORT --workers 2
   - Plan: Free (for testing) or Pro ($12/mo for production)
4. Click "Advanced" → Add Environment Variables:
   - GOOGLE_API_KEY: [your key]
   - SERPER_API_KEY: [your key]
   - PYTHONUNBUFFERED: 1
5. Deploy
```

**For UI Service (Optional):**

```
1. Dashboard → New → Web Service
2. Select same repository
3. Configure:
   - Name: quickglance-ui
   - Start Command: streamlit run streamlit_enhanced_app.py --server.port=$PORT --server.address=0.0.0.0
   - Add same environment variables
4. Deploy
```

### Step 4: Access Your Services

```
API: https://quickglance-api.onrender.com
API Docs: https://quickglance-api.onrender.com/api/docs
UI: https://quickglance-ui.onrender.com
```

### Step 5: Test the API

```bash
# Test health
curl https://quickglance-api.onrender.com/health

# Test query
curl -X POST https://quickglance-api.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

### Render Pricing

```
Free Tier:
- Services shut down after 15+ minutes of inactivity
- Limited resources
- Perfect for testing

Pro Plan ($12/month per service):
- Always-on
- Better resources
- 100 GB/month bandwidth
```

---

## 🚂 Railway Deployment

### Prerequisites
- GitHub account
- Railway account (free at railway.app)
- API keys

### Step 1: Create Railway Account

1. Visit: https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway
4. Create account

### Step 2: Deploy from GitHub

```
1. Dashboard → New Project
2. Select "Deploy from GitHub repo"
3. Search for your repository
4. Railway auto-detects railway.toml
5. Creates two services automatically
```

### Step 3: Configure Services

Railway automatically creates:
- `quickglance-api` (port 8000)
- `quickglance-ui` (port 8501)

### Step 4: Add Secrets

```
1. Service → Settings → Variables
2. Add secrets:
   - GOOGLE_API_KEY: [your key]
   - SERPER_API_KEY: [your key]
   - PYTHONUNBUFFERED: 1
```

### Step 5: Get Service URLs

```
1. Click each service
2. Find "URL" section
3. Copy public URL
4. Format: https://quickglance-api-production.up.railway.app
```

### Railway Pricing

```
Free Tier:
- $5/month credit
- Enough for both services

Usage-Based ($0.50/mo per GB RAM):
- 512MB API + 512MB UI = $0.50/month
- Total with credits: ~Free for 10 months
```

---

## 🤗 HuggingFace Spaces Deployment

### Prerequisites
- HuggingFace account (free)
- HuggingFace Space
- API keys

### Step 1: Create HuggingFace Account

1. Visit: https://huggingface.co
2. Sign up (free)
3. Email verification

### Step 2: Create Space

```
1. Navigate to: https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - Space name: quickglance
   - License: Apache 2.0
   - Space type: Docker OR Streamlit
   - Visibility: Public or Private
4. Create Space
```

### Step 3: Push Code to HuggingFace

```bash
# Clone your HF space
git clone https://huggingface.co/spaces/yourusername/quickglance
cd quickglance

# Copy your project files
cp -r /path/to/quickglance/* .

# Push to HF
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Add Secrets

For **Streamlit Space:**

```
Space Settings → Secrets:
- GOOGLE_API_KEY
- SERPER_API_KEY
```

For **Docker Space:**

Edit `Dockerfile` in Space:

```dockerfile
# Add environment variables
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV SERPER_API_KEY=${SERPER_API_KEY}
```

### Step 5: Configure app_file

For Streamlit:

```
app_file: streamlit_enhanced_app.py
```

### Step 6: Access Your Space

```
https://huggingface.co/spaces/yourusername/quickglance
```

### HuggingFace Pricing

```
Free Tier:
- Completely free
- Always-on inference
- Perfect for Streamlit UI
- 16GB RAM, 2 vCPU

Requirements:
- Public by default (can be private in paid tier)
```

---

## 🖥️ Local Production Setup

### Option 1: Using Gunicorn (Production WSGI)

```bash
# Install production server
pip install gunicorn

# Run API with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api:app

# Run Streamlit
streamlit run streamlit_enhanced_app.py --server.port 8501
```

### Option 2: Using Docker Locally

```bash
# Build image
docker build -t quickglance:latest .

# Run API
docker run -p 8000:8000 \
  --env-file .env \
  quickglance:latest

# Run UI
docker run -p 8501:8501 \
  --env-file .env \
  quickglance:latest \
  streamlit run streamlit_enhanced_app.py --server.port 8501
```

### Option 3: Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
    command: uvicorn api:app --host 0.0.0.0 --port 8000

  ui:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
      - API_URL=http://api:8000
    command: streamlit run streamlit_enhanced_app.py --server.port 8501

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
      - ui
```

Run:

```bash
docker-compose up
```

---

## ✅ Post-Deployment

### 1. Health Check

```bash
# Check API health
curl https://your-api-url.com/health

# Should return:
# {"status":"healthy","version":"1.0.0",...}
```

### 2. Test Full Query

```bash
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "enable_evaluation": true,
    "enable_formatting": true
  }'
```

### 3. Access Documentation

```
API Docs: https://your-api-url.com/api/docs
Streamlit UI: https://your-ui-url.com
```

### 4. Monitor Logs

**Render:**
```
Dashboard → Service → Logs
```

**Railway:**
```
Dashboard → Service → Logs
```

**HuggingFace:**
```
Space Settings → Logs
```

### 5. Set Up Custom Domain (Optional)

**Render:**
```
Service → Settings → Custom Domain
Add your domain: api.yourdomain.com
```

**Railway:**
```
Service → Settings → Environment
Add RAILWAY_DOMAIN if applicable
```

### 6. Enable HTTPS

Most platforms provide free HTTPS by default. Verify:

```bash
curl -I https://your-api-url.com
# Should show 200 OK
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

✅ Never commit `.env` file
```bash
echo ".env" >> .gitignore
```

✅ Use platform's secret manager
- Render: Environment Variables > Secrets
- Railway: Variables > Secrets
- HuggingFace: Repository secrets

### 2. API Security

✅ Enable CORS correctly (not `*` in production)
```python
# In api.py
ALLOWED_ORIGINS = ["https://yourdomain.com"]
```

✅ Add rate limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@limiter.limit("100/minute")
@app.post("/api/query")
```

✅ Add authentication (optional)
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.post("/api/query")
async def process_query(request: QueryRequest, credentials = Depends(security)):
    # Verify token
```

### 3. Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update requirements.txt
pip freeze > requirements-updated.txt
```

---

## 📊 Monitoring & Maintenance

### 1. Log Monitoring

Set up log aggregation:
- **Datadog**: Paid ($15+/mo)
- **LogRocket**: Freemium
- **Papertrail**: Freemium
- **ELK Stack**: Self-hosted

### 2. Error Tracking

Add Sentry for error tracking:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

### 3. Performance Monitoring

```bash
# Use New Relic (free tier)
pip install newrelic
```

### 4. Uptime Monitoring

- **UptimeRobot**: Free (50 monitors)
- **Pingdom**: Paid
- **Statuspage**: Free tier available

---

## 🆘 Troubleshooting

### API Returns 502 Bad Gateway

**Cause:** Server crashed or not responding

**Solution:**
```bash
# Check logs
# Check if start command is correct
# Increase timeout in platform settings
# Check memory usage
```

### Streamlit Shows "Connection Error"

**Cause:** Can't reach API

**Solution:**
```bash
# Update API_URL in .env
# Check CORS settings
# Verify API is running
```

### High Memory Usage

**Cause:** Inefficient pipeline

**Solution:**
```bash
# Increase allocated RAM
# Enable caching
# Use connection pooling
```

### Slow Responses

**Cause:** Many external API calls

**Solution:**
```bash
# Add caching layer (Redis)
# Increase worker count
# Use async processing
```

---

## 📈 Scaling Tips

### For API:

1. **Add caching**
   ```python
   from functools import lru_cache
   from redis import Redis
   ```

2. **Increase workers**
   ```bash
   uvicorn api:app --workers 4
   ```

3. **Database optimization**
   - Add indexes
   - Use connection pooling

### For UI:

1. **Enable caching**
   ```python
   @st.cache_data
   def expensive_operation():
       pass
   ```

2. **Lazy load content**
   ```python
   with st.expander("Details"):
       # Only loaded when expanded
   ```

---

## ✨ Next Steps

1. ✅ Deploy to your chosen platform
2. ✅ Test all endpoints
3. ✅ Set up monitoring
4. ✅ Configure custom domain (optional)
5. ✅ Share your live link!

---

**Deployment Checklist:**

- ✅ Repository pushed to GitHub
- ✅ API keys configured as secrets
- ✅ Environment variables set
- ✅ Health check passes
- ✅ Query endpoint tested
- ✅ UI accessible (if deployed)
- ✅ Logs monitored
- ✅ HTTPS enabled
- ✅ Custom domain (if applicable)

**🎉 You're live!**
