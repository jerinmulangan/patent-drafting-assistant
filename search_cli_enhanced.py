#!/usr/bin/env python3
# Enhanced search CLI with snippet generation, metadata, re-ranking, and logging


from argparse import ArgumentParser
from embed_tfidf import search as search_tfidf, search_with_metadata as search_tfidf_with_metadata
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid, search_hybrid_advanced
from search_utils import format_search_result, generate_snippet, log_query, load_patent_metadata
import time


def format_results(results, mode_name, query="", show_snippets=True, show_metadata=True):
    # Format search results for display with enhanced information
    print(f"\n{mode_name} search results:")
    
    if len(results) == 0:
        print("No results found.")
        return
    
    metadata = load_patent_metadata()
    
    for rank, result in enumerate(results, start=1):
        if len(result) == 2:  # TF-IDF results (doc_id, score)
            item_id, score = result
            
            # Get metadata for TF-IDF results
            base_doc_id = item_id.split('_chunk')[0] if '_chunk' in item_id else item_id
            meta = metadata.get(base_doc_id, {})
            title = meta.get("title", "No title")
            doc_type = meta.get("doc_type", "unknown")
            
            print(f"\n{rank}.{base_doc_id} ({doc_type}) - Score: {score:.4f}")
            print(f"Title: {title}")
            
            # Show snippet if requested
            if show_snippets and query:
                from search_utils import get_chunk_text
                chunk_text = get_chunk_text(item_id)
                if chunk_text:
                    snippet = generate_snippet(chunk_text, query, max_length=200)
                    print(f"Snippet: {snippet}")
            
            
        else:  # Semantic/Hybrid results (doc_id, score, metadata)
            item_id, score, meta = result
            
            # Extract base document info
            base_doc_id = item_id.split('_chunk')[0] if '_chunk' in item_id else item_id
            title = meta.get("title", "No title")
            doc_type = meta.get("doc_type", "unknown")
            
            # Display result header
            print(f"\n{rank}.{base_doc_id} ({doc_type}) - Score: {score:.4f}")
            print(f"Title: {title}")
            
            # Show snippet if requested
            if show_snippets and query and meta.get("chunk_text"):
                snippet = generate_snippet(meta["chunk_text"], query, max_length=200)
                print(f"Snippet: {snippet}")
            
            # Show additional metadata if requested
            if show_metadata:
                source_file = meta.get("source_file", "")
                if source_file:
                    print(f"Source: {source_file}")
            



def run_search(query, mode, top_k, alpha, tfidf_weight, semantic_weight, 
               rerank, show_snippets, show_metadata, log_enabled):
    # Run search with specified parameters
    start_time = time.time()
    
    try:
        if mode == "tfidf":
            results = search_tfidf_with_metadata(query, top_k=top_k)
            
        elif mode == "semantic":
            results = search_semantic(query, top_k=top_k, rerank=rerank, 
                                   keyword_weight=0.3, semantic_weight=0.7)
            
        elif mode == "hybrid":
            results = search_hybrid(query, top_k=top_k, alpha=alpha, rerank=rerank,
                                  keyword_weight=0.3, semantic_weight=0.7)
            
        elif mode == "hybrid-advanced":
            results = search_hybrid_advanced(query, top_k=top_k, 
                                           tfidf_weight=tfidf_weight, 
                                           semantic_weight=semantic_weight)
        
        search_time = time.time() - start_time
        
        # Format and display results
        format_results(results, mode.title(), query, show_snippets, show_metadata)
        
        # Log query if enabled
        if log_enabled:
            # Convert results to simple format for logging
            simple_results = [(doc_id, score) for doc_id, score, _ in results] if len(results) > 0 and len(results[0]) == 3 else results
            log_query(query, mode, simple_results)
        
        print(f"\nSearch completed in {search_time:.3f} seconds")
        print(f"Found {len(results)} results")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure required indices are built:")
        print("  - For TF-IDF: python embed_tfidf.py build")
        print("  - For semantic: python embed_semantic.py build")
        print("  - For hybrid: Both TF-IDF and semantic indices are required")
    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = ArgumentParser(description="Enhanced patent search with snippets, metadata, and logging")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--mode", choices=["tfidf", "semantic", "hybrid", "hybrid-advanced"], 
                       default="tfidf", help="Search mode")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to show")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for semantic search in hybrid mode (0.0-1.0)")
    parser.add_argument("--tfidf_weight", type=float, default=0.3, help="TF-IDF weight for advanced hybrid mode")
    parser.add_argument("--semantic_weight", type=float, default=0.7, help="Semantic weight for advanced hybrid mode")
    parser.add_argument("--rerank", action="store_true", help="Enable keyword-based re-ranking")
    parser.add_argument("--no-snippets", action="store_true", help="Disable snippet generation")
    parser.add_argument("--no-metadata", action="store_true", help="Disable metadata display")
    parser.add_argument("--log", action="store_true", help="Enable query logging")
    
    args = parser.parse_args()
    
    # Run the search
    run_search(
        query=args.query,
        mode=args.mode,
        top_k=args.top_k,
        alpha=args.alpha,
        tfidf_weight=args.tfidf_weight,
        semantic_weight=args.semantic_weight,
        rerank=args.rerank,
        show_snippets=not args.no_snippets,
        show_metadata=not args.no_metadata,
        log_enabled=args.log
    )


if __name__ == "__main__":
    main()
