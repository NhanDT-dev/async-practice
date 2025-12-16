"""
Exercise 3 (Hard): Advanced Async I/O

Your task is to implement complex async I/O systems.
Run the tests to verify your solutions:
    python -m pytest module_04_async_io/exercises/test_hard.py -v
"""

import asyncio
from typing import Any, Callable, Awaitable, AsyncIterator
from collections import defaultdict


# =============================================================================
# Exercise 3.1: Async Pub/Sub Message Broker
# =============================================================================
# Create a class called `AsyncMessageBroker` that:
# - Supports topics with multiple subscribers
# - Has async `subscribe(topic)` returning async iterator
# - Has async `publish(topic, message)` to broadcast
# - Has async `unsubscribe(topic, subscriber_id)` to remove subscriber
# - Has `create_subscriber(topic)` that returns (subscriber_id, async_iterator)
# - Supports message acknowledgment (subscribers must ack before getting next)
#
# Example:
#   broker = AsyncMessageBroker()
#
#   async def consumer(topic):
#       sub_id, messages = broker.create_subscriber(topic)
#       async for msg in messages:
#           print(f"Got: {msg.data}")
#           await msg.ack()  # Acknowledge receipt
#
#   await broker.publish("news", "Hello World!")
# =============================================================================

class Message:
    def __init__(self, data: Any, ack_callback: Callable[[], Awaitable[None]]):
        self.data = data
        self._ack_callback = ack_callback
        self._acked = False

    async def ack(self):
        if not self._acked:
            self._acked = True
            await self._ack_callback()


class AsyncMessageBroker:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.2: Async Circuit Breaker
# =============================================================================
# Create a class called `AsyncCircuitBreaker` that:
# - Wraps async functions with circuit breaker pattern
# - States: CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
# - Opens after `failure_threshold` consecutive failures
# - Stays open for `reset_timeout` seconds
# - In HALF_OPEN, allows one request to test recovery
# - Has `call(coro)` method to execute with circuit breaker
# - Has `state` property showing current state
#
# Example:
#   cb = AsyncCircuitBreaker(failure_threshold=3, reset_timeout=5)
#
#   async def unreliable_api():
#       # May raise exception
#       pass
#
#   try:
#       result = await cb.call(unreliable_api())
#   except CircuitBreakerOpenError:
#       print("Circuit is open, not attempting call")
# =============================================================================

class CircuitBreakerOpenError(Exception):
    pass


class AsyncCircuitBreaker:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.3: Async Batch Executor
# =============================================================================
# Create a class called `AsyncBatchExecutor` that:
# - Collects items and processes them in batches
# - Has async `add(item)` that may trigger batch processing
# - Has async `flush()` to process remaining items
# - Processes batch when batch_size reached OR max_wait_time elapsed
# - Has batch_processor callback: async def process(items) -> results
# - Returns future from add() that resolves to item's result
#
# Example:
#   async def process_batch(items):
#       return [item * 2 for item in items]
#
#   executor = AsyncBatchExecutor(
#       batch_size=10,
#       max_wait_time=1.0,
#       batch_processor=process_batch
#   )
#
#   future = await executor.add(5)
#   result = await future  # Gets 10 when batch is processed
# =============================================================================

class AsyncBatchExecutor:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.4: Async Pipeline with Fan-out/Fan-in
# =============================================================================
# Create a class called `AsyncFanOutPipeline` that:
# - Has source stage that produces items
# - Has parallel worker stage with N workers
# - Has sink stage that collects results
# - Has `run(source, worker_func, num_workers)` method
# - Returns collected results
#
# Example:
#   async def source():
#       for i in range(10):
#           yield i
#
#   async def worker(item):
#       await asyncio.sleep(0.1)
#       return item * 2
#
#   pipeline = AsyncFanOutPipeline()
#   results = await pipeline.run(source(), worker, num_workers=3)
#   # All items processed by 3 workers in parallel
# =============================================================================

class AsyncFanOutPipeline:
    # YOUR CODE HERE
    pass


# =============================================================================
# Exercise 3.5: Async Saga Coordinator
# =============================================================================
# Create a class called `AsyncSagaCoordinator` that:
# - Executes a sequence of async operations
# - Each operation has a compensating action (rollback)
# - If any operation fails, runs compensations in reverse order
# - Has `add_step(action, compensation)` to add steps
# - Has async `execute()` that runs saga
# - Returns (success, results_or_error)
#
# Example:
#   saga = AsyncSagaCoordinator()
#
#   async def create_order():
#       return order_id
#
#   async def cancel_order(order_id):
#       # Compensation
#       pass
#
#   saga.add_step(create_order, cancel_order)
#   saga.add_step(charge_payment, refund_payment)
#   saga.add_step(update_inventory, restore_inventory)
#
#   success, result = await saga.execute()
#   if not success:
#       print("Saga failed and rolled back")
# =============================================================================

class AsyncSagaCoordinator:
    # YOUR CODE HERE
    pass
