# 🏗️ Architecture & Deployment Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Streamlit Web App (streamlit_app_pdf.py)         │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Tab 1: Web Query        │  Tab 2: PDF Upload     │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ • Search input           │ • PDF file upload      │  │   │
│  │  │ • Query settings         │ • File validation      │  │   │
│  │  │ • Summarize button       │ • Extract text        │  │   │
│  │  │ • Results display        │ • Summarize           │  │   │
│  │  │ • Metrics dashboard      │ • Results + metrics   │  │   │
│  │  │ • Audio generation       │ • Exports             │  │   │
│  │  │ • CSV/JSON exports       │                       │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                             │   │
│  │              HTTP Client (requests library)                │   │
│  │                         ↓                                  │   │
│  │                 http://localhost:8000                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         (Port 8501)                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        FastAPI Backend (app_fastapi.py)                  │   │
│  │                    (Port 8000)                           │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │              API Endpoints                         │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ POST   /summarize    Web query summarization      │  │   │
│  │  │ POST   /pdf          PDF upload & extraction      │  │   │
│  │  │ POST   /batch        Batch process queries        │  │   │
│  │  │ GET    /health       System health check          │  │   │
│  │  │ GET    /metrics      Performance metrics          │  │   │
│  │  │ GET    /docs         API documentation (Swagger)  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │                                                             │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │       Request Processing Pipeline                 │  │   │
│  │  ├────────────────────────────────────────────────────┤  │   │
│  │  │ 1. Validate Request (CORS, auth, format)         │  │   │
│  │  │ 2. Extract Data (query or PDF text)              │  │   │
│  │  │ 3. Pre-process (chunking, cleaning)              │  │   │
│  │  │ 4. Call LangGraph Agent System                   │  │   │
│  │  │ 5. Post-process (formatting, metrics)            │  │   │
│  │  │ 6. Return Response (summary + stats)             │  │   │
│  │  │ 7. Error Handling & Fallbacks                    │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   INTELLIGENCE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LangGraph Multi-Agent System (agentic_browser_...)      │   │
│  │               (10 Specialized Agents)                    │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Agent Layer                                      │  │   │
│  │  ├─────────────────────────────────────────────────┤  │   │
│  │  │ • Query Expansion Agent (→ 3 queries)          │  │   │
│  │  │ • Search Agent (web search via Serper)         │  │   │
│  │  │ • Ranking Agent (quality-first sorting)        │  │   │
│  │  │ • Dedup Agent (remove repeated info)           │  │   │
│  │  │ • Chunk Agent (split for token limits)         │  │   │
│  │  │ • Summarization Agent (Gemini Pro)             │  │   │
│  │  │ • Reflection Agent (quality check)             │  │   │
│  │  │ • Fallback Agent (heuristics if needed)        │  │   │
│  │  │ + More...                                       │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                         │   │
│  │  Features: Parallel processing, intelligent routing   │   │
│  │            Token optimization, quality scoring        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL APIs LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐      ┌──────────────────────┐          │
│  │   Google Gemini Pro │      │   Serper Web Search  │          │
│  │                     │      │                      │          │
│  │ • Summarization     │      │ • Query expansion    │          │
│  │ • Text generation   │      │ • Web search results │          │
│  │ • Quality analysis  │      │ • Content ranking    │          │
│  │                     │      │                      │          │
│  └─────────────────────┘      └──────────────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Web Query Example

```
User Input (Streamlit)
    ↓
"machine learning in healthcare"
    ↓
HTTP POST to /summarize
    ↓
FastAPI validates request
    ↓
Call LangGraph Multi-Agent System
    ├─→ Query Expansion Agent: Creates 3 queries
    │   - "machine learning healthcare applications"
    │   - "AI medical diagnosis"
    │   - "neural networks treatment"
    │
    ├─→ Search Agent: Submit to Serper API
    │   - Get 10 results per query
    │   - Total: 30 web results
    │
    ├─→ Ranking Agent: Score & sort by quality
    │   - Quality score: 0-1
    │   - Filter low-quality results
    │
    ├─→ Dedup Agent: Remove duplicates
    │   - Consolidate similar results
    │   - Final: ~20 unique results
    │
    ├─→ Chunk Agent: Split for token limits
    │   - Max 2000 chars per chunk
    │   - ~10 chunks
    │
    ├─→ Summarization Agent: Process each chunk
    │   - Call Gemini Pro for summaries
    │   - Extract key points
    │
    ├─→ Reflection Agent: Quality check
    │   - Score final summary (0-1)
    │   - Verify relevance
    │
    └─→ Return Response
        {
          "summary": "Comprehensive summary text...",
          "bullets": ["Key point 1", "Key point 2", ...],
          "quality_score": 0.82,
          "reflection_score": 0.78,
          "sources_used": 20,
          "processing_time_ms": 4500,
          "iterations_used": 2
        }
    ↓
FastAPI computes metrics
    ↓
HTTP 200 Response to Streamlit
    ↓
Streamlit displays results
    ├─→ Show summary text
    ├─→ Show bullet points
    ├─→ Display metrics (quality, sources, time)
    ├─→ Generate audio (TTS)
    └─→ Show export options
    ↓
User sees formatted results
```

