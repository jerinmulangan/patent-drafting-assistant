#!/usr/bin/env python3
"""
Test script for the advanced 17-step patent drafting system.
"""

import json
from patent_drafting_system import get_advanced_drafting_system
from evaluation_harness import EvaluationHarness


def test_basic_generation():
    """Test basic draft generation."""
    print("=" * 60)
    print("Test 1: Basic Draft Generation")
    print("=" * 60)
    
    try:
        system = get_advanced_drafting_system(
            precision_model="llama3.2:3b",
            fluency_model="mistral:7b"
        )
        
        invention_description = """
        A neural network system for analyzing medical images that uses convolutional layers 
        to detect anomalies in X-ray scans. The system includes a preprocessing module that 
        normalizes image data, a feature extraction module using deep convolutional networks, 
        and a classification module that outputs probability scores for different anomaly types.
        """
        
        print("Generating draft...")
        result = system.generate_complete_draft(
            invention_description=invention_description,
            use_ensemble=True,
            use_scaffolding=True,
            use_two_pass=True,
            use_critique=True
        )
        
        print(f"\n✓ Generation completed in {result['generation_time']:.2f} seconds")
        print(f"✓ Generated {len(result['sections'])} sections")
        print(f"✓ Glossary contains {len(result['glossary'])} terms")
        
        if result.get('outline'):
            print("✓ Outline generated")
        
        if result.get('critique_results'):
            print(f"✓ Critique results for {len(result['critique_results'])} sections")
        
        # Print section names
        print("\nGenerated sections:")
        for section_name in result['sections'].keys():
            print(f"  - {section_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation():
    """Test evaluation harness."""
    print("\n" + "=" * 60)
    print("Test 2: Evaluation Harness")
    print("=" * 60)
    
    try:
        evaluator = EvaluationHarness()
        
        # Create a sample draft
        sample_draft = {
            "TITLE OF THE INVENTION": "System for Medical Image Analysis",
            "FIELD OF THE INVENTION": "The present invention relates to medical imaging systems.",
            "BACKGROUND OF THE INVENTION": "Prior art systems have limitations.",
            "BRIEF SUMMARY OF THE INVENTION": "The invention provides improvements.",
            "BRIEF DESCRIPTION OF THE DRAWINGS": "FIG. 1 shows a system diagram.",
            "DETAILED DESCRIPTION OF THE INVENTION": "The system includes various components.",
            "CLAIMS": "1. A system comprising: a processor; and a memory.",
            "ABSTRACT OF THE DISCLOSURE": "A system for analyzing medical images."
        }
        
        sample_glossary = {
            "system": {
                "definition": "A computing system",
                "allowed_variants": ["computing system"],
                "forbidden_synonyms": ["device", "apparatus"]
            }
        }
        
        print("Evaluating draft...")
        result = evaluator.evaluate_draft(
            draft=sample_draft,
            glossary=sample_glossary
        )
        
        print(f"\n✓ Evaluation completed")
        print(f"  Composite Score: {result.composite_score:.2f}")
        print(f"  Section Presence: {result.section_presence_score:.2f}")
        print(f"  Section Ordering: {result.section_ordering_score:.2f}")
        print(f"  Banned Phrases: {result.banned_phrase_detection_score:.2f}")
        print(f"  Glossary Compliance: {result.glossary_compliance_score:.2f}")
        print(f"  Figure Consistency: {result.figure_numeral_consistency_score:.2f}")
        print(f"  Claim Antecedent: {result.claim_antecedent_basis_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decoding_profiles():
    """Test decoding profiles."""
    print("\n" + "=" * 60)
    print("Test 3: Decoding Profiles")
    print("=" * 60)
    
    try:
        from patent_drafting_system import DECODING_PROFILES
        
        print("Available profiles:")
        for name, profile in DECODING_PROFILES.items():
            print(f"\n  {name}:")
            print(f"    Temperature: {profile.temperature}")
            print(f"    Top-p: {profile.top_p}")
            print(f"    Top-k: {profile.top_k}")
            print(f"    Repeat Penalty: {profile.repeat_penalty}")
            if profile.seed:
                print(f"    Seed: {profile.seed}")
        
        # Test conversion to Ollama options
        strict_options = DECODING_PROFILES["strict"].to_ollama_options()
        print(f"\n✓ Strict profile options: {strict_options}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_section_templates():
    """Test section templates."""
    print("\n" + "=" * 60)
    print("Test 4: Section Templates")
    print("=" * 60)
    
    try:
        from patent_drafting_system import SECTION_TEMPLATES
        
        print(f"Available templates: {len(SECTION_TEMPLATES)}")
        for name, template in SECTION_TEMPLATES.items():
            print(f"\n  {name}:")
            print(f"    Section: {template.section_name}")
            print(f"    Constraints: {len(template.constraints)}")
            print(f"    Banned Phrases: {len(template.banned_phrases)}")
        
        # Test prompt building
        test_template = SECTION_TEMPLATES["FIELD"]
        prompt = test_template.build_prompt(
            facts=["Medical imaging", "Neural networks"],
            glossary={"system": {"definition": "A computing system"}},
            figures=None
        )
        
        print(f"\n✓ Sample prompt generated ({len(prompt)} chars)")
        print(f"  First 200 chars: {prompt[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_terminology_manager():
    """Test terminology/glossary system."""
    print("\n" + "=" * 60)
    print("Test 5: Terminology Manager")
    print("=" * 60)
    
    try:
        from patent_drafting_system import TerminologyManager
        
        manager = TerminologyManager()
        
        # Test term extraction
        text = "The system includes a processor and memory. The processor executes instructions."
        terms = manager.extract_terms(text)
        print(f"✓ Extracted {len(terms)} candidate terms: {terms}")
        
        # Test validation
        manager.glossary = {
            "processor": {
                "definition": "A computing processor",
                "allowed_variants": ["CPU"],
                "forbidden_synonyms": ["chip", "circuit"]
            }
        }
        
        issues = manager.validate_terms("The chip processes data.")
        print(f"✓ Validation found {len(issues)} issues: {issues}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Advanced Patent Drafting System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Decoding Profiles", test_decoding_profiles),
        ("Section Templates", test_section_templates),
        ("Terminology Manager", test_terminology_manager),
        ("Evaluation Harness", test_evaluation),
        ("Basic Generation", test_basic_generation),  # Last - requires Ollama
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

