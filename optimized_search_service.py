#!/usr/bin/env python3
"""
Optimized search service with caching and performance improvements.
This module provides cached versions of search functions for better API performance.
"""

import time
import threading
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json

# Global caches for models and indices
_model_cache = {}
_index_cache = {}
_cache_lock = threading.Lock()

def get_cached_model(model_name: str):
    """Get cached model or load and cache it."""
    with _cache_lock:
        if model_name not in _model_cache:
            from sentence_transformers import SentenceTransformer
            print(f"Loading model {model_name}...")
            _model_cache[model_name] = SentenceTransformer(model_name)
            print(f"Model {model_name} loaded and cached")
        return _model_cache[model_name]

def get_cached_tfidf_index():
    """Get cached TF-IDF index or load and cache it."""
    with _cache_lock:
        if 'tfidf' not in _index_cache:
            from embed_tfidf import load_index
            print("Loading TF-IDF index...")
            _index_cache['tfidf'] = load_index()
            print("TF-IDF index loaded and cached")
        return _index_cache['tfidf']

def get_cached_semantic_index():
    """Get cached semantic index or load and cache it."""
    with _cache_lock:
        if 'semantic' not in _index_cache:
            from embed_semantic import load_semantic_index
            print("Loading semantic index...")
            _index_cache['semantic'] = load_semantic_index()
            print("Semantic index loaded and cached")
        return _index_cache['semantic']

