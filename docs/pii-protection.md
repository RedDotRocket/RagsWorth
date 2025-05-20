# PII Protection

RagsWorth includes built-in Personally Identifiable Information (PII) detection and protection features. This guide covers the security features and their configuration.

## Overview

The PII protection system:
- Detects sensitive information in text
- Replaces PII with safe placeholders
- Logs detection events (optional)
- Supports multiple PII types
- Integrates with the document processing pipeline

## Configuration

### Basic Configuration

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

### Supported PII Types

| Type | Description | Example |
|------|-------------|---------|
| EMAIL | Email addresses | user@example.com |
| PHONE | Phone numbers | (555) 123-4567 |
| SSN | Social Security numbers | 123-45-6789 |
| IP_ADDRESS | IP addresses | 192.168.1.1 |
| CREDIT_CARD | Credit card numbers | 4111-1111-1111-1111 |
| BANK_ACCOUNT | Bank account numbers | 1234567890 |

## Usage

### Document Processing

PII detection is automatically applied during document processing:

```python
from ragsworth.document_loader import DocumentLoader
from ragsworth.security import PIIDetector

# Initialize components
loader = DocumentLoader()
pii_detector = PIIDetector(
    block_types=["EMAIL", "PHONE"],
    replacement_char="X"
)

# Load and process document
document = loader.load("document.pdf")
sanitized_document = pii_detector.process(document)
```

### Real-time Processing

For real-time text processing:

```python
from ragsworth.security import PIIDetector

detector = PIIDetector()
text = "Contact us at user@example.com or (555) 123-4567"
sanitized_text = detector.process_text(text)
# Result: "Contact us at XXXXXXXXXXXXX or XXXXXXXXXXXX"
```

## Integration Points

### 1. Document Ingestion

```python
from ragsworth.pipeline import Pipeline

pipeline = Pipeline()
pipeline.add_stage("pii_detection", PIIDetector())
pipeline.process_document(document)
```

### 2. Query Processing

```python
from ragsworth.api import app

@app.post("/query")
async def process_query(query: str):
    # Detect PII in query
    sanitized_query = pii_detector.process_text(query)
    # Process sanitized query
    return await process_sanitized_query(sanitized_query)
```

### 3. Response Generation

```python
from ragsworth.llm import LLMClient

llm = LLMClient()
response = llm.generate(sanitized_query)
# PII detection is applied to response
sanitized_response = pii_detector.process_text(response)
```

## Audit Logging

Enable audit logging to track PII detection events:

```yaml
security:
  audit_logging: true
  log_file: "pii_audit.log"
  log_level: INFO
```

### Log Format

```json
{
  "timestamp": "2024-03-20T10:00:00Z",
  "event": "PII_DETECTED",
  "pii_type": "EMAIL",
  "context": "Contact information",
  "action": "REPLACED"
}
```

## Custom PII Types

Extend the PII detection system with custom patterns:

```python
from ragsworth.security import PIIDetector, CustomPIIType

# Define custom PII type
custom_type = CustomPIIType(
    name="CUSTOM_ID",
    pattern=r"\b[A-Z]{2}\d{6}\b",
    description="Custom ID format"
)

# Initialize detector with custom type
detector = PIIDetector(
    block_types=["EMAIL", "CUSTOM_ID"],
    custom_types=[custom_type]
)
```

## Best Practices

### 1. Configuration

- Enable PII detection for all sensitive data
- Use appropriate replacement characters
- Configure audit logging for compliance
- Regularly update PII patterns

### 2. Processing Order

1. Detect PII in input
2. Replace with placeholders
3. Process sanitized text
4. Log detection events
5. Store sanitized data

### 3. Error Handling

```python
from ragsworth.security import PIIError

try:
    sanitized_text = detector.process_text(text)
except PIIError as e:
    logger.error(f"PII processing error: {e}")
    # Handle error appropriately
```

### 4. Performance Considerations

- Batch process documents when possible
- Use appropriate logging levels
- Monitor detection performance
- Cache common patterns

## Compliance

### GDPR Compliance

- PII detection helps identify personal data
- Audit logging provides compliance trail
- Data minimization through PII removal
- Documentation of processing activities

### HIPAA Compliance

- PHI detection capabilities
- Secure logging of detection events
- Access control for audit logs
- Regular security reviews

## Troubleshooting

### Common Issues

1. **False Positives**
   - Adjust pattern sensitivity
   - Add context rules
   - Review detection logs

2. **Performance Issues**
   - Optimize pattern matching
   - Use batch processing
   - Monitor resource usage

3. **Logging Issues**
   - Check log permissions
   - Verify log configuration
   - Monitor log rotation

### Debugging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ragsworth.security")

# Enable debug logging
logger.debug("Processing text for PII...")
```

## Related Documentation

- [Configuration Guide](./configuration.md)
- [API Reference](./api/README.md)
- [Security Best Practices](./security.md) 