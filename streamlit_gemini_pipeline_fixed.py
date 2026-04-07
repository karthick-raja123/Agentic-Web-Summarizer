"""
Streamlit UI - Multi-Agent Research Aggregation
Production-ready with error handling, logging, and proper .env support
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64
import csv
import tempfile
import time
import traceback
from typing import List, Optional, Tuple
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from langchain_google_genai import ChatGoogleGenerativeAI
from services.model_handler import ModelHandler

# ============================================================================
# MODEL HANDLER FOR FALLBACK SUPPORT
# ============================================================================

model_handler = None
try:
    model_handler = ModelHandler(Config.GOOGLE_API_KEY)
except Exception as e:
    print(f"Warning: Could not initialize model handler: {e}")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="QuickGlance - Research Aggregator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS STYLING
# ============================================================================

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    .error-box { background-color: #ffcccc; padding: 1rem; border-radius: 5px; }
    .success-box { background-color: #ccffcc; padding: 1rem; border-radius: 5px; }
    .info-box { background-color: #ccccff; padding: 1rem; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

# Get debug mode flag
debug_mode = st.session_state.get("debug_mode", False)

# ============================================================================
# CONFIGURATION VALIDATION (SIDEBAR)
# ============================================================================

with st.sidebar:
    st.header("⚙️ Settings & Status")
    
    # Show config status
    is_valid, errors = Config.validate()
    
    if is_valid:
        st.success("✅ Configuration Valid")
        with st.expander("📋 View Configuration"):
            st.code(f"""API Keys: Configured
Timeouts:
  - Serper: {Config.SERPER_TIMEOUT}s
  - Scrape: {Config.SCRAPE_TIMEOUT}s
  - General: {Config.REQUEST_TIMEOUT}s

Content Limits:
  - Per URL: {Config.MAX_CONTENT_PER_URL} chars
  - Total: {Config.MAX_TOTAL_CONTENT} chars
  - Max Results: {Config.MAX_SEARCH_RESULTS}
  - Max URLs: {Config.MAX_URLS_TO_SCRAPE}

Features:
  - Evaluation: {Config.ENABLE_EVALUATION}
  - Formatting: {Config.ENABLE_FORMATTING}
