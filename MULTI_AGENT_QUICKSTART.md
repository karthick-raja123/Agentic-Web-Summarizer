# 🤖 Multi-Agent Pipeline - Quick Start Guide

## What is This?

This is a **TRUE multi-agent system** built with LangGraph that replaces the linear pipeline with **dynamic routing** and **intelligent decision-making**. Instead of always doing: Search → Scrape → Summarize, the system now:

1. **Plans** the execution strategy based on query analysis
2. **Routes** dynamically based on available data and quality
3. **Evaluates** content relevance to filter results
4. **Formats** output in multiple formats (CSV, JSON, Markdown, etc.)

---

## 🚀 Quick Start

### Installation

```bash
# All dependencies already in requirements.txt
pip install -r requirements.txt
```

### Method 1: Python Code (Programmatic)

```python
from multi_agent_pipeline import MultiAgentPipeline

# Create pipeline
pipeline = MultiAgentPipeline(
    enable_evaluation=True,   # Filter content by relevance
    enable_formatting=True    # Generate multiple formats
)

# Run query
result = pipeline.run("What is machine learning?")

# Access results
print(result['status'])              # 'success' or 'failed'
print(result['summary'])             # Generated summary
print(result['routing_path'])        # List of agents used
print(result['agent_history'])       # Full agent execution order
```

### Method 2: Command Line (CLI)

```bash
# Basic usage
python multi_agent_cli.py "What is AI?"

# With options
python multi_agent_cli.py "machine learning" --enable-eval --show-plan

# Show graph visualization
python multi_agent_cli.py "topic" --show-graph

# Save results to file
python multi_agent_cli.py "query" --output results.json

# Disable evaluation (faster)
python multi_agent_cli.py "quick news" --no-eval
```

### Method 3: Run Examples

```bash
# View all examples
python example_multi_agent.py

# Run specific example
python example_multi_agent.py 1    # Basic usage
python example_multi_agent.py 5    # Graph visualization
python example_multi_agent.py 6    # Decision-making
```

---

## 📊 Agent Flow

### Simple Overview

```
PLANNER (analyze query)
   ↓
ROUTER (decide: search?)
   ├─ YES → SEARCH (find URLs)
   └─ NO  → ERROR
   
SCRAPER (extract content)
   ↓
ROUTER (evaluate?)
   ├─ YES → EVALUATOR (rate relevance)
   └─ NO  → SUMMARIZER
   
SUMMARIZER (generate summary)
   ↓
FORMATTER (CSV/JSON/etc)
   ↓
OUTPUT
```

### Complex Overview with Routing

```
START
  ↓
PLANNER
  • Analyzes query type (academic, news, product, etc)
  • Sets complexity level (simple, medium, complex)
  • Determines which agents to enable
  ↓
ROUTE DECISION 1
  ├─ Search enabled? YES → SEARCH
  └─ NO → ERROR_HANDLER
  ↓
SEARCH
  • Queries Serper API
  • Returns URLs
  ↓
ROUTE DECISION 2
  ├─ URLs found? YES → SCRAPER
  └─ NO → ERROR_HANDLER
  ↓
SCRAPER
  • Extracts content from URLs
  • Cleans HTML/formatting
  ↓
ROUTE DECISION 3
  ├─ Evaluation enabled? YES → EVALUATOR
  └─ NO → SUMMARIZER
  ↓
EVALUATOR (OPTIONAL)
  • Rates content relevance (0-1 scale)
  • Filters by threshold (default: 0.6)
  • Extracts relevant sections
  ↓
ROUTE DECISION 4
  ├─ Content relevant? YES → SUMMARIZER
  └─ NO → ERROR_HANDLER
  ↓
SUMMARIZER
  • Generates bullet-point summary
  • Uses LLM (Gemini)
  ↓
ROUTE DECISION 5
  ├─ Format output? YES → FORMATTER
  └─ NO → END
  ↓
FORMATTER (OPTIONAL)
  • CSV format (for spreadsheet)
  • JSON format (for API)
  • Markdown format (for docs)
  • Audio (MP3 via gTTS)
  ↓
END
```

