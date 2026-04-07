"""
Adaptive Learning System for Intelligent Model Selection
=========================================================

Learns from past performance and improves decisions over time.
Stores historical data and adjusts model selection weights dynamically.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import numpy as np


class AdaptiveLearningSystem:
    """
    Learns from query performance history and optimizes model selection.
    
    Features:
    - Track performance across different query types
    - Learn which model works best for different scenarios
    - Adjust weights dynamically based on results
    - Provide recommendations for future queries
    """
    
    def __init__(self, history_file: str = "data/learning_history.json"):
        """Initialize learning system."""
        self.history_file = history_file
        self.history = self._load_history()
        self.model_performance = self._calculate_performance()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load historical data."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """Save history to file."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def record_query(self, query: str, result: Dict[str, Any], 
                    quality_score: float, category: str = "general"):
        """Record query and its results for learning."""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "query_length": len(query),
            "category": category,
            "model_used": result.get("model", "unknown"),
            "latency_ms": result.get("latency_ms", 0),
            "cost_usd": result.get("cost_usd", 0),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "quality_score": quality_score,
            "source": result.get("source", "api"),
            "success": result.get("status") == "success"
        }
        
        self.history.append(entry)
        self._save_history()
        self.model_performance = self._calculate_performance()
    
    def _calculate_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance metrics by model."""
        performance = defaultdict(lambda: {
            "count": 0,
            "avg_latency": 0,
            "avg_cost": 0,
            "avg_quality": 0,
            "success_rate": 0,
            "cache_hit_rate": 0,
            "by_category": defaultdict(dict)
        })
        
        if not self.history:
            return performance
        
        for entry in self.history:
            model = entry.get("model_used", "unknown")
            perf = performance[model]
            
            perf["count"] += 1
            perf["avg_latency"] = (perf["avg_latency"] * (perf["count"]-1) + 
                                  entry["latency_ms"]) / perf["count"]
            perf["avg_cost"] = (perf["avg_cost"] * (perf["count"]-1) + 
                               entry["cost_usd"]) / perf["count"]
            perf["avg_quality"] = (perf["avg_quality"] * (perf["count"]-1) + 
                                  entry["quality_score"]) / perf["count"]
            
            if entry["success"]:
                perf["success_rate"] = (perf.get("success_rate", 0) * (perf["count"]-1) + 1) / perf["count"]
            
            if entry["source"] == "cache":
                perf["cache_hit_rate"] = (perf.get("cache_hit_rate", 0) * (perf["count"]-1) + 1) / perf["count"]
        
        return dict(performance)
    
    def get_model_recommendation(self, query: str, priority: str = "balanced",
                               category: str = "general") -> Dict[str, Any]:
        """
        Get model recommendation based on learning history.
        
        Args:
            query: The query to process
            priority: "cost", "speed", "quality", or "balanced"
            category: Query category for better matching
        
        Returns:
            Recommendation with model and rationale
        """
        
        if not self.history:
            # Default recommendations if no history yet
            if priority == "cost":
                return {"model": "gemini-2.5-flash", "confidence": 0.5, "reason": "No history yet, using efficient model"}
            elif priority == "speed":
                return {"model": "gemini-2.5-flash", "reason": "Flash is fastest"}
            else:  # quality or balanced
                return {"model": "gemini-2.5-pro", "confidence": 0.5, "reason": "No history yet, using capable model"}
        
        # Analyze query characteristics
        query_length = len(query)
        
        # Get historical performance for this category
        category_history = [e for e in self.history if e["category"] == category]
        if not category_history:
            category_history = self.history
        
        # Score models based on priority
        scores = {}
        for model, perf in self.model_performance.items():
            if perf["count"] == 0:
                continue
            
            # Normalize metrics (0-100)
            quality_score = perf["avg_quality"] * 100
            speed_score = 100 - min(perf["avg_latency"] / 20, 100)  # Normalize latency
            cost_score = 100 - min(perf["avg_cost"] / 0.01, 100)    # Normalize cost
            
            # Apply priority weights
            if priority == "cost":
                scores[model] = (cost_score * 0.7 + quality_score * 0.3) * perf["success_rate"]
            elif priority == "speed":
                scores[model] = (speed_score * 0.7 + quality_score * 0.3) * perf["success_rate"]
            elif priority == "quality":
                scores[model] = (quality_score * 0.7 + cost_score * 0.3) * perf["success_rate"]
            else:  # balanced
                scores[model] = ((quality_score * 0.4 + speed_score * 0.35 + cost_score * 0.25) * 
                               perf["success_rate"])
        
        if not scores:
            return {"model": "gemini-2.5-flash", "confidence": 0.5, "reason": "No historical data"}
        
        best_model = max(scores, key=scores[best_model])
        confidence = min(scores[best_model] / 100, 1.0)
        
        perf = self.model_performance[best_model]
        reasons = [
            f"Best {priority} score: {scores[best_model]:.1f}",
            f"Avg quality: {perf['avg_quality']:.1f}%",
            f"Avg latency: {perf['avg_latency']:.0f}ms",
            f"Avg cost: ${perf['avg_cost']:.4f}",
            f"Success rate: {perf['success_rate']*100:.0f}%"
        ]
        
        return {
            "model": best_model,
            "confidence": confidence,
            "reasoning": reasons,
            "scores": scores,
            "category": category,
            "based_on_queries": perf["count"]
        }
    
    def get_insights(self) -> Dict[str, Any]:
        """Generate insights from learning data."""
        if not self.history:
            return {"status": "no_data", "message": "Not enough historical data yet"}
        
        insights = {
            "total_queries": len(self.history),
            "timestamp": datetime.now().isoformat(),
            "model_stats": {},
            "best_performers": {},
            "recommendations": [],
            "trends": {}
        }
        
        # Model statistics
        for model, perf in self.model_performance.items():
            insights["model_stats"][model] = {
                "queries": perf["count"],
                "avg_quality": f"{perf['avg_quality']:.1f}%",
                "avg_latency": f"{perf['avg_latency']:.0f}ms",
                "avg_cost": f"${perf['avg_cost']:.4f}",
                "success_rate": f"{perf['success_rate']*100:.1f}%",
                "cache_hit_rate": f"{perf['cache_hit_rate']*100:.1f}%"
            }
        
        # Best performers by metric
        if self.model_performance:
            best_quality = max(self.model_performance.items(), 
                              key=lambda x: x[1]["avg_quality"])
            best_speed = min(self.model_performance.items(),
                            key=lambda x: x[1]["avg_latency"])
            best_cost = min(self.model_performance.items(),
                           key=lambda x: x[1]["avg_cost"])
            
            insights["best_performers"] = {
                "quality": best_quality[0],
                "speed": best_speed[0],
                "cost": best_cost[0]
            }
        
        # Generate recommendations
        cost_ratio = self.model_performance.get("gemini-2.5-pro", {}).get("avg_cost", 0) / max(
            self.model_performance.get("gemini-2.5-flash", {}).get("avg_cost", 1), 0.0001
        )
        
        if cost_ratio > 10:
            insights["recommendations"].append(
                "Pro model is significantly more expensive than Flash. "
                "Use Flash for most queries, Pro only for critical ones."
            )
        
        quality_diff = (self.model_performance.get("gemini-2.5-pro", {}).get("avg_quality", 0) -
                       self.model_performance.get("gemini-2.5-flash", {}).get("avg_quality", 0))
        
        if quality_diff < 5:
            insights["recommendations"].append(
                "Quality difference between models is minimal. "
                "Prefer Flash model for better cost-efficiency."
            )
        
        # Recent trends (last 10 queries)
        recent = self.history[-10:] if len(self.history) >= 10 else self.history
        if recent:
            avg_recent_cost = np.mean([e["cost_usd"] for e in recent])
            avg_overall_cost = np.mean([e["cost_usd"] for e in self.history])
            
            if avg_recent_cost > avg_overall_cost * 1.2:
                insights["trends"]["cost_increasing"] = True
                insights["recommendations"].append("Cost is increasing recently - review model selection")
        
        return insights
    
    def export_learning_data(self, filename: str = "data/learning_export.json"):
        """Export learning data for analysis."""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(self.history),
            "performance_summary": self.model_performance,
            "raw_history": self.history[-100:],  # Last 100 entries
            "insights": self.get_insights()
        }
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def clear_old_history(self, days: int = 30):
        """Remove entries older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        self.history = [
            e for e in self.history
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        
        self._save_history()
        self.model_performance = self._calculate_performance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self.history:
            return {}
        
        return {
            "total_queries": len(self.history),
            "total_cost": sum(e["cost_usd"] for e in self.history),
            "avg_quality": np.mean([e["quality_score"] for e in self.history]),
            "avg_latency": np.mean([e["latency_ms"] for e in self.history]),
            "success_rate": sum(1 for e in self.history if e["success"]) / len(self.history),
            "cache_hit_rate": sum(1 for e in self.history if e["source"] == "cache") / len(self.history),
            "date_range": {
                "start": self.history[0]["timestamp"],
                "end": self.history[-1]["timestamp"]
            }
        }
