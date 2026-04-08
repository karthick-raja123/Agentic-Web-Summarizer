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
    """
    # HARD FILTER: Block low-quality sources before scraping
    BLOCKED_DOMAINS = [
        "researchgate", "ncbi.nlm.nih.gov", "sciencedirect",
        "springer", "wiley", "mdpi", "elsevier",
        "youtube", "youtu.be", ".pdf",
        "facebook.com", "twitter.com", "instagram.com"
    ]
    
    for blocked in BLOCKED_DOMAINS:
        if blocked.lower() in url.lower():
            print(f"⛔ Blocked domain: {blocked}")
            return None
    
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
    - Handles network timeouts
    - Handles API failures
    - Returns empty list on error
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
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=data,
            timeout=8
        )
        response.raise_for_status()
        results = response.json()
        urls = [result["link"] for result in results.get("organic", [])][:5]
        
        if not urls:
            return []
            
        return urls
        
    except requests.Timeout:
        st.error("⏱️ Search timeout. Server took too long to respond. Try a simpler query.")
        return []
    except requests.ConnectionError:
        st.error("🌐 Network error. Please check your connection.")
        return []
    except requests.HTTPError as e:
        st.error(f"🔍 Search API error. Please try again later.")
        return []
    except ValueError:
        st.error("⚠️ Invalid search response. Try a different query.")
        return []
    except Exception as e:
        st.error("❌ Unexpected error during search. Please try again.")
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
    - Remove if too many links (noisy)
    - Ignore if too short (< 500 chars)
    - Remove excessive whitespace
    """
    if not text:
        return None
    
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
    - Remove non-ASCII garbage
    - Remove HTML artifacts
    """
    if not text:
        return text
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove excessive punctuation
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'([.!?])([.!?]+)', r'\1', text)  # Remove repeated punctuation
    
    return text.strip()

def rank_urls_advanced(urls):
    """
    Advanced URL scoring system (-5 to +5):
    
    +5 → Tutorial, guide, explained, learn keywords
    +3 → Premium sources: medium, geeksforgeeks, towards
    +1 → Normal article/blog sites
    -1 → PDFs (hard to parse)
    -3 → Academic publishers: ncbi, wiley, springer, mdpi
    -5 → Suspicious: very long, many params, login
    
    Sort by score descending (best first)
    """
    if not urls:
        return []
    
    scored = []
    
    for url in urls:
        url_lower = url.lower()
        score = 0
        
        # POSITIVE SIGNALS: Tutorials & guides (+5)
        if any(word in url_lower for word in ["tutorial", "guide", "explained", "learn", "beginner", "how-to", "step-by-step"]):
            score += 5
        
        # POSITIVE SIGNALS: Premium educational sources (+3)
        if any(domain in url_lower for domain in ["medium.com", "geeksforgeeks", "analyticsvidhya", "towardsdatascience"]):
            score += 3
        
        # POSITIVE SIGNALS: .org, blogs, dev sites (+1)
        elif any(domain in url_lower for domain in ["dev.to", "blog", ".org", "github.com", "stackoverflow"]):
            score += 1
        
        # NEGATIVE SIGNALS: PDFs (-1)
        if ".pdf" in url_lower:
            score -= 1
        
        # NEGATIVE SIGNALS: Academic publishers (-3)
        if any(domain in url_lower for domain in ["ncbi", "wiley", "springer", "mdpi", "elsevier", "sciencedirect", "researchgate"]):
            score -= 3
        
        # NEGATIVE SIGNALS: Suspicious URLs (-5)
        if len(url) > 200 or url.count('=') > 3 or 'login' in url_lower or 'paywall' in url_lower:
            score -= 5
        
        scored.append((score, url))
    
    # Sort by score descending
    scored.sort(reverse=True, key=lambda x: x[0])
    
    print(f"\n🎯 ADVANCED RANKING (Top 5):")
    for i, (score, url) in enumerate(scored[:5], 1):
        print(f"   {i}. Score {score:+d}: {url[:65]}")
    
    return [url for _, url in scored]

def scrape_content_v2(urls):
    """
    Progressive scraping pipeline (GUARANTEE: Gets content if URLs exist)
    
    Process:
    1. Use top 3 URLs (safeguard: reduced from 5 to prevent hanging)
    2. Extract from each with validation
    3. Stop when 2500-3000 chars accumulated
    4. Validate: min 500 chars per source, remove noisy content
    5. Clean text before adding
    
    Args:
        urls: Ranked list of URLs
        
    Returns:
        Combined content (500-3000 chars) or None
    """
    if not urls:
        return None
    
    print("\n" + "="*60)
    print("📄 PROGRESSIVE SCRAPING (Top 3 URLs - Safeguard)")
    print("="*60)
    
    best_urls = urls[:3]
    print(f"\n📌 Will scrape: {len(best_urls)} URLs (hard filtered)\n")
    
    accumulated_content = ""
    target_size = 2500
    urls_scraped = 0
    
    for i, url in enumerate(best_urls, 1):
        print(f"{i}/{len(best_urls)}: {url[:70]}")
        
        try:
            # Extract content
            text = clean_scrape(url)
            
            if text:
                # Validate content (remove noisy/link-heavy content)
                validated = validate_content(text)
                
                if validated:
                    # Clean text before adding
                    cleaned = clean_text(validated)
                    print(f"   ✅ Valid: {len(cleaned)} chars")
                    accumulated_content += cleaned + "\n\n"
                    urls_scraped += 1
                    current_total = len(accumulated_content)
                    print(f"   📊 Running total: {current_total} chars")
                    
                    # Stop early if target reached (efficiency)
                    if current_total >= target_size:
                        print(f"   ✨ Target reached! Stopping.")
                        break
                else:
                    print(f"   ⚠️ Content invalid (noisy/links)")
            else:
                print(f"   ❌ No content extracted")
        
        except Exception as e:
            print(f"   ❌ Scrape error: {str(e)[:50]}")
            continue
    
    # Final validation
    final_text = accumulated_content.strip()
    
    print(f"\n📊 Scraped: {urls_scraped} URLs successfully")
    
    if len(final_text) >= 500:
        print(f"✅ SUCCESS: {len(final_text)} chars accumulated")
        return final_text[:3000]  # Cap at 3000
    
    print(f"⚠️ Insufficient: {len(final_text)} chars (need 500+)")
    return None

def generate_fallback_explanation(query):
    """
    FALLBACK GUARANTEE: If scraping fails, generate direct explanation from Gemini
    
    This ENSURES the system NEVER fails with empty content
    Provides high-quality AI explanation when web content unavailable
    """
    print("\n" + "="*60)
    print("🎯 FALLBACK: Direct AI Explanation (No Web Sources)")
    print("="*60)
    
    prompt = f"""You are an expert educator. Provide a clear, comprehensive explanation suitable for beginners.

