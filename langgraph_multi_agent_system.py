"""
LangGraph Multi-Agent System with Dynamic Routing and Conditional Loops
Agents: Planner, Search, Scraper, Evaluator, Summarizer, Reflection

Architecture:
- Dynamic routing based on agent decisions
- Shared state across agents
- Conditional loops for retry logic
- Tool use for each specialized agent
"""

import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List, Optional, Dict, Any, Annotated
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
import google.generativeai as genai
import os
import json
from enum import Enum
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from services.model_handler import create_model_with_fallback

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

try:
    model, CURRENT_MODEL_NAME = create_model_with_fallback(Config.GOOGLE_API_KEY)
except Exception as e:
    print(f"❌ Error initializing model: {e}")
    raise

# Serper API configuration
SERPER_API_KEY = Config.SERPER_API_KEY

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentType(Enum):
    """Enum for agent types"""
    PLANNER = "planner"
    SEARCH = "search"
    SCRAPER = "scraper"
    EVALUATOR = "evaluator"
    SUMMARIZER = "summarizer"
    REFLECTION = "reflection"

class PlanStep(TypedDict):
    """Individual step in a plan"""
    step_number: int
    action: str
    description: str
    required: bool

class SearchQuery(TypedDict):
    """Search query with metadata"""
    query: str
    priority: int
    depth: str  # "shallow" or "deep"

class ScrapedContent(TypedDict):
    """Scraped content with metadata"""
    url: str
    title: str
    content: str
    length: int
    quality_score: float
    source_type: str  # "article", "blog", "technical", etc.

class EvaluationResult(TypedDict):
    """Content evaluation result"""
    url: str
    quality_score: float
    relevance_score: float
    reasoning: str
    is_valid: bool

class PipelineState(TypedDict):
    """Shared state across all agents"""
    # Input
    query: str
    user_intent: str
    
    # Planning phase
    plan: List[PlanStep]
    plan_iterations: int
    
    # Search phase
    search_queries: List[SearchQuery]
    search_results: List[Dict[str, Any]]
    
    # Scraping phase
    urls: List[str]
    scraped_content: List[ScrapedContent]
    scraping_iterations: int
    
    # Evaluation phase
    evaluations: List[EvaluationResult]
    valid_content: List[ScrapedContent]
    
    # Summarization phase
    raw_summary: str
    summary: str
    summary_bullets: List[str]
    
    # Reflection phase
    reflection_score: float
    reflection_notes: str
    needs_improvement: bool
    iterations: int
    max_iterations: int
    
    # Metadata
    timestamps: Dict[str, datetime]
    messages: List[str]
    current_agent: str
    next_agent: str
    error: Optional[str]

# ============================================================================
# AGENT 1: PLANNER AGENT
# ============================================================================

