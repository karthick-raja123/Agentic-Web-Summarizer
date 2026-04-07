"""
CLI Pipeline - Multi-Agent Research Aggregation
Production-ready with error handling, logging, and debug mode
"""

import os
import sys
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
from datetime import datetime
import time
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from langgraph.graph import StateGraph, END
from typing import TypedDict
import google.generativeai as genai

# ============================================================================
# CONFIGURE LOGGING & DEBUG
# ============================================================================

DEBUG = Config.DEBUG
LOG_LEVEL = Config.LOG_LEVEL

def log_debug(msg: str, level: str = "INFO"):
    """Print log message with timestamp."""
    if level == "DEBUG" and not DEBUG:
        return
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = f"[{timestamp}] [{level}]"
    print(f"{prefix} {msg}")

def log_error(msg: str, exc: Optional[Exception] = None):
    """Print error message with optional traceback."""
    print(f"\n❌ ERROR: {msg}")
    if exc and DEBUG:
        print(f"Exception: {str(exc)}")
        traceback.print_exc()

def log_success(msg: str):
    """Print success message."""
    print(f"✅ {msg}")

# ============================================================================
# VALIDATE CONFIGURATION
# ============================================================================

def validate_config():
    """Validate configuration before running."""
    print("\n" + "=" * 70)
    print("CONFIGURATION VALIDATION")
    print("=" * 70)
    
    is_valid, errors = Config.validate()
    
    if not is_valid:
        for error in errors:
            print(error)
        print("\n⚠️  Setup Instructions:")
        print("1. Copy .env.clean to .env")
        print("2. Fill in your API keys from:")
        print("   - Google: https://makersuite.google.com/app/apikey")
        print("   - Serper: https://serper.dev/api")
        print("3. Run again\n")
        sys.exit(1)
    
    print("✅ Google API Key: Configured")
    print("✅ Serper API Key: Configured")
    print("✅ Timeouts: Configured")
    print("✅ All required settings valid\n")

# ============================================================================
# INITIALIZE GEMINI
# ============================================================================

def initialize_gemini():
    """Initialize Gemini API with proper error handling."""
    try:
        log_debug(f"Initializing Gemini with API key (first 10 chars: {Config.GOOGLE_API_KEY[:10]}...)")
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        # Use latest available model (gemini-1.5.x no longer available)
        model = genai.GenerativeModel("gemini-2.5-pro")
        log_success("Gemini initialized with gemini-2.5-pro")
        return model
    except Exception as e:
        log_error("Failed to initialize Gemini", e)
        sys.exit(1)

# ============================================================================
# AGENT STATE
# ============================================================================

class AgentState(TypedDict):
    query: str
    urls: List[str]
    content: str
    summary: str
    errors: List[str]

# ============================================================================
# AGENT NODES
# ============================================================================

def search_node(state: AgentState) -> AgentState:
    """Search node - Fetch URLs from Serper API"""
    log_debug(f"🔍 SEARCH NODE: Searching for '{state['query']}'", "DEBUG")
    
    try:
        headers = {
            "X-API-KEY": Config.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        data = {"q": state["query"], "num": Config.MAX_SEARCH_RESULTS}
        
        log_debug(f"  → Sending request to Serper API (timeout: {Config.SERPER_TIMEOUT}s)", "DEBUG")
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=data,
            timeout=Config.SERPER_TIMEOUT
        )
        response.raise_for_status()
        
        results = response.json()
        urls = [result["link"] for result in results.get("organic", [])][:Config.MAX_URLS_TO_SCRAPE]
        
        if not urls:
            error_msg = "No URLs found in search results"
            log_debug(f"  ⚠️  {error_msg}", "DEBUG")
            state["errors"].append(error_msg)
            state["urls"] = []
        else:
            log_debug(f"  ✓ Found {len(urls)} URLs", "DEBUG")
            for i, url in enumerate(urls, 1):
                log_debug(f"    {i}. {url}", "DEBUG")
            state["urls"] = urls
        
        return state
        
    except requests.Timeout:
        error_msg = f"Serper API timeout (>{Config.SERPER_TIMEOUT}s)"
        log_error(error_msg)
        state["errors"].append(error_msg)
        state["urls"] = []
        return state
        
    except requests.RequestException as e:
        error_msg = f"Serper API request failed: {str(e)}"
        log_error(error_msg, e)
        state["errors"].append(error_msg)
        state["urls"] = []
        return state
        
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        log_error(error_msg, e)
        state["errors"].append(error_msg)
        state["urls"] = []
        return state

