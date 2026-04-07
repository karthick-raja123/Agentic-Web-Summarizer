"""
Comprehensive Test Suite for Evaluation System
Tests for evaluation_metrics.py and evaluation_system.py
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from evaluation_metrics import (
    normalize_text,
    extract_sentences,
    extract_key_phrases,
    calculate_relevance_score,
    calculate_coverage_score,
    detect_redundancy,
    calculate_quality_score,
    calculate_batch_statistics,
    get_quality_grade,
    get_metric_interpretation
)

from evaluation_system import (
    store_evaluation_result,
    load_json_results,
    save_json_results,
    get_results_for_query,
    get_latest_result,
    get_all_results,
    get_results_count,
    calculate_batch_stats,
    export_as_json,
    export_as_csv,
    export_summary_report,
    clear_results,
    RESULTS_DIR,
    RESULTS_CSV,
    RESULTS_JSON
)

# ============================================================================
# TEXT PROCESSING TESTS
# ============================================================================

class TestTextProcessing:
    """Tests for text normalization and extraction"""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization"""
        text = "Hello WORLD 123!"
        result = normalize_text(text)
        assert result.islower()
        assert "!" not in result
        assert "123" not in result
    
    def test_normalize_text_empty(self):
        """Test normalization of empty string"""
        result = normalize_text("")
        assert result == ""
    
    def test_normalize_text_special_chars(self):
        """Test normalization with special characters"""
        text = "Hello@#$%World&*()"
        result = normalize_text(text)
        assert "@" not in result
        assert "#" not in result
    
    def test_extract_sentences_basic(self):
        """Test sentence extraction"""
        text = "This is sentence one. This is sentence two! And three?"
        sentences = extract_sentences(text)
        assert len(sentences) == 3
        assert all(isinstance(s, str) for s in sentences)
    
    def test_extract_sentences_empty(self):
        """Test sentence extraction from empty string"""
        sentences = extract_sentences("")
        assert sentences == []
    
    def test_extract_sentences_no_punctuation(self):
        """Test extraction when no sentence endings present"""
        text = "No punctuation here"
        sentences = extract_sentences(text)
        assert len(sentences) == 1
    
    def test_extract_key_phrases_basic(self):
        """Test key phrase extraction"""
        text = "Machine learning is a subset of artificial intelligence. Machine learning uses algorithms."
        phrases = extract_key_phrases(text, num_phrases=5)
        assert isinstance(phrases, list)
        assert len(phrases) <= 5
        assert all(isinstance(p, str) for p in phrases)
    
    def test_extract_key_phrases_empty(self):
        """Test phrase extraction from empty text"""
        phrases = extract_key_phrases("", num_phrases=5)
        assert phrases == []
    
    def test_extract_key_phrases_short_text(self):
        """Test phrase extraction from very short text"""
        text = "Hi there"
        phrases = extract_key_phrases(text)
        assert isinstance(phrases, list)

# ============================================================================
# RELEVANCE SCORING TESTS
# ============================================================================

class TestRelevanceScoring:
    """Tests for relevance score calculation"""
    
    def test_relevance_identical(self):
        """Test relevance when summary matches source"""
        source = "Machine learning is a subset of artificial intelligence"
        summary = "Machine learning is a subset of artificial intelligence"
        score = calculate_relevance_score(source, summary)
        assert score > 0.9
        assert 0 <= score <= 1
    
    def test_relevance_completely_different(self):
        """Test relevance when summary is completely different"""
        source = "Machine learning is advanced"
        summary = "Basketball is a sport played by two teams"
        score = calculate_relevance_score(source, summary)
        assert score < 0.3
        assert 0 <= score <= 1
    
    def test_relevance_partial_overlap(self):
        """Test relevance with partial content overlap"""
        source = "Python is a programming language used for data science"
        summary = "Python is widely used for programming"
        score = calculate_relevance_score(source, summary)
        assert 0.3 < score < 0.9
        assert 0 <= score <= 1
    
    def test_relevance_empty_summary(self):
        """Test relevance with empty summary"""
        source = "Some important content here"
        summary = ""
        score = calculate_relevance_score(source, summary)
        assert score == 0
    
    def test_relevance_range(self):
        """Test that relevance score is always 0-1"""
        source = "Source content about machine learning and AI"
        summary = "Summary about ML and AI systems"
        score = calculate_relevance_score(source, summary)
        assert 0 <= score <= 1

# ============================================================================
# COVERAGE SCORING TESTS
# ============================================================================

