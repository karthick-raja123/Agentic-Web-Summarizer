#!/usr/bin/env python3
"""
Streamlit Web Interface for Multi-Agent Pipeline
Visualizes agent execution, routing decisions, and results
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_pipeline import MultiAgentPipeline
from utils.graph_visualizer import GraphVisualizer


# Configure page
st.set_page_config(
    page_title="Multi-Agent Pipeline",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .agent-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.2rem;
        border-radius: 0.5rem;
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        font-weight: 500;
    }
    .status-success {
        color: #2e7d32;
        font-weight: bold;
    }
    .status-partial {
        color: #f57c00;
        font-weight: bold;
    }
    .status-failed {
        color: #c62828;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def get_agent_emoji(agent_name: str) -> str:
    """Get emoji for agent"""
    emojis = {
        'planner': '🎯',
        'search': '🔍',
        'scraper': '🪄',
        'evaluator': '⭐',
        'summarizer': '📝',
        'formatter': '💾',
        'error_handler': '⚠️',
        'router': '🔄'
    }
    return emojis.get(agent_name, '●')


def get_status_color(status: str) -> str:
    """Get color for status badge"""
    colors = {
        'success': '#4caf50',
        'partial_success': '#ff9800',
        'failed': '#f44336',
        'running': '#2196f3'
    }
    return colors.get(status, '#757575')


def get_status_icon(status: str) -> str:
    """Get icon for status"""
    icons = {
        'success': '✅',
        'partial_success': '⚠️',
        'failed': '❌',
        'running': '⏳'
    }
    return icons.get(status, '❓')


def display_header():
    """Display main header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🤖 Multi-Agent Pipeline")
        st.markdown("*TRUE multi-agent system with dynamic routing & decision-making*")
    
    with col2:
        st.markdown("### Version: 1.0")
        st.markdown("*Experience intelligent query processing*")


def display_configuration():
    """Display configuration options"""
    st.sidebar.header("⚙️ Configuration")
    
    enable_eval = st.sidebar.checkbox(
        "Enable Content Evaluation",
        value=True,
        help="Filter content by relevance score"
    )
    
    enable_format = st.sidebar.checkbox(
        "Enable Multi-Format Output",
        value=False,
        help="Generate CSV, JSON, Markdown outputs"
    )
    
    show_graph = st.sidebar.checkbox(
        "Show Graph Visualization",
        value=False,
        help="Display agent flow diagram"
    )
    
    return enable_eval, enable_format, show_graph


def display_query_input():
    """Display query input"""
    st.header("📝 Enter Your Query")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Query:",
            placeholder="Ask anything... (e.g., 'What is machine learning?')",
            label_visibility="collapsed"
        )
    
    with col2:
        process_button = st.button(
            "🚀 Process",
            use_container_width=True,
            type="primary"
        )
    
    return query, process_button


def display_graph_visualization():
    """Display agent graph"""
    st.header("📊 Agent Flow Diagram")
    
    tab1, tab2, tab3 = st.tabs(["Simplified", "Detailed", "Mermaid"])
    
    viz = GraphVisualizer()
    
    with tab1:
        st.code(viz.draw_ascii_graph(simplified=True), language="text")
    
    with tab2:
        st.code(viz.draw_ascii_graph(simplified=False), language="text")
    
    with tab3:
        mermaid_code = viz.draw_mermaid_diagram()
        st.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    st.text("Replace with mermaid.live for interactive diagram")


