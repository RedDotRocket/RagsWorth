import json
import os
import pickle
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np

from pymilvus import MilvusClient

from ..pipeline import Document
from ..config.logging_config import get_logger

logger = get_logger("rag.vectorstore")

@dataclass
class FAISSVectorStoreConfig:
    """Configuration for vector store."""
    dimension: int = 384  # Default for sentence-transformers
    index_type: str = "L2"  # L2 or cosine
    top_k: int = 3

@dataclass
class MilvusVectorStoreConfig:
    """Configuration for vector store."""
    uri: str = "http://localhost:19530"
    user: str = ""
    password: str = ""
    db_name: str = "default"
    token: str = ""
    timeout: int = 10
    collection_name: str = "document_store"
    dimension: int = 384
    top_k: int = 3
    index_type: str = "L2"  # "L2" or "IP" or "COSINE"

class MilvusVectorStore:
    """Vector store implementation using Milvus."""

    def __init__(self, config: MilvusVectorStoreConfig):
        self.config = config
        self.client = self._create_client()
        self.documents: Dict[str, Document] = {}
        self.id_mapping: Dict[int, str] = {}  # Map numeric IDs to document IDs
        self.next_id = 1  # Auto-incrementing ID for documents
        self._ensure_collection_exists()

    def _create_client(self) -> MilvusClient:
        """Create a Milvus client based on configuration."""
        return MilvusClient(
            uri=self.config.uri,
            user=self.config.user,
            password=self.config.password,
            db_name=self.config.db_name,
            token=self.config.token,
            timeout=self.config.timeout
        )

    def _ensure_collection_exists(self) -> None:
        """Ensure the collection exists, create it if it doesn't."""
        # print the collection
        logger.info(f"Checking for collection: {self.config.collection_name}")
        collections = self.client.list_collections()
        if self.config.collection_name not in collections:
            # Create the collection with proper dimension and index type
            self.client.create_collection(
                collection_name=self.config.collection_name,
                dimension=self.config.dimension,
                metric_type="L2" if self.config.index_type == "L2" else "COSINE",
                description="Document embeddings collection"
            )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents and their embeddings to the store."""
        if not documents:
            return

        # Prepare data for insertion
        data = []
        for doc in documents:
            if doc.embedding is None:
                raise ValueError(f"Document {doc.id} has no embedding")

            # Store document in local cache
            self.documents[doc.id] = doc

            # Assign a numeric ID for Milvus
            numeric_id = self.next_id
            self.id_mapping[numeric_id] = doc.id
            self.next_id += 1

            # Prepare data for Milvus
            data.append({
                "id": numeric_id,
                "vector": doc.embedding,
                "metadata": json.dumps({
                    "doc_id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata
                })
            })

        # Insert into Milvus
        if data:
            try:
                _res = self.client.insert(
                    collection_name=self.config.collection_name,
                    data=data
                )
                logger.info(f"Inserted {len(data)} documents into Milvus")
                # The response is now a list of primary keys
                # Don't print individual insertions to avoid cluttering the output
            except Exception as e:
                logger.error(f"Error inserting documents: {e}", exc_info=True)
                raise

    def search(self, query_embedding: List[float], top_k: Optional[int] = None) -> List[Tuple[Document, float]]:
        """Search for most similar documents."""
        k = top_k or self.config.top_k

        try:
            # Make sure the collection exists
            collections = self.client.list_collections()
            if self.config.collection_name not in collections:
                logger.warning(f"Collection '{self.config.collection_name}' doesn't exist")
                return []

            # Set search parameters based on index type
            search_params = {}
            if self.config.index_type.lower() == "l2":
                search_params = {"metric_type": "L2"}
            elif self.config.index_type.lower() == "ip":
                search_params = {"metric_type": "IP"}
            elif self.config.index_type.lower() == "cosine":
                search_params = {"metric_type": "COSINE"}

            logger.debug(f"Searching with params: {search_params}")

            # Try both with search params and without to see which works
            try:
                # Execute the search with params
                search_results = self.client.search(
                    collection_name=self.config.collection_name,
                    data=[query_embedding],
                    output_fields=["metadata"],
                    search_params=search_params,
                    limit=k
                )
            except Exception as e:
                logger.warning(f"Search with params failed: {e}, trying without params")
                # Fall back to search without params
                search_results = self.client.search(
                    collection_name=self.config.collection_name,
                    data=[query_embedding],
                    output_fields=["metadata"],
                    limit=k
                )

            logger.debug(f"Raw Milvus search results type: {type(search_results)}")

            # If we couldn't get search results, try a basic query
            if not search_results or not hasattr(search_results, "get") or not search_results.get("data"):
                logger.info("Search returned no results, trying simple query instead")
                try:
                    # Try getting a few documents via direct query
                    sample_entities = self.client.query(
                        collection_name=self.config.collection_name,
                        filter="",
                        output_fields=["id", "metadata"],
                        limit=k
                    )

                    if sample_entities:
                        logger.info(f"Direct query returned {len(sample_entities)} documents")
                        # Process sample entities similarly to search results
                        results = []
                        for entity in sample_entities:
                            metadata_str = entity.get("metadata")
                            if metadata_str:
                                try:
                                    metadata_json = json.loads(metadata_str)
                                    doc_id = metadata_json.get("doc_id")
                                    content = metadata_json.get("content")
                                    metadata = metadata_json.get("metadata", {})

                                    if doc_id and doc_id in self.documents:
                                        # Use document from cache
                                        doc = self.documents[doc_id]
                                        results.append((doc, 0.7))  # Moderate score since not from search
                                    elif content:
                                        # Create document from metadata
                                        doc = Document(
                                            id=doc_id or f"doc_{len(results)}",
                                            content=content,
                                            metadata=metadata,
                                            embedding=None,
                                            score=0.7
                                        )
                                        results.append((doc, 0.7))
                                except json.JSONDecodeError:
                                    logger.error(f"Error decoding metadata: {metadata_str}")

                        logger.info(f"Processed {len(results)} documents from direct query")
                        return results
                except Exception as e:
                    logger.error(f"Direct query failed: {e}", exc_info=True)

                # If we still have no results, return empty list
                return []

            results = []
            if "data" in search_results and search_results["data"]:
                # Extract results from the search response
                hits = search_results["data"][0]

                logger.debug(f"Number of hits: {len(hits)}")

                if isinstance(hits, str):
                    # In some versions of the client, the result might be a string that needs to be evaluated
                    hits = eval(hits)

                for hit in hits:
                    logger.debug(f"Processing hit: {hit}")

                    # Extract score/distance
                    if "distance" in hit:
                        # Convert distance to score (lower distance is better)
                        distance = hit["distance"]
                        # Normalize the score (invert and scale since lower distance is better)
                        score = 1.0 / (1.0 + distance / 1000.0)
                    elif "score" in hit:
                        score = hit["score"]
                    else:
                        score = 0.5  # Default score

                    # Get document ID and metadata
                    doc_id = None
                    content = None
                    metadata = {}

                    # Process metadata string from the hit
                    metadata_str = None
                    if "entity" in hit and "metadata" in hit["entity"]:
                        metadata_str = hit["entity"]["metadata"]
                    elif "metadata" in hit:
                        metadata_str = hit["metadata"]

                    if metadata_str:
                        try:
                            # Parse metadata
                            metadata_json = json.loads(metadata_str)
                            doc_id = metadata_json.get("doc_id")
                            content = metadata_json.get("content")
                            metadata = metadata_json.get("metadata", {})

                            # If document is in local cache, use that
                            if doc_id and doc_id in self.documents:
                                doc = self.documents[doc_id]
                                doc.score = score
                                results.append((doc, score))
                                logger.debug(f"Found document in cache: {doc_id}")
                            elif content:  # Otherwise create new document from content
                                doc = Document(
                                    id=doc_id or f"doc_{len(results)}",
                                    content=content,
                                    metadata=metadata,
                                    embedding=None,
                                    score=score
                                )
                                results.append((doc, score))
                                logger.debug(f"Created document from metadata: {doc_id}")
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding metadata JSON: {e}")
                    else:
                        logger.warning("No metadata found in hit")

            logger.info(f"Returning {len(results)} search results")
            return results

        except Exception as e:
            logger.error(f"Error searching documents: {e}", exc_info=True)
            return []

    def save(self, directory: str) -> None:
        """Save the vector store to disk.

        Note: This only saves the local document cache, as Milvus itself
        is a separate service that persists its own data.
        """
        os.makedirs(directory, exist_ok=True)

        # Save documents and ID mapping
        with open(os.path.join(directory, "milvus_documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)

        with open(os.path.join(directory, "milvus_id_mapping.pkl"), "wb") as f:
            pickle.dump({
                "id_mapping": self.id_mapping,
                "next_id": self.next_id
            }, f)

        # Save config
        with open(os.path.join(directory, "milvus_config.json"), "w") as f:
            json.dump({
                "uri": self.config.uri,
                "user": self.config.user,
                "password": self.config.password,
                "db_name": self.config.db_name,
                "token": self.config.token,
                "timeout": self.config.timeout,
                "collection_name": self.config.collection_name,
                "dimension": self.config.dimension,
                "top_k": self.config.top_k
            }, f)

    @classmethod
    def load(cls, directory: str) -> "MilvusVectorStore":
        """Load a vector store from disk."""
        # Load config
        with open(os.path.join(directory, "milvus_config.json"), "r") as f:
            config = MilvusVectorStoreConfig(**json.load(f))

        # Create instance
        store = cls(config)

        # Load documents
        with open(os.path.join(directory, "milvus_documents.pkl"), "rb") as f:
            store.documents = pickle.load(f)

        # Load ID mapping if it exists
        try:
            with open(os.path.join(directory, "milvus_id_mapping.pkl"), "rb") as f:
                mapping_data = pickle.load(f)
                store.id_mapping = mapping_data["id_mapping"]
                store.next_id = mapping_data["next_id"]
        except (FileNotFoundError, KeyError):
            # Handle legacy or missing files
            pass

        return store

    def _close_client(self) -> None:
        """Close the Milvus client connection."""
        # MilvusClient doesn't have an explicit close method
        # as it handles connections internally
        pass

        # Collect embeddings and store documents
class FAISSVectorStore:
    """Vector store implementation using FAISS."""

    def __init__(self, config: FAISSVectorStoreConfig):
        self.config = config
        self.index = self._create_index()
        self.documents: Dict[str, Document] = {}

    def _create_index(self) -> faiss.Index:
        """Create a FAISS index based on configuration."""
        if self.config.index_type == "L2":
            return faiss.IndexFlatL2(self.config.dimension)
        elif self.config.index_type == "cosine":
            return faiss.IndexFlatIP(self.config.dimension)
        else:
            raise ValueError(f"Unsupported index type: {self.config.index_type}")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents and their embeddings to the store."""
        if not documents:
            return

        # Collect embeddings and store documents
        embeddings = []
        for doc in documents:
            if doc.embedding is None:
                raise ValueError(f"Document {doc.id} has no embedding")

            embeddings.append(doc.embedding)
            self.documents[doc.id] = doc

        # Convert to numpy array and add to index
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity if needed
        if self.config.index_type == "cosine":
            faiss.normalize_L2(embeddings_array)

        self.index.add(embeddings_array)

    def search(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """Search for most similar documents."""
        if not self.index.ntotal:
            return []

        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)

        # Normalize for cosine similarity if needed
        if self.config.index_type == "cosine":
            faiss.normalize_L2(query_array)

        # Search index
        k = top_k or self.config.top_k
        distances, indices = self.index.search(query_array, k)

        # Map results to documents
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # FAISS returns -1 for empty slots
                doc_id = list(self.documents.keys())[idx]
                doc = self.documents[doc_id]

                # Convert distance to score (1 - normalized distance)
                score = 1.0 - (distance / 2.0) if self.config.index_type == "cosine" else 1.0 / (1.0 + distance)

                results.append((doc, score))

        return results

    def save(self, directory: str) -> None:
        """Save the vector store to disk."""
        os.makedirs(directory, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, os.path.join(directory, "index.faiss"))

        # Save documents
        with open(os.path.join(directory, "documents.pkl"), "wb") as f:
            pickle.dump(self.documents, f)

        # Save config
        with open(os.path.join(directory, "config.json"), "w") as f:
            json.dump({
                "dimension": self.config.dimension,
                "index_type": self.config.index_type,
                "top_k": self.config.top_k
            }, f)

    @classmethod
    def load(cls, directory: str) -> "FAISSVectorStore":
        """Load a vector store from disk."""
        # Load config
        with open(os.path.join(directory, "config.json"), "r") as f:
            config = FAISSVectorStoreConfig(**json.load(f))

        # Create instance
        store = cls(config)

        # Load FAISS index
        store.index = faiss.read_index(os.path.join(directory, "index.faiss"))

        # Load documents
        with open(os.path.join(directory, "documents.pkl"), "rb") as f:
            store.documents = pickle.load(f)

        return store
