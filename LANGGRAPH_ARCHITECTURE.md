# 🤖 LangGraph Multi-Agent System - Complete Architecture Guide

**Status**: ✅ Production Ready  
**Agents**: 6 Specialized Agents with Dynamic Routing  
**Architecture**: Conditional Loops & Shared State  

---

## 📐 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY INPUT                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
          ╔══════════════════════════════════╗
          ║  1️⃣  PLANNER AGENT              ║
          ║  - Break query into steps        ║
          ║  - Create multi-search strategy  ║
          ╚────────────┬─────────────────────╝
                       │
                       ▼
          ╔══════════════════════════════════╗
          ║  2️⃣  SEARCH AGENT               ║
          ║  - Execute multiple queries      ║
          ║  - Collect diverse URLs          ║
          ║  - Prioritize results            ║
          ╚────────────┬─────────────────────╝
                       │
                       ▼
          ╔══════════════════════════════════╗
          ║  3️⃣  SCRAPER AGENT              ║
          ║  - Extract structured content    ║
          ║  - Parse HTML intelligently      ║
          ║  - Classify content type         ║
          ╚────────────┬─────────────────────╝
                       │
                       ▼
          ╔══════════════════════════════════╗
          ║  4️⃣  EVALUATOR AGENT            ║
          ║  - Filter by quality/relevance   ║
          ║  - LLM-based evaluation          ║
          ║  - Score and rank content        ║
          ╚────────────┬─────────────────────╝
                       │
                       ▼
          ╔══════════════════════════════════╗
          ║  5️⃣  SUMMARIZER AGENT           ║
          ║  - Generate structured summary   ║
          ║  - Create bullet points          ║
          ║  - Ensure coherence              ║
          ╚────────────┬─────────────────────╝
                       │
                       ▼
          ╔══════════════════════════════════╗
          ║  6️⃣  REFLECTION AGENT           ║
          ║  - Evaluate summary quality      ║
          ║  - Check completeness            ║
          ║  - Decide: RETRY or END          ║
          ╚────┬──────────────────────────┬──╝
       RETRY   │                          │   END
          ┌────┘                          └────┐
          │                                     │
    ┌─────▼──────┐                      ┌──────▼──────┐
    │ Go back to │                      │   FINISH    │
    │ SEARCH     │                      │  Pipeline   │
    │ (Loop)     │                      │             │
    └────────────┘                      └─────────────┘
```

---

## 🏗️ Shared State Architecture

All agents communicate through a single shared `PipelineState` object:

```
PipelineState
├── Input Phase
│   ├── query: str                    # Original user query
│   └── user_intent: str              # Extracted intent
│
├── Planning Phase
│   ├── plan: List[PlanStep]          # Multi-step plan
│   └── plan_iterations: int          # Retry count
│
├── Search Phase
│   ├── search_queries: List[]        # Multiple search strategies
│   ├── search_results: List[]        # Raw search results
│   └── urls: List[str]               # Collected URLs
│
├── Scraping Phase
│   ├── scraped_content: List[]       # Extracted content with metadata
│   └── scraping_iterations: int      # Track scraping attempts
│
├── Evaluation Phase
│   ├── evaluations: List[]           # Quality/relevance scores
│   └── valid_content: List[]         # Filtered high-quality content
│
├── Summarization Phase
│   ├── raw_summary: str              # LLM overview
│   ├── summary: str                  # Final formatted summary
│   └── summary_bullets: List[str]   # Extracted key points
│
├── Reflection Phase
│   ├── reflection_score: float       # Final quality score (0-1)
│   ├── reflection_notes: str         # Evaluation notes
│   ├── needs_improvement: bool       # Retry flag
│   └── iterations: int               # Total pipeline runs
│
└── Metadata
    ├── timestamps: Dict[]            # Timing for each agent
    ├── messages: List[str]           # Execution log
    ├── current_agent: str            # Currently running agent
    ├── next_agent: str               # Next agent to run
    └── error: Optional[str]          # Error tracking
```

---

## 🤖 Agent Specifications

### **1️⃣ Planner Agent**

**Purpose**: Break down user query and create execution strategy

**Inputs**:
- `query`: User's original question

**Outputs**:
- `user_intent`: Core need extracted from query
- `plan`: List of actionable steps
- `search_queries`: Multiple search strategies with priorities

**Key Logic**:
```python
Uses LLM to:
  1. Understand core user intent
  2. Create 3-5 actionable steps
  3. Generate 3-5 diverse search queries
  4. Prioritize by importance
