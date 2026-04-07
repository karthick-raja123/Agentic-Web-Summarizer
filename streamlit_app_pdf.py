"""
🎨 Modern Streamlit App with PDF Support & Enhanced UI
Connects to FastAPI backend for summarization
Supports both web queries and PDF uploads
"""

import streamlit as st
import requests
import json
from pathlib import Path
import time
from datetime import datetime
from typing import Optional, Dict, List
import csv
from io import StringIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="QuickGlance - Smart Summarizer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - MODERN MINIMAL DESIGN
# ============================================================================

st.markdown("""
<style>
    /* Modern color palette */
    :root {
        --primary: #F54545;
        --secondary: #1F2937;
        --accent: #3B82F6;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --light: #F9FAFB;
        --dark: #111827;
    }
    
    /* Main container */
    .main {
        background-color: #FFFFFF;
    }
    
    /* Cards */
    .card {
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        padding: 16px;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.2s;
    }
    
    .card:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .status-success {
        background-color: #DCFCE7;
        color: #166534;
    }
    
    .status-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    
    .status-error {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    
    /* Progress text */
    .progress-text {
        font-size: 12px;
        color: #6B7280;
        margin-top: 8px;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 12px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:8000"  # Change to deployed URL

# Create session state for API calls
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = API_BASE_URL

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def check_api_health() -> tuple:
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(
            f"{st.session_state.api_base_url}/health",
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        return False, "API returned error"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)

def get_metrics(hours: int = 24) -> Optional[Dict]:
    """Fetch metrics from the API"""
    try:
        response = requests.get(
            f"{st.session_state.api_base_url}/metrics",
            params={"hours": hours},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return None

def display_metrics_dashboard():
    """Display comprehensive metrics dashboard"""
    st.markdown("### 📊 Performance Metrics Dashboard")
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        hours = st.selectbox("Time Period", [1, 6, 24], key="metrics_hours")
    
    with col1:
        if st.button("🔄 Refresh Metrics", use_container_width=False):
            st.rerun()
    
    # Fetch metrics
    metrics = get_metrics(hours=hours)
    
    if not metrics:
        st.warning("📊 No metrics available yet. Run some summarizations to see data.")
        return
    
    # Summary stats
    st.subheader("📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Requests</div>
            <div class="metric-value">{metrics.get('total_requests', 0)}</div>
            <small>In {hours}h period</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        success_rate = metrics.get('success_rate', 0)
        status_icon = "✅" if success_rate > 90 else "⚠️" if success_rate > 70 else "❌"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">{success_rate:.1f}%</div>
            <small>{status_icon} {('Excellent' if success_rate > 90 else 'Good' if success_rate > 70 else 'Fair')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_quality = metrics.get('avg_quality_score', 0)
        quality_status = "✅" if avg_quality > 0.7 else "⚠️" if avg_quality > 0.5 else "❌"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">Avg Quality</div>
            <div class="metric-value">{avg_quality:.2f}</div>
            <small>{quality_status} Quality Score</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">Avg Latency</div>
            <div class="metric-value">{metrics.get('avg_latency_seconds', 0):.1f}s</div>
            <small>End-to-end time</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Latency breakdown
    st.subheader("⏱️ Latency Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Search", f"{metrics.get('avg_search_time', 0):.2f}s", 
                 delta=f"-{metrics.get('avg_search_time', 0) * 10 / metrics.get('avg_latency_seconds', 1):.0f}%" if metrics.get('avg_latency_seconds', 0) > 0 else None)
    
    with col2:
        st.metric("Scrape", f"{metrics.get('avg_scrape_time', 0):.2f}s",
                 delta=f"-{metrics.get('avg_scrape_time', 0) * 10 / metrics.get('avg_latency_seconds', 1):.0f}%" if metrics.get('avg_latency_seconds', 0) > 0 else None)
    
    with col3:
        st.metric("Summarize", f"{metrics.get('avg_summarize_time', 0):.2f}s",
                 delta=f"-{metrics.get('avg_summarize_time', 0) * 10 / metrics.get('avg_latency_seconds', 1):.0f}%" if metrics.get('avg_latency_seconds', 0) > 0 else None)
    
    with col4:
        st.metric("Median", f"{metrics.get('median_latency_seconds', 0):.2f}s")
    
    st.divider()
    
    # Token usage
    st.subheader("🔤 Token Usage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Tokens/Request", metrics.get('avg_tokens', 0))
    
    with col2:
        total_tokens = metrics.get('total_tokens', 0)
        # Estimate cost (GPT-4: $0.03 per 1K input, $0.06 per 1K output)
        estimated_cost = (total_tokens * 0.00003)  # Rough estimate
        st.metric("Total Tokens", f"{total_tokens:,}")
    
    with col3:
        st.metric("Estimated Cost", f"${estimated_cost:.2f}")
    
    st.divider()
    
    # Request distribution
    st.subheader("📋 Request Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**By Type**")
        request_types = metrics.get('request_types', {})
        if request_types:
            for req_type, count in request_types.items():
                st.write(f"- {req_type}: {count}")
        else:
            st.caption("No data")
    
    with col2:
        st.write("**By Status**")
        status_dist = metrics.get('status_distribution', {})
        if status_dist:
            success_count = status_dist.get('success', 0)
            failed_count = status_dist.get('failed', 0)
            total = success_count + failed_count
            if total > 0:
                st.write(f"✅ Success: {success_count} ({success_count*100/total:.1f}%)")
                st.write(f"❌ Failed: {failed_count} ({failed_count*100/total:.1f}%)")
        else:
            st.caption("No data")

def summarize_query(query: str, max_iterations: int = 2, progress_callback=None) -> dict:
    """Call API to summarize web query with progress tracking"""
    try:
        if progress_callback:
            progress_callback(0.3, "🔍 Searching the web...")
        
        response = requests.post(
            f"{st.session_state.api_base_url}/summarize",
            json={
                "query": query,
                "max_iterations": max_iterations,
                "quality_threshold": 0.6
            },
            timeout=120
        )
        
        if progress_callback:
            progress_callback(0.7, "✍️ Generating summary...")
        
        if response.status_code == 200:
            result = response.json()
            if progress_callback:
                progress_callback(1.0, "✅ Complete!")
            return result
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Request timed out. API might be processing large content."}
    except requests.exceptions.ConnectionError:
        return {"error": "🔌 Cannot connect to API. Make sure backend is running."}
    except Exception as e:
        return {"error": f"❌ {str(e)}"}

def summarize_pdf(file_content: bytes, filename: str, progress_callback=None) -> dict:
    """Call API to summarize PDF with progress tracking"""
    try:
        if progress_callback:
            progress_callback(0.2, "📖 Reading PDF...")
        
        files = {"file": (filename, file_content, "application/pdf")}
        
        if progress_callback:
            progress_callback(0.5, "🔄 Processing content...")
        
        response = requests.post(
            f"{st.session_state.api_base_url}/summarize",
            files=files,
            timeout=120
        )
        
        if progress_callback:
            progress_callback(0.8, "✍️ Generating summary...")
        
        if response.status_code == 200:
            result = response.json()
            if progress_callback:
                progress_callback(1.0, "✅ Complete!")
            return result
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "⏱️ PDF processing timed out. File might be large."}
    except requests.exceptions.ConnectionError:
        return {"error": "🔌 Cannot connect to API. Make sure backend is running."}
    except Exception as e:
        return {"error": f"❌ {str(e)}"}

def display_error_card(error_msg: str):
    """Display styled error card"""
    col1, col2 = st.columns([0.5, 10])
    with col1:
        st.error("❌", icon="🔴")
    with col2:
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #EF4444;">
            <strong>Error</strong><br>
            {error_msg}
        </div>
        """, unsafe_allow_html=True)

