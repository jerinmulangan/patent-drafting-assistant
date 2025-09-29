import json
from pathlib import Path
from argparse import ArgumentParser
from typing import List, Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROCESSED_DIR = Path("./data/processed")
CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"
TFIDF_DIR = PROCESSED_DIR / "tfidf"
TFIDF_DIR.mkdir(parents=True, exist_ok=True)


def load_texts(source_file: Path) -> Tuple[List[str], List[str]]:
    texts: List[str] = []
    ids: List[str] = []
    with open(source_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            text = item.get("text", "").strip()
            if not text:
                continue
            item_id = item.get("chunk_id") or item.get("doc_id")
            texts.append(text)
            ids.append(str(item_id))
    return ids, texts


def build_tfidf(ids: List[str], texts: List[str], max_features: int = 100000) -> Tuple[TfidfVectorizer, any]:
    vectorizer = TfidfVectorizer(max_features=max_features)
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def save_index(vectorizer: TfidfVectorizer, matrix, ids: List[str]) -> None:
    import pickle
    with open(TFIDF_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(TFIDF_DIR / "matrix.npz", "wb") as f:
        # save as scipy sparse
        import scipy.sparse as sp
        sp.save_npz(f, matrix)
    with open(TFIDF_DIR / "ids.json", "w", encoding="utf-8") as f:
        json.dump(ids, f)


def load_index():
    import pickle
    import scipy.sparse as sp
    with open(TFIDF_DIR / "vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open(TFIDF_DIR / "matrix.npz", "rb") as f:
        matrix = sp.load_npz(f)
    with open(TFIDF_DIR / "ids.json", "r", encoding="utf-8") as f:
        ids = json.load(f)
    return vectorizer, matrix, ids


def search(query: str, top_k: int = 5, include_metadata: bool = False) -> List[Tuple[str, float]]:
    vectorizer, matrix, ids = load_index()
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, matrix).ravel()
    top_idx = sims.argsort()[::-1][:top_k]
    return [(ids[i], float(sims[i])) for i in top_idx]


def search_with_metadata(query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search with metadata included in results."""
    from search_utils import load_patent_metadata, get_chunk_text
    
    # Get basic search results
    results = search(query, top_k=top_k)
    metadata = load_patent_metadata()
    
    # Enrich results with metadata
    enriched_results = []
    for doc_id, score in results:
        # Get base document metadata
        base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
        base_meta = metadata.get(base_doc_id, {})
        
        # Get chunk text
        chunk_text = get_chunk_text(doc_id)
        
        # Combine metadata
        result_metadata = {
            "title": base_meta.get("title", "No title"),
            "doc_type": base_meta.get("doc_type", "unknown"),
            "source_file": base_meta.get("source_file", ""),
            "chunk_text": chunk_text or "",
            "base_doc_id": base_doc_id
        }
        
        enriched_results.append((doc_id, score, result_metadata))
    
    return enriched_results


if __name__ == "__main__":
    parser = ArgumentParser(description="Build or query TF-IDF over preprocessed patent text")
    parser.add_argument("action", choices=["build", "search"], help="Build index or run a search")
    parser.add_argument("--source", default=str(CHUNKS_FILE), help="Path to JSONL with 'text' and ids")
    parser.add_argument("--max_features", type=int, default=100000, help="Max features for TF-IDF")
    parser.add_argument("--query", type=str, default="", help="Query text for search")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    args = parser.parse_args()

    if args.action == "build":
        src = Path(args.source)
        ids, texts = load_texts(src)
        vectorizer, matrix = build_tfidf(ids, texts, max_features=args.max_features)
        save_index(vectorizer, matrix, ids)
        print(f"TF-IDF index built with {len(ids)} items and saved to {TFIDF_DIR}")
    else:
        if not args.query:
            raise SystemExit("--query is required for search")
        results = search(args.query, top_k=args.top_k)
        for rank, (item_id, score) in enumerate(results, start=1):
            print(f"{rank}. {item_id}\t{score:.4f}")



