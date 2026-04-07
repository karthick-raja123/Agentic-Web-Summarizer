"""
BENCHMARK ANALYSIS GUIDE - Finding & Fixing Issues
===================================================

How to use the benchmark analyzer to identify failure cases,
root causes, and get specific improvement recommendations.
"""

# ============================================================================
#                       QUICK START
# ============================================================================

## Step 1: Run Benchmarks First
```bash
python benchmark_runner.py --quick
```

## Step 2: Analyze Results
```bash
python analyze_benchmarks.py --full
```

## Expected Output
- List of worst performers
- Cases where intelligent system is slower
- Root cause analysis
- Specific fix recommendations
- Improvement plan

---

# ============================================================================
#                      ANALYSIS CAPABILITIES
# ============================================================================

### What the Analyzer Identifies

1. **WORST PERFORMERS**
   - Queries with slowest response times
   - Most expensive queries
   - Failed queries
   - Quality issues

2. **UNDERPERFORMANCE CASES**
   - Intelligent system slower than baseline
   - Higher costs than baseline
   - Quality too low
   - Wrong model selection

3. **FAILURE CASES**
   - API errors
   - Rate limits
   - Timeouts
   - Budget exceeded
   - Cache failures

4. **ROOT CAUSES**
   - Poor model selection
   - Cache inefficiency
   - Orchestration overhead
   - Quality evaluation cost
   - API reliability issues
   - Budget limits

5. **RECOMMENDATIONS**
   - Specific fixes for each issue
   - Implementation priority (CRITICAL/HIGH/MEDIUM/LOW)
   - Estimated impact
   - Step-by-step fix instructions

---

# ============================================================================
#                       COMMAND REFERENCE
# ============================================================================

### Analyze Latest Results
```bash
python analyze_benchmarks.py --analyze
```

### Show Scenario Analysis
```bash
python analyze_benchmarks.py --scenarios
```

### Generate Improvement Plan
```bash
python analyze_benchmarks.py --plan
```

### Full Analysis (Everything)
```bash
python analyze_benchmarks.py --full
```

### Analyze Specific File
```bash
python analyze_benchmarks.py --file data/benchmarks/benchmark_results_20240408_143000.json
```

### Save Analysis to File
```bash
python analyze_benchmarks.py --analyze --output my_analysis.json
```

---

# ============================================================================
#                    UNDERSTANDING THE OUTPUT
# ============================================================================

## Summary Section

```
Total Queries Tested: 12
Basic Pipeline Success Rate: 100.0%
Intelligent System Success Rate: 100.0%
Queries Underperforming: 1
Failure Cases: 0

Status: HEALTHY - Minor issues only
```

What it means:
- Both systems succeeded on all queries (good!)
- 1 query was slower in intelligent system (investigate)
- No API failures
- Overall: System is working, minor optimization opportunity

## Action Priority Section

```
FIX: 5 API call failures - blocking users
OPTIMIZE: 2 queries slower than baseline
REVIEW: Model selection strategy needs adjustment
```

What it means:
- Do this first: Fix the 5 failing queries
- Then: Speed up 2 slow queries
- Then: Improve how models are selected

## Worst Performing Queries

```
Query #3
  Issue Type: high_latency
  Latency: 2345ms
```

What it means:
- Query 3 took 2.3 seconds (very slow)
- This is the slowest query

## Underperformance Cases

```
Query #7: 1 issues
  • latency_regression
    Regression: 18.5% worse
```

What it means:
- Query 7 in intelligent system took 18.5% longer than baseline
- This is the main problem to fix

## Failure Analysis

```
API_CONNECTION_ERROR
  Occurrences: 2
  Percentage: 16.7%
  Possible Causes:
    • Network connectivity issue
    • Google API service temporarily unavailable
```

What it means:
- 2 queries failed with connection errors (out of 12 = 16.7%)
- Likely causes listed for investigation

## Root Cause Analysis

```
Poor Model Selection
  Frequency: 1 instances
  Impact: cost or latency
```

What it means:
- 1 query selected the wrong model
- This caused higher cost or latency

## Recommendations

```
[HIGH] 1. Poor Model Selection
   Affected: 1 queries
   Impact: 30-50% cost reduction per affected query
   Fixes:
      • Review model selection heuristics - consider size thresholds
      • Adjust quality thresholds - Pro may be selected unnecessarily
      • Enable learning system to build better decision rules
```

What it means:
- HIGH priority issue
- Affects 1 query
- Following 3 fixes will save 30-50% cost
- Do this fix soon

---

