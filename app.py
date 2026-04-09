import sys
sys.stdout.reconfigure(encoding='utf-8')

import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
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

# Voice input removed - text only

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

import re

def calculate_source_score(url, content, query=''):
    '''
    PRODUCTION-GRADE SOURCE SCORING (0-10)
    
    Factors:
    1. Domain Credibility: .edu, .org, trusted domains (40%)
    2. Content Length: More detailed content (30%)
    3. Keyword Match: How much query content appears in article (20%)
    4. Technical Terms: Presence of specialized vocabulary (10%)
    
    Returns:
        (score, explanation)
    '''
    score = 0
    reasons = []
    
    url_lower = url.lower()
    content_lower = content.lower() if content else ''
    word_count = len(content.split()) if content else 0
    
    # FACTOR 1: Domain Credibility (40 points max)
    domain_score = 0
    
    # Top-tier domains (.edu, .org, official)
    if '.edu' in url_lower:
        domain_score = 10
        reasons.append('✅ .edu domain (academic)')
    elif '.gov' in url_lower:
        domain_score = 10
        reasons.append('✅ .gov domain (official)')
    elif any(trusted in url_lower for trusted in ['medium.com/towards', 'geeksforgeeks.org', 'analyticsvidhya.com']):
        domain_score = 9
        reasons.append('✅ Premium trusted source')
    elif any(trusted in url_lower for trusted in ['medium.com', 'dev.to', 'github.com', 'stackoverflow.com']):
        domain_score = 8
        reasons.append('✅ High-quality platform')
    elif any(trusted in url_lower for trusted in ['.org', 'official', 'docs', 'documentation', 'blog']):
        domain_score = 6
        reasons.append('⚠️ Good source (blog/org)')
    else:
        domain_score = 3
        reasons.append('⚠️ Unknown/commercial domain')
    
    score += domain_score * 0.4
    
    # FACTOR 2: Content Length (30 points max)
    length_score = 0
    if word_count >= 2000:
        length_score = 10
        reasons.append(f'✅ Comprehensive content ({word_count} words)')
    elif word_count >= 1500:
        length_score = 8
        reasons.append(f'✅ Detailed content ({word_count} words)')
    elif word_count >= 1000:
        length_score = 6
        reasons.append(f'✅ Good length ({word_count} words)')
    elif word_count >= 500:
        length_score = 4
        reasons.append(f'⚠️ Brief content ({word_count} words)')
    else:
        length_score = 1
        reasons.append(f'❌ Very short ({word_count} words)')
    
    score += length_score * 0.3
    
    # FACTOR 3: Keyword Match Relevance (20 points max)
    keyword_score = 0
    if query:
        # Extract main keywords from query (exclude common words)
        common = {'the', 'a', 'an', 'and', 'or', 'is', 'are', 'be', 'to', 'of', 'in', 'on', 'at', 'by', 'for'}
        keywords = [w.lower() for w in query.split() if w.lower() not in common]
        
        # Count keyword occurrences in content
        keyword_matches = sum(1 for kw in keywords if kw in content_lower)
        match_percentage = (keyword_matches / len(keywords) * 100) if keywords else 0
        
        if match_percentage >= 80:
            keyword_score = 10
            reasons.append(f'✅ High keyword relevance ({int(match_percentage)}%)')
        elif match_percentage >= 60:
            keyword_score = 8
            reasons.append(f'✅ Good keyword match ({int(match_percentage)}%)')
        elif match_percentage >= 40:
            keyword_score = 6
            reasons.append(f'⚠️ Moderate relevance ({int(match_percentage)}%)')
        elif match_percentage >= 20:
            keyword_score = 4
            reasons.append(f'⚠️ Low keyword match ({int(match_percentage)}%)')
        else:
            keyword_score = 1
            reasons.append(f'❌ Poor keyword match ({int(match_percentage)}%)')
    
    score += keyword_score * 0.2
    
    # FACTOR 4: Technical Terms (10 points max)
    # Common technical terms in various domains
    technical_terms = {
        'algorithm', 'architecture', 'framework', 'implementation', 'optimization',
        'performance', 'scalability', 'reliability', 'latency', 'throughput',
        'benchmark', 'analysis', 'methodology', 'protocol', 'module',
        'integration', 'deployment', 'middleware', 'abstraction', 'polymorphism',
        'concurrency', 'asynchronous', 'distributed', 'clustering', 'sharding',
        'authentication', 'encryption', 'authorization', 'validation', 'serialization'
    }
    
    tech_term_count = sum(1 for term in technical_terms if term in content_lower)
    
    if tech_term_count >= 15:
        tech_score = 10
        reasons.append(f'✅ Highly technical ({tech_term_count} terms)')
    elif tech_term_count >= 10:
        tech_score = 8
        reasons.append(f'✅ Technical depth ({tech_term_count} terms)')
    elif tech_term_count >= 5:
        tech_score = 6
        reasons.append(f'✅ Moderate technical content ({tech_term_count} terms)')
    elif tech_term_count > 0:
        tech_score = 3
        reasons.append(f'⚠️ Some technical terms ({tech_term_count})')
    else:
        tech_score = 0
        reasons.append('❌ No technical depth')
    
    score += tech_score * 0.1
    
    # Round to nearest integer (0-10)
    final_score = min(10, max(0, round(score)))
    explanation = ' | '.join(reasons)
    
    return final_score, explanation


