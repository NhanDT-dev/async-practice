"""
Exercise 1 (Easy): Basic Async I/O

Your task is to learn basic async I/O operations.
Run the tests to verify your solutions:
    python -m pytest module_04_async_io/exercises/test_easy.py -v

Note: These exercises use simulation to avoid external dependencies.
"""

import asyncio
from typing import Any


# =============================================================================
# Exercise 1.1: Simulated File Reader
# =============================================================================
# Create a coroutine called `read_file_async` that:
# - Takes a filename and simulated content dict
# - Simulates async file reading with 0.1s delay
# - Returns the content for that filename
# - Raises FileNotFoundError if filename not in dict
#
# Example:
#   files = {"a.txt": "Hello", "b.txt": "World"}
#   content = await read_file_async("a.txt", files)
#   # Returns "Hello" after 0.1s delay
# =============================================================================

async def read_file_async(filename: str, file_contents: dict[str, str]) -> str:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.2: Simulated HTTP Client
# =============================================================================
# Create a class called `MockHttpClient` that:
# - Is initialized with a dict of url -> response mappings
# - Has async `get(url)` method that:
#   - Simulates network delay of 0.1s
#   - Returns the response for that URL
#   - Returns {"error": "Not Found"} for unknown URLs
# - Has async `post(url, data)` method that:
#   - Simulates network delay of 0.1s
#   - Returns {"status": "created", "data": data}
#
# Example:
#   responses = {"http://api/users": {"users": []}}
#   client = MockHttpClient(responses)
#   result = await client.get("http://api/users")
#   # Returns {"users": []}
# =============================================================================

class MockHttpClient:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.3: Parallel File Reader
# =============================================================================
# Create a coroutine called `read_files_parallel` that:
# - Takes a list of filenames and a content dict
# - Reads all files concurrently using read_file_async
# - Returns dict mapping filename -> content
# - Skips files that don't exist (no error)
#
# Example:
#   files = {"a.txt": "A", "b.txt": "B"}
#   results = await read_files_parallel(["a.txt", "c.txt"], files)
#   # Returns {"a.txt": "A"} (c.txt skipped)
# =============================================================================

async def read_files_parallel(
    filenames: list[str],
    file_contents: dict[str, str]
) -> dict[str, str]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.4: API Fetcher with Retry
# =============================================================================
# Create a coroutine called `fetch_with_retry` that:
# - Takes a MockHttpClient, url, and max_retries
# - Tries to fetch the URL
# - If response contains "error", retry up to max_retries times
# - Wait 0.05s between retries
# - Returns the response (even if error after all retries)
#
# For testing, we'll use a client that fails N times then succeeds.
#
# Example:
#   client = MockHttpClient({"url": {"data": "ok"}})
#   result = await fetch_with_retry(client, "url", max_retries=3)
#   # Returns {"data": "ok"}
# =============================================================================

async def fetch_with_retry(
    client: MockHttpClient,
    url: str,
    max_retries: int
) -> dict:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.5: Batch Processor
# =============================================================================
# Create a coroutine called `process_batch` that:
# - Takes a list of items and an async processor function
# - Processes all items concurrently
# - Returns list of results in same order as input
#
# The processor function signature: async def processor(item) -> result
#
# Example:
#   async def double(x):
#       await asyncio.sleep(0.1)
#       return x * 2
#
#   results = await process_batch([1, 2, 3], double)
#   # Returns [2, 4, 6]
# =============================================================================

from typing import Callable, Awaitable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

async def process_batch(
    items: list[T],
    processor: Callable[[T], Awaitable[R]]
) -> list[R]:
    # YOUR CODE HERE
    pass
