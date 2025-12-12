#!/usr/bin/env python3
"""
FastAPI endpoints for Patent NLP Project.
Enhanced API that uses the centralized search service.
"""
from typing import Literal
from pydantic import Field
import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator, ValidationError
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
import asyncio

# Import search service
from search_service import run_search, SearchRequest, format_results_for_api
from search_utils import generate_snippet, analyze_query_log
from ollama_service import get_ollama_service
from async_orchestration import get_orchestration_service, DraftWithSimilarity
from patent_drafting_system import get_advanced_drafting_system, AdvancedPatentDraftingSystem
from evaluation_harness import EvaluationHarness
# from similarity_visualizer import get_similarity_visualizer

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


class DraftRequestModel(BaseModel):
    description: str
    model: str = "llama3.2:3b"
    template_type: str = "utility"
    max_length: int = 2000
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        if len(v.strip()) < 50:
            raise ValueError('Description too short (minimum 50 characters)')
        if len(v) > 5000:
            raise ValueError('Description too long (maximum 5000 characters)')
        return v.strip()
    
    @validator('model')
    def validate_model(cls, v):
        valid_models = ["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"]
        if v not in valid_models:
            raise ValueError(f'Model must be one of {valid_models}')
        return v
    
    @validator('template_type')
    def validate_template_type(cls, v):
        valid_types = ["utility", "software", "medical", "design"]
        if v not in valid_types:
            raise ValueError(f'Template type must be one of {valid_types}')
        return v
    
    @validator('max_length')
    def validate_max_length(cls, v):
        if v <= 0:
            raise ValueError('max_length must be positive')
        if v > 10000:
            raise ValueError('max_length cannot exceed 10000')
        return v
# -------------------------------
# V2 USPTO Draft Models
# -------------------------------
Jurisdiction = Literal["USPTO", "EPO", "WIPO-PCT"]
ClaimBundle = Literal["system", "method", "crm", "system+method", "method+crm", "all"]
SpecDepth = Literal["concise", "standard", "deep"]
EmbodimentStyle = Literal["narrow", "balanced", "broad"]

class DraftV2RequestModel(BaseModel):
    description: str = Field(..., min_length=50, max_length=8000)
    model: Literal["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"] = "llama3.2:3b"
    template_type: Literal["utility", "software", "medical", "design"] = "utility"
    jurisdiction: Jurisdiction = "USPTO"
    claim_bundle: ClaimBundle = "all"
    independent_claims_per_type: int = 1
    dependent_claims_per_independent: int = 3
    spec_depth: SpecDepth = "deep"
    embodiment_style: EmbodimentStyle = "balanced"
    include_definitions: bool = True
    include_alternatives: bool = True
    include_figure_callouts: bool = True
    include_glossary: bool = True
    include_enablement_language: bool = True
    include_best_mode: bool = True
    include_markush_examples: bool = False
    add_boilerplate_variations: bool = True
    use_background_search: bool = True
    search_mode: Literal["tfidf", "semantic", "hybrid", "hybrid-advanced"] = "hybrid"
    search_top_k: int = 8
    include_snippets: bool = True
    include_metadata: bool = True
    use_cache: bool = True
    temperature: float = 0.4


class DraftV2ResponseModel(BaseModel):
    success: bool
    message: str
    model: str
    template_type: str
    jurisdiction: Jurisdiction
    generation_time: float
    cached: bool
    abstract: str
    full_text_markdown: str
    full_text_html: str


class AdvancedDraftRequestModel(BaseModel):
    """Request model for advanced 17-step drafting system."""
    description: str = Field(..., min_length=50, max_length=8000)
    precision_model: str = "llama3.2:3b"
    fluency_model: str = "mistral:7b"
    use_ensemble: bool = True
    use_scaffolding: bool = True
    use_two_pass: bool = True
    use_critique: bool = True
    run_evaluation: bool = False


