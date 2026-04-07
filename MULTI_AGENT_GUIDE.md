# 🤖 True Multi-Agent System with LangGraph

## Overview

This is a production-grade, TRUE multi-agent system with **dynamic routing** and **decision-making logic**. Unlike the linear pipeline, agents communicate via shared state and routing decisions guide execution flow.

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT PIPELINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Entry: Planner ──┐                                         │
│                   ├─→ Router ──┐                            │
│                                 ├─→ Search                  │
│                                 │     ↓                     │
│                                 ├─→ Scraper ──┐            │
│                                 │             ├─→ Router ──┐│
│                                 │             │             ││
│                                 ├─→ Evaluator │             ││
│                                 │             ├─→ Router ──┤│
│                                 │                           ││
│                                 ├─→ Summarizer ────┐        ││
│                                 │                  ├─→ Formatter
│                                 │                  │   ↓    ││
│                                 ├─→ Error Handler ─┤   Output
│                                 │                  │        ││
│                                 └──────────────────┴────────┘│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 1. **Planner Agent** 🎯
- **Input**: User query
- **Logic**: Analyzes query to determine optimal execution strategy
- **Decision**: Which agents to enable, complexity level, routing preferences
- **Output**: Execution plan with routing decisions

```python
Plan = {
    "query_type": "academic|news|how_to|product_review|general",
    "complexity": "simple|medium|complex",
    "priority_agents": ["search", "scrape", "evaluate", "summarize"],
    "needs_evaluation": True,
    "estimated_sources": 5,
    "summary_depth": "brief|detailed"
}
```

#### 2. **Search Agent** 🔍
- **Input**: Query + execution plan
- **Logic**: Fetches URLs via Serper API
- **Decision**: Filter/rank results based on plan
- **Output**: Relevant URLs list

#### 3. **Scraper Agent** 🪄
- **Input**: URLs from search
- **Logic**: Extracts and cleans content
- **Decision**: Content quality checks, deduplication
- **Output**: Clean, structured content

#### 4. **Evaluator Agent** ⭐ (Optional)
- **Input**: Content + original query
- **Logic**: Rates relevance and quality
- **Decision**: Keep/filter based on threshold
- **Output**: Quality scores, filtered content

```python
Evaluation = {
    "relevance_score": 0.85,  # 0-1
    "quality_score": 0.75,    # 0-1
    "is_relevant": True,      # Keep/Skip
    "content_bias": "neutral|biased|promotional",
    "recommendation": "keep|improve|skip"
}
```

#### 5. **Summarizer Agent** 📝
- **Input**: Evaluated/scraped content
- **Logic**: Generates bullet-point summary via LLM
- **Decision**: Summary depth based on content quality
- **Output**: Concise summary

#### 6. **Formatter Agent** 💾 (Optional)
- **Input**: Summary + original query
- **Logic**: Converts to multiple formats
- **Output**: CSV, JSON, Markdown, Audio

---

## 🔀 Dynamic Routing

### Key Routing Decisions

```
1. After Planner:
   ├─ Search enabled? → SEARCH
   └─ Search disabled? → SKIP

2. After Search:
   ├─ URLs found? → SCRAPER
   └─ No URLs? → ERROR_HANDLER

3. After Scraper:
   ├─ Evaluation enabled? → EVALUATOR
   └─ Evaluation disabled? → SUMMARIZER

4. After Evaluator:
   ├─ Content relevant? → SUMMARIZER
   └─ Content filtered? → ERROR_HANDLER

5. After Summarizer:
   ├─ Formatting enabled? → FORMATTER
   └─ Formatting disabled? → END
```

### Conditional Edges

The system uses **conditional edges** to route based on:
- Query complexity
- Available content
- Quality thresholds
- Configuration settings
- Runtime errors

---

## 📊 State Management

### Shared State (AgentState)

All agents communicate via shared state dictionary:

```python
state = {
    # Inputs
    "query": str,
    
    # Agent outputs
    "plan": Dict,
    "search_results": Dict,
    "scraped_content": str,
    "evaluation_results": Dict,
    "summary": str,
    "formatted_output": Dict,
    
    # Routing
    "routing_decisions": ["search", "scrape", "evaluate"],
    "agent_history": ["planner", "search", "scraper"],
    
    # Status
    "status": "running|success|failed|partial_success",
    "error_message": str,
    
    # Control
    "enabled_agents": ["search", "scrape", "evaluate", "summarize"],
    "evaluate_content": True,
    "format_output": True
}
```

### Example State Evolution

```
START
  ↓ Planner
{ plan: {...}, status: "running" }
  ↓ Search
{ urls: [...], status: "running" }
  ↓ Scraper
{ content: "...", status: "running" }
  ↓ Evaluator
{ relevance_score: 0.85, status: "running" }
  ↓ Summarizer
{ summary: "...", status: "running" }
  ↓ Formatter
{ formatted_output: {...}, status: "success" }
  ↓ END
```

