"""
Enhanced Query Expansion - Converts single query into multiple search strategies.
Improves search quality and coverage.
"""

from typing import List, Dict
from services.llm_service import LLMService
from utils.logging_config import get_logger
import json

logger = get_logger(__name__)


class QueryExpander:
    """Expands user query into multiple optimized search queries."""
    
    def __init__(self):
        """Initialize query expander."""
        self.llm_service = LLMService()
        logger.info("QueryExpander initialized")
    
    def expand_query(self, query: str, num_variations: int = 3) -> Dict[str, List[str]]:
        """
        Expand single query into multiple search variations.
        
        Args:
            query: Original user query
            num_variations: Number of query variations to generate
            
        Returns:
            Dictionary with original and expanded queries
        """
        logger.info(f"Expanding query: '{query}' into {num_variations} variations")
        
        if not query or len(query.strip()) < 3:
            logger.warning("Query too short for expansion")
            return {
                "original_query": query,
                "expanded_queries": [query],
                "strategy": "direct"
            }
        
        try:
            expansion_prompt = f"""Generate {num_variations} different search query variations for better web search coverage.
Each variation should target different angles or phrasings of the same topic.

Original query: "{query}"

Respond with ONLY valid JSON (no markdown, no extra text):
{{
    "primary_query": "best version emphasizing main topic",
    "variations": ["variation1", "variation2", "variation3"],
    "strategies": ["strategy used for variation1", "strategy for variation2", "strategy for variation3"],
    "reasoning": "why these variations improve coverage"
}}

Strategies to consider:
- Synonym expansion (use related terms)
- Question format (turn statement into question)
- Long-tail (add intent modifiers like 'best', 'latest', 'how to')
- Narrow scope (add specificity if too broad)
- Broaden scope (remove specificity if too narrow)
- Entity focus (emphasize specific entities)"""
            
            logger.debug("Requesting query expansion from LLM")
            response = self.llm_service.generate(expansion_prompt)
            expansion_result = json.loads(response)
            
            all_queries = [expansion_result.get("primary_query", query)]
            all_queries.extend(expansion_result.get("variations", [])[:num_variations-1])
            
            logger.info(f"Generated {len(all_queries)} query variations")
            
            return {
                "original_query": query,
                "primary_query": expansion_result.get("primary_query", query),
                "expanded_queries": all_queries,
                "strategies": expansion_result.get("strategies", []),
                "reasoning": expansion_result.get("reasoning", ""),
                "status": "success"
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse expansion JSON: {str(e)}")
            # Fallback: use simple heuristics
            return self._heuristic_expansion(query, num_variations)
        except Exception as e:
            logger.error(f"Query expansion failed: {str(e)}")
            return {
                "original_query": query,
                "expanded_queries": [query],
                "strategies": ["error_fallback"],
                "status": "failed"
            }
    
    def _heuristic_expansion(self, query: str, num_variations: int) -> Dict[str, List[str]]:
        """Fallback: Generate query variations using heuristics."""
        logger.info("Using heuristic query expansion (LLM fallback)")
        
        variations = [query]
        
        # Add 'how to' variant
        if num_variations > 1 and not query.lower().startswith(("how", "what", "why")):
            variations.append(f"how to {query}")
        
        # Add tutorial variant
        if num_variations > 2:
            variations.append(f"{query} tutorial")
        
        # Add 'best' variant
        if num_variations > 3:
            variations.append(f"best {query}")
        
        # Add 'latest' variant
        if num_variations > 4:
            variations.append(f"latest {query}")
        
        return {
            "original_query": query,
            "primary_query": query,
            "expanded_queries": variations[:num_variations],
            "strategies": ["heuristic"] * len(variations[:num_variations]),
            "status": "fallback"
        }
    
    def merge_expansion_results(self, expansion: Dict) -> str:
        """
        Create merged search query from expansion results.
        Useful for APIs that support complex queries.
        
        Args:
            expansion: Result from expand_query()
            
        Returns:
            Merged query string
        """
        queries = expansion.get("expanded_queries", [])
        if not queries:
            return expansion.get("original_query", "")
        
        # Join with OR for broader search coverage
        # Each quoted query is treated as exact phrase
        merged = " OR ".join([f'"{q}"' for q in queries])
        logger.debug(f"Merged query: {merged}")
        return merged
    
    def analyze_query_intent(self, query: str) -> Dict[str, str]:
        """
        Analyze the intent and type of query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with intent analysis
        """
        logger.info(f"Analyzing query intent: '{query}'")
        
        try:
            intent_prompt = f"""Analyze the intent of this query.
Query: "{query}"

Respond with ONLY valid JSON:
{{
    "intent_type": "informational|navigational|transactional|research",
    "primary_topic": "main subject",
    "sub_topics": ["topic1", "topic2"],
    "urgency": "immediate|standard|evergreen",
    "scope": "narrow|medium|broad",
    "language_type": "technical|casual|formal|mixed"
}}"""
            
            response = self.llm_service.generate(intent_prompt)
            return json.loads(response)
            
        except Exception as e:
            logger.warning(f"Intent analysis failed: {str(e)}")
            return {
                "intent_type": "informational",
                "primary_topic": query,
                "sub_topics": [],
                "urgency": "standard",
                "scope": "medium",
                "language_type": "casual"
            }
