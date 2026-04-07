# 🚀 LangGraph Multi-Agent System - Quick Start Guide

**Get started in 5 minutes!**

---

## ⚡ Quickest Start

### Run the System (30 seconds)
```bash
cd "d:\Git\Visual Web Agent\Visual-web-Agent"
python langgraph_multi_agent_system.py
```

**You'll be prompted to enter a query. Then the system automatically:**
1. Breaks query into steps (Planner)
2. Searches with multiple strategies (Search)
3. Scrapes content from URLs (Scraper)
4. Filters low-quality content (Evaluator)
5. Generates summary (Summarizer)
6. Checks quality and retries if needed (Reflection)

---

## 📊 Output Explanation

```
════════════════════════════════════════════════════════════
🤖 PLANNER AGENT
════════════════════════════════════════════════════════════
Intent: What is machine learning in healthcare
Plan steps: 4
Search strategies: 3

════════════════════════════════════════════════════════════
🔍 SEARCH AGENT
════════════════════════════════════════════════════════════
  Searching: machine learning healthcare (priority: 1)
  ✓ Found 5 results
  Searching: AI medical diagnosis (priority: 2)
  ✓ Found 5 results
  Searching: deep learning clinical (priority: 3)
  ✓ Found 5 results

✓ Collected 8 unique URLs

════════════════════════════════════════════════════════════
🌐 SCRAPER AGENT
════════════════════════════════════════════════════════════
  [1] Scraping: https://example.com/ml-healthcare
  ✓ Content extracted (1850 chars, quality: 0.78)
  [2] Scraping: https://example.com/ai-diagnosis
  ✓ Content extracted (2100 chars, quality: 0.82)
  ...

✓ Scraped 8 pages

════════════════════════════════════════════════════════════
🎯 EVALUATOR AGENT
════════════════════════════════════════════════════════════
  ✓ Valid: Medical AI Applications (0.85)
  ✓ Valid: Healthcare Deep Learning (0.78)
  ✗ Filtered: Generic AI Article (0.32)
  ...

✓ Valid content: 5 sources

════════════════════════════════════════════════════════════
📝 SUMMARIZER AGENT
════════════════════════════════════════════════════════════

✓ Summary created with 6 bullet points

════════════════════════════════════════════════════════════
🔄 REFLECTION AGENT
════════════════════════════════════════════════════════════

✓ Summary accepted - Score: 0.82

════════════════════════════════════════════════════════════
✅ PIPELINE COMPLETE
════════════════════════════════════════════════════════════

📊 FINAL SUMMARY
────────────────────────────────────────────────────────────
Machine learning in healthcare involves using AI algorithms
to improve diagnosis, treatment, and patient outcomes...

Key Points:
• Diagnostic imaging analysis using deep neural networks
• Predictive analytics for patient risk assessment
• Drug discovery acceleration through ML models
• Personalized treatment recommendations
• Administrative process automation
• Real-time patient monitoring systems

Considerations:
- Requires significant amounts of training data
- Privacy and regulatory compliance are critical
- Model interpretability is essential for clinical use

📈 METRICS
────────────────────────────────────────────────────────────
✓ Total iterations: 1
✓ Valid sources: 5
✓ Reflection score: 0.82
✓ Agents called: 6
```

---

## 💻 Usage Examples

### Example 1: Basic Usage

```python
from langgraph_multi_agent_system import create_graph, PipelineState
from datetime import datetime

# Create the multi-agent graph
graph = create_graph()

# Prepare initial state
initial_state: PipelineState = {
    "query": "climate change solutions",
    "user_intent": "",
    "plan": [],
    "plan_iterations": 0,
    "search_queries": [],
    "search_results": [],
    "urls": [],
    "scraped_content": [],
    "scraping_iterations": 0,
    "evaluations": [],
    "valid_content": [],
    "raw_summary": "",
    "summary": "",
    "summary_bullets": [],
    "reflection_score": 0.0,
    "reflection_notes": "",
    "needs_improvement": False,
    "iterations": 0,
    "max_iterations": 2,
    "timestamps": {},
    "messages": [],
    "current_agent": "start",
    "next_agent": "planner",
    "error": None
}

# Run the pipeline
result = graph.invoke(initial_state)

# Get results
print("Summary:")
print(result["summary"])
print(f"\nQuality Score: {result['reflection_score']:.2f}")
print(f"Sources Used: {len(result['valid_content'])}")
```

### Example 2: With Custom Max Iterations

```python
# Allow more retries for complex queries
initial_state["max_iterations"] = 3

result = graph.invoke(initial_state)
print(f"Iterations used: {result['iterations']}")
```

### Example 3: Batch Processing

