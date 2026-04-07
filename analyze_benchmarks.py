"""
Benchmark Analyzer Runner - Analyze Results & Identify Issues
==============================================================

Main script to analyze benchmark results and generate failure reports.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from services.benchmark_analyzer import BenchmarkAnalyzer


def find_latest_benchmark_files():
    """Find the latest benchmark result files."""
    
    benchmark_dir = "data/benchmarks"
    
    if not os.path.exists(benchmark_dir):
        return None, None
    
    # Find latest results and report files
    results_files = list(Path(benchmark_dir).glob("benchmark_results_*.json"))
    report_files = list(Path(benchmark_dir).glob("benchmark_report_*.json"))
    
    if not results_files:
        return None, None
    
    latest_results = sorted(results_files)[-1]
    latest_report = sorted(report_files)[-1] if report_files else None
    
    return str(latest_results), str(latest_report)


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*100)
    print(f"  {text}")
    print("="*100)


def analyze_benchmarks(results_file: str = None, output_file: str = None):
    """Run benchmark analysis."""
    
    print_header("BENCHMARK FAILURE ANALYSIS")
    
    # Find files if not provided
    if not results_file:
        results_file, report_file = find_latest_benchmark_files()
        if not results_file:
            print("❌ No benchmark results found in data/benchmarks/")
            print("   Run: python benchmark_runner.py --quick")
            return
        print(f"✓ Found latest results: {Path(results_file).name}")
    
    # Initialize analyzer
    try:
        analyzer = BenchmarkAnalyzer(results_file=results_file)
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return
    
    # Run analysis
    print("\nAnalyzing benchmark results...")
    analysis = analyzer.analyze_all()
    
    if analysis.get("status") == "no_data":
        print("❌ No data in benchmark results")
        return
    
    # Print report
    analyzer.print_analysis_report()
    
    # Export analysis
    export_file = analyzer.export_analysis(output_file)
    print(f"\n✓ Analysis exported to: {export_file}")
    
    return analysis


def analyze_specific_scenarios():
    """Analyze specific failure scenarios from user input."""
    
    print_header("SCENARIO-BASED FAILURE ANALYSIS")
    
    scenarios = {
        "Query 1 → Faster, cheaper": {
            "description": "Query completed faster and cheaper than baseline",
            "expected": "SUCCESS - System working as intended",
            "reason": "Model selection worked, possibly cache hit",
            "action": "MONITOR - Track cache hit rate"
        },
        "Query 2 → Slower, better quality": {
            "description": "Query took longer but produced better quality",
            "expected": "ACCEPTABLE TRADEOFF",
            "reason": "Selected Pro model for quality (legitimate choice)",
            "action": "INVESTIGATE - Was quality improvement necessary?",
            "recommendations": [
                "Check if quality threshold triggered Pro model unnecessarily",
                "Verify quality evaluation cost",
                "Consider: is 10-20% slower worth quality improvement?"
            ]
        },
        "Query 3 → Failed cache, fallback used": {
            "description": "Cache lookup failed, system fell back to API",
            "expected": "ACCEPTABLE - Fallback working",
            "reason": "Cache key mismatch or cache miss (expected for new queries)",
            "action": "ANALYZE - Is cache misses happening too often?",
            "recommendations": [
                "Check cache hit rate across entire benchmark",
                "Verify cache key generation logic",
                "Clear cache if corrupted",
                "Monitor cache size for limits",
                "First query for content always misses - normal"
            ]
        }
    }
    
    for scenario, details in scenarios.items():
        print(f"\n{'-'*100}")
        print(f"Scenario: {scenario}")
        print(f"{'-'*100}")
        print(f"Description: {details['description']}")
        print(f"Expected: {details['expected']}")
        print(f"Reason: {details['reason']}")
        print(f"Action: {details['action']}")
        
        if "recommendations" in details:
            print(f"Recommendations:")
            for rec in details["recommendations"]:
                print(f"  • {rec}")
    
    print("\n" + "="*100)


def generate_improvement_plan(analysis: dict):
    """Generate improvement plan from analysis."""
    
    print_header("IMPROVEMENT PLAN")
    
    if not analysis or analysis.get("status") == "no_data":
        print("No analysis available")
        return
    
    recommendations = analysis.get("recommendations", [])
    
    plan = {
        "immediate_actions": [],
        "short_term_fixes": [],
        "long_term_improvements": []
    }
    
    for rec in recommendations:
        priority = rec.get("priority", "LOW")
        issue = rec.get("issue", "Unknown")
        
        if priority == "CRITICAL":
            plan["immediate_actions"].append(issue)
        elif priority in ["HIGH", "MEDIUM"]:
            plan["short_term_fixes"].append(issue)
        else:
            plan["long_term_improvements"].append(issue)
    
    print("\nIMMEDIATE ACTIONS (Do First)")
    print("-" * 100)
    if plan["immediate_actions"]:
        for i, action in enumerate(plan["immediate_actions"], 1):
            print(f"{i}. {action}")
    else:
        print("✓ No critical issues detected")
    
    print("\nSHORT-TERM FIXES (This Week)")
    print("-" * 100)
    if plan["short_term_fixes"]:
        for i, fix in enumerate(plan["short_term_fixes"], 1):
            print(f"{i}. {fix}")
    else:
        print("✓ No significant issues detected")
    
    print("\nLONG-TERM IMPROVEMENTS (Optimization)")
    print("-" * 100)
    if plan["long_term_improvements"]:
        for i, imp in enumerate(plan["long_term_improvements"], 1):
            print(f"{i}. {imp}")
    else:
        print("✓ No optimization recommendations")
    
    print("\n" + "="*100)


def create_failure_report(analysis: dict):
    """Create detailed failure report."""
    
    if not analysis or analysis.get("status") == "no_data":
        return
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": analysis.get("summary", {}),
        "failures": {
            "worst_performers": analysis.get("worst_performers", []),
            "underperformance_cases": analysis.get("intelligent_underperformance", []),
            "failure_cases": analysis.get("failure_cases", [])
        },
        "analysis": {
            "root_causes": analysis.get("root_causes", {}),
            "recommendations": analysis.get("recommendations", [])
        }
    }
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/benchmarks/failure_report_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Detailed failure report saved to: {filename}")
    
    return filename


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Benchmark Results")
    parser.add_argument("--analyze", action="store_true", help="Analyze latest results")
    parser.add_argument("--file", type=str, help="Path to results file")
    parser.add_argument("--scenarios", action="store_true", help="Show scenario analysis")
    parser.add_argument("--plan", action="store_true", help="Generate improvement plan")
    parser.add_argument("--full", action="store_true", help="Full analysis (analyze + scenarios + plan)")
    parser.add_argument("--output", type=str, help="Output file for analysis")
    
    args = parser.parse_args()
    
    # Default to full analysis
    if not any([args.analyze, args.scenarios, args.plan, args.full, args.file]):
        args.analyze = True
    
    analysis = None
    
    # Run analysis
    if args.analyze or args.full:
        analysis = analyze_benchmarks(results_file=args.file, output_file=args.output)
    
    # Show scenarios
    if args.scenarios or args.full:
        analyze_specific_scenarios()
    
    # Generate plan
    if (args.plan or args.full) and analysis:
        generate_improvement_plan(analysis)
    
    # Create failure report
    if analysis and (args.analyze or args.full):
        create_failure_report(analysis)
    
    print("\n✓ Analysis complete.\n")
