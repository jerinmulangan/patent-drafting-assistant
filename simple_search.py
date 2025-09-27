#!/usr/bin/env python3
"""Simple working search script for testing."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_tfidf_search():
    # test tfidf search
    print("Testing TF-IDF search")
    try:
        from embed_tfidf import search as search_tfidf
        results = search_tfidf("machine learning", top_k=3)
        print(f"Found {len(results)} results:")
        for rank, (doc_id, score) in enumerate(results, 1):
            print(f"{rank}. {doc_id}\t{score:.4f}")
        return True
    except Exception as e:
        print(f"TF-IDF Error: {e}")
        return False

def test_semantic_search():
    # test semantic search
    print("\nTesting semantic search")
    try:
        from embed_semantic import search_semantic
        results = search_semantic("machine learning", top_k=3)
        print(f"Found {len(results)} results:")
        for rank, (doc_id, score, meta) in enumerate(results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"{rank}. {doc_id}\t{score:.4f}\t{title}")
        return True
    except Exception as e:
        print(f"Semantic Error: {e}")
        return False

def build_semantic_index():
    # build semantic index
    print("Building semantic index")
    try:
        from embed_semantic import build_semantic_index
        build_semantic_index()
        print("Semantic index built successfully")
        return True
    except Exception as e:
        print(f"Build Error: {e}")
        return False

if __name__ == "__main__":
    print("Patent Search System Test")
 
    
    # Test TF-IDF
    tfidf_ok = test_tfidf_search()
    
    # Build semantic index if needed
    semantic_dir = Path("./data/processed/semantic")
    if not semantic_dir.exists() or not (semantic_dir / "faiss_index.bin").exists():
        print("\nBuilding semantic index.")
        build_ok = build_semantic_index()
        if not build_ok:
            print("Failed to build semantic index")
            sys.exit(1)
    
    # Test semantic search
    semantic_ok = test_semantic_search()
    

    print("Test Summary:")
    print(f"TF-IDF: {'Worked' if tfidf_ok else 'Did not work'}")
    print(f"Semantic: {'Worked' if semantic_ok else 'Did not work'}")
    
    if tfidf_ok and semantic_ok:
        print("\nAll tests passed - Usage:")
        print("  python search_cli.py 'your query' --mode tfidf")
        print("  python search_cli.py 'your query' --mode semantic")
        print("  python search_cli.py 'your query' --mode hybrid")
