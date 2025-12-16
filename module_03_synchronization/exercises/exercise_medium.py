"""
Exercise 2 (Medium): Advanced Synchronization Patterns

Your task is to implement more complex synchronization patterns.
Run the tests to verify your solutions:
    python -m pytest module_03_synchronization/exercises/test_medium.py -v
"""

import asyncio
from typing import Any, TypeVar

T = TypeVar('T')


# =============================================================================
# Exercise 2.1: Async Queue Implementation
# =============================================================================
# Create a class called `SimpleAsyncQueue` that:
# - Is bounded (has max size)
# - Has async `put(item)` that blocks if full
# - Has async `get()` that blocks if empty
# - Has `qsize()` method returning current size
# - Has `empty()` method returning if queue is empty
#
# Use asyncio.Condition for synchronization.
#
# Example:
#   queue = SimpleAsyncQueue(maxsize=3)
#   await queue.put("a")
#   await queue.put("b")
#   item = await queue.get()  # "a"
# =============================================================================

class SimpleAsyncQueue:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.2: Read-Write Lock
# =============================================================================
# Create a class called `ReadWriteLock` that:
# - Allows multiple concurrent readers
# - Only one writer at a time
# - Writers have exclusive access (no readers while writing)
# - Has async context managers: read_lock() and write_lock()
#
# Example:
#   rwlock = ReadWriteLock()
#
#   async with rwlock.read_lock():
#       # Multiple readers can be here
#       data = read_data()
#
#   async with rwlock.write_lock():
#       # Only one writer, no readers
#       write_data()
# =============================================================================

class ReadWriteLock:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.3: Async Barrier with Action
# =============================================================================
# Create a class called `ActionBarrier` that:
# - Blocks until N parties arrive
# - When all arrive, executes an action function once
# - Then releases all parties
# - Resets for the next round
#
# Example:
#   results = []
#   def action():
#       results.append("SYNC")
#
#   barrier = ActionBarrier(3, action)
#
#   async def worker(name):
#       results.append(f"{name}-before")
#       await barrier.wait()
#       results.append(f"{name}-after")
#
#   await asyncio.gather(worker("A"), worker("B"), worker("C"))
#   # results contains all "before", then "SYNC", then all "after"
# =============================================================================

class ActionBarrier:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.4: Semaphore with Timeout
# =============================================================================
# Create a class called `TimeoutSemaphore` that:
# - Works like a regular Semaphore
# - Has async `acquire(timeout)` that returns True if acquired, False if timeout
# - Has `release()` method
# - Can be used as async context manager with default timeout
#
# Example:
#   sem = TimeoutSemaphore(2, default_timeout=1.0)
#
#   async with sem:  # Uses default timeout
#       await do_work()
#
#   acquired = await sem.acquire(timeout=0.5)
#   if acquired:
#       try:
#           await do_work()
#       finally:
#           sem.release()
# =============================================================================

class TimeoutSemaphore:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 2.5: Event-based Pub/Sub
# =============================================================================
# Create a class called `AsyncPubSub` that:
# - Has `subscribe(topic)` returning an async iterator
# - Has async `publish(topic, message)` to send to all subscribers
# - Subscribers receive messages published after they subscribe
#
# Example:
#   pubsub = AsyncPubSub()
#
#   async def subscriber(name):
#       async for message in pubsub.subscribe("news"):
#           print(f"{name} got: {message}")
#           if message == "stop":
#               break
#
#   async def publisher():
#       await asyncio.sleep(0.1)
#       await pubsub.publish("news", "Hello!")
#       await pubsub.publish("news", "stop")
#
#   await asyncio.gather(subscriber("A"), subscriber("B"), publisher())
# =============================================================================

class AsyncPubSub:
    # YOUR CODE HERE
    pass
