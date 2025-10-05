#!/usr/bin/env python3
"""
Debug benchmark to see what's happening.
"""

print("Starting debug benchmark...")

try:
    from search_service import run_search, SearchRequest
    print("Search service imported")
except Exception as e:
    print(f"Import error: {e}")
    exit(1)

try:
    request = SearchRequest(
        query="machine learning",
        mode="tfidf",
        top_k=3,
        include_snippets=False,
        include_metadata=False,
        log_enabled=False
    )
    print("SearchRequest created")
except Exception as e:
    print(f"SearchRequest error: {e}")
    exit(1)

try:
    print("Running search...")
    results, metadata = run_search(request)
    print(f"Search completed: {len(results)} results in {metadata['search_time']:.3f}s")
    
    if results:
        print(f"   First result: {results[0].doc_id}")
    
except Exception as e:
    print(f"Search error: {e}")
    import traceback
    traceback.print_exc()

print("Debug benchmark completed.")

