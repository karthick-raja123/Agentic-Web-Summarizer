# 📊 Metrics Quick Reference

## Dashboard Metrics Cheat Sheet

### Summary Statistics (Top Row)

| Metric | Range | Good | Fair | Poor |
|--------|-------|------|------|------|
| **Success Rate** | 0-100% | >90% | 70-90% | <70% |
| **Quality Score** | 0.0-1.0 | >0.7 | 0.5-0.7 | <0.5 |
| **Avg Latency** | seconds | <5s | 5-15s | >15s |
| **Total Requests** | count | N/A | Increases | Stalls |

### Latency Breakdown

| Stage | Typical | Fast | Slow | Issue |
|-------|---------|------|------|-------|
| **Search** | 2-3s | <2s | >4s | Network/API |
| **Scrape** | 1-2s | <1s | >3s | Large content |
| **Rank** | 0.5-1s | <0.5s | >2s | Many sources |
| **Deduplicate** | 0.3-0.5s | <0.3s | >1s | Duplicate content |
| **Summarize** | 2-4s | <2s | >5s | Model/Network |
| **Reflection** | 0.2-0.5s | <0.2s | >1s | N/A |
| **TOTAL** | 6-12s | <8s | >15s | Investigate stages |

### Token Usage

| Metric | Low | Medium | High | Very High |
|--------|-----|--------|------|-----------|
| **Input Tokens** | <200 | 200-500 | 500-1000 | >1000 |
| **Output Tokens** | <150 | 150-400 | 400-800 | >800 |
| **Content Tokens** | <1000 | 1000-2500 | 2500-5000 | >5000 |
| **Total Tokens** | <500 | 500-1500 | 1500-3000 | >3000 |

### Cost Estimation

| Range | Per Request | Per 100 | Per 1000 |
|-------|-------------|---------|----------|
| **Low (<500 tokens)** | ~$0.020 | ~$2.00 | ~$20 |
| **Medium (500-1500)** | ~$0.045 | ~$4.50 | ~$45 |
| **High (1500-3000)** | ~$0.090 | ~$9.00 | ~$90 |
| **Very High (>3000)** | ~$0.150 | ~$15.00 | ~$150 |

### Quality Metrics

#### Quality Score Interpretation
```
0.9-1.0  ⭐⭐⭐⭐⭐ Excellent - Perfect summary
0.8-0.9  ⭐⭐⭐⭐  Very Good - Highly accurate
0.7-0.8  ⭐⭐⭐    Good - Satisfactory
0.6-0.7  ⭐⭐     Fair - Acceptable
0.5-0.6  ⭐      Poor - May have issues
<0.5     ✗      Failed - Problematic
```

#### Success Rate Status
```
95-100%  ✅ Excellent   - System is stable
90-95%   ✅ Good        - Minor issues
80-90%   ⚠️  Fair       - Investigate failures
70-80%   ⚠️  Poor       - Many issues
<70%     ❌ Broken      - Critical problems
```

## Request Distribution

### By Type (Web Query vs PDF)
- **Web Queries**: Typically faster, 50-75% of requests
- **PDF Upload**: Typically slower, 25-50% of requests
- **Expected Ratio**: Depends on use case

### By Status
- **Success**: Should be >95%
- **Failed**: Any failures should be investigated
- **Timeout**: Indicates system overload or network issues

## Performance Zones

### Latency Zones
```
0-5s    🟢 GREEN  - Excellent performance
5-10s   🟡 YELLOW - Acceptable but room for improvement
10-15s  🟠 ORANGE - Investigate bottlenecks
>15s    🔴 RED    - Critical review needed
```

### Quality Zones
```
0.8-1.0 🟢 GREEN  - High quality
0.6-0.8 🟡 YELLOW - Acceptable quality
0.4-0.6 🟠 ORANGE - Low quality, improve sources
<0.4    🔴 RED    - Poor quality, check inputs
```

### Success Rate Zones
```
95-100% 🟢 GREEN  - Highly reliable
90-95%  🟡 YELLOW - Normal variations
80-90%  🟠 ORANGE - Needs attention
<80%    🔴 RED    - Serious issues
```

## Common Issues & Solutions

### High Latency (>15s)
1. Check Search time
   - If high: Network/API issues
   - Solution: Check internet, try simpler query
   
2. Check Scrape time
   - If high: Large content
   - Solution: Reduce sources, limit content size
   
3. Check Summarize time
   - If high: Model overload
   - Solution: Reduce iterations, try again later

