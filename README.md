<img src="static/images/ragsworth.png" alt="RagsWorth Logo" width="200" />

[![Tests](https://github.com/lukehinds/ragsworth/actions/workflows/test.yml/badge.svg)]

A spiffingly good, production-ready, secure, and embeddable AI chatbot with Retrieval-Augmented Generation (RAG) capabilities. Built with Python, it supports multiple LLM providers and includes robust PII protection.

## What Our Users Say

> "I didn't think a retrieval-augmented generation system could change my life. Then I found RagsWorth and my life changed." 
> — Juliet Armitage, General Counsel

> "Sometimes I wonder if RagsWorth is real. Sometimes I wonder if I’m real. But then he references a PDF I lost in 2019, and I know—he’s watching. In the good way."
> — Una Feld, Archivist

## What can RagsWorth do?

- Multi-Provider LLM Support (OpenAI, Anthropic, Ollama)
- RAG with document ingestion (PDF, Markdown, HTML, Text)
- Multiple Vector Database Backends (FAISS, Milvus)
- PII Detection and Protection Pipeline
- Easy Website ChatBot Integration
- Plugin Architecture for Custom Processing Steps
- Source Attribution for Generated Responses
- Make a splendid cup of tea

## Quick Start

1. Install using uv:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys (not needed for Ollama)
```

3. If using Ollama, pull required models:
```bash
# For chat completion
ollama pull gemma:2b  # or any other model like llama2, mistral

# For embeddings
ollama pull nomic-embed-text
```

4. Run the server:
```bash
uvicorn ragsworth.api:app --reload
```

5. Load some test documents:
```bash
# Create test documents directory
mkdir test_docs
# Add your documents (PDF, MD, TXT, HTML)
python scripts/load_documents.py test_docs
```

6. Embed in your website:
```html
<script src="http://localhost:8000/static/widget.js"></script>
<div id="ragsworth-chat"></div>
<script>
  new RagWorth({
    endpoint: 'http://localhost:8000',
    containerId: 'ragsworth-chat',
    theme: {
      primary: '#007bff',
      secondary: '#6c757d',
      background: '#ffffff',
      text: '#212529'
    }
  });
</script>
```

Note: Replace `http://localhost:8000` with your server's URL in production.

## Configuration

The bot can be configured via YAML or environment variables:

```yaml
llm:
  provider: ollama  # openai, anthropic, or ollama
  model: gemma3:4b  # Model name depends on the provider
  embedding_model: nomic-embed-text  # For Ollama embeddings
  temperature: 0.7

retrieval:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3
  vector_store:
    type: faiss  # 'faiss' or 'milvus'
    index_type: L2
    dimension: 768  # matches embedding model dimension
    # Milvus-specific configuration (if type is 'milvus')
    milvus:
      uri: "http://localhost:19530"
      user: ""
      password: ""
      db_name: "default"
      collection_name: "ragsworth_docs"
      token: ""
      timeout: 10

security:
  pii_detection: true
  audit_logging: true
  block_types:  # Customize PII detection
    - PERSON
    - EMAIL
    - PHONE
    - SSN
    - IP_ADDRESS
    - CREDIT_CARD
    - BANK_ACCOUNT
  replacement_char: X

server:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - "*"
  log_level: info
```

### Provider-Specific Notes

#### OpenAI
- Supports both chat completion and embeddings
- Requires `OPENAI_API_KEY` environment variable
- Recommended models: `gpt-4`, `gpt-3.5-turbo`
- Uses `text-embedding-3-small` for embeddings

#### Anthropic
- Supports only chat completion (no embeddings API)
- Requires `ANTHROPIC_API_KEY` environment variable
- Must use OpenAI or Ollama for embeddings
- Recommended models: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- When loading documents, specify an embedding provider:
  ```bash
  # Use OpenAI for embeddings
  python scripts/load_documents.py path/to/docs --embedding-provider openai

  # Use Ollama for embeddings
  python scripts/load_documents.py path/to/docs --embedding-provider ollama
  ```

#### Ollama
- Supports both chat completion and embeddings
- No API key required (runs locally)
- Recommended setup:
  - Use `gemma3:4b` or similar for chat completion
  - Use `nomic-embed-text` for embeddings (better quality than LLM embeddings)
- Custom endpoint configuration:
  ```bash
  # Use a custom Ollama endpoint
  python scripts/load_documents.py path/to/docs --ollama-url http://custom-ollama:11434
  ```
- Model management:
  ```bash
  # List available models
  ollama list
  
  # Pull new models
  ollama pull gemma:2b
  ollama pull nomic-embed-text
  
  # Remove models
  ollama rm gemma:2b
  ```

## Document Management

### Loading Documents

RagsWorth supports multiple document formats including PDF, Markdown, HTML, and plain text. You can load documents using the provided script:

```bash
# Load documents from a directory
python scripts/load_documents.py path/to/docs

# Load recursively with custom output location
python scripts/load_documents.py path/to/docs -r -o data/custom_vectorstore

# Use a different config file
python scripts/load_documents.py path/to/docs -c custom_config.yaml
```

For programmatic usage, here's how to load documents in your code:

```python
from ragsworth.rag.loader import DocumentLoader
from ragsworth.rag.chunker import TextChunker, ChunkConfig
from ragsworth.rag.vectorstore import FAISSVectorStore, FAISSVectorStoreConfig
# Or for Milvus:
# from ragsworth.rag.vectorstore import MilvusVectorStore, MilvusVectorStoreConfig

# Initialize components
loader = DocumentLoader()
chunker = TextChunker(ChunkConfig(
    chunk_size=500,
    chunk_overlap=50
))

# For FAISS vector store
vector_store = FAISSVectorStore(FAISSVectorStoreConfig(
    dimension=768,  # Matches your embedding model's dimension
    index_type="L2",
    top_k=3
))

# Or for Milvus vector store
# vector_store = MilvusVectorStore(MilvusVectorStoreConfig(
#     dimension=768,
#     top_k=3,
#     uri="http://localhost:19530",
#     collection_name="ragsworth_docs"
# ))

# Load documents from a directory
documents = loader.load_directory("path/to/docs", recursive=True)

# Process documents
for doc in documents:
    # Split into chunks
    chunks = chunker.split(doc)
    
    # Generate embeddings (requires LLM client)
    embeddings = await llm_client.embed([chunk.content for chunk in chunks])
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding
    
    # Add to vector store
    vector_store.add_documents(chunks)

# Save vector store for later use
vector_store.save("path/to/vectorstore")
```

### Loading Pre-existing Vector Store

To load a previously saved vector store:

```python
# For FAISS
vector_store = FAISSVectorStore.load("path/to/vectorstore")

# For Milvus
vector_store = MilvusVectorStore.load("path/to/vectorstore")
```

### Supported Document Types

- PDF (`.pdf`): Full document with page-level splitting
- Markdown (`.md`): Preserves markdown structure
- HTML (`.html`, `.htm`): Extracts clean text content
- Plain Text (`.txt`): Raw text processing
- Word Documents (`.docx`): Microsoft Word documents

### Vector Store Management

RagsWorth supports multiple vector store backends:

#### FAISS

FAISS is an in-memory vector database for efficient similarity search:

- `dimension`: Must match your embedding model's output dimension
- `index_type`: "L2" (Euclidean distance) or "cosine" (Cosine similarity)
- `top_k`: Number of similar documents to retrieve

Example configuration in `config.yaml`:

```yaml
retrieval:
  vector_store:
    type: faiss
    dimension: 768
    index_type: L2
```

#### Milvus

Milvus is a cloud-native vector database with advanced features:

- Requires a running Milvus server (included in docker-compose.yml)
- Scales better than FAISS for large document collections
- Persists data across application restarts

To use Milvus, start the services using Docker Compose:

```bash
# Start Milvus using Docker Compose
docker-compose up -d
```

Then configure RagsWorth to use Milvus in `config.yaml`:

```yaml
retrieval:
  vector_store:
    type: milvus
    dimension: 768
    index_type: L2
    milvus:
      uri: "http://localhost:19530"
      collection_name: "ragsworth_docs"
```

## Development

1. Install dev dependencies:
```bash
uv pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

3. Run linters:
```bash
black .
isort .
mypy .
```

## Docker Deployment

```bash
docker-compose up -d
```

## API Documentation

### Chat Endpoint

`POST /chat`

Request:
```json
{
  "session_id": "user-123",
  "user_message": "What are the key features?"
}
```

Response:
```json
{
  "session_id": "user-123",
  "bot_reply": "The key features include...",
  "source_documents": [
    {
      "id": "doc-456",
      "score": 0.92,
      "snippet": "..."
    }
  ]
}
```

## License

MIT License - see [LICENSE](LICENSE) for details. 
