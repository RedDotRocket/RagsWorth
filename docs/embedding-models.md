# Embedding Models

RagsWorth supports multiple embedding models for converting text into vector representations. This guide covers the supported models and their configuration.

## Supported Models

### 1. OpenAI Embeddings

OpenAI's embedding models are available through their API:

```yaml
llm:
  provider: openai
  embedding_model: text-embedding-3-small  # or text-embedding-3-large
```

#### Features
- High-quality embeddings
- 1536 dimensions (small) or 3072 dimensions (large)
- Optimized for semantic search
- Requires API key

#### Usage Example

```python
from ragsworth.llm import OpenAIEmbeddingModel

model = OpenAIEmbeddingModel(
    model="text-embedding-3-small",
    api_key="your-api-key"
)

# Generate embeddings
embeddings = model.embed(["Your text here"])
```

### 2. Nomic Embed Text

Nomic's embedding model is available through Ollama:

```yaml
llm:
  provider: ollama
  embedding_model: nomic-embed-text
```

#### Features
- 768 dimensions
- High-quality embeddings
- Local deployment
- No API key required

#### Usage Example

```python
from ragsworth.llm import OllamaEmbeddingModel

model = OllamaEmbeddingModel(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

# Generate embeddings
embeddings = model.embed(["Your text here"])
```

## Model Comparison

| Model | Dimensions | Quality | Speed | Cost | Local |
|-------|------------|---------|-------|------|-------|
| text-embedding-3-small | 1536 | High | Fast | $0.00002/1K tokens | No |
| text-embedding-3-large | 3072 | Very High | Medium | $0.00013/1K tokens | No |
| nomic-embed-text | 768 | High | Fast | Free | Yes |

## Configuration

### Basic Configuration

```yaml
llm:
  provider: ollama  # or openai
  embedding_model: nomic-embed-text  # or text-embedding-3-small
```

### Advanced Configuration

```yaml
llm:
  provider: ollama
  embedding_model: nomic-embed-text
  embedding_options:
    batch_size: 32
    max_retries: 3
    timeout: 30
```

## Best Practices

### 1. Model Selection

Choose a model based on your requirements:

- **OpenAI text-embedding-3-small**
  - Best for production use
  - High quality
  - Reasonable cost
  - Requires API key

- **OpenAI text-embedding-3-large**
  - Best for maximum accuracy
  - Higher cost
  - Slower processing
  - Requires API key

- **Nomic Embed Text**
  - Best for local deployment
  - No API costs
  - Good quality
  - Requires Ollama

### 2. Batch Processing

For large document collections:

```python
# Process in batches
batch_size = 32
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    embeddings = model.embed(batch)
    # Store embeddings
```

### 3. Error Handling

```python
from ragsworth.llm import EmbeddingError

try:
    embeddings = model.embed(texts)
except EmbeddingError as e:
    # Handle error
    logger.error(f"Embedding error: {e}")
    # Retry or fallback
```

### 4. Performance Optimization

- Use appropriate batch sizes
- Cache frequently used embeddings
- Monitor API usage and costs
- Consider local models for high-volume use

## Integration with Vector Stores

### FAISS

```python
from ragsworth.rag.vectorstore import FAISSVectorStore

# Initialize with matching dimensions
vector_store = FAISSVectorStore(
    dimension=768,  # for nomic-embed-text
    index_type="COSINE"
)
```

### Milvus

```python
from ragsworth.rag.vectorstore import MilvusVectorStore

# Initialize with matching dimensions
vector_store = MilvusVectorStore(
    dimension=768,  # for nomic-embed-text
    index_type="COSINE"
)
```

## Troubleshooting

### Common Issues

1. **Dimension Mismatch**
   - Error: "Vector dimension mismatch"
   - Solution: Ensure vector store dimension matches model

2. **API Rate Limits**
   - Error: "Rate limit exceeded"
   - Solution: Implement retry logic with backoff

3. **Memory Issues**
   - Error: "Out of memory"
   - Solution: Reduce batch size or use local model

### Debugging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ragsworth.llm")

# Enable debug logging for embeddings
logger.debug("Generating embeddings...")
```

## Related Documentation

- [Configuration Guide](./configuration.md)
- [Vector Database Integration](./vector-db.md)
- [API Reference](./api/README.md) 