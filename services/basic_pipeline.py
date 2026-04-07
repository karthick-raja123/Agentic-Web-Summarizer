"""
Basic LLM Pipeline - Control/Baseline for Benchmarking
=======================================================

This is a simple, unoptimized pipeline used as a baseline for comparison.
It represents typical usage without intelligent optimization.
"""

import time
import json
import google.generativeai as genai
from typing import Dict, Any
from datetime import datetime


class BasicLLMPipeline:
    """Unoptimized baseline pipeline for comparison."""
    
    # Fixed pricing (as of 2024)
    PRICING = {
        "gemini-2.5-flash": {
            "input": 0.075 / 1_000_000,      # $0.075 per 1M input tokens
            "output": 0.3 / 1_000_000        # $0.3 per 1M output tokens
        },
        "gemini-2.5-pro": {
            "input": 1.5 / 1_000_000,        # $1.5 per 1M input tokens
            "output": 4.5 / 1_000_000        # $4.5 per 1M output tokens
        }
    }
    
    def __init__(self, api_key: str):
        """Initialize basic pipeline."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.calls_made = 0
        self.total_cost = 0
    
    def summarize(self, content: str, max_length: int = 5) -> Dict[str, Any]:
        """Summarize content - basic approach."""
        start_time = time.time()
        start_timestamp = datetime.now()
        
        try:
            # Direct API call - no optimization
            response = self.model.generate_content(
                f"Summarize in {max_length} sentences:\n\n{content}"
            )
            
            latency = time.time() - start_time
            
            # Extract metrics
            summary = response.text
            input_tokens = len(content.split()) * 1.3  # Approximate
            output_tokens = len(summary.split()) * 1.3  # Approximate
            
            # Calculate cost
            model_name = "gemini-2.5-flash"
            cost = (
                input_tokens * self.PRICING[model_name]["input"] +
                output_tokens * self.PRICING[model_name]["output"]
            )
            
            self.calls_made += 1
            self.total_cost += cost
            
            return {
                "status": "success",
                "summary": summary,
                "model": model_name,
                "source": "api",  # Always API, no cache
                "latency_ms": int(latency * 1000),
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens),
                "cost_usd": cost,
                "timestamp": start_timestamp.isoformat(),
                "metadata": {
                    "pipeline": "basic",
                    "optimization": "none",
                    "cache_used": False
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": start_timestamp.isoformat(),
                "metadata": {
                    "pipeline": "basic"
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic pipeline statistics."""
        return {
            "calls_made": self.calls_made,
            "total_cost_usd": self.total_cost,
            "avg_cost_per_call": self.total_cost / self.calls_made if self.calls_made > 0 else 0,
            "pipeline": "basic",
            "optimization_level": "none"
        }


class BasicPipelineOptimized(BasicLLMPipeline):
    """Slightly optimized version using pro model when needed."""
    
    def summarize(self, content: str, max_length: int = 5, quality_threshold: float = 0.8) -> Dict[str, Any]:
        """Summarize - with basic quality check."""
        start_time = time.time()
        start_timestamp = datetime.now()
        
        try:
            # Simple heuristic: use pro model for long content
            content_length = len(content)
            model_name = "gemini-2.5-pro" if content_length > 2000 else "gemini-2.5-flash"
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content(
                f"Summarize in {max_length} sentences:\n\n{content}"
            )
            
            latency = time.time() - start_time
            
            summary = response.text
            input_tokens = len(content.split()) * 1.3
            output_tokens = len(summary.split()) * 1.3
            
            cost = (
                input_tokens * self.PRICING[model_name]["input"] +
                output_tokens * self.PRICING[model_name]["output"]
            )
            
            self.calls_made += 1
            self.total_cost += cost
            
            return {
                "status": "success",
                "summary": summary,
                "model": model_name,
                "source": "api",
                "latency_ms": int(latency * 1000),
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens),
                "cost_usd": cost,
                "timestamp": start_timestamp.isoformat(),
                "metadata": {
                    "pipeline": "basic_optimized",
                    "optimization": "heuristic_model_selection",
                    "model_decision": f"pro" if content_length > 2000 else "flash"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": start_timestamp.isoformat(),
                "metadata": {
                    "pipeline": "basic_optimized"
                }
            }
