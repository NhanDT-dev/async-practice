"""
Exercise 1 (Easy): Basic Synchronization Primitives

Your task is to learn the basic usage of Lock, Event, and Semaphore.
Run the tests to verify your solutions:
    python -m pytest module_03_synchronization/exercises/test_easy.py -v
"""

import asyncio


# =============================================================================
# Exercise 1.1: Safe Counter with Lock
# =============================================================================
# Create a class called `SafeCounter` that:
# - Has an initial value of 0
# - Has an async `increment()` method that safely increments the counter
# - Has a `value` property to get the current value
# - Uses asyncio.Lock to ensure thread-safe increments
#
# The increment should simulate some async work with a brief sleep.
#
# Example:
#   counter = SafeCounter()
#   await asyncio.gather(*[counter.increment() for _ in range(100)])
#   print(counter.value)  # Always 100!
# =============================================================================

class SafeCounter:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.2: Event-based Start Signal
# =============================================================================
# Create a coroutine called `run_with_start_signal` that:
# - Takes a list of worker names and a start_event (asyncio.Event)
# - Each worker waits for the start_event before starting
# - After start, each worker "works" for 0.1 seconds
# - Returns dict mapping worker names to their completion times
#
# Example:
#   event = asyncio.Event()
#
#   async def trigger():
#       await asyncio.sleep(0.5)
#       event.set()
#
#   results = await asyncio.gather(
#       run_with_start_signal(["A", "B"], event),
#       trigger()
#   )
#   # Workers start after 0.5s, complete after 0.6s
# =============================================================================

async def run_with_start_signal(
    worker_names: list[str],
    start_event: asyncio.Event
) -> dict[str, float]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.3: Limited Concurrent Access
# =============================================================================
# Create a coroutine called `rate_limited_fetch` that:
# - Takes a list of urls and max_concurrent (int)
# - "Fetches" each URL (simulate with 0.1s delay)
# - Only max_concurrent fetches run at a time
# - Returns list of results in format "Fetched: {url}"
#
# Use asyncio.Semaphore to limit concurrency.
#
# Example:
#   results = await rate_limited_fetch(["a", "b", "c", "d"], max_concurrent=2)
#   # Only 2 fetch at a time, total time ~0.2s for 4 urls
# =============================================================================

async def rate_limited_fetch(urls: list[str], max_concurrent: int) -> list[str]:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.4: Event Toggle
# =============================================================================
# Create a class called `AsyncToggle` that:
# - Starts in "off" state
# - Has async `wait_for_on()` that waits until toggle is on
# - Has `turn_on()` method
# - Has `turn_off()` method
# - Has `is_on` property
#
# Example:
#   toggle = AsyncToggle()
#
#   async def waiter():
#       await toggle.wait_for_on()
#       print("Toggle is on!")
#
#   task = asyncio.create_task(waiter())
#   await asyncio.sleep(0.1)
#   toggle.turn_on()  # Waiter now continues
# =============================================================================

class AsyncToggle:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 1.5: Mutex-protected Resource
# =============================================================================
# Create a class called `SharedResource` that:
# - Has a `data` attribute (initially empty list)
# - Has async `add(item)` that appends item (with 0.05s delay simulation)
# - Has async `get_all()` that returns copy of data
# - Uses Lock to protect access
#
# Multiple concurrent adds should all succeed without data corruption.
#
# Example:
#   resource = SharedResource()
#   await asyncio.gather(*[resource.add(i) for i in range(10)])
#   data = await resource.get_all()
#   print(len(data))  # Always 10
# =============================================================================

class SharedResource:
    # YOUR CODE HERE
    pass
