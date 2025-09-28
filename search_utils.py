#!/usr/bin/env python3
# Utility functions for search result enrichment and formatting.

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict


def load_patent_metadata() -> Dict[str, Dict[str, Any]]:
    # Load patent metadata from grants.jsonl and applications.jsonl
    metadata = {}
    
    for file_path in ["grants.jsonl", "applications.jsonl"]:
        full_path = Path("./data/processed") / file_path
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                for line in f:
                    patent = json.loads(line)
                    doc_id = patent.get("doc_id")
                    if doc_id:
                        metadata[doc_id] = {
                            "title": patent.get("title", ""),
                            "abstract": patent.get("abstract", ""),
                            "source_file": patent.get("source_file", ""),
                            "doc_type": "grant" if "grant" in file_path else "application"
                        }
    
    return metadata


def generate_snippet(text: str, query: str, max_length: int = 200) -> str:
    """
    Generate a snippet from text, highlighting query terms.
    
    Args:
        text: The text to snippet
        query: The search query
        max_length: Maximum length of snippet
    
    Returns:
        Formatted snippet with highlighted query terms
    """
    if not text or not query:
        return text[:max_length] + "..." if len(text) > max_length else text
    
    # Clean and tokenize query
    query_terms = re.findall(r'\b\w+\b', query.lower())
    
    # Find the best position to start the snippet
    text_lower = text.lower()
    best_start = 0
    max_matches = 0
    
    # Look for positions with most query term matches
    for i in range(0, len(text) - max_length + 1, 50):  # Check every 50 chars
        snippet_text = text_lower[i:i + max_length]
        matches = sum(1 for term in query_terms if term in snippet_text)
        if matches > max_matches:
            max_matches = matches
            best_start = i
    
    # Extract snippet
    snippet = text[best_start:best_start + max_length]
    
    # Highlight query terms
    for term in query_terms:
        if len(term) > 2:  # Only highlight terms longer than 2 chars
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            snippet = pattern.sub(f"**{term}**", snippet)
    
    # Add ellipsis if needed
    if best_start > 0:
        snippet = "..." + snippet
    if best_start + max_length < len(text):
        snippet = snippet + "..."
    
    return snippet


def format_search_result(result: Tuple[str, float], metadata: Dict[str, Dict[str, Any]], 
                        query: str = "", show_snippet: bool = True) -> str:
    """
    Format a single search result with metadata and snippet.
    
    Args:
        result: Tuple of (doc_id, score)
        metadata: Patent metadata dictionary
        query: Search query for snippet generation
        show_snippet: Whether to include snippet
    
    Returns:
        Formatted result string
    """
    doc_id, score = result
    meta = metadata.get(doc_id, {})
    
    # Extract base doc_id (remove chunk suffix)
    base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
    
    # Get metadata for base document
    base_meta = metadata.get(base_doc_id, meta)
    
    title = base_meta.get("title", "No title")
    doc_type = base_meta.get("doc_type", "unknown")
    
    # Format the result
    lines = []
    lines.append(f"{base_doc_id} ({doc_type}) - Score: {score:.4f}")
    lines.append(f"Title: {title}")
    
    if show_snippet and query:
        # Get the text for snippet generation
        text = get_chunk_text(doc_id)
        if text:
            snippet = generate_snippet(text, query)
            lines.append(f"Snippet: {snippet}")
    
    return "\n".join(lines)


def get_chunk_text(chunk_id: str) -> Optional[str]:
    # Get the text content for a chunk ID
    chunks_file = Path("./data/processed/chunks.jsonl")
    if not chunks_file.exists():
        return None
    
    with open(chunks_file, "r", encoding="utf-8") as f:
        for line in f:
            chunk_data = json.loads(line)
            if chunk_data.get("chunk_id") == chunk_id:
                return chunk_data.get("text", "")
    return None


