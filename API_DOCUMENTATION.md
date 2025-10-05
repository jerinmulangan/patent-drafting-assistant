# Patent NLP API Documentation

## Overview

The Patent NLP API provides advanced patent search and analysis capabilities with semantic search, re-ranking, summarization, and batch processing. The API is built with FastAPI and provides both REST endpoints and interactive documentation.

## Quick Start

### 1. Start the API Server

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### 2. Test the API

```bash
# Run the test suite
python test_api.py
```

## API Endpoints

### Search Endpoint

**POST** `/api/v1/search`

Search patents using various modes with advanced features.

#### Request Body

```json
{
  "query": "machine learning",
  "mode": "semantic",
  "top_k": 5,
  "alpha": 0.5,
  "tfidf_weight": 0.3,
  "semantic_weight": 0.7,
  "rerank": true,
  "include_snippets": true,
  "include_metadata": true,
  "log_enabled": false
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | Search query text |
| `mode` | string | `"semantic"` | Search mode: `"tfidf"`, `"semantic"`, `"hybrid"`, `"hybrid-advanced"` |
| `top_k` | integer | `5` | Number of results to return (1-100) |
| `alpha` | float | `0.5` | Weight for semantic search in hybrid mode (0.0-1.0) |
| `tfidf_weight` | float | `0.3` | TF-IDF weight for advanced hybrid mode |
| `semantic_weight` | float | `0.7` | Semantic weight for advanced hybrid mode |
| `rerank` | boolean | `false` | Enable keyword-based re-ranking |
| `include_snippets` | boolean | `true` | Include contextual snippets in results |
| `include_metadata` | boolean | `true` | Include patent metadata (title, type, source) |
| `log_enabled` | boolean | `false` | Log this query for analysis |

#### Response

```json
{
  "query": "machine learning",
  "mode": "semantic",
  "search_time": 2.145,
  "total_results": 5,
  "results": [
    {
      "doc_id": "US12417505B2_chunk11",
      "score": 0.7697,
      "title": "Detecting reliability across the internet after scraping",
      "doc_type": "grant",
      "source_file": "./data/grants/ipg250916.xml",
      "snippet": "This patent describes a **machine** **learning** algorithm that uses neural networks for image recognition...",
      "base_doc_id": "US12417505B2"
    }
  ]
}
```

#### Example Usage

```bash
# Basic search
curl -X POST "http://127.0.0.1:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "neural network", "mode": "semantic", "top_k": 3}'

