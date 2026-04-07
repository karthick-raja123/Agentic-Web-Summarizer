"""
Query Memory - Stores and retrieves previous queries and results.
Enables pattern recognition and faster responses.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
from utils.logging_config import get_logger

logger = get_logger(__name__)


class QueryMemory:
    """Persistent memory for queries and results."""
    
    def __init__(self, memory_dir: str = "query_memory"):
        """
        Initialize query memory.
        
        Args:
            memory_dir: Directory for storing query history
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        self.memory_file = self.memory_dir / "query_history.json"
        self.cache_file = self.memory_dir / "query_cache.json"
        
        self.memory = self._load_memory()
        self.cache = self._load_cache()
        
        logger.info(f"QueryMemory initialized - Stored {len(self.memory)} queries")
    
    def store_query(self, query: str, result: Dict, metadata: Dict = None) -> Dict:
        """
        Store query and its results in memory.
        
        Args:
            query: Search query
            result: Result dictionary
            metadata: Optional metadata (tags, category, etc)
            
        Returns:
            Storage confirmation
        """
        logger.info(f"Storing query in memory: '{query}'")
        
        store_entry = {
            "id": len(self.memory),
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result": {
                "status": result.get("status"),
                "summary_len": len(result.get("summary", "")),
                "urls_found": len(result.get("search_results", {}).get("results", []))
            },
            "metadata": metadata or {},
            "access_count": 0
        }
        
        self.memory.append(store_entry)
        self._save_memory()
        
        # Also cache for quick lookup
        query_lower = query.lower().strip()
        self.cache[query_lower] = {
            "full_result": result,
            "stored_at": datetime.now().isoformat(),
            "hits": 1
        }
        self._save_cache()
        
        logger.info(f"Query stored (ID: {store_entry['id']})")
        return {"status": "stored", "id": store_entry["id"]}
    
    def retrieve_similar_queries(self, query: str, similarity_threshold: float = 0.8, 
                                 days_back: int = 30) -> List[Dict]:
        """
        Find similar queries from memory.
        
        Args:
            query: Current query
            similarity_threshold: Minimum similarity (0-1)
            days_back: Look back N days
            
        Returns:
            List of similar queries from memory
        """
        logger.info(f"Searching for similar queries to: '{query}'")
        
        query_lower = query.lower().strip()
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        similar = []
        
        for entry in self.memory:
            # Check date range
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date < cutoff_date:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(query_lower, entry["query"].lower())
            
            if similarity >= similarity_threshold:
                entry["similarity_score"] = similarity
                similar.append(entry)
        
        # Sort by similarity score
        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(f"Found {len(similar)} similar queries above threshold {similarity_threshold}")
        return similar
    
    def get_cached_result(self, query: str) -> Optional[Dict]:
        """
        Get cached result for exact query match.
        
        Args:
            query: Query to look up
            
        Returns:
            Cached result or None
        """
        query_lower = query.lower().strip()
        
        if query_lower in self.cache:
            entry = self.cache[query_lower]
            entry["hits"] += 1
            self._save_cache()
            
            logger.info(f"Cache hit for query (hits: {entry['hits']})")
            return entry["full_result"]
        
        logger.debug(f"Cache miss for query: '{query}'")
        return None
    
    def get_frequently_searched(self, limit: int = 10) -> List[Dict]:
        """
        Get most frequently searched queries.
        
        Args:
            limit: Number of top queries to return
            
        Returns:
            List of top queries
        """
        # Get cache hits
        sorted_cache = sorted(
            self.cache.items(),
            key=lambda x: x[1].get("hits", 0),
            reverse=True
        )
        
        top_queries = [
            {"query": q, "hits": entry.get("hits", 0)}
            for q, entry in sorted_cache[:limit]
        ]
        
        logger.info(f"Top {len(top_queries)} frequently searched queries retrieved")
        return top_queries
    
    def get_memory_stats(self) -> Dict:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_queries = len(self.memory)
        cached_queries = len(self.cache)
        total_hits = sum(entry.get("hits", 0) for entry in self.cache.values())
        
        # Calculate success rate
        successful = sum(1 for entry in self.memory if entry["result"]["status"] == "success")
        success_rate = (successful / total_queries * 100) if total_queries > 0 else 0
        
        stats = {
            "total_stored_queries": total_queries,
            "cached_queries": cached_queries,
            "total_cache_hits": total_hits,
            "success_rate": success_rate,
            "memory_file_size": self.memory_file.stat().st_size if self.memory_file.exists() else 0
        }
        
        logger.info(f"Memory stats: {total_queries} queries, {success_rate:.1f}% success rate")
        return stats
    
    def clear_old_entries(self, days: int = 90) -> int:
        """
        Remove entries older than N days.
        
        Args:
            days: Age threshold
            
        Returns:
            Number of entries removed
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.memory)
        
        self.memory = [
            entry for entry in self.memory
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
        ]
        
        removed = original_count - len(self.memory)
        self._save_memory()
        
        logger.info(f"Cleared {removed} entries older than {days} days")
        return removed
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate similarity between two queries.
        Simple implementation using common words.
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(query1.split())
        words2 = set(query2.split())
        
        if not words1 or not words2:
            return 0.0
        
        common = len(words1 & words2)
        total = len(words1 | words2)
        
        return common / total if total > 0 else 0.0
    
    def _load_memory(self) -> List[Dict]:
        """Load query history from disk."""
        if not self.memory_file.exists():
            return []
        
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load memory: {str(e)}")
            return []
    
    def _load_cache(self) -> Dict:
        """Load query cache from disk."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cache: {str(e)}")
            return {}
    
    def _save_memory(self):
        """Save query history to disk."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.debug(f"Memory saved ({len(self.memory)} entries)")
        except Exception as e:
            logger.error(f"Failed to save memory: {str(e)}")
    
    def _save_cache(self):
        """Save query cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Cache saved ({len(self.cache)} entries)")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
    
    def export_report(self, filepath: str = "query_memory_report.json") -> str:
        """
        Export comprehensive memory report.
        
        Args:
            filepath: Output file path
            
        Returns:
            Path to report file
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_memory_stats(),
            "top_queries": self.get_frequently_searched(20),
            "total_entries": len(self.memory),
            "memory_size_mb": self.memory_file.stat().st_size / (1024*1024) if self.memory_file.exists() else 0
        }
        
        output_path = Path(filepath)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Memory report exported to {filepath}")
        return str(output_path)
