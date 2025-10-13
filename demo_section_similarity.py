#!/usr/bin/env python3
"""
Demonstration script for per-section similarity analysis.
Shows how LLM output is split into structured sections and analyzed for similarity.
"""

import asyncio
import json
import time
from pathlib import Path

from section_similarity_analyzer import (
    SectionSimilarityAnalyzer, 
    get_section_similarity_map,
    analyze_draft_sections
)
from async_orchestration import get_orchestration_service


async def demo_section_parsing():
    """Demonstrate section parsing from LLM output."""
    print("SECTION PARSING DEMO")
    
    # Sample LLM outputs for different patent types
    llm_outputs = {
        "utility_patent": """TITLE OF THE INVENTION
Advanced Neural Network System for Medical Image Analysis

ABSTRACT
A comprehensive neural network system for analyzing medical images using convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

FIELD OF THE INVENTION
This invention relates to medical image analysis systems and methods for detecting anomalies in X-ray scans using artificial intelligence and machine learning.

BACKGROUND OF THE INVENTION
Traditional medical image analysis relies on manual inspection by radiologists, which is time-consuming, prone to human error, and inconsistent. There is a critical need for automated systems that can accurately detect anomalies in medical images.

SUMMARY OF THE INVENTION
The present invention provides a neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans with improved accuracy and speed.

BRIEF DESCRIPTION OF THE DRAWINGS
Figure 1 shows the overall system architecture.
Figure 2 illustrates the convolutional neural network structure.

DETAILED DESCRIPTION OF THE INVENTION
The system comprises a convolutional neural network with multiple layers designed to process X-ray images and identify potential anomalies. The network includes preprocessing modules, feature extraction layers, and classification modules.

CLAIMS
1. A medical image analysis system comprising:
   a) A convolutional neural network with multiple layers;
   b) An input module for receiving X-ray images;
   c) An output module for generating anomaly detection results.

2. The system of claim 1, wherein the neural network includes at least three convolutional layers.""",
        
        "software_patent": """TITLE OF THE INVENTION
Quantum Machine Learning Algorithm for Drug Discovery

ABSTRACT
A quantum machine learning algorithm that uses superconducting qubits to perform drug discovery calculations with error correction and fault tolerance mechanisms.

FIELD OF THE INVENTION
This invention relates to quantum computing and machine learning algorithms for pharmaceutical research and drug discovery applications.

BACKGROUND OF THE INVENTION
Current drug discovery methods are computationally expensive and time-consuming. Quantum computing offers potential speedups but requires new algorithmic approaches.

SUMMARY OF THE INVENTION
The present invention provides a quantum machine learning algorithm optimized for drug discovery with improved efficiency and accuracy.

CLAIMS
1. A quantum machine learning method comprising:
   a) Encoding molecular data into quantum states;
   b) Applying quantum gates for feature transformation;
   c) Measuring quantum states to obtain predictions."""
    }
    
    analyzer = SectionSimilarityAnalyzer()
    
    for patent_type, draft_text in llm_outputs.items():
        print(f"\n{patent_type.upper().replace('_', ' ')}:")
        
        # Parse sections
        sections = analyzer.parse_draft_sections(draft_text)
        
        print(f"Sections found: {len([s for s in sections.values() if s.strip()])}")
        for section_name, section_text in sections.items():
            if section_text.strip():
                print(f"  {section_name}: {len(section_text)} characters")
                # Show first 50 characters
                preview = section_text[:50] + "..." if len(section_text) > 50 else section_text
                print(f"    Preview: {preview}")
        
        print()


