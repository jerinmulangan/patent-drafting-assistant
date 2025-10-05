#!/usr/bin/env python3
"""
Test script to verify the complete integration between frontend and backend.
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API directly."""
    print("Testing Backend API...")
    
    # Test search endpoint
    search_url = "http://localhost:8000/api/v1/search"
    search_data = {
        "query": "machine learning",
        "mode": "semantic",
        "top_k": 3
    }
    
    try:
        response = requests.post(search_url, json=search_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend search API working - Found {data.get('total_results', 0)} results")
            return data.get('results', [])
        else:
            print(f"✗ Backend search API failed - Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Backend search API error: {e}")
        return []

def test_frontend_api():
    """Test the frontend API route."""
    print("\nTesting Frontend API...")
    
    # Wait a bit for frontend to start
    time.sleep(3)
    
    search_url = "http://localhost:3000/api/search"
    search_data = {
        "query": "machine learning",
        "mode": "semantic",
        "top_k": 3
    }
    
    try:
        response = requests.post(search_url, json=search_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Frontend API working - Found {len(data.get('results', []))} results")
            return True
        else:
            print(f"✗ Frontend API failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend API error: {e}")
        return False

def test_summarize_api():
    """Test the summarize API."""
    print("\nTesting Summarize API...")
    
    # First get a result from search
    results = test_backend_api()
    if not results:
        print("✗ No results to test summarize API")
        return False
    
    doc_id = results[0].get('doc_id')
    if not doc_id:
        print("✗ No doc_id found in search results")
        return False
    
    # Test backend summarize
    backend_url = "http://localhost:8000/api/v1/summarize"
    backend_data = {"doc_id": doc_id}
    
    try:
        response = requests.post(backend_url, json=backend_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend summarize API working - Summary length: {len(data.get('summary', ''))}")
        else:
            print(f"✗ Backend summarize API failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend summarize API error: {e}")
        return False
    
    # Test frontend summarize
    frontend_url = "http://localhost:3000/api/summarize"
    frontend_data = {"doc_id": doc_id}
    
    try:
        response = requests.post(frontend_url, json=frontend_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Frontend summarize API working - Summary length: {len(data.get('summary', ''))}")
            return True
        else:
            print(f"✗ Frontend summarize API failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend summarize API error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("=" * 50)
    print("PATENT NLP INTEGRATION TEST")
    print("=" * 50)
    
    # Test backend
    backend_working = len(test_backend_api()) > 0
    
    # Test frontend
    frontend_working = test_frontend_api()
    
    # Test summarize
    summarize_working = test_summarize_api()
    
    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Backend API: {'✓ Working' if backend_working else '✗ Failed'}")
    print(f"Frontend API: {'✓ Working' if frontend_working else '✗ Failed'}")
    print(f"Summarize API: {'✓ Working' if summarize_working else '✗ Failed'}")
    
    if backend_working and frontend_working and summarize_working:
        print("\n🎉 ALL TESTS PASSED! Integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    main()

