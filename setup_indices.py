#!/usr/bin/env python3

# Setup script to build all search indices for the patent NLP project.


import sys
from pathlib import Path
from argparse import ArgumentParser

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from embed_tfidf import build_tfidf, save_index, load_texts
from embed_semantic import build_semantic_index
from preprocess_patents import process_file, OUTPUT_FILE


def check_data_files():
    # Check if required data files exist
    processed_dir = Path("./data/processed")
    grants_file = processed_dir / "grants.jsonl"
    apps_file = processed_dir / "applications.jsonl"
    
    if not grants_file.exists():
        print(f"Error: {grants_file} not found. Run parse_patents.py first.")
        return False
    
    if not apps_file.exists():
        print(f"Error: {apps_file} not found. Run parse_patents.py first.")
        return False
    
    return True


def build_tfidf_index():


    print("Building TF-IDF Index")

    
    try:
        # Check if chunks exist, if not create them
        if not OUTPUT_FILE.exists():
            print("Creating text chunks")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
                for fname in ["grants.jsonl", "applications.jsonl"]:
                    input_file = Path("./data/processed") / fname
                    if input_file.exists():
                        print(f"Processing {input_file}")
                        process_file(input_file, out, mode="chunks")
        
        # Build TF-IDF index
        ids, texts = load_texts(OUTPUT_FILE)
        print(f"Loaded {len(texts)} text chunks")
        
        vectorizer, matrix = build_tfidf(ids, texts)
        save_index(vectorizer, matrix, ids)
        
        print("TF-IDF index built successfully")
        return True
        
    except Exception as e:
        print(f"Error building TF-IDF index: {e}")
        return False


def build_semantic_index_wrapper():


    print("Building Semantic Index")

    
    try:
        build_semantic_index()
        print("Semantic index built successfully")
        return True
        
    except Exception as e:
        print(f"Error building semantic index: {e}")
        return False


def main():
    parser = ArgumentParser(description="Setup all search indices for patent NLP project")
    parser.add_argument("--tfidf-only", action="store_true", help="Build only TF-IDF index")
    parser.add_argument("--semantic-only", action="store_true", help="Build only semantic index")
    parser.add_argument("--skip-checks", action="store_true", help="Skip data file checks")
    args = parser.parse_args()
    
    print("Patent NLP Project - Index Setup")

    
    # Check data files
    if not args.skip_checks and not check_data_files():
        sys.exit(1)
    
    success_count = 0
    total_tasks = 0
    
    # Build TF-IDF index
    if not args.semantic_only:
        total_tasks += 1
        if build_tfidf_index():
            success_count += 1
    
    # Build semantic index
    if not args.tfidf_only:
        total_tasks += 1
        if build_semantic_index_wrapper():
            success_count += 1
    
    # Summary

    print("Setup Summary")

    print(f"Successfully built {success_count}/{total_tasks} indices")
    
    if success_count == total_tasks:
        print("All indices built successfully")
        print("\nSearch CLI USage:")
        print("  python search_cli.py 'query' --mode tfidf")
        print("  python search_cli.py 'query' --mode semantic")
        print("  python search_cli.py 'query' --mode hybrid")
    else:
        print("Some indices failed to build. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

