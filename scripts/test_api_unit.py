#!/usr/bin/env python3
"""
Unit tests for Klinicka Knowledge Base RAG API components.
Tests caching, rate limiting, and metrics collection.
"""
import sys
import time
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

# Import after path is set
from rag_api import ResponseCache, RateLimiter, APIMetrics


class TestResponseCache(unittest.TestCase):
    """Tests for ResponseCache class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = ResponseCache(ttl_seconds=1, max_size=3)

    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        test_value = {"query": "test", "results": []}
        self.cache.set("test query", 5, "search", test_value)

        result = self.cache.get("test query", 5, "search")
        self.assertEqual(result, test_value)

    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = self.cache.get("nonexistent", 5, "search")
        self.assertIsNone(result)

    def test_cache_expiration(self):
        """Test cache entries expire after TTL."""
        self.cache.set("test", 5, "search", {"data": "test"})

        # Wait for expiration
        time.sleep(1.1)

        result = self.cache.get("test", 5, "search")
        self.assertIsNone(result)

    def test_cache_case_insensitivity(self):
        """Test cache keys are case-insensitive."""
        test_value = {"query": "Test Query", "results": []}
        self.cache.set("Test Query", 5, "search", test_value)

        # Should find with lowercase
        result = self.cache.get("test query", 5, "search")
        self.assertEqual(result, test_value)

    def test_cache_different_endpoints(self):
        """Test same query cached separately for different endpoints."""
        search_value = {"type": "search"}
        qa_value = {"type": "qa"}

        self.cache.set("test", 5, "search", search_value)
        self.cache.set("test", 5, "qa", qa_value)

        search_result = self.cache.get("test", 5, "search")
        qa_result = self.cache.get("test", 5, "qa")

        self.assertEqual(search_result, search_value)
        self.assertEqual(qa_result, qa_value)

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        self.cache.set("query1", 5, "search", {"v": 1})
        time.sleep(0.01)
        self.cache.set("query2", 5, "search", {"v": 2})
        time.sleep(0.01)
        self.cache.set("query3", 5, "search", {"v": 3})

        # Cache is now full (max_size=3)
        self.assertEqual(self.cache.size(), 3)

        # Adding another should evict oldest (query1)
        self.cache.set("query4", 5, "search", {"v": 4})

        self.assertEqual(self.cache.size(), 3)
        self.assertIsNone(self.cache.get("query1", 5, "search"))
        self.assertIsNotNone(self.cache.get("query4", 5, "search"))

    def test_cache_clear(self):
        """Test cache clear removes all entries."""
        self.cache.set("query1", 5, "search", {"v": 1})
        self.cache.set("query2", 5, "search", {"v": 2})

        self.assertEqual(self.cache.size(), 2)
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)


class TestRateLimiter(unittest.TestCase):
    """Tests for RateLimiter class."""

    def setUp(self):
        """Set up test fixtures."""
        # 3 requests per 1 second window
        self.limiter = RateLimiter(max_requests=3, window_seconds=1)

    def test_allows_requests_under_limit(self):
        """Test requests under limit are allowed."""
        client = "test_client"

        self.assertTrue(self.limiter.is_allowed(client))
        self.assertTrue(self.limiter.is_allowed(client))
        self.assertTrue(self.limiter.is_allowed(client))

    def test_blocks_requests_over_limit(self):
        """Test requests over limit are blocked."""
        client = "test_client"

        # Use up the limit
        for _ in range(3):
            self.limiter.is_allowed(client)

        # Next should be blocked
        self.assertFalse(self.limiter.is_allowed(client))

    def test_window_reset(self):
        """Test rate limit resets after window expires."""
        client = "test_client"

        # Use up the limit
        for _ in range(3):
            self.limiter.is_allowed(client)

        # Should be blocked
        self.assertFalse(self.limiter.is_allowed(client))

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        self.assertTrue(self.limiter.is_allowed(client))

    def test_separate_client_limits(self):
        """Test each client has separate limit."""
        client1 = "client1"
        client2 = "client2"

        # Use up client1's limit
        for _ in range(3):
            self.limiter.is_allowed(client1)

        # client1 should be blocked
        self.assertFalse(self.limiter.is_allowed(client1))

        # client2 should still be allowed
        self.assertTrue(self.limiter.is_allowed(client2))

    def test_remaining_requests(self):
        """Test getting remaining requests count."""
        client = "test_client"

        self.assertEqual(self.limiter.get_remaining(client), 3)

        self.limiter.is_allowed(client)
        self.assertEqual(self.limiter.get_remaining(client), 2)

        self.limiter.is_allowed(client)
        self.assertEqual(self.limiter.get_remaining(client), 1)

        self.limiter.is_allowed(client)
        self.assertEqual(self.limiter.get_remaining(client), 0)


class TestAPIMetrics(unittest.TestCase):
    """Tests for APIMetrics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.metrics = APIMetrics()

    def test_record_request(self):
        """Test request recording."""
        self.metrics.record_request("search", 100.0, cache_hit=False)
        self.metrics.record_request("qa", 200.0, cache_hit=True)

        data = self.metrics.get_metrics()

        self.assertEqual(data["total_requests"], 2)
        self.assertEqual(data["search_requests"], 1)
        self.assertEqual(data["qa_requests"], 1)
        self.assertEqual(data["cache_hits"], 1)
        self.assertEqual(data["cache_misses"], 1)
        self.assertEqual(data["cache_hit_rate_percent"], 50.0)

    def test_average_latency(self):
        """Test average latency calculation."""
        self.metrics.record_request("search", 100.0)
        self.metrics.record_request("search", 200.0)
        self.metrics.record_request("search", 300.0)

        data = self.metrics.get_metrics()

        self.assertEqual(data["avg_latency_ms"], 200.0)

    def test_record_rate_limit(self):
        """Test rate limit recording."""
        self.metrics.record_rate_limit()
        self.metrics.record_rate_limit()

        data = self.metrics.get_metrics()

        self.assertEqual(data["rate_limited_requests"], 2)

    def test_record_error(self):
        """Test error recording."""
        self.metrics.record_error()

        data = self.metrics.get_metrics()

        self.assertEqual(data["error_count"], 1)

    def test_uptime_calculation(self):
        """Test uptime is calculated correctly."""
        time.sleep(0.1)

        data = self.metrics.get_metrics()

        self.assertGreater(data["uptime_seconds"], 0.09)
        self.assertLess(data["uptime_seconds"], 1.0)


class TestCacheKeyGeneration(unittest.TestCase):
    """Tests for cache key generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.cache = ResponseCache()

    def test_different_top_k_different_keys(self):
        """Test different top_k values produce different cache keys."""
        self.cache.set("query", 5, "search", {"topk": 5})
        self.cache.set("query", 10, "search", {"topk": 10})

        result5 = self.cache.get("query", 5, "search")
        result10 = self.cache.get("query", 10, "search")

        self.assertEqual(result5["topk"], 5)
        self.assertEqual(result10["topk"], 10)

    def test_whitespace_normalization(self):
        """Test queries are normalized for whitespace."""
        self.cache.set("  test query  ", 5, "search", {"v": 1})

        # Should find with different whitespace
        result = self.cache.get("test query", 5, "search")
        self.assertIsNotNone(result)


def run_tests():
    """Run all unit tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResponseCache))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimiter))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheKeyGeneration))

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
