#!/usr/bin/env python3
"""
Debug Ollama API response format.
"""

import ollama

def debug_ollama_response():
    """Debug the Ollama API response format."""
    try:
        print("Testing Ollama client...")
        client = ollama.Client()
        
        print("Getting models list...")
        models = client.list()
        print(f"Raw response: {models}")
        print(f"Type: {type(models)}")
        
        if hasattr(models, 'models'):
            print(f"models attribute: {models.models}")
        elif isinstance(models, dict):
            print(f"Dictionary keys: {models.keys()}")
            if 'models' in models:
                print(f"models key: {models['models']}")
        
        print("\nTesting model availability...")
        try:
            response = client.generate(
                model='llama3.2:3b',
                prompt='Hello, how are you?',
                stream=False
            )
            print(f"Model test successful: {response['response'][:100]}...")
        except Exception as e:
            print(f"Model test failed: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ollama_response()
