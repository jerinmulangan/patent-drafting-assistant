#!/usr/bin/env python3
"""
Comprehensive error handling test for Patent NLP API.
Tests all edge cases and error conditions.
"""

import requests
import json

API_BASE = "http://127.0.0.1:8000/api/v1"

def test_empty_query():
    """Test empty query handling."""
    print("Testing empty query...")
    try:
        payload = {
            "query": "",
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Empty query: Properly rejected")
            return True
        else:
            print(f"Empty query: Expected 400 or 422, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"Empty query: {e}")
        return False

def test_whitespace_query():
    """Test whitespace-only query handling."""
    print("Testing whitespace query...")
    try:
        payload = {
            "query": "   ",
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Whitespace query: Properly rejected")
            return True
        else:
            print(f"Whitespace query: Expected 400 or 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Whitespace query: {e}")
        return False

def test_invalid_mode():
    """Test invalid search mode handling."""
    print("Testing invalid mode...")
    try:
        payload = {
            "query": "test",
            "mode": "invalid_mode",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Invalid mode: Properly rejected")
            return True
        else:
            print(f"Invalid mode: Expected 400 or 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Invalid mode: {e}")
        return False

def test_invalid_top_k():
    """Test invalid top_k values."""
    print("Testing invalid top_k...")
    
    test_cases = [
        {"top_k": -1, "expected": [400, 422]},
        {"top_k": 0, "expected": [400, 422]},
        {"top_k": 101, "expected": [400, 422]},
        {"top_k": "invalid", "expected": [422]},  # Pydantic validation error
    ]
    
    results = []
    for case in test_cases:
        try:
            payload = {
                "query": "test",
                "mode": "semantic",
                "top_k": case["top_k"]
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
            if response.status_code in case["expected"]:
                print(f"top_k={case['top_k']}: Properly rejected with {response.status_code}")
                results.append(True)
            else:
                print(f"top_k={case['top_k']}: Expected {case['expected']}, got {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"top_k={case['top_k']}: {e}")
            results.append(False)
    
    return all(results)

def test_invalid_alpha():
    """Test invalid alpha values for hybrid search."""
    print("Testing invalid alpha...")
    
    test_cases = [
        {"alpha": -0.1, "expected": [400, 422]},
        {"alpha": 1.1, "expected": [400, 422]},
        {"alpha": "invalid", "expected": [422]},
    ]
    
    results = []
    for case in test_cases:
        try:
            payload = {
                "query": "test",
                "mode": "hybrid",
                "alpha": case["alpha"]
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
            if response.status_code in case["expected"]:
                print(f"alpha={case['alpha']}: Properly rejected with {response.status_code}")
                results.append(True)
            else:
                print(f"alpha={case['alpha']}: Expected {case['expected']}, got {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"alpha={case['alpha']}: {e}")
            results.append(False)
    
    return all(results)

def test_missing_required_fields():
    """Test missing required fields."""
    print("Testing missing required fields...")
    
    test_cases = [
        {"payload": {}, "expected": 422},  # Missing query
        {"payload": {"mode": "semantic"}, "expected": 422},  # Missing query
        {"payload": {"query": "test"}, "expected": 200},  # Should work with defaults
    ]
    
    results = []
    for i, case in enumerate(test_cases):
        try:
            response = requests.post(f"{API_BASE}/search", json=case["payload"], timeout=10)
            if response.status_code == case["expected"]:
                print(f"Missing fields test {i+1}: Got expected {case['expected']}")
                results.append(True)
            else:
                print(f"Missing fields test {i+1}: Expected {case['expected']}, got {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"Missing fields test {i+1}: {e}")
            results.append(False)
    
    return all(results)

def test_batch_search_errors():
    """Test batch search error handling."""
    print("Testing batch search errors...")
    
    # Test empty queries list
    try:
        payload = {
            "queries": [],
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/batch_search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Empty queries list: Properly rejected")
        else:
            print(f"Empty queries list: Expected 400 or 422, got {response.status_code}")
    except Exception as e:
        print(f"Empty queries list: {e}")
    
    # Test queries with empty strings
    try:
        payload = {
            "queries": ["test", "", "another test"],
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/batch_search", json=payload, timeout=10)
        if response.status_code in [400, 422]:
            print("Batch with empty query: Properly rejected")
            return True
        else:
            print(f"Batch with empty query: Expected 400 or 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Batch with empty query: {e}")
        return False

def test_summarize_errors():
    """Test summarize endpoint error handling."""
    print("Testing summarize errors...")
    
    # Test non-existent document
    try:
        payload = {
            "doc_id": "NONEXISTENT_DOC_12345",
            "max_length": 200
        }
        response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=10)
        if response.status_code == 404:
            print("Non-existent doc: Properly returned 404")
        else:
            print(f"Non-existent doc: Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"Non-existent doc: {e}")
    
    # Test invalid max_length
    try:
        payload = {
            "doc_id": "US12417505B2",
            "max_length": -1
        }
        response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=10)
        if response.status_code == 422:
            print("Invalid max_length: Properly rejected with 422")
            return True
        else:
            print(f"Invalid max_length: Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Invalid max_length: {e}")
        return False

def test_malformed_json():
    """Test malformed JSON handling."""
    print("Testing malformed JSON...")
    try:
        response = requests.post(
            f"{API_BASE}/search",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 422:
            print("Malformed JSON: Properly rejected with 422")
            return True
        else:
            print(f"Malformed JSON: Expected 422, got {response.status_code}")
            return False
    except Exception as e:
        print(f"Malformed JSON: {e}")
        return False

def test_large_requests():
    """Test handling of large requests."""
    print("Testing large requests...")
    
    # Test very large query
    try:
        large_query = "test " * 10000  # Very large query
        payload = {
            "query": large_query,
            "mode": "semantic",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        if response.status_code == 200:
            print("Large query: Handled successfully")
        else:
            print(f"Large query: Got {response.status_code}")
    except Exception as e:
        print(f"Large query: {e}")
    
    # Test large batch
    try:
        large_queries = [f"query {i}" for i in range(100)]  # 100 queries
        payload = {
            "queries": large_queries,
            "mode": "semantic",
            "top_k": 3
        }
        response = requests.post(f"{API_BASE}/batch_search", json=payload, timeout=60)
        if response.status_code == 200:
            print("Large batch: Handled successfully")
            return True
        else:
            print(f"Large batch: Got {response.status_code}")
            return False
    except Exception as e:
        print(f"Large batch: {e}")
        return False

def main():
    """Run all error handling tests."""
    print("Error Handling Test Suite")
    print("=" * 50)
    
    tests = [
        test_empty_query,
        test_whitespace_query,
        test_invalid_mode,
        test_invalid_top_k,
        test_invalid_alpha,
        test_missing_required_fields,
        test_batch_search_errors,
        test_summarize_errors,
        test_malformed_json,
        test_large_requests
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Error Handling Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All error handling tests passed!")
    else:
        print("Some error handling tests failed.")
    
    return passed == total

if __name__ == "__main__":
    main()

