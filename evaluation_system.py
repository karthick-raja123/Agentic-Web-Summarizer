"""
Evaluation System - Store and manage evaluation results
CSV/JSON storage, query tracking, batch analysis
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

from evaluation_metrics import calculate_quality_score

# ============================================================================
# CONFIGURATION
# ============================================================================

RESULTS_DIR = Path("evaluation_results")
RESULTS_CSV = RESULTS_DIR / "evaluations.csv"
RESULTS_JSON = RESULTS_DIR / "evaluations.json"
BATCH_SUMMARY = RESULTS_DIR / "batch_summary.json"

# ============================================================================
# INITIALIZATION
# ============================================================================

def ensure_results_dir():
    """Create results directory if needed"""
    RESULTS_DIR.mkdir(exist_ok=True)

def initialize_csv():
    """Create CSV file with headers if needed"""
    ensure_results_dir()
    
    if not RESULTS_CSV.exists():
        with open(RESULTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'query', 'num_urls', 'urls_used', 'source_length',
                'summary_length', 'relevance', 'coverage', 'redundancy',
                'coherence', 'conciseness', 'overall_quality', 'grade'
            ])

# ============================================================================
# STORE RESULTS
# ============================================================================

def store_evaluation_result(
    query: str,
    urls: List[str],
    source_content: str,
    summary: str,
    scores: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Store a single evaluation result.
    
    Args:
        query: Search query
        urls: URLs used
        source_content: Combined source content
        summary: Generated summary
        scores: Quality scores dict
        
    Returns:
        Result record with metadata
    """
    
    ensure_results_dir()
    initialize_csv()
    
    # Create result record
    record = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "num_urls": len(urls),
        "urls": urls,
        "source_length": len(source_content),
        "summary_length": len(summary),
        "source_preview": source_content[:200] + "..." if len(source_content) > 200 else source_content,
        "summary_preview": summary[:300] + "..." if len(summary) > 300 else summary,
        **scores
    }
    
    # Add to CSV
    with open(RESULTS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'query', 'num_urls', 'urls_used', 'source_length',
            'summary_length', 'relevance', 'coverage', 'redundancy',
            'coherence', 'conciseness', 'overall_quality', 'grade'
        ])
        writer.writerow({
            'timestamp': record['timestamp'],
            'query': record['query'],
            'num_urls': record['num_urls'],
            'urls_used': '; '.join(urls),
            'source_length': record['source_length'],
            'summary_length': record['summary_length'],
            'relevance': scores.get('relevance', ''),
            'coverage': scores.get('coverage', ''),
            'redundancy': scores.get('redundancy', ''),
            'coherence': scores.get('coherence', ''),
            'conciseness': scores.get('conciseness', ''),
            'overall_quality': scores.get('overall_quality', ''),
            'grade': scores.get('evaluation_status', '')
        })
    
    # Add to JSON
    results_json = load_json_results()
    results_json.append(record)
    save_json_results(results_json)
    
    return record

