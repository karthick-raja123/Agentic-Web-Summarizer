#!/usr/bin/env python3
"""
Enhanced Streamlit UI for Multi-Agent Pipeline
Modern design with dark theme, progress bars, URL cards, audio player, and download options
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import base64
import csv
import tempfile
import io
from urllib.parse import urlparse

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_pipeline import MultiAgentPipeline

# ============================================================================
# PAGE CONFIGURATION & THEME
# ============================================================================

st.set_page_config(
    page_title="QuickGlance AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "QuickGlance - Modern AI-powered research aggregator"
    }
)

# Dark theme & modern styling
st.markdown("""
    <style>
    /* Root colors - Dark theme */
    :root {
        --primary: #00D9FF;
        --primary-dark: #0099CC;
        --secondary: #6A0DAD;
        --success: #00FF9F;
        --warning: #FFB700;
        --error: #FF3366;
        --bg-dark: #0F1419;
        --bg-secondary: #1A1F2E;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B8C1;
        --border-color: #2A3142;
    }

    /* Main container */
    .stMainBlockContainer {
        background: linear-gradient(135deg, #0F1419 0%, #1A1F2E 100%);
        color: var(--text-primary);
    }

    /* Overall body background */
    body {
        background: var(--bg-dark);
        color: var(--text-primary);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    h1 {
        background: linear-gradient(135deg, #00D9FF, #6A0DAD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00D9FF, #6A0DAD);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 217, 255, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 217, 255, 0.5) !important;
    }

    /* Cards */
    .url-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #252D3D 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.3s ease;
        border-left: 4px solid var(--primary);
    }

    .url-card:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 24px rgba(0, 217, 255, 0.15);
        transform: translateX(4px);
    }

    /* Progress bar styling */
    .progress-text {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-top: 4px;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .status-success {
        background: rgba(0, 255, 159, 0.2);
        color: var(--success);
        border: 1px solid var(--success);
    }

    .status-warning {
        background: rgba(255, 183, 0, 0.2);
        color: var(--warning);
        border: 1px solid var(--warning);
    }

    .status-error {
        background: rgba(255, 51, 102, 0.2);
        color: var(--error);
        border: 1px solid var(--error);
    }

    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, #1A1F2E 0%, #252D3D 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid var(--border-color);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1A1F2E 0%, #252D3D 100%) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #252D3D 0%, #303A4D 100%) !important;
    }

    /* Divider */
    .stDivider {
        border-color: var(--border-color) !important;
        margin: 2rem 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1419 0%, #1A1F2E 100%) !important;
    }

    /* Error/Warning boxes */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid !important;
    }

    .stError {
        border-left-color: var(--error) !important;
        background: rgba(255, 51, 102, 0.1) !important;
    }

    .stWarning {
        border-left-color: var(--warning) !important;
        background: rgba(255, 183, 0, 0.1) !important;
    }

    .stSuccess {
        border-left-color: var(--success) !important;
        background: rgba(0, 255, 159, 0.1) !important;
    }

    .stInfo {
        border-left-color: var(--primary) !important;
        background: rgba(0, 217, 255, 0.1) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00FF9F, #00D9FF);
        color: var(--bg-dark);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
    }

    .stTabs [aria-selected="true"] [data-baseweb="tab"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: var(--bg-dark);
    }

    /* Code blocks */
    .stCodeBlock {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }

    /* Loading spinner */
    .spinner {
        color: var(--primary);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return 'unknown'


def get_status_icon(status: str) -> str:
    """Get icon for status"""
    icons = {
        'success': '✅',
        'partial_success': '⚠️',
        'failed': '❌',
        'running': '⏳'
    }
    return icons.get(status, '❓')


def get_status_class(status: str) -> str:
    """Get CSS class for status"""
    classes = {
        'success': 'status-success',
        'partial_success': 'status-warning',
        'failed': 'status-error'
    }
    return classes.get(status, '')


def create_csv_content(summary_text: str) -> str:
    """Create CSV content from summary"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Item', 'Content'])
    
    lines = summary_text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            writer.writerow([f'Point {i}', line.strip()])
    
    return output.getvalue()


def create_txt_content(summary_text: str) -> str:
    """Create TXT content from summary"""
    return summary_text


# ============================================================================
# UI COMPONENTS
# ============================================================================

def display_header():
    """Display modern header with gradient"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write("")
    
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 2rem 0;'>
                <h1 style='margin: 0;'>🚀 QuickGlance AI</h1>
                <p style='color: #B0B8C1; font-size: 1.1rem; margin-top: 0.5rem;'>
                    Modern AI-powered research & content aggregation
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.write("")
    
    st.divider()


def display_query_input():
    """Display modern query input section"""
    st.markdown("### 🔍 What would you like to know?")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        query = st.text_input(
            "Enter your search query",
            placeholder="e.g., 'Latest AI trends in 2026'",
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # Spacing
        process_button = st.button("Search", use_container_width=True, type="primary")
    
    return query, process_button


def display_url_preview_card(url: str, title: str = None, snippet: str = None):
    """Display modern URL preview card"""
    domain = get_domain_from_url(url)
    
    st.markdown(f"""
        <div class='url-card'>
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div style='flex: 1;'>
                    <p style='color: var(--primary); font-size: 0.875rem; margin: 0; font-weight: 600;'>
                        🌐 {domain}
                    </p>
                    {f"<p style='color: var(--text-primary); font-weight: 600; margin: 8px 0 4px 0;'>{title}</p>" if title else ""}
                    {f"<p style='color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.4;'>{snippet}</p>" if snippet else ""}
                    <p style='color: var(--text-secondary); font-size: 0.8rem; margin: 8px 0 0 0; word-break: break-all;'>
                        {url}
                    </p>
                </div>
                <a href='{url}' target='_blank' style='margin-left: 12px; padding: 6px 12px; background: linear-gradient(135deg, #00D9FF, #6A0DAD); 
                   color: white; border-radius: 6px; text-decoration: none; font-size: 0.8rem; white-space: nowrap; font-weight: 600;'>
                    Open ↗
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)


def display_progress_section(total_steps: int, current_step: int, step_name: str):
    """Display modern progress bar"""
    progress = current_step / total_steps
    
    st.markdown(f"""
        <div style='margin: 20px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <p style='margin: 0; font-weight: 600; color: var(--text-primary);'>📊 Progress</p>
                <p style='margin: 0; color: var(--text-secondary); font-size: 0.875rem;'>{current_step}/{total_steps} - {step_name}</p>
            </div>
            <div style='width: 100%; height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; border: 1px solid var(--border-color);'>
                <div style='width: {progress * 100}%; height: 100%; background: linear-gradient(90deg, #00D9FF, #6A0DAD); 
                           transition: width 0.3s ease; border-radius: 3px;'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def display_status_metrics(result: dict):
    """Display key metrics in modern design"""
    status = result.get('status', 'unknown')
    icon = get_status_icon(status)
    badge_class = get_status_class(status)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='stMetric'>
                <p style='color: var(--text-secondary); font-size: 0.875rem; margin: 0;'>Status</p>
                <p style='color: var(--text-primary); font-size: 1.5rem; font-weight: 700; margin: 4px 0 0 0;'>
                    {icon} {status.upper()}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        agents_count = len(result.get('agent_history', []))
        st.markdown(f"""
            <div class='stMetric'>
                <p style='color: var(--text-secondary); font-size: 0.875rem; margin: 0;'>Agents Used</p>
                <p style='color: var(--primary); font-size: 1.5rem; font-weight: 700; margin: 4px 0 0 0;'>
                    {agents_count} 🤖
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        url_count = len(result.get('search_results', {}).get('results', []))
        st.markdown(f"""
            <div class='stMetric'>
                <p style='color: var(--text-secondary); font-size: 0.875rem; margin: 0;'>URLs Found</p>
                <p style='color: var(--primary); font-size: 1.5rem; font-weight: 700; margin: 4px 0 0 0;'>
                    {url_count} 🔗
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        timestamp = result.get('timestamp', 'N/A')
        st.markdown(f"""
            <div class='stMetric'>
                <p style='color: var(--text-secondary); font-size: 0.875rem; margin: 0;'>Time</p>
                <p style='color: var(--text-primary); font-size: 0.9rem; font-weight: 600; margin: 4px 0 0 0;'>
                    {timestamp[:10] if timestamp else 'N/A'}
                </p>
            </div>
        """, unsafe_allow_html=True)


def display_urls_section(result: dict):
    """Display URL preview cards"""
    if not result.get('search_results'):
        return
    
    urls = result['search_results'].get('results', [])
    
    if not urls:
        st.info("📭 No URLs found for this query")
        return
    
    st.markdown("### 🔗 Source URLs")
    
    # Tab view for URL presentation
    tab1, tab2 = st.tabs(["Cards View", "List View"])
    
    with tab1:
        for url_item in urls[:5]:
            display_url_preview_card(
                url=url_item.get('url', ''),
                title=url_item.get('title', ''),
                snippet=url_item.get('snippet', '')
            )
        
        if len(urls) > 5:
            with st.expander(f"📄 View {len(urls) - 5} more URLs"):
                for url_item in urls[5:]:
                    display_url_preview_card(
                        url=url_item.get('url', ''),
                        title=url_item.get('title', ''),
                        snippet=url_item.get('snippet', '')
                    )
    
    with tab2:
        for i, url_item in enumerate(urls, 1):
            st.markdown(f"**{i}. {url_item.get('title', 'No title')}**")
            st.code(url_item.get('url', 'N/A'), language='text')


def display_summary_section(result: dict):
    """Display expandable summary section"""
    summary = result.get('summary', '')
    
    if not summary:
        return
    
    st.markdown("### 📝 Summary")
    
    # Expandable summary with preview
    col1, col2 = st.columns([20, 1])
    
    with col1:
        # Show first 200 chars as preview
        preview = summary[:200] + "..." if len(summary) > 200 else summary
        
        with st.expander("Click to expand summary", expanded=True):
            st.markdown(summary)
            st.caption(f"📊 Length: {len(summary)} characters | Paragraphs: {len(summary.split('\\n\\n'))}")


def display_audio_player(result: dict):
    """Display modern audio player if available"""
    if not result.get('formatted_output'):
        return
    
    formatted_output = result['formatted_output']
    formats = formatted_output.get('formats', {})
    
    # Check if audio file exists
    audio_format = formats.get('audio', {})
    audio_path = audio_format.get('file_path') if audio_format else None
    
    if audio_path and Path(audio_path).exists():
        st.markdown("### 🎵 Audio Summary")
        
        try:
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Modern audio player
            st.markdown("""
                <div style='background: linear-gradient(135deg, #1A1F2E 0%, #252D3D 100%); 
                           border: 1px solid var(--border-color); border-radius: 12px; 
                           padding: 16px; margin: 16px 0;'>
                    <p style='color: var(--text-secondary); font-size: 0.875rem; margin: 0 0 12px 0;'>
                        🎧 Listen to the summary
                    </p>
            """, unsafe_allow_html=True)
            
            st.audio(audio_bytes, format='audio/mp3')
            
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ Could not load audio: {str(e)}")


def display_download_section(result: dict):
    """Display modern download options"""
    summary = result.get('summary', '')
    
    if not summary:
        return
    
    st.markdown("### 💾 Download Results")
    
    col1, col2, col3 = st.columns(3)
    
    # CSV Download
    with col1:
        csv_content = create_csv_content(summary)
        st.download_button(
            label="📊 CSV",
            data=csv_content,
            file_name="summary.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # TXT Download
    with col2:
        txt_content = create_txt_content(summary)
        st.download_button(
            label="📄 TEXT",
            data=txt_content,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Audio Download (if available)
    with col3:
        if result.get('formatted_output'):
            formats = result['formatted_output'].get('formats', {})
            audio_format = formats.get('audio', {})
            audio_path = audio_format.get('file_path') if audio_format else None
            
            if audio_path and Path(audio_path).exists():
                try:
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    st.download_button(
                        label="🎵 AUDIO",
                        data=audio_bytes,
                        file_name="summary.mp3",
                        mime="audio/mpeg",
                        use_container_width=True
                    )
                except:
                    st.button("🎵 AUDIO", disabled=True, use_container_width=True)
            else:
                st.button("🎵 AUDIO", disabled=True, use_container_width=True)
        else:
            st.button("🎵 AUDIO", disabled=True, use_container_width=True)


def display_error_section(result: dict):
    """Display modern error handling"""
    if result.get('status') not in ['failed', 'partial_success']:
        return
    
    st.markdown("### ⚠️ Issues Detected")
    
    error_msg = result.get('error_message', 'Unknown error occurred')
    
    with st.expander("View Error Details", expanded=True):
        st.error(f"❌ {error_msg}")
        
        # Show additional troubleshooting
        st.markdown("""
            **🔧 Troubleshooting Tips:**
            - Check your internet connection
            - Try a different or more specific query
            - Wait a few moments and try again
            - Check the API quotas in your configuration
        """)


def display_sidebar():
    """Display modern sidebar"""
    st.sidebar.markdown("""
        <h2 style='color: var(--text-primary);'>⚙️ Settings</h2>
    """, unsafe_allow_html=True)
    
    enable_eval = st.sidebar.checkbox(
        "📊 Content Evaluation",
        value=True,
        help="Filter content by relevance score"
    )
    
    enable_format = st.sidebar.checkbox(
        "💾 Export Formats",
        value=True,
        help="Generate CSV, TXT, and Audio outputs"
    )
    
    st.sidebar.divider()
    
    st.sidebar.markdown("""
        <h2 style='color: var(--text-primary);'>ℹ️ About</h2>
        
        **QuickGlance AI** uses an intelligent multi-agent system:
        
        - 🎯 **Smart Planning** - Understands your query intent
        - 🔍 **Web Search** - Finds relevant sources
        - 🪄 **Content Extraction** - Scrapes key information
        - ⭐ **Quality Filtering** - Evaluates relevance
        - 📝 **Summarization** - Creates concise summaries
        - 💾 **Multi-Format Export** - CSV, TXT, Audio
        
        **Modern Features:**
        - 🌙 Dark theme optimized
        - ⚡ Real-time progress tracking
        - 🎨 Beautiful UI cards & animations
        - 🎵 Audio player integration
        - 📊 Comprehensive analytics
    """, unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    with st.sidebar.expander("📚 Quick Help"):
        st.markdown("""
        ### How to use:
        1. Enter your search query
        2. Click the **Search** button
        3. Watch real-time progress
        4. View summarized results
        5. Download in your preferred format
        
        ### Tips:
        - Be specific for better results
        - Use natural language
        - Long queries work better
        - Enable evaluation for filtering
        """)
    
    return enable_eval, enable_format


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    init_session_state()
    
    # Header
    display_header()
    
    # Sidebar (right side)
    enable_eval, enable_format = display_sidebar()
    
    # Query input
    query, process_button = display_query_input()
    
    st.divider()
    
    # Process query
    if process_button and query:
        # Progress tracking
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Step 1: Planning
            with progress_placeholder.container():
                display_progress_section(5, 1, "Analyzing query")
            
            with status_placeholder.container():
                st.info("🎯 Understanding your request...")
            
            # Step 2: Searching
            with progress_placeholder.container():
                display_progress_section(5, 2, "Searching the web")
            
            with status_placeholder.container():
                st.info("🔍 Finding relevant sources...")
            
            # Step 3: Scraping
            with progress_placeholder.container():
                display_progress_section(5, 3, "Extracting content")
            
            with status_placeholder.container():
                st.info("🪄 Gathering information...")
            
            # Step 4: Evaluation (if enabled)
            if enable_eval:
                with progress_placeholder.container():
                    display_progress_section(5, 4, "Evaluating quality")
                
                with status_placeholder.container():
                    st.info("⭐ Filtering content...")
            else:
                step = 4
            
            # Step 5: Summarizing
            with progress_placeholder.container():
                display_progress_section(5, 5, "Creating summary")
            
            with status_placeholder.container():
                st.info("📝 Generating summary...")
            
            # Run pipeline
            pipeline = MultiAgentPipeline(
                enable_evaluation=enable_eval,
                enable_formatting=enable_format
            )
            
            result = pipeline.run(query)
            st.session_state.result = result
            
            # Clear progress placeholders
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Add to history
            st.session_state.query_history.append({
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'status': result.get('status')
            })
            
            st.success("✅ Analysis complete!")
            
        except Exception as e:
            progress_placeholder.empty()
            status_placeholder.empty()
            
            st.error(f"""
            ❌ **Error Processing Query**
            
            {str(e)}
            """)
            st.session_state.result = None
    
    # Display results
    if st.session_state.result:
        st.divider()
        
        # Status metrics
        display_status_metrics(st.session_state.result)
        
        st.divider()
        
        # URLs section
        display_urls_section(st.session_state.result)
        
        st.divider()
        
        # Summary section
        display_summary_section(st.session_state.result)
        
        st.divider()
        
        # Audio player
        display_audio_player(st.session_state.result)
        
        st.divider()
        
        # Download options
        display_download_section(st.session_state.result)
        
        # Error section if needed
        if st.session_state.result.get('status') in ['failed', 'partial_success']:
            st.divider()
            display_error_section(st.session_state.result)
        
        st.divider()
        
        # Query analytics
        with st.expander("📊 Query Analytics"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Agent Count", len(st.session_state.result.get('agent_history', [])))
            
            with col2:
                st.metric("Summary Length", len(st.session_state.result.get('summary', '')))
            
            with col3:
                st.metric("URLs Processed", len(st.session_state.result.get('search_results', {}).get('results', [])))
            
            # Show full result JSON
            with st.expander("View Full Result Data (JSON)"):
                st.json(st.session_state.result)
    
    # Query history sidebar
    if st.session_state.query_history:
        st.sidebar.divider()
        st.sidebar.markdown("<h3 style='color: var(--text-primary);'>📜 Recent Searches</h3>", unsafe_allow_html=True)
        
        for i, hist in enumerate(reversed(st.session_state.query_history[-10:]), 1):
            status_icon = get_status_icon(hist['status'])
            st.sidebar.write(f"{i}. {status_icon} {hist['query'][:50]}")


if __name__ == '__main__':
    main()
