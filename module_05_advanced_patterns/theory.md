# Module 05: Advanced Patterns & Real-World Applications

## Prerequisites
Complete Modules 01-04 before starting this module.

---

## 1. Structured Concurrency

### 1.1 The Problem with Unstructured Concurrency

```python
# UNSTRUCTURED - Tasks can outlive their parent
async def bad_example():
    task = asyncio.create_task(background_work())
    return "done"  # task continues running after we return!

# STRUCTURED - Parent waits for all children
async def good_example():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(work1())
        tg.create_task(work2())
    # Both tasks guaranteed complete here
```

### 1.2 TaskGroup Pattern (Python 3.11+)

```python
import asyncio

async def fetch_data(source):
    await asyncio.sleep(0.1)
    return f"data from {source}"

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(fetch_data("api1"))
            task2 = tg.create_task(fetch_data("api2"))
            task3 = tg.create_task(fetch_data("api3"))

        # All tasks complete when exiting the context
        print(task1.result(), task2.result(), task3.result())

    except* ValueError as eg:
        # Handle multiple exceptions
        for exc in eg.exceptions:
            print(f"Error: {exc}")
```

### 1.3 Exception Groups (Python 3.11+)

```python
async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task_that_may_fail())
            tg.create_task(another_task())
    except* ValueError as eg:
        print(f"Caught {len(eg.exceptions)} ValueError(s)")
    except* TypeError as eg:
        print(f"Caught {len(eg.exceptions)} TypeError(s)")
```

---

## 2. Async Context Managers

### 2.1 Implementing Async Context Managers

```python
class AsyncResource:
    async def __aenter__(self):
        print("Acquiring resource")
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Releasing resource")
        await self._disconnect()
        return False  # Don't suppress exceptions

    async def _connect(self):
        await asyncio.sleep(0.1)

    async def _disconnect(self):
        await asyncio.sleep(0.1)

# Usage
async def main():
    async with AsyncResource() as resource:
        await resource.do_something()
```

### 2.2 Using @asynccontextmanager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_transaction(db):
    await db.begin()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise

# Usage
async def main():
    async with database_transaction(db) as tx:
        await tx.execute("INSERT ...")
```

---

## 3. Async Iterators and Generators

### 3.1 Async Iterator Protocol

```python
class AsyncCounter:
    def __init__(self, stop):
        self.stop = stop
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        value = self.current
        self.current += 1
        return value

# Usage
async def main():
    async for num in AsyncCounter(5):
        print(num)
```

### 3.2 Async Generators

```python
async def async_range(start, stop):
    """Async generator - simpler than implementing protocol"""
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def fetch_pages(urls):
    """Yield results as they complete"""
    for url in urls:
        data = await fetch(url)
        yield data

# Usage
async def main():
    async for page in fetch_pages(urls):
        process(page)
```

### 3.3 Async Comprehensions

```python
# Async list comprehension
results = [x async for x in async_iterator]

# Async generator expression
gen = (x async for x in async_iterator)

# With await in comprehension
data = [await fetch(url) for url in urls]  # Sequential!

# For concurrent execution, use gather
data = await asyncio.gather(*[fetch(url) for url in urls])
```

---

## 4. Graceful Shutdown

### 4.1 Handling Signals

```python
import asyncio
import signal

async def main():
    loop = asyncio.get_running_loop()

    def shutdown():
        print("Shutdown signal received")
        for task in asyncio.all_tasks():
            task.cancel()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    try:
        await long_running_task()
    except asyncio.CancelledError:
        print("Task was cancelled")
        await cleanup()
```

### 4.2 Graceful Server Shutdown

```python
import asyncio

async def server():
    server = await asyncio.start_server(
        handle_client, 'localhost', 8080
    )

    shutdown_event = asyncio.Event()

    async def shutdown():
        print("Shutting down...")
        server.close()
        await server.wait_closed()
        shutdown_event.set()

    # Register shutdown handler
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))

    async with server:
        await shutdown_event.wait()
```

---

## 5. Testing Async Code

### 5.1 Using pytest-asyncio

```python
# pip install pytest-asyncio

import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected

@pytest.fixture
async def async_fixture():
    resource = await create_resource()
    yield resource
    await cleanup_resource(resource)

@pytest.mark.asyncio
async def test_with_fixture(async_fixture):
    result = await async_fixture.do_something()
    assert result is not None
```

### 5.2 Mocking Async Functions

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    mock_fetch = AsyncMock(return_value={"data": "test"})

    with patch('module.fetch', mock_fetch):
        result = await function_that_calls_fetch()

    mock_fetch.assert_called_once()
    assert result["data"] == "test"
```

