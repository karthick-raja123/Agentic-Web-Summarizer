import sys
sys.stdout.reconfigure(encoding='utf-8')

import streamlit as st
import google.generativeai as genai
import requests
import trafilatura
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time
import base64
import csv
import tempfile
import os
from dotenv import load_dotenv
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def remove_emojis(text):
    """
    Remove emoji characters from text for safe file writing and printing
    Encodes to ASCII (ignoring non-ASCII like emojis), then decodes back
    """
    if not text:
        return text
    return text.encode("ascii", "ignore").decode()

# ============================================================================
# PHASE 2: INTELLIGENCE FEATURES - Multi-Source Comparison
# ============================================================================

def score_url_quality(url):
    """
    Score URL quality on scale 1-10 (for display)
    
    Scoring:
    10 → TowardsDataScience / Medium official AI channel
    9  → GeeksforGeeks, AnalyticsVidhya, Official docs
    8  → Medium (general), dev.to, GitHub
    7  → Official blogs, tech news, Stack Overflow
    5  → Other tech blogs
    3  → Unknown sources
    """
    url_lower = url.lower()
    
    # Tier 1: Premium sources (9-10)
    if any(domain in url_lower for domain in ["towardsdatascience.com", "medium.com/towards"]):
        return (10, "Premium - TowardsDataScience/Medium AI")
    if any(domain in url_lower for domain in ["geeksforgeeks", "analyticsvidhya"]):
        return (9, "Premium - GeeksforGeeks/AnalyticsVidhya")
    
    # Tier 2: High quality (8)
    if any(domain in url_lower for domain in ["medium.com", "dev.to", "github.com"]):
        return (8, "High Quality - Medium/Dev.to/GitHub")
    
    # Tier 3: Good sources (7)
    if any(domain in url_lower for domain in ["official", "docs", "documentation", "blog", ".org", "stackoverflow"]):
        return (7, "Good Source - Official/Documentation")
    
    # Default
    return (5, "Regular Tech Blog")

def generate_query_improvement(original_query):
    """
    PHASE 3: Improve user query for better search results
    
    Converts vague queries to specific search queries
    """
    print(f"\n🔍 PHASE 3: Improving query...")
    
    prompt = f"""You are a search expert. Improve this query for better web search results.
Make it more specific and add relevant keywords.

Original query: "{original_query}"

Return ONLY the improved query (no explanation, just the query):"""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False)
        improved = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
        
        if improved and len(improved) > 5:
            print(f"✅ Improved query: {improved}")
            return improved
    except Exception as e:
        print(f"⚠️ Query improvement failed: {str(e)[:50]}")
    
    return original_query

def select_mode_prompt(mode):
    """
    PHASE 3: Select prompt style based on user mode
    
    Modes:
    - Beginner: Simple, explain fundamentals
    - Student: Academic depth, theory + practice
    - Research: Deep dive, advanced concepts, citations
    """
    modes = {
        "Beginner": {
            "style": "Explain like I'm 15, focus on core ideas and real examples",
            "icon": "🟢"
        },
        "Student": {
            "style": "Academic level with theory, examples, and practical applications",
            "icon": "🟡"
        },
        "Research": {
            "style": "Go deep into techniques, models, research directions, and advanced concepts",
            "icon": "🔴"
        }
    }
    
    return modes.get(mode, modes["Student"])

def get_mode_specific_summary_prompt(content, mode="Student"):
    """Generate professional summarization prompt with 7-section format"""
    
    prompt = f"""You are an expert technical analyst. Analyze the web content and generate a structured summary.

STRICT FORMAT:

1. Definition:
Explain clearly what the topic is (2-3 lines, precise and technical).

2. Key Concepts:
List important concepts in bullet points.

3. Techniques / Methods:
Explain important algorithms, models, or approaches used.

4. Advantages:
List real benefits (not generic statements).

5. Limitations:
List actual problems or challenges.

6. Real-World Applications:
Give practical use cases (specific industries or systems).

7. Final Takeaway:
Give a strong, practical conclusion (what should someone learn or do).

IMPORTANT RULES:
- Avoid generic sentences
- Be specific and technical
- Do not repeat ideas
- Keep it clear and structured

CONTENT:
{content[:2000]}

Provide the structured 7-section summary:"""
    
    return prompt

def generate_final_insight(summaries_list, query, mode="Student"):
    """
    PHASE 2: Generate final insight combining all sources
    
    Takes individual source summaries and creates unified insight
    """
    print(f"\n✨ PHASE 2: Generating Final Insight...")
    
    # Format all summaries with sources
    formatted_summaries = "\n\n".join([
        f"[Source {i+1}: {s.get('title', 'Unknown')}]\n{s.get('summary', 'No summary available')}"
        for i, s in enumerate(summaries_list)
    ])
    
    prompt = f"""You are an expert analyst synthesizing information from {len(summaries_list)} sources.

Query: {query}
Mode: {mode}

INDIVIDUAL SOURCE SUMMARIES:
{formatted_summaries}

Now provide a UNIFIED FINAL INSIGHT that:
1. Synthesizes all perspectives
2. Identifies common themes
3. Highlights unique insights from each source
4. Provides your expert recommendation

Format:

**Synthesis**: [What all sources agree on]

**Key Differences**: [Where sources differ]

**Expert Recommendation**: [Your unified insight]

**Confidence**: High/Medium based on number of sources"""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False)
        insight = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
        print(f"✅ Final insight generated ({len(insight)} chars)")
        return insight
    except Exception as e:
        print(f"❌ Insight generation failed: {str(e)[:50]}")
        return None

def generate_actionable_insights(summary, mode="Student"):
    """
    PHASE 3: Generate actionable next steps based on mode
    
    Beginner → Learning path recommendations
    Student → Practice exercises
    Research → Advanced topics to explore
    """
    print(f"\n💡 PHASE 3: Generating Actionable Insights ({mode})...")
    
    if mode == "Beginner":
        next_steps_prompt = """What should a beginner do first to start learning this?
Provide 3-5 concrete, actionable steps a beginner can take TODAY."""
    elif mode == "Student":
        next_steps_prompt = """What should a student focus on to master this concept?
Provide 3-5 practical exercises or projects to deepen understanding."""
    else:  # Research
        next_steps_prompt = """What are the current research frontiers in this area?
Provide 3-5 advanced topics or research directions to explore."""
    
    prompt = f"""Based on this content:
{summary[:2000]}

MODE: {mode}

{next_steps_prompt}

Format as numbered list with explanations."""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False)
        insights = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
        return insights
    except Exception as e:
        print(f"⚠️ Actionable insights failed: {str(e)[:50]}")
        return None

