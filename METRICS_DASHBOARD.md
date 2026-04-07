# 📊 Metrics Dashboard - QuickGlance

## Overview

The QuickGlance metrics system provides comprehensive performance tracking and analytics for AI-powered summarization operations. It monitors latency, token usage, and success rates across your entire summarization pipeline.

## Features

### 1. **Latency Tracking** ⏱️
Measures the time spent at each stage of the summarization pipeline:

- **Search Time**: Web search query expansion and execution
- **Scrape Time**: Content extraction from web pages
- **Rank Time**: Content ranking and relevance scoring
- **Deduplicate Time**: Duplicate content removal
- **Summarize Time**: AI summarization generation
- **Reflection Time**: Quality assessment and reflection
- **Total Time**: End-to-end request duration

**Use Case**: Identify bottlenecks and optimize pipeline performance.

### 2. **Token Usage Estimation** 🔤
Tracks and estimates API token consumption:

- **Input Tokens**: Tokens from user queries and expanded searches
- **Output Tokens**: Tokens from generated summaries and bullet points
- **Search Query Tokens**: Tokens used for query expansion
- **Content Tokens**: Tokens from scraped web content
- **Total Tokens**: Complete token count for the request
- **Estimated Cost**: Approximate API cost (based on GPT-4 pricing)

**Use Case**: Monitor API costs and optimize token usage.

### 3. **Success Rate Tracking** ✅
Measures reliability and quality metrics:

- **Total Requests**: Complete request count in time period
- **Success Rate**: % of requests that completed successfully
- **Quality Pass Rate**: % of requests meeting quality threshold (>0.6)
- **Failed Requests**: Count of failed/errored requests
- **Timeout Requests**: Count of requests that exceeded time limits

**Use Case**: Ensure system reliability and identify recurring issues.

## How to Access Metrics

### **Via API Endpoint**

```bash
# Get metrics for last 24 hours
curl http://localhost:8000/metrics?hours=24

# Get metrics for last 6 hours
curl http://localhost:8000/metrics?hours=6

# Get metrics for last 1 hour
curl http://localhost:8000/metrics?hours=1
```

### **Via Streamlit UI**

1. Open the app and navigate to the **📊 Metrics** tab
2. Select time period (1h, 6h, or 24h)
3. Click **🔄 Refresh Metrics** to update data
4. View comprehensive dashboard with all metrics

### **Per-Request Metrics**

Each summarization response includes detailed metrics:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "latency_metrics": {
    "search_time": 2.5,
    "scrape_time": 1.3,
    "summarize_time": 3.2,
    "total_time": 7.0
  },
  "token_metrics": {
    "input_tokens": 450,
    "output_tokens": 280,
    "total_tokens": 730,
    "estimated_cost": 0.0285
  },
  "quality_score": 0.85,
  "sources_used": 5,
  "processing_time": 7.0
}
```

## Metrics Dashboard Layout

### **Summary Statistics**
- Total Requests
- Success Rate
- Average Quality Score
- Average Latency

### **Latency Breakdown**
- Search, Scrape, Summarize, Median times
- Helps identify performance bottlenecks

### **Token Usage**
- Average tokens per request
- Total tokens used in period
- Estimated cost for period

### **Request Distribution**
- By Type (web vs PDF)
- By Status (success vs failed)

## Interpreting Metrics

### Quality Score
- **> 0.7**: ✅ Excellent - Content well-summarized
- **0.5 - 0.7**: ⚠️ Good - Acceptable quality
- **< 0.5**: ❌ Fair - May need improvement

### Success Rate
- **> 90%**: ✅ Excellent reliability
- **70-90%**: ⚠️ Good reliability
- **< 70%**: ❌ Needs investigation

### Latency Performance
- **< 5 seconds**: ✅ Excellent
- **5-15 seconds**: ⚠️ Acceptable
- **> 15 seconds**: ❌ Consider optimization

### Token Efficiency
- Average tokens = `input_tokens + output_tokens`
- Cost estimate = `(input_tokens * $0.00003) + (output_tokens * $0.00006)`
- Trends over time help identify efficiency patterns

## Storage and Persistence

Metrics are stored in `metrics_data.json` with:
- All individual request metrics
- Aggregate statistics
- Historical data (persisted across restarts)

Load historical metrics automatically on startup.

## API Endpoints

### **GET /metrics**
Returns aggregated metrics for specified time period.

**Parameters:**
- `hours` (int, default: 24) - Time period in hours

**Response:**
```json
{
  "period_hours": 24,
  "total_requests": 42,
  "success_rate": 95.2,
  "avg_latency_seconds": 8.3,
  "median_latency_seconds": 7.5,
  "avg_search_time": 2.1,
  "avg_scrape_time": 1.5,
  "avg_summarize_time": 3.2,
  "avg_tokens": 650,
  "total_tokens": 27300,
  "avg_quality_score": 0.82,
  "request_types": {"web": 25, "pdf": 17},
  "status_distribution": {"success": 40, "failed": 2}
}
```

## Integration Examples

### **Python Client**
```python
import requests

