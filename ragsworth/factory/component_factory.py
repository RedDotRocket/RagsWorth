import os
from typing import Dict

from ..llm import OpenAIClient, AnthropicClient, OllamaClient
from ..llm.base import LLMConfig
from ..rag.vectorstore import FAISSVectorStore, FAISSVectorStoreConfig, MilvusVectorStore, MilvusVectorStoreConfig
from ..security.pii import PIIConfig, PIIDetector
from ..db.engine import Database
from ..config.logging_config import get_logger

logger = get_logger("factory.component")

class ComponentFactory:
    """Factory for creating RagsWorth components."""

    # Map of provider names to client classes
    LLM_PROVIDERS = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient
    }

    def __init__(self, config: Dict):
        self.config = config
        self.db = self.create_database()

    def create_database(self):
        """Create and configure the database."""
        db_config = self.config["database"]
        # check if db_config sqlite or postgres
        if db_config.get("type") == "postgres":
            db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        else:
            # Default to SQLite
            db_path = db_config.get("sqlite", {}).get("db_path", "ragsworth.sqlite3")
            db_url = f"sqlite:///{db_path}"

        return Database(db_url)

    def create_llm_client(self):
        """Create and configure LLM client."""
        provider = self.config["llm"]["provider"].lower()
        if provider not in self.LLM_PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        chat_model = self.config["llm"]["model"]
        llm_config = LLMConfig(
            model=chat_model,
            temperature=self.config["llm"]["temperature"]
        )

        if provider == "ollama":
            embedding_model = self.config["llm"].get("embedding_model")
            llm_config.extra_params = {
                "base_url": "http://localhost:11434",
                "embedding_model": embedding_model,
                "system_prompt": self.config["llm"].get("system_prompt", "")
            }

        return self.LLM_PROVIDERS[provider](llm_config)

    def create_vector_store(self):
        """Create and configure vector store."""
        vector_store_path = "data/vectorstore"
        vector_store_type = self.config["retrieval"]["vector_store"].get("type", "faiss").lower()
        logger.info(f"Configuring vector store of type: {vector_store_type}")

        if os.path.exists(vector_store_path):
            logger.info(f"Loading vector store from {vector_store_path}")
            logger.debug(f"Directory contents: {os.listdir(vector_store_path)}")

            if vector_store_type == "faiss":
                logger.info("Loading FAISS vector store")
                vector_store = FAISSVectorStore.load(vector_store_path)
            elif vector_store_type == "milvus":
                logger.info("Loading Milvus vector store")
                vector_store = MilvusVectorStore.load(vector_store_path)
            else:
                raise ValueError(f"Unsupported vector store type: {vector_store_type}")

            logger.info(f"Loaded {len(vector_store.documents)} documents from {type(vector_store).__name__}")
        else:
            logger.warning("No vector store found. Please run load_documents.py first.")

            if vector_store_type == "faiss":
                logger.info("Creating new empty FAISS vector store")
                vector_store = FAISSVectorStore(FAISSVectorStoreConfig(
                    dimension=self.config["retrieval"]["vector_store"]["dimension"],
                    index_type=self.config["retrieval"]["vector_store"]["index_type"],
                    top_k=self.config["retrieval"]["top_k"]
                ))
            elif vector_store_type == "milvus":
                logger.info("Creating new empty Milvus vector store")
                # Get Milvus configuration
                milvus_section = self.config["retrieval"]["vector_store"].get("milvus", {})
                milvus_config = MilvusVectorStoreConfig(
                    dimension=self.config["retrieval"]["vector_store"]["dimension"],
                    top_k=self.config["retrieval"]["top_k"],
                    index_type=self.config["retrieval"]["vector_store"].get("index_type", "L2")
                )

                # Add additional Milvus parameters if specified in config
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
                logger.debug(f"Milvus config: uri={milvus_config.uri}, collection={milvus_config.collection_name}")
                vector_store = MilvusVectorStore(milvus_config)
            else:
                raise ValueError(f"Unsupported vector store type: {vector_store_type}")

        logger.info(f"Using vector store type: {type(vector_store).__name__}")
        return vector_store

    def create_pii_detector(self):
        """Create and configure PII detector."""
        return PIIDetector(PIIConfig(
            enabled=self.config["security"]["pii_detection"],
            log_blocked=self.config["security"]["audit_logging"],
            block_types=set(self.config["security"]["block_types"])
        )) 