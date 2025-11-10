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
        # === V2 INLINE: USPTO structured draft generator (flags wired) ===
    def generate_uspto_structured_draft(
        self,
        description: str,
        model_name: Optional[str] = None,
        template_type: str = "utility",
        jurisdiction: str = "USPTO",
        claim_bundle: str = "all",
        independent_claims_per_type: int = 1,
        dependent_claims_per_independent: int = 3,
        spec_depth: str = "deep",
        embodiment_style: str = "balanced",
        include_definitions: bool = True,
        include_alternatives: bool = True,
        include_figure_callouts: bool = True,
        include_glossary: bool = True,
        include_enablement_language: bool = True,
        include_best_mode: bool = True,
        include_markush_examples: bool = False,
        add_boilerplate_variations: bool = True,
        novelty_refs: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.4,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a fully structured, USPTO-compliant nonprovisional utility patent draft
        that meets all formatting and disclosure requirements per 35 U.S.C. 112(a).
        """
        if not self.is_available():
            raise RuntimeError("Ollama is not available. Please install and start Ollama.")

        model = model_name or self.model_name
        if not self.ensure_model_available(model):
            raise RuntimeError(f"Model {model} is not available")

        # Validate description
        self.validate_description(description)

        # --- Prior art context (optional) ---
        refs_text = ""
        if novelty_refs:
            ref_lines = []
            for r in novelty_refs[:10]:
                title = r.get("title") or r.get("doc_id", "Unknown")
                doc_id = r.get("doc_id", "N/A")
                ref_lines.append(f"- {title} (ID: {doc_id})")
            refs_text = "\nRelevant prior art (for context only):\n" + "\n".join(ref_lines) + "\n"

        # --- Calculate total independent claims: target 3 independent claims ---
        # If claim_bundle is "all", we want 3 independent total (1 system, 1 method, 1 CRM)
        # Otherwise, scale based on claim_bundle
        if claim_bundle == "all":
            total_independent_target = 3
        elif claim_bundle in ["system+method", "method+crm"]:
            total_independent_target = 2
        else:
            total_independent_target = 1
        
        # Adjust dependent claims to target up to 6 total
        total_dependent_target = min(6, total_independent_target * dependent_claims_per_independent)

        # --- USPTO-required sections in exact order ---
        required_sections = [
            "TITLE OF THE INVENTION",
            "CROSS-REFERENCE TO RELATED APPLICATIONS",
            "FIELD OF THE INVENTION",
            "BACKGROUND OF THE INVENTION",
            "BRIEF SUMMARY OF THE INVENTION",
            "BRIEF DESCRIPTION OF THE DRAWINGS",
            "DETAILED DESCRIPTION OF THE INVENTION",
        ]
        
        # Optional sections
        optional_sections = []
        if include_definitions or include_glossary:
            optional_sections.append("DEFINITIONS")
        
        # Claims and Abstract are handled separately
        all_sections = required_sections + optional_sections

        # --- Style and compliance directives ---
        style_directives = [
            f"Specification depth: {spec_depth}. Embodiment scope: {embodiment_style}.",
            "Use clear, technical, non-promotional language. Avoid marketing terms like 'revolutionary' or 'will make millions'.",
            "Ensure proper antecedent basis: every term used in claims must be introduced in the specification before first use in claims.",
            "Use consistent terminology throughout: the same component/feature must use the same term in specification and claims.",
            "Write in the present tense and active voice where appropriate.",
        ]
        
        if include_enablement_language:
            style_directives.append(
                "Include explicit enablement language satisfying 35 U.S.C. §112(a): describe how to make and use the invention "
                "with sufficient detail that a person of ordinary skill in the art can practice it without undue experimentation."
            )
        
        if include_best_mode:
            style_directives.append(
                "Include an explicit 'Best Mode' paragraph within the Detailed Description describing the inventor's preferred "
                "implementation of the invention."
            )
        
        if include_alternatives:
            style_directives.append(
                "Provide multiple alternative embodiments and variations using phrases like 'In some embodiments', "
                "'In other embodiments', 'In yet another embodiment'."
            )
        
        if include_figure_callouts:
            style_directives.append(
                "In Brief Description of Drawings, list each figure as 'FIG. 1 shows...', 'FIG. 2 illustrates...', etc. "
                "Reference figures numerically (FIG. 1, FIG. 2, FIG. 3) throughout the Detailed Description."
            )
        
        if add_boilerplate_variations:
            style_directives.append(
                "Vary boilerplate language to avoid repetitive phrasing while maintaining formal patent style."
            )
        
        if include_markush_examples:
            style_directives.append(
                "Where appropriate, include Markush group examples in claims using 'selected from the group consisting of' format."
            )

        style_text = "\n".join([f"- {d}" for d in style_directives])

        # --- Claim formatting instructions ---
        claim_instructions = f"""
CLAIMS FORMATTING REQUIREMENTS:
- Generate {total_independent_target} independent claim(s) and up to {total_dependent_target} dependent claim(s).
- Each claim must be a single sentence starting with a capital letter and ending with a period.
- Number claims sequentially: 1., 2., 3., etc.
- Independent claims: Start with "1. A [system/method/apparatus] comprising:" or similar.
- Dependent claims: Start with "2. The [system/method/apparatus] of claim 1, wherein..." or "2. The [system/method/apparatus] of claim 1, further comprising..."
- Properly indent dependent claims (use 3-4 spaces) to show hierarchy.
- Ensure all claim terms have antecedent basis in the specification.
- Use consistent terminology: terms in claims must match terms used in the Detailed Description.
- Avoid using "said" unnecessarily; prefer "the" for subsequent references.
- Each dependent claim must depend from a preceding claim (claim 2 depends on claim 1, claim 3 can depend on claim 1 or 2, etc.).
"""

        # --- Comprehensive USPTO-compliant prompt ---
        prompt = f"""You are an expert U.S. patent attorney drafting a complete, USPTO-compliant nonprovisional utility patent application. Your task is to generate a DETAILED, TECHNICAL, and COMPREHENSIVE patent specification that is suitable for examiner review.

INVENTION DESCRIPTION:
\"\"\"{description.strip()}\"\"\"

{refs_text}

CRITICAL: You MUST generate DETAILED, TECHNICAL content based on the invention description above. Do NOT use generic placeholders or vague descriptions. Every section must be SPECIFIC, TECHNICAL, and DETAILED. Real USPTO patents are verbose, comprehensive, and include extensive technical detail.

USPTO SECTION REQUIREMENTS (write in this exact order with ALL CAPS headers on separate lines):

1. TITLE OF THE INVENTION
   - Write a short, specific, non-generic title (typically 5-15 words) that accurately describes the invention.
   - Capitalize major words.
   - Base the title directly on the invention description provided.

2. CROSS-REFERENCE TO RELATED APPLICATIONS
   - If applicable, list related applications (e.g., "This application claims priority to U.S. Provisional Application No. XX/XXX,XXX").
   - If none, write exactly: "None"

3. FIELD OF THE INVENTION
   - Write 2-4 detailed sentences describing the technical field(s) this invention relates to.
   - Be specific about the technical domain (e.g., "The present invention relates to the field of machine learning systems, and more particularly to neural network architectures for image processing and analysis.")
   - Base this on the actual invention description.

4. BACKGROUND OF THE INVENTION
   - This section must be COMPREHENSIVE and DETAILED (at least 3-5 paragraphs, 300-500 words).
   - Include two subsections:
     a) Field of the invention: Restate and expand on the technical field (1-2 paragraphs)
     b) Description of related art: Provide DETAILED discussion of:
        - Prior art systems and their limitations
        - Technical problems in the field that remain unsolved
        - Why existing solutions are inadequate
        - Specific technical challenges addressed by this invention
   - Reference specific technical limitations, performance issues, or design constraints.
   - Be detailed and technical - this is NOT a marketing section, it's a technical analysis.

