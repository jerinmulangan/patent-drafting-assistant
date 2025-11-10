# Advanced Patent Drafting System - 17-Step Implementation

This document describes the comprehensive 17-step patent drafting system that implements precision/fluency model ensembles, decoding profiles, section templates, scaffolding, glossary management, two-pass drafting, claims workbench, self-critique, and more.

## Overview

The advanced drafting system (`patent_drafting_system.py`) implements a sophisticated workflow for generating USPTO-compliant patent drafts with:

- **Model Selection**: Precision model for structured content, fluency model for narrative
- **Decoding Profiles**: Strict, balanced, and creative profiles with fixed parameters
- **Section Templates**: Reusable templates for all USPTO sections
- **Spec Scaffolding**: Outline-first approach before prose expansion
- **Terminology Control**: Glossary system for consistent terminology
- **Safe Language Guards**: Banned phrase detection per section
- **Two-Pass Drafting**: Draft then refine for each section
- **Claims Workbench**: Structure → prose → tighten workflow
- **Self-Critique**: Automated quality checking
- **Long-Context Management**: Fact card summarization
- **Model Ensemble**: Strategic use of precision/fluency models
- **Evaluation Harness**: Automated rubric-based evaluation
- **Red-Team Testing**: Adversarial prompt testing
- **Versioned Templates**: Template and profile versioning
- **Final Harmonization**: Document-wide consistency pass

## Architecture

### Core Components

1. **AdvancedPatentDraftingSystem** (`patent_drafting_system.py`)
   - Main orchestrator implementing all 17 steps
   - Manages model selection, profiles, templates, glossary, etc.

2. **EvaluationHarness** (`evaluation_harness.py`)
   - Automated evaluation against rubric
   - Checks section presence, ordering, banned phrases, glossary compliance, etc.

3. **API Integration** (`api_endpoints.py`)
   - `/generate_draft_advanced` endpoint
   - Exposes full 17-step system via REST API

## Step-by-Step Implementation

### Step 1: Model Selection
- **Precision Model**: Used for claims, outline, glossary, brief description of drawings
- **Fluency Model**: Used for background, detailed description, alternatives
- Both models must have ≥16k context window
- Models are validated on initialization

### Step 2: Decoding Profiles
Three predefined profiles:
- **Strict**: temperature=0.1, top_p=0.9, top_k=20, seed=42 (for claims, outline, glossary)
- **Balanced**: temperature=0.5, top_p=0.95, top_k=40 (for background, summary, detailed description)
- **Creative**: temperature=0.8, top_p=0.98, top_k=60 (for alternatives, embodiments)

### Step 3: Section Templates
Each USPTO section has a template with:
- Role definition
- Constraints (e.g., "Do not admit prior art superiority")
- Input specification
- Output contract (headings, numbering style)
- Banned phrases list

### Step 4: Spec Scaffolding
1. Generate structured outline (JSON) using strict profile
2. Extract section titles, bullets, figure plan, claim element inventory
3. Use outline to guide prose expansion

### Step 5: Controlled Terminology
1. Extract candidate terms from invention description
2. Model proposes glossary (term → definition, variants, forbidden synonyms)
3. Glossary used as input to all subsequent generation steps

### Step 6: Safe Language Guards
- Banned phrases per section (e.g., avoid "the present invention" in claims)
- Guards prepended to each template
- Model self-confirms compliance

### Step 7: Two-Pass Drafting
- **Pass A (Draft)**: Generate content with template + glossary using balanced profile
- **Pass B (Refine)**: Eliminate narrowing language, enforce tone, harmonize terms, ensure numbering

### Step 8: Claims Workbench
Three-phase workflow:
1. **Structure JSON**: Element inventory, relationships, dependencies, antecedent basis map, independent claim skeletons
2. **Draft**: Expand to full claims using strict profile
3. **Tighten**: Broaden by removing narrowing language, adding ranges, removing implementation-specific constraints

### Step 9: Self-Critique
After each major section:
- Score enablement, written description, best mode, consistency
- Generate fix-list JSON with targeted edits
- Apply fixes in next pass

### Step 10: Long-Context Management
- Summarize large inputs into fact cards (atomic, source-tagged)
- Cap at N tokens per prompt (default 10-12k)
- Feed only fact cards into drafting prompts

### Step 11: Model Ensemble Strategy
- Precision model: outline JSON, glossary, claims, brief description of drawings
- Fluency model: background, detailed description narrative, alternatives
- Final harmonization through precision model

### Step 12: Quantization & Performance
- Gold quantization: Higher precision, slower (for strict profile tasks)
- Daily quantization: Smaller, faster (for balanced/creative tasks)
- Profile-to-quantization mapping

### Step 13: Evaluation Harness
Automated rubric with:
- Section presence/ordering
- Banned phrase detection
- Glossary compliance
- Figure numeral consistency
- Claim antecedent basis
- JSON schema validity
- Composite score (weighted average)

### Step 14: Red-Team Prompts
Adversarial testing:
- Legal conclusions requests
- Statutory citation requests
- Prior art admission requests
- Fixed numeric cutoff requests
- Model must refuse or neutralize

### Step 15: Versioned Templates
- Template Pack: One file per section, versioned (e.g., `patent-spec@1.4.2`)
- Profile Pack: strict/balanced/creative profiles, versioned
- Model Map: Model/quantization mapping with version pinning
- Rollback support