### 5.3 Testing Timeouts

```python
@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_function(), timeout=0.1)
```

---

## 6. Common Patterns

### 6.1 Worker Pool Pattern

```python
class AsyncWorkerPool:
    def __init__(self, num_workers):
        self.queue = asyncio.Queue()
        self.workers = []
        self.num_workers = num_workers

    async def start(self):
        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)

    async def _worker(self, worker_id):
        while True:
            job = await self.queue.get()
            if job is None:
                break
            try:
                await job()
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
            finally:
                self.queue.task_done()

    async def submit(self, job):
        await self.queue.put(job)

    async def shutdown(self):
        await self.queue.join()
        for _ in self.workers:
            await self.queue.put(None)
        await asyncio.gather(*self.workers)
```

### 6.2 Async Singleton

```python
class AsyncSingleton:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        raise TypeError("Use create() instead")

    @classmethod
    async def create(cls):
        async with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                await instance._initialize()
                cls._instance = instance
            return cls._instance

    async def _initialize(self):
        # Async initialization
        await self._connect()
```

### 6.3 Retry Decorator

```python
import functools

def async_retry(max_retries=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator

# Usage
@async_retry(max_retries=3, delay=0.5, exceptions=(ConnectionError,))
async def fetch_data(url):
    return await http_client.get(url)
```

### 6.4 Circuit Breaker Decorator

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"

    def __call__(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure > self.reset_timeout:
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpen()

            try:
                result = await func(*args, **kwargs)
                self.failures = 0
                self.state = "CLOSED"
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                raise

        return wrapper
```

---

## 7. Performance Optimization

### 7.1 Batching Requests

```python
class BatchedClient:
    def __init__(self, batch_size=100, max_wait=0.1):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.pending = []
        self._timer = None
        self._lock = asyncio.Lock()

    async def request(self, item):
        future = asyncio.Future()

        async with self._lock:
            self.pending.append((item, future))

            if len(self.pending) >= self.batch_size:
                await self._flush()
            elif self._timer is None:
                self._timer = asyncio.create_task(self._timeout())

        return await future

    async def _timeout(self):
        await asyncio.sleep(self.max_wait)
        async with self._lock:
            if self.pending:
                await self._flush()

    async def _flush(self):
        items, futures = zip(*self.pending)
        self.pending = []
        self._timer = None

        results = await self._batch_request(list(items))
        for future, result in zip(futures, results):
            future.set_result(result)
```

### 7.2 Connection Pooling

```python
class AsyncConnectionPool:
    def __init__(self, factory, max_size=10):
        self.factory = factory
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.size = 0
        self._lock = asyncio.Lock()

    async def acquire(self):
        try:
            return self.pool.get_nowait()
        except asyncio.QueueEmpty:
            async with self._lock:
                if self.size < self.max_size:
                    self.size += 1
                    return await self.factory()
            return await self.pool.get()

    async def release(self, conn):
        await self.pool.put(conn)

    @asynccontextmanager
    async def connection(self):
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)
```

---

## 8. Debugging Async Code

### 8.1 Enable Debug Mode

```python
import asyncio

# Method 1: Environment variable
# PYTHONASYNCIODEBUG=1 python script.py

# Method 2: In code
asyncio.run(main(), debug=True)

# Method 3: Set on running loop
loop = asyncio.get_running_loop()
loop.set_debug(True)
```

### 8.2 Slow Callback Detection

```python
import asyncio

async def main():
    loop = asyncio.get_running_loop()
    loop.slow_callback_duration = 0.1  # Warn if callback takes > 100ms
```

### 8.3 Task Naming for Debugging

```python
async def main():
    task = asyncio.create_task(
        worker(),
        name="worker-1"  # Helpful in tracebacks
    )
    print(task.get_name())
```

---

## Summary

1. **Structured Concurrency** - Use TaskGroup for proper task lifetime
2. **Async Context Managers** - Resource management with `async with`
3. **Async Iterators** - Streaming data with `async for`
4. **Graceful Shutdown** - Handle signals, cancel tasks, cleanup
5. **Testing** - Use pytest-asyncio, AsyncMock
6. **Patterns** - Worker pools, singletons, retry, circuit breaker
7. **Performance** - Batching, connection pooling
8. **Debugging** - Debug mode, slow callback detection

---

## Congratulations!

You've completed the Python Async Programming course! You now understand:

- Coroutines and the Event Loop
- Tasks and Futures
- Synchronization primitives
- Async I/O and networking
- Advanced patterns for production code

Continue practicing by building real applications:
- Async web scraper
- Chat server
- API aggregator
- Background job processor
