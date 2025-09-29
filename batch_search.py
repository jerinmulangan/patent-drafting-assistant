#!/usr/bin/env python3
# Batch query processing for patent search evaluation

import json
import csv
import time
from pathlib import Path
from argparse import ArgumentParser
from typing import List, Dict, Any
from embed_tfidf import search as search_tfidf, search_with_metadata as search_tfidf_with_metadata
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid, search_hybrid_advanced
from search_utils import generate_snippet, log_query, load_patent_metadata


def load_queries_from_file(file_path: str) -> List[str]:
    # Load queries from a text file (one query per line)
    queries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            query = line.strip()
             # Skip empty lines and comments
            if query and not query.startswith("#"): 
                queries.append(query)
    return queries


def run_batch_search(queries: List[str], mode: str, top_k: int = 5, 
                    alpha: float = 0.5, tfidf_weight: float = 0.3, 
                    semantic_weight: float = 0.7, rerank: bool = False) -> List[Dict[str, Any]]:
    #Run batch search on multiple queries
    results = []
    metadata = load_patent_metadata()
    
    for i, query in enumerate(queries, 1):
        print(f"Processing query {i}/{len(queries)}: '{query}'")
        
        start_time = time.time()
        
        try:
            # Run search based on mode
            if mode == "tfidf":
                search_results = search_tfidf_with_metadata(query, top_k=top_k)
            elif mode == "semantic":
                search_results = search_semantic(query, top_k=top_k, rerank=rerank,
                                               keyword_weight=0.3, semantic_weight=0.7)
            elif mode == "hybrid":
                search_results = search_hybrid(query, top_k=top_k, alpha=alpha, rerank=rerank,
                                             keyword_weight=0.3, semantic_weight=0.7)
            elif mode == "hybrid-advanced":
                search_results = search_hybrid_advanced(query, top_k=top_k,
                                                     tfidf_weight=tfidf_weight,
                                                     semantic_weight=semantic_weight)
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            search_time = time.time() - start_time
            
            # Process results
            processed_results = []
            for rank, result in enumerate(search_results, 1):
                if len(result) == 2:  # TF-IDF results
                    doc_id, score = result
                    base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
                    meta = metadata.get(base_doc_id, {})
                    processed_results.append({
                        "rank": rank,
                        "doc_id": doc_id,
                        "base_doc_id": base_doc_id,
                        "score": score,
                        "title": meta.get("title", "No title"),
                        "doc_type": meta.get("doc_type", "unknown"),
                        "snippet": ""
                    })
                else:  # Semantic/Hybrid results
                    doc_id, score, meta = result
                    base_doc_id = doc_id.split('_chunk')[0] if '_chunk' in doc_id else doc_id
                    
                    # Generate snippet
                    snippet = ""
                    if meta.get("chunk_text"):
                        snippet = generate_snippet(meta["chunk_text"], query, max_length=150)
                    
                    processed_results.append({
                        "rank": rank,
                        "doc_id": doc_id,
                        "base_doc_id": base_doc_id,
                        "score": score,
                        "title": meta.get("title", "No title"),
                        "doc_type": meta.get("doc_type", "unknown"),
                        "snippet": snippet
                    })
            
            # Store query results
            results.append({
                "query": query,
                "mode": mode,
                "search_time": search_time,
                "num_results": len(processed_results),
                "results": processed_results
            })
            
            print(f"  Completed in {search_time:.3f}s, found {len(processed_results)} results")
            
        except Exception as e:
            print(f"  Error processing query: {e}")
            results.append({
                "query": query,
                "mode": mode,
                "search_time": 0,
                "num_results": 0,
                "results": [],
                "error": str(e)
            })
    
    return results


def save_results_to_csv(results: List[Dict[str, Any]], output_file: str):
    # Save batch search results to CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            "query", "mode", "search_time", "num_results", "rank", 
            "doc_id", "base_doc_id", "score", "title", "doc_type", "snippet"
        ])
        
        # Write data
        for query_result in results:
            query = query_result["query"]
            mode = query_result["mode"]
            search_time = query_result["search_time"]
            num_results = query_result["num_results"]
            
            for result in query_result["results"]:
                writer.writerow([
                    query, mode, search_time, num_results,
                    result["rank"], result["doc_id"], result["base_doc_id"],
                    result["score"], result["title"], result["doc_type"], result["snippet"]
                ])


