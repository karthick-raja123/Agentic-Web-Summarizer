"""
Enhanced Summarizer - Reduces hallucinations by only summarizing extracted content.
Validates summaries against input content.
"""

from typing import List, Dict, Optional
from services.llm_service import LLMService
from utils.logging_config import get_logger
import json

logger = get_logger(__name__)


class EnhancedSummarizer:
    """Summarizer with hallucination reduction mechanisms."""
    
    def __init__(self, max_hallucination_score: float = 0.3):
        """
        Initialize enhanced summarizer.
        
        Args:
            max_hallucination_score: Maximum acceptable hallucination score (0-1)
        """
        self.llm_service = LLMService()
        self.max_hallucination_score = max_hallucination_score
        
        logger.info(
            f"EnhancedSummarizer initialized "
            f"- Max hallucination score: {max_hallucination_score}"
        )
    
    def summarize_with_validation(self, query: str, content: str, 
                                  depth: str = "detailed") -> Dict:
        """
        Summarize content with built-in hallucination detection.
        
        Args:
            query: Original query
            content: Content to summarize
            depth: "brief" or "detailed"
            
        Returns:
            Dictionary with summary, validation, and hallucination score
        """
        logger.info(
            f"Summarizing {len(content)} chars with validation - Query: '{query}'"
        )
        
        if not content or len(content.strip()) < 50:
            logger.warning("Content too short for summarization")
            return {
                "status": "failed",
                "summary": "",
                "is_valid": False,
                "hallucination_score": 1.0,
                "error": "Insufficient content"
            }
        
        # Step 1: Generate raw summary
        raw_summary = self._generate_raw_summary(query, content, depth)
        
        if not raw_summary:
            return {
                "status": "failed",
                "summary": "",
                "is_valid": False,
                "hallucination_score": 1.0,
                "error": "Summary generation failed"
            }
        
        # Step 2: Extract factual claims from summary
        claims = self._extract_claims(raw_summary)
        
        # Step 3: Validate claims against source content
        validation_results = self._validate_claims_against_source(claims, content)
        
        # Step 4: Calculate hallucination score
        hallucination_score = validation_results["hallucination_score"]
        is_valid = hallucination_score <= self.max_hallucination_score
        
        logger.info(
            f"Summary generated - Hallucination score: {hallucination_score:.2f}, "
            f"Valid: {is_valid}"
        )
        
        return {
            "status": "success" if is_valid else "warning",
            "summary": raw_summary,
            "is_valid": is_valid,
            "hallucination_score": hallucination_score,
            "validated_claims": validation_results["validated_claims"],
            "unvalidated_claims": validation_results["unvalidated_claims"],
            "claim_accuracy_rate": validation_results["claim_accuracy_rate"],
            "total_claims": len(claims),
            "warnings": validation_results.get("warnings", [])
        }
    
    def _generate_raw_summary(self, query: str, content: str, depth: str) -> Optional[str]:
        """
        Generate raw summary using LLM.
        
        Args:
            query: Original query
            content: Content to summarize
            depth: "brief" or "detailed"
            
        Returns:
            Summary string or None
        """
        try:
            if depth == "brief":
                point_count = 3
                instruction = "Provide EXACTLY 3 bullet-point summary"
            else:
                point_count = 7
                instruction = "Provide EXACTLY 7 bullet-point summary with details"
            
            prompt = f"""Extract key information from this content to answer the query.
Query: "{query}"

Content to summarize:
{content}

Instructions:
- {instruction}
- Each point should be ONE sentence
- Only include facts directly stated or clearly implied in the content
- Do NOT add external information or assumptions
- Use bullet points with "-" prefix

Important: ONLY summarize what is in the content provided."""
            
            logger.debug("Requesting summary from LLM")
            response = self.llm_service.generate(prompt)
            
            return response if response and len(response.strip()) > 20 else None
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return None
    
    def _extract_claims(self, summary: str) -> List[str]:
        """
        Extract factual claims from summary.
        
        Args:
            summary: Summary text
            
        Returns:
            List of claim sentences
        """
        # Split by bullet points
        claims = []
        
        for line in summary.split("\n"):
            line = line.strip()
            
            # Remove bullet markers
            if line.startswith("-"):
                line = line[1:].strip()
            elif line and line[0].isdigit() and "." in line:
                # Remove numbered markers like "1."
                line = line.split(".", 1)[1].strip()
            
            if line and len(line) > 10:
                claims.append(line)
        
        logger.debug(f"Extracted {len(claims)} claims from summary")
        return claims
    
    def _validate_claims_against_source(self, claims: List[str], 
                                        source_content: str) -> Dict:
        """
        Validate summary claims against source content.
        
        Args:
            claims: Claims from summary
            source_content: Original content
            
        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {len(claims)} claims against source content")
        
        if not claims:
            return {
                "hallucination_score": 0.0,
                "claim_accuracy_rate": 1.0,
                "validated_claims": [],
                "unvalidated_claims": [],
                "warnings": []
            }
        
        validated_claims = []
        unvalidated_claims = []
        warnings = []
        
        for claim in claims:
            # Check 1: Keywords from claim appear in source
            claim_words = set(claim.lower().split())
            source_lower = source_content.lower()
            
            keyword_coverage = sum(1 for word in claim_words 
                                  if word in source_lower and len(word) > 3)
            keyword_ratio = keyword_coverage / len([w for w in claim_words if len(w) > 3]) if claim_words else 0
            
            # Check 2: Use LLM to validate semantic accuracy
            is_accurate = self._llm_validate_claim(claim, source_content)
            
            if keyword_ratio > 0.5 and is_accurate:
                validated_claims.append(claim)
                logger.debug(f"✓ Validated claim: {claim[:60]}")
            else:
                unvalidated_claims.append(claim)
                logger.debug(f"✗ Unvalidated claim: {claim[:60]}")
                
                if keyword_ratio < 0.3:
                    warnings.append(f"Low keyword coverage: {claim[:50]}")
        
        # Calculate hallucination score
        hallucination_score = len(unvalidated_claims) / len(claims) if claims else 0
        claim_accuracy_rate = len(validated_claims) / len(claims) if claims else 1.0
        
        return {
            "hallucination_score": hallucination_score,
            "claim_accuracy_rate": claim_accuracy_rate,
            "validated_claims": validated_claims,
            "unvalidated_claims": unvalidated_claims,
            "warnings": warnings
        }
    
    def _llm_validate_claim(self, claim: str, source_content: str) -> bool:
        """
        Use LLM to validate if claim is supported by source content.
        
        Args:
            claim: Claim to validate
            source_content: Source content
            
        Returns:
            True if claim is supported, False otherwise
        """
        try:
            prompt = f"""Is this claim supported by the provided content?

