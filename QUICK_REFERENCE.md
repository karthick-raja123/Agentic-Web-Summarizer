# 🚀 QUICK REFERENCE CARD

## ⚡ Getting Started (5 Minutes)

### Step 1: Setup Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure API Keys
```bash
cp .env.example .env
# Edit .env with your keys:
# GEMINI_API_KEY=your_key
# SERPER_API_KEY=your_key
```

### Step 3: Run
```bash
# Option 1: Web UI
streamlit run app.py
# Opens: http://localhost:8501

# Option 2: CLI
python main.py

# Option 3: Docker
docker build -t quickglance .
docker run -p 8501:8501 --env-file .env quickglance
```

---

## 📂 Project Structure

```
agents/
  ├─ search_agent.py      → Find URLs
  ├─ scrape_agent.py      → Extract content
  └─ summarize_agent.py   → Create summary

services/
  ├─ serper_service.py    → Serper API (search)
  ├─ scraping_service.py  → Web scraper
  └─ llm_service.py       → Gemini LLM

utils/
  ├─ logging_config.py    → Logging system
  ├─ cleaning.py          → Text processing
  └─ retry.py             → Automatic retry

main.py                    → Pipeline orchestrator
app.py                     → Streamlit web UI
```

---

## 🎯 Common Commands

### Makefile
```bash
make help              # See all commands
make install           # Install deps
make web              # Run web UI
make cli              # Run CLI
make test             # Run tests
make docker-build     # Build image
make docker-run       # Run container
```

### Manual
```bash
# Web UI
streamlit run app.py

# CLI
python main.py

# Testing
pytest tests_example.py -v

# Docker
docker-compose up --build
docker-compose down
docker-compose logs -f
```

---

## 🔧 Configuration

### Environment Variables (.env)
```ini
# Required
GEMINI_API_KEY=your_gemini_key
SERPER_API_KEY=your_serper_key

# Optional
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
DEBUG_MODE=false

# Pipeline settings (in code)
num_search_results=5        # URLs to fetch
summary_points=5            # Bullet points
use_chunking=False          # Hierarchical summarization
```

---

## 💻 Usage Examples

### Python Code
```python
from main import VisualWebAgentPipeline

pipeline = VisualWebAgentPipeline()
result = pipeline.run("What is machine learning?")

print(result["summary"])
# Output: • Machine learning is a subset of AI...
```

### CLI
```bash
$ python main.py
Enter topic: Quantum computing
[Processing...]
• Quantum computing uses qubits...
```

### Streamlit
```
1. Open http://localhost:8501
2. Enter query
3. Click "Search, Scrape & Summarize"
4. Download results (CSV/TXT)
```

---

## 📊 Pipeline Workflow

```
User Query
     ↓
SearchAgent (Serper API)
  ↓ URLs
ScrapeAgent (BeautifulSoup)
  ↓ Content
SummarizeAgent (Gemini LLM)
  ↓ Summary
Output (Display/Download)
```

Each stage:
- ✅ Retries automatically (3 attempts)
- ✅ Logs everything (DEBUG/INFO/ERROR)
- ✅ Handles errors gracefully
- ✅ Optimizes token usage

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
```bash
# Solution:
1. Check .env file exists
2. Verify key is set: echo %GEMINI_API_KEY%
3. Restart terminal and activate venv
```

### "Connection timeout"
```bash
# Solution:
1. Check internet
2. Reduce num_search_results=3
3. Increase timeout: ScrapingService(timeout=15)
```

### Streamlit won't start
```bash
# Solution:
streamlit cache clear
streamlit run app.py --server.port 8502  # Use different port
```

### High memory usage
```python
# Solution: Reduce content limits
ScrapeAgent(
    max_content_per_url=5000,      # was 10000
    max_total_content=15000         # was 30000
)
```

---

## 📚 Documentation Map

| Document | For | Time |
|----------|-----|------|
| This file | Quick start | 5 min |
| README_REFACTORED.md | Full guide | 30 min |
| ARCHITECTURE.md | Tech details | 20 min |
| REFACTORING_SUMMARY.md | Changes | 10 min |
| DELIVERY_CHECKLIST.md | What's included | 5 min |