def planner_agent(state: PipelineState) -> PipelineState:
    """
    Planner Agent: Breaks down user query into actionable steps
    
    Responsibilities:
    - Understand user intent
    - Create multi-step plan
    - Identify search strategies
    - Plan for content evaluation
    """
    print("\n" + "="*80)
    print("🤖 PLANNER AGENT")
    print("="*80)
    
    query = state["query"]
    state["timestamps"]["planner_start"] = datetime.now()
    
    # Use LLM to create a plan
    prompt = f"""You are a planning expert. Break down this user query into a detailed plan.

User Query: "{query}"

Create a JSON response with this structure:
{{
    "user_intent": "Identify the core need",
    "plan": [
        {{"step_number": 1, "action": "action_name", "description": "what to do", "required": true}},
        ...
    ],
    "search_strategies": [
        {{"query": "search term", "priority": 1, "depth": "deep"}},
        ...
    ]
}}

Provide exactly 3-5 search strategies. Include different angles to find comprehensive information."""
    
    response = model.generate_content(prompt)
    response_text = response.text
    
    # Extract JSON from response
    try:
        # Find JSON in response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        plan_data = json.loads(json_str)
        
        state["user_intent"] = plan_data.get("user_intent", query)
        state["plan"] = plan_data.get("plan", [])
        state["search_queries"] = plan_data.get("search_strategies", [])
    except json.JSONDecodeError:
        # Fallback plan
        state["user_intent"] = query
        state["plan"] = [
            {"step_number": 1, "action": "search", "description": "Search for information", "required": True},
            {"step_number": 2, "action": "scrape", "description": "Extract content", "required": True},
            {"step_number": 3, "action": "evaluate", "description": "Filter quality", "required": True},
            {"step_number": 4, "action": "summarize", "description": "Generate summary", "required": True},
        ]
        state["search_queries"] = [
            {"query": query, "priority": 1, "depth": "deep"},
            {"query": f"{query} overview", "priority": 2, "depth": "shallow"},
            {"query": f"{query} best practices", "priority": 3, "depth": "shallow"},
        ]
    
    state["plan_iterations"] = state.get("plan_iterations", 0) + 1
    state["messages"].append(f"✓ Plan created with {len(state['plan'])} steps")
    state["messages"].append(f"✓ {len(state['search_queries'])} search strategies identified")
    
    print(f"Intent: {state['user_intent']}")
    print(f"Plan steps: {len(state['plan'])}")
    print(f"Search strategies: {len(state['search_queries'])}")
    
    state["current_agent"] = "planner"
    state["next_agent"] = "search"
    
    return state

# ============================================================================
# AGENT 2: SEARCH AGENT
# ============================================================================

def search_agent(state: PipelineState) -> PipelineState:
    """
    Search Agent: Executes multiple search queries with different strategies
    
    Responsibilities:
    - Execute diverse searches
    - Prioritize results by relevance
    - Handle search failures gracefully
    - Collect URLs for scraping
    """
    print("\n" + "="*80)
    print("🔍 SEARCH AGENT")
    print("="*80)
    
    state["timestamps"]["search_start"] = datetime.now()
    
    all_urls = []
    all_results = []
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Execute each search query
    for search_query in state.get("search_queries", [{"query": state["query"]}]):
        query_str = search_query if isinstance(search_query, str) else search_query.get("query")
        priority = search_query.get("priority", 1) if isinstance(search_query, dict) else 1
        
        print(f"\n  Searching: {query_str} (priority: {priority})")
        
        try:
            data = {"q": query_str, "num": 5}
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                organic_results = results.get("organic", [])
                
                for result in organic_results:
                    url = result.get("link")
                    if url and url not in all_urls:
                        all_urls.append(url)
                        all_results.append({
                            "url": url,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", ""),
                            "query": query_str,
                            "priority": priority
                        })
                
                state["messages"].append(f"✓ Search '{query_str}' completed - {len(organic_results)} results")
                print(f"  ✓ Found {len(organic_results)} results")
            else:
                state["messages"].append(f"⚠ Search failed: {response.status_code}")
                print(f"  ⚠ Search failed with status {response.status_code}")
                
        except Exception as e:
            error_msg = f"Search error for '{query_str}': {str(e)}"
            state["messages"].append(f"⚠ {error_msg}")
            print(f"  ⚠ {error_msg}")
    
    # Limit URLs (prioritize by query priority)
    state["urls"] = all_urls[:8]  # Get top 8 URLs
    state["search_results"] = all_results
    
    state["messages"].append(f"✓ Total URLs collected: {len(state['urls'])}")
    print(f"\n✓ Collected {len(state['urls'])} unique URLs")
    
    state["current_agent"] = "search"
    state["next_agent"] = "scraper"
    
    return state

# ============================================================================
# AGENT 3: SCRAPER AGENT
# ============================================================================

