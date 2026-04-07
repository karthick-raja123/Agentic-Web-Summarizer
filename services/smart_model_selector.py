"""
Smart Model Selection Engine - Intelligent model routing based on task characteristics.
Analyzes content size, complexity, and latency requirements to choose optimal model.
"""

import time
from enum import Enum
from typing import Tuple, Optional, Dict, Any
import google.generativeai as genai


class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = 1      # Simple summaries, quick lookups
    MEDIUM = 2      # Moderate analysis, general queries
    COMPLEX = 3     # Deep analysis, reasoning required
    PREMIUM = 4     # Advanced reasoning, multiple steps


class TaskType(Enum):
    """Types of tasks"""
    SUMMARIZE = "summarize"
    ANALYZE = "analyze"
    GENERATE = "generate"
    TRANSLATE = "translate"
    CODE = "code"


class ModelProfile:
    """Profile and characteristics of each model"""
    
    PROFILES = {
        "gemini-2.5-flash": {
            "speed": 1.0,           # Relative speed (1.0 = baseline)
            "cost": 0.05,           # Relative cost multiplier
            "capability": 7,        # Capability score (0-10)
            "max_tokens": 4096,     # Max output tokens
            "latency_ms": 500,      # Average latency in ms
            "throughput": "high",   # Request throughput
            "best_for": ["SUMMARIZE", "ANALYZE", "GENERATE"]
        },
        "gemini-2.5-pro": {
            "speed": 1.5,
            "cost": 0.15,
            "capability": 9,
            "max_tokens": 8192,
            "latency_ms": 1200,
            "throughput": "medium",
            "best_for": ["COMPLEX", "REASONING", "MULTI_STEP"]
        },
        "gemini-flash-latest": {
            "speed": 1.0,
            "cost": 0.05,
            "capability": 7,
            "max_tokens": 4096,
            "latency_ms": 500,
            "throughput": "high",
            "best_for": ["SUMMARIZE", "ANALYZE"]
        },
        "gemini-pro-latest": {
            "speed": 1.5,
            "cost": 0.15,
            "capability": 9,
            "max_tokens": 8192,
            "latency_ms": 1200,
            "throughput": "medium",
            "best_for": ["COMPLEX", "REASONING"]
        }
    }


