"""
Quality Evaluation System - Assesses summary quality against source content.
Measures completeness, accuracy, and coherence of generated summaries.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
from difflib import SequenceMatcher


@dataclass
class QualityMetrics:
    """Quality metrics for a summary"""
    completeness_score: float      # 0-100: Coverage of key information
    coherence_score: float         # 0-100: Logical flow and readability
    conciseness_score: float       # 0-100: Appropriate brevity
    accuracy_score: float          # 0-100: Factual accuracy vs source
    overall_score: float           # 0-100: Overall quality
    
    key_topics_covered: int        # Number of topics covered
    key_topics_total: int          # Total topics in source
    
    details: Dict[str, any]


class QualityEvaluator:
    """
    Evaluates quality of LLM outputs against source content.
    Uses multi-dimensional scoring system.
    """
    
    def __init__(self):
        """Initialize evaluator"""
        self.evaluation_history = []
        self.min_score_for_cache = 70  # Minimum score to cache result
    
    def evaluate_summary(
        self,
        source_content: str,
        summary: str,
        original_length: int = None
    ) -> QualityMetrics:
        """
        Evaluate summary quality.
        
        Args:
            source_content: Original source text
            summary: Generated summary
            original_length: Original content length (for context)
            
        Returns:
            QualityMetrics with detailed assessment
        """
        
        # Extract key metrics
        completeness = self._evaluate_completeness(source_content, summary)
        coherence = self._evaluate_coherence(summary)
        conciseness = self._evaluate_conciseness(source_content, summary, original_length)
        accuracy = self._evaluate_accuracy(source_content, summary)
        
        # Calculate overall score (weighted average)
        overall = (
            completeness * 0.35 +      # Most important: covers key points
            accuracy * 0.35 +          # Factual accuracy
            coherence * 0.20 +         # Readability
            conciseness * 0.10         # Appropriate length
        )
        
        # Extract topics
        source_topics = self._extract_topics(source_content)
        summary_topics = self._extract_topics(summary)
        topics_covered = len(set(source_topics) & set(summary_topics))
        
        metrics = QualityMetrics(
            completeness_score=completeness,
            coherence_score=coherence,
            conciseness_score=conciseness,
            accuracy_score=accuracy,
            overall_score=overall,
            key_topics_covered=topics_covered,
            key_topics_total=len(source_topics),
            details={
                "source_chars": len(source_content),
                "summary_chars": len(summary),
                "compression_ratio": len(summary) / max(1, len(source_content)),
                "summary_quality": self._get_quality_label(overall),
                "matches_found": self._count_phrase_matches(source_content, summary)
            }
        )
        
        self.evaluation_history.append(metrics)
        return metrics
    
    def _evaluate_completeness(self, source: str, summary: str) -> float:
        """
        Evaluate how completely the summary covers source content.
        Checks for key information retention.
        """
        
        # Extract key entities and terms from source
        source_terms = self._extract_key_terms(source)
        summary_terms = self._extract_key_terms(summary)
        
        if not source_terms:
            return 100.0
        
        # Calculate coverage
        covered_terms = set(source_terms) & set(summary_terms)
        coverage_ratio = len(covered_terms) / len(source_terms)
        
        # Bonus for proper keyphrase coverage
        source_keyphrases = self._extract_keyphrases(source)
        summary_keyphrases = self._extract_keyphrases(summary)
        keyphrase_coverage = len(set(source_keyphrases) & set(summary_keyphrases)) / max(1, len(source_keyphrases))
        
        # Combined score
        completeness = (coverage_ratio * 0.6 + keyphrase_coverage * 0.4) * 100
        
        return min(100, completeness)
    
    def _evaluate_coherence(self, summary: str) -> float:
        """
        Evaluate coherence and readability of summary.
        Checks for proper sentence structure, transitions, etc.
        """
        
        lines = summary.strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]
        
        if len(lines) < 2:
            return 75.0  # Single line is less coherent
        
        score = 100.0
        
        # Check sentence structure
        for line in lines:
            # Remove bullet points
            text = re.sub(r'^[\•\-\*\·]\s*', '', line)
            
            # Too short
            if len(text) < 5:
                score -= 5
            
            # Multiple consecutive punctuation
            if re.search(r'[.!?]{2,}', text):
                score -= 10
            
            # Incomplete sentence (no verb)
            words = text.lower().split()
            common_verbs = {'is', 'are', 'was', 'were', 'be', 'have', 'has', 'do', 'does', 'did', 'can', 'will', 'would', 'should', 'could', 'make', 'take', 'use', 'provide', 'include', 'show', 'find'}
            if len(words) > 3 and not any(v in words for v in common_verbs):
                score -= 3
        
        # Check for logical flow (simple heuristic)
        transition_words = ['however', 'moreover', 'furthermore', 'therefore', 'thus', 'also', 'additionally', 'meanwhile', 'consequently']
        transition_count = sum(1 for word in transition_words if word in summary.lower())
        
        if len(lines) > 2 and transition_count == 0:
            score -= 10  # Some transitions expected for multi-point summaries
        
        return max(50, min(100, score))
    
    def _evaluate_conciseness(
        self,
        source: str,
        summary: str,
        original_length: int = None
    ) -> float:
        """
        Evaluate if summary is appropriately concise.
        Should be significantly shorter than source but not too short.
        """
        
        source_len = len(source)
        summary_len = len(summary)
        
        # Ideal compression ratio depends on source length
        if source_len < 500:
            # Very short content - should compress more
            ideal_ratio = 0.4
            acceptable_range = (0.3, 0.6)
        elif source_len < 2000:
            # Medium content
            ideal_ratio = 0.3
            acceptable_range = (0.2, 0.5)
        else:
            # Long content
            ideal_ratio = 0.2
            acceptable_range = (0.1, 0.4)
        
        actual_ratio = summary_len / max(1, source_len)
        
        # Score based on deviation from ideal
        if acceptable_range[0] <= actual_ratio <= acceptable_range[1]:
            score = 95.0 - abs(actual_ratio - ideal_ratio) * 200
        else:
            # Outside acceptable range
            score = 50.0 - abs(actual_ratio - ideal_ratio) * 100
        
        return max(30, min(100, score))
    
    def _evaluate_accuracy(self, source: str, summary: str) -> float:
        """
        Evaluate factual accuracy of summary vs source.
        Checks for hallucinations or contradictions.
        """
        
        # Extract key facts/numbers from source
        source_numbers = self._extract_numbers(source)
        summary_numbers = self._extract_numbers(summary)
        
        # Numbers should match or not be present
        accuracy_score = 100.0
        
        for num in summary_numbers:
            if num not in source_numbers and num not in ['1', '2', '3']:  # Generic numbers
                accuracy_score -= 5  # Potential hallucination
        
        # Check for contradictions (simple heuristic)
        source_negations = self._count_negations(source)
        summary_negations = self._count_negations(summary)
        
        # If source has no negations but summary does, might be contradiction
        if source_negations == 0 and summary_negations > 2:
            accuracy_score -= 10
        
        # Check text similarity
        similarity = self._calculate_similarity(source, summary)
        
        # Summary should have good overlap with source
        if similarity < 0.3:
            accuracy_score -= 15  # Too different from source
        
        return max(50, min(100, accuracy_score))
    
    def _extract_key_terms(self, text: str, top_n: int = 20) -> List[str]:
        """Extract key terms from text"""
        
        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'shall', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = text.lower().split()
        key_terms = [w for w in words if w not in common_words and len(w) > 3]
        
        # Count frequency
        from collections import Counter
        freq = Counter(key_terms)
        
        return [term for term, _ in freq.most_common(top_n)]
    
    def _extract_keyphrases(self, text: str, top_n: int = 10) -> List[str]:
        """Extract key phrases (2-3 word combinations)"""
        
        sentences = re.split(r'[.!?]+', text)
        phrases = []
        
        for sentence in sentences:
            words = sentence.lower().split()
            for i in range(len(words) - 1):
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
        
        from collections import Counter
        freq = Counter(phrases)
        
        return [p for p, _ in freq.most_common(top_n)]
    
    def _extract_numbers(self, text: str) -> List[str]:
        """Extract numbers from text"""
        return re.findall(r'\d+\.?\d*', text)
    
    def _count_negations(self, text: str) -> int:
        """Count negation words"""
        negations = ['not', 'no', 'never', 'none', 'neither', 'nor', 'nothing']
        return sum(1 for neg in negations if f' {neg} ' in f' {text.lower()} ')
    
    def _count_phrase_matches(self, source: str, summary: str) -> int:
        """Count matching phrases between source and summary"""
        
        source_phrases = re.findall(r'\b\w+\s+\w+\b', source.lower())
        summary_phrases = re.findall(r'\b\w+\s+\w+\b', summary.lower())
        
        return len(set(source_phrases) & set(summary_phrases))
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        
        # Simple extraction: look for capitalized words
        words = text.split()
        topics = [w.strip('.,!?;:') for w in words if w[0].isupper() and len(w) > 3]
        
        return list(set(topics))
    
    def _get_quality_label(self, score: float) -> str:
        """Get human-readable quality label"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def get_evaluation_stats(self) -> Dict[str, any]:
        """Get evaluation statistics"""
        
        if not self.evaluation_history:
            return {"total_evaluations": 0}
        
        scores = [m.overall_score for m in self.evaluation_history]
        
        return {
            "total_evaluations": len(self.evaluation_history),
            "avg_overall_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "avg_completeness": sum(m.completeness_score for m in self.evaluation_history) / len(self.evaluation_history),
            "avg_accuracy": sum(m.accuracy_score for m in self.evaluation_history) / len(self.evaluation_history),
            "avg_coherence": sum(m.coherence_score for m in self.evaluation_history) / len(self.evaluation_history),
            "cacheable_results": sum(1 for m in self.evaluation_history if m.overall_score >= self.min_score_for_cache)
        }
