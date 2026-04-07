"""
Evaluation Metrics - Calculate quality scores for summarization
Measures: Relevance, Coverage, Redundancy, Quality
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
import math

# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep basic structure
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text"""
    # Split on periods, question marks, exclamation marks
    sentences = re.split(r'[.!?]+', text)
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def extract_key_phrases(text: str, num_phrases: int = 10) -> List[str]:
    """Extract key phrases (n-grams) from text"""
    words = normalize_text(text).split()
    
    # 2-grams and 3-grams
    phrases = []
    
    # 2-grams
    for i in range(len(words) - 1):
        phrases.append(f"{words[i]} {words[i+1]}")
    
    # 3-grams
    for i in range(len(words) - 2):
        phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    
    # Count and get top phrases
    phrase_counts = Counter(phrases)
    top_phrases = [phrase for phrase, _ in phrase_counts.most_common(num_phrases)]
    
    return top_phrases

# ============================================================================
# RELEVANCE SCORING (0-1)
# ============================================================================

def calculate_relevance_score(source_content: str, summary: str) -> float:
    """
    Calculate relevance score (0-1).
    How well does summary represent the source content?
    
    Uses:
    - Keyword overlap
    - N-gram similarity
    - TF-IDF inspired weighting
    
    Args:
        source_content: Original web content
        summary: Generated summary
        
    Returns:
        Score from 0 to 1 (1 = highly relevant)
    """
    
    if not source_content or not summary:
        return 0.0
    
    # Normalize texts
    source_norm = normalize_text(source_content)
    summary_norm = normalize_text(summary)
    
    # Extract words
    source_words = set(source_norm.split())
    summary_words = set(summary_norm.split())
    
    # Word overlap
    if len(source_words) == 0:
        return 0.0
    
    word_overlap = len(source_words & summary_words) / len(source_words)
    
    # Extract key phrases
    source_phrases = set(extract_key_phrases(source_content, 20))
    summary_phrases = set(extract_key_phrases(summary, 20))
    
    # Phrase overlap
    phrase_overlap = 0.0
    if source_phrases:
        phrase_overlap = len(source_phrases & summary_phrases) / len(source_phrases)
    
    # Check if key topics are mentioned
    sentences = extract_sentences(source_content)
    source_topics = [normalize_text(s)[:50] for s in sentences[:5]]  # First 5 topics
    
    topic_coverage = 0.0
    if source_topics:
        matched_topics = sum(
            1 for topic in source_topics
            if any(word in summary_norm for word in topic.split())
        )
        topic_coverage = matched_topics / len(source_topics)
    
    # Weighted combination
    relevance_score = (
        word_overlap * 0.3 +  # 30% word overlap
        phrase_overlap * 0.4 +  # 40% phrase overlap
        topic_coverage * 0.3    # 30% topic coverage
    )
    
    return min(1.0, max(0.0, relevance_score))

# ============================================================================
# COVERAGE SCORE (0-1)
# ============================================================================

