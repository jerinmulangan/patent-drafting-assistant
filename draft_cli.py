#!/usr/bin/env python3
"""
CLI for patent draft generation with optional similarity analysis.
Supports both basic draft generation and combined draft + similarity results.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from ollama_service import get_ollama_service
from async_orchestration import get_orchestration_service
from schema_validator import get_schema_validator


def print_status(message: str, status_type: str = "info"):
    """Print status message with formatting."""
    status_symbols = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌",
        "progress": "🔄"
    }
    
    symbol = status_symbols.get(status_type, "ℹ️")
    print(f"{symbol} {message}")


def print_generation_progress(step: str, details: str = ""):
    """Print generation progress with status updates."""
    progress_messages = {
        "starting": "Starting patent draft generation...",
        "generating_title": "Generating patent title...",
        "generating_abstract": "Generating abstract...",
        "generating_claims": "Generating claims...",
        "generating_description": "Generating detailed description...",
        "generating_field": "Generating field of invention...",
        "generating_background": "Generating background section...",
        "generating_summary": "Generating summary...",
        "completed": "Draft generation completed!"
    }
    
    message = progress_messages.get(step, step)
    if details:
        message += f" {details}"
    
    print_status(message, "progress")


def print_search_progress(step: str, section: str = ""):
    """Print search progress with status updates."""
    search_messages = {
        "starting_search": "Starting similarity analysis...",
        "searching_section": f"Searching prior art for {section}...",
        "analyzing_similarity": f"Analyzing similarity for {section}...",
        "search_completed": "Similarity analysis completed!"
    }
    
    message = search_messages.get(step, step)
    if section:
        message = message.replace("{section}", section)
    
    print_status(message, "progress")


async def generate_draft_basic(description: str, model: str, template_type: str, 
                              use_cache: bool = True, output_file: Optional[str] = None) -> Dict[str, Any]:
    """Generate basic patent draft without similarity analysis."""
    print_generation_progress("starting")
    
    # Get Ollama service
    ollama_service = get_ollama_service()
    
    if not ollama_service.is_available():
        print_status("Ollama service is not available. Please ensure Ollama is running.", "error")
        return {"success": False, "error": "Ollama service unavailable"}
    
    try:
        # Generate draft
        print_generation_progress("generating_title")
        print_generation_progress("generating_abstract") 
        print_generation_progress("generating_claims")
        print_generation_progress("generating_description")
        print_generation_progress("generating_field")
        print_generation_progress("generating_background")
        print_generation_progress("generating_summary")
        
        result = ollama_service.generate_patent_draft(
            description=description,
            model_name=model,
            template_type=template_type,
            use_cache=use_cache
        )
        
        print_generation_progress("completed")
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print_status(f"Draft saved to {output_path}", "success")
        
        return result
        
    except Exception as e:
        print_status(f"Error generating draft: {str(e)}", "error")
        return {"success": False, "error": str(e)}


async def generate_draft_with_similarity(description: str, model: str, template_type: str,
                                       search_mode: str, top_k: int, include_snippets: bool,
                                       use_cache: bool = True, output_file: Optional[str] = None) -> Dict[str, Any]:
    """Generate patent draft with similarity analysis."""
    print_generation_progress("starting")
    
    # Get orchestration service
    orchestration_service = get_orchestration_service()
    
    try:
        # Generate draft with background search
        print_generation_progress("generating_title")
        print_generation_progress("generating_abstract")
        print_generation_progress("generating_claims") 
        print_generation_progress("generating_description")
        print_generation_progress("generating_field")
        print_generation_progress("generating_background")
        print_generation_progress("generating_summary")
        
        # Start similarity analysis
        print_search_progress("starting_search")
        
        result = await orchestration_service.generate_with_background_search(
            prompt=description,
            search_mode=search_mode,
            model_name=model,
            template_type=template_type,
            top_k=top_k,
            include_snippets=include_snippets,
            use_cache=use_cache
        )
        
        # Print section-specific search progress
        if hasattr(result, 'section_similarities') and result.section_similarities:
            for section_name in result.section_similarities.keys():
                print_search_progress("searching_section", section_name)
                print_search_progress("analyzing_similarity", section_name)
        
        print_search_progress("search_completed")
        print_generation_progress("completed")
        
        # Convert to JSON schema format
        json_result = orchestration_service.to_json_schema(result)
        
        # Validate result
        validator = get_schema_validator()
        is_valid, errors = validator.validate_draft_response(json_result)
        
        if not is_valid:
            print_status(f"Warning: Generated response has validation errors: {errors}", "warning")
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2)
            print_status(f"Combined draft and similarity results saved to {output_path}", "success")
        
        return json_result
        
    except Exception as e:
        print_status(f"Error generating draft with similarity: {str(e)}", "error")
        return {"success": False, "error": str(e)}


def print_results_summary(result: Dict[str, Any], with_similarity: bool = False):
    """Print a summary of the generation results."""
    if not result.get("success", True):
        print_status(f"Generation failed: {result.get('error', 'Unknown error')}", "error")
        return
    
    print("\n" + "="*60)
    print("GENERATION RESULTS SUMMARY")
    print("="*60)
    
    # Basic info
    print(f"Model: {result.get('model', 'N/A')}")
    print(f"Template: {result.get('template_type', 'N/A')}")
    print(f"Generation time: {result.get('generation_time', 0):.2f}s")
    print(f"Cached: {result.get('cached', False)}")
    
    # Draft info
    draft_text = result.get('draft', '')
    print(f"Draft length: {len(draft_text)} characters")
    print(f"Draft preview: {draft_text[:100]}...")
    
    if with_similarity:
        # Similarity info
        section_similarities = result.get('section_similarities', {})
        total_analysis_time = result.get('total_analysis_time', 0)
        metadata = result.get('metadata', {})
        
        print(f"\nSimilarity Analysis:")
        print(f"  Total analysis time: {total_analysis_time:.2f}s")
        print(f"  Sections analyzed: {metadata.get('sections_analyzed', 0)}")
        print(f"  Total similar patents: {metadata.get('total_similar_patents', 0)}")
        print(f"  Search mode: {metadata.get('search_mode', 'N/A')}")
        
        print(f"\nSection Details:")
        for section_name, section_data in section_similarities.items():
            patent_count = section_data.get('patent_count', 0)
            analysis_time = section_data.get('analysis_time', 0)
            top_score = section_data.get('top_similarity_score', 0)
            
            print(f"  {section_name.upper()}:")
            print(f"    Similar patents: {patent_count}")
            print(f"    Analysis time: {analysis_time:.3f}s")
            print(f"    Top similarity: {top_score:.3f}")
            
            # Show top similar patent
            similar_patents = section_data.get('similar_patents', [])
            if similar_patents:
                top_patent = similar_patents[0]
                print(f"    Most similar: {top_patent.get('title', 'N/A')} ({top_patent.get('similarity_score', 0):.3f})")
    
    print("="*60)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Patent draft generation CLI with optional similarity analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic draft generation
  python draft_cli.py "A neural network for image analysis" --model llama3.2:3b
  
  # Draft with similarity analysis
  python draft_cli.py "A neural network for image analysis" --with-similarity --search-mode hybrid
  
  # Save results to file
  python draft_cli.py "A quantum computing algorithm" --with-similarity --output results.json
  
  # Custom similarity settings
  python draft_cli.py "A medical device" --with-similarity --top-k 10 --search-mode semantic
        """
    )
    
    # Required arguments
    parser.add_argument(
        "description",
        type=str,
        help="Invention description (50-5000 characters)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="llama3.2:3b",
        choices=["llama3.2:1b", "llama3.2:3b", "mistral:7b", "codellama:7b"],
        help="Ollama model to use for generation (default: llama3.2:3b)"
    )
    
    parser.add_argument(
        "--template-type", "-t",
        type=str,
        default="utility",
        choices=["utility", "software", "medical", "design"],
        help="Patent template type (default: utility)"
    )
    
    parser.add_argument(
        "--with-similarity", "-s",
        action="store_true",
        help="Enable similarity analysis with background search"
    )
    
    parser.add_argument(
        "--search-mode",
        type=str,
        default="hybrid",
        choices=["tfidf", "semantic", "hybrid", "hybrid-advanced"],
        help="Search mode for similarity analysis (default: hybrid)"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of similar patents per section (1-20, default: 5)"
    )
    
    parser.add_argument(
        "--include-snippets",
        action="store_true",
        default=True,
        help="Include text snippets in similarity results (default: True)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (regenerate even if cached result exists)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path for results (JSON format)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress status messages (only show results)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output against JSON schema"
    )
    
    args = parser.parse_args()
    
    # Validate description length
    if len(args.description) < 50:
        print_status("Description must be at least 50 characters long", "error")
        sys.exit(1)
    
    if len(args.description) > 5000:
        print_status("Description must be no more than 5000 characters long", "error")
        sys.exit(1)
    
    # Validate top_k range
    if not 1 <= args.top_k <= 20:
        print_status("top_k must be between 1 and 20", "error")
        sys.exit(1)
    
    # Suppress status messages if quiet mode
    if args.quiet:
        def print_status(msg, status_type="info"):
            pass
        def print_generation_progress(step, details=""):
            pass
        def print_search_progress(step, section=""):
            pass
    
    # Run the appropriate generation function
    async def run_generation():
        if args.with_similarity:
            return await generate_draft_with_similarity(
                description=args.description,
                model=args.model,
                template_type=args.template_type,
                search_mode=args.search_mode,
                top_k=args.top_k,
                include_snippets=args.include_snippets,
                use_cache=not args.no_cache,
                output_file=args.output
            )
        else:
            return await generate_draft_basic(
                description=args.description,
                model=args.model,
                template_type=args.template_type,
                use_cache=not args.no_cache,
                output_file=args.output
            )
    
    try:
        result = asyncio.run(run_generation())
        
        # Print results summary
        if not args.quiet:
            print_results_summary(result, args.with_similarity)
        
        # Validate if requested
        if args.validate and args.with_similarity:
            validator = get_schema_validator()
            is_valid, errors = validator.validate_draft_response(result)
            if is_valid:
                print_status("Output validation: PASSED", "success")
            else:
                print_status(f"Output validation: FAILED - {errors}", "error")
                sys.exit(1)
        
        # Exit with appropriate code
        if result.get("success", True):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_status("Generation interrupted by user", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