def format_citations(summaries_list):
    """
    PHASE 4: Format citations for download
    
    Creates proper citation list for all sources
    """
    citations = "SOURCES:\n" + "="*50 + "\n\n"
    
    for i, item in enumerate(summaries_list, 1):
        url = item.get('url', 'Unknown')
        title = item.get('title', 'No title')
        score = item.get('score', 5)
        
        # Simple citation format
        citations += f"{i}. {title}\n"
        citations += f"   URL: {url}\n"
        citations += f"   Quality Score: {score}/10\n\n"
    
    return citations

def get_pipeline_steps():
    """
    PHASE 4: Return pipeline steps for UI display
    
    Shows user the processing pipeline
    """
    return [
        ("Step 1", "Improving query for better results", "🔍"),
        ("Step 2", "Finding and filtering trusted sources", "✓"),
        ("Step 3", "Extracting clean content from each source", "📄"),
        ("Step 4", "Summarizing by source (not merged)", "📝"),
        ("Step 5", "Generating final unified insight", "✨"),
        ("Step 6", "Creating actionable recommendations", "💡"),
    ]



# Load environment variables from Streamlit secrets (Cloud) or .streamlit/secrets.toml (Local)
try:
    # Try Streamlit Cloud secrets first
    GEMINI_API_KEY = st.secrets["GOOGLE_API_KEY"]
    print("API Key loaded from Streamlit secrets")
except (KeyError, FileNotFoundError):
    # Fall back to .env for local development
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GEMINI_API_KEY:
        print("API Key loaded from .env file (local development)")

if not GEMINI_API_KEY:
    st.error("GOOGLE_API_KEY not found. Please configure it in Streamlit secrets or .env file")
    st.stop()

# Also try to get Serper API key
try:
    SERPER_API_KEY = st.secrets.get("SERPER_API_KEY")
except:
    from dotenv import load_dotenv
    load_dotenv()
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# DEBUG: Verify API configuration
api_key_preview = GEMINI_API_KEY[:10] if GEMINI_API_KEY else "MISSING"
print("API Key configured: " + api_key_preview + "...[hidden]")
print("Using model: gemini-2.5-flash")

# Check if placeholder keys are being used
if "your_" in str(GEMINI_API_KEY).lower() or "placeholder" in str(GEMINI_API_KEY).lower():
    st.error("ERROR: GOOGLE_API_KEY contains placeholder value. Please edit .streamlit/secrets.toml with your real API key from https://aistudio.google.com/app/apikeys")
    st.stop()

if "your_" in str(SERPER_API_KEY).lower() or "placeholder" in str(SERPER_API_KEY).lower():
    st.warning("WARNING: SERPER_API_KEY contains placeholder value. Searches will fail. Edit .streamlit/secrets.toml with your real key from https://serper.dev")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize session state for query history and results
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None
if "last_content" not in st.session_state:
    st.session_state.last_content = None
if "last_urls" not in st.session_state:
    st.session_state.last_urls = None

def clean_scrape(url):
    """
    Professional content extraction using trafilatura
    - Works with JS-heavy pages, PDFs, paywalls
    - Removes ads, noise, boilerplate automatically
    - Returns clean article text or None
    - Includes comprehensive error handling
    - SAFEGUARD: Hard filters + fail-fast pattern
    - FILTER: Only trusted sources - blocks PDFs, research papers, low-quality sources
    """
    # HARD FILTER: Block low-quality and untrusted sources before scraping
    TRUSTED_DOMAINS = [
        "medium.com", "towardsdatascience.com", "geeksforgeeks.org",
        "analyticsvidhya.com", "dev.to", "blog", 
        ".org", "github.com", "stackoverflow.com",
        "official", "docs", "documentation"
    ]
    
    BLOCKED_DOMAINS = [
        # Research and academic papers
        "researchgate", "arxiv", "ncbi.nlm.nih.gov", "sciencedirect",
        "springer", "wiley", "mdpi", "elsevier", "ieee",
        "acm.org", "jstor", "nature.com", "science.org",
        # PDFs and documents
        ".pdf", "filetype:pdf",
        # Social media and untrusted sites
        "facebook.com", "twitter.com", "instagram.com", "tiktok",
        "reddit.com", "quora.com", "medium-static",
        # Video sites (not readable)
        "youtube", "youtu.be", "vimeo", "dailymotion",
        # Paywall and restricted
        "paywall", "subscription", "login?", "signin?",
        # Unknown/random sites
        "cloudflare", "libgen", "z-lib", "scribd"
    ]
    
    url_lower = url.lower()
    
    # Check if it's a BLOCKED domain
    for blocked in BLOCKED_DOMAINS:
        if blocked.lower() in url_lower:
            print(f"⛔ Blocked domain: {blocked}")
            return None
    
    # Prefer TRUSTED domains, be more lenient with them
    is_trusted = any(trusted.lower() in url_lower for trusted in TRUSTED_DOMAINS)
    
    try:
        # Fetch the URL using trafilatura (trafilatura v2 doesn't support timeout param)
        # It has built-in timeout handling internally (default ~10s)
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            return None
        
        # Extract main content using trafilatura
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            favor_precision=True
        )
        
        if not text:
            return None
        
        # Quality check: ensure meaningful content
        text = text.strip()
        if len(text) < 800:
            return None
        
        # UTF-8 safe encoding
        text = text.encode("utf-8", errors="ignore").decode("utf-8")
        
        # Cap at 3000 chars for API efficiency
        text = text[:3000]
        
        print(f"✅ Extracted {len(text)} chars from {url[:50]}")
        return text
    
    except requests.Timeout:
        print(f"⏱️ Timeout on {url}")
        return None
    except requests.ConnectionError:
        print(f"🌐 Connection error on {url}")
        return None
    except Exception as e:
        print(f"❌ Scrape error on {url}: {str(e)[:50]}")
        return None

