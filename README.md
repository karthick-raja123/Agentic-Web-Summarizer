# Visual Web Agent - Multi-Agent System 🤖

An AI-powered intelligent automation system that transforms web intelligence gathering through **TRUE multi-agent collaboration** with dynamic routing, decision-making, and quality filtering.

## 🎯 Overview

Visual Web Agent is a production-grade, multi-agent framework that intelligently processes queries by:

1. **Planning** execution strategy based on query analysis
2. **Searching** the web for relevant sources
3. **Scraping** and extracting meaningful content
4. **Evaluating** content quality and relevance
5. **Summarizing** findings into clear, actionable insights
6. **Formatting** output in multiple formats (CSV, JSON, Markdown, Audio)

Unlike traditional sequential pipelines, this system uses **LangGraph** for dynamic routing where different queries follow different execution paths based on intelligent decision-making.

## 🚀 Key Features

✅ **Multiple Operating Modes:**
- Minimal Pipeline: Search → Scrape → Summarize (fastest)
- Standard Pipeline: + Content Evaluation (recommended)
- Full Pipeline: + Multi-Format Export (comprehensive)

✅ **Dynamic Routing:**
- Not hardcoded sequential flow
- Decisions based on query analysis and content availability
- Can skip agents based on runtime decisions

✅ **Intelligent Decision-Making:**
- Planner Agent analyzes queries to determine optimal strategy
- Evaluator Agent filters content by relevance (0-1 scoring)
- Router Nodes decide next steps based on current state

✅ **Production-Ready:**
- Comprehensive error handling and graceful degradation
- Logging at each stage for debugging
- Retry mechanisms for API calls
- Multi-format export (CSV, JSON, Markdown, Audio)

✅ **Three User Interfaces:**
- Command-Line Interface (CLI) for power users
- Python API for developers
- Streamlit Web UI for non-technical users

## 📋 Project Structure

```
Visual-web-Agent/
├── agents/
│   ├── planner_agent.py        # Query analysis & planning
│   ├── search_agent.py          # Web search (Serper API)
│   ├── scraper_agent.py         # Content extraction
│   ├── evaluator_agent.py       # Quality filtering
│   ├── summarizer_agent.py      # Summary generation
│   └── formatter_agent.py       # Multi-format export
│
├── services/
│   ├── llm_service.py           # Gemini API wrapper
│   ├── search_service.py        # Serper search service
│   └── scraping_service.py      # Content extraction
│
├── utils/
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging utilities
│   ├── graph_visualizer.py      # Graph visualization
│   └── retry_handler.py         # Retry logic
│
├── multi_agent_pipeline.py      # Core LangGraph orchestrator
├── multi_agent_cli.py           # Command-line interface
├── multi_agent_app.py           # Streamlit web interface
├── example_multi_agent.py       # 10 usage examples
│
├── MULTI_AGENT_GUIDE.md         # Comprehensive documentation
├── MULTI_AGENT_QUICKSTART.md    # Quick start guide
└── requirements.txt             # Dependencies
```

## 💡 Objective

The primary objective of this project is to develop an intelligent, multi-agent pipeline with Gemini LLM that:

- **Automates** web research through search, scrape, and summarization
- **Reduces effort** by handling query planning and content evaluation
- **Ensures quality** through relevance filtering and bias detection
- **Provides flexibility** through multiple output formats and execution paths
- **Delivers insights** quickly through intelligent agent coordination

This system empowers learners, researchers, and professionals to gather high-quality information from the web without manual effort.

## 🛠️ Technology Stack

### Core Framework
- **LangGraph**: Multi-agent orchestration with conditional routing
- **Google Gemini**: LLM for planning, evaluation, and summarization

### APIs & Services
- **Serper API**: Web search and URL retrieval
- **gTTS**: Text-to-speech audio generation

### Libraries
- **BeautifulSoup**: HTML parsing and content extraction
- **Streamlit**: Web UI framework
- **Requests**: HTTP client for web fetching
- **Python 3.8+**: Core language

## 🎮 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Visual-web-Agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Copy example credentials and fill in your API keys
cp .env.example .env
```

### Method 1: Command-Line Interface (CLI)

```bash
# Basic usage
python multi_agent_cli.py "What is machine learning?"

# With evaluation enabled
python multi_agent_cli.py "quantum computing basics" --enable-eval

# Show execution graph
python multi_agent_cli.py "AI trends" --show-graph

# Save results to file
python multi_agent_cli.py "query" --output results.json

# Show detailed plan
python multi_agent_cli.py "topic" --show-plan
```

### Method 2: Python API

```python
from multi_agent_pipeline import MultiAgentPipeline

# Create pipeline
pipeline = MultiAgentPipeline(
    enable_evaluation=True,
    enable_formatting=False
)

# Run query
result = pipeline.run("What are benefits of AI?")