def browse_node(state: AgentState) -> AgentState:
    """Browse node - Scrape content from URLs"""
    if not state.get("urls"):
        log_debug("📄 BROWSE NODE: No URLs to scrape (skipped)", "DEBUG")
        state["content"] = ""
        return state
    
    log_debug(f"📄 BROWSE NODE: Scraping {len(state['urls'])} URLs", "DEBUG")
    
    combined_content = ""
    urls_scraped = 0
    urls_failed = 0
    
    for url in state["urls"]:
        try:
            log_debug(f"  → Scraping: {url[:60]}...", "DEBUG")
            
            response = requests.get(url, timeout=Config.SCRAPE_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            
            if text:
                # Limit content per URL
                text_limited = text[:Config.MAX_CONTENT_PER_URL]
                combined_content += text_limited + "\n"
                urls_scraped += 1
                log_debug(f"    ✓ Scraped {len(text_limited)} chars", "DEBUG")
            else:
                log_debug(f"    ⚠️  No text content found", "DEBUG")
                urls_failed += 1
                
        except requests.Timeout:
            log_debug(f"    ✗ Timeout (>{Config.SCRAPE_TIMEOUT}s)", "DEBUG")
            urls_failed += 1
            
        except Exception as e:
            log_debug(f"    ✗ Failed: {str(e)[:50]}", "DEBUG")
            urls_failed += 1
            continue
    
    # Limit total content
    combined_content = combined_content[:Config.MAX_TOTAL_CONTENT]
    
    log_debug(f"  ✓ Scraped {urls_scraped} URLs, Failed: {urls_failed}", "DEBUG")
    log_debug(f"  ✓ Total content: {len(combined_content)} chars", "DEBUG")
    
    if not combined_content:
        state["errors"].append("No content could be scraped from URLs")
    
    state["content"] = combined_content
    return state

def summarize_node(state: AgentState, model) -> AgentState:
    """Summarize node - Generate summary with Gemini"""
    if not state.get("content"):
        log_debug("✍️  SUMMARIZE NODE: No content to summarize (skipped)", "DEBUG")
        state["summary"] = "No content available for summarization"
        return state
    
    log_debug("✍️  SUMMARIZE NODE: Generating summary with Gemini", "DEBUG")
    
    try:
        content_preview = state["content"][:100].replace("\n", " ")
        log_debug(f"  → Content preview: {content_preview}...", "DEBUG")
        log_debug(f"  → Content length: {len(state['content'])} chars", "DEBUG")
        
        prompt = f"""Summarize this text in 5 clear bullet points.
Each bullet should be concise and informative.
Use proper formatting with • for bullets.

Content:
{state['content'][:Config.MAX_TOTAL_CONTENT]}"""
        
        log_debug(f"  → Sending to Gemini ({len(prompt)} chars in prompt)", "DEBUG")
        
        response = model.generate_content(prompt, timeout=Config.REQUEST_TIMEOUT)
        summary = response.text
        
        if not summary:
            log_debug(f"    ⚠️  Empty response from Gemini", "DEBUG")
            state["summary"] = "Error: Empty response from Gemini"
            state["errors"].append("Gemini returned empty response")
        else:
            log_debug(f"  ✓ Summary generated ({len(summary)} chars)", "DEBUG")
            state["summary"] = summary
        
        return state
        
    except Exception as e:
        error_msg = f"Summarization failed: {str(e)}"
        log_error(error_msg, e)
        state["errors"].append(error_msg)
        state["summary"] = f"Error: {error_msg}"
        return state

# ============================================================================
# BUILD GRAPH
# ============================================================================

def build_graph(model):
    """Build LangGraph workflow"""
    graph = StateGraph(AgentState)
    
    # Add nodes with closure to capture model
    graph.add_node("search", search_node)
    graph.add_node("browse", browse_node)
    graph.add_node("summarize", lambda state: summarize_node(state, model))
    
    # Add edges
    graph.set_entry_point("search")
    graph.add_edge("search", "browse")
    graph.add_edge("browse", "summarize")
    graph.add_edge("summarize", END)
    
    return graph.compile()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_pipeline(query: str) -> dict:
    """Run the complete pipeline"""
    print("\n" + "=" * 70)
    print("QUICKGLANCE - MULTI-AGENT RESEARCH PIPELINE")
    print("=" * 70 + "\n")
    
    # Initialize
    model = initialize_gemini()
    app = build_graph(model)
    
    # Prepare state
    initial_state = {
        "query": query,
        "urls": [],
        "content": "",
        "summary": "",
        "errors": []
    }
    
    log_debug(f"Query: {query}", "DEBUG")
    
    # Execute pipeline
    start_time = time.time()
    result = app.invoke(initial_state)
    elapsed_time = time.time() - start_time
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70 + "\n")
    
    print(f"⏱️  Execution Time: {elapsed_time:.2f}s\n")
    
    if result["urls"]:
        print(f"📌 URLs Found: {len(result['urls'])}")
        for i, url in enumerate(result["urls"], 1):
            print(f"   {i}. {url}")
        print()
    else:
        print("❌ No URLs found\n")
    
    if result.get("content"):
        content_len = len(result["content"])
        print(f"📄 Content Scraped: {content_len} characters\n")
    
    print("📋 SUMMARY")
    print("-" * 70)
    print(result.get("summary", "No summary generated"))
    print("-" * 70)
    
    if result.get("errors"):
        print(f"\n⚠️  Warnings/Errors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  • {error}")
    
    print("\n" + "=" * 70 + "\n")
    
    return result

# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Show debug config
    if DEBUG:
        print(Config.get_summary())
    
    # Validate
    validate_config()
    
    # Get query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your research query: ").strip()
    
    if not query:
        print("❌ Error: Query cannot be empty")
        sys.exit(1)
    
    # Run
    try:
        run_pipeline(query)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_error("Fatal error", e)
        sys.exit(1)
