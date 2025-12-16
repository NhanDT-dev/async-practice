"""
Tests for Exercise 2 (Medium): Intermediate Async Patterns
Run with: python -m pytest module_05_advanced_patterns/exercises/test_medium.py -v
"""

import asyncio
import time
import pytest

from exercise_medium import (
    AsyncDatabase,
    async_lru_cache,
    AsyncDebouncer,
    AsyncThrottle,
    async_memoize_ttl,
)


class TestAsyncDatabase:
    """Tests for Exercise 2.1: AsyncDatabase"""

    def test_singleton(self):
        async def check():
            db1 = await AsyncDatabase.get_instance()
            db2 = await AsyncDatabase.get_instance()
            assert db1 is db2

        asyncio.run(check())

    def test_initialized(self):
        async def check():
            # Reset singleton for test
            AsyncDatabase._instance = None
            db = await AsyncDatabase.get_instance()
            assert db.is_initialized is True

        asyncio.run(check())

    def test_query(self):
        async def check():
            db = await AsyncDatabase.get_instance()
            result = await db.query("SELECT * FROM users")
            assert result == "Result: SELECT * FROM users"

        asyncio.run(check())


class TestAsyncLruCache:
    """Tests for Exercise 2.2: async_lru_cache"""

    def test_caches_result(self):
        call_count = [0]

        @async_lru_cache(maxsize=10)
        async def expensive(x):
            call_count[0] += 1
            await asyncio.sleep(0.05)
            return x * 2

        async def check():
            r1 = await expensive(5)
            r2 = await expensive(5)
            assert r1 == r2 == 10
            assert call_count[0] == 1

        asyncio.run(check())

    def test_different_args(self):
        call_count = [0]

        @async_lru_cache(maxsize=10)
        async def fn(x):
            call_count[0] += 1
            return x

        async def check():
            await fn(1)
            await fn(2)
            await fn(1)
            assert call_count[0] == 2  # Called for 1 and 2

        asyncio.run(check())

    def test_lru_eviction(self):
        call_count = [0]

        @async_lru_cache(maxsize=2)
        async def fn(x):
            call_count[0] += 1
            return x

        async def check():
            await fn(1)
            await fn(2)
            await fn(3)  # Evicts 1
            await fn(1)  # Should recalculate
            assert call_count[0] == 4

        asyncio.run(check())


class TestAsyncDebouncer:
    """Tests for Exercise 2.3: AsyncDebouncer"""

    def test_debounces_rapid_calls(self):
        call_count = [0]

        async def increment():
            call_count[0] += 1
            return call_count[0]

        async def check():
            debouncer = AsyncDebouncer(delay=0.2)

            # Rapid calls
            tasks = [
                asyncio.create_task(debouncer.call(increment)),
                asyncio.create_task(debouncer.call(increment)),
                asyncio.create_task(debouncer.call(increment)),
            ]

            await asyncio.gather(*tasks)
            # Only one execution
            assert call_count[0] == 1

        asyncio.run(check())

    def test_executes_after_delay(self):
        async def check():
            debouncer = AsyncDebouncer(delay=0.1)

            async def work():
                return "done"

            start = time.time()
            result = await debouncer.call(work)
            elapsed = time.time() - start

            assert result == "done"
            assert elapsed >= 0.1

        asyncio.run(check())


class TestAsyncThrottle:
    """Tests for Exercise 2.4: AsyncThrottle"""

    def test_throttles_calls(self):
        async def check():
            throttle = AsyncThrottle(min_interval=0.1)

            async def work(n):
                return n

            start = time.time()
            results = await asyncio.gather(
                throttle.call(lambda: work(1)),
                throttle.call(lambda: work(2)),
                throttle.call(lambda: work(3)),
            )
            elapsed = time.time() - start

            # 3 calls with 0.1s between = at least 0.2s
            assert elapsed >= 0.2
            assert sorted(results) == [1, 2, 3]

        asyncio.run(check())

    def test_preserves_order(self):
        async def check():
            throttle = AsyncThrottle(min_interval=0.05)
            order = []

            async def work(n):
                order.append(n)
                return n

            await asyncio.gather(
                throttle.call(lambda: work(1)),
                throttle.call(lambda: work(2)),
                throttle.call(lambda: work(3)),
            )

            assert order == [1, 2, 3]

        asyncio.run(check())


class TestAsyncMemoizeTtl:
    """Tests for Exercise 2.5: async_memoize_ttl"""

    def test_caches_within_ttl(self):
        call_count = [0]

        @async_memoize_ttl(ttl=1.0)
        async def fetch(key):
            call_count[0] += 1
            return f"value-{key}"

        async def check():
            r1 = await fetch("a")
            r2 = await fetch("a")
            assert r1 == r2 == "value-a"
            assert call_count[0] == 1

        asyncio.run(check())

    def test_expires_after_ttl(self):
        call_count = [0]

        @async_memoize_ttl(ttl=0.1)
        async def fetch(key):
            call_count[0] += 1
            return f"value-{key}"

        async def check():
            await fetch("a")
            await asyncio.sleep(0.15)
            await fetch("a")
            assert call_count[0] == 2

        asyncio.run(check())

    def test_different_keys(self):
        call_count = [0]

        @async_memoize_ttl(ttl=1.0)
        async def fetch(key):
            call_count[0] += 1
            return key

        async def check():
            await fetch("a")
            await fetch("b")
            await fetch("a")
            assert call_count[0] == 2  # a and b

        asyncio.run(check())
