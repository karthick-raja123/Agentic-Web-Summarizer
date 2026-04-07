# EVALUATION SYSTEM - QUICK USAGE GUIDE

**Get started with evaluation in 5 minutes!**

---

## 🚀 The 60-Second Setup

```python
from evaluation_metrics import calculate_quality_score
from evaluation_system import store_evaluation_result

# 1. Evaluate quality
scores = calculate_quality_score(source_text, summary_text)

# 2. Store results
store_evaluation_result("search query", ["url1", "url2"], source_text, summary_text, scores)

# 3. Done! Results saved to CSV and JSON
```

---

## 📋 Common Tasks

### Task 1: Evaluate a Summary
```python
from evaluation_metrics import calculate_quality_score, get_quality_grade

source = "Machine learning is a subset of artificial intelligence..."
summary = "• ML is a subset of AI\n• Learns from data"

scores = calculate_quality_score(source, summary)

print(f"Relevance: {scores['relevance']:.1%}")
print(f"Coverage: {scores['coverage']:.1%}")
print(f"Grade: {get_quality_grade(scores['overall_quality'])}")
print(f"Status: {scores['evaluation_status']}")
```

**Output**:
```
Relevance: 52.1%
Coverage: 78.5%
Grade: C (Acceptable)
Status: pass
```

### Task 2: Store and Retrieve Results
```python
from evaluation_system import store_evaluation_result, get_results_for_query

# Store
scores = calculate_quality_score(source, summary)
store_evaluation_result(
    query="python tutorials",
    urls=["https://example.com/python"],
    source_content=source,
    summary=summary,
    scores=scores
)

# Retrieve all results for this query
results = get_results_for_query("python tutorials")
print(f"Found {len(results)} evaluations")

for r in results:
    print(f"  {r['timestamp']}: {r['overall_quality']:.1%}")
```

### Task 3: View Batch Statistics
```python
from evaluation_system import calculate_batch_stats

stats = calculate_batch_stats()

print(f"Total evaluations: {stats['total_evaluations']}")
print(f"Average quality: {stats['overall_quality_avg']:.1%}")
print(f"Pass rate: {stats['grade_distribution'].get('pass', 0)} / {stats['total_evaluations']}")
```

### Task 4: Generate Report
```python
from evaluation_system import export_summary_report

report_path = export_summary_report()
print(f"Report saved to: {report_path}")

# View in markdown viewer or text editor
# File contains: statistics, trends, top evaluations
```

### Task 5: Export for Analysis
```python
from evaluation_system import export_as_json, export_as_csv

# Export to specific location
json_path = export_as_json("my_results.json")
csv_path = export_as_csv("my_results.csv")

print(f"JSON: {json_path}")
print(f"CSV: {csv_path}")
```

---

## 🧪 Run Tests

```bash
cd "d:\Git\Visual Web Agent\Visual-web-Agent"

# Quick smoke test
python test_quick.py

# Full test suite
pytest test_evaluation_system.py -v

# Test specific functionality
pytest test_evaluation_system.py::TestRelevanceScoring -v

# With coverage report
pytest test_evaluation_system.py --cov=evaluation_metrics --cov=evaluation_system
```

---

## 📊 Sample Outputs

### Individual Evaluation Result
```python
{
    'relevance': 0.823,
    'coverage': 0.756,
    'redundancy': 0.0,
    'coherence': 1.0,
    'conciseness': 0.78,
    'overall_quality': 0.795,
    'evaluation_status': 'pass'
}
```

### Batch Statistics
```python
{
    'total_evaluations': 150,
    'relevance_avg': 0.823,
    'relevance_min': 0.401,
    'relevance_max': 0.985,
    'coverage_avg': 0.756,
    'coverage_min': 0.324,
    'coverage_max': 0.972,
    'overall_quality_avg': 0.789,
    'overall_quality_min': 0.452,
    'overall_quality_max': 0.961,
    'grade_distribution': {
        'pass': 120,
        'warning': 25,
        'fail': 5
    }
}
```

---

## 🎯 Use Cases

### Use Case 1: Quality Gate for Production
```python
scores = calculate_quality_score(source, summary)

if scores['evaluation_status'] == 'pass':
    # Publish summary
    publish_to_database(summary)
else:
    # Flag for review
    send_to_review_queue(summary, scores)
```

### Use Case 2: Quality Monitoring Dashboard
```python
# Run periodically
stats = calculate_batch_stats()

if stats['overall_quality_avg'] < 0.75:
    # Alert team
    send_alert(f"Quality dropped to {stats['overall_quality_avg']:.1%}")
else:
    # Log success
    log_success(f"Average quality: {stats['overall_quality_avg']:.1%}")
```

### Use Case 3: A/B Testing Summarizers
```python
# Summarizer A
score_a = calculate_quality_score(source, summary_a)

# Summarizer B
score_b = calculate_quality_score(source, summary_b)

# Compare
if score_a['overall_quality'] > score_b['overall_quality']:
    print("Summarizer A is better")
else:
    print("Summarizer B is better")
```