def load_json_results() -> List[Dict]:
    """Load all results from JSON file"""
    ensure_results_dir()
    
    if RESULTS_JSON.exists():
        with open(RESULTS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json_results(results: List[Dict]):
    """Save results to JSON file"""
    ensure_results_dir()
    
    with open(RESULTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def load_csv_results() -> List[Dict]:
    """Load results from CSV file"""
    ensure_results_dir()
    initialize_csv()
    
    results = []
    with open(RESULTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

# ============================================================================
# QUERY RESULTS
# ============================================================================

def get_results_for_query(query: str) -> List[Dict]:
    """Get all results for a specific query"""
    results = load_json_results()
    return [r for r in results if r.get('query', '').lower() == query.lower()]

def get_latest_result() -> Optional[Dict]:
    """Get most recent evaluation result"""
    results = load_json_results()
    return results[-1] if results else None

def get_all_results() -> List[Dict]:
    """Get all evaluation results"""
    return load_json_results()

def get_results_count() -> int:
    """Get total number of evaluations"""
    return len(load_json_results())

# ============================================================================
# BATCH STATISTICS
# ============================================================================

def calculate_batch_stats() -> Dict[str, Any]:
    """Calculate statistics across all evaluations"""
    results = load_json_results()
    
    if not results:
        return {
            "total_evaluations": 0,
            "average_quality": 0,
            "message": "No evaluations yet"
        }
    
    metrics = ['relevance', 'coverage', 'coherence', 'conciseness', 'overall_quality']
    stats = {"total_evaluations": len(results)}
    
    for metric in metrics:
        values = [float(r.get(metric, 0)) for r in results if r.get(metric)]
        if values:
            stats[f"{metric}_avg"] = round(sum(values) / len(values), 3)
            stats[f"{metric}_min"] = round(min(values), 3)
            stats[f"{metric}_max"] = round(max(values), 3)
    
    # Grade distribution
    grades = {}
    for result in results:
        grade = result.get('evaluation_status', 'unknown')
        grades[grade] = grades.get(grade, 0) + 1
    stats['grade_distribution'] = grades
    
    return stats

def save_batch_summary():
    """Save batch statistics to file"""
    ensure_results_dir()
    stats = calculate_batch_stats()
    
    with open(BATCH_SUMMARY, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_as_json(output_path: Optional[str] = None) -> str:
    """Export all results as JSON"""
    path = Path(output_path) if output_path else RESULTS_JSON
    path.parent.mkdir(exist_ok=True)
    
    results = load_json_results()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return str(path)

def export_as_csv(output_path: Optional[str] = None) -> str:
    """Export all results as CSV"""
    path = Path(output_path) if output_path else RESULTS_CSV
    path.parent.mkdir(exist_ok=True)
    return str(path)

def export_summary_report(output_path: Optional[str] = None) -> str:
    """Export a summary report"""
    path = Path(output_path) if output_path else RESULTS_DIR / "summary_report.md"
    path.parent.mkdir(exist_ok=True)
    
    stats = calculate_batch_stats()
    results = load_json_results()
    
    report = f"""# QuickGlance Evaluation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total Evaluations**: {stats.get('total_evaluations', 0)}
- **Average Quality**: {stats.get('overall_quality_avg', 0):.1%}
- **Quality Range**: {stats.get('overall_quality_min', 0):.1%} - {stats.get('overall_quality_max', 0):.1%}

## Metric Averages

| Metric | Average | Min | Max |
|--------|---------|-----|-----|
| Relevance | {stats.get('relevance_avg', 0):.1%} | {stats.get('relevance_min', 0):.1%} | {stats.get('relevance_max', 0):.1%} |
| Coverage | {stats.get('coverage_avg', 0):.1%} | {stats.get('coverage_min', 0):.1%} | {stats.get('coverage_max', 0):.1%} |
| Coherence | {stats.get('coherence_avg', 0):.1%} | {stats.get('coherence_min', 0):.1%} | {stats.get('coherence_max', 0):.1%} |
| Conciseness | {stats.get('conciseness_avg', 0):.1%} | {stats.get('conciseness_min', 0):.1%} | {stats.get('conciseness_max', 0):.1%} |

## Grade Distribution

"""
    
    for grade, count in stats.get('grade_distribution', {}).items():
        report += f"- {grade}: {count}\n"
    
    report += f"""

## Recent Evaluations

"""
    
    for result in results[-10:]:  # Last 10
        report += f"""
### {result.get('query', 'N/A')}

- **Timestamp**: {result.get('timestamp', 'N/A')}
- **URLs**: {len(result.get('urls', []))}
- **Overall Quality**: {result.get('overall_quality', 0):.1%}
- **Relevance**: {result.get('relevance', 0):.1%}
- **Coverage**: {result.get('coverage', 0):.1%}
- **Grade**: {result.get('evaluation_status', 'N/A')}

"""
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return str(path)

# ============================================================================
# CLEANUP & MANAGEMENT
# ============================================================================

def clear_results():
    """Clear all evaluation results"""
    ensure_results_dir()
    
    if RESULTS_JSON.exists():
        RESULTS_JSON.unlink()
    if RESULTS_CSV.exists():
        RESULTS_CSV.unlink()
    if BATCH_SUMMARY.exists():
        BATCH_SUMMARY.unlink()
    
    initialize_csv()

def get_results_status() -> Dict[str, Any]:
    """Get status of results storage"""
    ensure_results_dir()
    
    return {
        "results_dir": str(RESULTS_DIR),
        "exists": RESULTS_DIR.exists(),
        "csv_file": str(RESULTS_CSV),
        "csv_exists": RESULTS_CSV.exists(),
        "json_file": str(RESULTS_JSON),
        "json_exists": RESULTS_JSON.exists(),
        "total_evaluations": get_results_count(),
        "csv_size_mb": RESULTS_CSV.stat().st_size / (1024*1024) if RESULTS_CSV.exists() else 0,
        "json_size_mb": RESULTS_JSON.stat().st_size / (1024*1024) if RESULTS_JSON.exists() else 0
    }

if __name__ == "__main__":
    # Test
    ensure_results_dir()
    initialize_csv()
    print("✅ Evaluation system initialized")
    print(f"Results directory: {RESULTS_DIR}")
    print(f"CSV file: {RESULTS_CSV}")
    print(f"JSON file: {RESULTS_JSON}")