---

## 🎯 Using Different Configurations

### Minimal Pipeline (Fastest)
```python
pipeline = MultiAgentPipeline(
    enable_evaluation=False,   # Skip evaluation
    enable_formatting=False    # No CSV/JSON export
)
# Agents: Planner → Search → Scraper → Summarizer
```

### Standard Pipeline (Recommended)
```python
pipeline = MultiAgentPipeline(
    enable_evaluation=True,    # Filter by relevance
    enable_formatting=False
)
# Agents: Planner → Search → Scraper → Evaluator → Summarizer
```

### Full Pipeline (Complete)
```python
pipeline = MultiAgentPipeline(
    enable_evaluation=True,    # Filter content
    enable_formatting=True     # Multiple formats
)
# Agents: Planner → Search → Scraper → Evaluator → Summarizer → Formatter
```

---

## 📈 Understanding Results

### Result Dictionary

```python
result = {
    # Status
    'status': 'success',                           # success|partial_success|failed
    'error_message': None,
    
    # Execution path
    'routing_path': 'planner→search→scraper→summarizer',
    'agent_history': ['planner', 'search', 'scraper', 'summarizer'],
    'routing_decisions': ['search enabled', 'urls found', 'summarize'],
    
    # Data from agents
    'plan': {...},                                 # From Planner
    'search_results': {results: [...]},           # From Search
    'scraped_content': '...',                     # From Scraper
    'scraped_urls': ['http://...'],               # From Scraper
    'evaluation_results': {...},                  # From Evaluator
    'summary': '...',                             # From Summarizer
    'formatted_output': {...},                    # From Formatter
    
    # Tracking
    'timestamp': '2024-01-15T10:30:00',
    'enabled_agents': ['search', 'scrape', 'evaluate', 'summarize']
}
```

### Checking Results

```python
# Check if successful
if result['status'] == 'success':
    print("✅ Completed successfully")
elif result['status'] == 'partial_success':
    print("⚠️ Partial results available")
else:
    print(f"❌ Failed: {result['error_message']}")

# Check which agents were used
print(f"Agents: {' → '.join(result['agent_history'])}")

# Check evaluator filtering
if result.get('evaluation_results'):
    eval_res = result['evaluation_results']
    print(f"Kept {eval_res['relevant_count']} items")
    print(f"Filtered {eval_res['filtered_count']} items")

# Check formatted output
if result.get('formatted_output'):
    formats = result['formatted_output']['formats']
    print(f"Generated: {', '.join(formats.keys())}")
```

---

## 🔄 Query Examples & Expected Routing

### Academic Query
```
Query: "Latest research in quantum computing"

Planner Decision:
  • Type: academic
  • Complexity: complex
  • Enable evaluation: YES (strict relevance)
  • Enable formatting: YES (academic citations)

Routing: planner → search → scraper → evaluator → summarizer → formatter
```

### News Query
```
Query: "AI industry news today"

Planner Decision:
  • Type: news
  • Complexity: simple
  • Enable evaluation: NO (accept more results)
  • Enable formatting: NO

Routing: planner → search → scraper → summarizer
```

### Product Query
```
Query: "best gaming laptops 2024"

Planner Decision:
  • Type: product_review
  • Complexity: medium
  • Enable evaluation: YES (filter promotions)
  • Enable formatting: YES (comparison table)

Routing: planner → search → scraper → evaluator → summarizer → formatter
```

---

## 💻 CLI Examples

### Example 1: Basic Query
```bash
python multi_agent_cli.py "What is machine learning?"
```

### Example 2: With Plan Details
```bash
python multi_agent_cli.py "quantum computing basics" --show-plan
```

### Example 3: Show Graph
```bash
python multi_agent_cli.py "topic" --show-graph
```

### Example 4: Save Results
```bash
python multi_agent_cli.py "query" --output results.json
```

### Example 5: Verbose Logging
```bash
python multi_agent_cli.py "query" --verbose
```

