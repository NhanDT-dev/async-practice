"""
Exercise 1 (Easy): Async Patterns Basics

Your task is to practice fundamental async patterns.
Run the tests to verify your solutions:
    python -m pytest module_05_advanced_patterns/exercises/test_easy.py -v
"""

import asyncio
from typing import Any, AsyncIterator


# =============================================================================
# Exercise 1.1: Async Context Manager
# =============================================================================
# Create a class called `AsyncTimer` that:
# - Is an async context manager
# - Records the start time when entering
# - Calculates elapsed time when exiting
# - Has `elapsed` property (in seconds)
#
# Example:
#   async with AsyncTimer() as timer:
#       await asyncio.sleep(0.5)
#   print(timer.elapsed)  # ~0.5
# =============================================================================

class AsyncTimer:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.2: Async Iterator
# =============================================================================
# Create an async iterator class called `AsyncCountdown` that:
# - Takes a start number
# - Yields numbers from start down to 1
# - Waits 0.1 seconds between each number
#
# Example:
#   async for num in AsyncCountdown(3):
#       print(num)
#   # Prints: 3, 2, 1 (with 0.1s delays)
# =============================================================================

class AsyncCountdown:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.3: Async Generator
# =============================================================================
# Create an async generator function called `paginate` that:
# - Takes a list of items and page_size
# - Yields pages (lists) of items
# - Simulates delay of 0.1s per page fetch
#
# Example:
#   async for page in paginate([1,2,3,4,5], page_size=2):
#       print(page)
#   # Prints: [1,2], [3,4], [5]
# =============================================================================

async def paginate(items: list, page_size: int) -> AsyncIterator[list]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.4: Async Retry Decorator
# =============================================================================
# Create a decorator called `async_retry` that:
# - Takes max_retries parameter
# - Retries the decorated async function on exception
# - Waits 0.1 seconds between retries
# - Raises the last exception if all retries fail
#
# Example:
#   @async_retry(max_retries=3)
#   async def flaky_function():
#       if random.random() < 0.5:
#           raise ValueError()
#       return "success"
# =============================================================================

def async_retry(max_retries: int):
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.5: Async Resource Manager
# =============================================================================
# Create a function called `managed_resource` that:
# - Is an async context manager (use @asynccontextmanager)
# - Takes a resource_id string
# - "Acquires" resource (0.1s delay) and yields it
# - "Releases" resource (0.1s delay) on exit
# - Logs actions to a provided log list
#
# Example:
#   log = []
#   async with managed_resource("db", log) as resource:
#       print(resource)  # "db"
#   print(log)  # ["acquire:db", "release:db"]
# =============================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource(resource_id: str, log: list):
    # YOUR CODE HERE
    pass