### Low Quality (<0.6)
1. Check sources_used
   - If low (<3): Insufficient sources
   - Solution: Try broader query, more iterations
   
2. Check query complexity
   - If complex: Vague question
   - Solution: Clarify query, be more specific
   
3. Check sources_used vs reflections
   - If failing: Low quality sources
   - Solution: Adjust quality_threshold

### High Token Usage
1. Reduce input size
   - Solution: Limit PDF pages, shorter queries
   
2. Reduce output verbosity
   - Solution: Shorter summaries, fewer bullets
   
3. Reduce content
   - Solution: Lower max_iterations, fewer sources

### Failed Requests
1. Check error message
   - Network: Retry, check connection
   - Timeout: Reduce complexity, retry
   - Other: Check API logs

## Optimization Tips

### To Improve Speed
- ⬇️ Reduce max_iterations (1 instead of 3)
- ⬇️ Increase quality_threshold (0.8 instead of 0.6)
- ⬇️ Use Web Query instead of PDF (when possible)
- ✅ Batch similar queries

### To Improve Quality
- ⬆️ Increase max_iterations (3 instead of 1)
- ⬇️ Decrease quality_threshold (0.5 instead of 0.6)
- ✅ Be more specific in queries
- ✅ Check source diversity

### To Reduce Costs
- ⬇️ Shorten summaries
- ⬇️ Reduce output tokens
- ⬇️ Lower max_iterations
- ✅ Combine similar queries

### To Improve Reliability
- ✅ Monitor failures
- ✅ Retry timeouts
- ✅ Check network stability
- ✅ Validate API health

## Metric Collection Settings

### Automatic Features
- ✅ All requests tracked
- ✅ Metrics persisted to disk
- ✅ Historical data retained
- ✅ Auto-aggregated by period
- ✅ Cost calculated automatically

### What's Tracked
- Request ID (for audit trail)
- Timestamp (when it happened)
- Query (what was asked)
- Request type (web/pdf)
- All latencies (breakdown)
- All tokens (complete count)
- Quality score
- Success/failure status

## Export & Analysis

### Export Formats
- **JSON**: Full data with all metrics
- **CSV**: Tabular format for spreadsheets
- **txt**: Human-readable summary

### Analysis Ideas
- Compare 1h vs 24h trends
- Calculate cost per request
- Track quality improvements
- Identify peak usage times
- Find common failure patterns

## Monitoring Best Practices

1. **Daily Check**
   - Success rate >90%?
   - Quality score >0.7?
   - Latency acceptable?

2. **Weekly Review**
   - Trends improving?
   - Costs stable?
   - Any recurring issues?

3. **Monthly Planning**
   - Plan optimizations
   - Budget for API costs
   - Capacity planning

## API Response Field Guide

### latency_metrics
```json
{
  "search_time": float,        // Web search duration
  "scrape_time": float,        // Content extraction
  "rank_time": float,          // Content ranking
  "summarize_time": float,     // Summarization
  "reflection_time": float,    // Quality check
  "total_time": float          // End-to-end
}
```

### token_metrics
```json
{
  "input_tokens": int,         // Query tokens
  "output_tokens": int,        // Summary tokens
  "search_query_tokens": int,  // Expansion tokens
  "content_tokens": int,       // Scraped content tokens
  "total_tokens": int,         // Complete count
  "estimated_cost": float      // USD estimate
}
```

### Quality Indicators
```json
{
  "quality_score": float,      // 0.0-1.0
  "sources_used": int,         // Number sources
  "processing_time": float,    // Seconds
  "status": string             // success/failed
}
```

---

## Dashboard Navigation

### Time Periods
- **1h**: Recent activity, fine detail
- **6h**: Trend patterns
- **24h**: Full day performance

### Refresh Data
- Manual: Click "🔄 Refresh Metrics"
- Auto: Page refreshes every 30s (when open)

### Export Metrics
- Scroll to bottom of dashboard
- Select export format
- Download file automatically

---

## Benchmarks to Aim For

### Ideal Performance (24h)
- Success Rate: 95-99%
- Avg Latency: 6-10s
- Avg Quality: 0.80+
- Cost: $0.03-0.05 per request

### Good Performance
- Success Rate: 90-95%
- Avg Latency: 8-12s
- Avg Quality: 0.75-0.80
- Cost: $0.04-0.06 per request

### Needs Improvement
- Success Rate: <90%
- Avg Latency: >12s
- Avg Quality: <0.75
- Cost: >$0.06 per request

---

**Last Updated:** 2024
**For detailed docs:** See METRICS_DASHBOARD.md

