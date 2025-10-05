#!/usr/bin/env python3
"""
Simple test for evaluation dataset and basic benchmarking.
"""

import json
from search_service import run_search, SearchRequest

def test_evaluation_dataset():
    """Test loading and basic functionality of evaluation dataset."""
    print("Testing evaluation dataset...")
    
    # Load dataset
    with open("evaluation_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    print(f"Dataset loaded: {dataset['metadata']['total_queries']} queries")
    print(f"   Categories: {len(dataset['metadata']['categories'])}")
    
    # Test first query
    first_query = dataset["queries"][0]
    print(f"\nTesting first query:")
    print(f"   Query: {first_query['query']}")
    print(f"   Category: {first_query['category']}")
    print(f"   Expected patents: {first_query['expected_patents']}")
    
    # Test search
    print(f"\nTesting search...")
    try:
        request = SearchRequest(
            query=first_query["query"],
            mode="tfidf",
            top_k=5,
            include_snippets=False,
            include_metadata=False,
            log_enabled=False
        )
        
        results, metadata = run_search(request)
        print(f"Search successful: {len(results)} results in {metadata['search_time']:.3f}s")
        
        # Check if any expected patents are in results
        retrieved_docs = [result.doc_id for result in results]
        expected_docs = first_query["expected_patents"]
        
        found_expected = set(expected_docs) & set(retrieved_docs)
        print(f"   Expected patents found: {len(found_expected)}/{len(expected_docs)}")
        if found_expected:
            print(f"   Found: {list(found_expected)}")
        
        return True
        
    except Exception as e:
        print(f"Search failed: {e}")
        return False

def test_multiple_modes():
    """Test different search modes."""
    print(f"\nTesting multiple search modes...")
    
    test_query = "machine learning algorithm"
    modes = ["tfidf", "semantic", "hybrid"]
    
    for mode in modes:
        try:
            request = SearchRequest(
                query=test_query,
                mode=mode,
                top_k=3,
                include_snippets=False,
                include_metadata=False,
                log_enabled=False
            )
            
            results, metadata = run_search(request)
            print(f"   {mode}: {len(results)} results in {metadata['search_time']:.3f}s")
            
        except Exception as e:
            print(f"   {mode}: Failed - {e}")

if __name__ == "__main__":
    print("Patent NLP Evaluation Test")
    print("=" * 40)
    
    if test_evaluation_dataset():
        test_multiple_modes()
        print(f"\nEvaluation system is ready!")
        print(f"   Run full benchmark: python benchmark_evaluation.py --quick")
    else:
        print(f"\nEvaluation system has issues")

