"""
Solutions for Exercise 3 (Hard): Complex Synchronization Challenges

Study these solutions AFTER attempting the exercises yourself!
"""

import asyncio
import time
from typing import Any, Callable, Awaitable
from contextlib import asynccontextmanager


# =============================================================================
# Solution 3.1: Async Connection Pool
# =============================================================================
class ConnectionPool:
    def __init__(self, max_connections: int):
        self.max_connections = max_connections
        self._available = asyncio.Queue()
        self._created = 0
        self._lock = asyncio.Lock()

        # Pre-create connections
        for i in range(max_connections):
            self._available.put_nowait(i)

    async def acquire(self) -> int:
        return await self._available.get()

    async def release(self, conn: int):
        await self._available.put(conn)

    @asynccontextmanager
    async def connection(self):
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)


# =============================================================================
# Solution 3.2: Async Rate Limiter (Token Bucket)
# =============================================================================
class TokenBucketRateLimiter:
    def __init__(self, max_tokens: int, refill_period: float):
        self.max_tokens = max_tokens
        self.refill_period = refill_period
        self._tokens = float(max_tokens)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    @property
    def available_tokens(self) -> int:
        return int(self._tokens)

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        # Tokens regenerate at rate: max_tokens / refill_period per second
        refill_rate = self.max_tokens / self.refill_period
        self._tokens = min(
            self.max_tokens,
            self._tokens + elapsed * refill_rate
        )
        self._last_refill = now

    async def acquire(self):
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return

            # Wait for some tokens to refill
            wait_time = self.refill_period / self.max_tokens
            await asyncio.sleep(wait_time)


