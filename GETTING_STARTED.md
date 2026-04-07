# 🎯 30-Minute Getting Started Guide

## What You'll Learn

- ✅ How to run the multi-agent system
- ✅ Understand the 6 agents  
- ✅ See different execution paths
- ✅ Get results in multiple formats
- ✅ Troubleshoot common issues

**Time needed: ~30 minutes**

---

## Step 1: Setup (5 minutes)

### Option A: Quick Start (Recommended)

```bash
# Clone or navigate to project
cd Visual-web-Agent

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Mac/Linux

# Verify installation
python -c "import langgraph; print('✅ Ready!')"
```

### Option B: Fresh Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
# GOOGLE_API_KEY=your_key
# SERPER_API_KEY=your_key
```

---

## Step 2: Try Your First Query (2 minutes)

### Method 1: Command Line (Easiest)

```bash
python multi_agent_cli.py "What is artificial intelligence?"
```

**Expected Output:**
```
================================================================================
  MULTI-AGENT PIPELINE
================================================================================

Query: What is artificial intelligence?

Configuration:
  • Evaluation: ENABLED
  • Formatting: DISABLED

================================================================================
  STARTING EXECUTION...
================================================================================

▶ EXECUTION PLAN
  ──────────────────────────────────────────────────────────────
  Query Type: general
  Complexity: medium
  ...

▶ AGENT EXECUTION PATH
  Routing Order:
    1. 🎯 PLANNER
    2. 🔍 SEARCH
    3. 🪄 SCRAPER
    4. ⭐ EVALUATOR
    5. 📝 SUMMARIZER

▶ SEARCH RESULTS
  Found 5 URLs:
    1. What is AI? - Technical Overview
    2. Introduction to AI - Wikipedia
    ...

▶ SUMMARY
  AI (Artificial Intelligence) is...
  • Machine learning enables systems to learn
  • Deep learning uses neural networks
  ...

================================================================================
```

### Method 2: Python Code

```python
from multi_agent_pipeline import MultiAgentPipeline

# Create pipeline
pipeline = MultiAgentPipeline()

# Run query
result = pipeline.run("What is machine learning?")

# Print results
print(f"✅ Status: {result['status']}")
print(f"📝 Summary:\n{result['summary']}")
print(f"🔀 Path: {' → '.join(result['agent_history'])}")
```

### Method 3: Web UI

```bash
streamlit run multi_agent_app.py
# Opens: http://localhost:8501
```

---

## Step 3: Understanding the 6 Agents (8 minutes)

### What Happens Behind the Scenes

```
INPUT: "Best programming languages to learn"
│
├──► 🎯 PLANNER: "This is a 'how-to' query"
│    └─ Decision: Enable evaluation, Detailed summary
│
├──► 🔍 SEARCH: "Find relevant articles"
│    └─ Result: 5 URLs about programming languages
│
├──► 🪄 SCRAPER: "Extract clean text"
│    └─ Result: 12,500 characters of content
│
├──► ⭐ EVALUATOR: "Is this relevant?"
│    ├─ Article 1: Score 0.85 ✅ Keep
│    ├─ Article 2: Score 0.45 ❌ Filter (promotional)
│    └─ Article 3: Score 0.78 ✅ Keep
│
├──► 📝 SUMMARIZER: "Create bullet-point summary"
│    └─ Result: 
│        • Python: Beginner-friendly, great for AI
│        • JavaScript: Web development, versatile
│        • Java: Enterprise, strong typing
│
└──► 💾 FORMATTER: "Export to CSV/JSON"
     └─ Result: 
        Programs.csv (comparison table)
        Programs.json (structured data)

OUTPUT: Summary + Files
```

### Agent Details

**🎯 Planner Agent**
- Analyzes your query
- Decides: Simple, Medium, or Complex?
- Sets up: Should we filter content? Export formats?
- Duration: ~1 second

**🔍 Search Agent**  
- Uses Serper API to find URLs
- Returns top 5-10 results
- Duration: ~2 seconds

**🪄 Scraper Agent**
- Visits each URL
- Extracts clean text
- Removes ads, HTML, junk
- Duration: ~3 seconds

**⭐ Evaluator Agent** (Optional)
- Scores content relevance (0-1)
- Keeps only high-quality content (>0.6)
- Detects bias and spam
- Duration: ~2 seconds

**📝 Summarizer Agent**
- Uses AI to create summary
- Makes 5-7 bullet points
- Keeps important details only
- Duration: ~3 seconds

**💾 Formatter Agent** (Optional)
- Creates CSV for spreadsheets
- Creates JSON for APIs
- Creates Markdown for docs
- Duration: ~1 second

---

## Step 4: Try Different Query Types (8 minutes)

### Academic Query

```bash
python multi_agent_cli.py "Latest research in quantum computing" --show-plan
```

**What happens:**
- Planner: "Academic - needs strict evaluation"
- Evaluation: ENABLED (filters promotional content)
- Result: High-quality academic sources

### News Query

```bash
python multi_agent_cli.py "AI industry news today" --no-eval
```

**What happens:**
- Planner: "News - simple, many results OK"
- Evaluation: SKIPPED (faster)
- Result: Quick news summary

### Product Query

```bash
python multi_agent_cli.py "best coffee makers under $100" --enable-format
```

**What happens:**
- Planner: "Product - evaluate for bias"
- Evaluation: ENABLED (filter promotional)
- Formatter: Generates CSV comparison table
- Result: Clean comparison + CSV file

### How-To Query

```bash
python multi_agent_cli.py "how to learn machine learning"
```

**What happens:**
- Planner: "How-to - need structured steps"
- Content: Step-by-step instructions prioritized
- Result: Actionable steps

---

## Step 5: Visualization & Debugging (4 minutes)

### See the Agent Graph

```bash
python multi_agent_cli.py "query" --show-graph
```

**Output:**
```
AGENT FLOW:

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
   
