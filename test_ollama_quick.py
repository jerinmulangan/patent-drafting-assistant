#!/usr/bin/env python3
"""
Quick test of Ollama integration for patent draft generation.
"""

from ollama_service import OllamaService

def test_ollama_integration():
    """Test Ollama service integration."""
    print("Testing Ollama integration...")
    
    # Initialize service
    service = OllamaService()
    print(f"Ollama available: {service.is_available()}")
    print(f"Available models: {service.get_available_models()}")
    
    if service.is_available():
        # Test with a simple description
        test_description = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
        
        try:
            print("\nGenerating patent draft...")
            result = service.generate_patent_draft(
                description=test_description,
                model_name="llama3.2:3b",
                template_type="utility"
            )
            
            print(f"Generated draft length: {len(result['draft'])} characters")
            print(f"Generation time: {result['generation_time']:.2f} seconds")
            print(f"Model used: {result['model']}")
            print(f"Template type: {result['template_type']}")
            
            print("\nDraft preview:")
            print("-" * 50)
            print(result['draft'][:800] + "..." if len(result['draft']) > 800 else result['draft'])
            print("-" * 50)
            
        except Exception as e:
            print(f"Error generating draft: {e}")
    else:
        print("Ollama is not available")

if __name__ == "__main__":
    test_ollama_integration()





