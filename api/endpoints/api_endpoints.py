from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

# Import search functions from existing modules
from embed_tfidf import search as search_tfidf
from embed_semantic import search_semantic
from embed_hybrid import search_hybrid

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    mode: str = "semantic"  # Options: "tfidf", "semantic", or "hybrid"
    top_k: int = 5


@router.post("/search")
async def search_endpoint(request: SearchRequest):
    try:
        if request.mode == "tfidf":
            results = search_tfidf(request.query, top_k=request.top_k)
        elif request.mode == "semantic":
            results = search_semantic(request.query, top_k=request.top_k)
        elif request.mode == "hybrid":
            results = search_hybrid(request.query, top_k=request.top_k)
        else:
            raise HTTPException(status_code=400, detail="Invalid search mode")
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SummarizeRequest(BaseModel):
    doc_id: str


def load_patent_by_id(doc_id: str, jsonl_path: str):
    if not os.path.exists(jsonl_path):
        return None
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("doc_id") == doc_id:
                        return record
                except Exception:
                    continue
    except Exception:
        return None
    return None


# Define paths to processed patent data
PROCESSED_DIR = os.path.join("data", "processed")
GRANTS_JSONL = os.path.join(PROCESSED_DIR, "grants.jsonl")
APPLICATIONS_JSONL = os.path.join(PROCESSED_DIR, "applications.jsonl")


def generate_summary(text: str) -> str:
    # Simple summarization: return the first 150 chars of the description
    if not text:
        return "No content available"
    summary = text[:150]
    if len(text) > 150:
        summary += "..."
    return "Summary: " + summary


@router.post("/summarize")
async def summarize_endpoint(request: SummarizeRequest):
    # Attempt to load patent data from grants first, then applications
    patent = load_patent_by_id(request.doc_id, GRANTS_JSONL)
    if patent is None:
        patent = load_patent_by_id(request.doc_id, APPLICATIONS_JSONL)
    if patent is None:
        raise HTTPException(status_code=404, detail="Patent not found")
    description = patent.get("description", "")
    summary = generate_summary(description)
    return {"doc_id": request.doc_id, "summary": summary}