async def demo_per_section_similarity():
    """Demonstrate per-section similarity analysis."""
    print("\nPER-SECTION SIMILARITY ANALYSIS DEMO")
    
    # Sample draft with different content in each section
    sample_draft = """TITLE OF THE INVENTION
Advanced Machine Learning System for Autonomous Vehicles

ABSTRACT
A machine learning system using deep neural networks for autonomous vehicle navigation with computer vision and sensor fusion capabilities.

FIELD OF THE INVENTION
This invention relates to autonomous vehicle systems and machine learning algorithms for navigation and control.

BACKGROUND OF THE INVENTION
Current autonomous vehicle systems lack sufficient accuracy and reliability for safe operation in complex traffic scenarios.

SUMMARY OF THE INVENTION
The present invention provides an advanced machine learning system with improved accuracy and reliability for autonomous vehicle navigation.

CLAIMS
1. A machine learning system comprising:
   a) A convolutional neural network for image processing;
   b) A recurrent neural network for sequence modeling;
   c) A fusion module for combining sensor data."""
    
    analyzer = SectionSimilarityAnalyzer()
    
    print("Analyzing each section for similar patents...")
    print("(Note: This demo uses mock data - in production, this would search the actual patent database)")
    
    # Mock search results for demonstration
    mock_results = {
        "title": [
            {"patent_id": "US11111111", "title": "Machine Learning for Vehicle Control", "similarity_score": 0.92},
            {"patent_id": "US22222222", "title": "Autonomous Vehicle Navigation System", "similarity_score": 0.88}
        ],
        "abstract": [
            {"patent_id": "US33333333", "title": "Deep Learning for Autonomous Driving", "similarity_score": 0.95},
            {"patent_id": "US44444444", "title": "Neural Networks for Vehicle Navigation", "similarity_score": 0.87}
        ],
        "field": [
            {"patent_id": "US55555555", "title": "Autonomous Vehicle Control Systems", "similarity_score": 0.83}
        ],
        "background": [
            {"patent_id": "US66666666", "title": "Reliability in Autonomous Vehicles", "similarity_score": 0.79}
        ],
        "summary": [
            {"patent_id": "US77777777", "title": "Advanced Vehicle Navigation Methods", "similarity_score": 0.85}
        ],
        "claims": [
            {"patent_id": "US88888888", "title": "Neural Network Vehicle Control System", "similarity_score": 0.91},
            {"patent_id": "US99999999", "title": "Multi-Modal Sensor Fusion for Vehicles", "similarity_score": 0.86}
        ]
    }
    
    # Parse sections
    sections = analyzer.parse_draft_sections(sample_draft)
    
    print(f"\nSection Analysis Results:")
    
    total_similar_patents = 0
    for section_name, section_text in sections.items():
        if section_text.strip():
            # Simulate similarity analysis
            similar_patents = mock_results.get(section_name, [])
            total_similar_patents += len(similar_patents)
            
            print(f"\n{section_name.upper()}:")
            print(f"  Text length: {len(section_text)} characters")
            print(f"  Similar patents found: {len(similar_patents)}")
            
            if similar_patents:
                print(f"  Top similarity score: {similar_patents[0]['similarity_score']:.3f}")
                print(f"  Most similar patent: {similar_patents[0]['title']}")
                
                if len(similar_patents) > 1:
                    print(f"  Second most similar: {similar_patents[1]['title']} ({similar_patents[1]['similarity_score']:.3f})")
        else:
            print(f"\n{section_name.upper()}: (empty)")
    
    print(f"\nTotal similar patents found across all sections: {total_similar_patents}")


async def demo_utility_function():
    """Demonstrate the get_section_similarity_map utility function."""
    print("\nUTILITY FUNCTION DEMO")
    
    # Create mock draft result
    mock_draft_result = {
        "draft": "Sample patent draft text...",
        "model": "llama3.2:3b",
        "section_similarities": {
            "title": {
                "section_name": "title",
                "section_text": "Advanced Machine Learning System",
                "similar_patents": [
                    {"patent_id": "US11111111", "title": "Machine Learning System", "similarity_score": 0.92},
                    {"patent_id": "US22222222", "title": "Advanced AI System", "similarity_score": 0.85}
                ],
                "analysis_time": 0.5,
                "patent_count": 2,
                "top_similarity_score": 0.92
            },
            "abstract": {
                "section_name": "abstract",
                "section_text": "A machine learning system for autonomous vehicles...",
                "similar_patents": [
                    {"patent_id": "US33333333", "title": "Autonomous Vehicle System", "similarity_score": 0.88}
                ],
                "analysis_time": 0.3,
                "patent_count": 1,
                "top_similarity_score": 0.88
            },
            "claims": {
                "section_name": "claims",
                "section_text": "1. A machine learning system comprising...",
                "similar_patents": [],
                "analysis_time": 0.2,
                "patent_count": 0,
                "top_similarity_score": 0.0
            }
        }
    }
    
    print("Input draft result structure:")
    print(f"  Draft length: {len(mock_draft_result['draft'])} characters")
    print(f"  Model: {mock_draft_result['model']}")
    print(f"  Sections: {list(mock_draft_result['section_similarities'].keys())}")
    
    # Use utility function
    similarity_map = get_section_similarity_map(mock_draft_result)
    
    print(f"\nExtracted similarity map:")
    print(f"  Sections: {len(similarity_map)}")
    
    for section_name, data in similarity_map.items():
        print(f"\n  {section_name.upper()}:")
        print(f"    Section name: {data['section_name']}")
        print(f"    Patent count: {data['patent_count']}")
        print(f"    Analysis time: {data['analysis_time']:.3f}s")
        print(f"    Top similarity: {data['top_similarity_score']:.3f}")
        
        if data['similar_patents']:
            print(f"    Similar patents:")
            for i, patent in enumerate(data['similar_patents'][:2], 1):
                print(f"      {i}. {patent['patent_id']} - {patent['title']} ({patent['similarity_score']:.3f})")


