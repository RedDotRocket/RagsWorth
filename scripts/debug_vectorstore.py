#!/usr/bin/env python3
"""
Debug script to test vector store loading and querying.
"""
import os
import sys
import yaml
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ragsworth.rag.vectorstore import FAISSVectorStore, MilvusVectorStore
from ragsworth.llm.base import LLMConfig
from ragsworth.llm import OpenAIClient, AnthropicClient, OllamaClient

# Load configuration
def load_config():
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

def main():
    print("=== Vector Store Debugging ===")
    
    # Load the configuration
    config = load_config()
    print(f"Loaded configuration from config.yaml")
    
    # Get vector store configuration
    vector_store_path = os.path.join(project_root, "data/vectorstore")
    vector_store_type = config["retrieval"]["vector_store"].get("type", "faiss").lower()
    print(f"Vector store type: {vector_store_type}")
    print(f"Vector store path: {vector_store_path}")
    print(f"Directory exists: {os.path.exists(vector_store_path)}")
    
    if os.path.exists(vector_store_path):
        print(f"Directory contents: {os.listdir(vector_store_path)}")
    
    # Try to load the vector store
    try:
        if vector_store_type == "faiss":
            print("Loading FAISS vector store...")
            vector_store = FAISSVectorStore.load(vector_store_path)
        elif vector_store_type == "milvus":
            print("Loading Milvus vector store...")
            vector_store = MilvusVectorStore.load(vector_store_path)
        else:
            print(f"Unsupported vector store type: {vector_store_type}")
            return
        
        print(f"Successfully loaded {type(vector_store).__name__}")
        print(f"Number of documents: {len(vector_store.documents)}")
        
        # Initialize LLM client for embeddings
        provider = config["llm"]["provider"].lower()
        print(f"LLM provider: {provider}")
        
        # Map of provider names to client classes
        LLM_PROVIDERS = {
            "openai": OpenAIClient,
            "anthropic": AnthropicClient,
            "ollama": OllamaClient
        }
        
        if provider not in LLM_PROVIDERS:
            print(f"Unsupported LLM provider: {provider}")
            return
        
        llm_config = LLMConfig(
            model=config["llm"]["model"],
            temperature=config["llm"]["temperature"]
        )
        
        if provider == "ollama":
            embedding_model = config["llm"].get("embedding_model")
            llm_config.extra_params = {
                "base_url": "http://localhost:11434",
                "embedding_model": embedding_model
            }
        
        print(f"Creating LLM client with {provider}...")
        llm_client = LLM_PROVIDERS[provider](llm_config)
        
        # Test a simple query
        import asyncio
        
        print("\n=== Testing vector store search ===")
        test_query = "What is RagsWorth?"
        print(f"Test query: '{test_query}'")
        
        async def test_search():
            # Generate embedding for query
            print("Generating embedding...")
            query_embedding = await llm_client.embed([test_query])
            print(f"Embedding generated, dimension: {len(query_embedding[0])}")
            
            # Search for relevant documents
            print("Searching vector store...")
            results = vector_store.search(query_embedding[0])
            print(f"Search returned {len(results)} documents")
            
            if results:
                print("\nTop results:")
                for i, (doc, score) in enumerate(results[:3]):
                    print(f"Result {i+1} - Score: {score}")
                    print(f"Content: {doc.content[:200]}...")
                    print("-" * 50)
            else:
                print("No results found!")
                
            if vector_store_type == "milvus":
                # Check if the collection exists and has documents
                print("\n=== Milvus Collection Info ===")
                if hasattr(vector_store, 'client'):
                    collection_name = vector_store.config.collection_name
                    has_collection = vector_store.client.has_collection(collection_name)
                    print(f"Collection '{collection_name}' exists: {has_collection}")
                    
                    if has_collection:
                        collection_stats = vector_store.client.get_collection_stats(collection_name)
                        print(f"Collection stats: {collection_stats}")
                        entities = vector_store.client.query(
                            collection_name=collection_name,
                            filter="",
                            limit=5
                        )
                        print(f"Sample entities: {len(entities)} found")
                        if entities:
                            print(f"First entity: {entities[0]}")
            
        asyncio.run(test_search())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 