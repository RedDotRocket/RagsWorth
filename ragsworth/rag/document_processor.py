"""
Document processing functionality for RagsWorth.
"""

import os
from typing import Dict, Union

from .chunker import ChunkConfig, TextChunker
from .loader import DocumentLoader
from .vectorstore import (
    FAISSVectorStore,
    FAISSVectorStoreConfig,
    MilvusVectorStore,
    MilvusVectorStoreConfig
)
from ..llm import OpenAIClient, AnthropicClient, OllamaClient
from ..llm.base import LLMConfig

from ..config.logging_config import get_logger

logger = get_logger("rag.document_processor")

class DocumentProcessor:
    """Handles document loading, chunking, and vector store integration."""

    def __init__(self, config: Dict):
        """Initialize the document processor with configuration."""
        self.config = config
        self.loader = DocumentLoader()
        self.chunker = TextChunker(ChunkConfig(
            chunk_size=config["retrieval"]["chunk_size"],
            chunk_overlap=config["retrieval"]["chunk_overlap"]
        ))
        self._init_vector_store()
        self._init_llm_client()

    def _init_vector_store(self):
        """Initialize the appropriate vector store based on configuration."""
        vector_store_type = self.config["retrieval"]["vector_store"].get("type", "faiss").lower()
        vector_store_dimension = self.config["retrieval"]["vector_store"]["dimension"]
        vector_store_top_k = self.config["retrieval"]["top_k"]

        if vector_store_type == "faiss":
            self.vector_store = FAISSVectorStore(FAISSVectorStoreConfig(
                dimension=vector_store_dimension,
                index_type=self.config["retrieval"]["vector_store"]["index_type"],
                top_k=vector_store_top_k
            ))
        elif vector_store_type == "milvus":
            # Get Milvus-specific configuration
            milvus_config = MilvusVectorStoreConfig(
                dimension=vector_store_dimension,
                top_k=vector_store_top_k,
                index_type=self.config["retrieval"]["vector_store"].get("index_type", "L2")
            )

            # Add additional Milvus parameters if specified in config
            milvus_section = self.config["retrieval"]["vector_store"].get("milvus", {})
            if milvus_section:
                for key in ["uri", "user", "password", "db_name", "collection_name", "token", "timeout"]:
                    if key in milvus_section:
                        setattr(milvus_config, key, milvus_section[key])

            self.vector_store = MilvusVectorStore(milvus_config)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    def _init_llm_client(self):
        """Initialize the LLM client for embeddings."""
        provider = self.config["llm"]["provider"].lower()
        LLM_PROVIDERS = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "ollama": OllamaClient
        }

        if provider not in LLM_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        embedding_model = self.config["llm"].get("embedding_model", self.config["llm"]["model"])
        llm_config = LLMConfig(
            model=embedding_model,
            temperature=self.config["llm"]["temperature"]
        )

        if provider == "ollama":
            llm_config.extra_params = {
                "base_url": self.config["llm"].get("base_url", "http://localhost:11434"),
                "embedding_model": embedding_model
            }

        self.llm_client = LLM_PROVIDERS[provider](llm_config)

    async def process_documents(self, docs_dir: str, recursive: bool = False) -> None:
        """Process documents from a directory and add them to the vector store."""
        # Load documents
        documents = self.loader.load_directory(docs_dir, recursive=recursive)
        if not documents:
            logger.warning("No supported documents found!")
            return

        logger.info(f"Processing {len(documents)} documents...")
        total_chunks = 0
        for i, doc in enumerate(documents, 1):
            # Split into chunks
            chunks = self.chunker.split(doc)
            if not chunks:
                continue

            # Instead of printing with end="", log at debug level for each document
            logger.debug(f"Processing document {i}/{len(documents)}: {len(chunks)} chunks")

            # Generate embeddings
            embeddings = await self.llm_client.embed([chunk.content for chunk in chunks])

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding

            # Add to vector store
            self.vector_store.add_documents(chunks)
            total_chunks += len(chunks)

        logger.info(f"Completed! Processed {len(documents)} documents into {total_chunks} chunks")

    def save_vector_store(self, output_dir: str) -> None:
        """Save the vector store to disk."""
        os.makedirs(output_dir, exist_ok=True)
        self.vector_store.save(output_dir)
        logger.info(f"Vector store saved to {output_dir}")

    @classmethod
    def load_vector_store(cls, directory: str, config: Dict) -> Union[FAISSVectorStore, MilvusVectorStore]:
        """Load a vector store from disk."""
        vector_store_type = config["retrieval"]["vector_store"].get("type", "faiss").lower()

        if vector_store_type == "faiss":
            return FAISSVectorStore.load(directory)
        elif vector_store_type == "milvus":
            return MilvusVectorStore.load(directory)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")