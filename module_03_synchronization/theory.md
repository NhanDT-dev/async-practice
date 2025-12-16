# Module 03: Synchronization Primitives

## Prerequisites
Complete Module 01 and 02 before starting this module.

---

## 1. Why Synchronization?

### 1.1 The Problem

Even though asyncio is single-threaded, we still need synchronization when:
- Multiple coroutines access shared resources
- Order of operations matters
- We need to limit concurrent access

```python
import asyncio

# Shared state - can cause issues!
counter = 0

async def increment():
    global counter
    current = counter
    await asyncio.sleep(0.001)  # Simulate some async work
    counter = current + 1

async def main():
    global counter
    counter = 0
    await asyncio.gather(*[increment() for _ in range(100)])
    print(f"Expected: 100, Got: {counter}")  # Often less than 100!

asyncio.run(main())
```

### 1.2 Available Primitives

| Primitive | Purpose |
|-----------|---------|
| Lock | Mutual exclusion (only one at a time) |
| Event | Signal between coroutines |
| Condition | Wait for specific conditions |
| Semaphore | Limit concurrent access |
| BoundedSemaphore | Semaphore with overflow protection |
| Barrier | Synchronize multiple coroutines |

---

## 2. Lock

### 2.1 Basic Usage

```python
import asyncio

lock = asyncio.Lock()
counter = 0

async def safe_increment():
    global counter
    async with lock:
        current = counter
        await asyncio.sleep(0.001)
        counter = current + 1

async def main():
    global counter
    counter = 0
    await asyncio.gather(*[safe_increment() for _ in range(100)])
    print(f"Counter: {counter}")  # Always 100!

asyncio.run(main())
```

### 2.2 Lock Methods

```python
lock = asyncio.Lock()

# Method 1: Context manager (recommended)
async with lock:
    # Critical section
    pass

# Method 2: Manual acquire/release
await lock.acquire()
try:
    # Critical section
    pass
finally:
    lock.release()

# Check if locked
print(lock.locked())  # True/False
```

### 2.3 Lock with Timeout (Python 3.11+)

```python
import asyncio

lock = asyncio.Lock()

async def try_with_timeout():
    try:
        async with asyncio.timeout(1.0):
            async with lock:
                print("Got the lock!")
    except asyncio.TimeoutError:
        print("Couldn't get lock in time")
```

---

## 3. Event

### 3.1 Concept

An `Event` is a simple flag that coroutines can wait on.

```python
import asyncio

event = asyncio.Event()

async def waiter(name):
    print(f"{name}: Waiting for event...")
    await event.wait()
    print(f"{name}: Event received!")

async def setter():
    await asyncio.sleep(1)
    print("Setting event!")
    event.set()

async def main():
    await asyncio.gather(
        waiter("A"),
        waiter("B"),
        setter()
    )

asyncio.run(main())
```

### 3.2 Event Methods

```python
event = asyncio.Event()

# Wait for event to be set
await event.wait()

# Set the event (wake up all waiters)
event.set()

# Clear the event
event.clear()

# Check if set
print(event.is_set())  # True/False
```

### 3.3 Event Pattern: Start Signal

```python
import asyncio

start_signal = asyncio.Event()

async def worker(name):
    print(f"{name}: Ready, waiting for start...")
    await start_signal.wait()
    print(f"{name}: Working!")
    await asyncio.sleep(0.1)
    print(f"{name}: Done!")

async def main():
    workers = [worker(f"Worker-{i}") for i in range(3)]
    tasks = [asyncio.create_task(w) for w in workers]

    await asyncio.sleep(0.5)  # Setup time
    print("GO!")
    start_signal.set()

    await asyncio.gather(*tasks)

asyncio.run(main())
```

---

## 4. Condition

### 4.1 Concept

A `Condition` combines a Lock with the ability to wait for notifications.

```python
import asyncio

condition = asyncio.Condition()
data_ready = False
data = None

async def producer():
    global data_ready, data
    await asyncio.sleep(1)

    async with condition:
        data = "Important data"
        data_ready = True
        condition.notify_all()  # Wake up all waiters

async def consumer(name):
    async with condition:
        while not data_ready:
            await condition.wait()  # Release lock and wait
        print(f"{name}: Got data = {data}")

async def main():
    await asyncio.gather(
        consumer("A"),
        consumer("B"),
        producer()
    )

asyncio.run(main())
```

