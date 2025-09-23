import subprocess
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser(description="Run end-to-end pipeline: parse, validate, preprocess, embed")
    parser.add_argument("--skip_parse", action="store_true", help="Skip parsing XML to JSONL")
    parser.add_argument("--skip_validate", action="store_true", help="Skip validation")
    parser.add_argument("--mode", choices=["chunks", "doc"], default="chunks", help="Preprocess output mode")
    parser.add_argument("--build_index", action="store_true", help="Build TF-IDF index at the end")
    args = parser.parse_args()

    if not args.skip_parse:
        subprocess.check_call(["python", "parse_patents.py"])  # writes processed jsonl

    if not args.skip_validate:
        subprocess.check_call(["python", "validate_json.py"])  # prints report

    subprocess.check_call(["python", "preprocess_patents.py", "--mode", args.mode])

    if args.build_index:
        subprocess.check_call(["python", "embed_tfidf.py", "build"])  # uses chunks.jsonl by default

    print("Pipeline complete.")


