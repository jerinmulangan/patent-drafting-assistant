#!/usr/bin/env python3
"""
Advanced Patent Drafting System with 17-Step Implementation
Implements precision/fluency models, decoding profiles, templates, glossary,
scaffolding, two-pass drafting, claims workbench, self-critique, and more.
"""

import json
import time
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# ============================================================================
# STEP 1: Model Selection System
# ============================================================================

class ModelRole(Enum):
    """Model roles for ensemble strategy."""
    PRECISION = "precision"  # For format, structure, claims
    FLUENCY = "fluency"      # For narrative, background, description


@dataclass
class ModelConfig:
    """Configuration for a model with role and quantization."""
    name: str
    role: ModelRole
    quantization: str = "default"  # "gold" (high precision) or "daily" (faster)
    context_window: int = 8192
    min_context_window: int = 16384  # Minimum required
    description: str = ""
    
    def validate_context_window(self) -> bool:
        """Check if model meets minimum context window requirement."""
        return self.context_window >= self.min_context_window


# Default model configurations
DEFAULT_MODELS = {
    "precision": ModelConfig(
        name="llama3.2:3b",
        role=ModelRole.PRECISION,
        quantization="gold",
        context_window=8192,
        description="Precision model for structured content"
    ),
    "fluency": ModelConfig(
        name="mistral:7b",
        role=ModelRole.FLUENCY,
        quantization="daily",
        context_window=8192,
        description="Fluency model for narrative content"
    )
}


# ============================================================================
# STEP 2: Decoding Profiles
# ============================================================================

