#!/usr/bin/env python3
"""
Centralized search service for Patent NLP Project.
This module consolidates all search logic to be shared between CLI and API.
"""

import time
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# Import search functions
from embed_tfidf import search as search_tfidf, search_with_metadata as search_tfidf_with_metadata
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid, search_hybrid_advanced
from search_utils import generate_snippet, log_query, load_patent_metadata

# Import optimized search functions
try:
    from optimized_search_service import (
        optimized_tfidf_search_with_metadata,
        optimized_semantic_search,
        optimized_hybrid_search,
        optimized_hybrid_advanced_search,
        warm_up_caches
    )
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False


class SearchRequest:
    """Search request parameters."""
    def __init__(self, 
                 query: str,
                 mode: str = "tfidf",
                 top_k: int = 5,
                 alpha: float = 0.5,
                 tfidf_weight: float = 0.3,
                 semantic_weight: float = 0.7,
                 rerank: bool = False,
                 include_snippets: bool = True,
                 include_metadata: bool = True,
                 log_enabled: bool = False):
        self.query = query
        self.mode = mode
        self.top_k = top_k
        self.alpha = alpha
        self.tfidf_weight = tfidf_weight
        self.semantic_weight = semantic_weight
        self.rerank = rerank
        self.include_snippets = include_snippets
        self.include_metadata = include_metadata
        self.log_enabled = log_enabled


class SearchResult:
    """Standardized search result format."""
    def __init__(self, 
                 doc_id: str,
                 score: float,
                 title: str = "",
                 doc_type: str = "",
                 source_file: str = "",
                 snippet: str = "",
                 base_doc_id: str = ""):
        self.doc_id = doc_id
        self.score = score
        self.title = title
        self.doc_type = doc_type
        self.source_file = source_file
        self.snippet = snippet
        self.base_doc_id = base_doc_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doc_id": self.doc_id,
            "score": self.score,
            "title": self.title,
            "doc_type": self.doc_type,
            "source_file": self.source_file,
            "snippet": self.snippet,
            "base_doc_id": self.base_doc_id
        }


