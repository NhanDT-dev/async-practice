"""
Solutions for Exercise 3 (Hard): Advanced Async I/O

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
from typing import Any, Callable, Awaitable
from collections import defaultdict
from enum import Enum


# =============================================================================
# Solution 3.1: Async Pub/Sub Message Broker
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
    def __init__(self):
        self._subscribers: dict[str, dict[int, asyncio.Queue]] = defaultdict(dict)
        self._next_id = 0

    def create_subscriber(self, topic: str):
        sub_id = self._next_id
        self._next_id += 1
        queue = asyncio.Queue()
        self._subscribers[topic][sub_id] = queue

        async def message_iterator():
            while True:
                msg = await queue.get()
                yield msg

        return sub_id, message_iterator()

    async def publish(self, topic: str, data: Any):
        for queue in self._subscribers[topic].values():
            ack_event = asyncio.Event()

            async def ack_callback():
                ack_event.set()

            msg = Message(data, ack_callback)
            await queue.put(msg)

    async def unsubscribe(self, topic: str, subscriber_id: int):
        if topic in self._subscribers and subscriber_id in self._subscribers[topic]:
            del self._subscribers[topic][subscriber_id]


# =============================================================================
# Solution 3.2: Async Circuit Breaker
# =============================================================================
class CircuitBreakerOpenError(Exception):
    pass


class AsyncCircuitBreaker:
    def __init__(self, failure_threshold: int, reset_timeout: float):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failures = 0
        self._state = "CLOSED"
        self._last_failure_time = 0

    @property
    def state(self) -> str:
        if self._state == "OPEN":
            if time.monotonic() - self._last_failure_time >= self.reset_timeout:
                self._state = "HALF_OPEN"
        return self._state

    async def call(self, coro):
        current_state = self.state

        if current_state == "OPEN":
            raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await coro
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self._failures = 0
        self._state = "CLOSED"

    def _on_failure(self):
        self._failures += 1
        self._last_failure_time = time.monotonic()
        if self._failures >= self.failure_threshold:
            self._state = "OPEN"


# =============================================================================
# Solution 3.3: Async Batch Executor
# =============================================================================
class AsyncBatchExecutor:
    def __init__(
        self,
        batch_size: int,
        max_wait_time: float,
        batch_processor: Callable[[list], Awaitable[list]]
    ):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.batch_processor = batch_processor
        self._items = []
        self._futures = []
        self._lock = asyncio.Lock()
        self._timer_task = None

    async def add(self, item) -> asyncio.Future:
        future = asyncio.Future()

        async with self._lock:
            self._items.append(item)
            self._futures.append(future)

            if len(self._items) >= self.batch_size:
                await self._process_batch()
            elif self._timer_task is None:
                self._timer_task = asyncio.create_task(self._timer())

        return future

    async def _timer(self):
        await asyncio.sleep(self.max_wait_time)
        async with self._lock:
            if self._items:
                await self._process_batch()
            self._timer_task = None

    async def _process_batch(self):
        items = self._items
        futures = self._futures
        self._items = []
        self._futures = []

        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None

        try:
            results = await self.batch_processor(items)
            for future, result in zip(futures, results):
                future.set_result(result)
        except Exception as e:
            for future in futures:
                future.set_exception(e)

    async def flush(self):
        async with self._lock:
            if self._items:
                await self._process_batch()


# =============================================================================
# Solution 3.4: Async Pipeline with Fan-out/Fan-in
# =============================================================================
class AsyncFanOutPipeline:
    async def run(self, source, worker_func, num_workers: int) -> list:
        input_queue = asyncio.Queue()
        output_queue = asyncio.Queue()
        done = asyncio.Event()
        workers_done = 0
        lock = asyncio.Lock()

        async def worker():
            nonlocal workers_done
            while True:
                try:
                    item = await asyncio.wait_for(input_queue.get(), timeout=0.1)
                    result = await worker_func(item)
                    await output_queue.put(result)
                    input_queue.task_done()
                except asyncio.TimeoutError:
                    if done.is_set() and input_queue.empty():
                        break

            async with lock:
                workers_done += 1
                if workers_done == num_workers:
                    await output_queue.put(None)  # Sentinel

        async def producer():
            async for item in source:
                await input_queue.put(item)
            done.set()

        # Start workers
        worker_tasks = [asyncio.create_task(worker()) for _ in range(num_workers)]

        # Start producer
        producer_task = asyncio.create_task(producer())

        # Collect results
        results = []
        while True:
            result = await output_queue.get()
            if result is None:
                break
            results.append(result)

        await producer_task
        await asyncio.gather(*worker_tasks)

        return results


# =============================================================================
# Solution 3.5: Async Saga Coordinator
# =============================================================================
class AsyncSagaCoordinator:
    def __init__(self):
        self._steps = []

    def add_step(
        self,
        action: Callable[[], Awaitable[Any]],
        compensation: Callable[[Any], Awaitable[None]]
    ):
        self._steps.append((action, compensation))

    async def execute(self):
        results = []
        completed_steps = []

        for i, (action, compensation) in enumerate(self._steps):
            try:
                result = await action()
                results.append(result)
                completed_steps.append((result, compensation))
            except Exception as e:
                # Rollback in reverse order
                for result, comp in reversed(completed_steps):
                    try:
                        await comp(result)
                    except Exception:
                        pass  # Log but continue rollback

                return (False, e)

        return (True, results)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("Testing AsyncMessageBroker:")
        print("=" * 60)
        broker = AsyncMessageBroker()

        async def consumer():
            sub_id, messages = broker.create_subscriber("topic")
            async for msg in messages:
                print(f"  Received: {msg.data}")
                await msg.ack()
                if msg.data == "stop":
                    break

        async def publisher():
            await asyncio.sleep(0.1)
            await broker.publish("topic", "hello")
            await broker.publish("topic", "world")
            await broker.publish("topic", "stop")

        await asyncio.gather(consumer(), publisher())

        print("\n" + "=" * 60)
        print("Testing AsyncCircuitBreaker:")
        print("=" * 60)
        cb = AsyncCircuitBreaker(failure_threshold=2, reset_timeout=0.5)

        async def fail():
            raise ValueError("fail")

        for i in range(3):
            try:
                await cb.call(fail())
            except CircuitBreakerOpenError:
                print(f"  Attempt {i+1}: Circuit open!")
            except ValueError:
                print(f"  Attempt {i+1}: Failed, state={cb.state}")

        print("\n" + "=" * 60)
        print("Testing AsyncBatchExecutor:")
        print("=" * 60)

        async def process_batch(items):
            print(f"  Processing batch of {len(items)}")
            return [x * 2 for x in items]

        executor = AsyncBatchExecutor(
            batch_size=3,
            max_wait_time=1.0,
            batch_processor=process_batch
        )

        futures = []
        for i in range(5):
            f = await executor.add(i)
            futures.append(f)
        await executor.flush()
        results = await asyncio.gather(*futures)
        print(f"  Results: {results}")

        print("\n" + "=" * 60)
        print("Testing AsyncFanOutPipeline:")
        print("=" * 60)

        async def source():
            for i in range(5):
                yield i

        async def worker(item):
            await asyncio.sleep(0.05)
            return item * 2

        pipeline = AsyncFanOutPipeline()
        results = await pipeline.run(source(), worker, num_workers=2)
        print(f"  Results: {sorted(results)}")

        print("\n" + "=" * 60)
        print("Testing AsyncSagaCoordinator:")
        print("=" * 60)

        async def step1():
            print("  Step 1 executing")
            return "result1"

        async def comp1(r):
            print(f"  Compensating step 1 (result was {r})")

        async def step2():
            print("  Step 2 failing!")
            raise ValueError("Step 2 failed")

        async def comp2(r):
            print("  Compensating step 2")

        saga = AsyncSagaCoordinator()
        saga.add_step(step1, comp1)
        saga.add_step(step2, comp2)

        success, result = await saga.execute()
        print(f"  Success: {success}")

    asyncio.run(main())
