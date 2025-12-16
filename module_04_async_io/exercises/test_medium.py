"""
Tests for Exercise 2 (Medium): Async I/O Patterns
Run with: python -m pytest module_04_async_io/exercises/test_medium.py -v
"""

import asyncio
import time
import pytest

from exercise_medium import (
    AsyncConnectionPool,
    RateLimitedClient,
    AsyncStreamProcessor,
    TimeoutManager,
    AsyncResourceLoader,
)


class TestAsyncConnectionPool:
    """Tests for Exercise 2.1: AsyncConnectionPool"""

    def test_acquire_release(self):
        async def check():
            pool = AsyncConnectionPool(max_connections=3)
            conn = await pool.acquire()
            assert conn is not None
            await pool.release(conn)

        asyncio.run(check())

    def test_context_manager(self):
        async def check():
            pool = AsyncConnectionPool(max_connections=2)
            async with pool.connection() as conn:
                assert conn is not None

        asyncio.run(check())

    def test_respects_max(self):
        async def check():
            pool = AsyncConnectionPool(max_connections=2)
            conn1 = await pool.acquire()
            conn2 = await pool.acquire()

            acquired = False

            async def try_acquire():
                nonlocal acquired
                await pool.acquire()
                acquired = True

            task = asyncio.create_task(try_acquire())
            await asyncio.sleep(0.1)
            assert acquired is False

            await pool.release(conn1)
            await asyncio.sleep(0.05)
            assert acquired is True

            await pool.release(conn2)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        asyncio.run(check())


class TestRateLimitedClient:
    """Tests for Exercise 2.2: RateLimitedClient"""

    def test_basic_request(self):
        async def check():
            client = RateLimitedClient(max_per_second=10)
            result = await client.request("http://example.com")
            assert "Response from http://example.com" == result

        asyncio.run(check())

    def test_rate_limiting(self):
        async def check():
            client = RateLimitedClient(max_per_second=5)
            start = time.time()

            # 10 requests at 5/sec should take ~2 seconds
            await asyncio.gather(*[
                client.request(f"url{i}") for i in range(10)
            ])

            elapsed = time.time() - start
            # Should take at least 1 second (10 requests at 5/sec)
            assert elapsed >= 0.8

        asyncio.run(check())


class TestAsyncStreamProcessor:
    """Tests for Exercise 2.3: AsyncStreamProcessor"""

    def test_processes_all_items(self):
        async def check():
            async def source():
                for i in range(5):
                    yield i

            async def transform(x):
                await asyncio.sleep(0.01)
                return x * 2

            processor = AsyncStreamProcessor(max_concurrent=3)
            results = []
            async for result in processor.process(source(), transform):
                results.append(result)

            assert sorted(results) == [0, 2, 4, 6, 8]

        asyncio.run(check())

    def test_respects_max_concurrent(self):
        async def check():
            running = 0
            max_running = 0

            async def source():
                for i in range(10):
                    yield i

            async def transform(x):
                nonlocal running, max_running
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.05)
                running -= 1
                return x

            processor = AsyncStreamProcessor(max_concurrent=3)
            results = []
            async for result in processor.process(source(), transform):
                results.append(result)

            assert max_running <= 3

        asyncio.run(check())


class TestTimeoutManager:
    """Tests for Exercise 2.4: TimeoutManager"""

    def test_successful_completion(self):
        async def check():
            async def fast():
                await asyncio.sleep(0.05)
                return "done"

            manager = TimeoutManager()
            results = await manager.execute([(fast(), 1.0)])
            assert results == [("done", True)]

        asyncio.run(check())

    def test_timeout(self):
        async def check():
            async def slow():
                await asyncio.sleep(1.0)
                return "done"

            manager = TimeoutManager()
            results = await manager.execute([(slow(), 0.1)])
            assert results == [(None, False)]

        asyncio.run(check())

    def test_mixed(self):
        async def check():
            async def slow():
                await asyncio.sleep(1.0)
                return "slow"

            async def fast():
                await asyncio.sleep(0.05)
                return "fast"

            manager = TimeoutManager()
            results = await manager.execute([
                (slow(), 0.1),
                (fast(), 0.5),
            ])
            assert results[0] == (None, False)
            assert results[1] == ("fast", True)

        asyncio.run(check())


class TestAsyncResourceLoader:
    """Tests for Exercise 2.5: AsyncResourceLoader"""

    def test_load_single(self):
        async def check():
            loader = AsyncResourceLoader()
            result = await loader.load("resource1")
            assert result is not None

        asyncio.run(check())

    def test_caching(self):
        async def check():
            loader = AsyncResourceLoader()

            start = time.time()
            await loader.load("resource1")
            first_load = time.time() - start

            start = time.time()
            await loader.load("resource1")
            second_load = time.time() - start

            assert first_load >= 0.1  # Initial load has delay
            assert second_load < 0.05  # Cached is fast

        asyncio.run(check())

    def test_load_many(self):
        async def check():
            loader = AsyncResourceLoader()
            results = await loader.load_many(["r1", "r2", "r3"])
            assert len(results) == 3

        asyncio.run(check())

    def test_load_many_concurrent(self):
        async def check():
            loader = AsyncResourceLoader()

            start = time.time()
            await loader.load_many(["r1", "r2", "r3", "r4", "r5"])
            elapsed = time.time() - start

            # Should be ~0.1s concurrent, not 0.5s sequential
            assert elapsed < 0.2

        asyncio.run(check())

    def test_clear_cache(self):
        async def check():
            loader = AsyncResourceLoader()
            await loader.load("r1")  # Cache it

            start = time.time()
            await loader.load("r1")  # Fast (cached)
            cached_time = time.time() - start
            assert cached_time < 0.05

            loader.clear_cache()

            start = time.time()
            await loader.load("r1")  # Slow (not cached)
            uncached_time = time.time() - start
            assert uncached_time >= 0.1

        asyncio.run(check())
