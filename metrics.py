"""
📊 Metrics Collection & Analysis Module
Tracks latency, token usage, and success rates for the summarization system
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class LatencyMetrics:
    """Track timing for different pipeline stages"""
    search_time: float = 0.0          # Time for web search
    scrape_time: float = 0.0          # Time for content scraping
    rank_time: float = 0.0            # Time for ranking content
    deduplicate_time: float = 0.0     # Time for deduplication
    summarize_time: float = 0.0       # Time for summarization
    reflection_time: float = 0.0      # Time for reflection/quality check
    total_time: float = 0.0           # Total end-to-end time
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TokenMetrics:
    """Estimate and track token usage"""
    input_tokens: int = 0             # Tokens in input
    output_tokens: int = 0            # Tokens in output
    search_query_tokens: int = 0      # Tokens from search expansion
    content_tokens: int = 0           # Tokens from scraped content
    total_tokens: int = 0             # Total tokens used
    estimated_cost: float = 0.0       # Estimated cost in USD
    
    def to_dict(self):
        return asdict(self)

@dataclass
class SuccessMetrics:
    """Track success and failure rates"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timed_out_requests: int = 0
    quality_passes: int = 0           # Requests that met quality threshold
    quality_fails: int = 0            # Requests that failed quality check
    
    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
    
    @property
    def quality_pass_rate(self) -> float:
        qualified = self.quality_passes + self.quality_fails
        return (self.quality_passes / qualified * 100) if qualified > 0 else 0.0
    
    def to_dict(self):
        d = asdict(self)
        d['success_rate'] = self.success_rate
        d['quality_pass_rate'] = self.quality_pass_rate
        return d

@dataclass
class RequestMetrics:
    """Complete metrics for a single request"""
    request_id: str
    timestamp: str                    # ISO format timestamp
    query: str                        # The user query
    request_type: str                 # 'web' or 'pdf'
    latency: LatencyMetrics
    tokens: TokenMetrics
    quality_score: float = 0.0        # Output quality (0.0-1.0)
    sources_used: int = 0             # Number of sources
    status: str = "pending"           # pending, success, failed
    error_message: Optional[str] = None
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'timestamp': self.timestamp,
            'query': self.query,
            'request_type': self.request_type,
            'latency': self.latency.to_dict(),
            'tokens': self.tokens.to_dict(),
            'quality_score': self.quality_score,
            'sources_used': self.sources_used,
            'status': self.status,
            'error_message': self.error_message
        }

# ============================================================================
# METRICS COLLECTOR
# ============================================================================