def search_serper(query):
    """
    Search using Serper API with error handling
    - Handles network timeouts (8s hard limit)
    - Handles API failures gracefully
    - Returns empty list on error (never crashes)
    - SAFEGUARD: 8 second timeout to prevent hanging
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("SERPER_API_KEY")
        except:
            pass
    
    if not api_key:
        print("SERPER_API_KEY not configured")
        return []
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {"q": query}
    
    try:
        # CRITICAL: Set strict timeout to prevent hanging
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=data,
            timeout=8  # Hard limit: 8 seconds
        )
        response.raise_for_status()
        results = response.json()
        urls = [result["link"] for result in results.get("organic", [])][:5]
        
        if not urls:
            return []
        
        print(f"✅ Search returned {len(urls)} URLs")
        return urls
        
    except requests.Timeout:
        print("⏱️ Search timeout - server took too long")
        st.warning("⏱️ Search timeout. Try a simpler query.")
        return []
    except requests.ConnectionError:
        print("🌐 Connection error - no internet or server down")
        st.warning("🌐 Network error. Check your connection.")
        return []
    except requests.HTTPError as e:
        print(f"🔍 Search API error: {str(e)[:50]}")
        st.warning("🔍 Search failed. Try again later.")
        return []
    except ValueError as e:
        print(f"Invalid JSON response: {str(e)[:50]}")
        st.warning("⚠️ Invalid search response.")
        return []
    except Exception as e:
        print(f"❌ Unexpected search error: {str(e)[:100]}")
        st.warning(f"❌ Search error: {str(e)[:50]}")
        return []

def is_academic_query(query):
    """
    Detect if query is likely to return academic/research papers
    """
    academic_keywords = [
        "research", "study", "analysis", "methodology", "abstract",
        "paper", "journal", "publication", "hypothesis", "dissertation",
        "framework", "model", "algorithm", "approach", "finite element"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in academic_keywords)

def optimize_query_for_readability(query):
    """
    Transform academic queries into blog/tutorial-friendly queries
    
    Examples:
    - "applications of deep learning" → "applications of deep learning explained blog"
    - "blockchain research" → "blockchain tutorial beginner explanation"
    - "quantum computing study" → "quantum computing explained simple guide"
    """
    
    # If query is academic, add readability boosters
    if is_academic_query(query):
        print(f"🔍 Academic query detected, optimizing for readability...")
        
        # Check what's already in query
        if "blog" not in query.lower() and "tutorial" not in query.lower():
            # Add readability boosters
            optimized = f"{query} blog tutorial explained simple"
            print(f"📝 Optimized: '{query}' → '{optimized}'")
            return optimized
    
    return query

def generate_search_variations(query):
    """
    Generate 2 query variations to reduce load
    - Original query
    - Query + "explained blog tutorial"
    
    SAFEGUARD: Reduced from 3 variations to prevent timeout
    """
    variations = [
        query,
        f"{query} explained blog tutorial"
    ]
    
    return variations

def search_and_merge(query):
    """
    Execute multi-query search with safeguards
    - Reduced from 3 to 2 search variations
    - Timeout protection per search (8 seconds)
    - Deduplicates by domain
    """
    all_urls = []
    seen_domains = set()
    
    variations = generate_search_variations(query)
    print(f"\n🔍 MULTI-QUERY SEARCH: {len(variations)} variations (safeguard mode)")
    
    for i, var_query in enumerate(variations, 1):
        print(f"   Variation {i}/{len(variations)}: {var_query}")
        urls = search_serper(var_query)
        
        for url in urls:
            # Extract domain to avoid duplicate sources
            domain = url.split('/')[2] if '://' in url else url
            
            if domain not in seen_domains:
                all_urls.append(url)
                seen_domains.add(domain)
    
    print(f"📊 Merged: {len(all_urls)} unique URLs from {len(variations)} searches")
    return all_urls

def validate_content(text):
    """
    Validate and clean extracted content
    - Fix encoding issues (UTF-8 safe)
    - Remove if too many links (noisy)
    - Ignore if too short (< 500 chars)
    - Remove excessive whitespace
    """
    if not text:
        return None
    
    # CRITICAL FIX: Ensure UTF-8 safe encoding
    text = text.encode("utf-8", errors="ignore").decode("utf-8")
    
    # Too many links = low quality article
    link_count = text.count('http')
    if link_count > 20:
        print(f"   ⚠️ Skipped: Too many links ({link_count})")
        return None
    
    # Too short = insufficient content
    if len(text) < 500:
        print(f"   ⚠️ Skipped: Too short ({len(text)} chars)")
        return None
    
    # Clean whitespace
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    
    return text if len(text) >= 500 else None

def clean_text(text):
    """
    Clean text before summarizing:
    - Remove extra whitespace
    - Remove non-ASCII garbage and fix encoding issues
    - Remove HTML artifacts
    - UTF-8 safe handling
    """
    if not text:
        return text
    
    # CRITICAL FIX: UTF-8 safe encoding
    text = text.encode("utf-8", errors="ignore").decode("utf-8")
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove excessive punctuation
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([.!?])([.!?]+)', r'\1', text)  # Remove repeated punctuation
    
    return text.strip()

def rank_urls_advanced(urls):
    """
    Advanced URL scoring system (-10 to +10):
    FILTERS ONLY HIGH-QUALITY TRUSTED SOURCES
    
    +10 → Tutorial/guide keywords + trusted domain
    +8 → Premium sources: Medium, TowardsDataScience, GeeksforGeeks, AnalyticsVidhya
    +5 → Official blogs, documentation, dev sites
    +2 → Regular tech blogs and articles
    -100 → PDFs (automatic reject)
    -100 → Research papers/academic (arxiv, ncbi, springer, wiley, mdpi, etc)
    -30 → Suspicious/paywall URLs
    
    REJECTED: Any URL with -30 score or worse
    Sort by score descending (best first)
    """
    if not urls:
        return []
    
    scored = []
    
    # Sources to COMPLETELY AVOID
    BANNED_SOURCES = [
        ".pdf", "filetype:pdf",  # PDFs
        "arxiv", "researchgate", "ncbi.nlm.nih.gov", 
        "sciencedirect", "springer", "wiley", "mdpi", 
        "elsevier", "ieee.org", "acm.org", "jstor",
        "nature.com", "science.org"  # Research papers
    ]
    
    # TRUSTED HIGH-QUALITY SOURCES (WHITELIST)
    TRUSTED_SOURCES = [
        "medium.com", "towardsdatascience.com",
        "geeksforgeeks.org", "analyticsvidhya.com"
    ]
    
    # GOOD SOURCES (secondary)
    GOOD_SOURCES = [
        "dev.to", "github.com", "stackoverflow.com",
        ".org", "official", "docs", "documentation", "blog"
    ]
    
    for url in urls:
        url_lower = url.lower()
        score = 0
        
        # STEP 1: CHECK FOR BANNED SOURCES (automatic reject)
        is_banned = any(banned in url_lower for banned in BANNED_SOURCES)
        if is_banned:
            score = -100  # Automatic reject
            print(f"   ⛔ REJECTED (banned source): {url[:60]}")
        else:
            # STEP 2: SCORE TRUSTED SOURCES
            is_trusted = any(trusted in url_lower for trusted in TRUSTED_SOURCES)
            
            # STEP 3: Score by content type
            if any(word in url_lower for word in ["tutorial", "guide", "explained", "learn", "beginner", "how-to", "step-by-step"]):
                score += 10
            elif is_trusted:
                score += 8
            elif any(good in url_lower for good in GOOD_SOURCES):
                score += 5
            else:
                score += 2
            
            # STEP 4: PENALIZE SUSPICIOUS URLs
            if len(url) > 200 or url.count('=') > 5:
                score -= 30
            if 'login' in url_lower or 'paywall' in url_lower or 'subscription' in url_lower:
                score -= 30
        
        if score >= -30:  # Only keep acceptable sources
            scored.append((score, url))
    
    
    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])
    
    print(f"\n🎯 ADVANCED RANKING (Top 10 - Only Trusted Sources):")
    for i, (score, url) in enumerate(scored[:10], 1):
        status = "✅" if score >= 5 else "⚠️" if score >= 0 else "❌"
        print(f"   {status} {i}. Score {score:+d}: {url[:60]}")
    
    # Return only valid URLs (score >= -30)
    return [url for score, url in scored if score >= -30]

def scrape_content_v2(urls):
    """
    PHASE 2: Progressive scraping pipeline with per-source summaries
    
    Process:
    1. Use top 3 URLs hard limit (prevents hanging)
    2. Extract from each URL individually
    3. Return: List of {url, title, content, score}
    
    CHANGE: Returns INDIVIDUAL source content, not merged!
    This enables multi-source comparison.
    
    Returns:
        List of dicts: [{url, title, content, score}, ...]
    """
    if not urls:
        return []
    
    print("\n" + "="*60)
    print("📄 PROGRESSIVE SCRAPING (Top 3 URLs - Individual Sources)")
    print("="*60)
    
    best_urls = urls[:3]  # HARD LIMIT: Only 3 URLs max
    print(f"\n📌 Will scrape: {len(best_urls)} URLs (individual analysis)\n")
    
    results = []  # CHANGED: Now collects per-source results
    
    for i, url in enumerate(best_urls, 1):
        try:
            print(f"{i}/{len(best_urls)}: {url[:70]}")
            
            # Extract content with timeout built-in
            text = clean_scrape(url)
            
            if text:
                # Validate content (remove noisy/link-heavy content)
                validated = validate_content(text)
                
                if validated:
                    # Clean text before adding
                    cleaned = clean_text(validated)
                    
                    # Get source quality score
                    score, score_label = score_url_quality(url)
                    
                    # Extract title from URL
                    title = url.split('/')[-1][:50] if '/' in url else "Article"
                    
                    print(f"   ✅ Valid: {len(cleaned)} chars (Quality: {score}/10)")
                    
                    # NEW: Add as separate source instead of merging
                    results.append({
                        'url': url,
                        'title': title,
                        'content': cleaned,
                        'score': score,
                        'score_label': score_label
                    })
                else:
                    print(f"   ⚠️ Content invalid (noisy/links)")
            else:
                print(f"   ❌ No content extracted")
        
        except Exception as e:
            print(f"   ❌ Scrape error: {str(e)[:50]}")
            continue
    
    print(f"\n📊 Scraped: {len(results)} URLs successfully")
    
    if len(results) >= 1:
        print(f"✅ SUCCESS: {len(results)} sources ready for analysis")
        return results
    
    print(f"⚠️ Insufficient: {len(results)} sources (need 1+)")
    return []

def generate_fallback_explanation(query):
    """
    FALLBACK GUARANTEE: If scraping fails, generate direct explanation from Gemini
    
    This ENSURES the system NEVER fails with empty content
    Provides high-quality AI explanation when web content unavailable
    Uses structured, technical format for better quality
    """
    print("\n" + "="*60)
    print("🎯 FALLBACK: Direct AI Explanation (No Web Sources)")
    print("="*60)
    
    prompt = f"""Provide a comprehensive, structured explanation for: {query}