""", language="plaintext")
    else:
        st.error("❌ Configuration Error")
        for error in errors:
            st.error(error)
        st.info("""
        **Setup Required:**
        1. Copy `.env.clean` to `.env`
        2. Add your API keys:
           - Google: https://makersuite.google.com/app/apikey
           - Serper: https://serper.dev/api
        3. Restart the app
        """)
        st.stop()
    
    # Debug toggle
    st.divider()
    st.session_state.debug_mode = st.checkbox("🐛 Debug Mode", value=st.session_state.get("debug_mode", False))
    debug_mode = st.session_state.debug_mode
    
    # Query history
    if st.session_state.query_history:
        st.divider()
        st.subheader("📚 Query History")
        for i, q in enumerate(st.session_state.query_history[-5:], 1):
            if st.button(f"{i}. {q[:30]}...", key=f"history_{i}"):
                st.session_state.selected_query = q

# ============================================================================
# INITIALIZE LLM
# ============================================================================

@st.cache_resource
def get_llm():
    """Initialize LLM with fallback support"""
    try:
        if not model_handler:
            st.error("❌ Model handler not initialized")
            return None
        
        # Get model with fallback
        model_obj, model_name = model_handler.get_model("gemini-1.5-pro")
        
        # Initialize ChatGoogleGenerativeAI with working model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=Config.GOOGLE_API_KEY
        )
        
        st.session_state.llm_model_name = model_name
        return llm
        
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "NOT_FOUND" in error_msg:
            st.warning(f"⚠️ Model temporarily unavailable ({error_msg}), retrying with fallback...")
        else:
            st.error(f"Failed to initialize Gemini: {error_msg}")
        return None

# ============================================================================
# SEARCH FUNCTION
# ============================================================================

def search_serper(query: str, debug: bool = False) -> Tuple[List[str], str]:
    """Search using Serper API with error handling"""
    try:
        headers = {
            "X-API-KEY": Config.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        data = {"q": query, "num": Config.MAX_SEARCH_RESULTS}
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=data,
            timeout=Config.SERPER_TIMEOUT
        )
        response.raise_for_status()
        
        results = response.json()
        urls = [
            result["link"]
            for result in results.get("organic", [])
            if "link" in result
        ][:Config.MAX_URLS_TO_SCRAPE]
        
        if debug:
            st.write(f"🐛 Serper returned {len(urls)} URLs")
        
        return urls, None
        
    except requests.Timeout:
        return [], f"Serper API timeout (>{Config.SERPER_TIMEOUT}s)"
    except requests.RequestException as e:
        return [], f"Serper API error: {str(e)}"
    except Exception as e:
        return [], f"Search error: {str(e)}"

# ============================================================================
# SCRAPING FUNCTION
# ============================================================================

def scrape_content(urls: List[str], debug: bool = False) -> Tuple[str, int, List[str]]:
    """Scrape content from URLs with error handling"""
    if not urls:
        return "", 0, ["No URLs to scrape"]
    
    combined_content = ""
    urls_success = 0
    errors = []
    
    for url in urls:
        try:
            response = requests.get(
                url,
                timeout=Config.SCRAPE_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            
            if text:
                text_limited = text[:Config.MAX_CONTENT_PER_URL]
                combined_content += text_limited + "\n"
                urls_success += 1
                
                if debug:
                    st.write(f"🐛 Scraped {url[:50]}... ({len(text_limited)} chars)")
            
        except requests.Timeout:
            errors.append(f"Timeout: {url[:40]}...")
        except Exception as e:
            errors.append(f"Error: {url[:30]}... ({str(e)[:30]})")
    
    # Limit total content
    combined_content = combined_content[:Config.MAX_TOTAL_CONTENT]
    
    return combined_content, urls_success, errors

# ============================================================================
# SUMMARIZATION FUNCTION
# ============================================================================

def summarize_with_gemini(content: str, llm, debug: bool = False) -> Tuple[str, Optional[str]]:
    """Generate summary with Gemini - with fallback support for model errors"""
    if not content:
        return "", "No content to summarize"
    
    if not llm:
        return "", "LLM not initialized. Please check your configuration."
    
    try:
        prompt = f"""Summarize this text in **5 clear bullet points**.
Each bullet should be concise, informative, and actionable.
Format with • for each bullet.

---
{content[:Config.MAX_TOTAL_CONTENT]}
---

Summary (5 bullets):"""
        
        if debug:
            st.write(f"🐛 Sending {len(content)} chars to Gemini")
        
        response = llm.invoke(prompt)
        summary = response.content if hasattr(response, "content") else str(response)
        
        return summary, None
        
    except Exception as e:
        error_str = str(e)
        error_lower = error_str.lower()
        
        # Handle model not found errors
        if "404" in error_str or "not_found" in error_lower or "model" in error_lower and "not found" in error_lower:
            st.warning("🔄 Model temporarily unavailable. Retrying with fallback...")
            st.session_state.use_fallback = True
            # Retry with cleared LLM cache
            st.cache_resource.clear()
            return "", "Model error - " + error_str
        
        # Handle authentication errors
        elif "401" in error_str or "unauthorized" in error_lower:
            st.error("❌ Authentication failed. Check your API key.")
            return "", "Authentication error: " + error_str
        
        # Handle timeout errors
        elif "timeout" in error_lower or "timed out" in error_lower:
            st.warning("⏱️ Request timeout. Try again.")
            return "", "Timeout error - " + error_str
        
        # Handle rate limiting
        elif "429" in error_str or "rate" in error_lower:
            st.warning("📊 Rate limited. Wait a moment then try again.")
            return "", "Rate limit error - " + error_str
        
        # Generic error
        else:
            st.error(f"Summarization error: {error_str[:100]}")
            return "", f"Summarization failed: {error_str[:100]}"

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def create_csv_export(summary_text: str) -> bytes:
    """Create CSV file from summary"""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        newline="",
        encoding="utf-8",
        delete=False
    ) as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["Summary"])
        writer.writerow([""])
        for line in summary_text.split("\n"):
            if line.strip():
                writer.writerow([line])
        tmp.flush()
        return Path(tmp.name).read_bytes()

def create_text_export(query: str, summary: str, urls: List[str]) -> bytes:
    """Create text file export"""
    content = f"""QUICKGLANCE - RESEARCH SUMMARY
{'=' * 70}

