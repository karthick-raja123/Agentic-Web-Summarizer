"""
COMPLETE DEPLOYMENT GUIDE: PDF Summarization + FastAPI + Streamlit

This guide covers deployment on:
1. Render.com (Recommended)
2. Railway.app
3. HuggingFace Spaces
4. Local Docker

Plus:
- Environment setup
- API endpoints
- Live system guide
- Troubleshooting
"""

# ============================================================================
# RENDER.COM DEPLOYMENT
# ============================================================================

"""
RENDER.COM (Recommended - Best UX)

Step 1: Create GitHub Repository
- Push code to GitHub
- Ensure .gitignore includes .env and __pycache__

Step 2: Login to Render
- Go to render.com
- Sign up with GitHub
- Connect your repository

Step 3: Deploy Backend (FastAPI)
- Create new Web Service
- Select your GitHub repo
- Configuration:
  Name: quickglance-api
  Branch: main
  Runtime: Python 3.11
  Build Command: pip install -r requirements-render.txt
  Start Command: uvicorn app_fastapi:app --host 0.0.0.0 --port $PORT

- Environment Variables:
  GEMINI_API_KEY=sk-xxxxx
  SERPER_API_KEY=xxxxx
  ENVIRONMENT=production

Step 4: Deploy Frontend (Streamlit)
- Create another Web Service
- Configuration:
  Name: quickglance-ui
  Branch: main
  Runtime: Python 3.11
  Build Command: pip install -r requirements-streamlit.txt
  Start Command: streamlit run streamlit_app_pdf.py --server.port $PORT --server.address 0.0.0.0

- Environment Variables:
  API_BASE_URL=https://quickglance-api.onrender.com
  STREAMLIT_SERVER_PORT=10000

Step 5: Access Your System
- Backend: https://quickglance-api.onrender.com
- Frontend: https://quickglance-ui.onrender.com
- API Docs: https://quickglance-api.onrender.com/docs

Cost: Free tier available, ~$7/month for small production
"""

# ============================================================================
# RAILWAY.APP DEPLOYMENT
# ============================================================================

"""
RAILWAY.APP (Alternative - Pay-as-you-go)

Step 1: Install Railway CLI
npm install -g @railway/cli
railway login

Step 2: Initialize Project
railway init
railway link

Step 3: Create Services
- Go to railway.app/dashboard
- Create new project
- Add Python service for backend
- Add Python service for frontend

Step 4: Configure Backend
Environment Variables:
  PYTHON_VERSION=3.11
  GEMINI_API_KEY=your_key
  SERPER_API_KEY=your_key
  ENVIRONMENT=production
  PORT=8000

Start Command: uvicorn app_fastapi:app --host 0.0.0.0

Step 5: Configure Frontend
Environment Variables:
  API_BASE_URL=https://yourbackend-url.railway.app
  STREAMLIT_SERVER_PORT=8501

Start Command: streamlit run streamlit_app_pdf.py

Step 6: Deploy
railway up

Cost: ~$5-15/month depending on usage
"""

# ============================================================================
# HUGGINGFACE SPACES DEPLOYMENT
# ============================================================================

"""
HUGGINGFACE SPACES (Free tier available)

Step 1: Create Space
- Go to huggingface.co/spaces
- Create new Space
- Choose Docker as runtime

Step 2: Upload Files
- requirements.txt
- app_fastapi.py
- streamlit_app_pdf.py
- langgraph_enhanced_multi_agent_system.py
- Dockerfile

Step 3: Create Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV SERPER_API_KEY=${SERPER_API_KEY}
ENV API_BASE_URL=http://localhost:8000

EXPOSE 7860 8000

CMD uvicorn app_fastapi:app --host 0.0.0.0 --port 8000 & \
    streamlit run streamlit_app_pdf.py --server.port 7860 --server.address 0.0.0.0

Step 4: Set Space Secrets
- Go to Settings > Secrets
- GEMINI_API_KEY=your_key
- SERPER_API_KEY=your_key

Step 5: Deploy
- Push to HuggingFace repo
- Auto-deploy triggers

Cost: Free (with limitations), $9/month Pro
"""

# ============================================================================
# DOCKER DEPLOYMENT (For Any Platform)
# ============================================================================

"""
DOCKER DEPLOYMENT (Render, AWS, DigitalOcean, etc.)

Step 1: Create Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV API_BASE_URL=http://localhost:8000

EXPOSE 8000 8501

CMD ["sh", "-c", " \\
    python app_fastapi.py & \\
    sleep 2 && \\
    streamlit run streamlit_app_pdf.py"]

Step 2: Build Image
docker build -t quickglance:latest .

Step 3: Run Locally
docker run -p 8000:8000 -p 8501:8501 \\
  -e GEMINI_API_KEY=your_key \\
  -e SERPER_API_KEY=your_key \\
  quickglance:latest

Step 4: Push to Registry
docker tag quickglance:latest yourusername/quickglance:latest
docker push yourusername/quickglance:latest
"""