### Example 6: Disable Evaluation
```bash
python multi_agent_cli.py "news" --no-eval
```

### Example 7: Enable Formatting
```bash
python multi_agent_cli.py "topic" --enable-format
```

---

## 🧠 How Decision-Making Works

### The Planner Agent Decides

When you submit a query, the **Planner Agent** analyzes it:

```python
Analysis includes:
  1. Query Type Classification
     - academic: Research papers, technical docs
     - news: Current events, news articles
     - product_review: Product comparisons, reviews
     - how_to: Tutorials, guides, instructions
     - general: Everything else

  2. Complexity Assessment
     - simple: 1-2 sentence answer sufficient
     - medium: Moderate detail needed
     - complex: Deep research required

  3. Strategy Determination
     - Which agents to enable
     - Strictness of evaluation
     - Depth of summary needed
     - Output formats required
```

### Routing Decisions Are Made

Based on **runtime data**, not configuration:

```python
Decision points:
  1. URLs available? If no → ERROR
  2. Content relevant? If no → SKIP EVALUATION
  3. Quality sufficient? If no → PARTIAL RESULT
  4. Evaluation enabled? If yes → EVALUATE
  5. Formatting enabled? If yes → FORMAT
```

### Agents Adapt

Each agent adjusts based on **shared state**:

```python
Planner sets: plan['needs_evaluation'] = True
  ↓
Evaluator sees: state['evaluate_content'] = True
  ↓
Evaluator filters: Keep only relevance_score ≥ 0.6
  ↓
Summarizer receives: Only relevant content
  ↓
Formatter generates: Formats for relevant content only
```

---

## 🔍 Troubleshooting

### Check if pipeline is working:
```bash
# This should complete without errors
python multi_agent_cli.py "test query"
```

### View detailed execution:
```bash
# Show verbose logs
python multi_agent_cli.py "query" --verbose
```

### See agent routing:
```bash
# Display graph
python multi_agent_cli.py "query" --show-graph
```

### No results problem:
```bash
# Try disabling evaluation to see if that helps
python multi_agent_cli.py "query" --no-eval
```

---

## 📚 Files Overview

| File | Purpose |
|------|---------|
| `multi_agent_pipeline.py` | Core system (LangGraph orchestrator) |
| `multi_agent_cli.py` | Command-line interface |
| `example_multi_agent.py` | Usage examples (10 examples) |
| `MULTI_AGENT_GUIDE.md` | Detailed documentation |
| `agents/planner_agent.py` | Query analysis agent |
| `agents/evaluator_agent.py` | Content filtering agent |
| `agents/formatter_agent.py` | Format conversion agent |
| `utils/graph_visualizer.py` | Graph visualization tools |

---

## 🎓 Key Concepts

### Agent
A specialized component that does one job (search, scrape, evaluate, etc). Each agent:
- Reads shared state
- Processes data
- Updates state
- Returns control to orchestrator

### State
Shared dictionary that all agents read/write to. Enables agent communication without direct coupling.

### Conditional Edge
A router that decides which agent to run next based on current state.

### Dynamic Routing
Unlike fixed pipelines, the path changes based on:
- Query analysis
- Available data
- Quality assessments
- Configuration settings

---

## 🚀 Next Steps

1. **Run examples**: `python example_multi_agent.py`
2. **Try CLI**: `python multi_agent_cli.py "your query"`
3. **Integrate with UI**: See `multi_agent_app.py` for Streamlit integration
4. **Customize agents**: Modify agent files for your needs
5. **Read full guide**: See `MULTI_AGENT_GUIDE.md`

---

## ✅ You now have:

✅ TRUE multi-agent system (not just sequential)  
✅ Dynamic routing (changes based on content)  
✅ Decision-making (planner analyzes query)  
✅ Quality filtering (evaluator rates relevance)  
✅ Multiple outputs (CSV, JSON, Markdown, Audio)  
✅ Graph visualization (see agent flow)  
✅ CLI interface (easy command-line use)  
✅ Production ready (logging, error handling, retries)  

**Ready to use! 🎉**