def calculate_coverage_score(source_content: str, summary: str) -> float:
    """
    Calculate coverage score (0-1).
    Does summary cover the main points?
    
    Uses:
    - Sentence-level comparison
    - Information density
    - Topic diversity
    
    Args:
        source_content: Original content
        summary: Generated summary
        
    Returns:
        Score from 0 to 1 (1 = comprehensive coverage)
    """
    
    if not source_content or not summary:
        return 0.0
    
    # Extract sentences
    source_sentences = extract_sentences(source_content)
    summary_sentences = extract_sentences(summary)
    
    if not source_sentences:
        return 0.0
    
    # Coverage metric 1: Information density
    # How many important source sentences are reflected in summary?
    source_norm = [normalize_text(s) for s in source_sentences]
    summary_norm = normalize_text(summary)
    
    covered_sentences = 0
    for sent_norm in source_norm[:10]:  # Check first 10 sentences
        # Check if key words from this sentence appear in summary
        key_words = set(sent_norm.split()) - {'the', 'a', 'an', 'is', 'are', 'of', 'in'}
        if key_words and any(word in summary_norm for word in key_words):
            covered_sentences += 1
    
    coverage_from_sentences = covered_sentences / min(len(source_sentences), 10) if source_sentences else 0.0
    
    # Coverage metric 2: Topic diversity
    # Summary should mention different aspects
    summary_words = normalize_text(summary).split()
    unique_words = set(summary_words)
    
    # Higher diversity = higher coverage
    diversity_score = len(unique_words) / (len(summary_words) + 1)
    diversity_score = min(1.0, diversity_score * 2)  # Scale up
    
    # Coverage metric 3: Length proportionality
    # Summary should be ~10-20% of source length for good coverage
    content_ratio = len(summary) / (len(source_content) + 1)
    
    if 0.05 <= content_ratio <= 0.30:
        length_score = 1.0
    elif content_ratio < 0.05:
        length_score = content_ratio / 0.05  # Too short
    else:
        length_score = 1.0 - min(0.5, (content_ratio - 0.30) / 0.70)  # Too long
    
    # Combined coverage score
    coverage_score = (
        coverage_from_sentences * 0.5 +  # 50% sentence coverage
        diversity_score * 0.3 +            # 30% diversity
        length_score * 0.2                 # 20% length proportion
    )
    
    return min(1.0, max(0.0, coverage_score))

# ============================================================================
# REDUNDANCY CHECK
# ============================================================================

def detect_redundancy(summary: str) -> Tuple[List[str], float]:
    """
    Detect redundant bullets/lines in summary.
    
    Args:
        summary: Summary text with bullets
        
    Returns:
        (list of redundant lines, redundancy score 0-1)
    """
    
    # Extract bullet points
    bullets = []
    lines = summary.split('\n')
    
    for line in lines:
        # Match bullet patterns: •, -, *, 1., etc.
        if re.match(r'^\s*[•\-*\d+.]\s+', line):
            clean_line = re.sub(r'^\s*[•\-*\d+.]\s+', '', line).strip()
            if clean_line:
                bullets.append(clean_line)
    
    if not bullets:
        return [], 0.0
    
    # Normalize and compare bullets
    normalized_bullets = [normalize_text(b) for b in bullets]
    
    # Find similar bullets (>80% similarity)
    redundant_pairs = []
    redundant_indices = set()
    
    for i in range(len(normalized_bullets)):
        for j in range(i + 1, len(normalized_bullets)):
            # Calculate similarity
            words_i = set(normalized_bullets[i].split())
            words_j = set(normalized_bullets[j].split())
            
            if not words_i or not words_j:
                continue
            
            # Jaccard similarity
            intersection = len(words_i & words_j)
            union = len(words_i | words_j)
            similarity = intersection / union if union > 0 else 0.0
            
            if similarity > 0.7:  # High similarity threshold
                redundant_pairs.append((i, j, similarity))
                redundant_indices.add(j)
    
    # Redundant lines
    redundant_lines = [bullets[i] for i in sorted(redundant_indices)]
    
    # Redundancy score (0-1, higher = more redundancy = bad)
    redundancy_score = len(redundant_lines) / len(bullets) if bullets else 0.0
    
    return redundant_lines, redundancy_score

# ============================================================================
# QUALITY SCORE (COMPOSITE)
# ============================================================================

