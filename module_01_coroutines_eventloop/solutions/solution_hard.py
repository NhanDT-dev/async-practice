"""
Solutions for Exercise 3 (Hard): Advanced Coroutine Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Any, Callable, Awaitable
from collections import defaultdict


# =============================================================================
# Solution 3.1: Retry with Exponential Backoff
# =============================================================================
async def retry_with_backoff(
    func: Callable[[], Awaitable[Any]],
    max_retries: int,
    base_delay: float
) -> Any:
    last_exception = None
    delay = base_delay

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:  # Don't sleep after last attempt
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    raise last_exception


# =============================================================================
# Solution 3.2: Concurrent Limit (Semaphore-like)
# =============================================================================
async def limited_gather(
    coros: list[Awaitable[Any]],
    limit: int
) -> list[Any]:
    results = []

    # Process in chunks of size `limit`
    for i in range(0, len(coros), limit):
        batch = coros[i:i + limit]
        batch_results = await asyncio.gather(*batch)
        results.extend(batch_results)

    return results


# Alternative: Using indices to maintain order
async def limited_gather_v2(
    coros: list[Awaitable[Any]],
    limit: int
) -> list[Any]:
    """Version that processes and maintains results in chunks"""
    if not coros:
        return []

    all_results = []

    # Convert coroutines to list for indexing
    coro_list = list(coros)

    for start in range(0, len(coro_list), limit):
        end = min(start + limit, len(coro_list))
        chunk = coro_list[start:end]
        chunk_results = await asyncio.gather(*chunk)
        all_results.extend(chunk_results)

    return all_results


# =============================================================================
# Solution 3.3: Async Pipeline
# =============================================================================
async def pipeline(
    initial_value: Any,
    stages: list[Callable[[Any], Awaitable[Any]]]
) -> Any:
    value = initial_value

    for stage in stages:
        value = await stage(value)

    return value


# =============================================================================
# Solution 3.4: First Successful
# =============================================================================
async def first_successful(
    funcs: list[Callable[[], Awaitable[Any]]]
) -> Any:
    # Create tasks for all functions
    tasks = [asyncio.create_task(func()) for func in funcs]

    # Track pending tasks
    pending = set(tasks)
    result = None
    found = False

    while pending and not found:
        # Wait for any task to complete
        done, pending = await asyncio.wait(
            pending,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Check if any completed task was successful
        for task in done:
            try:
                result = task.result()
                found = True
                break
            except Exception:
                # This task failed, continue waiting for others
                pass

    # Cancel remaining tasks
    for task in pending:
        task.cancel()

    if found:
        return result
    else:
        raise Exception("All failed")


# Alternative: Using exception aggregation
async def first_successful_v2(
    funcs: list[Callable[[], Awaitable[Any]]]
) -> Any:
    """Alternative using gather with return_exceptions"""

    async def try_func(func):
        try:
            return ("success", await func())
        except Exception as e:
            return ("error", e)

    # Run all concurrently
    results = await asyncio.gather(*[try_func(f) for f in funcs])

    # Find first success (by completion order is tricky with gather,
    # so this version returns based on input order)
    for status, value in results:
        if status == "success":
            return value

    raise Exception("All failed")


# =============================================================================
# Solution 3.5: Async Event Emitter
# =============================================================================
class AsyncEventEmitter:
    def __init__(self):
        self._handlers: dict[str, list[Callable[..., Awaitable[Any]]]] = \
            defaultdict(list)

    def on(self, event_name: str, callback: Callable[..., Awaitable[Any]]):
        """Register an async callback for an event"""
        self._handlers[event_name].append(callback)

    async def emit(self, event_name: str, *args) -> list[Any]:
        """Emit an event and run all handlers concurrently"""
        handlers = self._handlers.get(event_name, [])

        if not handlers:
            return []

        # Run all handlers concurrently
        results = await asyncio.gather(
            *[handler(*args) for handler in handlers]
        )

        return list(results)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    import time

    print("=" * 60)
    print("Testing retry_with_backoff:")
    print("=" * 60)

    attempt = 0

    async def flaky():
        global attempt
        attempt += 1
        print(f"  Attempt {attempt}")
        if attempt < 3:
            raise ValueError("Not yet")
        return "Success!"

    start = time.time()
    result = asyncio.run(retry_with_backoff(flaky, 5, 0.1))
    print(f"Result: {result}")
    print(f"Time: {time.time() - start:.2f}s (expected ~0.3s)")

    print("\n" + "=" * 60)
    print("Testing limited_gather:")
    print("=" * 60)

    async def numbered_task(n):
        print(f"  Task {n} starting")
        await asyncio.sleep(0.1)
        print(f"  Task {n} done")
        return n

    async def test_limited():
        coros = [numbered_task(i) for i in range(5)]
        return await limited_gather(coros, 2)

    result = asyncio.run(test_limited())
    print(f"Results: {result}")

    print("\n" + "=" * 60)
    print("Testing pipeline:")
    print("=" * 60)

    async def add_one(x):
        return x + 1

    async def double(x):
        return x * 2

    async def to_str(x):
        return f"Result: {x}"

    result = asyncio.run(pipeline(5, [add_one, double, to_str]))
    print(f"5 -> +1 -> *2 -> str = {result}")

    print("\n" + "=" * 60)
    print("Testing first_successful:")
    print("=" * 60)

    async def fast_fail():
        await asyncio.sleep(0.05)
        print("  fast_fail finished (with error)")
        raise ValueError("Fast fail")

    async def slow_success():
        await asyncio.sleep(0.2)
        print("  slow_success finished (success!)")
        return "Slow but successful!"

    result = asyncio.run(first_successful([fast_fail, slow_success]))
    print(f"Result: {result}")

    print("\n" + "=" * 60)
    print("Testing AsyncEventEmitter:")
    print("=" * 60)

    async def handler1(data):
        await asyncio.sleep(0.1)
        return f"Handler1 received: {data}"

    async def handler2(data):
        await asyncio.sleep(0.1)
        return f"Handler2 received: {data}"

    async def test_emitter():
        emitter = AsyncEventEmitter()
        emitter.on("message", handler1)
        emitter.on("message", handler2)

        results = await emitter.emit("message", "Hello!")
        return results

    results = asyncio.run(test_emitter())
    for r in results:
        print(f"  {r}")
