"""
Planner Agent - Analyzes queries and determines optimal processing strategy.
Decides routing and which agents to activate.
"""

from typing import Dict, List
from services.llm_service import LLMService
from utils.logging_config import get_logger
import json

logger = get_logger(__name__)


class PlannerAgent:
    """Agent that analyzes queries and creates execution plans."""
    
    def __init__(self):
        """Initialize Planner Agent."""
        self.llm_service = LLMService()
        logger.info("Planner Agent initialized")
    
    def execute(self, query: str) -> dict:
        """
        Analyze query and create an execution plan.
        
        Args:
            query: User's search query
            
        Returns:
            Dictionary with plan details and routing decisions
        """
        logger.info(f"PlannerAgent analyzing query: '{query}'")
        
        if not query or len(query.strip()) == 0:
            logger.warning("Empty query provided to PlannerAgent")
            return {
                "status": "failed",
                "plan": None,
                "routing": []
            }
        
        try:
            analysis_prompt = f"""Analyze this query and create an execution plan.
Respond with ONLY a valid JSON object (no markdown, no extra text).

Query: "{query}"

Respond with exactly this JSON structure:
{{
    "query_type": "academic|news|how_to|product_review|general",
    "complexity": "simple|medium|complex",
    "priority_agents": ["search", "scrape", "evaluate", "summarize"],
    "skip_agents": [],
    "needs_evaluation": true|false,
    "needs_formatting": true|false,
    "estimated_sources": 3,
    "summary_depth": "brief|detailed",
    "rationale": "Brief explanation"
}}"""
            
            logger.debug(f"Sending analysis request to LLM")
            response = self.llm_service.generate(analysis_prompt)
            
            # Parse JSON response
            plan_data = json.loads(response)
            
            logger.info(f"Plan created - Type: {plan_data.get('query_type')}, Complexity: {plan_data.get('complexity')}")
            
            return {
                "status": "success",
                "plan": plan_data,
                "routing": plan_data.get("priority_agents", ["search", "scrape", "summarize"]),
                "needs_evaluation": plan_data.get("needs_evaluation", True),
                "needs_formatting": plan_data.get("needs_formatting", True)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {str(e)}")
            # Return default plan on parse error
            return {
                "status": "success",
                "plan": self._get_default_plan(query),
                "routing": ["search", "scrape", "summarize"],
                "needs_evaluation": True,
                "needs_formatting": True
            }
        except Exception as e:
            logger.error(f"PlannerAgent failed: {str(e)}")
            return {
                "status": "failed",
                "plan": None,
                "routing": []
            }
    
    def _get_default_plan(self, query: str) -> dict:
        """
        Get default plan when analysis fails.
        
        Args:
            query: The search query
            
        Returns:
            Default plan structure
        """
        return {
            "query_type": "general",
            "complexity": "medium",
            "priority_agents": ["search", "scrape", "evaluate", "summarize"],
            "skip_agents": [],
            "needs_evaluation": True,
            "needs_formatting": True,
            "estimated_sources": 5,
            "summary_depth": "detailed",
            "rationale": "Default plan applied"
        }
    
    def refine_plan(self, plan: dict, feedback: str) -> dict:
        """
        Refine plan based on feedback or intermediate results.
        
        Args:
            plan: Current execution plan
            feedback: Feedback on plan effectiveness
            
        Returns:
            Refined plan
        """
        logger.info(f"Refining plan with feedback: {feedback[:50]}...")
        
        try:
            refinement_prompt = f"""The following execution plan produced this feedback.
Suggest refinements to improve results.

Original Plan: {json.dumps(plan, indent=2)}

Feedback: {feedback}

Respond with ONLY a valid JSON object with refinements."""
            
            response = self.llm_service.generate(refinement_prompt)
            refined_plan = json.loads(response)
            
            logger.info("Plan refined successfully")
            return refined_plan
            
        except Exception as e:
            logger.error(f"Plan refinement failed: {str(e)}")
            return plan  # Return original if refinement fails