async def demo_integration_with_orchestration():
    """Demonstrate integration with the orchestration system."""
    print("\nINTEGRATION WITH ORCHESTRATION DEMO")
    
    print("This demo shows how per-section similarity analysis integrates")
    print("with the async orchestration system for concurrent execution.")
    
    # Sample invention description
    invention_description = "A quantum computing system for drug discovery using machine learning algorithms with error correction and fault tolerance mechanisms."
    
    print(f"\nInvention description: {invention_description}")
    print("\nThis would trigger:")
    print("1. Concurrent LLM generation of patent draft")
    print("2. Concurrent background search for similar patents")
    print("3. Per-section similarity analysis after generation completes")
    print("4. Structured results with similarity data for each section")
    
    # Show the expected workflow
    print(f"\nExpected workflow:")
    print("1. Parse generated draft into sections (title, abstract, field, etc.)")
    print("2. For each section with content:")
    print("   - Extract section text")
    print("   - Search for similar patents using section text as query")
    print("   - Rank results by similarity score")
    print("   - Store as {patent_id, title, similarity_score} objects")
    print("3. Combine all section results into unified response")
    
    print(f"\nBenefits of per-section analysis:")
    print("- More granular similarity insights")
    print("- Better understanding of which sections are most similar")
    print("- Targeted prior art search for specific patent sections")
    print("- Improved patent drafting guidance")


async def demo_performance_comparison():
    """Demonstrate performance comparison between different approaches."""
    print("\nPERFORMANCE COMPARISON DEMO")
    
    print("Comparing different similarity analysis approaches:")
    print()
    
    approaches = {
        "Whole Draft Analysis": {
            "description": "Search entire draft as single query",
            "pros": ["Simple implementation", "Fast single search"],
            "cons": ["Less granular", "May miss section-specific similarities", "Less targeted results"],
            "use_case": "Quick overview of overall similarity"
        },
        "Per-Section Analysis": {
            "description": "Analyze each section separately",
            "pros": ["Granular insights", "Targeted similarity", "Better section-specific guidance"],
            "cons": ["Multiple searches required", "More complex implementation"],
            "use_case": "Detailed patent analysis and drafting guidance"
        },
        "Hybrid Approach": {
            "description": "Combine whole draft + per-section analysis",
            "pros": ["Best of both worlds", "Comprehensive coverage"],
            "cons": ["Highest computational cost", "Most complex"],
            "use_case": "Comprehensive patent analysis"
        }
    }
    
    for approach, details in approaches.items():
        print(f"{approach}:")
        print(f"  Description: {details['description']}")
        print(f"  Pros: {', '.join(details['pros'])}")
        print(f"  Cons: {', '.join(details['cons'])}")
        print(f"  Best for: {details['use_case']}")
        print()
    
    print("Our implementation uses the Per-Section Analysis approach")
    print("with concurrent execution for optimal performance.")


async def main():
    """Main demonstration function."""
    print("PATENT NLP PROJECT - PER-SECTION SIMILARITY ANALYSIS DEMO")
    print("This demo showcases per-section similarity comparison after each generation step.")
    
    try:
        # Demo 1: Section parsing
        await demo_section_parsing()
        
        # Demo 2: Per-section similarity analysis
        await demo_per_section_similarity()
        
        # Demo 3: Utility function
        await demo_utility_function()
        
        # Demo 4: Integration with orchestration
        await demo_integration_with_orchestration()
        
        # Demo 5: Performance comparison
        await demo_performance_comparison()
        
        print("DEMO COMPLETED SUCCESSFULLY!")

        print("Key features demonstrated:")
        print("LLM output parsing into structured sections")
        print("Per-section similarity analysis using existing search API")
        print("Ranked similarity results as {patent_id, title, similarity_score} objects")
        print("Utility function for extracting similarity maps")
        print("Integration with async orchestration system")
        print("Performance comparison of different approaches")

        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