# =============================================================================
# Solution 3.3: Distributed Lock with Heartbeat
# =============================================================================
class HeartbeatLock:
    def __init__(self, timeout: float):
        self.timeout = timeout
        self._holder = None
        self._last_heartbeat = 0
        self._condition = asyncio.Condition()

    def _is_expired(self) -> bool:
        if self._holder is None:
            return True
        return (time.monotonic() - self._last_heartbeat) > self.timeout

    async def acquire(self, holder_id: str):
        async with self._condition:
            while not self._is_expired() and self._holder != holder_id:
                try:
                    await asyncio.wait_for(
                        self._condition.wait(),
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    pass  # Check again if expired

            self._holder = holder_id
            self._last_heartbeat = time.monotonic()

    async def heartbeat(self, holder_id: str):
        async with self._condition:
            if self._holder == holder_id:
                self._last_heartbeat = time.monotonic()

    async def release(self, holder_id: str):
        async with self._condition:
            if self._holder == holder_id:
                self._holder = None
                self._condition.notify_all()


# =============================================================================
# Solution 3.4: Async Dining Philosophers
# =============================================================================
class DiningTable:
    def __init__(self, n_philosophers: int):
        self.n = n_philosophers
        # Use a global lock to prevent deadlock
        # More sophisticated solutions use fork ordering
        self._forks = [asyncio.Lock() for _ in range(n_philosophers)]
        self._waiter = asyncio.Semaphore(n_philosophers - 1)  # Limit concurrent eaters

    async def think(self, philosopher_id: int):
        await asyncio.sleep(0.01)

    async def eat(self, philosopher_id: int):
        left_fork = philosopher_id
        right_fork = (philosopher_id + 1) % self.n

        # Use waiter to prevent deadlock (at most n-1 can try to eat)
        async with self._waiter:
            # Always pick up lower-numbered fork first (prevents deadlock)
            first, second = sorted([left_fork, right_fork])

            async with self._forks[first]:
                async with self._forks[second]:
                    await asyncio.sleep(0.01)  # Eating


# =============================================================================
# Solution 3.5: Async Pipeline with Backpressure
# =============================================================================
class BackpressurePipeline:
    def __init__(self):
        self._stages: list[tuple[Callable, int]] = []
        self._queues: list[asyncio.Queue] = []
        self._results: list[Any] = []
        self._running = False
        self._tasks: list[asyncio.Task] = []
        self._input_queue: asyncio.Queue = None
        self._items_in_flight = 0
        self._done_event = asyncio.Event()
        self._lock = asyncio.Lock()

    def add_stage(self, func: Callable[[Any], Awaitable[Any]], buffer_size: int):
        self._stages.append((func, buffer_size))

    def start(self):
        if self._running:
            return

        self._running = True
        self._results = []

        # Create queues between stages
        self._queues = []
        for i, (func, buffer_size) in enumerate(self._stages):
            self._queues.append(asyncio.Queue(maxsize=buffer_size))

        # Input queue
        self._input_queue = self._queues[0] if self._queues else asyncio.Queue()
        if not self._queues:
            self._queues.append(self._input_queue)

        # Start worker for each stage
        for i, (func, _) in enumerate(self._stages):
            input_q = self._queues[i]
            output_q = self._queues[i + 1] if i + 1 < len(self._queues) else None

            task = asyncio.create_task(
                self._stage_worker(func, input_q, output_q, i == len(self._stages) - 1)
            )
            self._tasks.append(task)

    async def _stage_worker(self, func, input_q, output_q, is_last):
        while self._running:
            try:
                item = await asyncio.wait_for(input_q.get(), timeout=0.1)
            except asyncio.TimeoutError:
                if not self._running:
                    break
                continue

            if item is None:
                if output_q:
                    await output_q.put(None)
                break

            result = await func(item)

            if is_last:
                async with self._lock:
                    self._results.append(result)
                    self._items_in_flight -= 1
                    if self._items_in_flight == 0:
                        self._done_event.set()
            elif output_q:
                await output_q.put(result)

    async def push(self, item):
        async with self._lock:
            self._items_in_flight += 1
            self._done_event.clear()
        await self._input_queue.put(item)

    async def drain(self):
        if self._items_in_flight > 0:
            await self._done_event.wait()

        # Signal workers to stop
        await self._input_queue.put(None)

        # Wait for all tasks
        for task in self._tasks:
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()

        self._running = False

    @property
    def results(self) -> list[Any]:
        return self._results.copy()


# =============================================================================
# Test runner
# =============================================================================
if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("Testing ConnectionPool:")
        print("=" * 60)
        pool = ConnectionPool(max_connections=2)

        async def use_connection(name):
            async with pool.connection() as conn:
                print(f"  {name} using connection {conn}")
                await asyncio.sleep(0.1)

        await asyncio.gather(*[use_connection(f"Worker-{i}") for i in range(4)])

        print("\n" + "=" * 60)
        print("Testing TokenBucketRateLimiter:")
        print("=" * 60)
        limiter = TokenBucketRateLimiter(max_tokens=5, refill_period=1.0)
        print(f"Initial tokens: {limiter.available_tokens}")

        start = time.time()
        for i in range(7):
            await limiter.acquire()
            print(f"  Acquired token {i+1} at {time.time() - start:.2f}s")

        print("\n" + "=" * 60)
        print("Testing HeartbeatLock:")
        print("=" * 60)
        lock = HeartbeatLock(timeout=0.5)

        async def holder():
            await lock.acquire("holder-1")
            print("  holder-1 acquired lock")
            for i in range(3):
                await asyncio.sleep(0.2)
                await lock.heartbeat("holder-1")
                print(f"  holder-1 heartbeat {i+1}")
            await lock.release("holder-1")
            print("  holder-1 released lock")

        await holder()

        print("\n" + "=" * 60)
        print("Testing DiningTable:")
        print("=" * 60)
        table = DiningTable(5)

        async def philosopher(id):
            await table.think(id)
            print(f"  Philosopher {id} eating")
            await table.eat(id)
            await table.think(id)

        await asyncio.gather(*[philosopher(i) for i in range(5)])
        print("All philosophers ate successfully!")

        print("\n" + "=" * 60)
        print("Testing BackpressurePipeline:")
        print("=" * 60)
        pipeline = BackpressurePipeline()

        async def double(x):
            await asyncio.sleep(0.05)
            return x * 2

        async def add_ten(x):
            await asyncio.sleep(0.05)
            return x + 10

        pipeline.add_stage(double, buffer_size=2)
        pipeline.add_stage(add_ten, buffer_size=2)
        pipeline.start()

        for i in range(5):
            await pipeline.push(i)

        await pipeline.drain()
        print(f"Results: {sorted(pipeline.results)}")

    asyncio.run(main())
