"""
Pipeline stage implementations for the chat endpoint.
"""

from typing import Dict, List, Union

from .llm.base import LLMClient
from .pipeline import ChatRequest, PipelineStage
from .rag.vectorstore import FAISSVectorStore, MilvusVectorStore
from .security.pii import PIIDetector
from .config.logging_config import get_logger

logger = get_logger("stages")

class InputSanitizer(PipelineStage):
    """Sanitizes and validates input."""

    async def process(self, request: ChatRequest, context: Dict) -> ChatRequest:
        # Basic input validation
        if not request.user_message.strip():
            raise ValueError("Empty user message")

        # Trim whitespace
        request.user_message = request.user_message.strip()
        return request

class PIIBlocker(PipelineStage):
    """Blocks PII in user input."""

    def __init__(self, detector: PIIDetector):
        self.detector = detector

    async def process(self, request: ChatRequest, context: Dict) -> ChatRequest:
        # Detect and block PII
        blocked_text, audit_log = self.detector.detect_and_block(request.user_message)

        # Store original text and audit log in context
        context["original_message"] = request.user_message
        context["pii_audit_log"] = audit_log

        # Update request with blocked text
        request.user_message = blocked_text
        return request

class Retriever(PipelineStage):
    """Retrieves relevant documents using RAG."""

    def __init__(self, vector_store: Union[FAISSVectorStore, MilvusVectorStore], llm_client: LLMClient):
        self.vector_store = vector_store
        self.llm_client = llm_client
        logger.info(f"Retriever initialized with {type(vector_store).__name__} containing {len(vector_store.documents)} documents")

    async def process(self, request: ChatRequest, context: Dict) -> ChatRequest:
        # Generate embedding for query
        query_embedding = await self.llm_client.embed([request.user_message])
        logger.debug(f"Generated embedding for query: {request.user_message[:50]}...")

        # Search for relevant documents
        results = self.vector_store.search(query_embedding[0])
        logger.info(f"Search returned {len(results)} documents")

        # Store results in context
        context["retrieved_documents"] = [doc for doc, score in results]
        context["document_scores"] = [score for _, score in results]
        
        if results:
            # Log all retrieved documents with their scores
            for i, (doc, score) in enumerate(results):
                logger.debug(f"Document {i+1}:")
                logger.debug(f"  ID: {doc.id}")
                logger.debug(f"  Score: {score}")
                logger.debug(f"  Content snippet: {doc.content[:100]}...")
        else:
            logger.warning("No documents retrieved from vector store")

        # Build prompt with context - only include documents with meaningful content
        context_docs = []
        for i, doc in enumerate(context["retrieved_documents"]):
            if doc.content and len(doc.content.strip()) > 0:
                # Format the document content with its ID for the prompt
                context_docs.append(f"Document {i+1} [{doc.id}]:\n{doc.content}")
        
        context_text = "\n\n".join(context_docs)
        
        if context_text:
            logger.info(f"Added {len(context_docs)} documents to context")
        else:
            logger.warning("No documents added to context - empty results")

        # Update request with context
        request.metadata["context_text"] = context_text
        return request

class LLMStage(PipelineStage):
    """Generates response using LLM."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def process(self, request: ChatRequest, context: Dict) -> ChatRequest:
        # Build conversation context
        conversation = request.metadata.get("context", [])

        # Add retrieved context to prompt
        context_text = request.metadata.get("context_text", "")
        system_prompt = self.llm_client.config.extra_params.get("system_prompt", "") if self.llm_client.config.extra_params else ""
        
        if context_text:
            system_prompt += f"\n\nRelevant context:\n{context_text}"

        # Generate response
        response = await self.llm_client.generate(
            prompt=request.user_message,
            system_prompt=system_prompt,
            context=conversation
        )

        # Store response in context
        context["bot_reply"] = response.text
        context["source_documents"] = context.get("retrieved_documents", [])

        return request

class OutputSanitizer(PipelineStage):
    """Sanitizes LLM output for PII and other issues."""

    def __init__(self, detector: PIIDetector):
        self.detector = detector

    async def process(self, request: ChatRequest, context: Dict) -> ChatRequest:
        if "bot_reply" not in context:
            return request

        # Scan output for PII
        clean_text, audit_log = self.detector.scan_output(context["bot_reply"])

        # Update audit log
        context["pii_audit_log"] = context.get("pii_audit_log", []) + audit_log

        # Update response
        context["bot_reply"] = clean_text
        return request