"""
Streamlit Application - User interface for Visual Web Agent.
Production-grade UI with error handling and output options.
"""

import streamlit as st
import base64
import csv
import tempfile
from pathlib import Path
from main import VisualWebAgentPipeline
from utils.logging_config import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="QuickGlance: Agentic Browser",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_pipeline():
    """Initialize or retrieve cached pipeline."""
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = VisualWebAgentPipeline(
            num_search_results=st.session_state.get("num_results", 5),
            summary_points=st.session_state.get("summary_points", 5),
            use_chunking=st.session_state.get("use_chunking", False)
        )
    return st.session_state.pipeline


def create_download_csv(summary_text: str) -> str:
    """Create CSV file for download."""
    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline='',
        encoding="utf-8"
    )
    writer = csv.writer(tmp)
    writer.writerow(["QuickGlance Summary"])
    writer.writerow([""])  # Empty line
    writer.writerow(["Summary"])
    writer.writerow([""])  # Empty line
    for line in summary_text.split("\n"):
        writer.writerow([line])
    tmp.close()
    return tmp.name


def main():
    """Main Streamlit application."""
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='main-header'>🔍 QuickGlance</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>AI-Powered Web Summarization</p>", unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    
    st.session_state.num_results = st.sidebar.slider(
        "Number of URLs to search",
        min_value=1,
        max_value=10,
        value=5
    )
    
    st.session_state.summary_points = st.sidebar.slider(
        "Summary bullet points",
        min_value=3,
        max_value=10,
        value=5
    )
    
    st.session_state.use_chunking = st.sidebar.checkbox(
        "Use hierarchical summarization (for long content)",
        value=False
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Pipeline Status")
    if "last_query" in st.session_state:
        st.sidebar.success(f"✅ Last query: {st.session_state.last_query[:30]}...")
    else:
        st.sidebar.info("No queries processed yet")
    
    # Main content area
    st.markdown("### 🔎 Search & Summarize Anything")
    
    # Input
    query = st.text_input(
        "Enter your topic for summarization:",
        placeholder="e.g., 'Artificial Intelligence trends 2024'",
        key="query_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_button = st.button("🚀 Search, Scrape & Summarize", use_container_width=True)
    
    with col2:
        clear_button = st.button("🔄 Clear", use_container_width=True)
    
    with col3:
        if st.sidebar.checkbox("Debug Mode"):
            st.info("Debug mode enabled - check logs for details")
    
    # Clear session state
    if clear_button:
        st.session_state.clear()
        st.rerun()
    
    # Process query
    if search_button:
        if not query or len(query.strip()) == 0:
            st.error("⚠️ Please enter a topic to proceed.")
        else:
            try:
                st.session_state.last_query = query
                
                # Initialize pipeline
                pipeline = initialize_pipeline()
                
                # Search phase
                with st.spinner("🔍 Searching using Serper API..."):
                    logger.info(f"Starting search for: {query}")
                
                # Execute pipeline
                with st.spinner("⏳ Fetching URLs, scraping content, and summarizing..."):
                    result = pipeline.run(query)
                
                # Display results
                if result["status"] == "success":
                    # URLs found
                    st.markdown("### 📌 Top URLs Found")
                    if result["urls"]:
                        for i, url in enumerate(result["urls"], 1):
                            st.markdown(f"**{i}.** [{url}]({url})")
                    else:
                        st.warning("No URLs were successfully scraped")
                    
                    # Summary
                    st.markdown("### 📝 Summary")
                    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
                    st.markdown(result["summary"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download options
                    st.markdown("### ⬇️ Download Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv_path = create_download_csv(result["summary"])
                        with open(csv_path, "rb") as f:
                            st.download_button(
                                label="📥 Download as CSV",
                                data=f,
                                file_name="summary.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                    with col2:
                        # Text file download
                        text_content = f"Query: {result['query']}\n\n{result['summary']}"
                        st.download_button(
                            label="📄 Download as Text",
                            data=text_content,
                            file_name="summary.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    logger.info(f"Query '{query}' processed successfully")
                
                else:
                    st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                    logger.error(f"Query failed: {result.get('error')}")
            
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                logger.error(f"Unexpected error in Streamlit app: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; color: #999; font-size: 12px;'>
    QuickGlance v1.0 | Powered by LangGraph + Gemini + Serper<br>
    Production-grade web agent for information extraction
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