class SmartModelSelector:
    """Intelligent model selection based on task characteristics"""
    
    def __init__(self, available_models: list):
        """
        Initialize selector with available models.
        
        Args:
            available_models: List of available model names
        """
        self.available_models = available_models
        self.selection_history = []
        self.cost_tracker = {}
        
    def select_model(
        self,
        content_size: int,
        task_type: TaskType = TaskType.SUMMARIZE,
        max_latency_ms: int = 5000,
        budget_tokens: int = 10000,
        priority: str = "speed"  # "speed", "cost", or "quality"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Select optimal model based on task characteristics.
        
        Args:
            content_size: Size of input content in characters
            task_type: Type of task to perform
            max_latency_ms: Maximum acceptable latency
            budget_tokens: Available token budget
            priority: Selection priority ("speed", "cost", or "quality")
            
        Returns:
            Tuple of (model_name, selection_info)
        """
        
        # Calculate task complexity
        complexity = self._calculate_complexity(content_size, task_type)
        
        # Score models based on criteria
        scores = {}
        for model_name in self.available_models:
            if model_name not in ModelProfile.PROFILES:
                continue
            
            profile = ModelProfile.PROFILES[model_name]
            score = self._calculate_score(
                model_name, profile, complexity, max_latency_ms,
                budget_tokens, priority, task_type
            )
            scores[model_name] = score
        
        # Select best model
        if not scores:
            best_model = self.available_models[0]
            scores[best_model] = 0
        else:
            best_model = max(scores, key=scores.get)
        
        selection_info = {
            "model": best_model,
            "complexity": complexity.name,
            "priority": priority,
            "score": scores.get(best_model, 0),
            "profile": ModelProfile.PROFILES.get(best_model, {}),
            "reason": self._explain_selection(best_model, complexity, priority)
        }
        
        # Track selection
        self.selection_history.append(selection_info)
        
        return best_model, selection_info
    
    def _calculate_complexity(self, content_size: int, task_type: TaskType) -> TaskComplexity:
        """Calculate task complexity based on content size and type"""
        
        # Size-based complexity
        if content_size < 500:
            base_complexity = TaskComplexity.SIMPLE
        elif content_size < 2000:
            base_complexity = TaskComplexity.MEDIUM
        elif content_size < 5000:
            base_complexity = TaskComplexity.COMPLEX
        else:
            base_complexity = TaskComplexity.PREMIUM
        
        # Task type modifiers
        complex_tasks = [TaskType.ANALYZE, TaskType.GENERATE, TaskType.CODE]
        if task_type in complex_tasks:
            if base_complexity == TaskComplexity.SIMPLE:
                base_complexity = TaskComplexity.MEDIUM
            elif base_complexity in [TaskComplexity.MEDIUM, TaskComplexity.COMPLEX]:
                base_complexity = TaskComplexity.PREMIUM
        
        return base_complexity
    
    def _calculate_score(
        self, model_name: str, profile: Dict, complexity: TaskComplexity,
        max_latency: int, budget_tokens: int, priority: str, task_type: TaskType
    ) -> float:
        """Calculate selection score for model"""
        
        score = 0.0
        
        # Capability match (0-30 points)
        min_capability = 5 + (complexity.value * 1.5)
        if profile["capability"] >= min_capability:
            score += 30
        else:
            score += profile["capability"] * 3
        
        # Latency (0-25 points)
        if profile["latency_ms"] <= max_latency:
            score += 25 - (profile["latency_ms"] / max_latency) * 10
        else:
            score -= 50  # Penalty for exceeding latency
        
        # Cost (0-20 points)
        if priority == "cost":
            score += (1.0 / profile["cost"]) * 5
        else:
            score += 20 * (1.0 / profile["cost"])
        
        # Token budget (0-15 points)
        if profile["max_tokens"] >= budget_tokens:
            score += 15
        else:
            score += (profile["max_tokens"] / budget_tokens) * 15
        
        # Task fit (0-10 points)
        task_name = task_type.name.upper()
        if task_name in profile.get("best_for", []):
            score += 10
        
        # Priority weighting
        if priority == "speed":
            score += (1.0 / profile["speed"]) * 10
        elif priority == "quality":
            score += profile["capability"] * 2
        
        return score
    
    def _explain_selection(self, model: str, complexity: TaskComplexity, priority: str) -> str:
        """Generate explanation for model selection"""
        
        profile = ModelProfile.PROFILES.get(model, {})
        
        reasons = []
        if complexity.value <= 2 and profile["speed"] < 1.2:
            reasons.append("optimized for speed")
        if complexity.value >= 3 and profile["capability"] >= 8:
            reasons.append("high capability for complex task")
        if priority == "cost" and profile["cost"] < 0.10:
            reasons.append("cost-effective")
        
        return "; ".join(reasons) if reasons else "best overall fit"
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Get statistics on model selections"""
        
        if not self.selection_history:
            return {"total_selections": 0}
        
        model_counts = {}
        total_by_priority = {"speed": 0, "cost": 0, "quality": 0}
        total_by_complexity = {}
        
        for selection in self.selection_history:
            model = selection["model"]
            model_counts[model] = model_counts.get(model, 0) + 1
            total_by_priority[selection["priority"]] += 1
            
            complexity = selection["complexity"]
            total_by_complexity[complexity] = total_by_complexity.get(complexity, 0) + 1
        
        return {
            "total_selections": len(self.selection_history),
            "models_used": model_counts,
            "by_priority": total_by_priority,
            "by_complexity": total_by_complexity,
            "avg_score": sum(s["score"] for s in self.selection_history) / len(self.selection_history)
        }