def display_execution_status(result: dict):
    """Display execution status"""
    st.header("⚡ Execution Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    status = result.get('status', 'unknown')
    icon = get_status_icon(status)
    
    with col1:
        st.metric(
            "Status",
            f"{icon} {status.upper()}",
        )
    
    with col2:
        agents_count = len(result.get('agent_history', []))
        st.metric("Agents Executed", agents_count)
    
    with col3:
        if result.get('search_results'):
            url_count = len(result['search_results'].get('results', []))
            st.metric("URLs Found", url_count)
        else:
            st.metric("URLs Found", "0")
    
    with col4:
        timestamp = result.get('timestamp', 'N/A')
        st.metric("Timestamp", timestamp[:10] if timestamp else "N/A")


def display_routing_path(result: dict):
    """Display agent routing path"""
    st.header("🔀 Routing Path")
    
    agent_history = result.get('agent_history', [])
    routing_decisions = result.get('routing_decisions', [])
    
    # Visualize path
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Agents Executed")
        
        for i, agent in enumerate(agent_history, 1):
            emoji = get_agent_emoji(agent)
            st.write(f"{i}. {emoji} **{agent.upper()}**")
    
    with col2:
        st.subheader("Routing Decisions")
        
        if routing_decisions:
            for decision in routing_decisions:
                st.write(f"→ {decision}")
        else:
            st.write("No routing decisions recorded")
    
    # ASCII flow
    st.subheader("Execution Flow")
    flow_text = " → ".join([get_agent_emoji(a) for a in agent_history])
    st.markdown(f"### {flow_text}")


def display_execution_plan(result: dict):
    """Display execution plan"""
    if not result.get('plan'):
        return
    
    st.header("📋 Execution Plan")
    
    plan = result['plan']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Query Type", plan.get('query_type', 'unknown'))
        st.metric("Complexity", plan.get('complexity', 'unknown'))
    
    with col2:
        st.metric(
            "Evaluation Needed",
            "✅ Yes" if plan.get('needs_evaluation') else "❌ No"
        )
        st.metric(
            "Formatting Needed",
            "✅ Yes" if plan.get('needs_formatting') else "❌ No"
        )
    
    with col3:
        st.metric("Est. Sources", plan.get('estimated_sources', 0))
        st.metric("Summary Depth", plan.get('summary_depth', 'brief'))
    
    # Show JSON
    with st.expander("View Plan JSON"):
        st.json(plan)


def display_search_results(result: dict):
    """Display search results"""
    if not result.get('search_results'):
        return
    
    st.header("🔍 Search Results")
    
    search_results = result['search_results']
    results = search_results.get('results', [])
    
    if not results:
        st.info("No search results found")
        return
    
    st.metric("Total URLs Found", len(results))
    
    # Display top results
    for i, result_item in enumerate(results[:5], 1):
        with st.expander(f"📄 Result {i}: {result_item.get('title', 'No title')[:60]}"):
            st.write(f"**Title:** {result_item.get('title', 'N/A')}")
            st.write(f"**URL:** {result_item.get('url', 'N/A')}")
            st.write(f"**Snippet:** {result_item.get('snippet', 'N/A')}")
    
    if len(results) > 5:
        st.info(f"... and {len(results) - 5} more results")


def display_evaluation_results(result: dict):
    """Display content evaluation"""
    if not result.get('evaluation_results'):
        return
    
    st.header("⭐ Content Evaluation")
    
    eval_results = result['evaluation_results']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        relevant = eval_results.get('relevant_count', 0)
        st.metric("✅ Relevant Content", relevant)
    
    with col2:
        filtered = eval_results.get('filtered_count', 0)
        st.metric("🔴 Filtered Out", filtered)
    
    with col3:
        avg_score = eval_results.get('avg_relevance', 0)
        st.metric("📊 Avg Relevance", f"{avg_score:.2f}")
    
    # Show recommendation
    recommendation = eval_results.get('recommendation', 'neutral')
    color = '#4caf50' if recommendation == 'keep' else '#ff9800' if recommendation == 'improve' else '#f44336'
    
    st.markdown(f"**Recommendation:** <span style='color:{color}'>{recommendation.upper()}</span>", 
                unsafe_allow_html=True)


def display_summary(result: dict):
    """Display generated summary"""
    summary = result.get('summary', '')
    
    if not summary:
        return
    
    st.header("📝 Summary")
    
    st.markdown(summary)
    
    # Show character count
    st.caption(f"📊 Length: {len(summary)} characters")


def display_formatted_output(result: dict):
    """Display formatted output"""
    if not result.get('formatted_output'):
        return
    
    st.header("💾 Formatted Output")
    
    formatted_output = result['formatted_output']
    formats = formatted_output.get('formats', {})
    
    if not formats:
        st.info("No formats generated")
        return
    
    cols = st.columns(len(formats))
    
    for col, (format_name, file_info) in zip(cols, formats.items()):
        with col:
            if file_info:
                st.markdown(f"### ✅ {format_name.upper()}")
                file_path = file_info.get('file_path', 'N/A')
                size = file_info.get('size', 0)
                
                st.write(f"**Path:** `{file_path}`")
                st.write(f"**Size:** {size:,} bytes")
    
    # Show files
    st.subheader("Generated Files")
    for format_name, file_info in formats.items():
        if file_info:
            file_path = file_info.get('file_path')
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    with st.expander(f"View {format_name.upper()} Content"):
                        if format_name.lower() == 'csv':
                            st.code(content, language='csv')
                        elif format_name.lower() == 'json':
                            st.json(json.loads(content))
                        elif format_name.lower() == 'markdown':
                            st.markdown(content)
                        else:
                            st.code(content)
                except Exception as e:
                    st.warning(f"Could not read {format_name}: {str(e)}")


def display_error_information(result: dict):
    """Display error information if present"""
    if result.get('status') in ['failed', 'partial_success']:
        error_msg = result.get('error_message', 'Unknown error')
        
        st.header("⚠️ Error Information")
        st.error(f"**Error:** {error_msg}")


def display_results(result: dict, show_graph: bool = False):
    """Display all results"""
    
    # Execution status
    display_execution_status(result)
    
    # Routing path
    display_routing_path(result)
    
    # Execution plan
    display_execution_plan(result)
    
    st.divider()
    
    # Search results
    display_search_results(result)
    
    st.divider()
    
    # Evaluation
    display_evaluation_results(result)
    
    st.divider()
    
    # Summary
    display_summary(result)
    
    st.divider()
    
    # Formatted output
    display_formatted_output(result)
    
    # Errors
    if result.get('status') in ['failed', 'partial_success']:
        st.divider()
        display_error_information(result)
    
    # Graph visualization
    if show_graph:
        st.divider()
        display_graph_visualization()


def display_sidebar_info():
    """Display sidebar information"""
    st.sidebar.header("ℹ️ About")
    
    st.sidebar.markdown("""
    **Multi-Agent Pipeline** is a production-grade system that:
    
    - 🎯 Plans query execution strategy
    - 🔍 Dynamically routes based on content
    - 🪄 Extracts relevant information
    - ⭐ Evaluates content quality
    - 📝 Generates summaries
    - 💾 Exports multiple formats
    
    **Key Features:**
    - Dynamic Routing (not sequential)
    - Decision-Making AI (Planner Agent)
    - Quality Filtering (Evaluator Agent)
    - Multi-Format Export (CSV, JSON, Markdown)
    - Production Ready (logging, retries, errors)
    """)
    
    st.sidebar.divider()
    
    st.sidebar.header("📚 Documentation")
    st.sidebar.markdown("""
    - [Quick Start](MULTI_AGENT_QUICKSTART.md)
    - [Full Guide](MULTI_AGENT_GUIDE.md)
    - [Examples](example_multi_agent.py)
    - [CLI Usage](multi_agent_cli.py)
    """)


def main():
    """Main application"""
    init_session_state()
    
    # Header
    display_header()
    
    # Sidebar
    display_sidebar_info()
    enable_eval, enable_format, show_graph = display_configuration()
    
    # Main content
    st.divider()
    
    # Query input
    query, process_button = display_query_input()
    
    # Process query
    if process_button and query:
        with st.spinner(f"🔄 Processing query: '{query}'..."):
            try:
                pipeline = MultiAgentPipeline(
                    enable_evaluation=enable_eval,
                    enable_formatting=enable_format
                )
                
                result = pipeline.run(query)
                st.session_state.result = result
                
                # Add to history
                st.session_state.query_history.append({
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'status': result.get('status')
                })
                
            except Exception as e:
                st.error(f"❌ Error processing query: {str(e)}")
                st.session_state.result = None
    
    # Display results
    if st.session_state.result:
        st.divider()
        display_results(st.session_state.result, show_graph=show_graph)
    
    # Query history
    if st.session_state.query_history:
        st.sidebar.divider()
        st.sidebar.header("📜 Query History")
        
        for i, hist_item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            status_icon = get_status_icon(hist_item['status'])
            st.sidebar.write(
                f"{i}. {status_icon} {hist_item['query'][:40]}"
            )


if __name__ == '__main__':
    main()
