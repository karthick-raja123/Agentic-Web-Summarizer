# ⚡ 5-Minute Quickstart - Deploy to Production

## 🎯 Choose Your Platform

- **Render** ← Best all-around (free tier available)
- **Railway** ← Most affordable (usage-based)
- **HuggingFace** ← Best for UI only

---

## 🚀 Option 1: Render (Recommended)

### ✅ Prerequisites
- [ ] GitHub account with your code pushed
- [ ] `GOOGLE_API_KEY` and `SERPER_API_KEY` ready
- [ ] Render account (create at render.com)

### Steps

**Step 1: Create API Service (2 min)**
```
1. render.com/dashboard → "New +" → "Web Service"
2. Connect GitHub repository
3. Name: quickglance-api
4. Build Cmd: pip install -r requirements.txt
5. Start Cmd: uvicorn api:app --host 0.0.0.0 --port $PORT
6. Add environment variables:
   - GOOGLE_API_KEY
   - SERPER_API_KEY
7. Click "Create Web Service"
```

**Your API URL:** https://quickglance-api.onrender.com

**Step 2: Create UI Service (1 min)**
```
1. "New +" → "Web Service"
2. Same repository
3. Name: quickglance-ui
4. Start Cmd: streamlit run streamlit_enhanced_app.py --server.port=$PORT --server.address=0.0.0.0
5. Add same environment variables
6. Create
```

**Your UI URL:** https://quickglance-ui.onrender.com

**Step 3: Test (2 min)**
```bash
# Wait for deploy (2-3 min)
# Then test:
curl https://quickglance-api.onrender.com/health
```

✅ **Live in 5 minutes!**

---

## 🚂 Option 2: Railway (Most Affordable)

### ✅ Prerequisites
- [ ] GitHub account with pushed code
- [ ] API keys ready
- [ ] Railway account (railway.app)

### Steps

**Step 1: Connect GitHub (1 min)**
```
1. railway.app/dashboard → "New Project"
2. "Deploy from GitHub repo"
3. Select your repository
4. Click "Deploy Now"
```

Railway auto-detects `railway.toml` and deploys!

**Step 2: Add Secrets (1 min)**
```
1. Dashboard → Service → Settings
2. "Variables" → Add:
   - GOOGLE_API_KEY
   - SERPER_API_KEY
3. Redeploy
```

**Step 3: Get URLs (1 min)**
```
1. Each service → Settings
2. Copy the public URL
3. Test it
```

**Step 4: Test (2 min)**
```bash
curl https://your-api-url.up.railway.app/health
```

✅ **Live in 5 minutes!**

---

## 🤗 Option 3: HuggingFace (UI Only)

### ✅ Prerequisites
- [ ] HuggingFace account
- [ ] Code pushed to GitHub

### Steps

**Step 1: Create Space (1 min)**
```
1. huggingface.co/spaces → Create new Space
2. Space name: quickglance
3. License: Apache 2.0
4. Space SDK: Streamlit
5. Visibility: Public
6. Create Space
```

**Step 2: Push Code (1 min)**
```bash
# Clone your space
git clone https://huggingface.co/spaces/yourname/quickglance
cd quickglance

# Copy your files
cp /path/to/project/* .

# Push
git add .
git commit -m "Initial"
git push
```

**Step 3: Add Secrets (1 min)**
```
1. Space Settings → Repository secrets
2. Add: GOOGLE_API_KEY, SERPER_API_KEY
3. Done
```

**Step 4: Access (1 min)**
```
https://huggingface.co/spaces/yourname/quickglance
```

✅ **Live in 5 minutes!**

---

## ✨ After Deployment

### Test Everything

```bash
# 1. Check health
curl https://your-api-url.com/health

# 2. Try a query
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?"}'

# 3. View docs
# Open: https://your-api-url.com/docs

# 4. Try UI
# Open: https://your-ui-url.com
```

### Share with Others

**Send them these links:**
```
📖 API Documentation: https://your-api-url.com/docs
🎨 Live UI: https://your-ui-url.com
```

---

## 🆘 Troubleshooting (2 min)

### "Cannot connect"
```
→ Check platform dashboard for errors
→ Render/Railway free tier may sleep after 15 min
→ Visit once to wake up
```

### "Environment variables not found"
```
→ Check you added GOOGLE_API_KEY and SERPER_API_KEY
→ Restart service after adding
```

### "Query timeout"
```
→ Increase timeout in env: TIMEOUT=60
→ Or simplify your query
```

---

## 📊 Pricing Comparison

| Platform | Free Tier | Cost | Best For |
|----------|-----------|------|----------|
| **Render** | ✅ Yes | $0.50/mo | API + UI |
| **Railway** | ✅ Limited | $0.50/mo | Budget-conscious |
| **HuggingFace** | ✅ Yes | Free | Streamlit UI only |
| **Heroku** | ❌ No | $7+/mo | Deprecated |

---

## 🎯 Recommended Path

1. ✅ **Deploy API on Render** (5 min)
2. ✅ **Deploy UI on Render** (5 min)
3. ✅ **Test everything** (2 min)
4. ✅ **Share links** (1 min)

**Total: 13 minutes from now to production!**

---

## 📝 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `api.py` exists in root
- [ ] `requirements.txt` has all dependencies
- [ ] `streamlit_enhanced_app.py` exists
- [ ] API keys obtained from Google and Serper
- [ ] Platform account created (Render/Railway/HF)
- [ ] Services deployed
- [ ] Environment variables added
- [ ] /health endpoint returns 200
- [ ] Query endpoint works
- [ ] UI loads in browser
- [ ] Links shared

---

## 🔗 Your Deployment Links

**Save these after deployment:**

```
API Lives at:     https://your-api-url.com
API Docs:         https://your-api-url.com/docs
UI Lives at:      https://your-ui-url.com
```

---

## 📞 Need Help?

**Common Issues:**
1. Environment variables → Check platform dashboard
2. Deploy failed → Check logs in platform
3. API not responding → Restart service
4. UI can't find API → Add API_URL to secrets

**More Help:**
- Detailed guide: See `DEPLOYMENT_GUIDE.md`
- API reference: See `API_REFERENCE.md`
- URL help: See `LIVE_URL_GUIDE.md`

---

## 🎉 Congratulations!

You now have:
- ✅ Production FastAPI backend
- ✅ Streamlit web UI
- ✅ Live URLs
- ✅ Auto-deployment on push

**Everything is set up to scale! 🚀**

---

**Next Steps:**
1. Add custom domain (optional)
2. Set up monitoring (optional)
3. Add API authentication (optional)
4. Enable caching for speed (optional)

---

**Questions? Check the detailed guides in the repository!**
