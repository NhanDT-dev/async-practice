"""
Tests for Exercise 2 (Medium): Concurrent Execution
Run with: python -m pytest module_01_coroutines_eventloop/exercises/test_medium.py -v
"""

import asyncio
import time
import pytest

from exercise_medium import (
    fetch_all,
    race,
    fetch_with_timeout,
    process_batch,
    async_map,
)


# Helper functions for async_map tests
async def double(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 2


async def square(x: int) -> int:
    await asyncio.sleep(0.1)
    return x ** 2


class TestFetchAll:
    """Tests for Exercise 2.1: fetch_all"""

    def test_single_url(self):
        result = asyncio.run(fetch_all(["url1"]))
        assert result == ["Content from url1"]

    def test_multiple_urls(self):
        result = asyncio.run(fetch_all(["url1", "url2", "url3"]))
        assert result == [
            "Content from url1",
            "Content from url2",
            "Content from url3"
        ]

    def test_concurrent_timing(self):
        """Multiple URLs should run concurrently, not sequentially"""
        start = time.time()
        asyncio.run(fetch_all(["a", "b", "c", "d", "e"]))
        elapsed = time.time() - start
        # 5 URLs should take ~0.1s (concurrent), not 0.5s (sequential)
        assert elapsed < 0.25, f"Expected concurrent execution, got {elapsed}s"

    def test_empty_list(self):
        result = asyncio.run(fetch_all([]))
        assert result == []


class TestRace:
    """Tests for Exercise 2.2: race"""

    def test_fastest_wins(self):
        result = asyncio.run(race([
            ("Slow", 0.3),
            ("Fast", 0.1),
            ("Medium", 0.2)
        ]))
        assert result == "Fast"

    def test_single_competitor(self):
        result = asyncio.run(race([("Solo", 0.1)]))
        assert result == "Solo"

    def test_timing(self):
        """Should return as soon as first finishes"""
        start = time.time()
        asyncio.run(race([
            ("Slow", 0.5),
            ("Fast", 0.1),
            ("Slower", 0.8)
        ]))
        elapsed = time.time() - start
        assert elapsed < 0.2, f"Expected early return at ~0.1s, got {elapsed}s"


class TestFetchWithTimeout:
    """Tests for Exercise 2.3: fetch_with_timeout"""

    def test_success_when_timeout_long(self):
        result = asyncio.run(fetch_with_timeout("example.com", 1.0))
        assert result == "Success: example.com"

    def test_timeout_when_timeout_short(self):
        result = asyncio.run(fetch_with_timeout("example.com", 0.2))
        assert result == "Timeout: example.com"

    def test_timeout_timing(self):
        """Should return at timeout, not wait for full fetch"""
        start = time.time()
        asyncio.run(fetch_with_timeout("test.com", 0.1))
        elapsed = time.time() - start
        # Should return at ~0.1s (timeout), not 0.5s (fetch time)
        assert elapsed < 0.2, f"Expected timeout at 0.1s, got {elapsed}s"


class TestProcessBatch:
    """Tests for Exercise 2.4: process_batch"""

    def test_single_batch(self):
        result = asyncio.run(process_batch(["a", "b"], batch_size=2))
        assert result == ["Processed: a", "Processed: b"]

    def test_multiple_batches(self):
        result = asyncio.run(process_batch(
            ["a", "b", "c", "d", "e"],
            batch_size=2
        ))
        assert result == [
            "Processed: a", "Processed: b",
            "Processed: c", "Processed: d",
            "Processed: e"
        ]

    def test_batch_timing(self):
        """Each batch should run concurrently"""
        start = time.time()
        asyncio.run(process_batch(["a", "b", "c", "d"], batch_size=2))
        elapsed = time.time() - start
        # 2 batches * 0.1s each = ~0.2s, not 0.4s
        assert 0.15 < elapsed < 0.35, f"Expected ~0.2s, got {elapsed}s"

    def test_large_batch_size(self):
        """Batch size larger than items should still work"""
        result = asyncio.run(process_batch(["x", "y"], batch_size=10))
        assert result == ["Processed: x", "Processed: y"]

    def test_empty_items(self):
        result = asyncio.run(process_batch([], batch_size=2))
        assert result == []


class TestAsyncMap:
    """Tests for Exercise 2.5: async_map"""

    def test_double(self):
        result = asyncio.run(async_map([1, 2, 3], double))
        assert result == [2, 4, 6]

    def test_square(self):
        result = asyncio.run(async_map([1, 2, 3, 4], square))
        assert result == [1, 4, 9, 16]

    def test_concurrent_timing(self):
        start = time.time()
        asyncio.run(async_map([1, 2, 3, 4, 5], double))
        elapsed = time.time() - start
        # Should be ~0.1s concurrent, not 0.5s sequential
        assert elapsed < 0.2, f"Expected concurrent execution, got {elapsed}s"

    def test_empty_list(self):
        result = asyncio.run(async_map([], double))
        assert result == []

    def test_preserves_order(self):
        """Results should match input order"""
        result = asyncio.run(async_map([5, 3, 1, 4, 2], double))
        assert result == [10, 6, 2, 8, 4]
