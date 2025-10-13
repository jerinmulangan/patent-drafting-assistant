#!/usr/bin/env python3
"""
Unit tests for section similarity analysis.
Tests with mock LLM outputs and dummy patent database.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from section_similarity_analyzer import (
    SectionSimilarityAnalyzer,
    SectionSimilarityResult,
    get_section_similarity_map,
    analyze_draft_sections
)
from search_service import SearchResult


class TestSectionSimilarityAnalyzer:
    """Test cases for SectionSimilarityAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SectionSimilarityAnalyzer()
        
        # Mock LLM outputs for testing
        self.mock_draft_outputs = {
            "simple_utility": """TITLE OF THE INVENTION
Simple Mechanical Device

ABSTRACT
A simple mechanical device for opening bottles with improved ergonomics.

FIELD OF THE INVENTION
This invention relates to mechanical devices for opening containers.

BACKGROUND OF THE INVENTION
Traditional bottle openers are difficult to use and can cause hand strain.

SUMMARY OF THE INVENTION
The present invention provides a mechanical device with improved ergonomics.

CLAIMS
1. A mechanical device comprising:
   a) A handle portion;
   b) An opening mechanism;
   c) A safety feature.""",
            
            "complex_software": """TITLE OF THE INVENTION
Advanced Machine Learning System for Autonomous Vehicles

ABSTRACT
A machine learning system using deep neural networks for autonomous vehicle navigation with computer vision and sensor fusion.

FIELD OF THE INVENTION
This invention relates to autonomous vehicle systems and machine learning algorithms.

BACKGROUND OF THE INVENTION
Current autonomous vehicle systems lack sufficient accuracy and reliability for safe operation.

SUMMARY OF THE INVENTION
The present invention provides an advanced machine learning system with improved accuracy.

DETAILED DESCRIPTION OF THE INVENTION
The system comprises multiple neural networks working together to process sensor data.

CLAIMS
1. A machine learning system comprising:
   a) A convolutional neural network for image processing;
   b) A recurrent neural network for sequence modeling;
   c) A fusion module for combining sensor data."""
        }
        
        # Mock patent database for testing
        self.mock_patent_database = [
            {
                "patent_id": "US12345678",
                "title": "Mechanical Bottle Opener Device",
                "abstract": "A mechanical device for opening bottles with ergonomic design",
                "claims": "A bottle opener comprising a handle and opening mechanism",
                "similarity_score": 0.85
            },
            {
                "patent_id": "US87654321",
                "title": "Ergonomic Container Opening Device",
                "abstract": "An ergonomic device for opening various types of containers",
                "claims": "A container opener with improved handle design",
                "similarity_score": 0.78
            },
            {
                "patent_id": "US11223344",
                "title": "Autonomous Vehicle Navigation System",
                "abstract": "A system for autonomous vehicle navigation using machine learning",
                "claims": "A navigation system comprising sensors and processing unit",
                "similarity_score": 0.92
            },
            {
                "patent_id": "US55667788",
                "title": "Deep Learning for Vehicle Control",
                "abstract": "Deep neural networks for controlling autonomous vehicles",
                "claims": "A control system using neural networks for vehicle operation",
                "similarity_score": 0.88
            }
        ]
    
    def test_parse_draft_sections_simple(self):
        """Test parsing of simple draft sections."""
        draft_text = self.mock_draft_outputs["simple_utility"]
        sections = self.analyzer.parse_draft_sections(draft_text)
        
        # Check that all expected sections are found
        expected_sections = ['title', 'abstract', 'field', 'background', 'summary', 'claims']
        for section in expected_sections:
            assert section in sections
            assert sections[section].strip() != "", f"Section {section} should not be empty"
        
        # Check specific content
        assert "Simple Mechanical Device" in sections["title"]
        assert "bottles with improved ergonomics" in sections["abstract"]
        assert "mechanical devices for opening containers" in sections["field"]
        assert "hand strain" in sections["background"]
        assert "improved ergonomics" in sections["summary"]
        assert "A mechanical device comprising" in sections["claims"]
    
    def test_parse_draft_sections_complex(self):
        """Test parsing of complex draft sections."""
        draft_text = self.mock_draft_outputs["complex_software"]
        sections = self.analyzer.parse_draft_sections(draft_text)
        
        # Check that all expected sections are found
        expected_sections = ['title', 'abstract', 'field', 'background', 'summary', 'description', 'claims']
        for section in expected_sections:
            assert section in sections
            if section in ['title', 'abstract', 'field', 'background', 'summary', 'claims']:
                assert sections[section].strip() != "", f"Section {section} should not be empty"
        
        # Check specific content
        assert "Advanced Machine Learning System" in sections["title"]
        assert "deep neural networks" in sections["abstract"]
        assert "autonomous vehicle systems" in sections["field"]
        assert "accuracy and reliability" in sections["background"]
        assert "neural networks working together" in sections["description"]
    
    def test_parse_draft_sections_empty(self):
        """Test parsing of empty or malformed draft."""
        sections = self.analyzer.parse_draft_sections("")
        
        # All sections should be empty strings
        for section_name, section_text in sections.items():
            assert section_text == "", f"Section {section_name} should be empty"
    
    def test_parse_draft_sections_malformed(self):
        """Test parsing of malformed draft without proper section headers."""
        malformed_draft = "This is just some text without proper section headers."
        sections = self.analyzer.parse_draft_sections(malformed_draft)
        
        # All sections should be empty
        for section_name, section_text in sections.items():
            assert section_text == "", f"Section {section_name} should be empty for malformed draft"
    
    @pytest.mark.asyncio
    async def test_analyze_similarity_with_mock_data(self):
        """Test similarity analysis with mock patent database."""
        # Mock search results
        mock_search_results = [
            SearchResult(
                doc_id="US12345678",
                score=0.85,
                title="Mechanical Bottle Opener Device",
                doc_type="grant",
                source_file="test_grant.xml",
                snippet="A mechanical device for opening bottles...",
                base_doc_id="US12345678"
            ),
            SearchResult(
                doc_id="US87654321",
                score=0.78,
                title="Ergonomic Container Opening Device",
                doc_type="application",
                source_file="test_app.xml",
                snippet="An ergonomic device for opening containers...",
                base_doc_id="US87654321"
            )
        ]
        
        with patch.object(self.analyzer, '_run_search_async') as mock_search:
            mock_search.return_value = (mock_search_results, {"search_time": 0.5})
            
            # Test similarity analysis
            section_text = "A mechanical device for opening bottles with improved ergonomics."
            similar_patents = await self.analyzer.analyze_similarity(
                section_text, 
                search_mode='hybrid',
                top_k=2,
                include_snippets=True
            )
            
            # Assertions
            assert len(similar_patents) == 2
            assert similar_patents[0]["patent_id"] == "US12345678"
            assert similar_patents[0]["title"] == "Mechanical Bottle Opener Device"
            assert similar_patents[0]["similarity_score"] == 0.85
            assert similar_patents[0]["doc_type"] == "grant"
            assert "mechanical device" in similar_patents[0]["snippet"]
            
            assert similar_patents[1]["patent_id"] == "US87654321"
            assert similar_patents[1]["similarity_score"] == 0.78
    
    @pytest.mark.asyncio
    async def test_analyze_similarity_empty_text(self):
        """Test similarity analysis with empty text."""
        similar_patents = await self.analyzer.analyze_similarity("")
        assert similar_patents == []
        
        similar_patents = await self.analyzer.analyze_similarity("   ")
        assert similar_patents == []
    
    @pytest.mark.asyncio
    async def test_analyze_similarity_error_handling(self):
        """Test error handling in similarity analysis."""
        with patch.object(self.analyzer, '_run_search_async') as mock_search:
            mock_search.side_effect = Exception("Search service error")
            
            similar_patents = await self.analyzer.analyze_similarity(
                "Test text",
                search_mode='hybrid'
            )
            
            assert similar_patents == []
    
    @pytest.mark.asyncio
    async def test_analyze_all_sections(self):
        """Test analysis of all sections in a draft."""
        draft_text = self.mock_draft_outputs["simple_utility"]
        
        # Mock search results for different sections
        mock_results = {
            "title": [
                SearchResult("US12345678", 0.85, "Mechanical Bottle Opener", "grant", "", "snippet", ""),
                SearchResult("US87654321", 0.78, "Ergonomic Device", "application", "", "snippet", "")
            ],
            "abstract": [
                SearchResult("US12345678", 0.90, "Bottle Opener Device", "grant", "", "snippet", ""),
                SearchResult("US87654321", 0.82, "Container Opener", "application", "", "snippet", "")
            ],
            "claims": [
                SearchResult("US12345678", 0.88, "Mechanical Device Claims", "grant", "", "snippet", "")
            ]
        }
        
        async def mock_search_side_effect(request):
            # Return different results based on query content
            query = request.query.lower()
            if "simple mechanical device" in query:
                return (mock_results["title"], {"search_time": 0.3})
            elif "bottles with improved ergonomics" in query:
                return (mock_results["abstract"], {"search_time": 0.4})
            elif "mechanical device comprising" in query:
                return (mock_results["claims"], {"search_time": 0.2})
            else:
                return ([], {"search_time": 0.1})
        
        with patch.object(self.analyzer, '_run_search_async', side_effect=mock_search_side_effect):
            results = await self.analyzer.analyze_all_sections(
                draft_text,
                search_mode='hybrid',
                top_k=2,
                include_snippets=True
            )
            
            # Check results
            assert len(results) > 0
            
            # Check title section
            if "title" in results:
                title_result = results["title"]
                assert title_result.section_name == "title"
                assert title_result.patent_count == 2
                assert title_result.top_similarity_score == 0.85
                assert title_result.analysis_time > 0
                assert len(title_result.similar_patents) == 2
            
            # Check abstract section
            if "abstract" in results:
                abstract_result = results["abstract"]
                assert abstract_result.section_name == "abstract"
                assert abstract_result.patent_count == 2
                assert abstract_result.top_similarity_score == 0.90
            
            # Check claims section
            if "claims" in results:
                claims_result = results["claims"]
                assert claims_result.section_name == "claims"
                assert claims_result.patent_count == 1
                assert claims_result.top_similarity_score == 0.88
    
    @pytest.mark.asyncio
    async def test_analyze_section_with_timing(self):
        """Test section analysis with timing."""
        section_name = "title"
        section_text = "Simple Mechanical Device"
        
        # Mock search results
        mock_search_results = [
            SearchResult("US12345678", 0.85, "Test Patent", "grant", "", "snippet", "")
        ]
        
        with patch.object(self.analyzer, '_run_search_async') as mock_search:
            mock_search.return_value = (mock_search_results, {"search_time": 0.3})
            
            result = await self.analyzer._analyze_section_with_timing(
                section_name,
                section_text,
                'hybrid',
                1,
                True
            )
            
            # Check result structure
            assert isinstance(result, SectionSimilarityResult)
            assert result.section_name == section_name
            assert result.section_text == section_text
            assert result.patent_count == 1
            assert result.top_similarity_score == 0.85
            assert result.analysis_time > 0
            assert len(result.similar_patents) == 1
    
    def test_get_section_similarity_map_dict_input(self):
        """Test get_section_similarity_map with dict input."""
        # Create mock draft dict
        mock_draft = {
            "section_similarities": {
                "title": {
                    "section_name": "title",
                    "similar_patents": [
                        {"patent_id": "US12345678", "title": "Test Patent", "similarity_score": 0.85}
                    ],
                    "analysis_time": 0.5,
                    "patent_count": 1,
                    "top_similarity_score": 0.85
                },
                "abstract": {
                    "section_name": "abstract",
                    "similar_patents": [],
                    "analysis_time": 0.3,
                    "patent_count": 0,
                    "top_similarity_score": 0.0
                }
            }
        }
        
        similarity_map = get_section_similarity_map(mock_draft)
        
        # Check structure
        assert "title" in similarity_map
        assert "abstract" in similarity_map
        
        # Check title section
        title_data = similarity_map["title"]
        assert title_data["section_name"] == "title"
        assert title_data["patent_count"] == 1
        assert title_data["analysis_time"] == 0.5
        assert title_data["top_similarity_score"] == 0.85
        assert len(title_data["similar_patents"]) == 1
        
        # Check abstract section
        abstract_data = similarity_map["abstract"]
        assert abstract_data["patent_count"] == 0
        assert abstract_data["top_similarity_score"] == 0.0
    
    def test_get_section_similarity_map_object_input(self):
        """Test get_section_similarity_map with object input."""
        # Create mock objects
        class MockSimilarity:
            def __init__(self, section_name, similar_patents, analysis_time, patent_count, top_similarity_score):
                self.section_name = section_name
                self.similar_patents = similar_patents
                self.analysis_time = analysis_time
                self.patent_count = patent_count
                self.top_similarity_score = top_similarity_score
        
        mock_draft = {
            "section_similarities": {
                "title": MockSimilarity(
                    section_name="title",
                    similar_patents=[{"patent_id": "US12345678", "title": "Test Patent", "similarity_score": 0.85}],
                    analysis_time=0.5,
                    patent_count=1,
                    top_similarity_score=0.85
                )
            }
        }
        
        similarity_map = get_section_similarity_map(mock_draft)
        
        # Check structure
        assert "title" in similarity_map
        title_data = similarity_map["title"]
        assert title_data["section_name"] == "title"
        assert title_data["patent_count"] == 1
        assert title_data["analysis_time"] == 0.5
    
    def test_get_section_similarity_map_invalid_input(self):
        """Test get_section_similarity_map with invalid input."""
        # Test with non-dict input
        result = get_section_similarity_map("invalid")
        assert result == {}
        
        # Test with dict without section_similarities
        result = get_section_similarity_map({"other_key": "value"})
        assert result == {}
        
        # Test with empty dict
        result = get_section_similarity_map({})
        assert result == {}


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_analyze_draft_sections_function(self):
        """Test the analyze_draft_sections convenience function."""
        draft_text = """TITLE OF THE INVENTION
Test Patent

CLAIMS
1. A test claim."""
        
        # Mock search results
        mock_search_results = [
            SearchResult("US12345678", 0.85, "Test Patent", "grant", "", "snippet", "")
        ]
        
        with patch('section_similarity_analyzer.run_search') as mock_run_search:
            mock_run_search.return_value = (mock_search_results, {"search_time": 0.3})
            
            results = await analyze_draft_sections(
                draft_text,
                search_mode='hybrid',
                top_k=1,
                include_snippets=True
            )
            
            # Check that we got results
            assert len(results) > 0
            
            # Check that title section was analyzed
            if "title" in results:
                title_result = results["title"]
                assert title_result.section_name == "title"
                assert title_result.patent_count == 1
                assert title_result.top_similarity_score == 0.85


