"""
Solutions for Exercise 2 (Medium): Concurrent Execution

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Callable, Awaitable


# =============================================================================
# Solution 2.1: Parallel Fetch
# =============================================================================
async def fetch_all(urls: list[str]) -> list[str]:
    async def fetch_one(url: str) -> str:
        await asyncio.sleep(0.1)
        return f"Content from {url}"

    # asyncio.gather runs all coroutines concurrently
    # and returns results in the same order as input
    results = await asyncio.gather(*[fetch_one(url) for url in urls])
    return list(results)


# =============================================================================
# Solution 2.2: Fastest Wins
# =============================================================================
async def race(competitors: list[tuple[str, float]]) -> str:
    async def compete(name: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return name

    # Create tasks for all competitors
    tasks = [
        asyncio.create_task(compete(name, delay))
        for name, delay in competitors
    ]

    # wait() with FIRST_COMPLETED returns when any task finishes
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel remaining tasks (cleanup)
    for task in pending:
        task.cancel()

    # Get the result from the completed task
    winner_task = done.pop()
    return winner_task.result()


# Alternative solution using asyncio.gather with return_exceptions
async def race_v2(competitors: list[tuple[str, float]]) -> str:
    """Alternative: manually track which finishes first"""
    winner = None
    winner_event = asyncio.Event()

    async def compete(name: str, delay: float):
        nonlocal winner
        await asyncio.sleep(delay)
        if winner is None:
            winner = name
            winner_event.set()

    # Start all competitors
    tasks = [
        asyncio.create_task(compete(name, delay))
        for name, delay in competitors
    ]

    # Wait for first to finish
    await winner_event.wait()

    # Cleanup
    for task in tasks:
        task.cancel()

    return winner


# =============================================================================
# Solution 2.3: Timeout Handler
# =============================================================================
async def fetch_with_timeout(url: str, timeout: float) -> str:
    async def do_fetch():
        await asyncio.sleep(0.5)  # Simulate slow fetch
        return f"Success: {url}"

    try:
        result = await asyncio.wait_for(do_fetch(), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return f"Timeout: {url}"


# =============================================================================
# Solution 2.4: Batch Processor
# =============================================================================
async def process_batch(items: list[str], batch_size: int) -> list[str]:
    async def process_item(item: str) -> str:
        await asyncio.sleep(0.1)
        return f"Processed: {item}"

    results = []

    # Process in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_item(item) for item in batch]
        )
        results.extend(batch_results)

    return results


# =============================================================================
# Solution 2.5: Parallel Map
# =============================================================================
async def async_map(
    items: list[int],
    func: Callable[[int], Awaitable[int]]
) -> list[int]:
    results = await asyncio.gather(*[func(item) for item in items])
    return list(results)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    import time

    print("Testing fetch_all:")
    start = time.time()
    result = asyncio.run(fetch_all(["url1", "url2", "url3"]))
    print(f"Results: {result}")
    print(f"Time: {time.time() - start:.2f}s")

    print("\nTesting race:")
    result = asyncio.run(race([
        ("Slow", 0.3),
        ("Fast", 0.1),
        ("Medium", 0.2)
    ]))
    print(f"Winner: {result}")

    print("\nTesting fetch_with_timeout:")
    print(asyncio.run(fetch_with_timeout("example.com", 1.0)))
    print(asyncio.run(fetch_with_timeout("example.com", 0.2)))

    print("\nTesting process_batch:")
    start = time.time()
    result = asyncio.run(process_batch(["a", "b", "c", "d", "e"], 2))
    print(f"Results: {result}")
    print(f"Time: {time.time() - start:.2f}s")

    print("\nTesting async_map:")

    async def double(x):
        await asyncio.sleep(0.1)
        return x * 2

    result = asyncio.run(async_map([1, 2, 3, 4, 5], double))
    print(f"Results: {result}")
