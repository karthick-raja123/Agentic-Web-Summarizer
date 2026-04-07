# QuickGlance: AI-Powered Web Summarization Agent

## 🚀 Project Overview

**QuickGlance** is a production-grade web intelligence system that automates searching, scraping, and summarizing web content. Built with LangGraph, Google Gemini, and Streamlit, it delivers actionable insights from the web in seconds.

### Key Capabilities
- 🔍 **Smart Web Search**: Uses Serper API for accurate Google-like results
- 🪄 **Intelligent Scraping**: Cleans HTML, removes noise, deduplicates content
- 📝 **AI Summarization**: Generates concise 5-point summaries with Gemini
- 💾 **Multiple Outputs**: CSV, TXT, and interactive web display
- ⚡ **Production-Ready**: Comprehensive logging, retry logic, error handling
- 🔒 **Secure**: All API keys in environment variables, no hardcoding

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ System Architecture

### High-Level Workflow

```
User Query
    ↓
Search Agent (Serper API) → Find URLs
    ↓
Scrape Agent (BeautifulSoup) → Extract & Clean Content
    ↓
Summarize Agent (Gemini LLM) → Generate Summary
    ↓
Output (CLI/Web UI/Downloads)
```

### Modular Structure

```
agents/
  ├── search_agent.py      → Query processing & URL retrieval
  ├── scrape_agent.py      → Content extraction & cleaning
  └── summarize_agent.py   → LLM-based summarization

services/
  ├── serper_service.py    → Search API client
  ├── scraping_service.py  → Web scraping engine
  └── llm_service.py       → Gemini wrapper

utils/
  ├── logging_config.py    → Structured logging
  ├── cleaning.py          → Text processing
  └── retry.py             → Retry decorators
```

### State Flow (LangGraph)

```python
AgentState = {
    "query": str,           # User's search query
    "urls": List[str],      # Found URLs
    "content": str,         # Scraped content
    "summary": str,         # Generated summary
    "status": str,          # Operation status
    "error": Optional[str]  # Error message
}
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- API keys from Serper and Google Gemini

### Step 1: Clone & Setup Environment

```bash
cd "d:\Git\Visual Web Agent\Visual-web-Agent"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Obtain API Keys

1. **Serper API** (Google Search):
   - Go to https://serper.dev
   - Sign up and get API key
   - Free tier: 100 searches/month

2. **Google Gemini**:
   - Go to https://makersuite.google.com/app/apikeys
   - Create API key
   - Enable generative AI API

### Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API keys
# Windows: Just edit the file directly
# Mac/Linux: nano .env
```

**Example .env file:**
```
GEMINI_API_KEY=AIzaSyD...your_key_here...
SERPER_API_KEY=5bb84fd...your_key_here...
LOG_LEVEL=INFO
DEBUG_MODE=false
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `SERPER_API_KEY` | ✅ | - | Serper search API key |
| `LOG_LEVEL` | ❌ | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `DEBUG_MODE` | ❌ | false | Enable verbose debugging |

### Pipeline Configuration (in code)

```python
pipeline = VisualWebAgentPipeline(
    num_search_results=5,      # URLs to fetch
    summary_points=5,          # Bullet points in summary
    use_chunking=False         # Hierarchical summarization
)
```

### Service Customization

**ScrapeAgent**:
```python
scrape_agent = ScrapeAgent(
    max_content_per_url=10000,    # Chars per URL
    max_total_content=30000        # Total combined chars
)
```

**SummarizeAgent**:
```python
summarize_agent = SummarizeAgent(
    summary_points=5,              # Output bullet points
    use_chunks=True                # Use chunking for large docs
)
```

---

## 🎯 Usage

### Method 1: CLI (Command Line)

```bash
python main.py
```

**Interactive Input**:
```
Enter your topic to summarize: What are quantum computers?
```

**Output**:
```
Fetched URLs:
1. https://www.example.com/quantum...
2. https://www.example.com/computers...
3. https://www.example.com/quantum-2...

----- SUMMARY -----
• Quantum computers use quantum bits (qubits)...
• They can solve certain problems faster...
• Current applications are limited...
• Major tech companies are investing heavily...
• Timeline for practical quantum computing...
```