def scraper_agent(state: PipelineState) -> PipelineState:
    """
    Scraper Agent: Extracts structured content from URLs
    
    Responsibilities:
    - Fetch and parse HTML
    - Extract meaningful content
    - Classify content type
    - Compute content metrics
    """
    print("\n" + "="*80)
    print("🌐 SCRAPER AGENT")
    print("="*80)
    
    state["timestamps"]["scraper_start"] = datetime.now()
    scraped_content: List[ScrapedContent] = []
    
    for idx, url in enumerate(state.get("urls", []), 1):
        print(f"\n  [{idx}] Scraping: {url}")
        
        try:
            response = requests.get(url, timeout=8)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "Unknown"
            
            # Extract main content
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            text = " ".join(text.split())  # Normalize whitespace
            
            # Limit content length but preserve quality
            content = text[:2000]
            
            # Classify content type based on URL and structure
            source_type = classify_content_type(url, soup)
            
            # Compute quality score (simple heuristic)
            quality_score = compute_content_quality(content, soup)
            
            scraped_content.append({
                "url": url,
                "title": title_text,
                "content": content,
                "length": len(content),
                "quality_score": quality_score,
                "source_type": source_type
            })
            
            state["messages"].append(f"✓ Scraped: {title_text[:50]}... (quality: {quality_score:.2f})")
            print(f"  ✓ Content extracted ({len(content)} chars, quality: {quality_score:.2f})")
            
        except requests.Timeout:
            state["messages"].append(f"⚠ Timeout: {url}")
            print(f"  ⚠ Timeout fetching {url}")
        except Exception as e:
            state["messages"].append(f"⚠ Error: {url} - {str(e)[:50]}")
            print(f"  ⚠ Error: {str(e)}")
    
    state["scraped_content"] = scraped_content
    state["scraping_iterations"] = state.get("scraping_iterations", 0) + 1
    
    state["messages"].append(f"✓ Scraped {len(scraped_content)} pages successfully")
    print(f"\n✓ Scraped {len(scraped_content)} pages")
    
    state["current_agent"] = "scraper"
    state["next_agent"] = "evaluator"
    
    return state

# ============================================================================
# AGENT 4: EVALUATOR AGENT
# ============================================================================

def evaluator_agent(state: PipelineState) -> PipelineState:
    """
    Evaluator Agent: Filters content by quality and relevance
    
    Responsibilities:
    - Assess content quality
    - Check relevance to query
    - Filter low-quality content
    - Provide evaluation reasoning
    """
    print("\n" + "="*80)
    print("🎯 EVALUATOR AGENT")
    print("="*80)
    
    state["timestamps"]["evaluator_start"] = datetime.now()
    
    evaluations: List[EvaluationResult] = []
    valid_content: List[ScrapedContent] = []
    
    query = state.get("query", "")
    user_intent = state.get("user_intent", query)
    
    for scraped in state.get("scraped_content", []):
        # Use LLM to evaluate relevance
        eval_prompt = f"""Evaluate this content for relevance and quality.

Query: "{query}"
Intent: "{user_intent}"

Content Title: {scraped['title']}
Content: {scraped['content'][:500]}...

Provide JSON response:
{{
    "relevance_score": 0.0-1.0,
    "quality_reasoning": "brief explanation",
    "is_relevant": true/false,
    "key_insights": []
}}"""
        
        try:
            response = model.generate_content(eval_prompt)
            response_text = response.text
            
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            eval_result = json.loads(json_str)
            
            relevance_score = float(eval_result.get("relevance_score", 0.5))
            is_valid = eval_result.get("is_relevant", relevance_score > 0.5)
            
        except:
            # Fallback: use basic heuristics
            relevance_score = simple_relevance_check(scraped["content"], query)
            is_valid = relevance_score > 0.3
            eval_result = {"quality_reasoning": "Auto-evaluated"}
        
        # Combine with content quality score
        combined_score = (scraped["quality_score"] + relevance_score) / 2
        
        evaluation = {
            "url": scraped["url"],
            "quality_score": combined_score,
            "relevance_score": relevance_score,
            "reasoning": eval_result.get("quality_reasoning", ""),
            "is_valid": is_valid
        }
        
        evaluations.append(evaluation)
        
        if is_valid and combined_score > 0.4:
            valid_content.append(scraped)
            state["messages"].append(f"✓ Valid: {scraped['title'][:40]}... ({combined_score:.2f})")
            print(f"  ✓ Valid content: {combined_score:.2f}")
        else:
            state["messages"].append(f"✗ Filtered: {scraped['title'][:40]}... ({combined_score:.2f})")
            print(f"  ✗ Filtered: {combined_score:.2f}")
    
    state["evaluations"] = evaluations
    state["valid_content"] = valid_content
    
    valid_count = len(valid_content)
    state["messages"].append(f"✓ Evaluation complete: {valid_count} valid sources")
    
    print(f"\n✓ Valid content: {valid_count} sources")
    
    state["current_agent"] = "evaluator"
    state["next_agent"] = "summarizer"
    
    return state