---

## Data Flow: PDF Upload Example

```
User Upload (Streamlit)
    ↓
Select PDF file (max 20MB)
    ↓
HTTP POST to /pdf with multipart form
    ↓
FastAPI validates PDF
    ├─→ Check file format
    └─→ Check file size
    ↓
Extract text using PyPDF2
    ├─→ Read all pages
    ├─→ Combine text
    └─→ ~20,000 characters
    ↓
Split into chunks (chunk_size=2000)
    ├─→ Chunk 1: ~2000 chars
    ├─→ Chunk 2: ~2000 chars
    ├─→ Chunk 3: ~2000 chars
    └─→ Total: ~10 chunks
    ↓
Process each chunk through LangGraph
    ├─→ For each chunk:
    │   ├─→ Chunk processing agent
    │   ├─→ Summarization via Gemini
    │   ├─→ Extract key points
    │   └─→ Quality score
    ↓
Combine chunk summaries
    ├─→ Merge all summaries
    ├─→ Remove duplicates
    ├─→ Create final summary
    ↓
Compute final metrics
    ├─→ Overall quality score
    ├─→ Total sources: ~10 chunks
    ├─→ Processing time
    ↓
Return Response
    {
      "summary": "Combined PDF summary...",
      "bullets": ["Key finding 1", "Key finding 2", ...],
      "quality_score": 0.79,
      "reflection_score": 0.75,
      "sources_used": 10,  # chunks
      "processing_time_ms": 8500,
      "iterations_used": 2,
      "pdf_metadata": {
        "pages": 5,
        "chunks": 10,
        "total_chars": 20000
      }
    }
    ↓
Streamlit displays PDF results
```

---

## Deployment Architecture

### Local Development
```
Your Computer
├─ Terminal 1: FastAPI Backend (8000)
│  └─ python -m uvicorn app_fastapi:app --reload
│
├─ Terminal 2: Streamlit Frontend (8501)
│  └─ streamlit run streamlit_app_pdf.py
│
└─ .env: Contains API keys
   └─ GEMINI_API_KEY=xxx
   └─ SERPER_API_KEY=xxx
```

### Docker Local
```
Docker Engine
├─ Container: API
│  ├─ Port 8000
│  ├─ app_fastapi.py
│  └─ Logs: /app/logs
│
└─ Container: Web
   ├─ Port 8501
   ├─ streamlit_app_pdf.py
   └─ Logs: /app/logs
```

### Render Production
```
Render.com
├─ Service 1: API Backend
│  ├─ Python 3.11
│  ├─ Start: uvicorn app_fastapi:app --host 0.0.0.0 --port $PORT
│  ├─ URL: https://quickglance-api.onrender.com
│  ├─ Env Vars: GEMINI_API_KEY, SERPER_API_KEY
│  ├─ Free Tier: 750 hrs/month, 0.5 GiB RAM
│  └─ Auto-deploy on git push
│
└─ Service 2: Web Frontend
   ├─ Python 3.11
   ├─ Start: streamlit run streamlit_app_pdf.py --server.port=$PORT
   ├─ URL: https://quickglance-web.onrender.com
   ├─ Env Vars: API_URL=https://quickglance-api.onrender.com
   ├─ Free Tier: 750 hrs/month, shared
   └─ Auto-deploy on git push
```

### Railway Production
```
Railway.app
├─ Service 1: API Backend
│  ├─ Docker or Python
│  ├─ Port: 8000
│  ├─ URL: https://quickglance-api.railway.app
│  ├─ Env Vars: GEMINI_API_KEY, SERPER_API_KEY
│  ├─ Pay: $5/month free credit + usage
│  └─ No auto-sleep
│
└─ Service 2: Web Frontend
   ├─ Docker or Python
   ├─ Port: 8501
   ├─ URL: https://quickglance-web.railway.app
   ├─ Env Vars: API_URL=https://quickglance-api.railway.app
   └─ Faster than Render
```