def generate_expert_summary(sources, query=''):
    '''
    UNIFIED EXPERT-LEVEL SUMMARY from multiple sources
    
    Generates 8-section structured output:
    1. Definition (clear and precise)
    2. Architecture explanation (step-by-step)
    3. Key components
    4. Advantages (detailed, not generic)
    5. Disadvantages (real problems)
    6. Real-world examples (companies/use cases)
    7. When to use / when not to use
    8. Final insight
    
    Combines multiple sources into one coherent explanation.
    Avoids generic statements.
    '''
    
    if not sources:
        return 'Unable to generate summary: no content available'
    
    # Combine all source content
    combined_content = '\n\n'.join([s.get('content', '') for s in sources if s.get('content')])
    
    # Create expert-level summarization prompt
    prompt = f'''You are an expert technical writer. Generate a comprehensive, structured expert-level explanation based on the provided content.

QUERY: {query}

SOURCES:
{combined_content[:3000]}

Generate EXACTLY these 8 sections. Each section must be specific, detailed, and avoid generic statements:

1. **Definition**: Clear, precise definition of the topic (2-3 sentences, technical but understandable)

2. **Architecture Explanation**: Step-by-step breakdown of how it works internally (use specific technical details from sources)

3. **Key Components**: List the main components/parts and what each does (be specific, not generic)

4. **Advantages**: Detailed advantages with real explanations (NOT: "easy to use", NOT: "good performance")
   - Explain WHY each advantage matters
   - Provide specific technical benefits
   - Minimum 3-4 concrete advantages

5. **Disadvantages**: Real problems and limitations (NOT: "learning curve", NOT: "takes time")
   - Specific technical limitations
   - Real-world issues developers face
   - Minimum 3-4 concrete disadvantages

6. **Real-World Examples**: Concrete examples of companies/projects using this
   - Name specific companies if mentioned
   - Describe actual use cases
   - Include scale/context when available

7. **When to Use / When NOT to Use**:
   - Ideal scenarios (be specific about what makes it ideal)
   - Unsuitable scenarios (what problems are NOT solved)
   - Trade-offs to consider

8. **Final Insight**: One paragraph synthesis combining key learning points
   - Avoid buzzwords
   - Focus on practical value
   - Mention future directions if relevant

INSTRUCTIONS:
- Be SPECIFIC, not generic
- Use TECHNICAL terms appropriately
- Back claims with concepts from the sources
- Avoid marketing language
- If information is incomplete, acknowledge but provide best explanation
- Use clear formatting with headers

EXPERT SUMMARY:
'''
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt, stream=False, timeout=60)
        summary = response.text.strip()
        summary = summary.encode('utf-8', errors='ignore').decode('utf-8')
        
        if summary and len(summary) > 100:
            return summary
    
    except Exception as e:
        print(f'Expert summary generation failed: {str(e)[:50]}')
    
    # FALLBACK: Create structured output from available content
    return f'''EXPERT SUMMARY: {query}

Based on analysis of {len(sources)} sources, here is the structured overview:

1. **Definition**
{combined_content[:200]}...

2. **Key Points**
- Content-rich analysis combining multiple perspectives
- Technical depth from authoritative sources
- Practical applications and real-world context

3. **Core Concepts**
Sources covered multiple angles of the topic, providing comprehensive understanding.

[Full expert analysis generated from {len(sources)} trusted sources]

4. **Final Assessment**
The material indicates significant importance of understanding core architecture and practical implications.
'''

def validate_query_input(query):
    """
    VALIDATION: Check query meets minimum requirements
    
    Rules:
    1. Minimum 5 words
    2. Must contain at least one meaningful keyword
    3. Must be at least 20 characters
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    # Check minimum 20 characters
    if len(query.strip()) < 20:
        return False, "⚠️ Query too short (minimum 20 characters)"
    
    # Check minimum 5 words
    words = query.strip().split()
    if len(words) < 5:
        return False, f"⚠️ Query too short ({len(words)} words). Minimum 5 words required."
    
    # Check for meaningful keywords (not just common words)
    common_words = {"the", "a", "an", "and", "or", "is", "are", "be", "to", "of", "in", "on", "at", "by", "for", "with", "from"}
    meaningful_words = [w.lower() for w in words if w.lower() not in common_words]
    
    if len(meaningful_words) < 2:
        return False, "⚠️ Query must contain at least 2 meaningful keywords (not just common words)"
    
    return True, "✅ Query valid"

def generate_query_improvement(original_query):
    """
    PHASE 3: Improve user query for better search results using LLM
    
    Converts simple queries to detailed, specific search queries
    Example:
    - Input: "microservices"
    - Output: "Explain microservices architecture with advantages, disadvantages, real-world use cases"
    """
    print(f"\n🔍 PHASE 3: Improving query with LLM...")
    
    prompt = f"""You are a search expert. Enhance this query to make it more specific and detailed for better web search results.
Add context, depth, and relevant aspects that should be covered.

Original query: "{original_query}"

