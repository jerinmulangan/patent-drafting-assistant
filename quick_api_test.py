#!/usr/bin/env python3
"""
Quick API test suite for Patent NLP Project.
Focused on essential functionality and performance.
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_health():
    """Test health endpoint."""
    print("Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Health: {data['status']} - Version {data['version']}")
            return True
        else:
            print(f"Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health error: {e}")
        return False

def test_search_modes():
    """Test all search modes quickly."""
    print("\nTesting Search Modes...")
    
    modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
    query = "machine learning"
    
    for mode in modes:
        try:
            payload = {
                "query": query,
                "mode": mode,
                "top_k": 3,
                "include_snippets": True
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=20)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                print(f"{mode}: {data['total_results']} results in {data['search_time']:.2f}s")
            else:
                print(f"{mode}: Status {response.status_code}")
        except Exception as e:
            print(f"{mode}: {e}")

def test_batch_search():
    """Test batch search."""
    print("\nTesting Batch Search...")
    try:
        payload = {
            "queries": ["neural network", "artificial intelligence"],
            "mode": "semantic",
            "top_k": 2
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/batch_search", json=payload, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Batch: {data['total_queries']} queries in {end_time - start_time:.2f}s")
        else:
            print(f"Batch: Status {response.status_code}")
    except Exception as e:
        print(f"Batch: {e}")

def test_compare_modes():
    """Test mode comparison."""
    print("\nTesting Compare Modes...")
    try:
        payload = {
            "query": "blockchain",
            "top_k": 2
        }
        
        response = requests.post(f"{API_BASE}/compare_modes", json=payload, timeout=40)
        
        if response.status_code == 200:
            data = response.json()
            modes = list(data['results'].keys())
            print(f"Compare: {len(modes)} modes compared")
        else:
            print(f"Compare: Status {response.status_code}")
    except Exception as e:
        print(f"Compare: {e}")

def test_summarize():
    """Test summarization."""
    print("\nTesting Summarize...")
    try:
        # Get a doc_id from search first
        search_payload = {
            "query": "machine learning",
            "mode": "semantic",
            "top_k": 1
        }
        search_response = requests.post(f"{API_BASE}/search", json=search_payload, timeout=20)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['results']:
                doc_id = search_data['results'][0]['doc_id']
                
                payload = {
                    "doc_id": doc_id,
                    "max_length": 150
                }
                response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Summarize: {len(data['summary'])} chars for {data['doc_id']}")
                else:
                    print(f"Summarize: Status {response.status_code}")
            else:
                print("Summarize: No search results to test with")
        else:
            print("Summarize: Could not get doc_id from search")
    except Exception as e:
        print(f"Summarize: {e}")

def test_error_handling():
    """Test error handling."""
    print("\nTesting Error Handling...")
    
    # Test invalid mode
    try:
        payload = {
            "query": "test",
            "mode": "invalid_mode",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Invalid mode: Properly rejected")
        else:
            print(f"Invalid mode: Expected 400 or 422, got {response.status_code}")
    except Exception as e:
        print(f"Invalid mode: {e}")
    
    # Test empty query
    try:
        payload = {
            "query": "",
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Empty query: Properly rejected")
        else:
            print(f"Empty query: Expected 400 or 422, got {response.status_code}")
    except Exception as e:
        print(f"Empty query: {e}")

def test_logs():
    """Test log analysis."""
    print("\nTesting Log Analysis...")
    try:
        response = requests.get(f"{API_BASE}/logs/analyze", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Logs: {data['total_queries']} total queries analyzed")
        else:
            print(f"Logs: Status {response.status_code}")
    except Exception as e:
        print(f"Logs: {e}")

def main():
    """Run quick API tests."""
    print("Quick API Test Suite")
    print("=" * 40)
    
    start_time = time.time()
    
    # Run tests
    test_health()
    test_search_modes()
    test_batch_search()
    test_compare_modes()
    test_summarize()
    test_error_handling()
    test_logs()
    
    end_time = time.time()
    
    print(f"\nTotal test time: {end_time - start_time:.2f} seconds")
    print("Quick test completed!")

if __name__ == "__main__":
    main()

