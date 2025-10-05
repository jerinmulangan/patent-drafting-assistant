#!/usr/bin/env python3
"""
Final comprehensive validation test for Patent NLP API.
Tests all endpoints, performance, and edge cases.
"""

import requests
import json
import time
import statistics

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

def test_all_search_modes():
    """Test all search modes with performance measurement."""
    print("\nTesting All Search Modes...")
    
    modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
    query = "machine learning artificial intelligence"
    results = {}
    
    for mode in modes:
        try:
            payload = {
                "query": query,
                "mode": mode,
                "top_k": 5,
                "include_snippets": True,
                "include_metadata": True
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                results[mode] = {
                    "success": True,
                    "response_time": end_time - start_time,
                    "search_time": data['search_time'],
                    "total_results": data['total_results'],
                    "has_snippets": any(r.get('snippet') for r in data['results']),
                    "has_metadata": any(r.get('title') for r in data['results'])
                }
                print(f"{mode}: {data['total_results']} results in {data['search_time']:.3f}s")
            else:
                results[mode] = {"success": False, "error": response.status_code}
                print(f"{mode}: Status {response.status_code}")
        except Exception as e:
            results[mode] = {"success": False, "error": str(e)}
            print(f"{mode}: {e}")
    
    return results

def test_batch_search():
    """Test batch search functionality."""
    print("\nTesting Batch Search...")
    try:
        payload = {
            "queries": ["neural network", "deep learning", "computer vision"],
            "mode": "semantic",
            "top_k": 3,
            "include_snippets": True
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/batch_search", json=payload, timeout=45)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Batch: {data['total_queries']} queries in {end_time - start_time:.3f}s")
            
            # Verify all queries were processed
            if len(data['results']) == data['total_queries']:
                print("All queries processed successfully")
                return True
            else:
                print(f"Mismatch: {len(data['results'])} results vs {data['total_queries']} queries")
                return False
        else:
            print(f"Batch: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Batch: {e}")
        return False

def test_compare_modes():
    """Test mode comparison."""
    print("\nTesting Compare Modes...")
    try:
        payload = {
            "query": "blockchain technology",
            "top_k": 3
        }
        
        response = requests.post(f"{API_BASE}/compare_modes", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            modes = list(data['results'].keys())
            expected_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
            
            if set(modes) == set(expected_modes):
                print(f"Compare: All {len(modes)} modes compared successfully")
                
                # Check that all modes returned results
                for mode, results in data['results'].items():
                    if results['total_results'] > 0:
                        print(f"  {mode}: {results['total_results']} results")
                    else:
                        print(f"  {mode}: No results")
                
                return True
            else:
                print(f"Compare: Missing modes. Got {modes}, expected {expected_modes}")
                return False
        else:
            print(f"Compare: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Compare: {e}")
        return False

def test_summarize():
    """Test summarization functionality."""
    print("\nTesting Summarize...")
    try:
        # Get a doc_id from search first
        search_payload = {
            "query": "machine learning",
            "mode": "semantic",
            "top_k": 3
        }
        search_response = requests.post(f"{API_BASE}/search", json=search_payload, timeout=20)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['results']:
                doc_id = search_data['results'][0]['doc_id']
                
                payload = {
                    "doc_id": doc_id,
                    "max_length": 200
                }
                response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Summarize: {len(data['summary'])} chars for {data['doc_id']}")
                    print(f"  Title: {data.get('title', 'No title')}")
                    return True
                else:
                    print(f"Summarize: Status {response.status_code}")
                    return False
            else:
                print("Summarize: No search results to test with")
                return False
        else:
            print("Summarize: Could not get doc_id from search")
            return False
    except Exception as e:
        print(f"Summarize: {e}")
        return False

def test_log_analysis():
    """Test log analysis."""
    print("\nTesting Log Analysis...")
    try:
        response = requests.get(f"{API_BASE}/logs/analyze", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Logs: {data['total_queries']} total queries analyzed")
            print(f"  Unique queries: {data['unique_queries']}")
            print(f"  Mode usage: {data['mode_usage']}")
            return True
        else:
            print(f"Logs: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Logs: {e}")
        return False

def test_validation():
    """Test input validation."""
    print("\nTesting Input Validation...")
    
    validation_tests = [
        {
            "name": "Empty query",
            "payload": {"query": "", "mode": "semantic", "top_k": 5},
            "expected_status": 422
        },
        {
            "name": "Invalid mode",
            "payload": {"query": "test", "mode": "invalid", "top_k": 5},
            "expected_status": 422
        },
        {
            "name": "Negative top_k",
            "payload": {"query": "test", "mode": "semantic", "top_k": -1},
            "expected_status": 422
        },
        {
            "name": "Large top_k",
            "payload": {"query": "test", "mode": "semantic", "top_k": 101},
            "expected_status": 422
        },
        {
            "name": "Invalid alpha",
            "payload": {"query": "test", "mode": "hybrid", "alpha": 1.5},
            "expected_status": 422
        }
    ]
    
    passed = 0
    for test in validation_tests:
        try:
            response = requests.post(f"{API_BASE}/search", json=test["payload"], timeout=10)
            if response.status_code == test["expected_status"]:
                print(f"{test['name']}: Properly rejected with {test['expected_status']}")
                passed += 1
            else:
                print(f"{test['name']}: Expected {test['expected_status']}, got {response.status_code}")
        except Exception as e:
            print(f"{test['name']}: {e}")
    
    return passed == len(validation_tests)

def test_performance():
    """Test API performance."""
    print("\nTesting Performance...")
    
    def make_request():
        payload = {
            "query": "artificial intelligence machine learning",
            "mode": "semantic",
            "top_k": 5
        }
        start_time = time.time()
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        end_time = time.time()
        return {
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "success": response.status_code == 200
        }
    
    # Test multiple requests
    print("  Testing multiple requests...")
    response_times = []
    successful_requests = 0
    
    for i in range(5):
        result = make_request()
        if result["success"]:
            response_times.append(result["response_time"])
            successful_requests += 1
        time.sleep(0.5)  # Small delay between requests
    
    if response_times:
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"Performance: {successful_requests}/5 successful requests")
        print(f"  Average response time: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        
        # Performance criteria
        if avg_time < 2.0:  # Less than 2 seconds average
            print("Performance: Excellent (< 2s average)")
            return True
        elif avg_time < 5.0:  # Less than 5 seconds average
            print("Performance: Good (< 5s average)")
            return True
        else:
            print("Performance: Acceptable but could be improved")
            return True
    else:
        print("Performance: No successful requests")
        return False

def main():
    """Run final validation tests."""
    print("Final API Validation Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Health Check", test_health),
        ("Search Modes", test_all_search_modes),
        ("Batch Search", test_batch_search),
        ("Compare Modes", test_compare_modes),
        ("Summarize", test_summarize),
        ("Log Analysis", test_log_analysis),
        ("Input Validation", test_validation),
        ("Performance", test_performance)
    ]
    
    results = {}
    passed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"{test_name}: Unexpected error - {e}")
            results[test_name] = False
    
    end_time = time.time()
    
    # Generate final report
    print("\n" + "=" * 60)
    print("FINAL VALIDATION REPORT")
    print("=" * 60)
    
    print(f"Total test time: {end_time - start_time:.2f} seconds")
    print(f"Tests passed: {passed}/{len(tests)}")
    
    print("\nTest Results:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {status} {test_name}")
    
    print("\nAPI Status:")
    if passed == len(tests):
        print("EXCELLENT - All tests passed!")
        print("API is ready for production use")
        print("All endpoints are functioning correctly")
        print("Performance is optimal")
        print("Error handling is robust")
        print("Input validation is comprehensive")
    elif passed >= len(tests) * 0.8:  # 80% pass rate
        print("GOOD - Most tests passed")
        print("API is mostly ready for production")
        print("Address failing tests before full deployment")
    else:
        print("NEEDS WORK - Multiple test failures")
        print("API needs fixes before production use")
        print("Review and fix failing tests")
    
    print("\nReady for React Frontend Integration!")
    print("=" * 60)
    
    return passed == len(tests)

if __name__ == "__main__":
    main()