class AdvancedDraftResponseModel(BaseModel):
    """Response model for advanced drafting system."""
    success: bool
    message: str
    sections: Dict[str, str]
    glossary: Dict[str, Any]
    outline: Optional[str] = None
    critique_results: Optional[Dict[str, Any]] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    generation_time: float
    model_used: Dict[str, str]


class SectionSimilarityModel(BaseModel):
    section_name: str
    section_text: str
    similar_patents: List[Dict[str, Any]]
    analysis_time: float
    patent_count: int


class AdvancedDraftWithSimilarityRequestModel(BaseModel):
    """Request model for advanced drafting system with similarity search."""
    description: str = Field(..., min_length=50, max_length=8000)
    precision_model: str = "llama3.2:3b"
    fluency_model: str = "mistral:7b"
    use_ensemble: bool = True
    use_scaffolding: bool = True
    use_two_pass: bool = True
    use_critique: bool = True
    run_evaluation: bool = False
    search_mode: str = "hybrid-advanced"
    top_k: int = 5
    include_snippets: bool = True


class AdvancedDraftWithSimilarityResponseModel(BaseModel):
    """Response model for advanced drafting system with similarity analysis."""
    success: bool
    message: str
    sections: Dict[str, str]
    glossary: Dict[str, Any]
    outline: Optional[str] = None
    critique_results: Optional[Dict[str, Any]] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    generation_time: float
    model_used: Dict[str, str]
    section_similarities: Dict[str, SectionSimilarityModel]
    total_analysis_time: float



class DraftResponseModel(BaseModel):
    draft: str
    model: str
    template_type: str
    generation_time: float
    cached: bool = False
    success: bool = True
    message: str = "Draft generated successfully"


class SaveDraftRequestModel(BaseModel):
    title: Optional[str] = None
    content: str
    model: Optional[str] = None
    template_type: Optional[str] = None


class SavedDraftModel(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    model: Optional[str] = None
    template_type: Optional[str] = None
    generation_time: Optional[float] = None
    created_at: str


@router.post("/drafts", response_model=SavedDraftModel)
async def save_draft_endpoint(request: SaveDraftRequestModel):
    """Save a generated draft to server-side storage (JSONL file)."""
    try:
        import uuid
        from datetime import datetime
        drafts_dir = Path("data/processed")
        drafts_dir.mkdir(parents=True, exist_ok=True)
        file_path = drafts_dir / "saved_drafts.jsonl"

        draft_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"

        draft_entry = {
            "id": draft_id,
            "title": request.title or (request.content.splitlines()[0] if request.content else "Untitled Draft"),
            "content": request.content,
            "model": request.model,
            "template_type": request.template_type,
            "generation_time": None,
            "created_at": created_at
        }

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(draft_entry) + "\n")

        return draft_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save draft: {str(e)}")


@router.get("/drafts")
async def list_drafts_endpoint():
    """Return the list of saved drafts."""
    try:
        file_path = Path("data/processed/saved_drafts.jsonl")
        if not file_path.exists():
            return []

        drafts = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    drafts.append(json.loads(line))
                except Exception:
                    continue
        # return most recent first
        drafts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return drafts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list drafts: {str(e)}")


@router.get("/drafts/{draft_id}")
async def get_draft_endpoint(draft_id: str):
    try:
        file_path = Path("data/processed/saved_drafts.jsonl")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Draft not found")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("id") == draft_id:
                        return entry
                except Exception:
                    continue

        raise HTTPException(status_code=404, detail="Draft not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get draft: {str(e)}")


@router.delete("/drafts/{draft_id}")
async def delete_draft_endpoint(draft_id: str):
    """Delete a saved draft by id (rewrites file excluding the deleted draft)."""
    try:
        file_path = Path("data/processed/saved_drafts.jsonl")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Draft not found")

        kept = []
        found = False
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("id") == draft_id:
                        found = True
                        continue
                    kept.append(entry)
                except Exception:
                    continue

        if not found:
            raise HTTPException(status_code=404, detail="Draft not found")

        # Rewrite file
        with open(file_path, "w", encoding="utf-8") as f:
            for entry in kept:
                f.write(json.dumps(entry) + "\n")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete draft: {str(e)}")

