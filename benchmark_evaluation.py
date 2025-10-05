#!/usr/bin/env python3
"""
Comprehensive benchmarking script for Patent NLP search system.
Computes precision@k, recall@k, NDCG, and other evaluation metrics.
"""

import json
import time
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
import argparse
from collections import defaultdict
# import pandas as pd  # Not needed for basic benchmarking

# Import search service
from search_service import run_search, SearchRequest


class EvaluationMetrics:
    """Compute various evaluation metrics for search results."""
    
    @staticmethod
    def precision_at_k(relevant_docs: List[str], retrieved_docs: List[str], k: int) -> float:
        """Compute Precision@k."""
        if k == 0:
            return 0.0
        
        retrieved_k = retrieved_docs[:k]
        relevant_retrieved = set(relevant_docs) & set(retrieved_k)
        return len(relevant_retrieved) / k
    
    @staticmethod
    def recall_at_k(relevant_docs: List[str], retrieved_docs: List[str], k: int) -> float:
        """Compute Recall@k."""
        if len(relevant_docs) == 0:
            return 0.0
        
        retrieved_k = retrieved_docs[:k]
        relevant_retrieved = set(relevant_docs) & set(retrieved_k)
        return len(relevant_retrieved) / len(relevant_docs)
    
    @staticmethod
    def ndcg_at_k(relevant_docs: List[str], relevance_scores: List[float], 
                  retrieved_docs: List[str], k: int) -> float:
        """Compute Normalized Discounted Cumulative Gain@k."""
        if k == 0:
            return 0.0
        
        # Create relevance mapping
        relevance_map = dict(zip(relevant_docs, relevance_scores))
        
        # Get relevance scores for retrieved documents
        retrieved_k = retrieved_docs[:k]
        relevance_retrieved = [relevance_map.get(doc, 0.0) for doc in retrieved_k]
        
        # Compute DCG@k
        dcg = 0.0
        for i, rel in enumerate(relevance_retrieved):
            dcg += rel / np.log2(i + 2)  # i+2 because log2(1) = 0
        
        # Compute IDCG@k (ideal DCG)
        ideal_relevance = sorted(relevance_scores, reverse=True)[:k]
        idcg = 0.0
        for i, rel in enumerate(ideal_relevance):
            idcg += rel / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def map_at_k(relevant_docs: List[str], retrieved_docs: List[str], k: int) -> float:
        """Compute Mean Average Precision@k."""
        if len(relevant_docs) == 0:
            return 0.0
        
        retrieved_k = retrieved_docs[:k]
        relevant_retrieved = set(relevant_docs) & set(retrieved_k)
        
        if len(relevant_retrieved) == 0:
            return 0.0
        
        # Compute average precision
        precision_sum = 0.0
        relevant_count = 0
        
        for i, doc in enumerate(retrieved_k):
            if doc in relevant_docs:
                relevant_count += 1
                precision_at_i = relevant_count / (i + 1)
                precision_sum += precision_at_i
        
        return precision_sum / len(relevant_docs)
    
    @staticmethod
    def mrr(relevant_docs: List[str], retrieved_docs: List[str]) -> float:
        """Compute Mean Reciprocal Rank."""
        if len(relevant_docs) == 0:
            return 0.0
        
        for i, doc in enumerate(retrieved_docs):
            if doc in relevant_docs:
                return 1.0 / (i + 1)
        
        return 0.0