def optimized_tfidf_search(query: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """Optimized TF-IDF search with caching."""
    try:
        vectorizer, matrix, ids = get_cached_tfidf_index()
        
        from sklearn.metrics.pairwise import cosine_similarity
        query_vec = vectorizer.transform([query])
        sims = cosine_similarity(query_vec, matrix).ravel()
        top_idx = sims.argsort()[::-1][:top_k]
        
        return [(ids[i], float(sims[i])) for i in top_idx]
    except Exception as e:
        print(f"TF-IDF search error: {e}")
        return []

def optimized_tfidf_search_with_metadata(query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Optimized TF-IDF search with metadata."""
    try:
        # Get basic search results
        results = optimized_tfidf_search(query, top_k=top_k)
        if not results:
            return []
        
        # Load metadata efficiently
        metadata = _load_patent_metadata_cached()
        
        # Enrich results with metadata
        enriched_results = []
        for doc_id, score in results:
            # Extract base doc_id (remove chunk suffix)
            base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
            
            # Get metadata for base document
            base_meta = metadata.get(base_doc_id, {})
            
            # Get chunk text for snippet
            chunk_text = _get_chunk_text_cached(doc_id)
            
            enriched_results.append((
                doc_id,
                score,
                {
                    "title": base_meta.get("title", ""),
                    "doc_type": base_meta.get("doc_type", "unknown"),
                    "source_file": base_meta.get("source_file", ""),
                    "base_doc_id": base_doc_id,
                    "chunk_text": chunk_text or ""
                }
            ))
        
        return enriched_results
    except Exception as e:
        print(f"TF-IDF search with metadata error: {e}")
        return []

def optimized_semantic_search(query: str, top_k: int = 5, rerank: bool = False, 
                            keyword_weight: float = 0.3, semantic_weight: float = 0.7) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Optimized semantic search with caching."""
    try:
        import numpy as np
        
        # Get cached index and model
        index, ids, metadata, model_name = get_cached_semantic_index()
        model = get_cached_model(model_name)
        
        # Encode query
        query_embedding = model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Search FAISS index
        search_k = top_k * 3 if rerank else top_k
        scores, indices = index.search(query_embedding.astype('float32'), search_k)
        
        # Load patent metadata for enrichment
        from search_utils import load_patent_metadata
        patent_metadata = load_patent_metadata()
        
        # Get results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:  # Invalid index
                continue
            
            doc_id = ids[idx]
            chunk_meta = metadata[idx]
            
            # Get base document ID
            base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
            
            # Get patent metadata
            patent_meta = patent_metadata.get(base_doc_id, {})
            
            # Get chunk text
            chunk_text = _get_chunk_text_cached(doc_id)
            
            # Combine metadata
            enriched_meta = {
                "title": patent_meta.get("title", ""),
                "doc_type": patent_meta.get("doc_type", "unknown"),
                "source_file": patent_meta.get("source_file", ""),
                "base_doc_id": base_doc_id,
                "chunk_text": chunk_text or ""
            }
            
            results.append((doc_id, float(score), enriched_meta))
        
        # Re-rank if requested
        if rerank and len(results) > top_k:
            from search_utils import rerank_results
            reranked = rerank_results(
                [(doc_id, score) for doc_id, score, _ in results],
                query,
                keyword_weight=keyword_weight,
                semantic_weight=semantic_weight
            )
            
            # Rebuild results with re-ranked scores
            reranked_dict = {doc_id: score for doc_id, score in reranked}
            results = [(doc_id, reranked_dict.get(doc_id, score), meta) 
                      for doc_id, score, meta in results 
                      if doc_id in reranked_dict]
        
        return results[:top_k]
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []

def optimized_hybrid_search(query: str, top_k: int = 5, alpha: float = 0.5, 
                          rerank: bool = False, keyword_weight: float = 0.3, 
                          semantic_weight: float = 0.7) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Optimized hybrid search combining TF-IDF and semantic."""
    try:
        # Get results from both methods
        tfidf_results = optimized_tfidf_search_with_metadata(query, top_k=top_k*2)
        semantic_results = optimized_semantic_search(query, top_k=top_k*2, rerank=False)
        
        # Combine scores
        combined_scores = {}
        
        # Add TF-IDF scores
        for doc_id, score, meta in tfidf_results:
            combined_scores[doc_id] = {
                'tfidf_score': score,
                'semantic_score': 0.0,
                'metadata': meta
            }
        
        # Add semantic scores
        for doc_id, score, meta in semantic_results:
            if doc_id in combined_scores:
                combined_scores[doc_id]['semantic_score'] = score
            else:
                combined_scores[doc_id] = {
                    'tfidf_score': 0.0,
                    'semantic_score': score,
                    'metadata': meta
                }
        
        # Calculate combined scores
        final_results = []
        for doc_id, scores in combined_scores.items():
            combined_score = (alpha * scores['semantic_score'] + 
                            (1 - alpha) * scores['tfidf_score'])
            final_results.append((doc_id, combined_score, scores['metadata']))
        
        # Sort by combined score
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        # Re-rank if requested
        if rerank and len(final_results) > top_k:
            from search_utils import rerank_results
            reranked = rerank_results(
                [(doc_id, score) for doc_id, score, _ in final_results],
                query,
                keyword_weight=keyword_weight,
                semantic_weight=semantic_weight
            )
            
            # Rebuild results with re-ranked scores
            reranked_dict = {doc_id: score for doc_id, score in reranked}
            final_results = [(doc_id, reranked_dict.get(doc_id, score), meta) 
                           for doc_id, score, meta in final_results 
                           if doc_id in reranked_dict]
        
        return final_results[:top_k]
    except Exception as e:
        print(f"Hybrid search error: {e}")
        return []

def optimized_hybrid_advanced_search(query: str, top_k: int = 5, 
                                   tfidf_weight: float = 0.3, 
                                   semantic_weight: float = 0.7) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Optimized advanced hybrid search with custom weights."""
    try:
        # Get results from both methods
        tfidf_results = optimized_tfidf_search_with_metadata(query, top_k=top_k*2)
        semantic_results = optimized_semantic_search(query, top_k=top_k*2, rerank=False)
        
        # Combine scores with custom weights
        combined_scores = {}
        
        # Add TF-IDF scores
        for doc_id, score, meta in tfidf_results:
            combined_scores[doc_id] = {
                'tfidf_score': score,
                'semantic_score': 0.0,
                'metadata': meta
            }
        
        # Add semantic scores
        for doc_id, score, meta in semantic_results:
            if doc_id in combined_scores:
                combined_scores[doc_id]['semantic_score'] = score
            else:
                combined_scores[doc_id] = {
                    'tfidf_score': 0.0,
                    'semantic_score': score,
                    'metadata': meta
                }
        
        # Calculate combined scores with custom weights
        final_results = []
        for doc_id, scores in combined_scores.items():
            combined_score = (tfidf_weight * scores['tfidf_score'] + 
                            semantic_weight * scores['semantic_score'])
            final_results.append((doc_id, combined_score, scores['metadata']))
        
        # Sort by combined score
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return final_results[:top_k]
    except Exception as e:
        print(f"Hybrid advanced search error: {e}")
        return []

# Cached metadata loading
_metadata_cache = None
_chunk_text_cache = {}

def _load_patent_metadata_cached() -> Dict[str, Dict[str, Any]]:
    """Load patent metadata with caching."""
    global _metadata_cache
    
    if _metadata_cache is None:
        from search_utils import load_patent_metadata
        _metadata_cache = load_patent_metadata()
    
    return _metadata_cache

def _get_chunk_text_cached(chunk_id: str) -> Optional[str]:
    """Get chunk text with caching."""
    if chunk_id not in _chunk_text_cache:
        from search_utils import get_chunk_text
        _chunk_text_cache[chunk_id] = get_chunk_text(chunk_id)
    
    return _chunk_text_cache.get(chunk_id)

def warm_up_caches():
    """Warm up all caches for better performance."""
    print("Warming up caches...")
    
    # Warm up TF-IDF
    try:
        get_cached_tfidf_index()
        print("TF-IDF cache warmed up")
    except Exception as e:
        print(f"TF-IDF cache warm-up failed: {e}")
    
    # Warm up semantic
    try:
        get_cached_semantic_index()
        get_cached_model("all-MiniLM-L6-v2")
        print("Semantic cache warmed up")
    except Exception as e:
        print(f"Semantic cache warm-up failed: {e}")
    
    # Warm up metadata
    try:
        _load_patent_metadata_cached()
        print("Metadata cache warmed up")
    except Exception as e:
        print(f"Metadata cache warm-up failed: {e}")
    
    print("Cache warm-up completed!")

if __name__ == "__main__":
    # Test the optimized functions
    print("Testing optimized search functions...")
    
    # Warm up caches
    warm_up_caches()
    
    # Test TF-IDF
    print("\nTesting TF-IDF search...")
    start_time = time.time()
    results = optimized_tfidf_search("machine learning", top_k=3)
    end_time = time.time()
    print(f"TF-IDF: {len(results)} results in {end_time - start_time:.3f}s")
    
    # Test semantic
    print("\nTesting semantic search...")
    start_time = time.time()
    results = optimized_semantic_search("neural network", top_k=3)
    end_time = time.time()
    print(f"Semantic: {len(results)} results in {end_time - start_time:.3f}s")
    
    print("\nOptimized search functions tested!")

