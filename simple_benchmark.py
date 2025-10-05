#!/usr/bin/env python3
"""
Simple benchmarking script for Patent NLP search system.
"""

import json
import time
from search_service import run_search, SearchRequest

def run_simple_benchmark():
    """Run a simple benchmark with a few test queries."""
    print("Simple Patent NLP Benchmark")
    print("=" * 40)
    
    # Test queries
    test_queries = [
        "machine learning algorithm",
        "neural network deep learning", 
        "artificial intelligence system",
        "computer vision image recognition",
        "natural language processing"
    ]
    
    modes = ["tfidf", "semantic", "hybrid"]
    
    results = {}
    
    for mode in modes:
        print(f"\nTesting {mode} mode...")
        mode_results = []
        
        for query in test_queries:
            print(f"  Query: {query}")
            
            try:
                request = SearchRequest(
                    query=query,
                    mode=mode,
                    top_k=5,
                    include_snippets=False,
                    include_metadata=False,
                    log_enabled=False
                )
                
                start_time = time.time()
                search_results, metadata = run_search(request)
                search_time = time.time() - start_time
                
                print(f"    {len(search_results)} results in {search_time:.3f}s")
                
                mode_results.append({
                    "query": query,
                    "results_count": len(search_results),
                    "search_time": search_time,
                    "top_result": search_results[0].doc_id if search_results else None
                })
                
            except Exception as e:
                print(f"    Error: {e}")
                mode_results.append({
                    "query": query,
                    "error": str(e)
                })
        
        results[mode] = mode_results
    
    # Print summary
    print(f"\nBENCHMARK SUMMARY")
    print("=" * 40)
    
    for mode, mode_results in results.items():
        successful_queries = [r for r in mode_results if "error" not in r]
        avg_time = sum(r["search_time"] for r in successful_queries) / len(successful_queries) if successful_queries else 0
        
        print(f"\n{mode.upper()} Mode:")
        print(f"  Successful queries: {len(successful_queries)}/{len(mode_results)}")
        print(f"  Average search time: {avg_time:.3f}s")
        
        if successful_queries:
            avg_results = sum(r["results_count"] for r in successful_queries) / len(successful_queries)
            print(f"  Average results: {avg_results:.1f}")
    
    # Save results
    with open("simple_benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: simple_benchmark_results.json")
    
    return results

if __name__ == "__main__":
    run_simple_benchmark()