# Access results
print(f"Status: {result['status']}")
print(f"Summary: {result['summary']}")
print(f"Agents used: {result['agent_history']}")
```

### Method 3: Web Interface (Streamlit)

```bash
# Start web interface
streamlit run multi_agent_app.py

# Access at: http://localhost:8501
```

### Method 4: Run Examples

```bash
# View all 10 examples
python example_multi_agent.py

# Run specific example
python example_multi_agent.py 1    # Basic usage
python example_multi_agent.py 5    # Graph visualization
python example_multi_agent.py 8    # Batch processing
```

## 📊 Agent Architecture

### Agent Roles

**🎯 Planner Agent**
- Analyzes query to determine execution strategy
- Classifies query type (academic, news, product, how_to, general)
- Determines complexity (simple, medium, complex)
- Decides which agents to enable
- Sets evaluation strictness and output format preferences

**🔍 Search Agent**
- Queries Serper API for relevant URLs
- Ranks results by relevance
- Returns top URLs based on planner priorities
- Handles search result parsing and deduplication

**🪄 Scraper Agent**
- Fetches webpages using HTTP requests
- Extracts clean text using BeautifulSoup
- Removes HTML, scripts, and formatting
- Handles encoding and character issues
- Returns structured content with metadata

**⭐ Evaluator Agent** (Optional)
- Rates content relevance to original query
- Scores on 0-1 scale using semantic similarity
- Filters content below threshold (default: 0.6)
- Detects bias and promotional content
- Returns quality metrics and recommendations

**📝 Summarizer Agent**
- Generates bullet-point summaries using Gemini LLM
- Adapts summary depth based on content quality
- Preserves key insights and statistics
- Maintains factual accuracy
- Returns summary with source attribution

**💾 Formatter Agent** (Optional)
- Converts summaries to multiple formats
- **CSV**: Tabular data for spreadsheets
- **JSON**: Structured data for APIs
- **Markdown**: Documentation-friendly format
- **Audio**: MP3 via text-to-speech
- Handles file generation and cleanup

### Conditional Routing

The system makes intelligent routing decisions:

```
Query → PLANNER (analyzes)
         ↓
        ROUTER 1 (search enabled?)
         ├─ YES → SEARCH (find URLs)
         └─ NO  → ERROR
         
SCRAPER (extract content)
         ↓
        ROUTER 2 (results valid?)
         ├─ YES → check evaluator setting
         └─ NO  → ERROR
         
        ROUTER 3 (evaluation enabled?)
         ├─ YES → EVALUATOR (quality check)
         └─ NO  → SUMMARIZER
         
SUMMARIZER (generate summary)
         ↓
        ROUTER 4 (format output?)
         ├─ YES → FORMATTER (CSV/JSON/etc)
         └─ NO  → END
```

## 📚 Documentation

- **[Multi-Agent Guide](MULTI_AGENT_GUIDE.md)** - Comprehensive system documentation
- **[Quick Start Guide](MULTI_AGENT_QUICKSTART.md)** - Get started in 5 minutes
- **[Examples](example_multi_agent.py)** - 10 usage examples with explanations
- **[CLI Reference](multi_agent_cli.py)** - Command-line interface usage

## 🔄 Processing Examples

### Example 1: Academic Query

```
Input: "Latest developments in quantum computing"

Planner Decision:
├─ Type: academic
├─ Complexity: complex
├─ Evaluation: ENABLED (strict)
└─ Format: ENABLED (citations)

Agent Flow: planner → search → scraper → evaluator → summarizer → formatter
Output: Detailed summary with academic sources
```

### Example 2: News Query

```
Input: "AI industry news today"

Planner Decision:
├─ Type: news
├─ Complexity: simple  
├─ Evaluation: NOT NEEDED (accept more)
└─ Format: NOT NEEDED

Agent Flow: planner → search → scraper → summarizer
Output: Quick news bulletin
```

### Example 3: Product Review Query

```
Input: "Best laptops under $1000"

Planner Decision:
├─ Type: product_review
├─ Complexity: medium
├─ Evaluation: ENABLED (filter bias)
└─ Format: ENABLED (comparison table)

Agent Flow: planner → search → scraper → evaluator → summarizer → formatter
Output: Comparison table with reviews
```

## 🎓 Key Concepts

**State Management**: All agents communicate through a shared `AgentState` TypedDict containing query context, intermediate results, routing decisions, and final outputs.

**Dynamic Routing**: Conditional edges determine agent execution based on runtime conditions (content availability, quality metrics, configuration settings).

**Decision-Making**: The Planner Agent analyzes queries using LLM to create execution plans, enabling intelligent adaptation to different query types.

**Graceful Degradation**: System handles missing data, failed requests, and low-quality content by returning partial results rather than failing completely.

## 📈 Performance

- **Minimal Pipeline**: ~5-10 seconds (search only)
- **Standard Pipeline**: ~15-30 seconds (with evaluation)
- **Full Pipeline**: ~20-40 seconds (with formatting)

Actual times depend on:
- Query complexity
- Internet connection speed
- Content size
- LLM API latency
- Number of sources processed

## 🔐 Configuration

Environment variables needed (create `.env` file):

```bash
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Serper API
SERPER_API_KEY=your_serper_api_key

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

