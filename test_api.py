#!/usr/bin/env python3
"""
Test script for Patent NLP API endpoints.
"""

import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_search():
    """Test search endpoint."""
    print("\nTesting search endpoint...")
    try:
        payload = {
            "query": "machine learning",
            "mode": "tfidf",
            "top_k": 3,
            "include_snippets": True,
            "include_metadata": True
        }
        
        response = requests.post(f"{API_BASE}/search", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Search endpoint passed")
            print(f"   Query: {data['query']}")
            print(f"   Mode: {data['mode']}")
            print(f"   Results: {data['total_results']}")
            print(f"   Search time: {data['search_time']:.3f}s")
            
            if data['results']:
                first_result = data['results'][0]
                print(f"   First result: {first_result['doc_id']} (score: {first_result['score']:.4f})")
                if first_result.get('snippet'):
                    print(f"   Snippet: {first_result['snippet'][:100]}...")
            
            return True
        else:
            print(f"Search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"Search error: {e}")
        return False

def test_semantic_search():
    """Test semantic search with re-ranking."""
    print("\nTesting semantic search with re-ranking...")
    try:
        payload = {
            "query": "neural network",
            "mode": "semantic",
            "top_k": 3,
            "rerank": True,
            "include_snippets": True
        }
        
        response = requests.post(f"{API_BASE}/search", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Semantic search passed")
            print(f"   Results: {data['total_results']}")
            print(f"   Search time: {data['search_time']:.3f}s")
            return True
        else:
            print(f"Semantic search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Semantic search error: {e}")
        return False

def test_compare_modes():
    """Test mode comparison endpoint."""
    print("\nTesting compare modes endpoint...")
    try:
        payload = {
            "query": "artificial intelligence",
            "top_k": 2
        }
        
        response = requests.post(f"{API_BASE}/compare_modes", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Compare modes passed")
            print(f"   Query: {data['query']}")
            print(f"   Modes tested: {list(data['results'].keys())}")
            
            for mode, results in data['results'].items():
                print(f"   {mode}: {results['total_results']} results")
            
            return True
        else:
            print(f"Compare modes failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Compare modes error: {e}")
        return False

def test_summarize():
    """Test summarize endpoint."""
    print("\n🔍 Testing summarize endpoint...")
    try:
        payload = {
            "doc_id": "USD1092964S1"
        }
        response = requests.post(f"{API_BASE}/summarize", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("Summarize endpoint passed")
            print(f"   Doc ID: {data.get('doc_id', 'N/A')}")
            print(f"   Summary: {data.get('summary', 'N/A')}")
            return True
        else:
            print(f"Summarize endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"Summarize error: {e}")
        return False

def create_session_with_retries():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # which status codes to retry
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def wait_for_api(api_base, max_retries=5, initial_delay=2):
    """Wait for API to be ready with exponential backoff."""
    session = create_session_with_retries()
    for attempt in range(max_retries):
        try:
            response = session.get(
                f"{api_base}/health",
                timeout=5  # 5 second timeout for health check
            )
            if response.status_code == 200:
                print(f"API ready after {attempt + 1} attempts")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
        
        # Exponential backoff
        delay = initial_delay * (2 ** attempt)
        print(f"Waiting {delay} seconds before next attempt...")
        time.sleep(delay)
    
    print("Max retries reached, API not ready")
    return False



def main():
    """Run all API tests."""
    print("Patent NLP API Test Suite")
    print()
    
    # Wait a moment for API to be ready
    print("Waiting for API to be ready...")
    if not wait_for_api(API_BASE):
        print("❌ Failed to connect to API after multiple attempts")
        return
    
    tests = [
        test_health,
        test_search,
        test_semantic_search,
        test_compare_modes,
        test_summarize
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! API is working correctly.")
    else:
        print("Some tests failed. Check the API server and logs.")

if __name__ == "__main__":
    main()
