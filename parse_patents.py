import os
import json
import re
import xml.etree.ElementTree as ET

DATA_DIR = "./data"
GRANTS_DIR = os.path.join(DATA_DIR, "grants")
APPLICATIONS_DIR = os.path.join(DATA_DIR, "applications")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def strip_namespace(tag):
    return tag.split("}")[-1] if "}" in tag else tag

def split_records(file_path, record_tag):
    # Yield one <record_tag> and </record_tag> string at a time.
    start_pat = f"<{record_tag}"
    end_pat = f"</{record_tag}>"
    buffer = []
    inside_record = False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if start_pat in line:
                inside_record = True
                buffer = [line]
            elif inside_record:
                buffer.append(line)

            if inside_record and end_pat in line:
                inside_record = False
                yield "".join(buffer)

def parse_record(xml_string, record_tag):
    try:
        root = ET.fromstring(xml_string)
        if strip_namespace(root.tag) != record_tag:
            return None
        return extract_metadata(root)
    except ET.ParseError as e:
        print(f"skipping record due to parse error: {e}")
        return None

def extract_metadata(patent_elem):
    # extracts full metadata from a single patent record.
    data = {}

    # document ID (combined country + doc-number + kind)
    pub_ref = patent_elem.find(".//publication-reference/document-id")
    if pub_ref is not None:
        country = (pub_ref.findtext("country") or "").strip()
        doc_num = (pub_ref.findtext("doc-number") or "").strip()
        kind = (pub_ref.findtext("kind") or "").strip()
        data["doc_id"] = f"{country}{doc_num}{kind}".strip()
    else:
        data["doc_id"] = ""

    # title
    title_elem = patent_elem.find(".//invention-title")
    data["title"] = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

    # abstract
    abstract_elem = patent_elem.find(".//abstract")
    data["abstract"] = " ".join(t.strip() for t in abstract_elem.itertext()) if abstract_elem is not None else ""

    # claims
    claims_elem = patent_elem.find(".//claims")
    data["claims"] = " ".join(t.strip() for t in claims_elem.itertext()) if claims_elem is not None else ""

    # description
    desc_elem = patent_elem.find(".//description")
    data["description"] = " ".join(t.strip() for t in desc_elem.itertext()) if desc_elem is not None else ""

    return data


def process_directory(directory, record_tag, output_file):
    total_count = 0
    with open(output_file, "w", encoding="utf-8") as out:
        for file in os.listdir(directory):
            if not file.endswith(".xml"):
                continue
            file_path = os.path.join(directory, file)
            print(f"Parsing {file_path}")
            count = 0
            for xml_string in split_records(file_path, record_tag):
                record = parse_record(xml_string, record_tag)
                if record:
                    record["source_file"] = file_path 
                    out.write(json.dumps(record) + "\n")
                    count += 1

            total_count += count
            print(f"Found {count} patents")
    print(f"Saved {total_count} patents to {output_file}")

if __name__ == "__main__":
    process_directory(GRANTS_DIR, "us-patent-grant", os.path.join(PROCESSED_DIR, "grants.jsonl"))
    process_directory(APPLICATIONS_DIR, "us-patent-application", os.path.join(PROCESSED_DIR, "applications.jsonl"))
    print("Parsing completed.")
