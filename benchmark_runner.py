"""
Benchmark Runner - Execute Full Comparison Tests
=================================================

Main script to run comprehensive benchmarks and generate reports.
"""

import time
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, '.')

from services.basic_pipeline import BasicLLMPipeline
from services.intelligent_orchestrator import IntelligentLLMOrchestrator
from services.benchmark_system import BenchmarkSystem
from services.learning_system import AdaptiveLearningSystem
from services.test_queries import TEST_QUERIES, get_query_stats
from config import Config


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*100)
    print(f"  {text}")
    print("="*100)


def print_section(text: str):
    """Print formatted section."""
    print(f"\n{text}")
    print("-" * len(text))


def run_benchmark_suite(num_queries: int = None, save_results: bool = True) -> dict:
    """
    Run complete benchmark suite.
    
    Args:
        num_queries: Number of queries to test (None = all)
        save_results: Whether to save results to files
    
    Returns:
        Benchmark results and report
    """
    
    print_header("INTELLIGENT LLM SYSTEM BENCHMARKING SUITE")
    
    # Initialize systems
    print_section("Initializing Systems")
    
    try:
        basic_pipeline = BasicLLMPipeline(Config.GOOGLE_API_KEY)
        print("✓ Basic Pipeline initialized")
    except Exception as e:
        print(f"✗ Failed to initialize basic pipeline: {e}")
        return None
    
    try:
        intelligent_system = IntelligentLLMOrchestrator(
            daily_budget_usd=50.0,
            monthly_budget_usd=500.0,
            cache_enabled=True,
            enable_evaluation=True
        )
        print("✓ Intelligent System initialized")
    except Exception as e:
        print(f"✗ Failed to initialize intelligent system: {e}")
        return None
    
    try:
        learning_system = AdaptiveLearningSystem()
        print("✓ Learning System initialized")
    except Exception as e:
        print(f"✗ Failed to initialize learning system: {e}")
        learning_system = None
    
    benchmark = BenchmarkSystem()
    print("✓ Benchmark System initialized")
    
    # Prepare test queries
    print_section("Test Query Statistics")
    
    queries_to_run = TEST_QUERIES if num_queries is None else TEST_QUERIES[:num_queries]
    stats = get_query_stats()
    
    print(f"Total Available Queries: {stats['total_queries']}")
    print(f"Queries to Test: {len(queries_to_run)}")
    print(f"Average Query Length: {stats['avg_length']:,} characters")
    print(f"\nQueries by Category:")
    for cat, count in stats["by_category"].items():
        pct = count / stats["total_queries"] * 100
        print(f"  • {cat.capitalize():<15} {count:>2} queries ({pct:>5.1f}%)")
    
    # Run benchmarks
    print_section("Running Benchmarks")
    
    start_time = time.time()
    results = []
    
    for i, test_query in enumerate(queries_to_run, 1):
        print(f"\n[{i:>2}/{len(queries_to_run)}] Testing {test_query['category'].capitalize():<10} - {test_query['description']}")
        
        try:
            result = benchmark.run_benchmark(
                test_query["query"],
                basic_pipeline,
                intelligent_system,
                learning_system,
                category=test_query["category"]
            )
            
            results.append(result)
            
            # Print result
            if result["comparison"]:
                comp = result["comparison"]
                print(f"    Latency: {comp['latency_improvement']['basic_ms']}ms → "
                      f"{comp['latency_improvement']['intelligent_ms']}ms "
                      f"({comp['latency_improvement']['speedup']:.1f}x faster)")
                print(f"    Cost: ${comp['cost_improvement']['basic_usd']:.4f} → "
                      f"${comp['cost_improvement']['intelligent_usd']:.4f} "
                      f"({comp['cost_improvement']['savings_pct']:+.1f}%)")
                print(f"    Quality: {comp['quality_comparison'].get('intelligent_quality_score', 'N/A')}")
                if comp['quality_comparison']['cache_used']:
                    print(f"    ✓ Cache used (super fast!)")
            else:
                print(f"    ✗ Incomplete comparison")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    elapsed = time.time() - start_time
    
    # Generate reports
    print_section("Generating Reports")
    
    report = benchmark.generate_summary_report()
    
    # Display comparison table
    print("\n")
    benchmark.print_comparison_table()
    
    # Save results if requested
    if save_results:
        print_section("Saving Results")
        
        files = benchmark.save_results()
        print(f"✓ Results saved to:")
        for label, filepath in files.items():
            print(f"    • {label}: {filepath}")
        
        # Save benchmark metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "benchmark_duration_seconds": elapsed,
            "total_queries": len(queries_to_run),
            "results_files": files,
            "query_categories": list(list(set(q["category"] for q in queries_to_run))),
            "systems_compared": ["basic_pipeline", "intelligent_system"],
            "report_summary": {
                "total_cost_saved": report.get("cost_analysis", {}).get("savings", {}).get("total_saved_usd", 0),
                "avg_speedup": report.get("latency_analysis", {}).get("improvement", {}).get("speedup", 0),
                "avg_quality_score": report.get("quality_metrics", {}).get("intelligent", {}).get("avg_quality_score", 0),
                "cache_hit_rate": report.get("cache_efficiency", {}).get("cache_hit_rate", 0)
            }
        }
        
        metadata_file = os.path.join("data/benchmarks", f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"    • metadata: {metadata_file}")
    
    # Learning system insights
    if learning_system and learning_system.history:
        print_section("Learning System Insights")
        
        insights = learning_system.get_insights()
        
        if "status" not in insights or insights["status"] != "no_data":
            print(f"Total Queries Recorded: {insights['total_queries']}")
            
            if insights.get("best_performers"):
                print(f"\nBest Performers:")
                print(f"  • Quality: {insights['best_performers'].get('quality', 'N/A')}")
                print(f"  • Speed: {insights['best_performers'].get('speed', 'N/A')}")
                print(f"  • Cost: {insights['best_performers'].get('cost', 'N/A')}")
            
            if insights.get("recommendations"):
                print(f"\nOptimization Recommendations:")
                for rec in insights["recommendations"]:
                    print(f"  • {rec}")
            
            # Export learning data
            export_file = learning_system.export_learning_data()
            print(f"\n✓ Learning data exported to: {export_file}")
    
    # Final summary
    print_section("Benchmark Summary")
    
    if report.get("overall_verdict"):
        verdict = report["overall_verdict"]
        print(f"\n{'Metric':<30} {'Status':<15}")
        print("-" * 45)
        print(f"{'Faster':<30} {'✓' if verdict['intelligent_faster'] else '✗':<15}")
        print(f"{'Cheaper':<30} {'✓' if verdict['intelligent_cheaper'] else '✗':<15}")
        print(f"{'Quality Acceptable (≥70%)':<30} {'✓' if verdict['intelligent_quality_acceptable'] else '✗':<15}")
    
    print(f"\nTotal Benchmark Time: {elapsed:.1f} seconds")
    print(f"Average Time per Query: {elapsed/len(queries_to_run):.1f} seconds")
    
    print("\n" + "="*100)
    print("BENCHMARK COMPLETE")
    print("="*100)
    
    return {
        "benchmark": benchmark,
        "report": report,
        "learning_system": learning_system,
        "elapsed_time": elapsed,
        "queries_tested": len(queries_to_run)
    }


