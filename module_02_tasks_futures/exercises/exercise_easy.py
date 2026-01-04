"""
Exercise 1 (Easy): Basic Tasks

Your task is to understand how Tasks work and create them properly.
Run the tests to verify your solutions:
    python -m pytest module_02_tasks_futures/exercises/test_easy.py -v
"""

import asyncio


# =============================================================================
# Exercise 1.1: Create a Task
# =============================================================================
# Create a coroutine called `create_greeting_task` that:
# - Takes a name (str) as parameter
# - Creates and returns a Task that will produce "Hello, {name}!"
# - The Task should be returned immediately (don't await it)
#
# Note: You need to create a helper coroutine and wrap it in a Task
#
# Example:
#   task = await create_greeting_task("Alice")
#   # task is now running in the background
#   result = await task
#   # result == "Hello, Alice!"
# =============================================================================


async def create_greeting_task(name: str) -> asyncio.Task:
    async def say_hello(name: str):
        return f"Hello, {name}!"

    return asyncio.create_task(say_hello(name))


# =============================================================================
# Exercise 1.2: Run Tasks Concurrently
# =============================================================================
# Create a coroutine called `run_concurrent_tasks` that:
# - Takes a list of delays (floats)
# - Creates a Task for each delay that waits that amount of time
# - All tasks should run concurrently
# - Returns the total number of tasks that were created
#
# Requirement: Use asyncio.create_task() to ensure concurrent execution
#
# Example:
#   result = await run_concurrent_tasks([0.1, 0.1, 0.1])
#   # All 3 tasks run concurrently, total time ~0.1s
#   # Returns 3
# =============================================================================


async def run_concurrent_tasks(delays: list[float]) -> int:
    tasks = [asyncio.create_task(asyncio.sleep(delay)) for delay in delays]
    return len(tasks)


# =============================================================================
# Exercise 1.3: Task with Name
# =============================================================================
# Create a coroutine called `create_named_task` that:
# - Takes a task_name (str) and value (int) as parameters
# - Creates a Task with the given name that returns value * 2
# - Returns a tuple of (task_name, task)
#
# Example:
#   name, task = await create_named_task("doubler", 5)
#   # name == "doubler"
#   # await task == 10
# =============================================================================


async def create_named_task(task_name: str, value: int) -> tuple[str, asyncio.Task]:
    async def double(value: int):
        return value * 2

    return task_name, asyncio.create_task(double(value), name=task_name)


# =============================================================================
# Exercise 1.4: Check Task Status
# =============================================================================
# Create a coroutine called `task_status_info` that:
# - Creates a Task that waits 0.2 seconds and returns "done"
# - Immediately checks if the task is done (should be False)
# - Waits for the task to complete
# - Checks if the task is done again (should be True)
# - Returns a dict with keys: "was_done_before", "is_done_after", "result"
#
# Example:
#   info = await task_status_info()
#   # info == {"was_done_before": False, "is_done_after": True, "result": "done"}
# =============================================================================


async def task_status_info() -> dict:
    async def delay_task():
        await asyncio.sleep(0.2)
        return "done"

    task = asyncio.create_task(delay_task())
    was_done_before = task.done()
    await task
    is_done_after = task.done()
    return {"was_done_before": was_done_before, "is_done_after": is_done_after, "result": task.result()}


# =============================================================================
# Exercise 1.5: Fire and Forget with Tracking
# =============================================================================
# Create a coroutine called `fire_and_forget` that:
# - Takes a list of values (ints)
# - For each value, creates a Task that waits 0.1s and stores value * 2
# - Returns the list of created Tasks immediately (don't await them)
# - Caller will await the tasks later
#
# Example:
#   tasks = await fire_and_forget([1, 2, 3])
#   # len(tasks) == 3
#   # tasks are all running in background
#   results = [await t for t in tasks]  # [2, 4, 6]
# =============================================================================


async def fire_and_forget(values: list[int]) -> list[asyncio.Task]:
    async def double_value(value: int):
        await asyncio.sleep(0.1)
        return value * 2

    return [asyncio.create_task(double_value(value)) for value in values]