```

**Example Output**:
```json
{
  "user_intent": "Learn about machine learning in healthcare",
  "plan": [
    {"step": 1, "action": "search", "description": "Find ML healthcare applications"},
    {"step": 2, "action": "scrape", "description": "Extract relevant content"},
    {"step": 3, "action": "evaluate", "description": "Filter by quality/relevance"},
    {"step": 4, "action": "summarize", "description": "Create final summary"}
  ],
  "search_strategies": [
    {"query": "machine learning healthcare", "priority": 1},
    {"query": "AI medical diagnosis", "priority": 2},
    {"query": "deep learning clinical applications", "priority": 3}
  ]
}
```

---

### **2️⃣ Search Agent**

**Purpose**: Execute diverse search queries and collect URLs

**Inputs**:
- `search_queries`: List of search strategies from Planner
- `query`: Original query as fallback

**Outputs**:
- `urls`: List of unique URLs (limit: 8 max)
- `search_results`: Metadata for each result

**Key Logic**:
```python
For each search query:
  1. Call Serper API
  2. Extract URLs from organic results
  3. Track priority and relevance
  4. Deduplicate and combine
  5. Limit to top 8 URLs
```

**Features**:
- Multiple search queries for better coverage
- Priority-based ranking
- Error handling and fallbacks
- Deduplication

---

### **3️⃣ Scraper Agent**

**Purpose**: Extract structured content from URLs

**Inputs**:
- `urls`: List of URLs to scrape
- `query`: For filtering irrelevant content

**Outputs**:
- `scraped_content`: List of structured content objects
  - URL, title, main text, quality score
  - Content type classification
  - Length metrics

**Key Logic**:
```python
For each URL:
  1. Fetch HTML with timeout
  2. Parse with BeautifulSoup
  3. Extract title and main text
  4. Remove noise (scripts, styles, nav)
  5. Classify content type
  6. Compute quality score
  7. Handle errors gracefully
```

**Content Classification**:
- "technical" → GitHub, code, technical docs
- "article" → Blog posts, news articles
- "documentation" → Wiki, reference docs
- "community" → Forums, Stack Overflow
- "general" → Everything else

**Quality Scoring** (0-1):
```
Base: 0.5
+ 0.2 if length > 500 chars
+ 0.15 if has headings (h1, h2)
+ 0.1 if has lists (ul, ol)
- 0.3 if length < 200 chars
```

---

### **4️⃣ Evaluator Agent**

**Purpose**: Filter content by quality and relevance

**Inputs**:
- `scraped_content`: Raw scraped content
- `query`: User query
- `user_intent`: Extracted intent

**Outputs**:
- `evaluations`: Quality/relevance scores for each URL
- `valid_content`: Filtered high-quality content only

**Key Logic**:
```python
For each scraped content:
  1. Use LLM to evaluate relevance
  2. Get relevance score (0-1)
  3. Combine with content quality score
  4. Keep if combined score > 0.4 AND marked relevant
  5. Provide reasoning for each decision
```

**Evaluation Criteria**:
- Does it answer the query?
- Is the content relevant?
- Is the quality acceptable?
- Are there key insights?

**Filtering**:
```python
Keep content if:
  - Combined quality score > 0.4
  - Marked as relevant by LLM
  - Content length > 200 chars
```

---

### **5️⃣ Summarizer Agent**

**Purpose**: Generate comprehensive summary from filtered content

**Inputs**:
- `valid_content`: Only high-quality relevant content
- `query`: Original query
- `user_intent`: Extracted intent

**Outputs**:
- `raw_summary`: LLM-generated overview
- `summary_bullets`: Key bullet points (5-7)
- `summary`: Fully formatted summary with bullets

**Key Logic**:
```python
1. Combine ALL valid content
2. Use LLM to generate structured summary:
   - Brief overview (2-3 sentences)
   - ExactlyKey bullet points (5-7)
   - Important considerations
3. Format as structured output
```

**Output Format**:
```
[Overview paragraph]

Key Points:
• Point 1
• Point 2
• Point 3
• Point 4
• Point 5

