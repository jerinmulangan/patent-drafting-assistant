import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from argparse import ArgumentParser
from sentence_transformers import SentenceTransformer
import faiss


PROCESSED_DIR = Path("./data/processed")
CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"
SEMANTIC_DIR = PROCESSED_DIR / "semantic"
SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)

# Model configuration
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast and lightweight model
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2


def load_texts_and_metadata(source_file: Path) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """Load texts and metadata from JSONL file."""
    texts: List[str] = []
    ids: List[str] = []
    metadata: List[Dict[str, Any]] = []
    
    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            text = item.get("text", "").strip()
            if not text:
                continue
                
            item_id = item.get("chunk_id") or item.get("doc_id")
            texts.append(text)
            ids.append(str(item_id))
            
            # Store metadata for later lookup
            metadata.append({
                "doc_id": item.get("doc_id"),
                "chunk_id": item.get("chunk_id"),
                "title": item.get("title", ""),
                "source_file": item.get("source_file", "")
            })
    
    return ids, texts, metadata


def generate_embeddings(texts: List[str], model_name: str = MODEL_NAME) -> np.ndarray:
    """Generate embeddings for texts using sentence-transformers."""
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"Generating embeddings for {len(texts)} texts...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    # Normalize embeddings for cosine similarity
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    return embeddings


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Build FAISS index for efficient similarity search."""
    dimension = embeddings.shape[1]
    
    # Create IndexFlatIP for inner product (cosine similarity with normalized vectors)
    index = faiss.IndexFlatIP(dimension)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    return index


def save_semantic_index(index: faiss.Index, ids: List[str], metadata: List[Dict], model_name: str) -> None:
    """Save FAISS index and metadata to disk."""
    # Save FAISS index
    faiss.write_index(index, str(SEMANTIC_DIR / "faiss_index.bin"))
    
    # Save IDs and metadata
    with open(SEMANTIC_DIR / "ids.json", "w", encoding="utf-8") as f:
        json.dump(ids, f)
    
    with open(SEMANTIC_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    
    # Save model name for consistency
    with open(SEMANTIC_DIR / "model_name.txt", "w", encoding="utf-8") as f:
        f.write(model_name)
    
    print(f"Semantic index saved to {SEMANTIC_DIR}")


def load_semantic_index() -> Tuple[faiss.Index, List[str], List[Dict], str]:
    """Load FAISS index and metadata from disk."""
    # Load FAISS index
    index = faiss.read_index(str(SEMANTIC_DIR / "faiss_index.bin"))
    
    # Load IDs and metadata
    with open(SEMANTIC_DIR / "ids.json", "r", encoding="utf-8") as f:
        ids = json.load(f)
    
    with open(SEMANTIC_DIR / "metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # Load model name
    with open(SEMANTIC_DIR / "model_name.txt", "r", encoding="utf-8") as f:
        model_name = f.read().strip()
    
    return index, ids, metadata, model_name


def search_semantic(query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search using semantic embeddings."""
    index, ids, metadata, model_name = load_semantic_index()
    
    # Load model and encode query
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query])
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    
    # Search FAISS index
    scores, indices = index.search(query_embedding.astype('float32'), top_k)
    
    # Return results with metadata
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(ids):  # Valid index
            results.append((ids[idx], float(score), metadata[idx]))
    
    return results


def build_semantic_index(source_file: Path = CHUNKS_FILE, model_name: str = MODEL_NAME) -> None:
    """Build semantic index from source file."""
    print(f"Building semantic index from {source_file}")
    
    # Load data
    ids, texts, metadata = load_texts_and_metadata(source_file)
    print(f"Loaded {len(texts)} documents")
    
    # Generate embeddings
    embeddings = generate_embeddings(texts, model_name)
    
    # Build FAISS index
    print("Building FAISS index...")
    index = build_faiss_index(embeddings)
    
    # Save everything
    save_semantic_index(index, ids, metadata, model_name)
    
    print(f"Semantic index built successfully with {len(ids)} documents")


def add_documents_to_index(new_texts: List[str], new_metadata: List[Dict], model_name: str = MODEL_NAME) -> None:
    """Add new documents to existing index (incremental update)."""
    if not (SEMANTIC_DIR / "faiss_index.bin").exists():
        raise FileNotFoundError("No existing semantic index found. Run build first.")
    
    # Load existing index
    index, ids, metadata, stored_model_name = load_semantic_index()
    
    if stored_model_name != model_name:
        raise ValueError(f"Model mismatch: stored {stored_model_name}, requested {model_name}")
    
    # Generate embeddings for new documents
    model = SentenceTransformer(model_name)
    new_embeddings = model.encode(new_texts, show_progress_bar=True, batch_size=32)
    new_embeddings = new_embeddings / np.linalg.norm(new_embeddings, axis=1, keepdims=True)
    
    # Add to FAISS index
    index.add(new_embeddings.astype('float32'))
    
    # Update IDs and metadata
    new_ids = [f"new_{i}" for i in range(len(new_texts))]
    ids.extend(new_ids)
    metadata.extend(new_metadata)
    
    # Save updated index
    save_semantic_index(index, ids, metadata, model_name)
    
    print(f"Added {len(new_texts)} new documents to semantic index")


if __name__ == "__main__":
    parser = ArgumentParser(description="Build or query semantic embeddings using FAISS")
    parser.add_argument("action", choices=["build", "search", "add"], help="Build index, run search, or add documents")
    parser.add_argument("--source", default=str(CHUNKS_FILE), help="Path to JSONL with 'text' and ids")
    parser.add_argument("--model", default=MODEL_NAME, help="Sentence transformer model name")
    parser.add_argument("--query", type=str, default="", help="Query text for search")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    args = parser.parse_args()

    if args.action == "build":
        build_semantic_index(Path(args.source), args.model)
    elif args.action == "add":
        # For adding documents, you'd need to provide new texts and metadata
        print("Add functionality requires programmatic usage")
    else:  # search
        if not args.query:
            raise SystemExit("--query is required for search")
        results = search_semantic(args.query, top_k=args.top_k)
        for rank, (item_id, score, meta) in enumerate(results, start=1):
            title = meta.get("title", "No title")[:50]
            print(f"{rank}. {item_id}\t{score:.4f}\t{title}...")

