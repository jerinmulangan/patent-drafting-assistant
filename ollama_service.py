#!/usr/bin/env python3
"""
Ollama service for local patent draft generation.
Provides patent-specific prompt templates and model management.
"""

import time
import hashlib
from typing import Dict, Any, Optional, List, Generator
from functools import lru_cache
import json

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not available. Install with: pip install ollama")

class OllamaService:
    """Service for generating patent drafts using local Ollama models."""
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.client = ollama if OLLAMA_AVAILABLE else None
        self.available_models = {
            "llama3.2:1b": "Ultra-fast (1B parameters) - Best for quick drafts",
            "llama3.2:3b": "Fast (3B parameters) - Balanced speed/quality", 
            "mistral:7b": "Balanced (7B parameters) - Good quality",
            "codellama:7b": "Technical (7B parameters) - Best for technical content"
        }
        
    def is_available(self) -> bool:
        """Check if Ollama is available and running."""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            self.client.list()
            return True
        except Exception:
            return False
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models."""
        if not self.is_available():
            return {}
        try:
            models = self.client.list()
            if hasattr(models, 'models'):
                return {model.model: self.available_models.get(model.model, "Custom model") 
                       for model in models.models}
            else:
                return {}
        except Exception as e:
            print(f"Error getting available models: {e}")
            return {}
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Ensure model is available, download if needed."""
        if not self.is_available():
            return False
        try:
            models = self.client.list()
            if hasattr(models, 'models'):
                available_names = [model.model for model in models.models]
                if model_name not in available_names:
                    print(f"Downloading model {model_name}...")
                    self.client.pull(model_name)
                    print(f"Model {model_name} downloaded successfully")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error ensuring model availability: {e}")
            return False
    
    def _create_patent_prompt(self, description: str, template_type: str = "utility") -> str:
        """Create patent-specific prompt template."""
        
        templates = {
            "utility": """
You are a patent attorney drafting a utility patent application. Based on this invention description: "{description}"

Generate a complete patent application draft including:

1. TITLE OF THE INVENTION
   [Generate a clear, descriptive title]

2. FIELD OF THE INVENTION
   [Describe the technical field this invention relates to]

3. BACKGROUND OF THE INVENTION
   [Describe the problem this invention solves and prior art limitations]

4. SUMMARY OF THE INVENTION
   [Provide a clear summary of the invention and its advantages]

5. BRIEF DESCRIPTION OF THE DRAWINGS
   [Describe any figures/diagrams that would illustrate the invention]

6. DETAILED DESCRIPTION OF THE INVENTION
   [Provide detailed technical description of the invention]

7. CLAIMS
   [Generate at least 3 independent claims and 2-3 dependent claims]

Use formal patent language and proper structure. Be specific and technical.
""",
            "software": """
You are a patent attorney specializing in software patents. Based on this software invention: "{description}"

Generate a software patent application draft including:

1. TITLE OF THE INVENTION
2. FIELD OF THE INVENTION  
3. BACKGROUND OF THE INVENTION
4. SUMMARY OF THE INVENTION
5. BRIEF DESCRIPTION OF THE DRAWINGS
6. DETAILED DESCRIPTION OF THE INVENTION
7. CLAIMS

Focus on the technical implementation, algorithms, and system architecture. Avoid abstract ideas and focus on concrete technical solutions.
""",
            "medical": """
You are a patent attorney specializing in medical device patents. Based on this medical invention: "{description}"

Generate a medical device patent application draft including:

1. TITLE OF THE INVENTION
2. FIELD OF THE INVENTION
3. BACKGROUND OF THE INVENTION  
4. SUMMARY OF THE INVENTION
5. BRIEF DESCRIPTION OF THE DRAWINGS
6. DETAILED DESCRIPTION OF THE INVENTION
7. CLAIMS

Focus on medical applications, safety considerations, and regulatory compliance.
"""
        }
        
        template = templates.get(template_type, templates["utility"])
        return template.format(description=description)
    
    def validate_description(self, description: str) -> bool:
        """Validate invention description."""
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        if len(description.strip()) < 50:
            raise ValueError("Description too short (minimum 50 characters)")
        if len(description) > 5000:
            raise ValueError("Description too long (maximum 5000 characters)")
        return True
    
    @lru_cache(maxsize=100)
    def generate_cached_draft(self, description_hash: str, model_name: str, template_type: str) -> str:
        """Generate draft with caching to avoid regeneration."""
        # This is a placeholder - in practice, you'd need to store the description
        # and retrieve it from the hash, or implement a different caching strategy
        return self.generate_patent_draft("", model_name, template_type)
    
    def generate_patent_draft(self, description: str, model_name: str = None, 
                            template_type: str = "utility", use_cache: bool = True) -> Dict[str, Any]:
        """Generate patent draft using Ollama."""
        if not self.is_available():
            raise RuntimeError("Ollama is not available. Please install and start Ollama.")
        
        # Validate inputs
        self.validate_description(description)
        
        # Use provided model or default
        model = model_name or self.model_name
        
        # Ensure model is available
        if not self.ensure_model_available(model):
            raise RuntimeError(f"Model {model} is not available")
        
        # Check cache if enabled
        if use_cache:
            description_hash = hashlib.md5(description.encode()).hexdigest()
            try:
                cached_result = self.generate_cached_draft(description_hash, model, template_type)
                if cached_result:
                    return {
                        "draft": cached_result,
                        "model": model,
                        "template_type": template_type,
                        "cached": True,
                        "generation_time": 0.0
                    }
            except:
                pass  # Continue with generation if cache fails
        
        # Create prompt
        prompt = self._create_patent_prompt(description, template_type)
        
        # Generate draft
        start_time = time.time()
        try:
            response = self.client.generate(
                model=model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'repeat_penalty': 1.1
                }
            )
            generation_time = time.time() - start_time
            
            return {
                "draft": response['response'],
                "model": model,
                "template_type": template_type,
                "cached": False,
                "generation_time": generation_time
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate draft: {str(e)}")
    
    def generate_draft_stream(self, description: str, model_name: str = None, 
                           template_type: str = "utility") -> Generator[str, None, None]:
        """Generate draft with streaming for real-time updates."""
        if not self.is_available():
            raise RuntimeError("Ollama is not available")
        
        self.validate_description(description)
        model = model_name or self.model_name
        
        if not self.ensure_model_available(model):
            raise RuntimeError(f"Model {model} is not available")
        
        prompt = self._create_patent_prompt(description, template_type)
        
        try:
            for chunk in self.client.generate(
                model=model,
                prompt=prompt,
                stream=True,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'repeat_penalty': 1.1
                }
            ):
                yield chunk['response']
        except Exception as e:
            raise RuntimeError(f"Failed to generate streaming draft: {str(e)}")
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get information about a specific model."""
        model = model_name or self.model_name
        if not self.is_available():
            return {"error": "Ollama not available"}
        
        try:
            models = self.client.list()
            for model_info in models['models']:
                if model_info['name'] == model:
                    return {
                        "name": model_info['name'],
                        "size": model_info.get('size', 'Unknown'),
                        "modified_at": model_info.get('modified_at', 'Unknown'),
                        "description": self.available_models.get(model, "Custom model")
                    }
            return {"error": f"Model {model} not found"}
        except Exception as e:
            return {"error": str(e)}


# Global service instance
_ollama_service = None

def get_ollama_service() -> OllamaService:
    """Get global Ollama service instance."""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service


if __name__ == "__main__":
    # Test the service
    service = OllamaService()
    print(f"Ollama available: {service.is_available()}")
    print(f"Available models: {service.get_available_models()}")
    
    if service.is_available():
        # Test with a simple description
        test_description = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        try:
            result = service.generate_patent_draft(test_description)
            print(f"Generated draft length: {len(result['draft'])} characters")
            print(f"Generation time: {result['generation_time']:.2f} seconds")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("Ollama is not available. Please install and start Ollama.")
