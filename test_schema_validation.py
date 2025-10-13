#!/usr/bin/env python3
"""
Comprehensive schema validation tests.
Tests JSON schema validation for the unified response format.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not available. Install with: pip install jsonschema")


class TestSchemaValidation:
    """Test cases for JSON schema validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        if not JSONSCHEMA_AVAILABLE:
            pytest.skip("jsonschema not available")
        
        # Load schemas
        self.schemas_dir = Path("schemas")
        self.draft_schema = self._load_schema("draft_with_similarity.json")
        self.section_schema = self._load_schema("section_similarity.json")
        self.request_schema = self._load_schema("api_request.json")
        
        # Sample valid data
        self.valid_draft_response = self._create_valid_draft_response()
        self.valid_section_similarity = self._create_valid_section_similarity()
        self.valid_api_request = self._create_valid_api_request()
    
    def _load_schema(self, filename: str) -> Dict[str, Any]:
        """Load JSON schema from file."""
        schema_path = self.schemas_dir / filename
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_valid_draft_response(self) -> Dict[str, Any]:
        """Create a valid draft response for testing."""
        return {
            "draft": "TITLE OF THE INVENTION\nTest Patent\n\nCLAIMS\n1. A test claim.",
            "model": "llama3.2:3b",
            "template_type": "utility",
            "generation_time": 2.5,
            "cached": False,
            "section_similarities": {
                "title": {
                    "section_name": "title",
                    "section_text": "Test Patent",
                    "similar_patents": [
                        {
                            "patent_id": "US12345678",
                            "title": "Similar Patent Title",
                            "similarity_score": 0.85,
                            "doc_type": "grant",
                            "snippet": "A similar patent description...",
                            "source_file": "test_grant.xml",
                            "base_doc_id": "US12345678"
                        }
                    ],
                    "analysis_time": 0.5,
                    "patent_count": 1,
                    "top_similarity_score": 0.85
                },
                "claims": {
                    "section_name": "claims",
                    "section_text": "1. A test claim.",
                    "similar_patents": [],
                    "analysis_time": 0.3,
                    "patent_count": 0,
                    "top_similarity_score": 0.0
                }
            },
            "total_analysis_time": 3.0,
            "success": True,
            "message": "Draft generated and similarity analysis completed successfully",
            "metadata": {
                "sections_analyzed": 2,
                "total_similar_patents": 1,
                "search_mode": "hybrid",
                "top_k": 5,
                "include_snippets": True,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    
    def _create_valid_section_similarity(self) -> Dict[str, Any]:
        """Create a valid section similarity for testing."""
        return {
            "section_name": "title",
            "section_text": "Test Patent Title",
            "similar_patents": [
                {
                    "patent_id": "US12345678",
                    "title": "Similar Patent",
                    "similarity_score": 0.85,
                    "doc_type": "grant",
                    "snippet": "Patent snippet...",
                    "source_file": "test.xml"
                }
            ],
            "analysis_time": 0.5,
            "patent_count": 1,
            "top_similarity_score": 0.85
        }
    
    def _create_valid_api_request(self) -> Dict[str, Any]:
        """Create a valid API request for testing."""
        return {
            "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
            "search_mode": "hybrid",
            "model": "llama3.2:3b",
            "template_type": "utility",
            "top_k": 5,
            "include_snippets": True,
            "use_cache": True
        }
    
    def test_valid_draft_response_schema(self):
        """Test that valid draft response passes schema validation."""
        validate(instance=self.valid_draft_response, schema=self.draft_schema)
        assert True  # If no exception is raised, validation passed
    
    def test_valid_section_similarity_schema(self):
        """Test that valid section similarity passes schema validation."""
        validate(instance=self.valid_section_similarity, schema=self.section_schema)
        assert True
    
    def test_valid_api_request_schema(self):
        """Test that valid API request passes schema validation."""
        validate(instance=self.valid_api_request, schema=self.request_schema)
        assert True
    
    def test_draft_response_missing_required_fields(self):
        """Test that missing required fields fail validation."""
        # Test missing draft field
        invalid_response = self.valid_draft_response.copy()
        del invalid_response["draft"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "draft" in str(exc_info.value)
        
        # Test missing model field
        invalid_response = self.valid_draft_response.copy()
        del invalid_response["model"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "model" in str(exc_info.value)
    
    def test_draft_response_invalid_field_types(self):
        """Test that invalid field types fail validation."""
        # Test invalid generation_time type
        invalid_response = self.valid_draft_response.copy()
        invalid_response["generation_time"] = "not_a_number"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "generation_time" in str(exc_info.value)
        
        # Test invalid template_type enum
        invalid_response = self.valid_draft_response.copy()
        invalid_response["template_type"] = "invalid_type"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "template_type" in str(exc_info.value)
    
    def test_draft_response_invalid_similarity_scores(self):
        """Test that invalid similarity scores fail validation."""
        invalid_response = self.valid_draft_response.copy()
        invalid_response["section_similarities"]["title"]["similar_patents"][0]["similarity_score"] = 1.5
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "similarity_score" in str(exc_info.value)
    
    def test_draft_response_invalid_negative_times(self):
        """Test that negative times fail validation."""
        invalid_response = self.valid_draft_response.copy()
        invalid_response["generation_time"] = -1.0
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "generation_time" in str(exc_info.value)
    
    def test_draft_response_empty_strings(self):
        """Test that empty strings fail validation where minLength is specified."""
        invalid_response = self.valid_draft_response.copy()
        invalid_response["draft"] = ""
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "draft" in str(exc_info.value)
    
    def test_draft_response_invalid_metadata(self):
        """Test that invalid metadata fails validation."""
        invalid_response = self.valid_draft_response.copy()
        invalid_response["metadata"]["top_k"] = 25  # Exceeds maximum
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "top_k" in str(exc_info.value)
    
    def test_api_request_invalid_description_length(self):
        """Test that invalid description length fails validation."""
        # Too short
        invalid_request = self.valid_api_request.copy()
        invalid_request["description"] = "short"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "description" in str(exc_info.value)
        
        # Too long
        invalid_request = self.valid_api_request.copy()
        invalid_request["description"] = "x" * 5001
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "description" in str(exc_info.value)
    
    def test_api_request_invalid_enum_values(self):
        """Test that invalid enum values fail validation."""
        # Invalid search_mode
        invalid_request = self.valid_api_request.copy()
        invalid_request["search_mode"] = "invalid_mode"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "search_mode" in str(exc_info.value)
        
        # Invalid model
        invalid_request = self.valid_api_request.copy()
        invalid_request["model"] = "invalid_model"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "model" in str(exc_info.value)
    
    def test_api_request_invalid_top_k_range(self):
        """Test that invalid top_k range fails validation."""
        # Too low
        invalid_request = self.valid_api_request.copy()
        invalid_request["top_k"] = 0
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "top_k" in str(exc_info.value)
        
        # Too high
        invalid_request = self.valid_api_request.copy()
        invalid_request["top_k"] = 25
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_request, schema=self.request_schema)
        assert "top_k" in str(exc_info.value)
    
    def test_section_similarity_invalid_patent_count(self):
        """Test that invalid patent count fails validation."""
        invalid_section = self.valid_section_similarity.copy()
        invalid_section["patent_count"] = -1
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_section, schema=self.section_schema)
        assert "patent_count" in str(exc_info.value)
    
    def test_section_similarity_missing_required_patent_fields(self):
        """Test that missing required patent fields fail validation."""
        invalid_section = self.valid_section_similarity.copy()
        del invalid_section["similar_patents"][0]["patent_id"]
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_section, schema=self.section_schema)
        assert "patent_id" in str(exc_info.value)
    
    def test_additional_properties_rejected(self):
        """Test that additional properties are rejected."""
        invalid_response = self.valid_draft_response.copy()
        invalid_response["extra_field"] = "should_not_be_here"
        
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=invalid_response, schema=self.draft_schema)
        assert "extra_field" in str(exc_info.value)
    
    def test_schema_consistency_across_implementations(self):
        """Test that schemas are consistent with actual implementations."""
        # Test that the schema matches what the async orchestration service produces
        from async_orchestration import DraftWithSimilarity, SectionSimilarity
        
        # Create a mock result
        section_similarity = SectionSimilarity(
            section_name="title",
            section_text="Test Title",
            similar_patents=[{
                "patent_id": "US12345678",
                "title": "Test Patent",
                "similarity_score": 0.85,
                "doc_type": "grant",
                "snippet": "Test snippet",
                "source_file": "test.xml"
            }],
            analysis_time=0.5
        )
        
        draft_result = DraftWithSimilarity(
            draft="Test draft",
            model="llama3.2:3b",
            template_type="utility",
            generation_time=2.0,
            cached=False,
            section_similarities={"title": section_similarity},
            total_analysis_time=2.5,
            success=True,
            message="Success"
        )
        
        # Convert to JSON schema format
        from async_orchestration import get_orchestration_service
        service = get_orchestration_service()
        json_result = service.to_json_schema(draft_result)
        
        # Validate against schema
        validate(instance=json_result, schema=self.draft_schema)
        assert True
    
    def test_real_world_data_validation(self):
        """Test validation with real-world-like data."""
        # Create a comprehensive real-world example
        real_world_response = {
            "draft": """TITLE OF THE INVENTION
Advanced Neural Network System for Medical Image Analysis

ABSTRACT
A comprehensive neural network system for analyzing medical images using convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

FIELD OF THE INVENTION
This invention relates to medical image analysis systems and methods for detecting anomalies in X-ray scans using artificial intelligence and machine learning.

BACKGROUND OF THE INVENTION
Traditional medical image analysis relies on manual inspection by radiologists, which is time-consuming, prone to human error, and inconsistent.

SUMMARY OF THE INVENTION
The present invention provides a neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

CLAIMS
1. A medical image analysis system comprising:
   a) A convolutional neural network with multiple layers;
   b) An input module for receiving X-ray images;
   c) An output module for generating anomaly detection results.""",
            "model": "llama3.2:3b",
            "template_type": "utility",
            "generation_time": 3.2,
            "cached": False,
            "section_similarities": {
                "title": {
                    "section_name": "title",
                    "section_text": "Advanced Neural Network System for Medical Image Analysis",
                    "similar_patents": [
                        {
                            "patent_id": "US11111111",
                            "title": "Medical Image Analysis Using Neural Networks",
                            "similarity_score": 0.92,
                            "doc_type": "grant",
                            "snippet": "A system for analyzing medical images using neural networks...",
                            "source_file": "grant_11111111.xml",
                            "base_doc_id": "US11111111"
                        },
                        {
                            "patent_id": "US22222222",
                            "title": "Convolutional Neural Network for X-ray Analysis",
                            "similarity_score": 0.88,
                            "doc_type": "application",
                            "snippet": "Convolutional neural networks for detecting anomalies...",
                            "source_file": "app_22222222.xml",
                            "base_doc_id": "US22222222"
                        }
                    ],
                    "analysis_time": 0.8,
                    "patent_count": 2,
                    "top_similarity_score": 0.92
                },
                "abstract": {
                    "section_name": "abstract",
                    "section_text": "A comprehensive neural network system for analyzing medical images using convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.",
                    "similar_patents": [
                        {
                            "patent_id": "US33333333",
                            "title": "Deep Learning for Medical Image Analysis",
                            "similarity_score": 0.95,
                            "doc_type": "grant",
                            "snippet": "Deep learning methods for medical image analysis...",
                            "source_file": "grant_33333333.xml",
                            "base_doc_id": "US33333333"
                        }
                    ],
                    "analysis_time": 0.6,
                    "patent_count": 1,
                    "top_similarity_score": 0.95
                },
                "claims": {
                    "section_name": "claims",
                    "section_text": "1. A medical image analysis system comprising:\n   a) A convolutional neural network with multiple layers;\n   b) An input module for receiving X-ray images;\n   c) An output module for generating anomaly detection results.",
                    "similar_patents": [
                        {
                            "patent_id": "US44444444",
                            "title": "Neural Network Medical Device System",
                            "similarity_score": 0.87,
                            "doc_type": "grant",
                            "snippet": "A medical device system using neural networks...",
                            "source_file": "grant_44444444.xml",
                            "base_doc_id": "US44444444"
                        }
                    ],
                    "analysis_time": 0.7,
                    "patent_count": 1,
                    "top_similarity_score": 0.87
                }
            },
            "total_analysis_time": 4.5,
            "success": True,
            "message": "Draft generated and similarity analysis completed successfully",
            "metadata": {
                "sections_analyzed": 3,
                "total_similar_patents": 4,
                "search_mode": "hybrid",
                "top_k": 5,
                "include_snippets": True,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        }
        
        # Validate the real-world data
        validate(instance=real_world_response, schema=self.draft_schema)
        assert True


class TestSchemaCompatibility:
    """Test schema compatibility with different implementations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        if not JSONSCHEMA_AVAILABLE:
            pytest.skip("jsonschema not available")
        
        self.schemas_dir = Path("schemas")
        self.draft_schema = self._load_schema("draft_with_similarity.json")
    
    def _load_schema(self, filename: str) -> Dict[str, Any]:
        """Load JSON schema from file."""
        schema_path = self.schemas_dir / filename
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_api_endpoint_compatibility(self):
        """Test that API endpoint responses are compatible with schema."""
        # This would test actual API responses in a real scenario
        # For now, we'll test the expected structure
        expected_structure = {
            "draft": "string",
            "model": "string", 
            "template_type": "string",
            "generation_time": "number",
            "cached": "boolean",
            "section_similarities": "object",
            "total_analysis_time": "number",
            "success": "boolean",
            "message": "string"
        }
        
        # Verify all expected fields are in schema
        for field in expected_structure:
            assert field in self.draft_schema["properties"]
    
    def test_frontend_compatibility(self):
        """Test that schema is compatible with frontend expectations."""
        # Frontend typically expects these fields
        frontend_required_fields = [
            "draft", "model", "template_type", "generation_time", 
            "cached", "section_similarities", "total_analysis_time", 
            "success", "message"
        ]
        
        for field in frontend_required_fields:
            assert field in self.draft_schema["required"]
    
    def test_json_serialization_compatibility(self):
        """Test that schema supports JSON serialization."""
        # Test that the schema itself is valid JSON
        json_str = json.dumps(self.draft_schema)
        parsed_schema = json.loads(json_str)
        assert parsed_schema == self.draft_schema


if __name__ == "__main__":
    # Run basic validation tests
    print("Running schema validation tests...")
    
    if not JSONSCHEMA_AVAILABLE:
        print("Warning: jsonschema not available. Install with: pip install jsonschema")
        print("Skipping validation tests.")
        exit(0)
    
    # Test schema loading
    schemas_dir = Path("schemas")
    schema_files = ["draft_with_similarity.json", "section_similarity.json", "api_request.json"]
    
    for schema_file in schema_files:
        schema_path = schemas_dir / schema_file
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            print(f"{schema_file} loaded successfully")
            
            # Test that schema is valid JSON Schema
            try:
                jsonschema.Draft7Validator.check_schema(schema)
                print(f"{schema_file} is valid JSON Schema")
            except jsonschema.exceptions.SchemaError as e:
                print(f"{schema_file} has schema errors: {e}")
        else:
            print(f"{schema_file} not found")
    
    print("\nSchema validation tests completed!")
