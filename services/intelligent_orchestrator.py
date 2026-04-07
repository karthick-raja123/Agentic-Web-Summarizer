"""
Intelligent LLM Orchestrator - Coordinates smart model selection, caching, cost control, and evaluation.
This is the main service that clients interact with.
"""

import time
from typing import Dict, Optional, Any, Tuple
from dataclasses import asdict

from services.model_handler import ModelHandler
from services.smart_model_selector import SmartModelSelector, TaskType
from services.intelligent_cache import IntelligentCache
from services.cost_tracker import CostTracker
from services.quality_evaluator import QualityEvaluator
from config import Config


class IntelligentLLMOrchestrator:
    """
    Orchestrates all LLM operations with intelligence across the stack.
    Handles model selection, caching, cost control, and quality evaluation.
    """
    
    def __init__(
        self,
        daily_budget_usd: float = 10.0,
        monthly_budget_usd: float = 200.0,
        cache_enabled: bool = True,
        enable_evaluation: bool = True
    ):
        """
        Initialize orchestrator.
        
        Args:
            daily_budget_usd: Daily cost budget
            monthly_budget_usd: Monthly cost budget
            cache_enabled: Whether to use caching
            enable_evaluation: Whether to evaluate summary quality
        """
        
        # Initialize components
        self.model_handler = ModelHandler(Config.GOOGLE_API_KEY)
        
        available_models = self.model_handler.AVAILABLE_MODELS
        self.model_selector = SmartModelSelector(available_models)
        
        self.cache = IntelligentCache() if cache_enabled else None
        self.cache_enabled = cache_enabled
        
        self.cost_tracker = CostTracker(daily_budget_usd, monthly_budget_usd)
        self.enable_evaluation = enable_evaluation
        
        self.evaluator = QualityEvaluator() if enable_evaluation else None
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "total_cost": 0.0,
            "total_latency_ms": 0,
            "avg_quality_score": 0.0
        }
    
    def summarize(
        self,
        content: str,
        max_length: int = 5,
        priority: str = "speed",
        force_fresh: bool = False,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Intelligent summarization with smart model selection and caching.
        
        Args:
            content: Text to summarize
            max_length: Number of bullet points
            priority: "speed", "cost", or "quality"
            force_fresh: Skip cache and generate new summary
            debug: Return debug information
            
        Returns:
            Dict with summary, metadata, and performance stats
        """
        
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        # Try cache first
        if self.cache_enabled and not force_fresh:
            cached = self.cache.get(content, "summary", str(max_length))
            if cached:
                self.metrics["cache_hits"] += 1
                
                return {
                    "status": "success",
                    "summary": cached,
                    "source": "cache",
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "cost_usd": 0.0,
                    "metadata": {
                        "cache_hit": True,
                        "priority_used": "cache"
                    }
                }
        
        # Smart model selection
        selected_model, selection_info = self.model_selector.select_model(
            content_size=len(content),
            task_type=TaskType.SUMMARIZE,
            priority=priority
        )
        
        if debug:
            print(f"🤖 Selected model: {selected_model}")
            print(f"   Reason: {selection_info['reason']}")
            print(f"   Score: {selection_info['score']:.1f}")
        
        # Check budget
        can_afford, reason = self.cost_tracker.can_continue(selected_model, content)
        if not can_afford:
            return {
                "status": "budget_exceeded",
                "error": reason,
                "latency_ms": int((time.time() - start_time) * 1000),
                "metadata": {"reason": reason}
            }
        
        # Prepare prompt
        prompt = f"""Summarize the following text in exactly {max_length} concise bullet points.
Each bullet point should be clear and informative.
Make sure to capture the key insights.

Text:
{content}

Provide the summary as bullet points only (use • or - format)."""
        
        # Call API
        try:
            self.metrics["api_calls"] += 1
            
            model = self.model_handler.get_model(selected_model)[0]
            response = model.generate_content(prompt, stream=False)
            summary = response.text
            
            # Estimate tokens (for cost tracking)
            input_tokens = self.cost_tracker.estimate_tokens(content)
            output_tokens = self.cost_tracker.estimate_tokens(summary)
            
            # Track cost
            cost_record = self.cost_tracker.record_usage(
                selected_model,
                input_tokens,
                output_tokens,
                "summarization"
            )
            
            self.metrics["total_cost"] += cost_record["cost"]
            
            # Evaluate quality
            quality_metrics = None
            if self.enable_evaluation:
                quality_metrics = self.evaluator.evaluate_summary(
                    content, summary, len(content)
                )
                self.metrics["avg_quality_score"] = self.evaluator.get_evaluation_stats()["avg_overall_score"]
            
            # Cache if quality is good enough
            if self.cache_enabled and quality_metrics and quality_metrics.overall_score >= 70:
                self.cache.set(
                    content, summary, "summary", str(max_length),
                    metadata={
                        "model": selected_model,
                        "quality_score": quality_metrics.overall_score,
                        "priority": priority
                    }
                )
            
            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics["total_latency_ms"] += latency_ms
            
            result = {
                "status": "success",
                "summary": summary,
                "source": "api",
                "latency_ms": latency_ms,
                "cost_usd": cost_record["cost"],
                "model": selected_model,
                "metadata": {
                    "cache_hit": False,
                    "priority_used": priority,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "selection_score": selection_info["score"],
                    "selection_reason": selection_info["reason"]
                }
            }
            
            # Add quality metrics if available
            if quality_metrics:
                result["quality"] = {
                    "overall_score": quality_metrics.overall_score,
                    "completeness": quality_metrics.completeness_score,
                    "accuracy": quality_metrics.accuracy_score,
                    "coherence": quality_metrics.coherence_score,
                    "conciseness": quality_metrics.conciseness_score,
                    "topics_covered": quality_metrics.key_topics_covered,
                    "topics_total": quality_metrics.key_topics_total
                }
            
            # Add cost breakdown
            result["cost_breakdown"] = cost_record["breakdown"]
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "latency_ms": int((time.time() - start_time) * 1000),
                "model": selected_model,
                "metadata": {"error_type": type(e).__name__}
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics"""
        
        cache_stats = self.cache.get_stats() if self.cache_enabled else {}
        cost_breakdown = self.cost_tracker.get_cost_breakdown()
        model_stats = self.model_selector.get_selection_stats()
        eval_stats = self.evaluator.get_evaluation_stats() if self.enable_evaluation else {}
        
        return {
            "system": {
                "cache_enabled": self.cache_enabled,
                "cost_tracking_enabled": True,
                "evaluation_enabled": self.enable_evaluation
            },
            "metrics": {
                **self.metrics,
                "avg_latency_ms": self.metrics["total_latency_ms"] / max(1, self.metrics["api_calls"]),
                "cache_hit_rate": f"{(self.metrics['cache_hits'] / max(1, self.metrics['total_requests'])) * 100:.1f}%"
            },
            "cache": cache_stats,
            "costs": cost_breakdown,
            "model_selection": model_stats,
            "evaluation": eval_stats,
            "recommendations": self.cost_tracker.get_optimization_recommendations()
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Generate detailed performance and cost report"""
        
        status = self.get_system_status()
        cache_top = self.cache.get_top_cached_queries(5) if self.cache_enabled else []
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_requests": status["metrics"]["total_requests"],
                "api_calls": status["metrics"]["api_calls"],
                "cache_hits": status["metrics"]["cache_hits"],
                "total_cost_usd": f"${status['metrics']['total_cost']:.2f}",
                "cache_hit_rate": status["metrics"]["cache_hit_rate"],
                "avg_latency_ms": f"{status['metrics']['avg_latency_ms']:.0f}ms"
            },
            "cost_analysis": {
                "daily_budget": f"${status['costs']['daily_budget']:.2f}",
                "daily_used": f"${status['costs']['daily_used']:.2f}",
                "daily_remaining": f"${status['costs']['daily_remaining']:.2f}",
                "daily_pct_used": f"{status['costs']['daily_pct_used']:.1f}%",
                "monthly_budget": f"${status['costs']['monthly_budget']:.2f}",
                "monthly_used": f"${status['costs']['monthly_used']:.2f}",
                "monthly_remaining": f"${status['costs']['monthly_remaining']:.2f}",
                "monthly_pct_used": f"{status['costs']['monthly_pct_used']:.1f}%",
                "by_model": status['costs']['by_model']
            },
            "cache_analysis": {
                "entries": status["cache"].get("memory_entries", 0),
                "size_mb": f"{status['cache'].get('memory_size_mb', 0):.2f}",
                "hit_rate": status["cache"].get("hit_rate", "N/A"),
                "top_cached": cache_top
            },
            "model_usage": status["model_selection"],
            "quality_metrics": status["evaluation"],
            "optimization_opportunities": status["recommendations"]
        }