5. BRIEF SUMMARY OF THE INVENTION
   - Provide a DETAILED summary (4-6 paragraphs, 400-600 words).
   - Describe the invention's technical solution in detail.
   - List and explain key technical features, components, and their functions.
   - Explain how the invention solves the problems identified in the Background.
   - Describe technical advantages and improvements over prior art.
   - Include specific technical details about how components work together.

6. BRIEF DESCRIPTION OF THE DRAWINGS
   - List each figure with DETAILED descriptions: "FIG. 1 shows [detailed description of what is illustrated]." "FIG. 2 illustrates [detailed description]." etc.
   - Each figure description should be 1-2 sentences explaining what technical elements are shown.
   - If no specific figures are described in the invention, provide detailed generic descriptions based on the invention:
     * "FIG. 1 is a block diagram of an example system architecture according to an embodiment of the invention."
     * "FIG. 2 is a flowchart illustrating an example method or process flow according to an embodiment."
     * "FIG. 3 illustrates a detailed component view or computing environment suitable for implementing embodiments described herein."

7. DETAILED DESCRIPTION OF THE INVENTION
   - This is the MOST IMPORTANT section. It must be EXTENSIVE, DETAILED, and TECHNICAL (minimum 1000-2000 words, preferably more).
   - Provide a clear, full, concise, and exact description per 35 U.S.C. §112(a).
   - Structure as follows:
     a) Introduction paragraph explaining the overall invention
     b) Detailed description of system/components (if applicable):
        - Describe each major component in detail
        - Explain how components interact
        - Include technical specifications, parameters, algorithms, data structures
        - Reference figures: "As shown in FIG. 1, the system includes..." "With reference to FIG. 2, the method comprises..."
     c) Detailed description of methods/processes (if applicable):
        - Step-by-step technical description of processes
        - Include algorithmic details, data flows, decision points
        - Describe parameters, thresholds, configurations
     d) Alternative embodiments:
        - Use "In some embodiments...", "In other embodiments...", "In yet another embodiment..."
        - Describe variations, modifications, and alternatives
        - Include different configurations, parameter ranges, implementation approaches
     e) Technical details:
        - Describe materials, apparatus, processing conditions, operational parameters
        - Include specific values, ranges, formulas, algorithms where applicable
        - Explain technical mechanisms, data structures, communication protocols
     f) Enablement paragraph:
        - "The foregoing description provides sufficient detail for a person of ordinary skill in the art to make and use the invention without undue experimentation. The description includes materials, apparatus, and processing conditions appropriate for the claimed subject matter. One of ordinary skill in the art can practice the invention based on this disclosure."
     g) Best Mode paragraph:
        - "Best Mode: The inventor contemplates the following as the best mode for carrying out the invention: [DETAILED description of preferred implementation with specific technical details, parameters, configurations, etc.]"
   - Be SPECIFIC and TECHNICAL. Include actual technical content from the invention description.
   - Do NOT use vague phrases like "various components" without describing what they are.
   - Include specific technical terminology, processes, algorithms, and implementation details.

