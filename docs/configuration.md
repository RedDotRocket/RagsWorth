# Configuration Guide

RagsWorth can be configured using a YAML configuration file (`config.yaml`) or environment variables. This guide covers all available configuration options and their usage.

## Configuration File Structure

The main configuration file (`config.yaml`) is organized into several sections:

```yaml
llm:
  provider: ollama  # openai, anthropic, or ollama
  model: gemma3:4b  # Model name depends on the provider
  embedding_model: nomic-embed-text  # For Ollama embeddings
  temperature: 0.7
  system_prompt: |
    You are an AI assistant for a corporate leadership training platform...

retrieval:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3
  vector_store:
    type: milvus  # 'faiss' or 'milvus'
    index_type: COSINE
    dimension: 768
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
  block_types:
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

## LLM Configuration

### Provider Selection

```yaml
llm:
  provider: ollama  # openai, anthropic, or ollama
```

- `openai`: Uses OpenAI's API (requires API key)
- `anthropic`: Uses Anthropic's API (requires API key)
- `ollama`: Uses local Ollama instance (no API key needed)

### Model Configuration

```yaml
llm:
  model: gemma3:4b  # for chat completion
  embedding_model: nomic-embed-text  # for embeddings
  temperature: 0.7
```

#### Provider-Specific Models

1. **OpenAI**
   - Chat: `gpt-4`, `gpt-3.5-turbo`
   - Embeddings: `text-embedding-3-small`

2. **Anthropic**
   - Chat: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
   - Embeddings: Must use OpenAI or Ollama

3. **Ollama**
   - Chat: `gemma3:4b`, `llama2`, `mistral`
   - Embeddings: `nomic-embed-text`

### System Prompt

```yaml
llm:
  system_prompt: |
    You are an AI assistant for a corporate leadership training platform...
```

Customize the system prompt to define the AI's behavior and capabilities.

## Retrieval Configuration

### Document Chunking

```yaml
retrieval:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3
```

- `chunk_size`: Maximum size of each text chunk
- `chunk_overlap`: Number of characters to overlap between chunks
- `top_k`: Number of most relevant chunks to retrieve

### Vector Store

```yaml
retrieval:
  vector_store:
    type: milvus  # 'faiss' or 'milvus'
    index_type: COSINE
    dimension: 768
```

#### FAISS Configuration

FAISS is a local vector store, suitable for smaller deployments:

```yaml
vector_store:
  type: faiss
  index_type: L2  # or COSINE
  dimension: 768
```

#### Milvus Configuration

Milvus is a distributed vector store, suitable for production:

```yaml
vector_store:
  type: milvus
  index_type: COSINE
  dimension: 768
  milvus:
    uri: "http://localhost:19530"
    user: ""
    password: ""
    db_name: "default"
    collection_name: "ragsworth_docs"
    token: ""
    timeout: 10
```

## Security Configuration

```yaml
security:
  pii_detection: true
  audit_logging: true
  block_types:
    - EMAIL
    - PHONE
    - SSN
    - IP_ADDRESS
    - CREDIT_CARD
    - BANK_ACCOUNT
  replacement_char: X
```

- `pii_detection`: Enable/disable PII detection
- `audit_logging`: Enable/disable audit logging
- `block_types`: Types of PII to detect and block
- `replacement_char`: Character to replace detected PII

## Server Configuration

```yaml
server:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - "*"
  log_level: info
```

- `host`: Server host address
- `port`: Server port
- `cors_origins`: Allowed CORS origins
- `log_level`: Logging level (debug, info, warning, error)

## Environment Variables

All configuration options can also be set using environment variables:

```bash
# LLM Configuration
RAGSWORTH_LLM_PROVIDER=ollama
RAGSWORTH_LLM_MODEL=gemma3:4b
RAGSWORTH_LLM_EMBEDDING_MODEL=nomic-embed-text
RAGSWORTH_LLM_TEMPERATURE=0.7

# Vector Store Configuration
RAGSWORTH_VECTOR_STORE_TYPE=milvus
RAGSWORTH_VECTOR_STORE_DIMENSION=768

# Security Configuration
RAGSWORTH_PII_DETECTION=true
RAGSWORTH_AUDIT_LOGGING=true

# Server Configuration
RAGSWORTH_HOST=0.0.0.0
RAGSWORTH_PORT=8000
```

## Configuration Precedence

1. Environment variables
2. Configuration file
3. Default values

## Related Documentation

- [Vector Database Integration](./vector-db.md)
- [Embedding Models](./embedding-models.md)
- [PII Protection](./pii-protection.md) 