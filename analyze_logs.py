#!/usr/bin/env python3
# Analyze query logs and generate insights.

import json
import csv
from pathlib import Path
from argparse import ArgumentParser
from collections import defaultdict, Counter
from search_utils import analyze_query_log


def load_log_entries(log_file: str):
    # Load all log entries from a JSONL file
    entries = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def analyze_query_patterns(entries):
    # Analyze query patterns and user behavior
    patterns = {
        "total_queries": len(entries),
        "unique_queries": len(set(entry["query"] for entry in entries)),
        "mode_usage": Counter(entry["mode"] for entry in entries),
        "query_length_distribution": {},
        "score_distribution": {},
        "time_distribution": {},
        "most_common_queries": Counter(entry["query"] for entry in entries).most_common(20),
        "queries_by_mode": defaultdict(list)
    }
    
    # Analyze query lengths
    query_lengths = [len(entry["query"].split()) for entry in entries]
    patterns["query_length_distribution"] = {
        "min": min(query_lengths) if query_lengths else 0,
        "max": max(query_lengths) if query_lengths else 0,
        "avg": sum(query_lengths) / len(query_lengths) if query_lengths else 0
    }
    
    # Analyze scores
    all_scores = []
    for entry in entries:
        all_scores.extend(entry["top_scores"])
    
    if all_scores:
        patterns["score_distribution"] = {
            "min": min(all_scores),
            "max": max(all_scores),
            "avg": sum(all_scores) / len(all_scores),
            "count": len(all_scores)
        }
    
    # Group queries by mode
    for entry in entries:
        patterns["queries_by_mode"][entry["mode"]].append(entry["query"])
    
    return patterns


def generate_performance_report(entries):
    # Generate performance analysis report
    if not entries:
        return {"error": "No entries to analyze"}
    
    # Calculate performance metrics
    total_time = sum(entry.get("search_time", 0) for entry in entries)
    avg_time = total_time / len(entries) if entries else 0
    
    # Performance by mode
    mode_performance = defaultdict(list)
    for entry in entries:
        mode_performance[entry["mode"]].append(entry.get("search_time", 0))
    
    performance_by_mode = {}
    for mode, times in mode_performance.items():
        if times:
            performance_by_mode[mode] = {
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "query_count": len(times)
            }
    
    return {
        "total_queries": len(entries),
        "total_time": total_time,
        "average_time": avg_time,
        "performance_by_mode": performance_by_mode
    }


def export_insights_to_csv(patterns, performance, output_file):
    # Export insights to CSV format
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write summary
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Queries", patterns["total_queries"]])
        writer.writerow(["Unique Queries", patterns["unique_queries"]])
        writer.writerow(["Average Query Length", f"{patterns['query_length_distribution']['avg']:.1f} words"])
        writer.writerow(["Average Score", f"{patterns['score_distribution']['avg']:.4f}"])
        writer.writerow(["Average Search Time", f"{performance['average_time']:.3f} seconds"])
        
        # Empty row
        writer.writerow([])  
        
        # Write mode usage
        writer.writerow(["Mode", "Usage Count", "Percentage"])
        total_queries = patterns["total_queries"]
        for mode, count in patterns["mode_usage"].items():
            percentage = (count / total_queries) * 100 if total_queries > 0 else 0
            writer.writerow([mode, count, f"{percentage:.1f}%"])
        
        # Empty row
        writer.writerow([])  
        
        # Write most common queries
        writer.writerow(["Rank", "Query", "Frequency"])
        for rank, (query, count) in enumerate(patterns["most_common_queries"], 1):
            writer.writerow([rank, query, count])
        
        # Empty row
        writer.writerow([])  
        
        # Write performance by mode
        writer.writerow(["Mode", "Avg Time (s)", "Min Time (s)", "Max Time (s)", "Query Count"])
        for mode, perf in performance["performance_by_mode"].items():
            writer.writerow([
                mode,
                f"{perf['avg_time']:.3f}",
                f"{perf['min_time']:.3f}",
                f"{perf['max_time']:.3f}",
                perf["query_count"]
            ])


def main():
    parser = ArgumentParser(description="Analyze patent search query logs")
    parser.add_argument("log_file", type=str, help="Query log file (JSONL format)")
    parser.add_argument("--output", type=str, default="log_analysis", help="Output file prefix")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    if not Path(args.log_file).exists():
        print(f"Error: Log file '{args.log_file}' not found")
        return
    
    print(f"Analyzing query log: {args.log_file}")
    
    # Load log entries
    entries = load_log_entries(args.log_file)
    print(f"Loaded {len(entries)} log entries")
    
    if not entries:
        print("No entries found in log file")
        return
    
    # Analyze patterns
    print("Analyzing query patterns")
    patterns = analyze_query_patterns(entries)
    
    # Generate performance report
    print("Generating performance report")
    performance = generate_performance_report(entries)
    
    # Save results
    timestamp = Path(args.log_file).stem.replace("query_log", "")
    
    if args.format in ["json", "both"]:
        json_file = f"{args.output}_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "patterns": patterns,
                "performance": performance
            }, f, indent=2, ensure_ascii=False)
        print(f"Analysis saved to {json_file}")
    
    if args.format in ["csv", "both"]:
        csv_file = f"{args.output}_{timestamp}.csv"
        export_insights_to_csv(patterns, performance, csv_file)
        print(f"Insights saved to {csv_file}")
    
    # Print summary
    print("QUERY LOG ANALYSIS SUMMARY")
    print(f"Total queries: {patterns['total_queries']}")
    print(f"Unique queries: {patterns['unique_queries']}")
    print(f"Average query length: {patterns['query_length_distribution']['avg']:.1f} words")
    print(f"Average search time: {performance['average_time']:.3f} seconds")
    
    print(f"\nMode Usage:")
    for mode, count in patterns["mode_usage"].items():
        percentage = (count / patterns["total_queries"]) * 100
        print(f"  {mode}: {count} ({percentage:.1f}%)")
    
    print(f"\nTop 5 Most Common Queries:")
    for rank, (query, count) in enumerate(patterns["most_common_queries"][:5], 1):
        print(f"  {rank}. '{query}' ({count} times)")
    
    print(f"\nPerformance by Mode:")
    for mode, perf in performance["performance_by_mode"].items():
        print(f"  {mode}: {perf['avg_time']:.3f}s avg, {perf['query_count']} queries")


if __name__ == "__main__":
    main()
