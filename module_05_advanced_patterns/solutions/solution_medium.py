"""
Solutions for Exercise 2 (Medium): Intermediate Async Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
import functools
from typing import Any, Callable, Awaitable
from collections import OrderedDict


# =============================================================================
# Solution 2.1: Async Singleton
# =============================================================================
class AsyncDatabase:
    _instance = None
    _lock = asyncio.Lock()
    _initialized = False

    def __init__(self):
        pass

    @classmethod
    async def get_instance(cls):
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
                await cls._instance.initialize()
            return cls._instance

    async def initialize(self):
        await asyncio.sleep(0.1)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    async def query(self, sql: str) -> str:
        return f"Result: {sql}"


# =============================================================================
# Solution 2.2: Async LRU Cache
# =============================================================================
def async_lru_cache(maxsize: int):
    def decorator(func):
        cache = OrderedDict()

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = await func(*args, **kwargs)
            cache[key] = result

            if len(cache) > maxsize:
                cache.popitem(last=False)

            return result

        return wrapper
    return decorator


# =============================================================================
# Solution 2.3: Async Event Debouncer
# =============================================================================
class AsyncDebouncer:
    def __init__(self, delay: float):
        self.delay = delay
        self._pending_task = None
        self._pending_future = None
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[[], Awaitable[Any]]) -> Any:
        async with self._lock:
            # Cancel any pending call
            if self._pending_task is not None:
                self._pending_task.cancel()

            # Create new future for this call
            future = asyncio.Future()
            self._pending_future = future

            async def delayed_call():
                await asyncio.sleep(self.delay)
                try:
                    result = await func()
                    self._pending_future.set_result(result)
                except Exception as e:
                    self._pending_future.set_exception(e)

            self._pending_task = asyncio.create_task(delayed_call())

        return await future


# =============================================================================
# Solution 2.4: Async Throttle
# =============================================================================
class AsyncThrottle:
    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._last_call = 0
        self._lock = asyncio.Lock()
        self._queue = asyncio.Queue()
        self._running = False

    async def call(self, func: Callable[[], Awaitable[Any]]) -> Any:
        future = asyncio.Future()
        await self._queue.put((func, future))

        if not self._running:
            self._running = True
            asyncio.create_task(self._process_queue())

        return await future

    async def _process_queue(self):
        while True:
            try:
                func, future = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                self._running = False
                break

            now = time.monotonic()
            wait_time = self.min_interval - (now - self._last_call)
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            try:
                result = await func()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

            self._last_call = time.monotonic()


# =============================================================================
# Solution 2.5: Async Memoize with TTL
# =============================================================================
def async_memoize_ttl(ttl: float):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result

            result = await func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper
    return decorator


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing AsyncDatabase:")
        AsyncDatabase._instance = None  # Reset
        db1 = await AsyncDatabase.get_instance()
        db2 = await AsyncDatabase.get_instance()
        print(f"Same instance: {db1 is db2}")
        print(f"Initialized: {db1.is_initialized}")

        print("\nTesting async_lru_cache:")

        @async_lru_cache(maxsize=2)
        async def expensive(x):
            print(f"  Computing {x}...")
            return x * 2

        print(await expensive(1))
        print(await expensive(1))  # Cached
        print(await expensive(2))
        print(await expensive(3))  # Evicts 1
        print(await expensive(1))  # Recomputes

        print("\nTesting AsyncDebouncer:")
        debouncer = AsyncDebouncer(delay=0.2)
        count = [0]

        async def increment():
            count[0] += 1
            return count[0]

        tasks = [
            asyncio.create_task(debouncer.call(increment)),
            asyncio.create_task(debouncer.call(increment)),
        ]
        await asyncio.gather(*tasks)
        print(f"Call count: {count[0]} (should be 1)")

        print("\nTesting AsyncThrottle:")
        throttle = AsyncThrottle(min_interval=0.1)

        async def work(n):
            return n

        start = time.time()
        results = await asyncio.gather(
            throttle.call(lambda: work(1)),
            throttle.call(lambda: work(2)),
            throttle.call(lambda: work(3)),
        )
        print(f"Results: {results}, Time: {time.time() - start:.2f}s")

        print("\nTesting async_memoize_ttl:")

        @async_memoize_ttl(ttl=0.2)
        async def fetch(key):
            print(f"  Fetching {key}...")
            return f"value-{key}"

        print(await fetch("a"))
        print(await fetch("a"))  # Cached
        await asyncio.sleep(0.25)
        print(await fetch("a"))  # Expired, refetch

    asyncio.run(main())