# ============================================================================
# ENVIRONMENT VARIABLES SETUP
# ============================================================================

"""
STEP-BY-STEP: Get API Keys

1. GEMINI API KEY
   a. Go to console.cloud.google.com
   b. Create new project
   c. Search "Generative AI" in Services
   d. Click "Enable"
   e. Go to Credentials
   f. Create API Key
   g. Copy and save securely

2. SERPER API KEY
   a. Go to serper.dev
   b. Create free account
   c. Go to Dashboard
   d. Copy API key
   e. You get 100 free searches

LOCAL SETUP (.env file)
GEMINI_API_KEY=your_gemini_key_here
SERPER_API_KEY=your_serper_key_here
ENVIRONMENT=production
PORT=8000
API_BASE_URL=http://localhost:8000

RENDER SETUP
- Settings > Environment
- Add each key as separate variable
- Mark as secrets if sensitive
"""

# ============================================================================
# REQUIREMENTS FILES
# ============================================================================

"""
requirements-render.txt (for Render backend):
---
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
langgraph==0.0.13
google-generativeai==0.3.0
PyPDF2==3.17.1
python-multipart==0.0.6
gunicorn==21.2.0
---

requirements-streamlit.txt (for Render frontend):
---
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
langgraph==0.0.13
google-generativeai==0.3.0
PyPDF2==3.17.1
streamlit==1.28.1
---

requirements-base.txt (common):
---
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
langgraph==0.0.13
google-generativeai==0.3.0
PyPDF2==3.17.1
python-multipart==0.0.6
streamlit==1.28.1
---
"""

# ============================================================================
# LOCAL TESTING BEFORE DEPLOYMENT
# ============================================================================

"""
LOCAL SETUP & TESTING

1. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate    # Windows

2. Install Dependencies
pip install -r requirements-base.txt

3. Create .env file
GEMINI_API_KEY=your_key
SERPER_API_KEY=your_key
ENVIRONMENT=development

4. Start FastAPI Backend (Terminal 1)
python app_fastapi.py
# Or: uvicorn app_fastapi:app --reload
# Accessible at: http://localhost:8000

5. Start Streamlit Frontend (Terminal 2)
streamlit run streamlit_app_pdf.py
# Accessible at: http://localhost:8501

6. Test API Endpoints (Terminal 3)

Health Check:
curl http://localhost:8000/health

Web Summarization:
curl -X POST http://localhost:8000/summarize \\
  -H "Content-Type: application/json" \\
  -d '{"query": "machine learning", "max_iterations": 2}'

PDF Summarization:
curl -X POST http://localhost:8000/summarize/pdf \\
  -F "file=@test.pdf"

API Docs:
Visit http://localhost:8000/docs

7. Test in Streamlit
- Go to http://localhost:8501
- Try web query
- Try PDF upload
- Check API health in sidebar
"""

# ============================================================================
# API ENDPOINTS DOCUMENTATION
# ============================================================================

"""
API ENDPOINTS

1. GET /health
   Check if API is running
   
   Response:
   {
     "status": "healthy",
     "timestamp": "2026-04-07T...",
     "system": "QuickGlance Enhanced API",
     "version": "1.0.0"
   }

2. POST /summarize
   Summarize web topic
   
   Request:
   {
     "query": "machine learning in healthcare",
     "max_iterations": 2,
     "quality_threshold": 0.6
   }
   
   Response:
   {
     "query": "machine learning in healthcare",
     "summary": "...",
     "bullet_points": ["...", "..."],
     "quality_score": 0.82,
     "sources_used": 7,
     "processing_time": 38.5,
     "status": "success"
   }

3. POST /summarize/pdf
   Summarize uploaded PDF
   
   Request: multipart/form-data with file
   
   Response:
   {
     "filename": "document.pdf",
     "original_length": 1024000,
     "extracted_text_length": 512000,
     "summary": "...",
     "bullet_points": ["...", "..."],
     "processing_time": 45.2,
     "status": "success"
   }

4. GET /docs
   Interactive API documentation (Swagger UI)

5. GET /
   Root endpoint with API info
"""

# ============================================================================
# LIVE SYSTEM GUIDE
# ============================================================================

"""
LIVE SYSTEM ACCESS

After Deployment:

FRONTEND (Streamlit)
- URL: https://quickglance-ui.onrender.com
- Usage:
  1. Enter topic or upload PDF
  2. Click Summarize
  3. View results
  4. Download summary

BACKEND API
- URL: https://quickglance-api.onrender.com
- Documentation: https://quickglance-api.onrender.com/docs
- Health: https://quickglance-api.onrender.com/health

COMMAND LINE USAGE

Test Health:
curl https://quickglance-api.onrender.com/health

Summarize Web Content:
curl -X POST https://quickglance-api.onrender.com/summarize \\
  -H "Content-Type: application/json" \\
  -d '{"query": "artificial intelligence", "max_iterations": 2}'

Summarize PDF:
curl -X POST https://quickglance-api.onrender.com/summarize/pdf \\
  -F "file=@document.pdf"

MONITORING

Health Check:
- Regularly test /health endpoint
- Monitor response times
- Track error rates

Performance Metrics:
- Quality score (0.0-1.0)
- Processing time (seconds)
- Sources used (count)
- Success rate (%)

Common Issues:
- Timeout: Increase timeout in FastAPI
- PDF Error: Check file size and format
- API Down: Check logs in deployment dashboard
"""

