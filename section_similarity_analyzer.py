#!/usr/bin/env python3
"""
Section-level similarity analysis utility.
Provides per-section similarity comparison after each generation step.
"""

import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from search_service import run_search, SearchRequest, SearchResult
from search_utils import load_patent_metadata


@dataclass
class SectionSimilarityResult:
    """Result of section similarity analysis."""
    section_name: str
    section_text: str
    similar_patents: List[Dict[str, Any]]
    analysis_time: float
    patent_count: int
    top_similarity_score: float = 0.0


class SectionSimilarityAnalyzer:
    """Analyzes similarity for individual patent sections."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = asyncio.get_event_loop().run_in_executor if asyncio.get_event_loop().is_running() else None
    
    def parse_draft_sections(self, draft_text: str) -> Dict[str, str]:
        """
        Parse generated draft into structured sections.
        
        Args:
            draft_text: The generated patent draft text
            
        Returns:
            Dict mapping section names to section text content
        """
        sections = {}
        
        # Define section patterns with improved regex
        section_patterns = {
            "title": r"TITLE OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "abstract": r"ABSTRACT\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "field": r"FIELD OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "background": r"BACKGROUND OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "summary": r"SUMMARY OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "drawings": r"BRIEF DESCRIPTION OF THE DRAWINGS\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "description": r"DETAILED DESCRIPTION OF THE INVENTION\s*\n(.*?)(?=\n[A-Z]|\n\n|$)",
            "claims": r"CLAIMS\s*\n(.*?)(?=\n[A-Z]|\n\n|$)"
        }
        
        # Extract each section
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, draft_text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
            else:
                sections[section_name] = ""
        
        return sections
    
    async def analyze_similarity(
        self, 
        section_text: str, 
        search_mode: str = 'hybrid',
        top_k: int = 5,
        include_snippets: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Analyze similarity for a single section using the existing search API.
        
        Args:
            section_text: Text content of the section to analyze
            search_mode: Search mode ('tfidf', 'semantic', 'hybrid', 'hybrid-advanced')
            top_k: Number of similar patents to return
            include_snippets: Whether to include text snippets
            
        Returns:
            List of similar patents as {patent_id, title, similarity_score} objects
        """
        if not section_text or not section_text.strip():
            return []
        
        try:
            # Create search request
            request = SearchRequest(
                query=section_text.strip(),
                mode=search_mode,
                top_k=top_k,
                include_snippets=include_snippets,
                include_metadata=True,
                log_enabled=False
            )
            
            # Run search
            search_results, _ = await self._run_search_async(request)
            
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
            
            return similar_patents
            
        except Exception as e:
            print(f"Error analyzing similarity for section: {e}")
            return []
    
    async def _run_search_async(self, request: SearchRequest) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Run search asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, run_search, request)
    
    async def analyze_all_sections(
        self,
        draft_text: str,
        search_mode: str = 'hybrid',
        top_k: int = 5,
        include_snippets: bool = True
    ) -> Dict[str, SectionSimilarityResult]:
        """
        Analyze similarity for all sections in a draft.
        
        Args:
            draft_text: The generated patent draft text
            search_mode: Search mode to use
            top_k: Number of similar patents per section
            include_snippets: Whether to include text snippets
            
        Returns:
            Dict mapping section names to SectionSimilarityResult objects
        """
        # Parse sections
        sections = self.parse_draft_sections(draft_text)
        
        # Create tasks for each section
        tasks = []
        for section_name, section_text in sections.items():
            if section_text.strip():
                task = asyncio.create_task(
                    self._analyze_section_with_timing(
                        section_name, 
                        section_text, 
                        search_mode, 
                        top_k, 
                        include_snippets
                    )
                )
                tasks.append((section_name, task))
        
        # Wait for all analyses to complete
        results = {}
        for section_name, task in tasks:
            try:
                result = await task
                results[section_name] = result
            except Exception as e:
                print(f"Error analyzing section {section_name}: {e}")
                # Create empty result for failed sections
                results[section_name] = SectionSimilarityResult(
                    section_name=section_name,
                    section_text="",
                    similar_patents=[],
                    analysis_time=0.0,
                    patent_count=0,
                    top_similarity_score=0.0
                )
        
        return results
    
    async def _analyze_section_with_timing(
        self,
        section_name: str,
        section_text: str,
        search_mode: str,
        top_k: int,
        include_snippets: bool
    ) -> SectionSimilarityResult:
        """Analyze a single section with timing."""
        start_time = time.time()
        
        similar_patents = await self.analyze_similarity(
            section_text, 
            search_mode, 
            top_k, 
            include_snippets
        )
        
        analysis_time = time.time() - start_time
        top_similarity_score = similar_patents[0]["similarity_score"] if similar_patents else 0.0
        
        return SectionSimilarityResult(
            section_name=section_name,
            section_text=section_text,
            similar_patents=similar_patents,
            analysis_time=analysis_time,
            patent_count=len(similar_patents),
            top_similarity_score=top_similarity_score
        )


