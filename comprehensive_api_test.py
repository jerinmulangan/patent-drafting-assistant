#!/usr/bin/env python3
"""
Comprehensive API test suite for Patent NLP Project.
Tests all endpoints, error handling, performance, and edge cases.
"""

import requests
import json
import time
import statistics
from typing import Dict, List, Any
import concurrent.futures
import threading

API_BASE = "http://127.0.0.1:8000/api/v1"

class APITester:
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.errors = []
        
    def log_error(self, test_name: str, error: str):
        """Log an error for later analysis."""
        self.errors.append(f"{test_name}: {error}")
        print(f"{test_name}: {error}")
    
    def log_success(self, test_name: str, details: str = ""):
        """Log a successful test."""
        print(f"{test_name}: {details}")
    
    def test_health_endpoint(self):
        """Test health endpoint thoroughly."""
        print("\nTesting Health Endpoint...")
        
        try:
            # Test basic health check
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "healthy"
                assert "version" in data
                self.log_success("Health Check", f"Status: {data['status']}, Version: {data['version']}")
                return True
            else:
                self.log_error("Health Check", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_error("Health Check", str(e))
            return False
    
    def test_search_endpoints_comprehensive(self):
        """Test all search modes comprehensively."""
        print("\nTesting Search Endpoints...")
        
        test_queries = [
            "machine learning",
            "neural network",
            "artificial intelligence",
            "blockchain technology",
            "quantum computing"
        ]
        
        search_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        
        results = {}
        
        for mode in search_modes:
            print(f"\n  Testing {mode} mode...")
            mode_results = []
            
            for query in test_queries:
                try:
                    payload = {
                        "query": query,
                        "mode": mode,
                        "top_k": 5,
                        "include_snippets": True,
                        "include_metadata": True,
                        "log_enabled": True
                    }
                    
                    start_time = time.time()
                    response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        data = response.json()
                        assert data["mode"] == mode
                        assert data["query"] == query
                        assert "results" in data
                        assert "search_time" in data
                        
                        mode_results.append({
                            "query": query,
                            "response_time": end_time - start_time,
                            "search_time": data["search_time"],
                            "total_results": data["total_results"],
                            "has_results": len(data["results"]) > 0
                        })
                        
                        self.log_success(f"{mode} - {query}", 
                                       f"{data['total_results']} results in {data['search_time']:.3f}s")
                    else:
                        self.log_error(f"{mode} - {query}", f"Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"{mode} - {query}", str(e))
            
            results[mode] = mode_results
        
        self.results["search_endpoints"] = results
        return results
    
    def test_search_parameters(self):
        """Test various search parameters and edge cases."""
        print("\nTesting Search Parameters...")
        
        # Test different top_k values
        for top_k in [1, 3, 5, 10, 20]:
            try:
                payload = {
                    "query": "machine learning",
                    "mode": "semantic",
                    "top_k": top_k
                }
                response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    actual_results = len(data["results"])
                    self.log_success(f"top_k={top_k}", f"Requested: {top_k}, Got: {actual_results}")
                else:
                    self.log_error(f"top_k={top_k}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"top_k={top_k}", str(e))
        
        # Test hybrid parameters
        try:
            payload = {
                "query": "neural network",
                "mode": "hybrid",
                "alpha": 0.7,
                "rerank": True
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
            if response.status_code == 200:
                self.log_success("Hybrid with alpha=0.7", "Parameters accepted")
            else:
                self.log_error("Hybrid with alpha=0.7", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Hybrid with alpha=0.7", str(e))
        
        # Test hybrid-advanced parameters
        try:
            payload = {
                "query": "artificial intelligence",
                "mode": "hybrid-advanced",
                "tfidf_weight": 0.4,
                "semantic_weight": 0.6
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
            if response.status_code == 200:
                self.log_success("Hybrid-advanced with custom weights", "Parameters accepted")
            else:
                self.log_error("Hybrid-advanced with custom weights", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Hybrid-advanced with custom weights", str(e))
    
    def test_batch_search(self):
        """Test batch search functionality."""
        print("\nTesting Batch Search...")
        
        test_cases = [
            {
                "queries": ["machine learning", "neural network"],
                "mode": "semantic",
                "top_k": 3
            },
            {
                "queries": ["artificial intelligence", "deep learning", "computer vision"],
                "mode": "hybrid",
                "top_k": 2,
                "rerank": True
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                response = requests.post(f"{API_BASE}/batch_search", json=test_case, timeout=60)
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["total_queries"] == len(test_case["queries"])
                    assert len(data["results"]) == len(test_case["queries"])
                    
                    self.log_success(f"Batch Search {i+1}", 
                                   f"{data['total_queries']} queries in {end_time - start_time:.3f}s")
                else:
                    self.log_error(f"Batch Search {i+1}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"Batch Search {i+1}", str(e))
    
    def test_compare_modes(self):
        """Test mode comparison functionality."""
        print("\nTesting Compare Modes...")
        
        test_queries = ["machine learning", "quantum computing", "blockchain"]
        
        for query in test_queries:
            try:
                payload = {
                    "query": query,
                    "top_k": 3
                }
                response = requests.post(f"{API_BASE}/compare_modes", json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["query"] == query
                    assert "results" in data
                    assert len(data["results"]) == 4  # All 4 modes
                    
                    modes = list(data["results"].keys())
                    expected_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
                    assert set(modes) == set(expected_modes)
                    
                    self.log_success(f"Compare Modes - {query}", f"All {len(modes)} modes compared")
                else:
                    self.log_error(f"Compare Modes - {query}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"Compare Modes - {query}", str(e))
    
    def test_summarize_endpoint(self):
        """Test summarization functionality."""
        print("\nTesting Summarize Endpoint...")
        
        # First, get some document IDs from search results
        try:
            search_payload = {
                "query": "machine learning",
                "mode": "semantic",
                "top_k": 5
            }
            search_response = requests.post(f"{API_BASE}/search", json=search_payload, timeout=30)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                doc_ids = [result["doc_id"] for result in search_data["results"]]
                
                # Test summarization for each document
                for doc_id in doc_ids[:3]:  # Test first 3
                    try:
                        payload = {
                            "doc_id": doc_id,
                            "max_length": 200
                        }
                        response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            assert data["doc_id"] == doc_id
                            assert "summary" in data
                            assert "title" in data
                            
                            self.log_success(f"Summarize - {doc_id}", 
                                           f"Summary length: {len(data['summary'])} chars")
                        else:
                            self.log_error(f"Summarize - {doc_id}", f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_error(f"Summarize - {doc_id}", str(e))
            else:
                self.log_error("Summarize Setup", "Could not get document IDs from search")
        except Exception as e:
            self.log_error("Summarize Setup", str(e))
    
    def test_log_analysis(self):
        """Test log analysis functionality."""
        print("\nTesting Log Analysis...")
        
        try:
            response = requests.get(f"{API_BASE}/logs/analyze", timeout=10)
            if response.status_code == 200:
                data = response.json()
                assert "total_queries" in data
                assert "unique_queries" in data
                assert "mode_usage" in data
                
                self.log_success("Log Analysis", 
                               f"Total queries: {data['total_queries']}, "
                               f"Unique: {data['unique_queries']}")
            else:
                self.log_error("Log Analysis", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Log Analysis", str(e))
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\nTesting Error Handling...")
        
        # Test invalid search mode
        try:
            payload = {
                "query": "test",
                "mode": "invalid_mode",
                "top_k": 5
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
            if response.status_code in [400, 422]:
                self.log_success("Invalid Mode", "Properly rejected invalid mode")
            else:
                self.log_error("Invalid Mode", f"Expected 400 or 422, got {response.status_code}")
        except Exception as e:
            self.log_error("Invalid Mode", str(e))
        
        # Test empty query
        try:
            payload = {
                "query": "",
                "mode": "semantic",
                "top_k": 5
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
            if response.status_code in [400, 422]:
                self.log_success("Empty Query", "Properly rejected empty query")
            else:
                self.log_error("Empty Query", f"Expected 400 or 422, got {response.status_code}")
        except Exception as e:
            self.log_error("Empty Query", str(e))
        
        # Test invalid top_k
        try:
            payload = {
                "query": "test",
                "mode": "semantic",
                "top_k": -1
            }
            response = requests.post(f"{API_BASE}/search", json=payload, timeout=10)
            if response.status_code in [400, 422]:
                self.log_success("Invalid top_k", "Properly rejected negative top_k")
            else:
                self.log_error("Invalid top_k", f"Expected 400 or 422, got {response.status_code}")
        except Exception as e:
            self.log_error("Invalid top_k", str(e))
        
        # Test non-existent document ID
        try:
            payload = {
                "doc_id": "NONEXISTENT_DOC_ID_12345",
                "max_length": 200
            }
            response = requests.post(f"{API_BASE}/summarize", json=payload, timeout=10)
            if response.status_code == 404:
                self.log_success("Non-existent Doc ID", "Properly returned 404")
            else:
                self.log_error("Non-existent Doc ID", f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_error("Non-existent Doc ID", str(e))
    
    def test_performance(self):
        """Test API performance under load."""
        print("\nTesting Performance...")
        
        def make_request():
            payload = {
                "query": "machine learning",
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
        
        # Test concurrent requests
        print("  Testing concurrent requests...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            self.log_success("Concurrent Performance", 
                           f"Success rate: {len(successful_requests)}/10, "
                           f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s, Min: {min_time:.3f}s")
        else:
            self.log_error("Concurrent Performance", "No successful requests")
    
    def test_data_integrity(self):
        """Test data integrity and consistency."""
        print("\nTesting Data Integrity...")
        
        # Test that search results are consistent
        query = "machine learning"
        results_sets = []
        
        for _ in range(3):
            try:
                payload = {
                    "query": query,
                    "mode": "semantic",
                    "top_k": 5
                }
                response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    doc_ids = [result["doc_id"] for result in data["results"]]
                    results_sets.append(set(doc_ids))
                else:
                    self.log_error("Data Integrity", f"Search failed with status {response.status_code}")
                    return
            except Exception as e:
                self.log_error("Data Integrity", str(e))
                return
        
        # Check consistency
        if len(results_sets) >= 2:
            # Results should be mostly consistent (allowing for some variation)
            intersection = results_sets[0] & results_sets[1] & results_sets[2]
            union = results_sets[0] | results_sets[1] | results_sets[2]
            consistency_ratio = len(intersection) / len(union) if union else 0
            
            if consistency_ratio >= 0.6:  # At least 60% consistency
                self.log_success("Data Consistency", f"Consistency ratio: {consistency_ratio:.2f}")
            else:
                self.log_error("Data Consistency", f"Low consistency: {consistency_ratio:.2f}")
    
    def run_all_tests(self):
        """Run all tests and generate report."""
        print("Starting Comprehensive API Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        self.test_health_endpoint()
        self.test_search_endpoints_comprehensive()
        self.test_search_parameters()
        self.test_batch_search()
        self.test_compare_modes()
        self.test_summarize_endpoint()
        self.test_log_analysis()
        self.test_error_handling()
        self.test_performance()
        self.test_data_integrity()
        
        end_time = time.time()
        
        # Generate report
        self.generate_report(end_time - start_time)
    
    def generate_report(self, total_time: float):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE API TEST REPORT")
        print("=" * 60)
        
        print(f"Total test time: {total_time:.2f} seconds")
        print(f"Total errors: {len(self.errors)}")
        
        if self.errors:
            print("\nERRORS FOUND:")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\nNO ERRORS FOUND - All tests passed!")
        
        # Performance summary
        if "search_endpoints" in self.results:
            print("\nPERFORMANCE SUMMARY:")
            for mode, results in self.results["search_endpoints"].items():
                if results:
                    avg_time = statistics.mean([r["search_time"] for r in results])
                    print(f"  • {mode}: {avg_time:.3f}s average")
        
        print("\nRECOMMENDATIONS:")
        if len(self.errors) == 0:
            print("  API is ready for production use")
            print("  All endpoints are functioning correctly")
            print("  Error handling is working properly")
            print("  Performance is acceptable")
        else:
            print("  Address the errors listed above before production")
            print("  Consider adding more comprehensive error handling")
        
        print("\n" + "=" * 60)

def main():
    """Run the comprehensive test suite."""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