# ============================================================================
# AGENT 5: SUMMARIZER AGENT
# ============================================================================

def summarizer_agent(state: PipelineState) -> PipelineState:
    """
    Summarizer Agent: Generates comprehensive summary from valid content
    
    Responsibilities:
    - Combine content strategically
    - Generate structured summary
    - Create bullet points
    - Ensure coherence and coverage
    """
    print("\n" + "="*80)
    print("📝 SUMMARIZER AGENT")
    print("="*80)
    
    state["timestamps"]["summarizer_start"] = datetime.now()
    
    # Combine valid content
    combined_content = ""
    for content in state.get("valid_content", []):
        combined_content += f"\n[Source: {content['title']}]\n{content['content']}\n"
    
    if not combined_content:
        combined_content = "\n".join([
            f"[Source: {c['title']}]\n{c['content']}"
            for c in state.get("scraped_content", [])[:3]
        ])
    
    # Limit combined content
    combined_content = combined_content[:5000]
    
    # Generate summary using LLM
    summary_prompt = f"""Summarize the following content comprehensively and clearly.

Query: {state.get('query', '')}
Intent: {state.get('user_intent', '')}

Content:
{combined_content}

Provide a summary with:
1. A brief comprehensive overview (2-3 sentences)
2. Exactly 5-7 key bullet points
3. Important considerations or caveats

Format as JSON:
{{
    "overview": "summary text",
    "bullet_points": ["point1", "point2", ...],
    "considerations": "any important notes"
}}"""
    
    try:
        response = model.generate_content(summary_prompt)
        response_text = response.text
        
        # Extract JSON
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        summary_data = json.loads(json_str)
        
        overview = summary_data.get("overview", "")
        bullets = summary_data.get("bullet_points", [])
        considerations = summary_data.get("considerations", "")
        
        # Build formatted summary
        state["raw_summary"] = overview
        state["summary_bullets"] = bullets
        state["summary"] = f"""{overview}

Key Points:
{chr(10).join([f"• {b}" for b in bullets])}

{f"Considerations: {considerations}" if considerations else ""}"""
        
    except Exception as e:
        # Fallback summary
        state["summary"] = f"Summary generated from {len(state.get('valid_content', []))} sources"
        state["summary_bullets"] = ["Content analyzed", "Summary created", "Ready for review"]
    
    state["messages"].append(f"✓ Summary generated with {len(state['summary_bullets'])} bullet points")
    print(f"\n✓ Summary created with {len(state.get('summary_bullets', []))} bullet points")
    
    state["current_agent"] = "summarizer"
    state["next_agent"] = "reflection"  # Always go to reflection
    
    return state

# ============================================================================
# AGENT 6: REFLECTION AGENT
# ============================================================================