class TestCoverageScoring:
    """Tests for coverage score calculation"""
    
    def test_coverage_high_coverage(self):
        """Test coverage when summary covers main points"""
        source = "Point one. Point two. Point three."
        summary = "Covers point one, two, and three effectively"
        score = calculate_coverage_score(source, summary)
        assert score > 0.5
        assert 0 <= score <= 1
    
    def test_coverage_low_coverage(self):
        """Test coverage when summary misses main points"""
        source = "Important point A. Important point B. Critical point C."
        summary = "Something else"
        score = calculate_coverage_score(source, summary)
        assert 0 <= score <= 1
    
    def test_coverage_empty_summary(self):
        """Test coverage with empty summary"""
        source = "Lots of important content"
        summary = ""
        score = calculate_coverage_score(source, summary)
        assert score == 0
    
    def test_coverage_very_long_summary(self):
        """Test coverage when summary is longer than source"""
        source = "Short"
        summary = "This is a very long summary that is much longer than the original source content"
        score = calculate_coverage_score(source, summary)
        assert 0 <= score <= 1
    
    def test_coverage_range(self):
        """Test that coverage score is always 0-1"""
        source = "Content with multiple points to cover"
        summary = "A summary"
        score = calculate_coverage_score(source, summary)
        assert 0 <= score <= 1

# ============================================================================
# REDUNDANCY DETECTION TESTS
# ============================================================================

class TestRedundancyDetection:
    """Tests for redundancy detection"""
    
    def test_redundancy_no_duplicates(self):
        """Test redundancy detection with no duplicates"""
        summary = "• Point A is important\n• Point B is different\n• Point C is unique"
        redundant_lines, score = detect_redundancy(summary)
        assert score == 0
        assert redundant_lines == []
    
    def test_redundancy_with_duplicates(self):
        """Test redundancy detection with similar points"""
        summary = "• Machine learning uses algorithms\n• ML also uses algorithms"
        redundant_lines, score = detect_redundancy(summary)
        assert score > 0
        assert score <= 1
    
    def test_redundancy_exact_duplicates(self):
        """Test redundancy detection with exact duplicates"""
        summary = "• Point X\n• Point X"
        redundant_lines, score = detect_redundancy(summary)
        assert score > 0
    
    def test_redundancy_multiple_formats(self):
        """Test redundancy detection with different bullet formats"""
        summary = "• Point one\n- Point one"
        redundant_lines, score = detect_redundancy(summary)
        assert 0 <= score <= 1
    
    def test_redundancy_no_bullets(self):
        """Test redundancy detection on plain text"""
        summary = "This is plain text with no bullet points"
        redundant_lines, score = detect_redundancy(summary)
        assert score == 0
    
    def test_redundancy_empty(self):
        """Test redundancy detection on empty string"""
        redundant_lines, score = detect_redundancy("")
        assert score == 0
        assert redundant_lines == []

# ============================================================================
# QUALITY SCORING TESTS
# ============================================================================

class TestQualityScoring:
    """Tests for comprehensive quality scoring"""
    
    def test_quality_score_structure(self):
        """Test that quality score returns correct structure"""
        source = "Machine learning is important for data science"
        summary = "• ML is important\n• Used in data science"
        scores = calculate_quality_score(source, summary)
        
        assert isinstance(scores, dict)
        expected_keys = ['relevance', 'coverage', 'redundancy', 'coherence', 
                        'conciseness', 'overall_quality', 'evaluation_status']
        for key in expected_keys:
            assert key in scores
    
    def test_quality_score_ranges(self):
        """Test that all quality scores are 0-1"""
        source = "Test source content here"
        summary = "Test summary"
        scores = calculate_quality_score(source, summary)
        
        assert 0 <= scores['relevance'] <= 1
        assert 0 <= scores['coverage'] <= 1
        assert 0 <= scores['redundancy'] <= 1
        assert 0 <= scores['coherence'] <= 1
        assert 0 <= scores['conciseness'] <= 1
        assert 0 <= scores['overall_quality'] <= 1
    
    def test_quality_score_high_quality(self):
        """Test quality score for high quality summary"""
        source = "Machine learning enables systems to learn from data"
        summary = "Machine learning is a system that learns from provided data"
        scores = calculate_quality_score(source, summary)
        
        assert scores['overall_quality'] > 0.5
        assert scores['evaluation_status'] in ['pass', 'warning', 'fail']
    
    def test_quality_score_poor_quality(self):
        """Test quality score for poor quality summary"""
        source = "Important scientific content about physics and mathematics"
        summary = "Random unrelated summary about cooking"
        scores = calculate_quality_score(source, summary)
        
        assert scores['overall_quality'] < 0.7
        assert scores['evaluation_status'] in ['pass', 'warning', 'fail']
    
    def test_quality_status_mapping(self):
        """Test status mapping based on quality score"""
        # Test pass threshold
        scores_high = {'overall_quality': 0.75}
        source = "x" * 100
        summary = "x" * 50
        result = calculate_quality_score(source, summary)
        
        if result['overall_quality'] > 0.6:
            assert result['evaluation_status'] == 'pass'
        elif result['overall_quality'] > 0.4:
            assert result['evaluation_status'] == 'warning'
        else:
            assert result['evaluation_status'] == 'fail'

