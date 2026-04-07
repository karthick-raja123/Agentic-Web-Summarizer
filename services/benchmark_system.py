"""
Benchmark System - Comparison Framework
========================================

Compares basic pipeline vs intelligent system.
Measures: latency, tokens, cost, quality.
Generates comparison reports and identifies improvements.
"""

import json
import csv
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os
import numpy as np


class BenchmarkSystem:
    """
    Comprehensive benchmarking framework for comparing LLM pipelines.
    """
    
    def __init__(self, output_dir: str = "data/benchmarks"):
        """Initialize benchmark system."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.results = {
            "basic": [],
            "intelligent": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_count": 0
            }
        }
    
    def run_benchmark(self, query: str, basic_pipeline, intelligent_system,
                     learning_system=None, category: str = "general") -> Dict[str, Any]:
        """
        Run benchmark on single query comparing both systems.
        
        Args:
            query: Test query
            basic_pipeline: BasicLLMPipeline instance
            intelligent_system: IntelligentLLMOrchestrator instance
            learning_system: AdaptiveLearningSystem instance (optional)
            category: Query category
        
        Returns:
            Benchmark result with comparison
        """
        
        result_entry = {
            "query_id": len(self.results["basic"]) + 1,
            "query": query,
            "query_length": len(query),
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "basic_result": None,
            "intelligent_result": None,
            "comparison": None
        }
        
        # Run basic pipeline
        try:
            basic_result = basic_pipeline.summarize(query)
            result_entry["basic_result"] = basic_result
        except Exception as e:
            result_entry["basic_result"] = {"status": "error", "error": str(e)}
        
        # Run intelligent system
        try:
            intelligent_result = intelligent_system.summarize(query, priority="balanced")
            result_entry["intelligent_result"] = intelligent_result
            
            # Record in learning system if available
            if learning_system and intelligent_result.get("status") == "success":
                quality_score = intelligent_result.get("quality", {}).get("overall_score", 70)
                learning_system.record_query(query, intelligent_result, quality_score, category)
        except Exception as e:
            result_entry["intelligent_result"] = {"status": "error", "error": str(e)}
        
        # Compare results
        if (result_entry["basic_result"].get("status") == "success" and
            result_entry["intelligent_result"].get("status") == "success"):
            
            basic = result_entry["basic_result"]
            intelligent = result_entry["intelligent_result"]
            
            comparison = {
                "latency_improvement": {
                    "basic_ms": basic["latency_ms"],
                    "intelligent_ms": intelligent["latency_ms"],
                    "improvement_pct": ((basic["latency_ms"] - intelligent["latency_ms"]) / 
                                       basic["latency_ms"] * 100) if basic["latency_ms"] > 0 else 0,
                    "speedup": basic["latency_ms"] / intelligent["latency_ms"] if intelligent["latency_ms"] > 0 else 1
                },
                "cost_improvement": {
                    "basic_usd": basic.get("cost_usd", 0),
                    "intelligent_usd": intelligent.get("cost_usd", 0),
                    "savings": basic.get("cost_usd", 0) - intelligent.get("cost_usd", 0),
                    "savings_pct": ((basic.get("cost_usd", 0) - intelligent.get("cost_usd", 0)) / 
                                   max(basic.get("cost_usd", 0), 0.0001) * 100)
                },
                "token_comparison": {
                    "basic_tokens": basic.get("total_tokens", 0),
                    "intelligent_tokens": intelligent.get("total_tokens", 0),
                    "reduction_pct": ((basic.get("total_tokens", 0) - intelligent.get("total_tokens", 0)) /
                                     max(basic.get("total_tokens", 1), 1) * 100)
                },
                "quality_comparison": {
                    "basic_model": basic.get("model"),
                    "intelligent_model": intelligent.get("model"),
                    "intelligent_quality_score": intelligent.get("quality", {}).get("overall_score", 0),
                    "cache_used": intelligent.get("source") == "cache"
                }
            }
            
            result_entry["comparison"] = comparison
        
        self.results["basic"].append(result_entry["basic_result"])
        self.results["intelligent"].append(result_entry["intelligent_result"])
        self.results["metadata"]["test_count"] += 1
        
        return result_entry
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        
        if not self.results["basic"] or not self.results["intelligent"]:
            return {"status": "insufficient_data"}
        
        basic_results = [r for r in self.results["basic"] if r.get("status") == "success"]
        intelligent_results = [r for r in self.results["intelligent"] if r.get("status") == "success"]
        
        if not basic_results or not intelligent_results:
            return {"status": "failed_queries"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(basic_results),
            "successful_queries": len(basic_results),
            "success_rate": len(basic_results) / len(self.results["basic"]) * 100,
            
            "latency_analysis": {
                "basic": {
                    "avg_ms": np.mean([r["latency_ms"] for r in basic_results]),
                    "min_ms": np.min([r["latency_ms"] for r in basic_results]),
                    "max_ms": np.max([r["latency_ms"] for r in basic_results]),
                    "median_ms": np.median([r["latency_ms"] for r in basic_results]),
                    "stddev_ms": np.std([r["latency_ms"] for r in basic_results])
                },
                "intelligent": {
                    "avg_ms": np.mean([r["latency_ms"] for r in intelligent_results]),
                    "min_ms": np.min([r["latency_ms"] for r in intelligent_results]),
                    "max_ms": np.max([r["latency_ms"] for r in intelligent_results]),
                    "median_ms": np.median([r["latency_ms"] for r in intelligent_results]),
                    "stddev_ms": np.std([r["latency_ms"] for r in intelligent_results])
                },
                "improvement": {
                    "avg_improvement_pct": ((np.mean([r["latency_ms"] for r in basic_results]) -
                                            np.mean([r["latency_ms"] for r in intelligent_results])) /
                                           np.mean([r["latency_ms"] for r in basic_results]) * 100),
                    "speedup": (np.mean([r["latency_ms"] for r in basic_results]) /
                               np.mean([r["latency_ms"] for r in intelligent_results]))
                }
            },
            
            "cost_analysis": {
                "basic": {
                    "total_usd": sum(r.get("cost_usd", 0) for r in basic_results),
                    "avg_usd": np.mean([r.get("cost_usd", 0) for r in basic_results]),
                    "median_usd": np.median([r.get("cost_usd", 0) for r in basic_results])
                },
                "intelligent": {
                    "total_usd": sum(r.get("cost_usd", 0) for r in intelligent_results),
                    "avg_usd": np.mean([r.get("cost_usd", 0) for r in intelligent_results]),
                    "median_usd": np.median([r.get("cost_usd", 0) for r in intelligent_results])
                },
                "savings": {
                    "total_saved_usd": sum(r.get("cost_usd", 0) for r in basic_results) - 
                                      sum(r.get("cost_usd", 0) for r in intelligent_results),
                    "savings_pct": ((sum(r.get("cost_usd", 0) for r in basic_results) -
                                    sum(r.get("cost_usd", 0) for r in intelligent_results)) /
                                   max(sum(r.get("cost_usd", 0) for r in basic_results), 0.0001) * 100)
                }
            },
            
            "token_analysis": {
                "basic": {
                    "total_tokens": sum(r.get("total_tokens", 0) for r in basic_results),
                    "avg_tokens": np.mean([r.get("total_tokens", 0) for r in basic_results])
                },
                "intelligent": {
                    "total_tokens": sum(r.get("total_tokens", 0) for r in intelligent_results),
                    "avg_tokens": np.mean([r.get("total_tokens", 0) for r in intelligent_results])
                },
                "reduction": {
                    "total_reduction": sum(r.get("total_tokens", 0) for r in basic_results) -
                                      sum(r.get("total_tokens", 0) for r in intelligent_results),
                    "reduction_pct": ((sum(r.get("total_tokens", 0) for r in basic_results) -
                                      sum(r.get("total_tokens", 0) for r in intelligent_results)) /
                                     max(sum(r.get("total_tokens", 0) for r in basic_results), 1) * 100)
                }
            },
            
            "quality_metrics": {
                "intelligent": {
                    "avg_quality_score": np.mean([r.get("quality", {}).get("overall_score", 70) 
                                                 for r in intelligent_results]),
                    "avg_completeness": np.mean([r.get("quality", {}).get("completeness", 70)
                                                for r in intelligent_results]),
                    "avg_accuracy": np.mean([r.get("quality", {}).get("accuracy", 70)
                                           for r in intelligent_results])
                }
            },
            
            "cache_efficiency": {
                "cache_hits": sum(1 for r in intelligent_results if r.get("source") == "cache"),
                "cache_hit_rate": sum(1 for r in intelligent_results if r.get("source") == "cache") /
                                 len(intelligent_results) * 100
            },
            
            "model_usage": {
                "basic_models": list(set(r.get("model", "unknown") for r in basic_results)),
                "intelligent_models": list(set(r.get("model", "unknown") for r in intelligent_results))
            },
            
            "overall_verdict": {
                "intelligent_faster": np.mean([r["latency_ms"] for r in intelligent_results]) <
                                    np.mean([r["latency_ms"] for r in basic_results]),
                "intelligent_cheaper": sum(r.get("cost_usd", 0) for r in intelligent_results) <
                                      sum(r.get("cost_usd", 0) for r in basic_results),
                "intelligent_quality_acceptable": np.mean([r.get("quality", {}).get("overall_score", 70)
                                                          for r in intelligent_results]) >= 70
            }
        }
        
        return report
    
    def save_results(self) -> Dict[str, str]:
        """Save benchmark results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = os.path.join(self.output_dir, f"benchmark_results_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save summary report
        report = self.generate_summary_report()
        report_file = os.path.join(self.output_dir, f"benchmark_report_{timestamp}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save as CSV for easy viewing
        csv_file = os.path.join(self.output_dir, f"benchmark_comparison_{timestamp}.csv")
        self._save_csv_comparison(csv_file)
        
        return {
            "results_json": json_file,
            "report_json": report_file,
            "comparison_csv": csv_file
        }
    
    def _save_csv_comparison(self, filename: str):
        """Save comparison data as CSV."""
        rows = []
        
        for i, (basic, intelligent) in enumerate(zip(self.results["basic"], 
                                                      self.results["intelligent"])):
            if basic.get("status") == "success" and intelligent.get("status") == "success":
                row = {
                    "Query_ID": i + 1,
                    "Basic_Latency_ms": basic["latency_ms"],
                    "Intelligent_Latency_ms": intelligent["latency_ms"],
                    "Speedup": basic["latency_ms"] / intelligent["latency_ms"] if intelligent["latency_ms"] > 0 else 1,
                    "Basic_Cost_USD": basic.get("cost_usd", 0),
                    "Intelligent_Cost_USD": intelligent.get("cost_usd", 0),
                    "Cost_Savings_Pct": ((basic.get("cost_usd", 0) - intelligent.get("cost_usd", 0)) /
                                        max(basic.get("cost_usd", 0), 0.0001) * 100),
                    "Basic_Tokens": basic.get("total_tokens", 0),
                    "Intelligent_Tokens": intelligent.get("total_tokens", 0),
                    "Token_Reduction_Pct": ((basic.get("total_tokens", 0) - intelligent.get("total_tokens", 0)) /
                                           max(basic.get("total_tokens", 0), 1) * 100),
                    "Intelligent_Quality": intelligent.get("quality", {}).get("overall_score", 0),
                    "Cache_Used": "Yes" if intelligent.get("source") == "cache" else "No",
                    "Basic_Model": basic.get("model"),
                    "Intelligent_Model": intelligent.get("model")
                }
                rows.append(row)
        
        if rows:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    
    def print_comparison_table(self):
        """Print formatted comparison table."""
        report = self.generate_summary_report()
        
        if report.get("status"):
            print(f"Status: {report['status']}")
            return
        
        print("\n" + "="*100)
        print("BENCHMARK COMPARISON REPORT")
        print("="*100)
        
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"Successful Queries: {report['successful_queries']} / {report['total_queries']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        
        print("\n" + "-"*100)
        print("LATENCY ANALYSIS (milliseconds)")
        print("-"*100)
        print(f"{'Metric':<20} {'Basic':<20} {'Intelligent':<20} {'Improvement':<20}")
        print(f"{'-'*20} {'-'*20} {'-'*20} {'-'*20}")
        
        lat = report["latency_analysis"]
        print(f"{'Average':<20} {lat['basic']['avg_ms']:<20.1f} {lat['intelligent']['avg_ms']:<20.1f} "
              f"{lat['improvement']['avg_improvement_pct']:<19.1f}%")
        print(f"{'Median':<20} {lat['basic']['median_ms']:<20.1f} {lat['intelligent']['median_ms']:<20.1f} ")
        print(f"{'Min':<20} {lat['basic']['min_ms']:<20.1f} {lat['intelligent']['min_ms']:<20.1f} ")
        print(f"{'Max':<20} {lat['basic']['max_ms']:<20.1f} {lat['intelligent']['max_ms']:<20.1f} ")
        print(f"{'StdDev':<20} {lat['basic']['stddev_ms']:<20.1f} {lat['intelligent']['stddev_ms']:<20.1f} ")
        print(f"{'Speedup':<20} {'1.0x':<20} {lat['improvement']['speedup']:<20.1f}x")
        
        print("\n" + "-"*100)
        print("COST ANALYSIS (USD)")
        print("-"*100)
        print(f"{'Metric':<20} {'Basic':<20} {'Intelligent':<20} {'Savings':<20}")
        print(f"{'-'*20} {'-'*20} {'-'*20} {'-'*20}")
        
        cost = report["cost_analysis"]
        print(f"{'Total Cost':<20} ${cost['basic']['total_usd']:<19.4f} ${cost['intelligent']['total_usd']:<19.4f} "
              f"${cost['savings']['total_saved_usd']:<19.4f}")
        print(f"{'Avg Cost':<20} ${cost['basic']['avg_usd']:<19.6f} ${cost['intelligent']['avg_usd']:<19.6f} "
              f"{cost['savings']['savings_pct']:<19.1f}%")
        print(f"{'Median Cost':<20} ${cost['basic']['median_usd']:<19.6f} ${cost['intelligent']['median_usd']:<19.6f} ")
        
        print("\n" + "-"*100)
        print("TOKEN ANALYSIS")
        print("-"*100)
        print(f"{'Metric':<20} {'Basic':<20} {'Intelligent':<20} {'Reduction':<20}")
        print(f"{'-'*20} {'-'*20} {'-'*20} {'-'*20}")
        
        tok = report["token_analysis"]
        print(f"{'Total Tokens':<20} {tok['basic']['total_tokens']:<20.0f} {tok['intelligent']['total_tokens']:<20.0f} "
              f"{tok['reduction']['total_reduction']:<19.0f}")
        print(f"{'Avg Tokens':<20} {tok['basic']['avg_tokens']:<20.1f} {tok['intelligent']['avg_tokens']:<20.1f} "
              f"{tok['reduction']['reduction_pct']:<19.1f}%")
        
        print("\n" + "-"*100)
        print("QUALITY & CACHE METRICS")
        print("-"*100)
        
        qual = report["quality_metrics"]["intelligent"]
        cache = report["cache_efficiency"]
        
        print(f"Intelligent System Average Quality Score: {qual['avg_quality_score']:.1f}%")
        print(f"Intelligent System Average Completeness: {qual['avg_completeness']:.1f}%")
        print(f"Intelligent System Average Accuracy: {qual['avg_accuracy']:.1f}%")
        print(f"\nCache Hits: {cache['cache_hits']} out of {report['total_queries']}")
        print(f"Cache Hit Rate: {cache['cache_hit_rate']:.1f}%")
        
        print("\n" + "-"*100)
        print("VERDICT")
        print("-"*100)
        
        verdict = report["overall_verdict"]
        print(f"✓ Faster: {verdict['intelligent_faster']}")
        print(f"✓ Cheaper: {verdict['intelligent_cheaper']}")
        print(f"✓ Quality Acceptable (≥70%): {verdict['intelligent_quality_acceptable']}")
        
        if verdict['intelligent_faster'] and verdict['intelligent_cheaper']:
            print("\n🎯 INTELLIGENT SYSTEM IS BETTER on all metrics!")
        elif verdict['intelligent_faster'] or verdict['intelligent_cheaper']:
            print("\n✅ INTELLIGENT SYSTEM SHOWS IMPROVEMENTS")
        
        print("\n" + "="*100)