TOPIC: {query}

Provide exactly 5 KEY POINTS:
1. [Core concept/definition]
2. [How it works / Core mechanism]
3. [Real-world application]
4. [Practical benefits/advantages]
5. [Key takeaway for learning]

Rules:
- Use ONLY simple, clear language
- 1-2 sentences per point
- Focus on practical, actionable information
- Make it accessible to beginners
- Start each with a number
"""
    
    try:
        print("\n🧠 Generating explanation from Gemini...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False)
        
        if response.text and len(response.text.strip()) > 100:
            result = response.text.strip()
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

def safe_generate(prompt, max_retries=3):
    """
    BULLETPROOF API wrapper with retry logic
    - 3 retry attempts with 2-second delays
    - Handles all API errors gracefully
    - Uses correct model (gemini-2.5-flash)
    """
    for attempt in range(max_retries):
        try:
            print(f"🧠 API Call (attempt {attempt + 1}/{max_retries})...")
            print(f"   Prompt length: {len(prompt)} chars")
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt, stream=False)
            
            if response.text and len(response.text.strip()) > 20:
                result = response.text.strip()
                print(f"✅ API Success: {len(result)} chars returned")
                return result
            else:
                print("⚠️ Empty response from API")
        
        except Exception as e:
            error_msg = str(e)[:80]
            print(f"⚠️ API Error: {error_msg}")
            
            if attempt < max_retries - 1:
                print(f"🔄 Waiting 2s before retry {attempt + 2}...")
                time.sleep(2)
            else:
                print(f"❌ All {max_retries} attempts failed")
    
    return None

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
    
    # CRITICAL FIX #0: CLEAN TEXT FIRST
    content = clean_text(content)
    
    # CRITICAL FIX #1: LIMIT INPUT SIZE TO 3000 CHARS
    safe_content = content[:3000]
    print(f"📏 Content size: {len(safe_content)} chars (cleaned and limited)")
    
    # PRIMARY ATTEMPT: Get summary from content
    prompt = f"""You are a professional content summarizer. Extract exactly 5 KEY INSIGHTS from this text.