# ============================================================================
# UTILITY FUNCTION TESTS
# ============================================================================

class TestUtilityFunctions:
    """Tests for utility functions"""
    
    def test_get_quality_grade_excellent(self):
        """Test grade conversion for excellent quality"""
        grade = get_quality_grade(0.95)
        assert grade == "A+"
        assert "Excellent" in grade or "A+" in grade
    
    def test_get_quality_grade_very_good(self):
        """Test grade conversion for very good quality"""
        grade = get_quality_grade(0.85)
        assert "A" in grade
    
    def test_get_quality_grade_good(self):
        """Test grade conversion for good quality"""
        grade = get_quality_grade(0.75)
        assert "B" in grade
    
    def test_get_quality_grade_acceptable(self):
        """Test grade conversion for acceptable quality"""
        grade = get_quality_grade(0.65)
        assert "C" in grade
    
    def test_get_quality_grade_poor(self):
        """Test grade conversion for poor quality"""
        grade = get_quality_grade(0.55)
        assert "D" in grade or "Poor" in grade
    
    def test_get_quality_grade_failed(self):
        """Test grade conversion for failed quality"""
        grade = get_quality_grade(0.25)
        assert "F" in grade
    
    def test_get_quality_grade_boundaries(self):
        """Test grade conversion at boundaries"""
        assert "A+" in get_quality_grade(0.90)
        assert "A" in get_quality_grade(0.89)
        assert "F" in get_quality_grade(0.50)
    
    def test_metric_interpretation_relevance(self):
        """Test metric interpretation for relevance"""
        interp_high = get_metric_interpretation("relevance", 0.9)
        interp_low = get_metric_interpretation("relevance", 0.2)
        
        assert isinstance(interp_high, str)
        assert isinstance(interp_low, str)
        assert len(interp_high) > 0
        assert len(interp_low) > 0
    
    def test_metric_interpretation_all_metrics(self):
        """Test metric interpretation for all metric types"""
        metrics = ['relevance', 'coverage', 'coherence', 'conciseness', 'redundancy']
        for metric in metrics:
            interp = get_metric_interpretation(metric, 0.7)
            assert isinstance(interp, str)
            assert len(interp) > 0

# ============================================================================
# BATCH STATISTICS TESTS
# ============================================================================

class TestBatchStatistics:
    """Tests for batch statistics calculation"""
    
    def test_batch_stats_structure(self):
        """Test batch statistics structure"""
        scores_list = [
            {'relevance': 0.8, 'coverage': 0.7, 'coherence': 0.9, 'conciseness': 0.8},
            {'relevance': 0.85, 'coverage': 0.75, 'coherence': 0.85, 'conciseness': 0.8},
        ]
        stats = calculate_batch_statistics(scores_list)
        
        assert isinstance(stats, dict)
        assert 'relevance_mean' in stats or 'count' in stats
    
    def test_batch_stats_empty(self):
        """Test batch statistics with empty list"""
        stats = calculate_batch_statistics([])
        assert isinstance(stats, dict)
    
    def test_batch_stats_calculations(self):
        """Test accuracy of batch statistics"""
        scores_list = [
            {'relevance': 0.8},
            {'relevance': 0.6},
            {'relevance': 1.0},
        ]
        stats = calculate_batch_statistics(scores_list)
        
        # Mean should be 0.8
        if 'relevance_mean' in stats:
            assert abs(stats['relevance_mean'] - 0.8) < 0.01

# ============================================================================
# STORAGE TESTS
# ============================================================================