### Use Case 4: Historical Analysis
```python
# Get all evaluations
results = get_all_results()

# Find best performers
best = max(results, key=lambda x: x['overall_quality'])
worst = min(results, key=lambda x: x['overall_quality'])

print(f"Best: {best['query']} ({best['overall_quality']:.1%})")
print(f"Worst: {worst['query']} ({worst['overall_quality']:.1%})")
```

---

## 🔌 Integration Examples

### Add to Streamlit App
```python
import streamlit as st
from evaluation_metrics import calculate_quality_score

# After generating summary
if summary and source_content:
    scores = calculate_quality_score(source_content, summary)
    
    # Create evaluation tab
    with st.tabs(["Summary", "Evaluation"]):
        st.write(summary)
        
        # Display metrics
        st.metric("Relevance", f"{scores['relevance']:.1%}")
        st.metric("Coverage", f"{scores['coverage']:.1%}")
        st.metric("Overall Quality", f"{scores['overall_quality']:.1%}")
        
        # Status badge
        if scores['evaluation_status'] == 'pass':
            st.success("✓ Production Ready")
        elif scores['evaluation_status'] == 'warning':
            st.warning("⚠ Review Recommended")
        else:
            st.error("✗ Needs Revision")
```

### Add to Pipeline
```python
from evaluation_system import store_evaluation_result

# After summarization
if summary:
    scores = calculate_quality_score(combined_content, summary)
    
    # Store for tracking
    store_evaluation_result(
        query=search_query,
        urls=source_urls,
        source_content=combined_content,
        summary=summary,
        scores=scores
    )
    
    # Log result
    logger.info(f"Summary quality: {scores['overall_quality']:.1%}")
    
    # Take action based on quality
    if scores['overall_quality'] < 0.5:
        logger.warning("Low quality summary - may need regeneration")
```

### Add to FastAPI Endpoint
```python
from fastapi import FastAPI
from evaluation_metrics import calculate_quality_score

app = FastAPI()

@app.post("/evaluate")
async def evaluate(source: str, summary: str):
    scores = calculate_quality_score(source, summary)
    return {
        "scores": scores,
        "status": scores["evaluation_status"],
        "grade": get_quality_grade(scores["overall_quality"])
    }

# GET /evaluate?source=...&summary=...
```

---

## ⚙️ Configuration

### Change Quality Thresholds
```python
# Current (in evaluate_quality_score):
# if overall_quality > 0.6: status = "pass"
# elif overall_quality > 0.4: status = "warning"
# else: status = "fail"

# To customize:
def get_status(quality):
    if quality > 0.75:
        return "excellent"
    elif quality > 0.60:
        return "good"
    elif quality > 0.40:
        return "needs_review"
    else:
        return "poor"
```

### Change Metric Weights
```python
# Current (in education_metrics.py):
# 35% Relevance, 25% Coverage, 20% Coherence, 20% Conciseness

# To customize:
overall_quality = (
    relevance * 0.40 +      # Increase relevance importance
    coverage * 0.30 +       # Increase coverage importance
    coherence * 0.15 +      # Decrease coherence importance
    conciseness * 0.15      # Decrease conciseness importance
)
```

---

## 🐛 Debugging

### Check Why Relevance is Low
```python
from evaluation_metrics import extract_key_phrases, normalize_text

source = "your source text..."
summary = "your summary text..."

# Compare key phrases
source_phrases = extract_key_phrases(source, num_phrases=10)
summary_phrases = extract_key_phrases(summary, num_phrases=10)

print("Source phrases:", source_phrases)
print("Summary phrases:", summary_phrases)

# Compare normalized text
print("\nNormalized source:", normalize_text(source)[:100])
print("Normalized summary:", normalize_text(summary)[:100])
```

### Check for Redundancy
```python
from evaluation_metrics import detect_redundancy

summary = "your summary with bullets..."

redundant_lines, score = detect_redundancy(summary)
print(f"Redundancy score: {score:.1%}")
print("Redundant lines found:")
for line in redundant_lines:
    print(f"  - {line}")
```

### View Stored Data
```python
# View CSV
import csv
with open("evaluation_results/evaluations.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)

# View JSON
import json
with open("evaluation_results/evaluations.json") as f:
    data = json.load(f)
    print(json.dumps(data, indent=2))
```

---

## 📈 Performance Tips

1. **Batch Evaluation**: Use stored results for trend analysis
2. **Cache Results**: Don't re-evaluate same content
3. **Async Storage**: Store results in background thread for speed
4. **Query Optimization**: Use `get_results_for_query()` instead of loading all results

---

## 🎓 Learning Resources

- **Full API**: See `EVALUATION_SYSTEM_GUIDE.md`
- **Test Examples**: See `test_evaluation_system.py`
- **Live Examples**: Run `test_quick.py`
- **Architecture**: See project diagrams in `EVALUATION_SYSTEM_GUIDE.md`

---

## ✅ Verification Checklist

Before deploying, verify:

- ✓ All functions import without errors
- ✓ `test_quick.py` runs successfully
- ✓ Results directory created automatically
- ✓ CSV and JSON files generated
- ✓ Scores are always 0-1 range
- ✓ Status is always pass/warning/fail

```bash
# Full verification
python test_quick.py && pytest test_evaluation_system.py -q
```

---

**Ready to evaluate!** 🚀

See `EVALUATION_SYSTEM_GUIDE.md` for complete documentation.