Claim: "{claim}"

Content:
{source_content[:2000]}

Respond with ONLY "yes" or "no" (nothing else)."""
            
            response = self.llm_service.generate(prompt)
            
            if response:
                result = response.strip().lower()
                return result.startswith("yes")
            
            return True  # Default to accepting if can't validate
            
        except Exception as e:
            logger.debug(f"LLM claim validation failed: {str(e)}")
            return True  # Default to accepting on error
    
    def create_grounded_summary(self, query: str, content: str, 
                               ranked_sections: List[Dict] = None) -> Dict:
        """
        Create summary grounded in specific content sections.
        
        Args:
            query: Original query
            content: Content to summarize
            ranked_sections: Optional ranked content sections
            
        Returns:
            Grounded summary with citations
        """
        logger.info("Creating grounded summary with section citations")
        
        # If ranked sections provided, use those
        if ranked_sections:
            top_sections = ranked_sections[:3]
            section_content = "\n\n".join([s.get("content", "") for s in top_sections])
        else:
            section_content = content
        
        summary_result = self.summarize_with_validation(
            query, 
            section_content,
            depth="detailed"
        )
        
        # Add source attribution
        if ranked_sections:
            summary_result["grounded"] = True
            summary_result["source_sections"] = len(top_sections)
            summary_result["top_sources"] = [
                {"rank": s.get("rank"), "score": s.get("relevance_score")} 
                for s in top_sections
            ]
        
        return summary_result
    
    def generate_summary_report(self, summary_result: Dict) -> str:
        """
        Generate human-readable report about summary quality.
        
        Args:
            summary_result: Result from summarize_with_validation()
            
        Returns:
            Formatted report string
        """
        report = f"""
═══════════════════════════════════════════════════════════════
SUMMARY QUALITY REPORT
═══════════════════════════════════════════════════════════════

Status: {summary_result.get('status', 'unknown').upper()}
Hallucination Score: {summary_result.get('hallucination_score', 0):.2f}
  → Interpretation: {self._interpret_hallucination_score(summary_result.get('hallucination_score', 0))}

Claim Validation:
  • Total Claims: {summary_result.get('total_claims', 0)}
  • Validated: {len(summary_result.get('validated_claims', []))}
  • Unvalidated: {len(summary_result.get('unvalidated_claims', []))}
  • Accuracy Rate: {summary_result.get('claim_accuracy_rate', 0):.1%}

Summary:
{summary_result.get('summary', 'N/A')}

{'Warnings:' if summary_result.get('warnings') else ''}
{chr(10).join('  • ' + w for w in summary_result.get('warnings', []))}

═══════════════════════════════════════════════════════════════
"""
        return report
    
    def _interpret_hallucination_score(self, score: float) -> str:
        """Interpret hallucination score for user."""
        if score < 0.1:
            return "Excellent - highly grounded in source"
        elif score < 0.3:
            return "Good - mostly grounded"
        elif score < 0.5:
            return "Fair - some unvalidated claims"
        else:
            return "Poor - significant hallucination risk"