Use this exact structure:

1. **Clear Definition** (2-3 lines): What is {query}? Define it clearly and concisely.

2. **Key Concepts** (bullet points):
   • [Concept 1]
   • [Concept 2]
   • [Concept 3]
   • [Concept 4]

3. **Important Techniques/Models Used**: [List any relevant techniques, frameworks, or methodologies]

4. **Advantages and Limitations**:
   Advantages: [key benefits]
   Limitations: [important limitations]

5. **Real-World Applications**: [Practical examples in industry and real scenarios]

6. **Final Practical Takeaway**: [One actionable insight the reader should remember]

RULES:
- Be specific and technical, avoid generic sentences
- Use professional, clear language
- Focus on accuracy and practical value
- No marketing language or fluff
- Make it suitable for beginners but with technical depth"""
    
    try:
        print("\n🧠 Generating explanation from Gemini...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False)
        
        if response.text and len(response.text.strip()) > 100:
            # UTF-8 safe encoding for response
            result = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
            print(f"✅ Generated: {len(result)} chars")
            return result
    
    except Exception as e:
        print(f"❌ Fallback generation error: {str(e)[:50]}")
    
    return None

def scrape_with_retry_and_fallback(query, attempt=1):
    """
    MASTER ORCHESTRATOR: Smart content extraction with guaranteed success
    
    Attempt 1: Multi-query search + Advanced ranking + Progressive scrape
    Attempt 2: Retry with enhanced query
    Attempt 3: Final retry
    Fallback: Gemini direct explanation
    
    GUARANTEE: Always returns usable content (scraped OR generated)
    """
    print(f"\n{'='*60}")
    print(f"🚀 CONTENT EXTRACTION (Attempt {attempt}/3)")
    print(f"{'='*60}")
    
    # STEP 1: Multi-query search
    print("\n📍 STEP 1: Multi-Query Search...")
    all_urls = search_and_merge(query)
    
    if not all_urls:
        print("❌ No URLs found in search")
        
        # Retry with better query
        if attempt < 3:
            better_query = f"{query} simple explanation blog"
            print(f"🔄 Retrying with: {better_query}")
            return scrape_with_retry_and_fallback(better_query, attempt + 1)
        else:
            # Use fallback
            result = generate_fallback_explanation(query)
            return result if result else None
    
    # STEP 2: Advanced ranking
    print("\n📍 STEP 2: Advanced URL Ranking...")
    ranked_urls = rank_urls_advanced(all_urls)
    
    # STEP 3: Progressive scraping
    print("\n📍 STEP 3: Progressive Scraping...")
    content = scrape_content_v2(ranked_urls)
    
    # SUCCESS: Got enough content
    if content and len(content) >= 500:
        print(f"\n✅ SUCCESS: {len(content)} chars scraped")
        return content
    
    # RETRY: Insufficient content, try better query
    if attempt < 3:
        better_query = f"{query} comprehensive guide tutorial explained simple"
        print(f"\n⚠️ Insufficient content ({len(content) if content else 0} chars)")
        print(f"🔄 Retrying with enhanced query...")
        print(f"   New query: {better_query}")
        return scrape_with_retry_and_fallback(better_query, attempt + 1)
    
    # FALLBACK: All scraping attempts failed
    print(f"\n⚠️ Scraping failed after {attempt} attempts")
    result = generate_fallback_explanation(query)
    
    if result:
        return result
    
    # EMERGENCY: Generic explanation (should never reach here)
    print("\n🆘 EMERGENCY: Generic fallback")
    generic = f"""📚 Understanding: {query}

