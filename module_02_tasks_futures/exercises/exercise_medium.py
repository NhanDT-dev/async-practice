"""
Exercise 2 (Medium): Task Management and Futures

Your task is to work with task cancellation, futures, and waiting patterns.
Run the tests to verify your solutions:
    python -m pytest module_02_tasks_futures/exercises/test_medium.py -v
"""

import asyncio
from typing import Any


# =============================================================================
# Exercise 2.1: Cancellation Handler
# =============================================================================
# Create a coroutine called `cancellable_work` that:
# - Takes a work_id (str) and duration (float)
# - Simulates work by sleeping for `duration` seconds
# - If cancelled, returns f"{work_id}: cancelled"
# - If completed, returns f"{work_id}: completed"
#
# Important: Handle CancelledError properly!
#
# Example:
#   task = asyncio.create_task(cancellable_work("job-1", 5.0))
#   await asyncio.sleep(0.1)
#   task.cancel()
#   result = await task  # "job-1: cancelled"
# =============================================================================

async def cancellable_work(work_id: str, duration: float) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.2: Timeout with Fallback
# =============================================================================
# Create a coroutine called `fetch_with_fallback` that:
# - Takes primary_delay (float), fallback_value (str), timeout (float)
# - Tries to "fetch" by waiting primary_delay seconds
# - If successful (within timeout), returns "primary: {primary_delay}"
# - If timeout, returns the fallback_value
#
# Use asyncio.wait_for() for timeout handling
#
# Example:
#   result = await fetch_with_fallback(0.5, "default", 1.0)
#   # Returns "primary: 0.5" (completed within timeout)
#
#   result = await fetch_with_fallback(2.0, "default", 0.5)
#   # Returns "default" (timeout occurred)
# =============================================================================

async def fetch_with_fallback(
    primary_delay: float,
    fallback_value: str,
    timeout: float
) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.3: Wait for First N
# =============================================================================
# Create a coroutine called `wait_for_first_n` that:
# - Takes a list of tasks and n (int)
# - Waits until n tasks complete
# - Returns results from the first n completed tasks
# - Cancels remaining tasks
#
# Hint: Use asyncio.wait() with return_when=FIRST_COMPLETED in a loop
#
# Example:
#   async def work(delay, value):
#       await asyncio.sleep(delay)
#       return value
#
#   tasks = [
#       asyncio.create_task(work(0.3, "slow")),
#       asyncio.create_task(work(0.1, "fast")),
#       asyncio.create_task(work(0.2, "medium")),
#   ]
#   results = await wait_for_first_n(tasks, 2)
#   # Returns ["fast", "medium"] (first 2 to complete)
# =============================================================================

async def wait_for_first_n(tasks: list[asyncio.Task], n: int) -> list[Any]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.4: Future-based Communication
# =============================================================================
# Create two coroutines that communicate via a Future:
#
# `async def producer(future, delay, value)`:
#   - Waits for `delay` seconds
#   - Sets `value` as the future's result
#
# `async def consumer(future)`:
#   - Waits for the future to have a result
#   - Returns f"Received: {result}"
#
# Create a coroutine called `run_producer_consumer` that:
#   - Creates a Future
#   - Runs producer and consumer concurrently
#   - Returns the consumer's result
#
# Example:
#   result = await run_producer_consumer(0.1, "Hello")
#   # Returns "Received: Hello"
# =============================================================================

async def producer(future: asyncio.Future, delay: float, value: Any) -> None:
    # YOUR CODE HERE
    pass


async def consumer(future: asyncio.Future) -> str:
    # YOUR CODE HERE
    pass


async def run_producer_consumer(delay: float, value: Any) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.5: Task Callback Collector
# =============================================================================
# Create a class called `TaskCollector` that:
# - Has a method `add_task(coro)` that creates a task and adds a callback
# - Has a method `get_results()` that returns all collected results
# - Uses callbacks to collect results (not awaiting)
#
# Create a coroutine `collect_results` that:
# - Takes a list of values
# - Creates tasks that double each value (with 0.1s delay)
# - Uses TaskCollector to collect results via callbacks
# - Returns all results after all tasks complete
#
# Example:
#   results = await collect_results([1, 2, 3])
#   # Returns [2, 4, 6] (order may vary)
# =============================================================================

class TaskCollector:
    # YOUR CODE HERE
    pass


async def collect_results(values: list[int]) -> list[int]:
    # YOUR CODE HERE
    pass