def reflection_agent(state: PipelineState) -> PipelineState:
    """
    Reflection Agent: Evaluates summary quality and decides if re-run needed
    
    Responsibilities:
    - Assess summary completeness
    - Check relevance coverage
    - Determine if improvement needed
    - Decide: END or RETRY
    """
    print("\n" + "="*80)
    print("🔄 REFLECTION AGENT")
    print("="*80)
    
    state["timestamps"]["reflection_start"] = datetime.now()
    state["iterations"] = state.get("iterations", 0) + 1
    
    query = state.get("query", "")
    summary = state.get("summary", "")
    valid_sources = len(state.get("valid_content", []))
    
    # Use LLM to evaluate summary
    reflection_prompt = f"""You are a quality control expert. Evaluate this summary.

Original Query: "{query}"
Number of Valid Sources: {valid_sources}
Summary:
{summary}

Evaluate on:
1. Relevance (does it answer the query?)
2. Completeness (covers all major aspects?)
3. Quality (well-structured and clear?)
4. Source coverage (enough sources used?)

Provide JSON:
{{
    "quality_score": 0.0-1.0,
    "assessment": "brief assessment",
    "needs_improvement": true/false,
    "improvement_suggestions": "what could be better"
}}"""
    
    try:
        response = model.generate_content(reflection_prompt)
        response_text = response.text
        
        # Extract JSON
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        reflection_data = json.loads(json_str)
        
        state["reflection_score"] = float(reflection_data.get("quality_score", 0.5))
        state["reflection_notes"] = reflection_data.get("assessment", "")
        state["needs_improvement"] = reflection_data.get("needs_improvement", False)
        
    except:
        # Fallback: score based on sources and length
        state["reflection_score"] = min(1.0, 0.5 + (valid_sources * 0.1) + (len(summary) / 1000))
        state["reflection_notes"] = "Auto-evaluated"
        state["needs_improvement"] = state["reflection_score"] < 0.6 and valid_sources < 3
    
    # Decide next action
    should_retry = (
        state["needs_improvement"] and 
        state["iterations"] < state.get("max_iterations", 2)
    )
    
    state["messages"].append(f"✓ Reflection complete - Score: {state['reflection_score']:.2f}")
    
    if should_retry:
        state["messages"].append(f"⟳ Quality needs improvement - Retrying (iteration {state['iterations']})")
        print(f"\n⟳ Score: {state['reflection_score']:.2f} - Needs improvement")
        print(f"⟳ Retrying pipeline (iteration {state['iterations']})")
        state["next_agent"] = "search"  # Retry from search with new strategy
    else:
        state["messages"].append(f"✓ Summary accepted - Final score: {state['reflection_score']:.2f}")
        print(f"\n✓ Summary accepted - Score: {state['reflection_score']:.2f}")
        state["next_agent"] = "end"  # Go to end
    
    state["current_agent"] = "reflection"
    
    return state

# ============================================================================
# ROUTER FUNCTION - DYNAMIC ROUTING
# ============================================================================

def route_after_reflection(state: PipelineState) -> str:
    """
    Dynamic router after reflection.
    Decides whether to end or retry the pipeline.
    """
    if state.get("next_agent") == "search":
        # Retry: go back to search with improved strategy
        return "search"
    else:
        # End pipeline
        return END

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def classify_content_type(url: str, soup) -> str:
    """Classify the content type based on URL and HTML structure"""
    url_lower = url.lower()
    
    if any(x in url_lower for x in ["github", "code", "technical"]):
        return "technical"
    elif any(x in url_lower for x in ["blog", "article", "news"]):
        return "article"
    elif any(x in url_lower for x in ["wiki", "doc", "reference"]):
        return "documentation"
    elif any(x in url_lower for x in ["forum", "reddit", "stack"]):
        return "community"
    else:
        return "general"

def compute_content_quality(content: str, soup) -> float:
    """Compute content quality score (0.0-1.0)"""
    score = 0.5
    
    # Bonus for length
    if len(content) > 500:
        score += 0.2
    
    # Bonus for structure (headings, paragraphs)
    if soup.find_all("h1") or soup.find_all("h2"):
        score += 0.15
    
    # Bonus for lists
    if soup.find_all("ul") or soup.find_all("ol"):
        score += 0.1
    
    # Penalty for short content
    if len(content) < 200:
        score -= 0.3
    
    return min(1.0, max(0.0, score))