class TestIntegrationWithMockData:
    """Integration tests with mock LLM outputs and patent database."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SectionSimilarityAnalyzer()
        
        # Comprehensive mock LLM output
        self.comprehensive_draft = """TITLE OF THE INVENTION
Advanced Neural Network System for Medical Image Analysis

ABSTRACT
A comprehensive neural network system for analyzing medical images using convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

FIELD OF THE INVENTION
This invention relates to medical image analysis systems and methods for detecting anomalies in X-ray scans using artificial intelligence and machine learning.

BACKGROUND OF THE INVENTION
Traditional medical image analysis relies on manual inspection by radiologists, which is time-consuming, prone to human error, and inconsistent. There is a critical need for automated systems that can accurately detect anomalies in medical images with high precision and recall.

SUMMARY OF THE INVENTION
The present invention provides a neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed compared to existing methods.

BRIEF DESCRIPTION OF THE DRAWINGS
Figure 1 shows the overall system architecture.
Figure 2 illustrates the convolutional neural network structure.
Figure 3 demonstrates the anomaly detection process.

DETAILED DESCRIPTION OF THE INVENTION
The system comprises a convolutional neural network with multiple layers designed to process X-ray images and identify potential anomalies. The network includes preprocessing modules, feature extraction layers, and classification modules.

