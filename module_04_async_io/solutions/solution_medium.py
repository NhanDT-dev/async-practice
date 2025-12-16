"""
Solutions for Exercise 2 (Medium): Async I/O Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
from typing import Any, Callable, Awaitable
from contextlib import asynccontextmanager


# =============================================================================
# Solution 2.1: Connection Pool
# =============================================================================
class AsyncConnectionPool:
    def __init__(self, max_connections: int):
        self.max_connections = max_connections
        self._available = asyncio.Queue()
        for i in range(max_connections):
            self._available.put_nowait(i)

    async def acquire(self) -> int:
        return await self._available.get()

    async def release(self, conn: int):
        await self._available.put(conn)

    @asynccontextmanager
    async def connection(self):
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)


# =============================================================================
# Solution 2.2: Rate-Limited Client
# =============================================================================
class RateLimitedClient:
    def __init__(self, max_per_second: int):
        self.max_per_second = max_per_second
        self._interval = 1.0 / max_per_second
        self._last_request = 0
        self._lock = asyncio.Lock()

    async def request(self, url: str) -> str:
        async with self._lock:
            now = time.monotonic()
            time_since_last = now - self._last_request
            if time_since_last < self._interval:
                await asyncio.sleep(self._interval - time_since_last)
            self._last_request = time.monotonic()

        await asyncio.sleep(0.05)  # Simulate request
        return f"Response from {url}"


# =============================================================================
# Solution 2.3: Async Stream Processor
# =============================================================================
class AsyncStreamProcessor:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent

    async def process(self, source, transform):
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results_queue = asyncio.Queue()
        pending = 0
        done_producing = False
        lock = asyncio.Lock()

        async def process_item(item):
            nonlocal pending
            async with semaphore:
                result = await transform(item)
                await results_queue.put(result)
                async with lock:
                    pending -= 1

        async def producer():
            nonlocal pending, done_producing
            async for item in source:
                async with lock:
                    pending += 1
                asyncio.create_task(process_item(item))
            done_producing = True

        producer_task = asyncio.create_task(producer())

        while True:
            async with lock:
                if done_producing and pending == 0 and results_queue.empty():
                    break
            try:
                result = await asyncio.wait_for(results_queue.get(), timeout=0.05)
                yield result
            except asyncio.TimeoutError:
                continue

        await producer_task


# =============================================================================
# Solution 2.4: Timeout Manager
# =============================================================================
class TimeoutManager:
    async def execute(self, coros_with_timeouts):
        async def run_with_timeout(coro, timeout):
            try:
                result = await asyncio.wait_for(coro, timeout=timeout)
                return (result, True)
            except asyncio.TimeoutError:
                return (None, False)

        results = await asyncio.gather(*[
            run_with_timeout(coro, timeout)
            for coro, timeout in coros_with_timeouts
        ])
        return list(results)


# =============================================================================
# Solution 2.5: Async Resource Loader
# =============================================================================
class AsyncResourceLoader:
    def __init__(self):
        self._cache = {}
        self._loading = {}  # Prevent duplicate loads

    async def load(self, resource_id: str) -> Any:
        if resource_id in self._cache:
            return self._cache[resource_id]

        if resource_id in self._loading:
            # Wait for existing load
            return await self._loading[resource_id]

        # Start loading
        future = asyncio.Future()
        self._loading[resource_id] = future

        try:
            await asyncio.sleep(0.1)  # Simulate loading
            result = f"Resource:{resource_id}"
            self._cache[resource_id] = result
            future.set_result(result)
            return result
        finally:
            del self._loading[resource_id]

    async def load_many(self, resource_ids: list[str]) -> list[Any]:
        results = await asyncio.gather(*[
            self.load(rid) for rid in resource_ids
        ])
        return list(results)

    def clear_cache(self):
        self._cache.clear()


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing AsyncConnectionPool:")
        pool = AsyncConnectionPool(max_connections=2)
        async with pool.connection() as conn:
            print(f"Got connection: {conn}")

        print("\nTesting RateLimitedClient:")
        client = RateLimitedClient(max_per_second=5)
        start = time.time()
        results = await asyncio.gather(*[
            client.request(f"url{i}") for i in range(5)
        ])
        print(f"5 requests took {time.time() - start:.2f}s")

        print("\nTesting AsyncStreamProcessor:")

        async def source():
            for i in range(5):
                yield i

        async def transform(x):
            await asyncio.sleep(0.05)
            return x * 2

        processor = AsyncStreamProcessor(max_concurrent=2)
        async for result in processor.process(source(), transform):
            print(f"  Got: {result}")

        print("\nTesting TimeoutManager:")
        manager = TimeoutManager()

        async def fast():
            return "fast"

        async def slow():
            await asyncio.sleep(1)
            return "slow"

        results = await manager.execute([
            (fast(), 0.5),
            (slow(), 0.1),
        ])
        print(f"Results: {results}")

        print("\nTesting AsyncResourceLoader:")
        loader = AsyncResourceLoader()
        start = time.time()
        await loader.load("r1")
        print(f"First load: {time.time() - start:.2f}s")
        start = time.time()
        await loader.load("r1")
        print(f"Cached load: {time.time() - start:.4f}s")

    asyncio.run(main())