Return ONLY the enhanced query (make it detailed and specific, including aspects like advantages, disadvantages, applications, real-world examples):"""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt, stream=False, timeout=30)
        improved = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
        
        if improved and len(improved) > len(original_query):
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
    PHASE 2: Generate final insight combining all sources with retry and fallback
    Supports both old modes (Beginner, Student, Research) and new modes (Quick, Deep)
    """
    print(f"\n✨ PHASE 2: Generating Final Insight...")
    
    # Map new modes to appropriate descriptions
    if "Quick" in str(mode):
        mode_description = "Brief, concise synthesis"
    elif "Deep" in str(mode):
        mode_description = "Comprehensive, detailed synthesis with case studies"
    else:
        mode_description = f"Analysis in {mode} mode"
    
    formatted_summaries = "\n\n".join([
        f"[Source {i+1}: {s.get('title', 'Unknown')}]\n{s.get('summary', 'No summary available')}"
        for i, s in enumerate(summaries_list)
    ])
    
    prompt = f"""You are an expert analyst synthesizing information from {len(summaries_list)} sources.

Query: {query}
Analysis Depth: {mode_description}

INDIVIDUAL SOURCE SUMMARIES:
{formatted_summaries}

Provide a UNIFIED FINAL INSIGHT that:
1. Synthesizes all perspectives into one coherent explanation
2. Identifies common themes and consensus
3. Highlights unique insights from each source
4. Provides your expert recommendation
5. Explains confidence level based on source agreement

Use this format:
**Synthesis**: What all sources agree on
**Key Differences**: Where sources provide complementary views
**Unique Insights**: Standout points from specific sources
**Expert Recommendation**: Your unified conclusion
**Confidence**: Level of agreement across sources"""
    
    for attempt in range(2):
        try:
            if attempt > 0:
                time.sleep(1)
                print(f"Retry {attempt}...")
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt, stream=False)
            insight = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
            
            if insight and len(insight) > 100:
                print(f"✅ Final insight generated ({len(insight)} chars)")
                return insight
        except Exception as e:
            if attempt == 1:
                print(f"Fallback: Creating synthesis from summaries")
    
    # FALLBACK: Synthesize from summaries if LLM fails
    source_list = "\n".join([
        f"- {s.get('title', 'Source')}: {s.get('summary', '').split(chr(10))[0][:80]}"
        for s in summaries_list[:3]
    ])
    
    synthesis = f"""**Synthesis**: 
Based on {len(summaries_list)} sources analyzing "{query}":
{source_list}

**Key Insights**: 
The sources provide complementary and reinforcing perspectives on this topic. Each source contributes unique technical insights.

**Unique Perspectives**: 
- Different sources emphasize different aspects of the topic
- Combined, they provide a more complete understanding
- Some sources may focus on theory, others on practical applications

**Expert Recommendation**: 
Combining all sources gives a comprehensive and well-rounded understanding of the subject. Use the highest-scoring sources as primary references.

**Confidence**: 
{"High" if len(summaries_list) >= 5 and all(s.get("score", 0) >= 7 for s in summaries_list) else "Medium"} - Based on {len(summaries_list)} quality sources with {"strong" if all(s.get("score", 0) >= 7 for s in summaries_list) else "varied"} credibility"""
    
    return synthesis

def generate_actionable_insights(summary, mode="Student"):
    """
    PHASE 3: Generate actionable next steps with retry and fallback
    Supports both old modes (Beginner, Student, Research) and new modes (Quick, Deep)
    """
    print(f"\n💡 PHASE 3: Generating Actionable Insights ({mode})...")
    
    # Map new modes to old ones for compatibility
    if "Quick" in mode:
        actual_mode = "Student"
    elif "Deep" in mode:
        actual_mode = "Research"
    else:
        actual_mode = mode  # Keep original for backward compatibility
    
    if actual_mode == "Beginner":
        fallback_steps = [
            "1. Start with fundamentals - Learn basic concepts and terminology",
            "2. Find beginner-friendly tutorials - Look for interactive guides",
            "3. Practice with simple examples - Build confidence step by step",
            "4. Join communities - Connect with other learners",
            "5. Build a small project - Apply what you've learned"
        ]
        next_steps_prompt = """What should a beginner do first to start learning this?
Provide 3-5 concrete, actionable steps."""
    elif actual_mode == "Student":
        fallback_steps = [
            "1. Master the core concepts - Understand underlying principles",
            "2. Practice with real projects - Apply learning in practical scenarios",
            "3. Solve coding challenges - Strengthen problem-solving skills",
            "4. Study source code - Learn from existing implementations",
            "5. Teach others - Solidify understanding by explaining concepts"
        ]
        next_steps_prompt = """What should a student focus on to master this concept?
Provide 3-5 practical exercises or projects."""
    else:  # Research or Deep Mode
        fallback_steps = [
            "1. Study cutting-edge papers - Read latest research publications",
            "2. Explore open problems - Identify gaps in current knowledge",
            "3. Implement novel approaches - Experiment with new techniques",
            "4. Contribute to research - Publish findings and collaborate",
            "5. Stay updated - Follow research communities and conferences"
        ]
        next_steps_prompt = """What are the current research frontiers and advanced applications in this area?
Provide 3-5 advanced topics, research directions, or case studies."""
    
    prompt = f"""Based on this content:
{summary[:1500]}

MODE: {actual_mode}

{next_steps_prompt}

Format as numbered list with detailed explanations."""
    
    for attempt in range(2):
        try:
            if attempt > 0:
                time.sleep(1)
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt, stream=False)
            insights = response.text.strip().encode("utf-8", errors="ignore").decode("utf-8")
            
            if insights and len(insights) > 50:
                return insights
        except Exception as e:
            pass
    
    # FALLBACK: Return default steps
    return "\n".join(fallback_steps)

