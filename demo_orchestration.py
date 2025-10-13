#!/usr/bin/env python3
"""
Demonstration script for the async orchestration system.
Shows the new concurrent LLM generation and patent search functionality.
"""

import asyncio
import json
import time
from pathlib import Path

from async_orchestration import get_orchestration_service, generate_with_background_search


async def demo_basic_functionality():
    """Demonstrate basic orchestration functionality."""
    print("ASYNC ORCHESTRATION DEMO")
    
    # Sample invention descriptions
    inventions = [
        {
            "name": "Medical AI System",
            "description": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.",
            "template_type": "utility"
        },
        {
            "name": "Quantum Computing Software",
            "description": "A quantum machine learning algorithm that uses superconducting qubits to perform drug discovery calculations with error correction and fault tolerance mechanisms.",
            "template_type": "software"
        },
        {
            "name": "Medical Device",
            "description": "A non-invasive blood glucose monitoring device that uses optical sensors and machine learning to provide real-time glucose readings for diabetic patients.",
            "template_type": "medical"
        }
    ]
    
    service = get_orchestration_service()
    
    for i, invention in enumerate(inventions, 1):
        print(f"\nINVENTION {i}: {invention['name']}")
        print(f"Description: {invention['description'][:100]}")
        print(f"Template: {invention['template_type']}")
        
        # Generate draft with background search
        start_time = time.time()
        
        result = await service.generate_with_background_search(
            prompt=invention['description'],
            search_mode='hybrid',
            model_name='llama3.2:3b',
            template_type=invention['template_type'],
            top_k=5,
            include_snippets=True,
            use_cache=False
        )
        
        total_time = time.time() - start_time
        
        # Display results
        print(f"Success: {result.success}")
        print(f"Generation time: {result.generation_time:.2f}s")
        print(f"Total analysis time: {result.total_analysis_time:.2f}s")
        print(f"Draft length: {len(result.draft)} characters")
        print(f"Sections analyzed: {len(result.section_similarities)}")
        
        # Show section analysis
        total_similar_patents = 0
        for section_name, similarity in result.section_similarities.items():
            if similarity.similar_patents:
                total_similar_patents += len(similarity.similar_patents)
                print(f"{section_name}: {len(similarity.similar_patents)} similar patents")
        
        print(f"Total similar patents found: {total_similar_patents}")
        
        # Show a sample of the draft
        print(f"\nDRAFT PREVIEW:")

        draft_preview = result.draft[:300] + "..." if len(result.draft) > 300 else result.draft
        print(draft_preview)

        
        # Show similar patents for the title section
        if 'title' in result.section_similarities and result.section_similarities['title'].similar_patents:
            print(f"\nSIMILAR PATENTS (Title Section):")
            for j, patent in enumerate(result.section_similarities['title'].similar_patents[:3], 1):
                print(f"  {j}. {patent['patent_id']} - {patent['title']}")
                print(f"     Similarity: {patent['similarity_score']:.3f}")
                if patent.get('snippet'):
                    snippet = patent['snippet'][:100] + "..." if len(patent['snippet']) > 100 else patent['snippet']
                    print(f"     Snippet: {snippet}")
                print()
        
        print(f"Total demo time for this invention: {total_time:.2f}s")


async def demo_concurrency_benefits():
    """Demonstrate concurrency benefits."""
    print("\nCONCURRENCY BENEFITS DEMO")
    
    service = get_orchestration_service()
    prompt = "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans."
    
    print("Testing concurrent vs sequential execution...")
    
    # Test concurrent execution
    print("\nConcurrent execution:")
    start_time = time.time()
    concurrent_result = await service.generate_with_background_search(
        prompt=prompt,
        search_mode='hybrid',
        top_k=5,
        use_cache=False
    )
    concurrent_time = time.time() - start_time
    
    print(f"Concurrent time: {concurrent_time:.2f}s")
    print(f"Draft generated: {len(concurrent_result.draft)} characters")
    print(f"Similar patents found: {sum(len(s.similar_patents) for s in concurrent_result.section_similarities.values())}")
    
    # Simulate sequential execution timing
    print("\nSimulated sequential execution:")
    
    # Measure draft generation only
    start_time = time.time()
    draft_result = await service._generate_draft_async(prompt, 'llama3.2:3b', 'utility', False)
    draft_time = time.time() - start_time
    
    # Measure search only
    start_time = time.time()
    search_results = await service._search_patents_async(prompt, 'hybrid', 5, True)
    search_time = time.time() - start_time
    
    sequential_time = draft_time + search_time
    concurrency_savings = sequential_time - concurrent_time
    
    print(f"Draft generation: {draft_time:.2f}s")
    print(f"Search execution: {search_time:.2f}s")
    print(f"Sequential total: {sequential_time:.2f}s")
    print(f"Concurrency savings: {concurrency_savings:.2f}s ({concurrency_savings/sequential_time*100:.1f}%)")