class SearchBenchmark:
    """Main benchmarking class for search evaluation."""
    
    def __init__(self, dataset_path: str = "evaluation_dataset.json"):
        """Initialize benchmark with evaluation dataset."""
        self.dataset_path = Path(dataset_path)
        self.dataset = self._load_dataset()
        self.metrics = EvaluationMetrics()
        
    def _load_dataset(self) -> Dict[str, Any]:
        """Load evaluation dataset."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_single_query_evaluation(self, query_data: Dict[str, Any], 
                                  mode: str, top_k: int = 10) -> Dict[str, Any]:
        """Run evaluation for a single query."""
        query = query_data["query"]
        expected_patents = query_data["expected_patents"]
        relevance_scores = query_data["relevance_scores"]
        
        # Create search request
        request = SearchRequest(
            query=query,
            mode=mode,
            top_k=top_k,
            include_snippets=False,  # Skip snippets for faster evaluation
            include_metadata=False,
            log_enabled=False
        )
        
        # Run search
        start_time = time.time()
        results, metadata = run_search(request)
        search_time = time.time() - start_time
        
        # Extract document IDs from results
        retrieved_docs = [result.doc_id for result in results]
        
        # Compute metrics
        metrics = {}
        for k in [1, 3, 5, 10]:
            if k <= top_k:
                metrics[f"precision@{k}"] = self.metrics.precision_at_k(
                    expected_patents, retrieved_docs, k)
                metrics[f"recall@{k}"] = self.metrics.recall_at_k(
                    expected_patents, retrieved_docs, k)
                metrics[f"ndcg@{k}"] = self.metrics.ndcg_at_k(
                    expected_patents, relevance_scores, retrieved_docs, k)
                metrics[f"map@{k}"] = self.metrics.map_at_k(
                    expected_patents, retrieved_docs, k)
        
        metrics["mrr"] = self.metrics.mrr(expected_patents, retrieved_docs)
        metrics["search_time"] = search_time
        
        return {
            "query_id": query_data["id"],
            "query": query,
            "category": query_data["category"],
            "mode": mode,
            "expected_patents": expected_patents,
            "retrieved_patents": retrieved_docs,
            "metrics": metrics
        }
    
    def run_mode_evaluation(self, mode: str, top_k: int = 10, 
                          max_queries: int = None) -> Dict[str, Any]:
        """Run evaluation for a specific search mode."""
        print(f"\nEvaluating {mode} mode...")
        
        queries = self.dataset["queries"]
        if max_queries:
            queries = queries[:max_queries]
        
        results = []
        total_time = 0
        
        for i, query_data in enumerate(queries):
            print(f"  Processing query {i+1}/{len(queries)}: {query_data['query'][:50]}...")
            
            try:
                result = self.run_single_query_evaluation(query_data, mode, top_k)
                results.append(result)
                total_time += result["metrics"]["search_time"]
            except Exception as e:
                print(f"    Error: {e}")
                continue
        
        # Compute aggregate metrics
        aggregate_metrics = self._compute_aggregate_metrics(results)
        
        return {
            "mode": mode,
            "total_queries": len(results),
            "total_time": total_time,
            "average_time_per_query": total_time / len(results) if results else 0,
            "results": results,
            "aggregate_metrics": aggregate_metrics
        }
    
    def _compute_aggregate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute aggregate metrics across all queries."""
        if not results:
            return {}
        
        aggregate = defaultdict(list)
        
        # Collect all metric values
        for result in results:
            for metric_name, value in result["metrics"].items():
                if metric_name != "search_time":
                    aggregate[metric_name].append(value)
        
        # Compute averages
        aggregate_metrics = {}
        for metric_name, values in aggregate.items():
            aggregate_metrics[f"avg_{metric_name}"] = np.mean(values)
            aggregate_metrics[f"std_{metric_name}"] = np.std(values)
            aggregate_metrics[f"min_{metric_name}"] = np.min(values)
            aggregate_metrics[f"max_{metric_name}"] = np.max(values)
        
        return aggregate_metrics
    
    def run_comprehensive_evaluation(self, modes: List[str] = None, 
                                   top_k: int = 10, max_queries: int = None) -> Dict[str, Any]:
        """Run comprehensive evaluation across all modes."""
        if modes is None:
            modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        
        print("Starting Comprehensive Search Evaluation")
        print("=" * 60)
        print(f"Dataset: {self.dataset['metadata']['total_queries']} queries")
        print(f"Modes: {', '.join(modes)}")
        print(f"Top-K: {top_k}")
        if max_queries:
            print(f"Max queries per mode: {max_queries}")
        
        evaluation_results = {}
        
        for mode in modes:
            try:
                mode_results = self.run_mode_evaluation(mode, top_k, max_queries)
                evaluation_results[mode] = mode_results
            except Exception as e:
                print(f"Failed to evaluate {mode}: {e}")
                continue
        
        # Generate comparison report
        comparison_report = self._generate_comparison_report(evaluation_results)
        
        return {
            "evaluation_metadata": {
                "dataset_version": self.dataset["metadata"]["version"],
                "total_queries": self.dataset["metadata"]["total_queries"],
                "modes_evaluated": list(evaluation_results.keys()),
                "top_k": top_k,
                "max_queries": max_queries,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "mode_results": evaluation_results,
            "comparison_report": comparison_report
        }
    
    def _generate_comparison_report(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison report across modes."""
        if not evaluation_results:
            return {}
        
        # Create comparison table
        comparison_data = []
        
        for mode, results in evaluation_results.items():
            row = {"mode": mode}
            row.update(results["aggregate_metrics"])
            row["total_queries"] = results["total_queries"]
            row["avg_search_time"] = results["average_time_per_query"]
            comparison_data.append(row)
        
        # Find best performing mode for each metric
        best_modes = {}
        key_metrics = ["avg_precision@5", "avg_recall@5", "avg_ndcg@5", "avg_map@5", "avg_mrr"]
        
        for metric in key_metrics:
            if comparison_data and metric in comparison_data[0]:
                best_mode = max(comparison_data, key=lambda x: x.get(metric, 0))
                best_modes[metric] = {
                    "mode": best_mode["mode"],
                    "value": best_mode[metric]
                }
        
        return {
            "comparison_table": comparison_data,
            "best_modes": best_modes,
            "recommendations": self._generate_recommendations(comparison_data, best_modes)
        }
    
    def _generate_recommendations(self, comparison_data: List[Dict], 
                                best_modes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on evaluation results."""
        if not comparison_data:
            return {}
        
        # Find fastest mode
        fastest_mode = min(comparison_data, key=lambda x: x.get("avg_search_time", float('inf')))
        
        # Find most accurate mode (highest precision@5)
        most_accurate_mode = max(comparison_data, key=lambda x: x.get("avg_precision@5", 0))
        
        # Find best balanced mode (good precision + reasonable speed)
        balanced_scores = []
        for row in comparison_data:
            precision = row.get("avg_precision@5", 0)
            speed = 1.0 / (row.get("avg_search_time", 1.0) + 0.1)  # Inverse of time
            balanced_score = precision * 0.7 + speed * 0.3  # Weight precision more
            balanced_scores.append((row["mode"], balanced_score))
        
        best_balanced_mode = max(balanced_scores, key=lambda x: x[1])
        
        return {
            "fastest_mode": {
                "mode": fastest_mode["mode"],
                "avg_time": fastest_mode["avg_search_time"]
            },
            "most_accurate_mode": {
                "mode": most_accurate_mode["mode"],
                "precision@5": most_accurate_mode["avg_precision@5"]
            },
            "best_balanced_mode": {
                "mode": best_balanced_mode[0],
                "balanced_score": best_balanced_mode[1]
            },
            "default_recommendation": best_balanced_mode[0]
        }
    
    def save_results(self, results: Dict[str, Any], output_path: str = "evaluation_results.json"):
        """Save evaluation results to file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print evaluation summary."""
        print("\nEVALUATION SUMMARY")
        print("=" * 60)
        
        # Print comparison table
        comparison_data = results["comparison_report"]["comparison_table"]
        if comparison_data:
            print("\nPerformance Comparison:")
            print(f"{'Mode':<15} {'P@5':<8} {'R@5':<8} {'NDCG@5':<8} {'MAP@5':<8} {'MRR':<8} {'Time(s)':<8}")
            print("-" * 70)
            
            for row in comparison_data:
                print(f"{row['mode']:<15} "
                      f"{row.get('avg_precision@5', 0):<8.3f} "
                      f"{row.get('avg_recall@5', 0):<8.3f} "
                      f"{row.get('avg_ndcg@5', 0):<8.3f} "
                      f"{row.get('avg_map@5', 0):<8.3f} "
                      f"{row.get('avg_mrr', 0):<8.3f} "
                      f"{row.get('avg_search_time', 0):<8.3f}")
        
        # Print recommendations
        recommendations = results["comparison_report"]["recommendations"]
        if recommendations:
            print(f"\nRECOMMENDATIONS:")
            print(f"   Fastest Mode: {recommendations['fastest_mode']['mode']} "
                  f"({recommendations['fastest_mode']['avg_time']:.3f}s avg)")
            print(f"   Most Accurate: {recommendations['most_accurate_mode']['mode']} "
                  f"(P@5: {recommendations['most_accurate_mode']['precision@5']:.3f})")
            print(f"   Best Balanced: {recommendations['best_balanced_mode']['mode']}")
            print(f"   Default Recommendation: {recommendations['default_recommendation']}")


def main():
    """Main function for running benchmarks."""
    parser = argparse.ArgumentParser(description="Patent NLP Search Benchmarking")
    parser.add_argument("--dataset", default="evaluation_dataset.json", 
                       help="Path to evaluation dataset")
    parser.add_argument("--modes", nargs="+", 
                       default=["tfidf", "semantic", "hybrid", "hybrid-advanced"],
                       help="Search modes to evaluate")
    parser.add_argument("--top-k", type=int, default=10, 
                       help="Number of results to retrieve")
    parser.add_argument("--max-queries", type=int, default=None,
                       help="Maximum number of queries to evaluate")
    parser.add_argument("--output", default="evaluation_results.json",
                       help="Output file for results")
    parser.add_argument("--quick", action="store_true",
                       help="Quick evaluation with first 10 queries only")
    
    args = parser.parse_args()
    
    # Quick mode override
    if args.quick:
        args.max_queries = 10
        print("Quick evaluation mode: testing first 10 queries only")
    
    # Initialize benchmark
    benchmark = SearchBenchmark(args.dataset)
    
    # Run evaluation
    results = benchmark.run_comprehensive_evaluation(
        modes=args.modes,
        top_k=args.top_k,
        max_queries=args.max_queries
    )
    
    # Save and display results
    benchmark.save_results(results, args.output)
    benchmark.print_summary(results)


if __name__ == "__main__":
    main()