def simple_relevance_check(content: str, query: str) -> float:
    """Simple relevance check using keyword matching"""
    query_words = set(query.lower().split())
    content_lower = content.lower()
    
    matches = sum(1 for word in query_words if word in content_lower)
    return min(1.0, matches / len(query_words)) if query_words else 0.5

# ============================================================================
# GRAPH INITIALIZATION
# ============================================================================

def create_graph():
    """
    Create the LangGraph multi-agent system with dynamic routing
    
    Flow:
    START → Planner → Search → Scraper → Evaluator → Summarizer → Reflection → (Loop or END)
    """
    
    # Initialize state graph
    workflow = StateGraph(PipelineState)
    
    # Add all nodes (agents)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("search", search_agent)
    workflow.add_node("scraper", scraper_agent)
    workflow.add_node("evaluator", evaluator_agent)
    workflow.add_node("summarizer", summarizer_agent)
    workflow.add_node("reflection", reflection_agent)
    
    # Setup edges (connections)
    workflow.set_entry_point("planner")
    
    # Linear path to summarizer
    workflow.add_edge("planner", "search")
    workflow.add_edge("search", "scraper")
    workflow.add_edge("scraper", "evaluator")
    workflow.add_edge("evaluator", "summarizer")
    workflow.add_edge("summarizer", "reflection")
    
    # Dynamic conditional routing after reflection
    workflow.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "search": "search",  # Retry: go back to search
            END: END              # Done: finish
        }
    )
    
    return workflow.compile()

# ============================================================================
# INITIALIZE GRAPH AND RUN
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "LangGraph Multi-Agent System - Dynamic Routing & Conditional Loops".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    # Get user query
    user_query = input("\n📝 Enter your topic to summarize: ").strip()
    
    if not user_query:
        user_query = "Machine learning applications in healthcare"
    
    # Initialize state
    initial_state: PipelineState = {
        "query": user_query,
        "user_intent": "",
        "plan": [],
        "plan_iterations": 0,
        "search_queries": [],
        "search_results": [],
        "urls": [],
        "scraped_content": [],
        "scraping_iterations": 0,
        "evaluations": [],
        "valid_content": [],
        "raw_summary": "",
        "summary": "",
        "summary_bullets": [],
        "reflection_score": 0.0,
        "reflection_notes": "",
        "needs_improvement": False,
        "iterations": 0,
        "max_iterations": 2,  # Allow 1 retry
        "timestamps": {},
        "messages": [],
        "current_agent": "start",
        "next_agent": "planner",
        "error": None
    }
    
    # Create and run graph
    graph = create_graph()
    
    print(f"\n▶ Starting pipeline for: '{user_query}'")
    print("─" * 80)
    
    try:
        # Run the graph
        result = graph.invoke(initial_state)
        
        # Display results
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE")
        print("="*80)
        
        print(f"\n📊 FINAL SUMMARY")
        print("─" * 80)
        print(result.get("summary", "No summary generated"))
        
        print(f"\n📈 METRICS")
        print("─" * 80)
        print(f"✓ Total iterations: {result.get('iterations', 0)}")
        print(f"✓ Valid sources: {len(result.get('valid_content', []))}")
        print(f"✓ Reflection score: {result.get('reflection_score', 0):.2f}")
        print(f"✓ Agents called: {len(result.get('messages', []))}")
        
        print(f"\n📋 PROCESSING LOG")
        print("─" * 80)
        for msg in result.get("messages", [])[-15:]:  # Last 15 messages
            print(f"  {msg}")
        
        print(f"\n✓ All timestamps:")
        for agent, ts in result.get("timestamps", {}).items():
            print(f"  {agent}: {ts}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
