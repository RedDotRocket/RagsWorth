# Frequently Asked Questions (FAQ)

## General Questions

### What is RagsWorth?

RagsWorth is a production-ready, secure, and embeddable AI chatbot with Retrieval-Augmented Generation (RAG) capabilities. It supports multiple LLM providers, includes robust PII protection, and can be easily integrated into websites and applications.

### What are the system requirements?

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB disk space
- Internet connection (for API-based LLMs)
- Docker (optional, for containerized deployment)

### Is RagsWorth free to use?

RagsWorth is open-source and free to use. However, some features may require paid API keys (e.g., OpenAI, Anthropic) or additional resources (e.g., Milvus for large-scale deployments).

## Technical Questions

### Which LLM providers are supported?

RagsWorth supports:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Ollama (local models)

### What vector databases are supported?

Currently supported:
- FAISS (local, lightweight)
- Milvus (distributed, scalable)

### How do I choose between FAISS and Milvus?

Choose based on your needs:
- FAISS: Development, testing, small deployments
- Milvus: Production, large-scale, distributed deployments

### What file formats are supported?

Supported formats:
- PDF
- Markdown
- HTML
- Text
- Word documents
- RTF

## Configuration Questions

### How do I configure the LLM provider?

```yaml
llm:
  provider: ollama  # or openai, anthropic
  model: gemma3:4b
  embedding_model: nomic-embed-text
```

### How do I set up PII protection?

```yaml
security:
  pii_detection: true
  block_types:
    - EMAIL
    - PHONE
    - SSN
  replacement_char: X
```

### How do I configure the vector store?

```yaml
retrieval:
  vector_store:
    type: milvus  # or faiss
    dimension: 768
    index_type: COSINE
```

## Performance Questions

### How can I improve query response time?

1. Use appropriate chunk sizes
2. Enable caching
3. Optimize vector store settings
4. Use GPU acceleration (if available)
5. Implement batch processing

### How much memory does RagsWorth use?

Memory usage depends on:
- Document collection size
- Vector store type
- Chunk size
- Batch size
- Number of concurrent requests

Typical usage:
- FAISS: 100MB-1GB
- Milvus: 1GB-10GB+

### How do I handle large document collections?

1. Use Milvus for distributed storage
2. Implement batch processing
3. Optimize chunk sizes
4. Use appropriate hardware
5. Monitor resource usage

## Security Questions

### How does PII protection work?

RagsWorth:
1. Detects PII in text
2. Replaces with placeholders
3. Logs detection events
4. Supports multiple PII types
5. Integrates with processing pipeline

### Is my data secure?

Yes, RagsWorth implements:
- PII detection and protection
- Secure API authentication
- Audit logging
- Data encryption
- Access control

### How do I handle API keys securely?

1. Use environment variables
2. Implement key rotation
3. Monitor usage
4. Set up rate limiting
5. Use secure storage

## Integration Questions

### How do I embed RagsWorth in my website?

```html
<script src="http://localhost:8000/static/widget.js"></script>
<div id="ragsworth-chat"></div>
<script>
  new RagsWorth({
    endpoint: 'http://localhost:8000',
    containerId: 'ragsworth-chat'
  });
</script>
```

### Can I use RagsWorth with my existing chatbot?

Yes, RagsWorth can be integrated with existing chatbots through:
- REST API
- WebSocket interface
- Python SDK
- JavaScript SDK

### How do I customize the chat interface?

```javascript
new RagsWorth({
  theme: {
    primary: '#007bff',
    secondary: '#6c757d',
    background: '#ffffff',
    text: '#212529'
  },
  position: 'bottom-right',
  welcomeMessage: 'Hello! How can I help you?'
});
```

## Deployment Questions

### How do I deploy RagsWorth in production?

1. Set up a production server
2. Configure environment variables
3. Set up vector database
4. Configure security settings
5. Set up monitoring
6. Implement backup strategy

### Can I use Docker?

Yes, RagsWorth supports Docker deployment:

```bash
docker-compose up -d
```

### How do I scale RagsWorth?

1. Use Milvus for distributed storage
2. Implement load balancing
3. Set up monitoring
4. Configure auto-scaling
5. Optimize resource usage

## Support Questions

### Where can I get help?

- Documentation: [Full Documentation](./)
- GitHub Issues: [RagsWorth Issues](https://github.com/yourusername/ragsworth/issues)
- Discord: [RagsWorth Community](https://discord.gg/ragsworth)
- Stack Overflow: Tag with `ragsworth`

### How do I report bugs?

1. Check existing issues
2. Create new issue
3. Provide:
   - Description
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

### Is there enterprise support?

Yes, enterprise support includes:
- Priority support
- Custom features
- Training
- Consulting
- SLA guarantees

## Related Documentation

- [Configuration Guide](./configuration.md)
- [API Reference](./api/README.md)
- [Vector Database Integration](./vector-db.md)
- [Embedding Models](./embedding-models.md)
- [PII Protection](./pii-protection.md)
- [Troubleshooting](./troubleshooting.md) 