... and so on
```

### Enable Verbose Logging

```bash
python multi_agent_cli.py "query" --verbose
```

**Output includes:**
- Timestamps for each step
- Detailed error messages
- Agent processing details
- Performance metrics

### Save Results to File

```bash
python multi_agent_cli.py "query" --output results.json
```

**File created:** `results.json` with all results

---

## Step 6: Common Tasks (3 minutes)

### Task 1: Disable Evaluation (Faster)

```bash
# CLI: Skip evaluation for speed
python multi_agent_cli.py "query" --no-eval

# Python:
pipeline = MultiAgentPipeline(enable_evaluation=False)
result = pipeline.run("query")
```

### Task 2: Get Multiple Formats

```bash
# CLI: Generate CSV, JSON, Markdown
python multi_agent_cli.py "topic" --enable-format --output result.json

# Python:
pipeline = MultiAgentPipeline(enable_formatting=True)
result = pipeline.run("topic")

# Access formats:
print(result['formatted_output']['formats'].keys())
# dict_keys(['csv', 'json', 'markdown', 'text'])
```

### Task 3: Batch Process Multiple Queries

```python
from multi_agent_pipeline import MultiAgentPipeline

pipeline = MultiAgentPipeline()

topics = [
    "What is AI?",
    "Machine learning trends",
    "Deep learning basics"
]

for topic in topics:
    result = pipeline.run(topic)
    print(f"✅ {topic}: {result['status']}")
    print(result['summary'][:100])  # First 100 chars
    print()
```

### Task 4: Check Evaluation Results

```python
result = pipeline.run("query")

if result.get('evaluation_results'):
    eval_res = result['evaluation_results']
    
    print(f"Kept: {eval_res['relevant_count']} items")
    print(f"Filtered: {eval_res['filtered_count']} items")
    print(f"Avg score: {eval_res['avg_relevance']:.2f}")
    print(f"Recommendation: {eval_res['recommendation']}")
```

---

## Troubleshooting

### Problem: "No module named 'langgraph'"

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Problem: "API key not found"

```bash
# Solution: Create .env file
echo GOOGLE_API_KEY=your_key > .env
echo SERPER_API_KEY=your_key >> .env
```

### Problem: "No search results found"

```bash
# Try:
# 1. Check internet connection
# 2. Disable evaluation (faster)
python multi_agent_cli.py "query" --no-eval
# 3. Check with verbose
python multi_agent_cli.py "query" --verbose
```

### Problem: "Evaluation scores too low"

```bash
# Solution: Disable evaluation
python multi_agent_cli.py "query" --no-eval
```

### Problem: "Script is slow"

```bash
# Solution: Use minimal pipeline
python -c "
from multi_agent_pipeline import MultiAgentPipeline
p = MultiAgentPipeline(enable_evaluation=False, enable_formatting=False)
print(p.run('query')['summary'])
"
```

---

## Configuration Options

| Option | Default | Effect |
|--------|---------|--------|
| `enable_evaluation` | True | Enable content filtering |
| `enable_formatting` | False | Generate CSV/JSON/Markdown |
| `--no-eval` | - | Disable evaluation (faster) |
| `--enable-format` | - | Enable output formats |
| `--show-graph` | - | Display agent flow |
| `--show-plan` | - | Show execution plan |
| `--verbose` | - | Detailed logging |
| `--output FILE` | - | Save results to JSON |

---

## Performance Tips

| Goal | Solution |
|------|----------|
| **Fastest execution** | `--no-eval` disables evaluation |
| **Best quality** | Default settings with evaluation |
| **Multiple formats** | `--enable-format` generates all |
| **Debugging** | `--verbose --show-plan` |

---

## What's Next?

✅ **Beginner**: Try the 4 query types above  
✅ **Intermediate**: Run the 10 examples: `python example_multi_agent.py`  
✅ **Advanced**: Read [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)  
✅ **Developer**: Check [multi_agent_pipeline.py](multi_agent_pipeline.py)  

---

## Quick Reference

```bash
# Basic usage
python multi_agent_cli.py "your question"

# With options
python multi_agent_cli.py "query" --show-plan --verbose

# Multiple formats
python multi_agent_cli.py "query" --enable-format

# Save results
python multi_agent_cli.py "query" --output results.json

# See examples
python example_multi_agent.py 1

# Web interface
streamlit run multi_agent_app.py
```

---

## Success Checklist

- ✅ Installation complete
- ✅ First query runs successfully  
- ✅ Results include summary
- ✅ Can see agent routing path
- ✅ Understand the 6 agents
- ✅ Tried different query types
- ✅ Can enable/disable evaluation
- ✅ Know how to get multiple formats

**Congratulations! 🎉 You're ready to use the multi-agent system!**

---

## Need Help?

1. **Quick issues**: See "Troubleshooting" section above
2. **Detailed guide**: Read [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)
3. **Quick reference**: Check [MULTI_AGENT_QUICKSTART.md](MULTI_AGENT_QUICKSTART.md)
4. **Examples**: Run `python example_multi_agent.py`
5. **Architecture**: See [EVOLUTION.md](EVOLUTION.md)

---

**Happy querying! 🚀**