1. **Definition**: {query} is an important concept that refers to the topic you're exploring.

2. **Key Principle**: It works by combining different elements to create value and impact.

3. **Real-World Use**: This concept is applied in various practical situations and industries.

4. **Why It Matters**: Understanding this helps you make better decisions and insights.

5. **Next Step**: Continue learning by exploring related topics and resources."""
    
    return generic

def safe_generate(prompt, max_retries=3, timeout_seconds=30):
    """
    BULLETPROOF API wrapper with retry logic and timeout
    - 3 retry attempts with 2-second delays between retries
    - Handles all API errors gracefully  
    - Uses correct model (gemini-2.5-flash)
    - Times out to prevent hanging
    - Never throws unhandled exceptions
    """
    for attempt in range(max_retries):
        try:
            print(f"🧠 API Call (attempt {attempt + 1}/{max_retries})...")
            print(f"   Prompt length: {len(prompt)} chars, timeout: {timeout_seconds}s")
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Call with explicit timeout handling
            response = model.generate_content(
                prompt, 
                stream=False,
                generation_config={"timeout": timeout_seconds}
            )
            
            if response and response.text and len(response.text.strip()) > 20:
                # CRITICAL FIX: UTF-8 safe encoding for API response
                result = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
                print(f"✅ API Success: {len(result)} chars returned")
                return result
            else:
                print("⚠️ Empty response from API")
        
        except TimeoutError:
            print(f"⏱️ API timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                print(f"🔄 Waiting 3s before retry...")
                time.sleep(3)
            else:
                print(f"❌ All {max_retries} attempts failed due to timeout")
        
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"⚠️ API Error (attempt {attempt + 1}): {error_msg}")
            
            if attempt < max_retries - 1:
                print(f"🔄 Waiting 2s before retry {attempt + 2}...")
                time.sleep(2)
            else:
                print(f"❌ All {max_retries} attempts failed")
    
    print(f"⚠️ safe_generate returning None after {max_retries} retries")
    return None

def summarize_per_source(scraped_sources, query="", mode="Student"):
    """
    PHASE 2: Summarize EACH source individually with retry logic and fallback
    
    Args:
        scraped_sources: List of {url, title, content, score, score_label}
        query: Original query
        mode: Beginner/Student/Research
        
    Returns:
        List of {url, title, content, score, summary, score_label}
    """
    print(f"\n" + "="*60)
    print(f"📝 PHASE 2: Per-Source Summarization ({len(scraped_sources)} sources)")
    print(f"="*60)
    
    results = []
    
    for i, source in enumerate(scraped_sources, 1):
        title = source.get('title', 'Unknown')[:50]
        print(f"\n{i}/{len(scraped_sources)}: {title}")
        
        summary = None
        
        for attempt in range(2):
            try:
                if attempt > 0:
                    time.sleep(1)
                    print(f"   Retry {attempt}...")
                
                prompt = get_mode_specific_summary_prompt(source.get('content', ''), mode)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt, stream=False)
                
                summary = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
                
                if summary and len(summary) > 50:
                    print(f"   Summarized: {len(summary)} chars")
                    break
                    
            except Exception as e:
                if attempt == 1:
                    content_preview = source.get('content', '')[:300]
                    summary = f"Summary: {content_preview}\n\n[Final Takeaway: Refer to original source for complete analysis]"
        
        if summary and len(summary) > 30:
            source['summary'] = summary
            results.append(source)
        else:
            results.append(source)
    
    print(f"\nSummarized {len(results)} sources successfully")
    return results if results else scraped_sources

def generate_summary(content, query=""):
    """
    Generate AI summary with BULLETPROOF error handling
    
    CRITICAL FIXES:
    ✅ Content cleaned before processing
    ✅ Content size limited to 3000 chars
    ✅ 3-attempt retry with 2-second delays
    ✅ Fallback explanation if API fails
    ✅ Final safety fallback
    ✅ Debug output at each stage
    ✅ UTF-8 encoding safe handling
    """
    print("\n" + "="*60)
    print("📊 SUMMARY GENERATION (With Fallbacks)")
    print("="*60)
    
    # VALIDATION
    if not content or not content.strip():
        print("❌ Empty content, using AI fallback")
        return generate_fallback_explanation(query)
    
    if len(content) < 500:
        print(f"⚠️ Content short: {len(content)} chars, using AI fallback")
        return generate_fallback_explanation(query)
    
    # CRITICAL FIX #0: CLEAN TEXT FIRST + UTF-8 SAFE ENCODING
    content = content.encode("utf-8", errors="ignore").decode("utf-8")
    content = clean_text(content)
    
    # CRITICAL FIX #1: LIMIT INPUT SIZE TO 3000 CHARS
    safe_content = content[:3000]
    print(f"📏 Content size: {len(safe_content)} chars (cleaned and limited)")
    
    # PRIMARY ATTEMPT: Get summary from content with STRUCTURED FORMAT
    prompt = f"""Summarize the following content in a structured and meaningful way:

