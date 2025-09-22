import json
from pathlib import Path

GRANTS_FILE = Path("./data/processed/grants.jsonl")
APPS_FILE = Path("./data/processed/applications.jsonl")

def validate_jsonl(file_path):
    required_fields = ["doc_id", "title", "abstract", "claims", "description", "source_file"]
    total = 0
    missing_fields_count = {field: 0 for field in required_fields}
    empty_fields_count = {field: 0 for field in required_fields}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
            try:
                patent = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON error in {file_path}: {e}")
                continue

            for field in required_fields:
                if field not in patent:
                    missing_fields_count[field] += 1
                elif not patent[field] or str(patent[field]).strip() == "":
                    empty_fields_count[field] += 1

    print(f"\nValidation report for {file_path.name}:")
    print(f"Total patents: {total}")
    print("Missing fields counts:")
    for k, v in missing_fields_count.items():
        print(f"  {k}: {v}")
    print("Empty fields counts:")
    for k, v in empty_fields_count.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    validate_jsonl(GRANTS_FILE)
    validate_jsonl(APPS_FILE)
