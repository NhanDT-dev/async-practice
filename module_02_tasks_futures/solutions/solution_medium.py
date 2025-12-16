"""
Solutions for Exercise 2 (Medium): Task Management and Futures

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Any


# =============================================================================
# Solution 2.1: Cancellation Handler
# =============================================================================
async def cancellable_work(work_id: str, duration: float) -> str:
    try:
        await asyncio.sleep(duration)
        return f"{work_id}: completed"
    except asyncio.CancelledError:
        return f"{work_id}: cancelled"


# =============================================================================
# Solution 2.2: Timeout with Fallback
# =============================================================================
async def fetch_with_fallback(
    primary_delay: float,
    fallback_value: str,
    timeout: float
) -> str:
    async def fetch():
        await asyncio.sleep(primary_delay)
        return f"primary: {primary_delay}"

    try:
        return await asyncio.wait_for(fetch(), timeout=timeout)
    except asyncio.TimeoutError:
        return fallback_value


# =============================================================================
# Solution 2.3: Wait for First N
# =============================================================================
async def wait_for_first_n(tasks: list[asyncio.Task], n: int) -> list[Any]:
    results = []
    pending = set(tasks)

    while len(results) < n and pending:
        done, pending = await asyncio.wait(
            pending,
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            if len(results) < n:
                results.append(task.result())

    # Cancel remaining tasks
    for task in pending:
        task.cancel()

    return results


# =============================================================================
# Solution 2.4: Future-based Communication
# =============================================================================
async def producer(future: asyncio.Future, delay: float, value: Any) -> None:
    await asyncio.sleep(delay)
    future.set_result(value)


async def consumer(future: asyncio.Future) -> str:
    result = await future
    return f"Received: {result}"


async def run_producer_consumer(delay: float, value: Any) -> str:
    future = asyncio.Future()

    # Run both concurrently
    _, consumer_result = await asyncio.gather(
        producer(future, delay, value),
        consumer(future)
    )

    return consumer_result


# =============================================================================
# Solution 2.5: Task Callback Collector
# =============================================================================
class TaskCollector:
    def __init__(self):
        self._results = []
        self._tasks = []

    def add_task(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.append(task)

        def callback(t):
            if not t.cancelled() and t.exception() is None:
                self._results.append(t.result())

        task.add_done_callback(callback)
        return task

    def get_results(self):
        return self._results.copy()


async def collect_results(values: list[int]) -> list[int]:
    async def double_with_delay(v):
        await asyncio.sleep(0.1)
        return v * 2

    collector = TaskCollector()

    for v in values:
        collector.add_task(double_with_delay(v))

    # Wait for all tasks
    if collector._tasks:
        await asyncio.gather(*collector._tasks)

    return collector.get_results()


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing cancellable_work:")
        task = asyncio.create_task(cancellable_work("job-1", 5.0))
        await asyncio.sleep(0.1)
        task.cancel()
        result = await task
        print(result)

        print("\nTesting fetch_with_fallback:")
        print(await fetch_with_fallback(0.1, "fallback", 1.0))
        print(await fetch_with_fallback(1.0, "fallback", 0.1))

        print("\nTesting wait_for_first_n:")

        async def work(delay, value):
            await asyncio.sleep(delay)
            return value

        tasks = [
            asyncio.create_task(work(0.3, "slow")),
            asyncio.create_task(work(0.1, "fast")),
            asyncio.create_task(work(0.2, "medium")),
        ]
        results = await wait_for_first_n(tasks, 2)
        print(f"First 2: {results}")

        print("\nTesting producer/consumer:")
        result = await run_producer_consumer(0.1, "Hello")
        print(result)

        print("\nTesting collect_results:")
        results = await collect_results([1, 2, 3])
        print(f"Results: {sorted(results)}")

    asyncio.run(main())