def compute_keyword_overlap_score(text: str, query: str) -> float:
    """
    Compute keyword overlap score between text and query.
    
    Args:
        text: Text to compare
        query: Query to compare against
    
    Returns:
        Jaccard similarity score between 0 and 1
    """
    if not text or not query:
        return 0.0
    
    # Tokenize and normalize
    text_tokens = set(re.findall(r'\b\w+\b', text.lower()))
    query_tokens = set(re.findall(r'\b\w+\b', query.lower()))
    
    # Remove very short tokens
    text_tokens = {token for token in text_tokens if len(token) > 2}
    query_tokens = {token for token in query_tokens if len(token) > 2}
    
    if not query_tokens:
        return 0.0
    
    # Compute Jaccard similarity
    intersection = len(text_tokens & query_tokens)
    union = len(text_tokens | query_tokens)
    
    return intersection / union if union > 0 else 0.0


def rerank_results(results: List[Tuple[str, float]], query: str, 
                  keyword_weight: float = 0.3, semantic_weight: float = 0.7) -> List[Tuple[str, float]]:
    """
    Re-rank results by combining semantic scores with keyword overlap.
    
    Args:
        results: List of (doc_id, score) tuples
        query: Search query
        keyword_weight: Weight for keyword overlap score
        semantic_weight: Weight for semantic score
    
    Returns:
        Re-ranked list of (doc_id, score) tuples
    """
    if not results or not query:
        return results
    
    reranked = []
    
    for doc_id, semantic_score in results:
        # Get text for keyword analysis
        text = get_chunk_text(doc_id)
        if not text:
            reranked.append((doc_id, semantic_score))
            continue
        
        # Compute keyword overlap score
        keyword_score = compute_keyword_overlap_score(text, query)
        
        # Combine scores
        combined_score = (semantic_weight * semantic_score + 
                         keyword_weight * keyword_score)
        
        reranked.append((doc_id, combined_score))
    
    # Sort by combined score
    reranked.sort(key=lambda x: x[1], reverse=True)
    
    return reranked


def log_query(query: str, mode: str, results: List[Tuple[str, float]], 
              log_file: str = "query_log.jsonl") -> None:
    """
    Log query and results to a file.
    
    Args:
        query: Search query
        mode: Search mode used
        results: Search results
        log_file: Log file path
    """
    import datetime
    
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "mode": mode,
        "num_results": len(results),
        "top_scores": [score for _, score in results[:5]],  # Top 5 scores
        "top_docs": [doc_id for doc_id, _ in results[:5]]   # Top 5 document IDs
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def analyze_query_log(log_file: str = "query_log.jsonl") -> Dict[str, Any]:
    """
    Analyze query log statistics.
    
    Args:
        log_file: Log file path
    
    Returns:
        Dictionary with analysis results
    """
    if not Path(log_file).exists():
        return {"error": "Log file not found"}
    
    queries = []
    modes = defaultdict(int)
    scores = []
    
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            queries.append(entry["query"])
            modes[entry["mode"]] += 1
            scores.extend(entry["top_scores"])
    
    # Find most common queries
    query_counts = defaultdict(int)
    for query in queries:
        query_counts[query] += 1
    
    most_common = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_queries": len(queries),
        "unique_queries": len(set(queries)),
        "mode_usage": dict(modes),
        "most_common_queries": most_common,
        "average_top_score": sum(scores) / len(scores) if scores else 0,
        "score_distribution": {
            "min": min(scores) if scores else 0,
            "max": max(scores) if scores else 0,
            "avg": sum(scores) / len(scores) if scores else 0
        }
    }


if __name__ == "__main__":
    # Test the utilities
    print("Testing search utilities")
    
    # Test metadata loading
    metadata = load_patent_metadata()
    print(f"Loaded metadata for {len(metadata)} patents")
    
    # Test snippet generation
    sample_text = "This is a machine learning algorithm that processes neural networks for artificial intelligence applications."
    snippet = generate_snippet(sample_text, "machine learning neural network")
    print(f"Sample snippet: {snippet}")
    
    # Test keyword overlap
    score = compute_keyword_overlap_score(sample_text, "machine learning algorithm")
    print(f"Keyword overlap score: {score:.3f}")
    
    print("Utilities test completed!")