# ============================================================================
#                     SCENARIO ANALYSIS
# ============================================================================

The analyzer recognizes 3 common scenarios:

### Scenario 1: Query Faster & Cheaper
```
Status: SUCCESS - Working as intended
Reason: Model selection worked, possibly cache hit
Action: MONITOR - Track cache hit rate
```

**What to do:**
- No action needed
- This is the expected behavior
- Celebrate this case!

### Scenario 2: Query Slower, Better Quality
```
Status: ACCEPTABLE TRADEOFF
Reason: Selected Pro model for quality (legitimate choice)
Action: INVESTIGATE - Was quality improvement necessary?

Recommendations:
  • Check if quality threshold triggered Pro model unnecessarily
  • Verify quality evaluation cost
  • Consider: is 10-20% slower worth quality improvement?
```

**What to do:**
- Analyze if quality improvement was worth the tradeoff
- Decide: lower quality threshold? skip evaluation?
- Document the decision

### Scenario 3: Failed Cache, Fallback Used
```
Status: ACCEPTABLE - Fallback working
Reason: Cache key mismatch or cache miss (expected for new queries)
Action: ANALYZE - Is cache misses happening too often?

Recommendations:
  • Check cache hit rate across entire benchmark
  • Verify cache key generation logic
  • Clear cache if corrupted
  • Monitor cache size for limits
  • First query for content always misses - normal
```

**What to do:**
- Check cache hit rate in benchmark report
- If hit rate is low (< 20%), investigate cache issues
- If hit rate is normal (30%+), this is expected behavior

---

# ============================================================================
#                    ROOT CAUSE ANALYSIS
# ============================================================================

### Common Root Causes and How to Fix Them

#### 1. Poor Model Selection
**Problem:** Wrong model chosen for query

**Why it happens:**
- Heuristic (size-based) too simple
- Quality threshold triggered Pro unnecessarily
- Learning system hasn't built decision rules yet

**Fixes:**
```python
# Fix 1: Adjust quality threshold
intelligent_system = IntelligentLLMOrchestrator(
    quality_threshold=0.75  # Less strict
)

# Fix 2: Change size heuristic
# In model_selector.py:
PRO_MODEL_THRESHOLD = 3000  # chars (instead of 2000)

# Fix 3: Enable learning
learning_system.get_model_recommendation(query, priority="cost")
```

**Expected impact:** 30-50% cost reduction


#### 2. Cache Inefficiency
**Problem:** Cache not providing expected speedup

**Why it happens:**
- Cache keys don't match identical queries
- Cache expired too quickly (low TTL)
- Cache disabled in configuration
- Cache file corrupted

**Fixes:**
```bash
# Fix 1: Clear corrupted cache
rm -r data/cache/*

# Fix 2: Verify cache enabled
# In intelligent_orchestrator.py:
cache_enabled=True

# Fix 3: Increase TTL
cache_ttl_hours = 24  # (instead of 1)

# Fix 4: Debug cache keys
orchestrator.cache_manager.debug_keys()
```

**Expected impact:** 50-100x speedup on cached queries


#### 3. Orchestration Overhead
**Problem:** Intelligent system adds latency

**Why it happens:**
- Quality evaluation too expensive
- Metric collection slow
- Model selection calculation expensive

**Fixes:**
```python
# Fix 1: Skip evaluation for simple queries
if len(query) < 500:
    enable_evaluation = False

# Fix 2: Use faster evaluation model
quality_model = "gemini-2.5-flash"  # instead of pro

# Fix 3: Cache evaluation results
evaluation_cache_enabled = True
```

**Expected impact:** 10-20% latency reduction


#### 4. Quality Evaluation Cost
**Problem:** Quality evaluation adds significant time/cost

**Why it happens:**
- Evaluating every response
- Using expensive Pro model for evaluation
- Evaluation logic inefficient

**Fixes:**
```python
# Fix 1: Skip evaluation sometimes
evaluation_frequency = 0.5  # Only eval 50% of time

# Fix 2: Use cheaper evaluation
use_pro_for_evaluation = False

# Fix 3: Reduce evaluation dimensions
evaluation_dimensions = ["completeness", "accuracy"]  # Skip "relevance"
```

**Expected impact:** 20-30% latency reduction


#### 5. API Reliability
**Problem:** API calls failing or timing out

**Why it happens:**
- Rate limiting / quota exhausted
- API service down temporarily
- Network issues
- Invalid credentials

