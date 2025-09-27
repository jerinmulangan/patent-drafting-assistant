#!/usr/bin/env python3
# compare different search modes (TF-IDF, semantic, hybrid) on sample queries

import sys
import time
from pathlib import Path
from argparse import ArgumentParser

sys.path.append(str(Path(__file__).parent))

from embed_tfidf import search as search_tfidf
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid, search_hybrid_advanced

# run all search modes and compare results
def run_search_comparison(query, top_k=5):
    print(f"\n{'='*80}")
    print(f"Search Query: '{query}'")
    print(f"{'='*80}")
    
    results = {}
    timings = {}
    
    # TF-IDF Search
    try:
        start_time = time.time()
        tfidf_results = search_tfidf(query, top_k=top_k)
        timings['TF-IDF'] = time.time() - start_time
        results['TF-IDF'] = tfidf_results
        print(f"\nTF-IDF Results (took {timings['TF-IDF']:.3f}s):")
        print("-" * 40)
        for rank, (doc_id, score) in enumerate(tfidf_results, 1):
            print(f"{rank}. {doc_id}\t{score:.4f}")
    except Exception as e:
        print(f"TF-IDF Error: {e}")
        results['TF-IDF'] = []
        timings['TF-IDF'] = 0
    
    # Semantic Search
    try:
        start_time = time.time()
        semantic_results = search_semantic(query, top_k=top_k)
        timings['Semantic'] = time.time() - start_time
        results['Semantic'] = semantic_results
        print(f"\nSemantic Results (took {timings['Semantic']:.3f}s):")
        print("-" * 40)
        for rank, (doc_id, score, meta) in enumerate(semantic_results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"{rank}. {doc_id}\t{score:.4f}\t{title}")
    except Exception as e:
        print(f"Semantic Error: {e}")
        results['Semantic'] = []
        timings['Semantic'] = 0
    
    # Hybrid Search
    try:
        start_time = time.time()
        hybrid_results = search_hybrid(query, top_k=top_k, alpha=0.5)
        timings['Hybrid'] = time.time() - start_time
        results['Hybrid'] = hybrid_results
        print(f"\nHybrid Results (took {timings['Hybrid']:.3f}s):")
        print("-" * 40)
        for rank, (doc_id, score, meta) in enumerate(hybrid_results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"{rank}. {doc_id}\t{score:.4f}\t{title}")
    except Exception as e:
        print(f"Hybrid Error: {e}")
        results['Hybrid'] = []
        timings['Hybrid'] = 0
    
    # Advanced Hybrid Search
    try:
        start_time = time.time()
        adv_hybrid_results = search_hybrid_advanced(query, top_k=top_k, tfidf_weight=0.3, semantic_weight=0.7)
        timings['Advanced Hybrid'] = time.time() - start_time
        results['Advanced Hybrid'] = adv_hybrid_results
        print(f"\nAdvanced Hybrid Results (took {timings['Advanced Hybrid']:.3f}s):")
        print("-" * 40)
        for rank, (doc_id, score, meta) in enumerate(adv_hybrid_results, 1):
            title = meta.get("title", "No title")[:50]
            print(f"{rank}. {doc_id}\t{score:.4f}\t{title}")
    except Exception as e:
        print(f"Advanced Hybrid Error: {e}")
        results['Advanced Hybrid'] = []
        timings['Advanced Hybrid'] = 0
    
    # Performance Summary
    print(f"\n{'='*80}")
    print("Performance Summary")
    print(f"{'='*80}")
    for mode, timing in timings.items():
        print(f"{mode:15}: {timing:.3f}s")
    
    return results, timings

# analyze overlap between different search modes
def analyze_result_overlap(results):
    print(f"\n{'='*80}")
    print("Result Overlap Analysis")
    print(f"{'='*80}")
    
    # extract document IDs from results
    doc_sets = {}
    for mode, mode_results in results.items():
        if mode == 'TF-IDF':
            doc_sets[mode] = set(doc_id for doc_id, _ in mode_results)
        else:
            doc_sets[mode] = set(doc_id for doc_id, _, _ in mode_results)
    
    # calculate pairwise overlaps
    modes = list(doc_sets.keys())
    for i, mode1 in enumerate(modes):
        for mode2 in modes[i+1:]:
            overlap = doc_sets[mode1] & doc_sets[mode2]
            union = doc_sets[mode1] | doc_sets[mode2]
            jaccard = len(overlap) / len(union) if union else 0
            print(f"{mode1} ∩ {mode2:15}: {len(overlap)} docs, Jaccard: {jaccard:.3f}")


def main():
    parser = ArgumentParser(description="Compare different search modes")
    parser.add_argument("--queries", nargs="+", 
                       default=["machine learning", "artificial intelligence", "neural network", "data processing"],
                       help="Queries to test")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results per query")
    args = parser.parse_args()
    
    print("Patent Search Mode Comparison")
    print("="*80)
    
    all_results = {}
    all_timings = {}
    
    for query in args.queries:
        results, timings = run_search_comparison(query, args.top_k)
        all_results[query] = results
        all_timings[query] = timings
        
        # analyze overlap for this query
        analyze_result_overlap(results)
    
    # overall performance summary
    print(f"\n{'='*80}")
    print("Overall Performance Summary")
    print(f"{'='*80}")
    
    avg_timings = {}
    for mode in ["TF-IDF", "Semantic", "Hybrid", "Advanced Hybrid"]:
        if mode in all_timings[args.queries[0]]:
            avg_timing = sum(timings.get(mode, 0) for timings in all_timings.values()) / len(args.queries)
            avg_timings[mode] = avg_timing
            print(f"{mode:15}: {avg_timing:.3f}s average")
    
    print(f"\nRecommendations:")
    print(f"- Fastest: {min(avg_timings, key=avg_timings.get)}")
    print(f"- Use TF-IDF for exact keyword matches")
    print(f"- Use Semantic for conceptual similarity")
    print(f"- Use Hybrid for balanced results")


if __name__ == "__main__":
    main()

