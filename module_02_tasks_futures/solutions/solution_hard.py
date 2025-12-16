"""
Solutions for Exercise 3 (Hard): Advanced Task Patterns

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
from typing import Any, Callable, Awaitable
from collections import defaultdict


# =============================================================================
# Solution 3.1: Task Pool with Concurrency Limit
# =============================================================================
class TaskPool:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._tasks: list[asyncio.Task] = []
        self._results: list[Any] = []

    async def submit(self, coro) -> asyncio.Task:
        await self.semaphore.acquire()

        async def wrapped():
            try:
                result = await coro
                self._results.append(result)
                return result
            finally:
                self.semaphore.release()

        task = asyncio.create_task(wrapped())
        self._tasks.append(task)
        return task

    async def join(self):
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    @property
    def results(self) -> list[Any]:
        return self._results.copy()


# =============================================================================
# Solution 3.2: Dependency Graph Executor
# =============================================================================
async def execute_with_dependencies(
    graph: dict[str, tuple[Callable[[], Awaitable[Any]], list[str]]]
) -> dict[str, Any]:
    results = {}
    completed = set()
    pending = set(graph.keys())

    while pending:
        # Find tasks whose dependencies are all completed
        ready = []
        for name in pending:
            _, deps = graph[name]
            if all(d in completed for d in deps):
                ready.append(name)

        if not ready:
            raise ValueError("Circular dependency detected!")

        # Run ready tasks concurrently
        async def run_task(name):
            factory, _ = graph[name]
            result = await factory()
            return name, result

        tasks_results = await asyncio.gather(*[run_task(n) for n in ready])

        for name, result in tasks_results:
            results[name] = result
            completed.add(name)
            pending.remove(name)

    return results


# =============================================================================
# Solution 3.3: Resilient Task Manager
# =============================================================================
class ResilientTaskManager:
    def __init__(self, max_retries: int):
        self.max_retries = max_retries
        self._tasks: dict[str, Callable[[], Awaitable[Any]]] = {}
        self.successful: dict[str, Any] = {}
        self.failed: dict[str, Exception] = {}

    def add_task(self, name: str, coro_factory: Callable[[], Awaitable[Any]]):
        self._tasks[name] = coro_factory

    async def run_all(self):
        async def run_with_retry(name, factory):
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    result = await factory()
                    self.successful[name] = result
                    return
                except Exception as e:
                    last_error = e

            self.failed[name] = last_error

        await asyncio.gather(*[
            run_with_retry(name, factory)
            for name, factory in self._tasks.items()
        ])


# =============================================================================
# Solution 3.4: Progressive Loader
# =============================================================================
async def progressive_load(
    urls: list[str],
    callback: Callable[[int, int, str], None]
) -> list[str]:
    total = len(urls)
    completed = 0
    results = [None] * total  # Preserve order
    lock = asyncio.Lock()

    async def load_url(index: int, url: str):
        nonlocal completed
        await asyncio.sleep(0.1)
        result = f"Loaded: {url}"

        async with lock:
            completed += 1
            results[index] = result
            callback(completed, total, result)

        return result

    await asyncio.gather(*[
        load_url(i, url) for i, url in enumerate(urls)
    ])

    return results


# =============================================================================
# Solution 3.5: Task Supervisor
# =============================================================================
class TaskSupervisor:
    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._factories: dict[str, Callable[[], Awaitable[Any]]] = {}
        self._restart_counts: dict[str, int] = defaultdict(int)
        self._should_run: dict[str, bool] = {}

    async def start(self, name: str, coro_factory: Callable[[], Awaitable[Any]]):
        self._factories[name] = coro_factory
        self._should_run[name] = True
        self._restart_counts[name] = 0
        await self._start_task(name)

    async def _start_task(self, name: str):
        async def supervised():
            while self._should_run.get(name, False):
                try:
                    await self._factories[name]()
                    break  # Task completed normally
                except asyncio.CancelledError:
                    break  # Explicitly cancelled
                except Exception:
                    if self._should_run.get(name, False):
                        self._restart_counts[name] += 1
                        await asyncio.sleep(0.01)  # Brief delay before restart
                    else:
                        break

        self._tasks[name] = asyncio.create_task(supervised())

    async def stop(self, name: str):
        self._should_run[name] = False
        if name in self._tasks:
            self._tasks[name].cancel()
            try:
                await self._tasks[name]
            except asyncio.CancelledError:
                pass

    async def stop_all(self):
        for name in list(self._tasks.keys()):
            await self.stop(name)

    def get_restart_count(self, name: str) -> int:
        return self._restart_counts.get(name, 0)


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("Testing TaskPool:")
        print("=" * 60)

        async def work(n):
            print(f"  Task {n} running")
            await asyncio.sleep(0.1)
            return n

        pool = TaskPool(max_concurrent=2)
        for i in range(5):
            await pool.submit(work(i))
        await pool.join()
        print(f"Results: {sorted(pool.results)}")

        print("\n" + "=" * 60)
        print("Testing execute_with_dependencies:")
        print("=" * 60)

        async def make_task(name):
            print(f"  Executing {name}")
            await asyncio.sleep(0.1)
            return f"result_{name}"

        graph = {
            "a": (lambda: make_task("a"), []),
            "b": (lambda: make_task("b"), []),
            "c": (lambda: make_task("c"), ["a", "b"]),
        }
        results = await execute_with_dependencies(graph)
        print(f"Results: {results}")

        print("\n" + "=" * 60)
        print("Testing ResilientTaskManager:")
        print("=" * 60)

        attempt = 0

        async def flaky():
            nonlocal attempt
            attempt += 1
            print(f"  Attempt {attempt}")
            if attempt < 3:
                raise ValueError("Not yet")
            return "success!"

        manager = ResilientTaskManager(max_retries=5)
        manager.add_task("flaky", flaky)
        await manager.run_all()
        print(f"Successful: {manager.successful}")

        print("\n" + "=" * 60)
        print("Testing progressive_load:")
        print("=" * 60)

        def on_progress(completed, total, result):
            print(f"  Progress: {completed}/{total} - {result}")

        results = await progressive_load(["a", "b", "c"], on_progress)
        print(f"Final: {results}")

        print("\n" + "=" * 60)
        print("Testing TaskSupervisor:")
        print("=" * 60)

        fail_count = 0

        async def fails_twice():
            nonlocal fail_count
            fail_count += 1
            print(f"  Worker attempt {fail_count}")
            if fail_count <= 2:
                raise ValueError("Oops")
            while True:
                await asyncio.sleep(0.1)

        supervisor = TaskSupervisor()
        await supervisor.start("worker", fails_twice)
        await asyncio.sleep(0.3)
        await supervisor.stop_all()
        print(f"Restart count: {supervisor.get_restart_count('worker')}")

    asyncio.run(main())