class DraftWithSearchRequestModel(DraftRequestModel):
    search_mode: str = "semantic"
    search_top_k: int = 5
    include_snippets: bool = True
    include_metadata: bool = True

class DraftWithSearchResponseModel(DraftResponseModel):
    similar_patents: List[Dict[str, Any]] = []
    search_mode: str = "semantic"
    search_top_k: int = 5


class SimilarityMatchModel(BaseModel):
    draft_text: str
    prior_text: str
    similarity_score: float
    prior_patent_id: str
    prior_title: str
    section_type: str


class HighlightedSectionModel(BaseModel):
    section_name: str
    text: str
    html_output: str
    markdown_output: str
    similarity_matches: List[SimilarityMatchModel]


class DraftWithSimilarityVisualizationModel(BaseModel):
    draft: str
    model: str
    template_type: str
    generation_time: float
    cached: bool
    similar_patents: List[Dict[str, Any]]
    highlighted_sections: Dict[str, HighlightedSectionModel]
    similarity_statistics: Dict[str, Any]
    search_mode: str
    search_top_k: int


class DraftWithSimilarityRequestModel(BaseModel):
    description: str
    search_mode: str = "hybrid"
    model: str = "llama3.2:3b"
    template_type: str = "utility"
    top_k: int = 5
    include_snippets: bool = True
    use_cache: bool = True
    
    @validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        if len(v.strip()) < 50:
            raise ValueError('Description too short (minimum 50 characters)')
        if len(v) > 5000:
            raise ValueError('Description too long (maximum 5000 characters)')
        return v.strip()
    
    @validator('search_mode')
    def validate_search_mode(cls, v):
        valid_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        if v not in valid_modes:
            raise ValueError(f'Search mode must be one of {valid_modes}')
        return v
    
    @validator('model')
    def validate_model(cls, v):
        valid_models = ["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"]
        if v not in valid_models:
            raise ValueError(f'Model must be one of {valid_models}')
        return v
    
    @validator('template_type')
    def validate_template_type(cls, v):
        valid_types = ["utility", "software", "medical", "design"]
        if v not in valid_types:
            raise ValueError(f'Template type must be one of {valid_types}')
        return v
    
    @validator('top_k')
    def validate_top_k(cls, v):
        if v <= 0:
            raise ValueError('top_k must be positive')
        if v > 20:
            raise ValueError('top_k cannot exceed 20 for similarity analysis')
        return v


class DraftWithSimilarityResponseModel(BaseModel):
    draft: str
    model: str
    template_type: str
    generation_time: float
    cached: bool
    section_similarities: Dict[str, SectionSimilarityModel]
    total_analysis_time: float
    success: bool
    message: str


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

@router.post("/generate_with_search", response_model=DraftWithSearchResponseModel)
async def generate_with_search_endpoint(request: DraftWithSearchRequestModel):
    """Generate a patent draft and find similar patents based on claims."""
    # Generate the draft
    draft_result = await generate_draft_endpoint(request)
    
    # Extract claims (you'll need to implement this function)
    claims = extract_claims_from_draft(draft_result.draft)
    
    if not claims:
        return {
            **draft_result.dict(),
            "similar_patents": [],
            "search_mode": request.search_mode,
            "search_top_k": request.search_top_k,
            "message": "No claims found in the generated draft"
        }
    
    # Search for similar patents
    search_results = []
    for claim in claims:
        search_request = SearchRequest(
            query=claim,
            mode=request.search_mode,
            top_k=request.search_top_k,
            include_snippets=request.include_snippets,
            include_metadata=request.include_metadata
        )
        results, _ = run_search(search_request)
        search_results.extend([r.to_dict() for r in results])
    
    # Deduplicate results by doc_id
    seen = set()
    unique_results = []
    for result in search_results:
        if result['doc_id'] not in seen:
            seen.add(result['doc_id'])
            unique_results.append(result)
    
    return {
        **draft_result.dict(),
        "similar_patents": unique_results[:request.search_top_k],
        "search_mode": request.search_mode,
        "search_top_k": request.search_top_k
    }