### HuggingFace Spaces Production
```
HuggingFace.co/Spaces
├─ Space Type: Streamlit
├─ Runtime: A10G Spaces (optional)
├─ URL: https://huggingface.co/spaces/username/quickglance
├─ Secrets: GEMINI_API_KEY, SERPER_API_KEY
├─ Auto-deploy: Git push to Space repo
└─ Best for: Streamlit UI only (no separate API)
```

---

## Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Local Setup (5 min)                            │
├─────────────────────────────────────────────────────────┤
│ • Create virtual environment                            │
│ • Install requirements-deploy.txt                       │
│ • Create .env with API keys                            │
│ • Run setup script (Windows/Mac)                        │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: Local Testing (10 min)                         │
├─────────────────────────────────────────────────────────┤
│ • Start FastAPI backend (port 8000)                     │
│ • Start Streamlit frontend (port 8501)                  │
│ • Test /health endpoint                                 │
│ • Test web query in UI                                  │
│ • Test PDF upload in UI                                 │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Step 3: Code Preparation (2 min)                       │
├─────────────────────────────────────────────────────────┤
│ • Commit code to GitHub                                 │
│ • Ensure .env NOT in git                                │
│ • Create deployment platform account                    │
└────────────────┬────────────────────────────────────────┘
                 ↓
                 │
      ┌──────────┼──────────┐
      ↓          ↓          ↓
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Render   │ │ Railway  │ │ HuggingFace  │
└──────────┘ └──────────┘ └──────────────┘
      ↓          ↓          ↓
┌──────────────────────────────────────────────┐
│ Step 4: Deploy to Chosen Platform (5-10 min)│
├──────────────────────────────────────────────┤
│ • Connect GitHub repo                        │
│ • Configure environment variables            │
│ • Trigger deploy                             │
│ • Wait for build/deploy completion           │
└──────────────┬───────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Step 5: Verify Deployment (5 min)                      │
├─────────────────────────────────────────────────────────┤
│ • Get public URL                                        │
│ • Test /health endpoint on public URL                   │
│ • Test web query via public frontend                    │
│ • Test PDF upload via public frontend                   │
│ • Check all features working                            │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Step 6: Production Ready! (1 min)                      │
├─────────────────────────────────────────────────────────┤
│ ✅ Public URL working                                    │
│ ✅ API endpoints functional                             │
│ ✅ UI responsive                                        │
│ ✅ Ready to share with team/users                       │
└─────────────────────────────────────────────────────────┘
```

---

## Component Communication

```
Internet
    ↓
┌─────────────────────────┐
│  Public URL (Render)    │
│ quickglance-api.        │
│ onrender.com            │
└────────────┬────────────┘
             ↓
      ┌──────────────────────┐
      │  Render Proxy        │
      │  (HTTPS → HTTP)      │
      └──────────┬───────────┘
                 ↓
    ┌────────────────────────────┐
    │  FastAPI Backend (8000)    │
    │  • Validate requests       │
    │  • Route to agents         │
    │  • Call external APIs      │
    │  • Send responses          │
    └────┬───────────────────────┘
         ↓ (Internal network)
    ┌────────────────────────────┐
    │  Google Gemini Pro API     │
    │  Serper Search API         │
    └────────────────────────────┘
    
    ┌────────────────────────────┐
    │  Streamlit Frontend (8501) │
    │  • HTTP Client             │
    │  • Connect to API:8000     │
    │  • Display results         │
    │  • Process uploads         │
    └────┬───────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  Browser (User)            │
    │  https://quickglance-....  │
    │  .onrender.com             │
    └────────────────────────────┘
```

---

## Technology Stack Summary

```
┌─────────────────────────────────────┐
│  FRONTEND                           │
│  • Streamlit (Web UI)              │
│  • Python 3.11                     │
│  • requests (HTTP client)          │
│  • gTTS (Audio generation)         │
│  • pandas (Data handling)          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  BACKEND                            │
│  • FastAPI (API framework)          │
│  • Uvicorn (ASGI server)           │
│  • Python 3.11                     │
│  • PyPDF2 (PDF processing)         │
│  • python-multipart (File uploads)  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  INTELLIGENCE                       │
│  • LangGraph (Agent orchestration)  │
│  • Google Gemini Pro (LLM)         │
│  • Serper API (Web search)         │
│  • BeautifulSoup4 (Web scraping)   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  DEPLOYMENT                         │
│  • Docker (Containerization)        │
│  • Docker Compose (Multi-container) │
│  • Render.com (Recommended)        │
│  • Railway.app (Alternative)       │
│  • HuggingFace Spaces (Simplest)   │
└─────────────────────────────────────┘
```

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready
