#!/usr/bin/env python3
"""
FastAPI main application for Patent NLP Project.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_endpoints import router

# Create FastAPI app
app = FastAPI(
    title="Patent NLP API",
    description="Advanced patent search and analysis API with semantic search, re-ranking, and summarization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["patent-search"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Patent NLP API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/v1/search",
            "summarize": "/api/v1/summarize", 
            "batch_search": "/api/v1/batch_search",
            "compare_modes": "/api/v1/compare_modes",
            "logs_analyze": "/api/v1/logs/analyze",
            "health": "/api/v1/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
