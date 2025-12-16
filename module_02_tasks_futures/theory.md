# Module 02: Tasks & Futures

## Prerequisites
Complete Module 01 (Coroutines & Event Loop) before starting this module.

---

## 1. What is a Task?

### 1.1 Definition

A **Task** is a wrapper around a coroutine that:
- Schedules the coroutine to run on the event loop
- Allows the coroutine to run "in the background"
- Provides methods to check status, cancel, and get results

```python
import asyncio

async def my_coroutine():
    await asyncio.sleep(1)
    return "Done!"

async def main():
    # Method 1: Just await (coroutine runs when awaited)
    result = await my_coroutine()

    # Method 2: Create task (coroutine starts immediately)
    task = asyncio.create_task(my_coroutine())
    # Task is now running in the background!
    result = await task  # Get the result when ready
```

### 1.2 Key Difference: Coroutine vs Task

```python
import asyncio
import time

async def work(name, delay):
    print(f"{name}: Starting")
    await asyncio.sleep(delay)
    print(f"{name}: Done")
    return name

async def without_tasks():
    """Coroutines run sequentially when awaited directly"""
    start = time.time()

    result1 = await work("A", 1)  # Wait for A
    result2 = await work("B", 1)  # Then wait for B

    print(f"Time: {time.time() - start:.1f}s")  # ~2s

async def with_tasks():
    """Tasks run concurrently"""
    start = time.time()

    task1 = asyncio.create_task(work("A", 1))  # Start A
    task2 = asyncio.create_task(work("B", 1))  # Start B immediately

    result1 = await task1  # Both are already running!
    result2 = await task2

    print(f"Time: {time.time() - start:.1f}s")  # ~1s
```

---

## 2. Creating and Managing Tasks

### 2.1 Creating Tasks

```python
import asyncio

async def my_work():
    await asyncio.sleep(1)
    return "result"

async def main():
    # Python 3.7+
    task = asyncio.create_task(my_work())

    # With a name (Python 3.8+)
    task = asyncio.create_task(my_work(), name="my-task")

    # Check the name
    print(task.get_name())  # "my-task"
```

### 2.2 Task States

```python
task = asyncio.create_task(some_coroutine())

# Check if task is done
task.done()  # True/False

# Check if task was cancelled
task.cancelled()  # True/False

# Get exception (if any) - only after task is done
task.exception()  # Returns exception or None
```

### 2.3 Getting Results

```python
async def main():
    task = asyncio.create_task(work())

    # Method 1: await the task
    result = await task

    # Method 2: use result() - only after done()
    if task.done():
        result = task.result()
```

---

## 3. Cancelling Tasks

### 3.1 Basic Cancellation

```python
import asyncio

async def long_running():
    try:
        while True:
            print("Working...")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("I was cancelled!")
        raise  # Re-raise to properly cancel

async def main():
    task = asyncio.create_task(long_running())

    await asyncio.sleep(2.5)  # Let it run for a bit

    task.cancel()  # Request cancellation

    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")
```

### 3.2 Cancellation with Cleanup

```python
async def task_with_cleanup():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        # Cleanup code here
        print("Cleaning up resources...")
        await save_state()  # Can still await in cleanup
        raise  # Always re-raise!

async def save_state():
    await asyncio.sleep(0.1)
    print("State saved!")
```

### 3.3 Cancel with Message (Python 3.9+)

```python
task.cancel(msg="Timeout exceeded")

try:
    await task
except asyncio.CancelledError as e:
    print(f"Cancelled: {e}")  # "Cancelled: Timeout exceeded"
```

---

## 4. What is a Future?

### 4.1 Definition

A **Future** represents a result that will be available in the future.

- `Task` is a subclass of `Future`
- You rarely create Futures directly
- Futures are used internally by asyncio

```python
import asyncio

async def main():
    # Create a Future (rarely done directly)
    future = asyncio.Future()

    # Set result later
    future.set_result("Hello!")

    # Get result
    result = await future
    print(result)  # "Hello!"
```

### 4.2 Future vs Task

| Feature | Future | Task |
|---------|--------|------|
| Represents | A pending result | A running coroutine |
| Created by | `asyncio.Future()` | `asyncio.create_task()` |
| Has coroutine | No | Yes |
| Common use | Low-level APIs | High-level code |

### 4.3 Practical Future Example

```python
import asyncio

async def producer(future: asyncio.Future):
    """Simulates work and sets result"""
    await asyncio.sleep(1)
    future.set_result("Data ready!")

async def consumer(future: asyncio.Future):
    """Waits for the result"""
    print("Waiting for data...")
    result = await future
    print(f"Got: {result}")

async def main():
    future = asyncio.Future()

    await asyncio.gather(
        producer(future),
        consumer(future)
    )

asyncio.run(main())
```

---

## 5. Task Groups (Python 3.11+)

### 5.1 Basic TaskGroup

```python
import asyncio

async def work(n):
    await asyncio.sleep(0.1)
    return n * 2

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(work(1))
        task2 = tg.create_task(work(2))
        task3 = tg.create_task(work(3))

    # All tasks are done when exiting the context
    print(task1.result())  # 2
    print(task2.result())  # 4
    print(task3.result())  # 6
```