```python
from langgraph_multi_agent_system import create_graph, PipelineState

graph = create_graph()

queries = [
    "artificial intelligence in agriculture",
    "renewable energy technologies",
    "quantum computing applications",
]

results = []

for query in queries:
    print(f"Processing: {query}")
    
    state: PipelineState = {
        "query": query,
        "plan": [], "search_queries": [],
        "urls": [], "scraped_content": [],
        "evaluations": [], "valid_content": [],
        "raw_summary": "", "summary": "", "summary_bullets": [],
        "reflection_score": 0.0, "iterations": 0,
        "max_iterations": 2,
        "plan_iterations": 0, "scraping_iterations": 0,
        "reflection_notes": "", "needs_improvement": False,
        "timestamps": {}, "messages": [],
        "current_agent": "start", "next_agent": "planner",
        "error": None, "user_intent": ""
    }
    
    result = graph.invoke(state)
    results.append({
        "query": query,
        "summary": result["summary"],
        "score": result["reflection_score"],
        "sources": len(result["valid_content"])
    })
    
    print(f"  Score: {result['reflection_score']:.2f}")
    print()

# Display results
for r in results:
    print(f"{r['query']}: {r['score']:.2f} ({r['sources']} sources)")
```

### Example 4: Modify Search Strategy

```python
# Create graph
graph = create_graph()

# Prepare state
state = {...}  # Copy from Example 1

# Run with custom search queries
state["search_queries"] = [
    {"query": "machine learning algorithms", "priority": 1, "depth": "deep"},
    {"query": "AI neural networks", "priority": 2, "depth": "deep"},
    {"query": "deep learning training", "priority": 3, "depth": "shallow"},
    {"query": "ML model optimization", "priority": 4, "depth": "deep"},
]

result = graph.invoke(state)
```

### Example 5: Access Detailed Logs

```python
result = graph.invoke(initial_state)

# Print all messages
print("Execution Log:")
for i, msg in enumerate(result["messages"], 1):
    print(f"{i:2}. {msg}")

# Print timestamps
print("\nTiming:")
for agent, ts in result["timestamps"].items():
    print(f"{agent}: {ts}")

# Detailed content breakdown
print(f"\nContent Analysis:")
print(f"URLs found: {len(result['urls'])}")
print(f"Content scraped: {len(result['scraped_content'])}")
print(f"Valid content: {len(result['valid_content'])}")
print(f"Quality: {result['reflection_score']:.2f}")
```

---

## 🔧 Customization Examples

### Customize: Change Max Iterations

```python
# Allow up to 3 retries
state["max_iterations"] = 3  # Default is 2
```

### Customize: Adjust Quality Threshold

```python
# In evaluator_agent function, change:
# if is_valid and combined_score > 0.4:
# to:
# if is_valid and combined_score > 0.6:  # Higher bar
```

### Customize: Add New Agent

```python
def my_custom_agent(state: PipelineState) -> PipelineState:
    """My custom agent does something special"""
    # Your custom logic here
    state["messages"].append("✓ Custom agent ran")
    state["current_agent"] = "custom"
    state["next_agent"] = "reflection"
    return state

# Add to workflow
workflow.add_node("custom", my_custom_agent)
workflow.add_edge("summarizer", "custom")
workflow.add_edge("custom", "reflection")
```

---

## 🎯 Use Cases

### Use Case 1: Research Synthesis
```python
# Gather information from multiple sources
query = "latest developments in quantum computing"
# System automatically:
# - Searches from multiple angles
# - Finds diverse sources
# - Evaluates quality
# - Synthesizes comprehensive summary
```

### Use Case 2: Fact Checking
```python
# Verify claims with evidence
query = "effectiveness of solar energy vs fossil fuels"
# System:
# - Gets multiple perspectives
# - Filters reliable sources
# - Highlights key facts
# - Retries if low confidence
```

### Use Case 3: Trend Analysis
```python
# Analyze current trends
query = "AI ethics considerations and trends"
# System:
# - Finds recent articles and research
# - Extracts key insights
# - Evaluates source quality
# - Provides comprehensive overview
```

### Use Case 4: Competitive Intelligence
```python
# Research competitors
query = "top AI companies and their products"
# System:
# - Searches with multiple strategies
# - Extracts company details
# - Evaluates and filters
# - Synthesizes competitive overview
```

---

## 📈 Monitoring & Debugging

### Check Quality Score

```python
score = result["reflection_score"]
if score > 0.8:
    print("✓ Excellent quality")
elif score > 0.6:
    print("⚠ Acceptable quality")
else:
    print("❌ Low quality")
```

### Check Retry Status

