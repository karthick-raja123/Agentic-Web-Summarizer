"""
True Multi-Agent System using LangGraph.
Dynamic routing with decision nodes and agent communication via shared state.
"""

from typing import TypedDict, List, Optional, Any, Dict
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command
import json

# Import all agents
from agents.planner_agent import PlannerAgent
from agents.search_agent import SearchAgent
from agents.scrape_agent import ScrapeAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.summarize_agent import SummarizeAgent
from agents.formatter_agent import FormatterAgent

from utils.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class AgentState(TypedDict):
    """Complete state for multi-agent system."""
    # Core inputs
    query: str
    
    # Agent outputs
    plan: Optional[Dict[str, Any]]
    search_results: Optional[Dict[str, Any]]
    scraped_content: Optional[str]
    scraped_urls: Optional[List[str]]
    evaluation_results: Optional[Dict[str, Any]]
    summary: Optional[str]
    formatted_output: Optional[Dict[str, Any]]
    
    # Control flow
    current_agent: str
    agent_history: List[str]
    routing_decisions: List[str]
    
    # Status tracking
    status: str  # "running", "success", "failed", "skipped"
    error_message: Optional[str]
    
    # Plan tracking
    enabled_agents: List[str]
    evaluate_content: bool
    format_output: bool
    
    # Shared context
    relevant_content: Optional[str]
    final_result: Optional[str]


# =============================================================================
# MULTI-AGENT PIPELINE
# =============================================================================

