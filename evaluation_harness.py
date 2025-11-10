#!/usr/bin/env python3
"""
Step 13: Evaluation Harness for Patent Drafting System
Lightweight evaluation with auto-scored checks.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvaluationResult:
    """Result of evaluation on a single draft."""
    section_presence_score: float
    section_ordering_score: float
    banned_phrase_detection_score: float
    glossary_compliance_score: float
    figure_numeral_consistency_score: float
    claim_antecedent_basis_score: float
    json_schema_validity_score: float
    composite_score: float
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_presence_score": self.section_presence_score,
            "section_ordering_score": self.section_ordering_score,
            "banned_phrase_detection_score": self.banned_phrase_detection_score,
            "glossary_compliance_score": self.glossary_compliance_score,
            "figure_numeral_consistency_score": self.figure_numeral_consistency_score,
            "claim_antecedent_basis_score": self.claim_antecedent_basis_score,
            "json_schema_validity_score": self.json_schema_validity_score,
            "composite_score": self.composite_score,
            "details": self.details
        }


class EvaluationHarness:
    """Evaluation harness for patent drafts."""
    
    REQUIRED_SECTIONS = [
        "TITLE OF THE INVENTION",
        "FIELD OF THE INVENTION",
        "BACKGROUND OF THE INVENTION",
        "BRIEF SUMMARY OF THE INVENTION",
        "BRIEF DESCRIPTION OF THE DRAWINGS",
        "DETAILED DESCRIPTION OF THE INVENTION",
        "CLAIMS",
        "ABSTRACT OF THE DISCLOSURE"
    ]
    
    BANNED_PHRASES = {
        "claims": ["the present invention", "said"],  # "said" when unnecessary
        "summary": ["must", "only", "exclusively", "cannot be"],
        "background": ["the present invention is superior", "prior art fails completely"],
        "all": ["revolutionary", "will make millions"]
    }
    
    def __init__(self, dataset_path: Path = Path("evaluation_dataset.json")):
        self.dataset_path = dataset_path
        self.dataset = self._load_dataset()
    
    def _load_dataset(self) -> List[Dict[str, Any]]:
        """Load evaluation dataset."""
        if not self.dataset_path.exists():
            return []
        
        try:
            with open(self.dataset_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []
    
    def evaluate_draft(
        self,
        draft: Dict[str, str],
        expected_structure: Dict[str, Any] = None,
        glossary: Dict[str, Any] = None
    ) -> EvaluationResult:
        """Evaluate a draft against rubric."""
        
        # 1. Section presence
        section_presence = self._check_section_presence(draft)
        
        # 2. Section ordering
        section_ordering = self._check_section_ordering(draft)
        
        # 3. Banned phrase detection
        banned_phrases = self._detect_banned_phrases(draft)
        
        # 4. Glossary compliance
        glossary_compliance = self._check_glossary_compliance(draft, glossary or {})
        
        # 5. Figure numeral consistency
        figure_consistency = self._check_figure_numeral_consistency(draft)
        
        # 6. Claim antecedent basis
        claim_antecedent = self._check_claim_antecedent_basis(draft)
        
        # 7. JSON schema validity (if applicable)
        json_validity = self._check_json_schema_validity(draft)
        
        # Composite score (weighted average)
        composite = (
            section_presence["score"] * 0.15 +
            section_ordering["score"] * 0.10 +
            (1.0 - banned_phrases["score"]) * 0.20 +  # Inverted (lower is better)
            glossary_compliance["score"] * 0.15 +
            figure_consistency["score"] * 0.15 +
            claim_antecedent["score"] * 0.15 +
            json_validity["score"] * 0.10
        )
        
        return EvaluationResult(
            section_presence_score=section_presence["score"],
            section_ordering_score=section_ordering["score"],
            banned_phrase_detection_score=banned_phrases["score"],
            glossary_compliance_score=glossary_compliance["score"],
            figure_numeral_consistency_score=figure_consistency["score"],
            claim_antecedent_basis_score=claim_antecedent["score"],
            json_schema_validity_score=json_validity["score"],
            composite_score=composite,
            details={
                "section_presence": section_presence,
                "section_ordering": section_ordering,
                "banned_phrases": banned_phrases,
                "glossary_compliance": glossary_compliance,
                "figure_consistency": figure_consistency,
                "claim_antecedent": claim_antecedent,
                "json_validity": json_validity
            }
        )
    
    def _check_section_presence(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Check if all required sections are present."""
        present_sections = set(draft.keys())
        required_set = set(self.REQUIRED_SECTIONS)
        
        missing = required_set - present_sections
        present = required_set & present_sections
        
        score = len(present) / len(required_set) if required_set else 0.0
        
        return {
            "score": score,
            "present": list(present),
            "missing": list(missing),
            "total_required": len(required_set)
        }
    
    def _check_section_ordering(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Check if sections are in correct order."""
        # Extract section order from draft keys (assuming ordered dict or list)
        draft_sections = list(draft.keys())
        
        # Find positions of required sections
        positions = {}
        for i, section in enumerate(draft_sections):
            for req_section in self.REQUIRED_SECTIONS:
                if req_section.upper() in section.upper():
                    positions[req_section] = i
                    break
        
        # Check if order matches expected
        ordered_positions = [positions.get(s, -1) for s in self.REQUIRED_SECTIONS if s in positions]
        is_ordered = ordered_positions == sorted(ordered_positions) and len(ordered_positions) > 0
        
        score = 1.0 if is_ordered else 0.5
        
        return {
            "score": score,
            "is_ordered": is_ordered,
            "positions": positions
        }
    
    def _detect_banned_phrases(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Detect banned phrases in draft."""
        violations = []
        total_phrases = 0
        
        for section_name, section_text in draft.items():
            text_lower = section_text.lower()
            
            # Check section-specific banned phrases
            section_key = section_name.lower()
            banned = []
            for key, phrases in self.BANNED_PHRASES.items():
                if key in section_key or key == "all":
                    banned.extend(phrases)
            
            for phrase in banned:
                if phrase.lower() in text_lower:
                    violations.append({
                        "section": section_name,
                        "phrase": phrase,
                        "count": text_lower.count(phrase.lower())
                    })
                    total_phrases += text_lower.count(phrase.lower())
        
        # Score: 0.0 if violations found, 1.0 if none
        # But we want to penalize based on number of violations
        score = max(0.0, 1.0 - (len(violations) * 0.1))
        
        return {
            "score": score,
            "violations": violations,
            "total_violations": len(violations),
            "total_phrase_count": total_phrases
        }
    
    def _check_glossary_compliance(self, draft: Dict[str, str], glossary: Dict[str, Any]) -> Dict[str, Any]:
        """Check if draft uses glossary terms correctly."""
        if not glossary:
            return {"score": 1.0, "issues": []}
        
        issues = []
        all_text = " ".join(draft.values()).lower()
        
        for term, entry in glossary.items():
            # Check for forbidden synonyms
            forbidden = entry.get("forbidden_synonyms", [])
            for synonym in forbidden:
                if synonym.lower() in all_text:
                    issues.append({
                        "term": term,
                        "forbidden_synonym": synonym,
                        "should_use": term
                    })
        
        # Score based on issues
        score = max(0.0, 1.0 - (len(issues) * 0.2))
        
        return {
            "score": score,
            "issues": issues,
            "total_issues": len(issues)
        }
    
    def _check_figure_numeral_consistency(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Check if figure numerals are consistent."""
        # Extract all figure references
        figure_refs = []
        for section_name, section_text in draft.items():
            # Find FIG. N patterns
            matches = re.findall(r'FIG\.\s*(\d+)', section_text, re.IGNORECASE)
            figure_refs.extend([(section_name, int(m)) for m in matches])
        
        # Check for consistency
        unique_figures = set(fig_num for _, fig_num in figure_refs)
        
        # Check if figures are sequential and referenced consistently
        if not unique_figures:
            return {"score": 1.0, "figures": [], "issues": []}
        
        max_fig = max(unique_figures)
        expected_figures = set(range(1, max_fig + 1))
        missing_figures = expected_figures - unique_figures
        
        # Check if Brief Description mentions all figures
        brief_desc = draft.get("BRIEF DESCRIPTION OF THE DRAWINGS", "")
        brief_figures = set(int(m) for m in re.findall(r'FIG\.\s*(\d+)', brief_desc, re.IGNORECASE))
        
        issues = []
        if missing_figures:
            issues.append(f"Missing figure references: {missing_figures}")
        if brief_figures != unique_figures:
            issues.append(f"Brief Description figures ({brief_figures}) don't match referenced figures ({unique_figures})")
        
        score = 1.0 if not issues else 0.5
        
        return {
            "score": score,
            "figures": list(unique_figures),
            "issues": issues,
            "total_figures": len(unique_figures)
        }
    
    def _check_claim_antecedent_basis(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Check if claim terms have antecedent basis in specification."""
        claims_text = draft.get("CLAIMS", "")
        spec_text = draft.get("DETAILED DESCRIPTION OF THE INVENTION", "")
        
        if not claims_text:
            return {"score": 0.0, "issues": ["No claims found"]}
        
        # Extract claim terms (simplified - look for capitalized terms)
        claim_terms = set(re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', claims_text))
        
        # Remove common words
        common_words = {"The", "A", "An", "And", "Or", "Of", "To", "In", "For", "With", "By"}
        claim_terms = {t for t in claim_terms if t not in common_words and len(t) > 3}
        
        # Check if terms appear in specification
        spec_lower = spec_text.lower()
        missing_basis = []
        for term in claim_terms:
            if term.lower() not in spec_lower:
                missing_basis.append(term)
        
        score = max(0.0, 1.0 - (len(missing_basis) / max(len(claim_terms), 1)) * 0.5)
        
        return {
            "score": score,
            "claim_terms": list(claim_terms),
            "missing_basis": missing_basis,
            "total_terms": len(claim_terms),
            "terms_without_basis": len(missing_basis)
        }
    
    def _check_json_schema_validity(self, draft: Dict[str, str]) -> Dict[str, Any]:
        """Check if draft structure matches expected schema."""
        # Basic validation: check if it's a dict with string values
        is_valid = isinstance(draft, dict) and all(isinstance(v, str) for v in draft.values())
        
        return {
            "score": 1.0 if is_valid else 0.0,
            "is_valid": is_valid
        }
    
    def run_evaluation_suite(
        self,
        drafting_system,
        num_tests: int = None
    ) -> Dict[str, Any]:
        """Run evaluation suite on dataset."""
        if not self.dataset:
            return {"error": "No evaluation dataset loaded"}
        
        tests = self.dataset[:num_tests] if num_tests else self.dataset
        results = []
        
        for test_case in tests:
            invention_brief = test_case.get("invention_description", "")
            expected_structure = test_case.get("expected_structure", {})
            
            # Generate draft
            draft_result = drafting_system.generate_complete_draft(invention_brief)
            
            # Evaluate
            evaluation = self.evaluate_draft(
                draft_result["sections"],
                expected_structure,
                draft_result.get("glossary", {})
            )
            
            results.append({
                "test_case": test_case.get("id", "unknown"),
                "evaluation": evaluation.to_dict(),
                "generation_time": draft_result.get("generation_time", 0.0)
            })
        
        # Aggregate scores
        avg_composite = sum(r["evaluation"]["composite_score"] for r in results) / len(results) if results else 0.0
        
        return {
            "total_tests": len(results),
            "average_composite_score": avg_composite,
            "results": results
        }

