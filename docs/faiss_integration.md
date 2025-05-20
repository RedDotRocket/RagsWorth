# Integrating RagsWorth with FAISS Vector Store

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search and clustering of dense vectors. It is an excellent choice for embedding-based retrieval when you need a local, file-based vector store without managing a separate database service.

## 1. Prerequisites

### a. Install FAISS Python SDK

RagsWorth interacts with FAISS using its Python bindings. The necessary FAISS package (`faiss-cpu` or `faiss-gpu`) should be managed as a dependency in your `pyproject.toml` file.

*   **CPU Version (Default):**
    Your `pyproject.toml` should include `faiss-cpu` as a dependency. If RagsWorth is set up according to its installation instructions, this should already be handled.
    Example (conceptual, actual syntax depends on your `pyproject.toml` structure, e.g., under `[tool.poetry.dependencies]` or `[project.dependencies]`):
    ```toml
    # In pyproject.toml
    # faiss-cpu = "^1.7.4" # Or the appropriate version
    ```

*   **GPU Version (Optional):**
    If you have a compatible NVIDIA GPU and require GPU acceleration, you can switch to `faiss-gpu`. This typically involves:
    1.  Ensuring you have the necessary NVIDIA drivers and CUDA toolkit installed on your system.
    2.  Modifying your `pyproject.toml` to specify `faiss-gpu` instead of `faiss-cpu`.
        ```toml
        # In pyproject.toml (replace faiss-cpu with faiss-gpu)
        # faiss-gpu = "^1.7.4" # Or the appropriate version for your CUDA version
        ```
    3.  Re-installing/updating your environment based on the modified `pyproject.toml` (e.g., `uv pip install -e .` or `poetry install`).

    **Note:** `faiss-gpu` often has specific version requirements tied to your CUDA toolkit version. Consult the [FAISS GitHub repository](https://github.com/facebookresearch/faiss/blob/main/INSTALL.md) for detailed installation instructions and compatibility.

Ensure your Python environment is updated after any changes to `pyproject.toml` by running your project's installation command (e.g., `uv pip install -e .` or `poetry install`).

## 2. Configure RagsWorth for FAISS

Modify your RagsWorth `config.yaml` file to specify FAISS as the vector store and provide its configuration.

```yaml
llm:
  provider: ollama
  model: gemma:7b
  embedding_model: nomic-embed-text # Or your chosen embedding model
  temperature: 0.7

retrieval:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3 # Number of documents to retrieve

  vector_store:
    type: faiss                      # REQUIRED: Set to "faiss"
    dimension: 768                   # REQUIRED: Output dimension of your embedding_model
                                     # (e.g., nomic-embed-text: 768, OpenAI text-embedding-3-small: 1536)
    index_type: "L2"                 # Optional: "L2" (Euclidean) or "cosine" (Cosine Similarity via IndexFlatIP)
                                     # Default is "L2" if not specified.
    # top_k: 3                       # Optional: Can also be specified here, overrides retrieval.top_k for FAISS

# ... other RagsWorth configurations (security, server)
```

### Key Configuration Parameters:

*   `type: "faiss"`: Tells RagsWorth to use the `FAISSVectorStore` implementation.
*   `dimension`: **CRITICAL!** This integer value *must* exactly match the output dimension of the embedding model specified in `llm.embedding_model`.
    *   Example Dimensions:
        *   `nomic-embed-text` (default in Ollama): 768
        *   `sentence-transformers/all-mpnet-base-v2`: 768
        *   OpenAI `text-embedding-3-small`: 1536
        *   OpenAI `text-embedding-3-large`: 3072
        *   OpenAI `text-embedding-ada-002`: 1536
    *   An incorrect dimension will lead to errors during document loading or search.
*   `index_type`: (Optional) Specifies the type of FAISS index to use.
    *   `"L2"`: Uses `IndexFlatL2` for Euclidean distance. Lower distance means more similar. This is the default.
    *   `"cosine"`: Uses `IndexFlatIP` (Inner Product). If embeddings are normalized (which RagsWorth does for this option), inner product becomes cosine similarity. Higher similarity score (closer to 1) means more similar.
*   `top_k`: (Optional) The number of top similar documents to retrieve. If set here, it can override the global `retrieval.top_k` specifically for FAISS.

## 3. Understanding FAISS Data Storage

When using `FAISSVectorStore` with RagsWorth:

*   The FAISS index itself (containing the vectors) is saved to a file named `index.faiss` in the output directory specified during document loading (default: `data/vectorstore/`).
*   Document metadata (ID, original text content, source, etc.) is saved in a separate file named `documents.pkl` in the same directory.
*   A `config.json` file is also saved, storing the FAISS configuration (`dimension`, `index_type`, `top_k`, and `store_type: "faiss"`).

This means your FAISS vector store is entirely file-based and portable by copying this directory.

## 4. Loading Documents into FAISS

Once FAISS is installed and RagsWorth is configured, you can load your documents:

```bash
ragsworth load path/to/your/docs --config config.yaml
```

This script will:
1.  Read the `config.yaml`.
2.  Recognize that `vector_store.type` is `faiss` (or default to it if no type is specified).
3.  Initialize `FAISSVectorStore` using the provided configuration.
4.  Process your documents, generate embeddings using the configured LLM embedding model, and add them to the FAISS index.
5.  Save the FAISS index, document metadata, and configuration to the output directory (e.g., `data/vectorstore/`).

You should see output indicating the progress and successful saving of the FAISS store.

## 5. Verification

*   **Check Output Directory:** After running `load_documents.py`, inspect the output directory (e.g., `data/vectorstore/`). You should find:
    *   `index.faiss`
    *   `documents.pkl`
    *   `config.json` (with `"store_type": "faiss"`)
*   **Application Behavior:** When RagsWorth starts, it will load this FAISS store and use it for retrieval. Test the chat functionality to ensure it's fetching relevant documents.

## 6. Troubleshooting Common Issues

*   **Installation Issues:**
    *   `faiss-gpu` can be tricky to install due to CUDA dependencies. `faiss-cpu` is generally easier.
    *   Ensure you are installing into the correct Python environment used by RagsWorth.
*   **Dimension Mismatch:**
    *   Errors during `add_documents` or `search` (often NumPy shape errors or FAISS internal errors) can indicate a mismatch between `vector_store.dimension` in `config.yaml` and the actual output dimension of your `llm.embedding_model`. Double-check both.
*   **File Permissions:**
    *   Ensure RagsWorth has write permissions to the output directory when saving the FAISS index and read permissions when loading it.

## 7. Data Persistence and Backup

*   Since FAISS stores data as files, persistence is achieved by keeping these files (`index.faiss`, `documents.pkl`, `config.json`).
*   Backup is straightforward: simply back up the directory containing these files.

By following these steps, you can effectively leverage FAISS as a simple and efficient local vector store for your RagsWorth application.