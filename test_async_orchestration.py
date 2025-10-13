#!/usr/bin/env python3
"""
Comprehensive tests for async orchestration service.
Tests concurrent LLM generation and patent search functionality.
"""

import asyncio
import json
import time
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Import the modules to test
from async_orchestration import (
    AsyncOrchestrationService, 
    DraftWithSimilarity, 
    SectionSimilarity,
    generate_with_background_search
)
from search_service import SearchResult


class TestAsyncOrchestrationService:
    """Test cases for AsyncOrchestrationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AsyncOrchestrationService(max_workers=2)
        self.sample_prompt = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        
        # Mock search results
        self.mock_search_results = [
            SearchResult(
                doc_id="US12345678",
                score=0.85,
                title="Medical Image Analysis System",
                doc_type="grant",
                source_file="test_grant.xml",
                snippet="A system for analyzing medical images using neural networks...",
                base_doc_id="US12345678"
            ),
            SearchResult(
                doc_id="US87654321",
                score=0.78,
                title="Convolutional Neural Network for X-ray Analysis",
                doc_type="application",
                source_file="test_app.xml",
                snippet="Convolutional neural networks for detecting anomalies in X-ray images...",
                base_doc_id="US87654321"
            )
        ]
        
        # Mock draft result
        self.mock_draft_result = {
            "draft": """TITLE OF THE INVENTION
Medical Image Analysis System Using Neural Networks

FIELD OF THE INVENTION
This invention relates to medical image analysis systems and methods for detecting anomalies in X-ray scans using convolutional neural networks.

BACKGROUND OF THE INVENTION
Traditional medical image analysis relies on manual inspection by radiologists, which is time-consuming and prone to human error. There is a need for automated systems that can accurately detect anomalies in medical images.

SUMMARY OF THE INVENTION
The present invention provides a neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

BRIEF DESCRIPTION OF THE DRAWINGS
Figure 1 shows the overall system architecture.
Figure 2 illustrates the convolutional neural network structure.

DETAILED DESCRIPTION OF THE INVENTION
The system comprises a convolutional neural network with multiple layers designed to process X-ray images and identify potential anomalies.

CLAIMS
1. A medical image analysis system comprising:
   a) A convolutional neural network with multiple layers;
   b) An input module for receiving X-ray images;
   c) An output module for generating anomaly detection results.

2. The system of claim 1, wherein the neural network includes at least three convolutional layers.

3. The system of claim 1, further comprising a preprocessing module for image normalization.""",
            "model": "llama3.2:3b",
            "template_type": "utility",
            "generation_time": 2.5,
            "cached": False
        }
    
    @pytest.mark.asyncio
    async def test_generate_with_background_search_success(self):
        """Test successful draft generation with background search."""
        with patch.object(self.service.ollama_service, 'generate_patent_draft') as mock_generate, \
             patch.object(self.service, '_search_patents_async') as mock_search, \
             patch.object(self.service, '_analyze_section_similarities') as mock_analyze:
            
            # Setup mocks
            mock_generate.return_value = self.mock_draft_result
            mock_search.return_value = (self.mock_search_results, {"search_time": 1.0})
            mock_analyze.return_value = {
                "title": SectionSimilarity(
                    section_name="title",
                    section_text="Medical Image Analysis System Using Neural Networks",
                    similar_patents=[{"patent_id": "US12345678", "title": "Test Patent", "similarity_score": 0.85}],
                    analysis_time=0.5
                )
            }
            
            # Execute test
            result = await self.service.generate_with_background_search(
                prompt=self.sample_prompt,
                search_mode='hybrid',
                top_k=3
            )
            
            # Assertions
            assert result.success is True
            assert result.draft == self.mock_draft_result["draft"]
            assert result.model == self.mock_draft_result["model"]
            assert result.template_type == self.mock_draft_result["template_type"]
            assert result.generation_time == self.mock_draft_result["generation_time"]
            assert result.cached == self.mock_draft_result["cached"]
            assert len(result.section_similarities) > 0
            assert result.total_analysis_time > 0
            assert "successfully" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_generate_with_background_search_ollama_error(self):
        """Test handling of Ollama service errors."""
        with patch.object(self.service.ollama_service, 'generate_patent_draft') as mock_generate:
            # Setup mock to raise exception
            mock_generate.side_effect = RuntimeError("Ollama service unavailable")
            
            # Execute test
            result = await self.service.generate_with_background_search(
                prompt=self.sample_prompt,
                search_mode='hybrid'
            )
            
            # Assertions
            assert result.success is False
            assert result.draft == ""
            assert "Error" in result.message
            assert "Ollama service unavailable" in result.message
    
    @pytest.mark.asyncio
    async def test_generate_with_background_search_search_error(self):
        """Test handling of search service errors."""
        with patch.object(self.service.ollama_service, 'generate_patent_draft') as mock_generate, \
             patch.object(self.service, '_search_patents_async') as mock_search:
            
            # Setup mocks
            mock_generate.return_value = self.mock_draft_result
            mock_search.side_effect = Exception("Search service error")
            
            # Execute test
            result = await self.service.generate_with_background_search(
                prompt=self.sample_prompt,
                search_mode='hybrid'
            )
            
            # Assertions
            assert result.success is False
            assert "Error" in result.message
            assert "Search service error" in result.message
    
    def test_parse_draft_sections(self):
        """Test parsing of draft into structured sections."""
        draft_text = """TITLE OF THE INVENTION