def extract_claims_from_draft(draft: str) -> List[str]:
    """Extract claims from the generated draft text."""
    # This is a simple implementation - you may need to adjust based on your draft format
    import re
    claims = re.findall(r'Claim \d+\.\s*(.*?)(?=\n\nClaim \d+\.|\Z)', draft, re.DOTALL)
    return [claim.strip() for claim in claims if claim.strip()]


@router.post("/generate_draft", response_model=DraftResponseModel)
async def generate_draft_endpoint(request: DraftRequestModel):
    """
    Generate patent application draft using local Ollama model.
    """
    try:
        # Get Ollama service
        ollama_service = get_ollama_service()
        
        # Check if Ollama is available
        if not ollama_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not available. Please install and start Ollama."
            )
        
        # Generate draft
        result = ollama_service.generate_patent_draft(
            description=request.description,
            model_name=request.model,
            template_type=request.template_type
        )
        
        return DraftResponseModel(
            draft=result["draft"],
            model=result["model"],
            template_type=result["template_type"],
            generation_time=result["generation_time"],
            cached=result.get("cached", False),
            success=True,
            message="Draft generated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


@router.post("/generate_draft_v2", response_model=DraftV2ResponseModel)
async def generate_draft_v2_endpoint(request: DraftV2RequestModel):
    """
    Generate a long-form USPTO-grade patent draft with sections, triple-claim sets,
    enablement language, figure callouts, and compliance structure.
    """
    try:
        ollama_service = get_ollama_service()
        if not ollama_service.is_available():
            raise HTTPException(status_code=503, detail="Ollama service is not available. Please install and start Ollama.")

        # Optional novelty search context
        novelty_refs = []
        if request.use_background_search:
            search_request = SearchRequest(
                query=request.description,
                mode=request.search_mode,
                top_k=request.search_top_k,
                include_snippets=request.include_snippets,
                include_metadata=request.include_metadata
            )
            results, _ = run_search(search_request)
            novelty_refs = [r.to_dict() for r in results]

        # Generate full structured USPTO draft
        result = ollama_service.generate_uspto_structured_draft(
            description=request.description,
            model_name=request.model,
            template_type=request.template_type,
            jurisdiction=request.jurisdiction,
            claim_bundle=request.claim_bundle,
            independent_claims_per_type=request.independent_claims_per_type,
            dependent_claims_per_independent=request.dependent_claims_per_independent,
            spec_depth=request.spec_depth,
            embodiment_style=request.embodiment_style,
            include_definitions=request.include_definitions,
            include_alternatives=request.include_alternatives,
            include_figure_callouts=request.include_figure_callouts,
            include_glossary=request.include_glossary,
            include_enablement_language=request.include_enablement_language,
            include_best_mode=request.include_best_mode,
            include_markush_examples=request.include_markush_examples,
            add_boilerplate_variations=request.add_boilerplate_variations,
            novelty_refs=novelty_refs,
            temperature=request.temperature,
            use_cache=request.use_cache
        )

        # Use the structured output from the upgraded function
        return DraftV2ResponseModel(
            success=True,
            message="USPTO-grade draft generated successfully",
            model=result.get("model", request.model),
            template_type=request.template_type,
            jurisdiction=request.jurisdiction,
            generation_time=result.get("generation_time", 0.0),
            cached=result.get("cached", False),
            abstract=result.get("abstract", ""),
            full_text_markdown=result.get("full_text_markdown", ""),
            full_text_html=result.get("full_text_html", "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft v2 generation failed: {str(e)}")


@router.post("/generate_draft_advanced", response_model=AdvancedDraftResponseModel)
async def generate_draft_advanced_endpoint(request: AdvancedDraftRequestModel):
    """
    Generate patent draft using the advanced 17-step system with:
    - Precision/fluency model ensemble
    - Decoding profiles (strict/balanced/creative)
    - Section-by-section templates
    - Spec scaffolding
    - Controlled terminology/glossary
    - Safe language guards
    - Two-pass drafting
    - Claims workbench
    - Self-critique
    - Final harmonization
    """
    try:
        # Initialize advanced drafting system
        drafting_system: AdvancedPatentDraftingSystem = get_advanced_drafting_system(
            precision_model=request.precision_model,
            fluency_model=request.fluency_model
        )
        
        # Generate complete draft
        result = drafting_system.generate_complete_draft(
            invention_description=request.description,
            use_ensemble=request.use_ensemble,
            use_scaffolding=request.use_scaffolding,
            use_two_pass=request.use_two_pass,
            use_critique=request.use_critique
        )
        
        # Validate result structure
        if not isinstance(result, dict):
            raise ValueError(f"Expected dict from generate_complete_draft, got {type(result)}")
        
        if "sections" not in result:
            raise ValueError("Missing 'sections' in result")
        
        # Ensure sections is a dict with string values
        sections = result.get("sections", {})
        if not isinstance(sections, dict):
            raise ValueError(f"Expected sections to be dict, got {type(sections)}")
        
        # Convert any non-string section values to strings
        cleaned_sections = {}
        for key, value in sections.items():
            if value is None:
                cleaned_sections[key] = ""
            elif not isinstance(value, str):
                cleaned_sections[key] = str(value)
            else:
                cleaned_sections[key] = value
        
        # Run evaluation if requested
        evaluation_results = None
        if request.run_evaluation:
            try:
                evaluator = EvaluationHarness()
                evaluation_results = evaluator.evaluate_draft(
                    cleaned_sections,
                    glossary=result.get("glossary", {})
                ).to_dict()
            except Exception as e:
                print(f"Warning: Evaluation failed: {e}")
                evaluation_results = None
        
        return AdvancedDraftResponseModel(
            success=True,
            message="Advanced draft generated successfully using 17-step system",
            sections=cleaned_sections,
            glossary=result.get("glossary", {}),
            outline=result.get("outline"),
            critique_results=result.get("critique_results"),
            evaluation_results=evaluation_results,
            generation_time=result.get("generation_time", 0.0),
            model_used=result.get("model_used", {})
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in generate_draft_advanced: {error_details}")
        raise HTTPException(status_code=500, detail=f"Advanced draft generation failed: {str(e)}\n\nDetails: {error_details}")


@router.post("/generate_draft_advanced_with_similarity", response_model=AdvancedDraftWithSimilarityResponseModel)
async def generate_draft_advanced_with_similarity_endpoint(request: AdvancedDraftWithSimilarityRequestModel):
    """
    Generate patent draft using the advanced 17-step system with concurrent similarity search.
    Combines the advanced 17-step generation with background prior art analysis.
    """
    try:
        # Get orchestration service
        orchestration_service = get_orchestration_service()
        
        # Check if Ollama is available
        ollama_service = get_ollama_service()
        if not ollama_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not available. Please install and start Ollama."
            )
        
        # Generate advanced draft with background similarity search
        result = await orchestration_service.generate_advanced_with_similarity(
            description=request.description,
            precision_model=request.precision_model,
            fluency_model=request.fluency_model,
            use_ensemble=request.use_ensemble,
            use_scaffolding=request.use_scaffolding,
            use_two_pass=request.use_two_pass,
            use_critique=request.use_critique,
            search_mode=request.search_mode,
            top_k=request.top_k,
            include_snippets=request.include_snippets
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
        
        # Convert similarity results to response model format
        section_similarities = {}
        for section_name, similarity in result.get("section_similarities", {}).items():
            section_similarities[section_name] = SectionSimilarityModel(
                section_name=similarity.section_name,
                section_text=similarity.section_text,
                similar_patents=similarity.similar_patents,
                analysis_time=similarity.analysis_time,
                patent_count=len(similarity.similar_patents)
            )
        
        return AdvancedDraftWithSimilarityResponseModel(
            success=True,
            message="Advanced draft generated successfully with similarity analysis",
            sections=result.get("sections", {}),
            glossary=result.get("glossary", {}),
            outline=result.get("outline"),
            critique_results=result.get("critique_results"),
            evaluation_results=None,
            generation_time=result.get("generation_time", 0.0),
            model_used=result.get("model_used", {}),
            section_similarities=section_similarities,
            total_analysis_time=result.get("total_analysis_time", 0.0)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in generate_draft_advanced_with_similarity: {error_details}")
        raise HTTPException(status_code=500, detail=f"Advanced draft generation with similarity failed: {str(e)}")


@router.post("/generate_draft_advanced_with_similarity_stream")
async def generate_draft_advanced_with_similarity_stream_endpoint(request: AdvancedDraftWithSimilarityRequestModel):
    """
    Generate patent draft using the advanced 17-step system with real-time section completion streaming.
    Returns Server-Sent Events stream of section completions as they happen.
    """
    async def progress_generator():
        """Generator that yields progress updates as sections complete."""
        try:
            # Check if Ollama is available
            ollama_service = get_ollama_service()
            if not ollama_service.is_available():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Ollama service is not available'})}\n\n"
                return
            
            # Queue for section completions
            sections_queue: asyncio.Queue = asyncio.Queue()
            
            def on_section_callback(section_name: str, section_text: str):
                """Callback invoked when a section completes."""
                try:
                    asyncio.run_coroutine_threadsafe(
                        sections_queue.put((section_name, section_text)),
                        asyncio.get_event_loop()
                    )
                except Exception as e:
                    print(f"Error in section callback: {e}")
            
            # Start generation in a thread
            loop = asyncio.get_event_loop()
            
            # Generate draft with callback
            drafting_system = get_advanced_drafting_system(
                precision_model=request.precision_model,
                fluency_model=request.fluency_model
            )
            
            # Run generation in executor to avoid blocking
            generation_task = loop.run_in_executor(
                None,
                drafting_system.generate_complete_draft,
                request.description,
                request.use_ensemble,
                request.use_scaffolding,
                request.use_two_pass,
                request.use_critique,
                on_section_callback
            )
            
            # Stream sections as they complete
            completed_sections = {}
            try:
                while True:
                    try:
                        # Wait for a section with timeout
                        section_name, section_text = await asyncio.wait_for(
                            sections_queue.get(),
                            timeout=1.0
                        )
                        completed_sections[section_name] = section_text
                        
                        # Send section completion event
                        event_data = {
                            'type': 'section_complete',
                            'section_name': section_name,
                            'section_text': section_text[:500] + '...' if len(section_text) > 500 else section_text,
                            'total_sections': len(completed_sections)
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
                        
                    except asyncio.TimeoutError:
                        # Check if generation is done
                        if generation_task.done():
                            break
                        # Otherwise continue waiting
                        continue
                
                # Wait for generation to complete
                result = await generation_task
                
                if not result.get("success"):
                    yield f"data: {json.dumps({'type': 'error', 'message': result.get('message', 'Unknown error')})}\n\n"
                    return
                
                # Send final result
                final_event = {
                    'type': 'complete',
                    'success': True,
                    'total_sections': len(result.get('sections', {})),
                    'generation_time': result.get('generation_time', 0.0)
                }
                yield f"data: {json.dumps(final_event)}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                
        except Exception as e:
            print(f"Error in progress_generator: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        progress_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/generate_draft_with_similarity", response_model=DraftWithSimilarityResponseModel)
async def generate_draft_with_similarity_endpoint(request: DraftWithSimilarityRequestModel):
    """
    Generate patent application draft with concurrent background search and section-level similarity analysis.
    """
    try:
        # Get orchestration service
        orchestration_service = get_orchestration_service()
        
        # Check if Ollama is available
        ollama_service = get_ollama_service()
        if not ollama_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Ollama service is not available. Please install and start Ollama."
            )
        
        # Generate draft with background search
        result: DraftWithSimilarity = await orchestration_service.generate_with_background_search(
            prompt=request.description,
            search_mode=request.search_mode,
            model_name=request.model,
            template_type=request.template_type,
            top_k=request.top_k,
            include_snippets=request.include_snippets,
            use_cache=request.use_cache
        )
        
        # Convert to response model
        section_similarities = {}
        for section_name, similarity in result.section_similarities.items():
            section_similarities[section_name] = SectionSimilarityModel(
                section_name=similarity.section_name,
                section_text=similarity.section_text,
                similar_patents=similarity.similar_patents,
                analysis_time=similarity.analysis_time,
                patent_count=len(similarity.similar_patents)
            )
        
        return DraftWithSimilarityResponseModel(
            draft=result.draft,
            model=result.model,
            template_type=result.template_type,
            generation_time=result.generation_time,
            cached=result.cached,
            section_similarities=section_similarities,
            total_analysis_time=result.total_analysis_time,
            success=result.success,
            message=result.message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class GenerateWithSearchRequestModel(BaseModel):
    """Request model for generate_with_search endpoint."""
    description: str
    model: str = "llama3.2:3b"
    template_type: str = "utility"
    search_mode: str = "hybrid"
    top_k: int = 5
    include_snippets: bool = True
    use_cache: bool = True
    
    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) < 50:
            raise ValueError('Description must be at least 50 characters long')
        if len(v) > 5000:
            raise ValueError('Description must be no more than 5000 characters long')
        return v.strip()
    
    @validator('model')
    def validate_model(cls, v):
        valid_models = ["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"]
        if v not in valid_models:
            raise ValueError(f'Model must be one of {valid_models}')
        return v
    
    @validator('template_type')
    def validate_template_type(cls, v):
        valid_types = ["utility", "software", "medical", "design"]
        if v not in valid_types:
            raise ValueError(f'Template type must be one of {valid_types}')
        return v
    
    @validator('search_mode')
    def validate_search_mode(cls, v):
        valid_modes = ["tfidf", "semantic", "hybrid", "hybrid-advanced"]
        if v not in valid_modes:
            raise ValueError(f'Search mode must be one of {valid_modes}')
        return v
    
    @validator('top_k')
    def validate_top_k(cls, v):
        if not 1 <= v <= 20:
            raise ValueError('top_k must be between 1 and 20')
        return v


class StatusUpdateModel(BaseModel):
    """Model for status updates during generation."""
    step: str
    message: str
    progress: float  # 0.0 to 1.0
    timestamp: str


class GenerateWithSearchResponseModel(BaseModel):
    """Response model for generate_with_search endpoint."""
    draft: str
    model: str
    template_type: str
    generation_time: float
    cached: bool
    section_similarities: Dict[str, SectionSimilarityModel]
    total_analysis_time: float
    success: bool
    message: str
    metadata: Dict[str, Any]
    status_updates: List[StatusUpdateModel] = []


@router.get("/ollama/health")
async def ollama_health_check():
    """
    Check Ollama service health and available models.
    """
    try:
        ollama_service = get_ollama_service()
        
        if not ollama_service.is_available():
            return {
                "status": "unhealthy",
                "message": "Ollama is not available",
                "available_models": {},
                "error": "Ollama service not running"
            }
        
        available_models = ollama_service.get_available_models()
        
        return {
            "status": "healthy",
            "message": "Ollama service is running",
            "available_models": available_models,
            "default_model": ollama_service.model_name
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error checking Ollama health: {str(e)}",
            "available_models": {},
            "error": str(e)
        }


@router.get("/ollama/models")
async def get_available_models():
    """
    Get list of available Ollama models.
    """
    try:
        ollama_service = get_ollama_service()
        
        if not ollama_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available"
            )
        
        models = ollama_service.get_available_models()
        model_info = {}
        
        for model_name in models:
            info = ollama_service.get_model_info(model_name)
            model_info[model_name] = info
        
        return {
            "available_models": models,
            "model_info": model_info,
            "total_models": len(models)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ollama/pull_model")
async def pull_model(model_name: str):
    """
    Download a specific Ollama model.
    """
    try:
        ollama_service = get_ollama_service()
        
        if not ollama_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not available"
            )
        
        # Validate model name
        valid_models = ["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"]
        if model_name not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name. Must be one of: {valid_models}"
            )
        
        # Pull the model
        success = ollama_service.ensure_model_available(model_name)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_name} downloaded successfully",
                "model_name": model_name
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download model {model_name}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_claims_from_draft(draft: str) -> List[str]:
    """Extract claims from the generated draft text."""
    # This is a simple implementation - you may need to adjust based on your draft format
    import re
    claims = re.findall(r'Claim \d+\.\s*(.*?)(?=\n\nClaim \d+\.|\Z)', draft, re.DOTALL)
    return [claim.strip() for claim in claims if claim.strip()]


@router.post("/generate_draft_with_visualization", response_model=DraftWithSimilarityVisualizationModel)
async def generate_draft_with_visualization_endpoint(request: DraftWithSearchRequestModel):
    """
    Generate a patent draft with similarity visualization and highlighting.
    """
    try:
        # Generate the draft
        draft_result = await generate_draft_endpoint(request)
        
        # Extract claims for similarity search
        claims = extract_claims_from_draft(draft_result.draft)
        
        # If no claims found, use the original description for search
        if not claims:
            claims = [request.description]
        
        # Search for similar patents
        search_results = []
        for claim in claims:
            search_request = SearchRequest(
                query=claim,
                mode=request.search_mode,
                top_k=request.search_top_k,
                include_snippets=request.include_snippets,
                include_metadata=request.include_metadata
            )
            results, _ = run_search(search_request)
            search_results.extend([r.to_dict() for r in results])
            print(f"DEBUG: Search for '{claim[:50]}...' returned {len(results)} results")
        
        # Deduplicate results by doc_id
        seen = set()
        unique_results = []
        for result in search_results:
            if result['doc_id'] not in seen:
                seen.add(result['doc_id'])
                unique_results.append(result)
        
        # Limit to requested top_k
        similar_patents = unique_results[:request.search_top_k]
        
        # Debug logging
        print(f"DEBUG: Found {len(similar_patents)} similar patents")
        if similar_patents:
            print(f"DEBUG: First patent: {similar_patents[0]}")
        
        # Perform similarity visualization
        # visualizer = get_similarity_visualizer()
        # similarity_report = visualizer.generate_similarity_report(draft_result.draft, similar_patents)
        
        # Convert to response models
        highlighted_sections = {}
        # for section_name, section_data in similarity_report["highlighted_sections"].items():
        #     similarity_matches = [
        #         SimilarityMatchModel(
        #             draft_text=match["draft_text"],
        #             prior_text=match["prior_text"],
        #             similarity_score=match["similarity_score"],
        #             prior_patent_id=match["prior_patent_id"],
        #             prior_title=match["prior_title"],
        #             section_type=match["section_type"]
        #         )
        #         for match in section_data["similarity_matches"]
        #     ]
        #     
        #     highlighted_sections[section_name] = HighlightedSectionModel(
        #         section_name=section_name,
        #         text=section_data["text"],
        #         html_output=section_data["html_output"],
        #         markdown_output=section_data["markdown_output"],
        #         similarity_matches=similarity_matches
        #     )
        
        return DraftWithSimilarityVisualizationModel(
            draft=draft_result.draft,
            model=draft_result.model,
            template_type=draft_result.template_type,
            generation_time=draft_result.generation_time,
            cached=draft_result.cached,
            similar_patents=similar_patents,
            highlighted_sections=highlighted_sections,
            similarity_statistics={},
            search_mode=request.search_mode,
            search_top_k=request.search_top_k
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")


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
