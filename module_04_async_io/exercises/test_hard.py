"""
Tests for Exercise 3 (Hard): Advanced Async I/O
Run with: python -m pytest module_04_async_io/exercises/test_hard.py -v
"""

import asyncio
import time
import pytest

from exercise_hard import (
    Message,
    AsyncMessageBroker,
    CircuitBreakerOpenError,
    AsyncCircuitBreaker,
    AsyncBatchExecutor,
    AsyncFanOutPipeline,
    AsyncSagaCoordinator,
)


class TestAsyncMessageBroker:
    """Tests for Exercise 3.1: AsyncMessageBroker"""

    def test_publish_subscribe(self):
        async def check():
            broker = AsyncMessageBroker()
            received = []

            async def consumer():
                sub_id, messages = broker.create_subscriber("topic")
                async for msg in messages:
                    received.append(msg.data)
                    await msg.ack()
                    if msg.data == "stop":
                        break

            async def publisher():
                await asyncio.sleep(0.05)
                await broker.publish("topic", "hello")
                await broker.publish("topic", "stop")

            await asyncio.gather(consumer(), publisher())
            assert received == ["hello", "stop"]

        asyncio.run(check())

    def test_multiple_subscribers(self):
        async def check():
            broker = AsyncMessageBroker()
            received_a = []
            received_b = []

            async def consumer(storage):
                sub_id, messages = broker.create_subscriber("topic")
                async for msg in messages:
                    storage.append(msg.data)
                    await msg.ack()
                    if msg.data == "stop":
                        break

            async def publisher():
                await asyncio.sleep(0.05)
                await broker.publish("topic", "msg")
                await broker.publish("topic", "stop")

            await asyncio.gather(
                consumer(received_a),
                consumer(received_b),
                publisher()
            )

            assert received_a == ["msg", "stop"]
            assert received_b == ["msg", "stop"]

        asyncio.run(check())


class TestAsyncCircuitBreaker:
    """Tests for Exercise 3.2: AsyncCircuitBreaker"""

    def test_normal_operation(self):
        async def check():
            cb = AsyncCircuitBreaker(failure_threshold=3, reset_timeout=1.0)

            async def success():
                return "ok"

            result = await cb.call(success())
            assert result == "ok"
            assert cb.state == "CLOSED"

        asyncio.run(check())

    def test_opens_after_failures(self):
        async def check():
            cb = AsyncCircuitBreaker(failure_threshold=3, reset_timeout=1.0)

            async def fail():
                raise ValueError("error")

            # Fail 3 times
            for _ in range(3):
                try:
                    await cb.call(fail())
                except ValueError:
                    pass

            assert cb.state == "OPEN"

            # Next call should raise CircuitBreakerOpenError
            with pytest.raises(CircuitBreakerOpenError):
                await cb.call(fail())

        asyncio.run(check())

    def test_half_open_recovery(self):
        async def check():
            cb = AsyncCircuitBreaker(failure_threshold=2, reset_timeout=0.1)

            async def fail():
                raise ValueError()

            async def success():
                return "ok"

            # Open the circuit
            for _ in range(2):
                try:
                    await cb.call(fail())
                except ValueError:
                    pass

            assert cb.state == "OPEN"

            # Wait for reset timeout
            await asyncio.sleep(0.15)

            # Should be HALF_OPEN, allow one request
            result = await cb.call(success())
            assert result == "ok"
            assert cb.state == "CLOSED"

        asyncio.run(check())