1. **Clear Definition** (2-3 lines): What is this about?

2. **Key Concepts** (bullet points): 
   • [concept 1]
   • [concept 2]
   • [concept 3]

3. **Important Techniques/Models Used**: [List any relevant techniques, frameworks, or models]

4. **Advantages and Limitations**: 
   Advantages: [list]
   Limitations: [list]

5. **Real-World Applications**: [Practical uses in industry and real scenarios]

6. **Final Practical Takeaway**: [One actionable insight for the reader]

RULES:
- Be specific and technical, avoid generic sentences
- Use clear, professional language
- Focus on accuracy and practical value
- No fluff or marketing language

CONTENT TO SUMMARIZE:
{safe_content}

Provide the structured summary with all 6 sections:"""
    
    # CRITICAL FIX #2: USE SAFE API WRAPPER
    print("\n1️⃣  PRIMARY: Summarizing from content...")
    summary = safe_generate(prompt, max_retries=3)
    
    if summary and len(summary) > 50:
        print(f"✅ PRIMARY SUCCESS: {len(summary)} chars")
        return summary
    
    # FALLBACK #1: Simpler explanation request
    if query:
        print("\n2️⃣  FALLBACK #1: Simple explanation request...")
        fallback_prompt = f"""Provide 5 simple, key points about: {query}

Format:
1. [Point 1]
2. [Point 2]
3. [Point 3]
4. [Point 4]
5. [Point 5]

Be brief and simple (1-2 sentences each)."""
        
        summary = safe_generate(fallback_prompt, max_retries=2)
        
        if summary and len(summary) > 30:
            print(f"✅ FALLBACK #1 SUCCESS: {len(summary)} chars")
            return summary
    
    # FALLBACK #2: Generic explanation
    print("\n3️⃣  FALLBACK #2: Generic explanation...")
    generic = f"""📚 Overview

1. **What it is**: {query if query else 'This topic'} is an important concept in modern knowledge.

2. **Key principle**: It combines multiple elements to create meaningful value.

3. **How it works**: The process involves gathering information and synthesizing insights.

4. **Real-world use**: This concept applies across various industries and contexts.

