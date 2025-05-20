# API Reference

This section provides detailed documentation for RagsWorth's API endpoints, classes, and functions.

## Table of Contents

- [Core API](./core.md)
- [LLM Integration](./llm.md)
- [Vector Store](./vectorstore.md)
- [Document Processing](./document.md)
- [Security](./security.md)

## Quick Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Process a query and return response |
| `/documents` | POST | Upload and process documents |
| `/documents/{id}` | GET | Retrieve document metadata |
| `/documents/{id}` | DELETE | Delete a document |
| `/health` | GET | Check API health |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/ws/chat` | Real-time chat interface |
| `/ws/status` | Document processing status |

## Core Components

### 1. Pipeline

```python
from ragsworth.pipeline import Pipeline

pipeline = Pipeline()
pipeline.add_stage("pii_detection", PIIDetector())
pipeline.add_stage("embedding", EmbeddingGenerator())
pipeline.add_stage("retrieval", VectorStoreRetriever())
```

### 2. Document Loader

```python
from ragsworth.document_loader import DocumentLoader

loader = DocumentLoader()
documents = loader.load_directory("path/to/docs")
```

### 3. Vector Store

```python
from ragsworth.rag.vectorstore import FAISSVectorStore

vector_store = FAISSVectorStore(
    dimension=768,
    index_type="COSINE"
)
```

## API Usage Examples

### Basic Query

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "What is RagsWorth?",
        "context": "general"
    }
)
```

### Document Upload

```python
import requests

files = {
    "file": ("document.pdf", open("document.pdf", "rb"))
}
response = requests.post(
    "http://localhost:8000/documents",
    files=files
)
```

### WebSocket Chat

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat");

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log(response.message);
};

ws.send(JSON.stringify({
    type: "message",
    content: "Hello, RagsWorth!"
}));
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

### Error Response Format

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {
            "field": "Additional error details"
        }
    }
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- 100 requests per minute for `/query`
- 50 requests per minute for `/documents`
- 1000 requests per minute for `/health`

## Authentication

### API Key Authentication

```python
headers = {
    "Authorization": f"Bearer {api_key}"
}
response = requests.get(
    "http://localhost:8000/documents",
    headers=headers
)
```

### JWT Authentication

```python
headers = {
    "Authorization": f"Bearer {jwt_token}"
}
response = requests.post(
    "http://localhost:8000/query",
    headers=headers,
    json={"query": "Hello"}
)
```

## Webhook Integration

Configure webhooks for event notifications:

```python
webhook_config = {
    "url": "https://your-server.com/webhook",
    "events": ["document.processed", "query.completed"],
    "secret": "your-webhook-secret"
}
```

## SDK Support

### Python SDK

```python
from ragsworth import RagsWorth

client = RagsWorth(api_key="your-api-key")
response = client.query("What is RagsWorth?")
```

### JavaScript SDK

```javascript
import { RagsWorth } from '@ragsworth/sdk';

const client = new RagsWorth({
    apiKey: 'your-api-key'
});

client.query('What is RagsWorth?')
    .then(response => console.log(response));
```

## Related Documentation

- [Configuration Guide](../configuration.md)
- [Vector Database Integration](../vector-db.md)
- [Embedding Models](../embedding-models.md)
- [PII Protection](../pii-protection.md) 