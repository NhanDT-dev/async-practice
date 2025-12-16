"""
Exercise 2 (Medium): Concurrent Execution with gather

Your task is to implement coroutines that run concurrently.
Run the tests to verify your solutions:
    python -m pytest module_01_coroutines_eventloop/exercises/test_medium.py -v
"""

import asyncio


# =============================================================================
# Exercise 2.1: Parallel Fetch
# =============================================================================
# Create a coroutine called `fetch_all` that:
# - Takes a list of URLs (strings)
# - "Fetches" each URL concurrently (simulate with 0.1s delay per URL)
# - Returns a list of results in the format "Content from {url}"
#
# Requirements:
# - Must use asyncio.gather() to run concurrently
# - Total time should be ~0.1s regardless of URL count (concurrent!)
#
# Example:
#   fetch_all(["url1", "url2", "url3"])
#   -> ["Content from url1", "Content from url2", "Content from url3"]
#   -> Takes ~0.1s, NOT 0.3s
# =============================================================================

async def fetch_all(urls: list[str]) -> list[str]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.2: Fastest Wins
# =============================================================================
# Create a coroutine called `race` that:
# - Takes a list of (name, delay) tuples
# - Runs all "competitors" concurrently
# - Each competitor waits for their delay then "finishes"
# - Returns the name of the FIRST competitor to finish
#
# Hint: Use asyncio.wait() with return_when=FIRST_COMPLETED
#       or think creatively with gather
#
# Example:
#   race([("Alice", 0.3), ("Bob", 0.1), ("Charlie", 0.2)])
#   -> "Bob" (because Bob has the shortest delay)
# =============================================================================

async def race(competitors: list[tuple[str, float]]) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.3: Timeout Handler
# =============================================================================
# Create a coroutine called `fetch_with_timeout` that:
# - Takes a url (str) and timeout (float)
# - Simulates fetching by waiting 0.5 seconds
# - If the fetch completes before timeout, return "Success: {url}"
# - If timeout occurs first, return "Timeout: {url}"
#
# Hint: Use asyncio.wait_for() with asyncio.TimeoutError
#
# Example:
#   fetch_with_timeout("example.com", 1.0) -> "Success: example.com"
#   fetch_with_timeout("example.com", 0.2) -> "Timeout: example.com"
# =============================================================================

async def fetch_with_timeout(url: str, timeout: float) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.4: Batch Processor
# =============================================================================
# Create a coroutine called `process_batch` that:
# - Takes a list of items (strings) and batch_size (int)
# - Processes items in batches of batch_size concurrently
# - Each item takes 0.1 seconds to process
# - Processing an item returns "Processed: {item}"
# - Returns all results in order
#
# Example:
#   process_batch(["a", "b", "c", "d", "e"], batch_size=2)
#   -> First batch ["a", "b"] runs concurrently (0.1s)
#   -> Second batch ["c", "d"] runs concurrently (0.1s)
#   -> Third batch ["e"] runs (0.1s)
#   -> Total time: ~0.3s
#   -> Returns ["Processed: a", "Processed: b", "Processed: c",
#               "Processed: d", "Processed: e"]
# =============================================================================

async def process_batch(items: list[str], batch_size: int) -> list[str]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.5: Parallel Map
# =============================================================================
# Create a coroutine called `async_map` that:
# - Takes a list of integers and an async function
# - Applies the function to each integer concurrently
# - Returns the results in the same order as input
#
# For testing, we'll provide these helper functions:
#
# async def double(x: int) -> int:
#     await asyncio.sleep(0.1)
#     return x * 2
#
# async def square(x: int) -> int:
#     await asyncio.sleep(0.1)
#     return x ** 2
#
# Example:
#   async_map([1, 2, 3], double) -> [2, 4, 6]  (takes ~0.1s)
#   async_map([1, 2, 3], square) -> [1, 4, 9]  (takes ~0.1s)
# =============================================================================

from typing import Callable, Awaitable

async def async_map(
    items: list[int],
    func: Callable[[int], Awaitable[int]]
) -> list[int]:
    # YOUR CODE HERE
    pass
