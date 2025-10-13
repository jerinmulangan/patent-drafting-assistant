#!/usr/bin/env python3
"""
API tests for async orchestration endpoints.
Tests the new generate_draft_with_similarity endpoint.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Import the main app and router
from main import app
from async_orchestration import DraftWithSimilarity, SectionSimilarity


class TestOrchestrationAPI:
    """Test cases for orchestration API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.sample_request = {
            "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
            "search_mode": "hybrid",
            "model": "llama3.2:3b",
            "template_type": "utility",
            "top_k": 5,
            "include_snippets": True,
            "use_cache": True
        }
        
        # Mock response data
        self.mock_section_similarity = SectionSimilarity(
            section_name="title",
            section_text="Medical Image Analysis System",
            similar_patents=[
                {
                    "patent_id": "US12345678",
                    "title": "Medical Image Analysis System",
                    "similarity_score": 0.85,
                    "doc_type": "grant",
                    "snippet": "A system for analyzing medical images...",
                    "source_file": "test_grant.xml"
                }
            ],
            analysis_time=0.5
        )
        
        self.mock_result = DraftWithSimilarity(
            draft="TITLE OF THE INVENTION\nMedical Image Analysis System\n\nFIELD OF THE INVENTION\nThis invention relates to medical image analysis...",
            model="llama3.2:3b",
            template_type="utility",
            generation_time=2.5,
            cached=False,
            section_similarities={"title": self.mock_section_similarity},
            total_analysis_time=3.0,
            success=True,
            message="Draft generated and similarity analysis completed successfully"
        )
    
    @patch('api_endpoints.get_orchestration_service')
    @patch('api_endpoints.get_ollama_service')
    def test_generate_draft_with_similarity_success(self, mock_get_ollama, mock_get_orchestration):
        """Test successful draft generation with similarity analysis."""
        # Setup mocks
        mock_ollama_service = Mock()
        mock_ollama_service.is_available.return_value = True
        mock_get_ollama.return_value = mock_ollama_service
        
        mock_orchestration_service = Mock()
        mock_orchestration_service.generate_with_background_search = AsyncMock(return_value=self.mock_result)
        mock_get_orchestration.return_value = mock_orchestration_service
        
        # Make request
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=self.sample_request)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["model"] == "llama3.2:3b"
        assert data["template_type"] == "utility"
        assert data["generation_time"] == 2.5
        assert data["cached"] is False
        assert data["total_analysis_time"] == 3.0
        assert "Medical Image Analysis System" in data["draft"]
        assert "title" in data["section_similarities"]
        assert data["section_similarities"]["title"]["patent_count"] == 1
        assert data["section_similarities"]["title"]["similar_patents"][0]["patent_id"] == "US12345678"
    
    @patch('api_endpoints.get_ollama_service')
    def test_generate_draft_with_similarity_ollama_unavailable(self, mock_get_ollama):
        """Test handling when Ollama service is unavailable."""
        # Setup mock
        mock_ollama_service = Mock()
        mock_ollama_service.is_available.return_value = False
        mock_get_ollama.return_value = mock_ollama_service
        
        # Make request
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=self.sample_request)
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert "Ollama service is not available" in data["detail"]
    
    def test_generate_draft_with_similarity_invalid_request(self):
        """Test handling of invalid request data."""
        # Test empty description
        invalid_request = self.sample_request.copy()
        invalid_request["description"] = ""
        
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422  # Validation error
        
        # Test short description
        invalid_request["description"] = "short"
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid search mode
        invalid_request = self.sample_request.copy()
        invalid_request["search_mode"] = "invalid_mode"
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid model
        invalid_request = self.sample_request.copy()
        invalid_request["model"] = "invalid_model"
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid template type
        invalid_request = self.sample_request.copy()
        invalid_request["template_type"] = "invalid_type"
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
        
        # Test invalid top_k
        invalid_request = self.sample_request.copy()
        invalid_request["top_k"] = 0
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
        
        invalid_request["top_k"] = 25  # Exceeds limit
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
        assert response.status_code == 422
    
    @patch('api_endpoints.get_orchestration_service')
    @patch('api_endpoints.get_ollama_service')
    def test_generate_draft_with_similarity_service_error(self, mock_get_ollama, mock_get_orchestration):
        """Test handling of service errors."""
        # Setup mocks
        mock_ollama_service = Mock()
        mock_ollama_service.is_available.return_value = True
        mock_get_ollama.return_value = mock_ollama_service
        
        mock_orchestration_service = Mock()
        mock_orchestration_service.generate_with_background_search = AsyncMock(
            side_effect=Exception("Service error")
        )
        mock_get_orchestration.return_value = mock_orchestration_service
        
        # Make request
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=self.sample_request)
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    def test_generate_draft_with_similarity_missing_fields(self):
        """Test handling of missing required fields."""
        # Test missing description
        incomplete_request = {
            "search_mode": "hybrid",
            "model": "llama3.2:3b"
        }
        
        response = self.client.post("/api/v1/generate_draft_with_similarity", json=incomplete_request)
        assert response.status_code == 422
    
    def test_generate_draft_with_similarity_default_values(self):
        """Test that default values are applied correctly."""
        # Request with minimal required fields
        minimal_request = {
            "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        }
        
        with patch('api_endpoints.get_orchestration_service') as mock_get_orchestration, \
             patch('api_endpoints.get_ollama_service') as mock_get_ollama:
            
            # Setup mocks
            mock_ollama_service = Mock()
            mock_ollama_service.is_available.return_value = True
            mock_get_ollama.return_value = mock_ollama_service
            
            mock_orchestration_service = Mock()
            mock_orchestration_service.generate_with_background_search = AsyncMock(return_value=self.mock_result)
            mock_get_orchestration.return_value = mock_orchestration_service
            
            # Make request
            response = self.client.post("/api/v1/generate_draft_with_similarity", json=minimal_request)
            
            # Assertions
            assert response.status_code == 200
            
            # Check that default values were used
            mock_orchestration_service.generate_with_background_search.assert_called_once()
            call_args = mock_orchestration_service.generate_with_background_search.call_args
            assert call_args[1]["search_mode"] == "hybrid"  # Default
            assert call_args[1]["model"] == "llama3.2:3b"  # Default
            assert call_args[1]["template_type"] == "utility"  # Default
            assert call_args[1]["top_k"] == 5  # Default
            assert call_args[1]["include_snippets"] is True  # Default
            assert call_args[1]["use_cache"] is True  # Default


class TestResponseSchema:
    """Test response schema validation."""
    
    @patch('api_endpoints.get_orchestration_service')
    @patch('api_endpoints.get_ollama_service')
    def test_response_schema_structure(self, mock_get_ollama, mock_get_orchestration):
        """Test that response follows the expected schema structure."""
        client = TestClient(app)
        
        # Setup mocks
        mock_ollama_service = Mock()
        mock_ollama_service.is_available.return_value = True
        mock_get_ollama.return_value = mock_ollama_service
        
        # Create comprehensive mock result
        section_similarities = {
            "title": SectionSimilarity(
                section_name="title",
                section_text="Test Title",
                similar_patents=[
                    {
                        "patent_id": "US12345678",
                        "title": "Test Patent",
                        "similarity_score": 0.85,
                        "doc_type": "grant",
                        "snippet": "Test snippet",
                        "source_file": "test.xml"
                    }
                ],
                analysis_time=0.5
            ),
            "claims": SectionSimilarity(
                section_name="claims",
                section_text="Test claims",
                similar_patents=[],
                analysis_time=0.3
            )
        }
        
        mock_result = DraftWithSimilarity(
            draft="Test draft content",
            model="llama3.2:3b",
            template_type="utility",
            generation_time=2.0,
            cached=False,
            section_similarities=section_similarities,
            total_analysis_time=2.5,
            success=True,
            message="Success"
        )
        
        mock_orchestration_service = Mock()
        mock_orchestration_service.generate_with_background_search = AsyncMock(return_value=mock_result)
        mock_get_orchestration.return_value = mock_orchestration_service
        
        # Make request
        request_data = {
            "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        }
        
        response = client.post("/api/v1/generate_draft_with_similarity", json=request_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "draft", "model", "template_type", "generation_time", "cached",
            "section_similarities", "total_analysis_time", "success", "message"
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(data["draft"], str)
        assert isinstance(data["model"], str)
        assert isinstance(data["template_type"], str)
        assert isinstance(data["generation_time"], (int, float))
        assert isinstance(data["cached"], bool)
        assert isinstance(data["section_similarities"], dict)
        assert isinstance(data["total_analysis_time"], (int, float))
        assert isinstance(data["success"], bool)
        assert isinstance(data["message"], str)
        
        # Check section similarities structure
        for section_name, section_data in data["section_similarities"].items():
            assert "section_name" in section_data
            assert "section_text" in section_data
            assert "similar_patents" in section_data
            assert "analysis_time" in section_data
            assert "patent_count" in section_data
            assert isinstance(section_data["similar_patents"], list)
            assert isinstance(section_data["patent_count"], int)
        
        # Check similar patents structure
        for patent in data["section_similarities"]["title"]["similar_patents"]:
            assert "patent_id" in patent
            assert "title" in patent
            assert "similarity_score" in patent
            assert "doc_type" in patent
            assert isinstance(patent["similarity_score"], (int, float))
            assert 0 <= patent["similarity_score"] <= 1


if __name__ == "__main__":
    # Run basic API tests
    print("Running orchestration API tests...")
    
    # Test the endpoint directly
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    
    # Test 1: Basic request validation
    print("Test 1: Request validation")
    
    # Valid request
    valid_request = {
        "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
    }
    
    response = client.post("/api/v1/generate_draft_with_similarity", json=valid_request)
    print(f"Valid request status: {response.status_code}")
    
    # Invalid request (empty description)
    invalid_request = {"description": ""}
    response = client.post("/api/v1/generate_draft_with_similarity", json=invalid_request)
    print(f"Invalid request status: {response.status_code}")
    
    # Test 2: Response schema validation
    print("\nTest 2: Response schema validation")
    
    # This would require mocking the services, but we can test the schema structure
    print("Schema validation tests would require service mocking")
    
    print("\nAPI tests completed!")
