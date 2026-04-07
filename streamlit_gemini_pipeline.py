import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
import base64
import csv
import tempfile
import os
from dotenv import load_dotenv
from advanced_scraper import create_improved_scraper

# Load environment variables
load_dotenv()

# Initialize Google Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize advanced scraper
scraper = create_improved_scraper()

def search_serper(query):
    """Search using Serper API"""
    api_key = os.getenv("SERPER_API_KEY", "5bb84fd903aa487920271c447d4b2ef245e1fa60")
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {"q": query}
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, json=data, timeout=10)
        results = response.json()
        urls = [result["link"] for result in results.get("organic", [])][:5]
        return urls
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []

def scrape_content(urls):
    """
    Scrape content from URLs using advanced scraper
    - Removes noise and ads
    - Extracts only article content
    - Cleans and validates quality
    - Selects best 1-2 sources
    """
    if not urls:
        return "No URLs provided"
    
    try:
        # Use advanced scraper to get best content
        combined_content, source_metrics = scraper.scrape_urls(urls, max_sources=2)
        
        if not combined_content.strip():
            return "❌ Could not extract meaningful content from URLs"
        
        # Show source quality info in expandable section
        with st.expander("📊 Content Quality Metrics"):
            for metric in source_metrics:
                if metric['is_valid']:
                    status = "✅ Valid"
                    score_color = "green"
                else:
                    status = "❌ Invalid"
                    score_color = "red"
                
                st.write(f"""
                **{metric['url'][:50]}...**
                - Status: {status}
                - Quality Score: {metric['quality_score']}/100
                - Content Length: {metric['length']} chars
                """)
        
        return combined_content
        
    except Exception as e:
        st.error(f"⚠ Scraping error: {str(e)[:100]}")
        return ""

def generate_summary(content):
    """
    Generate summary using Google Gemini API directly.
    
    Args:
        content: Text to summarize
        
    Returns:
        Summary as bullet points or error message
    """
    if not content or not content.strip():
        return "❌ No content to summarize."
    
    try:
        # Initialize model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Create prompt
        prompt = f"""Summarize this text in 5 key bullet points. Format as:
• Point 1
• Point 2
• Point 3
• Point 4
• Point 5

Text to summarize:
{content[:3000]}"""
        
        # Generate response
        response = model.generate_content(prompt, stream=False)
        
        if response.text:
            return response.text
        else:
            return "❌ No response from API"
            
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Summarization failed: {error_msg}")
        return f"Failed to generate summary: {error_msg}"
def generate_tts(summary_text):
    """Generate text-to-speech from summary"""
    if not GTTS_AVAILABLE:
        return None
    try:
        tts = gTTS(summary_text, lang='en')
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        return fp.name
    except Exception as e:
        return None

def create_csv(summary_text):
    """Create CSV file from summary"""
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline='', encoding="utf-8")
        writer = csv.writer(tmp)
        writer.writerow(["Summary"])
        for line in summary_text.split("\n"):
            if line.strip():
                writer.writerow([line])
        tmp.close()
        return tmp.name
    except Exception as e:
        st.error(f"❌ CSV creation failed: {e}")
        return None

# ============================================================================
# STREAMLIT UI
# ============================================================================
st.set_page_config(page_title="QuickGlance", page_icon="🔍", layout="wide")
st.title("🔍 QuickGlance: Agentic Browser Pipeline")
st.markdown("Search, scrape, and summarize any topic with AI-powered summaries")

# Input
query = st.text_input("📝 Enter your topic for summarization:", placeholder="e.g., 'latest AI developments'")

# Process button
if st.button("🚀 Search, Scrape, and Summarize", use_container_width=True):
    if query.strip() == "":
        st.warning("⚠️ Please enter a topic to proceed.")
    else:
        # Step 1: Search
        with st.spinner("🔍 Searching with Serper..."):
            urls = search_serper(query)
            if urls:
                st.success(f"✅ Found {len(urls)} URLs")
                with st.expander("View URLs"):
                    for i, url in enumerate(urls, 1):
                        st.write(f"{i}. {url}")
            else:
                st.error("❌ No URLs found")
                st.stop()

        # Step 2: Scrape
        with st.spinner("🪄 Scraping content from URLs..."):
            content = scrape_content(urls)
            st.success(f"✅ Retrieved {len(content)} characters")

        # Step 3: Summarize
        with st.spinner("⚡ Generating summary with Gemini..."):
            summary = generate_summary(content)
            
        # Display summary
        if summary and "❌" not in summary and "Failed" not in summary:
            st.success("✅ Summary Generated!")
            st.markdown("### 📋 Summary")
            st.write(summary)
            
            # Download options
            col1, col2 = st.columns(2)
            
            # Download CSV
            with col1:
                csv_path = create_csv(summary)
                if csv_path:
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            label="📄 Download as CSV",
                            data=f,
                            file_name="summary.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            
            # Download PDF
            with col2:
                try:
                    from pdf_generator import generate_summary_pdf
                    pdf_bytes = generate_summary_pdf(
                        summary,
                        title="QuickGlance Summary",
                        url=urls[0] if urls else None
                    )
                    st.download_button(
                        label="📕 Download as PDF",
                        data=pdf_bytes,
                        file_name="summary.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except ImportError:
                    st.info("ℹ️ PDF export not available (install: pip install reportlab gtts)")
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {str(e)[:100]}")
            
            
            # Generate audio (only if gtts available)
            if GTTS_AVAILABLE:
                try:
                    with st.spinner("🎙️ Generating audio..."):
                        audio_path = generate_tts(summary)
                        if audio_path:
                            audio_bytes = open(audio_path, "rb").read()
                            b64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f"""
                                <audio controls autoplay>
                                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                                    Your browser does not support the audio element.
                                </audio>
                            """
                            st.markdown("### 🎵 Audio Summary")
                            st.markdown(audio_html, unsafe_allow_html=True)
                            st.success("✅ Audio generated successfully")
                except Exception as e:
                    st.warning(f"⚠️ Audio generation skipped: {str(e)[:50]}")
        else:
            st.error("❌ Failed to generate summary")

# Footer
st.markdown("---")
st.markdown("Built with streamlit + Google Gemini API")