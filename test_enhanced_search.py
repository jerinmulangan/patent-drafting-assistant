#!/usr/bin/env python3
"""Test the enhanced search features."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_tfidf_with_metadata():
    """Test TF-IDF search with metadata."""
    print("Testing TF-IDF search with metadata...")
    try:
        from embed_tfidf import search_with_metadata
        results = search_with_metadata("machine learning", top_k=3)
        
        print(f"Found {len(results)} results:")
        for i, (doc_id, score, meta) in enumerate(results, 1):
            print(f"{i}. {doc_id} - {score:.4f}")
            print(f"   Title: {meta.get('title', 'No title')}")
            print(f"   Type: {meta.get('doc_type', 'unknown')}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_semantic_with_rerank():
    """Test semantic search with re-ranking."""
    print("Testing semantic search with re-ranking...")
    try:
        from embed_semantic import search_semantic
        results = search_semantic("machine learning", top_k=3, rerank=True)
        
        print(f"Found {len(results)} results:")
        for i, (doc_id, score, meta) in enumerate(results, 1):
            print(f"{i}. {doc_id} - {score:.4f}")
            print(f"   Title: {meta.get('title', 'No title')}")
            print()
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_snippet_generation():
    """Test snippet generation."""
    print("Testing snippet generation...")
    try:
        from search_utils import generate_snippet
        
        sample_text = "This is a machine learning algorithm that processes neural networks for artificial intelligence applications in computer vision and natural language processing."
        query = "machine learning neural network"
        
        snippet = generate_snippet(sample_text, query, max_length=100)
        print(f"Original text: {sample_text}")
        print(f"Query: {query}")
        print(f"Generated snippet: {snippet}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query_logging():
    """Test query logging."""
    print("Testing query logging...")
    try:
        from search_utils import log_query
        
        # Test logging
        test_results = [("test_doc_1", 0.95), ("test_doc_2", 0.87)]
        log_query("test query", "tfidf", test_results, "test_log.jsonl")
        
        print("Query logged successfully")
        
        # Test log analysis
        from search_utils import analyze_query_log
        analysis = analyze_query_log("test_log.jsonl")
        print(f"Log analysis: {analysis}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Enhanced Search Features Test")
    print("=" * 50)
    
    tests = [
        test_tfidf_with_metadata,
        test_semantic_with_rerank,
        test_snippet_generation,
        test_query_logging
    ]
    
    results = []
    for test in tests:
        print("\n" + "-" * 30)
        result = test()
        results.append(result)
        print(f"Result: {'PASSED' if result else 'FAILED'}")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! Enhanced search features are working.")
    else:
        print("Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
