# 📋 Streamlit Enhanced App - Code Examples

## Quick Reference

### 1️⃣ Dark Theme Setup

```python
# Automatic - theme is built into the app!
# No additional setup needed.
# Just run: streamlit run streamlit_enhanced_app.py
```

**CSS Variables (can customize):**
```css
:root {
    --primary: #00D9FF;        /* Change accent color */
    --secondary: #6A0DAD;      /* Change secondary color */
    --bg-dark: #0F1419;        /* Change background */
    --success: #00FF9F;        /* Change success green */
    --error: #FF3366;          /* Change error red */
}
```

---

### 2️⃣ Progress Bar Code

```python
# Display 5-step progress
def display_progress_section(total_steps: int, current_step: int, step_name: str):
    progress = current_step / total_steps
    
    st.markdown(f"""
        <div style='margin: 20px 0;'>
            <div style='display: flex; justify-content: space-between;'>
                <p>📊 Progress</p>
                <p>{current_step}/{total_steps} - {step_name}</p>
            </div>
            <div style='width: 100%; height: 6px; background: var(--bg-secondary); 
                       border-radius: 3px; overflow: hidden;'>
                <div style='width: {progress * 100}%; height: 100%; 
                           background: linear-gradient(90deg, #00D9FF, #6A0DAD);'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Usage in main:
if process_button and query:
    display_progress_section(5, 1, "Analyzing query")
    display_progress_section(5, 2, "Searching the web")
    display_progress_section(5, 3, "Extracting content")
    display_progress_section(5, 4, "Evaluating quality")
    display_progress_section(5, 5, "Creating summary")
```

---

### 3️⃣ URL Preview Card Code

```python
def display_url_preview_card(url: str, title: str = None, snippet: str = None):
    """Create beautiful URL cards"""
    domain = get_domain_from_url(url)  # Extract domain
    
    st.markdown(f"""
        <div class='url-card'>
            <div style='display: flex; justify-content: space-between;'>
                <div style='flex: 1;'>
                    <p style='color: var(--primary); font-weight: 600;'>
                        🌐 {domain}
                    </p>
                    <p style='color: var(--text-primary); font-weight: 600;'>
                        {title}
                    </p>
                    <p style='color: var(--text-secondary);'>
                        {snippet}
                    </p>
                    <p style='color: var(--text-secondary); font-size: 0.8rem;'>
                        {url}
                    </p>
                </div>
                <a href='{url}' target='_blank' 
                   style='background: linear-gradient(135deg, #00D9FF, #6A0DAD);
                          color: white; border-radius: 6px; padding: 6px 12px;'>
                    Open ↗
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Usage:
for url_item in urls:
    display_url_preview_card(
        url=url_item['url'],
        title=url_item['title'],
        snippet=url_item['snippet']
    )
```

---

### 4️⃣ Expandable Summary Code

```python
def display_summary_section(result: dict):
    """Show expandable summary"""
    summary = result.get('summary', '')
    
    # Show first 200 chars as preview
    preview = summary[:200] + "..." if len(summary) > 200 else summary
    
    # Expandable section
    with st.expander("📝 Summary", expanded=True):
        st.markdown(summary)
        st.caption(f"📊 {len(summary)} characters | {len(summary.split(chr(10)))} paragraphs")

# Output:
# [▼ Summary]
#   Full summary text...
#   📊 Length stats
```

---

### 5️⃣ Audio Player Code

```python
def display_audio_player(result: dict):
    """Show modern audio player"""
    formatted_output = result.get('formatted_output', {})
    formats = formatted_output.get('formats', {})
    audio_format = formats.get('audio', {})
    audio_path = audio_format.get('file_path')
    
    if audio_path and Path(audio_path).exists():
        st.markdown("### 🎵 Audio Summary")
        
        # Create modern player container
        st.markdown("""
            <div style='background: linear-gradient(135deg, #1A1F2E 0%, #252D3D 100%); 
                       border-radius: 12px; padding: 16px;'>
                <p style='color: var(--text-secondary); font-size: 0.875rem;'>
                    🎧 Listen to the summary
                </p>
        """, unsafe_allow_html=True)
        
        # Native HTML5 audio player
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format='audio/mp3')
        
        st.markdown("</div>", unsafe_allow_html=True)

# Output:
# 🎵 Audio Summary
# 🎧 Listen to the summary
# [▶ ═══●═════] 00:45
```