class MultiAgentPipeline:
    """True multi-agent system with dynamic routing and decision-making."""
    
    def __init__(self, enable_evaluation: bool = True, enable_formatting: bool = True):
        """
        Initialize multi-agent pipeline.
        
        Args:
            enable_evaluation: Whether to use evaluator agent
            enable_formatting: Whether to use formatter agent
        """
        # Initialize agents
        self.planner = PlannerAgent()
        self.search_agent = SearchAgent()
        self.scraper = ScrapeAgent()
        self.evaluator = EvaluatorAgent()
        self.summarizer = SummarizeAgent()
        self.formatter = FormatterAgent()
        
        # Configuration
        self.enable_evaluation = enable_evaluation
        self.enable_formatting = enable_formatting
        
        # Build graph
        self.graph = self._build_graph()
        
        logger.info(
            "MultiAgentPipeline initialized - "
            f"Evaluation: {enable_evaluation}, Formatting: {enable_formatting}"
        )
    
    def _build_graph(self):
        """Build LangGraph with conditional routing."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("planner", self._planner_node)
        graph.add_node("search", self._search_node)
        graph.add_node("scraper", self._scraper_node)
        
        # Conditional nodes (only if enabled)
        if self.enable_evaluation:
            graph.add_node("evaluator", self._evaluator_node)
        
        graph.add_node("summarizer", self._summarizer_node)
        
        if self.enable_formatting:
            graph.add_node("formatter", self._formatter_node)
        
        # Router nodes for decision-making
        graph.add_node("route_after_plan", self._route_after_plan)
        graph.add_node("error_handler", self._error_handler)
        
        # Set entry point
        graph.set_entry_point("planner")
        
        # Add edges - Sequential flow
        graph.add_edge("planner", "route_after_plan")
        
        # Routing after plan (conditional)
        graph.add_conditional_edges(
            "route_after_plan",
            self._decide_next_step,
            {
                "search": "search",
                "skip": "error_handler",
            }
        )
        
        # Search to scraper (conditional based on results)
        graph.add_conditional_edges(
            "search",
            self._decide_after_search,
            {
                "scrape": "scraper",
                "skip": "error_handler",
            }
        )
        
        # After scraper: evaluate or summarize
        if self.enable_evaluation:
            graph.add_edge("scraper", "evaluator")
            graph.add_conditional_edges(
                "evaluator",
                self._decide_after_evaluation,
                {
                    "summarize": "summarizer",
                    "skip": "error_handler",
                }
            )
        else:
            graph.add_edge("scraper", "summarizer")
        
        # After summarizer: format or end
        if self.enable_formatting:
            graph.add_edge("summarizer", "formatter")
            graph.add_edge("formatter", END)
        else:
            graph.add_edge("summarizer", END)
        
        # Error handler leads to end
        graph.add_edge("error_handler", END)
        
        logger.info("LangGraph workflow compiled successfully")
        return graph.compile()
    
    # =========================================================================
    # NODE IMPLEMENTATIONS
    # =========================================================================
    
    def _planner_node(self, state: AgentState) -> AgentState:
        """Planner node: Analyze query and create execution plan."""
        logger.info("→ PLANNER NODE: Analyzing query...")
        
        state["current_agent"] = "planner"
        state["agent_history"].append("planner")
        
        result = self.planner.execute(state["query"])
        
        state["plan"] = result.get("plan")
        state["enabled_agents"] = result.get("routing", ["search", "scraper", "summarizer"])
        state["evaluate_content"] = result.get("needs_evaluation", self.enable_evaluation)
        state["format_output"] = result.get("needs_formatting", self.enable_formatting)
        
        if result["status"] == "success":
            state["status"] = "running"
            logger.info(f"  Plan: {state['plan'].get('query_type')} | "
                       f"Complexity: {state['plan'].get('complexity')}")
        else:
            state["status"] = "failed"
            state["error_message"] = "Planning failed"
            logger.error("  Planning failed!")
        
        return state
    
    def _search_node(self, state: AgentState) -> AgentState:
        """Search node: Fetch URLs based on query."""
        logger.info("→ SEARCH NODE: Searching for URLs...")
        
        state["current_agent"] = "search"
        state["agent_history"].append("search")
        state["routing_decisions"].append("search")
        
        result = self.search_agent.execute(state["query"])
        
        state["search_results"] = result
        
        if result["status"] == "success" and result.get("urls"):
            state["status"] = "running"
            logger.info(f"  Found {len(result['urls'])} URLs")
        else:
            state["error_message"] = "No URLs found"
            logger.warning("  No URLs found!")
        
        return state
    
    def _scraper_node(self, state: AgentState) -> AgentState:
        """Scraper node: Extract content from URLs."""
        logger.info("→ SCRAPER NODE: Extracting content...")
        
        state["current_agent"] = "scraper"
        state["agent_history"].append("scraper")
        state["routing_decisions"].append("scraper")
        
        urls = state.get("search_results", {}).get("urls", [])
        
        if not urls:
            state["status"] = "failed"
            state["error_message"] = "No URLs to scrape"
            logger.warning("  No URLs available!")
            return state
        
        result = self.scraper.execute(urls)
        
        state["scraped_content"] = result.get("content", "")
        state["scraped_urls"] = urls
        
        if result["status"] == "success":
            state["status"] = "running"
            logger.info(f"  Extracted {len(result.get('content', ''))} characters")
        else:
            state["error_message"] = "Scraping failed"
            logger.warning("  Scraping failed!")
        
        return state
    
    def _evaluator_node(self, state: AgentState) -> AgentState:
        """Evaluator node: Filter content by relevance."""
        logger.info("→ EVALUATOR NODE: Evaluating content...")
        
        state["current_agent"] = "evaluator"
        state["agent_history"].append("evaluator")
        state["routing_decisions"].append("evaluator")
        
        content = state.get("scraped_content", "")
        
        if not content:
            state["status"] = "failed"
            state["error_message"] = "No content to evaluate"
            logger.warning("  No content to evaluate!")
            return state
        
        result = self.evaluator.execute(state["query"], content)
        
        state["evaluation_results"] = result
        
        if result.get("is_relevant"):
            state["relevant_content"] = result.get("filtered_content", content)
            state["status"] = "running"
            logger.info(f"  Content relevant (score: {result.get('relevance_score', 0):.2f})")
        else:
            state["error_message"] = f"Content not relevant (score: {result.get('relevance_score', 0):.2f})"
            logger.info(f"  Content filtered out (score: {result.get('relevance_score', 0):.2f})")
        
        return state
    
    def _summarizer_node(self, state: AgentState) -> AgentState:
        """Summarizer node: Generate summary from content."""
        logger.info("→ SUMMARIZER NODE: Generating summary...")
        
        state["current_agent"] = "summarizer"
        state["agent_history"].append("summarizer")
        state["routing_decisions"].append("summarizer")
        
        # Use evaluated content if available, otherwise scraped content
        content = state.get("relevant_content") or state.get("scraped_content", "")
        
        if not content:
            state["status"] = "failed"
            state["error_message"] = "No content to summarize"
            logger.warning("  No content to summarize!")
            return state
        
        result = self.summarizer.execute(content)
        
        state["summary"] = result.get("summary", "")
        
        if result["status"] == "success":
            state["status"] = "running"
            logger.info(f"  Summary generated ({len(result.get('summary', ''))} chars)")
        else:
            state["error_message"] = "Summarization failed"
            logger.warning("  Summarization failed!")
        
        return state
    
    def _formatter_node(self, state: AgentState) -> AgentState:
        """Formatter node: Format output into multiple formats."""
        logger.info("→ FORMATTER NODE: Formatting output...")
        
        state["current_agent"] = "formatter"
        state["agent_history"].append("formatter")
        state["routing_decisions"].append("formatter")
        
        result = self.formatter.execute(
            state["query"],
            state.get("summary", ""),
            state.get("scraped_urls", [])
        )
        
        state["formatted_output"] = result
        
        if result["status"] == "success":
            state["status"] = "success"
            state["final_result"] = result
            logger.info(f"  Formatted to: {list(result.get('formats', {}).keys())}")
        else:
            state["status"] = "failed"
            state["error_message"] = "Formatting failed"
            logger.warning("  Formatting failed!")
        
        return state
    
    def _route_after_plan(self, state: AgentState) -> AgentState:
        """Route after planning phase."""
        logger.info("→ ROUTE NODE: Determining next step...")
        return state
    
    def _error_handler(self, state: AgentState) -> AgentState:
        """Error handler: Graceful degradation."""
        logger.info(f"→ ERROR HANDLER: {state.get('error_message', 'Unknown error')}")
        
        state["current_agent"] = "error_handler"
        state["status"] = "failed"
        
        # Try to provide best output possible
        if state.get("summary"):
            state["status"] = "partial_success"
            logger.info("  Returning partial results (summary available)")
        
        return state
    
    # =========================================================================
    # ROUTING DECISIONS
    # =========================================================================
    
    def _decide_next_step(self, state: AgentState) -> str:
        """Decide next step after planning."""
        if state.get("status") == "failed":
            return "skip"
        
        # Check if search is enabled in plan
        if "search" in state.get("enabled_agents", []):
            return "search"
        
        return "skip"
    
    def _decide_after_search(self, state: AgentState) -> str:
        """Decide next step after search."""
        if state.get("status") == "failed":
            return "skip"
        
        search_results = state.get("search_results", {})
        if search_results.get("urls"):
            return "scrape"
        
        return "skip"
    
    def _decide_after_evaluation(self, state: AgentState) -> str:
        """Decide next step after evaluation."""
        if state.get("status") == "failed":
            return "skip"
        
        eval_results = state.get("evaluation_results", {})
        if eval_results.get("is_relevant"):
            return "summarize"
        
        return "skip"
    
    # =========================================================================
    # EXECUTION
    # =========================================================================
    
    def run(self, query: str) -> dict:
        """
        Execute multi-agent pipeline.
        
        Args:
            query: User's search query
            
        Returns:
            Dictionary with complete results
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"MULTI-AGENT PIPELINE START: '{query}'")
        logger.info(f"{'='*70}\n")
        
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "plan": None,
            "search_results": None,
            "scraped_content": None,
            "scraped_urls": None,
            "evaluation_results": None,
            "summary": None,
            "formatted_output": None,
            "current_agent": None,
            "agent_history": [],
            "routing_decisions": [],
            "status": "initializing",
            "error_message": None,
            "enabled_agents": [],
            "evaluate_content": self.enable_evaluation,
            "format_output": self.enable_formatting,
            "relevant_content": None,
            "final_result": None,
        }
        
        try:
            # Execute graph
            result_state = self.graph.invoke(initial_state)
            
            logger.info(f"\n{'='*70}")
            logger.info(f"PIPELINE COMPLETE - Status: {result_state.get('status')}")
            logger.info(f"Agents executed: {' → '.join(result_state.get('agent_history', []))}")
            logger.info(f"{'='*70}\n")
            
            return self._format_result(result_state)
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "query": query,
                "summary": ""
            }
    
    def _format_result(self, state: AgentState) -> dict:
        """Format final result for output."""
        return {
            "status": state.get("status"),
            "query": state.get("query"),
            "summary": state.get("summary", ""),
            "urls": state.get("scraped_urls", []),
            "agents_used": state.get("agent_history", []),
            "routing_path": " → ".join(state.get("agent_history", [])),
            "plan": state.get("plan"),
            "evaluation": state.get("evaluation_results"),
            "formatted_output": state.get("formatted_output"),
            "error": state.get("error_message")
        }