```python
iterations = result["iterations"]
max_iter = result["max_iterations"]

if iterations == max_iter:
    print(f"⚠ Max iterations reached ({iterations})")
else:
    print(f"✓ Completed in {iterations} iteration(s)")
```

### Analyze Source Distribution

```python
sources_by_type = {}
for content in result["valid_content"]:
    src_type = content.get("source_type", "unknown")
    sources_by_type[src_type] = sources_by_type.get(src_type, 0) + 1

print("Source types used:")
for src_type, count in sources_by_type.items():
    print(f"  {src_type}: {count}")
```

### Debug Individual Agents

```python
# Print messages from evaluation phase
eval_msgs = [m for m in result["messages"] if "Valid:" in m or "Filtered:" in m]
print(f"Evaluation decisions ({len(eval_msgs)}):")
for msg in eval_msgs:
    print(f"  {msg}")
```

---

## ⚙️ Configuration Guide

### Max Iterations (Quality vs Speed Tradeoff)

```python
# 1 iteration (fast, may have quality issues)
state["max_iterations"] = 1

# 2 iterations (balanced - DEFAULT)
state["max_iterations"] = 2

# 3+ iterations (thorough, takes longer)
state["max_iterations"] = 3
```

### Search Strategy

```python
# Default: 3 searches (balanced)
state["search_queries"] = [
    {"query": "main topic", "priority": 1},
    {"query": "subtopic", "priority": 2},
    {"query": "related aspect", "priority": 3}
]

# More searches (thorough)
state["search_queries"] = [
    {"query": query1, "priority": 1},
    {"query": query2, "priority": 2},
    {"query": query3, "priority": 3},
    {"query": query4, "priority": 4},
    {"query": query5, "priority": 5}
]
```

### Evaluation Criteria

```python
# In evaluator_agent, adjust threshold:
if is_valid and combined_score > 0.4:  # More lenient
    valid_content.append(scraped)

# vs

if is_valid and combined_score > 0.6:  # More strict
    valid_content.append(scraped)
```

---

## 🔍 Comparison: Linear vs Multi-Agent

### Linear Pipeline (Old)
```
Input → Search (1 query) → Scrape (3 URLs) → Summarize → Output
```

**Issues**:
- Single search query (limited coverage)
- No quality filtering
- No retry capability
- No reflection

### Multi-Agent System (New)
```
Input → Plan → Search (3 queries) → Scrape → Evaluate → Summarize → Reflect → (Retry or Output)
```

**Benefits**:
- Multiple search strategies
- Quality filtering with LLM
- Intelligent retry with reflection
- Better source diversity
- Adaptive routing

### Performance Comparison

| Aspect | Linear | Multi-Agent |
|--------|--------|------------|
| Search queries | 1 | 3 |
| URLs considered | 3 | 8 |
| Quality filtering | No | Yes |
| Sources in summary | 1-3 | 3-5 |
| Retry capability | No | Yes |
| LLM calls | 2 | 6 |
| Typical runtime | 20-30s | 30-60s |
| Result quality | Good | Better |

---

## 🐛 Troubleshooting

### API Errors

```python
# If Serper API fails:
# - Check SERPER_API_KEY environment variable
# - Check API quota
# - System has fallback heuristics

# If Gemini API fails:
# - Check GEMINI_API_KEY environment variable
# - Check API quota
# - System has fallback logic
```

### Low Quality Scores

```python
# If reflection_score < 0.6:
# 1. Increase max_iterations for retry
# 2. Adjust evaluation criteria
# 3. Use more diverse search queries
# 4. Try clearer user query
```

### Running Out of Sources

```python
# If valid_content is too small:
# 1. Lower quality filter threshold (0.4 → 0.3)
# 2. Add more search queries
# 3. Increase max scraped URLs (8 → 12)
```

---

## 📊 Performance Tips

1. **Faster Results**: Set `max_iterations = 1`
2. **Better Quality**: Set `max_iterations = 3`
3. **More Sources**: Add search queries
4. **Stricter Filtering**: Increase quality threshold
5. **Fallback Options**: Catches all errors gracefully

---

## ✅ Next Steps

1. ✓ Run `python langgraph_multi_agent_system.py`
2. ✓ Try Example 1 (Basic Usage)
3. ✓ Try Example 3 (Batch Processing)
4. ✓ Read LANGGRAPH_ARCHITECTURE.md
5. ✓ Customize for your needs
6. ✓ Deploy to production

---

**Ready to use!** Start with:
```bash
python langgraph_multi_agent_system.py
```

---

**Version**: 1.0  
**Status**: ✅ Ready to Use  
**Support**: See LANGGRAPH_ARCHITECTURE.md