def display_success_card(title: str, message: str):
    """Display styled success card"""
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid #10B981; background: #F0FDF4;">
        <strong style="color: #166534;">✅ {title}</strong><br>
        <span style="color: #065F46;">{message}</span>
    </div>
    """, unsafe_allow_html=True)

def display_source_card(url: str, snippet: str, quality: float):
    """Display styled source card"""
    quality_color = "#10B981" if quality > 0.7 else "#F59E0B" if quality > 0.5 else "#EF4444"
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <strong>🔗 Source</strong><br>
                <code style="color: #3B82F6;">{url[:60]}...</code><br>
                <small style="color: #6B7280;">{snippet[:100]}...</small>
            </div>
            <div style="background: {quality_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">
                {quality:.1%} Quality
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def format_summary_output(result: dict):
    """Format summarization result for display"""
    if "error" in result:
        display_error_card(result["error"])
        return
    
    if result.get("status") == "error":
        display_error_card(result.get('error', 'Unknown error occurred'))
        return
    
    # Success state
    display_success_card("Summary Generated", "AI has processed your content successfully")
    
    # Main summary in expandable card
    with st.expander("📝 Full Summary", expanded=True):
        st.markdown(f"""
        <div class="card">
            {result.get("summary", "No summary available")}
        </div>
        """, unsafe_allow_html=True)
    
    # Bullet points with expandable
    if result.get("bullets") or result.get("bullet_points"):
        bullets = result.get("bullets") or result.get("bullet_points", [])
        if bullets:
            with st.expander("🎯 Key Points", expanded=True):
                for i, point in enumerate(bullets, 1):
                    st.markdown(f"**{i}.** {point}")
    
    # Metrics section
    st.markdown("### 📊 Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quality = result.get("quality_score", 0)
        status = "✅" if quality > 0.7 else "⚠️" if quality > 0.5 else "❌"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Quality Score</div>
            <div class="metric-value">{quality:.2f}</div>
            <small>{status} {('Excellent' if quality > 0.7 else 'Good' if quality > 0.5 else 'Fair')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sources = result.get("sources_used", 0)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Sources</div>
            <div class="metric-value">{sources}</div>
            <small>High-quality sources</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Use processing_time if available, with fallback to processing_time_ms
        time_taken = result.get("processing_time", 0) or (result.get("processing_time_ms", 0) / 1000)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">Processing</div>
            <div class="metric-value">{time_taken:.1f}s</div>
            <small>Time taken</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        reflection = result.get("reflection_score", 0)
        status = "✅" if reflection > 0.7 else "⚠️"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">Reflection</div>
            <div class="metric-value">{reflection:.2f}</div>
            <small>{status} Quality check</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed metrics (latency and tokens)
    if result.get("latency_metrics") or result.get("token_metrics"):
        st.divider()
        st.markdown("### ⏱️ Detailed Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Latency Breakdown")
            latency = result.get("latency_metrics", {})
            if latency:
                metrics_data = [
                    ("Search", latency.get("search_time", 0)),
                    ("Scrape", latency.get("scrape_time", 0)),
                    ("Rank", latency.get("rank_time", 0)),
                    ("Summarize", latency.get("summarize_time", 0)),
                    ("Reflection", latency.get("reflection_time", 0)),
                ]
                for label, value in metrics_data:
                    if value > 0:
                        st.metric(label, f"{value:.2f}s")
            else:
                st.caption("No breakdown available")
        
        with col2:
            st.subheader("Token Usage")
            tokens = result.get("token_metrics", {})
            if tokens:
                total_tokens = tokens.get("total_tokens", 0)
                st.metric("Total Tokens", f"{total_tokens:,}")
                st.metric("Input Tokens", tokens.get("input_tokens", 0))
                st.metric("Output Tokens", tokens.get("output_tokens", 0))
                if tokens.get("estimated_cost", 0) > 0:
                    st.metric("Est. Cost", f"${tokens.get('estimated_cost', 0):.4f}")
            else:
                st.caption("No token data available")
        
        # Request ID for reference
        request_id = result.get("request_id", "")
        if request_id:
            st.caption(f"🔗 Request ID: `{request_id}`")
    
    # Export options
    st.divider()
    st.markdown("### 💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_str = json.dumps(result, indent=2)
        st.download_button(
            "📋 JSON",
            json_str,
            "summary.json",
            "application/json",
            use_container_width=True
        )
    
    with col2:
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Quality Score", result.get("quality_score", "N/A")])
        writer.writerow(["Sources Used", result.get("sources_used", "N/A")])
        # Use processing_time if available
        time_taken = result.get("processing_time", 0) or (result.get("processing_time_ms", 0) / 1000)
        writer.writerow(["Processing Time", f"{time_taken:.1f}s"])
        writer.writerow(["Summary", result.get("summary", "N/A")[:500]])
        tokens = result.get("token_metrics", {})
        if tokens:
            writer.writerow(["Total Tokens", tokens.get("total_tokens", 0)])
        
        st.download_button(
            "📊 CSV",
            csv_buffer.getvalue(),
            "summary.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col3:
        summary_text = f"""