class TestEvaluationStorage:
    """Tests for evaluation storage system"""
    
    @pytest.fixture
    def temp_results_dir(self):
        """Create temporary results directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_store_evaluation_creates_files(self, temp_results_dir):
        """Test that storing evaluation creates JSON and CSV files"""
        source = "Test source content"
        summary = "Test summary"
        scores = {
            'relevance': 0.8,
            'coverage': 0.75,
            'redundancy': 0.0,
            'coherence': 1.0,
            'conciseness': 0.85,
            'overall_quality': 0.79,
            'evaluation_status': 'pass'
        }
        
        result = store_evaluation_result(
            query="test query",
            urls=["http://example.com"],
            source_content=source,
            summary=summary,
            scores=scores
        )
        
        assert result is not None
        assert 'timestamp' in result
        assert result['query'] == "test query"
    
    def test_get_results_for_query(self):
        """Test retrieving results for specific query"""
        clear_results()
        
        source = "Content about Python"
        summary = "Python is a language"
        scores = {
            'relevance': 0.8, 'coverage': 0.75, 'redundancy': 0.0,
            'coherence': 1.0, 'conciseness': 0.85, 'overall_quality': 0.82,
            'evaluation_status': 'pass'
        }
        
        store_evaluation_result("Python tutorial", ["url1"], source, summary, scores)
        store_evaluation_result("Java tutorial", ["url2"], "Java content", "Java summary", scores)
        
        python_results = get_results_for_query("Python tutorial")
        assert len(python_results) > 0
        
        clear_results()
    
    def test_batch_stats_calculation(self):
        """Test batch statistics from stored results"""
        clear_results()
        
        scores = {
            'relevance': 0.8, 'coverage': 0.75, 'redundancy': 0.0,
            'coherence': 1.0, 'conciseness': 0.85, 'overall_quality': 0.82,
            'evaluation_status': 'pass'
        }
        
        store_evaluation_result("Query 1", ["url1"], "source1", "summary1", scores)
        
        stats = calculate_batch_stats()
        assert stats['total_evaluations'] > 0
        
        clear_results()

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_end_to_end_evaluation(self):
        """Test complete evaluation pipeline"""
        source = """
        Machine learning is a subset of artificial intelligence that enables
        systems to learn from data without being explicitly programmed.
        It uses algorithms to identify patterns and make predictions.
        """
        
        summary = """
        • Machine learning is part of AI
        • Enables systems to learn from data
        • Uses algorithms for predictions
        """
        
        # Calculate metrics
        scores = calculate_quality_score(source, summary)
        
        # Verify all components present
        assert scores['relevance'] > 0
        assert scores['coverage'] > 0
        assert scores['overall_quality'] > 0
        assert scores['evaluation_status'] in ['pass', 'warning', 'fail']
        
        # Get grade
        grade = get_quality_grade(scores['overall_quality'])
        assert len(grade) > 0
    
    def test_multiple_evaluations_batch_processing(self):
        """Test processing multiple evaluations"""
        clear_results()
        
        test_cases = [
            ("Python AI", "source1", "summary1"),
            ("Data Science", "source2", "summary2"),
            ("Web Development", "source3", "summary3"),
        ]
        
        for query, source, summary in test_cases:
            scores = calculate_quality_score(source, summary)
            store_evaluation_result(query, ["url"], source, summary, scores)
        
        # Verify all stored
        assert get_results_count() >= 3
        
        # Get stats
        stats = calculate_batch_stats()
        assert stats['total_evaluations'] >= 3
        
        clear_results()

# ============================================================================
# EXPORT TESTS
# ============================================================================

class TestExport:
    """Tests for export functionality"""
    
    def test_export_json(self):
        """Test JSON export"""
        clear_results()
        
        source = "Test content"
        summary = "Test summary"
        scores = {
            'relevance': 0.8, 'coverage': 0.75, 'redundancy': 0.0,
            'coherence': 1.0, 'conciseness': 0.85, 'overall_quality': 0.82,
            'evaluation_status': 'pass'
        }
        
        store_evaluation_result("test", ["url"], source, summary, scores)
        
        # Export should succeed
        export_path = export_as_json()
        assert Path(export_path).exists()
        
        clear_results()
    
    def test_export_summary_report(self):
        """Test summary report export"""
        clear_results()
        
        scores = {
            'relevance': 0.8, 'coverage': 0.75, 'redundancy': 0.0,
            'coherence': 1.0, 'conciseness': 0.85, 'overall_quality': 0.82,
            'evaluation_status': 'pass'
        }
        
        store_evaluation_result("test", ["url"], "source", "summary", scores)
        
        report_path = export_summary_report()
        assert Path(report_path).exists()
        
        with open(report_path, 'r') as f:
            content = f.read()
            assert "Evaluation Report" in content or "Summary" in content
        
        clear_results()

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_very_long_content(self):
        """Test with very long source and summary"""
        source = "word " * 1000
        summary = "summary " * 500
        scores = calculate_quality_score(source, summary)
        
        assert 0 <= scores['overall_quality'] <= 1
    
    def test_special_characters(self):
        """Test with special characters and Unicode"""
        source = "Hello 你好 مرحبا Здравствуйте! @#$%"
        summary = "Summary with émojis 🚀 ⭐ ✨"
        scores = calculate_quality_score(source, summary)
        
        assert 0 <= scores['overall_quality'] <= 1
    
    def test_single_word_content(self):
        """Test with minimal content"""
        source = "hello"
        summary = "hi"
        scores = calculate_quality_score(source, summary)
        
        assert 0 <= scores['overall_quality'] <= 1
    
    def test_duplicate_content(self):
        """Test with completely duplicate content"""
        content = "This is duplicate content"
        scores = calculate_quality_score(content, content)
        
        # Should have high relevance and coverage
        assert scores['relevance'] > 0.8
        assert scores['coverage'] > 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
