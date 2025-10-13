#!/usr/bin/env python3
"""
Integration tests for the complete async orchestration system.
Tests the full pipeline from API request to response.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any

# Import the services
from async_orchestration import get_orchestration_service, generate_with_background_search
from search_service import run_search, SearchRequest
from ollama_service import get_ollama_service


class TestIntegrationOrchestration:
    """Integration tests for the complete orchestration system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestration_service = get_orchestration_service()
        self.ollama_service = get_ollama_service()
        
        # Test prompts of varying complexity
        self.test_prompts = {
            "simple": "A simple mechanical device for opening bottles.",
            "medium": "A neural network system for analyzing medical images that uses convolutional layers to detect anomalies in X-ray scans.",
            "complex": "An advanced quantum computing system that uses superconducting qubits to perform quantum machine learning algorithms for drug discovery, with error correction and fault tolerance mechanisms."
        }
    
    async def test_full_pipeline_simple(self):
        """Test the full pipeline with a simple prompt."""
        print("Testing full pipeline with simple prompt...")
        
        prompt = self.test_prompts["simple"]
        
        # Test the orchestration service directly
        result = await self.orchestration_service.generate_with_background_search(
            prompt=prompt,
            search_mode='hybrid',
            model_name='llama3.2:3b',
            template_type='utility',
            top_k=3,
            include_snippets=True,
            use_cache=False
        )
        
        # Validate result structure
        assert result.success, f"Generation failed: {result.message}"
        assert result.draft, "Draft should not be empty"
        assert result.model == 'llama3.2:3b'
        assert result.template_type == 'utility'
        assert result.generation_time > 0
        assert result.total_analysis_time > result.generation_time
        assert len(result.section_similarities) > 0
        
        # Check that sections were parsed
        expected_sections = ['title', 'field', 'background', 'summary', 'drawings', 'description', 'claims']
        for section in expected_sections:
            if section in result.section_similarities:
                similarity = result.section_similarities[section]
                assert similarity.section_name == section
                assert similarity.analysis_time >= 0
                assert isinstance(similarity.similar_patents, list)
        
        print(f"Simple pipeline completed in {result.total_analysis_time:.2f}s")
        print(f"Generated {len(result.draft)} characters")
        print(f"Analyzed {len(result.section_similarities)} sections")
        
        return result
    
    async def test_full_pipeline_medium(self):
        """Test the full pipeline with a medium complexity prompt."""
        print("\nTesting full pipeline with medium complexity prompt...")
        
        prompt = self.test_prompts["medium"]
        
        result = await self.orchestration_service.generate_with_background_search(
            prompt=prompt,
            search_mode='semantic',
            model_name='llama3.2:3b',
            template_type='utility',
            top_k=5,
            include_snippets=True,
            use_cache=False
        )
        
        # Validate result
        assert result.success, f"Generation failed: {result.message}"
        assert result.draft, "Draft should not be empty"
        assert "neural network" in result.draft.lower() or "medical" in result.draft.lower()
        
        # Check section similarities
        total_similar_patents = sum(
            len(similarity.similar_patents) 
            for similarity in result.section_similarities.values()
        )
        assert total_similar_patents > 0, "Should find some similar patents"
        
        print(f"Medium pipeline completed in {result.total_analysis_time:.2f}s")
        print(f"Found {total_similar_patents} total similar patents across all sections")
        
        return result
    
    async def test_concurrency_performance(self):
        """Test that generation and search run concurrently."""
        print("\nTesting concurrency performance...")
        
        prompt = self.test_prompts["medium"]
        
        # Measure individual operations
        start_time = time.time()
        
        # Generate draft only
        draft_result = await self.orchestration_service._generate_draft_async(
            prompt, 'llama3.2:3b', 'utility', False
        )
        draft_time = time.time() - start_time
        
        # Search only
        start_time = time.time()
        search_results = await self.orchestration_service._search_patents_async(
            prompt, 'hybrid', 5, True
        )
        search_time = time.time() - start_time
        
        # Combined operation
        start_time = time.time()
        combined_result = await self.orchestration_service.generate_with_background_search(
            prompt=prompt,
            search_mode='hybrid',
            top_k=5,
            use_cache=False
        )
        combined_time = time.time() - start_time
        
        # Concurrency should make combined time less than sum of individual times
        sequential_time = draft_time + search_time
        concurrency_savings = sequential_time - combined_time
        
        print(f"Draft generation: {draft_time:.2f}s")
        print(f"Search: {search_time:.2f}s")
        print(f"Sequential total: {sequential_time:.2f}s")
        print(f"Combined (concurrent): {combined_time:.2f}s")
        print(f"Concurrency savings: {concurrency_savings:.2f}s")
        
        # Should have some concurrency benefit (allow for overhead)
        assert concurrency_savings > 0, "Concurrent execution should be faster than sequential"
        assert combined_result.success, "Combined operation should succeed"
    
    async def test_json_serialization(self):
        """Test JSON serialization of results."""
        print("\nTesting JSON serialization...")
        
        prompt = self.test_prompts["simple"]
        
        result = await self.orchestration_service.generate_with_background_search(
            prompt=prompt,
            search_mode='hybrid',
            top_k=3,
            use_cache=False
        )
        
        # Convert to JSON schema
        json_result = self.orchestration_service.to_json_schema(result)
        
        # Test JSON serialization
        json_str = json.dumps(json_result, indent=2)
        assert isinstance(json_str, str)
        assert len(json_str) > 100, "JSON should have substantial content"
        
        # Test JSON deserialization
        parsed_result = json.loads(json_str)
        assert parsed_result["draft"] == result.draft
        assert parsed_result["model"] == result.model
        assert parsed_result["success"] == result.success
        assert "section_similarities" in parsed_result
        
        print(f"JSON serialization successful ({len(json_str)} characters)")
        print(f"JSON deserialization successful")
        
        return json_result
    
    async def test_different_search_modes(self):
        """Test different search modes."""
        print("\nTesting different search modes...")
        
        prompt = self.test_prompts["medium"]
        search_modes = ['tfidf', 'semantic', 'hybrid', 'hybrid-advanced']
        
        results = {}
        
        for mode in search_modes:
            print(f"  Testing {mode} mode...")
            
            result = await self.orchestration_service.generate_with_background_search(
                prompt=prompt,
                search_mode=mode,
                top_k=3,
                use_cache=False
            )
            
            assert result.success, f"Mode {mode} failed: {result.message}"
            
            # Count similar patents found
            total_similar = sum(
                len(similarity.similar_patents) 
                for similarity in result.section_similarities.values()
            )
            
            results[mode] = {
                'total_time': result.total_analysis_time,
                'similar_patents': total_similar,
                'sections_analyzed': len(result.section_similarities)
            }
            
            print(f"    {mode}: {total_similar} similar patents, {result.total_analysis_time:.2f}s")
        
        # All modes should work
        assert len(results) == len(search_modes)
        
        return results
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("\nTesting error handling...")
        
        # Test with empty prompt
        result = await self.orchestration_service.generate_with_background_search(
            prompt="",
            search_mode='hybrid'
        )
        assert not result.success, "Empty prompt should fail"
        assert "Error" in result.message
        
        # Test with very short prompt
        result = await self.orchestration_service.generate_with_background_search(
            prompt="short",
            search_mode='hybrid'
        )
        assert not result.success, "Short prompt should fail"
        assert "Error" in result.message
        
        print("Error handling tests passed")
    
    async def test_section_parsing_accuracy(self):
        """Test accuracy of section parsing."""
        print("\nTesting section parsing accuracy...")
        
        prompt = self.test_prompts["medium"]
        
        result = await self.orchestration_service.generate_with_background_search(
            prompt=prompt,
            search_mode='hybrid',
            top_k=3,
            use_cache=False
        )
        
        assert result.success, "Generation should succeed"
        
        # Parse sections manually
        sections = self.orchestration_service._parse_draft_sections(result.draft)
        
        # Check that we found the expected sections
        expected_sections = ['title', 'field', 'background', 'summary', 'drawings', 'description', 'claims']
        found_sections = [name for name, text in sections.items() if text.strip()]
        
        print(f"Found {len(found_sections)} sections: {found_sections}")
        
        # Should find at least some sections
        assert len(found_sections) >= 3, f"Should find at least 3 sections, found: {found_sections}"
        
        # Check section content quality
        for section_name, section_text in sections.items():
            if section_text.strip():
                assert len(section_text) > 10, f"Section {section_name} too short"
                print(f"  {section_name}: {len(section_text)} characters")
    
    async def run_all_tests(self):
        """Run all integration tests."""
 
        print("RUNNING INTEGRATION TESTS FOR ASYNC ORCHESTRATION")

        
        try:
            # Test 1: Simple pipeline
            simple_result = await self.test_full_pipeline_simple()
            
            # Test 2: Medium complexity pipeline
            medium_result = await self.test_full_pipeline_medium()
            
            # Test 3: Concurrency performance
            await self.test_concurrency_performance()
            
            # Test 4: JSON serialization
            json_result = await self.test_json_serialization()
            
            # Test 5: Different search modes
            mode_results = await self.test_different_search_modes()
            
            # Test 6: Error handling
            await self.test_error_handling()
            
            # Test 7: Section parsing accuracy
            await self.test_section_parsing_accuracy()
            

            print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

            
            # Summary
            print(f"\nSUMMARY:")
            print(f"Simple pipeline: {simple_result.total_analysis_time:.2f}s")
            print(f"Medium pipeline: {medium_result.total_analysis_time:.2f}s")
            print(f"JSON serialization: {len(json.dumps(json_result))} characters")
            print(f"Search modes tested: {len(mode_results)}")
            
            return True
            
        except Exception as e:
            print(f"\nINTEGRATION TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main test runner."""
    tester = TestIntegrationOrchestration()
    success = await tester.run_all_tests()
    
    if success:
        print("\n All tests completed successfully!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
