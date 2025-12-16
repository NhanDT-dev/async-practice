# Module 01: Coroutines & Event Loop

## 1. Why Async?

### 1.1 The Problem with Synchronous Code

```python
import time

def fetch_data(url):
    print(f"Fetching {url}...")
    time.sleep(2)  # Simulate network delay
    return f"Data from {url}"

# Sequential - takes 6 seconds
start = time.time()
result1 = fetch_data("url1")
result2 = fetch_data("url2")
result3 = fetch_data("url3")
print(f"Total: {time.time() - start:.1f}s")  # ~6s
```

**Problem**: CPU is idle while waiting for I/O!

### 1.2 Solutions: Concurrency

| Approach | Description | Use Case |
|----------|-------------|----------|
| Threading | Multiple threads, shared memory | I/O-bound, simple cases |
| Multiprocessing | Multiple processes | CPU-bound |
| **Asyncio** | Single thread, event loop | I/O-bound, many connections |

**Asyncio** is more efficient than threading when:
- Handling thousands of concurrent connections
- Avoiding context switching overhead
- Needing precise control over execution flow

---

## 2. What is a Coroutine?

### 2.1 Definition

A **coroutine** is a function that can **suspend** and **resume** its execution.

```python
# Regular function - runs from start to end
def regular_function():
    print("Start")
    print("End")
    return "Done"

# Coroutine - can pause at await
async def coroutine_function():
    print("Start")
    await asyncio.sleep(1)  # PAUSE here
    print("End")
    return "Done"
```

### 2.2 Key Keywords

| Keyword | Meaning |
|---------|---------|
| `async def` | Defines a coroutine function |
| `await` | Suspend execution, wait for another coroutine |

### 2.3 Coroutine Object vs Coroutine Function

```python
import asyncio

async def greet(name):
    return f"Hello, {name}!"

# greet is a coroutine FUNCTION
print(type(greet))  # <class 'function'>

# greet("World") returns a coroutine OBJECT
coro = greet("World")
print(type(coro))  # <class 'coroutine'>

# Coroutine object MUST be awaited or run
result = asyncio.run(coro)
print(result)  # Hello, World!
```

**Important**: Calling `greet("World")` does NOT execute the code, it only creates a coroutine object!

---

## 3. Event Loop

### 3.1 Concept

The **Event Loop** is the "orchestrator" that runs coroutines. It:
1. Manages a queue of coroutines
2. Runs a coroutine until it hits `await`
3. Switches to another coroutine when the current one is waiting
4. Resumes coroutines when their I/O completes

```
┌─────────────────────────────────────────┐
│              EVENT LOOP                  │
├─────────────────────────────────────────┤
│  Ready Queue: [coro1, coro2, coro3]     │
│                                          │
│  1. Take coro1 from queue               │
│  2. Run coro1 until await               │
│  3. coro1 waits for I/O → move to wait  │
│  4. Take coro2, run...                  │
│  5. coro1's I/O done → back to queue    │
│  6. Continue...                         │
└─────────────────────────────────────────┘
```

### 3.2 Running the Event Loop

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Method 1: asyncio.run() - recommended for Python 3.7+
asyncio.run(main())

# Method 2: Manual event loop (legacy)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
```

### 3.3 Running Multiple Coroutines Concurrently

```python
import asyncio
import time

async def task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} finished")
    return f"{name} result"

async def main():
    start = time.time()

    # Run CONCURRENTLY with gather
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )

    print(f"Results: {results}")
    print(f"Total time: {time.time() - start:.1f}s")  # ~3s, not 6s!

asyncio.run(main())
```

**Output**:
```
A started
B started
C started
B finished
A finished
C finished
Results: ['A result', 'B result', 'C result']
Total time: 3.0s
```

---

## 4. Understanding Await

### 4.1 What is Awaitable?

You can `await` these objects:
1. **Coroutine** - created by `async def`
2. **Task** - wrapper for coroutine (Module 02)
3. **Future** - result to be available in the future (Module 02)

### 4.2 Await Chain

```python
async def inner():
    await asyncio.sleep(1)
    return "inner result"

async def middle():
    result = await inner()  # await coroutine
    return f"middle got: {result}"

async def outer():
    result = await middle()  # await chain
    return f"outer got: {result}"

# When awaiting, control flows to the deepest level
# then results "bubble up"
```

### 4.3 Cannot Await in Regular Functions

```python
import asyncio

async def async_work():
    await asyncio.sleep(1)
    return "done"

def regular_function():
    # SyntaxError! Cannot await in regular def
    # result = await async_work()

    # Must use asyncio.run() or be in async context
    result = asyncio.run(async_work())
    return result
```

---

## 5. Comparison with Threading

### 5.1 Threading Approach

```python
import threading
import time

def task(name):
    print(f"{name} started")
    time.sleep(2)
    print(f"{name} finished")

threads = [
    threading.Thread(target=task, args=(f"Thread-{i}",))
    for i in range(3)
]

for t in threads:
    t.start()
for t in threads:
    t.join()
```

### 5.2 Asyncio Approach

```python
import asyncio

async def task(name):
    print(f"{name} started")
    await asyncio.sleep(2)
    print(f"{name} finished")

async def main():
    await asyncio.gather(
        task("Coro-0"),
        task("Coro-1"),
        task("Coro-2")
    )

asyncio.run(main())
```

### 5.3 Key Differences

| Aspect | Threading | Asyncio |
|--------|-----------|---------|
| Switching | OS decides (preemptive) | Code decides at `await` (cooperative) |
| Race conditions | Can happen | Less likely (single thread) |
| Overhead | High (thread stack ~1MB) | Low (coroutine ~KB) |
| Scalability | ~thousands | ~millions |
| Blocking I/O | Works | BREAKS - must use async I/O |

---

## 6. Common Mistakes

### 6.1 Forgetting to Await

```python
async def fetch():
    await asyncio.sleep(1)
    return "data"

async def main():
    # WRONG - only creates coroutine object, doesn't run!
    result = fetch()
    print(result)  # <coroutine object>

    # CORRECT
    result = await fetch()
    print(result)  # "data"
```

### 6.2 Blocking in Async Code

```python
import time
import asyncio

async def bad_async():
    # WRONG - time.sleep BLOCKS the event loop!
    time.sleep(5)  # No other coroutine can run
    return "done"

async def good_async():
    # CORRECT - await allows switching
    await asyncio.sleep(5)
    return "done"
```

### 6.3 Not Awaiting Coroutines

```python
async def main():
    # WRONG - coroutine not awaited
    asyncio.sleep(1)  # Warning: coroutine never awaited

    # CORRECT
    await asyncio.sleep(1)
```

---

## 7. Debug Tips

### 7.1 Enable Debug Mode

```python
import asyncio

# Method 1: Environment variable
# PYTHONASYNCIODEBUG=1 python script.py

# Method 2: In code
asyncio.run(main(), debug=True)
```

### 7.2 Check for Unawaited Coroutines

Python will warn if a coroutine is not awaited:
```
RuntimeWarning: coroutine 'xxx' was never awaited
```

---

## Summary

1. **Coroutine** = function that can pause/resume at `await`
2. **Event Loop** = orchestrator that runs coroutines
3. `async def` creates a coroutine function
4. `await` pauses current coroutine, waits for result
5. `asyncio.run()` runs coroutine from sync code
6. `asyncio.gather()` runs multiple coroutines concurrently
7. **NEVER** use blocking I/O in async code

---

## Next Steps

After completing the 3 exercises, move to **Module 02: Tasks & Futures** to learn more fine-grained control over coroutines.
