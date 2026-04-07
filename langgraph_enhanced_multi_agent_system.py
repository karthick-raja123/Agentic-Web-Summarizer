"""
LangGraph ENHANCED Multi-Agent System with Intelligent Upgrades

Enhanced Features:
1. Query Expansion - Convert 1 query into 3 diverse queries
2. Content Ranking - Sort content by quality+relevance before summarizing
3. Deduplication - Remove duplicate/similar information
4. Chunk-based Summarization - Process content in chunks to avoid token overflow
5. URL Fallback - Replace failed URLs with backup URLs automatically

Architecture:
- Dynamic routing based on agent decisions
- Shared state across agents
- Conditional loops for retry logic
- Intelligent content processing
"""

import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
import os
import json
from enum import Enum
import difflib
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
from config import Config

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

# Initialize model with fallback support
from services.model_handler import create_model_with_fallback
try:
    model, CURRENT_MODEL_NAME = create_model_with_fallback(Config.GOOGLE_API_KEY)
except Exception as e:
    print(f"❌ Error initializing model: {e}")
    raise

SERPER_API_KEY = Config.SERPER_API_KEY

# ============================================================================
# ENHANCED STATE DEFINITIONS
# ============================================================================

class QueryExpansion(TypedDict):
    """Query expansion result"""
    original_query: str
    expanded_queries: List[str]
    angles: List[str]

class ScrapedContent(TypedDict):
    """Enhanced scraped content with ranking metrics"""
    url: str
    title: str
    content: str
    length: int
    quality_score: float
    source_type: str
    relevance_score: float
    combined_rank: float
    rank_position: int
    is_duplicate: bool
    chunk_count: int

class ContentChunk(TypedDict):
    """Individual content chunk for processing"""
    chunk_id: str
    url: str
    chunk_text: str
    chunk_summary: str
    tokens_estimated: int

class PipelineState(TypedDict):
    """Enhanced shared state across all agents"""
    # Input
    query: str
    user_intent: str
    
    # UPGRADE 1: Query Expansion
    query_expansion: QueryExpansion
    expanded_queries: List[str]
    
    # Planning phase
    plan: List[Dict[str, Any]]
    plan_iterations: int
    
    # Search phase (enhanced with backup URLs)
    search_queries: List[Dict[str, Any]]
    search_results: List[Dict[str, Any]]
    
    # Scraping phase (with fallback)
    urls: List[str]
    backup_urls: List[str]  # Fallback URLs
    failed_urls: List[str]
    scraped_content: List[ScrapedContent]
    scraping_iterations: int
    
    # UPGRADE 2: Content Ranking
    ranked_content: List[ScrapedContent]
    content_rankings: Dict[str, float]
    
    # UPGRADE 3: Deduplication
    deduplicated_content: List[ScrapedContent]
    duplicate_groups: Dict[str, List[str]]
    
    # UPGRADE 4: Chunk-based Summarization
    content_chunks: List[ContentChunk]
    chunk_summaries: List[str]
    
    # Evaluation phase
    evaluations: List[Dict[str, Any]]
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
    performance_metrics: Dict[str, float]

# ============================================================================
# UPGRADE 1: QUERY EXPANSION AGENT
# ============================================================================

