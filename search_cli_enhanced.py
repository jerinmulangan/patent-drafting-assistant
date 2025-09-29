#!/usr/bin/env python3
# Enhanced search CLI with snippet generation, metadata, re-ranking, and logging

from argparse import ArgumentParser
from search_service import run_search, format_results_for_cli, SearchRequest
import time


def run_search_cli(query, mode, top_k, alpha, tfidf_weight, semantic_weight, 
                   rerank, show_snippets, show_metadata, log_enabled):
    # Run search with specified parameters using the centralized search service
    try:
        # Create search request
        request = SearchRequest(
            query=query,
            mode=mode,
            top_k=top_k,
            alpha=alpha,
            tfidf_weight=tfidf_weight,
            semantic_weight=semantic_weight,
            rerank=rerank,
            include_snippets=show_snippets,
            include_metadata=show_metadata,
            log_enabled=log_enabled
        )
        
        # Run search
        results, metadata = run_search(request)
        
        # Format and display results
        format_results_for_cli(results, mode.title(), query)
        
        print(f"\nSearch completed in {metadata['search_time']:.3f} seconds")
        print(f"Found {metadata['total_results']} results")

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
    run_search_cli(
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