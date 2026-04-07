# 🌐 API Reference - QuickGlance Multi-Agent Pipeline

## Overview

The FastAPI server exposes RESTful endpoints for the QuickGlance multi-agent research pipeline.

**Base URL:** `https://your-api-url.com` or `http://localhost:8000`

**Authentication:** Not required (can be added via middleware)

**Rate Limiting:** Recommended 100 req/min per IP (not enforced by default)

---

## 📡 Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Monitor API status and health

**Status Codes:**
- `200` - API healthy and ready
- `503` - Service unavailable

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 3600
}
```

**Example:**
```bash
curl https://your-api-url.com/health
```

---

### 2. Main Query Endpoint

**Endpoint:** `POST /api/query`

**Purpose:** Execute multi-agent research query

**Request Body:**
```json
{
  "query": "What is artificial intelligence and its applications?",
  "timeout": 30,
  "enable_evaluation": true,
  "enable_formatting": true,
  "max_sources": 5
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query |
| `timeout` | integer | ❌ No | 30 | Seconds to wait |
| `enable_evaluation` | boolean | ❌ No | true | Run quality evaluation |
| `enable_formatting` | boolean | ❌ No | true | Format output |
| `max_sources` | integer | ❌ No | 5 | Number of sources to return |

**Response (200 OK):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "query": "What is artificial intelligence?",
  "results": {
    "summary": "Artificial intelligence refers to computer systems designed to perform tasks...",
    "sources": [
      {
        "title": "Introduction to AI",
        "url": "https://example.com/ai-intro",
        "snippet": "AI is a branch of computer science..."
      }
    ],
    "evaluation": {
      "quality_score": 0.92,
      "relevance_score": 0.88,
      "credibility": "high"
    }
  },
  "metadata": {
    "processing_time_seconds": 4.2,
    "sources_found": 5,
    "model_used": "gemini-pro"
  }
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "detail": "Query cannot be empty"
}
```

**408 Request Timeout:**
```json
{
  "detail": "Processing timeout after 30 seconds"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating response: API key invalid"
}
```

**Examples:**

Simple query:
```bash
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI breakthroughs 2024"}'
```

With options:
```bash
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change solutions",
    "timeout": 60,
    "max_sources": 10,
    "enable_evaluation": true
  }'
```

---

### 3. Batch Query Endpoint

**Endpoint:** `POST /api/batch`

**Purpose:** Process multiple queries efficiently

**Request Body:**
```json
{
  "queries": [
    "What is machine learning?",
    "Difference between AI and ML",
    "Deep learning applications"
  ],
  "timeout": 60,
  "parallel": true
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `queries` | array | ✅ Yes | - | List of queries |
| `timeout` | integer | ❌ No | 60 | Seconds per query |
| `parallel` | boolean | ❌ No | true | Process in parallel |

**Response (200 OK):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "batch_size": 3,
  "results": [
    {
      "query": "What is machine learning?",
      "summary": "Machine learning is a subset of AI...",
      "status": "success"
    },
    {
      "query": "Difference between AI and ML",
      "summary": "AI is broader than ML...",
      "status": "success"
    },
    {
      "query": "Deep learning applications",
      "summary": "Deep learning powers modern AI...",
      "status": "success"
    }
  ],
  "metadata": {
    "total_processing_time": 12.5,
    "successful": 3,
    "failed": 0
  }
}
```

**Example:**
```bash
curl -X POST https://your-api-url.com/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What is blockchain?",
      "How does cryptocurrency work?",
      "NFT use cases"
    ],
    "parallel": true,
    "timeout": 45
  }'
```

---

### 4. Query Status Endpoint

**Endpoint:** `GET /api/status/{request_id}`

**Purpose:** Check status of a previous query

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| `request_id` | string | URL path | UUID from query response |

**Response (200 OK):**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "query": "What is AI?",
  "completion_time": "2024-01-15T10:35:00Z",
  "results": {
    "summary": "...",
    "sources": [...]
  }
}
```

**Status Values:**
- `pending` - Processing
- `completed` - Done
- `failed` - Error occurred
- `timeout` - Exceeded timeout

**Example:**
```bash
curl https://your-api-url.com/api/status/550e8400-e29b-41d4-a716-446655440000
```

---

### 5. API Capabilities Endpoint

**Endpoint:** `GET /api/capabilities`

**Purpose:** Discover available features and models

**Response (200 OK):**
```json
{
  "version": "1.0.0",
  "models": [
    "gemini-pro",
    "gpt-4-turbo",
    "claude-3"
  ],
  "features": {
    "evaluation": true,
    "formatting": true,
    "summarization": true,
    "source_ranking": true,
    "real_time_search": true
  },
  "limits": {
    "max_query_length": 2000,
    "max_batch_size": 50,
    "max_timeout": 300,
    "max_sources": 20
  },
  "endpoints": [
    "/api/query",
    "/api/batch",
    "/api/status/{request_id}",
    "/api/capabilities"
  ]
}
```

**Example:**
```bash
curl https://your-api-url.com/api/capabilities
```