---

## 💡 Decision-Making Examples

### Example 1: Academic Query

```
Query: "Latest developments in quantum computing"

Planner Decision:
├─ query_type: "academic"
├─ complexity: "complex"
├─ needs_evaluation: True  (strict relevance required)
├─ summary_depth: "detailed"
└─ priority_agents: ["search", "scrape", "evaluate", "summarize"]

Routing:
├─ Search → Find academic papers
├─ Scraper → Extract technical content
├─ Evaluator → Filter for highly relevant content (threshold: 0.8)
├─ Summarizer → Detailed 7-point summary
└─ Formatter → Academic citations in CSV
```

### Example 2: News Query

```
Query: "Quick update on AI investments"

Planner Decision:
├─ query_type: "news"
├─ complexity: "simple"
├─ needs_evaluation: False  (accept more results)
├─ summary_depth: "brief"
└─ priority_agents: ["search", "scrape", "summarize"]

Routing:
├─ Search → Find recent news articles
├─ Scraper → Extract main points
├─ Skip Evaluator → Accept all content
├─ Summarizer → Quick 3-point summary
└─ Formatter → News bulletin format
```

### Example 3: Product Review Query

```
Query: "Best laptops under $1000"

Planner Decision:
├─ query_type: "product_review"
├─ complexity: "medium"
├─ needs_evaluation: True  (filter spam/bias)
├─ summary_depth: "detailed"
└─ priority_agents: ["search", "scrape", "evaluate", "summarize"]

Routing:
├─ Search → Find reviews
├─ Scraper → Extract specs + ratings
├─ Evaluator → Filter promotional bias (threshold: 0.7)
├─ Summarizer → Comparison summary
└─ Formatter → Comparison table CSV
```

---

## 🎯 Key Features

### 1. **Dynamic Routing**
✅ Not hardcoded sequential flow  
✅ Decisions based on query analysis  
✅ Can skip agents dynamically  
✅ Different paths for different queries  

### 2. **Decision-Making Logic**
✅ Planner analyzes and decides execution strategy  
✅ Router nodes choose next agents  
✅ Evaluator filters based on thresholds  
✅ Error handler provides graceful degradation  

### 3. **Agent Communication**
✅ Shared state (not direct agent calls)  
✅ Each agent reads and updates state  
✅ History of agent execution tracked  
✅ Audit trail of routing decisions  

### 4. **Conditional Edges**
✅ Based on content availability  
✅ Based on quality thresholds  
✅ Based on plan decisions  
✅ Based on runtime errors  

### 5. **Graceful Degradation**
✅ No required agents (all conditional)  
✅ Error handler for failed paths  
✅ Partial results when possible  
✅ User-friendly error messages  

---

## 📈 Execution Flow Visualization

### ASCII Visualization

```
Entry: PLANNER
   ↓ (analyzes query)
Decision Node (ROUTER)
   ├─→ Yes: Go to SEARCH
   └─→ No: Skip to ERROR_HANDLER
   
SEARCH (if enabled)
   ↓ (find URLs)
Decision Node (CHECK_RESULTS)
   ├─→ URLs found: Go to SCRAPER
   └─→ No URLs: Skip to ERROR_HANDLER
   
SCRAPER (if URLs available)
   ↓ (extract content)
Decision Node (EVALUATE_MODE)
   ├─→ Evaluation enabled: Go to EVALUATOR
   └─→ Evaluation disabled: Go to SUMMARIZER
   
EVALUATOR (optional)
   ↓ (rate content)
Decision Node (RELEVANCE_CHECK)
   ├─→ Relevant: Go to SUMMARIZER
   └─→ Not relevant: Skip to ERROR_HANDLER
   
SUMMARIZER (core)
   ↓ (generate summary)
Decision Node (FORMAT_MODE)
   ├─→ Format enabled: Go to FORMATTER
   └─→ Format disabled: Go to END
   
FORMATTER (optional)
   ↓ (convert formats)
END (output)

ERROR_HANDLER (catch-all)
   ↓ (graceful degradation)
END (partial output)
```

---

## 🔧 Configuration

### Enable/Disable Agents

```python
from multi_agent_pipeline import MultiAgentPipeline

# Default: All agents enabled
pipeline = MultiAgentPipeline(
    enable_evaluation=True,    # Use evaluator?
    enable_formatting=True     # Use formatter?
)

# Minimal pipeline (search → scrape → summarize only)
pipeline_minimal = MultiAgentPipeline(
    enable_evaluation=False,
    enable_formatting=False
)
```

### Customize Agent Behavior

```python
from agents.evaluator_agent import EvaluatorAgent

# Stricter evaluation
evaluator = EvaluatorAgent(relevance_threshold=0.8)

# Looser evaluation
evaluator_loose = EvaluatorAgent(relevance_threshold=0.5)
```