### 5.2 TaskGroup vs gather

| Feature | TaskGroup | gather |
|---------|-----------|--------|
| Syntax | Context manager | Function call |
| Error handling | Raises ExceptionGroup | First error or all |
| Cancellation | Auto-cancels on error | Manual |
| Python version | 3.11+ | 3.4+ |

### 5.3 Error Handling with TaskGroup

```python
import asyncio

async def good_task():
    await asyncio.sleep(0.1)
    return "OK"

async def bad_task():
    await asyncio.sleep(0.1)
    raise ValueError("Something went wrong!")

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(good_task())
            t2 = tg.create_task(bad_task())
    except* ValueError as eg:
        # ExceptionGroup handling (Python 3.11+)
        for exc in eg.exceptions:
            print(f"Caught: {exc}")

asyncio.run(main())
```

---

## 6. Callbacks

### 6.1 Adding Callbacks to Tasks

```python
import asyncio

def on_complete(task):
    """Called when task completes"""
    if task.cancelled():
        print("Task was cancelled")
    elif task.exception():
        print(f"Task failed: {task.exception()}")
    else:
        print(f"Task result: {task.result()}")

async def work():
    await asyncio.sleep(1)
    return "Done!"

async def main():
    task = asyncio.create_task(work())
    task.add_done_callback(on_complete)

    await task

asyncio.run(main())
```

### 6.2 Multiple Callbacks

```python
def callback1(task):
    print("Callback 1 called")

def callback2(task):
    print("Callback 2 called")

task.add_done_callback(callback1)
task.add_done_callback(callback2)
# Both will be called when task completes
```

---

## 7. Waiting for Tasks

### 7.1 asyncio.wait()

```python
import asyncio

async def work(n):
    await asyncio.sleep(n * 0.1)
    return n

async def main():
    tasks = [asyncio.create_task(work(i)) for i in range(5)]

    # Wait for ALL to complete
    done, pending = await asyncio.wait(tasks)

    # Wait for FIRST to complete
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    # Wait for FIRST exception
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION
    )
```

### 7.2 asyncio.wait() with Timeout

```python
async def main():
    tasks = [asyncio.create_task(work(i)) for i in range(5)]

    # Wait with timeout
    done, pending = await asyncio.wait(
        tasks,
        timeout=0.25
    )

    print(f"Done: {len(done)}, Pending: {len(pending)}")

    # Don't forget to cancel pending tasks!
    for task in pending:
        task.cancel()
```

### 7.3 asyncio.as_completed()

Process results as they become available:

```python
import asyncio

async def fetch(url, delay):
    await asyncio.sleep(delay)
    return f"Data from {url}"

async def main():
    tasks = [
        asyncio.create_task(fetch("slow.com", 0.3)),
        asyncio.create_task(fetch("fast.com", 0.1)),
        asyncio.create_task(fetch("medium.com", 0.2)),
    ]

    # Process in completion order (not creation order!)
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(result)
        # Output:
        # Data from fast.com
        # Data from medium.com
        # Data from slow.com

asyncio.run(main())
```

---

## 8. Common Patterns

### 8.1 Fire and Forget

```python
import asyncio

async def background_work():
    await asyncio.sleep(5)
    print("Background work done!")

async def main():
    # Start task but don't wait
    task = asyncio.create_task(background_work())

    # Do other work...
    print("Main continues immediately")
    await asyncio.sleep(1)
    print("Main done, but background still running")

    # Optional: wait for background to finish
    await task
```

### 8.2 Task Shielding

Protect a task from cancellation:

```python
import asyncio

async def important_work():
    await asyncio.sleep(1)
    return "Critical result"

async def main():
    task = asyncio.create_task(important_work())

    # Shield prevents cancellation of the inner task
    try:
        result = await asyncio.wait_for(
            asyncio.shield(task),
            timeout=0.5
        )
    except asyncio.TimeoutError:
        print("Timeout, but task still running!")
        # Task continues running, we can still await it
        result = await task
        print(f"Got result: {result}")
```

### 8.3 Collecting All Results

```python
async def main():
    tasks = [asyncio.create_task(work(i)) for i in range(5)]

    # Method 1: asyncio.gather (preserves order)
    results = await asyncio.gather(*tasks)

    # Method 2: asyncio.wait + extract results
    done, _ = await asyncio.wait(tasks)
    results = [t.result() for t in done]  # Order not guaranteed!
```

---

## Summary

1. **Task** = scheduled coroutine that runs in the background
2. `asyncio.create_task()` starts coroutine immediately
3. Tasks can be cancelled with `task.cancel()`
4. Handle `CancelledError` for cleanup
5. **Future** = low-level pending result container
6. **TaskGroup** (3.11+) = structured concurrency
7. Use `asyncio.wait()` for complex waiting patterns
8. Use `asyncio.as_completed()` for processing in completion order

---

## Next Steps

After completing the 3 exercises, move to **Module 03: Synchronization Primitives** to learn about locks, semaphores, and coordinating concurrent tasks.
