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
    parser = ArgumentParser(description="Patent search and draft generation CLI")

    # Mutually exclusive group: either --query or --description is required
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', '-q', type=str, help='Search query (for search mode)')
    group.add_argument('--description', '-d', type=str, help='Description for patent draft generation')

    # Search-specific options
    parser.add_argument('--mode', choices=['tfidf', 'semantic', 'hybrid', 'hybrid-advanced'],
                        default='tfidf', help='Search mode (default: tfidf)')
    parser.add_argument('--top_k', type=int, default=5, help='Number of search results to show (default: 5)')
    parser.add_argument('--alpha', type=float, default=0.5,
                        help='Weight for semantic search in hybrid mode (0.0-1.0)')
    parser.add_argument('--tfidf_weight', type=float, default=0.3,
                        help='TF-IDF weight for advanced hybrid mode')
    parser.add_argument('--semantic_weight', type=float, default=0.7,
                        help='Semantic weight for advanced hybrid mode')

    # Draft-generation / similarity-search options
    parser.add_argument('--with-similarity', '-s', action='store_true',
                        help='After generating a draft, run similarity search on claims')
    parser.add_argument('--search-top-k', type=int, default=5,
                        help='Number of similar patents to return (default: 5)')
    parser.add_argument('--search-mode', choices=['tfidf', 'semantic', 'hybrid', 'hybrid-advanced'],
                        default='semantic', help='Search mode for similarity search (default: semantic)')

    args = parser.parse_args()

    try:
        # SEARCH MODE
        if args.query:
            if args.mode == 'tfidf':
                results = search_tfidf(args.query, top_k=args.top_k)
                format_results(results, 'TF-IDF')
            elif args.mode == 'semantic':
                results = search_semantic(args.query, top_k=args.top_k)
                format_results(results, 'Semantic')
            elif args.mode == 'hybrid':
                results = search_hybrid(args.query, top_k=args.top_k, alpha=args.alpha)
                format_results(results, 'Hybrid')
            elif args.mode == 'hybrid-advanced':
                results = search_hybrid_advanced(
                    args.query,
                    top_k=args.top_k,
                    tfidf_weight=args.tfidf_weight,
                    semantic_weight=args.semantic_weight,
                )
                format_results(results, 'Advanced Hybrid')
        # DRAFT GENERATION MODE
        elif args.description:
            import requests
            if args.with_similarity:
                print('\nGenerating draft and searching for similar patents...')
                endpoint = 'http://localhost:8000/api/v1/generate_with_search'
            else:
                print('\nGenerating patent draft...')
                endpoint = 'http://localhost:8000/api/v1/generate_draft'

            payload = {
                'description': args.description,
                'search_mode': args.search_mode,
                'search_top_k': args.search_top_k,
            }
            response = requests.post(endpoint, json=payload)
            if response.status_code == 200:
                data = response.json()
                print('\n=== Generated Draft ===')
                print(data.get('draft', 'No draft returned'))
                if args.with_similarity:
                    print('\n=== Similar Patents ===')
                    for i, pat in enumerate(data.get('similar_patents', []), start=1):
                        title = pat.get('title', 'No title')
                        score = pat.get('score', 0)
                        print(f"{i}. {title} (Score: {score:.4f})")
                        if pat.get('snippet'):
                            print(f"   {pat['snippet']}")
            else:
                print(f"Error: {response.status_code} {response.text}")

    except FileNotFoundError as e:
        print(f'Error: {e}')
        print('Make sure required indices are built:')
        print('  - For TF-IDF: python embed_tfidf.py build')
        print('  - For semantic: python embed_semantic.py build')
        print('  - For hybrid: Both TF-IDF and semantic indices are required')
    except Exception as e:
        print(f'Unexpected error: {e}')