def calculate_quality_score(
    source_content: str,
    summary: str
) -> Dict[str, float]:
    """
    Calculate comprehensive quality score for summary.
    
    Args:
        source_content: Original web content
        summary: Generated summary
        
    Returns:
        Dictionary with all scores
    """
    
    # Individual scores
    relevance = calculate_relevance_score(source_content, summary)
    coverage = calculate_coverage_score(source_content, summary)
    redundant_lines, redundancy = detect_redundancy(summary)
    
    # Quality metrics
    conciseness = 1.0 - min(1.0, len(summary) / (len(source_content) + 1))
    coherence = 1.0 - (redundancy * 0.5)  # Redundancy reduces coherence
    
    # Overall quality (weighted average)
    overall_quality = (
        relevance * 0.35 +
        coverage * 0.25 +
        coherence * 0.20 +
        conciseness * 0.20
    )
    
    return {
        "relevance": round(relevance, 3),
        "coverage": round(coverage, 3),
        "redundancy": round(redundancy, 3),
        "coherence": round(coherence, 3),
        "conciseness": round(conciseness, 3),
        "overall_quality": round(overall_quality, 3),
        "evaluation_status": "pass" if overall_quality > 0.6 else "warning" if overall_quality > 0.4 else "fail"
    }

# ============================================================================
# BATCH STATISTICS
# ============================================================================

def calculate_batch_statistics(scores_list: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Calculate statistics across multiple evaluations.
    
    Args:
        scores_list: List of quality score dictionaries
        
    Returns:
        Statistics (mean, median, min, max for each metric)
    """
    
    if not scores_list:
        return {}
    
    metrics = [
        "relevance", "coverage", "redundancy",
        "coherence", "conciseness", "overall_quality"
    ]
    
    stats = {}
    
    for metric in metrics:
        values = [s.get(metric, 0) for s in scores_list]
        values = [v for v in values if v is not None]
        
        if values:
            stats[f"{metric}_mean"] = round(sum(values) / len(values), 3)
            stats[f"{metric}_min"] = round(min(values), 3)
            stats[f"{metric}_max"] = round(max(values), 3)
            stats[f"{metric}_count"] = len(values)
    
    return stats

# ============================================================================
# GRADING
# ============================================================================

def get_quality_grade(overall_quality: float) -> str:
    """Convert quality score to grade"""
    if overall_quality >= 0.9:
        return "A+ (Excellent)"
    elif overall_quality >= 0.8:
        return "A (Very Good)"
    elif overall_quality >= 0.7:
        return "B (Good)"
    elif overall_quality >= 0.6:
        return "C (Acceptable)"
    elif overall_quality >= 0.5:
        return "D (Poor)"
    else:
        return "F (Failed)"

def get_metric_interpretation(metric_name: str, value: float) -> str:
    """Get human-readable interpretation of a metric"""
    interpretations = {
        "relevance": {
            "high": "Summary is highly relevant to source",
            "medium": "Summary captures main ideas",
            "low": "Summary misses key content"
        },
        "coverage": {
            "high": "Summary comprehensively covers topics",
            "medium": "Summary covers most topics",
            "low": "Summary lacks important details"
        },
        "redundancy": {
            "high": "Many repeated points (bad)",
            "medium": "Some repetition",
            "low": "Well-structured, no repetition (good)"
        },
        "coherence": {
            "high": "Logically consistent and clear",
            "medium": "Generally coherent",
            "low": "Lacks coherence"
        },
        "conciseness": {
            "high": "Well condensed",
            "medium": "Reasonable length",
            "low": "Too verbose"
        }
    }
    
    if metric_name not in interpretations:
        return "Unknown metric"
    
    thresholds = interpretations[metric_name]
    
    if value >= 0.7:
        return thresholds["high"]
    elif value >= 0.4:
        return thresholds["medium"]
    else:
        return thresholds["low"]

if __name__ == "__main__":
    # Test
    source = """
    Machine learning is a subset of artificial intelligence that focuses on enabling
    systems to learn from data without being explicitly programmed. It uses algorithms
    to identify patterns and make predictions based on sample data called training data.
    Deep learning is a subset of machine learning using neural networks.
    """
    
    summary = """
    • Machine learning enables systems to learn from data
    • Uses algorithms to find patterns
    • Deep learning uses neural networks
    """
    
    scores = calculate_quality_score(source, summary)
    print("Quality Scores:")
    for key, value in scores.items():
        print(f"  {key}: {value}")