---

### 6. Root Endpoint

**Endpoint:** `GET /`

**Purpose:** API documentation and links

**Response (200 OK):**
```json
{
  "name": "QuickGlance Multi-Agent Pipeline API",
  "version": "1.0.0",
  "description": "Intelligent web research using multi-agent architecture",
  "docs": "https://your-api-url.com/docs",
  "redoc": "https://your-api-url.com/redoc",
  "endpoints": {
    "documentation": "/docs",
    "alternative_docs": "/redoc",
    "health": "/health",
    "query": "/api/query",
    "batch": "/api/batch",
    "status": "/api/status/{request_id}",
    "capabilities": "/api/capabilities"
  }
}
```

---

## Response Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid parameters |
| `408` | Timeout | Query took too long |
| `422` | Validation Error | Invalid request format |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Internal error |
| `503` | Service Unavailable | Server down |

---

## Request Examples by Language

### Python (requests)

```python
import requests
import json

API_URL = "https://your-api-url.com"

# Single query
response = requests.post(
    f"{API_URL}/api/query",
    json={
        "query": "What is machine learning?",
        "timeout": 30
    }
)
print(response.json())

# Batch queries
response = requests.post(
    f"{API_URL}/api/batch",
    json={
        "queries": [
            "Query 1",
            "Query 2",
            "Query 3"
        ]
    }
)
print(response.json())

# Check status
response = requests.get(
    f"{API_URL}/api/status/request-id-here"
)
print(response.json())
```

### JavaScript/Node.js

```javascript
const API_URL = 'https://your-api-url.com';

// Single query
async function query() {
  const response = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: 'What is machine learning?',
      timeout: 30
    })
  });
  const data = await response.json();
  console.log(data);
}

// Batch queries
async function batchQuery() {
  const response = await fetch(`${API_URL}/api/batch`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      queries: ['Query 1', 'Query 2', 'Query 3']
    })
  });
  const data = await response.json();
  console.log(data);
}

// Check status
async function checkStatus(requestId) {
  const response = await fetch(`${API_URL}/api/status/${requestId}`);
  const data = await response.json();
  console.log(data);
}
```

### cURL

```bash
# Health check
curl https://your-api-url.com/health

# Single query
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question here?"}'

# Batch queries
curl -X POST https://your-api-url.com/api/batch \
  -H "Content-Type: application/json" \
  -d '{"queries": ["Q1", "Q2", "Q3"]}'

# Check status
curl https://your-api-url.com/api/status/request-id
```

---

## Authentication (Optional)

To add API key authentication:

**Request with API Key:**
```bash
curl -X POST https://your-api-url.com/api/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"query": "Your question?"}'
```

(Requires backend modification to implement)

---

## Rate Limiting (Optional)

Recommended implementation:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/query")
@limiter.limit("100/minute")
async def query(request: QueryRequest):
    # ...
```

---

## Error Handling

Common errors and solutions:

**"Query cannot be empty"**
```json
{"detail": "Query cannot be empty"}
```
*Solution:* Provide a non-empty `query` string

**"Processing timeout"**
```json
{"detail": "Processing timeout after 30 seconds"}
```
*Solution:* Increase `timeout` parameter or simplify query

**"API key invalid"**
```json
{"detail": "Error generating response: API key invalid"}
```
*Solution:* Check GOOGLE_API_KEY and SERPER_API_KEY

**"Rate limit exceeded"**
```json
{"detail": "Rate limit exceeded: 100 requests per minute"}
```
*Solution:* Wait before making more requests

---

## Testing Tools

### Postman

1. Import via URL:
   ```
   https://your-api-url.com/openapi.json
   ```

2. Or create manually in Postman:
   - Method: POST
   - URL: `https://your-api-url.com/api/query`
   - Body: JSON with query

### Swagger UI

Visit: `https://your-api-url.com/docs`

### FastAPI ReDoc

Visit: `https://your-api-url.com/redoc`

---

## WebSocket Support (Optional)

For real-time streaming results:

```python
@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        # Stream results
        yield partial results...
    except Exception as e:
        await websocket.send_json({"error": str(e)})
```

---

## Response Time Benchmarks

Typical response times from high-quality internet:

| Query Type | Time | Notes |
|-----------|------|-------|
| Simple (< 50 chars) | 2-4s | Quick lookup |
| Medium (50-200 chars) | 4-8s | Moderate processing |
| Complex (> 200 chars) | 8-15s | Requires analysis |
| Batch (3 queries) | 12-20s | Parallel processing |

---

## API Documentation Available At

- **Swagger/OpenAPI**: `https://your-api-url.com/docs`
- **ReDoc**: `https://your-api-url.com/redoc`
- **OpenAPI JSON**: `https://your-api-url.com/openapi.json`

---

## Support

For issues:
1. Check API `/health` endpoint
2. Review logs on deployment platform
3. Test query parameters in `/api/capabilities`
4. Check error responses for details

---

**API Version:** 1.0.0  
**Last Updated:** January 2024