Query: {query}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 70}
SUMMARY
{'=' * 70}

{summary}

{'=' * 70}
SOURCES
{'=' * 70}

"""
    for i, url in enumerate(urls, 1):
        content += f"{i}. {url}\n"
    
    return content.encode("utf-8")

# ============================================================================
# MAIN UI
# ============================================================================

st.title("🔍 QuickGlance - Research Aggregator")
st.write("*Multi-agent AI system for research summarization*")

# Input section
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Enter your research query:",
        placeholder="e.g., Effects of exercise on mental health",
        help="What would you like to research?"
    )

with col2:
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Process query
if search_button:
    if not query or query.strip() == "":
        st.error("⚠️ Please enter a query")
    else:
        # Add to history
        if query not in st.session_state.query_history:
            st.session_state.query_history.append(query)
        
        with st.spinner("🔄 Processing your research..."):
            start_time = time.time()
            
            # Get fresh debug mode value
            current_debug = st.session_state.get("debug_mode", False)
            
            # Step 1: Search
            progress = st.progress(0)
            st.info("🔍 Step 1/3: Searching the web...")
            urls, search_error = search_serper(query, debug=current_debug)
            progress.progress(33)
            
            if search_error:
                st.error(f"Search failed: {search_error}")
                st.stop()
            
            if not urls:
                st.warning("No results found for this query")
                st.stop()
            
            # Step 2: Scrape
            st.info("📄 Step 2/3: Scraping content...")
            content, urls_success, scrape_errors = scrape_content(urls, debug=current_debug)
            progress.progress(66)
            
            if scrape_errors and current_debug:
                with st.expander("⚠️ Scraping errors"):
                    for error in scrape_errors:
                        st.write(f"• {error}")
            
            if not content:
                st.error("Could not retrieve content from any source")
                st.stop()
            
            # Step 3: Summarize
            st.info("✍️ Step 3/3: Generating summary...")
            llm = get_llm()
            summary, summarize_error = summarize_with_gemini(content, llm, debug=current_debug)
            progress.progress(100)
            time.sleep(0.5)
            progress.empty()
            
            if summarize_error:
                st.error(f"Summarization failed: {summarize_error}")
                st.stop()
            
            elapsed_time = time.time() - start_time
            
            # Store result
            st.session_state.last_result = {
                "query": query,
                "urls": urls,
                "summary": summary,
                "time": elapsed_time
            }

# Display results
if st.session_state.last_result:
    result = st.session_state.last_result
    current_debug = st.session_state.get("debug_mode", False)
    
    # Results header
    st.success(f"✅ Complete in {result['time']:.2f}s")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📌 Sources", "📊 Debug Info", "💾 Export"])
    
    with tab1:
        st.markdown("### Summary")
        st.markdown(result["summary"])
    
    with tab2:
        st.markdown("### Sources Used")
        for i, url in enumerate(result["urls"], 1):
            st.write(f"{i}. [{url}]({url})")
    
    with tab3:
        if current_debug:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("URLs Found", len(result["urls"]))
            with col2:
                st.metric("Execution Time", f"{result['time']:.2f}s")
            with col3:
                st.metric("Content Length", f"{len(st.session_state.get('last_content', ''))} chars")
            
            with st.expander("Configuration"):
                st.code(f"Max Content/URL: {Config.MAX_CONTENT_PER_URL}")
                st.code(f"Max Total: {Config.MAX_TOTAL_CONTENT}")
                st.code(f"Serper Timeout: {Config.SERPER_TIMEOUT}s")
        else:
            st.info("Enable Debug Mode in sidebar to see detailed information")
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            csv_bytes = create_csv_export(result["summary"])
            st.download_button(
                "📥 Download as CSV",
                csv_bytes,
                file_name=f"summary_{int(time.time())}.csv",
                mime="text/csv"
            )
        
        with col2:
            text_bytes = create_text_export(result["query"], result["summary"], result["urls"])
            st.download_button(
                "📥 Download as TXT",
                text_bytes,
                file_name=f"summary_{int(time.time())}.txt",
                mime="text/plain"
            )

# Footer
st.divider()
st.caption("🚀 QuickGlance v1.0 - Multi-Agent Research Aggregator | Powered by Gemini + Serper")
