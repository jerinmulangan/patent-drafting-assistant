#!/usr/bin/env python3
"""
Schema validation utility for the unified response format.
Provides validation functions for API and frontend use.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not available. Install with: pip install jsonschema")


class SchemaValidator:
    """Schema validator for the unified response format."""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self.validators = {}
        
        if JSONSCHEMA_AVAILABLE:
            self._load_schemas()
        else:
            print("Warning: Schema validation disabled - jsonschema not available")
    
    def _load_schemas(self):
        """Load all JSON schemas."""
        schema_files = {
            "draft_with_similarity": "draft_with_similarity.json",
            "section_similarity": "section_similarity.json",
            "api_request": "api_request.json"
        }
        
        for schema_name, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schemas[schema_name] = json.load(f)
                    self.validators[schema_name] = Draft7Validator(self.schemas[schema_name])
            else:
                print(f"Warning: Schema file {filename} not found")
    
    def validate_draft_response(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate draft response data against schema.
        
        Args:
            data: Draft response data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, []
        
        if "draft_with_similarity" not in self.validators:
            return False, ["Schema not available"]
        
        try:
            validate(instance=data, schema=self.schemas["draft_with_similarity"])
            return True, []
        except ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def validate_section_similarity(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate section similarity data against schema.
        
        Args:
            data: Section similarity data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, []
        
        if "section_similarity" not in self.validators:
            return False, ["Schema not available"]
        
        try:
            validate(instance=data, schema=self.schemas["section_similarity"])
            return True, []
        except ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def validate_api_request(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate API request data against schema.
        
        Args:
            data: API request data to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, []
        
        if "api_request" not in self.validators:
            return False, ["Schema not available"]
        
        try:
            validate(instance=data, schema=self.schemas["api_request"])
            return True, []
        except ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    def validate_json_string(self, json_str: str, schema_type: str = "draft_with_similarity") -> Tuple[bool, List[str]]:
        """
        Validate JSON string against schema.
        
        Args:
            json_str: JSON string to validate
            schema_type: Type of schema to use for validation
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {str(e)}"]
        
        if schema_type == "draft_with_similarity":
            return self.validate_draft_response(data)
        elif schema_type == "section_similarity":
            return self.validate_section_similarity(data)
        elif schema_type == "api_request":
            return self.validate_api_request(data)
        else:
            return False, [f"Unknown schema type: {schema_type}"]
    
    def get_schema_errors(self, data: Dict[str, Any], schema_type: str = "draft_with_similarity") -> List[str]:
        """
        Get detailed schema validation errors.
        
        Args:
            data: Data to validate
            schema_type: Type of schema to use
            
        Returns:
            List of detailed error messages
        """
        if not JSONSCHEMA_AVAILABLE:
            return []
        
        if schema_type not in self.validators:
            return [f"Schema {schema_type} not available"]
        
        errors = []
        validator = self.validators[schema_type]
        
        for error in validator.iter_errors(data):
            path = " -> ".join(str(p) for p in error.absolute_path)
            errors.append(f"{path}: {error.message}")
        
        return errors
    
    def is_valid_draft_response(self, data: Dict[str, Any]) -> bool:
        """Check if data is a valid draft response."""
        is_valid, _ = self.validate_draft_response(data)
        return is_valid
    
    def is_valid_api_request(self, data: Dict[str, Any]) -> bool:
        """Check if data is a valid API request."""
        is_valid, _ = self.validate_api_request(data)
        return is_valid
    
    def create_valid_draft_response(self, 
                                  draft: str,
                                  model: str,
                                  template_type: str,
                                  generation_time: float,
                                  cached: bool = False,
                                  section_similarities: Optional[Dict[str, Any]] = None,
                                  total_analysis_time: Optional[float] = None,
                                  success: bool = True,
                                  message: str = "Success",
                                  metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a valid draft response with proper structure.
        
        Args:
            draft: Generated patent draft text
            model: Model used for generation
            template_type: Patent template type
            generation_time: Time taken to generate draft
            cached: Whether result was cached
            section_similarities: Section similarity data
            total_analysis_time: Total analysis time
            success: Whether operation succeeded
            message: Status message
            metadata: Additional metadata
            
        Returns:
            Valid draft response dictionary
        """
        if section_similarities is None:
            section_similarities = {}
        
        if total_analysis_time is None:
            total_analysis_time = generation_time
        
        if metadata is None:
            metadata = {
                "sections_analyzed": len([s for s in section_similarities.values() if s.get("similar_patents")]),
                "total_similar_patents": sum(len(s.get("similar_patents", [])) for s in section_similarities.values()),
                "search_mode": "hybrid",
                "top_k": 5,
                "include_snippets": True,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        
        response = {
            "draft": draft,
            "model": model,
            "template_type": template_type,
            "generation_time": generation_time,
            "cached": cached,
            "section_similarities": section_similarities,
            "total_analysis_time": total_analysis_time,
            "success": success,
            "message": message,
            "metadata": metadata
        }
        
        # Validate the created response
        is_valid, errors = self.validate_draft_response(response)
        if not is_valid:
            raise ValueError(f"Created response is invalid: {errors}")
        
        return response
    
    def get_schema_info(self, schema_type: str = "draft_with_similarity") -> Dict[str, Any]:
        """
        Get information about a schema.
        
        Args:
            schema_type: Type of schema
            
        Returns:
            Schema information dictionary
        """
        if schema_type not in self.schemas:
            return {"error": f"Schema {schema_type} not found"}
        
        schema = self.schemas[schema_type]
        return {
            "title": schema.get("title", ""),
            "description": schema.get("description", ""),
            "required_fields": schema.get("required", []),
            "properties": list(schema.get("properties", {}).keys()),
            "schema_version": schema.get("$schema", "")
        }


# Global validator instance
_validator = None

def get_schema_validator() -> SchemaValidator:
    """Get global schema validator instance."""
    global _validator
    if _validator is None:
        _validator = SchemaValidator()
    return _validator


def validate_draft_response(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Convenience function to validate draft response."""
    validator = get_schema_validator()
    return validator.validate_draft_response(data)


def validate_api_request(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Convenience function to validate API request."""
    validator = get_schema_validator()
    return validator.validate_api_request(data)


def is_valid_draft_response(data: Dict[str, Any]) -> bool:
    """Convenience function to check if data is valid draft response."""
    validator = get_schema_validator()
    return validator.is_valid_draft_response(data)


if __name__ == "__main__":
    # Test the schema validator
    print("Testing Schema Validator...")
    
    validator = SchemaValidator()
    
    # Test 1: Valid data
    print("\n1. Testing valid data:")
    valid_data = validator.create_valid_draft_response(
        draft="Test draft",
        model="llama3.2:3b",
        template_type="utility",
        generation_time=2.0
    )
    
    is_valid, errors = validator.validate_draft_response(valid_data)
    print(f"Valid data: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Test 2: Invalid data
    print("\n2. Testing invalid data:")
    invalid_data = valid_data.copy()
    invalid_data["generation_time"] = "not_a_number"
    
    is_valid, errors = validator.validate_draft_response(invalid_data)
    print(f"Invalid data: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Test 3: Schema info
    print("\n3. Schema information:")
    info = validator.get_schema_info("draft_with_similarity")
    print(f"Title: {info.get('title', 'N/A')}")
    print(f"Required fields: {info.get('required_fields', [])}")
    print(f"Properties: {len(info.get('properties', []))}")
    
    print("\nSchema validator test completed!")
