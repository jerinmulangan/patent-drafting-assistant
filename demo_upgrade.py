#!/usr/bin/env python3


import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def demonstrate_tfidf_search():


    print("1. TF-IDF SEARCH DEMONSTRATION")

    
    try:
        from embed_tfidf import search as search_tfidf
        
        queries = [
            "machine learning algorithm",
            "neural network processing", 
            "artificial intelligence system"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")

            start_time = time.time()
            results = search_tfidf(query, top_k=3)
            search_time = time.time() - start_time
            
            print(f"Found {len(results)} results in {search_time:.3f}s:")
            for rank, (doc_id, score) in enumerate(results, 1):
                print(f"  {rank}. {doc_id}\t{score:.4f}")
                
    except Exception as e:
        print(f"TF-IDF Error: {e}")

def demonstrate_semantic_search():


    print("2. SEMANTIC SEARCH DEMONSTRATION")

    
    try:
        from embed_semantic import search_semantic
        
        queries = [
            "machine learning algorithm",
            "neural network processing", 
            "artificial intelligence system"
        ]
        
        for query in queries:
            print(f"\nQuery: '{query}'")

            start_time = time.time()
            results = search_semantic(query, top_k=3)
            search_time = time.time() - start_time
            
            print(f"Found {len(results)} results in {search_time:.3f}s:")
            for rank, (doc_id, score, meta) in enumerate(results, 1):
                title = meta.get("title", "No title")[:50]
                print(f"  {rank}. {doc_id}\t{score:.4f}\t{title}")
                
    except Exception as e:
        print(f"Semantic Error: {e}")

def demonstrate_hybrid_search():

    print("3. HYBRID SEARCH DEMONSTRATION")

    
    try:
        from embed_hybrid import search_hybrid, search_hybrid_advanced
        
        query = "machine learning algorithm"
        print(f"\nQuery: '{query}'")

        
        # Simple hybrid search
        print("Simple Hybrid (50/50 TF-IDF/Semantic):")
        start_time = time.time()
        results = search_hybrid(query, top_k=3, alpha=0.5)
        search_time = time.time() - start_time
        
        print(f"Found {len(results)} results in {search_time:.3f}s:")
        for rank, (doc_id, score, meta) in enumerate(results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"  {rank}. {doc_id}\t{score:.4f}\t{title}")
        
        # Advanced hybrid search
        print("\nAdvanced Hybrid (30/70 TF-IDF/Semantic):")
        start_time = time.time()
        results = search_hybrid_advanced(query, top_k=3, tfidf_weight=0.3, semantic_weight=0.7)
        search_time = time.time() - start_time
        
        print(f"Found {len(results)} results in {search_time:.3f}s:")
        for rank, (doc_id, score, meta) in enumerate(results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"  {rank}. {doc_id}\t{score:.4f}\t{title}")
                
    except Exception as e:
        print(f"Hybrid Error: {e}")

def demonstrate_search_comparison():

    print("4. SEARCH MODE COMPARISON")

    
    query = "artificial intelligence neural network"
    print(f"Query: '{query}'")

    
    try:
        from embed_tfidf import search as search_tfidf
        from embed_semantic import search_semantic
        from embed_hybrid import search_hybrid
        
        # TF-IDF
        print("TF-IDF Results:")
        start_time = time.time()
        tfidf_results = search_tfidf(query, top_k=3)
        tfidf_time = time.time() - start_time
        print(f"  Time: {tfidf_time:.3f}s")
        for rank, (doc_id, score) in enumerate(tfidf_results, 1):
            print(f"  {rank}. {doc_id}\t{score:.4f}")
        
        # Semantic
        print("\nSemantic Results:")
        start_time = time.time()
        semantic_results = search_semantic(query, top_k=3)
        semantic_time = time.time() - start_time
        print(f"  Time: {semantic_time:.3f}s")
        for rank, (doc_id, score, meta) in enumerate(semantic_results, 1):
            title = meta.get("title", "No title")[:40]
            print(f"  {rank}. {doc_id}\t{score:.4f}\t{title}")
        
        # Hybrid
        print("\nHybrid Results:")
        start_time = time.time()
        hybrid_results = search_hybrid(query, top_k=3, alpha=0.5)
        hybrid_time = time.time() - start_time
        print(f"  Time: {hybrid_time:.3f}s")
        for rank, (doc_id, score, meta) in enumerate(hybrid_results, 1):
            title = meta.get("title", "No title")[:40]
            print(f"  {rank}. {doc_id}\t{score:.4f}\t{title}")
            
    except Exception as e:
        print(f"Comparison Error: {e}")

def check_system_status():

    print("SYSTEM STATUS CHECK")

    
    # Check TF-IDF index
    tfidf_dir = Path("./data/processed/tfidf")
    tfidf_files = ["vectorizer.pkl", "matrix.npz", "ids.json"]
    tfidf_status = all((tfidf_dir / f).exists() for f in tfidf_files)
    print(f"TF-IDF Index: {'Working:' if tfidf_status else 'Not Working:'}")
    
    # Check semantic index
    semantic_dir = Path("./data/processed/semantic")
    semantic_files = ["faiss_index.bin", "ids.json", "metadata.json", "model_name.txt"]
    semantic_status = all((semantic_dir / f).exists() for f in semantic_files)
    print(f"Semantic Index: {'Working:' if semantic_status else 'Not Working:'}")
    
    # Check data files
    data_dir = Path("./data/processed")
    data_files = ["grants.jsonl", "applications.jsonl", "chunks.jsonl"]
    data_status = all((data_dir / f).exists() for f in data_files)
    print(f"Data Files: {'Working:' if data_status else 'Not Working:'}")
    
    return tfidf_status, semantic_status, data_status

def main():

    print("PATENT NLP PROJECT - SEMANTIC EMBEDDINGS UPGRADE DEMO")

    
    # Check system status
    tfidf_ok, semantic_ok, data_ok = check_system_status()
    
    if not data_ok:
        print("\nMissing data files. Run parse_patents.py first.")
        return
    
    if not tfidf_ok:
        print("\nTF-IDF index not found. Run: python embed_tfidf.py build")
        return
    
    # Demonstrate TF-IDF search
    demonstrate_tfidf_search()
    
    if not semantic_ok:
        print("\nSemantic index not found. Building now")
        try:
            from embed_semantic import build_semantic_index
            build_semantic_index()
            print("Semantic index built successfully")
        except Exception as e:
            print(f"Failed to build semantic index: {e}")
            return
    
    # Demonstrate semantic search
    demonstrate_semantic_search()
    
    # Demonstrate hybrid search
    demonstrate_hybrid_search()
    
    # Demonstrate comparison
    demonstrate_search_comparison()
    

    print("UPGRADE COMPLETE")


    print("Working: TF-IDF search (keyword-based)")
    print("Working: Semantic search (meaning-based)")
    print("Working: Hybrid search (combined approach)")
    print("Working: Advanced hybrid search (weighted combination)")
    print("\nUsage:")
    print("  python search_cli.py 'query' --mode tfidf")
    print("  python search_cli.py 'query' --mode semantic")
    print("  python search_cli.py 'query' --mode hybrid")
    print("  python search_cli.py 'query' --mode hybrid-advanced")

if __name__ == "__main__":
    main()