async def demo_json_schema():
    """Demonstrate JSON schema output."""
    print("\nJSON SCHEMA DEMO")

    
    service = get_orchestration_service()
    
    result = await service.generate_with_background_search(
        prompt="A simple mechanical device for opening bottles with improved ergonomics and safety features.",
        search_mode='hybrid',
        top_k=3,
        use_cache=False
    )
    
    # Convert to JSON schema
    json_result = service.to_json_schema(result)
    
    print("JSON Schema generated successfully")
    print(f"Schema size: {len(json.dumps(json_result))} characters")
    print(f"Sections: {list(json_result['section_similarities'].keys())}")
    print(f"Total similar patents: {sum(s['patent_count'] for s in json_result['section_similarities'].values())}")
    
    # Show schema structure
    print("\nSCHEMA STRUCTURE:")
    print(f"  draft: {len(json_result['draft'])} characters")
    print(f"  model: {json_result['model']}")
    print(f"  template_type: {json_result['template_type']}")
    print(f"  generation_time: {json_result['generation_time']:.2f}s")
    print(f"  total_analysis_time: {json_result['total_analysis_time']:.2f}s")
    print(f"  success: {json_result['success']}")
    print(f"  section_similarities: {len(json_result['section_similarities'])} sections")
    
    # Save to file for inspection
    output_file = Path("demo_orchestration_output.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull JSON saved to: {output_file}")
    print(f"File size: {output_file.stat().st_size} bytes")


async def demo_section_analysis():
    """Demonstrate section-level similarity analysis."""
    print("\nSECTION-LEVEL SIMILARITY ANALYSIS DEMO")

    
    service = get_orchestration_service()
    
    result = await service.generate_with_background_search(
        prompt="An advanced machine learning system for autonomous vehicle navigation using computer vision and deep neural networks.",
        search_mode='semantic',
        top_k=4,
        use_cache=False
    )
    
    print("Section analysis completed")
    print(f"Draft length: {len(result.draft)} characters")
    print(f"Sections analyzed: {len(result.section_similarities)}")
    
    print("\nSECTION ANALYSIS RESULTS:")
    
    for section_name, similarity in result.section_similarities.items():
        if similarity.section_text.strip():
            print(f"\n{section_name.upper()}:")
            print(f"   Text length: {len(similarity.section_text)} characters")
            print(f"   Analysis time: {similarity.analysis_time:.3f}s")
            print(f"   Similar patents: {len(similarity.similar_patents)}")
            
            if similarity.similar_patents:
                print(f"   Top similar patent:")
                top_patent = similarity.similar_patents[0]
                print(f"     ID: {top_patent['patent_id']}")
                print(f"     Title: {top_patent['title']}")
                print(f"     Similarity: {top_patent['similarity_score']:.3f}")
                
                if top_patent.get('snippet'):
                    snippet = top_patent['snippet'][:80] + "..." if len(top_patent['snippet']) > 80 else top_patent['snippet']
                    print(f"     Snippet: {snippet}")
        else:
            print(f"\n{section_name.upper()}: (empty)")


async def main():
    """Main demonstration function."""
    print("PATENT NLP PROJECT - ASYNC ORCHESTRATION DEMO")

    print("This demo showcases the new concurrent LLM generation and")
    print("patent search functionality with section-level similarity analysis.")
    try:
        # Demo 1: Basic functionality
        await demo_basic_functionality()
        
        # Demo 2: Concurrency benefits
        await demo_concurrency_benefits()
        
        # Demo 3: JSON schema
        await demo_json_schema()
        
        # Demo 4: Section analysis
        await demo_section_analysis()
        
        print("\nDEMO COMPLETED SUCCESSFULLY!")

        print("Key features demonstrated:")
        print("Concurrent LLM generation and patent search")
        print("Section-level similarity analysis")
        print("JSON schema validation")
        print("Performance benefits of async execution")
        print("Comprehensive error handling")

        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
