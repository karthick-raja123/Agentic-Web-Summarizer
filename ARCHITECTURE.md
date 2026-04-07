# Architecture Documentation

## Visual Web Agent - Production-Grade Refactoring

### Overview
This is a complete refactoring of the Visual Web Agent system into a production-grade, modular architecture following best practices for maintainability, scalability, and reliability.

### Folder Structure

```
Visual-web-Agent/
├── agents/                    # LangGraph workflow agents
│   ├── __init__.py
│   ├── search_agent.py       # Web search via Serper API
│   ├── scrape_agent.py       # Content scraping and cleaning
│   └── summarize_agent.py    # LLM-based summarization
│
├── services/                  # External API integrations
│   ├── __init__.py
│   ├── llm_service.py        # Gemini LLM wrapper
│   ├── scraping_service.py   # Web scraping service
│   └── serper_service.py     # Serper search API client
│
├── utils/                     # Shared utilities
│   ├── __init__.py
│   ├── logging_config.py     # Centralized logging
│   ├── cleaning.py           # Text cleaning & deduplication
│   └── retry.py              # Retry decorator & utilities
│
├── main.py                    # LangGraph pipeline orchestrator
├── app.py                     # Streamlit web UI
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── logs/                      # Runtime logs (auto-created)
```

### Architecture Highlights

#### 1. **Modular Design**
- **Agents**: Independent units responsible for specific tasks (Search, Scrape, Summarize)
- **Services**: Encapsulate API integrations and business logic
- **Utils**: Reusable utilities for logging, text cleaning, and retry logic

#### 2. **LangGraph Pipeline**
```
User Query → Search Agent → Scrape Agent → Summarize Agent → Result
```
- State-driven workflow with TypedDict for type safety
- Easy to extend with new agents
- Proper error propagation at each stage

#### 3. **Robust Error Handling**
- **Retry Decorator**: Exponential backoff for transient failures
- **Try-Catch Blocks**: Comprehensive error handling in services
- **Logging**: DEBUG/INFO/ERROR levels for troubleshooting

#### 4. **Configuration Management**
- Environment variables via `.env` file
- No hardcoded API keys or secrets
- Easy to switch between development and production configs

#### 5. **Content Processing**
- Script/style removal from HTML
- Meaningful paragraph extraction (minimum length filtering)
- Deduplication based on text similarity (Jaccard similarity)
- Text chunking for token limit management

#### 6. **Token Optimization**
- Intelligent content truncation before API calls
- Hierarchical summarization for large documents
- Chunk-based processing with metadata preservation

### Key Features

#### A. Search Agent
- Fetches top N results from Serper API
- Retry logic with exponential backoff
- Returns URLs and metadata (title, snippet, position)

#### B. Scrape Agent
- Parallel URL fetching with timeout handling
- HTML cleaning (removes scripts, styles, metadata)
- Per-URL content deduplication
- Combined content length limiting

#### C. Summarize Agent
- LLM integration with retry logic
- Standard summarization (single pass)
- Hierarchical summarization (chunked for long content)
- Token estimation for cost optimization

#### D. Logging System
- Rotating file handlers (10MB max per file, 5 backups)
- Console and file output
- Configurable log levels
- Stack traces for debugging

#### E. Retry Mechanism
- Automatic retry with exponential backoff
- Configurable max attempts and delay multiplier
- Specific exception catching
- Detailed logging of retry attempts

### Configuration

#### Environment Variables (.env)
```
GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
LOG_LEVEL=INFO
DEBUG_MODE=false
```

#### Streamlit Configuration
If you want to customize Streamlit behavior, create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"

[logger]
level = "info"
```

### Usage

#### 1. Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

#### 2. Run CLI (main.py)
```bash
python main.py
```
This will:
- Prompt for a search query
- Execute the pipeline
- Print results and summary

#### 3. Run Web UI (Streamlit)
```bash
streamlit run app.py
```
This will:
- Launch web interface at http://localhost:8501
- Provide UI for configuration and interaction
- Enable CSV and text downloads

### Integration Points

#### External APIs
1. **Serper API** - Web search
   - Endpoint: `https://google.serper.dev/search`
   - Key: `SERPER_API_KEY`