### 4.2 Condition Methods

```python
condition = asyncio.Condition()

async with condition:
    # Wait for notification (releases lock while waiting)
    await condition.wait()

    # Wait with predicate (convenience method)
    await condition.wait_for(lambda: some_condition)

    # Notify one waiter
    condition.notify()

    # Notify n waiters
    condition.notify(n=3)

    # Notify all waiters
    condition.notify_all()
```

### 4.3 Producer-Consumer Pattern

```python
import asyncio
from collections import deque

class AsyncQueue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self.queue = deque()
        self.condition = asyncio.Condition()

    async def put(self, item):
        async with self.condition:
            while self.maxsize > 0 and len(self.queue) >= self.maxsize:
                await self.condition.wait()
            self.queue.append(item)
            self.condition.notify()

    async def get(self):
        async with self.condition:
            while not self.queue:
                await self.condition.wait()
            item = self.queue.popleft()
            self.condition.notify()
            return item
```

---

## 5. Semaphore

### 5.1 Concept

A `Semaphore` limits concurrent access to a number of slots.

```python
import asyncio

# Allow max 3 concurrent operations
semaphore = asyncio.Semaphore(3)

async def limited_operation(n):
    async with semaphore:
        print(f"Task {n}: Starting")
        await asyncio.sleep(1)
        print(f"Task {n}: Done")

async def main():
    # Only 3 will run at a time
    await asyncio.gather(*[limited_operation(i) for i in range(10)])

asyncio.run(main())
```

### 5.2 Semaphore Methods

```python
sem = asyncio.Semaphore(5)

# Acquire a slot
await sem.acquire()

# Release a slot
sem.release()

# Context manager (recommended)
async with sem:
    # Do work
    pass

# Check if locked (all slots used)
print(sem.locked())
```

### 5.3 Rate Limiting with Semaphore

```python
import asyncio

class RateLimiter:
    def __init__(self, max_concurrent):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute(self, coro):
        async with self.semaphore:
            return await coro

# Usage
limiter = RateLimiter(max_concurrent=5)

async def api_call(n):
    await asyncio.sleep(0.1)
    return f"Result {n}"

async def main():
    tasks = [
        limiter.execute(api_call(i))
        for i in range(20)
    ]
    results = await asyncio.gather(*tasks)
    print(results)
```

### 5.4 BoundedSemaphore

Raises `ValueError` if released more times than acquired:

```python
sem = asyncio.BoundedSemaphore(3)

await sem.acquire()
sem.release()
sem.release()  # ValueError! Only acquired once
```

---

## 6. Barrier (Python 3.11+)

### 6.1 Concept

A `Barrier` blocks until a specified number of coroutines arrive.

```python
import asyncio

barrier = asyncio.Barrier(3)

async def worker(name):
    print(f"{name}: Doing preparation...")
    await asyncio.sleep(0.1)

    print(f"{name}: Waiting at barrier...")
    await barrier.wait()

    print(f"{name}: Barrier passed, continuing!")

async def main():
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C")
    )

asyncio.run(main())
```

Output:
```
A: Doing preparation...
B: Doing preparation...
C: Doing preparation...
A: Waiting at barrier...
B: Waiting at barrier...
C: Waiting at barrier...
A: Barrier passed, continuing!
B: Barrier passed, continuing!
C: Barrier passed, continuing!
```

### 6.2 Barrier Methods

```python
barrier = asyncio.Barrier(5)

# Wait at barrier
await barrier.wait()

# Reset barrier (releases all waiters with BrokenBarrierError)
await barrier.reset()

# Abort barrier
await barrier.abort()

# Check state
print(barrier.parties)   # Number required (5)
print(barrier.n_waiting) # Currently waiting
print(barrier.broken)    # If barrier is broken
```

---

## 7. asyncio.Queue

