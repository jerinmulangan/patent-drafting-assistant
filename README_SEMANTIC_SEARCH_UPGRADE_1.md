This document summarizes the upgrade from TF-IDF keyword search to semantic embeddings and FAISS-based similarity search.

## Overview

The search system now supports:

- **TF-IDF Search** – keyword-based matching
- **Semantic Search** – embedding-based similarity using `sentence-transformers`
- **Hybrid Search** – combines TF-IDF and semantic scores
- **Advanced Hybrid** – weighted combination for fine-tuned results

## Implementation Summary

1. **Dependencies Installed**
    - `sentence-transformers`, `faiss-cpu`, `scikit-learn`
2. **Data Loading**
    - Uses preprocessed `grants.jsonl` and `applications.jsonl`
    - Combines title, abstract, claims, and description into text chunks
3. **Semantic Embeddings**
    - Uses `all-MiniLM-L6-v2` (384-dimensional)
    - Normalized embeddings for cosine similarity
4. **FAISS Index**
    - Built with `IndexFlatIP` (inner product)
    - Saved to disk with metadata for efficient reuse
5. **Semantic Search**
    - Encodes query, performs similarity search in FAISS index
    - Returns document IDs, scores, and metadata
6. **CLI Integration**
    - `search_cli.py` now supports `--mode tfidf | semantic | hybrid | hybrid-advanced`
7. **Testing and Comparison**
    - Benchmarked TF-IDF vs semantic vs hybrid modes
    - Validated that semantic search finds relevant results even without keyword overlap

## New Files

| File                      | Description                                                 |
| ------------------------- | ----------------------------------------------------------- |
| `embed_semantic.py`       | Builds embeddings and FAISS index, performs semantic search |
| `embed_hybrid.py`         | Combines TF-IDF and semantic results                        |
| `setup_indices.py`        | Builds TF-IDF and semantic indices together                 |
| `compare_search_modes.py` | Runs side-by-side comparisons                               |
| `demo_upgrade.py`         | Runs a full demonstration of all search modes               |

## Usage

### Build Indices

`# TF-IDF index python embed_tfidf.py build  # Semantic index python embed_semantic.py build  # Or build both python setup_indices.py`

### Run Searches

`# TF-IDF search python search_cli.py "machine learning" --mode tfidf  # Semantic search python search_cli.py "machine learning" --mode semantic  # Hybrid search python search_cli.py "machine learning" --mode hybrid`

### Demo

`python demo_upgrade.py`

## Performance Notes

- **TF-IDF** – fast, good for exact matches
- **Semantic** – slower, better for conceptually similar results
- **Hybrid** – balances precision and recall, generally best overall

## Future Work

- Explore GPU acceleration (`faiss-gpu`)
- Add multilingual support
- Improve ranking with query expansion
- Support incremental indexing for new data