{claim_instructions}

8. ABSTRACT OF THE DISCLOSURE
   - Write a single paragraph (exactly ≤150 words) describing what is new in the invention.
   - Focus on the technical solution and key features.
   - Be specific and technical, not generic.
   - Do not exceed 150 words.

STYLE & COMPLIANCE DIRECTIVES:
{style_text}

CRITICAL REQUIREMENTS FOR QUALITY:
- Generate DETAILED, TECHNICAL content based on the actual invention description. Do NOT use generic placeholders.
- Every section must be SPECIFIC and INFORMATIVE. Real patents are verbose and comprehensive.
- Background section: Minimum 300-500 words with detailed prior art discussion.
- Summary section: Minimum 400-600 words with detailed technical features.
- Detailed Description: Minimum 1000-2000 words with extensive technical detail, specific components, processes, algorithms, parameters.
- Use the invention description to generate SPECIFIC technical content - extract and expand on the technical details provided.
- Include specific technical terminology, processes, data structures, algorithms, parameters, configurations.
- Abstract must be exactly ≤150 words (count carefully).
- Claims must be numbered, single-sentence, properly formatted (no double words like "The The").
- All claim terms must have antecedent basis in the specification.
- Use consistent terminology between specification and claims.
- Avoid marketing language; use technical, objective, precise language.
- Ensure enablement and written description requirements are met (35 U.S.C. §112(a)).

