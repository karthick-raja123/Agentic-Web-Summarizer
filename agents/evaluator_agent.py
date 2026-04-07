"""
Evaluator Agent - Filters and rates content relevance.
Decides whether content meets quality standards.
"""

from typing import List, Dict
from services.llm_service import LLMService
from utils.logging_config import get_logger
import json

logger = get_logger(__name__)


class EvaluatorAgent:
    """Agent that evaluates content quality and relevance."""
    
    def __init__(self, relevance_threshold: float = 0.6):
        """
        Initialize Evaluator Agent.
        
        Args:
            relevance_threshold: Minimum relevance score (0-1) to keep content
        """
        self.llm_service = LLMService()
        self.relevance_threshold = relevance_threshold
        logger.info(f"Evaluator Agent initialized (threshold: {relevance_threshold})")
    
    def execute(self, query: str, content: str) -> dict:
        """
        Evaluate content relevance and quality.
        
        Args:
            query: Original search query
            content: Content to evaluate
            
        Returns:
            Dictionary with evaluation results and filtered content
        """
        logger.info(f"EvaluatorAgent evaluating {len(content)} characters for query: '{query}'")
        
        if not content or len(content.strip()) < 50:
            logger.warning("Content too short for meaningful evaluation")
            return {
                "status": "failed",
                "is_relevant": False,
                "relevance_score": 0.0,
                "quality_issues": ["Content too short"],
                "filtered_content": "",
                "recommendation": "skip"
            }
        
        try:
            evaluation_prompt = f"""Evaluate this content for relevance to the query.
Respond with ONLY a valid JSON object (no markdown, no extra text).

Query: "{query}"

Content Preview: {content[:1000]}...

Respond with exactly this JSON structure:
{{
    "relevance_score": 0.85,
    "is_relevant": true,
    "quality_score": 0.75,
    "quality_issues": ["issue1", "issue2"],
    "content_bias": "neutral|biased|promotional",
    "information_density": "high|medium|low",
    "recommendation": "keep|improve|skip",
    "why": "Brief explanation"
}}"""
            
            logger.debug("Sending evaluation request to LLM")
            response = self.llm_service.generate(evaluation_prompt)
            evaluation = json.loads(response)
            
            relevance_score = evaluation.get("relevance_score", 0.0)
            is_relevant = relevance_score >= self.relevance_threshold
            
            logger.info(
                f"Evaluation complete - Relevance: {relevance_score:.2f}, "
                f"Quality: {evaluation.get('quality_score', 0):.2f}, "
                f"Recommendation: {evaluation.get('recommendation')}"
            )
            
            return {
                "status": "success",
                "is_relevant": is_relevant,
                "relevance_score": relevance_score,
                "quality_score": evaluation.get("quality_score", 0),
                "quality_issues": evaluation.get("quality_issues", []),
                "content_bias": evaluation.get("content_bias", "unknown"),
                "information_density": evaluation.get("information_density", "unknown"),
                "recommendation": evaluation.get("recommendation", "skip"),
                "evaluation_notes": evaluation.get("why", ""),
                "filtered_content": content if is_relevant else ""
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {str(e)}")
            # Default: accept if evaluation fails
            return {
                "status": "success",
                "is_relevant": True,
                "relevance_score": 0.5,
                "quality_score": 0.0,
                "quality_issues": ["Could not evaluate"],
                "recommendation": "keep",
                "filtered_content": content
            }
        except Exception as e:
            logger.error(f"EvaluatorAgent failed: {str(e)}")
            return {
                "status": "failed",
                "is_relevant": False,
                "relevance_score": 0.0,
                "quality_issues": [str(e)],
                "recommendation": "skip",
                "filtered_content": ""
            }
    
    def evaluate_batch(self, query: str, contents: List[str]) -> dict:
        """
        Evaluate multiple content pieces.
        
        Args:
            query: Search query
            contents: List of content pieces
            
        Returns:
            Dictionary with evaluation results for each content
        """
        logger.info(f"EvaluatorAgent evaluating batch of {len(contents)} items")
        
        evaluations = []
        filtered_contents = []
        relevant_count = 0
        
        for i, content in enumerate(contents, 1):
            result = self.execute(query, content)
            evaluations.append(result)
            
            if result["is_relevant"]:
                filtered_contents.append(content)
                relevant_count += 1
            
            logger.debug(f"Batch item {i}/{len(contents)} - Relevance: {result.get('relevance_score', 0):.2f}")
        
        logger.info(f"Batch evaluation complete - {relevant_count}/{len(contents)} items relevant")
        
        return {
            "status": "success",
            "total_evaluated": len(contents),
            "relevant_count": relevant_count,
            "relevance_rate": relevant_count / len(contents) if contents else 0,
            "evaluations": evaluations,
            "filtered_contents": filtered_contents,
            "combined_content": "\n\n".join(filtered_contents)
        }
    
    def rate_relevance(self, query: str, content: str) -> float:
        """
        Quick relevance rating without full evaluation.
        
        Args:
            query: Search query
            content: Content to rate
            
        Returns:
            Relevance score 0-1
        """
        result = self.execute(query, content)
        return result.get("relevance_score", 0.0)