---

### 6️⃣ Download Options Code

```python
def display_download_section(result: dict):
    """Show three download formats"""
    summary = result.get('summary', '')
    
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
    
    # Audio Download
    with col3:
        if result.get('formatted_output'):
            formats = result['formatted_output'].get('formats', {})
            audio_format = formats.get('audio', {})
            audio_path = audio_format.get('file_path')
            
            if audio_path and Path(audio_path).exists():
                with open(audio_path, 'rb') as f:
                    audio_bytes = f.read()
                
                st.download_button(
                    label="🎵 AUDIO",
                    data=audio_bytes,
                    file_name="summary.mp3",
                    mime="audio/mpeg",
                    use_container_width=True
                )

# Output:
# [📊 CSV] [📄 TEXT] [🎵 AUDIO]
```

---

### 7️⃣ Error Handling Code

```python
def display_error_section(result: dict):
    """Show professional error UI"""
    if result.get('status') not in ['failed', 'partial_success']:
        return
    
    st.markdown("### ⚠️ Issues Detected")
    
    error_msg = result.get('error_message', 'Unknown error')
    
    with st.expander("View Error Details", expanded=True):
        # Color-coded error box
        st.error(f"❌ {error_msg}")
        
        # Helpful suggestions
        st.markdown("""
            **🔧 Troubleshooting Tips:**
            - Check your internet connection
            - Try a different or more specific query
            - Wait a few moments and try again
            - Check the API quotas in your configuration
        """)

# Output:
# ⚠️ Issues Detected
# [❌ Network timeout]
# 🔧 Troubleshooting Tips:
#    • Check internet connection
#    • Try different query
#    etc.
```

---

### 8️⃣ Status Metrics Code

```python
def display_status_metrics(result: dict):
    """Show 4 key metrics"""
    status = result.get('status', 'unknown')
    icon = get_status_icon(status)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", f"{icon} {status.upper()}")
    
    with col2:
        agents_count = len(result.get('agent_history', []))
        st.metric("Agents Used", f"{agents_count} 🤖")
    
    with col3:
        url_count = len(result.get('search_results', {}).get('results', []))
        st.metric("URLs Found", f"{url_count} 🔗")
    
    with col4:
        timestamp = result.get('timestamp', 'N/A')
        st.metric("Date", timestamp[:10] if timestamp else 'N/A')

# Output:
# ┌──────────┬──────────┬──────────┬──────────┐
# │ Status   │ Agents   │ URLs     │ Date     │
# │ SUCCESS  │ 4 🤖     │ 8 🔗     │ 2026-04-07
# └──────────┴──────────┴──────────┴──────────┘
```

---

## 🎨 Helper Functions

### Extract Domain from URL
```python
def get_domain_from_url(url: str) -> str:
    """Extract domain: https://www.wikipedia.org → wikipedia.org"""
    try:
        return urlparse(url).netloc.replace('www.', '')
    except:
        return 'unknown'
```

### Create CSV Content
```python
def create_csv_content(summary_text: str) -> str:
    """Convert summary to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Item', 'Content'])
    
    lines = summary_text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            writer.writerow([f'Point {i}', line.strip()])
    
    return output.getvalue()
```

### Get Status Icon
```python
def get_status_icon(status: str) -> str:
    """Map status to emoji"""
    icons = {
        'success': '✅',
        'partial_success': '⚠️',
        'failed': '❌',
        'running': '⏳'
    }
    return icons.get(status, '❓')
```

---

## 🚀 Main Entry Point

