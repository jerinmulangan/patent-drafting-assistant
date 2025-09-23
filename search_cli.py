from argparse import ArgumentParser
from embed_tfidf import search


if __name__ == "__main__":
    parser = ArgumentParser(description="Search preprocessed patents using TF-IDF cosine similarity")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to show")
    args = parser.parse_args()

    results = search(args.query, top_k=args.top_k)
    for rank, (item_id, score) in enumerate(results, start=1):
        print(f"{rank}. {item_id}\t{score:.4f}")