2. **Google Gemini** - LLM
   - Model: `gemini-1.5-flash`
   - Key: `GEMINI_API_KEY`

#### Libraries
- **LangGraph**: Workflow orchestration
- **BeautifulSoup**: HTML parsing
- **Requests**: HTTP client
- **Streamlit**: Web UI framework

### Performance Considerations

#### Token Usage
- Content truncated to 8000 chars for summarization
- Per-URL limit: 10,000 characters
- Total combined content limit: 30,000 characters

#### Timeouts
- Request timeout: 10 seconds per URL
- Supported graceful degradation on timeout

#### Retry Strategy
- Search: 3 attempts, 2s delay, 1.5x backoff
- Scraping: 3 attempts, 1s delay, 1.5x backoff
- LLM: 3 attempts, 2s delay, 2x backoff

### Logging

Logs are written to `logs/app.log` with:
- Timestamp, logger name, level, function name, line number
- Rotating file handler with 10MB max size
- 5 backup files retained
- Console output for real-time monitoring

### Error Handling Examples

**Empty Query**
```
Query: '' → Returns error message immediately
```

**API Failure**
```
Serper API down → Retries 3 times → Logs error → Returns gracefully
```

**No Results**
```
Search returns 0 URLs → Scrape skipped → Summary shows "No content to summarize"
```

### Extension Points

#### Add New Agent
1. Create new agent class in `agents/`
2. Add node to graph in `main.py`
3. Connect edges to workflow
4. Update state TypedDict if needed

#### Add New Service
1. Create service class in `services/`
2. Import in appropriate agent
3. Use retry decorator for API calls
4. Add logging at key points

#### Custom Text Processing
1. Add function to `utils/cleaning.py`
2. Import and use in scraping service
3. Add tests in `tests/` directory

### Testing

Run tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Deployment

#### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t quickglance .
docker run -p 8501:8501 --env-file .env quickglance
```

### Monitoring

#### Key Metrics
- Average API response time
- Cache hit rate
- Error rate by service
- Token usage per query

#### Logs to Monitor
```
ERROR: Service failures
WARNING: Retry attempts
INFO: Successful operations
DEBUG: Detailed execution traces
```

### Best Practices Implemented

1. ✅ **Separation of Concerns**: Agents, Services, Utils
2. ✅ **Configuration Management**: Environment variables
3. ✅ **Error Handling**: Comprehensive try-catch and retry logic
4. ✅ **Logging**: Structured logging at all levels
5. ✅ **Type Safety**: TypedDict for workflow state
6. ✅ **Documentation**: Docstrings and comments
7. ✅ **Graceful Degradation**: Handles partial failures
8. ✅ **Security**: No hardcoded secrets
9. ✅ **Performance**: Token optimization and chunking
10. ✅ **Maintainability**: Modular, testable code

### Future Enhancements

1. **Caching**: Redis for search results caching
2. **Database**: PostgreSQL for query history
3. **Rate Limiting**: Per-user API rate limits
4. **Authentication**: User authentication for Streamlit
5. **Analytics**: Dashboard for usage metrics
6. **A/B Testing**: Test different summarization strategies
7. **Custom Models**: Fine-tuned LLM for domain-specific tasks
8. **Multi-Language**: Support for non-English content

### Support & Troubleshooting

**API Key Issues**
- Verify keys in `.env` file
- Check API dashboard for rate limits
- Ensure keys have correct permissions

**Import Errors**
- Run: `pip install -r requirements.txt`
- Check Python version: 3.8+

**Network Issues**
- Check internet connection
- Verify proxy settings if behind corporate network

**Memory Issues**
- Reduce `max_content_per_url` in ScrapeAgent
- Reduce `num_search_results` in configuration

---

**Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production-Ready