### 7.1 Basic Queue

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        print(f"Produced: {i}")
    await queue.put(None)  # Signal end

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

asyncio.run(main())
```

### 7.2 Queue Types

```python
# FIFO Queue
queue = asyncio.Queue(maxsize=10)

# LIFO Queue (Stack)
lifo = asyncio.LifoQueue(maxsize=10)

# Priority Queue (lowest first)
prio = asyncio.PriorityQueue(maxsize=10)
await prio.put((1, "low priority"))
await prio.put((0, "high priority"))
```

### 7.3 Queue Methods

```python
queue = asyncio.Queue(maxsize=10)

# Add item (blocks if full)
await queue.put(item)

# Add item without blocking
queue.put_nowait(item)  # Raises QueueFull if full

# Get item (blocks if empty)
item = await queue.get()

# Get item without blocking
item = queue.get_nowait()  # Raises QueueEmpty if empty

# Mark task as done
queue.task_done()

# Wait for all tasks to be done
await queue.join()

# Queue info
queue.qsize()    # Current size
queue.empty()    # Is empty?
queue.full()     # Is full?
```

---

## 8. Common Patterns

### 8.1 Worker Pool Pattern

```python
import asyncio

async def worker(name, queue, results):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break

        result = await process(item)
        results.append(result)
        queue.task_done()

async def process(item):
    await asyncio.sleep(0.1)
    return item * 2

async def main():
    queue = asyncio.Queue()
    results = []

    # Create workers
    workers = [
        asyncio.create_task(worker(f"Worker-{i}", queue, results))
        for i in range(3)
    ]

    # Add items
    for i in range(10):
        await queue.put(i)

    # Signal workers to stop
    for _ in range(3):
        await queue.put(None)

    # Wait for completion
    await queue.join()
    await asyncio.gather(*workers)

    print(results)

asyncio.run(main())
```

### 8.2 Reader-Writer Lock

```python
import asyncio

class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._writer = False
        self._condition = asyncio.Condition()

    async def acquire_read(self):
        async with self._condition:
            while self._writer:
                await self._condition.wait()
            self._readers += 1

    async def release_read(self):
        async with self._condition:
            self._readers -= 1
            if self._readers == 0:
                self._condition.notify_all()

    async def acquire_write(self):
        async with self._condition:
            while self._writer or self._readers > 0:
                await self._condition.wait()
            self._writer = True

    async def release_write(self):
        async with self._condition:
            self._writer = False
            self._condition.notify_all()
```

---

## 9. Deadlock Prevention

### 9.1 Always Use Context Managers

```python
# GOOD - automatic release
async with lock:
    await risky_operation()

# BAD - might not release on exception
await lock.acquire()
await risky_operation()  # If this raises, lock is held forever!
lock.release()
```

### 9.2 Acquire Locks in Consistent Order

```python
# If you need multiple locks, always acquire in same order
lock_a = asyncio.Lock()
lock_b = asyncio.Lock()

async def safe_operation():
    async with lock_a:  # Always a first
        async with lock_b:  # Then b
            pass

# NOT this (can deadlock)
async def unsafe_op1():
    async with lock_a:
        async with lock_b:
            pass

async def unsafe_op2():
    async with lock_b:  # Different order!
        async with lock_a:
            pass
```

### 9.3 Use Timeouts

```python
import asyncio

lock = asyncio.Lock()

async def with_timeout():
    try:
        async with asyncio.timeout(5.0):
            async with lock:
                await do_work()
    except asyncio.TimeoutError:
        print("Could not acquire lock in time")
```

---

## Summary

1. **Lock** - Mutual exclusion, one at a time
2. **Event** - Simple signal flag
3. **Condition** - Wait for complex conditions
4. **Semaphore** - Limit concurrent access
5. **Barrier** - Synchronize N coroutines
6. **Queue** - Producer-consumer communication

Key principles:
- Always use `async with` for safety
- Single-threaded doesn't mean race-free
- Design for minimal lock holding time
- Prevent deadlocks with consistent ordering

---

## Next Steps

After completing the 3 exercises, move to **Module 04: Async I/O & Networking** to learn about real-world async applications.
