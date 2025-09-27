import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
from argparse import ArgumentParser
from embed_tfidf import load_index as load_tfidf_index, search as search_tfidf
from embed_semantic import load_semantic_index, search_semantic


def search_hybrid(query: str, top_k: int = 5, alpha: float = 0.5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Hybrid search combining TF-IDF and semantic search.
    
    Args:
        query: Search query
        top_k: Number of results to return
        alpha: Weight for semantic search (0.0 = only TF-IDF, 1.0 = only semantic)
    """
    # Get TF-IDF results
    tfidf_results = search_tfidf(query, top_k=top_k * 2) 
    tfidf_scores = {doc_id: score for doc_id, score in tfidf_results}
    
    # Get semantic results
    semantic_results = search_semantic(query, top_k=top_k * 2)
    semantic_scores = {doc_id: score for doc_id, score, _ in semantic_results}
    semantic_metadata = {doc_id: meta for doc_id, _, meta in semantic_results}
    
    # Combine scores
    all_docs = set(tfidf_scores.keys()) | set(semantic_scores.keys())
    combined_scores = {}
    
    for doc_id in all_docs:
        tfidf_score = tfidf_scores.get(doc_id, 0.0)
        semantic_score = semantic_scores.get(doc_id, 0.0)
        
        # Normalize scores to [0, 1] range
        tfidf_norm = tfidf_score
        semantic_norm = semantic_score
        
        # Combine with weighted average
        combined_score = (1 - alpha) * tfidf_norm + alpha * semantic_norm
        combined_scores[doc_id] = combined_score
    
    # Sort by combined score
    sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top_k results with metadata
    results = []
    for doc_id, score in sorted_docs[:top_k]:
        metadata = semantic_metadata.get(doc_id, {"title": "Unknown", "doc_id": doc_id})
        results.append((doc_id, score, metadata))
    
    return results


def search_hybrid_advanced(query: str, top_k: int = 5, tfidf_weight: float = 0.3, 
                          semantic_weight: float = 0.7, min_tfidf_score: float = 0.1) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Advanced hybrid search with more sophisticated scoring.
    
    Args:
        query: Search query
        top_k: Number of results to return
        tfidf_weight: Weight for TF-IDF scores
        semantic_weight: Weight for semantic scores
        min_tfidf_score: Minimum TF-IDF score threshold
    """
    # Get TF-IDF results
    tfidf_results = search_tfidf(query, top_k=top_k * 3)
    tfidf_scores = {doc_id: score for doc_id, score in tfidf_results if score >= min_tfidf_score}
    
    # Get semantic results
    semantic_results = search_semantic(query, top_k=top_k * 3)
    semantic_scores = {doc_id: score for doc_id, score, _ in semantic_results}
    semantic_metadata = {doc_id: meta for doc_id, _, meta in semantic_results}
    
    # Normalize scores using min-max scaling
    if tfidf_scores:
        tfidf_min, tfidf_max = min(tfidf_scores.values()), max(tfidf_scores.values())
        tfidf_range = tfidf_max - tfidf_min if tfidf_max > tfidf_min else 1.0
        tfidf_scores = {doc_id: (score - tfidf_min) / tfidf_range for doc_id, score in tfidf_scores.items()}
    
    if semantic_scores:
        semantic_min, semantic_max = min(semantic_scores.values()), max(semantic_scores.values())
        semantic_range = semantic_max - semantic_min if semantic_max > semantic_min else 1.0
        semantic_scores = {doc_id: (score - semantic_min) / semantic_range for doc_id, score in semantic_scores.items()}
    
    # Combine scores
    all_docs = set(tfidf_scores.keys()) | set(semantic_scores.keys())
    combined_scores = {}
    
    for doc_id in all_docs:
        tfidf_score = tfidf_scores.get(doc_id, 0.0)
        semantic_score = semantic_scores.get(doc_id, 0.0)
        
        # Weighted combination
        combined_score = tfidf_weight * tfidf_score + semantic_weight * semantic_score
        combined_scores[doc_id] = combined_score
    
    # Sort by combined score
    sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top_k results with metadata
    results = []
    for doc_id, score in sorted_docs[:top_k]:
        metadata = semantic_metadata.get(doc_id, {"title": "Unknown", "doc_id": doc_id})
        results.append((doc_id, score, metadata))
    
    return results


if __name__ == "__main__":
    parser = ArgumentParser(description="Hybrid search combining TF-IDF and semantic search")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for semantic search (0.0-1.0)")
    parser.add_argument("--mode", choices=["simple", "advanced"], default="simple", help="Hybrid search mode")
    parser.add_argument("--tfidf_weight", type=float, default=0.3, help="TF-IDF weight for advanced mode")
    parser.add_argument("--semantic_weight", type=float, default=0.7, help="Semantic weight for advanced mode")
    args = parser.parse_args()

    if args.mode == "simple":
        results = search_hybrid(args.query, top_k=args.top_k, alpha=args.alpha)
    else:
        results = search_hybrid_advanced(
            args.query, 
            top_k=args.top_k, 
            tfidf_weight=args.tfidf_weight, 
            semantic_weight=args.semantic_weight
        )
    
    print(f"\nHybrid search results for: '{args.query}'")

    for rank, (item_id, score, meta) in enumerate(results, start=1):
        title = meta.get("title", "No title")[:60]
        print(f"{rank}. {item_id}\t{score:.4f}\t{title}")