SUMMARY REPORT
{'='*50}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

QUALITY METRICS:
- Quality Score: {result.get('quality_score', 'N/A')}
- Sources Used: {result.get('sources_used', 'N/A')}
- Processing Time: {result.get('processing_time_ms', 0)/1000:.1f}s
- Reflection Score: {result.get('reflection_score', 'N/A')}

SUMMARY:
{result.get('summary', 'N/A')}

KEY POINTS:
{chr(10).join(f'- {p}' for p in (result.get('bullets') or result.get('bullet_points', [])))}
        """
        st.download_button(
            "📄 Text",
            summary_text,
            "summary.txt",
            "text/plain",
            use_container_width=True
        )

# ============================================================================
# SIDEBAR - SETTINGS & STATUS
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # API Health Status Card
    st.subheader("🔌 API Status")
    is_healthy, health_info = check_api_health()
    
    if is_healthy:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #10B981; background: #F0FDF4;">
            <span class="status-badge status-success">✅ ONLINE</span><br>
            <small style="color: #065F46;">API is responding normally</small>
        </div>
        """, unsafe_allow_html=True)
        if health_info:
            st.caption(f"Uptime: {health_info.get('uptime_seconds', 0)}s")
    else:
        st.markdown("""
        <div class="card" style="border-left: 4px solid #EF4444; background: #FEF2F2;">
            <span class="status-badge status-error">❌ OFFLINE</span><br>
            <small style="color: #991B1B;">API is not responding</small>
        </div>
        """, unsafe_allow_html=True)
    
    # API Configuration
    st.divider()
    st.subheader("🔧 Configuration")
    
    custom_api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="Change to deployed API URL"
    )
    
    if custom_api_url != st.session_state.api_base_url:
        st.session_state.api_base_url = custom_api_url
        st.rerun()
    
    # Processing settings
    st.divider()
    st.subheader("⚡ Processing")
    
    max_iterations = st.slider(
        "Max Iterations",
        min_value=1,
        max_value=3,
        value=2,
        help="Higher = more thorough but slower"
    )
    st.session_state.max_iterations = max_iterations
    
    quality_threshold = st.slider(
        "Quality Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.1,
        help="Filter low-quality sources"
    )
    st.session_state.quality_threshold = quality_threshold
    
    # About section
    st.divider()
    st.subheader("ℹ️ About")
    st.info("""
    **QuickGlance** - Modern AI Summarizer
    
    Transform any web content or PDF into concise, actionable summaries.
    
    [GitHub](https://github.com) | [Docs](https://docs)
    """)
    
    # Footer
    st.divider()
    st.caption(f"v1.0 • {datetime.now().strftime('%Y-%m-%d')}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.title("✨")
with col2:
    st.title("QuickGlance Summarizer")

st.markdown("**Transform any content into concise, actionable insights** powered by AI", 
            help="Web articles, PDFs, or documents - all converted to smart summaries")

st.divider()

# Select mode
tab1, tab2, tab3 = st.tabs(["🔍 Web Query", "📄 PDF Upload", "📊 Metrics"])

# ============================================================================
# TAB 1: WEB QUERY
# ============================================================================

with tab1:
    st.markdown("""
    <div class="card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-bottom: 20px;">
        <h3 style="margin: 0;">🔍 Web Query Summarization</h3>
        <small>Search the web and get AI-powered summaries in seconds</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "What do you want to know?",
            placeholder="e.g., Latest trends in AI, Machine learning in healthcare...",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True, key="search_btn")
    
    if search_button:
        if not query.strip():
            st.markdown("""
            <div class="card" style="border-left: 4px solid #F59E0B; background: #FFFBEB;">
                <strong style="color: #92400E;">⚠️ Input Required</strong><br>
                <small style="color: #92400E;">Please enter a topic to summarize</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Progress section
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            def update_progress(value: float, status: str):
                with progress_placeholder.container():
                    st.progress(value, text=status)
                with status_placeholder.container():
                    st.caption(f"⏱️ {status}")
            
            with st.spinner("Processing..."):
                result = summarize_query(query, st.session_state.max_iterations, update_progress)
                time.sleep(0.5)  # Brief pause for UX
            
            # Clear progress
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Display results
            format_summary_output(result)
    
    # Recent searches
    with st.expander("📚 Tips"):
        st.markdown("""
        - **Be specific**: "Machine learning in healthcare" → better than "AI"
        - **Use natural language**: Ask as you would in conversation
        - **Combine keywords**: Mix different topics for richer results
        """)


# ============================================================================
# TAB 2: PDF UPLOAD
# ============================================================================

with tab2:
    st.markdown("""
    <div class="card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; margin-bottom: 20px;">
        <h3 style="margin: 0;">📄 PDF Summarization</h3>
        <small>Upload any PDF and get an instant AI-powered summary</small>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload area
    uploaded_file = st.file_uploader(
        "Drag and drop a PDF here or click to browse",
        type="pdf",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # File info card
        file_size_kb = uploaded_file.size / 1024
        file_size_mb = file_size_kb / 1024
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <strong>📄 {uploaded_file.name}</strong><br>
                <small style="color: #6B7280;">Ready to process</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Size", f"{file_size_mb:.1f} MB" if file_size_mb >= 1 else f"{file_size_kb:.0f} KB")
        
        with col3:
            if file_size_mb > 20:
                st.warning("⚠️ Large file")
            else:
                st.success("✅ OK")
        
        # Process button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            process_button = st.button("📊 Summarize PDF", use_container_width=True, key="pdf_btn")
        
        if process_button:
            # Progress section
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            def update_pdf_progress(value: float, status: str):
                with progress_placeholder.container():
                    st.progress(value, text=status)
                with status_placeholder.container():
                    st.caption(f"⏱️ {status}")
            
            with st.spinner("Processing PDF..."):
                result = summarize_pdf(
                    uploaded_file.read(),
                    uploaded_file.name,
                    update_pdf_progress
                )
                time.sleep(0.5)
            
            # Clear progress
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Display results
            format_summary_output(result)
    
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 40px; border: 2px dashed #E5E7EB; border-radius: 8px;">
            <h2>📄 Upload a PDF to get started</h2>
            <p style="color: #6B7280;">Supported formats: PDF (< 20 MB)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # FAQ
    with st.expander("❓ FAQ"):
        st.markdown("""
        **What file formats are supported?**
        - PDF files up to 20 MB
        
        **How long does processing take?**
        - Usually 10-30 seconds depending on file size
        
        **What happens to my file?**
        - Files are not stored, processed only for summarization
        """)

# ============================================================================
# TAB 3: METRICS DASHBOARD
# ============================================================================

with tab3:
    st.markdown("""
    <div class="card" style="background: linear-gradient(135deg, #FFB347 0%, #FF8C00 100%); color: white; margin-bottom: 20px;">
        <h3 style="margin: 0;">📊 Performance Dashboard</h3>
        <small>Real-time metrics and system statistics</small>
    </div>
    """, unsafe_allow_html=True)
    
    display_metrics_dashboard()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("❤️ Like this?", use_container_width=True):
        st.balloons()
        st.success("Thanks for the love! 🙏")

with col2:
    st.caption(f"API: {st.session_state.api_base_url}")

with col3:
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