### Step 16: Fine-Tuning Adapters (Structure)
- Support for LoRA/QLoRA adapters
- Narrow adapters (one per task)
- A/B swap capability
- Note: Training infrastructure not included (external)

### Step 17: Final Harmonization
Last pass that:
- Replaces inconsistent terms with glossary terms
- Checks headings/numbering
- Aligns claims terms with Detailed Description
- Generates final Abstract (≤150 words, no legalese)

## Usage

### Python API

```python
from patent_drafting_system import get_advanced_drafting_system

# Initialize system
system = get_advanced_drafting_system(
    precision_model="llama3.2:3b",
    fluency_model="mistral:7b"
)

# Generate draft
result = system.generate_complete_draft(
    invention_description="Your invention description here...",
    use_ensemble=True,
    use_scaffolding=True,
    use_two_pass=True,
    use_critique=True
)

# Access results
sections = result["sections"]
glossary = result["glossary"]
outline = result["outline"]
critique_results = result["critique_results"]
```

### REST API

```bash
POST /api/v1/generate_draft_advanced
Content-Type: application/json

{
  "description": "Your invention description...",
  "precision_model": "llama3.2:3b",
  "fluency_model": "mistral:7b",
  "use_ensemble": true,
  "use_scaffolding": true,
  "use_two_pass": true,
  "use_critique": true,
  "run_evaluation": false
}
```

### Evaluation

```python
from evaluation_harness import EvaluationHarness

evaluator = EvaluationHarness()
result = evaluator.evaluate_draft(
    draft=sections,
    glossary=glossary
)

print(f"Composite Score: {result.composite_score}")
print(f"Section Presence: {result.section_presence_score}")
print(f"Banned Phrases: {result.banned_phrase_detection_score}")
```

## Configuration

### Model Configuration

Edit `DEFAULT_MODELS` in `patent_drafting_system.py`:

```python
DEFAULT_MODELS = {
    "precision": ModelConfig(
        name="llama3.2:3b",
        role=ModelRole.PRECISION,
        quantization="gold",
        context_window=8192,
        min_context_window=16384
    ),
    "fluency": ModelConfig(...)
}
```

### Decoding Profiles

Edit `DECODING_PROFILES` in `patent_drafting_system.py`:

```python
DECODING_PROFILES = {
    "strict": DecodingProfile(
        temperature=0.1,
        top_p=0.9,
        top_k=20,
        repeat_penalty=1.15,
        seed=42
    ),
    ...
}
```

### Section Templates

Templates are defined in `SECTION_TEMPLATES` dictionary. Each template includes:
- Section name
- Role
- Constraints
- Input specification
- Output contract
- Banned phrases

### Task-to-Profile Mapping

Edit `TASK_PROFILE_MAP` to change which profile is used for which task:

```python
TASK_PROFILE_MAP = {
    "claims": "strict",
    "outline": "strict",
    "background": "balanced",
    "alternatives": "creative",
    ...
}
```

## File Structure

```
patent-drafting-assistant/
├── patent_drafting_system.py    # Main 17-step system
├── evaluation_harness.py         # Evaluation rubric
├── api_endpoints.py              # REST API integration
├── ollama_service.py             # Ollama client wrapper
├── templates/                    # Versioned templates (created on first use)
│   ├── sections/
│   │   └── 1.0.0/
│   └── profiles/
│       └── 1.0.0/
└── evaluation_dataset.json        # Test dataset
```

## Acceptance Criteria

Each step includes acceptance criteria:

1. **Model Selection**: Both models produce full spec without truncation at target context length
2. **Decoding Profiles**: Same prompt + profile yields stable structure (<2% token variance)
3. **Section Templates**: Every template outputs exact headings and numbering specified
4. **Scaffolding**: 100% of final content traceable to outline node
5. **Glossary**: Zero undefined terms; all claim nouns in glossary
6. **Safe Language**: No banned phrases in 20 consecutive generations
7. **Two-Pass**: Readability improves; zero mismatched figure numerals
8. **Claims Workbench**: No antecedent-basis errors; independent claims cover different statutory classes
9. **Self-Critique**: Applying fixes eliminates all checklist failures
10. **Long-Context**: ≥95% fact card fidelity in spot-check
11. **Ensemble**: Ensemble beats single model by >10% on rubric
12. **Quantization**: Predictable generation time; no structure loss
13. **Evaluation**: New changes cannot ship if composite score drops
14. **Red-Team**: 0 critical failures across adversarial set
15. **Versioning**: Can roll back any single template/profile/model mapping
16. **Fine-Tuning**: Adapter improves target task ≥10% with no regressions
17. **Harmonization**: Document passes full rubric with all checklists green

## Testing

Run evaluation suite:

```python
from evaluation_harness import EvaluationHarness
from patent_drafting_system import get_advanced_drafting_system

system = get_advanced_drafting_system()
evaluator = EvaluationHarness()

results = evaluator.run_evaluation_suite(system, num_tests=10)
print(f"Average Composite Score: {results['average_composite_score']}")
```

## Limitations & Future Work

- **Step 16 (Fine-Tuning)**: Structure only; training infrastructure not included
- **Context Window**: Current models may not meet 16k requirement; validation needed
- **Fact Card Fidelity**: Requires manual spot-checking
- **Red-Team Coverage**: Limited test set; expand for production

## References

- USPTO Patent Application Guide: https://www.uspto.gov/patents/basics
- 35 U.S.C. §112(a): Enablement, written description, best mode requirements
- MPEP (Manual of Patent Examining Procedure)

