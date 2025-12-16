"""
Tests for Exercise 2 (Medium): Task Management and Futures
Run with: python -m pytest module_02_tasks_futures/exercises/test_medium.py -v
"""

import asyncio
import time
import pytest

from exercise_medium import (
    cancellable_work,
    fetch_with_fallback,
    wait_for_first_n,
    producer,
    consumer,
    run_producer_consumer,
    TaskCollector,
    collect_results,
)


class TestCancellableWork:
    """Tests for Exercise 2.1: cancellable_work"""

    def test_completes_normally(self):
        async def check():
            result = await cancellable_work("job-1", 0.1)
            assert result == "job-1: completed"

        asyncio.run(check())

    def test_handles_cancellation(self):
        async def check():
            task = asyncio.create_task(cancellable_work("job-2", 5.0))
            await asyncio.sleep(0.05)
            task.cancel()
            result = await task
            assert result == "job-2: cancelled"

        asyncio.run(check())

    def test_different_ids(self):
        async def check():
            task = asyncio.create_task(cancellable_work("test-job", 5.0))
            await asyncio.sleep(0.05)
            task.cancel()
            result = await task
            assert "test-job" in result

        asyncio.run(check())


class TestFetchWithFallback:
    """Tests for Exercise 2.2: fetch_with_fallback"""

    def test_returns_primary_when_fast(self):
        result = asyncio.run(fetch_with_fallback(0.1, "fallback", 1.0))
        assert result == "primary: 0.1"

    def test_returns_fallback_on_timeout(self):
        result = asyncio.run(fetch_with_fallback(1.0, "default", 0.1))
        assert result == "default"

    def test_timing_respects_timeout(self):
        start = time.time()
        asyncio.run(fetch_with_fallback(5.0, "timeout", 0.1))
        elapsed = time.time() - start
        assert elapsed < 0.2, f"Should timeout quickly, got {elapsed}s"


class TestWaitForFirstN:
    """Tests for Exercise 2.3: wait_for_first_n"""

    def test_returns_n_results(self):
        async def work(delay, value):
            await asyncio.sleep(delay)
            return value

        async def check():
            tasks = [
                asyncio.create_task(work(0.1, "a")),
                asyncio.create_task(work(0.1, "b")),
                asyncio.create_task(work(0.1, "c")),
            ]
            results = await wait_for_first_n(tasks, 2)
            assert len(results) == 2

        asyncio.run(check())

    def test_returns_fastest(self):
        async def work(delay, value):
            await asyncio.sleep(delay)
            return value

        async def check():
            tasks = [
                asyncio.create_task(work(0.3, "slow")),
                asyncio.create_task(work(0.1, "fast")),
                asyncio.create_task(work(0.2, "medium")),
            ]
            results = await wait_for_first_n(tasks, 2)
            assert "fast" in results
            assert "medium" in results
            assert "slow" not in results

        asyncio.run(check())

    def test_cancels_remaining(self):
        async def work(delay, value):
            await asyncio.sleep(delay)
            return value

        async def check():
            tasks = [
                asyncio.create_task(work(0.5, "slow")),
                asyncio.create_task(work(0.1, "fast")),
            ]
            await wait_for_first_n(tasks, 1)
            # The slow task should be cancelled
            assert tasks[0].cancelled() or tasks[0].done()

        asyncio.run(check())


class TestProducerConsumer:
    """Tests for Exercise 2.4: producer/consumer"""

    def test_producer_sets_result(self):
        async def check():
            future = asyncio.Future()
            await producer(future, 0.1, "test")
            assert future.done()
            assert future.result() == "test"

        asyncio.run(check())

    def test_consumer_receives_result(self):
        async def check():
            future = asyncio.Future()
            future.set_result("hello")
            result = await consumer(future)
            assert result == "Received: hello"

        asyncio.run(check())

    def test_run_producer_consumer(self):
        result = asyncio.run(run_producer_consumer(0.1, "data"))
        assert result == "Received: data"

    def test_concurrent_execution(self):
        start = time.time()
        asyncio.run(run_producer_consumer(0.1, "test"))
        elapsed = time.time() - start
        # Should complete around 0.1s
        assert elapsed < 0.2


class TestTaskCollector:
    """Tests for Exercise 2.5: TaskCollector"""

    def test_collector_exists(self):
        collector = TaskCollector()
        assert hasattr(collector, 'add_task')
        assert hasattr(collector, 'get_results')

    def test_collect_results_returns_doubled(self):
        results = asyncio.run(collect_results([1, 2, 3]))
        assert sorted(results) == [2, 4, 6]

    def test_collect_results_different_values(self):
        results = asyncio.run(collect_results([5, 10, 15]))
        assert sorted(results) == [10, 20, 30]

    def test_empty_input(self):
        results = asyncio.run(collect_results([]))
        assert results == []

    def test_concurrent_execution(self):
        start = time.time()
        asyncio.run(collect_results([1, 2, 3, 4, 5]))
        elapsed = time.time() - start
        # Should be ~0.1s (concurrent), not 0.5s
        assert elapsed < 0.2