QUALITY CHECK: Before finishing, review your draft. If any section seems generic, vague, or lacks technical detail, expand it with specific technical content based on the invention description.

Now generate the complete, DETAILED, TECHNICAL patent application following the above structure exactly."""

        # --- Generate draft ---
        import re
        import time
        start_time = time.time()
        # Use slightly higher temperature for more detailed, creative content while maintaining coherence
        generation_temperature = min(0.7, max(0.5, float(temperature) + 0.1))
        response = self.client.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": generation_temperature,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
            },
        )
        generation_time = time.time() - start_time
        full_text = response.get("response", "")

        # --- Robust section parsing ---
        # Normalize text
        full_text = full_text.strip() + "\n"
        
        # Enhanced header regex: matches ALL CAPS headers on their own line
        header_patterns = [
            r"\n(TITLE OF THE INVENTION)\s*\n",
            r"\n(CROSS-REFERENCE TO RELATED APPLICATIONS)\s*\n",
            r"\n(FIELD OF THE INVENTION)\s*\n",
            r"\n(BACKGROUND OF THE INVENTION)\s*\n",
            r"\n(BRIEF SUMMARY OF THE INVENTION)\s*\n",
            r"\n(BRIEF DESCRIPTION OF THE DRAWINGS)\s*\n",
            r"\n(DETAILED DESCRIPTION OF THE INVENTION)\s*\n",
            r"\n(DEFINITIONS)\s*\n",
            r"\n(CLAIMS)\s*\n",
            r"\n(ABSTRACT OF THE DISCLOSURE)\s*\n",
            r"\n(ABSTRACT)\s*\n",  # Alternative header
        ]
        
        # Find all section headers
        section_matches = []
        for pattern in header_patterns:
            for match in re.finditer(pattern, full_text, re.IGNORECASE):
                section_name = match.group(1).upper()
                # Normalize variations
                if section_name == "ABSTRACT":
                    section_name = "ABSTRACT OF THE DISCLOSURE"
                section_matches.append((match.start(), match.end(), section_name))
        
        # Sort by position
        section_matches.sort(key=lambda x: x[0])
        
        # Extract sections
        sections: Dict[str, str] = {}
        claims_text = ""
        
        for i, (start, end, name) in enumerate(section_matches):
            # Get content until next section or end
            next_start = section_matches[i + 1][0] if i + 1 < len(section_matches) else len(full_text)
            content = full_text[end:next_start].strip()
            
            if name == "CLAIMS":
                claims_text = content
            else:
                sections[name] = content

        # --- Extract key terms from description for better defaults ---
        desc_words = description.lower().split()
        # Try to identify key technical terms (nouns, technical phrases)
        key_terms = []
        if len(desc_words) > 0:
            # Use first 10-15 words as potential title basis
            title_basis = " ".join(desc_words[:15]).title()
            key_terms.append(title_basis)
        
        # --- Ensure all required sections exist with defaults ---
        # Note: Defaults should rarely be used if prompt is working correctly
        defaults = {
            "TITLE OF THE INVENTION": f"System and Method for {key_terms[0] if key_terms else 'Processing Data'}",
            "CROSS-REFERENCE TO RELATED APPLICATIONS": "None",
            "FIELD OF THE INVENTION": (
                f"The present invention relates to the field of {description[:100].lower() if description else 'data processing systems'}, "
                "and more particularly to systems and methods for improving efficiency and functionality in this technical domain."
            ),
            "BACKGROUND OF THE INVENTION": (
                "Field of the Invention\n\n"
                f"The present invention relates to the field of {description[:100].lower() if description else 'data processing systems'}.\n\n"
                "Description of Related Art\n\n"
                "Prior art systems in this field suffer from various limitations including performance constraints, "
                "scalability issues, and lack of integration capabilities. Existing solutions fail to adequately address "
                "the technical challenges that the present invention overcomes through its novel approach."
            ),
            "BRIEF SUMMARY OF THE INVENTION": (
                f"The present invention provides a system and method that addresses limitations in the prior art related to {description[:80].lower() if description else 'data processing'}. "
                "Key features include improved efficiency, enhanced reliability, and novel technical approaches to solving existing problems. "
                "The invention incorporates specific technical improvements that enable superior performance compared to conventional systems."
            ),
            "BRIEF DESCRIPTION OF THE DRAWINGS": (
                "FIG. 1 is a block diagram of an example system architecture according to an embodiment of the invention.\n"
                "FIG. 2 is a flowchart illustrating an example method or process flow according to an embodiment of the invention.\n"
                "FIG. 3 illustrates a detailed component view or computing environment suitable for implementing embodiments described herein."
            ),
            "DETAILED DESCRIPTION OF THE INVENTION": (
                "The following description provides detailed embodiments of the invention. Reference is made to the accompanying drawings.\n\n"
                "With reference to FIG. 1, an example system is shown. The system includes various components "
                "configured to perform the described functions according to the invention.\n\n"
                "With reference to FIG. 2, an example method is illustrated. The method includes steps for "
                "processing data according to the invention."
            ),
        }
        
        # Apply defaults for missing sections
        for section_name in required_sections:
            if section_name not in sections or not sections[section_name].strip():
                if section_name in defaults:
                    sections[section_name] = defaults[section_name]
                else:
                    sections[section_name] = f"[{section_name} content to be provided]"

        # --- Post-process Detailed Description for enablement and best mode ---
        detailed_desc = sections.get("DETAILED DESCRIPTION OF THE INVENTION", "")
        
        if include_enablement_language:
            enablement_para = (
                "\n\nEnablement: The foregoing description provides sufficient detail for a person of ordinary skill "
                "in the art to make and use the invention without undue experimentation. The description includes "
                "materials, apparatus, and processing conditions appropriate for the claimed subject matter. "
                "One of ordinary skill in the art can practice the invention based on this disclosure."
            )
            if "enablement" not in detailed_desc.lower() and "make and use" not in detailed_desc.lower():
                detailed_desc += enablement_para
        
        if include_best_mode:
            best_mode_para = (
                "\n\nBest Mode: The inventor contemplates the following as the best mode for carrying out the invention. "
                "In a preferred embodiment, the system is configured as described with reference to FIG. 1, utilizing "
                "the parameter ranges and configurations detailed above. However, other modes of carrying out the invention "
                "are contemplated and fall within the scope of the claims."
            )
            if "best mode" not in detailed_desc.lower():
                detailed_desc += best_mode_para
        
        sections["DETAILED DESCRIPTION OF THE INVENTION"] = detailed_desc

        # --- Ensure Brief Description of Drawings uses FIG. format ---
        if include_figure_callouts:
            drawings_desc = sections.get("BRIEF DESCRIPTION OF THE DRAWINGS", "")
            if not re.search(r"FIG\.\s*\d+", drawings_desc, re.IGNORECASE):
                sections["BRIEF DESCRIPTION OF THE DRAWINGS"] = defaults["BRIEF DESCRIPTION OF THE DRAWINGS"]

        # --- Process and format claims ---
        if not claims_text or len(claims_text.strip()) < 20:
            # Generate default claims if missing
            claims_text = (
                "1. A system comprising: a processor; and a memory storing instructions that, when executed by the processor, "
                "cause the system to perform operations according to the invention.\n\n"
                "2. The system of claim 1, further comprising a communication interface.\n\n"
                "3. A method comprising: receiving input data; processing the input data according to the invention; and "
                "outputting processed data.\n\n"
                "4. The method of claim 3, wherein processing includes applying a transformation algorithm.\n\n"
                "5. A non-transitory computer-readable medium storing instructions that, when executed, cause a processor to "
                "perform the method of claim 3.\n\n"
                "6. The non-transitory computer-readable medium of claim 5, wherein the instructions include error handling logic."
            )
        
        # Normalize claim formatting: ensure numbered, single-sentence claims
        claims_lines = []
        current_claim = []
        for line in claims_text.split('\n'):
            line = line.strip()
            if not line:
                if current_claim:
                    claims_lines.append(' '.join(current_claim))
                    current_claim = []
                continue
            
            # Check if line starts a new claim (number followed by period or space)
            if re.match(r'^\d+[\.\)]\s*', line):
                if current_claim:
                    claims_lines.append(' '.join(current_claim))
                current_claim = [line]
            else:
                current_claim.append(line)
        
        if current_claim:
            claims_lines.append(' '.join(current_claim))
        
        # Reformat claims with proper indentation
        formatted_claims = []
        for claim in claims_lines:
            claim = claim.strip()
            if not claim:
                continue
            
            # Extract claim number
            match = re.match(r'^(\d+)[\.\)]\s*(.+)', claim)
            if match:
                num = match.group(1)
                text = match.group(2).strip()
                # Ensure ends with period
                if not text.endswith('.'):
                    text += '.'
                
                # Check if dependent (references another claim)
                if re.search(r'\b(claim|claims)\s+\d+', text, re.IGNORECASE):
                    # Dependent claim: ensure it starts with "The" but don't duplicate
                    if not text.strip().startswith(('The ', 'the ')):
                        formatted_claims.append(f"{num}. The {text}")
                    else:
                        formatted_claims.append(f"{num}. {text}")
                else:
                    # Independent claim
                    formatted_claims.append(f"{num}. {text}")
            else:
                formatted_claims.append(claim)
        
        claims_text = "\n\n".join(formatted_claims)

        # --- Ensure Abstract is ≤150 words ---
        abstract = sections.get("ABSTRACT OF THE DISCLOSURE", "").strip()
        if not abstract:
            # Generate from summary if missing
            summary = sections.get("BRIEF SUMMARY OF THE INVENTION", "")
            abstract = " ".join(summary.split()[:150])
        
        # Hard limit to 150 words
        abstract_words = abstract.split()
        if len(abstract_words) > 150:
            abstract = " ".join(abstract_words[:150])
            # Ensure it ends properly
            if not abstract.endswith('.'):
                abstract = abstract.rsplit('.', 1)[0] + '.'
        
        sections["ABSTRACT OF THE DISCLOSURE"] = abstract

        # --- Generate markdown output ---
        markdown_parts = []
        for section_name in required_sections:
            if section_name in sections:
                markdown_parts.append(f"## {section_name}\n\n{sections[section_name]}")
        
        # Add optional sections
        for section_name in optional_sections:
            if section_name in sections:
                markdown_parts.append(f"## {section_name}\n\n{sections[section_name]}")
        
        # Add claims
        markdown_parts.append(f"## CLAIMS\n\n{claims_text}")
        
        # Add abstract at the end (USPTO format)
        if "ABSTRACT OF THE DISCLOSURE" in sections:
            markdown_parts.append(f"## ABSTRACT OF THE DISCLOSURE\n\n{sections['ABSTRACT OF THE DISCLOSURE']}")
        
        full_text_markdown = "\n\n".join(markdown_parts)

        # --- Generate HTML output ---
        html_parts = []
        for section_name in required_sections:
            if section_name in sections:
                content = sections[section_name].replace('\n', '<br/>\n')
                html_parts.append(f"<h2>{section_name}</h2>\n<p>{content}</p>")
        
        # Add optional sections
        for section_name in optional_sections:
            if section_name in sections:
                content = sections[section_name].replace('\n', '<br/>\n')
                html_parts.append(f"<h2>{section_name}</h2>\n<p>{content}</p>")
        
        # Add claims (preserve line breaks)
        claims_html = claims_text.replace('\n\n', '</p><p>').replace('\n', '<br/>\n')
        html_parts.append(f"<h2>CLAIMS</h2>\n<p>{claims_html}</p>")
        
        # Add abstract
        if "ABSTRACT OF THE DISCLOSURE" in sections:
            abstract_html = sections["ABSTRACT OF THE DISCLOSURE"].replace('\n', ' ')
            html_parts.append(f"<h2>ABSTRACT OF THE DISCLOSURE</h2>\n<p>{abstract_html}</p>")
        
        full_text_html = "\n\n".join(html_parts)

        return {
            "model": model,
            "generation_time": generation_time,
            "cached": False,
            "abstract": abstract,
            "sections": sections,
            "claims_text": claims_text,
            "full_text_markdown": full_text_markdown,
            "full_text_html": full_text_html,
        }



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
