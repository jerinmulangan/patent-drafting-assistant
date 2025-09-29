from argparse import ArgumentParser
from embed_tfidf import search as search_tfidf
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid, search_hybrid_advanced


def format_results(results, mode_name):

    print(f"\n{mode_name} search results:")

    
    if len(results) == 0:
        print("No results found.")
        return
    
    for rank, result in enumerate(results, start=1):
        if len(result) == 2:  
            item_id, score = result
            print(f"{rank}. {item_id}\t{score:.4f}")
        else:  
            item_id, score, meta = result
            title = meta.get("title", "No title")[:60]
            print(f"{rank}. {item_id}\t{score:.4f}\t{title}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Search preprocessed patents using TF-IDF, semantic, or hybrid search")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--mode", choices=["tfidf", "semantic", "hybrid", "hybrid-advanced"], 
                       default="tfidf", help="Search mode")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to show")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for semantic search in hybrid mode (0.0-1.0)")
    parser.add_argument("--tfidf_weight", type=float, default=0.3, help="TF-IDF weight for advanced hybrid mode")
    parser.add_argument("--semantic_weight", type=float, default=0.7, help="Semantic weight for advanced hybrid mode")
    args = parser.parse_args()

    try:
        if args.mode == "tfidf":
            results = search_tfidf(args.query, top_k=args.top_k)
            format_results(results, "TF-IDF")
            
        elif args.mode == "semantic":
            results = search_semantic(args.query, top_k=args.top_k)
            format_results(results, "Semantic")
            
        elif args.mode == "hybrid":
            results = search_hybrid(args.query, top_k=args.top_k, alpha=args.alpha)
            format_results(results, "Hybrid")
            
        elif args.mode == "hybrid-advanced":
            results = search_hybrid_advanced(
                args.query, 
                top_k=args.top_k, 
                tfidf_weight=args.tfidf_weight, 
                semantic_weight=args.semantic_weight
            )
            format_results(results, "Advanced Hybrid")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure required indices are built:")
        print("  - For TF-IDF: python embed_tfidf.py build")
        print("  - For semantic: python embed_semantic.py build")
        print("  - For hybrid: Both TF-IDF and semantic indices are required")
    except Exception as e:
        print(f"Error: {e}")


