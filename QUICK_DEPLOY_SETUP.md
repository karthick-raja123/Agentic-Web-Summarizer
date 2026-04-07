# 🚀 Quick Deployment Setup Guide

## ⚡ 5-Minute Local Setup

### Prerequisites
- Python 3.9+
- Git installed
- API keys: `GEMINI_API_KEY` and `SERPER_API_KEY`

### Step 1: Create Virtual Environment
```bash
cd "d:\Git\Visual Web Agent\Visual-web-Agent"
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Or on Linux/Mac
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements-deploy.txt
```

### Step 3: Create .env File
Create `.env` in `Visual-web-Agent` folder:
```
GEMINI_API_KEY=your_gemini_key_here
SERPER_API_KEY=your_serper_key_here
```

**Get API Keys:**
- **Gemini**: https://makersuite.google.com/app/apikey
- **Serper**: https://serper.dev/dashboard

### Step 4: Run Backend (Terminal 1)
```bash
python -m uvicorn app_fastapi:app --reload --host 0.0.0.0 --port 8000
```

✓ Backend running: http://localhost:8000
✓ API docs: http://localhost:8000/docs
✓ Health check: http://localhost:8000/health

### Step 5: Run Frontend (Terminal 2)
```bash
streamlit run streamlit_app_pdf.py
```

✓ Frontend running: http://localhost:8501

---

## 🧪 Test Your System

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 45,
  "components": {
    "gemini": "ok",
    "serper": "ok"
  }
}
```

### Test 2: Web Query
```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications in healthcare",
    "max_iterations": 2,
    "quality_threshold": 0.4
  }'
```

### Test 3: PDF Upload
```bash
curl -X POST http://localhost:8000/pdf \
  -F "file=@/path/to/sample.pdf"
```

### Test 4: In Streamlit UI
1. Open http://localhost:8501
2. Go to "Web Query" tab
3. Enter: "artificial intelligence trends 2024"
4. Click "Summarize"
5. Verify metrics display
6. Go to "PDF Upload" tab
7. Upload a PDF (test file)
8. Verify extraction and summarization

---

## 🐳 Docker Setup (Optional)

### Build Docker Image
```bash
docker build -t quickglance:latest .
```

### Run with Docker Compose
```bash
docker-compose up
```

- API: http://localhost:8000
- Web: http://localhost:8501

### Stop Services
```bash
docker-compose down
```

---

## 🌍 Deploy to Production

Choose ONE platform and follow its guide:

### Option 1: Render.com (⭐ RECOMMENDED)
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://render.com
# 3. Create new Web Service
# 4. Connect to your GitHub repo
# 5. Set environment variables:
#    - GEMINI_API_KEY
#    - SERPER_API_KEY
# 6. Deploy!

# Your URL: https://quickglance-api.onrender.com
```

**Why Render?**
- Free tier generous (750 compute hours/month)
- Git-based auto-deploy
- No credit card (unless want paid features)
- Perfect for starting projects

### Option 2: Railway.app
```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://railway.app
# 3. Create new project
# 4. Deploy from GitHub
# 5. Add environment variables
# 6. Done!

# Your URL: https://quickglance.railway.app
```

**Why Railway?**
- $5/month free credit
- Better scaling capabilities
- Faster inference
- More powerful free tier

### Option 3: HuggingFace Spaces
```bash
# 1. Create account at https://huggingface.co
# 2. Create new Space (Streamlit)
# 3. Upload all files:
#    - streamlit_app_pdf.py
#    - requirements-deploy.txt
# 4. Add secrets in Space settings:
#    - GEMINI_API_KEY
#    - SERPER_API_KEY
# 5. Streamlit loads automatically

# Your URL: https://huggingface.co/spaces/username/quickglance
```

**Why HuggingFace?**
- Simplest setup
- ML-optimized infrastructure
- Free unlimited public spaces
- GPU available (optional)

---

## 📊 Deployment Status Checklist

After deployment, verify:

- [ ] Public URL loads in browser
- [ ] Health check returns 200: `curl https://yoururl/health`
- [ ] Web query works
- [ ] PDF upload works
- [ ] Metrics display correctly
- [ ] Share URL with team

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app_fastapi:app --port 8001
```

### Streamlit can't connect to API
```bash
# Make sure backend is running
# Check API URL in streamlit_app_pdf.py (line ~20)

# Default: http://localhost:8000
# Deployed: https://yoururl (without /api)
```

### API returns 401 "Unauthorized"
```bash
# Check GEMINI_API_KEY in .env
# Verify key is valid: https://makersuite.google.com/app/apikey

# Test locally first before deploying
curl -H "X-Goog-Api-Key: YOUR_KEY" https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
```

### PDF upload fails
```bash
# Check file size (max 20MB)
# Ensure file is valid PDF
# Try sample PDF from: https://www.pdf-archive.com/

# For deployment, check server logs:
# Render: Dashboard → Logs
# Railway: Railway dashboard → Service logs
# HuggingFace: Space settings → Logs
```

### Slow responses
```bash
# Reduce quality_threshold (faster but less detailed)
# Reduce max_iterations (1 instead of 2)
# Use Railway/Render instead of HuggingFace (faster)
```

---

## 📈 Performance Tips

**For Web Queries:**
```python
# Default (balanced)
quality_threshold = 0.4
max_iterations = 2

# Faster (less detail)
quality_threshold = 0.3
max_iterations = 1

# Higher quality (slower)
quality_threshold = 0.6
max_iterations = 3
```

**For PDFs:**
- Ideal size: 5-50 MB
- Larger PDFs = slower processing
- Consider splitting large files

**For Production:**
- Use Railway or Render (not HuggingFace for API)
- Set `quality_threshold = 0.5` (balanced)
- Monitor uptime with: https://uptime.com

---

## 🚀 Next Steps

1. **Test Locally** (now)
2. **Deploy to Render/Railway** (5 min)
3. **Get public URL** (instant)
4. **Share with team** (now)
5. **Monitor logs** (daily)
6. **Optional: Add database** (for result history)

---

## 📚 Quick Reference

| Component | Port | URL |
|-----------|------|-----|
| FastAPI Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Streamlit UI | 8501 | http://localhost:8501 |
| Health Check | 8000 | http://localhost:8000/health |

| Platform | Free Tier | URL Format |
|----------|-----------|-----------|
| Render | 750 hrs/mo | https://projectname.onrender.com |
| Railway | $5 credit | https://projectname.railway.app |
| HuggingFace | Unlimited | https://huggingface.co/spaces/user/project |

---

## ✅ Success Criteria

Your deployment is successful when:

✓ Backend responds to `/health`
✓ Web queries return summaries
✓ PDF uploads extract and summarize
✓ Metrics display in Streamlit
✓ Public URL loads in browser
✓ Audio generation works (TTS)
✓ Exports work (CSV/JSON)

---

## 🆘 Get Help

For issues, check:

1. **Local test guide**: See "Test Your System" above
2. **API docs**: http://localhost:8000/docs (Swagger)
3. **Server logs**: Platform dashboard → Logs
4. **Troubleshooting**: See section above
5. **Documentation**: COMPLETE_DEPLOYMENT_GUIDE.md

