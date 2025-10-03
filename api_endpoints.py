#!/usr/bin/env python3
"""
FastAPI endpoints for Patent NLP Project.
Enhanced API that uses the centralized search service.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, validator, ValidationError
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

# Import search service
from search_service import run_search, SearchRequest, format_results_for_api
from search_utils import generate_snippet, analyze_query_log

router = APIRouter()


class SearchRequestModel(BaseModel):
    query: str
    mode: str = "semantic"  # Options: "tfidf", "semantic", "hybrid", "hybrid-advanced"
    top_k: int = 5
    alpha: float = 0.5
    tfidf_weight: float = 0.3
    semantic_weight: float = 0.7
    rerank: bool = False
    include_snippets: bool = True
    include_metadata: bool = True
    log_enabled: bool = False
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('mode')
    def validate_mode(cls, v):
        valid_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        if v not in valid_modes:
            raise ValueError(f'Mode must be one of {valid_modes}')
        return v
    
    @validator('top_k')
    def validate_top_k(cls, v):
        if v <= 0:
            raise ValueError('top_k must be positive')
        if v > 100:
            raise ValueError('top_k cannot exceed 100')
        return v
    
    @validator('alpha')
    def validate_alpha(cls, v):
        if v < 0 or v > 1:
            raise ValueError('alpha must be between 0 and 1')
        return v


class SummarizeRequestModel(BaseModel):
    doc_id: str
    max_length: int = 200
    
    @validator('doc_id')
    def validate_doc_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Document ID cannot be empty')
        return v.strip()
    
    @validator('max_length')
    def validate_max_length(cls, v):
        if v <= 0:
            raise ValueError('max_length must be positive')
        if v > 2000:
            raise ValueError('max_length cannot exceed 2000')
        return v


class BatchSearchRequestModel(BaseModel):
    queries: List[str]
    mode: str = "semantic"
    top_k: int = 5
    alpha: float = 0.5
    tfidf_weight: float = 0.3
    semantic_weight: float = 0.7
    rerank: bool = False
    include_snippets: bool = True
    include_metadata: bool = True
    log_enabled: bool = False
    
    @validator('queries')
    def validate_queries(cls, v):
        if not v:
            raise ValueError('Queries list cannot be empty')
        for i, query in enumerate(v):
            if not query or not query.strip():
                raise ValueError(f'Query at index {i} cannot be empty')
        return [q.strip() for q in v]
    
    @validator('mode')
    def validate_mode(cls, v):
        valid_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        if v not in valid_modes:
            raise ValueError(f'Mode must be one of {valid_modes}')
        return v
    
    @validator('top_k')
    def validate_top_k(cls, v):
        if v <= 0:
            raise ValueError('top_k must be positive')
        if v > 100:
            raise ValueError('top_k cannot exceed 100')
        return v


class CompareModesRequestModel(BaseModel):
    query: str
    top_k: int = 5
    alpha: float = 0.5
    tfidf_weight: float = 0.3
    semantic_weight: float = 0.7
    rerank: bool = False
    include_snippets: bool = True
    include_metadata: bool = True


@router.post("/search")
async def search_endpoint(request: SearchRequestModel):
    """
    Enhanced search endpoint with full feature support.
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Create search request
        search_request = SearchRequest(
            query=request.query.strip(),
            mode=request.mode,
            top_k=request.top_k,
            alpha=request.alpha,
            tfidf_weight=request.tfidf_weight,
            semantic_weight=request.semantic_weight,
            rerank=request.rerank,
            include_snippets=request.include_snippets,
            include_metadata=request.include_metadata,
            log_enabled=request.log_enabled
        )
        
        # Run search
        results, metadata = run_search(search_request)
        
        # Format for API response
        response = format_results_for_api(results, metadata)
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationError as e:
        # Convert Pydantic validation errors to 400
        error_messages = []
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        raise HTTPException(status_code=400, detail="; ".join(error_messages))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/summarize")
async def summarize_endpoint(request: SummarizeRequestModel):
    """
    Enhanced summarization endpoint with snippet generation.
    """
    try:
        # Handle both chunk IDs and document IDs
        doc_id = request.doc_id
        
        # If it's a chunk ID, get the base document ID
        if '_chunk' in doc_id:
            base_doc_id = doc_id.split('_chunk')[0]
        else:
            base_doc_id = doc_id
        
        # Try to load patent data by base document ID
        patent = load_patent_by_id(base_doc_id)
        if patent is None:
            raise HTTPException(status_code=404, detail=f"Patent not found: {base_doc_id}")
        
        # Get text content
        text_content = ""
        
        # If it's a chunk ID, get chunk text
        if '_chunk' in doc_id:
            from search_utils import get_chunk_text
            text_content = get_chunk_text(doc_id) or ""
        
        # If no chunk text, try to get description from patent
        if not text_content:
            text_content = patent.get("description", "") or patent.get("abstract", "")
        
        if not text_content:
            return {
                "doc_id": request.doc_id,
                "summary": "No text content available for summarization",
                "title": patent.get("title", "No title"),
                "doc_type": patent.get("doc_type", "unknown")
            }
        
        # Generate smart snippet
        summary = generate_snippet(text_content, "", max_length=request.max_length)
        
        return {
            "doc_id": request.doc_id,
            "summary": summary,
            "title": patent.get("title", "No title"),
            "doc_type": patent.get("doc_type", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/batch_search")
async def batch_search_endpoint(request: BatchSearchRequestModel):
    """
    Batch search endpoint for multiple queries.
    """
    try:
        # Validate queries
        if not request.queries:
            raise HTTPException(status_code=400, detail="Queries list cannot be empty")
        
        for i, query in enumerate(request.queries):
            if not query or not query.strip():
                raise HTTPException(status_code=400, detail=f"Query at index {i} cannot be empty")
        
        results = []
        
        for query in request.queries:
            # Create search request for each query
            search_request = SearchRequest(
                query=query.strip(),
                mode=request.mode,
                top_k=request.top_k,
                alpha=request.alpha,
                tfidf_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight,
                rerank=request.rerank,
                include_snippets=request.include_snippets,
                include_metadata=request.include_metadata,
                log_enabled=request.log_enabled
            )
            
            # Run search
            query_results, metadata = run_search(search_request)
            
            # Format results
            formatted_results = format_results_for_api(query_results, metadata)
            results.append(formatted_results)
        
        return {
            "total_queries": len(request.queries),
            "mode": request.mode,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch search failed: {str(e)}")


@router.post("/compare_modes")
async def compare_modes_endpoint(request: CompareModesRequestModel):
    """
    Compare search results across all modes.
    """
    try:
        modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        results = {}
        
        for mode in modes:
            # Create search request for each mode
            search_request = SearchRequest(
                query=request.query,
                mode=mode,
                top_k=request.top_k,
                alpha=request.alpha,
                tfidf_weight=request.tfidf_weight,
                semantic_weight=request.semantic_weight,
                rerank=request.rerank,
                include_snippets=request.include_snippets,
                include_metadata=request.include_metadata,
                log_enabled=False  # Don't log comparison queries
            )
            
            # Run search
            query_results, metadata = run_search(search_request)
            
            # Format results
            formatted_results = format_results_for_api(query_results, metadata)
            results[mode] = formatted_results
        
        return {
            "query": request.query,
            "top_k": request.top_k,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mode comparison failed: {str(e)}")


@router.get("/logs/analyze")
async def analyze_logs_endpoint(log_file: str = "query_log.jsonl"):
    """
    Analyze query logs and return statistics.
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return {
                "error": f"Log file {log_file} not found",
                "total_queries": 0,
                "unique_queries": 0,
                "mode_usage": {},
                "average_score": 0.0,
                "most_common_queries": []
            }
        
        # Analyze logs
        analysis = analyze_query_log(str(log_path))
        
        return {
            "log_file": log_file,
            "total_queries": analysis.get("total_queries", 0),
            "unique_queries": analysis.get("unique_queries", 0),
            "mode_usage": analysis.get("mode_usage", {}),
            "average_score": analysis.get("average_score", 0.0),
            "most_common_queries": analysis.get("most_common_queries", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        # Test basic imports
        from embed_tfidf import load_texts
        from embed_semantic import load_semantic_index
        
        return {
            "status": "healthy",
            "message": "Patent NLP API is running",
            "version": "1.0.0"
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


def load_patent_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Load patent data by document ID from grants or applications.
    """
    # Define paths to processed patent data
    processed_dir = Path("data/processed")
    grants_jsonl = processed_dir / "grants.jsonl"
    applications_jsonl = processed_dir / "applications.jsonl"
    
    # Try grants first
    patent = _load_patent_from_file(doc_id, grants_jsonl)
    if patent is not None:
        return patent
    
    # Try applications
    patent = _load_patent_from_file(doc_id, applications_jsonl)
    return patent


def _load_patent_from_file(doc_id: str, file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load patent from a specific JSONL file.
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
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


# Global exception handler for validation errors
from fastapi import FastAPI
from fastapi.responses import JSONResponse

def setup_validation_error_handler(app: FastAPI):
    """Setup global exception handler to convert 422 to 400 for validation errors."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Convert Pydantic validation errors to 400 Bad Request
        error_messages = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        return JSONResponse(
            status_code=400,
            content={"detail": "; ".join(error_messages)}
        )