---

## 📊 Execution Examples

### Example Output: Success Path

```
MULTI-AGENT PIPELINE START: 'What is machine learning?'
==================================================================

→ PLANNER NODE: Analyzing query...
  Plan: general | Complexity: medium

→ ROUTE NODE: Determining next step...

→ SEARCH NODE: Searching for URLs...
  Found 5 URLs

→ SCRAPER NODE: Extracting content...
  Extracted 12450 characters

→ EVALUATOR NODE: Evaluating content...
  Content relevant (score: 0.82)

→ SUMMARIZER NODE: Generating summary...
  Summary generated (287 chars)

→ FORMATTER NODE: Formatting output...
  Formatted to: ['text', 'csv', 'json', 'markdown']

PIPELINE COMPLETE - Status: success
Agents executed: planner → search → scraper → evaluator → summarizer → formatter

==================================================================
```

### Example Output: Skip Path

```
MULTI-AGENT PIPELINE START: 'Quick tech news'
==================================================================

→ PLANNER NODE: Analyzing query...
  Plan: news | Complexity: simple

→ ROUTE NODE: Determining next step...

→ SEARCH NODE: Searching for URLs...
  Found 8 URLs

→ SCRAPER NODE: Extracting content...
  Extracted 8900 characters

→ EVALUATOR NODE: Evaluating content...
  [SKIPPED - Evaluation disabled for news queries]

→ SUMMARIZER NODE: Generating summary...
  Summary generated (150 chars)

→ FORMATTER NODE: Formatting output...
  Formatted to: ['text', 'csv']

PIPELINE COMPLETE - Status: success
Agents executed: planner → search → scraper → summarizer → formatter

==================================================================
```

### Example Output: Partial Failure

```
MULTI-AGENT PIPELINE START: 'Very obscure topic'
==================================================================

→ PLANNER NODE: Analyzing query...
  Plan: academic | Complexity: complex

→ ROUTE NODE: Determining next step...

→ SEARCH NODE: Searching for URLs...
  Found 2 URLs

→ SCRAPER NODE: Extracting content...
  Extracted 1200 characters

→ EVALUATOR NODE: Evaluating content...
  Content not relevant (score: 0.45) - FILTERED OUT

→ ERROR HANDLER: Content not relevant
  Returning partial results (summary available)

PIPELINE COMPLETE - Status: partial_success
Agents executed: planner → search → scraper → evaluator → error_handler

==================================================================
```

---

## 🔗 Comparison: Old vs New

### Old Pipeline (Linear)

```
Query → Search → Scrape → Summarize → Output
         Fixed    Fixed   Fixed      Fixed
```

❌ No planning  
❌ No content evaluation  
❌ No format options  
❌ No dynamic routing  

### New Pipeline (Multi-Agent)

```
Query → Plan → ⓡRouteⓡ → Search → ⓡRouteⓡ → Scrape → ⓡRouteⓡ
                  ↓           ↓         ↓
                 Skip        Skip      Eval
                                        ↓
                                    ⓡRouteⓡ → Summarize → ⓡRouteⓡ
                                      ↓                    ↓
                                     Skip                Format
                                                          ↓
                                                       Output
```

✅ Intelligent planning  
✅ Quality evaluation  
✅ Multiple formats  
✅ Dynamic routing  
✅ Decision-making  
✅ Graceful degradation  

---

## 🚀 Usage

### Method 1: Python Code

```python
from multi_agent_pipeline import MultiAgentPipeline

# Initialize
pipeline = MultiAgentPipeline(
    enable_evaluation=True,
    enable_formatting=True
)

# Run
result = pipeline.run("What are benefits of AI?")

# Access results
print(f"Status: {result['status']}")
print(f"Summary: {result['summary']}")
print(f"Agents used: {result['routing_path']}")
```

### Method 2: CLI

```bash
python multi_agent_cli.py "Machine learning trends 2024"
```

### Method 3: Streamlit Web UI

```bash
streamlit run multi_agent_app.py
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `multi_agent_pipeline.py` | Core system implementation |
| `multi_agent_cli.py` | Command-line interface |
| `multi_agent_app.py` | Streamlit web interface |
| `utils/graph_visualizer.py` | Graph visualization |
| `MULTI_AGENT_GUIDE.md` | This file |

---

## 🎯 Key Takeaways

1. **True Multi-Agent**: Not sequential, agents have decision-making
2. **Dynamic Routing**: Different queries follow different paths
3. **Shared State**: Agents communicate via state dictionary
4. **Conditional Edges**: Routing based on query analysis and content
5. **Graceful Degradation**: Handles failures elegantly
6. **Production-Ready**: Logging, error handling, retries included

---

**Ready to use TRUE multi-agent AI system! 🤖**
