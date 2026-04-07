"""
Content Ranker - Ranks scraped content by relevance before summarization.
Ensures summarizer processes highest-quality content first.
"""

from typing import List, Dict, Tuple
from services.llm_service import LLMService
from utils.logging_config import get_logger
import json

logger = get_logger(__name__)


class ContentRanker:
    """Ranks and prioritizes content by relevance score."""
    
    def __init__(self, min_content_length: int = 100):
        """
        Initialize content ranker.
        
        Args:
            min_content_length: Minimum content length in characters
        """
        self.llm_service = LLMService()
        self.min_content_length = min_content_length
        logger.info(f"ContentRanker initialized (min length: {min_content_length} chars)")
    
    def rank_contents(self, query: str, contents: List[str], urls: List[str] = None) -> Dict:
        """
        Rank multiple content pieces by relevance to query.
        
        Args:
            query: Search query
            contents: List of content pieces
            urls: Optional list of source URLs (for tracking)
            
        Returns:
            Dictionary with ranked contents and scores
        """
        logger.info(f"Ranking {len(contents)} content pieces for query: '{query}'")
        
        if not contents:
            logger.warning("No content to rank")
            return {
                "status": "empty",
                "ranked_contents": [],
                "total_scored": 0
            }
        
        ranked_items = []
        
        for i, content in enumerate(contents):
            if len(content.strip()) < self.min_content_length:
                logger.debug(f"Content {i+1} too short ({len(content)} chars), skipping")
                continue
            
            score = self._compute_relevance_score(query, content)
            
            ranked_items.append({
                "rank": 0,  # Will be set after sorting
                "content": content,
                "url": urls[i] if urls and i < len(urls) else "unknown",
                "relevance_score": score["overall"],
                "semantic_score": score.get("semantic", 0),
                "keyword_score": score.get("keyword", 0),
                "length_score": score.get("length", 0),
                "quality_indicators": score.get("quality_indicators", []),
                "sections": score.get("sections", [])
            })
        
        # Sort by relevance score (descending)
        ranked_items.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Add ranks after sorting
        for rank, item in enumerate(ranked_items, 1):
            item["rank"] = rank
        
        logger.info(
            f"Ranked {len(ranked_items)} content pieces - "
            f"Top score: {ranked_items[0]['relevance_score']:.2f if ranked_items else 'N/A'}"
        )
        
        return {
            "status": "success",
            "query": query,
            "ranked_contents": ranked_items,
            "total_scored": len(contents),
            "total_valid": len(ranked_items),
            "top_score": ranked_items[0]["relevance_score"] if ranked_items else 0,
            "average_score": sum(item["relevance_score"] for item in ranked_items) / len(ranked_items) if ranked_items else 0
        }
    
    def _compute_relevance_score(self, query: str, content: str) -> Dict[str, float]:
        """
        Compute multi-faceted relevance score.
        
        Args:
            query: Search query
            content: Content to score
            
        Returns:
            Dictionary with component scores
        """
        try:
            # Component 1: Semantic relevance via LLM
            semantic_score = self._semantic_similarity(query, content)
            
            # Component 2: Keyword matching
            keyword_score = self._keyword_matching_score(query, content)
            
            # Component 3: Content length bonus
            length_score = min(len(content) / 5000, 1.0)  # 5000 chars = max score
            
            # Component 4: Quality indicators
            quality_indicators, quality_score = self._detect_quality_indicators(content)
            
            # Weighted combination
            overall = (
                semantic_score * 0.5 +      # Semantic matching is primary
                keyword_score * 0.2 +        # Keywords support
                length_score * 0.1 +         # Content depth
                quality_score * 0.2          # Quality signals
            )
            
            return {
                "overall": min(overall, 1.0),
                "semantic": semantic_score,
                "keyword": keyword_score,
                "length": length_score,
                "quality": quality_score,
                "quality_indicators": quality_indicators,
                "sections": []
            }
            
        except Exception as e:
            logger.warning(f"Error computing relevance score: {str(e)}")
            return {"overall": 0.5, "semantic": 0, "keyword": 0, "length": 0, "quality": 0}
    
    def _semantic_similarity(self, query: str, content: str) -> float:
        """
        Compute semantic similarity between query and content.
        Uses LLM for intelligent comparison.
        
        Args:
            query: Search query
            content: Content preview (first 1000 chars)
            
        Returns:
            Similarity score (0-1)
        """
        try:
            similarity_prompt = f"""Rate semantic similarity between query and content.
Query: "{query}"

Content preview: {content[:1000]}...

Respond with ONLY a number between 0 and 1 (e.g., 0.85)
0 = completely unrelated
0.5 = partially related
1 = perfectly relevant"""
            
            response = self.llm_service.generate(similarity_prompt)
            score = float(response.strip())
            return max(0, min(score, 1.0))
            
        except Exception as e:
            logger.debug(f"Semantic similarity computation failed: {str(e)}")
            return 0.5
    
    def _keyword_matching_score(self, query: str, content: str) -> float:
        """
        Score based on keyword matching.
        
        Args:
            query: Search query
            content: Content to check
            
        Returns:
            Keyword score (0-1)
        """
        query_words = set(query.lower().split())
        content_lower = content.lower()
        
        # Count how many query words appear in content
        matches = sum(1 for word in query_words if word in content_lower)
        keyword_score = matches / len(query_words) if query_words else 0
        
        return min(keyword_score, 1.0)
    
    def _detect_quality_indicators(self, content: str) -> Tuple[List[str], float]:
        """
        Detect quality indicators in content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Tuple of (indicator_list, quality_score)
        """
        indicators = []
        score = 0.0
        
        # Check for structured content
        if any(marker in content for marker in ["•", "◦", "-", "*", "1.", "2.", "3."]):
            indicators.append("structured_list")
            score += 0.15
        
        # Check for data/statistics
        if any(char in content for char in ["0123456789%"]):
            indicators.append("contains_data")
            score += 0.1
        
        # Check for citations/sources
        if any(marker in content for marker in ["(Source", "[Source", "According to", "Research shows"]):
            indicators.append("cited")
            score += 0.15
        
        # Check for professional language
        if any(word in content.lower() for word in ["research", "study", "analysis", "methodology"]):
            indicators.append("technical_language")
            score += 0.1
        
        # Check for headings/sections
        if content.count("\n\n") > 3:  # Multiple paragraphs suggest organization
            indicators.append("well_organized")
            score += 0.1
        
        # Check length (more content usually = more quality)
        if len(content) > 2000:
            indicators.append("comprehensive")
            score += 0.1
        
        return indicators, score
    
    def get_top_content(self, ranking_result: Dict, count: int = 3) -> str:
        """
        Get top N ranked contents combined.
        
        Args:
            ranking_result: Result from rank_contents()
            count: Number of top contents to combine
            
        Returns:
            Combined top content string
        """
        top_items = ranking_result["ranked_contents"][:count]
        
        combined = []
        for item in top_items:
            combined.append(f"\n--- Content #{item['rank']} (Score: {item['relevance_score']:.2f}) ---\n{item['content']}")
        
        result = "\n".join(combined)
        logger.info(f"Combined top {len(top_items)} ranked contents ({len(result)} chars)")
        
        return result
    
    def filter_by_score(self, ranking_result: Dict, min_score: float = 0.6) -> List[Dict]:
        """
        Filter ranked content by minimum score threshold.
        
        Args:
            ranking_result: Result from rank_contents()
            min_score: Minimum relevance score (0-1)
            
        Returns:
            List of contents meeting threshold
        """
        filtered = [item for item in ranking_result["ranked_contents"] 
                   if item["relevance_score"] >= min_score]
        
        logger.info(
            f"Filtered {len(filtered)}/{len(ranking_result['ranked_contents'])} "
            f"contents above threshold {min_score}"
        )
        
        return filtered