### Method 2: Web UI (Streamlit)

```bash
streamlit run app.py
```

Then open browser to `http://localhost:8501`

**Features**:
- ✅ Text input for queries
- ✅ Adjustable parameters (results, summary points)
- ✅ Real-time processing with spinners
- ✅ Download as CSV or TXT
- ✅ Debug mode for troubleshooting

### Method 3: As a Python Module

```python
from main import VisualWebAgentPipeline

# Initialize
pipeline = VisualWebAgentPipeline(
    num_search_results=5,
    summary_points=5
)

# Run query
result = pipeline.run("AI in healthcare")

# Access results
print(f"Status: {result['status']}")
print(f"URLs: {result['urls']}")
print(f"Summary: {result['summary']}")
```

---

## 📚 API Reference

### Main Pipeline

```python
class VisualWebAgentPipeline:
    def run(query: str) -> dict
    """
    Execute complete pipeline.
    
    Args:
        query: Search query
    
    Returns:
        {
            "query": str,
            "urls": List[str],
            "content": str,
            "summary": str,
            "status": "success" | "failed",
            "error": Optional[str]
        }
    """
```

### Agents

#### SearchAgent
```python
search_agent.execute(query: str) -> dict
    # Returns: {"urls": [...], "status": "success"}

search_agent.execute_with_metadata(query: str) -> dict
    # Returns: {"results": [{"title": ..., "snippet": ..., "link": ...}], "status": ...}
```

#### ScrapeAgent
```python
scrape_agent.execute(urls: List[str]) -> dict
    # Returns: {"content": str, "url_count": int, "status": "success"}

scrape_agent.execute_for_urls(urls: List[str]) -> dict
    # Returns: {"url_contents": {url: content}, "status": "success"}
```

#### SummarizeAgent
```python
summarize_agent.execute(content: str) -> dict
    # Returns: {"summary": str, "token_estimate": int, "status": "success"}

summarize_agent.execute_with_chunking(content: str) -> dict
    # Returns: {"summary": str, "chunk_count": int, "status": "success"}
```

### Services

#### SerperService
```python
service = SerperService(api_key=None)

service.search(query: str, num_results: int = 10) -> List[str]
    # Returns list of URLs

service.search_with_metadata(query: str, num_results: int = 5) -> List[dict]
    # Returns list of {"title": ..., "snippet": ..., "link": ...}
```

#### ScrapingService
```python
service = ScrapingService(timeout=10, max_content_length=50000)

service.fetch_content(url: str) -> Optional[str]
    # Returns cleaned content or None

service.fetch_multiple(urls: List[str]) -> dict
    # Returns {url: content} mapping

service.combine_contents(contents: dict, max_chars: int) -> str
    # Returns combined content
```

#### LLMService
```python
service = LLMService(api_key=None, model="gemini-1.5-flash")

service.summarize(content: str, max_length: int = 5) -> str
    # Returns bullet-point summary

service.generate(prompt: str) -> str
    # Returns generated text

service.estimate_tokens(text: str) -> int
    # Returns estimated token count
```

### Utilities

#### Logging
```python
from utils import get_logger

logger = get_logger(__name__)
logger.info("Info message")
logger.error("Error message")
```

#### Text Cleaning
```python
from utils import clean_content, chunk_text, deduplicate_content

cleaned = clean_content(html_text)
chunks = chunk_text(text, chunk_size=3000)
unique = deduplicate_content(paragraphs)
```

#### Retry Decorator
```python
from utils import retry

@retry(max_attempts=3, delay=2.0, backoff=2.0, exceptions=(TimeoutError,))
def my_function():
    ...
```

---

## 🚀 Advanced Features

### Hierarchical Summarization

For long documents, use hierarchical summarization:

```python
result = summarize_agent.execute_with_chunking(
    content=long_content,
    chunk_size=5000
)
```

This:
1. Splits content into 5000-char chunks
2. Summarizes each chunk
3. Creates a meta-summary from all summaries

### Token Optimization

Automatic token management:
- ✅ Content truncation before LLM calls
- ✅ Chunk-based processing
- ✅ Token estimation
- ✅ Per-URL content limiting

