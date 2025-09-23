import json
import os
import re
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from argparse import ArgumentParser

# nltk resources available + separate punkt and punkt_tab
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)


INPUT_DIR = Path("./data/processed")
OUTPUT_FILE = INPUT_DIR / "chunks.jsonl"

STOPWORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

CHUNK_SIZE = 500 
CHUNK_OVERLAP = 50 

def clean_text(text):
    # strip and collapse whitespace
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)  
    text = re.sub(r"\s+", " ", text)     
    return text.lower().strip()

def tokenize_and_filter(text):
    tokens = word_tokenize(text)
    filtered = []
    for token in tokens:
        if not token.isalnum():
            continue
        if any(ch.isdigit() for ch in token):
            continue
        if len(token) < 3:
            continue
        if token in STOPWORDS:
            continue
        lemma = LEMMATIZER.lemmatize(token)
        filtered.append(lemma)
    return filtered

def chunk_tokens(tokens, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # yield overlapping chunks
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        yield tokens[start:end]
        if end == len(tokens):
            break
        start = end - overlap 

def process_file(input_file, out_file, mode="chunks", chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            patent = json.loads(line)
            combined_text = " ".join([
                clean_text(patent.get("title", "")),
                clean_text(patent.get("abstract", "")),
                clean_text(patent.get("claims", "")),
                clean_text(patent.get("description", "")),
            ])
            tokens = tokenize_and_filter(combined_text)
            if mode == "doc":
                out_file.write(json.dumps({
                    "doc_id": patent.get("doc_id"),
                    "text": " ".join(tokens)
                }) + "\n")
            else:
                for i, chunk in enumerate(chunk_tokens(tokens, chunk_size=chunk_size, overlap=overlap)):
                    out_file.write(json.dumps({
                        "doc_id": patent.get("doc_id"),
                        "chunk_id": f"{patent.get('doc_id')}_chunk{i}",
                        "text": " ".join(chunk)
                    }) + "\n")

if __name__ == "__main__":
    parser = ArgumentParser(description="Preprocess patents: tokenize, clean, and chunk text")
    parser.add_argument("--mode", choices=["chunks", "doc"], default="chunks", help="Output mode: chunks or full document")
    parser.add_argument("--chunk_size", type=int, default=CHUNK_SIZE, help="Tokens per chunk")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP, help="Token overlap between chunks")
    args = parser.parse_args()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for fname in ["grants.jsonl", "applications.jsonl"]:
            input_file = INPUT_DIR / fname
            if input_file.exists():
                print(f"Processing {input_file}")
                process_file(input_file, out, mode=args.mode, chunk_size=args.chunk_size, overlap=args.overlap)
    print(f"Preprocessing complete -> saved to {OUTPUT_FILE}")
