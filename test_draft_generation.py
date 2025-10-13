#!/usr/bin/env python3
"""
Test suite for patent draft generation using Ollama.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from ollama_service import OllamaService, get_ollama_service
from api_endpoints import DraftRequestModel, DraftResponseModel


class TestOllamaService:
    """Test cases for OllamaService."""
    
    def test_ollama_service_initialization(self):
        """Test OllamaService initialization."""
        service = OllamaService()
        assert service.model_name == "llama3.2:3b"
        assert service.available_models is not None
        assert len(service.available_models) > 0
    
    def test_validate_description_valid(self):
        """Test description validation with valid input."""
        service = OllamaService()
        valid_description = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        assert service.validate_description(valid_description) == True
    
    def test_validate_description_too_short(self):
        """Test description validation with too short input."""
        service = OllamaService()
        short_description = "Short"
        with pytest.raises(ValueError, match="Description too short"):
            service.validate_description(short_description)
    
    def test_validate_description_too_long(self):
        """Test description validation with too long input."""
        service = OllamaService()
        long_description = "A" * 5001
        with pytest.raises(ValueError, match="Description too long"):
            service.validate_description(long_description)
    
    def test_validate_description_empty(self):
        """Test description validation with empty input."""
        service = OllamaService()
        with pytest.raises(ValueError, match="Description cannot be empty"):
            service.validate_description("")
    
    def test_create_patent_prompt_utility(self):
        """Test patent prompt creation for utility patents."""
        service = OllamaService()
        description = "Test invention"
        prompt = service._create_patent_prompt(description, "utility")
        
        assert "TITLE OF THE INVENTION" in prompt
        assert "FIELD OF THE INVENTION" in prompt
        assert "CLAIMS" in prompt
        assert description in prompt
    
    def test_create_patent_prompt_software(self):
        """Test patent prompt creation for software patents."""
        service = OllamaService()
        description = "Test software invention"
        prompt = service._create_patent_prompt(description, "software")
        
        assert "software patents" in prompt.lower()
        assert "technical implementation" in prompt.lower()
        assert description in prompt
    
    def test_create_patent_prompt_medical(self):
        """Test patent prompt creation for medical patents."""
        service = OllamaService()
        description = "Test medical invention"
        prompt = service._create_patent_prompt(description, "medical")
        
        assert "medical device patents" in prompt.lower()
        assert "medical applications" in prompt.lower()
        assert description in prompt
    
    @patch('ollama_service.ollama')
    def test_generate_patent_draft_success(self, mock_ollama):
        """Test successful patent draft generation."""
        # Mock Ollama response
        mock_ollama.generate.return_value = {
            'response': 'TITLE OF THE INVENTION\nTest Patent\n\nFIELD OF THE INVENTION\nThis invention relates to...'
        }
        
        service = OllamaService()
        service.client = mock_ollama
        service.is_available = Mock(return_value=True)
        service.ensure_model_available = Mock(return_value=True)
        
        result = service.generate_patent_draft(
            "A neural network system for medical image analysis",
            "llama3.2:3b",
            "utility"
        )
        
        assert result["draft"] is not None
        assert result["model"] == "llama3.2:3b"
        assert result["template_type"] == "utility"
        assert result["generation_time"] > 0
        assert result["cached"] == False
    
    @patch('ollama_service.ollama')
    def test_generate_patent_draft_ollama_unavailable(self, mock_ollama):
        """Test patent draft generation when Ollama is unavailable."""
        service = OllamaService()
        service.is_available = Mock(return_value=False)
        
        with pytest.raises(RuntimeError, match="Ollama is not available"):
            service.generate_patent_draft("Test description")
    
    def test_get_available_models(self):
        """Test getting available models."""
        service = OllamaService()
        models = service.get_available_models()
        
        # Should return empty dict if Ollama not available
        assert isinstance(models, dict)


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_draft_request_model_validation(self):
        """Test DraftRequestModel validation."""
        # Valid request
        valid_request = DraftRequestModel(
            description="A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
            model="llama3.2:3b",
            template_type="utility",
            max_length=2000
        )
        assert valid_request.description is not None
        assert valid_request.model == "llama3.2:3b"
        assert valid_request.template_type == "utility"
        assert valid_request.max_length == 2000
    
    def test_draft_request_model_invalid_model(self):
        """Test DraftRequestModel with invalid model."""
        with pytest.raises(ValueError, match="Model must be one of"):
            DraftRequestModel(
                description="Test description that is long enough to pass validation",
                model="invalid-model"
            )
    
    def test_draft_request_model_invalid_template(self):
        """Test DraftRequestModel with invalid template type."""
        with pytest.raises(ValueError, match="Template type must be one of"):
            DraftRequestModel(
                description="Test description that is long enough to pass validation",
                template_type="invalid-template"
            )
    
    def test_draft_request_model_short_description(self):
        """Test DraftRequestModel with short description."""
        with pytest.raises(ValueError, match="Description too short"):
            DraftRequestModel(description="Short")
    
    def test_draft_request_model_long_description(self):
        """Test DraftRequestModel with long description."""
        with pytest.raises(ValueError, match="Description too long"):
            DraftRequestModel(description="A" * 5001)
    
    def test_draft_response_model(self):
        """Test DraftResponseModel creation."""
        response = DraftResponseModel(
            draft="Test patent draft content",
            model="llama3.2:3b",
            template_type="utility",
            generation_time=1.5,
            cached=False,
            success=True,
            message="Draft generated successfully"
        )
        
        assert response.draft == "Test patent draft content"
        assert response.model == "llama3.2:3b"
        assert response.template_type == "utility"
        assert response.generation_time == 1.5
        assert response.cached == False
        assert response.success == True
        assert response.message == "Draft generated successfully"


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_generate_draft_endpoint_success(self):
        """Test successful draft generation endpoint."""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Mock the Ollama service
        with patch('api_endpoints.get_ollama_service') as mock_service:
            mock_ollama_service = Mock()
            mock_ollama_service.is_available.return_value = True
            mock_ollama_service.generate_patent_draft.return_value = {
                "draft": "TITLE OF THE INVENTION\nTest Patent\n\nFIELD OF THE INVENTION\nThis invention relates to...",
                "model": "llama3.2:3b",
                "template_type": "utility",
                "generation_time": 1.5,
                "cached": False
            }
            mock_service.return_value = mock_ollama_service
            
            response = client.post("/api/v1/generate_draft", json={
                "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
                "model": "llama3.2:3b",
                "template_type": "utility",
                "max_length": 2000
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["draft"] is not None
            assert data["model"] == "llama3.2:3b"
            assert data["template_type"] == "utility"
            assert data["generation_time"] == 1.5
    
    @pytest.mark.asyncio
    async def test_generate_draft_endpoint_ollama_unavailable(self):
        """Test draft generation endpoint when Ollama is unavailable."""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Mock the Ollama service as unavailable
        with patch('api_endpoints.get_ollama_service') as mock_service:
            mock_ollama_service = Mock()
            mock_ollama_service.is_available.return_value = False
            mock_service.return_value = mock_ollama_service
            
            response = client.post("/api/v1/generate_draft", json={
                "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
                "model": "llama3.2:3b",
                "template_type": "utility"
            })
            
            assert response.status_code == 503
            data = response.json()
            assert "Ollama service is not available" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_ollama_health_endpoint(self):
        """Test Ollama health check endpoint."""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Mock the Ollama service
        with patch('api_endpoints.get_ollama_service') as mock_service:
            mock_ollama_service = Mock()
            mock_ollama_service.is_available.return_value = True
            mock_ollama_service.get_available_models.return_value = {
                "llama3.2:3b": "Fast (3B parameters)"
            }
            mock_ollama_service.model_name = "llama3.2:3b"
            mock_service.return_value = mock_ollama_service
            
            response = client.get("/api/v1/ollama/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "Ollama service is running" in data["message"]
            assert "llama3.2:3b" in data["available_models"]


def run_manual_tests():
    """Run manual tests that require actual Ollama installation."""
    print("Running manual tests...")
    
    # Test Ollama service availability
    service = OllamaService()
    print(f"Ollama available: {service.is_available()}")
    
    if service.is_available():
        print("Available models:", service.get_available_models())
        
        # Test with a simple description
        test_description = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        try:
            result = service.generate_patent_draft(test_description)
            print(f"Generated draft length: {len(result['draft'])} characters")
            print(f"Generation time: {result['generation_time']:.2f} seconds")
            print("Draft preview:", result['draft'][:200] + "...")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("Ollama is not available. Please install and start Ollama.")


if __name__ == "__main__":
    # Run manual tests
    run_manual_tests()
    
    # Run pytest tests
    print("\nRunning pytest tests...")
    pytest.main([__file__, "-v"])