### Content Deduplication

Automatic detection and removal of:
- Duplicate paragraphs
- Similar content (Jaccard similarity >0.85)
- Script/style tags
- Minimal paragraphs (<30 chars)

### Retry Mechanism

Automatic retry with exponential backoff:
```
Attempt 1 → Failure → Wait 1s
Attempt 2 → Failure → Wait 1.5s
Attempt 3 → Failure → Error logged
```

---

## 📊 Performance Guidelines

### API Costs (Approximate)

| API | Free Tier | Cost per 1000 |
|-----|-----------|---------------|
| Serper Search | 100 searches/month | $5-20 |
| Gemini 1.5 Flash | 15 RPM, 1M/day tokens | Pay-as-you-go |

### Optimization Tips

1. **Reduce URLs**: Use `num_search_results=3` instead of 10
2. **Smaller Summaries**: Use `summary_points=3` instead of 5
3. **Disable Chunking**: Set `use_chunking=False` for short content
4. **Cache Results**: Store summaries locally
5. **Batch Queries**: Process multiple queries at once

### Performance Targets

- Search + Scrape: ~3-5 seconds
- Summarization: ~2-3 seconds
- **Total**: ~5-8 seconds per query

---

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution**:
1. Check `.env` file exists
2. Verify key is set: `echo %GEMINI_API_KEY%` (Windows) or `echo $GEMINI_API_KEY` (Mac)
3. Restart terminal and virtual environment

### Issue: API Rate Limit Error

**Solution**:
1. Reduce `num_search_results` value
2. Add delay between requests: `time.sleep(2)` between queries
3. Upgrade API plan if using free tier

### Issue: "No content to summarize"

**Solutions**:
1. Check internet connection
2. Verify URLs are accessible (try in browser)
3. Check firewall/proxy settings
4. Increase timeout: `timeout=15` in ScrapingService

### Issue: Streamlit Not Starting

**Solution**:
```bash
# Clear cache
streamlit cache clear

# Check port is available
netstat -an | grep 8501

# Run on different port
streamlit run app.py --server.port 8502
```

### Issue: Memory Error

**Solution**:
```python
# Reduce content limits
scrape_agent = ScrapeAgent(
    max_content_per_url=5000,
    max_total_content=15000
)
```

### Issue: Timeout Error (Too Slow)

**Solution**:
1. Check internet speed
2. Reduce `num_search_results`
3. Reduce `max_content_per_url`
4. Enable `use_chunking=False`
5. Use faster summarization model

### Debug Mode

For detailed troubleshooting:

```python
import logging
from utils import get_logger

logger = get_logger("DEBUG")
logger.setLevel(logging.DEBUG)
```

Check logs in `logs/app.log`.

---

## 📝 Examples

### Example 1: Quick Summary

```python
from main import VisualWebAgentPipeline

pipeline = VisualWebAgentPipeline()
result = pipeline.run("Python best practices 2024")

print(result["summary"])
```

### Example 2: Batch Processing

```python
queries = [
    "Machine learning trends",
    "Cloud computing",
    "DevOps best practices"
]

pipeline = VisualWebAgentPipeline()

for query in queries:
    result = pipeline.run(query)
    print(f"\n{query}:")
    print(result["summary"])
```

### Example 3: Custom Configuration

```python
pipeline = VisualWebAgentPipeline(
    num_search_results=10,    # Get more sources
    summary_points=7,         # Longer summary
    use_chunking=True         # For long documents
)

result = pipeline.run("Comprehensive AI guide")
```

---

## 📄 License

MIT License - Feel free to use for personal and commercial projects

---

## 🤝 Contributing

To extend the system:

1. Create new agent in `agents/`
2. Add service in `services/` if needed
3. Use existing logging and retry patterns
4. Write tests in `tests/`
5. Update documentation

---

## 📞 Support

For issues or questions:
1. Check `TROUBLESHOOTING` section above
2. Review logs in `logs/app.log`
3. Enable DEBUG mode
4. Check API credentials and quotas

---

**Version**: 1.0 | **Status**: Production-Ready ✅
