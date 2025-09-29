#!/usr/bin/env python3
# Demonstration of all enhanced search features


import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def demo_snippet_generation():
    # Demonstrate snippet generation
    print("1. SNIPPET GENERATION DEMONSTRATION")
    
    from search_utils import generate_snippet
    
    sample_texts = [
        "This patent describes a machine learning algorithm that uses neural networks for image recognition and computer vision applications.",
        "The system implements artificial intelligence techniques including deep learning models for natural language processing tasks.",
        "A novel approach to data processing using distributed computing architecture for real-time analytics and predictive modeling."
    ]
    
    query = "machine learning artificial intelligence"
    
    for i, text in enumerate(sample_texts, 1):
        snippet = generate_snippet(text, query, max_length=120)
        print(f"\nText {i}: {text}")
        print(f"Snippet: {snippet}")

def demo_metadata_enrichment():
    # Demonstrate metadata enrichment
    print("2. METADATA ENRICHMENT DEMONSTRATION")
    
    from embed_tfidf import search_with_metadata
    from embed_semantic import search_semantic
    
    query = "machine learning"
    
    print(f"\nQuery: '{query}'")
    
    # TF-IDF with metadata
    print("TF-IDF Results with Metadata:")
    try:
        results = search_with_metadata(query, top_k=3)
        for rank, (doc_id, score, meta) in enumerate(results, 1):
            print(f"{rank}. {doc_id} - {score:.4f}")
            print(f"   Title: {meta.get('title', 'No title')}")
            print(f"   Type: {meta.get('doc_type', 'unknown')}")
            print(f"   Source: {meta.get('source_file', 'Unknown')}")
            print()
    except Exception as e:
        print(f"Error: {e}")
    
    # Semantic with metadata
    print("Semantic Results with Metadata:")
    try:
        results = search_semantic(query, top_k=3)
        for rank, (doc_id, score, meta) in enumerate(results, 1):
            print(f"{rank}. {doc_id} - {score:.4f}")
            print(f"   Title: {meta.get('title', 'No title')}")
            print(f"   Type: {meta.get('doc_type', 'unknown')}")
            print()
    except Exception as e:
        print(f"Error: {e}")

def demo_reranking():
    # Demonstrate re-ranking functionality
    print("3. RE-RANKING DEMONSTRATION")
    
    from embed_semantic import search_semantic
    from search_utils import compute_keyword_overlap_score
    
    query = "neural network deep learning"
    
    print(f"\nQuery: '{query}'")

    
    # Without re-ranking
    print("Semantic Search (No Re-ranking):")
    try:
        results_no_rerank = search_semantic(query, top_k=3, rerank=False)
        for rank, (doc_id, score, meta) in enumerate(results_no_rerank, 1):
            print(f"{rank}. {doc_id} - {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # With re-ranking
    print("\nSemantic Search (With Re-ranking):")
    try:
        results_rerank = search_semantic(query, top_k=3, rerank=True, keyword_weight=0.3, semantic_weight=0.7)
        for rank, (doc_id, score, meta) in enumerate(results_rerank, 1):
            print(f"{rank}. {doc_id} - {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")

def demo_query_logging():
    # Demonstrate query logging

    print("4. QUERY LOGGING DEMONSTRATION")

    
    from search_utils import log_query, analyze_query_log
    
    # Simulate some queries
    test_queries = [
        ("machine learning algorithm", "tfidf", [("doc1", 0.95), ("doc2", 0.87)]),
        ("neural network processing", "semantic", [("doc3", 0.92), ("doc4", 0.85)]),
        ("artificial intelligence system", "hybrid", [("doc5", 0.89), ("doc6", 0.83)])
    ]
    
    log_file = "demo_log.jsonl"
    
    print("Logging test queries")
    for query, mode, results in test_queries:
        log_query(query, mode, results, log_file)
        print(f"  Logged: '{query}' ({mode})")
    
    print(f"\nAnalyzing log file: {log_file}")
    analysis = analyze_query_log(log_file)
    
    print("Log Analysis Results:")
    print(f"  Total queries: {analysis['total_queries']}")
    print(f"  Unique queries: {analysis['unique_queries']}")
    print(f"  Mode usage: {analysis['mode_usage']}")
    print(f"  Average score: {analysis['average_top_score']:.4f}")
    
    print(f"\nMost common queries:")
    for query, count in analysis['most_common_queries']:
        print(f"  '{query}': {count} times")

def demo_batch_processing():
    # Demonstrate batch processing

    print("5. BATCH PROCESSING DEMONSTRATION")

    
    # Create a small test queries file
    test_queries = [
        "machine learning",
        "neural network",
        "artificial intelligence"
    ]
    
    test_file = "demo_queries.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        for query in test_queries:
            f.write(query + "\n")
    
    print(f"Created test queries file: {test_file}")
    print("Queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"  {i}. {query}")
    
    print("\nNote: To run batch processing, use:")
    print(f"  python batch_search.py {test_file} --mode tfidf --top_k 3")

def demo_enhanced_cli():
    # Demonstrate enhanced CLI features
    print("6. ENHANCED CLI FEATURES DEMONSTRATION")

    
    print("Enhanced CLI Usage Examples:")
    print("\n1. Basic search with snippets:")
    print("   python search_cli_enhanced.py 'machine learning' --mode tfidf --top_k 3")
    
    print("\n2. Semantic search with re-ranking:")
    print("   python search_cli_enhanced.py 'neural network' --mode semantic --rerank --top_k 3")
    
    print("\n3. Hybrid search with custom weights:")
    print("   python search_cli_enhanced.py 'AI system' --mode hybrid --alpha 0.7 --rerank")
    
    print("\n4. Search with logging enabled:")
    print("   python search_cli_enhanced.py 'deep learning' --mode semantic --log")
    
    print("\n5. Search without snippets:")
    print("   python search_cli_enhanced.py 'computer vision' --mode tfidf --no-snippets")
    
    print("\n6. Advanced hybrid with custom weights:")
    print("   python search_cli_enhanced.py 'data processing' --mode hybrid-advanced --tfidf_weight 0.4 --semantic_weight 0.6")

def main():
    print("ENHANCED PATENT SEARCH FEATURES DEMONSTRATION")

    print("This demo showcases all the new features implemented:")
    print("Snippet generation with query highlighting")
    print("Enhanced metadata display")
    print("Keyword-based re-ranking")
    print("Query logging and analysis")
    print("Batch query processing")
    print("Enhanced CLI with multiple options")
    
    # Run demonstrations
    demo_snippet_generation()
    demo_metadata_enrichment()
    demo_reranking()
    demo_query_logging()
    demo_batch_processing()
    demo_enhanced_cli()
    
    print("DEMONSTRATION COMPLETE")
    print("All enhanced features are now available:")
    print("Working: Snippet generation with query term highlighting")
    print("Working: Rich metadata display (title, type, source)")
    print("Working: Keyword-based re-ranking for better relevance")
    print("Working: Query logging for analysis and evaluation")
    print("Working: Batch processing for multiple queries")
    print("Working: Enhanced CLI with comprehensive options")
    
    print("\nNext steps:")
    print("1. Try the enhanced CLI: python search_cli_enhanced.py 'your query' --mode semantic --rerank")
    print("2. Run batch processing: python batch_search.py sample_queries.txt --mode hybrid")
    print("3. Analyze query logs: python analyze_logs.py query_log.jsonl")

if __name__ == "__main__":
    main()
