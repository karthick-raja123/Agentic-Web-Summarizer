"""
Main Pipeline - LangGraph workflow orchestration.
Coordinates agents (Search -> Scrape -> Summarize).
"""

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from agents.search_agent import SearchAgent
from agents.scrape_agent import ScrapeAgent
from agents.summarize_agent import SummarizeAgent
from utils.logging_config import get_logger

logger = get_logger(__name__)


# Define workflow state
class AgentState(TypedDict):
    """State dictionary for LangGraph workflow."""
    query: str
    urls: List[str]
    content: str
    summary: str
    status: str
    error: Optional[str]


class VisualWebAgentPipeline:
    """Main orchestrator for the web agent workflow."""
    
    def __init__(
        self,
        num_search_results: int = 5,
        summary_points: int = 5,
        use_chunking: bool = False
    ):
        """
        Initialize pipeline with agents.
        
        Args:
            num_search_results: Number of URLs to search for
            summary_points: Number of bullet points in summary
            use_chunking: Whether to use hierarchical summarization
        """
        self.search_agent = SearchAgent(num_results=num_search_results)
        self.scrape_agent = ScrapeAgent()
        self.summarize_agent = SummarizeAgent(
            summary_points=summary_points,
            use_chunks=use_chunking
        )
        self.use_chunking = use_chunking
        
        # Build graph
        self.graph = self._build_graph()
        logger.info("VisualWebAgentPipeline initialized and graph built")
    
    def _build_graph(self):
        """Build LangGraph workflow."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("search", self._search_node)
        graph.add_node("scrape", self._scrape_node)
        graph.add_node("summarize", self._summarize_node)
        
        # Add edges
        graph.set_entry_point("search")
        graph.add_edge("search", "scrape")
        graph.add_edge("scrape", "summarize")
        graph.add_edge("summarize", END)
        
        logger.info("LangGraph workflow compiled")
        return graph.compile()
    
    def _search_node(self, state: AgentState) -> AgentState:
        """Search node: find URLs based on query."""
        logger.info(f"Entering search_node for query: '{state['query']}'")
        
        result = self.search_agent.execute(state["query"])
        
        state["urls"] = result.get("urls", [])
        state["status"] = result.get("status", "failed")
        state["error"] = result.get("error")
        
        logger.info(f"search_node completed with {len(state['urls'])} URLs")
        return state
    
    def _scrape_node(self, state: AgentState) -> AgentState:
        """Scrape node: fetch and clean content from URLs."""
        logger.info(f"Entering scrape_node for {len(state['urls'])} URLs")
        
        if not state["urls"]:
            logger.warning("No URLs to scrape")
            state["content"] = ""
            state["status"] = "failed"
            state["error"] = "No URLs available to scrape"
            return state
        
        result = self.scrape_agent.execute(state["urls"])
        
        state["content"] = result.get("content", "")
        state["status"] = result.get("status", "failed")
        state["error"] = result.get("error")
        
        logger.info(f"scrape_node completed with {len(state['content'])} characters")
        return state
    
    def _summarize_node(self, state: AgentState) -> AgentState:
        """Summarize node: create summary of content."""
        logger.info(f"Entering summarize_node for {len(state['content'])} characters")
        
        if not state["content"]:
            logger.warning("No content to summarize")
            state["summary"] = "No content available to summarize."
            state["status"] = "failed"
            state["error"] = "No content to summarize"
            return state
        
        # Use chunking if enabled
        if self.use_chunking:
            result = self.summarize_agent.execute_with_chunking(state["content"])
        else:
            result = self.summarize_agent.execute(state["content"])
        
        state["summary"] = result.get("summary", "")
        state["status"] = result.get("status", "failed")
        state["error"] = result.get("error")
        
        logger.info(f"summarize_node completed")
        return state
    
    def run(self, query: str) -> dict:
        """
        Execute workflow.
        
        Args:
            query: User search query
            
        Returns:
            Dictionary with complete workflow result
        """
        logger.info(f"Pipeline.run() called with query: '{query}'")
        
        if not query or len(query.strip()) == 0:
            logger.error("Empty query provided")
            return {
                "query": query,
                "urls": [],
                "content": "",
                "summary": "Please provide a valid search query.",
                "status": "failed",
                "error": "Empty query"
            }
        
        try:
            # Initialize state
            initial_state: AgentState = {
                "query": query,
                "urls": [],
                "content": "",
                "summary": "",
                "status": "running",
                "error": None
            }
            
            # Run workflow
            result = self.graph.invoke(initial_state)
            
            logger.info(f"Pipeline.run() completed with status: {result.get('status')}")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "query": query,
                "urls": [],
                "content": "",
                "summary": "",
                "status": "failed",
                "error": str(e)
            }


if __name__ == "__main__":
    # Example usage
    pipeline = VisualWebAgentPipeline(
        num_search_results=3,
        summary_points=5,
        use_chunking=False
    )
    
    query = "Key advancements in artificial intelligence"
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting pipeline for query: '{query}'")
    logger.info(f"{'='*60}\n")
    
    result = pipeline.run(query)
    
    logger.info(f"\n{'='*60}")
    logger.info("FINAL RESULTS")
    logger.info(f"{'='*60}")
    logger.info(f"Query: {result['query']}")
    logger.info(f"URLs Found: {len(result['urls'])}")
    logger.info(f"Status: {result['status']}")
    logger.info(f"\nSummary:\n{result['summary']}\n")
    
    if result.get('error'):
        logger.error(f"Error: {result['error']}")