class TestAsyncBatchExecutor:
    """Tests for Exercise 3.3: AsyncBatchExecutor"""

    def test_batch_on_size(self):
        async def check():
            processed = []

            async def process_batch(items):
                processed.append(len(items))
                return [x * 2 for x in items]

            executor = AsyncBatchExecutor(
                batch_size=3,
                max_wait_time=10.0,
                batch_processor=process_batch
            )

            futures = []
            for i in range(3):
                f = await executor.add(i)
                futures.append(f)

            results = await asyncio.gather(*futures)
            assert results == [0, 2, 4]
            assert 3 in processed  # Batch of 3 processed

        asyncio.run(check())

    def test_batch_on_timeout(self):
        async def check():
            async def process_batch(items):
                return [x * 2 for x in items]

            executor = AsyncBatchExecutor(
                batch_size=100,  # Large size, won't trigger
                max_wait_time=0.1,
                batch_processor=process_batch
            )

            f = await executor.add(5)
            result = await f
            assert result == 10

        asyncio.run(check())

    def test_flush(self):
        async def check():
            async def process_batch(items):
                return [x * 2 for x in items]

            executor = AsyncBatchExecutor(
                batch_size=100,
                max_wait_time=100.0,
                batch_processor=process_batch
            )

            f1 = await executor.add(1)
            f2 = await executor.add(2)

            await executor.flush()

            r1 = await f1
            r2 = await f2
            assert r1 == 2
            assert r2 == 4

        asyncio.run(check())


class TestAsyncFanOutPipeline:
    """Tests for Exercise 3.4: AsyncFanOutPipeline"""

    def test_processes_all(self):
        async def check():
            async def source():
                for i in range(5):
                    yield i

            async def worker(item):
                await asyncio.sleep(0.05)
                return item * 2

            pipeline = AsyncFanOutPipeline()
            results = await pipeline.run(source(), worker, num_workers=2)

            assert sorted(results) == [0, 2, 4, 6, 8]

        asyncio.run(check())

    def test_parallel_workers(self):
        async def check():
            running = 0
            max_running = 0

            async def source():
                for i in range(10):
                    yield i

            async def worker(item):
                nonlocal running, max_running
                running += 1
                max_running = max(max_running, running)
                await asyncio.sleep(0.05)
                running -= 1
                return item

            pipeline = AsyncFanOutPipeline()
            await pipeline.run(source(), worker, num_workers=3)

            assert max_running <= 3

        asyncio.run(check())


class TestAsyncSagaCoordinator:
    """Tests for Exercise 3.5: AsyncSagaCoordinator"""

    def test_successful_saga(self):
        async def check():
            log = []

            async def step1():
                log.append("step1")
                return "result1"

            async def comp1(result):
                log.append("comp1")

            async def step2():
                log.append("step2")
                return "result2"

            async def comp2(result):
                log.append("comp2")

            saga = AsyncSagaCoordinator()
            saga.add_step(step1, comp1)
            saga.add_step(step2, comp2)

            success, results = await saga.execute()

            assert success is True
            assert results == ["result1", "result2"]
            assert "comp1" not in log  # No compensation on success

        asyncio.run(check())

    def test_rollback_on_failure(self):
        async def check():
            log = []

            async def step1():
                log.append("step1")
                return "r1"

            async def comp1(result):
                log.append("comp1")

            async def step2():
                log.append("step2")
                raise ValueError("step2 failed")

            async def comp2(result):
                log.append("comp2")

            saga = AsyncSagaCoordinator()
            saga.add_step(step1, comp1)
            saga.add_step(step2, comp2)

            success, error = await saga.execute()

            assert success is False
            # Compensation should run in reverse order
            assert "comp1" in log
            # step2 failed so comp2 may or may not run depending on implementation

        asyncio.run(check())

    def test_compensation_order(self):
        async def check():
            compensation_order = []

            async def step(n):
                return n

            async def comp(n):
                compensation_order.append(n)

            async def failing_step():
                raise ValueError()

            async def failing_comp(r):
                compensation_order.append("fail")

            saga = AsyncSagaCoordinator()
            saga.add_step(lambda: step(1), lambda r: comp(1))
            saga.add_step(lambda: step(2), lambda r: comp(2))
            saga.add_step(lambda: step(3), lambda r: comp(3))
            saga.add_step(failing_step, failing_comp)

            success, _ = await saga.execute()

            assert success is False
            # Compensations should run in reverse: 3, 2, 1
            assert compensation_order == [3, 2, 1]

        asyncio.run(check())