**Fixes:**
```python
# Fix 1: Check API status
https://status.cloud.google.com/

# Fix 2: Verify credentials
echo $GOOGLE_API_KEY

# Fix 3: Add retry logic
max_retries = 3
backoff_factor = 2.0

# Fix 4: Monitor quota
gcloud quota-metrics list
```

**Expected impact:** Recovery of 100% of failed queries


#### 6. Budget Limits
**Problem:** Some queries rejected for cost

**Why it happens:**
- Daily/monthly budget exceeded
- Unexpected expensive operation
- Cost calculation error

**Fixes:**
```python
# Fix 1: Increase budget
daily_budget_usd = 20.0  # (instead of 10.0)

# Fix 2: Use cheaper model exclusively
priority = "cost"  # Forces Flash model

# Fix 3: Enable caching
cache_enabled = True

# Fix 4: Add budget alerts
alert_at_percentage = 80.0  # Warn at 80% used
```

**Expected impact:** Serve 100% of user requests

---

# ============================================================================
#                      WORKFLOW: ANALYZE → FIX → VERIFY
# ============================================================================

### Step 1: Analyze Results
```bash
python analyze_benchmarks.py --full
```
Output: List of issues with recommendations

### Step 2: Prioritize Issues
Issues are prioritized:
- CRITICAL: Do first, blocks users
- HIGH: Do ASAP, significant impact
- MEDIUM: Do this week
- LOW: Nice to have

### Step 3: Implement Fixes
For each issue:
1. Read the "Fixes" section
2. Understand the root cause
3. Implement fix (usually 1-5 line code change)
4. Test with quick benchmark

### Step 4: Verify Fix Works
```bash
# Quick retest
python benchmark_runner.py --quick

# Check if issue improved
python analyze_benchmarks.py --analyze
```

### Step 5: Repeat
Go to Step 2 until all issues resolved

---

# ============================================================================
#                     SAMPLE WORKFLOW
# ============================================================================

### Initial Analysis Output
```
Queries Underperforming: 3
Failure Cases: 1

[CRITICAL] API Reliability Issues - 1 affected
[HIGH] Poor Model Selection - 3 affected
[MEDIUM] Cache Inefficiency - 1 affected
```

### Fix 1: API Reliability (CRITICAL)
```bash
# Check API status - seems OK
# Verify credentials - also OK
# Look at error details
python analyze_benchmarks.py --analyze > analysis.txt
# See: "timeout" error

# Add retry logic to intelligent_orchestrator.py
max_retries = 3
backoff_factor = 2.0

# Retest
python benchmark_runner.py --quick
# ✓ No more failures!
```

### Fix 2: Model Selection (HIGH)
```bash
# Analysis shows: "expensive_model_selection"
# Pro model chosen unnecessarily

# In model_selector.py:
PRO_MODEL_THRESHOLD = 3000  # increased from 2000

# In intelligent_orchestrator.py:
quality_threshold = 0.75  # lowered from 0.8

# Retest
python benchmark_runner.py --quick
# Latency improved! But still one slow query...
```

### Fix 3: Cache Inefficiency (MEDIUM)
```bash
# Analysis shows: cache hit rate = 0%

# Clear cache
rm -r data/cache/*

# Run test again to rebuild cache
python benchmark_runner.py --quick
# Cache hit: 0% (first run, expected)

# Run test again
python benchmark_runner.py --quick
# Cache hit: 67%! (works now)

# ✓ All issues fixed!
```

### Final Verification
```bash
python analyze_benchmarks.py --full

# Output shows:
# Status: HEALTHY - No significant issues
# ✓ All benchmarks passing
# ✓ No failures
# ✓ Performance acceptable
```

---

# ============================================================================
#                    OUTPUT FILES GENERATED
# ============================================================================

### After Running Analysis

1. **analysis_YYYYMMDD_HHMMSS.json**
   - Full analysis in JSON format
   - Loadable for programmatic access
   - Contains all issues and recommendations

2. **failure_report_YYYYMMDD_HHMMSS.json**
   - Detailed failure report
   - Worst performers listed
   - Underperformance cases detailed
   - All recommendations included

3. **Console Output**
   - Human-readable analysis
   - Formatted tables
   - Clear priorities
   - Easy to share

---

# ============================================================================
#                    ADVANCED: CUSTOM ANALYSIS
# ============================================================================

### Add Custom Analysis Logic

In benchmark_analyzer.py, add to _identify_root_causes():

```python
# Custom root cause
if specific_condition:
    root_causes["my_custom_issue"] = {
        "description": "My custom issue",
        "cases": [],
        "frequency": 0,
        "impact": "describes impact"
    }
```

