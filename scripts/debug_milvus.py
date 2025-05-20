#!/usr/bin/env python3
"""
Debug script to specifically test Milvus vector store.
"""
import os
import sys
import yaml
import json
import asyncio
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ragsworth.rag.vectorstore import MilvusVectorStore, MilvusVectorStoreConfig
from ragsworth.llm.base import LLMConfig
from ragsworth.llm import OpenAIClient, AnthropicClient, OllamaClient

# Load configuration
def load_config():
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

async def main():
    print("=== Milvus Vector Store Debug ===")
    
    # Load the configuration
    config = load_config()
    print(f"Configuration loaded from {os.path.join(project_root, 'config.yaml')}")
    
    # Set up vector store
    vector_store_path = os.path.join(project_root, "data/vectorstore")
    print(f"Loading vector store from {vector_store_path}")
    
    # Check if the vector store exists
    if not os.path.exists(vector_store_path):
        print(f"Error: Vector store directory does not exist at {vector_store_path}")
        return
    
    # List all files in the vector store directory
    print(f"Files in vector store directory: {os.listdir(vector_store_path)}")
    
    # Load the Milvus vector store
    try:
        print("Loading Milvus vector store...")
        vector_store = MilvusVectorStore.load(vector_store_path)
        print(f"Loaded vector store with {len(vector_store.documents)} documents")
        
        # Show the first few document IDs
        doc_ids = list(vector_store.documents.keys())
        print(f"Document IDs (first 5): {doc_ids[:5]}")
        
        # Show a sample document
        if doc_ids:
            sample_doc = vector_store.documents[doc_ids[0]]
            print("\nSample document:")
            print(f"  ID: {sample_doc.id}")
            print(f"  Content (first 100 chars): {sample_doc.content[:100]}...")
            print(f"  Metadata: {sample_doc.metadata}")
        
        # Check if Milvus collection exists and get statistics
        print("\nChecking Milvus collection status:")
        if vector_store.client.has_collection(vector_store.config.collection_name):
            print(f"Collection '{vector_store.config.collection_name}' exists")
            try:
                stats = vector_store.client.get_collection_stats(vector_store.config.collection_name)
                print(f"Collection stats: {stats}")
            except Exception as e:
                print(f"Error getting collection stats: {e}")
        else:
            print(f"Collection '{vector_store.config.collection_name}' does not exist")
            
        # Test search with a sample query
        print("\nTesting search with sample query...")
        
        # Set up embedding model
        embedding_model = None
        provider = config["llm"]["provider"].lower()
        
        if provider == "openai":
            llm_config = LLMConfig(
                model=config["llm"]["model"],
                temperature=config["llm"]["temperature"]
            )
            embedding_model = OpenAIClient(llm_config)
        elif provider == "anthropic":
            llm_config = LLMConfig(
                model=config["llm"]["model"],
                temperature=config["llm"]["temperature"]
            )
            embedding_model = AnthropicClient(llm_config)
        elif provider == "ollama":
            embedding_model = config["llm"].get("embedding_model", "nomic-embed-text")
            llm_config = LLMConfig(
                model=config["llm"]["model"],
                temperature=config["llm"]["temperature"],
                extra_params={
                    "base_url": "http://localhost:11434",
                    "embedding_model": embedding_model
                }
            )
            embedding_model = OllamaClient(llm_config)
        
        if embedding_model:
            # Generate embedding for test query
            query = "What new helper functions in ollama?"
            print(f"Test query: '{query}'")
            
            # Embed the query
            embeddings = await embedding_model.embed([query])
            query_embedding = embeddings[0]
            print(f"Generated embedding of dimension {len(query_embedding)}")
            
            # Get start and end of embedding vector
            print(f"Embedding start: {query_embedding[:3]}")
            print(f"Embedding end: {query_embedding[-3:]}")
            
            # Search with the embedding
            print("\nPerforming search...")
            results = vector_store.search(query_embedding)
            
            # Display results
            print(f"Found {len(results)} results")
            for i, (doc, score) in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  Document ID: {doc.id}")
                print(f"  Score: {score}")
                print(f"  Content snippet: {doc.content[:100]}...")
                print(f"  Metadata: {doc.metadata}")
        else:
            print("No embedding model configured, skipping search test")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 