Test Patent Title

FIELD OF THE INVENTION
This relates to test technology.

BACKGROUND OF THE INVENTION
Background information here.

SUMMARY OF THE INVENTION
Summary of the invention.

BRIEF DESCRIPTION OF THE DRAWINGS
Figure descriptions.

DETAILED DESCRIPTION OF THE INVENTION
Detailed technical description.

CLAIMS
1. A test claim."""
        
        sections = self.service._parse_draft_sections(draft_text)
        
        # Assertions
        assert "title" in sections
        assert "field" in sections
        assert "background" in sections
        assert "summary" in sections
        assert "drawings" in sections
        assert "description" in sections
        assert "claims" in sections
        
        assert "Test Patent Title" in sections["title"]
        assert "test technology" in sections["field"]
        assert "Background information" in sections["background"]
        assert "Summary of the invention" in sections["summary"]
        assert "Figure descriptions" in sections["drawings"]
        assert "Detailed technical description" in sections["description"]
        assert "A test claim" in sections["claims"]
    
    def test_parse_draft_sections_empty(self):
        """Test parsing of empty or malformed draft."""
        sections = self.service._parse_draft_sections("")
        
        # All sections should be empty strings
        for section_name, section_text in sections.items():
            assert section_text == ""
    
    def test_get_section_similarity_map(self):
        """Test conversion to section similarity map."""
        # Create mock section similarities
        section_similarities = {
            "title": SectionSimilarity(
                section_name="title",
                section_text="Test Title",
                similar_patents=[{"patent_id": "US123", "title": "Test", "similarity_score": 0.8}],
                analysis_time=0.5
            )
        }
        
        # Create mock result
        result = DraftWithSimilarity(
            draft="Test draft",
            model="test_model",
            template_type="utility",
            generation_time=1.0,
            cached=False,
            section_similarities=section_similarities,
            total_analysis_time=2.0,
            success=True,
            message="Success"
        )
        
        # Test conversion
        similarity_map = self.service.get_section_similarity_map(result)
        
        # Assertions
        assert "title" in similarity_map
        assert similarity_map["title"]["section_name"] == "title"
        assert similarity_map["title"]["patent_count"] == 1
        assert similarity_map["title"]["analysis_time"] == 0.5
        assert len(similarity_map["title"]["similar_patents"]) == 1
    
    def test_to_json_schema(self):
        """Test JSON schema conversion."""
        # Create mock result
        section_similarities = {
            "title": SectionSimilarity(
                section_name="title",
                section_text="Test Title",
                similar_patents=[{"patent_id": "US123", "title": "Test", "similarity_score": 0.8}],
                analysis_time=0.5
            )
        }
        
        result = DraftWithSimilarity(
            draft="Test draft",
            model="test_model",
            template_type="utility",
            generation_time=1.0,
            cached=False,
            section_similarities=section_similarities,
            total_analysis_time=2.0,
            success=True,
            message="Success"
        )
        
        # Convert to JSON schema
        json_result = self.service.to_json_schema(result)
        
        # Assertions
        assert isinstance(json_result, dict)
        assert json_result["draft"] == "Test draft"
        assert json_result["model"] == "test_model"
        assert json_result["template_type"] == "utility"
        assert json_result["generation_time"] == 1.0
        assert json_result["cached"] is False
        assert json_result["total_analysis_time"] == 2.0
        assert json_result["success"] is True
        assert json_result["message"] == "Success"
        assert "section_similarities" in json_result
        assert "title" in json_result["section_similarities"]
        
        # Test JSON serialization
        json_str = json.dumps(json_result)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed == json_result


class TestConvenienceFunction:
    """Test the convenience function."""
    
    @pytest.mark.asyncio
    async def test_generate_with_background_search_function(self):
        """Test the convenience function works correctly."""
        with patch('async_orchestration.get_orchestration_service') as mock_get_service:
            mock_service = Mock()
            mock_result = DraftWithSimilarity(
                draft="Test draft",
                model="test_model",
                template_type="utility",
                generation_time=1.0,
                cached=False,
                section_similarities={},
                total_analysis_time=2.0,
                success=True,
                message="Success"
            )
            mock_service.generate_with_background_search.return_value = mock_result
            mock_get_service.return_value = mock_service
            
            # Test the convenience function
            result = await generate_with_background_search(
                prompt="Test prompt",
                search_mode='hybrid',
                top_k=5
            )
            
            # Assertions
            assert result == mock_result
            mock_service.generate_with_background_search.assert_called_once_with(
                prompt="Test prompt",
                search_mode='hybrid',
                model_name=None,
                template_type='utility',
                top_k=5,
                include_snippets=True,
                use_cache=True
            )


class TestConcurrency:
    """Test concurrency aspects."""
    
    @pytest.mark.asyncio
    async def test_concurrent_execution_timing(self):
        """Test that generation and search run concurrently."""
        service = AsyncOrchestrationService(max_workers=2)
        
        # Mock functions with delays
        async def mock_generate_with_delay():
            await asyncio.sleep(0.1)  # 100ms delay
            return self.mock_draft_result
        
        async def mock_search_with_delay():
            await asyncio.sleep(0.1)  # 100ms delay
            return (self.mock_search_results, {"search_time": 0.1})
        
        with patch.object(service, '_generate_draft_async', side_effect=mock_generate_with_delay), \
             patch.object(service, '_search_patents_async', side_effect=mock_search_with_delay), \
             patch.object(service, '_analyze_section_similarities', return_value={}):
            
            start_time = time.time()
            result = await service.generate_with_background_search(
                prompt="Test prompt",
                search_mode='hybrid'
            )
            total_time = time.time() - start_time
            
            # Should take approximately 100ms (not 200ms) due to concurrency
            assert total_time < 0.15  # Allow some overhead
            assert result.success is True


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_invalid_prompt(self):
        """Test handling of invalid prompts."""
        service = AsyncOrchestrationService()
        
        # Test empty prompt
        result = await service.generate_with_background_search(
            prompt="",
            search_mode='hybrid'
        )
        assert result.success is False
        assert "Error" in result.message
        
        # Test very short prompt
        result = await service.generate_with_background_search(
            prompt="short",
            search_mode='hybrid'
        )
        assert result.success is False
        assert "Error" in result.message
    
    @pytest.mark.asyncio
    async def test_invalid_search_mode(self):
        """Test handling of invalid search modes."""
        service = AsyncOrchestrationService()
        
        with patch.object(service.ollama_service, 'generate_patent_draft') as mock_generate:
            mock_generate.return_value = {
                "draft": "Test draft",
                "model": "test",
                "template_type": "utility",
                "generation_time": 1.0,
                "cached": False
            }
            
            result = await service.generate_with_background_search(
                prompt="Valid prompt with sufficient length for testing purposes",
                search_mode='invalid_mode'
            )
            
            # Should still succeed as search mode validation happens in SearchRequest
            assert result.success is True


if __name__ == "__main__":
    # Run basic tests
    print("Running async orchestration tests...")
    
    async def run_tests():
        service = AsyncOrchestrationService()
        
        # Test 1: Basic functionality
        print("Test 1: Basic draft generation with background search")
        result = await service.generate_with_background_search(
            prompt="A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
            search_mode='hybrid',
            top_k=3
        )
        print(f"Success: {result.success}")
        print(f"Generation time: {result.generation_time:.2f}s")
        print(f"Total time: {result.total_analysis_time:.2f}s")
        print(f"Sections: {len(result.section_similarities)}")
        
        # Test 2: JSON serialization
        print("\nTest 2: JSON serialization")
        json_result = service.to_json_schema(result)
        json_str = json.dumps(json_result, indent=2)
        print(f"JSON length: {len(json_str)} characters")
        print("JSON serialization successful")
        
        # Test 3: Section parsing
        print("\nTest 3: Section parsing")
        test_draft = """TITLE OF THE INVENTION
Test Patent

FIELD OF THE INVENTION
Test field.

CLAIMS
1. A test claim."""
        
        sections = service._parse_draft_sections(test_draft)
        print(f"Parsed sections: {list(sections.keys())}")
        print(f"Title section: {sections['title'][:50]}...")
        
        print("\nAll tests completed successfully!")
    
    asyncio.run(run_tests())