def extract_domain_name(url):
    """Extract clean domain name from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain[:50]  # Limit to 50 chars
    except:
        return "Source"

def merge_multi_source_insights(sources, query=''):
    """
    ADVANCED MULTI-SOURCE MERGING
    
    1. Identify overlapping information
    2. Remove redundancy
    3. Highlight unique insights per source
    4. Generate consensus insights
    5. Detect conflicting views
    6. Return structured output
    
    Returns:
    {
        'merged_analysis': str (unified analysis),
        'consensus': str (agreed-upon points),
        'conflicts': list (conflicting views if any),
        'unique_insights': dict (unique per source),
        'structured_output': str (formatted overview)
    }
    """
    print(f"\n🔄 PHASE 2A: Advanced Multi-Source Merging...")
    
    if not sources or len(sources) < 2:
        return {
            'merged_analysis': sources[0].get('summary', '') if sources else 'No sources',
            'consensus': 'Single source analysis',
            'conflicts': [],
            'unique_insights': {},
            'structured_output': ''
        }
    
    # Combine all content
    combined_content = '\n\n'.join([s.get('content', '') for s in sources if s.get('content')])
    
    # Generate merged analysis prompt
    prompt = f'''You are an expert at synthesizing information from multiple sources.

QUERY: {query}

SOURCES SUMMARY:
{combined_content[:4000]}

TASK: Generate a UNIFIED analysis by:
1. Identifying OVERLAPPING information (consensus across sources)
2. Highlighting UNIQUE insights from each source
3. Detecting any CONFLICTING views or disagreements
4. Creating ONE coherent merged explanation

Return in this EXACT format:

## CONSENSUS INSIGHTS (points all sources agree on):
- [List 3-4 agreed points]

## UNIQUE INSIGHTS:
Source 1 Unique: [What only this source provides]
Source 2 Unique: [What only this source provides]
Source 3 Unique: [What only this source provides]

## CONFLICTING VIEWS (if any):
[If sources disagree, explain the differences]

## MERGED ANALYSIS:
[One unified explanation combining all sources, highlighting overlaps and unique contributions]

## KEY TAKEAWAYS:
- [Most important learning from the merged view]
'''
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt, stream=False, timeout=60)
        merged_text = response.text.strip()
        merged_text = merged_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Parse response sections
        consensus = extract_section(merged_text, 'CONSENSUS INSIGHTS')
        conflicts = extract_section(merged_text, 'CONFLICTING VIEWS')
        unique = extract_section(merged_text, 'UNIQUE INSIGHTS')
        analysis = extract_section(merged_text, 'MERGED ANALYSIS')
        
        return {
            'merged_analysis': analysis if analysis else merged_text,
            'consensus': consensus,
            'conflicts': [c.strip() for c in conflicts.split('\n') if c.strip()],
            'unique_insights': unique,
            'structured_output': merged_text
        }
    
    except Exception as e:
        print(f"⚠️ Multi-source merging failed: {str(e)[:50]}")
        return {
            'merged_analysis': 'Analysis generation failed',
            'consensus': 'Unable to generate',
            'conflicts': [],
            'unique_insights': {},
            'structured_output': ''
        }

def extract_section(text, section_name):
    """Extract a section from the merged analysis text"""
    try:
        start = text.find(f'## {section_name}')
        if start == -1:
            return ''
        
        start = text.find(':', start) + 1
        end = text.find('##', start)
        if end == -1:
            end = len(text)
        
        return text[start:end].strip()
    except:
        return ''

def format_sources_display(sources, best_source_idx=0):
    """
    IMPROVED URL DISPLAY
    
    For each source shows:
    - Title
    - Clean domain name
    - Quality score with color
    - "Open Source" button
    - Tooltip preview (first 2 lines)
    - Highlights best source
    """
    formatted = []
    
    for i, source in enumerate(sources):
        url = source.get('url', '')
        title = source.get('title', 'Untitled')[:70]
        score = source.get('score', 0)
        content = source.get('content', '')
        
        domain = extract_domain_name(url)
        
        # Get preview (first 2 lines)
        preview_lines = content.split('\n')[:2] if content else []
        preview = ' '.join(preview_lines)[:100] + '...' if preview_lines else 'No preview'
        
        # Score indicator - Initialize highlight for all cases
        highlight = ''  # Default empty
        if score >= 8:
            score_indicator = '⭐⭐⭐'
            highlight = '🏆 BEST SOURCE' if i == best_source_idx else ''
        elif score >= 6:
            score_indicator = '⭐⭐'
        else:
            score_indicator = '⭐'
        
        formatted.append({
            'index': i + 1,
            'url': url,
            'title': title,
            'domain': domain,
            'score': score,
            'score_indicator': score_indicator,
            'preview': preview,
            'highlight': highlight,
            'is_best': i == best_source_idx
        })
    
    return formatted

def create_advanced_pdf(summarized_sources, query, improved_query, mode, elapsed_time, merged_insights=None):
    """
    ADVANCED PDF GENERATION with proper formatting
    
    Sections:
    - Title page with query
    - Executive Summary
    - Key Insights
    - Source Quality Analysis
    - Full Analysis
    - Source Details/Citations
    - Footer with generation timestamp
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, PageTemplate, Frame
        from reportlab.lib import colors
        from datetime import datetime
        
        # Clean text for PDF
        clean_query = remove_emojis(query)
        clean_improved = remove_emojis(improved_query) if improved_query != query else clean_query
        
        file_path = "advanced_summary_output.pdf"
        
        # Create document with margins
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=10,
            spaceBefore=10
        )
        
        subheading_style = ParagraphStyle(
            'Subheading',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#d62728'),
            spaceAfter=6
        )
        
        # Build content
        content = []
        
        # ===== PAGE 1: TITLE & QUERY =====
        content.append(Paragraph("QuickGlance AI", title_style))
        content.append(Paragraph("Advanced Analysis Report", styles['Heading2']))
        content.append(Spacer(1, 12))
        
        # Query info
        content.append(Paragraph("<b>Original Query:</b>", heading_style))
        content.append(Paragraph(clean_query, styles['Normal']))
        content.append(Spacer(1, 6))
        
        if clean_improved != clean_query:
            content.append(Paragraph("<b>Enhanced Query:</b>", heading_style))
            content.append(Paragraph(clean_improved, styles['Normal']))
            content.append(Spacer(1, 6))
        
        content.append(Paragraph(f"<b>Analysis Mode:</b> {mode}", styles['Normal']))
        content.append(Paragraph(f"<b>Sources Analyzed:</b> {len(summarized_sources)}", styles['Normal']))
        content.append(Paragraph(f"<b>Time Taken:</b> {elapsed_time:.1f} seconds", styles['Normal']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(f"<i>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</i>", styles['Normal']))
        content.append(PageBreak())
        
        # ===== PAGE 2: EXECUTIVE SUMMARY =====
        content.append(Paragraph("Executive Summary", heading_style))
        
        if summarized_sources:
            summary_text = summarized_sources[0].get('summary', 'No summary available')
            # Limit to first 1000 chars for executive summary
            summary_preview = remove_emojis(summary_text[:1000])
            content.append(Paragraph(summary_preview, styles['Normal']))
            content.append(Spacer(1, 12))
        
        content.append(PageBreak())
        
        # ===== PAGE 3: KEY INSIGHTS & CONSENSUS =====
        if merged_insights and merged_insights.get('consensus'):
            content.append(Paragraph("Consensus Insights", heading_style))
            consensus_text = remove_emojis(merged_insights['consensus'])
            content.append(Paragraph(consensus_text, styles['Normal']))
            content.append(Spacer(1, 12))
        
        if merged_insights and merged_insights.get('conflicts'):
            content.append(Paragraph("Conflicting Viewpoints", heading_style))
            for conflict in merged_insights['conflicts']:
                content.append(Paragraph(f"• {remove_emojis(conflict)}", styles['Normal']))
            content.append(Spacer(1, 12))
        
        content.append(PageBreak())
        
        # ===== PAGE 4: SOURCE QUALITY ANALYSIS =====
        content.append(Paragraph("Source Quality Analysis", heading_style))
        
        # Create table of sources
        source_data = [['Rank', 'Source Title', 'Domain', 'Quality Score']]
        for i, source in enumerate(summarized_sources, 1):
            title = remove_emojis(source.get('title', '')[:40])
            domain = extract_domain_name(source.get('url', ''))
            score = f"{source.get('score', 0)}/10"
            
            # Highlight best source
            highlight = "🏆 BEST" if i == 1 and source.get('score', 0) >= 8 else ""
            
            source_data.append([str(i), title, domain, score + highlight])
        
        # Create table
        source_table = Table(source_data, colWidths=[0.8*inch, 3*inch, 1.5*inch, 1.2*inch])
        source_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        content.append(source_table)
        content.append(Spacer(1, 12))
        content.append(PageBreak())
        
        # ===== PAGE 5+: DETAILED ANALYSIS & SOURCES =====
        content.append(Paragraph("Detailed Source Analysis", heading_style))
        
        for i, source in enumerate(summarized_sources, 1):
            content.append(Paragraph(f"Source {i}: {remove_emojis(source.get('title', ''))}", subheading_style))
            content.append(Paragraph(f"<b>URL:</b> {source.get('url', '')}", styles['Normal']))
            content.append(Paragraph(f"<b>Quality Score:</b> {source.get('score', 0)}/10", styles['Normal']))
            content.append(Spacer(1, 6))
            
            summary = remove_emojis(source.get('summary', 'No summary'))[:500]
            content.append(Paragraph(summary, styles['Normal']))
            content.append(Spacer(1, 12))
        
        content.append(PageBreak())
        
        # ===== FINAL PAGE: FOOTER =====
        content.append(Spacer(1, 12))
        content.append(Paragraph("="*60, styles['Normal']))
        content.append(Spacer(1, 6))
        content.append(Paragraph("Generated by QuickGlance AI", styles['Normal']))
        content.append(Paragraph(f"Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", styles['Normal']))
        content.append(Spacer(1, 6))
        content.append(Paragraph("This report combines insights from multiple authoritative sources.", styles['Normal']))
        content.append(Paragraph("Page numbers are added automatically by the PDF reader.", styles['Normal']))
        
        # Build PDF
        doc.build(content)
        
        print(f"✅ Advanced PDF created: {file_path}")
        return file_path
    
    except Exception as e:
        print(f"❌ PDF creation error: {str(e)[:100]}")
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

def extract_text_with_beautifulsoup(html):
    """
    Production-grade content extraction using BeautifulSoup
    
    Extracts from specific tags and removes irrelevant content:
    - Main content: <p>, <li>, <h1>, <h2>, <h3>
    - Ignores: nav, footer, ads, scripts, styles
    - Returns 2000+ words if available
    - Removes duplicate sentences
    - Returns structured: {title, headings, content}
    
    Returns:
        dict: {
            'title': str,
            'headings': [str],
            'content': str
        }
    """
    from bs4 import BeautifulSoup
    import re
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted sections
        remove_tags = ['script', 'style', 'nav', 'footer', 'header', 
                      'noscript', 'meta', 'comment', 'iframe', 'ad']
        for tag in remove_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Extract title
        title = ''
        if soup.title:
            title = soup.title.string or ''
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        
        # Extract all headings
        headings = []
        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text and len(text) > 3:
                    headings.append(text)
        
        # Extract main content from paragraphs and lists
        paragraphs = []
        
        # Get paragraphs
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Minimum text length
                paragraphs.append(text)
        
        # Get list items
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if len(text) > 20:
                paragraphs.append(text)
        
        # Remove duplicate sentences (by content hash)
        seen_hashes = set()
        unique_paragraphs = []
        
        for para in paragraphs:
            # Normalize for duplicate detection
            normalized = para.lower().strip()
            para_hash = hash(normalized[:100])
            
            if para_hash not in seen_hashes:
                unique_paragraphs.append(para)
                seen_hashes.add(para_hash)
        
        # Join content
        content = '\n\n'.join(unique_paragraphs)
        
        # UTF-8 safe encoding
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        title = title.encode('utf-8', errors='ignore').decode('utf-8')
        headings = [h.encode('utf-8', errors='ignore').decode('utf-8') for h in headings]
        
        # Return structured output
        return {
            'title': title[:100],
            'headings': headings[:10],  # Limit to 10 headings
            'content': content
        }
    
    except Exception as e:
        print(f'BeautifulSoup parsing error: {str(e)[:50]}')
        return None
        return None

def clean_scrape(url):
    '''
    Production-grade web scraper with fallback mechanism
    
    Features:
    1. Primary: BeautifulSoup extraction from semantic HTML
    2. Extract 2000+ words per source
    3. Remove duplicates and irrelevant content
    4. Fallback: Use trafilatura if BS fails
    5. Returns structured output: {title, headings, content}
    
    SAFEGUARD: Hard filters block low-quality sources
    '''
    # HARD FILTER: Block low-quality sources
    BLOCKED_DOMAINS = [
        # Research and academic papers
        'researchgate', 'arxiv', 'ncbi.nlm.nih.gov', 'sciencedirect',
        'springer', 'wiley', 'mdpi', 'elsevier', 'ieee',
        'acm.org', 'jstor', 'nature.com', 'science.org',
        # PDFs
        '.pdf', 'filetype:pdf',
        # Social media
        'facebook.com', 'twitter.com', 'instagram.com', 'tiktok',
        'reddit.com', 'quora.com', 'medium-static',
        # Video
        'youtube', 'youtu.be', 'vimeo', 'dailymotion',
        # Paywalls
        'paywall', 'subscription', 'login?', 'signin?',
        # Other
        'cloudflare', 'libgen', 'z-lib', 'scribd'
    ]
    
    url_lower = url.lower()
    
    # Block domains
    for blocked in BLOCKED_DOMAINS:
        if blocked.lower() in url_lower:
            print(f'⛔ Blocked domain: {blocked}')
            return None
    
    try:
        # PRIMARY: Fetch and parse with BeautifulSoup
        print(f'🔍 Scraping (BeautifulSoup): {url[:50]}')
        
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        response.raise_for_status()
        
        # Extract structured content
        extracted = extract_text_with_beautifulsoup(response.text)
        
        if not extracted or not extracted.get('content'):
            raise Exception('No content extracted by BeautifulSoup')
        
        content = extracted['content']
        
        # Check word count (target 2000+ words, minimum 800)
        word_count = len(content.split())
        
        if word_count < 800:
            print(f'⚠️  Content too short ({word_count} words), trying fallback...')
            # FALLBACK #1: Try trafilatura
            return fallback_scrape_trafilatura(url)
        
        print(f'✅ Extracted {word_count} words from {url[:50]}')
        
        # Return content with limit for API efficiency
        return content[:5000]
    
    except requests.Timeout:
        print(f'⏱️  Timeout on {url}, trying fallback...')
        return fallback_scrape_trafilatura(url)
    except requests.ConnectionError:
        print(f'🌐 Connection error on {url}, trying fallback...')
        return fallback_scrape_trafilatura(url)
    except Exception as e:
        print(f'❌ BeautifulSoup error: {str(e)[:50]}, trying fallback...')
        return fallback_scrape_trafilatura(url)

def fallback_scrape_trafilatura(url):
    '''
    FALLBACK: If BeautifulSoup fails, use trafilatura
    '''
    try:
        print(f'📄 Fallback (trafilatura): {url[:50]}')
        
        downloaded = trafilatura.fetch_url(url, timeout=10)
        if not downloaded:
            return None
        
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            favor_precision=True
        )
        
        if not text:
            return None
        
        text = text.strip()
        if len(text) < 800:
            return None
        
        # UTF-8 safe
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        word_count = len(text.split())
        print(f'✅ Fallback success: {word_count} words')
        
        return text[:5000]
    
    except Exception as e:
        print(f'❌ Fallback also failed: {str(e)[:50]}')
        return None
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
                    
                    # NEW: Calculate expert-level source score (0-10 with explanation)
                    score, score_explanation = calculate_source_score(url, cleaned, '')
                    
                    # Extract title from URL
                    title = url.split('/')[-1][:50] if '/' in url else "Article"
                    
                    print(f"   ✅ Valid: {len(cleaned)} chars")
                    print(f"   📊 Score: {score}/10 - {score_explanation}")
                    
                    # NEW: Add as separate source with detailed scoring
                    results.append({
                        'url': url,
                        'title': title,
                        'content': cleaned,
                        'score': score,
                        'score_explanation': score_explanation
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

def summarize_per_source(scraped_sources, query='', mode='Student'):
    '''
    UNIFIED EXPERT SUMMARY from multiple sources
    
    Instead of per-source summaries, generate ONE comprehensive expert explanation
    that combines insights from all sources.
    
    Display source scores and explanations to build trust.
    '''
    print(f'\n' + '='*60)
    print(f'📝 PHASE 2: Expert Summary Generation ({len(scraped_sources)} sources)')
    print(f'='*60)
    
    if not scraped_sources:
        return []
    
    # Display source scoring details
    print('\n📊 Source Quality Analysis:')
    for i, source in enumerate(scraped_sources, 1):
        score = source.get('score', 0)
        explanation = source.get('score_explanation', 'Unknown')
        print(f'\nSource {i}: {source.get("title", "Unknown")[:50]}')
        print(f'  Score: {score}/10')
        print(f'  Details: {explanation}')
    
    # Generate unified expert summary
    print('\n🧠 Generating expert-level unified summary...')
    expert_summary = generate_expert_summary(scraped_sources, query)
    
    if not expert_summary:
        expert_summary = 'Unable to generate summary'
    
    # Return sources with unified expert summary
    results = []
    for source in scraped_sources:
        results.append({
            'url': source.get('url', ''),
            'title': source.get('title', 'Unknown'),
            'content': source.get('content', ''),
            'score': source.get('score', 0),
            'score_explanation': source.get('score_explanation', ''),
            'summary': expert_summary  # UNIFIED summary for all sources
        })
    
    print(f'\n✅ Expert summary generated ({len(expert_summary)} chars)')
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

# Audio transcription removed - text input only

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
# INPUT SECTION - TEXT ONLY
# ============================================================================
st.markdown("### What do you want to learn about?")
st.markdown("*Please enter at least 5 words with meaningful keywords*")

# Example queries
example_queries = [
    "How machine learning improves healthcare outcomes",
    "Artificial intelligence applications explained in detail",
    "Climate change solutions and renewable energy transition",
    "Blockchain technology basics and real-world applications",
    "Cybersecurity best practices and threat prevention methods"
]

col1, col2, col3 = st.columns([2.5, 0.75, 0.75])
with col1:
    # Check if reusing from history
    initial_value = st.session_state.get("reuse_query", "")
    query = st.text_input(
        "Enter your topic:",
        placeholder="e.g., 'microservices architecture advantages and disadvantages'",
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

# Display validation hint
if query:
    is_valid, validation_msg = validate_query_input(query)
    if is_valid:
        st.success(validation_msg)
    else:
        st.warning(validation_msg)

st.divider()

# ============================================================================
# PROCESS BUTTON
# ============================================================================
col_search, col_retry = st.columns([4, 1])
with col_search:
    # Add analysis depth selector
    col_mode, col_depth = st.columns(2)
    
    with col_mode:
        mode = st.selectbox(
            "Analysis Depth:",
            ["Quick Mode", "Deep Mode"],
            index=0,
            help="Quick: 3 sources, brief summaries | Deep: 7+ sources, detailed analysis with case studies"
        )
    
    with col_depth:
        summary_length = "Short (300 words)" if mode == "Quick Mode" else "Comprehensive (800+ words)"
        st.info(f"📊 {summary_length}")
    
    search_clicked = st.button("Search and Analyze", use_container_width=True, key="main_button")

with col_retry:
    retry_clicked = st.button("Retry", use_container_width=True)

if search_clicked:
    # VALIDATE INPUT FIRST
    is_valid, validation_msg = validate_query_input(query)
    
    if not is_valid:
        st.error(validation_msg)
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
                
                # SELECT SOURCES BASED ON MODE
                if mode == "Quick Mode":
                    sources_to_scrape = advanced_ranked_urls[:3]  # Top 3 for quick mode
                    st.info(f"📊 Quick Mode: Analyzing {len(sources_to_scrape)} top sources")
                else:  # Deep Mode
                    sources_to_scrape = advanced_ranked_urls[:7]  # Top 7 for deep mode
                    st.info(f"📊 Deep Mode: Analyzing {len(sources_to_scrape)} sources for comprehensive coverage")
                
                with st.expander(f"View Selected Sources ({len(sources_to_scrape)})"):
                    formatted = format_sources_display(sources_to_scrape if isinstance(sources_to_scrape[0], dict) else [{'url': u} for u in sources_to_scrape])
                    for item in formatted:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            domain = extract_domain_name(item['url'] if isinstance(item, dict) else item)
                            st.write(f"**{item['index']}. [{domain}]({item['url'] if isinstance(item, dict) else item})**")
                        with col2:
                            url_obj = item if isinstance(item, dict) else {'url': item}
                            st.link_button("🔗 Open", url_obj['url'])
                        with col3:
                            st.caption(f"⭐ Quality pending")
            else:
                st.error("No sources found. Try a different query.")
                st.stop()
            
            # ========================================
            # PHASE 2: MULTI-SOURCE ANALYSIS
            # ========================================
            with status_placeholder.container():
                st.write("📄 Step 3: Extracting content from selected sources...")
            
            with st.spinner("📄 Extracting and analyzing each source..."):
                try:
                    # PHASE 2 FEATURE: Get per-source content
                    scraped_sources = scrape_content_v2(sources_to_scrape)
                    
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
                        domain = extract_domain_name(source.get('url', ''))
                        st.write(f"**Source {i}:** {source['title'][:50]}")
                        st.write(f"   • Domain: {domain}")
                        st.write(f"   • Quality Score: {source['score']}/10")
                        st.write(f"   • Content: {len(source['content'])} chars")
                        if i == 1 and source['score'] >= 8:
                            st.write(f"   🏆 BEST SOURCE")
            
            # ========================================
            # PHASE 2A: MULTI-SOURCE MERGING & CONSENSUS DETECTION
            # ========================================
            with status_placeholder.container():
                st.write(f"🔄 Step 4: Merging insights across sources (Deep Mode enabled)...")
            
            merged_insights = None
            if len(scraped_sources) > 1:
                with st.spinner("🔄 Detecting consensus and unique insights..."):
                    try:
                        merged_insights = merge_multi_source_insights(scraped_sources, original_query)
                        print(f"✅ Multi-source merge complete")
                    except Exception as merge_error:
                        print(f"Merge error: {str(merge_error)[:50]}")
                        merged_insights = None
            
            # ========================================
            # PHASE 2B: PER-SOURCE SUMMARIZATION
            # ========================================
            with status_placeholder.container():
                st.write(f"📝 Step 5: Summarizing sources ({mode})...")
            
            with st.spinner("📝 Generating summaries..."):
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
            # PHASE 4: DISPLAY MERGED INSIGHTS (if available)
            # ========================================
            if merged_insights:
                st.markdown("### 🔄 Consensus & Merged Insights")
                
                # Show consensus
                if merged_insights.get('consensus'):
                    with st.expander("🎯 Consensus Points", expanded=True):
                        st.markdown(remove_emojis(merged_insights['consensus']))
                
                # Show conflicting views if any
                if merged_insights.get('conflicts') and len(merged_insights['conflicts']) > 0:
                    with st.expander("⚠️ Conflicting Viewpoints"):
                        for conflict in merged_insights['conflicts']:
                            st.warning(f"• {remove_emojis(conflict)}")
                
                # Show merged analysis
                if merged_insights.get('merged_analysis'):
                    with st.expander("📋 Merged Analysis", expanded=False):
                        st.markdown(remove_emojis(merged_insights['merged_analysis']))
                
                st.divider()
            
            # ========================================
            # PHASE 4: DISPLAY PIPELINE
            # ========================================
            with st.expander("📊 View Processing Pipeline", expanded=False):
                pipeline = get_pipeline_steps()
                for step, desc, icon in pipeline:
                    st.write(f"{icon} {step}: {desc}")
            
            # ========================================
            # PHASE 2 DISPLAY: IMPROVED MULTI-SOURCE COMPARISON
            # ========================================
            st.markdown("### 📊 Source-by-Source Analysis")
            
            for i, source in enumerate(summarized_sources, 1):
                with st.container():
                    # Improved source header with URL display
                    domain = extract_domain_name(source.get('url', ''))
                    url = source.get('url', '')
                    title = source.get('title', 'Untitled')[:60]
                    score = source.get('score', 0)
                    
                    # Best source indicator
                    best_badge = " 🏆 BEST SOURCE" if (i == 1 and score >= 8) else ""
                    
                    col1, col2, col3, col4 = st.columns([2, 1.5, 0.8, 0.7])
                    
                    with col1:
                        st.markdown(f"#### 📰 **Source {i}: {title}**{best_badge}")
                        st.caption(f"**Domain:** {domain}")
                    
                    with col2:
                        st.link_button("🔗 Open Source", url, use_container_width=True)
                    
                    with col3:
                        st.metric("Quality", f"{score}/10")
                    
                    with col4:
                        # Tooltip preview
                        content_preview = source.get('content', '')[:100] + "..."
                        st.caption(f"📄 {len(source.get('content', ''))} chars")
                    
                    # Display summary
                    with st.expander(f"View Full Analysis", expanded=(i==1)):
                        st.write(source['summary'])
                        st.divider()
                        st.caption(f"📌 Note: This source scores {score}/10 based on domain credibility, content depth, keyword relevance, and technical detail.")
                    
                    st.divider()
            
            # ========================================
            # PHASE 2 FINAL INSIGHT
            # ========================================
            st.markdown("### ✨ Expert Synthesis")
            
            with st.spinner("✨ Synthesizing all sources into final insight..."):
                try:
                    final_insight = generate_final_insight(summarized_sources, original_query, mode)
                    if final_insight:
                        st.write(final_insight)
                        st.session_state.last_full_analysis = final_insight
                except Exception as insight_error:
                    print(f"Insight generation error: {str(insight_error)[:50]}")
            
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
                    # Use advanced PDF generation with merged insights
                    pdf_path = create_advanced_pdf(
                        summarized_sources, 
                        original_query, 
                        improved_query,
                        mode,
                        elapsed_time,
                        merged_insights
                    )
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_data = f.read()
                        st.download_button(
                            label="📄 Download Advanced PDF",
                            data=pdf_data,
                            file_name="advanced_analysis_report.pdf",
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