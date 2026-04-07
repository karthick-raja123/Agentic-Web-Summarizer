"""
Intelligent Caching System - Stores and reuses LLM results with smart invalidation.
Reduces API calls and costs by caching successful responses.
"""

import hashlib
import json
import time
import sqlite3
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import pickle


class CacheEntry:
    """Represents a cached entry"""
    
    def __init__(self, key: str, value: str, metadata: Dict[str, Any] = None):
        self.key = key
        self.value = value
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.hits = 0
        self.size_bytes = len(pickle.dumps(value))
    
    def is_expired(self, ttl_seconds: int = 86400) -> bool:
        """Check if entry has expired (default 24 hours)"""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > ttl_seconds
    
    def record_hit(self):
        """Record a cache hit"""
        self.hits += 1


class IntelligentCache:
    """
    Intelligent caching system with TTL, eviction policies, and statistics.
    Supports both in-memory and persistent SQLite storage.
    """
    
    def __init__(self, cache_dir: str = ".cache", max_size_mb: int = 500, use_sqlite: bool = True):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache storage
            max_size_mb: Maximum cache size in MB
            use_sqlite: Whether to use SQLite for persistence
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.use_sqlite = use_sqlite
        self.sqlite_path = self.cache_dir / "cache.db"
        
        # In-memory cache
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._current_size = 0
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "errors": 0,
            "avg_hit_latency_ms": 0
        }
        
        # Initialize SQLite if enabled
        if self.use_sqlite:
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(str(self.sqlite_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP,
                    accessed_at TIMESTAMP,
                    hits INTEGER,
                    expiry TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expiry ON cache_entries(expiry)
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing cache DB: {e}")
    
    def _generate_key(self, content: str, model: str, task_type: str = "") -> str:
        """
        Generate cache key from content and parameters.
        Uses SHA256 hash for consistency.
        """
        key_str = f"{content}|{model}|{task_type}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, content: str, model: str, task_type: str = "") -> Optional[str]:
        """
        Get value from cache if available.
        
        Args:
            content: Query content
            model: Model used
            task_type: Type of task
            
        Returns:
            Cached value if found and valid, None otherwise
        """
        key = self._generate_key(content, model, task_type)
        
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            
            if not entry.is_expired():
                entry.record_hit()
                self.stats["hits"] += 1
                return entry.value
            else:
                # Remove expired entry
                del self._memory_cache[key]
                self._current_size -= entry.size_bytes
        
        # Check persistent cache
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                # Get from DB
                cursor.execute("""
                    SELECT value, hits, expiry FROM cache_entries
                    WHERE key = ?
                """, (key,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    value, hits, expiry = result
                    expiry_time = datetime.fromisoformat(expiry)
                    
                    if datetime.now() < expiry_time:
                        # Found and not expired - move to memory
                        self._memory_cache[key] = CacheEntry(key, value)
                        self.stats["hits"] += 1
                        return value
            except Exception as e:
                print(f"Cache get error: {e}")
                self.stats["errors"] += 1
        
        self.stats["misses"] += 1
        return None
    
    def set(
        self,
        content: str,
        value: str,
        model: str,
        task_type: str = "",
        ttl_seconds: int = 86400,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Store value in cache.
        
        Args:
            content: Query content
            value: Value to cache
            model: Model used
            task_type: Type of task
            ttl_seconds: Time-to-live in seconds
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            key = self._generate_key(content, model, task_type)
            entry = CacheEntry(key, value, metadata)
            
            # Check size
            if self._current_size + entry.size_bytes > self.max_size_bytes:
                self._evict_entries()
            
            # Store in memory
            self._memory_cache[key] = entry
            self._current_size += entry.size_bytes
            
            # Store in persistent cache
            if self.use_sqlite:
                expiry = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
                
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO cache_entries
                    (key, value, metadata, created_at, accessed_at, hits, expiry)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    key,
                    value,
                    json.dumps(metadata or {}),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    0,
                    expiry
                ))
                
                conn.commit()
                conn.close()
            
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            self.stats["errors"] += 1
            return False
    
    def _evict_entries(self, target_size_ratio: float = 0.8):
        """
        Evict entries when cache is full.
        Uses LRU (Least Recently Used) strategy.
        """
        target_size = int(self.max_size_bytes * target_size_ratio)
        
        # Sort by hits (ascending) - evict least used
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].hits
        )
        
        for key, entry in sorted_entries:
            if self._current_size <= target_size:
                break
            
            del self._memory_cache[key]
            self._current_size -= entry.size_bytes
            self.stats["evictions"] += 1
    
    def clear(self):
        """Clear all cache"""
        self._memory_cache.clear()
        self._current_size = 0
        
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache_entries")
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Cache clear error: {e}")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache"""
        
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            entry = self._memory_cache[key]
            del self._memory_cache[key]
            self._current_size -= entry.size_bytes
        
        # Cleanup SQLite
        if self.use_sqlite:
            try:
                conn = sqlite3.connect(str(self.sqlite_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM cache_entries
                    WHERE expiry < ?
                """, (datetime.now().isoformat(),))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Cache cleanup error: {e}")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        hit_rate = 0
        if self.stats["hits"] + self.stats["misses"] > 0:
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])
        
        return {
            **self.stats,
            "hit_rate": f"{hit_rate * 100:.1f}%",
            "memory_entries": len(self._memory_cache),
            "memory_size_mb": self._current_size / (1024 * 1024),
            "memory_capacity_mb": self.max_size_bytes / (1024 * 1024)
        }
    
    def get_top_cached_queries(self, n: int = 10) -> list:
        """Get top cached queries by hit count"""
        
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].hits,
            reverse=True
        )
        
        return [
            {
                "key": entry.key[:16] + "...",
                "hits": entry.hits,
                "size_kb": entry.size_bytes / 1024,
                "age_minutes": (datetime.now() - entry.timestamp).total_seconds() / 60
            }
            for _, entry in sorted_entries[:n]
        ]
