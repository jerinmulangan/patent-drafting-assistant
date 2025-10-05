#!/usr/bin/env python3
"""
Test script to verify memory-efficient text processing works with large patent descriptions.
"""

import json
import sys
from pathlib import Path

# Import the fixed functions
from preprocess_patents import clean_text
from search_utils import generate_snippet, compute_keyword_overlap_score

def test_large_text_processing():
    """Test processing of the largest patent description."""
    print("Testing memory-efficient text processing...")
    
    # Load the largest patent description
    grants_file = Path("./data/processed/grants.jsonl")
    if not grants_file.exists():
        print("Error: grants.jsonl not found. Run parse_patents.py first.")
        return False
    
    max_desc_len = 0
    largest_patent = None
    
    print("Finding largest patent description...")
    with open(grants_file, "r", encoding="utf-8") as f:
        for line in f:
            patent = json.loads(line)
            desc_len = len(patent.get("description", ""))
            if desc_len > max_desc_len:
                max_desc_len = desc_len
                largest_patent = patent
    
    if not largest_patent:
        print("No patents found.")
        return False
    
    print(f"Largest description: {max_desc_len:,} characters")
    print(f"Patent ID: {largest_patent.get('doc_id', 'Unknown')}")
    
    # Test clean_text function
    print("\nTesting clean_text function...")
    try:
        description = largest_patent.get("description", "")
        cleaned = clean_text(description)
        print(f"clean_text() processed {len(description):,} chars -> {len(cleaned):,} chars")
    except Exception as e:
        print(f"clean_text() failed: {e}")
        return False
    
    # Test generate_snippet function
    print("\nTesting generate_snippet function...")
    try:
        snippet = generate_snippet(description, "machine learning algorithm", max_length=200)
        print(f"generate_snippet() created snippet: {len(snippet)} chars")
        print(f"  Preview: {snippet[:100]}...")
    except Exception as e:
        print(f"generate_snippet() failed: {e}")
        return False
    
    # Test compute_keyword_overlap_score function
    print("\nTesting compute_keyword_overlap_score function...")
    try:
        score = compute_keyword_overlap_score(description, "machine learning algorithm")
        print(f"compute_keyword_overlap_score() returned: {score:.4f}")
    except Exception as e:
        print(f"compute_keyword_overlap_score() failed: {e}")
        return False
    
    print("\nAll memory-efficient functions work correctly!")
    return True

def main():
    print("Memory Fix Test for Patent NLP Project")
    print("=" * 50)
    
    if test_large_text_processing():
        print("\nMemory fixes are working! Your colleague can now run:")
        print("   python run_pipeline.py --build_index")
        sys.exit(0)
    else:
        print("\nMemory fixes need more work.")
        sys.exit(1)

if __name__ == "__main__":
    main()