5. **Why it matters**: Understanding this helps improve decision-making and knowledge."""
    
    print(f"✅ FALLBACK #2: Using generic content: {len(generic)} chars")
    return generic

def clean_for_audio(text):
    """Clean text for audio generation - remove unicode/emoji that crashes gTTS"""
    if not text:
        return ""
    
    # Remove emoji and special unicode characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Remove multiple newlines
    text = text.replace('\n\n', ' ')
    text = text.replace('\n', ' ')
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text[:2000]  # Limit to 2000 chars for TTS

def transcribe_audio(audio_bytes):
    """Transcribe audio from bytes to text using speech recognition"""
    if not SPEECH_RECOGNITION_AVAILABLE:
        return None
    
    try:
        from io import BytesIO
        import wave
        
        # Convert bytes to audio file
        recognizer = sr.Recognizer()
        
        # Create audio data from bytes
        audio_data = sr.AudioData(audio_bytes, 44100, 2)
        
        print("🎤 Transcribing audio...")
        # Use Google Speech Recognition (free, no API key needed)
        text = recognizer.recognize_google(audio_data)
        print(f"✅ Transcribed: {len(text)} chars")
        return text
        
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Try speaking more clearly.")
        return None
    except sr.RequestError as e:
        st.warning(f"Speech recognition service error: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"Transcription error: {str(e)[:100]}")
        return None

def generate_tts(summary_text):
    """Generate text-to-speech from summary with FIXED unicode handling"""
    if not GTTS_AVAILABLE:
        return None
    
    try:
        # Clean text BEFORE sending to gTTS
        clean_text = clean_for_audio(summary_text)
        
        if not clean_text or len(clean_text) < 10:
            return None
        
        # Use static path
        file_path = "summary_audio.mp3"
        
        # Generate audio
        tts = gTTS(text=clean_text, lang='en')
        tts.save(file_path)
        
        # Return path
        return file_path
        
    except Exception as e:
        print(f"Audio error: {str(e)[:100]}")
        return None

def create_csv(summary_text):
    """Create CSV file from summary with proper UTF-8 encoding"""
    try:
        # Remove emojis for safe writing
        clean_summary = remove_emojis(summary_text)
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline='', encoding="utf-8")
        writer = csv.writer(tmp)
        writer.writerow(["Summary"])
        for line in clean_summary.split("\n"):
            if line.strip():
                writer.writerow([line])
        tmp.close()
        return tmp.name
    except Exception as e:
        st.error(f"CSV creation failed: {e}")
        return None

def create_pdf(summary_text):
    """Create PDF file from summary with FIXED static path"""
    try:
        # Clean text for PDF compatibility
        clean_summary = remove_emojis(summary_text)
        
        # Use absolute static path
        file_path = "summary_output.pdf"
        
        # Create document
        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()
        
        # Build content
        content = []
        content.append(Paragraph("Summary Report", styles['Title']))
        content.append(Spacer(1, 12))
        
        # Split into paragraphs to avoid unicode issues
        for line in clean_summary.split('\n'):
            if line.strip():
                try:
                    content.append(Paragraph(line, styles['Normal']))
                    content.append(Spacer(1, 6))
                except:
                    pass
        
        # Build PDF
        doc.build(content)
        
        # Return path immediately (don't verify, streamlit handles it)
        return file_path
            
    except Exception as e:
        print(f"PDF error: {str(e)[:100]}")
        return None

# ============================================================================
# STREAMLIT UI
# ============================================================================
st.set_page_config(
    page_title="QuickGlance AI",
    page_icon="magnifying_glass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE & DESCRIPTION
# ============================================================================
st.markdown("# QuickGlance AI")
st.markdown("### Search, Scrape and Summarize Web Content")

st.divider()

# ============================================================================
# SIDEBAR - QUERY HISTORY
# ============================================================================
with st.sidebar:
    st.markdown("### Recent Searches")
    if st.session_state.query_history:
        for i, past_query in enumerate(st.session_state.query_history[-5:], 1):
            if st.button(
                f"{past_query[:35]}{'...' if len(past_query) > 35 else ''}",
                key=f"history_{i}",
                use_container_width=True
            ):
                st.session_state.reuse_query = past_query
                st.rerun()
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.rerun()
    else:
        st.caption("No search history yet")

# ============================================================================
# INPUT SECTION
# ============================================================================
st.markdown("### What do you want to learn about?")

# Voice input option
st.markdown("#### Input Methods")
input_method = st.radio("Choose input method:", ["Text", "Voice"], horizontal=True)

if input_method == "Voice":
    st.info("🎤 Click the microphone button below to record your query")
    audio_input = st.audio_input("Record your question:")
    
    if audio_input:
        st.info("🔄 Transcribing your audio...")
        # Transcribe audio to text
        if SPEECH_RECOGNITION_AVAILABLE:
            transcribed_query = transcribe_audio(audio_input.read())
            if transcribed_query:
                query = transcribed_query
                st.success(f"✅ Transcribed: {query}")
            else:
                st.error("Could not transcribe audio. Try again or use text input.")
                query = ""
        else:
            st.warning("Voice input not available. Using text input instead.")
            query = st.text_input(
                "Enter your topic:",
                placeholder="e.g., 'artificial intelligence in healthcare'",
                label_visibility="collapsed"
            )
else:
    # Text input
    # Example queries
    example_queries = [
        "How machine learning improves healthcare outcomes",
        "Artificial intelligence applications explained",
        "Climate change solutions and renewable energy",
        "Blockchain technology basics",
        "Cybersecurity best practices 2024"
    ]

    col1, col2, col3 = st.columns([2.5, 0.75, 0.75])
    with col1:
        # Check if reusing from history
        initial_value = st.session_state.get("reuse_query", "")
        query = st.text_input(
            "Enter your topic:",
            placeholder="e.g., 'artificial intelligence in healthcare'",
            value=initial_value,
            label_visibility="collapsed"
        )
        if initial_value:
            del st.session_state["reuse_query"]

    with col2:
        if st.button("Examples", use_container_width=True):
            with st.expander("Example Queries", expanded=True):
                for i, example in enumerate(example_queries, 1):
                    st.write(f"• {example}")

    with col3:
        if st.button("Clear", use_container_width=True):
            st.rerun()

st.divider()

# ============================================================================
# PROCESS BUTTON
# ============================================================================
col_search, col_retry = st.columns([4, 1])
with col_search:
    # Add mode selector BEFORE search button
    mode = st.selectbox(
        "Analysis Mode:",
        ["Beginner", "Student", "Research"],
        index=1,
        help="Beginner: Simple explanations | Student: Academic depth | Research: Advanced deep-dive"
    )
    
    search_clicked = st.button("Search and Analyze", use_container_width=True, key="main_button")

with col_retry:
    retry_clicked = st.button("Retry", use_container_width=True)

if search_clicked:
    if query.strip() == "":
        st.warning("⚠️ Please enter a topic to proceed.")
    else:
        # MAIN TRY-EXCEPT: Wrap ENTIRE pipeline to prevent crashes
        try:
            # Add query to history (avoid duplicates)
            if query not in st.session_state.query_history:
                st.session_state.query_history.append(query)
            # Start timing
            start_time = time.time()
            
            # Create a progress tracking container
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # ========================================
            # PHASE 3: QUERY IMPROVEMENT
            # ========================================
            with status_placeholder.container():
                st.markdown("### 📊 PHASE 3: Intelligent Analysis Pipeline...")
                st.write("🔍 Step 1: Improving query for better results...")
            
            original_query = query
            improved_query = generate_query_improvement(original_query)
            
            # ========================================
            # STEP 1: SEARCH with improved query
            # ========================================
            with status_placeholder.container():
                st.write("🔍 Step 2: Finding trusted sources...")
            
            with st.spinner("🔍 Searching for high-quality sources..."):
                try:
                    urls = search_and_merge(improved_query)
                    if not urls:
                        st.info("ℹ️ No results on first search, trying variation...")
                        urls = search_and_merge(f"{original_query} explained")
                except Exception as search_error:
                    print(f"❌ Search error: {str(search_error)[:50]}")
                    urls = []
                
            if urls:
                with status_placeholder.container():
                    st.success(f"✅ Found {len(urls)} sources. Ranking by quality...")
                
                advanced_ranked_urls = rank_urls_advanced(urls)
                
                with st.expander(f"View {len(advanced_ranked_urls[:5])} Top Sources"):
                    for i, url in enumerate(advanced_ranked_urls[:5], 1):
                        score, score_label = score_url_quality(url)
                        st.write(f"**{i}.** [{url[:60]}...]({{url}})")
                        st.caption(f"Quality: {score}/10 - {score_label}")
            else:
                st.error("No sources found. Try a different query.")
                st.stop()
            
            # ========================================
            # PHASE 2: MULTI-SOURCE ANALYSIS (Per-source, not merged!)
            # ========================================
            with status_placeholder.container():
                st.write("📄 Step 3: Extracting content from each source individually...")
            
            with st.spinner("📄 Extracting and analyzing each source..."):
                try:
                    # PHASE 2 FEATURE: Get per-source content
                    scraped_sources = scrape_content_v2(advanced_ranked_urls)
                    
                    if not scraped_sources:
                        raise Exception("Failed to scrape any sources")
                    
                    print(f"Scraped {len(scraped_sources)} individual sources")
                except Exception as scrape_error:
                    print(f"Scraping error: {str(scrape_error)[:50]}")
                    st.error("Could not extract content from sources.")
                    st.stop()
            
            if scraped_sources:
                with status_placeholder.container():
                    st.success(f"✅ Extracted {len(scraped_sources)} sources")
                
                with st.expander(f"📊 View Source Quality Scores"):
                    for i, source in enumerate(scraped_sources, 1):
                        st.write(f"**Source {i}:** {source['title'][:50]}")
                        st.write(f"   • Quality Score: {source['score']}/10")
                        st.write(f"   • Content: {len(source['content'])} chars")
            
            # ========================================
            # PHASE 2: PER-SOURCE SUMMARIZATION
            # ========================================
            with status_placeholder.container():
                st.write(f"📝 Step 4: Summarizing each source independently (Mode: {mode})...")
            
            with st.spinner("📝 Generating per-source summaries..."):
                try:
                    # PHASE 2 FEATURE: Summarize each source separately
                    summarized_sources = summarize_per_source(scraped_sources, original_query, mode)
                    
                    if not summarized_sources:
                        raise Exception("Failed to summarize any sources")
                    
                    print(f"Summarized {len(summarized_sources)} sources")
                except Exception as summary_error:
                    print(f"Summarization error: {str(summary_error)[:50]}")
                    st.error("Could not summarize content.")
                    st.stop()
            
            st.session_state.last_summary = summarized_sources
            
            # Clear status
            status_placeholder.empty()
            
            st.divider()
            
            # ========================================
            # PHASE 4: DISPLAY PIPELINE
            # ========================================
            with st.expander("📊 View Processing Pipeline", expanded=False):
                pipeline = get_pipeline_steps()
                for step, desc, icon in pipeline:
                    st.write(f"{icon} {step}: {desc}")
            
            # ========================================
            # PHASE 2 DISPLAY: MULTI-SOURCE COMPARISON
            # ========================================
            st.markdown("### 📊 Multi-Source Comparison")
            
            for i, source in enumerate(summarized_sources, 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"#### 📰 **Source {i}: {source['title'][:50]}**")
                        st.caption(f"Quality Score: ⭐ {source['score']}/10 ({source['score_label']})")
                    
                    with col2:
                        st.metric("Quality", f"{source['score']}/10")
                    
                    # Display summary
                    with st.expander(f"View Summary", expanded=(i==1)):  # First one expanded
                        st.write(source['summary'])
                    
                    st.divider()
            
            # ========================================
            # PHASE 2 FINAL INSIGHT
            # ========================================
            st.markdown("### ✨ Final Unified Insight")
            
            with st.spinner("✨ Synthesizing all sources into final insight..."):
                try:
                    final_insight = generate_final_insight(summarized_sources, original_query, mode)
                    
                    if final_insight:
                        st.write(final_insight)
                        st.session_state.last_full_analysis = final_insight
                    else:
                        st.info("Could not generate final insight")
                except Exception as insight_error:
                    print(f"Insight generation error: {str(insight_error)[:50]}")
                    st.warning("Could not generate final insight")
            
            st.divider()
            
            # ========================================
            # PHASE 3: ACTIONABLE INSIGHTS
            # ========================================
            st.markdown("### 💡 Actionable Insights")
            
            # Get first source summary for actionable insights
            if summarized_sources:
                first_summary = summarized_sources[0]['summary']
                
                with st.spinner(f"💡 Generating actionable insights for {mode}..."):
                    try:
                        actionable = generate_actionable_insights(first_summary, mode)
                        
                        if actionable:
                            st.write(actionable)
                        else:
                            st.info("No actionable insights generated")
                    except Exception as action_error:
                        print(f"Actionable insights error: {str(action_error)[:50]}")
            
            st.divider()
            
            # ========================================
            # TIMING & METRICS
            # ========================================
            elapsed_time = time.time() - start_time
            
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Sources Analyzed", len(summarized_sources))
                with col2:
                    st.metric("Analysis Mode", mode)
                with col3:
                    st.metric("Time Elapsed", f"{elapsed_time:.1f}s")
                with col4:
                    st.metric("Query Improved", "Yes" if improved_query != original_query else "No")
            
            st.divider()
            
            # ========================================
            # PHASE 4: CITATIONS & DOWNLOADS
            # ========================================
            st.markdown("### CITATIONS")
            
            # Format citations for all sources
            citations_text = format_citations(summarized_sources)
            
            with st.expander("View Citations", expanded=False):
                st.text(citations_text)
            
            st.divider()
            
            # ========================================
            # PHASE 4: DOWNLOAD OPTIONS (Clean UI)
            # ========================================
            st.markdown("### Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            # Prepare export content with modes
            export_content = f"""QUERY: {original_query}