Considerations:
[Any caveats or important notes]
```

---

### **6️⃣ Reflection Agent**

**Purpose**: Evaluate summary quality and decide if retry needed

**Inputs**:
- `summary`: Generated summary
- `summary_bullets`: Key points
- `valid_content`: Number of sources used
- `query`: Original query
- `iterations`: Current retry count

**Outputs**:
- `reflection_score`: Final quality score (0-1)
- `reflection_notes`: Quality assessment
- `needs_improvement`: Boolean retry flag
- `next_agent`: Route decision (search or END)

**Key Logic**:
```python
1. Use LLM to evaluate summary on:
   - Relevance (does it answer query?)
   - Completeness (covers all aspects?)
   - Quality (well-structured?)
   - Source coverage (enough sources?)

2. Generate quality score (0-1)

3. Decide:
   IF score < 0.6 AND iterations < 2:
      → Route back to SEARCH (retry)
   ELSE:
      → Route to END (finish)
```

**Retry Logic**:
```python
Max iterations: 2 (1 retry)
Triggers for retry:
  - Quality score < 0.6
  - < 3 valid sources used
  - Incomplete coverage detected

Modifies for retry:
  - Adjusts search strategy
  - Uses different queries
  - Looks for more sources
```

---

## 🔀 Dynamic Routing

### **Conditional Edge: Route After Reflection**

```python
def route_after_reflection(state: PipelineState) -> str:
    if state["next_agent"] == "search":
        return "search"  # Retry: Loop back
    else:
        return END       # Finish: Exit pipeline
```

### **Routing Decision Points**

| Current Agent | Condition | Next Agent |
|---|---|---|
| Planner | Always | Search |
| Search | Always | Scraper |
| Scraper | Always | Evaluator |
| Evaluator | Always | Summarizer |
| Summarizer | Always | Reflection |
| Reflection | Score < 0.6 AND iterations < 2 | Search (retry) |
| Reflection | Score ≥ 0.6 OR iterations ≥ 2 | END (finish) |

---

## 🔄 State Management & Information Flow

### **Data Flow Example**

```
1. Planner gets:
   ├─ query: "machine learning healthcare"
   └─ generates:
      ├─ plan: 4 steps
      └─ search_queries: 3 queries

2. Search gets:
   ├─ search_queries: 3 queries
   └─ generates:
      ├─ urls: 8 unique URLs
      └─ search_results: metadata

3. Scraper gets:
   ├─ urls: 8 URLs
   └─ generates:
      ├─ scraped_content: 8 items
      └─ each with: {url, title, content, quality}

4. Evaluator gets:
   ├─ scraped_content: 8 items
   ├─ query: original query
   └─ generates:
      ├─ evaluations: 8 scores
      └─ valid_content: 4-5 filtered items

5. Summarizer gets:
   ├─ valid_content: 4-5 items
   ├─ query: original query
   └─ generates:
      ├─ summary_bullets: 5-7 points
      └─ summary: formatted output

6. Reflection gets:
   ├─ summary: formatted text
   ├─ valid_content: 4-5 sources
   └─ generates:
      ├─ reflection_score: 0.75
      ├─ needs_improvement: false
      └─ next_agent: END
```

---

## 📊 Advanced Features

### **1. Multi-Query Search Strategy**

Instead of single query:
```python
# Single approach (❌ Limited)
search("machine learning healthcare")

# Multi-query approach (✅ Better coverage)
search("machine learning healthcare")      # Primary
search("AI medical diagnosis")             # Alternative angle
search("deep learning clinical applications") # Specific focus
```

### **2. Iterative Refinement Loop**

```python
Iteration 1:
  ├─ Search with initial strategy
  ├─ Get 8 URLs
  ├─ Scrape and evaluate
  ├─ Generate summary
  └─ Reflection: Score 0.55 (needs improvement)
      ↓
Iteration 2:
  ├─ Search with adjusted strategy
  ├─ Get 8 NEW URLs (different queries)
  ├─ Scrape with higher standards
  ├─ Generate improved summary
  └─ Reflection: Score 0.82 (good!)
      ↓