def query_expansion_agent(state: PipelineState) -> PipelineState:
    """
    Query Expansion: Convert 1 query into 3 diverse queries
    
    Example:
    Input: "machine learning"
    Output: ["machine learning basics", "machine learning applications", "machine learning challenges"]
    """
    print("\n" + "="*80)
    print("🎯 QUERY EXPANSION AGENT")
    print("="*80)
    
    state["timestamps"]["expansion_start"] = datetime.now()
    query = state["query"]
    
    expansion_prompt = f"""You are an expert query strategist. Expand this query into 3 diverse search queries that explore different angles.

Original Query: "{query}"

Create 3 queries that:
1. Explore different aspects of the topic
2. Use different keywords and angles
3. Target different information needs

Provide JSON:
{{
    "original_query": "{query}",
    "expanded_queries": ["query1", "query2", "query3"],
    "angles": ["angle1_description", "angle2_description", "angle3_description"]
}}"""
    
    try:
        response = model.generate_content(expansion_prompt)
        response_text = response.text
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        expansion_data = json.loads(json_str)
        
        state["expanded_queries"] = expansion_data.get("expanded_queries", [query])
        state["query_expansion"] = {
            "original_query": query,
            "expanded_queries": expansion_data.get("expanded_queries", [query]),
            "angles": expansion_data.get("angles", [])
        }
        
        state["messages"].append(f"✓ Query expanded: {len(state['expanded_queries'])} queries created")
        print(f"✓ Expanded into {len(state['expanded_queries'])} diverse queries:")
        for i, q in enumerate(state['expanded_queries'], 1):
            print(f"  {i}. {q}")
            
    except Exception as e:
        state["expanded_queries"] = [
            query,
            f"{query} overview",
            f"{query} best practices"
        ]
        state["query_expansion"] = {
            "original_query": query,
            "expanded_queries": state["expanded_queries"],
            "angles": ["general", "guide", "best practices"]
        }
        state["messages"].append(f"⚠ Query expansion fallback: default expansion used")
        print(f"⚠ Using default expansion")
    
    state["current_agent"] = "expansion"
    state["next_agent"] = "search"
    
    return state

# ============================================================================
# AGENT 1: ENHANCED PLANNER AGENT
# ============================================================================

def planner_agent(state: PipelineState) -> PipelineState:
    """
    Enhanced Planner: Uses expanded queries for better planning
    """
    print("\n" + "="*80)
    print("🤖 PLANNER AGENT (Enhanced)")
    print("="*80)
    
    state["timestamps"]["planner_start"] = datetime.now()
    
    query = state["query"]
    expanded_queries = state.get("expanded_queries", [query])
    
    prompt = f"""You are a planning expert. Create a plan using these expanded queries.

Original Query: "{query}"
Expanded Queries: {expanded_queries}

Create a JSON response with search strategies for each query:
{{
    "user_intent": "core need",
    "plan": [
        {{"step": 1, "action": "action", "description": "description", "required": true}}
    ],
    "search_strategies": [
        {{"query": "query_text", "priority": 1, "depth": "deep", "angle": "angle_name"}},
        ...
    ]
}}

Include the expanded queries in your search strategies."""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        plan_data = json.loads(json_str)
        
        state["user_intent"] = plan_data.get("user_intent", query)
        state["plan"] = plan_data.get("plan", [])
        state["search_queries"] = plan_data.get("search_strategies", [])
        
    except:
        state["user_intent"] = query
        state["plan"] = [{"step": i, "action": "step", "description": f"Step {i}", "required": True} 
                        for i in range(1, 4)]
        state["search_queries"] = [
            {"query": q, "priority": i, "depth": "deep" if i == 1 else "shallow", "angle": f"angle_{i}"}
            for i, q in enumerate(expanded_queries, 1)
        ]
    
    state["messages"].append(f"✓ Plan created with expanded queries")
    state["current_agent"] = "planner"
    state["next_agent"] = "search"
    
    print(f"✓ Plan includes {len(state['search_queries'])} search queries")
    
    return state

# ============================================================================
# AGENT 2: ENHANCED SEARCH AGENT (with Backup URLs)
# ============================================================================

