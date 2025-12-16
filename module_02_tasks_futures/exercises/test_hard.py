"""
Tests for Exercise 3 (Hard): Advanced Task Patterns
Run with: python -m pytest module_02_tasks_futures/exercises/test_hard.py -v
"""

import asyncio
import time
import pytest

from exercise_hard import (
    TaskPool,
    execute_with_dependencies,
    ResilientTaskManager,
    progressive_load,
    TaskSupervisor,
)


class TestTaskPool:
    """Tests for Exercise 3.1: TaskPool"""

    def test_basic_submit(self):
        async def work(n):
            await asyncio.sleep(0.05)
            return n

        async def check():
            pool = TaskPool(max_concurrent=2)
            await pool.submit(work(1))
            await pool.submit(work(2))
            await pool.join()
            assert sorted(pool.results) == [1, 2]

        asyncio.run(check())

    def test_respects_concurrency_limit(self):
        running = 0
        max_running = 0

        async def track_work(n):
            nonlocal running, max_running
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.1)
            running -= 1
            return n

        async def check():
            pool = TaskPool(max_concurrent=2)
            for i in range(5):
                await pool.submit(track_work(i))
            await pool.join()
            assert max_running <= 2, f"Max concurrent was {max_running}"

        asyncio.run(check())

    def test_all_results_collected(self):
        async def work(n):
            await asyncio.sleep(0.05)
            return n * 2

        async def check():
            pool = TaskPool(max_concurrent=3)
            for i in range(5):
                await pool.submit(work(i))
            await pool.join()
            assert sorted(pool.results) == [0, 2, 4, 6, 8]

        asyncio.run(check())


class TestExecuteWithDependencies:
    """Tests for Exercise 3.2: execute_with_dependencies"""

    def test_no_dependencies(self):
        async def make_task(name):
            await asyncio.sleep(0.05)
            return f"result_{name}"

        async def check():
            graph = {
                "a": (lambda: make_task("a"), []),
                "b": (lambda: make_task("b"), []),
            }
            results = await execute_with_dependencies(graph)
            assert results == {"a": "result_a", "b": "result_b"}

        asyncio.run(check())

    def test_linear_dependency(self):
        order = []

        async def make_task(name):
            order.append(name)
            await asyncio.sleep(0.05)
            return name

        async def check():
            graph = {
                "a": (lambda: make_task("a"), []),
                "b": (lambda: make_task("b"), ["a"]),
                "c": (lambda: make_task("c"), ["b"]),
            }
            await execute_with_dependencies(graph)
            assert order.index("a") < order.index("b") < order.index("c")

        asyncio.run(check())

    def test_concurrent_when_possible(self):
        async def make_task(name):
            await asyncio.sleep(0.1)
            return name

        async def check():
            graph = {
                "a": (lambda: make_task("a"), []),
                "b": (lambda: make_task("b"), []),
                "c": (lambda: make_task("c"), ["a", "b"]),
            }
            start = time.time()
            await execute_with_dependencies(graph)
            elapsed = time.time() - start
            # a,b concurrent (0.1s) + c (0.1s) = ~0.2s
            assert elapsed < 0.3, f"Expected ~0.2s, got {elapsed}s"

        asyncio.run(check())


class TestResilientTaskManager:
    """Tests for Exercise 3.3: ResilientTaskManager"""

    def test_successful_task(self):
        async def always_works():
            return "success"

        async def check():
            manager = ResilientTaskManager(max_retries=3)
            manager.add_task("task1", always_works)
            await manager.run_all()
            assert manager.successful == {"task1": "success"}
            assert manager.failed == {}

        asyncio.run(check())

    def test_retry_until_success(self):
        attempt = 0

        async def works_on_third():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise ValueError("Not yet")
            return "finally"

        async def check():
            nonlocal attempt
            attempt = 0
            manager = ResilientTaskManager(max_retries=5)
            manager.add_task("flaky", works_on_third)
            await manager.run_all()
            assert manager.successful == {"flaky": "finally"}

        asyncio.run(check())

    def test_permanent_failure(self):
        async def always_fails():
            raise ValueError("Always fails")

        async def check():
            manager = ResilientTaskManager(max_retries=3)
            manager.add_task("bad", always_fails)
            await manager.run_all()
            assert "bad" in manager.failed
            assert manager.successful == {}

        asyncio.run(check())


class TestProgressiveLoad:
    """Tests for Exercise 3.4: progressive_load"""

    def test_final_results(self):
        async def check():
            results = await progressive_load(["a", "b", "c"], lambda *args: None)
            assert results == ["Loaded: a", "Loaded: b", "Loaded: c"]

        asyncio.run(check())

    def test_callback_called(self):
        log = []

        def on_progress(completed, total, result):
            log.append((completed, total, result))

        async def check():
            await progressive_load(["x", "y"], on_progress)
            assert len(log) == 2
            # Check totals are correct
            assert all(total == 2 for _, total, _ in log)

        asyncio.run(check())

    def test_callback_shows_progress(self):
        completed_counts = []

        def on_progress(completed, total, result):
            completed_counts.append(completed)

        async def check():
            await progressive_load(["a", "b", "c"], on_progress)
            assert sorted(completed_counts) == [1, 2, 3]

        asyncio.run(check())


class TestTaskSupervisor:
    """Tests for Exercise 3.5: TaskSupervisor"""

    def test_starts_task(self):
        started = False

        async def simple_task():
            nonlocal started
            started = True
            while True:
                await asyncio.sleep(0.1)

        async def check():
            supervisor = TaskSupervisor()
            await supervisor.start("worker", simple_task)
            await asyncio.sleep(0.05)
            await supervisor.stop_all()
            assert started

        asyncio.run(check())

    def test_restarts_on_failure(self):
        fail_count = 0

        async def fails_twice():
            nonlocal fail_count
            fail_count += 1
            if fail_count <= 2:
                raise ValueError("Oops")
            while True:
                await asyncio.sleep(0.1)

        async def check():
            nonlocal fail_count
            fail_count = 0
            supervisor = TaskSupervisor()
            await supervisor.start("worker", fails_twice)
            await asyncio.sleep(0.3)
            await supervisor.stop_all()
            assert supervisor.get_restart_count("worker") == 2

        asyncio.run(check())

    def test_stop_specific_task(self):
        async def forever():
            while True:
                await asyncio.sleep(0.1)

        async def check():
            supervisor = TaskSupervisor()
            await supervisor.start("task1", forever)
            await supervisor.start("task2", forever)
            await asyncio.sleep(0.05)
            await supervisor.stop("task1")
            await asyncio.sleep(0.05)
            await supervisor.stop_all()

        asyncio.run(check())
