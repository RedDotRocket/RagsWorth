# Vector Database Integration

RagsWorth supports multiple vector database backends for storing and retrieving document embeddings. This guide covers the supported options and their configuration.

## Supported Backends

### 1. FAISS (Facebook AI Similarity Search)

FAISS is a local vector store library developed by Facebook Research. It's ideal for:
- Small to medium-sized deployments
- Single-server setups
- Development and testing
- Low-latency requirements

#### Configuration

```yaml
retrieval:
  vector_store:
    type: faiss
    index_type: L2  # or COSINE
    dimension: 768  # matches embedding model dimension
```

#### Features
- In-memory and on-disk storage options
- Multiple index types (L2, COSINE, IP)
- GPU acceleration support
- No external dependencies

#### Usage Example

```python
from ragsworth.rag.vectorstore import FAISSVectorStore, FAISSVectorStoreConfig

# Initialize FAISS vector store
vector_store = FAISSVectorStore(FAISSVectorStoreConfig(
    dimension=768,
    index_type="L2",
    top_k=3
))

# Add vectors
vector_store.add(vectors, metadata)

# Search
results = vector_store.search(query_vector, top_k=3)
```

### 2. Milvus

Milvus is a distributed vector database designed for production use. It's ideal for:
- Large-scale deployments
- High availability requirements
- Cloud-native environments
- Production workloads

#### Configuration

```yaml
retrieval:
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

#### Features
- Distributed architecture
- Horizontal scaling
- High availability
- Cloud-native design
- Multiple index types
- GPU acceleration

#### Usage Example

```python
from ragsworth.rag.vectorstore import MilvusVectorStore, MilvusVectorStoreConfig

# Initialize Milvus vector store
vector_store = MilvusVectorStore(MilvusVectorStoreConfig(
    dimension=768,
    top_k=3,
    uri="http://localhost:19530",
    collection_name="ragsworth_docs"
))

# Add vectors
vector_store.add(vectors, metadata)

# Search
results = vector_store.search(query_vector, top_k=3)
```

## Choosing a Backend

### When to Use FAISS

- Development and testing environments
- Small to medium-sized document collections
- Single-server deployments
- Low-latency requirements
- Simple setup and maintenance

### When to Use Milvus

- Production environments
- Large document collections
- Distributed deployments
- High availability requirements
- Cloud-native infrastructure

## Performance Considerations

### FAISS
- Memory usage: ~4 bytes per vector dimension
- Query latency: < 1ms for small collections
- Storage: Local disk or memory
- Scalability: Limited to single machine

### Milvus
- Memory usage: Distributed across nodes
- Query latency: 5-50ms depending on cluster size
- Storage: Distributed storage
- Scalability: Horizontal scaling

## Migration Between Backends

To migrate from FAISS to Milvus (or vice versa):

1. Export vectors and metadata from source
2. Initialize new vector store
3. Import data into new store
4. Update configuration
5. Verify functionality

Example migration script:

```python
from ragsworth.rag.vectorstore import FAISSVectorStore, MilvusVectorStore

# Export from FAISS
faiss_store = FAISSVectorStore(...)
vectors, metadata = faiss_store.export_all()

# Import to Milvus
milvus_store = MilvusVectorStore(...)
milvus_store.add(vectors, metadata)
```

## Best Practices

1. **Dimension Matching**
   - Ensure vector dimensions match your embedding model
   - Default is 768 for nomic-embed-text

2. **Index Type Selection**
   - COSINE: Best for semantic similarity
   - L2: Best for exact distance matching
   - IP: Best for dot product similarity

3. **Performance Tuning**
   - Adjust `top_k` based on your needs
   - Monitor memory usage
   - Use appropriate chunk sizes

4. **Backup and Recovery**
   - Regular backups of vector stores
   - Document migration procedures
   - Test recovery processes

## Related Documentation

- [Configuration Guide](./configuration.md)
- [Embedding Models](./embedding-models.md)
- [API Reference](./api/README.md) 