def get_section_similarity_map(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Utility function to get section similarity map from a draft result.
    
    Args:
        draft: Draft result dict with section_similarities or similar structure
        
    Returns:
        Dict mapping section names to similarity data
    """
    if not isinstance(draft, dict):
        return {}
    
    # Handle different input formats
    if "section_similarities" in draft:
        section_similarities = draft["section_similarities"]
    elif "sections" in draft:
        section_similarities = draft["sections"]
    else:
        return {}
    
    similarity_map = {}
    
    for section_name, similarity_data in section_similarities.items():
        if isinstance(similarity_data, dict):
            similarity_map[section_name] = {
                "section_name": similarity_data.get("section_name", section_name),
                "similar_patents": similarity_data.get("similar_patents", []),
                "analysis_time": similarity_data.get("analysis_time", 0.0),
                "patent_count": similarity_data.get("patent_count", len(similarity_data.get("similar_patents", []))),
                "top_similarity_score": similarity_data.get("top_similarity_score", 0.0)
            }
        else:
            # Handle object-based similarity data
            similarity_map[section_name] = {
                "section_name": getattr(similarity_data, "section_name", section_name),
                "similar_patents": getattr(similarity_data, "similar_patents", []),
                "analysis_time": getattr(similarity_data, "analysis_time", 0.0),
                "patent_count": getattr(similarity_data, "patent_count", len(getattr(similarity_data, "similar_patents", []))),
                "top_similarity_score": getattr(similarity_data, "top_similarity_score", 0.0)
            }
    
    return similarity_map


async def analyze_draft_sections(
    draft_text: str,
    search_mode: str = 'hybrid',
    top_k: int = 5,
    include_snippets: bool = True
) -> Dict[str, SectionSimilarityResult]:
    """
    Convenience function to analyze all sections in a draft.
    
    Args:
        draft_text: The generated patent draft text
        search_mode: Search mode to use
        top_k: Number of similar patents per section
        include_snippets: Whether to include text snippets
        
    Returns:
        Dict mapping section names to SectionSimilarityResult objects
    """
    analyzer = SectionSimilarityAnalyzer()
    return await analyzer.analyze_all_sections(
        draft_text, 
        search_mode, 
        top_k, 
        include_snippets
    )


# Global analyzer instance
_analyzer = None

def get_section_analyzer() -> SectionSimilarityAnalyzer:
    """Get global section analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SectionSimilarityAnalyzer()
    return _analyzer


if __name__ == "__main__":
    # Test the section similarity analyzer
    async def test_analyzer():
        print("Testing Section Similarity Analyzer...")
        
        # Sample draft text
        sample_draft = """TITLE OF THE INVENTION
Neural Network System for Medical Image Analysis

ABSTRACT
A system for analyzing medical images using convolutional neural networks to detect anomalies in X-ray scans with improved accuracy and speed.

FIELD OF THE INVENTION
This invention relates to medical image analysis systems and methods for detecting anomalies in X-ray scans using artificial intelligence.

BACKGROUND OF THE INVENTION
Traditional medical image analysis relies on manual inspection by radiologists, which is time-consuming and prone to human error. There is a need for automated systems that can accurately detect anomalies in medical images.

SUMMARY OF THE INVENTION
The present invention provides a neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

CLAIMS
1. A medical image analysis system comprising:
   a) A convolutional neural network with multiple layers;
   b) An input module for receiving X-ray images;
   c) An output module for generating anomaly detection results."""
        
        analyzer = SectionSimilarityAnalyzer()
        
        # Test section parsing
        print("\n1. Testing section parsing:")
        sections = analyzer.parse_draft_sections(sample_draft)
        for section_name, section_text in sections.items():
            if section_text.strip():
                print(f"  {section_name}: {len(section_text)} characters")
        
        # Test similarity analysis
        print("\n2. Testing similarity analysis:")
        results = await analyzer.analyze_all_sections(
            sample_draft,
            search_mode='hybrid',
            top_k=3,
            include_snippets=True
        )
        
        for section_name, result in results.items():
            if result.similar_patents:
                print(f"  {section_name}: {result.patent_count} similar patents, {result.analysis_time:.3f}s")
                print(f"    Top similarity: {result.top_similarity_score:.3f}")
        
        # Test utility function
        print("\n3. Testing utility function:")
        draft_dict = {"section_similarities": results}
        similarity_map = get_section_similarity_map(draft_dict)
        print(f"  Similarity map created with {len(similarity_map)} sections")
        
        print("\nSection similarity analyzer test completed!")
    
    asyncio.run(test_analyzer())