def run_quick_benchmark(num_queries: int = 3) -> dict:
    """Run a quick benchmark with fewer queries."""
    print_header("QUICK BENCHMARK (Fast Test)")
    return run_benchmark_suite(num_queries=num_queries, save_results=True)


def run_full_benchmark() -> dict:
    """Run full benchmark with all available queries."""
    print_header("FULL BENCHMARK (Comprehensive Test)")
    return run_benchmark_suite(num_queries=None, save_results=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Intelligent LLM System")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark (3 queries)")
    parser.add_argument("--full", action="store_true", help="Run full benchmark (all queries)")
    parser.add_argument("--queries", type=int, help="Number of queries to test")
    parser.add_argument("--no-save", action="store_true", help="Don't save results")
    parser.add_argument("--learning", action="store_true", help="Show learning system insights")
    
    args = parser.parse_args()
    
    # Default to quick if no args
    if not args.quick and not args.full and not args.queries:
        args.quick = True
    
    # Run benchmark
    if args.full:
        result = run_full_benchmark()
    elif args.queries:
        result = run_benchmark_suite(num_queries=args.queries, save_results=not args.no_save)
    else:  # quick
        result = run_quick_benchmark()
    
    # Show learning insights if requested
    if args.learning and result and result.get("learning_system"):
        print_section("Learning System Full Analysis")
        
        learning_system = result["learning_system"]
        if learning_system.history:
            stats = learning_system.get_statistics()
            print(f"\nHistorical Statistics:")
            print(f"  Total Queries: {stats.get('total_queries', 0)}")
            print(f"  Total Cost: ${stats.get('total_cost', 0):.4f}")
            print(f"  Avg Quality: {stats.get('avg_quality', 0):.1f}%")
            print(f"  Avg Latency: {stats.get('avg_latency', 0):.0f}ms")
            print(f"  Success Rate: {stats.get('success_rate', 0)*100:.1f}%")
            print(f"  Cache Hit Rate: {stats.get('cache_hit_rate', 0)*100:.1f}%")
    
    print("\n✓ Benchmark execution complete. Check data/benchmarks/ for results.")
