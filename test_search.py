#!/usr/bin/env python3
# Simple test script for search functionality.

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from embed_tfidf import search as search_tfidf

def main():
    print("Testing TF-IDF search")
    query = "machine learning"
    top_k = 3
    
    try:
        results = search_tfidf(query, top_k=top_k)
        print(f"Found {len(results)} results for query: '{query}'")
        
        for rank, (doc_id, score) in enumerate(results, 1):
            print(f"{rank}. {doc_id}\t{score:.4f}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