class MetricsCollector:
    """Collect and aggregate metrics throughout the pipeline"""
    
    def __init__(self, storage_path: str = "metrics_data.json"):
        self.storage_path = Path(storage_path)
        self.metrics_data: Dict[str, RequestMetrics] = {}
        self.aggregate_metrics = SuccessMetrics()
        self._load_from_storage()
    
    def _load_from_storage(self):
        """Load historical metrics from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Reconstruct RequestMetrics objects
                    for req_id, req_data in data.get('requests', {}).items():
                        try:
                            latency = LatencyMetrics(**req_data['latency'])
                            tokens = TokenMetrics(**req_data['tokens'])
                            rm = RequestMetrics(
                                request_id=req_data['request_id'],
                                timestamp=req_data['timestamp'],
                                query=req_data['query'],
                                request_type=req_data['request_type'],
                                latency=latency,
                                tokens=tokens,
                                quality_score=req_data.get('quality_score', 0.0),
                                sources_used=req_data.get('sources_used', 0),
                                status=req_data.get('status', 'pending'),
                                error_message=req_data.get('error_message')
                            )
                            self.metrics_data[req_id] = rm
                        except Exception as e:
                            logger.warning(f"Could not reconstruct metrics for {req_id}: {e}")
                    
                    # Reconstruct aggregate metrics
                    agg_data = data.get('aggregate', {})
                    self.aggregate_metrics = SuccessMetrics(**agg_data)
                    logger.info(f"Loaded {len(self.metrics_data)} historical metrics")
            except Exception as e:
                logger.warning(f"Could not load metrics from storage: {e}")
    
    def _save_to_storage(self):
        """Save metrics to file"""
        try:
            data = {
                'requests': {
                    req_id: metrics.to_dict()
                    for req_id, metrics in self.metrics_data.items()
                },
                'aggregate': self.aggregate_metrics.to_dict(),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metrics: {e}")
    
    def start_request(self, request_id: str, query: str, request_type: str = "web") -> RequestMetrics:
        """Start tracking a new request"""
        metrics = RequestMetrics(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            query=query,
            request_type=request_type,
            latency=LatencyMetrics(),
            tokens=TokenMetrics()
        )
        self.metrics_data[request_id] = metrics
        return metrics
    
    def record_search_time(self, request_id: str, duration: float):
        """Record time spent on web search"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.search_time = duration
    
    def record_scrape_time(self, request_id: str, duration: float):
        """Record time spent scraping content"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.scrape_time = duration
    
    def record_rank_time(self, request_id: str, duration: float):
        """Record time spent ranking content"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.rank_time = duration
    
    def record_deduplicate_time(self, request_id: str, duration: float):
        """Record time spent deduplicating content"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.deduplicate_time = duration
    
    def record_summarize_time(self, request_id: str, duration: float):
        """Record time spent summarizing"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.summarize_time = duration
    
    def record_reflection_time(self, request_id: str, duration: float):
        """Record time spent on quality reflection"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.reflection_time = duration
    
    def record_total_time(self, request_id: str, duration: float):
        """Record total end-to-end time"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].latency.total_time = duration
    
    def record_token_usage(self, request_id: str, input_tokens: int, output_tokens: int, 
                          search_tokens: int = 0, content_tokens: int = 0):
        """Record token usage estimates"""
        if request_id in self.metrics_data:
            tokens = self.metrics_data[request_id].tokens
            tokens.input_tokens = input_tokens
            tokens.output_tokens = output_tokens
            tokens.search_query_tokens = search_tokens
            tokens.content_tokens = content_tokens
            tokens.total_tokens = input_tokens + output_tokens + search_tokens + content_tokens
            
            # Estimate cost (example: GPT-4 pricing)
            # $0.03 per 1K input tokens, $0.06 per 1K output tokens
            tokens.estimated_cost = (input_tokens * 0.00003) + (output_tokens * 0.00006)
    
    def record_success(self, request_id: str, quality_score: float, sources_used: int):
        """Record successful request"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].status = "success"
            self.metrics_data[request_id].quality_score = quality_score
            self.metrics_data[request_id].sources_used = sources_used
        
        self.aggregate_metrics.total_requests += 1
        self.aggregate_metrics.successful_requests += 1
        
        # Track quality pass rate
        if quality_score > 0.6:
            self.aggregate_metrics.quality_passes += 1
        else:
            self.aggregate_metrics.quality_fails += 1
        
        self._save_to_storage()
    
    def record_failure(self, request_id: str, error_message: str = None, is_timeout: bool = False):
        """Record failed request"""
        if request_id in self.metrics_data:
            self.metrics_data[request_id].status = "failed"
            self.metrics_data[request_id].error_message = error_message
        
        self.aggregate_metrics.total_requests += 1
        self.aggregate_metrics.failed_requests += 1
        
        if is_timeout:
            self.aggregate_metrics.timed_out_requests += 1
        
        self._save_to_storage()
    
    def get_metrics(self, request_id: str) -> Optional[RequestMetrics]:
        """Get metrics for a specific request"""
        return self.metrics_data.get(request_id)
    
    def get_aggregate_metrics(self) -> SuccessMetrics:
        """Get aggregate metrics across all requests"""
        return self.aggregate_metrics
    
    def get_recent_metrics(self, hours: int = 24) -> List[RequestMetrics]:
        """Get metrics from recent requests"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for metrics in self.metrics_data.values():
            try:
                metric_time = datetime.fromisoformat(metrics.timestamp)
                if metric_time > cutoff_time:
                    recent.append(metrics)
            except:
                pass
        
        return recent
    
    def get_performance_summary(self, hours: int = 24) -> Dict:
        """Get comprehensive performance summary"""
        recent = self.get_recent_metrics(hours)
        
        if not recent:
            return {
                'period_hours': hours,
                'total_requests': 0,
                'success_rate': 0.0,
                'avg_latency': 0.0,
                'avg_tokens': 0,
                'avg_quality': 0.0
            }
        
        # Calculate averages
        total_times = [m.latency.total_time for m in recent if m.latency.total_time > 0]
        search_times = [m.latency.search_time for m in recent if m.latency.search_time > 0]
        scrape_times = [m.latency.scrape_time for m in recent if m.latency.scrape_time > 0]
        summarize_times = [m.latency.summarize_time for m in recent if m.latency.summarize_time > 0]
        token_counts = [m.tokens.total_tokens for m in recent if m.tokens.total_tokens > 0]
        quality_scores = [m.quality_score for m in recent if m.status == "success"]
        success_count = sum(1 for m in recent if m.status == "success")
        
        return {
            'period_hours': hours,
            'total_requests': len(recent),
            'success_rate': (success_count / len(recent) * 100) if recent else 0.0,
            'avg_latency_seconds': statistics.mean(total_times) if total_times else 0.0,
            'median_latency_seconds': statistics.median(total_times) if total_times else 0.0,
            'avg_search_time': statistics.mean(search_times) if search_times else 0.0,
            'avg_scrape_time': statistics.mean(scrape_times) if scrape_times else 0.0,
            'avg_summarize_time': statistics.mean(summarize_times) if summarize_times else 0.0,
            'avg_tokens': statistics.mean(token_counts) if token_counts else 0,
            'total_tokens': sum(token_counts),
            'avg_quality_score': statistics.mean(quality_scores) if quality_scores else 0.0,
            'request_types': self._count_by_type(recent),
            'status_distribution': self._count_by_status(recent)
        }
    
    def _count_by_type(self, metrics_list: List[RequestMetrics]) -> Dict[str, int]:
        """Count metrics by request type"""
        counts = defaultdict(int)
        for m in metrics_list:
            counts[m.request_type] += 1
        return dict(counts)
    
    def _count_by_status(self, metrics_list: List[RequestMetrics]) -> Dict[str, int]:
        """Count metrics by status"""
        counts = defaultdict(int)
        for m in metrics_list:
            counts[m.status] += 1
        return dict(counts)
    
    def export_metrics(self, filepath: str = "metrics_export.json"):
        """Export metrics to JSON file"""
        try:
            data = {
                'exported_at': datetime.now().isoformat(),
                'summary': self.get_performance_summary(hours=24),
                'aggregate': self.aggregate_metrics.to_dict(),
                'requests': [m.to_dict() for m in list(self.metrics_data.values())[-100:]]  # Last 100
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Metrics exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Could not export metrics: {e}")
            return None

# ============================================================================
# TOKEN ESTIMATOR
# ============================================================================

class TokenEstimator:
    """Estimate token usage for various inputs"""
    
    # Rough token counting (1 token ≈ 4 characters for English)
    CHARS_PER_TOKEN = 4.0
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        return max(1, len(text) // int(TokenEstimator.CHARS_PER_TOKEN))
    
    @staticmethod
    def estimate_query_expansion(original_query: str, expanded_count: int = 3) -> int:
        """Estimate tokens for query expansion"""
        # Original query + expanded queries (assume each is ~1.5x original)
        base_tokens = TokenEstimator.estimate_tokens(original_query)
        return base_tokens + (base_tokens * 15 // 10 * expanded_count)
    
    @staticmethod
    def estimate_content_tokens(scraped_content: List[Dict]) -> int:
        """Estimate tokens from scraped content"""
        total = 0
        for item in scraped_content:
            if isinstance(item, dict) and 'content' in item:
                total += TokenEstimator.estimate_tokens(item['content'])
        return total
    
    @staticmethod
    def estimate_output_tokens(summary: str, bullet_points: List[str] = None) -> int:
        """Estimate tokens for output"""
        tokens = TokenEstimator.estimate_tokens(summary)
        if bullet_points:
            tokens += sum(TokenEstimator.estimate_tokens(bp) for bp in bullet_points)
        return tokens

# ============================================================================
# GLOBAL METRICS INSTANCE
# ============================================================================

# Create a global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def configure_metrics(storage_path: str = "metrics_data.json"):
    """Configure metrics collector with custom path"""
    global _metrics_collector
    _metrics_collector = MetricsCollector(storage_path=storage_path)