### Add Custom Recommendations

In benchmark_analyzer.py, add to _generate_recommendations():

```python
if cause_name == "my_custom_issue":
    recommendations.append({
        "issue": "My Custom Issue",
        "priority": "HIGH",
        "fixes": [
            "Fix step 1",
            "Fix step 2",
            "Fix step 3"
        ],
        "estimated_impact": "X% improvement"
    })
```

---

# ============================================================================
#                    TROUBLESHOOTING
# ============================================================================

### Q: "No benchmark results found"
A: Run benchmarks first
   ```bash
   python benchmark_runner.py --quick
   ```

### Q: "All queries show as failures"
A: Likely API key issue
   ```bash
   python -c "from config import Config; print(Config.GOOGLE_API_KEY)"
   ```

### Q: "Analysis looks wrong"
A: Clear cache and rerun
   ```bash
   rm -r data/cache/*
   python benchmark_runner.py --quick
   python analyze_benchmarks.py --analyze
   ```

### Q: "Can't find latest files"
A: Manually specify file path
   ```bash
   python analyze_benchmarks.py --file path/to/file.json
   ```

### Q: "Want to compare multiple runs"
A: Save analysis from each run
   ```bash
   python analyze_benchmarks.py --analyze --output run1_analysis.json
   python analyze_benchmarks.py --file old_results.json --output run2_analysis.json
   # Then compare JSON files
   ```

---

# ============================================================================
#                    REAL EXAMPLE: THREE SCENARIOS
# ============================================================================

## Scenario from User: Query Results

### Query 1: Faster, Cheaper ✓
```json
{
  "query_id": 1,
  "basic_latency_ms": 1243,
  "intelligent_latency_ms": 892,
  "speedup": 1.39,
  "cost_savings_pct": 30.8,
  "cache_used": false,
  "analysis": "SUCCESS - Working as intended"
}
```

**Analysis Output:**
- Status: "Query 1 - Good performance"
- Action: "MONITOR - Track this pattern"
- This is the expected behavior!

### Query 2: Slower, Better Quality
```json
{
  "query_id": 2,
  "basic_latency_ms": 1156,
  "intelligent_latency_ms": 1450,  // Slower
  "model_selected": "gemini-2.5-pro",  // Expensive model
  "quality_score": 92,  // But better quality!
  "latency_regression_pct": 25.4,
  "analysis": "TRADEOFF - Quality vs Speed"
}
```

**Analysis Output:**
- Issue: "Expensive model selection"
- Root Cause: "Pro model chosen for quality"
- Recommendation: "Lower quality threshold if unnecessary"
- Fix:
  ```python
  quality_threshold = 0.75  # was 0.90
  ```

### Query 3: Cache Failed, Fallback
```json
{
  "query_id": 3,
  "cache_attempt": "failed",
  "fallback_method": "api_call",
  "basic_latency_ms": 823,
  "intelligent_latency_ms": 890,  // Slightly slower (API call + overhead)
  "analysis": "ACCEPTABLE - Fallback working"
}
```

**Analysis Output:**
- Status: "Cache miss (first query for this content - normal)"
- Action: "Monitor cache hit rate trends"
- Expected: Future runs of Query 3 will be cached
- On next run:
  ```
  Cache hit: YES
  Latency: 22ms (instead of 890ms)
  Cost: $0.00 (cached, free!)
  ```

---

# ============================================================================
#                    SUMMARY
# ============================================================================

The Benchmark Analyzer provides:

✅ **Identification** - Finds worst performers and failures
✅ **Analysis** - Root cause analysis for each issue
✅ **Prioritization** - CRITICAL/HIGH/MEDIUM/LOW rankings
✅ **Solutions** - Specific fixes with expected impact
✅ **Reporting** - JSON and console outputs
✅ **Workflow** - Analyze → Fix → Verify loop

**Workflow:**
1. Run: `python benchmark_runner.py --quick`
2. Analyze: `python analyze_benchmarks.py --full`
3. Fix: Implement recommendations
4. Verify: Rerun benchmarks to confirm improvements
5. Repeat: Until all issues resolved

**Key Command:**
```bash
python analyze_benchmarks.py --full
```

This single command generates:
- Worst performers list
- Underperformance analysis
- Failure categorization
- Root cause identification
- Prioritized recommendations
- Improvement plan
- JSON export for further analysis

**You now have a complete system to:**
- Identify when system underperforms
- Understand why it's failing
- Get specific actionable fixes
- Verify improvements

🎯 Ready to analyze your benchmarks!