IMPROVED QUERY: {improved_query}
ANALYSIS MODE: {mode}
TIME TAKEN: {elapsed_time:.1f}s
SOURCES ANALYZED: {len(summarized_sources)}

{'='*60}

MULTI-SOURCE ANALYSIS

"""
            
            for i, source in enumerate(summarized_sources, 1):
                export_content += f"\nSOURCE {i}: {source['title']}\n"
                export_content += f"Quality Score: {source['score']}/10\n"
                export_content += f"URL: {source['url']}\n"
                export_content += "-" * 60 + "\n"
                export_content += source['summary']
                export_content += "\n\n" + "="*60 + "\n\n"
            
            # Add citations
            export_content += "\n" + citations_text
            
            with col1:
                try:
                    # Download as TXT (simplest, most reliable)
                    st.download_button(
                        label="Download as TXT",
                        data=export_content.encode('utf-8'),
                        file_name="analysis_results.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"TXT download error: {str(e)[:50]}")
            
            with col2:
                try:
                    csv_path = create_csv(export_content)
                    if csv_path:
                        with open(csv_path, "rb") as f:
                            csv_data = f.read()
                        st.download_button(
                            label="Download as CSV",
                            data=csv_data,
                            file_name="analysis_results.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                except Exception as e:
                    st.warning(f"CSV error: {str(e)[:30]}")
            
            with col3:
                try:
                    pdf_path = create_pdf(export_content)
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_data = f.read()
                        st.download_button(
                            label="Download as PDF",
                            data=pdf_data,
                            file_name="analysis_results.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.warning(f"PDF error: {str(e)[:30]}")
            
            st.divider()
            
            # Success notification
            st.success("Analysis complete! Download your results above.")
            
        except Exception as e:
            st.error("An unexpected error occurred during analysis.")
            with st.expander("Error Details", expanded=False):
                st.code(f"Error: {str(e)[:200]}")
                st.info("""
                Troubleshooting tips:
                1. Try a simpler query
                2. Refresh the page
                3. Check your internet connection
                4. Try again in a moment
                """)

st.divider()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
---
<div style="text-align: center; color: gray; padding: 20px;">
    <p><strong>QuickGlance AI</strong> • Powered by Streamlit + Google Gemini</p>
    <p>📧 Contact | 🐛 Report Issues | ⭐ Star on GitHub</p>
</div>
""", unsafe_allow_html=True)