def run_search(request: SearchRequest) -> Tuple[List[SearchResult], Dict[str, Any]]:
    """
    Centralized search function that handles all search modes and features.
    
    Args:
        request: SearchRequest object with all search parameters
        
    Returns:
        Tuple of (results, metadata) where:
        - results: List of SearchResult objects
        - metadata: Dict with search timing and other info
    """
    start_time = time.time()
    
    # Validate query
    if not request.query or not request.query.strip():
        raise ValueError("Query cannot be empty")
    
    # Validate top_k
    if request.top_k <= 0:
        raise ValueError("top_k must be positive")
    
    if request.top_k > 100:
        raise ValueError("top_k cannot exceed 100")
    
    # Validate mode
    valid_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
    if request.mode not in valid_modes:
        raise ValueError(f"Invalid search mode: {request.mode}. Must be one of {valid_modes}")
    
    # Validate alpha for hybrid mode
    if request.mode == "hybrid" and (request.alpha < 0 or request.alpha > 1):
        raise ValueError("alpha must be between 0 and 1 for hybrid mode")
    
    # Run search based on mode (use optimized versions if available)
    if request.mode == "tfidf":
        if OPTIMIZED_AVAILABLE:
            raw_results = optimized_tfidf_search_with_metadata(request.query, top_k=request.top_k)
        else:
            raw_results = search_tfidf_with_metadata(request.query, top_k=request.top_k)
        
    elif request.mode == "semantic":
        if OPTIMIZED_AVAILABLE:
            raw_results = optimized_semantic_search(
                request.query, 
                top_k=request.top_k, 
                rerank=request.rerank,
                keyword_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
        else:
            raw_results = search_semantic(
                request.query, 
                top_k=request.top_k, 
                rerank=request.rerank,
                keyword_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
        
    elif request.mode == "hybrid":
        if OPTIMIZED_AVAILABLE:
            raw_results = optimized_hybrid_search(
                request.query,
                top_k=request.top_k,
                alpha=request.alpha,
                rerank=request.rerank,
                keyword_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
        else:
            raw_results = search_hybrid(
                request.query,
                top_k=request.top_k,
                alpha=request.alpha,
                rerank=request.rerank,
                keyword_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
        
    elif request.mode == "hybrid-advanced":
        if OPTIMIZED_AVAILABLE:
            raw_results = optimized_hybrid_advanced_search(
                request.query,
                top_k=request.top_k,
                tfidf_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
        else:
            raw_results = search_hybrid_advanced(
                request.query,
                top_k=request.top_k,
                tfidf_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight
            )
    
    # Convert raw results to standardized format
    results = []
    for item in raw_results:
        if len(item) == 3:  # (doc_id, score, metadata)
            doc_id, score, meta = item
            result = SearchResult(
                doc_id=doc_id,
                score=score,
                title=meta.get("title", ""),
                doc_type=meta.get("doc_type", ""),
                source_file=meta.get("source_file", ""),
                base_doc_id=meta.get("base_doc_id", "")
            )
        else:  # (doc_id, score) - fallback for basic results
            doc_id, score = item
            result = SearchResult(doc_id=doc_id, score=score)
        
        # Generate snippet if requested
        if request.include_snippets:
            chunk_text = meta.get("chunk_text", "") if len(item) == 3 else ""
            if chunk_text:
                result.snippet = generate_snippet(chunk_text, request.query)
        
        results.append(result)
    
    # Log query if enabled
    if request.log_enabled:
        log_query(request.query, request.mode, [(r.doc_id, r.score) for r in results])
    
    # Calculate timing
    search_time = time.time() - start_time
    
    # Prepare metadata
    metadata = {
        "search_time": search_time,
        "mode": request.mode,
        "total_results": len(results),
        "query": request.query
    }
    
    return results, metadata


def format_results_for_cli(results: List[SearchResult], mode_name: str, query: str = "") -> None:
    """
    Format search results for CLI display.
    This maintains compatibility with existing CLI output format.
    """
    print(f"\n{mode_name} search results:")
    print()
    
    for rank, result in enumerate(results, 1):
        print(f"{rank}.{result.doc_id} ({result.doc_type}) - Score: {result.score:.4f}")
        if result.title:
            print(f"Title: {result.title}")
        if result.snippet:
            print(f"Snippet: {result.snippet}")
        if result.source_file:
            print(f"Source: {result.source_file}")
        print()


def format_results_for_api(results: List[SearchResult], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format search results for API JSON response.
    """
    return {
        "query": metadata["query"],
        "mode": metadata["mode"],
        "search_time": metadata["search_time"],
        "total_results": metadata["total_results"],
        "results": [result.to_dict() for result in results]
    }


def validate_search_request(query: str, mode: str, top_k: int, **kwargs) -> SearchRequest:
    """
    Validate and create SearchRequest object from parameters.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    
    if top_k > 100:
        raise ValueError("top_k cannot exceed 100")
    
    return SearchRequest(
        query=query.strip(),
        mode=mode,
        top_k=top_k,
        **kwargs
    )


# Convenience functions for backward compatibility
def search_tfidf_simple(query: str, top_k: int = 5) -> List[SearchResult]:
    """Simple TF-IDF search for backward compatibility."""
    request = SearchRequest(query=query, mode="tfidf", top_k=top_k)
    results, _ = run_search(request)
    return results


def search_semantic_simple(query: str, top_k: int = 5, rerank: bool = False) -> List[SearchResult]:
    """Simple semantic search for backward compatibility."""
    request = SearchRequest(query=query, mode="semantic", top_k=top_k, rerank=rerank)
    results, _ = run_search(request)
    return results


def search_hybrid_simple(query: str, top_k: int = 5, alpha: float = 0.5) -> List[SearchResult]:
    """Simple hybrid search for backward compatibility."""
    request = SearchRequest(query=query, mode="hybrid", top_k=top_k, alpha=alpha)
    results, _ = run_search(request)
    return results


if __name__ == "__main__":
    # Test the search service
    print("Testing Search Service...")
    
    # Test TF-IDF search
    print("\n1. Testing TF-IDF search:")
    request = SearchRequest(query="machine learning", mode="tfidf", top_k=3)
    results, metadata = run_search(request)
    print(f"Found {len(results)} results in {metadata['search_time']:.3f}s")
    for result in results[:2]:
        print(f"  - {result.doc_id}: {result.score:.4f}")
    
    # Test semantic search with re-ranking
    print("\n2. Testing semantic search with re-ranking:")
    request = SearchRequest(query="neural network", mode="semantic", top_k=3, rerank=True)
    results, metadata = run_search(request)
    print(f"Found {len(results)} results in {metadata['search_time']:.3f}s")
    for result in results[:2]:
        print(f"  - {result.doc_id}: {result.score:.4f}")
    
    print("\nSearch service test completed!")