def save_results_to_json(results: List[Dict[str, Any]], output_file: str):
    # Save batch search results to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def generate_summary_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Generate summary statistics for batch search results
    total_queries = len(results)
    successful_queries = len([r for r in results if "error" not in r])
    failed_queries = total_queries - successful_queries
    
    total_time = sum(r["search_time"] for r in results)
    avg_time = total_time / total_queries if total_queries > 0 else 0
    
    total_results = sum(r["num_results"] for r in results)
    avg_results = total_results / total_queries if total_queries > 0 else 0
    
    # Score statistics
    all_scores = []
    for result in results:
        for res in result["results"]:
            all_scores.append(res["score"])
    
    score_stats = {}
    if all_scores:
        score_stats = {
            "min": min(all_scores),
            "max": max(all_scores),
            "avg": sum(all_scores) / len(all_scores),
            "count": len(all_scores)
        }
    
    return {
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries,
        "total_search_time": total_time,
        "average_search_time": avg_time,
        "total_results": total_results,
        "average_results_per_query": avg_results,
        "score_statistics": score_stats
    }


def main():
    parser = ArgumentParser(description="Batch query processing for patent search")
    parser.add_argument("queries_file", type=str, help="File containing queries (one per line)")
    parser.add_argument("--mode", choices=["tfidf", "semantic", "hybrid", "hybrid-advanced"], 
                       default="tfidf", help="Search mode")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results per query")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for semantic search in hybrid mode")
    parser.add_argument("--tfidf_weight", type=float, default=0.3, help="TF-IDF weight for advanced hybrid mode")
    parser.add_argument("--semantic_weight", type=float, default=0.7, help="Semantic weight for advanced hybrid mode")
    parser.add_argument("--rerank", action="store_true", help="Enable keyword-based re-ranking")
    parser.add_argument("--output", type=str, default="batch_results", help="Output file prefix")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    # Load queries
    if not Path(args.queries_file).exists():
        print(f"Error: Queries file '{args.queries_file}' not found")
        return
    
    queries = load_queries_from_file(args.queries_file)
    print(f"Loaded {len(queries)} queries from {args.queries_file}")
    
    if not queries:
        print("No queries found in file")
        return
    
    # Run batch search
    print(f"\nRunning batch search in '{args.mode}' mode")
    print(f"Parameters: top_k={args.top_k}, alpha={args.alpha}, rerank={args.rerank}")
    
    results = run_batch_search(
        queries=queries,
        mode=args.mode,
        top_k=args.top_k,
        alpha=args.alpha,
        tfidf_weight=args.tfidf_weight,
        semantic_weight=args.semantic_weight,
        rerank=args.rerank
    )
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    if args.format in ["csv", "both"]:
        csv_file = f"{args.output}_{args.mode}_{timestamp}.csv"
        save_results_to_csv(results, csv_file)
        print(f"\nResults saved to {csv_file}")
    
    if args.format in ["json", "both"]:
        json_file = f"{args.output}_{args.mode}_{timestamp}.json"
        save_results_to_json(results, json_file)
        print(f"Results saved to {json_file}")
    
    # Generate summary report
    summary = generate_summary_report(results)
    summary_file = f"{args.output}_{args.mode}_{timestamp}_summary.json"
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to {summary_file}")
    
    # Print summary
    print("BATCH SEARCH SUMMARY")
    print(f"Total queries: {summary['total_queries']}")
    print(f"Successful: {summary['successful_queries']}")
    print(f"Failed: {summary['failed_queries']}")
    print(f"Total search time: {summary['total_search_time']:.2f}s")
    print(f"Average search time: {summary['average_search_time']:.3f}s")
    print(f"Total results: {summary['total_results']}")
    print(f"Average results per query: {summary['average_results_per_query']:.1f}")
    
    if summary['score_statistics']:
        stats = summary['score_statistics']
        print(f"\nScore Statistics:")
        print(f"  Min: {stats['min']:.4f}")
        print(f"  Max: {stats['max']:.4f}")
        print(f"  Average: {stats['avg']:.4f}")
        print(f"  Total scores: {stats['count']}")


if __name__ == "__main__":
    main()
