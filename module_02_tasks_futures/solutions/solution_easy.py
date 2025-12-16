"""
Solutions for Exercise 1 (Easy): Basic Tasks

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio


# =============================================================================
# Solution 1.1: Create a Task
# =============================================================================
async def create_greeting_task(name: str) -> asyncio.Task:
    async def greet():
        return f"Hello, {name}!"

    return asyncio.create_task(greet())


# =============================================================================
# Solution 1.2: Run Tasks Concurrently
# =============================================================================
async def run_concurrent_tasks(delays: list[float]) -> int:
    async def wait_for(delay):
        await asyncio.sleep(delay)

    tasks = [asyncio.create_task(wait_for(d)) for d in delays]
    if tasks:
        await asyncio.gather(*tasks)
    return len(tasks)


# =============================================================================
# Solution 1.3: Task with Name
# =============================================================================
async def create_named_task(task_name: str, value: int) -> tuple[str, asyncio.Task]:
    async def double_value():
        return value * 2

    task = asyncio.create_task(double_value(), name=task_name)
    return (task_name, task)


# =============================================================================
# Solution 1.4: Check Task Status
# =============================================================================
async def task_status_info() -> dict:
    async def work():
        await asyncio.sleep(0.2)
        return "done"

    task = asyncio.create_task(work())

    was_done_before = task.done()

    await task

    is_done_after = task.done()

    return {
        "was_done_before": was_done_before,
        "is_done_after": is_done_after,
        "result": task.result()
    }


# =============================================================================
# Solution 1.5: Fire and Forget with Tracking
# =============================================================================
async def fire_and_forget(values: list[int]) -> list[asyncio.Task]:
    async def double_with_delay(v):
        await asyncio.sleep(0.1)
        return v * 2

    return [asyncio.create_task(double_with_delay(v)) for v in values]


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("Testing create_greeting_task:")
        task = await create_greeting_task("World")
        print(await task)

        print("\nTesting run_concurrent_tasks:")
        count = await run_concurrent_tasks([0.1, 0.1, 0.1])
        print(f"Ran {count} tasks")

        print("\nTesting create_named_task:")
        name, task = await create_named_task("doubler", 5)
        print(f"Task {name} result: {await task}")

        print("\nTesting task_status_info:")
        info = await task_status_info()
        print(info)

        print("\nTesting fire_and_forget:")
        tasks = await fire_and_forget([1, 2, 3])
        results = [await t for t in tasks]
        print(f"Results: {results}")

    asyncio.run(main())