# Advanced search with re-ranking
curl -X POST "http://127.0.0.1:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "mode": "hybrid", "rerank": true, "alpha": 0.7}'
```

### Summarization Endpoint

**POST** `/api/v1/summarize`

Generate intelligent summaries of patent documents.

#### Request Body

```json
{
  "doc_id": "US12417505B2",
  "max_length": 200
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `doc_id` | string | **required** | Patent document ID |
| `max_length` | integer | `200` | Maximum length of summary |

#### Response

```json
{
  "doc_id": "US12417505B2",
  "summary": "This patent describes a machine learning system for detecting reliability across internet data sources. The system uses advanced algorithms to analyze and validate information...",
  "title": "Detecting reliability across the internet after scraping",
  "doc_type": "grant"
}
```

### Batch Search Endpoint

**POST** `/api/v1/batch_search`

Process multiple queries in a single request.

#### Request Body

```json
{
  "queries": ["machine learning", "neural network", "artificial intelligence"],
  "mode": "semantic",
  "top_k": 3,
  "rerank": true
}
```

#### Response

```json
{
  "total_queries": 3,
  "mode": "semantic",
  "results": [
    {
      "query": "machine learning",
      "mode": "semantic",
      "search_time": 1.234,
      "total_results": 3,
      "results": [...]
    }
  ]
}
```

### Mode Comparison Endpoint

**POST** `/api/v1/compare_modes`

Compare search results across all available modes.

#### Request Body

```json
{
  "query": "artificial intelligence",
  "top_k": 3
}
```

#### Response

```json
{
  "query": "artificial intelligence",
  "top_k": 3,
  "results": {
    "tfidf": {
      "query": "artificial intelligence",
      "mode": "tfidf",
      "search_time": 0.456,
      "total_results": 3,
      "results": [...]
    },
    "semantic": {
      "query": "artificial intelligence", 
      "mode": "semantic",
      "search_time": 1.789,
      "total_results": 3,
      "results": [...]
    },
    "hybrid": {...},
    "hybrid-advanced": {...}
  }
}
```

### Log Analysis Endpoint

**GET** `/api/v1/logs/analyze`

Analyze query logs and return usage statistics.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_file` | string | `"query_log.jsonl"` | Path to log file |

#### Response

```json
{
  "log_file": "query_log.jsonl",
  "total_queries": 150,
  "unique_queries": 45,
  "mode_usage": {
    "tfidf": 60,
    "semantic": 70,
    "hybrid": 20
  },
  "average_score": 0.7234,
  "most_common_queries": [
    {"query": "machine learning", "count": 15},
    {"query": "neural network", "count": 12}
  ]
}
```

### Health Check Endpoint

**GET** `/api/v1/health`

Check API health and status.

#### Response

```json
{
  "status": "healthy",
  "message": "Patent NLP API is running",
  "version": "1.0.0"
}
```

## Search Modes

### 1. TF-IDF (`"tfidf"`)
- **Best for**: Exact keyword matches, traditional text search
- **Speed**: Fast
- **Accuracy**: Good for specific terms

### 2. Semantic (`"semantic"`)
- **Best for**: Conceptual similarity, meaning-based search
- **Speed**: Medium
- **Accuracy**: Excellent for related concepts

### 3. Hybrid (`"hybrid"`)
- **Best for**: Balanced approach combining TF-IDF and semantic
- **Speed**: Medium
- **Accuracy**: Good overall performance
- **Parameters**: `alpha` (0.0 = TF-IDF only, 1.0 = semantic only)

### 4. Hybrid Advanced (`"hybrid-advanced"`)
- **Best for**: Fine-tuned control over search weights
- **Speed**: Medium
- **Accuracy**: Best with proper tuning
- **Parameters**: `tfidf_weight`, `semantic_weight`

## Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (patent not found)
- **500**: Internal Server Error
- **503**: Service Unavailable (health check failed)

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Performance Tips

### 1. Search Performance
- Use `top_k` ≤ 10 for faster responses
- TF-IDF is fastest, semantic is most accurate
- Re-ranking adds ~20% processing time

### 2. Batch Processing
- Use `/batch_search` for multiple queries
- Process up to 50 queries per batch request
- Consider async processing for large batches

### 3. Caching
- Results are not cached by default
- Consider implementing client-side caching for repeated queries

## Integration Examples

### Python Client

```python
import requests

# Search patents
response = requests.post("http://127.0.0.1:8000/api/v1/search", json={
    "query": "machine learning",
    "mode": "semantic",
    "top_k": 5,
    "rerank": True
})

results = response.json()
for result in results["results"]:
    print(f"{result['doc_id']}: {result['score']:.4f}")
```

### JavaScript Client

```javascript
// Search patents
const response = await fetch('http://127.0.0.1:8000/api/v1/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'neural network',
    mode: 'semantic',
    top_k: 3,
    rerank: true
  })
});

const results = await response.json();
console.log(`Found ${results.total_results} results`);
```

## Prerequisites

Before using the API, ensure:

1. **Data is processed**: Run `python run_pipeline.py --build_index`
2. **Indices are built**: TF-IDF and semantic indices must exist
3. **Dependencies installed**: `pip install -r requirements.txt`

## Troubleshooting

### Common Issues

1. **"Patent not found"**: Check that the doc_id exists in your data
2. **"Search failed"**: Ensure indices are built and data is processed
3. **Slow responses**: Try reducing `top_k` or using TF-IDF mode
4. **Memory errors**: The API includes memory-efficient processing for large texts

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## API Versioning

Current version: **v1**

The API uses URL-based versioning (`/api/v1/`). Future versions will be available at `/api/v2/`, etc.

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding:
- Request rate limiting
- API key authentication
- Usage quotas

## Support

For issues or questions:
1. Check the interactive docs at `/docs`
2. Review the test suite in `test_api.py`
3. Check server logs for detailed error messages
