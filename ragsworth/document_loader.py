"""
Document loading functionality for RagsWorth.
"""
import asyncio
import os
from pathlib import Path
from typing import Dict

import click
from tqdm.auto import tqdm

from .llm import OpenAIClient, AnthropicClient, OllamaClient
from .llm.base import LLMConfig
from .rag.chunker import ChunkConfig, TextChunker
from .rag.loader import DocumentLoader
from .rag.vectorstore import FAISSVectorStore, MilvusVectorStore, FAISSVectorStoreConfig, MilvusVectorStoreConfig

def load_documents(docs_dir: str, output_dir: str = "data/vectorstore", recursive: bool = False, config: Dict = None):
    """Load documents into the vector store.

    Args:
        docs_dir: Directory containing documents to load
        output_dir: Directory to save vector store
        recursive: Whether to recursively search for documents
        config: Configuration dictionary
    """
    # Initialize components
    chunker = TextChunker(ChunkConfig(
        chunk_size=config["retrieval"]["chunk_size"],
        chunk_overlap=config["retrieval"]["chunk_overlap"]
    ))

    # Initialize vector store based on configuration
    vector_store_type = config["retrieval"]["vector_store"].get("type", "faiss").lower()
    vector_store_dimension = config["retrieval"]["vector_store"]["dimension"]
    vector_store_top_k = config["retrieval"]["top_k"]
    
    if vector_store_type == "faiss":
        vector_store = FAISSVectorStore(FAISSVectorStoreConfig(
            dimension=vector_store_dimension,
            index_type=config["retrieval"]["vector_store"]["index_type"],
            top_k=vector_store_top_k
        ))
    elif vector_store_type == "milvus":
        # Get Milvus-specific configuration
        milvus_config = MilvusVectorStoreConfig(
            dimension=vector_store_dimension,
            top_k=vector_store_top_k,
            index_type=config["retrieval"]["vector_store"].get("index_type", "L2")
        )
        
        # Add additional Milvus parameters if specified in config
        milvus_section = config["retrieval"]["vector_store"].get("milvus", {})
        if milvus_section:
            if "uri" in milvus_section:
                milvus_config.uri = milvus_section["uri"]
            if "user" in milvus_section:
                milvus_config.user = milvus_section["user"]
            if "password" in milvus_section:
                milvus_config.password = milvus_section["password"]
            if "db_name" in milvus_section:
                milvus_config.db_name = milvus_section["db_name"]
            if "collection_name" in milvus_section:
                milvus_config.collection_name = milvus_section["collection_name"]
            if "token" in milvus_section:
                milvus_config.token = milvus_section["token"]
            if "timeout" in milvus_section:
                milvus_config.timeout = milvus_section["timeout"]
        
        vector_store = MilvusVectorStore(milvus_config)
    else:
        raise ValueError(f"Unsupported vector store type: {vector_store_type}. Choose 'faiss' or 'milvus'.")

    click.echo(f"Using vector store: {vector_store_type}")

    # Initialize LLM client for embeddings
    provider = config["llm"]["provider"].lower()
    LLM_PROVIDERS = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient
    }
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    embedding_model = config["llm"].get("embedding_model", config["llm"]["model"])
    click.echo(f"Using embedding model: {embedding_model}")

    llm_config = LLMConfig(
        model=embedding_model,
        temperature=config["llm"]["temperature"]
    )

    if provider == "ollama":
        llm_config.extra_params = {
            "base_url": "http://localhost:11434",
            "embedding_model": embedding_model,
            "system_prompt": config["llm"].get("system_prompt", "")
        }

    llm_client = LLM_PROVIDERS[provider](llm_config)

    # Initialize document loader
    loader = DocumentLoader()

    # Find documents
    docs_path = Path(docs_dir)
    pattern = "**/*" if recursive else "*"
    files = list(docs_path.glob(pattern))
    click.echo(f"Found {len(files)} files")

    # Process documents
    total_chunks = 0

    # Create progress bars
    file_progress = tqdm(total=len(files), desc="Processing files", unit="file",
                        position=0, leave=True, ncols=100)
    chunk_progress = None

    try:
        for file in files:
            # Load and process document
            docs = loader.load(str(file))
            chunks = []

            # Collect all chunks first
            for doc in docs:
                doc_chunks = chunker.split(doc)
                chunks.extend(doc_chunks)
                total_chunks += len(doc_chunks)

            # Update or create chunk progress bar
            if chunk_progress is not None:
                chunk_progress.close()
            chunk_progress = tqdm(total=len(chunks), desc=f"Processing {file.name}",
                                unit="chunk", position=1, leave=False, ncols=100)

            # Process chunks
            for chunk in chunks:
                embedding = asyncio.run(llm_client.embed([chunk.content]))[0]
                chunk.embedding = embedding
                vector_store.add_documents([chunk])
                chunk_progress.update(1)

            file_progress.update(1)
            file_progress.set_postfix({"total_chunks": total_chunks}, refresh=True)

    finally:
        # Clean up progress bars
        if chunk_progress is not None:
            chunk_progress.close()
        file_progress.close()

    click.echo(f"\nProcessed {total_chunks} chunks from {len(files)} files")

    # Save vector store
    os.makedirs(output_dir, exist_ok=True)
    vector_store.save(output_dir)