CLAIMS
1. A medical image analysis system comprising:
   a) A convolutional neural network with multiple layers;
   b) An input module for receiving X-ray images;
   c) An output module for generating anomaly detection results.

2. The system of claim 1, wherein the neural network includes at least three convolutional layers.

3. The system of claim 1, further comprising a preprocessing module for image normalization."""
        
        # Mock patent database with different similarity scores
        self.mock_patents = [
            {
                "patent_id": "US11111111",
                "title": "Medical Image Analysis Using Neural Networks",
                "similarity_score": 0.95
            },
            {
                "patent_id": "US22222222",
                "title": "Convolutional Neural Network for X-ray Analysis",
                "similarity_score": 0.88
            },
            {
                "patent_id": "US33333333",
                "title": "Anomaly Detection in Medical Images",
                "similarity_score": 0.82
            },
            {
                "patent_id": "US44444444",
                "title": "Deep Learning for Medical Diagnosis",
                "similarity_score": 0.75
            }
        ]
    
    @pytest.mark.asyncio
    async def test_comprehensive_section_analysis(self):
        """Test comprehensive analysis of all sections."""
        # Mock search results for different sections
        def mock_search_side_effect(request):
            query = request.query.lower()
            
            if "advanced neural network system" in query:
                # Title section - highest similarity
                results = [
                    SearchResult("US11111111", 0.95, "Medical Image Analysis Using Neural Networks", "grant", "", "snippet", ""),
                    SearchResult("US22222222", 0.88, "Convolutional Neural Network for X-ray Analysis", "grant", "", "snippet", "")
                ]
            elif "comprehensive neural network system" in query:
                # Abstract section
                results = [
                    SearchResult("US11111111", 0.90, "Medical Image Analysis Using Neural Networks", "grant", "", "snippet", ""),
                    SearchResult("US33333333", 0.82, "Anomaly Detection in Medical Images", "grant", "", "snippet", "")
                ]
            elif "medical image analysis systems" in query:
                # Field section
                results = [
                    SearchResult("US44444444", 0.75, "Deep Learning for Medical Diagnosis", "grant", "", "snippet", "")
                ]
            elif "manual inspection by radiologists" in query:
                # Background section
                results = [
                    SearchResult("US33333333", 0.80, "Anomaly Detection in Medical Images", "grant", "", "snippet", "")
                ]
            elif "convolutional neural network with multiple layers" in query:
                # Claims section
                results = [
                    SearchResult("US22222222", 0.92, "Convolutional Neural Network for X-ray Analysis", "grant", "", "snippet", ""),
                    SearchResult("US11111111", 0.85, "Medical Image Analysis Using Neural Networks", "grant", "", "snippet", "")
                ]
            else:
                results = []
            
            return (results, {"search_time": 0.3})
        
        with patch.object(self.analyzer, '_run_search_async', side_effect=mock_search_side_effect):
            results = await self.analyzer.analyze_all_sections(
                self.comprehensive_draft,
                search_mode='hybrid',
                top_k=2,
                include_snippets=True
            )
            
            # Check that we got results for multiple sections
            assert len(results) >= 5  # Should have at least 5 sections
            
            # Check title section
            if "title" in results:
                title_result = results["title"]
                assert title_result.patent_count == 2
                assert title_result.top_similarity_score == 0.95
                assert title_result.similar_patents[0]["patent_id"] == "US11111111"
            
            # Check abstract section
            if "abstract" in results:
                abstract_result = results["abstract"]
                assert abstract_result.patent_count == 2
                assert abstract_result.top_similarity_score == 0.90
            
            # Check claims section
            if "claims" in results:
                claims_result = results["claims"]
                assert claims_result.patent_count == 2
                assert claims_result.top_similarity_score == 0.92
                assert claims_result.similar_patents[0]["patent_id"] == "US22222222"
            
            # Test utility function
            draft_dict = {"section_similarities": results}
            similarity_map = get_section_similarity_map(draft_dict)
            
            assert len(similarity_map) >= 5
            assert "title" in similarity_map
            assert "abstract" in similarity_map
            assert "claims" in similarity_map
            
            # Check that similarity scores are properly ranked
            for section_name, data in similarity_map.items():
                if data["patent_count"] > 1:
                    patents = data["similar_patents"]
                    for i in range(len(patents) - 1):
                        assert patents[i]["similarity_score"] >= patents[i + 1]["similarity_score"], \
                            f"Patents in {section_name} should be ranked by similarity score"


if __name__ == "__main__":
    # Run basic tests
    print("Running section similarity tests...")
    
    async def run_tests():
        analyzer = SectionSimilarityAnalyzer()
        
        # Test 1: Section parsing
        print("Test 1: Section parsing")
        sample_draft = """TITLE OF THE INVENTION
Test Patent

CLAIMS
1. A test claim."""
        
        sections = analyzer.parse_draft_sections(sample_draft)
        print(f"Parsed sections: {list(sections.keys())}")
        print(f"Title: {sections['title']}")
        
        # Test 2: Mock similarity analysis
        print("\nTest 2: Mock similarity analysis")
        
        # This would require mocking the search service
        print("Mock similarity analysis test would require search service mocking")
        
        print("\nSection similarity tests completed!")
    
    asyncio.run(run_tests())