FINISH
```

### **3. Quality Filtering**

Progressive filtering ensures only best content in summary:

```
Original URLs: 8
After scraping: 8 pieces of content
After evaluation: 4-5 high-quality pieces
Final summary: Based on best content only
```

### **4. Content Classification**

Balanced source variety:

```
results may include:
├─ 2 Technical sources (GitHub, docs)
├─ 2 Articles (blogs, news)
├─ 1 Community source (forums)
└─ 1-2 Documentation sources
```

---

## 🚀 Usage Example

### **Basic Usage**

```python
from langgraph_multi_agent_system import create_graph

# Create graph
graph = create_graph()

# Run pipeline
result = graph.invoke({
    "query": "machine learning in healthcare",
    "plan": [],
    "search_queries": [],
    "urls": [],
    "scraped_content": [],
    "evaluations": [],
    "valid_content": [],
    "summary": "",
    "summary_bullets": [],
    "reflection_score": 0.0,
    "needs_improvement": False,
    "iterations": 0,
    "max_iterations": 2,
    "timestamps": {},
    "messages": [],
    "current_agent": "start",
    "next_agent": "planner",
    "error": None
})

# Get results
print(result["summary"])
print(f"Quality: {result['reflection_score']:.2f}")
print(f"Sources: {len(result['valid_content'])}")
```

### **Advanced: Run Multiple Times**

```python
from langgraph_multi_agent_system import create_graph

graph = create_graph()

queries = [
    "machine learning in healthcare",
    "AI for climate change",
    "blockchain applications"
]

for query in queries:
    print(f"Processing: {query}")
    result = graph.invoke({...})
    print(f"Quality: {result['reflection_score']:.2f}\n")
```

---

## 📈 Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Search queries executed | 3 | Per pipeline run |
| URLs collected | 8 max | Deduplicated |
| Content scraped | 8 pieces | With error handling |
| Quality filter rate | 50% | ~4 sources kept |
| LLM calls | 5-6 |Planner, Evaluator(×8), Summarizer, Reflection |
| Max iterations | 2 | 1 initial, 1 retry |
| Typical runtime | 30-60s | Depends on API response times |

---

## 🔒 Error Handling

### **Per-Agent Error Handling**

| Agent | Error | Behavior |
|-------|-------|----------|
| Planner | LLM error | Use fallback plan |
| Search | API timeout | Skip query, continue |
| Scraper | Parse error | Log & continue with next URL |
| Evaluator | LLM error | Use quality heuristics |
| Summarizer | No valid content | Use best available |
| Reflection | LLM error | Use auto-evaluation |

### **Graceful Degradation**

```python
Try-Except Pattern:
  1. Attempt LLM operation
  2. If success: use LLM result
  3. If fail: use heuristic fallback
  4. Log error but continue
  5. Deliver best-effort result
```

---

## 🎯 Key Advantages Over Linear Pipeline

| Feature | Linear | Multi-Agent |
|---------|--------|------------|
| Search strategy | Fixed | Adaptive (3+ queries) |
| Error recovery | None | Graceful fallbacks |
| Quality assurance | None | Reflection agent |
| Iterative improvement | No | Yes (retry loop) |
| State sharing | Yes | Yes (better) |
| Routing | Fixed | Dynamic conditional |
| Adaptability | Low | High |
| Source diversity | Limited | 5+ sources |
| Retry capability | No | Yes |

---

## 📚 Files in This System

| File | Purpose | Size |
|------|---------|------|
| `langgraph_multi_agent_system.py` | Main system | 600+ lines |
| `LANGGRAPH_ARCHITECTURE.md` | This guide | Reference |
| `example_multi_agent.py` | Usage examples | 50-100 lines |
| `test_multi_agent.py` | Test suite | 100+ lines |

---

## 🎓 Learning Path

1. **Read**: This architecture guide
2. **Run**: `python langgraph_multi_agent_system.py`
3. **Modify**: Adjust agents or routing logic
4. **Extend**: Add new agents or evaluation criteria
5. **Deploy**: Integrate into production

---

## ✅ Checklist for Understanding

- [ ] Understand 6 agents and their purposes
- [ ] Grasp shared state architecture
- [ ] Follow data flow through pipeline
- [ ] Understand dynamic routing
- [ ] Know retry/reflection logic
- [ ] Can identify error handling patterns
- [ ] Can explain state modifications

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Type**: LangGraph Multi-Agent System with Dynamic Routing