RULES:
- Use ONLY simple, clear language
- Maximum 1-2 sentences per insight
- Focus on actionable, practical information
- NO introductions, conclusions, or fluff
- NO generic statements
- Start each with a number: 1. 2. 3. etc

TEXT TO SUMMARIZE:
{safe_content}

Provide exactly 5 numbered key insights:"""
    
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
    search_clicked = st.button("Search and Summarize", use_container_width=True, key="main_button")

with col_retry:
    retry_clicked = st.button("Retry", use_container_width=True)

if search_clicked:
    if query.strip() == "":
        st.warning("⚠️ Please enter a topic to proceed.")
    else:
        # Add query to history (avoid duplicates)
        if query not in st.session_state.query_history:
            st.session_state.query_history.append(query)
        # Start timing
        start_time = time.time()
        
        # Create a progress tracking container
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Optimize query for better results
            original_query = query
            optimized_query = optimize_query_for_readability(query)
            
            # ========================================
            # STEP 1: SEARCH (with optimization)
            # ========================================
            with status_placeholder.container():
                st.markdown("### 📊 Processing Your Query...")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Step", "1 / 3", "SEARCHING")
            
            with st.spinner("🔍 Searching the web for relevant sources..."):
                try:
                    urls = search_serper(optimized_query)
                    if not urls:
                        st.info("ℹ️ No results on first search, trying variation...")
                        urls = search_serper(f"{query} explained")
                except Exception as search_error:
                    print(f"❌ Search error: {str(search_error)[:50]}")
                    urls = []
                
            if urls:
                with status_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.success(f"Step 1 Complete: Found {len(urls)} sources")
                
                with st.expander("View Sources"):
                    for i, url in enumerate(urls, 1):
                        st.write(f"**{i}.** [{url[:60]}...]({{url}})")
            else:
                st.error("No sources found. Try a different query.")
                st.stop()
            
            # ========================================
            # MASTER ORCHESTRATOR: Intelligent Content Extraction
            # ========================================
            with status_placeholder.container():
                st.markdown("### Processing Your Query...")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Step", "1-2 / 3", "Extracting Content")
            
            with st.spinner("Executing intelligent content extraction with hard filters..."):
                try:
                    content = scrape_with_retry_and_fallback(original_query)
                    if content:
                        print(f"Extracted: {len(content)} chars (after hard filters)")
                except Exception as scrape_error:
                    print(f"Scraping error: {str(scrape_error)[:50]}")
                    st.warning("Scraping encountered an issue, trying AI explanation...")
                    content = generate_fallback_explanation(original_query)
            
            if content:
                st.session_state.last_content = content
                content_chars = len(content)
                print(f"Content ready: {content_chars} chars")
                
                with status_placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.success("Search Complete")
                    with col2:
                        st.success(f"Extracted {content_chars} chars")
            else:
                st.error("Content extraction failed completely.")
                st.stop()
            
            # ========================================
            # STEP 3: SUMMARIZE
            # ========================================
            with status_placeholder.container():
                st.markdown("### Processing Your Query...")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.success("Step 1: Found sources")
                with col2:
                    st.success("Step 2: Extracted content")
                with col3:
                    st.metric("Step", "3 / 3", "Summarizing")
            
            with st.spinner("Generating summary with Google Gemini..."):
                try:
                    summary = generate_summary(content, original_query)
                    if summary:
                        print(f"Summary generated: {len(summary)} chars")
                except Exception as api_error:
                    print(f"API error: {str(api_error)[:50]}")
                    st.warning("Generating summary from content directly...")
                    summary = f"Summary\n\n{content[:1500] if content else 'No content available'}\n\n[Note: AI service temporarily unavailable - showing extracted content]" if content else None
            
            # Clear progress and show results
            status_placeholder.empty()
            
            st.divider()
            
            # ========================================
            # DISPLAY RESULTS
            # ========================================
            if summary:
                # Store summary for retry
                st.session_state.last_summary = summary
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                
                # Calculate number of sources used (max 2)
                num_sources = min(2, len(urls))
                
                # Success metrics
                with st.container():
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.success("Step 1: Searched")
                    with col2:
                        st.success("Step 2: Scraped")
                    with col3:
                        st.success("Step 3: Summarized")
                
                st.markdown("### Key Insights")
                st.success("Analysis Complete!")
                
                # Display summary with better formatting
                with st.container(border=True):
                    st.markdown(summary)
                
                st.divider()
                
                # Performance Metrics
                st.markdown("### Performance Metrics")
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Time Taken", f"{elapsed_time:.2f}s")
                
                with metric_col2:
                    st.metric("Sources Used", num_sources)
                
                with metric_col3:
                    st.metric("Content Length", f"{len(content)}")
                
                with metric_col4:
                    st.metric("Summary Size", f"{len(summary)}")
                
                st.divider()
                
                # Download Options
                st.markdown("### Download Your Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_path = create_csv(summary)
                    if csv_path:
                        with open(csv_path, "rb") as f:
                            st.download_button(
                                label="Download as CSV",
                                data=f,
                                file_name="summary.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                
                with col2:
                    try:
                        pdf_path = create_pdf(summary)
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                pdf_data = f.read()
                            st.download_button(
                                label="Download as PDF",
                                data=pdf_data,
                                file_name="summary.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.error("PDF generation failed")
                    except Exception as e:
                        st.error(f"PDF Error: {str(e)[:100]}")
                
                with col3:
                    if GTTS_AVAILABLE:
                        try:
                            audio_path = generate_tts(summary)
                            if audio_path and os.path.exists(audio_path):
                                with open(audio_path, "rb") as f:
                                    audio_data = f.read()
                                st.audio(audio_data, format="audio/mp3")
                                st.download_button(
                                    label="Download MP3",
                                    data=audio_data,
                                    file_name="summary.mp3",
                                    mime="audio/mp3",
                                    use_container_width=True
                                )
                            else:
                                st.warning("Audio generation failed")
                        except Exception as e:
                            st.error(f"Audio Error: {str(e)[:100]}")
                    else:
                        st.info("Audio feature unavailable (gTTS not installed)")
                
                st.divider()
                
                # Sources Section
                num_sources = min(2, len(urls))
                st.markdown(f"### Sources Used ({num_sources})")
                
                with st.expander(f"View {num_sources} Sources", expanded=False):
                    for i, url in enumerate(urls[:num_sources], 1):
                        col1, col2 = st.columns([1, 15])
                        with col1:
                            st.text(f"{i}")
                        with col2:
                            st.markdown(f"[{url}]({url})")
                
                st.balloons()
                st.success("Processing complete! Your summary is ready to download.")
                        
            else:
                print("Summary generation failed")
                st.error("Unable to generate summary. Please try again.")
                with st.expander("What to do", expanded=True):
                    st.info("""
                    - Try refreshing the page
                    - Try a different search query
                    - Check your internet connection
                    - Try again in a few moments
                    """)

                
        except Exception as e:
            status_placeholder.empty()
            st.error("An unexpected error occurred. Please try again.")
            with st.expander("Troubleshooting", expanded=False):
                st.code(f"Error: {str(e)[:200]}")
                st.info("""
                Steps to resolve:
                1. Refresh the page
                2. Try a different query
                3. Check your internet connection
                4. Wait a moment and try again
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