## ✅ Features Comparison

| Feature | Old Pipeline | Multi-Agent |
|---------|--------------|-------------|
| Fixed Flow | ✅ | ❌ |
| Dynamic Routing | ❌ | ✅ |
| Query Planning | ❌ | ✅ |
| Content Evaluation | ❌ | ✅ |
| Skip Agents | ❌ | ✅ |
| Decision-Making | ❌ | ✅ |
| Multi-Format | ✅ | ✅ |
| Error Handling | ✅ | ✅ |
| Logging | ✅ | ✅ |
| Production Ready | ✅ | ✅ |

## 🚀 Advanced Usage

### Custom Agent Configuration

```python
from agents.evaluator_agent import EvaluatorAgent

# Stricter evaluation
evaluator = EvaluatorAgent(relevance_threshold=0.8)

# Looser evaluation  
evaluator_loose = EvaluatorAgent(relevance_threshold=0.5)
```

### Batch Processing

```python
pipeline = MultiAgentPipeline()

queries = [
    "What is AI?",
    "Machine learning trends",
    "Deep learning applications"
]

for query in queries:
    result = pipeline.run(query)
    print(f"✅ {query}: {result['status']}")
```

### Custom Graph Analysis

```python
from utils.graph_visualizer import GraphVisualizer

viz = GraphVisualizer()

# ASCII visualization
print(viz.draw_ascii_graph(simplified=False))

# Mermaid diagram
print(viz.draw_mermaid_diagram())

# JSON structure
print(viz.draw_json_graph())
```

## 🐛 Troubleshooting

**Issue**: No search results found
```bash
# Solution: Check API key and internet connection
python multi_agent_cli.py "test" --verbose
```

**Issue**: Low evaluation scores
```bash
# Solution: Disable evaluation or lower threshold
python multi_agent_cli.py "query" --no-eval
```

**Issue**: Slow execution
```bash
# Solution: Use minimal pipeline
pipeline = MultiAgentPipeline(enable_evaluation=False, enable_formatting=False)
```

## 🧪 Testing

### Run Examples

```bash
# Run all 10 examples
python example_multi_agent.py

# Examples include:
# 1. Basic query processing
# 2. Fast news processing
# 3. Academic research queries
# 4. Product review queries
# 5. Graph visualization
# 6. Decision-making flow
# 7. Error handling
# 8. Batch processing
# 9. Configuration comparison
# 10. State evolution
```

### Manual Testing

```bash
# Test CLI
python multi_agent_cli.py "test query" --show-plan

# Test minimal pipeline
python -c "from multi_agent_pipeline import MultiAgentPipeline; p = MultiAgentPipeline(enable_evaluation=False); print(p.run('test'))"

# Test with formatting
python multi_agent_cli.py "query" --enable-format
```

## 📊 Performance Benchmarks

System performance on standard queries:

| Configuration | Search | Scrape | Evaluate | Summarize | Total |
|---------------|--------|--------|----------|-----------|-------|
| Minimal | 2-3s | 1-2s | - | 2-3s | 5-8s |
| Standard | 2-3s | 1-2s | 1-2s | 2-3s | 8-12s |
| Full | 2-3s | 1-2s | 1-2s | 2-3s | 8-15s |

*Times approximate and dependent on content size, API latency, and network speed*

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Add logging for debugging
- Write tests for new features
- Update documentation

### Areas for Contribution

- [ ] New agent types (Image analysis, Video processing, etc.)
- [ ] Alternative LLM providers (OpenAI, Claude, etc.)
- [ ] Performance optimizations
- [ ] Additional output formats
- [ ] Mobile app wrapper
- [ ] Docker containerization
- [ ] Cloud deployment templates

## 📜 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

Created as an intelligent automation system for web research and content extraction.

## 🙏 Acknowledgments

- LangGraph for multi-agent orchestration
- Google Gemini for LLM capabilities
- Serper API for web search
- BeautifulSoup for HTML parsing
- Streamlit for web UI framework

## 📞 Support

For issues, questions, or suggestions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Multi-Agent Guide](MULTI_AGENT_GUIDE.md)
3. Open an issue on GitHub
4. Review [Quick Start Guide](MULTI_AGENT_QUICKSTART.md)

## 🚀 Roadmap

### Version 1.1
- [ ] Add Mistral LLM support
- [ ] Implement caching for frequently accessed URLs
- [ ] Add webhook integration

### Version 1.2
- [ ] Multi-language support
- [ ] Custom agent builder
- [ ] API rate limiting

### Version 2.0
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Advanced visualization dashboard

---

**Made with ❤️ for intelligent automation**

Built with [LangGraph](https://github.com/langchain-ai/langgraph) | Powered by [Google Gemini](https://ai.google.dev/)
