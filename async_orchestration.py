#!/usr/bin/env python3
"""
Async orchestration service for concurrent LLM generation and patent search.
Implements background search execution while generating patent drafts.
"""

import asyncio
import time
import json
import re
from typing import Dict, Any, List, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# Import existing services
from ollama_service import get_ollama_service
from search_service import run_search, SearchRequest, SearchResult
from search_utils import load_patent_metadata


@dataclass
class SectionSimilarity:
    """Represents similarity analysis for a patent section."""
    section_name: str
    section_text: str
    similar_patents: List[Dict[str, Any]]
    analysis_time: float


@dataclass
class DraftWithSimilarity:
    """Combined result of draft generation and similarity analysis."""
    draft: str
    model: str
    template_type: str
    generation_time: float
    cached: bool
    section_similarities: Dict[str, SectionSimilarity]
    total_analysis_time: float
    success: bool
    message: str


class AsyncOrchestrationService:
    """Service for orchestrating concurrent LLM generation and patent search."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ollama_service = get_ollama_service()
        self.patent_metadata = None
    
    async def generate_with_background_search(
        self, 
        prompt: str, 
        search_mode: str = 'hybrid',
        model_name: str = None,
        template_type: str = 'utility',
        top_k: int = 5,
        include_snippets: bool = True,
        use_cache: bool = True
    ) -> DraftWithSimilarity:
        """
        Generate patent draft with concurrent background search.
        
        Args:
            prompt: Invention description
            search_mode: Search mode ('tfidf', 'semantic', 'hybrid', 'hybrid-advanced')
            model_name: Ollama model to use
            template_type: Patent template type
            top_k: Number of similar patents to find per section
            include_snippets: Whether to include text snippets
            use_cache: Whether to use cached results
            
        Returns:
            DraftWithSimilarity object with generated draft and similarity analysis
        """
        start_time = time.time()
        
        try:
            # Start both tasks concurrently
            draft_task = asyncio.create_task(
                self._generate_draft_async(prompt, model_name, template_type, use_cache)
            )
            search_task = asyncio.create_task(
                self._search_patents_async(prompt, search_mode, top_k, include_snippets)
            )
            
            # Wait for both to complete
            draft_result, search_results = await asyncio.gather(draft_task, search_task)
            
            # Parse draft into sections and analyze similarity
            section_similarities = await self._analyze_section_similarities(
                draft_result["draft"], 
                search_results,
                search_mode,
                top_k,
                include_snippets
            )
            
            total_time = time.time() - start_time
            
            return DraftWithSimilarity(
                draft=draft_result["draft"],
                model=draft_result["model"],
                template_type=draft_result["template_type"],
                generation_time=draft_result["generation_time"],
                cached=draft_result.get("cached", False),
                section_similarities=section_similarities,
                total_analysis_time=total_time,
                success=True,
                message="Draft generated and similarity analysis completed successfully"
            )
            
        except Exception as e:
            return DraftWithSimilarity(
                draft="",
                model="",
                template_type="",
                generation_time=0.0,
                cached=False,
                section_similarities={},
                total_analysis_time=time.time() - start_time,
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def _generate_draft_async(
        self, 
        prompt: str, 
        model_name: str, 
        template_type: str, 
        use_cache: bool
    ) -> Dict[str, Any]:
        """Generate patent draft asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.ollama_service.generate_patent_draft,
            prompt,
            model_name,
            template_type,
            use_cache
        )
    
    async def _search_patents_async(
        self, 
        query: str, 
        search_mode: str, 
        top_k: int, 
        include_snippets: bool
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Search patents asynchronously."""
        loop = asyncio.get_event_loop()
        
        # Create search request
        request = SearchRequest(
            query=query,
            mode=search_mode,
            top_k=top_k,
            include_snippets=include_snippets,
            include_metadata=True,
            log_enabled=False
        )
        
        return await loop.run_in_executor(
            self.executor,
            run_search,
            request
        )
    
    async def _analyze_section_similarities(
        self,
        draft: str,
        search_results: Tuple[List[SearchResult], Dict[str, Any]],
        search_mode: str,
        top_k: int,
        include_snippets: bool
    ) -> Dict[str, SectionSimilarity]:
        """Analyze similarity for each section of the generated draft."""
        results, _ = search_results
        sections = self._parse_draft_sections(draft)
        section_similarities = {}
        
        # Create tasks for each section analysis
        tasks = []
        for section_name, section_text in sections.items():
            if section_text.strip():
                task = asyncio.create_task(
                    self._analyze_single_section(
                        section_name, 
                        section_text, 
                        search_mode, 
                        top_k, 
                        include_snippets
                    )
                )
                tasks.append((section_name, task))
        
        # Wait for all section analyses to complete
        for section_name, task in tasks:
            try:
                similarity = await task
                section_similarities[section_name] = similarity
            except Exception as e:
                print(f"Error analyzing section {section_name}: {e}")
                # Create empty similarity for failed sections
                section_similarities[section_name] = SectionSimilarity(
                    section_name=section_name,
                    section_text="",
                    similar_patents=[],
                    analysis_time=0.0
                )
        
        return section_similarities
    
    async def _analyze_single_section(
        self,
        section_name: str,
        section_text: str,
        search_mode: str,
        top_k: int,
        include_snippets: bool
    ) -> SectionSimilarity:
        """Analyze similarity for a single section."""
        start_time = time.time()
        
        try:
            # Search for similar patents using this section's text
            search_results, _ = await self._search_patents_async(
                section_text, 
                search_mode, 
                top_k, 
                include_snippets
            )
            
            # Convert to similarity format
            similar_patents = []
            for result in search_results:
                similar_patents.append({
                    "patent_id": result.doc_id,
                    "title": result.title,
                    "similarity_score": result.score,
                    "doc_type": result.doc_type,
                    "snippet": result.snippet if include_snippets else "",
                    "source_file": result.source_file
                })
            
            analysis_time = time.time() - start_time
            
            return SectionSimilarity(
                section_name=section_name,
                section_text=section_text,
                similar_patents=similar_patents,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            print(f"Error in section analysis for {section_name}: {e}")
            return SectionSimilarity(
                section_name=section_name,
                section_text=section_text,
                similar_patents=[],
                analysis_time=time.time() - start_time
            )
    
    def _parse_draft_sections(self, draft: str) -> Dict[str, str]:
        """Parse generated draft into structured sections."""
        sections = {}
        
        # Define section patterns
        section_patterns = {
            "title": r"TITLE OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "field": r"FIELD OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "background": r"BACKGROUND OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "summary": r"SUMMARY OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "drawings": r"BRIEF DESCRIPTION OF THE DRAWINGS\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "description": r"DETAILED DESCRIPTION OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "claims": r"CLAIMS\s*\n(.*?)(?=\n[A-Z]|\n\n|$)"
        }
        
        # Extract each section
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, draft, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
            else:
                sections[section_name] = ""
        
        return sections
    
    def get_section_similarity_map(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        Utility function to get section similarity map from a draft result.
        
        Args:
            draft: DraftWithSimilarity object or dict with section_similarities
            
        Returns:
            Dict mapping section names to similarity data
        """
        if isinstance(draft, DraftWithSimilarity):
            section_similarities = draft.section_similarities
        elif isinstance(draft, dict) and "section_similarities" in draft:
            section_similarities = draft["section_similarities"]
        else:
            return {}
        
        similarity_map = {}
        for section_name, similarity in section_similarities.items():
            similarity_map[section_name] = {
                "section_name": similarity.section_name,
                "similar_patents": similarity.similar_patents,
                "analysis_time": similarity.analysis_time,
                "patent_count": len(similarity.similar_patents)
            }
        
        return similarity_map
    
    def to_json_schema(self, result: DraftWithSimilarity) -> Dict[str, Any]:
        """Convert result to JSON-serializable format."""
        return {
            "draft": result.draft,
            "model": result.model,
            "template_type": result.template_type,
            "generation_time": result.generation_time,
            "cached": result.cached,
            "section_similarities": {
                section_name: {
                    "section_name": similarity.section_name,
                    "section_text": similarity.section_text,
                    "similar_patents": similarity.similar_patents,
                    "analysis_time": similarity.analysis_time,
                    "patent_count": len(similarity.similar_patents)
                }
                for section_name, similarity in result.section_similarities.items()
            },
            "total_analysis_time": result.total_analysis_time,
            "success": result.success,
            "message": result.message
        }
    
    def __del__(self):
        """Cleanup executor on destruction."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


# Global service instance
_orchestration_service = None

def get_orchestration_service() -> AsyncOrchestrationService:
    """Get global orchestration service instance."""
    global _orchestration_service
    if _orchestration_service is None:
        _orchestration_service = AsyncOrchestrationService()
    return _orchestration_service


# Convenience function for easy usage
async def generate_with_background_search(
    prompt: str, 
    search_mode: str = 'hybrid',
    model_name: str = None,
    template_type: str = 'utility',
    top_k: int = 5,
    include_snippets: bool = True,
    use_cache: bool = True
) -> DraftWithSimilarity:
    """
    Convenience function for generating draft with background search.
    
    Args:
        prompt: Invention description
        search_mode: Search mode ('tfidf', 'semantic', 'hybrid', 'hybrid-advanced')
        model_name: Ollama model to use
        template_type: Patent template type
        top_k: Number of similar patents to find per section
        include_snippets: Whether to include text snippets
        use_cache: Whether to use cached results
        
    Returns:
        DraftWithSimilarity object with generated draft and similarity analysis
    """
    service = get_orchestration_service()
    return await service.generate_with_background_search(
        prompt=prompt,
        search_mode=search_mode,
        model_name=model_name,
        template_type=template_type,
        top_k=top_k,
        include_snippets=include_snippets,
        use_cache=use_cache
    )


if __name__ == "__main__":
    # Test the orchestration service
    async def test_orchestration():
        print("Testing Async Orchestration Service...")
        
        service = AsyncOrchestrationService()
        
        # Test with a sample prompt
        test_prompt = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        
        print(f"Generating draft with background search for: {test_prompt[:50]}...")
        
        result = await service.generate_with_background_search(
            prompt=test_prompt,
            search_mode='hybrid',
            top_k=3,
            include_snippets=True
        )
        
        print(f"Success: {result.success}")
        print(f"Generation time: {result.generation_time:.2f}s")
        print(f"Total analysis time: {result.total_analysis_time:.2f}s")
        print(f"Sections analyzed: {len(result.section_similarities)}")
        
        for section_name, similarity in result.section_similarities.items():
            print(f"  {section_name}: {len(similarity.similar_patents)} similar patents")
        
        # Test JSON serialization
        json_result = service.to_json_schema(result)
        print(f"JSON serializable: {isinstance(json_result, dict)}")
        
        print("Orchestration test completed!")
    
    # Run the test
    asyncio.run(test_orchestration())