# ============================================================================
# PRE-DEPLOYMENT CHECKLIST
# ============================================================================

"""
✅ DEPLOYMENT CHECKLIST

Before Deploying:
- [ ] .env file created with API keys
- [ ] API keys obtained (Gemini, Serper)
- [ ] requirements.txt files updated
- [ ] Local tests pass
- [ ] README.md updated with live URLs
- [ ] .gitignore includes .env
- [ ] No hardcoded secrets in code
- [ ] CORS middleware enabled
- [ ] Error handling implemented
- [ ] Logging configured

For Render:
- [ ] GitHub repository connected
- [ ] Environment variables set in dashboard
- [ ] Build command correct
- [ ] Start command correct
- [ ] Python version 3.11+
- [ ] Services auto-restart enabled

For Railway:
- [ ] Railway CLI installed
- [ ] Project initialized
- [ ] Services linked
- [ ] Environment variables set
- [ ] Start commands configured

For HuggingFace:
- [ ] Dockerfile created
- [ ] Requirements.txt provided
- [ ] Secrets configured
- [ ] Space created
- [ ] Files uploaded

General:
- [ ] DNS/Domain configured
- [ ] SSL certificates valid
- [ ] Monitoring set up
- [ ] Backup strategy planned
- [ ] Support plan ready
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
TROUBLESHOOTING GUIDE

ISSUE: API Not Responding
SOLUTION:
1. Check /health endpoint
2. View logs in dashboard
3. Check API key is valid
4. Verify network connectivity
5. Restart service

ISSUE: PDF Upload Fails
SOLUTION:
1. Check file size < 50MB
2. Verify file is valid PDF
3. Check PyPDF2 is installed
4. Check temp directory permissions
5. View error logs

ISSUE: Streamlit Can't Connect to API
SOLUTION:
1. Check API_BASE_URL is correct
2. Verify backend is running
3. Check CORS is enabled
4. Check firewall rules
5. Try direct API call: curl /health

ISSUE: Slow Performance
SOLUTION:
1. Check server resources
2. Reduce max_iterations
3. Monitor token usage
4. Check for memory leaks
5. Scale up resources

ISSUE: Timeout Errors
SOLUTION:
1. Increase timeout values (120s recommended)
2. Split large PDFs
3. Use async processing
4. Check API response times
5. Monitor server load

ISSUE: Out of Memory
SOLUTION:
1. Reduce PDF page limit
2. Implement streaming
3. Add pagination
4. Scale up server
5. Check for memory leaks
"""

# ============================================================================
# PRODUCTION SETUP CHECKLIST
# ============================================================================

"""
🚀 PRODUCTION CHECKLIST

Security:
- [ ] All secrets in environment variables
- [ ] HTTPS/SSL enabled
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] Rate limiting enabled
- [ ] API authentication (if needed)

Reliability:
- [ ] Error handling for all endpoints
- [ ] Logging to file/cloud
- [ ] Monitoring/alerts configured
- [ ] Backup strategy
- [ ] Disaster recovery plan
- [ ] Health checks automated

Performance:
- [ ] Caching implemented
- [ ] Database optimization (if applicable)
- [ ] CDN configured
- [ ] Load balancing (if needed)
- [ ] Auto-scaling rules
- [ ] Performance benchmarks

Operations:
- [ ] Documentation complete
- [ ] Runbooks created
- [ ] On-call process defined
- [ ] Update strategy planned
- [ ] Database migrations tested
- [ ] Rollback procedures documented
"""

# ============================================================================
# SUMMARY
# ============================================================================

"""
DEPLOYMENT SUMMARY

✅ WHAT YOU GET:
- FastAPI backend with PDF support
- Streamlit UI for easy access
- RESTful API endpoints
- Health monitoring
- Production-ready logging
- Error handling
- CORS enabled

✅ DEPLOYMENT OPTIONS:
1. Render.com - Recommended (Free + $ options)
2. Railway.app - Alternative (Pay-as-you-go)
3. HuggingFace Spaces - Free tier
4. Docker - Any cloud platform

✅ API ENDPOINTS:
1. GET /health - Health check
2. POST /summarize - Web summarization
3. POST /summarize/pdf - PDF summarization
4. GET /docs - API documentation
5. GET / - API info

✅ LIVE SYSTEM:
1. Frontend: Your Streamlit URL
2. Backend: Your FastAPI URL
3. Documentation: Backend /docs

✅ NEXT STEPS:
1. Get API keys (Gemini, Serper)
2. Choose deployment platform
3. Follow platform-specific steps
4. Test locally first
5. Deploy to production
6. Monitor and iterate

Ready to launch! 🚀
"""
