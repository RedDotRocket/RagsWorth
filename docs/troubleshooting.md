# Troubleshooting Guide

This guide covers common issues and their solutions when using RagsWorth.

## Common Issues

### 1. Installation Issues

#### Python Package Installation Fails

**Symptoms:**
- `pip install` or `uv pip install` fails
- Missing dependencies
- Version conflicts

**Solutions:**
1. Ensure Python 3.8+ is installed:
```bash
python --version
```

2. Create a fresh virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. Install with specific version:
```bash
uv pip install "ragsworth>=1.0.0"
```

### 2. LLM Provider Issues

#### OpenAI API Errors

**Symptoms:**
- "API key not found"
- Rate limit errors
- Model not available

**Solutions:**
1. Check API key:
```bash
echo $OPENAI_API_KEY
```

2. Verify model availability:
```python
from ragsworth.llm import OpenAIClient

client = OpenAIClient()
available_models = client.list_models()
```

3. Handle rate limits:
```python
from ragsworth.llm import OpenAIClient

client = OpenAIClient(
    max_retries=3,
    retry_delay=1
)
```

#### Ollama Connection Issues

**Symptoms:**
- "Connection refused"
- Model not found
- Slow responses

**Solutions:**
1. Check Ollama service:
```bash
ollama list
```

2. Pull required models:
```bash
ollama pull gemma:2b
ollama pull nomic-embed-text
```

3. Verify connection:
```python
from ragsworth.llm import OllamaClient

client = OllamaClient()
client.health_check()
```

### 3. Vector Store Issues

#### FAISS Errors

**Symptoms:**
- "Dimension mismatch"
- Memory errors
- Slow performance

**Solutions:**
1. Check vector dimensions:
```python
from ragsworth.rag.vectorstore import FAISSVectorStore

store = FAISSVectorStore(dimension=768)  # Match your embedding model
```

2. Optimize memory usage:
```python
store = FAISSVectorStore(
    dimension=768,
    index_type="L2",
    use_gpu=True  # If available
)
```

#### Milvus Connection Issues

**Symptoms:**
- "Connection timeout"
- Collection not found
- Authentication errors

**Solutions:**
1. Check Milvus service:
```bash
docker ps | grep milvus
```

2. Verify connection:
```python
from ragsworth.rag.vectorstore import MilvusVectorStore

store = MilvusVectorStore(
    uri="http://localhost:19530",
    timeout=30
)
store.health_check()
```

3. Check collection:
```python
collections = store.list_collections()
print(f"Available collections: {collections}")
```

### 4. Document Processing Issues

#### File Loading Errors

**Symptoms:**
- "Unsupported file type"
- "File not found"
- Memory errors with large files

**Solutions:**
1. Check file format:
```python
from ragsworth.document_loader import DocumentLoader

loader = DocumentLoader()
supported_formats = loader.supported_formats()
print(f"Supported formats: {supported_formats}")
```

2. Process large files:
```python
loader = DocumentLoader(
    chunk_size=500,
    max_file_size=10_000_000  # 10MB
)
```

#### Embedding Generation Issues

**Symptoms:**
- "Model not found"
- "Dimension mismatch"
- Slow processing

**Solutions:**
1. Verify model:
```python
from ragsworth.llm import EmbeddingModel

model = EmbeddingModel()
available_models = model.list_models()
```

2. Batch processing:
```python
model = EmbeddingModel(batch_size=32)
embeddings = model.embed_batch(texts)
```

### 5. API Issues

#### Server Not Starting

**Symptoms:**
- "Address already in use"
- "Permission denied"
- Port conflicts

**Solutions:**
1. Check port availability:
```bash
lsof -i :8000
```

2. Change port:
```bash
uvicorn ragsworth.api:app --port 8001
```

3. Check permissions:
```bash
sudo chown -R $USER:$USER .
```

#### Authentication Errors

**Symptoms:**
- "Invalid API key"
- "Unauthorized"
- Token expiration

**Solutions:**
1. Verify API key:
```python
from ragsworth.api import RagsWorthAPI

api = RagsWorthAPI()
api.verify_api_key(api_key)
```

2. Check token:
```python
api = RagsWorthAPI()
api.refresh_token()
```

### 6. Performance Issues

#### Slow Query Response

**Symptoms:**
- High latency
- Timeout errors
- Resource exhaustion

**Solutions:**
1. Optimize vector store:
```python
store = FAISSVectorStore(
    index_type="COSINE",
    use_gpu=True
)
```

2. Adjust chunk size:
```python
loader = DocumentLoader(
    chunk_size=1000,
    chunk_overlap=100
)
```

3. Enable caching:
```python
from ragsworth.cache import Cache

cache = Cache(
    ttl=3600,
    max_size=1000
)
```

#### Memory Issues

**Symptoms:**
- "Out of memory"
- Slow performance
- System crashes

**Solutions:**
1. Monitor memory usage:
```python
import psutil

def check_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024} MB")
```

2. Optimize batch size:
```python
model = EmbeddingModel(
    batch_size=16,
    max_memory=1024  # MB
)
```

## Debugging Tools

### 1. Logging

Enable debug logging:
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Health Checks

Run system health check:
```python
from ragsworth.health import HealthCheck

health = HealthCheck()
status = health.check_all()
print(status)
```

### 3. Performance Profiling

Profile code execution:
```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()
profiler.print_stats()
```

## Getting Help

### 1. Community Support

- GitHub Issues: [RagsWorth Issues](https://github.com/yourusername/ragsworth/issues)
- Discord: [RagsWorth Community](https://discord.gg/ragsworth)
- Stack Overflow: Tag with `ragsworth`

### 2. Professional Support

- Email: support@ragsworth.com
- Documentation: [Full Documentation](../)
- Enterprise Support: [Contact Sales](https://ragsworth.com/enterprise)

## Related Documentation

- [Configuration Guide](./configuration.md)
- [API Reference](./api/README.md)
- [Vector Database Integration](./vector-db.md)
- [Embedding Models](./embedding-models.md) 