# Fetch metrics
response = requests.get('http://localhost:8000/metrics', params={'hours': 24})
metrics = response.json()

print(f"Success Rate: {metrics['success_rate']:.1f}%")
print(f"Avg Latency: {metrics['avg_latency_seconds']:.1f}s")
print(f"Total Tokens: {metrics['total_tokens']:,}")
```

### **Track Individual Requests**
```python
# From summarization response
response = requests.post('http://localhost:8000/summarize', json={
    'query': 'What is AI?'
})
data = response.json()

print(f"Request ID: {data['request_id']}")
print(f"Processing Time: {data['processing_time']:.1f}s")
print(f"Token Usage: {data['token_metrics']['total_tokens']}")
```

## Best Practices

1. **Monitor Regularly**
   - Check metrics dashboard daily
   - Set up alerts for low success rates
   - Track trends over time

2. **Optimize Performance**
   - Identify latency bottlenecks
   - Reduce token usage where possible
   - Set max_iterations based on quality needs

3. **Cost Management**
   - Monitor estimated costs
   - Batch similar queries
   - Adjust quality thresholds as needed

4. **Quality Assurance**
   - Track quality scores
   - Investigate failed requests
   - Archive high-quality results

## Troubleshooting

### No Metrics Available
- **Cause**: No summarization requests completed yet
- **Solution**: Run some summarizations first

### Low Quality Scores
- **Cause**: Poor query or insufficient sources
- **Solution**: Try expanded queries or adjust max_iterations

### High Latency
- **Cause**: Network issues or large content
- **Solution**: Check network, reduce sources, profile stages

### High Token Usage
- **Cause**: Large input or verbose output
- **Solution**: Limit content size, summarize more aggressively

## Advanced Usage

### Export Metrics

Metrics can be exported to JSON for analysis:
```python
from metrics import get_metrics_collector

collector = get_metrics_collector()
collector.export_metrics('metrics_export.json')
```

### Custom Queries

Access metrics programmatically:
```python
# Get last 24 hours summary
summary = collector.get_performance_summary(hours=24)

# Get recent metrics
recent = collector.get_recent_metrics(hours=6)

# Get specific request
request_metrics = collector.get_metrics('request_id_here')
```

## Performance Benchmarks

### Typical Performance (24h Average)
- **Avg Latency**: 6-10 seconds
- **Success Rate**: 95%+
- **Avg Quality**: 0.80+
- **Tokens/Request**: 600-800

### Cost Estimation
- Per request: ~$0.025-0.040
- Per 100 requests: ~$2.50-4.00
- Per 1000 requests: ~$25-40

## Roadmap

Planned metrics enhancements:
- [ ] Custom metric views
- [ ] Automated alerts and notifications
- [ ] Performance recommendations
- [ ] Detailed cost breakdown by module
- [ ] Machine learning performance optimization suggestions
- [ ] Real-time monitoring dashboard
- [ ] Metric export to external services

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review metrics data in `metrics_data.json`
3. Enable debug logging for detailed traces
4. Contact support with request IDs

