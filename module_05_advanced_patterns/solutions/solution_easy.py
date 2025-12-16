"""
Solutions for Exercise 1 (Easy): Async Patterns Basics

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
import functools
from typing import Any, AsyncIterator
from contextlib import asynccontextmanager


# =============================================================================
# Solution 1.1: Async Context Manager
# =============================================================================
class AsyncTimer:
    def __init__(self):
        self._start = None
        self._elapsed = 0

    @property
    def elapsed(self) -> float:
        return self._elapsed

    async def __aenter__(self):
        self._start = time.monotonic()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._elapsed = time.monotonic() - self._start
        return False


# =============================================================================
# Solution 1.2: Async Iterator
# =============================================================================
class AsyncCountdown:
    def __init__(self, start: int):
        self.current = start

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current <= 0:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        value = self.current
        self.current -= 1
        return value


# =============================================================================
# Solution 1.3: Async Generator
# =============================================================================
async def paginate(items: list, page_size: int) -> AsyncIterator[list]:
    for i in range(0, len(items), page_size):
        await asyncio.sleep(0.1)
        yield items[i:i + page_size]


# =============================================================================
# Solution 1.4: Async Retry Decorator
# =============================================================================
def async_retry(max_retries: int):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1)
            raise last_exception
        return wrapper
    return decorator


# =============================================================================
# Solution 1.5: Async Resource Manager
# =============================================================================
@asynccontextmanager
async def managed_resource(resource_id: str, log: list):
    await asyncio.sleep(0.1)
    log.append(f"acquire:{resource_id}")
    try:
        yield resource_id
    finally:
        await asyncio.sleep(0.1)
        log.append(f"release:{resource_id}")


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing AsyncTimer:")
        async with AsyncTimer() as timer:
            await asyncio.sleep(0.2)
        print(f"Elapsed: {timer.elapsed:.2f}s")

        print("\nTesting AsyncCountdown:")
        async for num in AsyncCountdown(3):
            print(f"  {num}")

        print("\nTesting paginate:")
        async for page in paginate([1, 2, 3, 4, 5], 2):
            print(f"  Page: {page}")

        print("\nTesting async_retry:")
        attempts = [0]

        @async_retry(max_retries=3)
        async def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("fail")
            return "success"

        result = await flaky()
        print(f"Result after {attempts[0]} attempts: {result}")

        print("\nTesting managed_resource:")
        log = []
        async with managed_resource("database", log) as r:
            print(f"  Using: {r}")
        print(f"  Log: {log}")

    asyncio.run(main())
