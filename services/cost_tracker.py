"""
Cost Control & Token Management - Track and limit API usage dynamically.
Monitors token consumption and enforces budget limits intelligently.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json


class TokenPricingTier(Enum):
    """Pricing tiers for models"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ModelPricing:
    """Pricing information for models"""
    
    # Pricing in USD per 1M tokens (approximate as of 2024)
    PRICING = {
        "gemini-2.5-flash": {
            "input_per_1m": 0.075,      # $0.075 per 1M input tokens
            "output_per_1m": 0.30,     # $0.30 per 1M output tokens
            "tier": TokenPricingTier.BASIC
        },
        "gemini-2.5-pro": {
            "input_per_1m": 0.30,
            "output_per_1m": 1.20,
            "tier": TokenPricingTier.PRO
        },
        "gemini-flash-latest": {
            "input_per_1m": 0.075,
            "output_per_1m": 0.30,
            "tier": TokenPricingTier.BASIC
        },
        "gemini-pro-latest": {
            "input_per_1m": 0.30,
            "output_per_1m": 1.20,
            "tier": TokenPricingTier.PRO
        }
    }


class CostTracker:
    """
    Tracks API costs and enforces budget limits.
    Provides intelligent cost optimization recommendations.
    """
    
    def __init__(
        self,
        daily_budget_usd: float = 10.0,
        monthly_budget_usd: float = 200.0,
        warning_threshold_pct: float = 80.0
    ):
        """
        Initialize cost tracker.
        
        Args:
            daily_budget_usd: Daily budget limit
            monthly_budget_usd: Monthly budget limit
            warning_threshold_pct: Alert when this % of budget is used
        """
        self.daily_budget = daily_budget_usd
        self.monthly_budget = monthly_budget_usd
        self.warning_threshold = warning_threshold_pct
        
        # Tracking
        self.usage_log = []  # List of usage entries
        self.daily_usage = {}  # Date -> cost mapping
        self.monthly_usage = {}  # Month -> cost mapping
        
        self.alerts = []  # Alert history
    
    def estimate_tokens(self, text: str, token_ratio: float = 0.25) -> int:
        """
        Estimate token count from text.
        Rough estimate: ~4 characters per token.
        
        Args:
            text: Input text
            token_ratio: Estimation ratio (default 0.25 = 1 token per 4 chars)
            
        Returns:
            Estimated token count
        """
        return max(1, int(len(text) * token_ratio))
    
    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Estimate cost of API call.
        
        Args:
            model: Model name
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens
            
        Returns:
            Tuple of (total_cost, breakdown)
        """
        if model not in ModelPricing.PRICING:
            return 0.0, {}
        
        pricing = ModelPricing.PRICING[model]
        
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
        total_cost = input_cost + output_cost
        
        breakdown = {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
        
        return total_cost, breakdown
    
    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str = "unknown"
    ) -> Dict[str, any]:
        """
        Record API usage.
        
        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens consumed
            task_type: Type of task
            
        Returns:
            Usage record with cost and status
        """
        cost, breakdown = self.estimate_cost(model, input_tokens, output_tokens)
        
        today = datetime.now().date().isoformat()
        this_month = datetime.now().strftime("%Y-%m")
        
        # Update tracking
        self.daily_usage[today] = self.daily_usage.get(today, 0) + cost
        self.monthly_usage[this_month] = self.monthly_usage.get(this_month, 0) + cost
        
        usage_record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "cost": cost,
            "breakdown": breakdown,
            "task_type": task_type,
            "daily_total": self.daily_usage[today],
            "monthly_total": self.monthly_usage[this_month],
            "daily_budget_used_pct": (self.daily_usage[today] / self.daily_budget) * 100,
            "monthly_budget_used_pct": (self.monthly_usage[this_month] / self.monthly_budget) * 100
        }
        
        self.usage_log.append(usage_record)
        
        # Check limits and generate alerts
        self._check_limits(usage_record)
        
        return usage_record
    
    def _check_limits(self, record: Dict):
        """Check if usage limits exceeded and generate alerts"""
        
        # Daily limit check
        if record["daily_budget_used_pct"] >= 100:
            self._create_alert(
                "CRITICAL",
                f"Daily budget exceeded: ${record['daily_total']:.2f} / ${self.daily_budget:.2f}",
                "DAILY_LIMIT_EXCEEDED"
            )
        elif record["daily_budget_used_pct"] >= self.warning_threshold:
            self._create_alert(
                "WARNING",
                f"Daily budget {record['daily_budget_used_pct']:.1f}% used",
                "DAILY_LIMIT_WARNING"
            )
        
        # Monthly limit check
        if record["monthly_budget_used_pct"] >= 100:
            self._create_alert(
                "CRITICAL",
                f"Monthly budget exceeded: ${record['monthly_total']:.2f} / ${self.monthly_budget:.2f}",
                "MONTHLY_LIMIT_EXCEEDED"
            )
        elif record["monthly_budget_used_pct"] >= self.warning_threshold:
            self._create_alert(
                "WARNING",
                f"Monthly budget {record['monthly_budget_used_pct']:.1f}% used",
                "MONTHLY_LIMIT_WARNING"
            )
    
    def _create_alert(self, level: str, message: str, alert_type: str):
        """Create an alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "type": alert_type
        }
        self.alerts.append(alert)
    
    def can_continue(self, model: str, input_text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if we can afford next API call.
        
        Args:
            model: Model to use
            input_text: Input text
            
        Returns:
            Tuple of (can_continue, reason_if_no)
        """
        today = datetime.now().date().isoformat()
        this_month = datetime.now().strftime("%Y-%m")
        
        daily_used = self.daily_usage.get(today, 0)
        monthly_used = self.monthly_usage.get(this_month, 0)
        
        # Estimate cost
        input_tokens = self.estimate_tokens(input_text)
        # Rough estimate: output is usually 50% of input for summaries
        output_tokens = int(input_tokens * 0.5)
        
        estimated_cost, _ = self.estimate_cost(model, input_tokens, output_tokens)
        
        # Check limits
        if daily_used + estimated_cost > self.daily_budget:
            return False, f"Daily budget limit would be exceeded (${daily_used + estimated_cost:.2f})"
        
        if monthly_used + estimated_cost > self.monthly_budget:
            return False, f"Monthly budget limit would be exceeded (${monthly_used + estimated_cost:.2f})"
        
        return True, None
    
    def get_cost_breakdown(self) -> Dict[str, any]:
        """Get detailed cost breakdown"""
        
        today = datetime.now().date().isoformat()
        this_month = datetime.now().strftime("%Y-%m")
        
        daily_used = self.daily_usage.get(today, 0)
        monthly_used = self.monthly_usage.get(this_month, 0)
        
        # Group by model
        by_model = {}
        for record in self.usage_log:
            model = record["model"]
            if model not in by_model:
                by_model[model] = {"count": 0, "cost": 0, "tokens": 0}
            by_model[model]["count"] += 1
            by_model[model]["cost"] += record["breakdown"]["total_cost"]
            by_model[model]["tokens"] += (
                record["breakdown"]["input_tokens"] +
                record["breakdown"]["output_tokens"]
            )
        
        return {
            "total_calls": len(self.usage_log),
            "total_cost": sum(r["cost"] for r in self.usage_log),
            "daily_used": daily_used,
            "daily_budget": self.daily_budget,
            "daily_remaining": max(0, self.daily_budget - daily_used),
            "daily_pct_used": (daily_used / self.daily_budget) * 100,
            "monthly_used": monthly_used,
            "monthly_budget": self.monthly_budget,
            "monthly_remaining": max(0, self.monthly_budget - monthly_used),
            "monthly_pct_used": (monthly_used / self.monthly_budget) * 100,
            "by_model": by_model,
            "recent_alerts": self.alerts[-5:]  # Last 5 alerts
        }
    
    def get_optimization_recommendations(self) -> list:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        # Analyze usage patterns
        if not self.usage_log:
            return recommendations
        
        # Check if using expensive models unnecessarily
        expensive_count = sum(
            1 for r in self.usage_log
            if "pro" in r["model"].lower()
        )
        
        if expensive_count > len(self.usage_log) * 0.5:
            recommendations.append({
                "title": "High Premium Model Usage",
                "description": f"{expensive_count} of {len(self.usage_log)} calls used pro models",
                "savings_potential": "Use flash model for simple tasks - potential 75% savings",
                "priority": "HIGH"
            })
        
        # Check cache hit rate
        # (This would be populated if integrated with cache)
        
        # Check for burst usage
        last_7_days = {}
        now = datetime.now()
        
        for record in self.usage_log:
            timestamp = datetime.fromisoformat(record["timestamp"])
            day = (now - timestamp).days
            if day <= 7:
                date_key = (now - timedelta(days=day)).date().isoformat()
                last_7_days[date_key] = last_7_days.get(date_key, 0) + record["cost"]
        
        if last_7_days:
            daily_avg = sum(last_7_days.values()) / len(last_7_days)
            max_daily = max(last_7_days.values())
            
            if max_daily > daily_avg * 1.5:
                recommendations.append({
                    "title": "Uneven Usage Pattern",
                    "description": "Some days show 50%+ higher usage than average",
                    "savings_potential": "Optimize workflows to distribute load evenly",
                    "priority": "MEDIUM"
                })
        
        return recommendations
