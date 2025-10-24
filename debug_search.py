#!/usr/bin/env python3
"""
Debug script to check if the search is working.
"""

import requests
import json

def test_search():
    """Test the basic search functionality."""
    
    # Test basic search
    search_data = {
        'query': 'neural network medical image analysis',
        'mode': 'semantic',
        'top_k': 3,
        'include_snippets': True,
        'include_metadata': True
    }
    
    try:
        print("Testing basic search...")
        response = requests.post('http://localhost:8000/api/v1/search', json=search_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search successful!")
            print(f"📊 Results count: {len(result.get('results', []))}")
            
            if result.get('results'):
                print("🔍 First result:")
                first_result = result['results'][0]
                print(f"  - Title: {first_result.get('title', 'No title')}")
                print(f"  - Score: {first_result.get('score', 0):.3f}")
                print(f"  - Doc ID: {first_result.get('doc_id', 'No ID')}")
            else:
                print("❌ No search results found")
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_draft_generation():
    """Test draft generation without similarity."""
    
    draft_data = {
        'description': 'A neural network system for analyzing medical images using quantum computing principles',
        'model': 'llama3.2:3b',
        'template_type': 'utility',
        'max_length': 2000
    }
    
    try:
        print("\nTesting draft generation...")
        response = requests.post('http://localhost:8000/api/v1/generate_draft', json=draft_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Draft generation successful!")
            print(f"📝 Draft length: {len(result.get('draft', ''))}")
            
            # Check if draft has claims
            draft = result.get('draft', '')
            if 'Claim' in draft:
                print("✅ Draft contains claims section")
            else:
                print("❌ Draft does not contain claims section")
                print("📝 Draft preview:")
                print(draft[:200] + "...")
        else:
            print(f"❌ Draft generation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_search()
    test_draft_generation()