```python
def main():
    """Main application flow"""
    
    # 1. Initialize
    init_session_state()
    
    # 2. Display header
    display_header()
    
    # 3. Sidebar configuration
    enable_eval, enable_format = display_sidebar()
    
    # 4. Query input
    query, process_button = display_query_input()
    
    # 5. Process if button clicked
    if process_button and query:
        try:
            # Progress tracking (5 steps)
            display_progress_section(5, 1, "Analyzing query")
            display_progress_section(5, 2, "Searching the web")
            display_progress_section(5, 3, "Extracting content")
            display_progress_section(5, 4, "Evaluating quality")
            display_progress_section(5, 5, "Creating summary")
            
            # Run pipeline
            pipeline = MultiAgentPipeline()
            result = pipeline.run(query)
            st.session_state.result = result
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # 6. Display results
    if st.session_state.result:
        display_status_metrics(st.session_state.result)
        display_urls_section(st.session_state.result)
        display_summary_section(st.session_state.result)
        display_audio_player(st.session_state.result)
        display_download_section(st.session_state.result)
        display_error_section(st.session_state.result)

if __name__ == '__main__':
    main()
```

---

## 📱 Responsive Layout Examples

### Desktop (Wide)
```
┌────────────────────────────────────┐
│  🚀 QuickGlance AI                 │
├────────────────────────────────────┤
│  [Search Query.....................] │
│  ┌─────────┬─────────┬─────────┐   │
│  │ Metric1 │ Metric2 │ Metric3 │   │
│  └─────────┴─────────┴─────────┘   │
│  [URL Card 1 ......................]  │
│  [URL Card 2 ......................]  │
│  [Summary section ................]  │
│  [Download CSV] [TXT] [Audio]     │
└────────────────────────────────────┘
```

### Mobile (Narrow)
```
┌──────────────────────┐
│ 🚀 QuickGlance      │
├──────────────────────┤
│ [Search Query...] │
│                  │
│ Metric1: Value  │
│ Metric2: Value  │
│ Metric3: Value  │
│                  │
│ [URL Card 1...]  │
│ [URL Card 2...]  │
│ [Summary...]     │
│ [Download Opt.] │
└──────────────────────┘
```

---

## 🎨 CSS Customization Examples

### Change Primary Color to Orange
```css
/* In CSS section */
:root {
    --primary: #FF9500;        /* Change from cyan to orange */
    --primary-dark: #FF7500;
}
```

### Change Theme to Light
```css
/* In CSS section */
:root {
    --bg-dark: #FFFFFF;        /* White background */
    --bg-secondary: #F5F5F5;   /* Light gray */
    --text-primary: #000000;   /* Black text */
}
```

### Make Buttons Larger
```css
.stButton > button {
    padding: 16px 32px;        /* Increase from 12px 24px */
    font-size: 1.1rem;         /* Increase font */
    height: 50px;              /* Set explicit height */
}
```

---

## ✅ Testing Checklist

- [ ] Run app: `streamlit run streamlit_enhanced_app.py`
- [ ] Check dark theme displays correctly
- [ ] Enter query and click search
- [ ] Watch 5-step progress bar
- [ ] View URL preview cards
- [ ] Expand summary
- [ ] Play audio
- [ ] Download CSV
- [ ] Download TXT
- [ ] Download Audio
- [ ] Trigger error to see error UI
- [ ] Check mobile responsiveness
- [ ] Check sidebar works
- [ ] Verify query history

---

## 🚀 Deployment Tips

### Streamlit Cloud Deployment
```bash
# 1. Push to GitHub
git add streamlit_enhanced_app.py
git commit -m "Add enhanced Streamlit UI"
git push

# 2. Deploy on Streamlit Cloud
# Visit: https://share.streamlit.io
# Connect GitHub repo
# Select streamlit_enhanced_app.py
# Deploy!
```

### Local Deployment
```bash
# Use Streamlit built-in server
streamlit run streamlit_enhanced_app.py

# Or specify port
streamlit run streamlit_enhanced_app.py --server.port 8080
```

---

**Ready to run! 🎉**
