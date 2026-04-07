"""
Benchmark Analysis & Failure Detection System
==============================================

Analyzes benchmark results to identify:
- Worst performing queries
- Cases where intelligent system underperforms
- Root causes of failures
- Recommended improvements
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import statistics


class BenchmarkAnalyzer:
    """Analyzes benchmark results for failures and improvements."""
    
    def __init__(self, results_file: str = None, report_file: str = None):
        """Initialize analyzer with benchmark results."""
        self.results_file = results_file
        self.report_file = report_file
        self.results = None
        self.report = None
        self.failures = []
        self.improvements_needed = []
        
        if results_file and os.path.exists(results_file):
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        
        if report_file and os.path.exists(report_file):
            with open(report_file, 'r') as f:
                self.report = json.load(f)
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run complete analysis."""
        if not self.results:
            return {"status": "no_data"}
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "worst_performers": self._find_worst_performers(),
            "intelligent_underperformance": self._find_underperformance(),
            "failure_cases": self._analyze_failures(),
            "root_causes": self._identify_root_causes(),
            "recommendations": self._generate_recommendations(),
            "summary": self._generate_summary()
        }
        
        return analysis
    
    def _find_worst_performers(self) -> List[Dict[str, Any]]:
        """Identify queries with worst performance in intelligent system."""
        
        if not self.results or not self.results.get("intelligent"):
            return []
        
        worst = []
        
        for i, result in enumerate(self.results["intelligent"]):
            if result.get("status") != "success":
                worst.append({
                    "query_id": i + 1,
                    "category": "error",
                    "status": "failed",
                    "error": result.get("error", "Unknown error"),
                    "issue_type": "api_failure"
                })
            elif result.get("latency_ms", 0) > 2000:  # Very slow
                worst.append({
                    "query_id": i + 1,
                    "latency_ms": result.get("latency_ms"),
                    "category": "slow_response",
                    "model": result.get("model"),
                    "issue_type": "high_latency"
                })
            elif result.get("cost_usd", 0) > 0.01:  # Very expensive
                worst.append({
                    "query_id": i + 1,
                    "cost_usd": result.get("cost_usd"),
                    "category": "expensive_query",
                    "model": result.get("model"),
                    "issue_type": "high_cost"
                })
        
        # Sort by severity
        worst.sort(key=lambda x: -x.get("latency_ms", x.get("cost_usd", 0)))
        return worst[:10]  # Top 10 worst
    
    def _find_underperformance(self) -> List[Dict[str, Any]]:
        """Find cases where intelligent system is WORSE than baseline."""
        
        if not self.results:
            return []
        
        underperforming = []
        basic = self.results.get("basic", [])
        intelligent = self.results.get("intelligent", [])
        
        for i, (basic_result, intell_result) in enumerate(zip(basic, intelligent)):
            if basic_result.get("status") != "success" or intell_result.get("status") != "success":
                continue
            
            basic_latency = basic_result.get("latency_ms", 0)
            intell_latency = intell_result.get("latency_ms", 0)
            basic_cost = basic_result.get("cost_usd", 0)
            intell_cost = intell_result.get("cost_usd", 0)
            
            issues = []
            
            # Latency worse
            if intell_latency > basic_latency * 1.1:  # 10% threshold
                latency_ratio = intell_latency / basic_latency
                issues.append({
                    "type": "latency_regression",
                    "basic_ms": basic_latency,
                    "intelligent_ms": intell_latency,
                    "regression_multiplier": latency_ratio,
                    "regression_pct": (latency_ratio - 1) * 100
                })
            
            # Cost worse
            if intell_cost > basic_cost * 1.1:  # 10% threshold
                cost_ratio = intell_cost / basic_cost
                issues.append({
                    "type": "cost_regression",
                    "basic_cost": basic_cost,
                    "intelligent_cost": intell_cost,
                    "regression_multiplier": cost_ratio,
                    "regression_pct": (cost_ratio - 1) * 100
                })
            
            # Quality too low
            quality_score = intell_result.get("quality", {}).get("overall_score", 100)
            if quality_score < 70:
                issues.append({
                    "type": "quality_too_low",
                    "quality_score": quality_score,
                    "target": 70
                })
            
            # Cache failure
            if intell_result.get("source") == "api" and intell_result.get("model") != basic_result.get("model"):
                # Used pro model instead of flash - might be unnecessary
                if intell_latency > basic_latency * 1.5:
                    issues.append({
                        "type": "expensive_model_selection",
                        "selected_model": intell_result.get("model"),
                        "basic_model": basic_result.get("model"),
                        "reason": "Switched to expensive model unnecessarily"
                    })
            
            if issues:
                underperforming.append({
                    "query_id": i + 1,
                    "issues": issues,
                    "severity": len(issues)
                })
        
        # Sort by severity
        underperforming.sort(key=lambda x: -x["severity"])
        return underperforming
    
    def _analyze_failures(self) -> List[Dict[str, Any]]:
        """Categorize and analyze failure cases."""
        
        failures_by_type = defaultdict(list)
        
        if not self.results:
            return []
        
        intelligent = self.results.get("intelligent", [])
        
        for i, result in enumerate(intelligent):
            if result.get("status") != "success":
                error = result.get("error", "Unknown")
                
                # Categorize error
                error_type = self._categorize_error(error)
                
                failures_by_type[error_type].append({
                    "query_id": i + 1,
                    "error": error,
                    "model_attempted": result.get("model", "unknown"),
                    "full_error": error
                })
        
        # Convert to list with analysis
        failure_analysis = []
        for error_type, instances in failures_by_type.items():
            failure_analysis.append({
                "error_type": error_type,
                "count": len(instances),
                "percentage": len(instances) / len(intelligent) * 100,
                "instances": instances,
                "possible_causes": self._explain_error_type(error_type)
            })
        
        return sorted(failure_analysis, key=lambda x: -x["count"])
    
    def _categorize_error(self, error: str) -> str:
        """Categorize error into type."""
        error_lower = error.lower()
        
        if "api" in error_lower or "connection" in error_lower:
            return "api_connection_error"
        elif "quota" in error_lower or "rate" in error_lower:
            return "quota_or_rate_limit"
        elif "invalid" in error_lower or "key" in error_lower:
            return "invalid_credentials"
        elif "timeout" in error_lower:
            return "timeout"
        elif "budget" in error_lower:
            return "budget_exceeded"
        elif "quality" in error_lower or "evaluation" in error_lower:
            return "quality_evaluation_failure"
        elif "cache" in error_lower:
            return "cache_system_error"
        else:
            return "other"
    
    def _explain_error_type(self, error_type: str) -> List[str]:
        """Explain possible causes for error type."""
        explanations = {
            "api_connection_error": [
                "Network connectivity issue",
                "Google API service temporarily unavailable",
                "Firewall/proxy blocking connections",
                "API endpoint changed or deprecated"
            ],
            "quota_or_rate_limit": [
                "Daily quota exhausted",
                "Rate limit (too many requests)",
                "Concurrent request limit exceeded",
                "Project quota limit reached"
            ],
            "invalid_credentials": [
                "API key expired or revoked",
                "API key not valid for this API",
                "Project disabled or deleted",
                "Wrong credentials configured"
            ],
            "timeout": [
                "Query too complex (tokenization timeout)",
                "API responding slowly",
                "Large input causing processing delay",
                "Server-side timeout on API"
            ],
            "budget_exceeded": [
                "Daily budget limit hit",
                "Monthly budget limit hit",
                "Cost tracking incorrect",
                "Unexpected expensive operation"
            ],
            "quality_evaluation_failure": [
                "Quality evaluator model failed",
                "Invalid quality evaluation response",
                "Quality scoring logic error",
                "Evaluation criteria too strict"
            ],
            "cache_system_error": [
                "Cache corruption",
                "Disk I/O error on cache",
                "Cache size limit exceeded",
                "Cache key generation error"
            ],
            "other": [
                "Unexpected system error",
                "Model incompatibility",
                "Request format invalid",
                "Response parsing error"
            ]
        }
        return explanations.get(error_type, ["Unknown cause"])
    
    def _identify_root_causes(self) -> Dict[str, Any]:
        """Identify root causes of underperformance."""
        
        root_causes = {
            "poor_model_selection": {
                "description": "Intelligent system chose wrong model",
                "cases": [],
                "frequency": 0,
                "impact": "latency or cost"
            },
            "cache_inefficiency": {
                "description": "Caching not working as expected",
                "cases": [],
                "frequency": 0,
                "impact": "no speedup despite cache"
            },
            "orchestration_overhead": {
                "description": "Intelligent system adds overhead",
                "cases": [],
                "frequency": 0,
                "impact": "slower than direct API"
            },
            "quality_evaluation_cost": {
                "description": "Quality evaluation adds latency/cost",
                "cases": [],
                "frequency": 0,
                "impact": "extra time/cost for evaluation"
            },
            "api_reliability": {
                "description": "API errors or timeouts",
                "cases": [],
                "frequency": 0,
                "impact": "request failures"
            },
            "budget_limits": {
                "description": "Cost management blocked requests",
                "cases": [],
                "frequency": 0,
                "impact": "queries rejected for cost"
            }
        }
        
        underperforming = self._find_underperformance()
        
        for case in underperforming:
            for issue in case.get("issues", []):
                if issue["type"] == "expensive_model_selection":
                    root_causes["poor_model_selection"]["cases"].append(case["query_id"])
                    root_causes["poor_model_selection"]["frequency"] += 1
                elif issue["type"] == "latency_regression":
                    root_causes["orchestration_overhead"]["cases"].append(case["query_id"])
                    root_causes["orchestration_overhead"]["frequency"] += 1
                elif issue["type"] == "cost_regression":
                    root_causes["poor_model_selection"]["cases"].append(case["query_id"])
                    root_causes["poor_model_selection"]["frequency"] += 1
        
        failures = self._analyze_failures()
        for failure in failures:
            if failure["error_type"] == "budget_exceeded":
                root_causes["budget_limits"]["frequency"] = failure["count"]
                root_causes["budget_limits"]["cases"] = [f["query_id"] for f in failure["instances"]]
            elif failure["error_type"] in ["api_connection_error", "timeout"]:
                root_causes["api_reliability"]["frequency"] += failure["count"]
            elif failure["error_type"] == "quality_evaluation_failure":
                root_causes["quality_evaluation_cost"]["frequency"] += failure["count"]
        
        # Filter out zero-frequency causes
        return {k: v for k, v in root_causes.items() if v["frequency"] > 0}
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate fix recommendations based on analysis."""
        
        recommendations = []
        root_causes = self._identify_root_causes()
        
        for cause_name, cause_data in root_causes.items():
            if cause_data["frequency"] == 0:
                continue
            
            if cause_name == "poor_model_selection":
                recommendations.append({
                    "issue": "Poor Model Selection",
                    "priority": "HIGH",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": f"Cost increase of {sum(r.get('regression_pct', 0) for r in self._find_underperformance())}%",
                    "fixes": [
                        "Review model selection heuristics - consider size thresholds",
                        "Adjust quality thresholds - Pro may be selected unnecessarily",
                        "Enable learning system to build better decision rules",
                        "Lower quality requirements if Flash sufficient",
                        "Increase Flash model usage threshold"
                    ],
                    "estimated_impact": "30-50% cost reduction per affected query"
                })
            
            elif cause_name == "orchestration_overhead":
                recommendations.append({
                    "issue": "Orchestration Overhead",
                    "priority": "MEDIUM",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": "Added latency from intelligent system wrapper",
                    "fixes": [
                        "Profile orchestration code for bottlenecks",
                        "Reduce quality evaluation frequency",
                        "Cache model selection decisions",
                        "Parallelize metric collection if possible",
                        "Consider async processing for evaluations"
                    ],
                    "estimated_impact": "10-20% latency reduction"
                })
            
            elif cause_name == "cache_inefficiency":
                recommendations.append({
                    "issue": "Cache Inefficiency",
                    "priority": "HIGH",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": "Not getting expected speedup from caching",
                    "fixes": [
                        "Check cache key generation - may not match identical queries",
                        "Verify cache TTL settings - expired too quickly",
                        "Ensure cache is enabled in configuration",
                        "Check cache storage folder exists and is writable",
                        "Enable cache debugging to see what's being cached"
                    ],
                    "estimated_impact": "50-100x speedup on affected queries"
                })
            
            elif cause_name == "quality_evaluation_cost":
                recommendations.append({
                    "issue": "Quality Evaluation Overhead",
                    "priority": "MEDIUM",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": "Extra latency and cost from quality evaluation",
                    "fixes": [
                        "Skip quality evaluation for simple queries",
                        "Use lower-cost evaluation model (Flash instead of Pro)",
                        "Cache evaluation results for similar content",
                        "Reduce evaluation dimensions to critical ones only",
                        "Disable evaluation for high-throughput scenarios"
                    ],
                    "estimated_impact": "20-30% latency reduction"
                })
            
            elif cause_name == "api_reliability":
                recommendations.append({
                    "issue": "API Reliability Issues",
                    "priority": "CRITICAL",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": "Request failures or timeouts",
                    "fixes": [
                        "Check Google API service status",
                        "Verify API key has correct permissions",
                        "Implement exponential backoff for retries",
                        "Add request timeout parameters",
                        "Monitor API quota usage",
                        "Consider rate limiting to avoid quota exhaustion"
                    ],
                    "estimated_impact": "Recovery of 100% of failed queries"
                })
            
            elif cause_name == "budget_limits":
                recommendations.append({
                    "issue": "Budget Limits Blocking Requests",
                    "priority": "MEDIUM",
                    "affected_queries": len(cause_data["cases"]),
                    "impact": "End-user visible failures or degradation",
                    "fixes": [
                        "Increase daily/monthly budget if sustainable",
                        "Use Flash model exclusively for cost reduction",
                        "Enable caching to reduce number of API calls",
                        "Implement request prioritization",
                        "Set up alerts before reaching budget limit"
                    ],
                    "estimated_impact": "Serve 100% of user requests"
                })
        
        return sorted(recommendations, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["priority"], 4))
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary."""
        
        if not self.results:
            return {"status": "no_data"}
        
        basic = self.results.get("basic", [])
        intelligent = self.results.get("intelligent", [])
        
        basic_success = sum(1 for r in basic if r.get("status") == "success")
        intell_success = sum(1 for r in intelligent if r.get("status") == "success")
        
        underperforming = self._find_underperformance()
        failures = self._analyze_failures()
        
        return {
            "total_queries": len(intelligent),
            "basic_success_rate": f"{basic_success/len(basic)*100:.1f}%",
            "intelligent_success_rate": f"{intell_success/len(intelligent)*100:.1f}%",
            "queries_underperforming": len(underperforming),
            "failure_cases": sum(f["count"] for f in failures),
            "overall_status": self._determine_status(basic_success, intell_success, len(underperforming)),
            "action_priority": self._prioritize_actions(failures, underperforming)
        }
    
    def _determine_status(self, basic_success: int, intell_success: int, underperf: int) -> str:
        """Determine overall status."""
        
        if intell_success < basic_success * 0.9:
            return "CRITICAL - Success rate degradation"
        elif underperf > intell_success * 0.2:
            return "WARNING - 20%+ queries underperforming"
        elif underperf > intell_success * 0.1:
            return "CAUTION - 10%+ queries underperforming"
        else:
            return "HEALTHY - Minor issues only"
    
    def _prioritize_actions(self, failures: List, underperf: List) -> List[str]:
        """Prioritize actions to take."""
        
        actions = []
        
        if failures:
            total_failures = sum(f["count"] for f in failures)
            if total_failures > 0:
                actions.append(f"FIX: {total_failures} API call failures - blocking users")
        
        if underperf:
            actions.append(f"OPTIMIZE: {len(underperf)} queries slower than baseline")
        
        if len(underperf) / max(len(underperf) + sum(1 for f in failures for _ in f["instances"]), 1) > 0.1:
            actions.append("REVIEW: Model selection strategy needs adjustment")
        
        if not actions:
            actions.append("MONITOR: System performing normally, track trends")
        
        return actions
    
    def export_analysis(self, filename: str = None) -> str:
        """Export analysis to file."""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/benchmarks/analysis_{timestamp}.json"
        
        analysis = self.analyze_all()
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return filename
    
    def print_analysis_report(self):
        """Print formatted analysis report."""
        
        analysis = self.analyze_all()
        
        if analysis.get("status") == "no_data":
            print("No benchmark data available for analysis")
            return
        
        print("\n" + "="*100)
        print("BENCHMARK FAILURE ANALYSIS REPORT")
        print("="*100)
        
        # Summary
        print("\nOVERALL SUMMARY")
        print("-" * 100)
        summary = analysis.get("summary", {})
        print(f"Total Queries Tested: {summary.get('total_queries')}")
        print(f"Basic Pipeline Success Rate: {summary.get('basic_success_rate')}")
        print(f"Intelligent System Success Rate: {summary.get('intelligent_success_rate')}")
        print(f"Queries Underperforming: {summary.get('queries_underperforming')}")
        print(f"Failure Cases: {summary.get('failure_cases')}")
        print(f"\nStatus: {summary.get('overall_status')}")
        
        print("\nACTION PRIORITY")
        print("-" * 100)
        for action in summary.get('action_priority', []):
            print(f"• {action}")
        
        # Worst performers
        worst = analysis.get("worst_performers", [])
        if worst:
            print("\n" + "-" * 100)
            print("WORST PERFORMING QUERIES")
            print("-" * 100)
            for item in worst[:5]:
                print(f"\nQuery #{item.get('query_id')}")
                print(f"  Issue Type: {item.get('issue_type')}")
                if item.get('latency_ms'):
                    print(f"  Latency: {item.get('latency_ms')}ms")
                if item.get('cost_usd'):
                    print(f"  Cost: ${item.get('cost_usd'):.4f}")
                if item.get('error'):
                    print(f"  Error: {item.get('error')}")
        
        # Underperformance
        underperf = analysis.get("intelligent_underperformance", [])
        if underperf:
            print("\n" + "-" * 100)
            print("INTELLIGENT SYSTEM UNDERPERFORMANCE")
            print("-" * 100)
            for case in underperf[:5]:
                print(f"\nQuery #{case.get('query_id')}: {len(case.get('issues', []))} issues")
                for issue in case.get('issues', []):
                    print(f"  • {issue.get('type')}")
                    if issue.get('regression_multiplier'):
                        print(f"    Regression: {issue.get('regression_pct'):.1f}% worse")
        
        # Failure analysis
        failures = analysis.get("failure_cases", [])
        if failures:
            print("\n" + "-" * 100)
            print("FAILURE ANALYSIS")
            print("-" * 100)
            for failure in failures:
                print(f"\n{failure.get('error_type').upper()}")
                print(f"  Occurrences: {failure.get('count')}")
                print(f"  Percentage: {failure.get('percentage'):.1f}%")
                print(f"  Possible Causes:")
                for cause in failure.get('possible_causes', []):
                    print(f"    • {cause}")
        
        # Root causes
        root_causes = analysis.get("root_causes", {})
        if root_causes:
            print("\n" + "-" * 100)
            print("ROOT CAUSE ANALYSIS")
            print("-" * 100)
            for cause_name, cause_data in root_causes.items():
                if cause_data.get("frequency", 0) > 0:
                    print(f"\n{cause_data.get('description')}")
                    print(f"  Frequency: {cause_data.get('frequency')} instances")
                    print(f"  Impact: {cause_data.get('impact')}")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            print("\n" + "="*100)
            print("RECOMMENDATIONS FOR IMPROVEMENT")
            print("="*100)
            
            for i, rec in enumerate(recommendations, 1):
                priority = rec.get("priority", "LOW")
                print(f"\n[{priority}] {i}. {rec.get('issue')}")
                print(f"   Affected: {rec.get('affected_queries')} queries")
                print(f"   Impact: {rec.get('estimated_impact')}")
                print(f"   Fixes:")
                for fix in rec.get('fixes', []):
                    print(f"      • {fix}")
        
        print("\n" + "="*100)