def search_agent(state: PipelineState) -> PipelineState:
    """
    Enhanced Search Agent: Includes backup URLs for fallback
    """
    print("\n" + "="*80)
    print("🔍 SEARCH AGENT (Enhanced with Backup URLs)")
    print("="*80)
    
    state["timestamps"]["search_start"] = datetime.now()
    
    all_urls = []
    backup_urls = []
    all_results = []
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    for search_query in state.get("search_queries", [{"query": state["query"]}]):
        query_str = search_query if isinstance(search_query, str) else search_query.get("query")
        priority = search_query.get("priority", 1) if isinstance(search_query, dict) else 1
        
        print(f"\n  Searching: {query_str} (priority: {priority})")
        
        try:
            data = {"q": query_str, "num": 10}  # Get 10 results per query
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                organic_results = results.get("organic", [])
                
                for idx, result in enumerate(organic_results):
                    url = result.get("link")
                    if url and url not in all_urls and url not in backup_urls:
                        if idx < 5:  # First 5 go to primary URLs
                            all_urls.append(url)
                        else:  # Rest go to backup
                            backup_urls.append(url)
                        
                        all_results.append({
                            "url": url,
                            "title": result.get("title", ""),
                            "snippet": result.get("snippet", ""),
                            "query": query_str,
                            "priority": priority
                        })
                
                print(f"  ✓ Found {len(organic_results)} results ({len([u for u in all_urls[-len(organic_results):]])} primary)")
                
            else:
                state["messages"].append(f"⚠ Search failed: {response.status_code}")
                
        except Exception as e:
            state["messages"].append(f"⚠ Search error: {str(e)}")
            print(f"  ⚠ Error: {str(e)}")
    
    # Limit primary URLs
    state["urls"] = all_urls[:8]
    state["backup_urls"] = backup_urls[:4]  # Keep 4 backup URLs
    state["failed_urls"] = []
    state["search_results"] = all_results
    
    state["messages"].append(f"✓ Collected {len(state['urls'])} URLs + {len(state['backup_urls'])} backups")
    print(f"\n✓ Primary URLs: {len(state['urls'])}, Backup URLs: {len(state['backup_urls'])}")
    
    state["current_agent"] = "search"
    state["next_agent"] = "scraper"
    
    return state

# ============================================================================
# AGENT 3: ENHANCED SCRAPER AGENT (with Fallback & Chunking)
# ============================================================================