---

## ✨ Key Features

✅ **Zero Hardcoded Keys** - All in .env  
✅ **Smart Retries** - Exponential backoff  
✅ **Advanced Scraping** - Clean, dedup, chunk  
✅ **Production Logging** - Rotating files  
✅ **Error Handling** - Graceful degradation  
✅ **Token Optimization** - Smart truncation  
✅ **Modular Design** - Easy to extend  
✅ **Docker Ready** - Containerized  
✅ **Well Documented** - 1500+ lines  
✅ **Tested** - Examples included  

---

## 🎓 Learning Path

### Beginner (30 min)
1. Read this file
2. Run `streamlit run app.py`
3. Try a few searches

### Intermediate (1-2 hours)
1. Read README_REFACTORED.md
2. Review main.py code
3. Customize configurations

### Advanced (1-2 days)
1. Study ARCHITECTURE.md
2. Add custom agents
3. Extend services
4. Deploy to cloud

---

## 🚢 Deployment

### Local
```bash
streamlit run app.py
```

### Docker
```bash
docker build -t quickglance .
docker run -p 8501:8501 --env-file .env quickglance
```

### Docker Compose
```bash
docker-compose up --build
```

### Cloud (Google Cloud Run)
```bash
gcloud run deploy quickglance \
  --source . \
  --platform managed \
  --allow-unauthenticated
```

---

## 📞 API Reference (Quick)

### Pipeline
```python
result = pipeline.run(query: str)
# Returns: {status, urls, content, summary, error}
```

### Agents
```python
search_agent.execute(query) → {urls, status}
scrape_agent.execute(urls) → {content, url_count, status}
summarize_agent.execute(content) → {summary, status}
```

### Services
```python
serper.search(query) → List[urls]
scraper.fetch_content(url) → str
llm.summarize(content) → str
```

---

## 💡 Pro Tips

#### 1. Batch Processing
```python
queries = ["AI", "ML", "DL"]
for q in queries:
    result = pipeline.run(q)
    print(result["summary"])
```

#### 2. Save Results
```python
import json
with open("results.json", "w") as f:
    json.dump(result, f, indent=2)
```

#### 3. Monitor Logs
```bash
# In another terminal
tail -f logs/app.log
```

#### 4. Performance Optimization
```python
# Faster but less comprehensive
pipeline = VisualWebAgentPipeline(
    num_search_results=3,      # was 5
    summary_points=3,          # was 5
    use_chunking=False         # was True
)
```

---

## 📋 Checklist Before First Use

- [ ] Python 3.8+ installed
- [ ] pip works (`pip --version`)
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with API keys
- [ ] GEMINI_API_KEY set and valid
- [ ] SERPER_API_KEY set and valid
- [ ] Internet connection working
- [ ] Port 8501 is free (for Streamlit)
- [ ] Ready to run!

---

## 🎯 What's Next?

### After First Run
```
1. ✅ Test with 2-3 different queries
2. ✅ Check logs in logs/app.log
3. ✅ Try downloading CSV
4. ✅ Explore configuration options
```

### First Week
```
1. ✅ Share with team
2. ✅ Deploy to Docker
3. ✅ Setup automatic backups
4. ✅ Monitor API usage
```

### First Month
```
1. ✅ Add custom integrations
2. ✅ Setup database
3. ✅ Create REST API
4. ✅ Add user authentication
```

---

## 🏆 You're All Set!

```
✅ Production-grade architecture
✅ Modular, secure, well-documented
✅ Ready for team use
✅ Easy to deploy
✅ Simple to extend

Happy searching! 🚀
```

---

**Need Help?**
- Full guide: README_REFACTORED.md
- Technical: ARCHITECTURE.md
- Troubleshooting: Scroll up or check logs
- Questions: Try Debug Mode (LOG_LEVEL=DEBUG)

**Last Updated**: January 2024  
**Status**: Production Ready ✅
