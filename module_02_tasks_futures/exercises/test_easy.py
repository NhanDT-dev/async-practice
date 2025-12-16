"""
Tests for Exercise 1 (Easy): Basic Tasks
Run with: python -m pytest module_02_tasks_futures/exercises/test_easy.py -v
"""

import asyncio
import time
import pytest

from exercise_easy import (
    create_greeting_task,
    run_concurrent_tasks,
    create_named_task,
    task_status_info,
    fire_and_forget,
)


class TestCreateGreetingTask:
    """Tests for Exercise 1.1: create_greeting_task"""

    def test_returns_task(self):
        async def check():
            task = await create_greeting_task("Test")
            assert isinstance(task, asyncio.Task)
            await task  # Cleanup

        asyncio.run(check())

    def test_task_produces_greeting(self):
        async def check():
            task = await create_greeting_task("Alice")
            result = await task
            assert result == "Hello, Alice!"

        asyncio.run(check())

    def test_different_name(self):
        async def check():
            task = await create_greeting_task("Bob")
            result = await task
            assert result == "Hello, Bob!"

        asyncio.run(check())


class TestRunConcurrentTasks:
    """Tests for Exercise 1.2: run_concurrent_tasks"""

    def test_returns_count(self):
        async def check():
            count = await run_concurrent_tasks([0.05, 0.05, 0.05])
            assert count == 3

        asyncio.run(check())

    def test_runs_concurrently(self):
        async def check():
            start = time.time()
            await run_concurrent_tasks([0.1, 0.1, 0.1, 0.1])
            elapsed = time.time() - start
            # Should be ~0.1s (concurrent), not 0.4s (sequential)
            assert elapsed < 0.2, f"Expected concurrent execution, got {elapsed}s"

        asyncio.run(check())

    def test_empty_list(self):
        async def check():
            count = await run_concurrent_tasks([])
            assert count == 0

        asyncio.run(check())


class TestCreateNamedTask:
    """Tests for Exercise 1.3: create_named_task"""

    def test_returns_tuple(self):
        async def check():
            result = await create_named_task("test", 5)
            assert isinstance(result, tuple)
            assert len(result) == 2

        asyncio.run(check())

    def test_task_name(self):
        async def check():
            name, task = await create_named_task("my-task", 5)
            assert name == "my-task"
            assert task.get_name() == "my-task"
            await task

        asyncio.run(check())

    def test_task_doubles_value(self):
        async def check():
            _, task = await create_named_task("doubler", 7)
            result = await task
            assert result == 14

        asyncio.run(check())


class TestTaskStatusInfo:
    """Tests for Exercise 1.4: task_status_info"""

    def test_returns_dict(self):
        result = asyncio.run(task_status_info())
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = asyncio.run(task_status_info())
        assert "was_done_before" in result
        assert "is_done_after" in result
        assert "result" in result

    def test_correct_status_values(self):
        result = asyncio.run(task_status_info())
        assert result["was_done_before"] is False
        assert result["is_done_after"] is True
        assert result["result"] == "done"


class TestFireAndForget:
    """Tests for Exercise 1.5: fire_and_forget"""

    def test_returns_tasks(self):
        async def check():
            tasks = await fire_and_forget([1, 2, 3])
            assert len(tasks) == 3
            for t in tasks:
                assert isinstance(t, asyncio.Task)
            # Wait for all to complete
            await asyncio.gather(*tasks)

        asyncio.run(check())

    def test_tasks_not_done_immediately(self):
        async def check():
            tasks = await fire_and_forget([1, 2])
            # Should not be done immediately
            any_done = any(t.done() for t in tasks)
            # Wait then check
            await asyncio.gather(*tasks)
            all_done = all(t.done() for t in tasks)
            assert all_done

        asyncio.run(check())

    def test_correct_results(self):
        async def check():
            tasks = await fire_and_forget([1, 2, 3])
            results = [await t for t in tasks]
            assert results == [2, 4, 6]

        asyncio.run(check())

    def test_runs_concurrently(self):
        async def check():
            start = time.time()
            tasks = await fire_and_forget([1, 2, 3, 4, 5])
            await asyncio.gather(*tasks)
            elapsed = time.time() - start
            # Should be ~0.1s (concurrent), not 0.5s
            assert elapsed < 0.2

        asyncio.run(check())
