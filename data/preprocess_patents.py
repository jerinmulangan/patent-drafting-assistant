import json
import os
import re
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# nltk resources available + separate punkt and punkt_tab
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)


INPUT_DIR = Path("./data/processed")
OUTPUT_FILE = INPUT_DIR / "chunks.jsonl"

STOPWORDS = set(stopwords.words("english"))

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
    return [t for t in tokens if t.isalnum() and t not in STOPWORDS]

def chunk_tokens(tokens, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # yield overlapping chunks
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        yield tokens[start:end]
        if end == len(tokens):
            break
        start = end - overlap 

def process_file(input_file, out_file):
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
            for i, chunk in enumerate(chunk_tokens(tokens)):
                out_file.write(json.dumps({
                    "doc_id": patent.get("doc_id"),
                    "chunk_id": f"{patent.get('doc_id')}_chunk{i}",
                    "text": " ".join(chunk)
                }) + "\n")

if __name__ == "__main__":
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for fname in ["grants.jsonl", "applications.jsonl"]:
            input_file = INPUT_DIR / fname
            if input_file.exists():
                print(f"Processing {input_file}")
                process_file(input_file, out)
    print(f"Preprocessing complete -> chunks saved to {OUTPUT_FILE}")
