"""
Exercise 3 (Hard): Advanced Coroutine Patterns

Your task is to implement more complex async patterns.
Run the tests to verify your solutions:
    python -m pytest module_01_coroutines_eventloop/exercises/test_hard.py -v
"""

import asyncio
from typing import Any, Callable, Awaitable


# =============================================================================
# Exercise 3.1: Retry with Exponential Backoff
# =============================================================================
# Create a coroutine called `retry_with_backoff` that:
# - Takes an async function, max_retries (int), and base_delay (float)
# - Calls the function, which may raise an exception
# - If it fails, wait and retry with exponential backoff
# - Delay pattern: base_delay, base_delay*2, base_delay*4, ...
# - If all retries fail, raise the last exception
# - If successful, return the result
#
# Example:
#   attempt = 0
#   async def flaky():
#       nonlocal attempt
#       attempt += 1
#       if attempt < 3:
#           raise ValueError("Failed")
#       return "Success"
#
#   result = await retry_with_backoff(flaky, max_retries=5, base_delay=0.1)
#   # Attempt 1: fails, wait 0.1s
#   # Attempt 2: fails, wait 0.2s
#   # Attempt 3: succeeds, return "Success"
# =============================================================================

async def retry_with_backoff(
    func: Callable[[], Awaitable[Any]],
    max_retries: int,
    base_delay: float
) -> Any:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.2: Concurrent Limit (Semaphore-like)
# =============================================================================
# Create a coroutine called `limited_gather` that:
# - Takes a list of coroutines and a concurrency limit
# - Runs at most `limit` coroutines at the same time
# - Returns all results in order
#
# DO NOT use asyncio.Semaphore (that's for Module 03)
# Instead, process in chunks of size `limit`
#
# Example:
#   # 5 tasks, limit 2
#   # Batch 1: tasks[0], tasks[1] run together
#   # Batch 2: tasks[2], tasks[3] run together
#   # Batch 3: tasks[4] runs alone
# =============================================================================

async def limited_gather(
    coros: list[Awaitable[Any]],
    limit: int
) -> list[Any]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.3: Async Pipeline
# =============================================================================
# Create a coroutine called `pipeline` that:
# - Takes an initial value and a list of async functions (stages)
# - Passes the value through each stage sequentially
# - Each stage transforms the value and passes to the next
# - Returns the final transformed value
#
# Example:
#   async def add_one(x): await asyncio.sleep(0.1); return x + 1
#   async def double(x): await asyncio.sleep(0.1); return x * 2
#   async def to_string(x): await asyncio.sleep(0.1); return str(x)
#
#   result = await pipeline(5, [add_one, double, to_string])
#   # 5 -> add_one -> 6 -> double -> 12 -> to_string -> "12"
# =============================================================================

async def pipeline(
    initial_value: Any,
    stages: list[Callable[[Any], Awaitable[Any]]]
) -> Any:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.4: First Successful
# =============================================================================
# Create a coroutine called `first_successful` that:
# - Takes a list of async functions that might raise exceptions
# - Runs ALL functions concurrently
# - Returns the result of the FIRST function that succeeds
# - If ALL functions fail, raise an Exception with message "All failed"
#
# Key difference from race: here we want the first SUCCESS, not first to finish
# A fast failure should not prevent a slower success from winning
#
# Example:
#   async def fast_fail():
#       await asyncio.sleep(0.1)
#       raise ValueError("Fast fail")
#
#   async def slow_success():
#       await asyncio.sleep(0.3)
#       return "Success!"
#
#   result = await first_successful([fast_fail, slow_success])
#   # fast_fail finishes first but fails
#   # slow_success finishes later but succeeds
#   # Returns "Success!"
# =============================================================================

async def first_successful(
    funcs: list[Callable[[], Awaitable[Any]]]
) -> Any:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.5: Async Event Emitter
# =============================================================================
# Create a class called `AsyncEventEmitter` that:
# - Has an `on(event_name, callback)` method to register async callbacks
# - Has an `emit(event_name, *args)` coroutine that:
#   - Calls all registered callbacks for that event concurrently
#   - Passes *args to each callback
#   - Returns a list of all callback results
# - Multiple callbacks can be registered for the same event
#
# Example:
#   emitter = AsyncEventEmitter()
#
#   async def handler1(x):
#       await asyncio.sleep(0.1)
#       return f"Handler1: {x}"
#
#   async def handler2(x):
#       await asyncio.sleep(0.1)
#       return f"Handler2: {x}"
#
#   emitter.on("data", handler1)
#   emitter.on("data", handler2)
#
#   results = await emitter.emit("data", 42)
#   # ["Handler1: 42", "Handler2: 42"]
# =============================================================================

class AsyncEventEmitter:
    # YOUR CODE HERE
    pass