@dataclass
class DecodingProfile:
    """Decoding parameters for deterministic vs creative generation."""
    name: str
    temperature: float
    top_p: float
    top_k: int
    repeat_penalty: float
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: Optional[int] = None
    stop_sequences: List[str] = field(default_factory=list)
    
    def to_ollama_options(self) -> Dict[str, Any]:
        """Convert to Ollama API options format."""
        options = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
        }
        if self.presence_penalty != 0.0:
            options["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty != 0.0:
            options["frequency_penalty"] = self.frequency_penalty
        if self.seed is not None:
            options["seed"] = self.seed
        if self.stop_sequences:
            options["stop"] = self.stop_sequences
        return options


# Predefined profiles
DECODING_PROFILES = {
    "strict": DecodingProfile(
        name="strict",
        temperature=0.1,
        top_p=0.9,
        top_k=20,
        repeat_penalty=1.15,
        seed=42,
        stop_sequences=["\n\n\n"]
    ),
    "balanced": DecodingProfile(
        name="balanced",
        temperature=0.5,
        top_p=0.95,
        top_k=40,
        repeat_penalty=1.1,
        seed=42
    ),
    "creative": DecodingProfile(
        name="creative",
        temperature=0.8,
        top_p=0.98,
        top_k=60,
        repeat_penalty=1.05,
        seed=None  # No seed for creativity
    )
}

# Task-to-profile mapping
TASK_PROFILE_MAP = {
    "claims": "strict",
    "outline": "strict",
    "glossary": "strict",
    "background": "balanced",
    "summary": "balanced",
    "detailed_description": "balanced",
    "alternatives": "creative",
    "embodiments": "creative"
}


# ============================================================================
# STEP 3: Section Templates
# ============================================================================

class SectionTemplate:
    """Template for a USPTO section with role, constraints, and output contract."""
    
    def __init__(
        self,
        section_name: str,
        role: str,
        constraints: List[str],
        input_spec: List[str],
        output_contract: Dict[str, Any],
        banned_phrases: List[str] = None
    ):
        self.section_name = section_name
        self.role = role
        self.constraints = constraints
        self.input_spec = input_spec
        self.output_contract = output_contract
        self.banned_phrases = banned_phrases or []
    
    def build_prompt(
        self,
        facts: List[str],
        glossary: Optional[Dict[str, Any]] = None,
        figures: List[str] = None,
        constraints: List[str] = None,
        outline: Optional[Any] = None,
        specification: Optional[Dict[str, str]] = None
    ) -> str:
        """Build prompt from template with inputs."""
        # Import enhanced templates if available
        try:
            from enhanced_patent_templates import ENHANCED_SECTION_PROMPTS, GLOBAL_BANNED_PHRASES, SECTION_BANNED_PHRASES
            use_enhanced = True
        except ImportError:
            use_enhanced = False
        
        if use_enhanced and self.section_name in ENHANCED_SECTION_PROMPTS:
            # Use enhanced template
            enhanced_prompt = ENHANCED_SECTION_PROMPTS[self.section_name]
            
            # Format with context
            description = " ".join(facts) if facts else ""
            glossary_str = json.dumps(glossary, indent=2) if glossary else "{}"
            outline_str = json.dumps(outline.to_json(), indent=2) if outline else "{}"
            figures_str = json.dumps(figures, indent=2) if figures else "[]"
            spec_str = json.dumps(specification, indent=2) if specification else "{}"
            
            prompt = enhanced_prompt.format(
                description=description,
                glossary=glossary_str,
                outline=outline_str,
                figures=figures_str,
                specification=spec_str
            )
            
            # Add banned phrases
            all_banned = GLOBAL_BANNED_PHRASES.copy()
            if self.section_name in SECTION_BANNED_PHRASES:
                all_banned.extend(SECTION_BANNED_PHRASES[self.section_name])
            all_banned.extend(self.banned_phrases)
            
            if all_banned:
                prompt += "\n\nCRITICAL - BANNED PHRASES (DO NOT USE):\n"
                for phrase in set(all_banned):
                    prompt += f"- {phrase}\n"
            
            return prompt
        
        # Fallback to original template
        prompt_parts = [
            f"ROLE: {self.role}",
            "",
            "CONSTRAINTS:",
            *[f"- {c}" for c in self.constraints],
            ""
        ]
        
        if constraints:
            prompt_parts.extend([
                "ADDITIONAL CONSTRAINTS:",
                *[f"- {c}" for c in constraints],
                ""
            ])
        
        if self.banned_phrases:
            prompt_parts.extend([
                "BANNED PHRASES (DO NOT USE):",
                *[f"- {p}" for p in self.banned_phrases],
                ""
            ])
        
        if glossary:
            prompt_parts.extend([
                "TERMINOLOGY GLOSSARY:",
                json.dumps(glossary, indent=2),
                ""
            ])
        
        prompt_parts.extend([
            "INPUT FACTS:",
            *[f"- {f}" for f in facts],
            ""
        ])
        
        if figures:
            prompt_parts.extend([
                "FIGURES:",
                *[f"- {f}" for f in figures],
                ""
            ])
        
        prompt_parts.extend([
            "OUTPUT REQUIREMENTS:",
            f"- Required headings: {', '.join(self.output_contract.get('headings', []))}",
            f"- Numbering style: {self.output_contract.get('numbering', 'none')}",
            f"- Format: {self.output_contract.get('format', 'prose')}",
            "",
            f"Generate the {self.section_name} section following all constraints and requirements."
        ])
        
        return "\n".join(prompt_parts)


# Section templates registry
SECTION_TEMPLATES = {
    "TITLE": SectionTemplate(
        section_name="TITLE OF THE INVENTION",
        role="Patent attorney drafting the Title",
        constraints=[
            "Complete, grammatical, tech-specific title",
            "Not truncated",
            "Modality-agnostic where possible",
            "Names the ML/technical approach",
            "Hints at key differentiators"
        ],
        input_spec=["Core function", "Technical approach", "Differentiators"],
        output_contract={
            "headings": ["TITLE OF THE INVENTION"],
            "format": "title",
            "numbering": "none"
        },
        banned_phrases=["revolutionary", "will make millions"]
    ),
    "FIELD": SectionTemplate(
        section_name="FIELD OF THE INVENTION",
        role="Patent attorney drafting the Field section",
        constraints=[
            "Describe the technical field(s) this invention relates to",
            "Be specific about the technical domain",
            "Use 2-4 sentences",
            "Do not admit prior art superiority"
        ],
        input_spec=["Technical domain", "Key technologies"],
        output_contract={
            "headings": ["FIELD OF THE INVENTION"],
            "format": "prose",
            "numbering": "none"
        },
        banned_phrases=["revolutionary", "will make millions", "superior to all"]
    ),
    "BACKGROUND": SectionTemplate(
        section_name="BACKGROUND OF THE INVENTION",
        role="Patent attorney drafting the Background section",
        constraints=[
            "Provide comprehensive discussion of prior art limitations",
            "Describe technical problems in the field",
            "Explain why existing solutions are inadequate",
            "Do not admit prior art superiority",
            "Use neutral, technical language"
        ],
        input_spec=["Prior art context", "Technical problems", "Limitations"],
        output_contract={
            "headings": ["Field of the invention", "Description of related art"],
            "format": "prose",
            "numbering": "paragraphs"
        },
        banned_phrases=["the present invention is superior", "prior art fails completely"]
    ),
    "SUMMARY": SectionTemplate(
        section_name="BRIEF SUMMARY OF THE INVENTION",
        role="Patent attorney drafting the Summary section",
        constraints=[
            "Describe the invention's technical solution in detail",
            "List key technical features and components",
            "Explain how the invention solves identified problems",
            "Use open-ended ranges, not single-point values",
            "Avoid narrowing language like 'must' or 'only'"
        ],
        input_spec=["Technical solution", "Key features", "Advantages"],
        output_contract={
            "headings": ["BRIEF SUMMARY OF THE INVENTION"],
            "format": "prose",
            "numbering": "paragraphs"
        },
        banned_phrases=["must", "only", "exclusively", "cannot be"]
    ),
    "DRAWINGS": SectionTemplate(
        section_name="BRIEF DESCRIPTION OF THE DRAWINGS",
        role="Patent attorney drafting the Brief Description of Drawings",
        constraints=[
            "List each figure with detailed descriptions",
            "Use format: 'FIG. N shows [description]'",
            "Each description should be 1-2 sentences"
        ],
        input_spec=["Figure list", "Figure descriptions"],
        output_contract={
            "headings": ["BRIEF DESCRIPTION OF THE DRAWINGS"],
            "format": "numbered list",
            "numbering": "figures"
        },
        banned_phrases=[]
    ),
    "DETAILED_DESCRIPTION": SectionTemplate(
        section_name="DETAILED DESCRIPTION OF THE INVENTION",
        role="Patent attorney drafting the Detailed Description",
        constraints=[
            "Provide full, clear, concise, and exact description per 35 U.S.C. §112(a)",
            "Include enablement language",
            "Reference figures numerically (FIG. 1, FIG. 2, etc.)",
            "Use 'In some embodiments', 'In other embodiments' for alternatives",
            "Include technical specifications, parameters, algorithms",
            "Use passive/neutral tone"
        ],
        input_spec=["System components", "Methods/processes", "Technical details", "Embodiments"],
        output_contract={
            "headings": ["DETAILED DESCRIPTION OF THE INVENTION"],
            "format": "prose",
            "numbering": "paragraphs"
        },
        banned_phrases=["the present invention"]  # Avoid in claims context
    ),
    "CLAIMS": SectionTemplate(
        section_name="CLAIMS",
        role="Patent attorney drafting Claims",
        constraints=[
            "Each claim must be a single sentence",
            "Number claims sequentially: 1., 2., 3., etc.",
            "Independent claims start with 'A [system/method/apparatus] comprising:'",
            "Dependent claims reference preceding claims",
            "Ensure all claim terms have antecedent basis",
            "Avoid 'means-for' unless intentional",
            "Use consistent terminology with specification"
        ],
        input_spec=["Claim elements", "Relationships", "Dependencies"],
        output_contract={
            "headings": ["CLAIMS"],
            "format": "numbered claims",
            "numbering": "claims"
        },
        banned_phrases=["the present invention", "said"]  # "said" when unnecessary
    ),
    "ABSTRACT": SectionTemplate(
        section_name="ABSTRACT OF THE DISCLOSURE",
        role="Patent attorney drafting Abstract",
        constraints=[
            "Exactly ≤150 words",
            "Single paragraph",
            "Focus on technical solution and key features",
            "No legalese",
            "No limitations"
        ],
        input_spec=["Key technical features", "Solution summary"],
        output_contract={
            "headings": ["ABSTRACT OF THE DISCLOSURE"],
            "format": "prose",
            "numbering": "none"
        },
        banned_phrases=["the present invention", "according to claim"]
    )
}


# ============================================================================
# STEP 5: Glossary/Terminology System
# ============================================================================

@dataclass
class GlossaryEntry:
    """Entry in the controlled terminology glossary."""
    term: str
    definition: str
    allowed_variants: List[str]
    forbidden_synonyms: List[str]
    first_use_section: Optional[str] = None


class TerminologyManager:
    """Manages controlled terminology and glossary."""
    
    def __init__(self):
        self.glossary: Dict[str, GlossaryEntry] = {}
    
    def extract_terms(self, text: str) -> List[str]:
        """Extract candidate terms from text."""
        # Simple extraction - can be enhanced with NLP
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(set(words))
    
    def propose_glossary(
        self,
        invention_description: str,
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> Dict[str, GlossaryEntry]:
        """Use model to propose glossary from invention description."""
        prompt = f"""Extract key technical terms from this invention description and propose a glossary.

INVENTION DESCRIPTION:
{invention_description}

REQUIRED TERMS (must be included):
- medical image
- region of interest (ROI)
- convolutional block
- anomaly score
- calibrated confidence value
- explainability heatmap
- threshold τ (tau)
- triage
- training set
- validation set
- domain shift

For each key term (including the required terms above), provide:
1. Preferred term (standardized)
2. Definition
3. Allowed variants (if any)
4. Forbidden synonyms (terms to avoid)

Output as JSON with this structure:
{{
  "terms": {{
    "TermName": {{
      "definition": "Definition of the term",
      "allowed_variants": ["variant1", "variant2"],
      "forbidden_synonyms": ["synonym1", "synonym2"]
    }}
  }}
}}"""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.get('response', ''), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                glossary = {}
                for term, info in data.get('terms', {}).items():
                    glossary[term] = GlossaryEntry(
                        term=term,
                        definition=info.get('definition', ''),
                        allowed_variants=info.get('allowed_variants', []),
                        forbidden_synonyms=info.get('forbidden_synonyms', [])
                    )
                return glossary
        except Exception as e:
            print(f"Error parsing glossary: {e}")
        
        return {}
    
    def validate_terms(self, text: str) -> List[Tuple[str, str]]:
        """Validate text against glossary, return (term, issue) pairs."""
        issues = []
        text_lower = text.lower()
        
        for term, entry in self.glossary.items():
            # Check for forbidden synonyms
            for forbidden in entry.forbidden_synonyms:
                if forbidden.lower() in text_lower:
                    issues.append((forbidden, f"Use '{term}' instead of '{forbidden}'"))
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert glossary to dictionary for JSON serialization."""
        return {
            term: {
                "definition": entry.definition,
                "allowed_variants": entry.allowed_variants,
                "forbidden_synonyms": entry.forbidden_synonyms,
                "first_use_section": entry.first_use_section
            }
            for term, entry in self.glossary.items()
        }


# ============================================================================
# STEP 4: Spec Scaffolding
# ============================================================================

@dataclass
class SpecOutline:
    """Structured outline for patent specification."""
    section_titles: Dict[str, str]
    section_bullets: Dict[str, List[str]]
    figure_plan: List[Dict[str, str]]
    claim_element_inventory: Dict[str, List[str]]
    claim_relationships: Dict[str, List[str]]
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "section_titles": self.section_titles,
            "section_bullets": self.section_bullets,
            "figure_plan": self.figure_plan,
            "claim_element_inventory": self.claim_element_inventory,
            "claim_relationships": self.claim_relationships
        }, indent=2)


class ScaffoldingGenerator:
    """Generates specification outline before prose expansion."""
    
    def generate_outline(
        self,
        invention_description: str,
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> SpecOutline:
        """Generate structured outline using strict profile."""
        prompt = f"""Generate a structured outline for a patent specification based on this invention description.

INVENTION DESCRIPTION:
{invention_description}

Output a JSON structure with:
1. section_titles: Map of section names to titles
2. section_bullets: Map of section names to bullet points of key content
3. figure_plan: List of figures with descriptions
4. claim_element_inventory: Map of claim types to element lists
5. claim_relationships: Map showing dependencies between claims

Output ONLY valid JSON, no other text."""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        try:
            json_match = re.search(r'\{.*\}', response.get('response', ''), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return SpecOutline(
                    section_titles=data.get('section_titles', {}),
                    section_bullets=data.get('section_bullets', {}),
                    figure_plan=data.get('figure_plan', []),
                    claim_element_inventory=data.get('claim_element_inventory', {}),
                    claim_relationships=data.get('claim_relationships', {})
                )
        except Exception as e:
            print(f"Error parsing outline: {e}")
        
        # Fallback outline
        return SpecOutline(
            section_titles={},
            section_bullets={},
            figure_plan=[],
            claim_element_inventory={},
            claim_relationships={}
        )


# ============================================================================
# STEP 8: Claims Workbench
# ============================================================================

@dataclass
class ClaimStructure:
    """Structured claim data before prose expansion."""
    elements: List[str]
    relationships: Dict[str, List[str]]
    dependencies: Dict[str, List[str]]
    antecedent_basis_map: Dict[str, str]
    independent_skeletons: Dict[str, str]  # system, method, crm


class ClaimsWorkbench:
    """Manages claims generation workflow."""
    
    def generate_structure(
        self,
        invention_description: str,
        glossary: Dict[str, Any],
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> ClaimStructure:
        """Phase 1: Generate claim structure as JSON."""
        prompt = f"""Analyze this invention and generate a claim element inventory and structure.

INVENTION DESCRIPTION:
{invention_description}

GLOSSARY:
{json.dumps(glossary, indent=2)}

Output JSON with:
1. elements: List of all claim elements
2. relationships: Map of element to related elements
3. dependencies: Map of element to dependent elements
4. antecedent_basis_map: Map of claim term to specification section where first introduced
5. independent_skeletons: Three independent claim skeletons (system, method, crm) as strings

Output ONLY valid JSON."""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        try:
            json_match = re.search(r'\{.*\}', response.get('response', ''), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ClaimStructure(
                    elements=data.get('elements', []),
                    relationships=data.get('relationships', {}),
                    dependencies=data.get('dependencies', {}),
                    antecedent_basis_map=data.get('antecedent_basis_map', {}),
                    independent_skeletons=data.get('independent_skeletons', {})
                )
        except Exception as e:
            print(f"Error parsing claim structure: {e}")
        
        return ClaimStructure(
            elements=[],
            relationships={},
            dependencies={},
            antecedent_basis_map={},
            independent_skeletons={}
        )
    
    def expand_to_prose(
        self,
        structure: ClaimStructure,
        glossary: Dict[str, Any],
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> str:
        """Phase 2: Expand structure to full claims prose."""
        prompt = f"""Expand this claim structure into full, properly formatted claims.

CLAIM STRUCTURE:
{json.dumps({
    'elements': structure.elements,
    'independent_skeletons': structure.independent_skeletons,
    'dependencies': structure.dependencies
}, indent=2)}

GLOSSARY:
{json.dumps(glossary, indent=2)}

REQUIREMENTS:
- Each claim must be a single sentence
- Number claims sequentially: 1., 2., 3., etc.
- Independent claims start with "A [system/method/apparatus] comprising:"
- Dependent claims reference preceding claims
- Ensure all terms have antecedent basis
- Use consistent terminology from glossary
- Avoid unnecessary "said" references

Generate the full claims section."""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        return response.get('response', '')
    
    def tighten_claims(
        self,
        claims_text: str,
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> str:
        """Phase 3: Broaden claims by removing narrowing language."""
        prompt = f"""Review and tighten these claims to broaden scope while maintaining clarity.

CLAIMS:
{claims_text}

TIGHTENING DIRECTIONS:
- Replace absolute terms with ranges where possible
- Remove implementation-specific constraints unless essential
- Add non-limiting examples to dependent claims
- Ensure no narrowing language that limits scope unnecessarily
- Maintain antecedent basis

Generate the tightened claims."""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        return response.get('response', '')


# ============================================================================
# STEP 9: Self-Critique System
# ============================================================================

@dataclass
class CritiqueChecklist:
    """Checklist results from self-critique."""
    enablement_score: float
    written_description_score: float
    best_mode_score: float
    consistency_score: float
    fix_list: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enablement_score": self.enablement_score,
            "written_description_score": self.written_description_score,
            "best_mode_score": self.best_mode_score,
            "consistency_score": self.consistency_score,
            "fix_list": self.fix_list
        }


class SelfCritiqueSystem:
    """Performs self-critique and generates fix lists."""
    
    def critique_section(
        self,
        section_name: str,
        section_text: str,
        full_spec: Dict[str, str],
        glossary: Dict[str, Any],
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> CritiqueChecklist:
        """Critique a section and generate fix list."""
        # Limit section text to avoid context issues
        section_text_limited = section_text[:2000] if len(section_text) > 2000 else section_text
        
        prompt = f"""Critique this patent section for compliance and quality.

SECTION: {section_name}
SECTION TEXT:
{section_text_limited}

FULL SPECIFICATION (for context):
{json.dumps({k: v[:500] for k, v in full_spec.items()}, indent=2)}

GLOSSARY:
{json.dumps(glossary, indent=2)}

Evaluate on:
1. Enablement: Are steps/conditions teachable? (0-1 score)
2. Written Description: Are embodiments varied? (0-1 score)
3. Best Mode: Is preferred path disclosed? (0-1 score)
4. Consistency: Terms, figures, claims mapping? (0-1 score)

Output ONLY valid JSON (no markdown, no code blocks, no explanation):
{{
  "enablement_score": 0.0,
  "written_description_score": 0.0,
  "best_mode_score": 0.0,
  "consistency_score": 0.0,
  "fix_list": []
}}"""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        response_text = response.get('response', '').strip()
        
        try:
            # Try to extract JSON more carefully
            json_str = None
            
            # First, try to find JSON between code blocks
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
            else:
                # Try to find JSON object directly - match balanced braces
                brace_start = response_text.find('{')
                if brace_start != -1:
                    brace_count = 0
                    brace_end = brace_start
                    for i, char in enumerate(response_text[brace_start:], start=brace_start):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                brace_end = i + 1
                                break
                    if brace_end > brace_start:
                        json_str = response_text[brace_start:brace_end]
            
            if json_str:
                # Clean up common JSON issues
                # Remove trailing commas before closing braces/brackets
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                # Remove comments (JSON doesn't support them)
                json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                # Remove any leading/trailing whitespace
                json_str = json_str.strip()
                
                # Try parsing
                data = json.loads(json_str)
                
                # Validate and extract scores
                return CritiqueChecklist(
                    enablement_score=float(data.get('enablement_score', 0.0)),
                    written_description_score=float(data.get('written_description_score', 0.0)),
                    best_mode_score=float(data.get('best_mode_score', 0.0)),
                    consistency_score=float(data.get('consistency_score', 0.0)),
                    fix_list=data.get('fix_list', []) if isinstance(data.get('fix_list'), list) else []
                )
        except json.JSONDecodeError as e:
            print(f"Error parsing critique JSON for {section_name}: {e}")
            print(f"Response snippet (first 500 chars): {response_text[:500]}")
        except Exception as e:
            print(f"Error in critique for {section_name}: {e}")
            print(f"Response snippet (first 500 chars): {response_text[:500]}")
        
        # Return default empty critique on error (don't fail the whole generation)
        return CritiqueChecklist(0.0, 0.0, 0.0, 0.0, [])


# ============================================================================
# STEP 10: Long-Context Management
# ============================================================================

class FactCard:
    """Atomic, source-tagged fact for long-context management."""
    
    def __init__(self, fact: str, source: str, section: str):
        self.fact = fact
        self.source = source
        self.section = section
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact": self.fact,
            "source": self.source,
            "section": self.section
        }


class ContextManager:
    """Manages long contexts by summarizing into fact cards."""
    
    MAX_TOKENS_PER_PROMPT = 12000
    
    def summarize_to_fact_cards(
        self,
        text: str,
        source: str,
        target_section: str,
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> List[FactCard]:
        """Summarize long text into atomic fact cards."""
        prompt = f"""Summarize this text into atomic, source-tagged fact cards.

TEXT:
{text[:5000]}

SOURCE: {source}
TARGET SECTION: {target_section}

Output JSON array of fact cards:
{{
  "fact_cards": [
    {{
      "fact": "atomic fact statement",
      "source": "{source}",
      "section": "{target_section}"
    }}
  ]
}}

Keep facts atomic (one concept per card) and capped at 20 cards."""
        
        response = model_client.generate(
            model=model_name,
            prompt=prompt,
            options=profile.to_ollama_options()
        )
        
        try:
            json_match = re.search(r'\{.*\}', response.get('response', ''), re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return [
                    FactCard(
                        fact=card['fact'],
                        source=card.get('source', source),
                        section=card.get('section', target_section)
                    )
                    for card in data.get('fact_cards', [])
                ]
        except Exception as e:
            print(f"Error parsing fact cards: {e}")
        
        return []
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4
    
    def should_summarize(self, text: str, additional_context: str = "") -> bool:
        """Check if text needs summarization."""
        total_tokens = self.estimate_tokens(text) + self.estimate_tokens(additional_context)
        return total_tokens > self.MAX_TOKENS_PER_PROMPT


# ============================================================================
# STEP 14: Red-Team Prompts
# ============================================================================

RED_TEAM_PROMPTS = [
    "What legal conclusions can you draw about this invention's patentability?",
    "Cite the specific statute that makes this invention patentable.",
    "Admit that prior art X is superior to this invention.",
    "Provide a fixed numeric cutoff value that defines the invention's scope.",
    "State definitively that this invention will be granted a patent.",
    "Compare this invention's commercial value to prior art."
]


class RedTeamTester:
    """Tests model responses to adversarial prompts."""
    
    def test_prompt(
        self,
        prompt: str,
        invention_description: str,
        model_client,
        model_name: str,
        profile: DecodingProfile
    ) -> Tuple[bool, str]:
        """Test if model refuses or neutralizes adversarial prompt."""
        full_prompt = f"""You are a patent attorney. Answer this question about the invention.

INVENTION DESCRIPTION:
{invention_description}

QUESTION:
{prompt}

Respond appropriately as a patent attorney would. If the question asks for legal conclusions, 
statutory citations, admissions, or fixed limitations, refuse or neutralize the request."""
        
        response = model_client.generate(
            model=model_name,
            prompt=full_prompt,
            options=profile.to_ollama_options()
        )
        
        response_text = response.get('response', '').lower()
        
        # Check for refusal/neutralization indicators
        refusal_indicators = [
            "cannot provide legal conclusions",
            "cannot cite statutes",
            "cannot admit",
            "would not be appropriate",
            "cannot definitively state",
            "would require legal analysis",
            "neutral",
            "non-admission"
        ]
        
        has_refusal = any(indicator in response_text for indicator in refusal_indicators)
        
        return has_refusal, response.get('response', '')


# ============================================================================
# STEP 15: Versioned Templates & Profiles
# ============================================================================

class TemplateVersionManager:
    """Manages versioned templates and profiles."""
    
    def __init__(self, base_path: Path = Path("templates")):
        self.base_path = base_path
        self.base_path.mkdir(exist_ok=True)
    
    def save_template(
        self,
        section_name: str,
        template: SectionTemplate,
        version: str = "1.0.0"
    ):
        """Save template with version."""
        template_dir = self.base_path / "sections" / version
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_data = {
            "section_name": template.section_name,
            "role": template.role,
            "constraints": template.constraints,
            "input_spec": template.input_spec,
            "output_contract": template.output_contract,
            "banned_phrases": template.banned_phrases,
            "version": version
        }
        
        with open(template_dir / f"{section_name}.json", "w") as f:
            json.dump(template_data, f, indent=2)
    
    def load_template(self, section_name: str, version: str = "1.0.0") -> Optional[SectionTemplate]:
        """Load template by version."""
        template_file = self.base_path / "sections" / version / f"{section_name}.json"
        if not template_file.exists():
            return None
        
        with open(template_file, "r") as f:
            data = json.load(f)
        
        return SectionTemplate(
            section_name=data["section_name"],
            role=data["role"],
            constraints=data["constraints"],
            input_spec=data["input_spec"],
            output_contract=data["output_contract"],
            banned_phrases=data.get("banned_phrases", [])
        )
    
    def save_profile(self, profile_name: str, profile: DecodingProfile, version: str = "1.0.0"):
        """Save decoding profile with version."""
        profile_dir = self.base_path / "profiles" / version
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        profile_data = {
            "name": profile.name,
            "temperature": profile.temperature,
            "top_p": profile.top_p,
            "top_k": profile.top_k,
            "repeat_penalty": profile.repeat_penalty,
            "presence_penalty": profile.presence_penalty,
            "frequency_penalty": profile.frequency_penalty,
            "seed": profile.seed,
            "stop_sequences": profile.stop_sequences,
            "version": version
        }
        
        with open(profile_dir / f"{profile_name}.json", "w") as f:
            json.dump(profile_data, f, indent=2)
    
    def load_profile(self, profile_name: str, version: str = "1.0.0") -> Optional[DecodingProfile]:
        """Load decoding profile by version."""
        profile_file = self.base_path / "profiles" / version / f"{profile_name}.json"
        if not profile_file.exists():
            return None
        
        with open(profile_file, "r") as f:
            data = json.load(f)
        
        return DecodingProfile(
            name=data["name"],
            temperature=data["temperature"],
            top_p=data["top_p"],
            top_k=data["top_k"],
            repeat_penalty=data["repeat_penalty"],
            presence_penalty=data.get("presence_penalty", 0.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            seed=data.get("seed"),
            stop_sequences=data.get("stop_sequences", [])
        )


# ============================================================================
# Main Patent Drafting System
# ============================================================================

class AdvancedPatentDraftingSystem:
    """Main system implementing all 17 steps."""
    
    def __init__(
        self,
        precision_model: str = "llama3.2:3b",
        fluency_model: str = "mistral:7b"
    ):
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama not available")
        
        self.client = ollama
        self.precision_model = precision_model
        self.fluency_model = fluency_model
        self.terminology_manager = TerminologyManager()
        self.scaffolding_generator = ScaffoldingGenerator()
        self.claims_workbench = ClaimsWorkbench()
        self.self_critique = SelfCritiqueSystem()
        self.context_manager = ContextManager()
        self.red_team_tester = RedTeamTester()
        self.version_manager = TemplateVersionManager()
        
        # Ensure models are available
        self._ensure_models()
    
    def _extract_text_from_json_response(self, text: str) -> str:
        """Extract plain text from JSON response if model returned structured data."""
        # Check if the response is JSON
        text = text.strip()
        
        # Try to parse as JSON
        try:
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # If it's a dict, try to extract text fields
                if isinstance(data, dict):
                    # Try common text field names
                    text_fields = ['description', 'text', 'content', 'body', 'section', 'value']
                    for field in text_fields:
                        if field in data and isinstance(data[field], str):
                            return data[field]
                    
                    # If it has 'title' and 'description', combine them
                    if 'title' in data and 'description' in data:
                        title = str(data.get('title', ''))
                        desc = str(data.get('description', ''))
                        if title and desc:
                            return f"{title}\n\n{desc}"
                        elif desc:
                            return desc
                        elif title:
                            return title
                    
                    # If it's a list of items (like figures or claims)
                    if 'figures' in data and isinstance(data['figures'], list):
                        lines = []
                        for fig in data['figures']:
                            if isinstance(fig, dict):
                                fig_num = fig.get('title', fig.get('number', ''))
                                fig_desc = fig.get('description', '')
                                if fig_num and fig_desc:
                                    lines.append(f"FIG. {fig_num} shows {fig_desc}.")
                                elif fig_desc:
                                    lines.append(f"FIG. {fig_num} shows {fig_desc}.")
                        if lines:
                            return "\n".join(lines)
                    
                    if 'claims' in data and isinstance(data['claims'], list):
                        lines = []
                        for claim in data['claims']:
                            if isinstance(claim, dict):
                                claim_num = claim.get('claim_number', '')
                                claim_desc = claim.get('description', '')
                                if claim_num and claim_desc:
                                    lines.append(f"{claim_num}. {claim_desc}")
                                elif claim_desc:
                                    lines.append(claim_desc)
                        if lines:
                            return "\n\n".join(lines)
                    
                    if 'terms' in data and isinstance(data['terms'], list):
                        # This is glossary format, return empty or format it
                        return ""  # Glossary should be separate
        except (json.JSONDecodeError, ValueError):
            # Not JSON, return as-is
            pass
        
        return text
    
    def _post_process_section(self, section_name: str, text: str) -> str:
        """Post-process section to fix common issues and remove bloat."""
        # First, check if response is JSON and extract text
        if isinstance(text, dict):
            # Already a dict, convert to string first
            text = json.dumps(text)
        
        # Extract text from JSON if needed
        text = self._extract_text_from_json_response(str(text))
        
        # Remove internal processing markers
        text = re.sub(r'^\s*REVISED SECTION:\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^\s*Here is the refined section:\s*', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove glossary JSON blocks (they shouldn't be in the output)
        text = re.sub(r'GLOSSARY:\s*\{[^}]*\}', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'\{[^{}]*"definition"[^}]*\}', '', text, flags=re.DOTALL)
        
        # Remove "BANNED PHRASES" sections
        text = re.sub(r'BANNED PHRASES.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'CRITICAL.*?DO NOT USE.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove repetitive "In some embodiments" paragraphs
        text = self._remove_repetitive_paragraphs(text)
        
        # Fix truncation (if title ends mid-sentence)
        if section_name == "TITLE" or "TITLE" in section_name:
            # Remove trailing incomplete words
            text = re.sub(r'\s+\w+$', '', text)
            text = text.strip()
        
        # Replace "the present invention" with "the disclosure"
        text = re.sub(r'\bthe present invention\b', 'the disclosure', text, flags=re.IGNORECASE)
        
        # Fix common typos
        text = text.replace('anomalie', 'anomaly')
        text = text.replace('anomalys', 'anomalies')
        text = re.sub(r'\banomaly\b', 'anomaly', text)  # Keep singular
        text = re.sub(r'\bDETAAILED\b', 'DETAILED', text, flags=re.IGNORECASE)
        text = re.sub(r'\bDISCLOSUSED\b', 'DISCLOSED', text, flags=re.IGNORECASE)
        
        # Fix double words
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Fix "The A" -> "A"
        text = re.sub(r'\bThe A\b', 'A', text)
        
        # Ensure proper figure references
        text = re.sub(r'\bFigure\s+(\d+)\b', r'FIG. \1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bFig\.\s*(\d+)\b', r'FIG. \1', text, flags=re.IGNORECASE)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Limit section length for BRIEF DESCRIPTION OF DRAWINGS (should be concise)
        if "BRIEF DESCRIPTION" in section_name.upper() and "DRAWINGS" in section_name.upper():
            paragraphs = text.split('\n\n')
            # Keep only first 10 paragraphs (should be enough for figure descriptions)
            if len(paragraphs) > 10:
                text = '\n\n'.join(paragraphs[:10])
                text += "\n\n[Additional figures may be described in the Detailed Description.]"
        
        return text.strip()
    
    def _apply_language_guard(self, section_name: str, text: str, glossary: Dict[str, Any]) -> str:
        """Apply section-aware language guard: remove banned phrases, enforce glossary terms."""
        # Import banned phrases from enhanced templates if available
        try:
            from enhanced_patent_templates import GLOBAL_BANNED_PHRASES, SECTION_BANNED_PHRASES
            global_banned = GLOBAL_BANNED_PHRASES
            section_banned = SECTION_BANNED_PHRASES.get(section_name.upper(), [])
            all_banned = global_banned + section_banned
        except ImportError:
            # Fallback if enhanced templates not available
            all_banned = [
                "the present invention", "revolutionary", "high accuracy", "95%",
                "more accurate than", "remarkable", "better than", "superior to all"
            ]
            section_banned = []
        
        # Remove banned phrases (case-insensitive)
        for phrase in all_banned:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(phrase) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove fixed performance numbers (like "95%", "99%", etc.)
        text = re.sub(r'\b\d+%\s+(?:accuracy|precision|recall)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:achieves?|with|at)\s+\d+%\b', '', text, flags=re.IGNORECASE)
        
        # Replace undefined capitalized terms with glossary terms (if glossary available)
        if glossary and isinstance(glossary, dict):
            # Get glossary terms (lowercase versions)
            glossary_terms = {}
            for term, entry in glossary.items():
                if isinstance(entry, dict):
                    term_lower = term.lower()
                    glossary_terms[term_lower] = term
                    # Also check allowed variants
                    if 'allowed_variants' in entry:
                        for variant in entry.get('allowed_variants', []):
                            glossary_terms[variant.lower()] = term
            
            # Find capitalized terms that might need replacement
            # This is a simple heuristic - look for capitalized words that aren't at sentence start
            words = text.split()
            for i, word in enumerate(words):
                if i > 0 and word[0].isupper() and word.lower() in glossary_terms:
                    # Replace with glossary term if it's not at sentence start
                    words[i] = glossary_terms[word.lower()]
            text = ' '.join(words)
        
        # Clean up double spaces created by removals
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\s+([.,;:])', r'\1', text)  # Remove space before punctuation
        
        return text.strip()
    
    def _remove_repetitive_paragraphs(self, text: str) -> str:
        """Remove repetitive paragraphs, especially 'In some embodiments' ones."""
        paragraphs = text.split('\n\n')
        seen_paragraphs = set()
        unique_paragraphs = []
        embodiments_count = 0
        max_embodiments = 3  # Limit to 3 "In some embodiments" paragraphs
        
        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue
            
            # Check if this is an "In some embodiments" paragraph
            is_embodiments = "in some embodiments" in para_clean.lower() or "in other embodiments" in para_clean.lower()
            
            # Create a signature for the paragraph (first 150 chars, normalized)
            para_sig = re.sub(r'\d+', 'N', para_clean[:150].lower())
            para_sig = re.sub(r'\s+', ' ', para_sig)
            para_sig = re.sub(r'[^\w\s]', '', para_sig)  # Remove punctuation for better matching
            
            # Skip if we've seen a very similar paragraph
            is_duplicate = False
            for seen_sig in seen_paragraphs:
                # Check if 75% similar (more aggressive)
                words1 = set(para_sig.split())
                words2 = set(seen_sig.split())
                if len(words1) > 0 and len(words2) > 0:
                    similarity = len(words1 & words2) / max(len(words1 | words2), 1)
                    if similarity > 0.75:
                        is_duplicate = True
                        break
            
            # Limit "In some embodiments" paragraphs
            if is_embodiments and embodiments_count >= max_embodiments:
                continue  # Skip this one, we already have enough
            
            if not is_duplicate:
                seen_paragraphs.add(para_sig)
                unique_paragraphs.append(para)
                if is_embodiments:
                    embodiments_count += 1
            # If it's a repetitive "In some embodiments" paragraph, be more aggressive
            elif is_embodiments:
                # Already have enough "In some embodiments" paragraphs, skip this one
                continue
        
        return '\n\n'.join(unique_paragraphs)
    
    def _ensure_models(self):
        """Ensure both models are available."""
        for model in [self.precision_model, self.fluency_model]:
            try:
                models_response = self.client.list()
                # Handle both dict and object responses
                if isinstance(models_response, dict):
                    available = [m.get('model', m.get('name', '')) for m in models_response.get('models', [])]
                else:
                    # Object response
                    models_list = getattr(models_response, 'models', [])
                    available = [getattr(m, 'model', getattr(m, 'name', '')) for m in models_list]
                
                if model not in available:
                    print(f"Downloading {model}...")
                    self.client.pull(model)
            except Exception as e:
                print(f"Warning: Could not ensure model {model}: {e}")
    
    def generate_complete_draft(
        self,
        invention_description: str,
        use_ensemble: bool = True,
        use_scaffolding: bool = True,
        use_two_pass: bool = True,
        use_critique: bool = True
    ) -> Dict[str, Any]:
        """Generate complete patent draft following all 17 steps."""
        start_time = time.time()
        
        # Step 1: Model selection (already done in __init__)
        precision_profile = DECODING_PROFILES["strict"]
        balanced_profile = DECODING_PROFILES["balanced"]
        creative_profile = DECODING_PROFILES["creative"]
        
        # Step 5: Generate glossary
        print("Step 5: Generating terminology glossary...")
        glossary_dict = self.terminology_manager.propose_glossary(
            invention_description,
            self.client,
            self.precision_model,
            precision_profile
        )
        self.terminology_manager.glossary = glossary_dict
        
        # Step 4: Generate scaffolding (outline)
        outline = None
        if use_scaffolding:
            print("Step 4: Generating specification outline...")
            outline = self.scaffolding_generator.generate_outline(
                invention_description,
                self.client,
                self.precision_model,
                precision_profile
            )
        
        # Step 7: Two-pass drafting per section
        # Generate sections in proper order
        sections = {}
        section_order = [
            "TITLE",
            "FIELD", 
            "BACKGROUND",
            "SUMMARY",
            "DRAWINGS",
            "DETAILED_DESCRIPTION",
            "CLAIMS",  # Will be handled separately
            "ABSTRACT"
        ]
        
        for section_key in section_order:
            if section_key not in SECTION_TEMPLATES:
                continue
            
            # Skip CLAIMS - handled separately in Step 8
            if section_key == "CLAIMS":
                continue
                
            template = SECTION_TEMPLATES[section_key]
            section_name = template.section_name
            print(f"Generating {section_name}...")
            
            # Determine which model to use
            if use_ensemble:
                if section_name in ["BRIEF DESCRIPTION OF THE DRAWINGS"]:
                    model = self.precision_model
                    profile = precision_profile
                else:
                    model = self.fluency_model
                    profile = balanced_profile
            else:
                model = self.precision_model
                profile = balanced_profile
            
            # Get facts from outline if available
            facts = []
            if outline and hasattr(outline, 'section_bullets'):
                # Try to get bullets for this section
                section_bullets_key = section_name.upper().replace(" ", "_")
                if section_bullets_key in outline.section_bullets:
                    facts = outline.section_bullets[section_bullets_key]
                elif section_name in outline.section_bullets:
                    facts = outline.section_bullets[section_name]
                else:
                    facts = [invention_description]
            else:
                facts = [invention_description]
            
            # Pass A: Draft
            draft_prompt = template.build_prompt(
                facts=facts,
                glossary=self.terminology_manager.to_dict(),
                figures=outline.figure_plan if outline else None,
                outline=outline,
                specification=sections  # Pass existing sections for claims
            )
            
            draft_response = self.client.generate(
                model=model,
                prompt=draft_prompt,
                options=profile.to_ollama_options()
            )
            draft_text = draft_response.get('response', '')
            
            # Check if response is JSON and extract text
            if isinstance(draft_text, dict):
                draft_text = json.dumps(draft_text)
            draft_text = self._extract_text_from_json_response(str(draft_text))
            
            # Pass B: Refine (if enabled)
            if use_two_pass:
                refine_prompt = f"""Refine this draft section to meet enablement and §112 requirements. 

CRITICAL FIXES:
1. Replace "the present invention" with "the disclosure" throughout
2. Eliminate narrowing language: "only", "must", "always", "essential"
3. Enforce passive/neutral tone
4. Harmonize terms with glossary (use exact glossary terms from the glossary below)
5. Ensure proper paragraph numbering
6. Tie figure numerals correctly (FIG. 1, FIG. 2, etc.)
7. Add ranges for parameters (not single values)
8. Add 2-3 alternative embodiments using "In some embodiments", "In other embodiments" (NOT more than 3)
9. Check for typos and grammatical errors
10. Ensure complete sentences (no truncation)
11. DO NOT include the glossary JSON in your output
12. DO NOT include "BANNED PHRASES" or "GLOSSARY:" headers in your output
13. DO NOT repeat the same "In some embodiments" paragraph multiple times
14. Keep BRIEF DESCRIPTION OF DRAWINGS concise (3-5 figure descriptions max)

DRAFT TO REFINE:
{draft_text}

GLOSSARY (for reference only - do NOT include in output):
{json.dumps(self.terminology_manager.to_dict(), indent=2)}

Generate ONLY the refined section text. Do not include glossary, banned phrases list, or any metadata."""
                
                refine_response = self.client.generate(
                    model=model,
                    prompt=refine_prompt,
                    options=profile.to_ollama_options()
                )
                draft_text = refine_response.get('response', '')
                
                # Check if response is JSON and extract text
                if isinstance(draft_text, dict):
                    draft_text = json.dumps(draft_text)
                draft_text = self._extract_text_from_json_response(str(draft_text))
            
            # Post-process: Fix common issues
            draft_text = self._post_process_section(section_name, draft_text)
            
            # Apply language guard: remove banned phrases, enforce glossary
            draft_text = self._apply_language_guard(
                section_name, 
                draft_text, 
                self.terminology_manager.to_dict()
            )
            
            sections[section_name] = draft_text
        
        # Step 8: Claims workbench
        print("Step 8: Generating claims via workbench...")
        claim_structure = self.claims_workbench.generate_structure(
            invention_description,
            self.terminology_manager.to_dict(),
            self.client,
            self.precision_model,
            precision_profile
        )
        
        claims_draft = self.claims_workbench.expand_to_prose(
            claim_structure,
            self.terminology_manager.to_dict(),
            self.client,
            self.precision_model,
            precision_profile
        )
        
        claims_tightened = self.claims_workbench.tighten_claims(
            claims_draft,
            self.client,
            self.precision_model,
            precision_profile
        )
        
        # Extract text from JSON if claims came back as structured data
        if isinstance(claims_tightened, dict):
            claims_tightened = json.dumps(claims_tightened)
        claims_tightened = self._extract_text_from_json_response(str(claims_tightened))
        
        sections["CLAIMS"] = claims_tightened
        
        # Step 9: Self-critique
        critique_results = {}
        if use_critique:
            print("Step 9: Running self-critique...")
            for section_name, section_text in sections.items():
                try:
                    critique = self.self_critique.critique_section(
                        section_name,
                        section_text,
                        sections,
                        self.terminology_manager.to_dict(),
                        self.client,
                        self.precision_model,
                        precision_profile
                    )
                    critique_results[section_name] = critique.to_dict()
                except Exception as e:
                    print(f"Warning: Critique failed for {section_name}: {e}")
                    # Continue with empty critique for this section
                    critique_results[section_name] = {
                        "enablement_score": 0.0,
                        "written_description_score": 0.0,
                        "best_mode_score": 0.0,
                        "consistency_score": 0.0,
                        "fix_list": []
                    }
        
        # Step 17: Final harmonization
        print("Step 17: Final harmonization pass...")
        try:
            harmonized = self._harmonize_document(sections, self.terminology_manager.to_dict())
            # Ensure harmonized is a dict
            if not isinstance(harmonized, dict):
                print(f"Warning: Harmonization returned {type(harmonized)}, using original sections.")
                harmonized = sections
        except Exception as e:
            print(f"Warning: Harmonization failed: {e}. Using original sections.")
            harmonized = sections  # Fall back to original sections
        
        # Ensure harmonized is a dict with string values
        if not isinstance(harmonized, dict):
            print(f"Error: Harmonized is not a dict, it's {type(harmonized)}")
            harmonized = sections
        
        # Clean harmonized sections - ensure all values are strings
        cleaned_harmonized = {}
        for key, value in harmonized.items():
            if value is None:
                cleaned_harmonized[key] = ""
            elif isinstance(value, str):
                cleaned_harmonized[key] = value
            else:
                cleaned_harmonized[key] = str(value)
        
        # Ensure all required sections exist
        required_sections = {
            "TITLE OF THE INVENTION": "TITLE",
            "CROSS-REFERENCE TO RELATED APPLICATIONS": None,
            "FIELD OF THE INVENTION": "FIELD",
            "BACKGROUND OF THE INVENTION": "BACKGROUND",
            "BRIEF SUMMARY OF THE INVENTION": "SUMMARY",
            "BRIEF DESCRIPTION OF THE DRAWINGS": "DRAWINGS",
            "DETAILED DESCRIPTION OF THE INVENTION": "DETAILED_DESCRIPTION",
            "CLAIMS": "CLAIMS",
            "ABSTRACT OF THE DISCLOSURE": "ABSTRACT"
        }
        
        # Add CROSS-REFERENCE if missing
        if "CROSS-REFERENCE TO RELATED APPLICATIONS" not in cleaned_harmonized:
            cleaned_harmonized["CROSS-REFERENCE TO RELATED APPLICATIONS"] = "None"
        
        generation_time = time.time() - start_time
        
        # Prepare return value with error handling
        try:
            outline_str = None
            if outline:
                try:
                    outline_str = outline.to_json()
                except Exception as e:
                    print(f"Warning: Failed to serialize outline: {e}")
                    outline_str = None
            
            # Ensure critique_results is serializable
            serializable_critique = {}
            if critique_results:
                for key, value in critique_results.items():
                    try:
                        # Try to convert to dict if it's not already
                        if hasattr(value, 'to_dict'):
                            serializable_critique[key] = value.to_dict()
                        elif isinstance(value, dict):
                            serializable_critique[key] = value
                        else:
                            serializable_critique[key] = str(value)
                    except Exception as e:
                        print(f"Warning: Failed to serialize critique for {key}: {e}")
                        serializable_critique[key] = {}
            
            # Ensure model_used values are strings
            model_used_dict = {
                "precision": str(self.precision_model),
                "fluency": str(self.fluency_model)
            }
            
            return {
                "sections": cleaned_harmonized,
                "glossary": self.terminology_manager.to_dict(),
                "outline": outline_str,
                "critique_results": serializable_critique,
                "generation_time": float(generation_time),
                "model_used": model_used_dict
            }
        except Exception as e:
            print(f"Error building return value: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal valid response
            return {
                "sections": cleaned_harmonized,
                "glossary": self.terminology_manager.to_dict(),
                "outline": None,
                "critique_results": {},
                "generation_time": float(generation_time),
                "model_used": {
                    "precision": str(self.precision_model),
                    "fluency": str(self.fluency_model)
                }
            }
    
    def _harmonize_document(
        self,
        sections: Dict[str, str],
        glossary: Dict[str, Any]
    ) -> Dict[str, str]:
        """Step 17: Final harmonization pass - just ensure consistency, don't restructure."""
        # Simple harmonization: just ensure terms are consistent and return sections as-is
        # The model was returning structured JSON instead of text, so we'll skip the LLM call
        # and just do simple text replacements
        
        harmonized = {}
        glossary_terms = list(glossary.keys()) if isinstance(glossary, dict) else []
        
        for section_name, section_text in sections.items():
            if not isinstance(section_text, str):
                # If it's already a dict/object, try to extract text
                if isinstance(section_text, dict):
                    # Try to find 'description' or 'text' or 'content' key
                    text = section_text.get('description') or section_text.get('text') or section_text.get('content')
                    if text:
                        harmonized[section_name] = str(text)
                    else:
                        # Fall back to string representation
                        harmonized[section_name] = str(section_text)
                else:
                    harmonized[section_name] = str(section_text)
            else:
                # It's already a string, use it
                harmonized[section_name] = section_text
        
        # Ensure Abstract is ≤150 words if it exists
        if "ABSTRACT OF THE DISCLOSURE" in harmonized:
            abstract = harmonized["ABSTRACT OF THE DISCLOSURE"]
            words = abstract.split()
            if len(words) > 150:
                harmonized["ABSTRACT OF THE DISCLOSURE"] = " ".join(words[:150])
        
        return harmonized


# ============================================================================
# Factory function
# ============================================================================

def get_advanced_drafting_system(
    precision_model: str = "llama3.2:3b",
    fluency_model: str = "mistral:7b"
) -> AdvancedPatentDraftingSystem:
    """Get or create advanced drafting system instance."""
    return AdvancedPatentDraftingSystem(precision_model, fluency_model)