def scraper_agent(state: PipelineState) -> PipelineState:
    """
    Enhanced Scraper: 
    - Fallback to backup URLs if primary fails
    - Chunk content for better processing
    """
    print("\n" + "="*80)
    print("🌐 SCRAPER AGENT (Enhanced with Fallback & Chunking)")
    print("="*80)
    
    state["timestamps"]["scraper_start"] = datetime.now()
    
    scraped_content: List[ScrapedContent] = []
    failed_urls = []
    
    urls_to_scrape = list(state.get("urls", []))
    backup_urls = list(state.get("backup_urls", []))
    
    for idx, url in enumerate(urls_to_scrape, 1):
        print(f"\n  [{idx}] Scraping: {url}")
        
        success = False
        try:
            response = requests.get(url, timeout=8)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract and process content
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "Unknown"
            
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            text = " ".join(text.split())
            
            # UPGRADE 4: Calculate chunk count
            chunk_count = max(1, len(text) // 1000)
            
            content = text[:2000]
            source_type = classify_content_type(url, soup)
            quality_score = compute_content_quality(content, soup)
            
            scraped_content.append({
                "url": url,
                "title": title_text,
                "content": content,
                "length": len(content),
                "quality_score": quality_score,
                "source_type": source_type,
                "relevance_score": 0.0,  # Will be set by evaluator
                "combined_rank": 0.0,    # Will be set by ranker
                "rank_position": 0,       # Will be set by ranker
                "is_duplicate": False,    # Will be set by deduplicator
                "chunk_count": chunk_count
            })
            
            print(f"  ✓ Success ({len(content)} chars, {chunk_count} chunks)")
            success = True
            
        except requests.Timeout:
            failed_urls.append(url)
            print(f"  ⚠ Timeout")
        except Exception as e:
            failed_urls.append(url)
            print(f"  ⚠ Error: {str(e)[:50]}")
    
    # UPGRADE 5: Fallback Logic - Replace failed URLs with backups
    for failed_url in failed_urls:
        if backup_urls:
            backup_url = backup_urls.pop(0)
            print(f"\n  ↻ Fallback: {failed_url} → {backup_url}")
            
            try:
                response = requests.get(backup_url, timeout=8)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, "html.parser")
                
                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else "Unknown"
                
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                text = soup.get_text(separator=" ", strip=True)
                text = " ".join(text.split())
                chunk_count = max(1, len(text) // 1000)
                
                content = text[:2000]
                source_type = classify_content_type(backup_url, soup)
                quality_score = compute_content_quality(content, soup)
                
                scraped_content.append({
                    "url": backup_url,
                    "title": title_text,
                    "content": content,
                    "length": len(content),
                    "quality_score": quality_score,
                    "source_type": source_type,
                    "relevance_score": 0.0,
                    "combined_rank": 0.0,
                    "rank_position": 0,
                    "is_duplicate": False,
                    "chunk_count": chunk_count
                })
                
                print(f"  ✓ Backup successful")
                
            except Exception as e:
                state["messages"].append(f"⚠ Backup also failed: {str(e)}")
                print(f"  ⚠ Backup failed too")
    
    state["scraped_content"] = scraped_content
    state["failed_urls"] = failed_urls
    state["messages"].append(f"✓ Scraped {len(scraped_content)} pages (used {len(failed_urls)} fallbacks)")
    
    print(f"\n✓ Scraped {len(scraped_content)} pages")
    
    state["current_agent"] = "scraper"
    state["next_agent"] = "ranker"
    
    return state

# ============================================================================
# UPGRADE 2: CONTENT RANKING AGENT
# ============================================================================

def ranking_agent(state: PipelineState) -> PipelineState:
    """
    Content Ranking: Sort content by combined relevance + quality score
    
    Ranks content before deduplication and summarization for better quality
    """
    print("\n" + "="*80)
    print("📊 RANKING AGENT (Intelligent Content Ranking)")
    print("="*80)
    
    state["timestamps"]["ranking_start"] = datetime.now()
    
    query = state.get("query", "")
    
    # Evaluate relevance for each piece of content
    for content in state.get("scraped_content", []):
        relevance_score = simple_relevance_check(content["content"], query)
        content["relevance_score"] = relevance_score
    
    # Rank content by combined score (quality + relevance)
    ranked_content = sorted(
        state.get("scraped_content", []),
        key=lambda x: (x["quality_score"] + x["relevance_score"]) / 2,
        reverse=True
    )
    
    # Assign rank positions
    for idx, content in enumerate(ranked_content, 1):
        content["combined_rank"] = (content["quality_score"] + content["relevance_score"]) / 2
        content["rank_position"] = idx
    
    state["ranked_content"] = ranked_content
    state["content_rankings"] = {
        c["url"]: c["combined_rank"] for c in ranked_content
    }
    
    print(f"✓ Ranked {len(ranked_content)} content items:")
    for i, content in enumerate(ranked_content[:5], 1):
        print(f"  {i}. {content['title'][:50]}... ({content['combined_rank']:.2f})")
    
    state["messages"].append(f"✓ Ranked {len(ranked_content)} items by quality+relevance")
    
    state["current_agent"] = "ranker"
    state["next_agent"] = "deduplicator"
    
    return state

# ============================================================================
# UPGRADE 3: DEDUPLICATION AGENT
# ============================================================================

def deduplication_agent(state: PipelineState) -> PipelineState:
    """
    Deduplication: Remove duplicate/similar information
    
    Uses similarity matching to identify and mark duplicates
    """
    print("\n" + "="*80)
    print("🔄 DEDUPLICATION AGENT (Remove Duplicate Information)")
    print("="*80)
    
    state["timestamps"]["dedup_start"] = datetime.now()
    
    ranked_content = state.get("ranked_content", [])
    duplicate_groups = {}
    
    # Find duplicates by comparing content similarity
    for i, content1 in enumerate(ranked_content):
        if content1["url"] in duplicate_groups:
            continue
        
        group = [content1["url"]]
        
        for j in range(i + 1, len(ranked_content)):
            content2 = ranked_content[j]
            
            # Calculate similarity ratio
            similarity = difflib.SequenceMatcher(
                None,
                content1["content"][:500],
                content2["content"][:500]
            ).ratio()
            
            # Mark as duplicate if similarity > 0.7 (70%)
            if similarity > 0.7:
                content2["is_duplicate"] = True
                group.append(content2["url"])
        
        if len(group) > 1:
            duplicate_groups[content1["url"]] = group
    
    # Keep only non-duplicate content
    deduplicated_content = [c for c in ranked_content if not c["is_duplicate"]]
    
    state["deduplicated_content"] = deduplicated_content
    state["duplicate_groups"] = duplicate_groups
    
    removed_count = len(ranked_content) - len(deduplicated_content)
    print(f"✓ Removed {removed_count} duplicate entries")
    
    if duplicate_groups:
        print(f"  Duplicate groups found:")
        for main_url, group in list(duplicate_groups.items())[:3]:
            print(f"    - {len(group)} similar items")
    
    state["messages"].append(f"✓ Deduplication: removed {removed_count} duplicates")
    
    state["current_agent"] = "deduplicator"
    state["next_agent"] = "chunker"
    
    return state

# ============================================================================
# UPGRADE 4: CHUNK-BASED PROCESSING AGENT
# ============================================================================

def chunking_agent(state: PipelineState) -> PipelineState:
    """
    Chunk-based Processing: Break content into chunks to avoid token overflow
    
    Creates content chunks for processing without token overflow issues
    """
    print("\n" + "="*80)
    print("📦 CHUNKING AGENT (Chunk-based Summarization Setup)")
    print("="*80)
    
    state["timestamps"]["chunking_start"] = datetime.now()
    
    content_chunks: List[ContentChunk] = []
    chunk_summaries = []
    
    for content in state.get("deduplicated_content", []):
        text = content["content"]
        url = content["url"]
        
        # Split content into chunks (~1000 chars each to avoid token overflow)
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        for chunk_idx, chunk_text in enumerate(chunks, 1):
            if chunk_text.strip():  # Only process non-empty chunks
                chunk_id = f"{content['url']}_chunk_{chunk_idx}"
                
                content_chunks.append({
                    "chunk_id": chunk_id,
                    "url": url,
                    "chunk_text": chunk_text,
                    "chunk_summary": "",  # Will be populated
                    "tokens_estimated": len(chunk_text) // 4  # Rough estimate
                })
    
    # Summarize each chunk using LLM
    query = state.get("query", "")
    for chunk in content_chunks:
        chunk_summary_prompt = f"""Summarize this content chunk in 1-2 sentences, focused on the query.

Query: "{query}"

Chunk:
{chunk['chunk_text'][:500]}...

Provide only the summary, no additional text."""
        
        try:
            response = model.generate_content(chunk_summary_prompt)
            chunk["chunk_summary"] = response.text.strip()
            chunk_summaries.append(response.text.strip())
        except:
            chunk["chunk_summary"] = "Content chunk processed"
            chunk_summaries.append("Content chunk processed")
    
    state["content_chunks"] = content_chunks
    state["chunk_summaries"] = chunk_summaries
    
    print(f"✓ Created {len(content_chunks)} chunks")
    print(f"✓ Generated summaries for all chunks")
    
    state["messages"].append(f"✓ Processed {len(content_chunks)} content chunks")
    
    state["current_agent"] = "chunker"
    state["next_agent"] = "evaluator"
    
    return state

# ============================================================================
# AGENT 4: ENHANCED EVALUATOR AGENT
# ============================================================================

def evaluator_agent(state: PipelineState) -> PipelineState:
    """
    Enhanced Evaluator: Uses ranked, deduplicated, chunked content
    """
    print("\n" + "="*80)
    print("🎯 EVALUATOR AGENT (Using Enhanced Content)")
    print("="*80)
    
    state["timestamps"]["evaluator_start"] = datetime.now()
    
    evaluations = []
    valid_content = []
    
    # Use deduplicated content (already ranked)
    for scraped in state.get("deduplicated_content", []):
        # Get chunk summaries for this content
        chunk_summaries = [c["chunk_summary"] for c in state.get("content_chunks", []) 
                          if c["url"] == scraped["url"]]
        
        combined_chunk_summary = " ".join(chunk_summaries[:3])  # Use top 3 chunks
        
        relevance_score = simple_relevance_check(
            combined_chunk_summary or scraped["content"],
            state.get("query", "")
        )
        
        combined_score = (scraped["quality_score"] + relevance_score) / 2
        
        evaluation = {
            "url": scraped["url"],
            "quality_score": combined_score,
            "relevance_score": relevance_score,
            "reasoning": f"Rank: {scraped['rank_position']}, Chunks: {len(chunk_summaries)}",
            "is_valid": combined_score > 0.4
        }
        
        evaluations.append(evaluation)
        
        if evaluation["is_valid"] and combined_score > 0.4:
            valid_content.append(scraped)
            print(f"  ✓ Valid: {scraped['title'][:40]}... ({combined_score:.2f})")
        else:
            print(f"  ✗ Filtered: {scraped['title'][:40]}... ({combined_score:.2f})")
    
    state["evaluations"] = evaluations
    state["valid_content"] = valid_content
    
    print(f"\n✓ Valid content: {len(valid_content)} sources")
    
    state["messages"].append(f"✓ Evaluation complete: {len(valid_content)} valid sources")
    state["current_agent"] = "evaluator"
    state["next_agent"] = "summarizer"
    
    return state

# ============================================================================
# AGENT 5: ENHANCED SUMMARIZER AGENT
# ============================================================================

def summarizer_agent(state: PipelineState) -> PipelineState:
    """
    Enhanced Summarizer: Uses chunk summaries to avoid token overflow
    """
    print("\n" + "="*80)
    print("📝 SUMMARIZER AGENT (Chunk-based Summarization)")
    print("="*80)
    
    state["timestamps"]["summarizer_start"] = datetime.now()
    
    # Use chunk summaries instead of full content
    summary_sources = []
    
    for valid_content in state.get("valid_content", []):
        chunks = [c for c in state.get("content_chunks", []) if c["url"] == valid_content["url"]]
        chunk_summaries = [c["chunk_summary"] for c in chunks]
        
        if chunk_summaries:
            summary_sources.append(f"[{valid_content['title']}]\n" + " ".join(chunk_summaries))
        else:
            summary_sources.append(f"[{valid_content['title']}]\n{valid_content['content'][:500]}")
    
    # Combine summaries (limited to avoid token overflow)
    combined_summary_input = "\n".join(summary_sources[:1500])  # Limit input
    
    summary_prompt = f"""Create a comprehensive summary from these chunked content summaries.

Query: {state.get('query', '')}

Content:
{combined_summary_input}

Provide JSON:
{{
    "overview": "2-3 sentence summary",
    "bullet_points": ["point1", "point2", "point3", "point4", "point5"],
    "considerations": "important notes"
}}"""
    
    try:
        response = model.generate_content(summary_prompt)
        response_text = response.text
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        summary_data = json.loads(json_str)
        
        overview = summary_data.get("overview", "")
        bullets = summary_data.get("bullet_points", [])[:7]
        considerations = summary_data.get("considerations", "")
        
        state["raw_summary"] = overview
        state["summary_bullets"] = bullets
        state["summary"] = f"""{overview}

Key Points:
{chr(10).join([f"• {b}" for b in bullets])}

{f"Considerations: {considerations}" if considerations else ""}"""
        
    except Exception as e:
        state["summary"] = f"Summary from {len(state.get('valid_content', []))} sources"
        state["summary_bullets"] = ["Content analyzed", "Summary created", "Ready for review"]
    
    state["messages"].append(f"✓ Summary generated using {len(summary_sources)} chunk sources")
    print(f"\n✓ Summary created")
    
    state["current_agent"] = "summarizer"
    state["next_agent"] = "reflection"
    
    return state

# ============================================================================
# AGENT 6: REFLECTION AGENT
# ============================================================================

def reflection_agent(state: PipelineState) -> PipelineState:
    """
    Reflection Agent: Evaluates quality and decides retry
    """
    print("\n" + "="*80)
    print("🔄 REFLECTION AGENT")
    print("="*80)
    
    state["timestamps"]["reflection_start"] = datetime.now()
    state["iterations"] = state.get("iterations", 0) + 1
    
    query = state.get("query", "")
    summary = state.get("summary", "")
    valid_sources = len(state.get("valid_content", []))
    
    reflection_prompt = f"""Evaluate this summary quality.

Query: "{query}"
Sources: {valid_sources}
Summary:
{summary}

Evaluate on: relevance, completeness, quality, coverage

Provide JSON:
{{
    "quality_score": 0.0-1.0,
    "assessment": "brief note",
    "needs_improvement": true/false
}}"""
    
    try:
        response = model.generate_content(reflection_prompt)
        response_text = response.text
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        reflection_data = json.loads(json_str)
        
        state["reflection_score"] = float(reflection_data.get("quality_score", 0.5))
        state["reflection_notes"] = reflection_data.get("assessment", "")
        state["needs_improvement"] = reflection_data.get("needs_improvement", False)
        
    except:
        state["reflection_score"] = min(1.0, 0.5 + (valid_sources * 0.1))
        state["reflection_notes"] = "Auto-evaluated"
        state["needs_improvement"] = state["reflection_score"] < 0.6
    
    should_retry = (
        state["needs_improvement"] and 
        state["iterations"] < state.get("max_iterations", 2)
    )
    
    if should_retry:
        state["next_agent"] = "search"
        print(f"\n⟳ Score: {state['reflection_score']:.2f} - Retrying")
    else:
        state["next_agent"] = "end"
        print(f"\n✓ Score: {state['reflection_score']:.2f} - Accepted")
    
    state["messages"].append(f"✓ Reflection: {state['reflection_score']:.2f}")
    state["current_agent"] = "reflection"
    
    return state

# ============================================================================
# ROUTER & UTILITIES
# ============================================================================

def route_after_reflection(state: PipelineState) -> str:
    """Dynamic routing after reflection"""
    if state.get("next_agent") == "search":
        return "search"
    else:
        return END

def classify_content_type(url: str, soup) -> str:
    """Classify content type"""
    url_lower = url.lower()
    
    if any(x in url_lower for x in ["github", "code"]):
        return "technical"
    elif any(x in url_lower for x in ["blog", "article"]):
        return "article"
    elif any(x in url_lower for x in ["wiki", "doc"]):
        return "documentation"
    elif any(x in url_lower for x in ["forum", "reddit"]):
        return "community"
    else:
        return "general"

def compute_content_quality(content: str, soup) -> float:
    """Compute content quality (0.0-1.0)"""
    score = 0.5
    
    if len(content) > 500:
        score += 0.2
    if soup.find_all("h1") or soup.find_all("h2"):
        score += 0.15
    if soup.find_all("ul") or soup.find_all("ol"):
        score += 0.1
    if len(content) < 200:
        score -= 0.3
    
    return min(1.0, max(0.0, score))

def simple_relevance_check(content: str, query: str) -> float:
    """Simple relevance check"""
    query_words = set(query.lower().split())
    content_lower = content.lower()
    
    matches = sum(1 for word in query_words if word in content_lower)
    return min(1.0, matches / len(query_words)) if query_words else 0.5

# ============================================================================
# GRAPH CREATION
# ============================================================================

def create_graph():
    """
    Create enhanced LangGraph with all improvements
    
    Flow:
    START → Expansion → Planner → Search → Scraper → Ranker → Deduplicator → 
    Chunker → Evaluator → Summarizer → Reflection → (Loop or END)
    """
    workflow = StateGraph(PipelineState)
    
    # Add all enhanced nodes
    workflow.add_node("expansion", query_expansion_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("search", search_agent)
    workflow.add_node("scraper", scraper_agent)
    workflow.add_node("ranker", ranking_agent)
    workflow.add_node("deduplicator", deduplication_agent)
    workflow.add_node("chunker", chunking_agent)
    workflow.add_node("evaluator", evaluator_agent)
    workflow.add_node("summarizer", summarizer_agent)
    workflow.add_node("reflection", reflection_agent)
    
    # Set up edges
    workflow.set_entry_point("expansion")
    
    # Linear path with enhancements
    workflow.add_edge("expansion", "planner")
    workflow.add_edge("planner", "search")
    workflow.add_edge("search", "scraper")
    workflow.add_edge("scraper", "ranker")
    workflow.add_edge("ranker", "deduplicator")
    workflow.add_edge("deduplicator", "chunker")
    workflow.add_edge("chunker", "evaluator")
    workflow.add_edge("evaluator", "summarizer")
    workflow.add_edge("summarizer", "reflection")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {"search": "search", END: END}
    )
    
    return workflow.compile()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "LangGraph ENHANCED Multi-Agent System - All Intelligence Upgrades".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    user_query = input("\n📝 Enter your topic to summarize: ").strip()
    if not user_query:
        user_query = "Machine learning applications in healthcare"
    
    # Initialize enhanced state
    initial_state: PipelineState = {
        "query": user_query,
        "user_intent": "",
        "query_expansion": {"original_query": "", "expanded_queries": [], "angles": []},
        "expanded_queries": [],
        "plan": [],
        "plan_iterations": 0,
        "search_queries": [],
        "search_results": [],
        "urls": [],
        "backup_urls": [],
        "failed_urls": [],
        "scraped_content": [],
        "scraping_iterations": 0,
        "ranked_content": [],
        "content_rankings": {},
        "deduplicated_content": [],
        "duplicate_groups": {},
        "content_chunks": [],
        "chunk_summaries": [],
        "evaluations": [],
        "valid_content": [],
        "raw_summary": "",
        "summary": "",
        "summary_bullets": [],
        "reflection_score": 0.0,
        "reflection_notes": "",
        "needs_improvement": False,
        "iterations": 0,
        "max_iterations": 2,
        "timestamps": {},
        "messages": [],
        "current_agent": "start",
        "next_agent": "expansion",
        "error": None,
        "performance_metrics": {}
    }
    
    # Run enhanced graph
    graph = create_graph()
    
    print(f"\n▶ Starting enhanced pipeline for: '{user_query}'")
    print("─" * 80)
    
    try:
        result = graph.invoke(initial_state)
        
        # Display results
        print("\n" + "="*80)
        print("📊 FINAL RESULTS (Enhanced System)")
        print("="*80)
        
        print(f"\n🎯 Query Expansion:")
        for i, q in enumerate(result.get("expanded_queries", []), 1):
            print(f"  {i}. {q}")
        
        print(f"\n📈 Content Ranking:")
        print(f"  Total content: {len(result.get('ranked_content', []))}")
        print(f"  Duplicates removed: {len(result.get('duplicate_groups', {})) > 0}")
        print(f"  Content chunks: {len(result.get('content_chunks', []))}")
        
        print(f"\n📝 Summary ({len(result.get('summary_bullets', []))} points):")
        print(f"  {result.get('summary', 'No summary')[:300]}...")
        
        print(f"\n✨ Quality Score: {result.get('reflection_score', 0):.2f}")
        print(f"   Valid sources: {len(result.get('valid_content', []))}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
